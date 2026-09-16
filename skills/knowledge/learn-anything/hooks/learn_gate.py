#!/usr/bin/env python3
"""Classify whether an incoming task should trigger learn-anything behavior."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPLICIT_SKILL_PATTERNS = [
    r"\bcreate (?:a )?skill\b",
    r"\bmake (?:a )?skill\b",
    r"\bupdate (?:the )?skill\b",
    r"\bturn .{0,80} into (?:a )?skill\b",
    r"\bskill creator\b",
    r"\$learn-anything\b",
    r"\$skill-creator\b",
    r"创建\s*skill",
    r"创建.*技能",
    r"沉淀.*流程",
    r"沉淀.*skill",
    r"沉淀.*技能",
    r"变成.*skill",
    r"变成.*技能",
]

ONE_OFF_PATTERNS = [
    r"\btranslate\b",
    r"\btranslation\b",
    r"\brewrite this sentence\b",
    r"\bwhat time\b",
    r"\bcurrent time\b",
    r"\bweather\b",
    r"\bforecast\b",
    r"翻译",
    r"几点",
    r"现在.*时间",
    r"天气",
]

WORKFLOW_PATTERNS = [
    r"\bworkflow\b",
    r"\bprocess\b",
    r"\bplaybook\b",
    r"\brunbook\b",
    r"\brepo\b",
    r"\bworkspace\b",
    r"\bfolder\b",
    r"\bproject\b",
    r"\bAGENTS\.md\b",
    r"\bREADME\b",
    r"工作流",
    r"流程",
    r"项目",
    r"文件夹",
    r"仓库",
    r"路径",
    r"规范",
    r"规则",
]

REUSE_PATTERNS = [
    r"\breusable\b",
    r"\brepeatable\b",
    r"\bnext time\b",
    r"\bfuture agent",
    r"\bfuture agents",
    r"\bagent should\b",
    r"\balways\b",
    r"\bnever\b",
    r"以后",
    r"下次",
    r"未来.*agent",
    r"复用",
    r"重复",
    r"每次",
    r"总是",
    r"不要",
]

SOURCE_RICH_PATTERNS = [
    r"`[^`]+`",
    r"```",
    r"\b[a-zA-Z]:\\",
    r"/[\w.-]+/[\w./-]+",
    r"\b(?:python|pytest|npm|pnpm|git|gh|cargo)\b",
    r"^\s*(?:[-*]|\d+\.)\s+",
]


@dataclass(frozen=True)
class PatternScore:
    count: int
    matches: list[str]


def _read_input(argv_text: list[str]) -> dict[str, Any]:
    if argv_text:
        text = " ".join(argv_text)
    else:
        text = sys.stdin.read()

    text = text.strip()
    if not text:
        return {"request": ""}

    if Path(text).exists() and Path(text).is_file():
        text = Path(text).read_text(encoding="utf-8")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"request": text}

    if isinstance(data, dict):
        return data
    return {"request": str(data)}


def _combined_text(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("request", "context", "source", "transcript", "notes"):
        value = data.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif value is not None:
            parts.append(json.dumps(value, ensure_ascii=False))
    return "\n".join(parts)


def _score_patterns(text: str, patterns: list[str]) -> PatternScore:
    matches: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            matches.append(pattern)
    return PatternScore(count=len(matches), matches=matches)


def classify(data: dict[str, Any]) -> dict[str, Any]:
    text = _combined_text(data)
    compact = re.sub(r"\s+", " ", text).strip()

    explicit = _score_patterns(text, EXPLICIT_SKILL_PATTERNS)
    one_off = _score_patterns(text, ONE_OFF_PATTERNS)
    workflow = _score_patterns(text, WORKFLOW_PATTERNS)
    reuse = _score_patterns(text, REUSE_PATTERNS)
    source = _score_patterns(text, SOURCE_RICH_PATTERNS)

    length_score = min(len(compact) // 140, 3)
    reusable_score = explicit.count * 5 + workflow.count * 2 + reuse.count * 2 + source.count + length_score
    one_off_score = one_off.count * 4

    reasons: list[str] = []
    if explicit.count:
        reasons.append("explicit skill creation/update language")
    if workflow.count:
        reasons.append("workflow or project/folder signals")
    if reuse.count:
        reasons.append("future reuse or agent-rule language")
    if source.count:
        reasons.append("source artifact, path, command, or structured-note signals")
    if one_off.count:
        reasons.append("one-off lookup or transformation language")
    if len(compact) < 20:
        reasons.append("sparse input")

    if explicit.count:
        decision = "create_or_update_skill"
        confidence = min(0.98, 0.78 + explicit.count * 0.05 + reuse.count * 0.03)
    elif one_off_score >= 4 and reusable_score < 5:
        decision = "normal_task"
        confidence = 0.9
    elif reusable_score >= 7:
        decision = "observe_and_summarize"
        confidence = min(0.88, 0.55 + reusable_score * 0.035)
    else:
        decision = "normal_task"
        confidence = 0.28 if len(compact) < 30 else 0.45

    return {
        "decision": decision,
        "confidence": round(confidence, 2),
        "score": reusable_score,
        "one_off_score": one_off_score,
        "reasons": reasons,
        "signals": {
            "explicit_skill": explicit.count,
            "workflow": workflow.count,
            "reuse": reuse.count,
            "source_rich": source.count,
            "one_off": one_off.count,
            "length_score": length_score,
        },
        "recommended_next_step": _next_step(decision, confidence),
    }


def _next_step(decision: str, confidence: float) -> str:
    if decision == "create_or_update_skill":
        return "Use learn-anything to create or update a Skill Creator compatible skill."
    if decision == "observe_and_summarize":
        return "Perform the task normally while preserving reusable workflow evidence for post-task reflection."
    if confidence < 0.4:
        return "Treat as a normal task unless the user provides clearer reusable-learning intent."
    return "Handle as a normal one-off task."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="*", help="Raw text, JSON, or a file path")
    args = parser.parse_args()

    result = classify(_read_input(args.text))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
