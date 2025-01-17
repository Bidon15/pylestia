from dataclasses import dataclass

from ._RPC import Wrapper


@dataclass
class Balance:
    amount: int
    denom: str

    def __init__(self, amount: int, denom: str):
        self.amount = int(amount)
        self.denom = denom


class StateClient(Wrapper):

    async def account_address(self) -> str:
        """ Retrieves the address of the node's account/signer """
        return await self._rpc.call("state.AccountAddress")

    async def balance(self) -> Balance:
        """ Retrieves the Celestia coin balance for the node's account/signer
        and verifies it against the corresponding block's AppHash.
        """
        return await self._rpc.call("state.Balance", (), lambda kwargs: Balance(**kwargs))

    async def balance_for_address(self, address: str) -> Balance:
        """ Retrieves the Celestia coin balance for the given address and
        verifies the returned balance against the corresponding block's AppHash.
        """
        return await self._rpc.call("state.BalanceForAddress", (address,), lambda kwargs: Balance(**kwargs))
