import json
import sys
from pathlib import Path


def fail(message):
    raise RuntimeError(message)


def warn(message):
    print(f"warning: {message}")


def project_dir():
    return Path(__file__).resolve().parents[2]


def config_path():
    return project_dir() / "Harness" / "config" / "project.json"


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")


def load_config():
    path = config_path()
    if not path.exists():
        fail(f"Missing Harness config: {path}")
    return load_json(path)


def resolve_relative(path_text):
    return project_dir() / path_text


def verify_package_json(config):
    package_path = resolve_relative(config.get("package_json", "package.json"))
    if not package_path.exists():
        warn(f"Missing package.json: {package_path.relative_to(project_dir())}")
        return None

    package = load_json(package_path)
    for field in config.get("required_package_fields", []):
        if field not in package:
            fail(f"Missing package.json field: {field}")

    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        fail("package.json field 'scripts' must be an object")

    for script_name in config.get("required_scripts", []):
        if script_name not in scripts:
            fail(f"Missing package.json script: {script_name}")

    return package


def verify_required_files(config):
    for relative_path in config.get("required_files", []):
        path = resolve_relative(relative_path)
        if not path.exists():
            fail(f"Missing required file: {relative_path}")


def verify_roots(config, key):
    roots = config.get(key, [])
    if not roots:
        return

    existing = [root for root in roots if resolve_relative(root).exists()]
    if not existing:
        warn(f"No configured {key} exist yet: {', '.join(roots)}")


def detect_package_manager(config):
    configured = config.get("package_manager", "auto")
    if configured != "auto":
        return configured

    root = project_dir()
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    if (root / "package-lock.json").exists() or (root / "npm-shrinkwrap.json").exists():
        return "npm"
    return "npm"


def main():
    config = load_config()

    if config.get("project_type") not in ("javascript", "typescript", "node", "web"):
        fail("project_type must be one of: javascript, typescript, node, web")

    verify_package_json(config)
    verify_required_files(config)
    verify_roots(config, "source_roots")
    verify_roots(config, "test_roots")

    package_manager = detect_package_manager(config)
    print(f"Harness JavaScript verification passed. package_manager={package_manager}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
