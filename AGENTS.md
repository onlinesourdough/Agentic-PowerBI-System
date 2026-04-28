# Agentic Power BI

Use this guidance when working in a Power BI / Business Analytics repo.

## Core rules

1. Treat PBIP/PBIR/TMDL as source code, but validate after edits.
2. Prefer deterministic tools before guessing:
   - `pbir validate` for reports
   - `fab` for Fabric / Power BI Service
   - `pbi-tools` for PBIX/PBIT workflows
   - Tabular Editor / DAX Studio for model and DAX work
3. Ask before deleting visuals/pages, rebinding reports, publishing, overwriting service items, or changing `.platform` IDs.
4. Keep business definitions clear: KPI name, DAX, format, interpretation, limitation.
5. Always finish with changed files + validation result + remaining risks.

## Power BI workflow

- Model first: star schema, relationships, hidden technical keys, explicit measures.
- Report second: one page per business question, clear KPI row, explanation, detail.
- Validate always: JSON, PBIR structure, report binding, TMDL warnings, field references.

## Useful commands

```bash
node scripts/doctor.mjs
node scripts/validate-pbip.mjs .
pbir validate "Report.Report" --all
fab auth status
```
