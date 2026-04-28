---
name: report
description: Design and edit Power BI PBIR reports: pages, visuals, themes, filters, layout, bindings, and validation. Prefer pbir CLI when available.
---

# PBIR Report Work

## Preferred tool workflow

```bash
pbir tree "Report.Report" -v
pbir backup "Report.Report" -m "Before edits"
pbir validate "Report.Report" --all
```

Use direct JSON editing only when the change is small and the structure is clear.

## Design rules

- One page = one business question.
- KPI row at top, explanation in middle, detail at bottom.
- Prefer theme-level formatting over per-visual formatting.
- Use consistent colors with business meaning.
- Avoid too many slicers; use filter pane for secondary filters.
- Add text that explains the insight and recommended action.

## PBIR safety

- JSON must be valid.
- Page/visual folder names should avoid spaces and punctuation.
- Folder name and JSON `name` should match.
- Ask before deleting pages/visuals or bulk formatting.
- Validate after edits.
