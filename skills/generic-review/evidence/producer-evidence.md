# Generic Review producer evidence

This is Producer evidence for Ticket 10. It is not independent review evidence
and does not issue an admission, package, project, or release verdict.

## Scope

- Package: `skills/generic-review`
- Invocation: model-invoked; `agents/openai.yaml` permits implicit invocation.
- Owned product surfaces: the package contract, metadata, output schema, tests,
  and this record. The repository-level Reviewer Contract is separately owned
  by Ticket 10.
- Ownership: original first-party capability; no upstream code, asset, runtime
  dependency, installer, network connector, or executable product script.

## Test seam and planned evidence

The deterministic seam is a candidate Markdown report. The focused suite
validates successful normalized findings, explicit no-findings results,
malformed fields, previous-finding rechecks, duplicate links, malicious
mutation/final-verdict output, invocation metadata, and a clean copied package.
It rejects report text that attempts target edits, repair instructions, or
`PASS`/`FAIL`/`BLOCKED` verdicts.

Executed after implementation in the local Python `3.9.6` environment:

```text
python3 -m unittest discover -s skills/generic-review/tests -p 'test_*.py' -v

Ran 14 tests in 0.006s
OK
```

`python3 -m compileall -q skills/generic-review` and `git diff --check` also
completed successfully. The suite includes the clean copied-package scenario;
this run is Producer evidence only.

## Evidence classification and limitations

- **Structural:** package files, metadata, internal link, and schema inspected
  by the contract tests.
- **Behavioral:** deterministic report fixtures exercise the declared output,
  recheck, malformed, and read-only rules.
- **Invocation:** matching frontmatter and host policy are asserted.
- **Installation/discovery:** clean copied package evidence checks only that
  the package is self-contained; it is not a fresh host installation.

No live model-host invocation, independent Evaluator, full `review-loop`
acceptance, catalog synchronization, or final `PASS`/`FAIL`/`BLOCKED` verdict
is claimed. The Controller owns shared integration and final admission path.
