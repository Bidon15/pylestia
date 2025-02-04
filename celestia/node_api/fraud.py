from collections.abc import AsyncIterator

from ._RPC import Wrapper
import celestia.types as celestia_types

class FraudClient(Wrapper):

    async def get(self, proof_type: str) -> list[dict[str, str]]:
        """ Fetches fraud proofs from the disk by its type."""

        return await self._rpc.call("fraud.Get", (proof_type,))

    async def subscribe(self, proof_type: str) -> AsyncIterator[dict[str, str]]:
        """ Allows to subscribe on a Proof pub sub topic by its type."""

        return self._rpc.iter("fraud.Subscribe", (proof_type,))