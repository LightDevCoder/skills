# Routing

## Six dimensions

Score each dimension `0`, `1`, or `2`. A missing answer is `unknown`; use an
effective score of `1`, record it, and do not silently turn it into zero.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Scale | one bounded item | several sections or a medium report | book/manual, many sections, or cross-session volume |
| Source complexity | one trusted source | several sources with simple precedence | conflicting, mixed-authority, multimodal, or evidence-heavy sources |
| Risk | ordinary prose | material factual/reputational impact | safety, privacy, legal/regulatory, medical, financial, or other high-stakes facts |
| Output complexity | one text-native output | one styled output or several simple outputs | multilingual, locked derivative, or several layout-sensitive outputs |
| Collaboration | one writer and one user review | several reviewers or a handoff | multi-thread independent review or several owners |
| Reproducibility | direct edit is acceptable | repeatable generation is useful | deterministic regeneration, hashes, gates, and archived evidence are required |

## Hard triggers

Select `Project` regardless of total when any trigger is true:

- the user explicitly requests the Project route;
- work must continue across sessions;
- the manuscript is large enough that a single coherent review is unsafe;
- facts carry high safety, privacy, legal, regulatory, medical, or financial risk;
- a locked source will produce translations or other derived editions;
- several formats must be reproducibly generated and visually checked;
- independent multi-thread acceptance is required.

Unknown hard-trigger facts remain visible in `unknowns` and select `Project`
until evidence resolves them. Ask only when the answer is required to continue
safely; do not convert an unresolved trigger to false.

## Decision rule

1. Sum effective dimension scores.
2. Apply hard triggers; a true or unresolved hard-trigger fact selects
   `Project`.
3. Use `Quick` for `0-3`, `Structured` for `4-7`, and `Project` for `8-12`.
4. If an unknown leaves the effective total exactly `3` or `7`, route upward.
5. Record the evidence and reason. Do not score from prose intuition alone.

## Routing evidence

Repository evidence may include file count, total bytes, extensions, existing
instructions, source manifests, output folders, scripts, version-control
markers, prior review records, and user-provided facts. A filename is a clue,
not proof of authority, privacy, language, or content.

Use `scripts/assess_project.py` to create a read-only snapshot. Its automatic
inspection intentionally leaves intent and risk unknown unless an answers file
supplies them.

## Examples

| Scenario | Expected route | Reason |
|---|---|---|
| Correct one paragraph in a Markdown note | Quick | bounded, low-risk, one output |
| Write a sourced departmental report | Structured | multiple sources, outline, review |
| Rebuild a long technical manual | Project | scale, sources, layout, reproducibility |
| Polish a short safety notice | Project | high-risk hard trigger |
| Create locked Chinese and English DOCX/PDF editions | Project | language, derivation, multi-format hard triggers |
