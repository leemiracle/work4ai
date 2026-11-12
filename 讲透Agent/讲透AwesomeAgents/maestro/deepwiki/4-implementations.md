<!-- source: DeepWiki mcp.deepwiki.com · repo Doriandarko/maestro · page 4 Implementations · fetched 2026-10-26 -->

# Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page provides an overview of the different Maestro implementations available for various LLM providers. Maestro offers multiple implementation variants designed to work with different AI model providers including Anthropic, OpenAI, Groq, and local LLM solutions. For detailed instructions on installation and setup, see [Installation & Setup](#2). For usage guidance, see [Usage Guide](#3).

## Implementation Overview

Maestro offers implementations for different LLM providers, each designed to leverage the specific capabilities of the target models while maintaining the core orchestration architecture.

```mermaid
graph TD
    subgraph "Maestro Implementations"
        maestro["maestro.py\nAnthropic Claude"]
        maestroAny["maestro-anyapi.py\nMulti-provider"]
        maestroGPT["maestro-gpt.py\nOpenAI GPT-4"]
        maestroGPT4o["maestro-gpt4o.py\nOpenAI GPT-4o"]
        maestroGroq["maestro-groq.py\nGroq Models"]
        maestroLM["maestro-lmstudio.py\nLocal LM Studio"]
        maestroOllama["maestro-ollama.py\nLocal Ollama"]
    end
    
    subgraph "LLM Services"
        anthropic["Anthropic API"]
        openai["OpenAI API"]
        groq["Groq API"]
        litellm["LiteLLM\n(Multi-API Support)"]
        ollama["Ollama\n(Local Models)"]
        lmstudio["LM Studio\n(Local Models)"]
    end
    
    maestro -->|"Uses Claude Opus/Haiku/Sonnet"| anthropic
    maestroGPT -->|"Uses GPT-4"| openai
    maestroGPT4o -->|"Uses GPT-4o"| openai
    maestroGroq -->|"Uses Various Groq Models"| groq
    maestroAny -->|"Uses Various Providers"| litellm
    maestroOllama -->|"Uses Llama 3 Models"| ollama
    maestroLM -->|"Uses Local Models"| lmstudio
    
    litellm -->|"Connects to"| anthropic
    litellm -->|"Connects to"| openai
    litellm -->|"Connects to"| groq
```

Sources: [README.md:1-130]()

## Implementation Components

Each implementation follows the same architectural pattern but uses different clients and model configurations. The main components include:

```mermaid
classDiagram
    class "Maestro Implementation" {
        +client_setup()
        +run_maestro(objective)
        +orchestrator(objective, previous_results)
        +sub_agent(prompt, previous_tasks)
        +refiner(objective, sub_task_results)
        +search_capability(optional)
        +code_generation_capability(optional)
    }
    
    class "API Client" {
        +create_message()
        +handle_response()
    }
    
    class "Models Configuration" {
        +ORCHESTRATOR_MODEL: string
        +SUB_AGENT_MODEL: string
        +REFINER_MODEL: string
    }
    
    class "Optional Components" {
        +TavilyClient
        +code_generation_utilities
    }
    
    "Maestro Implementation" --> "API Client" : uses
    "Maestro Implementation" --> "Models Configuration" : configures
    "Maestro Implementation" --> "Optional Components" : may include
```

Sources: [README.md:132-211]()

## Implementation Comparison

The table below summarizes the key differences between Maestro implementations:

| Implementation | File | LLM Provider | Models Used | Key Features | Requirements |
|----------------|------|-------------|-------------|--------------|--------------|
| Claude Maestro | maestro.py | Anthropic | Claude 3.5 Sonnet, Claude 3 Opus/Haiku | Original implementation, search capability | anthropic package, Anthropic API key |
| Multi-API Maestro | maestro-anyapi.py | Multiple (via LiteLLM) | Any supported by LiteLLM | Multi-provider flexibility | litellm package, API keys for chosen providers |
| GPT-4 Maestro | maestro-gpt.py | OpenAI | GPT-4 | GPT-4 optimization | openai package, OpenAI API key |
| GPT-4o Maestro | maestro-gpt4o.py | OpenAI | GPT-4o | Enhanced code capabilities | openai package, OpenAI API key |
| Groq Maestro | maestro-groq.py | Groq | Various Groq models | Fast API responses | groq package, Groq API key |
| LM Studio Maestro | maestro-lmstudio.py | Local | Models in LM Studio | Local execution, no API costs | LM Studio application |
| Ollama Maestro | maestro-ollama.py | Local | Llama 3 models (8B/70B) | Local execution, no API costs | ollama package, Ollama application |

Sources: [README.md:6-130]()

## Core Implementation: Anthropic Claude

The original Maestro implementation uses Anthropic's Claude models, specifically designed to work with Claude 3.5 Sonnet and Claude 3 Opus/Haiku.

```mermaid
flowchart TD
    subgraph "maestro.py"
        client["Anthropic Client\nSetup"]
        orchestrator["opus_orchestrator()\nUses Claude Opus"]
        subagent["haiku_sub_agent()\nUses Claude Haiku"]
        refiner["opus_refine()\nUses Claude Opus"]
        search["tavily_search()\nOptional Search"]
    end
    
    input["User Objective"] -->|"Input"| orchestrator
    orchestrator -->|"Creates Sub-tasks"| subagent
    orchestrator -->|"May use"| search
    subagent -->|"Sub-task Results"| orchestrator
    orchestrator -->|"Task Complete"| refiner
    refiner -->|"Final Output"| output["Refined Result"]
```

Sources: [README.md:3-5](), [README.md:7-10]()

## Multi-Provider Implementation

The `maestro-anyapi.py` implementation leverages LiteLLM to support multiple LLM providers in a unified interface.

```mermaid
flowchart TD
    subgraph "maestro-anyapi.py"
        liteconfig["LiteLLM Configuration"]
        modeldef["Model Definitions\nORCHESTRATOR_MODEL\nSUB_AGENT_MODEL\nREFINER_MODEL"]
        orchestrator["orchestrator()\nCan use any provider"]
        subagent["sub_agent()\nCan use any provider"]
        refiner["refiner()\nCan use any provider"]
    end
    
    liteconfig -->|"Configures"| modeldef
    apikeys["API Keys\nOpenAI/Anthropic/Gemini/etc."] -->|"Authenticates"| liteconfig
    input["User Objective"] -->|"Input"| orchestrator
    orchestrator -->|"Creates Sub-tasks"| subagent
    subagent -->|"Sub-task Results"| orchestrator
    orchestrator -->|"Task Complete"| refiner
    refiner -->|"Final Output"| output["Refined Result"]
```

Sources: [README.md:13-42]()

## Local LLM Implementations

Maestro supports local LLM execution through both Ollama and LM Studio implementations.

```mermaid
flowchart TD
    subgraph "Local Implementations"
        direction LR
        
        subgraph "maestro-ollama.py"
            ollamaClient["Ollama Client"]
            ollamaOrch["orchestrator()\nUses Llama3 70B"]
            ollamaSub["sub_agent()\nUses Llama3 8B"]
            ollamaRef["refiner()\nUses Llama3 70B"]
        end
        
        subgraph "maestro-lmstudio.py"
            lmstudioClient["LM Studio REST API Client"]
            lmstudioOrch["orchestrator()"]
            lmstudioSub["sub_agent()"]
            lmstudioRef["refiner()"]
        end
    end
    
    localModels["Local LLM Models"] -->|"Provides Models"| ollamaClient
    localModels -->|"Provides Models"| lmstudioClient
    
    input1["User Objective"] -->|"Input"| ollamaOrch
    ollamaOrch -->|"Creates Sub-tasks"| ollamaSub
    ollamaSub -->|"Sub-task Results"| ollamaOrch
    ollamaOrch -->|"Task Complete"| ollamaRef
    
    input2["User Objective"] -->|"Input"| lmstudioOrch
    lmstudioOrch -->|"Creates Sub-tasks"| lmstudioSub
    lmstudioSub -->|"Sub-task Results"| lmstudioOrch
    lmstudioOrch -->|"Task Complete"| lmstudioRef
```

Sources: [README.md:55-98]()

## Groq Implementation

The Groq implementation leverages Groq's high-speed API for faster processing.

```mermaid
flowchart TD
    subgraph "maestro-groq.py"
        groqClient["Groq Client Setup"]
        groqOrch["orchestrator()\nUses Groq LLMs"]
        groqSub["sub_agent()\nUses Groq LLMs"]
        groqRef["refiner()\nUses Groq LLMs"]
    end
    
    groqAPI["Groq API"] -->|"Provides Models"| groqClient
    
    input["User Objective"] -->|"Input"| groqOrch
    groqOrch -->|"Creates Sub-tasks"| groqSub
    groqSub -->|"Sub-task Results"| groqOrch
    groqOrch -->|"Task Complete"| groqRef
    groqRef -->|"Final Output"| output["Refined Result"]
```

Sources: [README.md:100-110]()

## OpenAI Implementations

Maestro provides dedicated implementations for OpenAI's GPT models, with specific optimizations for GPT-4 and GPT-4o.

```mermaid
flowchart TD
    subgraph "OpenAI Implementations"
        direction LR
        
        subgraph "maestro-gpt.py"
            gptClient["OpenAI Client\nGPT-4"]
            gptOrch["orchestrator()"]
            gptSub["sub_agent()"]
            gptRef["refiner()"]
        end
        
        subgraph "maestro-gpt4o.py"
            gpt4oClient["OpenAI Client\nGPT-4o"]
            gpt4oOrch["orchestrator()"]
            gpt4oSub["sub_agent()"]
            gpt4oRef["refiner()"]
        end
    end
    
    openaiAPI["OpenAI API"] -->|"Provides Models"| gptClient
    openaiAPI -->|"Provides Models"| gpt4oClient
    
    input1["User Objective"] -->|"Input"| gptOrch
    gptOrch -->|"Creates Sub-tasks"| gptSub
    gptSub -->|"Sub-task Results"| gptOrch
    gptOrch -->|"Task Complete"| gptRef
    
    input2["User Objective"] -->|"Input"| gpt4oOrch
    gpt4oOrch -->|"Creates Sub-tasks"| gpt4oSub
    gpt4oSub -->|"Sub-task Results"| gpt4oOrch
    gpt4oOrch -->|"Task Complete"| gpt4oRef
```

Sources: [README.md:45-54](), [README.md:121-129]()

## Common Features Across Implementations

All implementations share a common set of features regardless of the LLM provider used:

```mermaid
graph TD
    subgraph "Common Features"
        breakdown["Task Breakdown"]
        execution["Sub-task Execution"]
        memory["Context Memory"]
        refinement["Result Refinement"]
        logging["Exchange Logging"]
        codeGen["Code Generation"]
        search["Search Capability"]
    end
    
    implementation["Any Maestro Implementation"] -->|"Includes"| breakdown
    implementation -->|"Includes"| execution
    implementation -->|"Includes"| memory
    implementation -->|"Includes"| refinement
    implementation -->|"Includes"| logging
    implementation -->|"May Include"| codeGen
    implementation -->|"May Include"| search
    
    search -->|"Uses"| tavily["Tavily Search API"]
    codeGen -->|"Creates"| folders["Project Folders/Files"]
```

Sources: [README.md:132-142]()

## Implementation Selection Guide

When choosing a Maestro implementation, consider the following factors:

1. **API Access**: Which LLM provider APIs you have access to
2. **Model Capabilities**: Required capabilities for your use case (code generation, reasoning, etc.)
3. **Cost Considerations**: API usage costs vs. local computation
4. **Response Speed**: Some implementations like Groq focus on faster responses
5. **Local vs. Cloud**: Privacy or network connectivity requirements

For detailed usage of specific implementations, see:
- [OpenAI (GPT) Implementation](#4.1)
- [Local LLM with Ollama](#4.2)
- [Other Implementations](#4.3)

Sources: [README.md:6-130]()

---

