<!-- source: DeepWiki mcp.deepwiki.com · repo NousResearch/hermes-agent · page 4 Core Agent · fetched 2026-10-30 -->

# Core Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/auxiliary_client.py](agent/auxiliary_client.py)
- [cli-config.yaml.example](cli-config.yaml.example)
- [cli.py](cli.py)
- [gateway/run.py](gateway/run.py)
- [gateway/session.py](gateway/session.py)
- [gateway/slash_commands.py](gateway/slash_commands.py)
- [hermes_cli/cli_commands_mixin.py](hermes_cli/cli_commands_mixin.py)
- [hermes_cli/commands.py](hermes_cli/commands.py)
- [hermes_cli/config.py](hermes_cli/config.py)
- [hermes_cli/config_defaults.py](hermes_cli/config_defaults.py)
- [hermes_cli/main.py](hermes_cli/main.py)
- [hermes_cli/setup.py](hermes_cli/setup.py)
- [hermes_state.py](hermes_state.py)
- [run_agent.py](run_agent.py)
- [tests/agent/test_auxiliary_client.py](tests/agent/test_auxiliary_client.py)
- [tests/gateway/test_session.py](tests/gateway/test_session.py)
- [tests/hermes_cli/test_commands.py](tests/hermes_cli/test_commands.py)
- [ui-tui/src/__tests__/details.test.ts](ui-tui/src/__tests__/details.test.ts)
- [ui-tui/src/domain/details.ts](ui-tui/src/domain/details.ts)
- [website/docs/getting-started/quickstart.md](website/docs/getting-started/quickstart.md)
- [website/docs/integrations/providers.md](website/docs/integrations/providers.md)
- [website/docs/reference/cli-commands.md](website/docs/reference/cli-commands.md)
- [website/docs/reference/environment-variables.md](website/docs/reference/environment-variables.md)
- [website/docs/reference/slash-commands.md](website/docs/reference/slash-commands.md)
- [website/docs/user-guide/cli.md](website/docs/user-guide/cli.md)
- [website/docs/user-guide/configuration.md](website/docs/user-guide/configuration.md)
- [website/docs/user-guide/features/fallback-providers.md](website/docs/user-guide/features/fallback-providers.md)
- [website/docs/user-guide/messaging/index.md](website/docs/user-guide/messaging/index.md)
- [website/docs/user-guide/tui.md](website/docs/user-guide/tui.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/getting-started/quickstart.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/getting-started/quickstart.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/environment-variables.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/environment-variables.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/configuration.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/configuration.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/fallback-providers.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/fallback-providers.md)

</details>



The Core Agent is the central orchestration component of Hermes Agent, implemented by the `AIAgent` class in `run_agent.py` [run_agent.py:2-7](). It manages the complete lifecycle of AI-powered conversations, coordinating LLM interactions, tool execution, context management, memory, and session persistence. All entry points — including the CLI, Gateway service, and Batch Runner — instantiate an `AIAgent` and invoke its conversation methods to execute tasks [run_agent.py:4-6]().

This page provides a high-level overview of the `AIAgent` class structure, its initialization, core responsibilities, and how it connects natural language conversation inputs to underlying code entities managing tools, execution loops, and memory subsystems.

## Purpose and Scope

The Core Agent serves as the unified interface for conversation flows within Hermes Agent. It abstracts system complexities such as:

- Selecting and managing LLM providers and their client instances via provider resolution and the proxy client wrapper [agent/auxiliary_client.py:1-9]().
- Discovering, enabling, and dispatching tools through the centralized tool system [run_agent.py:103-105]().
- Maintaining conversation context, system prompts, and user memory [agent/memory_provider.py:109]().
- Handling session persistence, message logging, and trajectory management [agent/session_persistence.py:119]().
- Managing iteration budgets with support for subagent delegation and user interrupts [run_agent.py:91]().

For detailed technical workflows and component behaviors, see the child pages linked at the end of this page.

Sources: [run_agent.py:2-7](), [run_agent.py:91](), [run_agent.py:103-105](), [agent/auxiliary_client.py:1-9](), [agent/memory_provider.py:109](), [agent/session_persistence.py:119]()

---

## AIAgent Class Overview

The `AIAgent` class encapsulates the Core Agent, managing session state and conversational behavior. Due to its scope, its logic is modularized into mixins and helper packages under `agent/`, with `AIAgent` acting as the central coordinator [run_agent.py:2-7]().

### Diagram: Natural Language Space to Code Entity Space

```mermaid
graph TB
    subgraph Natural_Language_Space
        NL[""User Query / Natural Language Input""]
    end

    subgraph Code_Entity_Space
        PROMPT[""PromptBuilder<br/>(agent/prompt_builder.py)""]
        LOOP[""run_conversation<br/>(agent/conversation_loop.py)""]
        CLIENT[""call_llm<br/>(agent/auxiliary_client.py)""]
        TOOLS[""get_toolset_for_tool<br/>(model_tools.py)""]
        MEM[""is_trivial_prompt<br/>(agent/memory_provider.py)""]
    end

    NL --> PROMPT
    PROMPT --> LOOP
    LOOP --> CLIENT
    CLIENT --> TOOLS
    TOOLS --> MEM
```

Sources: [run_agent.py:2-7](), [run_agent.py:103](), [agent/auxiliary_client.py:20](), [agent/memory_provider.py:109]()

---

### Diagram: AIAgent Subsystem Architecture

```mermaid
graph TB
    subgraph Natural_Language_Space
        IN[""External Request / CLI / Gateway""]
    end

    subgraph Code_Entity_Space
        AGENT[""AIAgent<br/>(run_agent.py)""]
        INIT[""ClientLifecycleMixin<br/>(agent/client_lifecycle.py)""]
        COMPRESSOR[""CompressionFacadeMixin<br/>(agent/compression_facade.py)""]
        LOOP[""TurnFacadeMixin<br/>(agent/turn_facade.py)""]
        APICALL[""ApiRequestHooksMixin<br/>(agent/api_request_hooks.py)""]
        FINALIZER[""SessionPersistenceMixin<br/>(agent/session_persistence.py)""]
    end

    IN --> AGENT
    AGENT --> INIT
    AGENT --> COMPRESSOR
    AGENT --> LOOP
    LOOP --> APICALL
    APICALL --> FINALIZER
```

Sources: [run_agent.py:110-121]()

---

## Initialization and Configuration

The `AIAgent` class accepts configuration parameters during instantiation, handling provider auto-detection, credential resolution, and context-engine bootstrap [run_agent.py:5-6]().

| Configuration Area | Core Parameters | Purpose |
|-------------------|-----------------|---------|
| LLM Setup | `model`, `base_url`, `api_key`, `provider` | Specify model identity and connectivity [run_agent.py:5-6]() |
| Tool Management | `toolsets` | Filter enabled toolsets [hermes_cli/config_defaults.py:43]() |
| Conversation Control | `max_turns`, `run_budget_seconds` | Limit iteration steps and wall-clock time [hermes_cli/config_defaults.py:76-85]() |
| Persistent Sessions | `session_id`, `_session_db` | Enable persistent session logging and trajectory saving [run_agent.py:119]() |

Sources: [run_agent.py:5-6](), [run_agent.py:119](), [hermes_cli/config_defaults.py:43](), [hermes_cli/config_defaults.py:76-85]()

---

## Core Responsibilities of `AIAgent`

### 1. Conversation Loop and Tool Execution
The agent drives multi-turn reasoning loops, evaluating incoming messages, orchestrating sequential or concurrent tool execution rounds, and enforcing iteration budgets [run_agent.py:91](). The `TurnFacadeMixin` [run_agent.py:121]() provides the core logic for managing turns. For details, see [Conversation Loop](#4.1).

Sources: [run_agent.py:91](), [run_agent.py:121]()

### 2. Context and Prompt Management
Responsible for system prompt composition, persona injection (`SOUL.md`), prompt caching policies, and dynamic sanitization of message contents [website/docs/user-guide/configuration.md:25](). The `CompressionFacadeMixin` [run_agent.py:120]() handles automatic context window compression to manage token limits. For details, see [Context and Prompt Management](#4.2).

Sources: [run_agent.py:120](), [website/docs/user-guide/configuration.md:25]()

### 3. Memory and Sessions
Manages SQLite-backed session persistence (`SessionDB`), trajectory logging, user files (`MEMORY.md`/`USER.md`), and native tokenizer extensions [hermes_state.py:1-6](). Session data is stored and retrieved to maintain conversational history across turns. The `SessionPersistenceMixin` [run_agent.py:119]() integrates this functionality. For details, see [Memory and Sessions](#4.3).

Sources: [hermes_state.py:1-6](), [run_agent.py:119]()

### 4. Honcho Integration
Provides AI-native memory capabilities via `HonchoSessionManager`, handling write frequencies, prefetch pipelines, and dialectic queries. This integration enhances the agent's ability to manage and retrieve complex information. For details, see [Honcho Integration](#4.4).

Sources: [hermes_cli/config_defaults.py:1-5]() (Implicitly, as Honcho is an advanced memory provider)

### 5. Auxiliary Client
Executes side tasks such as vision analysis, context compression, and web extractions using decoupled provider resolution and specialized adapters [agent/auxiliary_client.py:1-9](). The `call_llm` function [agent/auxiliary_client.py:20]() is used for these auxiliary LLM calls. For details, see [Auxiliary Client](#4.5).

Sources: [agent/auxiliary_client.py:1-9](), [agent/auxiliary_client.py:20]()

---

## Child Pages

For detailed technical deep dives on Core Agent subtopics, see the following child pages:

- [Conversation Loop](#4.1) — Detail the iterative conversation loop, tool calling flow, turn finalization, transports, error classification, iteration budget, and interrupt handling.
- [Context and Prompt Management](#4.2) — Explain system prompt building, context files, SOUL.md persona, prompt caching, message sanitization, redaction, and dynamic prompt injection.
- [Memory and Sessions](#4.3) — Cover session persistence (SQLite SessionDB), trajectory logging, MEMORY.md/USER.md files, session search and recovery, and native CJK FTS5 tokenizer extensions.
- [Honcho Integration](#4.4) — Document Honcho AI-native memory, HonchoSessionManager, write frequency modes, prefetch pipeline, and dialectic queries.
- [Auxiliary Client](#4.5) — Explain the auxiliary LLM client system for side tasks (vision, compression, web extraction), provider resolution for auxiliary tasks, and Anthropic/Bedrock/Codex/Gemini adapters.

Sources: [run_agent.py:2-7]()

---

