# Next

## Immediate Setup After Migration

- Fill `Harness/config/project.json` with the target JavaScript project's `required_files`, `required_scripts`, and `source_roots`.
- Run `python Harness/scripts/verify_project.py` in the target project.
- Run the smallest relevant `Harness/scripts/build_verify.cmd -Mode ...` check in the target project.
- If `python` resolves to the Microsoft Store alias on Windows, fix Python PATH or use a real Python 3 executable first.

## Feature Work

- Add target-project feature tasks here with max cycle count and success criteria when iteration is requested.

## Structure Improvement Candidates

- Add short repository-specific rules to `AGENTS.md` or `CLAUDE.md` only when a target project needs them.
- Register external docs roots in `Harness/config/docs.json` only when the target project already uses them.

## Manual Verification

- Browser UI, accessibility, responsive layout, and real API integration should be manually checked in the target project when automation cannot prove them.

## Known Issues

- None.
