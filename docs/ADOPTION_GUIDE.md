# Adopting the Master Engineering System

## New adoption or material re-baseline

1. Verify actual execution capabilities and live target repository/PR state.
2. Read applicable target instructions and project contracts.
3. Inspect current central reference and docs/AUTHORITY_MODEL.md.
4. Perform the read-only Master Re-baseline and use the baseline-report template.
5. Read the existing canonical roadmap after source verification; propose missing
   or changed state without writing it in the read-only round.
6. In an authorized governance-mutation round, run bootstrap, preserve existing
   AGENTS.md, record the adopted reference and risk profile, and reconcile project files.
7. Fill unknown values from actual project facts and qualify applicable environment,
   CI/protection, secrets, runtime, evidence, and backup/restore requirements.
8. Exercise a bounded read-only workflow and an isolated implementation workflow.
   Qualify actual executor tool boundaries separately from JSON fixture tests.

```bash
python -m pip install -r requirements.txt
python scripts/bootstrap-project.py --project-name "Example Project" \
  --repository "owner/example-project" --official-branch main \
  --risk-profile STANDARD --destination /path/to/example-project
```

Generated files are DRAFT — LIVE VERIFICATION REQUIRED. The bootstrap creates
root AGENTS.md automatically only when absent and preserves an existing file
exactly. The lock captures actual reference hashes; dirty/non-Git source cannot
claim a clean source commit.

## Existing adopted projects

Read governance/GOVERNANCE_LOCK.json and the existing
/ENGINEERING/MASTER_ROADMAP.md. Use the session-delta flow in docs/RISK_PROFILES.md.
Preserve working architecture and authoritative project documents.

Review central policy updates before adopting them. Update the same lock and
project authority through an authorized bounded change, retaining previous
adoption evidence. Never create a competing roadmap.

## Qualification

QUALIFIED requires the applicable combination of verified identity/source,
authority, canonical roadmap, tests/CI/protection, execution environment, secret
boundaries, evidence, recovery, and first governed workflows.

A passing source-lock or fixture test does not qualify the product or an AI
executor. Missing settings access, physical devices, or external services remain
accurately classified. Do not block unrelated authorized work unnecessarily.
