# v0.1.1 limitations

[中文限制](LIMITATIONS.zh-CN.md)

- `NOT TESTED`: Fresh public whole-collection and per-Skill installation must
  be run against the actual tagged remote release.
- `BLOCKED`: An independent `review-loop agent-skill` Evaluator record is not
  present yet; same-context inspection cannot be labeled independent.
- `NOT TESTED`: GitHub Actions status depends on the public release commit and
  runner execution.
- Host-specific Skill destinations and discovery refresh behavior vary; the
  public record must not publish private paths or credentials.
- Direct upstream and private third-party packages are availability-dependent;
  this first-party repository does not copy or vend them.

