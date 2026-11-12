<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/lighteval · page 4 Evaluation Pipeline · fetched 2026-10-26 -->

# Evaluation Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/lighteval/logging/evaluation_tracker.py](src/lighteval/logging/evaluation_tracker.py)
- [src/lighteval/logging/info_loggers.py](src/lighteval/logging/info_loggers.py)
- [src/lighteval/main_accelerate.py](src/lighteval/main_accelerate.py)
- [src/lighteval/main_custom.py](src/lighteval/main_custom.py)
- [src/lighteval/main_endpoint.py](src/lighteval/main_endpoint.py)
- [src/lighteval/main_nanotron.py](src/lighteval/main_nanotron.py)
- [src/lighteval/main_sglang.py](src/lighteval/main_sglang.py)
- [src/lighteval/main_vllm.py](src/lighteval/main_vllm.py)
- [src/lighteval/pipeline.py](src/lighteval/pipeline.py)

</details>



The Evaluation Pipeline is the core execution system in LightEval that orchestrates the model evaluation process from start to finish. It manages loading models, creating and executing evaluation requests, computing metrics from model responses, and tracking results.

This page details how the pipeline works, from initialization to results tracking. For information about specific evaluation tasks, see [Tasks](#4), and for metrics systems, see [Metrics](#5).

## Core Components and Data Flow

The Evaluation Pipeline coordinates several key components that work together to evaluate language models:

```mermaid
graph TD
    subgraph "Pipeline Initialization"
        PClass["Pipeline"] --> PParams["PipelineParameters"]
        PClass --> ET["EvaluationTracker"]
        PClass --> Accel["Accelerator/ParallelContext"]
        PClass --> Model["LightevalModel"]
    end
    
    subgraph "Task & Request Management"
        PClass --> Registry["Registry"]
        Registry --> Tasks["LightevalTask"]
        Tasks --> |"create_requests_from_tasks()"| Requests["Evaluation Requests"]
        Tasks --> |"generates"| Docs["Doc objects"]
    end
    
    subgraph "Execution & Results"
        Requests --> |"model.process()"| Responses["Model Responses"]
        Docs --> |"reference data"| Metrics["Metrics Computation"]
        Responses --> |"predictions"| Metrics
        Metrics --> |"log()"| ET
        ET --> |"save()"| Results["Evaluation Results"]
        Results --> LocalFiles["Local Files"]
        Results --> Hub["Hugging Face Hub"]
        Results --> TensorBoard["TensorBoard"]
    end
```

Sources: 
- [src/lighteval/pipeline.py:131-156]
- [src/lighteval/pipeline.py:209-242]
- [src/lighteval/pipeline.py:458-477]

## Pipeline Initialization

The `Pipeline` class is initialized with task specifications, model configuration, and evaluation parameters:

```mermaid
classDiagram
    class Pipeline {
        +tasks: str
        +pipeline_parameters: PipelineParameters
        +evaluation_tracker: EvaluationTracker
        +model_config: ModelConfig
        +model: LightevalModel
        +accelerator: Accelerator
        +parallel_context: ParallelContext
        +requests: dict
        +docs: dict
        +task_dict: dict
        +fewshot_dict: dict
        +_init_parallelism_manager()
        +_init_model()
        +_init_tasks_and_requests()
        +_init_random_seeds()
        +evaluate()
        +_run_model()
        +_compute_metrics()
        +save_and_push_results()
        +show_results()
        +get_results()
    }
    
    class PipelineParameters {
        +launcher_type: ParallelismManager
        +job_id: int
        +dataset_loading_processes: int
        +nanotron_checkpoint_path: str
        +custom_tasks_directory: str
        +num_fewshot_seeds: int
        +max_samples: int
        +use_chat_template: bool
        +system_prompt: str
        +cot_prompt: str
        +load_responses_from_details_date_id: str
    }
    
    class ParallelismManager {
        <<enum>>
        ACCELERATE
        NANOTRON
        TGI
        OPENAI
        VLLM
        NONE
        SGLANG
    }
    
    Pipeline *-- PipelineParameters
    PipelineParameters *-- ParallelismManager
```

Sources: 
- [src/lighteval/pipeline.py:131-164]
- [src/lighteval/pipeline.py:94-129]
- [src/lighteval/pipeline.py:84-91]

The initialization process involves these key steps:

1. Setup the parallelism manager based on the backend type (Accelerate, Nanotron, etc.)
2. Load the model with the appropriate configuration
3. Initialize the task registry and create evaluation requests
4. Set random seeds for reproducibility

```python
def __init__(self, tasks, pipeline_parameters, evaluation_tracker, model_config=None, model=None, metric_options=None):
    # Initialize components
    self.accelerator, self.parallel_context = self._init_parallelism_manager()
    self.model = self._init_model(model_config, model)
    
    # Log model information
    self.evaluation_tracker.general_config_logger.log_model_info(...)
    
    # Initialize tasks and requests
    self._init_random_seeds()
    self._init_tasks_and_requests(tasks=tasks)
```

Sources: 
- [src/lighteval/pipeline.py:132-164]

## The Evaluation Process

The complete evaluation workflow is orchestrated by the `evaluate()` method:

```mermaid
sequenceDiagram
    participant Pipeline
    participant Model as LightevalModel
    participant Tasks as LightevalTask
    participant Metrics as MetricFunctions
    participant Tracker as EvaluationTracker
    
    Note over Pipeline: Start evaluation
    Pipeline->>Tracker: Log configuration info
    
    alt Load responses from previous run
        Pipeline->>Pipeline: _load_responses_from_details()
    else Run model on requests
        Pipeline->>Pipeline: _run_model()
        loop For each request type
            Pipeline->>Model: get_method_from_request_type()
            Model-->>Pipeline: method (e.g., loglikelihood, greedy_until)
            Pipeline->>Model: method(requests)
            Model-->>Pipeline: responses
            Pipeline->>Pipeline: Group responses by sample ID and metric category
        end
    end
    
    Pipeline->>Pipeline: _compute_metrics(sample_id_to_responses)
    
    loop For each task and metric category
        Pipeline->>Tasks: get_metric_method_from_category()
        Tasks-->>Pipeline: metric_function
        Pipeline->>Metrics: metric_function(samples, responses, docs, metrics)
        Metrics-->>Pipeline: outputs
        
        loop For each result
            Pipeline->>Tracker: metrics_logger.log(task_name, output)
            Pipeline->>Tracker: details_logger.log(task_name, task, doc, response, output)
        end
    end
    
    alt Is main process
        Pipeline->>Tracker: metrics_logger.aggregate()
        Pipeline->>Tracker: details_logger.aggregate()
    end
    
    Note over Pipeline: Finalize evaluation
```

Sources:
- [src/lighteval/pipeline.py:272-304]
- [src/lighteval/pipeline.py:458-527]

## Request and Response Flow

The pipeline handles different request types, each processed by specific model methods:

```mermaid
graph TD
    subgraph "Request Types"
        Request["Request Base Class"] --> LLR["LoglikelihoodRequest"]
        Request --> LLSTR["LoglikelihoodSingleTokenRequest"]
        Request --> LLRR["LoglikelihoodRollingRequest"]
        Request --> GUR["GreedyUntilRequest"]
        Request --> GUMTR["GreedyUntilMultiTurnRequest"]
    end
    
    subgraph "Model Methods"
        LLR --> |"runs"| LLM["model.loglikelihood()"]
        LLSTR --> |"runs"| LLSTM["model.loglikelihood_single_token()"]
        LLRR --> |"runs"| LLRM["model.loglikelihood_rolling()"]
        GUR --> |"runs"| GUM["model.greedy_until()"]
        GUMTR --> |"runs"| GUMTM["model.greedy_until_multi_turn()"]
    end
    
    subgraph "Response Types"
        ModelResponse["ModelResponse Base Class"] --> LLResp["LoglikelihoodResponse"]
        ModelResponse --> LLSTResp["LoglikelihoodSingleTokenResponse"] 
        ModelResponse --> GResp["GenerativeResponse"]
        ModelResponse --> GMTResp["GenerativeMultiturnResponse"]
        
        LLM --> LLResp
        LLSTM --> LLSTResp
        LLRM --> LLResp
        GUM --> GResp
        GUMTM --> GMTResp
    end
```

Sources:
- [src/lighteval/models/model_output.py:40-46]
- [src/lighteval/tasks/requests.py:49]

The `_run_model` method executes requests and organizes responses:

```python
def _run_model(self):
    # Dictionary to store responses, keyed by (sample_id, metric_category)
    sample_id_to_responses = collections.defaultdict(list)
    
    # Process each request type (loglikelihood, generative, etc.)
    for request_type, requests in self.requests.items():
        # Get the appropriate model method for this request type
        run_model = self.model.get_method_from_request_type(request_type=request_type)
        # Execute all requests of this type in batch
        responses = run_model(requests)
        
        # Store the responses by sample ID and metric category
        for response, request in zip(responses, requests):
            for metric_category in request.metric_categories:
                sample_id = SampleUid(request.task_name, request.sample_index)
                sample_id_to_responses[(sample_id, metric_category)].append(response)
    
    return sample_id_to_responses
```

Sources:
- [src/lighteval/pipeline.py:458-477]

## Metrics Computation

After collecting model responses, the pipeline computes metrics through the `_compute_metrics` method:

```mermaid
graph TD
    subgraph "Metrics Computation Flow"
        Responses["Model Responses"] --> Group["Group by Task + Metric Category"]
        Group --> |"For each task"| TaskProcess["Process Task"]
        TaskProcess --> |"For each metric category"| MetricProcess["Process Metric Category"]
        MetricProcess --> |"Get metric function"| MetricFunc["task.get_metric_method_from_category()"]
        MetricFunc --> MetricApply["Apply metric function"]
        MetricApply --> Outputs["Metric Outputs"]
        Outputs --> Log["Log results to tracker"]
    end
    
    subgraph "Metric Categories"
        MC["MetricCategory"] --> PERP["PERPLEXITY"]
        MC --> TPERP["TARGET_PERPLEXITY"]
        MC --> GEN["GENERATIVE"]
        MC --> MCPMI["MULTICHOICE_PMI"]
        MC --> MCH["MULTICHOICE"]
        MC --> MCHOT["MULTICHOICE_ONE_TOKEN"]
        MC --> LLMJ["LLM_AS_JUDGE"]
    end
    
    subgraph "Metric Functions"
        PERP --> APM["apply_perplexity_metric()"]
        TPERP --> ATPM["apply_target_perplexity_metric()"]
        GEN --> AGM["apply_generative_metric()"]
        MCPMI --> AMCM["apply_multichoice_metric()"]
        MCH --> AMCM
        MCHOT --> AMCOTM["apply_multichoice_metric_one_token()"]
        LLMJ --> ALLMJM["apply_llm_as_judge_metric()"]
    end
```

Sources:
- [src/lighteval/pipeline.py:484-527]
- [src/lighteval/metrics/__init__.py:30-241]

The metric computation process follows these steps:

1. Group responses by task name and metric category
2. For each task and metric category:
   - Get the appropriate metric function based on the category
   - Apply the function to the responses and reference data
   - Log the results to the `metrics_logger` and `details_logger`

```python
def _compute_metrics(self, sample_id_to_responses):
    # Group responses by task and metric category
    task_metric_category_groups = collections.defaultdict(
        lambda: collections.defaultdict(lambda: collections.defaultdict(list))
    )
    
    for (sample_id, metric_category), sample_responses in sample_id_to_responses.items():
        task_metric_category_groups[sample_id.task_name][metric_category]["ids"].append(sample_id.doc_id_seed)
        task_metric_category_groups[sample_id.task_name][metric_category]["responses"].append(sample_responses)
        task_metric_category_groups[sample_id.task_name][metric_category]["docs"].append(self.docs[sample_id])
    
    # Process each group and apply metrics
    for task_name, samples_per_metric in task_metric_category_groups.items():
        task = self._get_task(task_name)
        
        for metric_category, samples in samples_per_metric.items():
            metric_function = task.get_metric_method_from_category(metric_category=metric_category)
            metric_category_metrics = [m for m in task.metrics if m.category == metric_category]
            
            outputs = metric_function(
                sample_ids=samples["ids"],
                responses=samples["responses"],
                formatted_docs=samples["docs"],
                metrics=metric_category_metrics,
            )
            
            # Log results
            for output, doc, response in zip(outputs, samples["docs"], samples["responses"]):
                self.evaluation_tracker.metrics_logger.log(task_name, output)
                self.evaluation_tracker.details_logger.log(task_name, task, doc, response, output)
```

Sources:
- [src/lighteval/pipeline.py:484-527]

## Results Tracking and Management

The `EvaluationTracker` class is responsible for tracking and managing evaluation results:

```mermaid
classDiagram
    class EvaluationTracker {
        +details_logger: DetailsLogger
        +metrics_logger: MetricsLogger
        +versions_logger: VersionsLogger
        +general_config_logger: GeneralConfigLogger
        +task_config_logger: TaskConfigLogger
        +output_dir: str
        +hub_results_org: str
        +should_push_to_hub: bool
        +should_save_details: bool
        +should_push_results_to_tensorboard: bool
        +tensorboard_repo: str
        +public: bool
        +save()
        +save_results(date_id, results_dict)
        +save_details(date_id, details_datasets)
        +push_to_hub(date_id, details, results_dict)
        +push_to_tensorboard(results, details)
        +generate_final_dict()
    }
    
    class DetailsLogger {
        +details: dict
        +compiled_details: dict
        +compiled_details_over_all_tasks: CompiledDetailOverAllTasks
        +log(task_name, task, doc, response, output)
        +aggregate()
    }
    
    class MetricsLogger {
        +metrics: dict
        +metric_aggregated: dict
        +log(task_name, output)
        +aggregate(task_dict, bootstrap_iters)
    }
    
    EvaluationTracker *-- DetailsLogger
    EvaluationTracker *-- MetricsLogger
    EvaluationTracker *-- VersionsLogger
    EvaluationTracker *-- GeneralConfigLogger
    EvaluationTracker *-- TaskConfigLogger
```

Sources:
- [src/lighteval/logging/evaluation_tracker.py:87-669]

The `save` method in `EvaluationTracker` handles saving results and optionally pushing to the Hugging Face Hub:

```mermaid
graph TD
    Save["EvaluationTracker.save()"] --> Date["Generate date_id"]
    Date --> ResultsDict["Prepare results_dict"]
    Date --> DetailDatasets["Prepare details_datasets"]
    
    ResultsDict --> SaveResults["save_results(date_id, results_dict)"]
    SaveResults --> ResultsFiles["Local results files"]
    
    DetailDatasets --> CheckSaveDetails{"should_save_details?"}
    CheckSaveDetails --> |"Yes"| SaveDetails["save_details(date_id, details_datasets)"]
    SaveDetails --> DetailsFiles["Local details files"]
    
    ResultsDict --> CheckPushHub{"should_push_to_hub?"}
    DetailDatasets --> CheckPushHub
    CheckPushHub --> |"Yes"| PushHub["push_to_hub(date_id, details, results_dict)"]
    PushHub --> HFHub["Hugging Face Hub dataset"]
    
    ResultsDict --> CheckPushTB{"should_push_results_to_tensorboard?"}
    DetailDatasets --> CheckPushTB
    CheckPushTB --> |"Yes"| PushTB["push_to_tensorboard(results, details)"]
    PushTB --> TB["TensorBoard logs"]
```

Sources:
- [src/lighteval/logging/evaluation_tracker.py:178-228]

The saved results include:
- General configuration information
- Task configurations and versions
- Metric results for each task
- Detailed information about each evaluation sample
- Summary statistics across all tasks

```python
# Structure of the results_dict
results_dict = {
    "config_general": config_general,
    "results": self.metrics_logger.metric_aggregated,
    "versions": self.versions_logger.versions,
    "config_tasks": self.task_config_logger.tasks_configs,
    "summary_tasks": self.details_logger.compiled_details,
    "summary_general": asdict(self.details_logger.compiled_details_over_all_tasks),
}
```

Sources:
- [src/lighteval/logging/evaluation_tracker.py:188-195]

## Dynamic Batching for Performance

The evaluation pipeline uses dynamic batching to process requests efficiently:

```mermaid
classDiagram
    class DynamicBatchDataset {
        <<Abstract>>
        +sorted_data: list
        +original_order: list
        +total_size: int
        +num_dataset_splits: int
        +splits: list
        +split_start: int
        +split_end: int
        +init_split_limits(num_dataset_splits)
        +get_original_order(new_arr)
        +get_split_start_end(split_id)
        +splits_start_end_iterator()
        +__getitem__(index)
        +__len__()
        +__iter__()
        +_sorting_criteria(request)
    }
    
    class LoglikelihoodDataset {
        +_sorting_criteria(request)
    }
    
    class LoglikelihoodSingleTokenDataset {
        +_sorting_criteria(request)
    }
    
    class GenerativeTaskDataset {
        +init_split_limits(num_dataset_splits)
        +_sorting_criteria(request)
    }
    
    DynamicBatchDataset <|-- LoglikelihoodDataset
    DynamicBatchDataset <|-- LoglikelihoodSingleTokenDataset
    DynamicBatchDataset <|-- GenerativeTaskDataset
```

Sources:
- [src/lighteval/data.py:50-303]

The dynamic batching system:
1. Sorts requests based on a criterion (typically sequence length)
2. Splits the dataset into manageable chunks
3. Processes each chunk with an appropriate batch size
4. Restores the original ordering of results

This efficient batching approach allows for maximum GPU utilization by grouping similar-length requests together, reducing padding waste and memory usage.

## Integration with Distributed Computing

The Pipeline supports distributed evaluation through different parallelism managers:

```mermaid
graph TD
    subgraph "Parallelism Managers"
        PM["ParallelismManager Enum"] --> ACC["ACCELERATE"]
        PM --> NANO["NANOTRON"]
        PM --> VLLM["VLLM"]
        PM --> TGI["TGI"]
        PM --> OAI["OPENAI"]
        PM --> SGL["SGLANG"]
        PM --> NONE["NONE"]
    end
    
    subgraph "Initialization"
        PClass["Pipeline._init_parallelism_manager()"] --> CheckType{"launcher_type?"}
        CheckType --> |"ACCELERATE"| InitAcc["Initialize Accelerator"]
        CheckType --> |"NANOTRON"| InitNano["Initialize ParallelContext"]
        CheckType --> |"Other"| NoInit["No special initialization"]
    end
    
    subgraph "Results Management"
        PClass2["Pipeline.is_main_process()"] --> CheckPM{"Which parallelism?"}
        CheckPM --> |"Accelerator"| CheckAcc["accelerator.is_main_process"]
        CheckPM --> |"Nanotron"| CheckNano["dist.get_rank(...) == 0"]
        CheckPM --> |"Other"| RetTrue["Return True"]
    end
```

Sources:
- [src/lighteval/pipeline.py:84-91]
- [src/lighteval/pipeline.py:165-184]
- [src/lighteval/pipeline.py:265-270]

This distributed computing support enables efficient evaluation of large models across multiple GPUs and nodes.

## Summary

The Evaluation Pipeline is the core orchestration system in LightEval that:

1. Loads models and tasks
2. Creates evaluation requests based on task configurations
3. Processes requests with the appropriate model backend
4. Computes metrics from model responses
5. Tracks, aggregates, and saves results

This flexible architecture allows LightEval to evaluate various language models across different tasks and metrics while providing comprehensive result tracking and analysis capabilities.

Sources:
- [src/lighteval/pipeline.py]
- [src/lighteval/logging/evaluation_tracker.py]
- [src/lighteval/metrics/__init__.py]
- [src/lighteval/data.py]

---

