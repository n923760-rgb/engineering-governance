# Engineering Governance System

Reusable governance framework for AI-assisted software engineering across multiple projects.

## Core rule

Current Problem → Current Source → Isolated Change → Evidence → Review → Merge Decision

The repository or project currently being worked on remains the source of truth. Historical chats, AI memory, old pull requests, archived SHAs, screenshots, and planning documents are context only.

## How to use this repository

1. Keep `MASTER_GOVERNANCE.md` generic and stable.
2. For each project, create a project-specific `PROJECT_GOVERNANCE_PROFILE.md` from `templates/PROJECT_PROFILE.md`.
3. Before implementation, issue one bounded `TASK_PACKET.md`.
4. Run the Live Gate before source mutation.
5. Execute the task in an isolated branch/worktree.
6. Record tests and evidence honestly.
7. Produce a `RESULT_PACKET.md`.
8. Review the result before any protected action such as merge, release, deployment, destructive migration, or history rewrite.

## Repository layout

- `MASTER_GOVERNANCE.md` — reusable governance authority.
- `templates/` — project, task, result, repository, environment, subsystem, and resource-map templates.
- `checklists/` — operational safety and review checklists.
- `schemas/` — machine-readable validation schemas.
- `scripts/` — Live Gate and packet validation helpers.
- `docs/` — concise role and policy references.
- `examples/` — example project profile and task/result flow.

## First adoption workflow

Copy the following into the target project or reference them from its own engineering instructions:

- `templates/PROJECT_PROFILE.md`
- `templates/REPOSITORY_ENGINEERING_INSTRUCTIONS.md`
- `templates/ENGINEERING_ENVIRONMENT_CONTRACT.md`
- `templates/RESOURCE_MAP.md`

Then fill them from the target project's current live environment. Never copy repository names, SHAs, credentials, paths, CI details, or infrastructure identities from another project.

## Version

Initial implementation baseline: `0.1.0`.