# Producer Evidence — Round 01

## Package Artifacts
- `skills/project-retro/SKILL.md`
- `skills/project-retro/agents/openai.yaml`
- `skills/project-retro/ATTRIBUTION.md`
- `skills/project-retro/references/categories.md`
- `skills/project-retro/references/heuristics.md`
- `skills/project-retro/references/template.md`
- `skills/project-retro/tests/test_project_retro_contract.py`
- `skills/project-retro/tests/test_project_retro_behavior.py`

## Validation Results
1. Contract test: `python3 -m unittest skills/project-retro/tests/test_project_retro_contract.py` -> 7 assertions PASS.
2. Behavior test: `python3 -m unittest skills/project-retro/tests/test_project_retro_behavior.py` -> 5 assertions PASS.
3. Total 12 assertions passing.
4. Clean invocation policy: `allow_implicit_invocation: true` in metadata and model-invoked in frontmatter.
