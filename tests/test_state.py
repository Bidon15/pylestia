import asyncio

import pytest
import pytest_asyncio

from celestia.node_api import Client
from celestia.node_api.blob import Blob


@pytest_asyncio.fixture(scope='session')
async def clients_connection(container_ids):
    container1, container2, container3 = container_ids[:3]
    client1 = Client(port=container1[1])
    client2 = Client(port=container2[1])
    client3 = Client(port=container3[1])
    cnt = 60
    while cnt:
        try:
            async with client1.connect(container1[0]) as api:
                balance = await api.state.balance()
                balance2 = await api.state.balance_for_address('celestia16ws8cxx9ykl4598qgshvt36mejpkeyvzayndth')
                balance3 = await api.state.balance_for_address('celestia10yeexpgcpx88qru4ca63frhw3jqua4qw8swxy0')
                if balance.amount != 0 and balance2.amount != 0 and balance3.amount != 0:
                    break
        except Exception:
            pass
        cnt -= 1
        await asyncio.sleep(1)

    return client1, client2, client3


@pytest.mark.asyncio
async def test_account_address(auth_token, bridge_address):
    client = Client()
    async with client.connect(auth_token) as api:
        address = await api.state.account_address()
        assert address == bridge_address


@pytest.mark.asyncio
async def test_account_balance(auth_token):
    client = Client()
    async with client.connect(auth_token) as api:
        balance = await api.state.balance()
        assert balance.amount > 100000000000000
        assert balance.denom == 'utia'
        address = await api.state.account_address()
        address_balance = await api.state.balance_for_address(address)
        assert address_balance == balance


@pytest.mark.asyncio
async def test_transfer(clients_connection, container_ids):
    client1, client2, client3 = clients_connection
    container1, container2, container3 = container_ids[:3]

    async with client3.connect(container3[0]) as api:
        address3 = await api.state.account_address()
        start_balance3 = await api.state.balance()
        await api.blob.submit(Blob(b'abc', b'client3'))

    async with client2.connect(container2[0]) as api:
        address2 = await api.state.account_address()
        start_balance2 = await api.state.balance()
        await api.blob.submit(Blob(b'abc', b'client2'))

    async with client1.connect(container1[0]) as api:
        start_balance1 = await api.state.balance()
        await api.blob.submit(Blob(b'abc', b'client1'))
        await asyncio.sleep(5)
        new_balance3 = await api.state.balance_for_address(address3)
        new_balance2 = await api.state.balance_for_address(address2)
        new_balance1 = await api.state.balance()

        assert new_balance3.amount < start_balance3.amount
        assert new_balance2.amount < start_balance2.amount
        assert new_balance1.amount < start_balance1.amount

        await api.state.transfer(address3, 20)
        await api.state.transfer(address2, 20)

        await asyncio.sleep(5)
        assert (await api.state.balance()).amount < new_balance1.amount - 40
        assert (await api.state.balance_for_address(address2)).amount == new_balance2.amount + 20
        assert (await api.state.balance_for_address(address3)).amount == new_balance3.amount + 20

        await api.state.grant_fee(address2, 10000)
        await api.state.revoke_grant_fee(address2)


@pytest.mark.asyncio
async def test_undelegate(clients_connection, container_ids, validator_addresses):
    client1 = clients_connection[0]
    container1 = container_ids[0]
    validator1 = validator_addresses[0]
    try:
        async with client1.connect(container1[0]) as api:
            await api.blob.submit(Blob(b'abc', b'client3'))
            try:
                amount_before_delegation = (
                    await api.state.query_delegation(validator1)).delegation_response.balance.amount
            except ValueError:
                amount_before_delegation = 0

            await api.state.delegate(validator1, 10000)
            await api.state.undelegate(validator1, 1000)

            assert (await api.state.query_delegation(
                validator1)).delegation_response.balance.amount == amount_before_delegation + 9000

            query_unbonding1 = await api.state.query_unbonding(validator1)
            undelegate = await api.state.undelegate(validator1, 9000)
            query_unbonding2 = await api.state.query_unbonding(validator1)

            assert len(query_unbonding1.unbond.entries) + 1 == len(query_unbonding2.unbond.entries)

            await api.state.cancel_unbonding_delegation(validator1, 3000, undelegate.height)
            query_unbonding3 = await api.state.query_unbonding(validator1)

            assert query_unbonding2.unbond.entries[-1].balance - 3000 == query_unbonding3.unbond.entries[-1].balance

            query_delegation = await api.state.query_delegation(validator1)
            with pytest.raises(ValueError):
                await api.state.undelegate(validator1, query_delegation.delegation_response.balance.amount + 1000)
            await api.state.undelegate(validator1, query_delegation.delegation_response.balance.amount)
    except ValueError as e:
        if 'too many unbonding delegation entries for' in e.args[0]:
            print(
                """ The unbound pool is full. To test the functions undelegate, query_unbonding,
                cancel_unbonding_delegation the network needs to be recreated
                """
            )


@pytest.mark.asyncio
async def test_delegating(clients_connection, container_ids, validator_addresses):
    client1 = clients_connection[0]
    container1 = container_ids[0]
    validator1 = validator_addresses[0]

    async with client1.connect(container1[0]) as api:
        await api.blob.submit(Blob(b'abc', b'client3'))
        try:
            amount_before_delegation = (
                await api.state.query_delegation(validator1)).delegation_response.balance.amount
        except ValueError:
            amount_before_delegation = 0

        await api.state.delegate(validator1, 10000)
        assert (await api.state.query_delegation(
            validator1)).delegation_response.balance.amount == amount_before_delegation + 10000

        with pytest.raises(ValueError):
            await api.state.begin_redelegate(validator1, validator1, 3000)
        #     ToDo make tests for begin_redelegate with different validators

        with pytest.raises(ValueError):
            await api.state.query_redelegations(validator1, validator1)

# "E           ValueError: unmarshaling params for 'state.delegate' (param: *types.valaddress): decoding bech32 failed: invalid checksum (expected zdmcml got 8jepde)"
# 'ConnectionError: [Errno RPC failed; estimating gas: estimating gas: account celestia16ws8cxx9ykl4598qgshvt36mejpkeyvzayndth not found] <ajsonrpc.core.JSONRPC20Error object at 0x76b1b7f9e630>'
# 'ConnectionError: [Errno RPC failed; estimating gas: estimating gas: rpc error: code = unknown desc = failed to execute message; message index: 0: fee allowance already exists: invalid request [celestiaorg/cosmos-sdk@v1.25.0-sdk-v0.46.16/x/feegrant/keeper/msg_server.go:42] with gas wanted: '18446744073709551615' and gas used: '63734' ] <ajsonrpc.core.JSONRPC20Error object at 0x746777f472f0>'
# ConnectionError: [Errno RPC failed; estimating gas: estimating gas: rpc error: code = unknown desc = failed to execute message; message index: 0: too many unbonding delegation entries for (delegator, validator) tuple [celestiaorg/cosmos-sdk@v1.25.0-sdk-v0.46.16/baseapp/baseapp.go:886] with gas wanted: '18446744073709551615' and gas used: '68324' ] <ajsonrpc.core.JSONRPC20Error object at 0x7707660d8470>
# 'E           ConnectionError: [Errno RPC failed; estimating gas: estimating gas: rpc error: code = unknown desc = failed to execute message; message index: 0: too many unbonding delegation entries for (delegator, validator) tuple [celestiaorg/cosmos-sdk@v1.25.0-sdk-v0.46.16/baseapp/baseapp.go:886] with gas wanted: '18446744073709551615' and gas used: '68321' ] <ajsonrpc.core.JSONRPC20Error object at 0x7675953fc6b0>'
# 'RPC failed; estimating gas: estimating gas: rpc error: code = unknown desc = failed to execute message; message index: 0: cannot redelegate to the same validator [celestiaorg/cosmos-sdk@v1.25.0-sdk-v0.46.16/baseapp/baseapp.go:886] with gas wanted: '18446744073709551615' and gas used: '63967' '
