from collections.abc import AsyncIterator

from celestia.types.header import ExtendedHeader, State, HashedData
from ._RPC import Wrapper


class HeaderClient(Wrapper):

    async def get_by_hash(self, header_hash: HashedData) -> ExtendedHeader | None:
        """ Returns the header of the given hash from the node's header store.
        """
        try:
            return await self._rpc.call("header.GetByHash", (header_hash,), ExtendedHeader.deserializer)
        except ConnectionError as e:
            if 'header: not found' in e.args[1].body['message'].lower():
                return None
            else:
                raise e

    async def get_by_height(self, height: int) -> ExtendedHeader:
        """ Returns the ExtendedHeader at the given height if it is currently available.
        """
        return await self._rpc.call("header.GetByHeight", (int(height),), ExtendedHeader.deserializer)

    async def get_range_by_height(self, range_from: ExtendedHeader, range_to: int) -> list[ExtendedHeader]:
        """ Returns the given range (from:to) of ExtendedHeaders from the node's header
        store and verifies that the returned headers are adjacent to each other.
        """

        def deserializer(result):
            if result is not None:
                return [ExtendedHeader(**kwargs) for kwargs in result]

        return await self._rpc.call("header.GetRangeByHeight", (range_from.extended_header, int(range_to)),
                                    deserializer)

    async def local_head(self) -> ExtendedHeader:
        """ Returns the ExtendedHeader of the chain head. """
        return await self._rpc.call("header.LocalHead", (), ExtendedHeader.deserializer)

    async def network_head(self) -> ExtendedHeader:
        """ Provides the Syncer's view of the current network head. """
        return await self._rpc.call("header.NetworkHead", (), ExtendedHeader.deserializer)

    async def subscribe(self) -> AsyncIterator[ExtendedHeader | None]:
        """ Subscribe to recent ExtendedHeaders from the network.
        """

        async for subs_header_result in self._rpc.iter("header.Subscribe"):
            if subs_header_result is not None:
                yield subs_header_result

    async def sync_state(self) -> State:
        """ Returns the current state of the header Syncer.
        """
        return await self._rpc.call("header.SyncState", (), State.deserializer)

    async def sync_wait(self) -> None:
        """ Blocks until the header Syncer is synced to network head.
        """
        return await self._rpc.call("header.SyncWait")

    async def wait_for_height(self, height: int) -> ExtendedHeader:
        """ Blocks until the header at the given height has been processed
        by the store or context deadline is exceeded.
        """
        return await self._rpc.call("header.WaitForHeight", (height,), ExtendedHeader.deserializer)
