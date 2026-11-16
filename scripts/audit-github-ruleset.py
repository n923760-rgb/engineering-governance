#!/usr/bin/env python3
"""Read-only, fail-closed audit of ONE GitHub branch ruleset.

This does not verify effective combined organization/branch protections or owner
consent. It never changes repository settings and is safe for offline fixtures.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"


def check_ruleset(data: object, *, branch: str, context: str, min_approvals: int) -> list[tuple[str, str, str]]:
    """Return checks as (key, status, explanation); never interpret missing data as PASS."""
    if not isinstance(data, dict):
        return [("payload", UNKNOWN, "expected a ruleset JSON object")]

    findings: list[tuple[str, str, str]] = []

    def add(key: str, status: str, message: str) -> None:
        findings.append((key, status, message))

    add("target", PASS if data.get("target") == "branch" else FAIL,
        "must target branches")
    add("enforcement", PASS if data.get("enforcement") == "active" else FAIL,
        "must be active (not evaluate or disabled)")

    conditions = data.get("conditions")
    refs = conditions.get("ref_name") if isinstance(conditions, dict) else None
    if not isinstance(refs, dict) or not isinstance(refs.get("include"), list) or not isinstance(refs.get("exclude"), list):
        add("branch_scope", UNKNOWN, "cannot prove target branch is included and not excluded")
    else:
        target_ref = f"refs/heads/{branch}"
        include = refs["include"]
        exclude = refs["exclude"]
        if target_ref in exclude or branch in exclude or "~ALL" in exclude:
            add("branch_scope", FAIL, "branch is explicitly excluded")
        elif target_ref in include or "~ALL" in include:
            # Wildcard exclusions are not safe to interpret with Python fnmatch:
            # GitHub pattern semantics can differ.
            if any(isinstance(x, str) and ("*" in x or "?" in x or x == "~DEFAULT_BRANCH") for x in exclude):
                add("branch_scope", UNKNOWN, "potential wildcard/default-branch exclusion")
            else:
                add("branch_scope", PASS, "explicit branch inclusion without ambiguous exclusions")
        else:
            add("branch_scope", UNKNOWN, "no explicit inclusion; wildcard or ~DEFAULT_BRANCH needs live verification")

    rules = data.get("rules")
    if not isinstance(rules, list):
        add("rules", UNKNOWN, "rules array missing")
        return findings
    by_type = {}
    for rule in rules:
        if isinstance(rule, dict) and isinstance(rule.get("type"), str):
            by_type.setdefault(rule["type"], []).append(rule)

    for rule_name in ("deletion", "non_fast_forward"):
        add(rule_name, PASS if rule_name in by_type else FAIL,
            f"{rule_name} protection required")

    pr = by_type.get("pull_request", [])
    if len(pr) != 1:
        add("pr_reviews", FAIL, "exactly one pull_request rule required")
        add("stale_reviews", FAIL, "cannot inspect dismiss_stale_reviews_on_push")
    else:
        params = pr[0].get("parameters")
        if not isinstance(params, dict):
            add("pr_reviews", UNKNOWN, "pull_request parameters unavailable")
            add("stale_reviews", UNKNOWN, "pull_request parameters unavailable")
        else:
            n = params.get("required_approving_review_count")
            add("pr_reviews", PASS if isinstance(n, int) and not isinstance(n, bool) and n >= min_approvals else FAIL,
                f"required approvals: {n!r}; minimum: {min_approvals}")
            v = params.get("dismiss_stale_reviews_on_push")
            add("stale_reviews", PASS if v is True else FAIL,
                "stale approvals must be dismissed on new pushes")

    check_rules = by_type.get("required_status_checks", [])
    if len(check_rules) != 1:
        add("status_check", FAIL, f"required_status_checks rule missing; expected {context!r}")
        add("up_to_date", FAIL, "cannot verify strict status-check policy")
    else:
        params = check_rules[0].get("parameters")
        if not isinstance(params, dict):
            add("status_check", UNKNOWN, "status-check parameters unavailable")
            add("up_to_date", UNKNOWN, "status-check parameters unavailable")
        else:
            checks = params.get("required_status_checks")
            names = {x.get("context") for x in checks if isinstance(x, dict)} if isinstance(checks, list) else set()
            add("status_check", PASS if context in names else FAIL,
                f"required context {context!r} must be present")
            add("up_to_date", PASS if params.get("strict_required_status_checks_policy") is True else FAIL,
                "required checks must be verified against up-to-date branch")

    bypass = data.get("bypass_actors", None)
    if not isinstance(bypass, list):
        add("bypass", UNKNOWN, "bypass actors not returned; cannot prove absence")
    else:
        add("bypass", PASS if not bypass else FAIL,
            "ruleset must have no bypass actors")
    return findings


def load_ruleset(args: argparse.Namespace) -> object:
    if args.fixture:
        return json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    if not REPO_RE.fullmatch(args.repository or ""):
        raise ValueError("--repository must be owner/name for live queries")
    if not args.ruleset_id or args.ruleset_id <= 0:
        raise ValueError("--ruleset-id must be a positive integer for live queries")
    url = f"https://api.github.com/repos/{args.repository}/rulesets/{args.ruleset_id}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "master-engineering-ruleset-audit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", help="local full ruleset JSON for offline qualification")
    mode.add_argument("--repository", help="owner/name for a live read-only GitHub query")
    parser.add_argument("--ruleset-id", type=int, help="GitHub ruleset ID (live mode)")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--required-context", default="Validate Master Engineering System")
    parser.add_argument("--min-approvals", type=int, default=1)
    args = parser.parse_args()
    if not args.branch or not re.fullmatch(r"[A-Za-z0-9._/-]+", args.branch) or args.min_approvals < 1 or not args.required_context:
        parser.error("invalid branch, status-check context, or min-approvals")
    if args.fixture and args.ruleset_id is not None:
        parser.error("--ruleset-id only applies to live mode")
    try:
        data = load_ruleset(args)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(f"RULESET_AUDIT=UNKNOWN: cannot obtain trusted ruleset data ({type(exc).__name__})", file=sys.stderr)
        return 2
    findings = check_ruleset(data, branch=args.branch, context=args.required_context,
                             min_approvals=args.min_approvals)
    for key, status, message in findings:
        print(f"{key}: {status} — {message}")
    result = FAIL if any(status == FAIL for _, status, _ in findings) else (
        UNKNOWN if any(status == UNKNOWN for _, status, _ in findings) else PASS
    )
    print(f"RULESET_AUDIT={result}")
    print("scope=single_ruleset_only; this is NOT a proof of owner authorization or combined effective protections")
    return {PASS: 0, FAIL: 1, UNKNOWN: 2}[result]


if __name__ == "__main__":
    raise SystemExit(main())
