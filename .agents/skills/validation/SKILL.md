---
name: validation
description: Validate PBIP/PBIR/TMDL edits or audit project structure, bindings, field references, rename cascades, and available native checks.
---

# Power BI Validation

Use this for PBIP/PBIR/TMDL edits or a requested project validation. Business
questions and page plans need their relevant semantic/planning review, not
structural commands against nonexistent or unchanged artifacts.

## Harness-neutral validation contract

The validation route accepts a repository or project `target` (default `.`)
and runs these steps in order:

1. `node workspace/engine/validate-pbip.mjs <target>`;
2. `pbir validate <Report.Report> --all` for each report when `pbir` is
   installed;
3. approved Fabric existence or item checks only when service scope is
   relevant.

For renames, also search affected model/report references for the old names,
including filters, sort definitions, DAX queries, and diagram layouts. A
missing optional tool or an unrun service check is not a completion claim.

Return files changed, blockers, warnings, exact paths, commands run, unavailable checks, and
remaining risks. Native Power BI, Fabric, Tabular Editor, and DAX Studio
results are optional evidence and must never be invented.

## Common blockers

- invalid JSON
- broken `definition.pbir` binding
- missing theme/resource files
- page/visual folder-name mismatch
- renamed fields still referenced in visuals
- TMDL indentation or malformed descriptions
