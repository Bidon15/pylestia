import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Dict, Optional, TypeVar, Union, cast
from urllib.parse import urlparse

from websockets import connect
# In websockets 12.0, the connection types have changed
# Use Protocol instead of ClientConnection/Connection
from websockets.protocol import Protocol as ClientConnection

from .abc import Transport, RPCExecutor
from .executor import RPC, TxConfig

__all__ = ["JsonRpcClient", "TxConfig"]

T = TypeVar('T')

class JsonRpcClient(RPCExecutor):
    """Client for communicating with a Celestia node via JSON-RPC over WebSockets."""
    
    def __init__(self, base_url: str) -> None:
        """Initialize a new JSON-RPC client.
        
        Args:
            base_url: The base URL of the Celestia node, e.g., 'http://localhost:26658'
        """
        self.base_url = self._prepare_url(base_url)
        self.connection = None
        self.rpc = None
    
    def _prepare_url(self, url: str) -> str:
        """Process the URL to ensure it has the correct protocol."""
        if not url.startswith(('ws://', 'wss://')):
            # If no protocol specified, use ws://
            url = f"ws://{url}"
        
        # Parse the URL to validate and normalize it
        parsed = urlparse(url)
        if parsed.scheme not in ("ws", "wss"):
            raise ValueError("Unsupported URL scheme, must be ws or wss")
        
        # Ensure port is specified
        port = parsed.port or 26658
        return f'{parsed.scheme}://{parsed.hostname}:{port}'
    
    async def connect(self, auth_token: Optional[str] = None) -> None:
        """Connect to the Celestia node.
        
        Args:
            auth_token: Optional authentication token for the node
        """
        headers = []
        if auth_token:
            headers.append(('Authorization', f'Bearer {auth_token}'))
        
        # Create the connection
        connection = await connect(self.base_url, additional_headers=headers)
        
        # Set up the transport
        class WebSocketTransport(Transport):
            def __init__(self, connection):
                self.connection = connection
            
            async def send(self, message: str) -> None:
                await self.connection.send(message)
        
        transport = WebSocketTransport(connection)
        self.rpc = RPC(transport)
        self.connection = connection
        
        # Start the message listener
        asyncio.create_task(self._listen(connection, transport))
    
    async def _listen(self, connection: ClientConnection, transport: Transport) -> None:
        """Listen for messages from the connection.
        
        Args:
            connection: The WebSocket connection
            transport: The transport to handle messages
        """
        try:
            async for message in connection:
                transport.on_message(message)
        except asyncio.CancelledError:
            transport.on_close(None)
        except Exception as exc:
            transport.on_close(exc)
    
    async def disconnect(self) -> None:
        """Disconnect from the Celestia node."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.rpc = None
    
    async def call(self, method: str, params: tuple = None, 
                  deserializer: Optional[Callable[[Any], T]] = None) -> Optional[T]:
        """Call an RPC method.
        
        Args:
            method: The method name
            params: The parameters to pass to the method
            deserializer: Optional function to deserialize the result
            
        Returns:
            The result of the method call, optionally deserialized
        """
        if not self.rpc:
            raise RuntimeError("Not connected to the node. Call connect() first.")
        
        # Use the RPC implementation from executor.py
        return await self.rpc.call(method, params, deserializer)
    
    async def subscribe(self, method: str, params: tuple = None,
                       deserializer: Optional[Callable[[Any], T]] = None) -> AsyncGenerator[Optional[T], None]:
        """Subscribe to an RPC method.
        
        Args:
            method: The method name
            params: The parameters to pass to the method
            deserializer: Optional function to deserialize the results
            
        Yields:
            The subscription results, optionally deserialized
        """
        if not self.rpc:
            raise RuntimeError("Not connected to the node. Call connect() first.")
        
        # Use the RPC implementation from executor.py
        async for result in self.rpc.subscribe(method, params, deserializer):
            yield result
