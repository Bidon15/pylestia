# pylestia Package Structure

## Overview

This package provides a Python interface for interacting with the Celestia Node API. All methods communicate with the API via JSON-RPC, offering a flexible and developer-friendly solution for integrating Celestia functionality into applications.

## Directory Structure

```
pylestia/
├── __init__.py        # Main package initialization, exports Client
├── pylestia_core.so   # Compiled Rust extension (not in repo)
├── node_api/          # Node API interface
│   ├── __init__.py    # Defines Client and NodeAPIContext
│   ├── blob.py        # Blob API endpoint
│   ├── das.py         # DAS API endpoint
│   ├── fraud.py       # Fraud API endpoint
│   ├── header.py      # Header API endpoint
│   ├── p2p.py         # P2P API endpoint
│   ├── rpc/           # RPC client implementation
│   ├── share.py       # Share API endpoint
│   └── state.py       # State API endpoint
└── types/             # Type definitions
    ├── __init__.py    # Exports all types
    ├── blob.py        # Blob-related types
    ├── common_types.py # Common data structures
    ├── das.py         # DAS-related types
    ├── errors.py      # Error handling
    ├── header.py      # Header-related types
    ├── p2p.py         # P2P-related types
    ├── share.py       # Share-related types
    └── state.py       # State-related types
```

## Version History

- **0.2.1** - Streamlined package with consistent pylestia namespace
- **0.2.0** - Package restructuring
- **0.1.7** - Initial release

## Usage

```python
from pylestia import Client
from pylestia.types import Namespace, Blob

# Initialize client
client = Client("http://localhost:26658")

# Connect and use the API
async with client.connect("auth_token") as api:
    # Get node information
    node_info = await api.p2p.info()

    # Submit a blob
    namespace = Namespace(b"my-namespace")
    blob = Blob(namespace=namespace, data=b"Hello, World!")
    result = await api.blob.submit(blob)
```
