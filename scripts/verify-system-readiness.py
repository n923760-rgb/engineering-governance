#!/usr/bin/env python3
"""Fail-closed readiness gate for the current Master Engineering System source."""
from pathlib import Path
import re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def fail(m):
    print(f"NOT_READY: {m}",file=sys.stderr); raise SystemExit(1)

def main():
    version=(ROOT/"VERSION").read_text().strip()
    if not re.fullmatch(r"(0|[1-9][0-9]*)[.](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:[+][0-9A-Za-z.-]+)?",version):
        fail(f"invalid semantic VERSION: {version!r}")
    required=["AGENTS.md","MASTER_GOVERNANCE.md","templates/MASTER_ENGINEERING_BASELINE_REPORT.md",
              "templates/MASTER_ENGINEERING_ROADMAP.md","scripts/bootstrap-project.py",
              "scripts/verify-repository-state.sh","scripts/verify-github-pr-state.py",
              "scripts/verify-environment-capacity.py","scripts/validate-task-packet.py",
              "scripts/validate-result-packet.py","scripts/validate-evidence-manifest.py",
              "scripts/scan-secrets.py","qualification/run-qualification.py"]
    missing=[p for p in required if not (ROOT/p).is_file()]
    if missing: fail("missing capabilities: "+", ".join(missing))
    master=(ROOT/"MASTER_GOVERNANCE.md").read_text()
    for m in ["# MASTER ENGINEERING SYSTEM","## EXECUTION CAPABILITY DECLARATION",
              "## LIVE TRUTH","## MASTER ENGINEERING ROADMAP","/ENGINEERING/MASTER_ROADMAP.md",
              "## PERMANENT ENGINEERING LAB","## FIRST ROUND","START THE READ-ONLY MASTER RE-BASELINE NOW."]:
        if m not in master: fail(f"master missing marker: {m}")
    workflow=(ROOT/".github/workflows/governance-ci.yml").read_text()
    for m in ["Verify execution environment capacity","Validate repository contracts",
              "Scan tracked text for baseline secret patterns","Run governance stop-condition qualification",
              "Verify Master Engineering System readiness","Record source identity"]:
        if m not in workflow: fail(f"Governance CI missing step: {m}")
    h=subprocess.run([sys.executable,"scripts/bootstrap-project.py","--help"],cwd=ROOT,text=True,capture_output=True)
    if h.returncode: fail("project bootstrap is not runnable")
    b=(ROOT/"scripts/bootstrap-project.py").read_text()
    for m in ["AGENTS.md","ENGINEERING/MASTER_ROADMAP.md",
              "ENGINEERING/REPORTS/MASTER_ENGINEERING_BASELINE_REPORT.md",
              "ENGINEERING/EVIDENCE/","verified_execution_capabilities",
              "preserved_existing","DRAFT_LIVE_VERIFICATION_REQUIRED"]:
        if m not in b: fail(f"bootstrap missing marker: {m}")
    prompt=(ROOT/"docs/NEW_PROJECT_ADOPTION_PROMPT.md").read_text()
    for m in ["UNIVERSAL PROJECT START PROMPT (v2)","EXECUTION ENVIRONMENT — MANDATORY",
              "/ENGINEERING/MASTER_ROADMAP.md",
              "Do not modify the target repository during this first round."]:
        if m not in prompt: fail(f"Universal Project Start Prompt v2 missing marker: {m}")
    print("MASTER_ENGINEERING_SYSTEM_READINESS=PASS")
    print(f"version={version}")
    print("release_tag_created=no")
    print("github_release_created=no")

if __name__=="__main__": main()
