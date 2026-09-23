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


import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

sys.path.insert(0, str(ROOT / "scripts"))
from agent_config import agent_config_recommend
from datetime import datetime, timezone


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def fresh_host(name: str, workspace: str) -> dict:
    host = load(name)
    now = datetime.now(timezone.utc).isoformat()
    host["observed_at"] = now
    host["workspace"] = workspace
    for model in host.get("available_models", []):
        if model.get("evidence"):
            model["evidence"]["observed_at"] = now
    for capability in host.get("capabilities", {}).values():
        if capability.get("evidence"):
            capability["evidence"]["observed_at"] = now
    return host


class CompanionContractIntegrationTest(unittest.TestCase):
    """Deterministic Schema & Canonical Contract Tests: Hermetic Layer 1 and Cross-Repo Integration Layer 2."""

    def test_hermetic_schemas_snapshot_provenance_and_integrity(self) -> None:
        """Layer 1 Hermetic: In-repo schema snapshot carries full provenance metadata and valid JSON schemas."""
        schemas_dir = FIXTURES / "schemas"
        meta_file = schemas_dir / "METADATA.json"
        self.assertTrue(meta_file.is_file(), f"Hermetic schema snapshot metadata missing: {meta_file}")

        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        self.assertEqual(meta.get("source_repository"), "LightDevCoder/agent-config")
        self.assertEqual(len(meta.get("source_revision", "")), 40)
        self.assertTrue(meta.get("contract_version"))
        self.assertTrue(meta.get("snapshot_date"))

        declared_schemas = meta.get("schemas", [])
        self.assertGreaterEqual(len(declared_schemas), 3)

        for s_name in declared_schemas:
            s_file = schemas_dir / s_name
            self.assertTrue(s_file.is_file(), f"Declared schema snapshot file missing: {s_file}")
            s_json = json.loads(s_file.read_text(encoding="utf-8"))
            self.assertIn("$schema", s_json)
            self.assertIn("type", s_json)

    def test_hermetic_fixtures_structural_contracts(self) -> None:
        """Layer 1 Hermetic: Validate profiles, hosts, and execution configs structurally in clean environment."""
        # 1. Profiles
        for p in ["profile-single-model.json", "profile-multi-model.json", "profile-multi-model-shared.json"]:
            data = json.loads((FIXTURES / p).read_text(encoding="utf-8"))
            self.assertEqual(data.get("profile_version"), 1)
            self.assertIn("host", data)
            self.assertIn("scope", data)
            self.assertIn(data.get("model_mode"), ("single", "multi"))
            self.assertIn("capabilities", data)
            if data["model_mode"] == "single":
                self.assertIn("single_model", data)
            else:
                self.assertIn("tiers", data)

        # 2. Host fixtures
        host_files = [
            "case-c-fixed-single-pass.json",
            "case-d-fixed-decomposed.json",
            "case-a-tiered-single-pass.json",
            "case-b-tiered-decomposed.json",
            "unranked-multiple-models.json",
            "missing-reasoning-control.json",
        ]
        for h in host_files:
            data = json.loads((FIXTURES / h).read_text(encoding="utf-8"))
            self.assertIn("host_id", data)
            self.assertIn("adapter_id", data)
            self.assertIn("available_models", data)
            self.assertIsInstance(data["available_models"], list)
            self.assertIn("capabilities", data)

        # 3. Execution Configs
        for c in ["case-a", "case-b", "case-c", "case-d"]:
            data = json.loads((FIXTURES / f"execution-config-{c}.json").read_text(encoding="utf-8"))
            self.assertIn("task_shape", data)
            self.assertIn(data["task_shape"], ("single-pass", "decomposed"))
            self.assertIn("model_mode", data)
            self.assertIn(data["model_mode"], ("single", "multi"))
            self.assertIn("topology", data)
            self.assertIsInstance(data["topology"]["concurrency"], int)
            if data["task_shape"] == "single-pass":
                self.assertIn("execution", data)
                self.assertIn("model", data["execution"])
            else:
                self.assertIn("controller", data)
                self.assertIn("work_items", data)
                self.assertIsInstance(data["work_items"], list)

    def test_cross_repo_schema_drift_detection(self) -> None:
        """Layer 2 Cross-Repo: Detect schema drift between local hermetic snapshot and live companion repo."""
        companion_repo = find_companion_repo()
        if not companion_repo:
            self.skipTest("Companion repo not found in test environment; cross-repo drift check skipped.")

        schemas_dir = FIXTURES / "schemas"
        meta = json.loads((schemas_dir / "METADATA.json").read_text(encoding="utf-8"))
        drifted: list[str] = []

        for s_name in meta.get("schemas", []):
            local_file = schemas_dir / s_name
            comp_file = companion_repo / "schemas" / s_name
            if not comp_file.is_file():
                drifted.append(f"{s_name} (missing in companion)")
                continue

            local_json = json.loads(local_file.read_text(encoding="utf-8"))
            comp_json = json.loads(comp_file.read_text(encoding="utf-8"))
            if local_json != comp_json:
                drifted.append(s_name)

        self.assertEqual(
            drifted,
            [],
            f"Schema drift detected between local hermetic snapshot (revision {meta['source_revision']}) "
            f"and live companion repo for: {drifted}. Update local snapshot schemas and METADATA.json.",
        )

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


class ProductionRoutingMatrixTest(unittest.TestCase):
    """Exercise the actual Skill entry point with canonical companion fixtures."""

    def setUp(self) -> None:
        self.multi = load("profile-multi-model.json")
        self.single = load("profile-single-model.json")
        workspace = self.multi["scope"]["workspace"]
        self.tiered = fresh_host("case-a-tiered-single-pass.json", workspace)
        self.fixed = fresh_host("case-c-fixed-single-pass.json", workspace)

    def route(self, host: dict, profile: dict | None, **task: object):
        return agent_config_recommend(host, task, profile=profile, use_jev=False)

    def test_routine_uses_confirmed_tier(self) -> None:
        result = self.route(self.tiered, self.multi, difficulty="routine", difficulty_source="explicit-user")
        self.assertEqual(result.readiness, "READY")
        self.assertEqual(result.execution_config.model, "model-alpha")

    def test_high_uses_confirmed_high_tier(self) -> None:
        result = self.route(self.tiered, self.multi, difficulty="high", difficulty_source="explicit-user")
        self.assertEqual(result.execution_config.model, "model-gamma")
        self.assertEqual(result.execution_config.resolved_effort, "high")

    def test_decomposed_multimodel_uses_case_d_when_evidenced(self) -> None:
        result = self.route(self.tiered, self.multi, shape="decomposed", formal_tickets_exist=True)
        self.assertEqual(result.readiness, "READY")
        self.assertEqual(result.execution_config.topology, "Case D")

    def test_decomposed_without_tickets_stops(self) -> None:
        result = self.route(self.tiered, self.multi, shape="decomposed", formal_tickets_exist=False)
        self.assertEqual(result.readiness, "NEED_PROJECT_TICKETS")
        self.assertIsNone(result.execution_config)

    def test_fixed_single_model_uses_case_a(self) -> None:
        result = self.route(self.fixed, self.single, difficulty="routine")
        self.assertEqual(result.readiness, "READY")
        self.assertEqual(result.execution_config.topology, "Case A")
        self.assertEqual(result.execution_config.model, "model-alpha")

    def test_fixed_decomposed_uses_case_b(self) -> None:
        result = self.route(self.fixed, self.single, shape="decomposed", formal_tickets_exist=True)
        self.assertEqual(result.readiness, "READY")
        self.assertEqual(result.execution_config.topology, "Case B")

    def test_unavailable_profile_model_stops(self) -> None:
        host = json.loads(json.dumps(self.tiered))
        host["available_models"] = [m for m in host["available_models"] if m["id"] != "model-gamma"]
        self.assertEqual(self.route(host, self.multi, difficulty="critical").readiness, "NEED_INPUT")

    def test_highest_supported_uses_host_max(self) -> None:
        host = json.loads(json.dumps(self.tiered))
        host["supported_effort_values"] += ["xhigh", "max"]
        result = self.route(host, self.multi, difficulty="high", difficulty_source="explicit-user")
        self.assertEqual(result.execution_config.resolved_effort, "max")

    def test_unprofiled_host_stops(self) -> None:
        self.assertEqual(self.route(self.tiered, None).readiness, "NEED_INPUT")

    def test_extra_host_model_is_not_promoted_to_tier(self) -> None:
        host = json.loads(json.dumps(self.tiered))
        extra = json.loads(json.dumps(host["available_models"][0]))
        extra["id"] = "unprofiled-extra"
        host["available_models"].append(extra)
        result = self.route(host, self.multi, difficulty="standard", difficulty_source="explicit-user")
        self.assertEqual(result.execution_config.model, "model-beta")

    def test_harness_mismatch_stops(self) -> None:
        host = json.loads(json.dumps(self.tiered))
        host["adapter_id"] = "other-adapter"
        self.assertEqual(self.route(host, self.multi).readiness, "NEED_INPUT")

    def test_declined_preview_without_active_model_stops(self) -> None:
        result = agent_config_recommend(self.tiered, {}, profile=self.multi, approval="declined", use_jev=False)
        self.assertEqual(result.readiness, "NEED_INPUT")
        self.assertIsNone(result.execution_config)


if __name__ == "__main__":
    unittest.main()
