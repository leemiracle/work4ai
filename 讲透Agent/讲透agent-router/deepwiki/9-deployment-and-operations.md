<!-- source: DeepWiki mcp.deepwiki.com · repo theagentrouter/agent-router · page 9 Deployment and Operations · fetched 2026-10-21 -->

# Deployment and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [manifests/charts/ai-gateway-helm/.helmignore](manifests/charts/ai-gateway-helm/.helmignore)
- [manifests/charts/ai-gateway-helm/Chart.yaml](manifests/charts/ai-gateway-helm/Chart.yaml)
- [manifests/charts/ai-gateway-helm/templates/NOTES.txt](manifests/charts/ai-gateway-helm/templates/NOTES.txt)
- [manifests/charts/ai-gateway-helm/templates/_helpers.tpl](manifests/charts/ai-gateway-helm/templates/_helpers.tpl)
- [manifests/charts/ai-gateway-helm/templates/admission_webhook.yaml](manifests/charts/ai-gateway-helm/templates/admission_webhook.yaml)
- [manifests/charts/ai-gateway-helm/templates/envoy_gateway_cluster_role_for_inference_pool.yaml](manifests/charts/ai-gateway-helm/templates/envoy_gateway_cluster_role_for_inference_pool.yaml)
- [manifests/charts/ai-gateway-helm/templates/mcp_session_encryption_secret.yaml](manifests/charts/ai-gateway-helm/templates/mcp_session_encryption_secret.yaml)
- [manifests/charts/ai-gateway-helm/templates/service.yaml](manifests/charts/ai-gateway-helm/templates/service.yaml)
- [manifests/charts/ai-gateway-helm/templates/serviceaccount.yaml](manifests/charts/ai-gateway-helm/templates/serviceaccount.yaml)
- [tests/e2e-namespaced/namespaced_test.go](tests/e2e-namespaced/namespaced_test.go)

</details>



The **Deployment and Operations** section provides a high-level overview of packaging, helm charts, runtime container configurations, and the CI/CD pipeline used to test, build, and release Agent Router. Agent Router is packaged using Helm charts for Kubernetes deployment and automated via GitHub Actions workflows for multi-platform container builds and semantic releases.

For deep technical details, see the child pages:
- [Helm Charts and Runtime Binaries](#9.1) — Covers `ai-gateway-helm` chart templates, values, RBAC configurations, controller and external processor entrypoint flags, and container build configurations.
- [CI/CD and Release Engineering](#9.2) — Covers GitHub Actions workflows, matrix test builds, coverage collection, GitVersion integration, and automated GitHub release pipelines.

---

## 9.1 Helm Charts and Runtime Binaries

Agent Router provides Helm charts under `manifests/charts/` to deploy the control plane controllers, mutating admission webhooks, and configure Kubernetes RBAC and ServiceAccounts [manifests/charts/ai-gateway-helm/Chart.yaml:6-18](), [manifests/charts/ai-gateway-helm/templates/serviceaccount.yaml:6-115](). The `ai-gateway-helm` chart defines the application's metadata, versioning, and maintainers [manifests/charts/ai-gateway-helm/Chart.yaml:6-36]().

The core deployment artifacts include:
- **`ai-gateway-helm`**: The primary application chart managing the controller manager deployment, ServiceAccount, ClusterRoles, and mutating webhook configurations [manifests/charts/ai-gateway-helm/templates/admission_webhook.yaml:7-124](). It also includes helper templates for naming conventions and secret management, such as for MCP session encryption [manifests/charts/ai-gateway-helm/templates/_helpers.tpl:8-144](), [manifests/charts/ai-gateway-helm/templates/mcp_session_encryption_secret.yaml:6-28]().
- **Runtime Binaries and Docker Images**: Multi-arch container builds for the controller, external processor (`extproc`), command-line interface (`aigw`), and test utilities. The `extProc` container's environment variables and image pull secrets can be configured via Helm values [manifests/charts/ai-gateway-helm/templates/_helpers.tpl:115-133]().
- **RBAC for InferencePools**: Specific ClusterRoles and ClusterRoleBindings are defined to allow Envoy Gateway to read `InferencePool` resources [manifests/charts/ai-gateway-helm/templates/envoy_gateway_cluster_role_for_inference_pool.yaml:10-38]().

```mermaid
graph TD
  sub5[""Helm Charts and Runtime Binaries""]
  sub5 --> nodeChart[""ai-gateway-helm Chart (manifests/charts/ai-gateway-helm/Chart.yaml)""]
  sub5 --> nodeWebhook[""Admission Webhook (manifests/charts/ai-gateway-helm/templates/admission_webhook.yaml)""]
  sub5 --> nodeRBAC[""RBAC & ServiceAccount (manifests/charts/ai-gateway-helm/templates/serviceaccount.yaml)""]
  sub5 --> nodeHelpers[""Chart Helpers (manifests/charts/ai-gateway-helm/templates/_helpers.tpl)""]
  sub5 --> nodeMCPSec[""MCP Session Encryption Secret (manifests/charts/ai-gateway-helm/templates/mcp_session_encryption_secret.yaml)""]
  sub5 --> nodeEGInfPool[""Envoy Gateway InferencePool RBAC (manifests/charts/ai-gateway-helm/templates/envoy_gateway_cluster_role_for_inference_pool.yaml)""]

  classDef default stroke:#000,fill:none;
```
*Figure 1: Helm and Runtime Artifact Topology.*

Sources: `manifests/charts/ai-gateway-helm/Chart.yaml`, `manifests/charts/ai-gateway-helm/templates/serviceaccount.yaml`, `manifests/charts/ai-gateway-helm/templates/admission_webhook.yaml`, `manifests/charts/ai-gateway-helm/templates/_helpers.tpl`, `manifests/charts/ai-gateway-helm/templates/mcp_session_encryption_secret.yaml`, `manifests/charts/ai-gateway-helm/templates/envoy_gateway_cluster_role_for_inference_pool.yaml`.

For comprehensive details on chart configuration, helm values, container build args, and binary entrypoints, see [Helm Charts and Runtime Binaries](#9.1).

---

## 9.2 CI/CD and Release Engineering

The development and release life cycle of Agent Router is fully automated through GitHub Actions workflows. The CI framework validates code quality, executes unit, controller, CRD CEL, and data plane test suites across multiple operating systems, and uploads code coverage metrics `[.github/workflows/build_and_test.yaml:1-192]()`. E2E tests, such as `TestNamespaced`, verify deployment configurations like namespace watching and endpoint prefixes [tests/e2e-namespaced/namespaced_test.go:38-132]().

Key pipelines include:
- **Build and Test (`build_and_test.yaml`)**: Runs path-filtered code checks, unit test matrices, CRD CEL validation, and downstream integration tests `[.github/workflows/build_and_test.yaml:29-192]()`.
- **Docker Build Job (`docker_build_job.yaml`)**: Handles multi-platform (`amd64`, `arm64`) image compilation and pushing for controllers, extproc, and the `aigw` CLI `[.github/workflows/docker_build_job.yaml:11-79]()`.
- **Release Pipeline (`release.yaml`)**: Triggered on semantic version tags (`v*`), packaging Helm charts, pushing images, and compiling static binaries for supported operating systems `[.github/workflows/release.yaml:1-65]()`.

```mermaid
graph TD
  subCI[""CI/CD and Release Engineering""]
  subCI --> nodeBuildTest[""Build & Test Workflow (.github/workflows/build_and_test.yaml)""]
  nodeBuildTest --> e2eTest[""E2E Namespaced Test (tests/e2e-namespaced/namespaced_test.go)""]
  subCI --> nodeDockerBuild[""Docker Build Job (.github/workflows/docker_build_job.yaml)""]
  subCI --> nodeRelease[""Release Pipeline (.github/workflows/release.yaml)""]

  classDef default stroke:#000,fill:none;
```
*Figure 2: CI/CD Pipeline Architecture.*

Sources: `.github/workflows/build_and_test.yaml`, `.github/workflows/docker_build_job.yaml`, `.github/workflows/release.yaml`, `tests/e2e-namespaced/namespaced_test.go`.

For complete workflows, build matrix definitions, and release note automation details, see [CI/CD and Release Engineering](#9.2).

---

