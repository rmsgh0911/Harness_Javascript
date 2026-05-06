# HARNESS.md

This file defines the default operating rules for agents working with this JavaScript/TypeScript Harness template.

## Core Principles

- Default mode is one fast primary worker.
- Default flow is `implement -> minimal verification -> self-review -> record`.
- Do not run external review, external agent checks, or summary agents in the default loop.
- Read and edit only the files that are directly relevant to the current request.
- Prefer evidence from code, config, logs, and command output over assumptions.
- Never revert user changes or unrelated generated files unless the user explicitly asks.

## Startup Read Order

1. Check the project root `README.md` if it exists.
2. Read `Harness/README.md`, `Harness/state.md`, and `Harness/next.md`.
3. If today's `Harness/cycles/YYYY-MM-DD.md` exists, skim the latest entries.
4. If the user asks for cycles, iteration, "up to N times", or "up to N cycles", check `Harness/config/cycle_policy.json`.
5. If the user asks to reference design docs, specs, scenarios, validation criteria, or if the implementation intent is unclear, check `Harness/config/docs.json` and read only the relevant project docs.
6. Inspect only the `package.json`, lockfile, `src/`, `app/`, `lib/`, `packages/`, `test/`, `tests/`, `config`, or `Harness/scripts/` files needed for the current request.

## User Request Interpretation

- If the user gives a clear feature name, bug, success criterion, or maximum cycle count, prioritize implementation and verification.
- If success criteria are unclear, infer the smallest reasonable criterion from the current context and continue.
- If the user says "cycle", "iterate", "up to N times", or "up to N cycles", treat the task as Harness cycle work.
- A maximum cycle count is an upper bound, not a required count.
- If no maximum is given, run one cycle by default.
- Stop before the maximum when the success criteria are met and there is no obvious safety improvement left.
- One cycle means `implement or improve -> minimal verification -> self-review -> short record -> decide whether to continue`.
- Do not repeat the same failed attempt without new evidence.
- Stop and report when the same issue repeats twice, tests or builds fail twice for the same reason, the diff becomes unexpectedly large, or a public API / package-manager risk appears.

## Feature Work Loop

1. Restate the request, scope, and verification method briefly.
2. Read only the files needed to understand the existing pattern.
3. Check risk before editing.
4. Implement the smallest useful change.
5. Run the smallest reasonable verification command: typecheck, test, lint, build, or a focused project script.
6. Self-review the changed files for JavaScript runtime, bundling, async, and type-safety risks.
7. Apply one focused safety improvement only if it directly reduces risk.
8. Record manual verification needs for browser behavior, accessibility, responsive layout, or real API integration when automation cannot prove them.

Cycle priority:

1. Make the requested behavior actually work.
2. Fix test, typecheck, lint, or build failures.
3. Cover empty states, failure states, loading states, and input handling.
4. Add stability checks such as null/undefined handling, async cleanup, cancellation, and race-condition protection.
5. Keep records short and current.

Do not spend cycle time on wording, formatting, comments, or naming cleanup unless it blocks verification or debugging.

## Project Docs

- Project design docs, implementation specs, scenarios, validation criteria, and retrospectives live under `Harness/docs/` by default.
- `Harness/docs/Progress.md` is the only Harness document that should be written in Korean by default. It is a human-facing dashboard, not a work log. Update it briefly only after major feature completion, before commits, when direction changes, or when human confirmation is needed.
- Keep the template migration unit small: by default, move only `HARNESS.md` and `Harness/`.
- If docs are too large or the team already has an external docs folder, register root-level `ProjectDocs/`, `Docs/`, or `DesignDocs/` in `Harness/config/docs.json`.
- `Harness/config/docs.json` stores doc locations and reading policy only. Do not store full design documents under `Harness/config/`.
- Agents do not read project docs by default. Read them only when requested, when product rules or success criteria are unclear, or when code/config/tests are not enough.
- When reading docs, start from `entry_points` and relevant sections. Do not bulk-read every document.
- If unsure whether docs are needed, run `python Harness/scripts/tools/harness_context.py --request "<request>"` or `python Harness/scripts/tools/harness_docs_check.py --request "<request>"`.
- If project docs conflict with code, config, tests, or command output, report the difference instead of forcing the docs assumption.

## Recording Rules

- `cycles/YYYY-MM-DD.md` contains only short attempts, results, and next actions.
- `state.md` is not a work log. Keep only the latest confirmed facts in present tense.
- `next.md` contains only unresolved work, deferred risks, and human decisions needed.
- `docs/Progress.md` contains a short Korean human summary only. Do not duplicate long content from `state.md`, `next.md`, or `cycles/`.
- Do not duplicate the same details across `state.md`, `next.md`, and `cycles/`.
- When editing the template repository itself, do not create real project cycle logs unless the user explicitly asks.

Recommended cycle log format:

```markdown
## HH:MM Task Name
- Changed:
- Verified:
- Remaining:
```

## Config Files

- `Harness/config/cycle_policy.json` is a structured reference for cycle rules. If it conflicts with this file, `HARNESS.md` wins and the config should be updated.
- `Harness/config/agents.json` maps supported workers to their root instruction files.
- `Harness/config/docs.json` stores project document locations and on-demand reading policy.
- `Harness/config/project.json` stores JavaScript package, source root, test root, script, and package-manager settings.

## Worker Switching

- Use one primary worker: Codex or Claude Code.
- Switch workers only when the human explicitly assigns it, Codex token budget is exhausted, or context is too large.
- Worker switching is never automatic.
- Before switching, record the reason and the first files the next worker should read in today's `cycles/YYYY-MM-DD.md`.
- The new worker should first read `HARNESS.md`, `Harness/state.md`, `Harness/next.md`, today's cycle log, and the current `git status/diff`.
- Do not store credentials, API keys, tokens, or personal local paths in Harness.

## JavaScript Cautions

- Check impact when changing `package.json`, lockfiles, `tsconfig`, bundler config, or test config.
- Do not mix package managers. If a lockfile exists, prefer that package manager.
- Change public APIs, export names, routes, schemas, and environment variable names only when required.
- For async code, check failure paths, cancellation, cleanup, and duplicate-request behavior.
- For browser code, consider loading, empty, error, keyboard-accessibility, and mobile states.
- For server code, check input validation, auth boundaries, and whether logs expose sensitive data.
- Treat `node_modules/`, `dist/`, `build/`, `coverage/`, and cache folders as generated outputs, not work products.

## Verification

- Run the smallest useful build or verification command.
- Passing `Harness/scripts/verify_project.py` alone does not prove feature success.
- When doc policy may matter, run `python Harness/scripts/tools/harness_docs_check.py --json`.
- For code changes, prefer the relevant real project command from `test`, `typecheck`, `lint`, or `build`.
- For project-script verification, prefer `Harness/scripts/build_verify.cmd` or `Harness/scripts/build_verify.ps1`.
- Browser behavior, accessibility, responsive layout, and real external API integration may require manual verification. Record that need when automation cannot prove it.
- If a test or verification could not be run, record why.

## Tool Additions

- Agents may add small CLI tools for repeated exploration, verification, summarization, or recording work.
- Put such tools under `Harness/scripts/tools/` by default.
- Tools should have one small purpose and be read-only by default.
- File writes must require explicit options such as `--write`, `--apply`, or `--update`.
- Do not hardcode project-specific values in tool code. Use `Harness/config/project.json` or command-line arguments.
- When adding or changing a tool, update `Harness/scripts/tools/tool_manifest.json` with purpose, inputs, outputs, write behavior, and verification command.
- Verify new or changed tools with `--help`, dry run, JSON output, or the smallest reasonable command.
- Do not create tools for one-off transformations, judgment-heavy refactors, or unstable external state.

## Git

- If this is a Git repository, start by checking `git status --short`.
- Do not revert user changes or unrelated changes.
- Generated folders such as `node_modules/`, `dist/`, `build/`, `coverage/`, `.next/`, `.turbo/`, and `.vite/` are usually not commit targets.
- Avoid large renames, format-only churn, and lockfile regeneration unless requested or clearly required.
- Commit only when the user asks.
- Create branches, rebase, force-push, or rewrite history only when the user explicitly asks.
- Before finishing, inspect `git diff --stat` or the relevant diff and confirm the change scope matches the request.

## Language

- Reply to the user in the user's language.
- Write agent-facing Harness files in English by default for migration stability.
- The default exception is `Harness/docs/Progress.md`, which should be written in Korean because it is a human-facing project dashboard.
- Keep code identifiers, file names, class names, function names, commands, logs, and error messages in their original language.
- When editing non-ASCII files from Windows PowerShell, use explicit UTF-8 handling.
