import pytest

from celestia.node_api import Client
from celestia.node_api.blob import Blob


@pytest.mark.asyncio
async def test_send_blobs(auth_token):
    client = Client()
    async with client.connect(auth_token) as api:
        blobs = await api.blob.get_all(1, b'abc')
        assert blobs is None

        result = await api.blob.submit(
            Blob(b'abc', b'0123456789'),
            Blob(b'abc', b'QWERTYUIOP'),
            Blob(b'xyz', b'ASDFGHJKL'),
        )

        assert len(result.commitments) == 3

        blobs = await api.blob.get_all(result.height, b'abc')
        assert len(blobs) == 2
        assert blobs[0].data == b'0123456789'
        assert blobs[0].commitment == result.commitments[0]

        assert blobs[1].data == b'QWERTYUIOP'
        assert blobs[1].commitment == result.commitments[1]

        blobs = await api.blob.get_all(result.height, b'xyz')
        assert len(blobs) == 1
        assert blobs[0].data == b'ASDFGHJKL'
        assert blobs[0].commitment == result.commitments[2]

        blob = await api.blob.get(1, b'abc', b'ASDFGHJKL')
        assert blob is None

        blob = await api.blob.get(result.height, b'abc', result.commitments[1])
        assert len(blobs) == 1
        assert blob.data == b'QWERTYUIOP'

        proof = await api.blob.get_proof(1, b'abc', b'ASDFGHJKL')
        assert proof is None

        proof = await api.blob.get_proof(result.height, b'abc', result.commitments[1])
        assert proof is not None

        included = await api.blob.included(result.height, b'xyz', proof, result.commitments[1])
        assert not included

        included = await api.blob.included(result.height, b'abc', proof, result.commitments[1])
        assert included

        # com_proof = await api.blob.get_commitment_proof(result.height, b'abc', b'345')
        # assert com_proof is not None
        # ToDo: Figure out how to test the data type shareCommitment, blob.CommitmentProof
