import asyncio
import json
import sys
import typing as t
import uuid
from asyncio import Future
from collections import deque
from collections.abc import AsyncGenerator
from dataclasses import is_dataclass, asdict

from ajsonrpc.core import JSONRPC20Response, JSONRPC20Request

from pylestia.types import Base64
from .abc import RPCExecutor, Transport, logger

class TxConfig(t.TypedDict):
    """ Represents a transaction configuration for submitting transactions to Celestia.

    Attributes:
        signer_address (str | None): The address of the transaction signer.
        is_gas_price_set (bool | None): Whether a custom gas price is set.
        key_name (str | None): The name of the key used for signing.
        gas_price (float | None): The gas price for the transaction.
        gas (int | None): The amount of gas to use.
        fee_granter_address (str | None): Address of the fee granter (if applicable).
    """
    signer_address: str | None
    is_gas_price_set: bool | None
    key_name: str | None
    gas_price: float | None
    gas: int | None
    fee_granter_address: str | None

if sys.version_info[:2] <= (3, 10):
    from async_timeout import timeout as asyncio_timeout

    asyncio.timeout = asyncio_timeout

RPC_VALUE_ERRORS = [
    # Original errors
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
    'too many redelegation entries for (delegator, src-validator, dst-validator)',
    'datastore: key not found',
    # New error codes added in v0.10.0 and v0.11.0
    'reserved namespace',
    'invalid namespace length',
    'invalid data size',
    'blob size mismatch',
    'unsupported share version',
    'zero blob size',
    'no blobs',
    'invalid blob signer',
    'invalid namespace type',
]


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, Base64):
            return str(obj)
        return super().default(obj)


class RPC(RPCExecutor):
    """ RPC encoder / executor / decoder
    """

    def __init__(self, transport: Transport, timeout: float = 180):
        self.timeout = timeout
        self.transport = transport
        self.transport.on_message = self.on_transport_response
        self.transport.on_close = self.on_transport_close
        self._pending = dict()  # type: dict[str, Future]
        self._subscriptions = dict()  # type: dict[str, deque[t.Any]]

    def on_transport_response(self, message: str):
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
                        future.set_exception(ConnectionError("RPC failed; undefined error"))
                    else:
                        future.set_exception(ConnectionError(f"RPC failed; {error_message}", response.error))
                else:
                    future.set_result(response.result)
            else:
                logger.warning("Received message with unexpected ID.")

    def on_transport_close(self, exc: Exception = None):
        if exc:
            e = ConnectionError(f"RPC failed; transport closed by error {exc}")
            exc = e.with_traceback(exc.__traceback__)

        for future in self._pending.values():
            if exc:
                future.set_exception(exc)
            else:
                future.set_exception(ConnectionError("RPC failed; transport closed"))

        for id in tuple(self._subscriptions.keys()):
            subscription = self._subscriptions.pop(id)
            if exc:
                subscription.append(exc)

    async def call(self, method: str, params: tuple[t.Any, ...] = None,
                   deserializer: t.Callable[[t.Any], t.Any] = None) -> t.Any | None:
        params = params or ()
        deserializer = deserializer or (lambda a: a)
        id = str(uuid.uuid4())
        request = JSONRPC20Request(method, params, id)
        await self.transport.send(json.dumps(request.body, cls=JSONEncoder))
        future = self._pending[id] = Future()
        future.add_done_callback(lambda _: self._pending.pop(id, None))
        async with asyncio.timeout(self.timeout):
            result = await future
            return deserializer(result)

    async def subscribe(self, method: str, params: tuple[t.Any, ...] = None,
                   deserializer: t.Callable[[t.Any], t.Any] = None) -> AsyncGenerator[t.Any, None]:
        deserializer = deserializer or (lambda a: a)
        subscription_id = await self.call(method, params)
        try:
            subscription = self._subscriptions[subscription_id] = deque()
            while subscription_id in self._subscriptions:
                if len(subscription):
                    item = subscription.popleft()
                    if isinstance(item, Exception):
                        raise item
                    yield deserializer(item)
                else:
                    await asyncio.sleep(0.1)
        finally:
            self._subscriptions.pop(subscription_id, None)
