import pytest

from celestia.node_api import Client


@pytest.mark.asyncio
async def test_share(container_ids):
    bridges, light_container = container_ids[:3], container_ids[3]
    client = Client(port=bridges[0][1])
    async with client.connect(light_container[0][0]) as api:
        eds = await api.share.get_eds(5)
        assert (await api.share.get_namespace_data(1, b'qweqwe')) == []
        range_data = await api.share.get_range(5, 0, 1)
        samples = await api.share.get_samples((await api.header.get_by_height(5)), [{'row': 0, 'col': 1}])
        coords_data = await api.share.get_share(5, 0, 1)
        assert range_data['Proof']['data'][0] == samples[0] == coords_data == eds.data_square[0]
        await api.share.get_available(5)
