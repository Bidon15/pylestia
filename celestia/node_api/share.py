import celestia.common_types as celestia_types
from celestia.types.header import ExtendedHeader
from celestia.types.share import ExtendedDataSquare, NamespaceData, SampleCoords, GetRangeResult, Sample
from ._RPC import Wrapper


class ShareClient(Wrapper):

    async def get_eds(self, height: int) -> ExtendedDataSquare:
        """ Gets the full EDS identified by the given extended header."""
        return await self._rpc.call("share.GetEDS", (height,), ExtendedDataSquare.deserializer)

    async def get_namespace_data(self, height: int, namespace: celestia_types.Namespace) -> list[NamespaceData]:
        """ Gets all shares from an EDS within the given namespace. Shares are returned in a row-by-row
        order if the namespace spans multiple rows."""

        def deserializer(result):
            if result is not None:
                return [NamespaceData(**data) for data in result]

        return await self._rpc.call("share.GetNamespaceData", (height, celestia_types.Namespace(namespace)),
                                    deserializer)

    async def get_range(self, height: int, start: int, end: int) -> GetRangeResult:
        """ Gets a list of shares and their corresponding proof."""
        return await self._rpc.call("share.GetRange", (height, start, end), GetRangeResult.deserializer)

    async def get_samples(self, header: ExtendedHeader, indices: [SampleCoords]) -> list[Sample]:
        """ Gets sample for given indices."""
        return await self._rpc.call("share.GetSamples", (header.extended_header, indices,))

    async def get_share(self, height: int, row: int, col: int) -> Sample:
        """ Gets a Share by coordinates in EDS."""
        return await self._rpc.call("share.GetShare", (height, row, col,))

    async def get_available(self, height: int):
        """ Subjectively validates if Shares committed to the given ExtendedHeader are available on the Network."""
        return await self._rpc.call("share.SharesAvailable", (height,))
