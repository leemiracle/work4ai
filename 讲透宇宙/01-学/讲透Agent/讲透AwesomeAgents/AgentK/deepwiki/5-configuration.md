<!-- source: DeepWiki mcp.deepwiki.com · repo mikekelly/AgentK · page 5 Configuration · fetched 2026-10-26 -->

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [config.py](config.py)

</details>



## Overview
The Configuration system in AgentK manages language model selection and system-wide settings. This document explains how to configure the language model provider, model parameters, and optional integrations.

For more detailed information about specific language model setup instructions, see [Language Model Setup](#5.1).

Sources: [config.py](), [.env.example]()

## Environment Configuration
AgentK uses environment variables for configuration, typically set in a `.env` file in the project root. A template file `.env.example` is provided to show the expected format.

Key configuration variables:

| Variable | Purpose | Default Value | Location |
|----------|---------|---------------|----------|
| `OPENAI_API_KEY` | Authentication key for OpenAI API | None (Required for OpenAI) | `.env` |
| `DEFAULT_MODEL_NAME` | Language model identifier | "gpt-4o" | `config.py:7` |
| `DEFAULT_MODEL_TEMPERATURE` | Controls randomness (0-1) | 0 | `config.py:5` |
| `DEFAULT_MODEL_PROVIDER` | Model provider selection | "OPENAI" | `config.py:6` |
| `ANTHROPIC_API_KEY` | Authentication key for Anthropic | None (Required for Anthropic) | `.env` |

The system also supports optional LangSmith integration for tracking and monitoring language model interactions:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=...
```

Sources: [.env.example:1-13]()

## Language Model Configuration
The core model configuration logic resides in `config.py`, which initializes a language model based on environment variables. The resulting `default_langchain_model` object is used throughout the system for AI interactions.

The system supports three model providers with specific initialization requirements:

1. **OpenAI**: Default provider, initializes a `ChatOpenAI` instance
2. **Anthropic**: Initializes a `ChatAnthropic` instance for Claude models
3. **Ollama**: Initializes a `ChatOpenAI` instance with custom API base URL for local models

Sources: [config.py:1-23]()

## Configuration Flow Diagram

```mermaid
graph TD
    EnvFile[".env File"] -->|"OS Environment"| EnvVars["Environment Variables"]
    EnvVars -->|"os.getenv() in config.py"| ConfigVars["Configuration Variables"]
    ConfigVars -->|"Match-case in config.py"| ModelInit["Model Initialization"]
    ModelInit -->|"OPENAI case"| OpenAIInit["ChatOpenAI() (Lines 10-11)"]
    ModelInit -->|"ANTHROPIC case"| AnthropicInit["ChatAnthropic() (Lines 12-13)"]
    ModelInit -->|"OLLAMA case"| OllamaInit["ChatOpenAI with custom URL (Lines 14-20)"]
    OpenAIInit -->|"assigned to"| DefaultModel["default_langchain_model"]
    AnthropicInit -->|"assigned to"| DefaultModel
    OllamaInit -->|"assigned to"| DefaultModel
    DefaultModel -->|"Used by"| AgentSystem["Agent System"]
```

Sources: [config.py:5-22]()

## Model Provider Selection Process

```mermaid
flowchart TD
    Start["AgentK Initialization"] -->|"1. Load Environment"| ReadEnv["Read Environment Variables"]
    ReadEnv -->|"2. Pattern Match"| MatchProvider{"Match on default_model_provider"}
    MatchProvider -->|"OPENAI"| OpenAI["Initialize ChatOpenAI (Line 11)"]
    MatchProvider -->|"ANTHROPIC"| Anthropic["Initialize ChatAnthropic (Line 13)"]
    MatchProvider -->|"OLLAMA"| Ollama["Initialize ChatOpenAI with custom URL (Lines 15-20)"]
    MatchProvider -->|"Other"| Error["Raise ValueError (Line 22)"]
    OpenAI -->|"assigned to"| ModelAssign["default_langchain_model"]
    Anthropic -->|"assigned to"| ModelAssign
    Ollama -->|"assigned to"| ModelAssign
    ModelAssign -->|"3. Use Model"| AgentSystem["Provide to Agent System"]
```

Sources: [config.py:9-22]()

---

