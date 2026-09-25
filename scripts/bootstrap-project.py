#!/usr/bin/env python3
"""Create a safe starter pack for the Master Engineering System."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
REPOSITORY_RE=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH_RE=re.compile(r"^[A-Za-z0-9._/-]+$")
FILES=("PROJECT_PROFILE.md","project-profile.json","REPOSITORY_ENGINEERING_INSTRUCTIONS.md",
       "ENGINEERING_ENVIRONMENT_CONTRACT.md","RESOURCE_MAP.md","ADOPTION_STATUS.md",
       "MASTER_ENGINEERING_BASELINE_REPORT.md","MASTER_ENGINEERING_ROADMAP.md")

def fail(m,c=1): print(f"STOP: {m}",file=sys.stderr); raise SystemExit(c)
def validate(n,r,b):
    if not n.strip(): fail("project name must be non-empty",2)
    if not REPOSITORY_RE.fullmatch(r): fail("repository must use owner/name form",2)
    if not BRANCH_RE.fullmatch(b) or b.startswith("/") or b.endswith("/"): fail("invalid official branch",2)

def main():
    p=argparse.ArgumentParser(description="Bootstrap the Master Engineering System for a project.")
    p.add_argument("--project-name",required=True); p.add_argument("--repository",required=True)
    p.add_argument("--official-branch",default="main"); p.add_argument("--destination",required=True)
    p.add_argument("--governance-source",default="engineering-governance/MASTER_GOVERNANCE.md")
    a=p.parse_args(); validate(a.project_name,a.repository,a.official_branch)
    root=Path(a.destination)/"governance"
    collisions=[root/n for n in FILES if (root/n).exists()]
    if collisions: fail("refusing to overwrite existing governance files: "+", ".join(map(str,collisions)),20)
    root.mkdir(parents=True,exist_ok=True)

    md=f"""# Project Governance Profile

Status: DRAFT — LIVE VERIFICATION REQUIRED
Governance baseline: {a.governance_source}

## Project Identity
PROJECT NAME: {a.project_name}
REPOSITORY: {a.repository}
REPOSITORY URL: [VERIFY LIVE]
DEFAULT BRANCH: [VERIFY LIVE]
OFFICIAL BRANCH: {a.official_branch}

## Governing Instructions
REPOSITORY AUTHORITY FILE: [VERIFY OR CREATE]
PROJECT BASELINE: [VERIFY]
ARCHITECTURE GUIDES: [VERIFY]
SUBSYSTEM CONTRACTS: [VERIFY]

## Engineering Systems
MASTER ROADMAP: governance/MASTER_ENGINEERING_ROADMAP.md
MASTER BASELINE REPORT: governance/MASTER_ENGINEERING_BASELINE_REPORT.md
CI SYSTEM: [VERIFY LIVE]
ENGINEERING LAB CONTRACT: governance/ENGINEERING_ENVIRONMENT_CONTRACT.md
EXECUTION ENVIRONMENT: [VERIFY LIVE]
CONTROLLER: Engineering Controller
EXECUTOR: Engineering Executor

## Protected Actions
PROTECTED ACTIONS: [DERIVE AND VERIFY]

## Verification and Evidence
TEST STRATEGY: [DERIVE]
EVIDENCE LOCATION: .evidence/
REPORT LOCATION: .reports/
ARTIFACT LOCATION: [VERIFY]
BACKUP / RESTORE STRATEGY: [VERIFY]
RELEASE MODEL: [VERIFY]
RUNTIME / DEVICE / PLATFORM MATRIX: [DERIVE]

## Notes
Live repository truth overrides historical context.
"""
    profile={"status":"DRAFT_LIVE_VERIFICATION_REQUIRED","governance_source":a.governance_source,
      "project_name":a.project_name,"repository":a.repository,"repository_url":None,"default_branch":None,
      "official_branch":a.official_branch,"repository_authority_file":None,"project_baseline":None,
      "architecture_guides":[],"subsystem_contracts":[],"master_roadmap":"governance/MASTER_ENGINEERING_ROADMAP.md",
      "master_baseline_report":"governance/MASTER_ENGINEERING_BASELINE_REPORT.md","ci_system":None,
      "engineering_lab_contract":"governance/ENGINEERING_ENVIRONMENT_CONTRACT.md","execution_environment":None,
      "controller":"Engineering Controller","executor":"Engineering Executor",
      "protected_actions":["merge","release","tag","signing","store_publication","production_deploy","dns_changes",
        "destructive_database_migration","production_credential_rotation","server_or_cloud_destruction_or_reinstall",
        "repository_deletion","force_push","history_rewrite","permanent_release_artifact_deletion",
        "destructive_billing_or_cloud_resource_actions"],
      "test_strategy":"VERIFY_FROM_CURRENT_PROJECT","evidence_location":".evidence/","report_location":".reports/",
      "artifact_location":None,"backup_restore_strategy":None,"release_model":None,"runtime_device_platform_matrix":[]}

    repo_rules=f"""# Repository Engineering Instructions
Governance baseline: {a.governance_source}
Repository: {a.repository}
Official branch: {a.official_branch}
Status: DRAFT — VERIFY AGAINST LIVE REPOSITORY

- Never mutate before live-state verification.
- Never force-push or rewrite published history without explicit exceptional authority.
- Prefer one confirmed problem = one branch = one Pull Request.
- Prefer isolated worktrees.
- Merge/release/tag/signing/deployment remain protected unless explicitly authorized.
"""
    env=f"""# Engineering Environment Contract
Project: {a.project_name}
Status: DRAFT — VERIFY LIVE

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
    resource=f"""# Project Sources / Resource Map
Project: {a.project_name}
Repository: {a.repository}
Status: DRAFT — VERIFY LIVE

## Source Repository
{a.repository}
## Repository Authority
## Project Baseline
## Master Engineering Baseline Report
governance/MASTER_ENGINEERING_BASELINE_REPORT.md
## Master Engineering Roadmap
governance/MASTER_ENGINEERING_ROADMAP.md
## Architecture / Engineering Guides
## Subsystem Contracts
## Engineering Lab / Environment Contract
governance/ENGINEERING_ENVIRONMENT_CONTRACT.md
## CI / Automation
## Runtime / Device / Production-Like Environments
## Evidence
.evidence/
## Reports
.reports/
## Artifacts
"""
    adoption=f"""# Governance Adoption Status
Project: {a.project_name}
Repository: {a.repository}
Official branch: {a.official_branch}
Status: DRAFT_LIVE_VERIFICATION_REQUIRED

- [ ] Complete read-only Master Re-baseline.
- [ ] Produce MASTER ENGINEERING BASELINE REPORT.
- [ ] Establish one MASTER ENGINEERING ROADMAP.
- [ ] Verify repository authority, CI/tests, protection, secrets, lab, runtime matrix, evidence, and backups.
- [ ] Prove stop conditions fail closed.
- [ ] Complete one governed read-only task and one isolated implementation.
"""
    baseline=f"""# MASTER ENGINEERING BASELINE REPORT
Project: {a.project_name}
Repository: {a.repository}
Official branch: {a.official_branch}
Verified official HEAD: [VERIFY LIVE]
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
## Q. MASTER ENGINEERING ROADMAP STRUCTURE
## R. ENGINEERING LAB PLAN
## S. REQUIRED LAB TOOLCHAIN FOR THIS EXACT REPOSITORY
## T. CONTROLLER / EXECUTOR OPERATING MODEL
## U. EVIDENCE / REPORT STORAGE MODEL
## V. OWNER-PROTECTED DECISIONS
## W. EXACT NEXT ENGINEERING ROUND
"""
    roadmap=f"""# Master Engineering Roadmap
Project: {a.project_name}
Repository: {a.repository}
Official branch: {a.official_branch}
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

Use FACT / INFERENCE / UNKNOWN / BLOCKED.
"""
    content={"PROJECT_PROFILE.md":md,"project-profile.json":json.dumps(profile,indent=2,sort_keys=True)+"\n",
      "REPOSITORY_ENGINEERING_INSTRUCTIONS.md":repo_rules,"ENGINEERING_ENVIRONMENT_CONTRACT.md":env,
      "RESOURCE_MAP.md":resource,"ADOPTION_STATUS.md":adoption,
      "MASTER_ENGINEERING_BASELINE_REPORT.md":baseline,"MASTER_ENGINEERING_ROADMAP.md":roadmap}
    for n,v in content.items(): (root/n).write_text(v,encoding="utf-8")
    print("BOOTSTRAP=PASS"); print(f"project={a.project_name}"); print(f"repository={a.repository}")
    print(f"official_branch={a.official_branch}"); print(f"governance_dir={root.resolve()}")
    print("status=DRAFT_LIVE_VERIFICATION_REQUIRED")

if __name__=="__main__": main()
