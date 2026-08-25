# Agent-Skill Profile

Select this Profile when the frozen target is an installable Agent Skill
package: a directory containing a `SKILL.md`, optional agent metadata, and any
references, scripts, templates, or assets that its contract requires. This
Profile is for accepting a reusable Skill at its installation, discovery,
invocation, behavior, and interaction boundaries. It adds package-specific
review inputs to the generic Core; it does not replace the Core's finding
identity and disposition lifecycle, repair boundary, state machine, independence
requirement, round limit, or final verdict.

## Review axes

Review every applicable axis independently and retain the axis on each finding:

1. **Package structure and discoverability** — the package has valid required
   frontmatter, an honest description and invocation policy, a complete
   declared resource tree, and links that resolve from the installed package.
2. **Installation and fresh discovery** — a clean installation contains only
   the intended package, preserves its resources and metadata, is discoverable
   by the declared host, and does not rely on undeclared local files or stale
   runtime state.
3. **Invocation contract and boundaries** — user-invoked versus model-invoked
   behavior is explicit and observed; trigger and non-trigger cases are clear;
   inputs, outputs, authority, and stop conditions prevent accidental execution
   of another user-invoked Skill or an out-of-scope workflow.
4. **Reusable behavior and method fidelity** — a focused success scenario,
   boundary scenario, and failure or missing-dependency scenario exercise the
   public Skill contract; the package preserves the source-backed method,
   corrections, decisions, and limitations rather than generic headings.
5. **Interaction and composition seams** — hand-offs to upstream, first-party,
   or third-party Skills use explicit inputs and evidence; the package neither
   duplicates another authority nor claims a specialist or downstream final
   verdict; unsupported environments produce a precise stop or recommendation.
6. **Executable artifact quality** — when the package includes scripts or other
   executable resources, focused assertion-bearing tests cover changed success,
   boundary, and failure behavior, negative or adversarial fixtures cover
   relevant misuse, and a separate `code-review` supplies Standards and Spec
   evidence. A package without executables records that this axis is not
   applicable and why.

## Evidence requirements

The Agent-Skill review packet must include the following, each with exactly one
primary label from the generic [Evidence Protocol](../evidence-protocol.md):

- the frozen target package revision, acceptance source, invocation type, and
  declared resource tree;
- structural inspection of `SKILL.md`, `agents/openai.yaml` when present,
  required directories, frontmatter, resource references, and resolved
  relative Markdown links;
- a clean-copy installation and discovery observation, including exact command
  or reproducible action, installed path, package metadata, and any host
  limitations;
- invocation evidence for a positive trigger, a non-trigger or boundary case,
  and the rule that another user-invoked Skill is recommended rather than
  silently executed;
- behavioral evidence for at least one successful method path, one boundary or
  no-op path, and one failure or missing-dependency path, with expected and
  observed outcomes;
- interaction evidence for every declared hand-off, including the input,
  output, authority owner, stop condition, and preservation of evidence;
- for executable resources, focused automated tests with non-zero assertions,
  a relevant negative or adversarial result, and separate
  `code-review` Standards and Spec reports. These specialist reports are
  `review` evidence and candidate findings only;
- fresh independent Evaluator evidence with its raw Core independence value and
  the Agent-Skill-normalized value preserved. Missing independent context is a
  blocker, not a weaker acceptance claim.

Evidence items use only the protocol's labels (`source`, `structural`,
`behavioral`, `installation`, `invocation`, `runtime`, `manual`, or `review`). A
fixture or static keyword check cannot be relabeled as runtime evidence.

## Specialist reviewers

Use read-only specialists as applicable for package structure and links,
installer/discovery behavior, invocation boundaries, method/interaction
behavior, and executable code review. `code-review` remains the software
specialist for scripts; it reports separate Standards and Spec findings and
never edits the package or issues the Program's final verdict. Every specialist
observation is a candidate for the generic finding schema. Candidate
dispositions remain `confirmed`, `rejected`, `duplicate`, or `out-of-scope`.
The review-loop Core validates each candidate and owns the final `PASS`, `FAIL`,
or `BLOCKED`.

## Severity guidance

Use impact against the frozen Skill package baseline, not estimated repair
effort:

- **Critical** — unsafe or unauthorized execution, a package that can corrupt
  user data or expose secrets, or an invocation boundary that makes the Skill
  unusable or dangerous for its accepted purpose;
- **High** — the package cannot install or be discovered, required method or
  resource is absent, invocation type is wrong, a declared interaction silently
  crosses authority boundaries, or required executable evidence is missing;
- **Medium** — a material trigger, behavior, dependency, link, compatibility,
  or test-quality gap that must be resolved before `PASS` unless the Charter
  records an eligible risk acceptance;
- **Low** — a limited-impact documentation, diagnostic, or maintainability
  observation that does not block `PASS` unless the Charter says otherwise.

Severity is impact against the frozen target. It does not authorize a new
capability, invocation policy, dependency, host, or architecture decision.

## Acceptance conditions

The Core may ask its fresh Evaluator to consider `PASS` only when:

- the exact package revision, acceptance source, Profile, and invocation policy
  are frozen and agree;
- structure, metadata, links, and declared resources are valid;
- a clean installation is discoverable and the package does not depend on
  undeclared files or prior `.review-loop/` state;
- positive trigger, non-trigger/boundary, and invocation-type observations match
  the Skill contract, including no automatic invocation of another user-invoked
  Skill;
- success, boundary, failure or missing-dependency, and all required
  interaction-seam scenarios have accurate evidence labels and expected versus
  observed outcomes;
- executable packages have assertion-bearing focused tests, relevant negative
  or adversarial coverage, and separate Standards/Spec `code-review` evidence;
  non-executable packages have an explicit applicability record;
- every confirmed blocking finding is resolved under its stable ID with fresh
  per-ID repair evidence, and any accepted Medium/Low risk has the user's exact
  post-review statement, actor, and timestamp; and
- a genuinely fresh Evaluator records criterion-by-criterion judgment. The
  generic Core records the final verdict.

## Artifact-specific failure cases

Preserve specialist observations and apply the Core's generic `FAIL` or
`BLOCKED` stopping rule when:

- `SKILL.md`, required metadata, acceptance source, package revision, or
  declared resource is missing, stale, contradictory, or cannot identify the
  reviewed scope;
- installation or discovery requires an undeclared path, previous runtime
  state, unavailable host capability, or an unverified command;
- trigger metadata and observed invocation disagree, the package executes a
  different user-invoked Skill without an explicit user choice, or its hand-off
  omits the authority owner, required input, output, or stop condition;
- a method is only a passive summary, generic scaffold, or no-op test and does
  not demonstrate reusable success, boundary, and failure behavior;
- required scripts lack assertion-bearing focused tests, relevant negative or
  adversarial coverage, or independent `code-review` evidence, or a specialist
  summary is presented as the Program verdict;
- a dependency, permission, network, or host condition needed for an accepted
  scenario is unavailable and the smallest safe unblock is not recorded; or
- a proposed repair expands the frozen capability, invocation, host, source,
  dependency, or architecture, or requires new authority or tickets. Do not
  weaken this Profile to make such a target pass.

The generic Core, not this Profile or a package specialist, owns finding
identity, dispositions, repair rounds, state transitions, independence stops,
and final `PASS`, `FAIL`, or `BLOCKED`.

## Selection record

Record `Profile: agent-skill` in the Acceptance Charter and identify the
package revision, host/discovery target, invocation type, and reason this
Profile applies. A later request to change the package capability, invocation
policy, supported host, or required dependency is a baseline change requiring
the Core's approved change process.
