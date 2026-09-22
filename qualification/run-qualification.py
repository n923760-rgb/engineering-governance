#!/usr/bin/env python3
"""Adversarial qualification tests for governance safety, authority, and evidence."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE_GATE = ROOT / "scripts" / "verify-repository-state.sh"
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
            qualify_live_gate(tmp)
            qualify_secret_scanner(tmp)
        except QualificationFailure as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            raise SystemExit(1)
    print("PASS: governance qualification suite completed")


if __name__ == "__main__":
    main()
