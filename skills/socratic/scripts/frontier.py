#!/usr/bin/env python3
"""Small machine-readable frontier engine for socratic.

This helper models the decision-state logic that `socratic` executes in the
conversation: compute the current actionable frontier, parse a batch reply,
and apply answers. It is test-support material, not a replacement for the
agent's full conversational judgment.
"""

from __future__ import annotations

import re
from typing import Any


class Decision:
    def __init__(
        self,
        id: str,
        question: str,
        options: list[dict[str, str]] | None = None,
        recommended: str = "",
        depends_on: list[str] | None = None,
        resolved: bool = False,
        answer: str = "",
        note: str = "",
    ) -> None:
        self.id = id
        self.question = question
        self.options = options or []
        self.recommended = recommended
        self.depends_on = depends_on or []
        self.resolved = resolved
        self.answer = answer
        self.note = note


def _resolved_ids(decisions: list[Decision]) -> set[str]:
    return {item.id for item in decisions if item.resolved}


def compute_frontier(decisions: list[Decision]) -> list[Decision]:
    resolved = _resolved_ids(decisions)
    return [
        item for item in decisions
        if not item.resolved and all(dep in resolved for dep in item.depends_on)
    ]


def parse_batch_response(text: str, frontier: list[Decision]) -> dict[str, str]:
    """Map a compact batch reply like `1B, 2A, 3C` to decision ids.

    Also accepts `Q1: ...`, `1: ...`, full prose, and a bare free-text answer
    when the frontier has exactly one unresolved decision.
    """
    answers: dict[str, str] = {}
    used_ranges: list[tuple[int, int]] = []

    def consume(match: re.Match[str]) -> None:
        used_ranges.append(match.span())

    for index, decision in enumerate(frontier, start=1):
        # Q1: ... or 1: ...
        for pattern in (
            rf"\bQ{index}\s*[:.\-]\s*(.+)",
            rf"\b{index}\s*[:.\-]\s*(.+)",
        ):
            match = re.search(pattern, text, re.I | re.S)
            if match:
                answers[decision.id] = match.group(1).strip()
                consume(match)
                break
        else:
            # Compact 1B / 1 B style, capturing a trailing qualifier when present.
            pattern = rf"(?<!\w){index}\s*([A-Za-z])(?!\w)"
            match = re.search(pattern, text)
            if match:
                answer = match.group(1).upper()
                rest = text[match.end():]
                if rest.strip():
                    next_token = re.search(r"(?<!\w)(?:\d+\s*[A-Za-z]|\d+\s*[:.\-]|Q\d+)", rest)
                    chunk = rest[:next_token.start()] if next_token else rest
                    chunk = chunk.strip().lstrip(",").strip().rstrip(",").strip()
                    if chunk:
                        answer += f", {chunk}"
                answers[decision.id] = answer
                consume(match)

    if not answers and len(frontier) == 1 and text.strip():
        answers[frontier[0].id] = text.strip()

    return answers


def apply_answers(decisions: list[Decision], answers: dict[str, str]) -> list[Decision]:
    by_id = {item.id: item for item in decisions}
    for decision_id, answer in answers.items():
        if decision_id in by_id and answer.strip():
            by_id[decision_id].resolved = True
            by_id[decision_id].answer = answer.strip()
    return decisions


def round_items(decisions: list[Decision]) -> list[dict[str, Any]]:
    return [
        {
            "id": item.id,
            "question": item.question,
            "options": item.options,
            "recommended": item.recommended,
            "depends_on": item.depends_on,
        }
        for item in compute_frontier(decisions)
    ]


def next_step(decisions: list[Decision]) -> str:
    if compute_frontier(decisions):
        return "ask-round"
    if any(not item.resolved for item in decisions):
        return "dependency-blocked"
    return "synthesize"


if __name__ == "__main__":
    import json
    import sys

    payload = json.load(sys.stdin)
    decisions = [
        Decision(
            id=item["id"],
            question=item["question"],
            options=item.get("options", []),
            recommended=item.get("recommended", ""),
            depends_on=item.get("depends_on", []),
            resolved=item.get("resolved", False),
            answer=item.get("answer", ""),
        )
        for item in payload.get("decisions", [])
    ]
    mode = payload.get("mode", "frontier")
    if mode == "frontier":
        print(json.dumps([item.id for item in compute_frontier(decisions)], ensure_ascii=False))
    elif mode == "parse":
        frontier = compute_frontier(decisions)
        print(json.dumps(parse_batch_response(payload.get("response", ""), frontier), ensure_ascii=False))
    else:
        raise SystemExit("unknown mode")