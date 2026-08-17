# LightDevCoder/skills v0.1.5 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `RELEASED` — tag published, post-release verification recorded on
main. The tag snapshot carries the pre-release gate; this finalized record
(with post-release verification) lives on main and is linked from the GitHub
Release.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` (public) |
| Release | `v0.1.5` |
| Release commit | `a56aa9d98de0b941ee2282144bc7e756ef5e48bd` |
| Release tag | `v0.1.5` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.5 |
| Scope | `light-kanban-worker` behavior contract: same-agent non-overlapping runs, atomic-claim boundary clarification, first-registration identity (ID + name + avatar), release-evidence workflow cleanup |

## What changed

- `light-kanban-worker` now explicitly forbids overlapping scheduled runs
  with the same `LIGHT_KANBAN_AGENT_ID`: at most one invocation per agent id
  may be active, and a wake that fires while the previous run is still
  active must skip. Different agent ids may still run concurrently.
- The atomic-claim boundary is documented accurately: atomic claim protects
  two different workers claiming the same To Do task; it is not a
  concurrency lock for multiple invocations using the same agent identity.
  Concurrency control stays with the scheduler / agent runtime
  (`max concurrent runs = 1` or an equivalent skip-while-active setting);
  the worker adds no lock process, heartbeat, or lease service.
- First registration now clearly requires ID + name + avatar. A local image
  is uploaded through `POST /api/avatars` and the returned
  `/api/avatars/...` path is used for the claim. An existing agent id reuses
  the server's stored name/avatar — the avatar is required for first
  registration, not every worker wake. A new agent id without a name or
  avatar reports identity configuration missing, claims nothing, and
  mutates nothing.
- Contract and behavior suites extended with the new rules, two new
  adversarial negative fixtures, and behavior scenarios G and H (see
  [TEST_SUMMARY.md](TEST_SUMMARY.md)).
- Release-evidence workflow clarified: this receipt separates the
  pre-release gate from post-release verification so a published tag no
  longer shows unexplained `PENDING` markers.

## Pre-release gate

| Gate | Status |
| --- | --- |
| Worker contract tests PASS | PASS |
| Worker behavior tests PASS | PASS |
| Same-agent overlap rule tested (Scenario G) | PASS |
| First-registration avatar rule tested (Scenario H) | PASS |
| Scenarios A–F unchanged and passing | PASS |
| Collection tests PASS | PASS — final green run on the candidate commit after the review-loop record files were written (see [TEST_SUMMARY.md](TEST_SUMMARY.md)) |
| `review-loop agent-skill` acceptance | PASS — see [AGENT_SKILL_REVIEW.md](AGENT_SKILL_REVIEW.md) |
| Docs synchronized (README, catalog, installation, guides, changelog) | PASS |
| Changelog prepared | PASS |
| Release candidate clean (`git status` clean on the candidate commit) | PASS |

## Post-release verification

The following were confirmed after the `v0.1.5` tag existed and are recorded
in this finalized receipt on main (the tag itself contains the pre-release
gate snapshot; see the section above):

| Check | Record |
| --- | --- |
| Published tag identity and release commit | `v0.1.5` → `a56aa9d98de0b941ee2282144bc7e756ef5e48bd` |
| Fresh install from `LightDevCoder/skills#v0.1.5` | PASS — [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md) |
| Host discovery | PASS — [DISCOVERY_VERIFICATION.md](DISCOVERY_VERIFICATION.md) |
| Repeat installation | PASS (no-op overwrite) — [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md) |
| Release CI (`collection-quality`) | PASS — run `31985455493` on commit `a56aa9d` |
| GitHub Release body links to this record and the post-release receipt | Done — see the [GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.1.5) |
