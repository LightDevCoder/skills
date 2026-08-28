# `project-init` 使用指南

[英文指南](../../skills/project-init.md)

行为权威是 [skills/project-init/SKILL.md](../../../skills/project-init/SKILL.md)。

## 解决什么问题

`project-init` 建立后续 Light Project Skills 真正消费的稳定仓库配置。它保留既有指令与手工备注，只创建有消费者的契约，并可安全重复运行。

## 何时使用 / 不使用

当软件、文稿、研究、知识库、数据分析或 Skill-development 项目只需要一个最小且已确认的起点时使用。不要用它做 discovery、specification、tickets、业务实现、验收或永久 workflow 管理，这些都是后续显式选择。

它是 `user-invoked only`，必须由用户选择：

```text
$project-init
```

## 前置条件、输入和输出

默认目标是当前目录。写入前读取根部指令、README、manifest、项目文档和当前状态。输入包括项目类型、目标、输出、协作、约束、相关 Skills、issue tracker、domain context locator、review profile/acceptance strategy、working area，以及由当前 host 证据确认的 instruction filename。现有 tracker adapter 只支持 `.scratch/<effort>/issues`；其他 locator 需要新增 adapter。两个 preset 都合理时，先比较影响、给出推荐并让用户选择。深度 discovery 属于 `$clarify`/`$project-clarify`/`$decision-map`。

输出包含一个 instruction pointer、`docs/agents/light-project.md`、`docs/agents/issue-tracker.md`，以及精确的 created/updated/preserved 报告；不创建 triage labels、tickets、implementation plan、final-review record 或竞争性的 specification。

事务式 bootstrap helper 依赖 Python 3.9 或更高版本；缺少该 runtime 时，在任何写入前返回 `BLOCKED`。

## 成功与 `BLOCKED`

成功要求唯一 instruction pointer 指向稳定契约、两个 managed contract 位于目标根内、三个目标解析为不同文件、手工内容被保留，重复运行只更新一个 managed block 且不复制。根目录不存在、preset 尚未选择或 fallback 缺少确认/证据时返回 `BLOCKED`。

## 组合和停止点

`ask-light` 可以推荐它。初始化后，用户可以显式选择 `project-spec`、`manuscript-ops` 或 `project-review`；本 Skill 不调用它们。初始化是停止点，不等于 discovery、specification、implementation 或 final review。

## 安装与发现验证

使用 `npx skills add LightDevCoder/skills --skill project-init` 安装，刷新 host，在脱离 source checkout 的环境确认发现结果，并运行 [tests](../../../skills/project-init/tests/)。把 host 限制记录到 release evidence。
