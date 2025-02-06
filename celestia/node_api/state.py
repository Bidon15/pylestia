import typing as t

from celestia._celestia import types  # noqa

from celestia.common_types import TxConfig, Blob
from celestia.types.state import Address, Balance, TXResponse, QueryUnbondingDelegationResponse, \
    QueryDelegationResponse, QueryRedelegationResponse
from ._RPC import Wrapper


class StateClient(Wrapper):

    async def account_address(self) -> Address:
        """ Retrieves the address of the node's account/signer """
        return await self._rpc.call("state.AccountAddress")

    async def balance(self) -> Balance:
        """ Retrieves the Celestia coin balance for the node's account/signer
        and verifies it against the corresponding block's AppHash.
        """
        return await self._rpc.call("state.Balance", (), Balance.deserializer)

    async def balance_for_address(self, address: Address) -> Balance:
        """ Retrieves the Celestia coin balance for the given address and
        verifies the returned balance against the corresponding block's AppHash.
        """
        return await self._rpc.call("state.BalanceForAddress", (address,), Balance.deserializer)

    async def begin_redelegate(self, src_val_addr: Address, dst_val_addr: Address, amount: int,
                               **config: t.Unpack[TxConfig]) -> TXResponse:
        """ Sends a user's delegated tokens to a new validator for redelegation.
        """
        return await self._rpc.call("state.BeginRedelegate", (src_val_addr, dst_val_addr, str(amount), config),
                                    TXResponse.deserializer)

    async def cancel_unbonding_delegation(self, val_addr: Address, amount: int, height: int,
                                          **config: t.Unpack[TxConfig]) -> TXResponse:
        """ Cancels a user's pending undelegation from a validator.
        """
        return await self._rpc.call("state.CancelUnbondingDelegation", (val_addr, str(amount), str(height), config),
                                    TXResponse.deserializer)

    async def delegate(self, del_addr: Address, amount: int, **config: t.Unpack[TxConfig]) -> TXResponse:
        """ Sends a user's liquid tokens to a validator for delegation.
        """
        return await self._rpc.call("state.Delegate", (del_addr, str(amount), config), TXResponse.deserializer)

    async def grant_fee(self, grantee: Address, amount: int, **config: t.Unpack[TxConfig]) -> TXResponse:
        """ No comment exists yet for this method.
        """
        return await self._rpc.call("state.GrantFee", (grantee, str(amount), config), TXResponse.deserializer)

    async def query_delegation(self, val_addr: Address) -> QueryDelegationResponse:
        """ Retrieves the delegation information between a delegator and a validator.
        """
        return await self._rpc.call("state.QueryDelegation", (val_addr,), QueryDelegationResponse.deserializer)

    async def query_redelegations(self, src_val_addr: Address, dst_val_addr: Address) -> QueryRedelegationResponse:
        """ Retrieves the status of the redelegations between a delegator and a validator.
        """
        return await self._rpc.call("state.QueryRedelegations", (src_val_addr, dst_val_addr,),
                                    QueryRedelegationResponse.deserializer)

    async def query_unbonding(self, val_addr: Address) -> QueryUnbondingDelegationResponse:
        """ Retrieves the unbonding status between a delegator and a validator.
        """
        return await self._rpc.call("state.QueryUnbonding", (val_addr,), QueryUnbondingDelegationResponse.deserializer)

    async def revoke_grant_fee(self, grantee: Address, **config: t.Unpack[TxConfig]) -> TXResponse:
        """ No comment exists yet for this method.
        """
        return await self._rpc.call("state.RevokeGrantFee", (grantee, config), TXResponse.deserializer)

    async def submit_pay_for_blob(self, blob: Blob, *blobs: Blob, **config: t.Unpack[TxConfig]) -> int:
        """ Builds, signs and submits a PayForBlob transaction.
        """
        blobs = tuple(types.normalize_blob(blob) if blob.commitment is None else blob for blob in (blob, *blobs))
        return await self._rpc.call("state.SubmitPayForBlob", (blobs, config), )

    async def transfer(self, to: Address, amount: int, **config: t.Unpack[TxConfig]) -> TXResponse:
        """ Sends the given amount of coins from default wallet of the node to the given account address.
        """
        return await self._rpc.call("state.Transfer", (to, str(amount), config), TXResponse.deserializer)

    async def undelegate(self, del_addr: Address, amount: int, **config: t.Unpack[TxConfig]) -> TXResponse:
        """ Undelegates a user's delegated tokens, unbonding them from the current validator.
        """
        return await self._rpc.call("state.Undelegate", (del_addr, str(amount), config), TXResponse.deserializer)
