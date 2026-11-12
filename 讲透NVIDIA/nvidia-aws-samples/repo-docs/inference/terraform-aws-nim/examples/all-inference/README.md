# example: all-inference

Deploys **NVIDIA Llama-3.1-Nemotron-Nano-8B-v1** across all four inference paths in a single `terraform apply`:

| Output key | Platform | Path | Source | Instance |
|------------|----------|------|--------|----------|
| `llama-nemotron-nano-8b-nim` | SageMaker | NIM | NGC container (`nvcr.io`) | `ml.g6e.12xlarge` ([4× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/)) |
| `llama-nemotron-nano-8b-ow` | SageMaker | Open-weight (vLLM) | HuggingFace weights | `ml.g6e.12xlarge` ([4× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/)) |
| `llama-nemotron-nano-8b-nim` | EKS | NIM via Helm | NGC container (`nvcr.io`) | `g6e.12xlarge` ([4× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/)) |
| `llama-nemotron-nano-8b-ow` | EKS | Open-weight (vLLM) via kubectl | HuggingFace weights | `g6e.12xlarge` ([4× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/)) |

The NIM paths use NGC's pre-optimized container with automatic GPU profile selection.
The open-weight paths download raw HuggingFace weights to S3 and serve them via vLLM.
SageMaker and EKS open-weight paths share the same S3 weight download — one CodeBuild
run, two consumers. For supported models, `enable_vllm_recipe = true` fetches optimized
`vllm serve` flags from [recipes.vllm.ai](https://recipes.vllm.ai) and applies them at
container startup — no manual tuning required.

> **EKS namespace separation:** When NIM and open-weight deployments share the same EKS
> cluster, they must use different Kubernetes namespaces. Both default to the `eks_deployments`
> map key as the namespace name (e.g. `llama-nemotron-nano-8b`), which would collide when both NIM and
> open-weight use the same key on the same cluster. This example sets `namespace = "llama-nemotron-nano-8b-ow"`
> on the open-weight deployment explicitly. Without it, `terraform destroy` can leave
> an NLB dangling (the namespace deletion swallows the other deployment's Service before
> the LB controller can clean up its NLB), causing VPC destroy to fail with
> `DependencyViolation`. This only applies when two deployments share the same cluster
> and the same key name — separate clusters need no special handling.

---

## Prerequisites

**NGC API key** — required for the NIM paths (pulls from `nvcr.io`). Store it as a
plaintext secret in AWS Secrets Manager and set `ngc_secret_name` to its name.

**No HuggingFace token needed.** `nvidia/Llama-3.1-Nemotron-Nano-8B-v1` is publicly
available under the [NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/).

**Instance quota** — four endpoints deploy simultaneously:
- Two `ml.g6e.12xlarge` SageMaker endpoint instances
- Two `g6e.12xlarge` EKS nodes (via EKS Auto Mode NodePool)

Request quota increases in the [Service Quotas console](https://console.aws.amazon.com/servicequotas/)
under **Amazon SageMaker** and **Amazon EC2** if needed.

---

## Usage

```bash
terraform init
terraform plan
terraform apply
```

Supply `ngc_secret_name` via `-var`, `.tfvars`, or accept the default if your secret name
matches. See [variables.tf](variables.tf).

## Apply timeline

**Total wall-clock time: ~20-25 min** (first apply). All eight CodeBuild actions and
SageMaker endpoint provisioning run in parallel. The table below shows what's happening
concurrently — these are not sequential stages.

| Concurrent work | Duration |
|-----------------|----------|
| VPC + EKS cluster provisioning | ~15-20 min |
| CodeBuild: base-sync + shim + model-profile-cache + weight-fetch + cluster-setup | ~5-15 min (all fire simultaneously) |
| CodeBuild: EKS NIM deploy + EKS open-weight deploy (poll for cluster-setup, then deploy) | completes within the 20-25 min window |
| SageMaker NIM + open-weight endpoints InService | completes within the 20-25 min window |

Subsequent applies: model-profile-cache and weight-fetch exit immediately (S3 markers present).

> **Cost note:** ECR images, NIM profile caches, and open-weight S3 downloads accumulate
> orphaned objects as you change model versions or instance types. Set
> `ecr_image_retention_days`, `model_profile_cache_retention_days`, and review S3 lifecycle
> rules to auto-expire stale objects.

---

## Invoking the endpoints

### SageMaker NIM endpoint

```bash
ENDPOINT=$(terraform output -json endpoint_names | jq -r '."llama-nemotron-nano-8b-nim"')
REGION=$(aws configure get region)

echo '{"model":"nvidia/llama-3.1-nemotron-nano-8b-v1","messages":[{"role":"user","content":"Who is Jensen Huang in one sentence?"}],"max_tokens":64}' > /tmp/request.json

aws sagemaker-runtime invoke-endpoint \
  --endpoint-name "$ENDPOINT" \
  --content-type application/json \
  --body fileb:///tmp/request.json \
  --region "$REGION" \
  /tmp/response.json

cat /tmp/response.json
```

### SageMaker open-weight endpoint

```bash
ENDPOINT=$(terraform output -json endpoint_names | jq -r '."llama-nemotron-nano-8b-ow"')
REGION=$(aws configure get region)

echo '{"model":"nvidia/Llama-3.1-Nemotron-Nano-8B-v1","messages":[{"role":"user","content":"Who is Jensen Huang in one sentence?"}],"max_tokens":64}' > /tmp/request.json

aws sagemaker-runtime invoke-endpoint \
  --endpoint-name "$ENDPOINT" \
  --content-type application/json \
  --body fileb:///tmp/request.json \
  --region "$REGION" \
  /tmp/response.json

cat /tmp/response.json
```

### EKS NIM endpoint

```bash
CLUSTER=$(terraform output -json eks_cluster_names | jq -r '."llama-nemotron-nano-8b"')
NAMESPACE=$(terraform output -json eks_namespaces | jq -r '."llama-nemotron-nano-8b-nim"')
RELEASE=$(terraform output -json eks_release_names | jq -r '."llama-nemotron-nano-8b-nim"')
REGION=$(aws configure get region)

aws eks update-kubeconfig --name "$CLUSTER" --region "$REGION"

LB=$(kubectl get svc -n "$NAMESPACE" \
  -l "app.kubernetes.io/instance=$RELEASE" \
  -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}')

curl -s http://$LB:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/llama-3.1-nemotron-nano-8b-v1","messages":[{"role":"user","content":"Who is Jensen Huang in one sentence?"}],"max_tokens":64}' | jq .
```

### EKS open-weight endpoint

```bash
CLUSTER=$(terraform output -json eks_cluster_names | jq -r '."llama-nemotron-nano-8b"')
NAMESPACE=$(terraform output -json eks_namespaces | jq -r '."llama-nemotron-nano-8b-ow"')
DEPLOYMENT=$(terraform output -json eks_release_names | jq -r '."llama-nemotron-nano-8b-ow"')
REGION=$(aws configure get region)

aws eks update-kubeconfig --name "$CLUSTER" --region "$REGION"

LB=$(kubectl get svc -n "$NAMESPACE" "$DEPLOYMENT-svc" \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

curl -s http://$LB:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/Llama-3.1-Nemotron-Nano-8B-v1","messages":[{"role":"user","content":"Who is Jensen Huang in one sentence?"}],"max_tokens":64}' | jq .
```

---

## Teardown

```bash
terraform destroy
```

---

## Outputs

| Name | Description |
|------|-------------|
| `endpoint_names` | Map of endpoint key → SageMaker endpoint name |
| `sagemaker_endpoint_arns` | Map of endpoint key → SageMaker endpoint ARN |
| `model_profile_cache_uris` | S3 URI for the pre-cached NIM model profile (`llama-nemotron-nano-8b`); null for open-weight |
| `model_weights_s3_uris` | S3 URI of downloaded HuggingFace weights (`llama-nemotron-nano-8b`); empty for NIM |
| `s3_model_assets_bucket` | S3 bucket holding open-weight model files |
| `eks_cluster_names` | Map of cluster key → EKS cluster name |
| `eks_release_names` | Map of deployment key → Helm release / deployment name |
| `eks_namespaces` | Map of deployment key → Kubernetes namespace |
