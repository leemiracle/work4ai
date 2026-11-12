<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RecAI · page 4 InteRecAgent · fetched 2026-10-26 -->

# InteRecAgent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [InteRecAgent/llm4crs/agent_plan_first_openai.py](InteRecAgent/llm4crs/agent_plan_first_openai.py)
- [InteRecAgent/llm4crs/prompt/tool.py](InteRecAgent/llm4crs/prompt/tool.py)
- [InteRecAgent/llm4crs/utils/open_ai.py](InteRecAgent/llm4crs/utils/open_ai.py)
- [InteRecAgent/requirements.txt](InteRecAgent/requirements.txt)

</details>



## Purpose and Scope

InteRecAgent is a conversational recommendation agent that uses tool-based LLM orchestration to provide interactive item recommendations. The system employs a plan-first execution framework where an LLM acts as the brain to understand user intent, plan tool usage, and orchestrate recommendation tools to generate contextual responses. This document covers the agent architecture, tool system, memory management, and integration patterns.

For information about other LLM-enhanced recommendation approaches, see [RecLM-emb](#2), [RecExplainer](#3), and [RecLM-gen and RecLM-cgen](#5).

## Architecture Overview

InteRecAgent implements a plan-first agent architecture where the LLM generates execution plans that are then executed by specialized recommendation tools.

### Core Components Architecture

```mermaid
graph TB
    subgraph "InteRecAgent System"
        subgraph "Agent Layer"
            Agent["CRSAgentPlanFirstOpenAI<br/>Main Agent Controller"]
            Memory["DialogueMemory<br/>Conversation History"]
            Profile["UserProfileMemory<br/>User Preferences"]
        end
        
        subgraph "Planning & Execution"
            Planner["LLM Planner<br/>Plan Generation"]
            ToolBox["ToolBox<br/>Tool Orchestrator"]
            Critic["Critic<br/>Response Validation"]
        end
        
        subgraph "Tool Ecosystem"
            Buffer["BufferStoreTool<br/>Candidate Storage"]
            Lookup["LookUpTool<br/>SQL Information Retrieval"]
            HardFilter["HardFilterTool<br/>Property-based Filtering"]
            SoftFilter["SoftFilterTool<br/>Similarity-based Filtering"]
            Ranking["RankingTool<br/>Preference-based Ranking"]
            Mapping["MapTool<br/>ID to Title Conversion"]
        end
        
        subgraph "External Services"
            OpenAI["OpenAICall<br/>LLM API Integration"]
            ItemDB["item_corups<br/>Item Database"]
            CandBuffer["candidate_buffer<br/>Working Memory"]
        end
    end
    
    Agent --> Memory
    Agent --> Profile
    Agent --> Planner
    Agent --> ToolBox
    Agent --> Critic
    
    Planner --> OpenAI
    ToolBox --> Buffer
    ToolBox --> Lookup
    ToolBox --> HardFilter
    ToolBox --> SoftFilter
    ToolBox --> Ranking
    ToolBox --> Mapping
    
    Buffer --> CandBuffer
    Lookup --> ItemDB
    HardFilter --> ItemDB
    SoftFilter --> ItemDB
    Ranking --> CandBuffer
    Mapping --> CandBuffer
    
    Critic --> Agent
```

**Sources:** [InteRecAgent/llm4crs/agent_plan_first_openai.py:245-585]()

### Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent as "CRSAgentPlanFirstOpenAI"
    participant Memory as "DialogueMemory"
    participant Planner as "LLM Planner"
    participant ToolBox as "ToolBox"
    participant Tools as "Recommendation Tools"
    
    User->>Agent: User Input
    Agent->>Memory: Store User Message
    Agent->>Planner: Generate Plan
    Planner->>Agent: Tool Execution Plan
    Agent->>ToolBox: Execute Plan
    ToolBox->>Tools: Run Individual Tools
    Tools->>ToolBox: Tool Results
    ToolBox->>Agent: Aggregated Results
    Agent->>Agent: Summarize Response
    Agent->>Memory: Store Agent Response
    Agent->>User: Final Response
```

**Sources:** [InteRecAgent/llm4crs/agent_plan_first_openai.py:417-490]()

## Tool System

InteRecAgent employs six specialized tools for different recommendation tasks, each with specific input formats and behaviors.

### Tool Definitions and Capabilities

| Tool Name | Code Class | Purpose | Input Format |
|-----------|------------|---------|--------------|
| `BufferStoreTool` | Item Candidates Storing Tool | Store candidate items for processing | String of item names split by ";;" |
| `LookUpTool` | Item Information Look Up Tool | Query item database with SQL | SQL SELECT command |
| `HardFilterTool` | Item Properties Filtering Tool | Filter items by hard constraints | SQL SELECT with WHERE conditions |
| `SoftFilterTool` | Item Similarity Filtering Tool | Find similar items using embeddings | Python list of seed item titles |
| `RankingTool` | Item Candidates Ranking Tool | Rank items by preference/similarity | JSON with "schema", "prefer", "unwanted" |
| `MapTool` | Mapping Tool | Convert item IDs to titles | Integer (number of items needed) |

**Sources:** [InteRecAgent/llm4crs/prompt/tool.py:7-14](), [InteRecAgent/llm4crs/prompt/tool.py:82-101]()

### Tool Description System

The system uses dynamic tool descriptions that are formatted based on the domain:

```mermaid
graph LR
    subgraph "Tool Description Generation"
        Domain["Domain Mapping<br/>{item, Item, ITEM}"]
        Templates["Tool Description Templates<br/>CANDIDATE_STORE_TOOL_DESC<br/>LOOK_UP_TOOL_DESC<br/>HARD_FILTER_TOOL_DESC<br/>etc."]
        Formatted["OVERALL_TOOL_DESC<br/>Formatted Tool Descriptions"]
    end
    
    Domain --> Templates
    Templates --> Formatted
    Formatted --> SystemPrompt["SYSTEM_PROMPT_PLAN_FIRST"]
```

**Sources:** [InteRecAgent/llm4crs/prompt/tool.py:17-101](), [InteRecAgent/llm4crs/agent_plan_first_openai.py:267-274]()

### Tool Execution Framework

The `ToolBox` class orchestrates tool execution with validation and error handling:

```mermaid
graph TB
    subgraph "ToolBox Execution Pipeline"
        Input["JSON Plan Input<br/>[{tool_name, input}, ...]"]
        Parser["JSON Parser<br/>json.loads()"]
        Validator["Tool Validation<br/>_check_plan_legacy()"]
        AutoFix["Auto-correction<br/>Add missing MapTool"]
        Executor["Tool Execution Loop"]
        Aggregator["Result Aggregation"]
        Output["Final Output"]
    end
    
    Input --> Parser
    Parser --> Validator
    Validator --> AutoFix
    AutoFix --> Executor
    Executor --> Aggregator
    Aggregator --> Output
    
    Validator -.-> |"Map tool missing"| AutoFix
    Parser -.-> |"Parse error"| Output
    Executor -.-> |"Tool error"| Output
```

**Sources:** [InteRecAgent/llm4crs/agent_plan_first_openai.py:23-153]()

## Memory Management

InteRecAgent implements sophisticated memory management for maintaining conversation context and user profiles.

### DialogueMemory Implementation

The `DialogueMemory` class handles conversation history with automatic shortening capabilities:

| Feature | Implementation | Configuration |
|---------|---------------|---------------|
| Memory Storage | List of role-content dictionaries | `self.memory = []` |
| Token Limiting | Configurable max tokens per dialogue | `max_dialogue_tokens = 512` |
| Shortening Strategy | "cut" (truncate) or "pure" (LLM summarize) | `shortening_strategy` |
| Auto-shortening | Triggered on token limit exceeded | `enable_shorten = True` |

```mermaid
graph TB
    subgraph "Memory Management Flow"
        NewMessage["New Message"]
        Append["append(role, message)"]
        TokenCheck["Check Token Count<br/>num_tokens_from_string()"]
        Decision{"Exceeds Limit?"}
        Strategy{"Shortening Strategy"}
        Cut["Cut Strategy<br/>Remove earliest messages"]
        Pure["Pure Strategy<br/>LLM Summarization"]
        Update["Update Memory State"]
    end
    
    NewMessage --> Append
    Append --> TokenCheck
    TokenCheck --> Decision
    Decision -->|Yes| Strategy
    Decision -->|No| Update
    Strategy -->|cut| Cut
    Strategy -->|pure| Pure
    Cut --> Update
    Pure --> Update
```

**Sources:** [InteRecAgent/llm4crs/agent_plan_first_openai.py:155-243]()

### User Profile Integration

The system optionally maintains user profiles through `UserProfileMemory`:

- **Profile Updates**: Triggered every N turns based on `user_profile_update` parameter
- **Profile Integration**: Automatically injected into ranking tools
- **Profile Structure**: Contains "prefer", "unwanted", and historical interaction data

**Sources:** [InteRecAgent/llm4crs/agent_plan_first_openai.py:361-363](), [InteRecAgent/llm4crs/agent_plan_first_openai.py:481-484]()

## LLM Integration and API Management

### OpenAI API Integration

The `OpenAICall` class provides robust API integration with multiple provider support:

```mermaid
graph TB
    subgraph "OpenAI Integration Architecture"
        Config["API Configuration<br/>model, api_key, api_type<br/>api_base, temperature"]
        Client["Client Initialization<br/>OpenAI() or AzureOpenAI()"]
        Methods["API Methods<br/>_chat_completion()<br/>_completion()"]
        ErrorHandling["Error Handling<br/>Retry Logic<br/>Token Usage Tracking"]
        Response["Response Processing<br/>Content Extraction<br/>Usage Statistics"]
    end
    
    Config --> Client
    Client --> Methods
    Methods --> ErrorHandling
    ErrorHandling --> Response
    
    subgraph "Supported APIs"
        OpenAIAPI["OpenAI API<br/>api_type='open_ai'"]
        AzureAPI["Azure OpenAI<br/>api_type='azure'"]
        LocalAPI["Local APIs<br/>FastChat compatible"]
    end
    
    Client --> OpenAIAPI
    Client --> AzureAPI
    Client --> LocalAPI
```

**Sources:** [InteRecAgent/llm4crs/utils/open_ai.py:32-145]()

### Token Usage Tracking

The system implements context-aware token usage tracking:

- **Context Variables**: Uses `ContextVar` for thread-safe token counting
- **Automatic Aggregation**: Accumulates tokens across multiple API calls
- **Usage Categories**: Tracks completion, prompt, and total tokens separately

**Sources:** [InteRecAgent/llm4crs/utils/open_ai.py:14-29](), [InteRecAgent/llm4crs/utils/open_ai.py:132-139]()

## Plan Generation and Execution

### System Prompt Structure

The agent uses `SYSTEM_PROMPT_PLAN_FIRST` which includes:

- Tool descriptions formatted for the specific domain
- Tool execution format specifications
- Action/Action Input parsing patterns
- Final Answer generation instructions

### Plan Parsing and Validation

```mermaid
graph TB
    subgraph "Plan Processing Pipeline"
        LLMOutput["LLM Output<br/>Raw text response"]
        RegexMatch["Regex Pattern Matching<br/>Action: ... Action Input: ..."]
        FinalCheck["Final Answer Check<br/>'Final Answer:' pattern"]
        ActionParsing["Action Input Extraction"]
        ToolExecution["Tool Execution via ToolBox"]
        ResponseGeneration["Response Summarization"]
    end
    
    LLMOutput --> RegexMatch
    RegexMatch --> |Match found| ActionParsing
    RegexMatch --> |No match| FinalCheck
    FinalCheck --> |Final Answer| ResponseGeneration
    FinalCheck --> |Neither| ResponseGeneration
    ActionParsing --> ToolExecution
    ToolExecution --> ResponseGeneration
```

**Sources:** [InteRecAgent/llm4crs/agent_plan_first_openai.py:523-537]()

## Dependencies and Requirements

The system requires the following key dependencies:

| Category | Dependencies | Purpose |
|----------|-------------|---------|
| LLM Integration | `openai>=1.5.0`, `langchain==0.0.312` | API communication and agent framework |
| Data Processing | `pandasql==0.7.3`, `sqlparse==0.4.2` | SQL query processing for tool operations |
| Vector Operations | `faiss-cpu==1.7.4`, `sentence_transformers==2.2.2` | Similarity-based filtering |
| Web Interface | `gradio==3.40.1` | Interactive demo interface |
| Utilities | `loguru==0.7.0`, `tiktoken==0.4.0` | Logging and token counting |

**Sources:** [InteRecAgent/requirements.txt:1-17]()

---

