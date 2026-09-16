#!/usr/bin/env python3
"""Return the next unused manuscript date version without changing the project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from manuscript_ops_core import ContractError, next_date_version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat().replace("-", "."))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--existing", action="append", default=[])
    return parser.parse_args()


def collect_existing(root: Path, explicit: list[str]) -> list[str]:
    values = list(explicit)
    gates = root.resolve() / ".manuscript-ops" / "gates"
    if gates.is_dir():
        for path in gates.rglob("*"):
            if not path.is_file():
                continue
            values.append(path.name)
            if path.suffix.lower() == ".json":
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if isinstance(data, dict) and isinstance(data.get("date_version"), str):
                    values.append(data["date_version"])
    if (root / ".jj").exists():
        command = [
            "jj",
            "--ignore-working-copy",
            "-R",
            str(root.resolve()),
            "bookmark",
            "list",
        ]
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            result = None
        if result and result.returncode == 0:
            values.extend(result.stdout.splitlines())
    return values


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"version error: project root does not exist: {root}", file=sys.stderr)
        return 2
    try:
        print(next_date_version(args.date, collect_existing(root, args.existing)))
    except ContractError as exc:
        print(f"version error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
