"""
Celestia data types for the v0.11.0+ celestia-types compatibility.

This package provides the fundamental data types needed to interact with the
Celestia network, including blobs, namespaces, and error handling. It has been
updated to support celestia-types v0.11.0 features like Share Version 1 (signed blobs).

Key types:
- Blob: Data structure for storing content in the Celestia network
- Namespace: Unique identifier for categorizing blobs
- Commitment: Cryptographic proof for data integrity
- Base64: Utility class for base64 encoding/decoding
- ErrorCode: Error codes for blob submission and other operations
"""

import sys

# Core data types
from .common_types import Base64, Blob, Commitment, Namespace

# Error handling
from .errors import ErrorCode, parse_error_message

# Compatibility imports for type checking
if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack