# Ask Light to explicit next-step selection

[中文示例](../../docs/zh-CN/workflows/first-party-composition.md)

## Use case

An Agent task has a goal, artifacts, blockers, project type, task kind, availability, and invocation-control constraints, but the next Skill is not obvious. The user explicitly invokes `ask-light` to inspect the active environment and recommend one next Skill.

## Composition boundary

~~~
user goal and current artifacts
              |
              v
        $ask-light
              |
              v
one recommendation + host-appropriate invocation
              |
              v
user explicitly chooses the next Skill
~~~

Possible next choices include:

- `$project-init` when the project needs confirmed initialization;
- `$project-clarify` when an existing project has unresolved decisions;
- `$clarify` when a vague idea needs lightweight triage without a project;
- `$decision-map` when the effort is large, foggy, and multi-session;
- `$research` when an external fact is needed;
- `$prototype` when a design question needs a throwaway probe;
- `$project-spec` / `$project-tickets` when a SPEC or ticket graph is the next artifact;
- `$implement` when one unblocked ticket is ready;
- `$diagnosing-bugs` when something is broken/throwing/failing/slow;
- `$project-review` or `$review-loop` when the target and acceptance source are already frozen;
- `$learn-anything` when source material may contain a reusable method;
- `$recap` when the user explicitly wants a one-line session summary;
- `$manuscript-ops` when manuscript scope, state, formats, or review gates need domain routing; or
- `$release-workflow` when the project passed acceptance and is ready to publish.

`ask-light` stops after its recommendation. It does not execute, install, delegate, create workflow state, or silently chain another user-invoked Skill. The selected Skill keeps its own contract and evidence boundary.

## Evidence and status

- Package contracts: the 33 `skills/*/SKILL.md` files (see [CATALOG.md](../../CATALOG.md)).
- Discovery contract: [ask-light discovery contract](../../skills/ask-light/references/discovery-contract.md).
- Executable discovery check: [collection discovery](../../tests/test_collection_discovery.py) + [composition](../../tests/test_composition.py).
- Package admission evidence: existing release records plus specialized evidence under `docs/evidence/admissions/` and `docs/evidence/releases/`.

This is a validation asset, not a canonical workflow or an admission requirement. Fresh installation and cross-package runtime interaction evidence are explicitly reserved for the release gate.
