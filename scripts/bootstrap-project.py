#!/usr/bin/env python3
"""Create a safe, project-specific governance starter pack.

The bootstrapper never imports live SHAs, credentials, environment paths, or
historical decisions from another project. Generated files are intentionally
DRAFT until the target project's live state is verified.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")

FILES = (
    "PROJECT_PROFILE.md",
    "project-profile.json",
    "REPOSITORY_ENGINEERING_INSTRUCTIONS.md",
    "ENGINEERING_ENVIRONMENT_CONTRACT.md",
    "RESOURCE_MAP.md",
    "ADOPTION_STATUS.md",
)


def fail(message: str, code: int = 1) -> None:
    print(f"STOP: {message}", file=sys.stderr)
    raise SystemExit(code)


def validate_args(project_name: str, repository: str, branch: str) -> None:
    if not project_name.strip():
        fail("project name must be non-empty", 2)
    if not REPOSITORY_RE.fullmatch(repository):
        fail("repository must use owner/name form", 2)
    if not BRANCH_RE.fullmatch(branch) or branch.startswith("/") or branch.endswith("/"):
        fail("official branch contains invalid characters", 2)


def target_dir(destination: Path) -> Path:
    return destination / "governance"


def ensure_safe_destination(destination: Path) -> Path:
    root = target_dir(destination)
    collisions = [root / name for name in FILES if (root / name).exists()]
    if collisions:
        joined = ", ".join(str(path) for path in collisions)
        fail(f"refusing to overwrite existing governance files: {joined}", 20)
    return root


def project_profile_md(project_name: str, repository: str, branch: str, source: str) -> str:
    return f"""# Project Governance Profile

Status: DRAFT — LIVE VERIFICATION REQUIRED
Governance baseline: {source}

## Project Identity

PROJECT NAME: {project_name}
REPOSITORY: {repository}
OFFICIAL BRANCH: {branch}

## Governing Instructions

REPOSITORY INSTRUCTION FILE: [VERIFY OR CREATE]
PROJECT INSTRUCTION FILE: [VERIFY OR CREATE]
ENGINEERING GUIDE: [VERIFY OR CREATE]
SUBSYSTEM CONTRACTS: [VERIFY CURRENT PROJECT]

## Engineering Systems

CI SYSTEM: [VERIFY LIVE]
EXECUTION ENVIRONMENT: [VERIFY LIVE]
CONTROLLER: Engineering Controller
EXECUTOR: Engineering Executor

## Protected Actions

PROTECTED ACTIONS:
- merge
- release
- tag
- production_deploy
- force_push
- history_rewrite
- destructive_infrastructure
- credential_rotation

## Verification and Evidence

TEST STRATEGY: [DERIVE FROM CURRENT PROJECT]
EVIDENCE LOCATION: .evidence/
REPORT LOCATION: .reports/
BACKUP STRATEGY: [VERIFY LIVE]

## Project-Specific Stop Conditions

- Do not mutate source until repository identity, official branch, remote HEAD, local HEAD, and working-tree state are verified.
- Add only project-specific stop conditions after inspecting current production source and environment.

## Notes

This profile was generated as a starter only.
Production source is the authority.
Do not copy SHAs, credentials, environment paths, or historical decisions from another project.
"""


def project_profile_json(project_name: str, repository: str, branch: str, source: str) -> str:
    data = {
        "status": "DRAFT_LIVE_VERIFICATION_REQUIRED",
        "governance_source": source,
        "project_name": project_name,
        "repository": repository,
        "official_branch": branch,
        "repository_instruction_file": None,
        "project_instruction_file": None,
        "engineering_guide": None,
        "subsystem_contracts": [],
        "ci_system": None,
        "execution_environment": None,
        "controller": "Engineering Controller",
        "executor": "Engineering Executor",
        "protected_actions": [
            "merge",
            "release",
            "tag",
            "production_deploy",
            "force_push",
            "history_rewrite",
            "destructive_infrastructure",
            "credential_rotation",
        ],
        "test_strategy": "VERIFY_FROM_CURRENT_PROJECT",
        "evidence_location": ".evidence/",
        "report_location": ".reports/",
        "backup_strategy": None,
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def repository_instructions(repository: str, branch: str, source: str) -> str:
    return f"""# Repository Engineering Instructions

Governance baseline: {source}
Repository: {repository}
Official branch: {branch}
Status: DRAFT — VERIFY AGAINST LIVE REPOSITORY

This file owns repository-specific execution rules. It may narrow authority but must not override the Master Governance or current owner instruction.

## Git Safety

- Never mutate source before Live Gate verification.
- Never infer the official HEAD from this generated file; fetch it live.
- Never force-push or rewrite published history unless explicitly authorized as a separate exceptional task.
- Never push directly to a protected official branch unless explicitly authorized.
- Prefer one confirmed problem = one branch = one pull request.
- Prefer isolated worktrees for concurrent work.

## Commit Policy

- Commit only completed bounded work.
- Review status, changed files, full diff, validation, accidental files, and secrets before the final task commit.

## Pull Request Policy

- A PR is a review surface, not a development scratchpad.
- Open/update only when the implementation is reviewable.
- Merge requires authority from the current owner instruction.

## Testing and Evidence

Required local checks: [VERIFY FROM PROJECT]
Required CI checks: [VERIFY FROM LIVE CI]
Required runtime evidence: [VERIFY FROM PROJECT]
Evidence location: .evidence/

## Repository-Specific Stop Conditions

[ADD AFTER LIVE INSPECTION]

## Protected Paths

[VERIFY FROM PROJECT]

## Notes

Generated scaffolding must be replaced or completed using live project facts.
"""


def environment_contract(project_name: str) -> str:
    return f"""# Engineering Environment Contract

Project: {project_name}
Status: DRAFT — VERIFY LIVE

## Environment Identity
Name:
Purpose:
Owner:

## Toolchain
OS:
Git:
Runtime(s):
SDK(s):
Build tools:
Container tooling:

## Source Paths
Canonical clone:
Worktrees root:

## Data Separation
Evidence root:
Reports root:
Artifacts root:
Caches root:
Temporary runs root:
Machine configuration root:
Secrets mechanism:

## Resource Policy
CPU limits:
Memory limits:
Storage limits:
Minimum free disk before mutation:
Heavy-workload lock:

## Preflight Gate

Before mutation, qualify the actual environment. Do not copy paths or capacity assumptions from another project.

## Retention
Evidence:
Reports:
Artifacts:
Caches:
Temporary runs:

## Backup and Restore
Backup target:
Backup cadence:
Restore test procedure:
Last successful restore test:

## Health Checks

## Rebuild Procedure
"""


def resource_map(project_name: str, repository: str, source: str) -> str:
    return f"""# Project Sources / Resource Map

Project: {project_name}
Repository: {repository}
Governance baseline: {source}
Status: DRAFT — VERIFY LIVE

This file records authoritative locations. It is not a second rulebook.

## Source Repository
{repository}

## Project Instructions
[VERIFY]

## Repository Engineering Instructions
governance/REPOSITORY_ENGINEERING_INSTRUCTIONS.md

## Engineering Guide
[VERIFY]

## Subsystem Contracts
[VERIFY]

## CI
[VERIFY LIVE]

## Runtime Environments
[VERIFY LIVE]

## Evidence
.evidence/

## Reports
.reports/

## Artifacts
[VERIFY]

## Infrastructure Definitions
[VERIFY]

## Operational Dashboards / Logs
[VERIFY]
"""


def adoption_status(project_name: str, repository: str, branch: str) -> str:
    return f"""# Governance Adoption Status

Project: {project_name}
Repository: {repository}
Official branch: {branch}
Status: NOT QUALIFIED

The generated governance pack is only scaffolding.

Before marking adoption QUALIFIED:

- [ ] Verify repository identity from the live remote.
- [ ] Verify the official branch from live repository settings.
- [ ] Fetch and record the current official HEAD in each Task Packet, not here.
- [ ] Inspect current repository instruction files.
- [ ] Inspect CI workflows and required checks.
- [ ] Inspect deployment/runtime environments.
- [ ] Define project-specific tests and evidence requirements.
- [ ] Define protected paths and project-specific stop conditions.
- [ ] Confirm secrets mechanism and backup/restore strategy.
- [ ] Run a read-only governance task end to end.
- [ ] Run one isolated implementation task end to end.
- [ ] Confirm resulting evidence is attributable to the exact tested SHA.

Only then change this file's status to QUALIFIED.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap governance for a new or existing project.")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--repository", required=True, help="GitHub-style owner/name identity.")
    parser.add_argument("--official-branch", default="main")
    parser.add_argument("--destination", required=True, help="Target project root.")
    parser.add_argument(
        "--governance-source",
        default="engineering-governance/MASTER_GOVERNANCE.md",
        help="Reference to the governing baseline.",
    )
    args = parser.parse_args()

    validate_args(args.project_name, args.repository, args.official_branch)
    destination = Path(args.destination)
    root = ensure_safe_destination(destination)
    root.mkdir(parents=True, exist_ok=True)

    content = {
        "PROJECT_PROFILE.md": project_profile_md(
            args.project_name, args.repository, args.official_branch, args.governance_source
        ),
        "project-profile.json": project_profile_json(
            args.project_name, args.repository, args.official_branch, args.governance_source
        ),
        "REPOSITORY_ENGINEERING_INSTRUCTIONS.md": repository_instructions(
            args.repository, args.official_branch, args.governance_source
        ),
        "ENGINEERING_ENVIRONMENT_CONTRACT.md": environment_contract(args.project_name),
        "RESOURCE_MAP.md": resource_map(args.project_name, args.repository, args.governance_source),
        "ADOPTION_STATUS.md": adoption_status(
            args.project_name, args.repository, args.official_branch
        ),
    }

    for name, text in content.items():
        (root / name).write_text(text, encoding="utf-8")

    print("BOOTSTRAP=PASS")
    print(f"project={args.project_name}")
    print(f"repository={args.repository}")
    print(f"official_branch={args.official_branch}")
    print(f"governance_dir={root.resolve()}")
    print("status=DRAFT_LIVE_VERIFICATION_REQUIRED")


if __name__ == "__main__":
    main()
