# v0.1.2 限制说明

[English limitations](LIMITATIONS.md)

- `PASS`：使用 CLI `1.5.22` 对 tag `v0.1.2` 与通用 `latest` 命令执行了 fresh
  public 整仓与单包安装；host refresh 仍因 host 而异。见
  [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md)。
- `BLOCKED`：`recap` 与 `language-learning` 各自带有 fresh independent
  prompt-only fast-track Evaluator `PASS`，见[各自准入证据](../../admissions/)。原有五个包仍缺 fresh independent evaluator record，因此它们的
  `review-loop agent-skill` 验收行仍为 `BLOCKED`。
- `PASS`：GitHub Actions `collection-quality` 在合并的 release commit
  `8de5ec1a453b0e93f71dcda160e17ea7b42c3997` 上通过。
- host-specific Skill destination 与 discovery refresh 行为因 host 而异；公开
  记录不得发布私有路径或凭据。
- Direct upstream 与私有第三方包依赖可用性；本第一方仓库不复制也不 vend 它们。
