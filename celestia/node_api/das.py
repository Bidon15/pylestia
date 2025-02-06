from celestia.types.das import SamplingStats
from ._RPC import Wrapper


class DasClient(Wrapper):

    async def sampling_stats(self) -> SamplingStats:
        """ Returns the current statistics over the DA sampling process."""
        return await self._rpc.call("das.SamplingStats", (), SamplingStats.deserializer)

    async def wait_catch_up(self):
        """ Blocks until DASer finishes catching up to the network head."""
        return await self._rpc.call("das.WaitCatchUp")
