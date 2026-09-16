# Categorized collection maintenance — 2026-09-16

## Acceptance scope

User requested Matt-style category directories containing Skill collections,
with an explanation in each category. Baseline: `70a48ef` (36 packages including
project-retro). Preserve all current package names, invocation modes, behavior,
approval gates, historical evidence, and release tags. Update current source
references, discovery, installation guidance, and CI. Main-only publication.

## Layout

- project: 8 packages
- engineering: 5 packages
- review: 4 packages
- thinking: 5 packages
- knowledge: 5 packages
- writing: 3 packages
- productivity: 6 packages

Each category has English and Chinese guides, purpose, invocation grouping,
package links, and navigation to the collection. Category directories are not
Skill packages. See [migration guide](../../CATEGORY_MIGRATION.md).

## Checks and limitations

- Full suite after path adaptation: 317 passed; additional category contract
  plus focused discovery/router checks: 88 passed.
- Root unittest suite: 28 passed before adding the category contract.
- Skills CLI 1.5.26 discovered all 36 packages using the categorized local source.
- Isolated local installation of all 36 packages with `--skill '*' --yes --copy
  --agent codex` succeeded. Package files and supporting resources byte-matched
  source, excluding transient Python caches and .DS_Store. Host destinations
  remain flat. This is local-source install evidence, not published-install
  or host-loading proof.
- Frozen source files retain their bytes. Historical paths are resolved through
  the name-based migration lookup only for frozen hashes and historical links;
  current documentation links must resolve directly. Pinned dependency tuples
  remain bound to their original commits and paths.
- Independent candidate review pending. Final outcomes recorded at closeout.
