import asyncio

import pytest

from celestia.node_api import Client


@pytest.mark.asyncio
async def test_header(auth_token):
    client = Client()
    async with client.connect(auth_token) as api:
        local_head = await api.header.local_head()
        network_head = await api.header.network_head()
        assert local_head['header']['height'] <= network_head['header']['height']


@pytest.mark.asyncio
async def test_header_subscribe(auth_token):
    result = []
    client = Client()
    async with client.connect(auth_token) as api:
        async with asyncio.timeout(30):
            async for header in api.header.subscribe():
                result.append(header)
                if len(result) == 3:
                    break
    assert len(result) == 3
