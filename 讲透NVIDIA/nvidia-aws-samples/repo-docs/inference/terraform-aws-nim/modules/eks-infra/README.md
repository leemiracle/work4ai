# modules/eks-infra

Provisions an EKS Auto Mode cluster for NIM deployment:

- EKS Auto Mode cluster (AWS manages node lifecycle, AMIs, NVIDIA device plugin)
- GPU NodePool provisioned via a CodeBuild action trigger (`cluster-setup` buildspec)
- IAM: cluster role, NIM IRSA role (ECR pull + S3 read for model cache / weights)
- Security groups: cluster SG + additional ingress rules for allowed CIDR blocks
- OIDC provider for IRSA

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
| <a name="requirement_tls"></a> [tls](#requirement\_tls) | >= 4.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 6.0 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |
| <a name="provider_time"></a> [time](#provider\_time) | >= 0.9 |
| <a name="provider_tls"></a> [tls](#provider\_tls) | >= 4.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [aws_cloudwatch_log_group.eks_cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_codebuild_project.cluster_setup](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_project) | resource |
| [aws_eks_access_entry.additional](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_access_entry) | resource |
| [aws_eks_access_entry.codebuild_setup](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_access_entry) | resource |
| [aws_eks_access_policy_association.additional](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_access_policy_association) | resource |
| [aws_eks_access_policy_association.codebuild_setup](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_access_policy_association) | resource |
| [aws_eks_cluster.nim](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_cluster) | resource |
| [aws_iam_openid_connect_provider.eks](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_openid_connect_provider) | resource |
| [aws_iam_role.codebuild_setup](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.eks_cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.eks_node](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.nim_irsa](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.codebuild_setup](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.eks_cluster_deny_log_group_create](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.nim_irsa_s3](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.eks_block_storage_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_cluster_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_compute_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_load_balancing_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_networking_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_node_cni_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_node_ecr_pull](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_node_ecr_readonly](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_node_worker_minimal](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.eks_node_worker_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_security_group.cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_security_group_rule.cluster_external_ingress](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule) | resource |
| [aws_security_group_rule.cluster_self_ingress](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule) | resource |
| [terraform_data.autoscaling_cleanup](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.cleanup_lbc_resources](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.cluster_setup_trigger](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.internet_gateway_destroy_fence](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [time_sleep.codebuild_setup_iam_propagation](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |
| [aws_iam_policy_document.codebuild_setup_assume](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.codebuild_setup_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.eks_cluster_assume](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.eks_node_assume](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.nim_irsa_assume](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.nim_irsa_s3](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [tls_certificate.eks_oidc](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/data-sources/certificate) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_buildspec_s3_arn"></a> [buildspec\_s3\_arn](#input\_buildspec\_s3\_arn) | S3 ARN of the cluster-setup buildspec (uploaded by the root module). Format: arn:aws:s3:::bucket/key. Sidesteps CodeBuild's 25,600-char inline buildspec limit. | `string` | n/a | yes |
| <a name="input_buildspec_s3_bucket"></a> [buildspec\_s3\_bucket](#input\_buildspec\_s3\_bucket) | S3 bucket name that holds the buildspec object. Used for the CodeBuild service role's s3:GetObject grant. | `string` | n/a | yes |
| <a name="input_buildspec_s3_key"></a> [buildspec\_s3\_key](#input\_buildspec\_s3\_key) | S3 key of the buildspec object within buildspec\_s3\_bucket. Used for the CodeBuild service role's s3:GetObject grant. | `string` | n/a | yes |
| <a name="input_instance_type"></a> [instance\_type](#input\_instance\_type) | EC2 GPU instance type for NIM nodes (e.g. g6e.12xlarge). No ml. prefix. | `string` | n/a | yes |
| <a name="input_name_prefix"></a> [name\_prefix](#input\_name\_prefix) | Resource name prefix. Derived from root module local.name\_prefix + cluster key. | `string` | n/a | yes |
| <a name="input_private_subnet_ids"></a> [private\_subnet\_ids](#input\_private\_subnet\_ids) | Private subnet IDs for EKS nodes and CodeBuild. Must have outbound internet access via NAT gateway. | `list(string)` | n/a | yes |
| <a name="input_public_subnet_ids"></a> [public\_subnet\_ids](#input\_public\_subnet\_ids) | Public subnet IDs. Tagged kubernetes.io/role/elb=1 for load balancer placement. | `list(string)` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | AWS region. | `string` | n/a | yes |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC ID to deploy the EKS cluster into. | `string` | n/a | yes |
| <a name="input_allowed_cidr_blocks"></a> [allowed\_cidr\_blocks](#input\_allowed\_cidr\_blocks) | Additional CIDR blocks (e.g. developer VPN, office) granted port 443 ingress on the cluster security group. | `list(string)` | `null` | no |
| <a name="input_cache_bucket_arn"></a> [cache\_bucket\_arn](#input\_cache\_bucket\_arn) | ARN of the shared NIM model profile cache S3 bucket. Grants NIM pod IRSA read access. | `string` | `null` | no |
| <a name="input_cluster_log_types"></a> [cluster\_log\_types](#input\_cluster\_log\_types) | EKS control plane log types to enable. Sent to CloudWatch Logs. | `list(string)` | <pre>[<br/>  "api",<br/>  "audit",<br/>  "authenticator",<br/>  "controllerManager",<br/>  "scheduler"<br/>]</pre> | no |
| <a name="input_debug"></a> [debug](#input\_debug) | Enable verbose (set -x) output in the cluster-setup CodeBuild build. | `bool` | `false` | no |
| <a name="input_eks_access_entries"></a> [eks\_access\_entries](#input\_eks\_access\_entries) | Additional EKS access entries (IAM roles/users that need kubectl access). The cluster creator and CodeBuild roles get admin access automatically. | <pre>map(object({<br/>    principal_arn = string<br/>    type          = optional(string, "STANDARD")<br/>    policy_associations = optional(list(object({<br/>      policy_arn = string<br/>      access_scope = object({<br/>        type       = string<br/>        namespaces = optional(list(string))<br/>      })<br/>    })), [])<br/>  }))</pre> | `{}` | no |
| <a name="input_enable_autoscaling"></a> [enable\_autoscaling](#input\_enable\_autoscaling) | Install KEDA + kube-prometheus-stack + DCGM exporter as part of cluster-setup. Required before any deployment on this cluster can use ScaledObject-based autoscaling. | `bool` | `false` | no |
| <a name="input_enable_cache_iam"></a> [enable\_cache\_iam](#input\_enable\_cache\_iam) | Create the NIM IRSA S3 policy that grants read access to the cache bucket. Must be set from a plan-time-known value (not a computed resource attribute) to avoid count dependency errors. | `bool` | `false` | no |
| <a name="input_endpoint_private_access"></a> [endpoint\_private\_access](#input\_endpoint\_private\_access) | Enable private EKS API server endpoint. Must be true — CodeBuild is VPC-placed. | `bool` | `true` | no |
| <a name="input_endpoint_public_access"></a> [endpoint\_public\_access](#input\_endpoint\_public\_access) | Enable public EKS API server endpoint. | `bool` | `true` | no |
| <a name="input_force_rebuild"></a> [force\_rebuild](#input\_force\_rebuild) | Force cluster-setup CodeBuild to re-run on next apply regardless of input changes. | `bool` | `false` | no |
| <a name="input_internet_gateway_id"></a> [internet\_gateway\_id](#input\_internet\_gateway\_id) | IGW ID from the consumer VPC. Creates a destroy-time fence: the EKS cluster is always destroyed before the IGW, preventing ENI/NLB cleanup failures from blocking VPC teardown. | `string` | `null` | no |
| <a name="input_kubernetes_version"></a> [kubernetes\_version](#input\_kubernetes\_version) | Kubernetes version for the EKS cluster. Default 1.35 (latest standard support as of this module version). Check https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html for current versions. | `string` | `"1.35"` | no |
| <a name="input_public_access_cidrs"></a> [public\_access\_cidrs](#input\_public\_access\_cidrs) | CIDR blocks allowed to reach the public API endpoint. Null = all. Only used when endpoint\_public\_access = true. | `list(string)` | `null` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags applied to all resources. | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_cluster_endpoint"></a> [cluster\_endpoint](#output\_cluster\_endpoint) | EKS API server endpoint. |
| <a name="output_cluster_name"></a> [cluster\_name](#output\_cluster\_name) | EKS cluster name. |
| <a name="output_cluster_security_group_id"></a> [cluster\_security\_group\_id](#output\_cluster\_security\_group\_id) | Security group attached to the EKS cluster. Pass to eks-app for CodeBuild VPC placement. |
| <a name="output_nim_irsa_role_arn"></a> [nim\_irsa\_role\_arn](#output\_nim\_irsa\_role\_arn) | IRSA role ARN for NIM pods. Annotated on the nim-sa service account in each deployment. |
| <a name="output_nim_irsa_role_name"></a> [nim\_irsa\_role\_name](#output\_nim\_irsa\_role\_name) | IRSA role name for NIM pods. Used by root module to attach additional policies. |
| <a name="output_node_role_name"></a> [node\_role\_name](#output\_node\_role\_name) | EKS node IAM role name. Referenced in EC2NodeClass to assign the instance profile. |
| <a name="output_oidc_provider_arn"></a> [oidc\_provider\_arn](#output\_oidc\_provider\_arn) | OIDC provider ARN for the cluster. Used to create additional IRSA roles. |
| <a name="output_private_subnet_ids"></a> [private\_subnet\_ids](#output\_private\_subnet\_ids) | Private subnet IDs — passed through for eks-app CodeBuild vpc\_config. |
| <a name="output_vpc_id"></a> [vpc\_id](#output\_vpc\_id) | VPC ID — passed through for eks-app. |
<!-- END_TF_DOCS -->
<!-- markdownlint-enable -->
