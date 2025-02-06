import typing as t
from dataclasses import dataclass
from datetime import datetime

from celestia._celestia import types as ext  # noqa

type Address = str

type HashedData = str


@dataclass
class Balance:
    amount: int
    denom: str

    def __init__(self, amount: int, denom: str):
        self.amount = int(amount)
        self.denom = denom

    @staticmethod
    def deserializer(result):
        if result is not None:
            return Balance(**result)


@dataclass
class TXResponse:
    height: int
    txhash: HashedData
    logs: tuple[t.Any] | None = None
    events: tuple[t.Any, ...] | None = None

    def __init__(self, height, txhash, logs, events):
        self.height = int(height)
        self.txhash = txhash
        self.logs = tuple(log for log in logs) if logs else None
        self.events = tuple(event for event in events) if events else None

    @staticmethod
    def deserializer(result):
        if result is not None:
            return TXResponse(**result)


@dataclass
class Delegation:
    delegator_address: Address
    validator_address: Address
    shares: float

    def __init__(self, delegator_address, validator_address, shares):
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.shares = float(shares)


@dataclass
class DelegationResponse:
    delegation: Delegation
    balance: Balance

    def __init__(self, delegation, balance):
        self.delegation = Delegation(**delegation)
        self.balance = Balance(**balance)


@dataclass
class QueryDelegationResponse:
    delegation_response: DelegationResponse

    def __init__(self, delegation_response):
        self.delegation_response = DelegationResponse(**delegation_response)

    @staticmethod
    def deserializer(result):
        if result is not None:
            return QueryDelegationResponse(**result)


@dataclass
class RedelegationEntry:
    creation_height: int
    completion_time: datetime
    initial_balance: int
    shares_dst: float

    def __init__(self, creation_height, completion_time, initial_balance, shares_dst):
        self.creation_height = creation_height
        self.completion_time = datetime.fromisoformat(completion_time)
        self.initial_balance = int(initial_balance)
        self.shares_dst = float(shares_dst)


@dataclass
class Redelegation:
    delegator_address: Address
    validator_src_address: Address
    validator_dst_address: Address
    entries: tuple[RedelegationEntry, ...]

    def __init__(self, delegator_address, validator_src_address, validator_dst_address, entries):
        self.delegator_address = delegator_address
        self.validator_src_address = validator_src_address
        self.validator_dst_address = validator_dst_address
        self.entries = tuple(RedelegationEntry(**entry) for entry in entries)


@dataclass
class RedelegationResponseEntry:
    redelegation_entry: RedelegationEntry
    balance: int

    def __init__(self, redelegation_entry, balance):
        self.redelegation_entry = RedelegationEntry(**redelegation_entry)
        self.balance = int(balance)


@dataclass
class RedelegationResponse:
    redelegation: Redelegation
    entries: tuple[RedelegationResponseEntry, ...]

    def __init__(self, redelegation, entries):
        self.redelegation = Redelegation(**redelegation)
        self.entries = tuple(RedelegationResponseEntry(**entry) for entry in entries)


@dataclass
class Pagination:
    next_key: HashedData = None
    total: int = None


@dataclass
class QueryRedelegationResponse:
    redelegation_responses: tuple[RedelegationResponse, ...]
    pagination: Pagination

    def __init__(self, redelegation_responses, pagination=None):
        self.redelegation_responses = tuple(
            RedelegationResponse(**redelegation_response) for redelegation_response in redelegation_responses)
        self.pagination = Pagination(**pagination) if pagination else None

    @staticmethod
    def deserializer(result):
        if result is not None:
            return QueryRedelegationResponse(**result)


@dataclass
class UnbondEntry:
    creation_height: int
    completion_time: datetime
    initial_balance: int
    balance: int

    def __init__(self, creation_height, completion_time, initial_balance, balance):
        self.creation_height = creation_height
        self.completion_time = datetime.fromisoformat(completion_time)
        self.initial_balance = int(initial_balance)
        self.balance = int(balance)


@dataclass
class Unbond:
    delegator_address: Address
    validator_address: Address
    entries: tuple[UnbondEntry, ...]

    def __init__(self, delegator_address, validator_address, entries):
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.entries = tuple(UnbondEntry(**entry) for entry in entries)


@dataclass
class QueryUnbondingDelegationResponse:
    unbond: Unbond

    def __init__(self, unbond):
        self.unbond = Unbond(**unbond)

    @staticmethod
    def deserializer(result):
        if result is not None:
            return QueryUnbondingDelegationResponse(**result)
