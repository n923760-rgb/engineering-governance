#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SOURCE_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")


def fail(message: str, code: int = 1) -> None:
    print(f"INVALID: {message}", file=sys.stderr)
    raise SystemExit(code)


def parse_timestamp(value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        fail("timestamp must be a non-empty ISO-8601 string")
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        fail("timestamp must be ISO-8601")
    if parsed.tzinfo is None:
        fail("timestamp must include a timezone offset")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_artifact(base: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        fail("artifact path must be a non-empty string")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        fail(f"artifact path escapes manifest directory: {value}")
    resolved_base = base.resolve()
    resolved = (base / candidate).resolve()
    if resolved != resolved_base and resolved_base not in resolved.parents:
        fail(f"artifact path escapes manifest directory: {value}")
    return resolved


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate-evidence-manifest.py <manifest.json>", 2)

    manifest_path = Path(sys.argv[1])
    if not manifest_path.is_file():
        fail(f"manifest not found: {manifest_path}", 2)

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot parse JSON: {exc}")

    for key in ("task_id", "source_sha", "execution_environment", "timestamp", "artifacts"):
        if key not in data:
            fail(f"missing required field: {key}")

    if not isinstance(data["task_id"], str) or not data["task_id"].strip():
        fail("task_id must be a non-empty string")
    if not SOURCE_SHA_RE.fullmatch(str(data["source_sha"])):
        fail("source_sha must look like a Git SHA")
    if not isinstance(data["execution_environment"], str) or not data["execution_environment"].strip():
        fail("execution_environment must be a non-empty string")
    parse_timestamp(data["timestamp"])

    artifacts = data["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        fail("artifacts must be a non-empty array")

    base = manifest_path.parent
    seen: set[str] = set()

    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            fail(f"artifacts[{index}] must be an object")
        for key in ("path", "sha256", "size", "sensitive_data"):
            if key not in artifact:
                fail(f"artifacts[{index}] missing required field: {key}")

        path_value = artifact["path"]
        if path_value in seen:
            fail(f"duplicate artifact path: {path_value}")
        seen.add(path_value)

        path = resolve_artifact(base, path_value)
        if not path.is_file():
            fail(f"artifact is missing: {path_value}")

        expected_hash = str(artifact["sha256"]).lower()
        if not SHA_RE.fullmatch(expected_hash):
            fail(f"artifacts[{index}].sha256 must be 64 hexadecimal characters")

        size = artifact["size"]
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            fail(f"artifacts[{index}].size must be a non-negative integer")
        actual_size = path.stat().st_size
        if actual_size != size:
            fail(
                f"artifact size mismatch for {path_value}: expected {size}, actual {actual_size}"
            )

        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            fail(
                f"artifact SHA-256 mismatch for {path_value}: "
                f"expected {expected_hash}, actual {actual_hash}"
            )

        if not isinstance(artifact["sensitive_data"], bool):
            fail(f"artifacts[{index}].sensitive_data must be boolean")

    print(f"VALID: evidence manifest verified {len(artifacts)} artifact(s)")


if __name__ == "__main__":
    main()
