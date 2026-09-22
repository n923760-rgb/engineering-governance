#!/usr/bin/env python3
"""Deterministic repository-level validation for the governance system."""
from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "MASTER_GOVERNANCE.md",
    "README.md",
    "VERSION",
    "CHANGELOG.md",
    "docs/V1_READINESS.md",
    "scripts/verify-v1-readiness.py",
    "templates/PROJECT_PROFILE.md",
    "templates/TASK_PACKET.md",
    "templates/RESULT_PACKET.md",
    "templates/EVIDENCE_MANIFEST.md",
    "templates/REPOSITORY_ENGINEERING_INSTRUCTIONS.md",
    "templates/ENGINEERING_ENVIRONMENT_CONTRACT.md",
    "templates/SUBSYSTEM_CONTRACT.md",
    "templates/RESOURCE_MAP.md",
    "checklists/PRE_TASK_CHECKLIST.md",
    "checklists/PRE_MERGE_CHECKLIST.md",
    "checklists/CI_FAILURE_CHECKLIST.md",
    "checklists/RELEASE_CHECKLIST.md",
    "schemas/project-profile.schema.json",
    "schemas/task-packet.schema.json",
    "schemas/result-packet.schema.json",
    "schemas/evidence-manifest.schema.json",
    "examples/task-packet.example.json",
    "examples/result-packet.example.json",
    "examples/evidence-manifest.example.json",
    "examples/artifacts/evidence-fixture.txt",
    "scripts/verify-repository-state.sh",
    "scripts/verify-clean-tree.sh",
    "scripts/verify-environment-capacity.py",
    "scripts/verify-github-pr-state.py",
    "scripts/bootstrap-project.py",
    "scripts/collect-git-evidence.sh",
    "scripts/validate-task-packet.py",
    "scripts/validate-result-packet.py",
    "scripts/validate-evidence-manifest.py",
    "docs/AUTHORITY_MODEL.md",
    "docs/CONTROLLER_EXECUTOR_MODEL.md",
    "docs/EVIDENCE_POLICY.md",
    "docs/SECRETS_POLICY.md",
    "docs/STOP_CONDITIONS.md",
    "docs/ADOPTION_GUIDE.md",
    "docs/PULL_REQUEST_STATE_POLICY.md",
    "qualification/README.md",
    "qualification/run-qualification.py",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        fail(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def check_required_paths() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
    if missing:
        fail("missing required paths: " + ", ".join(missing))


def check_version() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(
        r"(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)"
        r"(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?",
        version,
    ):
        fail(f"VERSION is not valid semantic versioning: {version!r}")


def check_json() -> None:
    for path in sorted(ROOT.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def check_shell() -> None:
    scripts = sorted((ROOT / "scripts").glob("*.sh"))
    if not scripts:
        fail("no shell scripts found")
    for path in scripts:
        run(["bash", "-n", str(path.relative_to(ROOT))])
        if path.stat().st_mode & 0o111 == 0:
            fail(f"shell script is not executable: {path.relative_to(ROOT)}")


def check_python() -> None:
    scripts = sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "qualification").glob("*.py"))
    if not scripts:
        fail("no Python scripts found")
    for path in scripts:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            fail(f"Python syntax error in {path.relative_to(ROOT)}: {exc.msg}")


def check_packet_examples() -> None:
    run([sys.executable, "scripts/validate-task-packet.py", "examples/task-packet.example.json"])
    run([sys.executable, "scripts/validate-result-packet.py", "examples/result-packet.example.json"])
    run([sys.executable, "scripts/validate-evidence-manifest.py", "examples/evidence-manifest.example.json"])


def check_master_integrity() -> None:
    master = (ROOT / "MASTER_GOVERNANCE.md").read_text(encoding="utf-8")
    required_phrases = [
        "Production source is the authority.",
        "Current Problem → Current Source → Isolated Change → Evidence → Review → Merge Decision",
        "Stopping safely is an engineering success, not a failure.",
        "Final Governance Principle",
    ]
    for phrase in required_phrases:
        if phrase not in master:
            fail(f"MASTER_GOVERNANCE.md missing anchor phrase: {phrase}")
    if len(master.splitlines()) < 1000:
        fail("MASTER_GOVERNANCE.md appears truncated (<1000 lines)")


def check_template_contracts() -> None:
    expectations = {
        "templates/TASK_PACKET.md": [
            "## TASK TYPE", "## AUTHORITY", "## MACHINE-READABLE ACTION AUTHORITY",
            "## LIVE GATE", "## STOP CONDITIONS", "## SUCCESS CRITERIA",
        ],
        "templates/RESULT_PACKET.md": [
            "## Repository Identity", "## Validation Actually Run",
            "### Facts", "### Inferences", "### Assumptions", "## Residual Risks",
        ],
        "templates/EVIDENCE_MANIFEST.md": [
            "SHA-256", "size in bytes", "sensitive-data flag",
        ],
        "templates/ENGINEERING_ENVIRONMENT_CONTRACT.md": [
            "## Preflight Gate", "Minimum free disk before mutation:",
        ],
        "templates/PROJECT_PROFILE.md": [
            "PROJECT NAME:", "REPOSITORY:", "OFFICIAL BRANCH:",
            "PROTECTED ACTIONS:", "TEST STRATEGY:",
        ],
    }
    for rel, anchors in expectations.items():
        content = (ROOT / rel).read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in content:
                fail(f"{rel} missing required anchor: {anchor}")


def check_git_exclusions() -> None:
    try:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=True
        ).stdout.splitlines()
    except Exception:
        return
    forbidden_prefixes = (".evidence/", ".reports/", ".tmp/")
    bad = [p for p in tracked if p.startswith(forbidden_prefixes) or "__pycache__" in p or p.endswith(".pyc")]
    if bad:
        fail("forbidden generated/evidence files are tracked: " + ", ".join(bad))


def main() -> None:
    check_required_paths()
    check_version()
    check_json()
    check_shell()
    check_python()
    check_packet_examples()
    check_master_integrity()
    check_template_contracts()
    check_git_exclusions()
    print("PASS: repository governance baseline is internally consistent")


if __name__ == "__main__":
    main()
