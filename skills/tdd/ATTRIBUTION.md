# Attribution — tdd

This package is a Light first-party port of an upstream Skill.

- **Source repository:** [https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)
- **Original Skill path:** `skills/engineering/tdd` (contains `SKILL.md`, `agents/openai.yaml`, `mocking.md`, `tests.md`)
- **Pinned revision:** `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e` (short `6acc160`, 2026-08-06, version `1.2.3` via `package.json` at that revision; nearest tag is changeset-release/main merge commit)
- **License:** MIT — Copyright (c) 2026 Matt Pocock — see upstream `LICENSE`. The MIT notice is preserved as required; no original authorship is claimed.
- **Transformation summary:** PORT — NO REDESIGN (SPEC §14/§16). Preserved mature behavior verbatim; only the following Light integration changes were applied:
  1. Flattened path from upstream `skills/engineering/tdd` to Light `skills/tdd/`.
  2. Kept `SKILL.md` verbatim (no bloat, no rewrite). Supporting files kept verbatim (`tests.md`, `mocking.md` remain reference-only supporting docs).
  3. Adapted `agents/openai.yaml` for Light host discovery: added `interface.default_prompt` and `policy.allow_implicit_invocation` (true for model-invoked capabilities, false for user-invoked handoff) while retaining upstream `display_name`/`short_description`. No behavioral instructions duplicated.
  4. Added this `ATTRIBUTION.md` as required by SPEC §22.
  5. No runtime dependency on `https://github.com/mattpocock/skills` remains; the package is self-contained and does not require `install Matt skills first`.

Verification: `SKILL.md` frontmatter `name: tdd` matches, `agents/openai.yaml` is valid, and aside from this attribution no `mattpocock/skills` runtime coupling remains in executable content.
