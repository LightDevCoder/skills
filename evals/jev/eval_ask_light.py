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
    expected_execution_intent: Optional[bool] = None
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
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01.md"],
        ),
        user_request="Maybe we should do auth, or maybe redesign the storage layer first, or just start writing code?",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        expected_ambiguity=True,
        expected_escalation=None,
        is_authorized=False,
        notes="High ambiguity detected on implementable state -> recommends clarification alternative.",
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
        expected_ambiguity=None,
        expected_escalation=True,
        is_authorized=False,
        notes="High architectural complexity -> escalation recommendation to agent-config.",
    ),
    AskLightScenario(
        id="AL-18",
        name="Clear status question negative case (no false ambiguity)",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["02-tests.md"],
            resolved_tickets=["01-parser.md"],
        ),
        user_request="汇报当前工单状态与已完成测试进度",
        expected_legal_actions=[],
        expected_fallback_action=None,
        expected_status="EXPLAIN",
        expected_primary_skill=None,
        is_authorized=False,
        notes="Status query negative baseline: planner plans 0 queries.",
    ),
    AskLightScenario(
        id="AL-19",
        name="Negative ambiguity case: unambiguous disjunction query",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-parser.md"],
        ),
        user_request="Should we implement ticket 01 or tell me if ticket 01 is ready?",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        expected_ambiguity=False,
        is_authorized=False,
        notes="Phrasing contains ' or ' but semantics are clear (not material ambiguity).",
    ),
    AskLightScenario(
        id="AL-20",
        name="Negative escalation case: simple refactor task",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-parser.md"],
        ),
        user_request="Implement ticket 01: simple refactor to fix typo in README doc comments.",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        expected_escalation=False,
        is_authorized=False,
        notes="Phrasing contains 'refactor' but task is simple typo fix (not deep architectural escalation).",
    ),
    AskLightScenario(
        id="AL-21",
        name="Adversarial: what is next, do not execute",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-parser.md"],
        ),
        user_request="What's next? Do not execute.",
        expected_legal_actions=["implement"],
        expected_fallback_action="implement",
        expected_status="RECOMMEND",
        expected_primary_skill="implement",
        is_authorized=False,
        notes="Explicit negative execution constraint; planner plans 0 queries.",
    ),
    AskLightScenario(
        id="AL-22",
        name="Adversarial: explain whether implementation is next",
        state=CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["01-parser.md"],
        ),
        user_request="Can you explain whether implementation is next?",
        expected_legal_actions=[],
        expected_fallback_action=None,
        expected_status="EXPLAIN",
        expected_primary_skill=None,
        is_authorized=False,
        notes="Explanation query about workflow step remains EXPLAIN path (0 queries).",
    ),
]


def evaluate_scenario(scenario: AskLightScenario, client: Optional[Any] = None) -> Dict[str, Any]:
    """Evaluate one scenario and return observation report separating safety from semantics."""
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

    workflow_safety_passed = legal_ok and fallback_ok and status_ok and primary_ok and authority_ok and choice_skipped_ok

    # Semantic evaluation (participates when live Jev or mock semantic judgments are available)
    # Tri-state: "PASS", "FAIL", "NOT_EVALUATED"
    semantic_status = "NOT_EVALUATED"
    ambiguity_matched = None
    escalation_matched = None

    if rec.semantic_judgments and not rec.fallback_used:
        qs_sent = rec.semantic_judgments.questions_sent
        evaluated_any = False
        all_matched = True

        if "has_material_ambiguity" in qs_sent:
            evaluated_any = True
            if scenario.expected_ambiguity is not None:
                observed_ambig = (
                    rec.semantic_judgments.ambiguity_probability is not None
                    and rec.semantic_judgments.ambiguity_probability >= 0.65
                )
                ambiguity_matched = (observed_ambig == scenario.expected_ambiguity)
                if not ambiguity_matched:
                    all_matched = False
            else:
                all_matched = False

        if "needs_deep_reasoning_escalation" in qs_sent:
            evaluated_any = True
            if scenario.expected_escalation is not None:
                observed_escala = rec.escalated
                escalation_matched = (observed_escala == scenario.expected_escalation)
                if not escalation_matched:
                    all_matched = False
            else:
                all_matched = False

        if "next_action" in qs_sent:
            evaluated_any = True
            choice_ok = (rec.primary_skill == scenario.expected_primary_skill)
            if not choice_ok:
                all_matched = False

        if evaluated_any:
            semantic_status = "PASS" if all_matched else "FAIL"
        else:
            semantic_status = "NOT_EVALUATED"
    else:
        semantic_status = "NOT_EVALUATED"

    # Overall pass: safety must pass; and if semantics were evaluated, semantics must not have failed
    overall_passed = workflow_safety_passed and (semantic_status != "FAIL")

    return {
        "id": scenario.id,
        "name": scenario.name,
        "passed": overall_passed,
        "workflow_safety_passed": workflow_safety_passed,
        "semantic_status": semantic_status,
        "semantic_passed": (semantic_status == "PASS"),
        "legal_actions_matched": legal_ok,
        "fallback_action_matched": fallback_ok,
        "status_matched": status_ok,
        "primary_skill_matched": primary_ok,
        "authority_invariant_held": authority_ok,
        "choice_skipped_for_singleton": choice_skipped_ok,
        "ambiguity_matched": ambiguity_matched,
        "escalation_matched": escalation_matched,
        "observed_status": rec.status,
        "observed_primary_skill": rec.primary_skill,
        "fallback_used": rec.fallback_used,
        "escalated": rec.escalated,
        "semantic_judgments": rec.semantic_judgments.model_dump() if rec.semantic_judgments else None,
    }


def run_ask_light_eval(client: Optional[Any] = None) -> Dict[str, Any]:
    """Run all ask-light evaluation scenarios with confusion matrix metrics."""
    results = [evaluate_scenario(sc, client=client) for sc in SCENARIOS]
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    safety_passed = sum(1 for r in results if r["workflow_safety_passed"])

    semantic_evaluated = sum(1 for r in results if r["semantic_status"] in ("PASS", "FAIL"))
    semantic_not_evaluated = sum(1 for r in results if r["semantic_status"] == "NOT_EVALUATED")
    semantic_passed = sum(1 for r in results if r["semantic_status"] == "PASS")
    semantic_failed = sum(1 for r in results if r["semantic_status"] == "FAIL")
    semantic_acc = (semantic_passed / semantic_evaluated) if semantic_evaluated > 0 else None

    # Compute confusion matrix for binary semantic dimensions
    confusion_matrices = {
        "ambiguity": {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "total": 0},
        "escalation": {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "total": 0},
    }

    for sc, res in zip(SCENARIOS, results):
        sj = res.get("semantic_judgments")
        if not sj or res.get("fallback_used"):
            continue

        if sc.expected_ambiguity is not None and sj.get("ambiguity_probability") is not None:
            obs = sj["ambiguity_probability"] >= 0.65
            exp = sc.expected_ambiguity
            confusion_matrices["ambiguity"]["total"] += 1
            if exp and obs: confusion_matrices["ambiguity"]["tp"] += 1
            elif not exp and obs: confusion_matrices["ambiguity"]["fp"] += 1
            elif not exp and not obs: confusion_matrices["ambiguity"]["tn"] += 1
            elif exp and not obs: confusion_matrices["ambiguity"]["fn"] += 1

        if sc.expected_escalation is not None and sj.get("escalation_probability") is not None:
            obs = res.get("escalated", False)
            exp = sc.expected_escalation
            confusion_matrices["escalation"]["total"] += 1
            if exp and obs: confusion_matrices["escalation"]["tp"] += 1
            elif not exp and obs: confusion_matrices["escalation"]["fp"] += 1
            elif not exp and not obs: confusion_matrices["escalation"]["tn"] += 1
            elif exp and not obs: confusion_matrices["escalation"]["fn"] += 1

    return {
        "suite": "ask-light",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total if total > 0 else 0.0,
        "workflow_safety_passed": safety_passed,
        "workflow_safety_accuracy": safety_passed / total if total > 0 else 0.0,
        "semantic_evaluated": semantic_evaluated,
        "semantic_not_evaluated": semantic_not_evaluated,
        "semantic_passed": semantic_passed,
        "semantic_failed": semantic_failed,
        "semantic_accuracy": semantic_acc,
        "confusion_matrices": confusion_matrices,
        "results": results,
    }
