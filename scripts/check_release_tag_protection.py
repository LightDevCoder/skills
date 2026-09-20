#!/usr/bin/env python3
"""Remote Release Tag Protection Verification Gate.

Verifies that GitHub repository rulesets remotely enforce tag immutability:
1. Ruleset target is 'tag'.
2. Ruleset enforcement is 'active'.
3. Pattern covers 'refs/tags/v*'.
4. Rules restrict 'deletion'.
5. Rules restrict 'update'.

Supports pure local verification via --fixture for hermetic CI and offline tests.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, NamedTuple


class ProtectionCheckResult(NamedTuple):
    passed: bool
    status: str
    message: str
    details: dict[str, Any] | None = None


def pattern_excludes_release_namespace(pattern: str, target_pattern: str = "refs/tags/v*") -> bool:
    """Check if an exclude pattern removes any tags from the target release namespace."""
    if pattern == target_pattern or pattern == "refs/tags/*" or pattern == "*":
        return True
    if pattern.startswith("refs/tags/v"):
        return True
    # Test sample release tags across common version forms
    sample_tags = ["refs/tags/v0.0.0", "refs/tags/v0.2.3", "refs/tags/v0.2.4", "refs/tags/v1.0.0", "refs/tags/v9.9.9"]
    for sample in sample_tags:
        if fnmatch.fnmatch(sample, pattern):
            return True
    return False


def verify_ruleset_payload(
    rulesets_data: list[dict[str, Any]] | dict[str, Any],
    target_pattern: str = "refs/tags/v*",
) -> ProtectionCheckResult:
    """Evaluate ruleset JSON structure for required tag protection rules."""
    rulesets: list[dict[str, Any]]
    if isinstance(rulesets_data, dict):
        # Could be a single detailed ruleset or a wrapper
        if "rulesets" in rulesets_data and isinstance(rulesets_data["rulesets"], list):
            rulesets = rulesets_data["rulesets"]
        else:
            rulesets = [rulesets_data]
    elif isinstance(rulesets_data, list):
        rulesets = rulesets_data
    else:
        return ProtectionCheckResult(
            passed=False,
            status="BLOCKED",
            message="Invalid ruleset data format: expected list or object.",
        )

    if not rulesets:
        return ProtectionCheckResult(
            passed=False,
            status="BLOCKED",
            message="No repository rulesets found on remote.",
        )

    for rs in rulesets:
        # Check target
        target = rs.get("target")
        if target != "tag":
            continue

        # Check enforcement
        enforcement = rs.get("enforcement")
        if enforcement != "active":
            continue

        # Check ref conditions
        conditions = rs.get("conditions", {})
        ref_name = conditions.get("ref_name", {})
        includes = ref_name.get("include", [])
        excludes = ref_name.get("exclude", [])

        # Strict canonical namespace check: requires explicit target_pattern
        if target_pattern not in includes:
            continue

        # Exclude check: forbid any exclusion that impacts release namespace
        for ex in excludes:
            if pattern_excludes_release_namespace(ex, target_pattern):
                return ProtectionCheckResult(
                    passed=False,
                    status="BLOCKED",
                    message=(
                        f"Ruleset '{rs.get('name', 'unnamed')}' (id: {rs.get('id')}) contains exclude pattern '{ex}' "
                        f"which excludes tags from protected namespace '{target_pattern}'. Release tag namespace must be immutable."
                    ),
                    details=rs,
                )

        # Check rules: update and deletion restrictions
        rules = rs.get("rules", [])
        rule_types = {r.get("type") for r in rules if isinstance(r, dict)}

        has_deletion = "deletion" in rule_types
        has_update = "update" in rule_types

        if not has_deletion and not has_update:
            continue

        missing_rules: list[str] = []
        if not has_deletion:
            missing_rules.append("deletion")
        if not has_update:
            missing_rules.append("update")

        if missing_rules:
            return ProtectionCheckResult(
                passed=False,
                status="BLOCKED",
                message=f"Ruleset '{rs.get('name', 'unnamed')}' (id: {rs.get('id')}) is missing rule(s): {', '.join(missing_rules)}.",
                details=rs,
            )

        # Check bypass policy - must fail closed if bypass info is missing or non-compliant
        if "bypass_actors" not in rs or not isinstance(rs["bypass_actors"], list):
            return ProtectionCheckResult(
                passed=False,
                status="BLOCKED",
                message=(
                    f"Ruleset '{rs.get('name', 'unnamed')}' (id: {rs.get('id')}) is missing bypass_actors information. "
                    "Release tags require verified empty bypass_actors ([])."
                ),
                details=rs,
            )

        bypass_actors = rs["bypass_actors"]
        if bypass_actors != []:
            return ProtectionCheckResult(
                passed=False,
                status="BLOCKED",
                message=(
                    f"Ruleset '{rs.get('name', 'unnamed')}' (id: {rs.get('id')}) allows bypass actors: {bypass_actors}. "
                    "Release tags must be permanently immutable with zero bypass actors."
                ),
                details=rs,
            )

        if "current_user_can_bypass" not in rs or rs["current_user_can_bypass"] != "never":
            current_user_bypass = rs.get("current_user_can_bypass")
            return ProtectionCheckResult(
                passed=False,
                status="BLOCKED",
                message=(
                    f"Ruleset '{rs.get('name', 'unnamed')}' (id: {rs.get('id')}) has invalid current_user_can_bypass ('{current_user_bypass}'). "
                    "Release tags require current_user_can_bypass='never'."
                ),
                details=rs,
            )

        # All requirements satisfied!
        details = {
            "id": rs.get("id"),
            "name": rs.get("name"),
            "target": target,
            "enforcement": enforcement,
            "patterns": includes,
            "excludes": excludes,
            "rules": sorted(rule_types),
            "bypass": "none (enforced)",
            "updated_at": rs.get("updated_at") or rs.get("created_at"),
        }
        return ProtectionCheckResult(
            passed=True,
            status="PASS",
            message=(
                f"Active tag protection ruleset confirmed (id: {rs.get('id')}, name: '{rs.get('name')}'): "
                f"enforces update and deletion restrictions on {includes} with zero bypass actors and current_user_can_bypass='never'."
            ),
            details=details,
        )

    return ProtectionCheckResult(
        passed=False,
        status="BLOCKED",
        message=f"No active tag ruleset found covering '{target_pattern}' with update and deletion restrictions.",
    )


def fetch_remote_rulesets(repo: str = "LightDevCoder/skills") -> list[dict[str, Any]]:
    """Fetch rulesets using gh CLI or GitHub REST API."""
    # 1. Try gh CLI if available
    gh_path = shutil.which("gh")
    if gh_path:
        proc = subprocess.run(
            [gh_path, "api", f"repos/{repo}/rulesets"],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            list_data = json.loads(proc.stdout)
            full_rulesets: list[dict[str, Any]] = []
            for item in list_data:
                rs_id = item.get("id")
                if rs_id:
                    detail_proc = subprocess.run(
                        [gh_path, "api", f"repos/{repo}/rulesets/{rs_id}"],
                        capture_output=True,
                        text=True,
                    )
                    if detail_proc.returncode == 0:
                        full_rulesets.append(json.loads(detail_proc.stdout))
                    else:
                        full_rulesets.append(item)
                else:
                    full_rulesets.append(item)
            return full_rulesets

    # 2. Try direct HTTP with token
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "LightDevCoder-ReleaseTagProtectionCheck",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/rulesets", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            list_data = json.loads(resp.read().decode("utf-8"))
            full_rulesets = []
            for item in list_data:
                rs_id = item.get("id")
                if rs_id:
                    detail_req = urllib.request.Request(
                        f"https://api.github.com/repos/{repo}/rulesets/{rs_id}",
                        headers=headers,
                    )
                    with urllib.request.urlopen(detail_req, timeout=10) as dresp:
                        full_rulesets.append(json.loads(dresp.read().decode("utf-8")))
                else:
                    full_rulesets.append(item)
            return full_rulesets
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API returned HTTP {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to connect to GitHub API: {e.reason}") from e


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify remote GitHub release tag ruleset protection.")
    parser.add_argument("--repo", default="LightDevCoder/skills", help="Target GitHub repository (default: LightDevCoder/skills).")
    parser.add_argument("--pattern", default="refs/tags/v*", help="Target tag pattern (default: refs/tags/v*).")
    parser.add_argument("--fixture", help="Path to local ruleset JSON fixture for hermetic testing.")

    args = parser.parse_args()

    print(f"=== Remote Tag Protection Guard ===")
    print(f"Target Repository: {args.repo}")
    print(f"Required Pattern:  {args.pattern}")
    print("------------------------------------")

    if args.fixture:
        fixture_path = Path(args.fixture)
        if not fixture_path.is_file():
            print(f"RESULT: BLOCKED — Fixture file not found: {args.fixture}")
            return 1
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        res = verify_ruleset_payload(data, target_pattern=args.pattern)
    else:
        try:
            rulesets = fetch_remote_rulesets(args.repo)
            res = verify_ruleset_payload(rulesets, target_pattern=args.pattern)
        except Exception as e:
            print(f"RESULT: BLOCKED — Unable to fetch remote rulesets from GitHub API: {e}")
            return 1

    print(f"[{res.status}] {res.message}")
    if res.details:
        print("Verified Ruleset Details:")
        print(f"  - ID:          {res.details.get('id')}")
        print(f"  - Name:        {res.details.get('name')}")
        print(f"  - Target:      {res.details.get('target')}")
        print(f"  - Enforcement: {res.details.get('enforcement')}")
        print(f"  - Patterns:    {res.details.get('patterns')}")
        print(f"  - Rules:       {res.details.get('rules')}")
        print(f"  - Updated at:  {res.details.get('updated_at')}")

    print("------------------------------------")
    if res.passed:
        print("RESULT: PASS — Remote release tags are actively protected against deletion and update.")
        return 0
    else:
        print("RESULT: BLOCKED — Tag publication is forbidden without active remote tag protection.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
