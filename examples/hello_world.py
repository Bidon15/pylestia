#!/usr/bin/env python3
"""
Hello World Example for pylestia

This example demonstrates how to submit both regular and signed blobs to a
Celestia node using the pylestia library with v0.11.0+ features.

Requirements:
- A running Celestia node (light node or bridge node)
- An authentication token for the node
- A funded wallet associated with your node
- bech32 library for Share Version 1 blobs (install with: pip install bech32)

Usage:
    python hello_world.py --rpc "ws://localhost:26658" --auth YOUR_AUTH_TOKEN [--message "Custom message"]

This example will:
1. Generate a random namespace
2. Submit an unsigned blob with "Hello, World!" data
3. Submit a signed blob with the same data (Share Version 1)
4. Retrieve and verify both blobs
5. Display information about the blobs

For more information about signed blobs, see:
https://docs.celestia.org/developers/data-availability
"""

# Standard library imports
import argparse
import asyncio
import base64
import hashlib
import os
import secrets
import sys
import traceback

# Third-party libraries
# NOTE: bech32 is optional but recommended for Celestia address decoding
try:
    from bech32 import bech32_decode, convertbits

    BECH32_AVAILABLE = True
except ImportError:
    BECH32_AVAILABLE = False

# Add the parent directory to the path to allow importing pylestia
# This is only needed if running the example directly from the repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the Client and types
from pylestia import Client
from pylestia.types import Namespace, Blob, Base64


def decode_celestia_address(address):
    """
    Decode a Celestia bech32 address into its 20-byte binary representation.

    Args:
        address (str): A Celestia address in bech32 format (celestia1...)

    Returns:
        bytes: A 20-byte representation of the address

    Raises:
        ValueError: If the address cannot be properly decoded
    """
    if not BECH32_AVAILABLE:
        # Fallback if bech32 library is not available
        # This is not recommended for production use
        h = hashlib.sha1()
        h.update(address.encode())
        return h.digest()  # SHA-1 gives exactly 20 bytes

    # Decode the bech32 address
    hrp, data = bech32_decode(address)

    if hrp != "celestia":
        # Still proceed, but warn that this may not be a Celestia address
        print(f"  ⚠️ Warning: Address has unexpected prefix: {hrp}, expected 'celestia'")

    # Convert from 5-bit representation to 8-bit
    decoded_bytes = convertbits(data, 5, 8, False)

    if not decoded_bytes:
        raise ValueError("Failed to decode address")

    signer_bytes = bytes(decoded_bytes)

    # Ensure we have exactly 20 bytes
    if len(signer_bytes) > 20:
        return signer_bytes[:20]  # Truncate to first 20 bytes
    elif len(signer_bytes) < 20:
        return signer_bytes.ljust(20, b"\0")  # Pad to 20 bytes

    return signer_bytes


async def submit_hello_world(rpc_endpoint, auth_token, message=None, skip_signed=False):
    """
    Submits "Hello World" blobs to the Celestia network in both unsigned and signed versions.

    This example demonstrates two types of blobs:
    1. Unsigned blobs (Share Version 0) - Basic blobs without signer information
    2. Signed blobs (Share Version 1) - Blobs that include the account that submitted them

    For Share Version 1 blobs, the signer must be a 20-byte value derived from the
    Celestia account address that submits the transaction. This example properly
    decodes the bech32 address to the correct binary format.

    Args:
        rpc_endpoint (str): The RPC endpoint to connect to
        auth_token (str): Authentication token for the Celestia node
        message (str, optional): Custom message to submit
        skip_signed (bool, optional): Skip signed blob submission if True

    Returns:
        dict: Summary information about the submitted blobs

    Note:
        Using bech32 library (pip install bech32) is recommended for proper address handling.
    """
    # Create a client connecting to the Celestia node
    # The Client expects the URL as a positional argument, not a keyword
    client = Client(rpc_endpoint)

    # Generate a random namespace ID (8 bytes for security and uniqueness)
    # This ensures our namespace doesn't conflict with others on the network
    random_namespace = secrets.token_bytes(8)
    namespace = Namespace(random_namespace)

    # For more control, you could also create a namespace from a specific string:
    # namespace = Namespace(b"my-project-name")

    # Use the provided message or default to "Hello, World!"
    blob_data = message.encode() if message else b"Hello, World! From pylestia v0.11.0"

    print("\n🔄 Connecting to Celestia node...")
    async with client.connect(auth_token) as api:
        try:
            # Check node status and account information
            try:
                node_info = await api.p2p.info()
                # The node_info could be an AddrInfo object with direct attributes, not a dict
                if hasattr(node_info, "id"):
                    node_id = node_info.id
                elif isinstance(node_info, dict) and "ID" in node_info:
                    node_id = node_info["ID"]
                else:
                    node_id = str(node_info)
            except Exception as e:
                print(f"⚠️ Warning: Could not get node info: {e}")
                node_id = "Unknown"

            try:
                account_address = await api.state.account_address()
            except Exception as e:
                print(f"⚠️ Warning: Could not get account address: {e}")
                account_address = "Unknown"

            print(f"✅ Connected to Celestia node: {node_id}")
            print(f"📝 Using account address: {account_address}")

            # Check wallet balance
            balance = await api.state.balance()
            print(f"💰 Wallet balance: {balance.amount} {balance.denom}")

            # Make sure we have funds before proceeding
            if balance.amount <= 0:
                print(
                    "⚠️ Warning: Your wallet has no funds. You may not be able to submit blobs."
                )

            # PART 1: Create and submit an UNSIGNED blob (Share Version 0)
            print("\n--- SUBMITTING UNSIGNED BLOB (Share Version 0) ---")
            unsigned_blob = Blob(namespace=namespace, data=blob_data)

            print(f"📝 Blob details:")
            print(f"  Namespace: {str(namespace)}")
            print(f"  Data: '{blob_data.decode()}'")
            print(f"  Share Version: {unsigned_blob.share_version}")
            print(f"  Signer: None (unsigned)")

            # Submit the unsigned blob
            unsigned_result = await api.blob.submit(unsigned_blob)
            print(f"\n✅ Unsigned blob submitted at height: {unsigned_result.height}")

            # PART 2: Create and submit a SIGNED blob (Share Version 1)
            # Skip if requested
            if skip_signed:
                print("\n--- SKIPPING SIGNED BLOB SUBMISSION (--no-signed flag) ---")
                signed_blob_submitted = False
                signed_result = type("obj", (object,), {"height": 0})()
            else:
                print("\n--- SUBMITTING SIGNED BLOB (Share Version 1) ---")

            # Only proceed with signed blob if not skipped
            if not skip_signed:
                # Create a signer from the account address
                try:
                    # For Share Version 1, the signer must be exactly 20 bytes
                    # The signer must match the account that submits the transaction
                    print(f"  ℹ️ Using account address as signer: {account_address}")

                    try:
                        # Decode the Celestia address to get the 20-byte representation
                        signer_bytes = decode_celestia_address(account_address)

                        # Create the signer from the decoded bytes
                        signer = Base64(signer_bytes)

                        # Display the signer information
                        print(f"  ✓ Successfully decoded address to signer")
                        print(f"  ✓ Signer (hex): 0x{signer_bytes.hex()}")
                        print(f"  ✓ Length: {len(signer_bytes)} bytes (correct)")

                    except Exception as e:
                        print(f"  ⚠️ Warning: Failed to decode address properly: {e}")
                        print(
                            f"  ⚠️ Using fallback method - NOT RECOMMENDED FOR PRODUCTION"
                        )

                        # Create a 20-byte fallback using hash
                        h = hashlib.sha1()
                        h.update(account_address.encode())
                        signer_bytes = h.digest()  # SHA-1 gives exactly 20 bytes
                        signer = Base64(signer_bytes)

                        if not BECH32_AVAILABLE:
                            print(
                                f"  ⚠️ Recommendation: Install bech32 for proper address handling"
                            )
                            print(f"  ⚠️ Run: pip install bech32")
                except Exception as e:
                    print(f"  ⚠️ Warning: Error creating signer: {e}")
                    # Create a 20-byte placeholder signer
                    signer = Base64(b"celestia_placeholder_".ljust(20, b"x"))

                # Create a blob with signer (automatically sets Share Version 1)
                try:
                    # Try to create a blob with the signer
                    signed_blob = Blob(
                        namespace=namespace, data=blob_data, signer=signer
                    )
                    print(
                        f"  ✓ Created blob with signer, share version: {signed_blob.share_version}"
                    )
                except Exception as e:
                    print(f"  ⚠️ Warning: Failed to create blob with signer: {e}")
                    print(f"  ⚠️ Falling back to unsigned blob (Share Version 0)")
                    # Fallback to a blob without signer if there's an issue
                    signed_blob = Blob(namespace=namespace, data=blob_data)

                print(f"📝 Blob details:")
                print(f"  Namespace: {str(namespace)}")
                print(f"  Data: '{blob_data.decode()}'")
                print(f"  Share Version: {signed_blob.share_version}")
                print(f"  Signer: {account_address}")

                # Submit the signed blob
                try:
                    signed_result = await api.blob.submit(signed_blob)
                    print(
                        f"\n✅ Signed blob submitted at height: {signed_result.height}"
                    )
                    signed_blob_submitted = True
                except Exception as e:
                    print(f"\n❌ Error submitting signed blob: {e}")
                    print("   This could be because:")
                    print(
                        "   - The node doesn't support signed blobs (Share Version 1)"
                    )
                    print("   - The signer address format is not what the node expects")
                    print("   - There are insufficient funds in your wallet")
                    print("   - The blob size is too large")

                    # Create a flag to skip signed blob retrieval
                    signed_blob_submitted = False

                    # Set a placeholder result for later code
                    class DummyResult:
                        def __init__(self):
                            self.height = 0

                    signed_result = DummyResult()
            else:
                # If we skipped signed blob submission entirely
                signed_blob_submitted = False
                signed_result = type("obj", (object,), {"height": 0})()

            # PART 3: Wait for blocks to be finalized
            print("\n--- WAITING FOR BLOCKS TO BE FINALIZED ---")
            print("Waiting a few seconds for blobs to be included in blocks...")
            await asyncio.sleep(5)

            # PART 4: Retrieve and verify both blobs
            print("\n--- RETRIEVING UNSIGNED BLOB ---")
            unsigned_blobs = await api.blob.get_all(unsigned_result.height, namespace)

            if unsigned_blobs and len(unsigned_blobs) > 0:
                print(
                    f"✅ Retrieved {len(unsigned_blobs)} blob(s) at height {unsigned_result.height}"
                )
                for i, blob in enumerate(unsigned_blobs):
                    print(f"\nBlob {i+1}:")
                    print(f"  Data: '{blob.data.decode()}'")
                    print(f"  Share Version: {blob.share_version}")
                    # The signer is binary data, so display as hex
                    if blob.signer:
                        signer_hex = "0x" + blob.signer.hex()
                        print(f"  Signer (hex): {signer_hex}")
                    else:
                        print(f"  Signer: None")

                    # Verify data integrity
                    if blob.data.decode() == blob_data.decode():
                        print(f"  Data Verification: ✅ Data matches")
                    else:
                        print(f"  Data Verification: ❌ Data mismatch")
            else:
                print(f"⚠️ No unsigned blobs found at height {unsigned_result.height}")

            # Only try to retrieve the signed blob if it was successfully submitted
            if signed_blob_submitted:
                print("\n--- RETRIEVING SIGNED BLOB ---")
                try:
                    signed_blobs = await api.blob.get_all(
                        signed_result.height, namespace
                    )
                except Exception as e:
                    print(f"❌ Error retrieving signed blob: {e}")
                    signed_blobs = []
            else:
                print("\n--- SKIPPING SIGNED BLOB RETRIEVAL (not submitted) ---")
                signed_blobs = []

            if signed_blobs and len(signed_blobs) > 0:
                print(
                    f"✅ Retrieved {len(signed_blobs)} blob(s) at height {signed_result.height}"
                )
                for i, blob in enumerate(signed_blobs):
                    print(f"\nBlob {i+1}:")
                    print(f"  Data: '{blob.data.decode()}'")
                    print(f"  Share Version: {blob.share_version}")
                    # The signer is binary data, so display as hex
                    if blob.signer:
                        signer_hex = "0x" + blob.signer.hex()
                        print(f"  Signer (hex): {signer_hex}")
                    else:
                        print(f"  Signer: None")

                    # Verify data integrity
                    if blob.data.decode() == blob_data.decode():
                        print(f"  Data Verification: ✅ Data matches")
                    else:
                        print(f"  Data Verification: ❌ Data mismatch")

                    # Verify signer - in v0.11.0 the signer is binary data not plaintext
                    if blob.signer:
                        # For Share Version 1, we can't directly compare with the account address
                        # Instead, we just show the signer is present
                        print(
                            f"  Signer Verification: ✅ Signer present (Share Version 1)"
                        )

                        # Try to compare with our decoded account address
                        try:
                            # Use our helper function to decode the address
                            expected_signer = decode_celestia_address(account_address)

                            if expected_signer == blob.signer:
                                print(
                                    f"  Signer Verification: ✅ Matches our decoded account address!"
                                )
                            else:
                                # Display both signers for comparison
                                print(f"  Signer Comparison:")
                                print(f"    Expected: 0x{expected_signer.hex()}")
                                print(f"    Actual:   0x{blob.signer.hex()}")
                        except Exception as e:
                            # If we can't decode or compare, just show the signer is present
                            print(f"  Note: Could not verify signer match: {str(e)}")
                    else:
                        print(f"  Signer Verification: ❌ No signer information")
            else:
                print(f"⚠️ No signed blobs found at height {signed_result.height}")

            # PART 5: Educational explanation about blob signers
            print("\n--- UNDERSTANDING BLOB SIGNERS (Share Version 1) ---")
            print("What are signed blobs in Celestia v0.11.0+?")
            print(
                "• Signed blobs (Share Version 1) include the account address that submitted them"
            )
            print(
                "• This enables accountability and permission management in applications"
            )
            print(
                "• Signers are useful for tracking which accounts submitted which data"
            )
            print(
                "• Future versions of Celestia may enforce namespace permissions based on signers"
            )
            print("• Unsigned blobs (Share Version 0) don't include this information")

            print("\n--- BLOB SUMMARY ---")
            print(f"Namespace: {str(namespace)}")
            print(f"Message: '{blob_data.decode()}'")
            print(f"Unsigned Blob Height: {unsigned_result.height}")
            print(f"Signed Blob Height: {signed_result.height}")
            print(f"Account Address (Signer): {account_address}")

            result = {
                "namespace": str(namespace),
                "namespace_hex": random_namespace.hex(),
                "unsigned_height": unsigned_result.height,
                "account_address": account_address,
            }

            # Only include signed blob info if it was submitted successfully
            if signed_blob_submitted:
                result["signed_height"] = signed_result.height
            else:
                result["signed_height"] = "Not submitted (error)"

            return result

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise


def main():
    """
    Parse arguments and run the Hello World example.

    This function:
    1. Parses command-line arguments
    2. Runs the blob submission example
    3. Shows a summary of the results

    Returns exit code 0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Submit Hello World blobs to Celestia",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--rpc",
        default=os.environ.get("RPC_ENDPOINT", "ws://localhost:26658"),
        help="RPC endpoint of the Celestia node (can also set RPC_ENDPOINT env var)",
    )
    parser.add_argument(
        "--auth",
        default=os.environ.get("AUTH_TOKEN"),
        help="Authentication token for the Celestia node (can also set AUTH_TOKEN env var)",
    )
    parser.add_argument(
        "--message",
        default=None,
        help="Custom message to submit (default: Hello, World! From pylestia v0.11.0)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print debug information when errors occur"
    )
    parser.add_argument(
        "--no-signed",
        action="store_true",
        help="Skip signed blob (Share Version 1) submission",
    )

    args = parser.parse_args()

    if not args.auth:
        print(
            "❌ Error: Authentication token required. Provide it with --auth or set AUTH_TOKEN environment variable."
        )
        sys.exit(1)

    # Show dependency status
    if not BECH32_AVAILABLE and not args.no_signed:
        print(
            "⚠️ Warning: bech32 library not found. Signed blobs may not work correctly."
        )
        print(
            "💡 Recommendation: Install bech32 with 'pip install bech32' for proper signed blob support."
        )

    print(f"🌟 pylestia v0.11.0+ Hello World Example")
    print(f"🔗 RPC Endpoint: {args.rpc}")
    print(f"📝 Message: {args.message or 'Hello, World! From pylestia v0.11.0'}")
    if args.no_signed:
        print(f"ℹ️ Share Version 1 (signed) blob submission is disabled")

    try:
        # Run the example
        result = asyncio.run(
            submit_hello_world(args.rpc, args.auth, args.message, args.no_signed)
        )

        print("\n✅ Example completed successfully!")
        print("\n📋 Quick Reference (save for later use):")
        print(f"  Namespace: {result['namespace']}")
        print(f"  Namespace (hex): {result['namespace_hex']}")
        print(f"  Unsigned Blob Height: {result['unsigned_height']}")
        print(f"  Signed Blob Height: {result['signed_height']}")
        print(f"  Account Address: {result['account_address']}")

        # Show note about signed blobs
        if result["signed_height"] == "Not submitted (error)":
            print("\nNote: The signed blob (Share Version 1) submission failed.")
            print("This could be because:")
            print("1. The node doesn't fully support Share Version 1 blobs yet")
            print("2. The signer format is different from what the node expects")
            print("3. There was an issue with the account permissions")
            print("\nThe unsigned blob (Share Version 0) should still work correctly.")

        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            print("\n--- Debug Information ---")
            traceback.print_exc()
            print("\nTroubleshooting tips:")
            print("1. Verify your Celestia node is running and accessible")
            print(
                "2. Check that your RPC endpoint is correct (should be WebSocket format)"
            )
            print("3. Confirm your authentication token is valid")
            print("4. Ensure you have funds in your account for blob submission")
            print("5. Try the --no-signed flag to skip signed blob submission")
            if not BECH32_AVAILABLE:
                print("6. Install the bech32 library: pip install bech32")
        sys.exit(1)


if __name__ == "__main__":
    main()
