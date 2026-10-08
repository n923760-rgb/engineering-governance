# Master Engineering System

A reusable, project-agnostic operating system for AI-assisted production engineering.

## Start here

- MASTER_GOVERNANCE.md — primary policies.
- docs/AUTHORITY_MODEL.md — instruction precedence, facts, and approved inputs.
- docs/NEW_PROJECT_ADOPTION_PROMPT.md — Universal Project Start Prompt v3.
- docs/QUICK_START.md and docs/ADOPTION_GUIDE.md — adoption and continuation.
- docs/RISK_PROFILES.md — LIGHT / STANDARD / HIGH and scoped blockers.
- docs/GOVERNANCE_VERSIONING.md — adopted source/version tracking.
- docs/UNTRUSTED_CONTENT_POLICY.md — external content and agent boundaries.

The live target repository establishes product facts. Owner instructions and
project contracts define intended behavior and authority. Historical memory is context.

## Reference-only scope

This repository is the general master reference, not a project orchestrator.
Maintaining it does not select, bootstrap, or change any target repository.
Adopt it later within an explicitly identified project's authorized task, using
that project's live source and native instructions. Do not infer adoption authority
from a repository remembered in history or from access to a connected account.

For a concise handoff to a project's conversation, use docs/QUICK_START.md and
docs/NEW_PROJECT_ADOPTION_PROMPT.md. Source readiness, project adoption, executor
qualification and stable release are separate decisions; none implies the others.

## Development state

VERSION is the current development version. 2.0.0-dev.1 is an unreleased evolution
with incompatible validator/packet contracts. Published v1.0.0 remains immutable
historical evidence. No development update creates a release or tag.

## Adopt or continue

First adoption or a material re-baseline starts read-only and uses
templates/MASTER_ENGINEERING_BASELINE_REPORT.md. Propose roadmap state without
writing target files in that round. Ordinary sessions use the existing roadmap
and a scoped delta.

During authorized bootstrap:

```bash
python -m pip install -r requirements.txt
python scripts/bootstrap-project.py \
  --project-name "Example Project" --repository "owner/example-project" \
  --official-branch main --risk-profile STANDARD --destination /path/to/example-project
```

The bootstrap creates AGENTS.md from templates/PROJECT_AGENTS.md when none exists,
preserves existing AGENTS.md exactly, and creates draft project profile/environment
records and governance/GOVERNANCE_LOCK.json. It does not qualify a project.

Target projects retain one /ENGINEERING/MASTER_ROADMAP.md, detailed reports in
/ENGINEERING/REPORTS/, and evidence metadata in /ENGINEERING/EVIDENCE/.

Record the reference source and hashes. Review newer central changes before
adopting them; central main must not silently replace an existing project's policy.

## Validate contracts

Python 3.12 is the qualified CI toolchain. Install the pinned requirements first.

```bash
python scripts/validate-repository.py
python qualification/run-qualification.py
python scripts/verify-system-readiness.py
python scripts/validate-task-packet.py examples/task-packet.example.json
python scripts/validate-result-packet.py examples/result-packet.example.json \
  --task examples/task-packet.example.json \
  --evidence-manifest examples/evidence-manifest.example.json
```

The controller supplies approved task/evidence paths independently. Results bind
to task hashes and manifest task/source/environment identity. PASS/FAIL cites
verified retained bytes. UNKNOWN requires a reason and never becomes PASS.

Validators check contracts and file integrity; they do not authenticate owners,
sandbox executors, or establish that a command was honestly run. Tool permissions,
trusted issuance, live attribution, and review remain necessary.

## Safety and autonomy

Use one bounded problem/coherent change per branch and PR. Keep protected actions
within explicit active owner authorization, including standing authorization that
still meets its scope and conditions. Technical access is not authorization.

Never expose secrets, rewrite shared history for convenience, move published
release tags, or use missing verification as success. Stop the dependent action
when a real boundary is unresolved; continue independent authorized work.
