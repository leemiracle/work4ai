> 来源: [https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/4-desktop-and-web-agent-platforms](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/4-desktop-and-web-agent-platforms)
> DeepWiki deepseek-ai/awesome-deepseek-agent

# Desktop and Web Agent Platforms

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1)
 - [docs/cherry_studio.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/cherry_studio.md?plain=1)
 
  This section provides an overview of cross-platform desktop clients and web-based agent orchestration platforms that support DeepSeek V4. These platforms typically offer graphical user interfaces (GUIs) for managing multiple AI assistants, knowledge bases (RAG), and Model Context Protocol (MCP) integrations.

 The primary platforms covered in this category are **Cherry Studio**, a feature-rich desktop client, and **LobeHub**, a versatile agent operating system available via web, desktop, and self-hosted deployments [README.md19-30](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L19-L30)

 
## Platform Overview

 Desktop and web platforms serve as "Agent Operators," moving beyond simple chat interfaces to provide persistent environments for agentic workflows. They often include:

 
 - **Provider Management:** Centralized configuration for API keys and endpoints.
 - **Agent Orchestration:** Tools to create specialized agents with distinct system prompts and model parameters.
 - **Extended Capabilities:** Built-in support for RAG (Retrieval-Augmented Generation), translation engines, and tool-calling via MCP.
 
 
### Comparison of Primary Platforms

 
| Feature | Cherry Studio | LobeHub |
|---|---|---|
| Deployment | Desktop (Win/macOS/Linux) | Web, Desktop, Self-hosted (Docker) |
| Primary Focus | Personal productivity & Knowledge Base | Team orchestration & Agent "hiring" |
| DeepSeek Models | deepseek-v4-pro, deepseek-v4-flash | deepseek-v4-pro, deepseek-v4-flash |
| Reasoning Control | "Extra High" (reasoning_effort: max) | Intensity (None/High/Max) |
| Context Window | 1M Tokens (Out of the box) | 1M Tokens (Model card config) |

 
## Bridging Natural Language to Code Entity Space

 The following diagrams illustrate how these platforms map user-facing configuration to the underlying DeepSeek API and system architecture.

 
### Cherry Studio Integration Flow

 This diagram shows how the `Model Provider` settings map to the internal `DeepSeek` provider logic and API parameters.

 
```

```

 **Sources:** [docs/cherry_studio.md20-47](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/cherry_studio.md?plain=1#L20-L47)

 
### LobeHub Service Configuration

 This diagram demonstrates the relationship between environment variables in self-hosted deployments and the model selection logic.

 
```

```

 **Sources:** [README.md30](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L30-L30) [Page 4.2 Description](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/Page 4.2 Description)

 
## Supported Platforms

 
### Cherry Studio

 Cherry Studio is an open-source desktop AI client supporting Windows, macOS, and Linux [docs/cherry_studio.md5-18](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/cherry_studio.md?plain=1#L5-L18) It is designed for users who need a unified interface for multiple LLM providers with advanced features like:

 
 - **Knowledge Bases:** RAG support for PDFs, Markdown, and Office files [docs/cherry_studio.md53](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/cherry_studio.md?plain=1#L53-L53)
 - **MCP Servers:** Integration of external tools into DeepSeek-driven conversations [docs/cherry_studio.md55](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/cherry_studio.md?plain=1#L55-L55)
 - **OpenClaw Integration:** A bundled assistant for connecting DeepSeek to messaging platforms like Feishu and WeChat [docs/cherry_studio.md56](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/cherry_studio.md?plain=1#L56-L56)
 
 For detailed configuration steps, see **[Cherry Studio](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/4.1-cherry-studio)**.

 
### LobeHub

 LobeHub acts as a "Chief Agent Operator," focusing on the scheduling and reporting of AI teams [README.md30](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L30-L30) It supports:

 
 - **Flexible Deployment:** Available as a web app, desktop client, or self-hosted Docker container.
 - **Reasoning Control:** Fine-grained control over reasoning intensity (None, High, or Max).
 - **Model Cards:** Pre-configured cards for DeepSeek V4 that respect the 1M token context window.
 
 For detailed configuration steps, see **[LobeHub](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/4.2-lobehub)**.

 
---

 **Sources:**

 
 - [README.md19-30](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/README.md?plain=1#L19-L30)
 - [docs/cherry_studio.md1-57](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/cherry_studio.md?plain=1#L1-L57)
