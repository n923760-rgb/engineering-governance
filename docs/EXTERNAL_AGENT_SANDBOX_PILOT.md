# External coding agent: isolated executor pilot

Status: REFERENCE ONLY. This document does not install Hermes, authorize a target project, or qualify a running VPS.

This contract applies to the disposable **tool/executor sandbox**, NOT the networked Hermes gateway/controller. Hermes, Codex and Claude Code may be evaluated under the same boundary. Never start by installing an agent as root or mounting the Docker socket, home directories, project worktrees, SSH keys, API keys, production volumes or backups into a model-controlled process.

## Qualification sequence

1. Record owner authorization, target repository, exact official source SHA, scope, risk, time/resource limits and stop conditions using the existing Task Packet. Inspect live PR state before mutation.
2. Inventory actual VPS CPU/memory/disk, existing services, network, volumes, ports, backups and health. Do not assume spare host capacity from an advertised machine size.
3. Review the official Hermes source and immutable image digest, skills/plugins/hooks, model provider and budget. The Hermes gateway may need external model API access: independently review and constrain its outbound network and tool rights. Never equate gateway configuration or an LLM prompt with an OS security boundary.
4. Use a throwaway Docker Compose executor with explicit non-root numeric user, read-only root filesystem, all capabilities dropped, no-new-privileges, network_mode none, exactly one named scratch volume at /workspace, no host bind mounts/credentials/exposed ports, cpus <= 1, mem_limit <= 1 GiB and pids_limit <= 128. Keep pilot concurrency at one.
5. Validate rendered Compose JSON, not just the YAML source. With the governance repository checked out, run:

        umask 077
        config_file="$(mktemp)"
        trap 'rm -f "$config_file"' EXIT
        docker compose -f hermes-pilot.compose.yml config --format json > "$config_file"
        python3 scripts/validate-agent-sandbox.py "$config_file" \
          --service hermes-executor --scratch-volume agent-exec-scratch

   The Compose filename and service/volume names above are examples; use the real approved values. Rendered Compose files can contain interpolated credentials: keep the temporary file private and delete it.
6. Independently inspect the running container: exact image digest, process UID, network isolation, effective mounts/capabilities, host firewall, CPU/memory/pid enforcement, unauthorized file/secret access, cross-worktree writes and resource exhaustion. Run negative permission probes using synthetic fixtures. Check service health and cleanup/rollback.
7. Start with a read-only disposable repository task. After separate authorization, compare one bounded implementation against Codex/Claude on correctness, tests, evidence, token/API cost, duration and unintended changes.
8. Only then request a decision on integration with the AI Dev Lab controller, GitHub App and private dashboard. The owner retains authority for merge to main, deployment, credentials and protected policy actions.

## Interpretation

STATIC_PREFLIGHT=PASS means only that a supplied JSON document met these **structural** checks. It does NOT prove an image was executed, OS isolation is effective, gateway egress is restricted, the model/skills are safe, or authority was granted. The tool deliberately prints RUNTIME_QUALIFICATION=NOT_RUN and AUTHORIZATION=NOT_GRANTED. Unknown runtime state blocks dependent execution.

Related reference contracts:
- docs/AGENT_EXECUTION_AUDIT_POLICY.md
- docs/MCP_SERVER_SECURITY_POLICY.md
- docs/STOP_CONDITIONS.md

Official upstream references (verify exact versions/digests when adopting):
- https://github.com/NousResearch/hermes-agent
- https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md
- https://hermes-agent.nousresearch.com/docs/getting-started/official-domains
