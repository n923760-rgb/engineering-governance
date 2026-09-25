# Adopting the Master Engineering System in Any Project

A target project must derive its own facts from current source and environment.

## 1. Start with the Master Re-baseline

The first round is read-only. Inspect repository identity, branches/live HEAD, instructions, architecture and subsystem contracts, active PRs, toolchain, product identity, release/signing/deployment structure, source/state ownership, tests/CI, protection/security, runtime evidence, lab requirements, evidence/report/artifact locations, backup/restore, and project stop conditions.

Produce a `MASTER ENGINEERING BASELINE REPORT` before normal implementation.

## 2. Bootstrap

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

Generated files are scaffolding, not proof.

## 3. Establish one Master Roadmap

Create and maintain one `MASTER_ENGINEERING_ROADMAP.md`. Reconcile it with new evidence instead of creating competing roadmaps.

Classify important claims as `FACT`, `INFERENCE`, `UNKNOWN`, or `BLOCKED`.

## 4. Qualify the engineering environment

Record the actual lab/execution environment, toolchains, paths, resources, artifacts, evidence retention, backups, and runtime limitations. Use a hybrid model when the lab cannot prove required runtime behavior.

## 5. Qualify governance

Prove safe stopping for wrong SHA, dirty source, unauthorized protected action, conflicting PR, missing evidence, environment failure, secret exposure attempt, and scope expansion.

## 6. First governed work

Run one read-only diagnosis end to end, then one small isolated implementation task with exact-source validation.

## 7. Adoption qualification

Mark adoption `QUALIFIED` only when project identity, repository authority, roadmap, CI/tests, environment/lab, secrets, protection state, qualification fixtures, and attributable evidence are proven.

Governance qualification does not mean the product itself is production-qualified.
