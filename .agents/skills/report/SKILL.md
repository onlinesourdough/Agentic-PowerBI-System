---
name: report
description: Plan Power BI report pages and edit PBIR visuals, themes, filters, and layout.
---

# PBIR Report Work

## Editing tools

For PBIR edits, inspect the report structure and preserve a recoverable original.
Prefer `pbir` when available; direct JSON edits are valid when structure and
references can be checked. Use `validation` after edits and report unavailable
native checks honestly. A page plan alone does not require CLI checks or backups.

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
- Complete bulk formatting within the exact authorized local scope. Require
  explicit authorization for deleting pages/visuals, rebinding, `.platform`
  identity, RLS, service, publish, or access/refresh changes. Honor authorization
  already given for the specific action; ask when the scope expands.
- Validate after edits.

## Harness-neutral page-plan contract

Use this contract when planning a page from a `business_question` input. Return
these fields in order, with names that a caller can consume without a command
extension:

```text
page title:
audience and decision:
required measures/fields:
KPI row:
main visuals:
slicers/filters:
business interpretation text:
validation checklist:
```

The page title must answer the business question, and the interpretation must
state the action or decision supported by the evidence. Do not claim data,
refresh, or visual validation that was not run.
