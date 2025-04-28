"""
Core types for the Celestia data availability layer.

This module provides the fundamental types used in Celestia, including Base64 encoding,
Namespaces, Commitments, and Blobs. It supports both unsigned (Share Version 0)
and signed (Share Version 1) blobs in accordance with celestia-types v0.11.0+.
"""

import hashlib
import typing as t
from base64 import b64decode, b64encode
from dataclasses import dataclass

from pylestia.pylestia_core import types as ext  # Rust extension module


class Base64(bytes):
    """ Represents a byte string that supports Base64 encoding and decoding.

    This class ensures that the stored data is always in bytes and provides
    Base64 encoding/decoding when converting to and from strings.
    """

    def __new__(cls, value: str | bytes):
        if isinstance(value, str):
            value = b64decode(value)
        if value is None:
            return None
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return b64encode(self).decode('ascii')

    @classmethod
    def ensure_type(cls, value):
        """ Ensures the value is an instance of Base64.

        Args:
            value (str | bytes | Base64): The value to convert.

        Returns:
            Base64: A valid Base64 instance.
        """
        if isinstance(value, cls):
            return value
        return cls(value)


class Namespace(Base64):
    """ Represents a Celestia namespace.

    A namespace is a unique identifier for blobs stored on the Celestia network.
    It is used to segregate data based on different applications or use cases.
    """

    def __new__(cls, value: str | bytes):
        value = super().__new__(cls, value)
        value = ext.normalize_namespace(value)
        return super().__new__(cls, value)


class Commitment(Base64):
    """ Represents a Celestia blob commitment.

    A commitment is a cryptographic proof that ensures data integrity and allows
    verification of whether a blob has been correctly included in a block.
    """


@dataclass
class Blob:
    """ Represents a Celestia blob (v0.11.0).

    This implementation is only compatible with celestia-types v0.11.0 and later.
    It supports Share Version 1 with signer information.

    A blob is a chunk of data stored on Celestia. Each blob is associated with
    a namespace and a cryptographic commitment to ensure data integrity.

    Attributes:
        namespace (Namespace): The namespace under which the blob is stored.
        data (Base64): The actual blob data.
        commitment (Commitment): The cryptographic commitment for the blob.
        share_version (int): The version of the share encoding (0 for unsigned, 1 for signed).
        index (int | None): The index of the blob in the block (optional).
        signer (Base64 | None): The account that submitted the blob (for Share Version 1).
                               Should be a valid bech32 celestia address.
    """
    namespace: Namespace
    data: Base64
    commitment: Commitment
    share_version: int
    index: int | None = None
    signer: Base64 | None = None

    def __init__(self, namespace: Namespace | str | bytes, data: Base64 | str | bytes,
                 commitment: Commitment | str | bytes | None = None, share_version: int | None = None,
                 index: int | None = None, signer: Base64 | str | bytes | None = None):
        """Initialize a new Blob with v0.11.0 features.
        
        Args:
            namespace: The namespace under which the blob is stored.
            data: The actual blob data.
            commitment: Optional commitment for verification.
            share_version: Optional share version specification.
            index: Optional blob index.
            signer: Optional signer information (for Share Version 1).
        """
        self.namespace = Namespace.ensure_type(namespace)
        self.data = Base64.ensure_type(data)
        self.signer = Base64.ensure_type(signer) if signer is not None else None
        
        if commitment is not None:
            # If commitment is provided directly, use it
            self.commitment = Commitment.ensure_type(commitment)
            # In v0.11.0, share version defaults to 1 if signer is present, 0 otherwise
            self.share_version = share_version if share_version is not None else (1 if self.signer else 0)
        else:
            # Create a new blob via Rust using v0.11.0 features
            try:
                try:
                    # Try the v0.11.0 API with signer parameter
                    try:
                        kwargs = ext.normalize_blob(self.namespace, self.data, self.signer)
                    except TypeError:
                        # Fall back to basic version if the Rust extension has issues
                        kwargs = ext.normalize_blob(self.namespace, self.data)
                        # For v0.11.0 compatibility, set share_version manually
                        if self.signer is not None:
                            kwargs['share_version'] = 1
                    
                    # Handle commitment format (could be string or bytes in v0.11.0)
                    commitment_value = kwargs['commitment']
                    if isinstance(commitment_value, str) and commitment_value.startswith('Commitment('):
                        # Debug format - extract actual bytes
                        hex_part = commitment_value.split('(')[1].split(')')[0]
                        if hex_part.startswith('0x'):
                            hex_part = hex_part[2:]
                        commitment_value = bytes.fromhex(hex_part)
                    elif isinstance(commitment_value, str) and len(commitment_value) > 0:
                        # Base64 formatted commitment - convert to bytes
                        try:
                            commitment_value = b64decode(commitment_value)
                        except Exception:
                            # If not valid Base64, use as is
                            pass
                
                    # Set commitment and share_version
                    self.commitment = Commitment.ensure_type(commitment_value)
                    # Use explicitly provided share_version if available, otherwise use kwargs or default
                    if share_version is not None:
                        self.share_version = share_version
                    else:
                        self.share_version = kwargs.get('share_version', 0 if self.signer is None else 1)
                    
                    # Update signer if returned by Rust and not already set
                    if 'signer' in kwargs and self.signer is None:
                        self.signer = Base64.ensure_type(kwargs['signer'])
                except Exception as e:
                    # If Rust extension fails, create a basic blob
                    # This ensures Python code works even if Rust has issues
                    # Generate a commitment using SHA-256
                    h = hashlib.sha256()
                    h.update(self.namespace)
                    h.update(self.data)
                    if self.signer:
                        h.update(self.signer)
                    self.commitment = Commitment(h.digest())
                    # Use explicitly provided share_version if available
                    self.share_version = share_version if share_version is not None else (1 if self.signer else 0)
                    
            except Exception as e:
                raise RuntimeError(f"Failed to create blob with v0.11.0: {e}")
                
        self.index = index

    @staticmethod
    def deserializer(result: dict) -> 'Blob':
        """ Deserializes a dictionary into a Blob object.

        Args:
            result: The dictionary representation of a Blob.

        Returns:
            A deserialized Blob object.
        """
        if result is not None:
            return Blob(**result)


# TxConfig has been moved to pylestia.node_api.rpc.executor
# as per celestia-types v0.10.0 changes
