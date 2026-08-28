# Agentic Power BI System contract

## Product and boundary

The canonical product name is **Agentic Power BI System**. This repository is a
standalone System mapped to the System Template contract. It owns its local
briefs, model/report work, state, run evidence, history, and learning under
`workspace/`.

The first-class concepts remain Space, System, and Project. This repository is
the System capability; a bounded Power BI delivery is a Project outcome inside
its brief and workspace. The repository does not import another System,
centralize records, or require a service to interpret its contract.

## Functional roots

Only these visible functional roots are used:

| Path | Purpose |
| --- | --- |
| `workspace/` | persistent briefs, model/report work, state, and operational truth |
| `examples/` | deliberately curated standalone proof |
| `docs/` | public contract and validation notes |

Technical implementation lives below `workspace/engine/`. Root instructions,
the README, the primary System skill, package metadata, and hidden CI are shell
support rather than additional functional roots.

## Primary route

`.agents/skills/agentic-powerbi-system/SKILL.md` is the one primary System skill.
It must:

1. inspect relevant prior records before routing work;
2. select the existing Power BI specialist route(s) for the business question,
   PBIP/PBIR/TMDL structure, DAX, report composition, Fabric, or validation;
3. write structured input, output, and proof references under
   `workspace/runs/<run-id>/`;
4. append one JSON object to `workspace/history/runs.jsonl`;
5. preserve failure and recovery evidence without rewriting the failed record;
6. promote an example only after an explicit curation choice.

The periodic `system-audit` route is the read-only exception to run recording:
it selects `repository`, `workspace`, or `both`, returns exactly `PASS`,
`FAIL`, or `BLOCKED` with evidence, gaps, and a next action, and never writes a
run, ledger record, example, repository state, or service state. It reads the
existing Power BI/domain audit and validation contracts by reference.

Inputs are references and structured facts, not request transcripts. Nothing
in the route may invent PBIX/PBIP, refresh, access, tenant, or publish proof.

## Run ledger

Each ledger object contains:

```text
run_id
started_at
finished_at
status
input_ref
output_ref
proof_ref
previous_run_id
previous_run_relation
failure
recovery
```

`previous_run_relation` is `null` for the first relevant run, `predecessor`
for ordinary continuation, and `recovery` when the route explicitly recovers
an unresolved failed predecessor. A failed record stays append-only and can be
recovered at most once. References point to the run directory; the ledger is
not a second content database.

## Power BI authority gates

The System preserves these gates in the brief and specialist routes:

- KPI definition, interpretation, limitation, and business owner;
- canonical data ownership, grain, relationships, freshness, and privacy;
- row-level security design and test ownership;
- refresh, gateway/capacity, workspace, and operational ownership;
- publish, overwrite, access, sensitivity, and rollback authority.

Optional native Power BI, PBIR, PBIP, Fabric, or Tabular Editor checks are
reported only when their commands are installed and the project scope permits
them.

## Promotion boundary

`examples/` is not a scratch area. A promoted leaf must contain its own
`README.md` and `proof.json`, identify its source run, carry a curated marker,
and remain understandable without importing this repository.

## Seed packaging boundary

The package whitelist contains the System seed, not active operational state.
The `prepack` guard allows blank `.gitkeep` placeholders and a blank
`workspace/history/runs.jsonl`. It refuses non-empty history and mutable files
under the workspace operational directories. It does not inspect or remove
curated examples, and a refusal leaves all evidence in place.
