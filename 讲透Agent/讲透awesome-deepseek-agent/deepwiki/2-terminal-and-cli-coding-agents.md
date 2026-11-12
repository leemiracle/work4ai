> 来源: [https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2-terminal-and-cli-coding-agents](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2-terminal-and-cli-coding-agents)
> DeepWiki deepseek-ai/awesome-deepseek-agent

# Terminal & CLI Coding Agents

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1)
 - [docs/assets/claude_code_vsc_ext.png](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/assets/claude_code_vsc_ext.png)
 - [docs/claude_code.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/claude_code.md?plain=1)
 - [docs/deepseek-tui.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-tui.md?plain=1)
 - [docs/deepseek-tui.zh-CN.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-tui.zh-CN.md?plain=1)
 
  This section provides an overview of terminal-native AI coding assistants integrated with DeepSeek V4 models. These tools prioritize speed, keyboard-driven workflows, and direct interaction with local file systems and shell environments.

 
## Overview of CLI Agents

 Terminal agents typically operate as standalone binaries or Node.js packages that leverage DeepSeek's 1M context window and reasoning capabilities to perform multi-step coding tasks. They often include features such as:

 
 - **Sandboxed Execution:** Securely running shell commands or Python REPLs.
 - **Tool Calling:** Automatically reading, writing, and searching files.
 - **Reasoning Control:** Toggling between high-speed "Flash" models and high-effort "Pro" reasoning modes.
 
 
### Agent to Code Space Mapping

 The following diagram illustrates how CLI agent systems interact with specific code entities and local resources.

 **System to Entity Association**

 
```

```

 Sources: [docs/deepseek-tui.md32](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-tui.md?plain=1#L32-L32) [docs/deepseek-tui.md78-82](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-tui.md?plain=1#L78-L82) [docs/claude_code.md41](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/claude_code.md?plain=1#L41-L41) [README.md20-36](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L20-L36)

 
---

 
## Tool Integration Guides

 
### Claude Code

 Claude Code is a terminal-native assistant that can be configured to use DeepSeek via an Anthropic-compatible endpoint. Key configurations include setting the `ANTHROPIC_BASE_URL` to `https://api.deepseek.com/anthropic` and utilizing the `[1m]` context suffix for model identifiers.

 
 - **Key Files:** `~/.claude/settings.json` [docs/claude_code.md41](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/claude_code.md?plain=1#L41-L41)
 - **Critical Env:** `CLAUDE_CODE_EFFORT_LEVEL=max` [docs/claude_code.md57](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/claude_code.md?plain=1#L57-L57)
 - For details, see [Claude Code](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2.1-claude-code).
 
 
### DeepSeek-TUI

 A Rust-based assistant built as a 13-crate workspace. It supports native sandboxing on macOS, Linux, and Windows and features a TUI with three distinct modes: Plan, Agent, and YOLO.

 
 - **Key Command:** `deepseek auth` [docs/deepseek-tui.md32](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-tui.md?plain=1#L32-L32)
 - **Key Logic:** `Shift+Tab` cycles reasoning effort [docs/deepseek-tui.md43](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-tui.md?plain=1#L43-L43)
 - For details, see [DeepSeek-TUI](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2.2-deepseek-tui).
 
 
### Deep Code

 An open-source terminal assistant specifically optimized for DeepSeek-V4. It features a discovery mechanism for "Agent Skills" stored in project-level or user-level markdown files.

 
 - **Key File:** `~/.deepcode/settings.json` [README.md23](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L23-L23)
 - For details, see [Deep Code](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2.3-deep-code).
 
 
### Reasonix

 A DeepSeek-native agent emphasizing a "cache-first" loop and "flash-first" cost control. It is designed to be MCP-native from the ground up.

 
 - **Key Command:** `npx reasonix code` [README.md36](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L36-L36)
 - For details, see [Reasonix](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2.4-reasonix).
 
 
### Crush

 A terminal agent from the Charm ecosystem. It supports LSP integration and uses a JSON-based provider configuration.

 
 - **Key File:** `~/.config/crush/crush.json` [README.md22](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L22-L22)
 - For details, see [Crush](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2.5-crush).
 
 
### Pi and Oh My Pi

 Pi is a minimal terminal harness with tree-structured sessions. Its fork, Oh My Pi, adds specific tools, model roles, and complex agent workflows.

 
 - **Key File:** `~/.pi/agent/models.json` [README.md32-35](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L32-L35)
 - For details, see [Pi and Oh My Pi](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2.6-pi-and-oh-my-pi).
 
 
### Other Terminal Agents

 This section covers lightweight or specialized tools including:

 
 - **Langcli:** 100% Claude Code compatible CLI [README.md29](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L29-L29)
 - **nanobot:** Lightweight agent with MCP and memory [README.md31](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L31-L31)
 - **OpenCode:** Multi-form assistant (Terminal/Web) [README.md34](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L34-L34)
 - For details, see [Other Terminal Agents](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/2.7-other-terminal-agents).
 
 
---

 
## Architecture of CLI Tool Interaction

 The following diagram demonstrates the data flow from the CLI entry point through the configuration layer to the DeepSeek API.

 **CLI Data Flow Architecture**

 
```

```

 Sources: [docs/deepseek-tui.md32-43](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/deepseek-tui.md?plain=1#L32-L43) [docs/claude_code.md47-60](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/claude_code.md?plain=1#L47-L60)
