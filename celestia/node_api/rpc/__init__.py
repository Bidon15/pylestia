import asyncio
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from urllib.parse import urlparse

from websockets import connect
# In websockets 12.0, the connection types have changed
# Use Protocol instead of ClientConnection/Connection
from websockets.protocol import Protocol as ClientConnection

from .abc import Transport as AbcTransport
from .executor import RPC, TxConfig


class Client:
    """ WS JSON-RPC Client
    """

    def __init__(self, url: str = None, /, *, auth_token: str =None,
                 host: str = 'localhost', port: int = 26658):
        url = self._make_url(url, host=host, port=port)
        self.options = dict(url=url, auth_token=auth_token)

    def _make_url(self, url: str = None, /, *,
                  host: str = 'localhost', port: int = 26658, protocol: str = 'ws') -> str:
        if url is None:
            url = f'{protocol}://{host}:{port}'
        pr = urlparse(url or "ws://localhost:26658")
        if pr.scheme not in ("ws", "wss"):
            raise ValueError("Unsupported URL scheme, must be ws or wss")
        return f'{pr.scheme}://{pr.hostname}:{pr.port or port}'

    def connect(self, auth_token: str = None, /, *,
                response_timeout: float = 180) -> AbstractAsyncContextManager[RPC]:
        headers = []
        url = self.options['url']
        if auth_token := auth_token or self.options['auth_token']:
            headers.append(('Authorization', f'Bearer {auth_token}'))

        async def listener(connection: ClientConnection, handlers: AbcTransport):
            try:
                async for message in connection:
                    handlers.on_message(message)
            except asyncio.CancelledError:
                handlers.on_close(None)
            except Exception as exc:
                handlers.on_close(exc)

        @asynccontextmanager
        async def connect_context():
            try:
                listener_task = None
                async with connect(url, additional_headers=headers) as connection:
                    class Transport(AbcTransport):

                        async def send(self, message: str):
                            await connection.send(message)

                    transport = Transport()
                    rpc = RPC(transport, response_timeout)
                    listener_task = asyncio.create_task(listener(connection, transport))
                    yield rpc
            finally:
                if listener_task and not listener_task.done():
                    listener_task.cancel()
                    await listener_task

        return connect_context()
