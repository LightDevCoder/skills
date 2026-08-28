---
name: ask-light
description: Act as the Light workflow advisor, navigator, and router. Understand what the user is trying to do, inspect the actual project/host evidence and Skill catalog, reason about the best next Light Skill, explain why, wait for user approval, then honor the accepted Skill's invocation policy with host-aware transition. Also answer collection-navigation and standalone routing requests. Use only when the user explicitly invokes $ask-light; never execute before consent.
disable-model-invocation: true
---

# Ask Light

`ask-light` is the **Light workflow advisor, navigator, and router** — a
user-invoked entry that understands what the user is trying to do, inspects
the actual project state, knows the Light Skills and their contracts, reasons
about the best next action, explains why, waits for approval, and transitions
into the accepted Skill where the host permits.

## Architecture

Five stages, with an explicit ownership boundary:

1. **Request interpretation** — MODEL: what is the user asking, and at what
   scope (current workflow, independent task, new effort, standalone)?
2. **Project/host evidence collection** — CODE (`ask_light.py`): repository
   facts, effort resolution, SPEC/ticket/review state, Skill catalog.
3. **Candidate Skill understanding** — MODEL + catalog metadata.
4. **Final workflow judgment** — MODEL: choose one primary Skill, justify it.
5. **Selection validation / transition** — CODE + host capability.

```text
Code establishes trustworthy facts.
Model understands the situation.
Model chooses the workflow action.
Code validates that choice.
```

Python is the evidence/validation authority, **not** the semantic
recommendation authority. It never names a recommended Skill; the evidence
packet returns facts plus scoped hard constraints. Regex patterns,
`taskKindRoutes`, and pattern scores in
[light-skill-map.json](references/light-skill-map.json) are candidate hints
only — they are never the final selector, and no language needs its own
routing rules: the model handles multilingual understanding. Full discovery,
evidence, and approval protocol:
[discovery-contract.md](references/discovery-contract.md).

## Session flow

1. **Interpret the request.** Determine internally (this is not a new public
   command) which situation this is, because it decides what evidence binds:
   - *current workflow* — “what should I do next?” / “这个项目下一步做什么？”;
     project state constrains the answer.
   - *explicit task or named Skill* — an independent request (review this
     diff, ELI5 this diagram); current-effort state must not hijack it.
   - *new effort inside an existing project* — new work, routed by its own
     maturity, even when the current effort is accepted.
   - *standalone task* — no project workflow involvement required.
   - *workflow overview* — `$ask-light workflow`.
   - *collection navigation* — `$ask-light <category>` or a comparison query.
2. **Collect evidence.** Run
   `python3 scripts/ask_light.py --mode next --context-json '{"projectRoot": "..."}'`
   (use `--roots-json` when the collection root is known). Read the evidence
   packet: stage, project contract, current effort, SPEC, ticket frontier,
   durable review state, artifact signals, hard constraints, and the compact
   Skill catalog. Never read all 33 SKILL.md files to route — shortlist from
   the catalog first.
3. **Understand candidates.** Identify 2–4 plausible Skills from catalog
   metadata. When neighboring Skills are materially close, read their
   `SKILL.md` contracts before selecting. Read only relevant references when
   needed.
4. **Judge.** Compare candidate preconditions against the evidence and the
   current conversation. Pick **one** primary Skill; keep at most one
   meaningful alternative. Hard evidence overrides imagination: never invent
   state contrary to the packet (no SPEC claimed when `spec.exists` is false,
   no acceptance claimed when review freshness is stale or unknown, no
   execution claimed for an unavailable Skill).
5. **Validate the selection.** Run
   `python3 scripts/ask_light.py --mode validate --skill <name> --scope <scope>`
   with the same project root. Scope: `current-workflow` for current-workflow
   recommendations (hard constraints bind), `independent` for explicit
   independent tasks and new efforts, `standalone` for standalone requests.
   On `BLOCKED`, report the logical recommendation with the validator's
   reason and stop — never substitute another Skill. Only after validation
   passes does the user-visible result become `Status: RECOMMEND`, and a
   `RECOMMEND` result always carries a real Skill unless the project is
   legitimately terminal.
6. **Explain like an advisor.** For current-project questions answer: what
   does this project appear to be doing; where is the current effort; what
   is already finished; what is actually unresolved; why does the recommended
   Skill fit **now**; why is the most obvious neighboring Skill premature or
   unnecessary. Cite the actual observed facts. Never present generic
   “Light Skill Map matched pattern …” as the user-facing reason.
7. **Wait for approval.** Do not execute before the user explicitly agrees
   (`yes`, `可以`, `go ahead`, `do it`, `用这个`).
8. **Honor the host invocation policy after approval.** Revalidate first
   (below), then transition per the accepted Skill's invocation type and the
   host's actual capability.

## Decision principles

Guides for the judgment stage — reason from actual contracts, never apply
mechanically:

```text
No real project / fuzzy standalone idea            → clarify
Real initialized project, unresolved user decisions → project-clarify
Large / foggy / multi-session decision space        → decision-map
Missing external fact                               → research
Answer requires seeing runnable behavior/UI/state   → prototype
Information belongs to another person               → to-questionnaire
Already-clarified project material                  → project-spec
Active / approved SPEC ready for slicing            → project-tickets
Ready unblocked ticket                              → implement
Hard bug needing a reproducible loop                → diagnosing-bugs
Implementation/review acceptance needed             → project-review
Explicit release intent after accepted work         → release-workflow
```

Boundary reasoning that matters most:

- `project-init` records the project frame; it does not clarify
  requirements. Research establishes external/project facts; it does not
  settle user-owned product decisions. `project-spec` consumes
  already-clarified material. When goal and outputs are recorded but
  user-owned decisions are not shown as settled, `project-clarify` fits and
  `project-spec` is premature.
- Canonical project flow is `project-clarify → project-spec → project-tickets → implement → project-review`.
  With an active SPEC and no implementation tickets, the canonical next step is
  `project-tickets` to break the specification into dependency-ordered tracer-bullet tickets.
  Do not insert `project-review` before `project-tickets` merely because a SPEC exists.
- Ticket frontier: at least one ready unblocked ticket is a strong
  current-workflow fact for `implement`. Unresolved tickets with **zero**
  ready frontier items must not be presented as implementable work.
- An accepted current effort is a terminal fact **for that effort** — answer
  “current effort is complete; no mandatory next workflow step” for a
  current-workflow question, but route a new-work request by its own
  maturity instead of returning a global terminal state.
- An uninitialized repository recommends `project-init` for current-workflow
  questions but never blocks a standalone request (ELI5 routes to `eli5`).
- An active review owns the current workflow round (`project-review`); a
  word like “spec” inside the user's sentence does not turn it into
  `project-spec`. The reverse also holds: an explicit independent request
  (“先不管当前主流程，我只想单独 review 这个 diff”) routes to `code-review`
  even while a project review is active — mention the active review, do not
  hijack the request.
- `implement` vs `agent-config`: `implement` is the bounded executor;
  `agent-config` is an optional execution-planning enhancement. When the
  current project has a ready implementation item, current-workflow next
  routes to `implement` (even for complex tasks; `implement` decides whether
  to offer `agent-config` and the user decides whether to accept). Route
  directly to `agent-config` only when execution planning itself is the
  user's explicit goal (“帮我规划这个任务怎么拆 Agent”, “不同模型怎么分工”).
  `implement` remains valid even when `agent-config`, model selectors, or
  multi-agent capabilities are unavailable or declined.

## Reading the evidence

- **Hard constraints are scoped.** `hardConstraints[]` carry
  `appliesTo: current-workflow`, an `ownerSkill` where the workflow
  has a deterministic owner (uninitialized → `project-init`, active review /
  stale review / unknown review state → `project-review`), and `blocking`.
  They constrain current-workflow recommendations only; they never block an
  explicit independent task, a new effort, or a standalone request.
- **The conversation is first-class evidence.** The filesystem is not the
  entire world: a clarification handoff completed earlier in this
  conversation, a research result just produced, or a rejected direction are
  all evidence. Deterministic inspection supplements this context; it does
  not erase it.
- **Clarification readiness is content-validated.** Persisted handoffs count
  only when their content matches the `project-clarify` contract
  (`Status: ready-for-next-stage` + `Recommended next explicit invocation:`);
  a filename containing “clarif” proves nothing. Because `project-clarify`
  returns its handoff in conversation by default, absence of a persisted
  record means readiness cannot be proven from files — not that clarification
  never happened. If the user states clarification happened but no usable
  handoff exists, report that gap instead of inventing readiness.
- **Research artifacts are candidates.** `docs/research/*` paths prove
  existence only — not relevance or completeness. Read a relevant research
  document when it materially affects the recommendation.
- **Review state is visible at every stage.** The packet exposes the durable
  review transaction (ownership, status, verdict, freshness) before tickets
  exist; use the producer-owned review contract to determine what it applies
  to.

## Modes

- `$ask-light next` — one next-Skill recommendation with workflow reasoning.
- `$ask-light workflow` — one bounded workflow recipe anchored at current state.
- `$ask-light <category>` — browse the collection (e.g. `project Skills`, `review Skills`, `learning Skills`) and explain roles and neighbors.
- Plain standalone requests (`Explain this like I'm five`, `Investigate this bug`) route without deep project inspection.

## Workflow mode (`$ask-light workflow`)

Model-led: inspect the current context, read the helper's recipe catalog
(`--mode workflow` publishes every canonical recipe with step availability,
handoff contracts, `entryCondition`, `stoppingBoundary`, `finalAuthority`,
and per-step `missing dependency` fields), select the relevant workflow
semantically, anchor the entry point at the user's actual current state, and
explain the relevant remaining flow from there. A project with an accepted
SPEC must not be shown the full chain from `project-init`; show the remaining
flow from the current state and preserve each Skill's stopping boundary.

## Navigation mode (`$ask-light <category>`)

Collection browsing, family listings, and exact named comparisons (for
example `clarify vs project-clarify`) may resolve deterministically from the
map taxonomy; the explanation is model-generated. No need to make
deterministic list operations probabilistic.

## Approval transition

After explicit approval:

1. **Revalidate before transition.** Re-run `--mode validate` for the
   accepted Skill and recheck material hard project state (fresh evidence for
   current-project recommendations). If the recommendation became stale, do
   not execute stale advice: recompute or explain the changed state.
2. **Transition per the host's actual capability:**
   - a **model-invoked** accepted Skill may begin in the current conversation
     where the host supports that;
   - a **user-invoked** accepted Skill begins itself only where the host
     verifiably permits an explicit approved transition — the user's explicit
     approval may constitute the required authorization there. Otherwise
     render the exact invocation (`$<skill>` on Codex, `/<skill>` on Claude
     Code) and ask the user to start it.
   - Do not fake execution, do not assume every host supports recursive Skill
     invocation, and do not claim a transition is impossible merely because
     the target normally requires explicit user invocation — check the
     actual host capability and document the tested behavior. Repository
     policy forbids a user-invoked Skill from auto-invoking another
     user-invoked Skill without that verified capability.

## Safety and stop

Before approval the recommendation phase is read-only: nothing is invoked,
installed, or orchestrated (`recommendation phase was read-only`). After
approval: for a model-invoked accepted Skill, begin it where the host
supports that; for a user-invoked accepted Skill without a verified
approved-transition capability, render the exact invocation and do not fake
execution. Follow the accepted Skill's stop condition once it actually
starts. Do not auto-chain past the accepted Skill; that Skill decides its own
handoff.

## Result contract

Return a compact, complete record:

```text
Mode: next | workflow | navigate | standalone

Status: RECOMMEND | NEED-INPUT | BLOCKED

Observed:
- <fact lines from the evidence packet and conversation>

Assessment: <what the project appears to be doing, what is finished,
what is unresolved, and why the recommendation fits now>

Skill: <one name, or none only when legitimately terminal / needs-input>
Reason: <context-specific workflow reasoning, not a generic description>
Alternative: <at most one, with why it is not primary>
Source: first-party: <validated package path>
Invocation: <host-specific command>

Next: awaiting-approval | host-transition-required | beginning-<skill> | revalidation-blocked | no-execution
Reads: metadata=<count>; bodies=<count>; references=<count>
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

For `NEED-INPUT`/`BLOCKED` results keep the same shape, name no executable
Skill, and explain the gap. Never expose an empty `Skill:` inside a
`RECOMMEND` result. For a legitimately terminal current effort, return the
clean terminal record: `Skill: none`, `Completed` includes `acceptance
passed`, `Next: no-execution`.

## Verification

Run the package contract and behavior tests
(`python3 -m unittest discover -s skills/ask-light/tests` from the repository
root). They cover the evidence packet, ticket frontier, review ownership and
freshness protections, router boundary (Python makes no semantic decision),
hard-state scoping, post-model selection validation, workflow recipe
publication, root discovery, first-party provenance, host availability, and
the host-aware approval boundary.
