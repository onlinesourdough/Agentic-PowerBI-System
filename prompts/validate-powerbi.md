---
description: Validate the current Power BI project
argument-hint: "[path]"
---
Validate the Power BI project at `${1:-.}`.

Use deterministic checks first:

1. `node scripts/validate-pbip.mjs ${1:-.}` if available.
2. `pbir validate <Report.Report> --all` for each report if `pbir` is available.
3. `fab auth status` / `fab exists` only if service bindings are relevant.

Return blockers, warnings, exact paths, and commands run.
