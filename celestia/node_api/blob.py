import typing as t
from dataclasses import dataclass

from celestia._celestia import types  # noqa

from ._RPC import Wrapper, Base64


class Namespace(Base64):
    """ Celestia namespace. """

    def __new__(cls, value: str | bytes):
        value = super().__new__(cls, value)
        value = types.normalize_namespace(value)
        return super().__new__(cls, value)


@dataclass
class Blob:
    namespace: Namespace
    data: Base64
    commitment: Base64
    share_version: int
    index: int | None = None

    def __init__(self, namespace: Namespace | str | bytes, data: Base64 | str | bytes,
                 commitment: Base64 | str | bytes | None = None, share_version: int | None = 0,
                 index: int | None = None):
        self.namespace = namespace if isinstance(namespace, Namespace) else Namespace(namespace)
        self.data = data if isinstance(data, Base64) else Base64(data)
        if commitment is not None:
            self.commitment = commitment if isinstance(commitment, Base64) else Base64(commitment)
            self.share_version = share_version or 0
        else:
            kwargs = types.normalize_blob(self.namespace, self.data)
            self.commitment = Base64(kwargs['commitment'])
            self.share_version = kwargs['share_version']
        self.index = index


class TxConfig(t.TypedDict):
    signer_address: str | None
    key_name: str | None
    gas_price: float | None
    gas: int | None
    fee_granter_address: str | None


@dataclass
class SubmitBlobResult:
    height: int
    commitments: tuple[Base64, ...]


class BlobClient(Wrapper):

    async def get_all(self, height: int, namespace: bytes, *namespaces: bytes) -> list[Blob] | None:
        """ GetAll returns all blobs under the given namespaces at the given height.
        If all blobs were found without any errors, the user will receive a list of blobs.
        If the BlobService couldn't find any blobs under the requested namespaces,
        the user will receive an empty list of blobs.
        """

        def deserializer(result):
            if result is not None:
                return [Blob(**kwargs) for kwargs in result]

        namespaces = tuple(Namespace(namespace) for namespace in (namespace, *namespaces))
        return await self._rpc.call("blob.GetAll", (height, namespaces), deserializer)

    async def submit(self, blob: Blob, *blobs: Blob, **options: t.Unpack[TxConfig]) -> int:
        """ Sends Blobs and reports the height in which they were included.
        Allows sending multiple Blobs atomically synchronously.
        Uses default wallet registered on the Node.
        """
        blobs = tuple(types.normalize_blob(blob) if blob.commitment is None else blob
                      for blob in (blob, *blobs))

        def deserializer(height):
            if height is not None:
                return SubmitBlobResult(height, tuple(blob.commitment for blob in blobs))

        return await self._rpc.call("blob.Submit", (blobs, options), deserializer)
