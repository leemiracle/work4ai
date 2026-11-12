---
name: review-business-kpis
description: Review approved Grafana business-intelligence evidence for revenue, conversion, and operational KPIs. Use for bounded KPI scorecards, financial or operational metric checks, baseline comparisons, and business-unit reviews without changing source systems.
---

# Review Business KPIs

Run the fixed `grafana.business-kpis` pack for an enrolled business unit or KPI set and keep financial and operational conclusions evidence-bound.

## Safety contract

- Use only `grafana_profile_status`, `grafana_list_packs`, `grafana_run_pack`, `grafana_get_evidence`, and `grafana_resolve_link`.
- Accept only profile and scope aliases; one declared `LIVE`, `REPLAY`, or `SIMULATED` origin; bounded current and baseline windows; and opaque references returned by these tools.
- Never accept or construct SQL, provider queries, URLs, headers, datasource IDs, panel JSON, variables, account identifiers, or raw database requests.
- Keep Grafana, PostgreSQL and other datasources, dashboards, alerts, financial systems, and operational systems read-only.
- Confirm `LIVE` access. Do not mix `LIVE`, `REPLAY`, and `SIMULATED` values, and label simulated financial data prominently.

## Workflow

1. Establish `profileAlias`, an enrolled business or KPI `scopeAlias`, origin, and a current window no longer than seven days. Use an equal-duration, non-overlapping baseline for change claims.
2. Call `grafana_profile_status({profileAlias})`. Stop on `ERROR` or blocked readiness; disclose `PARTIAL` readiness.
3. Call `grafana_list_packs({profileAlias})` and require the exact active pack ID `grafana.business-kpis`.
4. Create one non-secret idempotency key and reuse it only for an exact retry.
5. Call `grafana_run_pack` with that key, the aliases, `packId: "grafana.business-kpis"`, origin, current window, and optional baseline window.
6. Review revenue, conversion, and the enrolled operational KPI in returned order. Preserve returned units, severity, direction, nulls, and time basis; never add values with incompatible currencies or units.
7. Call `grafana_get_evidence({reportRef,evidenceRef})` only for report-owned references needed to substantiate a material KPI claim.
8. Call `grafana_resolve_link({reportRef,linkRef})` only for a same-report link reference that helps a human inspect the enrolled Grafana view. Never accept a URL as input.

Use regression language only when a returned issue has `classification: SIGNED_RULE` and `kind: REGRESSION`, supported by its qualifying baseline evidence. Treat `classification: DEVIATION` only as a deviation. Do not present observed KPIs as audited financial statements, forecasts, causal impact, or investment advice.

## Interpret report status exactly

- `COMPLETE`: expected KPI evidence completed; assess the returned signals and issues instead of assuming targets were met.
- `EMPTY`: no usable KPI evidence was returned; do not substitute zeros.
- `STALE`: evidence is too old for the requested reporting period; state the timestamps.
- `PARTIAL`: a KPI, unit, source, or baseline is missing, failed, or mixed; limit comparisons to supported values.
- `CONTRADICTORY`: KPI evidence conflicts; preserve both sides and do not choose a preferred business result.
- `ERROR`: collection failed or was rejected; report the sanitized error and stop.

## Completion format

Return scope, origin, reporting and baseline windows, overall status, a unit-aware KPI table, issues with their returned classification, gaps and contradictions, evidence references for every material claim, and only successfully resolved report-owned links.
