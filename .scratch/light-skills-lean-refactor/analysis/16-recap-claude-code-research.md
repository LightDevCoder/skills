# Claude Code `/recap` behavior and a manual-only Light contract

Research date: 2026-08-27
Sources: Anthropic first-party documentation only

## Official behavior

- Claude Code describes a session recap as a **one-line** account of what has
  happened in the current session so far. Both the automatic recap and an
  on-demand `/recap` are capped at **400 characters**.
- `/recap` is the explicit, on-demand entry point. Claude Code also has a
  separate automatic away-recap feature, enabled by default, that prepares a
  recap after the terminal has been unfocused for at least three minutes and
  the session has at least three turns. That automatic behavior is configurable
  and is not intrinsic to the `/recap` command.
- Anthropic explicitly distinguishes the two commands: `/recap` appends the
  summary as command output instead of replacing message history, while
  `/compact [instructions]` replaces history with a summary. The recap is a
  display summary, not a compaction operation.

Sources:

- [Anthropic: Interactive mode — Session recap](https://code.claude.com/docs/en/interactive-mode#session-recap)
- [Anthropic: Prompt caching — Running `/recap`](https://code.claude.com/docs/en/prompt-caching#running-recap)
- [Anthropic: Manage sessions — Manage context within a session](https://code.claude.com/docs/en/sessions#manage-context-within-a-session)

## Manual-only adaptation for Light

Anthropic's skill documentation says a `SKILL.md` contains frontmatter **and a
Markdown instruction body**. It also defines
`disable-model-invocation: true` as the control that prevents automatic model
loading and leaves invocation to the user through `/<name>`.

The smallest useful Light behavior contract should therefore retain:

1. `disable-model-invocation: true` in frontmatter (plus the existing
   Codex-host `allow_implicit_invocation: false` metadata).
2. A body that tells the model what to do after manual invocation; frontmatter
   alone describes discovery and invocation but does not supply the executable
   instruction.
3. One output line, no more than 400 characters, summarizing what happened in
   the current session so far.
4. An explicit non-compaction boundary: do not clear, replace, compact, or
   rewrite conversation history; then stop.
5. No automatic away/idle trigger. The automatic behavior belongs to Claude
   Code's host feature, while the requested Light variant is manual-only.

A minimal body consistent with those constraints is:

> After an explicit `$recap` request, output one concise line of at most 400
> characters summarizing what happened in the current session so far without
> clearing, replacing, compacting, or rewriting conversation history, then
> stop.

Source for the manual-only skill control and the need for an instruction body:

- [Anthropic: Extend Claude with skills — Configure skills and control who invokes a skill](https://code.claude.com/docs/en/skills#configure-skills)

## Scope note

Claude Code's built-in `/recap` is fixed host logic, not a published upstream
`SKILL.md` that can be copied verbatim. The Light package should reproduce its
documented user-visible contract, not imitate undocumented implementation
details or the optional automatic away-recap scheduler.
