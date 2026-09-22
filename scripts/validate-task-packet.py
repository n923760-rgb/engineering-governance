#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "title", "task_type", "authority", "repository", "official_branch",
    "expected_official_head", "scope", "out_of_scope", "task",
    "validation", "stop_conditions", "success_criteria"
]

TASK_TYPES = {
    "READ-ONLY DIAGNOSIS",
    "IMPLEMENTATION",
    "RUNTIME QUALIFICATION",
    "CI INVESTIGATION",
    "INFRASTRUCTURE MAINTENANCE",
}


def fail(message: str, code: int = 1) -> None:
    print(f"INVALID: {message}", file=sys.stderr)
    raise SystemExit(code)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate-task-packet.py <packet.json>", 2)
    path = Path(sys.argv[1])
    if not path.is_file():
        fail(f"file not found: {path}", 2)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot parse JSON: {exc}")

    missing = [key for key in REQUIRED if key not in data or data[key] in (None, "", [])]
    if missing:
        fail("missing required fields: " + ", ".join(missing))

    if data["task_type"] not in TASK_TYPES:
        fail(f"unsupported task_type: {data['task_type']}")

    head = str(data["expected_official_head"])
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", head):
        fail("expected_official_head must look like a Git SHA")

    print("VALID: task packet passes baseline checks")


if __name__ == "__main__":
    main()
