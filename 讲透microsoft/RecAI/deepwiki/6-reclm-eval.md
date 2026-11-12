<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RecAI · page 6 RecLM-eval · fetched 2026-10-26 -->

# RecLM-eval

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [RecLM-eval/.gitignore](RecLM-eval/.gitignore)
- [RecLM-eval/README.md](RecLM-eval/README.md)
- [RecLM-eval/api_cost.jsonl](RecLM-eval/api_cost.jsonl)

</details>



RecLM-eval is a comprehensive evaluation framework for LLM-based recommendation systems that provides standardized benchmarking across multiple recommendation tasks. It serves as the central evaluation hub for all recommendation models in the RecAI ecosystem, supporting both generative and embedding-based approaches.

For information about specific RecLM-eval evaluation methodologies and task orchestration, see [RecLM-eval Methods](#6.1). For details about model integration and distributed evaluation infrastructure, see [RecLM-eval Model Integration](#6.2).

## Architecture Overview

RecLM-eval implements a modular evaluation architecture that supports seven distinct recommendation evaluation tasks through a unified interface.

### System Architecture

```mermaid
graph TB
    subgraph "RecLM-eval Framework"
        subgraph "Entry Point"
            eval_py["eval.py<br/>Main evaluation script"]
        end
        
        subgraph "Configuration Layer"
            config_yaml["openai_api_config.yaml<br/>API configuration"]
            cost_jsonl["api_cost.jsonl<br/>Cost tracking"]
            main_sh["main.sh<br/>Execution script"]
        end
        
        subgraph "Task Orchestration"
            ranking_task["ranking<br/>Sequential ranking evaluation"]
            retrieval_task["retrieval<br/>Item retrieval evaluation"]
            emb_ranking["embedding_ranking<br/>Embedding-based ranking"]
            emb_retrieval["embedding_retrieval<br/>Embedding-based retrieval"]
            explanation_task["explanation<br/>Explanation generation"]
            conversation_task["conversation<br/>Conversational evaluation"]
            chatbot_task["chatbot<br/>General chat ability"]
        end
        
        subgraph "Model Integration"
            vllm_models["VLLM Models<br/>Local model serving"]
            openai_models["OpenAI API Models<br/>Remote model access"]
            hf_models["Hugging Face Models<br/>Embedding models"]
        end
        
        subgraph "Data Sources"
            steam_data["Steam Dataset<br/>./data/ folder"]
            custom_data["Custom Datasets<br/>User-provided"]
        end
        
        subgraph "Evaluation Components"
            judge_models["Judge Models<br/>GPT-based evaluation"]
            simulator_models["Simulator Models<br/>User simulation"]
            baseline_models["Baseline Models<br/>Comparison standards"]
        end
    end
    
    %% Entry point connections
    eval_py --> ranking_task
    eval_py --> retrieval_task
    eval_py --> emb_ranking
    eval_py --> emb_retrieval
    eval_py --> explanation_task
    eval_py --> conversation_task
    eval_py --> chatbot_task
    
    %% Configuration connections
    config_yaml --> openai_models
    cost_jsonl --> openai_models
    main_sh --> eval_py
    
    %% Task to model connections
    ranking_task --> vllm_models
    ranking_task --> openai_models
    retrieval_task --> vllm_models
    retrieval_task --> openai_models
    emb_ranking --> hf_models
    emb_ranking --> openai_models
    emb_retrieval --> hf_models
    emb_retrieval --> openai_models
    explanation_task --> judge_models
    conversation_task --> simulator_models
    chatbot_task --> judge_models
    chatbot_task --> baseline_models
    
    %% Data connections
    steam_data --> ranking_task
    steam_data --> retrieval_task
    steam_data --> emb_ranking
    steam_data --> emb_retrieval
    steam_data --> explanation_task
    steam_data --> conversation_task
    custom_data --> ranking_task
    custom_data --> retrieval_task
    custom_data --> explanation_task
    custom_data --> conversation_task
```

**Sources:** [RecLM-eval/README.md:1-135]()

### Task-Model Integration Map

```mermaid
graph LR
    subgraph "Evaluation Tasks"
        ranking["ranking"]
        retrieval["retrieval"] 
        emb_ranking["embedding_ranking"]
        emb_retrieval["embedding_retrieval"]
        explanation["explanation"]
        conversation["conversation"]
        chatbot["chatbot"]
    end
    
    subgraph "Model Requirements"
        generative["Generative Models<br/>--model_path_or_name"]
        embedding["Embedding Models<br/>text-embedding-*"]
        judge["Judge Models<br/>--judge-model"]
        baseline["Baseline Models<br/>--baseline-model"]
        simulator["Simulator Models<br/>--simulator-model"]
        summary["Summary Models<br/>--summary-model"]
    end
    
    subgraph "Parameter Sets"
        basic_params["bench_name<br/>model_path_or_name"]
        emb_params["user_emb_type<br/>item_emb_type<br/>summary_model"]
        judge_params["judge_model<br/>baseline_model"]
        conv_params["simulator_model<br/>max_turn"]
        vllm_params["max_new_tokens<br/>batch_size"]
    end
    
    %% Task to model type connections
    ranking --> generative
    retrieval --> generative
    emb_ranking --> embedding
    emb_retrieval --> embedding
    explanation --> generative
    explanation --> judge
    conversation --> generative
    conversation --> simulator
    chatbot --> generative
    chatbot --> judge
    chatbot --> baseline
    
    %% Model to parameter connections
    generative --> basic_params
    generative --> vllm_params
    embedding --> emb_params
    embedding --> summary
    judge --> judge_params
    simulator --> conv_params
```

**Sources:** [RecLM-eval/README.md:51-135]()

## Supported Evaluation Tasks

RecLM-eval supports seven distinct evaluation tasks, each designed to assess different aspects of recommendation system performance.

### Core Recommendation Tasks

| Task | Purpose | Required Parameters | Model Types |
|------|---------|-------------------|-------------|
| `ranking` | Sequential item ranking evaluation | `--bench-name`, `--model_path_or_name` | Generative LLMs |
| `retrieval` | Item retrieval from large catalogs | `--bench-name`, `--model_path_or_name` | Generative LLMs |
| `embedding_ranking` | Ranking using embedding similarity | `--model_path_or_name`, `--user_emb_type`, `--item_emb_type` | Embedding models |
| `embedding_retrieval` | Retrieval using embedding similarity | `--model_path_or_name`, `--user_emb_type`, `--item_emb_type` | Embedding models |

### Interactive Evaluation Tasks

| Task | Purpose | Required Parameters | Model Types |
|------|---------|-------------------|-------------|
| `explanation` | Recommendation explanation quality | `--judge-model`, `--baseline-model` | Generative + Judge |
| `conversation` | Multi-turn conversational ability | `--simulator-model`, `--max_turn` | Generative + Simulator |
| `chatbot` | General conversational capability | `--judge-model`, `--baseline-model` | Generative + Judge + Baseline |

**Sources:** [RecLM-eval/README.md:51-52](), [RecLM-eval/README.md:55-135]()

### Embedding Task Configuration

The embedding-based tasks support flexible configuration for user and item representations:

```bash
# Title-based embeddings
python eval.py --task-names embedding_ranking embedding_retrieval \
    --model_path_or_name text-embedding-3-small \
    --user_emb_type title \
    --item_emb_type title

# Summary-based user embeddings  
python eval.py --task-names embedding_ranking embedding_retrieval \
    --model_path_or_name text-embedding-3-small \
    --user_emb_type summary \
    --summary-model gpt-3.5-turbo \
    --item_emb_type title
```

**Sources:** [RecLM-eval/README.md:78-92]()

## Configuration and Setup

### API Configuration

RecLM-eval uses a YAML-based configuration system for external API access:

```yaml
# openai_api_config.yaml
API_BASE: "if-you-have-different-api-url"
API_KEY: "your-api-key"
```

**Sources:** [RecLM-eval/README.md:21-26]()

### Cost Tracking

The framework tracks API usage costs through a JSONL configuration file that maps model names to input/output token costs:

| Model | Input Cost ($/1M tokens) | Output Cost ($/1M tokens) |
|-------|-------------------------|---------------------------|
| `gpt-4o` | 5.0 | 15.0 |
| `gpt-4o-mini` | 0.15 | 0.6 |
| `gpt-35-turbo` | 0.5 | 1.5 |
| `text-embedding-3-small` | 0.02 | 0 |
| `text-embedding-3-large` | 0.13 | 0 |

**Sources:** [RecLM-eval/api_cost.jsonl:1-14]()

### Environment Setup

```bash
conda create -n receval python==3.9
conda activate receval
pip install -r requirements.txt
```

**Sources:** [RecLM-eval/README.md:36-40]()

## Data Requirements

### Default Dataset

RecLM-eval provides a Steam dataset as the default evaluation benchmark, combining multiple data sources:

- Steam game metadata from UCSD datasets
- Sequential interaction data from SASRec
- Additional game information from Kaggle

**Sources:** [RecLM-eval/README.md:47-48]()

### Data Structure

The framework expects datasets to be placed in the `./data/` directory and follows a standardized format for cross-task compatibility.

**Sources:** [RecLM-eval/README.md:7-13](), [RecLM-eval/.gitignore:4-5]()

## Integration with RecAI Components

RecLM-eval serves as the central evaluation hub for all RecAI components, providing standardized benchmarking across different recommendation approaches:

### Supported Model Architectures

```mermaid
graph TB
    subgraph "RecAI Model Integration"
        subgraph "Generative Models"
            reclm_gen["RecLM-gen<br/>Generative fine-tuned models"]
            reclm_cgen["RecLM-cgen<br/>Constrained generation models"]
            interec["InteRecAgent<br/>Tool-based conversational agent"]
        end
        
        subgraph "Embedding Models" 
            reclm_emb["RecLM-emb<br/>Specialized embedding models"]
            generic_emb["Generic Embeddings<br/>OpenAI, Hugging Face"]
        end
        
        subgraph "Explanation Models"
            recexplainer["RecExplainer<br/>Alignment-based explainers"]
        end
        
        subgraph "Knowledge Enhanced"
            knowledge_plugin["Knowledge_Plugin<br/>Traditional + LLM hybrid"]
        end
    end
    
    subgraph "RecLM-eval Tasks"
        eval_ranking["ranking/retrieval<br/>eval.py"]
        eval_embedding["embedding_ranking/<br/>embedding_retrieval"]
        eval_explanation["explanation<br/>evaluation"]
        eval_conversation["conversation/<br/>chatbot evaluation"]
    end
    
    %% Model to task connections
    reclm_gen --> eval_ranking
    reclm_gen --> eval_explanation
    reclm_gen --> eval_conversation
    
    reclm_cgen --> eval_ranking
    reclm_cgen --> eval_explanation
    
    interec --> eval_conversation
    
    reclm_emb --> eval_embedding
    generic_emb --> eval_embedding
    
    recexplainer --> eval_explanation
    
    knowledge_plugin --> eval_ranking
    knowledge_plugin --> eval_explanation
```

**Sources:** [RecLM-eval/README.md:1-3]()

### Execution Workflow

The main execution script `main.sh` orchestrates the complete evaluation pipeline, while `eval.py` provides the primary interface for task-specific evaluation.

**Sources:** [RecLM-eval/README.md:28-31](), [RecLM-eval/.gitignore:7-9]()

---

