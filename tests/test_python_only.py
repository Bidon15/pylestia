"""
Test the v0.11.0 features with pure Python (no Rust extension).
"""
import sys
import pytest

# Mock the pylestia.pylestia_core.types module
sys.modules['pylestia.pylestia_core'] = type('MockPylestiaModule', (), {})
sys.modules['pylestia.pylestia_core.types'] = type('MockPylestiaTypes', (), {
    'normalize_namespace': lambda x: x,
    'normalize_blob': lambda *args: {
        'namespace': args[0],
        'data': args[1],
        'commitment': b'mockedcommitment',
        'share_version': 1 if len(args) > 2 and args[2] else 0,
        'index': None,
        'signer': args[2] if len(args) > 2 and args[2] else None
    }
})

# Now import the actual code that uses pylestia.pylestia_core
from pylestia.types import Blob, Base64, Namespace
from pylestia.types.errors import ErrorCode, parse_error_message


def test_blob_with_signer():
    """Test blob creation with signer information."""
    namespace = Namespace(b'test')
    data = Base64(b'test_data')
    signer = Base64(b'celestia1jv65s3grqf6v6jl3dp4t6c9t9rk99cd8jaydtw')
    
    blob = Blob(namespace, data, signer=signer)
    
    # Check that the signer was correctly set
    assert blob.signer is not None
    assert blob.signer == signer
    
    # Verify Share Version is 1 for blobs with signers
    assert blob.share_version == 1


def test_blob_without_signer():
    """Test blob creation without signer information."""
    namespace = Namespace(b'test')
    data = Base64(b'test_data')
    
    blob = Blob(namespace, data)
    
    # Check that the signer is None
    assert blob.signer is None
    
    # No signer means Share Version 0
    assert blob.share_version == 0
    
    
def test_explicit_share_version():
    """Test explicit share version setting."""
    namespace = Namespace(b'test')
    data = Base64(b'test_data')
    
    # Override the automatic share version selection
    blob = Blob(namespace, data, share_version=1)
    assert blob.share_version == 1
    
    # With signer but explicit share version
    signer = Base64(b'celestia1jv65s3grqf6v6jl3dp4t6c9t9rk99cd8jaydtw')
    blob = Blob(namespace, data, signer=signer, share_version=1)
    assert blob.share_version == 1
    assert blob.signer == signer


def test_error_codes():
    """Test the error codes enum."""
    assert ErrorCode.ReservedNamespace != ErrorCode.InvalidBlobSigner
    assert ErrorCode.UnsupportedShareVersion != ErrorCode.ZeroBlobSize
    
    # Test error code matching
    # Test with valid error message
    result = parse_error_message("error: reserved namespace not allowed")
    assert result is not None
    assert result[0] == ErrorCode.ReservedNamespace
    
    # Test with invalid error message
    result = parse_error_message("some random error")
    assert result is None