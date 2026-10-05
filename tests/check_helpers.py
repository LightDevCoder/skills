"""Shared assertion harness for the first-party collection tests.

Cross-platform replacement for the PowerShell assert helpers. Every test
module reports (assertions, failures) so that suites can be composed exactly
like the old dot-sourced PowerShell scripts.
"""

from __future__ import annotations

import re
from pathlib import Path


class Checks:
    def __init__(self) -> None:
        self.assertions = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.assertions += 1
        if not condition:
            self.failures.append(message)

    def require_file(self, root: Path, path: str, label: str) -> None:
        self.check((root / path).is_file(), f"{label}: missing file {path}")

    def require_match(self, label: str, text: str, pattern: str) -> None:
        self.assertions += 1
        if not re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE):
            self.failures.append(f"{label}: expected /{pattern}/")

    def require_no_match(self, label: str, text: str, pattern: str) -> None:
        self.assertions += 1
        if re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE):
            self.failures.append(f"{label}: must not contain /{pattern}/")

    def finish(self, suite: str, zero_allowed: bool = False) -> None:
        if self.assertions == 0 and not zero_allowed:
            raise AssertionError(f"{suite}=FAIL (zero assertions)")
        if self.failures:
            raise AssertionError(
                f"{suite}=FAIL ({len(self.failures)} failures, {self.assertions} assertions)\n"
                + "\n".join(f"FAIL: {f}" for f in self.failures)
            )


def read(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def package_dir(root: Path, name: str) -> Path:
    """Resolve exactly one categorized package by its stable skill name."""
    matches = list((root / "skills").glob(f"*/{name}/SKILL.md"))
    if len(matches) != 1:
        raise ValueError(f"expected one package for {name}, found {len(matches)}")
    return matches[0].parent


# Read-boundary mapping for immutable historical evidence; never a callable alias.
HISTORICAL_NAMES = {
    "implement": "light-implement", "code-review": "light-code-review",
    "research": "light-research", "prototype": "light-prototype", "tdd": "light-tdd",
    "diagnosing-bugs": "light-diagnosing-bugs", "wizard": "light-wizard",
    "handoff": "light-handoff", "teach": "light-teach",
    "to-questionnaire": "light-to-questionnaire", "wait-what": "light-wait-what",
    "writing-for-agents": "light-writing-for-agents",
}


def relocated_path(root: Path, relative: str) -> Path:
    """Resolve a legacy source path in immutable pre-migration evidence."""
    path = root / relative
    if path.exists():
        return path
    parts = Path(relative).parts
    if len(parts) >= 2 and parts[0] == "skills":
        try:
            name_index = 2 if len(parts) >= 3 and parts[1] in {"engineering", "knowledge", "productivity", "project", "review", "thinking", "writing"} else 1
            name = HISTORICAL_NAMES.get(parts[name_index], parts[name_index])
            return package_dir(root, name).joinpath(*parts[name_index + 1:])
        except ValueError:
            pass
    return path
