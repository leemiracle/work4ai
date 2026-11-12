# Contributing to terraform-aws-nim

Example Terraform for deploying NVIDIA NIMs on AWS — SageMaker (async/realtime) and EKS.
Maintained by the NVIDIA Solutions Architect team as customer-enablement code, not an
official NVIDIA-supported product. Consumers reference it via git source from this
repository.

---

## Quick Reference

What makes a good contribution to this module:

- **Structure:** One concern per file. Submodules when a platform's resources are complex enough to warrant isolation (e.g. EKS has two submodules: one for cluster infrastructure, one for app deployment).
- **Variables:** `existing_` prefix for consumer-provided resources. Objects for grouped config.
- **Resources:** Descriptive logical names. Random IDs for uniqueness. `local.name_prefix` for AWS names.
- **Security:** No `0.0.0.0/0` ingress. Consumers control external access.
- **Networking:** Module never creates VPCs or subnets — consumers provide existing infrastructure.
- **Testing:** Plan tests for all new code paths. Apply tests with explicit opt-in only.
- **Secrets:** Either a direct value or a Secrets Manager ARN — never both, never created inside the module.

See [DESIGN_STANDARDS.md](DESIGN_STANDARDS.md) for the full standards and rationale behind each pattern.

---

## Tools Required

```bash
# Terraform >= 1.14 (required for action_trigger lifecycle)
brew install tfenv && tfenv install latest

# terraform-docs — keeps README.md inputs/outputs current
brew install terraform-docs

# tflint — catches naming issues, missing descriptions, deprecated syntax
brew install tflint && tflint --init   # installs the AWS ruleset

# shellcheck — shell script linting (shim/ scripts)
brew install shellcheck

# pre-commit — runs all checks in one command
pip install pre-commit
```

`pre-commit run --all-files` calls these tools directly — it does not install them.
Pre-commit only manages its own hook environments (gitleaks, terraform hooks, etc.).

---

## Development Workflow

### Commits are checkpoints — use them freely

Commit frequently during development, especially when working with AI assistance. A commit
does not need to be complete or passing. Commits are cheap rollback points; the push gate
is where quality is enforced.

```bash
git add -p && git commit -m "wip: eks node group draft"   # checkpoint, fine
```

### Before you push: run the full local check

```bash
pre-commit run --all-files
```

This runs all checks: formatting, docs generation, validation, linting, and plan tests.
Auto-fixing hooks (`terraform_fmt`, `terraform_docs`) modify files in place — stage those
changes and re-run:

```bash
pre-commit run --all-files
# → terraform_fmt reformatted main.tf
git add main.tf README.md
pre-commit run --all-files   # clean pass
git commit -m "add foo variable" && git push
```

`terraform_test` requires AWS credentials in the environment — plan tests call AWS APIs
to resolve data sources.

### terraform-docs and README.md

Variable and output documentation is auto-generated between these markers in `README.md`:

```
<!-- BEGIN_TF_DOCS -->
...never edit by hand...
<!-- END_TF_DOCS -->
```

`pre-commit run --all-files` updates these automatically. To regenerate manually:

```bash
terraform-docs .
```

Edit prose above and below the markers freely. Never edit between them.

---

## Testing

```bash
# Run all plan-only tests (AWS credentials required — data sources are resolved during plan)
terraform test

# Specific file
terraform test -filter=tests/01_sagemaker_nim.tftest.hcl
```

Plan tests validate the resource graph. Apply tests (commented out in test files) create
real AWS resources — only run those with explicit intent and valid credentials.

**Rules:**

- Every example in `examples/` must have a corresponding test. Examples serve dual
  purpose: they show consumers how to use the module, and they are the primary test
  vehicle for the variable combinations and code paths that matter in practice.
- Structure examples to exercise as many variables and conditional paths as possible —
  an example that only sets two fields provides weak coverage.
- Test assertions reference root-level `output.*`, not `module.nim.*`.
- Plan tests are always on. Apply tests are always opt-in (commented out by default).

**Common apply test failures:**

| Failure                                   | Cause                                 | Fix                                                                            |
| ----------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------ |
| `InsufficientInstanceCapacity`            | GPU instance not available            | Try a different AZ or instance family |
| `Cannot create already existing endpoint` | Async deletion race: `CreateEndpoint` returns 200 immediately, endpoint transitions to `Failed`, delete waiter exits early, name stays held | `-replace='module.terraform-aws-nim.random_id.endpoint_suffix["<key>"]'` (see README Troubleshooting) |
| Endpoint reaches `Failed` after N minutes | `container_startup_timeout` too short | Increase timeout; check CloudWatch logs for startup duration                   |

---

## Module Structure

```
├── main.tf            Core compute + cross-variable validation preconditions
├── variables.tf       All inputs — global scalars + per-resource config objects
├── outputs.tf         All outputs — try() for count-gated refs, null when platform not set
├── locals.tf          All locals, organized by concern with section comments
├── data.tf            All data sources
├── versions.tf        required_providers only — no provider block
├── iam.tf             IAM roles and policies
├── ecr.tf             ECR repository and lifecycle policy
├── s3.tf              S3 buckets and configurations
├── codebuild.tf       CodeBuild projects and action triggers
├── archives.tf        Shim source zip — data archive + S3 object upload
├── buildspecs/        CodeBuild buildspec YAML files (never inline in .tf)
├── shim/              SageMaker protocol adapter — TEMPORARY (see below)
├── modules/
│   ├── eks-infra/     EKS Auto Mode cluster + GPU NodePool (via cluster-setup CodeBuild)
│   └── eks-app/       EKS deploy — NIM via Helm or open-weight via kubectl
├── examples/
│   ├── README.md      Index of all examples
│   ├── sagemaker/
│   │   ├── nim/       NGC NIM realtime endpoint on SageMaker
│   │   └── open-weight/ Open-weight LLM via vLLM on SageMaker
│   ├── eks/
│   │   ├── nim/       NIM on EKS Auto Mode via Helm
│   │   └── open-weight/ Open-weight LLM via vLLM on EKS
│   └── all-inference/ All four paths in one apply: SageMaker + EKS, NIM + open-weight
└── tests/
    ├── 01_sagemaker_nim.tftest.hcl
    ├── 02_sagemaker_open_weight.tftest.hcl
    ├── 03_eks_nim.tftest.hcl
    ├── 04_eks_open_weight.tftest.hcl
    ├── 05_all_inference.tftest.hcl
    └── helpers/
        ├── invoke-sagemaker/
        ├── invoke-eks-nim/
        └── invoke-eks-open-weight/
```

---

## Adding a New Deployment Target

New platforms are added as submodules gated by a typed map variable. An empty map (`{}`) =
platform not deployed. A non-empty map = one or more deployments provisioned.

**Why maps of objects over strings:** A typed `map(object({...}))` gives Terraform
compile-time validation of all platform-specific fields and allows multiple named deployments
in one module call. A string variable (`deployment_target = "EKS"`) requires consumers to
know which other top-level variables apply — config is scattered and unvalidated.

```hcl
# variables.tf — new platform variable (use typed object from the start, not type = any)
variable "triton_endpoints" {
  type = map(object({
    instance_type  = string
    model_id       = string
    # ... platform-specific fields with optional() and defaults
  }))
  default     = {}
  description = "Triton inference server endpoints. Empty map = no Triton resources."
}
```

Steps to add a new platform:

1. Add `<platform>_endpoints` (or `<platform>_deployments` for multi-stage platforms like EKS)
   variable to `variables.tf` as a typed `map(object({...}))` with `optional()` for all
   non-required fields and sensible defaults. Follow the naming convention of existing variables:
   `sagemaker_endpoints`, `eks_deployments`.
2. Create `modules/<descriptive-name>/` with functional names that describe the concern, not
   the NIM brand (e.g. `eks-infra`, `eks-app` — not `nim-eks`). Include `main.tf`,
   `variables.tf`, `outputs.tf`, `versions.tf`, and `README.md`.
3. Add a `module "<name>"` block in `main.tf` using `for_each = var.<platform>_endpoints`.
   Gate all resources inside the submodule on the map being non-empty.
4. Add `examples/<platform>/` with a working example and update `examples/README.md`.
5. Add a test in `tests/` following the existing numbering scheme.

---

## The Shim (Temporary)

The `shim/` directory adapts the NIM API to SageMaker's `/ping` + `/invocations` interface
via a Caddy reverse proxy. It is a **temporary workaround** until NIMs natively support
SageMaker's non-standard health-check and invocation paths (`/ping`, `/invocations`) instead
of the standard OpenAI-compatible endpoints NIMs expose by default.

When native support ships:

1. Add `"DEPRECATED: "` prefix to `shim_config` variable description.
2. After one minor version cycle, remove: `shim/`, CodeBuild shim project in `codebuild.tf`,
   `archives.tf`, and the `shim_config` variable.

Do not add new features to the shim. Fix bugs only.

---

## Branching and PRs

- Branch from `main`. Prefix: `feat/`, `fix/`, `chore/`, `docs/`
- One logical change per PR. Interface changes, new platforms, and bug fixes in separate PRs.
- Breaking variable changes require a major version bump. Adding optional variables does not.
- Use `moved {}` blocks when renaming resources to preserve existing consumer state.

---

## Checklists

### New variable or output

- [ ] Has a `description`
- [ ] Sensitive variables have `sensitive = true`
- [ ] Complex objects use `optional()` for all fields with defaults
- [ ] Consumer-provided resources use `existing_` prefix
- [ ] `terraform test` passes (plan-only)
- [ ] `terraform-docs` regenerated

### New resource

- [ ] Uses descriptive logical name (not `this` or `main`)
- [ ] Sets `region = var.region`
- [ ] Uses `merge(var.tags, { Name = "..." })` for tags
- [ ] Name derives from `local.name_prefix`
- [ ] No `0.0.0.0/0` ingress rules
- [ ] Added to `outputs.tf` if consumers need to reference it

### New platform

- [ ] Gated by non-empty map via `for_each = var.<platform>_endpoints`
- [ ] Config variable uses typed `map(object({...}))` with `optional()` fields and defaults
- [ ] Submodule stub created in `modules/`
- [ ] Example added in `examples/<platform>/`
- [ ] Tests added in `tests/`

### Before opening a PR

- [ ] `pre-commit run --all-files` passes clean
- [ ] `terraform test` passes
- [ ] `terraform fmt -check` clean
- [ ] No hardcoded account IDs, ARNs, or region strings
- [ ] No secrets or credentials in any file
- [ ] DESIGN_STANDARDS.md consulted for any pattern questions

---

## Referencing this sample from customer code

This code is **not published to the Terraform Registry** — it is SA-maintained
sample/example code and is not an official NVIDIA product. Customers consuming this
sample reference it via git source from this repository:

```hcl
module "nim" {
  source = "git::https://github.com/NVIDIA/nvidia-aws-samples.git//inference/terraform-aws-nim?ref=main"
}
```

For reproducibility, pin `ref` to a specific commit SHA rather than `main` in production
customer code.
