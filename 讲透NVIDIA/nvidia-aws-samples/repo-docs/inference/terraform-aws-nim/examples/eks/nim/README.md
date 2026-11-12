# example: eks/nim

Deploys a standard NGC NIM onto an EKS Auto Mode cluster via Helm. Configured for
`llama-3.1-nemotron-nano-8b-v1` on `g6e.xlarge` ([1× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/), 48 GB VRAM) with NGC model profile pre-caching.

Change `source_image_uri`, `instance_type`, and `helm_chart_version` in [main.tf](main.tf)
to target a different model or instance.

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
before Helm install, so it starts immediately and waits inline rather than sequencing at
the Terraform level (workaround for [hashicorp/terraform#37975](https://github.com/hashicorp/terraform/issues/37975)).

| Concurrent work | Duration |
| --------------------------------------------- | ---------- |
| VPC + EKS cluster provisioning | ~15-20 min |
| CodeBuild: base-sync + cluster-setup (fire simultaneously) | ~5-10 min |
| CodeBuild: deploy-nim (polls for NodePool, then Helm install) | completes within the 20 min window |

## Invoking the endpoint

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

## Teardown

```bash
terraform destroy
```

## Outputs

| Name                 | Description                                      |
| -------------------- | ------------------------------------------------ |
| `eks_cluster_names`       | Map of cluster key → EKS cluster name              |
| `eks_release_names`       | Map of deployment key → Helm release name          |
| `eks_namespaces`          | Map of deployment key → Kubernetes namespace       |
| `model_profile_cache_uris`| Map of deployment key → S3 URI of pre-cached profile|
