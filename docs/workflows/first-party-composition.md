# Ask Light to explicit next-step selection

[中文示例](../zh-CN/workflows/first-party-composition.md)

## Use case

An Agent task has a goal, artifacts, blockers, project type, task kind,
availability, and invocation-control constraints, but the next Skill is not
obvious. The user explicitly invokes ask-light to inspect the active
environment and recommend one next Skill.

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

- $project-init when the project needs confirmed initialization;
- $learn-anything when source material must be assessed for a reusable method;
- $recap when the user explicitly wants a one-line summary of the current
  session without continuing work;
- $manuscript-ops when manuscript scope, state, formats, or review gates need
  domain routing; or
- $review-loop when the target and acceptance source are already frozen.

ask-light stops after its recommendation. It does not execute, install,
delegate, create workflow state, or silently chain another user-invoked Skill.
The selected Skill keeps its own contract and evidence boundary.

## Evidence and status

- Package contracts: the six skills/*/SKILL.md files.
- Discovery contract: [ask-light discovery contract](../../skills/ask-light/references/discovery-contract.md).
- Executable discovery check:
  [collection discovery tests](../../tests/test_collection_discovery.py).
- Package admission evidence: the existing release records plus the
  [recap admission record](../evidence/admissions/recap/README.md).

This is a validation asset, not a canonical workflow or an admission
requirement. Fresh installation and cross-package runtime interaction evidence
are explicitly reserved for T14.
