# 第一方审查策略

[English review policy](REVIEW_POLICY.md)

本策略分配第一方 Skill 的审查角色和证据要求；静态检查、specialist finding 或 Producer 自报不能替代 final acceptance。

## Review triggers

以下情况适用：新 Skill 准入；改变行为、trigger、invocation、边界、dependency、resource 或 attribution；改变 executable script/test/installer；影响 discovery/installation/migration 的 rename/deprecate/remove；以及包含上述变更的 release candidate。仅文档治理改动也要做链接、范围和 cross-reference 检查，但不能替代 package-level `review-loop agent-skill` acceptance。

## Profile 与角色

| 变更 | 必需 final review | specialist evidence |
| --- | --- | --- |
| 新增或实质改变第一方 Skill | `review-loop` 的 `agent-skill` Profile | structural、fresh-install、behavioral、invocation、attribution。 |
| 包含 executable script | `review-loop agent-skill` | focused/negative/adversarial tests 和 `code-review`。 |
| Skill 内的软件 artifact | `review-loop` 拥有最终 verdict | `code-review` 提供 Standards/Spec findings。 |
| 文稿或 specification artifact | 适用的 manuscript/specification Profile | artifact-specific evidence 和 specialist findings。 |
| Release candidate | 包级 review 加 Program acceptance gate | verified release installation 和文档同步证据。 |

Producer 负责修复；Critic 和 Evaluator 只读。最终 evaluation 必须由拿到冻结验收源和 admissible evidence 的 fresh independent Evaluator 完成；不能用 same-context role-play 冒充独立审查。`code-review` 只提供 specialist findings，不拥有最终 verdict。

## Repair、verdict 和 release boundary

只修复已确认、范围内、能在 repair limit 内收敛的 finding。需求变化、架构决策、新 tickets、authority/environment/evidence 缺失或 independent review 不可用时停止并返回 `FAIL` 或 `BLOCKED`。

- **PASS：** 所有冻结验收条件和证据要求满足。
- **FAIL：** 范围内条件未满足且修复窗口内未解决。
- **BLOCKED：** authority、environment、evidence 或独立 review 不可用。

只有 structural、keyword、模拟 fixture 或零断言测试时，不能声称 behavior/runtime proof。release、catalog 或安装文档在必需 verdict 和 release checks 存在前，不得暗示最终接受。
