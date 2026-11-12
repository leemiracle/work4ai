<!-- source: DeepWiki mcp.deepwiki.com · repo Alibaba-NLP/DeepResearch · page 7 Advanced Topics · fetched 2026-10-29 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [inference/react_agent.py](inference/react_agent.py)

</details>



This document covers advanced usage patterns, system customization, and extending the Tongyi DeepResearch inference engine beyond basic deployment. These topics are intended for users who need to customize agent behavior, develop new tools, optimize deployment for production workloads, or integrate with alternative inference providers.

For basic setup and configuration, see [Setup and Configuration](#6). For core inference concepts, see [Core Inference Engine](#2).

---

## Overview

The Tongyi DeepResearch system is designed with extensibility in mind. Advanced users can customize and extend the system in several key areas:

- **Tool Development**: Create custom tools that extend agent capabilities beyond the built-in search, visit, file parsing, and code execution tools
- **Prompt Engineering**: Modify system prompts and tool call formats to customize agent reasoning behavior
- **Distributed Inference**: Deploy multiple vLLM servers with load balancing for high-throughput production workloads
- **Alternative Inference Providers**: Use OpenRouter or other OpenAI-compatible APIs without local GPU resources

The following sections provide technical overviews of these capabilities. For detailed implementation guidance, refer to the corresponding subsections ([7.1](#7.1), [7.2](#7.2), [7.3](#7.3), [7.4](#7.4)).

---

## Architecture for Extensibility

The inference system is structured to support customization at multiple layers. Understanding this architecture is essential for advanced usage.

### System Extension Points

```mermaid
graph TB
    subgraph "User Space"
        UserQuery["User Query"]
        CustomPrompt["Custom System Prompts"]
        CustomTools["Custom Tool Implementations"]
    end
    
    subgraph "Agent Layer: react_agent.py"
        MTRAgent["MultiTurnReactAgent<br/>(_run method)"]
        ToolRegistry["TOOL_MAP Dictionary<br/>(line 38)"]
        PromptLoader["SYSTEM_PROMPT<br/>(line 132)"]
        ServerCaller["call_server Method<br/>(line 59)"]
    end
    
    subgraph "Tool Execution Layer"
        ToolDispatch["custom_call_tool<br/>(line 228)"]
        BuiltInTools["Built-in Tools:<br/>FileParser, Scholar,<br/>Visit, Search,<br/>PythonInterpreter"]
        ToolInterface["BaseTool Interface"]
    end
    
    subgraph "LLM Backend Layer"
        vLLMLocal["Local vLLM Server<br/>(planning_port param)"]
        OpenRouterAPI["OpenRouter API<br/>(line 86-88)"]
        OtherAPIs["Other OpenAI-compatible APIs"]
    end
    
    UserQuery --> MTRAgent
    CustomPrompt -.->|"Replaces"| PromptLoader
    CustomTools -.->|"Extends"| ToolRegistry
    
    MTRAgent --> PromptLoader
    MTRAgent --> ServerCaller
    MTRAgent --> ToolDispatch
    
    PromptLoader --> ServerCaller
    ServerCaller --> vLLMLocal
    ServerCaller -.->|"Alternative"| OpenRouterAPI
    ServerCaller -.->|"Alternative"| OtherAPIs
    
    ToolDispatch --> ToolRegistry
    ToolRegistry --> BuiltInTools
    BuiltInTools --> ToolInterface
    CustomTools -.->|"Implements"| ToolInterface
    
    style CustomPrompt fill:#f9f9f9
    style CustomTools fill:#f9f9f9
    style OpenRouterAPI fill:#f9f9f9
```

**Sources**: [inference/react_agent.py:31-38](), [inference/react_agent.py:47-55](), [inference/react_agent.py:59-68](), [inference/react_agent.py:228-247]()

### Code Entity Map: Tool System

The tool system is the primary extension point for adding new capabilities. Understanding the key code entities is essential:

```mermaid
graph LR
    subgraph "Tool Registry: react_agent.py"
        TOOL_CLASS["TOOL_CLASS List<br/>(line 31-37)"]
        TOOL_MAP["TOOL_MAP Dict<br/>(line 38)"]
    end
    
    subgraph "Tool Implementations"
        FileParser["FileParser()<br/>tool_file.py"]
        Scholar["Scholar()<br/>tool_scholar.py"]
        Visit["Visit()<br/>tool_visit.py"]
        Search["Search()<br/>tool_search.py"]
        Python["PythonInterpreter()<br/>tool_python.py"]
    end
    
    subgraph "Tool Interface"
        BaseTool["BaseTool<br/>(from qwen_agent.tools)"]
        ToolName["tool.name property"]
        ToolCall["tool.call() method"]
    end
    
    subgraph "Agent Invocation"
        CustomCallTool["custom_call_tool()<br/>(line 228)"]
        ToolExecution["Tool execution logic<br/>(line 230-247)"]
    end
    
    TOOL_CLASS --> FileParser
    TOOL_CLASS --> Scholar
    TOOL_CLASS --> Visit
    TOOL_CLASS --> Search
    TOOL_CLASS --> Python
    
    FileParser --> BaseTool
    Scholar --> BaseTool
    Visit --> BaseTool
    Search --> BaseTool
    Python --> BaseTool
    
    BaseTool --> ToolName
    BaseTool --> ToolCall
    
    TOOL_CLASS --> TOOL_MAP
    TOOL_MAP --> CustomCallTool
    CustomCallTool --> ToolExecution
    ToolExecution --> ToolCall
```

**Key Code Entities**:

| Entity | Location | Purpose |
|--------|----------|---------|
| `TOOL_CLASS` | [inference/react_agent.py:31-37]() | List of instantiated tool objects |
| `TOOL_MAP` | [inference/react_agent.py:38]() | Dictionary mapping tool names to tool instances |
| `custom_call_tool()` | [inference/react_agent.py:228-247]() | Tool dispatcher that routes calls to appropriate tools |
| `BaseTool` | qwen_agent.tools | Base class defining tool interface |
| Tool implementations | tool_*.py modules | Individual tool implementations (FileParser, Scholar, Visit, Search, PythonInterpreter) |

**Sources**: [inference/react_agent.py:31-38](), [inference/react_agent.py:228-247]()

---

## Message Flow and Customization Points

Understanding the message flow through the system reveals where customization hooks exist:

```mermaid
sequenceDiagram
    participant User
    participant MultiTurnReactAgent
    participant call_server
    participant vLLM_Server
    participant Tool_System
    
    User->>MultiTurnReactAgent: Question + Config
    
    Note over MultiTurnReactAgent: Build initial messages<br/>(line 132-135)
    MultiTurnReactAgent->>MultiTurnReactAgent: SYSTEM_PROMPT + question
    
    loop Conversation Loop (max MAX_LLM_CALL_PER_RUN)
        MultiTurnReactAgent->>call_server: messages + planning_port
        Note over call_server: API call with retry logic<br/>(line 59-110)
        call_server->>vLLM_Server: OpenAI-compatible request
        vLLM_Server-->>call_server: Response content
        call_server-->>MultiTurnReactAgent: content
        
        MultiTurnReactAgent->>MultiTurnReactAgent: Append assistant message<br/>(line 158)
        
        alt Contains <tool_call>
            MultiTurnReactAgent->>MultiTurnReactAgent: Parse tool call<br/>(line 159-176)
            MultiTurnReactAgent->>Tool_System: custom_call_tool(name, args)
            Tool_System-->>MultiTurnReactAgent: Tool result
            MultiTurnReactAgent->>MultiTurnReactAgent: Append tool_response<br/>(line 177-179)
        end
        
        alt Contains <answer>
            MultiTurnReactAgent->>User: Return final result<br/>(line 180-182)
        end
        
        alt Token limit exceeded
            MultiTurnReactAgent->>MultiTurnReactAgent: Force termination<br/>(line 186-209)
            MultiTurnReactAgent->>User: Return result
        end
        
        alt Max calls exceeded
            MultiTurnReactAgent->>User: Return result<br/>(line 183-185)
        end
    end
```

**Customization Points in Flow**:

1. **System Prompt** (line 132): Replace `SYSTEM_PROMPT` to change agent behavior
2. **API Endpoint** (line 62): Change `openai_api_base` to use different servers or OpenRouter
3. **Generation Parameters** (line 78-82): Modify temperature, top_p, presence_penalty
4. **Tool Registry** (line 38): Add custom tools to `TOOL_MAP`
5. **Tool Parsing** (line 159-176): Customize how tool calls are extracted and formatted
6. **Response Formatting** (line 86-88): Handle different API response formats (e.g., OpenRouter reasoning)

**Sources**: [inference/react_agent.py:59-110](), [inference/react_agent.py:120-226]()

---

## Tool Call Protocol

The agent uses a specific XML-based protocol for tool calls. Understanding this protocol is essential for custom tool development and prompt engineering:

### Tool Call Format

```mermaid
graph TD
    AssistantMsg["Assistant Message"]
    
    subgraph "Message Structure"
        Think[""]
        ToolCall["<tool_call>JSON</tool_call>"]
        Answer["<answer>response</answer>"]
    end
    
    subgraph "Tool Call JSON"
        ToolName["name: tool_name"]
        ToolArgs["arguments: dict"]
    end
    
    subgraph "Tool Response"
        ToolResp["<tool_response>result</tool_response>"]
    end
    
    AssistantMsg --> Think
    Think --> ToolCall
    ToolCall --> ToolName
    ToolCall --> ToolArgs
    
    ToolCall -.->|"Triggers execution"| ToolResp
    ToolResp -.->|"Appended as user message"| AssistantMsg
    
    Think --> Answer
    ToolCall -.->|"If no answer tag"| Think
```

**Protocol Specification**:

| Element | Format | Purpose | Code Reference |
|---------|--------|---------|----------------|
| `` | Agent reasoning | [inference/react_agent.py:56-57]() |
| `<tool_call>` | `<tool_call>{"name": "...", "arguments": {...}}</tool_call>` | Tool invocation | [inference/react_agent.py:159-176]() |
| `<tool_response>` | `<tool_response>text</tool_response>` | Tool result | [inference/react_agent.py:177]() |
| `<answer>` | `<answer>text</answer>` | Final answer | [inference/react_agent.py:180-182]() |
| Stop sequences | `["\n<tool_response>", "<tool_response>"]` | LLM stop tokens | [inference/react_agent.py:77]() |

**Special Cases**:

- **Python Interpreter**: Uses `<code>` tags within `<tool_call>` for code blocks [inference/react_agent.py:162-167]()
- **File References**: File paths prepended to questions for parse_file tool [README.md:141-143]()

**Sources**: [inference/react_agent.py:56-57](), [inference/react_agent.py:159-182](), [README.md:141-143]()

---

## Configuration Parameters

The system exposes several configuration points through environment variables and runtime parameters:

### Environment Variables

| Variable | Purpose | Location | Default |
|----------|---------|----------|---------|
| `MAX_LLM_CALL_PER_RUN` | Maximum agent loop iterations | [inference/react_agent.py:29]() | 100 |
| `SERPER_KEY_ID` | Web search API key | .env | Required |
| `JINA_API_KEYS` | Web reading API key | .env | Required |
| `API_KEY` | OpenAI-compatible API key | .env | Required |
| `DASHSCOPE_API_KEY` | File parsing API key | .env | Required |
| `SANDBOX_FUSION_ENDPOINT` | Python execution sandbox | .env | Optional |
| `MODEL_PATH` | Model weights path | .env | Required |

### Runtime Configuration

```mermaid
graph TB
    subgraph "LLM Configuration"
        GenCfg["llm_generate_cfg dict"]
        Temp["temperature<br/>(line 78)"]
        TopP["top_p<br/>(line 79)"]
        PresencePen["presence_penalty<br/>(line 82)"]
        MaxTokens["max_tokens: 10000<br/>(line 81)"]
    end
    
    subgraph "Agent Configuration"
        MaxCalls["MAX_LLM_CALL_PER_RUN<br/>(line 29, 136)"]
        MaxTime["Time limit: 150 min<br/>(line 140)"]
        MaxContextTokens["Token limit: 110K<br/>(line 186)"]
    end
    
    subgraph "Server Configuration"
        Port["planning_port<br/>(line 62, 129)"]
        Timeout["timeout: 600s<br/>(line 67)"]
        Retry["max_tries: 10<br/>(line 59)"]
    end
    
    GenCfg --> Temp
    GenCfg --> TopP
    GenCfg --> PresencePen
    
    style GenCfg fill:#f9f9f9
    style MaxCalls fill:#f9f9f9
    style Port fill:#f9f9f9
```

**Configuration Points**:

- **Generation Config**: Passed through `llm["generate_cfg"]` dict [inference/react_agent.py:53]()
- **Temperature**: Controls randomness (default 0.6) [inference/react_agent.py:78]()
- **Top-p**: Nucleus sampling (default 0.95) [inference/react_agent.py:79]()
- **Presence Penalty**: Reduces repetition (default 1.1) [inference/react_agent.py:82]()
- **Max Turns**: Configurable via `MAX_LLM_CALL_PER_RUN` environment variable [inference/react_agent.py:29]()

**Sources**: [inference/react_agent.py:29](), [inference/react_agent.py:53-54](), [inference/react_agent.py:59-83](), [inference/react_agent.py:136-210]()

---

## Token Management

The system implements sophisticated token tracking and overflow handling:

### Token Counting and Limits

```mermaid
graph TD
    Messages["messages list"]
    
    subgraph "Token Counting: count_tokens"
        LoadTokenizer["Load AutoTokenizer<br/>(line 113)"]
        ApplyTemplate["apply_chat_template<br/>(line 114)"]
        Tokenize["Tokenize prompt<br/>(line 115)"]
        CountTokens["Count tokens<br/>(line 116)"]
    end
    
    subgraph "Limit Checking"
        CheckLimit["token_count > 110K?<br/>(line 190)"]
        ForceAnswer["Inject termination prompt<br/>(line 193)"]
        FinalCall["Final LLM call<br/>(line 194)"]
        ExtractAnswer["Extract answer<br/>(line 196-201)"]
    end
    
    Messages --> LoadTokenizer
    LoadTokenizer --> ApplyTemplate
    ApplyTemplate --> Tokenize
    Tokenize --> CountTokens
    
    CountTokens --> CheckLimit
    CheckLimit -->|"Yes"| ForceAnswer
    ForceAnswer --> FinalCall
    FinalCall --> ExtractAnswer
    CheckLimit -->|"No"| Messages
```

**Token Management Strategy**:

1. **Periodic Counting**: Token count computed after each round [inference/react_agent.py:187-188]()
2. **Threshold**: Hard limit at 110K tokens (slightly below 128K model capacity) [inference/react_agent.py:186]()
3. **Graceful Degradation**: When limit reached, inject special prompt requesting final answer [inference/react_agent.py:193]()
4. **Forced Termination**: Final LLM call to extract best-effort answer [inference/react_agent.py:194-209]()

**Termination Reasons**:

| Reason | Condition | Code Reference |
|--------|-----------|----------------|
| `"answer"` | Agent produces `<answer>` tag | [inference/react_agent.py:181, 213]() |
| `"generate an answer as token limit reached"` | Token overflow with valid answer | [inference/react_agent.py:198]() |
| `"format error: generate an answer as token limit reached"` | Token overflow without valid answer format | [inference/react_agent.py:201]() |
| `"exceed available llm calls"` | Hit `MAX_LLM_CALL_PER_RUN` | [inference/react_agent.py:218]() |
| `"No answer found after 2h30mins"` | Time limit exceeded | [inference/react_agent.py:140-142]() |

**Sources**: [inference/react_agent.py:112-118](), [inference/react_agent.py:186-209]()

---

## Retry Logic and Error Handling

The system implements exponential backoff retry logic for robust API communication:

### Retry Mechanism

```mermaid
graph TD
    Start["API Call Attempt"]
    
    subgraph "Retry Loop: max_tries=10"
        TryCall["Try API call<br/>(line 74-83)"]
        CheckSuccess["Response valid?<br/>(line 90-94)"]
        ReturnSuccess["Return content<br/>(line 92)"]
        
        CatchError["Catch exceptions:<br/>APIError, APIConnectionError,<br/>APITimeoutError<br/>(line 96-99)"]
        
        CheckRetries["attempt < max_tries?<br/>(line 101)"]
        CalcBackoff["sleep_time = base * 2^attempt<br/>+ random(0,1)<br/>min(sleep_time, 30)<br/>(line 102-103)"]
        Sleep["time.sleep(sleep_time)<br/>(line 106)"]
        
        AllFailed["Return error message<br/>(line 110)"]
    end
    
    Start --> TryCall
    TryCall --> CheckSuccess
    CheckSuccess -->|"Yes"| ReturnSuccess
    CheckSuccess -->|"No"| CatchError
    
    CatchError --> CheckRetries
    CheckRetries -->|"Yes"| CalcBackoff
    CalcBackoff --> Sleep
    Sleep --> TryCall
    
    CheckRetries -->|"No"| AllFailed
```

**Retry Strategy**:

- **Base Sleep Time**: 1 second [inference/react_agent.py:70]()
- **Exponential Backoff**: `sleep_time = base_sleep_time * (2 ** attempt) + random(0, 1)` [inference/react_agent.py:102]()
- **Max Sleep Time**: 30 seconds cap [inference/react_agent.py:103]()
- **Max Attempts**: 10 tries [inference/react_agent.py:59]()
- **Random Jitter**: Prevents thundering herd [inference/react_agent.py:102]()

**Error Types Caught**:

- `APIError`: API-level errors from OpenAI client
- `APIConnectionError`: Network connectivity issues
- `APITimeoutError`: Request timeout (600s configured) [inference/react_agent.py:67]()

**Sources**: [inference/react_agent.py:59-110]()

---

## OpenRouter Integration Notes

OpenRouter provides access to Tongyi DeepResearch without local GPU resources. The integration requires specific modifications:

### Required Code Changes

The system includes commented code for OpenRouter compatibility:

```python
# Lines 86-88 in inference/react_agent.py
# reasoning_content = ""
# content = reasoning_content + content
```

**OpenRouter Differences**:

1. **Reasoning Field**: OpenRouter returns reasoning in separate `message.reasoning` field
2. **Content Concatenation**: Must manually prepend reasoning content with `<think>` tags
3. **API Configuration**: Replace `openai_api_base` with OpenRouter URL
4. **Model Name**: Use `alibaba/tongyi-deepresearch-30b-a3b`

**Configuration Table**:

| Parameter | Local vLLM | OpenRouter |
|-----------|------------|------------|
| `api_key` | "EMPTY" | OpenRouter API key |
| `base_url` | `http://127.0.0.1:{port}/v1` | `https://openrouter.ai/api/v1` |
| `model` | Model path | `alibaba/tongyi-deepresearch-30b-a3b` |
| Reasoning handling | Included in content | Separate field (lines 86-88) |

For complete OpenRouter setup instructions, see [OpenRouter Integration](#7.4).

**Sources**: [README.md:172-180](), [inference/react_agent.py:86-88]()

---

## Summary

This page introduced the advanced capabilities of the Tongyi DeepResearch system:

- **Tool System**: Extensible through `TOOL_MAP` registry and `BaseTool` interface
- **Prompt Engineering**: XML-based protocol with `<think>`, `<tool_call>`, `<answer>` tags
- **Distributed Inference**: Multi-server deployment through `planning_port` parameter
- **OpenRouter**: Alternative inference without local GPUs

For implementation details on each topic, see the corresponding subsections:

- [Custom Tool Development](#7.1)
- [Prompt Engineering](#7.2)
- [Distributed Inference](#7.3)
- [OpenRouter Integration](#7.4)

**Sources**: [inference/react_agent.py](), [README.md:172-180]()

---

