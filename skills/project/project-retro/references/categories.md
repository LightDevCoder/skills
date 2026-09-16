# Retrospective Improvement Categories

Use these six categories when analyzing an agent session or project run.

## 1. Navigation

- **Question:** How easily did the agent find the relevant files, tests, and configurations?
- **Friction symptoms:**
  - Repeated `find` or `grep` searches with broad patterns.
  - Modifying the wrong file or missing an adjacent coupled file.
  - Confusion over where assets, templates, or tests live.
- **Remediation patterns:**
  - Add navigation pointers in `AGENTS.md` / `README.md` to specific subsystems.
  - Maintain a table of contents or directory map for complex file structures.
  - Co-locate tests or types with their implementations when repository conventions allow.

## 2. Automated Checks & Guardrails

- **Question:** Could an automated, deterministic check have caught an error the agent made?
- **Friction symptoms:**
  - Agent made syntax, type, formatting, or lint errors that were only caught late or during manual review.
  - Regressions were introduced in existing functionality.
  - A check script exists in the repository but was never wired to CI or git hooks.
  - The repository has no pre-commit hook or automated CI check at all.
- **Remediation patterns:**
  - Wire existing lint/test commands into pre-commit or CI workflows.
  - Add custom lint rules or AST checks for repository-specific invariant violations.
  - Introduce fast local verification scripts (`npm test`, `pytest`, `cargo check`).
  - Remember: An un-linted repository is a standing missed opportunity. Prefer building an automated check over writing a prose instruction.

## 3. Coding Standards & Review

- **Question:** Should the review agent be given an updated rule, or should a rule be clarified or removed?
- **Friction symptoms:**
  - Reviewer agent failed to catch a defect that human inspection identified.
  - Reviewer repeatedly flagged subjective or nitpicky items that lack consensus.
  - Standards documentation mixes mechanical rules with judgment calls.
- **Remediation patterns:**
  - Separate mechanical violations from judgment calls:
    - **Mechanical violations** (import order, syntax patterns, banned APIs, naming conventions) belong in automated linters or pre-commit hooks, not prose.
    - **Judgment calls** (architectural consistency, readability, design patterns) belong in `CODING_STANDARDS.md`.
  - Clarify ambiguous rules in review rubric files.

## 4. Steering Economy (`AGENTS.md` / `CLAUDE.md`)

- **Question:** Are instructions in agent steering files concise, effective, and non-redundant?
- **Friction symptoms:**
  - `AGENTS.md` or `CLAUDE.md` is overly long (>500 lines) and consumes valuable context window space.
  - Instructions contain rules that the agent naturally follows without prompting (no-ops).
  - Domain-specific details clutter the global entry file instead of using progressive disclosure.
- **Remediation patterns:**
  - Move detailed guides into `docs/` or `skills/` and leave concise pointers in `AGENTS.md`.
  - Delete instructions that do not demonstrably change agent behavior.
  - Move coding rules to `CODING_STANDARDS.md` or linter configs.

## 5. Tool Economy & Context

- **Question:** Did the agent make expensive or inefficient tool calls?
- **Friction symptoms:**
  - Reading full multi-megabyte files when a bounded slice or grep would suffice.
  - Redundant tool calls fetching the same metadata repeatedly.
  - High token consumption on routine status queries.
- **Remediation patterns:**
  - Suggest specialized CLI scripts or MCP tools for recurring queries.
  - Use offset/limit or targeted search tools.
  - Add summary indexes to large data files.

## 6. Information Access & Telemetry

- **Question:** Was critical information missing or hard to reach during the run?
- **Friction symptoms:**
  - Inability to inspect server logs, database state, or network responses.
  - Missing environment documentation or required secret keys.
  - External documentation or upstream specifications were unavailable locally.
- **Remediation patterns:**
  - Tee development server logs to inspectable log files.
  - Document local environment variables and reproduction commands.
  - Cache upstream specs or schemas in repository reference docs.
