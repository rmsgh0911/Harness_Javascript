"""Check Harness project-doc discovery and on-demand read policy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from harness_common import dump_json, find_project_root, harness_dir, load_json, read_text, rel


REQUEST_READ_HINTS = [
    "기획", "명세", "구현기준", "체크리스트", "시나리오", "검증 기준", "요구사항", "규칙", "설계",
    "design", "spec", "scenario", "validation", "requirements", "rules", "UX", "UI", "API", "schema",
]
REQUEST_SKIP_HINTS = [
    "컴파일 오류", "빌드 오류", "포맷", "리네임", "파일 이동",
    "compile error", "build error", "format", "rename", "file move",
]


def _strings(value: object) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _configured_hints(config: dict, key: str, fallback: list[str]) -> list[str]:
    hints = config.get("request_hints", {})
    value = hints.get(key, fallback) if isinstance(hints, dict) else fallback
    return value if isinstance(value, list) and all(isinstance(item, str) for item in value) else fallback


def evaluate_request(request: str, docs_config: dict) -> dict:
    request_text = request.strip()
    if not request_text:
        return {"request": "", "should_read_docs": False, "reason": "no request provided", "recommended_first_reads": []}

    read_hints = _configured_hints(docs_config, "read", REQUEST_READ_HINTS)
    skip_hints = _configured_hints(docs_config, "skip", REQUEST_SKIP_HINTS)
    lowered = request_text.lower()
    read_hits = [hint for hint in read_hints if hint.lower() in lowered]
    skip_hits = [hint for hint in skip_hints if hint.lower() in lowered]
    should_read = bool(read_hits) and not skip_hits
    reason = "matched document reference hints" if should_read else "no document read trigger matched"
    if skip_hits:
        reason = "matched skip hints for code-only work"
    return {
        "request": request_text,
        "should_read_docs": should_read,
        "reason": reason,
        "read_hits": read_hits,
        "skip_hits": skip_hits,
        "recommended_first_reads": docs_config.get("entry_points", []) if should_read else [],
    }


def _safe_relative(path_text: str) -> bool:
    path = Path(path_text)
    return bool(path_text) and path_text.strip() == path_text and not path.is_absolute() and ".." not in path.parts


def build_report(root: Path, request: str = "") -> dict:
    config_path = harness_dir(root) / "config" / "docs.json"
    findings: list[dict] = []
    docs_config = load_json(config_path, None)
    if not isinstance(docs_config, dict):
        findings.append({"level": "error", "path": rel(config_path, root), "message": "docs.json is missing or invalid"})
        docs_config = {}

    doc_roots = _strings(docs_config.get("doc_roots", []))
    entry_points = _strings(docs_config.get("entry_points", []))
    optional_roots = _strings(docs_config.get("optional_external_roots", []))
    read_policy = docs_config.get("read_policy", {}) if isinstance(docs_config.get("read_policy", {}), dict) else {}

    for path_text in [*doc_roots, *entry_points, *optional_roots]:
        if not _safe_relative(path_text):
            findings.append({"level": "error", "path": rel(config_path, root), "message": f"path must be safe and relative: {path_text}"})

    if not doc_roots:
        findings.append({"level": "warning", "path": rel(config_path, root), "message": "doc_roots is empty"})
    if not entry_points:
        findings.append({"level": "warning", "path": rel(config_path, root), "message": "entry_points is empty"})
    if read_policy.get("default") != "on_demand":
        findings.append({"level": "warning", "path": rel(config_path, root), "message": "read_policy.default should be on_demand"})

    root_status = [{"path": item, "exists": (root / item).is_dir()} for item in doc_roots]
    for item in root_status:
        if not item["exists"]:
            findings.append({"level": "warning", "path": item["path"], "message": "doc root is missing"})
    entry_status = [{"path": item, "exists": (root / item).is_file()} for item in entry_points]
    for item in entry_status:
        if not item["exists"]:
            findings.append({"level": "warning", "path": item["path"], "message": "entry point is missing"})
    if (root / "Harness" / "doc").exists():
        findings.append({"level": "warning", "path": "Harness/doc", "message": "legacy Harness/doc exists; migrate docs to Harness/docs"})

    markdown_files: list[str] = []
    for doc_root in doc_roots:
        base = root / doc_root
        if base.is_dir():
            markdown_files.extend(rel(path, root) for path in sorted(base.glob("**/*.md")) if path.is_file())

    errors = [item for item in findings if item["level"] == "error"]
    return {
        "root": str(root),
        "ok": not errors,
        "config": rel(config_path, root),
        "summary": {
            "doc_roots": len(doc_roots),
            "entry_points": len(entry_points),
            "optional_external_roots": len(optional_roots),
            "markdown_files": len(markdown_files),
            "findings": len(findings),
        },
        "doc_roots": root_status,
        "entry_points": entry_status,
        "markdown_files": markdown_files,
        "read_policy": {"default": read_policy.get("default")},
        "request_eval": evaluate_request(request, docs_config),
        "findings": findings,
    }


def format_text(report: dict) -> str:
    lines = [
        "Harness Docs Check",
        f"- Root: {report['root']}",
        f"- Status: {'ok' if report['ok'] else 'needs attention'}",
        f"- Doc roots: {report['summary']['doc_roots']}",
        f"- Entry points: {report['summary']['entry_points']}",
        f"- Markdown files: {report['summary']['markdown_files']}",
        f"- Read policy: {report['read_policy']['default'] or 'missing'}",
    ]
    request_eval = report["request_eval"]
    if request_eval["request"]:
        lines.extend(["", "Request policy:", f"- Should read docs: {request_eval['should_read_docs']}", f"- Reason: {request_eval['reason']}"])
    if report["findings"]:
        lines.append("")
        lines.append("Findings:")
        for item in report["findings"]:
            path = f" {item['path']}:" if item.get("path") else ""
            lines.append(f"- [{item['level']}]{path} {item['message']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Harness project-doc discovery and docs.json read policy.")
    parser.add_argument("--root", type=Path, default=None, help="Project root. Defaults to nearest Harness root.")
    parser.add_argument("--request", default="", help="Optional user request to evaluate against the docs read policy.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    root = find_project_root(args.root)
    report = build_report(root, args.request)
    print(dump_json(report) if args.json else format_text(report))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
