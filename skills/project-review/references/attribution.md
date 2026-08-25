# Attribution

## Internal migration

The frozen-baseline, Profile, evidence, finding-registry, stopping-rules, and
`PASS`/`FAIL`/`BLOCKED` final-acceptance protocol migrated here verbatim from
`skills/review-loop` at baseline `26110c9` (and the `review-loop` heavy
implementation at `/tmp/skills-baseline`). `review-loop` is the original
first-party author of that protocol; no external rewrite was performed. The
review-loop engine was then refactored to its lightweight 5-step convergence
loop. See [migration.md](migration.md) for the full mapping.

## External sources

This Skill's final-acceptance mechanism was independently written after
auditing these MIT licensed projects:

- [Gale0418/Codex-Mission-Center](https://github.com/Gale0418/Codex-Mission-Center),
  especially its execution gates, bounded agent packets, smoke-test evidence,
  snapshots, closeout, and advisory review gate.
- [mattpocock/skills](https://github.com/mattpocock/skills), especially
  `grill-me` as the user entry to its underlying `grilling` capability, and
  `wayfinder` for the boundary between decision discovery, planning, and
  execution.

The audited projects are credited to their respective authors under MIT. No
source text, code, visual asset, task-board implementation, or license text was
copied into this Skill. The workflow, schemas, wording, and compatibility rules
here are independently specified and adapted only at the level of general
mechanisms.
