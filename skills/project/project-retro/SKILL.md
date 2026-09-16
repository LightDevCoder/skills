---
name: project-retro
description: Conduct a retrospective on a completed project or session to identify environment, guardrail, navigation, tool economy, and workflow improvements. Model-invoked at the conclusion of a project or user-invoked when requested.
---

# Project Retro

`project-retro` conducts a retrospective on a completed project or coding
session, identifying actionable improvements to the agent's environment,
guardrails, navigation, tool economy, and steering files to make future runs
smoother and more reliable.

## When to use

- **At the conclusion of a project workflow:** After `project-review` issues a
  verdict or `release-workflow` completes, the Agent evaluates whether a
  retrospective is warranted.
- **After a complex implementation session:** When an agent encounters
  non-trivial friction during coding or debugging.
- **User-invoked on demand:** Whenever the user explicitly asks for a
  retrospective, post-mortem, or environment review (`$project-retro`).

## Agent self-evaluation trigger (Workflow final step)

At the final step of a project or task, the Agent must independently assess
whether to invoke `project-retro` by checking for friction signals:

| Friction signal | Threshold to invoke |
| --- | --- |
| **Navigation** | Agent spent significant turns or tool calls searching for files, or hidden dependencies caused confusion. |
| **Missing guardrail** | Agent made an error or broke tests that an automated check (lint, typecheck, pre-commit hook, CI job) could have caught deterministically. |
| **Reviewer / Standards gap** | Reviewer missed an issue, or a mechanical rule was expressed as prose rather than a deterministic check. |
| **Steering bloat** | `AGENTS.md` / `CLAUDE.md` has grown unwieldy, contains stale rules, or has instructions that do not alter behavior (no-ops). |
| **Tool economy** | Inefficient or redundant tool calls were made (e.g. repeated large-file reads, unindexed searches). |
| **Information access** | Crucial logs, runtime status, or primary source docs were unavailable or hard to inspect. |

- **If one or more friction signals are observed:** Invoke `project-retro` to
  analyze the session and present structured findings.
- **If the session ran smoothly without friction:** Skip `project-retro`
  cleanly. Do not add noise, unnecessary token overhead, or redundant steps to
  a successful, routine run.

## Steps

1. **Review writing standards:** Follow `writing-for-agents` principles — keep
   recommendations concise, specific, and actionable.
2. **Gather session evidence:** Examine the primary sources for the session:
   session logs, git history/diff, test output, review findings, and steering
   files. Default to the current session if none is specified.
3. **Analyze candidate improvements across core categories:**
   - **Navigation:** Are file pointers missing? Would an explicit index help?
   - **Automated checks:** Can a deterministic check (lint, typecheck, hook,
     script) replace human vigilance or agent guesswork? Prefer building a
     check over writing a prose rule.
   - **Coding standards:** Should reviewer instructions be clarified? Reserve
     `CODING_STANDARDS.md` for genuine judgment calls; push mechanical rules to
     linters or CI.
   - **Steering economy:** Can instructions in `AGENTS.md` or `CLAUDE.md` be
     slimmed, moved to standards, or removed as no-ops?
   - **Tool economy:** Did the agent make expensive or redundant tool calls?
   - **Information access:** Was key telemetry or logging missing?
4. **Present findings in order of severity:** Use the standard report format
   (see [template.md](references/template.md)). Rank candidates by impact,
   distinguishing high-leverage guardrails from minor polish.

## Handoff and stop

- Stop after presenting the retrospective findings.
- Do not automatically edit repository configuration, linters, or steering
  files without explicit human approval.
- When the user approves a specific recommendation, implement only the
  approved change in a bounded, verified step.

## References

- [categories.md](references/categories.md) — Detailed inspection criteria and
  remediation patterns across the six categories.
- [heuristics.md](references/heuristics.md) — Decision matrix and heuristic
  rules for the agent's self-evaluation trigger.
- [template.md](references/template.md) — Markdown retrospective report template.
