# example: eks/additional-scripts

Demonstrates `additional_scripts` on EKS — run custom shell scripts as Kubernetes init
containers before the NIM pod starts. Both a local file and an existing S3 object are shown.

| Deployment    | Path | Script execution point                            |
| ------------- | ---- | ------------------------------------------------- |
| `llama-nemotron-nano-8b` | NIM  | Init containers before the NIM Helm pod starts    |

The same `additional_scripts` mechanism works for the open-weight (vLLM) path — see
`examples/eks/open-weight/` for that pattern. This example uses a single deployment on a
`g6e.xlarge` (1× L40S) node. To run NIM + open-weight on the same cluster, bump the
cluster's `instance_type` to a multi-GPU size like `g6e.12xlarge` (4× L40S) so the two
deployments don't contend for a single GPU.

---

## How additional_scripts work on EKS

Scripts are listed in order under `additional_scripts`. Each entry has a `source` field:

- **Local file** — uploaded automatically to the module's S3 bucket at apply time (keyed by
  content hash — re-uploading an unchanged file is a no-op). No manual zip or upload needed.
- **S3 URI** — passed through directly. The S3 object must already exist before `terraform apply`.

Each script becomes a separate Kubernetes init container (`amazon/aws-cli:latest`) that
downloads and executes the script. Init containers run in list order and must exit 0 before
the main container starts. IRSA provides S3 access automatically — no IAM changes needed for
scripts stored in the module's own bucket. For scripts in an external bucket, add an inline
policy to the NIM IRSA role.

---

## Usage

The example ships with two `additional_scripts` entries in [main.tf](main.tf):

- A local file at `${path.module}/../../scripts/local-test.sh` — uploaded to the module's S3
  bucket automatically by Terraform.
- An s3:// URI (`var.remote_script_s3_uri`) pointing at a pre-existing S3 object — Terraform
  does NOT upload this; the init container downloads it from S3 at startup.

### One-time setup

Upload `remote-test.sh` to your own bucket:

```bash
aws s3 cp ../../scripts/remote-test.sh s3://<your-bucket>/remote-test.sh
```

Then create a `terraform.tfvars` (gitignored — never committed) with:

```hcl
ngc_secret_name      = "your-ngc-secret-name"
remote_script_s3_uri = "s3://<your-bucket>/remote-test.sh"
```

Then:

```bash
terraform init
terraform plan
terraform apply
```

Supply `ngc_secret_name` via `-var`, `.tfvars`, or accept the default in [terraform.tfvars](terraform.tfvars).
See [variables.tf](variables.tf).

## Apply timeline

**Total wall-clock time: ~20 min** (first apply). Local scripts are uploaded to S3 during
`terraform apply` before any CodeBuild runs. VPC/EKS provisioning, base-sync, and
cluster-setup all run concurrently.

| Concurrent work | Duration |
| -------------------------------------------------------------------- | ---------- |
| S3 upload of local scripts | seconds |
| VPC + EKS cluster provisioning | ~15-20 min |
| CodeBuild: base-sync + cluster-setup (fire simultaneously) | ~5-10 min |
| CodeBuild: deploy-nim (polls for NodePool, then deploys with init containers) | completes within the 20 min window |

## Verifying additional_scripts ran

The init containers are the proof. Once the pod reaches `Running`, you can confirm each
script executed by reading its init container logs:

```bash
NAMESPACE=$(terraform output -json eks_namespaces | jq -r '."llama-nemotron-nano-8b-nim"')
POD=$(kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/name=nim-llm -o jsonpath='{.items[0].metadata.name}')

# One log per init container — names follow additional-script-{index}
kubectl -n "$NAMESPACE" logs "$POD" -c additional-script-0
kubectl -n "$NAMESPACE" logs "$POD" -c additional-script-1
```

Each script's stdout/stderr is captured by Kubernetes. If a script had failed (non-zero
exit), the pod would have been stuck in `Init:0/N` or `Init:1/N` — reaching `Running` at
all means every init container in order exited 0.

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

# Health check
curl -s "http://$LB:8000/v1/health/ready" && echo

# Inference (8B model — answers may be small-model-quality; this is a wiring smoke test)
curl -s "http://$LB:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/llama-3.1-nemotron-nano-8b-v1","messages":[{"role":"user","content":"Who is Jensen Huang in one sentence?"}],"max_tokens":64}' | jq .
```

NLB DNS can take 1-2 minutes to propagate after the Service goes Ready. If you hit a DNS
error first, wait a minute and retry.

## Teardown

```bash
terraform destroy
```

## Outputs

| Name                       | Description                                          |
| -------------------------- | ---------------------------------------------------- |
| `eks_cluster_names`        | Map of cluster key → EKS cluster name                |
| `eks_release_names`        | Map of deployment key → Helm release / deployment name |
| `eks_namespaces`           | Map of deployment key → Kubernetes namespace         |
| `model_profile_cache_uris` | Map of deployment key → S3 URI of pre-cached profile |
