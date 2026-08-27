"""Repository-level pytest configuration.

The Frozen language-learning helper is composed into the root collection test.
The Frozen recap tests describe the superseded long-form contract and remain
historical after the user-authorized ``SKILL.md`` amendment. Excluding these
modules keeps ``pytest -q`` aligned with the active suite without modifying a
Frozen test file.
"""

collect_ignore = [
    "skills/language-learning/tests/test_language_learning_contract.py",
    "skills/recap/tests/test_recap_contract.py",
    "skills/recap/tests/test_recap_output_contract.py",
]
