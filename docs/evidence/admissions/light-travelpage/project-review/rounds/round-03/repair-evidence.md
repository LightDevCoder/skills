# Final known-path repair

retryAll returns each confirmed POST snapshot with its adapter. Ledger consumes it directly; a later GET failure cannot prevent receiving the confirmed state or clearing only the submitted draft. Batch retries return both successes and per-adapter errors so a different failed adapter cannot suppress an already-confirmed result. Added focused tests for both paths.

23 Node tests pass (17 core/6 Happy DOM). The final changes require a later clean independent review before admission; do not report these tests as that review.
