import pytest

from .utils import start_testnet, stop_testnet, get_auth_token, get_container_id


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
def auth_token(container_id):
    auth_token = get_auth_token(container_id)
    assert auth_token, "Failed to get auth token"
    yield auth_token


@pytest.fixture(scope='session')
def bridge_address():
    yield 'celestia1t52q7uqgnjfzdh3wx5m5phvma3umrq8k6tq2p9'
