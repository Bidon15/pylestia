"""
pylestia: Python client for the Celestia blockchain platform
===========================================================

This package provides a Python interface for interacting with the Celestia Node API.
It supports all v0.11.0+ features including Share Version 1 (blob signers).

Main components:
- Client: Main client for connecting to a Celestia node
- Types: Core data structures for working with Celestia
- Node API: Access to all Celestia node APIs

For more information, visit: https://github.com/Alesh/pylestia
"""

__version__ = "0.1.7"

# Provide API classes at package level
from celestia.node_api import Client