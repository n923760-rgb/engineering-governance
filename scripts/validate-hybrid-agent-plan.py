#!/usr/bin/env python3
"""Static, fail-closed contract for API-first coding-agent pilot plans.

This validates a JSON *plan*, not an agent, network policy, credential store,
service configuration, or runtime enforcement. No network calls are made.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit


class DuplicateKeyError(ValueError):
    pass


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def exact_fields(obj, fields, label, errors):
    if not isinstance(obj, dict):
        errors.append(f"{label} must be an object")
        return False
    for key in sorted(set(obj) ^ set(fields)):
        errors.append(f"{label}.{key} is unexpected or missing")
    return set(obj) == set(fields)


def remote_https_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return False
    try:
        u = urlsplit(value)
        host = u.hostname
        if (u.scheme != "https" or not host or u.username is not None
                or u.password is not None or u.query or u.fragment
                or u.port not in (None, 443) or not u.path.startswith("/")):
            return False
    except ValueError:
        return False
    if not re.fullmatch(r"[a-zA-Z0-9.-]+", host):
        return False
    if "." not in host or host.endswith(".") or ".." in host:
        return False
    if host.lower() == "localhost" or host.lower().endswith((".localhost", ".local", ".internal")):
        return False
    if any(not x or x.startswith("-") or x.endswith("-") for x in host.split(".")):
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return True
    return False


def positive_int(value, max_allowed):
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= max_allowed


def validate(plan):
    errors = []
    if not exact_fields(plan, {"schema_version", "deployment", "model_api", "hermes",
                               "limits", "permissions", "protected_actions"}, "plan", errors):
        return errors
    if type(plan["schema_version"]) is not int or plan["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if plan["deployment"] != "reference_only_no_runtime_activation":
        errors.append("deployment must be reference_only_no_runtime_activation")

    model = plan["model_api"]
    if exact_fields(model, {"kind", "base_url", "credentials"}, "model_api", errors):
        if model["kind"] != "remote_inference_only":
            errors.append("model_api.kind must be remote_inference_only")
        if not remote_https_url(model["base_url"]):
            errors.append("model_api.base_url must be a remote HTTPS URL without credentials")
        if model["credentials"] != "runtime_secret_reference_only":
            errors.append("model_api.credentials must use a runtime secret reference, never literal values")

    hermes = plan["hermes"]
    if exact_fields(hermes, {"mode", "requires_separate_runtime_qualification"}, "hermes", errors):
        if hermes["mode"] != "disabled":
            errors.append("hermes.mode must remain disabled in the API-first pilot")
        if hermes["requires_separate_runtime_qualification"] is not True:
            errors.append("Hermes runtime qualification must be separately required")

    limits = plan["limits"]
    if exact_fields(limits, {"max_parallel_tasks", "max_tool_calls", "max_task_seconds",
                             "max_cost_usd"}, "limits", errors):
        for name, maximum in (("max_parallel_tasks", 1), ("max_tool_calls", 80),
                              ("max_task_seconds", 1800)):
            if not positive_int(limits[name], maximum):
                errors.append(f"limits.{name} must be an integer from 1 to {maximum}")
        cost = limits["max_cost_usd"]
        try:
            if not isinstance(cost, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", cost):
                raise InvalidOperation
            amount = Decimal(cost)
            if not Decimal("0") < amount <= Decimal("5"):
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            errors.append("limits.max_cost_usd must be a positive decimal string <= 5.00")

    permissions = plan["permissions"]
    required = {"isolated_worktree", "production_read", "production_write",
                "docker_socket", "host_secrets", "main_branch_write"}
    if exact_fields(permissions, required, "permissions", errors):
        if permissions["isolated_worktree"] is not True:
            errors.append("permissions.isolated_worktree must be true")
        for name in required - {"isolated_worktree"}:
            if permissions[name] is not False:
                errors.append(f"permissions.{name} must be false")

    protected = plan["protected_actions"]
    required_actions = {"merge", "deploy", "release", "credential_changes", "policy_changes"}
    if exact_fields(protected, required_actions, "protected_actions", errors):
        for name in required_actions:
            if protected[name] != "owner_approval":
                errors.append(f"protected_actions.{name} requires owner_approval")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    args = parser.parse_args()
    try:
        text = args.plan_json.read_text(encoding="utf-8")
        plan = json.loads(text, object_pairs_hook=no_duplicate_keys,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"HYBRID_PREFLIGHT=BLOCKED: {exc}", file=sys.stderr)
        return 2
    errors = validate(plan)
    if errors:
        print("HYBRID_PREFLIGHT=BLOCKED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HYBRID_PREFLIGHT=PASS")
    print("RUNTIME_ENFORCEMENT=NOT_VERIFIED")
    print("HERMES_ACTIVATION=DISABLED")
    print("DEPLOYMENT=NOT_AUTHORIZED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
