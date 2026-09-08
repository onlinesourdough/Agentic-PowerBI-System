---
name: powerbi
description: "Business analytics workflow for Power BI: translate business questions into model needs, DAX measures, report pages, KPIs, and interpretation. Use for planning dashboards, cases, and analytical storytelling."
---

# Power BI Business Analytics

Use this skill when the work is about the business question, KPI design, dashboard structure, or analytical interpretation.

## Workflow

Use the parts relevant to the requested outcome and preserve resolved context.
Business interpretation or a page plan does not require creating a model;
for a model/report build, establish model requirements before report design.

1. Clarify the business question:
   - Who is the audience?
   - What decision should the report support?
   - What is the grain of analysis?
   - What dimensions and filters matter?
2. Translate to model requirements:
   - fact tables
   - dimensions
   - relationships
   - required measures
3. Translate to report structure:
   - KPI row
   - main explanatory visual
   - supporting detail
   - slicers/filters
   - short interpretation text
4. Validate the result:
   - measures make business sense
   - visuals answer the question
   - assumptions/limitations are documented

For a material data, model, or KPI decision, follow the
[shared data-change boundary](../../../docs/contract.md#data-change-boundary),
inspect the relevant authorized brief and artifacts plus reasonable
alternatives, and record the chosen option, rationale, consequences, and
decision owner. Ask only when that authority or decision is genuinely absent.

## Output format

```text
Business question:
Audience:
Required data/model:
Measures:
Report page plan:
Interpretation:
Validation:
```

## Harness-neutral audit contract

Use this contract when the route is an audit. The input is an optional bounded
`focus` value; it is not a transcript. Return:

```text
semantic model structure:
DAX measures and metadata:
Power Query/data shaping risks:
report design and storytelling:
validation blockers/warnings:
recommended next actions:
```

Include exact paths for findings and identify the owner or missing evidence for
each material risk. Keep the business question, decision, grain, KPI owner,
data boundary, and proof journey visible in the result.

When diagnosing a data-domain defect, reproduce the affected decision or
metric at the nearest safe representative boundary before proposing a fix. If
the original behavior cannot be reproduced, say why; then use the
[canonical regression recipe](../../../docs/validation.md#representative-data-domain-regressions)
and report the result or evidence gap.

## Good Power BI habits

- One page should answer one business question.
- Prefer explicit measures over implicit aggregations.
- Use business names, descriptions, and consistent formatting.
- Report conclusions should say what to do, not only what changed.
