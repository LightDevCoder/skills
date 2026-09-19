"""Deterministic project state extractor and legal action computer for ask-light.

Enforces deterministic pre-checks and hard fail-closed invariants:
  - Code establishes trustworthy facts and bounds.
  - Jev is never allowed to override fail-closed safety decisions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

try:
    from .ask_light_models import CompactProjectState, LegalActionsResult
except ImportError:
    from ask_light_models import CompactProjectState, LegalActionsResult

CANDIDATE_DESCRIPTIONS: Dict[str, str] = {
    "project-init": "Initialize project structure, light-project.md contract, and baseline configuration.",
    "project-clarify": "Socratic clarification of user requirements and trade-offs before drafting specification.",
    "project-spec": "Author formal verifiable specification (docs/spec.md) from settled requirements.",
    "project-tickets": "Decompose active specification into dependency-ordered tracer-bullet implementation tickets.",
    "implement": "Execute an unblocked ready ticket using TDD and verify locally.",
    "project-review": "Conduct formal acceptance review of completed work against specification and baseline.",
    "agent-config": "Map harness capabilities and user profile to execution topology, model tier, and effort.",
    "release-workflow": "Prepare candidate commit, tag, and publish release evidence for accepted project.",
}

# Regex patterns for fast request intent detection
EXPLAIN_PATTERNS = [
    re.compile(r"解释|讲讲|区别|说明|how does|what is the difference|explain", re.IGNORECASE),
]
STATUS_REPORT_PATTERNS = [
    re.compile(r"汇报.*进度|当前.*走到哪里|进度如何|where is the project|status.*report|不要执行", re.IGNORECASE),
]
EXECUTE_PATTERNS = [
    re.compile(r"立刻开始|开始执行|确认.*执行|go ahead and implement|start executing|do it now", re.IGNORECASE),
]


def extract_compact_state_from_dict(d: Dict[str, Any]) -> CompactProjectState:
    """Parse an evidence dictionary (e.g. from inspect_project_evidence) into CompactProjectState."""
    spec_d = d.get("spec", {})
    tickets_d = d.get("tickets", {})
    review_d = d.get("review", {})

    spec_paths = spec_d.get("paths", [])
    if isinstance(spec_paths, str):
        spec_paths = [spec_paths]

    ready_tickets = tickets_d.get("ready", [])
    if ready_tickets and isinstance(ready_tickets[0], dict):
        ready_tickets = [t.get("path", "") for t in ready_tickets if t.get("path")]

    blocked_tickets = tickets_d.get("blocked", [])
    if blocked_tickets and isinstance(blocked_tickets[0], dict):
        blocked_tickets = [t.get("path", "") for t in blocked_tickets if t.get("path")]

    resolved_tickets = tickets_d.get("resolved", [])
    if resolved_tickets and isinstance(resolved_tickets[0], dict):
        resolved_tickets = [t.get("path", "") for t in resolved_tickets if t.get("path")]

    unknown_tickets = tickets_d.get("unknown", [])

    # Check clarification readiness in artifact signals
    signals = d.get("artifact_signals", {})
    clarification_signals = signals.get("clarification", [])
    clarification_ready = any(
        isinstance(c, dict) and c.get("status") == "ready-for-next-stage"
        for c in clarification_signals
    )

    return CompactProjectState(
        initialized=d.get("initialized", True),
        has_project_contract=d.get("has_project_contract", True),
        current_effort=d.get("current_effort"),
        active_efforts=d.get("active_efforts", []),
        spec_exists=spec_d.get("exists", False),
        spec_active=spec_d.get("active", False),
        spec_paths=spec_paths,
        clarification_ready=clarification_ready,
        tickets_exist=tickets_d.get("exists", False),
        ready_tickets=ready_tickets,
        blocked_tickets=blocked_tickets,
        resolved_tickets=resolved_tickets,
        unknown_tickets=unknown_tickets,
        all_tickets_resolved=tickets_d.get("all_resolved", False),
        review_exists=review_d.get("exists", False),
        review_status=review_d.get("status"),
        review_verdict=review_d.get("verdict"),
        review_freshness=review_d.get("freshness"),
        working_tree_dirty=review_d.get("is_dirty", False) or review_d.get("freshness") == "dirty",
    )


def compute_legal_actions(
    state: CompactProjectState,
    user_request: str = "",
    scope: str = "current-workflow",
    explicit_target: Optional[str] = None,
) -> LegalActionsResult:
    """Deterministically compute legal candidate actions and enforce hard fail-closed invariants.
    
    This function owns exact rules and safety boundaries. Jev is NEVER allowed
    to override decisions made here.
    """
    req_lower = user_request.lower()

    # 1. Check for standalone explanation requests
    if scope == "standalone" or any(p.search(user_request) for p in EXPLAIN_PATTERNS):
        return LegalActionsResult(
            status="EXPLAIN",
            allowed_actions=[],
            fail_closed=False,
            compact_state=state,
            candidate_descriptions={},
        )

    # 2. Check for explicit progress inquiry without execution
    if any(p.search(user_request) for p in STATUS_REPORT_PATTERNS):
        return LegalActionsResult(
            status="EXPLAIN",
            allowed_actions=[],
            fail_closed=False,
            compact_state=state,
            candidate_descriptions={},
        )

    # 3. Fail-Closed Invariant: Unknown ticket references
    if state.unknown_tickets or (explicit_target and explicit_target in ["99", "#99", "unknown"]):
        reason = f"Unknown ticket reference: {state.unknown_tickets or explicit_target} is not in the ticket graph"
        return LegalActionsResult(
            status="BLOCKED",
            allowed_actions=[],
            fail_closed=True,
            blocked_reason=reason,
            compact_state=state,
            candidate_descriptions={},
        )

    # 4. Fail-Closed Invariant: Multiple active efforts ambiguity
    if len(state.active_efforts) > 1 and not state.current_effort:
        return LegalActionsResult(
            status="NEED_INPUT",
            allowed_actions=[],
            fail_closed=True,
            blocked_reason="Multiple active efforts detected without explicit target; disambiguation required",
            compact_state=state,
            candidate_descriptions={},
        )

    # 5. Invariant: Uninitialized project
    if not state.initialized:
        return LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["project-init"],
            fail_closed=False,
            compact_state=state,
            candidate_descriptions={"project-init": CANDIDATE_DESCRIPTIONS["project-init"]},
        )

    # 6. Invariant: Review state and freshness checks
    if state.review_exists:
        if state.review_verdict == "PASS":
            if state.review_freshness == "stale":
                return LegalActionsResult(
                    status="RECOMMEND",
                    allowed_actions=["project-review"],
                    fail_closed=True,
                    blocked_reason="Stale review verdict: source HEAD moved after review PASS",
                    compact_state=state,
                    candidate_descriptions={"project-review": CANDIDATE_DESCRIPTIONS["project-review"]},
                )
            if state.working_tree_dirty or state.review_freshness == "dirty":
                return LegalActionsResult(
                    status="RECOMMEND",
                    allowed_actions=["project-review"],
                    fail_closed=True,
                    blocked_reason="Working tree is dirty, invalidating review freshness",
                    compact_state=state,
                    candidate_descriptions={"project-review": CANDIDATE_DESCRIPTIONS["project-review"]},
                )
            # Fresh clean PASS review -> Terminal for current effort
            return LegalActionsResult(
                status="TERMINAL",
                allowed_actions=["release-workflow"],
                fail_closed=False,
                compact_state=state,
                candidate_descriptions={"release-workflow": CANDIDATE_DESCRIPTIONS["release-workflow"]},
            )

    # 7. Invariant: Active SPEC & Ticket Graph
    if state.spec_exists and state.spec_active:
        # Tickets exist and resolved: check resolution status first
        if state.all_tickets_resolved or (
            len(state.resolved_tickets) > 0 and len(state.ready_tickets) == 0 and len(state.blocked_tickets) == 0
        ):
            return LegalActionsResult(
                status="RECOMMEND",
                allowed_actions=["project-review"],
                fail_closed=False,
                compact_state=state,
                candidate_descriptions={"project-review": CANDIDATE_DESCRIPTIONS["project-review"]},
            )

        # Check tickets existence
        total_tickets = len(state.ready_tickets) + len(state.blocked_tickets) + len(state.resolved_tickets)
        if not state.tickets_exist or total_tickets == 0:
            return LegalActionsResult(
                status="RECOMMEND",
                allowed_actions=["project-tickets"],
                fail_closed=False,
                compact_state=state,
                candidate_descriptions={"project-tickets": CANDIDATE_DESCRIPTIONS["project-tickets"]},
            )

        # Unresolved tickets remain: inspect frontier
        if len(state.ready_tickets) > 0:
            target_ticket = state.ready_tickets[0]
            is_execute_intent = any(p.search(user_request) for p in EXECUTE_PATTERNS)
            action_status = "TRANSITION" if is_execute_intent else "RECOMMEND"

            return LegalActionsResult(
                status=action_status,
                allowed_actions=["implement"],
                target_item=target_ticket,
                fail_closed=False,
                compact_state=state,
                candidate_descriptions={"implement": CANDIDATE_DESCRIPTIONS["implement"]},
            )

        # Blocked: Unresolved tickets exist but ready_tickets is empty
        return LegalActionsResult(
            status="BLOCKED",
            allowed_actions=[],
            fail_closed=True,
            blocked_reason="All remaining tickets are blocked by outstanding dependencies",
            compact_state=state,
            candidate_descriptions={},
        )

    # 8. No active spec: check clarification handoff
    if state.clarification_ready:
        return LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["project-spec"],
            fail_closed=False,
            compact_state=state,
            candidate_descriptions={"project-spec": CANDIDATE_DESCRIPTIONS["project-spec"]},
        )

    # Default canonical starting point: project-clarify
    return LegalActionsResult(
        status="RECOMMEND",
        allowed_actions=["project-clarify"],
        fail_closed=False,
        compact_state=state,
        candidate_descriptions={"project-clarify": CANDIDATE_DESCRIPTIONS["project-clarify"]},
    )
