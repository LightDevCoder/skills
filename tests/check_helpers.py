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
        if not re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE):
            self.failures.append(f"{label}: expected /{pattern}/")

    def require_no_match(self, label: str, text: str, pattern: str) -> None:
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
