---
name: kb-init
description: Design and initialize a maintainable knowledge base through a knowledge-base-specific interview. Use only when the user explicitly invokes kb-init to create, rebuild, structure, or initialize a knowledge base, wiki, reference library, research archive, operational knowledge system, or similar long-term knowledge workspace. If invoked with little or no prompt, start the interview automatically.
disable-model-invocation: true
---

# KB Init

Design a knowledge base from the user's real workflow, then initialize it only after the user explicitly ends the interview, approves the resulting implementation SPEC, and asks to proceed.

This skill is knowledge-base-specific. It is not tied to any particular software, directory layout, file format, database, wiki engine, or collaboration platform.

## Invocation and scope

Run only after an explicit `kb-init` request. It is user-invoked and must not trigger on its own from a generic mention of knowledge bases, notes, wikis, or research archives. Once explicitly invoked, if the prompt contains little or no useful context, start the knowledge-base interview automatically.

`kb-init` may call the model-invoked `research` capability when an unresolved decision depends on external facts or current platform capabilities. It must not invoke another user-invoked Skill on its own.

## Core principles

1. **Interview before architecture.**  
   Do not choose a base, structure, schema, or maintenance model before the user's workflow supports that choice.

2. **The user owns decisions.**  
   Facts are the Agent's job to discover. Decisions are the user's job to make. Recommendations are welcome, but never silently turn a recommendation into a settled requirement.

3. **The user owns the end of the interview.**  
   Even when the Agent believes enough information has been gathered, do not generate the SPEC until the user explicitly says the interview is finished or asks for the SPEC.

4. **User questions interrupt the interview.**  
   If the user asks why, asks what something means, challenges a proposal, or wants a comparison, answer that first. The underlying decision remains open until the user actually decides it.

5. **No silent gap-filling.**  
   An unresolved decision stays unresolved. Do not infer the remaining design just because the likely answer seems obvious.

6. **Depth before settlement.**  
   Important decisions are not settled merely because the topic was mentioned once. For a high-impact decision, understand the user's real workflow, the priority or tradeoff behind the choice, and at least one concrete future-use scenario before treating it as settled.

7. **Surface architecture-shaping open decisions.**  
   If the Agent notices an unresolved question that could materially change structure, navigation, storage, automation, permissions, migration, backup, or operating workflow, it must surface that question to the user. Do not silently downgrade it into an implementation choice merely because the Agent has a plausible answer.

8. **Decision provenance matters.**  
   A high-impact decision is ready only when its source is clear: explicit user decision, user-accepted recommendation, verified environment fact, explicit deferral, or genuinely not-applicable. "The Agent can infer a sensible default" is not a valid source. If the user explicitly keeps a choice under their own control (for example, deciding sharing permissions case by case), preserve that as a governance rule; do not invent a default value for the choice.

9. **No platform recipes in the skill.**  
   Do not keep built-in setup instructions for named software bases. Discover the base from the interview, then research how that specific base works.

10. **Computer use is optional, never foundational.**  
   Prefer stable file, CLI, connector, MCP, API, SDK, import/export, or other programmatic routes when they exist. A knowledge base design should remain useful even when the current Agent has no GUI automation.

11. **Maintenance is part of the knowledge base.**  
   The implementation is not complete when the initial structure exists. It must also define how people and Agents add, find, update, reorganize, validate, back up, reconnect to, and hand off the knowledge base.

12. **Design for both human and Agent use when both exist.**  
   If people will directly browse or operate the chosen base, human navigation and presentation are first-class design requirements. Do not optimize only for Agent/API maintenance. If people will not directly use the base, do not add a human-facing navigation layer merely for completeness.

13. **Stay inside the knowledge-base boundary.**  
   Understand downstream uses only far enough to design the knowledge base correctly. Do not drift into designing downstream reports, analysis products, dashboards, applications, or other consumer systems unless the user explicitly expands the scope.

## External skill policy

`kb-init` may invoke one external skill:

- `research` — for external facts that should be verified instead of guessed.

`research` is a soft dependency.

- If the environment exposes `research` as a callable skill, use it for KB-init research detours. Do not bypass it with direct web search merely because direct search is also available.
- If `research` cannot actually be invoked in the current harness, fall back to another trustworthy research capability already present or keep the affected decision explicitly unresolved.

Do not invoke generic grilling or generic to-spec skills. Their useful behaviors are incorporated into this skill.

Whenever research is needed, read and follow `references/research-contract.md`.

## High-level workflow

```text
Skill invoked
    ↓
Knowledge-base interview
    ↓
A base becomes a serious candidate
    ↓
Base Discovery as needed
    ↓
Continue interview / revisit decisions / research detours
    ↓
Coverage + Implementation Readiness check
    ↓
User explicitly ends interview / asks for SPEC
    ↓
Design synthesis
    ↓
Knowledge-base implementation SPEC
    ↓
Wait for explicit user approval
    │
    ├── User requests changes → revise SPEC → wait again
    │
    └── User approves
            ↓
    Connection Setup if required
            ↓
    Connection Validation if required
            ↓
        Implementation
            ↓
        Validation
            ↓
         Handoff
```

## Phase 1 — Start the interview automatically

Read `references/interview-contract.md`.

If invoked without useful context, start with a simple question about the knowledge itself, for example:

> 你想建一个什么知识库？主要准备往里面放些什么？

Do not ask for a formal brief, technology stack, template, or questionnaire first.

If useful context already exists, continue from what is still unresolved.

## Phase 2 — Maintain an internal decision map

Track every major design area with:

### Status
- `unresolved`
- `discussing`
- `researching`
- `settled`
- `deferred`
- `not-applicable`

### Decision source
- `user-explicit`
- `user-accepted-recommendation`
- `verified-environment-fact`
- `user-deferred`
- `not-applicable`

Do not normally expose the whole map to the user.

A decision becomes `settled` only when the user explicitly answers it or clearly accepts a recommendation.

For high-impact decisions, settlement also requires enough depth to understand:

- the real workflow or behavior the decision must support;
- the user's important priority, reason, or accepted tradeoff;
- at least one concrete scenario showing how the choice will work in practice;
- a valid decision source.

If the Agent's own reasoning identifies an architecture-shaping open question, keep that decision `discussing` and surface it to the user. The Agent may propose a recommendation, but the recommendation does not become settled until the user accepts it.

Do not interrogate low-impact details unnecessarily, but do not mark an important decision settled merely because the Agent can infer a reasonable answer.

If a later answer invalidates an earlier decision, reopen it.

## Phase 3 — Handle questions and research detours

User questions have priority over interview progression.

If the user challenges or asks about a proposal:

1. answer the question directly;
2. explain unfamiliar technical language in plain terms;
3. keep the underlying decision open unless the user actually decides it;
4. return to that decision afterward.

If external facts are needed, use `research` under `references/research-contract.md`.

Do not tell the user that research is underway until the research dispatch has actually been accepted/started by the harness. A planned research call is not an active research run.

Research never makes the user's decision for them.

## Phase 4 — Base Discovery during the interview

When a base becomes a serious candidate:

- if it is a third-party software/service base, **MUST read `references/base-discovery.md` before the base or connection route is treated as settled**;
- if it is direct local files or a simple local database, use Base Discovery only to the depth needed for fit and operation.

Base Discovery is fact-finding and fit-checking. It is not configuration.

It may happen before the interview ends because the result can change the base decision or reopen other design decisions.

Do not use a built-in recipe.

Discover enough to understand:

- what the base actually stores;
- how an Agent can read and write it;
- how permissions and authentication work;
- how attachments and non-text material work;
- how search or extraction works;
- how backup/export/migration work;
- what programmatic access is officially supported;
- what the current Agent environment can actually use.

If those facts are current, unfamiliar, or unverified, use `research`.

For a third-party software or service base whose programmatic interfaces, authentication, permissions, or limits can change over time, verify the current official connection options before locking the connection route unless they were already verified from first-party sources in the current session.

If Base Discovery shows the candidate cannot satisfy the user's needs, reopen the base decision.

Do not configure software, install tools, alter Agent configuration, authenticate, or create remote objects during the interview.

## Phase 5 — Complete the interview

Every required area in `references/interview-contract.md` must be genuinely surfaced, and important decisions must meet the depth standard defined there.

If the user will directly browse or operate the base, **MUST read `references/human-navigation.md` before the structure/navigation decision is treated as settled**.

Do not compress the interview into a few broad questions just to finish quickly.

Before readiness passes, do not use closure-signaling phrases such as "最后一个问题", "最后几个问题", "收尾问题", "问完就完整", "之后就完整了", "已经完整", "都覆盖完了", "可以定稿了", "马上可以出 SPEC", or equivalent wording merely because the conversation feels mature.

Before telling the user the design is ready for a SPEC:

1. review the internal decision map for any architecture-shaping open questions discovered during reasoning;
2. surface any such question to the user instead of resolving it silently;
3. run `references/readiness-check.md`.

If the readiness check finds missing implementation-critical facts or invalid decision provenance, continue the interview with the smallest useful question.

If the check passes, do not automatically produce the SPEC. Say something like:

> 我这边需要弄清楚的内容和实施前提都已经覆盖到了。你还可以继续问、改任何一块，也可以让我再 research 一个方向。等你觉得够了，再告诉我出 SPEC。

Only explicit user intent such as the following ends the interview:

- "问答结束"
- "可以出 SPEC 了"
- "就这些，整理方案"
- "按现在的内容出 SPEC"
- equivalent wording with the same meaning

Silence, a short acknowledgement, answering the last question, or asking another question does not end the interview.

## Phase 6 — Synthesize the design

After the user ends the interview, read `references/design-guide.md`.

Keep two abstractions separate until intentionally combined:

1. **Knowledge model** — what the knowledge is, how it is structured, how it enters, how it is found, how source material relates to derived knowledge, and how it is maintained.
2. **Human navigation model, when applicable** — how a person enters, browses, groups, filters, revisits, and understands the knowledge base without relying on the Agent for every lookup.
3. **Base operating model** — how the selected base stores information, how the Agent accesses it, what can be automated, what requires authorization, and what limitations remain.

Do not let the base dictate the knowledge model unnecessarily.

Do not hide a base limitation by changing the user's requirement without discussion.

## Phase 7 — Produce the implementation SPEC

Read `references/spec-guide.md`.

The SPEC is knowledge-base-specific. It synthesizes already-settled decisions and must not restart the interview.

If a blocking item remains unresolved, do not disguise it as settled. Either:

- produce a clearly marked draft SPEC with the blocker visible; or
- return to the relevant decision if the user prefers.

The SPEC must include:

- knowledge design;
- human navigation and presentation when people directly use the base;
- base operating path;
- exact implementation destination;
- maintenance entry point;
- operational mechanisms for core workflows;
- connection plan when the base requires a separate connection;
- validation plan;
- remaining manual or blocked work.

After presenting the SPEC, stop.

Do not initialize or configure anything yet. Pre-SPEC research artifacts are evidence, not implementation deliverables unless the user explicitly chooses to retain them. If the research harness was forced to write evidence inside the current project, do not falsely claim that no file at all was created; state the research-note exception while making clear that no knowledge-base structure, connection, or maintenance implementation has started.

## Phase 8 — Approval gate

Implementation begins only after explicit approval of the SPEC.

Examples:

- "可以，开始"
- "按这个做"
- "没问题，开工"
- equivalent wording

A question about the SPEC is not approval.

A request to change the SPEC is not approval.

## Phase 9 — Connection Setup

If the approved base requires a separate application/service connection rather than direct local access, read `references/connection-setup.md`.

Connection Setup happens only after SPEC approval.

The Agent should actively complete the approved connection work that the current environment allows.

Do not ask the user for public documentation links that the Agent can research itself.

Ask the user only for information or actions that the Agent genuinely cannot obtain or perform, such as choosing an account/workspace, granting authorization, approving installation, or providing access to a private/internal endpoint.

Never ask the user to paste API keys, tokens, passwords, or other secrets into chat, prompts, maintenance documentation, example files, or shell command arguments. Prefer OAuth/connector authorization or instruct the user to place the secret in an approved local secret store/environment location that the Agent can use without echoing its value.

Prefer project-scoped configuration when supported. Global Agent or harness configuration requires explicit approval in the SPEC.

## Phase 10 — Connection Validation

For a connection-required base, validate the connection before relying on it.

Validation must confirm the operations the approved knowledge-base design actually needs.

Typical checks may include:

- identify the intended target workspace/container;
- read;
- create or write;
- read back the written result;
- update when required;
- search when required;
- attachment handling when required.

Use the smallest safe test.

Do not claim "connected" merely because a config file exists, a CLI is installed, or authentication started.

If connection validation fails, stop the affected implementation path, explain the exact failure, and preserve all base-independent work.

## Phase 11 — Implement

Implement the approved SPEC using the tools available in the current environment.

For each core workflow, follow the operational mechanism defined by the SPEC. Do not silently substitute a different mechanism.

If the environment cannot complete a base-specific operation:

1. complete every base-independent part;
2. prepare schemas, structures, configuration, scripts, import material, maintenance documents, or setup instructions;
3. identify exactly what remains;
4. identify why it remains;
5. identify what capability, permission, or user action will unblock it.

Do not silently fall back to computer use as the only route.

## Phase 12 — Validate the knowledge base

Validate against the approved SPEC and the user's actual workflows.

At minimum, verify representative end-to-end scenarios for:

- adding knowledge;
- finding or analyzing knowledge;
- maintaining or updating knowledge;
- source traceability when required;
- operating/reconnecting to the selected base;
- respecting permissions and user boundaries.

If any implementation remains manual or blocked, validate the generated handoff material for that remaining step.

## Phase 13 — Handoff

Explain briefly:

- what was created;
- where it lives;
- how new knowledge enters;
- how users or Agents find/analyze it;
- how source material is traced when relevant;
- how the Agent reconnects to and maintains the base;
- which operations are automatic;
- which operations still require the user;
- how another Agent session continues maintenance;
- how backup/export works;
- how to check that the knowledge base remains healthy.

Keep the handoff practical and free of unnecessary knowledge-management jargon.
