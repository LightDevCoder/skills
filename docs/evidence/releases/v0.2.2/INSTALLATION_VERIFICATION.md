# Installation Verification — v0.2.2

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Fresh Installation Matrix

Tested in disposable fresh environments using official `skills` CLI:

| Variant | Command | Result | Verified Artifacts |
| --- | --- | --- | --- |
| Pinned Whole Collection | `npx --yes skills add LightDevCoder/skills#v0.2.2 --yes --copy --agent '*'` | `CANDIDATE` | All 36 package directories to be installed and verified against candidate tag. |
| Generic Latest Whole Collection | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `CANDIDATE` | All 36 package directories installed from default branch `main`. |
| Pinned Single Skill (`agent-config`) | `npx --yes skills add LightDevCoder/skills#v0.2.2 --skill agent-config --yes --copy --agent '*'` | `CANDIDATE` | `skills/agent-config/` installed with full profile-driven contracts and abstract profiler. |
| Pinned Single Skill (`ask-light`) | `npx --yes skills add LightDevCoder/skills#v0.2.2 --skill ask-light --yes --copy --agent '*'` | `CANDIDATE` | `skills/ask-light/` installed with bounded semantic query planner and discovery contracts. |
| Pinned Single Skill (`project-init`) | `npx --yes skills add LightDevCoder/skills#v0.2.2 --skill project-init --yes --copy --agent '*'` | `CANDIDATE` | `skills/project-init/` installed with canonical CLI mappings and optional Jev onboarding. |
