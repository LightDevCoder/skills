[English README](README.md)

![LightDevCoder/skills — 可组合的 Agent 工作流](skills/docs/assets/skills-header.png)

# Personal Skills Collection

`LightDevCoder/skills` 是公开的第一方 Agent Skills 集合；当前分支包含七个可以独立安装、独立发现、明确声明调用边界的 Skill。包内 `SKILL.md` 仍是行为权威；本 README 与用户指南负责说明使用方式。

> **简介：** Personal Skills Collection — Drive your creativity

> **发布：** [v0.1.1](https://github.com/LightDevCoder/skills/releases/tag/v0.1.1)
> 已从 commit `c50f1ef` 发布。发布记录和 fresh-install 证据见
> [docs/evidence/releases/v0.1.1/](docs/evidence/releases/v0.1.1/)。
>
> **发布状态：** 集合已发布且可使用。五个第一方 Skill 的安装与
> `collection-quality` 检查均已通过。当前剩余的发布验收限制是
> `review-loop agent-skill` 的独立 evaluator 证据：由于尚未附上 fresh
> independent evaluator record，该项仍为 `BLOCKED`。这不影响安装或一般使用；
> 详细边界见[发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)
> 和[限制说明](docs/evidence/releases/v0.1.1/LIMITATIONS.zh-CN.md)。
>
> **当前分支准入：** `recap` 已通过本变更的低风险纯提示型快速通道，但尚未发布；
> `language-learning` 的纯提示型快速通道证据已为本分支准备好。两者均未发布；
> 稳定 v0.1.1 仍是原来的五个包。

## Quick Start

安装已发布的第一方集合：

```text
npx skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex
```

安装同一已发布版本下的一个 Skill：

```text
npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex
```

刷新 Agent host，然后在其 Skill catalog 中确认发现结果。若 host 提供文件系统，检查已安装包的 `SKILL.md` 与 `agents/openai.yaml`；脱离 source checkout 后仍能发现，才是有意义的验证。CLI 版本、destination 和结果见 [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。

第一次不知道下一步时，推荐显式调用 `$ask-light`：

```text
$ask-light next
```

四个最短示例：

```text
$ask-light next       # 推荐下一 Skill，不执行
$project-init         # 初始化已确认的最小项目 preset
$recap                # 用一行总结当前 session
$review-loop init     # 冻结已有验收标准的 baseline
```

`ask-light` 只返回建议或一个有边界的 recipe，然后停止；不会执行、安装或自动串联。阅读 [Quick Start](examples/quick-start/README.zh-CN.md)、[Skill 使用指南](docs/zh-CN/skills/)、[工作流 recipes](docs/zh-CN/workflows/) 了解输入、输出、handoff 和停止点。

## 外部能力（External Capabilities）

当前分支包含七个第一方包：v0.1.1 的五个包，新准入但尚未发布的 `recap`，以及已提议、尚未发布的 `language-learning`。

以下是可选的 workflow 能力，来自外部或第三方来源，不属于默认集合：

- `grill-me` / `grilling`：`grill-me` 是一次会话澄清访谈的用户入口，会启动底层的 model-invoked `grilling` 能力。应把它们视为同一个能力，不要当成两个重复的工作流步骤。
- `research`：本地 preset 不足时，用于调查外部事实或实践。
- `to-spec`：把已确认的目标和约束整理成可追踪的 specification。
- `to-tickets`：把已批准的 specification 整理成按依赖排序的 tickets。
- `implement`：执行一个有边界且未被阻塞的 implementation ticket。
- `code-review`：为固定变更提供 specialist findings。
- `handoff`：为 closeout 或后续 resume 保存已接受结果或 blocker。

这些能力可能来自 `mattpocock/skills` 或其他外部来源。本仓库不复制这些 Skill，
也不会自动安装；选择包含它们的 workflow 前，请先确认当前 host 能看到对应能力。

## 第一方目录

| Skill | 作用 | 调用方式 | 包路径 |
| --- | --- | --- | --- |
| [review-loop](skills/review-loop/SKILL.md) | 执行有边界的证据、修复和最终验收循环。 | Model-invoked；支持手动入口。 | skills/review-loop/ |
| [project-init](skills/project-init/SKILL.md) | 从最小 preset 初始化已确认的软件、文稿、研究、知识、数据或 Skill-development 项目。 | 仅 user-invoked。 | skills/project-init/ |
| [ask-light](skills/ask-light/SKILL.md) | 检查 host 并推荐一个下一 Skill 或 bounded recipe，不执行建议。 | 仅 user-invoked。 | skills/ask-light/ |
| [language-learning](skills/language-learning/SKILL.md) | 通过六种学习模式辅导任意目标语言：课程、卡片、对话、语法、测验与沉浸。 | 仅 user-invoked。 | skills/language-learning/ |
| [recap](skills/recap/SKILL.md) | 用严格一行总结当前 Agent session，不改变历史也不继续任务。 | 仅 user-invoked。 | skills/recap/ |
| [learn-anything](skills/learn-anything/SKILL.md) | 从有足够证据的资料中提炼可复用 Agent Skill 方法。 | 仅 user-invoked。 | skills/learn-anything/ |
| [manuscript-ops](skills/manuscript-ops/SKILL.md) | 治理跨格式、批次、审查和 handoff 的可复现文稿工程。 | Model-invoked；支持手动入口。 | skills/manuscript-ops/ |

完整目录见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)。组合示例是文档和验证资产，不是固定 pipeline，也不是自动编排器；退休的 `project-workflow` 不会重新引入。

## 所有权与上游边界

| 来源状态 | 权威 | 本仓库处理方式 |
| --- | --- | --- |
| First-party | 本仓库及其包契约 | 放在 `skills/` 下。 |
| Direct upstream | 原始上游仓库 | 直接安装，不复制未修改 Skill。 |
| Modified third-party | 私有 `LightDevCoder/skills-3rdParty` | 保存 provenance、patch、license、sync lock 和安装证据。 |
| Deprecated / archived | 已发布迁移记录 | 保留历史并指向当前权威来源。 |

未纳入第一方集合的 Matt Pocock Skills 仍在
[mattpocock/skills](https://github.com/mattpocock/skills)。指定的私有第三方快照独立维护于 [LightDevCoder/skills-3rdParty](https://github.com/LightDevCoder/skills-3rdParty)，不会复制到本公开仓库。

## 治理与证据

- [维护契约](AGENTS.md)
- [Skill 准入](docs/SKILL_ADMISSION.zh-CN.md)
- [维护与同步](docs/MAINTENANCE.zh-CN.md)
- [安装与 fresh-install 验证](docs/INSTALLATION.zh-CN.md)
- [审查策略](docs/REVIEW_POLICY.zh-CN.md)
- [目录](CATALOG.zh-CN.md)
- [变更记录](CHANGELOG.zh-CN.md)
- [发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)
- [recap 准入证据](docs/evidence/admissions/recap/README.zh-CN.md)
- [language-learning 准入证据](docs/evidence/admissions/language-learning/README.zh-CN.md)
