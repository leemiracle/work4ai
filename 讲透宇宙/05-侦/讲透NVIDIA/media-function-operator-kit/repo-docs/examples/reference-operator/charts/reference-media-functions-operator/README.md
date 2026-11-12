<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# reference-media-functions-operator Helm Chart

Helm chart for the example operator (`reference-media-functions-operator`).

## Prerequisites

- Kubernetes cluster access (`kubectl` configured)
- Helm 3 installed
- Operator image already built and pushed
- Required image pull secrets created in target namespaces

## Install / Upgrade

From repository root:

```bash
helm upgrade --install reference-media-functions-operator \
  ./examples/reference-operator/charts/reference-media-functions-operator \
  -n reference-media-functions-operator --create-namespace \
  --set image.repository=<registry>/reference-media-functions-operator \
  --set image.tag=<tag> \
  --set mediaFunction.mxlImage=<registry>/<mxl-media-function>:<tag>
```

MXL media-function image requirements are documented in
[getting-started.md](../../../../docs/getting-started.md#runtime-contracts).
After install, set `MXL_MEDIA_FUNCTION_IMAGE` (or `mediaFunction.mxlImage` above)
and apply the samples in `examples/reference-operator/config/samples`.

## Using Packaged Chart

```bash
helm upgrade --install reference-media-functions-operator \
  ./examples/reference-operator/charts/reference-media-functions-operator-<version>.tgz \
  -n reference-media-functions-operator --create-namespace \
  --set image.repository=<registry>/reference-media-functions-operator \
  --set image.tag=<tag> \
  --set mediaFunction.mxlImage=<registry>/<mxl-media-function>:<tag>
```

## Verify

```bash
helm list -n reference-media-functions-operator
kubectl get pods -n reference-media-functions-operator
```

## Uninstall

```bash
helm uninstall reference-media-functions-operator -n reference-media-functions-operator
```

## Notes on Image Pull Secrets

- `image.imagePullSecrets` is for the operator Deployment (namespace: `reference-media-functions-operator` in the command above).
- `mediaFunction.imagePullSecrets` is used by media function workloads created by the operator.
- Kubernetes secrets are namespace-scoped, so each secret must exist in the same namespace as the pods that use it.
