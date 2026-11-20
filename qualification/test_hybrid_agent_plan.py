"""Offline adversarial tests of the API-first hybrid agent plan contract."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-hybrid-agent-plan.py"
EXAMPLE = ROOT / "examples" / "hybrid-agent-plan.example.json"


class HybridAgentPlanTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def run_case(self, value, allowed, *, raw=False):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "plan.json"
            path.write_text(value if raw else json.dumps(value), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                    capture_output=True, text=True, check=False)
        if allowed:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("HYBRID_PREFLIGHT=PASS", result.stdout)
            self.assertIn("RUNTIME_ENFORCEMENT=NOT_VERIFIED", result.stdout)
            self.assertIn("HERMES_ACTIVATION=DISABLED", result.stdout)
            self.assertIn("DEPLOYMENT=NOT_AUTHORIZED", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("HYBRID_PREFLIGHT=BLOCKED", result.stdout + result.stderr)

    def test_reference_example(self):
        self.run_case(self.base, True)

    def test_disallowed_root_and_model_fields(self):
        for name, key, value in (
            ("surprise network override", "network_override", "all"),
            ("raw provider key", "api_key", "synthetic-not-a-secret"),
            ("unreviewed model toolset", "enable_tools", True),
        ):
            with self.subTest(name=name):
                p = copy.deepcopy(self.base)
                p["model_api"][key] = value
                self.run_case(p, False)
        p = copy.deepcopy(self.base)
        p["runtime_enabled"] = True
        self.run_case(p, False)

    def test_unsafe_endpoints(self):
        for endpoint in (
            "http://api.example.invalid/v1",
            "https://localhost:8642/v1",
            "https://127.0.0.1/v1",
            "https://10.0.0.5/v1",
            "https://api.local/v1",
            "https://api.internal/v1",
            "https://user:pass@api.example.invalid/v1",
            "https://api.example.invalid/v1?token=synthetic",
            "https://api.example.invalid/v1#fragment",
            "https://api.example.invalid:8080/v1",
            "https://api.example.invalid/v1\nInjected:synthetic",
            "https://api.example.invalid/v1\t",
            "https://api.example.invalid/v1%0d%0aInjected",
            "https://api.example.invalid/v1%5c",
            "https://api.example.invalid/v1%252e",
            "https://api.example.invalid/v1\\suffix",
            "https://api.example.invalid/v1 space",
            "file:///etc/passwd",
            "https://invalid",
            5,
            None,
        ):
            with self.subTest(endpoint=endpoint):
                p = copy.deepcopy(self.base)
                p["model_api"]["base_url"] = endpoint
                self.run_case(p, False)

    def test_sandbox_and_approval_gates(self):
        modifications = (
            ("hermes", "mode", "api_server"),
            ("hermes", "requires_separate_runtime_qualification", False),
            ("permissions", "isolated_worktree", False),
            ("permissions", "production_read", True),
            ("permissions", "production_write", True),
            ("permissions", "docker_socket", True),
            ("permissions", "host_secrets", True),
            ("permissions", "main_branch_write", True),
            ("protected_actions", "merge", "auto"),
            ("protected_actions", "deploy", "auto"),
            ("protected_actions", "release", "auto"),
            ("protected_actions", "credential_changes", "auto"),
            ("protected_actions", "policy_changes", "auto"),
            ("model_api", "credentials", "inline_key"),
            ("model_api", "kind", "remote_agent_with_tools"),
        )
        for section, key, value in modifications:
            with self.subTest(section=section, key=key, value=value):
                p = copy.deepcopy(self.base)
                p[section][key] = value
                self.run_case(p, False)

    def test_limits(self):
        changes = (
            ("max_parallel_tasks", 0),
            ("max_parallel_tasks", 2),
            ("max_parallel_tasks", True),
            ("max_tool_calls", 0),
            ("max_tool_calls", 999),
            ("max_task_seconds", 1801),
            ("max_cost_usd", "0"),
            ("max_cost_usd", "5.01"),
            ("max_cost_usd", 0.50),
            ("max_cost_usd", "1e9"),
        )
        for key, value in changes:
            with self.subTest(key=key, value=value):
                p = copy.deepcopy(self.base)
                p["limits"][key] = value
                self.run_case(p, False)

    def test_missing_fields_and_ambiguous_json(self):
        p = copy.deepcopy(self.base)
        del p["limits"]["max_parallel_tasks"]
        self.run_case(p, False)
        p = copy.deepcopy(self.base)
        p["deployment"] = "live"
        self.run_case(p, False)
        self.run_case('{"schema_version": 1, "schema_version": 2}', False, raw=True)
        self.run_case("not json", False, raw=True)
        self.run_case(self.base | {"schema_version": True}, False)


if __name__ == "__main__":
    unittest.main()
