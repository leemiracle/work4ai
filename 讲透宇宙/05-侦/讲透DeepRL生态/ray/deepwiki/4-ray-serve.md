> 来源: [https://deepwiki.com/ray-project/ray/4-ray-serve](https://deepwiki.com/ray-project/ray/4-ray-serve)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Ray Serve

  Relevant source files 
 - [doc/source/serve/advanced-guides/advanced-autoscaling.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/advanced-guides/advanced-autoscaling.md?plain=1)
 - [doc/source/serve/api/index.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/api/index.md?plain=1)
 - [doc/source/serve/doc_code/application_level_autoscaling.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/doc_code/application_level_autoscaling.py)
 - [doc/source/serve/doc_code/application_level_autoscaling.yaml](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/doc_code/application_level_autoscaling.yaml)
 - [doc/source/serve/doc_code/autoscaling_policy.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/doc_code/autoscaling_policy.py)
 - [doc/source/serve/doc_code/custom_metrics_autoscaling.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/doc_code/custom_metrics_autoscaling.py)
 - [doc/source/serve/doc_code/scheduled_batch_processing.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/doc_code/scheduled_batch_processing.py)
 - [doc/source/serve/monitoring.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/monitoring.md?plain=1)
 - [python/ray/dashboard/modules/serve/tests/test_serve_dashboard.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/serve/tests/test_serve_dashboard.py)
 - [python/ray/includes/timeseries_utils.pxi](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/timeseries_utils.pxi)
 - [python/ray/llm/tests/serve/cpu/deployments/routers/test_make_fastapi_ingress.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/llm/tests/serve/cpu/deployments/routers/test_make_fastapi_ingress.py)
 - [python/ray/serve/_private/application_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/application_state.py)
 - [python/ray/serve/_private/autoscaling_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/autoscaling_state.py)
 - [python/ray/serve/_private/client.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/client.py)
 - [python/ray/serve/_private/common.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/common.py)
 - [python/ray/serve/_private/config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/config.py)
 - [python/ray/serve/_private/constants.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/constants.py)
 - [python/ray/serve/_private/controller.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/controller.py)
 - [python/ray/serve/_private/deploy_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/deploy_utils.py)
 - [python/ray/serve/_private/deployment_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/deployment_state.py)
 - [python/ray/serve/_private/haproxy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/haproxy.py)
 - [python/ray/serve/_private/haproxy_metrics.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/haproxy_metrics.py)
 - [python/ray/serve/_private/haproxy_templates.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/haproxy_templates.py)
 - [python/ray/serve/_private/http_util.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/http_util.py)
 - [python/ray/serve/_private/ingress_request_router.lua.tmpl](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/ingress_request_router.lua.tmpl)
 - [python/ray/serve/_private/local_testing_mode.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/local_testing_mode.py)
 - [python/ray/serve/_private/metrics_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/metrics_utils.py)
 - [python/ray/serve/_private/proxy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/proxy.py)
 - [python/ray/serve/_private/proxy_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/proxy_state.py)
 - [python/ray/serve/_private/replica.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py)
 - [python/ray/serve/api.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/api.py)
 - [python/ray/serve/autoscaling_policy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/autoscaling_policy.py)
 - [python/ray/serve/config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/config.py)
 - [python/ray/serve/deployment.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/deployment.py)
 - [python/ray/serve/exceptions.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/exceptions.py)
 - [python/ray/serve/experimental/round_robin_router.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/experimental/round_robin_router.py)
 - [python/ray/serve/schema.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/schema.py)
 - [python/ray/serve/tests/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/BUILD.bazel)
 - [python/ray/serve/tests/test_api.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_api.py)
 - [python/ray/serve/tests/test_autoscaling_policy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_autoscaling_policy.py)
 - [python/ray/serve/tests/test_callback.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_callback.py)
 - [python/ray/serve/tests/test_cluster.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_cluster.py)
 - [python/ray/serve/tests/test_config_files/multi_fastapi.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_config_files/multi_fastapi.py)
 - [python/ray/serve/tests/test_controller.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_controller.py)
 - [python/ray/serve/tests/test_controller_recovery.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_controller_recovery.py)
 - [python/ray/serve/tests/test_deploy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_deploy.py)
 - [python/ray/serve/tests/test_deploy_2.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_deploy_2.py)
 - [python/ray/serve/tests/test_deploy_app.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_deploy_app.py)
 - [python/ray/serve/tests/test_deploy_app_2.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_deploy_app_2.py)
 - [python/ray/serve/tests/test_failure.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_failure.py)
 - [python/ray/serve/tests/test_fastapi.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_fastapi.py)
 - [python/ray/serve/tests/test_gcs_failure.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_gcs_failure.py)
 - [python/ray/serve/tests/test_haproxy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_haproxy.py)
 - [python/ray/serve/tests/test_haproxy_api.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_haproxy_api.py)
 - [python/ray/serve/tests/test_haproxy_metrics.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_haproxy_metrics.py)
 - [python/ray/serve/tests/test_metrics.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_metrics.py)
 - [python/ray/serve/tests/test_metrics_3.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_metrics_3.py)
 - [python/ray/serve/tests/test_multiplex.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_multiplex.py)
 - [python/ray/serve/tests/test_proxy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_proxy.py)
 - [python/ray/serve/tests/test_round_robin_router.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_round_robin_router.py)
 - [python/ray/serve/tests/test_runtime_env_2.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_runtime_env_2.py)
 - [python/ray/serve/tests/test_target_capacity.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_target_capacity.py)
 - [python/ray/serve/tests/unit/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/BUILD.bazel)
 - [python/ray/serve/tests/unit/test_application_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_application_state.py)
 - [python/ray/serve/tests/unit/test_autoscaling_policy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_autoscaling_policy.py)
 - [python/ray/serve/tests/unit/test_config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_config.py)
 - [python/ray/serve/tests/unit/test_deployment_class.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_deployment_class.py)
 - [python/ray/serve/tests/unit/test_deployment_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_deployment_state.py)
 - [python/ray/serve/tests/unit/test_haproxy_binary.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_haproxy_binary.py)
 - [python/ray/serve/tests/unit/test_haproxy_process_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_haproxy_process_manager.py)
 - [python/ray/serve/tests/unit/test_http_util.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_http_util.py)
 - [python/ray/serve/tests/unit/test_local_testing_mode.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_local_testing_mode.py)
 - [python/ray/serve/tests/unit/test_metrics_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_metrics_utils.py)
 - [python/ray/serve/tests/unit/test_proxy_state.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_proxy_state.py)
 - [python/ray/serve/tests/unit/test_round_robin_router.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_round_robin_router.py)
 - [python/ray/serve/tests/unit/test_schema.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_schema.py)
 - [python/ray/serve/tests/unit/test_user_callable_wrapper.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_user_callable_wrapper.py)
 - [src/ray/protobuf/serve.proto](https://github.com/ray-project/ray/blob/bf129559/src/ray/protobuf/serve.proto)
 
  
## Purpose and Scope

 Ray Serve is a scalable model serving platform for deploying and managing machine learning applications on Ray clusters. It provides HTTP and gRPC ingress capabilities, dynamic request routing, metrics-based autoscaling, and fault-tolerant deployment management. This document focuses on the core orchestration and data plane components:

 
 - **Deployment Management**: How deployments are created, updated, and monitored through the control plane.
 - **Request Routing**: How HTTP and gRPC requests are routed from proxies to replica actors.
 - **Autoscaling**: How metrics are collected and used to make scaling decisions.
 - **Fault Tolerance**: How state is persisted and recovered after failures.
 
 Ray Serve builds on Ray Core's actor and task execution model (see [Ray Core Infrastructure](https://deepwiki.com/ray-project/ray/2-ray-core-infrastructure)). All deployments run as Ray actors, and inter-deployment communication uses Ray's distributed object references.

 
---

 
## Architecture Overview

 Ray Serve implements a three-tier architecture consisting of a proxy layer for request ingestion, a control plane for orchestration, and a replica layer for executing user code.

 
### Three-Tier Architecture

 
```

```

 **Sources:** [python/ray/serve/_private/proxy.py135-156](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/proxy.py#L135-L156) [python/ray/serve/_private/controller.py127-150](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/controller.py#L127-L150) [python/ray/serve/_private/deployment_state.py1390-1410](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/deployment_state.py#L1390-L1410) [python/ray/serve/_private/replica.py503-530](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py#L503-L530)

 For details on low-level request processing and the data plane, see [Architecture and Request Processing](https://deepwiki.com/ray-project/ray/4.1-architecture-and-request-processing).

 
---

 
## Core Components

 
### ServeController: Central Orchestration

 The `ServeController` is a Ray actor that serves as the central orchestrator for the entire Serve cluster. It persists all hard state through checkpoints in the KVStore, enabling fault tolerance.

 
```

```

 **Key Responsibilities:**

 
 - **Application Lifecycle:** Manages deploying, updating, and deleting applications through `ApplicationStateManager` [python/ray/serve/_private/application_state.py16-20](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/application_state.py#L16-L20)
 - **Deployment Management:** Coordinates deployment replica counts and versions through `DeploymentStateManager` [python/ray/serve/_private/controller.py218-221](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/controller.py#L218-L221)
 - **Autoscaling Decisions:** Processes metrics from replicas and handles to make scaling decisions through `AutoscalingStateManager` [python/ray/serve/_private/controller.py229-231](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/controller.py#L229-L231)
 - **Endpoint Registration:** Maintains the route table through `EndpointState` and broadcasts updates via `LongPollHost` [python/ray/serve/_private/controller.py172-174](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/controller.py#L172-L174)
 - **Fault Tolerance:** Persists state to `RayInternalKVStore` and recovers from failures using checkpoints [python/ray/serve/_private/controller.py169-171](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/controller.py#L169-L171)
 
 **Sources:** [python/ray/serve/_private/controller.py127-186](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/controller.py#L127-L186) [python/ray/serve/_private/deployment_state.py1390-1420](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/deployment_state.py#L1390-L1420)

 
---

 
### Proxy Layer: HTTP and gRPC Request Handling

 The proxy layer consists of `GenericProxy` implementations for HTTP and gRPC protocols. Proxies run as Ray actors on nodes with replicas and route incoming requests to the appropriate deployment replicas.

 **Key Features:**

 
 - **Draining Support:** Proxies support graceful draining where they stop accepting new requests but finish ongoing ones before shutting down [python/ray/serve/_private/proxy.py192-209](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/proxy.py#L192-L209)
 - **Request Routing:** Uses `ProxyRouter` to match incoming paths or gRPC services to `DeploymentHandle` objects [python/ray/serve/_private/proxy.py164-166](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/proxy.py#L164-L166)
 - **High Availability:** Can integrate with `HAProxyManager` for advanced load balancing and health checking [python/ray/serve/_private/haproxy.py23-28](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/haproxy.py#L23-L28)
 
 **Sources:** [python/ray/serve/_private/proxy.py135-213](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/proxy.py#L135-L213) [python/ray/serve/_private/haproxy.py119-134](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/haproxy.py#L119-L134)

 
---

 
### Deployment State Management

 The `DeploymentStateManager` manages the lifecycle of all deployments in the cluster, including replica creation, updates, health checks, and scaling.

 
| Class | Location | Purpose |
|---|---|---|
| DeploymentStateManager | python/ray/serve/_private/deployment_state.py1390 | Orchestrates all deployments in the cluster. |
| DeploymentState | python/ray/serve/_private/deployment_state.py1940 | Maintains the target and actual state for a single deployment. |
| DeploymentReplica | python/ray/serve/_private/deployment_state.py2150 | Logic for managing an individual replica actor. |
| ActorReplicaWrapper | python/ray/serve/_private/deployment_state.py219 | Low-level Ray actor operations (remote calls, health checks). |

 **Sources:** [python/ray/serve/_private/deployment_state.py1390-2150](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/deployment_state.py#L1390-L2150) [python/ray/serve/tests/unit/test_deployment_state.py40-54](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/unit/test_deployment_state.py#L40-L54)

 
---

 
### Replica Execution: Running User Code

 The `ReplicaBase` actor (implemented via `create_replica_impl`) executes user-defined code. Each replica runs in its own Ray actor process and handles incoming requests through the `UserCallableWrapper`.

 **Key Features:**

 
 - **Concurrency Control:** Replicas use a `Semaphore` to limit concurrent requests based on the `max_ongoing_requests` configuration [python/ray/serve/_private/replica.py542-543](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py#L542-L543)
 - **Health Monitoring:** Implements periodic health checks via the `check_health` method, which can invoke user-defined health probes [python/ray/serve/_private/replica.py1077-1108](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py#L1077-L1108)
 - **Request Protocols:** Supports `StreamingHTTPRequest`, `gRPCRequest`, and `gRPCStreamingRequest` [python/ray/serve/_private/replica.py52-57](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py#L52-L57)
 
 **Sources:** [python/ray/serve/_private/replica.py503-610](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py#L503-L610) [python/ray/serve/_private/replica.py833-861](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py#L833-L861)

 
---

 
## Autoscaling and Metrics

 Ray Serve supports dynamic scaling based on request traffic metrics. The `AutoscalingStateManager` aggregates metrics pushed from replicas and handles to calculate the target number of replicas.

 **Key Metrics:**

 
 - `serve_deployment_queued_queries`: Requests waiting in the handle queue [python/ray/serve/tests/test_metrics.py142](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_metrics.py#L142-L142)
 - `serve_replica_processing_queries`: Requests currently being processed by replicas [python/ray/serve/tests/test_metrics.py151](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_metrics.py#L151-L151)
 - `serve_deployment_processing_latency_ms`: Distribution of request processing time [python/ray/serve/tests/test_metrics.py146](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_metrics.py#L146-L146)
 
 The autoscaling loop runs within the `ServeController` at intervals defined by `CONTROL_LOOP_INTERVAL_S` [python/ray/serve/_private/constants.py77-79](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/constants.py#L77-L79)

 For details on metrics-based autoscaling and the long-poll pub/sub mechanism, see [Architecture and Request Processing](https://deepwiki.com/ray-project/ray/4.1-architecture-and-request-processing).

 **Sources:** [python/ray/serve/_private/autoscaling_state.py10-27](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/autoscaling_state.py#L10-L27) [python/ray/serve/tests/test_metrics.py137-156](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/tests/test_metrics.py#L137-L156)

 
---

 
## LLM Serving

 Ray Serve provides specialized support for Large Language Models (LLMs) through the `LLMServer` and integration with high-performance engines like vLLM and SGLang.

 **Key Features:**

 
 - **OpenAI-Compatible API**: Serves LLMs with a standardized interface.
 - **KV Cache Transfer**: Optimizes multi-step reasoning via specialized transfer protocols (LMCache, NIXL).
 - **Multiplexing**: Supports LoRA adapter multiplexing for serving multiple fine-tuned versions of a model on a single base model instance.
 
 For details on LLM serving patterns and engine integrations, see [Ray Serve LLM](https://deepwiki.com/ray-project/ray/4.2-ray-serve-llm).

 **Sources:** [python/ray/serve/_private/replica.py19-30](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/_private/replica.py#L19-L30) [python/ray/serve/schema.py41-50](https://github.com/ray-project/ray/blob/bf129559/python/ray/serve/schema.py#L41-L50)
