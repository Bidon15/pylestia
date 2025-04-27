# py-celestia Quick Start Guide

This guide will help you get started with py-celestia, a Python client for interacting with the Celestia network.

## Prerequisites

- Python 3.10 or higher
- A running Celestia node (light node or bridge node)
- A funded wallet associated with your node

## Installation

Install py-celestia using pip:

```bash
pip install pycelestia
```

Or directly from the repository:

```bash
git clone https://github.com/your-org/py-celestia.git
cd py-celestia
pip install -e .
```

## Setting up a Celestia Node

If you don't have a Celestia node running yet, follow the [official Celestia documentation](https://docs.celestia.org/nodes/light-node) to set up a light node.

Quick steps to run a local light node:

```bash
# Install celestia-node
curl -sSL https://install.celestia.org | bash

# Initialize the light node
celestia light init

# Start the light node (replace network_version with the current version)
celestia light start --core.ip rpc-mocha.pops.one --p2p.network mocha
```

### Getting Your Authentication Token

Once your node is running, you'll need the authentication token:

```bash
# Get the auth token from your node
AUTH_TOKEN=$(celestia light auth admin)
echo $AUTH_TOKEN
```

Save this token for use with py-celestia.

## Basic Usage

Here's a simple example of how to connect to a Celestia node and check your wallet balance:

```python
import asyncio
from celestia.node_api import Client

async def get_balance():
    # Connect to a local Celestia node
    client = Client(url="ws://localhost:26658")
    
    # Replace with your authentication token
    auth_token = "your_auth_token_here"
    
    async with client.connect(auth_token) as api:
        # Check your wallet balance
        balance = await api.state.balance()
        print(f"Wallet balance: {balance}")
        
        # Get node information
        node_info = await api.p2p.info()
        print(f"Node ID: {node_info.get('ID')}")

if __name__ == "__main__":
    asyncio.run(get_balance())
```

## Submitting a Blob

Submitting data to Celestia is done through blobs. Here's how to submit a "Hello, World!" blob:

```python
import asyncio
import secrets
from celestia.node_api import Client
from celestia.types.common_types import Namespace, Blob

async def submit_hello_world():
    client = Client(url="ws://localhost:26658")
    auth_token = "your_auth_token_here"
    
    # Generate a random namespace
    namespace = Namespace(secrets.token_bytes(8))
    
    # Create a blob with your data
    data = b"Hello, World!"
    blob = Blob(namespace, data)
    
    async with client.connect(auth_token) as api:
        # Submit the blob
        result = await api.blob.submit(blob)
        print(f"Blob submitted at height: {result.height}")
        print(f"Namespace: {str(namespace)}")
        
        # Retrieve the blob to verify submission
        retrieved_blobs = await api.blob.get_all(result.height, namespace)
        if retrieved_blobs:
            print(f"Retrieved blob data: {retrieved_blobs[0].data}")

if __name__ == "__main__":
    asyncio.run(submit_hello_world())
```

## Running the Hello World Example

The repository includes a complete Hello World example. Run it with:

```bash
# Export your auth token as an environment variable
export AUTH_TOKEN="your_auth_token_here"

# Run the example
python examples/hello_world.py
```

Or specify arguments directly:

```bash
python examples/hello_world.py --rpc ws://localhost:26658 --auth your_auth_token_here --message "Custom message"
```

## Understanding Blob Signers

In Celestia v0.11.0+, all blobs support the concept of a "signer" - an identifier for the account that submitted the blob. This is a critical feature for several reasons:

### What are Blob Signers?

A blob signer is a cryptographic identifier (typically an account address) that's embedded within the blob's metadata. It indicates which account submitted the blob to the Celestia network.

### Why Signers Matter

1. **Accountability**: Signers provide a way to verify who submitted specific data to Celestia.
2. **Permissions**: Future versions of Celestia may enforce namespace permissions where only certain accounts can submit to specific namespaces.
3. **Application Logic**: dApps can use signer information to implement authentication and authorization rules.
4. **Auditing**: Signers create an immutable record of who submitted what data, enabling better audit trails.

### Technical Implementation

When you create a blob with a signer:
- The blob uses Share Version 1 format (vs Version 0 for unsigned blobs)
- The signer data is cryptographically embedded in the blob's shares
- The signer information persists with the blob throughout its lifecycle

### How to Use Signers

```python
from celestia.types.common_types import Namespace, Blob, Base64

# Create a blob with signer information
namespace = Namespace(b'your_namespace')
data = b"Your data"
signer = Base64(b"your_account_address")  # Usually a celestia1... address

# The signer will be included in the blob (Share Version 1)
blob = Blob(namespace, data, signer=signer)

# Submit the blob
result = await api.blob.submit(blob)
```

### Blob With vs. Without Signer

**With Signer (Share Version 1)**:
- Contains cryptographic proof of submitter identity
- Supports accountability and permission management
- Requires the signer parameter when creating the blob
- Used in applications requiring attribution or governance

**Without Signer (Share Version 0)**:
- Traditional blob format without submitter information
- No way to verify who submitted the data
- Simpler but less feature-rich
- Used for purely anonymous data submission

```python
# Blob WITHOUT signer (Share Version 0)
blob_anonymous = Blob(namespace, data)  

# Blob WITH signer (Share Version 1)
blob_signed = Blob(namespace, data, signer=signer)
```

## Common Operations

### Retrieving Blobs

```python
# Get all blobs at a specific height under a namespace
blobs = await api.blob.get_all(height, namespace)

# Get a specific blob by commitment
blob = await api.blob.get(height, namespace, commitment)
```

### Subscribing to Blobs

```python
# Subscribe to new blobs under a specific namespace
async for result in api.blob.subscribe(namespace):
    print(f"New blob at height {result.height}")
    for blob in result.blobs:
        print(f"Data: {blob.data}")
```

### Network and State Operations

```python
# Get network information
network_info = await api.p2p.info()

# Get connected peers
peers = await api.p2p.peers()

# Check header at specific height
header = await api.header.get_by_height(height)
```

## Handling Errors

py-celestia provides improved error handling in v0.11.0+:

```python
from celestia.types.errors import ErrorCode

try:
    result = await api.blob.submit(blob)
except ValueError as e:
    # Handle specific error scenarios
    if "invalid namespace" in str(e).lower():
        print("The namespace is invalid")
    elif "blob size" in str(e).lower():
        print("The blob size is invalid")
    else:
        raise
```

## Next Steps

- Check the [examples directory](../examples/) for more usage examples
- Explore the [API documentation](./API.md) for detailed information about available methods
- See the [test directory](../tests/) for implementation examples

For more information about the Celestia network, visit the [official Celestia documentation](https://docs.celestia.org/).