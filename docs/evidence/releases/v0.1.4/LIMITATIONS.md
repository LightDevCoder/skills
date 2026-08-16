# v0.1.4 limitations

[中文记录](LIMITATIONS.zh-CN.md)

## Known limitations of this release

- The `light-kanban-worker` behavioral scenarios A–F ran on a single
  localhost machine against a real Light-Kanban server. Cross-machine LAN
  reachability (board reachable from another host) and the corresponding
  workspace-reachability distinction are documented as a block rule in the
  Skill contract, not live-tested.
- The worker's "never guess the agent identity" rule is instruction-level:
  enforcement depends on the executing agent following `SKILL.md`.
- Host refresh and model-mediated runtime invocation were not claimed by the
  installation verification; CLI discovery was run from fresh destinations
  without a source checkout.
- The package test suites import the collection's shared
  `tests/check_helpers.py` harness; running them against an installed copy
  requires that harness on `PYTHONPATH` (same convention as the other
  collection packages).
- Independent `review-loop agent-skill` acceptance for the original five
  packages remains `BLOCKED`; this does not block ordinary installation or
  use.
