# LightDevCoder/skills v0.2.7 Release Manifest

[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md)

**Preparation status:** Local candidate; independent acceptance is BLOCKED by missing required Host observations, so the lifecycle has not reached PREPARED. v0.2.6 remains stable. This draft records no future verification result.

This document will be frozen in the candidate snapshot. Post-publication facts belong in a receipt first created on `main` during ATTESTED; no receipt belongs in this candidate or its tag snapshot.

| Field | Value |
| --- | --- |
| **Release Version** | `v0.2.7` (owner-confirmed target; unpublished) |
| **Expected Tag** | `refs/tags/v0.2.7` |
| **Release Identity** | `refs/tags/v0.2.7^{commit}` |
| **Release Scope** | Twelve Light Skill names; package identity and UI labels; internal references and ask-light routing/state/discovery; migration, attribution, bilingual current/release documentation, and focused verification. |
| **Collection Package Count** | 36 admitted packages; 12 renamed, other 24 names retained |
| **Policy Status** | `PROVISIONAL` (unchanged Jev policy) |
| **Tag Immutability** | Annotated tag permanently immutable after publication |
| **Implementation Input** | Namespace SPEC Revision 3, local `.scratch/light-skill-namespace/spec-revision-3.md`; SHA-256 `f64a5f266015961b362812b24148557aca57371ba6a6dc4b8bacb680e51b2ed4` |
| **Current Base** | `origin/main` at `97adf5f319b8800b6635057434dcb4aeda2ddecd` |
| **Previous Stable Snapshot** | `v0.2.6` at `38015048f69f988eb2fc57dca66e65c252c2b4e4` |
| **Compatibility Baseline** | Responsibilities, invocation permissions, categories, released travel handbook/AI behavior and historical evidence retained; no installable old-name aliases or automatic user-global migration. |

## Candidate evidence

Merged local checks pass 534 pytest tests, 158 unittest tests, compilation and public documentation checks. All 224 baseline travel/history files are preserved. [Producer evidence](../../namespace-v0.2.7/producer-evidence.md) records these bounded observations. A1–A10 verification, R1–R5 diagnostic coverage, independent review-loop convergence and project-review final acceptance must be completed against the new frozen candidate. Candidate CI, A2/A9 real Host selector/invocation observations, and actual release-source fresh installation are pending. Static discovery or Producer checks do not establish Host runtime or independent acceptance.

## Subsequent release gates

Exact-candidate CI, active tag protection/preflight, annotated tag identity, fixed-tag and default-branch fresh installation, complete package/source/content checks, GitHub Release publication, and post-publication attestation remain pending. The earlier v0.2.6 namespace attempt remains historical; the owner confirmed v0.2.7 and its new base. Actual user-global migration is a separately authorized operation.

[Final candidate acceptance](../../namespace-v0.2.7/acceptance.md): BLOCKED; no publication facts recorded.
