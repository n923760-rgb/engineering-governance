# Shared VPS capacity: read-only observation

Status: **reference-only diagnostic**. This is not a deployment, agent-executor
qualification, credential check, or authorization to run Hermes.

This portable Linux probe complements `scripts/verify-environment-capacity.py`.
The older script can test disk writeability; this new observer performs **no
writes**, creates no temporary files, and collects only a small set of counters.

## Observe a host, after reviewing the source

Run as an ordinary, already authorized operator (e.g., a non-root development
account) on an approved checkout, without sudo:

    python3 scripts/observe-vps-capacity.py --path /

Its JSON output includes:

- CPU count and one-minute load average (not a CPU utilization percentage).
- Current available/total memory and swap in MiB, from /proc/meminfo.
- Disk capacity in MiB for the requested filesystem.
- Counts of *running* containers and aggregate Docker health states, if the
  **local** Docker Unix socket is accessible.

It does not print names, images, ports, environment variables, credentials,
Docker labels, mounts, individual process arguments, or full Docker errors.
It explicitly targets the local Unix socket and only runs `docker ps` with a
status-only template and a six-second timeout. It does not use Docker Compose,
call an API, download files, modify Git, or invoke a privileged operation.
If Docker is inaccessible, its status is UNKNOWN rather than PASS.

The tool reports OBSERVED or PARTIAL; neither means capacity qualification.
CPU/RAM pressure may spike and Docker permissions or service health may be
unknown. Use separate live peak metrics, task limits, resource contention,
backup state, and runtime isolation probes before authorizing any agent.

## Offline regression checks

    python3 -m unittest discover -s qualification -p 'test_vps_capacity_observer.py' -v

On GitHub Actions this test runs only against synthetic fixtures; its optional
host smoke check observes a **GitHub-hosted runner**, not the user's VPS.

## Safe handoff

Provide the JSON snapshot to the project owner/reviewer. Avoid pasting an
entire Docker inspect, compose config, process environment, private key, or API
token. A capacity snapshot by itself must not trigger a deployment.

Related: docs/AGENT_EXECUTION_AUDIT_POLICY.md, docs/STOP_CONDITIONS.md,
docs/CONTROLLER_EXECUTOR_MODEL.md.
