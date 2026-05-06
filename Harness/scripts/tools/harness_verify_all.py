"""Run the standard lightweight Harness verification bundle."""

from __future__ import annotations

import argparse
import py_compile
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import dump_json, find_project_root, harness_dir, load_json, rel
from harness_diff_guard import build_report as build_diff_report
from harness_doctor import run_doctor
from harness_docs_check import build_report as build_docs_report
from harness_state_check import build_report as build_state_report


def compile_python_files(root: Path) -> dict:
    files = sorted((harness_dir(root) / "scripts").glob("**/*.py"))
    failures: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="harness_pycompile_") as temp_dir:
        temp_root = Path(temp_dir)
        for path in files:
            try:
                cfile = temp_root / (rel(path, root).replace("/", "_") + ".pyc")
                py_compile.compile(str(path), cfile=str(cfile), doraise=True)
            except py_compile.PyCompileError as exc:
                failures.append({"path": rel(path, root), "error": str(exc)})
    return {"ok": not failures, "checked": [rel(path, root) for path in files], "failures": failures}


def check_json_files(root: Path) -> dict:
    paths = sorted((harness_dir(root) / "config").glob("*.json"))
    paths.append(harness_dir(root) / "scripts" / "tools" / "tool_manifest.json")
    failures: list[dict] = []
    for path in paths:
        try:
            load_json(path, {})
        except Exception as exc:  # noqa: BLE001
            failures.append({"path": rel(path, root), "error": str(exc)})
    return {"ok": not failures, "checked": [rel(path, root) for path in paths], "failures": failures}


def build_verify_all(root: Path, compile_python: bool = True) -> dict:
    doctor = run_doctor(root)
    diff = build_diff_report(root)
    docs = build_docs_report(root)
    state = build_state_report(root)
    json_check = check_json_files(root)
    compile_check = compile_python_files(root) if compile_python else {"ok": True, "checked": [], "failures": [], "skipped": True}
    ok = doctor["ok"] and docs["ok"] and state["ok"] and json_check["ok"] and compile_check["ok"]
    return {
        "root": str(root),
        "ok": ok,
        "summary": {
            "doctor": "ok" if doctor["ok"] else "failed",
            "doctor_warnings": doctor["summary"]["warnings"],
            "docs_check": "ok" if docs["ok"] else "failed",
            "state_check": "ok" if state["ok"] else "failed",
            "json": "ok" if json_check["ok"] else "failed",
            "python_compile": "ok" if compile_check["ok"] else "failed",
            "diff_guard": "ok" if diff["ok"] else "needs_attention",
        },
        "doctor": doctor["summary"],
        "docs_check": {"findings": len(docs["findings"]), "markdown_files": docs["summary"]["markdown_files"]},
        "state_check": {"findings": len(state["findings"]), "cycle_files": state["cycles"]["file_count"]},
        "json_check": json_check,
        "python_compile": compile_check,
        "diff_guard": {"risk_count": diff["risk_count"], "mode": diff["mode"]},
    }


def format_text(report: dict) -> str:
    lines = [
        "Harness Verify All",
        f"- Root: {report['root']}",
        f"- Status: {'ok' if report['ok'] else 'needs attention'}",
        f"- Doctor: {report['summary']['doctor']}",
        f"- Doctor warnings: {report['summary']['doctor_warnings']}",
        f"- Docs policy: {report['summary']['docs_check']}",
        f"- State check: {report['summary']['state_check']}",
        f"- JSON: {report['summary']['json']}",
        f"- Python compile: {report['summary']['python_compile']}",
        f"- Diff guard: {report['summary']['diff_guard']} ({report['diff_guard']['mode']})",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run standard lightweight Harness verification checks.")
    parser.add_argument("--root", type=Path, default=None, help="Project root. Defaults to nearest Harness root.")
    parser.add_argument("--skip-compile", action="store_true", help="Skip Python compile checks.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    root = find_project_root(args.root)
    report = build_verify_all(root, compile_python=not args.skip_compile)
    print(dump_json(report) if args.json else format_text(report))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
