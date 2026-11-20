#!/usr/bin/env python3
"""Offline API token-cost estimator for a bounded, single-task pilot.

No model calls, credentials, network, billing reconciliation or runtime cost
enforcement. All rates are manually supplied and must be independently checked.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_UP
from pathlib import Path

MAX_BYTES = 16384
MILLION = Decimal("1000000")
MONEY = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,8})?\Z")


class InvalidPacket(ValueError):
    pass


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidPacket("duplicate JSON property")
        result[key] = value
    return result


def exact_keys(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise InvalidPacket(f"{label} has missing or unrecognized properties")
    return value


def decimal(value, label, upper, *, allow_zero=False):
    if not isinstance(value, str) or MONEY.fullmatch(value) is None:
        raise InvalidPacket(f"{label} must be a plain decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise InvalidPacket(f"{label} invalid decimal") from exc
    if parsed > upper or (parsed == 0 and not allow_zero):
        raise InvalidPacket(f"{label} outside permitted range")
    return parsed


def int_tokens(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100000:
        raise InvalidPacket(f"{label} must be an integer from 0 to 100000")
    return value


def estimate(data):
    root = exact_keys(data, {
        "schema_version", "task_id", "source_type", "tokens",
        "rates_usd_per_million", "limits",
    }, "packet")
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise InvalidPacket("schema_version must be 1")
    task = root["task_id"]
    if not isinstance(task, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,64}", task) is None:
        raise InvalidPacket("task_id must be a non-sensitive identifier")
    if root["source_type"] not in ("synthetic_fixture", "provider_reported"):
        raise InvalidPacket("source_type must be synthetic_fixture or provider_reported")

    counts = exact_keys(root["tokens"], {"input", "output"}, "tokens")
    num_in = int_tokens(counts["input"], "tokens.input")
    num_out = int_tokens(counts["output"], "tokens.output")
    total = num_in + num_out
    if total <= 0:
        raise InvalidPacket("token counts cannot both be zero")

    rates = exact_keys(root["rates_usd_per_million"], {"input", "output"}, "rates")
    rate_in = decimal(rates["input"], "rates.input", Decimal("1000"))
    rate_out = decimal(rates["output"], "rates.output", Decimal("1000"))
    limits = exact_keys(root["limits"], {"max_task_cost_usd", "max_total_tokens"}, "limits")
    cap = decimal(limits["max_task_cost_usd"], "limits.max_task_cost_usd", Decimal("5"))
    max_tokens = limits["max_total_tokens"]
    if type(max_tokens) is not int or not 1 <= max_tokens <= 100000:
        raise InvalidPacket("limits.max_total_tokens must be an integer 1..100000")

    exact_usd = (Decimal(num_in) * rate_in + Decimal(num_out) * rate_out) / MILLION
    passed = total <= max_tokens and exact_usd <= cap
    # Round UP only for display; cap comparison always uses full precision.
    shown = exact_usd.quantize(Decimal("0.00000001"), rounding=ROUND_UP)
    return {
        "schema_version": 1,
        "task_id": task,
        "source_type": root["source_type"],
        "token_count": total,
        "estimated_cost_usd": format(shown, ".8f"),
        "within_declared_limits": passed,
        "api_cost_estimate": "WITHIN_CAP" if passed else "OVER_CAP",
        "provider_billing": "NOT_VERIFIED",
        "runtime_enforcement": "NOT_PERFORMED",
        "api_calls": "NONE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("usage_packet_json", type=Path)
    args = parser.parse_args()
    try:
        if args.usage_packet_json.stat().st_size > MAX_BYTES:
            raise InvalidPacket("packet too large")
        content = args.usage_packet_json.read_text(encoding="utf-8")
        data = json.loads(content, object_pairs_hook=unique_keys,
                          parse_constant=lambda x: (_ for _ in ()).throw(InvalidPacket("nonfinite number")))
        result = estimate(data)
    except (InvalidPacket, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"API_COST_PREFLIGHT=BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["within_declared_limits"] else 3


if __name__ == "__main__":
    sys.exit(main())
