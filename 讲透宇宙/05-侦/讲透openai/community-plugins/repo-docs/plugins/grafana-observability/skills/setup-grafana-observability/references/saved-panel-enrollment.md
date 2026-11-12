# Saved-panel enrollment envelopes

These examples document the complete input envelope accepted by
`grafana-authorityctl saved-panel enroll`. They are offline review aids, not
active configuration. Copy one to a new owner-controlled JSON file and replace
every example identity, scope, output contract, and saved target with values
reviewed for the intended trust root. The command accepts exactly one saved
target with `refId` `A`; variables, mixed or expression datasources,
transformations, and additional targets are rejected.

The frozen target must bind every enrolled environment, optional service, and
optional provider-native subject to a distinct returned scope field and constrain
each one directly. Every Prometheus or Loki selector
must contain every exact equality matcher. Every Tempo span-set selector must
contain `resource.deployment.environment` and, when enrolled,
`resource.service.name` as exact top-level conjunctions; an enrolled subject uses
its mapped native TraceQL attribute the same way. A PostgreSQL target must be one
direct-table `SELECT`, directly project each mapped scope column, and contain
every exact column equality in its top-level `WHERE` conjunction. Global or
partially scoped aggregation, Prometheus/LogQL label mutation, constant scope
projection, `OR` widening, joins, subqueries, and CTEs do not prove scope.
Enrollment rejects unsupported target structures, and runtime verification
fails closed when any returned row or series omits or mismatches enrolled scope.

## Prometheus example

```json
{
  "schemaVersion": "1.0.0",
  "kind": "grafana-saved-panel-enrollment-v1",
  "dashboard": {
    "uid": "checkout-overview",
    "version": 7,
    "templating": { "list": [] },
    "panels": [
      {
        "id": 12,
        "datasource": { "type": "prometheus", "uid": "prometheus-main" },
        "targets": [
          {
            "refId": "A",
            "datasource": { "type": "prometheus", "uid": "prometheus-main" },
            "expr": "sum by (environment, service) (rate(http_requests_total{environment=\"production\",service=\"checkout\"}[5m]))",
            "instant": false,
            "range": true,
            "format": "time_series"
          }
        ]
      }
    ]
  },
  "panelId": 12,
  "id": "saved-checkout-rate",
  "outputName": "checkout_rate",
  "datasourceIdentitySha256": "1111111111111111111111111111111111111111111111111111111111111111",
  "frame": {
    "resultKind": "TIMESERIES",
    "fields": [
      { "sourceName": "Time", "outputName": "observed_at", "type": "time", "role": "TIME" },
      { "sourceName": "Value", "outputName": "value", "type": "number", "role": "VALUE" }
    ],
    "allowedLabels": ["environment", "service"]
  },
  "minIntervalMs": 1000,
  "scope": { "environment": "production", "service": "checkout" },
  "scopeMappings": { "environment": "environment", "service": "service" }
}
```

## PostgreSQL example

The opaque role hash must identify the separately reviewed database role
configured behind Grafana. The administrator must independently verify that
the role is restricted to `SELECT`; the attestation does not grant or inspect
database permissions. V1 PostgreSQL enrollment rejects every SQL function call,
including aggregate and user-defined functions, because syntactic `SELECT`
alone cannot prove that an executable function is side-effect-free.

```json
{
  "schemaVersion": "1.0.0",
  "kind": "grafana-saved-panel-enrollment-v1",
  "dashboard": {
    "uid": "business-overview",
    "version": 4,
    "templating": { "list": [] },
    "panels": [
      {
        "id": 9,
        "datasource": { "type": "grafana-postgresql-datasource", "uid": "postgres-main" },
        "targets": [
          {
            "refId": "A",
            "datasource": { "type": "grafana-postgresql-datasource", "uid": "postgres-main" },
            "rawSql": "SELECT environment, business_scope, value FROM business_kpis WHERE $__timeFilter(observed_at) AND environment = 'production' AND business_scope = 'checkout-unit' LIMIT 10",
            "format": "table"
          }
        ]
      }
    ]
  },
  "panelId": 9,
  "id": "saved-business-kpis",
  "outputName": "business_kpis",
  "datasourceIdentitySha256": "2222222222222222222222222222222222222222222222222222222222222222",
  "frame": {
    "resultKind": "TABLE",
    "fields": [
      { "sourceName": "environment", "outputName": "environment", "type": "string", "role": "DIMENSION" },
      { "sourceName": "business_scope", "outputName": "business_scope", "type": "string", "role": "DIMENSION" },
      { "sourceName": "value", "outputName": "value", "type": "number", "role": "COLUMN" }
    ],
    "allowedLabels": []
  },
  "minIntervalMs": 1000,
  "scope": {
    "environment": "production",
    "subject": {
      "kind": "BUSINESS_UNIT",
      "ref": "pmsub_ExampleBusinessUnit1234",
      "providerValue": "checkout-unit"
    }
  },
  "scopeMappings": {
    "environment": "environment",
    "subject.ref": "business_scope"
  },
  "postgresMaxRows": 10,
  "postgresReadOnlyIdentity": {
    "roleIdentitySha256": "3333333333333333333333333333333333333333333333333333333333333333",
    "privilegeModel": "SELECT_ONLY"
  }
}
```
