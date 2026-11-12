<!-- source: DeepWiki mcp.deepwiki.com · repo supermemoryai/supermemory · page 14 Self-Hosting · fetched 2026-10-30 -->

# Self-Hosting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/docs/self-hosting/overview.mdx](apps/docs/self-hosting/overview.mdx)
- [apps/docs/self-hosting/quickstart.mdx](apps/docs/self-hosting/quickstart.mdx)

</details>



Supermemory offers a self-hosted deployment option that packages the entire memory engine into a single, portable binary. This local server provides the same core API capabilities as the Cloud platform—including graph-based memory extraction, hybrid semantic search, and user profiling—while keeping data entirely on your own infrastructure.

### System Overview

The self-hosted version is designed for "zero-config" operation. It embeds the graph engine and local embedding models directly into the binary, eliminating the need for external databases like Postgres or vector stores.

#### Local Server Architecture
The following diagram illustrates how the `supermemory-server` binary interacts with your local environment and external LLM providers.

**Self-Hosted Component Map**
```mermaid
graph TD
    subgraph "LocalMachine"
        ["supermemory-server"]
        ["EmbeddedGraphEngine"]
        ["LocalEmbeddings_WASM"]
        ["SUPERMEMORY_DATA_DIR"]
        
        ["supermemory-server"] --> ["EmbeddedGraphEngine"]
        ["supermemory-server"] --> ["LocalEmbeddings_WASM"]
        ["EmbeddedGraphEngine"] --> ["SUPERMEMORY_DATA_DIR"]
        ["supermemory-server"] -.-> ["~/.supermemory/env"]
    end

    subgraph "ExternalProviders_BYOK"
        ["OpenAI_Anthropic_Gemini"]
        ["LocalLLM_Ollama_vLLM"]
    end

    subgraph "Clients"
        ["SupermemorySDK"]
        ["CodingPlugins_ClaudeCode"]
    end

    ["SupermemorySDK"] -- "baseURL:localhost:6767" --> ["supermemory-server"]
    ["CodingPlugins_ClaudeCode"] -- "SUPERMEMORY_API_URL" --> ["supermemory-server"]
    ["supermemory-server"] -- "Extraction&Summarization" --> ["OpenAI_Anthropic_Gemini"]
    ["supermemory-server"] -- "FullyOfflineMode" --> ["LocalLLM_Ollama_vLLM"]
```
Sources: [apps/docs/self-hosting/overview.mdx:8-31](), [apps/docs/self-hosting/quickstart.mdx:32-45]()

### Core Capabilities

The self-hosted binary enables several high-privacy and low-latency workflows:

*   **Local Embeddings**: Vectors are computed on-device using WASM-based models, ensuring that raw text is not sent to third-party embedding providers [apps/docs/self-hosting/overview.mdx:27-27]().
*   **Bring Your Own Key (BYOK)**: Use your existing API keys for OpenAI, Anthropic, Gemini, or Groq to power the "intelligent" steps of the pipeline, such as memory extraction and summarization [apps/docs/self-hosting/overview.mdx:31-31]().
*   **Fully Offline Operation**: By pointing the server to a local OpenAI-compatible endpoint (like Ollama or vLLM), you can run the entire memory stack without an internet connection [apps/docs/self-hosting/overview.mdx:33-44]().
*   **API Parity**: The local server implements the standard Memory API, including `/v3/documents`, `/v3/search`, and `/v4/profile` [apps/docs/self-hosting/overview.mdx:29-29]().

### Deployment Options

| Feature | Supermemory Local | Supermemory Enterprise |
| :--- | :--- | :--- |
| **Hosting** | Self-run binary | Fully managed cloud |
| **Multi-tenancy** | Single-tenant (one API key) | Multi-member orgs & roles |
| **Connectors** | Not supported | Google Drive, Notion, Gmail, etc. |
| **Models** | BYOK (User provided) | Proprietary tuned models |
| **Scalability** | Single machine | Globally distributed |

Sources: [apps/docs/self-hosting/overview.mdx:63-74]()

### Related Pages

- **[Local Server Setup](#14.1)**: Detailed instructions for installing via `curl` or `npx`, managing the data directory via `SUPERMEMORY_DATA_DIR`, and running the first-boot wizard. For details, see [Local Server Setup](#14.1).
- **[Configuration & Enterprise vs Local](#14.2)**: Deep dive into environment variables like `OPENAI_BASE_URL`, performance tuning, and a detailed comparison of features. For details, see [Configuration & Enterprise vs Local](#14.2).

**Code Entity to System Mapping**
```mermaid
graph LR
    subgraph "CodeEntities"
        ["Supermemory_TS_Client"]
        ["Supermemory_Python_Client"]
        ["withSupermemory_Middleware"]
    end

    subgraph "DeploymentTargets"
        ["supermemory-server_Local"]
        ["api.supermemory.ai_Cloud"]
    end

    ["Supermemory_TS_Client"] -- "baseURL:localhost:6767" --> ["supermemory-server_Local"]
    ["Supermemory_Python_Client"] -- "base_url:api.supermemory.ai" --> ["api.supermemory.ai_Cloud"]
    ["withSupermemory_Middleware"] -- "options.baseUrl" --> ["supermemory-server_Local"]
```
Sources: [apps/docs/self-hosting/overview.mdx:50-58](), [apps/docs/self-hosting/quickstart.mdx:57-85]()

Sources:
- [apps/docs/self-hosting/overview.mdx:1-86]()
- [apps/docs/self-hosting/quickstart.mdx:1-152]()

---

