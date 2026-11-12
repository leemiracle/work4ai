<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/DeepTutor · page 14 Glossary · fetched 2026-11-09 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/README/README_AR.md](assets/README/README_AR.md)
- [assets/README/README_CN.md](assets/README/README_CN.md)
- [assets/README/README_ES.md](assets/README/README_ES.md)
- [assets/README/README_FR.md](assets/README/README_FR.md)
- [assets/README/README_HI.md](assets/README/README_HI.md)
- [assets/README/README_JA.md](assets/README/README_JA.md)
- [assets/README/README_PL.md](assets/README/README_PL.md)
- [assets/README/README_PT.md](assets/README/README_PT.md)
- [assets/README/README_RU.md](assets/README/README_RU.md)
- [assets/README/README_TH.md](assets/README/README_TH.md)
- [deeptutor/__version__.py](deeptutor/__version__.py)
- [deeptutor/api/routers/mastery_path.py](deeptutor/api/routers/mastery_path.py)
- [deeptutor/api/routers/sessions.py](deeptutor/api/routers/sessions.py)
- [deeptutor/api/routers/unified_ws.py](deeptutor/api/routers/unified_ws.py)
- [deeptutor/capabilities/mastery/loop.py](deeptutor/capabilities/mastery/loop.py)
- [deeptutor/capabilities/mastery/prompts/en/mastery_loop.yaml](deeptutor/capabilities/mastery/prompts/en/mastery_loop.yaml)
- [deeptutor/capabilities/mastery/prompts/zh/mastery_loop.yaml](deeptutor/capabilities/mastery/prompts/zh/mastery_loop.yaml)
- [deeptutor/capabilities/mastery/tools.py](deeptutor/capabilities/mastery/tools.py)
- [deeptutor/learning/mastery.py](deeptutor/learning/mastery.py)
- [deeptutor/learning/models.py](deeptutor/learning/models.py)
- [deeptutor/learning/policy.py](deeptutor/learning/policy.py)
- [deeptutor/learning/question_card.py](deeptutor/learning/question_card.py)
- [deeptutor/learning/scheduler.py](deeptutor/learning/scheduler.py)
- [deeptutor/learning/semantic_assessment.py](deeptutor/learning/semantic_assessment.py)
- [deeptutor/learning/service.py](deeptutor/learning/service.py)
- [deeptutor/learning/storage.py](deeptutor/learning/storage.py)
- [deeptutor/learning/teaching.py](deeptutor/learning/teaching.py)
- [deeptutor/learning/tests/test_api_endpoints.py](deeptutor/learning/tests/test_api_endpoints.py)
- [deeptutor/learning/tests/test_guided_mastery_updates.py](deeptutor/learning/tests/test_guided_mastery_updates.py)
- [deeptutor/learning/tests/test_mastery_tools.py](deeptutor/learning/tests/test_mastery_tools.py)
- [deeptutor/learning/tests/test_models.py](deeptutor/learning/tests/test_models.py)
- [deeptutor/learning/tests/test_policy.py](deeptutor/learning/tests/test_policy.py)
- [deeptutor/learning/tests/test_scheduler.py](deeptutor/learning/tests/test_scheduler.py)
- [deeptutor/learning/tests/test_storage.py](deeptutor/learning/tests/test_storage.py)
- [deeptutor/services/session/attachment_parsing.py](deeptutor/services/session/attachment_parsing.py)
- [deeptutor/services/session/pocketbase_store.py](deeptutor/services/session/pocketbase_store.py)
- [deeptutor/services/session/protocol.py](deeptutor/services/session/protocol.py)
- [deeptutor/services/session/sqlite_store.py](deeptutor/services/session/sqlite_store.py)
- [deeptutor/services/session/thread_attribution.py](deeptutor/services/session/thread_attribution.py)
- [deeptutor/services/session/turn_runtime.py](deeptutor/services/session/turn_runtime.py)
- [deeptutor/services/session/turns/executor.py](deeptutor/services/session/turns/executor.py)
- [deeptutor/services/session/turns/request_preparer.py](deeptutor/services/session/turns/request_preparer.py)
- [tests/api/test_mastery_path_reviews.py](tests/api/test_mastery_path_reviews.py)
- [tests/api/test_session_organization.py](tests/api/test_session_organization.py)
- [tests/api/test_unified_ws_turn_runtime.py](tests/api/test_unified_ws_turn_runtime.py)
- [tests/capabilities/test_mastery_capability.py](tests/capabilities/test_mastery_capability.py)
- [tests/capabilities/test_mastery_profile_continuity.py](tests/capabilities/test_mastery_profile_continuity.py)
- [tests/capabilities/test_mastery_semantic_assessment.py](tests/capabilities/test_mastery_semantic_assessment.py)
- [tests/capabilities/test_mastery_teaching_compass.py](tests/capabilities/test_mastery_teaching_compass.py)
- [tests/capabilities/test_mastery_teaching_focus.py](tests/capabilities/test_mastery_teaching_focus.py)
- [tests/services/session/test_attachment_parsing.py](tests/services/session/test_attachment_parsing.py)
- [tests/services/session/test_pocketbase_store_fallbacks.py](tests/services/session/test_pocketbase_store_fallbacks.py)
- [tests/services/session/test_regenerate.py](tests/services/session/test_regenerate.py)
- [tests/services/session/test_sqlite_store.py](tests/services/session/test_sqlite_store.py)
- [tests/services/session/test_thread_attribution.py](tests/services/session/test_thread_attribution.py)
- [tests/services/session/test_turn_runtime_subscribe.py](tests/services/session/test_turn_runtime_subscribe.py)
- [web/app/(workspace)/learning/page.tsx](web/app/(workspace)/learning/page.tsx)
- [web/lib/learning-api.ts](web/lib/learning-api.ts)
- [web/lib/session-api.ts](web/lib/session-api.ts)

</details>



## Purpose and Scope
This wiki page provides comprehensive technical definitions of codebase-specific terms, architectural patterns, and internal jargon used across the DeepTutor codebase (`https://github.com/HKUDS/DeepTutor`). It bridges natural language concepts with their exact code entities, classes, routers, and data structures.

Sources: `[README.md:1-40]()`, `[README.md:60-70]()`

---

## Core Concepts

### Content Workspace
A user-definable folder representing the filesystem context where the agent has read access and writes all generated outputs (including tool results, downloads, caches, rendered figures). Output files reside under `outputs/<capability>/<session>/<turn>/` within this workspace. The content workspace is isolated from sensitive user settings, API keys, databases, or internal app state, which live separately in the private runtime home directory.

Sources: `[assets/README/README_CN.md:77-90]()`

### Capability
A distinct functional module or mode within the DeepTutor system (e.g., `Chat`, `Quiz`, `Research`, `Visualize`, `Solve`, `Mastery Path`, `Reading`, `Watching`). All capabilities share a common runtime environment and session context while maintaining specialized loops and pipelines.

Sources: `[README.md:60-70]`, `[deeptutor/capabilities/mastery/loop.py:43-66]()`

### Turn Runtime
The environment responsible for handling a single user turn request, including preparation, context assembly, execution, and lifecycle management. The `TurnRuntimeManager` class orchestrates these activities.

Sources: `[deeptutor/services/session/turn_runtime.py:26-35]`, `[deeptutor/services/session/sqlite_store.py:147-184]()`

### Agentic Loop
The iterative reasoning loop driving agent decision-making within a turn. Each loop round issues a large language model call producing tagged outputs parsed incrementally into thoughts, tool calls, and final response text.

Sources: `[deeptutor/capabilities/mastery/loop.py:43-66]()`

### Partners
Persistent AI tutor companions with stateful workspaces, individualized memories, and dedicated IM bindings across channels (Telegram, Discord, Slack). Each Partner is configured with a `SOUL.md` persona definition.

Sources: `[assets/README/README_RU.md:63-67]`, `[README.md:63-66]()`

### SOUL.md
A markdown-based persona file defining a Partner’s identity, goals, constraints, and conversational style. It acts as the immutable source of truth for the Partner’s persistent character.

Sources: `[README.md:63-66]()`

### Mastery Path
An engine for personalized learning following mastery-based progression through topics and modules. It tracks `LearningProgress` aggregates with detailed knowledge points (KPs), quiz attempts, error records, and spaced repetition states.

Sources: `[deeptutor/learning/models.py:1-30]`, `[deeptutor/learning/service.py:1-50]`, `[deeptutor/capabilities/mastery/tools.py:1-15]()`

### Knowledge Point (KP)
A granular unit of learner knowledge within a `LearningModule`. Each KP has an ID, name, type (e.g., `memory`, `procedure`, `concept`, `design`), and is linked with prerequisites and sources.

Sources: `[deeptutor/learning/models.py:10-30]`, `[deeptutor/learning/service.py:118-121]()`

### RAG Engines
Retrieval-Augmented Generation engines enabling knowledge retrieval and reasoning with external or internal knowledge bases. Supported engines include LlamaIndex, PageIndex, GraphRAG, LightRAG, WeKnora, and Tencent IMA.

Sources: `[assets/README/README_AR.md:60-65]()`

### MCP (Model Context Protocol)
A client-server integration protocol allowing DeepTutor to connect to external tool servers or agent harnesses. The MCP connection manager handles connection lifecycle and tool registry synchronization.

Sources: `[README.md:63-66]()`

### Subagent
An external agent handler (such as Claude Code, Codex, Grok CLI) callable from chat, acting as a specialized compute backend or assistant persona.

Sources: `[assets/README/README_RU.md:63-67]()`

### CLI Apps
Command-line interface applications which the system can invoke as agent tools, enabling agent use of system utilities, specialized workflows, or SDKs.

Sources: `[assets/README/README_CN.md:63-67]()`

### Reading Locator
A fine-grained document location reference used for precise annotations, navigating to positions within PDFs or EPUBs, and linking in immersive reading modes.

Sources: `[README.md:60-65]()`

### Book Blocks
Structural content units within the Living Book pipeline, representing annotated text, code snippets, images, or interactive elements authored into pages and chapters.

Sources: `[README.md:60-65]()`

### Whisper Rooms
UI components and backend support for multi-agent conversational spaces allowing multiple agents or humans to collaboratively interact in a persistent chat room.

Sources: `[README.md:63-66]()`

### Invidious
A self-hosted privacy-focused frontend for YouTube video playback integrated into the Immersive Watching mode.

Sources: `[assets/README/README_RU.md:65-66]()`

### Grants
Account-level permissions and access rights governing availability to knowledge bases, tools, capabilities, and learning policies for users.

Sources: `[README.md:60-65]()`

### Chat-Engine Profiles
TypeScript-native engine configurations under `packages/chat-engine` defining run-loops, model rounds, stream decoding, and tool dispatching.

Sources: `[README.md:60-65]()`

### Module Manifests
Declarative capability manifests under `deeptutor/modules` governing optional dependency gating, requirements, and plugin loading.

Sources: `[README.md:60-65]()`

Sources: `[README.md:1-70]`, `[deeptutor/learning/models.py:1-30]`, `[deeptutor/learning/service.py:1-50]`, `[deeptutor/services/session/turn_runtime.py:26-35]()`

---

## Architectural Components

### AgentLoop
The core per-turn execution engine implementing the agentic interactive loop. Coordinates LLM calls, command parsing, tool dispatch, intermediate streaming output, and final user response.

Sources: `[deeptutor/agents/chat/agent_loop.py:1-50]()`

### AgenticChatPipeline
The assembling layer of chat capability handling request pre-processing, composing prompts, invoking the `AgentLoop`, managing tool registries, and gatekeeping user grants on tool usage.

Sources: `[deeptutor/agents/chat/agentic_pipeline.py:1-48]()`

### LearningService
Manages the Mastery Path learning engine lifecycle, orchestrating module initialization, progress resets, grading, mastery computation, and spaced repetition scheduling.

Sources: `[deeptutor/learning/service.py:1-40]()`

### MCP Manager
The connection and configuration manager for Model Context Protocol servers, supervising remote tool adapters and synchronization with the local runtime.

Sources: `[deeptutor/services/mcp/manager.py:1-40]()`

Sources: `[deeptutor/agents/chat/agent_loop.py:1-50]`, `[deeptutor/agents/chat/agentic_pipeline.py:1-48]`, `[deeptutor/learning/service.py:1-40]`, `[deeptutor/services/mcp/manager.py:1-40]()`

---

## Technical Terminology & Jargon

| Term | Description | Code Reference |
| :--- | :--- | :--- |
| **Content Workspace** | User-accessible file folder for agent I/O, isolated from config and secrets. | `[assets/README/README_CN.md:77-90]()` |
| **Capability** | Functional unit or mode sharing runtime but with specialized execution logic. | `[README.md:60-70]()` |
| **Turn Runtime** | Single turn execution environment for request handling and lifecycle management. | `[deeptutor/services/session/turn_runtime.py:26-35]()` |
| **Agentic Loop** | Iterative LLM reasoning and tool dispatch loop per chat turn. | `[deeptutor/capabilities/mastery/loop.py:43-66]()` |
| **Partners** | Persistent AI tutor instances with workspace, memory, and IM channel bindings. | `[assets/README/README_RU.md:63-67]()` |
| **SOUL.md** | Markdown persona file defining Partner identity and constraints. | `[README.md:63-66]()` |
| **Mastery Path** | Progressive learning engine with modules, topics, spaced repetition, and grading. | `[deeptutor/learning/service.py:1-50]()` |
| **KP (Knowledge Point)** | Atomic learning unit tracked for mastery in modules. | `[deeptutor/learning/models.py:10-30]()` |
| **RAG Engines** | Multi-engine RAG pipeline for knowledge retrieval (LlamaIndex, LightRAG, etc.). | `[assets/README/README_AR.md:60-65]()` |
| **MCP** | Protocol to connect external tool servers as integrated capabilities. | `[README.md:63-66]()` |
| **Subagent** | External agent harnesses callable inside chat (Claude Code, Codex). | `[assets/README/README_RU.md:63-67]()` |
| **CLI Apps** | Shell applications available as agent-invokable tools. | `[assets/README/README_CN.md:63-67]()` |
| **Reading Locator** | Fine-grained document location reference for Immersive Reading annotations. | `[README.md:60-65]()` |
| **Book Blocks** | Modular content units composing Living Book pages (text, code, images). | `[README.md:60-65]()` |
| **Whisper Rooms** | Multi-agent chat UI rooms enabling collaborative session across agents and users. | `[README.md:63-66]()` |
| **Invidious** | Privacy-friendly self-hosted YouTube frontend used in Immersive Watching mode. | `[assets/README/README_RU.md:65-66]()` |
| **Grants** | User permission sets controlling access to KBs, capabilities, and system tools. | `[README.md:60-65]()` |
| **Chat-Engine Profiles** | TypeScript-native engine profiles and run-loop configurations. | `[README.md:60-65]()` |
| **Module Manifests** | Declarative manifests under deeptutor/modules for plugin gating and loading. | `[README.md:60-65]()` |

Sources: `[README.md:60-70]`, `[deeptutor/learning/service.py:1-50]`, `[deeptutor/services/session/turn_runtime.py:26-35]()`

---

## Data Flow Diagrams

### Diagram 1: Natural Language Space to Turn Runtime and Tool Dispatch
Bridging user natural language input down to concrete execution classes (`TurnRuntimeManager`, `AgenticChatPipeline`, `AgentLoop`, and `ToolRegistry`).

```mermaid
graph TD
    User[""UserNaturalLanguageInput""] --> Pipeline[""AgenticChatPipeline (deeptutor/agents/chat/agentic_pipeline.py)""]
    Pipeline --> Runtime[""TurnRuntimeManager (deeptutor/services/session/turn_runtime.py)""]
    Runtime --> Loop[""AgentLoop (deeptutor/capabilities/mastery/loop.py)""]
    Loop --> Dispatch[""dispatch_tool_calls""]
    Dispatch --> Registry[""ToolRegistry (runtime/registry/tool_registry.py)""]
    Registry --> Result[""ToolResult""]
    Result --> Loop
```

Sources: `[deeptutor/services/session/turn_runtime.py:26-35]`, `[deeptutor/agents/chat/agentic_pipeline.py:1-48]`, `[deeptutor/capabilities/mastery/loop.py:43-66]()`

### Diagram 2: Mastery Path Learning Engine Data Flow
Bridging course objectives and student submissions to `LearningService`, grading heuristics, and persistent SQLite storage.

```mermaid
graph TD
    StudentInput[""StudentAssessmentSubmission""] --> Service[""LearningService (deeptutor/learning/service.py)""]
    Service --> Grading[""grade_answer (deeptutor/learning/grading.py)""]
    Service --> Mastery[""compute_mastery (deeptutor/learning/mastery.py)""]
    Mastery --> Progress[""LearningProgress (deeptutor/learning/models.py)""]
    Progress --> Store[""LearningStore (deeptutor/learning/storage.py)""]
    Store --> DB[""SQLiteDatabase (deeptutor/services/session/sqlite_store.py)""]
```

Sources: `[deeptutor/learning/service.py:1-50]`, `[deeptutor/learning/models.py:1-30]`, `[deeptutor/services/session/sqlite_store.py:147-184]()`

---

## CLI Command Glossary

| Command | Purpose | Code Reference |
| :--- | :--- | :--- |
| `deeptutor init` | Interactive setup wizard for initial configuration and provider keys. | `[README.md:80-90]()` |
| `deeptutor start` | Launch backend FastAPI server and Next.js frontend UI workspace. | `[README.md:80-90]()` |
| `deeptutor chat` | Command-line REPL interface for direct agent interaction. | `[README.md:80-90]()` |
| `deeptutor kb` | Manage knowledge bases (creation, document staging, evaluation). | `[README.md:80-90]()` |
| `deeptutor doctor` | Diagnostic utility for checking dependencies, ports, and environment setup. | `[README.md:80-90]()` |
| `deeptutor book` | Trigger the Living Book generation and spine synthesis pipeline. | `[README.md:80-90]()` |
| `deeptutor memory` | Inspect and curate layered memory traces, facts, and L3 syntheses. | `[README.md:80-90]()` |

Sources: `[README.md:80-90]()`