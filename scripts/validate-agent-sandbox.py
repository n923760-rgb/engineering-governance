#!/usr/bin/env python3
"""Static, fail-closed preflight for a disposable agent *executor* Compose service.

This is NOT a Docker runtime inspection, an egress firewall, or permission to run.
A networked agent gateway/controller must be reviewed independently.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MIB = 1024 * 1024
MAX_BYTES = 1024 * MIB
MIN_BYTES = 128 * MIB
UID = re.compile(r"^[1-9][0-9]*(?::[1-9][0-9]*)?$")
DIGEST = re.compile(r"^[a-zA-Z0-9._/-]+(?:\:[0-9]+)?(?:/[a-zA-Z0-9._/-]+)?@sha256:[a-f0-9]{64}$")


def memory_bytes(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"([0-9]+)([kKmMgG]?)", value.strip())
    if not match:
        return None
    units = {"": 1, "k": 1024, "m": MIB, "g": 1024 * MIB}
    return int(match.group(1)) * units[match.group(2).lower()]


def check(config: object, service_name: str, scratch_volume: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(config, dict) or not isinstance(config.get("services"), dict):
        return ["invalid Compose JSON: expected services object"]
    service = config["services"].get(service_name)
    if not isinstance(service, dict):
        return [f"service {service_name!r} is absent"]

    if not isinstance(service.get("image"), str) or not DIGEST.fullmatch(service["image"]):
        problems.append("image must be pinned to an immutable sha256 digest")
    if service.get("build") is not None:
        problems.append("build is prohibited for the qualified executor image")
    if not UID.fullmatch(str(service.get("user", ""))):
        problems.append("user must be an explicit non-root numeric UID[:GID]")
    if service.get("read_only") is not True:
        problems.append("read_only filesystem is required")
    if service.get("privileged") is not False:
        problems.append("privileged must be explicitly false")
    drops = service.get("cap_drop", [])
    if not isinstance(drops, list) or "ALL" not in [str(v).upper() for v in drops]:
        problems.append("cap_drop must contain ALL")
    if service.get("cap_add"):
        problems.append("cap_add is prohibited")
    opts = service.get("security_opt", [])
    if not isinstance(opts, list) or not any(
        str(opt).lower() in ("no-new-privileges", "no-new-privileges:true") for opt in opts
    ):
        problems.append("security_opt must include no-new-privileges:true")
    if isinstance(opts, list) and any(
        "unconfined" in str(opt).lower() or "no-new-privileges:false" in str(opt).lower()
        for opt in opts
    ):
        problems.append("unconfined or disabled security settings are prohibited")
    if service.get("network_mode") != "none":
        problems.append("executor network_mode must be none (gateway is separate)")

    mem = memory_bytes(service.get("mem_limit"))
    if mem is None or not MIN_BYTES <= mem <= MAX_BYTES:
        problems.append("mem_limit must be between 128 MiB and 1 GiB")
    cpus = service.get("cpus")
    try:
        cpu_value = float(cpus)
    except (TypeError, ValueError):
        cpu_value = 0.0
    if not 0 < cpu_value <= 1:
        problems.append("cpus must be positive and at most 1")
    pids = service.get("pids_limit")
    if isinstance(pids, bool) or not isinstance(pids, int) or not 1 <= pids <= 128:
        problems.append("pids_limit must be between 1 and 128")

    for key in (
        "ports", "expose", "devices", "device_cgroup_rules", "secrets", "configs",
        "group_add", "volumes_from", "extra_hosts", "sysctls", "dns", "dns_search",
        "gpus", "device_requests", "runtime",
        "environment", "env_file", "links", "extends", "cgroup_parent",
    ):
        if service.get(key):
            problems.append(f"{key} is prohibited in the isolated executor")
    if service.get("pid") == "host" or service.get("ipc") == "host":
        problems.append("host PID/IPC namespace is prohibited")
    if service.get("userns_mode") == "host":
        problems.append("host user namespace is prohibited")
    if service.get("restart") not in (None, "no"):
        problems.append("executor must not be configured as an always-on service")

    mounts = service.get("volumes", [])
    if not isinstance(mounts, list) or len(mounts) != 1:
        problems.append("exactly one isolated named scratch volume is required")
    else:
        mount = mounts[0]
        if (not isinstance(mount, dict)
                or mount.get("type") != "volume"
                or mount.get("source") != scratch_volume
                or mount.get("target") != "/workspace"
                or mount.get("read_only") is True):
            problems.append("only an exact, writable named scratch volume at /workspace is allowed")

    declared_volumes = config.get("volumes", {})
    volume = declared_volumes.get(scratch_volume) if isinstance(declared_volumes, dict) else None
    if not isinstance(volume, dict):
        problems.append("scratch volume must be explicitly declared at Compose top level")
    elif (volume.get("external") is True
          or volume.get("driver") not in (None, "local")
          or volume.get("driver_opts")
          or volume.get("name") != scratch_volume):
        problems.append("scratch volume must be local, non-external, unbound and exactly named")

    # Top-level service policy is only one piece of a complete Compose/runtime review.
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("compose_json", type=Path, help="docker compose config --format json output")
    parser.add_argument("--service", required=True, help="executor (not gateway) service name")
    parser.add_argument("--scratch-volume", required=True, help="approved exact named volume")
    args = parser.parse_args()
    if not args.scratch_volume or "/" in args.scratch_volume or "\\" in args.scratch_volume:
        print("STATIC_PREFLIGHT=BLOCKED: scratch volume must be a name", file=sys.stderr)
        return 2
    try:
        config = json.loads(args.compose_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"STATIC_PREFLIGHT=BLOCKED: unreadable or invalid Compose JSON: {exc}", file=sys.stderr)
        return 2
    errors = check(config, args.service, args.scratch_volume)
    if errors:
        print("STATIC_PREFLIGHT=BLOCKED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("STATIC_PREFLIGHT=PASS")
    print("RUNTIME_QUALIFICATION=NOT_RUN")
    print("AUTHORIZATION=NOT_GRANTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
