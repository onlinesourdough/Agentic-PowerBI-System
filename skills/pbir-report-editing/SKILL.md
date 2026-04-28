---
name: pbir-report-editing
description: Edit and review PBIR Power BI reports: pages, visuals, themes, filters, layout, bindings, bookmarks, and report JSON. Prefer pbir CLI when available.
---

# PBIR Report Editing

PBIR is text-based report metadata. It is powerful but brittle. Prefer the `pbir` CLI for report mutations when available.

## Preferred workflow

```bash
pbir tree "Report.Report" -v
pbir backup "Report.Report" -m "Before agentic edit"
pbir validate "Report.Report"
```

Then make a targeted change and validate again.

## Direct file editing rules

- PBIR files are strict JSON.
- Page/visual folder names should use letters, numbers, underscores, or hyphens.
- Folder name and JSON `name` should match.
- Prefer theme-level formatting over one-off visual formatting.
- Avoid bookmarks unless the user explicitly needs them.
- Ask before deleting or bulk-moving visuals.

## Report design principles

- One page = one business question.
- Put KPIs and conclusion near the top.
- Use charts that match the analytical task.
- Keep slicers limited; use filter pane for secondary filters.
- Add titles/annotations that explain business meaning.
- Use consistent color semantics.

## Validation

Use whichever is available:

```bash
pbir validate "Report.Report" --all
node scripts/validate-pbip.mjs .
```
