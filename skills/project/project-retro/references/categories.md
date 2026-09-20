# Retrospective Improvement Categories

Use these categories when analyzing session friction and extracting durable improvements.

---

## 1. Navigation

- **Question:** How easily did the agent find the relevant files, tests, contracts, and configurations?
- **Friction symptoms:**
  - Repeated `find` or `grep` searches with broad patterns across unrelated directories.
  - Modifying the wrong file or missing an adjacent coupled file.
  - Confusion over where contracts, schemas, or tests live.
- **Useful signals:**
  - >3 turns spent locating a file known to exist.
  - Stale directory pointers causing agent confusion.
  - Missing entry file or directory index.
- **Typical durable improvements:**
  - Add navigation pointers in `AGENTS.md` / `README.md` to specific subsystems.
  - Maintain a table of contents or directory map for complex file structures.
  - Co-locate tests or types with their implementations when conventions allow.

---

## 2. Automated Checks & Guardrails

- **Question:** Could an automated, deterministic check have caught an error the agent made?
- **Friction symptoms:**
  - Agent made syntax, type, formatting, or contract errors only caught late or during manual review.
  - Regressions were introduced in existing functionality.
  - Check script exists but was never wired to CI or pre-commit hooks.
  - Repository has no automated CI preflight or verification check.
- **Useful signals:**
  - Reviewer repeatedly catches the same deterministic failure.
  - Release identity or package count mismatch.
  - Test fixture contamination or ground truth label leakage into prompt context.
  - Contract drift between implementation and schema.
- **Typical durable improvements:**
  - Wire lint, typecheck, or test commands into pre-commit hooks and CI workflows.
  - Write dedicated preflight scripts (e.g. `scripts/verify_release_integrity.py`).
  - Add negative test assertions and fixture sanitization tests (e.g. `test_evaluation_fixtures_clean.py`).
  - Implement deterministic structural AST or schema linters.
  - *Rule:* Prefer building an automated check over writing a prose instruction.

---

## 3. Coding Standards & Review

- **Question:** Should reviewer instructions be clarified, or should a rule be moved between code and standards?
- **Friction symptoms:**
  - Reviewer agent failed to catch a defect that human inspection identified.
  - Reviewer repeatedly flagged subjective or nitpicky items lacking team consensus.
  - Standards documentation mixes mechanical rules with architectural judgment calls.
- **Useful signals:**
  - Repeated reviewer false positives on acceptable patterns.
  - Review rubric ambiguities leading to conflicting verdicts.
  - Mechanical style guidelines enforced via human review rather than tools.
- **Typical durable improvements:**
  - Separate mechanical violations from architectural judgment calls:
    - **Mechanical rules** (import order, syntax patterns, banned APIs, naming conventions) belong in automated linters, AST checks, or pre-commit hooks.
    - **Judgment calls** (architectural consistency, readability, design patterns) belong in `CODING_STANDARDS.md`.
  - Clarify ambiguous rules in review rubric files and reviewer prompts.

---

## 4. Steering Economy (`AGENTS.md` / `CLAUDE.md`)

- **Question:** Are instructions in agent steering files concise, effective, non-redundant, and current?
- **Friction symptoms:**
  - `AGENTS.md` or `CLAUDE.md` is overly long (>500 lines) and consumes valuable context window space.
  - Instructions contain rules that the agent naturally follows without prompting (no-ops).
  - Domain-specific details clutter the global entry file instead of using progressive disclosure.
  - Steering files contain stale paths, outdated milestone trackers, or obsolete instructions.
- **Useful signals:**
  - Agent misled by obsolete scratchpad or milestone pointers.
  - Redundant rules that duplicate upstream tool definitions or standard language idioms.
  - Instructions that fail to alter agent behavior across sessions.
- **Typical durable improvements:**
  - Move detailed guides into `docs/` or `references/`, leaving concise pointers in `AGENTS.md`.
  - Delete instructions that do not demonstrably change agent behavior.
  - Replace hardcoded feature paths with dynamic wayfinding conventions.

---

## 5. Tool Economy & Context

- **Question:** Did the agent make expensive, redundant, or zero-value tool calls?
- **Friction symptoms:**
  - Reading full multi-megabyte files when a bounded slice or grep would suffice.
  - Redundant tool calls fetching the same metadata repeatedly.
  - Semantic inference or LLM calls dispatched when downstream code has no active consumer branching on the output.
- **Useful signals:**
  - Unconditional query dispatching on singleton candidate sets.
  - High token consumption on routine status queries.
  - Repeated large file reads (>50KB) in consecutive turns.
- **Typical durable improvements:**
  - Implement active consumer query planning (dispatch queries only when downstream logic branches on the result).
  - Use offset/limit or targeted search tools.
  - Add summary indexes to large data files.

---

## 6. Information Access & Telemetry

- **Question:** Was critical information missing, hard to reach, or unverified during the run?
- **Friction symptoms:**
  - Inability to inspect server logs, database state, or network responses.
  - Missing environment documentation, required secret keys, or credential setup.
  - Upstream specifications or canonical CLI conventions were missing locally, forcing the agent to guess.
- **Useful signals:**
  - Agent guesses CLI flags or directory scopes due to lack of local documentation.
  - Missing error traces or hidden server crashes.
  - Secrets leaked or unmasked in debug outputs.
- **Typical durable improvements:**
  - Add canonical reference files (e.g. `skills_cli_conventions.md`) documenting verified upstream provenance.
  - Tee development server logs to inspectable log files.
  - Document local environment variables and reproduction commands in reference docs.

---

## 7. Test Architecture & Environment Isolation

- **Question:** Are tests hermetic, isolated, reproducible, and decoupled from external environment assumptions?
- **Friction symptoms:**
  - Tests pass on the author's machine but fail in clean CI or standalone checkouts.
  - Implicit dependencies on sibling repositories checked out in adjacent folders.
  - Contract drift between local test fixtures and upstream runtime schemas.
- **Useful signals:**
  - `FileNotFoundError` when running tests in a clean container without external sibling folders.
  - Unpinned fixture schemas diverging from upstream companion schemas.
  - All-or-nothing test suites lacking clear separation between unit contracts and integration tests.
- **Typical durable improvements:**
  - Establish a two-layer test architecture:
    - **Layer 1 (Hermetic Contract Test):** In-repo schema snapshots with explicit provenance metadata (`METADATA.json`), 100% passing offline without sibling dependencies.
    - **Layer 2 (Cross-Repo Integration Test):** Dedicated integration channel targeting pinned companion revisions, with non-blocking drift detection against companion latest.

---

## 8. Workflow & Release Mechanics

- **Question:** Are state transitions, release boundaries, tag immutability, and evidence receipts protected against human error?
- **Friction symptoms:**
  - Release tags retroactively moved or rewritten, breaking consumer cache guarantees.
  - Historical changelog sections mutated without a corresponding version bump.
  - Inconsistent version claims across release notes, receipts, and documentation.
- **Useful signals:**
  - Post-release provenance confusion requiring manual Git history audits.
  - Tag retargeting during rapid stabilization iterations.
  - Manual copy-pasting of commit SHAs leading to stale references.
- **Typical durable improvements:**
  - Implement deterministic release preflight gates enforcing tag immutability:
    - Tag nonexistent $\to$ allowed.
    - Tag exists with same target commit SHA $\to$ idempotent pass.
    - Tag exists with different target commit SHA $\to$ hard fail.
  - Distinguish mechanical invariants (tag SHA, receipt SHA, package count) from human-review invariants (release scope and documentation corrections).
