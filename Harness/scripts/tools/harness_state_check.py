"""Check Harness state/next/cycle documents for bloat and stale structure."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import dump_json, find_project_root, harness_dir, read_text, rel


HISTORY_HINTS = ["migrated", "migration", "이식", "제거", "추가했다", "변경:", "검증:", "남은 것:"]
UNRESOLVED_HINTS = ["작성 필요", "TODO", "TBD"]
OLD_PATH_HINTS = ["Harness/doc", "GOOSE.md"]
DATE_PATTERN = re.compile(r"20\d\d-\d\d-\d\d")


def _line_count(text: str) -> int:
    return len(text.splitlines()) if text else 0


def _hits(text: str, hints: list[str]) -> int:
    return sum(text.count(hint) for hint in hints)


def check_file(root: Path, relative: str, soft_limit: int, hard_limit: int, allow_placeholders: bool = False) -> dict:
    path = root / relative
    text = read_text(path)
    warnings: list[str] = []
    errors: list[str] = []
    lines = _line_count(text)
    if not path.exists():
        warnings.append("missing")
    if lines > soft_limit:
        warnings.append(f"longer_than_soft_limit:{soft_limit}")
    if lines > hard_limit:
        errors.append(f"longer_than_hard_limit:{hard_limit}")
    unresolved = _hits(text, UNRESOLVED_HINTS)
    old_paths = _hits(text, OLD_PATH_HINTS)
    if unresolved and not allow_placeholders:
        warnings.append(f"unresolved_placeholders:{unresolved}")
    if old_paths:
        warnings.append(f"old_path_hints:{old_paths}")
    return {"path": relative, "exists": path.exists(), "lines": lines, "chars": len(text), "warnings": warnings, "errors": errors}


def build_report(root: Path) -> dict:
    docs = [
        check_file(root, "Harness/state.md", 140, 220),
        check_file(root, "Harness/next.md", 100, 160, allow_placeholders=True),
        check_file(root, "Harness/README.md", 180, 280),
    ]
    state_text = read_text(root / "Harness" / "state.md")
    history_hits = _hits(state_text, HISTORY_HINTS) + len(DATE_PATTERN.findall(state_text))
    cycles_dir = harness_dir(root) / "cycles"
    cycle_files = sorted(path for path in cycles_dir.glob("*.md") if path.name != ".gitkeep") if cycles_dir.exists() else []
    total_cycle_lines = sum(_line_count(read_text(path)) for path in cycle_files)
    findings: list[dict] = []
    for doc in docs:
        findings.extend({"level": "error", "path": doc["path"], "message": item} for item in doc["errors"])
        findings.extend({"level": "warning", "path": doc["path"], "message": item} for item in doc["warnings"])
    if history_hits >= 8:
        findings.append({"level": "warning", "path": "Harness/state.md", "message": "state.md appears to contain work-log or migration history"})
    return {
        "root": str(root),
        "ok": not any(item["level"] == "error" for item in findings),
        "docs": docs,
        "state": {"history_hint_count": history_hits, "looks_like_work_log": history_hits >= 8},
        "cycles": {"file_count": len(cycle_files), "total_lines": total_cycle_lines},
        "findings": findings,
    }


def format_text(report: dict) -> str:
    lines = [
        "Harness State Check",
        f"- Root: {report['root']}",
        f"- Status: {'ok' if report['ok'] else 'needs attention'}",
        f"- Cycle files: {report['cycles']['file_count']}",
        f"- Cycle total lines: {report['cycles']['total_lines']}",
        "",
        "Docs:",
    ]
    for doc in report["docs"]:
        warn = ", ".join(doc["warnings"]) if doc["warnings"] else "ok"
        lines.append(f"- {doc['path']}: {doc['lines']} lines, {warn}")
    if report["findings"]:
        lines.append("")
        lines.append("Findings:")
        lines.extend(f"- [{item['level']}] {item['path']}: {item['message']}" for item in report["findings"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Harness state, next, and cycle documents for bloat and stale paths.")
    parser.add_argument("--target", type=Path, default=None, help="Target project root. Defaults to nearest Harness root.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    root = args.target.resolve() if args.target else find_project_root()
    report = build_report(root)
    print(dump_json(report) if args.json else format_text(report))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
