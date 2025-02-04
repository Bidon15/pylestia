import typing as t

import celestia.types as celestia_types
from ._RPC import Wrapper


class ShareClient(Wrapper):

    async def get_eds(self, height: int) -> celestia_types.ExtendedDataSquare:
        """ Gets the full EDS identified by the given extended header."""

        def deserializer(result):
            if result is not None:
                return celestia_types.ExtendedDataSquare(**result)

        return await self._rpc.call("share.GetEDS", (height,), deserializer)

    async def get_namespace_data(self, height: int,
                                 namespace: celestia_types.Namespace) -> list[celestia_types.NamespaceData]:
        """ Gets all shares from an EDS within the given namespace. Shares are returned in a row-by-row
        order if the namespace spans multiple rows."""

        def deserializer(result):
            if result is not None:
                return [celestia_types.NamespaceData(**data) for data in result]

        return await self._rpc.call("share.GetNamespaceData", (height, celestia_types.Namespace(namespace)),
                                    deserializer)

    async def get_range(self, height: int, start: int, end: int):
        """ Gets a list of shares and their corresponding proof."""
        return await self._rpc.call("share.GetRange", (height, start, end), )

    async def get_samples(self, header: celestia_types.ExtendedHeader, indices: [celestia_types.SampleCoords]) -> [
        t.Any]:
        """ Gets sample for given indices."""
        return await self._rpc.call("share.GetSamples", (header, indices,), )

    async def get_share(self, height: int, row: int, col: int):
        """ Gets a Share by coordinates in EDS."""
        return await self._rpc.call("share.GetShare", (height, row, col,), )

    async def get_available(self, height: int):
        """ Subjectively validates if Shares committed to the given ExtendedHeader are available on the Network."""
        return await self._rpc.call("share.SharesAvailable", (height,), )
