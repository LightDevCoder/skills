# Validated Composition Examples

[中文示例](../../docs/zh-CN/workflows/README.md)

This directory explains repository-level Skill composition. Each document shows `entry → handoff → stop → optional` for a group; it does not copy any Skill's internal workflow. `SKILL.md` remains the behavior authority.

## Composition documents (SPEC §20)

- [Project Workflow](project-workflow.md) — `project-init → project-clarify → project-spec → project-tickets → implement → project-review → release-workflow`
- [Clarification System](clarification-system.md) — `socratic` engine with `clarify` / `project-clarify` / `decision-map` + `research` / `prototype` / `to-questionnaire`
- [Execution](execution.md) — `implement` + `agent-config` + `tdd` / `diagnosing-bugs` / `resolving-merge-conflicts`
- [Review System](review-system.md) — `review-loop` (engine) + `generic-review` / `code-review` + `project-review` (acceptance owner)
- [Specialized Workflows](specialized-workflows.md) — `manuscript-ops` / `kb-init` / `learn-anything` / `language-learning` / `kanban-worker` / `recap` / `eli5` / `release-workflow`

## Legacy examples (preserved)

- [Ask Light to explicit next-step selection](first-party-composition.md)
- [Workflow recipes](recipes.md)

Legacy examples are preserved for reference but now describe **first-party** composition; the Skills they name are included in this repository (see [CATALOG.md](../../CATALOG.md)). Approved Matt PORTs are self-contained with `ATTRIBUTION.md` and require no runtime install of `mattpocock/skills`.

These documents are validation assets. They never determine whether a Skill is admissible, must not become a predefined canonical workflow, and must not automatically invoke another user-invoked Skill.
