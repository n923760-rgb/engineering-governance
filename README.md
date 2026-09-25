# Master Engineering System

A reusable, project-agnostic engineering operating system for AI-assisted production software engineering.

This repository is the **central reference for all software projects**. It is not tied to any one product, framework, platform, repository, cloud provider, lab provider, or execution environment.

## Primary authority

- `MASTER_GOVERNANCE.md` — the Master Engineering System.
- `GLOBAL_REFERENCE.md` — compact navigation and adoption entry point.
- `AGENTS.md` — repository-specific instructions for maintaining this reference.
- `docs/ADOPTION_GUIDE.md` — adoption for new and existing projects.
- `docs/QUICK_START.md` — shortest safe adoption path.
- `docs/NEW_PROJECT_ADOPTION_PROMPT.md` — ready controller prompt.
- `templates/MASTER_ENGINEERING_ROADMAP.md` — one permanent roadmap per target project.
- `templates/MASTER_ENGINEERING_BASELINE_REPORT.md` — first-round read-only re-baseline report.

## Core operating rule

**Live repository truth → governance → one Master Roadmap → bounded task → isolated execution → validation → evidence → review → protected decision**

The target project's current repository and environment remain the source of truth. Historical chats, AI memory, old Pull Requests, archived SHAs, screenshots, copied configs, and another project's governance files are context only.

## First round for every adopted project

Start with a **READ-ONLY MASTER RE-BASELINE**.

Verify the live repository, architecture, source ownership, build/release model, tests, CI, security/privacy boundaries, runtime evidence, governance gaps, and engineering-lab requirements.

Do not mutate source during this first round.

The first formal output is a `MASTER ENGINEERING BASELINE REPORT`, followed by one maintained `MASTER ENGINEERING ROADMAP`.

## How every project uses this reference

1. Start with the read-only Master Re-baseline.
2. Derive project identity, official branch, live HEAD, repository authority, CI, toolchain, tests, runtime matrix, evidence locations, release model, and protected actions from live facts.
3. Run `scripts/bootstrap-project.py` or copy the relevant templates into the target project's `governance/` directory.
4. Replace placeholders using **that project's current live facts only**.
5. Establish one Master Engineering Roadmap.
6. Qualify the execution environment/lab that will execute work.
7. For each implementation task, issue one bounded Task Packet.
8. Prefer isolated branches/worktrees.
9. Validate with the smallest deterministic proof first, then affected regressions.
10. Produce attributable Result Packets and evidence.
11. Use runtime/physical/production-like environments only for claims that require them.
12. Perform protected actions only with explicit current owner authorization.

## Repository layout

- `MASTER_GOVERNANCE.md` — primary reusable engineering-system authority.
- `GLOBAL_REFERENCE.md` — reference map and usage contract.
- `AGENTS.md` — maintenance rules for this repository.
- `templates/` — project, roadmap, baseline report, task, result, environment, subsystem, evidence, adoption, and protected-action templates.
- `checklists/` — operational safety and review checklists.
- `schemas/` — machine-readable validation schemas.
- `scripts/` — bootstrap, live-state, PR-state, environment, evidence, and contract validation helpers.
- `docs/` — concise authority, secrets, evidence, stop-condition, PR-state, adoption, and readiness references.
- `examples/` — non-authoritative examples only.
- `qualification/` — adversarial tests that prove stop conditions fail closed.

## Bootstrap

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

The generated `governance/` directory is intentionally **DRAFT — LIVE VERIFICATION REQUIRED**. It is not automatically qualified.

## Never copy between projects

Do not copy repository SHAs, server identities, credentials, secret values, paths, CI identities, infrastructure details, test counts, production topology, backup destinations, runtime assumptions, or historical product decisions from another project.

## Protected actions

Protected actions normally require explicit current owner authorization. Typical examples include merge, release, tag, signing, store publication, production deployment, DNS changes, destructive database migration, production credential rotation, server/cloud destruction or reinstall, repository deletion, branch-history rewrite, permanent release-artifact deletion, and destructive billing/cloud-resource actions.

Technical access does not equal authorization.

## Validation vocabulary

`PASS` / `FAIL` / `BLOCKED` / `UNKNOWN` / `NOT RUN` / `SKIPPED`

## Release state

Stable published historical release: `v1.0.0`.

The `v1.0.0` tag and GitHub Release are immutable evidence. Current `main` may contain unreleased evolution of the Master Engineering System. A future release requires a separate explicit owner decision and exact-source qualification.
