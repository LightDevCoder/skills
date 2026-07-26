# v0.1.1 release receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `RELEASED WITH ACCEPTANCE LIMITATION` — the immutable tag, remote
default branch, GitHub Actions, and fresh-install evidence are verified;
independent `review-loop agent-skill` acceptance remains `BLOCKED`.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` |
| Release | `v0.1.1` |
| Release commit | `c50f1ef403a5f0bfe02e75d1aeff2c237556db63` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.1 |
| Date | `2026-07-26` |
| Scope | Five first-party packages, bilingual docs, Quick Start, workflow recipes, header, CI, and ask-light workflow mode. |

## Acceptance evidence

- Structure and discovery: [DISCOVERY_VERIFICATION.md](DISCOVERY_VERIFICATION.md)
- Package and collection tests: [TEST_SUMMARY.md](TEST_SUMMARY.md)
- Fresh install and host discovery: [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md)
- Limitations and evidence labels: [LIMITATIONS.md](LIMITATIONS.md)
- Review policy: [../../../REVIEW_POLICY.md](../../../REVIEW_POLICY.md)
- Admission contract: [../../../SKILL_ADMISSION.md](../../../SKILL_ADMISSION.md)

## Release gate

| Gate | Status | Evidence |
| --- | --- | --- |
| Ownership and scope | `VERIFIED` | First-party package list and public ownership boundary. |
| Metadata/invocation consistency | `VERIFIED` | Collection test plus package frontmatter and `agents/openai.yaml`. |
| Package behavior | `VERIFIED` for the listed local contract/behavior checks | See [TEST_SUMMARY.md](TEST_SUMMARY.md); fresh installation and independent acceptance remain separate gates. |
| Fresh whole-repository install | `VERIFIED` | See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md). |
| Fresh per-Skill install | `VERIFIED` | See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md). |
| Independent `review-loop agent-skill` acceptance | `BLOCKED` until a fresh independent evaluator record is attached | Same-context review is not independent evidence. |
| GitHub Actions | `VERIFIED` on merged release commit | See `.github/workflows/quality.yml` and the public Actions run. |

This receipt is a release record, not an independent acceptance record, while
the independent evaluator row is `BLOCKED`. Do not call structural evidence
model-mediated runtime proof.
