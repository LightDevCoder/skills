# 第一方 Skill 准入契约

[English admission contract](SKILL_ADMISSION.md)

本契约适用于新包进入 `skills/` 前，以及改变行为、invocation boundary、dependency、resource 或 ownership claim 的变更。

## Reuse-before-invention 与 ownership gate

优先顺序：直接使用 upstream；在边界配置/适配；增加 local Profile 或 internal Layer；必要时 wrapper；必要的本地修改放入 `skills-3rdParty`；只有确实缺少能力时才创建新的第一方 Skill。目录美观、便利或想要本地副本不是 fork/admit 的理由。

第一方候选必须满足其一：

- 由 collection owner 编写；或
- 已实质变换为独立 owned capability，并有 `ATTRIBUTION.md` 记录原仓库、路径、pinned revision/tag、license/notice 与具体变换；或
- 为**已批准的上游 Port**—— SPEC（§14/§16）已显式授权，带 `ATTRIBUTION.md`、有 Light 特定集成（handoff/命名/解耦），且**无上游运行时依赖**。

未获 SPEC 授权的未修改 upstream/third-party 复制必须拒绝，指向原仓库安装路径。仍以第三方为主且未获授权的修改版进入 `skills-3rdParty`。

**本仓库已批准的 PORT（SPEC §14）：** `research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`——均为带 `ATTRIBUTION.md` 的自包含第一方包，运行时不要求安装 `mattpocock/skills`。Light 变更限于运行时解耦、命名与 handoff 串联，不允许实质性重设计。

> **Port ≠ 任意复制。** 架构层面的迁入授权不免除 attribution、license/notice 保留与自包含无上游运行时依赖的要求。未经 SPEC 授权的任意上游快照仍不合格。

## Admission questions

审查必须确认：independent value、明确 triggers、bounded responsibility、user/model invocation type、动态组合安全、无不可用依赖（含未安装的上游运行时）、包及其 scripts/templates/assets 完整且无 placeholder-only 目录。进入某个 canonical workflow 不是准入条件。

## 低风险纯提示型快速通道

仅同时满足以下条件才能使用快速通道：由 owner 编写且无第三方代码/资产；仅 user-invoked 且两处 metadata 均禁止 implicit invocation；输出仅 bounded text 且不能运行工具/网络/读写文件/改变状态/处理凭据/调用其他 Skill；无 runtime scripts/hooks/installers/binaries/外部服务/依赖；不改变 migration/security/privacy/licensing 等高风险行为。

仅验证静态 prompt 与 output contract 的自包含测试不算 runtime executable resource，但仍须非零断言与正负 fixtures。

快速通道要求 structure/metadata、隔离单包 copy/discovery、deterministic contract tests、显式调用与 non-trigger observations、同步 catalog/docs/changelog，以及一个 fresh independent Evaluator；不需要额外 Critic 或 `code-review`。存疑、副作用、implicit trigger、runtime executable、外部依赖、provenance 问题或 confirmed finding 质疑 eligibility 时必须升级到 `review-loop`/`project-review` 完整路径。

## 必需 evidence

| Evidence | 必须展示 | 不证明 |
| --- | --- | --- |
| Structural | 包树、metadata、内部链接与资源通过结构工具。 | runtime、fresh install 或 host discovery。 |
| Installation/discovery | fresh environment 安装并脱离 source checkout 发现。 | 除 discovery 外的行为。 |
| Behavioral | success、boundary、failure/missing-dependency 场景；快速通道可用显式调用与 non-trigger observations。 | 无 independent review 的 acceptance。 |
| Invocation | 调用类型一致，且 user-invoked 不会自动调用另一个 user-invoked。 | 未覆盖行为。 |
| Review | 完整路径为 `review-loop`（引擎）按 Profile，或项目级 `project-review`；快速通道为单 fresh Evaluator。 | 扩大冻结 scope 的权限。 |
| Attribution | owner/source/revision/notice/license/transformation 可检查；Port 需 `ATTRIBUTION.md` 且无上游运行时要求。 | 把未修改 copy 变成第一方。 |
| Executable scripts | focused、negative、adversarial/mutation tests 与 `code-review`。 | 静态 validator 覆盖全部行为。 |

所有 static、inferred、simulated、keyword-only 检查必须标注真实 evidence class，不能写成 runtime proof。

## 最终决定

仅当满足 ownership gate、全部 admission questions、所需 evidence（含准确标签）、适用的快速通道或完整 `review-loop`/`project-review` `PASS`，并完成维护文档同步，包才可进入第一方集合；`FAIL`/`BLOCKED` 必须留在集合外并写明缺口。
