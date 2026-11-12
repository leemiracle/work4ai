<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/SkillOpt · page 5 Model Backends and LLM Integration · fetched 2026-10-26 -->

# Model Backends and LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/eval_only.py](scripts/eval_only.py)
- [scripts/train.py](scripts/train.py)
- [skillopt/model/__init__.py](skillopt/model/__init__.py)
- [skillopt/model/backend_config.py](skillopt/model/backend_config.py)
- [skillopt/model/codex_backend.py](skillopt/model/codex_backend.py)
- [skillopt/model/codex_harness.py](skillopt/model/codex_harness.py)
- [skillopt/model/common.py](skillopt/model/common.py)
- [skillopt/model/copilot_backend.py](skillopt/model/copilot_backend.py)
- [skillopt/model/minimax_backend.py](skillopt/model/minimax_backend.py)
- [tests/test_codex_config_aliases.py](tests/test_codex_config_aliases.py)
- [tests/test_codex_optimizer_backend.py](tests/test_codex_optimizer_backend.py)
- [tests/test_copilot_exec_backend.py](tests/test_copilot_exec_backend.py)
- [tests/test_copilot_tool_scope.py](tests/test_copilot_tool_scope.py)
- [tests/test_minimax_backend.py](tests/test_minimax_backend.py)
- [tests/test_role_backend_resolution.py](tests/test_role_backend_resolution.py)

</details>



The model layer in SkillOpt provides a unified interface for interacting with various Large Language Models (LLMs) and execution harnesses. It abstracts API providers, authentication mechanisms, and execution environments, allowing the core training pipeline to remain model-agnostic. For details on specific providers, see [Azure OpenAI and OpenAI-Compatible Backends](#5.1) and [Execution Harness Backends (Codex, Claude Code, Cursor, Copilot)](#5.2).

Sources: `[skillopt/model/__init__.py:1-91]()`, `[skillopt/model/backend_config.py:1-55]()`

## Dual-Deployment Architecture

SkillOpt implements a dual-deployment pattern separating the **Optimizer Model** from the **Target Model** [skillopt/model/__init__.py:28-68](). This architecture allows operators to deploy a high-reasoning model (such as GPT-4o or Claude Sonnet) for gradient reflection and patch aggregation, while assigning task rollouts to a specialized rollout model or execution harness [skillopt/model/backend_config.py:139-169]().

The backend router (`skillopt.model`) inspects environment variables and configuration dictionaries via `backend_config.py` to dispatch optimizer and target calls independently [skillopt/model/backend_config.py:51-52]().

**Model Routing and Dispatch Flow**
```mermaid
graph TD
    ENV[""Environment Variables (OPTIMIZER_BACKEND, TARGET_BACKEND)""] --> BC[""backend_config.py:set_optimizer_backend()""]
    BC --> INIT[""skillopt.model.__init__.py""]
    
    subgraph "Dispatch Logic"
    INIT -->|""chat_optimizer()""| OP[""Optimizer Dispatcher""]
    INIT -->|""chat_target()""| TG[""Target Dispatcher""]
    end

    OP -->|""Route""| AO_OP[""azure_openai.py""]
    OP -->|""Route""| CL_OP[""claude_backend.py""]
    OP -->|""Route""| QW_OP[""qwen_backend.py""]

    TG -->|""Route""| AO_TG[""azure_openai.py""]
    TG -->|""Route""| CX_TG[""codex_backend.py""]
    TG -->|""Route""| CP_TG[""copilot_backend.py""]
```
Sources: `[skillopt/model/backend_config.py:51-169]`, `[skillopt/model/__init__.py:121-200]`

## Token Tracking and Common Utilities

The `skillopt.model.common` module defines core classes shared across all backends [skillopt/model/common.py:1-204](). 

- **`TokenTracker`**: A thread-safe class that records `prompt_tokens` and `completion_tokens` bucketed by execution stage (e.g., `"optimizer"`, `"target"`, `"gate"`, `"meta_skill"`) [skillopt/model/common.py:87-128]().
- **Compatibility Layers**: Normalizes different API formats into structured `CompatAssistantMessage`, `CompatToolCall`, and `CompatToolFunction` objects [skillopt/model/common.py:137-176]().
- **Default Models**: Establishes standard fallback models via `default_model_for_backend()` [skillopt/model/common.py:18-34]().

**Code Entity Mapping: Common Utilities and Token Tracking**
```mermaid
graph LR
    subgraph "Code Entity Space (skillopt/model/common.py)"
        TT[""TokenTracker""]
        CAM[""CompatAssistantMessage""]
        CTC[""CompatToolCall""]
        CTF[""CompatToolFunction""]
        NORM[""normalize_backend_name()""]
    end

    subgraph "Backend Integration"
        MM[""minimax_backend.py""] -->|""TokenTracker""| TT
        QW[""qwen_backend.py""] -->|""TokenTracker""| TT
        CX[""codex_backend.py""] -->|""CompatAssistantMessage""| CAM
    end
```
Sources: `[skillopt/model/common.py:18-176]`, `[skillopt/model/minimax_backend.py:102]`, `[skillopt/model/qwen_backend.py:34]`

## Overview of Backend Categories

SkillOpt groups backends into two primary families: standard chat completion APIs and execution harnesses.

### Azure OpenAI and OpenAI-Compatible Backends
Provides support for OpenAI, Azure OpenAI Service, DeepSeek, vLLM, Ollama, Qwen, and MiniMax endpoints [skillopt/model/__init__.py:7-14](). Supports advanced authentication modes, custom base URLs, and retry policies [skillopt/model/minimax_backend.py:23-55]().
For details, see [Azure OpenAI and OpenAI-Compatible Backends](#5.1).

### Execution Harness Backends
Wraps local CLI tools and SDK agents (`codex_harness`, Claude Code, Cursor, Copilot) to execute tasks inside isolated workspaces with sandbox and approval policies [skillopt/model/codex_harness.py:96-185](), [skillopt/model/backend_config.py:54-80]().
For details, see [Execution Harness Backends (Codex, Claude Code, Cursor, Copilot)](#5.2).

Sources: `[skillopt/model/__init__.py:7-14]()`, `[skillopt/model/codex_harness.py:96-185]()`, `[skillopt/model/backend_config.py:54-80]()`

---

