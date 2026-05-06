# Harness Docs

This folder is the default location for design docs, implementation specs, scenarios, validation criteria, and retrospectives.

Because `HARNESS.md` and the `Harness/` folder are the normal migration unit, keeping docs here makes the template easier to move between projects.

## Placement Rules

- Operating rules live in the root `HARNESS.md`.
- Project reference docs live in `Harness/docs/`.
- If docs are too large or the team already has a separate docs folder, register that root in `Harness/config/docs.json`.
- Agents do not read all docs by default. They read docs only when the user asks or when implementation intent or success criteria are unclear.

## Default Files

- `Progress.md`: Korean human-facing dashboard for current goal, status, recent completion, and decisions needed.

`Progress.md` is not a work log. Update it briefly only after major feature completion, before commits, when direction changes, or when human confirmation is needed.

## Suggested Extensions

- `specs/`: feature specs, API contracts, schema definitions
- `scenarios/`: test scenarios and input/output examples
- `ux/`: screen flow, state definitions, accessibility criteria
- `validation/`: success criteria and manual verification checklists
- `references/`: external references, retrospectives, and experiment notes

## Document Map

- `Progress.md`: Korean human-facing progress dashboard
