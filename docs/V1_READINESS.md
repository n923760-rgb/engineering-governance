# v1.0 Readiness

Status: **QUALIFIED STABLE SOURCE BASELINE**
Source version: **1.0.0**

This document records what the reusable governance system proves before and after formal release metadata is created.

## Qualified Baseline

The automated qualification suite covers:

- repository identity, official branch, clean worktree, and official HEAD;
- pull-request repository, state, head SHA, base branch, and conflicting-open-PR detection;
- Task Packet requested/authorized/protected action boundaries;
- explicit current-owner authorization for protected actions;
- Result Packet validation with PASS/FAIL/BLOCKED evidence requirements;
- reasons for BLOCKED/SKIPPED/NOT RUN;
- Evidence Manifest path, size, SHA-256, timestamp, source SHA, and environment identity;
- baseline secret-pattern scanning;
- execution-environment path, free-disk, and write preflight;
- safe project bootstrap that refuses overwrite and never auto-qualifies a target project;
- CI execution of environment preflight, repository validation, secret scan, adversarial qualification, v1 readiness, and exact source identity recording.

## Reusable Adoption Contract

A new project can be bootstrapped with:

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

The output remains **DRAFT — LIVE VERIFICATION REQUIRED** until the target project's real source, CI, tests, environment, secrets, backup strategy, and protected paths are verified.

## What v1 Does Not Pretend to Know

The reusable system does not invent or centrally hard-code:

- a target project's current SHA;
- production credentials or secret values;
- production server paths;
- project-specific CI requirements;
- project-specific runtime tests;
- production topology;
- backup destinations;
- migration procedures;
- subsystem-specific contracts.

Those remain project-level facts and must be derived from the live target project.

## Stable Release Boundary

`v1.0.0` has been formally published from its qualified exact `main` SHA.

The published tag and GitHub Release are immutable release evidence. They must not be moved to newer commits.

Post-release changes on `main` are unreleased until a future version is explicitly authorized, qualified, and published.
