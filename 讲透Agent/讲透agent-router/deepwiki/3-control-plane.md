<!-- source: DeepWiki mcp.deepwiki.com · repo theagentrouter/agent-router · page 3 Control Plane · fetched 2026-10-21 -->

# Control Plane

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmd/aigw/testdata/translate_basic.out.yaml](cmd/aigw/testdata/translate_basic.out.yaml)
- [internal/controller/ai_gateway_route.go](internal/controller/ai_gateway_route.go)
- [internal/controller/ai_gateway_route_test.go](internal/controller/ai_gateway_route_test.go)
- [internal/controller/ai_service_backend.go](internal/controller/ai_service_backend.go)
- [internal/controller/ai_service_backend_test.go](internal/controller/ai_service_backend_test.go)
- [internal/controller/controller.go](internal/controller/controller.go)
- [internal/controller/controller_test.go](internal/controller/controller_test.go)
- [tests/controller/controller_test.go](tests/controller/controller_test.go)

</details>



## Purpose and Scope

The control plane of Envoy AI Gateway manages custom resource definitions (`AIGatewayRoute`, `AIServiceBackend`, `MCPRoute`, `BackendSecurityPolicy`, `GatewayConfig`) and translates them into Envoy Gateway resources (`HTTPRoute`, `Backend`, `HTTPRouteFilter`, `BackendTLSPolicy`) and filter configurations for the external processor (`extproc`) data plane. 

This page provides a high-level overview of the controller manager, core reconcilers, mutating webhooks, credential rotation subsystems, and the Envoy Gateway extension server. For detailed implementation mechanics, refer to the child pages linked below.

Sources: [`internal/controller/controller.go:120-140`](), [`internal/controller/ai_gateway_route.go:53-107`]()

---

```mermaid
graph TD
    sub5 ["Code Entity Space"]
    sub5 --> StartControllers["controller.StartControllers()"]
    StartControllers --> GatewayC["controller.GatewayController"]
    StartControllers --> AIRouteC["controller.AIGatewayRouteController"]
    StartControllers --> BackendC["controller.AIBackendController"]
    
    GatewayC --> FilterSec["controller.reconcileFilterConfigSecret()"]
    FilterSec --> FilterConfig["filterapi.Config"]
    
    AIRouteC --> HTTPRoute["gwapiv1.HTTPRoute"]
    AIRouteC --> RouteFilters["controller.generateHTTPRouteFilters()"]

    sub4 ["Natural Language Space"]
    sub4 -.->|"Reconciles Gateway CRs"| GatewayC
    sub4 -.->|"Reconciles AI Routes"| AIRouteC
    sub4 -.->|"Manages Secret Bundles"| FilterConfig
```
*Figure 1: Control Plane architecture bridging natural language concepts to controller and translation entities.*

Sources: [`internal/controller/controller.go:116-140`](), [`internal/controller/ai_gateway_route.go:53-157`]()

---

## 3.1 Controllers and Reconciliation

The controller manager initializes all controllers via `controller.StartControllers` [`internal/controller/controller.go:120-140`](). It registers field indexers to optimize lookup performance across dependent resources [`internal/controller/controller.go:122-125`](). Reconcilers such as `AIGatewayRouteController` [`internal/controller/ai_gateway_route.go:53-68`]() and `AIBackendController` [`internal/controller/ai_service_backend.go:27-32`]() manage state transitions, applying finalizers for cleanup and validating cross-namespace references through `ReferenceGrant`.

For detailed implementation, indexing strategies, status updates, and finalizer mechanics, see [Controllers and Reconciliation](#3.1).

Sources: [`internal/controller/controller.go:120-140`](), [`internal/controller/ai_gateway_route.go:53-107`](), [`internal/controller/ai_service_backend.go:27-63`]()

---

## 3.2 Filter Config Generation and Pod Mutation

`GatewayController` aggregates active route and backend definitions into structured bundles stored as Kubernetes Secrets. The underlying schema is defined by `filterapi.Config` [`cmd/aigw/testdata/translate_basic.out.yaml:189-207`](). A mutating admission webhook (`gatewayMutator`) intercepts `Gateway` creation and updates, automatically injecting the `extproc` container sidecar with the correct configuration hashes and environment variables.

For detailed schema definitions, watcher logic, and container builder mechanics, see [Filter Config Generation and Pod Mutation](#3.2).

Sources: [`internal/controller/controller.go:120-140`](), [`cmd/aigw/testdata/translate_basic.out.yaml:189-207`]()

---

```mermaid
graph TD
    sub3 ["Code Entity Space"]
    sub3 --> GwReconcile["GatewayController.Reconcile()"]
    GwReconcile --> FetchCfg["GatewayController.fetchGatewayConfig()"]
    GwReconcile --> RecSec["GatewayController.reconcileFilterConfigSecret()"]
    RecSec --> AnnotatePods["GatewayController.annotateGatewayPods()"]
    AnnotatePods --> ExtProc["extProcBuilder"]

    sub2 ["Natural Language Space"]
    sub2 -.->|"Watch Gateway Event"| GwReconcile
    sub2 -.->|"Build Config Secret"| RecSec
    sub2 -.->|"Inject Sidecar"| AnnotatePods
```
*Figure 2: Gateway reconciliation pipeline and filter config bundle generation flow.*

Sources: [`internal/controller/controller.go:120-140`]()

---

## 3.3 Credential Management and Token Rotators

The `BackendSecurityPolicy` controller monitors backend authentication requirements and integrates with cloud provider token providers (AWS, GCP, Azure) [internal/controller/controller_test.go:73-191](). It manages secure lifecycle handling, automated token rotation, and dynamic secret mounting to ensure secure communication between the data plane and upstream LLM providers.

For details on secret handling, error retry semantics, and token rotators, see [Credential Management and Token Rotators](#3.3).

Sources: [`internal/controller/controller_test.go:73-191`]()

---

## 3.4 Envoy Gateway Extension Server

The Envoy Gateway Extension Server intercepts Envoy Gateway translation phases via xDS hooks (`PostTranslateModify`, `PostRouteModify`, `PostClusterModify`). It dynamically injects UNIX Domain Socket (UDS) clusters for `extproc`, manages `InferencePool` and `MCP` routing extensions, and configures forward proxy capabilities.

For information on xDS extension hook wiring and proxy translation logic, see [Envoy Gateway Extension Server](#3.4).

Sources: [`internal/controller/controller.go:120-140`]()

---

