> 来源: [https://deepwiki.com/ray-project/ray/6-ray-train](https://deepwiki.com/ray-project/ray/6-ray-train)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Ray Train

  Relevant source files 
 - [doc/source/cluster/doc_code/xgboost_submit.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/doc_code/xgboost_submit.py)
 - [doc/source/train/api/api.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/api/api.rst)
 - [doc/source/train/api/deprecated.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/api/deprecated.rst)
 - [doc/source/train/benchmarks.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/benchmarks.rst)
 - [doc/source/train/doc_code/checkpoints.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/doc_code/checkpoints.py)
 - [doc/source/train/user-guides/checkpoints.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/user-guides/checkpoints.rst)
 - [doc/source/train/user-guides/fault-tolerance.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/user-guides/fault-tolerance.rst)
 - [python/ray/dashboard/modules/metrics/dashboards/data_grafana_dashboard_base.json](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/metrics/dashboards/data_grafana_dashboard_base.json)
 - [python/ray/dashboard/modules/metrics/dashboards/default_grafana_dashboard_base.json](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/metrics/dashboards/default_grafana_dashboard_base.json)
 - [python/ray/dashboard/modules/metrics/dashboards/serve_deployment_grafana_dashboard_base.json](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/metrics/dashboards/serve_deployment_grafana_dashboard_base.json)
 - [python/ray/dashboard/modules/metrics/dashboards/serve_grafana_dashboard_base.json](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/metrics/dashboards/serve_grafana_dashboard_base.json)
 - [python/ray/dashboard/modules/metrics/dashboards/train_dashboard_panels.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/metrics/dashboards/train_dashboard_panels.py)
 - [python/ray/dashboard/modules/metrics/dashboards/train_grafana_dashboard_base.json](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/metrics/dashboards/train_grafana_dashboard_base.json)
 - [python/ray/data/_internal/iterator/stream_split_iterator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/data/_internal/iterator/stream_split_iterator.py)
 - [python/ray/train/__init__.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/__init__.py)
 - [python/ray/train/v2/BUILD.bazel](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/BUILD.bazel)
 - [python/ray/train/v2/_internal/callbacks/datasets.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/callbacks/datasets.py)
 - [python/ray/train/v2/_internal/callbacks/metrics.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/callbacks/metrics.py)
 - [python/ray/train/v2/_internal/callbacks/user_callback.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/callbacks/user_callback.py)
 - [python/ray/train/v2/_internal/constants.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/constants.py)
 - [python/ray/train/v2/_internal/data_integration/dataset_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/data_integration/dataset_manager.py)
 - [python/ray/train/v2/_internal/data_integration/interfaces.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/data_integration/interfaces.py)
 - [python/ray/train/v2/_internal/execution/callback.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/callback.py)
 - [python/ray/train/v2/_internal/execution/checkpoint/checkpoint_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/checkpoint/checkpoint_manager.py)
 - [python/ray/train/v2/_internal/execution/checkpoint/report_handler.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/checkpoint/report_handler.py)
 - [python/ray/train/v2/_internal/execution/checkpoint/validation_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/checkpoint/validation_manager.py)
 - [python/ray/train/v2/_internal/execution/context.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/context.py)
 - [python/ray/train/v2/_internal/execution/controller/controller.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/controller/controller.py)
 - [python/ray/train/v2/_internal/execution/train_fn_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/train_fn_utils.py)
 - [python/ray/train/v2/_internal/execution/worker_group/worker.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/worker_group/worker.py)
 - [python/ray/train/v2/_internal/execution/worker_group/worker_group.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/worker_group/worker_group.py)
 - [python/ray/train/v2/_internal/metrics/__init__.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/metrics/__init__.py)
 - [python/ray/train/v2/_internal/metrics/base.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/metrics/base.py)
 - [python/ray/train/v2/_internal/metrics/controller.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/metrics/controller.py)
 - [python/ray/train/v2/_internal/metrics/worker.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/metrics/worker.py)
 - [python/ray/train/v2/api/config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/config.py)
 - [python/ray/train/v2/api/data_parallel_trainer.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/data_parallel_trainer.py)
 - [python/ray/train/v2/api/reported_checkpoint.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/reported_checkpoint.py)
 - [python/ray/train/v2/api/train_fn_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/train_fn_utils.py)
 - [python/ray/train/v2/api/validation_config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/validation_config.py)
 - [python/ray/train/v2/tests/test_accelerator_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_accelerator_utils.py)
 - [python/ray/train/v2/tests/test_async_checkpointing_validation.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_async_checkpointing_validation.py)
 - [python/ray/train/v2/tests/test_checkpoint_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_checkpoint_manager.py)
 - [python/ray/train/v2/tests/test_config.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_config.py)
 - [python/ray/train/v2/tests/test_controller.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_controller.py)
 - [python/ray/train/v2/tests/test_data_integration.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_data_integration.py)
 - [python/ray/train/v2/tests/test_data_parallel_trainer.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_data_parallel_trainer.py)
 - [python/ray/train/v2/tests/test_data_resource_cleanup.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_data_resource_cleanup.py)
 - [python/ray/train/v2/tests/test_dataset_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_dataset_manager.py)
 - [python/ray/train/v2/tests/test_metrics.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_metrics.py)
 - [python/ray/train/v2/tests/test_report_handler.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_report_handler.py)
 - [python/ray/train/v2/tests/test_serialization.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_serialization.py)
 - [python/ray/train/v2/tests/test_validation_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_validation_manager.py)
 - [python/ray/train/v2/tests/test_worker_group.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/test_worker_group.py)
 - [python/ray/train/v2/tests/util.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/tests/util.py)
 - [release/train_tests/multinode_persistence/compute_aws.yaml](https://github.com/ray-project/ray/blob/bf129559/release/train_tests/multinode_persistence/compute_aws.yaml)
 - [release/train_tests/multinode_persistence/compute_gce.yaml](https://github.com/ray-project/ray/blob/bf129559/release/train_tests/multinode_persistence/compute_gce.yaml)
 
  Ray Train is a distributed training framework built on top of Ray Core, designed to scale model training from a single machine to large clusters. It provides a unified API for data-parallel training across multiple deep learning and machine learning frameworks. The "v2" architecture introduces a robust state-machine-based controller and improved lifecycle management for distributed worker groups.

 
## Architecture Overview

 The Ray Train architecture follows a hierarchical control pattern where a central controller manages a group of distributed workers.

 
### System Components

 
 - **`DataParallelTrainer`**: The primary entry point for users. It configures the training run, including scaling, backends, and datasets, and launches the `TrainController` [python/ray/train/v2/api/data_parallel_trainer.py66-107](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/data_parallel_trainer.py#L66-L107)
 - **`TrainController`**: An actor that manages the training lifecycle. It implements a state machine to handle scheduling, running, resizing (elasticity), and failure recovery [python/ray/train/v2/_internal/execution/controller/controller.py105-114](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/controller/controller.py#L105-L114)
 - **`WorkerGroup`**: A collection of Ray actors (`RayTrainWorker`) that execute the user-provided training function in parallel [python/ray/train/v2/_internal/execution/worker_group/worker_group.py88-91](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/worker_group/worker_group.py#L88-L91)
 - **`TrainContext`**: A singleton available within the training function that provides access to world rank, local rank, and storage for reporting metrics and checkpoints [python/ray/train/v2/_internal/execution/context.py123-132](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/context.py#L123-L132)
 
 
### Code Entity Relationship

 The following diagram illustrates how high-level API calls translate into the underlying code entities.

 **Diagram: API to Execution Mapping**

 
```

```

 Sources: [python/ray/train/v2/api/data_parallel_trainer.py160-175](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/data_parallel_trainer.py#L160-L175) [python/ray/train/v2/_internal/execution/controller/controller.py105-114](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/controller/controller.py#L105-L114) [python/ray/train/v2/_internal/execution/worker_group/worker_group.py88-118](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/worker_group/worker_group.py#L88-L118) [python/ray/train/v2/api/train_fn_utils.py23-31](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/train_fn_utils.py#L23-L31)

 
## Distributed Training Lifecycle

 Ray Train manages the complex transitions of a distributed job through a series of states.

 
### Controller State Machine

 The `TrainController` transitions through several states to ensure workers are healthy and resources are allocated correctly:

 
 - **`SchedulingState`**: Requesting resources and starting the `WorkerGroup` [python/ray/train/v2/_internal/execution/controller/state.py48](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/controller/state.py#L48-L48)
 - **`RunningState`**: The training function is active on the workers [python/ray/train/v2/_internal/execution/controller/state.py47](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/controller/state.py#L47-L47)
 - **`ResizingState` / `RestartingState`**: Triggered by `ScalingPolicy` (e.g., adding nodes) or `FailurePolicy` (e.g., node death) [python/ray/train/v2/_internal/execution/controller/state.py45-46](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/controller/state.py#L45-L46)
 
 
### Worker Execution

 Each worker runs in its own process, managed by `RayTrainWorker`. The user's `train_loop_per_worker` is executed inside a `ThreadRunner` to allow the worker actor to remain responsive to heartbeats and status polls from the controller [python/ray/train/v2/_internal/execution/context.py100-116](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/context.py#L100-L116)

 For details on the state machine and lifecycle, see [Train v2 Controller and Worker Group](https://deepwiki.com/ray-project/ray/6.1-train-v2-controller-and-worker-group).

 
## Checkpointing and Metrics

 Ray Train provides a standardized way to save model state and track progress via `ray.train.report`.

 
| Feature | Implementation | Description |
|---|---|---|
| CheckpointManager | python/ray/train/v2/_internal/execution/checkpoint/checkpoint_manager.py98 | Manages checkpoint persistence, deletion of old checkpoints, and restoration. |
| SynchronizationActor | python/ray/train/v2/_internal/execution/checkpoint/sync_actor.py | Facilitates broadcasting data (like model weights) across ranks for synchronized checkpointing. |
| Async Reporting | python/ray/train/v2/api/report_config.py37 | Supports CheckpointUploadMode.ASYNC to avoid blocking the training loop during I/O. |

 Sources: [python/ray/train/v2/api/train_fn_utils.py23-31](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/train_fn_utils.py#L23-L31) [python/ray/train/v2/_internal/execution/checkpoint/checkpoint_manager.py143-185](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/checkpoint/checkpoint_manager.py#L143-L185)

 
## Framework Integrations and Data

 Ray Train abstracts the setup of distributed backends (NCCL, Gloo, etc.) and integrates with Ray Data for high-performance ingestion.

 
 - **Backend Setup**: Classes like `AcceleratorSetupCallback` and `BackendSetupCallback` handle environment-specific initialization (e.g., setting `MASTER_ADDR` for PyTorch) [python/ray/train/v2/api/data_parallel_trainer.py28-29](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/data_parallel_trainer.py#L28-L29)
 - **Data Ingestion**: The `DataConfig` system allows `Ray Data` to be automatically sharded across workers. Workers access their local shard via `get_context().get_dataset_shard()` [python/ray/train/v2/_internal/execution/context.py193-199](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/context.py#L193-L199)
 
 For details on PyTorch, TensorFlow, and other framework specifics, see [Framework Integrations and Data Loading](https://deepwiki.com/ray-project/ray/6.2-framework-integrations-and-data-loading).

 
## System Flow: Checkpoint Reporting

 The following diagram bridges the `ray.train.report` call to the internal persistence logic.

 **Diagram: Checkpoint Persistence Flow**

 
```

```

 Sources: [python/ray/train/v2/api/train_fn_utils.py23-132](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/api/train_fn_utils.py#L23-L132) [python/ray/train/v2/_internal/execution/context.py123-191](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/context.py#L123-L191) [python/ray/train/v2/_internal/execution/checkpoint/checkpoint_manager.py143-185](https://github.com/ray-project/ray/blob/bf129559/python/ray/train/v2/_internal/execution/checkpoint/checkpoint_manager.py#L143-L185)

 
## Next Steps

 
 - [Train v2 Controller and Worker Group](https://deepwiki.com/ray-project/ray/6.1-train-v2-controller-and-worker-group) — Deep dive into the `TrainController` state machine and `WorkerGroup` management.
 - [Framework Integrations and Data Loading](https://deepwiki.com/ray-project/ray/6.2-framework-integrations-and-data-loading) — Details on PyTorch/TF/XGBoost integrations and the `DataConfig` pipeline.
