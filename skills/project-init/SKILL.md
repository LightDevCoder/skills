---
name: project-init
description: Initialize a software or non-software project from a minimal preset, preserving existing instructions and validating resulting paths and capabilities. Use only when the user explicitly invokes $project-init to set up generic, software, manuscript, Skill-development, research, knowledge-base, or data-analysis work.
---

# Project Init

`project-init` is a user-invoked initialization aid, not a project manager. It
inspects the target directory, asks a small set of questions, chooses one of the
presets in [presets.md](references/presets.md), writes the minimum useful
project guidance, validates what it wrote, and reports the result. Keep the
actual goal and acceptance source in the user's existing records; this Skill
does not create a competing specification or ticket system.

## Invocation and scope

Run this Skill only after an explicit `$project-init` request. Treat the current
directory as the target unless the user names another path. Read the target's
root instructions (`AGENTS.md`, `CLAUDE.md`), README, manifests, project
documents, and current status before proposing a write. Do not install Skills,
commit, push, publish, or modify business artifacts as part of initialization.

## Workflow

### 1. Inspect before writing

Record confirmed paths and missing evidence. Detect project artifacts (source,
docs, data, notebooks, images, presentations, issue records, and review
records) and the Skills actually available to the current agent. An unavailable
Skill is a reportable capability gap, not a reason to invent a command.

### 2. Ask lightweight project questions

Use `grilling` as a model-invoked capability when answers are not already
explicit. Ask one short question at a time and capture six answers:

1. project type;
2. user-visible goal;
3. expected outputs;
4. collaboration mode;
5. important constraints;
6. required review level.

Do not turn this into a full discovery interview. If a supplied brief already
answers a question, record it and move on.

### 3. Select a preset or prepare a fallback

Match the evidence and answers against [presets.md](references/presets.md). A
preset is a small initialization profile, not a complete workflow. If two
presets are plausible, show the distinction and ask the user to choose; do not
silently combine their write sets.

If no preset matches, use the model-invoked `research` capability to gather
high-quality, project-type-specific initialization patterns. Synthesize a
candidate plan listing every proposed path, instruction change, declared
capability, source, and validation check. The plan is advisory until the user
explicitly confirms it:

- on `reject`, write nothing and report the rejection;
- on a requested modification, revise the plan and ask for confirmation again;
- only after `confirm` may the fallback plan write.

Never write externally researched policy without this gate. A useful fallback
pattern may later be promoted by `learn-anything`, but that is outside this run.

### 4. Write the minimum initialization

Use the smallest preset write set that fits the confirmed goal. Preserve all
unrelated user rules and history. For agent instructions, apply this exact
target order:

1. update the existing root `AGENTS.md` in place;
2. otherwise update the existing root `CLAUDE.md` in place;
3. otherwise create one root `AGENTS.md` when the active environment supports it.

Do not create both files, replace `CLAUDE.md`, or append a second initialization
section. Merge or update one clearly headed `## Project Initialization` section,
retain existing content, and include only the selected preset's minimal
guidance. Create a recommended document only when no equivalent exists and the
project needs it now; report optional documents instead of creating them.
When existing instruction files disagree, preserve both files, use the
precedence above for the write, and report the conflict for the user to resolve;
do not silently delete or harmonize a user rule.

Do not create tickets, permanent workflow state machines, implementation plans,
or final-review records. Initialization can name relevant Skills for the user
to invoke later; it must not invoke another user-invoked Skill.

### 5. Validate and report

Before reporting success, validate:

- every created path exists and is inside the requested project root;
- exactly one instruction target was created or updated;
- existing instruction text remains present and there is one initialization
  section (rerunning is idempotent);
- every declared capability is installed/readable or clearly marked unavailable;
- no forbidden workflow, ticket, implementation, or review artifact was created.

Report `implemented`, `verified`, `blocked`, `not tested`, and `out of scope`
separately. Include the preset or confirmed fallback, files changed, optional
follow-ups, relevant Skills (without invoking them), missing evidence, and the
confirmation decision if research was used.

## Explicit boundaries

This Skill does not run `to-spec`, `to-tickets`, `implement`, `final review`,
`review-loop`, `ask-light`, `learn-anything`, or any other user-invoked Skill.
It does not manage tickets, perform implementation, establish acceptance, or
become a permanent project workflow manager. `grilling` and `research` above
are model-invoked capabilities permitted only for the stated questions and
confirmed fallback; they do not authorize additional writes.
