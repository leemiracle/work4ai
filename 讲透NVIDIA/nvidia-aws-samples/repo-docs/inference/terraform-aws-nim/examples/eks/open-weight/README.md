# example: eks/open-weight

Deploys raw HuggingFace model weights onto an EKS Auto Mode cluster using vLLM. No NGC
NIM container or Helm chart involved — an init container syncs weights from S3 and the main
container runs `vllm/vllm-openai` directly.

Configured for `nvidia/Llama-3.1-Nemotron-Nano-8B-v1` on `g6e.xlarge` ([1× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/), 48 GB VRAM). This model is
public on HuggingFace (NVIDIA Open Model License) — no HuggingFace token required.

Change `model_id`, `model_source`, and `instance_type` in [main.tf](main.tf) to target a
different model.

---

## Usage

```bash
terraform init
terraform plan
terraform apply
```

No credentials variable needed for this public model. Set a `region` var or rely on the
AWS provider default. See [variables.tf](variables.tf).

## Apply timeline

**Total wall-clock time: ~17 min** (first apply). VPC/EKS provisioning, cluster-setup, and
weight-fetch all run concurrently. The `deploy-nim` buildspec polls for the GPU NodePool
before applying the manifest, so it starts immediately and waits inline.

| Concurrent work | Duration |
| --------------------------------------------------- | ---------- |
| VPC + EKS cluster provisioning | ~15-20 min |
| CodeBuild: cluster-setup + weight-fetch (fire simultaneously) | ~5-10 min |
| CodeBuild: deploy-nim (polls for NodePool, then kubectl apply + rollout) | completes within the 17 min window |

## Invoking the endpoint

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

## Trade-offs vs NIM path

| | NIM path | Open-weight path |
|---|---|---|
| Container | NGC pre-optimized | `vllm/vllm-openai:latest` |
| GPU profile selection | Automatic | Manual (`tensor-parallel-size`, etc.) |
| Cold start | Faster (profile cache) | Slower (full S3 sync each restart) |
| NGC license required | Yes | No (public HF models) |

## Teardown

```bash
terraform destroy
```

## Outputs

| Name                    | Description                                          |
| ----------------------- | ---------------------------------------------------- |
| `eks_cluster_names`     | Map of cluster key → EKS cluster name               |
| `eks_release_names`     | Map of deployment key → Kubernetes deployment name  |
| `eks_namespaces`        | Map of deployment key → Kubernetes namespace        |
| `model_weights_s3_uris` | Map of model slug → S3 URI where weights are stored |
| `s3_model_assets_bucket`| S3 bucket holding downloaded model weights          |
