# modules/eks-app

Deploys a NIM or open-weight model onto an existing EKS cluster via a CodeBuild action trigger:

- **NIM path**: Helm install from NGC registry (`nvidia/nim-llm` chart). Optional init container syncs NGC model profile cache from S3 at pod startup.
- **Open-weight path**: raw `kubectl apply` of a Deployment + Service. Init container syncs HuggingFace/NGC weights from S3; main container runs `vllm serve`.
- **Additional scripts**: optional list of shell scripts (`additional_scripts`) that run as init containers before the NIM or vLLM container starts. Local files are uploaded to S3 automatically; S3 URIs are passed through directly.

Both paths provision a Kubernetes Service of type `LoadBalancer` (NLB via EKS Load Balancer Controller).
A `local-exec` destroy provisioner runs `helm uninstall` / `kubectl delete` before the cluster tears down,
ensuring the NLB is removed before VPC deletion.

Called internally by the `terraform-aws-nim` module root. Not intended for direct use.

---

<!-- markdownlint-disable -->
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.14 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 6.0 |
| <a name="requirement_time"></a> [time](#requirement\_time) | >= 0.9 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 6.0 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |
| <a name="provider_time"></a> [time](#provider\_time) | >= 0.9 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [aws_codebuild_project.nim_deploy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_project) | resource |
| [aws_eks_access_entry.codebuild_deploy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_access_entry) | resource |
| [aws_eks_access_policy_association.codebuild_deploy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_access_policy_association) | resource |
| [aws_iam_role.codebuild_deploy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.codebuild_deploy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [terraform_data.deploy_trigger](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.helm_cleanup](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [time_sleep.codebuild_deploy_iam_propagation](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |
| [aws_iam_policy_document.codebuild_deploy_assume](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.codebuild_deploy_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_buildspec_s3_arn"></a> [buildspec\_s3\_arn](#input\_buildspec\_s3\_arn) | S3 ARN of the deploy-nim buildspec (uploaded by the root module). Format: arn:aws:s3:::bucket/key. Sidesteps CodeBuild's 25,600-char inline buildspec limit. | `string` | n/a | yes |
| <a name="input_buildspec_s3_bucket"></a> [buildspec\_s3\_bucket](#input\_buildspec\_s3\_bucket) | S3 bucket name that holds the buildspec object. Used for the CodeBuild service role's s3:GetObject grant. | `string` | n/a | yes |
| <a name="input_buildspec_s3_key"></a> [buildspec\_s3\_key](#input\_buildspec\_s3\_key) | S3 key of the buildspec object within buildspec\_s3\_bucket. Used for the CodeBuild service role's s3:GetObject grant. | `string` | n/a | yes |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | EKS cluster name (output from modules/eks-infra). | `string` | n/a | yes |
| <a name="input_cluster_security_group_id"></a> [cluster\_security\_group\_id](#input\_cluster\_security\_group\_id) | EKS cluster security group ID (output from modules/eks-infra). Used for CodeBuild VPC placement. | `string` | n/a | yes |
| <a name="input_ecr_repository_url"></a> [ecr\_repository\_url](#input\_ecr\_repository\_url) | ECR repository URL (without tag). Image is pulled from ECR by EKS nodes via node IAM role. | `string` | n/a | yes |
| <a name="input_name_prefix"></a> [name\_prefix](#input\_name\_prefix) | Resource name prefix. Derived from root module local.name\_prefix + deployment key. | `string` | n/a | yes |
| <a name="input_nim_irsa_role_arn"></a> [nim\_irsa\_role\_arn](#input\_nim\_irsa\_role\_arn) | IRSA role ARN for NIM pods (output from modules/eks-infra). Annotated on the nim-sa service account. | `string` | n/a | yes |
| <a name="input_node_pool_name"></a> [node\_pool\_name](#input\_node\_pool\_name) | Name of the GPU NodePool to wait for before deploying. Must match the NodePool created by eks-infra. | `string` | n/a | yes |
| <a name="input_private_subnet_ids"></a> [private\_subnet\_ids](#input\_private\_subnet\_ids) | Private subnet IDs (from eks\_clusters config). Used for CodeBuild VPC placement. | `list(string)` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | AWS region. | `string` | n/a | yes |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC ID (from eks\_clusters config). Used for CodeBuild VPC placement. | `string` | n/a | yes |
| <a name="input_additional_scripts"></a> [additional\_scripts](#input\_additional\_scripts) | Resolved S3 URIs for additional scripts to run before the NIM/vLLM container starts. Scripts run in list order — as init containers for EKS. | `list(string)` | `[]` | no |
| <a name="input_autoscaling"></a> [autoscaling](#input\_autoscaling) | Fully-resolved KEDA ScaledObject config (metric and target\_value are non-null by the time this reaches eks-app — defaults were applied in the root module locals). | <pre>object({<br/>    min_replicas     = number<br/>    max_replicas     = number<br/>    metric           = string<br/>    target_value     = number<br/>    scale_down_delay = number<br/>  })</pre> | `null` | no |
| <a name="input_cache_bucket"></a> [cache\_bucket](#input\_cache\_bucket) | S3 bucket name for the model profile cache. Required when enable\_model\_profile\_cache = true. | `string` | `null` | no |
| <a name="input_cache_prefix"></a> [cache\_prefix](#input\_cache\_prefix) | S3 key prefix within cache\_bucket (e.g. nim-cache/llama-3.1-8b-instruct-1.8.3/g6e.12xlarge). | `string` | `null` | no |
| <a name="input_debug"></a> [debug](#input\_debug) | Enable verbose output in the deploy CodeBuild build. | `bool` | `false` | no |
| <a name="input_ecr_image_tag"></a> [ecr\_image\_tag](#input\_ecr\_image\_tag) | ECR image tag for the base NIM image (e.g. llama-3.1-8b-instruct-1.8.3-base). Null for open-weight deployments (uses DockerHub vLLM image directly). | `string` | `null` | no |
| <a name="input_enable_model_profile_cache"></a> [enable\_model\_profile\_cache](#input\_enable\_model\_profile\_cache) | When true, an init container syncs the pre-built model profile cache from S3 into the NIM pod at startup. | `bool` | `false` | no |
| <a name="input_extra_args_str"></a> [extra\_args\_str](#input\_extra\_args\_str) | Rendered vLLM CLI flags string (e.g. '--tensor-parallel-size 4 --dtype bfloat16'). Appended to vllm serve command. Null or empty = no extra flags. | `string` | `null` | no |
| <a name="input_force_rebuild"></a> [force\_rebuild](#input\_force\_rebuild) | Force the deploy CodeBuild to re-run on next apply regardless of input changes. | `bool` | `false` | no |
| <a name="input_gpu_count"></a> [gpu\_count](#input\_gpu\_count) | Number of GPUs to request per NIM pod replica. Increase for multi-GPU models (e.g. Mamba/SSM architectures that require more VRAM). | `number` | `1` | no |
| <a name="input_helm_chart_name"></a> [helm\_chart\_name](#input\_helm\_chart\_name) | NGC Helm chart name. Derived from nim\_type when null. Override for custom charts. | `string` | `null` | no |
| <a name="input_helm_chart_repo_url"></a> [helm\_chart\_repo\_url](#input\_helm\_chart\_repo\_url) | Base HTTPS URL for the NGC Helm chart repo. Derived from nim\_type when null. | `string` | `null` | no |
| <a name="input_helm_chart_s3_uri"></a> [helm\_chart\_s3\_uri](#input\_helm\_chart\_s3\_uri) | S3 URI of a custom Helm chart .tgz (e.g. s3://my-bucket/charts/my-nim-1.0.0.tgz). When set, skips NGC fetch entirely. Chart must be packaged with 'helm package' producing a .tgz. | `string` | `null` | no |
| <a name="input_helm_chart_version"></a> [helm\_chart\_version](#input\_helm\_chart\_version) | Helm chart version to pull from NGC. Null = latest available. | `string` | `null` | no |
| <a name="input_helm_values_override"></a> [helm\_values\_override](#input\_helm\_values\_override) | Raw YAML string merged after the generated nim-values.yaml. Applied with a second -f flag so any key here wins over the generated defaults. Use to supply chart-specific fields the module doesn't generate (e.g. Riva model configs, custom resource limits). | `string` | `null` | no |
| <a name="input_load_balancer_internal"></a> [load\_balancer\_internal](#input\_load\_balancer\_internal) | When true, annotates the NIM Service as internal-facing (VPC only). When false, creates an internet-facing NLB. | `bool` | `false` | no |
| <a name="input_model_assets_bucket"></a> [model\_assets\_bucket](#input\_model\_assets\_bucket) | S3 bucket name for open weight downloads. Required when model\_id is set. | `string` | `null` | no |
| <a name="input_model_id"></a> [model\_id](#input\_model\_id) | Open weight model ID (e.g. meta-llama/Llama-3.1-8B-Instruct). When set, deploys via raw kubectl Deployment+Service instead of Helm. Null = NIM path. | `string` | `null` | no |
| <a name="input_namespace"></a> [namespace](#input\_namespace) | Kubernetes namespace for the NIM deployment. | `string` | `"nim"` | no |
| <a name="input_ngc_api_key"></a> [ngc\_api\_key](#input\_ngc\_api\_key) | Resolved NGC API key. Required at pod startup for NIM license validation even when image is from ECR. | `string` | `null` | no |
| <a name="input_nim_type"></a> [nim\_type](#input\_nim\_type) | NIM category (used by the buildspec to select Helm values template + chart-specific quirks). One of: llm, vlm, embedding, reranking, speech, custom. See root-module variables.tf for the full per-type breakdown. | `string` | `"llm"` | no |
| <a name="input_port"></a> [port](#input\_port) | Service port the NIM exposes for inference. Resolved by the root module from `port` (override) or sensible defaults per protocol + nim\_type. The buildspec emits this as the Service `port` and `targetPort`. | `number` | `8000` | no |
| <a name="input_protocol"></a> [protocol](#input\_protocol) | Inference protocol: "http" (Helm deploy via the chart selected by nim\_type) or "grpc" (raw kubectl Deployment+Service; no Helm). | `string` | `"http"` | no |
| <a name="input_replicas"></a> [replicas](#input\_replicas) | Number of NIM pod replicas. When autoscaling is set, this is the initial replica count that KEDA takes over from. | `number` | `1` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags applied to all resources. | `map(string)` | `{}` | no |
| <a name="input_weights_s3_prefix"></a> [weights\_s3\_prefix](#input\_weights\_s3\_prefix) | S3 key prefix for the model weights within model\_assets\_bucket (e.g. open-weights/huggingface/meta-llama-.../main). | `string` | `null` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_namespace"></a> [namespace](#output\_namespace) | Kubernetes namespace the NIM deployment is installed into. |
| <a name="output_release_name"></a> [release\_name](#output\_release\_name) | Helm release name for the NIM deployment. |
<!-- END_TF_DOCS -->
<!-- markdownlint-enable -->
