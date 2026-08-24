# Workspace

`workspace/` is the persistent operational truth for the Agentic Power BI
System. It is a local filesystem contract, not a service or a shared store.

- `PROJECT-BRIEF.md` is the active decision, KPI, data, security, refresh, and
  publish contract.
- `briefs/` holds additional bounded briefs when a project needs them.
- `models/` and `reports/` hold active semantic-model and report work.
- `state/` holds only safe, local System state; generated Power BI cache remains
  excluded.
- `runs/` holds durable evidence for each route attempt.
- `history/runs.jsonl` keeps the append-only relation between runs.
- `learning/` holds durable notes intentionally retained for future work.
- `engine/` contains optional local validators, the deterministic tracer, and
  dependency-light tests.

Run records keep references to input, output, and proof artifacts instead of
copying request transcripts into the ledger. No service, database, or external
System installation is needed to understand this workspace.
