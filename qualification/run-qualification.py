#!/usr/bin/env python3
"""Adversarial qualification tests for governance safety, authority, evidence, and environment gates."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

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
        output_must_contain="missing required fields",
    )

    bad_sha = tmp / "task-bad-sha.json"
    data = json.loads(VALID_TASK.read_text(encoding="utf-8"))
    data["expected_official_head"] = "not-a-sha"
    write_json(bad_sha, data)
    expect_code(
        "malformed expected SHA rejected",
        [sys.executable, str(TASK_VALIDATOR), str(bad_sha)],
        1,
        output_must_contain="must look like a Git SHA",
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
    data["protected_action_authorizations"]["merge"] = {
        "source": "CURRENT_OWNER_INSTRUCTION",
        "reference": "owner explicitly authorized merge for this bounded task",
    }
    write_json(protected_with_owner, data)
    expect_code(
        "protected action with explicit owner authorization accepted",
        [sys.executable, str(TASK_VALIDATOR), str(protected_with_owner)],
        0,
        output_must_contain="VALID:",
    )


def qualify_result_packet_validation(tmp: Path) -> None:
    expect_code(
        "valid result packet accepted",
        [sys.executable, str(RESULT_VALIDATOR), str(VALID_RESULT)],
        0,
        output_must_contain="VALID:",
    )

    pass_without_evidence = tmp / "result-pass-without-evidence.json"
    data = json.loads(VALID_RESULT.read_text(encoding="utf-8"))
    data["validation"][0]["evidence"] = []
    write_json(pass_without_evidence, data)
    expect_code(
        "PASS without evidence rejected",
        [sys.executable, str(RESULT_VALIDATOR), str(pass_without_evidence)],
        1,
        output_must_contain="requires meaningful evidence",
    )

    not_run_without_reason = tmp / "result-not-run-without-reason.json"
    data = json.loads(VALID_RESULT.read_text(encoding="utf-8"))
    data["validation"][1].pop("reason")
    write_json(not_run_without_reason, data)
    expect_code(
        "NOT RUN without reason rejected",
        [sys.executable, str(RESULT_VALIDATOR), str(not_run_without_reason)],
        1,
        output_must_contain="requires a reason",
    )

    performed_without_authority = tmp / "result-performed-without-authority.json"
    data = json.loads(VALID_RESULT.read_text(encoding="utf-8"))
    data["actions_actually_performed"].append("merge")
    write_json(performed_without_authority, data)
    expect_code(
        "performed action outside authority rejected",
        [sys.executable, str(RESULT_VALIDATOR), str(performed_without_authority)],
        1,
        output_must_contain="actions actually performed exceed authorization: merge",
    )


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
        ["bash", str(LIVE_GATE), "main", expected_head, "remote.git"],
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
        ["bash", str(LIVE_GATE), "main", expected_head, "remote.git"],
        21,
        cwd=work,
        output_must_contain="STOP: wrong branch",
    )

    git(work, "checkout", "main")
    (work / "README.md").write_text("dirty fixture\n", encoding="utf-8")
    expect_code(
        "dirty worktree stops mutation",
        ["bash", str(LIVE_GATE), "main", expected_head, "remote.git"],
        22,
        cwd=work,
        output_must_contain="STOP: working tree is not clean",
    )

    git(work, "reset", "--hard", "HEAD")
    expect_code(
        "unexpected official HEAD stops mutation",
        ["bash", str(LIVE_GATE), "main", "0" * 40, "remote.git"],
        23,
        cwd=work,
        output_must_contain="STOP: unexpected official HEAD",
    )


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


def main() -> None:
    if shutil.which("git") is None:
        raise SystemExit("BLOCKED: git is required for governance qualification")
    with tempfile.TemporaryDirectory(prefix="governance-qualification-") as td:
        tmp = Path(td)
        try:
            qualify_task_packet_validation(tmp)
            qualify_result_packet_validation(tmp)
            qualify_evidence_manifest_validation(tmp)
            qualify_environment_gate(tmp)
            qualify_project_bootstrap(tmp)
            qualify_pr_state_gate(tmp)
            qualify_live_gate(tmp)
            qualify_secret_scanner(tmp)
        except QualificationFailure as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            raise SystemExit(1)
    print("PASS: governance qualification suite completed")


if __name__ == "__main__":
    main()
