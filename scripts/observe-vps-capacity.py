#!/usr/bin/env python3
"""Read-only, sanitized capacity snapshot for a shared Linux development host.

No network calls, writes, privileged operations, Docker mutating commands, or
environment/config/secrets disclosure. This does NOT qualify an agent runtime.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

MIB = 1024 * 1024
DOCKER_SOCKET = Path("/var/run/docker.sock")


def parse_meminfo(content: str) -> dict[str, int | None]:
    fields = {}
    for line in content.splitlines():
        key, sep, value = line.partition(":")
        if not sep or key not in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
            continue
        parts = value.split()
        if len(parts) != 2 or parts[1] != "kB" or not parts[0].isdigit():
            continue
        fields[key] = int(parts[0]) * 1024
    return {
        "total_mib": fields.get("MemTotal", 0) // MIB or None,
        "available_mib": fields.get("MemAvailable", 0) // MIB or None,
        "swap_total_mib": fields.get("SwapTotal", 0) // MIB,
        "swap_free_mib": fields.get("SwapFree", 0) // MIB,
    }


def read_memory() -> dict:
    try:
        content = Path("/proc/meminfo").read_text(encoding="ascii")
        result = parse_meminfo(content)
        if result["total_mib"] is None or result["available_mib"] is None:
            return {"status": "UNKNOWN", "reason": "required memory counters unavailable"}
        return {"status": "OBSERVED", **result}
    except (OSError, UnicodeError, ValueError):
        return {"status": "UNKNOWN", "reason": "cannot read Linux memory counters"}


def read_disk(path: str) -> dict:
    try:
        usage = shutil.disk_usage(path)
        return {"status": "OBSERVED", "total_mib": usage.total // MIB,
                "free_mib": usage.free // MIB, "used_mib": usage.used // MIB}
    except OSError:
        return {"status": "UNKNOWN", "reason": "cannot inspect requested filesystem"}


def docker_status_counts(stdout: str) -> dict:
    lines = [x.strip().lower() for x in stdout.splitlines() if x.strip()]
    # 'docker ps' includes RUNNING containers only; stopped containers are not counted.
    return {
        "status": "OBSERVED",
        "running_containers": len(lines),
        "unhealthy": sum("(unhealthy)" in x for x in lines),
        "health_starting": sum("(health: starting)" in x for x in lines),
        "health_unreported": sum(not any(tag in x for tag in
                                     ("(healthy)", "(unhealthy)", "(health: starting)"))
                                 for x in lines),
    }


def observe_local_docker(socket: Path = DOCKER_SOCKET) -> dict:
    try:
        if not stat.S_ISSOCK(socket.stat().st_mode):
            return {"status": "UNKNOWN", "reason": "Docker local socket unavailable"}
    except OSError:
        return {"status": "UNKNOWN", "reason": "Docker local socket unavailable"}
    executable = shutil.which("docker")
    if not executable:
        return {"status": "UNKNOWN", "reason": "Docker client unavailable"}
    # Bypass DOCKER_HOST/context: query only the local Unix socket.
    command = [
        executable, "--host", "unix:///var/run/docker.sock",
        "ps", "--format", "{{.Status}}",
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, check=False, timeout=6,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                 "HOME": "/nonexistent", "DOCKER_CONFIG": "/nonexistent"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "UNKNOWN", "reason": "local Docker status probe unavailable"}
    # Never print stderr, names, labels, images, env, command lines, or secrets.
    if completed.returncode != 0 or len(completed.stdout) > 65536:
        return {"status": "UNKNOWN", "reason": "local Docker status probe unsuccessful"}
    return docker_status_counts(completed.stdout)


def collect(path: str) -> dict:
    memory = read_memory()
    disk = read_disk(path)
    docker = observe_local_docker()
    try:
        load1 = round(os.getloadavg()[0], 2)
    except (OSError, AttributeError):
        load1 = None
    logical_cpu = os.cpu_count()
    partial = any(x["status"] != "OBSERVED" for x in (memory, disk, docker))
    return {
        "schema_version": 1,
        "sample_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "mode": "READ_ONLY_OBSERVATION",
        "snapshot_status": "PARTIAL" if partial else "OBSERVED",
        "logical_cpus": logical_cpu if isinstance(logical_cpu, int) and logical_cpu > 0 else None,
        "load_average_1m": load1,
        "memory": memory,
        "disk": disk,
        "docker": docker,
        "agent_runtime_qualification": "NOT_RUN",
        "capacity_approval": "NOT_GRANTED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default="/", help="Filesystem to inspect (read-only)")
    args = parser.parse_args()
    print(json.dumps(collect(args.path), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
