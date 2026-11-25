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
            "shared process namespace": {"pid": "service:production"},
            "shared container process namespace": {"pid": "container:production"},
            "shared IPC namespace": {"ipc": "service:production"},
            "custom user namespace": {"userns_mode": "container:production"},
            "dependent service": {"depends_on": ["production"]},
            "other network": {"networks": ["production"]},
            "replicated executor": {"scale": 20},
            "deploy replicas": {"deploy": {"replicas": 20}},
            "extra writable tmpfs": {"tmpfs": ["/tmp"]},
            "remote log destination": {"logging": {"driver": "syslog"}},
            "container name collision": {"container_name": "production"},
            "host cgroup namespace": {"cgroup": "host"},
            "bool CPU limit": {"cpus": True},
            "security option override": {"security_opt": ["no-new-privileges:true", "no-new-privileges:false"]},
            "security option alternative": {"security_opt": ["no-new-privileges:true", "apparmor:unconfined"]},
            "secrets": {"secrets": [{"source": "prod-secret"}]},
            "restart daemon": {"restart": "unless-stopped"},
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                data = copy.deepcopy(BASE)
                data["services"]["hermes-executor"].update(change)
                self.run_case(data, False)

    def test_reject_volume_level_escape_hatches(self):
        cases = {
            "implicit volume": None,
            "external volume": {"name": "agent-exec-scratch", "external": True},
            "host bind via driver options": {"name": "agent-exec-scratch", "driver": "local", "driver_opts": {"type": "none", "o": "bind", "device": "/srv/production"}},
            "alternate volume name": {"name": "prod-postgres", "driver": "local"},
            "non-local driver": {"name": "agent-exec-scratch", "driver": "other"},
        }
        for name, val in cases.items():
            with self.subTest(name=name):
                data = copy.deepcopy(BASE)
                if val is None:
                    data.pop("volumes")
                else:
                    data["volumes"]["agent-exec-scratch"] = val
                self.run_case(data, False)

    def test_reject_extra_compose_resources(self):
        extra_service = copy.deepcopy(BASE)
        extra_service["services"]["production"] = {
            "image": "example.invalid/production:latest",
            "privileged": True,
        }
        self.run_case(extra_service, False)

        extra_volume = copy.deepcopy(BASE)
        extra_volume["volumes"]["production"] = {
            "name": "prod-postgres", "driver": "local"
        }
        self.run_case(extra_volume, False)

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
