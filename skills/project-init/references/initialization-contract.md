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
contracts. Do not create tickets, workflow state, implementation code, review
verdicts, or Skill packages.

`scripts/bootstrap.py` requires Python 3.9 or newer. When the runtime is absent,
the write set is empty and the result is `BLOCKED`; there is no manual write
fallback because the script owns validation, staging, and rollback.

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
