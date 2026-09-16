# v0.2.1 — 改进的工作流、Agent-Config 重构与 Light-TravelPage

[English Notes](RELEASE_NOTES.md) · [发布收据](RELEASE_RECEIPT.zh-CN.md)

## v0.2.1 更新亮点

Light Skills v0.2.1 带来包含 36 个已准入第一方 Skill 的完整能力集合，重点推出工作流终点自主复盘机制（`project-retro`）、支持 10 大原生宿主的 `agent-config` Profile 驱动重构，以及新加入集合的 `light-travelpage`。

### 1. 改进的工作流与自主复盘（`project-retro`）
- **工作流终点自主评估：** 在 `project-review` 完成最终验收或 `release-workflow` 执行完成后，Agent 自主判断是否需要触发复盘：
  - 导航困难或未索引的隐式依赖。
  - 自动化检查缺失（可通过 linter、类型检查或 pre-commit 钩子避免的错误）。
  - 审查疏漏或在规范中写死机械检查规则。
  - `AGENTS.md` / `CLAUDE.md` 引导膨胀或包含无效指令（no-ops）。
  - 工具开销大或 token 冗余读取。
  - 关键运行日志与信息缺失。
- **无感与低干扰：** 若整个执行过程顺畅无阻，Agent 干净跳过复盘，不引入任何多余交互与 token 开销；若检测到摩擦，则输出按严重性排序的具体建议。
- **移植自 Matt Pocock `retro`：** 适配为第一方 model-invoked 能力，完整保留归属与 MIT 声明，提炼六大改进维度。

### 2. `agent-config` 架构重构与 Companion MCP
- **Profile 权威驱动：** 彻底摒弃名称猜智商与启发式打分（`routing_rank`），档位与推理 effort 授权完全基于用户确认的 Profile 与宿主真实能力证据。
- **10 大原生 Harness 支持：** 原生适配 Codex、Claude Code、Antigravity（`agy`）、DeepSeek Harness（`DSH`）、OpenCode、ZCode、Cursor、Grok Build、Hermes、Pi（需安装 MCP 扩展），并提供通用 plan-only 回退。
- **Companion MCP 运行时：** 集成独立的伴侣 MCP 服务（`LightDevCoder/agent-config`），提供 8 个标准工具、健康探针（`agent-config setup --check`）与安全 preview-before-apply 机制。
- **标准契约流转：** 标准化输出 `AgentConfigResult`，与下游 `implement` 及 `ask-light` 严密串联。

### 3. 新加入集合的 `light-travelpage`
- **移动优先旅行展示页：** 生成并维护交互式、自适应旅行行程与费用账本。
- **丰富视觉元素：** 中英文双语切换、航班/酒店卡片、优雅衬线版式、锚定导航菜单与 10 种地形模版的路线地图构建器。
- **协作后端：** 离线优先架构，打通 Cloudflare Pages、Functions 与 D1 数据库多端同步。

### 4. 阶段自主权与完成边界收敛
- 明确了 `tdd`、`clarify`、`implement`、`review-loop` 及 `manuscript-ops` 中的授权复用与局部阶段完成边界，避免由于过度请示导致工作流非预期中断。

## 安装指南

```bash
# 推荐从最新 main 进行交互式安装：
npx skills add LightDevCoder/skills

# 锁定 v0.2.1 稳定版本：
npx skills add LightDevCoder/skills#v0.2.1

# 按需安装单包：
npx skills add LightDevCoder/skills --skill project-retro
npx skills add LightDevCoder/skills --skill agent-config
npx skills add LightDevCoder/skills --skill light-travelpage
```
