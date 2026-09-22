# Repository Engineering Instructions

This file owns repository-specific execution rules. It may narrow authority but may not override the Master Governance or current owner instruction.

## Repository Identity
Repository:
Official branch:
Default development base:

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
- Prefer isolated worktrees for concurrent work.

## Commit Policy
- Commit only completed bounded work.
- Review status, changed files, full diff, validation, accidental files, and secrets before the final task commit.

## Pull Request Policy
- A PR is a review surface, not a development scratchpad.
- Open/update only when the implementation is reviewable.
- Merge requires explicit project authority.

## Testing and Evidence
Required local checks:
Required CI checks:
Required runtime evidence:
Evidence location:

## Repository-Specific Stop Conditions

## Protected Paths

## Notes
