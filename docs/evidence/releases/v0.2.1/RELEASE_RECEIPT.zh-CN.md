# LightDevCoder/skills v0.2.1 发布收据

[English Receipt](RELEASE_RECEIPT.md)

状态：`RELEASED` — 标签已发布（`v0.2.1`），GitHub Release 已发布，CI 在候选 commit 上通过，且 36 个包在全新环境下安装验证全部通过。

## 标识信息

| 字段 | 值 |
| --- | --- |
| 仓库 | `LightDevCoder/skills`（公开） |
| 发布版本 | `v0.2.1` |
| 发布 commit | `cb17b17c8227b7d7211e4bf5b72223703d987d60` |
| 发布标签 | `v0.2.1` |
| 发布链接 | https://github.com/LightDevCoder/skills/releases/tag/v0.2.1 |
| 范围 | 发布 36 个第一方 Skill，包含工作流复盘集成（`project-retro`）、支持 10 种原生 Harness 的 `agent-config` 架构重构，以及新准入的 `light-travelpage`。 |

## 变更摘要

- **工作流改进（`project-retro`）：** 在项目工作流终点引入 model-invoked 复盘自主评估。Agent 独立检测执行摩擦（导航瓶颈、缺失自动化守护线、引导指令膨胀、工具效率低下），提出针对性环境改进建议，而在顺畅无摩擦时干净跳过。
- **`agent-config` 重构与 Companion MCP：** 彻底重构为 Profile 驱动的执行配置器，原生覆盖 10 大主流编码 Agent Harness（Codex、Claude Code、Antigravity、DeepSeek Harness、OpenCode、ZCode、Cursor、Grok Build、Hermes、Pi [需 MCP 扩展]）及通用回退。用真实宿主证据与用户确认 Profile 替代名称推断；引入 Companion MCP 运行时与健康检查语义（`agent-config setup --check`）。
- **新准入 `light-travelpage`：** 作为第 35 个包准入，提供双语旅行页面、机票住宿卡片、区域地图生成器、离线优先账本及 Cloudflare Pages/Functions/D1 协同同步。
- **自主权与完成边界：** 澄清了 `tdd`、`clarify`、`implement`、`review-loop` 与 `manuscript-ops` 中的授权复用与阶段局部完成边界。
- **集合扩充：** 集合由 v0.2.0 阶段的 34 个包扩充为 36 个已准入第一方包。

## 发布验证清单

| 关卡 | 状态 | 证据 |
| --- | --- | --- |
| 本地候选测试套件 | `PASS` | 316 pytest，28 unittest（266 断言），compileall 正常，git diff --check 正常 |
| Phase 2 人工确认关卡 | `PASS` | 显式发布指令已确认 |
| GitHub Actions CI (`collection-quality`) | `PASS` | main 分支发布前验证通过 |
| 锁定版本整集合全新安装 | `PASS` | `npx skills add LightDevCoder/skills#v0.2.1` 安装 36 个包 |
| 通用最新整集合全新安装 | `PASS` | `npx skills add LightDevCoder/skills` 安装 36 个包 |
| 发现验证 | `PASS` | `npx --yes skills list` 成功发现全部 36 个已安装包 |
