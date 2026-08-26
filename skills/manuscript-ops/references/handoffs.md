# Explicit Skill handoffs

`manuscript-ops` coordinates dependencies; it does not impersonate or install
them. Read `assets/dependency-contracts.json` before a Project handoff and run:

```text
python scripts/check_dependencies.py --catalog <active-skill-catalog>
```

For a provenance-complete check, add `--online`; `READY` is required before a
Project handoff. If Decision-map selects an optional branch, also pass
`--require-optional prototype` as applicable. An unselected
optional branch is not a missing dependency.

Repository maintainers use `--online --audit-all` to audit every optional
contract as well. Do not use `--audit-all` in an ordinary manuscript handoff;
it changes audit scope, not the selected workflow branch.

Use `--strict-agent-skills` on a client that rejects non-standard frontmatter.
The pinned `clarify` user entry starts the underlying `socratic` capability;
the `clarify` and `decision-map` contracts currently use
`disable-model-invocation`; a strict client must return `BLOCKED` unless it has
compatible releases or an explicit host extension.

## Host-neutral call model

Record a handoff as a logical Skill name, mode/arguments, expected artifact, and
resume condition. Render it using the current host:

| Host | Rendering |
|---|---|
| Codex | `$<skill-name> <arguments>` |
| Slash-command client | `/<skill-name> <arguments>` |
| Other Agent Skills client | Explicitly activate `<skill-name>` with `<arguments>` using the host's documented mechanism |

The `$` and `/` prefixes are host syntax, not part of the portable contract.

## Discovery

Use exactly one route:

- `clarify`: unresolved decisions can be settled with the user in one session.
- `decision-map`: the effort spans sessions and the decision frontier is still
  unclear. Request its local Markdown tracker for manuscript work unless the
  project already has an approved issue tracker.

Logical calls:

```text
activate clarify with: resolve the open manuscript decisions recorded in <path>
activate decision-map with: chart this manuscript effort in a local Markdown task graph; do not implement it
```

After the dependency stops, ask the user to activate `manuscript-ops` with
`resume`. In Codex, render that as `$manuscript-ops resume`.

## Project initialization recommendation

After Brief approval, check the exact target root for the project-initialization
outcome required by this Skill: applicable project rules, a mapped Project
Profile, a `.manuscript-ops/` state directory, and a resumable baseline path.
If that outcome is missing, recommend the user activate `project-init` with the
exact root. In Codex:

```text
$project-init init in <exact-project-root>
```

`manuscript-ops` must stop after stating the missing outcome and the expected
validation evidence. It must not automatically invoke the user-invoked
initializer. The user resumes with:

```text
$manuscript-ops resume from <exact-project-root>/.manuscript-ops/state.json
```

## Independent acceptance

After project initialization and a dated baseline, logically activate
`project-review` with:

```text
init using <approved-brief-path>
```

At a required milestone, use:

```text
review <milestone> against <charter-path>
```

Use its `resume` mode only when durable state makes the next action unambiguous.
Preserve `PASS`, `FAIL`, `BLOCKED`, and the raw `project-review` independence
metadata. Normalize it into the manuscript report without overwriting it:
`full -> native`; `degraded -> fresh_session` only with evidence of a genuinely
new isolated session, otherwise `degraded`; `unavailable -> degraded/BLOCKED`.

After `project-review init`, the expected artifacts are
`<exact-project-root>/.project-review/charter.md` and `state.md`. After a milestone
review, the expected artifact is the frozen round verdict referenced by
`state.md`. Once those paths and the reported verdict are checked, logically
activate `manuscript-ops` with `resume`. In Codex:

```text
$manuscript-ops resume from <exact-project-root>/.project-review/state.md
```

## Dependency closure and order

Install and refresh the agent between layers when necessary:

1. Required first-party discovery closure from `LightDevCoder/skills`:
   `clarify` (the user entry), its underlying `socratic` capability, and
   `decision-map`.
2. Optional Decision-map branches, before they are selected: `prototype`.
3. Independent acceptance from `LightDevCoder/skills`: `project-review`.
4. `manuscript-ops`.

Never install dependencies automatically during manuscript execution.

### Generic installer

```text
npx skills@latest add LightDevCoder/skills
```

Select the exact closure above. Use the installer's global flag only when the
user intentionally wants a global catalog; otherwise keep project scope.
These generic commands follow the repository's current default branch; they do
not by themselves prove the reviewed commit. Refresh the host's Skill catalog
and rerun `check_dependencies.py --catalog <catalog> --online`. Online checking
compares the complete pinned directory tree, every installed package file byte,
and whole-package default-branch drift; unregistered extra files block. Use the
Codex or manual method below when the installer cannot select an exact commit.

### Codex installer

Resolve the default Codex home when `CODEX_HOME` is unset:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$installer = Join-Path $codexHome 'skills\.system\skill-installer\scripts\install-skill-from-github.py'
python $installer `
  --repo LightDevCoder/skills `
  --ref 93f2c3dc7d0dc400ee6aaf4ee240fe28592dfb93 `
  --path skills/clarify skills/socratic skills/decision-map skills/project-review
```

Install `skills/prototype` only if the chosen Decision-map branch
requires it. Start a fresh Codex session after installation.

### Manual portable installation

Clone `LightDevCoder/skills` at
`93f2c3dc7d0dc400ee6aaf4ee240fe28592dfb93`. Copy every selected
`skills/<name>` folder so it ends at `.agents/skills/<name>/SKILL.md`. For
example:

```text
.agents/skills/clarify/SKILL.md
.agents/skills/socratic/SKILL.md
.agents/skills/decision-map/SKILL.md
.agents/skills/project-review/SKILL.md
```

Do not copy a repository root into a single Skill folder. Confirm each Skill is
discoverable before continuing.

## Missing capability

Return a blocking handoff with:

- missing dependency or platform primitive;
- exact step that requires it;
- one of the installation methods above and a fresh-session instruction;
- evidence already preserved;
- exact logical resume call plus current-host rendering.

If native subagents are absent, review can continue only through a frozen packet
in an independent fresh session. Mark `independence: fresh_session`. If no
independent context exists, mark `degraded` and return `BLOCKED`; do not
describe same-context role play as independent.

## Platform claims

The core contract follows the Agent Skills specification. Product metadata in
`agents/openai.yaml` improves Codex discovery but is not part of the portable
core. Upstream dependency compatibility is a separate fact. State support as:

- `end-to-end tested`;
- `component tested`;
- `core specification compatible; Project dependencies client-dependent`;
- `unsupported`.

Never promote core specification compatibility into a full Project-route or
runtime test claim.
