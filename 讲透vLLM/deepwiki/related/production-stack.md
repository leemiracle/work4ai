# production-stack

> 来源: https://deepwiki.com/vllm-project/production-stack 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [README.md](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1)
  * [community/community-event.md](https://github.com/vllm-project/production-stack/blob/99ab33ab/community/community-event.md?plain=1)
  * [docs/source/community/meetings.rst](https://github.com/vllm-project/production-stack/blob/99ab33ab/docs/source/community/meetings.rst)
  * [docs/source/deployment/gateway-inference-extension.rst](https://github.com/vllm-project/production-stack/blob/99ab33ab/docs/source/deployment/gateway-inference-extension.rst)
  * [docs/source/deployment/index.rst](https://github.com/vllm-project/production-stack/blob/99ab33ab/docs/source/deployment/index.rst)
  * [helm/README.md](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/README.md?plain=1)
  * [helm/templates/_helpers.tpl](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl)
  * [helm/templates/deployment-router.yaml](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-router.yaml)
  * [helm/templates/deployment-vllm-multi.yaml](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml)
  * [helm/templates/secrets.yaml](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/secrets.yaml)
  * [helm/values.schema.json](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.schema.json)
  * [helm/values.yaml](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml)
  * [tutorials/README.md](https://github.com/vllm-project/production-stack/blob/99ab33ab/tutorials/README.md?plain=1)

## Purpose and Scope

The **vLLM Production Stack** provides a reference implementation for deploying vLLM inference engines at production scale on Kubernetes. This document introduces the system architecture, core components, deployment options, and key capabilities. It serves as the entry point for understanding how the stack orchestrates distributed model serving, request routing, KV cache management, and observability.

For detailed deployment instructions, see [Getting Started](/vllm-project/production-stack/3-getting-started), [Helm Chart Deployment](/vllm-project/production-stack/4-helm-chart-deployment), or [Kubernetes Operator](/vllm-project/production-stack/10-kubernetes-operator). For router-specific details, see [vLLM Router](/vllm-project/production-stack/5-vllm-router). For caching and optimization, see [Caching and Optimization](/vllm-project/production-stack/6-caching-and-optimization).

**Sources:** [README.md20-27](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L20-L27) [helm/README.md1-9](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/README.md?plain=1#L1-L9)

## What is vLLM Production Stack?

vLLM Production Stack is a Kubernetes-native inference serving platform that extends vLLM with production-grade capabilities including intelligent request routing, distributed KV cache management, multi-model serving, and comprehensive observability. The stack enables organizations to scale from a single vLLM instance to a distributed deployment without application code changes while providing performance optimizations through cache reuse and routing strategies.

The system consists of three primary layers:

  * **Serving Layer:** vLLM engine pods that execute model inference with GPU acceleration
  * **Routing Layer:** FastAPI-based router that distributes requests and exports metrics
  * **Observability Layer:** Prometheus and Grafana for monitoring inference workloads

**Sources:** [README.md22-27](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L22-L27) [README.md40-45](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L40-L45)

## System Architecture

The following diagram shows the core components and their relationships:

**Core Components Architecture**

This diagram maps system concepts to their Kubernetes resources and configuration keys.

**Sources:** [README.md40-48](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L40-L48) [helm/values.yaml1-739](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L1-L739) [helm/templates/deployment-vllm-multi.yaml1-523](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L1-L523) [helm/templates/deployment-router.yaml1-200](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-router.yaml#L1-L200)

## Deployment Paradigms

The stack supports two deployment methods, each suited for different operational requirements:

Deployment Method| Configuration Mechanism| Resource Generation| Use Case  
---|---|---|---  
**Helm-based**| `values.yaml` with `servingEngineSpec` and `routerSpec`| Helm template engine processes templates in `helm/templates/`| Standard deployments, straightforward configuration, GitOps workflows  
**Operator-based**|  Custom Resource Definitions (CRDs): `VLLMRuntime`, `VLLMRouter`, `CacheServer`| Operator controllers reconcile desired state into Kubernetes resources| Advanced scenarios requiring Kubernetes-native lifecycle management  
  
### Helm Chart Deployment

The Helm chart approach uses declarative YAML configuration in `values.yaml` to define the entire stack. The template engine in [helm/templates/_helpers.tpl](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl) provides helper functions that generate Kubernetes Deployments, Services, PVCs, ConfigMaps, and Secrets.

**Key Configuration Sections:**

  * `servingEngineSpec`: Global serving engine settings and `modelSpec` array for multi-model deployments
  * `routerSpec`: Router configuration including service discovery, routing logic, and observability settings
  * `loraController` and `loraAdapters`: LoRA adapter management
  * `cacheserverSpec`: Remote shared cache configuration

The chart generates resources using standard Kubernetes manifests:

  * [helm/templates/deployment-vllm-multi.yaml1-523](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L1-L523) creates serving engine Deployments
  * [helm/templates/deployment-router.yaml1-200](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-router.yaml#L1-L200) creates router Deployment
  * [helm/templates/secrets.yaml1-32](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/secrets.yaml#L1-L32) manages sensitive credentials

**Sources:** [helm/values.yaml1-739](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L1-L739) [helm/README.md1-28](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/README.md?plain=1#L1-L28) [helm/templates/_helpers.tpl1-292](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl#L1-L292)

### Operator-based Deployment

The Operator approach uses Kubernetes Custom Resources that are reconciled by controller processes. This enables declarative management with automatic reconciliation, health monitoring, and update handling through Kubernetes-native patterns.

For details on CRD-based deployment, see [Kubernetes Operator](/vllm-project/production-stack/10-kubernetes-operator).

**Sources:** [README.md58-88](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L58-L88) [docs/source/deployment/index.rst1-26](https://github.com/vllm-project/production-stack/blob/99ab33ab/docs/source/deployment/index.rst#L1-L26)

## Core Components

### Serving Engines

Serving engines are vLLM inference pods that execute model inference using GPU acceleration. Each serving engine is configured through `servingEngineSpec.modelSpec[]` entries in the Helm values.

**Serving Engine Configuration Mapping**

Each `modelSpec` entry defines:

  * **Image:** `repository` and `tag` specify the vLLM container image (e.g., `lmcache/vllm-openai:latest`)
  * **Model:** `modelURL` points to the Hugging Face model ID (e.g., `facebook/opt-125m`)
  * **Resources:** `requestCPU`, `requestMemory`, `requestGPU` define resource requirements
  * **Replicas:** `replicaCount` sets horizontal scaling
  * **vLLM Settings:** `vllmConfig` map containing `enablePrefixCaching`, `maxModelLen`, `tensorParallelSize`, `gpuMemoryUtilization`, etc.
  * **Storage:** `pvcStorage` requests persistent volume for model weights

The template at [helm/templates/deployment-vllm-multi.yaml111-206](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L111-L206) constructs the vLLM command line:

Health checks use probes defined in [helm/values.yaml269-312](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L269-L312):

  * `startupProbe`: HTTP GET on `/health` endpoint
  * `livenessProbe`: Ensures container is running
  * `readinessProbe`: Indicates readiness to serve traffic

**Sources:** [helm/values.yaml4-256](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L4-L256) [helm/templates/deployment-vllm-multi.yaml1-523](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L1-L523) [helm/values.schema.json59-525](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.schema.json#L59-L525)

### Router

The router is a FastAPI application that acts as the intelligent request distributor. It implements service discovery, routing algorithms, metrics collection, and model aliasing.

**Router Implementation Details:**

The router is deployed via [helm/templates/deployment-router.yaml1-200](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-router.yaml#L1-L200) and configured through `routerSpec` in values.yaml. Key configuration parameters:

  * **Service Discovery:** `serviceDiscovery` mode (`k8s` or `static`) 
    * `k8s` mode: Discovers backends using Kubernetes API with label selectors
    * `static` mode: Uses comma-separated `staticBackends` and `staticModels`
  * **Discovery Type:** `k8sServiceDiscoveryType` (`pod-ip` or `service-name`)
  * **Routing Logic:** `routingLogic` determines request distribution strategy: 
    * `roundrobin`: Load balance across all backends
    * `session`: Sticky routing based on `sessionKey` header (e.g., `x-user-id`)
    * `kvaware`: Routes to instances with highest KV cache hit probability
    * `prefixaware`: Routes requests with similar prefixes to same backend
    * `disaggregated_prefill`: Separates prefill and decode workloads

The router deployment arguments are constructed at [helm/templates/deployment-router.yaml100-156](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-router.yaml#L100-L156):

**Router Service Exposure:**

The router is exposed as a Kubernetes Service with type configured by `routerSpec.serviceType`:

  * `ClusterIP` (default): Internal cluster access only
  * `NodePort`: Exposes on fixed port across all nodes (configurable via `routerSpec.nodePort`)
  * `LoadBalancer`: Cloud provider load balancer

Ingress and Gateway API support are configured via `routerSpec.ingress` and `routerSpec.route` respectively, as defined in [helm/values.yaml489-554](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L489-L554)

**Sources:** [helm/values.yaml367-607](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L367-L607) [helm/templates/deployment-router.yaml1-200](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-router.yaml#L1-L200) [README.md112-123](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L112-L123)

### Observability Stack

The observability layer provides metrics collection, visualization, and distributed tracing capabilities.

**Observability Configuration Mapping**

**Metrics Collection:**

  * Router exports metrics via `prometheus-client` Python library
  * Engine metrics scraped from vLLM's native `/metrics` endpoint
  * Scrape interval configured via `routerSpec.engineScrapeInterval` (default 15 seconds)
  * Request statistics window set by `routerSpec.requestStatsWindow` (default 60 seconds)

**Key Metrics Exposed:**

  * QPS per instance
  * Request latency distribution
  * Time-to-First-Token (TTFT)
  * Number of running/pending/swapped requests
  * GPU KV cache usage percentage
  * Prefix cache hit rate

**Distributed Tracing:** OpenTelemetry tracing is enabled when `routerSpec.otel.endpoint` is configured:

Configuration at [helm/values.yaml456-464](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L456-L464) and command-line arguments at [helm/templates/deployment-router.yaml148-156](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-router.yaml#L148-L156)

**Autoscaling with KEDA:** Per-model autoscaling is configured via `modelSpec[].keda`:

Schema defined in [helm/values.schema.json408-512](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.schema.json#L408-L512)

**Sources:** [helm/values.yaml450-464](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L450-L464) [helm/values.yaml127-154](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L127-L154) [README.md89-109](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L89-L109) [observability/README.md (referenced)](https://github.com/vllm-project/production-stack/blob/99ab33ab/observability/README.md \(referenced\))

## Key Capabilities

### Multi-Model Serving

The `modelSpec` array in `servingEngineSpec` enables deploying multiple models in a single Helm release. Each entry creates an independent Deployment with dedicated pods, services, and resources.

**Configuration Pattern:**

Each model gets:

  * Unique Deployment: `{{ .Release.Name }}-{{ modelName }}-deployment-vllm`
  * Unique Service: `{{ .Release.Name }}-{{ modelName }}-engine-service`
  * Unique PVC (if `pvcStorage` specified): `{{ .Release.Name }}-{{ modelName }}-storage-claim`

The router's service discovery automatically detects all serving engines matching the label selector and exposes them through the `/v1/models` endpoint.

**Sources:** [helm/values.yaml19-256](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L19-L256) [helm/templates/deployment-vllm-multi.yaml2-3](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L2-L3)

### Request Routing Strategies

Five routing algorithms are implemented:

Algorithm| Configuration| Behavior| Use Case  
---|---|---|---  
`roundrobin`| `routingLogic: "roundrobin"`| Distributes requests evenly across backends| Default load balancing  
`session`| `routingLogic: "session"`  
`sessionKey: "x-user-id"`| Routes requests with same session key to same backend| User session affinity, conversation continuity  
`kvaware`| `routingLogic: "kvaware"`| Routes to backend with highest KV cache hit probability| Maximize cache reuse for similar requests  
`prefixaware`| `routingLogic: "prefixaware"`| Routes requests with similar prompt prefixes together| Optimize prefix caching  
`disaggregated_prefill`| `routingLogic: "disaggregated_prefill"`| Separates prefill and decode to different instances| Hardware specialization, throughput optimization  
  
Configuration at [helm/values.yaml436-440](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L436-L440)

**Sources:** [helm/values.yaml436-440](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L436-L440) [README.md119-122](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L119-L122)

### KV Cache Management

The LMCache integration provides multi-tier KV cache offloading:

**Three-Tier Cache Hierarchy:**

  1. **GPU Cache:** Primary cache, fastest access
  2. **CPU Cache:** Configured via `lmcacheConfig.cpuOffloadingBufferSize` (in GB)
  3. **Disk Cache:** Configured via `lmcacheConfig.diskOffloadingBufferSize` (in GB)

**Remote Shared Cache:** Optional cache server enables KV cache sharing across pods:

  * Deployed when `cacheserverSpec` is defined
  * Uses `lm://` protocol with configurable serialization (`naive` or `cachegen`)
  * Environment variable `LMCACHE_REMOTE_URL` injected into serving pods

**Configuration Example:**

Cache-related environment variables are set at [helm/templates/deployment-vllm-multi.yaml265-368](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L265-L368)

**Sources:** [helm/values.yaml91-95](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L91-L95) [helm/templates/deployment-vllm-multi.yaml188-201](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L188-L201) [helm/templates/deployment-vllm-multi.yaml265-368](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L265-L368)

### LoRA Adapter Management

Dynamic LoRA adapter loading is supported through two mechanisms:

**1\. Helm-based Configuration:**

**2\. Controller-based Management:** When `loraController.enableLoraController: true`, a dedicated controller pod manages adapter lifecycle:

  * Image: `lmcache/lmstack-lora-controller:latest`
  * Handles adapter downloads, placement, and API calls to vLLM
  * Configured at [helm/values.yaml654-736](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L654-L736)

**Requirements:**

  * Serving engine must have `enableLoRA: true` in modelSpec
  * `VLLM_ALLOW_RUNTIME_LORA_UPDATING` environment variable enables runtime updates
  * Shared PVC with `ReadWriteMany` access mode for adapter storage

**Sidecar Pattern:** When LoRA is enabled, a sidecar container (`lmcache/lmstack-sidecar:latest`) runs alongside the vLLM container:

  * Listens on port 30090
  * Manages adapter downloads to `/data/lora-adapters`
  * Configuration at [helm/templates/deployment-vllm-multi.yaml422-434](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L422-L434)

**Sources:** [helm/values.yaml608-653](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L608-L653) [helm/values.yaml654-736](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L654-L736) [helm/templates/deployment-vllm-multi.yaml422-434](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L422-L434)

### Authentication and Security

**API Key Authentication:** Secure vLLM endpoints using `vllmApiKey` configuration:

The Helm chart handles secret management:

  * String values are base64-encoded and stored in generated Secret `{{ .Release.Name }}-secrets`
  * Secret references point to existing Kubernetes Secrets
  * Environment variable `VLLM_API_KEY` injected into both router and serving engine pods

Implementation at [helm/templates/secrets.yaml9-12](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/secrets.yaml#L9-L12) and [helm/templates/deployment-vllm-multi.yaml244-258](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L244-L258)

**Hugging Face Token Management:** Per-model HF tokens for private model access:

Token stored as `hf_token_{{ modelName }}` in secrets and mounted as `HF_TOKEN` environment variable at [helm/templates/deployment-vllm-multi.yaml230-243](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L230-L243)

**Security Context:** Pod and container security contexts configurable via:

  * `servingEngineSpec.securityContext`: Pod-level security
  * `servingEngineSpec.containerSecurityContext`: Container-level security
  * `routerSpec.securityContext` and `routerSpec.containerSecurityContext`: Router security

Default container security includes `runAsNonRoot: false` to support GPU access requirements.

**Sources:** [helm/values.yaml13-18](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L13-L18) [helm/templates/secrets.yaml1-32](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/secrets.yaml#L1-L32) [helm/values.yaml331-361](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L331-L361) [helm/values.yaml375-379](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L375-L379)

## Configuration Schema

The Helm chart enforces configuration schema validation via [helm/values.schema.json](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.schema.json) which defines:

  * Required fields for `modelSpec` entries (name, repository, tag, modelURL, replicaCount, requestCPU, requestMemory, requestGPU, pvcStorage)
  * Valid enumerations for routing logic, service discovery modes, and other categorical values
  * Type constraints for all configuration parameters
  * Nested object structures for complex configurations like KEDA autoscaling

Schema validation occurs during `helm install` and `helm upgrade` operations, preventing misconfigured deployments.

**Sources:** [helm/values.schema.json1-1454](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.schema.json#L1-L1454)

## Resource Management

### Storage Configuration

**Persistent Volume Claims:** Each model can request dedicated storage via `pvcStorage`:

PVC generation at [helm/templates/pvc.yaml](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/pvc.yaml) (referenced but not in provided files).

**Shared Storage for LoRA:**

Mounted at `/data/shared-pvc-storage` in pods that need shared access to LoRA adapters.

**emptyDir for Shared Memory:** When `tensorParallelSize > 1`, shared memory volume created:

Configuration at [helm/templates/deployment-vllm-multi.yaml459-463](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L459-L463)

**Sources:** [helm/values.yaml49-53](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L49-L53) [helm/templates/deployment-vllm-multi.yaml442-478](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/deployment-vllm-multi.yaml#L442-L478)

### Resource Requests and Limits

Two configuration approaches:

**1\. Simplified Resource Fields:**

**2\. Standard Kubernetes Resources Block:**

The `resources` block takes precedence when both are specified. Resource template at [helm/templates/_helpers.tpl164-207](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl#L164-L207) constructs the final resources specification.

**GPU Memory Management (HAMi):** For clusters with HAMi GPU sharing:

**Sources:** [helm/values.yaml34-47](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L34-L47) [helm/templates/_helpers.tpl164-207](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl#L164-L207) [helm/values.schema.json121-187](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.schema.json#L121-L187)

## Deployment Lifecycle

### Installation

### Updates and Rollouts

Deployment strategies configured via `servingEngineSpec.strategy` and `routerSpec.strategy`:

Default strategy at [helm/templates/_helpers.tpl38-47](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl#L38-L47) uses rolling updates with zero downtime.

### Health Checks

Three probe types ensure pod health:

  * **Startup Probe:** Allows long initialization times (default 60 failures × 10s = 10 minutes)
  * **Liveness Probe:** Restarts unhealthy containers
  * **Readiness Probe:** Controls Service endpoint membership

All probes use HTTP GET on `/health` endpoint at port 8000. Configuration at [helm/values.yaml269-312](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L269-L312) and template generation at [helm/templates/_helpers.tpl86-150](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl#L86-L150)

**Sources:** [helm/templates/_helpers.tpl38-63](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/templates/_helpers.tpl#L38-L63) [helm/values.yaml269-312](https://github.com/vllm-project/production-stack/blob/99ab33ab/helm/values.yaml#L269-L312)

## Next Steps

  * For step-by-step deployment guide, see [Getting Started](/vllm-project/production-stack/3-getting-started) and [Minimal Installation](/vllm-project/production-stack/3.2-minimal-installation)
  * For complete configuration reference, see [Helm Chart Deployment](/vllm-project/production-stack/4-helm-chart-deployment) and [Values Reference](/vllm-project/production-stack/4.1-values-reference)
  * For router architecture and routing algorithms, see [vLLM Router](/vllm-project/production-stack/5-vllm-router)
  * For cache optimization strategies, see [Caching and Optimization](/vllm-project/production-stack/6-caching-and-optimization)
  * For production monitoring setup, see [Observability](/vllm-project/production-stack/7-observability)
  * For advanced features like LoRA and disaggregated inference, see [Advanced Features](/vllm-project/production-stack/8-advanced-features)
  * For operator-based deployment, see [Kubernetes Operator](/vllm-project/production-stack/10-kubernetes-operator)

**Sources:** [README.md28-37](https://github.com/vllm-project/production-stack/blob/99ab33ab/README.md?plain=1#L28-L37) [tutorials/README.md1-40](https://github.com/vllm-project/production-stack/blob/99ab33ab/tutorials/README.md?plain=1#L1-L40)
