---
name: monitor-iot-edge
description: Monitor reviewed Grafana telemetry and freshness evidence for IoT devices and edge fleets. Use for smart devices, home automation sensors, remote equipment, wind turbines, space hardware, device-fleet freshness, missing telemetry, and bounded edge-health comparisons.
---

# Monitor IoT and Edge

Run the fixed `grafana.iot-edge` pack for an enrolled device or fleet scope and preserve telemetry gaps explicitly.

## Safety contract

- Use only `grafana_profile_status`, `grafana_list_packs`, `grafana_run_pack`, `grafana_get_evidence`, and `grafana_resolve_link`.
- Accept only profile and scope aliases; one declared `LIVE`, `REPLAY`, or `SIMULATED` origin; bounded current and baseline windows; and opaque references returned by these tools.
- Never accept or construct provider queries, SQL, URLs, headers, datasource IDs, device identifiers, panel JSON, variables, or raw telemetry requests.
- Do not send device commands, change sampling, restart equipment, edit Grafana, or mutate alerts or datasources. This skill is observational only.
- Confirm `LIVE` access. Never combine `LIVE`, `REPLAY`, and `SIMULATED` telemetry into one fleet claim.

## Workflow

1. Establish `profileAlias`, an enrolled device or fleet `scopeAlias`, origin, and a current window no longer than seven days. Use an equal-duration, non-overlapping baseline only when change analysis is needed.
2. Call `grafana_profile_status({profileAlias})`. Stop on `ERROR` or blocked readiness; disclose `PARTIAL` readiness.
3. Call `grafana_list_packs({profileAlias})` and require the exact active pack ID `grafana.iot-edge`.
4. Create one non-secret idempotency key and reuse it only for an exact retry.
5. Call `grafana_run_pack` with that key, the aliases, `packId: "grafana.iot-edge"`, origin, current window, and optional baseline window.
6. Review telemetry first and device freshness second. Preserve returned timestamps, units, severity, direction, nulls, and fleet/device distinctions.
7. Call `grafana_get_evidence({reportRef,evidenceRef})` only for report-owned references needed to support a material device or fleet claim.
8. Call `grafana_resolve_link({reportRef,linkRef})` only for a same-report link reference that helps a human inspect the enrolled Grafana view. Never accept a URL as input.

A stale device is not necessarily offline, unsafe, or failed. An empty telemetry result is an evidence gap, not a zero measurement. Treat a freshness issue as rule-backed only when it has `classification: SIGNED_RULE`; treat `classification: DEVIATION` only as a deviation.

## Interpret report status exactly

- `COMPLETE`: expected telemetry and freshness evidence completed; evaluate the returned device and fleet signals.
- `EMPTY`: no usable telemetry was returned; do not substitute zero values or declare devices healthy.
- `STALE`: the latest evidence exceeds the reviewed freshness bound; state the age and affected scope.
- `PARTIAL`: some devices, signals, or expected evidence are missing, failed, or mixed; avoid a fleet-wide conclusion.
- `CONTRADICTORY`: telemetry conflicts; preserve the evidence references and withhold a single state claim.
- `ERROR`: collection failed or was rejected; report the sanitized error and stop.

## Completion format

Return scope, origin, windows, overall status, telemetry summary and freshness by returned scope with returned severity and direction, issues with their returned classification, gaps and contradictions, evidence references for material claims, and only successfully resolved report-owned links.
