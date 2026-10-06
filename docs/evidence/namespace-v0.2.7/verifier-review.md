# Released-source verifier software review

- Fixed point: `ff259a0230b038387101a75df728136f7de3dcc1`.
- Independent read-only Standards and Spec axes; findings only. The project-review Core owns the candidate verdict.
- The existing three-check limit was extended once to four by the owner on 2026-10-06, together with the concrete Codex/Claude Code installation scope. No fifth specialist check or restarted loop occurred.

| Check | Target | Standards | Spec |
| --- | --- | --- | --- |
| 1 | `c526547` | Findings: [] | V27RS001 medium: inferred observed roots could hide an omitted intended target |
| 2 | `81790de` | Findings: [] | V27RS001 fixed; V27RS002 medium: partial literal CLI registry parser accepted an expression prefix |
| 3 | `a50510e` | Findings: [] | V27RS002 persists for multiline continuation |
| 4 | `cb61cee` | Findings: [] | V27RS001/V27RS002 fixed; V27RS003 medium: default source count unguarded; V27RS004 low: Chinese target scope too broad |

The approved simplification removes the generic registry parser and declares Codex `.agents/skills` and Claude Code `.claude/skills` project targets. Global Codex and three representative Codex singles remain. Both whole sources must have exactly36 packages; each intended target must contain the full source payload. Unsupported selections, omitted destinations, missing/extra/mutated packages, invalid identities and non-fresh global environments are rejected.

Bounded fourth-check repairs are frozen at `a6ffa11bb827b43e8c9dec162698eb1b9968539e`. V27RS003 adds a shared36-package guard immediately after both clones plus real35/37-source negatives. V27RS004 narrows the Chinese text to Codex/Claude Code. Nine focused checks,543 pytest tests,167 unittest tests, compilation and documentation checks pass. These two repairs are handed to the previously required fresh whole-candidate Evaluator; no extra specialist pass is implied.

Actual all-Agent exploration used79 configurations at55 distinct roots. Eve intentionally rewrites Skill frontmatter, so that exploration is not byte-identical all-target proof. Codex and Claude Code each preserve36 packages/386 files. No universal Agent or Claude runtime claim is made.

Public release-source installation remains a subsequent gate requiring a real protected tag and actual hosted-run artifact. Local script tests are not R4 installation evidence.

The fresh independent whole-candidate Evaluator inspected both raw check4 reports and final repairs, independently ran nine verifier tests, and closed V27RS003/V27RS004. See [evaluation](evaluator-resumed.md).
