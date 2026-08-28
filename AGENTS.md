# Agentic Power BI System

Turn a business question into an owned, validated Power BI model, report, and
decision journey that can retain its operational proof across runs.

## System contract

This repository is the standalone Agentic Power BI System. It follows the
System Template contract: `workspace/` is persistent operational truth,
`examples/` contains only deliberate standalone proof, and `docs/` contains
the public contract and validation recipe. The System is self-contained and is
not installed into another agent runtime.

The primary route is `.agents/skills/agentic-powerbi-system/SKILL.md`. It first
inspects relevant records in `workspace/history/runs.jsonl`, routes Power BI
work through the specialist skills, and preserves input, output, proof,
failure, recovery, and previous-run references. Request content is represented
by references and structured facts, never by transcript files. Do not put
secrets, tenant identifiers, private data, or generated local Power BI state in
the repository.

## Start

1. Read `workspace/PROJECT-BRIEF.md` and preserve any resolved business or
   project context.
2. Name the decision, audience, KPI definitions, data owners, refresh/runtime,
   proof, and optional Agentic Design System handoff.
3. Model first: use a star schema, explicit relationships, hidden technical
   keys, and explicit measures.
4. Report second: one page per business question, with the decision and its
   evidence ahead of decoration.
5. Validate every PBIP/PBIR/TMDL edit and record unavailable optional tools.

## Specialist routes

- `.agents/skills/powerbi/SKILL.md`: business question, decision, KPI, and
  audit framing
- `.agents/skills/pbip/SKILL.md`: PBIP/PBIR/TMDL structure and safe edits
- `.agents/skills/dax/SKILL.md`: measures and semantic logic
- `.agents/skills/report/SKILL.md`: page plans, states, visuals, and filters
- `.agents/skills/fabric/SKILL.md`: service and Fabric work under authority
  gates
- `.agents/skills/validation/SKILL.md`: deterministic completion proof

The specialist skills are harness-neutral contracts. The deterministic doctor,
PBIP validator, Python System engine, and tests live under
`workspace/engine/` and are callable directly or through the package scripts.
Normal `npm pack`/publish packaging also runs the read-only seed guard; mutable
workspace evidence causes an explicit failure and is never removed.

## Rules

- Keep KPI name, DAX, format, interpretation, limitation, and business owner
  together.
- Use deterministic validation before visual inspection or guesses.
- Preserve data ownership, row-level security, refresh, workspace, and publish
  authority boundaries.
- Ask before deleting pages or visuals, rebinding reports, changing `.platform`
  IDs, publishing, overwriting service items, or changing access/refresh
  policy.
- Do not invent PBIX/PBIP evidence or require optional Power BI tools that are
  unavailable.
- Finish with changed files, validation evidence, unavailable checks, and
  remaining risk.

## Proof

```sh
node workspace/engine/doctor.mjs
node workspace/engine/validate-pbip.mjs . --ignore-tests
npm test
npm pack --dry-run
```

Use `pbir validate`, Fabric CLI, Tabular Editor, DAX Studio, Power BI Desktop,
or `pbi-tools` only when the command is truthfully installed and the project
scope justifies it. Record exact unavailable checks rather than inferring
their result.
