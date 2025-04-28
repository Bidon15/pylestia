import logging
import typing as t
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

logger = logging.Logger('WS JSON-RPC')

class Transport(ABC):
    on_message: t.Callable[[bytes | str], None]
    on_close: t.Callable[[Exception | None], None]

    @abstractmethod
    async def send(self, message: str) -> None:
        """ Send a message to the connection. """


class RPCExecutor(ABC):

    @abstractmethod
    async def call(self, method: str, params: tuple[t.Any, ...] = None,
                   deserializer: t.Callable[[t.Any], t.Any] = None) -> t.Any | None:
        """ This method must implement calling an RPC method and returning the result.
        """

    @abstractmethod
    async def subscribe(self, method: str, params: tuple[t.Any, ...] = None,
                   deserializer: t.Callable[[t.Any], t.Any] = None) -> AsyncGenerator[t.Any, None]:
        """ This method must implement creating an `RPC` subscription and returning
        an asynchronous iterator that returns the incoming subscription results.
        """


class Wrapper:
    def __init__(self, rpc: RPCExecutor):
        self._rpc = rpc
