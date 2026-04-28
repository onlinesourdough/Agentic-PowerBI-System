---
name: semantic-modeling
description: Design and review Power BI semantic models: star schema, fact/dimension grain, relationships, measure tables, field metadata, hidden keys, display folders, and model quality.
---

# Semantic Modeling

Use this skill for semantic model design and review.

## Modeling principles

- Prefer star schema: facts at measurable grain, dimensions for filtering/grouping.
- Hide technical keys and relationship columns unless users need them.
- Use explicit measures; discourage implicit measures.
- Add descriptions and display folders for measures and important fields.
- Use one-direction relationships by default.
- Avoid many-to-many and bidirectional relationships unless justified.
- Mark date tables and create useful date attributes.

## Review checklist

- Grain documented for each fact table.
- Dimension keys unique and facts match dimensions.
- Relationships are active, correctly cardinalized, and named consistently.
- Numeric attributes have correct summarization.
- Measures have format strings, descriptions, and display folders.
- Hidden columns are hidden from report consumers.
- Business terminology is consistent with `.agent/SYSTEM.md`.

## Deterministic checks

Use available tools before guessing:

```bash
pbir model <Report.Report> -d
fab get "Workspace.Workspace/Model.SemanticModel" -q definition -f
```

For local PBIP, inspect `.SemanticModel/definition/tables/*.tmdl` and `relationships.tmdl`.
