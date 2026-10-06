# LightDevCoder/skills v0.2.6 Release Manifest

[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release notes](RELEASE_NOTES.md)

This is the pre-publication candidate specification. A receipt will be created on `main` after publication. No receipt belongs in the candidate or tag snapshot.

| Field | Value |
| --- | --- |
| **Release Version** | `v0.2.6` (proposed; remote availability must be checked) |
| **Expected Tag** | `refs/tags/v0.2.6` |
| **Release Identity** | `refs/tags/v0.2.6^{commit}` |
| **Release Scope** | `light-travelpage` handbook UI, visible daily routes, place selection, undated initialization, consistent secondary surfaces, optional server-side AI, draft and retry recovery; affected bilingual collection and release documentation. |
| **Collection Package Count** | 36 admitted packages |
| **Policy Status** | `PROVISIONAL` (unchanged Jev policy) |
| **Tag Immutability** | Annotated tag permanently immutable after publication |
| **Compatibility Baseline** | Existing trip/record IDs, original materials, authored facts, shared mutation validation and scoped authentication retained; AI defaults off. |

## Candidate evidence

- Runtime basis: locally saved travel candidate `ae77154`, followed by bounded credential-validation and mouse date-strip repairs. Generation instructions and AI examples align with daily-page and to-do behavior.
- Producer tests: 80 template and 4 generator tests passed; AI-off, AI-on and undated Hokkaido builds passed. Actual desktop and 390px browser observations cover daily switching, grouped-place expansion, direct Materials navigation, content counts and a synthetic AI read-only request.
- Full collection: `python3 -m pytest -q -p no:cacheprovider` — 528 passed; `python3 -m unittest discover -s tests` — 156 passed. Compileall, public documentation checks, generated-release-body link validation and `git diff --check` passed. Compilation used a disposable Python cache directory. The candidate detection test now uses isolated version folders rather than the previous published version.
- Source acceptance: Core recorded `PASS` on reviewed implementation `d0a4b0700cc645aa9ca45bff0106a2c7badb52de`, charter `itinerary-visible-maps-2026-10-05-v2`, `agent-skill`, owner-authorized round 4 of 4. Separate Standards/Spec and a different fresh Evaluator cover the complete frozen baseline; independence is `FULL`, with no exception or open blocker. Undated full initialization, credential rejection and date-strip dragging are independently verified. The Evaluator repeated 80 template tests, 4 generator tests, 75-file clean-copy comparison and actual local discovery. Earlier rounds remain historical.
- Remote main, target-version availability and active immutable-tag protection were checked during preparation. Exact-commit CI, tagged pinned/latest installation and publication remain subsequent release-workflow gates; they will be rechecked against the final candidate. Local acceptance is not a remote publication claim.

Post-publication facts will be attested on `main` in `RELEASE_RECEIPT.md`, created only after publication.
