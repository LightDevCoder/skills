# `recap` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/recap/`
- Invocation type: user-invoked only
- Profile: `review-loop` `agent-skill`
- Stable-release boundary: v0.1.1 contains five packages and does not contain `recap`
- Admission status: `PASS` under the low-risk prompt-only fast track; legacy full-path history is preserved under [review-loop/](review-loop/)

## Evidence summary

| Area | Result | Evidence boundary |
| --- | --- | --- |
| Source | PASS | Anthropic's official commands, interactive-mode, and prompt-caching documentation define the observable on-demand one-line/non-compaction boundary; implementation is independent. |
| Structure | PASS | 12 contract assertions; explicit-only Claude and Codex metadata; no runtime dependency. |
| Output contract | PASS | 8 accurately labeled deterministic assertions cover positive, multiline, generalized leading-label, and zero-assertion boundaries. |
| Fresh-copy install | PASS | Final isolated local-source copy discovered only `recap`, contained no source checkout, matched the complete source file set with zero SHA-256 mismatches, and passed the installed 12 + 8 assertion suites. |
| Behavior | PASS | Fresh agents produced valid success and empty-session one-line outputs. |
| Invocation | PASS | A separate fresh agent returned `NOT_INVOKED` when `$recap` was absent. |
| Collection quality | PASS | Final closeout: header 11, Quick Start 8, collection discovery 853, ask-light behavior 54, recap 20, all review-loop Profile suites, Python collection 74, hooks 7, and 4 Python tests passed locally. |
| Independent review | PASS | A fresh final fast-track Evaluator confirmed eligibility, complete evidence, exact-copy installation, accurate output-contract labels, and no issue requiring full-path escalation. The earlier full-path `BLOCKED` remains historical. |

Local-source fresh-copy evidence is admission evidence, not proof of a released
install command. A pinned `recap` command must wait for the next published tag
and fresh released-repository verification.

## Behavior sources

- [Claude Code commands](https://code.claude.com/docs/en/commands)
- [Claude Code interactive mode](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code prompt caching](https://code.claude.com/docs/en/prompt-caching)

No Anthropic source code or proprietary prompt text was copied.
