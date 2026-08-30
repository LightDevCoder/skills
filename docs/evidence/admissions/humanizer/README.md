# `humanizer` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/humanizer/`
- Origin: ADAPT — substantially transformed first-party capability based on
  blader/humanizer `e2e92e7b4b8229253ed5c8e81dc65463fdeddda5` (version
  2.11.2) with a thin Chinese adaptation layer; see
  [ATTRIBUTION.md](../../../../skills/humanizer/ATTRIBUTION.md)
- Invocation type: model-invoked (`allow_implicit_invocation: true`)
- Admission route: full path — `review-loop` `agent-skill` Profile (the
  prompt-only fast track is unavailable because the package carries upstream
  content); final verdict owned by `project-review`
- Admission status: `PASS` (round 01; one minor finding repaired in scope)
- Release boundary: recorded on the `v0.2.0` release line; the pinned
  per-Skill install command is verifiable only after the collection tag is
  re-published and fresh released-repository verification is recorded

## Evidence summary

| Area | Result | Evidence boundary |
| --- | --- | --- |
| Attribution | PASS | `ATTRIBUTION.md` records both upstream sources, the pinned revision, both MIT notices, and the numbered transformation summary; independent review confirmed the pinned revision matches the upstream checkout. |
| Structure | PASS | Scripted verbatim-carry check: the `SKILL.md` body minus collection frontmatter and the added Language routing section is byte-identical to the pinned upstream revision; four files only; links resolve; no placeholders; no retired references. |
| Fresh-copy install | PASS | Isolated copy of the complete package: identical file set, all SHA-256 hashes match, discovery scan of the copy alone passes (name, description, model-invoked metadata, resolvable zh reference, attribution). Local-source admission evidence, not a released install command. |
| Behavior | PASS | Four producer fixtures (English AI-slop success; clean human boundary unchanged; Chinese AI-slop success with Chinese quotation marks preserved; fabrication-pressure refusal) plus one independent self-composed Chinese fixture — every rewrite kept all claims, invented nothing, and applied the zh overrides correctly. |
| Invocation | PASS | Declared model-invoked; `SKILL.md` frontmatter and `agents/openai.yaml` policy consistent (re-asserted by collection contract tests). |
| Collection quality | PASS | Repository suite re-run after registration; see the changelog entry on the `v0.2.0` line. |

## Review record

- Charter: [review-loop/charter.md](review-loop/charter.md)
- State: [review-loop/state.md](review-loop/state.md)
- Producer evidence: [review-loop/rounds/round-01/producer-evidence.md](review-loop/rounds/round-01/producer-evidence.md)
- Findings: [review-loop/findings.md](review-loop/findings.md) — one minor
  (HUM-01, attribution wording), disposition in
  [review-loop/rounds/round-01/finding-disposition.md](review-loop/rounds/round-01/finding-disposition.md)
- Independent evaluator verdict:
  [review-loop/rounds/round-01/evaluator-verdict.md](review-loop/rounds/round-01/evaluator-verdict.md)
- Final verdict (project-review): [review-loop/verdict.md](review-loop/verdict.md)

## Retirement of the source skills

The two source skills were retired from the local hosts when this package
was installed: the blader/humanizer git clone (previously symlinked into
`~/.agents/skills/` and `~/.claude/skills/`) and all three `humanizer-zh`
copies (previously installed from `LightDevCoder/skills-3rdParty` v0.2.1,
whose `UPSTREAM.md`/`PATCHES.md` provenance record documented zero behavior
patches). Nothing in the collection depends on either; the upstream
repositories remain the recommended direct-install sources for their
unmodified English and Chinese forms.
