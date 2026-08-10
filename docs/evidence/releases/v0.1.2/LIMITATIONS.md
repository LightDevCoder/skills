# v0.1.2 limitations

[中文限制](LIMITATIONS.zh-CN.md)

- `NOT TESTED`: Fresh public whole-collection and per-Skill installation
  against the v0.1.2 tag and the generic `latest` command are pending; they will
  be filled in [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md).
- `VERIFIED`: The two newly admitted packages `recap` and `language-learning`
  each carry a fresh independent prompt-only fast-track Evaluator `PASS` in
  [their admission evidence](../../admissions/). The original five packages
  still lack a fresh independent evaluator record, so the `review-loop
  agent-skill` acceptance row remains `BLOCKED` for them.
- `NOT TESTED`: GitHub Actions `collection-quality` on the v0.1.2 release
  commit.
- Host-specific Skill destinations and discovery refresh behavior vary; the
  public record must not publish private paths or credentials.
- Direct upstream and private third-party packages are availability-dependent;
  this first-party repository does not copy or vend them.
