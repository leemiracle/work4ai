<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ACV · extra page Experience Banks · fetched 2026-10-26 -->

# Experience Banks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/social-network.jsonl](self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/social-network.jsonl)
- [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/sock-shop.jsonl](self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/sock-shop.jsonl)

</details>



## Purpose and Scope

Experience Banks provide persistent storage for agent experiences in JSONL (JSON Lines) format, enabling the self-managing systems to learn from past actions and improve decision-making over time. This system stores structured records of agent activities across different microservice environments, supporting experience-based learning for both ClusterManager and ServiceMaintainer agents.

For information about how experiences are generated and filtered before storage, see [Experience Management](#2.3.2). For details on how stored experiences are retrieved and used during agent execution, see [Intent Execution System](#2.3.1).

## File System Organization

The experience banks are organized as environment-specific JSONL files within the AutoKube source tree:

```mermaid
graph TD
    root["self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/"]
    sockshop["sock-shop.jsonl"]
    socialnet["social-network.jsonl"]
    
    root --> sockshop
    root --> socialnet
    
    sockshop --> sockexp["Sock Shop Environment<br/>Agent Experiences"]
    socialnet --> socialexp["Social Network Environment<br/>Agent Experiences"]
```

**Storage Directory Structure**
| Environment | File Path | Purpose |
|-------------|-----------|---------|
| Sock Shop | `sock-shop.jsonl` | Experiences from sock-shop microservice demo |
| Social Network | `social-network.jsonl` | Experiences from DeathStarBench social network |

Sources: [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/sock-shop.jsonl:1-1](), [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/social-network.jsonl:1-2]()

## Experience Entry Format

Each experience entry follows a standardized JSON schema that captures the complete context and execution trace of an agent task:

```mermaid
graph LR
    entry["Experience Entry"]
    
    entry --> component["component"]
    entry --> tasktype["task_type"] 
    entry --> taskdesc["task_description"]
    entry --> result["result"]
    entry --> trajectories["trajectories[]"]
    
    trajectories --> step["step"]
    trajectories --> input["input"]
    trajectories --> output["output"] 
    trajectories --> reasoning["reasoning"]
    
    component --> compval["home-timeline-service"]
    tasktype --> tasktypeval["Monitoring"]
    taskdesc --> taskdescval["Check CPU usage..."]
    result --> resultval["success"]
```

**Core Experience Fields**
| Field | Type | Description |
|-------|------|-------------|
| `component` | string | Target microservice component name |
| `task_type` | string | Category of task (Monitoring, Scaling, etc.) |
| `task_description` | string | Natural language description of the task |
| `result` | string | Outcome status (success, failure) |
| `trajectories` | array | Step-by-step execution trace |

**Trajectory Step Fields**
| Field | Type | Description |
|-------|------|-------------|
| `step` | integer | Sequential step number |
| `input` | string | Command or action executed |
| `output` | string | Command output or response |
| `reasoning` | string | Agent's reasoning for the step |

Sources: [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/social-network.jsonl:1-1]()

## Experience Storage Schema

The following diagram illustrates how agent experiences map to the JSONL storage format:

```mermaid
graph TB
    subgraph "Agent Execution"
        agent["ServiceMaintainer Agent"]
        task["kubectl top pod command"]
        steps["Multi-step trajectory"]
    end
    
    subgraph "JSONL Storage Format"
        jsonentry["JSON Entry"]
        comp["component: home-timeline-service"]
        ttype["task_type: Monitoring"] 
        tdesc["task_description: Check CPU usage..."]
        res["result: success"]
        traj["trajectories: [step1, step2, ...]"]
    end
    
    subgraph "Trajectory Steps"
        step1["step: 1, input: No command, reasoning: Preparing..."]
        step2["step: 2, input: kubectl top pod..., output: CPU data"]
        step3["step: 3, reasoning: Inform CPU usage..."]
        step4["step: 4, input: report_result(...), reasoning: Reporting..."]
        step5["step: 5, reasoning: Terminate monitoring..."]
    end
    
    agent --> jsonentry
    task --> comp
    steps --> traj
    
    traj --> step1
    traj --> step2  
    traj --> step3
    traj --> step4
    traj --> step5
```

Sources: [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/social-network.jsonl:1-1]()

## Integration with Agent System

Experience banks integrate with the broader agent architecture through read/write operations during agent execution:

```mermaid
sequenceDiagram
    participant "ServiceMaintainer" as SM
    participant "Experience Manager" as EM  
    participant "Experience Bank" as EB
    participant "social-network.jsonl" as SNDB
    
    SM->>EM: "Execute monitoring task"
    EM->>SM: "Retrieve relevant experiences"
    EM->>SNDB: "Read matching experiences" 
    SNDB->>EM: "Return experience data"
    EM->>SM: "Provide context from past tasks"
    
    SM->>SM: "Execute kubectl commands"
    SM->>EM: "Store new experience"
    EM->>EM: "Format experience as JSON"
    EM->>SNDB: "Append to JSONL file"
    
    Note over SNDB: "Each line = one experience"
    Note over SNDB: "Persistent across agent restarts"
```

**Read Operations**: Experience retrieval for context-aware decision making
**Write Operations**: New experience persistence after successful task completion
**File Format**: JSONL enables incremental append operations without full file rewrites

Sources: [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/social-network.jsonl:1-1]()

## Environment-Specific Storage

Different microservice environments maintain separate experience banks to ensure context-appropriate learning:

**Sock Shop Environment**
- File: `sock-shop.jsonl`
- Focus: E-commerce microservice patterns
- Components: Frontend, catalogue, user services

**Social Network Environment** 
- File: `social-network.jsonl`
- Focus: Social media microservice patterns  
- Components: `home-timeline-service`, user-service, compose-post-service

This separation enables environment-specific optimization while maintaining experience portability across similar microservice architectures.

Sources: [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/sock-shop.jsonl:1-1](), [self_managing_systems/microservice/AutoKube/src/self_exploration/experience_bank/social-network.jsonl:1-1]()

---

