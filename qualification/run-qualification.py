#!/usr/bin/env python3
"""Adversarial qualification tests for governance safety, authority, evidence, and environment gates."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
LIVE_GATE = ROOT / "scripts" / "verify-repository-state.sh"
ENVIRONMENT_GATE = ROOT / "scripts" / "verify-environment-capacity.py"
BOOTSTRAP = ROOT / "scripts" / "bootstrap-project.py"
PR_STATE_GATE = ROOT / "scripts" / "verify-github-pr-state.py"
TASK_VALIDATOR = ROOT / "scripts" / "validate-task-packet.py"
RESULT_VALIDATOR = ROOT / "scripts" / "validate-result-packet.py"
EVIDENCE_VALIDATOR = ROOT / "scripts" / "validate-evidence-manifest.py"
SECRET_SCANNER = ROOT / "scripts" / "scan-secrets.py"
VALID_TASK = ROOT / "examples" / "task-packet.example.json"
VALID_RESULT = ROOT / "examples" / "result-packet.example.json"
VALID_EVIDENCE = ROOT / "examples" / "evidence-manifest.example.json"


class QualificationFailure(RuntimeError):
    pass


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QualificationFailure(message)


def expect_code(
    name: str,
    command: list[str],
    expected_code: int,
    cwd: Path | None = None,
    output_must_contain: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = run(command, cwd=cwd)
    combined = f"{result.stdout}\n{result.stderr}"
    require(
        result.returncode == expected_code,
        f"{name}: expected exit {expected_code}, got {result.returncode}\n{combined}",
    )
    if output_must_contain:
        require(
            output_must_contain in combined,
            f"{name}: missing expected output {output_must_contain!r}\n{combined}",
        )
    print(f"PASS: {name}")
    return result


def git(cwd: Path, *args: str) -> str:
    result = run(["git", *args], cwd=cwd)
    require(
        result.returncode == 0,
        f"git {' '.join(args)} failed in {cwd}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
    )
    return result.stdout.strip()


def build_live_gate_fixture(base: Path) -> tuple[Path, str]:
    remote = base / "remote.git"
    seed = base / "seed"
    work = base / "work"

    require(run(["git", "init", "--bare", str(remote)]).returncode == 0, "cannot init bare remote")
    require(run(["git", "init", "-b", "main", str(seed)]).returncode == 0, "cannot init seed repo")
    git(seed, "config", "user.email", "qualification@example.invalid")
    git(seed, "config", "user.name", "Governance Qualification")
    (seed / "README.md").write_text("qualification fixture\n", encoding="utf-8")
    git(seed, "add", "README.md")
    git(seed, "commit", "-m", "fixture: initial")
    git(seed, "remote", "add", "origin", str(remote))
    git(seed, "push", "-u", "origin", "main")
    expected_head = git(seed, "rev-parse", "HEAD")

    clone = run(["git", "clone", "-b", "main", str(remote), str(work)])
    require(clone.returncode == 0, f"cannot clone live-gate fixture\n{clone.stderr}")
    return work, expected_head


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def qualify_task_packet_validation(tmp: Path) -> None:
    expect_code(
        "valid task packet accepted",
        [sys.executable, str(TASK_VALIDATOR), str(VALID_TASK)],
        0,
        output_must_contain="VALID:",
    )

    missing = tmp / "task-missing-field.json"
    data = json.loads(VALID_TASK.read_text(encoding="utf-8"))
    data.pop("scope")
    write_json(missing, data)
    expect_code(
        "missing task field rejected",
        [sys.executable, str(TASK_VALIDATOR), str(missing)],
        1,
        output_must_contain="scope",
    )

    bad_sha = tmp / "task-bad-sha.json"
    data = json.loads(VALID_TASK.read_text(encoding="utf-8"))
    data["expected_official_head"] = "not-a-sha"
    write_json(bad_sha, data)
    expect_code(
        "malformed expected SHA rejected",
        [sys.executable, str(TASK_VALIDATOR), str(bad_sha)],
        1,
        output_must_contain="expected_official_head",
    )

    requested_not_authorized = tmp / "task-requested-not-authorized.json"
    data = json.loads(VALID_TASK.read_text(encoding="utf-8"))
    data["requested_actions"].append("merge")
    write_json(requested_not_authorized, data)
    expect_code(
        "requested action without authority rejected",
        [sys.executable, str(TASK_VALIDATOR), str(requested_not_authorized)],
        1,
        output_must_contain="requested actions are not authorized: merge",
    )

    protected_without_owner = tmp / "task-protected-without-owner.json"
    data = json.loads(VALID_TASK.read_text(encoding="utf-8"))
    data["requested_actions"].append("merge")
    data["authorized_actions"].append("merge")
    write_json(protected_without_owner, data)
    expect_code(
        "protected action without owner authorization rejected",
        [sys.executable, str(TASK_VALIDATOR), str(protected_without_owner)],
        1,
        output_must_contain="lacks explicit owner authorization",
    )

    protected_with_owner = tmp / "task-protected-with-owner.json"
    data["action_targets"] = {"merge": "PR:1"}
    data["protected_action_authorizations"]["merge"] = {
        "source": "CURRENT_OWNER_INSTRUCTION",
        "reference": "owner explicitly authorized merge for this bounded task",
        "authorization_id": "FIXTURE-APPROVAL-1",
        "status": "ACTIVE",
        "repository": data["repository"],
        "target": "PR:1",
        "boundary": "Merge only the qualified PR:1 after required CI.",
    }
    write_json(protected_with_owner, data)
    expect_code(
        "protected action with explicit owner authorization accepted",
        [sys.executable, str(TASK_VALIDATOR), str(protected_with_owner)],
        0,
        output_must_contain="VALID:",
    )


def result_command(path: Path) -> list[str]:
    # Reviewer/test supplies the approved paths; the result cannot select them.
    return [sys.executable, str(RESULT_VALIDATOR), str(path),
            "--task", str(path.parent / "task-packet.example.json"),
            "--evidence-manifest", str(path.parent / "evidence-manifest.example.json")]

def qualify_task_policy_boundaries(tmp: Path) -> None:
    def check(name: str, mutate, expected: str, code: int = 1) -> None:
        data = json.loads(VALID_TASK.read_text(encoding="utf-8"))
        mutate(data)
        path = tmp / (name.replace(" ", "-") + ".json")
        write_json(path, data)
        expect_code(name, [sys.executable, str(TASK_VALIDATOR), str(path)], code,
                    output_must_contain=expected)

    check("omitting merge protection cannot authorize merge",
          lambda d: (d["requested_actions"].append("merge"), d["authorized_actions"].append("merge"),
                     d.update(protected_actions=[])),
          "lacks explicit owner authorization")
    check("read only source mutation rejected",
          lambda d: d.update(task_type="READ-ONLY DIAGNOSIS", requested_actions=["read", "edit_source"],
                             authorized_actions=["read", "edit_source"]),
          "actions prohibited for task type")
    check("read only report creation accepted",
          lambda d: d.update(task_type="READ-ONLY DIAGNOSIS", requested_actions=["read", "write_report"],
                             authorized_actions=["read", "write_report"]),
          "VALID:", 0)
    check("runtime source mutation rejected", lambda d: d.update(task_type="RUNTIME QUALIFICATION"),
          "actions prohibited for task type")
    check("schema rejects non string action", lambda d: d["authorized_actions"].append({"merge": True}),
          "schema violation")
    check("schema rejects abbreviated source SHA", lambda d: d.update(expected_official_head="0123456"),
          "schema violation")

    approval = json.loads(VALID_TASK.read_text(encoding="utf-8"))
    approval["requested_actions"].append("merge")
    approval["authorized_actions"].append("merge")
    approval["action_targets"] = {"merge": "PR:1"}
    approval["protected_action_authorizations"]["merge"] = {
        "source": "OWNER_AUTHORIZATION_RECORD", "reference": "standing owner approval",
        "authorization_id": "FIXTURE-STANDING-1", "status": "ACTIVE",
        "repository": approval["repository"], "target": "PR:1",
        "boundary": "Only PR:1; qualified CI required.",
    }
    for name, change, code, expected in (
        ("standing authorization accepted", {}, 0, "VALID:"),
        ("revoked authorization rejected", {"status": "REVOKED"}, 1, "not active"),
        ("wrong authorization target rejected", {"target": "PR:2"}, 1, "target mismatch"),
        ("wrong authorization repository rejected", {"repository": "other/repo"}, 1, "repository mismatch"),
        ("expired authorization rejected", {"expires_at": "2000-01-01T00:00:00+00:00"}, 1, "expired"),
    ):
        data = json.loads(json.dumps(approval))
        data["protected_action_authorizations"]["merge"].update(change)
        path = tmp / (name.replace(" ", "-") + ".json")
        write_json(path, data)
        expect_code(name, [sys.executable, str(TASK_VALIDATOR), str(path)], code,
                    output_must_contain=expected)



def qualify_result_packet_validation(tmp: Path) -> None:
    expect_code("valid result packet accepted", result_command(VALID_RESULT), 0, output_must_contain="VALID:")
    base = tmp / "result-packets"
    shutil.copytree(ROOT / "examples", base)

    def check(name: str, mutate, expected: str, code: int = 1) -> None:
        data = json.loads(VALID_RESULT.read_text(encoding="utf-8"))
        mutate(data)
        path = base / (name.replace(" ", "-") + ".json")
        write_json(path, data)
        expect_code(name, result_command(path), code, output_must_contain=expected)

    check("PASS without evidence rejected", lambda d: d["validation"][0].update(evidence=[]),
          "requires meaningful evidence")
    check("NOT RUN without reason rejected", lambda d: d["validation"][1].pop("reason"),
          "requires a reason")
    check("performed action outside authority rejected",
          lambda d: d["actions_actually_performed"].append("merge"),
          "actions actually performed exceed authorization: merge")
    check("result self authorization rejected",
          lambda d: (d["authorized_actions"].append("merge"), d["actions_actually_performed"].append("merge")),
          "result authorized actions differ")
    check("missing task reference rejected", lambda d: d.update(task_packet_ref="missing-task.json"),
          "task packet reference does not match")
    check("changed approved task hash rejected", lambda d: d.update(task_packet_sha256="0" * 64),
          "task packet SHA-256 mismatch")
    check("result task identity mismatch rejected", lambda d: d.update(task_id="OTHER-TASK"),
          "result does not match approved task: task_id")
    check("result official source mismatch rejected",
          lambda d: d.update(verified_remote_official_head="0" * 40),
          "result official source does not match approved task")
    check("result typed field rejected", lambda d: d.update(repository=42), "schema violation")
    check("PASS with nonexistent evidence rejected",
          lambda d: d["validation"][0].update(evidence=["missing.log"]),
          "evidence absent from verified manifest")
    check("evidence source mismatch rejected", lambda d: d.update(exact_tested_head="0" * 40),
          "evidence manifest does not match result: source_sha")
    check("UNKNOWN with reason accepted",
          lambda d: d["validation"].append({"check": "external behavior", "status": "UNKNOWN",
                                           "evidence": [], "reason": "No external observation."}),
          "VALID:", 0)
    check("UNKNOWN without reason rejected",
          lambda d: d["validation"].append({"check": "external behavior", "status": "UNKNOWN", "evidence": []}),
          "requires a reason")
    expect_code("result cannot omit independent approved task",
                [sys.executable, str(RESULT_VALIDATOR), str(VALID_RESULT)], 2, output_must_contain="--task")
    artifact = base / "artifacts" / "evidence-fixture.txt"
    artifact.write_text("corrupted evidence of equal size"[:31], encoding="utf-8")
    # This payload is deliberately not the bytes accepted by the manifest.
    path = base / "corrupt-evidence-result.json"
    write_json(path, json.loads(VALID_RESULT.read_text(encoding="utf-8")))
    expect_code("result rejects corrupted retained artifact", result_command(path), 1,
                output_must_contain="SHA-256 mismatch")


def qualify_evidence_manifest_validation(tmp: Path) -> None:
    expect_code(
        "valid evidence manifest accepted",
        [sys.executable, str(EVIDENCE_VALIDATOR), str(VALID_EVIDENCE)],
        0,
        output_must_contain="VALID:",
    )

    fixture = ROOT / "examples" / "artifacts" / "evidence-fixture.txt"
    base = tmp / "evidence"
    artifacts = base / "artifacts"
    artifacts.mkdir(parents=True)
    shutil.copy2(fixture, artifacts / "evidence-fixture.txt")

    checksum_mismatch = base / "checksum-mismatch.json"
    data = json.loads(VALID_EVIDENCE.read_text(encoding="utf-8"))
    data["artifacts"][0]["sha256"] = "0" * 64
    write_json(checksum_mismatch, data)
    expect_code(
        "evidence checksum mismatch rejected",
        [sys.executable, str(EVIDENCE_VALIDATOR), str(checksum_mismatch)],
        1,
        output_must_contain="SHA-256 mismatch",
    )

    missing_artifact = base / "missing-artifact.json"
    data = json.loads(VALID_EVIDENCE.read_text(encoding="utf-8"))
    data["artifacts"][0]["path"] = "artifacts/missing.txt"
    write_json(missing_artifact, data)
    expect_code(
        "missing evidence artifact rejected",
        [sys.executable, str(EVIDENCE_VALIDATOR), str(missing_artifact)],
        1,
        output_must_contain="artifact is missing",
    )

    traversal = base / "path-traversal.json"
    data = json.loads(VALID_EVIDENCE.read_text(encoding="utf-8"))
    data["artifacts"][0]["path"] = "../outside.txt"
    write_json(traversal, data)
    expect_code(
        "evidence path traversal rejected",
        [sys.executable, str(EVIDENCE_VALIDATOR), str(traversal)],
        1,
        output_must_contain="escapes manifest directory",
    )


def qualify_environment_gate(tmp: Path) -> None:
    env_dir = tmp / "environment"
    env_dir.mkdir()

    expect_code(
        "healthy environment capacity accepted",
        [
            sys.executable,
            str(ENVIRONMENT_GATE),
            "--path",
            str(env_dir),
            "--min-free-bytes",
            "1",
        ],
        0,
        output_must_contain="ENVIRONMENT_GATE=PASS",
    )

    missing = tmp / "missing-environment"
    expect_code(
        "missing environment path rejected",
        [sys.executable, str(ENVIRONMENT_GATE), "--path", str(missing)],
        30,
        output_must_contain="environment path is unavailable",
    )

    expect_code(
        "insufficient disk capacity stops execution",
        [
            sys.executable,
            str(ENVIRONMENT_GATE),
            "--path",
            str(env_dir),
            "--min-free-bytes",
            str(2**63 - 1),
        ],
        31,
        output_must_contain="insufficient free disk",
    )



def qualify_project_bootstrap(tmp: Path) -> None:
    target = tmp / "adoption-target"
    expect_code(
        "project governance bootstrap succeeds",
        [
            sys.executable,
            str(BOOTSTRAP),
            "--project-name",
            "Qualification Project",
            "--repository",
            "owner/qualification-project",
            "--official-branch",
            "main",
            "--destination",
            str(target),
        ],
        0,
        output_must_contain="status=DRAFT_LIVE_VERIFICATION_REQUIRED",
    )

    governance = target / "governance"
    engineering = target / "ENGINEERING"

    expected_paths = {
        "AGENTS.md",
        "governance/GOVERNANCE_LOCK.json",
        "governance/PROJECT_PROFILE.md",
        "governance/project-profile.json",
        "governance/REPOSITORY_ENGINEERING_INSTRUCTIONS.md",
        "governance/ENGINEERING_ENVIRONMENT_CONTRACT.md",
        "governance/RESOURCE_MAP.md",
        "governance/ADOPTION_STATUS.md",
        "ENGINEERING/MASTER_ROADMAP.md",
        "ENGINEERING/REPORTS/MASTER_ENGINEERING_BASELINE_REPORT.md",
        "ENGINEERING/EVIDENCE/README.md",
    }
    actual_paths = {
        str(path.relative_to(target))
        for path in target.rglob("*")
        if path.is_file()
    }
    require(
        expected_paths == actual_paths,
        f"bootstrap files mismatch: expected={expected_paths} actual={actual_paths}",
    )

    require(
        (target / "AGENTS.md").is_file(),
        "bootstrap must create root AGENTS.md for a new project",
    )
    agents_text = (target / "AGENTS.md").read_text(encoding="utf-8")
    require(
        "https://github.com/n923760-rgb/engineering-governance" in agents_text,
        "generated AGENTS.md must point to the central governance repository",
    )
    require(
        "/ENGINEERING/MASTER_ROADMAP.md" in agents_text,
        "generated AGENTS.md must declare the canonical roadmap path",
    )
    require(
        (engineering / "MASTER_ROADMAP.md").is_file(),
        "bootstrap must create canonical ENGINEERING/MASTER_ROADMAP.md",
    )
    require(
        not (governance / "MASTER_ENGINEERING_ROADMAP.md").exists(),
        "bootstrap must not create a competing governance roadmap",
    )

    profile = json.loads((governance / "project-profile.json").read_text(encoding="utf-8"))
    require(profile["project_name"] == "Qualification Project", "bootstrap project name mismatch")
    require(profile["repository"] == "owner/qualification-project", "bootstrap repository mismatch")
    require(profile["official_branch"] == "main", "bootstrap branch mismatch")
    require(
        profile["status"] == "DRAFT_LIVE_VERIFICATION_REQUIRED",
        "bootstrap must not auto-qualify a project",
    )
    require(
        profile.get("execution_environment") is None,
        "bootstrap must not invent execution environment identity",
    )
    require(
        profile.get("verified_execution_capabilities") == [],
        "bootstrap must not invent execution capabilities",
    )
    require(
        profile.get("master_roadmap") == "ENGINEERING/MASTER_ROADMAP.md",
        "bootstrap must use the canonical roadmap path",
    )
    require(
        profile.get("report_location") == "ENGINEERING/REPORTS/",
        "bootstrap must use the canonical report location",
    )
    require(
        profile.get("evidence_location") == "ENGINEERING/EVIDENCE/",
        "bootstrap must use the canonical evidence location",
    )
    print("PASS: generated governance profile remains draft and project-specific")

    expect_code(
        "bootstrap refuses to overwrite governance files",
        [
            sys.executable,
            str(BOOTSTRAP),
            "--project-name",
            "Qualification Project",
            "--repository",
            "owner/qualification-project",
            "--destination",
            str(target),
        ],
        20,
        output_must_contain="refusing to overwrite existing governance files",
    )

    existing_agents_target = tmp / "existing-agents-target"
    existing_agents_target.mkdir()
    existing_agents = existing_agents_target / "AGENTS.md"
    original_agents = "# Existing Project Authority\n\nPreserve this file exactly.\n"
    existing_agents.write_text(original_agents, encoding="utf-8")

    expect_code(
        "bootstrap preserves existing root AGENTS.md",
        [
            sys.executable,
            str(BOOTSTRAP),
            "--project-name",
            "Existing Authority Project",
            "--repository",
            "owner/existing-authority-project",
            "--official-branch",
            "main",
            "--destination",
            str(existing_agents_target),
        ],
        0,
        output_must_contain="agents=preserved_existing",
    )
    require(
        existing_agents.read_text(encoding="utf-8") == original_agents,
        "bootstrap must not overwrite an existing AGENTS.md",
    )
    require(
        (existing_agents_target / "ENGINEERING" / "MASTER_ROADMAP.md").is_file(),
        "bootstrap must continue creating other governance files when AGENTS.md already exists",
    )
    print("PASS: existing project AGENTS.md is preserved")

    invalid = tmp / "invalid-adoption-target"
    expect_code(
        "bootstrap rejects invalid repository identity",
        [
            sys.executable,
            str(BOOTSTRAP),
            "--project-name",
            "Qualification Project",
            "--repository",
            "not-owner-slash-repository",
            "--destination",
            str(invalid),
        ],
        2,
        output_must_contain="repository must use owner/name form",
    )


def qualify_governance_lock(tmp: Path) -> None:
    from unittest.mock import patch
    sys.path.insert(0, str(ROOT / "scripts"))
    from governance_lock import source_state
    with patch("governance_lock.shutil.which", return_value=None):
        require(source_state(ROOT) == (None, None), "missing Git must not invent source attribution")
    print("PASS: unavailable Git leaves source attribution unknown")
    target = tmp / "lock-adoption-target"
    expect_code("high risk bootstrap accepted",
                [sys.executable, str(BOOTSTRAP), "--project-name", "High Risk Fixture",
                 "--repository", "owner/lock-fixture", "--destination", str(target), "--risk-profile", "HIGH"],
                0, output_must_contain="BOOTSTRAP=PASS")
    lock_path = target / "governance" / "GOVERNANCE_LOCK.json"
    original = json.loads(lock_path.read_text())
    require(original["risk_profile"] == "HIGH", "risk profile missing from lock")
    profile = json.loads((target / "governance/project-profile.json").read_text())
    require(profile["risk_profile"] == "HIGH", "risk profile missing from profile")
    command = [sys.executable, str(ROOT / "scripts/verify-governance-lock.py"), str(lock_path),
               "--source", str(ROOT)]
    expect_code("captured governance source hashes accepted", command, 0,
                output_must_contain="GOVERNANCE_LOCK_INTEGRITY=PASS")
    modified = json.loads(json.dumps(original))
    modified["files"]["MASTER_GOVERNANCE.md"] = "0" * 64
    write_json(lock_path, modified)
    expect_code("changed governance source hash rejected", command, 1,
                output_must_contain="source hash mismatch")
    modified = json.loads(json.dumps(original))
    modified["files"].pop("scripts/governance_contracts.py")
    write_json(lock_path, modified)
    expect_code("incomplete governance source lock rejected", command, 1,
                output_must_contain="complete required source set")
    modified = json.loads(json.dumps(original))
    modified["source_commit_sha"] = None
    write_json(lock_path, modified)
    expect_code("draft lock cannot claim clean source qualification",
                command + ["--require-clean-source"], 1,
                output_must_contain="clean exact governance source commit is required")

    source_copy = tmp / "clean-reference-fixture"
    from_source = json.loads(json.dumps(original))
    for name in original["files"]:
        destination = source_copy / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    git(source_copy, "init", "-b", "main")
    git(source_copy, "config", "user.email", "qualification@example.invalid")
    git(source_copy, "config", "user.name", "Governance Qualification")
    git(source_copy, "add", ".")
    git(source_copy, "commit", "-m", "fixture: clean reference source")
    from_source["source_commit_sha"] = git(source_copy, "rev-parse", "HEAD")
    from_source["observed_git_head_sha"] = from_source["source_commit_sha"]
    from_source["source_worktree_dirty"] = False
    write_json(lock_path, from_source)
    clean_command = [sys.executable, str(ROOT / "scripts/verify-governance-lock.py"), str(lock_path),
                     "--source", str(source_copy), "--require-clean-source"]
    expect_code("clean exact adopted source accepted", clean_command, 0,
                output_must_contain="project_adoption_qualified=no")
    (source_copy / "UNRELATED.md").write_text("uncommitted fixture state\n")
    expect_code("dirty reference source cannot pass clean gate", clean_command, 1,
                output_must_contain="clean exact governance source commit is required")



def qualify_pr_state_gate(tmp: Path) -> None:
    pr_dir = tmp / "pr-state"
    pr_dir.mkdir()

    valid_sha = "1234567890abcdef1234567890abcdef12345678"
    valid = {
        "number": 42,
        "state": "open",
        "head": {"sha": valid_sha, "ref": "feature/example"},
        "base": {
            "ref": "main",
            "repo": {"full_name": "owner/project"},
        },
    }
    valid_path = pr_dir / "valid-pr.json"
    write_json(valid_path, valid)

    expect_code(
        "matching PR state accepted",
        [
            sys.executable,
            str(PR_STATE_GATE),
            "--repository",
            "owner/project",
            "--pr-number",
            "42",
            "--expected-head",
            valid_sha,
            "--expected-base",
            "main",
            "--fixture",
            str(valid_path),
        ],
        0,
        output_must_contain="PR_STATE_GATE=PASS",
    )

    expect_code(
        "stale PR head rejected",
        [
            sys.executable,
            str(PR_STATE_GATE),
            "--repository",
            "owner/project",
            "--pr-number",
            "42",
            "--expected-head",
            "0" * 40,
            "--expected-base",
            "main",
            "--fixture",
            str(valid_path),
        ],
        42,
        output_must_contain="PR head mismatch",
    )

    closed = dict(valid)
    closed["state"] = "closed"
    closed_path = pr_dir / "closed-pr.json"
    write_json(closed_path, closed)
    expect_code(
        "unexpected closed PR rejected",
        [
            sys.executable,
            str(PR_STATE_GATE),
            "--repository",
            "owner/project",
            "--pr-number",
            "42",
            "--expected-head",
            valid_sha,
            "--expected-base",
            "main",
            "--fixture",
            str(closed_path),
        ],
        41,
        output_must_contain="PR state mismatch",
    )

    expect_code(
        "wrong PR base rejected",
        [
            sys.executable,
            str(PR_STATE_GATE),
            "--repository",
            "owner/project",
            "--pr-number",
            "42",
            "--expected-head",
            valid_sha,
            "--expected-base",
            "release",
            "--fixture",
            str(valid_path),
        ],
        43,
        output_must_contain="PR base mismatch",
    )

    empty_list = pr_dir / "no-open-pr.json"
    write_json(empty_list, [])
    expect_code(
        "no open PR for work branch accepted",
        [
            sys.executable,
            str(PR_STATE_GATE),
            "--repository",
            "owner/project",
            "--expect-no-open-pr-for-head",
            "feature/example",
            "--fixture",
            str(empty_list),
        ],
        0,
        output_must_contain="open_prs=0",
    )

    conflicting_list = pr_dir / "conflicting-open-pr.json"
    write_json(conflicting_list, [valid])
    expect_code(
        "conflicting open PR for work branch rejected",
        [
            sys.executable,
            str(PR_STATE_GATE),
            "--repository",
            "owner/project",
            "--expect-no-open-pr-for-head",
            "feature/example",
            "--fixture",
            str(conflicting_list),
        ],
        45,
        output_must_contain="conflicting open PR exists",
    )

def qualify_live_gate(tmp: Path) -> None:
    work, expected_head = build_live_gate_fixture(tmp / "live-gate")

    expect_code(
        "clean expected repository state accepted",
        ["bash", str(LIVE_GATE), "main", expected_head, str(tmp / "live-gate" / "remote.git")],
        0,
        cwd=work,
        output_must_contain="LIVE_GATE=PASS",
    )

    expect_code(
        "repository identity mismatch stops mutation",
        ["bash", str(LIVE_GATE), "main", expected_head, "definitely-not-this-remote"],
        20,
        cwd=work,
        output_must_contain="STOP: repository identity mismatch",
    )

    git(work, "checkout", "-b", "feature/qualification")
    expect_code(
        "wrong branch stops mutation",
        ["bash", str(LIVE_GATE), "main", expected_head, str(tmp / "live-gate" / "remote.git")],
        21,
        cwd=work,
        output_must_contain="STOP: wrong branch",
    )

    git(work, "checkout", "main")
    (work / "README.md").write_text("dirty fixture\n", encoding="utf-8")
    expect_code(
        "dirty worktree stops mutation",
        ["bash", str(LIVE_GATE), "main", expected_head, str(tmp / "live-gate" / "remote.git")],
        22,
        cwd=work,
        output_must_contain="STOP: working tree is not clean",
    )

    git(work, "reset", "--hard", "HEAD")
    expect_code(
        "unexpected official HEAD stops mutation",
        ["bash", str(LIVE_GATE), "main", "0" * 40, str(tmp / "live-gate" / "remote.git")],
        23,
        cwd=work,
        output_must_contain="STOP: unexpected official HEAD",
    )

    seed = tmp / "live-gate" / "seed"
    (seed / "ADVANCE.md").write_text("new official fixture state\n", encoding="utf-8")
    git(seed, "add", "ADVANCE.md")
    git(seed, "commit", "-m", "fixture: advance official source")
    git(seed, "push", "origin", "main")
    new_head = git(seed, "rev-parse", "HEAD")
    origin = str(tmp / "live-gate" / "remote.git")
    expect_code("clean stale local baseline rejected",
                ["bash", str(LIVE_GATE), "main", new_head, origin], 24, cwd=work,
                output_must_contain="local HEAD differs")
    git(work, "merge", "--ff-only", "origin/main")
    git(work, "config", "user.email", "qualification@example.invalid")
    git(work, "config", "user.name", "Governance Qualification")
    (work / "LOCAL.md").write_text("local task state\n", encoding="utf-8")
    git(work, "add", "LOCAL.md")
    git(work, "commit", "-m", "fixture: local task")
    expect_code("clean local baseline ahead rejected",
                ["bash", str(LIVE_GATE), "main", new_head, origin], 24, cwd=work,
                output_must_contain="local HEAD differs")
    git(work, "checkout", "-b", "feature/descendant")
    expect_code("task descendant source accepted",
                ["bash", str(LIVE_GATE), "main", new_head, origin, "--task-branch", "feature/descendant"],
                0, cwd=work, output_must_contain="source_mode=task")
    expect_code("repository fragment cannot impersonate full identity",
                ["bash", str(LIVE_GATE), "main", new_head, origin + "-evil",
                 "--task-branch", "feature/descendant"], 20, cwd=work,
                output_must_contain="repository identity mismatch")


def qualify_secret_scanner(tmp: Path) -> None:
    repo = tmp / "secret-scan"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(SECRET_SCANNER, scripts / "scan-secrets.py")
    require(run(["git", "init", "-b", "main", str(repo)]).returncode == 0, "cannot init secret fixture")
    git(repo, "config", "user.email", "qualification@example.invalid")
    git(repo, "config", "user.name", "Governance Qualification")
    (repo / "safe.txt").write_text("no credentials here\n", encoding="utf-8")
    git(repo, "add", "scripts/scan-secrets.py", "safe.txt")
    expect_code(
        "clean tracked text passes secret scan",
        [sys.executable, "scripts/scan-secrets.py"],
        0,
        cwd=repo,
        output_must_contain="PASS:",
    )

    (repo / "unsafe.txt").write_text(
        "api_" + "key=" + "qualificationFakeSecret12345" + "\n",
        encoding="utf-8",
    )
    git(repo, "add", "unsafe.txt")
    expect_code(
        "synthetic secret pattern blocks qualification",
        [sys.executable, "scripts/scan-secrets.py"],
        1,
        cwd=repo,
        output_must_contain="possible secrets detected",
    )


def qualify_complete_workflows(tmp: Path) -> None:
    """Exercise real Git/commands and bound evidence, not an AI-agent sandbox."""
    fixture = tmp / "workflow-fixture"
    fixture.mkdir()
    work, _ = build_live_gate_fixture(fixture)
    seed, remote = fixture / "seed", fixture / "remote.git"
    original_source = "def value():\n    return 1\n"
    corrected_source = "def value():\n    return 2\n"
    (seed / "app.py").write_text(original_source, encoding="utf-8")
    git(seed, "add", "app.py")
    git(seed, "commit", "-m", "fixture: reproducible contract defect")
    git(seed, "push", "origin", "main")
    git(work, "fetch", "origin")
    git(work, "merge", "--ff-only", "origin/main")
    baseline = git(work, "rev-parse", "HEAD")
    environment = "local-disposable-git-workflow-fixture"
    contract_test = [sys.executable, "-B", "-c", "from app import value; assert value() == 2"]
    approved_hashes: dict[str, str] = {}

    def task_packet(directory: Path, task_id: str, task_type: str, actions: list[str]) -> dict:
        directory.mkdir()
        task = json.loads(VALID_TASK.read_text(encoding="utf-8"))
        task.update({
            "task_id": task_id, "title": "Controlled workflow qualification",
            "task_type": task_type, "repository": str(remote),
            "expected_official_head": baseline, "risk_profile": "STANDARD",
            "authority": "Fixture controller authorizes only the listed actions in this disposable repository.",
            "scope": "Diagnose or correct the synthetic value() contract only.",
            "out_of_scope": "Real repositories, external network, merge, release, deployment, and credentials.",
            "task": "Prove the synthetic contract and retain attributable command output.",
            "validation": "Run the real source gate and the deterministic value() assertion.",
            "stop_conditions": "Stop dependent work on source mismatch or invalid authority/evidence.",
            "success_criteria": "Report the actual assertion outcome on the exact tested source.",
            "report_path": None, "requested_actions": actions, "authorized_actions": actions,
            "protected_action_authorizations": {},
        })
        write_json(directory / "approved-task.json", task)
        approved_hashes[task_id] = hashlib.sha256((directory / "approved-task.json").read_bytes()).hexdigest()
        expect_code(f"{task_id} approved task accepted",
                    [sys.executable, str(TASK_VALIDATOR), str(directory / "approved-task.json")], 0)
        return task

    def capture(directory: Path, name: str, command: list[str], cwd: Path, code: int) -> str:
        observed = run(command, cwd)
        require(observed.returncode == code,
                f"workflow command {name}: expected {code}, got {observed.returncode}\n{observed.stderr}")
        relative = name + ".json"
        write_json(directory / relative, {
            "command": command, "cwd": str(cwd), "exit_code": observed.returncode,
            "stdout": observed.stdout, "stderr": observed.stderr,
            "observed_source_sha": git(cwd, "rev-parse", "HEAD"),
        })
        return relative

    def complete(directory: Path, task: dict, tested: str, checks: list[dict], facts: list[str]) -> None:
        require(hashlib.sha256((directory / "approved-task.json").read_bytes()).hexdigest()
                == approved_hashes[task["task_id"]], "approved task changed after fixture issuance")
        artifacts = sorted({name for check in checks for name in check["evidence"]})
        manifest = {
            "task_id": task["task_id"], "source_sha": tested,
            "execution_environment": environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "artifacts": [{
                "path": name,
                "sha256": hashlib.sha256((directory / name).read_bytes()).hexdigest(),
                "size": (directory / name).stat().st_size, "sensitive_data": False,
            } for name in artifacts],
        }
        write_json(directory / "evidence-manifest.json", manifest)
        result = {
            "task_id": task["task_id"], "task_type": task["task_type"],
            "task_packet_ref": "approved-task.json",
            "task_packet_sha256": approved_hashes[task["task_id"]],
            "executor": "deterministic fixture harness (not an AI executor)",
            "execution_environment": environment, "repository": task["repository"],
            "official_branch": "main", "verified_remote_official_head": baseline,
            "exact_tested_head": tested, "authorized_actions": task["authorized_actions"],
            "actions_actually_performed": task["requested_actions"], "validation": checks,
            "facts": facts, "inferences": [], "assumptions": [],
            "residual_risks": ["No real AI-agent isolation or product runtime was qualified."],
            "recommended_next_action": "Review fixture evidence; no merge or release is authorized.",
            "evidence_manifest_ref": "evidence-manifest.json",
        }
        write_json(directory / "result.json", result)
        expect_code(f"{task['task_id']} complete result and retained evidence accepted",
                    [sys.executable, str(RESULT_VALIDATOR), str(directory / "result.json"),
                     "--task", str(directory / "approved-task.json"),
                     "--evidence-manifest", str(directory / "evidence-manifest.json")], 0)

    diagnosis = tmp / "workflow-diagnosis"
    diagnostic_actions = ["read", "inspect_source", "run_validation", "write_report"]
    task = task_packet(diagnosis, "WORKFLOW-DIAGNOSIS", "READ-ONLY DIAGNOSIS", diagnostic_actions)
    require((work / "app.py").read_text() == original_source, "diagnosis fixture source mismatch")
    gate = capture(diagnosis, "source-gate", ["bash", str(LIVE_GATE), "main", baseline, str(remote)], work, 0)
    assertion = capture(diagnosis, "contract-test", contract_test, work, 1)
    require(git(work, "rev-parse", "HEAD") == baseline and not git(work, "status", "--porcelain"),
            "read-only workflow changed source or repository state")
    complete(diagnosis, task, baseline, [
        {"check": "exact baseline source gate", "status": "PASS", "evidence": [gate]},
        {"check": "actual contract reproduction", "status": "FAIL", "evidence": [assertion]},
    ], ["The real assertion failed; diagnosis did not remediate or change source."])
    print("PASS: complete read-only workflow preserves source and reports actual FAIL")

    implementation = tmp / "workflow-implementation"
    actions = diagnostic_actions + ["modify", "edit_source", "commit"]
    task = task_packet(implementation, "WORKFLOW-IMPLEMENTATION", "IMPLEMENTATION", actions)
    executor = tmp / "workflow-executor"
    git(work, "config", "user.email", "qualification@example.invalid")
    git(work, "config", "user.name", "Governance Qualification")
    git(work, "worktree", "add", "-b", "feature/workflow-fixture", str(executor), baseline)
    gate_command = ["bash", str(LIVE_GATE), "main", baseline, str(remote),
                    "--task-branch", "feature/workflow-fixture"]
    preflight = capture(implementation, "preflight", gate_command, executor, 0)
    (executor / "app.py").write_text(corrected_source, encoding="utf-8")
    require(git(executor, "diff", "--name-only") == "app.py", "implementation escaped its bounded source scope")
    git(executor, "add", "app.py")
    git(executor, "commit", "-m", "fixture: correct synthetic contract")
    tested = git(executor, "rev-parse", "HEAD")
    assertion = capture(implementation, "contract-test", contract_test, executor, 0)
    gate = capture(implementation, "source-gate", gate_command, executor, 0)
    require(tested != baseline and not git(executor, "status", "--porcelain"),
            "implementation must test an exact clean changed commit")
    require(git(work, "rev-parse", "HEAD") == baseline and not git(work, "status", "--porcelain")
            and git(remote, "rev-parse", "refs/heads/main") == baseline,
            "isolated implementation changed official or diagnosis source")
    complete(implementation, task, tested, [
        {"check": "pre-mutation source gate", "status": "PASS", "evidence": [preflight]},
        {"check": "declared descendant source gate", "status": "PASS", "evidence": [gate]},
        {"check": "actual corrected contract", "status": "PASS", "evidence": [assertion]},
    ], ["The assertion passed on the exact committed correction; official main was not changed."])
    print("PASS: complete isolated implementation binds actual PASS to approved task and tested commit")

    replay = json.loads((implementation / "result.json").read_text())
    replay["evidence_manifest_ref"] = "../workflow-diagnosis/evidence-manifest.json"
    write_json(implementation / "replayed-result.json", replay)
    expect_code("complete workflow rejects evidence replay from diagnosis",
                [sys.executable, str(RESULT_VALIDATOR), str(implementation / "replayed-result.json"),
                 "--task", str(implementation / "approved-task.json"),
                 "--evidence-manifest", str(diagnosis / "evidence-manifest.json")], 1,
                output_must_contain="evidence manifest does not match result: task_id")

    (seed / "REMOTE.md").write_text("official source advanced independently\n", encoding="utf-8")
    git(seed, "add", "REMOTE.md")
    git(seed, "commit", "-m", "fixture: official source advances")
    git(seed, "push", "origin", "main")
    expect_code("complete workflow stops when official source advances", gate_command, 23,
                cwd=executor, output_must_contain="unexpected official HEAD")
    require(git(executor, "rev-parse", "HEAD") == tested and not git(executor, "status", "--porcelain"),
            "failed source gate changed the tested implementation")


def main() -> None:
    if shutil.which("git") is None:
        raise SystemExit("BLOCKED: git is required for governance qualification")
    with tempfile.TemporaryDirectory(prefix="governance-qualification-") as td:
        tmp = Path(td)
        try:
            qualify_task_packet_validation(tmp)
            qualify_task_policy_boundaries(tmp)
            qualify_result_packet_validation(tmp)
            qualify_evidence_manifest_validation(tmp)
            qualify_environment_gate(tmp)
            qualify_project_bootstrap(tmp)
            qualify_governance_lock(tmp)
            qualify_pr_state_gate(tmp)
            qualify_live_gate(tmp)
            qualify_secret_scanner(tmp)
            qualify_complete_workflows(tmp)
        except QualificationFailure as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            raise SystemExit(1)
    print("PASS: governance qualification suite completed")


if __name__ == "__main__":
    main()
