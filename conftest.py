"""Repository-level pytest configuration.

The Frozen language-learning helper is composed into the root collection test.
The Frozen recap tests describe the superseded long-form contract and remain
historical after the user-authorized ``SKILL.md`` amendment. Excluding these
modules keeps ``pytest -q`` aligned with the active suite without modifying a
Frozen test file.
"""

import sys
from pathlib import Path

# Frozen package test files retain their original relative import assumptions.
sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))

collect_ignore = [
    "skills/knowledge/language-learning/tests/test_language_learning_contract.py",
    "skills/productivity/recap/tests/test_recap_contract.py",
    "skills/productivity/recap/tests/test_recap_output_contract.py",
]
