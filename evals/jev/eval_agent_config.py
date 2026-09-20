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
    expected_min_complexity: float = 0.0
    expected_max_complexity: float = 3.0
    expected_complexity_tier: Optional[str] = None
    expected_min_reasoning: float = 0.0
    expected_max_reasoning: float = 2.0
    expected_reasoning_level: Optional[str] = None
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
        expected_min_complexity=0.0,
        expected_max_complexity=0.5,
        expected_complexity_tier="routine",
        expected_min_reasoning=0.0,
        expected_max_reasoning=0.8,
        expected_reasoning_level="low",
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
        expected_min_complexity=0.5,
        expected_max_complexity=1.5,
        expected_complexity_tier="standard",
        expected_min_reasoning=0.0,
        expected_max_reasoning=1.5,
        expected_reasoning_level=None,
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
        expected_min_complexity=0.5,
        expected_max_complexity=1.5,
        expected_complexity_tier="standard",
        expected_min_reasoning=0.5,
        expected_max_reasoning=1.5,
        expected_reasoning_level="medium",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=0.0,
        expected_max_complexity=0.5,
        expected_complexity_tier="routine",
        expected_min_reasoning=0.0,
        expected_max_reasoning=0.8,
        expected_reasoning_level="low",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
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
        expected_min_complexity=0.0,
        expected_max_complexity=0.5,
        expected_complexity_tier="routine",
        expected_min_reasoning=0.0,
        expected_max_reasoning=0.8,
        expected_reasoning_level="low",
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
        expected_min_complexity=1.5,
        expected_max_complexity=3.0,
        expected_complexity_tier="high",
        expected_min_reasoning=1.5,
        expected_max_reasoning=2.0,
        expected_reasoning_level="high",
    ),
]


def evaluate_scenario(scenario: AgentConfigScenario, client: Optional[Any] = None) -> Dict[str, Any]:
    """Evaluate one agent-config scenario separating config correctness from semantic quality."""
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

    config_correctness_passed = readiness_ok and topology_ok and model_ok and effort_ok and tier_ok and candidate_safe

    # Semantic evaluation (tri-state: PASS, FAIL, NOT_EVALUATED)
    complexity_semantic = "NOT_EVALUATED"
    reasoning_semantic = "NOT_EVALUATED"

    comp_score = res.abstract_profile.complexity_score if res.abstract_profile else None
    comp_conf = res.abstract_profile.complexity_confidence if res.abstract_profile else None
    comp_src = None
    reas_score = res.abstract_profile.reasoning_score if res.abstract_profile else None
    reas_conf = res.abstract_profile.reasoning_confidence if res.abstract_profile else None
    reas_src = None

    if res.abstract_profile and res.abstract_profile.dimension_provenance:
        prov = res.abstract_profile.dimension_provenance
        if "complexity" in prov:
            comp_src = prov["complexity"].source
            if comp_src == "jev" and comp_score is not None:
                score_ok = scenario.expected_min_complexity <= comp_score <= scenario.expected_max_complexity
                tier_matched = (scenario.expected_complexity_tier is None or res.abstract_profile.recommended_tier == scenario.expected_complexity_tier)
                complexity_semantic = "PASS" if (score_ok and tier_matched) else "FAIL"
        if "reasoning" in prov:
            reas_src = prov["reasoning"].source
            if reas_src == "jev" and reas_score is not None:
                score_ok = scenario.expected_min_reasoning <= reas_score <= scenario.expected_max_reasoning
                level_matched = (scenario.expected_reasoning_level is None or res.abstract_profile.reasoning_need == scenario.expected_reasoning_level)
                reasoning_semantic = "PASS" if (score_ok and level_matched) else "FAIL"

    # Overall pass: configuration must be correct; and evaluated semantics must not fail
    overall_passed = config_correctness_passed and (complexity_semantic != "FAIL") and (reasoning_semantic != "FAIL")

    return {
        "id": scenario.id,
        "name": scenario.name,
        "passed": overall_passed,
        "config_correctness_passed": config_correctness_passed,
        "complexity_semantic": complexity_semantic,
        "reasoning_semantic": reasoning_semantic,
        "readiness_matched": readiness_ok,
        "topology_matched": topology_ok,
        "model_matched": model_ok,
        "effort_matched": effort_ok,
        "tier_matched": tier_ok,
        "candidate_safe": candidate_safe,
        "observed_model": res.execution_config.model if res.execution_config else None,
        "observed_effort": res.execution_config.resolved_effort if res.execution_config else None,
        "observed_topology": res.execution_config.topology if res.execution_config else None,
        "observed_tier": res.abstract_profile.recommended_tier if res.abstract_profile else None,
        "observed_reasoning": res.abstract_profile.reasoning_need if res.abstract_profile else None,
        "fallback_used": res.fallback_used,
        "approval_state": res.approval,
        "raw_evidence": {
            "complexity_score": comp_score,
            "complexity_confidence": comp_conf,
            "complexity_source": comp_src,
            "expected_complexity_range": [scenario.expected_min_complexity, scenario.expected_max_complexity],
            "reasoning_score": reas_score,
            "reasoning_confidence": reas_conf,
            "reasoning_source": reas_src,
            "expected_reasoning_range": [scenario.expected_min_reasoning, scenario.expected_max_reasoning],
        },
    }


def run_agent_config_eval(client: Optional[Any] = None) -> Dict[str, Any]:
    """Run all 14 agent-config evaluation scenarios."""
    results = [evaluate_scenario(sc, client=client) for sc in SCENARIOS]
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    config_passed = sum(1 for r in results if r["config_correctness_passed"])

    comp_eval = sum(1 for r in results if r["complexity_semantic"] in ("PASS", "FAIL"))
    comp_not_eval = sum(1 for r in results if r["complexity_semantic"] == "NOT_EVALUATED")
    comp_pass = sum(1 for r in results if r["complexity_semantic"] == "PASS")
    comp_fail = sum(1 for r in results if r["complexity_semantic"] == "FAIL")
    comp_acc = (comp_pass / comp_eval) if comp_eval > 0 else None

    reas_eval = sum(1 for r in results if r["reasoning_semantic"] in ("PASS", "FAIL"))
    reas_not_eval = sum(1 for r in results if r["reasoning_semantic"] == "NOT_EVALUATED")
    reas_pass = sum(1 for r in results if r["reasoning_semantic"] == "PASS")
    reas_fail = sum(1 for r in results if r["reasoning_semantic"] == "FAIL")
    reas_acc = (reas_pass / reas_eval) if reas_eval > 0 else None

    return {
        "suite": "agent-config",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total if total > 0 else 0.0,
        "config_correctness_passed": config_passed,
        "config_correctness_accuracy": config_passed / total if total > 0 else 0.0,
        "complexity_evaluated": comp_eval,
        "complexity_not_evaluated": comp_not_eval,
        "complexity_passed": comp_pass,
        "complexity_failed": comp_fail,
        "complexity_accuracy": comp_acc,
        "reasoning_evaluated": reas_eval,
        "reasoning_not_evaluated": reas_not_eval,
        "reasoning_passed": reas_pass,
        "reasoning_failed": reas_fail,
        "reasoning_accuracy": reas_acc,
        "results": results,
    }
