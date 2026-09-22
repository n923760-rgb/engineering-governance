#!/usr/bin/env python3
"""Fail-closed readiness gate for the engineering-governance v1 release candidate."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^1\.0\.0-rc\.[1-9][0-9]*$")

REQUIRED_CAPABILITIES = {
    "master governance": "MASTER_GOVERNANCE.md",
    "governance CI": ".github/workflows/governance-ci.yml",
    "project bootstrap": "scripts/bootstrap-project.py",
    "repository live gate": "scripts/verify-repository-state.sh",
    "pull request state gate": "scripts/verify-github-pr-state.py",
    "environment resource gate": "scripts/verify-environment-capacity.py",
    "task authority validator": "scripts/validate-task-packet.py",
    "result evidence validator": "scripts/validate-result-packet.py",
    "evidence manifest validator": "scripts/validate-evidence-manifest.py",
    "baseline secret scanner": "scripts/scan-secrets.py",
    "adoption guide": "docs/ADOPTION_GUIDE.md",
    "PR state policy": "docs/PULL_REQUEST_STATE_POLICY.md",
    "authority policy": "docs/AUTHORITY_MODEL.md",
    "evidence policy": "docs/EVIDENCE_POLICY.md",
    "secrets policy": "docs/SECRETS_POLICY.md",
    "stop conditions": "docs/STOP_CONDITIONS.md",
    "qualification suite": "qualification/run-qualification.py",
    "qualification coverage": "qualification/README.md",
}

EXECUTABLE_SCRIPTS = [
    "scripts/bootstrap-project.py",
    "scripts/verify-repository-state.sh",
    "scripts/verify-github-pr-state.py",
    "scripts/verify-environment-capacity.py",
    "scripts/validate-task-packet.py",
    "scripts/validate-result-packet.py",
    "scripts/validate-evidence-manifest.py",
    "scripts/scan-secrets.py",
    "qualification/run-qualification.py",
]

QUALIFICATION_MARKERS = [
    "Repository live-state safety:",
    "Task Packet authority:",
    "Result Packet evidence:",
    "Evidence manifest integrity:",
    "Environment / resource gate:",
    "Project adoption bootstrap:",
    "Pull request state:",
    "Secret hygiene:",
]

WORKFLOW_MARKERS = [
    "Verify execution environment capacity",
    "Validate repository contracts",
    "Scan tracked text for baseline secret patterns",
    "Run governance stop-condition qualification",
    "Record source identity",
]


def fail(message: str) -> None:
    print(f"NOT_READY: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not VERSION_RE.fullmatch(version):
        fail(f"VERSION must be a v1 release candidate (1.0.0-rc.N), got {version!r}")

    missing = [
        f"{name} ({rel})"
        for name, rel in REQUIRED_CAPABILITIES.items()
        if not (ROOT / rel).is_file()
    ]
    if missing:
        fail("missing required capabilities: " + ", ".join(missing))

    for rel in EXECUTABLE_SCRIPTS:
        if (ROOT / rel).stat().st_mode & 0o111 == 0:
            fail(f"required executable is not executable: {rel}")

    qualification = (ROOT / "qualification" / "README.md").read_text(encoding="utf-8")
    for marker in QUALIFICATION_MARKERS:
        if marker not in qualification:
            fail(f"qualification coverage missing marker: {marker}")

    workflow = (ROOT / ".github" / "workflows" / "governance-ci.yml").read_text(encoding="utf-8")
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            fail(f"Governance CI missing required step: {marker}")

    if (ROOT / ".github" / "workflows" / "runner-diagnostic.yml").exists():
        fail("temporary runner diagnostic workflow must not exist in release candidate")

    bootstrap_help = subprocess.run(
        [sys.executable, "scripts/bootstrap-project.py", "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if bootstrap_help.returncode != 0:
        fail("project bootstrap command is not runnable")

    if "DRAFT_LIVE_VERIFICATION_REQUIRED" not in (
        ROOT / "scripts" / "bootstrap-project.py"
    ).read_text(encoding="utf-8"):
        fail("project bootstrap no longer preserves draft/live-verification semantics")

    master = (ROOT / "MASTER_GOVERNANCE.md").read_text(encoding="utf-8")
    if "Production source is the authority." not in master:
        fail("master governance lost the production-source authority invariant")

    print("V1_READINESS=PASS")
    print(f"version={version}")
    print(f"capabilities={len(REQUIRED_CAPABILITIES)}")
    print(f"qualification_domains={len(QUALIFICATION_MARKERS)}")
    print("release_tag_created=no")
    print("github_release_created=no")


if __name__ == "__main__":
    main()
