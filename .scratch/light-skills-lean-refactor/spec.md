# SPEC: Light Skills Lean Architecture Refactor

**Status:** SUPERSEDED — execution authority retired by `.scratch/light-skills-core-flow-repair/spec.md` (SPEC-light-skills-core-workflow-socratic-repair)
**Repository:** `LightDevCoder/skills`
**Primary reference:** `mattpocock/skills`
**Replaces:** `.scratch/light-skills-refactor/spec.md` and its issue set
**Goal:** Make each Skill small, understandable, composable, and practical by treating `SKILL.md` as the Skill's minimal executable interface and moving only genuinely conditional detail into Skill-owned supporting material.

---

## 1. Problem

The current refactor improved the repository structure, but several Skills still carry too much prose inside `SKILL.md`.

The problem is not only duplicated explanations of neighboring Skills. Many Skills also accumulate defensive instructions such as repeated `DO NOT` clauses, handoff disclaimers, duplicated responsibility boundaries, verification prose, and wording added mainly to satisfy tests.

This creates four problems:

- the actual logic of a Skill becomes harder to see;
- simple Skills start reading like policy documents;
- neighboring Skills re-explain one another instead of composing cleanly;
- prose-coupled tests make unnecessary wording difficult to remove.

This refactor must not solve that by mechanically splitting every long `SKILL.md` into a fixed set of reference documents. The correct structure depends on the actual logic of each Skill.

**Shorter files are an outcome, not the KPI.**

---

## 2. Design Reference

Use `mattpocock/skills` as the primary design reference.

The important pattern to preserve is **progressive disclosure**, not a particular folder template:

- a very small composition Skill may contain almost nothing beyond an invocation;
- a simple standalone Skill may need only `SKILL.md`;
- a more complex Skill may keep its core execution loop in `SKILL.md` and move conditional formats, examples, or specialized guidance into local supporting files;
- supporting material belongs to the Skill that owns it;
- another Skill should normally invoke the owning Skill instead of copying its rules or deep-linking into its internal documentation.

Do not imitate Matt's repository mechanically. Extract the design principle and apply it to Light's actual workflows.

---

## 3. Core Principle: `SKILL.md` Is the Minimal Executable Interface

After the refactor, `SKILL.md` should contain only what the agent normally needs in order to execute that Skill correctly.

Typical contents may include:

- what the Skill does;
- the invocation/trigger behavior when relevant;
- the core execution loop or decision path;
- pointers to conditional supporting material;
- the real completion condition.

A section belongs outside `SKILL.md` when all of the following are true:

1. it is not needed on every normal invocation;
2. the agent can know when it needs that information;
3. the Skill can point to that information at the moment it becomes relevant.

Possible supporting material includes reference documents, scripts, assets, examples, schemas, templates, or other files. These are optional implementation tools, not required furniture.

There is **no required number, naming scheme, or shape of reference files**.

A Skill may legitimately end as:

```text
skill-name/
└── SKILL.md
```

or:

```text
skill-name/
├── SKILL.md
└── references/
    └── one-specific-reference.md
```

or a richer structure if its real logic requires it.

**The file structure must be derived from the Skill's logic. The file structure must not determine the Skill's logic.**

---

## 4. Scope Manifest

This manifest is normative for the refactor.

The implementation agent may not silently move a Skill into a more invasive category.

### 4.1 Frozen — no Skill changes

These Skills are outside the refactor:

- `eli5`
- `recap`
- `language-learning`
- `kb-init`
- `kanban-worker`
- `learn-anything`

Their Skill directories must remain byte-for-byte unchanged.

**User-approved amendment — 2026-08-27:** `recap` is the sole exception to
this frozen boundary. Its `SKILL.md` may be reduced to required frontmatter and
one execution sentence that keeps the explicit `$recap` manual trigger. The
behavior description remains: `show one concise line about the current session
without replacing or compacting conversation history.` No automatic recap is
added. No other Frozen package is released from the boundary by this amendment.
The package-local `recap/tests` files remain byte-for-byte frozen as historical
tests for the superseded long-form contract; they are excluded from the active
suite because changing them was not authorized. Repository-level functional
tests are the acceptance authority for the amended `recap/SKILL.md` contract.

This includes their:

- `SKILL.md`;
- local references;
- scripts;
- assets;
- local agent metadata;
- other files under the Skill directory.

Repository-level indexes or tests may continue to recognize these Skills, but those changes must never require modifying the Frozen Skill itself.

Before implementation, record a hash of every file under these directories. Re-run the same check at final acceptance.

**"This could also be improved" is not a reason to modify a Frozen Skill.**

---

### 4.2 Integration-only — preserve behavior, make only necessary wiring changes

These Skills already have an accepted core design. They may receive only the smallest changes required to fit the final Light architecture:

- `manuscript-ops`
- `release-workflow`
- `research`
- `prototype`
- `tdd`
- `handoff`
- `diagnosing-bugs`
- `wizard`
- `teach`
- `wait-what`
- `to-questionnaire`
- `writing-for-agents`
- `resolving-merge-conflicts`

Allowed work includes only changes such as:

- updating a renamed Skill invocation;
- repairing an integration pointer;
- adapting repository-level invocation metadata;
- updating catalog/README integration;
- fixing a composition edge created by this refactor;
- updating tests that validate repository integration rather than rewriting Skill prose.

The Skill's purpose, execution logic, writing style, and internal structure are presumed valid.

If a proposed change would still be desirable even if this Lean Refactor did not exist, it is probably **not** an Integration-only change and should not be included here.

Do not turn an Integration-only Skill into a Full-refactor Skill without an explicit change to this SPEC.

---

### 4.3 Full refactor — reconstruct logic, then redesign information structure

These Skills are the actual refactor targets:

- `agent-config`
- `ask-light`
- `clarify`
- `code-review`
- `decision-map`
- `generic-review`
- `implement`
- `project-clarify`
- `project-init`
- `project-review`
- `project-spec`
- `project-tickets`
- `review-loop`
- `socratic`

These Skills may be substantially rewritten, but only after their real behavior has been reconstructed.

---

## 5. Phase 0 — Retire the Previous Refactor Plan

Before changing any Skill, retire the previous active planning set.

Current previous plan:

```text
.scratch/light-skills-refactor/spec.md
.scratch/light-skills-refactor/issues/
```

Move it to an archival location such as:

```text
.scratch/archive/light-skills-refactor/
```

Preserve the historical content, but make its state unambiguous:

```text
status: superseded
superseded_by: ../light-skills-lean-refactor/spec.md
execution_authority: none
```

Equivalent clear archival metadata is acceptable.

The old 13 issues are historical evidence. Their unchecked tasks are **not outstanding work** after this SPEC becomes active.

Do not complete old tickets merely because their checkboxes are still open.

Create the new active work area:

```text
.scratch/light-skills-lean-refactor/
├── spec.md
├── analysis/
└── issues/
```

This SPEC becomes the only active planning authority for this refactor.

New implementation tickets must be generated from this SPEC and the logic reconstruction work below, not copied from the previous ticket set.

---

## 6. Phase 1 — Reconstruct the Real Logic Before Editing

Do not begin by shortening files.

For every Full-refactor Skill, first read its current implementation, relevant tests, repository documentation, known callers/callees, and any upstream Matt Skill that materially informed it.

Then reconstruct what that Skill actually is.

The analysis must establish, in whatever concise form best fits that Skill:

- its real job;
- what state or user need causes entry into it;
- its core execution loop or decision logic;
- what it produces or changes;
- its actual completion/stop condition;
- what knowledge is required on every invocation;
- what knowledge is only conditionally needed;
- what currently duplicates another Skill;
- why its important negative constraints exist;
- whether those constraints are still needed once the positive behavior is stated clearly;
- whether any behavior currently in this Skill actually belongs to another Skill.

This is a reasoning requirement, **not a documentation template**.

Do not produce 14 identical audit documents with the same headings merely to satisfy the phase.

The analysis files under `.scratch/light-skills-lean-refactor/analysis/` are temporary implementation aids. Their structure should follow the Skill being analyzed. They are not part of the final public Skill interface.

### Required examples of reasoning

For `socratic`, determine the actual conversational loop and its exit condition before deciding whether it needs references.

For `clarify`, determine what makes clarification complete and how it differs from `socratic` and `project-clarify`.

For `project-init`, reconstruct the initialization decision tree before deciding whether project detection, initialization flows, or other branches deserve separate supporting material.

The same principle applies to every Full-refactor Skill.

**Understand first. Restructure second.**

---

## 7. Phase 2 — Replace Defensive Prose With Positive Behavior

Repeated negative constraints are a major refactor target.

Do not mechanically move existing `DO NOT` clauses into `references/BOUNDARIES.md`.

For every meaningful negative constraint, determine why it exists.

Use this decision model:

```text
Can the correct positive behavior make the restriction unnecessary?
    → Remove the negative wording and state the positive behavior.

Is the restriction a repository-wide invariant?
    → Move it to the appropriate repository-level rule.

Does it merely describe another Skill's responsibility?
    → Remove the duplicated explanation and use composition or a concise boundary.

Is it only needed on a rare branch?
    → Put the detail in conditional local supporting material if it still adds value.

Is it a genuinely high-risk, Skill-specific failure mode that remains easy to make?
    → Keep the minimal explicit guardrail.
```

The goal is not zero negative language.

The goal is that a Skill is understandable from what it **does**, rather than from a wall of things it is forbidden to do.

---

## 8. Phase 3 — Design Supporting Material Per Skill

Only after the Skill's real logic is understood should the agent decide whether anything belongs outside `SKILL.md`.

Supporting material must be **need-driven**.

Good reasons to create a local reference include:

- a detailed format that is only needed when producing a particular artifact;
- branch-specific instructions;
- a substantial example set;
- a domain-specific checklist used only in one stage;
- a schema or template;
- a long procedure that the core Skill only invokes in a specific condition.

Bad reasons include:

- every Skill "should" have references;
- keeping a fixed file count;
- mirroring the headings from the old `SKILL.md`;
- moving prose out solely to reduce line count;
- creating `METHOD.md`, `BOUNDARIES.md`, `VERIFICATION.md`, and `EXAMPLES.md` by default;
- copying another Skill's internal rules.

Name supporting files according to the information they actually contain.

Create zero files when zero files are needed.

---

## 9. Skill Ownership and Composition

Each piece of detailed knowledge should have one clear owner.

When Skill A needs Skill B's capability, prefer invoking Skill B rather than embedding a second explanation of Skill B inside Skill A.

Do not use cross-folder deep references as a substitute for composition.

Prefer:

```text
project-review
    → invokes review-loop when iterative review is needed
```

over:

```text
project-review/SKILL.md
    → redefines review-loop's method
    → redefines review-loop's stop conditions
    → redefines review-loop's reviewer contract
```

A caller may contain the minimum information needed to decide **when** to call another Skill. It should not restate the callee's internal runbook.

Shared repository-level invariants may live at repository level. Skill-specific supporting material stays with the Skill that owns it.

---

## 10. Router and Wrapper Skills

Routers, wrappers, and composition Skills deserve especially aggressive simplification when they have little behavior of their own.

If the real logic of a Skill is "choose one of these capabilities" or "invoke these two Skills in sequence", its `SKILL.md` should express that directly.

Do not inflate a wrapper merely to make it resemble a complex workflow Skill.

`ask-light` should primarily route.

A wrapper should primarily compose.

A recap-like Skill should primarily perform its tiny action.

Complexity must follow responsibility.

---

## 11. Tests — Validate Behavior, Not Prose

The current test suite contains assertions that couple behavior to literal wording in `SKILL.md`.

Remove or rewrite prose-coupled tests where the exact phrase is not itself a product requirement.

Tests should prioritize:

- valid frontmatter and metadata;
- invocation policy;
- required file existence;
- valid local pointers;
- valid composition edges;
- scripts and executable helpers;
- behavior-focused smoke tests where practical;
- important output contracts;
- real high-risk boundaries;
- Frozen directory integrity;
- Integration-only scope integrity.

Avoid tests whose main purpose is:

```python
assert "specific sentence" in skill_md
assertRegex(skill_md, "required prose wording")
```

unless that literal text is genuinely part of a machine-readable or user-visible contract.

A test failure caused only because explanatory prose was shortened is normally evidence that the test is too coupled to prose.

Do not add prose back merely to make such a test pass.

Also clean up test discovery issues so helper functions are not accidentally collected as tests.

---

## 12. Repository-Level Documentation

README/catalog/docs should help humans discover Skills and understand where they fit.

They should not force every `SKILL.md` to redraw the entire Skill graph.

Keep repository-level routing and categorization outside individual Skills where possible.

When a Full-refactor Skill becomes simpler, update human-facing documentation only where its actual behavior, invocation, or relationship changed.

Do not rewrite unrelated documentation for stylistic consistency.

---

## 13. Implementation Order

Use this execution order:

```text
0. Archive and supersede the previous SPEC/tickets
1. Record Frozen baselines
2. Establish the normative scope manifest
3. Reconstruct logic for all Full-refactor Skills
4. Review the logic map across neighboring Skills
5. Create new implementation tickets from the reconstructed logic
6. Refactor Full-refactor Skills
7. Apply minimal Integration-only wiring
8. Rewrite prose-coupled tests
9. Update only affected repository documentation
10. Run full validation
11. Verify Frozen and Integration-only scope integrity
12. Mark the new tickets complete and record final results
```

Do not refactor Skills opportunistically while still in the logic-reconstruction phase.

---

## 14. Neighboring Skill Groups That Must Be Reasoned About Together

Some Full-refactor Skills cannot be understood correctly in isolation.

At minimum, reason across these relationships before implementation:

```text
socratic
clarify
project-clarify
project-init
```

```text
project-spec
project-tickets
implement
code-review
```

```text
generic-review
review-loop
project-review
```

```text
ask-light
+ the final repository routing model
```

The purpose is to find duplicated responsibility and unclear boundaries before editing prose.

Do not force these groups into identical architecture. They are grouped for reasoning, not templating.

---

## 15. Out of Scope

This refactor is not an excuse to:

- redesign Frozen Skills;
- redesign Integration-only Skills;
- invent new Skills merely to reduce file size;
- rename large parts of the repository for aesthetics;
- enforce a universal reference-folder template;
- impose maximum line counts on `SKILL.md`;
- optimize every piece of documentation;
- complete superseded tickets;
- rewrite direct Matt ports without a Light integration requirement;
- change established workflow responsibilities unless the logic reconstruction demonstrates that the current split is genuinely wrong.

If a broader redesign becomes desirable, capture it separately rather than expanding this refactor.

---

## 16. Acceptance Criteria

The refactor is complete only when all of the following are true.

### Planning state

- the previous `.scratch/light-skills-refactor/` plan is clearly archived/superseded;
- no old issue is treated as active work;
- the new SPEC and its tickets are the only active refactor planning set.

### Frozen integrity

- five Frozen Skill directories match their pre-refactor hashes exactly;
- `recap` matches its pre-refactor hashes except for the single user-approved
  `SKILL.md` amendment recorded in §4.1.

### Integration-only integrity

- every Integration-only diff can be explained as necessary Light integration;
- no Integration-only Skill receives an unsolicited behavioral redesign;
- no standard reference structure is added merely for consistency.

### Full-refactor quality

For every Full-refactor Skill:

- its actual logic was reconstructed before editing;
- the final `SKILL.md` exposes the core executable behavior clearly;
- repeated sibling logic has been removed;
- unnecessary defensive `DO NOT` prose has been removed or converted into clearer positive behavior;
- conditional detail is loaded progressively;
- references/scripts/assets exist only where the Skill genuinely benefits from them;
- the supporting structure is specific to that Skill rather than copied from a template;
- completion/stop behavior remains clear.

### Composition

- one Skill does not re-document another Skill's internal runbook;
- callers contain only the information needed to decide when/how to compose;
- local supporting material has a clear owning Skill.

### Tests

- the full test suite passes;
- test collection succeeds cleanly;
- the active suite excludes only the frozen historical `recap/tests` files
  identified in §4.1 and replaces their superseded prose checks with current
  repository-level functional coverage;
- prose-only assertions have been removed unless literal wording is a real contract;
- tests protect behavior, invocation, composition, execution, and important boundaries instead of prose layout.

### Documentation

- affected README/catalog/docs match the final behavior;
- unrelated docs are left alone.

---

## 17. Final Review Questions

Before declaring completion, review the repository from the perspective of someone opening a Skill for the first time.

For each Full-refactor Skill, ask:

> Can I understand its real job and execution path quickly from `SKILL.md`?

> Is the detail I do not need right now kept out of the way?

> If I need more detail, is it obvious when and where to load it?

> Does this Skill explain itself, or spend most of its time explaining what it is not?

> Is it copying another Skill's job?

> Did we create a supporting file because the Skill needed one, or because a refactor template told us to?

If the answer exposes unnecessary cognitive load, continue simplifying.

---

## 18. Expected End State

The final repository should feel like a toolbox rather than a policy manual.

Simple Skills remain simple.

Composition Skills primarily compose.

Complex Skills expose a small executable surface and reveal deeper material only when needed.

Each Skill owns its own specialized knowledge.

Neighboring Skills stop repeating one another.

Tests make the architecture safer without freezing prose.

And most importantly: future edits should be able to make a Skill clearer or shorter without fighting a wall of legacy wording contracts.
