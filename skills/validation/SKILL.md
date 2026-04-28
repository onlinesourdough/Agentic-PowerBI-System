---
name: validation
description: Validate Power BI work before completion: PBIP structure, PBIR JSON, report binding, TMDL warnings, field references, rename cascades, and toolchain status.
---

# Power BI Validation

Use this before saying a Power BI task is done.

## Validation ladder

1. Local structural validation:

```bash
node scripts/validate-pbip.mjs .
```

2. PBIR validation when `pbir` is available:

```bash
pbir validate "Report.Report" --all
```

3. Fabric/service checks when relevant:

```bash
fab auth status
fab exists "Workspace.Workspace/Model.SemanticModel"
```

4. Rename cascade checks:

```bash
rg "Old Name|OldTable|OldMeasure" .
```

## Report format

```text
Validation run:
Blockers:
Warnings:
Files changed:
Remaining risks:
```

## Common blockers

- invalid JSON
- broken `definition.pbir` binding
- missing theme/resource files
- page/visual folder-name mismatch
- renamed fields still referenced in visuals
- TMDL indentation or malformed descriptions
