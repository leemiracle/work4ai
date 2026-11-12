<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/game_arena · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [game_arena/__init__.py](game_arena/__init__.py)

</details>



## Purpose and Scope

Game Arena is a sophisticated orchestration platform developed by Google DeepMind that enables Large Language Models (LLMs) to compete in strategic games. This document provides a high-level architectural overview of the Game Arena harness system, which manages the complete pipeline from game state representation through LLM interaction to move execution.

The platform serves as the foundation for a Kaggle-hosted competition where LLMs play games against each other, with the harness handling all technical coordination between game environments, model providers, and move validation systems.

For detailed implementation guidance, see [Getting Started](#1.1). For an end-to-end trace of a single turn, see [End-to-End Move Pipeline](#1.2).

## System Architecture Overview

Game Arena orchestrates interactions between three primary domains: game environments, LLM providers, and reliability mechanisms. The architecture emphasizes robustness and extensibility to handle the inherent unpredictability of LLM responses.

### High-Level System Architecture

```mermaid
graph TB
    subgraph GameEnvironment["Game Environment Layer"]
        OpenSpiel["OpenSpiel<br/>Game Engine"]
        GameState["Game States<br/>(FEN, ASCII, etc.)"]
        LegalMoves["Legal Move<br/>Validation"]
    end
    
    subgraph LLMOrchestration["LLM Orchestration Layer"]
        Agent["Agent Controllers<br/>(KaggleAgent, LLMAgent)"]
        PromptGen["Prompt Generation<br/>(prompt_generation.py)"]
        ModelCall["Model Calling<br/>(model_generation.py)"]
        ResponseParse["Response Parsing<br/>(parsers.py, llm_parsers.py)"]
    end
    
    subgraph ReliabilityLayer["Reliability Layer"]
        Samplers["Sampling Strategies<br/>(samplers.py, rethink.py)"]
        MajorityVote["Majority Voting<br/>Parallel Attempts"]
        Rethinking["Rethinking<br/>Sequential Feedback"]
    end
    
    subgraph ModelProviders["Model Provider Layer"]
        SDKModels["SDK Integration<br/>(model_generation_sdk.py)"]
        HTTPModels["HTTP Integration<br/>(model_generation_http.py)"]
        Gemini["Google AI Studio"]
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Others["Other Providers"]
    end
    
    OpenSpiel --> GameState
    OpenSpiel --> LegalMoves
    Agent --> PromptGen
    Agent --> ModelCall
    Agent --> ResponseParse
    
    PromptGen --> ModelCall
    ModelCall --> Samplers
    Samplers --> MajorityVote
    Samplers --> Rethinking
    ResponseParse --> LegalMoves
    
    ModelCall --> SDKModels
    ModelCall --> HTTPModels
    SDKModels --> Gemini
    SDKModels --> OpenAI
    SDKModels --> Anthropic
    HTTPModels --> Others
    
    GameState --> PromptGen
    LegalMoves --> ResponseParse
    ResponseParse --> OpenSpiel
```

Sources: [README.md:1-151]()

## Core Components and Code Entities

The Game Arena harness is implemented through several key subsystems, each with specific responsibilities in the LLM-game orchestration pipeline.

### Component-to-Code Mapping

```mermaid
graph LR
    subgraph HarnessCore["harness/ Package"]
        HarnessDemo["harness_demo.py<br/>Demo Orchestration"]
        Prompts["prompts.py<br/>Template Definitions"]
        PromptGeneration["prompt_generation.py<br/>Prompt Assembly"]
        Parsers["parsers.py<br/>Rule-based Parsing"]
        LLMParsers["llm_parsers.py<br/>LLM-based Parsing"]
        Samplers["samplers.py<br/>Majority Voting"]
        Rethink["rethink.py<br/>Sequential Feedback"]
        ModelGeneration["model_generation.py<br/>Retry Wrapper"]
        ModelSDK["model_generation_sdk.py<br/>Official SDK Calls"]
        ModelHTTP["model_generation_http.py<br/>HTTP API Calls"]
    end
    
    subgraph AgentClasses["Agent Implementations"]
        KaggleAgent["KaggleAgent<br/>Base Protocol"]
        LLMAgent["LLMAgent<br/>Base LLM Agent"]
    end
    
    subgraph ParsingStrategies["Parsing Strategies"]
        RuleBasedMoveParser["RuleBasedMoveParser<br/>Regex & String Rules"]
        SoftMoveParser["SoftMoveParser<br/>Fuzzy Matching"]
        LLMParser["LLMParser<br/>Secondary LLM"]
        ChainedMoveParser["ChainedMoveParser<br/>Sequential Processing"]
    end
    
    subgraph ModelClasses["Model Provider Classes"]
        AIStudioModel["AIStudioModel<br/>Gemini Integration"]
        OpenAIChatCompletionsModel["OpenAIChatCompletionsModel<br/>GPT Integration"]
        AnthropicModel["AnthropicModel<br/>Claude Integration"]
    end
    
    HarnessDemo --> KaggleAgent
    HarnessDemo --> LLMAgent
    
    PromptGeneration --> Prompts
    LLMAgent --> Samplers
    LLMAgent --> Rethink
    
    Parsers --> RuleBasedMoveParser
    Parsers --> SoftMoveParser
    LLMParsers --> LLMParser
    Parsers --> ChainedMoveParser
    
    ModelSDK --> AIStudioModel
    ModelSDK --> OpenAIChatCompletionsModel
    ModelSDK --> AnthropicModel
    
    ModelGeneration --> ModelSDK
    ModelGeneration --> ModelHTTP
```

Sources: [README.md:41-151]()

## Game Turn Orchestration Flow

The complete flow from game state to executed move involves multiple coordination points and error handling mechanisms. For a detailed step-by-step examination of this pipeline, see [End-to-End Move Pipeline](#1.2).

### LLM Game Turn Sequence

```mermaid
sequenceDiagram
    participant OpenSpiel as "OpenSpiel<br/>Game Engine"
    participant Agent as "LLMAgent<br/>or RethinkAgent"
    participant PromptGen as "prompt_generation.py<br/>Prompt Assembly"
    participant Sampler as "samplers.py<br/>or rethink.py"
    participant ModelGen as "model_generation.py<br/>API Wrapper"
    participant Provider as "model_generation_sdk.py<br/>or model_generation_http.py"
    participant Parser as "parsers.py<br/>Move Extraction"
    
    OpenSpiel->>Agent: "Current game state + legal_moves()"
    Agent->>PromptGen: "format_prompt(game_state, player)"
    PromptGen->>Agent: "Formatted prompt string"
    
    alt Majority Voting (samplers.py)
        Agent->>Sampler: "majority_voting_sample()"
        loop "N parallel attempts"
            Sampler->>ModelGen: "generate_text(prompt)"
            ModelGen->>Provider: "API call with retry logic"
            Provider->>ModelGen: "Response text"
            ModelGen->>Sampler: "Generated text"
        end
        Sampler->>Agent: "Most frequent valid move"
    else Rethinking (rethink.py)
        Agent->>Sampler: "rethinking_sample()"
        Sampler->>ModelGen: "Initial generate_text(prompt)"
        ModelGen->>Provider: "API call"
        Provider->>ModelGen: "Response text"
        alt "Move invalid"
            Sampler->>ModelGen: "generate_text(prompt + feedback)"
            ModelGen->>Provider: "Retry API call"
            Provider->>ModelGen: "Refined response"
        end
        Sampler->>Agent: "Final move or failure"
    end
    
    Agent->>Parser: "parse_move(response, legal_moves)"
    Parser->>Agent: "Extracted OpenSpiel action"
    Agent->>OpenSpiel: "apply_action(parsed_move)"
```

Sources: [README.md:93-140]()

## Key Subsystems Summary

| Subsystem | Primary Files | Core Classes | Purpose |
|-----------|--------------|--------------|---------|
| **Game Environment** | OpenSpiel integration | `pyspiel.Game`, `pyspiel.State` | Game state management and move validation |
| **Agent Control** | Agent implementations | `KaggleAgent`, `LLMAgent` | Orchestrate complete turn sequence |
| **Prompt Generation** | [README.md]() | Template functions | Convert game state to LLM prompts |
| **Model Integration** | [README.md]() | `AIStudioModel`, `OpenAIChatCompletionsModel` | Interface with LLM providers |
| **Reliability Sampling** | [README.md]() | Sampling functions | Improve move validity through multiple attempts |
| **Response Parsing** | [README.md]() | `RuleBasedMoveParser`, `LLMParser` | Extract valid moves from LLM responses |
| **Retry Handling** | [README.md]() | Retry decorators | Handle API failures and timeouts |

Sources: [README.md:64-151]()

## Child Pages

- [Getting Started](#1.1) — Setup, installation, API keys, running the demos, and contribution guidelines
- [End-to-End Move Pipeline](#1.2) — Walk through a single turn: observation -> prompt -> model call -> parse -> sampler/rethin -> action submitted to OpenSpiel

---

