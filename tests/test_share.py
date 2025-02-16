import pytest

from celestia.common_types import Blob
from celestia.node_api import Client
from celestia.types.share import SampleCoords


@pytest.mark.asyncio
async def test_share(clients_connection, container_ids):
    container = container_ids['bridge'][0]
    client = Client(port=container['port'])
    async with client.connect(container['auth_token']) as api:
        result = await api.blob.submit(
            Blob(b'abc', b'0123456789'),
            Blob(b'abc', b'QWERTYUIOP'),
            Blob(b'xyz', b'ASDFGHJKL'),
        )

        eds = await api.share.get_eds(result.height)
        gnd = await api.share.get_namespace_data(result.height, b'abc')
        range_data = await api.share.get_range(result.height, 1, 2)
        samples = await api.share.get_samples((await api.header.get_by_height(result.height)),
                                              [SampleCoords(row=0, col=1)])
        coords_data = await api.share.get_share(result.height, 0, 1)
        assert coords_data == samples[0] == range_data.proof.data[0] == eds.data_square[1] == gnd[0].shares[0]
        await api.share.get_available(result.height)
