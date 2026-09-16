# `project-retro` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/project-retro/`
- Origin: PORT & LIGHT WORKFLOW ADAPTATION — based on Matt Pocock's `retro` at
  `959a8e9f1edc3adbe2f7e3054bb6fbefa6696260` (2026-09-15), adapted into a
  first-party capability with model-invoked self-evaluation heuristics for the
  Light project lifecycle; see
  [ATTRIBUTION.md](../../../../skills/project-retro/ATTRIBUTION.md)
- Invocation type: model-invoked (`allow_implicit_invocation: true`), with
  support for manual user invocation (`$project-retro`)
- Admission route: full path — `review-loop` `agent-skill` Profile; final
  verdict owned by `project-review`
- Admission status: `PASS` (round 01; 0 findings)
- Release boundary: admitted for release `v0.2.1`

## Evidence summary

| Area | Result | Evidence boundary |
| --- | --- | --- |
| Attribution | PASS | `ATTRIBUTION.md` records the upstream repository (`mattpocock/skills`), original path (`skills/in-progress/retro`), pinned revision (`959a8e9f1edc3adbe2f7e3054bb6fbefa6696260`), MIT notice, and exact transformation summary. |
| Structure | PASS | Concise `SKILL.md`, `agents/openai.yaml`, supporting references (`references/categories.md`, `references/heuristics.md`, `references/template.md`), and comprehensive tests under `tests/`. All links resolve. No placeholders. |
| Fresh-copy install | PASS | Package is self-contained with no external runtime dependencies on `mattpocock/skills`. Fresh isolated copy passes discovery and contract validation. |
| Behavior | PASS | Unit and contract test suite passes: verifies self-evaluation heuristics (smooth runs skip retro; high/moderate friction triggers retro), severity ordering, category classification, and template adherence. |
| Invocation | PASS | Model-invoked (`allow_implicit_invocation: true`); consistent between `SKILL.md` and `agents/openai.yaml`. |
| Collection quality | PASS | Collection test suite and router tests pass with 36 admitted packages. |

## Review record

- Charter: [review-loop/charter.md](review-loop/charter.md)
- State: [review-loop/state.md](review-loop/state.md)
- Producer evidence: [review-loop/rounds/round-01/producer-evidence.md](review-loop/rounds/round-01/producer-evidence.md)
- Findings: [review-loop/findings.md](review-loop/findings.md) (0 findings)
- Independent evaluator verdict: [review-loop/rounds/round-01/evaluator-verdict.md](review-loop/rounds/round-01/evaluator-verdict.md)
- Final verdict (project-review): [review-loop/verdict.md](review-loop/verdict.md)
