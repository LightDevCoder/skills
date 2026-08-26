# Project Init — logic reconstruction

**Real job:** Initialize a new software/non-software project from a minimal preset, with an inspect→ask→preset→write→validate flow.

**Entry:** User explicitly invokes `$project-init`.

**Core decision tree:** Inspect workspace/AGENTS/CLAUDE/manifests → determine project type and missing context → ask only decisions the preset cannot answer → select preset → write minimal project files → validate structure/handoff.

**Produces:** A new project skeleton and initialization report.

**Completion/stop:** After validation and reporting the next explicit step; does not proceed into clarification/spec/implementation/review automatically.

**Every-invocation knowledge:** Invocation boundary, inspect/ask/write/validate loop, preset pointer, stop rule.

**Conditional knowledge:** Preset details and contract in `references/initialization-contract.md` and `presets.md`.

**Duplicates:** Does not re-document `project-clarify`/`project-spec`; it only initializes structure.

**Negative constraints:** The no-auto-chain boundary is a real user-invoked boundary; other defensive wording was condensed.
