#!/usr/bin/env python3
"""Lifecycle contract for one-invocation clarification sessions."""

from __future__ import annotations

POLICY = {
    "compositionTarget": "socratic",
    "ordinaryRepliesContinue": True,
    "autoChainUserInvokedSkills": False,
    "factWork": "report-only",
    "completionRequiresConfirmation": True,
}


class Session:
    def __init__(self, status: str = "inactive") -> None:
        self.status = status


def transition(session: Session, event: str) -> Session:
    allowed = {
        "inactive": {"invoke": "active"},
        "active": {"answer": "active", "synthesize": "awaiting-confirmation", "leave": "done"},
        "awaiting-confirmation": {"confirm": "done", "correct": "active", "leave": "done"},
        "done": {},
    }
    if event not in allowed.get(session.status, {}):
        raise ValueError(f"invalid clarification transition: {session.status} + {event}")
    return Session(allowed[session.status][event])
