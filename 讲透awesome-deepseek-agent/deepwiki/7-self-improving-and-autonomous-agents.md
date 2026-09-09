> 来源: [https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/7-self-improving-and-autonomous-agents](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/7-self-improving-and-autonomous-agents)
> DeepWiki deepseek-ai/awesome-deepseek-agent

# Self-Improving and Autonomous Agents

  Relevant source files 
 - [docs/hermes.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1)
 - [docs/hermes.zh-CN.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.zh-CN.md?plain=1)
 - [docs/nanobot.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.md?plain=1)
 - [docs/nanobot.zh-CN.md](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.zh-CN.md?plain=1)
 
  This section provides an overview of agents within the DeepSeek ecosystem that possess autonomous or self-evolving capabilities. Unlike standard chat interfaces, these agents are designed to manage long-term state, refine their own internal logic (skills), and operate with a higher degree of independence across sessions.

 The two primary implementations covered here are **Hermes Agent**, which focuses on a recursive learning loop for skill evolution, and **nanobot**, a lightweight autonomous agent designed for seamless integration into existing chat platforms.

 
## Hermes Agent

 Hermes, developed by Nous Research, is a self-improving AI agent that implements a built-in learning loop. It is designed to move beyond static instruction following by evolving its capabilities based on user interaction and task outcomes.

 
### Core Evolution Mechanisms

 Hermes utilizes DeepSeek V4 models to drive several autonomous cycles:

 
 - **Skill Creation**: Automatically derives new reusable skills from successful task executions [docs/hermes.md5-6](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L5-L6)
 - **Preference Modeling**: Builds a dynamic model of user preferences that persists across different sessions [docs/hermes.md5-6](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L5-L6)
 - **Knowledge Persistence**: Saves and improves knowledge over time to optimize future reasoning paths [docs/hermes.md5-6](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L5-L6)
 
 
### Configuration Overview

 Users can initialize Hermes using a one-line installer and a dedicated setup wizard.

 
 - **Command**: `hermes setup` [docs/hermes.md27](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L27-L27)
 - **Provider**: DeepSeek [docs/hermes.md29](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L29-L29)
 - **Model**: `deepseek-v4-pro` [docs/hermes.md32](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L32-L32)
 
 For detailed installation and setup instructions, see [Hermes Agent](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/7.1-hermes-agent).

 
---

 
## nanobot

 nanobot is a lightweight autonomous agent focused on portability and integration. It leverages the `uv` toolchain for rapid deployment and uses a structured configuration schema to interface with DeepSeek.

 
### Operational Architecture

 nanobot operates as a standalone agent that can be launched directly from the terminal to handle tasks autonomously. It relies on a `config.json` file to define provider behaviors and agent defaults.

 
### Key Configuration Symbols

 
 - **Initialization**: `nanobot onboard` [docs/nanobot.md39](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.md?plain=1#L39-L39)
 - **Launch Command**: `nanobot agent` [docs/nanobot.md71](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.md?plain=1#L71-L71)
 - **Config Path**: `~/.nanobot/config.json` [docs/nanobot.md45](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.md?plain=1#L45-L45)
 
 For details on the JSON schema and environment setup, see [nanobot](https://deepwiki.com/deepseek-ai/awesome-deepseek-agent/7.2-nanobot).

 
---

 
## Technical Mapping: Agent to Code Space

 The following diagrams illustrate how natural language concepts for these autonomous agents map to specific code entities and configuration keys within the repository.

 
### Hermes Configuration Flow

 This diagram maps the `hermes setup` wizard choices to the underlying configuration requirements for DeepSeek integration.

 
```

```

 **Sources:** [docs/hermes.md25-33](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L25-L33) [docs/hermes.md5-6](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L5-L6)

 
### nanobot Runtime Structure

 This diagram bridges the `nanobot` CLI commands to the specific JSON configuration fields required for the agent to function.

 
```

```

 **Sources:** [docs/nanobot.md47-64](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.md?plain=1#L47-L64) [docs/nanobot.md68-72](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.md?plain=1#L68-L72)

 
## Summary Table

 
| Agent | Core Philosophy | Primary Model | Configuration File |
|---|---|---|---|
| Hermes | Self-improving, skill-based evolution | deepseek-v4-pro | Internal state / wizard-driven |
| nanobot | Lightweight, modular autonomy | deepseek-v4-pro | config.json |

 **Sources:** [docs/hermes.md3-6](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/hermes.md?plain=1#L3-L6) [docs/nanobot.md50-64](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/4481ad5b/docs/nanobot.md?plain=1#L50-L64)
