import asyncio
import json
import typing as t
import uuid
from asyncio import Future
from collections import deque
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from dataclasses import is_dataclass, asdict

from ajsonrpc.core import JSONRPC20Response, JSONRPC20Request

RPC_VALUE_ERRORS = [
    'unmarshaling params',
    'equal to 0',
    'given height is from the future',
    'invalid range',
    'height must be bigger than zero',
    'dial to self attempted',
    'gater disallows connection to peer',
    'notfound desc = delegation with delegator',
    'unknown desc = failed to execute message; message index: 0: invalid shares amount:',
    'cannot redelegate to the same validator',
    'too many unbonding delegation entries for (delegator, validator) tuple',
    'redelegation not found for delegator address',
    'too many redelegation entries for (delegator, src-validator, dst-validator)'
    'datastore: key not found'
]

from celestia.types import Base64


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, Base64):
            return str(obj)
        return super().default(obj)


class Wrapper:
    def __init__(self, rpc: 'RPC'):
        self._rpc = rpc


class Transport(t.Protocol):

    async def send(self, message: str) -> None:
        """ Send a message to the connection. """


class RPC:
    """ RPC executor """

    def __init__(self, response_timeout: int):
        self._response_timeout = response_timeout
        self._transport = None  # type: Transport | None
        self._pending = dict()  # type: dict[str, Future]
        self._subscriptions = dict()  # type: dict[str,deque[t.Any]]

    @property
    def transport(self) -> Transport:
        if self._transport:
            return self._transport
        raise ConnectionError("Transport is not connected.")

    def connect(self, transport: Transport) -> AbstractAsyncContextManager[t.Callable[[str], None]]:

        def receiver(message: str):
            message = json.loads(message)
            if 'method' in message:
                subscription_id, item = message['params']
                subscription = self._subscriptions.get(subscription_id, None)
                if subscription is not None:
                    subscription.append(item)
            else:
                response = JSONRPC20Response(result=False)
                response.body = message
                if future := self._pending.get(response.id):
                    if response.error is not None:
                        error_body = getattr(response.error, "body", None)
                        error_message = error_body.get('message', None).lower() if error_body else None
                        if any(keyword in error_message for keyword in RPC_VALUE_ERRORS):
                            future.set_exception(ValueError(error_message))
                        elif error_message is None or error_body is None:
                            future.set_exception(ConnectionError("RPC faled; undefined error"))
                        else:
                            future.set_exception(ConnectionError(f"RPC failed; {error_message}", response.error))
                    else:
                        future.set_result(response.result)
                else:
                    raise RuntimeError("Received message with unexpected ID.")

        @asynccontextmanager
        async def connect_context():
            try:
                self._transport = transport
                yield receiver
            finally:
                self._transport = None
                for id in tuple(self._pending.keys()):
                    future = self._pending.pop(id)
                    if not future.done():
                        self._pending[id].set_exception(ConnectionError("RPC closed"))
                self._pending.clear()
                # ToDo: cleanup subscription

        return connect_context()

    async def call(self, method: str, params: tuple[t.Any, ...] = None,
                   deserializer: t.Callable[[t.Any], t.Any] = None) -> t.Any | None:
        params = params or ()
        deserializer = deserializer or (lambda a: a)
        id = str(uuid.uuid4())
        request = JSONRPC20Request(method, params, id)
        await self._transport.send(json.dumps(request.body, cls=JSONEncoder))
        future = self._pending[id] = Future()
        future.add_done_callback(lambda _: self._pending.pop(id, None))
        async with asyncio.timeout(self._response_timeout):
            result = await future
            return deserializer(result)

    async def iter(self, method: str, params: tuple[t.Any, ...] = None,
                   deserializer: t.Callable[[t.Any], t.Any] = None
                   ) -> AsyncGenerator[t.Any]:
        deserializer = deserializer or (lambda a: a)
        subscription_id = await self.call(method, params)
        try:
            subscription = self._subscriptions[subscription_id] = deque()
            while True:
                if len(subscription):
                    yield deserializer(subscription.popleft())
                else:
                    await asyncio.sleep(0.1)
        finally:
            del self._subscriptions[subscription_id]
