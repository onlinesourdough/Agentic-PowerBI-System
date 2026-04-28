# Agentic Power BI Instructions

This repo provides project-local skills, prompts, scripts, and guardrails for Power BI / Business Analytics work.

## Operating model

1. Treat Power BI artifacts as code when they are in PBIP/PBIR/TMDL format.
2. Prefer deterministic tools before manual reasoning:
   - `pbir validate` for reports when available
   - `fab` for Fabric workspace/service operations
   - `pbi-tools` for PBIX/PBIT source-control workflows
   - Tabular Editor CLI/TOM for semantic model operations when available
   - `node scripts/validate-pbip.mjs` for local structural checks
3. Ask before destructive operations: deleting pages/visuals, rebinding reports, changing `.platform`, publishing, overwriting Fabric items.
4. Never edit secrets, credentials, `.pbi/cache.abf`, or local user settings into source control.
5. Validate after edits and report exact file paths changed.

## Progressive disclosure

Read these files when relevant:

| File | When |
|---|---|
| `.agent/SYSTEM.md` | Understand the target Power BI project |
| `.agent/docs/toolchain.md` | Tool install/check commands |
| `.agent/docs/pbip-safety.md` | Before modifying PBIP/PBIR/TMDL files |
| `.agent/docs/business-analytics-workflow.md` | When turning a business question into a report/model plan |
| `.agent/docs/harness-integration.md` | When setting up Pi/Codex/Claude/Copilot integration |
| `.agent/tasks/task_template.md` | When starting a new unit of work |

## Power BI rules of thumb

- Model first: star schema, clean dimensions, explicit measures, no implicit measures.
- Reports are consumers of the semantic model; avoid report-level hacks unless needed.
- Keep business terms documented in `.agent/SYSTEM.md`.
- Use measure descriptions, display folders, and consistent formatting.
- Prefer themes for formatting over one-off visual JSON changes.
- For renames, search across TMDL, PBIR JSON, DAX queries, filters, sort definitions, and diagram layouts.

## Completion checklist

Before saying a Power BI task is done:

- [ ] Files changed are listed.
- [ ] Validation command was run or reason for skipping is stated.
- [ ] Any warnings/risks are documented.
- [ ] User-facing business interpretation is updated when the report/model changes.
