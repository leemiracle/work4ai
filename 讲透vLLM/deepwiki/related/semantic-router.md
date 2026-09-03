# semantic-router

> 来源: https://deepwiki.com/vllm-project/semantic-router 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [.github/ISSUE_TEMPLATE/001_feature_request.yaml](https://github.com/vllm-project/semantic-router/blob/5d186b58/.github/ISSUE_TEMPLATE/001_feature_request.yaml)
  * [.github/ISSUE_TEMPLATE/002_bug_report.yaml](https://github.com/vllm-project/semantic-router/blob/5d186b58/.github/ISSUE_TEMPLATE/002_bug_report.yaml)
  * [.github/ISSUE_TEMPLATE/config.yml](https://github.com/vllm-project/semantic-router/blob/5d186b58/.github/ISSUE_TEMPLATE/config.yml)
  * [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/vllm-project/semantic-router/blob/5d186b58/.github/PULL_REQUEST_TEMPLATE.md?plain=1)
  * [CONTRIBUTING.md](https://github.com/vllm-project/semantic-router/blob/5d186b58/CONTRIBUTING.md?plain=1)
  * [README.md](https://github.com/vllm-project/semantic-router/blob/5d186b58/README.md?plain=1)
  * [config/config.yaml](https://github.com/vllm-project/semantic-router/blob/5d186b58/config/config.yaml)
  * [src/semantic-router/pkg/classification/classifier.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/classification/classifier.go)
  * [src/semantic-router/pkg/config/config.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go)
  * [src/semantic-router/pkg/config/config_test.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config_test.go)
  * [src/semantic-router/pkg/decision/engine.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/decision/engine.go)
  * [src/semantic-router/pkg/decision/engine_empty_and_test.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/decision/engine_empty_and_test.go)
  * [src/semantic-router/pkg/extproc/processor_req_body.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_body.go)
  * [src/semantic-router/pkg/extproc/processor_req_header.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_header.go)
  * [src/semantic-router/pkg/extproc/processor_res_body.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_res_body.go)
  * [src/semantic-router/pkg/extproc/processor_res_header.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_res_header.go)
  * [src/semantic-router/pkg/extproc/req_filter_classification.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/req_filter_classification.go)
  * [src/semantic-router/pkg/extproc/router.go](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/router.go)
  * [website/docs/intro.md](https://github.com/vllm-project/semantic-router/blob/5d186b58/website/docs/intro.md?plain=1)
  * [website/docs/overview/semantic-router-overview.md](https://github.com/vllm-project/semantic-router/blob/5d186b58/website/docs/overview/semantic-router-overview.md?plain=1)
  * [website/docs/proposals/prompt-classification-routing.md](https://github.com/vllm-project/semantic-router/blob/5d186b58/website/docs/proposals/prompt-classification-routing.md?plain=1)
  * [website/static/img/banner.png](https://github.com/vllm-project/semantic-router/blob/5d186b58/website/static/img/banner.png)
  * [website/static/img/level.png](https://github.com/vllm-project/semantic-router/blob/5d186b58/website/static/img/level.png)

The **vLLM Semantic Router** is a signal-driven intelligent routing system for Large Language Model (LLM) inference workloads. It operates as an Envoy External Processing (ExtProc) filter that intercepts OpenAI-compatible HTTP requests (`/v1/chat/completions`) and applies routing logic based on 20+ signal families extracted from request content, headers, and context [src/semantic-router/pkg/config/config.go24-45](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L24-L45) [README.md23-25](https://github.com/vllm-project/semantic-router/blob/5d186b58/README.md?plain=1#L23-L25)

The core implementation is a Go gRPC service (`OpenAIRouter`) at [src/semantic-router/pkg/extproc/router.go27-61](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/router.go#L27-L61) that implements the `ext_proc.ExternalProcessorServer` interface. This service receives `ProcessingRequest` messages from Envoy at four lifecycle phases: request headers, request body, response headers, and response body. At each phase, the router can inspect, modify, or short-circuit the request flow [src/semantic-router/pkg/extproc/processor_req_header.go21-59](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_header.go#L21-L59) [src/semantic-router/pkg/extproc/processor_req_body.go29-97](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_body.go#L29-L97)

The system delivers three core values [README.md27-31](https://github.com/vllm-project/semantic-router/blob/5d186b58/README.md?plain=1#L27-L31):

  1. **Token Economics** : Reduce wasted tokens and maximize the value of every token through efficient model selection and semantic caching.
  2. **LLM Safety** : Detect jailbreaks, sensitive PII leakage, and hallucinations so agents remain controllable, trustworthy, and auditable.
  3. **Fullmesh Intelligence** : Coordinate local, private, and frontier models across cost, privacy, and capability boundaries.

For a detailed enumeration of capabilities, see [Key Features and Capabilities](/vllm-project/semantic-router/1.1-key-features-and-capabilities). For system architecture deep-dives, see [System Architecture at a Glance](/vllm-project/semantic-router/1.2-system-architecture-at-a-glance). For theoretical foundations, see [White Paper and Research](/vllm-project/semantic-router/1.3-white-paper-and-research).

**Sources:** [README.md19-32](https://github.com/vllm-project/semantic-router/blob/5d186b58/README.md?plain=1#L19-L32) [src/semantic-router/pkg/config/config.go24-45](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L24-L45) [src/semantic-router/pkg/extproc/processor_req_body.go29-97](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_body.go#L29-L97)

## High-Level Architecture

The router implements a multi-layer architecture: client interfaces → Envoy proxy → Go ExtProc service → backend model endpoints. The Go service delegates ML inference to specialized Rust libraries via FFI.

**Title: Component Mapping from Natural Language to Code Entities**

**Component Descriptions:**

Component| File Path| Responsibility  
---|---|---  
`OpenAIRouter`| [src/semantic-router/pkg/extproc/router.go27-61](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/router.go#L27-L61)| Main ExtProc server struct implementing `ExternalProcessorServer`.  
`Classifier`| [src/semantic-router/pkg/classification/classifier.go10-79](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/classification/classifier.go#L10-L79)| Orchestrates signal evaluation across 20+ signal families.  
`RouterConfig`| [src/semantic-router/pkg/config/config.go59-89](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L59-L89)| Central configuration structure for routing, models, and signals.  
`candle-binding`| [CONTRIBUTING.md105](https://github.com/vllm-project/semantic-router/blob/5d186b58/CONTRIBUTING.md?plain=1#L105-L105)| Rust crate dependency for BERT/LoRA/mmBERT classification via FFI.  
`ModelSelector`| [src/semantic-router/pkg/extproc/req_filter_classification.go73](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/req_filter_classification.go#L73-L73)| Registry of model selection algorithms (Elo, RouterDC, etc.).  
  
The system uses a canonical YAML contract (`v0.3`) across all deployment modes [config/config.yaml1-20](https://github.com/vllm-project/semantic-router/blob/5d186b58/config/config.yaml#L1-L20)

**Sources:** [src/semantic-router/pkg/extproc/router.go27-61](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/router.go#L27-L61) [src/semantic-router/pkg/config/config.go59-89](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L59-L89) [config/config.yaml1-20](https://github.com/vllm-project/semantic-router/blob/5d186b58/config/config.yaml#L1-L20)

## Signal Extraction and Decision Evaluation

The router evaluates requests using signal families defined in the configuration. Each signal type has a corresponding classifier that outputs matched rule names and confidence scores.

**Title: Signal Extraction Pipeline from Request to Decision**

**Signal Categories:**

The router extracts 20+ maintained signal families defined as constants in the configuration package [src/semantic-router/pkg/config/config.go24-45](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L24-L45):

  * **Heuristic** : `keyword`, `language`, `context`, `structure`, `authz`.
  * **Learned/ML** : `embedding`, `domain`, `complexity`, `modality`, `jailbreak`, `pii`, `fact_check`, `user_feedback`, `reask`, `preference`, `kb`, `projection`, `conversation`, `event`.

For details on how these signals drive routing logic, see [Key Features and Capabilities](/vllm-project/semantic-router/1.1-key-features-and-capabilities).

**Sources:** [src/semantic-router/pkg/config/config.go24-45](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L24-L45) [src/semantic-router/pkg/extproc/req_filter_classification.go21-130](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/req_filter_classification.go#L21-L130)

## Request Processing Pipeline

The `OpenAIRouter` implements the four-phase Envoy ExtProc protocol: request headers → request body → response headers → response body [src/semantic-router/pkg/extproc/processor_req_header.go21-59](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_header.go#L21-L59) [src/semantic-router/pkg/extproc/processor_req_body.go29-97](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_body.go#L29-L97)

### ExtProc Four-Phase Flow

For a deeper dive into the pipeline, see [System Architecture at a Glance](/vllm-project/semantic-router/1.2-system-architecture-at-a-glance).

**Sources:** [src/semantic-router/pkg/extproc/processor_req_header.go21-59](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_header.go#L21-L59) [src/semantic-router/pkg/extproc/processor_req_body.go29-141](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_body.go#L29-L141) [src/semantic-router/pkg/extproc/req_filter_classification.go21-64](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/req_filter_classification.go#L21-L64)

## Deployment and Operations

The system is designed for production environments using modern container orchestration and hardware acceleration.

  * **Config Sources** : Configuration can be loaded from local files or Kubernetes CRDs [src/semantic-router/pkg/config/config.go6-11](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L6-L11)
  * **AMD ROCm** : Specialized support for AMD GPUs via ROCm is provided for training and inference [README.md121-125](https://github.com/vllm-project/semantic-router/blob/5d186b58/README.md?plain=1#L121-L125) [CONTRIBUTING.md41-46](https://github.com/vllm-project/semantic-router/blob/5d186b58/CONTRIBUTING.md?plain=1#L41-L46)
  * **Kubernetes** : Deployment is supported via Helm charts and a dedicated Kubernetes Operator.
  * **Observability** : The router integrates with OpenTelemetry for tracing and Prometheus for metrics [src/semantic-router/pkg/extproc/processor_req_header.go10-18](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_header.go#L10-L18) [src/semantic-router/pkg/extproc/processor_req_body.go11-13](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/extproc/processor_req_body.go#L11-L13)

**Sources:** [README.md121-125](https://github.com/vllm-project/semantic-router/blob/5d186b58/README.md?plain=1#L121-L125) [src/semantic-router/pkg/config/config.go6-11](https://github.com/vllm-project/semantic-router/blob/5d186b58/src/semantic-router/pkg/config/config.go#L6-L11) [CONTRIBUTING.md41-46](https://github.com/vllm-project/semantic-router/blob/5d186b58/CONTRIBUTING.md?plain=1#L41-L46)
