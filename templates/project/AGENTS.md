# Power BI Project Agent Instructions

This project uses `agentic-powerbi` for project-local Power BI / Business Analytics agentic development.

## Start of session

1. Read `.agent/SYSTEM.md`.
2. Inspect the repo structure.
3. Identify PBIP/PBIR/TMDL artifacts.
4. Check available tooling with `/powerbi-doctor` if using Pi.

## Working rules

- Prefer deterministic CLIs before manual edits.
- Validate after PBIP/PBIR/TMDL changes.
- Ask before deleting, rebinding, publishing, or rewriting `.platform` files.
- Keep business definitions and assumptions updated in `.agent/SYSTEM.md`.

## Completion

Always report:

- changed files
- validation command/result
- remaining risks
- business interpretation impact
