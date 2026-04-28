---
name: dax-measures
description: Write, review, and document Power BI DAX measures for business analytics. Use for KPI measures, time intelligence, validation queries, formatting, and measure descriptions.
---

# DAX Measures

Use this skill when creating or reviewing DAX.

## Measure authoring workflow

1. Define the business meaning in plain language.
2. Identify required tables/columns and filter context.
3. Write the measure using explicit base measures where possible.
4. Add format string, description, and display folder.
5. Validate with DAX query or model tool when available.
6. Explain caveats such as blanks, granularity, or filter sensitivity.

## Patterns

- Use `DIVIDE()` instead of `/` for ratios.
- Use variables for readability.
- Avoid unnecessary iterators over large tables.
- Keep base measures simple, then build derived measures.
- Use `CALCULATE` intentionally and explain filter changes.
- For time intelligence, confirm date table and calendar grain first.

## Output format

For each measure provide:

```text
Name:
DAX:
Format string:
Display folder:
Description:
Validation idea:
```

## Safety

Do not edit DAX in a model file unless the target table/file is clear. If possible, test with DAX Studio, Tabular Editor, pbi-cli/pbir model support, or Fabric execute queries.
