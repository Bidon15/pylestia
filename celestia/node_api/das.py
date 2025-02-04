from ._RPC import Wrapper
import celestia.types as celestia_types

class DasClient(Wrapper):

    async def sampling_stats(self) -> celestia_types.SamplingStats:
        """ Returns the current statistics over the DA sampling process."""

        def deserializer(result):
            if result is not None:
                return celestia_types.SamplingStats(**result)

        return await self._rpc.call("das.SamplingStats", (), deserializer)

    async def wait_catch_up(self):
        """ Blocks until DASer finishes catching up to the network head."""
        return await self._rpc.call("das.WaitCatchUp")
