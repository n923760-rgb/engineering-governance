# Master Engineering System

A reusable, project-agnostic engineering operating system for AI-assisted production software engineering.

This repository is the **central reference for all software projects**. It is not tied to any one product, framework, platform, repository, cloud provider, lab provider, or execution environment.

## Primary authority

- `MASTER_GOVERNANCE.md` — the Master Engineering System.
- `GLOBAL_REFERENCE.md` — compact navigation and adoption entry point.
- `AGENTS.md` — repository-specific instructions for maintaining this reference.
- `docs/NEW_PROJECT_ADOPTION_PROMPT.md` — **Universal Project Start Prompt v2**, the ready-to-use project entry prompt.
- `docs/ADOPTION_GUIDE.md` — adoption for new and existing projects.
- `docs/QUICK_START.md` — shortest safe adoption path.
- `templates/MASTER_ENGINEERING_ROADMAP.md` — canonical roadmap template.
- `templates/MASTER_ENGINEERING_BASELINE_REPORT.md` — first-round read-only re-baseline report.

## Core operating rule

**Live repository truth → governance → one Master Roadmap → bounded task → isolated execution → validation → evidence → review → protected decision**

The target project's current repository and environment remain the source of truth. Historical chats, AI memory, old Pull Requests, archived SHAs, screenshots, copied configs, and another project's governance files are context only.

## Execution capability first

Every session must verify what it can actually do before claiming repository access or execution.

Typical modes include a real Git/CLI environment, a repository API/MCP connector, external CI, a qualified engineering lab, or advisory-only chat.

Unavailable actions are reported as `BLOCKED`, `NOT RUN`, or `UNKNOWN`; they are never simulated.

## First round for every adopted project

Start with a **READ-ONLY MASTER RE-BASELINE**.

Verify live repository state, architecture, source ownership, build/release model, tests, CI, security/privacy boundaries, runtime evidence, governance gaps, engineering-lab requirements, and any existing canonical roadmap.

Do not mutate source or create/update the roadmap during this first round.

The first formal output is a `MASTER ENGINEERING BASELINE REPORT`, including a proposed roadmap state.

## Canonical target-project engineering storage

Every adopted target project uses one fixed convention:

- `/ENGINEERING/MASTER_ROADMAP.md` — single permanent project roadmap.
- `/ENGINEERING/REPORTS/` — detailed engineering reports.
- `/ENGINEERING/EVIDENCE/` — evidence indexes/metadata and retained evidence as appropriate.

The central governance repository owns reusable rules. The target repository owns its project-specific roadmap and evidence history.

## How every project uses this reference

1. Verify the actual execution mode for the current session.
2. Start with the read-only Master Re-baseline.
3. Derive project identity, branch, live HEAD, authority, CI, toolchain, tests, runtime matrix, release model, and protected actions from live facts.
4. Read `/ENGINEERING/MASTER_ROADMAP.md` if it already exists.
5. Produce the Baseline Report and propose the roadmap state without writing during the read-only round.
6. In a later explicitly authorized governance-mutation round, bootstrap or establish the project governance files and canonical `ENGINEERING/` structure.
7. Qualify the execution environment/lab that will execute work.
8. For each implementation task, issue one bounded Task Packet.
9. Prefer isolated branches/worktrees when the actual execution mode supports them.
10. Validate with the smallest deterministic proof first, then affected regressions.
11. Produce attributable Result Packets, reports, and evidence.
12. Perform protected actions only with explicit current owner authorization.

## Bootstrap

Run the bootstrap only after the read-only baseline when repository mutation is explicitly authorized:

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

The generated governance and `ENGINEERING/` files are **DRAFT — LIVE VERIFICATION REQUIRED**. Scaffolding is not proof.

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
