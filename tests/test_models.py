from celestia._celestia import types  # noqa

from celestia.node_api.blob import Namespace


def test_namespace():
    namespace = Namespace(b'Alesh')
    assert namespace == b'\x00' * 24 + b'Alesh'
    assert str(namespace) == 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQWxlc2g='
    assert namespace == Namespace('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQWxlc2g=')


def test_blob():
    blob = types.normalize_blob(b'Alesh', b'0123456789ABCDEF')
    assert blob == {
        'namespace': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Alesh',
        'commitment': b'\x88e\rh\xc1\x02\xbd\xfc\xbcc\xa3\xcc\x10\n5\xdf\xcbCh\xa3m\x04\xe1\xeds(\xdf}j>\xab/',
        'data': b'0123456789ABCDEF', 'index': None, 'share_version': 0
    }
