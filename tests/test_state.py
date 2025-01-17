import pytest

from celestia.node_api import Client


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
