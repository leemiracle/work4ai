<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/codenav · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of CodeNav, an LLM-powered code navigation system that enables users to interact with and leverage unfamiliar codebases through natural language queries. This page covers the system's architecture, core components, and high-level workflow.

For specific usage instructions, see [Getting Started](#2). For detailed component documentation, see [Core Architecture](#3). For evaluation and experimentation capabilities, see [Evaluation Framework](#4).

## What is CodeNav?

CodeNav is an LLM agent system that automatically navigates and leverages previously unseen code repositories to solve user queries. Unlike traditional tool-use LLM agents that require manual registration of tools, CodeNav automatically indexes code repositories, searches for relevant code snippets, imports them, and uses them to iteratively generate solutions with execution feedback.

The system operates through three main interaction patterns:
- **Code execution**: Running Python code in a controlled environment
- **Code retrieval**: Searching indexed codebases for relevant snippets
- **Task completion**: Signaling when a query has been resolved

**Sources:** [README.md:14-14]()

## System Architecture Overview

CodeNav follows a layered architecture with clear separation between user interfaces, orchestration logic, agent implementations, and execution environments.

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI["codenav_run.py<br/>CLI Interface"]
        API["codenav module<br/>Python API"]
    end
    
    subgraph "Evaluation & Orchestration"
        EvalSpec["default_eval_spec.py<br/>DefaultEvalSpec"]
        ParallelEval["parallel_evaluation.py<br/>ParallelEvaluator"]
    end
    
    subgraph "Episode Management"
        Episode["episode.py<br/>Episode"]
        QueryPrompt["query_prompt.py<br/>QueryPrompt"]
    end
    
    subgraph "Agent Layer"
        OpenAIAgent["gpt4/agent.py<br/>OpenAICodeNavAgent"]
        CohereAgent["cohere/agent.py<br/>CohereCodeNavAgent"] 
        LLMChatAgent["llm_chat_agent.py<br/>LLMChatAgent"]
    end
    
    subgraph "Environment Layer"
        CodeEnv["code_env.py<br/>PythonCodeEnv"]
        RetrievalEnv["retrieval_env.py<br/>RetrievalEnv"]
        DoneEnv["done_env.py<br/>DoneEnv"]
    end
    
    subgraph "External Systems"
        Elasticsearch["Elasticsearch<br/>Code Index Server"]
        LLMAPIs["OpenAI/Cohere<br/>LLM API Services"]
    end
    
    CLI --> EvalSpec
    API --> EvalSpec
    EvalSpec --> Episode
    ParallelEval --> EvalSpec
    
    Episode --> QueryPrompt
    Episode --> OpenAIAgent
    Episode --> CohereAgent
    OpenAIAgent --> LLMChatAgent
    CohereAgent --> LLMChatAgent
    
    Episode --> CodeEnv
    Episode --> RetrievalEnv  
    Episode --> DoneEnv
    
    RetrievalEnv --> Elasticsearch
    LLMChatAgent --> LLMAPIs
```

**Sources:** [README.md:24-36](), diagrams from system analysis

## Core Workflow

The following sequence illustrates how a user query flows through the system from CLI invocation to final output generation:

```mermaid
sequenceDiagram
    participant User
    participant CLI as "codenav_run.py"
    participant DefaultEvalSpec as "DefaultEvalSpec"
    participant Episode as "Episode"
    participant Agent as "LLMChatAgent"
    participant CodeEnv as "PythonCodeEnv"
    participant RetrievalEnv as "RetrievalEnv"
    participant ES as "Elasticsearch"
    
    User->>CLI: "codenav query --code_dir --query"
    CLI->>ES: "Initialize/check index"
    CLI->>DefaultEvalSpec: "run_codenav_on_query()"
    
    DefaultEvalSpec->>Episode: "build_episode()"
    Episode->>Agent: "Initialize with QueryPrompt"
    
    loop "Interaction Loop"
        Episode->>Agent: "get_action()"
        Agent->>Agent: "Query LLM API"
        Agent-->>Episode: "CodeNavAction"
        
        alt "Code Action"
            Episode->>CodeEnv: "step(action)"
            CodeEnv->>CodeEnv: "Execute Python code"
            CodeEnv-->>Episode: "Execution result"
        else "Search Action"
            Episode->>RetrievalEnv: "step(action)"
            RetrievalEnv->>ES: "Search code index"
            ES-->>RetrievalEnv: "Code snippets"
            RetrievalEnv-->>Episode: "Search results"
        else "Done Action"
            Episode->>DoneEnv: "step(action)"
            DoneEnv-->>Episode: "Task completion"
        end
        
        Episode->>Agent: "Update conversation state"
    end
    
    Episode->>Episode: "Convert to notebook format"
    DefaultEvalSpec-->>CLI: "Results and logs"
    CLI-->>User: "Output .ipynb file"
```

**Sources:** [README.md:31-36](), system architecture diagrams

## Key Components and Code Entities

The following diagram maps the main conceptual components to their concrete implementations in the codebase:

```mermaid
graph LR
    subgraph "Agent Implementations"
        OpenAIAgent["OpenAICodeNavAgent<br/>gpt4/agent.py"]
        CohereAgent["CohereCodeNavAgent<br/>cohere/agent.py"]
        BaseChatAgent["LLMChatAgent<br/>llm_chat_agent.py"]
    end
    
    subgraph "Environment Implementations"
        PythonCodeEnv["PythonCodeEnv<br/>code_env.py"]
        RetrievalEnv["RetrievalEnv<br/>retrieval_env.py"] 
        DoneEnv["DoneEnv<br/>done_env.py"]
        BaseEnv["CodeNavEnv<br/>Abstract base"]
    end
    
    subgraph "Action System"
        CodeNavAction["CodeNavAction<br/>Data structure"]
        ActionTypes["code/search/done<br/>Action types"]
    end
    
    subgraph "Index Management"
        BuildIndex["build_index()<br/>Index creation"]
        EsCodeRetriever["EsCodeRetriever<br/>Search interface"]
    end
    
    subgraph "Prompt System"
        QueryPrompt["QueryPrompt<br/>query_prompt.py"]
        PromptTemplates["System prompts<br/>Context formatting"]
    end
    
    OpenAIAgent --> BaseChatAgent
    CohereAgent --> BaseChatAgent
    
    PythonCodeEnv --> BaseEnv
    RetrievalEnv --> BaseEnv
    DoneEnv --> BaseEnv
    
    BaseChatAgent --> CodeNavAction
    CodeNavAction --> ActionTypes
    
    RetrievalEnv --> EsCodeRetriever
    BuildIndex --> EsCodeRetriever
    
    BaseChatAgent --> QueryPrompt
    QueryPrompt --> PromptTemplates
```

**Sources:** File structure analysis, component relationships from diagrams

## Data Flow Architecture

CodeNav processes user queries through a structured data flow that transforms natural language into executable actions:

| **Stage** | **Input** | **Component** | **Output** |
|-----------|-----------|---------------|------------|
| **Query Processing** | Natural language query | `QueryPrompt` | Formatted system prompt |
| **Action Generation** | System prompt + conversation | `LLMChatAgent` | `CodeNavAction` object |
| **Environment Routing** | `CodeNavAction` | `Episode` | Environment-specific execution |
| **Code Execution** | Python code string | `PythonCodeEnv` | Execution results/errors |
| **Code Retrieval** | Search query | `RetrievalEnv` → `EsCodeRetriever` | Relevant code snippets |
| **Task Completion** | Done signal | `DoneEnv` | Episode termination |
| **Output Generation** | Interaction history | `Episode` | Jupyter notebook |

The system maintains state through the `Episode` class, which orchestrates the conversation between agents and environments while logging all interactions for later analysis and reproduction.

```mermaid
graph TB
    subgraph "Input Processing"
        UserQuery["User Query<br/>Natural Language"]
        CodeDir["Target Codebase<br/>File System"]
    end
    
    subgraph "Index Creation"
        BuildIndex["build_index()<br/>Code Analysis"]
        ESIndex["Elasticsearch Index<br/>Searchable Code Blocks"]
    end
    
    subgraph "Agent Processing"  
        QueryPrompt["QueryPrompt<br/>Context Assembly"]
        LLMCall["LLM API Call<br/>Action Generation"]
        CodeNavAction["CodeNavAction<br/>Structured Output"]
    end
    
    subgraph "Environment Execution"
        EnvRouter["Episode<br/>Action Router"]
        PythonExec["PythonCodeEnv<br/>Code Execution"]
        CodeSearch["RetrievalEnv<br/>Code Search"]
        TaskDone["DoneEnv<br/>Completion"]
    end
    
    subgraph "Output Generation"
        StateUpdate["Conversation State<br/>History Tracking"]
        NotebookGen["Jupyter Notebook<br/>Reproducible Output"]
    end
    
    UserQuery --> QueryPrompt
    CodeDir --> BuildIndex
    BuildIndex --> ESIndex
    
    QueryPrompt --> LLMCall
    LLMCall --> CodeNavAction
    CodeNavAction --> EnvRouter
    
    EnvRouter --> PythonExec
    EnvRouter --> CodeSearch
    EnvRouter --> TaskDone
    
    CodeSearch --> ESIndex
    
    PythonExec --> StateUpdate
    CodeSearch --> StateUpdate  
    TaskDone --> StateUpdate
    
    StateUpdate --> NotebookGen
```

**Sources:** [README.md:44-87](), workflow analysis from system diagrams

---

