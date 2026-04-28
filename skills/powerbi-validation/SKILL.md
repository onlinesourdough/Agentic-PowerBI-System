---
name: powerbi-validation
description: Validate Power BI projects after edits: PBIP structure, PBIR JSON, report bindings, TMDL warnings, field references, rename cascades, and tool availability.
---

# Power BI Validation

Use this skill before declaring a Power BI task complete.

## Validation ladder

1. Local structural validation:

```bash
node scripts/validate-pbip.mjs .
```

2. Report validation with pbir when available:

```bash
pbir validate "Report.Report" --all
```

3. Fabric/service validation when relevant:

```bash
fab auth status
fab exists "Workspace.Workspace/Model.SemanticModel"
```

4. Manual grep for rename cascades:

```bash
rg "Old Name|OldTable|OldMeasure" .
```

## Findings format

Report findings as:

```text
BLOCKERS
- [path] issue. Fix: ...

WARNINGS
- [path] issue. Recommendation: ...

VALIDATION RUN
- command: ...
- result: ...
```

## Common blockers

- Invalid JSON.
- `definition.pbir` byPath target missing.
- PBIR page/visual name mismatch.
- Missing theme/resource package files.
- Report references fields renamed in model.
- TMDL indentation or malformed descriptions.

## Fixing rules

- Fix only obvious syntax issues without asking.
- Ask before delete/rename/rebind/publish.
- Never silently rewrite `.platform` IDs.
