---
name: fabric
description: Use Microsoft Fabric CLI for Power BI Service/Fabric workspaces, reports, semantic models, import/export, refresh, deployment, and item checks.
---

# Fabric CLI Workflow

Use this skill when working with Power BI Service or Microsoft Fabric.

## First checks

```bash
fab --version
```

Only inspect an approved workspace or item after the user supplies that scope
and the operation is relevant. A version check alone is not service proof.

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
- Require explicit authorization for import/export overwrite, publish, move,
  delete, or permission changes. Existing authorization must cover the exact
  target and operation; local source-edit authority does not cover service writes.
- Use `-f` only when the user accepts the overwrite/sensitivity-label implications.
- Record exact commands run.

For any approved data, RLS, permission, or refresh operation, follow the
[shared data-change boundary](../../../docs/contract.md#data-change-boundary)
with the Fabric workspace/item as the target. A successful authentication,
listing, or source edit is not proof of refresh, access, or RLS behavior;
report an unrun service check as a gap.
