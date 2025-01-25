import typing as t
from base64 import b64decode, b64encode
from dataclasses import dataclass
from celestia._celestia import types as ext  # noqa


class Base64(bytes):
    """ Byte string. """

    def __new__(cls, value: str | bytes):
        if isinstance(value, str):
            value = b64decode(value)
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return b64encode(self).decode('ascii')


class Namespace(Base64):
    """ Celestia namespace. """

    def __new__(cls, value: str | bytes):
        value = super().__new__(cls, value)
        value = ext.normalize_namespace(value)
        return super().__new__(cls, value)


class Commitment(Base64):
    """Celestia commitment"""


@dataclass
class Blob:
    namespace: Namespace
    data: Base64
    commitment: Commitment
    share_version: int
    index: int | None = None

    def __init__(self, namespace: Namespace | str | bytes, data: Base64 | str | bytes,
                 commitment: Commitment | str | bytes | None = None, share_version: int | None = 0,
                 index: int | None = None):
        self.namespace = namespace if isinstance(namespace, Namespace) else Namespace(namespace)
        self.data = data if isinstance(data, Base64) else Base64(data)
        if commitment is not None:
            self.commitment = commitment if isinstance(commitment, Commitment) else Commitment(commitment)
            self.share_version = share_version or 0
        else:
            kwargs = ext.normalize_blob(self.namespace, self.data)
            self.commitment = Commitment(kwargs['commitment'])
            self.share_version = kwargs['share_version']
        self.index = index

    @staticmethod
    def deserializer(result):
        if result is not None:
            return Blob(**result)


class TxConfig(t.TypedDict):
    signer_address: str | None
    key_name: str | None
    gas_price: float | None
    gas: int | None
    fee_granter_address: str | None


@dataclass
class SubmitBlobResult:
    height: int
    commitments: tuple[Commitment, ...]


type CommitmentProof = dict[str, t.Any]
type Proof = dict[str, t.Any]
