> 来源: [https://deepwiki.com/ray-project/ray/7-ray-tune](https://deepwiki.com/ray-project/ray/7-ray-tune)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Ray Tune

  Relevant source files 
 - [doc/.gitignore](https://github.com/ray-project/ray/blob/bf129559/doc/.gitignore)
 - [doc/source/_static/css/custom.css](https://github.com/ray-project/ray/blob/bf129559/doc/source/_static/css/custom.css)
 - [doc/source/_static/img/ray_logo.svg](https://github.com/ray-project/ray/blob/bf129559/doc/source/_static/img/ray_logo.svg)
 - [doc/source/cluster/running-applications/job-submission/quickstart.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/cluster/running-applications/job-submission/quickstart.rst)
 - [doc/source/conf.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/conf.py)
 - [doc/source/custom_directives.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/custom_directives.py)
 - [doc/source/data/examples.yml](https://github.com/ray-project/ray/blob/bf129559/doc/source/data/examples.yml)
 - [doc/source/images/ray_header_logo.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/images/ray_header_logo.png)
 - [doc/source/images/ray_logo.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/images/ray_logo.png)
 - [doc/source/ray-overview/examples/index.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-overview/examples/index.rst)
 - [doc/source/ray-overview/images/ray_svg_logo.svg](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-overview/images/ray_svg_logo.svg)
 - [doc/source/ray-overview/use-cases.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/ray-overview/use-cases.rst)
 - [doc/source/serve/examples.yml](https://github.com/ray-project/ray/blob/bf129559/doc/source/serve/examples.yml)
 - [doc/source/train/deepspeed.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/deepspeed.rst)
 - [doc/source/train/examples.yml](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples.yml)
 - [doc/source/train/examples/jax/intro_to_jax_trainer/README.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/jax/intro_to_jax_trainer/README.ipynb)
 - [doc/source/train/examples/jax/intro_to_jax_trainer/README.md](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/examples/jax/intro_to_jax_trainer/README.md?plain=1)
 - [doc/source/train/train.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/train.rst)
 - [doc/source/tune/examples/index.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/tune/examples/index.rst)
 - [doc/source/tune/examples/tune-pytorch-cifar.ipynb](https://github.com/ray-project/ray/blob/bf129559/doc/source/tune/examples/tune-pytorch-cifar.ipynb)
 - [python/ray/_private/event/event_logger.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/event/event_logger.py)
 - [python/ray/_private/event/export_event_logger.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/event/export_event_logger.py)
 - [python/ray/_private/test_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/_private/test_utils.py)
 - [python/ray/dashboard/modules/event/event_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/event/event_utils.py)
 - [python/ray/dashboard/modules/event/tests/test_event.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/event/tests/test_event.py)
 - [python/ray/dashboard/modules/event/tests/test_generate_export_events.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/event/tests/test_generate_export_events.py)
 - [python/ray/dashboard/modules/job/cli.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/cli.py)
 - [python/ray/dashboard/modules/job/common.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/common.py)
 - [python/ray/dashboard/modules/job/job_agent.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/job_agent.py)
 - [python/ray/dashboard/modules/job/job_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/job_manager.py)
 - [python/ray/dashboard/modules/job/job_supervisor.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/job_supervisor.py)
 - [python/ray/dashboard/modules/job/tests/test_cli.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/tests/test_cli.py)
 - [python/ray/dashboard/modules/job/tests/test_cli_integration.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/tests/test_cli_integration.py)
 - [python/ray/dashboard/modules/job/tests/test_common.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/tests/test_common.py)
 - [python/ray/dashboard/modules/job/tests/test_job_agent.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/tests/test_job_agent.py)
 - [python/ray/dashboard/modules/job/tests/test_job_manager.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/tests/test_job_manager.py)
 - [python/ray/tests/conftest.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/conftest.py)
 - [python/ray/tests/test_dashboard.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_dashboard.py)
 - [python/ray/tests/test_gcs_fault_tolerance.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_gcs_fault_tolerance.py)
 - [python/ray/tests/test_gcs_utils.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_gcs_utils.py)
 - [python/ray/tests/test_network_failure_e2e.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_network_failure_e2e.py)
 - [python/ray/tests/test_placement_group_5.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_placement_group_5.py)
 - [python/ray/tests/test_runtime_env_conda_and_pip_3.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_runtime_env_conda_and_pip_3.py)
 - [python/ray/tests/test_runtime_env_working_dir_3.py](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_runtime_env_working_dir_3.py)
 - [release/nightly_tests/setup_chaos.py](https://github.com/ray-project/ray/blob/bf129559/release/nightly_tests/setup_chaos.py)
 - [src/ray/raylet/placement_group_resource_manager.cc](https://github.com/ray-project/ray/blob/bf129559/src/ray/raylet/placement_group_resource_manager.cc)
 
  Ray Tune is a distributed hyperparameter optimization (HPO) framework built on Ray. It provides a unified interface for scaling hyperparameter search, supporting various search algorithms (e.g., Bayesian Optimization, HyperOpt) and scheduling strategies (e.g., ASHA, PBT) to efficiently manage cluster resources and trial lifecycles.

 
## Tuner API and Experiment Definition

 The primary entry point for Ray Tune is the `Tuner` class, which orchestrates the tuning process by taking a `Trainable` (the function or class to optimize) and a `param_space` (the search space) [doc/source/conf.py113](https://github.com/ray-project/ray/blob/bf129559/doc/source/conf.py#L113-L113) The `Tuner` internally manages the conversion of user inputs into an experiment specification that encapsulates the HPO run.

 
### Core Configuration Entities

 
 - **`RunConfig`**: Defines runtime configurations for individual trials, including storage paths, checkpointing policies, and failure handling.
 - **`TuneConfig`**: Specifies HPO-specific settings such as the optimization metric, mode (min/max), search algorithm, scheduler, and the number of samples to draw.
 - **`Trial`**: Represents a single execution of a `Trainable` with a specific hyperparameter configuration. It tracks its own state (PENDING, RUNNING, TERMINATED, ERROR) and resource requirements.
 
 
### Tuner to Execution Bridge

 The following diagram illustrates how high-level API calls translate into the internal execution components.

 **Tuner Architecture Mapping**

 
```

```

 Sources: [doc/source/conf.py113](https://github.com/ray-project/ray/blob/bf129559/doc/source/conf.py#L113-L113) [python/ray/dashboard/modules/job/job_manager.py79](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/job_manager.py#L79-L79)

 
## Execution Engine and Trial Management

 The execution of a Tune experiment is driven by the `TuneController`. It manages the main event loop, interacting with the Ray cluster to request resources and launch trials as Ray Actors.

 The `TuneController` handles:

 
 - **Trial Lifecycle**: Transitioning trials through states and managing actor placement.
 - **Experiment Persistence**: Periodically saving the experiment state to allow for restoration after driver failures.
 - **Result Reporting**: Aggregating metrics reported by trials via `tune.report()` and passing them to schedulers.
 
 For a detailed deep dive into the execution loop and state management, see **[Tune Execution and Trial Management](https://deepwiki.com/ray-project/ray/7.1-tune-execution-and-trial-management)**.

 
## Search Algorithms and Schedulers

 Ray Tune decouples the generation of hyperparameter configurations from the scheduling of trial execution.

 
 - **Search Algorithms**: Implement the logic to suggest new configurations. Examples include `BasicVariantGenerator` for grid/random search and integrations with libraries like Optuna, HyperOpt, or BayesOpt.
 - **Schedulers**: Decide when to stop, pause, or exploit trials based on performance. Common schedulers include `ASHA` for early stopping and `PopulationBasedTraining` (PBT) for dynamic hyperparameter tuning.
 
 **Search and Schedule Interaction**

 
```

```

 Sources: [doc/source/conf.py113](https://github.com/ray-project/ray/blob/bf129559/doc/source/conf.py#L113-L113) [python/ray/dashboard/modules/job/job_manager.py133-150](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/job_manager.py#L133-L150)

 For details on specific algorithms and the search space API, see **[Search Algorithms and Schedulers](https://deepwiki.com/ray-project/ray/7.2-search-algorithms-and-schedulers)**.

 
## Experiment Management and Restoration

 Tune provides robust support for experiment management, including logging, checkpointing, and fault tolerance.

 
| Component | Description | Reference |
|---|---|---|
| ExperimentAnalysis | Utilities to analyze results, find the best trial, and load metrics dataframes. | doc/source/conf.py113 |
| JobManager | Manages the lifecycle of the Tune driver job and supervisor actors. | python/ray/dashboard/modules/job/job_manager.py57 |
| JobSupervisor | Ray actor responsible for setting up environment and executing the entrypoint. | python/ray/dashboard/modules/job/job_supervisor.py57 |
| GcsClient | Used for persisting experiment state and internal KV storage. | python/ray/tests/test_gcs_utils.py46 |

 Sources: [python/ray/dashboard/modules/job/job_manager.py57-88](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/job_manager.py#L57-L88) [python/ray/dashboard/modules/job/job_supervisor.py57-79](https://github.com/ray-project/ray/blob/bf129559/python/ray/dashboard/modules/job/job_supervisor.py#L57-L79) [python/ray/tests/test_gcs_utils.py43-68](https://github.com/ray-project/ray/blob/bf129559/python/ray/tests/test_gcs_utils.py#L43-L68)
