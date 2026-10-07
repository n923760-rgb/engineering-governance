#!/usr/bin/env python3
"""Compare an approved lock to an independently selected governance source."""
import argparse
import sys
from pathlib import Path

from governance_contracts import ContractError, load_object
from governance_lock import verify_lock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lock", type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--require-clean-source", action="store_true")
    args = parser.parse_args()
    try:
        verify_lock(load_object(args.lock), args.source, args.require_clean_source)
    except ContractError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("GOVERNANCE_LOCK_INTEGRITY=PASS")
    print("project_adoption_qualified=no")


if __name__ == "__main__":
    main()
