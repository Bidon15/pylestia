import pytest

from celestia.node_api import Client


@pytest.mark.asyncio
async def test_das(clients_connection, container_ids):
    light_client = Client(port=container_ids['light'][0]['port'])

    async with light_client.connect(container_ids['light'][0]['auth_token']) as api:
        await api.das.wait_catch_up()
        assert (await api.das.sampling_stats()).catch_up_done
