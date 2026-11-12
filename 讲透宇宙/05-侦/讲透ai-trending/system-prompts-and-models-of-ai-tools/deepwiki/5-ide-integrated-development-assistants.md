<!-- source: DeepWiki mcp.deepwiki.com · repo x1xhlol/system-prompts-and-models-of-ai-tools · page 5 IDE-Integrated Development Assistants · fetched 2026-10-30 -->

# IDE-Integrated Development Assistants

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Amp/README.md](Amp/README.md)
- [Amp/claude-4-sonnet.yaml](Amp/claude-4-sonnet.yaml)
- [Cursor Prompts/Agent Prompt v1.2.txt](Cursor Prompts/Agent Prompt v1.2.txt)
- [VSCode Agent/Prompt.txt](VSCode Agent/Prompt.txt)

</details>



This page introduces various AI coding assistants designed to integrate directly with Integrated Development Environments (IDEs). These tools enhance developer productivity by providing capabilities such as code generation, refactoring, debugging, and context-aware assistance directly within the coding environment.

The assistants covered include:
- **Cursor**: An IDE built around AI-first principles, offering advanced prompting and agentic capabilities.
- **VSCode Agent (GitHub Copilot)**: Microsoft's implementation of an AI assistant within VSCode, focusing on context gathering and strict tool-based editing.
- **Windsurf Cascade System**: An AI Flow paradigm assistant with a rich set of tools for browser interaction, file operations, and deployment.
- **Amp by Sourcegraph**: An AI coding agent featuring an Oracle AI advisor and sub-agent delegation for complex tasks.
- **Claude Code by Anthropic**: A tool-based coding CLI with specialized sub-agents and comprehensive file/execution capabilities.
- **Augment Code**: An assistant with per-model prompts and tools, allowing for tailored AI interactions.
- **Trae**: An AI Flow paradigm assistant offering distinct chat and builder modes.
- **CodeBuddy**: An assistant with chat and craft prompts for varied coding tasks.
- **Junie**: JetBrains' AI assistant, integrated into their suite of IDEs.
- **Xcode Intelligence Action Prompts**: Apple's AI assistance within Xcode, providing Swift-focused help through various action prompts.

This page provides a high-level overview of each, with links to dedicated child pages for in-depth technical details.

---

## 5.1. VSCode Agent (GitHub Copilot)

The VSCode Agent, an implementation of GitHub Copilot, operates as a sophisticated AI programming assistant directly within Visual Studio Code. Its core philosophy emphasizes thorough context gathering before executing any actions and strictly adheres to tool-based file editing. The agent is designed to be highly autonomous, taking initiative to resolve user queries using its available tools.

Key aspects of the VSCode Agent include:
- **Identity and Instructions**: It identifies as "GitHub Copilot" and follows user requirements carefully, adhering to Microsoft content policies and avoiding harmful or copyrighted content [VSCode Agent/Prompt.txt:3-10]().
- **Context Gathering**: The agent prioritizes gathering context, preferring `semantic_search` for broad queries and avoiding assumptions [VSCode Agent/Prompt.txt:18-20]().
- **Tool-Based Editing**: All file modifications are performed using the `insert_edit_into_file` tool, with strict rules against directly printing code blocks for changes [VSCode Agent/Prompt.txt:23, 41-45]().
- **Validation Workflow**: After any file edit, the agent is mandated to call `get_errors` to validate changes and fix relevant issues [VSCode Agent/Prompt.txt:48]().

For detailed information on its architecture, tool categories, context discovery, file editing workflow, and model-specific variants, see [VSCode Agent (GitHub Copilot)](#5.1).

Sources: [VSCode Agent/Prompt.txt:1-405]()

---

## 5.2. Windsurf Cascade System

Windsurf, also known as Cascade, is an AI Flow paradigm assistant that integrates deeply within the IDE environment. It boasts an extensive tool ecosystem with over 30 tools, enabling a wide range of capabilities from browser interaction to deployment. The system is designed to operate with an "AI Flow" model, allowing for independent and collaborative work across various development tasks.

Key features of the Windsurf Cascade System include:
- **Comprehensive Tool Suite**: Tools cover browser interaction (`browser_preview`, `open_browser_url`), file system operations (`list_dir`, `write_to_file`, `replace_file_content`), deployment (`deploy_web_app`), command execution (`run_command`), and memory management (`create_memory`) [Windsurf/Tools Wave 11.txt:1-300]().
- **AI Flow Paradigm**: This operational model allows the system to manage complex workflows, making decisions and executing tasks autonomously or with user guidance.
- **Safety Mechanisms**: Command execution includes `SafeToAutoRun` flags to ensure user approval for potentially destructive operations [Windsurf/Tools Wave 11.txt:277-278]().
- **Structured File Editing**: The `replace_file_content` tool uses `ReplacementChunks` for precise, multi-part file modifications [Windsurf/Tools Wave 11.txt:231-260]().

For an in-depth look at its AI Flow paradigm, tool ecosystem, browser interaction capabilities, code search, file editing, deployment pipeline, and memory system, see [Windsurf Cascade System](#5.2).

Sources: [Windsurf/Tools Wave 11.txt:1-300]()

---

## 5.3. Amp by Sourcegraph

Amp is Sourcegraph's AI coding agent, distinguished by its sophisticated sub-agent delegation model and an "Oracle" AI advisor. It integrates with IDEs like VSCode and allows for fine-grained control over LLM configurations through YAML files. Amp is designed to handle complex software engineering tasks by breaking them down and delegating to specialized agents.

Core components of Amp include:
- **Oracle AI Advisor**: Utilizes a powerful reasoning model (e.g., OpenAI o3) for high-level planning, code reviews, debugging, and architectural guidance [Amp/gpt-5.yaml:254-270]().
- **Sub-agent Delegation**: The `Task` tool allows the main agent to launch specialized sub-agents for heavy implementations, while `codebase_search_agent` handles intelligent conceptual searches [Amp/gpt-5.yaml:235-252, 761-828]().
- **LLM-Specific Configurations**: Prompts and behaviors are configured via YAML files (e.g., `claude-4-sonnet.yaml`, `gpt-5.yaml`), allowing for tailored interactions based on the underlying LLM [Amp/README.md:13-20]().
- **Tool Suite and Guardrails**: Amp provides a comprehensive set of tools for Bash execution, file operations (`create_file`, `edit_file`, `Read`, `Write`), search (`glob`, `Grep`), and diagnostics (`get_diagnostics`), all governed by quality gates and verification sequences [Amp/gpt-5.yaml:620-1140]().

For a detailed exploration of Amp's system overview, LLM configuration, Oracle advisor, sub-agent delegation, tool suite, and guardrails, see [Amp by Sourcegraph](#5.3).

Sources: [Amp/README.md:1-20](), [Amp/claude-4-sonnet.yaml:1-2175](), [Amp/gpt-5.yaml:1-1140]()

---

## 5.4. Cursor Prompts Across Versions

Cursor is an AI-first IDE that provides a unique approach to AI assistance through its evolving prompt family and agent tool schema. It focuses on deep integration with the user's coding context, including open files, cursor position, edit history, and linter errors, to provide highly relevant assistance.

Key aspects of Cursor's AI capabilities include:
- **Prompt Evolution**: Cursor's agent prompts have evolved across versions (v1.0, v1.2, 2.0, 2025-09-03), refining its tone, tool-calling rules, code citation formats, and autonomy [Cursor Prompts/Agent Prompt v1.2.txt:1-68]().
- **Agent Tool Schema**: A defined JSON schema governs the tools available to the agent, ensuring structured and predictable interactions.
- **Context Maximization**: The agent is instructed to be "THOROUGH when gathering information" and to "TRACE every symbol back to its definitions and usages" to fully understand the context [Cursor Prompts/Agent Prompt v1.2.txt:29-31]().
- **Code Change Protocol**: When making code changes, Cursor agents are strictly instructed to use code edit tools rather than outputting code directly to the user, and to ensure generated code is immediately runnable [Cursor Prompts/Agent Prompt v1.2.txt:44-47]().

For a comprehensive understanding of Cursor's agent prompt evolution, tool schema, and its distinct chat and CLI modes, see [Cursor Prompts Across Versions](#5.4).

Sources: [Cursor Prompts/Agent Prompt v1.2.txt:1-569]()

---

## 5.5. Augment Code, Trae, CodeBuddy and Junie

This section provides an overview of several other IDE-integrated AI assistants, each with unique features and operational models. These tools demonstrate the diversity in approaches to AI-powered coding assistance.

- **Augment Code**: This assistant features dual-model prompts, with distinct configurations for models like `gpt-5` and `claude-4-sonnet`. It provides tailored tools and behaviors depending on the chosen underlying AI model, allowing for optimized performance and interaction styles for different tasks.
- **Trae**: Operating under an "AI Flow" paradigm, Trae offers both a chat mode for conversational assistance and a builder mode for structured task execution. Its builder prompt and tool schema enable it to construct and execute complex development workflows.
- **CodeBuddy**: This assistant provides "Chat" and "Craft" prompts. The Chat prompt is likely for general conversational assistance, while the Craft prompt suggests a focus on more structured code generation or modification tasks, possibly with specific constraints or templates.
- **Junie**: JetBrains' AI assistant, Junie, is integrated into their suite of IDEs (e.g., IntelliJ IDEA, PyCharm). It provides context-aware assistance, code completion, and other AI-driven features directly within the JetBrains ecosystem, leveraging the IDE's deep understanding of project structure and code semantics.

For more detailed information on Augment Code's per-model prompts and tools, Trae's chat and builder modes, CodeBuddy's chat and craft prompts, and JetBrains Junie, see [Augment Code, Trae, CodeBuddy and Junie](#5.5).

---

## 5.6. Xcode Intelligence Action Prompts

Apple's Xcode IDE incorporates AI assistance through a family of "Intelligence Action Prompts," designed to provide Swift-focused help. These prompts extend a base `System.txt` prompt with specialized instructions for various development actions, enhancing productivity within the Xcode environment.

The Xcode Intelligence Action Prompts include:
- **System.txt**: The foundational prompt that establishes the AI's core identity and general guidelines for assistance within Xcode.
- **Document**: A prompt specifically tailored to help developers generate documentation for Swift code, functions, classes, and modules.
- **Explain**: This prompt assists in understanding complex Swift code snippets, providing explanations of logic, purpose, and potential issues.
- **Message**: Likely used for generating commit messages, code review comments, or other textual communications related to the codebase.
- **Playground**: A prompt designed to assist with Swift Playgrounds, enabling interactive code experimentation and learning.
- **Preview**: This prompt probably helps in generating UI previews for Swift/SwiftUI code, assisting with visual development and layout.

These action-specific prompts allow Xcode's AI to provide highly contextual and relevant assistance for common developer tasks in the Swift ecosystem.

For a detailed breakdown of Xcode's prompt family, including the base `System.txt` and the various action prompts, see [Xcode Intelligence Action Prompts](#5.6).

---

