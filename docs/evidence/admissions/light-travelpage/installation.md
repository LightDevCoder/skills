# Isolated installation evidence

Date: 2026-09-13. macOS, Node v26.7.0. Candidate-local source, not a published release.

Created a clean source copy under `.scratch/install-source/light-travelpage` excluding node_modules, .wrangler, dist and local build backups. Size of installed package: 3.2M. Installation runs used fresh project roots, explicit Codex target, copy mode; no global user skill directories were modified.

- In `.scratch/install-final-package`: `npx --yes skills add <absolute .scratch/install-source/light-travelpage> --skill light-travelpage --agent codex --yes --copy`, then `npx --yes skills list --agent codex`.
- In `.scratch/install-final-scope`: `npx --yes skills add <absolute .scratch/install-source> --agent codex --yes --copy`, then the same list command.

Both commands succeeded and listed light-travelpage under the isolated `.agents/skills` directory for Codex. Raw output: install-package.log and install-scope.log. This demonstrates CLI installation/discovery, not a running Codex host automatically loading the Skill. Independent forward use is recorded separately. No remote released-install command is claimed verified.

`python3 /Users/light/.codex/skills/.system/skill-creator/scripts/quick_validate.py candidate/light-travelpage` returned `Skill is valid!`.

Final revision refresh (6bee388): repeated both source forms in fresh `.scratch/admitted-package-check` and `.scratch/admitted-scope-check` directories. Logs: install-final-package.log and install-final-scope.log. Both list the Skill for Codex. A byte-for-byte comparison of every candidate source/resource file (excluding dependencies/build outputs and Finder metadata) confirmed both installed copies match the final candidate.

## Published main verification — 2026-09-14

After admission commit `26a9f8d` was pushed to `LightDevCoder/skills` main, a fresh `.scratch/published-install` project successfully ran `npx --yes skills add LightDevCoder/skills --skill light-travelpage --agent codex --yes --copy`, followed by `npx --yes skills list --agent codex`. All 47 installed files matched the final candidate byte for byte. Raw log: [install-remote.log](install-remote.log). This verifies the published main source and CLI discovery, not a new release tag or automatic loading in an existing host. No global skill directory was modified.
