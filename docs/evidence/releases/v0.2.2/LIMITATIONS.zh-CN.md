# 版本局限性说明 — v0.2.2

[English Record](LIMITATIONS.md)

1. **Pi Coding Agent Harness MCP 依赖：** `agent-config` 中的 Pi 适配器需要 `@earendil-works/pi-coding-agent` MCP 扩展才能与 companion MCP 工具交互。在没有该扩展的环境中，`agent-config` 自动降级为会话本地的纯规划（plan-only）Fallback 模式。
2. **Companion MCP 服务独立性：** 可选的 companion MCP 服务维护在独立仓库（`LightDevCoder/agent-config`）中。集合包在脱离 companion 的情况下能够以纯规划模式完整运行。
3. **TravelPage 的 Cloudflare 凭据需求：** 为 `light-travelpage` 运行远端数据同步需要用户提供 Cloudflare API Token 并配置 D1 数据库；本地预览可在无需任何凭据的情况下离线运行。
4. **TypeSafe Jev API Key 需求与策略状态：** `ask-light`、`agent-config` 和 `project-init` 中的可选语义加速依赖 `TYPESAFE_API_KEY` 及 `typesafe-sdk` 包。当不可用或未配置时，所有 Skill 均自动平滑降级至确定性基线，不发生功能阻塞或安全妥协。非对称降级策略当前处于 `PROVISIONAL`（暂定）状态，等待更全面的基准标定。在没有 `--jev` 参数的非交互环境中，`project-init` 安全默认采用标准初始化流程。
