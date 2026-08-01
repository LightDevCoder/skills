---
name: recap
description: Generate exactly one line summarizing the current Agent session's active goal, latest material outcome, and current state. Use only when the user explicitly invokes $recap; never trigger automatically, run tools, alter files, compact history, or invoke another Skill.
disable-model-invocation: true
---

# Session Recap

`recap` is a user-invoked, read-only session summary. It mirrors the useful
boundary of Claude Code's on-demand `/recap`: show one concise line about the
current session without replacing or compacting conversation history.

## Invocation and scope

Run only after an explicit `$recap` request. Use only the conversation and
completed tool activity already present in context. Do not call tools, read new
files, continue the task, modify an artifact, create durable state, or invoke
another Skill while producing the recap.

## Method

1. Identify the user's active goal from the current session.
2. Select the latest material outcome or decision and the current state.
3. Include the immediate next action or blocker only when it materially
   clarifies that state.
4. If the session has too little prior activity, say so without inventing
   progress.
5. Emit the result as exactly one line and stop.

## Output contract

- Output exactly one non-empty line of plain text containing one concise
  sentence.
- Do not add a heading, label, bullet, preface, code block, second paragraph,
  follow-up question, or separate next-step line.
- Summarize the current session, not the project in general.
- Prefer the newest material state over older details.
- Do not repeat credentials, tokens, private keys, or other secrets that may
  appear in tool output; describe the state at a safe level instead.
- Do not claim work was completed, tested, committed, pushed, or accepted
  unless that result is already present in the session.

## Boundaries and handoffs

This Skill does not create a durable handoff, compact context, issue a review
verdict, or resume work. If the user needs durable continuation material, they
may explicitly choose `handoff`; if they need final acceptance, they may
explicitly choose `review-loop`. `recap` never invokes either capability and
stops after its single output line.

## Verification

Run the contract and output-contract tests under [tests/](tests/). They validate the
explicit-only metadata, one-line output boundary, safe no-context result, and
rejection of multiline or labeled output. These deterministic tests are
structural/contract evidence; fresh Agent observations remain behavioral and
invocation evidence.
