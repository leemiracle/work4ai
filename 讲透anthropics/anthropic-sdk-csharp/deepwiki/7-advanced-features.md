<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/anthropic-sdk-csharp · page 7 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/MessagesExample/MessagesExample.csproj](examples/MessagesExample/MessagesExample.csproj)
- [examples/MessagesExample/Program.cs](examples/MessagesExample/Program.cs)
- [examples/MessagesStreamingExample/MessagesStreamingExample.csproj](examples/MessagesStreamingExample/MessagesStreamingExample.csproj)
- [examples/MessagesStreamingExample/Program.cs](examples/MessagesStreamingExample/Program.cs)
- [examples/ThinkingExample/Program.cs](examples/ThinkingExample/Program.cs)
- [examples/ThinkingExample/ThinkingExample.csproj](examples/ThinkingExample/ThinkingExample.csproj)
- [examples/ThinkingStreamingExample/Program.cs](examples/ThinkingStreamingExample/Program.cs)
- [examples/ThinkingStreamingExample/ThinkingStreamingExample.csproj](examples/ThinkingStreamingExample/ThinkingStreamingExample.csproj)
- [src/Anthropic.Tests/Models/Beta/BetaErrorTest.cs](src/Anthropic.Tests/Models/Beta/BetaErrorTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/Batches/BetaMessageBatchResultTest.cs](src/Anthropic.Tests/Models/Beta/Messages/Batches/BetaMessageBatchResultTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaBashCodeExecutionToolResultBlockParamTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaBashCodeExecutionToolResultBlockParamTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaBashCodeExecutionToolResultBlockTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaBashCodeExecutionToolResultBlockTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaCitationsDeltaTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaCitationsDeltaTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaClearToolUses20250919EditTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaClearToolUses20250919EditTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaCodeExecutionToolResultBlockContentTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaCodeExecutionToolResultBlockContentTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaCodeExecutionToolResultBlockParamContentTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaCodeExecutionToolResultBlockParamContentTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaContentBlockParamTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaContentBlockParamTest.cs)
- [src/Anthropic.Tests/Models/Beta/Messages/BetaContextManagementConfigTest.cs](src/Anthropic.Tests/Models/Beta/Messages/BetaContextManagementConfigTest.cs)

</details>



This page documents sophisticated SDK capabilities designed for advanced use cases including context management, extended thinking, container-based request reuse, and prompt caching. These features are primarily available through the Beta API and enable fine-grained control over Claude's behavior, memory management, and performance optimization.

For basic message creation and streaming, see [Working with Messages](#5). For tool integration, see [Tools and Function Calling](#6). For beta-specific APIs like Files and Skills, see [Beta Services](#4.4).

---

## Overview

The SDK exposes several advanced features that provide enhanced control over request processing:

| Feature | Purpose | API Surface | Beta Required |
|---------|---------|-------------|---------------|
| Context Management | Control how conversation history is cleared between turns | `BetaContextManagementConfig` | Yes |
| Extended Thinking | Enable Claude's reasoning process in responses | `BetaThinkingConfigParam` | Yes (some models) |
| Container System | Reuse request state across multiple API calls | `BetaContainerParams` | Yes |
| Cache Control | Reduce costs and latency via prompt caching | `CacheControl` with `TTL` | No |
| Output Configuration | Control response effort level | `BetaOutputConfig` | Yes |
| Service Tiers | Choose between priority and standard capacity | `ServiceTier` enum | No |

**Sources:**
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:1-577]()
- [src/Anthropic/Models/Beta/Messages/BetaContextManagementConfig.cs:1-350]()

---

## Context Management

Context management allows precise control over conversation history, enabling applications to clear tool uses, thinking content, or other elements when context windows grow large. This is essential for long-running conversations that would otherwise exceed token limits.

### Configuration Structure

```mermaid
graph TB
    subgraph "Request Configuration"
        MsgParams["MessageCreateParams"]
        CtxMgmt["ContextManagement<br/>(BetaContextManagementConfig)"]
    end
    
    subgraph "Edit Types"
        EditUnion["Edit Union"]
        ClearTools["BetaClearToolUses20250919Edit"]
        ClearThink["BetaClearThinking20251015Edit"]
    end
    
    subgraph "Trigger Conditions"
        TriggerUnion["Trigger Union"]
        InputTokens["BetaInputTokensTrigger"]
        ToolUses["BetaToolUsesTrigger"]
    end
    
    subgraph "Configuration Options"
        ClearAtLeast["ClearAtLeast<br/>(min tokens to clear)"]
        Keep["Keep<br/>(items to retain)"]
        ExcludeTools["ExcludeTools<br/>(preserve specific tools)"]
        ClearInputs["ClearToolInputs<br/>(bool or string list)"]
    end
    
    MsgParams -->|contains| CtxMgmt
    CtxMgmt -->|"Edits: List<Edit>"| EditUnion
    EditUnion -->|variant 1| ClearTools
    EditUnion -->|variant 2| ClearThink
    
    ClearTools -->|"Trigger?"| TriggerUnion
    TriggerUnion -->|input_tokens| InputTokens
    TriggerUnion -->|tool_uses| ToolUses
    
    ClearTools -->|optional config| ClearAtLeast
    ClearTools -->|optional config| Keep
    ClearTools -->|optional config| ExcludeTools
    ClearTools -->|optional config| ClearInputs
```

**Diagram: Context Management Configuration Hierarchy**

**Sources:**
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:132-148]()
- [src/Anthropic/Models/Beta/Messages/BetaContextManagementConfig.cs:10-77]()
- [src/Anthropic/Models/Beta/Messages/BetaClearToolUses20250919Edit.cs:1-649]()

### Clearing Tool Uses

The `BetaClearToolUses20250919Edit` edit type removes tool use history from conversation context. This helps manage token usage in tool-heavy workflows.

| Property | Type | Description |
|----------|------|-------------|
| `ClearAtLeast` | `BetaInputTokensClearAtLeast?` | Minimum tokens that must be cleared for edit to apply |
| `ClearToolInputs` | `ClearToolInputs?` | Boolean (clear all) or list of tool names (clear specific) |
| `ExcludeTools` | `IReadOnlyList<string>?` | Tool names to preserve from clearing |
| `Keep` | `BetaToolUsesKeep?` | Number of recent tool uses to retain |
| `Trigger` | `Trigger?` | Condition that activates clearing (input tokens or tool use count) |

The `ClearToolInputs` property uses a union type that accepts either:
- `bool` - Clear all tool inputs if `true`
- `IReadOnlyList<string>` - Specific tool input IDs to clear

The `Trigger` property determines when clearing occurs:
- `BetaInputTokensTrigger` - Triggers when input token count reaches threshold
- `BetaToolUsesTrigger` - Triggers when tool use count reaches threshold

**Sources:**
- [src/Anthropic/Models/Beta/Messages/BetaClearToolUses20250919Edit.cs:16-154]()
- [src/Anthropic/Models/Beta/Messages/BetaClearToolUses20250919Edit.cs:156-378]()
- [src/Anthropic/Models/Beta/Messages/BetaClearToolUses20250919Edit.cs:380-649]()

### Clearing Thinking Content

The `BetaClearThinking20251015Edit` edit type removes extended thinking blocks from conversation history, useful for managing context when using the thinking feature extensively.

```mermaid
graph LR
    Edit["BetaClearThinking20251015Edit"]
    Keep["Keep<br/>(BetaThinkingTurns)"]
    Type["type = 'clear_thinking_20251015'"]
    
    Edit -->|property| Keep
    Edit -->|constant| Type
```

**Diagram: Clear Thinking Edit Structure**

**Sources:**
- [src/Anthropic/Models/Beta/Messages/BetaContextManagementConfig.cs:196-199]()

### Response Tracking

After a request with context management, the response includes `BetaContextManagementResponse` showing which edits were applied:

```mermaid
graph TB
    Response["BetaContextManagementResponse"]
    AppliedEdits["AppliedEdits<br/>(List<AppliedEdit>)"]
    
    ClearToolsResp["BetaClearToolUses20250919EditResponse"]
    ClearThinkResp["BetaClearThinking20251015EditResponse"]
    
    Response -->|contains| AppliedEdits
    AppliedEdits -->|variant 1| ClearToolsResp
    AppliedEdits -->|variant 2| ClearThinkResp
    
    ClearToolsResp -->|"ClearedInputTokens: long"| TokenCount["Token count cleared"]
    ClearThinkResp -->|"ClearedInputTokens: long"| TokenCount2["Token count cleared"]
```

**Diagram: Context Management Response Structure**

**Sources:**
- [src/Anthropic/Models/Beta/Messages/BetaContextManagementResponse.cs:1-385]()

---

## Extended Thinking and Reasoning

Extended thinking enables Claude to show its reasoning process in `thinking` content blocks before providing a final answer. This feature is configured via the `Thinking` parameter in `MessageCreateParams`. For comprehensive details on thinking blocks, redacted thinking, and response processing, see [Thinking and Reasoning](#7.2).

### Configuration Structure

```mermaid
graph TB
    MsgParams["MessageCreateParams"]
    ThinkingProp["Thinking property<br/>(ThinkingConfigParam union)"]
    
    EnabledCfg["ThinkingConfigEnabled"]
    DisabledCfg["ThinkingConfigDisabled"]
    
    BudgetProp["BudgetTokens: long"]
    MinBudget["Minimum: 1024 tokens"]
    
    MsgParams -->|optional| ThinkingProp
    ThinkingProp -->|variant| EnabledCfg
    ThinkingProp -->|variant| DisabledCfg
    
    EnabledCfg -->|contains| BudgetProp
    BudgetProp -->|constraint| MinBudget
```

**Diagram: Thinking Configuration in MessageCreateParams**

### Basic Usage Example

The SDK includes example applications demonstrating thinking feature usage:

| Example | Purpose | Key Types |
|---------|---------|-----------|
| `ThinkingExample/Program.cs` | Non-streaming thinking responses | `ThinkingConfigEnabled`, `ThinkingBlock` |
| `ThinkingStreamingExample/Program.cs` | Streaming thinking deltas | `ThinkingConfigEnabled`, `ThinkingDelta` |

The thinking budget specifies how many tokens Claude can allocate to reasoning. This counts toward the overall `MaxTokens` limit. The minimum budget is 1024 tokens.

```csharp
// From ThinkingExample/Program.cs
Thinking = new ThinkingConfigEnabled() { BudgetTokens = 1024 }
```

Response content blocks include thinking via the `ThinkingBlock` type, which can be extracted using `TryPickThinking()`:

```csharp
// From ThinkingExample/Program.cs
if (block.TryPickThinking(out ThinkingBlock? thinking))
{
    Console.WriteLine($"Thinking: {thinking.Thinking}");
}
```

**Sources:**
- [examples/ThinkingExample/Program.cs:1-38]()
- [examples/ThinkingStreamingExample/Program.cs:1-36]()
- [src/Anthropic/Models/Messages/MessageCreateParams.cs:232-258]()

---

## Container System

Containers enable request state reuse across multiple API calls, improving efficiency for stateful interactions. The container system is integrated with the Skills API for maintaining execution context across conversation turns. For comprehensive container lifecycle management and expiration details, see [Container System](#7.3).

### Container Configuration Types

```mermaid
graph TB
    MsgParams["MessageCreateParams<br/>(Beta)"]
    ContainerUnion["Container property<br/>(union type)"]
    
    ContainerParams["BetaContainerParams"]
    ContainerID["string<br/>(existing container ID)"]
    
    IDProp["ID: string"]
    SkillsList["Skills: List&lt;BetaSkillParams&gt;"]
    
    SkillParams["BetaSkillParams"]
    SkillID["SkillID: string"]
    TypeProp["Type: BetaSkillParamsType"]
    VersionProp["Version: string"]
    
    MsgParams -->|optional| ContainerUnion
    ContainerUnion -->|"new container"| ContainerParams
    ContainerUnion -->|"reuse existing"| ContainerID
    
    ContainerParams -->|required| IDProp
    ContainerParams -->|optional| SkillsList
    
    SkillsList -->|contains| SkillParams
    SkillParams --> SkillID
    SkillParams --> TypeProp
    SkillParams --> VersionProp
```

**Diagram: Container Property Structure in MessageCreateParams**

### Container Response Fields

Responses include container metadata via the `BetaContainer` type:

| Property | Type | Description |
|----------|------|-------------|
| `ID` | `string` | Unique container identifier for reuse |
| `ExpiresAt` | `DateTimeOffset` | Container expiration timestamp |
| `Skills` | `List<BetaSkill>?` | Active skills in container |

Container IDs from responses can be passed to subsequent requests to maintain state.

**Sources:**
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:123-130]()
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:579-761]()
- [src/Anthropic.Tests/Models/Beta/Messages/Batches/BetaMessageBatchResultTest.cs:20-33]()

---

## Prompt Caching

Prompt caching reduces costs and latency by caching frequently reused content such as system prompts, tool definitions, and conversation context. Cache entries use configurable time-to-live (TTL) values. For detailed caching strategies and usage metrics, see [Cache Control](#7.4).

### Cache Control Types

```mermaid
graph TB
    CacheCtrl["CacheControlEphemeral /<br/>BetaCacheControlEphemeral"]
    TTLEnum["TTL enum"]
    
    TTL5m["TTL.TTL5m"]
    TTL1h["TTL.TTL1h"]
    
    TypeProp["Type: 'ephemeral'"]
    
    CacheCtrl -->|contains| TypeProp
    CacheCtrl -->|contains| TTLEnum
    
    TTLEnum -->|"5 minute cache"| TTL5m
    TTLEnum -->|"1 hour cache"| TTL1h
```

**Diagram: CacheControlEphemeral Structure**

### Cacheable Content Types

Cache control can be applied to multiple content types via their `CacheControl` property:

| Content Type | Example Class | Location |
|--------------|---------------|----------|
| System Prompts | `BetaTextBlockParam` | System prompt text blocks |
| Tool Definitions | `BetaTool`, `Tool` | Individual tool configurations |
| Message Content | `BetaContentBlockParam` | User/assistant message blocks |
| Tool Results | `BetaToolResultBlockParam` | Tool execution results |
| Search Results | `BetaSearchResultBlockParam` | Web search result blocks |

The `CacheControl` property is optional on all supported types, enabling selective caching at granular levels.

### Usage Metrics

Cache usage is reported in response `Usage` objects:

| Metric | Property | Description |
|--------|----------|-------------|
| Cache Creation | `CacheCreationInputTokens` | Tokens used to create cache entries |
| Cache Reads | `CacheReadInputTokens` | Tokens loaded from cache |
| TTL-Specific Creation | `CacheCreation.Ephemeral5mInputTokens` | Tokens cached with 5m TTL |
| TTL-Specific Creation | `CacheCreation.Ephemeral1hInputTokens` | Tokens cached with 1h TTL |

**Sources:**
- [src/Anthropic.Tests/Models/Beta/Messages/BetaContentBlockParamTest.cs:43-44]()
- [src/Anthropic.Tests/Models/Beta/Messages/BetaBashCodeExecutionToolResultBlockParamTest.cs:17-18]()
- [src/Anthropic.Tests/Models/Beta/Messages/Batches/BetaMessageBatchResultTest.cs:68-76]()

---

## Output Configuration

The `BetaOutputConfig` type controls Claude's response generation characteristics, particularly the computational effort applied to reasoning and response quality. This configuration is available in beta messages and batch processing requests.

### Configuration Structure

```mermaid
graph TB
    OutputConfig["BetaOutputConfig"]
    EffortProp["Effort property"]
    EffortEnum["Effort enum"]
    
    Low["Effort.Low"]
    Medium["Effort.Medium"]
    High["Effort.High"]
    
    OutputConfig -->|contains| EffortProp
    EffortProp -->|type| EffortEnum
    
    EffortEnum -->|value| Low
    EffortEnum -->|value| Medium
    EffortEnum -->|value| High
    
    MsgParams["MessageCreateParams<br/>(Beta)"]
    BatchParams["BatchCreateParams<br/>(Beta)"]
    CountParams["MessageCountTokensParams<br/>(Beta)"]
    
    MsgParams -->|"OutputConfig?"| OutputConfig
    BatchParams -->|"OutputConfig?"| OutputConfig
    CountParams -->|"OutputConfig?"| OutputConfig
```

**Diagram: BetaOutputConfig Usage Across Request Types**

### Effort Levels

The `Effort` enum controls computational resource allocation:

| Effort Level | Behavior |
|--------------|----------|
| `Effort.Low` | Faster responses, reduced reasoning depth |
| `Effort.Medium` | Balanced speed and reasoning quality |
| `Effort.High` | Maximum reasoning depth, longer processing time |

Higher effort levels may produce more thorough responses but consume additional tokens and processing time. The effort setting influences both thinking token usage and output token generation.

**Sources:**
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:190-209]()
- [src/Anthropic.Tests/Models/Beta/Messages/Batches/BatchCreateParamsTest.cs:61]()

---

## Service Tiers

Service tiers provide capacity management by allowing applications to select between priority processing (when available) and standard capacity. The `ServiceTier` enum is available in both standard and beta message requests.

### Configuration Usage

```mermaid
graph TB
    ServiceTierEnum["ServiceTier enum"]
    
    Auto["ServiceTier.Auto"]
    StandardOnly["ServiceTier.StandardOnly"]
    
    ServiceTierEnum -->|value| Auto
    ServiceTierEnum -->|value| StandardOnly
    
    MsgParams["MessageCreateParams"]
    BetaMsgParams["MessageCreateParams<br/>(Beta)"]
    BatchParams["BatchCreateParams"]
    
    MsgParams -->|"ServiceTier?"| ServiceTierEnum
    BetaMsgParams -->|"ServiceTier?"| ServiceTierEnum
    BatchParams -->|"ServiceTier?"| ServiceTierEnum
    
    Auto -.->|"priority available"| Priority["Priority capacity"]
    Auto -.->|"priority unavailable"| Standard["Standard capacity"]
    StandardOnly -.->|always| Standard
```

**Diagram: ServiceTier Usage in Request Types**

### Enum Values and Behavior

| Enum Value | JSON Wire Value | Description |
|------------|-----------------|-------------|
| `ServiceTier.Auto` | `"auto"` | Uses priority capacity if available; automatically falls back to standard capacity when priority is unavailable |
| `ServiceTier.StandardOnly` | `"standard_only"` | Exclusively uses standard capacity; never attempts priority capacity |

### Response Service Tier Reporting

Responses include the actual service tier used via the `Usage.ServiceTier` property:

- Standard API: `UsageServiceTier.Standard`
- Beta API: `BetaUsageServiceTier.Standard` or `BetaUsageServiceTier.Auto`

Priority capacity may offer reduced latency during high-demand periods. Standard capacity provides consistent availability with predictable pricing.

**Sources:**
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:226-251]()
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:812-855]()
- [src/Anthropic.Tests/Models/Beta/Messages/Batches/BetaMessageBatchResultTest.cs:77]()

---

## Beta Feature Activation

Advanced features often require beta API access, enabled via the `Betas` header. The SDK provides the `AnthropicBeta` enum for type-safe feature activation.

### Beta Header Configuration

```mermaid
graph TB
    MsgParams["MessageCreateParams"]
    BatchParams["BatchCreateParams"]
    
    BetasProperty["Betas: List&lt;AnthropicBeta&gt;"]
    
    BetaEnum["AnthropicBeta enum"]
    
    HTTPHeader["anthropic-beta<br/>HTTP header"]
    
    MsgParams -->|optional| BetasProperty
    BatchParams -->|optional| BetasProperty
    
    BetasProperty -->|contains| BetaEnum
    BetasProperty -->|"serialized to"| HTTPHeader
    
    BetaEnum -->|example| PromptCaching["PromptCaching_2024_07_31"]
    BetaEnum -->|example| MessageBatches["MessageBatches_2024_09_24"]
    BetaEnum -->|example| ContextMgmt["ContextManagement_2025_01_01"]
    BetaEnum -->|example| ComputerUse["ComputerUse_2025_01_10"]
```

**Diagram: Beta Feature Activation via Betas Property**

### Beta Feature Examples

The `AnthropicBeta` enum defines available beta features:

| Enum Value | Wire Format | Feature |
|------------|-------------|---------|
| `AnthropicBeta.PromptCaching_2024_07_31` | `"prompt-caching-2024-07-31"` | Prompt caching with TTL |
| `AnthropicBeta.MessageBatches_2024_09_24` | `"message-batches-2024-09-24"` | Batch message processing |
| `AnthropicBeta.ContextManagement_2025_01_01` | `"context-management-2025-01-01"` | Context editing and clearing |
| `AnthropicBeta.ComputerUse_2025_01_10` | `"computer-use-2025-01-10"` | Computer interaction tools |

Multiple beta features can be activated simultaneously. The SDK serializes the list as comma-separated values in the `anthropic-beta` HTTP header.

**Sources:**
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:484-505]()
- [src/Anthropic/Models/Beta/Messages/Batches/BatchCreateParams.cs:44-65]()

---

## Feature Compatibility Matrix

```mermaid
graph TB
    subgraph "Beta API Features"
        CtxMgmt["Context Management"]
        OutputCfg["Output Configuration"]
        Container["Container System"]
        ExtThinking["Extended Thinking<br/>(some models)"]
    end
    
    subgraph "Stable API Features"
        StdThinking["Basic Thinking"]
        CacheCtrl["Cache Control"]
        ServiceTiers["Service Tiers"]
    end
    
    subgraph "Shared Features"
        MCPServers["MCP Server Integration"]
        ToolDefs["Tool Definitions"]
        Metadata["Request Metadata"]
    end
    
    BetaParams["Beta MessageCreateParams"] -->|supports| CtxMgmt
    BetaParams -->|supports| OutputCfg
    BetaParams -->|supports| Container
    BetaParams -->|supports| ExtThinking
    
    StdParams["Standard MessageCreateParams"] -->|supports| StdThinking
    StdParams -->|supports| CacheCtrl
    StdParams -->|supports| ServiceTiers
    
    BetaParams -->|also supports| Shared["Shared Features"]
    StdParams -->|also supports| Shared
    
    Shared -->|includes| MCPServers
    Shared -->|includes| ToolDefs
    Shared -->|includes| Metadata
```

**Diagram: Feature Availability by API Version**

Both beta and standard APIs support core features like tools and metadata. Advanced features like context management and output configuration require the beta API, while features like cache control and service tiers are available in both.

**Sources:**
- [src/Anthropic/Models/Beta/Messages/MessageCreateParams.cs:1-577]()
- [src/Anthropic/Models/Messages/MessageCreateParams.cs:1-588]()

---

