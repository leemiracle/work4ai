---
name: analyze-log-signals
description: Analyze reviewed Grafana log evidence for event patterns, error-rate changes, and enrolled security markers. Use when a user needs bounded log analytics for an incident window, error-log comparison, anomaly triage, operational debugging, or a cautious check of approved security signals.
---

# Analyze Log Signals

Run the fixed `grafana.logs` pack and analyze only the normalized, redacted events and aggregates it returns.

## Safety contract

- Use only `grafana_profile_status`, `grafana_list_packs`, `grafana_run_pack`, `grafana_get_evidence`, and `grafana_resolve_link`.
- Accept only profile and scope aliases; one declared `LIVE`, `REPLAY`, or `SIMULATED` origin; bounded current and baseline windows; and opaque references returned by these tools.
- Never accept or construct LogQL, PromQL, SQL, regex searches, URLs, headers, datasource IDs, panel JSON, variables, or raw provider requests.
- Do not request broader logs to compensate for an empty result. Scope expansion requires a separately reviewed server-side binding.
- Keep logs, Grafana, alerts, datasources, and runtime state read-only. Do not reveal or reconstruct redacted content.
- Confirm `LIVE` access and keep `LIVE`, `REPLAY`, and `SIMULATED` conclusions separate.

## Workflow

1. Establish `profileAlias`, `scopeAlias`, origin, and a current window no longer than seven days. Use an equal-duration, non-overlapping baseline when evaluating a change in error logs.
2. Call `grafana_profile_status({profileAlias})`. Stop on `ERROR` or blocked readiness; disclose `PARTIAL` readiness.
3. Call `grafana_list_packs({profileAlias})` and require the exact active pack ID `grafana.logs`.
4. Create one non-secret idempotency key and reuse it only for an exact retry.
5. Call `grafana_run_pack` with that key, the aliases, `packId: "grafana.logs"`, origin, current window, and optional baseline window.
6. Review log event volume, log error rate, and any returned enrolled security-marker signal. Preserve event times, summaries, units, severity, direction, and ordering.
7. Call `grafana_get_evidence({reportRef,evidenceRef})` only for report-owned references needed to verify a pattern or issue. Summarize bounded patterns; do not reproduce sensitive event content unnecessarily.
8. Call `grafana_resolve_link({reportRef,linkRef})` only for a same-report link reference that helps a human inspect the enrolled Grafana view. Never accept a URL as input.

Use anomaly, regression, or security-event language only when a returned issue has `classification: SIGNED_RULE` and its returned kind and evidence support that label. A marker is not proof of exploitation, attribution, or impact. Treat `classification: DEVIATION` only as a deviation and state the uncertainty.

## Interpret report status exactly

- `COMPLETE`: expected log evidence completed; assess its returned signals rather than assuming there were no problems.
- `EMPTY`: no usable events were returned for the approved scope and window; this is not proof that no events occurred.
- `STALE`: events are too old for a current claim; report their observed and collected times.
- `PARTIAL`: an expected signal, enrolled security marker, or baseline is missing, failed, or mixed; identify the gap.
- `CONTRADICTORY`: evidence conflicts; cite both sides and do not collapse them into one narrative.
- `ERROR`: collection failed or was rejected; report the sanitized error and stop.

## Completion format

Return scope, origin, windows, overall status, event and error-rate summary with returned severity and direction, issues and security markers with their returned classification, gaps or contradictions, evidence references for every material claim, and only successfully resolved report-owned links.
