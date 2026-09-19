# 发布局限性 — v0.2.1

[English](LIMITATIONS.md)

1. **Pi Coding Agent Harness MCP 扩展依赖：** `agent-config` 中的 Pi 适配器需要安装 `@earendil-works/pi-coding-agent` MCP 扩展才能使用 Companion MCP 工具；未安装时自动安全运行于会话局部 plan-only 模式。
2. **Companion MCP 服务独立性：** 可选的 Companion MCP 运行时独立维护于 `LightDevCoder/agent-config` 仓库；核心技能在没有伴侣服务时仍具备完整静态规划能力。
3. **TravelPage 的 Cloudflare 凭证要求：** `light-travelpage` 的远程多端同步依赖用户自备的 Cloudflare API 令牌与已配置的 D1 数据库；本地预览可在完全离线无凭证下运行。
4. **TypeSafe Jev API Key 依赖说明：** `ask-light` 与 `agent-config` 中的可选语义加速需要配置环境变量 `TYPESAFE_API_KEY` 并安装 `typesafe-sdk`。在未配置或环境不可用时，两项技能自动平滑退回确定性规则基准，功能与安全性不受影响。
