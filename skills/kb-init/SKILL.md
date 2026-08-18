---
name: kb-init
description: Design and initialize a maintainable knowledge base through a knowledge-base-specific interview. Use only when the user explicitly invokes kb-init to create, rebuild, structure, or initialize a knowledge base, wiki, reference library, research archive, operational knowledge system, or similar long-term knowledge workspace. If invoked with little or no prompt, start the interview automatically.
disable-model-invocation: true
---

# KB Init

Design a knowledge base from the user's real workflow, then initialize it only after the user explicitly ends the interview, approves the resulting implementation SPEC, and asks to proceed.

This skill is knowledge-base-specific. It is not a generic grilling skill and it is not tied to any particular software, file format, database, wiki engine, or collaboration platform.

## Invocation and scope

Run only after an explicit `kb-init` request. It is user-invoked and must not trigger on its own from a generic mention of knowledge bases, notes, wikis, or research archives. Once explicitly invoked, if the prompt contains little or no useful context, start the knowledge-base interview automatically.

`kb-init` may call the model-invoked `research` capability when an unresolved decision depends on external facts or current platform capabilities. It must not invoke another user-invoked Skill on its own.

## Core principles

1. **Interview before architecture.**
   Do not choose a base, folder structure, schema, or maintenance model before the user's workflow supports that choice.

2. **The user owns decisions.**
   Facts are the Agent's job to discover. Decisions are the user's job to make. Recommendations are welcome, but never silently convert a recommendation into a settled requirement.

3. **The user owns the end of the interview.**
   Even when the Agent believes enough information has been gathered, do not generate the SPEC until the user explicitly says the interview is finished or asks for the SPEC.

4. **Questions from the user interrupt the interview.**
   If the user asks "why?", "what does this mean?", "what is the tradeoff?", or challenges a proposal, answer that question first. Do not treat the question itself as acceptance of a decision.

5. **No silent gap-filling.**
   An unresolved decision stays unresolved. Do not infer the remaining design simply because the likely answer seems obvious.

6. **No platform recipes in the core skill.**
   Do not embed hard-coded instructions for specific knowledge-base products. The base is discovered from the interview, then researched and operationalized as needed.

7. **Computer use is never a prerequisite.**
   Prefer programmatic or file-based access. GUI automation may be used as an optional enhancement when available, but the design must not depend on computer-use capability unless the user explicitly accepts that limitation.

8. **Maintenance is part of the product.**
   A knowledge base is not complete when its initial structure exists. The implementation must also define how people and Agents will add, find, update, reorganize, validate, back up, and hand off the knowledge base over time.

## Allowed external skill

`kb-init` may invoke one external skill:

- `research` — when an unresolved decision depends on external facts, current product capabilities, official APIs, storage limits, integration methods, or other information that should be verified rather than guessed.

Treat `research` as an optional capability, not a hard installation dependency. If it is unavailable, do not fail the entire skill. Explain what fact remains unverified and either use another research capability already available in the environment or leave that fact explicitly unresolved.

Do not invoke generic grilling or generic to-spec skills. Their useful behavior is incorporated into this skill's interview and SPEC rules.

## Workflow

```text
Skill invoked
    ↓
Knowledge-base interview
    ↓
All required design areas have been surfaced
    ↓
User continues, revises, researches, or asks questions as long as desired
    ↓
User explicitly ends interview / asks for SPEC
    ↓
Design synthesis
    ↓
Base Discovery for the selected base
    ↓
Knowledge-base implementation SPEC
    ↓
Wait for explicit user approval
    │
    ├── User requests changes → revise SPEC → wait again
    │
    └── User approves
            ↓
        Implementation
            ↓
        Validation
            ↓
         Handoff
```

## Phase 1 — Start the interview automatically

Read `references/interview-contract.md`.

If the user invokes this skill without useful context, start with a simple question about the knowledge itself, for example:

> 你想建一个什么知识库？主要准备往里面放些什么？

Do not ask for a formal brief, technology stack, template, or questionnaire first.

If useful context already exists, continue from what is still unresolved.

## Phase 2 — Maintain an internal interview map

Track the following internal statuses for every major design area:

- `unresolved`
- `discussing`
- `researching`
- `settled`
- `deferred`
- `not-applicable`

Do not normally dump this map into the conversation. Show it only when it helps the user understand progress or when the user asks where things stand.

A design area may be marked:

- `settled` only when the user has explicitly answered it or clearly accepted a recommendation;
- `deferred` only when the user explicitly chooses to postpone it and it does not block implementation;
- `not-applicable` only when the conversation makes that genuinely clear.

Do not mark a design area settled merely because the Agent can imagine a reasonable answer.

## Phase 3 — Handle user questions and research detours

User questions have priority over interview progression.

If the user challenges or asks about a proposal:

1. answer the question directly;
2. explain unfamiliar technical language in plain terms;
3. keep the underlying decision open unless the user actually decides it;
4. resume from that same decision afterward.

If the unresolved point depends on external facts or current platform capabilities, use `research`.

Before research, state the exact question being investigated and which interview decision is paused.

After research:

1. summarize the relevant findings in plain language;
2. distinguish facts from recommendations;
3. return to the paused decision;
4. let the user decide;
5. reopen any downstream design areas that the new result invalidates.

Research never makes the user's decision for them.

## Phase 4 — Complete the knowledge-base interview

Every required design area in `references/interview-contract.md` must be actively surfaced before an implementation-ready SPEC can be produced.

Do not collapse the interview into a small number of broad questions just to finish faster.

Prefer one major decision area, or one tightly related cluster of decisions, per turn.

The interview may move backward. A later answer may invalidate an earlier decision. Reopen it when necessary.

When the Agent believes the design is sufficiently understood, do **not** produce the SPEC automatically.

Instead say something like:

> 我这边已经有足够信息整理实施方案了。你还想继续讨论、再查一个方向，还是现在结束问答让我出 SPEC？

Wait for the user's choice.

Only explicit user intent such as the following ends the interview:

- "问答结束"
- "可以出 SPEC 了"
- "就这些，整理方案"
- "按现在的内容出 SPEC"
- equivalent wording with the same meaning

Silence, a short acknowledgement, answering the last question, or asking another question does not end the interview.

## Phase 5 — Base Discovery

After the user ends the interview and a base has been selected or strongly proposed, read `references/base-discovery.md`.

Do not use a built-in platform recipe.

Discover how the selected base actually works and how an Agent can operate it.

If the required facts are current, unfamiliar, or not already verified, invoke `research`.

The base is not considered implementation-ready until its operating path is clear enough to answer:

- what the knowledge is physically or logically stored as;
- how an Agent can read it;
- how an Agent can create and modify it;
- how authentication or permission works;
- how attachments or non-text material are handled;
- how search or retrieval works;
- how it can be exported, backed up, or moved;
- which operations the current Agent environment can perform directly;
- which operations require user action or a future capability.

If the Base Discovery result contradicts the user's needs, return to the base decision rather than forcing the original choice into the SPEC.

## Phase 6 — Synthesize the design

Read `references/design-guide.md`.

Translate the settled interview into a coherent design.

Keep two abstractions separate until they are intentionally combined:

1. **Knowledge model** — what the knowledge is, how it is structured, how it enters, how it is found, and how it is maintained.
2. **Base operating model** — how the chosen base stores information, how the Agent accesses it, what it can automate, and what limitations remain.

Do not let the chosen base dictate the knowledge model unnecessarily.

Do not let a preferred knowledge structure hide limitations of the chosen base.

## Phase 7 — Produce the implementation SPEC

Read `references/spec-guide.md`.

The SPEC is knowledge-base-specific. It must synthesize what was already discussed; it must not restart the interview.

If a blocking decision is still unresolved, do not disguise it as settled. Tell the user what blocks an implementation-ready SPEC and offer either:

- a draft SPEC with the blocker clearly marked; or
- a return to the relevant interview decision.

The SPEC must include both the knowledge design and the Base Discovery result.

After presenting the SPEC, stop.

Do not initialize anything yet.

## Phase 8 — Approval gate

Implementation begins only after the user explicitly approves the SPEC.

Approval means clear intent such as:

- "可以，开始"
- "按这个做"
- "没问题，开工"
- equivalent wording

If the user asks a question or requests a change, remain in the SPEC phase.

## Phase 9 — Implement

After approval, implement the approved SPEC using the tools available in the current environment.

Prefer non-GUI routes when both GUI and programmatic routes exist.

If the current environment cannot complete some base-specific operations:

1. complete every part that can be completed safely;
2. generate the structures, schemas, configuration, import material, scripts, maintenance documents, or setup instructions that make the remaining work minimal;
3. identify exactly what remains;
4. identify why it remains;
5. identify what capability, permission, or user action will unblock it.

Do not treat partial automation as failure when the remaining work genuinely depends on unavailable external capabilities.

Do not silently switch to computer use as the only implementation route.

## Phase 10 — Validate

Validate the result against the approved SPEC.

Validation should test the user's actual workflow, not a universal knowledge-management checklist.

At minimum, verify representative end-to-end scenarios for:

- adding knowledge;
- finding or querying knowledge;
- maintaining or updating knowledge;
- operating the chosen base;
- respecting permissions and user boundaries.

If part of the implementation remains manual or blocked by an unavailable connector, validate the generated handoff material for that remaining step.

## Phase 11 — Handoff

Explain briefly:

- what was created;
- where it lives;
- how new knowledge enters;
- how the user finds or analyzes knowledge;
- how the Agent connects to and maintains the base;
- which operations are automatic;
- which operations still require the user;
- how another Agent session can continue maintenance;
- how to check whether the knowledge base remains healthy.

Keep the handoff practical and free of unnecessary knowledge-management jargon.
