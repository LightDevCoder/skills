# v0.1.1 limitations

[中文限制](LIMITATIONS.zh-CN.md)

- `PASS`: Fresh public whole-collection and per-Skill installation were run
  against tag `v0.1.1` with CLI `1.5.20`; host refresh remains host-specific.
- `BLOCKED`: An independent `review-loop agent-skill` Evaluator record is not
  present yet; same-context inspection cannot be labeled independent.
- `PASS`: GitHub Actions `collection-quality` passed on merged release commit
  `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`.
- Host-specific Skill destinations and discovery refresh behavior vary; the
  public record must not publish private paths or credentials.
- Direct upstream and private third-party packages are availability-dependent;
  this first-party repository does not copy or vend them.
