"""Build a compact handoff brief for another agent."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import dump_json, find_project_root, harness_dir, markdown_list_items, read_text, rel, today_cycle_path, write_text
from harness_context import build_context
from harness_diff_guard import build_report, changed_path_from_status


def _tail(text: str, limit: int = 30) -> list[str]:
    return [line.rstrip() for line in text.splitlines()][-limit:]


def build_handoff(root: Path, request: str = "") -> str:
    harness = harness_dir(root)
    context = build_context(root)
    diff = build_report(root)
    next_items = markdown_list_items(read_text(harness / "next.md"), limit=8)
    lines = [
        "# Harness Handoff",
        "",
        f"- Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- Root: {root}",
        f"- Request: {request or 'needs update'}",
        f"- Project: {context['project']['name'] or 'not configured'}",
        f"- Package: {context['project']['package_json']}",
        f"- Git available: {diff['git_available']}",
        f"- Change mode: {diff['mode']}",
        f"- Changed paths: {diff['changed_count'] if diff['change_list_reliable'] else 'limited scan only'}",
        f"- Risk signals: {diff['risk_count']}",
        "",
        "## Read First",
    ]
    lines.extend(f"- {item}" for item in context["recommended_first_reads"])
    lines.extend(["", "## Next Work"])
    lines.extend(f"- {item}" for item in next_items) if next_items else lines.append("- none")
    lines.extend(["", "## Changed Files"])
    lines.extend(f"- {changed_path_from_status(item)}" for item in diff["changed"][:40]) if diff["changed"] else lines.append("- none detected")
    lines.extend(["", "## Risks"])
    lines.extend(f"- [{item['level']}] {item['path']}: {item['reason']}" for item in diff["risks"]) if diff["risks"] else lines.append("- none")
    lines.extend(["", "## Today Cycle Tail"])
    tail = _tail(read_text(today_cycle_path(root)), 30)
    lines.extend(tail) if tail else lines.append("- no cycle log for today")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a compact Harness handoff brief.")
    parser.add_argument("--root", type=Path, default=None, help="Project root. Defaults to nearest Harness root.")
    parser.add_argument("--request", default="", help="Current user request or handoff reason.")
    parser.add_argument("--output", type=Path, default=None, help="Output path. Defaults to Harness/handoff.md.")
    parser.add_argument("--write", action="store_true", help="Write the handoff brief. Default is dry run.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    root = find_project_root(args.root)
    output = args.output or (root / "Harness" / "handoff.md")
    text = build_handoff(root, args.request)
    result = {"root": str(root), "output": rel(output, root), "write": args.write, "status": "written" if args.write else "dry_run", "handoff": text}
    if args.write:
        write_text(output, text)
    print(dump_json(result) if args.json else (f"Wrote handoff brief: {output}" if args.write else text.rstrip() + f"\n\nDry run only. Add --write to write {output}"))


if __name__ == "__main__":
    main()
