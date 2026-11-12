# Real Grafana packaged-plugin E2E

This opt-in test runs the **actual copied Grafana Observability plugin**, its
MCP stdio server, signed provider worker, and all five capability packs against
real, disposable Grafana, Prometheus, Loki, Tempo, and PostgreSQL containers.
The telemetry is synthetic and every evidence artifact remains `SIMULATED`.
It is not a production connection or a cloud-resource test.

## Run

From the repository root, with Node.js 22.19+ and a running local Docker daemon:

```sh
npm run test:grafana:live
GRAFANA_E2E_MAJOR=11 npm run test:grafana:live
npm run test:grafana:matrix
```

The default is the exact Grafana 12 image in [matrix.json](matrix.json).
The selector accepts only 10, 11, 12, or 13. The matrix command runs all four
pinned versions sequentially and fails if any one fails. Ordinary `npm test`
does not start containers; the live test skips unless `GRAFANA_E2E_DOCKER=1` is
set. Both `docker compose` and standalone `docker-compose` are supported.
The runner rejects a remote Docker endpoint and inherited Docker/Compose
overrides, creates a unique project, and removes that project's containers,
networks, disposable volumes, and project-built seed image when it finishes.

## What is verified

- Exact Grafana version and actual PostgreSQL `SELECT`-only role privileges.
- A temporary owner-only authority root, an in-memory test signing key, and
  validation/activation using the **shipped** authority CLI.
- The copied package launches without ancestor `node_modules` and exposes all
  five activated packs: infrastructure, APM, logs, IoT/edge, and business KPIs.
- All 17 frozen operations return complete, non-empty real datasource evidence.
  This includes metric-named Prometheus fields, native Loki JSON-label log
  frames, Tempo matching-span resource attributes, and PostgreSQL KPI values.
- Report idempotency, signed issue rules, opaque evidence/source-link retrieval,
  all 17 sealed evidence artifacts, provider lineage, and subject redaction.

The normal non-Docker suite separately checks denied, empty, stale, partial,
contradictory, malformed, rate-limited, and out-of-scope responses with an
explicitly synthetic HTTP server. Those cases are not represented as real
Grafana failures or real token revocations.

## Isolation and fixture details

All real providers share an `internal: true` Docker network. Only a small,
fixed-target HTTP gateway also joins an ingress bridge. Its single published
port is assigned by Docker and bound to `127.0.0.1`; it forwards only the
reviewed Grafana read routes. This accommodates Docker versions that do not
publish ports from an internal-only network. Grafana uses anonymous Viewer
access, the database is internal-only, and storage is temporary. No credential,
service account, OS-keychain entry, marketplace registration, or persistent
Grafana configuration is created.

Prometheus explicitly disables lifecycle/admin APIs and preserves the fixture's
`instance="host-alpha"` label. The seed emits a 97% CPU incident, 20% checkout
errors, 1,250 ms latency, a stale edge device, error/security log events, slow
traces, and fixed business KPIs. The database role can read only the seeded KPI
table. The test authority permits only this loopback endpoint and `SIMULATED`
origin; it cannot authorize a real environment.

The matrix files are executable test inputs, not evidence that a version was
run. Record actual results and remaining release gates in the
[test guide](../../README.md).
A passing Docker test does not by itself prove production credentials, native
keychain rotation/revocation, or installation inside the Codex UI.
