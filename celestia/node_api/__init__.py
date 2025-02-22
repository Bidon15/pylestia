from contextlib import asynccontextmanager, AbstractAsyncContextManager

from . import rpc
from .blob import BlobClient
from .das import DasClient
from .fraud import FraudClient
from .header import HeaderClient
from .p2p import P2PClient
from .rpc import RPC
from .share import ShareClient
from .state import StateClient


class NodeAPI:
    """ Celestia node API """

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

    @property
    def das(self):
        return DasClient(self._rpc)

    @property
    def fraud(self):
        return FraudClient(self._rpc)

    @property
    def share(self):
        return ShareClient(self._rpc)


class Client(rpc.Client):
    """ Celestia Node API client
    """

    def connect(self, auth_token: str = None, /, response_timeout: float = 180) -> AbstractAsyncContextManager[NodeAPI]:
        """ Creates and return connection context manager. """

        @asynccontextmanager
        async def connect_context():
            async with super(Client, self).connect(auth_token, response_timeout=response_timeout) as rpc:
                yield NodeAPI(rpc)

        return connect_context()
