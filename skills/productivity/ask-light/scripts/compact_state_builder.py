"""Compact state builder for ask-light.

Constructs a compact, token-efficient, sanitized structured dictionary for Jev System One queries:
  1. Zero raw repository files or whole file trees.
  2. No secrets, API keys, credentials, or raw code diffs.
  3. Strict input length capping and regex-based token redaction.
  4. Minimal essential facts: sanitized user_request, project readiness summary, known blockers, allowed actions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List
try:
    from .ask_light_models import CompactProjectState, LegalActionsResult
except ImportError:
    from ask_light_models import CompactProjectState, LegalActionsResult

SECRET_PATTERNS = [
    re.compile(r"(?:sk-[a-zA-Z0-9_\-]{16,}|ts-[a-zA-Z0-9_\-]{16,}|[A-Za-z0-9_\-]{32,}|bearer\s+[a-zA-Z0-9_\-\.]+)", re.IGNORECASE),
    re.compile(r"(?:api[_-]?key|secret|token|password|auth)\s*[:=]\s*[^\s]+", re.IGNORECASE),
]


def sanitize_user_request(text: str, max_chars: int = 350) -> str:
    """Sanitize user request: cap length and redact obvious tokens/secrets."""
    cleaned = text.strip()
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].rstrip() + "..."
    for pattern in SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    return cleaned


def build_compact_jev_state(
    legal_result: LegalActionsResult,
    user_request: str,
) -> Dict[str, Any]:
    """Build a compact, sanitized structured dictionary for Jev queries."""
    state = legal_result.compact_state or CompactProjectState()

    # Summarize implementation status
    total_tickets = len(state.ready_tickets) + len(state.blocked_tickets) + len(state.resolved_tickets)
    if state.all_tickets_resolved or (total_tickets > 0 and len(state.resolved_tickets) == total_tickets):
        impl_status = "complete"
    elif len(state.resolved_tickets) > 0:
        impl_status = "partial"
    elif len(state.ready_tickets) > 0:
        impl_status = "ready_to_start"
    elif total_tickets > 0:
        impl_status = "blocked_by_dependencies"
    else:
        impl_status = "no_tickets"

    # Summarize review status
    if state.review_exists:
        if state.review_verdict == "PASS":
            if state.review_freshness == "stale" or state.working_tree_dirty:
                rev_status = "stale_or_dirty"
            else:
                rev_status = "fresh_pass"
        else:
            rev_status = state.review_verdict or "in_progress"
    else:
        rev_status = "none"

    known_blockers: List[str] = []
    if legal_result.blocked_reason:
        known_blockers.append(legal_result.blocked_reason)
    if state.working_tree_dirty:
        known_blockers.append("working_tree_dirty")
    if state.review_freshness == "stale":
        known_blockers.append("stale_review_verdict")

    sanitized_request = sanitize_user_request(user_request)

    return {
        "user_request": sanitized_request,
        "project": {
            "initialized": state.initialized,
            "spec_active": state.spec_active,
            "clarification_ready": state.clarification_ready,
            "implementation_status": impl_status,
            "ready_tickets_count": len(state.ready_tickets),
            "resolved_tickets_count": len(state.resolved_tickets),
            "review_status": rev_status,
        },
        "known_blockers": known_blockers,
        "allowed_candidate_actions": legal_result.allowed_actions,
    }
