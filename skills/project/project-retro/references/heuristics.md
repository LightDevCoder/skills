# Agent Self-Evaluation Heuristics

When reaching the conclusion of a project workflow (after `project-review` or `release-workflow`), or at the end of an implementation milestone, the Agent considers whether to invoke `project-retro`.

## Decision Principles

1. **Friction-Driven:** Retrospectives are triggered by evidenced friction during execution, not by default rote procedure.
2. **Noise Reduction:** On clean, smooth runs where everything succeeded on the first pass without confusion, skip the retrospective to minimize latency and token consumption.
3. **Actionability:** A retrospective finding must lead to a concrete check, pointer, or rule change. Speculative or vague observations are discarded.

## Scoring & Trigger Matrix

Evaluate the session against the following indicators:

| Category | Indicator | Weight |
| --- | --- | --- |
| Navigation | >3 unsuccessful file search attempts, or editing the wrong target | Moderate |
| Guardrails | Test failure or bug that a deterministic linter/typecheck could catch | High |
| Guardrails | Unwired or missing CI/pre-commit check in the repository | High |
| Standards | Reviewer missed an error, or mechanical rules exist in prose | Moderate |
| Steering | `AGENTS.md` / `CLAUDE.md` contains redundant instructions or no-ops | Moderate |
| Tool Economy | >2 redundant reads of large files (>50KB) or excessive token usage | Low |
| Information | Missing dev server logs or inaccessible error traces | Moderate |

### Evaluation Outcome

- **Trigger `project-retro`:** If any **High** weight indicator is present, or if two or more **Moderate** indicators are detected.
- **Skip `project-retro`:** If zero High indicators and at most one Moderate/Low indicator are present, and the primary work passed review cleanly.

## Example Scenarios

### Scenario A — Trigger (Missing Guardrail & Navigation Friction)
- **Session events:** Agent edited `api.ts`, forgot an import, ran tests which crashed. Then searched 4 different folders to find where types were exported. Reviewer finally caught a formatting discrepancy.
- **Decision:** Trigger `project-retro`.
- **Finding:**
  1. Add pre-commit typecheck (`tsc --noEmit`) to catch missing imports immediately.
  2. Add navigation index in `src/types/README.md`.

### Scenario B — Skip (Routine Clean Run)
- **Session events:** Ticket was clear, agent located the exact file immediately, wrote tests first (TDD), implemented the feature, all tests passed on first run, code-review and project-review issued clean PASS.
- **Decision:** Skip `project-retro`. Report task completion without retrospective noise.
