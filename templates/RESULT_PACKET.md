# Engineering Task Result

## Task Identity
Task ID:
Task type:
Task packet reference:
Executor:
Execution environment:
Started:
Completed:

## Repository Identity
Repository:
Official branch:
Verified remote official HEAD:
Work branch/worktree:
Exact tested HEAD:
PR:
Git status before:
Git status after:

## Authority
Authorized actions:
Actions actually performed:

Rule: every action actually performed must be a subset of Authorized actions.

## Scope
Completed:
Observed but intentionally left out of scope:

## Commands Actually Run
Command:
Exit code:
Result:
Evidence path:

## Validation Actually Run
For each check record:
- Check:
- Result: PASS / FAIL / BLOCKED / SKIPPED / NOT RUN
- Evidence:
- Reason: required for BLOCKED / SKIPPED / NOT RUN

Rules:
- PASS, FAIL, and BLOCKED require attributable evidence.
- BLOCKED, SKIPPED, and NOT RUN require a reason.
- NOT RUN must never be reported as PASS.

## Findings

### Facts

### Inferences

### Assumptions

## Changes
Files changed:
Purpose:
Diff summary:
Commit:
Push:
PR:

## Artifacts
Path:
SHA-256:
Size:
Sensitive data: yes/no

## Failure Analysis
First causal failure:
Secondary failures:
Stop condition reached:

## Residual Risks

## Recommended Next Action
One smallest next engineering action.
