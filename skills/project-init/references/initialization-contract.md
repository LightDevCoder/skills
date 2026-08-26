# Initialization contract

This reference is loaded when writing or validating a project initialization.

## Instruction-file precedence

Inspect root files case-insensitively. Select exactly one target:

1. existing `AGENTS.md`;
2. existing `CLAUDE.md` when `AGENTS.md` is absent;
3. new `AGENTS.md` only when neither exists and the host supports it.

Never replace `CLAUDE.md`, create both files, or rewrite nested instruction
files unless the user names that file. Preserve unrelated lines and merge a
single `## Project Initialization` section in place. A rerun updates the values
inside that section rather than appending another copy.
If `AGENTS.md` and `CLAUDE.md` conflict, keep both, write only to the selected
precedence target, and report the conflict instead of silently reconciling it.

## Plan and write boundary

Preset plans may proceed after the six lightweight answers. A research fallback
must show the sources, proposed write set, capability declarations, and checks,
then stop for an explicit confirmation. `reject` means an empty write set;
requested changes produce a revised plan and another confirmation gate.

Writes are limited to minimal instructions and an immediately needed project
document with no equivalent already present. Do not create tickets, workflow
state, implementation code, review verdicts, or Skill packages.

## Validation record

Check that every created path is under the target root, each path exists, the
selected instruction file retained pre-existing content, and only one
initialization section exists. Check that each named Skill has discoverable
metadata; report unavailable capabilities rather than claiming they work.
Record skipped checks and optional documents explicitly.

## Capability and invocation boundary

The six lightweight questions are asked directly by this initializer; no
separate clarification Skill is required. `research` is the only model-invoked
capability allowed, and only for the confirmed fallback. The user remains in
control of `project-spec`, `project-tickets`, `implement`, `project-review`,
`ask-light`, `learn-anything`, and every other user-invoked Skill. Project-init
may recommend those names but never executes or orchestrates them.
