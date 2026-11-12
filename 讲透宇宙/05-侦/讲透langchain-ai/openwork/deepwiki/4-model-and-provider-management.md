<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/openwork · page 4 Model and Provider Management · fetched 2026-10-26 -->

# Model and Provider Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/main/ipc/models.ts](src/main/ipc/models.ts)
- [src/main/types.ts](src/main/types.ts)
- [src/renderer/src/components/chat/ModelSwitcher.tsx](src/renderer/src/components/chat/ModelSwitcher.tsx)
- [src/renderer/src/types.ts](src/renderer/src/types.ts)

</details>



This document covers the system responsible for configuring, storing, and accessing AI language models and their associated providers within OpenWork. The Model and Provider Management system handles three primary concerns: (1) defining the catalog of available models, (2) securely storing and retrieving API credentials, and (3) exposing model selection interfaces to both the UI and agent runtime.

For information about how selected models are instantiated and used during agent execution, see [Agent Runtime and Initialization](#3.1). For workspace-related configuration, see [Workspace Selection and Management](#5.1).

---

## System Architecture

The Model and Provider Management system follows a three-tier architecture: storage (`.env` file and `electron-store`), IPC API layer (handlers in main process), and UI components (renderer process). The storage tier maintains both static model definitions and dynamic runtime state, while the IPC layer enforces separation between renderer and main process privileges.

```mermaid
graph TB
    subgraph "Renderer Process"
        ModelSwitcher["ModelSwitcher Component<br/>(ModelSwitcher.tsx)"]
        ApiKeyDialog["ApiKeyDialog Component"]
        Store["useAppStore<br/>models: ModelConfig[]<br/>providers: Provider[]<br/>currentModel: string"]
    end
    
    subgraph "Main Process IPC Layer"
        ListModels["models:list handler<br/>(models.ts:194-200)"]
        GetDefault["models:getDefault handler<br/>(models.ts:203-205)"]
        SetDefault["models:setDefault handler<br/>(models.ts:208-210)"]
        SetApiKey["models:setApiKey handler<br/>(models.ts:213-218)"]
        GetApiKey["models:getApiKey handler<br/>(models.ts:221-223)"]
        ListProviders["models:listProviders handler<br/>(models.ts:231-236)"]
    end
    
    subgraph "Storage Layer"
        AVAILABLE_MODELS["AVAILABLE_MODELS<br/>Static array (models.ts:23-190)<br/>~23 model definitions"]
        PROVIDERS["PROVIDERS<br/>Static array (models.ts:16-20)<br/>3 providers"]
        EnvFile["~/.openwork/.env<br/>ANTHROPIC_API_KEY<br/>OPENAI_API_KEY<br/>GOOGLE_API_KEY"]
        ElectronStore["electron-store<br/>settings.json<br/>defaultModel"]
    end
    
    subgraph "Storage Module Functions"
        GetApiKeyFn["getApiKey(provider)<br/>(storage.ts:65-75)"]
        SetApiKeyFn["setApiKey(provider, key)<br/>(storage.ts:77-87)"]
        HasApiKeyFn["hasApiKey(provider)<br/>(storage.ts:101-103)"]
    end
    
    subgraph "Agent Runtime"
        GetDefaultModelFn["getDefaultModel()<br/>(models.ts:509-511)"]
        AgentRuntime["createAgentRuntime<br/>Instantiates model client"]
    end
    
    ModelSwitcher --> Store
    ApiKeyDialog --> Store
    
    Store -->|"window.api.models.list()"| ListModels
    Store -->|"window.api.models.setDefault()"| SetDefault
    Store -->|"window.api.models.setApiKey()"| SetApiKey
    Store -->|"window.api.models.getApiKey()"| GetApiKey
    Store -->|"window.api.models.listProviders()"| ListProviders
    
    ListModels --> AVAILABLE_MODELS
    ListModels --> HasApiKeyFn
    GetDefault --> ElectronStore
    SetDefault --> ElectronStore
    SetApiKey --> SetApiKeyFn
    GetApiKey --> GetApiKeyFn
    ListProviders --> PROVIDERS
    ListProviders --> HasApiKeyFn
    
    SetApiKeyFn --> EnvFile
    GetApiKeyFn --> EnvFile
    HasApiKeyFn --> GetApiKeyFn
    
    AgentRuntime --> GetDefaultModelFn
    AgentRuntime --> GetApiKeyFn
    GetDefaultModelFn --> ElectronStore
```

**Sources:** [src/main/ipc/models.ts:1-512](), [src/main/storage.ts:1-104](), [src/renderer/src/components/chat/ModelSwitcher.tsx:1-246]()

---

## Provider Configuration

Providers represent the AI API vendors that supply language models. The system defines three supported providers in the `PROVIDERS` constant, each with an identifier used throughout the codebase.

### Provider Data Structure

The `Provider` type includes runtime API key status:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `ProviderId` | One of: `'anthropic'`, `'openai'`, `'google'`, `'ollama'` |
| `name` | `string` | Human-readable display name |
| `hasApiKey` | `boolean` | Whether an API key is configured (computed at runtime) |

**Sources:** [src/main/types.ts:27-34](), [src/renderer/src/types.ts:27-33]()

### Provider Definitions

The static provider list is defined at [src/main/ipc/models.ts:16-20]():

```typescript
const PROVIDERS: Omit<Provider, 'hasApiKey'>[] = [
  { id: 'anthropic', name: 'Anthropic' },
  { id: 'openai', name: 'OpenAI' },
  { id: 'google', name: 'Google' }
]
```

The `models:listProviders` IPC handler augments this static list with dynamic API key status by calling `hasApiKey(provider.id)` for each provider [src/main/ipc/models.ts:231-236]().

**Sources:** [src/main/ipc/models.ts:16-20](), [src/main/ipc/models.ts:231-236]()

---

## Model Catalog

The model catalog is a hardcoded array of model configurations that defines all models available in OpenWork. Each entry contains metadata about the model and its provider association.

### ModelConfig Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier used in code (e.g., `'claude-sonnet-4-5-20250929'`) |
| `name` | `string` | Display name (e.g., `'Claude Sonnet 4.5'`) |
| `provider` | `ProviderId` | Provider identifier (`'anthropic'`, `'openai'`, `'google'`) |
| `model` | `string` | API model identifier passed to the provider's SDK |
| `description` | `string?` | Optional description shown in UI |
| `available` | `boolean` | Computed availability based on API key presence |

**Sources:** [src/main/types.ts:36-44](), [src/renderer/src/types.ts:35-42]()

### AVAILABLE_MODELS Array

The `AVAILABLE_MODELS` constant contains 23 model definitions spanning three model generations (as of January 2026):

```mermaid
graph LR
    subgraph "Anthropic Models"
        Claude45["Claude 4.5 Series<br/>opus-4-5, sonnet-4-5, haiku-4-5"]
        Claude41["Claude 4.1 Series<br/>opus-4-1, sonnet-4"]
    end
    
    subgraph "OpenAI Models"
        GPT5["GPT-5 Series<br/>gpt-5.2, gpt-5.1"]
        O_Series["o-Series Reasoning<br/>o3, o3-mini, o4-mini, o1"]
        GPT4["GPT-4 Series<br/>gpt-4.1, gpt-4.1-mini,<br/>gpt-4.1-nano, gpt-4o, gpt-4o-mini"]
    end
    
    subgraph "Google Models"
        Gemini3["Gemini 3<br/>gemini-3-pro-preview"]
        Gemini25["Gemini 2.5<br/>pro, flash, flash-lite"]
    end
```

The default model is `'claude-sonnet-4-5-20250929'`, chosen for its balance of intelligence, speed, and cost for agent workloads [src/main/ipc/models.ts:204]().

**Example model definition** [src/main/ipc/models.ts:34-40]():

```typescript
{
  id: 'claude-sonnet-4-5-20250929',
  name: 'Claude Sonnet 4.5',
  provider: 'anthropic',
  model: 'claude-sonnet-4-5-20250929',
  description: 'Best balance of intelligence, speed, and cost for agents',
  available: true
}
```

**Sources:** [src/main/ipc/models.ts:23-190]()

---

## API Key Storage and Security

API keys are stored in a dedicated `.env` file located at `~/.openwork/.env`, separate from application configuration to facilitate security practices like `.gitignore` exclusion.

### Storage Module

The `storage.ts` module provides key management functions:

```mermaid
graph TB
    EnvFile["~/.openwork/.env<br/>Plain text key=value format"]
    
    subgraph "storage.ts Functions"
        GetApiKey["getApiKey(provider)<br/>Returns: string | undefined"]
        SetApiKey["setApiKey(provider, apiKey)<br/>Writes to file + process.env"]
        DeleteApiKey["deleteApiKey(provider)<br/>Removes from file + process.env"]
        HasApiKey["hasApiKey(provider)<br/>Returns: boolean"]
    end
    
    subgraph "Environment Variable Mapping"
        EnvVarNames["ENV_VAR_NAMES<br/>anthropic → ANTHROPIC_API_KEY<br/>openai → OPENAI_API_KEY<br/>google → GOOGLE_API_KEY"]
    end
    
    GetApiKey --> EnvVarNames
    GetApiKey --> EnvFile
    GetApiKey -->|"Fallback"| ProcessEnv["process.env"]
    
    SetApiKey --> EnvVarNames
    SetApiKey --> EnvFile
    SetApiKey --> ProcessEnv
    
    DeleteApiKey --> EnvVarNames
    DeleteApiKey --> EnvFile
    DeleteApiKey --> ProcessEnv
    
    HasApiKey --> GetApiKey
```

**Sources:** [src/main/storage.ts:1-104]()

### Key Management Functions

**`getApiKey(provider: string): string | undefined`** [src/main/storage.ts:65-75]()

Retrieves an API key for a provider. First checks the `.env` file via `parseEnvFile()`, then falls back to `process.env`. This allows keys to be provided either through the OpenWork UI or via system environment variables.

**`setApiKey(provider: string, apiKey: string): void`** [src/main/storage.ts:77-87]()

Persists an API key by:
1. Parsing existing `.env` file content
2. Updating the key in the parsed object
3. Writing back to `.env` file via `writeEnvFile()`
4. Setting `process.env[envVarName]` for immediate availability

**`deleteApiKey(provider: string): void`** [src/main/storage.ts:89-99]()

Removes a key from both the `.env` file and `process.env`.

**`hasApiKey(provider: string): boolean`** [src/main/storage.ts:101-103]()

Returns `true` if `getApiKey(provider)` returns a non-empty value.

### Environment Variable Naming

The mapping from provider ID to environment variable name [src/main/storage.ts:9-13]():

| Provider ID | Environment Variable |
|-------------|---------------------|
| `anthropic` | `ANTHROPIC_API_KEY` |
| `openai` | `OPENAI_API_KEY` |
| `google` | `GOOGLE_API_KEY` |

**Sources:** [src/main/storage.ts:9-13](), [src/main/storage.ts:65-103]()

---

## IPC Handler API Reference

The main process exposes six IPC handlers for model and provider operations. All handlers are registered in `registerModelHandlers(ipcMain: IpcMain)` [src/main/ipc/models.ts:192-504]().

### models:list

**Handler:** [src/main/ipc/models.ts:194-200]()

**Request:** None

**Response:** `ModelConfig[]`

Returns the `AVAILABLE_MODELS` array with each model's `available` field set based on whether its provider has an API key configured. Calls `hasApiKey(model.provider)` for each model.

### models:getDefault

**Handler:** [src/main/ipc/models.ts:203-205]()

**Request:** None

**Response:** `string`

Returns the currently selected default model ID from `electron-store`. Defaults to `'claude-sonnet-4-5-20250929'` if not set.

### models:setDefault

**Handler:** [src/main/ipc/models.ts:208-210]()

**Request:** `modelId: string`

**Response:** `void`

Persists the selected model ID to `electron-store` at key `'defaultModel'`.

### models:setApiKey

**Handler:** [src/main/ipc/models.ts:213-218]()

**Request:** `{ provider: string, apiKey: string }`

**Response:** `void`

Delegates to `setApiKey(provider, apiKey)` from the storage module, which writes to `~/.openwork/.env`.

### models:getApiKey

**Handler:** [src/main/ipc/models.ts:221-223]()

**Request:** `provider: string`

**Response:** `string | null`

Retrieves the API key for a provider via `getApiKey(provider)`, returning `null` if not found.

### models:listProviders

**Handler:** [src/main/ipc/models.ts:231-236]()

**Request:** None

**Response:** `Provider[]`

Returns the `PROVIDERS` array with each provider's `hasApiKey` field computed via `hasApiKey(provider.id)`.

**Sources:** [src/main/ipc/models.ts:192-236]()

---

## Model Selection Flow

The model selection flow involves the `ModelSwitcher` component coordinating with the Zustand store to update both local UI state and persisted settings.

```mermaid
sequenceDiagram
    participant User
    participant ModelSwitcher
    participant Store as "useAppStore"
    participant IPC as "IPC Handler"
    participant Storage as "electron-store"
    
    User->>ModelSwitcher: Click model switcher button
    ModelSwitcher->>ModelSwitcher: Set open=true, show popover
    
    Note over ModelSwitcher: User selects provider tab
    User->>ModelSwitcher: Click provider (e.g., "Anthropic")
    ModelSwitcher->>ModelSwitcher: setSelectedProviderId('anthropic')
    ModelSwitcher->>ModelSwitcher: Filter models by provider
    
    Note over ModelSwitcher: User selects model
    User->>ModelSwitcher: Click model (e.g., "claude-sonnet-4-5")
    ModelSwitcher->>Store: setCurrentModel('claude-sonnet-4-5-20250929')
    Store->>IPC: models:setDefault(modelId)
    IPC->>Storage: store.set('defaultModel', modelId)
    Storage-->>IPC: Success
    IPC-->>Store: Success
    Store->>Store: Update currentModel state
    Store-->>ModelSwitcher: State updated
    ModelSwitcher->>ModelSwitcher: Close popover
```

**Sources:** [src/renderer/src/components/chat/ModelSwitcher.tsx:49-245]()

### ModelSwitcher Component

The `ModelSwitcher` component [src/renderer/src/components/chat/ModelSwitcher.tsx:49-245]() presents a two-column popover interface:

1. **Left column:** Provider list with visual indicators
   - Provider icons (SVG components for Anthropic, OpenAI, Google)
   - Warning icon if `hasApiKey === false`
   - Selected provider highlighted with `bg-muted`

2. **Right column:** Model list filtered by selected provider
   - Displays model IDs in monospace font
   - Check icon next to currently selected model
   - "Configure API Key" button if no API key exists
   - "Edit API Key" link at bottom if API key exists

### State Management

The component uses several local state variables:

- `open`: Boolean controlling popover visibility
- `selectedProviderId`: Currently selected provider tab
- `apiKeyDialogOpen`: Boolean for API key dialog
- `apiKeyProvider`: Provider for which to configure API key

It also consumes Zustand store state:

- `models`: Array of `ModelConfig` objects
- `providers`: Array of `Provider` objects with `hasApiKey` status
- `currentModel`: String ID of selected model

**Sources:** [src/renderer/src/components/chat/ModelSwitcher.tsx:49-115]()

### Provider Icons

Provider icons are implemented as inline SVG components [src/renderer/src/components/chat/ModelSwitcher.tsx:11-40]():

```typescript
const PROVIDER_ICONS: Record<ProviderId, React.FC<{ className?: string }>> = {
  anthropic: AnthropicIcon,
  openai: OpenAIIcon,
  google: GoogleIcon,
  ollama: () => null
}
```

Each icon is a simple SVG path element with `currentColor` fill for theming.

**Sources:** [src/renderer/src/components/chat/ModelSwitcher.tsx:11-40]()

---

## Runtime Model Instantiation

When the agent runtime initializes, it retrieves the default model configuration and instantiates the appropriate LangChain chat model client.

```mermaid
graph TB
    InvokeAgent["User invokes agent<br/>(ChatContainer)"]
    
    CreateRuntime["createAgentRuntime()<br/>(agent.ts)"]
    
    GetDefaultModel["getDefaultModel()<br/>(models.ts:509-511)"]
    
    LookupModel["Find ModelConfig<br/>in AVAILABLE_MODELS"]
    
    GetApiKey["getApiKey(provider)<br/>(storage.ts:65-75)"]
    
    InstantiateModel["Instantiate model client"]
    
    subgraph "Model Client Types"
        ChatAnthropic["ChatAnthropic<br/>(langchain/anthropic)"]
        ChatOpenAI["ChatOpenAI<br/>(langchain/openai)"]
        ChatGoogle["ChatGoogleGenerativeAI<br/>(langchain/google-genai)"]
    end
    
    InvokeAgent --> CreateRuntime
    CreateRuntime --> GetDefaultModel
    GetDefaultModel --> LookupModel
    LookupModel --> GetApiKey
    GetApiKey --> InstantiateModel
    
    InstantiateModel --> ChatAnthropic
    InstantiateModel --> ChatOpenAI
    InstantiateModel --> ChatGoogle
    
    ChatAnthropic --> AgentStream["DeepAgent.stream()"]
    ChatOpenAI --> AgentStream
    ChatGoogle --> AgentStream
```

**Sources:** [src/main/ipc/models.ts:509-511](), [src/main/storage.ts:65-75]()

### getDefaultModel Function

The `getDefaultModel()` function [src/main/ipc/models.ts:509-511]() is exported for use by the agent runtime:

```typescript
export function getDefaultModel(): string {
  return store.get('defaultModel', 'claude-sonnet-4-5-20250929') as string
}
```

This function retrieves the persisted model ID from `electron-store`, with a hardcoded default fallback.

### Model Client Instantiation

The agent runtime determines which model client to instantiate based on the `provider` field of the selected model's `ModelConfig`. The API key retrieved via `getApiKey(provider)` is passed to the client constructor along with the `model` field specifying the exact model variant.

The three supported client types are:
- `ChatAnthropic` (from `@langchain/anthropic`)
- `ChatOpenAI` (from `@langchain/openai`)
- `ChatGoogleGenerativeAI` (from `@langchain/google-genai`)

**Sources:** [src/main/ipc/models.ts:509-511](), Inferred from model provider types

---

## API Key Configuration Dialog

The `ApiKeyDialog` component (referenced but not provided in source files) presents a modal for entering, viewing, and deleting API keys. It is triggered from the `ModelSwitcher` component when users click "Configure API Key" or "Edit API Key" [src/renderer/src/components/chat/ModelSwitcher.tsx:102-114]().

### Dialog Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant ModelSwitcher
    participant ApiKeyDialog
    participant IPC
    participant EnvFile as "~/.openwork/.env"
    
    User->>ModelSwitcher: Click "Configure API Key"
    ModelSwitcher->>ModelSwitcher: setApiKeyProvider(provider)
    ModelSwitcher->>ModelSwitcher: setApiKeyDialogOpen(true)
    ModelSwitcher->>ApiKeyDialog: Render with provider
    
    ApiKeyDialog->>IPC: models:getApiKey(provider)
    IPC->>EnvFile: Read existing key
    EnvFile-->>IPC: API key or null
    IPC-->>ApiKeyDialog: Display in masked input
    
    User->>ApiKeyDialog: Enter/modify API key
    User->>ApiKeyDialog: Click "Save"
    ApiKeyDialog->>IPC: models:setApiKey(provider, key)
    IPC->>EnvFile: Write to .env file
    EnvFile-->>IPC: Success
    IPC-->>ApiKeyDialog: Success
    
    ApiKeyDialog->>ApiKeyDialog: onOpenChange(false)
    ApiKeyDialog->>ModelSwitcher: Dialog closes
    ModelSwitcher->>ModelSwitcher: loadProviders() + loadModels()
    ModelSwitcher->>ModelSwitcher: Refresh UI with new availability
```

When the dialog closes, the `ModelSwitcher` refreshes both providers and models lists to reflect the new API key availability [src/renderer/src/components/chat/ModelSwitcher.tsx:107-114]().

**Sources:** [src/renderer/src/components/chat/ModelSwitcher.tsx:102-114](), [src/renderer/src/components/chat/ModelSwitcher.tsx:238-243]()

---

## Extending the Model Catalog

To add new models or providers, developers must modify the static configuration arrays in `src/main/ipc/models.ts`.

### Adding a New Model

1. Add a new `ModelConfig` object to the `AVAILABLE_MODELS` array [src/main/ipc/models.ts:23-190]()
2. Set `provider` to an existing `ProviderId` or add a new provider first
3. Set `model` to the exact string expected by the provider's API
4. Set `available: true` (availability is recomputed based on API keys)

### Adding a New Provider

1. Add the provider ID to the `ProviderId` union type in type definitions [src/main/types.ts:28]()
2. Add a new provider object to the `PROVIDERS` array [src/main/ipc/models.ts:16-20]()
3. Add environment variable mapping in `ENV_VAR_NAMES` [src/main/storage.ts:9-13]()
4. Add an icon component in `ModelSwitcher.tsx` [src/renderer/src/components/chat/ModelSwitcher.tsx:35-40]()
5. Update agent runtime to handle new client type (implementation-specific)

**Sources:** [src/main/ipc/models.ts:16-20](), [src/main/ipc/models.ts:23-190](), [src/main/storage.ts:9-13](), [src/main/types.ts:28]()

---

## Security Considerations

### Credential Isolation

API keys are stored in `~/.openwork/.env` rather than `electron-store`'s `settings.json` to facilitate security practices:

1. The `.env` file can be excluded from backups
2. File permissions can be restricted (e.g., `chmod 600`)
3. The file location is consistent with common development practices

### Process Environment Fallback

The `getApiKey()` function falls back to `process.env` [src/main/storage.ts:74](), allowing users to provide credentials via system environment variables instead of storing them in the `.env` file. This supports scenarios where credential management is handled externally (e.g., enterprise secrets management).

### Renderer Process Isolation

API keys are never exposed to the renderer process. The `models:getApiKey` IPC handler returns the key only when explicitly requested (e.g., for display in the API key dialog), and model instantiation occurs entirely in the main process. The renderer only sees model availability booleans computed via `hasApiKey()`.

**Sources:** [src/main/storage.ts:65-75](), [src/main/ipc/models.ts:221-223]()

---

