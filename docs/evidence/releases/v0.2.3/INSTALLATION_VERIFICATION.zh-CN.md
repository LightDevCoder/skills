# 安装验证记录 — v0.2.3

[English Version](INSTALLATION_VERIFICATION.md)

## 全新环境安装矩阵

在干净的临时隔离环境中基于官方 `skills` CLI 进行验证：

| 安装类型 | 命令 | 状态 | 验证产物 |
| --- | --- | --- | --- |
| 锁定版本全量集合 | `npx --yes skills add LightDevCoder/skills#v0.2.3 --yes --copy --agent '*'` | `PASS` | 成功安装全部 36 个包目录并比对一致。 |
| 最新主干全量集合 | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `PASS` | 从默认分支 `main` 成功安装全部 36 个包目录。 |
| 锁定单个 Skill (`project-retro`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill project-retro --yes --copy --agent '*'` | `PASS` | `skills/project-retro/` 及其正向状态驱动指令与建议动作流转逻辑。 |
| 锁定单个 Skill (`agent-config`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill agent-config --yes --copy --agent '*'` | `PASS` | `skills/agent-config/` 及其 Profile 驱动契约与抽象画像模块。 |
| 锁定单个 Skill (`ask-light`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill ask-light --yes --copy --agent '*'` | `PASS` | `skills/ask-light/` 及其有界语义查询规划与发现契约。 |
| 锁定单个 Skill (`project-init`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill project-init --yes --copy --agent '*'` | `PASS` | `skills/project-init/` 及其规范 CLI 映射与可选 Jev 接入模块。 |
