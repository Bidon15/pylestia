#!/usr/bin/env python3
"""
Test script to verify pylestia imports are working correctly.
This script attempts to import key components from pylestia.
"""

import importlib
import sys
from typing import List, Tuple


def test_imports():
    """Attempt to import various modules from pylestia."""
    import_tests: List[Tuple[str, str]] = [
        ("pylestia", "Test top-level package import"),
        ("pylestia.Client", "Test Client import"),
        ("pylestia.types", "Test types package import"),
        ("pylestia.types.Namespace", "Test Namespace class import"),
        ("pylestia.types.Blob", "Test Blob class import"),
        ("pylestia.pylestia_core", "Test Rust extension import"),
    ]

    results = []

    print("Testing pylestia imports...\n")

    for import_path, description in import_tests:
        try:
            if "." in import_path:
                module_path, item = import_path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                getattr(module, item)
            else:
                importlib.import_module(import_path)

            print(f"✅ PASS: {description}")
            results.append(True)
        except ImportError as e:
            print(f"❌ FAIL: {description}")
            print(f"   Error: {e}")
            results.append(False)
        except AttributeError as e:
            print(f"❌ FAIL: {description}")
            print(f"   Error: {e}")
            results.append(False)

    # Print summary
    print(f"\nSummary: {results.count(True)}/{len(results)} imports successful")

    if all(results):
        print(
            "\n🎉 All pylestia imports successful! Your installation appears to be working."
        )
        return 0
    else:
        print("\n⚠️ Some imports failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(test_imports())
