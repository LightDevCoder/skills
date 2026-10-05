# LightDevCoder/skills v0.2.6 Release Manifest

[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md)

**Preparation status: BLOCKED draft.** The namespace candidate is unpublished; the local implementation is committed, but no release-ready candidate or PREPARED integrity result exists. v0.2.5 is this checkout’s verified release baseline. Remote v0.2.6 is already occupied; D7 prohibits overwriting it or selecting another version. See the [publication blocker](../publication-blocker.md).

This document is prepared for the immutable candidate snapshot. Post-publication facts belong in a receipt first created on `main` during ATTESTED; no receipt belongs in the candidate or tag snapshot.

| Field | Value |
| --- | --- |
| **Release Version** | `v0.2.6` |
| **Requested Tag (occupied)** | `refs/tags/v0.2.6` |
| **Requested Identity (not this candidate)** | `refs/tags/v0.2.6^{commit}` |
| **Release Scope** | Twelve Light Skill names and current references/routing/UI/discovery/attribution; bilingual migration and release documentation; existing travel PDF preview and readable map-navigation fixes; stable-check derivation and v0.2.5 post-tag documentation/attestation follow-up. |
| **Collection Package Count** | 36 admitted packages; 12 renamed, 24 names retained |
| **Policy Status** | `PROVISIONAL` (unchanged Jev policy) |
| **Tag Immutability** | Annotated tag permanently immutable after publication |
| **Implementation Input** | Local namespace SPEC Revision 2; baseline `7a98ed9574e6ffb69f533cdcbdf16a22633ef0e6` |
| **Local Verified Release Baseline** | `v0.2.5` at `ecafc2f3da3ab25a62e7a31285658fac5a50b47f` |

## Local candidate evidence

The reviewed local implementation is `79d15fd410f1295f84d9761d66c601895ff9ee31`. It passes 521 pytest and 158 unittest tests, compilation and public documentation checks. Two fresh independent review axes have no outstanding findings. Four local installation combinations preserve complete package identities/content and expected links; final Light manifest digest is `fe58ea6e7af0e7ffa4b52fc484c9b78cdbffc6e8c22cf1a28b0596779c191041`.

[Producer evidence](../producer-evidence.md), [installation and actual Host attempts](../installation-host.md), and [independent review convergence](../review-summary.md) preserve boundaries. A2 Host selector and A9 actual discovery/invocation are unobserved; [final candidate acceptance](../acceptance.md) is BLOCKED after fresh independent evaluation. R3 is blocked by an existing published version; R4/R5 have not occurred for this candidate.

## Later lifecycle gates

Exact-candidate remote CI, tag protection/preflight, annotated tag identity, remote fixed-version and default-branch fresh installs, package-content/source verification, GitHub Release publication, and post-publication attestation are pending. Preserve real evidence and limitations at the stage where each observation occurs. Real user global migration is a separate authorized operation and is outside this repository implementation.
