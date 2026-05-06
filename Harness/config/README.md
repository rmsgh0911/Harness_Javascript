# Harness Config

This folder stores reusable project, worker, cycle, and document policy settings.

- `project.json`: JavaScript project verification settings
- `agents.json`: supported workers and their root instruction files
- `cycle_policy.json`: structured helper for cycle interpretation, recording, worker switching, tool policy, and stop conditions
- `docs.json`: project document roots and on-demand read policy

This folder contains declarative settings only. Do not store cycle logs, long reviews, tokens, API keys, local credentials, or personal paths here.

Authentication and local runtime configuration belong to each user's app, CLI, or agent environment.

## Primary Worker

When working in Codex, `AGENTS.md` applies first. When working in Claude Code, `CLAUDE.md` applies first.

`agents.json` does not launch agents. It documents which worker reads which root instruction file.

To switch the primary worker, the human starts a new session in the app or CLI they want to use. Switching is explicit, never automatic. When switching, record the reason and the first files the next worker should read in today's `Harness/cycles/YYYY-MM-DD.md`.

## project.json Fields

- `package_json`: path to the target project's `package.json`
- `package_manager`: one of `auto`, `npm`, `pnpm`, or `yarn`
- `source_roots`: source root candidates
- `test_roots`: test root candidates
- `required_files`: files that must exist
- `required_package_fields`: required `package.json` fields
- `required_scripts`: npm scripts that must exist
- `optional_scripts`: scripts that can be used when present
- `commands`: script-name mapping used by `build_verify.ps1`

## docs.json Fields

- `doc_roots`: relative paths where project docs may live
- `entry_points`: first documents agents should read when docs are needed
- `optional_external_roots`: external doc folders that may be registered during migration
- `read_policy`: when agents should or should not read project docs
- `request_hints`: request text hints for docs-on-demand decisions
