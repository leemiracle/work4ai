---
name: inspect-infrastructure-health
description: Inspect reviewed Grafana infrastructure evidence for host or fleet CPU usage, memory load, disk space, and system load. Use for server-health checks, capacity symptoms, resource saturation, disk pressure, cloud or local host comparisons, and bounded infrastructure triage.
---

# Inspect Infrastructure Health

Run the fixed `grafana.infrastructure` pack and present its normalized evidence without modifying the monitored environment.

## Safety contract

- Use only `grafana_profile_status`, `grafana_list_packs`, `grafana_run_pack`, `grafana_get_evidence`, and `grafana_resolve_link`.
- Accept only profile and scope aliases; one declared `LIVE`, `REPLAY`, or `SIMULATED` origin; bounded current and baseline windows; and opaque references returned by these tools.
- Never accept or construct PromQL, SQL, URLs, headers, datasource IDs, panel JSON, variables, or raw provider requests.
- Never write to Grafana, a datasource, a host, an alert, or a deployment. This skill cannot authorize remediation or a patch.
- Confirm the environment before using `LIVE`. Do not silently switch among `LIVE`, `REPLAY`, and `SIMULATED`.

## Workflow

1. Establish `profileAlias`, `scopeAlias`, origin, and a current window no longer than seven days. Ask for an earlier equal-duration, non-overlapping baseline only when comparison matters.
2. Call `grafana_profile_status({profileAlias})`. Stop on `ERROR` or blocked readiness; disclose `PARTIAL` readiness before continuing.
3. Call `grafana_list_packs({profileAlias})` and require the exact active pack ID `grafana.infrastructure`.
4. Create one non-secret idempotency key for this attempt and reuse it for any exact retry.
5. Call `grafana_run_pack` with that key, the aliases, `packId: "grafana.infrastructure"`, origin, current window, and optional baseline window.
6. Inspect CPU usage, memory load, disk free space, and system load in the returned signal order. Preserve returned units, severity, and direction; do not combine unlike units.
7. Call `grafana_get_evidence({reportRef,evidenceRef})` only for evidence references returned by this report and needed to support a material claim.
8. Call `grafana_resolve_link({reportRef,linkRef})` only for a link reference returned by the same report when a trusted Grafana panel link helps the user verify the evidence. Never accept a URL as input.

Treat an issue as a rule-backed alert only when it has `classification: SIGNED_RULE` and `kind: ALERT`. Treat `classification: DEVIATION` as a deviation, not an anomaly. Do not infer root cause from saturation alone, and do not treat absent or stale telemetry as a healthy host.

## Interpret report status exactly

- `COMPLETE`: all expected evidence completed; evaluate each signal and issue rather than saying “healthy” by default.
- `EMPTY`: the bounded scope and window returned no usable evidence; this is an evidence gap, not zero usage.
- `STALE`: the evidence is too old for a current health claim; report its observed and collected times.
- `PARTIAL`: expected evidence is missing, failed, or mixed; state which conclusions remain unsupported.
- `CONTRADICTORY`: evidence conflicts; show the conflicting evidence references and do not choose a preferred value.
- `ERROR`: collection failed or was rejected; report the sanitized error and stop.

## Completion format

Return scope, origin, current and baseline windows, overall status, a compact CPU/memory/disk/load table, issues with their returned classification, evidence gaps or contradictions, evidence references for every material claim, and trusted panel links only when resolved from report-owned references.
