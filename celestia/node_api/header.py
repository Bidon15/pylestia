import typing as t
from collections.abc import AsyncIterator

from ._RPC import Wrapper

type ExtendedHeader = dict[str, t.Any]
type State = dict[str, t.Any]


class HeaderClient(Wrapper):

    async def get_by_hash(self, header_hash) -> ExtendedHeader | None:
        """ Returns the header of the given hash from the node's header store.
        """
        try:
            return await self._rpc.call("header.GetByHash", (header_hash,))
        except ConnectionError as e:
            if 'header: not found' in e.args[1].body['message'].lower():
                return None
            else:
                raise e

    async def get_by_height(self, height: int) -> ExtendedHeader:
        """ Returns the ExtendedHeader at the given height if it is currently available.
        """
        return await self._rpc.call("header.GetByHeight", (height,))

    async def get_range_by_height(self, range_from: ExtendedHeader, range_to: int) -> list[ExtendedHeader]:
        """ Returns the given range (from:to) of ExtendedHeaders from the node's header
        store and verifies that the returned headers are adjacent to each other.
        """
        return await self._rpc.call("header.GetRangeByHeight", (range_from, range_to))

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

    async def sync_state(self) -> State:
        """ Returns the current state of the header Syncer.
        """
        return await self._rpc.call("header.SyncState")

    async def sync_wait(self) -> None:
        """ Blocks until the header Syncer is synced to network head.
        """
        return await self._rpc.call("header.SyncWait")

    async def wait_for_height(self, header: int) -> ExtendedHeader:
        """ Blocks until the header at the given height has been processed
        by the store or context deadline is exceeded.
        """
        return await self._rpc.call("header.WaitForHeight", (header,))