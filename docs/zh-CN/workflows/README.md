# 已验证组合示例

[英文版](../../workflows/README.md)

本目录说明仓库级 Skill 组合。每个文档只讲 `entry → handoff → stop → optional`，不复制 Skill 内部流程；`SKILL.md` 仍为行为权威。

## 组合文档（SPEC §20）

- [Project Workflow](project-workflow.md) — `project-init → project-clarify → project-spec → project-tickets → implement → project-review → release-workflow`
- [Clarification System](clarification-system.md) — `socratic` 引擎 + `clarify` / `project-clarify` / `decision-map` + `research` / `prototype` / `to-questionnaire`
- [Execution](execution.md) — `implement` + `agent-config` + `tdd` / `diagnosing-bugs` / `resolving-merge-conflicts`
- [Review System](review-system.md) — `review-loop`（引擎）+ `generic-review` / `code-review` + `project-review`（验收拥有者）
- [Specialized Workflows](specialized-workflows.md) — `manuscript-ops` / `kb-init` / `learn-anything` / `language-learning` / `kanban-worker` / `recap` / `eli5` / `release-workflow`

## 遗留示例（保留）

- [Ask Light 显式选择下一步](first-party-composition.md)
- [工作流 recipes](recipes.md)

遗留示例已更新为**第一方**组合；其中涉及的 Skill 均已包含于本仓库（见 [CATALOG.zh-CN.md](../../../CATALOG.zh-CN.md)）。已批准的 Matt PORT 为带 `ATTRIBUTION.md` 的自包含包，运行时不要求安装 `mattpocock/skills`。

这些文档仅为验证资产，不决定 Skill 是否可准入，不构成固定流水线，也不会自动串联 user-invoked Skill。
