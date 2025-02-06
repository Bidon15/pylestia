from dataclasses import dataclass

from celestia.common_types import Base64, Namespace
from celestia.types.blob import RowProof, Proof

type Sample = Base64


@dataclass
class SampleCoords:
    row: int
    col: int


@dataclass
class ShareProof:
    namespace_id: Namespace
    namespace_version: int
    row_proof: RowProof
    data: tuple[Sample, ...]
    share_proofs: tuple[Proof, ...]

    def __init__(self, namespace_id, namespace_version, row_proof, data, share_proofs):
        self.namespace_id = Namespace.ensure_type(namespace_id)
        self.namespace_version = int(namespace_version)
        self.row_proof = RowProof(**row_proof)
        self.data = tuple(data_unit for data_unit in data)
        self.share_proofs = tuple(Proof(**share_proof) for share_proof in share_proofs)


@dataclass
class GetRangeResult:
    shares: tuple[Base64, ...]
    proof: ShareProof

    def __init__(self, Shares, Proof):
        self.shares = tuple(share for share in Shares)
        self.proof = ShareProof(**Proof)

    @staticmethod
    def deserializer(result):
        if result is not None:
            return GetRangeResult(**result)


@dataclass
class ExtendedDataSquare:
    data_square: tuple[Sample, ...]
    codec: str

    @staticmethod
    def deserializer(result):
        if result is not None:
            return ExtendedDataSquare(**result)


@dataclass
class NamespaceData:
    shares: tuple[Sample, ...]
    proof: Proof

    def __init__(self, shares, proof):
        self.shares = tuple(share for share in shares)
        self.proof = Proof(**proof)

    @staticmethod
    def deserializer(result):
        if result is not None:
            return NamespaceData(**result)
