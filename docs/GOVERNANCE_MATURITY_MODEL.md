# Governance Maturity and Agent Autonomy Qualification

Status: **central reference proposal**. These are internal capability levels, not
an external certification, permission grant, or claim that any target has passed.
Assess each target project and capability against its live adopted governance
source and runtime. Use `docs/RISK_PROFILES.md` independently: LIGHT/STANDARD/HIGH
is impact-based and is **not** interchangeable with maturity level.

## Invariants at every level

- Owner authority, live source identity, protected actions, explicit scope,
  truthful evidence, secret hygiene and tested rollback are non-negotiable.
- Controller-issued task and tool policy cannot be rewritten or expanded by an
  Executor, model output, MCP server, AGENTS.md/CLAUDE.md, CI artifact or comment.
- A claimed level requires recorded applicable test results against the **actual
  enforcement boundary**. Missing evidence is UNKNOWN / NOT RUN, not PASS.
- A higher maturity level does not permit unattended main merges, releases,
  payments, production changes, credential rotation or approval-policy changes.
  Such actions remain protected by the adopted target's owner-approved workflow.
- No project automatically inherits a central reference change, level or grant.

## Capability levels and evidence gates

| Level | Goal | Minimum evidence before declaring achieved |
|---|---|---|
| L1 — Controlled | Source identity, risk classification, scoped tasks, required checks and manual approval | Verified branch/HEAD, reviewed diff, deterministic affected tests, protected-action inventory and rollback path |
| L2 — Isolated and observable | L1 plus least-privilege Executor, task-scoped credentials/tools, sandbox boundaries and redacted audit | Denied path/network/tool/secret probes, unexpected secondary MCP call blocked, access revocation test, trace linked to task and exact configuration |
| L3 — Supervised automation | L2 plus bounded agents that implement, test, independently review and raise PRs | Worktree isolation, concurrency collision test, exact-source CI, separate reviewer or independently governed verification, token expiry and budget/timeout fail-closed, no auto-merge |
| L4 — Measured and adaptive governance | L3 plus continuous control evaluation, drift detection, incident replay and policy-gated containment | Repeatable adversarial suite and review of false negatives/positives, deployment/version drift alerts, evidence retention and reproducible rollback/restoration drills |

Levels are cumulative **only for applicable capabilities**; document
non-applicability and evidence gaps. A maturity assessment is descriptive, never a
shortcut around the HIGH risk profile or the human owner.

## Temporary grant lifecycle

1. Controller binds a grant to task ID, repository, source/ref, specific tool and
   operation, path/recipient/egress allowlist, delegated identity and data scope.
2. Set a short expiry, usage limits, compute/network budget, issuer, revocation
   handle, and permitted concurrent workers. Prefer per-task identities over
   shared persistent keys. Executor cannot renew its own grant.
3. Enforce grants **outside** the Executor process or writable worktree. An
   expired, revoked, replayed, or widened grant must be rejected at call time.
4. Record sanitized allow/deny decisions; promptly revoke on task completion,
   timeout, cancellation, source drift or scope change. Test denial after expiry
   and revocation, not only happy-path access.
5. Protected actions require separate valid authority even when a tool or grant
   technically permits the API call.

## Independent verification and change gates

- Distinguish agent self-checks from independent review; a model explaining
  why its own output is safe is not a security gate.
- For HIGH impact changes, require the independent reviewer/test control defined
  by the project's adopted contract. Reviewer identity, source SHA, artifacts,
  audit results and approvals must be attributable.
- Model-generated tests alone are insufficient. Use negative-path authorization,
  prompt injection, unexpected MCP secondary call, race/concurrency, resource
  exhaustion and recovery fixtures as relevant.
- Verification occurs on the exact branch/artifact being proposed; any relevant
  source, dependency, environment or policy change invalidates affected evidence.
- Agents may prepare PRs only within an approved task. Never infer permission to
  merge or release from passing CI, a maturity label or a reviewer recommendation.

## Tool/model update qualification

Before adopting new Codex, Claude, DeepSeek or other agent/tool versions, or
changing MCP/skills/tool policies, run a **bounded, isolated comparison** using
pinned inputs and versions:

- baseline correctness and regressions on representative task fixtures;
- allowed versus denied tool decisions, data exfiltration, instruction injection
  from files/tool output and tool-call sequence audits;
- parallel-worktree isolation, replay/expiry/revocation and restore scenarios;
- token/compute/latency budgets, false-positive rate and review workload.

Document the version/digest, exact benchmark source and environment, samples,
outcomes, inconclusive cases and the owner-approved acceptance thresholds **before**
promotion. Use synthetic data, no production secrets, and never treat a vendor
benchmark or paper alone as deployment qualification. Compare against the existing
approved baseline and retain it if regression or missing evidence is material.

## Rollout, observability, rollback

Roll out L2-L4 controls by isolated qualification, limited pilot, and approved
wider adoption. Assess CPU/memory/disk, trace volume, latency, token cost, and
operator burden; a control that exhausts a shared VPS is not production-ready.
Define an approved rollback and revocation procedure; rehearse recovery from
failed tool policy updates, malformed grants, interrupted workers, and backup
restore where applicable. Keep prior known-good policies/records immutable.

Maintain a short per-project assessment:
`capability | claimed level | exact adopted reference | environment |
tests/evidence | known gaps | approver | expiry/reassessment date`.
Reassess after critical advisories, major tool upgrades, permission changes or
new privileged integrations. Recording a level must not mutate a target's
adoption lock or release state without separate authorization.

Related policies:
- `docs/CONTROLLER_EXECUTOR_MODEL.md`
- `docs/AGENT_EXECUTION_AUDIT_POLICY.md`
- `docs/MCP_SERVER_SECURITY_POLICY.md`
- `docs/CI_SUPPLY_CHAIN_SECURITY_POLICY.md`
- `docs/VULNERABILITY_RESPONSE_AND_RECOVERY.md`
- `docs/GOVERNANCE_VERSIONING.md`
