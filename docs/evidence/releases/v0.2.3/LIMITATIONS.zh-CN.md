# 版本局限性说明 — v0.2.3

[English Version](LIMITATIONS.md)

1. **Pi Coding Agent Harness MCP 扩展要求：** `agent-config` 中的 Pi 适配器需要安装 `@earendil-works/pi-coding-agent` MCP 扩展才能调用 companion MCP 工具。若未安装，`agent-config` 降级为会话局部的 plan-only 回退模式。
2. **Companion MCP 运行时独立性：** 可选的 companion MCP 运行时维护于独立代码库（`LightDevCoder/agent-config`）。本集合包在无 companion 环境下仍可在纯规划模式下完整运行。
3. **TravelPage 的 Cloudflare 凭据要求：** 为 `light-travelpage` 执行远端同步需要用户提供 Cloudflare API 令牌及配置好的 D1 数据库；本地预览可在离线无凭据环境下运行。
4. **TypeSafe Jev API Key 要求与政策状态：** 在 `ask-light`、`agent-config` 与 `project-init` 中使用可选的语义加速需要提供 `TYPESAFE_API_KEY` 及 `typesafe-sdk`。未配置时，所有 Skill 均自动安全回退至确定性基线，不发生功能故障或安全降级。非对称降级政策状态为 `PROVISIONAL`，待更广泛的基准校准。在无交互且未显式指定 `--jev` 的环境下，`project-init` 默认进入标准初始化。
5. **发布收据证明架构说明：** 根据 v0.2.3 发布生命周期设计，`RELEASE_MANIFEST.md` 固化于 Release Tag 快照内，而记录完整发布后事实的 `RELEASE_RECEIPT.md` 最终收据则在 Tag 发布、远端 CI 验证与 GitHub Release 创建完成后提交至 `main` 分支。
