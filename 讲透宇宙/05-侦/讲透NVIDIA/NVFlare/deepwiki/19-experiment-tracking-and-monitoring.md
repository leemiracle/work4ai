<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NVFlare · page 19 Experiment Tracking and Monitoring · fetched 2026-10-26 -->

# Experiment Tracking and Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/resources/log_config.json](docs/resources/log_config.json)
- [docs/user_guide/admin_guide/configurations/logging_configuration.rst](docs/user_guide/admin_guide/configurations/logging_configuration.rst)
- [docs/user_guide/nvflare_cli/fl_simulator.rst](docs/user_guide/nvflare_cli/fl_simulator.rst)
- [examples/tutorials/logging.ipynb](examples/tutorials/logging.ipynb)
- [examples/tutorials/self-paced-training/part-1_federated_learning_introduction/chapter-1_running_federated_learning_applications/01.7_logging/logging.ipynb](examples/tutorials/self-paced-training/part-1_federated_learning_introduction/chapter-1_running_federated_learning_applications/01.7_logging/logging.ipynb)
- [nvflare/apis/analytix.py](nvflare/apis/analytix.py)
- [nvflare/apis/utils/analytix_utils.py](nvflare/apis/utils/analytix_utils.py)
- [nvflare/app_common/app_event_type.py](nvflare/app_common/app_event_type.py)
- [nvflare/app_common/tracking/log_writer.py](nvflare/app_common/tracking/log_writer.py)
- [nvflare/app_common/tracking/tracker_types.py](nvflare/app_common/tracking/tracker_types.py)
- [nvflare/app_common/widgets/streaming.py](nvflare/app_common/widgets/streaming.py)
- [nvflare/app_opt/tracking/mlflow/__init__.py](nvflare/app_opt/tracking/mlflow/__init__.py)
- [nvflare/app_opt/tracking/mlflow/mlflow_receiver.py](nvflare/app_opt/tracking/mlflow/mlflow_receiver.py)
- [nvflare/app_opt/tracking/mlflow/mlflow_writer.py](nvflare/app_opt/tracking/mlflow/mlflow_writer.py)
- [nvflare/app_opt/tracking/tb/tb_receiver.py](nvflare/app_opt/tracking/tb/tb_receiver.py)
- [nvflare/app_opt/tracking/tb/tb_writer.py](nvflare/app_opt/tracking/tb/tb_writer.py)
- [nvflare/app_opt/tracking/wandb/wandb_receiver.py](nvflare/app_opt/tracking/wandb/wandb_receiver.py)
- [nvflare/app_opt/tracking/wandb/wandb_writer.py](nvflare/app_opt/tracking/wandb/wandb_writer.py)
- [nvflare/client/tracking.py](nvflare/client/tracking.py)
- [nvflare/fuel/utils/log_config.json](nvflare/fuel/utils/log_config.json)
- [nvflare/fuel/utils/log_utils.py](nvflare/fuel/utils/log_utils.py)
- [tests/unit_test/apis/analytix_test.py](tests/unit_test/apis/analytix_test.py)
- [tests/unit_test/app_common/widgets/streaming_test.py](tests/unit_test/app_common/widgets/streaming_test.py)
- [tests/unit_test/fuel/log_utils_dynamic_config_test.py](tests/unit_test/fuel/log_utils_dynamic_config_test.py)
- [tests/unit_test/job_config/log_config_env_var_test.py](tests/unit_test/job_config/log_config_env_var_test.py)

</details>



NVIDIA FLARE provides a robust framework for tracking and monitoring federated learning experiments. It allows developers to use familiar tools like **TensorBoard**, **MLflow**, and **Weights & Biases (W&B)** to visualize metrics from multiple client sites in a centralized or decentralized manner.

The system is built on a streaming analytics architecture that decouples metric generation in the training code from the actual logging backend. This flexibility allows users to switch between different tracking tools or change the logging topology (e.g., from server-side centralized logging to client-side local logging) purely through configuration, without modifying the training scripts.

### High-Level Architecture

The experiment tracking system utilizes an event-based streaming pattern. Metrics generated on the client are wrapped into a Data Exchange Object (`DXO`) of kind `DataKind.ANALYTIC` [nvflare/apis/analytix.py:122-125]() and transmitted across the federated network as analytic events (`analytix_log_stats`) [nvflare/apis/analytix.py:19-19]().

#### Data Flow and Code Entities
The following diagram illustrates how natural language tracking concepts map to specific code entities within the NVFLARE runtime:

**Metric Streaming Pipeline**
```mermaid
graph TD
    subgraph "Client_Logic"
        [LogWriter_Subclasses] -- "calls_write" --> [AnalyticsSender_add]
        [AnalyticsSender_add] -- "creates" --> [AnalyticsData_DXO]
    end

    subgraph "NVFLARE_Runtime_Events"
        [AnalyticsData_DXO] -- "event_analytix_log_stats" --> [AnalyticsSender_Widget]
        [AnalyticsSender_Widget] -- "Aux_Communication" --> [AnalyticsReceiver_Widget]
    end

    subgraph "Logging_Backend_Implementations"
        [AnalyticsReceiver_Widget] -- "save" --> [Backend_Receivers]
        [Backend_Receivers] -- "External_API" --> [Tracking_Service_Clients]
    end

    [LogWriter_Subclasses]["LogWriter (MLflowWriter/TBWriter/WandBWriter)"]
    [AnalyticsSender_add]["AnalyticsSender.add()"]
    [AnalyticsData_DXO]["AnalyticsData / DXO"]
    [AnalyticsSender_Widget]["AnalyticsSender (Widget)"]
    [AnalyticsReceiver_Widget]["AnalyticsReceiver (Widget)"]
    [Backend_Receivers]["TBAnalyticsReceiver / MLflowReceiver / WandBReceiver"]
    [Tracking_Service_Clients]["MlflowClient / wandb.log / TensorBoardEventWriter"]
```
Sources: [nvflare/app_common/widgets/streaming.py:28-79](), [nvflare/apis/analytix.py:76-103](), [nvflare/apis/analytix.py:19-19]()

### Core Components

1.  **Log Writers**: High-level APIs like `SummaryWriter`, `MLflowWriter`, and `WandBWriter` mimic standard third-party libraries. They instrument training code with methods like `log_metric()`, `log_params()`, or `add_scalar()`.
2.  **AnalyticsSender**: A `Widget` that handles the conversion of local logging calls into NVFLARE events (`analytix_log_stats`) that can be sent across the network via the engine's event system [nvflare/app_common/widgets/streaming.py:28-44](), [nvflare/app_common/widgets/streaming.py:69-71]().
3.  **AnalyticsReceiver**: An abstract base class for components that listen for analytic events (`EventType.START_RUN`, `ANALYTIC_EVENT_TYPE`, `EventType.END_RUN`) and commit them to a persistent store or tracking server [nvflare/app_common/widgets/streaming.py:79-135]().
4.  **AnalyticsData**: A wrapper class that defines the format for analytic data, providing helper methods to convert to and from `DXO` objects for transmission [nvflare/apis/analytix.py:76-123](). It supports various `AnalyticsDataType` such as `SCALAR`, `IMAGE`, `TEXT`, `PARAMETER`, and `METRICS` [nvflare/apis/analytix.py:57-75]().

### Supported Tracking Backends

NVFLARE provides built-in receivers for the most popular experiment tracking tools:

| Tool | Receiver Class | Key Features |
| :--- | :--- | :--- |
| **TensorBoard** | `TBAnalyticsReceiver` | Uses `TensorBoardEventWriter`. Supports `SCALAR`, `IMAGE`, `TEXT`, and `SCALARS` mapping [nvflare/app_opt/tracking/tb/tb_receiver.py:26-33](), [nvflare/app_opt/tracking/tb/tb_receiver.py:47-71](). |
| **MLflow** | `MLflowReceiver` | Uses `MlflowClient`. Supports tracking parameters, metrics, and experiments with configurable `buffer_flush_time` [nvflare/app_opt/tracking/mlflow/mlflow_receiver.py:53-84](). |
| **W&B** | `WandBReceiver` | Manages separate `wandb` runs for each client site using isolated `multiprocessing.Process` workers to handle concurrent site logging [nvflare/app_opt/tracking/wandb/wandb_receiver.py:58-73](), [nvflare/app_opt/tracking/wandb/wandb_receiver.py:166-168](). |

**Component Mapping**
```mermaid
graph LR
    subgraph "External_Tracking_Libraries"
        [TB_Writer_Entity]
        [ML_Client_Entity]
        [WB_Lib_Entity]
    end

    subgraph "NVFLARE_Receiver_Entities"
        [TBR_Class] -- "calls" --> [TB_Writer_Entity]
        [MLR_Class] -- "calls" --> [ML_Client_Entity]
        [WBR_Class] -- "puts_to_Queue" --> [WBP_Process]
        [WBP_Process] -- "calls" --> [WB_Lib_Entity]
    end

    subgraph "Base_Abstractions"
        [AR_ABC]
    end

    [TBR_Class] -- "inherits" --> [AR_ABC]
    [MLR_Class] -- "inherits" --> [AR_ABC]
    [WBR_Class] -- "inherits" --> [AR_ABC]

    [TB_Writer_Entity]["TensorBoardEventWriter"]
    [ML_Client_Entity]["mlflow.tracking.client.MlflowClient"]
    [WB_Lib_Entity]["wandb"]
    [TBR_Class]["TBAnalyticsReceiver"]
    [MLR_Class]["MLflowReceiver"]
    [WBR_Class]["WandBReceiver"]
    [WBP_Process]["WandB Process"]
    [AR_ABC]["AnalyticsReceiver (ABC)"]
```
Sources: [nvflare/app_opt/tracking/mlflow/mlflow_receiver.py:20-22](), [nvflare/app_opt/tracking/wandb/wandb_receiver.py:17-20](), [nvflare/app_common/widgets/streaming.py:79-79](), [nvflare/app_opt/tracking/tb/tb_receiver.py:24-24]()

### System Metrics Monitoring

In addition to machine learning experiment tracking, NVFLARE provides a framework for monitoring the FL system itself, focusing on job and system lifecycle metrics.

*   **Collection Framework**: The framework includes specialized components to publish metrics to a databus, integrating with StatsD, Prometheus, and Grafana.
*   **Standard Metrics**: Built-in metrics include event counts and time taken for operations like round starts (`AppEventType.ROUND_STARTED`) and training completion (`AppEventType.TRAINING_FINISHED`) [nvflare/app_common/app_event_type.py:50-60]().
*   **Job Lifecycle**: Metrics are published across various lifecycle stages, from `BEFORE_INITIALIZE` to `AFTER_TRAIN` [nvflare/app_common/app_event_type.py:28-31]().
*   **Logging System**: NVFLARE implements a structured logging system using `LogMode` (e.g., `CONCISE`, `VERBOSE`) and `BaseFormatter` to handle standard and JSON-formatted logs [nvflare/fuel/utils/log_utils.py:32-38](), [nvflare/fuel/utils/log_utils.py:114-131]().

For details, see [System Metrics Monitoring](#19.3).

### Child Pages

For detailed implementation guides and configuration examples, please refer to the following sub-pages:

*   **[Streaming Analytics Architecture](#19.1)**: Explains the underlying `AnalyticsSender`/`Receiver` pattern, the `AnalyticsDataType` enum, and the internal `DXO` data formats used for metrics [nvflare/apis/analytix.py:57-75](), [nvflare/app_common/widgets/streaming.py:28-135]().
*   **[TensorBoard, MLflow, and W&B Integration](#19.2)**: Provides step-by-step instructions on configuring receivers in your job's configuration and using high-level writers [nvflare/app_opt/tracking/mlflow/mlflow_receiver.py:53-127](), [nvflare/app_opt/tracking/wandb/wandb_receiver.py:58-177]().
*   **[System Metrics Monitoring](#19.3)**: Explains NVFLARE's system metrics collection framework, integration with StatsD/Prometheus/Grafana, and the role of metric publishing components based on `AppEventType` [nvflare/app_common/app_event_type.py:16-66]().

Sources: [nvflare/app_common/widgets/streaming.py:28-135](), [nvflare/app_opt/tracking/mlflow/mlflow_receiver.py:53-127](), [nvflare/app_opt/tracking/wandb/wandb_receiver.py:58-177](), [nvflare/apis/analytix.py:19-156](), [nvflare/fuel/utils/log_utils.py:32-167]()

---

