---
name: agentic-powerbi-system
description: Primary System route for durable, decision-first Power BI work, specialist routing, and append-only proof.
---

# Agentic Power BI System primary route

This is the one primary System skill. It preserves operational truth in
`workspace/` and uses the existing Power BI specialist skills for the work
they own. It is a filesystem workflow, not a service or orchestration runtime.

## Route

1. Read `workspace/PROJECT-BRIEF.md` and inspect relevant records in
   `workspace/history/runs.jsonl` before selecting a route. Match the input
   reference and route, not copied request text, to find the previous run.
2. Name the decision, audience, KPI contract, data owner, grain, freshness,
   RLS owner, refresh/runtime boundary, publish authority, and proof needed.
3. Route the work to one or more specialist skills:
   - `powerbi` for business question, decision, KPI definitions, and audit;
   - `pbip` for PBIP/PBIR/TMDL structure and safe project edits;
   - `dax` for explicit measures and semantic logic;
   - `report` for page plans, report states, visuals, filters, and layout;
   - `fabric` for approved service/workspace checks and publish operations;
   - `validation` for deterministic local and optional native proof.
   - `system-audit` for a strictly read-only periodic repository, workspace,
     or combined accumulated-state audit.
   A `system-audit` returns its result directly and does not continue to the
   run-writing or example-promotion steps below.
4. Create `workspace/runs/<run-id>/` and write structured `input.json`,
   `output.json`, and `proof.json`. Failures write `failure.json`; recoveries
   write `recovery.json` in their new run directory.
5. Append one JSON object to `workspace/history/runs.jsonl` with the run ID,
   timestamps, status, input/output/proof references, previous-run relation,
   and failure/recovery references. Do not rewrite an earlier record.
6. Promote an example only when the caller explicitly requests curation. The
   promoted directory must contain its own `README.md` and `proof.json` and
   must be understandable without importing this repository.

Normal package creation runs the read-only seed guard. It permits the blank
seed placeholders and deliberate curated examples, but refuses to package a
non-empty ledger or mutable workspace evidence without changing that evidence.

## Input contract

The route accepts structured references:

```text
route: audit | page-plan | validation | model | report | service | system-audit | system-proof
input_ref: repository path, fixture reference, or approved work reference
decision_ref: workspace/PROJECT-BRIEF.md or a more specific brief reference
focus: optional bounded audit focus
business_question: required for a page-plan route
target: repository/project path for validation
scope: repository | workspace | both (required for system-audit)
promote_example: explicit true only when curation is desired
```

An input reference identifies the source; it is not a place to store a request
transcript, credentials, tenant identifiers, or private data.

## Output and proof contract

Every completed route returns or records:

```text
status
run_id
previous_run_id
previous_run_relation
decision_ref
specialist_routes
output_ref
proof_ref
blockers
warnings
unavailable_checks
remaining_risks
```

The Power BI/domain `audit` route must cover semantic model structure, DAX and
measure metadata, data
shaping risks, report storytelling, validation blockers/warnings, and next
actions. A `system-audit` returns exactly `PASS`, `FAIL`, or `BLOCKED` with
observable evidence, evidence gaps, and the smallest next action; it never
writes a run record. A page plan must return page title, audience and decision, required
measures/fields, KPI row, main visuals, slicers/filters, interpretation text,
and a validation checklist. A validation route must run deterministic checks
first, then report optional native checks only when installed, with blockers,
warnings, exact paths, unavailable checks, and commands run.

## Power BI gates

The route never substitutes a generated artifact for evidence. Keep each KPI's
name, DAX, format, interpretation, limitation, source, and business owner
together. Preserve star-schema grain, explicit relationships, hidden technical
keys, explicit measures, data ownership, RLS, refresh/runtime, workspace, and
publish authority. Ask before deleting or rebinding report assets, changing
`.platform` identity, publishing, overwriting service items, or changing
access/refresh policy.

## Failure and recovery

Keep a failed run and its evidence available. A recovery is a new run with
`previous_run_relation: recovery`, `previous_run_id` set to the unresolved
failed run, and a recovery reference. Recover a failed run at most once. An
ordinary continuation uses `predecessor`; the first relevant run uses `null`.

## Reference implementation

`workspace/engine/tracer.py` is the deterministic reference route. It proves
prior-run inspection, success, failure, recovery, append-only history, and
explicit example promotion with a fixed demonstration clock. It does not claim
that a live Power BI model, refresh, RLS, Fabric workspace, or publish exists.
