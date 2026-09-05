---
name: implement
description: Execute one bounded, already-decided work item — code, document, configuration, research artifact, Skill, or generic project task — by inspecting relevant context, offering agent-config routing when materially useful, verifying locally, and handing the result to review-loop with the appropriate specialist reviewer.
disable-model-invocation: true
---

# Implement

`implement` is a user-invoked bounded executor. Run it only after an explicit
`$implement` request. It turns one ready work item into a verified artifact and
hands it to review.

## Core loop

1. **Pin one work item.** Resolve exactly one ticket, Spec section, or explicit
   conversation slice and record it as the target.
2. **Inspect relevant context.** When `docs/agents/light-project.md` exists,
   read its tracker, domain-context, and review-profile fields. Then skim only
   the named glossary, ADRs, and files the item touches; record source locations.
3. **Offer execution routing when materially useful.** When model right-sizing,
   reasoning effort tuning, delegated implementation with stronger review,
   or execution topology would materially help, offer the user a choice to
   invoke `agent-config` or proceed directly. If the user explicitly requested
   routing, invoke `agent-config` directly; if the user declined or disabled
   routing, or for bounded solo work, proceed directly without blocking.
   When `agent-config` is invoked, consume the `AgentConfigResult`:
   - `readiness === "READY"`: consume `execution_config` and execute bounded slice.
   - `readiness === "NEED_INPUT"`: profile missing / setup needed. Offer setup or fallback safely to single-agent execution if declined.
   - `readiness === "NEED_PROJECT_TICKETS"`: decomposed task without tickets -> handoff to `project-tickets` and halt implementation (never batch-execute un-ticketed tasks).
   - `readiness === "BLOCKED"` or `"UNSUPPORTED"`: core rejection (e.g. unauthorized model, unevidenced model, or unknown capability) -> halt implementation with diagnostic reason.
4. **Execute the bounded slice, then verify.** Use `tdd` for code when
   appropriate; produce non-code artifacts per their contract. Verify locally
   (tests, render, schema, or domain check).
5. **Hand to `review-loop`** with the matching reviewer: `code-review` for
   code, `generic-review` or a domain reviewer for non-code. Report evidence
   and stop.

## Composition

```text
implement
   ↓
inspect bounded task
   ↓
would routing materially help?
   ├─ no  → execute directly
   └─ yes → offer agent-config
              ├─ accept  → agent-config → consume AgentConfigResult (READY / NEED_INPUT / NEED_PROJECT_TICKETS / BLOCKED / UNSUPPORTED)
              └─ decline → execute directly
   ↓
tdd when appropriate
   ↓
review-loop → code-review (code) / generic-review (non-code)
```

`implement` composes these capabilities; it does not reimplement them.
`agent-config` is an optional enhancement: declining it or running on a Host
without model-routing capabilities does not block implementation. A missing or
blocked prerequisite is a `BLOCKED` handoff gap — report the smallest
unblock and stop. Full per-artifact procedures are in
[WORKFLOW.md](references/WORKFLOW.md); examples are in
[EXAMPLES.md](references/EXAMPLES.md).
