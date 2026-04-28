---
name: pbip-workflow
description: Work safely with Power BI Project files: PBIP, PBIR reports, TMDL semantic models, .platform files, .pbi cache, Git ignores, and project-local validation. Use whenever editing .pbip/.Report/.SemanticModel files.
---

# PBIP Workflow

PBIP makes Power BI source-control friendly by splitting a report/model into text files. Treat the files as code, but remember that PBIR/TMDL can be brittle.

## Key concepts

- `.pbip` points to a `.Report` folder.
- `.Report/definition.pbir` binds the report to a semantic model by path or connection.
- `.Report/definition/` contains PBIR report JSON.
- `.SemanticModel/definition/` contains TMDL model files.
- `.pbi/` is local runtime/cache state and usually gitignored.
- `.platform` contains Fabric identity. Do not invent or casually rewrite IDs.

## Safe edit workflow

1. Inspect structure before changing files.
2. Prefer deterministic tooling:
   - `pbir tree`, `pbir validate`, `pbir backup` for reports
   - Tabular Editor/TOM for model mutations when available
   - `node scripts/validate-pbip.mjs` for local structural checks
3. Make small, reversible edits.
4. Validate immediately.
5. Summarize changed paths and risks.

## Rename cascade checklist

When renaming tables/columns/measures/pages/visuals, search across:

- TMDL table files
- relationships.tmdl
- PBIR `visual.json`, `page.json`, `pages.json`
- report filters, sort definitions, conditional formatting
- report extensions / visual calculations
- DAXQueries in both Report and SemanticModel folders
- diagram layouts and culture metadata

## Never do without explicit user confirmation

- Delete report pages/visuals.
- Rewrite `.platform` logical IDs.
- Rebind a report to another model.
- Publish/import/overwrite Fabric items.
- Bulk format every visual.
