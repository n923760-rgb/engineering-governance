# Adopting the Master Engineering System in Any Project

A target project must derive its own facts from current source and environment.

## 1. Verify execution capability

At the beginning of each session, verify the capabilities actually available: real Git/CLI, repository API/MCP, CI, engineering lab/runtime, or advisory-only mode.

Do not claim unavailable actions. Report them as `BLOCKED`, `NOT RUN`, or `UNKNOWN` as appropriate.

## 2. Start with the Master Re-baseline

The first round is read-only. Inspect repository identity, branches/live HEAD, instructions, architecture and subsystem contracts, active PRs, toolchain, product identity, release/signing/deployment structure, source/state ownership, tests/CI, protection/security, runtime evidence, lab requirements, evidence/report/artifact locations, backup/restore, project stop conditions, and an existing `/ENGINEERING/MASTER_ROADMAP.md` if present.

Produce a `MASTER ENGINEERING BASELINE REPORT` before normal implementation.

The report may propose the canonical roadmap state. It must not write that roadmap while the first round remains read-only.

## 3. Establish canonical project engineering storage

In the first later repository-mutation round explicitly authorized for governance adoption, establish or reconcile:

- `/ENGINEERING/MASTER_ROADMAP.md`
- `/ENGINEERING/REPORTS/`
- `/ENGINEERING/EVIDENCE/`

Maintain only one roadmap for the project.

The roadmap holds project state, gates, decisions, risks, and exact next round. Detailed report bodies and evidence belong in their dedicated locations and are linked from the roadmap.

## 4. Bootstrap when authorized

```bash
python scripts/bootstrap-project.py \
  --project-name "Example Project" \
  --repository "owner/example-project" \
  --official-branch main \
  --destination /path/to/example-project
```

Generated files are scaffolding, not proof. The bootstrap must not be run as part of the strictly read-only first round.

## 5. Qualify the engineering environment

Record the actual lab/execution environment, toolchains, paths, resources, artifacts, evidence retention, backups, and runtime limitations. Use a hybrid model when the lab cannot prove required runtime behavior.

## 6. Qualify governance

Prove safe stopping for wrong SHA, dirty source, unauthorized protected action, conflicting PR, missing evidence, unavailable execution capability, environment failure, secret exposure attempt, and scope expansion.

## 7. First governed work

Run one read-only diagnosis end to end, then one small isolated implementation task with exact-source validation.

## 8. Adoption qualification

Mark adoption `QUALIFIED` only when project identity, repository authority, canonical roadmap, CI/tests, environment/lab, secrets, protection state, qualification fixtures, and attributable evidence are proven.

Governance qualification does not mean the product itself is production-qualified.
