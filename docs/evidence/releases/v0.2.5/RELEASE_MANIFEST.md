# LightDevCoder/skills v0.2.5 Release Manifest

[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md)

This is the immutable candidate specification. Post-publication facts belong in a receipt created on `main` only after publication; no receipt is part of this tag snapshot.

| Field | Value |
| --- | --- |
| **Release Version** | `v0.2.5` |
| **Expected Tag** | `refs/tags/v0.2.5` |
| **Release Identity** | `refs/tags/v0.2.5^{commit}` |
| **Release Scope** | Fail-closed Host/Profile and workflow routing; shared ticket numbering; manuscript initialization and dependency contract repair; normalized review findings; travel todo contract; CI and remote release verification hardening; bilingual documentation synchronization. |
| **Collection Package Count** | 36 admitted packages |
| **Policy Status** | `PROVISIONAL` (unchanged Jev policy) |
| **Tag Immutability** | Annotated tag permanently immutable after publication |

## Local candidate evidence

- Python: `python3 -m pytest -q -p no:cacheprovider` — 515 passed; `unittest discover` — 156 passed.
- Travel page: 35 Node tests, valid generated-trip validation and build passed.
- Current sibling MCP at `3c97180219ed1dfef8f80a9fd4be05f8f4f32077`: contract integration passed.
- Public documentation gate and `git diff --check`: passed.
- Remote CI, tag identity, fresh installs, and GitHub Release remain pending until their respective lifecycle stages.
