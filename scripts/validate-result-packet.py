#!/usr/bin/env python3
"""Bind a result to an independently supplied approved task and retained evidence."""
import argparse
import sys
from pathlib import Path

from governance_contracts import (
    ContractError, load_object, sha256, validate_manifest, validate_schema, validate_task,
)


def validate_result(packet: Path, approved_task: Path, manifest_path: Path | None) -> None:
    data = load_object(packet)
    validate_schema(data, "result-packet.schema.json")
    task = load_object(approved_task)
    validate_task(task)
    if (packet.parent / data["task_packet_ref"]).resolve() != approved_task.resolve():
        raise ContractError("task packet reference does not match independently supplied approved task")
    if data["task_packet_sha256"] != sha256(approved_task):
        raise ContractError("approved task packet SHA-256 mismatch")
    for key in ("task_id", "task_type", "repository", "official_branch"):
        if data[key] != task[key]:
            raise ContractError(f"result does not match approved task: {key}")
    if data["verified_remote_official_head"] != task["expected_official_head"]:
        raise ContractError("result official source does not match approved task")
    authorized = set(task["authorized_actions"])
    if set(data["authorized_actions"]) != authorized:
        raise ContractError("result authorized actions differ from approved task")
    outside = set(data["actions_actually_performed"]) - authorized
    if outside:
        raise ContractError("actions actually performed exceed authorization: " + ", ".join(sorted(outside)))

    manifest = None
    if manifest_path is not None:
        reference = data.get("evidence_manifest_ref")
        if not reference or (packet.parent / reference).resolve() != manifest_path.resolve():
            raise ContractError("evidence manifest reference does not match supplied manifest")
        manifest = validate_manifest(manifest_path)
        for key, result_key in (("task_id", "task_id"), ("source_sha", "exact_tested_head"),
                                ("execution_environment", "execution_environment")):
            if manifest[key] != data[result_key]:
                raise ContractError(f"evidence manifest does not match result: {key}")
    elif data.get("evidence_manifest_ref"):
        raise ContractError("independently supplied --evidence-manifest is required")

    retained = {a["path"] for a in manifest["artifacts"]} if manifest else set()
    for index, item in enumerate(data["validation"]):
        status = item["status"]
        evidence = item["evidence"]
        if status in {"PASS", "FAIL"} and not evidence:
            raise ContractError(f"validation[{index}] with status {status} requires meaningful evidence")
        if status in {"BLOCKED", "UNKNOWN", "SKIPPED", "NOT RUN"} and not item.get("reason", "").strip():
            raise ContractError(f"validation[{index}] with status {status} requires a reason")
        if set(evidence) - retained:
            raise ContractError(f"validation[{index}] references evidence absent from verified manifest")
        if status in {"PASS", "FAIL"} and manifest is None:
            raise ContractError("PASS/FAIL requires a verified evidence manifest")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--task", required=True, type=Path,
                        help="Approved task selected by the controller, not by the result author.")
    parser.add_argument("--evidence-manifest", type=Path,
                        help="Retained evidence manifest supplied independently by the reviewer.")
    args = parser.parse_args()
    try:
        validate_result(args.packet, args.task, args.evidence_manifest)
    except ContractError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("VALID: result matches approved task and verified evidence")


if __name__ == "__main__":
    main()
