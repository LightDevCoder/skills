"""Repository-level pytest configuration.

The Frozen skill suites under ``skills/language-learning/tests`` and
``skills/recap/tests`` are composed into the root collection tests as imported
helper modules; their module-level ``test_*`` helper functions are not intended
to be collected by pytest as standalone tests. Excluding them here keeps
``pytest -q`` collection clean without modifying any Frozen Skill directory.
"""

collect_ignore = [
    "skills/language-learning/tests/test_language_learning_contract.py",
    "skills/recap/tests/test_recap_contract.py",
    "skills/recap/tests/test_recap_output_contract.py",
]