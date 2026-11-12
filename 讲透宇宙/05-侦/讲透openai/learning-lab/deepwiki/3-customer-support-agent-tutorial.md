<!-- source: DeepWiki mcp.deepwiki.com · repo openai/learning-lab · page 3 Customer Support Agent Tutorial · fetched 2026-10-26 -->

# Customer Support Agent Tutorial

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [01-agents/1_routines.py](01-agents/1_routines.py)
- [01-agents/7_orchestration.py](01-agents/7_orchestration.py)

</details>



## Purpose and Scope

This tutorial series demonstrates how to build sophisticated customer support agents using OpenAI's API, progressing from basic conversational agents to fully orchestrated systems with tool-calling capabilities. The tutorials use ACME Inc. as a fictional company scenario, teaching developers how to implement structured customer service workflows that can handle issue resolution, refund processing, and human escalation.

The tutorial covers the complete evolution from simple chat interactions to complex agent orchestration systems. For initial setup and basic chatbot implementation, see [Getting Started](#2). For technical details about utility functions and schemas, see [Utility Functions and Schema Generation](#4.1).

## Tutorial Progression Overview

The customer support agent tutorial follows a progressive learning path, with each stage building upon the previous one's capabilities.

**Tutorial Progression Architecture**
```mermaid
graph TD
    A["1_routines.py"] --> B["Basic Procedures"]
    C["2_tools.py"] --> D["Tool Integration"] 
    E["3_tools.py"] --> F["Enhanced Tools"]
    G["4_tools.py"] --> H["Tool Orchestration"]
    I["5_escalation.py"] --> J["Human Escalation"]
    K["6_agents.py"] --> L["Agent Framework"]
    M["7_orchestration.py"] --> N["Full Orchestration"]
    
    B --> D
    D --> F  
    F --> H
    H --> J
    J --> L
    L --> N
    
    O["demo_util.py"] --> D
    O --> F
    O --> H
    O --> J
    O --> L
    O --> N
    
    subgraph "Basic Level"
        A
        B
    end
    
    subgraph "Intermediate Level" 
        C
        D
        E
        F
        G  
        H
    end
    
    subgraph "Advanced Level"
        I
        J
        K
        L
        M
        N
    end
```

Sources: [01-agents/1_routines.py:1-47](), [01-agents/7_orchestration.py:1-171]()

## ACME Inc Customer Support Scenario

All tutorials use ACME Inc. as the customer service context, implementing a standardized 4-step support procedure that guides agents through issue resolution.

**ACME Support Workflow**
```mermaid
flowchart TD
    A["User Issue"] --> B["Step 1: Understanding"]
    B --> C{"User provided reason?"}
    C -->|No| D["Ask clarifying questions"]
    C -->|Yes| E["Step 2: Propose solution"]
    D --> E
    E --> F["User tries solution"]
    F --> G{"Solution works?"}
    G -->|Yes| H["Issue resolved"]
    G -->|No| I["Step 3: Offer refund"]
    I --> J{"User accepts refund?"}
    J -->|Yes| K["Step 4: Execute refund"]
    J -->|No| L["escalate_to_human"]
    K --> M["look_up_item"]
    M --> N["execute_refund"]
    N --> H
    L --> O["Human handoff"]
```

The system message in `1_routines.py` defines this workflow: "1. 最初に質問をして、ユーザーの問題を深く理解してください" (First, ask questions to deeply understand the user's problem), followed by solution proposals, refund offers, and ID lookup for refund execution.

Sources: [01-agents/1_routines.py:13-23](), [01-agents/7_orchestration.py:146-155]()

## Agent Capabilities Evolution

The tutorial demonstrates how agent capabilities evolve from basic conversation to sophisticated tool orchestration.

**Agent Architecture Evolution**
```mermaid
graph LR
    subgraph "Basic Agent (1_routines.py)"
        A1["client.chat.completions.create"]
        A2["system_message"]
        A3["messages list"]
        A1 --> A4["Text responses only"]
    end
    
    subgraph "Tool-Enabled Agent (2-5_*.py)"
        B1["OpenAI API with tools"]
        B2["Tool schemas"]
        B3["Tool execution"]
        B1 --> B4["look_up_item"]
        B1 --> B5["execute_refund"] 
        B1 --> B6["escalate_to_human"]
    end
    
    subgraph "Orchestrated Agent (6-7_*.py)"
        C1["Agent class"]
        C2["run_full_turn"]
        C3["execute_tool_call"]
        C4["function_to_schema"]
        C1 --> C5["Multi-turn orchestration"]
        C2 --> C5
        C3 --> C5
        C4 --> C5
    end
    
    A4 --> B1
    B6 --> C1
```

The progression moves from simple `chat.completions.create` calls in `1_routines.py` to the sophisticated `Agent` class with `run_full_turn` orchestration in `7_orchestration.py`.

Sources: [01-agents/1_routines.py:35-38](), [01-agents/7_orchestration.py:8-17](), [01-agents/7_orchestration.py:28-77]()

## Technical Architecture Overview

The customer support system architecture demonstrates the integration between OpenAI's API, tool execution, and conversation management.

**System Component Architecture**
```mermaid
graph TB
    subgraph "OpenAI Integration"
        A["client.chat.completions.create"]
        B["gpt-4o-mini model"]
        C["tool_calls response"]
    end
    
    subgraph "Agent Framework"
        D["Agent class"]
        E["run_full_turn"]
        F["execute_tool_call"]
    end
    
    subgraph "Tool Functions"
        G["look_up_item"]
        H["execute_refund"] 
        I["escalate_to_human"]
    end
    
    subgraph "Schema Management"
        J["function_to_schema"]
        K["tools_map"]
        L["tool_schemas"]
    end
    
    subgraph "Message Management"
        M["messages list"]
        N["system instructions"]
        O["tool results"]
    end
    
    A --> C
    B --> A
    C --> F
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    J --> L
    K --> F
    L --> A
    M --> A
    N --> A
    O --> M
```

The `Agent` class encapsulates the core orchestration logic, while `run_full_turn` manages the complete interaction cycle from user input through tool execution to response generation.

Sources: [01-agents/7_orchestration.py:8-17](), [01-agents/7_orchestration.py:28-77](), [01-agents/7_orchestration.py:80-95]()

## Key Technical Components

| Component | File Location | Purpose |
|-----------|---------------|---------|
| `Agent` class | `7_orchestration.py:8-17` | Defines agent configuration with name, model, instructions, and tools |
| `run_full_turn` | `7_orchestration.py:28-77` | Orchestrates complete conversation turns with tool calling |
| `execute_tool_call` | `7_orchestration.py:80-95` | Executes individual tool functions and handles results |
| `look_up_item` | `7_orchestration.py:99-110` | Searches for product IDs using search queries |
| `execute_refund` | `7_orchestration.py:112-126` | Processes refund requests with item ID and reason |
| `escalate_to_human` | `7_orchestration.py:128-140` | Handles escalation to human representatives |
| System message | `1_routines.py:13-23` | Defines ACME Inc. support procedures and constraints |

## Learning Path Recommendations

1. **Start with Basic Procedures** ([Basic Customer Support Procedures](#3.1)): Understand the fundamental ACME Inc. workflow using `1_routines.py`
2. **Add Tool Integration** ([Tool Integration and Function Calling](#3.2)): Learn how tools like `look_up_item` and `execute_refund` extend agent capabilities  
3. **Implement Advanced Features** ([Advanced Agent Features](#3.3)): Master the `Agent` class and `run_full_turn` orchestration patterns

Each tutorial builds upon the previous one's concepts, with the Japanese system messages providing consistent context for the ACME Inc. customer service scenario throughout the progression.

Sources: [01-agents/1_routines.py:1-47](), [01-agents/7_orchestration.py:1-171]()

---

