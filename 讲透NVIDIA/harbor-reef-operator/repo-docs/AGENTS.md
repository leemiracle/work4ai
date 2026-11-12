<!--
SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# AGENTS.md

Guidance for AI coding agents working in this repository. Human-facing docs live
in [README.md](./README.md); this file is the fast path for making correct
changes.

## What this is

`harbor-reef-operator` is a Go Kubernetes operator (module name
`harbor-reef-operator`, Go 1.24, `sigs.k8s.io/controller-runtime`) for the
Harbor Reef image caching system. It ships two controllers:

- **Pod fallback** (`pkg/controller/pod`) — reverts Pod container images from the
  Harbor cache back to the original upstream when a Pod hits
  `ImagePullBackOff`/`ErrImagePull`. Always active. Reads the
  `harbor.rewrite/original-upstreams` annotation.
- **ProxyCache** (`pkg/controller/proxycache`) — reconciles the cluster-scoped
  `ProxyCache` CRD (`harbor-reef.nvidia.com/v1alpha1`) into Harbor registry
  endpoints and proxy-cache projects via the Harbor v2.0 REST API. **Opt-in:
  only runs when `HARBOR_URL` is set.**

## Layout

```text
main.go                             # Manager bootstrap, scheme + controller wiring, env parsing
pkg/apis/v1alpha1/                  # ProxyCache API types + zz_generated.deepcopy.go (generated)
pkg/controller/pod/reconciler.go    # Pod fallback controller
pkg/controller/proxycache/          # ProxyCache reconciler + metrics.go
pkg/harbor/client.go                # Harbor v2.0 REST client
helm-charts/harbor-reef-operator/   # Chart: CRD (crds/), RBAC, Deployment
test/chainsaw/                      # e2e (chainsaw) — see its README.md
Dockerfile                          # distroless multi-stage build
```

## Build, test, verify

```bash
go build -o harbor-reef-operator .   # build
make test                            # unit tests == go test -v ./...
gofmt -l . && go vet ./...           # format check + vet (run before committing)
```

- **Always run `make test` and `go vet ./...` after changing Go code.** There is
  no linter config beyond `gofmt`/`go vet`; follow standard Go idioms.
- **Unit tests** use a fake k8s client and a stubbed Harbor — no cluster needed.
  Add coverage here for anything testable with a fake client.
- **e2e (`make chainsaw`)** needs a live cluster + live Harbor and is for seams
  unit tests cannot reach (CRD admission schema, RBAC, Secret-watch wiring, the
  real Harbor wire format, the kubelet-driven Pod patch). It won't run in a
  sandbox. See [test/chainsaw/README.md](./test/chainsaw/README.md) before
  touching it. Config comes from `HARBOR_API_BASE`, `HARBOR_API_HOST`,
  `HARBOR_ADMIN_PASS` (via `.chainsaw.env`, gitignored).

## Conventions

- **SPDX headers are mandatory** on every new source/YAML/Markdown file:
  ```go
  // SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  // SPDX-License-Identifier: Apache-2.0
  ```
  (use `<!-- ... -->` for Markdown; `# ...` for YAML). Copy the form from a sibling file.
- **Commits**: recent history uses Conventional Commits with a scope, e.g.
  `fix(proxycache): ...`, `chore: ...`. Contributions require a DCO sign-off
  (`git commit -s`) — see [CONTRIBUTING.md](./CONTRIBUTING.md). Only commit or
  push when the user asks.
- `pkg/apis/v1alpha1/zz_generated.deepcopy.go` is **generated** — don't hand-edit;
  regenerate if you change the API types.
- Keep the repo **vendor-neutral**: no internal hostnames, no Datadog-specific
  assets (a recent commit deliberately stripped them). Public-safe defaults like
  `harbor.example.com` are intentional and should stay.

## Behavior that's easy to get wrong

- **CRD ↔ Go type drift**: the CRD YAML (`helm-charts/.../crds/proxycache-crd.yaml`)
  and the Go types in `pkg/apis/v1alpha1/types.go` must stay in sync. The
  `crd-schema` chainsaw suite exists to catch drift that unit tests miss — update
  both together.
- **ProxyCache writes are health-gated**: an existing endpoint Harbor reports
  `healthy` is left untouched; only an `unhealthy` endpoint triggers a
  `PUT .../registries/{id}` + `ping`. This is what makes rotated credentials
  propagate. Don't reintroduce unconditional skip-if-exists.
- **`phase` vs `health` are different signals**: `phase: Ready` means the operator
  applied config successfully; `health` mirrors Harbor's own upstream ping. A
  Ready+unhealthy row is a valid state (stale/rejected credential), not a bug.
- **`proxycache_healthy` gauge only flips on a definitive Harbor reading** —
  unknown status / transient read failures / reconcile errors hold the previous
  value to avoid spurious alerts. Preserve that guard.
- **Pod patching is per-container idempotent** via the
  `harbor-reef/patched-containers` annotation — only patch containers currently
  in backoff, and never re-patch. This prevents restart loops.
- **Deletion cascade** is finalizer-driven and gated by `HARBOR_RETAIN_ON_DELETE`.

## Key env vars

`HARBOR_URL` (enables ProxyCache controller), `HARBOR_ADMIN_SECRET` /
`HARBOR_ADMIN_SECRET_KEY`, `HARBOR_RETAIN_ON_DELETE`, `WATCH_NAMESPACE`
(comma-separated; cluster-wide if unset), `POD_NAMESPACE` (where credential
secrets are read), `LEADER_ELECTION_ENABLED`. Full table in the README.
