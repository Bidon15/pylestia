import asyncio

import pytest
import pytest_asyncio

from celestia.node_api import Client
from tests.utils import start_testnet, stop_testnet, get_container_id


@pytest.fixture(scope='session')
def container_ids():
    if containers := get_container_id(return_all=True):
        yield containers
    else:
        start_testnet()
        if containers := get_container_id(30, return_all=True):
            yield containers
            stop_testnet()
        assert containers, "Failed to start testnet"


@pytest_asyncio.fixture(scope='session')
async def clients_connection(container_ids, validator_addresses, bridge_addresses, light_address):
    client1 = Client(port=container_ids['bridge'][0]['port'])
    cnt = 60
    while cnt:
        try:
            async with client1.connect(container_ids['bridge'][0]['auth_token']) as api:
                addresses = [*validator_addresses, *bridge_addresses, *light_address]
                balances = await asyncio.gather(*[api.state.balance_for_address(address) for address in addresses])
                if all(list(map(lambda balance: balance.amount != 0, balances))):
                    break
        except Exception:
            pass
        cnt -= 1
        await asyncio.sleep(1)
    assert cnt, """Cannot connect to testnet"""
    return True


@pytest.fixture(scope='session')
def bridge_address():
    yield 'celestia1t52q7uqgnjfzdh3wx5m5phvma3umrq8k6tq2p9'


@pytest.fixture(scope='session')
def light_address():
    yield ('celestia1ll9pjlvy8cg7ux3pr98sc96nlpwgzt48j2mjwz',)


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
