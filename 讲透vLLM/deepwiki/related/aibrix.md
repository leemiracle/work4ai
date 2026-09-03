# aibrix

> 来源: https://deepwiki.com/vllm-project/aibrix 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [CONTRIBUTING.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/CONTRIBUTING.md?plain=1)
  * [README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1)
  * [benchmarks/generator/dataset_generator/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/benchmarks/generator/dataset_generator/README.md?plain=1)
  * [benchmarks/scenarios/gateway/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/benchmarks/scenarios/gateway/README.md?plain=1)
  * [deployment/terraform/gcp/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/deployment/terraform/gcp/README.md?plain=1)
  * [deployment/terraform/gcp/docs.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/deployment/terraform/gcp/docs.md?plain=1)
  * [development/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/development/README.md?plain=1)
  * [development/tutorials/batch/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/development/tutorials/batch/README.md?plain=1)
  * [development/tutorials/podautoscaler/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/development/tutorials/podautoscaler/README.md?plain=1)
  * [docs/source/_static/.gitkeep](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/_static/.gitkeep)
  * [docs/source/assets/images/aibrix-architecture-v1.jpeg](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/assets/images/aibrix-architecture-v1.jpeg)
  * [docs/source/assets/images/cloud/lambda-cloud-installation.png](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/assets/images/cloud/lambda-cloud-installation.png)
  * [docs/source/assets/images/cloud/lambda-cloud-instance.png](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/assets/images/cloud/lambda-cloud-instance.png)
  * [docs/source/assets/images/cloud/lambda-cloud-ssh.png](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/assets/images/cloud/lambda-cloud-ssh.png)
  * [docs/source/assets/images/cloud/lambda-cloud-verify-installation.png](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/assets/images/cloud/lambda-cloud-verify-installation.png)
  * [docs/source/community/community.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/community/community.rst)
  * [docs/source/community/research.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/community/research.rst)
  * [docs/source/conf.py](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/conf.py)
  * [docs/source/designs/aibrix-kvcache-offloading-framework.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/designs/aibrix-kvcache-offloading-framework.rst)
  * [docs/source/designs/architecture.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/designs/architecture.rst)
  * [docs/source/development/development.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/development/development.rst)
  * [docs/source/development/release.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/development/release.rst)
  * [docs/source/features/batch-api.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/features/batch-api.rst)
  * [docs/source/features/batch-resource-manager.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/features/batch-resource-manager.rst)
  * [docs/source/getting_started/faq.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/faq.rst)
  * [docs/source/getting_started/installation/installation.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst)
  * [docs/source/getting_started/installation/lambda.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/lambda.rst)
  * [docs/source/getting_started/quickstart.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/quickstart.rst)
  * [docs/source/index.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/index.rst)
  * [docs/source/production/gateway.rst](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/production/gateway.rst)
  * [hack/lambda-cloud/setup.sh](https://github.com/vllm-project/aibrix/blob/e9866a6f/hack/lambda-cloud/setup.sh)
  * [python/aibrix/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/python/aibrix/README.md?plain=1)
  * [python/aibrix/aibrix/gpu_optimizer/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/python/aibrix/aibrix/gpu_optimizer/README.md?plain=1)
  * [python/aibrix_kvcache/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/python/aibrix_kvcache/README.md?plain=1)
  * [python/aibrix_kvcache/aibrix_kvcache/status.py](https://github.com/vllm-project/aibrix/blob/e9866a6f/python/aibrix_kvcache/aibrix_kvcache/status.py)
  * [scripts/port-forward.sh](https://github.com/vllm-project/aibrix/blob/e9866a6f/scripts/port-forward.sh)
  * [test/README.md](https://github.com/vllm-project/aibrix/blob/e9866a6f/test/README.md?plain=1)

## Purpose and Scope

This document introduces AIBrix, a cloud-native infrastructure for deploying and managing large language model (LLM) inference at scale on Kubernetes. It covers the system's purpose, key features, high-level architecture, and component organization.

For detailed information about specific subsystems:

  * Gateway routing and load balancing → [Gateway System](/vllm-project/aibrix/3-gateway-system)
  * Kubernetes controllers and lifecycle management → [Controller System](/vllm-project/aibrix/4-controller-system)
  * Python services and runtime components → [Python Runtime and Services](/vllm-project/aibrix/5-python-runtime-and-services)
  * Deployment and operations → [Deployment and Operations](/vllm-project/aibrix/6-deployment-and-operations)

**Sources:** [README.md1-90](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L1-L90) [docs/source/index.rst1-83](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/index.rst#L1-L83)

* * *

## What is AIBrix?

AIBrix is an open-source Kubernetes-native platform designed to provide production-grade building blocks for constructing scalable GenAI inference infrastructure. It delivers a complete solution for deploying, managing, and scaling LLM inference workloads, specifically optimized for enterprise environments running models like DeepSeek, Llama, and other large language models [README.md3-4](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L3-L4) [docs/source/index.rst9-11](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/index.rst#L9-L11)

The system operates as a middleware layer between Kubernetes and LLM inference engines (vLLM, SGLang), providing:

  * **Intelligent request routing** through Envoy Gateway with specialized algorithms [README.md34](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L34-L34)
  * **Dynamic resource management** via custom Kubernetes controllers [docs/source/getting_started/installation/installation.rst199-206](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L199-L206)
  * **Unified runtime abstraction** for multiple inference engines [docs/source/index.rst18](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/index.rst#L18-L18)
  * **Production-grade features** including autoscaling, distributed inference, and KV cache optimization [README.md28-40](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L28-L40)

AIBrix is deployed entirely within Kubernetes using standard APIs (Gateway API, Custom Resources) and does not require external dependencies beyond a Kubernetes cluster.

**Sources:** [README.md3-4](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L3-L4) [docs/source/index.rst9-11](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/index.rst#L9-L11)

* * *

## Key Features

AIBrix implements the following core capabilities:

Feature| Description| Component  
---|---|---  
**LLM Gateway and Routing**|  Traffic management with algorithms including prefix-cache, least-request, and PD disaggregation| `gateway-plugins`, AIBrix Router  
**High-Density LoRA Management**|  Dynamic loading/unloading of LoRA adapters with automatic orchestration| `ModelAdapter` Controller  
**LLM App-Tailored Autoscaler**|  Dynamic scaling (HPA, KPA, APA) with profile-based proactive scaling| `PodAutoscaler` Controller, `gpu-optimizer`  
**Unified AI Runtime**|  Versatile sidecar for model management, metrics standardization, and artifact delegation| `aibrix_runtime`  
**Distributed Inference**|  Scalable architecture for large workloads across multiple nodes| `DistributedInference` Controller  
**Distributed KV Cache**|  GPU-accelerated cache framework with cross-engine reuse and multi-tier storage| `aibrix-kvcache`, `KVCache` Controller  
**Heterogeneous GPU Serving**|  Cost-efficient mixed GPU inference with SLO guarantees| `GPU Optimizer`  
**GPU Hardware Failure Detection**|  Proactive detection of GPU hardware issues| AI Runtime health checks  
  
**Sources:** [README.md28-40](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L28-L40) [docs/source/index.rst12-23](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/index.rst#L12-L23)

* * *

## System Architecture

### High-Level Component View

AIBrix implements a layered architecture with clear separation between the gateway layer, control plane, and data plane:

**AIBrix Component Architecture**

**Sources:** [README.md41-43](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L41-L43) [docs/source/getting_started/installation/installation.rst199-206](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L199-L206)

* * *

### Request Processing Flow

AIBrix processes inference requests through three distinct phases: gateway processing, routing decision, and request forwarding.

**Request Processing Sequence Diagram**

**Sources:** [docs/source/production/gateway.rst55-93](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/production/gateway.rst#L55-L93) [docs/source/designs/aibrix-kvcache-offloading-framework.rst11-20](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/designs/aibrix-kvcache-offloading-framework.rst#L11-L20)

* * *

### Control Plane Organization

The control plane implements specialized controllers within a single binary (`controller-manager`), each managing distinct resource lifecycles.

**Control Plane Controller Architecture**

**Sources:** [docs/source/getting_started/installation/installation.rst184-206](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L184-L206) [docs/source/getting_started/quickstart.rst41-59](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/quickstart.rst#L41-L59)

* * *

## Component Overview

### Gateway Layer Components

  * **`gateway-plugins`** ([pkg/gateway](https://github.com/vllm-project/aibrix/blob/e9866a6f/pkg/gateway)): gRPC server implementing Envoy's External Processing protocol for rate limiting and routing delegation [docs/source/production/gateway.rst15-18](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/production/gateway.rst#L15-L18)
  * **`AIBrix Router`** : Pluggable framework with algorithms like `prefix-cache`, `least-request`, and `pd` [docs/source/getting_started/quickstart.rst112-117](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/quickstart.rst#L112-L117) [docs/source/production/gateway.rst89-93](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/production/gateway.rst#L89-L93)
  * **Envoy Gateway** : Configured via Gateway API with `EnvoyPatchPolicy` enabled [docs/source/getting_started/installation/installation.rst41-65](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L41-L65)

### Control Plane Components

  * **`controller-manager`** ([cmd/controller-manager](https://github.com/vllm-project/aibrix/blob/e9866a6f/cmd/controller-manager)): Single binary hosting multiple controllers, registered via flags [docs/source/getting_started/installation/installation.rst189-206](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L189-L206)
  * **ModelRouter** : Automatically creates `HTTPRoute` resources for model deployments [docs/source/getting_started/faq.rst43-65](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/faq.rst#L43-L65)
  * **PodAutoscaler** : Implements HPA, KPA, and APA strategies [docs/source/getting_started/installation/installation.rst206](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L206-L206)
  * **StormService** : Orchestrates disaggregated prefill-decode deployments [docs/source/getting_started/installation/installation.rst210](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L210-L210)

### Python Services and Runtime

  * **`metadata-service`** : FastAPI service for user management and rate limiting [docs/source/getting_started/quickstart.rst34](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/quickstart.rst#L34-L34)
  * **`gpu-optimizer`** : Profile-based autoscaling logic [docs/source/getting_started/quickstart.rst32](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/quickstart.rst#L32-L32)
  * **`aibrix_runtime`** : Sidecar for engine abstraction (vLLM/SGLang) and adapter management [docs/source/index.rst18](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/index.rst#L18-L18)
  * **`aibrix-kvcache`** : High-performance KV offloading framework [docs/source/designs/aibrix-kvcache-offloading-framework.rst11-12](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/designs/aibrix-kvcache-offloading-framework.rst#L11-L12)

* * *

## Deployment and Operations

AIBrix is deployed via Kubernetes manifests or Helm charts.

### Installation Methods

  * **Raw YAML** : Stable distributions available on GitHub releases [README.md66-76](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L66-L76)
  * **Helm** : Recommended for production, managing dependencies like Envoy Gateway [docs/source/getting_started/installation/installation.rst35-120](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L35-L120)
  * **Nightly** : Direct installation from the repository for development [README.md51-64](https://github.com/vllm-project/aibrix/blob/e9866a6f/README.md?plain=1#L51-L64)

### Production Considerations

  * **Redis** : Required for cross-replica state synchronization in multi-replica gateway deployments [docs/source/production/gateway.rst55-71](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/production/gateway.rst#L55-L71)
  * **Resource Sizing** : Recommendations for Gateway Plugin and Envoy Proxy CPU/Memory allocations [docs/source/production/gateway.rst9-54](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/production/gateway.rst#L9-L54)

**Sources:** [docs/source/getting_started/installation/installation.rst1-206](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/getting_started/installation/installation.rst#L1-L206) [docs/source/production/gateway.rst1-180](https://github.com/vllm-project/aibrix/blob/e9866a6f/docs/source/production/gateway.rst#L1-L180)
