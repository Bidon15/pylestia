import asyncio

import pytest
import pytest_asyncio

from celestia.node_api import Client


@pytest_asyncio.fixture(scope='session')
async def das_client_connection(container_ids, light_address):
    light_container = container_ids[3]
    client1 = Client(port=light_container[1])
    cnt = 60
    while cnt:
        try:
            async with client1.connect(light_container[0]) as api:
                balance = await api.state.balance_for_address(light_address)
                if balance.amount != 0:
                    break
        except Exception:
            pass
        cnt -= 1
        await asyncio.sleep(1)

    return client1


@pytest.mark.asyncio
async def test_das(container_ids, das_client_connection):
    bridges, light_container = container_ids[:3], container_ids[3]

    async with das_client_connection.connect(light_container[0]) as api:
        await api.das.wait_catch_up()
        assert (await api.das.sampling_stats()).catch_up_done
