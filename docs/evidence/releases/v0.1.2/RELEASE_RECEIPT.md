# v0.1.2 release receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `IN PROGRESS` — the seven-package collection and this evidence tree are
prepared; tag, remote release, fresh installation, and the publish commit remain
open gates.

## Identity

| Field | Value |
| --- | --- |
| Repository | `LightDevCoder/skills` |
| Release | `v0.1.2` |
| Release commit | `NOT TESTED — fill after the release tag is created` |
| Release URL | `NOT TESTED — fill after GitHub release creation` |
| Date | `2026-08-10` |
| Scope | Seven first-party packages (the five in v0.1.1 plus `recap` and `language-learning`), bilingual docs, Quick Start, workflow recipes, header, CI, and the generic `latest` install command. |

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
| Ownership and scope | `VERIFIED` | Seven first-party package list and public ownership boundary. |
| Metadata/invocation consistency | `VERIFIED` | Collection test plus package frontmatter and `agents/openai.yaml`. |
| Package behavior | `VERIFIED` for the listed local contract/behavior checks | See [TEST_SUMMARY.md](TEST_SUMMARY.md); fresh installation and independent acceptance remain separate gates. |
| Fresh whole-repository install | `NOT TESTED` | See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md). |
| Fresh per-Skill install | `NOT TESTED` | See [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md). |
| Independent `review-loop agent-skill` acceptance | `VERIFIED` for the two newly admitted packages; `BLOCKED` for the original five | `recap` and `language-learning` each carry a fresh independent fast-track Evaluator `PASS`; the original five still lack a fresh independent evaluator record. |
| GitHub Actions | `NOT TESTED` until the workflow has run on the release commit | See `.github/workflows/quality.yml`. |

Do not call this receipt an independent acceptance record for the original five
packages while their independent evaluator row is `BLOCKED`. Do not call
structural evidence runtime proof.
