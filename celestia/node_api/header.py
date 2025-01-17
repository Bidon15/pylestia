from typing_extensions import AsyncIterator

from ._RPC import Wrapper

type ExtendedHeader = dict


class HeaderClient(Wrapper):

    async def local_head(self) -> ExtendedHeader:
        """ Returns the ExtendedHeader of the chain head. """
        return await self._rpc.call("header.LocalHead")

    async def network_head(self) -> ExtendedHeader:
        """ Provides the Syncer's view of the current network head. """
        return await self._rpc.call("header.NetworkHead")

    def subscribe(self) -> AsyncIterator[ExtendedHeader]:
        """ Subscribe to recent ExtendedHeaders from the network.
        """
        return self._rpc.iter("header.Subscribe")
