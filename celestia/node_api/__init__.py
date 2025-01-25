import asyncio
import typing as t
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from websockets.asyncio.client import connect, ClientConnection

from ._RPC import RPC
from .blob import BlobClient
from .header import HeaderClient
from .p2p import P2PClient
from .state import StateClient


class Client:
    """ Celestia Node API client
    """

    def __init__(self,
                 host: str = 'localhost', port: int = 26658,
                 auth_token: str = None, response_timeout: int = 180, **options: t.Any):
        self.__options = dict(options, url=f'ws://{host}:{port}',
                              auth_token=auth_token, response_timeout=response_timeout)

    @property
    def options(self):
        """ Client create options """
        return self.__options

    class NodeAPI:
        """ Celestia node API
        """

        def __init__(self, rpc: RPC):
            self._rpc = rpc

        @property
        def state(self):
            return StateClient(self._rpc)

        @property
        def blob(self):
            return BlobClient(self._rpc)

        @property
        def header(self):
            return HeaderClient(self._rpc)

        @property
        def p2p(self):
            return P2PClient(self._rpc)

    def connect(self, auth_token: str = None, **options: t.Any) -> AbstractAsyncContextManager[NodeAPI]:
        """ Creates and return connection context manager. """
        headers = []
        options = dict(self.options, **options)
        url = options['url']
        response_timeout = options['response_timeout']
        auth_token = auth_token or options['auth_token']
        if auth_token is not None:
            headers.append(('Authorization', f'Bearer {auth_token}'))

        async def listener(connection: ClientConnection, receiver: t.Callable[[str | bytes], None]):
            async for message in connection:
                receiver(message)

        @asynccontextmanager
        async def connect_context():
            rpc = RPC(response_timeout)
            async with connect(url, additional_headers=headers) as connection:
                async with rpc.connect(connection) as receiver:
                    self._listener_task = asyncio.create_task(listener(connection, receiver))
                    yield self.NodeAPI(rpc)

        return connect_context()
