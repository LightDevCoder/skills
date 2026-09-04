# 02 — Task Assessment Guidelines & Adaptive Plan Schema

**What to build:** Create task assessment criteria distinguishing single-pass vs decomposed tasks and semantic difficulty levels, and refactor the plan output schema to be adaptive with conditional sections instead of mandatory role bureaucracy.

**Blocked by:** None — can start immediately

**Status:** resolved

- [x] `skills/agent-config/references/task-assessment.md` defines `single-pass` vs `decomposed` task shape criteria based on independent acceptance units, dependency graphs, and review surface, explicitly forbidding word-count thresholds.
- [x] Task assessment defines semantic difficulty levels (`routine`, `moderate`, `demanding`, `critical`) based on reasoning depth, uncertainty, reversibility, and risk, answering "what is the minimum sufficient intelligence tier needed".
- [x] `skills/agent-config/references/plan-schema.md` defines the adaptive header contract: `Status` (READY, NEED-INPUT, BOUNDARY), `Scope`, `Provider mode`, `Task shape`, `Execution readiness`, and `Apply mode`.
- [x] Plan schema defines compact single-pass output without forcing ownership matrices, execution waves, or separate Explorer/Merger roles.
- [x] Plan schema specifies decomposed output with work-item routing table, coordination block, and conditional-only ownership/wave sections.
- [x] Plan schema explicitly formalizes review semantics separating Controller Review, Self-check, and Independent Review.

## Comments

Source: .scratch/agent-config-refactor/spec.md. §2, §8, §13, §14, §15, §21.

## Answer

Created `skills/agent-config/references/task-assessment.md` defining semantic task shape (single-pass vs decomposed) with strict anti-wordcount invariant and 8-dimension difficulty evaluation (routine, moderate, demanding, critical). Refactored `skills/agent-config/references/plan-schema.md` to establish adaptive output contracts, distinguishing single-pass simplicity from decomposed ticket routing and establishing formal review semantics.
