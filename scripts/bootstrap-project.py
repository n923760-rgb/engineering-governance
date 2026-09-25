#!/usr/bin/env python3
"""Create a safe starter pack for the Master Engineering System.

Run only in an explicitly authorized repository-mutation round after the
read-only Master Re-baseline. The bootstrap creates scaffolding; it does not
qualify a target project or prove live facts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")

GENERATED_PATHS = (
    "governance/PROJECT_PROFILE.md",
    "governance/project-profile.json",
    "governance/REPOSITORY_ENGINEERING_INSTRUCTIONS.md",
    "governance/ENGINEERING_ENVIRONMENT_CONTRACT.md",
    "governance/RESOURCE_MAP.md",
    "governance/ADOPTION_STATUS.md",
    "ENGINEERING/MASTER_ROADMAP.md",
    "ENGINEERING/REPORTS/MASTER_ENGINEERING_BASELINE_REPORT.md",
    "ENGINEERING/EVIDENCE/README.md",
)


def fail(message: str, code: int = 1) -> None:
    print(f"STOP: {message}", file=sys.stderr)
    raise SystemExit(code)


def validate(project_name: str, repository: str, branch: str) -> None:
    if not project_name.strip():
        fail("project name must be non-empty", 2)
    if not REPOSITORY_RE.fullmatch(repository):
        fail("repository must use owner/name form", 2)
    if not BRANCH_RE.fullmatch(branch) or branch.startswith("/") or branch.endswith("/"):
        fail("invalid official branch", 2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Bootstrap Master Engineering System files after a read-only baseline "
            "and explicit mutation authorization."
        )
    )
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--official-branch", default="main")
    parser.add_argument("--destination", required=True)
    parser.add_argument(
        "--governance-source",
        default="engineering-governance/MASTER_GOVERNANCE.md",
    )
    args = parser.parse_args()
    validate(args.project_name, args.repository, args.official_branch)

    destination = Path(args.destination)
    collisions = [destination / rel for rel in GENERATED_PATHS if (destination / rel).exists()]
    if collisions:
        fail(
            "refusing to overwrite existing governance files: "
            + ", ".join(str(path) for path in collisions),
            20,
        )

    governance = destination / "governance"
    engineering = destination / "ENGINEERING"
    reports = engineering / "REPORTS"
    evidence = engineering / "EVIDENCE"

    governance.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)

    profile_md = f"""# Project Governance Profile

Status: DRAFT — LIVE VERIFICATION REQUIRED
Governance baseline: {args.governance_source}

## Project Identity
PROJECT NAME: {args.project_name}
REPOSITORY: {args.repository}
REPOSITORY URL: [VERIFY LIVE]
DEFAULT BRANCH: [VERIFY LIVE]
OFFICIAL BRANCH: {args.official_branch}

## Governing Instructions
REPOSITORY AUTHORITY FILE: [VERIFY OR CREATE]
PROJECT BASELINE: [VERIFY]
ARCHITECTURE GUIDES: [VERIFY]
SUBSYSTEM CONTRACTS: [VERIFY]

## Engineering Systems
MASTER ROADMAP: /ENGINEERING/MASTER_ROADMAP.md
MASTER BASELINE REPORT: /ENGINEERING/REPORTS/MASTER_ENGINEERING_BASELINE_REPORT.md
REPORT LOCATION: /ENGINEERING/REPORTS/
EVIDENCE LOCATION: /ENGINEERING/EVIDENCE/
CI SYSTEM: [VERIFY LIVE]
ENGINEERING LAB CONTRACT: governance/ENGINEERING_ENVIRONMENT_CONTRACT.md
EXECUTION ENVIRONMENT: [VERIFY LIVE]
VERIFIED EXECUTION CAPABILITIES: [VERIFY EACH SESSION]
CONTROLLER: Engineering Controller
EXECUTOR: Engineering Executor

## Protected Actions
PROTECTED ACTIONS: [DERIVE AND VERIFY]

## Verification and Evidence
TEST STRATEGY: [DERIVE]
ARTIFACT LOCATION: [VERIFY]
BACKUP / RESTORE STRATEGY: [VERIFY]
RELEASE MODEL: [VERIFY]
RUNTIME / DEVICE / PLATFORM MATRIX: [DERIVE]

## Notes
Live repository truth overrides historical context.
Bootstrap scaffolding does not replace the mandatory read-only Master Re-baseline.
"""

    profile = {
        "status": "DRAFT_LIVE_VERIFICATION_REQUIRED",
        "governance_source": args.governance_source,
        "project_name": args.project_name,
        "repository": args.repository,
        "repository_url": None,
        "default_branch": None,
        "official_branch": args.official_branch,
        "repository_authority_file": None,
        "project_baseline": None,
        "architecture_guides": [],
        "subsystem_contracts": [],
        "master_roadmap": "ENGINEERING/MASTER_ROADMAP.md",
        "master_baseline_report": "ENGINEERING/REPORTS/MASTER_ENGINEERING_BASELINE_REPORT.md",
        "ci_system": None,
        "engineering_lab_contract": "governance/ENGINEERING_ENVIRONMENT_CONTRACT.md",
        "execution_environment": None,
        "verified_execution_capabilities": [],
        "controller": "Engineering Controller",
        "executor": "Engineering Executor",
        "protected_actions": [
            "merge",
            "release",
            "tag",
            "signing",
            "store_publication",
            "production_deploy",
            "dns_changes",
            "destructive_database_migration",
            "production_credential_rotation",
            "server_or_cloud_destruction_or_reinstall",
            "repository_deletion",
            "force_push",
            "history_rewrite",
            "permanent_release_artifact_deletion",
            "destructive_billing_or_cloud_resource_actions",
        ],
        "test_strategy": "VERIFY_FROM_CURRENT_PROJECT",
        "evidence_location": "ENGINEERING/EVIDENCE/",
        "report_location": "ENGINEERING/REPORTS/",
        "artifact_location": None,
        "backup_restore_strategy": None,
        "release_model": None,
        "runtime_device_platform_matrix": [],
    }

    repository_rules = f"""# Repository Engineering Instructions

Governance baseline: {args.governance_source}
Repository: {args.repository}
Official branch: {args.official_branch}
Status: DRAFT — VERIFY AGAINST LIVE REPOSITORY

- Reverify actual execution capabilities at the beginning of each session.
- Never mutate before live-state verification.
- Never claim repository, test, CI, runtime, or deployment work that was not actually executed.
- Never force-push or rewrite published history without explicit exceptional authority.
- Prefer one confirmed problem = one branch = one Pull Request.
- Prefer isolated worktrees when a real Git execution environment supports them.
- Use /ENGINEERING/MASTER_ROADMAP.md as the one canonical project roadmap.
- Store detailed reports under /ENGINEERING/REPORTS/.
- Store evidence indexes/metadata under /ENGINEERING/EVIDENCE/.
- Merge/release/tag/signing/deployment remain protected unless explicitly authorized.
"""

    environment = f"""# Engineering Environment Contract

Project: {args.project_name}
Status: DRAFT — VERIFY LIVE

## Available Execution Modes
## Environment Identity
## Toolchain
## Source Paths
## Data Separation
## Resource Policy
Minimum free disk before mutation:
## Runtime / Virtualization Gate
## Preflight Gate
## Retention
## Backup and Restore
## Health Checks
## Rebuild Procedure
"""

    resource_map = f"""# Project Sources / Resource Map

Project: {args.project_name}
Repository: {args.repository}
Status: DRAFT — VERIFY LIVE

## Source Repository
{args.repository}

## Repository Authority

## Project Baseline

## Master Engineering Baseline Report
/ENGINEERING/REPORTS/MASTER_ENGINEERING_BASELINE_REPORT.md

## Master Engineering Roadmap
/ENGINEERING/MASTER_ROADMAP.md

## Architecture / Engineering Guides

## Subsystem Contracts

## Engineering Lab / Environment Contract
governance/ENGINEERING_ENVIRONMENT_CONTRACT.md

## CI / Automation

## Runtime / Device / Production-Like Environments

## Evidence
/ENGINEERING/EVIDENCE/

## Reports
/ENGINEERING/REPORTS/

## Artifacts
"""

    adoption = f"""# Governance Adoption Status

Project: {args.project_name}
Repository: {args.repository}
Official branch: {args.official_branch}
Status: DRAFT_LIVE_VERIFICATION_REQUIRED

- [ ] Verify actual execution mode/capabilities.
- [ ] Complete read-only Master Re-baseline.
- [ ] Produce MASTER ENGINEERING BASELINE REPORT.
- [ ] Read existing /ENGINEERING/MASTER_ROADMAP.md if present.
- [ ] Establish or reconcile /ENGINEERING/MASTER_ROADMAP.md in an authorized mutation round.
- [ ] Verify repository authority, CI/tests, protection, secrets, lab, runtime matrix, evidence, and backups.
- [ ] Prove stop conditions fail closed.
- [ ] Complete one governed read-only task and one isolated implementation.
"""

    baseline = f"""# MASTER ENGINEERING BASELINE REPORT

Project: {args.project_name}
Repository: {args.repository}
Official branch: {args.official_branch}
Verified official HEAD: [VERIFY LIVE]
Verified execution mode: [VERIFY LIVE]
First-round mode: READ-ONLY

## A. PROJECT IDENTITY
## B. LIVE REPOSITORY STATE
## C. CURRENT CANONICAL SOURCE
## D. EXISTING REPOSITORY GOVERNANCE
## E. BUILD / RELEASE CONFIGURATION
## F. APPLICATION / SYSTEM ARCHITECTURE MAP
## G. AUTHORITATIVE STATE / OWNERSHIP MAP
## H. FEATURE / SUBSYSTEM INVENTORY
## I. PLATFORM / RUNTIME CONTRACT
## J. TEST INVENTORY
## K. CI / AUTOMATION INVENTORY
## L. SECURITY / PRIVACY BOUNDARIES
## M. CURRENT EVIDENCE COVERAGE
## N. RISK / GAP LEDGER
## O. PROPOSED REPOSITORY AUTHORITY MODEL
## P. PROPOSED PROJECT-SOURCES MODEL
## Q. PROPOSED MASTER ENGINEERING ROADMAP STATE FOR /ENGINEERING/MASTER_ROADMAP.md
## R. ENGINEERING LAB PLAN
## S. REQUIRED LAB TOOLCHAIN FOR THIS EXACT REPOSITORY
## T. CONTROLLER / EXECUTOR OPERATING MODEL
## U. EVIDENCE / REPORT STORAGE MODEL
## V. OWNER-PROTECTED DECISIONS
## W. EXACT NEXT ENGINEERING ROUND

This scaffold must be populated only from verified evidence.
The actual first-round baseline must remain read-only.
"""

    roadmap = f"""# Master Engineering Roadmap

Project: {args.project_name}
Repository: {args.repository}
Official branch: {args.official_branch}
Canonical path: /ENGINEERING/MASTER_ROADMAP.md
Status: DRAFT — LIVE VERIFICATION REQUIRED

## 1. Current Verified State
## 2. Architecture
## 3. Closed Historical Work
## 4. Current Findings
## 5. Release Blocker Map
## 6. Qualification Gaps
## 7. Ordered Engineering Gates
## 8. Runtime Gates
## 9. Release Gates
## 10. Owner Decisions
## 11. Deferred Post-Release Work
## 12. Exact Immediate Next Round
## Linked Reports
## Linked Evidence

Use FACT / INFERENCE / UNKNOWN / BLOCKED.
Do not create a competing roadmap elsewhere.
"""

    evidence_readme = """# Engineering Evidence

Canonical project evidence location: /ENGINEERING/EVIDENCE/

Store only safe evidence indexes/metadata and intentionally retained artifacts appropriate for version control.

Never commit credentials, tokens, private keys, signing material, production secrets, or sensitive raw dumps.

Associate evidence with the exact source SHA and link it from the relevant report and Master Roadmap.
"""

    content = {
        "governance/PROJECT_PROFILE.md": profile_md,
        "governance/project-profile.json": json.dumps(profile, indent=2, sort_keys=True) + "\n",
        "governance/REPOSITORY_ENGINEERING_INSTRUCTIONS.md": repository_rules,
        "governance/ENGINEERING_ENVIRONMENT_CONTRACT.md": environment,
        "governance/RESOURCE_MAP.md": resource_map,
        "governance/ADOPTION_STATUS.md": adoption,
        "ENGINEERING/REPORTS/MASTER_ENGINEERING_BASELINE_REPORT.md": baseline,
        "ENGINEERING/MASTER_ROADMAP.md": roadmap,
        "ENGINEERING/EVIDENCE/README.md": evidence_readme,
    }

    for relative_path, value in content.items():
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding="utf-8")

    print("BOOTSTRAP=PASS")
    print(f"project={args.project_name}")
    print(f"repository={args.repository}")
    print(f"official_branch={args.official_branch}")
    print(f"destination={destination.resolve()}")
    print("master_roadmap=ENGINEERING/MASTER_ROADMAP.md")
    print("reports=ENGINEERING/REPORTS/")
    print("evidence=ENGINEERING/EVIDENCE/")
    print("status=DRAFT_LIVE_VERIFICATION_REQUIRED")


if __name__ == "__main__":
    main()
