# example: sagemaker/open-weight

Deploys open-weight models as SageMaker realtime inference endpoints using vLLM.
Weights are downloaded from HuggingFace or NGC during `terraform apply`, staged in S3,
and synced into the container at startup.

The active endpoint is `nvidia/Llama-3.1-Nemotron-Nano-8B-v1` on `ml.g6e.xlarge` ([1× NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/), 48 GB VRAM) —
single-model, no tensor parallelism required for 8B parameters. A commented `nemotron-30b` entry
demonstrates how to configure tensor parallelism for models that exceed a single GPU's VRAM.

Change `model_id`, `model_source`, and `instance_type` in [main.tf](main.tf) to target a
different model or instance. See the commented examples for a 30B multi-GPU deployment, Qwen,
and NGC model paths.

> **Instance recommendation:** Use `ml.g6e` instances ([NVIDIA L40S](https://aws.amazon.com/ec2/instance-types/g6e/)) or newer. Older generations such
> as `ml.g5` ([NVIDIA A10G](https://aws.amazon.com/ec2/instance-types/g5/)) ship with CUDA driver versions that may be incompatible with recent
> `vllm/vllm-openai` releases, causing silent container startup failures with no CloudWatch logs.
> If you must use `ml.g5`, pin `vllm/vllm-openai` to a version that matches your instance's
> driver — see `locals.tf` in the module root.

---

## Usage

```bash
terraform init
terraform plan
terraform apply
```

The `hf_secret_name` variable is optional and only needed for gated HuggingFace models.
`nvidia/Llama-3.1-Nemotron-Nano-8B-v1` is publicly available under the
[NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/)
— no HF account or token required. Supply `hf_secret_name` via `-var` or `.tfvars` only
if you swap in a gated model. See [variables.tf](variables.tf).

## Apply timeline

**Total wall-clock time: ~15-20 min** (first apply). Weight-fetch and shim build fire
simultaneously and SageMaker endpoint provisioning begins as soon as the shim image is ready.

| Concurrent work | Duration (first apply) |
| ------------------------------------------ | ---------------------- |
| CodeBuild: weight-fetch + shim build | ~5-10 min (fire simultaneously) |
| SageMaker endpoint InService | completes within the 15-20 min window |

Subsequent applies: weight-fetch exits immediately (S3 `WEIGHTS_COMPLETE` marker present).

> **Cost note:** Model weights (tens to hundreds of GB) accumulate in S3 across model
> versions and revisions. Set `model_assets_retention_days` to auto-expire stale weights
> and avoid unbounded storage costs as you iterate on models.

## vLLM Recipe auto-configuration

Open-weight deployments can optionally use [vLLM Recipes](https://recipes.vllm.ai) to
automatically select optimized `vllm serve` flags for the target model and GPU — instead
of requiring you to research and specify `extra_args` manually.

vLLM Recipes is a community-maintained database of validated deployment configurations,
published as a JSON API at `recipes.vllm.ai/<hf_org>/<hf_repo>.json`. Each recipe
specifies the flags, environment variables, and VRAM requirements that work well for a
given model on a given GPU family.

This is conceptually similar to the NIM model profile cache in the `sagemaker/nim`
example: both solve the same "what settings should I use for this model on this hardware"
problem, but for different deployment paths. NIMs carry their own profile metadata from
NGC; open-weight models rely on the community-driven recipes database.

To enable it:

```hcl
llama-nemotron-nano-8b = {
  model_id           = "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"
  model_source       = "huggingface"
  instance_type      = "ml.g5.2xlarge"
  enable_vllm_recipe = true
  vllm_precision     = "default"   # "default" (bf16) or "fp8"
}
```

**Not all models have a recipe.** The database currently covers ~64 models across 25+
providers. If your `model_id` does not have a recipe, the module warns during the
weight-fetch build and falls back to vLLM's own defaults (or your explicit `extra_args`
if set). The endpoint still deploys — recipe fetch is a best-effort optimization, not a
hard dependency.

**`extra_args` always wins.** Any flag you set explicitly in `extra_args` overrides the
corresponding recipe value. Use this to tune individual settings while still getting
recipe defaults for everything else.

## Invoking the endpoint

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

## Troubleshooting

### `Cannot create already existing endpoint`

**Error:** `ValidationException: Cannot create already existing endpoint "arn:aws:sagemaker:..."`.

**What happened:** `CreateEndpoint` returns 200 immediately and AWS registers the endpoint
name at that point. If the endpoint later transitions to `Failed` for any reason
(`InsufficientInstanceCapacity`, container crash, wrong `tensor-parallel-size`, or anything
else), Terraform calls `DeleteEndpoint`, but the provider's delete waiter exits before AWS
finishes the async cleanup. The name remains held. The next `terraform apply` tries to call
`CreateEndpoint` with the same name again: collision. This is a known Terraform AWS provider
issue ([#40080](https://github.com/hashicorp/terraform-provider-aws/issues/40080),
[#40048](https://github.com/hashicorp/terraform-provider-aws/issues/40048)).

This does **not** happen to healthy endpoints receiving a config update; those go through
`UpdateEndpoint` (blue-green, in-place) which does not touch the endpoint name.

`-replace` is a standard Terraform flag (available since v0.15.2) that forces a resource to
be destroyed and recreated in the same apply. Replacing `random_id.endpoint_suffix` generates
a new hex suffix → new endpoint name. Terraform destroys the Failed endpoint and creates a
fresh one with a different name, bypassing the held-name collision.

**Fix:**

```bash
terraform apply -replace='module.terraform-aws-nim.random_id.endpoint_suffix["<key>"]'
```

Replace `<key>` with the map key of the failing endpoint (e.g. `llama-nemotron-nano-8b`). Clean up the
old Failed endpoint afterward:

```bash
aws sagemaker delete-endpoint --endpoint-name <old-endpoint-name> --region <region>
```

**Why open-weight deployments hit this more often:** NIM containers auto-select tensor
parallelism and GPU configuration from NGC model profiles. Open-weight deployments require
you to set `tensor-parallel-size` and other flags correctly. A misconfigured container fails
after `CreateEndpoint` returns (not before), which is exactly the condition that triggers this
race. NIM failures tend to be infrastructure-level (quota, capacity, credentials) rather than
misconfigured container args.

**How to avoid it:**

- Check the model card on HuggingFace for VRAM requirements before choosing an instance type.
- For models larger than a single GPU's VRAM, set `tensor-parallel-size` in `extra_args`
  equal to the GPU count for the instance (e.g. `"4"` for `ml.g6e.12xlarge` with [4× L40S](https://aws.amazon.com/ec2/instance-types/g6e/),
  or `"4"` for `ml.g5.12xlarge` with [4× A10G](https://aws.amazon.com/ec2/instance-types/g5/)).
- Enable `enable_vllm_recipe = true` — community-validated recipes include tensor parallelism
  for supported models and are a good starting point if you are unsure.

---

## Teardown

```bash
terraform destroy
```

## Outputs

| Name                      | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| `endpoint_names`          | Map of endpoint key → SageMaker endpoint name        |
| `sagemaker_endpoint_arns` | Map of endpoint key → SageMaker endpoint ARN         |
| `model_weights_s3_uris`   | Map of endpoint key → S3 URI of downloaded weights   |
| `s3_model_assets_bucket`  | S3 bucket holding downloaded model weights           |
