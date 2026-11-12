<!-- source: DeepWiki mcp.deepwiki.com · repo decolua/9router · page 5 Provider System · fetched 2026-10-30 -->

# Provider System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [open-sse/config/constants.js](open-sse/config/constants.js)
- [open-sse/config/providerModels.js](open-sse/config/providerModels.js)
- [open-sse/config/providers.js](open-sse/config/providers.js)
- [open-sse/executors/index.js](open-sse/executors/index.js)
- [open-sse/services/model.js](open-sse/services/model.js)
- [src/app/api/providers/[id]/test/route.js](src/app/api/providers/[id]/test/route.js)
- [src/app/api/providers/validate/route.js](src/app/api/providers/validate/route.js)
- [src/shared/constants/config.js](src/shared/constants/config.js)
- [src/shared/constants/providers.js](src/shared/constants/providers.js)

</details>



The Provider System is 9Router's comprehensive infrastructure for managing AI provider integrations. It encompasses provider registration, configuration, execution, credential management, and validation. The system supports over 130 providers across multiple authentication types (OAuth, API Key, Free, Web Cookie) and handles all aspects of provider interaction from request building to token refresh.

This is a parent page providing a high-level overview. For deep technical details, refer to the child pages:
- **5.1 Provider Configuration** — Document provider registry, configuration schema, supported providers. See [Provider Configuration](#5.1).
- **5.2 Provider Models & Pricing** — `PROVIDER_MODELS` structure, pricing tables, catalog sync, cost calculation. See [Provider Models & Pricing](#5.2).
- **5.3 Provider Executors** — `BaseExecutor` pattern, request building, URL fallbacks, default executor, and specialized executors (Kiro, Antigravity, Gemini, Codex, Copilot, Cursor, etc.). See [Provider Executors](#5.3).
- **5.4 Token Refresh & Credential Management** — OAuth token lifecycle, background refresh, deduplication, project IDs, and credential storage. See [Token Refresh & Credential Management](#5.4).
- **5.5 Account Selection Strategies** — Round-robin, fill-first, sticky limits, selection mutex, and account rotation. See [Account Selection Strategies](#5.5).
- **5.6 Provider Validation & Testing** — Connection testing, API key validation via `POST /api/providers/validate`, model ping/test routing, and endpoint probing. See [Provider Validation & Testing](#5.6).
- **5.7 Provider Quotas & Usage Limits** — Per-provider quota fetchers and normalization/dispatch. See [Provider Quotas & Usage Limits](#5.7).

## System Architecture

The Provider System coordinates provider metadata, dynamic model lookups, credential resolution, and transport execution through specialized executor modules and registry constants.

Diagram: Provider System Architecture
```mermaid
graph TB
    subgraph "Request_Processing"
        A["handleChatCore"] --> B["getExecutor (open-sse/executors/index.js)"]
    end

    subgraph "Provider_Registry"
        C["REGISTRY (open-sse/providers/registry/index.js)"] --> D["AI_PROVIDERS (src/shared/constants/providers.js)"]
        C --> E["PROVIDER_MODELS (open-sse/config/providerModels.js)"]
    end

    subgraph "Execution_Layer"
        B --> F["BaseExecutor (open-sse/executors/base.js)"]
        F --> G["DefaultExecutor (open-sse/executors/default.js)"]
        F --> H["SpecializedExecutors"]
    end

    subgraph "Validation_Services"
        I["POST /api/providers/validate (src/app/api/providers/validate/route.js)"] --> J["probeWebProvider"]
        I --> K["probeMediaProvider"]
    end

    Sources: [open-sse/config/providerModels.js:1-8](), [src/shared/constants/providers.js:1-45](), [open-sse/executors/index.js:81-89](), [src/app/api/providers/validate/route.js:18-88]()
```

**Core Component Responsibilities:**

| Component | File Path | Purpose |
|-----------|---------|---------|
| `AI_PROVIDERS` | [src/shared/constants/providers.js:104]() | Combined dictionary of all configured providers built via `buildProviderEntry` [src/shared/constants/providers.js:13-41](). |
| `PROVIDER_MODELS` | [open-sse/config/providerModels.js:3]() | Co-located model and transport configurations per provider alias. |
| `getExecutor` | [open-sse/executors/index.js:81-85]() | Resolves specialized or `DefaultExecutor` instances based on provider id. |
| `resolveProviderAlias` | [open-sse/services/model.js:27-29]() | Resolves provider aliases or shortcodes to canonical provider IDs. |

Sources: [src/shared/constants/providers.js:13-104](), [open-sse/config/providerModels.js:1-7](), [open-sse/executors/index.js:81-85](), [open-sse/services/model.js:27-29]()

## Provider Types & Registry Integration

Providers are categorized by their category attribute in the master registry (`REGISTRY`), distinguishing between free providers (`FREE_PROVIDERS`), free-tier services (`FREE_TIER_PROVIDERS`), OAuth-backed systems (`OAUTH_PROVIDERS`), API key providers (`APIKEY_PROVIDERS`), and web cookie sessions (`WEB_COOKIE_PROVIDERS`) [src/shared/constants/providers.js:43-71](). 

Model identification handles provider-specific nuances such as dot-version tolerances (`DOT_VERSION_PROVIDERS` for Kiro/Claude version parsing) and dynamic upstream model resolution (`getModelUpstreamId`) [open-sse/config/providerModels.js:23-26,90-109]().

Sources: [src/shared/constants/providers.js:43-71](), [open-sse/config/providerModels.js:23-109]()

## Provider Executors

When an outgoing request targets a specific provider, 9Router delegates request building, URL formatting, and response parsing to the appropriate executor subclass extending `BaseExecutor` [open-sse/executors/index.js:81-89](). Specialized executors manage complex platforms (such as Kiro, Antigravity, Gemini CLI, Codex, Cursor, and Bedrock), while standard OpenAI-compatible endpoints fall back to `DefaultExecutor` [open-sse/executors/index.js:83]().

Diagram: Executor Resolution Flow
```mermaid
graph LR
    A["RequestTarget"] --> B["getExecutor (open-sse/executors/index.js)"]
    B --> C{"Has Specialized?"}
    C -->|Yes| D["SpecializedExecutor (e.g. CodexExecutor, KiroExecutor)"]
    C -->|No| E["DefaultExecutor (open-sse/executors/default.js)"]

    Sources: [open-sse/executors/index.js:81-89]()
```

For detailed documentation on specific executors, request transformation pipelines, and stream processing, see [Provider Executors](#5.3).

Sources: [open-sse/executors/index.js:1-121]()

## Credential Management & Validation

Credential handling integrates token generation, secure storage, and active probing:
- **Validation**: The validation route `POST /api/providers/validate` [src/app/api/providers/validate/route.js:91-104]() checks API keys against provider endpoints, utilizing helper probes like `probeWebProvider` [src/app/api/providers/validate/route.js:18-49]() and `probeMediaProvider` [src/app/api/providers/validate/route.js:53-88]() for specialized service kinds.
- **Refresh & Storage**: OAuth credentials undergo automatic background checks and token refreshes to ensure uninterrupted connection lifecycles.

For details on credential persistence and token lifecycles, see [Token Refresh & Credential Management](#5.4). For connection testing and health checks, see [Provider Validation & Testing](#5.6).

Sources: [src/app/api/providers/validate/route.js:18-104]()

---

