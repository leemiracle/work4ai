# Deploying Transformers CI Public Grafana

This directory packages the Transformers CI public observability stack for
Kubernetes. The Helm chart is intentionally self-contained and values-driven so
it can be deployed into a cluster without changing application code. Production
values (internal domains, certificate ARNs, secret wiring) are **not** committed
to this public repository — supply them through a private values file.

## Contents

- `helm/` contains the Helm chart. It deploys:
  - **OpenTelemetry Collector** — receives OTLP traces from CI jobs
  - **Grafana Tempo** — persistent trace storage (StatefulSet)
  - **pytest-trace-exporter** — custom Prometheus metrics exporter from traces
  - **Prometheus** — metrics storage (StatefulSet)
  - **Grafana** — public read-only dashboards
  - **CI data publisher** — optional scheduled publisher for trace-derived datasets (CronJob)
  - **NetworkPolicy** — optional cluster-boundary traffic policy for blast-radius reduction
- `helm/env/example.yaml` carries public-safe placeholder values. Copy it to a
  private file (e.g. `helm/env/private.yaml`, git-ignored) for a real deployment.
- `helm/transformers-ci-secrets.example.yaml` is a template for the sensitive
  runtime Secret. Copy it to `helm/transformers-ci-secrets.yaml` (git-ignored),
  fill it locally, and never commit it.
- `helm/dashboards/` holds the Grafana dashboard JSONs mounted into Grafana.
- `scripts/deploy.py` checks the current Kubernetes context, creates the
  namespace when needed, optionally applies a local Secret file, runs Helm, then
  restarts only the workloads a config-only change left on stale config and
  verifies the stack came back healthy. See [Deploying](#deploying) and
  [Config Changes and Restarts](#config-changes-and-restarts).
- `scripts/logs.py` finds the current running pod for a given component and
  prints recent logs.
- `scripts/tempo.py` queries the Tempo trace store (and Prometheus) through the
  public read-only Grafana proxy — no kubectl needed. Useful for reconciling a
  green dashboard against a red GitHub run: `search`/`spans`/`status` inspect a
  test's spans (even inside a >16 MB sharded trace), and `promql` reads the exact
  metric a panel uses. Run `deploy/scripts/tempo.py -h` for examples.

## Chart Behavior

Tempo and Prometheus run as StatefulSets backed by PVCs (`ebs-gp3` by default),
so trace and metric history survives pod restarts. Grafana, the OTel Collector,
and the trace exporter run as Deployments; the CI data publisher runs as a
CronJob.

Sensitive values are loaded from a pre-created Secret (referenced by
`secrets.name`); non-secret runtime config lives in `values.yaml` / your env
values file. Set `secrets.create: false` in production and provide the Secret
through your secret-management mechanism — either a local Secret file applied by
`deploy.py --secret-file`, or the generic `externalSecret` block (a
provider-specific secret-sync CRD such as Infisical's `InfisicalSecret`).

The trace exporter and CI data publisher clone code from this repository at pod
startup. For code-only changes, pass a source revision so the pods pick it up
(see [Source Code Changes](#source-code-changes)).

## Deploy

Render manifests locally without touching the cluster:

```bash
deploy/scripts/deploy.py --dry-run -f deploy/helm/env/private.yaml
```

Create or update the Secret in the target namespace and deploy:

```bash
cp deploy/helm/transformers-ci-secrets.example.yaml deploy/helm/transformers-ci-secrets.yaml
$EDITOR deploy/helm/transformers-ci-secrets.yaml
deploy/scripts/deploy.py \
  -n transformers-ci \
  --secret-file deploy/helm/transformers-ci-secrets.yaml \
  -f deploy/helm/env/private.yaml
```

Deploy without applying a Secret file (Secret already exists, e.g. synced by an
external-secret operator):

```bash
deploy/scripts/deploy.py -n transformers-ci -f deploy/helm/env/private.yaml
```

Use `--context` to refuse any other kube context:

```bash
deploy/scripts/deploy.py \
  --context infra:opensource-aws-use1-prod-54 \
  -n transformers-ci \
  -f deploy/helm/env/private.yaml
```

## Logs

Fetch recent logs for a component (`grafana`, `otelcol`, `trace-exporter`,
`tempo`, `prometheus`, `ci-data-publisher`):

```bash
deploy/scripts/logs.py \
  --context infra:opensource-aws-use1-prod-54 \
  -n transformers-ci \
  -c trace-exporter \
  --since 2h \
  --grep 'error|traceback|crashed|HTTPError'
```

Print only the latest error block:

```bash
deploy/scripts/logs.py -n transformers-ci -c trace-exporter --since 2h --last-error
```

## Network Policies

Network policies are disabled by default so the example chart renders safely in
any cluster/CNI. To reduce blast radius from the public Grafana, trace-exporter,
and OTLP endpoints, enable the policy in private values and set `allowedCIDRs` to
the cluster/VPC address space that should be reachable:

```yaml
networkPolicy:
  enabled: true
  allowedCIDRs:
    - 10.0.0.0/8
  allowSameReleasePods: true
```

When enabled, the chart renders a `NetworkPolicy` selecting pods in this Helm
release with `policyTypes: [Ingress, Egress]`. It allows ingress from, and
egress to, only the configured CIDRs plus same-release pod-to-pod traffic.
Standard Kubernetes `NetworkPolicy` supports CIDRs, not DNS names — if the
deployment performs runtime source/package downloads, add tightly scoped
`networkPolicy.extraEgress` rules for the required address ranges.

## Secrets

The chart references a Secret by `secrets.name` (default
`transformers-ci-secrets`). The required key names are configurable under
`secrets.keys`:

| values key             | default Secret key       | used by           |
| ---------------------- | ------------------------ | ----------------- |
| `traceApiKey`          | `trace-api-key`          | OTLP ingestion    |
| `grafanaAdminPassword` | `grafana-admin-password` | Grafana admin     |
| `githubToken`          | `gh-token`               | GitHub metadata   |
| `hfToken`              | `hf-token`               | ci-data-publisher |

For production, set `secrets.create: false` and provide the Secret through your
preferred mechanism. The `externalSecret` block can have Helm manage a
provider-specific secret-sync CRD:

```yaml
secrets:
  create: false
  name: transformers-ci-secrets

externalSecret:
  enabled: true
  apiVersion: secrets.infisical.com/v1alpha1
  kind: InfisicalSecret
  spec:
    # Provider-specific configuration belongs in private values.
```

> The `githubToken` key matters for dashboard correctness: without it the
> trace-exporter and ci-data-publisher call the GitHub API unauthenticated
> (60 req/hr), get rate-limited, and PR/commit metadata can render blank.

## Keeping Docker Compose and Helm in Sync

The `dashboard/` directory is the **single source of truth** for the dashboard
JSONs (it's where contributors edit them, and the Docker Compose stack mounts
them directly). The entries under `deploy/helm/dashboards/` are **symlinks** into
`dashboard/` — Helm follows them when embedding the chart, so there is only ever
one real copy and nothing to sync. (Recreate a link with
`ln -s ../../../dashboard/<file> deploy/helm/dashboards/<file>`.)

The exporter helper endpoints use the same bare paths (`/failure`, `/badge`,
`/summary`) in both deployments, so a single dashboard JSON works for both.

### Dashboard Changes

Edit dashboards in `dashboard/` only — the chart symlinks pick the changes up
automatically.

Checklist:

- [ ] New dashboards: add the JSON file to `grafana.dashboards.files` in `helm/values.yaml`
- [ ] Version bump: run `dashboard/bump-version.py X.Y.Z` (edits the canonical `dashboard/` copies)

### Config Changes and Restarts

Helm rolls a pod only when its **pod template** changes. A change that touches
just a ConfigMap — `tempo.yaml`, `grafana.ini`, the Prometheus scrape config —
rewrites the ConfigMap and leaves the running pod alone, and these processes read
their config only at startup. `helm upgrade` reports success while the change sits
inert.

Only three workloads tie their config to the pod template with a `checksum/*`
annotation, so only those roll by themselves:

| Workload | Annotation | Rolls automatically on |
|---|---|---|
| `otelcol` | `checksum/config` | any config change |
| `grafana` | `checksum/alerting` | alerting changes only — **not** `grafana.ini` |
| `prometheus` | `checksum/recording-rules` | rules changes only — not scrape config |
| `tempo`, `trace-exporter`, `backup-status-exporter` | none | nothing |

`deploy.py` closes that gap: it diffs the rendered manifest against the live
release, maps each changed ConfigMap/Secret to the workloads that mount or
reference it, skips anything Helm is already rolling, and then converges the rest
in dependency order (`tempo → trace-exporter → otelcol → backup-status-exporter →
prometheus → grafana`), one at a time, waiting for each to be healthy.

| Changed ConfigMap | Action | Why |
|---|---|---|
| `grafana-dashboards`, `grafana-dashboards-restricted` | none | Grafana's file provisioner rescans the directory (10s default) |
| `prometheus-config` | reload in place | Prometheus runs `--web.enable-lifecycle`; keeps the TSDB head, no scrape gap |
| anything else | restart | config is read only at startup |
| anything on a CronJob | none | the next scheduled run picks it up |

Preview the decision without touching the cluster:

```bash
deploy/scripts/deploy.py --plan -f deploy/helm/env/private.yaml
```

Relevant flags: `--plan`, `--diff`, `--skip-restart <name>`, `--no-restart`,
`--restart-all`, `--no-verify`, `--no-source-check`, `--allow-source-rollback`,
`--timeout`.

**The plan also reports what a change removes.** `change ConfigMap/X` is equally
true of adding a key and of deleting one, so the plan prints per-resource line
counts and flags any config key that is live but absent from the render — the
shape of an accidental revert of something applied by hand. `--diff` prints the
hunks. Secret values are never expanded into a diff: key names and byte counts
only, so a rotation is visible without printing the credential.

**Cloned source revisions are checked for direction.** `traceExporter.sourceRevision`
and `ciDataPublisher.sourceRevision` are checked out by an init container at pod
start, so the values file — not `main` — decides which commit prod runs, and a
values file that has fallen behind the live release rolls the code *backwards*
while `helm upgrade` reports success. The plan resolves both revisions against the
local clone, prints the move, and refuses anything that is not a fast-forward
(including a revision it cannot resolve, which is not the same as approval) unless
`--allow-source-rollback` says so. After the deploy, `verify` reads the revision
back out of the running pod and fails on a mismatch.

**Rotated secrets are detected separately.** Credentials delivered by a
secret-sync CRD never appear in a manifest diff — the chart renders identically
before and after a rotation, because the values live in the secret store. So
instead of diffing, `deploy.py` compares **when the live Secret was last written**
(`metadata.managedFields[].time`) against **when each consuming pod started**. A
pod older than the Secret it references is still serving the previous credential,
because secrets are injected with `env … secretKeyRef` and read once at startup.

```
restart needed (Secret written after the pod started)
  Deployment/trace-exporter  [single replica: brief gap]
    app-secrets written 2026-07-30T13:23:30Z, pod started 2026-07-29T06:54:20Z
```

Only Secret **metadata** is read — the jsonpath never touches `.data`, so no
secret value is fetched, printed or held in memory.

Two limitations worth knowing:

- **Secret-level, not key-level.** `managedFields` carries one timestamp per field
  manager, not per key, so adding or rotating *any* key flags every workload that
  references that Secret — even ones that only read a different key.
- It detects a *write*, not necessarily a changed value. A sync operator normally
  writes only on a real change (a no-op reconcile does not bump the timestamp), and
  `helm upgrade` does not touch these Secrets, so deploys do not cause false
  positives. The plan prints both timestamps so you can judge.

Either way the result is self-correcting: once the pod restarts, its start time is
newer than the Secret and it stops being flagged. Use `--no-secret-check` to skip
the check entirely.

### Source Code Changes

The trace exporter and CI data publisher clone code from this repository at pod
startup. For code-only changes that do not otherwise change the rendered
manifests, pass a source revision during upgrade (a git commit SHA is
recommended):

```bash
helm upgrade transformers-ci ./deploy/helm \
  --namespace transformers-ci \
  -f deploy/helm/env/private.yaml \
  --set-string traceExporter.sourceRevision="$GIT_SHA" \
  --set-string ciDataPublisher.sourceRevision="$GIT_SHA"
```

These values render as pod template annotations, so changing them triggers a
rollout for `trace-exporter` and updates the `ci-data-publisher` CronJob pod
template for future jobs.

### Deployment Verification

`deploy.py` verifies this itself and exits non-zero on failure: it waits on every
workload's rollout (discovered from the rendered manifest, so new workloads are
covered automatically), then checks each pod is Ready, has no
`CrashLoopBackOff`/image-pull failure, and gained no new container restarts
relative to a pre-deploy baseline. Pass `--no-verify` to skip it.

To check manually:

```bash
kubectl rollout status deployment/grafana -n transformers-ci
kubectl rollout status deployment/otelcol -n transformers-ci
kubectl rollout status deployment/trace-exporter -n transformers-ci
kubectl rollout status deployment/backup-status-exporter -n transformers-ci
kubectl rollout status statefulset/tempo -n transformers-ci
kubectl rollout status statefulset/prometheus -n transformers-ci
```

### Windows Checkouts

`helm/dashboards/*` are git symlinks (mode `120000`) into `dashboard/`, read by the
chart with `.Files.Get`. Git for Windows defaults to `core.symlinks=false`, which
materialises each one as a text file containing its target path — Helm would then
ship `../../../dashboard/foo.json` to Grafana *as the dashboard body*, so the
deploy succeeds and the dashboards are silently empty.

`deploy.py` refuses to deploy in that state and prints the fix, and separately
validates that every rendered dashboard parses as JSON.

Symlinks do work on Windows, but need an OS privilege *and* a git setting that
only applies during checkout — so set it when you clone:

```powershell
git clone -c core.symlinks=true https://github.com/huggingface/transformers-ci.git
```

Enable Developer Mode (Settings > Privacy & security > For developers) or run git
elevated, so Windows permits symlink creation. With the privilege granted and the
flag set, git fails the checkout loudly (`unable to create symlink`) instead of
silently writing text files. `git config --global core.symlinks true` makes every
future clone behave this way.

To repair a checkout that is already broken — the setting does not convert files
already on disk, so delete them and let git restore them:

```powershell
git config core.symlinks true
Remove-Item deploy\helm\dashboards\*
git checkout -- deploy/helm/dashboards
```

To verify, check the **working tree** — `git ls-files -s` is not a valid check
here, because the index reports mode `120000` even when the working tree holds
plain text files:

```bash
test -L deploy/helm/dashboards/pytest-observability-dashboard.json && echo OK || echo BROKEN
```

Or just run `deploy/scripts/deploy.py --plan`, whose chart-integrity phase performs
this check.
