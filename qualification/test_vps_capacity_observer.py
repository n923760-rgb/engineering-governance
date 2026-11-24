"""Offline qualification of the read-only Linux host snapshot."""
from __future__ import annotations

import importlib.util
import io
import json
import stat
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "observe-vps-capacity.py"
spec = importlib.util.spec_from_file_location("capacity_observer", SCRIPT)
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)


class CapacityObserverTests(unittest.TestCase):
    def test_memory_parser_returns_only_explicit_counters(self):
        sample = "\n".join([
            "MemTotal:        8192000 kB",
            "MemAvailable:    4096000 kB",
            "SwapTotal:       1048576 kB",
            "SwapFree:        524288 kB",
            "SensitiveHostLabel: possible-secret-value",
        ])
        result = observer.parse_meminfo(sample)
        self.assertEqual(result, {
            "total_mib": 8000, "available_mib": 4000,
            "swap_total_mib": 1024, "swap_free_mib": 512,
        })
        self.assertNotIn("possible-secret-value", json.dumps(result))

    def test_missing_required_memory_is_unknown(self):
        with mock.patch.object(observer.Path, "read_text", return_value="MemTotal: 10 kB"):
            self.assertEqual(observer.read_memory()["status"], "UNKNOWN")

    def test_docker_status_aggregates_without_disclosing_names(self):
        result = observer.docker_status_counts(
            "Up 20 seconds (healthy)\nUp 3 hours (unhealthy)\n"
            "Up 1 minute (health: starting)\nUp 4 days\n"
        )
        self.assertEqual(result, {
            "status": "OBSERVED", "running_containers": 4,
            "unhealthy": 1, "health_starting": 1, "health_unreported": 1,
        })

    def test_docker_query_is_local_bounded_and_read_only(self):
        result = SimpleNamespace(returncode=0, stdout="Up 1 hour (healthy)\n",
                                 stderr="PRIVATE_TOKEN=synthetic-do-not-print")
        with mock.patch.object(observer.Path, "stat",
                               return_value=SimpleNamespace(st_mode=stat.S_IFSOCK)), \
             mock.patch.object(observer.shutil, "which", return_value="/usr/bin/docker"), \
             mock.patch.object(observer.subprocess, "run", return_value=result) as run:
            data = observer.observe_local_docker()
            self.assertEqual(data["status"], "OBSERVED")
            self.assertEqual(data["running_containers"], 1)
            self.assertNotIn("synthetic-do-not-print", json.dumps(data))
            args, kwargs = run.call_args
            self.assertEqual(args[0], [
                "/usr/bin/docker", "--host", "unix:///var/run/docker.sock",
                "ps", "--format", "{{.Status}}",
            ])
            self.assertEqual(kwargs["timeout"], 6)
            self.assertEqual(kwargs["env"]["DOCKER_CONFIG"], "/nonexistent")
            self.assertFalse(kwargs["check"])

    def test_docker_failure_does_not_reveal_stderr(self):
        result = SimpleNamespace(returncode=1, stdout="",
                                 stderr="PAT=synthetic-untrusted-log")
        with mock.patch.object(observer.Path, "stat",
                               return_value=SimpleNamespace(st_mode=stat.S_IFSOCK)), \
             mock.patch.object(observer.shutil, "which", return_value="/usr/bin/docker"), \
             mock.patch.object(observer.subprocess, "run", return_value=result):
            data = observer.observe_local_docker()
            self.assertEqual(data["status"], "UNKNOWN")
            self.assertNotIn("synthetic-untrusted-log", json.dumps(data))

    def test_docker_timeout_and_missing_socket_are_unknown(self):
        with mock.patch.object(observer.Path, "stat", side_effect=FileNotFoundError):
            self.assertEqual(observer.observe_local_docker()["status"], "UNKNOWN")
        with mock.patch.object(observer.Path, "stat",
                               return_value=SimpleNamespace(st_mode=stat.S_IFSOCK)), \
             mock.patch.object(observer.shutil, "which", return_value="/usr/bin/docker"), \
             mock.patch.object(observer.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired("docker", 6)):
            self.assertEqual(observer.observe_local_docker()["status"], "UNKNOWN")

    def test_partial_capacity_is_not_runtime_qualification(self):
        with mock.patch.object(observer, "read_memory", return_value={"status": "OBSERVED"}), \
             mock.patch.object(observer, "read_disk", return_value={"status": "OBSERVED"}), \
             mock.patch.object(observer, "observe_local_docker",
                               return_value={"status": "UNKNOWN"}), \
             mock.patch.object(observer.os, "cpu_count", return_value=4), \
             mock.patch.object(observer.os, "getloadavg", return_value=(1.5, 0.5, 0.2)):
            data = observer.collect("/")
            self.assertEqual(data["snapshot_status"], "PARTIAL")
            self.assertEqual(data["logical_cpus"], 4)
            self.assertEqual(data["agent_runtime_qualification"], "NOT_RUN")
            self.assertEqual(data["capacity_approval"], "NOT_GRANTED")
            self.assertNotIn("PASS", json.dumps(data))

    def test_collect_does_not_require_docker_access(self):
        with mock.patch.object(observer, "observe_local_docker",
                               return_value={"status": "UNKNOWN", "reason": "no socket"}):
            data = observer.collect("/")
            self.assertIn(data["snapshot_status"], ("PARTIAL", "OBSERVED"))


if __name__ == "__main__":
    unittest.main()
