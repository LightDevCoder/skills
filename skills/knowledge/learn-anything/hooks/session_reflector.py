#!/usr/bin/env python3
"""Detect reusable skill-learning candidates in a completed session transcript."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CORRECTION_PATTERNS = [
    r"\bcorrection\b",
    r"\bactually\b",
    r"\binstead\b",
    r"\bnot .* but\b",
    r"\bdo not\b",
    r"\bdon't\b",
    r"\bfailure mode\b",
    r"\bfailed because\b",
    r"\bregression\b",
    r"\bwrong\b",
    r"\bblocked\b",
    r"不是.*而是",
    r"不要",
    r"错误",
    r"失败",
    r"修正",
    r"纠正",
    r"反复",
]

REUSE_PATTERNS = [
    r"\breuse\b",
    r"\breusable\b",
    r"\brepeatable\b",
    r"\bfuture agent",
    r"\bnext time\b",
    r"\balways\b",
    r"\bnever\b",
    r"\bworkflow\b",
    r"\bprocess\b",
    r"\brule\b",
    r"\bAGENTS\.md\b",
    r"复用",
    r"以后",
    r"下次",
    r"未来.*agent",
    r"流程",
    r"规则",
    r"总是",
]

EXPLICIT_SKILL_PATTERNS = [
    r"\bcreate (?:a )?skill\b",
    r"\bupdate (?:the )?skill\b",
    r"\bskill creator\b",
    r"\blearn-anything\b",
    r"创建.*skill",
    r"沉淀.*skill",
    r"沉淀.*流程",
]

ARTIFACT_PATTERNS = [
    r"```",
    r"`[^`]+`",
    r"\b[a-zA-Z]:\\",
    r"/[\w.-]+/[\w./-]+",
    r"\b(?:python|pytest|npm|pnpm|git|gh|cargo)\b",
    r"^\s*(?:[-*]|\d+\.)\s+",
]


def _read_input(argv_text: list[str]) -> dict[str, Any]:
    if argv_text:
        text = " ".join(argv_text)
    else:
        text = sys.stdin.read()

    text = text.strip()
    if not text:
        return {"transcript": ""}

    if Path(text).exists() and Path(text).is_file():
        text = Path(text).read_text(encoding="utf-8")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"transcript": text}

    if isinstance(data, dict):
        return data
    return {"transcript": str(data)}


def _combined_text(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("transcript", "request", "result", "notes", "source"):
        value = data.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif value is not None:
            parts.append(json.dumps(value, ensure_ascii=False))
    return "\n".join(parts)


def _matches(text: str, patterns: list[str]) -> list[str]:
    return [
        pattern
        for pattern in patterns
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    ]


def reflect(data: dict[str, Any]) -> dict[str, Any]:
    text = _combined_text(data)
    compact = re.sub(r"\s+", " ", text).strip()

    correction = _matches(text, CORRECTION_PATTERNS)
    reuse = _matches(text, REUSE_PATTERNS)
    explicit = _matches(text, EXPLICIT_SKILL_PATTERNS)
    artifact = _matches(text, ARTIFACT_PATTERNS)
    length_score = min(len(compact) // 220, 3)

    score = len(correction) * 3 + len(reuse) * 3 + len(explicit) * 5 + len(artifact) + length_score
    reasons: list[str] = []
    if explicit:
        reasons.append("explicit skill request")
    if correction:
        reasons.append("corrections or failure modes detected")
    if reuse:
        reasons.append("future reuse language detected")
    if artifact:
        reasons.append("commands, paths, code, or structured notes detected")
    if len(compact) < 40:
        reasons.append("sparse transcript")

    if explicit and (reuse or correction or len(compact) > 120):
        decision = "create_skill"
        confidence = min(0.97, 0.76 + score * 0.02)
    elif score >= 8 and correction and (reuse or artifact):
        decision = "summarize_candidate"
        confidence = min(0.9, 0.58 + score * 0.025)
    else:
        decision = "ignore"
        confidence = 0.22 if len(compact) < 40 else min(0.5, 0.25 + score * 0.025)

    return {
        "decision": decision,
        "confidence": round(confidence, 2),
        "score": score,
        "reasons": reasons,
        "signals": {
            "explicit_skill": len(explicit),
            "correction_or_failure": len(correction),
            "reuse": len(reuse),
            "artifact": len(artifact),
            "length_score": length_score,
        },
        "candidate_summary": _candidate_summary(text) if decision != "ignore" else "",
    }


def _candidate_summary(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    evidence = []
    for line in lines:
        if any(token in line.lower() for token in ("do not", "instead", "failure", "workflow", "next time", "不要", "失败", "流程", "规则")):
            evidence.append(line)
        if len(evidence) == 3:
            break
    if not evidence:
        evidence = lines[:2]
    return " | ".join(evidence)[:500]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="*", help="Raw text, JSON, or a file path")
    args = parser.parse_args()

    result = reflect(_read_input(args.text))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
