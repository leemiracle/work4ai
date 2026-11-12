<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Getting Started

This guide covers three common paths:

- Create another operator that imports the shared kit API.
- Work on the included example operator.
- Apply the included samples in `config/samples`.

## Repository Layout

The root module is the reusable kit:

- `api/v1alpha1`: shared media-function API types such as `Control`,
  `Transport`, `VideoFormat`, `AudioFormat`, `DataFormat`, and `BaseStatus`.
- `examples/reference-operator`: an Operator SDK project that uses the shared
  API types in example CRDs, controllers, manifests, a Helm chart, and samples
  under `config/samples`.

Other operators can import the shared API directly:

```go
import mfov1alpha1 "github.com/NVIDIA/media-function-operator-kit/api/v1alpha1"
```

The root `Makefile` delegates most operator targets to
`examples/reference-operator` and also generates DeepCopy code for the shared
root API package.

## Create Your Own Operator

Start from a normal Operator SDK project in your own repository:

```sh
operator-sdk init \
  --plugins go/v4 \
  --domain example.com \
  --repo github.com/example/my-media-operator

operator-sdk create api \
  --group media \
  --version v1alpha1 \
  --kind MyMediaFunction \
  --resource \
  --controller
```

Add this kit as a dependency:

```sh
go get github.com/NVIDIA/media-function-operator-kit@<version>
```

Use the shared types in your CRD package:

```go
package v1alpha1

import mfov1alpha1 "github.com/NVIDIA/media-function-operator-kit/api/v1alpha1"

type MyMediaFormat struct {
	Audio mfov1alpha1.AudioFormat `json:"audio"`
}

type MyMediaInput struct {
	Control   mfov1alpha1.Control   `json:"control"`
	Transport mfov1alpha1.Transport `json:"transport"`
	Format    MyMediaFormat         `json:"format"`
}
```

Your controller logic lives in your operator's `internal/controller` package.
The included example controller lives in
`examples/reference-operator/internal/controller`.

## Work on the Example Operator

The included example operator can be used like a regular Operator SDK project:

```sh
cd examples/reference-operator
make operator-sdk
./bin/operator-sdk create api \
  --group example.com \
  --version v1alpha1 \
  --kind ExampleMediaFunction \
  --resource \
  --controller
```

That adds another CRD and controller to the included example operator. To create
a separate operator, follow the previous section instead.

When adding a media function to this example operator:

- Import reusable media API types from root `api/v1alpha1`.
- Define example-operator CRDs in `examples/reference-operator/api/v1alpha1`.
- Keep operator-specific helper types in the example API package until they are
  useful across multiple operators.
- Put reconciler code under `examples/reference-operator/internal/controller`.
- Add samples under `examples/reference-operator/config/samples`.

Useful example implementation files:

- `examples/reference-operator/internal/controller/reconcile_common.go`: shared
  reconcile loop.
- `examples/reference-operator/internal/controller/reconcile.go`: Deployment
  assembly and common pod wiring.
- `examples/reference-operator/internal/controller/mxl.go`: MXL config, domain
  mount, and runtime profile.
- `examples/reference-operator/internal/controller/colorpatternmediafunction_controller.go`:
  sender example.
- `examples/reference-operator/internal/controller/srtgatewaymediafunction_controller.go`:
  receiver and Service example.

## Try the Samples

Sample CR manifests use the Operator SDK layout in
`examples/reference-operator/config/samples/`. First build and deploy the
example operator manager (`examples/reference-operator`):

```sh
make docker-build IMG=<registry>/reference-media-functions-operator:<tag>
make docker-push IMG=<registry>/reference-media-functions-operator:<tag>
make deploy IMG=<registry>/reference-media-functions-operator:<tag>
```

Or install with Helm:

```sh
helm upgrade --install reference-media-functions-operator \
  ./examples/reference-operator/charts/reference-media-functions-operator \
  -n reference-media-functions-operator --create-namespace \
  --set image.repository=<registry>/reference-media-functions-operator \
  --set image.tag=<tag> \
  --set mediaFunction.mxlImage=<registry>/<mxl-media-function>:<tag>
```

For kustomize deploys, set `MXL_MEDIA_FUNCTION_IMAGE` on the manager before applying
the MXL samples (required — there is no default MXL media-function image):

```sh
kubectl set env deployment/rmf-operator-controller-manager \
  -n reference-media-functions-operator \
  MXL_MEDIA_FUNCTION_IMAGE=<registry>/<mxl-media-function>:<tag>
kubectl apply -k examples/reference-operator/config/samples
```

The default kustomization applies:

- `mxl-domain-tmpfs.yaml`
- `mxl-demo-mediafunctions.yaml`

MXL samples need `mediaFunction.mxlImage` and an MXL domain PVC. RTP remains in
the shared API transport type for compatibility, but the example operator does not
wire an RTP controller runtime.

Apply the samples:

```sh
kubectl apply -k examples/reference-operator/config/samples
kubectl get colorpatternmediafunctions -A
kubectl get srtgatewaymediafunctions -A
kubectl get pods -A -l app.kubernetes.io/managed-by=reference-media-functions-operator
```

## Prepare an MXL tmpfs Demo Domain

The MXL demo samples expect a shared domain mounted into each media-function pod.
For local demos, the domain can be backed by a host tmpfs directory exposed
through a local `StorageClass`, `PersistentVolume`, and `PersistentVolumeClaim`.

Set the node and namespace used by the demo:

```sh
NODE=<node-hostname>
NAMESPACE=default
DOMAIN_PATH=/dev/shm/mxl/domains/default-demo/data
```

Create the tmpfs domain directory and a demo `domain_def.json` on the node that
will run the MXL demo pods:

```sh
DOMAIN_ID=6e3db301-6efa-4b70-9b42-7a8a2c3c5a01
ssh ${NODE} "sudo mkdir -p '${DOMAIN_PATH}' && printf '{\"id\":\"%s\"}\n' '${DOMAIN_ID}' | sudo tee '${DOMAIN_PATH}/domain_def.json' >/dev/null && sudo chown -R 10001:10001 /dev/shm/mxl/domains/default-demo && sudo chmod -R ug+rwX /dev/shm/mxl/domains/default-demo"
```

On OpenShift clusters, you can also create the directory through node debug:

```sh
oc debug node/${NODE} -- chroot /host sh -c "mkdir -p '${DOMAIN_PATH}' && printf '{\"id\":\"%s\"}\n' '${DOMAIN_ID}' > '${DOMAIN_PATH}/domain_def.json' && chown -R 10001:10001 /dev/shm/mxl/domains/default-demo && chmod -R ug+rwX /dev/shm/mxl/domains/default-demo"
```

Use a domain ID that matches the MXL static sample if you plan to run
`mxl-static-demo-mediafunctions.yaml`. NMOS-driven samples only require a valid
domain definition at the mounted path.

Create the local `StorageClass`:

```sh
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: mxl-domain-tmpfs
provisioner: kubernetes.io/no-provisioner
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
```

Create the `PersistentVolume` for the node-local tmpfs path:

```sh
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mxl-domain-demo-tmpfs-pv
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: mxl-domain-tmpfs
  local:
    path: ${DOMAIN_PATH}
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - ${NODE}
EOF
```

Create the `PersistentVolumeClaim` in the media-function namespace:

```sh
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mxl-domain-demo-tmpfs
  namespace: ${NAMESPACE}
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: mxl-domain-tmpfs
  volumeName: mxl-domain-demo-tmpfs-pv
  resources:
    requests:
      storage: 1Gi
EOF
```

Verify the backing store:

```sh
kubectl get storageclass mxl-domain-tmpfs
kubectl get pv mxl-domain-demo-tmpfs-pv
kubectl get pvc -n ${NAMESPACE} mxl-domain-demo-tmpfs
```

Reference the PVC from MXL media-function specs:

```yaml
spec:
  parameters:
    mxl:
      claimName: mxl-domain-demo-tmpfs
      mountPath: /mxl-domain
```

This tmpfs setup is demo-only. Data under `/dev/shm` is node-local and
ephemeral, and production deployments should provision the MXL domain outside
individual media-function pods.

## Runtime Contracts

- **MXL media-function image:** set `MXL_MEDIA_FUNCTION_IMAGE` or Helm
  `mediaFunction.mxlImage` to `<registry>/<mxl-media-function>:<tag>`.
  The entrypoint must accept `gst-launch-1.0` pipeline arguments.
  A suitable image is built from the
  [nvnmos `docker/gst-nmos-rs/Dockerfile`](https://github.com/NVIDIA/nvnmos/blob/main/docker/gst-nmos-rs/Dockerfile)
  (`nvnmosd`, `nmossrc` / `nmossink` with `transport=mxl`, non-root UID/GID **10001**).
- The operator mounts the MXL domain PVC and passes `gst-launch-1.0` arguments
  to the container entrypoint. NMOS-controlled endpoints use `nmossink` /
  `nmossrc`; static MXL endpoints use `mxlsink` / `mxlsrc` in the same image.
- The mounted MXL domain path must be writable by UID/GID **10001** and should
  contain `domain_def.json` so `nmossink` / `nmossrc` can resolve the MXL
  domain ID for NMOS-controlled endpoints.
- Static MXL flows use `control.mxl_static`; NMOS-driven MXL uses
  `control.nmos`.

## Build Image Base

The example operator Dockerfile defaults to the public distroless runtime base:

```sh
make docker-build IMG=<registry>/reference-media-functions-operator:<tag>
```

Override the runtime base image with a Docker build argument:

```sh
make docker-build IMG=<registry>/reference-media-functions-operator:<tag> \
  DOCKER_BUILD_ARGS="--build-arg RUNTIME_BASE_IMAGE=<runtime-base-image>"
```
