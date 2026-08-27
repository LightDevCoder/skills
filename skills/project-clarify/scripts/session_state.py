#!/usr/bin/env python3
"""Lifecycle contract for one-invocation project-clarify sessions.

`project-clarify` matches `clarify`'s continuous-session interaction model:
one explicit `$project-clarify` starts the stage, ordinary replies continue
the frontier, and only shared-understanding confirmation (or explicit exit /
workflow switch) produces the bounded handoff and stop.
"""

from __future__ import annotations

POLICY = {
    "compositionTarget": "socratic",
    "ordinaryRepliesContinue": True,
    "autoChainUserInvokedSkills": False,
    "factWork": "report-only",
    "completionRequiresConfirmation": True,
    "handoffAtCompletion": True,
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
        raise ValueError(f"invalid project-clarify transition: {session.status} + {event}")
    return Session(allowed[session.status][event])