"""The test runner's network guard must inspect commands, not argument text."""

import pytest

from conftest import is_external_command


@pytest.mark.parametrize(
    ("command", "blocked"),
    [
        (["git", "-C", "/tmp/codex-ci-npm-repro/project", "status"], False),
        (["git", "commit", "-m", "document npm instructions"], False),
        (["npm", "ci"], True),
        (["/usr/local/bin/npx", "skills", "add"], True),
        (["curl", "https://example.com"], True),
        (["pip", "install", "example"], True),
        (["python", "-m", "pip", "install", "example"], True),
        (["python", "-m", "pip", "--version"], False),
        (["env", "MODE=test", "npm", "ci"], True),
        ("git -C /tmp/codex-ci-npm-repro/project status", False),
        ("npm ci", True),
        ("git status && npm ci", True),
        (["bash", "-c", "npm ci"], True),
    ],
)
def test_external_command_detection(command, blocked):
    assert is_external_command(command) is blocked
