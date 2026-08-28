# Migration and Repository Retirement Record — v0.2.0

[中文记录](MIGRATION_RETIREMENT.zh-CN.md)

This document records the provenance, migration history, and retirement status for standalone repositories consolidated into `LightDevCoder/skills` as part of the v0.2.0 33-Skill architecture release.

## 1. LightDevCoder/release-workflow

### Upstream and standalone history

- **Original repository:** `LightDevCoder/release-workflow` (public)
- **Final standalone HEAD:** `fc454f63b44b88779a7b607c5bea0c95f0bcfa01`
- **Migration destination:** `skills/release-workflow/` in `LightDevCoder/skills`
- **Reason for retirement:** Consolidate release governance and release execution directly into the unified first-party collection repository to ensure atomic synchronization of release gates, verification procedures, and package catalogs.

### Migration details

- **Files migrated / retained:**
  - `SKILL.md` (Release workflow contract and 4-phase governance process)
  - `references/VERIFICATION.md` (Fresh-install verification procedure and command matrix)
  - `agents/openai.yaml` (Interface and policy metadata)
- **Post-migration maintenance changes:**
  - Replaced obsolete PowerShell test references with portable Python test suites (`pytest`, `unittest`, `compileall`, `git diff --check`).
  - Extended publication gate in Phase 2 to push candidate `main` alongside the annotated tag, enabling generic latest (`npx skills add LightDevCoder/skills`) verification against the candidate commit.
  - Added atomic push preference (`git push --atomic origin main v0.2.0`) with sequential fallback.
  - Aligned CI semantics with GitHub Actions `collection-quality` (runs on push to `main`, pull requests, and manual dispatches).
- **Retirement / Deletion status:**
  - **Status:** Retired in v0.2.0.
  - **API deletion requirement:** GitHub CLI repository deletion requires the `delete_repo` OAuth scope (`gh auth refresh -h github.com -s delete_repo`).

---

## 2. LightDevCoder/ELI5

### Upstream and standalone history

- **Original upstream repository:** `DreambigOu/ELI5` (public)
- **Source revision:** `a766623b062331fdde53467001379b4ddf3acc2f`
- **Temporary migration fork:** `LightDevCoder/ELI5`
- **License:** MIT License
- **Migration destination:** `skills/eli5/` in `LightDevCoder/skills`
- **Reason for retirement:** `LightDevCoder/ELI5` served only as a temporary migration fork during collection consolidation. Maintained functionality is now integrated as `skills/eli5/` under collection governance.

### Migration details

- **Files migrated / retained:**
  - `SKILL.md` (Explain Like I Am... prompt and role matrix)
  - `ATTRIBUTION.md` (Upstream provenance, MIT license notice, source commit link)
- **Behavioral modification:** `none / MIGRATE — NO REWRITE`
- **Retirement / Deletion status:**
  - `DreambigOu/ELI5` (upstream): **UNTOUCHED / PRESERVED** (external author's upstream repository).
  - `LightDevCoder/ELI5` (temporary migration fork): Retired in v0.2.0. API deletion requires the `delete_repo` OAuth scope.
