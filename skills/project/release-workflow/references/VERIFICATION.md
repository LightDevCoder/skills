# Fresh-install verification procedure

Run against the **published tag** in a fresh destination, with the source
checkout unavailable to the discovery step. Host refresh is host-specific and
not claimed; CLI discovery is the check that runs without a source checkout.

## Setup

```bash
npx --yes skills --version   # record the exact CLI version
```

Create a disposable empty temporary project for each destination class. Do not
point the CLI at a path that contains the repository checkout.

## Command matrix — all four variants

| Form | Whole collection | Per-Skill |
| --- | --- | --- |
| Generic `latest` | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `npx --yes skills add LightDevCoder/skills --skill <name> --yes --copy --agent '*'` |
| Pinned `#vX.Y.Z` | `npx --yes skills add LightDevCoder/skills#vX.Y.Z --yes --copy --agent '*'` | `npx --yes skills add LightDevCoder/skills#vX.Y.Z --skill <name> --yes --copy --agent '*'` |

An unqualified source follows the repository's default revision; `#vX.Y.Z`
pins the Git revision. Neither is a claim about a future default revision;
re-run discovery against the fresh destination for the resolved content.

## Steps per variant

1. Record `npx --yes skills --version` and the exact command.
2. Run the install; record exit code and package count under the destination's
   `.agents/skills/` (whole: exactly the admitted package set; per-Skill:
   exactly one).
3. Run `npx --yes skills list` from the fresh destination; strip ANSI codes if
   needed. Record that the package(s) are listed and that no source checkout is
   present.
4. Run one success and one boundary/missing-dependency smoke against the
   installed package (e.g. the recap output contract, or the review-loop
   package byte-identical to source).
5. Repeat the same command; record whether it is a no-op overwrite or reports
   a duplicate.

## Evidence fields to record

- exact command and CLI version;
- repository URL and released commit or tag;
- host, installation scope, and resolved destination class (never absolute
  private paths, tokens, or usernames);
- fresh-environment discovery without the source checkout;
- success, boundary, invocation, and missing-dependency smoke results;
- any manual fallback used;
- known limitations.

## Known pitfalls

- ANSI color codes can make `skills list` grep appear empty; strip them.
- Transient GitHub TLS handshake failures happen over SChannel; retry the
  command (a success run is the recorded result).
- A repeat install that reports `overwrites:` is a no-op overwrite, not a
  defect.
- Structural validation or a source-checkout scan is not installation
  evidence. The collection-discovery script is a structural cross-reference
  check; it does not replace fresh host installation.
