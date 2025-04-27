# Upgrading to celestia-types v0.11.0

This guide explains the key changes when upgrading to pyCelestia with celestia-types v0.11.0 support.

## Breaking Changes in v0.11.0

The v0.11.0 release includes several breaking changes to ensure optimal support for the latest Celestia features.

### 1. Blob Signer Support (Share Version 1)

The biggest change in v0.11.0 is first-class support for blob signers, which identify the account that submitted a blob. This is implemented as Share Version 1.

**Important Note**: When using Share Version 1, the signer must be a 20-byte value that matches the account submitting the transaction. This is a security feature that ensures accountability.

#### Before (v0.9.0):
```python
# Before - only unsigned blobs (Share Version 0)
blob = Blob(namespace, data)
```

#### After (v0.11.0):
```python
# Unsigned blob (Share Version 0)
blob = Blob(namespace, data)

# Signed blob (Share Version 1) - includes signer information
# IMPORTANT: The signer must be a 20-byte value that matches the account submitting the transaction
from bech32 import bech32_decode, convertbits

# Properly decode the Celestia account address to get the 20-byte signer value
account_address = "celestia1vxh4zk38zz76r468le68uyzrzn2f7wn5632ma2"  # Example address
hrp, data = bech32_decode(account_address)
decoded_bytes = convertbits(data, 5, 8, False)
signer_bytes = bytes(decoded_bytes)

# Create the signer from the bytes
signer = Base64(signer_bytes)
blob = Blob(namespace, data, signer=signer)  # Automatically sets share_version=1
```

### 2. Commitment Format Changes

The internal representation of commitments has changed in v0.11.0.

#### Before (v0.9.0):
```python
# Commitments were always raw bytes
assert isinstance(blob.commitment, bytes)
```

#### After (v0.11.0):
```python
# Commitments are still represented as bytes externally
# But internally use a different structure
assert isinstance(blob.commitment, bytes)
```

### 3. Moved TxConfig

The `TxConfig` class was moved from `common_types.py` to `celestia.node_api.rpc.executor`.

#### Before (v0.9.0):
```python
from celestia.types.common_types import TxConfig
```

#### After (v0.11.0):
```python
from celestia.node_api.rpc import TxConfig
```

### 4. Public ShareProof Fields

The ShareProof fields are now public (they were previously private).

### 5. Error Handling Enhancements

New error codes for blob submission were introduced in v0.10.0 and expanded in v0.11.0. Use the new `ErrorCode` enum and `parse_error_message` function for improved error handling.

```python
from celestia.types.errors import ErrorCode, parse_error_message

try:
    result = await api.blob.submit(blob)
except Exception as e:
    error_code = parse_error_message(str(e))
    if error_code == ErrorCode.ReservedNamespace:
        print("Cannot use reserved namespace")
    elif error_code == ErrorCode.BlobsTooLarge:
        print("Blob size exceeds maximum")
    # etc.
```

## Migration Steps

1. Update import paths for `TxConfig`:
   ```python
   # Old
   from celestia.types.common_types import TxConfig
   
   # New
   from celestia.node_api.rpc import TxConfig
   ```

2. Add signer information when creating blobs where accountability is needed:
   ```python
   # Get account address
   account_address = await api.state.account_address()
   
   # Create signed blob
   signer = Base64(account_address.encode())
   blob = Blob(namespace, data, signer=signer)
   ```

3. Update error handling to use the new error codes:
   ```python
   from celestia.types.errors import ErrorCode, parse_error_message
   
   try:
       result = await api.blob.submit(blob)
   except Exception as e:
       error_code = parse_error_message(str(e))
       if error_code:
           # Handle specific error
           print(f"Error code: {error_code}")
       else:
           # General error
           raise
   ```

## Understanding Share Versions

- **Share Version 0**: Traditional unsigned blobs with no signer information
- **Share Version 1**: Blobs that include signer information for accountability

To check a blob's share version:

```python
print(f"Share Version: {blob.share_version}")
# 0 = Unsigned
# 1 = Signed
```

## Example Usage

```python
# Create a namespace
namespace = Namespace(b"my_namespace")

# Create an unsigned blob (Share Version 0)
unsigned_blob = Blob(namespace, b"My unsigned data")
assert unsigned_blob.share_version == 0
assert unsigned_blob.signer is None

# Get the account address
account_address = await api.state.account_address()

# Create a signed blob (Share Version 1)
signer = Base64(account_address.encode())
signed_blob = Blob(namespace, b"My signed data", signer=signer)
assert signed_blob.share_version == 1
assert signed_blob.signer is not None

# Submit blobs
unsigned_result = await api.blob.submit(unsigned_blob)
signed_result = await api.blob.submit(signed_blob)

# Retrieve blobs
unsigned_blobs = await api.blob.get_all(unsigned_result.height, namespace)
signed_blobs = await api.blob.get_all(signed_result.height, namespace)

# Check signer information
for blob in signed_blobs:
    if blob.signer:
        print(f"Blob was submitted by: {blob.signer.decode()}")
```

For a complete example of both signed and unsigned blobs, see the `hello_world.py` example in the examples directory.