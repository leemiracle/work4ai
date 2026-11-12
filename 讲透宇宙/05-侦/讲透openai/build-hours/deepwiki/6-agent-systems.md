<!-- source: DeepWiki mcp.deepwiki.com · repo openai/build-hours · page 6 Agent Systems · fetched 2026-10-26 -->

# Agent Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [12-agentic-tool-calling/0_task.py](12-agentic-tool-calling/0_task.py)
- [12-agentic-tool-calling/1_agent.py](12-agentic-tool-calling/1_agent.py)
- [12-agentic-tool-calling/2_tools.py](12-agentic-tool-calling/2_tools.py)
- [2-assistants/7_orchestration.py](2-assistants/7_orchestration.py)
- [2-assistants/demo_util.py](2-assistants/demo_util.py)
- [6-structured_outputs/structured-outputs-assistant-final/components/ui/breadcrumb.tsx](6-structured_outputs/structured-outputs-assistant-final/components/ui/breadcrumb.tsx)
- [6-structured_outputs/structured-outputs-assistant-starting-point/components/ui/breadcrumb.tsx](6-structured_outputs/structured-outputs-assistant-starting-point/components/ui/breadcrumb.tsx)

</details>



This document covers the comprehensive agent frameworks implemented across the codebase, ranging from basic tool calling patterns to complex multi-agent orchestration systems. The agent systems demonstrate various approaches to LLM integration, tool management, and conversational flows using OpenAI's APIs.

For information about evaluation and testing of agent behaviors, see [Evaluation and Testing](#5). For voice-based agent implementations, see [Realtime Applications](#8).

## Agent Architecture Overview

The codebase implements a layered agent architecture that progresses from simple chat loops to sophisticated multi-agent systems with tool calling and transfer capabilities.

```mermaid
graph TD
    subgraph "Basic Agent Layer"
        Agent["Agent Class<br/>name, model, instructions, tools"]
        RunDemo["run_demo_loop()<br/>Interactive chat interface"]
        OpenAIClient["OpenAI Client<br/>Responses API, Chat Completions"]
    end
    
    subgraph "Tool Integration Layer"
        FunctionTool["@function_tool decorator<br/>Python function to schema"]
        MockAPI["MockAPI<br/>search_policies(), get_emails(), send_email()"]
        ToolSchemas["function_to_schema()<br/>Inspect-based schema generation"]
    end
    
    subgraph "Orchestration Layer"
        RunFullTurn["run_full_turn()<br/>Complete conversation cycle"]
        ExecuteToolCall["execute_tool_call()<br/>Tool execution with result handling"]
        AgentTransfer["Agent Transfer<br/>Dynamic agent switching"]
    end
    
    subgraph "Demo Applications"
        TriageAgent["triage_agent<br/>Customer service routing"]
        SalesAgent["sales_agent<br/>Sales conversation flow"]
        RepairsAgent["issues_and_repairs_agent<br/>Support ticket handling"]
    end
    
    Agent --> RunDemo
    Agent --> OpenAIClient
    FunctionTool --> ToolSchemas
    MockAPI --> FunctionTool
    RunFullTurn --> ExecuteToolCall
    ExecuteToolCall --> AgentTransfer
    TriageAgent --> SalesAgent
    TriageAgent --> RepairsAgent
```

Sources: [12-agentic-tool-calling/1_agent.py:1-11](), [2-assistants/7_orchestration.py:8-13](), [2-assistants/demo_util.py:19-64]()

## Basic Agent Implementation

The foundation of the agent system is the `Agent` class and supporting utilities that provide a simple interface for LLM-powered conversations.

### Core Agent Structure

| Component | File | Purpose |
|-----------|------|---------|
| `Agent` | [2-assistants/7_orchestration.py:8-13]() | Base agent configuration with name, model, instructions, tools |
| `run_demo_loop` | [12-agentic-tool-calling/1_agent.py:10]() | Interactive chat interface for agent testing |
| `OpenAI` client | [12-agentic-tool-calling/0_task.py:3]() | Direct API integration for responses and chat completions |

The simplest agent implementation demonstrates the foundational pattern:

```mermaid
sequenceDiagram
    participant User
    participant RunDemoLoop["run_demo_loop()"]
    participant Agent
    participant OpenAI["OpenAI API"]
    
    User->>RunDemoLoop: "User input"
    RunDemoLoop->>Agent: Process message
    Agent->>OpenAI: Chat completion request
    OpenAI-->>Agent: Response
    Agent-->>RunDemoLoop: Formatted response
    RunDemoLoop-->>User: Display output
```

Sources: [12-agentic-tool-calling/1_agent.py:5-10](), [12-agentic-tool-calling/0_task.py:5-9]()

## Tool Calling and Integration

The agent system supports sophisticated tool calling through Python function decorators and automatic schema generation.

### Tool Definition Pattern

The `@function_tool` decorator and `function_to_schema` utility enable seamless integration of Python functions as agent tools:

```mermaid
graph LR
    subgraph "Tool Definition"
        PythonFunc["Python Function<br/>search_policies(query: str)"]
        FunctionTool["@function_tool<br/>Decorator"]
        Schema["OpenAI Tool Schema<br/>JSON format"]
    end
    
    subgraph "Tool Registry"
        MockAPI["MockAPI Instance<br/>Backend implementation"]
        ToolList["Agent.tools[]<br/>Function references"]
        ToolSchemas["tool_schemas[]<br/>Generated schemas"]
    end
    
    subgraph "Execution"
        ToolCall["OpenAI Tool Call<br/>function name + args"]
        ExecuteCall["execute_tool_call()<br/>Dynamic function dispatch"]
        Result["Tool Result<br/>Returned to conversation"]
    end
    
    PythonFunc --> FunctionTool
    FunctionTool --> Schema
    MockAPI --> ToolList
    ToolList --> ToolSchemas
    ToolCall --> ExecuteCall
    ExecuteCall --> Result
```

### Available Tools

| Tool Function | Purpose | Parameters |
|---------------|---------|------------|
| `search_policies` | Query company policy database | `query: str` |
| `get_emails` | Retrieve email messages | `to: Optional[str]` |
| `send_email` | Send email communication | `from_addr, to_addr, subject, body: str` |

Sources: [12-agentic-tool-calling/2_tools.py:9-28](), [2-assistants/demo_util.py:19-64]()

## Multi-Agent Orchestration

The orchestration system enables complex conversational flows with multiple specialized agents and dynamic transfer capabilities.

### Agent Transfer Mechanism

```mermaid
stateDiagram-v2
    [*] --> TriageAgent: "Initial contact"
    
    TriageAgent --> SalesAgent: "transfer_to_sales_agent()"
    TriageAgent --> RepairsAgent: "transfer_to_issues_and_repairs()"
    TriageAgent --> Human: "escalate_to_human(summary)"
    
    SalesAgent --> TriageAgent: "transfer_back_to_triage()"
    RepairsAgent --> TriageAgent: "transfer_back_to_triage()"
    
    SalesAgent --> OrderExecution: "execute_order(product, price)"
    RepairsAgent --> RefundExecution: "execute_refund(item_id, reason)"
    
    OrderExecution --> [*]
    RefundExecution --> [*]
    Human --> [*]
```

### Agent Specializations

| Agent | Instructions | Tools | Purpose |
|-------|-------------|-------|---------|
| `triage_agent` | Customer service routing | `transfer_to_sales_agent`, `transfer_to_issues_and_repairs`, `escalate_to_human` | Initial contact and routing |
| `sales_agent` | Sales conversation flow | `execute_order`, `transfer_back_to_triage` | Product sales and order processing |
| `issues_and_repairs_agent` | Support ticket handling | `execute_refund`, `look_up_item`, `transfer_back_to_triage` | Issue resolution and refunds |

Sources: [2-assistants/7_orchestration.py:112-188]()

## Conversation Flow Management

The `run_full_turn` function implements the core conversation cycle with tool calling and agent transfer logic.

```mermaid
flowchart TD
    Start["run_full_turn(agent, messages)"] --> InitMessages["Initialize message history"]
    InitMessages --> CreateSchemas["Generate tool_schemas from agent.tools"]
    CreateSchemas --> ChatCompletion["OpenAI chat.completions.create()"]
    
    ChatCompletion --> HasContent{"message.content exists?"}
    HasContent -->|Yes| PrintResponse["Print agent response"]
    HasContent -->|No| CheckTools
    PrintResponse --> CheckTools{"message.tool_calls exists?"}
    
    CheckTools -->|No| ReturnResponse["Return Response(agent, messages)"]
    CheckTools -->|Yes| ExecuteTools["For each tool_call: execute_tool_call()"]
    
    ExecuteTools --> CheckTransfer{"Result is Agent instance?"}
    CheckTransfer -->|Yes| UpdateAgent["current_agent = result"]
    CheckTransfer -->|No| AppendResult["Append tool result to messages"]
    UpdateAgent --> AppendResult
    
    AppendResult --> MoreTools{"More tool_calls?"}
    MoreTools -->|Yes| ExecuteTools
    MoreTools -->|No| ChatCompletion
    
    ReturnResponse --> End["Return final state"]
```

### Tool Execution Flow

The `execute_tool_call` function handles dynamic tool dispatch and special return types:

| Return Type | Handling | Effect |
|-------------|----------|--------|
| `Agent` instance | Agent transfer | Updates `current_agent` and continues conversation |
| String result | Tool output | Appended to message history as tool result |
| Complex object | Serialized | Converted to string representation |

Sources: [2-assistants/7_orchestration.py:25-81]()

## Mock API Integration

The testing infrastructure uses a `MockAPI` class to simulate external services without requiring actual API connections.

```mermaid
classDiagram
    class MockAPI {
        +search_policies(query: str)
        +get_emails(to: Optional[str])
        +send_email(from_addr: str, to_addr: str, subject: str, body: str)
    }
    
    class Agent {
        +name: str
        +model: str
        +instructions: str
        +tools: list
    }
    
    class ToolFunctions {
        +search_policies(query: str)
        +get_emails(to: Optional[str])
        +send_email(from_addr: str, to_addr: str, subject: str, body: str)
    }
    
    MockAPI --> ToolFunctions : "implements backend"
    Agent --> ToolFunctions : "uses as tools"
    ToolFunctions --> MockAPI : "delegates to instance"
```

Sources: [12-agentic-tool-calling/2_tools.py:6-22]()

## Utility Functions

The system includes several utility functions that support agent operations and development workflows.

### Schema Generation

The `function_to_schema` utility automatically converts Python functions to OpenAI-compatible tool schemas:

| Feature | Implementation |
|---------|---------------|
| Type mapping | `str → "string"`, `int → "integer"`, `float → "number"`, `bool → "boolean"` |
| Parameter detection | Uses `inspect.signature()` to extract function parameters |
| Required parameters | Identifies parameters without default values |
| Documentation | Extracts docstring as tool description |

### Demo Interface

The demo utilities provide colored terminal output and interactive loops for agent testing:

| Function | Purpose |
|----------|---------|
| `color(text, color)` | Terminal color formatting with ANSI escape codes |
| `run_demo_loop` | Interactive chat interface for agent testing |

Sources: [2-assistants/demo_util.py:4-64]()

---

