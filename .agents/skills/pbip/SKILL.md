---
name: pbip
description: Work safely with Power BI Project files: PBIP, PBIR report folders, TMDL semantic model folders, .platform identity files, and .pbi local state. Use whenever editing Power BI project files.
---

# PBIP / PBIR / TMDL Workflow

PBIP makes Power BI source-control friendly by saving report and model metadata as text files.

## Structure

```text
Project/
├── Report.pbip
├── Report.Report/
│   ├── definition.pbir
│   └── definition/
└── Report.SemanticModel/
    ├── definition.pbism
    └── definition/
```

## Rules

- `.Report/definition.pbir` binds the report to a semantic model.
- `.Report/definition/` contains PBIR report JSON.
- `.SemanticModel/definition/` contains TMDL model files.
- `.pbi/` contains local cache/settings and should normally not be committed.
- `.platform` contains Fabric identity. Do not invent or casually rewrite it.

## Safe edit workflow

1. Inspect before editing.
2. Prefer `pbir` CLI for report edits when available.
3. Prefer Tabular Editor/TOM for model edits when available.
4. Make small changes.
5. Validate immediately.

```bash
node workspace/engine/validate-pbip.mjs .
pbir validate "Report.Report" --all
```

## Rename checklist

When renaming tables, columns, measures, pages, or visuals, search across:

- TMDL table files
- relationships
- PBIR visual JSON
- filters and sort definitions
- report metadata / visual calculations
- DAX query files
- diagram layouts

Ask before doing broad rename cascades.
