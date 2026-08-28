---
name: system-audit
description: Run a strictly read-only periodic audit of accumulated Agentic Power BI System repository or workspace health.
---

# Periodic System audit

Use this route for an accumulated-state health check, not for setup, repair,
release work, per-change Review, or a single Power BI deliverable.

## Input

Select exactly one scope:

- `repository`: Git identity, clean state, live upstream relation, specialist
  routes, and deterministic validation surface;
- `workspace`: project truth, run/history/proof relations, and discoverable
  failure/recovery evidence;
- `both`: both surfaces plus the existing deterministic structural checks.

Run from the exact repository root:

```sh
python3 workspace/engine/system_audit.py --scope repository
python3 workspace/engine/system_audit.py --scope workspace
python3 workspace/engine/system_audit.py --scope both
```

## Output

Return exactly one status: `PASS`, `FAIL`, or `BLOCKED`, followed by observable
evidence, evidence gaps, and the smallest next action. `PASS` requires all
selected evidence and no observed defect. `FAIL` means a defect is observable.
`BLOCKED` means required evidence is unavailable and no defect already proves
failure. Uncertainty is never `PASS`.

## Read-only boundary

Do not fetch into the audited repository, repair a finding, generate a run,
append the ledger, promote an example, create an issue, publish, change a
service, or alter any audited ref, index, worktree, or workspace file. The
reference route reads the live upstream with `ls-remote` and loads commits only
into temporary storage for ancestry comparison. It records no audit run.
Reject embedded remote credentials before any Git network command; credentials
belong in an external helper or SSH agent, never in the configured remote URL.

Use the `powerbi` audit contract by reference when a bounded business/domain
audit is needed. Use `validation` by reference for deterministic PBIP/PBIR/TMDL
proof. Semantic or visual judgment remains a specialist review, and per-change
Review remains the lifecycle gate for proposed changes; neither is this
periodic audit.

Route a System finding to its owning Build and per-change Review. If the work
originated in an AIOS improvement flow and the finding concerns that flow
rather than this repository's local truth, route it back to AIOS improvement
triage. The audit never performs the repair or authorizes Ship.
