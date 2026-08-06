---
name: dax
description: Create, review, and document Power BI DAX measures for KPIs, ratios, time intelligence, and business analytics. Use when writing or validating DAX.
---

# DAX Measures

## Workflow

1. Define the measure in business language.
2. Identify required tables/columns and filter context.
3. Prefer base measures + derived measures.
4. Add format string, description, and display folder.
5. Validate with a DAX query/tool when possible.

## Patterns

- Use `DIVIDE()` for ratios.
- Use variables for readability.
- Avoid unnecessary row-by-row iterators.
- Explain `CALCULATE()` filter changes.
- Confirm date table before time intelligence.

## Output format

```text
Name:
Business definition:
DAX:
Format string:
Display folder:
Description:
Validation idea:
```

Do not edit model files unless the target table/file is clear.
