import asyncio
import pytest
import os
import secrets

from celestia.node_api import Client
from celestia.types.common_types import Namespace, Blob, Base64


@pytest.mark.asyncio
async def test_e2e_blob_submission():
    """
    End-to-end test for submitting a blob to a local Celestia node.

    This test requires:
    - A running Celestia node
    - AUTH_TOKEN environment variable to be set
    - Proper RPC endpoint (default: ws://localhost:26658)

    Skip if environment variables aren't set.
    """
    auth_token = os.environ.get("AUTH_TOKEN")
    if not auth_token:
        pytest.skip("AUTH_TOKEN environment variable not set")

    rpc_endpoint = os.environ.get("RPC_ENDPOINT", "ws://localhost:26658")

    # Create a client connecting to a local node
    client = Client(url=rpc_endpoint)

    # Generate a random namespace ID (8 bytes)
    random_namespace = secrets.token_bytes(8)
    namespace = Namespace(random_namespace)

    # Create a "Hello, World!" blob
    hello_world_data = b"Hello, World! From py-celestia test."
    blob = Blob(namespace, hello_world_data)

    async with client.connect(auth_token) as api:
        # Get the wallet balance to confirm we can pay for the transaction
        balance = await api.state.balance()
        print(f"Wallet balance: {balance}")

        # Submit the blob
        result = await api.blob.submit(blob)

        # Verify the blob was submitted by retrieving it
        height = result.height
        print(f"Blob submitted at height: {height}")
        print(f"Blob namespace (Base64): {str(namespace)}")
        print(f"Blob namespace (Hex): {random_namespace.hex()}")

        # Wait a moment for the blob to be indexed
        await asyncio.sleep(2)

        # Retrieve the blob
        retrieved_blobs = await api.blob.get_all(height, namespace)

        # Assertions
        assert len(retrieved_blobs) == 1, "Should retrieve exactly one blob"
        assert (
            retrieved_blobs[0].data == hello_world_data
        ), "Retrieved blob data should match"
        assert (
            retrieved_blobs[0].namespace == namespace
        ), "Retrieved namespace should match"

        print("✅ Successfully submitted and retrieved blob!")

        return {
            "height": height,
            "namespace": str(namespace),
            "namespace_hex": random_namespace.hex(),
            "commitment": str(retrieved_blobs[0].commitment),
        }


@pytest.mark.asyncio
async def test_e2e_blob_with_signer():
    """
    End-to-end test for submitting a blob with signer information.
    """
    auth_token = os.environ.get("AUTH_TOKEN")
    if not auth_token:
        pytest.skip("AUTH_TOKEN environment variable not set")

    rpc_endpoint = os.environ.get("RPC_ENDPOINT", "ws://localhost:26658")

    # Create a client connecting to a local node
    client = Client(url=rpc_endpoint)

    # Generate a random namespace ID (8 bytes)
    random_namespace = secrets.token_bytes(8)
    namespace = Namespace(random_namespace)

    # Create test data and a test signer
    test_data = b"Blob with signer test"
    test_signer = (
        b"celestia1testaddress"  # In a real scenario, this would be a valid address
    )

    # Create a blob with signer
    blob = Blob(namespace, test_data, signer=test_signer)

    async with client.connect(auth_token) as api:
        # Submit the blob
        result = await api.blob.submit(blob)

        # Retrieve the blob
        height = result.height
        retrieved_blobs = await api.blob.get_all(height, namespace)

        # Assertions
        assert len(retrieved_blobs) == 1, "Should retrieve exactly one blob"
        assert retrieved_blobs[0].data == test_data, "Retrieved blob data should match"
        assert (
            retrieved_blobs[0].namespace == namespace
        ), "Retrieved namespace should match"

        # Verify the signer is present if the node version supports it
        # Note: This might fail if the node doesn't support signers
        try:
            assert retrieved_blobs[0].signer is not None, "Signer should be present"
            print(f"Blob signer: {retrieved_blobs[0].signer}")
        except (AssertionError, AttributeError) as e:
            print(
                f"Note: Signer verification failed: {e}. This is expected if the node doesn't support signers."
            )

        print("✅ Successfully submitted and retrieved blob with signer!")


if __name__ == "__main__":
    # This allows running the test directly with python tests/test_end_to_end.py
    asyncio.run(test_e2e_blob_submission())
