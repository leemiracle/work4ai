# terraform-aws-nim

Terraform module for deploying NVIDIA NIMs and open-weight models on AWS across Amazon SageMaker AI and Amazon Elastic Kubernetes Service (EKS).

---

## Scope and framework support

This module is primarily designed around **[NVIDIA NIMs](https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/)** — the recommended path for all NVIDIA
models in production. NIMs handle runtime selection, optimization, and model management
internally. Users need only supply the image URI.

For models not yet available as NIMs, the module provides **limited open-weight support via
vLLM** — covering standard LLMs and multimodal LLMs from [HuggingFace](https://huggingface.co/) or [NGC](https://catalog.ngc.nvidia.com/).

---

## Supported deployment paths

| Path                | Framework      | Platform        | Status       |
| ------------------- | -------------- | --------------- | ------------ |
| **NIM container**   | NVIDIA-managed | SageMaker       | ✅ Available |
| **NIM container**   | NVIDIA-managed | EKS             | ✅ Available |
| **Open weight LLM** | vLLM           | SageMaker       | ✅ Available |
| **Open weight LLM** | vLLM           | EKS             | ✅ Available |
| **Open weight**     | Triton         | SageMaker + EKS | 🗓 Planned   |

Any combination can be deployed in a single `module "nim"` call. Empty map = no
resources for that platform.

---

## GPU instance reference

All families below are available as `ml.<family>` on SageMaker and as `<family>` on EKS —
identical underlying hardware, different prefix.

| Family                                                      | GPU                 | VRAM/GPU | GPU counts | NVLink         |
| ----------------------------------------------------------- | ------------------- | -------- | ---------- | -------------- |
| [G4dn](https://aws.amazon.com/ec2/instance-types/g4/)       | NVIDIA T4           | 16 GB    | 1×, 4×, 8× | No             |
| [G5](https://aws.amazon.com/ec2/instance-types/g5/)         | NVIDIA A10G         | 24 GB    | 1×, 4×, 8× | No             |
| [G6](https://aws.amazon.com/ec2/instance-types/g6/)         | NVIDIA L4           | 24 GB    | 1×, 4×, 8× | No             |
| [G6e](https://aws.amazon.com/ec2/instance-types/g6e/)       | NVIDIA L40S         | 48 GB    | 1×, 4×, 8× | No             |
| [P4d](https://aws.amazon.com/ec2/instance-types/p4/)        | NVIDIA A100 (HBM2)  | 40 GB    | 8× only    | Yes (NVSwitch) |
| [P4de](https://aws.amazon.com/ec2/instance-types/p4/)       | NVIDIA A100 (HBM2e) | 80 GB    | 8× only    | Yes (NVSwitch) |
| [P5](https://aws.amazon.com/ec2/instance-types/p5/)         | NVIDIA H100 (HBM3)  | 80 GB    | 1×, 8×     | Yes (NVLink 4) |
| [P5e / P5en](https://aws.amazon.com/ec2/instance-types/p5/) | NVIDIA H200 (HBM3e) | 140 GB   | 8× only    | Yes            |

NVLink/NVSwitch enables high-bandwidth GPU-to-GPU communication, which matters when a model
requires tensor parallelism across multiple GPUs. G-family instances use PCIe for cross-GPU
traffic; P-family instances use NVSwitch — roughly 10× higher bandwidth.

### Sizing tip

Within the G-family, the `xlarge` through `8xlarge` sizes are all **1 GPU** — only host CPU /
RAM scale up. You jump to **4 GPUs at `12xlarge`** and **8 GPUs at `48xlarge`**.

Pick by deployment count, not just model size:

- **One deployment per EKS cluster**: any single-GPU size (`g6e.xlarge` recommended — fits
  most ≤30 GB models, best availability)
- **Multiple deployments sharing one cluster**: you need a GPU per deployment, so use
  `g6e.12xlarge` (4 GPUs) — see `examples/all-inference/`
- **SageMaker endpoints**: each endpoint provisions its own instance — no sharing concern,
  size to fit the single model

### Default example model

All examples ship configured for **[`nvidia/Llama-3.1-Nemotron-Nano-8B-v1`](https://build.nvidia.com/nvidia/llama-3_1-nemotron-nano-8b-v1)** —
NVIDIA's instruction-tuned fine-tune of Llama-3.1-8B. NIM image:
`nvcr.io/nim/nvidia/llama-3.1-nemotron-nano-8b-v1:latest`. HuggingFace ID (open-weight path):
`nvidia/Llama-3.1-Nemotron-Nano-8B-v1`.

The model is generic — the module is image-agnostic — so customers will swap it for whatever
fits their use case. The choice for the *default* in the examples was deliberate:

- **Single-GPU compatible on L40S.** 8B Transformer-family weights occupy ~16 GB BF16; KV
  cache and activations leave comfortable headroom in 48 GB. This keeps the
  default example simple (one `g6e.xlarge` node, one endpoint) and avoids forcing customers
  onto multi-GPU instances with worse capacity availability and higher cost just to try the
  module.
- **Standard Transformer architecture.** Earlier iterations used `Nemotron-Nano-9B-v2`, a
  Mamba-Transformer hybrid. The MambaCacheManager pre-allocates ~33 GB regardless of GPU,
  which OOMs single-GPU L40S. Switching to a standard Llama-family model removes that
  landmine so customers don't hit an obscure architecture-specific OOM as their first
  experience of the module.
- **Pre-built NIM profiles for L40S and most data-center GPUs.** Container startup picks an
  optimized TRT-LLM profile (when available) or vLLM fallback. With
  `enable_model_profile_cache = true`, the chosen profile is pre-staged to S3 and a
  cache-sync init container makes cold start ~2–5 min instead of ~5–10 min downloading from
  NGC every time.
- **NVIDIA-published, non-gated on HuggingFace.** Customers don't need to manually accept
  the Llama Community License or store an HF token to try the open-weight path —
  `nvidia/Llama-3.1-Nemotron-Nano-8B-v1` is downloadable anonymously under the NVIDIA Open
  Model License (with Llama 3.1 Community License as additional terms).
- **Commercial-use OK.** Customers can carry the same configuration into production without
  changing the model.

To swap models, change `source_image_uri` (NIM path) or `model_id` + `model_source`
(open-weight path) and the matching `instance_type` for the new model's VRAM and tensor-
parallelism needs. The [GPU instance reference](#gpu-instance-reference) above and the
[Sizing tip](#sizing-tip) section map common model sizes to instance choices.

### Multi-AZ design for GPU capacity

GPU instance families — especially newer ones like G6e (L40S), P5 (H100), and P5e/P5en (H200)
— hit AWS capacity walls regularly. A `terraform apply` requesting a `g6e.xlarge` can sit
indefinitely with the pod Pending if the VPC only has subnets in AZs that AWS happens to be
out of stock in. The fix is **VPC topology**, not larger instances.

**The EKS example VPCs span 4 AZs.** EKS Auto Mode (managed Karpenter) issues a single
`CreateFleet` call listing every (AZ, subnet, instance type) combination drawn from your
subnet set — AWS fulfills capacity from whichever AZ has it. More AZs = more chances for at
least one to succeed. The cost is essentially zero (subnets are free; the examples use a
single shared NAT gateway, so AZ count doesn't multiply NAT/EIP charges).

**Reference AZs by ID, not by name.** AZ names (`us-east-1a`) are
[randomly mapped per AWS account](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html) —
your `us-east-1a` and another account's `us-east-1a` are different physical datacenters.
[AZ IDs (`use1-az1`)](https://docs.aws.amazon.com/global-infrastructure/latest/regions/az-ids.html)
are stable across accounts. The example VPCs use `availability_zone_id`, sourced from
`data.aws_availability_zones.available.zone_ids` — region-portable, account-portable, and
aligned with how ODCRs are pinned.

**Newer instance types favor older AZs.** AWS rolls out new GPU families to physical AZs
unevenly, and capacity tends to follow that rollout for some time. Picking AZs by letter
without checking actual instance-type availability is the most common cause of recurring
"no capacity" errors. The
[`describe-instance-type-offerings`](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instance-type-offerings.html)
CLI command with `--location-type availability-zone-id` shows which AZ IDs offer a given
instance type — useful before committing to a region or designing a VPC for a specific
workload.

**ODCRs are AZ-ID-pinned.** An On-Demand Capacity Reservation for `g6e.xlarge` in `use1-az3`
only fulfills launches into that exact AZ. Two requirements follow: your VPC must include a
subnet in that AZ ID, and the NodePool should pin to it (via `karpenter.sh/capacity-type:
reserved` plus a zone requirement). Otherwise Karpenter launches on-demand elsewhere and the
reservation goes unused.

**SageMaker is unaffected.** SageMaker endpoints don't run in customer VPCs — AWS manages the
underlying EC2 in its own infrastructure. Capacity errors there surface at the region level
with no VPC-side mitigation; retry or change region.

---

## Why a shim is always required for SageMaker

SageMaker hardcodes two paths on every container it runs:

- `POST /invocations` — inference
- `GET /ping` — health check

No inference framework serves these natively. The module wraps every SageMaker container with
a lightweight Caddy reverse proxy that rewrites these paths to whatever the framework actually
serves. This is a permanent SageMaker requirement — not a NIM workaround.

| Framework          | Caddy rewrites `/invocations` → | Caddy rewrites `/ping` → |
| ------------------ | ------------------------------- | ------------------------ |
| NIM                | `/v1/chat/completions`          | `/v1/health/ready`       |
| vLLM               | `/v1/chat/completions`          | `/health`                |
| Triton _(planned)_ | `/v2/models/{model}/infer`      | `/v2/health/ready`       |

**EKS does not need the shim.** Callers hit the NLB directly with the framework's native API.

---

## Connectivity — hybrid by default

The module defaults to a hybrid connectivity model: **as private as possible without requiring
callers to be inside a VPC.**

- **SageMaker:** Endpoints are invoked via the SageMaker Runtime API, which is internet-routable
  but requires SigV4 (AWS IAM) authentication. No VPC required for callers. All internal
  traffic (ECR, S3, Secrets Manager) stays within AWS. A fully private PrivateLink path is
  available for enterprise deployments.

- **EKS:** NLB is internet-facing by default (`load_balancer_internal = false`). Controlled by
  security group and CIDR rules — the example restricts access to the deployer's IP only.
  Internal NLB option available via `load_balancer_internal = true` for VPC-only access.

---

## NIM on SageMaker

```hcl
module "inference" {
  source = "git::https://github.com/NVIDIA/nvidia-aws-samples.git//inference/terraform-aws-nim?ref=main"

  project_prefix = "my-project"
  environment    = "prod"
  region         = "us-east-1"

  ngc_credentials = {
    secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:ngc-api-key"
  }

  sagemaker_endpoints = {
    llama-3-1-8b = {
      source_image_uri           = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
      instance_type              = "ml.g6e.12xlarge"
      endpoint_type              = "realtime"
      enable_model_profile_cache = true
    }
  }
}
```

### Multiple NIMs, one module call

Two endpoints sharing the same `source_image_uri` share one ECR base image, one shim image,
and one S3 cache prefix — no duplicate storage or builds.

```hcl
sagemaker_endpoints = {
  llama-3-1-8b = {
    source_image_uri           = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
    instance_type              = "ml.g6e.12xlarge"
    enable_model_profile_cache = true
  }
  nemotron-nano = {
    source_image_uri           = "nvcr.io/nim/nvidia/nemotron-3-nano:2.0.2"
    instance_type              = "ml.g6e.12xlarge"
    enable_model_profile_cache = true
  }
}
```

### Large-payload models (async)

Use `endpoint_type = "async"` when the request body exceeds SageMaker's 6 MB synchronous
limit (e.g. vision models receiving base64-encoded image frames).

```hcl
sagemaker_endpoints = {
  alpamayo = {
    source_image_uri = "nvcr.io/nim/nvidia/alpamayo:1.0.0"
    instance_type    = "ml.g6e.12xlarge"
    endpoint_type    = "async"
  }
}
```

---

## Open weights on SageMaker

Specify a model ID and source — the module downloads the weights to S3, builds a vLLM shim
image, and syncs weights into the container at startup. No Dockerfile, no framework knowledge
required.

```hcl
sagemaker_endpoints = {
  llama-8b = {
    model_id      = "meta-llama/Llama-3.1-8B-Instruct"
    model_source  = "huggingface"   # "huggingface" | "ngc"
    instance_type = "ml.g6e.12xlarge"
  }
}
```

`extra_args` passes `vllm serve` flags as a map — keys are flag names without `--`, values
are the argument value (empty string for boolean flags). Use for model-specific settings
documented on the model card or when overriding recipe defaults.

```hcl
sagemaker_endpoints = {
  llama-8b = {
    model_id      = "meta-llama/Llama-3.1-8B-Instruct"
    model_source  = "huggingface"
    instance_type = "ml.g6e.12xlarge"
    extra_args = {
      max-model-len    = "32768"
      dtype            = "bfloat16"
      reasoning-parser = "qwen3"    # empty string "" for boolean flags
    }
  }
}
```

`model_id` and `source_image_uri` are mutually exclusive per endpoint. Presence of one
determines which path the module takes.

Supported `framework` values:

| Value                  | Base image                    | Use when                                               |
| ---------------------- | ----------------------------- | ------------------------------------------------------ |
| `"vllm"` (default)     | `vllm/vllm-openai`            | Standard LLMs, multimodal LLMs — covers most HF models |
| `"triton"` _(planned)_ | `nvcr.io/nvidia/tritonserver` | Non-LLM models, CV, physical AI without a NIM          |

### vLLM Recipe auto-configuration

Setting `enable_vllm_recipe = true` instructs the weight-fetch build to query
[vLLM Recipes](https://recipes.vllm.ai) — a community-maintained database of validated
`vllm serve` configurations, published as a JSON API at
`recipes.vllm.ai/<hf_org>/<hf_repo>.json`. The module extracts the recommended flags,
environment variables, and minimum VRAM requirements for the target model and precision
variant, then applies them automatically.

This is the open-weight equivalent of `enable_model_profile_cache` for NIMs: both solve the
same question — "what settings should I use for this model on this hardware?" — but draw
from different sources. NIMs carry profile metadata from NGC; open-weight models use the
vLLM Recipes database.

```hcl
sagemaker_endpoints = {
  llama-8b = {
    model_id           = "meta-llama/Llama-3.1-8B-Instruct"
    model_source       = "huggingface"
    instance_type      = "ml.g6e.12xlarge"
    enable_vllm_recipe = true       # fetch optimized flags from recipes.vllm.ai
    vllm_precision     = "default"  # "default" (bf16) or "fp8"
  }
}
```

**`extra_args` always wins.** Any flag set explicitly in `extra_args` overrides the
corresponding recipe value. Use this to tune individual settings while still getting recipe
defaults for everything else.

**Not all models have a recipe.** The database currently covers ~64 models across 25+
providers. If the model does not have a recipe, the weight-fetch build logs a warning and
falls back to vLLM's own defaults (or explicit `extra_args` if set). The endpoint still
deploys — recipe fetch is a best-effort optimization, not a hard dependency.

If the model you want has a NIM on NGC, use `source_image_uri` instead — the NIM path uses
NGC model profiles directly from NVIDIA rather than the community recipes database.

---

## Inference optimization

Three options are available. They are not interchangeable — each applies to a specific
deployment path and operates at a different level.

### NIM path: model profile cache

`enable_model_profile_cache = true` pre-downloads the best TRT-LLM engine for the target GPU
to S3 before the endpoint starts. Without it, NIM downloads the profile from NGC at every
container start (~5–10 min). With a warm cache, startup drops to ~2–5 min (S3 sync).

A NIM profile is a pre-compiled, GPU-specific artifact — built by NVIDIA for a specific GPU
architecture, tensor parallelism count, and precision. Profiles are not portable across GPU
families (an L40S profile won't load on H100).

```hcl
llama-nim = {
  source_image_uri           = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
  instance_type              = "ml.g6e.12xlarge"
  enable_model_profile_cache = true
}
```

**Use when:** deploying any NIM where startup time or restart frequency matters.

### Open weight path: vLLM recipe

`enable_vllm_recipe = true` fetches recommended `vllm serve` flags from
[recipes.vllm.ai](https://recipes.vllm.ai) — community-validated settings per model
(chunk size, tensor parallelism, dtype, etc.). Flags are applied at container startup
before any explicit `extra_args`. If no recipe exists for the model, vLLM defaults are
used and the endpoint still deploys — recipe fetch is non-fatal.

```hcl
llama-8b = {
  model_id           = "meta-llama/Llama-3.1-8B-Instruct"
  model_source       = "huggingface"
  instance_type      = "ml.g6e.12xlarge"
  enable_vllm_recipe = true
}
```

**Use when:** deploying a HuggingFace model via vLLM and you don't know the optimal
settings. Only applies to `model_source = "huggingface"` — NGC models have no recipes.

### Open weight path: extra_args

Passes flags directly to `vllm serve`. Keys are flag names without `--`; value is the
argument, or `""` for boolean flags.

```hcl
extra_args = {
  max-model-len = "32768"   # value flag
  enforce-eager = ""        # boolean flag — empty string emits --enforce-eager with no value
  trust-remote-code = ""    # another boolean flag
}
```

**`extra_args` always wins.** Any flag set here overrides the corresponding recipe value.
Use `enable_vllm_recipe = true` together with `extra_args` to get recipe defaults for
most settings while pinning specific ones.

### Comparison

|                 | NIM profile cache                                  | vLLM recipe                          | extra_args                        |
| --------------- | -------------------------------------------------- | ------------------------------------ | --------------------------------- |
| Deployment path | NIM (`source_image_uri`)                           | Open weight (`model_id`)             | Open weight (`model_id`)          |
| Content         | Pre-compiled TRT-LLM engine                        | Recommended CLI flags                | Your explicit CLI flags           |
| Source          | NGC (NVIDIA)                                       | recipes.vllm.ai (community)          | Terraform config                  |
| Applied at      | Container startup — S3 sync into `/opt/nim/.cache` | Container startup — env file sourced | Container startup — appended last |
| Priority        | —                                                  | Lower                                | Highest — overrides recipe        |
| If unavailable  | Endpoint fails (profile required)                  | Falls back to vLLM defaults          | —                                 |

---

## NIM on EKS

EKS uses the base NIM image from ECR directly — no shim. EKS Auto Mode provisions the GPU
node and NLB. Access is restricted to the deployer's IP by default via security group CIDR rules.

### Inference protocols supported

| Protocol | Default port | Typical NIMs | Module path |
| -------- | ------------ | ------------ | ----------- |
| `http` (default) | 8000 | NIM-LLM (Llama, Nemotron, etc.), text-embedding, Riva speech | Helm chart from NGC (pinned `helm_chart_version`) |
| `grpc` | 8001 | Maxine media NIMs (Synthetic Video Detector, Audio2Face, Studio Voice, Eye Contact, BNR), Triton-based NIMs | Raw kubectl Deployment + Service with NLB TCP passthrough (no Helm chart available for Maxine today) |

Opt into gRPC per deployment:

```hcl
eks_deployments = {
  nim = {
    svd = {
      cluster_key      = "svd-cluster"
      source_image_uri = "nvcr.io/nim/nvidia/synthetic-video-detector:latest"
      protocol         = "grpc"      # default: "http"
      # grpc_port      = 8001        # default: 8001
    }
  }
}
```

For background on why different NIM families use different protocols, how LLM REST/JSON
differs from media gRPC, how `grpcurl` works, and the cloud-storage handoff pattern for
large payloads, see the [Inference Protocols section in DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md#inference-protocols-and-the-choices-in-this-module).

```hcl
eks_clusters = {
  llama-cluster = {
    vpc_id              = aws_vpc.main.id
    private_subnet_ids  = aws_subnet.private[*].id
    public_subnet_ids   = aws_subnet.public[*].id
    instance_type       = "g6e.12xlarge"
    allowed_cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
    internet_gateway_id = aws_internet_gateway.main.id
  }
}

eks_deployments = {
  nim = {
    llama-deploy = {
      cluster_key                = "llama-cluster"
      source_image_uri           = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
      enable_model_profile_cache = true
      helm_chart_version         = "2.0.3"
    }
  }
}
```

### GPU count — auto-derived from instance type

The module automatically sets the Kubernetes GPU resource request to the full GPU count of
the node instance type. A `g6e.12xlarge` has 4× L40S — the pod requests `nvidia.com/gpu: 4`
automatically so NIM can load the matching 4-GPU tensor-parallel profile.

You never need to specify a GPU count. Override with `gpu_count` only when you intentionally
want fewer GPUs than the instance provides (e.g. testing, or sharing a node between deployments).

| Instance type                                        | GPUs auto-requested |
| ---------------------------------------------------- | ------------------- |
| g6e.xlarge / g6e.2xlarge / g6e.4xlarge / g6e.8xlarge | 1                   |
| g6e.12xlarge / g6e.24xlarge                          | 4                   |
| g6e.48xlarge                                         | 8                   |
| p5.48xlarge                                          | 8                   |

See `DEVELOPER_REFERENCE.md` for the full instance table and the reasoning behind why
SageMaker does not need this (whole instance = all GPUs, implicit) while EKS does (explicit
Kubernetes resource request required).

### NGC Helm charts — version must be pinned

NGC does not expose a chart index, so `helm repo add` is not supported. Always set
`helm_chart_version` for NGC charts. The module derives the correct chart name and repo URL
from `nim_type` automatically.

| `nim_type`      | Chart                                         | Default                                            |
| --------------- | --------------------------------------------- | -------------------------------------------------- |
| `llm` (default) | `nim-llm`                                     | `https://helm.ngc.nvidia.com/nim/charts`           |
| `embedding`     | `text-embedding-nim`                          | `https://helm.ngc.nvidia.com/nim/snowflake/charts` |
| `speech`        | `riva-api`                                    | `https://helm.ngc.nvidia.com/nvidia/riva/charts`   |
| `custom`        | set `helm_chart_s3_uri` or explicit name+repo | —                                                  |

---

## Open weights on EKS

Same interface as SageMaker open weights. Weights in S3 are reused across platforms — no
duplicate download. An init container syncs weights from S3 into the pod at startup.

```hcl
eks_clusters = {
  gpu-cluster = {
    vpc_id              = aws_vpc.main.id
    private_subnet_ids  = aws_subnet.private[*].id
    public_subnet_ids   = aws_subnet.public[*].id
    instance_type       = "g6e.48xlarge"
    allowed_cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
    internet_gateway_id = aws_internet_gateway.main.id
  }
}

eks_deployments = {
  open_weight = {
    nemotron-deploy = {
      cluster_key  = "gpu-cluster"
      model_id     = "nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning"
      model_source = "huggingface"
      extra_args   = { trust-remote-code = "" }
    }
  }
}
```

---

## Autoscaling on EKS

Static `replicas = N` is the default: whatever count you set runs forever, regardless of load.
For real inference traffic that isn't enough — LLMs saturate KV cache and latency explodes;
gRPC media NIMs pin one video stream per pod, so concurrent tenants share a GPU. Autoscaling
lets pod count follow demand between `min_replicas` and `max_replicas`, and Karpenter provisions
GPU nodes underneath as pods pend.

This module implements the pattern outlined in
[NVIDIA's *Horizontal Autoscaling of NVIDIA NIM Microservices on Kubernetes*](https://developer.nvidia.com/blog/horizontal-autoscaling-of-nvidia-nim-microservices-on-kubernetes/)
blog post — KEDA + kube-prometheus-stack + DCGM exporter fronting the standard Kubernetes
HorizontalPodAutoscaler. The module extends that pattern to cover both the NIM path and the
open-weight (vLLM direct) path on the same cluster, and adds Maxine-family (gRPC / one-video-per-GPU)
NIMs which the blog's `k8s-nim-operator` alternative does not currently support (see the design
rationale in [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md#autoscaling-design)).

### Enabling

Two flags — one on the cluster, one on the deployment. All existing examples continue to work
unchanged; autoscaling is fully opt-in per deployment.

```hcl
eks_clusters = {
  gpu-cluster = {
    # ... existing fields ...
    enable_autoscaling = true   # installs KEDA + kube-prometheus-stack + DCGM exporter cluster-wide
  }
}

eks_deployments = {
  nim = {
    llama = {
      cluster_key      = "gpu-cluster"
      source_image_uri = "nvcr.io/nim/nvidia/llama-3.1-nemotron-nano-8b-v1:latest"
      replicas         = 1                # initial replica count; KEDA takes over from here
      autoscaling = {
        min_replicas = 1
        max_replicas = 5
        # metric, target_value, scale_down_delay all optional — see defaults below
      }
    }
  }
}
```

### What gets installed when `enable_autoscaling = true`

Cluster-wide, one time per cluster (via the existing `cluster-setup` CodeBuild action):

- **KEDA** ([kedacore/keda](https://github.com/kedacore/charts) v2.20.1) — Kubernetes Event-Driven
  Autoscaler. Wraps native HPA and adds native Prometheus + 60+ other triggers with zero
  glue configuration.
- **kube-prometheus-stack** ([prometheus-community](https://github.com/prometheus-community/helm-charts)
  v87.16.1) — Prometheus operator + Prometheus. Grafana + Alertmanager disabled by default;
  enable via a follow-up `helm upgrade` if you want dashboards.
- **dcgm-exporter** ([NVIDIA/dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter) v4.8.3) —
  Per-node GPU telemetry daemonset. Provides `DCGM_FI_DEV_GPU_UTIL` and friends, labeled with
  `pod` and `namespace` so ScaledObject queries can filter to a specific NIM's pods.

Cluster-side install honors the destroy path: a `terraform_data.autoscaling_cleanup`
resource runs `helm uninstall` for all three before the cluster is torn down.

### What the module emits per deployment

- A **KEDA `ScaledObject`** in the deployment's namespace, targeting the Deployment we just
  rolled out, with a Prometheus trigger scoped to that deployment's pods.
- For the NIM Helm path: `metrics.enabled: true` + `metrics.serviceMonitor.enabled: true` in
  the generated values.yaml so the NGC chart emits its own correctly-shaped ServiceMonitor.
  No hand-rolled ServiceMonitor — the chart already knows its port name and metrics path.
- For the open-weight (vLLM) path: a hand-emitted ServiceMonitor scraping `/metrics` on the
  Service port `http`, since we own the manifest.
- For the gRPC / Maxine path: no ServiceMonitor. Maxine NIMs expose only GPU/process telemetry
  on `/v1/metrics` ([per NVIDIA docs](https://docs.nvidia.com/nim/maxine/synthetic-video-detector/latest/observability.html))
  with no request-load signal — DCGM's own ServiceMonitor is the only scrape target needed.

### Metric defaults per `nim_type`

The module picks a sensible default so most deployments need only `min_replicas` /
`max_replicas`. All are overridable.

| `nim_type`                        | Default metric              | Default target | Rationale                                                                       |
| --------------------------------- | --------------------------- | -------------- | ------------------------------------------------------------------------------- |
| `llm`, `vlm`                      | `gpu_cache_usage_perc`      | 0.7 (70%)      | vLLM KV cache saturation — canonical LLM scaling signal (NVIDIA blog, NIM operator sample) |
| `embedding`, `reranking`, `speech`, `custom` | `DCGM_FI_DEV_GPU_UTIL` | 70 (%)  | No universal request-load metric; per-pod GPU util is the reliable fallback     |
| open_weight (vLLM direct)         | `vllm:kv_cache_usage_perc`  | 0.7 (70%)      | Upstream vLLM V1 naming (NIM's chart re-exports without the `vllm:` prefix)     |

Threshold formats differ: cache metrics are 0.0–1.0 fractions; DCGM util is 0–100 percent.
The comparison is scale-agnostic; use the format matching your chosen metric.

### Overriding the defaults

Any field on the `autoscaling` object can be set explicitly. Only the fields you set are
overridden — the rest fall through to defaults.

```hcl
autoscaling = {
  min_replicas     = 2                 # keep 2 warm to avoid first-request cold-start pain
  max_replicas     = 10
  metric           = "num_requests_running"   # any Prometheus metric your NIM emits
  target_value     = 5                        # per-pod concurrent-request threshold
  scale_down_delay = 900                      # 15 min HPA stabilization window
}
```

### Cold-start guidance

NIMs cold-start slowly (5–15 min for image pull + model load on a fresh GPU node). The
scale-up path has to wait for that regardless of how aggressive the KEDA config is. Two
practical implications:

- **Set `min_replicas >= 2` in production.** The floor keeps warm capacity available so the
  first live request during a scale-up event doesn't hit a cold pod.
- **`scale_down_delay` defaults to 600s (10 min).** Short windows cause replica thrash
  when load oscillates near threshold — every removed pod is a 5–15 min cold-start away
  from being replaced.

`enable_model_profile_cache = true` on the deployment cuts cold-start substantially by
pre-syncing the NGC model profile from S3 into the pod. Recommended for autoscaled deployments.

### One-video-per-GPU workloads (Maxine SVD, streaming inference)

The Maxine SVD NIM processes one video stream per GPU. With `replicas = 1` and two concurrent
tenants, both streams share the same pod's GPU and each sees roughly half the throughput.
Autoscaling to `max_replicas = N` with `gpu_count = 1` per pod gives each concurrent tenant
its own pod. Karpenter provisions one GPU node per replica.

For the SVD example:

```hcl
autoscaling = {
  min_replicas     = 1
  max_replicas     = 3   # up to 3 concurrent streams before capping
  scale_down_delay = 180 # 3 min tail instead of module default 600s
}
```

Target metric auto-derives to `DCGM_FI_DEV_GPU_UTIL` because `nim_type = "custom"`.

Streaming-inference workloads are often short and bursty — the module default 10 min
scale-down window keeps idle GPU nodes running longer than the burst that provisioned
them. Dropping to 3 min balances scale-down aggressiveness against replica thrash near
threshold. For services where cold-start dominates (large LLMs), keep the 600s default.

### Runtime verification

After apply completes:

```bash
aws eks update-kubeconfig --name <cluster-name> --region <region>

# Addons landed
kubectl get pods -n keda           # keda-operator + keda-metrics-apiserver
kubectl get pods -n monitoring     # kps-* + dcgm-exporter DaemonSet
kubectl get scaledobject -A        # your NIM's ScaledObject
kubectl get hpa -A                 # KEDA auto-creates keda-hpa-<scaledobject-name>

# Prometheus scraping the NIM
kubectl port-forward -n monitoring svc/kps-kube-prometheus-stack-prometheus 9090:9090
# Browser → http://localhost:9090 → Status → Targets. Confirm the NIM's target is UP.

# Watch scaling under load
kubectl get hpa -n <namespace> -w
kubectl get pods -n <namespace> -w
```

**Metric appears after first request.** The Prometheus counter is 0 (or absent) until the NIM
serves at least one request. HPA/KEDA display `<unknown>` until traffic arrives — send a test
request to activate.

**Load driver overhead can hide GPU saturation.** If you're driving load with an interpreter
that spins up per-request (e.g. `uv run python …` in a shell loop), the fork + import cost
between invocations can leave the GPU idle for 3–5 seconds per cycle. With a small worker
pool, the DCGM average never sustains above threshold and autoscaling looks broken. Use a
long-lived driver (open the connection once, loop inside the process) or increase concurrency
to fully saturate the GPU during your test window.

### Cost implications

Autoscaling means real GPU instances get created when load rises. `min_replicas = 1` on
g6e.xlarge (~$2/hr) is one node at all times. `max_replicas = 5` means up to five nodes during
peak. Match `max_replicas` to your traffic ceiling and monthly budget — Karpenter provisions
on-demand nodes eagerly.

### When Karpenter can't provision new nodes

Under real production load a customer will eventually hit AWS capacity constraints. HPA scales
the StatefulSet up, StatefulSet controller creates pending pods, Karpenter tries to launch
new instances, and EC2 replies with `InsufficientInstanceCapacity`. Pods stay Pending.

Diagnose with:

```bash
kubectl describe nodepool <name-prefix>-<cluster-key>-gpu
# Look for events at the bottom — repeated `NoCompatibleInstanceTypes`
# warnings signal AWS capacity exhaustion for the chosen instance type.

kubectl get nodeclaim -A
# Karpenter's NodeClaim resources. If NEW claims appear then get deleted
# without ever showing a NODE, the EC2 API rejected them.
```

Options when this happens:

- **Wait.** On-demand GPU capacity in a given AZ typically returns within an hour or two.
  Load balancer keeps serving existing traffic; only the burst suffers.
- **Enable Spot.** Change the NodePool's `karpenter.sh/capacity-type` to include `spot`. Spot
  markets usually have capacity when on-demand doesn't. Cost is ~70% lower. Downside: pods
  can be reclaimed with 2-minute warning — problematic for a NIM that takes 5–15 min to
  cold-start. Not recommended for latency-critical inference.
- **Fall back to a more available instance family.** g6.xlarge (L4, 24 GB VRAM) has
  substantially better inventory than g6e.xlarge (L40S, 48 GB) in most regions and is cheaper.
  For LLMs that fit in 24 GB (up to ~8B in BF16, or larger in FP8), it's a real option.
- **Deploy in a less-congested region.** us-east-1 has the tightest GPU inventory of any
  region. us-east-2, us-west-2, and eu-west-1 often have better g6e availability.

This is real production behavior — worth calling out to end customers who expect autoscaling
to "just work." Autoscaling behaves correctly on the k8s side; AWS EC2 is the last-mile
constraint.

### Instance sizing and pods per node

Kubernetes' NVIDIA device plugin allocates GPUs exclusively per pod — one pod requesting
`nvidia.com/gpu: 1` owns that GPU, and a second GPU-requesting pod can't share it. This means:

- `g6e.xlarge` (1× L40S) → **one NIM pod per node**. Karpenter provisions one node per replica.
- `g6e.12xlarge` (4× L40S) → up to **four NIM pods per node** (with `gpu_count = 1` each).
- `g6e.48xlarge` (8× L40S) → up to **eight pods per node**.

Practical tradeoffs when picking an `eks_clusters[*].instance_type`:

- **Smaller instances (g6e.xlarge, g6e.2xlarge)** — scaling granularity is one-pod-per-node,
  so Karpenter's decisions are simple. Downside: more nodes = more base overhead (kubelet,
  CNI, network), longer cold-start wall-clock when scaling because each pod triggers a full
  node provision.
- **Larger instances (g6e.12xlarge, g6e.48xlarge)** — one node accommodates several pods
  once it's up. Lower cost per GPU-hour usually (volume pricing). Downside: node failures
  take out multiple replicas at once, and Karpenter provisions a whole big instance even
  when only one additional pod is pending.
- **Multi-Instance GPU (MIG)** — only works on A100/H100. Partitions one physical GPU into
  slices each visible to k8s as a separate GPU. Not applicable to L40S/L4.
- **NVIDIA MPS** — GPU time-sharing across pods. Not recommended for latency-sensitive
  inference due to contention.

For a demo or POC, single-GPU instances are fine. For real multi-tenant production, sizing to
match your baseline load (e.g. `min_replicas = 4` on a `g6e.12xlarge` cluster = one node
always warm) is usually the right call.

---

## Additional scripts

Run custom shell scripts as part of every deployment — before the NIM or vLLM process starts.
Scripts can be local files or existing S3 objects; both are supported per-endpoint.

```hcl
sagemaker_endpoints = {
  nim = {
    llama = {
      source_image_uri = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
      instance_type    = "ml.g6e.12xlarge"

      # Scripts run in order inside the container before Caddy and NIM start.
      # Local files are uploaded to S3 automatically — no manual zip or upload needed.
      additional_scripts = [
        { source = "./scripts/tune-kernel.sh" },              # local file
        { source = "s3://my-bucket/scripts/setup-nvme.sh" }, # existing S3 object
      ]
    }
  }
}
```

```hcl
eks_deployments = {
  nim = {
    llama = {
      cluster_key      = "gpu-cluster"
      source_image_uri = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"

      # Scripts run in order as init containers before the NIM pod starts.
      additional_scripts = [
        { source = "./scripts/tune-kernel.sh" },
        { source = "s3://my-bucket/scripts/setup-nvme.sh" },
      ]
    }
  }
}
```

**How it works:**

- `additional_scripts` is a list — scripts execute in the order listed.
- Local paths are uploaded to the module's CodeBuild S3 bucket at `additional-scripts/{filemd5}/{filename}`. The key is keyed by content hash, so re-uploading an unchanged file is a no-op.
- S3 URIs are passed through directly — the module does not copy or validate them at plan time.

### Mechanism by platform

EKS and SageMaker use different primitives for the same feature because the two platforms
have different building blocks available. The user-visible behavior is identical — scripts
run in order, before the inference process starts, and a non-zero exit aborts startup. The
implementation under the hood is platform-native.

| Aspect | EKS | SageMaker |
| ------ | --- | --------- |
| Mechanism | Kubernetes [init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) — one per script | Bash loop inside the main container's entrypoint (`shim/launch.sh`) |
| Container image | `amazon/aws-cli:latest` (separate, ephemeral) | Inherits the shim image (Caddy + launcher) |
| Isolation | Each script runs in its own filesystem/process namespace | Scripts share filesystem and environment with the main container |
| Ordering | Kubelet runs them sequentially; each must exit 0 before next starts | `while read` loop; `set -e` style — non-zero exits abort startup |
| Failure mode | Pod stuck in `Init:0/N` state, never reaches `Running` | Container fails to start → SageMaker endpoint transitions to `Failed` |
| IAM | NIM IRSA role (pod-level service account → IAM role) | SageMaker execution role (model-level) |
| Where the generation logic lives | [`modules/eks-app/buildspecs/deploy-nim.yml`](modules/eks-app/buildspecs/deploy-nim.yml) (CodeBuild generates init containers in the Helm values) | [`shim/launch.sh`](shim/launch.sh) (the entrypoint loops over `ADDITIONAL_SCRIPTS` env var) |

**Why different idioms instead of one shared approach?** SageMaker has no concept of init
containers — you give it one container image to run. EKS, conversely, doesn't run our
SageMaker shim (`launch.sh`) on the NIM container — it uses the NIM image directly via Helm.
Init containers are the K8s-native way to run pre-flight scripts without modifying the main
container's entrypoint; the shim's bash loop is the only place that exists on the SageMaker
path. Both produce the same outcome through different machinery.

**IAM details (handled automatically):**

- **EKS**: NIM IRSA role gets `s3:GetObject` on `${codebuild_bucket}/additional-scripts/*` and on every external bucket referenced by an `s3://` URI in `additional_scripts`. Policies are attached only to clusters that have at least one deployment using `additional_scripts`.
- **SageMaker**: The execution role gets the same `s3:GetObject` grants. Policies are added only when at least one SageMaker endpoint uses `additional_scripts`.
- External buckets across both platforms are unioned into a single set, so an `s3://my-shared-bucket/...` URI used on both EKS and SageMaker is granted once.

See [examples/sagemaker/additional-scripts/](examples/sagemaker/additional-scripts/) and [examples/eks/additional-scripts/](examples/eks/additional-scripts/) for working examples.

---

## All platforms simultaneously

```hcl
module "inference" {
  source = "git::https://github.com/NVIDIA/nvidia-aws-samples.git//inference/terraform-aws-nim?ref=main"

  project_prefix = "my-project"
  environment    = "prod"
  region         = "us-east-1"

  ngc_credentials = { secret_arn = "arn:aws:secretsmanager:..." }
  hf_credentials  = { secret_arn = "arn:aws:secretsmanager:..." }

  # SageMaker — NIM and open weight side-by-side for A/B
  sagemaker_endpoints = {
    llama-nim = {
      source_image_uri = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
      instance_type    = "ml.g6e.12xlarge"
    }
    llama-vllm = {
      model_id      = "meta-llama/Llama-3.1-8B-Instruct"
      model_source  = "huggingface"
      instance_type = "ml.g6e.12xlarge"
    }
  }

  # EKS — NIM on GPU cluster
  eks_clusters = {
    gpu-cluster = {
      vpc_id             = aws_vpc.main.id
      private_subnet_ids = aws_subnet.private[*].id
      public_subnet_ids  = aws_subnet.public[*].id
      instance_type      = "g6e.12xlarge"
      allowed_cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
      internet_gateway_id = aws_internet_gateway.main.id
    }
  }
  eks_deployments = {
    nim = {
      llama-eks = {
        cluster_key      = "gpu-cluster"
        source_image_uri = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
      }
    }
  }
}
```

---

## Credentials

### NGC credentials (NIM images and NGC model artifacts)

```hcl
# Recommended — Secrets Manager ARN.
# secret_json_key = "access-key" means the module references the JSON key named
# "access-key" from the stored secret. See "Secret format" below.
ngc_credentials = {
  secret_arn      = "arn:aws:secretsmanager:us-east-1:123456789012:secret:ngc-api-key"
  secret_json_key = "access-key"
}

# Development only — stored in Terraform state.
ngc_credentials = {
  api_key = "nvapi-..."
}
```

#### Secret format

When using `secret_arn`, the module passes an AWS Secrets Manager reference of the form
`<arn>:<secret_json_key>::` to CodeBuild — CodeBuild fetches the value at build start via
IAM. The raw key never enters Terraform state or the CodeBuild project configuration.

CodeBuild's SECRETS_MANAGER env-var mode requires you to declare the shape of the secret:

- **Recommended:** create a JSON secret with a key named exactly `access-key`
  (case-sensitive) and set `secret_json_key = "access-key"` in your `ngc_credentials`
  block. AWS CLI:

  ```bash
  aws secretsmanager create-secret \
    --name my-ngc-key \
    --secret-string '{"access-key":"<paste-your-NGC-API-key-here>"}' \
    --region us-east-1
  ```

- **Plaintext secret:** if the secret is stored as a raw string (no JSON), leave
  `secret_json_key = null`. The module then passes just the ARN — CodeBuild returns the
  whole SecretString.

- **Custom JSON key name:** if your secret is JSON with a different key name (e.g.
  `{"ngc_api_key": "..."}`), set `secret_json_key = "ngc_api_key"`.

Providing both `api_key` and `secret_arn` for either credential is a validation error.

### HuggingFace credentials (gated open-weight models)

Same shape and semantics as `ngc_credentials`:

```hcl
hf_credentials = {
  secret_arn      = "arn:aws:secretsmanager:us-east-1:123456789012:secret:hf-token"
  secret_json_key = "access-key"  # if the secret is JSON with an "access-key" field
}
```

Public HuggingFace models do not require `hf_credentials`.

> **Gated models require manual license acceptance before `terraform apply`.**
> Models like Meta Llama are gated on HuggingFace — a valid token is not enough on its own.
> The HuggingFace account that owns the token must first visit
> `huggingface.co/<org>/<repo>` and click **"Agree and access repository"**.
> Approval is usually instant. Without it, the weight-fetch CodeBuild job will fail with
> `Error: Access denied. This repository requires approval.`
>
> This friction does not exist for NIM endpoints — NVIDIA handles licensing on the NGC side
> and the NIM container manages its own weight download at startup.

---

## Automatic Model Profile Selection

When `enable_model_profile_cache = true`, the module runs `list-model-profiles` inside the
NIM container and picks the best NGC profile for the target instance type before the endpoint
starts. This reduces cold-start time from ~5–10 min (NGC download) to ~2–5 min (S3 sync).

Selection priority (first match wins):

1. TRT-LLM — GPU-specific name + `tp{n}` + `bf16` + `throughput`
2. TRT-LLM — GPU-specific name + `tp{n}` + `bf16`
3. TRT-LLM — GPU-specific name + `tp{n}`
4. vLLM — `tp{n}` + `bf16`
5. vLLM — `tp{n}`
6. Any profile with `tp1` + `bf16`
7. Any profile with `tp1`
8. **Hard error** — prints full profile list; use `model_profile` to set an explicit override

| Instance family | GPU        | VRAM  | Auto-select target          |
| --------------- | ---------- | ----- | --------------------------- |
| `ml.g6e.*`      | L40S       | 48 GB | `l40s-tp{n}-bf16`           |
| `ml.g6.*`       | L4         | 24 GB | `l4-tp{n}-bf16`             |
| `ml.g5.*`       | A10G       | 24 GB | `a10g-tp{n}-bf16`           |
| `ml.p5.*`       | H100 SXM   | 80 GB | `h100-tp{n}-bf16`           |
| `ml.p4d.*`      | A100 40 GB | 40 GB | `a100_sxm4_40gb-tp{n}-bf16` |
| `ml.p4de.*`     | A100 80 GB | 80 GB | `a100-tp{n}-bf16`           |

---

## Debugging and Forced Rebuilds

| Variable        | Scope                  | Effect                                              |
| --------------- | ---------------------- | --------------------------------------------------- |
| `debug`         | module or per-endpoint | Enables `set -x`, timestamps, elapsed time per step |
| `force_rebuild` | module or per-endpoint | Retriggers all CodeBuild builds on next apply       |

```hcl
sagemaker_endpoints = {
  llama = {
    source_image_uri = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
    instance_type    = "ml.g6e.12xlarge"
    debug            = true   # verbose logs for this endpoint only
  }
}
```

Set `force_rebuild = false` after the one-time retrigger — idempotency guards in each
buildspec make retriggered builds cheap when nothing changed, but the timestamp-based trigger
still fires on every apply until disabled.

---

## Invoking endpoints

### SageMaker realtime

```bash
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name $(terraform output -json endpoint_names | jq -r '.["<key>"]') \
  --content-type application/json \
  --cli-binary-format raw-in-base64-out \
  --body '{"model":"meta/llama-3.1-8b-instruct","messages":[{"role":"user","content":"Who is Jensen Huang in one sentence?"}],"max_tokens":50}' \
  --region us-east-1 \
  /tmp/response.json && cat /tmp/response.json
```

### SageMaker async

```bash
aws s3 cp payload.json s3://<your-bucket>/input/payload.json

aws sagemaker-runtime invoke-endpoint-async \
  --endpoint-name <endpoint-name> \
  --content-type application/json \
  --input-location s3://<your-bucket>/input/payload.json \
  --region us-east-1

# Poll outputLocation from the invoke response
aws s3 cp <outputLocation> /tmp/response.json && cat /tmp/response.json
```

### EKS

```bash
# Get NLB hostname from CodeBuild post_build output, or:
kubectl get svc -n nim -l "app.kubernetes.io/instance=<release-name>" \
  -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}'

curl http://<nlb-hostname>:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"meta/llama-3.1-8b-instruct","messages":[{"role":"user","content":"Who is Jensen Huang in one sentence?"}]}'
```

---

## Troubleshooting

### Endpoint reaches `Failed` — container startup timeout

CloudWatch Logs → `/aws/sagemaker/Endpoints/{endpoint-name}/AllTraffic/{instance-id}`.
Find the gap between container start and first `200` on the health check path. If ≥
`container_startup_timeout`, increase the value:

```hcl
container_startup_timeout = 900   # 15 min — covers most NIM sizes on g6e with warm cache
# container_startup_timeout = 1800  # for 70B+ or cold-start without cache
```

### `Cannot create already existing endpoint`

**When it happens:** An endpoint reaches `Failed` (e.g. OOM from a missing `tensor-parallel-size`
on a large model), Terraform removes it from state, you fix the config and re-apply — but
SageMaker still holds the old endpoint name. Terraform tries to create a new endpoint with the
same name and collides.

**Why NIMs rarely hit this:** NIMs auto-select tensor parallelism, precision, and engine
configuration from NGC model profiles. There is almost nothing to misconfigure at the
`source_image_uri` level. The main failure modes for NIMs are outside the module's control:
insufficient instance capacity or NGC credential issues.

**Why open-weight deployments can hit this:** vLLM has no auto-selection. If you omit
`tensor-parallel-size` for a model that doesn't fit on one GPU, vLLM defaults to
`tensor_parallel_size=1`, the container OOMs, the endpoint reaches `Failed`, and the name
gets stuck. This is the most common cause.

**Root cause:** A known Terraform AWS provider bug ([#40080](https://github.com/hashicorp/terraform-provider-aws/issues/40080)).
The provider does not wait for SageMaker to fully release the endpoint name after deletion.
`UpdateEndpoint` (the normal path for healthy endpoints) is unaffected — this only occurs when
an endpoint is in `Failed` state and falls out of Terraform state.

**Fix:** Generate a new endpoint name by replacing the suffix resource:

For NIM endpoints:
```bash
terraform apply -replace='module.terraform-aws-nim.random_id.endpoint_suffix_nim["<key>"]'
```

For open-weight endpoints:
```bash
terraform apply -replace='module.terraform-aws-nim.random_id.endpoint_suffix_ow["<key>"]'
```

Both can be combined in a single `apply` if needed:
```bash
terraform apply \
  -replace='module.terraform-aws-nim.random_id.endpoint_suffix_nim["<key>"]' \
  -replace='module.terraform-aws-nim.random_id.endpoint_suffix_ow["<key>"]'
```

This gives the new endpoint a different name (`-<new_hex>`) and leaves the stale Failed
endpoint to be cleaned up separately. The old endpoint can be deleted from the AWS console
or via `aws sagemaker delete-endpoint --endpoint-name <name>`.

**How to avoid it on open-weight deployments:** Always check the model card for VRAM
requirements before choosing an instance type. For models larger than one GPU's VRAM,
set `tensor-parallel-size` in `extra_args` equal to the number of GPUs on the instance
(e.g. `"4"` for `ml.g6e.12xlarge` with 4× L40S). Enabling `enable_vllm_recipe = true`
fetches community-validated settings that include tensor parallelism for supported models.

### `InvalidSignatureException: Signature expired` during apply

**This is not a module bug.** It is a local machine clock drift issue that only surfaces here
because of how this module works.

**Why it happens here:** All AWS API calls include a SigV4 signature timestamped with the
caller's system clock. AWS rejects any request where that timestamp is more than 5 minutes
behind real UTC time. Most Terraform applies finish in seconds — fast enough that drift never
matters. This module is different: it triggers CodeBuild builds that can run for 10–60+ minutes
and polls them via repeated `BatchGetBuilds` calls for the entire duration. These builds do
real work — downloading tens to hundreds of GB of model weights from HuggingFace or NGC,
pulling and building Docker images, running NIM containers to generate GPU-specific model
profiles. If your laptop goes to sleep mid-apply and the OS NTP daemon hasn't re-synced by
the time Terraform makes the next poll, the signature is rejected and the apply fails.

**Why CI/CD never hits this:** CodeBuild, GitHub Actions, and GitLab CI runners are always-on
cloud VMs. Their clocks are managed continuously by the cloud provider's NTP infrastructure.
There is no sleep, no drift, no threshold to cross.

**Fix — sync your clock and re-run:**

```bash
# macOS
sudo sntp -sS time.apple.com

# Linux
sudo ntpdate -u pool.ntp.org

terraform apply  # CodeBuild builds that already completed skip immediately via S3 marker checks
```

**Prevention — stop your machine sleeping during apply:**

```bash
# macOS — caffeinate prevents idle sleep for the duration of the command
caffeinate -i terraform apply

# Linux
systemd-inhibit terraform apply

# Windows (PowerShell) — no built-in equivalent; adjust sleep settings manually:
# Control Panel → Power Options → Change plan settings → Put computer to sleep → Never
# Remember to revert after the apply completes.
# If running Terraform inside WSL2, the Windows host controls sleep — use the above.
```

Or add a shell alias so it's always on (macOS/Linux):

```bash
# ~/.zshrc or ~/.bashrc
alias tf='caffeinate -i terraform'   # macOS
alias tf='systemd-inhibit terraform' # Linux
```

### `InsufficientInstanceCapacity`

SageMaker retries internally for the full startup timeout before failing. Retry after some
time, try a different AZ by specifying `existing_subnet_ids`, or try a different instance
type. For guaranteed capacity, use an EC2 On-Demand Capacity Reservation (not yet wired in
the module — see DEVELOPER_REFERENCE.md).

---

## Architecture

```
                        ┌─────────────────────────────────────────────┐
  source_image_uri      │              CodeBuild chain                 │
  (NIM / custom)        │                                              │
       │                │  base-sync → ECR:base                        │
       └──────────────► │  shim build → ECR:shim (SageMaker only)     │
                        │  weight-fetch → S3:open-weights/ (OW only)  │
  model_id              │  profile-cache → S3:nim-cache/ (optional)   │
  (open weight)         │                                              │
       └──────────────► │                                              │
                        └──────────────────────────────────────────────┘
                                   │              │              │
                                   ▼              ▼
                             SageMaker         EKS
                             ECR:shim        ECR:base
                             + ModelDataUrl  + NLB
                             (OW: S3 weights) (OW: emptyDir)
```

**Shared across platforms:** One ECR repo, one S3 cache bucket, one IAM role. Endpoints
sharing the same `source_image_uri` or `model_id` share one base image and one cache prefix
regardless of which platform they deploy to.

---

## Examples

- [sagemaker/nim/](examples/sagemaker/nim/) — NIM on SageMaker
- [sagemaker/open-weight/](examples/sagemaker/open-weight/) — open-weight LLM via vLLM on SageMaker
- [sagemaker/additional-scripts/](examples/sagemaker/additional-scripts/) — SageMaker NIM + open-weight with `additional_scripts`
- [eks/nim/](examples/eks/nim/) — NIM on EKS Auto Mode with model profile cache
- [eks/open-weight/](examples/eks/open-weight/) — open-weight LLM via vLLM on EKS
- [eks/additional-scripts/](examples/eks/additional-scripts/) — EKS NIM + open-weight with `additional_scripts`
- [all-inference/](examples/all-inference/) — SageMaker + EKS, NIM + open-weight simultaneously

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [DESIGN_STANDARDS.md](DESIGN_STANDARDS.md), and
[DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md).

---

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.15 |
| <a name="requirement_archive"></a> [archive](#requirement\_archive) | >= 2.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 6.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | >= 3.0 |
| <a name="requirement_time"></a> [time](#requirement\_time) | >= 0.9 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_archive"></a> [archive](#provider\_archive) | >= 2.0 |
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 6.0 |
| <a name="provider_random"></a> [random](#provider\_random) | >= 3.0 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |
| <a name="provider_time"></a> [time](#provider\_time) | >= 0.9 |

## Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_eks_app_nim"></a> [eks\_app\_nim](#module\_eks\_app\_nim) | ./modules/eks-app | n/a |
| <a name="module_eks_app_open_weight"></a> [eks\_app\_open\_weight](#module\_eks\_app\_open\_weight) | ./modules/eks-app | n/a |
| <a name="module_eks_infra"></a> [eks\_infra](#module\_eks\_infra) | ./modules/eks-infra | n/a |

## Resources

| Name | Type |
| ---- | ---- |
| [aws_cloudwatch_log_group.sagemaker_endpoint_nim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.sagemaker_endpoint_ow](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_codebuild_project.base_sync](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_project) | resource |
| [aws_codebuild_project.model_profile_cache](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_project) | resource |
| [aws_codebuild_project.shim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_project) | resource |
| [aws_codebuild_project.weight_fetch](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_project) | resource |
| [aws_ecr_lifecycle_policy.nim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_lifecycle_policy) | resource |
| [aws_ecr_repository.nim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository) | resource |
| [aws_iam_role.codebuild](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.sagemaker_execution](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.codebuild](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.nim_irsa_s3_additional_scripts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.nim_irsa_s3_external_scripts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.nim_irsa_s3_model_assets](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.sagemaker_inline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.sagemaker_full_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_s3_bucket.codebuild](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket.model_assets](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket.nim_cache](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket.sagemaker_output](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket_lifecycle_configuration.nim_cache](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_lifecycle_configuration) | resource |
| [aws_s3_bucket_versioning.nim_cache](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning) | resource |
| [aws_s3_object.additional_scripts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_s3_object.cluster_setup_buildspec](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_s3_object.deploy_nim_buildspec](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_s3_object.shim_source](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_sagemaker_endpoint.nim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sagemaker_endpoint) | resource |
| [aws_sagemaker_endpoint.open_weight](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sagemaker_endpoint) | resource |
| [aws_sagemaker_endpoint_configuration.nim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sagemaker_endpoint_configuration) | resource |
| [aws_sagemaker_endpoint_configuration.open_weight](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sagemaker_endpoint_configuration) | resource |
| [aws_sagemaker_model.nim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sagemaker_model) | resource |
| [aws_sagemaker_model.open_weight](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sagemaker_model) | resource |
| [random_id.endpoint_config_suffix_nim](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [random_id.endpoint_config_suffix_open_weight](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [random_id.endpoint_suffix_nim](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [random_id.endpoint_suffix_ow](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [random_id.model_content_suffix_nim](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [random_id.model_content_suffix_open_weight](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [random_id.suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) | resource |
| [terraform_data.build_trigger_base_sync](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.build_trigger_model_profile_cache](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.build_trigger_shim](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.build_trigger_weight_fetch](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.validation](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [time_sleep.codebuild_iam_propagation](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |
| [archive_file.shim_source](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.codebuild_assume](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.codebuild_inline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.nim_irsa_s3_additional_scripts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.nim_irsa_s3_external_scripts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.nim_irsa_s3_model_assets](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.sagemaker_assume](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.sagemaker_inline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_secretsmanager_secret_version.hf_token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/secretsmanager_secret_version) | data source |
| [aws_secretsmanager_secret_version.ngc_api_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/secretsmanager_secret_version) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_environment"></a> [environment](#input\_environment) | Deployment environment label (e.g. dev, staging, prod). Combined with project\_prefix to form local.name\_prefix. | `string` | n/a | yes |
| <a name="input_project_prefix"></a> [project\_prefix](#input\_project\_prefix) | Prefix for all resource names. Should identify the deployment (e.g. "nim-alpamayo", "nim-llama"). Combined with environment to form local.name\_prefix. | `string` | n/a | yes |
| <a name="input_cache_path"></a> [cache\_path](#input\_cache\_path) | Filesystem path inside the container where NIM reads its cached model artifacts.<br/>At startup, launch.sh syncs from S3 (MODEL\_PROFILE\_CACHE env var) into this path.<br/><br/>Standard NGC NIMs use /opt/nim/.cache (default). Custom NIMs may require a<br/>different path — see the NIM image documentation. | `string` | `"/opt/nim/.cache"` | no |
| <a name="input_debug"></a> [debug](#input\_debug) | Enable verbose logging in all CodeBuild builds — set -x, timestamps on each step,<br/>elapsed time per phase, and extended output (full profile lists, docker pull progress).<br/><br/>Applies globally to all CodeBuild projects. To enable verbose logging for a single<br/>endpoint's builds only, set debug = true inside that sagemaker\_endpoints or<br/>eks\_clusters / eks\_deployments entry. | `bool` | `false` | no |
| <a name="input_ecr_force_delete"></a> [ecr\_force\_delete](#input\_ecr\_force\_delete) | When true, the module-managed ECR repository is deletable even when it contains<br/>images. Required for clean terraform destroy after base-sync or shim CodeBuild<br/>builds have pushed images — which they almost always have after a first apply.<br/><br/>Set false only if you need Terraform to refuse destroy while images remain. | `bool` | `true` | no |
| <a name="input_ecr_image_retention_days"></a> [ecr\_image\_retention\_days](#input\_ecr\_image\_retention\_days) | Number of days before tagged images in the ECR repository are automatically expired.<br/>Null (default) = no age expiry — a count-based policy keeps the last 10 images instead.<br/><br/>Setting this handles the main orphan scenario: changing source\_image\_uri version<br/>(e.g. 1.8.3 → 1.9.0) leaves old {image}-{old-version}-base and {image}-{old-version}-shim<br/>tags behind. Each shim image is ~10 GB, so orphans accumulate cost quickly across<br/>many model versions.<br/><br/>Untagged images are always expired after 14 days regardless of this setting.<br/><br/>A retention of 30–90 days is a reasonable default — long enough to survive a rollback<br/>window without accumulating many stale versions. | `number` | `null` | no |
| <a name="input_eks_clusters"></a> [eks\_clusters](#input\_eks\_clusters) | Map of EKS clusters to create. Keys are user-defined cluster labels referenced<br/>by eks\_deployments[*].cluster\_key. Empty map (default) creates no EKS resources.<br/><br/>Each entry provisions an EKS Auto Mode cluster scoped to a single VPC and GPU<br/>instance type. Multiple entries allow different GPU families (e.g. g6e vs p5) or<br/>different VPCs to coexist in a single module call.<br/><br/>Key naming: letters, numbers, and hyphens only.<br/><br/>Fields:<br/>  vpc\_id                  — VPC to deploy the cluster into (required).<br/>  private\_subnet\_ids      — Private subnets for EKS nodes and CodeBuild. Must have<br/>                            NAT gateway outbound internet access for NGC pulls.<br/>  public\_subnet\_ids       — Public subnets for load balancer placement. Must be<br/>                            tagged kubernetes.io/role/elb=1.<br/>  instance\_type           — EC2 GPU instance type for NIM nodes (e.g. g6e.12xlarge).<br/>                            No ml. prefix. Sets the Karpenter NodePool constraint.<br/>  kubernetes\_version      — EKS Kubernetes version. Default "1.35" (latest standard support<br/>                               as of January 2026, available in all regions).<br/>  endpoint\_public\_access  — Enable public API server endpoint. Default true.<br/>                            Set false for fully private clusters (requires VPN or<br/>                            Direct Connect to reach the API from CodeBuild VPC).<br/>  endpoint\_private\_access — Enable private API server endpoint. Default true.<br/>                            Must be true when CodeBuild is VPC-placed (always the case<br/>                            in this module).<br/>  public\_access\_cidrs     — CIDR blocks allowed to reach the public API endpoint.<br/>                            Null = allow all. Only used when endpoint\_public\_access = true.<br/>                            Set to [your\_office\_cidr] to restrict kubectl access.<br/>  allowed\_cidr\_blocks     — CIDR blocks allowed inbound to the cluster security group<br/>                            (e.g. developer workstations, VPN, bastion subnets). These<br/>                            CIDRs receive port 443 ingress on the cluster SG. Null = no<br/>                            additional ingress beyond the VPC-internal CodeBuild rules.<br/>  internet\_gateway\_id     — IGW ID of the consumer VPC. Creates a destroy-time fence<br/>                            so the EKS cluster is always destroyed before the IGW,<br/>                            preventing NLB/ENI cleanup failures from blocking VPC<br/>                            teardown. Strongly recommended.<br/>  cluster\_log\_types       — EKS control plane log types. Default: all five types<br/>                            (api, audit, authenticator, controllerManager, scheduler).<br/>  eks\_access\_entries      — Additional IAM principals granted kubectl access.<br/>                            Map key is a unique label. Each entry may include multiple<br/>                            policy\_associations. See example below.<br/>  enable\_autoscaling      — Install the pod autoscaling stack cluster-wide (KEDA +<br/>                            kube-prometheus-stack + DCGM exporter) so any deployment on<br/>                            this cluster can opt into ScaledObject-based scaling by<br/>                            setting eks\_deployments[*].autoscaling. Default false.<br/>                            See the module README "Autoscaling" section for the<br/>                            cold-start caveats and metric-selection guidance.<br/>  debug                   — Verbose cluster-setup CodeBuild output for this cluster only.<br/>                            OR'd with var.debug.<br/>  force\_rebuild           — Force cluster-setup CodeBuild to re-run on next apply for<br/>                            this cluster only. OR'd with var.force\_rebuild.<br/><br/>Examples:<br/>  # Hybrid (public + private) — recommended for development:<br/>  eks\_clusters = {<br/>    gpu = {<br/>      vpc\_id                  = aws\_vpc.main.id<br/>      private\_subnet\_ids      = aws\_subnet.private[*].id<br/>      public\_subnet\_ids       = aws\_subnet.public[*].id<br/>      instance\_type           = "g6e.12xlarge"<br/>      endpoint\_public\_access  = true<br/>      endpoint\_private\_access = true<br/>      public\_access\_cidrs     = ["203.0.113.0/24"]  # your office IP<br/>    }<br/>  }<br/><br/>  # Private-only — production (CodeBuild reaches API over VPC):<br/>  eks\_clusters = {<br/>    gpu = {<br/>      vpc\_id                  = aws\_vpc.main.id<br/>      private\_subnet\_ids      = aws\_subnet.private[*].id<br/>      public\_subnet\_ids       = aws\_subnet.public[*].id<br/>      instance\_type           = "g6e.12xlarge"<br/>      endpoint\_public\_access  = false<br/>      endpoint\_private\_access = true<br/>    }<br/>  } | <pre>map(object({<br/>    vpc_id                  = string<br/>    private_subnet_ids      = list(string)<br/>    public_subnet_ids       = list(string)<br/>    instance_type           = string<br/>    kubernetes_version      = optional(string, "1.35")<br/>    endpoint_public_access  = optional(bool, true)<br/>    endpoint_private_access = optional(bool, true)<br/>    public_access_cidrs     = optional(list(string), null)<br/>    allowed_cidr_blocks     = optional(list(string), null)<br/>    internet_gateway_id     = optional(string, null)<br/>    cluster_log_types       = optional(list(string), ["api", "audit", "authenticator", "controllerManager", "scheduler"])<br/>    eks_access_entries = optional(map(object({<br/>      principal_arn = string<br/>      type          = optional(string, "STANDARD")<br/>      policy_associations = optional(list(object({<br/>        policy_arn = string<br/>        access_scope = object({<br/>          type       = string<br/>          namespaces = optional(list(string))<br/>        })<br/>      })), [])<br/>    })), {})<br/>    enable_autoscaling = optional(bool, false)<br/>    debug              = optional(bool, false)<br/>    force_rebuild      = optional(bool, false)<br/>  }))</pre> | `{}` | no |
| <a name="input_eks_deployments"></a> [eks\_deployments](#input\_eks\_deployments) | EKS NIM deployments. Two sub-maps: nim (Helm + NGC container) and open\_weight (kubectl + vLLM).<br/><br/>nim entries: Helm release onto the target cluster. source\_image\_uri required.<br/>open\_weight entries: raw vLLM Deployment+Service via kubectl. model\_id + model\_source required.<br/><br/>cluster\_key must match a key in eks\_clusters.<br/><br/>Example:<br/>  eks\_deployments = {<br/>    nim = {<br/>      nemotron-9b = {<br/>        cluster\_key        = "gpu"<br/>        source\_image\_uri   = "nvcr.io/nim/nvidia/nvidia-nemotron-nano-9b-v2:latest"<br/>        helm\_chart\_version = "2.0.3"<br/>      }<br/>    }<br/>    open\_weight = {<br/>      nemotron-9b = {<br/>        cluster\_key  = "gpu"<br/>        model\_id     = "nvidia/NVIDIA-Nemotron-Nano-9B-v2"<br/>        model\_source = "huggingface"<br/>      }<br/>    }<br/>  }<br/><br/>nim fields:<br/>  cluster\_key                — Key in eks\_clusters identifying the target cluster (required).<br/>  source\_image\_uri           — NIM container image URI (required). nvcr.io or ECR URI. The base<br/>                               image (synced to ECR by base-sync CodeBuild) is used directly —<br/>                               no shim for EKS.<br/>  enable\_model\_profile\_cache — Pre-sync the NGC model profile cache from S3 into the pod via<br/>                               an init container at startup. Default false. The S3 prefix is<br/>                               derived from source\_image\_uri and the cluster's instance\_type.<br/>  nim\_type                   — Categorization of the NIM, identifying the family of model<br/>                               this NIM serves. Used today to drive Helm chart selection and<br/>                               default port for the HTTP deployment path. Future versions may<br/>                               use this for other selectors (e.g., default GPU sizing<br/>                               recommendations, monitoring presets) — keep the field's<br/>                               semantics broad ("kind of NIM") even though today it primarily<br/>                               feeds the Helm path.<br/><br/>                               What `nim_type` controls today:<br/>                                 1. Helm chart name (nim-llm, text-embedding-nim, etc.)<br/>                                 2. Helm chart repo URL (per-family NGC path)<br/>                                 3. Default service port (8000 for LLM/VLM, 8080 for<br/>                                    embedding/reranking, varies for speech)<br/>                                 4. Chart-specific value shaping (e.g., Riva uses base64-encoded<br/>                                    NGC key; LLM/embedding use ngcAPISecret reference)<br/><br/>                               When protocol = "grpc" the Helm-related effects (#1, #2, #4) are<br/>                               bypassed because the gRPC path deploys via raw kubectl<br/>                               Deployment+Service. nim\_type is still meaningful for #3 (default<br/>                               port) and for documentation/categorization.<br/><br/>                               Default "llm". Valid values:<br/>                                 "llm"       — NVIDIA NIM for LLMs (Llama, Nemotron, Mistral, ...)<br/>                                               Chart: nim-llm<br/>                                               Repo: https://helm.ngc.nvidia.com/nim/charts<br/>                                               Default HTTP port: 8000<br/>                                 "vlm"       — NVIDIA NIM for Vision Language Models.<br/>                                               Chart: nim-vlm<br/>                                               Repo: https://helm.ngc.nvidia.com/nim/charts<br/>                                               Default HTTP port: 8000<br/>                                 "embedding" — NVIDIA NIM for text embedding.<br/>                                               Chart: text-embedding-nim<br/>                                               Repo: https://helm.ngc.nvidia.com/nim/nvidia/charts<br/>                                               Default HTTP port: 8080<br/>                                 "reranking" — NVIDIA NIM for text reranking (RAG rerank step).<br/>                                               Chart: text-reranking-nim<br/>                                               Repo: https://helm.ngc.nvidia.com/nim/nvidia/charts<br/>                                               Default HTTP port: 8080<br/>                                 "speech"    — NVIDIA Riva speech NIM (STT, TTS).<br/>                                               Chart: riva-api<br/>                                               Repo: https://helm.ngc.nvidia.com/nvidia/riva/charts<br/>                                               Riva-specific value shape (base64 NGC key).<br/>                                 "custom"    — Custom / internal NIM, or a NIM that doesn't fit<br/>                                               the categories above (e.g. Maxine media NIMs:<br/>                                               SVD, Audio2Face, Studio Voice, Eye Contact, BNR).<br/>                                               When protocol = "http": must set helm\_chart\_s3\_uri<br/>                                               (S3-hosted .tgz) OR both helm\_chart\_name +<br/>                                               helm\_chart\_repo\_url. When protocol = "grpc":<br/>                                               chart info is not required (raw kubectl path).<br/>  helm\_chart\_name            — Override the NGC Helm chart name. Null (default) = derived from nim\_type.<br/>  helm\_chart\_repo\_url        — Override the base HTTPS URL for the NGC Helm chart repo.<br/>                               Null (default) = derived from nim\_type.<br/>  helm\_chart\_version         — Helm chart version to fetch from NGC. Required for NGC charts —<br/>                               NGC does not expose a chart index (index.yaml), so helm repo<br/>                               add/pull do not work. Always pin a specific version (e.g. "2.0.3").<br/>                               Ignored when helm\_chart\_s3\_uri is set.<br/>  helm\_values\_override       — Raw YAML string merged after the generated values file. Applied<br/>                               with a second -f flag so any key here wins over the generated<br/>                               defaults. Use for chart-specific fields the module does not<br/>                               generate (e.g. Riva model configs, custom resource limits).<br/>                               Required for nim\_type = "custom" since no base values are<br/>                               generated for unknown chart schemas.<br/>  helm\_chart\_s3\_uri          — S3 URI of a pre-packaged Helm chart .tgz to deploy instead of<br/>                               fetching from NGC. Format: s3://bucket/path/chart-1.0.0.tgz<br/>                               When set, helm\_chart\_name, helm\_chart\_repo\_url, and<br/>                               helm\_chart\_version are ignored.<br/>  gpu\_count                  — GPUs to request per pod replica. Default: auto-derived from the<br/>                               cluster's instance\_type. Override only when you intentionally want<br/>                               fewer GPUs. Unknown instance types fall back to 1.<br/>  replicas                   — Number of NIM pod replicas. Default 1.<br/>  namespace                  — Kubernetes namespace. Default: the deployment key.<br/>  load\_balancer\_internal     — Create an internal (VPC-only) NLB instead of internet-facing.<br/>                               Default false.<br/>  debug                      — Verbose CodeBuild output for this deployment only.<br/>  force\_rebuild              — Force re-deploy on next apply regardless of input changes.<br/>  protocol                   — Inference protocol the NIM serves. Default "http". Valid values:<br/>                                 "http" — NIM exposes HTTP/JSON inference (default for LLM NIMs,<br/>                                          embedding, Riva speech, vLLM). Deployed via Helm.<br/>                                 "grpc" — NIM exposes gRPC inference (default for Maxine media<br/>                                          NIMs: SVD, Audio2Face, Studio Voice, Eye Contact, BNR).<br/>                                          Deployed via raw kubectl Deployment+Service since no<br/>                                          Helm chart is published for Maxine NIMs on NGC today.<br/>                                          See DEVELOPER\_REFERENCE.md "Inference Protocols" for<br/>                                          background on why media NIMs use gRPC.<br/>  port                       — Service port the NIM exposes for inference. Default null →<br/>                               the module picks a sensible default based on protocol + nim\_type:<br/>                                 protocol="http", nim\_type="llm"       → 8000<br/>                                 protocol="http", nim\_type="embedding" → 8080<br/>                                 protocol="http", nim\_type="speech"    → 8000<br/>                                 protocol="grpc"                       → 8001 (Maxine convention)<br/>                               Override only when the NIM uses a non-standard port (e.g. some<br/>                               Triton-based NIMs serve gRPC on 50051).<br/>  autoscaling                — When non-null, a KEDA ScaledObject is created for this<br/>                               deployment. The `replicas` field above becomes the initial<br/>                               replica count; KEDA then adjusts within [min\_replicas,<br/>                               max\_replicas] based on the metric. Requires the target<br/>                               cluster to have enable\_autoscaling = true.<br/>                                 min\_replicas     — Floor. Default 1. Set to >=2 in prod so<br/>                                                    the first scale-up doesn't force a<br/>                                                    5-15 min NIM cold-start on a live request.<br/>                                 max\_replicas     — Ceiling. Default 5.<br/>                                 metric           — Prometheus metric name to scale on.<br/>                                                    Null (default) auto-derives from nim\_type:<br/>                                                      llm/vlm → gpu\_cache\_usage\_perc<br/>                                                      all others → DCGM\_FI\_DEV\_GPU\_UTIL<br/>                                 target\_value     — Threshold. Null (default) → 70 for both<br/>                                                    metrics above. Percentage.<br/>                                 scale\_down\_delay — HPA scale-down stabilization window in<br/>                                                    seconds. Default 600 (10 min). Passed to<br/>                                                    the underlying HPA's<br/>                                                    behavior.scaleDown.stabilizationWindowSeconds<br/>                                                    so oscillation near threshold doesn't trigger<br/>                                                    replica thrash. NIMs cold-start slow; short<br/>                                                    windows are painful. Not to be confused with<br/>                                                    KEDA's cooldownPeriod (which only controls<br/>                                                    scale-to-zero, not the min>=1 case).<br/><br/>open\_weight fields:<br/>  cluster\_key            — Key in eks\_clusters identifying the target cluster (required).<br/>  model\_id               — Open weight model ID (required). HuggingFace repo ID or NGC path.<br/>                           Same format as sagemaker\_endpoints.open\_weight.<br/>  model\_source           — Required. "huggingface" or "ngc". Controls which downloader<br/>                           weight-fetch uses.<br/>  model\_revision         — HF branch, tag, or commit. Default "main". Baked into S3 prefix —<br/>                           changing it triggers a fresh download.<br/>  extra\_args             — vLLM CLI flags passed to vllm serve. Same map(string) format as<br/>                           sagemaker\_endpoints.open\_weight.extra\_args.<br/>  gpu\_count              — GPUs to request per pod replica. Default: auto-derived from the<br/>                           cluster's instance\_type.<br/>  replicas               — Number of pod replicas. Default 1.<br/>  namespace              — Kubernetes namespace. Default: the deployment key.<br/>  load\_balancer\_internal — Create an internal (VPC-only) NLB instead of internet-facing.<br/>                           Default false.<br/>  debug                  — Verbose CodeBuild output for this deployment only.<br/>  force\_rebuild          — Force re-deploy on next apply regardless of input changes.<br/>  autoscaling            — Same schema as eks\_deployments.nim.autoscaling above. Default<br/>                           metric for open\_weight is `gpu_cache_usage_perc` (vLLM exposes<br/>                           it natively on /metrics). | <pre>object({<br/>    nim = optional(map(object({<br/>      cluster_key                = string<br/>      source_image_uri           = string<br/>      enable_model_profile_cache = optional(bool, false)<br/>      nim_type                   = optional(string, "llm")<br/>      helm_chart_name            = optional(string, null)<br/>      helm_chart_repo_url        = optional(string, null)<br/>      helm_chart_version         = optional(string, null)<br/>      helm_chart_s3_uri          = optional(string, null)<br/>      helm_values_override       = optional(string, null)<br/>      gpu_count                  = optional(number, null)<br/>      replicas                   = optional(number, 1)<br/>      namespace                  = optional(string, null)<br/>      load_balancer_internal     = optional(bool, false)<br/>      debug                      = optional(bool, false)<br/>      force_rebuild              = optional(bool, false)<br/>      additional_scripts         = optional(list(object({ source = string })), [])<br/>      protocol                   = optional(string, "http")<br/>      port                       = optional(number, null)<br/>      autoscaling = optional(object({<br/>        min_replicas     = optional(number, 1)<br/>        max_replicas     = optional(number, 5)<br/>        metric           = optional(string, null)<br/>        target_value     = optional(number, null)<br/>        scale_down_delay = optional(number, 600)<br/>      }), null)<br/>    })), {})<br/>    open_weight = optional(map(object({<br/>      cluster_key            = string<br/>      model_id               = string<br/>      model_source           = string<br/>      model_revision         = optional(string, "main")<br/>      extra_args             = optional(map(string), {})<br/>      gpu_count              = optional(number, null)<br/>      replicas               = optional(number, 1)<br/>      namespace              = optional(string, null)<br/>      load_balancer_internal = optional(bool, false)<br/>      debug                  = optional(bool, false)<br/>      force_rebuild          = optional(bool, false)<br/>      additional_scripts     = optional(list(object({ source = string })), [])<br/>      autoscaling = optional(object({<br/>        min_replicas     = optional(number, 1)<br/>        max_replicas     = optional(number, 5)<br/>        metric           = optional(string, null)<br/>        target_value     = optional(number, null)<br/>        scale_down_delay = optional(number, 600)<br/>      }), null)<br/>    })), {})<br/>  })</pre> | `{}` | no |
| <a name="input_force_rebuild"></a> [force\_rebuild](#input\_force\_rebuild) | Force all CodeBuild builds (base-sync, shim, model-profile-cache, cluster-setup,<br/>nim-deploy) to re-run on the next apply regardless of whether inputs changed.<br/>Useful for retesting a build without touching any source files.<br/><br/>Set back to false after the forced rebuild to restore normal change-detection behavior.<br/>To force-rebuild a single endpoint or cluster's builds only, set force\_rebuild = true<br/>inside that sagemaker\_endpoints, eks\_clusters, or eks\_deployments entry. | `bool` | `false` | no |
| <a name="input_hf_credentials"></a> [hf\_credentials](#input\_hf\_credentials) | HuggingFace token for gated model weight download. Required when any<br/>sagemaker\_endpoints entry has model\_source = "huggingface" and the model is gated<br/>(e.g. Meta Llama, Mistral). Public models (e.g. Qwen, Phi) do not require a token.<br/><br/>Provide exactly one of:<br/>  token      — plaintext HuggingFace token. Stored in Terraform state — use only<br/>               for development. Use secret\_arn for production.<br/>  secret\_arn — ARN of an existing AWS Secrets Manager secret containing the token.<br/><br/>Null is acceptable when all open weight endpoints use public HuggingFace models or<br/>model\_source = "ngc". | <pre>object({<br/>    token      = optional(string, null)<br/>    secret_arn = optional(string, null)<br/>  })</pre> | `null` | no |
| <a name="input_log_retention_days"></a> [log\_retention\_days](#input\_log\_retention\_days) | CloudWatch log retention in days for SageMaker endpoint log groups. Set to 0 for never expire. | `number` | `30` | no |
| <a name="input_model_profile_cache_retention_days"></a> [model\_profile\_cache\_retention\_days](#input\_model\_profile\_cache\_retention\_days) | Number of days before objects in the model profile cache bucket are automatically<br/>expired. Null (default) = no expiration — objects persist until manually deleted.<br/><br/>Setting this handles the two main orphan scenarios:<br/>  - Changing instance\_type: old nim-cache/{key}/{old\_type}/ prefix becomes dead data.<br/>  - Changing a sagemaker\_endpoints key: old nim-cache/{old\_key}/ prefix is abandoned.<br/><br/>Model profile caches are large (tens of GB per endpoint). A retention of 30–90 days<br/>is a reasonable default to auto-clean orphaned prefixes without risking a valid cache<br/>being expired mid-deployment.<br/><br/>Applies to both current and noncurrent object versions (versioning is enabled on the<br/>cache bucket to protect against partial uploads overwriting known-good artifacts). | `number` | `null` | no |
| <a name="input_ngc_credentials"></a> [ngc\_credentials](#input\_ngc\_credentials) | NGC API key for NIM license validation (checked at every container startup) and<br/>image pull when any endpoint's source\_image\_uri is an nvcr.io URI.<br/><br/>Provide exactly one of:<br/>  api\_key    — raw NGC API key string. Stored in Terraform state — only use for<br/>               development. Use secret\_arn for production.<br/>  secret\_arn — ARN of an existing AWS Secrets Manager secret. Two formats work:<br/><br/>               Option A — Plaintext secret (recommended):<br/>                 In the Secrets Manager console, choose "Plaintext" and paste<br/>                 the raw NGC API key. The module uses the value directly.<br/><br/>               Option B — Key/value secret:<br/>                 In the Secrets Manager console, choose "Key/value" and add a<br/>                 single entry with any key name and the NGC API key as the value.<br/>                 The module auto-extracts the only value. If the secret contains<br/>                 more than one key/value pair this will not work — use Plaintext<br/>                 or a dedicated single-value secret instead.<br/><br/>Providing both api\_key and secret\_arn is a validation error. Null is acceptable<br/>when all endpoints use ECR source images and license validation is not required. | <pre>object({<br/>    api_key    = optional(string, null)<br/>    secret_arn = optional(string, null)<br/>  })</pre> | `null` | no |
| <a name="input_region"></a> [region](#input\_region) | AWS region to deploy into. | `string` | `"us-east-1"` | no |
| <a name="input_s3_force_destroy"></a> [s3\_force\_destroy](#input\_s3\_force\_destroy) | When true, all module-managed S3 buckets are deletable even when non-empty.<br/>Required for clean terraform destroy when caches, build zips, or async outputs<br/>are present — which they almost always are after a first apply.<br/><br/>Set false only if you need Terraform to refuse destroy while objects remain<br/>(e.g. a compliance gate that treats the S3 bucket as the last line of defence). | `bool` | `true` | no |
| <a name="input_sagemaker_endpoints"></a> [sagemaker\_endpoints](#input\_sagemaker\_endpoints) | SageMaker inference endpoints. Two sub-maps: nim (NGC container) and open\_weight (HuggingFace/NGC weights + vLLM).<br/><br/>nim entries: use source\_image\_uri (NGC or ECR container image). Helm is not used for SageMaker.<br/>open\_weight entries: use model\_id + model\_source. Module downloads weights to S3 and runs vLLM.<br/><br/>Key naming: letters, numbers, hyphens only. Periods and underscores break SageMaker endpoint name validation.<br/><br/>Example:<br/>  sagemaker\_endpoints = {<br/>    nim = {<br/>      nemotron-9b = {<br/>        source\_image\_uri           = "nvcr.io/nim/nvidia/nvidia-nemotron-nano-9b-v2:latest"<br/>        instance\_type              = "ml.g6e.12xlarge"<br/>        enable\_model\_profile\_cache = true<br/>      }<br/>    }<br/>    open\_weight = {<br/>      nemotron-9b = {<br/>        model\_id      = "nvidia/NVIDIA-Nemotron-Nano-9B-v2"<br/>        model\_source  = "huggingface"<br/>        instance\_type = "ml.g6e.12xlarge"<br/>      }<br/>    }<br/>  }<br/><br/>nim per-endpoint fields:<br/>  source\_image\_uri           — NIM container image URI (required). Two forms:<br/>                                 NGC: "nvcr.io/nim/<org>/<model>:<tag>"<br/>                                       Requires ngc\_credentials to be set.<br/>                                 ECR: "<account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>"<br/>                                       Authenticated via IAM — no extra credentials.<br/><br/>  instance\_type              — SageMaker instance type (required). e.g. "ml.g6e.12xlarge".<br/><br/>                               Validated instance types for standard NGC NIMs:<br/>                                 ml.g6e.12xlarge — 4x L40S (48 GB VRAM)  SM89  VALIDATED<br/>                                 ml.g6.12xlarge  — 4x L4   (24 GB VRAM)  SM89  at VRAM minimum<br/>                                 ml.p5.48xlarge  — 8x H100 (80 GB VRAM)  SM90  confirmed<br/>                                 ml.g5.*         — A10G/SM86 — avoid; vllm:latest requires CUDA driver >= 580.x, g5 AMIs ship older drivers<br/><br/>  endpoint\_type              — SageMaker endpoint invocation mode. Default "realtime".<br/>                                 "realtime" — synchronous inference (POST /invocations,<br/>                                              response returned inline). Request body limit<br/>                                              6 MB. Best for standard NGC NIMs (Llama, etc.)<br/>                                              with small-to-moderate payloads.<br/>                                 "async"    — asynchronous inference. Payload uploaded to S3,<br/>                                              response written to async\_output\_s3\_prefix.<br/>                                              Required for large payloads (> 6 MB) — e.g.<br/>                                              Alpamayo (16 base64-encoded camera frames, ~50 MB).<br/>                                              Adds async\_output\_s3\_prefix to the config.<br/><br/>  sync\_to\_ecr                — Controls whether the source image is copied into the module's<br/>                               ECR repo before the shim is built. Default true.<br/>                               The shim image always lives in your ECR regardless of this setting.<br/><br/>                               Four cases:<br/>                                 nvcr.io URI  + sync\_to\_ecr = true  (default) — base-sync pulls<br/>                                   from NGC -> your ECR. Shim + cache use your ECR.<br/>                                 ECR URI      + sync\_to\_ecr = true  — base-sync pulls from their<br/>                                   ECR -> your ECR. Shim + cache use your ECR.<br/>                                 ECR URI      + sync\_to\_ecr = false — base-sync skipped. Shim<br/>                                   builds FROM source URI directly. If enable\_model\_profile\_cache<br/>                                   = true, cache also runs FROM source URI. Their account must<br/>                                   grant your SageMaker execution role pull access.<br/>                                 nvcr.io URI  + sync\_to\_ecr = false — INVALID. nvcr.io requires<br/>                                   NGC credentials not available at SageMaker/EKS runtime.<br/><br/>  container\_startup\_timeout  — Health-check timeout in seconds. Default 600 (10 min)<br/>                               suits a warm S3 cache. Increase to 3600 for cold start.<br/><br/>  enable\_model\_profile\_cache — Pre-deployment cache the best NGC model profile for this<br/>                               endpoint in S3. Default false. Reduces cold start from<br/>                               ~5-10 min (NGC download) to ~2-5 min (S3 sync).<br/>                               Cache prefix: s3://<cache\_bucket>/nim-cache/<key>/<br/><br/>  model\_profile              — NGC profile name prefix override. null (default) =<br/>                               auto-select best profile for the instance type. Non-null<br/>                               = prefix-match (e.g. "vllm-bf16-tp1"). The full name<br/>                               with workspace hash is resolved automatically.<br/>                               Requires enable\_model\_profile\_cache = true.<br/><br/>  inference\_ami\_version      — Explicit SageMaker InferenceAmiVersion override. null<br/>                               (default) lets SageMaker pick the AMI.<br/><br/>  endpoint\_name              — Custom endpoint name override. null (default) auto-generates<br/>                               as "${project\_prefix}-${environment}-${key}".<br/><br/>  async\_output\_s3\_prefix     — S3 key prefix for async inference response payloads,<br/>                               relative to s3://<output\_bucket>/<key>/. Default: "async-output/".<br/><br/>  ml\_reservation\_arn         — ARN of a SageMaker Flexible Training Plan reservation.<br/>                               STUB — hashicorp/aws provider does not expose this attribute yet.<br/>                               See DEVELOPER\_REFERENCE.md.<br/><br/>  debug                      — Enable verbose logging for this endpoint's CodeBuild builds<br/>                               only (base-sync, shim, model-profile-cache). Equivalent to<br/>                               the module-level debug variable but scoped to this endpoint.<br/><br/>  force\_rebuild              — Force this endpoint's CodeBuild builds to re-run on the next<br/>                               apply regardless of whether inputs changed. Only retriggers<br/>                               builds for this endpoint's source URI (and instance type for<br/>                               cache). Other endpoints are unaffected.<br/><br/>  shim\_config                — Per-endpoint overrides for the SageMaker shim image (Caddy<br/>                               proxy + NIM launcher). Mirrors var.shim\_config but scoped to<br/>                               this endpoint only — same hierarchy as debug / force\_rebuild<br/>                               vs. var.shim\_config; null fields fall back to var.shim\_config.<br/>                               Omit entirely for standard NGC NIMs.<br/><br/>                               nim\_cmd            — Shell command to start the NIM.<br/>                               nim\_entrypoint     — NIM entrypoint script path in base image.<br/>                               caddy\_backend\_port — Port Caddy routes to. Null = auto-detected<br/>                                                    from NIM\_HTTP\_API\_PORT at container startup<br/>                                                    (standard NIMs expose 8000). Only set for<br/>                                                    custom NIMs on a different port (e.g. 8001).<br/>                               cuda\_driver\_label  — CUDA version for SageMaker AMI selection.<br/><br/>                               Example (custom NIM):<br/>                                 shim\_config = {<br/>                                   nim\_cmd            = "python /workspace/server.py"<br/>                                   caddy\_backend\_port = 8001<br/>                                 }<br/><br/>open\_weight per-endpoint fields:<br/>  model\_id               — Open weight model identifier (required). When set the module runs a<br/>                           weight-fetch CodeBuild job (downloads weights to S3), builds a vLLM<br/>                           shim image, and syncs weights from S3 at container startup.<br/>                           Format depends on model\_source:<br/>                             "huggingface" — HuggingFace repo ID,<br/>                                             e.g. "meta-llama/Llama-3.1-8B-Instruct"<br/>                                             NOTE: gated models (e.g. Meta Llama)<br/>                                             require the HF account to accept terms<br/>                                             at huggingface.co/<org>/<repo> before<br/>                                             apply. A valid token alone is not enough.<br/>                             "ngc"         — NGC model path including version,<br/>                                             e.g. "meta/llama-3.1-8b-instruct:1.0"<br/><br/>  model\_source           — Source registry for open weight download (required).<br/>                           Must be "huggingface" or "ngc".<br/>                             "huggingface" — huggingface-cli download. Requires<br/>                                             hf\_credentials for gated models.<br/>                             "ngc"         — ngc registry model download-version.<br/>                                             Requires ngc\_credentials.<br/><br/>  instance\_type          — SageMaker instance type (required). e.g. "ml.g6e.12xlarge".<br/><br/>  model\_revision         — HF branch, tag, or commit hash. Default "main". Baked into<br/>                           the S3 prefix — changing it triggers a fresh download to a<br/>                           new prefix. Ignored for NGC (version is in model\_id).<br/><br/>  framework              — Inference framework for the shim container image. Default "vllm".<br/>                           Currently supported: "vllm". Planned: "triton".<br/><br/>  extra\_args             — Framework CLI flags passed to the inference server at<br/>                           container startup. map(string) where each key is a flag name<br/>                           (without --) and the value is the flag value, or "" for boolean<br/>                           flags. Always overrides any flags from enable\_vllm\_recipe.<br/>                           Examples:<br/>                             extra\_args = {<br/>                               max-model-len = "8192"<br/>                               dtype         = "bfloat16"<br/>                               enforce-eager = ""<br/>                             }<br/><br/>  enable\_vllm\_recipe     — Fetch optimized vllm serve flags from recipes.vllm.ai at<br/>                           weight-fetch time. Default false. When true, the weight-fetch<br/>                           CodeBuild queries https://recipes.vllm.ai/<hf\_org>/<hf\_repo>.json<br/>                           and writes a recipe env file to S3. launch.sh sources it at<br/>                           container startup, applying base\_args and variant extra\_args<br/>                           before any explicit extra\_args (user always wins). If the model<br/>                           has no recipe, the build logs a warning and falls back to vLLM<br/>                           defaults — the endpoint still deploys. Only applies to<br/>                           model\_source = "huggingface" (NGC models do not have vLLM recipes).<br/><br/>  vllm\_precision         — Precision variant to select from the vLLM recipe. Default "default"<br/>                           (bf16). Set to "fp8" for FP8-quantized recipes when available.<br/>                           Ignored when enable\_vllm\_recipe = false.<br/><br/>  endpoint\_name          — Custom endpoint name override. null (default) auto-generates<br/>                           as "${project\_prefix}-${environment}-${key}".<br/><br/>  async\_output\_s3\_prefix — S3 key prefix for async inference response payloads,<br/>                           relative to s3://<output\_bucket>/<key>/. Default: "async-output/".<br/><br/>  ml\_reservation\_arn     — ARN of a SageMaker Flexible Training Plan reservation.<br/>                           STUB — hashicorp/aws provider does not expose this attribute yet.<br/>                           See DEVELOPER\_REFERENCE.md.<br/><br/>  debug                  — Enable verbose logging for this endpoint's CodeBuild builds only.<br/><br/>  force\_rebuild          — Force this endpoint's CodeBuild builds to re-run on the next apply. | <pre>object({<br/>    nim = optional(map(object({<br/>      source_image_uri           = string<br/>      instance_type              = string<br/>      endpoint_type              = optional(string, "realtime")<br/>      sync_to_ecr                = optional(bool, true)<br/>      container_startup_timeout  = optional(number, 600)<br/>      enable_model_profile_cache = optional(bool, false)<br/>      model_profile              = optional(string, null)<br/>      inference_ami_version      = optional(string, null)<br/>      endpoint_name              = optional(string, null)<br/>      async_output_s3_prefix     = optional(string, "async-output/")<br/>      ml_reservation_arn         = optional(string, null)<br/>      debug                      = optional(bool, false)<br/>      force_rebuild              = optional(bool, false)<br/>      additional_scripts         = optional(list(object({ source = string })), [])<br/>      shim_config = optional(object({<br/>        nim_cmd            = optional(string, null)<br/>        nim_entrypoint     = optional(string, null)<br/>        caddy_backend_port = optional(number, null)<br/>        cuda_driver_label  = optional(string, null)<br/>      }), {})<br/>    })), {})<br/>    open_weight = optional(map(object({<br/>      model_id                  = string<br/>      model_source              = string<br/>      instance_type             = string<br/>      model_revision            = optional(string, "main")<br/>      framework                 = optional(string, "vllm")<br/>      extra_args                = optional(map(string), {})<br/>      enable_vllm_recipe        = optional(bool, false)<br/>      vllm_precision            = optional(string, "default")<br/>      endpoint_type             = optional(string, "realtime")<br/>      container_startup_timeout = optional(number, 600)<br/>      inference_ami_version     = optional(string, null)<br/>      endpoint_name             = optional(string, null)<br/>      async_output_s3_prefix    = optional(string, "async-output/")<br/>      ml_reservation_arn        = optional(string, null)<br/>      debug                     = optional(bool, false)<br/>      force_rebuild             = optional(bool, false)<br/>      additional_scripts        = optional(list(object({ source = string })), [])<br/>    })), {})<br/>  })</pre> | `{}` | no |
| <a name="input_shim_config"></a> [shim\_config](#input\_shim\_config) | Module-level defaults for the SageMaker shim container (Caddy proxy + framework<br/>launcher). The shim is a permanent SageMaker requirement: SageMaker hardcodes<br/>POST /invocations and GET /ping, which no inference framework serves natively.<br/>Caddy rewrites these paths to the framework's native API paths.<br/><br/>These values apply to all NIM endpoints. A per-endpoint shim block inside<br/>sagemaker\_endpoints takes priority over these defaults for that specific endpoint —<br/>same hierarchy as var.debug / var.force\_rebuild vs. per-endpoint debug / force\_rebuild.<br/>Open weight endpoints (model\_id set) use framework-specific defaults automatically.<br/><br/>Omit this variable entirely for standard NGC NIMs — the defaults work out of the box.<br/><br/>nim\_cmd            — Shell command to start the NIM server process.<br/>                     Default suits all standard NGC NIMs.<br/>                     Alpamayo: "python /workspace/web/backend/edgellm\_server.py"<br/><br/>nim\_entrypoint     — Path to the NIM entrypoint script in the base image. Newer NIM<br/>                     versions omit nvidia\_entrypoint.sh; launch.sh falls back to<br/>                     nim\_cmd directly when the path does not exist.<br/><br/>caddy\_backend\_port — Port Caddy routes requests to (the NIM's external HTTP API port).<br/>                     Null (default) = auto-detected at container startup from the NIM<br/>                     image's own NIM\_HTTP\_API\_PORT env var (standard NIMs set this to<br/>                     8000). Only set this for custom NIMs that serve on a different<br/>                     port (e.g. Alpamayo uses 8001).<br/>                     Named caddy\_backend\_port — not nim\_backend\_port — to avoid<br/>                     colliding with the NIM image's own NIM\_BACKEND\_PORT env var,<br/>                     which vLLM-based NIMs use to configure vLLM's internal listen port.<br/><br/>cuda\_driver\_label  — CUDA version string baked into the shim image as Docker label:<br/>                       LABEL com.amazonaws.sagemaker.inference.cuda.verified\_versions<br/>                     SageMaker reads this to auto-select an inference AMI with a<br/>                     matching CUDA driver. Null (default) = SageMaker picks the default.<br/>                     See DEVELOPER\_REFERENCE.md — known AMI bug history. | <pre>object({<br/>    nim_cmd            = optional(string, "/opt/nim/start_server.sh")<br/>    nim_entrypoint     = optional(string, "/opt/nvidia/nvidia_entrypoint.sh")<br/>    caddy_backend_port = optional(number, null)<br/>    cuda_driver_label  = optional(string, null)<br/>  })</pre> | `{}` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags applied to all resources. Merged with a resource-specific Name tag per resource. | `map(string)` | <pre>{<br/>  "IaC": "Terraform",<br/>  "ModuleBy": "NVIDIA",<br/>  "ModuleName": "terraform-aws-nim",<br/>  "ModuleSource": "https://github.com/NVIDIA/nvidia-aws-samples/tree/main/inference/terraform-aws-nim",<br/>  "RootModuleName": "-"<br/>}</pre> | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_async_output_prefixes"></a> [async\_output\_prefixes](#output\_async\_output\_prefixes) | Map of endpoint key to S3 URI prefix where SageMaker writes InvokeEndpointAsync responses. Only includes async endpoints. Empty when no async endpoints exist. |
| <a name="output_ecr_base_image_uris"></a> [ecr\_base\_image\_uris](#output\_ecr\_base\_image\_uris) | Map of endpoint key to ECR URI for the base NIM image ({image-name}-{version}-base tag). Used by EKS directly. Endpoints sharing the same source\_image\_uri point to the same URI. Only includes NIM endpoints (source\_image\_uri set). Empty when no NIM endpoints exist. |
| <a name="output_ecr_repository_url"></a> [ecr\_repository\_url](#output\_ecr\_repository\_url) | ECR repository base URL (no tag). Tags follow the pattern {image-name}-{version}-base and {image-name}-{version}-shim per unique source image. |
| <a name="output_ecr_shim_image_uris"></a> [ecr\_shim\_image\_uris](#output\_ecr\_shim\_image\_uris) | Map of endpoint key to ECR URI for the SageMaker shim image ({image-name}-{version}-shim tag). This is the image SageMaker runs. Endpoints sharing the same source\_image\_uri point to the same URI. Only includes NIM endpoints (source\_image\_uri set). Empty when no NIM endpoints exist. |
| <a name="output_eks_cluster_endpoints"></a> [eks\_cluster\_endpoints](#output\_eks\_cluster\_endpoints) | Map of eks\_clusters key to EKS API server endpoint. Empty when eks\_clusters = {}. |
| <a name="output_eks_cluster_names"></a> [eks\_cluster\_names](#output\_eks\_cluster\_names) | Map of eks\_clusters key to EKS cluster name. Empty when eks\_clusters = {}. |
| <a name="output_eks_namespaces"></a> [eks\_namespaces](#output\_eks\_namespaces) | Map of eks\_deployments key to Kubernetes namespace. Keys are suffixed with -nim or -ow to distinguish deployment types when the same key appears in both maps. Empty when eks\_deployments = {}. |
| <a name="output_eks_nim_irsa_role_arns"></a> [eks\_nim\_irsa\_role\_arns](#output\_eks\_nim\_irsa\_role\_arns) | Map of eks\_clusters key to NIM IRSA role ARN. Annotated on nim-sa service accounts. Empty when eks\_clusters = {}. |
| <a name="output_eks_release_names"></a> [eks\_release\_names](#output\_eks\_release\_names) | Map of eks\_deployments key to Helm release name. Keys are suffixed with -nim or -ow to distinguish deployment types when the same key appears in both maps. Use with kubectl -n <namespace> to inspect deployments. Empty when eks\_deployments = {}. |
| <a name="output_endpoint_names"></a> [endpoint\_names](#output\_endpoint\_names) | Map of endpoint key to SageMaker endpoint name. Keys are suffixed with -nim or -ow to distinguish deployment types when the same key appears in both maps. |
| <a name="output_model_profile_cache_uris"></a> [model\_profile\_cache\_uris](#output\_model\_profile\_cache\_uris) | Map of endpoint key to S3 URI for the pre-cached NGC model profile (nim-cache/{image-name}-{version}/{instance-type}/). Endpoints sharing the same source\_image\_uri and instance\_type point to the same URI. Null per-entry when enable\_model\_profile\_cache = false. Empty when sagemaker\_endpoints = {}. |
| <a name="output_model_weights_s3_uris"></a> [model\_weights\_s3\_uris](#output\_model\_weights\_s3\_uris) | Map of endpoint key to S3 URI where open-weight model files were downloaded. Only includes open-weight endpoints (model\_id set). Empty when no open-weight endpoints exist. |
| <a name="output_s3_build_bucket"></a> [s3\_build\_bucket](#output\_s3\_build\_bucket) | S3 bucket for CodeBuild source (shim-source.zip). |
| <a name="output_s3_cache_bucket"></a> [s3\_cache\_bucket](#output\_s3\_cache\_bucket) | S3 bucket for NGC model profile cache. Cache prefixes: nim-cache/{image-name}-{version}/{instance-type}/ per unique (image, instance) combo. Null when no endpoints have enable\_model\_profile\_cache = true. |
| <a name="output_s3_model_assets_bucket"></a> [s3\_model\_assets\_bucket](#output\_s3\_model\_assets\_bucket) | S3 bucket holding downloaded open-weight model files. Null when no open-weight endpoints exist. |
| <a name="output_s3_output_bucket"></a> [s3\_output\_bucket](#output\_s3\_output\_bucket) | S3 bucket for SageMaker async inference response payloads. |
| <a name="output_sagemaker_endpoint_arns"></a> [sagemaker\_endpoint\_arns](#output\_sagemaker\_endpoint\_arns) | Map of endpoint key to SageMaker endpoint ARN. Keys are suffixed with -nim or -ow. Empty when sagemaker\_endpoints = {}. |
| <a name="output_sagemaker_execution_role_arn"></a> [sagemaker\_execution\_role\_arn](#output\_sagemaker\_execution\_role\_arn) | ARN of the IAM role attached to SageMaker endpoints. |
<!-- END_TF_DOCS -->
