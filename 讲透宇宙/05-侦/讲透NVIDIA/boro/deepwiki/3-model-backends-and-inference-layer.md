<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/boro · page 3 Model Backends and Inference Layer · fetched 2026-10-26 -->

# Model Backends and Inference Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/api.rs](src/api.rs)
- [src/config.rs](src/config.rs)
- [src/prompts.rs](src/prompts.rs)
- [src/target/libvirt.rs](src/target/libvirt.rs)
- [src/target/virt_manager.rs](src/target/virt_manager.rs)

</details>



The model backends and inference layer in `boro` manage all external interactions with Large Language Models, supporting both OpenAI-compatible HTTP endpoints and local subprocess CLI tools (`claude`, `opencode`, `codex`). This subsystem translates high-level review stages, system prompts, and repository tools into structured API requests, handles token budgeting and ephemeral caching, executes sandboxed repository tool loops, and parses strict JSON responses.

For detailed information, refer to the child pages:
- [chat_completion, Streaming and Retries](#3.1)
- [Token Budgets, Prompt Caching and Timeouts](#3.2)
- [Repository Tool Loop](#3.3)
- [Payload Builders and Response Parsers](#3.4)

---

## Backend Abstraction and Configuration

`boro` supports multiple model integration strategies encapsulated by the `Backend` enum [src/config.rs:8-34](). Configuration parameters such as API base URLs, API keys, model identifiers, sampling temperatures, context lengths, and prompt caching flags are unified under the `ResolvedModel` struct [src/config.rs:85-120]().

```mermaid
title "Backend Resolution Architecture"
graph TD
    Env["Environment Variables BORO_URL, BORO_KEY, BORO_MODEL"] --> Res["ResolvedModel src/config.rs:85-120"]
    Flag["CLI Flags --backend, --enable-prompt-cache"] --> Res
    Res -->|OpenAi| HttpBackend["OpenAI-Compatible HTTP Client src/api.rs"]
    Res -->|Claude| SubprocessClaude["claude CLI Subprocess src/claude_cli.rs"]
    Res -->|Opencode| SubprocessOpencode["opencode CLI Subprocess src/opencode.rs"]
    Res -->|Codex| SubprocessCodex["codex CLI Subprocess src/codex_cli.rs"]
```
*Sources: [src/config.rs:8-120](), [src/api.rs:16-20]()*

---

## Sub-Topic Overview and Child Links

### 3.1 chat_completion, Streaming and Retries
The core inference function orchestrates outbound HTTP posts, Server-Sent Events (SSE) streaming parse loops, automatic error recovery, and fallback mechanisms for non-2xx responses or malformed JSON payloads. For details, see [chat_completion, Streaming and Retries](#3.1).
*Sources: [src/api.rs:47-121]() *

### 3.2 Token Budgets, Prompt Caching and Timeouts
To prevent context window overflow and control costs, `boro` implements conservative input budget trimming, elided tool result management, Anthropic-style ephemeral `cache_control` markers, and stage-specific deadlines managed in `model_timeout.rs`. For details, see [Token Budgets, Prompt Caching and Timeouts](#3.2).
*Sources: [src/config.rs:97-118](), [src/api.rs:13-14]() *

### 3.3 Repository Tool Loop
Models are granted access to a sandboxed suite of repository exploration and modification tools (`grep_repo`, `read_files`, `read_symbol`, `git_*`, `rg`, `edit_file`). The inference layer manages multi-turn round-trips and enforces post-execution verification constraints via `ToolVerification`. For details, see [Repository Tool Loop](#3.3).
*Sources: [src/api.rs:130-154]() *

### 3.4 Payload Builders and Response Parsers
Each review stage constructs user payloads dynamically using reference contexts built by `build_reference_context` [src/prompts.rs:61-181](). Strict JSON parsers and validators enforce schemas for concerns, findings, and summaries. For details, see [Payload Builders and Response Parsers](#3.4).
*Sources: [src/api.rs:27-45](), [src/prompts.rs:61-181]() *

---

## Inference Execution Flow

The following diagram illustrates how review stages and tool invocations map to underlying execution routines within the inference codebase.

```mermaid
title "Inference Layer Execution Path"
graph TD
    Stage["Review Stage Execution"] --> BuildPayload["build_reference_context src/prompts.rs:61-181"]
    BuildPayload --> ChatComp["chat_completion src/api.rs"]
    ChatComp --> ToolCheck{"Tool Calls Requested?"}
    ToolCheck -->|Yes| ExecTool["tools::execute_tool src/api.rs"]
    ExecTool --> ChatComp
    ToolCheck -->|No| ParseResp["Strict JSON Parser src/api.rs"]
    ParseResp --> Findings["Validated Findings Array"]
```
*Sources: [src/api.rs:130-154](), [src/prompts.rs:61-181]() *

---

