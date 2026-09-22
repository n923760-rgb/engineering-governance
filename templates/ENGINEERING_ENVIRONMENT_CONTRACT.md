# Engineering Environment Contract

## Environment Identity
Name:
Purpose:
Owner:

## Toolchain
OS:
Git:
Runtime(s):
SDK(s):
Build tools:
Container tooling:

## Source Paths
Canonical clone:
Worktrees root:

## Data Separation
Evidence root:
Reports root:
Artifacts root:
Caches root:
Temporary runs root:
Machine configuration root:
Secrets mechanism:

## Resource Policy
CPU limits:
Memory limits:
Storage limits:
Minimum free disk before mutation:
Heavy-workload lock:

## Preflight Gate
Before mutation, run the environment preflight appropriate to this environment.

Baseline command:

```bash
python scripts/verify-environment-capacity.py --path <working-path> --min-free-bytes <required-bytes>
```

For strictly read-only work, a project may explicitly permit `--skip-write-test`.

A failed capacity or write check is a STOP condition, not permission to continue partially.

## Retention
Evidence:
Reports:
Artifacts:
Caches:
Temporary runs:

## Backup and Restore
Backup target:
Backup cadence:
Restore test procedure:
Last successful restore test:

## Health Checks

## Rebuild Procedure
