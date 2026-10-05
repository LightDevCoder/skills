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

- Runtime basis: locally saved travel candidate `ae77154`. The generation instructions and AI examples also align with its daily-page and to-do behavior.
- Producer tests: 77 template and 3 generator tests passed; AI-off, AI-on and undated Hokkaido builds passed. Actual desktop and 390px browser observations cover daily switching, grouped-place expansion, direct Materials navigation, content counts and a synthetic AI read-only request.
- Full collection: `python3 -m pytest -q -p no:cacheprovider` — 528 passed; `python3 -m unittest discover -s tests` — 156 passed. Compileall, public documentation checks, generated-release-body link validation and `git diff --check` passed. Compilation used a disposable Python cache directory. The candidate detection test now uses isolated version folders rather than the previous published version.
- Independent final acceptance is pending. The previous three-round review and its F-004 finding remain recorded; no fourth round has been run without owner approval.
- Remote main, version availability, tag protection, exact-commit CI, tagged fresh installation and release publication are pending. Local preparation is not a remote publication claim.

Post-publication facts will be attested on `main` in `RELEASE_RECEIPT.md`, created only after publication.
