# Clarification System — Composition

[中文](../zh-CN/workflows/clarification-system.md)

This document explains the **Clarification & Research** composition: entry, handoff, and stop. Internal questioning logic lives in each `SKILL.md` and its `references/`.

## Family

```text
                 socratic  (model-invoked engine)
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
   clarify   project-clarify  decision-map
                │                  │
                └───── unknown ────┘
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
        research  prototype  to-questionnaire
```

- [`socratic`](../../skills/socratic/SKILL.md) — core engine: dynamic, decision-owned questioning; no fixed questionnaire; distinguishes facts vs user decisions. Not a project workflow by itself. Other Skills *call* it; they do not reimplement it.
- [`clarify`](../../skills/clarify/SKILL.md) — **user-invoked standalone entry** for vague ideas/brainstorms with no project context. `clarify → socratic`. Returns `Current understanding / Resolved / Still unresolved / Gaps` + current question, then stops. No SPEC, no auto-chain.

## Project-aware clarification

| Skill | Entry | How it uses `socratic` | Handoff | Stop |
| --- | --- | --- | --- | --- |
| [`project-clarify`](../../skills/project-clarify/SKILL.md) — user-invoked | Existing project with genuine unresolved decisions | **Inspects first:** `README`, `AGENTS.md`, `CLAUDE.md`, existing docs/specs/source. *Then* calls `socratic` for only the gaps that need user-owned decisions | bounded handoff for `project-spec` (or back to `decision-map` if still foggy) | stop without creating SPEC/tickets or auto-starting another user-invoked Skill |
| [`decision-map`](../../skills/decision-map/SKILL.md) — user-invoked | Large, foggy, multi-session, many dependent decisions | Maintains a persistent map under `.scratch/<effort>/map.md` + child tickets; may call `socratic` and, per unknown routing, `research` / `prototype` / `to-questionnaire` | decision tickets resolved → hand to `project-spec` | stop at map updates; work stays on the tracker, not in execution |

## Unknown routing

When a fact/decision is missing inside clarification:

```text
Unknown
  ├─ user must decide          → socratic
  ├─ external fact             → research (model-invoked PORT, reads primary sources)
  ├─ needs experiment          → prototype (throwaway probe)
  └─ held by another person    → to-questionnaire (user-invoked PORT, builds a questionnaire)
```

Call the capability; never guess or copy its instructions into the caller. `research` and `prototype` are read-only investigators; `to-questionnaire` returns the questionnaire for the user to send.

## Handoff rules

- `clarify` stops at its summary. If a formal project emerges, the *user* may explicitly invoke `project-clarify` or `decision-map` — no auto-chain.
- `project-clarify` hands to `project-spec`; if a blocking user decision remains, `project-spec` returns to `project-clarify`.
- `decision-map` hands to `project-spec` once fog clears.

See [project-workflow](project-workflow.md) for how clarification feeds planning, and [`ask-light`](../../skills/ask-light/SKILL.md) for routing when the entry is unclear.
