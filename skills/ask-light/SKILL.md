---
name: ask-light
description: Act as the Light workflow advisor, navigator, and router. Inspect the current project/host evidence, explain the stage, recommend the next Light Skill with reasoning, wait for user approval, then honor the accepted Skill's invocation policy. Also answer collection-navigation and standalone routing requests. Use only when the user explicitly invokes $ask-light; never execute before consent.
disable-model-invocation: true
---

# Ask Light

`ask-light` is the **Light workflow advisor, navigator, and router** — a
user-invoked entry that understands workflows, not just Skill names. It
answers “where is this work, what is missing, and which Light Skill owns the
next step?”, then handles the accepted Skill according to the host’s
invocation policy after the user agrees.

## Session flow

1. **Inspect.** Read enough local evidence to understand the current stage:
   repository state, `docs/agents/light-project.md`, `docs/agents/issue-tracker.md`,
   `AGENTS.md`/`CLAUDE.md`, the active SPEC, `.scratch/*` effort state, current
   tickets, implementation changes, and review/acceptance state. Do not read
   the whole repository blindly.
2. **Explain.** State what the project appears to be trying to do, what stage
   it is in, what is already completed, and what is blocking or logically next.
3. **Recommend.** Name the next Light Skill and why it fits **now**, including
   why obvious neighboring alternatives are not the best next step when that
   distinction matters.
4. **Wait for approval.** Do not execute before the user explicitly agrees.
5. **Honor the host invocation policy after approval.** After a normal
   approval (`yes`, `可以`, `go ahead`, `do it`, `用这个`), determine the
   accepted Skill’s invocation type. If it is **model-invoked**, begin it in
   the current conversation where the host supports that. If it is
   **user-invoked** (the normal project-stage case), repository policy forbids
   a user-invoked Skill from auto-invoking another user-invoked Skill, so
   `ask-light` does **not** fake execution: it renders the exact invocation
   (`$<skill>` on Codex, `/<skill>` on Claude Code) and asks the user to start
   it. Do not claim a direct transition without host evidence.

## Modes

- `$ask-light next` — one next-Skill recommendation with workflow reasoning.
- `$ask-light workflow` — one bounded workflow recipe.
- `$ask-light <category>` — browse the collection (for example `project Skills`,
  `review Skills`, `learning Skills`) and explain roles and neighbors.
- Plain standalone requests (`Explain this like I’m five`, `Investigate this
  bug`, `Set up a manuscript workflow`) route without requiring project
  inspection.

Use [ask_light.py](scripts/ask_light.py) as the deterministic routing helper;
[ask-light.ps1](scripts/ask-light.ps1) is a compatibility launcher. The
helper is read-only during the recommendation phase. Logical routing and the
collection taxonomy come from
[light-skill-map.json](references/light-skill-map.json). Full discovery and
approval protocol is in [discovery-contract.md](references/discovery-contract.md).

## Safety and stop

Before approval: read-only recommendation; nothing is invoked, installed, or
orchestrated. After approval: for a model-invoked accepted Skill, begin it where the host
supports that; for a user-invoked accepted Skill, render the exact invocation
and do not fake execution. Follow the accepted Skill’s stop condition once it
actually starts. Do not auto-chain past the accepted Skill; that Skill decides
its own handoff.

## Result contract

Return a compact record with these fields:

```text
Mode: next | workflow | navigate | standalone
Status: RECOMMEND | NEED-INPUT | BLOCKED
ProjectStage: <evidence-based stage, or none for standalone>
Completed: <what is already done, when relevant>
Missing: <what is blocking or next, when relevant>
Skill: <one name, or none>
Source: first-party: <resolved package path>
Reason: <context-specific workflow reasoning, not a generic description>
Invocation: <host-specific command or picker action>
Alternative: <at most one, only for a material tie>
Gaps: <missing/unreadable metadata and actionable guidance>
Next: awaiting-approval | host-transition-required | beginning-<skill> | no-execution
Reads: metadata=<count>; bodies=<count>; references=<count>
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

For an already accepted project, return a clean terminal result:
`ProjectStage: accepted`, `Skill: none`, `Completed` includes `acceptance
passed`, `Missing: none`, and `Next: no-execution`.

## Verification

Run the package contract and behavior tests. They cover project-state
recommendation, recommendation reasoning, approval-to-execution, collection
navigation, standalone routing, root discovery, first-party provenance, host
availability, and the no-execution-before-approval boundary.