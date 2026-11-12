<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/llm.nvim · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [lua/llm/init.lua](lua/llm/init.lua)

</details>



## Purpose and Scope

This document provides a high-level overview of LLM.nvim's internal architecture, explaining how its components interact with each other and with external systems. The focus is on the core systems, their relationships, and the plugin's integration points with Neovim and language model backends.

For detailed configuration information, see [Configuration](#2). For in-depth explanations of the language server integration and completion system, see [Language Server Integration](#3.1) and [Completion System](#3.2) respectively.

## High-Level System Architecture

LLM.nvim follows a modular architecture with clear separation of concerns. The plugin acts as a bridge between Neovim and various large language model providers through the llm-ls language server.

### Core Component Relationships Diagram

```mermaid
graph TD
    Init["llm/init.lua"] --> Config["llm/config.lua"]
    Init --> LanguageServer["llm/language_server.lua"]
    Init --> Completion["llm/completion.lua"]
    Init --> Keymaps["llm/keymaps.lua"]
    
    LanguageServer --> Config
    Completion --> LanguageServer
    Completion --> Config
    Keymaps --> Completion
    Keymaps --> Config
    
    LanguageServer --> Utils["llm/utils.lua"]
    Completion --> Utils
```

Sources: [lua/llm/init.lua:1-5]()

The plugin is structured around several key modules:

| Module | Responsibility |
|--------|----------------|
| `init.lua` | Entry point and orchestration of plugin setup |
| `config.lua` | Configuration management and validation |
| `language_server.lua` | Integration with llm-ls language server |
| `completion.lua` | Suggestion and completion functionality |
| `keymaps.lua` | Keyboard shortcut handling |
| `utils.lua` | Shared utility functions |

### Integration Architecture

```mermaid
graph TD
    Neovim["Neovim Editor"] -->|"Loads"| Plugin["llm.nvim Plugin"]
    Plugin -->|"Uses"| LLMLS["llm-ls Language Server"]
    LLMLS -->|"HTTP Requests"| Backends{"LLM Backends"}
    Backends -->|"Option 1"| HF["Hugging Face Inference API"]
    Backends -->|"Option 2"| Ollama["Ollama"]
    Backends -->|"Option 3"| OpenAI["OpenAI"]
    Backends -->|"Option 4"| TGI["Text Generation Inference"]
    
    Plugin -->|"Shows"| GhostText["Ghost Text Completions"]
    GhostText -->|"Accept with"| AcceptKey["accept_keymap (<Tab>)"]
    GhostText -->|"Dismiss with"| DismissKey["dismiss_keymap (<S-Tab>)"]
```

Sources: [README.md:16-26](), [README.md:34-129]()

## Initialization Process

The initialization process begins when the user calls `require('llm').setup(opts)` in their Neovim configuration.

### Setup Flow Diagram

```mermaid
flowchart TD
    SetupFunc["M.setup(opts)"] --> SetupCheck{"setup_done?"}
    SetupCheck -->|"Yes"| ReturnEarly["Return early"]
    SetupCheck -->|"No"| CreateCmds["create_cmds()"]
    CreateCmds --> ConfigSetup["config.setup(opts)"]
    ConfigSetup --> LSSetup["llm_ls.setup()"]
    LSSetup --> CompletionSetup["completion.setup()"]
    CompletionSetup --> CreateAutocmds["completion.create_autocmds()"]
    CreateAutocmds --> KeymapsSetup["keymaps.setup()"]
    KeymapsSetup --> MarkDone["M.setup_done = true"]
```

Sources: [lua/llm/init.lua:18-35]()

The setup process:
1. Creates user commands (`LLMToggleAutoSuggest`, `LLMSuggestion`)
2. Initializes configuration with user options
3. Sets up the language server connection
4. Configures the completion system
5. Creates necessary autocommands
6. Sets up keymaps for accepting/dismissing suggestions

### Language Server Setup Process

```mermaid
flowchart TD
    LSSetup["llm_ls.setup()"] --> LSCheck{"Setup done?"}
    LSCheck -->|"Yes"| LSReturnEarly["Return early"]
    LSCheck -->|"No"| HostPortCheck{"Host & Port configured?"}
    
    HostPortCheck -->|"Yes"| ConnectRPC["Connect via RPC"]
    HostPortCheck -->|"No"| BinaryCheck{"Binary exists?"}
    
    BinaryCheck -->|"Yes"| UseBinary["Use existing binary"]
    BinaryCheck -->|"No"| DownloadBinary["Download llm-ls binary"]
    DownloadBinary --> DownloadCheck{"Download successful?"}
    
    DownloadCheck -->|"No"| NotifyError["Notify error"]
    DownloadCheck -->|"Yes"| UseBinary
    
    ConnectRPC --> StartClient["Start LSP client"]
    UseBinary --> StartClient
    
    StartClient --> ClientCheck{"Client started?"}
    ClientCheck -->|"No"| NotifyError
    ClientCheck -->|"Yes"| CreateLSAutocommands["Create autocommands"]
    
    CreateLSAutocommands --> SetClientId["Set client_id"]
    SetClientId --> MarkLSDone["Mark setup as done"]
```

Sources: [README.md:177-208]()

The language server setup process:
1. Connects to an existing llm-ls instance if host and port are configured
2. Otherwise checks for an existing binary or downloads it
3. Starts the LSP client
4. Creates autocommands for buffer attachment
5. Stores the client ID for future communication

## Completion Request Flow

The completion system is the core functionality of the plugin, responsible for requesting and displaying suggestions.

```mermaid
sequenceDiagram
    participant User
    participant Neovim as "Neovim Editor"
    participant Completion as "llm/completion.lua"
    participant LS as "llm/language_server.lua"
    participant LLMLS as "llm-ls Process"
    participant LLM as "LLM Backend"
    
    User->>Neovim: Types in insert mode
    Neovim->>Completion: CursorMovedI event
    Completion->>Completion: M.schedule()
    Note over Completion: Debounces for config.debounce_ms
    Completion->>LS: M.lsp_suggest()
    LS->>LLMLS: llm-ls/getCompletions request
    LLMLS->>LLM: HTTP request with context
    LLM->>LLMLS: Returns completion
    LLMLS->>LS: Returns formatted result
    LS->>Completion: Returns completion
    Completion->>Neovim: Display as ghost text
    
    alt User accepts suggestion
        User->>Neovim: Press accept_keymap
        Neovim->>Completion: complete()
        Completion->>LS: accept_completion()
        LS->>LLMLS: llm-ls/acceptCompletion
    else User rejects suggestion
        User->>Neovim: Press dismiss_keymap/move cursor
        Neovim->>Completion: reject()
        Completion->>LS: reject_completion()
        LS->>LLMLS: llm-ls/rejectCompletion
    end
```

Sources: [lua/llm/init.lua:1-5](), [README.md:248-255]()

The completion flow:
1. User input triggers the `CursorMovedI` event
2. The completion system debounces rapid input
3. When ready, it requests a suggestion from the language server
4. The language server forwards the request to llm-ls
5. llm-ls communicates with the configured LLM backend
6. The response is processed and displayed as ghost text
7. The user can accept or dismiss the suggestion

## Backend Integration

LLM.nvim supports multiple backend providers through a unified interface handled by llm-ls.

### Supported Backends

| Backend | API Endpoint | Description |
|---------|--------------|-------------|
| `huggingface` | `/model/{model}` | Hugging Face Inference API |
| `ollama` | `/api/generate` | Local LLM server |
| `openai` | `/v1/completions` | OpenAI compatible APIs |
| `tgi` | `/generate` | Text Generation Inference |

Sources: [README.md:34-129]()

### Context Window Management

```mermaid
graph TD
    UserInput["User Input"] --> Tokenization["Tokenization"]
    Tokenization --> ContextWindow["Context Window Fitting"]
    ContextWindow --> PromptConstruction["Prompt Construction"]
    PromptConstruction --> Request["Backend Request"]
    
    Tokenization -->|"Uses"| TokenizerConfig["Tokenizer Configuration"]
    ContextWindow -->|"Limited by"| MaxTokens["context_window setting"]
    PromptConstruction -->|"May use"| FIMSupport["Fill-in-the-Middle (FIM)"]
```

Sources: [README.md:130-171](), [README.md:209-246]()

The plugin ensures that prompts fit within the model's context window by:
1. Tokenizing content using the configured tokenizer
2. Truncating context to fit within the `context_window` limit
3. Constructing the prompt, potentially with Fill-in-the-Middle support
4. Sending the request to the backend with appropriate parameters

## Command and Keymap Integration

LLM.nvim provides user commands and keymaps to control its behavior:

| Command | Function | Description |
|---------|----------|-------------|
| `LLMToggleAutoSuggest` | `completion.toggle_suggestion()` | Enable/disable automatic suggestions |
| `LLMSuggestion` | `completion.lsp_suggest()` | Manually request a suggestion |

Sources: [lua/llm/init.lua:8-16](), [README.md:257-263]()

Default keymaps are configured in `keymaps.setup()` and are customizable through configuration:
- Accept suggestion: `<Tab>` (configurable via `accept_keymap`)
- Dismiss suggestion: `<S-Tab>` (configurable via `dismiss_keymap`)

## Summary

LLM.nvim follows a modular architecture that separates concerns into distinct components:

1. **Configuration Management**: Handles user settings and defaults
2. **Language Server Integration**: Bridges Neovim and LLM backends
3. **Completion System**: Manages the core suggestion functionality
4. **Keymap Handling**: Controls user interaction with suggestions

This design allows the plugin to adapt to different LLM backends while maintaining a consistent interface for users. The clear separation of responsibilities makes the codebase more maintainable and extensible.

---

