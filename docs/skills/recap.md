# `recap` user guide

[中文指南](../zh-CN/skills/recap.md)

The behavior authority is [skills/recap/SKILL.md](../../skills/recap/SKILL.md).
This page explains usage without creating a second contract.

## Purpose

`recap` is a user-invoked, read-only status glance. It summarizes the active
goal, newest material outcome, and current state in exactly one plain-text line.
It is independently implemented from Anthropic's documented on-demand recap
boundary: display a one-line summary without replacing history.

## Invoke

Select it explicitly:

```text
$recap
```

It must not run automatically. It uses only session context already available,
runs no tools, changes no files, does not compact history, and stops after the
single line.

## Expected results

- **Success:** one concise sentence names the latest material outcome and state.
- **Boundary:** when the session has little context, one line says that no prior
  activity is available rather than inventing progress.
- **Failure:** multiline, labeled, bulleted, tool-using, or state-changing output
  violates the contract and must not be presented as a valid recap.

`recap` never invokes another user-invoked Skill. A durable continuation record
requires a separate user choice such as `handoff`; final acceptance remains
owned by `review-loop`. Missing session context is handled in the one-line
boundary result and is not silently relabeled as a `review-loop` `BLOCKED`
verdict.

## Verification and release state

Run [the package tests](../../skills/recap/tests/) and inspect
`agents/openai.yaml` for `allow_implicit_invocation: false`. Fresh-copy and
independent review evidence is recorded in the
[admission record](../evidence/admissions/recap/README.md).

`recap` is not present in stable v0.1.1. Do not publish a pinned install command
for it until the next tag is released and verified under
[the installation policy](../INSTALLATION.md).

## Behavior references

- [Claude Code commands](https://code.claude.com/docs/en/commands)
- [Claude Code session recap](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code prompt caching and `/recap`](https://code.claude.com/docs/en/prompt-caching)

These references define the observed product boundary; no Anthropic source
code or prompt text is copied into this package.
