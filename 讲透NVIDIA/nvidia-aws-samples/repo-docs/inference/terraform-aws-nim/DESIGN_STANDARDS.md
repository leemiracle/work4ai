# terraform-aws-nim — Design Standards

Standards for contributors to this module. Every decision here has a reason — read the
rationale before changing a pattern.

---

## Core Principles

### 1. Readability First

Clear code over clever abstractions. A reviewer should understand what a resource does
without cross-referencing five locals. Prefer explicit over implicit. Comment the *why*,
not the *what*.

### 2. Dynamic Configuration with Reasonable Defaults

The primary design pattern for this module: use typed maps of objects with well-defined
schemas, optional fields, and sensible defaults. A single `module "nim"` call configures
everything. Consumers only set what they need — the rest works out of the box.

**Two kinds of variables:**

- **Global scalars** — settings that affect all resources equally (e.g., `region`, `tags`,
  `debug`, `force_rebuild`). Flat top-level variables are correct here.
- **Per-resource config** — settings that vary per endpoint, per platform, or per instance.
  These use maps of typed objects. Each key creates a resource; the object defines its
  configuration. `null` = resource not created.

```hcl
# CORRECT — global scalar for a setting that affects everything
debug = true

# CORRECT — map of typed objects for per-resource config
sagemaker_endpoints = {
  llama = {
    source_image_uri = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
    instance_type    = "ml.g6e.12xlarge"
    # optional fields use sensible defaults — consumers only set what they need
  }
}

# WRONG — boolean flags with scattered companion variables
enable_sagemaker        = true
sagemaker_instance_type = "ml.g6e.12xlarge"
sagemaker_image_uri     = "..."
```

Every per-resource object field that isn't required should be `optional()` with a default
that works for the common case:

```hcl
variable "sagemaker_endpoints" {
  type = map(object({
    source_image_uri          = string
    instance_type             = string
    endpoint_type             = optional(string, "realtime")
    container_startup_timeout = optional(number, 600)
    enable_model_profile_cache = optional(bool, false)
  }))
}
```

Plan for the future — add fields as the need becomes clear, not speculatively. Today's
problem solved cleanly is more valuable than a flexible abstraction that nobody asked for.

### 3. Conservative Variable Exposure

Start minimal — add variables when users request them. Easier to add than remove.
Every exposed variable is a backward-compatibility commitment. Default values should
work for 80% of use cases without modification.

### 4. Security by Default

- No `0.0.0.0/0` ingress rules in module code
- No plaintext secrets in state where avoidable
- Secrets via direct value OR Secrets Manager ARN — never both
- Users control external access; the module creates internal communication rules

---

## Networking Boundary

**This module does not create VPCs, subnets, Route 53 zones, NAT gateways, or any
foundational network infrastructure.**

**Why:** Networking is almost always managed by a separate infrastructure team or
repository and pre-exists before this module runs. Embedding VPC creation here would
couple the module to a specific network topology and prevent adoption in environments
where the network already exists. Foundational infrastructure has its own lifecycle —
it outlives any individual service deployment.

The module accepts pre-existing network infrastructure via consumer-provided variables.
Use the `existing_` prefix to signal that the resource was created outside this module:

```hcl
# CORRECT — consumer provides existing infrastructure
variable "existing_vpc_id" {
  type        = string
  description = "VPC ID where SageMaker and CodeBuild resources are deployed."
}

variable "existing_subnet_ids" {
  type        = map(string)  # AZ → subnet ID
  description = "Subnet IDs keyed by AZ. Used for EKS node placement."
}

# WRONG — module creates foundational infrastructure
resource "aws_vpc" "nim" { ... }
```

**What the module does create** (service-specific, not foundational):
- ECR repository
- S3 buckets (CodeBuild source, model cache, async output)
- IAM roles and policies
- CodeBuild projects
- SageMaker models, endpoint configurations, endpoints
- EKS Auto Mode cluster + GPU NodePool (via `modules/eks-infra/`)
- CloudWatch log groups for endpoint logs

**What the module never creates:**
- VPCs, subnets, internet gateways, NAT gateways, route tables
- Secrets Manager secrets (users create these before apply)
- Route 53 hosted zones
- ACM certificates

---

## Variable Naming

### `existing_` prefix for consumer-provided resources

Variables that reference infrastructure created outside this module use the `existing_`
prefix. This signals to consumers that the resource must exist before apply.

```hcl
# CORRECT
variable "existing_vpc_id" { }
variable "existing_subnet_ids" { }
variable "existing_security_group_ids" { }

# WRONG — ambiguous ownership
variable "vpc_id" { }
variable "subnet_ids" { }
```

### Object variables for grouped config

Per-endpoint or per-platform settings use typed objects, not flat variables. This keeps
related config self-contained and validates as a unit.

```hcl
# CORRECT — platform config is one typed object
sagemaker_endpoints = {
  llama = {
    source_image_uri          = "nvcr.io/nim/meta/llama-3.1-8b-instruct:1.8.3"
    instance_type             = "ml.g6e.12xlarge"
    container_startup_timeout = 900
  }
}

# WRONG — flat variables scatter related config
sagemaker_instance_type = "ml.g6e.12xlarge"
sagemaker_source_image_uri = "nvcr.io/nim/..."
sagemaker_container_startup_timeout = 900
```

### Required fields

Every variable must have a `description`. Sensitive variables must have `sensitive = true`.
Complex object variables use `optional()` for all fields with sane defaults.

---

## Resource Naming

### Logical names

Use descriptive Terraform resource identifiers. Never use `this` or `main` when a
more specific name is available.

```hcl
# CORRECT
resource "aws_iam_role" "sagemaker_execution" { }
resource "aws_iam_role" "codebuild" { }
resource "aws_s3_bucket" "nim_cache" { }
resource "aws_s3_bucket" "sagemaker_output" { }
resource "aws_ecr_repository" "nim" { }

# WRONG
resource "aws_iam_role" "this" { }
resource "aws_s3_bucket" "main" { }
```

### AWS resource names

All named AWS resources derive their name from `local.name_prefix`:

```hcl
locals {
  name_prefix = "${var.project_prefix}-${var.environment}"
}

resource "aws_iam_role" "sagemaker_execution" {
  name = "${local.name_prefix}-sagemaker-exec"
}
```

This avoids conflicts when the module is instantiated twice in the same account.

### Random suffixes

`random_id` (4-byte hex) is appended where AWS enforces unique names and async deletion
holds the name during cleanup (SageMaker endpoints, S3 buckets). Stored in Terraform
state — stable across applies, changes only on taint or full destroy+apply.

---

## File Organization

```
├── main.tf          Core compute resources + cross-variable validation
├── variables.tf     All input variables — global scalars + per-resource config objects
├── outputs.tf       All module outputs
├── locals.tf        All locals — organized by concern with section headers
├── data.tf          All data sources
├── versions.tf      required_providers only — no provider block
├── ecr.tf           ECR repository and lifecycle policy
├── s3.tf            S3 buckets and bucket configurations
├── iam.tf           All IAM roles and policies
├── codebuild.tf     All CodeBuild projects and action triggers
├── archives.tf      Data archive + S3 object for CodeBuild source
├── buildspecs/      CodeBuild buildspec files — never inline in .tf
├── shim/            SageMaker adapter (TEMPORARY — see CONTRIBUTING.md)
├── modules/
│   ├── eks-infra/   EKS Auto Mode cluster + GPU NodePool
│   └── eks-app/     EKS deploy — NIM via Helm or open-weight via kubectl
├── examples/        Working example configurations
└── tests/           Terraform test files (.tftest.hcl)
```

**Rule:** One concern per file. Don't add SageMaker resources to `s3.tf`. Don't add
IAM inline policies to `main.tf`.

---

## Terraform Patterns

### No provider block in the module

Consumers pass the AWS provider. Each resource sets `region = var.region` (AWS provider
v6 per-resource region pattern). No provider aliases.

```hcl
# CORRECT
resource "aws_s3_bucket" "nim_cache" {
  region = var.region
  bucket = local.cache_bucket_name
}

# WRONG — never declare a provider block in module files
provider "aws" {
  region = var.region
}
```

### Map-of-objects gating

```hcl
# Resources gated on a config object being non-null
resource "aws_sagemaker_endpoint" "nim" {
  for_each = var.sagemaker_endpoints  # empty map = no resources
}
```

### `try()` for count-gated resource attributes

```hcl
# CORRECT — try() avoids plan-time error when count = 0
output "cache_bucket" {
  value = try(aws_s3_bucket.nim_cache[0].bucket, null)
}

# WRONG — ternary evaluates both branches at plan time
output "cache_bucket" {
  value = local.enable_cache ? aws_s3_bucket.nim_cache[0].bucket : null
}
```

### Cross-variable validation

`variable` validation blocks cannot reference other variables. Use `lifecycle.precondition`
on a sentinel `terraform_data` resource in `main.tf`:

```hcl
resource "terraform_data" "validation" {
  lifecycle {
    precondition {
      condition     = var.ngc_credentials.api_key == null || var.ngc_credentials.secret_arn == null
      error_message = "ngc_credentials: set api_key or secret_arn, not both."
    }
  }
}
```

### Submodule variable alignment

Submodule calls use `for_each` on the typed map variable. Each entry creates one
submodule instance; `each.value` fields are passed individually to submodule inputs.

```hcl
# CORRECT — for_each on typed map; fields sourced from each.value
module "eks_infra" {
  for_each = var.eks_clusters
  source   = "./modules/eks-infra"

  name_prefix   = "${local.name_prefix}-${each.key}"
  region        = var.region
  vpc_id        = each.value.vpc_id
  subnet_ids    = each.value.private_subnet_ids
  instance_type = each.value.instance_type
}

# WRONG — scattered flat top-level variables instead of a typed map
module "eks_infra" {
  instance_type = var.eks_instance_type
  node_count    = var.eks_node_count
  subnet_ids    = var.eks_subnet_ids
}
```

Flat scalar variables scatter per-resource config across the top-level interface and are
untyped as a group. A typed `map(object({...}))` keeps related config together, validates
as a unit at plan time, and naturally extends to multiple named deployments.

---

## Tags

Every taggable resource uses `merge()`:

```hcl
tags = merge(var.tags, {
  Name = "${local.name_prefix}-sagemaker-exec"
})
```

`var.tags` is applied first so consumers can override module defaults. The `Name` tag
is always resource-specific and set last.

---

## Secrets

Two patterns, mutually exclusive per credential:

1. **Direct value** — stored in Terraform state (encrypted at rest). Acceptable for dev.
   Mark variables `sensitive = true`.

2. **Secrets Manager ARN** — module reads via `data "aws_secretsmanager_secret_version"`.
   Value never stored in module state. Required for production.

Never create Secrets Manager secrets from inside this module — consumers create them
before apply.

---

## S3 Bucket Naming

Bucket names **must** contain `"sagemaker"`. `AmazonSageMakerFullAccess` enforces this
via a condition on `s3:*` actions.

```
{project_prefix}-{environment}-sagemaker-{purpose}-{random_hex}
```

Do not remove `"sagemaker"` from this pattern.

---

## CodeBuild

- Buildspec files live in `buildspecs/` — never inline a buildspec in a `.tf` file.
- `action` blocks do not support `count` — use `for_each` on a map.
- The `depends_on` bug between `action_trigger` resources is real and confirmed
  (GitHub issue #37930). The pre_build polling workaround in each buildspec must remain
  until Terraform fixes this.
- All CodeBuild projects (base-sync, shim, weight-fetch, model-profile-cache) are always
  declared. IAM roles and projects have no cost when idle — the `terraform_data` trigger
  resource controls whether builds fire.

---

## Security Groups

The module creates internal communication groups. Consumers control external access.

```hcl
# Module creates — internal service communication only
resource "aws_security_group" "codebuild" {
  name   = "${local.name_prefix}-codebuild"
  vpc_id = var.existing_vpc_id

  egress {
    description = "Outbound for AWS APIs, ECR, NGC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Consumer provides — external access rules
variable "existing_security_group_ids" {
  type        = list(string)
  description = "Security group IDs for external access. Applied alongside module-created groups."
  default     = []
}
```

---

## Testing

- Test files live in `tests/` with `.tftest.hcl` extension.
- Plan-only tests (`command = plan`) are the default — AWS credentials required, as data sources are resolved during plan.
- Apply tests are commented out and require explicit opt-in.
- Test assertions reference root-level `output.*`, not `module.nim.*`.
- Every example in `examples/` must have a corresponding test. Examples serve dual
  purpose: they show consumers how to use the module, and they are the primary test
  vehicle for the variable combinations and code paths that matter in practice.
- Structure examples to exercise as many variables and conditional paths as possible —
  an example that only sets two fields provides weak coverage.

---

## Breaking Changes

- Removing or renaming a `variable` is a breaking change — bump the major version.
- Adding a `variable` with a default is non-breaking.
- Use `moved` blocks when renaming resources to preserve existing state.
- Mark deprecated variables with a `description` prefix of `"DEPRECATED: "` for at
  least one minor version before removal.

---

## What This Module Does Not Do

| Does Not | Why |
|---|---|
| Create VPCs or subnets | Networking pre-exists; owned by a separate team or repo |
| Create Secrets Manager secrets | Consumers own credential lifecycle |
| Create Route 53 zones | DNS is foundational infrastructure, out of scope |
| Create ACM certificates | Certificate lifecycle belongs to the domain owner |
| Manage GPU drivers or AMIs directly | Delegated to SageMaker and EKS Auto Mode |
| Use `0.0.0.0/0` ingress rules | Consumers define their own access boundaries |
