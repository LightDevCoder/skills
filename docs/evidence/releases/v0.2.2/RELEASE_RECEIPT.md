# LightDevCoder/skills v0.2.2 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `CANDIDATE` — Release candidate prepared; tag creation, public release push, and remote verification pending Phase 2 publication gate and human confirmation.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` (public) |
| Release | `v0.2.2` |
| Release commit | Candidate commit (to be tagged `v0.2.2`) |
| Release tag | `v0.2.2` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.2.2 |
| Scope | Release 36 first-party Skills across 7 purpose-based categories; TypeSafe Jev System One semantic acceleration stabilization across `ask-light`, `agent-config`, and `project-init`; official Skills CLI canonical mappings and scopes; provisional asymmetric downgrade guard; immutable release boundary. |
| Collection package count | 36 admitted packages |
| Working-tree status | `CLEAN` |
| Policy status | `PROVISIONAL` |
| Tag immutability | Declared permanently immutable upon publication |

## What changed

- **Release Boundary & Tag Immutability:** Established an immutable release snapshot. Published release tags are permanently immutable: never force-moved, retargeted, or rewritten. Any post-release maintenance requires either a documented metadata correction that does not move the tag or a new patch release.
- **Release Integrity Guard & Retrospective Evolution:** Added automated preflight check `scripts/verify_release_integrity.py` enforcing tag immutability (idempotent pass on matching target, hard fail on retargeting), receipt metadata consistency, and git cleanliness. Upgraded `project-retro` into a workflow-aware retrospective skill with tri-state status deduplication (`CLOSED` / `PARTIAL` / `OPEN`) and value-judgment heuristics. Documented official Skills CLI conventions in `skills_cli_conventions.md`, established two-layer companion testing architecture (hermetic snapshots + drift detection), and cleaned stale steering pointers.
- **`ask-light` Semantic Routing & Query Planning:** Finalized architecture where Python evidence engine retains deterministic workflow authority; Jev queries are executed only when an active consumer exists (Choice for multiple legal candidates; Noul for material ambiguity and reasoning escalation). Jev never grants workflow transition authority; execution intent queries have been removed. Zero-value queries are skipped.
- **`project-init` Canonical Skills CLI Integration:** Integrated official `vercel-labs/skills` v1.7.0 CLI agent mappings (`pi`, `claude-code`, `cursor`, `codex`, `antigravity`, `grok`, `hermes-agent`) and canonical project scopes (`.agents/skills` for Cursor, Codex, Antigravity). Unsupported targets (such as DSH) fail closed deterministically. Added optional TypeSafe Jev ecosystem onboarding (`--jev` / `--no-jev`), safe credential resolution (`os.environ` then project `.env`), `.gitignore` credential protection before local writing, and global skill reuse.
- **`agent-config` Abstract Task Profiling & Provisional Downgrade Guard:** Abstract task profiling (routine, standard, high) and reasoning needs (low, medium, high) without vendor model coupling. Label-clean evaluation with code-owned authoritative inputs. Enforced provisional asymmetric downgrade policy requiring confidence >= 0.75 and boundary margin >= 0.15 before reducing model capability below baseline (`Policy status: PROVISIONAL`).
- **Live Evaluation Evidence (AC-02):** Candidate downgrade from baseline standard to routine was safely rejected due to marginal confidence (0.59 < 0.75) and boundary proximity (score 0.41), correctly retaining standard baseline tier (`claude-3-5-sonnet`).
- **Category Reorganization:** Grouped all 36 admitted Skills into seven purpose-based categories under `skills/` (`project`, `thinking`, `engineering`, `review`, `knowledge`, `writing`, `productivity`) while preserving flat host installations and official CLI compatibility.

## Verification Checklist

| Gate | Status | Evidence |
| --- | --- | --- |
| Local Test Suite | `PASS` | 409 passed (408 passed, 1 skip: `test_layer1_deterministic_schemas_via_companion_ajv` without external companion repo); 39 unittest (271 assertions); compileall clean; git diff --check clean |
| Jev Evaluation Evidence | `PASS` | AC-02 score: 0.41, confidence: 0.59, final tier: standard (`Policy status: PROVISIONAL`) |
| Phase 2 Human Approval Gate | `PENDING` | Local commits only; waiting for human confirmation before remote publication |
| GitHub Actions CI (`collection-quality`) | `PENDING` | Pending remote push to main |
| Pinned Whole Collection Fresh Install | `PENDING` | `npx skills add LightDevCoder/skills#v0.2.2 -y` |
| Generic Latest Whole Collection Fresh Install | `PENDING` | `npx skills add LightDevCoder/skills -y` |
| Discovery Verification | `PASS` | All 36 package frontmatters and contracts discovered |

## Provenance Note

Release `v0.2.1` was originally published on 2026-09-16 against commit `70a48ef` (receipt recorded `cb17b17c8227b7d7211e4bf5b72223703d987d60`). Its tag was subsequently repointed during the Jev integration stabilization cycle (`6f9d173`, then `27f16e4`). Release `v0.2.2` establishes the new immutable release boundary.
