# KB Init Research Contract

`research` is a supporting capability for `kb-init`.

Its purpose is to resolve external facts that affect a knowledge-base decision.

It must not become a parallel design process.

## Before dispatch: frame the decision

Before invoking `research`, internally define:

### Decision being supported

What exact user decision is currently unresolved?

Examples of decision roles:

- base choice;
- integration feasibility;
- attachment feasibility;
- search/retrieval feasibility;
- scale/limit concern;
- export/backup feasibility.

Do not research a vague topic if the actual decision is narrower.

### Research question

Write one narrow fact-finding question.

The question should be answerable from trustworthy sources.

### Comparison level

If alternatives are being compared, compare like-for-like options that occupy the same decision role.

Do not mix unrelated abstraction levels merely because all of them are technically related.

If a cross-layer comparison is genuinely necessary, normalize the comparison around one user decision and explain the role of each alternative.

### Must verify

List only the facts that could change the current decision.

### Out of scope

State what the research should not expand into.

This prevents research from designing adjacent systems or exploring unrelated implementation details.

### Return condition

Define what evidence must exist before `kb-init` can resume the paused decision.

## Dispatch behavior

If a callable `research` skill is available in the current harness, use it for this detour.

Do not bypass an available research skill with direct web search merely for convenience.

If the harness cannot invoke the research skill, explicitly use the best trustworthy fallback research capability available and continue to enforce this contract.

Before dispatch, tell the user briefly:

- which decision is paused;
- what will be researched;
- why that fact matters.

Do not say "research is running", "I am researching now", "the research has started", or equivalent wording until the harness has actually accepted/started the research call.

Do not ask the user for public documentation links that the Agent can locate itself.

Prefer first-party sources, official documentation, specifications, official repositories, and first-party APIs.

If the relevant source is private/internal and cannot be discovered, ask only for the minimum access information needed.


## Dispatch verification

Treat research dispatch as its own verified state transition.

A run is `researching` only after the harness confirms that the research task/call was accepted or started. Evidence may be a task/run id, an accepted/running state, or another harness-equivalent acknowledgement.

If dispatch fails, is rejected, or never actually happens:

- do not tell the user it is underway;
- keep the decision `unresolved`;
- state that the research did not start;
- retry only when useful or let the user continue without it.

A sentence announcing future intent (for example, "我先去调研") is not dispatch evidence.

## Research artifact isolation

Research evidence created before SPEC approval should not silently become part of the knowledge base being designed.

Prefer a session-scoped, harness scratch, operating-system temporary, or existing research-notes location **outside the intended knowledge-base implementation destination**.

If the research skill/harness requires project-local output and no separate scratch location is available:

- place it in a clearly identified pre-implementation research location;
- treat it as research evidence, not knowledge-base implementation;
- do not automatically list it as a final KB deliverable;
- make any approval-gate statement accurate by acknowledging that research notes may already exist.

## Completion verification

Never treat a research run as complete merely because it started or produced partial messages.

A research result is usable only when all applicable conditions are true:

1. the research process finished successfully;
2. the expected result or artifact exists;
3. the main `kb-init` Agent has actually read the result;
4. the result addresses the framed research question;
5. important claims are supported by trustworthy sources.

If the research process is stopped, cancelled, interrupted, fails, or produces no usable artifact:

- keep the paused decision `researching` or `unresolved`;
- tell the user the research did not complete;
- do not summarize partial work as final findings;
- do not continue downstream decisions as if the fact were settled;
- offer to retry, narrow the question, or leave the item unresolved.

## After research

Return to the paused decision.

Summarize in this order:

1. verified facts;
2. important limitations or uncertainty;
3. what those facts mean for the current decision;
4. the Agent's recommendation, if useful;
5. ask the user to decide or continue exploring.

Research never settles the user's decision automatically.

Research also does not silently overwrite a decision the user already settled.

If new evidence conflicts with an earlier user decision:

1. state the conflict explicitly;
2. explain what changed or what the research suggests;
3. reopen that specific decision;
4. let the user keep or revise the earlier choice.

If the result invalidates downstream decisions already discussed, reopen them.
