#!/usr/bin/env python3
"""Validate evidence metadata and the exact bytes of retained artifacts."""
import argparse
import sys
from pathlib import Path

from governance_contracts import ContractError, validate_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = validate_manifest(args.manifest)
    except ContractError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"VALID: evidence manifest verified {len(data['artifacts'])} artifact(s)")


if __name__ == "__main__":
    main()
