# `language-learning` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/language-learning/`
- Invocation type: user-invoked only
- Profile: `review-loop` `agent-skill`
- Admission status: `PASS` under the low-risk prompt-only fast track
- Stable-release boundary: v0.1.1 contains five packages and does not contain `language-learning`

## Evidence summary

| Area | Result | Evidence boundary |
| --- | --- | --- |
| Source | PASS | Original first-party design; no copied third-party code, scripts, or assets. |
| Structure | PASS | 33 contract assertions; 931 collection-discovery assertions across all seven packages; valid frontmatter and resolved links. |
| Invocation | PASS | Claude `disable-model-invocation: true` and Codex `allow_implicit_invocation: false`; user-invoked only; non-trigger returned `NOT_INVOKED`. |
| Fresh-copy install | PASS | Isolated copy contained only `language-learning`, no source checkout, identical file set, zero SHA-256 mismatches, installed contract tests 33 assertions PASS; host install byte-identical and discovered in the host skills root. |
| Behavior | PASS | Fresh agents produced a routed flashcards set and a beginner-defaulted daily lesson without re-asking language/level/mode. |
| Documentation synchronization | PASS | Collection discovery, catalog, bilingual guides, maintenance baseline, and changelog agree on seven packages on `main` versus five in stable v0.1.1. |
| Independent review | PASS | A fresh final fast-track Evaluator confirmed eligibility, reproduced the evidence, verified all nine acceptance criteria, and returned `PASS`. The Evaluator raised one Low-severity evidence-accuracy observation, resolved in the Producer record. |

Full records are under [review-loop/](review-loop/).

Local-source and host-install evidence is admission evidence, not proof of a
released install command. A pinned `language-learning` command must wait for the
next published tag and fresh released-repository verification.

## Behavior sources

Original first-party design. No upstream Skill code or prompt text was copied.
