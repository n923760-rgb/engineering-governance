# Repository Engineering Instructions

This file owns repository-specific execution rules. It may narrow authority but may not override the Master Engineering System or current owner instruction.

## Repository Identity
Repository:
Official branch:
Default development base:

## Execution Capability
Current verified execution mode:
Capabilities actually available:
Unavailable capabilities:
Last verified:

Rule: never claim repository, shell, test, CI, runtime, or deployment work that was not actually executed.

## Canonical Project Engineering Storage
Master Roadmap: /ENGINEERING/MASTER_ROADMAP.md
Reports: /ENGINEERING/REPORTS/
Evidence: /ENGINEERING/EVIDENCE/

Do not create a competing roadmap elsewhere in the same project.

## Branch Protection / Ruleset
Required protection:
Current verified protection:
Required checks:
Direct official-branch writes allowed: [YES/NO — VERIFY]

## Git Safety
- Never mutate source before Live Gate verification.
- Never force-push or rewrite published history unless explicitly authorized as a separate exceptional task.
- Never push directly to the official branch when project policy requires PR-based change control. Technical ability to bypass protection is not authorization.
- Prefer one confirmed problem = one branch = one pull request.
- Prefer isolated worktrees only when the actual execution environment supports them.

## Commit Policy
- Commit only completed bounded work.
- Review status, changed files, full diff, validation, accidental files, and secrets before the final task commit.
- In API-only execution, perform the closest equivalent repository-state and full-diff review and record unavailable shell checks.

## Pull Request Policy
- A PR is a review surface, not a development scratchpad.
- Open/update only when the implementation is reviewable.
- Merge requires explicit current owner authority.

## Testing and Evidence
Required local checks:
Required CI checks:
Required runtime evidence:
Evidence location: /ENGINEERING/EVIDENCE/
Report location: /ENGINEERING/REPORTS/

## First-Round Rule
The Master Project Re-baseline is strictly read-only. It may propose roadmap contents but must not create or update /ENGINEERING/MASTER_ROADMAP.md.

## Repository-Specific Stop Conditions

## Protected Paths

## Notes
