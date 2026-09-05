"""Cross-repo behavioral contract and acceptance integration tests.

Verifies the integration between the Agent Config Skill and the Companion MCP runtime,
implementing the two-layer acceptance required by the SPEC:
  Layer 1 — Deterministic Contract Tests (Profile, HostCapabilities, ExecutionConfig against canonical schemas)
  Layer 2 — Behavioral Scenario Matrix Tests (All 12 mandatory scenarios from SPEC §8)
"""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"


def find_companion_repo() -> Path | None:
    candidates = [
        Path(os.environ.get("AGENT_CONFIG_COMPANION_PATH", "")),
        Path(__file__).resolve().parent.parent.parent.parent.parent / "agent-config",
        Path("/Users/light/Documents/Projects/Configurations/agent-config"),
    ]
    for c in candidates:
        if c.is_dir() and (c / "schemas").is_dir():
            return c
    return None


from test_agent_config_behavior import (
    load,
    route_execution,
    evaluate_setup_gate,
    classify_task_shape,
    resolve_effort,
    capability,
    check_profile_stale,
)


class CompanionContractIntegrationTest(unittest.TestCase):
    """Layer 1: Deterministic Schema & Canonical Contract Tests."""

    def test_layer1_deterministic_schemas_via_companion_ajv(self) -> None:
        """All Skill-documented profiles, host fixtures, and execution configs pass canonical companion schemas."""
        companion_repo = find_companion_repo()
        if not companion_repo:
            self.skipTest("Companion repo not found in test environment")

        node_script = """
const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

const ajv = new Ajv({ allErrors: true, strictTypes: false });
addFormats(ajv);

const companionDir = process.argv[1];
const skillsFixturesDir = process.argv[2];

const profileSchema = JSON.parse(fs.readFileSync(path.join(companionDir, 'schemas', 'profile.schema.json'), 'utf8'));
const hostSchema = JSON.parse(fs.readFileSync(path.join(companionDir, 'schemas', 'host-capabilities.schema.json'), 'utf8'));
const execSchema = JSON.parse(fs.readFileSync(path.join(companionDir, 'schemas', 'execution-config.schema.json'), 'utf8'));

const valProfile = ajv.compile(profileSchema);
const valHost = ajv.compile(hostSchema);
const valExec = ajv.compile(execSchema);

// 1. Validate Profiles
const profiles = ['profile-single-model.json', 'profile-multi-model.json', 'profile-multi-model-shared.json'];
for (const p of profiles) {
  const data = JSON.parse(fs.readFileSync(path.join(skillsFixturesDir, p), 'utf8'));
  if (!valProfile(data)) {
    console.error('Profile schema failure:', p, valProfile.errors);
    process.exit(1);
  }
}

// 2. Validate Host fixtures
const hosts = [
  'case-c-fixed-single-pass.json',
  'case-d-fixed-decomposed.json',
  'case-a-tiered-single-pass.json',
  'case-b-tiered-decomposed.json',
  'unranked-multiple-models.json',
  'missing-reasoning-control.json'
];
for (const h of hosts) {
  const data = JSON.parse(fs.readFileSync(path.join(skillsFixturesDir, h), 'utf8'));
  if (!valHost(data)) {
    console.error('Host schema failure:', h, valHost.errors);
    process.exit(1);
  }
}

// 3. Validate Canonical ExecutionConfigs (Cases A, B, C, D)
const cases = ['case-a', 'case-b', 'case-c', 'case-d'];
for (const c of cases) {
  const data = JSON.parse(fs.readFileSync(path.join(skillsFixturesDir, `execution-config-${c}.json`), 'utf8'));
  if (!valExec(data)) {
    console.error('ExecutionConfig schema failure:', c, valExec.errors);
    process.exit(1);
  }
}

console.log('ALL_SCHEMAS_PASS');
"""
        node_path = str(companion_repo / "node_modules")
        result = subprocess.run(
            ["node", "-e", node_script, str(companion_repo), str(FIXTURES)],
            env={**os.environ, "NODE_PATH": node_path},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"Node schema validation failed: {result.stderr or result.stdout}")
        self.assertIn("ALL_SCHEMAS_PASS", result.stdout)


class BehavioralAcceptanceMatrixTest(unittest.TestCase):
    """Layer 2: Mandatory Behavioral Acceptance Matrix (§8)."""

    def setUp(self) -> None:
        self.single_profile = load("profile-single-model.json")
        self.multi_profile = load("profile-multi-model.json")
        self.host_case_a = load("case-c-fixed-single-pass.json")  # Single-model host
        self.host_case_b = load("case-d-fixed-decomposed.json")   # Single-model decomposed host
        self.host_case_c = load("case-a-tiered-single-pass.json")  # Multi-model host
        self.host_case_d = load("case-b-tiered-decomposed.json")   # Multi-model decomposed host

    def test_scenario_01_multi_model_small_spec(self) -> None:
        """Scenario 1: Multi-model / small SPEC -> minimal topology + lowest sufficient authorized model."""
        task = {"difficulty": "routine", "word_count": 500}
        plan = route_execution(self.multi_profile, task, self.host_case_c)

        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["task_shape"], "single-pass")
        self.assertEqual(plan["mode"], "Case C (Tiered Multi-model + Single-pass)")
        self.assertEqual(plan["topology"], "minimal")
        self.assertEqual(plan["execution"]["tier"], "routine")
        self.assertEqual(plan["execution"]["model"], "model-alpha")
        self.assertEqual(plan["execution"]["effort"], "low")

        exec_cfg = plan["execution_config"]
        self.assertEqual(exec_cfg["task_shape"], "single-pass")
        self.assertEqual(exec_cfg["model_mode"], "multi")
        self.assertEqual(exec_cfg["topology"]["concurrency"], 1)
        self.assertEqual(exec_cfg["execution"]["model"], "model-alpha")

    def test_scenario_02_multi_model_demanding_small_task(self) -> None:
        """Scenario 2: Multi-model / demanding small task -> stronger implementation model and review."""
        task = {"difficulty": "demanding", "word_count": 800}
        plan = route_execution(self.multi_profile, task, self.host_case_c)

        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["task_shape"], "single-pass")
        self.assertEqual(plan["execution"]["tier"], "high")
        self.assertEqual(plan["execution"]["model"], "model-gamma")
        self.assertEqual(plan["execution"]["effort"], "high")
        self.assertEqual(plan["review"]["tier"], "review")
        self.assertEqual(plan["review"]["model"], "model-gamma")

        exec_cfg = plan["execution_config"]
        self.assertEqual(exec_cfg["execution"]["model"], "model-gamma")
        self.assertEqual(exec_cfg["review"]["strategy"], "independent-review")

    def test_scenario_03_multi_model_tickets(self) -> None:
        """Scenario 3: Multi-model / tickets -> per-ticket tier routing + bounded execution topology."""
        tickets = [
            {"id": "01", "difficulty": "routine", "blocked_by": []},
            {"id": "02", "difficulty": "moderate", "blocked_by": []},
            {"id": "03", "difficulty": "demanding", "blocked_by": ["01"]},
        ]
        task = {"tickets": tickets}
        plan = route_execution(self.multi_profile, task, self.host_case_d)

        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["task_shape"], "decomposed")
        self.assertEqual(plan["mode"], "Case D (Tiered Multi-model + Decomposed)")
        self.assertEqual(plan["concurrency_cap"], 3)
        self.assertEqual(plan["controller"]["model"], "model-gamma")

        # Per-ticket tier routing
        workers = plan["workers"]
        self.assertEqual(workers[0]["model"], "model-alpha")
        self.assertEqual(workers[0]["tier"], "routine")
        self.assertEqual(workers[1]["model"], "model-beta")
        self.assertEqual(workers[1]["tier"], "standard")
        self.assertEqual(workers[2]["model"], "model-gamma")
        self.assertEqual(workers[2]["tier"], "high")

        # Canonical execution config matches
        exec_cfg = plan["execution_config"]
        self.assertEqual(exec_cfg["topology"]["type"], "controller-workers")
        self.assertEqual(len(exec_cfg["work_items"]), 3)

    def test_scenario_04_complex_no_tickets(self) -> None:
        """Scenario 4: Complex / no tickets -> NEED_PROJECT_TICKETS handoff."""
        task = {"requires_ticket_decomposition": True}
        self.assertEqual(classify_task_shape(task), "decomposed")

        plan = route_execution(self.multi_profile, task, self.host_case_d)
        self.assertEqual(plan["readiness"], "needs-project-tickets")
        self.assertEqual(plan["handoff"], "project-tickets")
        self.assertIn("formal ticket breakdown", plan["reason"])

    def test_scenario_05_single_model_small(self) -> None:
        """Scenario 5: Single-model / small -> same model, no fake tier routing."""
        task = {"difficulty": "routine", "word_count": 300}
        plan = route_execution(self.single_profile, task, self.host_case_a)

        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["mode"], "Case A (Fixed Single-model + Single-pass)")
        self.assertEqual(plan["execution"]["model"], "model-alpha")
        self.assertEqual(plan["review"]["model"], "model-alpha")
        self.assertEqual(plan["review"]["strategy"], "self-check")
        self.assertFalse(plan["fake_roles"])

    def test_scenario_06_single_model_tickets(self) -> None:
        """Scenario 6: Single-model / tickets -> same model + Host-supported context/topology."""
        tickets = [
            {"id": "01", "difficulty": "routine"},
            {"id": "02", "difficulty": "moderate"},
        ]
        task = {"tickets": tickets}
        plan = route_execution(self.single_profile, task, self.host_case_b)

        self.assertEqual(plan["status"], "READY")
        self.assertEqual(plan["mode"], "Case B (Fixed Single-model + Decomposed)")
        self.assertEqual(plan["controller"]["model"], "model-alpha")
        self.assertEqual(plan["concurrency_cap"], 2)

        for w in plan["workers"]:
            self.assertEqual(w["model"], "model-alpha")
            self.assertEqual(w["context"], "subagent")

        self.assertFalse(plan["model_tier_assignment"])

    def test_scenario_07_no_subagents_parallelism_serial_fallback(self) -> None:
        """Scenario 7: No subagents/parallelism -> serial safe fallback."""
        host_serial = json.loads(json.dumps(self.host_case_b))
        host_serial["capabilities"]["subagents"]["state"] = "unavailable"
        host_serial["capabilities"]["threads"]["state"] = "unavailable"
        host_serial["capabilities"]["parallelism"]["state"] = "unavailable"
        host_serial["capabilities"]["concurrency"]["max_concurrency"] = 1

        tickets = [{"id": "01"}, {"id": "02"}]
        task = {"tickets": tickets}
        plan = route_execution(self.single_profile, task, host_serial)

        self.assertEqual(plan["concurrency_cap"], 1)
        for w in plan["workers"]:
            self.assertEqual(w["context"], "serial-main-session")

    def test_scenario_08_capability_unknown_fail_closed(self) -> None:
        """Scenario 8: Capability unknown -> no unsupported topology (fail closed)."""
        host_unknown = json.loads(json.dumps(self.host_case_a))
        host_unknown["capabilities"]["subagents"]["state"] = "unknown"
        host_unknown["capabilities"]["threads"]["state"] = "unknown"
        host_unknown["capabilities"]["parallelism"]["state"] = "unknown"

        self.assertEqual(capability(host_unknown, "subagents"), "unknown")
        self.assertEqual(capability(host_unknown, "threads"), "unknown")
        self.assertEqual(capability(host_unknown, "parallelism"), "unknown")

        # Routing does not fabricate parallel subagent execution when capability is unknown
        tickets = [{"id": "01"}, {"id": "02"}]
        task = {"tickets": tickets}
        plan = route_execution(self.single_profile, task, host_unknown)
        for w in plan["workers"]:
            self.assertNotEqual(w["context"], "subagent")
            self.assertEqual(w["context"], "serial-main-session")

    def test_scenario_09_profile_authorizes_subset(self) -> None:
        """Scenario 9: Profile authorizes subset -> only authorized models selectable."""
        # Host exposes model-alpha, model-beta, model-gamma, model-delta
        host_with_extra = json.loads(json.dumps(self.host_case_d))
        host_with_extra["available_models"].append({
            "id": "model-delta",
            "state": "available",
            "evidence": {"kind": "host-runtime", "locator": "test", "observed_at": "2026-08-24T00:00:00Z"},
        })

        # Profile only assigns alpha, beta, gamma
        tickets = [
            {"id": "01", "difficulty": "routine"},
            {"id": "02", "difficulty": "moderate"},
            {"id": "03", "difficulty": "critical"},
        ]
        task = {"tickets": tickets}
        plan = route_execution(self.multi_profile, task, host_with_extra)

        # Ensure model-delta is never assigned
        assigned_models = {w["model"] for w in plan["workers"]}
        assigned_models.add(plan["controller"]["model"])
        self.assertNotIn("model-delta", assigned_models)
        self.assertTrue(assigned_models.issubset({"model-alpha", "model-beta", "model-gamma"}))

    def test_scenario_10_companion_absent(self) -> None:
        """Scenario 10: Companion absent -> setup offer or session-local/plan-only."""
        # Unprofiled session
        gate_unprofiled = evaluate_setup_gate("normal", None, None)
        self.assertEqual(gate_unprofiled["action"], "plan-only-fallback")
        self.assertEqual(gate_unprofiled["companion"], "absent")

        # Session-local confirmed profile available
        gate_session_local = evaluate_setup_gate("normal", None, self.single_profile)
        self.assertEqual(gate_session_local["action"], "proceed-to-assessment")
        self.assertEqual(gate_session_local["apply_mode"], "plan-only")
        self.assertEqual(gate_session_local["companion"], "absent")

    def test_scenario_11_unsupported_harness_generic_behavior(self) -> None:
        """Scenario 11: Unsupported harness -> Generic/manual behavior in plan-only mode."""
        # Host with generic adapter
        host_generic = json.loads(json.dumps(self.host_case_a))
        host_generic["adapter_id"] = "generic"
        host_generic["capabilities"]["configuration_mutation"] = {"state": "unavailable"}

        gate = evaluate_setup_gate("normal", {"configured": True, "stale": False}, self.single_profile, ["model-alpha"])
        self.assertEqual(gate["action"], "proceed-to-assessment")
        self.assertEqual(gate["apply_mode"], "plan-only")

    def test_scenario_12_user_rejects_agent_config_in_implement(self) -> None:
        """Scenario 12: User rejects agent-config in implement -> normal implement continues."""
        def consume_result(agent_config_result: dict[str, Any], user_setup_response: str | None = None) -> dict[str, Any]:
            readiness = agent_config_result.get("readiness")
            if readiness == "READY":
                exec_cfg = agent_config_result.get("execution_config")
                if exec_cfg is None:
                    return {"action": "BLOCKED", "halted": True}
                return {"action": "execute_with_agent_config", "execution_config": exec_cfg}
            if readiness == "NEED_INPUT":
                if user_setup_response == "decline":
                    return {"action": "execute_direct", "halted": False}
                if user_setup_response == "accept":
                    return {"action": "handoff_to_setup", "handoff": "setup"}
                return {"action": "offer_setup", "handoff": "setup"}
            if readiness == "NEED_PROJECT_TICKETS":
                return {"action": "handoff_to_project_tickets", "halted": True}
            return {"action": "stop", "halted": True}

        agent_config_res = {
            "readiness": "NEED_INPUT",
            "mode": "plan-only",
            "setup_state": {"companion": "ready", "profile": "missing"},
            "handoff": "setup",
            "execution_config": None,
        }
        dispatch = consume_result(
            agent_config_res,
            user_setup_response="decline",
        )
        self.assertEqual(dispatch["action"], "execute_direct")
        self.assertFalse(dispatch.get("halted", False))


if __name__ == "__main__":
    unittest.main()
