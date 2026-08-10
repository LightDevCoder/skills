# Quick Start 示例

[英文版](README.md)

这个小示例展示第一方集合的显式选择边界。它是文档 fixture，不是 workflow，也不是已经执行过命令的证明。理解本页流程不要求先阅读英文版的 `brief.md` 或 `AGENTS.md`；所需上下文已在下面说明。

本示例的上下文是：目标是准备一份有来源支持、可检查的小型文档实验 brief；唯一提供的 artifact 是 `brief.md`，当前没有实现文件；用户尚未批准 specification、ticket graph 或 final acceptance source。第一步只是在 `$ask-light` 与 `$project-init` 之间做显式选择，不授权自动串联或发布。

## 1. 安装

下列命令安装已发布的 v0.1.2。示例输出仍然只展示选择边界；安装不会授权自动串联。

```text
npx skills add LightDevCoder/skills --yes --copy --agent '*'
```

刷新 Agent host，并在脱离 source checkout 的情况下确认 discovery。只安装一个包时，例如：

```text
npx skills add LightDevCoder/skills --skill ask-light --yes --copy --agent '*'
```

## 2. 查看示例

本页已经包含选择入口所需的上下文，不需要阅读英文文件才能继续。若要核对原始 fixture，可选阅读 [brief.md](brief.md) 和 [AGENTS.md](AGENTS.md)；它们只补充同一边界，不授权写业务代码，也不会静默串联 Skill。

## 3. 显式调用

```text
$ask-light next
$project-init
$review-loop init using brief.md
```

只选择与当前状态匹配的命令。预期结果是可检查的建议、最小初始化报告或 review Charter/state。以下是 Illustrative output（示意输出），不代表本仓库已经运行：

```text
Status: RECOMMEND
Execution: recommendation only; nothing was invoked, installed, or orchestrated
```

## 4. 停止并 handoff

`$ask-light` 后停止并等待用户选择；`$project-init` 后在 discovery/specification/implementation/final review 前停止；`$review-loop` 后在持久化的 `PASS`、`FAIL` 或 `BLOCKED` verdict 停止。每个 handoff 后都要停止并保留状态。更长的组合见[工作流 recipes](../../docs/zh-CN/workflows/recipes.md)，真实 release 验证见[安装证据](../../docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)。
