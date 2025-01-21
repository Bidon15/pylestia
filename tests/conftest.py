import asyncio

import pytest
import pytest_asyncio

from celestia.node_api import Client
from tests.utils import start_testnet, stop_testnet, get_auth_token, get_container_id


@pytest.fixture(scope='session')
def container_id():
    if container_id := get_container_id():
        yield container_id
    else:
        start_testnet()
        if container_id := get_container_id(30):
            yield container_id
            stop_testnet()
        assert container_id, "Failed to start testnet"


@pytest_asyncio.fixture(scope='session')
async def auth_token(container_id):
    auth_token = get_auth_token(container_id)
    assert auth_token, "Failed to get auth token"
    cnt = 30
    client = Client('localhost', 26658)
    while cnt:
        try:
            async with client.connect(auth_token) as api:
                balance = await api.state.balance()
                if balance.amount:
                    break
        except Exception:
            pass
        cnt -= 1
        await asyncio.sleep(1)
    assert cnt, """Cannot connect to testnet"""
    return auth_token


@pytest.fixture(scope='session')
def bridge_address():
    yield 'celestia1t52q7uqgnjfzdh3wx5m5phvma3umrq8k6tq2p9'
