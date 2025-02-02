import pytest

from celestia.node_api import Client

@pytest.mark.asyncio
async def test_testnet(auth_token):
    client = Client()
    async with client.connect(auth_token) as api:
        balance = await api.state.balance()
        assert balance.amount