"""Record and compare the exact reusable governance source adopted by a project."""
from __future__ import annotations

import subprocess
import shutil
from datetime import datetime, timezone
from pathlib import Path

from governance_contracts import ContractError, sha256, validate_schema

CENTRAL_REPOSITORY = "https://github.com/n923760-rgb/engineering-governance"
LOCKED_PATHS = (
    "MASTER_GOVERNANCE.md", "VERSION", "requirements.txt",
    "docs/AUTHORITY_MODEL.md", "docs/RISK_PROFILES.md",
    "docs/UNTRUSTED_CONTENT_POLICY.md", "docs/CONTROLLER_EXECUTOR_MODEL.md",
    "docs/GOVERNANCE_VERSIONING.md", "docs/EVIDENCE_POLICY.md",
    "docs/SECRETS_POLICY.md", "docs/STOP_CONDITIONS.md",
    "templates/PROJECT_AGENTS.md", "templates/REPOSITORY_ENGINEERING_INSTRUCTIONS.md",
    "schemas/task-packet.schema.json", "schemas/result-packet.schema.json",
    "schemas/evidence-manifest.schema.json", "schemas/project-profile.schema.json",
    "schemas/governance-lock.schema.json",
    "scripts/governance_contracts.py", "scripts/governance_lock.py",
    "scripts/validate-task-packet.py", "scripts/validate-result-packet.py",
    "scripts/validate-evidence-manifest.py", "scripts/verify-repository-state.py",
    "scripts/verify-repository-state.sh", "scripts/verify-governance-lock.py",
    "scripts/bootstrap-project.py",
)


def source_state(source: Path) -> tuple[str | None, bool | None]:
    if shutil.which("git") is None:
        return None, None
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=source, text=True, capture_output=True)
    if top.returncode or Path(top.stdout.strip()).resolve() != source.resolve():
        return None, None
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=source, text=True, capture_output=True)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=source, text=True, capture_output=True)
    if head.returncode or status.returncode:
        return None, None
    return head.stdout.strip(), bool(status.stdout.strip())


def make_lock(source: Path, risk_profile: str) -> dict:
    head, dirty = source_state(source)
    for relative in LOCKED_PATHS:
        if not (source / relative).is_file():
            raise ContractError(f"governance source missing: {relative}")
    data = {
        "format_version": 1,
        "status": "DRAFT_LIVE_VERIFICATION_REQUIRED",
        "source_repository": CENTRAL_REPOSITORY,
        "source_commit_sha": head if dirty is False else None,
        "observed_git_head_sha": head,
        "source_worktree_dirty": dirty,
        "governance_version": (source / "VERSION").read_text().strip(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "risk_profile": risk_profile,
        "files": {relative: sha256(source / relative) for relative in LOCKED_PATHS},
    }
    validate_schema(data, "governance-lock.schema.json")
    return data


def verify_lock(data: dict, source: Path, require_clean: bool = False) -> None:
    validate_schema(data, "governance-lock.schema.json")
    if set(data["files"]) != set(LOCKED_PATHS):
        raise ContractError("governance lock does not cover the complete required source set")
    for relative, expected in data["files"].items():
        path = source / relative
        if not path.is_file() or sha256(path) != expected:
            raise ContractError(f"governance source hash mismatch: {relative}")
    if data["governance_version"] != (source / "VERSION").read_text().strip():
        raise ContractError("governance version mismatch")
    head, dirty = source_state(source)
    if require_clean:
        if dirty is not False or not data["source_commit_sha"] or head != data["source_commit_sha"]:
            raise ContractError("clean exact governance source commit is required")
    elif data["source_commit_sha"] and head != data["source_commit_sha"]:
        raise ContractError("governance source commit mismatch")
