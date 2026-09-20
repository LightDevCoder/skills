# Installation Verification — v0.2.3

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Fresh Installation Matrix

Tested in disposable fresh environments using official `skills` CLI:

| Variant | Command | Result | Verified Artifacts |
| --- | --- | --- | --- |
| Pinned Whole Collection | `npx --yes skills add LightDevCoder/skills#v0.2.3 --yes --copy --agent '*'` | `PASS` | All 36 package directories installed and verified against published v0.2.3 tag. |
| Generic Latest Whole Collection | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `PASS` | All 36 package directories installed from default branch `main`. |
| Pinned Single Skill (`project-retro`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill project-retro --yes --copy --agent '*'` | `PASS` | `skills/project-retro/` installed with refactored positive instructions and state transitions. |
| Pinned Single Skill (`agent-config`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill agent-config --yes --copy --agent '*'` | `PASS` | `skills/agent-config/` installed with profile-driven contracts and abstract profiler. |
| Pinned Single Skill (`ask-light`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill ask-light --yes --copy --agent '*'` | `PASS` | `skills/ask-light/` installed with bounded semantic query planner and discovery contracts. |
| Pinned Single Skill (`project-init`) | `npx --yes skills add LightDevCoder/skills#v0.2.3 --skill project-init --yes --copy --agent '*'` | `PASS` | `skills/project-init/` installed with canonical CLI mappings and optional Jev onboarding. |
