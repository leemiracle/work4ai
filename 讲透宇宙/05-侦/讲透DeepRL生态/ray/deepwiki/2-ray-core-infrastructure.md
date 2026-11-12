> 来源: [https://deepwiki.com/ray-project/ray/2-ray-core-infrastructure](https://deepwiki.com/ray-project/ray/2-ray-core-infrastructure)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Ray Core Infrastructure

  Relevant source files 
 - [cpp/src/ray/runtime/task/task_executor.cc](https://github.com/ray-project/ray/blob/bf129559/cpp/src/ray/runtime/task/task_executor.cc)
 - [cpp/src/ray/runtime/task/task_executor.h](https://github.com/ray-project/ray/blob/bf129559/cpp/src/ray/runtime/task/task_executor.h)
 - [python/ray/_raylet.pyx](https://github.com/ray-project/ray/blob/bf129559/python/ray/_raylet.pyx)
 - [python/ray/includes/common.pxd](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/common.pxd)
 - [python/ray/includes/gcs_client.pxi](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/gcs_client.pxi)
 - [python/ray/includes/libcoreworker.pxd](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/libcoreworker.pxd)
 - [src/mock/ray/gcs_client/accessor.h](https://github.com/ray-project/ray/blob/bf129559/src/mock/ray/gcs_client/accessor.h)
 - [src/mock/ray/raylet/worker.h](https://github.com/ray-project/ray/blob/bf129559/src/mock/ray/raylet/worker.h)
 - [src/mock/ray/raylet/worker_pool.h](https://github.com/ray-project/ray/blob/bf129559/src/mock/ray/raylet/worker_pool.h)
 - [src/ray/common/task/task_spec.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/common/task/task_spec.cc)
 - [src/ray/common/task/task_spec.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/common/task/task_spec.h)
 - [src/ray/common/task/task_util.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/common/task/task_util.h)
 - [src/ray/core_worker/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/BUILD.bazel)
 - [src/ray/core_worker/actor_management/actor_handle.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/actor_management/actor_handle.cc)
 - [src/ray/core_worker/actor_management/actor_handle.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/actor_management/actor_handle.h)
 - [src/ray/core_worker/common.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/common.h)
 - [src/ray/core_worker/core_worker.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc)
 - [src/ray/core_worker/core_worker.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.h)
 - [src/ray/core_worker/core_worker_options.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker_options.h)
 - [src/ray/core_worker/core_worker_process.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker_process.cc)
 - [src/ray/core_worker/core_worker_process.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker_process.h)
 - [src/ray/core_worker/lib/java/io_ray_runtime_RayNativeRuntime.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/lib/java/io_ray_runtime_RayNativeRuntime.cc)
 - [src/ray/core_worker/metrics.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/metrics.h)
 - [src/ray/core_worker/task_manager.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_manager.cc)
 - [src/ray/core_worker/task_manager.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_manager.h)
 - [src/ray/core_worker/tests/core_worker_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/tests/core_worker_test.cc)
 - [src/ray/core_worker/tests/task_manager_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/tests/task_manager_test.cc)
 - [src/ray/core_worker_rpc_client/tests/core_worker_client_pool_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker_rpc_client/tests/core_worker_client_pool_test.cc)
 - [src/ray/gcs/gcs_node_manager.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs/gcs_node_manager.cc)
 - [src/ray/gcs/gcs_node_manager.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs/gcs_node_manager.h)
 - [src/ray/gcs/tests/export_api/gcs_node_manager_export_event_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs/tests/export_api/gcs_node_manager_export_event_test.cc)
 - [src/ray/gcs/tests/gcs_node_manager_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs/tests/gcs_node_manager_test.cc)
 - [src/ray/gcs_rpc_client/accessor.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs_rpc_client/accessor.cc)
 - [src/ray/gcs_rpc_client/accessor.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs_rpc_client/accessor.h)
 - [src/ray/gcs_rpc_client/gcs_client.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs_rpc_client/gcs_client.cc)
 - [src/ray/gcs_rpc_client/global_state_accessor.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/gcs_rpc_client/global_state_accessor.cc)
 - [src/ray/protobuf/common.proto](https://github.com/ray-project/ray/blob/bf129559/src/ray/protobuf/common.proto)
 - [src/ray/protobuf/gcs_service.proto](https://github.com/ray-project/ray/blob/bf129559/src/ray/protobuf/gcs_service.proto)
 - [src/ray/pubsub/gcs_subscriber.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/pubsub/gcs_subscriber.cc)
 - [src/ray/pubsub/gcs_subscriber.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/pubsub/gcs_subscriber.h)
 - [src/ray/raylet/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/BUILD.bazel)
 - [src/ray/raylet/fake_worker.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/fake_worker.h)
 - [src/ray/raylet/main.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/main.cc)
 - [src/ray/raylet/node_manager.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/node_manager.cc)
 - [src/ray/raylet/node_manager.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/node_manager.h)
 - [src/ray/raylet/noop_worker_killing_policy.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/noop_worker_killing_policy.h)
 - [src/ray/raylet/noop_worker_killing_policy_factory.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/noop_worker_killing_policy_factory.cc)
 - [src/ray/raylet/scheduling/local_lease_manager.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/scheduling/local_lease_manager.cc)
 - [src/ray/raylet/scheduling/local_lease_manager.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/scheduling/local_lease_manager.h)
 - [src/ray/raylet/scheduling/tests/cluster_lease_manager_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/scheduling/tests/cluster_lease_manager_test.cc)
 - [src/ray/raylet/scheduling/tests/local_lease_manager_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/scheduling/tests/local_lease_manager_test.cc)
 - [src/ray/raylet/tests/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/tests/BUILD.bazel)
 - [src/ray/raylet/tests/node_manager_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/tests/node_manager_test.cc)
 - [src/ray/raylet/tests/worker_killing_policy_group_by_owner_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/tests/worker_killing_policy_group_by_owner_test.cc)
 - [src/ray/raylet/tests/worker_pool_test.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/tests/worker_pool_test.cc)
 - [src/ray/raylet/worker.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker.cc)
 - [src/ray/raylet/worker.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker.h)
 - [src/ray/raylet/worker_interface.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker_interface.h)
 - [src/ray/raylet/worker_killing_policy_factory.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker_killing_policy_factory.h)
 - [src/ray/raylet/worker_killing_policy_group_by_owner.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker_killing_policy_group_by_owner.cc)
 - [src/ray/raylet/worker_killing_policy_group_by_owner.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker_killing_policy_group_by_owner.h)
 - [src/ray/raylet/worker_killing_policy_interface.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker_killing_policy_interface.h)
 - [src/ray/raylet/worker_pool.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker_pool.cc)
 - [src/ray/raylet/worker_pool.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/worker_pool.h)
 
  
## Purpose and Scope

 Ray Core Infrastructure provides the foundational distributed computing layer that underlies all Ray libraries. It handles task execution, object lifecycle management, distributed memory, reference counting, and fault tolerance. This infrastructure is implemented primarily in C++ for performance, with language-specific frontends (Python, Java, C++) that communicate through protocol buffers and shared memory.

 This document covers the core execution and storage mechanisms. For details on specific components:

 
 - Task execution and CoreWorker internals: see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution)
 - Experimental accelerated execution: see [Compiled DAG and Accelerated Execution](https://deepwiki.com/ray-project/ray/2.2-compiled-dag-and-accelerated-execution)
 - Node management, GCS, and Plasma: see [Raylet, GCS, and Object Store](https://deepwiki.com/ray-project/ray/2.3-raylet-gcs-and-object-store)
 - Higher-level libraries built on this infrastructure: see [Ray Data](https://deepwiki.com/ray-project/ray/3-ray-data), [Ray Serve](https://deepwiki.com/ray-project/ray/4-ray-serve), [Ray RLlib](https://deepwiki.com/ray-project/ray/5-ray-rllib)
 
 
## Core Infrastructure Components

 The Ray Core infrastructure consists of several key C++ components that work together to enable distributed execution:

 **Core Infrastructure Overview**

 
```

```

 Sources: [src/ray/core_worker/core_worker.h167-217](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.h#L167-L217) [src/ray/core_worker/core_worker.cc287-372](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc#L287-L372) [python/ray/_private/worker.py443-514](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/worker.py#L443-L514)

 
### CoreWorker

 The `CoreWorker` class is the central coordinator for all Ray functionality in a worker process. It is instantiated once per worker (or driver) and manages task submission, task execution, and object storage. It coordinates with the `Raylet` (local node manager) for resource scheduling and the `GCS` for global metadata. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 Sources: [src/ray/core_worker/core_worker.h167-276](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.h#L167-L276) [src/ray/core_worker/core_worker.cc287-526](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc#L287-L526)

 
### TaskManager

 The `TaskManager` tracks the lifecycle of all tasks submitted by a worker. It maintains task state, handles retries for failed tasks, and manages `ObjectRefStream` for streaming generator results. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 
| Component | Purpose |
|---|---|
| pending_tasks_ | Tasks awaiting execution or whose results are being consumed |
| submissible_tasks_ | Tasks that can be retried if needed |
| ObjectRefStream | Manages streaming generator task results |

 Sources: [src/ray/core_worker/task_manager.h175-193](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_manager.h#L175-L193) [src/ray/core_worker/task_manager.cc238-314](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_manager.cc#L238-L314)

 
### ReferenceCounter

 The `ReferenceCounter` implements distributed garbage collection by tracking object references across the cluster. It manages local references held by the language runtime, references passed to tasks, and borrower information for objects shared across nodes. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 Sources: [src/ray/core_worker/reference_counter.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/reference_counter.h) [src/ray/core_worker/core_worker.cc469-487](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc#L469-L487)

 
## Task Execution Flow

 **Natural Language to Code: Task Submission and Execution**

 
```

```

 Sources: [python/ray/_raylet.pyx764-879](https://github.com/ray-project/ray/blob/bf129559/python/ray/_raylet.pyx#L764-L879) [src/ray/core_worker/core_worker.cc373-396](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc#L373-L396) [python/ray/remote_function.py61-100](https://github.com/ray-project/ray/blob/bf129559/python/ray/remote_function.py#L61-L100) [src/ray/raylet/node_manager.cc164-250](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/node_manager.cc#L164-L250)

 
### Task Submission (Python to C++)

 When a user calls `func.remote()`, the Python layer invokes `RemoteFunction._remote()`. Arguments are serialized via `prepare_args_internal()` in Cython. The `CoreWorker::SubmitTask` method is then called, which registers the task in the `TaskManager` before sending it to the local `Raylet` for scheduling. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 Sources: [python/ray/_raylet.pyx748-879](https://github.com/ray-project/ray/blob/bf129559/python/ray/_raylet.pyx#L748-L879) [src/ray/core_worker/task_manager.cc238-267](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_manager.cc#L238-L267) [python/ray/remote_function.py200-350](https://github.com/ray-project/ray/blob/bf129559/python/ray/remote_function.py#L200-L350)

 
### Task Execution

 When a worker receives a task from the Raylet, `TaskReceiver::HandleTask` is triggered. The `CoreWorker` resolves task dependencies (ensuring all arguments are local) and executes the language-specific callback. Results are stored in the local `CoreWorkerMemoryStore` or the Plasma object store. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 Sources: [src/ray/core_worker/core_worker.cc373-396](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc#L373-L396) [src/ray/core_worker/task_execution/task_receiver.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_execution/task_receiver.h)

 
## Object Management and Storage

 Ray uses a tiered storage system to handle objects efficiently based on size. For details, see [Raylet, GCS, and Object Store](https://deepwiki.com/ray-project/ray/2.3-raylet-gcs-and-object-store).

 **Object Storage Hierarchy**

 
```

```

 Sources: [src/ray/core_worker/store_provider/memory_store/memory_store.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/store_provider/memory_store/memory_store.h) [src/ray/core_worker/store_provider/plasma_store_provider.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/store_provider/plasma_store_provider.h) [src/ray/core_worker/core_worker.cc357](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc#L357-L357)

 
### Memory Store vs. Plasma

 
 - **CoreWorkerMemoryStore**: Stores small objects directly in the worker's heap using `absl::flat_hash_map`. This provides the lowest latency for small objects (typically < 100KB).
 - **Plasma Object Store**: Large objects are stored in a shared memory region (Plasma). This allows multiple workers on the same node to read the same object via zero-copy memory mapping.
 
 Sources: [src/ray/core_worker/store_provider/memory_store/memory_store.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/store_provider/memory_store/memory_store.h) [src/ray/core_worker/store_provider/plasma_store_provider.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/store_provider/plasma_store_provider.h)

 
### Distributed Reference Counting

 The `ReferenceCounter` tracks ownership. The worker that creates an object is the "owner." Other workers that receive an `ObjectRef` are "borrowers." The owner is responsible for keeping the object alive as long as any borrower still has a reference. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 Sources: [src/ray/core_worker/reference_counter.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/reference_counter.h) [src/ray/core_worker/reference_counter.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/reference_counter.cc)

 
## Streaming and Generators

 Ray supports streaming task results through the `ObjectRefStream` abstraction. This allows a single task to yield multiple values (generators), which can be consumed by the caller as they are produced. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 Sources: [src/ray/core_worker/task_manager.h67-173](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_manager.h#L67-L173) [src/ray/core_worker/task_manager.cc66-236](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_manager.cc#L66-L236)

 
## Fault Tolerance

 The `ObjectRecoveryManager` handles the reconstruction of lost objects. If a node fails and its Plasma objects are lost, Ray can resubmit the tasks that originally produced those objects, provided the lineage is still available in the `TaskManager`. For details, see [Core Worker and Task Execution](https://deepwiki.com/ray-project/ray/2.1-core-worker-and-task-execution).

 Sources: [src/ray/core_worker/object_recovery_manager.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/object_recovery_manager.h) [src/ray/core_worker/object_recovery_manager.cc24-80](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/object_recovery_manager.cc#L24-L80)

 
## Observability and Metrics

 The core infrastructure exports detailed metrics through the `TaskCounter` and `TaskEventBuffer`. These track task states (Pending, Running, Finished) and record events that are sent to the GCS and eventually visualized in the Ray Dashboard. For details, see [Observability: Dashboard, Metrics, and State API](https://deepwiki.com/ray-project/ray/2.6-observability:-dashboard-metrics-and-state-api).

 Sources: [src/ray/core_worker/core_worker.h64-140](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.h#L64-L140) [src/ray/core_worker/task_event_buffer.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/task_event_buffer.h) [src/ray/core_worker/core_worker.cc165-285](https://github.com/ray-project/ray/blob/bf129559/src/ray/core_worker/core_worker.cc#L165-L285)
