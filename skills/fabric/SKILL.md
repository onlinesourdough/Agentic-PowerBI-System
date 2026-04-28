---
name: fabric
description: Use Microsoft Fabric CLI for Power BI Service/Fabric workspaces, reports, semantic models, import/export, refresh, deployment, and item checks.
---

# Fabric CLI Workflow

Use this skill when working with Power BI Service or Microsoft Fabric.

## First checks

```bash
fab --version
fab auth status
fab ls
```

If not logged in, ask the user to run:

```bash
fab auth login
```

## Path format

```text
WorkspaceName.Workspace/ItemName.ItemType
```

Examples:

```bash
fab ls "Sales.Workspace" -l
fab exists "Sales.Workspace/Sales Model.SemanticModel"
fab open "Sales.Workspace/Sales Report.Report"
```

## Safety

- Verify workspace and item before changing it.
- Ask before import/export overwrite, publish, move, delete, or permission changes.
- Use `-f` only when the user accepts the overwrite/sensitivity-label implications.
- Record exact commands run.
