#!/usr/bin/env python3
"""Deterministic repository validation for the Master Engineering System."""
from __future__ import annotations
import json, py_compile, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "AGENTS.md","MASTER_GOVERNANCE.md","GLOBAL_REFERENCE.md","README.md","VERSION","CHANGELOG.md",
    "docs/MASTER_ENGINEERING_SYSTEM_READINESS.md","scripts/verify-system-readiness.py",
    "templates/MASTER_ENGINEERING_ROADMAP.md","templates/MASTER_ENGINEERING_BASELINE_REPORT.md",
    "templates/PROJECT_PROFILE.md","templates/TASK_PACKET.md","templates/RESULT_PACKET.md",
    "templates/EVIDENCE_MANIFEST.md","templates/REPOSITORY_ENGINEERING_INSTRUCTIONS.md",
    "templates/ENGINEERING_ENVIRONMENT_CONTRACT.md","templates/SUBSYSTEM_CONTRACT.md",
    "templates/RESOURCE_MAP.md","templates/ADOPTION_STATUS.md","templates/PROTECTED_ACTIONS.md",
    "checklists/PRE_TASK_CHECKLIST.md","checklists/PRE_MERGE_CHECKLIST.md",
    "checklists/CI_FAILURE_CHECKLIST.md","checklists/RELEASE_CHECKLIST.md",
    "schemas/project-profile.schema.json","schemas/task-packet.schema.json","schemas/result-packet.schema.json",
    "schemas/evidence-manifest.schema.json","examples/task-packet.example.json","examples/result-packet.example.json",
    "examples/evidence-manifest.example.json","examples/artifacts/evidence-fixture.txt",
    "scripts/verify-repository-state.sh","scripts/verify-clean-tree.sh","scripts/verify-environment-capacity.py",
    "scripts/verify-github-pr-state.py","scripts/bootstrap-project.py","scripts/collect-git-evidence.sh",
    "scripts/validate-task-packet.py","scripts/validate-result-packet.py","scripts/validate-evidence-manifest.py",
    "docs/AUTHORITY_MODEL.md","docs/CONTROLLER_EXECUTOR_MODEL.md","docs/EVIDENCE_POLICY.md",
    "docs/SECRETS_POLICY.md","docs/STOP_CONDITIONS.md","docs/ADOPTION_GUIDE.md","docs/QUICK_START.md",
    "docs/NEW_PROJECT_ADOPTION_PROMPT.md","docs/PULL_REQUEST_STATE_POLICY.md",
    "qualification/README.md","qualification/run-qualification.py",
]

def fail(message):
    print(f"FAIL: {message}", file=sys.stderr); raise SystemExit(1)

def run(command):
    c=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    if c.returncode: fail(f"command failed ({c.returncode}): {' '.join(command)}\nstdout:\n{c.stdout}\nstderr:\n{c.stderr}")

def main():
    missing=[p for p in REQUIRED_PATHS if not (ROOT/p).is_file()]
    if missing: fail("missing required paths: "+", ".join(missing))
    version=(ROOT/"VERSION").read_text().strip()
    if not re.fullmatch(r"(0|[1-9][0-9]*)[.](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:[+][0-9A-Za-z.-]+)?",version):
        fail(f"VERSION is not valid semantic versioning: {version!r}")
    for p in sorted(ROOT.rglob("*.json")):
        try: json.loads(p.read_text())
        except Exception as e: fail(f"invalid JSON in {p.relative_to(ROOT)}: {e}")
    for p in sorted((ROOT/"scripts").glob("*.sh")):
        run(["bash","-n",str(p.relative_to(ROOT))])
        if p.stat().st_mode & 0o111 == 0: fail(f"shell script is not executable: {p.relative_to(ROOT)}")
    for p in sorted((ROOT/"scripts").glob("*.py"))+sorted((ROOT/"qualification").glob("*.py")):
        try: py_compile.compile(str(p),doraise=True)
        except py_compile.PyCompileError as e: fail(f"Python syntax error in {p.relative_to(ROOT)}: {e.msg}")
    run([sys.executable,"scripts/validate-task-packet.py","examples/task-packet.example.json"])
    run([sys.executable,"scripts/validate-result-packet.py","examples/result-packet.example.json"])
    run([sys.executable,"scripts/validate-evidence-manifest.py","examples/evidence-manifest.example.json"])
    master=(ROOT/"MASTER_GOVERNANCE.md").read_text()
    for phrase in ["# MASTER ENGINEERING SYSTEM","## LIVE TRUTH","## MASTER ENGINEERING ROADMAP",
                   "## PERMANENT ENGINEERING LAB","## SOURCE VS RUNTIME EVIDENCE","## FIRST ROUND",
                   "MASTER PROJECT RE-BASELINE + ENGINEERING SYSTEM DISCOVERY",
                   "START THE READ-ONLY MASTER RE-BASELINE NOW."]:
        if phrase not in master: fail(f"MASTER_GOVERNANCE.md missing anchor phrase: {phrase}")
    if len(master.splitlines()) < 1000: fail("MASTER_GOVERNANCE.md appears truncated (<1000 lines)")
    expectations={
      "templates/TASK_PACKET.md":["## TASK TYPE","## AUTHORITY","## LIVE GATE","## STOP CONDITIONS","## SUCCESS CRITERIA"],
      "templates/RESULT_PACKET.md":["## Repository Identity","## Validation Actually Run","### Facts","### Inferences","### Unknowns","## Residual Risks"],
      "templates/EVIDENCE_MANIFEST.md":["SHA-256","size in bytes","sensitive-data flag"],
      "templates/ENGINEERING_ENVIRONMENT_CONTRACT.md":["## Preflight Gate","Minimum free disk before mutation:"],
      "templates/PROJECT_PROFILE.md":["PROJECT NAME:","REPOSITORY:","DEFAULT BRANCH:","OFFICIAL BRANCH:",
                                      "MASTER ROADMAP:","ENGINEERING LAB CONTRACT:","PROTECTED ACTIONS:",
                                      "TEST STRATEGY:","ARTIFACT LOCATION:","RELEASE MODEL:"],
      "templates/MASTER_ENGINEERING_ROADMAP.md":["## 1. Current Verified State","## 5. Release Blocker Map","## 12. Exact Immediate Next Round"],
      "templates/MASTER_ENGINEERING_BASELINE_REPORT.md":["## A. PROJECT IDENTITY","## N. RISK / GAP LEDGER","## W. EXACT NEXT ENGINEERING ROUND"],
    }
    for rel,anchors in expectations.items():
        content=(ROOT/rel).read_text()
        for a in anchors:
            if a not in content: fail(f"{rel} missing required anchor: {a}")
    tracked=subprocess.run(["git","ls-files"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.splitlines()
    bad=[p for p in tracked if p.startswith((".evidence/",".reports/",".tmp/")) or "__pycache__" in p or p.endswith(".pyc")]
    if bad: fail("forbidden generated/evidence files are tracked: "+", ".join(bad))
    print("PASS: Master Engineering System repository baseline is internally consistent")

if __name__=="__main__": main()
