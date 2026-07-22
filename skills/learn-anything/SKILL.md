---
name: learn-anything
description: Turn conversations, transcripts, project notes, folder workflows, documentation, or other sources into reusable agent skills and Skill Creator compatible instructions. Use when a user asks to create, update, distill, or "learn" a workflow as a skill; preserve repeated operating methods for future AI agents; encode corrections/failure modes as durable procedure; or transform source material into portable skill guidance for coding agents, research agents, automation agents, or custom agent frameworks.
---

# Learn Anything

This is a **user-invoked** Skill. Creating or updating a durable package needs
the user's intentional selection; do not invoke another user-invoked Skill on
the user's behalf.

## Purpose

Use this skill to learn whether arbitrary source material contains a compact, reusable agent method. Extract repeatable operating methods, not passive summaries of what happened.

The source-sufficiency branch produces an **internal Method Contract** only when the evidence is complete. It must preserve triggers, decisions, commands, constraints, failure modes, verification gates, and output contracts that are likely to recur. It must not use generic defaults to manufacture a production-ready `SKILL.md` from incomplete material.

## Compatible Agents

Write generated skills so they can be adapted by common AI agent hosts, not only one runtime. Expected consumers include:

- OpenAI Codex and Codex-style local coding agents
- Claude Code
- Gemini CLI
- Cursor agents
- Windsurf agents
- GitHub Copilot coding agent
- Aider
- OpenCode
- Roo Code
- Continue
- CrewAI agents
- LangGraph agents
- AutoGen agents
- ReAct-style custom agents
- Other file-reading coding, research, documentation, or automation agents that can follow Markdown instructions and run bundled scripts

## Source Intake

Gather only the source needed to infer a repeatable method:

- User request or goal statement
- Conversation transcript, task notes, issue thread, README, folder tree, test output, or workflow document
- Corrections from the user, especially repeated "do not do X; do Y" guidance
- Commands, paths, file names, APIs, schemas, and exact error strings that future agents must recognize
- Existing skills or project rules that the new skill must align with

If source material is sparse, return `BLOCKED` with the exact missing method fields. Treat `TBD`, `TODO`, `N/A`, `unknown`, empty placeholders, generic template boilerplate, inline literal markup such as `<placeholder>`, and embedded unresolved markers such as `TBD - decide later` as missing evidence even when headings are present. A standalone `TBD` or `TODO` within Purpose, Triggers, Inputs, Ordered Method, Decisions, Outputs, or Verification is also unresolved evidence; do not reject Constraints or Failure Modes merely because a guardrail says not to leave `TBD` values. Treat an asserted resource ending in an unresolved marker as a source gap; an explicit `none` resource is allowed. If invocation evidence names both user-invoked and model-invoked, return a blocked invocation-type conflict instead of choosing one. If it is narration, a one-off task, or a passive summary, return a learning summary explicitly marked `not_promoted`. Do not draft a package until source evidence is sufficient.

## Decision Workflow

1. Identify whether the source is a reusable workflow, narration, a passive summary, a one-off task, or too sparse to assess. Use affirmative title, leading-context, Purpose, Trigger, or bounded Scope/Context evidence for one-off and passive-summary classification; do not scan generic failure-mode prose and do not demote a complete method because a field says `not merely a one-off`, `no longer a one-off`, or because only a failure mode records `no procedure`.
2. Separate durable procedure from incidental task details. Keep what changes future behavior; preserve exact operational details from authoritative material.
3. Extract purpose, trigger branches, explicit invocation type, inputs, an ordered method, decisions, constraints, failure modes, outputs, resources, and verification.
4. Convert corrections and failure modes into source-backed constraints, guardrails, or verification checks without paraphrasing away commands, paths, decisions, or errors.
5. Create the internal Method Contract only when every required method field is evidenced. Record confidence and unresolved gaps in that contract.
6. When evidence is insufficient, return either a not-promoted learning summary or `BLOCKED` with precise required source gaps. Never fill missing fields with generic workflow, constraints, or quality checks.
7. Only after a complete internal Method Contract exists may the integrated Package Build Layer consider a package. The Method Contract is not a separately installable Skill.

## Package Build Prerequisite

Do not enter package build from raw source. A complete internal Method Contract is the prerequisite. The source-sufficiency gate itself outputs no `SKILL.md`.

## Package Build

After the gate returns `outcome: method_contract`, run the integrated package
builder with that JSON result. The builder is deterministic and keeps the
Method Contract internal:

```text
python learn-anything/hooks/package_builder.py \
  --contract-file <method-contract-result.json> \
  --output-root <skill-collection-root> \
  [--resource-root <source-resource-root>]
```

The builder derives a kebab-case name from the contract title unless `--name`
is supplied. It renders a direct-instruction `SKILL.md` with the source-backed
purpose, trigger branches, invocation type, inputs, ordered method, decisions,
constraints, failure modes, outputs, resources, preserved evidence, and
verification. Each ordered step has a checkable completion criterion. It does
not import, copy, or require `writing-great-skills` at runtime.

Treat builder results as explicit state:

- `created` means a new package was written.
- `updated` requires `--update` and changes only the generated package
  instructions while preserving unrelated files. The builder tracks copied
  resources in `.learn-anything-managed.json` and removes only resources that
  the previous generated contract owned but the new contract omits.
- `no-op` means the same contract already produced the package; preserve it.
- `duplicate` means an unowned package or different installation already
  exists; stop and obtain explicit authority before updating it.
- `blocked` means the contract is incomplete, unresolved, contradictory, or
  outside the package boundary. Return the precise reason and do not write.

Install only from a generated package into a clean host directory. Use the
builder's `install_package()` boundary (or copy the complete package directory
with the host's documented installer), then verify that `SKILL.md`, declared
metadata, and every justified resource are present. A second identical install
must be a no-op; a different existing package is a duplicate unless the user
explicitly authorizes an update.

## Internal Authoring Rules

Apply these rules while rendering the package; they are internal guidance, not
a runtime dependency on another Skill:

- Put the smallest ordered method needed for every trigger branch in `SKILL.md`;
  disclose branch-specific reference material only when that branch needs it.
- State what the package does and when to use it in the description. Keep one
  source of truth for each decision and remove duplicated or no-op prose.
- Preserve exact commands, paths, corrections, and failure conditions from the
  accepted source. Never fill a missing field with a generic heading or default.
- Include a resource only when the contract names and justifies it. Do not
  create empty directories, placeholder files, or an unverified script copy.
  Relative resources are copied only from an explicitly supplied
  `--resource-root` after existence and containment checks; absolute paths stay
  documented as external prerequisites.
- Keep the declared invocation boundary explicit. Recommend another
  user-invoked Skill and stop instead of silently running it.

## Generated Skill Shape

Every generated skill must include:

- `SKILL.md` with YAML frontmatter containing only `name` and `description`
- A kebab-case folder and skill name under 64 characters
- A description that states both what the skill does and when an agent should use it
- A body written as direct operating instructions
- Sections or equivalent content covering purpose, trigger, inputs, workflow, constraints, output format, and quality checks
- Bundled resources only when they are directly useful

Prefer this body structure unless the source strongly suggests another concise shape:

```markdown
# Skill Title

## Purpose

State what repeatable work the skill enables.

## Inputs

List source artifacts, credentials, paths, or context needed before acting.

## Workflow

Give the minimum ordered procedure that a future agent should follow.

## Constraints

Capture user preferences, scope boundaries, failure modes, safety rules, and exact decisions.

## Output Format

Describe the artifact, summary, patch, command output, or decision the skill should produce.

## Quality Checks

List concrete verification gates before final response.
```

## Extraction Rules

- Preserve exact commands, file names, headings, APIs, error strings, and user corrections when they carry operational meaning.
- Prefer imperative workflow steps over descriptive prose.
- Keep examples short and concrete.
- Do not include project-specific names unless they are necessary trigger signals, path conventions, or examples.
- Do not turn a one-off answer, translation, weather lookup, or time check into a skill.
- Do not create broad memory summaries. Encode how to act differently next time.
- Do not allow unresolved method fields to become stub sections. Return the source gap instead.
- Do not include unused resource folders.

## Hook Scripts

Optional deterministic helpers live in `hooks/`:

- `learn_gate.py`: classify a request before the task as `normal_task`, `observe_and_summarize`, or `create_or_update_skill`.
- `session_reflector.py`: inspect a completed transcript for reusable learning and return `ignore`, `summarize_candidate`, or `create_skill`.
- `skill_candidate_builder.py`: assess source sufficiency and return an internal Method Contract, a not-promoted learning summary, or `BLOCKED` source gaps.

Run them with raw text or a JSON object on stdin. They print JSON so other agents can use the decision without parsing prose.

## Quality Checks

Before delivering a generated or updated skill:

- Confirm the source-sufficiency result is `method_contract`, not `learning_summary` or `blocked`.
- Confirm the Method Contract includes purpose, triggers, invocation type, inputs, ordered method, decisions, constraints, failure modes, outputs, resources, verification, unresolved gaps, and confidence.
- Confirm exact commands, paths, decisions, corrections, and failure modes remain represented in source evidence when supplied.
- Confirm `SKILL.md` has valid frontmatter with only `name` and `description`.
- Confirm the description contains concrete trigger conditions.
- Confirm the body teaches a repeatable operating method rather than summarizing a session.
- Confirm constraints reflect user corrections and known failure modes.
- Confirm output format and quality checks are actionable.
- Run Skill Creator validation when a skill folder is available.
