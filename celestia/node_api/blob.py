import typing as t
from collections.abc import AsyncIterator
from dataclasses import dataclass

from celestia._celestia import types  # noqa

from ._RPC import Wrapper, Base64, Commitment, Namespace


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
            kwargs = types.normalize_blob(self.namespace, self.data)
            self.commitment = Commitment(kwargs['commitment'])
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
    commitments: tuple[Commitment, ...]


type CommitmentProof = dict[str, t.Any]
type Proof = dict[str, t.Any]


class BlobClient(Wrapper):

    async def get(self, height: int, namespace: Namespace, commitment: Commitment) -> Blob | None:
        """ Retrieves the blob by commitment under the given namespace and height.
        """

        def deserializer(result):
            if result is not None:
                return Blob(**result)

        try:
            return await self._rpc.call("blob.Get", (height, Namespace(namespace), Commitment(commitment)),
                                        deserializer)
        except Exception as e:
            if 'blob: not found' in e.args[1].body['message'].lower():
                return None

    async def get_all(self, height: int, namespace: Namespace, *namespaces: Namespace) -> list[Blob] | None:
        """ Returns all blobs under the given namespaces at the given height.
        If all blobs were found without any errors, the user will receive a list of blobs.
        If the BlobService couldn't find any blobs under the requested namespaces,
        the user will receive an empty list of blobs.
        """

        def deserializer(result):
            if result is not None:
                return [Blob(**kwargs) for kwargs in result]

        namespaces = tuple(Namespace(namespace) for namespace in (namespace, *namespaces))
        return await self._rpc.call("blob.GetAll", (height, namespaces), deserializer)

    async def submit(self, blob: Blob, *blobs: Blob, **options: t.Unpack[TxConfig]) -> SubmitBlobResult:
        """ Sends Blobs and reports the height in which they were included.
        Allows sending multiple Blobs atomically synchronously.
        Uses default wallet registered on the Node.
        """

        def deserializer(height):
            if height is not None:
                return SubmitBlobResult(height, tuple(blob.commitment for blob in blobs))

        blobs = tuple(types.normalize_blob(blob) if blob.commitment is None else blob for blob in (blob, *blobs))
        return await self._rpc.call("blob.Submit", (blobs, options), deserializer)

    async def get_commitment_proof(self, height: int, namespace: Namespace,
                                   commitment: Base64) -> CommitmentProof | None:
        """ Generates a commitment proof for a share commitment.
        """
        try:
            return await self._rpc.call("blob.GetCommitmentProof", (height, Namespace(namespace), Base64(commitment)))
        except Exception as e:
            if 'blob: not found' in e.args[1].body['message'].lower():
                return None

    async def get_proof(self, height: int, namespace: Namespace, commitment: Commitment) -> Proof | None:
        """ Retrieves proofs in the given namespaces at the given height by commitment.
        """
        try:
            return await self._rpc.call("blob.GetProof", (height, Namespace(namespace), Commitment(commitment)))
        except Exception as e:
            if 'blob: not found' in e.args[1].body['message'].lower():
                return None

    async def included(self, height: int, namespace: Namespace, proof: Proof, commitment: Commitment) -> bool:
        """ Checks whether a blob's given commitment(Merkle subtree root)
        is included at given height and under the namespace.
        """
        return await self._rpc.call("blob.Included", (height, Namespace(namespace), proof, Commitment(commitment)))

    def subscribe(self, namespace: Namespace) -> AsyncIterator[Blob]:
        """ The method subscribes to published blobs from the given namespace as they are included.
        """
        return self._rpc.iter("blob.Subscribe", (Namespace(namespace),))
