# Repair pass: finish incomplete Full-refactor information architecture

Type: task
Status: resolved

- Remove duplicate root SPEC; `.scratch/light-skills-lean-refactor/spec.md` is the single active authority.
- Add repository-level pytest collection exclusion for Frozen helper modules (`language-learning`, `recap`) without editing Frozen directories.
- Re-review every Full-refactor Skill and simplify SKILL.md entry points that still duplicated their local references or carried defensive prose:
  - changed: `agent-config`, `clarify`, `code-review`, `decision-map`, `generic-review`, `implement`, `project-clarify`, `project-init`, `project-spec`, `project-tickets`, `socratic`.
  - reviewed and intentionally left unchanged: `ask-light`, `project-review`, `review-loop` (already satisfied the SPEC in the previous pass).
- Replace prose-coupled test assertions with behavior/contract checks for the changed Skills.
- Remove `.DS_Store` artifacts and ignore them in `.gitignore`.
- Re-run Frozen hash integrity, Integration-only scope check, pytest, unittest, and compileall; record results in `final-results.md`.