# Global Engineering Governance Reference

A reusable, project-agnostic governance system for AI-assisted software engineering.

This repository is the **central reference for all software projects**. It is not tied to TYFINO or any other product, framework, platform, repository, cloud provider, or execution environment.

## Primary authority

- `MASTER_GOVERNANCE.md` — global governance authority.
- `GLOBAL_REFERENCE.md` — compact navigation and adoption entry point.
- `docs/ADOPTION_GUIDE.md` — adoption for new and existing projects.
- `docs/QUICK_START.md` — shortest safe adoption path.
- `docs/NEW_PROJECT_ADOPTION_PROMPT.md` — ready controller prompt.

## Core rule

Current Problem → Current Source → Isolated Change → Evidence → Review → Merge Decision

The target project's current repository and environment remain the source of truth. Historical chats, AI memory, old pull requests, archived SHAs, screenshots, copied configs, and another project's governance files are context only.

## How every project uses this reference

1. Start with a read-only Live Truth Gate.
2. Identify the target repository, official branch, current remote HEAD, instructions, CI, execution environment, branch protection/rulesets, secret scanning, tests, evidence/report locations, and backup/restore policy.
3. Run `scripts/bootstrap-project.py` or copy the relevant templates into the target project's `governance/` directory.
4. Replace placeholders using **that project's current live facts only**.
5. Run governance qualification before normal production engineering.
6. For each engineering task, issue one bounded `TASK_PACKET.md`.
7. Work in an isolated branch/worktree.
8. Validate with the smallest deterministic proof first, then relevant regressions.
9. Produce a `RESULT_PACKET.md` and attributable evidence.
10. Perform protected actions only with explicit current owner authorization.

## Repository layout

- `MASTER_GOVERNANCE.md` — global reusable governance authority.
- `GLOBAL_REFERENCE.md` — reference map and usage contract.
- `templates/` — project, repository, task, result, environment, subsystem, evidence, adoption, and protected-action templates.
- `checklists/` — operational safety and review checklists.
- `schemas/` — machine-readable validation schemas.
- `scripts/` — bootstrap, Live Gate, PR-state, environment, evidence, and packet validation helpers.
- `docs/` — concise authority, secrets, evidence, stop-condition, PR-state, and adoption references.
- `examples/` — non-authoritative examples only.
- `qualification/` — adversarial tests that prove stop conditions fail closed.
- `docs/V1_READINESS.md` — scope of the qualified v1 baseline.

## Bootstrap

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

The generated `governance/` directory is intentionally **DRAFT — LIVE VERIFICATION REQUIRED**. It must never be treated as automatically qualified.

## Never copy between projects

Do not copy repository SHAs, server identities, credentials, secret values, paths, CI identities, infrastructure details, test counts, production topology, backup destinations, or historical product decisions from another project.

Derive them from the target project's own current environment.

## Protected actions

Protected actions normally require explicit current owner authorization. Typical examples include merge, release, tag, signing, production deployment, destructive database migration, production credential rotation, server destruction/reinstall, repository deletion, branch history rewrite, permanent artifact deletion, and billing/cloud-resource destruction.

Technical access does not equal authorization.

## Validation vocabulary

Use only accurate states: `PASS`, `FAIL`, `BLOCKED`, `SKIPPED`, `NOT RUN`.

`BLOCKED` is not `PASS`. `NOT RUN` must remain visible.

## Release state

Stable published release: `v1.0.0`.

The published `v1.0.0` tag and GitHub Release are immutable historical release evidence. Changes merged to `main` after that release are **unreleased** until a future version is explicitly authorized, qualified, and published.
