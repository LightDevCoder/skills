# Producer repair evidence

Charter travel-handbook-2026-10-03-v1; software with agent-skill package checks. This is Producer evidence, not final acceptance. Fixed scope and criteria are unchanged.

Round 1 candidate e1f1f4b84088f5d8bfd6b5f15431d2b81a403191 → Round 2 candidate 3f6cb55c9f0abcfda8d0f6d46da5d7d48753e1b6:
- F-001: add exact context, fixture identities and hashes (structural evidence).
- F-002: ledger labels/helpers 14px/12px; actual English 390px screenshot (manual evidence).
- F-003: retain current chapter on #main/#top; disabled ledger hash falls back to enabled travel content (behavioral assertion tests and actual-browser skip/draft observation).
- F-004: insert demo map examples before materials/legacy footer or append to main; existing actual-template regression asserts map button and demo notice (behavioral evidence).
Round 2 Standards returned Findings: []; Spec confirmed F-002..004 fixed and identified F-005/F-006. Original findings and source aliases remain in round1-findings.json and round2-findings.json.

Round 3 bounded repairs:
- F-005: handbook.css uses actual .todo-text and sufficiently specific menu selector. Actual 390px browser shows task 14px, menu 13px (manual evidence: task-menu-mobile.jpg). Only typography changes.
- F-006: ledger.js publishes existing travel-ledger:changed after its snapshot updates. Helper preserves the existing event shape; init, normal/forced refresh, successful recovery and local edits notify readers. Existing draft capture/guards remain. Two real-ledger/handbook integration tests assert changed bill/member pocket and retention of bill/member drafts, including blocked non-force refresh (behavioral evidence with a synthetic adapter, not remote D1).
- Latest complete suite: 48 pass, 0 fail (template-tests-round3.txt). Latest generated build succeeded (template-build-round3.txt). Runtime files match the package; package identity is package-hashes-round3.json. Exact command/environment/source inputs remain in context.md.

No source-schema, API authentication, SQL migration, deployment, permission, or package invocation change was introduced by these repairs. Original observations remain historical. Remote publication and fresh published-source installation are subsequent checks.
