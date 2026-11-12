<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RD-Agent · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rdagent/app/cli.py](rdagent/app/cli.py)
- [rdagent/app/general_model/general_model.py](rdagent/app/general_model/general_model.py)
- [rdagent/app/qlib_rd_loop/factor.py](rdagent/app/qlib_rd_loop/factor.py)
- [rdagent/app/qlib_rd_loop/factor_from_report.py](rdagent/app/qlib_rd_loop/factor_from_report.py)
- [rdagent/app/qlib_rd_loop/model.py](rdagent/app/qlib_rd_loop/model.py)
- [rdagent/app/qlib_rd_loop/quant.py](rdagent/app/qlib_rd_loop/quant.py)
- [rdagent/components/workflow/rd_loop.py](rdagent/components/workflow/rd_loop.py)
- [rdagent/core/conf.py](rdagent/core/conf.py)
- [rdagent/core/exception.py](rdagent/core/exception.py)
- [rdagent/core/proposal.py](rdagent/core/proposal.py)
- [rdagent/core/utils.py](rdagent/core/utils.py)
- [rdagent/oai/llm_utils.py](rdagent/oai/llm_utils.py)
- [rdagent/scenarios/data_science/proposal/exp_gen/base.py](rdagent/scenarios/data_science/proposal/exp_gen/base.py)
- [rdagent/scenarios/data_science/proposal/exp_gen/merge.py](rdagent/scenarios/data_science/proposal/exp_gen/merge.py)
- [rdagent/scenarios/data_science/proposal/exp_gen/merge.yaml](rdagent/scenarios/data_science/proposal/exp_gen/merge.yaml)
- [rdagent/scenarios/qlib/factor_experiment_loader/pdf_loader.py](rdagent/scenarios/qlib/factor_experiment_loader/pdf_loader.py)
- [rdagent/scenarios/qlib/factor_experiment_loader/prompts.yaml](rdagent/scenarios/qlib/factor_experiment_loader/prompts.yaml)
- [rdagent/scenarios/qlib/proposal/quant_proposal.py](rdagent/scenarios/qlib/proposal/quant_proposal.py)
- [rdagent/utils/fmt.py](rdagent/utils/fmt.py)
- [rdagent/utils/workflow/loop.py](rdagent/utils/workflow/loop.py)
- [test/oai/test_completion.py](test/oai/test_completion.py)

</details>



This document explains the fundamental systems and abstractions that power RD-Agent's automated research and development capabilities. It covers the environment abstraction layer, workspace management system, experiment model, and configuration architecture that form the foundation for all R&D scenarios.

For specific R&D workflows and domain applications, see [R&D Loop Framework](#2.1). For execution environment details, see [Environment and Execution System](#2.3). For LLM integration patterns, see [LLM Integration and Backends](#2.4).

## Environment Abstraction Layer

RD-Agent provides a unified environment abstraction that allows code execution across different computational environments while maintaining consistent interfaces. The core abstraction is built around the `Env` class hierarchy.

```mermaid
classDiagram
    class Env {
        +ASpecificEnvConf conf
        +prepare()
        +run(entry, local_path, env) EnvResult
        +check_output() str
        +_run()* tuple[str, int]
    }
    
    class EnvConf {
        +str default_entry
        +dict extra_volumes
        +int running_timeout_period
        +bool enable_cache
        +int retry_count
    }
    
    class LocalEnv {
        +_run() tuple[str, int]
        +prepare()
    }
    
    class DockerEnv {
        +_run() tuple[str, int]
        +prepare()
        +_gpu_kwargs() dict
    }
    
    class LocalConf {
        +str bin_path
        +bool live_output
    }
    
    class DockerConf {
        +str image
        +str mount_path
        +bool build_from_dockerfile
        +str network
        +bool enable_gpu
        +str mem_limit
    }
    
    Env --> EnvConf
    LocalEnv --|> Env
    DockerEnv --|> Env
    LocalConf --|> EnvConf
    DockerConf --|> EnvConf
    LocalEnv --> LocalConf
    DockerEnv --> DockerConf
```

**Environment Execution Flow**

The environment system supports both local and containerized execution with automatic retry, caching, and timeout handling.

```mermaid
flowchart TD
    entry["Entry Command"] --> timeout_check{"Timeout Configured?"}
    timeout_check -->|Yes| timeout_wrap["Wrap with timeout command"]
    timeout_check -->|No| direct_exec["Direct execution"]
    timeout_wrap --> cache_check{"Cache Enabled?"}
    direct_exec --> cache_check
    
    cache_check -->|Yes| cache_lookup["Check cached_run()"]
    cache_check -->|No| retry_logic["__run_with_retry()"]
    
    cache_lookup --> cache_hit{"Cache Hit?"}
    cache_hit -->|Yes| return_cached["Return cached EnvResult"]
    cache_hit -->|No| retry_logic
    
    retry_logic --> env_type{"Environment Type"}
    env_type -->|Local| local_run["LocalEnv._run()"]
    env_type -->|Docker| docker_run["DockerEnv._run()"]
    
    local_run --> symlink_volumes["Create symlinks for volumes"]
    docker_run --> container_create["Create Docker container"]
    
    symlink_volumes --> subprocess_exec["subprocess.Popen()"]
    container_create --> container_run["container.run()"]
    
    subprocess_exec --> collect_output["Collect stdout/stderr"]
    container_run --> docker_logs["container.logs()"]
    
    collect_output --> env_result["EnvResult(stdout, exit_code, time)"]
    docker_logs --> env_result
    
    env_result --> retry_check{"Retry on Error?"}
    retry_check -->|Yes| retry_logic
    retry_check -->|No| final_result["Return EnvResult"]
```

**Sources:** [rdagent/utils/env.py:149-412](), [rdagent/utils/env.py:459-599](), [rdagent/utils/env.py:762-930]()

## Workspace Management System

The workspace system manages code, data, and execution state through the `Workspace` abstraction, with `FBWorkspace` providing file-based implementation for most scenarios.

```mermaid
classDiagram
    class Workspace {
        +ASpecificTask target_task
        +ASpecificFeedback feedback
        +RunningInfo running_info
        +execute()* object
        +copy()* Workspace
        +all_codes* str
        +create_ws_ckp()*
        +recover_ws_ckp()*
    }
    
    class FBWorkspace {
        +dict file_dict
        +Path workspace_path
        +bytes ws_ckp
        +str change_summary
        +prepare()
        +inject_files(**files)
        +execute(env, entry) str
        +run(env, entry) EnvResult
        +create_ws_ckp()
        +recover_ws_ckp()
    }
    
    class Task {
        +str name
        +int version
        +str description
        +get_task_information() str
    }
    
    class RunningInfo {
        +object result
        +float running_time
    }
    
    FBWorkspace --|> Workspace
    Workspace --> Task
    Workspace --> RunningInfo
```

**Workspace Lifecycle and File Management**

```mermaid
flowchart TD
    init["FBWorkspace.__init__()"] --> prepare["prepare()"]
    prepare --> inject["inject_files(**files)"]
    
    inject --> file_ops{"File Operations"}
    file_ops --> create_file["Write file to workspace_path"]
    file_ops --> delete_file["Delete file (DEL_KEY)"]
    file_ops --> update_dict["Update file_dict"]
    
    create_file --> execute_ready["Ready for Execution"]
    delete_file --> execute_ready
    update_dict --> execute_ready
    
    execute_ready --> run_method["run(env, entry)"]
    run_method --> env_run["env.run(entry, workspace_path)"]
    env_run --> filter_output["filter_redundant_text()"]
    filter_output --> shrink_output["shrink_text()"]
    shrink_output --> env_result["Return EnvResult"]
    
    execute_ready --> checkpoint["create_ws_ckp()"]
    checkpoint --> zip_workspace["zipfile.ZipFile creation"]
    zip_workspace --> store_bytes["Store in ws_ckp"]
    
    store_bytes --> recover["recover_ws_ckp()"]
    recover --> extract_zip["Extract from ws_ckp bytes"]
    extract_zip --> restore_files["Restore workspace_path"]
```

**Sources:** [rdagent/core/experiment.py:75-116](), [rdagent/core/experiment.py:127-362]()

## Experiment and Task Model

The experiment model organizes research work through `Task` and `Experiment` abstractions that coordinate multiple sub-tasks and their implementations.

```mermaid
classDiagram
    class Experiment {
        +Sequence[ASpecificTask] sub_tasks
        +list[ASpecificWSForSubTasks] sub_workspace_list
        +ASpecificWSForExperiment experiment_workspace
        +Hypothesis hypothesis
        +Feedback prop_dev_feedback
        +RunningInfo running_info
        +dict sub_results
        +ExperimentPlan plan
        +create_ws_ckp()
        +recover_ws_ckp()
    }
    
    class Task {
        +str name
        +int version
        +str description
        +get_task_information() str
    }
    
    class ExperimentPlan {
        <<dict[str, Any]>>
        +Planning information for experiment stages
    }
    
    class WsLoader {
        +load(task)* ASpecificWS
    }
    
    class Loader {
        +load(*args, **kwargs)* TaskOrExperiment
    }
    
    Experiment --> Task
    Experiment --> ExperimentPlan
    Experiment --> Workspace
    WsLoader --> Task
    WsLoader --> Workspace
```

**Experiment Execution Coordination**

```mermaid
flowchart TD
    exp_init["Experiment.__init__()"] --> sub_tasks["Initialize sub_tasks sequence"]
    sub_tasks --> ws_list["Initialize sub_workspace_list[None, ...]"]
    ws_list --> exp_ws["Set experiment_workspace = None"]
    
    exp_ws --> load_phase["Workspace Loading Phase"]
    load_phase --> ws_loader["WsLoader.load(task)"]
    ws_loader --> populate_ws["Populate sub_workspace_list"]
    
    populate_ws --> execution_phase["Execution Phase"]
    execution_phase --> iterate_tasks["Iterate through sub_tasks"]
    iterate_tasks --> task_exec["workspace.execute(env, entry)"]
    task_exec --> collect_results["Collect to sub_results"]
    
    collect_results --> checkpoint_phase["Checkpointing Phase"]
    checkpoint_phase --> exp_ckp["experiment_workspace.create_ws_ckp()"]
    exp_ckp --> sub_ckp["sub_workspace.create_ws_ckp()"]
    
    sub_ckp --> recovery_ready["Ready for Recovery"]
    recovery_ready --> recover_exp["experiment_workspace.recover_ws_ckp()"]
    recover_exp --> recover_sub["sub_workspace.recover_ws_ckp()"]
```

**Sources:** [rdagent/core/experiment.py:36-63](), [rdagent/core/experiment.py:374-450]()

## Configuration Architecture

RD-Agent uses a hierarchical configuration system based on `pydantic-settings` that supports environment variables and type validation for different execution contexts. The `ExtendedBaseSettings` class allows for prefix-based overrides across class hierarchies.

```mermaid
classDiagram
    class ExtendedBaseSettings {
        +settings_customise_sources()
        +Environment variable parsing
    }
    
    class RDAgentSettings {
        +Path workspace_path
        +int multi_proc_n
        +bool cache_with_pickle
        +int step_semaphore
    }
    
    class EnvConf {
        +str default_entry
        +dict extra_volumes
        +int running_timeout_period
        +bool enable_cache
        +int retry_count
    }
    
    class DockerConf {
        +str image
        +str mount_path
        +bool build_from_dockerfile
        +Path dockerfile_folder_path
        +str network
        +bool enable_gpu
    }
    
    ExtendedBaseSettings <|-- RDAgentSettings
    ExtendedBaseSettings <|-- EnvConf
    EnvConf <|-- DockerConf
```

**Configuration Resolution Flow**

The configuration system resolves settings from environment variables with prefix matching, allowing per-scenario customization. Classes like `RDAgentSettings` manage global execution parameters such as parallelism and workspace paths.

```mermaid
flowchart TD
    config_init["Configuration Initialization"] --> env_prefix["Check env_prefix setting"]
    env_prefix --> scan_env["Scan environment variables"]
    
    scan_env --> prefix_match{"Prefix Match?"}
    prefix_match -->|Yes| override_setting["Override specific setting"]
    prefix_match -->|No| base_setting["Use base class default"]
    
    override_setting --> validate["pydantic validation"]
    base_setting --> validate
    
    validate --> type_convert["Type conversion"]
    type_convert --> final_config["Final configuration object"]
    
    final_config --> env_creation["Environment creation"]
    env_creation --> get_ds_env["get_ds_env(conf_type)"]
    get_ds_env --> docker_or_conda{"env_type?"}
    
    docker_or_conda -->|docker| docker_env["DockerEnv(DSDockerConf)"]
    docker_or_conda -->|conda| local_env["LocalEnv(CondaConf)"]
    
    docker_env --> prepare_env["env.prepare()"]
    local_env --> prepare_env
```

**Sources:** [rdagent/core/conf.py:13-43](), [rdagent/core/conf.py:46-109](), [rdagent/utils/env.py:119-133](), [rdagent/utils/env.py:622-759]()

## Integration Points

The core architecture provides standardized integration points for higher-level systems:

| Integration Point | Interface | Purpose |
|------------------|-----------|---------|
| **Environment Factory** | `get_ds_env(conf_type, extra_volumes, ...)` | Creates configured environments for scenarios |
| **Workspace Loading** | `WsLoader.load(task) -> Workspace` | Loads task-specific workspaces |
| **Execution Interface** | `workspace.run(env, entry) -> EnvResult` | Executes code in isolated environments |
| **State Management** | `create_ws_ckp()` / `recover_ws_ckp()` | Checkpoints and restores workspace state |
| **LLM Backend** | `APIBackend()` | Dynamic LLM provider selection and chat completion |

This architecture enables the R&D loop system to orchestrate complex multi-stage experiments while maintaining isolation, reproducibility, and configurability across different computational environments.

**Sources:** [rdagent/core/experiment.py:120-125](), [rdagent/utils/env.py:182-245](), [rdagent/oai/llm_utils.py:35-44]()

---

