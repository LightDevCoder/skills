# Project-init presets

Use one preset only after inspecting the project and recording the lightweight
answers. The entries below describe the minimum initialization contract; they
are not complete project workflows.

## Ambiguous match

When evidence supports two presets, compare only the material difference and
recommend one. Example: `software` establishes code/test/review assumptions;
`research` establishes source/provenance/reproducibility assumptions. Ask for
the choice before writing. Do not silently select by filename count.

## Common fields

Every preset asks for the same six answers: project type, user-visible goal,
expected outputs, collaboration mode, important constraints, and required
review level. Every plan also records the target root, the instruction filename
confirmed from current host evidence, created or updated paths, relevant
capabilities, and validation checks. The implemented local-markdown adapter
uses `.scratch/<effort>/issues`; a different locator requires another adapter.

| Preset | Detection signals | Recommended documents | Issue tracker | Context and Skills | Review default | Initialization checks |
| --- | --- | --- | --- | --- | --- | --- |
| generic | mixed files, no dominant domain, or a small general project | `README.md` or an existing project brief only when needed | Light local markdown; existing external trackers remain separate | project context and the user's chosen Skills | focused checks; escalate by risk | root instruction target, paths, and capability names |
| software | source code, package/build manifest, tests, CI, or deployment config | preserve README; add a project brief only if the goal is otherwise unrecorded | Light local markdown; existing external trackers remain separate until an adapter exists | code-review, tdd, implement, and project-review may be recommended for later user invocation | review level follows risk; code review remains specialist | confirmed test/build commands, source paths, and instruction merge |
| manuscript | manuscript/document files, editorial brief, figures, or batch folders | brief/spec and source/evidence map only when missing | Light local markdown; it may remain unused when no ticket stage is needed | manuscript-ops and project-review may be recommended; preserve editorial constraints | format/source/review level from answers | source/evidence paths, document targets, and image/figure applicability |
| skill-development | `SKILL.md`, `agents/openai.yaml`, skill templates, or a Skill package goal | Skill brief and validation notes only when needed | Light local markdown; do not create tickets during bootstrap | learn-anything, writing-for-agents, and project-review may be recommended for later invocation | validator plus independent review when requested | package tree, frontmatter, metadata, references, and declared capabilities |
| research | source/evidence folders, literature notes, datasets, or an evidence-synthesis goal | research question, source register, and findings note only when missing | Light local markdown; preserve separate research logs | research and project-review may be recommended; source authority remains explicit | source-quality and synthesis review | source paths, provenance fields, and no unsupported claims |
| knowledge-base | notes vault, MOC/index files, wiki exports, or knowledge-ingest goal | index/MOC and source/derived-note locations only when missing | Light local markdown; preserve separate vault conventions | obsidian-vault or learn-anything may be recommended for later invocation | provenance and link/structure checks | vault root, links, indexes, and source preservation |
| data-analysis | CSV/XLSX/SQL/notebooks, dashboards, metrics, or analytical decision goal | data context, analysis notebook/report, and source register only when missing | Light local markdown; it may remain unused when no ticket stage is needed | data-analytics, spreadsheets, and project-review may be recommended for later invocation | reproducibility, data quality, and decision review | data paths, query/notebook entry points, outputs, and capability availability |

## Stable configuration block

Pass the confirmed values to `scripts/bootstrap.py`. The instruction file gets
only the stable pointer; the managed block lives in
`docs/agents/light-project.md`:

```markdown
<!-- light-project:managed:start -->
# Light Project Configuration
- Project type: [preset]
- Goal: [user-visible goal]
- Outputs: [expected outputs]
- Relevant Skills: [available names]
- Issue tracker: [kind and locator]
- Domain context: [locators]
- Review profile: [profile]
- Acceptance strategy: [strategy]
- Working area: [.scratch]
<!-- light-project:managed:end -->
```

For a confirmed research fallback, pass `preset: research-fallback` and add the
same fields plus non-empty `Sources:`, `Confirmation: user confirmed on
[date]`, and a short `Validation:` line. `bootstrap.py` persists all three
inside the managed project contract and fails before writing when any is
missing. Never omit the source or confirmation record. The working area remains
`.scratch`; no alternative is implemented by this bootstrap.
