# Review Charter — project-retro admission

- Target: `skills/project-retro/`
- Profile: `agent-skill`
- Origin: Port & Light workflow adaptation of Matt Pocock `retro` (`959a8e9f1edc3adbe2f7e3054bb6fbefa6696260`)
- Acceptance criteria:
  1. Attribution integrity: MIT license notice preserved, pinned upstream commit, explicit transformation summary.
  2. Structure: Concise `SKILL.md`, supporting files under `references/`, metadata under `agents/openai.yaml`.
  3. Invocation: Declared model-invoked (`allow_implicit_invocation: true`), consistent across files.
  4. Behavior: Comprehensive contract and behavior tests covering heuristics and 6 core categories.
  5. Workflow integration: Documented agent self-evaluation at workflow conclusion.
