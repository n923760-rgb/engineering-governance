"""Offline adversarial tests for the independent GitHub ruleset audit gate."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit-github-ruleset.py"
spec = importlib.util.spec_from_file_location("github_ruleset_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def valid_ruleset() -> dict:
    return {
        "target": "branch", "enforcement": "active", "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
        "rules": [
            {"type": "deletion"}, {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
            }},
            {"type": "required_status_checks", "parameters": {
                "strict_required_status_checks_policy": True,
                "required_status_checks": [{"context": "Validate Master Engineering System"}],
            }},
        ],
    }


class RulesetQualification(unittest.TestCase):
    def audit(self, payload: object):
        return module.check_ruleset(payload, branch="main",
                                    context="Validate Master Engineering System", min_approvals=1)

    def assert_gate(self, payload: object, key: str, expected: str) -> None:
        checks = {name: state for name, state, _ in self.audit(payload)}
        self.assertEqual(checks[key], expected)

    def test_approved_baseline(self):
        self.assertTrue(all(status == "PASS" for _, status, _ in self.audit(valid_ruleset())))

    def test_zero_reviews_rejected(self):
        d = valid_ruleset()
        d["rules"][2]["parameters"]["required_approving_review_count"] = 0
        self.assert_gate(d, "pr_reviews", "FAIL")

    def test_stale_approvals_rejected(self):
        d = valid_ruleset()
        d["rules"][2]["parameters"]["dismiss_stale_reviews_on_push"] = False
        self.assert_gate(d, "stale_reviews", "FAIL")

    def test_bypass_actor_rejected(self):
        d = valid_ruleset()
        d["bypass_actors"] = [{"actor_id": 1, "actor_type": "Team"}]
        self.assert_gate(d, "bypass", "FAIL")

    def test_missing_bypass_is_unknown(self):
        d = valid_ruleset()
        del d["bypass_actors"]
        self.assert_gate(d, "bypass", "UNKNOWN")

    def test_disabled_or_evaluate_rejected(self):
        for enforcement in ("disabled", "evaluate", None):
            with self.subTest(enforcement=enforcement):
                d = valid_ruleset()
                d["enforcement"] = enforcement
                self.assert_gate(d, "enforcement", "FAIL")

    def test_other_branch_cannot_pass(self):
        d = valid_ruleset()
        d["conditions"]["ref_name"]["include"] = ["refs/heads/dev"]
        self.assert_gate(d, "branch_scope", "UNKNOWN")

    def test_excluded_branch_rejected(self):
        d = valid_ruleset()
        d["conditions"]["ref_name"]["exclude"] = ["refs/heads/main"]
        self.assert_gate(d, "branch_scope", "FAIL")

    def test_wildcard_exclusion_is_unknown(self):
        d = valid_ruleset()
        d["conditions"]["ref_name"]["exclude"] = ["refs/heads/m*"]
        self.assert_gate(d, "branch_scope", "UNKNOWN")

    def test_missing_rules_rejected(self):
        d = valid_ruleset()
        d["rules"] = []
        self.assert_gate(d, "pr_reviews", "FAIL")
        self.assert_gate(d, "status_check", "FAIL")

    def test_missing_required_context_rejected(self):
        d = valid_ruleset()
        d["rules"][-1]["parameters"]["required_status_checks"] = [{"context": "Other"}]
        self.assert_gate(d, "status_check", "FAIL")

    def test_non_strict_status_rejected(self):
        d = valid_ruleset()
        d["rules"][-1]["parameters"]["strict_required_status_checks_policy"] = False
        self.assert_gate(d, "up_to_date", "FAIL")

    def test_invalid_object_unknown(self):
        self.assert_gate([], "payload", "UNKNOWN")

    def test_offline_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "rules.json"
            for count, expected in ((1, 0), (0, 1)):
                with self.subTest(count=count):
                    d = valid_ruleset()
                    d["rules"][2]["parameters"]["required_approving_review_count"] = count
                    fixture.write_text(json.dumps(d), encoding="utf-8")
                    p = subprocess.run([sys.executable, str(SCRIPT), "--fixture", str(fixture)],
                                       capture_output=True, text=True)
                    self.assertEqual(p.returncode, expected, p.stderr)
                    self.assertIn("RULESET_AUDIT=" + ("PASS" if count else "FAIL"), p.stdout)


if __name__ == "__main__":
    unittest.main()
