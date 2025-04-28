"""
Error handling for Celestia operations.

This module provides error codes and parsing utilities for handling 
errors that occur during Celestia operations, particularly blob submissions.
These error codes align with celestia-types v0.11.0+.
"""

from enum import Enum, auto
from typing import Optional, Tuple, Union


class ErrorCode(Enum):
    """ Error codes for the Celestia blob submission system.

    These error codes were added in celestia-types v0.10.0 and expanded in v0.11.0.
    """
    # Namespace-related errors
    ReservedNamespace = auto()
    InvalidNamespaceLen = auto()
    
    # Size-related errors
    InvalidDataSize = auto()
    BlobSizeMismatch = auto()
    ZeroBlobSize = auto()
    
    # Version-related errors
    UnsupportedShareVersion = auto()
    
    # Operation-related errors
    NoBlobs = auto()
    InvalidBlobSigner = auto()
    
    # Transaction-related errors
    InvalidNamespaceType = auto()
    NotEnoughFunds = auto()
    TxCreateError = auto()
    TxEncodeError = auto()
    
    # Internal errors
    InvalidRequest = auto()
    InternalError = auto()


def parse_error_message(error_message: str) -> Optional[Tuple[ErrorCode, str]]:
    """ Parse an error message to extract the error code and description.
    
    This function attempts to match the error message against known error patterns 
    and returns the appropriate error code with the original message. This is useful
    for handling errors from the Celestia node in a more structured way.
    
    Args:
        error_message: The error message to parse, typically from an exception
        
    Returns:
        A tuple of (ErrorCode, description) or None if no known error pattern is found
        
    Example:
        >>> try:
        ...     # Some operation that might fail
        ...     await api.blob.submit(blob)
        ... except Exception as e:
        ...     error_info = parse_error_message(str(e))
        ...     if error_info and error_info[0] == ErrorCode.NotEnoughFunds:
        ...         print("You need to add more funds to your account")
    """
    error_codes = {
        "reserved namespace": ErrorCode.ReservedNamespace,
        "invalid namespace length": ErrorCode.InvalidNamespaceLen,
        "invalid data size": ErrorCode.InvalidDataSize, 
        "blob size mismatch": ErrorCode.BlobSizeMismatch,
        "unsupported share version": ErrorCode.UnsupportedShareVersion,
        "zero blob size": ErrorCode.ZeroBlobSize,
        "no blobs": ErrorCode.NoBlobs,
        "invalid blob signer": ErrorCode.InvalidBlobSigner,
        "invalid namespace type": ErrorCode.InvalidNamespaceType,
        "not enough funds": ErrorCode.NotEnoughFunds,
        "tx create error": ErrorCode.TxCreateError,
        "tx encode error": ErrorCode.TxEncodeError,
        "invalid request": ErrorCode.InvalidRequest,
        "internal error": ErrorCode.InternalError,
    }
    
    for pattern, code in error_codes.items():
        if pattern in error_message.lower():
            return code, error_message
    
    return None