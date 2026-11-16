"""Adversarial, offline tests for a vendor-neutral agent executor preflight."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate-agent-sandbox.py"
BASE = {
    "volumes": {"agent-exec-scratch": {"name": "agent-exec-scratch", "driver": "local"}},
    "services": {"hermes-executor": {
        "image": "example.invalid/agent@sha256:" + "a" * 64,
        "user": "10001:10001",
        "read_only": True,
        "privileged": False,
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges:true"],
        "network_mode": "none",
        "mem_limit": "768m",
        "cpus": 1,
        "pids_limit": 64,
        "restart": "no",
        "volumes": [{"type": "volume", "source": "agent-exec-scratch", "target": "/workspace"}],
    }}
}


class AgentSandboxTest(unittest.TestCase):
    def run_case(self, data, allowed):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "compose.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--service", "hermes-executor",
                 "--scratch-volume", "agent-exec-scratch"],
                text=True, capture_output=True, check=False,
            )
        if allowed:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("STATIC_PREFLIGHT=PASS", result.stdout)
            self.assertIn("RUNTIME_QUALIFICATION=NOT_RUN", result.stdout)
            self.assertIn("AUTHORIZATION=NOT_GRANTED", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("STATIC_PREFLIGHT=BLOCKED", result.stdout + result.stderr)

    def test_valid_disposable_executor(self):
        self.run_case(BASE, True)

    def test_fail_closed(self):
        changes = {
            "host network": {"network_mode": "host"},
            "default network": {"network_mode": None},
            "root": {"user": "0:0"},
            "named root": {"user": "root"},
            "no immutable image": {"image": "example/agent:latest"},
            "privileged": {"privileged": True},
            "no privilege drop": {"cap_drop": []},
            "added capability": {"cap_add": ["SYS_ADMIN"]},
            "disabled no-new-privileges": {"security_opt": ["no-new-privileges:false"]},
            "seccomp unconfined": {"security_opt": ["no-new-privileges:true", "seccomp=unconfined"]},
            "writable host root": {"read_only": False},
            "unbounded memory": {"mem_limit": None},
            "excessive memory": {"mem_limit": "2g"},
            "unbounded cpus": {"cpus": None},
            "excessive cpus": {"cpus": 3},
            "unbounded pids": {"pids_limit": None},
            "docker socket bind": {"volumes": [{"type": "bind", "source": "/var/run/docker.sock", "target": "/workspace"}]},
            "unexpected volume": {"volumes": [{"type": "volume", "source": "prod-backup", "target": "/workspace"}]},
            "credentials": {"environment": {"OPENAI_API_KEY": "synthetic-test-value"}},
            "published port": {"ports": [{"target": 1234, "published": "1234"}]},
            "host pid": {"pid": "host"},
            "host user namespace": {"userns_mode": "host"},
            "secrets": {"secrets": [{"source": "prod-secret"}]},
            "restart daemon": {"restart": "unless-stopped"},
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                data = copy.deepcopy(BASE)
                data["services"]["hermes-executor"].update(change)
                self.run_case(data, False)

    def test_no_service(self):
        self.run_case({"services": {}}, False)

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--service", "hermes-executor",
                 "--scratch-volume", "agent-exec-scratch"],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED", result.stderr)


if __name__ == "__main__":
    unittest.main()
