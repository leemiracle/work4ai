> 来源: [https://deepwiki.com/xorbitsai/inference/2-system-architecture](https://deepwiki.com/xorbitsai/inference/2-system-architecture)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# System Architecture

  Relevant source files 
 - [xinference/_compat.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/_compat.py)
 - [xinference/api/restful_api.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py)
 - [xinference/client/restful/restful_client.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/restful/restful_client.py)
 - [xinference/client/tests/test_client.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/tests/test_client.py)
 - [xinference/constants.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py)
 - [xinference/core/autostart.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/autostart.py)
 - [xinference/core/cache_tracker.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/cache_tracker.py)
 - [xinference/core/event.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/event.py)
 - [xinference/core/launch_strategy.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/launch_strategy.py)
 - [xinference/core/model.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py)
 - [xinference/core/status_guard.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/status_guard.py)
 - [xinference/core/supervisor.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py)
 - [xinference/core/tests/test_launch_strategy.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_launch_strategy.py)
 - [xinference/core/tests/test_restful_api.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_restful_api.py)
 - [xinference/core/tests/test_types.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_types.py)
 - [xinference/core/tests/test_utils.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_utils.py)
 - [xinference/core/tests/test_virtual_env_manager.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_virtual_env_manager.py)
 - [xinference/core/tests/test_worker.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_worker.py)
 - [xinference/core/utils.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/utils.py)
 - [xinference/core/virtual_env_manager.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/virtual_env_manager.py)
 - [xinference/core/worker.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py)
 - [xinference/deploy/cmdline.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py)
 - [xinference/deploy/test/test_cmdline.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/test/test_cmdline.py)
 - [xinference/types.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/types.py)
 
  
## Purpose and Scope

 This document provides a comprehensive overview of Xinference's system architecture, describing the core components, their interactions, and deployment patterns. It covers the actor-based distributed system design, the layered architecture from API to inference engines, and the fundamental communication patterns.

 For specific subsystems:

 
 - Supervisor-worker coordination and health monitoring: see [Supervisor and Worker System](https://deepwiki.com/xorbitsai/inference/2.1-supervisor-and-worker-system)
 - Model actor lifecycle and request handling: see [Model Actor Framework](https://deepwiki.com/xorbitsai/inference/2.2-model-actor-framework)
 - End-to-end request processing: see [Request Flow and Lifecycle](https://deepwiki.com/xorbitsai/inference/2.3-request-flow-and-lifecycle)
 - Model storage and versioning: see [Model Registry and Cache Management](https://deepwiki.com/xorbitsai/inference/2.4-model-registry-and-cache-management)
 - GPU allocation strategies: see [GPU Resource Management](https://deepwiki.com/xorbitsai/inference/2.5-gpu-resource-management)
 
 
## Overall Architecture

 Xinference follows a layered, actor-based distributed architecture. The system is built on `xoscar`, an actor framework that enables distributed computation with location transparency.

 
### System Layers

 
```

```

 **Sources:** [xinference/api/restful_api.py160-210](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L210) [xinference/core/supervisor.py127-174](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L127-L174) [xinference/core/worker.py31-93](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L31-L93) [xinference/core/model.py204-258](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L204-L258)

 
### Core Components

 
| Component | File | Primary Responsibility |
|---|---|---|
| SupervisorActor | xinference/core/supervisor.py127-174 | Cluster coordination, worker management, model routing, and launch history |
| WorkerActor | xinference/core/worker.py31-118 | GPU allocation, model launching, subprocess management, and virtual environment setup |
| ModelActor | xinference/core/model.py204-258 | Model lifecycle, request handling, metrics tracking, and OOM handling |
| RESTfulAPI | xinference/api/restful_api.py160-215 | HTTP endpoints, request validation, authentication, and OpenAI compatibility |
| StatusGuardActor | xinference/core/status_guard.py | Model launch status tracking and state transitions |
| CacheTrackerActor | xinference/core/cache_tracker.py | Model version tracking and cache status across workers |
| EventCollectorActor | xinference/core/event.py | Event aggregation, reporting, and persistent event storage |

 **Sources:** [xinference/core/supervisor.py127-174](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L127-L174) [xinference/core/worker.py31-118](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L31-L118) [xinference/core/model.py204-258](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L204-L258) [xinference/api/restful_api.py160-215](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L215)

 
## Actor System Architecture

 Xinference uses `xoscar`'s actor model for distributed computation. All core components are actors that communicate via message passing, providing location transparency.

 
### Actor Hierarchy and Communication

 
```

```

 **Actor Communication Patterns:**

 
| Pattern | Implementation | Example |
|---|---|---|
| Actor Reference | await xo.actor_ref(address, uid) | xinference/api/restful_api.py94 xinference/core/supervisor.py179-186 |
| Actor Creation | await xo.create_actor(ActorClass, address, uid) | xinference/core/supervisor.py149-154 |
| Message Passing | await actor_ref.method_name(args) | xinference/api/restful_api.py1059 |
| Subprocess Isolation | await pool.append_sub_pool(env) | xinference/core/worker.py622-624 |

 **Sources:** [xinference/core/supervisor.py127-174](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L127-L174) [xinference/core/worker.py31-118](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L31-L118) [xinference/api/restful_api.py160-215](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L215)

 
## Deployment Architectures

 Xinference supports multiple deployment modes, each suited for different hardware scales.

 
### Local Deployment

 Single-process deployment combining supervisor and worker functionality. Suitable for development and single-machine inference.

 
```

```

 **Entry Point:** [xinference/deploy/cmdline.py95-124](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L95-L124) → `start_local_cluster()`
 **Implementation:** [xinference/deploy/local.py42-80](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L42-L80) → `_start_local_cluster()`

 **Sources:** [xinference/deploy/cmdline.py95-124](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L95-L124) [xinference/deploy/local.py42-80](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/local.py#L42-L80)

 
### Distributed Deployment

 Separate supervisor and worker nodes for production clusters. Enables horizontal scaling and fault isolation.

 
```

```

 **Supervisor Entry Point:** [xinference/deploy/cmdline.py232-250](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L232-L250) → `supervisor()`
 **Worker Entry Point:** [xinference/deploy/cmdline.py298-320](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L298-L320) → `worker()`

 **Sources:** [xinference/deploy/cmdline.py232-320](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py#L232-L320) [xinference/deploy/supervisor.py73-102](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/supervisor.py#L73-L102) [xinference/deploy/worker.py78-108](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/worker.py#L78-L108)

 
## Configuration and Constants

 Key configuration parameters defined in [xinference/constants.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py):

 
| Constant | Default | Description |
|---|---|---|
| XINFERENCE_DEFAULT_ENDPOINT_PORT | 9997 | RESTful API port (xinference/constants.py54) |
| XINFERENCE_HOME | ~/.xinference | Base directory (xinference/constants.py84) |
| XINFERENCE_CACHE_DIR | $HOME/cache | Model cache (xinference/constants.py85) |
| XINFERENCE_LOG_DIR | $HOME/logs | Logging directory (xinference/constants.py88-90) |
| XINFERENCE_AUTH_DIR | $HOME/auth | Authentication keys (xinference/constants.py93) |

 **Sources:** [xinference/constants.py54-93](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L54-L93)

 
## Health Monitoring and Fault Tolerance

 
### Health Check System

 Xinference maintains cluster stability through a bidirectional health monitoring system.

 
```

```

 **Configuration:**

 
| Variable | Default | Description |
|---|---|---|
| XINFERENCE_HEALTH_CHECK_INTERVAL | 5s | Interval between checks (xinference/constants.py26) |
| XINFERENCE_HEALTH_CHECK_FAILURE_THRESHOLD | 5 | Max failed checks (xinference/constants.py23-25) |
| XINFERENCE_DISABLE_HEALTH_CHECK | False | Disable logic (xinference/constants.py37) |

 **Sources:** [xinference/constants.py23-37](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L23-L37) [xinference/core/supervisor.py148-152](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L148-L152) [xinference/core/worker.py336-344](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L336-L344)

 
## Key Design Patterns

 
### 1. Actor Isolation Pattern

 Each model runs in an isolated subprocess via `xoscar` subpools. This ensures that a segmentation fault in one inference engine (e.g., `llama.cpp`) does not crash the `WorkerActor` or other models. **Implementation:** [xinference/core/worker.py610-624](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L610-L624)

 
### 2. Request Limiting Pattern

 The `ModelActor` uses the `@request_limit` decorator to manage concurrency. It tracks `_serve_count` and rejects requests if they exceed `_request_limits` to prevent OOM or extreme latency. **Implementation:** [xinference/core/model.py88-171](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L88-L171)

 
### 3. Virtual Environment Isolation

 Xinference can create isolated Python virtual environments for different inference engines (e.g., `vLLM` vs `SGLang`) to avoid dependency conflicts. **Implementation:** [xinference/core/virtual_env_manager.py26-67](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/virtual_env_manager.py#L26-L67) [xinference/core/worker.py130-212](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L130-L212)

 
### 4. OOM Recovery Pattern

 The `oom_check` decorator wraps inference calls. If a `torch.cuda.OutOfMemoryError` is caught, the actor triggers `_handle_oom_error` to release resources and notify the supervisor. **Implementation:** [xinference/core/model.py173-202](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L173-L202)

 **Sources:** [xinference/core/worker.py610-624](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py#L610-L624) [xinference/core/model.py88-202](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L88-L202) [xinference/core/virtual_env_manager.py26-67](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/virtual_env_manager.py#L26-L67)
