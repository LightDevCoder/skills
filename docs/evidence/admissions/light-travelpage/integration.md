# Isolated collection integration proposal

Location: `.scratch/skills-integration`, detached worktree from Skills `66aa39a`. Actual Skills main remained unchanged while preparing the reviewable proposal.

Contains the final light-travelpage package (6bee388 source), Chinese/English README, catalog, changelog, installation and maintenance count updates. Stable release history is retained; current main count becomes35 and the new Skill is explicitly unreleased. ask-light's descriptive inventory adds the new package; no routing algorithm or other Skill behavior is changed. Its two count expectations and collection discovery tests are synchronized.

Verification:
- `python3 -m unittest discover -s tests -p 'test_*.py'`:28 tests passed;260 collection assertions and7 hook assertions reported.
- `python3 -m unittest discover -s skills/ask-light/tests -p 'test_*.py'`:85 tests passed.
- `git diff --check`:clean.
- Descriptor inventory:35 packages.

Initial checks correctly detected missing catalog installation field and old inventory/count expectations; repaired those specific synchronization omissions and reran the affected suites. No test was disabled.

Admission README and supporting evidence are under `docs/evidence/admissions/light-travelpage/`. The integration is a proposal until final Evaluator/Core acceptance, not a premature mutation of the actual collection.
