---
name: validation
description: Validate Power BI work before completion: PBIP structure, PBIR JSON, report binding, TMDL warnings, field references, rename cascades, and toolchain status.
---

# Power BI Validation

Use this before saying a Power BI task is done.

## Validation ladder

1. Local structural validation:

```bash
node workspace/engine/validate-pbip.mjs .
```

2. PBIR validation when `pbir` is available:

```bash
pbir validate "Report.Report" --all
```

3. Fabric/service checks when relevant:

```bash
fab exists "Workspace.Workspace/Model.SemanticModel"
```

Run service checks only for an approved target. Do not turn a missing optional
tool or an unrun service check into a completion claim.

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

## Harness-neutral validation contract

The validation route accepts a repository or project `target` (default `.`)
and runs these steps in order:

1. `node workspace/engine/validate-pbip.mjs <target>`;
2. `pbir validate <Report.Report> --all` for each report when `pbir` is
   installed;
3. approved Fabric existence or item checks only when service scope is
   relevant.

Return blockers, warnings, exact paths, commands run, unavailable checks, and
remaining risks. Native Power BI, Fabric, Tabular Editor, and DAX Studio
results are optional evidence and must never be invented.

## Common blockers

- invalid JSON
- broken `definition.pbir` binding
- missing theme/resource files
- page/visual folder-name mismatch
- renamed fields still referenced in visuals
- TMDL indentation or malformed descriptions
