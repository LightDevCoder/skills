# v0.1.4 discovery verification

[中文记录](DISCOVERY_VERIFICATION.zh-CN.md)

## Status

`PENDING` at the time of this commit — completed after the published-tag
installation run records the discovery result without a source checkout.
See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md).

## What must hold

- `npx --yes skills list` in the fresh destination lists
  `light-kanban-worker` after the whole-collection install, and only
  `light-kanban-worker` after the per-Skill install.
- The installed package contains `SKILL.md`, `agents/openai.yaml`,
  `references/api.md`, and `tests/`, byte-identical to the tagged source.
- No source checkout is present in the destination.
