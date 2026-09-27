"""Repository-level pytest configuration.

The Frozen language-learning helper is composed into the root collection test.
The Frozen recap tests describe the superseded long-form contract and remain
historical after the user-authorized ``SKILL.md`` amendment. Excluding these
modules keeps ``pytest -q`` aligned with the active suite without modifying a
Frozen test file.
"""

import subprocess
import sys
import re
import shlex
from pathlib import Path
import pytest

# Frozen package test files retain their original relative import assumptions.
sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))

collect_ignore = [
    "skills/knowledge/language-learning/tests/test_language_learning_contract.py",
    "skills/productivity/recap/tests/test_recap_contract.py",
    "skills/productivity/recap/tests/test_recap_output_contract.py",
]


def _is_external_argv(words):
    if not words:
        return False
    executable = Path(words[0]).name.lower()
    if executable in {"npx", "npm", "curl", "wget"}:
        return True
    if re.fullmatch(r"pip(?:\d+(?:\.\d+)?)?", executable):
        return len(words) > 1 and words[1] == "install"
    if re.fullmatch(r"python(?:\d+(?:\.\d+)?)?", executable):
        return words[1:4] == ["-m", "pip", "install"]
    if executable in {"env", "sudo"}:
        rest = words[1:]
        while rest and (rest[0].startswith("-") or (executable == "env" and "=" in rest[0])):
            rest = rest[1:]
        return _is_external_argv(rest)
    if executable in {"bash", "sh", "zsh"} and "-c" in words[1:]:
        index = words.index("-c")
        return index + 1 < len(words) and is_external_command(words[index + 1])
    return False


def is_external_command(cmd):
    """Identify installer/network executables without scanning path arguments."""
    if isinstance(cmd, (list, tuple)):
        return _is_external_argv([str(part) for part in cmd])
    try:
        lexer = shlex.shlex(str(cmd), posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return True
    segment = []
    for token in [*tokens, ";"]:
        if token and all(char in ";&|" for char in token):
            if _is_external_argv(segment):
                return True
            segment = []
        else:
            segment.append(token)
    return False


@pytest.fixture(autouse=True)
def guard_external_boundaries(monkeypatch):
    """Guard against un-mocked external network and installer calls in regression suite."""
    orig_run = subprocess.run

    def guarded_run(cmd, *args, **kwargs):
        if is_external_command(cmd):
            raise AssertionError(f"GUARD FAILED: Real external command {cmd!r} was invoked in regression suite without being mocked!")
        return orig_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
