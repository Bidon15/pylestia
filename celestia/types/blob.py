from dataclasses import dataclass

from celestia._celestia import types as ext  # noqa

from celestia.common_types import Blob, Base64, Namespace, Commitment


@dataclass
class SubmitBlobResult:
    height: int
    commitments: tuple[Commitment, ...]


@dataclass
class SubscriptionBlobResult:
    height: int
    blobs: tuple[Blob, ...]


@dataclass
class Proof:
    end: int
    nodes: tuple[Base64, ...]
    start: int | None
    is_max_namespace_ignored: bool | None

    def __init__(self, nodes, end, is_max_namespace_ignored=None, start=None):
        self.start = start
        self.nodes = tuple(node for node in nodes)
        self.end = end
        self.is_max_namespace_ignored = is_max_namespace_ignored

    @staticmethod
    def deserializer(result):
        if result is not None:
            return [Proof(**kwargs) for kwargs in result]


@dataclass
class RowProofEntry:
    index: int
    total: int
    leaf_hash: Base64
    aunts: tuple[Base64, ...]

    def __init__(self, leaf_hash, aunts, total, index):
        self.leaf_hash = leaf_hash
        self.aunts = tuple(aunt for aunt in aunts)
        self.total = total
        self.index = index


@dataclass
class RowProof:
    start_row: int
    end_row: int
    row_roots: tuple[Base64, ...]
    proofs: tuple[RowProofEntry, ...]

    def __init__(self, row_roots, proofs, end_row, start_row):
        self.row_roots = tuple(row_root for row_root in row_roots)
        self.proofs = tuple(RowProofEntry(**proof) for proof in proofs)
        self.end_row = end_row
        self.start_row = start_row


@dataclass
class CommitmentProof:
    namespace_id: Namespace
    namespace_version: int
    row_proof: RowProof
    subtree_root_proofs: tuple[Proof, ...]
    subtree_roots: tuple[Base64, ...]

    def __init__(self, namespace_id, namespace_version, row_proof, subtree_root_proofs, subtree_roots):
        self.namespace_id = Namespace.ensure_type(namespace_id)
        self.namespace_version = int(namespace_version)
        self.row_proof = RowProof(**row_proof)
        self.subtree_root_proofs = tuple(Proof(**subtree_root_proof) for subtree_root_proof in subtree_root_proofs)
        self.subtree_roots = tuple(subtree_root for subtree_root in subtree_roots)

    @staticmethod
    def deserializer(result):
        if result is not None:
            return CommitmentProof(**result)
