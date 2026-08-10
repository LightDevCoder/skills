# v0.1.2 limitations

[中文限制](LIMITATIONS.zh-CN.md)

- `PASS`: Fresh public whole-collection and per-Skill installation were run
  against tag `v0.1.2` and the generic `latest` command with CLI `1.5.22`; host
  refresh remains host-specific. See
  [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md).
- `BLOCKED`: `recap` and `language-learning` each carry a fresh independent
  prompt-only fast-track Evaluator `PASS` in [their admission
  evidence](../../admissions/). The original five packages still lack a fresh
  independent evaluator record, so the `review-loop agent-skill` acceptance row
  remains `BLOCKED` for them.
- `PASS`: GitHub Actions `collection-quality` passed on merged release commit
  `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`.
- Host-specific Skill destinations and discovery refresh behavior vary; the
  public record must not publish private paths or credentials.
- Direct upstream and private third-party packages are availability-dependent;
  this first-party repository does not copy or vend them.
