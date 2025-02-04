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


@pytest.fixture(scope='session')
def container_ids():
    if containers := get_container_id(return_all=True):
        yield *[(get_auth_token(container[0]), container[1]) for container in containers['bridge']], *[
            (get_auth_token(container[0], 'light'), container[1]) for container in containers['light']]
    else:
        start_testnet()
        if containers_id := get_container_id(30, return_all=True):
            yield *[(get_auth_token(container_id[0]), container_id[1]) for container_id in containers_id['bridge']], *[
                (get_auth_token(container_id[0], 'light'), container_id[1]) for container_id in containers_id['light']]
            stop_testnet()
        assert containers_id, "Failed to start testnet"


@pytest_asyncio.fixture(scope='session')
async def auth_token(container_id):
    auth_token = get_auth_token(container_id)
    assert auth_token, "Failed to get auth token"
    cnt = 30
    client = Client()
    while cnt:
        try:
            async with client.connect(auth_token) as api:
                balance = await api.state.balance()
                if balance.amount:
                    break
        except Exception as exc:
            pass
        cnt -= 1
        await asyncio.sleep(1)
    assert cnt, """Cannot connect to testnet"""
    return auth_token


@pytest.fixture(scope='session')
def bridge_address():
    yield 'celestia1t52q7uqgnjfzdh3wx5m5phvma3umrq8k6tq2p9'


@pytest.fixture(scope='session')
def light_address():
    yield 'celestia1ll9pjlvy8cg7ux3pr98sc96nlpwgzt48j2mjwz'


@pytest.fixture(scope='session')
def bridge_addresses():
    yield ('celestia1t52q7uqgnjfzdh3wx5m5phvma3umrq8k6tq2p9',
           'celestia16ws8cxx9ykl4598qgshvt36mejpkeyvzayndth',
           'celestia10yeexpgcpx88qru4ca63frhw3jqua4qw8swxy0')


@pytest.fixture(scope='session')
def validator_addresses():
    yield ('celestiavaloper1tzkpek429yxtvrshqh5yvqhvq4ydu3pjrshjhh',
           'celestiavaloper1uqmt6u5zwzucxjkg7pd30qw8lc6l4c8xxv9288',
           'celestiavaloper12crcjleegs25gp8wdx3nwn2m9kvfdmc34apd28')
