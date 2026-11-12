<!-- source: DeepWiki mcp.deepwiki.com · repo stanford-oval/storm · page 5 Usage and Examples · fetched 2026-10-26 -->

# Examples and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/costorm_examples/run_costorm_gpt.py](examples/costorm_examples/run_costorm_gpt.py)
- [examples/storm_examples/run_storm_wiki_mistral.py](examples/storm_examples/run_storm_wiki_mistral.py)
- [examples/storm_examples/run_storm_wiki_ollama.py](examples/storm_examples/run_storm_wiki_ollama.py)

</details>



This document provides practical examples demonstrating how to use both STORM and Co-STORM systems for automated and collaborative knowledge curation. The examples show complete working implementations with different language model providers and retrieval modules.

For detailed information on the core system architecture, see [Architecture Overview](#1.2). For specific component documentation, see [STORM Wiki Generation System](#2) and [Co-STORM Collaborative System](#3).

## Overview of Example Structure

The STORM repository includes comprehensive command-line examples that demonstrate the full pipeline execution for both systems. These examples show how to configure language models, retrieval modules, and execution parameters for different use cases.

```mermaid
graph TB
    subgraph "Example Scripts"
        MistralExample["run_storm_wiki_mistral.py<br/>VLLM + Mistral Integration"]
        OllamaExample["run_storm_wiki_ollama.py<br/>Ollama Local Model Integration"]
        CoStormExample["Co-STORM Examples<br/>Collaborative Workflows"]
    end
    
    subgraph "Core Configuration"
        LMConfigs["STORMWikiLMConfigs<br/>Language Model Setup"]
        EngineArgs["STORMWikiRunnerArguments<br/>Pipeline Parameters"]
        Runner["STORMWikiRunner<br/>Main Orchestrator"]
    end
    
    subgraph "External Dependencies"
        LMProviders["Language Model Providers<br/>VLLMClient, OllamaClient"]
        RMProviders["Retrieval Modules<br/>YouRM, BingSearch, etc."]
        APIKeys["Environment Variables<br/>API Keys & Secrets"]
    end
    
    MistralExample --> LMConfigs
    OllamaExample --> LMConfigs
    LMConfigs --> Runner
    EngineArgs --> Runner
    
    Runner --> LMProviders
    Runner --> RMProviders
    
    APIKeys --> RMProviders
    APIKeys --> LMProviders
```

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:1-273](), [examples/storm_examples/run_storm_wiki_ollama.py:1-277]()

## Example Output Structure

All STORM examples produce a standardized output directory structure that organizes the generated content and intermediate results:

| File | Description | Purpose |
|------|-------------|---------|
| `conversation_log.json` | Information-seeking conversation logs | Records simulated expert conversations |
| `raw_search_results.json` | Unprocessed search engine results | Raw retrieval module outputs |
| `direct_gen_outline.txt` | LLM parametric knowledge outline | Baseline outline without external information |
| `storm_gen_outline.txt` | Research-enhanced outline | Final outline incorporating retrieved information |
| `url_to_info.json` | Source reference mapping | Maps URLs to extracted information used in article |
| `storm_gen_article.txt` | Generated article | Complete article with citations |
| `storm_gen_article_polished.txt` | Polished final article | Refined version with summarization (optional) |

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:7-16](), [examples/storm_examples/run_storm_wiki_ollama.py:7-16]()

## Language Model Configuration Pattern

The examples demonstrate a consistent pattern for configuring specialized language model instances for different pipeline stages:

```mermaid
graph LR
    subgraph "LM Configuration Flow"
        BaseClient["Base LM Client<br/>VLLMClient/OllamaClient"]
        
        ConvSim["conv_simulator_lm<br/>max_tokens=500"]
        QuestionAsker["question_asker_lm<br/>max_tokens=500"]  
        OutlineGen["outline_gen_lm<br/>max_tokens=400"]
        ArticleGen["article_gen_lm<br/>max_tokens=700"]
        ArticlePolish["article_polish_lm<br/>max_tokens=4000"]
        
        LMConfigs["STORMWikiLMConfigs<br/>Central Configuration"]
    end
    
    BaseClient --> ConvSim
    BaseClient --> QuestionAsker
    BaseClient --> OutlineGen
    BaseClient --> ArticleGen
    BaseClient --> ArticlePolish
    
    ConvSim --> LMConfigs
    QuestionAsker --> LMConfigs
    OutlineGen --> LMConfigs
    ArticleGen --> LMConfigs
    ArticlePolish --> LMConfigs
```

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:44-66](), [examples/storm_examples/run_storm_wiki_ollama.py:44-66]()

## Retrieval Module Selection

The examples implement a flexible retrieval module selection system supporting multiple search engines and APIs:

```mermaid
graph TD
    subgraph "Retrieval Module Options"
        BingRM["BingSearch<br/>BING_SEARCH_API_KEY"]
        YouRMOption["YouRM<br/>YDC_API_KEY"]
        BraveRMOption["BraveRM<br/>BRAVE_API_KEY"]
        DuckRM["DuckDuckGoSearchRM<br/>No API Key Required"]
        SerperRMOption["SerperRM<br/>SERPER_API_KEY"]
        TavilyRMOption["TavilySearchRM<br/>TAVILY_API_KEY"]
        SearXRMOption["SearXNG<br/>SEARXNG_API_KEY"]
    end
    
    subgraph "Configuration Logic"
        RetrieverArg["args.retriever<br/>Command Line Selection"]
        MatchStatement["Python match statement<br/>Retriever instantiation"]
        APIKeyEnv["Environment Variables<br/>os.getenv() calls"]
    end
    
    RetrieverArg --> MatchStatement
    APIKeyEnv --> BingRM
    APIKeyEnv --> YouRMOption
    APIKeyEnv --> BraveRMOption
    APIKeyEnv --> SerperRMOption
    APIKeyEnv --> TavilyRMOption
    APIKeyEnv --> SearXRMOption
    
    MatchStatement --> BingRM
    MatchStatement --> YouRMOption
    MatchStatement --> BraveRMOption
    MatchStatement --> DuckRM
    MatchStatement --> SerperRMOption
    MatchStatement --> TavilyRMOption
    MatchStatement --> SearXRMOption
```

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:77-112](), [examples/storm_examples/run_storm_wiki_ollama.py:77-112]()

## Pipeline Stage Control

The examples provide granular control over pipeline execution through boolean flags that enable selective stage execution:

| Stage Flag | Function | Default Behavior |
|------------|----------|------------------|
| `--do-research` | Execute knowledge curation | Skip if results exist |
| `--do-generate-outline` | Generate article outline | Skip if results exist |
| `--do-generate-article` | Generate article content | Skip if results exist |
| `--do-polish-article` | Polish and summarize | Optional refinement |

This design allows for:
- **Incremental execution**: Resume from any stage if previous results exist
- **Debugging**: Isolate specific pipeline stages
- **Resource management**: Skip expensive operations when testing

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:179-185](), [examples/storm_examples/run_storm_wiki_ollama.py:179-185]()

## Open Model Enhancement Techniques

The examples demonstrate specific techniques for improving open-source language model performance through prompt engineering:

```mermaid
graph TB
    subgraph "Enhancement Strategies"
        OneShot["One-shot Examples<br/>dspy.Example objects"]
        PseudoExamples["Pseudo Examples<br/>Simplified demonstrations"]
        FormatSteering["Output Format Control<br/>Structured responses"]
    end
    
    subgraph "Target Components"
        PersonaGen["StormPersonaGenerator<br/>find_related_topic, gen_persona"]
        OutlineGen["WritePageOutlineFromConv<br/>write_page_outline"]
        SectionGen["ConvToSection<br/>write_section"]
    end
    
    subgraph "Example Types"
        TopicExample["find_related_topic_example<br/>Topic → Related URLs"]
        PersonaExample["gen_persona_example<br/>Topic → Expert Personas"]
        OutlineExample["write_page_outline_example<br/>Conversation → Outline"]
        SectionExample["write_section_example<br/>Info → Formatted Section"]
    end
    
    OneShot --> PersonaGen
    PseudoExamples --> OutlineGen
    PseudoExamples --> SectionGen
    
    TopicExample --> PersonaGen
    PersonaExample --> PersonaGen
    OutlineExample --> OutlineGen
    SectionExample --> SectionGen
```

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:116-176](), [examples/storm_examples/run_storm_wiki_ollama.py:116-176]()

## Command Line Interface Structure

The examples implement comprehensive argument parsing for flexible execution control:

### Global Configuration Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `--url` | str | `http://localhost` | Server URL for local LM |
| `--port` | int | Model-specific | Server port |
| `--model` | str | Model-specific | Model identifier |
| `--output-dir` | str | `./results/` | Output directory path |
| `--max-thread-num` | int | 3 | Parallel execution threads |
| `--retriever` | str | Required | Search engine selection |

### Pipeline Hyperparameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `--max-conv-turn` | int | 3 | Conversation question limit |
| `--max-perspective` | int | 3 | Perspective diversity limit |
| `--search-top-k` | int | 3 | Search results per query |
| `--retrieve-top-k` | int | 3 | References per section |

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:192-273](), [examples/storm_examples/run_storm_wiki_ollama.py:192-277]()

## Environment Setup Requirements

The examples require specific environment configuration for external service integration:

```mermaid
graph LR
    subgraph "Required Setup"
        SecretsFile["secrets.toml<br/>API Key Storage"]
        EnvVars["Environment Variables<br/>Service Authentication"]
        LocalServers["Local Model Servers<br/>VLLM/Ollama instances"]
    end
    
    subgraph "API Key Requirements"
        SearchKeys["Search Engine Keys<br/>YDC_API_KEY, BING_SEARCH_API_KEY, etc."]
        ModelKeys["Model Provider Keys<br/>Service-specific authentication"]
    end
    
    subgraph "Runtime Dependencies"
        LoadAPIKey["load_api_key()<br/>TOML file loading"]
        OSGetenv["os.getenv()<br/>Environment variable access"]
    end
    
    SecretsFile --> LoadAPIKey
    EnvVars --> OSGetenv
    SearchKeys --> EnvVars
    ModelKeys --> EnvVars
```

Sources: [examples/storm_examples/run_storm_wiki_mistral.py:43](), [examples/storm_examples/run_storm_wiki_ollama.py:43]()

---

