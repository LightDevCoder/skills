# Initialization contract

This reference is loaded when writing or validating a project initialization.

## Stable bootstrap output

`docs/agents/light-project.md` is the compact source of stable project facts:

- project type, goal, outputs, and preset;
- relevant Skills;
- issue tracker kind and locator;
- domain-context locators;
- review profile and acceptance strategy;
- working area, collaboration mode, and constraints.

`docs/agents/issue-tracker.md` records the work-item location, SPEC/ticket
locators, blocking edge, statuses, and frontier rule consumed by
`decision-map`, `project-spec`, `project-tickets`, and `implement`. Do not create
`triage-labels.md`: no admitted Light workflow consumes it.

Managed markers allow reruns to update confirmed configuration while preserving
manual notes outside the block.

## Instruction-file precedence

Inspect root files and the active host before writing. Pass one explicit
`instructionFile` value: `AGENTS.md` or `CLAUDE.md`. Match an existing file
case-insensitively or create that exact host target when absent. Do not infer a
host style from an empty repository. If both styles exist, update only the
inspected host target, preserve the other file, and report the conflict.

Preserve unrelated lines and merge one `## Project Initialization` pointer to
the stable contract. A rerun updates that section instead of appending a copy.
Reject instruction symlinks that resolve to either managed contract; all three
write targets must resolve to distinct files.

## Plan and write boundary

Preset plans may proceed after the six lightweight answers. A research fallback
uses `preset: research-fallback` and must show the sources, proposed write set,
capability declarations, and checks, then stop for an explicit confirmation.
The confirmed sources, dated confirmation, and validation summary are persisted
in the stable project contract. `reject` means an empty write set;
requested changes produce a revised plan and another confirmation gate.

Writes are limited to the instruction pointer and the two stable bootstrap
contracts. When TypeSafe Jev System One onboarding is confirmed, writes may
additionally include `.gitignore` (for `.env` protection), local `.env`, and
the project-level `typesafe-ai` skill directory when absent globally. Do not
create tickets, workflow state, implementation code, or review verdicts.

`scripts/bootstrap.py` requires Python 3.9 or newer. When the runtime is absent,
the write set is empty and the result is `BLOCKED`; there is no manual write
fallback because the script owns validation, staging, and rollback.

## TypeSafe Jev ecosystem onboarding (optional)

When initializing a project, `project-init` provides an optional, non-intrusive
onboarding gate for TypeSafe Jev ecosystem integration (`typesafe-ai`):

1. **Explicit transaction phases:**
   - **Phase A (Preflight):** Validates configuration and targets.
   - **Phase B (Core project-init):** Stages and commits baseline contracts
     (`docs/agents/light-project.md`, `docs/agents/issue-tracker.md`, instruction target).
   - **Phase C (Jev onboarding):** Official skill check/installation, key detection,
     and Python SDK runtime verification.
   - **Phase D (Jev verification):** Minimal System One readiness verification.
   - **Phase E (Contract registration):** Appends `typesafe-ai` to `Relevant Skills`
     and constraints *only after* verified skill availability.
   - **Isolation invariant:** If optional Jev onboarding or verification fails, the
     core project bootstrap remains successful (`projectInit = SUCCESS`,
     `jev = INCOMPLETE/UNVERIFIED`).

2. **Interactive opt-in gate:**
   - Prompt: `"是否为此项目初始化 TypeSafe Jev？[y/N]"` (default: `No`).
   - CLI flags: `--jev` forces activation; `--no-jev` forces deactivation.
   - Safe fallback: In non-interactive environments or CI pipelines without
     explicit `--jev`, defaults safely to standard flow with zero Jev side-effects.

3. **Official TypeSafe skill installation & global reuse:**
   - Targets the explicit active Agent via `--agent-target <target>` (`pi`, `claude`, `cursor`, `codex`, `agy`, `grok-build`, `hermes`).
   - `bootstrap.py` canonical mapping is authoritative and distinguishes internal host identity from official Skills CLI `--agent` IDs.
   - If the active agent is unresolved or unsupported (e.g. DeepSeek Harness / DSH), halts Jev onboarding safely (`TARGET_UNRESOLVED`) with 0 installer calls.
   - Checks whether the official `typesafe-ai` skill is already available to the
     active Agent globally (valid `SKILL.md` with `name: typesafe-ai`). Distinguishes canonical global from legacy discoverable global reuse.
   - If present globally: reuses the official global installation directly without
     duplicating files into the project.
   - If absent globally: installs through the official installer
     (`npx skills add typesafe-ai/skills --skill typesafe-ai --agent <cli_agent> --yes`).
   - Strictly validates that the installed skill landed inside the canonical project scope of the target agent.
   - Strictly rejects and never generates fake stubs, stubs with fabricated content,
     or arbitrary local tree copies. If installation fails, reports
     `JEV_SKILL_SETUP_INCOMPLETE`.

   | Light Host Identity | Evidenced Indicators | Skills CLI Agent ID | Supported? | Canonical Project Path | Canonical Global Path |
   | --- | --- | --- | --- | --- | --- |
   | `pi` | `PI_*` env vars, `.pi/` directory | `pi` | YES | `.pi/skills` | `~/.pi/agent/skills` |
   | `claude` | `CLAUDE_CODE_ENTRY`, `CLAUDE_PROJECT_DIR`, `CLAUDE.md` | `claude-code` | YES | `.claude/skills` | `~/.claude/skills` (or `$CLAUDE_CONFIG_DIR/skills`) |
   | `cursor` | `CURSOR_AGENT`, `CURSOR_PROJECT_DIR` | `cursor` | YES | `.agents/skills` | `~/.cursor/skills` |
   | `codex` | `CODEX_AGENT`, `CODEX_DIR` | `codex` | YES | `.agents/skills` | `~/.codex/skills` (or `$CODEX_HOME/skills`) |
   | `agy` | `ANTIGRAVITY_AGENT`, `GEMINI_AGENT` | `antigravity` | YES | `.agents/skills` | `~/.gemini/antigravity/skills` |
   | `grok-build` | `GROK_AGENT`, `GROK_BUILD` | `grok` | YES | `.grok/skills` | `~/.grok/skills` (or `$GROK_HOME/skills`) |
   | `hermes` | `HERMES_AGENT` | `hermes-agent` | YES | `.hermes/skills` | `~/.hermes/skills` (or `$HERMES_HOME/skills`) |
   | `dsh` | DeepSeek Harness | None | NO | UNSUPPORTED / fail-closed (`TARGET_UNRESOLVED`). Do not call installer. |
   | Unrecognized | No evidenced host target | None | NO | Fail-closed (`TARGET_UNRESOLVED`). Do not call installer. |

4. **Environment & key detection:**
   - Auto-detects `TYPESAFE_API_KEY` from `os.environ` and local `.env`.
   - If missing, prompts the user via a non-echoing secret entry mechanism (`getpass`).
   - **Strict gitignore guarantee:** Whenever a local `.env` is created or
     updated, `.env` is strictly added to `.gitignore` *before* writing the key.
   - **Strict redaction:** Raw API keys are never printed, displayed, or
     recorded in logs/reports (`[REDACTED]`).

5. **Python runtime dependency & smoke verification:**
   - Inspects the active Python interpreter executing the Light scripts and
     verifies `typesafe_sdk` is importable (`<python> -c "import typesafe_sdk"`).
   - If unavailable and full onboarding is opted in, installs `typesafe-sdk` using
     that interpreter without installing `python-dotenv`.
   - When skill, SDK, and key are present, runs a minimal System One smoke test
     verifying authentication, basic request handling, and typed response.
     Failure reports `JEV_RUNTIME_UNVERIFIED` separately from skill installation.
   - Stack recommendations advise `pip install typesafe-sdk` (Python) or
     `npm install @typesafe/sdk` (Node.js).

## Downstream consumption

- `project-clarify`: goal, outputs, domain context, tracker locator.
- `decision-map`: tracker locator and working area.
- `project-spec`: goal, outputs, domain context, working area.
- `project-tickets`: issue tracker and working area.
- `implement`: issue tracker, domain context, and review profile.
- `project-review`: review profile and acceptance strategy.

Each consumer reads only these fields when the file exists. The Skill's own
artifact contract remains authoritative for its runtime output.

## Validation record

Check that every created path is under the target root, each path exists, the
selected instruction file retained pre-existing content, and only one
initialization section exists. Check each declared relevant capability and
classify it as `available`, `unavailable`, or `unknown`; do not silently
promote `unknown` to `available`. Record skipped checks and optional documents
explicitly.

## Capability and invocation boundary

The six lightweight questions are asked directly by this initializer; no
separate clarification Skill is required. `research` is the only model-invoked
capability allowed, and only for the confirmed fallback. The user remains in
control of `project-spec`, `project-tickets`, `implement`, `project-review`,
`ask-light`, `learn-anything`, and every other user-invoked Skill. Project-init
may recommend those names but never executes or orchestrates them.
