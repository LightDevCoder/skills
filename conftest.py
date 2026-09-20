"""Repository-level pytest configuration.

The Frozen language-learning helper is composed into the root collection test.
The Frozen recap tests describe the superseded long-form contract and remain
historical after the user-authorized ``SKILL.md`` amendment. Excluding these
modules keeps ``pytest -q`` aligned with the active suite without modifying a
Frozen test file.
"""

import subprocess
import sys
from pathlib import Path
import pytest

# Frozen package test files retain their original relative import assumptions.
sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))

collect_ignore = [
    "skills/knowledge/language-learning/tests/test_language_learning_contract.py",
    "skills/productivity/recap/tests/test_recap_contract.py",
    "skills/productivity/recap/tests/test_recap_output_contract.py",
]


@pytest.fixture(autouse=True)
def guard_external_boundaries(monkeypatch):
    """Guard against un-mocked external network and installer calls in regression suite."""
    orig_run = subprocess.run

    def guarded_run(cmd, *args, **kwargs):
        cmd_str = " ".join(str(c) for c in (cmd if isinstance(cmd, (list, tuple)) else [cmd]))
        for blocked in ("npx", "npm", "pip install", "curl", "wget"):
            if blocked in cmd_str:
                raise AssertionError(f"GUARD FAILED: Real external command '{cmd_str}' was invoked in regression suite without being mocked!")
        return orig_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)

