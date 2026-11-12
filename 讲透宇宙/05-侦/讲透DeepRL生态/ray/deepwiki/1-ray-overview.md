> 来源: [https://deepwiki.com/ray-project/ray/1-ray-overview](https://deepwiki.com/ray-project/ray/1-ray-overview)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Ray Overview

  Relevant source files 
 - [ci/lint/git-clang-format](https://github.com/ray-project/ray/blob/bf129559/ci/lint/git-clang-format)
 - [ci/lint/pydoclint-baseline.txt](https://github.com/ray-project/ray/blob/bf129559/ci/lint/pydoclint-baseline.txt)
 - [doc/source/_static/img/run-on-anyscale.svg](https://github.com/ray-project/ray/blob/bf129559/doc/source/_static/img/run-on-anyscale.svg)
 - [doc/source/cluster/doc_code/slurm-basic.sh](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/doc_code/slurm-basic.sh)
 - [doc/source/cluster/vms/user-guides/community/slurm.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/vms/user-guides/community/slurm.rst)
 - [doc/source/data/benchmark.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/benchmark.md?plain=1)
 - [doc/source/data/data.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/data.rst)
 - [doc/source/data/examples/batch_inference_object_detection.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/examples/batch_inference_object_detection.ipynb)
 - [doc/source/data/examples/huggingface_vit_batch_prediction.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/examples/huggingface_vit_batch_prediction.ipynb)
 - [doc/source/data/examples/pytorch_resnet_batch_prediction.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/examples/pytorch_resnet_batch_prediction.ipynb)
 - [doc/source/data/images/dataset-progress-bar.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/images/dataset-progress-bar.png)
 - [doc/source/data/images/multimodal_inference_results.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/images/multimodal_inference_results.png)
 - [doc/source/data/inspecting-data.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/inspecting-data.rst)
 - [doc/source/data/monitoring-your-workload.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/monitoring-your-workload.rst)
 - [doc/source/data/quickstart.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/quickstart.rst)
 - [doc/source/ray-core/api/exceptions.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/api/exceptions.rst)
 - [doc/source/ray-core/examples/batch_prediction.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/examples/batch_prediction.ipynb)
 - [doc/source/ray-core/examples/gentle_walkthrough.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/examples/gentle_walkthrough.ipynb)
 - [doc/source/ray-core/examples/highly_parallel.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/examples/highly_parallel.ipynb)
 - [doc/source/ray-core/examples/map_reduce.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/examples/map_reduce.ipynb)
 - [doc/source/ray-core/examples/monte_carlo_pi.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/examples/monte_carlo_pi.rst)
 - [doc/source/ray-core/examples/plot_hyperparameter.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/examples/plot_hyperparameter.ipynb)
 - [doc/source/ray-core/examples/plot_parameter_server.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/examples/plot_parameter_server.ipynb)
 - [doc/source/ray-core/fault_tolerance/actors.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/fault_tolerance/actors.rst)
 - [doc/source/ray-core/fault_tolerance/nodes.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/fault_tolerance/nodes.rst)
 - [doc/source/ray-core/fault_tolerance/objects.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/fault_tolerance/objects.rst)
 - [doc/source/ray-core/internals/task-lifecycle.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/internals/task-lifecycle.rst)
 - [doc/source/ray-core/objects/object-spilling.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/objects/object-spilling.rst)
 - [doc/source/ray-core/objects/serialization.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/objects/serialization.rst)
 - [doc/source/ray-core/ray-dag.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/ray-dag.rst)
 - [doc/source/ray-core/walkthrough.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-core/walkthrough.rst)
 - [doc/source/ray-overview/getting-started.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-overview/getting-started.md?plain=1)
 - [doc/source/serve/doc_code/stable_diffusion.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/doc_code/stable_diffusion.py)
 - [doc/source/serve/tutorials/stable-diffusion.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/tutorials/stable-diffusion.md?plain=1)
 - [doc/source/templates/04_finetuning_llms_with_deepspeed/utils.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/templates/04_finetuning_llms_with_deepspeed/utils.py)
 - [doc/source/train/common/torch-configure-run.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/common/torch-configure-run.rst)
 - [doc/source/train/examples/deepspeed/gptj_deepspeed_fine_tuning.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/deepspeed/gptj_deepspeed_fine_tuning.ipynb)
 - [doc/source/train/examples/lightning/dolly_lightning_fsdp_finetuning.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/lightning/dolly_lightning_fsdp_finetuning.ipynb)
 - [doc/source/train/examples/lightning/lightning_cola_advanced.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/lightning/lightning_cola_advanced.ipynb)
 - [doc/source/train/examples/lightning/vicuna_13b_lightning_deepspeed_finetune.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/lightning/vicuna_13b_lightning_deepspeed_finetune.ipynb)
 - [doc/source/train/examples/pytorch/torch_detection.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/pytorch/torch_detection.ipynb)
 - [doc/source/train/examples/transformers/huggingface_text_classification.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/transformers/huggingface_text_classification.ipynb)
 - [doc/source/train/getting-started-pytorch-lightning.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/getting-started-pytorch-lightning.rst)
 - [doc/source/train/getting-started-pytorch.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/getting-started-pytorch.rst)
 - [doc/source/train/getting-started-transformers.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/getting-started-transformers.rst)
 - [doc/source/train/huggingface-accelerate.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/huggingface-accelerate.rst)
 - [doc/source/train/user-guides/data-loading-preprocessing.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/user-guides/data-loading-preprocessing.rst)
 - [doc/source/train/user-guides/experiment-tracking.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/user-guides/experiment-tracking.rst)
 - [java/test/src/main/java/io/ray/test/NodeLabelSchedulingTest.java](https://github.com/ray-project/ray/blob/bf129559/java/test/src/main/java/io/ray/test/NodeLabelSchedulingTest.java)
 - [pyproject.toml](https://github.com/ray-project/ray/blob/bf129559/pyproject.toml)
 - [python/ray/_common/ray_option_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_common/ray_option_utils.py)
 - [python/ray/_private/label_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/label_utils.py)
 - [python/ray/_private/node.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/node.py)
 - [python/ray/_private/object_ref_generator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/object_ref_generator.py)
 - [python/ray/_private/parameter.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/parameter.py)
 - [python/ray/_private/ray_constants.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/ray_constants.py)
 - [python/ray/_private/services.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/services.py)
 - [python/ray/_private/utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/utils.py)
 - [python/ray/_private/worker.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/worker.py)
 - [python/ray/_raylet.pxd](https://github.com/ray-project/ray/blob/bf129559/python/ray/_raylet.pxd)
 - [python/ray/_raylet.pyi](https://github.com/ray-project/ray/blob/bf129559/python/ray/_raylet.pyi)
 - [python/ray/actor.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/actor.py)
 - [python/ray/autoscaler/_private/constants.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/autoscaler/_private/constants.py)
 - [python/ray/exceptions.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/exceptions.py)
 - [python/ray/includes/object_ref.pxi](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/object_ref.pxi)
 - [python/ray/includes/object_ref.pyi](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/object_ref.pyi)
 - [python/ray/includes/ray_config.pxd](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/ray_config.pxd)
 - [python/ray/includes/ray_config.pxi](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/ray_config.pxi)
 - [python/ray/includes/unique_ids.pyi](https://github.com/ray-project/ray/blob/bf129559/python/ray/includes/unique_ids.pyi)
 - [python/ray/remote_function.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/remote_function.py)
 - [python/ray/scripts/scripts.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/scripts/scripts.py)
 - [python/ray/scripts/symmetric_run.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/scripts/symmetric_run.py)
 - [python/ray/setup-dev.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/setup-dev.py)
 - [python/ray/tests/autoscaler_test_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/autoscaler_test_utils.py)
 - [python/ray/tests/kuberay/rune2e.sh](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/kuberay/rune2e.sh)
 - [python/ray/tests/test_actor.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_actor.py)
 - [python/ray/tests/test_baseexceptionandgroup.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_baseexceptionandgroup.py)
 - [python/ray/tests/test_basic.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_basic.py)
 - [python/ray/tests/test_cli.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_cli.py)
 - [python/ray/tests/test_client_terminate.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_client_terminate.py)
 - [python/ray/tests/test_failure.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_failure.py)
 - [python/ray/tests/test_generators.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_generators.py)
 - [python/ray/tests/test_label_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_label_utils.py)
 - [python/ray/tests/test_node_label_scheduling_strategy.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_node_label_scheduling_strategy.py)
 - [python/ray/tests/test_node_labels.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_node_labels.py)
 - [python/ray/tests/test_streaming_generator.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_streaming_generator.py)
 - [python/ray/tests/test_streaming_generator_backpressure.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_streaming_generator_backpressure.py)
 - [python/ray/tests/test_symmetric_run.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_symmetric_run.py)
 - [python/ray/tests/test_traceback.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_traceback.py)
 - [python/ray/tests/test_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_utils.py)
 - [python/ray/tests/unit/test_decorator_validation.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/unit/test_decorator_validation.py)
 - [python/ray/util/check_open_ports.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/util/check_open_ports.py)
 - [release/ray_release/byod/byod_dolly_test.sh](https://github.com/ray-project/ray/blob/bf129559/release/ray_release/byod/byod_dolly_test.sh)
 - [release/ray_release/byod/byod_gptj_test.sh](https://github.com/ray-project/ray/blob/bf129559/release/ray_release/byod/byod_gptj_test.sh)
 - [release/ray_release/byod/byod_vicuna_test.sh](https://github.com/ray-project/ray/blob/bf129559/release/ray_release/byod/byod_vicuna_test.sh)
 - [release/release_logs/compare_perf_metrics](https://github.com/ray-project/ray/blob/bf129559/release/release_logs/compare_perf_metrics)
 - [rllib/utils/tests/test_utils.py](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/tests/test_utils.py)
 - [src/ray/common/ray_config_def.h](https://github.com/ray-project/ray/blob/bf129559/src/ray/common/ray_config_def.h)
 
  Ray is a unified framework for scaling Python applications from a laptop to a cluster. It provides a distributed computing runtime and a suite of domain-specific libraries for AI/ML workloads including data processing, model training, hyperparameter tuning, reinforcement learning, and model serving.

 **Core Value Proposition:**

 
 - **Unified API**: Use the same code and APIs (`@ray.remote`) across tasks, actors, and distributed data structures.
 - **Flexible Scheduling**: From embarrassingly parallel workloads to complex distributed applications.
 - **Composable Libraries**: Ray Data, Serve, Train, Tune, and RLlib share the same underlying runtime.
 - **Production-Ready**: Fault tolerance, autoscaling, and observability built-in.
 
 For detailed information about specific subsystems, see:

 
 - Architecture and Core Concepts: [Architecture and Core Concepts](https://deepwiki.com/ray-project/ray/1.1-architecture-and-core-concepts)
 - Core execution infrastructure: [Ray Core Infrastructure](https://deepwiki.com/ray-project/ray/2-ray-core-infrastructure)
 - Data processing pipelines: [Ray Data](https://deepwiki.com/ray-project/ray/3-ray-data)
 - Model serving platform: [Ray Serve](https://deepwiki.com/ray-project/ray/4-ray-serve)
 - Distributed Training: [Ray Train](https://deepwiki.com/ray-project/ray/6-ray-train)
 - Reinforcement learning: [Ray RLlib](https://deepwiki.com/ray-project/ray/5-ray-rllib)
 
 **Sources:** [python/ray/_private/worker.py47-115](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/worker.py#L47-L115)

 
---

 
## High-Level Architecture

 Ray consists of a core distributed runtime layer upon which specialized libraries are built. The core provides fundamental distributed computing primitives (tasks, actors, objects), while libraries provide domain-specific abstractions.

 
### System Topology

 The following diagram maps high-level system components to their primary implementation entities in the codebase.

 
```

```

 **Sources:** [src/ray/common/ray_config_def.h18-19](https://github.com/ray-project/ray/blob/bf129559/src/ray/common/ray_config_def.h#L18-L19) [python/ray/_private/services.py58-64](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/services.py#L58-L64)

 
---

 
## Core Components

 
### Global Control Store (GCS)

 The GCS is the centralized metadata service that maintains cluster state including node membership, actor registry, and job information. It runs as the `gcs_server` executable [python/ray/_private/services.py62-64](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/services.py#L62-L64) The `GcsClient` [python/ray/_private/services.py197-202](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/services.py#L197-L202) is used by other Ray components to interact with the GCS.

 
### Raylet (NodeManager)

 Each Ray node runs a `raylet` process [python/ray/_private/services.py59-61](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/services.py#L59-L61) It manages local resources, worker process lifecycles via a `WorkerPool`, and coordinates task scheduling. For details on node management, see [Architecture and Core Concepts](https://deepwiki.com/ray-project/ray/1.1-architecture-and-core-concepts).

 
### CoreWorker

 The `CoreWorker` is the engine embedded in every worker process. It is responsible for:

 
 - **Task Submission**: Handling normal tasks and actor tasks [python/ray/_private/worker.py117-118](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/worker.py#L117-L118)
 - **Reference Counting**: Tracking object lifetimes across the cluster.
 - **Task Execution**: Managing the execution loop for incoming RPC requests.
 
 
### Object Store (Plasma)

 Ray uses a shared-memory object store for zero-copy data exchange between processes on the same node. The `CoreWorker` interacts with this via the `PlasmaStoreProvider`.

 
---

 
## Code Entity Mapping

 The following diagram bridges the natural language concepts of "Workers" and "Tasks" to the specific C++ and Cython classes that implement them.

 
```

```

 **Sources:** [python/ray/_private/worker.py55-63](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/worker.py#L55-L63) [python/ray/actor.py26-28](https://github.com/ray-project/ray/blob/bf129559/python/ray/actor.py#L26-L28) [python/ray/remote_function.py1-50](https://github.com/ray-project/ray/blob/bf129559/python/ray/remote_function.py#L1-L50) [python/ray/_raylet.pxd1-10](https://github.com/ray-project/ray/blob/bf129559/python/ray/_raylet.pxd#L1-L10) [python/ray/_private/services.py197-202](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/services.py#L197-L202)

 
---

 
## Ray Libraries Ecosystem

 Ray provides a set of domain-specific libraries that build on the core runtime:

 
| Library | Purpose | Entry Point Module |
|---|---|---|
| Ray Data | Distributed data processing (ETL, LLM preprocessing) | ray.data |
| Ray Serve | Model serving with autoscaling and HTTP/gRPC proxies | ray.serve |
| Ray Train | Distributed training for PyTorch, TensorFlow, etc. | ray.train |
| Ray Tune | Hyperparameter tuning and experiment tracking | ray.tune |
| RLlib | Reinforcement learning algorithms | ray.rllib |
| Ray LLM | Tools for large language model workloads | ray.llm |

 
### Supported Environments

 Ray supports Python 3.10 through 3.13. It runs on Linux, macOS, and Windows [python/ray/_private/services.py41-46](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/services.py#L41-L46)

 
---

 
## Getting Started

 To start a local Ray cluster via the CLI:

 
```

```

 This command triggers the logic in `ray.scripts.scripts.cli` [python/ray/scripts/scripts.py192-193](https://github.com/ray-project/ray/blob/bf129559/python/ray/scripts/scripts.py#L192-L193) which initializes the GCS, Raylet, and other necessary processes [python/ray/_private/node.py70-110](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/node.py#L70-L110)

 For detailed architecture info, see [Architecture and Core Concepts](https://deepwiki.com/ray-project/ray/1.1-architecture-and-core-concepts).

 **Sources:** [python/ray/scripts/scripts.py192-193](https://github.com/ray-project/ray/blob/bf129559/python/ray/scripts/scripts.py#L192-L193) [python/ray/_private/node.py70-110](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/node.py#L70-L110)
