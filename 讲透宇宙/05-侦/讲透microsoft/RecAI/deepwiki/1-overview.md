<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RecAI · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [InteRecAgent/README.md](InteRecAgent/README.md)
- [Knowledge_Plugin/README.md](Knowledge_Plugin/README.md)
- [RAI_FAQ.md](RAI_FAQ.md)
- [README.md](README.md)
- [RecLM-cgen/README.md](RecLM-cgen/README.md)
- [RecLM-gen/README.md](RecLM-gen/README.md)

</details>



This document provides a comprehensive overview of the RecAI repository architecture, which implements various strategies for integrating Large Language Models (LLMs) into recommender systems. RecAI addresses the fundamental challenge that while LLMs excel at natural language interaction, they lack domain-specific recommendation knowledge, and while traditional recommender systems are effective with in-domain data, they lack interactivity and explainability.

The repository contains six main systems that explore different LLM4Rec integration approaches: conversational agents, knowledge injection, specialized LLM training, model explanation, and evaluation frameworks. For specific implementation details of individual systems, see [InteRecAgent](#4), [RecLM-emb](#2), [RecExplainer](#3), [RecLM-gen and RecLM-cgen](#5), [Knowledge_Plugin](#), and [RecLM-eval](#6).

## System Architecture Overview

RecAI implements four distinct approaches to LLM-recommender integration, each addressing different aspects of the recommendation pipeline:

```mermaid
graph TB
    subgraph "RecAI Repository Structure"
        subgraph "InteRecAgent/"
            IRA["app.py<br/>Interactive Agent Entry"]
            IRA_Tools["tools/<br/>SQL, Similarity, Ranking"]
            IRA_Prompts["prompts/<br/>System Prompts"]
        end
        
        subgraph "Knowledge_Plugin/"
            KP_Extract["Knowledge_Extraction/<br/>extract_I2I.py, extract_U2I.py"]
            KP_DOKE["DOKE/<br/>generate_prompt.py, call_openai.py"]
            KP_Models["preprocess/step2-Base_models/"]
        end
        
        subgraph "RecLM-emb/"
            RLEMB_Demo["demo/<br/>ten_task_dataset.py"]
            RLEMB_Train["training/<br/>train.py"]
            RLEMB_Eval["evaluation/<br/>eval_embedding.py"]
        end
        
        subgraph "RecExplainer/"
            REX_Align["src/<br/>alignment training"]
            REX_Data["data_preprocess/<br/>GPT data generation"]
            REX_Eval["eval/<br/>evaluation pipeline"]
        end
        
        subgraph "RecLM-gen/"
            RLG_SFT["main.py<br/>SFT Training"]
            RLG_RL["main.py<br/>RL Training"]
            RLG_Serve["unirec/async_server.py<br/>SASRec Server"]
        end
        
        subgraph "RecLM-cgen/"
            RLCG_Train["main.py<br/>Constrained Training"]
            RLCG_Prefix["train_utils/processor.py<br/>FastPrefixConstrainedLogitsProcessor"]
        end
        
        subgraph "RecLM-eval/"
            REVAL_Tasks["tasks/<br/>Multi-task Evaluation"]
            REVAL_Models["models/<br/>HF Integration"]
        end
        
        subgraph "External Dependencies"
            OpenAI["OpenAI API<br/>GPT-3.5/4"]
            HF["Hugging Face<br/>transformers library"]
            UniRec["UniRec Library<br/>Traditional RecSys"]
        end
    end
    
    %% Integration connections
    IRA --> OpenAI
    IRA --> IRA_Tools
    KP_DOKE --> OpenAI
    KP_Models --> KP_Extract
    RLEMB_Demo --> OpenAI
    REX_Data --> OpenAI
    RLG_Serve --> UniRec
    RLCG_Prefix --> HF
    REVAL_Models --> HF
```

Sources: [README.md:1-234](), [InteRecAgent/README.md:1-196](), [RecLM-gen/README.md:1-310](), [RecLM-cgen/README.md:1-289](), [Knowledge_Plugin/README.md:1-69]()

## LLM Integration Approaches

RecAI implements four distinct strategies for combining LLMs with recommender systems:

| Approach | System | Key Components | Training Required | Benefits |
|----------|--------|----------------|-------------------|----------|
| **Tool-based Orchestration** | InteRecAgent | `app.py`, `tools/`, LLM API | No LLM training | Natural interaction, preserves domain expertise |
| **Knowledge Injection** | Knowledge_Plugin | `generate_prompt.py`, CF extractors | No LLM training | Selective knowledge use, maintains LLM capabilities |
| **LLM Specialization** | RecLM-gen/cgen/emb | `main.py`, SFT/RL training | Extensive training | End-to-end optimization, task-specific adaptation |
| **Model Explanation** | RecExplainer | Alignment training, behavior analysis | Moderate training | Interpretability, trust building |

Sources: [README.md:13-68](), [RAI_FAQ.md:7-19]()

## Core System Components

### Data Processing Pipeline

```mermaid
graph LR
    subgraph "Raw Data Sources"
        Amazon["Amazon Reviews<br/>Movies_and_TV_5.json.gz<br/>meta_Movies_and_TV.json.gz"]
        Steam["Steam Game Data"]
        ShareGPT["ShareGPT<br/>Conversations"]
        ML1M["ML1M Movies"]
    end
    
    subgraph "Preprocessing"
        DataPrep["data_preprocess_amazon.py<br/>sequential.jsonl<br/>metas.jsonl<br/>category.jsonl"]
        UniRecPrep["UniRec Format<br/>train.pkl, valid.pkl<br/>test.pkl, user_history.pkl"]
    end
    
    subgraph "Traditional Training"
        SASRec["SASRec via UniRec<br/>unirec/async_server.py"]
        MF["Matrix Factorization<br/>MF_embedding.pkl"]
    end
    
    subgraph "LLM Data Generation"
        GPTGen["GPT-4 API Calls<br/>call_openai.py<br/>ten_task_dataset.py"]
        Templates["Prompt Templates<br/>config/ directories"]
    end
    
    subgraph "LLM Training"
        SFT["Supervised Fine-tuning<br/>main.py --train_stage SFT"]
        RL["Reinforcement Learning<br/>main.py --train_stage RL"]
        Alignment["Alignment Training<br/>RecExplainer training"]
    end
    
    Amazon --> DataPrep
    Steam --> DataPrep
    DataPrep --> UniRecPrep
    UniRecPrep --> SASRec
    DataPrep --> MF
    Templates --> GPTGen
    SASRec --> SFT
    GPTGen --> SFT
    SFT --> RL
    SFT --> Alignment
```

Sources: [RecLM-gen/README.md:60-66](), [RecLM-cgen/README.md:20-35](), [Knowledge_Plugin/README.md:7-17]()

### Technology Stack

The RecAI implementation leverages several key libraries and frameworks:

**Core ML Libraries:**
- `transformers` (Hugging Face) - LLM training and inference [RecLM-gen/README.md:8](), [RecLM-cgen/README.md:18]()
- `UniRec` - Traditional recommender model training [RecLM-gen/README.md:69](), [RecLM-cgen/README.md:78]()
- `vllm` - Fast LLM serving for inference [RecLM-gen/README.md:262]()

**LLM Integration:**
- OpenAI API integration for GPT-3.5/4 [InteRecAgent/README.md:74-88]()
- FastChat for local model serving [InteRecAgent/README.md:112-141]()
- Custom constrained generation via `FastPrefixConstrainedLogitsProcessor` [RecLM-cgen/README.md:251-276]()

**Data Processing:**
- Amazon dataset preprocessing pipelines [RecLM-gen/README.md:61-66](), [RecLM-cgen/README.md:21-34]()
- Collaborative filtering knowledge extraction [Knowledge_Plugin/README.md:19-35]()
- Multi-task dataset generation for LLM training

Sources: [README.md:102-107](), [InteRecAgent/README.md:56-141](), [RecLM-gen/README.md:1-310]()

## Evaluation and Deployment

RecAI provides comprehensive evaluation through `RecLM-eval` and multiple deployment options:

**Evaluation Framework:**
- Multi-task evaluation across retrieval, ranking, explanation capabilities [README.md:64-66]()
- User simulator for conversational evaluation [RAI_FAQ.md:25-27]()
- GPT-4 based comparative analysis

**Deployment Options:**
- Gradio interfaces for interactive demos [InteRecAgent/README.md:91-99]()
- REST API endpoints for model serving [RecLM-gen/README.md:262-276]()
- Docker containerization support for production deployment

The system is designed for both research experimentation and practical deployment, with responsible AI considerations documented in [RAI_FAQ.md:1-59]().

Sources: [README.md:62-68](), [RAI_FAQ.md:21-37](), [RecLM-gen/README.md:258-289]()

---

