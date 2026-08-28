# `recap` user guide

[中文指南](../zh-CN/skills/recap.md)

The behavior authority is [skills/recap/SKILL.md](../../skills/recap/SKILL.md).
This page explains usage without creating a second contract.

## Purpose

Show one concise line about the current session without replacing or compacting
conversation history. The output is capped at 400 characters.

## Invoke

Select it explicitly:

```text
$recap
```

The package frontmatter and host metadata keep this entry user-invoked.

## Verification and release state

Run the current amendment checks in
[tests/test_functional_closure.py](../../tests/test_functional_closure.py).
The unchanged [package tests](../../skills/recap/tests/) are historical records
for the prior long-form contract and are not part of the active suite.
Fresh-copy and independent review evidence is recorded in the
[admission record](../evidence/admissions/recap/README.md).

The prior `recap` form is released in v0.1.2; this manual-only amendment remains
unreleased in the current candidate. Install the current stable release form with
`npx skills add LightDevCoder/skills#v0.1.6 --skill recap`,
refresh, and confirm discovery without the source checkout under
[the installation policy](../INSTALLATION.md).

## Behavior references

- [Claude Code commands](https://code.claude.com/docs/en/commands)
- [Claude Code session recap](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code prompt caching and `/recap`](https://code.claude.com/docs/en/prompt-caching)

These references define the observed product boundary; no Anthropic source
code or prompt text is copied into this package.
