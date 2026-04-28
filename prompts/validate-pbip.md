---
description: Validate the current PBIP/PBIR/TMDL project and report blockers/warnings
argument-hint: "[path]"
---
Validate the Power BI project at `${1:-.}`.

Use deterministic tools first:

1. `node scripts/validate-pbip.mjs ${1:-.}` if available.
2. `pbir validate <Report.Report> --all` for each report folder if `pbir` is available.
3. For Fabric bindings, check `fab auth status` and `fab exists` only if needed.

Report blockers, warnings, exact file paths, and the commands run.
