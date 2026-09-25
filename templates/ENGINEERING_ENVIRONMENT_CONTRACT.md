# Engineering Environment Contract

## Available Execution Modes
Verified current mode:
Verification method:
CLI/Git available:
Repository API/MCP available:
CI/CD available:
Runtime/device access available:
Advisory-only limitations:
Last verified:

Do not infer an unavailable capability from a prompt declaration.

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
Project roadmap: /ENGINEERING/MASTER_ROADMAP.md
Evidence root: /ENGINEERING/EVIDENCE/
Reports root: /ENGINEERING/REPORTS/
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
Before mutation, run the environment preflight appropriate to this environment when that capability actually exists.

Baseline command for a shell-capable environment:

```bash
python scripts/verify-environment-capacity.py --path <working-path> --min-free-bytes <required-bytes>
```

For strictly read-only work, a project may explicitly permit `--skip-write-test`.

If shell execution is unavailable, do not pretend this command ran. Record it as NOT RUN/BLOCKED and use only the checks genuinely available through the current execution mode.

A failed capacity or write check is a STOP condition, not permission to continue partially.

## Runtime / Virtualization Gate

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
