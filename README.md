# pylestia

This module provides a Python interface for interacting with the Celestia Node API. All methods communicate with the API via JSON-RPC, offering a flexible and developer-friendly solution for integrating Celestia functionality into applications.

It is designed for developers who want to interact with the Celestia network without dealing with the complexities of low-level RPC request handling.

## Getting Started

**Please see our [Quick Start Guide](docs/QUICKSTART.md) to get up and running with pylestia!**

We also have [example code](examples/) to help you integrate pylestia into your projects.

## Compatibility

**IMPORTANT**: This library is ONLY compatible with celestia-types v0.11.0 and later. It is NOT backward compatible with earlier versions.

Built exclusively for celestia-types v0.11.0+, supporting:

- Blob signer information (Share Version 1)
- Improved error handling for blob submission
- Public ShareProof fields
- Updated commitment formats

This library requires celestia-types v0.11.0 and is designed to work with the latest Celestia node versions.

## 🚀 Installation

### Recommended: Using Poetry

```sh
# Add pylestia to your project dependencies
poetry add pylestia

# Or specify a specific version
poetry add pylestia==0.2.1
```

### Alternative: Using pip

```sh
pip install pylestia
```

## 🔧 Usage

### Connecting to Celestia Node

Below is an example of how to connect to a real Celestia node using its RPC endpoint.

```python
from pylestia import Client

# Configuration for connecting to a Celestia node
node_url = "https://celestia-rpc.example.com"  # Replace with the actual RPC node URL
auth_token = "your-auth-token"  # Replace with your authentication token (if required)

# Initialize the client
client = Client(node_url)

# Example usage of the API
async with client.connect(auth_token) as api:
    balance = await api.state.balance()
```

### Custom Deserialization Example

```python
from pydantic import BaseModel

class CustomBalanceModel(BaseModel):
    amount: int
    denom: str

async with client.connect(auth_token) as api:
    # The `deserializer` parameter allows you to transform raw API data into a desired format
    last_height = await api.header.local_head(deserializer=lambda data: int(data['header']['height']))
    isinstance(last_height, int) # True
    # Use the Pydantic model to validate and transform the balance response
    balance = await api.state.balance(deserializer=CustomBalanceModel.model_validate)
    isinstance(balance.amount, int) # True
```

## Contributing

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Rust & Cargo](https://www.rust-lang.org/tools/install) (required for compiling the extension)
- [Poetry](https://python-poetry.org/docs/#installation) (for development)

For those interested in contributing to pylestia:

```sh
# Clone the repository
git clone https://github.com/Bidon15/pylestia.git
cd pylestia

# Install dependencies with Poetry
poetry install

# Run Python-only tests (don't require Rust compilation)
poetry run pytest tests/test_models.py tests/test_blob_signer.py tests/test_python_only.py

# For full testing including Rust extensions
pip install maturin
maturin develop
poetry run pytest
```

### Building from Source

pylestia contains Rust extensions, so you'll need:

1. [Rust and Cargo](https://www.rust-lang.org/tools/install) installed
2. A supported Python version (3.10+)

To build the package:

```sh
# Install maturin if you don't have it
pip install maturin

# Build the package (will compile Rust code)
maturin build --release

# The built package can be installed with
pip install target/wheels/pylestia-0.2.0-*.whl
```
