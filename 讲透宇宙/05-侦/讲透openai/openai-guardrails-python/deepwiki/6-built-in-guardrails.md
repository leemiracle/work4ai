<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-guardrails-python · page 6 Built-in Guardrails · fetched 2026-10-26 -->

# Built-in Guardrails

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/assets/images/guardrails-python-config-screenshot-100pct-q70.webp](docs/assets/images/guardrails-python-config-screenshot-100pct-q70.webp)

</details>



This page provides a comprehensive overview of all built-in guardrail checks included in the OpenAI Guardrails Python package. Each guardrail implements a specific safety or compliance check that can be applied at different stages of the LLM interaction pipeline.

For detailed information about individual guardrails, see the child pages under this section (#6.1-#6.10). For information about how to configure and execute these guardrails, see [Runtime Execution Model](#3.5) and [Configuration Files](#2.2). For information about creating custom guardrails, see [LLM-Based Guardrail Framework](#6.8).

---

## Guardrail Categories

Built-in guardrails are organized into two primary categories based on their execution engine:

### API-Based Guardrails

API-based guardrails leverage external services or specialized libraries for content analysis. These guardrails typically have lower latency and more deterministic behavior than LLM-based checks.

| Guardrail | Description | Engine | Stage Compatibility |
|-----------|-------------|--------|-------------------|
| **Moderation** | Content moderation using OpenAI's Moderation API across 13 categories | API | input, output |
| **URL Filter** | Domain allowlist/blocklist validation and URL filtering | API | input, pre_flight |
| **Contains PII** | Personally Identifiable Information detection using Presidio framework | API | input, output, pre_flight |

### LLM-Based Guardrails

LLM-based guardrails use language models to perform nuanced content analysis. These guardrails can be conversation-aware and support multi-turn reasoning.

| Guardrail | Description | Engine | Stage Compatibility | Conversation Aware |
|-----------|-------------|--------|--------------------|--------------------|
| **Jailbreak** | Detects jailbreak attempts using 7-technique taxonomy | LLM | input | Yes |
| **NSFW Text** | Detects workplace-inappropriate content | LLM | output | No |
| **Hallucination Detection** | Validates responses against vector stores and file search | LLM | output | No |
| **Prompt Injection** | Detects prompt injection in tool calls and validates intent alignment | LLM | input | Yes |
| **Off Topic Prompts** | Ensures prompts stay within defined business scope | LLM | input | Yes |
| **User-defined LLM** | Custom LLM-based guardrails with user-provided system prompts | LLM | input, output | Configurable |

**Sources:** [README.md:183-195]()

---

## Guardrail Registry System

All built-in guardrails register themselves with the `default_spec_registry`, which maintains metadata about each guardrail's capabilities and configuration schema.

```mermaid
graph TB
    subgraph "Registry Components"
        Registry["default_spec_registry<br/>(Central Registry)"]
        Metadata["GuardrailSpecMetadata<br/>- spec_id: str<br/>- engine: 'API' | 'LLM'<br/>- media_type: 'text' | 'conversation'<br/>- stage_compatibility"]
    end
    
    subgraph "API-Based Guardrails"
        Mod["Moderation<br/>src/guardrails/checks/moderation.py"]
        URL["URL Filter<br/>src/guardrails/checks/url_filter.py"]
        PII["Contains PII<br/>src/guardrails/checks/contains_pii.py"]
    end
    
    subgraph "LLM-Based Guardrails"
        JB["Jailbreak<br/>src/guardrails/checks/jailbreak.py"]
        NSFW["NSFW Text<br/>src/guardrails/checks/nsfw_text.py"]
        Hal["Hallucination Detection<br/>src/guardrails/checks/hallucination.py"]
        PI["Prompt Injection<br/>src/guardrails/checks/prompt_injection.py"]
        OT["Off Topic Prompts<br/>src/guardrails/checks/off_topic.py"]
        Custom["User-defined LLM<br/>src/guardrails/checks/custom_llm.py"]
    end
    
    Mod -->|"registers with"| Registry
    URL -->|"registers with"| Registry
    PII -->|"registers with"| Registry
    JB -->|"registers with"| Registry
    NSFW -->|"registers with"| Registry
    Hal -->|"registers with"| Registry
    PI -->|"registers with"| Registry
    OT -->|"registers with"| Registry
    Custom -->|"registers with"| Registry
    
    Registry -->|"contains"| Metadata
    
    Runtime["run_guardrails<br/>(Execution Engine)"] -->|"queries"| Registry
    Config["guardrails_config.json"] -->|"references spec_id"| Registry
```

### Registry Discovery Flow

When the runtime engine executes guardrails, it:

1. Reads `spec_id` from configuration (e.g., `"Moderation"`, `"Jailbreak"`)
2. Queries `default_spec_registry` to retrieve `GuardrailSpecMetadata`
3. Instantiates the guardrail check function using metadata
4. Executes the check with appropriate context based on metadata (e.g., conversation history for conversation-aware checks)

**Sources:** [README.md:149-154](), Diagram 4 from high-level architecture

---

## Pipeline Stage Integration

Guardrails execute at different stages of the LLM interaction pipeline. The stage determines when the check runs and what data it has access to.

```mermaid
graph LR
    subgraph "Stage 1: Pre-flight"
        PF["Pre-flight Guardrails<br/>- Contains PII (masking mode)<br/>- URL Filter (validation)<br/>- Input transformation"]
    end
    
    subgraph "Stage 2: Input Validation"
        Input["Input Guardrails<br/>- Moderation<br/>- Jailbreak<br/>- Prompt Injection<br/>- Off Topic Prompts<br/>Run concurrently with LLM"]
        LLM["LLM API Call"]
    end
    
    subgraph "Stage 3: Output Validation"
        Output["Output Guardrails<br/>- NSFW Text<br/>- Hallucination Detection<br/>- Moderation<br/>Check LLM response"]
    end
    
    subgraph "Agent Mode: Tool Level"
        ToolIn["Tool Input Guardrails<br/>Before tool execution"]
        ToolOut["Tool Output Guardrails<br/>After tool execution"]
    end
    
    UserInput["User Input"] --> PF
    PF -->|"Modified input"| Input
    PF -->|"Modified input"| LLM
    Input -.parallel.-> LLM
    LLM --> Output
    
    LLM -.agent mode.-> ToolIn
    ToolIn --> ToolExec["Tool Execution"]
    ToolExec --> ToolOut
    
    PF -.tripwire.-> Block["Execution Blocked<br/>GuardrailTripwireTriggered"]
    Input -.tripwire.-> Block
    Output -.tripwire.-> Block
    ToolIn -.tripwire.-> Block
    ToolOut -.tripwire.-> Block
```

### Stage Characteristics

- **Pre-flight**: Transforms input before LLM processing (e.g., PII masking). Can modify the input that reaches the LLM.
- **Input**: Validates user input concurrently with LLM call to minimize latency. Cannot modify input.
- **Output**: Validates LLM responses before returning to user. Runs after LLM completes.
- **Tool-level** (Agents only): Validates tool inputs and outputs during agent execution.

**Sources:** Diagram 2 from high-level architecture, [README.md:66-94]()

---

## LLM-Based Guardrail Infrastructure

All LLM-based guardrails share common infrastructure provided by the `llm_base` module. This module provides factory functions, configuration schemas, and standardized interfaces for LLM-powered checks.

```mermaid
graph TB
    subgraph "llm_base Module"
        Factory["create_llm_check_fn<br/>(Factory Function)"]
        RunLLM["run_llm<br/>(LLM Execution)"]
        LLMConfig["LLMConfig<br/>- system_prompt: str<br/>- model: str<br/>- temperature: float"]
        LLMOutput["LLMOutput<br/>- result: bool<br/>- explanation: str<br/>- confidence: float<br/>- token_usage: TokenUsage"]
    end
    
    subgraph "Context Propagation"
        Context["GuardrailLLMContextProto<br/>- guardrail_llm: OpenAI client<br/>- conversation_history<br/>- get_conversation_history()"]
        CVars["ContextVars<br/>Thread-safe state management"]
    end
    
    subgraph "Result Handling"
        GRResult["GuardrailResult<br/>- tripwire_triggered: bool<br/>- info: dict<br/>- token_usage: TokenUsage"]
    end
    
    JBCheck["Jailbreak Check"] -->|"uses"| Factory
    NSFWCheck["NSFW Text Check"] -->|"uses"| Factory
    HalCheck["Hallucination Check"] -->|"uses"| Factory
    PICheck["Prompt Injection Check"] -->|"uses"| Factory
    OTCheck["Off Topic Check"] -->|"uses"| Factory
    CustomCheck["Custom LLM Check"] -->|"uses"| Factory
    
    Factory -->|"creates check function"| CheckFn["CheckFn<br/>(Guardrail Function)"]
    CheckFn -->|"receives"| Context
    CheckFn -->|"calls"| RunLLM
    RunLLM -->|"uses"| LLMConfig
    RunLLM -->|"returns"| LLMOutput
    LLMOutput -->|"transformed to"| GRResult
    
    Context -->|"backed by"| CVars
```

### Key Components

**`create_llm_check_fn`**: Factory function that creates standardized guardrail check functions. Accepts:
- `system_prompt`: The prompt that defines the guardrail's behavior
- `model`: LLM model to use (defaults from configuration)
- `parse_fn`: Function to parse LLM response into structured output

**`GuardrailLLMContextProto`**: Context object passed to LLM-based guardrails providing:
- `guardrail_llm`: OpenAI client configured for guardrail checks
- `conversation_history`: List of previous messages for conversation-aware checks
- `get_conversation_history()`: Method to retrieve normalized conversation history

**`LLMOutput`**: Structured output from LLM guardrail checks containing:
- `result`: Boolean indicating if check passed/failed
- `explanation`: Human-readable explanation of the decision
- `confidence`: Confidence score (0.0-1.0)
- `token_usage`: Token consumption details

**Sources:** Diagram 4 from high-level architecture

---

## Conversation-Aware Guardrails

Several guardrails support multi-turn conversation analysis, enabling them to detect attacks that span multiple messages (e.g., gradual jailbreak attempts).

```mermaid
graph TB
    subgraph "Conversation-Aware Guardrails"
        JB["Jailbreak<br/>media_type: conversation<br/>Multi-turn attack detection"]
        PI["Prompt Injection<br/>media_type: conversation<br/>Cross-message context"]
        OT["Off Topic Prompts<br/>media_type: conversation<br/>Topic drift detection"]
    end
    
    subgraph "Context Management"
        Session["Session Object<br/>Conversation History"]
        CVars["ContextVars<br/>_agent_session<br/>_agent_conversation"]
        Context["GuardrailLLMContextProto<br/>get_conversation_history()"]
    end
    
    subgraph "Non-Conversation-Aware"
        NSFW["NSFW Text<br/>media_type: text<br/>Single message analysis"]
        Hal["Hallucination Detection<br/>media_type: text<br/>Output-only validation"]
    end
    
    Client["GuardrailsOpenAI<br/>or GuardrailAgent"] -->|"stores in"| Session
    Session -->|"persisted via"| CVars
    CVars -->|"provides to"| Context
    
    Context -->|"full history"| JB
    Context -->|"full history"| PI
    Context -->|"full history"| OT
    
    Context -->|"current text only"| NSFW
    Context -->|"current text only"| Hal
```

### Conversation History Format

Conversation-aware guardrails receive history in normalized format:
```json
[
  {"role": "user", "content": "First message"},
  {"role": "assistant", "content": "First response"},
  {"role": "user", "content": "Current message"}
]
```

The `GuardrailLLMContextProto.get_conversation_history()` method provides this normalized format regardless of whether the client is using chat completions, responses API, or agents SDK.

**Sources:** Diagram 6 from high-level architecture, [README.md:66-94]()

---

## API-Based Guardrail Details

### Moderation Guardrail

Uses OpenAI's Moderation API to check content across 13 predefined categories:

```mermaid
graph LR
    Input["User Input<br/>or LLM Output"] --> ModCheck["Moderation Check<br/>src/guardrails/checks/moderation.py"]
    ModCheck -->|"API call"| ModAPI["OpenAI Moderation API<br/>api.openai.com/v1/moderations"]
    ModAPI -->|"returns"| Categories["13 Categories<br/>- sexual<br/>- hate<br/>- harassment<br/>- self-harm<br/>- sexual/minors<br/>- hate/threatening<br/>- violence/graphic<br/>- self-harm/intent<br/>- self-harm/instructions<br/>- harassment/threatening<br/>- violence<br/>- illicit<br/>- illicit/violent"]
    Categories --> Result["GuardrailResult<br/>tripwire_triggered: bool<br/>info: {flagged_categories}"]
```

**Configuration**: Accepts category-specific thresholds and can be configured to trigger only on specific categories.

**See:** [Moderation Guardrail](#6.1) for detailed documentation.

### URL Filter Guardrail

Validates URLs against allowlists and blocklists:

```mermaid
graph LR
    Input["User Input"] --> URLCheck["URL Filter Check<br/>src/guardrails/checks/url_filter.py"]
    URLCheck -->|"extracts"| URLs["URL Extraction<br/>Regex pattern matching"]
    URLs --> Validate["Domain Validation"]
    
    Config["Configuration<br/>- allowlist: [domains]<br/>- blocklist: [domains]"] --> Validate
    
    Validate -->|"check against"| Lists["Allow/Block Lists<br/>Domain-level matching"]
    Lists --> Result["GuardrailResult<br/>tripwire: blocked URLs found<br/>info: {blocked_urls}"]
```

**Configuration**: Supports both domain-level and full URL matching with wildcard patterns.

**See:** [PII Detection and URL Filtering](#6.6) for detailed documentation.

### Contains PII Guardrail

Detects and optionally masks Personally Identifiable Information using Microsoft's Presidio framework:

```mermaid
graph LR
    Input["User Input"] --> PIICheck["Contains PII Check<br/>src/guardrails/checks/contains_pii.py"]
    PIICheck -->|"uses"| Presidio["Presidio Framework<br/>Open-source PII detection"]
    Presidio --> Entities["Entity Recognition<br/>- PERSON<br/>- EMAIL_ADDRESS<br/>- PHONE_NUMBER<br/>- CREDIT_CARD<br/>- SSN<br/>- etc."]
    
    Config["Configuration<br/>- entity_types: list<br/>- mask_mode: bool"] --> PIICheck
    
    Entities -->|"if mask_mode=false"| Detect["Detection Result<br/>tripwire_triggered: true/false"]
    Entities -->|"if mask_mode=true"| Mask["Masked Output<br/>Replace PII with [ENTITY_TYPE]<br/>Modified input flows to LLM"]
    
    Detect --> Result["GuardrailResult"]
    Mask --> Result
```

**Configuration**: 
- `entity_types`: List of PII entity types to detect
- `mask_mode`: If true, runs in pre_flight stage and masks detected PII

**See:** [PII Detection and URL Filtering](#6.6) for detailed documentation.

**Sources:** [README.md:183-195]()

---

## LLM-Based Guardrail Details

### Jailbreak Detection

Detects jailbreak attempts using a 7-technique taxonomy with multi-turn conversation analysis:

```mermaid
graph TB
    ConvHistory["Conversation History<br/>Multi-turn messages"] --> JBCheck["Jailbreak Check<br/>src/guardrails/checks/jailbreak.py"]
    
    JBCheck -->|"uses"| Taxonomy["7-Technique Taxonomy<br/>1. Role-playing<br/>2. Hypothetical scenarios<br/>3. Character simulation<br/>4. Translation/encoding<br/>5. Token manipulation<br/>6. Payload splitting<br/>7. Prompt injection"]
    
    Taxonomy -->|"analyzes via"| LLM["LLM Analysis<br/>System prompt with taxonomy<br/>Multi-turn reasoning"]
    
    Context["GuardrailLLMContextProto<br/>get_conversation_history()"] --> JBCheck
    
    LLM --> Output["LLMOutput<br/>- result: bool<br/>- technique_detected: str<br/>- confidence: float"]
    
    Output --> Result["GuardrailResult<br/>tripwire_triggered<br/>info: {technique, evidence}"]
```

**Conversation Awareness**: Analyzes full conversation history to detect gradual jailbreak attempts across multiple turns.

**See:** [Jailbreak Detection](#6.2) for detailed documentation and benchmarks.

### NSFW Text Detection

Detects workplace-inappropriate content in LLM outputs:

```mermaid
graph LR
    LLMOutput["LLM Response"] --> NSFWCheck["NSFW Text Check<br/>src/guardrails/checks/nsfw_text.py"]
    
    NSFWCheck -->|"uses"| LLM["LLM Analysis<br/>Workplace appropriateness<br/>System prompt"]
    
    LLM --> Output["LLMOutput<br/>- result: bool<br/>- content_type: str<br/>- explanation: str"]
    
    Output --> Result["GuardrailResult<br/>tripwire_triggered<br/>info: {content_type}"]
```

**Stage**: Output only - validates LLM responses for workplace appropriateness.

**See:** [NSFW Text Detection](#6.3) for detailed documentation.

### Hallucination Detection

Validates LLM responses against vector stores and file search tools:

```mermaid
graph TB
    LLMOutput["LLM Response"] --> HalCheck["Hallucination Detection<br/>src/guardrails/checks/hallucination.py"]
    
    Config["Configuration<br/>- knowledge_source<br/>- vector_store_id<br/>- file_search_tool"] --> HalCheck
    
    HalCheck -->|"queries"| VectorStore["Vector Store<br/>File Search Tool<br/>Ground truth data"]
    
    VectorStore --> Compare["Semantic Comparison<br/>Response vs. Source"]
    
    HalCheck -->|"uses"| LLM["LLM Validation<br/>Fact-checking against sources"]
    
    Compare --> LLM
    
    LLM --> Output["LLMOutput<br/>- result: bool<br/>- hallucination_detected: bool<br/>- evidence: str"]
    
    Output --> Result["GuardrailResult<br/>tripwire_triggered<br/>info: {evidence}"]
```

**Configuration**: Requires `knowledge_source` configuration pointing to vector store or file search tool.

**See:** [Hallucination Detection](#6.5) for detailed documentation.

### Prompt Injection Detection

Detects prompt injection attempts, particularly in tool call scenarios:

```mermaid
graph TB
    Input["User Input<br/>or Tool Call"] --> PICheck["Prompt Injection Check<br/>src/guardrails/checks/prompt_injection.py"]
    
    ConvHistory["Conversation History"] --> PICheck
    
    PICheck -->|"analyzes"| Intent["Intent Alignment<br/>User intent vs. action"]
    
    Intent -->|"uses"| LLM["LLM Analysis<br/>Injection pattern detection<br/>Tool call validation"]
    
    LLM --> Output["LLMOutput<br/>- result: bool<br/>- injection_detected: bool<br/>- technique: str<br/>- evidence: str"]
    
    Output --> Result["GuardrailResult<br/>tripwire_triggered<br/>info: {technique, evidence}"]
```

**Use Cases**:
- Validating tool calls in agent systems
- Detecting indirect prompt injection in retrieved content
- Ensuring alignment between user intent and executed actions

**See:** [Prompt Injection Detection](#6.4) for detailed documentation.

### Off Topic Prompts

Ensures user prompts stay within defined business scope:

```mermaid
graph TB
    Input["User Input"] --> OTCheck["Off Topic Check<br/>src/guardrails/checks/off_topic.py"]
    
    Config["Configuration<br/>- business_scope: str<br/>- allowed_topics: list"] --> OTCheck
    
    ConvHistory["Conversation History<br/>Topic drift tracking"] --> OTCheck
    
    OTCheck -->|"uses"| LLM["LLM Analysis<br/>Topic alignment check<br/>Scope validation"]
    
    LLM --> Output["LLMOutput<br/>- result: bool<br/>- off_topic: bool<br/>- detected_topic: str"]
    
    Output --> Result["GuardrailResult<br/>tripwire_triggered<br/>info: {detected_topic}"]
```

**Configuration**: Requires `business_scope` description or list of `allowed_topics`.

**See:** [Off-Topic Prompts and Custom Checks](#6.7) for detailed documentation.

### User-defined LLM (Custom Checks)

Extensible framework for custom LLM-based guardrails:

```mermaid
graph TB
    UserConfig["User Configuration<br/>- custom_system_prompt<br/>- model<br/>- temperature"] --> CustomCheck["User-defined LLM Check<br/>src/guardrails/checks/custom_llm.py"]
    
    CustomCheck -->|"uses"| Factory["create_llm_check_fn<br/>Factory from llm_base"]
    
    Factory -->|"creates"| CheckFn["Custom Check Function<br/>User-defined behavior"]
    
    Input["Input Data<br/>Text or Conversation"] --> CheckFn
    
    CheckFn -->|"calls"| LLM["LLM with Custom Prompt<br/>User-defined system prompt"]
    
    LLM --> Output["LLMOutput<br/>Custom response format"]
    
    Output --> Result["GuardrailResult<br/>User-defined semantics"]
```

**Use Cases**:
- Domain-specific content policies
- Custom safety requirements
- Organization-specific compliance checks

**See:** [Off-Topic Prompts and Custom Checks](#6.7) for detailed documentation.

**Sources:** [README.md:183-195](), Diagram 4 from high-level architecture

---

## Configuration and Execution Flow

Guardrails are configured via `guardrails_config.json` and executed by the runtime engine:

```mermaid
graph TB
    subgraph "Configuration"
        Portal["guardrails.openai.com<br/>Web Configuration UI"] --> ConfigJSON["guardrails_config.json<br/>Pipeline Definition"]
        ConfigJSON --> LoadConfig["load_config_bundle<br/>Configuration Loader"]
    end
    
    subgraph "Execution"
        LoadConfig --> Instantiate["instantiate_guardrails<br/>Create check functions"]
        Instantiate -->|"queries"| Registry["default_spec_registry<br/>Guardrail metadata"]
        Instantiate --> CheckFns["List of CheckFn<br/>Instantiated guardrails"]
        
        CheckFns --> Runtime["run_guardrails<br/>Execution Engine"]
        Runtime -->|"executes by stage"| PreFlight["Pre-flight Checks"]
        Runtime -->|"executes by stage"| Input["Input Checks"]
        Runtime -->|"executes by stage"| Output["Output Checks"]
    end
    
    subgraph "Results"
        PreFlight --> Results["GuardrailResults<br/>Aggregated results"]
        Input --> Results
        Output --> Results
        Results --> Response["GuardrailsResponse<br/>LLM response + results"]
    end
    
    Client["GuardrailsOpenAI<br/>or GuardrailAgent"] -->|"calls"| Runtime
```

### Configuration Schema Example

```json
{
  "pipeline": {
    "pre_flight": [
      {
        "spec_id": "Contains PII",
        "config": {
          "entity_types": ["PERSON", "EMAIL_ADDRESS"],
          "mask_mode": true
        }
      }
    ],
    "input": [
      {
        "spec_id": "Moderation",
        "config": {
          "categories": ["sexual", "violence"]
        }
      },
      {
        "spec_id": "Jailbreak",
        "config": {
          "model": "gpt-4o-mini"
        }
      }
    ],
    "output": [
      {
        "spec_id": "NSFW Text",
        "config": {}
      },
      {
        "spec_id": "Hallucination Detection",
        "config": {
          "knowledge_source": "vector_store_id"
        }
      }
    ]
  }
}
```

**Sources:** [README.md:36-64](), Diagram 2 from high-level architecture

---

## Guardrail Reference Table

Complete reference of all built-in guardrails with key characteristics:

| Guardrail | spec_id | Engine | Media Type | Stages | Conv. Aware | External Dependency |
|-----------|---------|--------|------------|--------|-------------|---------------------|
| Moderation | `"Moderation"` | API | text | input, output | No | OpenAI Moderation API |
| URL Filter | `"URL Filter"` | API | text | input, pre_flight | No | None |
| Contains PII | `"Contains PII"` | API | text | input, output, pre_flight | No | Presidio (optional) |
| Jailbreak | `"Jailbreak"` | LLM | conversation | input | Yes | None |
| NSFW Text | `"NSFW Text"` | LLM | text | output | No | None |
| Hallucination Detection | `"Hallucination Detection"` | LLM | text | output | No | Vector Store / File Search |
| Prompt Injection | `"Prompt Injection"` | LLM | conversation | input | Yes | None |
| Off Topic Prompts | `"Off Topic Prompts"` | LLM | conversation | input | Yes | None |
| User-defined LLM | `"Custom"` | LLM | text / conversation | input, output | Configurable | None |

### Field Descriptions

- **spec_id**: Identifier used in `guardrails_config.json` to reference the guardrail
- **Engine**: Execution engine type (`API` or `LLM`)
- **Media Type**: Input format (`text` for single messages, `conversation` for multi-turn)
- **Stages**: Pipeline stages where guardrail can execute
- **Conv. Aware**: Whether guardrail analyzes full conversation history
- **External Dependency**: Third-party services or tools required

**Sources:** [README.md:183-195](), Diagram 4 from high-level architecture

---

## Token Usage and Performance

All guardrails track token consumption and return it in `GuardrailResult`:

```typescript
interface GuardrailResult {
  tripwire_triggered: boolean;
  info: Record<string, any>;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
```

### Performance Characteristics

- **API-Based Guardrails**: Typical latency 100-500ms, deterministic results
- **LLM-Based Guardrails**: Latency varies by model:
  - `gpt-4o-mini`: 500-1500ms (P50: ~800ms)
  - `gpt-4o`: 1000-3000ms (P50: ~1800ms)
- **Conversation-Aware Guardrails**: Additional latency proportional to conversation length

For detailed performance benchmarks including ROC AUC metrics, latency percentiles, and model comparisons, see [Performance Benchmarks](#6.10).

**Sources:** Diagram 6 from high-level architecture

---

## Next Steps

For detailed information about each guardrail:

- [Moderation Guardrail](#6.1) - OpenAI Moderation API integration
- [Jailbreak Detection](#6.2) - Multi-turn attack detection with taxonomy
- [NSFW Text Detection](#6.3) - Workplace content filtering
- [Prompt Injection Detection](#6.4) - Tool call validation and intent alignment
- [Hallucination Detection](#6.5) - Vector store validation
- [PII Detection and URL Filtering](#6.6) - Presidio integration and domain filtering
- [Off-Topic Prompts and Custom Checks](#6.7) - Business scope validation and extensibility
- [LLM-Based Guardrail Framework](#6.8) - Creating custom guardrails
- [Guardrail Configuration Reference](#6.9) - Complete configuration options
- [Performance Benchmarks](#6.10) - ROC AUC, latency, and model comparisons

For information about integrating guardrails into your application:

- [Client Integration](#4) - Using guardrails with OpenAI clients
- [Agent Integration](#5) - Using guardrails with Agents SDK
- [Runtime Execution Model](#3.5) - How guardrails are executed

**Sources:** [README.md:1-205]()

---

