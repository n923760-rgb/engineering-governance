#!/usr/bin/env python3
"""Validate a controller-approved task against schemas and action policy."""
import argparse
import sys
from pathlib import Path

from governance_contracts import ContractError, load_object, validate_task


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    try:
        validate_task(load_object(args.packet))
    except ContractError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("VALID: task packet passes schema and action-authority checks")


if __name__ == "__main__":
    main()
