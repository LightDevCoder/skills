"""Evaluation dataset and runner for agent-config task profiling and topology selection.

Covers representative scenarios specified in Section 35 of SPEC:
  - routine documentation edit
  - small bug fix
  - standard feature
  - large refactor
  - security-critical change
  - complex concurrency work
  - cost-sensitive complex work
  - latency-sensitive routine work
  - fixed-model harness
  - multi-model harness
  - no effort selector
  - limited effort selector
  - current model already sufficient
  - user explicitly requests high effort
  - user rejects configuration change
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_CONFIG_SCRIPTS = PROJECT_ROOT / "skills" / "engineering" / "agent-config" / "scripts"
if str(AGENT_CONFIG_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(AGENT_CONFIG_SCRIPTS))

from agent_config_models import (
    AbstractTaskProfile,
    AgentConfigResult,
    HostCapabilities,
    TaskCharacteristics,
)
from agent_config import agent_config_recommend


@dataclass
class AgentConfigScenario:
    id: str
    name: str
    host: HostCapabilities
    task: TaskCharacteristics
    approval: str  # "unknown", "approved", "declined"
    expected_tier: str  # "routine", "standard", "high"
    expected_model: str
    expected_topology: str
    expected_readiness: str
    expected_resolved_effort: Optional[str] = None
    notes: str = ""


SCENARIOS: List[AgentConfigScenario] = [
    AgentConfigScenario(
        id="AC-01",
        name="Routine documentation edit",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
        ),
        task=TaskCharacteristics(
            title="Fix typo in README",
            description="Fix spelling error in installation section",
            difficulty="routine",
        ),
        approval="approved",
        expected_tier="routine",
        expected_model="gpt-4o-mini",
        expected_topology="Case C",
        expected_readiness="READY",
        notes="Routine task maps to routine tier (gpt-4o-mini).",
    ),
    AgentConfigScenario(
        id="AC-02",
        name="Small bug fix",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
        ),
        task=TaskCharacteristics(
            title="Fix off-by-one error in pagination",
            description="Page index starts at 0 instead of 1",
            difficulty="standard",
        ),
        approval="approved",
        expected_tier="standard",
        expected_model="claude-3-5-sonnet",
        expected_topology="Case A",
        expected_readiness="READY",
        notes="Standard bug fix stays on active standard model.",
    ),
    AgentConfigScenario(
        id="AC-03",
        name="Standard feature implementation",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
        ),
        task=TaskCharacteristics(
            title="Add CSV export endpoint",
            description="Add export to CSV with standard schema",
            difficulty="standard",
        ),
        approval="approved",
        expected_tier="standard",
        expected_model="claude-3-5-sonnet",
        expected_topology="Case A",
        expected_readiness="READY",
        notes="Standard feature maps to standard tier.",
    ),
    AgentConfigScenario(
        id="AC-04",
        name="Large refactor",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
            supported_effort=["low", "medium", "high"],
        ),
        task=TaskCharacteristics(
            title="Refactor core storage engine",
            description="Decompose monolithic storage class into pluggable backend adapters",
            difficulty="high",
        ),
        approval="approved",
        expected_tier="high",
        expected_model="o3-mini",
        expected_topology="Case C",
        expected_readiness="READY",
        expected_resolved_effort="high",
        notes="Large refactor requires high tier and high reasoning.",
    ),
    AgentConfigScenario(
        id="AC-05",
        name="Security-critical change",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
            supported_effort=["low", "medium", "high"],
        ),
        task=TaskCharacteristics(
            title="Fix authentication token forgery vulnerability",
            description="Harden JWT signature verification and constant-time comparison",
            difficulty="critical",
        ),
        approval="approved",
        expected_tier="high",
        expected_model="o3-mini",
        expected_topology="Case C",
        expected_readiness="READY",
        expected_resolved_effort="high",
        notes="Security critical task requires high tier.",
    ),
    AgentConfigScenario(
        id="AC-06",
        name="Complex concurrency work",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
            supported_effort=["low", "medium", "high"],
        ),
        task=TaskCharacteristics(
            title="Implement lock-free queue with memory barriers",
            description="High-throughput cross-thread message passing queue",
            difficulty="high",
        ),
        approval="approved",
        expected_tier="high",
        expected_model="o3-mini",
        expected_topology="Case C",
        expected_readiness="READY",
        expected_resolved_effort="high",
        notes="Concurrency invariants require high reasoning effort.",
    ),
    AgentConfigScenario(
        id="AC-07",
        name="Cost-sensitive complex work",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
            supported_effort=["low", "medium", "high"],
        ),
        task=TaskCharacteristics(
            title="Complex algorithm optimization",
            description="Optimize graph traversal algorithms",
            difficulty="high",
            cost_sensitive=True,
        ),
        approval="approved",
        expected_tier="high",
        expected_model="o3-mini",
        expected_topology="Case C",
        expected_readiness="READY",
        expected_resolved_effort="high",
        notes="Cost sensitivity does NOT downgrade capability tier; stays high.",
    ),
    AgentConfigScenario(
        id="AC-08",
        name="Latency-sensitive routine work",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="claude-3-5-sonnet",
            available_models=["gpt-4o-mini", "claude-3-5-sonnet", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "claude-3-5-sonnet", "high": "o3-mini"},
        ),
        task=TaskCharacteristics(
            title="Quick lint fix",
            description="Run linter and fix whitespace",
            difficulty="routine",
            latency_sensitive=True,
        ),
        approval="approved",
        expected_tier="routine",
        expected_model="gpt-4o-mini",
        expected_topology="Case C",
        expected_readiness="READY",
        notes="Fast turnaround on routine tier.",
    ),
    AgentConfigScenario(
        id="AC-09",
        name="Fixed-model harness",
        host=HostCapabilities(
            has_model_selector=False,
            active_model="fixed-sonnet",
            available_models=["fixed-sonnet"],
        ),
        task=TaskCharacteristics(
            title="Complex database migration",
            difficulty="high",
        ),
        approval="approved",
        expected_tier="high",
        expected_model="fixed-sonnet",
        expected_topology="Case A",
        expected_readiness="READY",
        notes="Fixed harness gracefully preserves active model.",
    ),
    AgentConfigScenario(
        id="AC-10",
        name="Multi-model decomposed harness",
        host=HostCapabilities(
            has_model_selector=True,
            per_agent_config=True,
            active_model="gpt-4o",
            available_models=["gpt-4o", "o3-mini"],
            profile_tiers={"standard": "gpt-4o", "high": "o3-mini"},
        ),
        task=TaskCharacteristics(
            title="Full authentication subsystem",
            shape="decomposed",
            formal_tickets_exist=True,
            difficulty="high",
        ),
        approval="approved",
        expected_tier="high",
        expected_model="o3-mini",
        expected_topology="Case D",
        expected_readiness="READY",
        notes="Decomposed multi-model task generates Case D topology.",
    ),
    AgentConfigScenario(
        id="AC-11",
        name="Host with no effort selector",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="gpt-4o",
            supported_effort=[],  # No effort selector
            profile_tiers={"high": "gpt-4o"},
        ),
        task=TaskCharacteristics(
            title="Complex logic overhaul",
            difficulty="high",
        ),
        approval="approved",
        expected_tier="high",
        expected_model="gpt-4o",
        expected_topology="Case A",
        expected_readiness="READY",
        expected_resolved_effort=None,
        notes="Host without effort selector returns None effort safely.",
    ),
    AgentConfigScenario(
        id="AC-12",
        name="Limited effort selector bounds Jev output",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="model-x",
            supported_effort=["low", "medium"],  # No 'high' supported
            profile_tiers={"high": "model-x"},
        ),
        task=TaskCharacteristics(
            difficulty="high",
        ),
        approval="approved",
        expected_tier="high",
        expected_model="model-x",
        expected_topology="Case A",
        expected_readiness="READY",
        expected_resolved_effort="medium",
        notes="Host bounds Jev 'high' to nearest verified level 'medium'.",
    ),
    AgentConfigScenario(
        id="AC-13",
        name="User explicitly requests high effort (overrides Jev)",
        host=HostCapabilities(
            active_model="model-x",
            available_models=["model-x"],
            supported_effort=["low", "medium", "high"],
            profile_tiers={"routine": "model-x"},
        ),
        task=TaskCharacteristics(
            difficulty="routine",
            reasoning_policy="highest-supported",
        ),
        approval="approved",
        expected_tier="routine",
        expected_model="model-x",
        expected_topology="Case A",
        expected_readiness="READY",
        expected_resolved_effort="high",
        notes="Explicit user reasoning policy wins over routine task.",
    ),
    AgentConfigScenario(
        id="AC-14",
        name="User rejects configuration change preview",
        host=HostCapabilities(
            has_model_selector=True,
            active_model="active-stay",
            available_models=["active-stay", "tier-high"],
            profile_tiers={"high": "tier-high"},
        ),
        task=TaskCharacteristics(difficulty="high"),
        approval="declined",
        expected_tier="high",
        expected_model="active-stay",
        expected_topology="Case A",
        expected_readiness="READY",
        expected_resolved_effort=None,
        notes="User declined preview -> safely retains active model.",
    ),
]


def evaluate_scenario(scenario: AgentConfigScenario, client: Optional[Any] = None) -> Dict[str, Any]:
    """Evaluate one agent-config scenario."""
    res = agent_config_recommend(
        host=scenario.host,
        task=scenario.task,
        approval=scenario.approval,
        client=client,
    )

    readiness_ok = res.readiness == scenario.expected_readiness
    topology_ok = res.execution_config.topology == scenario.expected_topology if res.execution_config else True
    model_ok = res.execution_config.model == scenario.expected_model if res.execution_config else True
    effort_ok = res.execution_config.resolved_effort == scenario.expected_resolved_effort if res.execution_config else True
    tier_ok = res.abstract_profile.recommended_tier == scenario.expected_tier if res.abstract_profile else True

    # Candidate safety invariant: selected_model must be in valid candidates (or active_model)
    valid_candidates = scenario.host.available_models or [scenario.host.active_model]
    candidate_safe = res.execution_config.model in valid_candidates if res.execution_config else True

    passed = readiness_ok and topology_ok and model_ok and effort_ok and tier_ok and candidate_safe

    return {
        "id": scenario.id,
        "name": scenario.name,
        "passed": passed,
        "readiness_matched": readiness_ok,
        "topology_matched": topology_ok,
        "model_matched": model_ok,
        "effort_matched": effort_ok,
        "tier_matched": tier_ok,
        "candidate_safe": candidate_safe,
        "observed_model": res.execution_config.model if res.execution_config else None,
        "observed_effort": res.execution_config.resolved_effort if res.execution_config else None,
        "observed_topology": res.execution_config.topology if res.execution_config else None,
        "fallback_used": res.fallback_used,
        "approval_state": res.approval,
    }


def run_agent_config_eval(client: Optional[Any] = None) -> Dict[str, Any]:
    """Run all 14 agent-config evaluation scenarios."""
    results = [evaluate_scenario(sc, client=client) for sc in SCENARIOS]
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "suite": "agent-config",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total if total > 0 else 0.0,
        "results": results,
    }
