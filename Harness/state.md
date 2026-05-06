# State

## Project

- Project type: JavaScript/TypeScript Harness template
- Project name: Harness_Javascript
- Repository: `https://github.com/rmsgh0911/Harness_Javascript.git`
- Default worker: current Codex app or Claude Code app
- Supported workers: Codex, Claude Code
- Package manager: auto-detected from the target project lockfile
- Baseline config: `Harness/config/project.json`

## Confirmed Current State

- The root operating rules target JavaScript/TypeScript projects.
- Agent-facing Harness files are written in English by default for migration stability.
- `Harness/config/agents.json` uses `current_app` as the default worker and allows Codex and Claude Code as primary workers.
- `Harness/config/docs.json` defines on-demand project-doc reading from `Harness/docs/`.
- `Harness/scripts/verify_project.py` checks `package.json`, required files, and required scripts for JavaScript/TypeScript projects.
- `Harness/scripts/build_verify.ps1` runs npm/pnpm/yarn based project scripts.
- `Harness/scripts/tools/` contains small CLI tools for context, docs policy, diff risk, cycle logging, handoff, state checks, and lightweight verification.

## Key Files

- `HARNESS.md`
- `AGENTS.md`
- `CLAUDE.md`
- `Harness/README.md`
- `Harness/config/project.json`
- `Harness/config/agents.json`
- `Harness/config/cycle_policy.json`
- `Harness/config/docs.json`
- `Harness/scripts/verify_project.py`
- `Harness/scripts/build_verify.ps1`
- `Harness/scripts/tools/tool_manifest.json`

## Verification State

- Last Harness structure check: 2026-05-06 `harness_doctor.py` passed with 0 warnings
- Last lightweight verification bundle: 2026-05-06 `harness_verify_all.py` passed
- Last Harness config check: 2026-05-06 JSON parsing passed for config files and tool manifest
- Last diff check: 2026-05-06 `git diff --check` passed
- Last template project verifier: 2026-05-06 `verify_project.py` passed with expected standalone-template warnings for missing target `package.json`, source roots, and test roots
- Last project script verification: must run after migrating into a target JavaScript project

## Risks

- This standalone template may not have `package.json`; the template verifier should treat that as a warning.
- After migration, fill `required_scripts`, `source_roots`, and any required files in `Harness/config/project.json`.
- On Windows, if `python` resolves to the Microsoft Store alias, use a real Python 3 executable or the workspace runtime Python path before running Harness tools.
