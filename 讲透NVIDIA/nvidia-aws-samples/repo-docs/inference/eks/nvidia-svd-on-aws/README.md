# NVIDIA Synthetic Video Detector (SVD) NIM on AWS

Deployment guide and reference Terraform for running the [NVIDIA Maxine Synthetic Video Detector NIM](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/overview.html) on AWS.

---

## Contents

1. [What this NIM does](#what-this-nim-does)
2. [Access](#access)
3. [AWS instance selection](#aws-instance-selection)
4. [Driver landscape](#driver-landscape)
5. [Multi-GPU and scaling](#multi-gpu-and-scaling)
6. [Capacity options when g6e is constrained](#capacity-options-when-g6e-is-constrained)
7. [Cost reference](#cost-reference)
8. [Autoscaling](#autoscaling)
9. [Deployment — Terraform path](#deployment--terraform-path)
10. [Testing the endpoint](#testing-the-endpoint)
11. [SVD input video constraints](#svd-input-video-constraints)
12. [Troubleshooting](#troubleshooting)
13. [Teardown](#teardown)
14. [References](#references)

---

## What this NIM does

The SVD NIM is a GPU-accelerated microservice that analyzes H.264-encoded MP4 video and returns per-frame plus aggregated probability scores indicating likelihood that the video is AI-generated. Inference is exposed via a bidirectional streaming gRPC API on port 8001.

HTTP on port 8000 exposes license / metadata / metrics endpoints only — there is no HTTP inference endpoint and no HTTP health endpoint. Health checks use the gRPC health protocol (`grpc.health.v1.Health/Check`).

## Access

The SVD container image is gated behind the **AI for Media Private Access Program** on NGC. Access requires manual approval — coordinate with NVIDIA before attempting `docker pull nvcr.io/nim/nvidia/synthetic-video-detector:latest`.

## AWS instance selection

### Bottom line

- **`g4dn.2xlarge` (T4) is the recommended default for POC and cost-sensitive workloads.** Explicitly supported by SVD, ~66% cheaper than g6e, and consistently has on-demand capacity across AZs in us-east-1 when g6/g6e are constrained. Tradeoff: ~5x slower per video than L40S (~24s per sample video vs ~5s on L40S).
- **For throughput / production benchmarking, prefer `g6e` (L40S)** — most memory bandwidth in the supported set. Verify AWS capacity in your target region first.
- **Any of `g4dn` / `g5` / `g6` / `g6e` will run SVD functionally.** Don't get stuck waiting on `g6e` capacity for POC validation.
- **`p4d` / `p4de` / `p5` / `p5e` / `p5en` are NOT supported.** A100 / H100 / B100 lack NVENC/NVDEC. No application-layer workaround exists.

### SVD hardware + software requirements

Source: [Maxine SVD Support Matrix](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/support-matrix.html)

**Supported GPUs** (all FP32):

- Turing: T4
- Ampere: A2, A10, A16, A40
- Ada: L4, L40, L40S, RTX 4090
- Blackwell: RTX PRO 6000 Blackwell Server Edition, RTX 5090, RTX 5080

**Explicit exclusion (verbatim from docs):** _"GPUs without NVENC/NVDEC hardware support are not supported, including A100, H100, and B100 products."_

**Software baseline:**

| Component                | Minimum version |
| ------------------------ | --------------- |
| NVIDIA Driver (Linux)    | 571.21+         |
| CUDA                     | 12.8.1          |
| cuDNN                    | 9.7.1.26        |
| TensorRT                 | 10.9.0.34       |
| DeepStream               | 8.0             |
| Docker                   | latest          |
| NVIDIA Container Toolkit | latest          |

### AWS instance family map

| AWS family      | GPU       | Arch   | VRAM/GPU  | Smallest size | SVD support                        |
| --------------- | --------- | ------ | --------- | ------------- | ---------------------------------- |
| **g4dn**        | T4        | Turing | 16 GB     | g4dn.2xlarge  | **Recommended for POC** — cheapest, most available |
| **g5**          | A10G      | Ampere | 24 GB     | g5.2xlarge    | Supported                          |
| **g6**          | L4        | Ada    | 24 GB     | g6.2xlarge    | Supported (closest to L40S)        |
| **g6e**         | L40S      | Ada    | 48 GB     | g6e.2xlarge   | **Preferred** for production throughput |
| p4d / p4de      | A100      | Ampere | 40/80 GB  | —             | **Not supported** (no NVENC/NVDEC) |
| p5 / p5e / p5en | H100/H200 | Hopper | 80/141 GB | —             | **Not supported** (no NVENC/NVDEC) |

### Recommended ordering for the POC

1. **g4dn.2xlarge** (1× T4, 16 GB) — **default recommendation.** Cheapest supported, most available on-demand in us-east-1, verified end-to-end with this module. ~24s per sample video (~5x slower than L40S). If your per-video latency budget allows, start here.
2. **g5.2xlarge** (1× A10G, 24 GB) — Ampere; ~30% cheaper than g6e, broader availability than g6.
3. **g6.2xlarge** (1× L4, 24 GB) — same Ada arch as L40S, closest performance profile at lower cost.
4. **g6e.2xlarge** (1× L40S, 48 GB) — highest throughput, matches SageMaker `ml.g6e.2xlarge` for apples-to-apples comparison. Verify AWS capacity in your target region first.

### Why not p-family

SVD uses GPU-accelerated H.264 decoding via NVDEC. A100 / H100 / B100 are datacenter-class GPUs designed for ML training and large-model inference — they intentionally omit the video codec engines that consumer/visualization GPUs have. The instance families that include them inherit this limitation. Counterintuitive for customers expecting "biggest = best" — flag this prominently in customer conversations.

## Driver landscape

### EKS (recommended)

**EKS Auto Mode** uses Bottlerocket NVIDIA AMI variants which ship **NVIDIA driver 580** for K8s 1.34+. Older Bottlerocket variants on kernel 6.1 use **R570**. Both satisfy SVD's 571.21+ minimum on any supported instance family.

Source: [AWS Containers Blog: Bottlerocket NVIDIA](https://aws.amazon.com/blogs/containers/bottlerocket-support-for-nvidia-gpus/), [Bottlerocket #4441](https://github.com/bottlerocket-os/bottlerocket/issues/4441).

**EKS-managed node groups with EKS-optimized accelerated AMI** — latest AL2023 release `amazon-eks-node-al2023-x86_64-nvidia-1.36-v20260523` (May 26 2026) ships **NVIDIA driver 580.159.03** and **NVIDIA Container Toolkit 1.19.1-1**.

Source: [amazon-eks-ami v20260523](https://github.com/awslabs/amazon-eks-ami/releases).

**One AMI / driver covers all four candidate families** (g4dn / g5 / g6 / g6e). No per-family AMI matrix.

**Edge case:** EKS node groups pinned to custom or stale AMI IDs may ship older drivers. Confirm latest EKS-optimized accelerated AMI or Auto Mode usage at deployment time.

### SageMaker (not recommended for SVD)

SageMaker has a per-`InferenceAmiVersion` driver matrix where g5 has historically been pinned to driver 470.x — far below SVD's 571.21 minimum. Even if the driver issue is resolved, SageMaker's invocation API is HTTP/1.1 only and does not natively support gRPC, which SVD requires. **EKS avoids both problems.**

### Plain EC2

For plain EC2 deployments, AMI choice determines whether drivers + Container Toolkit are pre-installed:

| AMI                                            | Drivers + Container Toolkit pre-installed? |
| ---------------------------------------------- | ------------------------------------------ |
| **NVIDIA GPU-Optimized AMI** (AWS Marketplace) | Yes                                        |
| **AWS Deep Learning AMI** (DLAMI)              | Yes                                        |
| **Stock Amazon Linux 2 / AL2023 / Ubuntu**     | No — install manually                      |

Source: [NVIDIA GPU-Optimized AMI](https://aws.amazon.com/marketplace/pp/prodview-7ikjtg3um26wq), [DLAMI release notes](https://docs.aws.amazon.com/dlami/latest/devguide/appendix-ami-release-notes.html).

## Multi-GPU and scaling

The SVD docs do not document multi-GPU / tensor-parallel inference at this time. The working assumption is **single-GPU per replica**, and empirical testing with two concurrent video streams against a single pod confirms sequential processing (total wall clock = 2× single-video time).

Implications:

- A single SVD process uses 1 GPU regardless of how many the host has.
- Bigger instances in the same family (e.g. `g6e.12xlarge` with 4× L40S) **don't reduce per-video latency**. They only help if you run multiple replicas per node for concurrent throughput.
- For most POC topologies (single-replica per node), pick the smallest supported size in your chosen family (e.g. `g4dn.2xlarge`, `g6e.2xlarge`).

**Concurrent throughput comes from pod autoscaling.** The `terraform-aws-nim` module deploys SVD with a KEDA-driven ScaledObject that scales pods 1→N based on `DCGM_FI_DEV_GPU_UTIL`. Each additional pod lands on its own GPU node via Karpenter, so N concurrent tenants get N parallel streams. Scale-down is 3 min after load subsides (tuned for bursty video workloads). See [Autoscaling](#autoscaling) below.

## Capacity options when g6e is constrained

In order of preference:

> **NOTE**: **AZ mappings vary by account** ([AWS docs](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html)) so this module references them via `az_id` which is consistent across accounts, where `az_name` is not.

1. **Diversify AZs within a region** — g6e is available in `us-east-1`, `us-east-2`, `us-west-2`. To ensure a higher chance of procuring an instance, in this module example we leverage **Multi-AZ EKS node group** — spreads across AZs in the region, reduces single-AZ insufficient-capacity failures. Karpenter (within EKS auto mode) will search each of those AZs for capacity matching what is defined in the configuration (e.g. `g6e.2xlarge`).
2. **Switch AWS region** - you may try to deploy in another region which may have more capacity for your desired instance type
3. **Fall back to g6 / g5 / g4dn for POC** — functionally equivalent; throughput differs.
4. **On-Demand Capacity Reservation (ODCR)** — guaranteed capacity in a specific AZ. [AWS docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-reservations.html).
5. **Capacity Blocks for ML** — short-term reserved blocks specifically for ML workloads.
6. **AWS TAM coordination** — enterprise-support customers have a TAM who can help plan capacity and request ODCR.

## Cost reference

us-east-1 on-demand, single-GPU 2xlarge sizes (illustrative — check current pricing). The 2xlarge tier is the smallest instance that meets SVD's CPU/memory sidecar minimums for GPU-accelerated decoding.

| Instance     | Approximate hourly | GPU  | vs g6e.2xlarge |
| ------------ | ------------------ | ---- | -------------- |
| g4dn.2xlarge | ~$0.75             | T4   | ~66% cheaper   |
| g5.2xlarge   | ~$1.21             | A10G | ~46% cheaper   |
| g6.2xlarge   | ~$0.98             | L4   | ~56% cheaper   |
| g6e.2xlarge  | ~$2.24             | L40S | baseline       |

At the burst-tier level: with pod autoscaling `min_replicas=1, max_replicas=3`, you're always paying for one node and scaling out on demand. On g4dn.2xlarge that's ~$18/day baseline + ~$0.75/hr per additional concurrent pod during burst.

## Autoscaling

Pod autoscaling is enabled by default in this example. When `enable_autoscaling = true` on the cluster, the vendored module installs three components cluster-wide during the initial apply:

- **KEDA** — event-driven autoscaler that fronts native Kubernetes HPA and lets us scale on Prometheus queries directly (no custom-metrics adapter needed).
- **kube-prometheus-stack** — Prometheus operator + Prometheus (Grafana/Alertmanager disabled to keep the install minimal).
- **NVIDIA DCGM exporter** — Prometheus exporter for GPU telemetry, running as a DaemonSet on GPU nodes. Provides `DCGM_FI_DEV_GPU_UTIL` per-pod so KEDA can scale on real GPU load.

### Why DCGM and not a NIM-emitted metric

Maxine NIMs (SVD included) do not emit a request-load or queue-depth metric. Their `/v1/metrics` endpoint exposes `gpu_power_usage_watts`, `gpu_utilization`, `process_cpu_seconds_total`, and similar telemetry only — no way to correlate scale decisions to actual request pressure. DCGM's per-pod `DCGM_FI_DEV_GPU_UTIL` is the only usable signal, and the module auto-derives it when `nim_type = "custom"`.

### Scaling behavior

The example configures:

```hcl
autoscaling = {
  min_replicas     = 1
  max_replicas     = 3
  scale_down_delay = 180
}
```

Meaning:

- **Floor of 1 pod always warm** — first request never hits a cold start.
- **Scales up to 3 concurrent pods** when sustained GPU utilization exceeds 70% (module default). Each new pod requests its own GPU, so Karpenter provisions a new node.
- **3-minute scale-down stabilization** — module default is 600s (10 min); overriding to 180s because SVD videos are short and workloads tend to be bursty. A 10 min idle GPU tail after each burst is ~$0.13 of wasted spend per event on g4dn.2xlarge.

### Verifying autoscaling

After apply completes:

```bash
aws eks update-kubeconfig --name svd-dev-svd --region <region>

# Addons landed
kubectl get pods -n keda           # keda-operator + keda-metrics-apiserver
kubectl get pods -n monitoring     # kps-* + dcgm-exporter DaemonSet
kubectl get scaledobject -n svd    # your NIM's ScaledObject
kubectl get hpa -n svd             # KEDA auto-creates keda-hpa-<scaledobject-name>

# Watch scaling under load
kubectl get hpa -n svd -w
kubectl get pods -n svd -w
```

Send sustained gRPC inference traffic (multiple parallel `synthetic-video-detector` client processes hitting the NLB) and expect `TARGETS` to climb, `REPLICAS` to grow, and new pods to appear as Karpenter provisions GPU nodes. Scale-down engages 3 min after load subsides.

**Note on load-test drivers.** If you drive load with a shell loop that re-invokes `uv run python …` per video, per-invocation interpreter startup (~5s) leaves the GPU idle between videos and per-pod `DCGM_FI_DEV_GPU_UTIL` averages ~50% instead of pegging at 100%. Use a long-lived driver (open the connection once, loop inside the process) or 2× the number of workers you'd naively expect — otherwise autoscaling looks broken when it's actually the driver that's the bottleneck.

## Deployment — Terraform path

> **Status (2026-07-16):** **Live.** End-to-end validated on g4dn.2xlarge (T4) — bundled SVD sample scored 99.41% SYNTHETIC in ~24s. Pod autoscaling verified 1↔2 under sustained load with zero probe-timeout restarts.

One `terraform apply` provisions VPC + related networking components (or refs existing ones you supply) + EKS Auto Mode cluster + GPU NodePool + ECR mirror + NGC pull secret + SVD `Deployment` (Helm) + gRPC-enabled `Service` backed by an NLB. Sourced from the bundled `terraform-aws-nim` module under [`modules/`](modules/). Eventually this module will be publicly available, but in the meantime it is supplied locally here for your convenience.

Wall-clock: **~20 min** first apply (cluster ~15-20 min, image sync + cluster setup concurrent, deploy + cold start ~10-15 min, mostly parallel).

### Prerequisites

#### Local tooling (modify for your OS as needed)

| Tool       | Minimum version                                                        | Install (macOS)                                                          |
| ---------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| AWS CLI v2 | ≥ 2.15                                                                 | `brew install awscli`                                                    |
| Terraform  | ≥ 1.14 (**required** — needs the new `action_trigger` lifecycle block) | `brew install terraform` — or use `tfenv` (recommended, see below)       |
| kubectl    | ≥ 1.31                                                                 | `brew install kubectl`                                                   |
| ffmpeg     | latest                                                                 | `brew install ffmpeg` — provides `ffmpeg` + `ffprobe`                    |
| git-lfs    | latest                                                                 | `brew install git-lfs`                                                   |
| uv         | latest                                                                 | `brew install uv` (preferred over pip on macOS — avoids PEP 668 lockout) |
| jq         | latest                                                                 | `brew install jq`                                                        |

**Terraform version management — `tfenv` recommended.** If you already have a different Terraform version installed for other projects, `tfenv` lets you switch per-directory without uninstalling. It also makes pinning easy if you want to lock to a specific version:

```bash
brew install tfenv

# Use the latest stable Terraform
tfenv install latest
tfenv use latest

# Or pin to a specific version
tfenv install 1.14.0
tfenv use 1.14.0
```

Verify Terraform version after install:

```bash
terraform version
# Terraform v1.14.0 or newer
```

#### AWS account access

1. **AWS account** with billing enabled.
2. **Programmatic access configured** — `~/.aws/credentials` with an access key + secret, OR an SSO profile, OR an assume-role setup. Whatever lets `aws sts get-caller-identity` succeed.
   ```bash
   aws sts get-caller-identity
   # Should print your AWS account ID, user/role ARN, user ID
   ```
3. **Pick your target region** — g6e is available in `us-east-1`, `us-east-2`, and `us-west-2`. Every AWS CLI example below uses a `<YOUR_REGION>` placeholder. Substitute your chosen region (e.g. `us-east-1`) in each command before running.
4. **IAM permissions** — the deploying principal needs broad-but-scoped permissions across these services: `vpc`, `ec2`, `eks`, `iam`, `ecr`, `s3`, `codebuild`, `secretsmanager`, `logs`, `elasticloadbalancing`. Easiest path: attach `AdministratorAccess` for the POC. Production deploys should scope down to least-privilege.
5. **Service quotas** — confirm you have quota for **G and VT instances** in your target region. A fresh AWS account often has 0 vCPU quota for these.
   ```bash
   # Check current quota for "Running On-Demand G and VT instances"
   aws service-quotas get-service-quota \
     --service-code ec2 --quota-code L-DB2E81BA \
     --region <YOUR_REGION>
   ```
   Need ≥ 8 vCPU for one `g6e.2xlarge`. Request via Service Quotas console if too low (approval takes ~24 hours).

#### NGC account + SVD entitlement

> [!IMPORTANT]
> **SVD is a private-access NIM.** It is NOT available to general NGC users.
> Without the AI for Media Private Access Program entitlement, the image pull will fail with `Payment Required` and the deployment will not succeed. This is **required** — there is no workaround.
>
> **Org scoping matters.** The license is granted to a specific NGC **org**. An API key from a different org — even one under the same email — will fail. Track which org you apply with; the same org must be selected when generating the API key in Step 2.

### Step 1 — Request SVD access (NGC entitlement)

> [!IMPORTANT]
> **Required.** Without this entitlement, `terraform apply` will fail at the image-pull step with `Payment Required` from `nvcr.io`. Plan around 1-2 business days for approval.

1. **Create or use an NGC account.** Visit <https://build.nvidia.com/> and sign in. New users sign up; existing NVIDIA developer logins work.

2. **Create or select an organization.** In NGC, an _org_ is the container for entitlements and API keys. If you don't have one, you'll be prompted to create one on first login. **Make a note of the org name.** Everything below (entitlement, API key, deployment) must happen within this same org.

3. **Apply for SVD access.** Visit <https://build.nvidia.com/nvidia/synthetic-video-detector> and click **Apply for access**. You'll be prompted to fill in justification (company, use case, etc.). Submit.

4. **Wait for the approval email** (~1-2 business days). When approved, NVIDIA sends an email with a "complete onboarding" link.

5. **Click the email link.** Sign in to NGC if prompted. The page asks you to:
   - **Accept the program terms.**
   - **Select the org to apply the license to** — this is the critical step. Pick the **same org you noted in sub-step 2 above**. The license is bound to this org; it does NOT propagate to other orgs you belong to.

6. **Verify entitlement.** After accepting, browse <https://build.nvidia.com/nvidia/synthetic-video-detector> while signed in — you should see deployment artifacts (NIM container details, manifest profiles, etc.) instead of the "Apply for access" gate. If still gated, the license hasn't activated yet — give it a few minutes and retry.

### Step 2 — Generate an NGC API key

> [!IMPORTANT]
> **Required.** The deployment uses this key to authenticate to `nvcr.io` and pull the SVD image. **Generate the key inside the same org you applied the SVD license to in Step 1.** A key from any other org will fail with `Payment Required` at pull time even though it's technically valid NGC credentials.

1. Sign in to <https://catalog.ngc.nvidia.com/> and **confirm the active org** in the top-right dropdown matches the org you applied the SVD license to in Step 1. Switch if needed.

2. Click your profile (top-right) → **Account settings** → scroll down to the **Keys & Secrets** section → on the API keys card, click **Generate API Key**.

3. On the next page, click **Generate Personal Key**. Within the details card, enter a name, set the expiration, and ensure the key has `NGC Catalog` permissions.

4. **Click Generate**, then **Copy the key immediately.** NGC will not show it again — if you close the dialog, you have to generate a new one.

The key looks like `nvapi-` followed by ~64 alphanumeric characters.

### Step 3 — Store the key in AWS

> [!IMPORTANT]
> **Required.** The NGC API key authenticates the module against `nvcr.io` (image pulls) and NGC model artifact endpoints. Two storage paths supported; choose one.

#### Path A — AWS Secrets Manager (recommended, more secure)

The key lives in Secrets Manager. Terraform reads only the secret ARN (via `data.aws_secretsmanager_secret.ngc`); the raw key value is never written to Terraform state. CodeBuild retrieves the value at build start via IAM (`secretsmanager:GetSecretValue` scoped to the specific ARN), and the SageMaker path fetches it at container startup through the shim — so the value only exists in the running build/container process environment.

**A1. Via AWS CLI** (faster, scriptable):

JSON-wrapped with `access-key` (recommended — self-describing, matches the module's canonical shape):

```bash
aws secretsmanager create-secret \
  --name svd-ngc-api-key \
  --description "NGC API key with AI for Media Private Access entitlement" \
  --secret-string '{"access-key":"<PASTE_YOUR_NGC_API_KEY_HERE>"}' \
  --region <YOUR_REGION>
```

Use **single quotes** around the JSON so your shell doesn't try to expand `$` or strip the double quotes.

Plaintext (alternative — works but the secret value is opaque to anyone inspecting it later):

```bash
aws secretsmanager create-secret \
  --name svd-ngc-api-key \
  --description "NGC API key with AI for Media Private Access entitlement" \
  --secret-string "<PASTE_YOUR_NGC_API_KEY_HERE>" \
  --region <YOUR_REGION>
```

Replace `<PASTE_YOUR_NGC_API_KEY_HERE>` with the key from Step 2. The secret name (`svd-ngc-api-key`) is what you'll reference in `terraform.tfvars` in Step 4.

Verify it's stored:

```bash
aws secretsmanager describe-secret \
  --secret-id svd-ngc-api-key \
  --region <YOUR_REGION>
```

> Do NOT run `aws secretsmanager get-secret-value` in a shared terminal — it echoes the key to stdout in plaintext.

**A2. Via AWS Console** (visual, click-through):

1. Navigate to <https://console.aws.amazon.com/secretsmanager/> in the AWS region you'll deploy to.
2. Click **Store a new secret**.
3. **Secret type**: _Other type of secret_.
4. Choose ONE of:
   - **Key/value pairs tab** (recommended) → set **Key**: `access-key`, **Value**: `<PASTE_YOUR_NGC_API_KEY_HERE>`. The console saves this as a JSON object `{"access-key":"nvapi-..."}` — matching the CLI JSON-wrapped command above. Use the literal key name `access-key` — that's what the module's parser checks for first.
   - **Plaintext tab** (alternative) → paste the NGC API key (just the key string — no JSON wrapping, no quotes, no `key=value` format). Works, but the secret value is opaque to anyone inspecting it later.
5. **Encryption key**: leave default (`aws/secretsmanager`).
6. **Next** → **Secret name**: `svd-ngc-api-key`.
7. **Next** → skip rotation → **Next** → **Store**.

> [!NOTE]
> **Secret value format — must match what you tell the module.**
>
> The module passes a Secrets Manager reference to CodeBuild in the form
> `<arn>:<secret_json_key>::`. CodeBuild fetches the value at build start via IAM —
> the raw key never enters Terraform state or the CodeBuild project config. But the
> reference format needs to match how you stored the secret:
>
> 1. **JSON with `"access-key"`** (recommended, matches this sample's `main.tf`):
>    `{"access-key": "nvapi-..."}` + `ngc_credentials.secret_json_key = "access-key"`.
> 2. **JSON with a different key name:** set `secret_json_key` to that key
>    (e.g. `{"my_key": "nvapi-..."}` → `secret_json_key = "my_key"`).
> 3. **Plaintext** (raw string, no JSON): set `secret_json_key = null` in your
>    `ngc_credentials` block. The module then references the whole secret value.
>
> The `main.tf` in this sample sets `secret_json_key = "access-key"` — matches the
> recommended JSON shape above. If you use a different format, adjust that field.
> Mismatch will surface as an `unauthorized` error from `nvcr.io` on the first
> `terraform apply` (the wrong string gets piped to `docker login`).

#### Path B — inline in Terraform module (less secure, NOT recommended)

The module accepts an `api_key` field directly through the `ngc_api_key` variable. The key ends up in Terraform state, which is why this is discouraged. No `main.tf` edits required — the module already conditionally dispatches on which variable is set.

`main.tf` selects Path A / Path B automatically based on which variable is set:

```hcl
ngc_credentials = var.ngc_secret_name != null ? {
  secret_arn      = data.aws_secretsmanager_secret.ngc[0].arn
  secret_json_key = "access-key"
} : {
  api_key = var.ngc_api_key
}
```

⚠ **Trade-offs**: simpler, but the key is now committed to your tfstate file. If state is in S3 with encryption + restricted access, it's tolerable for a POC. If state is local, anyone with disk access can read the key.

### Step 4 — Configure Terraform

```bash
# Extract the ZIP (or git clone if you have access)
unzip nvidia-svd-on-aws.zip
cd nvidia-svd-on-aws

cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` — set **exactly one** of the two variables:

```hcl
# Path A (recommended) — Secrets Manager
ngc_secret_name = "svd-ngc-api-key"

# Path B (dev-only) — inline key. Leave ngc_secret_name = null (or omit it).
# ngc_api_key = "nvapi-XXXXXXXXXXXXXXXXXXXXXXXX"
```

If you need to change the deploy region (default us-east-1) or other knobs, see [variables.tf](variables.tf).

### Step 5 — Apply

First, verify your AWS credentials are still active in this shell. Credentials can expire between sessions (SSO tokens) or get unset by switching shells / restarting your terminal:

```bash
aws sts get-caller-identity
# Should print your AWS account ID + ARN. If you get "Unable to locate credentials"
# or an expired-token error, re-authenticate (aws sso login / aws configure / etc.)
# before continuing — terraform apply will fail otherwise.
```

Then:

```bash
terraform init
terraform plan    # optional: review what's about to be created (~74 resources)
terraform apply
```

`Apply complete!` arrives after **~20 min**. Outputs:

```
eks_cluster_names = { "svd" = "svd-dev-svd" }
eks_namespaces    = { "svd-nim" = "svd" }
eks_release_names = { "svd-nim" = "svd-dev-svd-nim" }
```

> [!NOTE]
> The SVD container takes ~10-15 minutes to download its model from NGC on first pod startup. `terraform apply` returning success means the manifests were applied; the pod may still be in `0/1 Running` until the model finishes downloading. Watch with `kubectl get pods -n svd -w`.

Proceed to [Testing the endpoint](#testing-the-endpoint).

## Testing the endpoint

End-to-end validation uses NVIDIA's reference Python client from [NVIDIA-Maxine/nim-clients](https://github.com/NVIDIA-Maxine/nim-clients), which ships with two bundled sample videos (one fake, one real).

**Wait for the pod to be Ready first** (~10-15 min after `terraform apply` — SVD downloads its model from NGC on cold start):

```bash
aws eks update-kubeconfig --name svd-dev-svd --region <YOUR_REGION>
kubectl get pods -n svd -w   # ctrl-C when STATUS=Running, READY=1/1
```

**Set up the client, point it at the cluster, run inference** (copy-paste the whole block):

```bash
# Set up the Python client (one-time)
brew install git-lfs && git lfs install
git clone https://github.com/NVIDIA-Maxine/nim-clients.git
cd nim-clients/synthetic-video-detector
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Grab the NLB hostname
LB=$(kubectl get svc -n svd svd-dev-svd-nim-svc \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Run inference against both bundled samples
python scripts/synthetic-video-detector.py --target "$LB:8001" --video-input assets/fake_sample_video.mp4 --save-csv
python scripts/synthetic-video-detector.py --target "$LB:8001" --video-input assets/real_sample_video.mp4 --save-csv
```

**Expected output**: fake scores VERDICT: SYNTHETIC (>95% confidence), real scores VERDICT: REAL (>95%). Per-frame logits land in `fake_sample_video.csv` and `real_sample_video.csv` in your current directory.

If both verdicts come out correct = end-to-end validation complete.

**For your own video**: most phone/screen-capture footage needs format conversion first — see [SVD input video constraints](#svd-input-video-constraints) below.

> [!NOTE]
> Cluster/namespace/release names above (`svd-dev-svd`, `svd`, `svd-dev-svd-nim-svc`) match the defaults from this module. If you changed `project_prefix` or `environment` in `terraform.tfvars`, use the actual values from `terraform output`.

## SVD input video constraints

SVD's hardware decoder is strict. Inputs must satisfy **all four**:

| Property     | Required        | Common offender                                                                        |
| ------------ | --------------- | -------------------------------------------------------------------------------------- |
| Codec        | H.264           | iPhone records HEVC (H.265) by default                                                 |
| Pixel format | 8-bit `yuv420p` | iPhone HDR mode records 10-bit `yuv420p10le` — decoder rejects with `INVALID_ARGUMENT` |
| Frame rate   | Constant (CFR)  | Phones (especially HDR/slow-mo) and screen captures record VFR                         |
| Container    | `.mp4`          | iPhone writes `.MOV`                                                                   |

### Inspect a video

```bash
ffprobe -v error -select_streams v \
  -show_entries stream=codec_name,pix_fmt,r_frame_rate,avg_frame_rate \
  input.mov
```

Compliant output: `codec_name=h264`, `pix_fmt=yuv420p`, `r_frame_rate == avg_frame_rate`.

### Convert to a compliant MP4

```bash
ffmpeg -i input.mov \
  -c:v libx264 -pix_fmt yuv420p -profile:v high -r 30 -an \
  output.mp4
```

| Flag               | Why                                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------------------- |
| `-c:v libx264`     | re-encode video as H.264                                                                             |
| `-pix_fmt yuv420p` | force **8-bit** output (without this, ffmpeg preserves 10-bit from HEVC sources → decoder rejection) |
| `-profile:v high`  | standard H.264 High profile (not High 10)                                                            |
| `-r 30`            | force 30 fps constant frame rate                                                                     |
| `-an`              | drop audio (not needed by SVD)                                                                       |

Re-run `ffprobe` afterward to confirm compliance, then pass the new `.mp4` to the Python client.

## Troubleshooting

Issues encountered during end-to-end validation. Most are environmental — the NIM itself works as documented.

### `Payment Required` on first apply

```
Error response from daemon: Head "https://nvcr.io/v2/nim/nvidia/synthetic-video-detector/manifests/latest":
unknown: {"errors": [{"code": "DENIED", "message": "Payment Required"}]}
```

**Cause:** Your NGC API key is valid but doesn't have **AI for Media Private Access Program** entitlement on the org it belongs to. SVD is a private-access NIM — a generic NGC developer key is not sufficient.

**Fix:** Request access through your NVIDIA contact. Once approved, generate a fresh API key in that org and update the Secrets Manager value:

```bash
aws secretsmanager put-secret-value \
  --secret-id svd-ngc-api-key \
  --secret-string "<PASTE_YOUR_NEW_NGC_API_KEY_HERE>" \
  --region <YOUR_REGION>
```

Then `terraform destroy && terraform apply` (the image sync CodeBuild caches the failed pull, so re-apply alone won't retry).

### `Video file format not supported by hardware decoder`

```
GRPC Error: StatusCode.INVALID_ARGUMENT
Video file format not supported by hardware decoder. Please try another video file.
```

**Cause:** The video is technically H.264 but in 10-bit (`yuv420p10le`, "High 10" profile). The L40S's NVDEC hardware decoder only handles standard 8-bit H.264.

**Fix:** Re-encode with `-pix_fmt yuv420p -profile:v high`. See [SVD input video constraints](#svd-input-video-constraints).

### Pod stuck `Pending` past 5 min

```
kubectl describe pod ... | tail
Events:
  Warning  FailedScheduling  ...  no instance type has enough resources, requirements=...nvidia.com/gpu:"1"...
```

**Cause:** Karpenter cycling through node candidates. Normal for the first ~2-3 min on a fresh cluster as it provisions a g6e.2xlarge instance.

**Fix:** Wait. If still Pending past 5 min, your account has insufficient g6e quota in that region — request a quota increase via Service Quotas, or fall back to `g6.2xlarge` (L4 GPU, slower but more available).

### Sample video opens as text in QuickTime / "not compatible"

**Cause:** You cloned `NVIDIA-Maxine/nim-clients` before running `git lfs install`. The `assets/*.mp4` files in the repo are 131-byte LFS pointer text files, not real videos.

**Fix:**

```bash
brew install git-lfs
cd path/to/nim-clients
git lfs install
git lfs pull
```

After this, `ls -lh synthetic-video-detector/assets/` should show files in the hundreds of KB.

### `pip install` fails with `externally-managed-environment`

```
error: externally-managed-environment
× This environment is externally managed
```

**Cause:** macOS Homebrew Python (PEP 668) refuses to let `pip` install into the system environment. Not specific to SVD — affects any pip use against Homebrew Python.

**Fix:** Use `uv` (recommended — creates and manages a venv automatically):

```bash
brew install uv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Or the standard venv path:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Python client hangs at `Uploading video: 0%`

**Cause:** Two common ones:

1. The NLB hostname has just been provisioned — DNS resolves but target groups aren't healthy yet. Initial gRPC handshake takes 15-30 seconds.
2. Pod is still in NGC cold-start (~10-15 min on first deploy) — passes liveness but not readiness yet, so NLB targets are `unhealthy`.

**Diagnose:**

```bash
# Is the pod 1/1 Ready?
kubectl get pods -n svd

# Are NLB targets healthy?
TG=$(aws elbv2 describe-target-groups --region <YOUR_REGION> \
       --query 'TargetGroups[].{name:TargetGroupName,arn:TargetGroupArn}' --output text | \
     grep nimtesti | awk '{print $1}')
aws elbv2 describe-target-health --target-group-arn "$TG" --region <YOUR_REGION>
```

If both look good and the client still hangs >5 min, kill it and retry — a failed prior request (e.g. the 10-bit rejection above) can leave the gRPC stream in a throttled state.

### `terraform apply` reports deploy-nim action failed but pod is healthy

**Cause:** Kubernetes Deployment's default `progressDeadlineSeconds` (600s) is shorter than SVD's NGC cold-start (~10-15 min). The Deployment marks itself failed-to-progress at 10 min even though the pod is making real progress toward Ready.

**Fix:** This was patched in `terraform-aws-nim` (now sets `progressDeadlineSeconds: 3600` on the Deployment manifest). If you see this on an old module version, pull the latest `terraform-aws-nim` (≥ commit `2b7201a`) and re-apply.

## Teardown

When you're done with the POC:

```bash
cd nvidia-svd-on-aws
terraform destroy
```

~5-10 min. The module's cleanup hooks drain the NLB, delete the `Deployment`/`Service`, and clean orphan ENIs before tearing down the VPC. Watch for `Destroy complete! Resources: 74 destroyed.` — no orphan AWS resources should remain.

If destroy fails partway through, re-run it. The cleanup hooks are idempotent and the destroy is safe to retry until it reports `0 destroyed` on a subsequent run (meaning state and AWS agree everything's gone).

## References

- [Maxine SVD overview](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/overview.html)
- [Maxine SVD support matrix](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/support-matrix.html)
- [Maxine SVD getting started](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/getting-started.html)
- [NVIDIA-Maxine/nim-clients (GitHub)](https://github.com/NVIDIA-Maxine/nim-clients)
- [EKS-optimized accelerated AMIs](https://docs.aws.amazon.com/eks/latest/userguide/ml-eks-optimized-ami.html)
- [amazon-eks-ami GitHub releases](https://github.com/awslabs/amazon-eks-ami/releases)
- [Bottlerocket NVIDIA support](https://aws.amazon.com/blogs/containers/bottlerocket-support-for-nvidia-gpus/)
- [NVIDIA GPU-Optimized AMI on Marketplace](https://aws.amazon.com/marketplace/pp/prodview-7ikjtg3um26wq)
- [AWS Deep Learning AMI release notes](https://docs.aws.amazon.com/dlami/latest/devguide/appendix-ami-release-notes.html)
- [EC2 Capacity Reservations](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-reservations.html)
- [AWS RAM AZ ID mappings](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html)
