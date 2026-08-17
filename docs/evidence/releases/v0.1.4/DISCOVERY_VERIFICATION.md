# v0.1.4 discovery verification

[中文记录](DISCOVERY_VERIFICATION.zh-CN.md)

## Status

`PASS` — recorded from the published-tag installation runs in
[INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md).

## Results

- Whole-collection install (pinned `#v0.1.4`): `Found 8 skills`,
  `Installing all 8 skills`; `.agents/skills/` contains ask-light,
  language-learning, learn-anything, light-kanban-worker, manuscript-ops,
  project-init, recap, review-loop; `npx --yes skills list` lists
  `light-kanban-worker ./.agents/skills/light-kanban-worker`.
- Per-Skill install (pinned `#v0.1.4 --skill light-kanban-worker`):
  `.agents/skills/` contains exactly `light-kanban-worker`; `skills list`
  lists exactly one package; all 10 installed files are SHA-256
  byte-identical to the tagged source.
- Both fresh destinations contained no source checkout.
- The `skills list` output also prints the CLI's uniform
  "missing required frontmatter field(s): name" warning for the CLI's own
  `agent/skills/` per-host copies (see the installation record); the
  discovered `.agents/skills/` packages are unaffected.
