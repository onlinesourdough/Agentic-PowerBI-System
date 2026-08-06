# PowerBI-template

Turn a business question into an owned, validated Power BI model and report.

## Start

1. Read `workspace/PROJECT-BRIEF.md` and preserve resolved AIOS or project context.
2. Name the decision, audience, KPI definitions, data owners, refresh/runtime,
   proof, and optional Design-template handoff.
3. Model first: use a star schema, explicit relationships, hidden technical
   keys, and explicit measures.
4. Report second: one page per business question, with the decision and its
   evidence ahead of decoration.
5. Validate every PBIP/PBIR/TMDL edit.

## Routes

- `.agents/skills/powerbi/SKILL.md`: business analytics and decision framing
- `.agents/skills/pbip/SKILL.md`: PBIP/PBIR/TMDL structure
- `.agents/skills/dax/SKILL.md`: measures and semantic logic
- `.agents/skills/report/SKILL.md`: report composition, states, and filters
- `.agents/skills/fabric/SKILL.md`: service and Fabric work
- `.agents/skills/validation/SKILL.md`: completion proof

Pi is optional. Use `scripts/doctor.mjs` and `scripts/validate-pbip.mjs`
directly in any harness.

## Rules

- Keep KPI name, DAX, format, interpretation, limitation, and business owner
  together.
- Use deterministic validation before visual inspection or guesses.
- Preserve data ownership, row-level security, refresh, and workspace
  boundaries.
- Keep secrets, tenant identifiers, private data, and generated local Power BI
  state out of Git.
- Ask before deleting pages or visuals, rebinding, publishing, overwriting
  service items, changing `.platform` IDs, or changing access/refresh policy.
- Finish with changed files, validation evidence, unavailable checks, and
  remaining risk.

## Proof

```sh
node scripts/doctor.mjs
node scripts/validate-pbip.mjs . --ignore-tests
npm test
```

Use `pbir validate`, Fabric CLI, Tabular Editor, DAX Studio, Power BI Desktop,
or `pbi-tools` only when the project and available environment justify them.
