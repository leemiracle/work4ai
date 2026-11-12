<!-- source: DeepWiki mcp.deepwiki.com · repo alibaba/page-agent · page 8 Configuration and Customization · fetched 2026-10-29 -->

# Configuration and Customization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/core/src/types.ts](packages/core/src/types.ts)
- [packages/llms/src/types.ts](packages/llms/src/types.ts)
- [packages/ui/src/panel/Panel.ts](packages/ui/src/panel/Panel.ts)
- [packages/ui/src/panel/types.ts](packages/ui/src/panel/types.ts)

</details>



PageAgent provides a comprehensive configuration system that controls agent behavior, LLM integration, DOM processing, and execution lifecycle. All configuration is passed to the `PageAgent` or `PageAgentCore` constructor as a single object.

This page documents all available configuration options across the three main domains: Agent Configuration, LLM Configuration, and PageController Configuration.

---

## Configuration Architecture

The configuration system consists of several primary interfaces. The high-level `AgentConfig` (used by `PageAgentCore`) combines agent logic and LLM settings. Internally, this is decomposed into specialized configurations for each subsystem.

**Configuration Structure Diagram**

```mermaid
graph TB
    subgraph "Input_Space"
        ["AgentConfig"]
    end
    
    subgraph "Core_Configuration_Interfaces"
        ["LLMConfig"]
        ["PageControllerConfig"]
    end
    
    subgraph "Code_Entity_Space"
        ["PageAgentCore"]
        ["LLM_Class"]
        ["PageController"]
        ["Panel"]
    end
    
    ["AgentConfig"] -- "extends" --> ["LLMConfig"]
    ["AgentConfig"] --> ["PageAgentCore"]
    ["LLMConfig"] --> ["LLM_Class"]
    ["PageControllerConfig"] --> ["PageController"]
    
    ["PageAgentCore"] -- "instantiates" --> ["LLM_Class"]
    ["PageAgentCore"] -- "uses" --> ["PageController"]
    ["Panel"] -- "adapts" --> ["PageAgentCore"]
```

**Sources:** [packages/core/src/types.ts:10](), [packages/core/src/PageAgentCore.ts:108-115](), [packages/ui/src/panel/Panel.ts:30-41](), [packages/llms/src/types.ts:90]()

The `PageAgentCoreConfig` type is the internal representation used by the core engine, requiring an instantiated `PageController`:

```typescript
export type PageAgentCoreConfig = AgentConfig & { pageController: PageController }
```

**Sources:** [packages/core/src/PageAgentCore.ts:29]()

---

## LLM Configuration (Section 8.2)

The LLM configuration controls how PageAgent connects to and invokes Large Language Models. All LLM configuration extends from the `LLMConfig` interface.

**LLM Configuration Mapping**

```mermaid
graph LR
    subgraph "Natural_Language_Config"
        ["Model_Name"]
        ["Endpoint_URL"]
        ["Auth_Key"]
        ["Retry_Limit"]
        ["Custom_Fetch"]
    end
    
    subgraph "Code_Entity_Space"
        ["LLMConfig.model"]
        ["LLMConfig.baseURL"]
        ["LLMConfig.apiKey"]
        ["LLMConfig.maxRetries"]
        ["LLMConfig.customFetch"]
        ["LLM_Class"]
    end
    
    ["Model_Name"] --> ["LLMConfig.model"]
    ["Endpoint_URL"] --> ["LLMConfig.baseURL"]
    ["Auth_Key"] --> ["LLMConfig.apiKey"]
    ["Retry_Limit"] --> ["LLMConfig.maxRetries"]
    ["Custom_Fetch"] --> ["LLMConfig.customFetch"]
    
    ["LLMConfig.model"] --> ["LLM_Class"]
    ["LLMConfig.baseURL"] --> ["LLM_Class"]
```

**Sources:** [packages/llms/src/types.ts:90-125](), [packages/core/src/types.ts:10](), [packages/core/src/PageAgentCore.ts:113]()

### Core LLM Parameters

| Parameter | Type | Required | Purpose |
|-----------|------|----------|---------|
| `model` | `string` | Yes | Model identifier (e.g., `gpt-4o`, `qwen-plus`) |
| `baseURL` | `string` | Yes | API endpoint URL |
| `apiKey` | `string` | No | Authentication key |
| `maxRetries` | `number` | No | Retries on transient errors |
| `customFetch` | `function` | No | Custom fetch implementation for proxying or custom auth headers [packages/llms/src/types.ts:120-124]() |
| `transformRequestBody` | `function` | No | Tweak request body for specific provider requirements [packages/llms/src/types.ts:104-111]() |

For details, see [LLM Configuration](#8.2).

---

## Agent Configuration (Section 8.1)

The `AgentConfig` interface controls agent behavior, task execution limits, and custom tool registration.

**Agent Behavior Diagram**

```mermaid
graph TB
    subgraph "AgentConfig_Properties"
        ["language"]
        ["maxSteps"]
        ["customTools"]
        ["stepDelay"]
    end
    
    subgraph "Internal_Code_Entities"
        ["PageAgentCore.tools"]
        ["PageAgentCore.execute"]
        ["PageAgentCore.history"]
        ["AgentStatus"]
    end
    
    ["language"] --> ["PageAgentCore.execute"]
    ["maxSteps"] --> ["PageAgentCore.execute"]
    ["stepDelay"] --> ["PageAgentCore.execute"]
    ["customTools"] --> ["PageAgentCore.tools"]
    ["AgentStatus"] -- "tracks" --> ["PageAgentCore.execute"]
```

**Sources:** [packages/core/src/types.ts:10-161](), [packages/core/src/PageAgentCore.ts:111-147]()

### Core Agent Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `language` | `'en-US' \| 'zh-CN'` | `undefined` | Target language for UI and prompts [packages/core/src/types.ts:8-11]() |
| `maxSteps` | `number` | `40` | Maximum steps per task [packages/core/src/types.ts:17]() |
| `stepDelay` | `number` | `0.4` | Delay in seconds between agent steps [packages/core/src/types.ts:160]() |
| `customTools` | `Record` | `undefined` | Map of custom tool definitions or `null` to disable internal tools [packages/core/src/types.ts:49]() |
| `experimentalScriptExecutionTool` | `boolean` | `false` | Enable the `execute_javascript` tool [packages/core/src/types.ts:124]() |

For details, see [Agent Configuration](#8.1).

---

## PageController Configuration (Section 8.3)

The `PageControllerConfig` governs how the agent perceives and interacts with the web page DOM.

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `enableMask` | `boolean` | `true` | Show/hide the interactive simulator overlay |
| `viewportExpansion` | `number` | `0` | Pixels beyond viewport to include in DOM extraction |
| `interactiveBlacklist`| `string[]` | `[]` | CSS selectors to ignore as interactive |
| `interactiveWhitelist`| `string[]` | `[]` | CSS selectors to force as interactive |

For details, see [PageController Configuration](#8.3).

**Sources:** [packages/core/src/PageAgentCore.ts:115]()

---

## Custom Instructions (Section 8.5)

PageAgent supports multi-layered instructions to guide agent reasoning and behavior.

- **System Instructions**: Global rules defined in `instructions.system` [packages/core/src/types.ts:54-58]() or via `customSystemPrompt` [packages/core/src/types.ts:154]().
- **Page Instructions**: Dynamic callback `getPageInstructions(url)` to provide context based on the current URL [packages/core/src/types.ts:61-66]().
- **llms.txt**: `experimentalLlmsTxt` flag to automatically fetch site-specific guidance from the site origin [packages/core/src/types.ts:127-132]().

For details, see [Custom Instructions](#8.5).

---

## Lifecycle Hooks (Section 8.4)

Hooks allow developers to intercept agent execution at key points for logging, analytics, or custom side effects.

- `onBeforeTask` / `onAfterTask`: Triggered at the start and end of a task execution [packages/core/src/types.ts:93-105]().
- `onBeforeStep` / `onAfterStep`: Triggered before and after each agent step [packages/core/src/types.ts:77-90]().
- `onDispose`: Triggered when the agent instance is destroyed [packages/core/src/types.ts:108-114]().

For details, see [Lifecycle Hooks](#8.4).

**Sources:** [packages/core/src/PageAgentCore.ts:210-310]()

---

## Data Transformation and Masking (Section 8.6)

The `transformPageContent` hook is a powerful tool for privacy and token optimization. It allows you to process the simplified DOM string after extraction but before it is sent to the LLM [packages/core/src/types.ts:135-148]().

```typescript
const agent = new PageAgent({
  transformPageContent: async (content) => {
    // Mask sensitive phone numbers before sending to LLM
    return content.replace(/1[3-9]\d{9}/g, '***********');
  }
})
```

**Sources:** [packages/core/src/types.ts:143-148]()

For details, see [Data Masking and Content Transformation](#8.6).

---

