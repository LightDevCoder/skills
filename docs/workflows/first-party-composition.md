# Ask Light to explicit next-step selection

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
- $manuscript-ops when manuscript scope, state, formats, or review gates need
  domain routing; or
- $review-loop when the target and acceptance source are already frozen.

ask-light stops after its recommendation. It does not execute, install,
delegate, create workflow state, or silently chain another user-invoked Skill.
The selected Skill keeps its own contract and evidence boundary.

## Evidence and status

- Package contracts: the five skills/*/SKILL.md files.
- Discovery contract: [ask-light discovery contract](../../skills/ask-light/references/discovery-contract.md).
- Executable discovery check:
  [collection-discovery-tests.ps1](../../tests/collection-discovery-tests.ps1).
- Package admission evidence: the controller's T13-A acceptance record.

This is a validation asset, not a canonical workflow or an admission
requirement. Fresh installation and cross-package runtime interaction evidence
are explicitly reserved for T14.
