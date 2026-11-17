# API-first hybrid coding agents: reference-only contract

Status: **PROPOSAL / OFFLINE PREFLIGHT ONLY**. This document does not install Hermes, access a VPS, enable new API credentials, or authorize changes to a target repository. All deployments and policy adoption require an independently authorized task and live runtime qualification.

## Goal and boundary

Use remote inference APIs for model computation, while an existing, owner-controlled local AI development controller handles the workspace, Codex / Claude Code tools, review, GitHub, and CI. This avoids running local inference or a continuously running Hermes agent on a resource-constrained shared VPS. An inference API call does not itself execute repository operations or provide shared memory.

An optional future Hermes API server is a **tool-capable agent process**, not merely an LLM inference endpoint. Its tools may operate on the Hermes server host; never treat its endpoint as a harmless model proxy. Evaluate it independently with the isolated-executor boundaries in the proposed EXTERNAL_AGENT_SANDBOX_PILOT guide (separate PR), and with docs/AGENT_EXECUTION_AUDIT_POLICY.md. Do not rely on prompts or config flags alone for sandboxing.

## API-first contract

The sample in examples/hybrid-agent-plan.example.json is intentionally nonfunctional: the hostname ends in .invalid. The model API URL must be remotely hosted HTTPS, with **no key embedded** in the URL or checked-in plan. Credentials must be issued and injected separately with task-scoped, auditable permissions. Exact outbound host, DNS/IP changes, request destination, and secret handling must be enforced by infrastructure beyond this static validator.

The initial profile is deliberately limited:

- One active task; bounded tool calls, task time and dollar budget.
- No Hermes API use until separate runtime qualification is approved.
- Isolated worktree execution; no production read/write, direct main write, Docker socket, or host-secret access.
- Merge, deployment, release, credential changes and policy changes require owner approval.
- Task Packet and Result/Evidence Packet retain exact source identity and independently checked CI evidence.
- Existing agents may write only through previously qualified sandbox/tool permissions; this JSON does not grant access.

Validate a proposed reference plan locally without contacting any remote service:

    python3 scripts/validate-hybrid-agent-plan.py examples/hybrid-agent-plan.example.json
    python3 -m unittest discover -s qualification -p test_hybrid_agent_plan.py -v

Expected valid output includes HYBRID_PREFLIGHT=PASS, RUNTIME_ENFORCEMENT=NOT_VERIFIED, HERMES_ACTIVATION=DISABLED and DEPLOYMENT=NOT_AUTHORIZED.

## Operational adoption sequence (separate authorization required)

1. Inspect current project/server resources, runtime, GitHub state, existing PRs, approval policy and data classification.
2. Select a provider with an approved endpoint, model capability, billing cap and appropriate data-handling terms; independently verify actual costs.
3. Establish a controller-side outbound host allowlist, secret boundary, network/egress restrictions, token usage and cost logging without unnecessary exposure of prompts, private code, or credentials.
4. Exercise one read-only task on a disposable repository. Then authorize one bounded write task in an isolated worktree; review diff, tests, evidence hashes, CI and rollback path.
5. Compare cost and result quality to the existing Codex/Claude setup. Only consider Hermes on demand if there is a demonstrated benefit. Treat a Hermes API gateway, executor and tool rights as separate security subjects.
6. Keep main merges, production deploys, releases, policy edits and secret rotation behind independent owner-approval gates.

## What this change does not prove

HYBRID_PREFLIGHT=PASS verifies only the shape and conservative intent of a JSON plan. It does **not** prove the provider is authentic, URLs are reachable or safe from DNS rebinding, credentials remain secret, API costs will be bounded, worktrees are isolated, model tool calls are authorized, or the VPS has spare CPU/RAM. No runtime integration or provider call is performed by this contract.

Related reference contracts:
- docs/CONTROLLER_EXECUTOR_MODEL.md
- docs/AGENT_EXECUTION_AUDIT_POLICY.md
- docs/STOP_CONDITIONS.md
- Hermes official API guide: https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/
