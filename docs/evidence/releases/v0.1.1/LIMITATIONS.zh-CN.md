# v0.1.1 限制

[English limitations](LIMITATIONS.md)

- `PASS`：已用 CLI `1.5.20` 针对 `v0.1.1` tag 完成公开整仓和单 Skill 安装；host
  refresh 仍是 host-specific 行为。
- `BLOCKED`：尚无独立 `review-loop agent-skill` Evaluator 记录；同一上下文检查不能标为 independent。
- `PASS`：合并后的 release commit
  `c50f1ef403a5f0bfe02e75d1aeff2c237556db63` 上的 GitHub Actions
  `collection-quality` 已通过。
- 不同 host 的 Skills destination 和 refresh/discovery 行为不同；公开记录不能包含私人路径或凭据。
- Direct upstream 和 private third-party 包依赖可见性；本第一方仓库不复制或代售它们。
