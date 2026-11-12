<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/ClawWork · page 3 Architecture · fetched 2026-11-09 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [assets/architecture.png](assets/architecture.png)

</details>



This document presents the overall system architecture of ClawWork, showing how components interact and data flows through the system. It covers the dual-mode deployment architecture (standalone and ClawMode), component organization, data persistence layer, and communication patterns between subsystems.

For detailed information about individual components and their responsibilities, see [System Components](#3.1). For data flow sequences and communication protocols, see [Data Flow and Communication](#3.2). For external API dependencies and their costs, see [External Dependencies](#3.3).

---

## System Overview

ClawWork is organized into three primary subsystems: the **Core Economic Agent System** (standalone operation), the **ClawMode Integration Layer** (nanobot bridge), and the **Supporting Infrastructure** (evaluation, dashboard, data storage). The architecture supports two deployment modes that share most components while differing in their execution context.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "livebench/ - Core Agent System"
        LiveAgent["livebench/agent/live_agent.py<br/>LiveAgent class"]
        EconTracker["livebench/agent/economic_tracker.py<br/>EconomicTracker class"]
        TaskMgr["livebench/work/task_manager.py<br/>TaskManager class"]
        WorkEval["livebench/work/evaluator.py<br/>WorkEvaluator class"]
        DirectTools["livebench/tools/direct_tools.py<br/>decide_activity()<br/>submit_work()<br/>learn()<br/>get_status()"]
        ProdTools["livebench/tools/productivity/<br/>search_web.py<br/>create_file.py<br/>execute_code.py<br/>create_video.py"]
        Prompts["livebench/prompts/<br/>live_agent_prompt.py"]
    end
    
    subgraph "clawmode_integration/ - Nanobot Bridge"
        AgentLoop["clawmode_integration/agent_loop.py<br/>LiveBenchAgentLoop<br/>extends AgentLoop"]
        TrackedProv["clawmode_integration/provider_wrapper.py<br/>TrackedProvider<br/>wraps LLMProvider"]
        CLI["clawmode_integration/cli.py<br/>gateway command"]
        Skill["clawmode_integration/skill/SKILL.md<br/>Protocol documentation"]
    end
    
    subgraph "eval/ - Evaluation System"
        MetaGen["eval/generate_meta_prompts.py<br/>generate_meta_prompts()"]
        MetaPrompts["eval/meta_prompts/*.json<br/>44 category rubrics"]
    end
    
    subgraph "livebench/api/ - Dashboard Backend"
        APIServer["livebench/api/server.py<br/>FastAPI app<br/>WebSocket endpoints"]
    end
    
    subgraph "frontend/ - Dashboard UI"
        ReactApp["frontend/src/<br/>React components<br/>WebSocket client"]
    end
    
    subgraph "Data Layer"
        GDPVal[("livebench/data/tasks/gdpval/<br/>train-00000-of-00001.parquet<br/>task_data.json")]
        TokenCosts[("livebench/data/agent_data/{signature}/<br/>token_costs.jsonl")]
        Memory[("livebench/data/agent_data/{signature}/<br/>memory/memory.jsonl")]
        TaskValues[("scripts/task_value_estimates/<br/>task_values.jsonl")]
        Config[("livebench/configs/*.json")]
    end
    
    LiveAgent --> EconTracker
    LiveAgent --> TaskMgr
    LiveAgent --> DirectTools
    LiveAgent --> ProdTools
    LiveAgent --> Prompts
    
    TaskMgr --> WorkEval
    WorkEval --> EconTracker
    
    AgentLoop -.->|extends/wraps| LiveAgent
    AgentLoop --> TrackedProv
    AgentLoop --> EconTracker
    CLI --> AgentLoop
    
    WorkEval --> MetaPrompts
    MetaGen --> MetaPrompts
    
    EconTracker --> TokenCosts
    DirectTools --> Memory
    
    TaskMgr --> GDPVal
    TaskMgr --> TaskValues
    LiveAgent --> Config
    
    APIServer --> EconTracker
    APIServer --> TokenCosts
    ReactApp --> APIServer
```

**Sources:** [livebench/agent/live_agent.py](), [livebench/agent/economic_tracker.py](), [livebench/work/task_manager.py](), [livebench/work/evaluator.py](), [livebench/tools/direct_tools.py](), [clawmode_integration/agent_loop.py](), [clawmode_integration/provider_wrapper.py](), [livebench/api/server.py](), [README.md:584-620]()

---

## Directory Structure and Component Mapping

The repository is organized into clearly separated subsystems, each responsible for distinct functional areas:

| Directory | Purpose | Key Components |
|-----------|---------|----------------|
| `livebench/agent/` | Core agent orchestration and economic tracking | `LiveAgent`, `EconomicTracker` |
| `livebench/work/` | Task management and evaluation | `TaskManager`, `WorkEvaluator` |
| `livebench/tools/` | Agent capabilities | `direct_tools.py`, `productivity/` subdirectory |
| `livebench/api/` | FastAPI backend for dashboard | `server.py` with WebSocket endpoints |
| `livebench/prompts/` | System prompts | `live_agent_prompt.py` |
| `livebench/configs/` | Agent configuration files | JSON config files per agent |
| `livebench/data/` | Runtime data storage | `tasks/`, `agent_data/` subdirectories |
| `clawmode_integration/` | Nanobot integration layer | `agent_loop.py`, `provider_wrapper.py`, `cli.py` |
| `eval/` | Evaluation infrastructure | `generate_meta_prompts.py`, `meta_prompts/*.json` |
| `frontend/` | React dashboard | `src/` components, Vite build system |
| `scripts/` | Data preprocessing utilities | Task value estimation scripts |

**Sources:** [README.md:584-620](), [.gitignore:1-82]()

---

## Dual-Mode Architecture

ClawWork supports two distinct deployment architectures that share core components while differing in their execution context and user interaction patterns.

### Mode Comparison Diagram

```mermaid
graph LR
    subgraph "Standalone Mode"
        Cron["Cron scheduler<br/>or manual trigger"]
        SA_Agent["LiveAgent instance"]
        SA_Config["livebench/configs/<br/>test_agent.json"]
        SA_Tracker["EconomicTracker<br/>direct instance"]
        SA_Dashboard["Dashboard<br/>localhost:3000"]
        
        Cron --> SA_Agent
        SA_Config --> SA_Agent
        SA_Agent --> SA_Tracker
        SA_Tracker --> SA_Dashboard
    end
    
    subgraph "ClawMode Architecture"
        User["User message<br/>Telegram/Discord/CLI"]
        Gateway["nanobot gateway<br/>multi-channel router"]
        CM_Loop["LiveBenchAgentLoop<br/>extends nanobot.AgentLoop"]
        CM_Tracked["TrackedProvider<br/>wraps LLMProvider"]
        CM_Tracker["EconomicTracker<br/>shared instance"]
        CM_Response["Response + cost footer"]
        
        User --> Gateway
        Gateway --> CM_Loop
        CM_Loop --> CM_Tracked
        CM_Tracked --> CM_Tracker
        CM_Loop --> CM_Response
        CM_Response --> User
    end
    
    subgraph "Shared Components"
        Tools["livebench/tools/<br/>8 agent tools"]
        TaskMgr["TaskManager<br/>GDPVal tasks"]
        Evaluator["WorkEvaluator<br/>LLM scoring"]
        DataFiles["token_costs.jsonl<br/>memory.jsonl"]
    end
    
    SA_Agent --> Tools
    SA_Agent --> TaskMgr
    SA_Agent --> Evaluator
    SA_Tracker --> DataFiles
    
    CM_Loop --> Tools
    CM_Loop --> TaskMgr
    CM_Loop --> Evaluator
    CM_Tracker --> DataFiles
```

**Sources:** [README.md:134-178](), [README.md:367-556](), [clawmode_integration/agent_loop.py](), [livebench/agent/live_agent.py]()

### Architectural Differences

| Aspect | Standalone Mode | ClawMode |
|--------|----------------|----------|
| **Entry Point** | `livebench/agent/live_agent.py` | `clawmode_integration/cli.py gateway` |
| **Execution Trigger** | Daily cron loop or manual script | User message via nanobot channels |
| **Agent Loop** | `LiveAgent` class instance | `LiveBenchAgentLoop` extends `nanobot.AgentLoop` |
| **LLM Provider** | Direct LLM calls via LangChain/LiteLLM | `TrackedProvider` wrapper intercepts calls |
| **Cost Tracking** | Per-task aggregation in `EconomicTracker` | Per-message tracking with real-time footer |
| **Configuration** | `livebench/configs/*.json` | Nanobot config + ClawWork config |
| **Output** | Console logs + dashboard updates | Chat response + `Cost: $X \| Balance: $Y` footer |
| **Tools Available** | 8 ClawWork tools | 8 ClawWork tools + all nanobot tools |

**Sources:** [README.md:134-178](), [README.md:367-556]()

---

## Component Interaction Patterns

### Standalone Mode Execution Flow

```mermaid
sequenceDiagram
    participant Script as "run_test_agent.sh"
    participant LA as "LiveAgent"
    participant ET as "EconomicTracker"
    participant TM as "TaskManager"
    participant Tools as "Agent Tools"
    participant WE as "WorkEvaluator"
    participant Files as "JSONL Files"
    participant WS as "WebSocket Server"
    
    Script->>LA: Initialize with config
    LA->>ET: Initialize tracker
    LA->>TM: Load GDPVal tasks
    
    loop Daily Loop
        LA->>ET: start_task(task_id)
        LA->>TM: get_next_task()
        TM-->>LA: Task prompt + reference files
        
        LA->>Tools: decide_activity("work")
        Tools-->>LA: Decision confirmed
        
        loop Work Execution
            LA->>Tools: Use tools (search, create_file, etc.)
            Tools-->>LA: Tool results
            LA->>ET: track_tokens(input, output, cost)
        end
        
        LA->>Tools: submit_work(artifacts)
        Tools->>WE: Evaluate work quality
        WE-->>Tools: Quality score 0-1
        Tools->>ET: add_work_income(payment)
        ET-->>Tools: Balance updated
        
        LA->>ET: end_task()
        ET->>Files: Write task record to token_costs.jsonl
        ET->>WS: Broadcast balance update
    end
```

**Sources:** [livebench/agent/live_agent.py](), [livebench/agent/economic_tracker.py](), [livebench/tools/direct_tools.py](), [livebench/api/server.py]()

### ClawMode Message Handling Flow

```mermaid
sequenceDiagram
    participant User as "User (Telegram)"
    participant NG as "nanobot.gateway"
    participant LBL as "LiveBenchAgentLoop"
    participant TP as "TrackedProvider"
    participant ET as "EconomicTracker"
    participant Tools as "Agent Tools"
    participant Files as "JSONL Files"
    
    User->>NG: Send message
    NG->>LBL: on_message(msg)
    LBL->>ET: start_task(msg.id)
    
    loop Generate Response
        LBL->>TP: chat(messages)
        TP->>TP: Extract provider from self.providers
        TP->>API: Forward to actual LLM
        API-->>TP: Response + usage metadata
        TP->>ET: track_tokens(prompt_tokens, completion_tokens, cost)
        TP-->>LBL: Return response
        
        opt Tool Call
            LBL->>Tools: Execute tool
            Tools-->>LBL: Tool result
        end
    end
    
    LBL->>ET: end_task()
    ET->>Files: Append to token_costs.jsonl
    ET-->>LBL: Final balance and cost
    
    LBL->>LBL: Append cost footer
    LBL->>NG: Return response + footer
    NG->>User: Display message
```

**Sources:** [clawmode_integration/agent_loop.py](), [clawmode_integration/provider_wrapper.py](), [livebench/agent/economic_tracker.py]()

---

## Data Persistence Architecture

ClawWork uses file-based persistence with JSONL (JSON Lines) format for economic records and agent memory, and JSON for configuration and evaluation rubrics.

### Data Storage Layout

```mermaid
graph TB
    subgraph "Configuration (JSON)"
        AgentConfig["livebench/configs/{agent}.json<br/>initial_balance, date_range,<br/>token_pricing, enabled"]
        TaskValues["scripts/task_value_estimates/<br/>task_values.jsonl<br/>task_id → estimated_value"]
        MetaPrompts["eval/meta_prompts/<br/>{category}.json<br/>Evaluation rubrics"]
    end
    
    subgraph "Static Data (Parquet)"
        GDPValData["livebench/data/tasks/gdpval/<br/>train-00000-of-00001.parquet<br/>220 tasks, 44 categories"]
        TaskJSON["livebench/data/tasks/gdpval/<br/>task_data.json<br/>Processed task metadata"]
    end
    
    subgraph "Runtime Data (JSONL)"
        TokenCosts["livebench/data/agent_data/{signature}/<br/>token_costs.jsonl<br/>Per-task economic records"]
        Memory["livebench/data/agent_data/{signature}/<br/>memory/memory.jsonl<br/>Learned knowledge entries"]
    end
    
    subgraph "Dashboard Static Data"
        StaticData["frontend/public/data/<br/>agents.json<br/>tasks.json<br/>Generated by scripts/generate_static_data.py"]
    end
    
    TaskManager --> GDPValData
    TaskManager --> TaskJSON
    TaskManager --> TaskValues
    
    EconomicTracker --> TokenCosts
    LearnTool --> Memory
    
    WorkEvaluator --> MetaPrompts
    
    GenerateScript["scripts/generate_static_data.py"] --> TokenCosts
    GenerateScript --> StaticData
    
    LiveAgent --> AgentConfig
```

**Sources:** [livebench/work/task_manager.py](), [livebench/agent/economic_tracker.py](), [livebench/tools/direct_tools.py](), [.gitignore:59-78]()

### Key Data Files

| File Path | Format | Purpose | Written By | Read By |
|-----------|--------|---------|------------|---------|
| `livebench/configs/*.json` | JSON | Agent configuration | Manual | `LiveAgent`, `LiveBenchAgentLoop` |
| `livebench/data/tasks/gdpval/train-*.parquet` | Parquet | GDPVal dataset | External | `TaskManager` |
| `livebench/data/agent_data/{signature}/token_costs.jsonl` | JSONL | Economic history | `EconomicTracker` | Dashboard, analysis |
| `livebench/data/agent_data/{signature}/memory/memory.jsonl` | JSONL | Agent knowledge | `learn()` tool | `get_status()` tool |
| `eval/meta_prompts/{category}.json` | JSON | Evaluation rubrics | `generate_meta_prompts.py` | `WorkEvaluator` |
| `scripts/task_value_estimates/task_values.jsonl` | JSONL | Task payment values | `calculate_task_values.py` | `TaskManager` |
| `frontend/public/data/*.json` | JSON | Static dashboard data | `generate_static_data.py` | React frontend |

**Sources:** [livebench/agent/economic_tracker.py](), [livebench/work/task_manager.py](), [livebench/work/evaluator.py](), [.gitignore:59-78]()

### token_costs.jsonl Record Structure

Each line in `token_costs.jsonl` represents a complete task session:

```json
{
  "task_id": "abc-123-def",
  "date": "2025-01-20",
  "category": "Financial Managers",
  "llm_usage": {
    "total_input_tokens": 4500,
    "total_output_tokens": 900,
    "total_cost": 0.02025
  },
  "api_usage": {
    "search_api_cost": 0.0016
  },
  "cost_summary": {
    "total_cost": 0.02185
  },
  "work_income": 198.44,
  "balance_after": 1198.41,
  "status": "thriving"
}
```

**Sources:** [livebench/agent/economic_tracker.py:1-100](), [README.md:327-347]()

---

## External API Integration

ClawWork integrates with multiple external APIs for LLM capabilities, productivity tools, and evaluation. All API costs are tracked by `EconomicTracker` and deducted from agent balance.

### API Dependency Diagram

```mermaid
graph TB
    subgraph "ClawWork Core"
        Agent["LiveAgent /<br/>LiveBenchAgentLoop"]
        Tracker["EconomicTracker"]
        Tools["Productivity Tools"]
        Evaluator["WorkEvaluator"]
    end
    
    subgraph "LLM Providers (via .env)"
        OpenAI["OpenAI API<br/>OPENAI_API_KEY<br/>OPENAI_API_BASE"]
        SiliconFlow["SiliconFlow<br/>GLM-4, Qwen, etc."]
        Alternative["Claude / Other<br/>via LiteLLM"]
    end
    
    subgraph "Search APIs"
        Tavily["Tavily Search<br/>WEB_SEARCH_API_KEY<br/>$0.0008/search"]
        Jina["Jina AI Search<br/>$0.05/1M tokens"]
    end
    
    subgraph "Specialized Services"
        E2B["E2B Code Sandbox<br/>E2B_API_KEY<br/>Python execution"]
        OCR["Qwen VL OCR<br/>OCR_VLLM_API_KEY<br/>DashScope/Alibaba"]
    end
    
    subgraph "Evaluation"
        GPT4o["GPT-4o/GPT-5.2<br/>EVALUATION_API_KEY<br/>EVALUATION_API_BASE"]
    end
    
    Agent --> OpenAI
    Agent --> SiliconFlow
    Agent --> Alternative
    
    Tools --> Tavily
    Tools --> Jina
    Tools --> E2B
    Tools --> OCR
    
    Evaluator --> GPT4o
    
    OpenAI --> Tracker
    SiliconFlow --> Tracker
    Alternative --> Tracker
    Tavily --> Tracker
    Jina --> Tracker
    E2B --> Tracker
    OCR --> Tracker
    GPT4o -.->|Not tracked| Tracker
```

**Sources:** [README.md:214-229](), [livebench/tools/productivity/search_web.py](), [livebench/tools/productivity/execute_code.py](), [livebench/work/evaluator.py]()

### Environment Variable Configuration

| Variable | Used By | Purpose | Cost Model |
|----------|---------|---------|------------|
| `OPENAI_API_KEY` | Agent LLM calls | Primary agent model | `$2.5/1M input + $10/1M output` |
| `OPENAI_API_BASE` | Agent LLM calls | Custom endpoint (e.g., SiliconFlow) | Provider-specific |
| `EVALUATION_API_KEY` | `WorkEvaluator` | GPT-4o evaluation calls | Not tracked (evaluation overhead) |
| `E2B_API_KEY` | `execute_code` tool | Python sandbox execution | Free tier available |
| `WEB_SEARCH_API_KEY` | `search_web` tool | Tavily or Jina search | `$0.0008/search` (Tavily) |
| `OCR_VLLM_API_KEY` | OCR processing | Image text extraction | DashScope pricing |

**Sources:** [README.md:214-229](), [.env.example (referenced in README)]()

---

## Dashboard and Real-Time Communication

The dashboard provides real-time visualization of agent economic activity through a FastAPI backend with WebSocket support and a React frontend.

### Dashboard Architecture

```mermaid
graph LR
    subgraph "Backend - livebench/api/server.py"
        FastAPI["FastAPI app<br/>Port 8000"]
        WSManager["WebSocketManager<br/>broadcast() method"]
        Endpoints["HTTP Endpoints<br/>/api/agents<br/>/api/tasks"]
    end
    
    subgraph "Frontend - frontend/src/"
        React["React App<br/>Port 3000"]
        WSClient["WebSocket Client<br/>useWebSocket hook"]
        Components["Dashboard Components<br/>BalanceChart<br/>TaskList<br/>LeaderBoard"]
    end
    
    subgraph "Data Sources"
        TokenFiles["token_costs.jsonl"]
        StaticData["frontend/public/data/<br/>agents.json, tasks.json"]
    end
    
    EconomicTracker["EconomicTracker"] --> WSManager
    WSManager --> FastAPI
    
    TokenFiles --> Endpoints
    StaticData --> React
    
    FastAPI -->|WebSocket| WSClient
    Endpoints -->|HTTP| React
    WSClient --> Components
```

**Sources:** [livebench/api/server.py](), [README.md:558-581](), [frontend/ directory referenced]()

### WebSocket Message Protocol

The `EconomicTracker` broadcasts updates after each task completion:

```python
# Sent by EconomicTracker to WebSocket server
{
    "type": "balance_update",
    "agent_signature": "gpt-4o-agent",
    "balance": 1198.41,
    "status": "thriving",
    "total_cost": 0.02185,
    "total_income": 198.44,
    "timestamp": "2025-01-20T14:23:45Z"
}
```

**Sources:** [livebench/api/server.py](), [livebench/agent/economic_tracker.py]()

---

This architecture enables ClawWork to operate as either a standalone benchmark system or an integrated economic layer for nanobot instances, while maintaining consistent economic tracking, evaluation, and visualization across both deployment modes.

---

