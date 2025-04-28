"""
pylestia: Python client for the Celestia blockchain platform
===========================================================

This package provides a Python interface for interacting with the Celestia Node API.
It supports all v0.11.0+ features including Share Version 1 (blob signers).

Main components:
- Client: Main client for connecting to a Celestia node
- Types: Core data structures for working with Celestia
- Node API: Access to all Celestia node APIs

For more information, visit: https://github.com/Bidon15/pylestia
"""

__version__ = "0.2.1"

# Import directly from pylestia's modules
from pylestia.node_api import Client

# Re-export common types at package level for convenience
from pylestia.types import Namespace, Blob

# Make node_api module available at package level
from pylestia import node_api