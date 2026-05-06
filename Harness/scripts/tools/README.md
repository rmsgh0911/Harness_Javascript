# Harness Tools

This folder contains small CLI tools that reduce repeated exploration, verification, summarization, and recording work for agents.

## Add A Tool When

- The same exploration, verification, summary, or record step will repeat.
- The result can be short text or JSON.
- Project-specific values can come from `Harness/config/project.json` or command-line arguments.
- Default execution is read-only, and file writes require an explicit option.

## Do Not Add A Tool When

- The task is a one-off conversion.
- The task is a judgment-heavy refactor.
- Reliable execution depends on unstable external state.
- Adding an option to an existing script is enough.

## Manifest Rules

When adding or changing a tool, register it in `tool_manifest.json` with:

- `name`: tool name
- `path`: path relative to the repository root
- `purpose`: repeated cost this tool reduces
- `inputs`: main inputs
- `outputs`: main outputs
- `writes_files`: whether the tool writes files by default or only with an explicit option
- `safe_by_default`: whether the default run is read-only and safe on failure
- `verify`: smallest verification command

## Recommended Interface

```powershell
python Harness/scripts/tools/example_tool.py --help
python Harness/scripts/tools/example_tool.py --json
python Harness/scripts/tools/example_tool.py --write
```

Keep tools small. Split them by purpose if they grow.

## Standard Tools

- `harness_common.py`: shared helpers imported by other tools
- `harness_context.py`: prints a compact Harness briefing
- `harness_docs_check.py`: checks docs roots and on-demand read policy
- `harness_doctor.py`: checks Harness structure and config consistency
- `harness_diff_guard.py`: summarizes changed files and JavaScript risk signals
- `harness_cycle.py`: creates cycle log entries; writes only with `--write`
- `harness_state_check.py`: checks whether state/next/cycles are compact and current
- `harness_handoff.py`: creates a handoff brief; writes only with `--write`
- `harness_verify_all.py`: runs the standard lightweight checks

Examples:

```powershell
python Harness/scripts/tools/harness_context.py
python Harness/scripts/tools/harness_context.py --request "Add login retry"
python Harness/scripts/tools/harness_docs_check.py --json
python Harness/scripts/tools/harness_doctor.py
python Harness/scripts/tools/harness_diff_guard.py
python Harness/scripts/tools/harness_cycle.py "Input fix" --changed "..." --verified "..." --remaining "..."
python Harness/scripts/tools/harness_cycle.py "Input fix" --changed "..." --write
python Harness/scripts/tools/harness_state_check.py
python Harness/scripts/tools/harness_handoff.py --request "Continue login work"
python Harness/scripts/tools/harness_verify_all.py
```

If `python` resolves to the Microsoft Store alias on Windows, use a real Python 3 executable or the workspace runtime Python path.
