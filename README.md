# Engineering Governance System

Reusable governance framework for AI-assisted software engineering across multiple projects.

## Core rule

Current Problem → Current Source → Isolated Change → Evidence → Review → Merge Decision

The repository or project currently being worked on remains the source of truth. Historical chats, AI memory, old pull requests, archived SHAs, screenshots, and planning documents are context only.

## How to use this repository

1. Keep `MASTER_GOVERNANCE.md` generic and stable.
2. For each project, run `scripts/bootstrap-project.py` to create a safe DRAFT governance starter pack.
3. Qualify that starter pack against the target project's live source, CI, environment, and instructions.
4. Before implementation, issue one bounded `TASK_PACKET.md`.
5. Run the Live Gate and environment gate before source mutation.
6. Execute the task in an isolated branch/worktree.
7. Record tests and evidence honestly.
8. Produce a `RESULT_PACKET.md` and Evidence Manifest where file artifacts matter.
9. Review the result before any protected action such as merge, release, deployment, destructive migration, or history rewrite.

## Repository layout

- `MASTER_GOVERNANCE.md` — reusable governance authority.
- `templates/` — project, task, result, repository, environment, subsystem, and resource-map templates.
- `checklists/` — operational safety and review checklists.
- `schemas/` — machine-readable validation schemas.
- `scripts/` — Live Gate and packet validation helpers.
- `docs/` — concise role, policy, and project-adoption references.
- `examples/` — example project profile, task/result flow, and evidence manifest.
- `qualification/` — adversarial tests that prove stop conditions fail closed.
- `docs/V1_READINESS.md` — formal scope of the qualified v1 baseline.

## First adoption workflow

Bootstrap the target project:

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

The generated `governance/` directory is deliberately marked **DRAFT — LIVE VERIFICATION REQUIRED**. Follow `docs/ADOPTION_GUIDE.md` and fill it from the target project's current live environment. Never copy SHAs, credentials, paths, CI details, or infrastructure identities from another project.

## Version

Current source version: `1.0.0`.

The `v1.0.0` tag and GitHub Release must point to the exact `main` SHA that passes Governance CI after this version is merged.
