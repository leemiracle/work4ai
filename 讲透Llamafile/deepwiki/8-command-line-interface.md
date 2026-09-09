> 来源: [https://deepwiki.com/mozilla-ai/llamafile/8-command-line-interface](https://deepwiki.com/mozilla-ai/llamafile/8-command-line-interface)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Command Line Interface

  Relevant source files 
 - [llamafile/bestline.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.c)
 - [llamafile/bestline.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.h)
 - [llamafile/chatbot_api.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp)
 - [llamafile/chatbot_hint.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hint.cpp)
 - [llamafile/chatbot_hist.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hist.cpp)
 - [llamafile/chatbot_main.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp)
 - [llamafile/chatbot_repl.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp)
 
  This page documents llamafile's Command Line Interface (CLI), which provides an interactive text generation session. The CLI is built on the **chatbot REPL** system and uses the **bestline** library for advanced line editing, history management, and UTF-8 support.

 
## Overview

 The CLI mode allows users to chat with Large Language Models directly from the terminal. Since version 0.10.0, the CLI is part of a unified execution system that supports different backends (local inference or API-based). The interface provides a persistent history, multi-line input support, and a rich set of slash commands (e.g., `/help`, `/undo`, `/upload`). [llamafile/chatbot_hint.cpp37-51](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hint.cpp#L37-L51)

 **Key components of the CLI:**

 
 - **[Bestline Library](https://deepwiki.com/mozilla-ai/llamafile/8.1-bestline-library)**: A lightweight, readline-compatible library providing ANSI terminal control, UTF-8 editing, and a kill ring. [llamafile/bestline.c8-14](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.c#L8-L14)
 - **[Chatbot REPL and Execution Modes](https://deepwiki.com/mozilla-ai/llamafile/8.2-chatbot-repl-and-execution-modes)**: The high-level logic managing conversation history, role-playing (user/assistant/system), and backend dispatching. [llamafile/chatbot_repl.cpp154-207](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L154-L207)
 - **[Syntax Highlighting](https://deepwiki.com/mozilla-ai/llamafile/8.3-syntax-highlighting)**: Integrated TUI highlighting for code blocks and markdown using `HighlightMarkdown` and `ColorBleeder`. [llamafile/chatbot_repl.cpp173-175](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L173-L175)
 
 Sources: [llamafile/chatbot_repl.cpp19-35](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L19-L35) [llamafile/bestline.c5-15](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.c#L5-L15) [llamafile/chatbot_hint.cpp37-51](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hint.cpp#L37-L51)

 
## Architecture

 The CLI bridges user input from the terminal to the underlying inference engine through a layered architecture. It supports execution modes defined by `ProgramMode`, which dictates whether the REPL communicates with a local model or a remote server. [llamafile/chatbot_api.cpp37-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L37-L40)

 
### CLI System Structure

 
```

```

 **CLI to Code Entity Association**: The `repl()` function in [llamafile/chatbot_repl.cpp154](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L154-L154) serves as the main loop, calling `bestlineWithHistory()` [llamafile/bestline.h27](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.h#L27-L27) to capture input. The `ChatBackend` [llamafile/chatbot_backend.h20](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_backend.h#L20-L20) (abstract base class) facilitates polymorphic dispatch to either `DirectBackend` (local llama.cpp context) or `ApiBackend` [llamafile/chatbot_api.cpp37](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L37-L37) (OpenAI-compatible HTTP client).

 Sources: [llamafile/chatbot_repl.cpp152-207](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L152-L207) [llamafile/bestline.h23-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.h#L23-L40) [llamafile/chatbot_api.cpp37-54](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L37-L54)

 
## Interactive Features

 
### Line Editing and History

 The CLI uses `bestline` to provide a modern terminal experience. It supports standard GNU readline shortcuts (e.g., `CTRL-A` for start of line, `CTRL-R` for reverse history search) and handles complex UTF-8 characters including emojis and non-Latin scripts. [llamafile/bestline.c52-95](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.c#L52-L95)

 
 - **Persistent History**: Managed via `bestlineHistoryLoad()` and `bestlineHistorySave()`. [llamafile/bestline.h29-30](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.h#L29-L30)
 - **LLM Optimization**: `bestlineLlamaMode(true)` [llamafile/bestline.h38](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.h#L38-L38) is enabled to tune the editor for long-form LLM prompts, specifically handling indentation and multi-line submissions. [llamafile/chatbot_repl.cpp195](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L195-L195)
 - **Tab Completion**: The `on_completion` and `on_hint` callbacks provide interactive command discovery for slash commands like `/forget` or `/undo`. [llamafile/chatbot_hint.cpp27-72](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hint.cpp#L27-L72)
 
 Sources: [llamafile/bestline.c52-95](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.c#L52-L95) [llamafile/chatbot_repl.cpp189-200](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L189-L200) [llamafile/chatbot_hint.cpp27-72](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hint.cpp#L27-L72)

 
### Execution State Management

 The CLI tracks the conversation state using several global vectors to support advanced features like undo and context forgetting.

 
| Entity | Type | Role |
|---|---|---|
| g_messages | std::vector<common_chat_msg> | High-level chat history for templates. llamafile/chatbot_hist.cpp35 |
| g_history | std::vector<int> | Token-level history for local inference. llamafile/chatbot_hist.cpp38 |
| g_undo | std::vector<int> | Stack of token positions for the /undo command. llamafile/chatbot_hist.cpp37 |
| g_role | enum Role | Current speaker (User, Assistant, System). llamafile/chatbot_hist.cpp34 |

 Sources: [llamafile/chatbot_hist.cpp33-51](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hist.cpp#L33-L51) [llamafile/chatbot_hist.cpp181-193](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hist.cpp#L181-L193)

 
## Execution Flow

 When a user submits a line in the REPL, the following sequence occurs:

 
```

```

 **Reasoning Support**: The CLI implements `apply_chat_template_with_thinking` to honor `--reasoning` flags for models like Qwen3.5 or DeepSeek, enabling or disabling `<thought>` blocks. [llamafile/chatbot_repl.cpp67-90](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L67-L90) It also uses `maintain_faint_styling` to ensure reasoning content remains visually distinct (dimmed) even when internal markdown highlighting resets terminal attributes. [llamafile/chatbot_repl.cpp47-62](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L47-L62)

 Sources: [llamafile/chatbot_repl.cpp47-90](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L47-L90) [llamafile/chatbot_repl.cpp193-207](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L193-L207)

 
## Platform Support

 The CLI is designed to be highly portable, leveraging **Cosmopolitan Libc** to run across multiple operating systems with a single binary.

 
 - **Platform Support**: Runs on Linux, macOS, Windows (CMD.EXE or MinTTY), and BSDs. [llamafile/bestline.c49-50](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.c#L49-L50)
 - **Signal Handling**: Correctly handles `SIGINT` (CTRL-C) via `on_sigint` to interrupt current generation and return to the prompt without exiting the application. [llamafile/chatbot_repl.cpp92-94](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L92-L94)
 - **Multimodal Support**: Supports the `/upload` command to inject image data into the conversation history, which `ApiBackend` converts into OpenAI-compatible `image_url` parts. [llamafile/chatbot_api.cpp58-102](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L58-L102)
 
 Sources: [llamafile/bestline.c49-50](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/bestline.c#L49-L50) [llamafile/chatbot_repl.cpp92-94](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L92-L94) [llamafile/chatbot_api.cpp58-102](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L58-L102)

 
## Sub-Pages

 For deeper technical details on the CLI components, see the following child pages:

 
 - **[Bestline Library](https://deepwiki.com/mozilla-ai/llamafile/8.1-bestline-library)**: Details on the ANSI terminal control, UTF-8 editing logic, and the kill ring implementation. Covers `bestline.c` and `bestline.h`.
 - **[Chatbot REPL and Execution Modes](https://deepwiki.com/mozilla-ai/llamafile/8.2-chatbot-repl-and-execution-modes)**: Details on the `ProgramMode` logic, the `ChatBackend` abstraction (`DirectBackend` vs `ApiBackend`), history management, and reasoning filters. Covers `chatbot_repl.cpp`, `chatbot_main.cpp`, `chatbot_hist.cpp`, and `chatbot_api.cpp`.
 - **[Syntax Highlighting](https://deepwiki.com/mozilla-ai/llamafile/8.3-syntax-highlighting)**: Details on the TUI highlighting subsystem and language-specific highlighters. Covers `llamafile/highlight/`.
