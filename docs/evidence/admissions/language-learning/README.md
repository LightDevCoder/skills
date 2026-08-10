# `language-learning` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/language-learning/`
- Invocation type: user-invoked only
- Admission status: staged for the low-risk prompt-only fast track; no final verdict yet
- Stable-release boundary: v0.1.1 contains five packages and does not contain `language-learning`

## Evidence staged

| Area | Result | Evidence boundary |
| --- | --- | --- |
| Source | PASS | Original first-party design; no copied third-party code, scripts, or assets. |
| Structure | PENDING | Package tree, `SKILL.md` metadata, and internal links validate under the collection discovery check. |
| Contract | PENDING | 33 locally passing contract assertions cover context reuse, teaching behavior, selective correction, the time-split guideline, everyday-first flashcards, confusable contrasts, evaluation, and immersion scaling, with positive and negative fixtures. |
| Invocation | PASS | Claude `disable-model-invocation: true` and Codex `allow_implicit_invocation: false`; the package declares user-invoked only. |
| Fresh-copy install | PENDING | Requires a fresh host and, for a pinned command, a future released tag; no release tag exists yet. |
| Behavior | PENDING | Requires fresh Agent observations of success, boundary, and failure scenarios. |
| Independent review | PENDING | Requires one fresh independent fast-track Evaluator before a final `PASS`, `FAIL`, or `BLOCKED`. |
| Collection quality | PENDING | Full local suite result to be recorded once admission edits are finalized. |

## What must happen before a final verdict

1. Run the collection discovery, header-asset, and quick-start suites locally and record the results.
2. Obtain one fresh independent Evaluator verdict for the prompt-only fast track.
3. Perform a fresh-copy install and discovery check on a fresh host.
4. Record fresh Agent success, boundary, and non-trigger behavior observations.

Until these complete, the package is proposed, not admitted, and no pinned
install command may be published.

## Behavior sources

Original first-party design. No upstream Skill code or prompt text is copied
into this package.
