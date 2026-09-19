"""Evaluation dataset and runner for ask-light semantic routing.

Covers representative scenarios specified in Section 34 of SPEC:
  - What should I do next?
  - Where is the project now?
  - Explain this workflow.
  - Go ahead.
  - Should we start implementing?
  - I only want advice.
  - No SPEC exists.
  - Clarification is complete.
  - SPEC exists but tickets do not.
  - Ready ticket exists.
  - All tickets resolved.
  - Review is stale.
  - Review is dirty.
  - Unknown ticket requested.
  - Multiple efforts are active.
  - Ambiguous request.
  - Complex architectural request.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add skill scripts to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASK_LIGHT_SCRIPTS = PROJECT_ROOT / "skills" / "productivity" / "ask-light" / "scripts"
if str(ASK_LIGHT_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ASK_LIGHT_SCRIPTS))

from ask_light_models import AskLightRecommendation, CompactProjectState, LegalActionsResult
from state_extractor import compute_legal_actions
from semantic_router import route_with_jev


@dataclass
class AskLightScenario:
    id: str
    name: str
    state: CompactProjectState
    user_request: str
    expected_legal_actions: List[str]
    expected_fallback_action: Optional[str]
    expected_status: str  # "RECOMMEND", "TRANSITION", "BLOCKED", "NEED_INPUT", "EXPLAIN", "TERMINAL"
    expected_primary_skill: Optional[str] = None
    expected_ambiguity: Optional[bool] = None
    expected_escalation: Optional[bool] = None
    is_authorized: bool = False
    notes: str = ""


SCENARIOS: List[AskLightScenario] = [
    AskLightScenario(
        id="AL-01",
        name="Standard frontier query: ready ticket exists",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-parser.md"],
        ),
        user_request="What should I do next?",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        is_authorized=False,
        notes="Standard recommendation frontier without explicit command.",
    ),
    AskLightScenario(
        id="AL-02",
        name="Progress inquiry / where is project now",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["02-tests.md"],
            resolved_tickets=["01-parser.md"],
        ),
        user_request="Where is the project now? 汇报当前项目进度",
        expected_legal_actions=[],
        expected_fallback_action=None,
        expected_status="EXPLAIN",
        expected_primary_skill=None,
        is_authorized=False,
        notes="Status inquiry only; non-execution path.",
    ),
    AskLightScenario(
        id="AL-03",
        name="Workflow explanation request",
        state=CompactProjectState(initialized=True),
        user_request="Explain this workflow and the difference between tdd and prototype.",
        expected_legal_actions=[],
        expected_fallback_action=None,
        expected_status="EXPLAIN",
        expected_primary_skill=None,
        is_authorized=False,
        notes="Educational inquiry; no workflow transition.",
    ),
    AskLightScenario(
        id="AL-04",
        name="Explicit execution command: Go ahead",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-feature.md"],
        ),
        user_request="立刻开始执行工单。 Go ahead and implement now.",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="TRANSITION",
        expected_primary_skill="implement",
        is_authorized=True,
        notes="Deterministic command authorizes TRANSITION.",
    ),
    AskLightScenario(
        id="AL-05",
        name="Hesitant inquiry: Should we start implementing?",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-feature.md"],
        ),
        user_request="Should we start implementing? 现在开始做吗？",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        is_authorized=False,
        notes="Questioning intent must remain RECOMMEND (Jev cannot upgrade to TRANSITION).",
    ),
    AskLightScenario(
        id="AL-06",
        name="Advice only constraint: I only want advice",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-feature.md"],
        ),
        user_request="I only want advice, please do not start anything yet.",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        is_authorized=False,
        notes="Advice only; remains RECOMMEND.",
    ),
    AskLightScenario(
        id="AL-07",
        name="Initial project state: No SPEC exists",
        state=CompactProjectState(
            initialized=True,
            spec_exists=False,
            spec_active=False,
            clarification_ready=False,
        ),
        user_request="What is the next step for this project?",
        expected_legal_actions=["project-clarify"],
        expected_fallback_action="project-clarify",
        expected_status="RECOMMEND",
        expected_primary_skill="project-clarify",
        is_authorized=False,
        notes="No spec -> clarify first.",
    ),
    AskLightScenario(
        id="AL-08",
        name="Clarification complete: Clarification is ready",
        state=CompactProjectState(
            initialized=True,
            spec_exists=False,
            clarification_ready=True,
        ),
        user_request="Requirements are settled, what next?",
        expected_legal_actions=["project-spec"],
        expected_fallback_action="project-spec",
        expected_status="RECOMMEND",
        expected_primary_skill="project-spec",
        is_authorized=False,
        notes="Clarification handoff -> project-spec.",
    ),
    AskLightScenario(
        id="AL-09",
        name="Active SPEC exists but tickets do not",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=False,
        ),
        user_request="SPEC is authored. What next?",
        expected_legal_actions=["project-tickets"],
        expected_fallback_action="project-tickets",
        expected_status="RECOMMEND",
        expected_primary_skill="project-tickets",
        is_authorized=False,
        notes="Active spec without tickets -> project-tickets.",
    ),
    AskLightScenario(
        id="AL-10",
        name="Ready ticket exists at frontier",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["03-ui.md"],
            blocked_tickets=["04-backend.md"],
        ),
        user_request="Next step please.",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        is_authorized=False,
        notes="Unblocked ready ticket -> implement.",
    ),
    AskLightScenario(
        id="AL-11",
        name="All tickets resolved",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            all_tickets_resolved=True,
            resolved_tickets=["01.md", "02.md"],
        ),
        user_request="Implementation finished, what next?",
        expected_legal_actions=["project-review"],
        expected_fallback_action="project-review",
        expected_status="RECOMMEND",
        expected_primary_skill="project-review",
        is_authorized=False,
        notes="All resolved -> project-review.",
    ),
    AskLightScenario(
        id="AL-12",
        name="Stale review verdict",
        state=CompactProjectState(
            initialized=True,
            review_exists=True,
            review_verdict="PASS",
            review_freshness="stale",
        ),
        user_request="Can we release?",
        expected_legal_actions=["project-review"],
        expected_fallback_action="project-review",
        expected_status="RECOMMEND",
        expected_primary_skill="project-review",
        is_authorized=False,
        notes="Stale review invalidates PASS -> must re-review.",
    ),
    AskLightScenario(
        id="AL-13",
        name="Dirty working tree invalidating review",
        state=CompactProjectState(
            initialized=True,
            review_exists=True,
            review_verdict="PASS",
            working_tree_dirty=True,
        ),
        user_request="Next step?",
        expected_legal_actions=["project-review"],
        expected_fallback_action="project-review",
        expected_status="RECOMMEND",
        expected_primary_skill="project-review",
        is_authorized=False,
        notes="Dirty tree invalidates review freshness -> must re-review.",
    ),
    AskLightScenario(
        id="AL-14",
        name="Unknown ticket requested (fail-closed)",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01.md"],
        ),
        user_request="Implement ticket 99 please.",
        expected_legal_actions=[],
        expected_fallback_action=None,
        expected_status="BLOCKED",
        expected_primary_skill=None,
        is_authorized=False,
        notes="Unknown ticket 99 fails closed.",
    ),
    AskLightScenario(
        id="AL-15",
        name="Multiple active efforts without explicit target (fail-closed)",
        state=CompactProjectState(
            initialized=True,
            active_efforts=["feat-login", "feat-billing"],
            current_effort=None,
        ),
        user_request="What should we work on next?",
        expected_legal_actions=[],
        expected_fallback_action=None,
        expected_status="NEED_INPUT",
        expected_primary_skill=None,
        is_authorized=False,
        notes="Multiple active efforts require explicit disambiguation.",
    ),
    AskLightScenario(
        id="AL-16",
        name="Ambiguous user request with trade-offs",
        state=CompactProjectState(
            initialized=True,
            spec_exists=False,
        ),
        user_request="Maybe we should do auth, or maybe redesign the storage layer first, or just start writing code?",
        expected_legal_actions=["project-clarify"],
        expected_fallback_action="project-clarify",
        expected_status="RECOMMEND",
        expected_primary_skill="project-clarify",
        expected_ambiguity=True,
        is_authorized=False,
        notes="High ambiguity detected -> clarify.",
    ),
    AskLightScenario(
        id="AL-17",
        name="Complex architectural overhaul request",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["05-distributed-consensus.md"],
        ),
        user_request="Implement the distributed consensus engine with Raft leader election, multi-raft log replication, and split-brain recovery.",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        expected_escalation=True,
        is_authorized=False,
        notes="High architectural complexity -> escalation recommendation.",
    ),
]


def evaluate_scenario(scenario: AskLightScenario, client: Optional[Any] = None) -> Dict[str, Any]:
    """Evaluate one scenario and return observation report."""
    explicit_tgt = "99" if "99" in scenario.user_request else None
    legal = compute_legal_actions(scenario.state, scenario.user_request, explicit_target=explicit_tgt)

    rec = route_with_jev(legal, scenario.user_request, client=client)

    legal_ok = legal.allowed_actions == scenario.expected_legal_actions
    fallback_ok = legal.fallback_action == scenario.expected_fallback_action
    status_ok = rec.status == scenario.expected_status
    primary_ok = rec.primary_skill == scenario.expected_primary_skill

    # Invariant checks:
    # 1. Authority invariant: Jev output cannot grant TRANSITION
    authority_ok = True
    if not scenario.is_authorized and rec.status == "TRANSITION":
        authority_ok = False

    # 2. Singleton candidate skips Choice
    choice_skipped_ok = True
    if len(legal.allowed_actions) <= 1 and rec.semantic_judgments:
        if "next_action" in rec.semantic_judgments.questions_sent:
            choice_skipped_ok = False

    passed = legal_ok and fallback_ok and status_ok and primary_ok and authority_ok and choice_skipped_ok

    return {
        "id": scenario.id,
        "name": scenario.name,
        "passed": passed,
        "legal_actions_matched": legal_ok,
        "fallback_action_matched": fallback_ok,
        "status_matched": status_ok,
        "primary_skill_matched": primary_ok,
        "authority_invariant_held": authority_ok,
        "choice_skipped_for_singleton": choice_skipped_ok,
        "observed_status": rec.status,
        "observed_primary_skill": rec.primary_skill,
        "fallback_used": rec.fallback_used,
        "escalated": rec.escalated,
        "semantic_judgments": rec.semantic_judgments.model_dump() if rec.semantic_judgments else None,
    }


def run_ask_light_eval(client: Optional[Any] = None) -> Dict[str, Any]:
    """Run all 17 ask-light evaluation scenarios."""
    results = [evaluate_scenario(sc, client=client) for sc in SCENARIOS]
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "suite": "ask-light",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total if total > 0 else 0.0,
        "results": results,
    }
