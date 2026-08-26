# Project-init presets

Use one preset only after inspecting the project and recording the lightweight
answers. The entries below describe the minimum initialization contract; they
are not complete project workflows.

## Common fields

Every preset asks for the same six answers: project type, user-visible goal,
expected outputs, collaboration mode, important constraints, and required
review level. Every plan also records the target root, existing instruction
file, created or updated paths, relevant capabilities, and validation checks.

| Preset | Detection signals | Recommended documents | Issue tracker | Context and Skills | Review default | Initialization checks |
| --- | --- | --- | --- | --- | --- | --- |
| generic | mixed files, no dominant domain, or a small general project | `README.md` or an existing project brief only when needed | optional; preserve an existing tracker | project context and the user's chosen Skills | focused checks; escalate by risk | root instruction target, paths, and capability names |
| software | source code, package/build manifest, tests, CI, or deployment config | preserve README; add a project brief only if the goal is otherwise unrecorded | recommended for multi-slice work; never create one automatically | code-review, tdd, implement, and project-review may be recommended for later user invocation | review level follows risk; code review remains specialist | confirmed test/build commands, source paths, and instruction merge |
| manuscript | manuscript/document files, editorial brief, figures, or batch folders | brief/spec and source/evidence map only when missing | optional; use the existing issue/batch system | manuscript-ops and project-review may be recommended; preserve editorial constraints | format/source/review level from answers | source/evidence paths, document targets, and image/figure applicability |
| skill-development | `SKILL.md`, `agents/openai.yaml`, skill templates, or a Skill package goal | Skill brief and validation notes only when needed | optional; do not create tickets | learn-anything, writing-for-agents, and project-review may be recommended for later invocation | validator plus independent review when requested | package tree, frontmatter, metadata, references, and declared capabilities |
| research | source/evidence folders, literature notes, datasets, or an evidence-synthesis goal | research question, source register, and findings note only when missing | optional; preserve an existing research log | research and project-review may be recommended; source authority remains explicit | source-quality and synthesis review | source paths, provenance fields, and no unsupported claims |
| knowledge-base | notes vault, MOC/index files, wiki exports, or knowledge-ingest goal | index/MOC and source/derived-note locations only when missing | optional; preserve vault conventions | obsidian-vault or learn-anything may be recommended for later invocation | provenance and link/structure checks | vault root, links, indexes, and source preservation |
| data-analysis | CSV/XLSX/SQL/notebooks, dashboards, metrics, or analytical decision goal | data context, analysis notebook/report, and source register only when missing | optional; recommended only if an existing project convention requires it | data-analytics, spreadsheets, and project-review may be recommended for later invocation | reproducibility, data quality, and decision review | data paths, query/notebook entry points, outputs, and capability availability |

## Minimal instruction blocks

Add only the block for the selected preset to the one chosen instruction file.
Keep the block under a single `## Project Initialization` heading and preserve
all surrounding user-authored rules. Replace the bracketed values with answers;
do not copy this reference or an entire Skill into the project.

```markdown
## Project Initialization

- Type: [preset]
- Goal: [user-visible goal]
- Outputs: [expected outputs]
- Collaboration: [collaboration mode]
- Constraints: [important constraints]
- Review level: [required review level]
- Relevant Skills (invoke separately when needed): [available names]
- Initialization scope: paths and guidance only; no ticketing or implementation.
```

For a confirmed research fallback, add the same fields plus `Sources:`,
`Confirmation: user confirmed on [date]`, and a short `Validation:` line. Never
omit the source or confirmation record.
