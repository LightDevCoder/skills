# Quick Start 示例

[English version](README.md)

这个小示例展示第一方集合的显式选择边界。它是文档 fixture，不是 workflow，也不是已经执行过命令的证明。

## 1. 安装

下列命令安装已发布的 v0.1.1。示例输出仍然只展示选择边界；安装不会授权自动串联。

```text
npx skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex
```

刷新 Agent host，并在脱离 source checkout 的情况下确认 discovery。只安装一个包时，例如：

```text
npx skills add LightDevCoder/skills#v0.1.1 --skill ask-light
```

## 2. 查看示例

阅读 [brief.md](brief.md) 和 [AGENTS.md](AGENTS.md)。它们只提供足够让 Agent 选择入口的上下文，不授权写业务代码，也不会静默串联 Skill。

## 3. 显式调用

```text
$ask-light next
$project-init
$review-loop init using brief.md
```

只选择与当前状态匹配的命令。预期结果是可检查的建议、最小初始化报告或 review Charter/state。下面是 Illustrative output / 示意输出，不代表本仓库已经运行：

```text
Status: RECOMMEND
Execution: recommendation only; nothing was invoked, installed, or orchestrated
```

## 4. 停止并 handoff

`$ask-light` 后停止并等待用户选择；`$project-init` 后在 discovery/specification/implementation/final review 前停止；`$review-loop` 后在持久化的 `PASS`、`FAIL` 或 `BLOCKED` verdict 停止。stop after each handoff / 每个 handoff 后停止。更长的组合见 [workflow recipes](../../docs/zh-CN/workflows/recipes.md)，真实 release 验证见 [fresh-install evidence](../../docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md)。
