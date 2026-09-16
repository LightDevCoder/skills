# 安装验证 — v0.2.1

[English](INSTALLATION_VERIFICATION.md)

## 全新安装矩阵

使用官方 `skills` CLI 在隔离干净环境下验证：

| 形式 | 命令 | 结果 | 验证产物 |
| --- | --- | --- | --- |
| 锁定版本整集合 | `npx --yes skills add LightDevCoder/skills#v0.2.1 --yes --copy --agent '*'` | `PASS` | 全部 36 个包目录正确安装，与发布提交 byte-identical。 |
| 通用最新整集合 | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `PASS` | 从默认分支 `main` 正确安装全部 36 个包目录。 |
| 锁定单包 (`project-retro`) | `npx --yes skills add LightDevCoder/skills#v0.2.1 --skill project-retro --yes --copy --agent '*'` | `PASS` | 安装 `skills/project-retro/`（含 `SKILL.md`、`openai.yaml` 与支持文档）。 |
| 通用单包 (`agent-config`) | `npx --yes skills add LightDevCoder/skills --skill agent-config --yes --copy --agent '*'` | `PASS` | 安装 `skills/agent-config/`（含 Profile 驱动全套契约）。 |
| 通用单包 (`light-travelpage`) | `npx --yes skills add LightDevCoder/skills --skill light-travelpage --yes --copy --agent '*'` | `PASS` | 安装 `skills/light-travelpage/`（含模版、资产与同步逻辑）。 |
