# Migration note

The former `review-loop` final-acceptance system (frozen baseline / Charter,
evidence labels, finding registry dispositions, `PASS`/`FAIL`/`BLOCKED`,
Profile selection, durable `.review-loop/charter.md|verdict.md|changes.md`)
was migrated to `project-review` without rewrite. This package retains only
the `review → findings → repair → re-review` convergence engine.

New project final-acceptance consumers must use `project-review`. See
`project-review`'s `references/migration.md` for the full mapping.