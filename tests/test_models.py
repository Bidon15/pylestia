"""
Tests for the core data types in the Celestia client.

These tests verify the basic functionality of Namespace, Blob, and other
core data types without requiring a running Celestia node.
"""

import pytest
import pytest_asyncio
from pylestia.pylestia_core import types  # noqa

from pylestia.types import Namespace


@pytest.mark.asyncio
async def test_namespace():
    namespace = Namespace(b'Alesh')
    assert namespace == b'\x00' * 24 + b'Alesh'
    assert str(namespace) == 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQWxlc2g='
    assert namespace == Namespace('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQWxlc2g=')
    with pytest.raises(ValueError):
        Namespace(b'111111111111111111111111111111111')
    with pytest.raises(ValueError):
        Namespace(b'1111111111111111111111111111111111111111111111111111111111')


@pytest.mark.asyncio
async def test_blob():
    blob = types.normalize_blob(b'Alesh', b'0123456789ABCDEF')
    # Verify all blob properties thoroughly
    assert blob['namespace'] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Alesh'
    assert blob['data'] == b'0123456789ABCDEF'
    assert blob['index'] is None
    assert blob['share_version'] == 0
    # In v0.11.0, commitment is still bytes but extracted differently
    # Verify the commitment hash matches the expected value
    assert isinstance(blob['commitment'], bytes)
    assert blob['commitment'] == b'\x88e\rh\xc1\x02\xbd\xfc\xbcc\xa3\xcc\x10\n5\xdf\xcbCh\xa3m\x04\xe1\xeds(\xdf}j>\xab/'
