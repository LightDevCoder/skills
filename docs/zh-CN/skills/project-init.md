# `project-init` 使用指南

[English guide](../../skills/project-init.md)

行为权威是 [skills/project-init/SKILL.md](../../../skills/project-init/SKILL.md)。

## 解决什么问题

`project-init` 检查目标目录，根据已确认的 preset 写入最小项目指导，并验证写入路径；它是初始化辅助工具，不是项目管理器。

## 何时使用 / 不使用

当软件、文稿、研究、知识库、数据分析或 Skill-development 项目只需要一个最小且已确认的起点时使用。不要用它做 discovery、specification、tickets、业务实现、验收或永久 workflow 管理，这些都是后续显式选择。

它是 `user-invoked only`，必须由用户选择：

```text
$project-init
```

## 前置条件、输入和输出

默认目标是当前目录。写入前读取根部 `AGENTS.md`/`CLAUDE.md`、README、manifest、项目文档和当前状态。输入包括项目类型、用户目标、输出物、协作方式、约束和 review level；已有 brief 能回答时不重复询问。`grilling` 只能帮助澄清问题，不能授权额外写入。

输出包括 preset 或已确认的 fallback、唯一 instruction target、变更路径、能力可用性、验证结果和后续 Skill 建议；不得创建 tickets、implementation plan、final-review record 或竞争性的 specification。

## 成功与 `BLOCKED`

成功要求只创建/更新一个 instruction target，保留旧内容，只有一个 `## Project Initialization` 段落，路径位于目标根内，重复执行保持幂等。根目录不存在、指令冲突无法安全决定、preset 有歧义、fallback 缺少确认或证据时返回 `BLOCKED`。拒绝或未确认的 fallback 不得写入。

## 组合和停止点

`ask-light` 可以推荐它。初始化后，用户可以显式选择 `to-spec`、`manuscript-ops` 或 `review-loop`；本 Skill 不调用它们。初始化是停止点，不等于 discovery、specification、implementation 或 final review。

## 安装与发现验证

对于已发布的 v0.1.1，使用 `npx skills add LightDevCoder/skills#v0.1.1 --skill project-init` 安装，刷新 host，在脱离 source checkout 的环境确认发现结果，并运行 [tests](../../../skills/project-init/tests/)。把 host 限制记录到 release evidence。
