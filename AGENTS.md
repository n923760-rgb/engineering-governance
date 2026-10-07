# Engineering Governance Repository Instructions

This repository is the central, project-agnostic reference for the Master Engineering System defined in `MASTER_GOVERNANCE.md`.

Use the instruction hierarchy in `docs/AUTHORITY_MODEL.md`.
This AGENTS.md owns repository-local maintenance safety. Scoped contracts refine
their own area without widening owner permission or silently weakening these rules.
Active owner authorization persists within its recorded scope and conditions.

Before mutation, verify repository identity, official branch, live official HEAD, open/conflicting Pull Requests, applicable instructions, and exact task scope.

Repository rules:

- use one confirmed problem or one coherent governance change per branch and Pull Request;
- do not push ordinary changes directly to `main`;
- do not force-push or rewrite published history;
- do not move or recreate published release tags;
- treat merge, tag, release, signing, and destructive repository actions as protected;
- review the full diff and require Governance CI before merge;
- never weaken a safety gate merely to obtain a green build;
- update validators when the governing contract intentionally changes;
- keep target-project facts out of this central reference;
- never commit credentials, tokens, signing material, private keys, recovery codes, or production secrets.

The published `v1.0.0` release is immutable historical evidence.

Validation results must be reported truthfully as `PASS`, `FAIL`, `BLOCKED`, `UNKNOWN`, `NOT RUN`, or `SKIPPED`.
