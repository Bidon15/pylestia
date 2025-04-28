# pylestia Quick Start Guide

This guide will help you get started with pylestia, a Python client for interacting with the Celestia network.

## Prerequisites

Before you begin, make sure you have:

- A running Celestia node (light node or bridge node)
- Python 3.10 or higher installed

## Installation

Install pylestia using pip:

```bash
pip install pylestia
```

Or install from source:

```bash
git clone https://github.com/Bidon15/pylestia.git
cd pylestia
pip install -e .
```

## Setting up a Celestia Node

If you don't have a Celestia node running yet, follow the [official Celestia documentation](https://docs.celestia.org/nodes/light-node) to set up a light node.

Here's a quick setup for a light node on the Mocha testnet:

```bash
# Install celestia-node
curl -sSL https://install.celestia.org | bash

# Initialize a light node
celestia light init

# Start the light node
celestia light start --core.ip rpc-mocha.pops.one --p2p.network mocha
```

## Getting Your Authentication Token

After starting your node, get your authentication token:

```bash
AUTH_TOKEN=$(celestia light auth admin)
echo $AUTH_TOKEN
```

Save this token for use with pylestia.

## Basic Usage

Here's a simple example of how to connect to a Celestia node and check your wallet balance:

```python
import asyncio
from pylestia import Client

async def main():
    # Connect to a local Celestia node
    client = Client("http://localhost:26658")

    # Use your authentication token
    async with client.connect("your_auth_token_here") as api:
        # Get account information
        address = await api.state.account_address()
        print(f"Account address: {address}")

        # Check balance
        balance = await api.state.balance()
        print(f"Balance: {balance.amount} {balance.denom}")

# Run the async function
asyncio.run(main())
```

## Submitting Data

Submitting data to Celestia is done through blobs. Here's how to submit a "Hello, World!" blob:

```python
import asyncio
import secrets

from pylestia import Client
from pylestia.types import Namespace, Blob

async def submit_blob():
    client = Client("http://localhost:26658")

    # Connect to the node
    async with client.connect("your_auth_token_here") as api:
        # Create a random namespace (8 bytes)
        random_namespace = secrets.token_bytes(8)
        namespace = Namespace(random_namespace)

        # Create your blob
        blob_data = b"Hello, World!"
        blob = Blob(namespace=namespace, data=blob_data)

        # Submit the blob
        result = await api.blob.submit(blob)
        print(f"Blob submitted at height: {result.height}")

        # Get back the blob to verify
        retrieved_blob = await api.blob.get(result.height, namespace, blob.commitment)
        if retrieved_blob:
            print(f"Retrieved blob data: {retrieved_blob.data}")
        else:
            print("Failed to retrieve blob")

# Run the async function
asyncio.run(submit_blob())
```

## Working with Signers (Share Version 1)

In Celestia v0.11.0+, all blobs support the concept of a "signer" - an identifier for the account that submitted the blob. This is a critical feature for several reasons:

When you submit a blob with a signer, the blob includes information about which account submitted the blob to the Celestia network.

Benefits include:

1. **Accountability**: Signers provide a way to verify who submitted specific data to Celestia.
2. **Permissions**: Future versions of Celestia may enforce namespace permissions where only certain accounts can submit to specific namespaces.
3. **Provenance**: Data consumers can verify the origin of data.

Here's how to submit a blob with a signer:

```python
import asyncio
import secrets

from pylestia.types import Namespace, Blob, Base64
from pylestia import Client

async def submit_signed_blob():
    client = Client("http://localhost:26658")

    # Get a valid signer (must be 20 bytes)
    signer = Base64(b"your_account_address")  # Usually a celestia1... address

    # Connect to the node
    async with client.connect("your_auth_token_here") as api:
        # Get the account address that's submitting the transaction
        account_address = await api.state.account_address()

        # Create a namespace
        namespace = Namespace(secrets.token_bytes(8))

        # Create a blob with signer
        blob = Blob(
            namespace=namespace,
            data=b"Signed blob example",
            signer=signer  # This makes it a Share Version 1 blob
        )

        # The blob's share_version should be 1
        print(f"Blob share version: {blob.share_version}")

        # Submit the blob
        result = await api.blob.submit(blob)
        print(f"Signed blob submitted at height: {result.height}")

        # Retrieve the blob
        retrieved_blob = await api.blob.get(result.height, namespace, blob.commitment)
        if retrieved_blob:
            print(f"Retrieved blob data: {retrieved_blob.data}")
            print(f"Retrieved blob signer: {retrieved_blob.signer}")
        else:
            print("Failed to retrieve blob")

# Run the async function
asyncio.run(submit_signed_blob())
```

## Error Handling

pylestia provides improved error handling in v0.11.0+:

```python
from pylestia.types.errors import ErrorCode

try:
    # Try to submit to a reserved namespace
    reserved_namespace = Namespace(b"\0\0\0\0\0\0\0\0")
    bad_blob = Blob(namespace=reserved_namespace, data=b"This will fail")
    result = await api.blob.submit(bad_blob)
except ValueError as e:
    # Will catch specific errors like "reserved namespace not allowed"
    print(f"Error: {e}")
```

## Further Resources

For more examples, check the [examples directory](https://github.com/Bidon15/pylestia/tree/master/examples) in the pylestia repository.

For more information about the Celestia network, visit the [official Celestia documentation](https://docs.celestia.org/).
