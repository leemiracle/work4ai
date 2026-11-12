<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ACV · extra page Prompt Templates · fetched 2026-10-26 -->

# Prompt Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml](self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml)

</details>



This document covers the prompt template system used by the self-managing systems to generate structured experiences from chat logs and other LLM interactions. The prompt templates define how raw conversational data is transformed into structured JSON experiences that can be stored and retrieved by the experience management system.

For information about how these structured experiences are stored and managed, see [Experience Banks](#2.3.4). For details on how experiences are filtered and retrieved during agent operations, see [Experience Management](#2.3.2).

## Purpose and Architecture

The prompt template system serves as the bridge between unstructured natural language interactions and the structured experience data required by the agent system. When agents interact with LLMs to manage Kubernetes environments, the conversational logs need to be converted into standardized JSON format for storage in experience banks.

### Template System Overview

```mermaid
graph TB
    ChatLogs["Chat Logs<br/>(Natural Language)"] --> PromptTemplate["generate_mem.yaml<br/>Prompt Template"]
    PromptTemplate --> LLMService["LLM Service<br/>(GPT-4)"]
    LLMService --> StructuredJSON["Structured JSON<br/>Experience"]
    StructuredJSON --> ExperienceBank["Experience Banks<br/>(JSONL Files)"]
    
    subgraph "Template Components"
        SystemMessage["system_message"]
        Instructions["Instructions"]
        JSONTemplate["JSON Template"]
    end
    
    PromptTemplate --> SystemMessage
    PromptTemplate --> Instructions
    PromptTemplate --> JSONTemplate
```

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:1-37]()

## Template Structure

### Core Template: generate_mem.yaml

The primary prompt template is defined in `generate_mem.yaml` and contains three main components:

| Component | Purpose | Content |
|-----------|---------|---------|
| `system_message` | Defines LLM role and task | Instructions for converting chat logs to JSON |
| Instructions | Structured rules | 6 specific formatting requirements |
| Template | JSON schema | Expected output format |

```mermaid
graph LR
    subgraph "generate_mem.yaml Structure"
        SystemMsg["system_message:<br/>Role Definition"]
        Rules["Instructions:<br/>6 Formatting Rules"]
        Schema["Template:<br/>JSON Schema"]
    end
    
    subgraph "Output JSON Fields"
        Component["component"]
        TaskType["task_type"]
        TaskDesc["task_description"]
        Result["result"]
        Trajectories["trajectories[]"]
    end
    
    SystemMsg --> Component
    Rules --> TaskType
    Rules --> TaskDesc
    Rules --> Result
    Schema --> Trajectories
    
    subgraph "Trajectory Structure"
        Step["step"]
        Input["input"]
        Output["output"]
        Reasoning["reasoning"]
    end
    
    Trajectories --> Step
    Trajectories --> Input
    Trajectories --> Output
    Trajectories --> Reasoning
```

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:1-37]()

### System Message Design

The system message establishes the LLM's role as a converter of Kubernetes interaction logs:

- **Input**: Series of steps from chat logs describing Kubernetes interactions
- **Output**: Structured JSON experience log
- **Transformation**: Natural language → Standardized experience format

The message specifically targets Kubernetes environment interactions, making it domain-specific for the microservice management use case.

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:1-3]()

## JSON Schema Definition

### Top-Level Structure

The template defines a specific JSON schema with four required top-level fields:

```mermaid
graph TD
    ExperienceJSON["Experience JSON"] --> Component["component:<br/>Component Under Test"]
    ExperienceJSON --> TaskType["task_type:<br/>Task Descriptor"]
    ExperienceJSON --> TaskDesc["task_description:<br/>Overall Task Goal"]
    ExperienceJSON --> Result["result:<br/>Overall Outcome"]
    ExperienceJSON --> Trajectories["trajectories[]:<br/>Step Array"]
    
    subgraph "Example Values"
        CompEx["'nginx-service'"]
        TypeEx["'Verification'"]
        DescEx["'Check service health'"]
        ResEx["'success' | 'failure'"]
    end
    
    Component -.-> CompEx
    TaskType -.-> TypeEx
    TaskDesc -.-> DescEx
    Result -.-> ResEx
```

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:6-10]()

### Trajectory Step Schema

Each trajectory step follows a standardized four-field structure:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `step` | Number | Sequential step order | `1, 2, 3...` |
| `input` | String | Command or action executed | `"kubectl get pods"` |
| `output` | String | Response or result | `"3 pods running"` |
| `reasoning` | String | Why step was taken | `"Verify deployment status"` |

The template includes fallback values for missing data: `"No command executed"` for input and `"No output"` for output when no actual command was run.

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:11-16]()

## Data Flow and Integration

### Natural Language to Structured Data Pipeline

```mermaid
sequenceDiagram
    participant Agent as "ClusterManager/ServiceMaintainer"
    participant ChatLog as "Chat Log Buffer"
    participant Template as "generate_mem.yaml"
    participant LLM as "LLM Service"
    participant Experience as "Experience Bank"
    
    Agent->>ChatLog: "Log interaction steps"
    Agent->>Template: "Load prompt template"
    Template->>LLM: "System message + instructions"
    ChatLog->>LLM: "Raw chat log data"
    LLM->>LLM: "Apply JSON transformation rules"
    LLM->>Experience: "Structured JSON experience"
    
    Note over LLM: "Converts:<br/>Natural language → JSON<br/>Unstructured → Structured<br/>Conversational → Experiential"
```

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:1-37]()

### Template Processing Rules

The template includes six specific processing rules that ensure consistent output:

1. **Field Completeness**: All top-level JSON fields must be present
2. **Data Consistency**: Information must be correctly inferred from conversation
3. **Missing Data Handling**: Standardized fallback values for missing commands
4. **JSON Validity**: Output must be syntactically correct
5. **Step Ordering**: Trajectory steps must maintain sequential numbering
6. **Format Compliance**: Must match the provided JSON template exactly

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:17-18]()

## Template Usage Context

The `generate_mem.yaml` template specifically supports the experience-based learning system by converting operational interactions into reusable experiences. This enables agents to:

- **Learn from Past Actions**: Store successful interaction patterns
- **Avoid Repeated Mistakes**: Capture failure scenarios with reasoning
- **Share Knowledge**: Create transferable experience records
- **Debug Operations**: Maintain detailed step-by-step logs

The template's focus on Kubernetes operations aligns with the self-managing systems' primary use case of microservice environment management.

Sources: [self_managing_systems/microservice/AutoKube/src/prompts/generate_mem.yaml:1-37]()

---

