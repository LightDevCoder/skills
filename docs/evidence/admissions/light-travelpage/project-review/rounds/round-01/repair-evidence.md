# Repairs

- Backup restore now rejects incomplete snapshot shape before any network operation.
- Browser and server share the extracted fixed currency catalog; unsupported codes fail before any mutation.
- Ledger conflict reloads the observed snapshot without replacing the active form. Explicit refresh does the same for an editor; retry uses the fresh revision. Deleted edited bills require an explicit new-record decision.
- Retry reports the adapters actually recovered. Ledger handles only its own recovered mutation and uses form edit generation to avoid clearing newer input.
- Actual Chrome form login exposed `Referrer-Policy: no-referrer` producing `Origin: null`. Changed policy to `same-origin` while retaining strict origin validation. Local native browser login and homepage AX observation succeeded before the Mac became unavailable.

Current regression result: 17 Node tests passed, including three Happy DOM form tests. DOM simulation is not visual or actual-browser evidence. Remote D1 checks in `evidence/remote-results.json` predate these repairs and must be rerun after deployment.
