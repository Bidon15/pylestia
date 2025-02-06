from celestia.types.p2p import PeerID, BandwidthStats, Connectedness, AddrInfo, Reachability, ResourceManagerStat

from ._RPC import Wrapper


class P2PClient(Wrapper):

    async def bandwidth_for_peer(self, peer_id: PeerID) -> BandwidthStats:
        """ Returns a Stats struct with bandwidth metrics associated with the given peer.ID.
        The metrics returned include all traffic sent / received for the peer, regardless of protocol."""
        return await self._rpc.call("p2p.BandwidthForPeer", (peer_id,), BandwidthStats.deserializer)

    async def bandwidth_for_protocol(self, protocol_id: str) -> BandwidthStats:
        """ Returns a Stats struct with bandwidth metrics associated with the given protocol.ID."""
        return await self._rpc.call("p2p.BandwidthForProtocol", (protocol_id,), BandwidthStats.deserializer)

    async def bandwidth_stats(self) -> BandwidthStats:
        """ Returns a Stats struct with bandwidth metrics for all data sent/received by
        the local peer, regardless of protocol or remote peer IDs."""
        return await self._rpc.call("p2p.BandwidthStats", (), BandwidthStats.deserializer)

    async def block_peer(self, peer_id: PeerID):
        """ Adds a peer to the set of blocked peers and closes any existing connection to that peer."""
        return await self._rpc.call("p2p.BlockPeer", (peer_id,))

    async def close_peer(self, peer_id: PeerID):
        """ Closes the connection to a given peer."""
        return await self._rpc.call("p2p.ClosePeer", (peer_id,))

    async def connect(self, address: AddrInfo):
        """ Ensures there is a connection between this host and the peer with given peer."""
        return await self._rpc.call("p2p.Connect", (address,))

    async def connectedness(self, peer_id: PeerID) -> Connectedness:
        """ Returns a state signaling connection capabilities."""
        return await self._rpc.call("p2p.Connectedness", (peer_id,))

    async def info(self) -> AddrInfo:
        """ Returns address information about the host."""
        return await self._rpc.call("p2p.Info", (), AddrInfo.deserializer)

    async def is_protected(self, peer_id: PeerID, tag: str) -> bool:
        """ Returns whether the given peer is protected."""
        return await self._rpc.call("p2p.IsProtected", (peer_id, tag))

    async def list_blocked_peers(self) -> list[PeerID]:
        """ Returns a list of blocked peers."""
        return await self._rpc.call("p2p.ListBlockedPeers")

    async def nat_status(self) -> Reachability:
        """ Returns the current NAT status."""
        return await self._rpc.call("p2p.NATStatus")

    async def peer_info(self, peer_id: PeerID) -> AddrInfo:
        """ Returns a small slice of information Peerstore has on the given peer."""
        return await self._rpc.call("p2p.PeerInfo", (peer_id,), AddrInfo.deserializer)

    async def peers(self) -> list[PeerID]:
        """ Returns connected peers."""
        return await self._rpc.call("p2p.Peers")

    async def protect(self, peer_id: PeerID, tag: str):
        """ Adds a peer to the list of peers who have a bidirectional peering agreement
        that they are protected from being trimmed, dropped or negatively scored."""
        return await self._rpc.call("p2p.Protect", (peer_id, tag))

    async def pub_sub_peers(self, topic: str) -> list[PeerID]:
        """ Returns the peer IDs of the peers joined on the given topic."""
        return await self._rpc.call("p2p.PubSubPeers", (topic,))

    async def pub_sub_topics(self) -> list[str] | None:
        """ Reports current PubSubTopics the node participates in."""
        return await self._rpc.call("p2p.PubSubTopics")

    async def resource_state(self) -> ResourceManagerStat:
        """ Returns the state of the resource manager."""
        return await self._rpc.call("p2p.ResourceState", (), ResourceManagerStat.deserializer)

    async def unblock_peer(self, peer_id: PeerID):
        """ Removes a peer from the set of blocked peers."""
        return await self._rpc.call("p2p.UnblockPeer", (peer_id,))

    async def unprotect(self, peer_id: PeerID, tag: str) -> bool:
        """ Removes a peer from the list of peers who have a bidirectional peering agreement
        that they are protected from being trimmed, dropped or negatively scored, returning
        a bool representing whether the given peer is protected or not."""
        return await self._rpc.call("p2p.Unprotect", (peer_id, tag))
