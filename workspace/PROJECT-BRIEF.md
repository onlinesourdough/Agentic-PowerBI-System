# Agentic Power BI System project brief

This file is the active decision contract for one bounded Power BI outcome. Do
not fill unknowns with invented data or service evidence.

- **Business question:** What must the report answer?
- **Decision:** What will someone do differently with the answer?
- **Audience and owner:** Who decides, who uses the result, and who owns it?
- **KPIs:** For each KPI record the name, definition, source, data owner,
  format, target, interpretation, limitation, and approval status.
- **Data:** Canonical systems, tables, grain, relationships, freshness, quality,
  privacy, and access boundaries.
- **Model:** Star-schema facts and dimensions, explicit relationships, hidden
  technical keys, and explicit measures.
- **Security:** Row-level security roles, filter logic, owner, test evidence,
  and unresolved access risks.
- **Refresh and runtime:** Desktop, gateway, workspace, schedule, capacity,
  credentials/connection ownership, freshness expectation, and operational
  owner. Keep credentials and connection details out of this file.
- **Report behavior:** Pages, filters, drill paths, loading/no-data/error/stale
  states, accessibility, and mobile requirements.
- **Publish authority:** Approved workspace/item, promotion authority, overwrite
  boundary, sensitivity/access review, and rollback path.
- **Design handoff:** Optional path to an approved Agentic Design System bundle
  and the decisions it settles; the handoff does not replace validation.
- **Proof:** The real question, model validation, refresh, access, publish, and
  decision journey that must pass.
- **Non-goals:** What the first complete result deliberately excludes.
