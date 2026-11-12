<!-- source: DeepWiki mcp.deepwiki.com · repo Significant-Gravitas/AutoGPT · extra page LLM Integration · fetched 2026-10-26 -->

# LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [autogpt_platform/backend/backend/blocks/llm.py](autogpt_platform/backend/backend/blocks/llm.py)
- [autogpt_platform/backend/backend/blocks/test/test_llm.py](autogpt_platform/backend/backend/blocks/test/test_llm.py)
- [autogpt_platform/backend/backend/copilot/sdk/compaction.py](autogpt_platform/backend/backend/copilot/sdk/compaction.py)
- [autogpt_platform/backend/backend/copilot/sdk/compaction_test.py](autogpt_platform/backend/backend/copilot/sdk/compaction_test.py)
- [autogpt_platform/backend/backend/copilot/sdk/conftest.py](autogpt_platform/backend/backend/copilot/sdk/conftest.py)
- [autogpt_platform/backend/backend/copilot/sdk/prompt_too_long_test.py](autogpt_platform/backend/backend/copilot/sdk/prompt_too_long_test.py)
- [autogpt_platform/backend/backend/copilot/sdk/thinking_blocks_test.py](autogpt_platform/backend/backend/copilot/sdk/thinking_blocks_test.py)
- [autogpt_platform/backend/backend/copilot/sdk/transcript_builder.py](autogpt_platform/backend/backend/copilot/sdk/transcript_builder.py)
- [autogpt_platform/backend/backend/copilot/tools/run_block.py](autogpt_platform/backend/backend/copilot/tools/run_block.py)
- [autogpt_platform/backend/backend/copilot/tools/run_block_test.py](autogpt_platform/backend/backend/copilot/tools/run_block_test.py)
- [autogpt_platform/backend/backend/data/block_cost_config.py](autogpt_platform/backend/backend/data/block_cost_config.py)
- [autogpt_platform/backend/backend/util/prompt.py](autogpt_platform/backend/backend/util/prompt.py)
- [autogpt_platform/backend/backend/util/prompt_test.py](autogpt_platform/backend/backend/util/prompt_test.py)
- [docs/integrations/block-integrations/llm.md](docs/integrations/block-integrations/llm.md)
- [docs/integrations/block-integrations/misc.md](docs/integrations/block-integrations/misc.md)

</details>



## Purpose and Scope

This document describes the LLM abstraction layer in the AutoGPT Platform backend, which provides a unified interface for calling multiple Large Language Model providers. The abstraction handles provider-specific API differences, prompt compression, tool call format conversion, and token usage tracking.

For information about AI blocks that use this integration layer, see [AI Blocks](#3.2.8). For the SmartDecisionMaker block that orchestrates tool calls via LLMs, see [AI Blocks](#3.2.8).

---

## Architecture Overview

The LLM integration layer provides a single `llm_call` function that abstracts away differences between 8+ LLM providers. This allows AI blocks to work with any supported model without provider-specific code.

```mermaid
graph TB
    subgraph "AI Blocks Layer"
        TEXT["AITextGeneratorBlock"]
        STRUCT["AIStructuredResponseGeneratorBlock"]
        SMART["SmartDecisionMakerBlock"]
        COND["AIConditionBlock"]
    end
    
    subgraph "LLM Abstraction Layer"
        LLM_CALL["llm_call()<br/>Unified Interface"]
        MODEL_META["LlmModel Enum<br/>MODEL_METADATA"]
        COMPRESS["compress_context()"]
        TOOL_CONV["Tool Format Converters"]
    end
    
    subgraph "Provider Clients"
        OPENAI["OpenAI Client<br/>AsyncOpenAI"]
        ANTHROPIC["Anthropic Client<br/>AsyncAnthropic"]
        GROQ["Groq Client<br/>AsyncGroq"]
        OLLAMA["Ollama Client<br/>AsyncClient"]
        OPEN_ROUTER["OpenRouter<br/>via OpenAI API"]
        LLAMA_API["Llama API<br/>via OpenAI API"]
        AIML["AI/ML API<br/>via OpenAI API"]
        V0["v0 by Vercel<br/>via OpenAI API"]
    end
    
    TEXT --> LLM_CALL
    STRUCT --> LLM_CALL
    SMART --> LLM_CALL
    COND --> LLM_CALL
    
    LLM_CALL --> MODEL_META
    LLM_CALL --> COMPRESS
    LLM_CALL --> TOOL_CONV
    
    LLM_CALL --> OPENAI
    LLM_CALL --> ANTHROPIC
    LLM_CALL --> GROQ
    LLM_CALL --> OLLAMA
    LLM_CALL --> OPEN_ROUTER
    LLM_CALL --> LLAMA_API
    LLM_CALL --> AIML
    LLM_CALL --> V0
```

**Sources:** [autogpt_platform/backend/backend/blocks/llm.py:1-768]()

---

## Core Components

### The llm_call Function

The `llm_call` function at [autogpt_platform/backend/backend/blocks/llm.py:410-768]() is the unified interface for all LLM interactions. It accepts standardized parameters and routes requests to the appropriate provider.

**Function Signature:**

```python
async def llm_call(
    credentials: APIKeyCredentials,
    llm_model: LlmModel,
    prompt: list[dict],
    max_tokens: int | None,
    force_json_output: bool = False,
    tools: list[dict] | None = None,
    ollama_host: str = "localhost:11434",
    parallel_tool_calls=None,
    compress_prompt_to_fit: bool = True,
) -> LLMResponse
```

**Parameters:**
- `credentials`: API key credentials for the provider
- `llm_model`: Model identifier from the `LlmModel` enum
- `prompt`: List of message dictionaries in OpenAI format
- `max_tokens`: Maximum tokens to generate (automatically capped based on context window)
- `force_json_output`: Whether to request JSON-only responses
- `tools`: Tool definitions for function calling (OpenAI format)
- `ollama_host`: Host for local Ollama instances
- `parallel_tool_calls`: Whether to allow multiple tool calls in one response
- `compress_prompt_to_fit`: Whether to compress prompts that exceed context window

**Return Value:**

The function returns an `LLMResponse` object [autogpt_platform/backend/backend/blocks/llm.py:326-334]():

```python
class LLMResponse(BaseModel):
    raw_response: Any
    prompt: List[Any]
    response: str
    tool_calls: Optional[List[ToolContentBlock]] | None
    prompt_tokens: int
    completion_tokens: int
    reasoning: Optional[str] = None
```

**Token Management:**

The function automatically manages token limits [autogpt_platform/backend/backend/blocks/llm.py:444-456]():

1. Optionally compresses prompts to fit context window
2. Estimates input token count
3. Calculates available tokens: `context_window - input_tokens`
4. Caps `max_tokens` to the minimum of:
   - Available tokens
   - Model's max output tokens
   - User-specified max tokens

**Sources:** [autogpt_platform/backend/backend/blocks/llm.py:410-768](), [autogpt_platform/backend/backend/blocks/llm.py:326-334]()

---

### LlmModel Enum and Model Metadata

The `LlmModel` enum [autogpt_platform/backend/backend/blocks/llm.py:88-189]() defines all supported models with their metadata.

```mermaid
graph LR
    subgraph "LlmModel Enum"
        O3["O3<br/>o3-2025-04-16"]
        O3_MINI["O3_MINI<br/>o3-mini"]
        GPT5_2["GPT5_2<br/>gpt-5.2-2025-12-11"]
        GPT4O["GPT4O<br/>gpt-4o"]
        CLAUDE_4_5_SONNET["CLAUDE_4_5_SONNET<br/>claude-sonnet-4-5-20250929"]
        GEMINI_2_5_PRO["GEMINI_2_5_PRO<br/>google/gemini-2.5-pro"]
    end
    
    subgraph "ModelMetadata"
        PROVIDER["provider: str"]
        CONTEXT["context_window: int"]
        MAX_OUT["max_output_tokens: int | None"]
    end
    
    O3 --> PROVIDER
    O3 --> CONTEXT
    O3 --> MAX_OUT
    
    GPT5_2 --> PROVIDER
    CLAUDE_4_5_SONNET --> PROVIDER
    GEMINI_2_5_PRO --> PROVIDER
```

**Model Metadata Structure:**

Each model in `MODEL_METADATA` [autogpt_platform/backend/backend/blocks/llm.py:191-306]() contains:

| Field | Description | Example |
|-------|-------------|---------|
| `provider` | Provider name (openai, anthropic, groq, etc.) | "openai" |
| `context_window` | Maximum input + output tokens | 200000 |
| `max_output_tokens` | Maximum tokens for completion | 100000 |

**Provider Groups:**

| Provider | Model Count | Examples |
|----------|-------------|----------|
| OpenAI | 17 | O3, GPT-5.2, GPT-4o, GPT-4.1 |
| Anthropic | 8 | Claude 4.1 Opus, Claude 4.5 Sonnet |
| OpenRouter | 32 | Gemini 2.5 Pro, DeepSeek R1, Grok 4 |
| Groq | 2 | Llama 3.3 70B, Llama 3.1 8B |
| Ollama | 5 | Llama 3.3, Dolphin Mistral |
| AI/ML API | 5 | Qwen 2.5 72B, Llama 3.3 70B |
| Llama API | 4 | Llama 4 Scout, Llama 3.3 70B |
| v0 by Vercel | 3 | v0-1.5-md, v0-1.5-lg |

**Default Model:**

The system uses `DEFAULT_LLM_MODEL = LlmModel.GPT5_2` [autogpt_platform/backend/backend/blocks/llm.py:308]() as the default across all AI blocks.

**Sources:** [autogpt_platform/backend/backend/blocks/llm.py:88-306]()

---

### Provider Implementations

Each provider has a dedicated code path within `llm_call` that handles API-specific details:

```mermaid
graph TB
    LLM_CALL["llm_call()"]
    
    subgraph "Provider Routing"
        ROUTE["provider = llm_model.metadata.provider"]
    end
    
    subgraph "OpenAI Path"
        OAI_CLIENT["AsyncOpenAI(api_key)"]
        OAI_CALL["chat.completions.create()"]
        OAI_TOOLS["tools parameter<br/>OpenAI format"]
        OAI_PARALLEL["parallel_tool_calls parameter"]
    end
    
    subgraph "Anthropic Path"
        ANT_CLIENT["AsyncAnthropic(api_key)"]
        ANT_CONVERT["convert_openai_tool_fmt_to_anthropic()"]
        ANT_SYSPROMPT["Extract system messages"]
        ANT_CALL["messages.create()"]
        ANT_PARSE["Parse tool_use blocks"]
    end
    
    subgraph "OpenRouter/Llama/v0 Paths"
        OPENAI_COMPAT["OpenAI-compatible clients<br/>with custom base_url"]
    end
    
    LLM_CALL --> ROUTE
    ROUTE -->|"provider=='openai'"| OAI_CLIENT
    ROUTE -->|"provider=='anthropic'"| ANT_CLIENT
    ROUTE -->|"provider=='open_router'<br/>provider=='llama_api'<br/>provider=='v0'"| OPENAI_COMPAT
    
    OAI_CLIENT --> OAI_CALL
    OAI_CALL --> OAI_TOOLS
    OAI_CALL --> OAI_PARALLEL
    
    ANT_CLIENT --> ANT_CONVERT
    ANT_CLIENT --> ANT_SYSPROMPT
    ANT_CONVERT --> ANT_CALL
    ANT_SYSPROMPT --> ANT_CALL
    ANT_CALL --> ANT_PARSE
```

**OpenAI Provider [autogpt_platform/backend/backend/blocks/llm.py:458-490]():**

- Direct use of `openai.AsyncOpenAI`
- Supports `tools` parameter for function calling
- Supports `parallel_tool_calls` parameter
- Supports `response_format` for JSON mode
- Returns tool calls in `message.tool_calls` array

**Anthropic Provider [autogpt_platform/backend/backend/blocks/llm.py:491-574]():**

Key differences:
1. System messages extracted separately [autogpt_platform/backend/backend/blocks/llm.py:495-496]()
2. Consecutive messages with same role are combined [autogpt_platform/backend/backend/blocks/llm.py:498-511]()
3. Tools converted from OpenAI format via `convert_openai_tool_fmt_to_anthropic()` [autogpt_platform/backend/backend/blocks/llm.py:336-365]()
4. Tool calls returned in `content` array as `tool_use` blocks [autogpt_platform/backend/backend/blocks/llm.py:529-545]()

**OpenRouter/Llama API/v0 Providers:**

These use the OpenAI-compatible API with custom base URLs:
- OpenRouter: `https://openrouter.ai/api/v1` [autogpt_platform/backend/backend/blocks/llm.py:621]()
- Llama API: `https://api.llama.com/compat/v1/` [autogpt_platform/backend/backend/blocks/llm.py:663]()
- v0: `https://api.v0.dev/v1` [autogpt_platform/backend/backend/blocks/llm.py:733]()

**Groq Provider [autogpt_platform/backend/backend/blocks/llm.py:575-595]():**

Uses `groq.AsyncGroq` client but does not support tools.

**Ollama Provider [autogpt_platform/backend/backend/blocks/llm.py:596-617]():**

Local model hosting via `ollama.AsyncClient`. Uses `generate()` instead of chat completions API.

**Sources:** [autogpt_platform/backend/backend/blocks/llm.py:458-765]()

---

### Tool Call Format Conversion

The system handles two major tool calling formats:

```mermaid
graph TB
    subgraph "OpenAI Format"
        OAI_REQ["Request: tools array"]
        OAI_RESP["Response: message.tool_calls"]
        OAI_STRUCT["Structure:<br/>{id, type, function: {name, arguments}}"]
    end
    
    subgraph "Anthropic Format"
        ANT_REQ["Request: tools array<br/>(converted structure)"]
        ANT_RESP["Response: content array"]
        ANT_STRUCT["Structure:<br/>{type: 'tool_use', id, name, input}"]
    end
    
    subgraph "Converter Function"
        CONVERT["convert_openai_tool_fmt_to_anthropic()"]
        PARAM_MAP["parameters → input_schema"]
        FUNC_MAP["function → top-level"]
    end
    
    OAI_REQ --> CONVERT
    CONVERT --> PARAM_MAP
    CONVERT --> FUNC_MAP
    PARAM_MAP --> ANT_REQ
    FUNC_MAP --> ANT_REQ
```

**OpenAI Tool Format:**

Request format [autogpt_platform/backend/backend/blocks/llm.py:459]():
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]
```

Response format [autogpt_platform/backend/backend/blocks/llm.py:384-398]():
```python
tool_calls = [
    {
        "id": "call_abc123",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": '{"location": "San Francisco"}'
        }
    }
]
```

**Anthropic Tool Format:**

The `convert_openai_tool_fmt_to_anthropic()` function [autogpt_platform/backend/backend/blocks/llm.py:336-365]() transforms OpenAI tools:

```python
# Input: OpenAI format
{"type": "function", "function": {"name": "...", "parameters": {...}}}

# Output: Anthropic format
{"name": "...", "description": "...", "input_schema": {"type": "object", "properties": {...}}}
```

Response parsing [autogpt_platform/backend/backend/blocks/llm.py:529-545]():
```python
# Anthropic returns tool_use blocks in content array
for content_block in response.content:
    if content_block.type == "tool_use":
        tool_calls.append({
            "id": content_block.id,
            "type": "tool_use",
            "function": {
                "name": content_block.name,
                "arguments": json.dumps(content_block.input)
            }
        })
```

**Tool Call Extraction:**

Helper functions extract tool calls from provider-specific responses:
- `extract_openai_tool_calls()` [autogpt_platform/backend/backend/blocks/llm.py:384-398]()
- `extract_openai_reasoning()` [autogpt_platform/backend/backend/blocks/llm.py:368-381]()

**Sources:** [autogpt_platform/backend/backend/blocks/llm.py:336-398](), [autogpt_platform/backend/backend/blocks/llm.py:529-545]()

---

### Prompt Compression

The `compress_context()` function [autogpt_platform/backend/backend/util/prompt.py:143-290]() reduces prompt size when it exceeds the model's context window.

```mermaid
graph TB
    INPUT["Input: messages list<br/>target_tokens<br/>reserve for output"]
    
    CHECK["total_tokens + reserve > target?"]
    
    STEP0["Step 0: Normalize content<br/>Convert non-string to JSON strings"]
    STEP1["Step 1: Token-aware truncation<br/>Cap each message content<br/>Halve cap if still over limit"]
    STEP2["Step 2: Middle-out deletion<br/>Delete whole messages from center<br/>Protect tool messages"]
    STEP3["Step 3: Last-chance trim<br/>Truncate first and last messages"]
    
    FAIL["lossy_ok?"]
    RAISE["Raise ValueError"]
    RETURN["Return trimmed messages"]
    
    PROTECT["Protected messages:<br/>- First message<br/>- Last message<br/>- Tool calls/responses<br/>- MAIN_OBJECTIVE_PREFIX"]
    
    INPUT --> CHECK
    CHECK -->|"Yes"| STEP0
    CHECK -->|"No"| RETURN
    
    STEP0 --> STEP1
    STEP1 -->|"Still over"| STEP2
    STEP1 -->|"Under limit"| RETURN
    
    STEP2 -->|"Still over"| STEP3
    STEP2 -->|"Under limit"| RETURN
    
    STEP3 -->|"Still over"| FAIL
    STEP3 -->|"Under limit"| RETURN
    
    FAIL -->|"No"| RAISE
    FAIL -->|"Yes"| RETURN
    
    PROTECT -.->|"Never truncate/delete"| STEP1
    PROTECT -.->|"Never truncate/delete"| STEP2
```

**Compression Strategy:**

The function uses a 4-step strategy [autogpt_platform/backend/backend/util/prompt.py:156-189]():

**Step 0: Normalize Content [autogpt_platform/backend/backend/util/prompt.py:203-218]():**
- Convert non-string content to JSON strings
- Skip tool messages and first/last messages
- Cap at 20,000 characters to prevent pathological blobs

**Step 1: Token-Aware Truncation [autogpt_platform/backend/backend/util/prompt.py:220-241]():**
- Start with `start_cap` tokens per message (default 8,192)
- Apply cap to all messages except first and last
- Halve cap repeatedly until reaching `floor_cap` (default 128)
- For tool messages, only truncate tool result content via `_truncate_tool_message_content()` [autogpt_platform/backend/backend/util/prompt.py:100-120]()

**Step 2: Middle-Out Deletion [autogpt_platform/backend/backend/util/prompt.py:243-260]():**
- Delete whole messages starting from the center
- Work outward symmetrically
- Never delete messages containing tool calls/responses
- Protect messages with `MAIN_OBJECTIVE_PREFIX` [autogpt_platform/backend/backend/util/prompt.py:13]()

**Step 3: Last-Chance Trim [autogpt_platform/backend/backend/util/prompt.py:262-271]():**
- Truncate first and last message content to `floor_cap`
- Uses `_truncate_middle_tokens()` to keep beginning and end

**Token Counting:**

Token counting uses tiktoken [autogpt_platform/backend/backend/util/prompt.py:20-70]():
- `_msg_tokens()` counts wrapper tokens (3-4 per message) plus content
- Handles tool calls in both OpenAI and Anthropic formats
- Counts tool_use and tool_result blocks in content arrays

**Integration with llm_call:**

When `compress_prompt_to_fit=True` [autogpt_platform/backend/backend/blocks/llm.py:444-449](), prompts are compressed to half the context window before sending to provider.

**Sources:** [autogpt_platform/backend/backend/util/prompt.py:143-290](), [autogpt_platform/backend/backend/util/prompt.py:20-70]()

---

### Token Usage Tracking

Token usage is tracked via `NodeExecutionStats` and accumulated across LLM calls and retries.

```mermaid
graph TB
    subgraph "LLM Call Flow"
        CALL["llm_call()"]
        RESPONSE["LLMResponse<br/>prompt_tokens<br/>completion_tokens"]
    end
    
    subgraph "Block Execution"
        AI_BLOCK["AIBlockBase"]
        MERGE["merge_stats()"]
        EXEC_STATS["execution_stats<br/>NodeExecutionStats"]
    end
    
    subgraph "NodeExecutionStats"
        INPUT_TOK["input_token_count"]
        OUTPUT_TOK["output_token_count"]
        CALL_COUNT["llm_call_count"]
        RETRY_COUNT["llm_retry_count"]
    end
    
    subgraph "Database Persistence"
        NODE_EXEC["AgentNodeExecution"]
        STATS_FIELD["execution_stats JSON"]
    end
    
    CALL --> RESPONSE
    RESPONSE --> AI_BLOCK
    AI_BLOCK --> MERGE
    MERGE --> INPUT_TOK
    MERGE --> OUTPUT_TOK
    MERGE --> CALL_COUNT
    MERGE --> RETRY_COUNT
    
    EXEC_STATS --> NODE_EXEC
    EXEC_STATS --> STATS_FIELD
```

**AIBlockBase Class:**

All AI-powered blocks extend `AIBlockBase` [autogpt_platform/backend/backend/blocks/llm.py:770-778](), which provides:

```python
class AIBlockBase(Block, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = []

    def merge_llm_stats(self, block: "AIBlockBase"):
        self.merge_stats(block.execution_stats)
        self.prompt = block.prompt
```

**Stats Accumulation Pattern:**

Blocks track stats across multiple LLM calls [autogpt_platform/backend/backend/blocks/smart_decision_maker.py:609-615]():

```python
resp = await llm.llm_call(...)

# Track LLM usage stats per call
self.merge_stats(
    NodeExecutionStats(
        input_token_count=resp.prompt_tokens,
        output_token_count=resp.completion_tokens,
        llm_call_count=1,
    )
)
```

**Retry Tracking:**

The `AIStructuredResponseGeneratorBlock` tracks retries [autogpt_platform/backend/backend/blocks/llm.py:921-1044]():
- Each retry increments `llm_retry_count`
- Token counts accumulate across all attempts
- Final stats reflect total usage

**Persistence:**

Stats are persisted to the `AgentNodeExecution` table as JSON [autogpt_platform/backend/backend/data/model.py](), enabling:
- Usage analytics
- Credit calculations
- Performance monitoring

**Sources:** [autogpt_platform/backend/backend/blocks/llm.py:770-778](), [autogpt_platform/backend/backend/blocks/smart_decision_maker.py:609-615]()

---

## Cost Configuration

Model costs are configured in `BLOCK_COSTS` [autogpt_platform/backend/backend/data/block_cost_config.py:265-643](), mapping block types and model selections to credit amounts.

```mermaid
graph TB
    subgraph "Cost Configuration"
        MODEL_COST["MODEL_COST dict<br/>{LlmModel: int}"]
        LLM_COST["LLM_COST list<br/>BlockCost objects"]
        BLOCK_COSTS["BLOCK_COSTS dict<br/>{Block class: costs}"]
    end
    
    subgraph "Cost Filters"
        FILTER_MODEL["cost_filter: {model: ...}"]
        FILTER_CREDS["cost_filter: {credentials: {...}}"]
    end
    
    subgraph "Provider-Specific Costs"
        ANTHROPIC_COSTS["Anthropic models<br/>1-21 credits"]
        OPENAI_COSTS["OpenAI models<br/>1-16 credits"]
        GROQ_COSTS["Groq models<br/>1 credit"]
        OPEN_ROUTER_COSTS["OpenRouter models<br/>1-9 credits"]
    end
    
    MODEL_COST --> LLM_COST
    LLM_COST --> FILTER_MODEL
    LLM_COST --> FILTER_CREDS
    
    LLM_COST --> ANTHROPIC_COSTS
    LLM_COST --> OPENAI_COSTS
    LLM_COST --> GROQ_COSTS
    LLM_COST --> OPEN_ROUTER_COSTS
    
    LLM_COST --> BLOCK_COSTS
```

**Cost Structure:**

| Cost Tier | Credit Amount | Example Models |
|-----------|---------------|----------------|
| Low (1) | 1 credit | GPT-4o-mini, Claude 3 Haiku, Groq models |
| Medium (2-5) | 2-5 credits | GPT-4.1, GPT-5, Claude 3.7 Sonnet |
| High (6-16) | 6-16 credits | O1, Claude 4.5 Opus |
| Premium (21) | 21 credits | Claude 4 Opus, Claude 4.1 Opus |

**Cost Definition [autogpt_platform/backend/backend/data/block_cost_config.py:60-138]():**

```python
MODEL_COST: dict[LlmModel, int] = {
    LlmModel.O3: 4,
    LlmModel.GPT5_2: 6,
    LlmModel.GPT4O_MINI: 1,
    LlmModel.CLAUDE_4_5_SONNET: 9,
    LlmModel.CLAUDE_4_6_OPUS: 14, # Updated from CLAUDE_4_1_OPUS: 21
    # ... 70+ model cost mappings
}
```

**BlockCost Objects [autogpt_platform/backend/backend/data/block_cost_config.py:145-261]():**

Costs are filtered by:
- Model name
- Credentials (provider, ID, type)

```python
BlockCost(
    cost_type=BlockCostType.RUN,
    cost_filter={
        "model": model,
        "credentials": {
            "id": openai_credentials.id,
            "provider": openai_credentials.provider,
            "type": openai_credentials.type,
        },
    },
    cost_amount=cost,
)
```

**Blocks Using LLM Costs [autogpt_platform/backend/backend/data/block_cost_config.py:265-513]():**

All AI blocks reference `LLM_COST`:
- `AIConversationBlock`
- `AITextGeneratorBlock`
- `AIStructuredResponseGeneratorBlock`
- `AITextSummarizerBlock`
- `AIListGeneratorBlock`
- `OrchestratorBlock` (formerly `SmartDecisionMakerBlock`)

**Sources:** [autogpt_platform/backend/backend/data/block_cost_config.py:60-261](), [autogpt_platform/backend/backend/data/block_cost_config.py:265-513]()

---

## Usage Patterns

### Pattern 1: Direct LLM Call in AI Blocks

`AITextGeneratorBlock` [autogpt_platform/backend/backend/blocks/llm.py:1249-1326]() uses delegation:

```python
async def run(self, input_data: Input, *, credentials: APIKeyCredentials, **kwargs):
    # Delegate to AIStructuredResponseGeneratorBlock
    struct_block = AIStructuredResponseGeneratorBlock()
    response = await struct_block.llm_call(
        input_data=struct_input,
        credentials=credentials,
    )
    
    # Merge stats from delegated block
    self.merge_llm_stats(struct_block)
    
    yield "response", response["response"]
```

### Pattern 2: Tool Call Orchestration

`OrchestratorBlock` [autogpt_platform/backend/backend/blocks/orchestrator.py:585-684]() orchestrates tool calls:

```python
# Get tool signatures from connected blocks
tool_functions = await self._create_tool_node_signatures(node_id)

# Call LLM with tools
resp = await llm.llm_call(
    credentials=credentials,
    llm_model=input_data.model,
    prompt=current_prompt,
    tools=tool_functions,
    parallel_tool_calls=input_data.multiple_tool_calls,
)

# Track stats
self.merge_stats(
    NodeExecutionStats(
        input_token_count=resp.prompt_tokens,
        output_token_count=resp.completion_tokens,
        llm_call_count=1,
    )
)

# Process tool calls
for tool_call in resp.tool_calls:
    # Execute the tool and feed results back to LLM
    ...
```

### Pattern 3: Conditional Logic with AI

`AIConditionBlock` [autogpt_platform/backend/backend/blocks/ai_condition.py:122-186]() uses LLM for natural language conditions:

```python
prompt = [
    {"role": "system", "content": "...evaluate conditions..."},
    {"role": "user", "content": f"Input: {input_str}\nCondition: {condition}"}
]

response = await self.llm_call(
    credentials=credentials,
    llm_model=input_data.model,
    prompt=prompt,
    max_tokens=50,
)

# Parse true/false from response
result = response.response.strip().lower() == "true"
```

### Pattern 4: Multi-Call with Retries

`AIStructuredResponseGeneratorBlock` [autogpt_platform/backend/backend/blocks/llm.py:921-1044]() retries on invalid responses:

```python
for attempt in range(input_data.retry):
    try:
        resp = await self.llm_call(...)
        
        # Track attempt
        self.merge_stats(NodeExecutionStats(
            input_token_count=resp.prompt_tokens,
            output_token_count=resp.completion_tokens,
            llm_call_count=1,
            llm_retry_count=(1 if attempt > 0 else 0),
        ))
        
        # Validate response format
        parsed = self.parse_response(resp.response)
        if valid:
            break
        
    except Exception as e:
        if attempt == input_data.retry - 1:
            raise
```

**Sources:** [autogpt_platform/backend/backend/blocks/llm.py:1249-1326](), [autogpt_platform/backend/backend/blocks/orchestrator.py:585-684](), [autogpt_platform/backend/backend/blocks/ai_condition.py:122-186](), [autogpt_platform/backend/backend/blocks/llm.py:921-1044]()

---

