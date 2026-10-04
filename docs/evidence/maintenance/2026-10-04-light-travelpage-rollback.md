# Light-TravelPage UI rollback — 2026-10-04

The owner requested withdrawal of the published handbook UI commits and local testing before any renewed publication. The rollback restores the entire `skills/productivity/light-travelpage` package byte-for-byte to `49e7cbe`, before `e1f1f4b` introduced the handbook design. It preserves the earlier geographic outlines, desktop flight controls, PDF previews, bilingual cards and shared-state behavior.

The experimental `codex/travel-handbook-ui` worktree remains at `f5f1a3d`; the separate local AI MVP is retained. This rollback does not deploy a travel page, alter booking facts, create a tag/release, or authorize publishing the revised UI again.

Historical review and publication evidence under `2026-10-04-light-travelpage-review/` remains unchanged. Its acceptance describes the withdrawn artifact, not current user approval. Current package behavior returns to the [pre-change maintenance baseline](2026-09-27-light-travelpage.md).

Local validation: all 57 package files match `49e7cbe`; 40 template tests and 18 collection contract/discovery/composition checks pass. The restored generator builds the complete synthetic Hokkaido trip with geographic outlines and ticket previews. A fresh project-local copy has identical hashes, resolves relative links and is discovered by the skills CLI. The generator rejects an existing destination directory. Missing cached npm dependency was resolved by reusing already installed project dependencies, without changing package sources.

The immutable rollback candidate is submitted for bounded independent Standards/Spec review and a fresh Evaluator. Publication is pending those checks.
