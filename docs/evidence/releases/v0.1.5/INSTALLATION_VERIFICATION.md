# v0.1.5 installation verification

[中文记录](INSTALLATION_VERIFICATION.zh-CN.md)

## Status

`PENDING` at the time of this commit. The verification runs after the
published `v0.1.5` tag exists, against fresh destinations and without a
source checkout, exactly as required by the release gate. The verified
results, CLI version, and discovery output are filled into the table below
once the run completes (post-release verification recorded on main).

## Procedure

1. Record `npx skills --version` and the exact command.
2. Use a disposable empty destination and make the source checkout
   unavailable to the host discovery step.
3. Run the whole-collection and per-Skill commands separately for both the
   generic `latest` form and the pinned `#v0.1.5` form.
4. Capture discovery (`npx --yes skills list`) and confirm
   `light-kanban-worker` is listed without relying on the source checkout.
5. Run one success and one boundary smoke against the installed
   `light-kanban-worker` package (package contract + behavior suites against
   the installed copy).
6. Repeat the same command and record whether it is a no-op or reports a
   duplicate.

| Field | Whole collection | Per-Skill (`light-kanban-worker`) |
| --- | --- | --- |
| Command | `npx skills add LightDevCoder/skills --yes --copy --agent '*'` and `npx skills add LightDevCoder/skills#v0.1.5 --yes --copy --agent '*'` | `npx skills add LightDevCoder/skills --skill light-kanban-worker --yes --copy --agent '*'` and `npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'` |
| Installer version | pending | pending |
| Host / destination | pending | pending |
| Result | pending | pending |
| Discovery without source checkout | pending | pending |
| Success smoke (contract + behavior suites on the installed copy) | pending | pending |
| Boundary smoke | pending | pending |
| Repeat install | pending | pending |
