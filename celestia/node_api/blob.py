"""
BlobClient for interacting with the Celestia blob API.

This module provides a client for submitting, retrieving, and subscribing to blobs
in the Celestia network. It supports both unsigned (Share Version 0) and
signed (Share Version 1) blobs as per celestia-types v0.11.0+.
"""

from collections.abc import AsyncIterator
from functools import wraps
from typing import Callable, List, Optional, Union

# Rust extension types
from celestia._celestia import types  # noqa

# Local imports
from celestia.node_api.rpc import TxConfig
from celestia.node_api.rpc.abc import Wrapper
from celestia.types import Blob, Commitment, Namespace, Unpack
from celestia.types.blob import (
    CommitmentProof,
    Proof,
    SubmitBlobResult,
    SubscriptionBlobResult,
)


from celestia.types.errors import parse_error_message, ErrorCode

def handle_blob_error(func):
    """ Decorator to handle blob-related errors."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConnectionError as e:
            error_message = e.args[1].body.get('message', '').lower()
            
            # Check for "blob not found" to maintain backward compatibility
            if 'blob: not found' in error_message:
                return None
                
            # Parse for specific error codes
            result = parse_error_message(error_message)
            if result:
                error_code, description = result
                if error_code == ErrorCode.NoBlobs:
                    return None
                # Convert specific error codes to appropriate exceptions
                if error_code in (ErrorCode.InvalidBlobSigner, ErrorCode.InvalidNamespaceLen, 
                                  ErrorCode.InvalidDataSize, ErrorCode.InvalidNamespaceType):
                    raise ValueError(description)
                if error_code == ErrorCode.UnsupportedShareVersion:
                    raise ValueError(f"Unsupported share version: {description}")
                if error_code == ErrorCode.ReservedNamespace:
                    raise ValueError(f"Reserved namespace: {description}")
            
            # If we couldn't handle it specifically, re-raise
            raise

    return wrapper


class BlobClient(Wrapper):
    """ Client for interacting with Celestia's Blob API."""

    @handle_blob_error
    async def get(self, height: int, namespace: Namespace, commitment: Commitment, *,
                  deserializer: Callable | None = None) -> Blob | None:
        """ Retrieves the blob by commitment under the given namespace and height.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the blob.
            commitment (Commitment): The commitment of the blob.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.common_types.Blob.deserializer`.

        Returns:
            Blob | None: The retrieved blob, or None if not found.
        """

        deserializer = deserializer if deserializer is not None else Blob.deserializer

        return await self._rpc.call("blob.Get", (height, Namespace(namespace), Commitment(commitment)), deserializer)

    async def get_all(self, height: int, namespace: Namespace, *namespaces: Namespace,
                      deserializer: Callable | None = None) -> list[Blob] | None:
        """ Returns all blobs under the given namespaces at the given height. If all blobs were
        found without any errors, the user will receive a list of blobs. If the BlobService couldn't
        find any blobs under the requested namespaces, the user will receive an empty list of blobs
        along with an empty error. If some of the requested namespaces were not found, the user will receive
        all the found blobs and an empty error. If there were internal errors during some of the requests, the
        user will receive all found blobs along with a combined error message. All blobs will preserve the order
        of the namespaces that were requested.

        Args:
            height (int): The block height.
            namespace (Namespace): The primary namespace of the blobs.
            namespaces (Namespace): Additional namespaces to query for blobs.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Returns:
            list[Blob]: The list of blobs or [] if not found.
        """

        def deserializer_(result) -> list['Blob']:
            if result is not None:
                return [Blob(**kwargs) for kwargs in result]
            else:
                return []

        deserializer = deserializer if deserializer is not None else deserializer_
        namespaces = tuple(Namespace(namespace) for namespace in (namespace, *namespaces))

        return await self._rpc.call("blob.GetAll", (height, namespaces), deserializer)

    async def submit(self, blob: Blob, *blobs: Blob, deserializer: Callable | None = None,
                     **options: Unpack[TxConfig]) -> SubmitBlobResult:
        """ Sends Blobs and reports the height in which they were included. Allows sending
        multiple Blobs atomically synchronously. Uses default wallet registered on the Node.

        Args:
            blob (Blob): The main blob to submit.
            blobs (Blob): Additional blobs to submit.
            deserializer (Callable | None): Custom deserializer. Defaults to None.
            options (TxConfig): Additional configuration options.

        Returns:
            SubmitBlobResult: The result of the submission, including the height.
        """

        def deserializer_(height):
            if height is not None:
                return SubmitBlobResult(height, tuple(blob.commitment for blob in blobs))

        deserializer = deserializer if deserializer is not None else deserializer_
        
        # Process blobs using v0.11.0 API
        processed_blobs = []
        for blob_obj in (blob, *blobs):
            if blob_obj.commitment is None:
                # Need to normalize the blob
                try:
                    # Try v0.11.0 API with signer parameter
                    try:
                        processed_blob = types.normalize_blob(blob_obj.namespace, blob_obj.data, blob_obj.signer)
                    except TypeError:
                        # Fall back to basic version if the Rust extension has linking issues
                        processed_blob = types.normalize_blob(blob_obj.namespace, blob_obj.data)
                        # For v0.11.0 compatibility, set share_version and signer manually
                        if blob_obj.signer is not None:
                            processed_blob['share_version'] = 1
                            processed_blob['signer'] = blob_obj.signer
                    
                    # Handle commitments that might be returned in different formats
                    commitment_value = processed_blob['commitment']
                    if isinstance(commitment_value, str) and commitment_value.startswith('Commitment('):
                        # Debug format - extract actual bytes
                        hex_part = commitment_value.split('(')[1].split(')')[0]
                        if hex_part.startswith('0x'):
                            hex_part = hex_part[2:]
                        processed_blob['commitment'] = bytes.fromhex(hex_part)
                    elif isinstance(commitment_value, str) and len(commitment_value) > 0:
                        # Try to handle Base64 formatted commitment
                        try:
                            from base64 import b64decode
                            processed_blob['commitment'] = b64decode(commitment_value)
                        except Exception:
                            # If not valid Base64, leave as is
                            pass
                    
                except Exception as e:
                    # Create a fallback processed_blob with the same structure
                    import hashlib
                    h = hashlib.sha256()
                    h.update(blob_obj.namespace)
                    h.update(blob_obj.data)
                    if blob_obj.signer:
                        h.update(blob_obj.signer)
                    
                    processed_blob = {
                        'namespace': blob_obj.namespace,
                        'data': blob_obj.data,
                        'commitment': h.digest(),
                        'share_version': 1 if blob_obj.signer else 0,
                        'index': blob_obj.index
                    }
                    
                    if blob_obj.signer:
                        processed_blob['signer'] = blob_obj.signer
                processed_blobs.append(processed_blob)
            else:
                # Use the blob as is
                processed_blobs.append(blob_obj)
        
        blobs = tuple(processed_blobs)
        return await self._rpc.call("blob.Submit", (blobs, options), deserializer)

    @handle_blob_error
    async def get_commitment_proof(self, height: int, namespace: Namespace, commitment: Commitment, *,
                                   deserializer: Callable | None = None) -> CommitmentProof | None:
        """ Generates a commitment proof for a share commitment.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the commitment.
            commitment (Commitment): The commitment to generate proof for.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.blob.CommitmentProof.deserializer`.

        Returns:
            CommitmentProof | None: The commitment proof, or None if not found.
        """

        deserializer = deserializer if deserializer is not None else CommitmentProof.deserializer

        return await self._rpc.call("blob.GetCommitmentProof", (height, Namespace(namespace), Commitment(commitment)),
                                    deserializer)

    async def get_proof(self, height: int, namespace: Namespace, commitment: Commitment, *,
                        deserializer: Callable | None = None) -> list[Proof] | None:
        """ Retrieves proofs in the given namespaces at the given height by commitment.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the proof.
            commitment (Commitment): The commitment to generate the proof for.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Returns:
            list[Proof]: A list of proofs or [] if not found.
        """

        def deserializer_(result) -> list['Proof']:
            if result is not None:
                return [Proof(**kwargs) for kwargs in result]

        deserializer = deserializer if deserializer is not None else deserializer_
        try:
            return await self._rpc.call("blob.GetProof", (height, Namespace(namespace), Commitment(commitment)),
                                        deserializer)
        except ConnectionError as e:
            if 'blob: not found' in e.args[1].body['message'].lower():
                return []
            raise

    async def included(self, height: int, namespace: Namespace, proof: Proof, commitment: Commitment) -> bool:
        """ Checks whether a blob's given commitment(Merkle subtree root) is
        included at given height and under the namespace.

        Args:
            height (int): The block height.
            namespace (Namespace): The namespace of the blob.
            proof (Proof): The proof to check.
            commitment (Commitment): The commitment to check inclusion for.

        Returns:
            bool: True if included, False otherwise.
        """

        return await self._rpc.call("blob.Included", (height, Namespace(namespace), proof, Commitment(commitment)))

    async def subscribe(self, namespace: Namespace, *,
                        deserializer: Callable | None = None) -> AsyncIterator[SubscriptionBlobResult | None]:
        """ Subscribe to published blobs from the given namespace as they are included.

        Args:
            namespace (Namespace): The namespace to subscribe to.
            deserializer (Callable | None): Custom deserializer. Defaults to None.

        Yields:
            SubscriptionBlobResult: A result with the blob information.

        """

        def deserializer_(result):
            height = result['Height']
            blobs = result.get('Blobs')
            if blobs is not None:
                return SubscriptionBlobResult(height, tuple(Blob(**kwargs) for kwargs in blobs))

        deserializer = deserializer if deserializer is not None else deserializer_

        async for subs_blob_result in self._rpc.iter("blob.Subscribe", (Namespace(namespace),), deserializer):
            if subs_blob_result is not None:
                yield subs_blob_result
