#!/usr/bin/env python3
"""Verify exact repository identity and baseline/task source using Git."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


def stop(message: str, code: int) -> None:
    print(f"STOP: {message}", file=sys.stderr)
    raise SystemExit(code)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], text=True, capture_output=True)
    if result.returncode:
        # Git output may contain credential-bearing URLs; report the operation only.
        stop("Git operation failed: " + args[0], 11)
    return result.stdout.strip()


def repository_identity(value: str) -> str:
    if "://" in value:
        parsed = urlsplit(value)
        if parsed.scheme == "file":
            return str(Path(parsed.path).resolve())
        if not parsed.hostname:
            stop("invalid repository URL", 2)
        host = parsed.hostname.lower()
        path = parsed.path.strip("/")
        port = f":{parsed.port}" if parsed.port else ""
    elif re.fullmatch(r"[^/@:]+@[^/:]+:.+", value):
        authority, path = value.split(":", 1)
        host = authority.split("@", 1)[1].lower()
        port = ""
    elif re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        host, path, port = "github.com", value, ""
    else:
        return str(Path(value).resolve())
    if path.endswith(".git"):
        path = path[:-4]
    if host == "github.com":
        path = path.lower()
    return host + port + "/" + path.strip("/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("official_branch")
    parser.add_argument("expected_remote_head")
    parser.add_argument("expected_repository", help="Exact owner/repo, repository URL, or local fixture path.")
    parser.add_argument("--task-branch", help="Use task mode on this branch; the official source must be its ancestor.")
    args = parser.parse_args()
    if shutil.which("git") is None:
        stop("git not found", 10)
    if not SHA_RE.fullmatch(args.expected_remote_head):
        stop("expected remote HEAD must be a full Git SHA", 2)
    if args.official_branch.startswith("-"):
        stop("invalid official branch", 2)
    git("check-ref-format", "--branch", args.official_branch)
    git("rev-parse", "--is-inside-work-tree")
    try:
        actual_identity = repository_identity(git("remote", "get-url", "origin"))
        expected_identity = repository_identity(args.expected_repository)
    except ValueError:
        stop("invalid repository URL", 2)
    if actual_identity != expected_identity:
        stop("repository identity mismatch", 20)
    branch = git("branch", "--show-current")
    if branch != (args.task_branch or args.official_branch):
        stop("wrong branch", 21)
    if args.task_branch == args.official_branch:
        stop("task branch must differ from official branch", 2)
    if git("status", "--porcelain"):
        stop("working tree is not clean", 22)
    git("fetch", "--quiet", "origin", args.official_branch)
    remote_head = git("rev-parse", "FETCH_HEAD")
    local_head = git("rev-parse", "HEAD")
    if remote_head != args.expected_remote_head:
        stop("unexpected official HEAD", 23)
    if args.task_branch:
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", remote_head, local_head],
            capture_output=True,
        )
        if ancestry.returncode:
            stop("task source does not descend from expected official HEAD", 24)
    elif local_head != remote_head:
        stop("local HEAD differs from expected official HEAD", 24)
    print("LIVE_GATE=PASS")
    print(f"repository={actual_identity}")
    print(f"official_branch={args.official_branch}")
    print(f"remote_head={remote_head}")
    print(f"local_head={local_head}")
    print("source_mode=" + ("task" if args.task_branch else "baseline"))
    print("working_tree=clean")


if __name__ == "__main__":
    main()
