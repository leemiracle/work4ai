<!-- source: DeepWiki mcp.deepwiki.com · repo supermemoryai/supermemory · page 13 Plugins & Extensions · fetched 2026-10-30 -->

# Plugins & Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/auth/agent-connect/page.tsx](apps/web/app/auth/agent-connect/page.tsx)
- [apps/web/components/document-cards/mcp-preview.tsx](apps/web/components/document-cards/mcp-preview.tsx)
- [apps/web/components/document-cards/note-preview.tsx](apps/web/components/document-cards/note-preview.tsx)
- [apps/web/components/document-cards/plugin-preview.tsx](apps/web/components/document-cards/plugin-preview.tsx)
- [apps/web/components/document-modal/content/plugin-content.tsx](apps/web/components/document-modal/content/plugin-content.tsx)
- [apps/web/components/document-modal/title.tsx](apps/web/components/document-modal/title.tsx)
- [apps/web/lib/plugin-catalog.ts](apps/web/lib/plugin-catalog.ts)
- [apps/web/lib/plugin-document.ts](apps/web/lib/plugin-document.ts)
- [apps/web/lib/plugin-space.ts](apps/web/lib/plugin-space.ts)
- [packages/agent-framework-python/README.md](packages/agent-framework-python/README.md)
- [packages/openai-sdk-python/README.md](packages/openai-sdk-python/README.md)
- [skills/supermemory/LICENSE](skills/supermemory/LICENSE)
- [skills/supermemory/README.md](skills/supermemory/README.md)
- [skills/supermemory/SKILL.md](skills/supermemory/SKILL.md)
- [skills/supermemory/references/api-reference.md](skills/supermemory/references/api-reference.md)
- [skills/supermemory/references/architecture.md](skills/supermemory/references/architecture.md)
- [skills/supermemory/references/quickstart.md](skills/supermemory/references/quickstart.md)
- [skills/supermemory/references/sdk-guide.md](skills/supermemory/references/sdk-guide.md)
- [skills/supermemory/references/use-cases.md](skills/supermemory/references/use-cases.md)

</details>



This section provides an overview of how Supermemory extends its capabilities beyond the web application and browser extension into third-party ecosystems. It covers the **Claude Skill**, the **Raycast Extension**, and a suite of **Coding Assistant Plugins** that bring persistent memory to development workflows, IDEs, and messaging platforms.

## Claude Skill

The Supermemory Claude Skill is a specialized reference package designed for the Anthropic skills marketplace and Claude Desktop. Its primary purpose is to "teach" Claude how to use Supermemory as a long-term and short-term memory infrastructure for AI agents [skills/supermemory/README.md:6-12]().

The skill uses an auto-invocation mechanism defined in `SKILL.md` that allows Claude to proactively suggest Supermemory when it detects a user needs persistent memory, personalization, or knowledge retrieval [skills/supermemory/README.md:35-43](). It includes a comprehensive set of reference documents that guide the LLM through implementation patterns for various SDKs and use cases.

### Skill Components
The skill is structured as a directory of Markdown files that serve as a knowledge base for the LLM:

| Component | Purpose |
|-----------|---------|
| `SKILL.md` | Main entry point with overview and quick examples [skills/supermemory/SKILL.md:1-4]() |
| `references/quickstart.md` | 5-minute setup guide for developers [skills/supermemory/references/quickstart.md:1-3]() |
| `references/sdk-guide.md` | Full reference for TypeScript and Python SDKs [skills/supermemory/references/sdk-guide.md:1-3]() |
| `references/api-reference.md` | REST API endpoint documentation [skills/supermemory/references/api-reference.md:1-3]() |
| `references/architecture.md` | Explains the Living Knowledge Graph and processing pipeline [skills/supermemory/references/architecture.md:5-7]() |
| `references/use-cases.md` | 8 concrete implementation examples (Chatbots, RAG, etc.) [skills/supermemory/references/use-cases.md:7-14]() |

For details, see [Claude Skill](#13.1).

**Sources:**
- [skills/supermemory/README.md:6-58]()
- [skills/supermemory/SKILL.md:6-38]()
- [skills/supermemory/references/quickstart.md:1-48]()

---

## Raycast Extension

The Raycast Extension provides a native macOS interface for interacting with Supermemory. It allows users to capture information and search their knowledge base without leaving their current application workflow.

### Core Commands
The extension implements several key commands using the `@raycast/api`:

*   **Add Memory**: A form-based command (`add-memory.tsx`) that allows users to save text to Supermemory. It features an automatic "Quick Add" capability that pre-fills the content field with currently selected text from any macOS application [apps/raycast-extension/src/add-memory.tsx:21-43]().
*   **Search Memories**: A list-view command (`search-memories.tsx`) for semantic search. It displays results with relevance scores and allows users to copy content or open source URLs directly [apps/raycast-extension/src/search-memories.tsx:56-107]().
*   **Search Projects**: A command to browse and select specific `containerTags` (projects) to organize memories [apps/raycast-extension/src/add-memory.tsx:97-112]().

### Technical Implementation
The extension is built with React and utilizes a Higher-Order Component (HoC) called `withSupermemory` to enforce API key presence and handle authentication logic before commands are executed [apps/raycast-extension/src/withSupermemory.tsx](). It communicates with the backend via the `makeAuthenticatedRequest` utility [apps/raycast-extension/src/api.ts:78-81]().

For details, see [Raycast Extension](#13.2).

**Sources:**
- [apps/raycast-extension/src/add-memory.tsx:1-114]()
- [apps/raycast-extension/src/search-memories.tsx:1-178]()
- [apps/raycast-extension/src/api.ts:78-135]()

---

## Coding Assistant Plugins

Supermemory provides dedicated plugins for terminal-based coding assistants, IDEs like Cursor, and messaging gateways. These plugins automate the "Recall" (context injection) and "Capture" (memory storage) cycle during active development or communication.

### Plugin Catalog & Installation
The system maintains a `PLUGIN_CATALOG` that defines the metadata and installation steps for each external surface [apps/web/lib/plugin-catalog.ts:31-177]().

*   **Claude Code**: Installed via `/plugin marketplace add supermemoryai/claude-supermemory`. It remembers conventions and project context [apps/web/lib/plugin-catalog.ts:32-53]().
*   **Cursor**: Integrates via the Cursor Marketplace and a local auth command `cursor-supermemory login` [apps/web/lib/plugin-catalog.ts:77-112]().
*   **OpenClaw**: A cross-platform gateway for Telegram, Discord, and Slack [apps/web/lib/plugin-catalog.ts:142-161]().
*   **OpenCode & Hermes**: Specialized agent memory providers offering persistent context for agent sessions [apps/web/lib/plugin-catalog.ts:113-141]().

### Plugin Data Handling
When plugins ingest data, Supermemory parses the content into structured `ParsedPluginDocument` objects [apps/web/lib/plugin-document.ts:46-62](). The system uses `detectPluginSpace` to map incoming `containerTag` identifiers to specific plugin identities like `claude-code`, `opencode`, or `hermes` [apps/web/lib/plugin-space.ts:185-218]().

"Plugin to API Entity Mapping"
```mermaid
graph TD
    subgraph "Natural Language Space (User Actions)"
        "CC_EDIT[Claude Code: Edit File]"
        "OC_CHAT[OpenClaw: Chat Message]"
        "CUR_CHAT[Cursor: Chat Session]"
    end

    subgraph "Code Entity Space (Plugin Logic)"
        "CC_HOOK[claude-supermemory:Auto-Capture]"
        "OC_RECALL[openclaw-supermemory:Auto-Recall]"
        "SDK_MW[withSupermemory:Middleware]"
    end

    subgraph "Supermemory API (v3/v4)"
        "EP_DOCS[POST /v3/documents]"
        "EP_PROF[POST /v4/profile]"
        "EP_ADD[POST /v3/add]"
    end

    "CC_EDIT" --> "CC_HOOK"
    "OC_CHAT" --> "OC_RECALL"
    "CUR_CHAT" --> "SDK_MW"
    
    "CC_HOOK" -- "sm_source: claude-code" --> "EP_DOCS"
    "OC_RECALL" -- "containerTag: openclaw" --> "EP_PROF"
    "SDK_MW" -- "content" --> "EP_ADD"
```

For details, see [Coding Assistant Plugins](#13.3).

**Sources:**
- [apps/web/lib/plugin-catalog.ts:31-177]()
- [apps/web/lib/plugin-document.ts:46-193]()
- [apps/web/lib/plugin-space.ts:17-54]()

---

## Ecosystem Overview

This diagram shows how these external surfaces bridge the gap between user intent and the core Supermemory infrastructure via the SDK and REST API.

"External Surface Integration"
```mermaid
graph LR
    subgraph "External Surfaces"
        "Claude[Claude Skill]"
        "Raycast[Raycast Extension]"
        "Coding[Coding Plugins]"
    end

    subgraph "Supermemory Core"
        "SDK[supermemory SDK]"
        "REST[REST API]"
        "Graph[Living Knowledge Graph]"
    end

    "Claude" -- "Teaches implementation" --> "SDK"
    "Claude" -- "Auto-invokes via" --> "SKILL.md"
    "Raycast" -- "Calls" --> "REST"
    "Coding" -- "Uses" --> "SDK"
    "SDK" -- "Wraps" --> "REST"
    "REST" -- "Mutates/Queries" --> "Graph"
```

**Sources:**
- [skills/supermemory/SKILL.md:95-103]()
- [apps/raycast-extension/src/api.ts:54-54]()
- [skills/supermemory/references/architecture.md:5-36]()
- [apps/web/lib/plugin-catalog.ts:31-53]()

---

