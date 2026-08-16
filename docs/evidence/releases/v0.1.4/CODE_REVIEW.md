# v0.1.4 ask-light scanner code-review evidence

[中文记录](CODE_REVIEW.zh-CN.md)

Runtime-script change in `skills/ask-light/scripts/ask-light.ps1`
(`Test-PathUnder` cross-platform separator fix) plus a negative
cross-platform scenario in `skills/ask-light/tests/test_ask_light_behavior.py`.
Repo policy requires `code-review` evidence for runtime-script changes.

## Review scope

- Fixed point: commit `f8a9fcf` (post-admission state)
- Files: `skills/ask-light/scripts/ask-light.ps1`,
  `skills/ask-light/tests/test_ask_light_behavior.py`
- Specialist: fresh read-only code-review subagent (Standards + Spec axes)

## Findings and disposition

| ID | Axis | Severity | Finding | Disposition |
| --- | --- | --- | --- | --- |
| STD-1 | Standards | Low | `Test-PathUnder` compares paths with `OrdinalIgnoreCase`, which on a case-sensitive Linux filesystem could treat `/tmp/MySkill` as "under" a readable `/tmp/myskill` (pre-existing behavior, now meaningful on Linux). | Accepted with rationale: case-insensitive comparison preserves historical behavior on Windows and macOS (case-insensitive filesystems by default); on Linux both sides of the comparison come from host-reported paths with consistent casing, and PowerShell has no portable per-filesystem case-sensitivity probe. No behavioral test exercises differing-case paths; the negative scenario pins outside-path rejection with matching casing. |

No Spec findings: the change matches the originating need exactly — the
hardcoded `'\'` made every candidate "outside host readable paths" on
Linux/macOS pwsh; the fix uses the platform separator while leaving the
Windows behavior byte-for-byte identical, and the new negative scenario is a
true negative (outside-skill under a discovered root but outside
`readablePaths`).

## Test evidence for the change

- `skills/ask-light/tests/test_ask_light_behavior.py` exercises the real
  scanner through pwsh (PowerShell 7.4.6) against disposable fixture
  catalogs: host-filter positive (compatible Skill eligible), the new
  outside-readable-path negative (unavailable + actionable gap), block-list
  and host-declaration cases. Result: OK locally on macOS; the same suite
  previously failed on ubuntu CI, which this change fixes.
