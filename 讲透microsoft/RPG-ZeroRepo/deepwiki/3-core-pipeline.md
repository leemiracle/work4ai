<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RPG-ZeroRepo · page 3 Core Pipeline · fetched 2026-10-26 -->

# Core Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [configs/checkpoint_config.yaml](configs/checkpoint_config.yaml)
- [configs/zerorepo_config.yaml](configs/zerorepo_config.yaml)

</details>



The Core Pipeline is the three-phase orchestration system that transforms a natural language project description into a complete, tested software repository. This page provides an architectural overview of how phases interact, what data flows between them, and how the system maintains state for resumability.

For detailed information about individual phase implementations, see [Phase 1: Feature Planning](#3.1), [Phase 2: Architecture Design](#3.2), and [Phase 3: Code Generation](#3.3). For configuration details, see [Configuration System](#4).

---

## Three-Phase Architecture

The pipeline consists of three sequential phases, each producing checkpoint files that serve as inputs to the next phase:

| Phase | Module | Entry Point | Input | Output |
|-------|--------|-------------|-------|--------|
| **Phase 1: Feature Planning** | `zerorepo/rpg_gen/prop_level/` | `PropBuilder.build_feature_tree()` | `repo_data.json` (name + purpose) | `repo_data.json` (with Feature_tree + Component) |
| **Phase 2: Architecture Design** | `zerorepo/rpg_gen/impl_level/` | `ImplBuilder.run()` | Feature_tree + Component | `skeleton.json`, `graph.json`, `tasks.json` |
| **Phase 3: Code Generation** | `zerorepo/code_gen/` | `IterativeCodeGenerator.task_executor()` | `tasks.json` | `workspace/` (generated repository) |

Each phase is idempotent and resumable. If interrupted, the system can skip completed phases and resume from the next incomplete stage.

**Sources:** [README.md:98-280](), [main.py](), [zerorepo_config.yaml]()

---

## Pipeline Data Flow

This diagram shows the concrete checkpoint files and code entities that connect the three phases:

**Pipeline Phase Transitions and Checkpoint Files**

```mermaid
graph TB
    subgraph Input["Input Layer"]
        UserDesc["Natural Language Description<br/>(repository_name, repository_purpose)"]
        RepoDataIn["repo_data.json<br/>Initial State"]
    end
    
    subgraph Phase1["Phase 1: Property Level<br/>zerorepo/rpg_gen/prop_level/"]
        PropBuilder["PropBuilder.build_feature_tree()"]
        FSA["FeatureSelectAgent"]
        FRA["FeatureRefactorAgent"]
        
        PropBuilder --> FSA
        FSA --> FeatSelection["feature_selection.json"]
        FeatSelection --> FRA
        FRA --> FeatRefactor["feature_refactoring.json"]
    end
    
    subgraph Phase1Out["Phase 1 Output"]
        RepoDataV2["repo_data.json<br/>+ Feature_tree<br/>+ Component[]"]
    end
    
    subgraph Phase2["Phase 2: Implementation Level<br/>zerorepo/rpg_gen/impl_level/"]
        ImplBuilder["ImplBuilder.run()"]
        FileDesigner["FileDesigner"]
        FuncDesigner["FuncDesigner"]
        TaskPlanner["TaskPlanner"]
        
        ImplBuilder --> InitRPG["Create Initial RPG"]
        InitRPG --> GlobalRPGV1["global_repo_rpg.json<br/>v1: Component nodes"]
        GlobalRPGV1 --> FileDesigner
        FileDesigner --> Skeleton["skeleton.json<br/>File/directory layout"]
        Skeleton --> FuncDesigner
        FuncDesigner --> Graph["graph.json<br/>Interface definitions"]
        Graph --> TaskPlanner
        TaskPlanner --> Tasks["tasks.json<br/>Implementation batches"]
        Tasks --> GlobalRPGV2["global_repo_rpg.json<br/>v2: Complete RPG"]
    end
    
    subgraph Phase3["Phase 3: Code Generation<br/>zerorepo/code_gen/"]
        ICG["IterativeCodeGenerator.task_executor()"]
        DockerExec["Docker Container<br/>(python-azure-pytest:3.12)"]
        TRAEAgent["TRAE Agent<br/>(LLM-powered coding agent)"]
        
        ICG --> DockerExec
        DockerExec --> TRAEAgent
        TRAEAgent --> IterState["iteration_state.json"]
        TRAEAgent --> ExecHistory["execution_history.json"]
        TRAEAgent --> BatchTraj["batch_trajectory.json"]
        TRAEAgent --> CurRPG["cur_repo_rpg.json<br/>Updated as code generates"]
    end
    
    subgraph Output["Output Layer"]
        Workspace["workspace/<br/>Generated Repository<br/>(src/, tests/, etc.)"]
        Results["results/<br/>Patches & trajectories"]
    end
    
    subgraph StateTracking["State Management"]
        TaskMgr["task_manager_state.json<br/>Progress tracking:<br/>- feature_selection_done<br/>- feature_refactoring_done<br/>- skeleton_done<br/>- graph_done<br/>- tasks_done<br/>- current_task<br/>- completed_tasks"]
    end
    
    UserDesc --> RepoDataIn
    RepoDataIn --> PropBuilder
    FeatRefactor --> RepoDataV2
    RepoDataV2 --> ImplBuilder
    GlobalRPGV2 --> ICG
    Tasks --> ICG
    TRAEAgent --> Workspace
    TRAEAgent --> Results
    
    PropBuilder -.->|"Updates"| TaskMgr
    ImplBuilder -.->|"Updates"| TaskMgr
    ICG -.->|"Updates"| TaskMgr
```

The pipeline transforms inputs through three distinct representations:

1. **Natural Language → Feature Tree**: User description becomes hierarchical taxonomy of features
2. **Feature Tree → Architecture**: Features mapped to file structure and interface specifications
3. **Architecture → Code**: Interface specifications filled with implementations via TDD

Each transition produces machine-readable JSON checkpoint files that enable phase independence and resumability.

**Sources:** [README.md:98-280](), [checkpoint_config.yaml](), [Diagram 2 from context]()

---

## Component Class Structure

The pipeline is implemented by three main builder classes, each managing a distinct phase:

**Core Pipeline Components and Their Relationships**

```mermaid
graph TB
    subgraph MainEntry["Entry Point: main.py"]
        MainFunc["main()"]
        LoadCheckpoints["load_checkpoint_manager()"]
        ParseArgs["ArgumentParser"]
    end
    
    subgraph Builders["Builder Classes"]
        PropBuilderCls["PropBuilder<br/>zerorepo/rpg_gen/prop_level/prop_builder.py"]
        ImplBuilderCls["ImplBuilder<br/>zerorepo/rpg_gen/impl_level/impl_builder.py"]
        CodeGenCls["IterativeCodeGenerator<br/>zerorepo/code_gen/iterative_code_generator.py"]
    end
    
    subgraph PropAgents["Phase 1 Agents"]
        FSAgent["FeatureSelectAgent<br/>feature_select_agent.py"]
        FRAgent["FeatureRefactorAgent<br/>feature_refactor_agent.py"]
    end
    
    subgraph ImplAgents["Phase 2 Agents"]
        FDAgent["FileDesigner<br/>file_designer.py<br/>(RawSkeletonAgent,<br/>GroupSkeletonAgent)"]
        FnDAgent["FuncDesigner<br/>func_designer.py<br/>(DataFlowAgent,<br/>BaseClassAgent,<br/>InterfaceAgent)"]
        TPAgent["TaskPlanner<br/>task_planner.py"]
    end
    
    subgraph CodeGenSys["Phase 3 System"]
        DockerMgr["DockerManager"]
        TRAESys["TRAE Agent System<br/>trae_agent package"]
        WorkflowExec["WorkflowExecutor"]
    end
    
    subgraph Shared["Shared Infrastructure"]
        CheckpointMgr["CheckpointManager<br/>checkpoint_manager.py"]
        RPGBuilder["RPGBuilder<br/>rpg_builder.py"]
        LLMClient["LLM Client<br/>llm/llm_client.py"]
    end
    
    MainFunc --> LoadCheckpoints
    LoadCheckpoints --> CheckpointMgr
    MainFunc --> PropBuilderCls
    MainFunc --> ImplBuilderCls
    MainFunc --> CodeGenCls
    
    PropBuilderCls --> FSAgent
    PropBuilderCls --> FRAgent
    PropBuilderCls --> CheckpointMgr
    PropBuilderCls --> LLMClient
    
    ImplBuilderCls --> FDAgent
    ImplBuilderCls --> FnDAgent
    ImplBuilderCls --> TPAgent
    ImplBuilderCls --> RPGBuilder
    ImplBuilderCls --> CheckpointMgr
    ImplBuilderCls --> LLMClient
    
    CodeGenCls --> DockerMgr
    CodeGenCls --> TRAESys
    CodeGenCls --> WorkflowExec
    CodeGenCls --> CheckpointMgr
    
    FSAgent --> LLMClient
    FRAgent --> LLMClient
    FDAgent --> LLMClient
    FnDAgent --> LLMClient
```

The `main()` function orchestrates phase execution by instantiating builder classes in sequence. Each builder depends on `CheckpointManager` for state persistence and `LLMClient` for model interactions (except Phase 3, which uses TRAE agent's internal LLM client).

**Sources:** [main.py](), [README.md:98-280](), [zerorepo/rpg_gen/prop_level/](), [zerorepo/rpg_gen/impl_level/](), [zerorepo/code_gen/]()

---

## Phase Orchestration

The `main()` function in [main.py]() controls phase execution based on command-line arguments and checkpoint state:

### Execution Flow

```mermaid
graph TD
    Start["main() Entry"]
    ParseCLI["Parse CLI Arguments<br/>--config, --checkpoint,<br/>--repo, --phase,<br/>--resume, --force-rebuild"]
    LoadConfig["Load zerorepo_config.yaml<br/>+ checkpoint_config.yaml<br/>+ llm_config.yaml"]
    InitCheckpoint["CheckpointManager.__init__()<br/>Load task_manager_state.json"]
    
    CheckPhase{"--phase<br/>argument"}
    
    CheckP1{"Phase 1<br/>Needed?"}
    RunP1["PropBuilder.build_feature_tree()<br/>+ save to repo_data.json<br/>+ update task_manager_state"]
    
    CheckP2{"Phase 2<br/>Needed?"}
    RunP2["ImplBuilder.run()<br/>+ save skeleton.json, graph.json, tasks.json<br/>+ update task_manager_state"]
    
    CheckP3{"Phase 3<br/>Needed?"}
    RunP3["IterativeCodeGenerator.task_executor()<br/>+ generate code in workspace/<br/>+ update task_manager_state"]
    
    Complete["Pipeline Complete"]
    
    Start --> ParseCLI
    ParseCLI --> LoadConfig
    LoadConfig --> InitCheckpoint
    InitCheckpoint --> CheckPhase
    
    CheckPhase -->|"all or prop"| CheckP1
    CheckPhase -->|"impl"| CheckP2
    CheckPhase -->|"code"| CheckP3
    
    CheckP1 -->|"Not done or<br/>--force-rebuild"| RunP1
    CheckP1 -->|"Done and<br/>--resume"| CheckP2
    RunP1 --> CheckP2
    
    CheckP2 -->|"Not done or<br/>--force-rebuild"| RunP2
    CheckP2 -->|"Done and<br/>--resume"| CheckP3
    RunP2 --> CheckP3
    
    CheckP3 -->|"Not done or<br/>--force-rebuild"| RunP3
    CheckP3 -->|"Done and<br/>--resume"| Complete
    RunP3 --> Complete
```

### Phase Selection Logic

The `--phase` argument determines which phases execute:

| Value | Behavior |
|-------|----------|
| `all` (default) | Run all three phases in sequence |
| `prop` | Run Phase 1 only (feature planning) |
| `impl` | Run Phase 2 only (architecture design) |
| `code` | Run Phase 3 only (code generation) |

When `--resume` is specified, completed phases are skipped based on flags in `task_manager_state.json`:
- `feature_selection_done` → skip `FeatureSelectAgent`
- `feature_refactoring_done` → skip `FeatureRefactorAgent`
- `skeleton_done` → skip `FileDesigner`
- `graph_done` → skip `FuncDesigner`
- `tasks_done` → skip `TaskPlanner`
- `completed_tasks[]` → skip completed implementation batches

The `--force-rebuild` flag clears completion flags, forcing phases to re-execute from scratch.

**Sources:** [main.py](), [README.md:354-380](), [checkpoint_config.yaml]()

---

## Checkpoint File Dependencies

Each phase produces specific checkpoint files that subsequent phases consume:

**Checkpoint File Dependency Graph**

```mermaid
graph LR
    subgraph Input["Input (User-Provided)"]
        RD0["repo_data.json<br/>{repository_name,<br/>repository_purpose}"]
    end
    
    subgraph P1Files["Phase 1 Checkpoints"]
        FS["feature_selection.json<br/>Raw feature taxonomy"]
        FR["feature_refactoring.json<br/>Component groupings"]
        RD1["repo_data.json<br/>+ Feature_tree<br/>+ Component[]"]
    end
    
    subgraph P2Files["Phase 2 Checkpoints"]
        RPG1["global_repo_rpg.json<br/>Initial RPG structure"]
        SKEL["skeleton.json<br/>File/directory layout"]
        SKELTRAJ["skeleton_traj.json<br/>LLM trajectories"]
        GRAPH["graph.json<br/>Interface definitions"]
        TASKS["tasks.json<br/>Implementation batches"]
        RPG2["global_repo_rpg.json<br/>Complete RPG with interfaces"]
    end
    
    subgraph P3Files["Phase 3 Checkpoints"]
        ITER["iteration_state.json<br/>Current iteration state"]
        EXEC["execution_history.json<br/>All workflow executions"]
        BATCH["batch_trajectory.json<br/>Per-batch execution records"]
        CRRPG["cur_repo_rpg.json<br/>Runtime RPG state"]
    end
    
    subgraph State["Global State"]
        TMS["task_manager_state.json<br/>Phase completion flags<br/>+ task progress"]
    end
    
    RD0 -->|"Phase 1 input"| FS
    FS --> FR
    FR --> RD1
    
    RD1 -->|"Phase 2 input"| RPG1
    RPG1 --> SKEL
    SKEL --> SKELTRAJ
    SKEL --> GRAPH
    GRAPH --> TASKS
    TASKS --> RPG2
    
    RPG2 -->|"Phase 3 input"| ITER
    TASKS -->|"Phase 3 input"| ITER
    ITER --> EXEC
    EXEC --> BATCH
    ITER --> CRRPG
    
    RD0 -.->|"Updated by all phases"| TMS
    RD1 -.->|"Updated by all phases"| TMS
    RPG2 -.->|"Updated by all phases"| TMS
```

### Critical Checkpoint Files

| File | Producer | Consumers | Purpose |
|------|----------|-----------|---------|
| `repo_data.json` | User (initial), Phase 1 (enriched) | Phase 1, Phase 2 | Master repository metadata with Feature_tree and Component definitions |
| `task_manager_state.json` | All phases | `main()`, All phases | Progress tracking and resume logic |
| `global_repo_rpg.json` | Phase 2 | Phase 3 | Complete Repository Planning Graph with all nodes/edges |
| `skeleton.json` | Phase 2 (`FileDesigner`) | Phase 2 (`FuncDesigner`) | File structure before interface design |
| `graph.json` | Phase 2 (`FuncDesigner`) | Phase 2 (`TaskPlanner`), Phase 3 | Complete interface definitions per file |
| `tasks.json` | Phase 2 (`TaskPlanner`) | Phase 3 | Implementation task batches with units and priorities |
| `cur_repo_rpg.json` | Phase 3 | Phase 3 | Dynamically updated RPG reflecting generated code |

The checkpoint system ensures that:
1. No phase is re-executed unnecessarily when resuming
2. Failures in later phases don't corrupt earlier work
3. Each phase can be developed/debugged independently

**Sources:** [README.md:383-399](), [checkpoint_config.yaml](), [Diagram 4 from context]()

---

## Configuration Hierarchy

The pipeline's behavior is controlled by a layered configuration system:

### Configuration File Structure

```mermaid
graph TB
    CLI["Command Line<br/>main.py --config ... --llm-config ..."]
    
    subgraph MainCfg["Primary Configuration"]
        ZRC["zerorepo_config.yaml<br/>Main orchestrator config"]
        
        ZRC_LLM["llm:<br/>model, provider, api_key,<br/>max_tokens, temperature"]
        ZRC_PROP["prop_level:<br/>feature_selection, feature_refactoring"]
        ZRC_IMPL["impl_level:<br/>file_design_cfg_path,<br/>func_design_cfg_path"]
        ZRC_CODE["code_generation:<br/>docker, trae_agent"]
        
        ZRC --> ZRC_LLM
        ZRC --> ZRC_PROP
        ZRC --> ZRC_IMPL
        ZRC --> ZRC_CODE
    end
    
    subgraph RefCfg["Referenced Configurations"]
        LLMCFG["llm_config.yaml<br/>(optional override)"]
        FDCFG["file_design_config.yaml<br/>RawSkeletonAgent,<br/>GroupSkeletonAgent params"]
        FNCFG["func_design_config.yaml<br/>DataFlowAgent, BaseClassAgent,<br/>InterfaceAgent params"]
        TRACFG["trae_config.yaml<br/>TRAE agent tools, models,<br/>max_steps"]
    end
    
    subgraph StateCfg["State Configuration"]
        CHKPT["checkpoint_config.yaml<br/>Checkpoint file definitions"]
    end
    
    CLI -.->|"--config"| ZRC
    CLI -.->|"--llm-config"| LLMCFG
    CLI -.->|"--checkpoint"| CHKPT
    
    ZRC_LLM -.->|"Can be overridden by"| LLMCFG
    ZRC_IMPL --> FDCFG
    ZRC_IMPL --> FNCFG
    ZRC_CODE --> TRACFG
```

### Configuration Loading Order

1. `main()` parses command-line arguments
2. Loads `zerorepo_config.yaml` from `--config` path
3. If `--llm-config` provided, overrides `llm` section
4. Loads `checkpoint_config.yaml` to initialize `CheckpointManager`
5. Phase 2 loads `file_design_config.yaml` and `func_design_config.yaml`
6. Phase 3 loads `trae_config.yaml` for TRAE agent

This hierarchy allows:
- **Global defaults** in `zerorepo_config.yaml`
- **LLM-specific overrides** via `--llm-config`
- **Phase-specific tuning** via referenced config files
- **State management schema** via `checkpoint_config.yaml`

**Sources:** [main.py](), [zerorepo_config.yaml:1-73](), [Diagram 3 from context](), [configs/]()

---

## Resume and Recovery Mechanism

The checkpoint system enables the pipeline to resume from any point without repeating expensive operations:

### Resume Logic Flow

```mermaid
graph TD
    Start["main() with --resume"]
    LoadState["Load task_manager_state.json"]
    
    CheckP1["Check feature_selection_done<br/>and feature_refactoring_done"]
    DecisionP1{"Phase 1<br/>Complete?"}
    RunP1["Execute PropBuilder"]
    SkipP1["Skip Phase 1"]
    
    CheckP2["Check skeleton_done,<br/>graph_done, tasks_done"]
    DecisionP2{"Phase 2<br/>Complete?"}
    RunP2["Execute ImplBuilder"]
    SkipP2["Skip Phase 2"]
    
    CheckP3["Check completed_tasks[]<br/>vs tasks.json batches"]
    DecisionP3{"Phase 3<br/>Complete?"}
    LoadTasks["Load tasks.json"]
    FilterTasks["Filter out completed_tasks"]
    RunP3["Execute IterativeCodeGenerator<br/>on remaining tasks"]
    SkipP3["Skip Phase 3"]
    
    Done["Pipeline Complete"]
    
    Start --> LoadState
    LoadState --> CheckP1
    CheckP1 --> DecisionP1
    DecisionP1 -->|"Yes"| SkipP1
    DecisionP1 -->|"No"| RunP1
    SkipP1 --> CheckP2
    RunP1 --> CheckP2
    
    CheckP2 --> DecisionP2
    DecisionP2 -->|"Yes"| SkipP2
    DecisionP2 -->|"No"| RunP2
    SkipP2 --> CheckP3
    RunP2 --> CheckP3
    
    CheckP3 --> DecisionP3
    DecisionP3 -->|"Yes"| SkipP3
    DecisionP3 -->|"No"| LoadTasks
    LoadTasks --> FilterTasks
    FilterTasks --> RunP3
    SkipP3 --> Done
    RunP3 --> Done
```

### task_manager_state.json Structure

```json
{
  "feature_selection_done": true,
  "feature_refactoring_done": true,
  "skeleton_done": true,
  "graph_done": true,
  "tasks_done": true,
  "code_generation": false,
  "completed_tasks": [
    "src_ai_pathfinding_astar.py_batch_1",
    "src_gameplay_rules_movement.py_batch_1"
  ],
  "failed_tasks": [
    "src_network_transport_reliability.py_batch_1"
  ],
  "current_task": {
    "task_id": "src_io_persistence_serialization.py_batch_1",
    "batch_name": "io.input_persistence",
    "iteration": 2,
    "last_workflow": "CODE_BUG_FIX"
  },
  "last_updated": "2026-02-09T14:23:45.123456"
}
```

### Recovery Capabilities

| Scenario | Behavior |
|----------|----------|
| **Phase 1 interrupted** | Resumes from `FeatureSelectAgent` or `FeatureRefactorAgent` based on completion flags |
| **Phase 2 interrupted** | Resumes from `FileDesigner`, `FuncDesigner`, or `TaskPlanner` |
| **Phase 3 interrupted** | Resumes from next uncompleted task batch; retries failed tasks |
| **Docker container crash** | Current task marked as failed; next run retries from iteration 0 |
| **LLM API error** | Task not marked complete; retry on next run |
| **Test failure at max iterations** | Task marked failed in `failed_tasks[]`; manual intervention required |

Failed tasks remain in `failed_tasks[]` until manually resolved. They can be retried by:
1. Removing the task from `failed_tasks[]` in `task_manager_state.json`
2. Running with `--resume`

Or by using `--force-rebuild` to restart all code generation from scratch.

**Sources:** [README.md:354-380](), [checkpoint_config.yaml](), [main.py](), [Diagram 4 from context]()

---

## Phase Input/Output Summary

This table summarizes the key transformations performed by each phase:

| Phase | Input Format | Output Format | Key Transformation |
|-------|--------------|---------------|-------------------|
| **Phase 1** | Natural language string: `"A multiplayer snake game..."` | Structured JSON: `Feature_tree` (hierarchical taxonomy), `Component[]` (logical modules) | Unstructured text → Structured feature hierarchy |
| **Phase 2** | Feature hierarchy + Components | File paths + Interface specifications: `skeleton.json` (76 files), `graph.json` (complete signatures, docstrings, types) | Abstract features → Concrete architecture |
| **Phase 3** | Interface specifications + Task batches | Executable Python code: `workspace/src/`, `workspace/tests/` | Type signatures → Working implementations |

### Data Size Growth

Using the SnakeGame example from the README:

- **Input**: ~50 words (project description)
- **After Phase 1**: ~200 features in Feature_tree, 6 Components
- **After Phase 2**: 76 files in skeleton, ~500 function/class interfaces in graph
- **After Phase 3**: ~5,000 lines of code, ~3,000 lines of tests

The pipeline expands a brief description into a complete repository through progressive refinement and LLM-guided generation.

**Sources:** [README.md:98-280](), [README.md:54-58](), [README.md:112-173](), [README.md:197-244]()

---

