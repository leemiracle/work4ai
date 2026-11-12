<!-- source: DeepWiki mcp.deepwiki.com · repo MineDojo/Voyager · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [voyager/agents/__init__.py](voyager/agents/__init__.py)
- [voyager/voyager.py](voyager/voyager.py)

</details>



This page documents the core architecture of Voyager, an LLM-powered embodied lifelong learning agent for Minecraft. It provides a technical overview of the system's main components, their interactions, and the control flow that enables Voyager's learning capabilities. For installation instructions, see [Installation and Setup](#2), and for detailed explanations of individual agent components, see [Agents](#4).

## System Overview

Voyager is built on a multi-agent architecture that enables autonomous exploration, skill acquisition, and task execution in Minecraft. The system is designed around a central orchestrator that coordinates specialized agents, manages communication with the Minecraft environment, and implements a continuous learning process.

```mermaid
graph TD
    subgraph "Voyager System"
        V["Voyager"] --> AA["ActionAgent"]
        V --> CA["CurriculumAgent"]
        V --> CRA["CriticAgent"]
        V --> SM["SkillManager"]
        V --> VE["VoyagerEnv"]
    end
    
    VE --> MC["Minecraft"]
    SM <--> SL["Skill Library"]
    
    AA --> LLM["GPT-4/3.5"]
    CA --> LLM
    CRA --> LLM
    SM --> LLM
    
    style V stroke-width:2px
```

**System Components Diagram: Voyager Core Architecture**

Sources: [voyager/voyager.py:17-412](), [README.md:21-37]()

## Key Components and Their Roles

The Voyager system consists of five key components, each with a specific responsibility in the learning and task execution process:

| Component | Role | Implementation |
|-----------|------|----------------|
| **Voyager** | Central orchestrator that coordinates the entire system | [voyager/voyager.py:17-368]() |
| **ActionAgent** | Generates JavaScript code to perform tasks in Minecraft | [voyager/voyager.py:118-127]() |
| **CurriculumAgent** | Proposes new tasks and maintains learning progress | [voyager/voyager.py:128-139]() |
| **CriticAgent** | Evaluates task success and provides feedback | [voyager/voyager.py:140-145]() |
| **SkillManager** | Maintains a library of learned skills for reuse | [voyager/voyager.py:146-153]() |
| **VoyagerEnv** | Interfaces with the Minecraft environment | [voyager/voyager.py:104-109]() |

Sources: [voyager/voyager.py:17-153](), [voyager/agents/__init__.py:1-4]()

## Voyager Class Implementation

The `Voyager` class serves as the central orchestrator of the entire system. It initializes all components, manages their interactions, and implements the main learning loop.

```mermaid
classDiagram
    class Voyager {
        -VoyagerEnv env
        -ActionAgent action_agent
        -CurriculumAgent curriculum_agent
        -CriticAgent critic_agent
        -SkillManager skill_manager
        -EventRecorder recorder
        +learn()
        +reset(task, context, reset_env)
        +step()
        +rollout(task, context, reset_env)
        +decompose_task(task)
        +inference(task, sub_goals, reset_mode, reset_env)
    }
```

**Class Diagram: Voyager Main Class**

Sources: [voyager/voyager.py:17-102](), [voyager/voyager.py:165-412]()

The Voyager class has several core methods that implement the learning and task execution processes:

- `learn()`: Implements the continuous learning loop where new tasks are proposed and executed
- `reset()`: Prepares the agent for a new task
- `step()`: Executes a single step in the learning process
- `rollout()`: Executes a complete task until success or maximum retries
- `decompose_task()`: Breaks down a complex task into subtasks
- `inference()`: Executes a specific task using learned skills

Sources: [voyager/voyager.py:165-412]()

## Data Flow and Control Loop

Voyager implements a continuous learning loop that involves task proposal, skill retrieval, code generation, execution, evaluation, and skill storage. This learning process is the core of Voyager's ability to autonomously explore and master the Minecraft environment.

```mermaid
sequenceDiagram
    participant V as "Voyager"
    participant CA as "CurriculumAgent"
    participant SM as "SkillManager"
    participant AA as "ActionAgent"
    participant VE as "VoyagerEnv"
    participant MC as "Minecraft"
    participant CRA as "CriticAgent"
    
    V->>CA: propose_next_task()
    CA-->>V: task, context
    V->>SM: retrieve_skills(query)
    SM-->>V: relevant_skills
    
    V->>AA: render_system_message(skills)
    V->>AA: render_human_message(events, task, context)
    
    loop Until task success or max retries
        AA->>AA: llm(messages)
        AA->>AA: process_ai_message()
        V->>VE: step(code)
        VE->>MC: Execute JavaScript code
        MC-->>VE: Return game events
        VE-->>V: events
        V->>CRA: check_task_success(events, task)
        CRA-->>V: success, critique
        
        alt success is false and retries left
            V->>AA: Update with critique
        end
    end
    
    alt Task successful
        V->>SM: add_new_skill(info)
    end
    
    V->>CA: update_exploration_progress(info)
```

**Sequence Diagram: Voyager Learning Process**

Sources: [voyager/voyager.py:295-368](), [voyager/voyager.py:203-285]()

## Initialization and Configuration

The Voyager system requires several configuration parameters during initialization. These parameters control aspects such as model selection, retry limits, and checkpoint management.

```mermaid
graph TD
    subgraph "Voyager Initialization"
        init["__init__()"] --> env_init["Initialize VoyagerEnv"]
        init --> aa_init["Initialize ActionAgent"]
        init --> ca_init["Initialize CurriculumAgent"]
        init --> cra_init["Initialize CriticAgent"]
        init --> sm_init["Initialize SkillManager"]
        init --> rec_init["Initialize EventRecorder"]
    end
    
    env_init --> env_params["mc_port, azure_login, server_port, request_timeout"]
    aa_init --> aa_params["model_name, temperature, request_timeout, task_max_retries"]
    ca_init --> ca_params["model_name, temperature, mode, warm_up"]
    cra_init --> cra_params["model_name, temperature, mode"]
    sm_init --> sm_params["model_name, temperature, retrieval_top_k"]
```

**Initialization Flow: Voyager System Setup**

Sources: [voyager/voyager.py:18-154]()

Key configuration parameters include:

- Model names and temperatures for each agent
- Task retry limits
- Environment timeouts and wait ticks
- Checkpoint directory for saving and resuming progress
- Skill library directory for loading pre-learned skills

Sources: [voyager/voyager.py:18-102]()

## Learning Process Implementation

The `learn()` method implements Voyager's continuous learning process. This involves proposing new tasks, executing them, evaluating the results, and storing successful skills for future use.

```mermaid
flowchart TD
    start["learn()"] --> reset["Reset environment"]
    reset --> loop["Learning loop"]
    
    subgraph "Learning loop"
        check_iter["Check iteration limit"] -->|If exceeded| exit["Exit loop"]
        check_iter -->|Continue| propose["Propose next task"]
        propose --> rollout["Rollout task execution"]
        
        rollout --> check_success{"Check task success"}
        check_success -->|Success| add_skill["Add new skill"]
        check_success -->|Failure| update_progress["Update progress"]
        add_skill --> update_progress
        
        update_progress --> check_iter
    end
    
    loop --> return["Return results"]
```

**Flowchart: Voyager Learning Process**

Sources: [voyager/voyager.py:295-368]()

The learning process continues until the maximum number of iterations is reached. During each iteration, the system:

1. Proposes a new task based on current progress
2. Retrieves relevant skills from the skill library
3. Generates code to execute the task
4. Executes the code in the Minecraft environment
5. Evaluates task success
6. Stores successful skills
7. Updates exploration progress

Sources: [voyager/voyager.py:295-368]()

## Task Execution Process

The `rollout()` and `step()` methods implement the task execution process. This involves resetting the agent with a specific task, executing steps until the task is completed or the maximum number of retries is reached, and returning the results.

```mermaid
flowchart TD
    start["rollout()"] --> reset["reset()"]
    reset --> step_loop["Step loop"]
    
    subgraph "Step loop"
        step["step()"] --> check_done{"done?"}
        check_done -->|Yes| exit["Exit loop"]
        check_done -->|No| step
    end
    
    step_loop --> return["Return results"]
    
    subgraph "step()"
        get_ai_message["Get AI message"] --> parse["Parse AI message"]
        parse --> execute["Execute code"]
        execute --> evaluate["Evaluate success"]
        evaluate --> update["Update messages"]
    end
```

**Flowchart: Voyager Task Execution Process**

Sources: [voyager/voyager.py:203-293]()

During each step, the ActionAgent:
1. Receives the current state and task
2. Generates JavaScript code to execute
3. Executes the code in the Minecraft environment
4. Processes the results and updates its state

Sources: [voyager/voyager.py:203-285]()

## Integration with Minecraft

Voyager integrates with Minecraft through the VoyagerEnv component, which provides an interface for executing JavaScript code in the game environment and receiving events and observations.

```mermaid
graph TD
    V["Voyager"] --> VE["VoyagerEnv"]
    VE --> MF["Mineflayer"]
    MF --> MC["Minecraft"]
    
    subgraph "Execution Flow"
        code["JavaScript Code"] --> ctrl_prims["Control Primitives"]
        ctrl_prims --> game_actions["Game Actions"]
    end
    
    subgraph "Observation Flow"
        game_events["Game Events"] --> obsrv["Observations"]
        obsrv --> agent_state["Agent State"]
    end
    
    game_actions --> MC
    MC --> game_events
```

**Integration Diagram: Voyager-Minecraft Communication**

Sources: [voyager/voyager.py:104-109](), [voyager/voyager.py:214-226]()

## Conclusion

The core architecture of Voyager comprises a central orchestrator (Voyager class) that coordinates multiple specialized agents (ActionAgent, CurriculumAgent, CriticAgent, and SkillManager) to enable autonomous learning and task execution in Minecraft. The system implements a continuous learning loop that involves task proposal, skill retrieval, code generation, execution, evaluation, and skill storage.

This modular architecture allows Voyager to:
1. Continuously explore and learn in the Minecraft environment
2. Develop and store reusable skills
3. Leverage learned skills to solve new tasks
4. Provide a framework for LLM-powered embodied agents in interactive environments

For more detailed information about individual components, refer to the [Agents](#4) page, and for information about the skill system, see the [Skill System](#5) page.

---

