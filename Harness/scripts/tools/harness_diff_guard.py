"""Report risky working-tree changes for JavaScript/TypeScript Harness projects."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import find_project_root, rel, print_text_or_json


GENERATED_DIRS = {
    "node_modules", "dist", "build", "coverage",
    ".next", ".turbo", ".vite", ".nuxt", ".output",
}

LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json"}

CONFIG_PATTERNS = {
    "package.json", "tsconfig.json", "tsconfig.base.json",
    ".env", ".env.local", ".env.production", ".env.staging",
    "next.config.js", "next.config.ts", "next.config.mjs",
    "vite.config.js", "vite.config.ts",
    "webpack.config.js", "webpack.config.ts",
    "rollup.config.js", "rollup.config.ts",
    "babel.config.js", "babel.config.json",
    ".eslintrc.js", ".eslintrc.json", ".eslintrc.cjs",
    "jest.config.js", "jest.config.ts",
    "vitest.config.js", "vitest.config.ts",
    "turbo.json",
}


def resolve_git_executable() -> str | None:
    found = shutil.which("git")
    if found:
        return found
    for candidate in [
        Path("C:/Program Files/Git/cmd/git.exe"),
        Path("C:/Program Files/Git/bin/git.exe"),
        Path("C:/Program Files (x86)/Git/cmd/git.exe"),
    ]:
        if candidate.exists():
            return str(candidate)
    return None


def run_git_status(root: Path) -> tuple[bool, list[str]]:
    git_executable = resolve_git_executable()
    if not git_executable:
        return False, []
    try:
        completed = subprocess.run(
            [git_executable, "status", "--short"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        return False, []
    if completed.returncode != 0:
        return False, []
    return True, [line.rstrip() for line in completed.stdout.splitlines() if line.strip()]


def changed_path_from_status(line: str) -> str:
    text = line[3:] if len(line) > 3 else line
    if " -> " in text:
        text = text.rsplit(" -> ", 1)[-1]
    return text.strip().strip('"')


def scan_without_git(root: Path) -> list[str]:
    candidates: list[str] = []
    for directory in GENERATED_DIRS:
        path = root / directory
        if path.exists():
            candidates.append(f"?? {directory}/")
    return candidates


def classify(paths: list[str]) -> dict:
    risks: list[dict] = []
    for status_line in paths:
        path_text = changed_path_from_status(status_line)
        parts = Path(path_text).parts
        name = Path(path_text).name
        suffix = Path(path_text).suffix.lower()

        if any(part in GENERATED_DIRS for part in parts):
            risks.append({"level": "high", "path": path_text, "reason": "generated_directory"})
            continue

        if name in LOCKFILES:
            risks.append({"level": "medium", "path": path_text, "reason": "lockfile_change"})

        if name in CONFIG_PATTERNS:
            if name == "package.json":
                risks.append({"level": "medium", "path": path_text, "reason": "package_json_change"})
            elif name.startswith(".env"):
                risks.append({"level": "high", "path": path_text, "reason": "env_file_change"})
            else:
                risks.append({"level": "low", "path": path_text, "reason": "config_file_change"})

        if suffix in {".d.ts"} or (suffix == ".ts" and name.endswith(".d.ts")):
            risks.append({"level": "low", "path": path_text, "reason": "type_declaration_change"})

    return {
        "changed_count": len(paths),
        "changed": paths,
        "risks": risks,
        "risk_count": len(risks),
    }


def inspect_export_changes(root: Path, report: dict) -> None:
    """Flag files with top-level export changes for public API review."""
    export_hits: list[dict] = []
    for item in report["changed"]:
        path_text = changed_path_from_status(item)
        path = root / path_text
        if not path.exists() or path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            continue
        lines = text.splitlines()
        export_lines = [
            ln.strip() for ln in lines
            if ln.strip().startswith("export ") and not ln.strip().startswith("export {")
        ]
        if export_lines:
            export_hits.append({"path": path_text, "exports": export_lines[:5]})
    report["export_change_hits"] = export_hits


def build_report(root: Path) -> dict:
    git_available, changed = run_git_status(root)
    if not git_available:
        changed = scan_without_git(root)
    report = classify(changed)
    reliable_change_list = git_available
    report.update(
        {
            "root": str(root),
            "git_available": git_available,
            "git_directory_exists": (root / ".git").exists(),
            "change_list_reliable": reliable_change_list,
            "mode": "git_status" if git_available else "limited_generated_directory_scan",
            "ok": not any(risk["level"] == "high" for risk in report["risks"]),
        }
    )
    inspect_export_changes(root, report)
    return report


def format_text(report: dict) -> str:
    lines = [
        "Harness Diff Guard (JavaScript)",
        f"- Root: {report['root']}",
        f"- Git available: {report['git_available']}",
        f"- Git directory exists: {report['git_directory_exists']}",
        f"- Mode: {report['mode']}",
        f"- Changed paths: {report['changed_count'] if report['change_list_reliable'] else 'limited scan only'}",
        f"- Risks: {report['risk_count']}",
        f"- Status: {'ok' if report['ok'] else 'needs attention'}",
    ]
    if not report["change_list_reliable"]:
        lines.append("- Note: git was not available, so ordinary file changes cannot be listed.")
    if report["risks"]:
        lines.append("")
        lines.append("Risks:")
        for risk in report["risks"]:
            lines.append(f"- [{risk['level']}] {risk['path']}: {risk['reason']}")
    if report.get("export_change_hits"):
        lines.append("")
        lines.append("Export changes (public API review needed):")
        for hit in report["export_change_hits"]:
            lines.append(f"- {hit['path']}:")
            for export_line in hit["exports"]:
                lines.append(f"    {export_line}")
    if report["changed"]:
        lines.append("")
        lines.append("Changed:")
        lines.extend(f"- {changed_path_from_status(item)}" for item in report["changed"][:40])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize risky changes in the current JavaScript Harness project."
    )
    parser.add_argument("--root", type=Path, default=None, help="Project root. Defaults to nearest Harness root.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    root = find_project_root(args.root)
    report = build_report(root)
    print_text_or_json(report if args.json else format_text(report), args.json)


if __name__ == "__main__":
    main()
