# LightDevCoder/skills v0.1.4 Release Receipt

Status: `RELEASED` — tag, CI, admission, and fresh-install verification
complete.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` (public) |
| Release | `v0.1.4` |
| Release commit | `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd` |
| Release tag | `v0.1.4` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.4 |
| Scope | New first-party `light-kanban-worker` Skill (full admission path), scheduled Light-Kanban worker workflow, version/documentation synchronization cleanup, cross-platform scanner fix, installation verification |

## What changed

- New first-party, model-invoked `light-kanban-worker` Skill: each scheduled
  agent run processes at most one Light-Kanban task; owned in-progress work
  and `reviewFeedback` are checked before new claims; atomic claim with
  bounded conflict retry; workspace validation blocks with a meaningful
  reason; `complete` returns work to human confirmation; never archives /
  accepts / deletes / recycles / unblocks; no daemon, polling, or runtime
  scripts.
- Package contract and behavior suites with adversarial single-rule negative
  fixtures; wired into the collection CI.
- Admission: `review-loop agent-skill` Profile, Charter revision 1, full
  independence; three confirmed findings repaired, one rejected; fresh
  Evaluator `PASS` criterion-by-criterion. Evidence under
  [docs/evidence/admissions/light-kanban-worker/](../admissions/light-kanban-worker/README.md).
- Behavioral evidence: scenarios A–F against a real Light-Kanban server
  (fresh task, request changes rework, two-worker atomic claim, workspace
  missing block, empty queue no-mutation, offline no-mutation).
- Fixed the ask-light scanner's `Test-PathUnder` path comparison, which
  hardcoded Windows separators and made the collection-quality workflow fail
  on ubuntu-latest; behavior suite gained a negative outside-readable-path
  scenario, and the runtime-script change carries
  [code-review evidence](CODE_REVIEW.md).
- Version/documentation synchronization: v0.1.4 is the current stable
  release; v0.1.3, v0.1.2, v0.1.1, and v0.1.0 remain historical records;
  README, catalog, installation guide, maintenance baseline, discovery and
  contract tests, bilingual guides, and changelog updated for the
  eight-package collection.

## Gates

| Gate | Status |
| --- | --- |
| `light-kanban-worker` admission PASS | PASS (review-loop agent-skill, full independence) |
| Full test suite PASS | PASS locally (91 collection assertions, 19 package suites, ask-light behavior with PowerShell 7.4.6) |
| CI (`collection-quality` on main) | PASS — run `31962459531` on commit `a9cc8aa` |
| Catalog synced | PASS |
| Installation docs synced | PASS |
| Fresh installation against the published v0.1.4 tag | PASS — see [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md) |
