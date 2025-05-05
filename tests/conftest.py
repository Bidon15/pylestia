"""
Pytest configuration and fixtures for pylestia tests.

This module contains the test fixtures needed to run pylestia tests,
including Docker container management for the Celestia testnet.
"""

import asyncio
from time import sleep
from typing import Dict, Tuple, Any

import pytest
import pytest_asyncio

# Explicitly set pytest-asyncio configuration
pytest_plugins = ["pytest_asyncio"]
pytestmark = pytest.mark.asyncio

# Configure asyncio settings in code as well to be sure
def pytest_configure(config):
    config.option.asyncio_mode = "auto"
    # Set fixture loop scope to function as recommended by pytest-asyncio
    config._inicache["asyncio_default_fixture_loop_scope"] = "function"
    config._inicache["asyncio_default_test_loop_scope"] = "function"

from pylestia import Client
from tests.docker import Containers
from tests.utils import start_testnet, stop_testnet, get_auth_token


@pytest.fixture(scope="session")
def containers():
    cnt = 10
    need_shutdown = False
    containers = Containers('testnet')
    while cnt:
        if containers:
            break
        if not need_shutdown:
            start_testnet()
            need_shutdown = True
        cnt -= 1
        sleep(10 - cnt)
        containers = Containers('testnet')
    else:
        RuntimeError("Cannot start testnet")
    yield containers
    if need_shutdown:
        stop_testnet()

@pytest.fixture(scope="session")
def ready_nodes():
    yield dict()

@pytest.fixture
async def node_provider(containers, ready_nodes):
    """
    Async fixture that provides access to Celestia nodes in the testnet.
    
    This fixture returns a function that can be used to get a specific node by name.
    The function will initialize the node if it's not already ready, and will cache
    the result for later use.
    
    Args:
        containers: Fixture containing Docker containers for Celestia nodes
        ready_nodes: Dictionary to cache ready nodes
    
    Returns:
        Function that takes a node name and returns a connection to that node
    """
    async def node_provider_(name: str) -> Tuple[Any, Dict[str, Any]]:
        """
        Get a connection to a specific Celestia node.
        
        If the node is not already initialized, this function will start it,
        wait for it to be ready, and then return a connection.
        
        Args:
            name: Name of the node to connect to
            
        Returns:
            Tuple of (client, info) for the requested node
        """
        if name in ready_nodes:
            return ready_nodes[name]
            
        if name == "bridge":
            container = containers["bridge"]
            info = {
                "base_url": "http://localhost:26659",
                "auth_token": "/root/.celestia-bridge/keys/auth_token",
            }
        
        elif name == "full":
            container = containers["full"]
            info = {
                "base_url": "http://localhost:26658",
                "auth_token": "/root/.celestia-full/keys/auth_token",
            }
        
        elif name == "light":
            container = containers["light"]
            info = {
                "base_url": "http://localhost:26657",
                "auth_token": "/root/.celestia-light/keys/auth_token",
            }
        
        else:
            raise RuntimeError(f"Node '{name}' not found")

    # Return a function that takes a node name
    return node_provider_


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
