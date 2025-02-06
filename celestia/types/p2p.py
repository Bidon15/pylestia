import typing as t
from dataclasses import dataclass
from enum import Enum

type PeerID = str
type Address = list[str]


@dataclass
class ResourceManagerStat:
    system: dict[str, t.Any]
    transient: dict[str, t.Any]
    services: dict[str, t.Any]
    protocols: dict[str, t.Any]
    peers: dict[str, t.Any]

    def __init__(self, System, Transient, Services, Protocols, Peers):
        self.system = System
        self.transient = Transient
        self.services = Services
        self.protocols = Protocols
        self.peers = Peers

    @staticmethod
    def deserializer(result):
        if result is not None:
            return ResourceManagerStat(**result)


@dataclass
class BandwidthStats:
    total_in: int
    total_out: int
    rate_in: float
    rate_out: float

    def __init__(self, TotalIn, TotalOut, RateIn, RateOut):
        self.total_in = TotalIn
        self.total_out = TotalOut
        self.rate_in = RateIn
        self.rate_out = RateOut

    @staticmethod
    def deserializer(result):
        if result is not None:
            return BandwidthStats(**result)


@dataclass
class AddrInfo:
    id: PeerID
    addrs: Address

    def __init__(self, ID, Addrs):
        self.id = ID
        self.addrs = Addrs

    @staticmethod
    def deserializer(result):
        if result is not None:
            return AddrInfo(**result)


class Connectedness(Enum):
    NOT_CONNECTED = 0
    CONNECTED = 1


class Reachability(Enum):
    Unknown = 0
    Public = 1
    Private = 2
