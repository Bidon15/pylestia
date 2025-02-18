import pytest

from celestia.node_api import Client

@pytest.mark.asyncio
async def test_testnet(clients_connection, container_ids):
    container = container_ids['bridge'][0]
    client = Client(port=container['port'])
    async with client.connect(container['auth_token']) as api:
        balance = await api.state.balance()
        assert balance.amount