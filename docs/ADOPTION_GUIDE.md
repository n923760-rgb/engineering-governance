# Adopting Global Engineering Governance in Any Project

This repository is a reusable control system. A target project must derive its own facts from its current source and environment.

## 1. Start Read-Only

Before creating governance files or changing source, inspect:
- repository identity;
- official branch;
- current official remote HEAD;
- repository/project instructions;
- relevant subsystem contracts;
- open/conflicting PRs;
- CI and required checks;
- branch protection/rulesets;
- secret scanning/security baseline;
- execution/runtime environment;
- test strategy;
- evidence/report locations;
- backup/restore policy;
- protected paths;
- project-specific stop conditions.

If any expected identity or SHA differs from live truth, stop mutation and investigate first.

## 2. Bootstrap

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

The command creates only a `governance/` directory and refuses to overwrite generated governance files that already exist.

## 3. Replace Placeholders from Live Facts

Generated values are scaffolding, not proof. Keep live SHAs in Task Packets and Result Packets, not in long-lived project profiles.

Never copy another project's repository name, current SHA, server identity, credentials, paths, CI identities, infrastructure details, test counts, production topology, or historical product decisions.

## 4. Qualify the Governance Process

Before normal production engineering, prove safe stopping for representative failures:
- wrong expected SHA;
- dirty worktree;
- unauthorized protected action;
- conflicting PR;
- missing evidence;
- resource/environment failure;
- secret exposure attempt;
- scope expansion.

A safe stop is a successful governance outcome.

## 5. First Governed Tasks

First run one READ-ONLY DIAGNOSIS end to end. Then run one small isolated IMPLEMENTATION task with exact-source validation.

Merge only when explicitly authorized.

## 6. Adoption Qualification

Mark `governance/ADOPTION_STATUS.md` as `QUALIFIED` only when project identity, authority, CI/tests, environment, secrets, protection state, qualification fixtures, and attributable evidence have been proven.

Governance qualification does not mean the product itself is production-qualified.
