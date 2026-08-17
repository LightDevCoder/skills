# v0.1.4 发现验证

[English record](DISCOVERY_VERIFICATION.md)

## 状态

`PASS` — 记录自已发布 tag 的安装运行，见
[INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md)。

## 结果

- 整集合安装（pinned `#v0.1.4`）：`Found 8 skills`、`Installing all 8
  skills`；`.agents/skills/` 包含 ask-light、language-learning、
  learn-anything、light-kanban-worker、manuscript-ops、project-init、recap、
  review-loop；`npx --yes skills list` 列出
  `light-kanban-worker ./.agents/skills/light-kanban-worker`。
- 单 Skill 安装（pinned `#v0.1.4 --skill light-kanban-worker`）：
  `.agents/skills/` 恰好只有 `light-kanban-worker`；`skills list` 只列出
  一个包；10 个安装文件与 tagged 源 SHA-256 逐字节一致。
- 两个 fresh destination 均不含 source checkout。
- `skills list` 输出同时包含 CLI 对其自身 `agent/skills/` 按 host 副本的
  统一 "missing required frontmatter field(s): name" 警告（见安装记录）；
  已发现的 `.agents/skills/` 包不受影响。
