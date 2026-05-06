"""Prepare or append short Harness cycle log entries."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import dump_json, find_project_root, parse_date_text, read_text, rel, today_cycle_path, write_text


def _items(items: list[str], fallback: str) -> list[str]:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return cleaned or [fallback]


def _lines(label: str, items: list[str]) -> list[str]:
    first, *rest = items
    lines = [f"- {label}: {first}"]
    lines.extend(f"  - {item}" for item in rest)
    return lines


def build_entry(title: str, changed: list[str], verified: list[str], remaining: list[str], now: datetime | None = None) -> str:
    time_text = (now or datetime.now()).strftime("%H:%M")
    lines = [
        f"## {time_text} {title}",
        "",
        *_lines("Changed", _items(changed, "needs update")),
        *_lines("Verified", _items(verified, "needs update")),
        *_lines("Remaining", _items(remaining, "none")),
    ]
    return "\n".join(lines) + "\n"


def append_entry(path: Path, entry: str) -> None:
    existing = read_text(path)
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing:
        existing += "\n"
    write_text(path, existing + entry)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a short Harness cycle log entry.")
    parser.add_argument("title", help="Cycle title.")
    parser.add_argument("--changed", action="append", default=[], help="What changed. Can be repeated.")
    parser.add_argument("--verified", action="append", default=[], help="What was verified. Can be repeated.")
    parser.add_argument("--remaining", action="append", default=[], help="Remaining work or risk. Can be repeated.")
    parser.add_argument("--root", type=Path, default=None, help="Project root. Defaults to nearest Harness root.")
    parser.add_argument("--date", default="", help="Cycle date as YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--write", action="store_true", help="Append to Harness/cycles/YYYY-MM-DD.md.")
    args = parser.parse_args()
    root = find_project_root(args.root)
    path = today_cycle_path(root)
    if args.date:
        try:
            path = root / "Harness" / "cycles" / f"{parse_date_text(args.date)}.md"
        except ValueError:
            parser.error("--date must be in YYYY-MM-DD format")
    entry = build_entry(args.title, args.changed, args.verified, args.remaining)
    result = {"root": str(root), "path": rel(path, root), "write": args.write, "entry": entry, "status": "dry_run"}
    if args.write:
        append_entry(path, entry)
        result["status"] = "written"
    print(dump_json(result) if args.json else (f"Appended cycle entry: {path}" if args.write else entry.rstrip() + f"\n\nDry run only. Add --write to append to {path}"))


if __name__ == "__main__":
    main()
