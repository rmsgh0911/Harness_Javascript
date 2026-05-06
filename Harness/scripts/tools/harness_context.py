"""Print a compact Harness briefing for the current agent."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import file_status, find_project_root, harness_dir, load_json, markdown_list_items, read_text, rel, today_cycle_path, print_text_or_json
from harness_docs_check import evaluate_request


def evaluate_cycle_request(request: str, cycle_policy: dict) -> dict:
    text = request.strip()
    if not text:
        return {"request": "", "is_cycle_work": False, "max_cycles": cycle_policy.get("default_max_cycles", 1), "reason": "no request provided"}
    lowered = text.lower()
    phrases = cycle_policy.get("cycle_count_rules", {}).get("phrases", [])
    hits = [phrase for phrase in phrases if isinstance(phrase, str) and phrase.lower().replace("n", "") in lowered]
    max_cycles = None
    for pattern in [r"up to\s*(\d+)\s*(?:times|cycles?)", r"max(?:imum)?\s*(\d+)\s*(?:times|cycles?)", r"(\d+)\s*cycles?", r"최대\s*(\d+)\s*(?:회|사이클)", r"(\d+)\s*사이클"]:
        match = re.search(pattern, lowered, flags=re.IGNORECASE)
        if match:
            max_cycles = int(match.group(1))
            break
    is_cycle = bool(hits or max_cycles)
    return {"request": text, "is_cycle_work": is_cycle, "max_cycles": max_cycles or cycle_policy.get("default_max_cycles", 1), "reason": "matched cycle request hints" if is_cycle else "no cycle trigger matched", "hits": hits}


def build_context(root: Path, request: str = "") -> dict:
    harness = harness_dir(root)
    project = load_json(harness / "config" / "project.json", {}) or {}
    cycle_policy = load_json(harness / "config" / "cycle_policy.json", {}) or {}
    docs_config = load_json(harness / "config" / "docs.json", {}) or {}
    manifest = load_json(harness / "scripts" / "tools" / "tool_manifest.json", {}) or {}
    cycle_path = today_cycle_path(root)
    package_path = root / project.get("package_json", "package.json")
    first_reads = ["HARNESS.md", "Harness/state.md", "Harness/next.md"]
    if cycle_path.exists():
        first_reads.append(rel(cycle_path, root))
    return {
        "root": str(root),
        "project": {"name": project.get("project_name", ""), "package_json": project.get("package_json", "package.json"), "package_exists": package_path.exists(), "package_manager": project.get("package_manager", "auto")},
        "files": {
            "HARNESS.md": file_status(root / "HARNESS.md"),
            "AGENTS.md": file_status(root / "AGENTS.md"),
            "CLAUDE.md": file_status(root / "CLAUDE.md"),
            "Harness/state.md": file_status(harness / "state.md"),
            "Harness/next.md": file_status(harness / "next.md"),
        },
        "next_items": markdown_list_items(read_text(harness / "next.md"), limit=6),
        "cycle_policy": {"default_max_cycles": cycle_policy.get("default_max_cycles", 1), "request_eval": evaluate_cycle_request(request, cycle_policy)},
        "project_docs": {"request_eval": evaluate_request(request, docs_config), "entry_points": docs_config.get("entry_points", [])},
        "tools": {"registered_count": len(manifest.get("tools", [])), "registered": [tool.get("name", "") for tool in manifest.get("tools", []) if isinstance(tool, dict)]},
        "warnings": build_warnings(root, package_path),
        "recommended_first_reads": first_reads,
    }


def build_warnings(root: Path, package_path: Path) -> list[str]:
    warnings: list[str] = []
    if not package_path.exists():
        warnings.append("package.json is missing; this is acceptable for the standalone template but must be filled after migration")
    if (root / ".git").exists() and not shutil.which("git"):
        warnings.append("git repository found but git CLI is not in PATH")
    return warnings


def format_text(context: dict) -> str:
    lines = [
        "Harness Context",
        f"- Root: {context['root']}",
        f"- Project: {context['project']['name'] or 'not configured'}",
        f"- Package: {context['project']['package_json']} ({'exists' if context['project']['package_exists'] else 'missing'})",
        f"- Package manager: {context['project']['package_manager']}",
        f"- Registered tools: {context['tools']['registered_count']}",
    ]
    if context["warnings"]:
        lines.append("- Warnings: " + "; ".join(context["warnings"]))
    req = context["project_docs"]["request_eval"]
    if req.get("request"):
        lines.append(f"- Should read docs: {req.get('should_read_docs')}")
    cyc = context["cycle_policy"]["request_eval"]
    if cyc.get("request"):
        lines.append(f"- Cycle work: {cyc.get('is_cycle_work')}")
        if cyc.get("is_cycle_work"):
            lines.append(f"- Max cycles: {cyc.get('max_cycles')} (upper bound)")
    lines.extend(["", "Files:"])
    lines.extend(f"- {name}: {status}" for name, status in context["files"].items())
    lines.extend(["", "Next:"])
    lines.extend(f"- {item}" for item in context["next_items"]) if context["next_items"] else lines.append("- no short next items found")
    lines.extend(["", "Read first:"])
    lines.extend(f"- {path}" for path in context["recommended_first_reads"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a compact Harness context briefing.")
    parser.add_argument("--root", type=Path, default=None, help="Project root. Defaults to nearest Harness root.")
    parser.add_argument("--request", default="", help="Optional user request to evaluate.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    root = find_project_root(args.root)
    context = build_context(root, args.request)
    print_text_or_json(context if args.json else format_text(context), args.json)


if __name__ == "__main__":
    main()
