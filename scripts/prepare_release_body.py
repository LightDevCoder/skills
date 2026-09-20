#!/usr/bin/env python3
"""Prepare GitHub Release Body.

Transforms local evidence Markdown (e.g. docs/evidence/releases/vX.Y.Z/RELEASE_NOTES.md)
into a GitHub Release-compatible body:
1. Detects sibling relative links (e.g. RELEASE_NOTES.zh-CN.md, RELEASE_MANIFEST.md, RELEASE_RECEIPT.md).
2. Expands them to canonical full GitHub URLs (https://github.com/<repo>/blob/<branch>/docs/evidence/releases/<tag>/<file>),
   preventing 404 errors on GitHub Release pages which evaluate relative links against repository root.
3. Outputs to stdout or an output file suitable for `gh release create --notes-file`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def transform_release_notes_for_web(
    text: str,
    tag: str,
    repo: str = "LightDevCoder/skills",
    branch: str = "main",
) -> str:
    """Expand sibling relative links to full repository URLs for GitHub Release rendering."""
    base_url = f"https://github.com/{repo}/blob/{branch}/docs/evidence/releases/{tag}"

    # Match markdown links: [text](target)
    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()

        # Keep absolute URLs, anchors, mailto unchanged
        if re.match(r"^(?:https?://|mailto:|#)", target, re.IGNORECASE):
            return match.group(0)

        # If already an expanded repo path from root
        if target.startswith("docs/evidence/releases/"):
            return f"[{label}](https://github.com/{repo}/blob/{branch}/{target})"

        # Sibling files in the same release evidence folder (e.g. RELEASE_NOTES.zh-CN.md, RELEASE_MANIFEST.md)
        cleaned_target = target.lstrip("./")
        return f"[{label}]({base_url}/{cleaned_target})"

    # Pattern: [label](target)
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    return pattern.sub(replace_link, text)


def validate_release_body_links(body: str, tag: str) -> tuple[bool, list[str]]:
    """Validate that a release body does not contain bare relative links that 404 on GitHub Releases."""
    errors: list[str] = []
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for match in pattern.finditer(body):
        label = match.group(1)
        target = match.group(2).strip()

        # Absolute URLs and anchors are safe
        if re.match(r"^(?:https?://|mailto:|#)", target, re.IGNORECASE):
            continue

        # Any relative link without scheme will be evaluated against repository root by GitHub Releases
        errors.append(
            f"Bare relative link detected: [{label}]({target}). "
            f"GitHub Releases evaluates relative links against repository root, causing 404 Not Found. "
            f"Use full URL: https://github.com/<repo>/blob/main/docs/evidence/releases/{tag}/{target.lstrip('./')}"
        )

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a GitHub Release body from release notes.")
    parser.add_argument("--tag", required=True, help="Release tag (e.g. v0.2.4).")
    parser.add_argument("--repo", default="LightDevCoder/skills", help="Target GitHub repository (default: LightDevCoder/skills).")
    parser.add_argument("--branch", default="main", help="Target branch for links (default: main).")
    parser.add_argument("--input", default=None, help="Path to input release notes file (default: docs/evidence/releases/<tag>/RELEASE_NOTES.md).")
    parser.add_argument("--output", default=None, help="Path to write transformed release body (default: stdout).")
    parser.add_argument("--validate-only", action="store_true", help="Only validate release body for broken relative links.")

    args = parser.parse_args()

    input_path = Path(args.input) if args.input else (REPO_ROOT / "docs" / "evidence" / "releases" / args.tag / "RELEASE_NOTES.md")
    if not input_path.is_file():
        print(f"ERROR: Input release notes file not found: {input_path}", file=sys.stderr)
        return 1

    content = input_path.read_text(encoding="utf-8")

    if args.validate_only:
        valid, errors = validate_release_body_links(content, args.tag)
        if not valid:
            print(f"Validation FAILED for {input_path}:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        print("Validation PASSED: All links are safe.")
        return 0

    transformed = transform_release_notes_for_web(
        text=content,
        tag=args.tag,
        repo=args.repo,
        branch=args.branch,
    )

    valid, errors = validate_release_body_links(transformed, args.tag)
    if not valid:
        print(f"ERROR: Transformed release body still has invalid links:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(transformed, encoding="utf-8")
        print(f"Successfully prepared release body at: {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(transformed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
