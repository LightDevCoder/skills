# Release Provenance Review: TypeSafe Jev Integration Boundary

This review inspects the release history, tag targets, and release evidence inconsistencies between `v0.2.1` and subsequent TypeSafe Jev integration commits, in accordance with Section 44 of the Jev Integration Hardening SPEC and `release-workflow`.

---

## 1. Commit and Tag Identification

| Entity | Reference | Commit SHA | Date | Description |
| --- | --- | --- | --- | --- |
| **Original v0.2.1 Release** | `70a48ef` | `70a48ef4c81b9b9f40604a43f2914e5467be4269` | 2026-09-16 | `feat: admit project-retro, enhance workflow retrospective integration, and release v0.2.1` |
| **Post-Release Category Reorg** | `0ca69ff` | `0ca69ffaeb032f7e4f23d4e4af12114175581d30` | 2026-09-19 | `Organize skills into documented purpose-based categories` (Documented as "Main-only update; no new tag or release") |
| **Provenance Note** | `363e6cf` | `363e6cf2227c40de6eb44474b638e401c0e03623` | 2026-09-19 | `Preserve historical provenance and document standalone test setup` |
| **Jev Initial Integration** | `0ac1c96` | `0ac1c96b16fbb2dc720c7fb836be919771d6c606` | 2026-09-20 | `feat: integrate TypeSafe Jev System One semantic acceleration into ask-light and agent-config` |
| **Release Doc Retrofit** | `f83720d` | `f83720d7fd6ad222f5ce4f6da6c54b12b831ff56` | 2026-09-20 | `docs(release): update v0.2.1 release notes and receipt with TypeSafe Jev semantic acceleration` |
| **Jev Project-Init Feature** | `9163a34` | `9163a34bddf8d0b149522c6940447d8c766cea19` | 2026-09-20 | `feat(project-init): add optional TypeSafe Jev ecosystem onboarding and .gitignore protection` |
| **Jev Project-Init Docs** | `6f9d173` | `6f9d173e1038e3d25c44fd8a42af52a2f14406e2` | 2026-09-20 | `docs(project-init): document Jev onboarding in contract references and release evidence` |
| **Reviewed Hardening Baseline** | `a990aa4` | `a990aa471ffc700a27d8f4b00a374624a7548eeb` | 2026-09-20 | `feat(jev): harden TypeSafe Jev integration across project-init, ask-light, and agent-config` (Reviewed: CHANGES REQUIRED) |
| **Initial Reviewed Repair** | `703039e` | `703039e737eb2e16f6c932ea39fa5c0d83e61d11` | 2026-09-20 | `feat(jev): resolve human review findings with active agent targeting, canonical credentials, and query planning` (Reviewed: CHANGES REQUIRED) |
| **Final Verification Repair** | `c975647` | `c9756478f480dda422510a8368491e22292ce5b5` | 2026-09-20 | Final hermetic verification repair (host independence, boundary guard, tri-state semantic evaluation, query consumer planning) |
| **Live Calibration Baseline** | `936653c` | `936653cdadf04036d39eefec988db356943dbce0` | 2026-09-20 | `docs(evidence): update live Jev evaluation report and calibration evidence` (Reviewed: CHANGES REQUIRED due to P0 mapping and P1 label leakage) |
| **Release-Gate Repair Pass** | `3625e61` | `3625e618a49ceb8fbd4a299da709acbc6263cd81` | 2026-09-20 | Canonical Skills CLI agent ID mappings and scopes, elimination of declared_difficulty label leakage, runtime input / ground truth separation |
| **Calibration Repair Pass** | `b260bb9` | `b260bb96fcc8633abe91a236d029d9a7f40520fe` | 2026-09-20 | Asymmetric downgrade policy (PROVISIONAL) distinguishing upgrade, hold, and downgrade; evidence guard for capability reduction; calibration convergence |
| **Current Tag `v0.2.1` Target** | `v0.2.1` | `6f9d173e1038e3d25c44fd8a42af52a2f14406e2` | 2026-09-20 | Annotated tag object `318d32a602e10f452e39974010aa03abb50aff33` pointing to commit `6f9d173` |

> **Note on evidence-only cleanup revisions:** Subsequent evidence-only documentation cleanup commits (such as synchronizing report metrics or clarifying test environment splits) are intentionally not self-recorded in the table above to prevent recursive Git SHA self-reference. Their immutable identity is provided by Git commit history and will be formally recorded by the subsequent release commit and release evidence under `release-workflow`.

---

## 2. Inconsistencies Identified

1. **Retroactive Modification of Release Boundary:**
   - The release commit `70a48ef` was tagged and documented on 2026-09-16 as the boundary for `v0.2.1` (admitting `project-retro` and `light-travelpage`).
   - On 2026-09-20, after commits `0ac1c96`, `9163a34`, and `6f9d173` introduced Jev integration, the annotated tag `v0.2.1` was moved/retagged to point to `6f9d173`.
   - `docs/evidence/releases/v0.2.1/RELEASE_NOTES.md` and `RELEASE_RECEIPT.md` were edited post-hoc to claim that `v0.2.1` included TypeSafe Jev semantic acceleration.

2. **Changelog Duplication:**
   - In `CHANGELOG.md` and `CHANGELOG.zh-CN.md`, TypeSafe Jev semantic acceleration appears **both** under `## Unreleased` and under `## 0.2.1 — 2026-09-16`.
   - The entry under `0.2.1` bears a release date of 2026-09-16, even though the Jev implementation commits (`0ac1c96`, `9163a34`) occurred on 2026-09-20.

3. **Release Artifact Integrity:**
   - In strict adherence to SPEC Section 44 and 49:
     - No tags have been mutated or deleted during this hardening pass.
     - No GitHub Release has been published, overwritten, or edited.
     - Working tree edits are strictly restricted to local files under review.

---

## 3. Recommended Release Repair Procedure

Under the project's `release-workflow` guidelines:

1. **Option A (Recommended — New Minor/Patch Release):**
   - Retain the historical release boundary of `v0.2.1` at `70a48ef` (representing `project-retro` and `light-travelpage`).
   - Keep the hardened TypeSafe Jev integration under `## Unreleased` in `CHANGELOG.md`.
   - Prepare a new release (e.g. `v0.3.0` or `v0.2.2`) via `release-workflow`:
     - Cleanly record TypeSafe Jev ecosystem onboarding and semantic task profiling.
     - Create annotated tag and new release evidence under `docs/evidence/releases/<version>/`.
     - Execute fresh-install verification against the new tag.

2. **Option B (Re-tag Reconciliation):**
   - If maintainers decide `v0.2.1` was never published externally to consumers prior to commit `6f9d173`, the `## Unreleased` section of `CHANGELOG.md` should be pruned to remove the redundant Jev bullet, and the release notes must reflect the consolidated commit date.

**Action Status:**
Temporary review artifact completed. Awaiting maintainer direction prior to any tag, push, or release alteration.
