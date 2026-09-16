# `project-retro` 准入证据

[English](README.md)

## 范围与状态

- 目标包：`skills/project-retro/`
- 来源：PORT 与 Light 工作流适配——基于 Matt Pocock 的 `retro`（SHA `959a8e9f1edc3adbe2f7e3054bb6fbefa6696260`，2026-09-15），适配为具备自主评估触发启发式的第一方能力；参见 [ATTRIBUTION.md](../../../../skills/project-retro/ATTRIBUTION.md)
- 调用类型：model-invoked（`allow_implicit_invocation: true`），同时支持人工手动调用（`$project-retro`）
- 准入路径：完整路径——`review-loop` `agent-skill` Profile；最终 verdict 由 `project-review` 拥有
- 准入状态：`PASS`（第 01 轮；0 缺陷）
- 版本边界：纳入 `v0.2.1` 发布线

## 证据概要

| 维度 | 结果 | 证据边界 |
| --- | --- | --- |
| 归属 (Attribution) | PASS | `ATTRIBUTION.md` 完整记录上游仓库（`mattpocock/skills`）、原始路径（`skills/in-progress/retro`）、锁定提交（`959a8e9f1edc3adbe2f7e3054bb6fbefa6696260`）、MIT 许可说明及精准变换摘要。 |
| 结构 (Structure) | PASS | 精简的 `SKILL.md`、`agents/openai.yaml`、渐进展开支持文档（`references/categories.md`、`references/heuristics.md`、`references/template.md`）及完整的自动化测试。所有链接正常解析，无占位符。 |
| 独立安装 (Fresh-copy) | PASS | 包具备完全自包含性，运行时不依赖 `mattpocock/skills`。隔离环境拷贝可正常被发现与验证。 |
| 行为 (Behavior) | PASS | 单元与契约测试全部通过：验证了自主评估启发式逻辑（顺畅流程跳过复盘；高/中度摩擦触发复盘）、严重性排序、改进分类与报告模板契约。 |
| 调用类型 (Invocation) | PASS | 声明为 model-invoked（`allow_implicit_invocation: true`）；`SKILL.md` 与 `agents/openai.yaml` 保持一致。 |
| 集合质量 (Quality) | PASS | 包含 36 个第一方包的集合契约、发现测试与路由测试全部通过。 |

## 审查记录

- Charter：[review-loop/charter.md](review-loop/charter.md)
- State：[review-loop/state.md](review-loop/state.md)
- Producer evidence：[review-loop/rounds/round-01/producer-evidence.md](review-loop/rounds/round-01/producer-evidence.md)
- Findings：[review-loop/findings.md](review-loop/findings.md)（0 个缺陷）
- Independent evaluator verdict：[review-loop/rounds/round-01/evaluator-verdict.md](review-loop/rounds/round-01/evaluator-verdict.md)
- Final verdict (project-review)：[review-loop/verdict.md](review-loop/verdict.md)
