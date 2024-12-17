"""Test script to verify project setup."""

import os
import sys


def main():
    """Verify project setup."""
    print("\nProject Setup Verification:")
    print("-" * 50)

    # Check working directory
    print(f"Current working directory: {os.getcwd()}")

    # Check Python path
    print("\nPython path:")
    for path in sys.path:
        print(f"  {path}")

    # Try imports
    try:
        from core.connector import DatabaseConnector

        print("\nCore import successful!")
    except ImportError as e:
        print(f"\nCore import failed: {e}")

    try:
        from templates.constraints import TargetDatabaseEngine

        print("Templates import successful!")
    except ImportError as e:
        print(f"Templates import failed: {e}")


if __name__ == "__main__":
    main()
