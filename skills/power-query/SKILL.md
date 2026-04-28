---
name: power-query
description: Work with Power Query M for Power BI data shaping, query folding, parameters, source steps, and refresh-friendly transformations.
---

# Power Query

Use this skill for Power Query / M work.

## Principles

- Keep source extraction, typing, cleaning, and business transformations separated.
- Preserve query folding when using SQL/Fabric sources.
- Use clear step names and avoid hard-coded local paths where possible.
- Push heavy joins/aggregations upstream when appropriate.
- Document source assumptions and refresh implications.

## Workflow

1. Identify source and privacy/credential implications.
2. Inspect existing M query steps.
3. Make the smallest safe transformation.
4. Check whether folding likely remains possible.
5. Document expected output columns and types.

## Common checks

- Column names match TMDL `sourceColumn` values.
- Data types are stable before loading to model.
- Date/time columns are normalized.
- Keys are not accidentally converted to decimals/text inconsistently.
- Null handling is explicit.
