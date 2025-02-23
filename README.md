# pyCelestia

This module provides a Python interface for interacting with the Celestia Node API. All methods communicate with the API via JSON-RPC, offering a flexible and developer-friendly solution for integrating Celestia functionality into applications.

It is designed for developers who want to interact with the Celestia network without dealing with the complexities of low-level RPC request handling.
## 🚀 Installation

```sh
pip install pycelestia  
```

## 🔧 Usage

### Connecting to Celestia Node
Below is an example of how to connect to a real Celestia node using its RPC endpoint.

```python

from pycelestia import Client

# Configuration for connecting to a Celestia node
node_url = "https://celestia-rpc.example.com"  # Replace with the actual RPC node URL
auth_token = "your-auth-token"  # Replace with your authentication token (if required)

# Initialize the client
client = Client(base_url=node_url)

# Example usage of the API
async with client.connect(auth_token) as api:
    balance = await api.state.balance()
```
### Custom Deserialization Example

```python
from pydantic import BaseModel

class CustomBalanceModel(BaseModel):
    amount: int
    denom: str

async with client.connect(auth_token) as api:
    # The `deserializer` parameter allows you to transform raw API data into a desired format
    last_height = await api.header.local_head(deserializer=lambda data: int(data['header']['height']))
    isinstance(last_height, int) # True
    # Use the Pydantic model to validate and transform the balance response
    balance = await api.state.balance(deserializer=CustomBalanceModel.model_validate)
    isinstance(balance.amount, int) # True
```
