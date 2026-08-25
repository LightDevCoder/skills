# 第一方审查策略

[English review policy](REVIEW_POLICY.md)

本策略分配第一方 Skill 的审查角色和证据要求；静态检查、specialist finding 或 Producer 自报不能替代 final acceptance。

## Reviewer vs review-loop vs project-review

| 角色 | 是什么 | 做什么 | 绝不做 |
| --- | --- | --- | --- |
| **Reviewer**（`generic-review` · `code-review` · 领域 reviewer） | 只读 specialist；见 [Reviewer 契约](REVIEWER_CONTRACT.zh-CN.md) | 检查有界 target + requirements，返回规范化 `Findings: []` | 修复目标、指挥 Producer、改需求或签发 verdict |
| **`review-loop`** | 轻量收敛引擎 | 解析 reviewer、调用、收 findings、交回 Producer、重跑，干净或达 repair 上限时停止 | 拥有冻结 baseline 或项目最终 `PASS`/`FAIL`/`BLOCKED`（属 `project-review`） |
| **`project-review`** | 项目级最终验收拥有者 | 冻结 Charter/baseline、组合 reviewer（`generic-review`/`code-review`/领域）、经 `review-loop` 驱动收敛并签发最终 `PASS`/`FAIL`/`BLOCKED` | 替代 reviewer 方法或捏造缺失的验收标准 |

不要把最终验收塞回 `review-loop`。 reviewer 的 finding 只有经 acceptance owner 判断后才成为 verdict。

## Review triggers

以下情况适用：新 Skill 准入；改变行为/trigger/invocation/边界/依赖/资源/attribution；改变 runtime executable script/shared test infrastructure/installer；影响 discovery/installation/migration 的 rename/deprecate/remove；以及包含上述变更的 release candidate。仅文档治理改动也要做链接与 cross-reference 检查，但不能替代未来的 `project-review` 或 `review-loop agent-skill` acceptance。

## Profile 与审查

| 变更 | 必需 final acceptance | specialist evidence |
| --- | --- | --- |
| 符合条件的低风险纯提示型 Skill | 快速通道单 fresh Evaluator | structure/metadata、隔离 copy/discovery、deterministic 正负 contract tests、显式调用/non-trigger、同步 docs；无 Critic 或 `code-review`。 |
| 新增或实质改变第一方 Skill | `project-review` 或 `review-loop` 的 `agent-skill` Profile | structural、fresh-install、behavioral、invocation、attribution。 |
| 包含 executable script | `project-review`/`review-loop` + `agent-skill` | focused/negative/adversarial tests 与 `code-review` findings。 |
| Skill 内的软件 artifact | `project-review` 拥有 verdict，`review-loop` 为引擎 | `code-review` 提供 Standards/Spec findings。 |
| 文稿/specification artifact | `project-review` 选 `manuscript`/`specification` Profile | artifact-specific 证据与 specialist findings。 |
| Release candidate | 包级验收 + Program 级验收 | verified release installation 与文档同步证据。 |

`generic-review` 为无 specialist 时的默认 reviewer。`code-review` 为有界 `git diff` 的 specialist（Standards + Spec），只读。

## 证据与独立性

Producer Evidence 须写明精确命令、环境、输入输出、revision、范围与限制。 reviewer 按 [REVIEWER_CONTRACT.md](REVIEWER_CONTRACT.zh-CN.md) 的输入包（`Target`·`Requirements`·`Relevant context`·`Previous findings`）返回 `id`/`severity`/`location`/`problem`/`reason`（可选 `suggestion`），绝不直接写 `PASS`/`FAIL`/`BLOCKED`。Producer 负责修复；Evaluator 须 fresh independent。快速通道省略单独 Critic；完整路径需要 one fresh independent Evaluator with the frozen baseline and admissible evidence。

## Repair、verdict 与边界

`review-loop` 仅对已确认、范围内、可在 repair 上限内收敛的 finding 要求 Producer 做有界修复；需改需求、改架构、多张新 ticket、缺 authority/environment/evidence 或 independent review 不可用时，以 `FAIL`/`BLOCKED` 停止。

最终 verdict 由 **`project-review`**（项目/发布）或指定的包 acceptance owner（无独立项目验收时为带 `agent-skill` Profile 的 `review-loop`）签发，绝不由 reviewer 签发：

- **PASS：** 全部冻结条件与证据满足。
- **FAIL：** 范围内条件在 repair 窗口内未满足。
- **BLOCKED：** authority/environment/evidence/independent review 不可用。

仅有结构检查、keyword 匹配、模拟 fixture 或零断言测试时，不得声称 behavior/runtime proof。

## 记录与发布边界

保存冻结 source、reviewer findings、repairs、跨轮 evidence、最终 Evaluator 与 verdict；Skill 链接到准入证据，release/项目链接到受影响包记录与已验证安装证据。

Release、目录或安装命令在必需 verdict 与 checks 齐全前不得暗示已验收。

历史说明：曾嵌在 `review-loop` 中的 final-acceptance 能力（`frozen baseline`、`PASS/FAIL/BLOCKED`、`scope-change boundary`）已迁移至 `project-review`（§25 Phase 7），`review-loop` 现为轻量引擎。
