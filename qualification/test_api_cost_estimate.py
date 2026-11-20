"""Offline adversarial qualification for task cost estimates."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("api_cost", ROOT / "scripts" / "estimate-api-task-cost.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CostEstimateTests(unittest.TestCase):
    def setUp(self):
        self.example = json.loads((ROOT / "examples" / "api-cost-estimate.synthetic.json")
                                  .read_text(encoding="utf-8"))

    def test_fixture_is_offline_and_within_cap(self):
        result = module.estimate(self.example)
        self.assertTrue(result["within_declared_limits"])
        self.assertEqual(result["estimated_cost_usd"], "0.00090000")
        self.assertEqual(result["source_type"], "synthetic_fixture")
        self.assertEqual(result["api_calls"], "NONE")
        self.assertEqual(result["runtime_enforcement"], "NOT_PERFORMED")
        self.assertEqual(result["provider_billing"], "NOT_VERIFIED")

    def test_over_cap_is_not_a_pass(self):
        packet = copy.deepcopy(self.example)
        packet["limits"]["max_task_cost_usd"] = "0.0008"
        self.assertEqual(module.estimate(packet)["api_cost_estimate"], "OVER_CAP")
        packet = copy.deepcopy(self.example)
        packet["limits"]["max_total_tokens"] = 899
        self.assertFalse(module.estimate(packet)["within_declared_limits"])

    def test_cost_precision_not_rounded_down(self):
        packet = copy.deepcopy(self.example)
        # 900 tokens at 1.00000001 USD/M costs just over $0.0009;
        # a displayed rounded value must never turn the overage into PASS.
        packet["rates_usd_per_million"] = {"input": "1.00000001", "output": "1.00000001"}
        packet["limits"]["max_task_cost_usd"] = "0.0009"
        result = module.estimate(packet)
        self.assertFalse(result["within_declared_limits"])
        self.assertEqual(result["api_cost_estimate"], "OVER_CAP")
        packet["limits"]["max_task_cost_usd"] = "0.001"
        self.assertTrue(module.estimate(packet)["within_declared_limits"])

    def test_reject_untrusted_usage(self):
        for section, name, val in (
            ("tokens", "input", -1),
            ("tokens", "input", True),
            ("tokens", "input", 3.14),
            ("tokens", "output", 200000),
            ("rates_usd_per_million", "input", 0),
            ("rates_usd_per_million", "input", "1e6"),
            ("rates_usd_per_million", "output", "0"),
            ("limits", "max_task_cost_usd", "0"),
            ("limits", "max_task_cost_usd", 1.5),
            ("limits", "max_task_cost_usd", "10.00"),
            ("limits", "max_total_tokens", True),
            ("limits", "max_total_tokens", 100001),
        ):
            with self.subTest(section=section, name=name, val=val):
                packet = copy.deepcopy(self.example)
                packet[section][name] = val
                with self.assertRaises(module.InvalidPacket):
                    module.estimate(packet)

    def test_reject_missing_fields_extra_fields_and_unexpected_sources(self):
        for key, value in (
            ("api_key", "synthetic-no-real-secret"),
            ("model_call_enabled", True),
        ):
            packet = copy.deepcopy(self.example)
            packet[key] = value
            with self.assertRaises(module.InvalidPacket):
                module.estimate(packet)
        packet = copy.deepcopy(self.example)
        del packet["tokens"]["output"]
        with self.assertRaises(module.InvalidPacket):
            module.estimate(packet)
        packet = copy.deepcopy(self.example)
        packet["source_type"] = "estimated_from_prompt_without_provider_tokens"
        with self.assertRaises(module.InvalidPacket):
            module.estimate(packet)
        packet = copy.deepcopy(self.example)
        packet["task_id"] = "../../secret"
        with self.assertRaises(module.InvalidPacket):
            module.estimate(packet)
        packet = copy.deepcopy(self.example)
        packet["schema_version"] = True
        with self.assertRaises(module.InvalidPacket):
            module.estimate(packet)

    def test_reject_duplicate_keys(self):
        with self.assertRaises(module.InvalidPacket):
            json.loads('{"schema_version":1,"schema_version":2}',
                       object_pairs_hook=module.unique_keys)

    def test_require_nonzero_usage(self):
        packet = copy.deepcopy(self.example)
        packet["tokens"] = {"input": 0, "output": 0}
        with self.assertRaises(module.InvalidPacket):
            module.estimate(packet)


if __name__ == "__main__":
    unittest.main()
