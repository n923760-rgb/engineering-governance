#!/usr/bin/env python3
import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

EXIT_PATH_UNAVAILABLE = 30
EXIT_INSUFFICIENT_DISK = 31
EXIT_NOT_WRITABLE = 32


def stop(message: str, code: int) -> None:
    print(f"STOP: {message}", file=sys.stderr)
    raise SystemExit(code)


def non_negative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify basic execution-environment capacity before engineering work."
    )
    parser.add_argument("--path", default=".", help="Working path to qualify.")
    parser.add_argument(
        "--min-free-bytes",
        type=non_negative_int,
        default=0,
        help="Minimum required free disk bytes.",
    )
    parser.add_argument(
        "--skip-write-test",
        action="store_true",
        help="Skip the temporary write probe when the task is strictly read-only.",
    )
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists() or not target.is_dir():
        stop(f"environment path is unavailable or not a directory: {target}", EXIT_PATH_UNAVAILABLE)

    try:
        usage = shutil.disk_usage(target)
    except OSError as exc:
        stop(f"cannot inspect disk capacity for {target}: {exc}", EXIT_PATH_UNAVAILABLE)

    if usage.free < args.min_free_bytes:
        stop(
            f"insufficient free disk: required={args.min_free_bytes} actual={usage.free}",
            EXIT_INSUFFICIENT_DISK,
        )

    if not args.skip_write_test:
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=target,
                prefix=".governance-write-test-",
                delete=True,
            ) as handle:
                handle.write(b"governance-write-test\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            stop(f"environment path is not safely writable: {target}: {exc}", EXIT_NOT_WRITABLE)

    print("ENVIRONMENT_GATE=PASS")
    print(f"path={target.resolve()}")
    print(f"disk_total_bytes={usage.total}")
    print(f"disk_used_bytes={usage.used}")
    print(f"disk_free_bytes={usage.free}")
    print(f"write_test={'SKIPPED' if args.skip_write_test else 'PASS'}")


if __name__ == "__main__":
    main()
