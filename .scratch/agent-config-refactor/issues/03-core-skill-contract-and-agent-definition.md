# 03 — Core SKILL.md Refactor & openai.yaml Agent Definition

**What to build:** Refactor the core `agent-config` skill and agent definition to execute the 2x2 decision grid (tiered vs fixed model provider x single-pass vs decomposed task) across the four required execution modes, providing model right-sizing and safe fallback while preserving canonical project workflow boundaries.

**Blocked by:** 01 — Host Evidence Schema v2 & Provider Adapter Contract, 02 — Task Assessment Guidelines & Adaptive Plan Schema

**Status:** resolved

- [x] `skills/agent-config/SKILL.md` implements the 2x2 decision grid: Tiered Multi-model + Single-pass, Tiered Multi-model + Decomposed, Fixed Single-model + Single-pass, Fixed Single-model + Decomposed.
- [x] Implements right-sizing: assigns minimum sufficient model rank for implementation, reserves higher model tier/effort for review when supported, and never defaults all tasks to the highest model.
- [x] Fixed-model execution is streamlined to direct execution at max supported effort without manufacturing fake multi-agent roles.
- [x] Decomposed tasks without formal tickets return `Execution readiness: needs-project-tickets` and hand off to `project-tickets` without generating ticket files.
- [x] Ticket graph routing honors monotonic difficulty invariants: demanding/critical tickets are never assigned lower tier or effort than routine tickets.
- [x] Roles are conditional rather than mandatory ontology; Controller defaults to current session unless delegated topology requires otherwise.
- [x] `skills/agent-config/agents/openai.yaml` updates prompt instructions to model right-sizing and execution topology, keeping `allow_implicit_invocation: true` strictly read-only.
- [x] Core skill and agent definition remain strictly provider-neutral with no vendor model names or config paths.

## Comments

Source: .scratch/agent-config-refactor/spec.md. §0, §2, §3, §4, §9, §10, §11, §12, §14, §18, §29, §30, §37, §38, §39.

## Answer

Refactored `skills/agent-config/SKILL.md` to establish the 2x2 decision grid and the 4 distinct execution modes, with clear model/effort right-sizing, conditional roles, safe fixed-model degradation, and project-tickets handoff. Updated `skills/agent-config/agents/openai.yaml` with focused model/effort prompt and preserved read-only implicit invocation. Verified provider neutrality.
