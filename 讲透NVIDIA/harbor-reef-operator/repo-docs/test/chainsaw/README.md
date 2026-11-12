<!--
SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Chainsaw end-to-end tests

These tests target seams that the Go unit suite cannot exercise: the CRD
openAPI schema, the operator's RBAC, the controller's Secret-watch wiring,
the Pod-fallback patch path, and the real Harbor API contract. Unit tests
use a fake k8s client and a stub Harbor; everything below requires a live
cluster with the operator deployed and a live Harbor instance.

## Suites

| Path | What it proves |
|---|---|
| `crd-schema/` | The CRD enforces enum + required-field validation at admission time. A drift between the CRD YAML and the Go API types would slip past unit tests but fail here. |
| `cascade-delete/` | When a `ProxyCache` CR is deleted, the operator removes the Harbor proxy project and the registry endpoint via the finalizer. Implicitly validates the ClusterRole `update` verb on `proxycaches` (finalizer add/remove). The pagination + "empty before delete project" logic in `DeleteAllRepositoriesInProject` is covered by `pkg/harbor/client_test.go`; this e2e deliberately stays out of Harbor proxy-cache populate behaviour. |
| `secret-watch/` | The controller's `Watches(&Secret{})` wiring fires a reconcile within seconds of a referenced Secret being created -- well below the 30s requeue interval. Unit tests cover the mapping function in isolation but cannot prove the informer is wired up. |
| `health-status/` | The operator reads Harbor's registry-endpoint health (`GET /api/v2.0/registries/{id}`) and surfaces it on `status.health`. Unit tests stub Harbor with the same Go structs used to encode/decode, so they cannot prove the health-read (or credential PUT/ping) wire format matches Harbor's real v2.0 API. Uses a public upstream (registry.k8s.io) so it needs no credentials. |
| `pod-fallback/` | The Pod-fallback controller patches `spec.containers[].image` to the value in `harbor.rewrite/original-upstreams` when a Pod enters `ImagePullBackOff`/`ErrImagePull`. Validates the controller-runtime predicate, the JSON6902 patch syntax, and the per-container idempotency annotation against a real kubelet -- none of which the Go unit suite (fake client, no kubelet) can exercise. |

## Runner contract

The tests are parameterized via three environment variables that the
runner (Makefile, CI job, or your shell) must set:

| Variable | Format | Example |
|---|---|---|
| `HARBOR_API_BASE` | full URL with scheme | `https://harbor.example.com` |
| `HARBOR_API_HOST` | host only, no scheme | `harbor.example.com` |
| `HARBOR_ADMIN_PASS` | plaintext Harbor admin password | `(from secret)` |

No internal hostnames are committed to the repository. The Makefile ships
public-safe defaults (`harbor.example.com`) so a casual `make chainsaw`
fails loudly rather than hitting a stale internal target.

## Running

```bash
make chainsaw-install              # one-time: pull the chainsaw binary
cp .chainsaw.env.example .chainsaw.env
# Edit .chainsaw.env with the host + URL for your Harbor instance.
make chainsaw
```

`.chainsaw.env` is gitignored. The Makefile sources it before invoking
chainsaw and falls back to fetching `HARBOR_ADMIN_PASS` from the
in-cluster admin secret if you have not set one in the env file.

### CI

CI is expected to inject the same three variables from a secret store
(Vault for NVIDIA-internal CI). The Makefile's behaviour is identical
whether the variables come from `.chainsaw.env` or the surrounding
environment.

### Running a single suite

```bash
chainsaw test test/chainsaw/cascade-delete/
```

(With `HARBOR_API_BASE`, `HARBOR_API_HOST`, and `HARBOR_ADMIN_PASS` set
in your environment.)

## Isolation between runs

All cluster-scoped resources derive their names from chainsaw's per-test
`$namespace`, which is randomly generated. Parallel CI pipelines therefore
cannot collide on Harbor project names (which are global). Test cleanup
runs on success and on failure.

## Adding a test

1. Create `test/chainsaw/<name>/chainsaw-test.yaml` (a chainsaw `Test`
   resource) plus any resource files it references.
2. Lint with `chainsaw lint test -f test/chainsaw/<name>/chainsaw-test.yaml`.
3. Run with `make chainsaw` against your Harbor-equipped cluster.
4. Document the test's contract in the table above (`What it proves`).

Keep e2e tests focused on the seams that unit tests *cannot* see. Anything
testable with a fake client belongs in `pkg/.../*_test.go`.