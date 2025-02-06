from dataclasses import dataclass
from datetime import datetime

from celestia._celestia import types as ext  # noqa

from celestia.common_types import Base64

type HashedData = str

type Address = str


@dataclass
class ConsensusVersion:
    block: int
    app: int


@dataclass
class Parts:
    total: int
    hash: HashedData


@dataclass
class BlockId:
    hash: HashedData
    parts: Parts

    def __init__(self, hash, parts):
        self.hash = hash
        self.parts = Parts(**parts)


@dataclass
class Header:
    version: ConsensusVersion
    chain_id: str
    height: int
    time: datetime
    last_block_id: BlockId
    last_commit_hash: HashedData
    data_hash: HashedData
    validators_hash: HashedData
    next_validators_hash: HashedData
    consensus_hash: HashedData
    app_hash: HashedData
    last_results_hash: HashedData
    evidence_hash: HashedData
    proposer_address: Address

    def __init__(self, version, chain_id, height, time, last_block_id, last_commit_hash, data_hash, validators_hash,
                 next_validators_hash, consensus_hash, app_hash, last_results_hash, evidence_hash, proposer_address):
        self.version = ConsensusVersion(block=int(version['block']), app=int(version['app']))
        self.chain_id = chain_id
        self.height = int(height)
        self.time = datetime.fromisoformat(time)
        self.last_block_id = BlockId(**last_block_id)
        self.last_commit_hash = last_commit_hash
        self.data_hash = data_hash
        self.validators_hash = validators_hash
        self.next_validators_hash = next_validators_hash
        self.consensus_hash = consensus_hash
        self.app_hash = app_hash
        self.last_results_hash = last_results_hash
        self.evidence_hash = evidence_hash
        self.proposer_address = proposer_address


@dataclass
class PubKey:
    type: str
    value: Base64


@dataclass
class Validator:
    address: Address
    pub_key: PubKey
    voting_power: str
    proposer_priority: str

    def __init__(self, address, pub_key, voting_power, proposer_priority):
        self.address = address
        self.pub_key = PubKey(**pub_key)
        self.voting_power = voting_power
        self.proposer_priority = proposer_priority


@dataclass
class ValidatorSet:
    validators: tuple[Validator, ...]
    proposer: Validator

    def __init__(self, validators, proposer):
        self.validators = tuple(Validator(**validator) for validator in validators)
        self.proposer = Validator(**proposer)


@dataclass
class Signature:
    block_id_flag: int
    validator_address: Address
    timestamp: datetime
    signature: Base64

    def __init__(self, block_id_flag, validator_address, timestamp, signature):
        self.block_id_flag = block_id_flag
        self.validator_address = validator_address
        self.timestamp = datetime.fromisoformat(timestamp)
        self.signature = signature


@dataclass
class Commit:
    height: int
    round: int
    block_id: BlockId
    signatures: tuple[Signature, ...]

    def __init__(self, height, round, block_id, signatures):
        self.height = height
        self.round = round
        self.block_id = BlockId(**block_id)
        self.signatures = tuple(Signature(**signature) for signature in signatures)


@dataclass
class Dah:
    row_roots: tuple[Base64, ...]
    column_roots: tuple[Base64, ...]

    def __init__(self, row_roots, column_roots):
        self.row_roots = tuple(row_root for row_root in row_roots)
        self.column_roots = tuple(column_root for column_root in column_roots)


@dataclass
class ExtendedHeader:
    header: Header
    validator_set: ValidatorSet
    commit: Commit
    dah: Dah

    def __init__(self, header, validator_set, dah, commit):
        self.header = Header(**header)
        self.validator_set = ValidatorSet(**validator_set)
        self.commit = Commit(**commit)
        self.dah = Dah(**dah)
        self._extended_header = {'header': header, 'validator_set': validator_set, 'dah': dah, 'commit': commit}

    @property
    def extended_header(self):
        return self._extended_header

    @staticmethod
    def deserializer(result):
        if result is not None:
            return ExtendedHeader(**result)


@dataclass
class State:
    id: int
    height: int
    from_height: int
    to_height: int
    from_hash: HashedData
    to_hash: HashedData
    start: datetime
    end: datetime

    def __init__(self, id, height, from_height, to_height, from_hash, to_hash, start, end):
        self.id = id
        self.height = height
        self.from_height = from_height
        self.to_height = to_height
        self.from_hash = from_hash
        self.to_hash = to_hash
        self.start = datetime.fromisoformat(start)
        self.end = datetime.fromisoformat(end)

    @staticmethod
    def deserializer(result):
        if result is not None:
            return State(**result)
