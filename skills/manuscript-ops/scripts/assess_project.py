#!/usr/bin/env python3
"""Read-only manuscript route assessor. Writes JSON to stdout only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from manuscript_ops_core import ContractError, build_routing_snapshot, dump_json, load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Exact project root")
    parser.add_argument("--answers", type=Path, help="Optional routing answers JSON")
    parser.add_argument("--captured-at", help="Override RFC 3339 timestamp for reproducible tests")
    parser.add_argument("--max-files", type=int, default=5000, help="Bound metadata scan")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        answers = load_json(args.answers) if args.answers else None
        snapshot = build_routing_snapshot(
            args.root,
            answers=answers,
            captured_at=args.captured_at,
            max_files=args.max_files,
        )
    except (ContractError, OSError) as exc:
        print(f"assessment error: {exc}", file=sys.stderr)
        return 2
    print(dump_json(snapshot, pretty=not args.compact))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

