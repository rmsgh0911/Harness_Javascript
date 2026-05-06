"""Check whether the Harness template structure is internally consistent."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import find_project_root, harness_dir, load_json, read_text, print_text_or_json, rel


def _check(condition: bool, message: str, severity: str = "error") -> dict:
    return {"ok": bool(condition), "severity": severity, "message": message}


def run_doctor(root: Path) -> dict:
    harness = harness_dir(root)
    results: list[dict] = []
    required = [
        root / "HARNESS.md",
        root / "AGENTS.md",
        root / "CLAUDE.md",
        harness / "README.md",
        harness / "state.md",
        harness / "next.md",
        harness / "config" / "project.json",
        harness / "config" / "agents.json",
        harness / "config" / "cycle_policy.json",
        harness / "config" / "docs.json",
        harness / "docs" / "README.md",
        harness / "scripts" / "verify_project.py",
        harness / "scripts" / "build_verify.ps1",
        harness / "scripts" / "build_verify.cmd",
        harness / "scripts" / "tools" / "tool_manifest.json",
        harness / "scripts" / "tools" / "harness_common.py",
    ]
    for path in required:
        results.append(_check(path.exists(), f"required file exists: {rel(path, root)}"))

    harness_text = read_text(root / "HARNESS.md")
    results.append(_check("up to N cycles" in harness_text, "HARNESS.md explains max-cycle requests"))
    results.append(_check("Tool Additions" in harness_text, "HARNESS.md explains agent-added tools"))
    results.append(_check("Harness/docs" in harness_text, "HARNESS.md explains default project document root"))
    results.append(_check("docs.json" in harness_text, "HARNESS.md explains docs.json policy"))
    results.append(_check("HARNESS.md" in read_text(root / "AGENTS.md"), "AGENTS.md routes agents to HARNESS.md"))
    results.append(_check("HARNESS.md" in read_text(root / "CLAUDE.md"), "CLAUDE.md routes Claude Code to HARNESS.md"))

    for path in [harness / "config" / "project.json", harness / "config" / "agents.json", harness / "config" / "cycle_policy.json", harness / "config" / "docs.json", harness / "scripts" / "tools" / "tool_manifest.json"]:
        try:
            data = load_json(path, None)
            ok = isinstance(data, dict)
        except Exception:  # noqa: BLE001
            data = None
            ok = False
        results.append(_check(ok, f"json parses: {rel(path, root)}"))
        if path.name == "cycle_policy.json" and isinstance(data, dict):
            results.append(_check("cycle_count_rules" in data, "cycle_policy.json has cycle_count_rules"))
            results.append(_check("tool_policy" in data, "cycle_policy.json has tool_policy"))
        if path.name == "tool_manifest.json" and isinstance(data, dict):
            tools = data.get("tools", [])
            results.append(_check(isinstance(tools, list), "tool_manifest.json has tools list"))
            names = [tool.get("name") for tool in tools if isinstance(tool, dict)]
            results.append(_check(len(names) == len(set(names)), "tool_manifest.json tool names are unique"))
            declared = {tool.get("path") for tool in tools if isinstance(tool, dict)}
            for tool in tools:
                if not isinstance(tool, dict):
                    results.append(_check(False, "manifest entry is object"))
                    continue
                name = tool.get("name", "unnamed")
                declared_path = tool.get("path", "")
                results.append(_check(bool(name), f"manifest tool has name: {name}"))
                results.append(_check(bool(tool.get("purpose")), f"manifest tool has purpose: {name}"))
                results.append(_check(str(declared_path).startswith("Harness/scripts/tools/"), f"manifest tool stays under tools: {name}"))
                results.append(_check((root / declared_path).exists(), f"manifest tool path exists: {declared_path or name}"))
                results.append(_check("writes_files" in tool, f"manifest tool declares writes_files: {name}"))
                results.append(_check(tool.get("safe_by_default") is True, f"manifest tool is safe by default: {name}"))
                results.append(_check(bool(tool.get("verify")), f"manifest tool has verify command: {name}"))
            for script in sorted((harness / "scripts" / "tools").glob("*.py")):
                if script.name == "harness_common.py":
                    continue
                results.append(_check(rel(script, root) in declared, f"tool script is listed in manifest: {rel(script, root)}", "warning"))

    generated = [*sorted((harness / "scripts").rglob("__pycache__")), *sorted((harness / "scripts").rglob("*.pyc"))]
    results.append(_check(not generated, "Harness scripts contain no generated Python cache files", "warning"))
    if (harness / "doc").exists():
        results.append(_check(False, "legacy Harness/doc directory has been removed or migrated", "warning"))

    errors = [item for item in results if not item["ok"] and item["severity"] == "error"]
    warnings = [item for item in results if not item["ok"] and item["severity"] == "warning"]
    return {"root": str(root), "ok": not errors, "summary": {"checks": len(results), "errors": len(errors), "warnings": len(warnings)}, "checks": results}


def format_text(result: dict) -> str:
    lines = ["Harness Doctor", f"- Root: {result['root']}", f"- Status: {'ok' if result['ok'] else 'needs attention'}", f"- Checks: {result['summary']['checks']}", f"- Errors: {result['summary']['errors']}", f"- Warnings: {result['summary']['warnings']}", "", "Details:"]
    for item in result["checks"]:
        mark = "OK" if item["ok"] else item["severity"].upper()
        lines.append(f"- [{mark}] {item['message']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Harness structure and policy files.")
    parser.add_argument("--root", type=Path, default=None, help="Project root. Defaults to nearest Harness root.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    root = find_project_root(args.root)
    result = run_doctor(root)
    print_text_or_json(result if args.json else format_text(result), args.json)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
