---
name: investigate-application-performance
description: Investigate reviewed Grafana APM evidence for request rate, error rate, and operational latency. Use when an application is slow, erroring, dropping traffic, regressing against a baseline, or needs a bounded request-rate, error, and p95 latency health assessment.
---

# Investigate Application Performance

Run the fixed `grafana.apm` pack to compare request, error, and latency signals while keeping provider queries and configuration server-side.

## Safety contract

- Use only `grafana_profile_status`, `grafana_list_packs`, `grafana_run_pack`, `grafana_get_evidence`, and `grafana_resolve_link`.
- Accept only profile and scope aliases; one declared `LIVE`, `REPLAY`, or `SIMULATED` origin; bounded current and baseline windows; and opaque references returned by these tools.
- Never accept or construct PromQL, LogQL, TraceQL, SQL, URLs, headers, datasource IDs, panel JSON, variables, or raw provider requests.
- Keep Grafana, datasources, alerts, deployments, and runtime state read-only. A result cannot authorize a code patch or production change.
- Confirm `LIVE` access and never substitute `REPLAY` or `SIMULATED` evidence without saying so.

## Workflow

1. Establish `profileAlias`, `scopeAlias`, origin, and a current window no longer than seven days. When the user asks whether performance regressed, use an earlier baseline that does not overlap the current window and has exactly the same duration.
2. Call `grafana_profile_status({profileAlias})`. Stop on `ERROR` or blocked readiness; disclose `PARTIAL` readiness before collection.
3. Call `grafana_list_packs({profileAlias})` and require the exact active pack ID `grafana.apm`.
4. Create one non-secret idempotency key and reuse it only for an exact retry.
5. Call `grafana_run_pack` with that key, the aliases, `packId: "grafana.apm"`, origin, current window, and optional baseline window.
6. Review request rate first, then the bounded error-code table, error rate, p95 latency, and required `grafana.apm.traces.slow` Tempo evidence. Preserve units and distinguish volume changes from reliability or latency changes.
7. Call `grafana_get_evidence({reportRef,evidenceRef})` only for report-owned references needed to substantiate a claim. Do not claim a specific error code or trace cause unless returned evidence explicitly supports it.
8. Call `grafana_resolve_link({reportRef,linkRef})` only for a same-report link reference that helps verify the finding. Never accept a URL as input.

Call a change a regression only when a returned issue has `classification: SIGNED_RULE` and `kind: REGRESSION`; it must cite its qualifying equal-duration, non-overlapping baseline evidence. Treat `classification: DEVIATION` as a deviation. Correlation among traffic, errors, latency, and slow traces is not proof of causation.

## Interpret report status exactly

- `COMPLETE`: all expected evidence completed; still distinguish healthy, warning, and critical returned signals.
- `EMPTY`: no usable requests or performance evidence were returned; do not translate this into zero errors.
- `STALE`: evidence is too old for a current APM claim; expose its timestamps.
- `PARTIAL`: evidence or baseline coverage is missing, failed, or mixed; narrow the conclusion accordingly.
- `CONTRADICTORY`: signals conflict; preserve the competing evidence and withhold a single causal conclusion.
- `ERROR`: collection failed or was rejected; report the sanitized error and stop.

## Completion format

Return scope, origin, both windows when used, overall status, request rate, returned error-code counts, error rate, latency signals, slow-trace evidence, issues with their returned classification, evidence gaps and contradictions, evidence references for material claims, and only report-owned trusted links that were resolved successfully.
