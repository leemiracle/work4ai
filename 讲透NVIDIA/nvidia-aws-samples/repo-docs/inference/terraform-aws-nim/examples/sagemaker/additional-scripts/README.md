# example: sagemaker/additional-scripts

Demonstrates `additional_scripts` on SageMaker — run custom shell scripts inside the
container before Caddy and the inference process start. Both a local file and an existing
S3 object are shown.

| Endpoint key  | Path | Script execution point                          |
| ------------- | ---- | ----------------------------------------------- |
| `llama-nemotron-nano-8b` | NIM  | Inside container, before Caddy + NIM start      |

The same `additional_scripts` mechanism works for the open-weight (vLLM) path — both
`sagemaker_endpoints.nim` and `sagemaker_endpoints.open_weight` route through the same
`shim/launch.sh` ADDITIONAL_SCRIPTS loop. See `examples/sagemaker/open-weight/` for the
open-weight pattern.

---

## How additional_scripts work on SageMaker

Scripts are listed in order under `additional_scripts`. Each entry has a `source` field:

- **Local file** — uploaded automatically to the module's S3 bucket at apply time (keyed by
  content hash — re-uploading an unchanged file is a no-op). No manual zip or upload needed.
- **S3 URI** — passed through directly. The S3 object must already exist before `terraform apply`.

At container startup, `launch.sh` downloads and executes each script in list order before
starting Caddy and the inference process. All scripts run as the container's default user;
the container IAM role must have `s3:GetObject` on any external script buckets.

---

## Usage

The example ships with two `additional_scripts` entries in [main.tf](main.tf):

- A local file at `${path.module}/../../scripts/local-test.sh` — uploaded to the module's S3
  bucket automatically by Terraform.
- An s3:// URI (`var.remote_script_s3_uri`) pointing at a pre-existing S3 object — Terraform
  does NOT upload this; the container downloads it from S3 at startup.

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

**Total wall-clock time: ~15-20 min** (first apply). Local scripts are uploaded to S3 during
`terraform apply` before any CodeBuild runs. All CodeBuild actions fire simultaneously.

| Concurrent work | Duration |
| ----------------------------------------------- | --------- |
| S3 upload of local scripts | seconds |
| CodeBuild: base-sync + shim + model-profile-cache | ~5-15 min (all fire simultaneously) |
| SageMaker endpoint InService | completes within the 15-20 min window |

## Verifying additional_scripts ran

The endpoint reaching `InService` proves `launch.sh` completed successfully — including the
ADDITIONAL_SCRIPTS loop. If any script had exited non-zero, the container would have failed
to start and SageMaker would report the endpoint as `Failed`. To see each script's
stdout/stderr in CloudWatch:

```bash
ENDPOINT=$(terraform output -json endpoint_names | jq -r '."llama-nemotron-nano-8b-nim"')
REGION=$(aws configure get region)

aws logs filter-log-events --region "$REGION" \
  --log-group-name "/aws/sagemaker/Endpoints/$ENDPOINT" \
  --filter-pattern '"Running additional script"' \
  --query 'events[].message' --output text
```

Expected output is one line per script, in execution order:

```
=== [HH:MM:SS] Running additional script [0]: s3://<codebuild-bucket>/additional-scripts/<md5>/local-test.sh ===
=== [HH:MM:SS] Running additional script [1]: s3://<your-bucket>/remote-test.sh ===
```

If you don't see these lines but the endpoint is `InService`, check that `ADDITIONAL_SCRIPTS`
was actually injected on the SageMaker Model — `aws sagemaker describe-model` and look for it
in the primary container environment variables.

## Invoking the endpoint

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

cat /tmp/response.json | jq .
```

## Teardown

```bash
terraform destroy
```

## Outputs

| Name                       | Description                                        |
| -------------------------- | -------------------------------------------------- |
| `endpoint_names`           | Map of endpoint key → SageMaker endpoint name      |
| `sagemaker_endpoint_arns`  | Map of endpoint key → SageMaker endpoint ARN       |
| `model_profile_cache_uris` | Map of endpoint key → S3 URI of pre-cached profile |
