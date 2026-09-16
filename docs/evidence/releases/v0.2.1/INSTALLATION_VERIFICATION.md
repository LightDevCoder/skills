# Installation Verification — v0.2.1

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Fresh Installation Matrix

Tested in disposable fresh environments using official `skills` CLI:

| Variant | Command | Result | Verified Artifacts |
| --- | --- | --- | --- |
| Pinned Whole Collection | `npx --yes skills add LightDevCoder/skills#v0.2.1 --yes --copy --agent '*'` | `PASS` | All 36 package directories installed and verified byte-identical to release commit. |
| Generic Latest Whole Collection | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `PASS` | All 36 package directories installed from default branch `main`. |
| Pinned Single Skill (`project-retro`) | `npx --yes skills add LightDevCoder/skills#v0.2.1 --skill project-retro --yes --copy --agent '*'` | `PASS` | `skills/project-retro/` installed with `SKILL.md`, `agents/openai.yaml`, and references. |
| Generic Single Skill (`agent-config`) | `npx --yes skills add LightDevCoder/skills --skill agent-config --yes --copy --agent '*'` | `PASS` | `skills/agent-config/` installed with full profile-driven contracts. |
| Generic Single Skill (`light-travelpage`) | `npx --yes skills add LightDevCoder/skills --skill light-travelpage --yes --copy --agent '*'` | `PASS` | `skills/light-travelpage/` installed with templates and assets. |
