---
name: fabric-deployment
description: Use Microsoft Fabric CLI for Power BI/Fabric workspaces, semantic models, reports, refresh, import/export, permissions, and deployment workflows. Use when tasks mention Fabric, Power BI Service, workspaces, or publishing.
---

# Fabric Deployment

Use this skill for Power BI Service / Fabric operations.

## First checks

```bash
fab --version
fab auth status
fab ls
```

If the user is not authenticated, ask them to run:

```bash
fab auth login
```

## Path pattern

Fabric CLI uses filesystem-like paths:

```text
WorkspaceName.Workspace/ItemName.ItemType
```

Examples:

```bash
fab ls "Sales.Workspace" -l
fab exists "Sales.Workspace/Sales Model.SemanticModel"
fab open "Sales.Workspace/Sales Report.Report"
```

## Safe workflow

- Verify workspace and item names before changing anything.
- For export/import, create output folders first.
- Use `-f` only when the user accepts overwrite/sensitivity-label implications.
- Avoid destructive commands unless explicitly requested.
- Record exact commands run.

## Common tasks

```bash
fab export "Workspace.Workspace/Report.Report" -o ./exports -f
fab import "Workspace.Workspace/Report.Report" -i ./Report.Report -f
fab api -A powerbi "groups/<workspace-id>/datasets/<dataset-id>/refreshes" -X post -i '{"type":"Full"}'
```

## CI/CD note

For automation, prefer service principal or managed identity auth and avoid interactive prompts.
