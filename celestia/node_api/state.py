import typing as t

from celestia._celestia import types  # noqa

import celestia.types as celestia_types
from ._RPC import Wrapper


class StateClient(Wrapper):

    async def account_address(self) -> celestia_types.Address:
        """ Retrieves the address of the node's account/signer """
        return await self._rpc.call("state.AccountAddress")

    async def balance(self) -> celestia_types.Balance:
        """ Retrieves the Celestia coin balance for the node's account/signer
        and verifies it against the corresponding block's AppHash.
        """
        return await self._rpc.call("state.Balance", (), lambda kwargs: celestia_types.Balance(**kwargs))

    async def balance_for_address(self, address: celestia_types.Address) -> celestia_types.Balance:
        """ Retrieves the Celestia coin balance for the given address and
        verifies the returned balance against the corresponding block's AppHash.
        """
        return await self._rpc.call("state.BalanceForAddress", (address,),
                                    lambda kwargs: celestia_types.Balance(**kwargs))

    async def begin_redelegate(self, src_val_addr: celestia_types.Address, dst_val_addr: celestia_types.Address,
                               amount: int, **config: t.Unpack[celestia_types.TxConfig]) -> celestia_types.TXResponse:
        """ Sends a user's delegated tokens to a new validator for redelegation.
        """
        return await self._rpc.call("state.BeginRedelegate", (src_val_addr, dst_val_addr, str(amount), config),
                                    lambda kwargs: celestia_types.TXResponse(**kwargs))

    async def cancel_unbonding_delegation(self, val_addr: celestia_types.Address, amount: int, height: int,
                                          **config: t.Unpack[celestia_types.TxConfig]) -> celestia_types.TXResponse:
        """ Cancels a user's pending undelegation from a validator.
        """
        return await self._rpc.call("state.CancelUnbondingDelegation", (val_addr, str(amount), str(height), config),
                                    lambda kwargs: celestia_types.TXResponse(**kwargs))

    async def delegate(self, del_addr: celestia_types.Address, amount: int,
                       **config: t.Unpack[celestia_types.TxConfig]) -> celestia_types.TXResponse:
        """ Sends a user's liquid tokens to a validator for delegation.
        """
        return await self._rpc.call("state.Delegate", (del_addr, str(amount), config),
                                    lambda kwargs: celestia_types.TXResponse(**kwargs))

    async def grant_fee(self, grantee: celestia_types.Address, amount: int,
                        **config: t.Unpack[celestia_types.TxConfig]) -> celestia_types.TXResponse:
        """ No comment exists yet for this method.
        """
        return await self._rpc.call("state.GrantFee", (grantee, str(amount), config),
                                    lambda kwargs: celestia_types.TXResponse(**kwargs))

    async def query_delegation(self, val_addr: celestia_types.Address) -> celestia_types.QueryDelegationResponse:
        """ Retrieves the delegation information between a delegator and a validator.
        """

        def deserializer(result):
            if result is not None:
                return celestia_types.QueryDelegationResponse(
                    delegation_response=celestia_types.DelegationResponse(
                        delegation=celestia_types.Delegation(
                            delegator_address=result['delegation_response']['delegation']['delegator_address'],
                            validator_address=result['delegation_response']['delegation']['validator_address'],
                            shares=float(result['delegation_response']['delegation']['shares']),
                        ),
                        balance=celestia_types.Balance(**result['delegation_response']['balance'])))

        return await self._rpc.call("state.QueryDelegation", (val_addr,), deserializer)

    async def query_redelegations(self, src_val_addr: celestia_types.Address,
                                  dst_val_addr: celestia_types.Address) -> celestia_types.QueryRedelegationResponse:
        """ Retrieves the status of the redelegations between a delegator and a validator.
        """

        def deserializer(result):
            if result is not None:
                return celestia_types.QueryRedelegationResponse(
                    redelegation_responses=[celestia_types.RedelegationResponse(
                        redelegation=celestia_types.Redelegation(
                            delegator_address=redelegation_response['redelegation']['delegator_address'],
                            validator_src_address=redelegation_response['redelegation']['validator_src_address'],
                            validator_dst_address=redelegation_response['redelegation']['validator_dst_address'],
                            entries=[celestia_types.RedelegationEntry(
                                creation_height=redelegation_entry['creation_height'],
                                completion_time=redelegation_entry['completion_time'],
                                initial_balance=int(redelegation_entry['initial_balance']),
                                shares_dst=float(redelegation_entry['shares_dst']),
                            ) for redelegation_entry in redelegation_response['redelegation']['entries']] if
                            redelegation_response['redelegation']['entries'] else None
                        ),
                        entries=[celestia_types.RedelegationResponseEntry(
                            redelegation_entry=celestia_types.RedelegationEntry(
                                creation_height=redelegation_response_entry['redelegation_entry']['creation_height'],
                                completion_time=redelegation_response_entry['redelegation_entry']['completion_time'],
                                initial_balance=int(
                                    redelegation_response_entry['redelegation_entry']['initial_balance']),
                                shares_dst=float(redelegation_response_entry['redelegation_entry']['shares_dst']),
                            ),
                            balance=int(redelegation_response_entry['balance'])
                        ) for redelegation_response_entry in redelegation_response['entries']]
                    ) for redelegation_response in result['redelegation_responses']],
                    pagination=celestia_types.Pagination(**result.get('pagination', {}))
                )

        return await self._rpc.call("state.QueryRedelegations", (src_val_addr, dst_val_addr,), deserializer)

    async def query_unbonding(self,
                              val_addr: celestia_types.Address) -> celestia_types.QueryUnbondingDelegationResponse:
        """ Retrieves the unbonding status between a delegator and a validator.
        """

        def deserializer(result):
            if result is not None:
                return celestia_types.QueryUnbondingDelegationResponse(
                    unbond=celestia_types.Unbond(
                        delegator_address=result['unbond']['delegator_address'],
                        validator_address=result['unbond']['validator_address'],
                        entries=[celestia_types.UnbondEntry(
                            creation_height=entry['creation_height'],
                            completion_time=entry['completion_time'],
                            initial_balance=int(entry['initial_balance']),
                            balance=int(entry['balance']),
                        ) for entry in result['unbond']['entries']]
                    )
                )

        return await self._rpc.call("state.QueryUnbonding", (val_addr,), deserializer)

    async def revoke_grant_fee(self, grantee: celestia_types.Address,
                               **config: t.Unpack[celestia_types.TxConfig]) -> celestia_types.TXResponse:
        """ No comment exists yet for this method.
        """
        return await self._rpc.call("state.RevokeGrantFee", (grantee, config),
                                    lambda kwargs: celestia_types.TXResponse(**kwargs))

    async def submit_pay_for_blob(self, blob: celestia_types.Blob, *blobs: celestia_types.Blob,
                                  **config: t.Unpack[celestia_types.TxConfig]) -> int:
        """ Builds, signs and submits a PayForBlob transaction.
        """
        blobs = tuple(types.normalize_blob(blob) if blob.commitment is None else blob for blob in (blob, *blobs))
        return await self._rpc.call("state.SubmitPayForBlob", (blobs, config), )

    async def transfer(self, to: celestia_types.Address, amount: int,
                       **config: t.Unpack[celestia_types.TxConfig]) -> celestia_types.TXResponse:
        """ Sends the given amount of coins from default wallet of the node to the given account address.
        """
        return await self._rpc.call("state.Transfer", (to, str(amount), config),
                                    lambda kwargs: celestia_types.TXResponse(**kwargs))

    async def undelegate(self, del_addr: celestia_types.Address, amount: int,
                         **config: t.Unpack[celestia_types.TxConfig]) -> celestia_types.TXResponse:
        """ Undelegates a user's delegated tokens, unbonding them from the current validator.
        """
        return await self._rpc.call("state.Undelegate", (del_addr, str(amount), config),
                                    lambda kwargs: celestia_types.TXResponse(**kwargs))
