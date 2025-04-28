# pylestia Examples

This directory contains examples showing how to use pylestia to interact with the Celestia network.

## Prerequisites

Before running these examples, make sure you:

1. Have a running Celestia node (light node or bridge node)
2. Have an authentication token from your node
3. Have a funded wallet associated with your node
4. Have Python 3.10 or higher installed

## Getting Started

The simplest way to get started is to run the `hello_world.py` example:

```bash
# Set your auth token as an environment variable
export AUTH_TOKEN="your_auth_token_here"

# Run the hello world example
python hello_world.py
```

Or specify parameters directly:

```bash
# Basic usage
python hello_world.py --rpc ws://localhost:26658 --auth your_auth_token --message "Custom message"

# With signer information (Share Version 1)
python hello_world.py --rpc ws://localhost:26658 --auth your_auth_token --with-signer
```

## Examples

### Hello World (`hello_world.py`)

Submits a "Hello, World!" blob to the Celestia network and verifies it was successfully stored.

Features demonstrated:

- Connecting to a Celestia node
- Creating a random namespace
- Submitting a blob with or without signer information
- Retrieving the blob to verify submission
- Displaying the blob's share version and signer (if applicable)

**Command-line options:**

- `--rpc`: The Celestia node RPC endpoint (default: ws://localhost:26658)
- `--auth`: Authentication token for the node
- `--message`: Custom message to submit (default: "Hello, World!")
- `--with-signer`: Include signer information (Share Version 1)

### Additional Examples

Coming soon:

- Subscribing to blob updates
- Working with Data Availability Sampling (DAS)
- Interacting with headers and state
- Advanced blob operations with signers

## Troubleshooting

If you encounter issues running the examples:

1. Make sure your Celestia node is running and accessible
2. Verify your authentication token is correct
3. Check that your wallet has sufficient funds for submitting transactions
4. Ensure you're using the correct RPC endpoint

For more detailed documentation, see the [Quick Start Guide](../docs/QUICKSTART.md).
