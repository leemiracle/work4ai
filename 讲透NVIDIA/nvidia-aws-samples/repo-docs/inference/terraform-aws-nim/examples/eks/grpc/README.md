# example: eks/grpc

Deploys NVIDIA Maxine **Synthetic Video Detector (SVD)** — a media NIM that serves
inference over **gRPC** — onto an EKS Auto Mode cluster on `g6e.2xlarge`
([1× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/), 48 GB VRAM).

This example exercises the module's gRPC path:

- `protocol = "grpc"` — emits a Kubernetes `Service` with `appProtocol: kubernetes.io/grpc`
  and TCP-passthrough NLB. K8s native gRPC probes (`grpc:` block) replace HTTP probes.
- `nim_type = "custom"` — Maxine NIMs ship no Helm chart on NGC today. The module's raw
  `kubectl apply` path emits a `Deployment` + `Service` directly.

`g6e.2xlarge` is chosen to match the SageMaker `ml.g6e.2xlarge` family so EKS↔SageMaker
performance comparisons stay apples-to-apples (same GPU, same vCPU/RAM).

> [!IMPORTANT]
> **SVD requires NGC private-access program entitlement.** The `base-sync` CodeBuild
> step pulls `nvcr.io/nim/nvidia/synthetic-video-detector:latest`. If your NGC API key
> doesn't have SVD access, base-sync fails with an `unauthorized` error from `nvcr.io`.
> Request access via your NVIDIA contact before applying.

See the root README ["Inference protocols supported"](../../../README.md) section and
[DEVELOPER_REFERENCE.md "Inference Protocols and the Choices in This Module"](../../../DEVELOPER_REFERENCE.md)
for the full background on gRPC vs HTTP NIMs.

---

## Usage

```bash
terraform init
terraform plan
terraform apply
```

Supply `ngc_secret_name` (the name of your NGC API key secret in Secrets Manager) when
prompted, via `-var`, or in a `.tfvars` file. See [variables.tf](variables.tf).

## Apply timeline

**Total wall-clock time: ~20 min** (first apply). VPC/EKS provisioning, base-sync, and
cluster-setup all run concurrently. The `deploy-nim` buildspec polls for the GPU NodePool
before applying the manifest, so it starts immediately and waits inline.

| Concurrent work | Duration |
| --------------------------------------------- | ---------- |
| VPC + EKS cluster provisioning | ~15-20 min |
| CodeBuild: base-sync (pulls SVD image to ECR) + cluster-setup | ~5-10 min |
| CodeBuild: deploy-nim (polls for NodePool, then kubectl apply) | completes within the 20 min window |

## Wait for the pod to be Ready

`terraform apply` returning success means the manifest was applied — the NIM may still
be pulling the model from NGC on first start (~10+ min, see "Cold-start" section below).

```bash
CLUSTER=$(terraform output -json eks_cluster_names | jq -r '.svd')
NAMESPACE=$(terraform output -json eks_namespaces | jq -r '."svd-nim"')
RELEASE=$(terraform output -json eks_release_names | jq -r '."svd-nim"')
REGION=$(aws configure get region)

aws eks update-kubeconfig --name "$CLUSTER" --region "$REGION"
kubectl get pods -n "$NAMESPACE" -w   # wait for STATUS=Running, READY=1/1, then Ctrl-C
```

## Invoking the endpoint (Python client)

SVD does **not** expose gRPC reflection, so `grpcurl` smoke tests require local
`.proto` files. Easier to just run NVIDIA's reference Python client — it ships with
pre-generated stubs and bundled sample videos for end-to-end validation.

**One-time setup** (in any working directory):

```bash
# nim-clients uses Git LFS for the sample videos — install LFS hooks before clone.
brew install git-lfs
git lfs install

git clone https://github.com/NVIDIA-Maxine/nim-clients.git
cd nim-clients/synthetic-video-detector

# uv recommended (avoids macOS Homebrew Python PEP 668 lockout):
brew install uv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

> [!NOTE]
> If you `git clone`d **before** running `git lfs install`, the `.mp4`s under
> `assets/` will be 131-byte LFS pointer files (QuickTime will refuse to open them).
> Run `git lfs pull` from the repo root to swap pointers for real binaries.

**Get the NLB hostname and run the bundled fake sample**:

```bash
LB=$(kubectl get svc -n "$NAMESPACE" "${RELEASE}-svc" \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

python scripts/synthetic-video-detector.py \
  --target "$LB:8001" \
  --video-input assets/fake_sample_video.mp4 \
  --save-csv
```

Flags (per the [SVD docs](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/basic-inference.html)):
- `--target` — NIM endpoint (`host:port`)
- `--video-input` — path to an H.264-encoded MP4 with **constant** frame rate
- `--save-csv` — writes per-frame + overall synthetic probability to CSV

The bundled `fake_sample_video.mp4` should score **>95% synthetic**; the
`real_sample_video.mp4` should score **<5% synthetic**. That's how you confirm the
NIM is actually doing inference and not returning a default.

## Input video constraints

SVD only accepts videos that meet all four:

| Property | Required |
| -------- | -------- |
| Codec | H.264 (no HEVC/H.265, no AV1) |
| Pixel format | 8-bit (`yuv420p`). 10-bit (`yuv420p10le`, H.264 High 10 profile) rejected by hardware decoder |
| Frame rate | Constant (CFR). Variable Frame Rate (VFR) unsupported |
| Container | `.mp4` (the client may reject `.mov`) |

Phone recordings are commonly all four wrong — iPhone in HDR mode records HEVC
Main 10 (10-bit) at variable frame rate in a `.mov` container. Convert with the
recipe below before testing.

```bash
# Inspect:
ffprobe -v error -select_streams v \
  -show_entries stream=codec_name,pix_fmt,r_frame_rate,avg_frame_rate input.mov

# Convert to H.264 8-bit + 30 fps CFR + strip audio:
ffmpeg -i input.mov \
  -c:v libx264 -pix_fmt yuv420p -profile:v high -r 30 -an \
  output.mp4
```

The `-pix_fmt yuv420p` flag forces 8-bit output (otherwise ffmpeg preserves the
source's 10-bit format, which SVD's hardware decoder rejects with
`StatusCode.INVALID_ARGUMENT - Video file format not supported by hardware decoder`).

`brew install ffmpeg` installs both `ffmpeg` and `ffprobe`.

## Cold-start time

First-pod start is **~10+ min** because the NIM downloads the model from NGC on
startup. NIM still auto-selects the GPU-appropriate profile — the wait is the download,
not the selection. The module's profile pre-cache feature (~<2 min cold start) is wired
through the Helm deploy path only; the raw-kubectl path used here doesn't yet plumb it.
Tracked as a follow-up. When Maxine ships an official Helm chart, switch `nim_type` and
caching comes for free.

## Teardown

```bash
terraform destroy
```

The module's `helm_cleanup` `terraform_data` runs `kubectl delete deployment/service`
on destroy (since this is the raw-kubectl path, not Helm), which signals the EKS LB
controller to delete the NLB before the cluster is torn down.

## Outputs

| Name                 | Description                                      |
| -------------------- | ------------------------------------------------ |
| `eks_cluster_names`  | Map of cluster key → EKS cluster name            |
| `eks_release_names`  | Map of deployment key → Deployment name          |
| `eks_namespaces`     | Map of deployment key → Kubernetes namespace     |
