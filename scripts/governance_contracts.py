"""Shared schema, action-authority, and evidence contracts.

Approved inputs must be selected independently by the controller. These checks
do not authenticate an owner's identity or establish an executor's honesty.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
STATUSES = {"PASS", "FAIL", "BLOCKED", "UNKNOWN", "NOT RUN", "SKIPPED"}
PROTECTED_ACTIONS = {
    "merge", "release", "tag", "signing", "store_publication",
    "production_deploy", "dns_changes", "destructive_database_migration",
    "production_database_operations", "production_credential_rotation",
    "credential_rotation", "server_or_cloud_destruction_or_reinstall",
    "destructive_infrastructure", "repository_deletion", "force_push",
    "history_rewrite", "permanent_release_artifact_deletion",
    "destructive_billing_or_cloud_resource_actions",
}
READ_ACTIONS = {
    "read", "inspect_source", "inspect_logs", "inspect_ci", "inspect_pr",
    "run_validation", "write_report",
}
REPOSITORY_ACTIONS = {"modify", "edit_source", "commit", "push", "create_pr", "update_pr"}
REPOSITORY_PROTECTED = {
    "merge", "release", "tag", "signing", "store_publication",
    "production_deploy", "force_push", "history_rewrite",
    "permanent_release_artifact_deletion", "repository_deletion",
}
TASK_ACTIONS = {
    "READ-ONLY DIAGNOSIS": READ_ACTIONS,
    "IMPLEMENTATION": READ_ACTIONS | REPOSITORY_ACTIONS | REPOSITORY_PROTECTED,
    "RUNTIME QUALIFICATION": READ_ACTIONS,
    "CI INVESTIGATION": READ_ACTIONS | {"rerun_workflow"},
    "INFRASTRUCTURE MAINTENANCE": READ_ACTIONS | REPOSITORY_ACTIONS | PROTECTED_ACTIONS
        | {"install_packages", "configure_environment"},
}


class ContractError(ValueError):
    pass


def load_object(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractError(f"cannot read JSON from {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"{path.name} must contain a JSON object")
    return data


def validate_schema(data: dict, schema_name: str) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise ContractError("jsonschema is required; install requirements.txt") from exc
    schema = load_object(ROOT / "schemas" / schema_name)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(e.path))
    if errors:
        error = errors[0]
        location = ".".join(str(v) for v in error.path) or "packet"
        raise ContractError(f"schema violation at {location}: {error.message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ContractError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ContractError("timestamp must include a timezone offset")
    return parsed


def resolve_artifact(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ContractError(f"artifact path escapes manifest directory: {value}")
    resolved = (base / candidate).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ContractError(f"artifact path escapes manifest directory: {value}")
    return resolved


def validate_task(data: dict) -> None:
    validate_schema(data, "task-packet.schema.json")
    requested = set(data["requested_actions"])
    authorized = set(data["authorized_actions"])
    outside = requested - authorized
    if outside:
        raise ContractError("requested actions are not authorized: " + ", ".join(sorted(outside)))
    forbidden = (requested | authorized) - TASK_ACTIONS[data["task_type"]]
    if forbidden:
        raise ContractError("actions prohibited for task type: " + ", ".join(sorted(forbidden)))
    # Packet declarations may add protection; they cannot remove this minimum.
    protected = PROTECTED_ACTIONS | set(data["protected_actions"])
    records = data["protected_action_authorizations"]
    targets = data.get("action_targets", {})
    needed = authorized & protected
    for action in sorted(needed):
        record = records.get(action)
        if not record:
            raise ContractError(f"protected action {action} lacks explicit owner authorization")
        if record["status"] != "ACTIVE":
            raise ContractError(f"protected action {action} authorization is not active")
        if record["repository"] != data["repository"]:
            raise ContractError(f"protected action {action} authorization repository mismatch")
        if not targets.get(action) or record["target"] != targets[action]:
            raise ContractError(f"protected action {action} authorization target mismatch")
        if record.get("expires_at") and parse_timestamp(record["expires_at"]) <= datetime.now(timezone.utc):
            raise ContractError(f"protected action {action} authorization expired")
    if set(records) - needed:
        raise ContractError("authorization records exist for actions that are not authorized protected actions")
    existing_pr = data.get("existing_pr")
    if existing_pr is not None:
        if not data.get("expected_pr_head") or not data.get("expected_pr_base"):
            raise ContractError("expected_pr_head and expected_pr_base are required when existing_pr is set")
    elif data.get("expected_pr_head") is not None or data.get("expected_pr_base") is not None:
        raise ContractError("expected_pr_head/base must be null when existing_pr is null")


def validate_manifest(path: Path) -> dict:
    data = load_object(path)
    validate_schema(data, "evidence-manifest.schema.json")
    parse_timestamp(data["timestamp"])
    seen = set()
    for artifact in data["artifacts"]:
        name = artifact["path"]
        if name in seen:
            raise ContractError(f"duplicate artifact path: {name}")
        seen.add(name)
        artifact_path = resolve_artifact(path.parent, name)
        if not artifact_path.is_file():
            raise ContractError(f"artifact is missing: {name}")
        if artifact_path.stat().st_size != artifact["size"]:
            raise ContractError(f"artifact size mismatch for {name}")
        if sha256(artifact_path) != artifact["sha256"].lower():
            raise ContractError(f"artifact SHA-256 mismatch for {name}")
    return data
