# Task assessment

Task assessment guides `agent-config` in determining the appropriate task execution
shape and right-sizing model tiers and reasoning effort.

Do not use raw token or word counts as an indicator of task complexity. Task shape
and difficulty are semantic properties of the work.

---

## 1. Task shape

Task shape determines whether work executes in a single continuous context or requires
ticket-level decomposition and coordination.

| Task shape | Meaning | Evaluation criteria |
|---|---|---|
| `single-pass` | Work safely completed in one continuous, controlled execution session. | • Single cohesive concern or bounded subsystem.<br>• Compact verification and review surface.<br>• No natural dependency chain or isolated parallel units.<br>• Implementation state easily retained in a single context window. |
| `decomposed` | Work broken into multiple independent or dependency-ordered work units. | • Multiple distinct, independently verifiable slices.<br>• Explicit dependency graph between components.<br>• Multiple architectural concerns (e.g. schema + backend + frontend + migration).<br>• Context window risk if attempted in one pass.<br>• Formal ticket graph already exists or is required. |

### Anti-wordcount rule

Word count or SPEC length is strictly prohibited as a proxy for task shape (never use word count):
- A 700-word brief spanning database migration, API contracts, and security audits is `decomposed`.
- A 3,000-word detailed specification for proofreading a single document or updating one reference file is `single-pass`.

---

## 2. Work-item difficulty and risk

Each work item is evaluated to determine the minimum sufficient intelligence tier
needed to execute it safely.

| Difficulty | Semantic description | Example work | Model & effort guidance |
|---|---|---|---|
| `routine` | Low uncertainty, mechanical transformation, local edits, clear patterns, trivial verification. | Typos, documentation wording, boilerplate tests, config additions, small refactors. | Lower sufficient model tier; economical/medium reasoning effort. |
| `moderate` | Standard feature slice, established architecture, clear interfaces, moderate reasoning depth. | New API endpoint, schema extension, standard UI component, unit & integration tests. | Middle model tier; medium/high reasoning effort. |
| `demanding` | High ambiguity, architectural seams, non-trivial concurrency, cross-cutting invariants, difficult debugging. | Core protocol changes, complex state machines, performance optimizations, multi-agent synchronization. | High model tier; high reasoning effort. |
| `critical` | Core security boundaries, irreversible data migrations, existential system invariants, zero-tolerance failure modes. | Cryptographic protocols, auth kernel, database schema rewrites, multi-system cutovers. | Highest available model tier; maximum supported reasoning effort. |

### Evaluation dimensions

Difficulty is assessed across eight semantic axes:
1. **Reasoning depth:** Chains of logic required before writing code.
2. **Uncertainty:** Incomplete documentation, exploratory tasks, unknown edge cases.
3. **Coupling:** Extent of blast radius across codebase modules.
4. **Architectural consequences:** Long-term impact on interfaces or design.
5. **Debugging & research burden:** Need to read external specs, trace stack traces, or profile.
6. **Reversibility:** Ease of rolling back or recovering from incorrect implementation.
7. **Verification difficulty:** Simplicity of unit tests vs complex integration environments.
8. **Failure risk:** Impact on system integrity, security, or data loss.

### Monotonicity invariant

Across any set of work items, a more difficult or higher-risk ticket must never
be assigned a lower model tier or lower reasoning effort than a simpler ticket
under equivalent host constraints.
