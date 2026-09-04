# 04 — Four-Quadrant Behavior Fixtures & Unit Test Suite

**What to build:** Create comprehensive test fixtures for the four execution quadrants (Cases A, B, C, D) plus degradation and adapter scenarios, and rewrite `test_agent_config_contract.py` and `test_agent_config_behavior.py` to enforce behavioral invariants without stale prose locking.

**Blocked by:** 03 — Core SKILL.md Refactor & openai.yaml Agent Definition

**Status:** resolved

- [x] Four-quadrant fixtures created: Case A (tiered + single-pass), Case B (tiered + decomposed), Case C (fixed + single-pass), Case D (fixed + decomposed) using provider-neutral model IDs (`model-alpha`, `model-beta`, `model-gamma`).
- [x] Degradation fixtures created: multiple models without trusted rank, missing reasoning control, missing per-agent model selection, missing subagents/parallelism, missing session threads, and unknown concurrency cap.
- [x] Adapter test fixtures created: adapter absent, stale metadata, mutation without user approval, valid mutation with explicit approval, and adapter failure.
- [x] `test_agent_config_contract.py` validates schema v2, v1 backward-compatibility, plan-schema invariants, and provider-neutrality across all files.
- [x] `test_agent_config_behavior.py` validates all 4 execution modes, difficulty-to-model monotonicity in Case B, single-model simplicity in Case C, and non-blocking degradation behavior.
- [x] Legacy rigid prose checks (e.g. mandatory Merger, mandatory waves on single-pass, mandatory 5 roles) are completely replaced with behavioral invariants.
- [x] `python3 -m unittest discover -s skills/agent-config/tests` runs clean with 100% pass rate.

## Comments

Source: .scratch/agent-config-refactor/spec.md. §31, §32, §33, §34, §36, §38.

## Answer

Created 7 new fixtures covering Cases A-D, unranked models, missing reasoning, and adapter scenarios. Rewrote `test_agent_config_contract.py` and `test_agent_config_behavior.py` replacing rigid prose locking with behavioral invariants for the 2x2 decision grid, monotonicity, degradation fallbacks, and adapter safety boundaries. 19 unit tests passing cleanly including isolated-copy test.
