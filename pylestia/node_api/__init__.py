"""
pylestia Node API Module

This module provides the interfaces for interacting with a Celestia node.
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast, overload

from pylestia.node_api.blob import BlobAPI
from pylestia.node_api.das import DasClient
from pylestia.node_api.fraud import FraudClient
from pylestia.node_api.header import HeaderClient
from pylestia.node_api.p2p import P2PClient
from pylestia.node_api.rpc import JsonRpcClient
from pylestia.node_api.share import ShareClient
from pylestia.node_api.state import StateClient

__all__ = ["Client"]


class Client:
    """
    Main client for interacting with a Celestia node.
    
    This class maintains the connection to the node and provides access
    to all the API endpoints.
    """
    
    def __init__(self, base_url: str) -> None:
        """
        Initialize a new client.
        
        Args:
            base_url: The base URL of the Celestia node, e.g., 'http://localhost:26658'
        """
        self.base_url = base_url
        self._client = JsonRpcClient(base_url)
        
    def connect(self, auth_token: Optional[str] = None):
        """
        Connect to the Celestia node.
        
        Args:
            auth_token: Optional authentication token for the node
            
        Returns:
            A context manager that provides access to the API endpoints
        """
        return NodeAPIContext(self._client, auth_token)
        

class NodeAPIContext:
    """Context manager for the node API connection."""
    
    def __init__(self, client: JsonRpcClient, auth_token: Optional[str] = None) -> None:
        self.client = client
        self.auth_token = auth_token
    
    async def __aenter__(self):
        """
        Enter the context, connecting to the node.
        
        Returns:
            An object with properties for each API endpoint
        """
        await self.client.connect(self.auth_token)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context, closing the connection.
        """
        await self.client.disconnect()
    
    @property
    def blob(self) -> BlobAPI:
        """Access the Blob API for working with data blobs."""
        return BlobAPI(self.client)
    
    @property
    def das(self) -> DasClient:
        """Access the DAS (Data Availability Sampling) API."""
        return DasClient(self.client)
    
    @property
    def fraud(self) -> FraudClient:
        """Access the Fraud API for reporting and verifying fraud proofs."""
        return FraudClient(self.client)
    
    @property
    def header(self) -> HeaderClient:
        """Access the Header API for working with block headers."""
        return HeaderClient(self.client)
    
    @property
    def p2p(self) -> P2PClient:
        """Access the P2P API for peer-to-peer network operations."""
        return P2PClient(self.client)
    
    @property
    def share(self) -> ShareClient:
        """Access the Share API for working with data shares."""
        return ShareClient(self.client)
    
    @property
    def state(self) -> StateClient:
        """Access the State API for state-related operations."""
        return StateClient(self.client)
