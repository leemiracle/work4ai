<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/genesys · page 5 Evolution System Components · fetched 2026-10-26 -->

# Evolution System Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bin/pages/design.py](bin/pages/design.py)
- [bin/pages/evolve.py](bin/pages/evolve.py)

</details>



## Purpose and Scope

This page provides a comprehensive overview of the core subsystems that drive Genesys's evolutionary model discovery process. It covers the main evolution loop, the `CommandCenter` orchestrator, the phylogenetic tree data structure, and how design and verification phases interact.

For details on specific subsystems:
- Selection algorithms and seed selection strategies: see [Selector and Selection Strategy](#5.1)
- Design agent workflow and implementation pipeline: see [Design Agents and Workflow](#5.2)
- Training and evaluation processes: see [Verification Engine](#5.3)
- Distributed node coordination: see [Distributed Coordination](#5.4)

---

## Evolution System Architecture

The evolution system implements a genetic programming paradigm where language models iteratively discover better language model architectures. The system operates through four main phases that form a closed feedback loop.

### High-Level Evolution Loop

```mermaid
graph TB
    subgraph "Selection Phase"
        PTree[("Phylogenetic Tree<br/>(evosys.ptree)")]
        Selector["Selector<br/>(evosys.selector)"]
        Seeds["Selected Seeds<br/>(design_ids)"]
    end
    
    subgraph "Design Phase"
        DesignSession["Design Session<br/>(sess_id)"]
        DesignAgents["Design Agents<br/>(DESIGN_PROPOSER,<br/>PROPOSAL_REVIEWER,<br/>etc.)"]
        Implementation["Implementation<br/>(DesignArtifact)"]
    end
    
    subgraph "Implementation Verification"
        FuncCheckers["Functional Checkers<br/>(format_checks,<br/>func_checks)"]
        ValidImpl["Valid Implementation<br/>(DesignArtifactImplemented)"]
    end
    
    subgraph "Verification Phase"
        Training["Model Training<br/>(Verification Engine)"]
        Evaluation["Evaluation<br/>(BabyLM tasks)"]
        Metrics["Performance Metrics<br/>(scores, loss)"]
    end
    
    PTree --> Selector
    Selector --> Seeds
    Seeds --> DesignSession
    DesignSession --> DesignAgents
    DesignAgents --> Implementation
    Implementation --> FuncCheckers
    FuncCheckers --> ValidImpl
    ValidImpl --> Training
    Training --> Evaluation
    Evaluation --> Metrics
    Metrics --> PTree
```

**Sources:** [README.md:1-190](), [bin/pages/evolve.py:1-2491]()

---

## CommandCenter: Workload Orchestration

The `CommandCenter` class is the master orchestrator that manages the evolution process across distributed nodes. It operates in two modes: **active mode** (orchestrating workloads) and **passive mode** (monitoring only).

### CommandCenter Architecture

```mermaid
graph TB
    subgraph "CommandCenter (Active Mode)"
        CC["CommandCenter<br/>(command_center)"]
        DocRef["Firebase Document<br/>(doc_ref)"]
        TaskQueue["Task Assignment Logic"]
    end
    
    subgraph "Node Monitoring"
        Connections["Active Connections<br/>(evosys.CM.connections)"]
        DesignWorkloads["Design Workloads<br/>(design_workloads dict)"]
        VerifyWorkloads["Verify Workloads<br/>(verify_workloads dict)"]
        Heartbeats["Node Heartbeats<br/>(last_heartbeat)"]
    end
    
    subgraph "Workload Assignment"
        AssignDesign["assign_design_workloads()<br/>(max_designs_per_node,<br/>max_designs_total)"]
        AssignVerify["assign_verify_workloads()<br/>(allow_resume)"]
        UserCommands["send_user_commands()<br/>(user_command_stack)"]
    end
    
    subgraph "Command Execution"
        DesignCmd["design_command()<br/>(node_id, sess_id)"]
        VerifyCmd["verify_command()<br/>(node_id, design_id, scale)"]
    end
    
    CC --> DocRef
    CC --> TaskQueue
    TaskQueue --> Connections
    Connections --> DesignWorkloads
    Connections --> VerifyWorkloads
    Connections --> Heartbeats
    
    TaskQueue --> AssignDesign
    TaskQueue --> AssignVerify
    TaskQueue --> UserCommands
    
    AssignDesign --> DesignCmd
    AssignVerify --> VerifyCmd
    UserCommands --> DesignCmd
    UserCommands --> VerifyCmd
```

**Sources:** [bin/pages/evolve.py:66-257]()

### Key CommandCenter Methods

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `run()` | Main orchestration loop | Poll frequency, zombie threshold |
| `assign_design_workloads()` | Distribute design tasks to nodes | `max_designs_per_node`, `max_designs_total` |
| `assign_verify_workloads()` | Distribute verification tasks | `allow_resume` |
| `send_user_commands()` | Process manual commands | `user_command_stack` |
| `build_connection()` | Establish coordination with Firebase | `active_mode` |
| `stop()` | Terminate orchestration | Updates Firebase status |

**Sources:** [bin/pages/evolve.py:66-257]()

### CommandCenter Configuration

```python
# Key constants from evolve.py
CC_POLL_FREQ = 30           # Poll frequency in seconds
CC_ZOMBIE_THRESHOLD = 60    # Node heartbeat timeout
CC_COMMAND_DELAY = 2        # Delay between command assignments
```

**Sources:** [bin/pages/evolve.py:42-44]()

---

## Phylogenetic Tree: Central State Management

The phylogenetic tree (`evosys.ptree`) is the central data structure that maintains the complete lineage of all designs, their relationships, verification results, and metadata.

### Phylogenetic Tree Structure

```mermaid
graph TB
    subgraph "Node Types in Tree"
        Root["Root Nodes<br/>(library seeds)"]
        Ref["Reference Nodes<br/>(ReferenceCore,<br/>ReferenceWithCode)"]
        Design["Design Artifacts<br/>(DesignArtifact)"]
        Impl["Implemented Designs<br/>(DesignArtifactImplemented)"]
    end
    
    subgraph "Node Data"
        Proposal["Proposal Data<br/>(node.proposal)"]
        Implementation["Implementation Data<br/>(node.implementation)"]
        Verifications["Verifications<br/>(node.verifications)"]
        State["State & Timestamp<br/>(node.state,<br/>node.timestamp)"]
    end
    
    subgraph "Tree Operations"
        FilterByType["filter_by_type()<br/>(return filtered nodes)"]
        GetNode["get_node(acronym)<br/>(return node object)"]
        GetUnfinished["get_unfinished_designs()<br/>(return sess_ids)"]
        GetScores["get_scores()<br/>(return dict by scale)"]
    end
    
    Root --> Ref
    Ref --> Design
    Design --> Impl
    
    Design --> Proposal
    Impl --> Implementation
    Impl --> Verifications
    Design --> State
    
    FilterByType --> Design
    FilterByType --> Impl
    GetNode --> Design
    GetUnfinished --> Design
    GetScores --> Verifications
```

**Sources:** [bin/pages/evolve.py:704-767]()

### Node States

Design nodes in the phylogenetic tree track their state through the implementation and verification process:

| State | Meaning | Transition |
|-------|---------|------------|
| `"proposed (unimplemented)"` | Proposal created, implementation pending | → implementing |
| `"implementing"` | Active implementation in progress | → implemented/failed |
| `"implemented (unverified)"` | Implementation complete, verification pending | → verified |
| `"implemented (verified)"` | Verification complete | Terminal state |
| `"failed"` | Proposal rejected by reviewer | Terminal state |
| `"unfinished (failed)"` | Implementation attempts exhausted | Terminal state |

**Sources:** [bin/pages/evolve.py:1264-1333]()

---

## Design Sessions: Implementation Pipeline

Design sessions manage the complete process of generating and implementing a model architecture from selected seeds through specialized LLM agents.

### Design Session Workflow

```mermaid
graph TB
    subgraph "Session Initialization"
        GenSessId["_gen_sess_id()<br/>(timestamp-uuid)"]
        AcquireLock["acquire_design_lock()<br/>(DESIGN_LOCK_TIMEOUT)"]
        CreateSession["Create Session Metadata<br/>(metadata.json)"]
    end
    
    subgraph "Design Modes"
        CheckSeeds["Check num_seeds"]
        Scratch["Scratch Mode<br/>(0 seeds)"]
        Mutation["Mutation Mode<br/>(1 seed)"]
        Crossover["Crossover Mode<br/>(2+ seeds)"]
    end
    
    subgraph "Agent Pipeline"
        Proposer["DESIGN_PROPOSER<br/>(generate proposals)"]
        Reviewer["PROPOSAL_REVIEWER<br/>(rate proposals)"]
        Planner["IMPLEMENTATION_PLANNER<br/>(plan structure)"]
        Coder["IMPLEMENTATION_CODER<br/>(write code)"]
        Observer["IMPLEMENTATION_OBSERVER<br/>(debug & test)"]
    end
    
    subgraph "Session Monitoring"
        SessionLog["Session Log<br/>(sess_id/log/*.log)"]
        Heartbeat["Heartbeat Updates<br/>(DESIGN_ZOMBIE_THRESHOLD)"]
        Daemon["Design Daemon<br/>(monitor zombie processes)"]
    end
    
    GenSessId --> AcquireLock
    AcquireLock --> CreateSession
    CreateSession --> CheckSeeds
    
    CheckSeeds --> Scratch
    CheckSeeds --> Mutation
    CheckSeeds --> Crossover
    
    Scratch --> Proposer
    Mutation --> Proposer
    Crossover --> Proposer
    
    Proposer --> Reviewer
    Reviewer --> Planner
    Planner --> Coder
    Coder --> Observer
    
    Observer --> SessionLog
    SessionLog --> Heartbeat
    Heartbeat --> Daemon
```

**Sources:** [bin/pages/design.py:50-161](), [bin/pages/design.py:167-204]()

### Design Session Functions

| Function | Purpose | Key Behavior |
|----------|---------|--------------|
| `design_command()` | Launch design session | Spawns subprocess + daemon monitor |
| `_design_command()` | Internal session runner | Acquires lock, resumes if unfinished |
| `design_daemon()` | Monitor session health | Detects zombies via heartbeat |
| `acquire_design_lock()` | Prevent concurrent sessions | Timeout-based lock mechanism |
| `run_design_thread()` | Execute design process | Calls `model_discovery.evolution --mode design` |

**Sources:** [bin/pages/design.py:50-204]()

### Design Lock Mechanism

```python
DESIGN_LOCK_TIMEOUT = 30  # seconds

# Lock prevents race conditions when resuming unfinished designs
# Located at: evosys.CM.get_design_lock_ref()
```

**Sources:** [bin/pages/design.py:25]()

---

## Verification Sessions: Model Training and Evaluation

Verification sessions train implemented designs and evaluate them on benchmark tasks to compute fitness scores.

### Verification Workflow

```mermaid
graph TB
    subgraph "Verification Initiation"
        SelectDesign["Select Design<br/>(design_id, scale)"]
        CheckUnverified["Check Verifications<br/>(node.verifications)"]
        AssignNode["Assign to Node<br/>(accept_verify_job)"]
    end
    
    subgraph "Training Phase"
        InitModel["Initialize Model<br/>(from implementation)"]
        TrainCorpus["Train on Corpus<br/>(smollm-12.5-corpus)"]
        SaveCkpt["Save Checkpoint<br/>(CKPT_DIR/sess_id)"]
        LogWandB["Log to W&B<br/>(wandb_ids.json)"]
    end
    
    subgraph "Evaluation Phase"
        LoadCkpt["Load Checkpoint"]
        RunEval["Run BabyLM Tasks<br/>(lm_eval harness)"]
        ComputeMetrics["Compute Metrics<br/>(blimp_filtered,<br/>blimp_supplement)"]
        UpdateTree["Update Tree<br/>(verification_report)"]
    end
    
    subgraph "Verification Results"
        TrainerState["trainer_state.json<br/>(loss, gradnorm)"]
        EvalResults["eval_results.json<br/>(task scores)"]
        WandBIds["wandb_ids.json<br/>(run tracking)"]
    end
    
    SelectDesign --> CheckUnverified
    CheckUnverified --> AssignNode
    AssignNode --> InitModel
    
    InitModel --> TrainCorpus
    TrainCorpus --> SaveCkpt
    SaveCkpt --> LogWandB
    
    LogWandB --> LoadCkpt
    LoadCkpt --> RunEval
    RunEval --> ComputeMetrics
    ComputeMetrics --> UpdateTree
    
    UpdateTree --> TrainerState
    UpdateTree --> EvalResults
    UpdateTree --> WandBIds
```

**Sources:** [bin/pages/evolve.py:466-504](), [README.md:116-127]()

### Verification Monitoring

Active verification sessions are tracked through Firebase and displayed in the network status:

| Field | Description | Source |
|-------|-------------|--------|
| `status` | Current training stage | Firebase log |
| `heartbeat` | Last update timestamp | Converted to datetime |
| `wandb_url` | W&B run URL | Constructed from `wandb_ids.json` |
| `node_id` | Executing node identifier | Firebase connection |
| `pid` | Process ID | System process |

**Sources:** [bin/pages/evolve.py:466-504]()

---

## Evolution Control Flow

The complete evolution cycle is managed through the `CommandCenter`'s `run()` method, which continuously polls for work and assigns tasks.

### Main Evolution Loop

```mermaid
graph TB
    Start["Start CommandCenter.run()"]
    
    CheckStop{"should_stop()?"}
    
    GetWorkloads["Get Design & Verify Workloads<br/>(evosys.CM.get_all_workloads())"]
    
    ProcessUserCmd["send_user_commands()<br/>(process user_command_stack)"]
    
    AssignDesign["assign_design_workloads()<br/>(check budgets & limits)"]
    
    AssignVerify["assign_verify_workloads()<br/>(assign to free nodes)"]
    
    UpdateHeartbeat["Update Heartbeat<br/>(doc_ref.update())"]
    
    Sleep["Sleep<br/>(remaining poll_freq time)"]
    
    Stop["Stop & Cleanup"]
    
    Start --> CheckStop
    CheckStop -->|"Yes"| Stop
    CheckStop -->|"No"| GetWorkloads
    
    GetWorkloads --> ProcessUserCmd
    ProcessUserCmd --> AssignDesign
    AssignDesign --> AssignVerify
    AssignVerify --> UpdateHeartbeat
    UpdateHeartbeat --> Sleep
    Sleep --> CheckStop
```

**Sources:** [bin/pages/evolve.py:207-248]()

### Budget and Limit Checks

The evolution system respects multiple constraints:

```python
# From CommandCenter.assign_design_workloads()
if evosys.remaining_verify_budget <= 0:
    # Stop assigning designs if no verification budget
    
if evosys.max_samples > 0 and evosys.finished_designs >= evosys.max_samples:
    # Stop if max designs reached
    
if total_design_workloads == max_designs_total:
    # Stop if parallel design limit reached
```

**Sources:** [bin/pages/evolve.py:113-156]()

---

## Session State Management

Both design and verification sessions maintain state through Firebase for distributed coordination.

### Design Session State Tracking

```mermaid
graph LR
    subgraph "Session Metadata"
        SessId["Session ID<br/>(sess_id)"]
        NodeId["Node ID<br/>(node_id)"]
        Pid["Process ID<br/>(pid)"]
        Status["Status<br/>(ACTIVE/ZOMBIE/TERMINATED)"]
        Progress["Progress<br/>(passed/implemented counts)"]
    end
    
    subgraph "Session Logs"
        LogRef["Log Reference<br/>(evosys.CM.get_session_log())"]
        Heartbeat["Heartbeat<br/>(timestamp)"]
        LatestLog["Latest Log Entry"]
    end
    
    subgraph "State Queries"
        GetSessionState["get_session_state(sess_id)<br/>(passed, implemented,<br/>challenging, unfinished)"]
        GetUnfinished["get_unfinished_designs()<br/>(return sess_ids)"]
    end
    
    SessId --> LogRef
    NodeId --> LogRef
    Status --> LogRef
    
    LogRef --> Heartbeat
    LogRef --> LatestLog
    
    GetSessionState --> Progress
    GetUnfinished --> Status
```

**Sources:** [bin/pages/design.py:114-161](), [bin/pages/design.py:226-278]()

### Session State Constants

```python
# From model_discovery.agents.flow.gau_flows
DESIGN_ACTIVE_STATES = [...]          # States indicating active session
DESIGN_TERMINAL_STATES = [...]        # States indicating completion
DESIGN_ZOMBIE_THRESHOLD = 60          # Heartbeat timeout in seconds
```

**Sources:** [bin/pages/design.py:19-20]()

---

## Data Persistence and Synchronization

The evolution system maintains state in three layers: local filesystem, session state cache, and Firebase remote database.

### Data Storage Architecture

```mermaid
graph TB
    subgraph "Local Storage"
        CkptDir["CKPT_DIR<br/>(checkpoint directory)"]
        EvoDir["evo_dir<br/>(namespace directory)"]
        DbDir["db_dir<br/>(phylogenetic tree data)"]
        SessionsDir["sessions/<br/>(design session logs)"]
        VeDir["ve/<br/>(verification results)"]
    end
    
    subgraph "Session State Cache"
        FilterByTypes["filter_by_types<br/>(cached node lists)"]
        DesignVectors["design_vectors<br/>(evaluation data)"]
        Leaderboards["leaderboards<br/>(normalized scores)"]
    end
    
    subgraph "Firebase Remote DB"
        ExpConnections["experiment_connections<br/>(CommandCenter state)"]
        NodeConnections["node_connections<br/>(worker heartbeats)"]
        ConfigDocs["config documents<br/>(shared settings)"]
        LogRefs["log references<br/>(session logs)"]
    end
    
    CkptDir --> EvoDir
    EvoDir --> DbDir
    EvoDir --> VeDir
    DbDir --> SessionsDir
    
    DbDir --> FilterByTypes
    VeDir --> DesignVectors
    DesignVectors --> Leaderboards
    
    ConfigDocs --> FilterByTypes
    ExpConnections --> LogRefs
    NodeConnections --> LogRefs
```

**Sources:** [bin/pages/evolve.py:689-702](), [README.md:56-67]()

---

## Benchmark Mode

The evolution system supports a special benchmark mode for agent evaluation, where design implementations are checked but not verified through training.

### Benchmark vs Evolution Mode

| Aspect | Evolution Mode | Benchmark Mode |
|--------|----------------|----------------|
| Verification | Full training + eval | Skipped (functional checks only) |
| Design Lock | None | Acquired per design attempt |
| Target | Discover better models | Evaluate agent capabilities |
| Stopping Condition | Budget/sample limits | All benchmarks attempted |
| Settings | `evosys.benchmark_mode = False` | `evosys.benchmark_mode = True` |

**Sources:** [bin/pages/evolve.py:620-687](), [bin/pages/evolve.py:861-1001]()

### Benchmark Design Lock

In benchmark mode, designs can only be attempted once at a time:

```python
# From CommandCenter.assign_design_workloads()
if evosys.benchmark_mode:
    if not evosys.ptree.acquire_design_lock():
        # Skip design assignment if lock held
        return
```

**Sources:** [bin/pages/evolve.py:124-127]()

---

## Component Integration Summary

The evolution system integrates four major subsystems into a cohesive feedback loop:

```mermaid
graph TB
    subgraph "1. Selection"
        S1["Selector analyzes tree"]
        S2["Selects seeds by utility/confidence"]
        S3["Provides instructions"]
    end
    
    subgraph "2. Design"
        D1["Design session created"]
        D2["Agents generate proposals"]
        D3["Implementation coded"]
    end
    
    subgraph "3. Verification"
        V1["Model trained"]
        V2["Benchmarks evaluated"]
        V3["Metrics computed"]
    end
    
    subgraph "4. Tree Update"
        T1["Results stored"]
        T2["Scores normalized"]
        T3["Lineage tracked"]
    end
    
    S1 --> S2
    S2 --> S3
    S3 --> D1
    
    D1 --> D2
    D2 --> D3
    D3 --> V1
    
    V1 --> V2
    V2 --> V3
    V3 --> T1
    
    T1 --> T2
    T2 --> T3
    T3 --> S1
```

**Sources:** [README.md:30-42](), [bin/pages/evolve.py:1-2491]()

For detailed information about each subsystem, refer to the dedicated sub-pages:
- [Selector and Selection Strategy](#5.1)
- [Design Agents and Workflow](#5.2)  
- [Verification Engine](#5.3)
- [Distributed Coordination](#5.4)

---

