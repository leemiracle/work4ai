# example: sagemaker/nim

Deploys a standard NGC NIM as a SageMaker realtime inference endpoint with NGC model
profile pre-deployment caching. Configured for `llama-3.1-nemotron-nano-8b-v1` on `ml.g6e.xlarge` ([1× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/), 48 GB VRAM).

Change `source_image_uri` and `instance_type` in [main.tf](main.tf) to target a
different model or instance.

---

## Usage

```bash
terraform init
terraform plan
terraform apply
```

Supply `ngc_secret_name` (the name of your NGC API key secret in Secrets Manager) when prompted, via `-var`, or in a `.tfvars` file. See [variables.tf](variables.tf).

## Apply timeline

**Total wall-clock time: ~15-20 min** (first apply). All three CodeBuild actions fire
simultaneously and SageMaker endpoint provisioning begins as soon as the shim image is ready.

| Concurrent work | Duration |
| ----------------------------------------------- | --------- |
| CodeBuild: base-sync + shim + model-profile-cache | ~5-15 min (all fire simultaneously) |
| SageMaker endpoint InService | completes within the 15-20 min window |

Subsequent applies: model-profile-cache exits immediately (S3 already warm).

> **Cost note:** Both ECR images (~10 GB/shim) and S3 model profile caches (tens of GB)
> accumulate orphaned objects when you change NIM versions, instance types, or endpoint keys.
> Set `ecr_image_retention_days = 90` and `model_profile_cache_retention_days = 90` to
> auto-expire stale objects and avoid unbounded storage costs across many models.

## Invoking the endpoint

The `model` field in the request body is the NIM model path without the version tag
(e.g. `"nvidia/llama-3.1-nemotron-nano-8b-v1"`, not `"nvidia/llama-3.1-nemotron-nano-8b-v1:latest"`).

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

## Troubleshooting

**`ResourceLimitExceeded: ml.g6e.12xlarge for endpoint usage is 0`**
Service quota is zero for this instance type in this region. Request an increase in the
[Service Quotas console](https://console.aws.amazon.com/servicequotas/) under **Amazon SageMaker**.
ODCR cannot help — quota must exist before capacity can be reserved.
Safe to re-apply once the quota is granted; no `-replace` needed.

**`Cannot create already existing endpoint` on re-apply**
`CreateEndpoint` returns 200 immediately and AWS registers the endpoint name at that point. If
the endpoint later transitions to `Failed` for any reason (no GPU capacity, container crash,
expired NGC credentials), Terraform calls `DeleteEndpoint`, but the provider's delete waiter
exits before AWS finishes the async cleanup. The name remains held. The next `terraform apply`
tries to call `CreateEndpoint` with the same name again: collision. This is a known Terraform
AWS provider issue ([#40080](https://github.com/hashicorp/terraform-provider-aws/issues/40080),
[#40048](https://github.com/hashicorp/terraform-provider-aws/issues/40048)).

`-replace` is a standard Terraform flag (available since v0.15.2) that forces a resource to be
destroyed and recreated in the same apply. Replacing `random_id.endpoint_suffix` generates a new
hex suffix → new endpoint name. Terraform destroys the Failed endpoint and creates a fresh one
with a different name, bypassing the held-name collision.

```bash
terraform apply -replace='module.terraform-aws-nim.random_id.endpoint_suffix["llama-nemotron-nano-8b"]'
```

Clean up the old Failed endpoint afterward:

```bash
aws sagemaker delete-endpoint --endpoint-name <old-endpoint-name> --region <region>
```

## Teardown

```bash
terraform destroy
```

## Outputs

| Name                    | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| `endpoint_names`          | Map of endpoint key → SageMaker endpoint name         |
| `sagemaker_endpoint_arns` | Map of endpoint key → SageMaker endpoint ARN          |
| `async_output_prefixes`   | Map of endpoint key → S3 URI prefix for async results |
| `model_profile_cache_uris`| Map of endpoint key → S3 URI of pre-cached NGC profile|
