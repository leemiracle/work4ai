# transformers-ci

This project contains CI packages used for the `transformers` project.


## OpenTelemetry


`transformersci.otel`, contains the OpenTelemetry support for `pytest` tests,
that can be used from the main `transformers` repository.

The main pieces are:

- `transformersci.otel.cli`: configures OTEL env vars and launches pytest
- `transformersci.otel.resource_plugin`: optional per-test CPU, RSS, and CUDA memory sampling
- `transformersci.otel.trace_exporter`: converts recent Tempo traces into Prometheus metrics

## CLI Entry Points

Installing the package exposes:

- `configure-ci-otel`
- `pytest-trace-exporter`
- `assign-reviewers`

Example:

```sh
configure-ci-otel \
  --job local_smoke \
  --service-name transformers-tests \
  --protocol grpc \
  --otlp-endpoint http://localhost:5317 \
  -- python3 -m pytest tests/test_cli.py -q
```

## Pytest Plugin

The resource plugin is registered through `pytest11` and stays inert unless resource collection is explicitly enabled with one of:

- `--resource-metrics-file <path>`
- `PYTEST_RESOURCE_METRICS_FILE=<path>`
- `TRANSFORMERS_TEST_RESOURCE_METRICS_FILE=<path>`

Example:

```sh
configure-ci-otel \
  --job resource_demo \
  --service-name pytest-observability-demo \
  --protocol grpc \
  --otlp-endpoint http://localhost:5317 \
  -- \
  python3 -m pytest tests/test_demo_workload.py -q \
  --resource-metrics-file dashboard/data/pytest-resource-metrics.jsonl
```

## GitHub Actions Usage

To use `transformers-ci` in a GitHub Actions workflow:

1. **Add repository secrets:**
   - `OTEL_EXPORTER_OTLP_ENDPOINT` - The OTLP endpoint URL (e.g., `https://transformers-ci-traces.lor-e.huggingface.cool`)
   - `OTEL_EXPORTER_OTLP_TOKEN` - Raw bearer token, without the `Authorization=Bearer ` prefix

   `configure-ci-otel` can now set `OTEL_TRACES_EXPORTER`,
   `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_ENDPOINT`, and
   `OTEL_EXPORTER_OTLP_HEADERS` for you from CLI flags.
   Use the traces collector host here, not the Grafana UI host:
   `transformers-ci-traces.lor-e.huggingface.cool`, not `transformers-ci.lor-e.huggingface.cool`.

2. **Update your workflow:**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install transformers-ci
        run: pip install transformers-ci[otel]

      - name: Run tests with OpenTelemetry tracing
        run: >-
          configure-ci-otel
          --service-name transformers-tests
          --protocol http
          --otlp-endpoint "${OTEL_EXPORTER_OTLP_ENDPOINT}"
          --token "${OTEL_EXPORTER_OTLP_TOKEN}"
          -- pytest tests/ -v
        env:
          OTEL_EXPORTER_OTLP_ENDPOINT: ${{ secrets.OTEL_EXPORTER_OTLP_ENDPOINT }}
          OTEL_EXPORTER_OTLP_TOKEN: ${{ secrets.OTEL_EXPORTER_OTLP_TOKEN }}
```

### Mirroring to a staging backend

To send every span to a second (staging) backend in addition to the primary,
add `--staging-endpoint` (and `--staging-token` if staging uses its own auth).
This attaches a second span processor inside the pytest run, so each span is
exported to both backends; a flaky staging box does not affect the primary
export. Staging reuses the primary `--protocol` unless you override it with
`--staging-protocol` (e.g. prod over `http` but the stage box only speaks
`grpc`).

```yaml
      - name: Run tests with OpenTelemetry tracing (mirrored to staging)
        run: >-
          configure-ci-otel
          --service-name transformers-tests
          --protocol http
          --otlp-endpoint "${OTEL_EXPORTER_OTLP_ENDPOINT}"
          --token "${OTEL_EXPORTER_OTLP_TOKEN}"
          --staging-endpoint "${OTEL_STAGING_OTLP_ENDPOINT}"
          --staging-protocol grpc
          --staging-token "${OTEL_STAGING_OTLP_TOKEN}"
          -- pytest tests/ -v
        env:
          OTEL_EXPORTER_OTLP_ENDPOINT: ${{ secrets.OTEL_EXPORTER_OTLP_ENDPOINT }}
          OTEL_EXPORTER_OTLP_TOKEN: ${{ secrets.OTEL_EXPORTER_OTLP_TOKEN }}
          OTEL_STAGING_OTLP_ENDPOINT: ${{ secrets.OTEL_STAGING_OTLP_ENDPOINT }}
          OTEL_STAGING_OTLP_TOKEN: ${{ secrets.OTEL_STAGING_OTLP_TOKEN }}
```

The endpoint/token/protocol can also come from the environment instead of flags
via `TRANSFORMERS_TEST_OTEL_STAGING_ENDPOINT`,
`TRANSFORMERS_TEST_OTEL_STAGING_TOKEN`, and
`TRANSFORMERS_TEST_OTEL_STAGING_PROTOCOL`. If `--staging-token` is omitted,
staging falls back to the primary token; if `--staging-protocol` is omitted, it
falls back to the primary protocol.

### Local Testing (No Endpoint Required)

To test the instrumentation locally without sending traces to a remote endpoint:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests with local resource metrics collection (no OTLP endpoint needed)
configure-ci-otel --force-export-traces --job local_test -- \
  pytest tests/test_demo_workload.py -v \
  --resource-metrics-file /tmp/pytest-metrics.jsonl
```

This writes per-test CPU, RSS, and CUDA metrics to a local JSONL file without requiring an OTLP endpoint.

## Reviewer assignment

`.github/workflows/assign-reviewers.yml` is a reusable workflow that requests up to two reviewers
on a pull request, ranked by how many lines the PR changes in the files they own. Call it from the
repository being reviewed:

```yaml
on:
  pull_request_target:
    branches: [main]
    types: [ready_for_review]

jobs:
  assign_reviewers:
    permissions:
      contents: read
      pull-requests: write
    uses: huggingface/transformers-ci/.github/workflows/assign-reviewers.yml@main
```

Only the resolution logic lives here (`transformersci.reviewers`). The ownership data stays in the
repository being reviewed, at `.github/scripts/codeowners_for_review_action` — who owns what is
that repo's decision. Point `codeowners_file` elsewhere if it lives somewhere else. A file
resolves to its owners in this order, most specific first:

1. `# Reviewers: @login` in the leading comment block of a model's `modular_*.py`/`modeling_*.py`
2. a path rule in the codeowners file
3. the model's modality — its section in `docs/source/en/_toctree.yml`, matched by an
   `@@modality/<slug> @login` rule
4. the `*` catch-all

Each reviewer is requested in a separate call, and anyone who is not a collaborator is skipped
with a `::warning::` so the next-ranked owner takes the slot — one stale codeowners entry costs
one reviewer, not all of them.

Call it from `pull_request_target`: requesting a review needs a write token, which a fork's
`pull_request` run does not get. The checkout is the PR's base and nothing from the head is
executed; the head is only read file-by-file through the API, as text, to see models and
`# Reviewers:` tags the PR adds, and every login is gated on the collaborator check. The
codeowners file is never read from the head, and `pr-ci-security-gate.yml` can block untrusted
PRs from touching it at all — list it in that workflow's `protected_paths` input, which is opt-in
and leaves the gate unchanged for callers that do not set it.

## Dashboard

An initial Grafana dashboard implementation lives under [`dashboard/`](dashboard/README.md).
