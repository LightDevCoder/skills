# Integration-only Diff Record

Only `manuscript-ops` has changes under an Integration-only Skill directory in this refactor.

Reviewed each changed file as necessary Light integration wiring:

- `SKILL.md` — updates renamed capability references (`grill-me`/`grilling`/`wayfinder`/`review-loop` → `clarify`/`socratic`/`decision-map`/`project-review`).
- `references/*.md` — same pointer repair; no behavioral redesign.
- `assets/dependency-contracts.json` — dependency closure updated to the first-party Light packages and current commit.
- `scripts/*.py` — updates string/function names to the new review ownership and excludes `.DS_Store` from package file scans; no logic redesign.

No other Integration-only Skill (`release-workflow`, `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts`) is modified.
