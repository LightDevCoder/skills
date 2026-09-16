# Decision-map examples

## Example 1 — Charted map (new effort)

User: `$decision-map We're going to rebuild the skills repo with a new
workflow architecture.`

**Destination** (settled via quick `socratic`):
> A refactor plan and initial slices that leave `LightDevCoder/skills` as a
> composable workflow system with inspectable clarification → planning →
> execution → review stages.

**map.md**

```markdown
## Destination

A refactor plan and initial slices that leave LightDevCoder/skills composable
and traceable through clarification, planning, execution, and review.

## Notes

Domain: dev-tooling. Skills to consult: socratic, research, prototype,
to-questionnaire. Preference: keep SKILL.md concise, details in references/.

## Decisions so far

(none yet)

## Not yet specified

- Execution routing and agent capability mapping (needs prototype vs Sol Advisor)
- Final acceptance ownership between review-loop and project-review

## Out of scope

- Hero image asset choice — separate asset pass
```

**Child tickets** (after second pass wiring):

- `01-domain-boundary.md` — Type: grilling — Status: open — Blocked by:
- `02-clarification-family-shape.md` — Type: grilling — Status: open — Blocked by:
- `03-execution-model.md` — Type: prototype — Status: open — Blocked by: 01
- `04-agent-availability-research.md` — Type: research — Status: open — Blocked by:

Frontier is then `01`, `02`, `04` (unblocked, unclaimed).

## Example 2 — Resolve one ticket and graduate fog

Session: `$decision-map .scratch/skills-refactor` (no ticket arg — takes frontier)

1. Claims `01-domain-boundary.md` (`Status: claimed`).
2. Runs `socratic` to settle domain terminology; records:
   ```markdown
   ## Answer
   Decision: domain bounded to workflow composition; glossary terms pinned.
   Next: see map Decisions so far.
   ```
3. Status → `resolved`, appends to map:
   ```markdown
   ## Decisions so far
   - `Domain boundary → issues/01-domain-boundary.md` — workflow-scoped, glossary pinned
   ```
4. Graduates fog: `Execution routing` patch becomes ticket
   `05-agent-config-design.md` (Type: prototype, Blocked by: 03). Removes that
   patch from `Not yet specified`.

## Example 3 — Out of scope ruling

While resolving `03-execution-model.md`, the answer reveals that building a
custom GPU scheduler is beyond this refactor's destination.

- Ticket `03` is resolved with the scheduler explicitly deferred.
- Add to map:
  ```markdown
  ## Out of scope
  - Custom GPU scheduler — requires separate effort beyond composable workflow; see 03.
  ```

Ticket never graduates; `Decisions so far` does not list out-of-scope items as
steps on the route.

## Example 4 — Handoff to project-spec

After several sessions, all tickets resolved and fog empty:

```markdown
## Decisions so far
- `Domain boundary → issues/01-domain-boundary.md` — ...
- `Clarification family shape → issues/02-clarification-family-shape.md` — socratic base + three entries
- ...

## Not yet specified

(empty)

## Out of scope

- Custom GPU scheduler — see above
```

Recommend: `Next: $project-spec using the map's Decisions so far and ticket
answers; no new clarification needed.` Stop.
