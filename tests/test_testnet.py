import pytest

from celestia.node_api import Client


@pytest.mark.asyncio
async def test_testnet(node_provider):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])
    async with client.connect(auth_token) as api:
        balance = await api.state.balance()
        assert balance.amount
