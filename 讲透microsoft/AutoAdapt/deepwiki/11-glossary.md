<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/AutoAdapt · page 11 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/data/models_data_database/models_database_medical+math.json](app/data/models_data_database/models_database_medical+math.json)
- [app/react/backend/conf/config_default.yaml](app/react/backend/conf/config_default.yaml)
- [app/sample/conf/config.yaml](app/sample/conf/config.yaml)
- [src/autoadapt/adapt/autoadapt_executor.py](src/autoadapt/adapt/autoadapt_executor.py)
- [src/autoadapt/agents/aggregator_agent.py](src/autoadapt/agents/aggregator_agent.py)
- [src/autoadapt/agents/best_practice_agent.py](src/autoadapt/agents/best_practice_agent.py)
- [src/autoadapt/agents/best_practices/openai_embeddings.py](src/autoadapt/agents/best_practices/openai_embeddings.py)
- [src/autoadapt/agents/knowledge_retriever_agent.py](src/autoadapt/agents/knowledge_retriever_agent.py)
- [src/autoadapt/agents/research_agent.py](src/autoadapt/agents/research_agent.py)
- [src/autoadapt/config/ACG.json](src/autoadapt/config/ACG.json)
- [src/autoadapt/dashboard/static/config_template.yaml](src/autoadapt/dashboard/static/config_template.yaml)
- [src/autoadapt/hpo/coreset_selection.py](src/autoadapt/hpo/coreset_selection.py)
- [src/autoadapt/hpo/llm_gp_sampler.py](src/autoadapt/hpo/llm_gp_sampler.py)
- [src/autoadapt/hpo/llm_sampler.py](src/autoadapt/hpo/llm_sampler.py)
- [src/autoadapt/hpo/llm_surrogate_sampler.py](src/autoadapt/hpo/llm_surrogate_sampler.py)
- [src/autoadapt/template/dpo/main.py](src/autoadapt/template/dpo/main.py)
- [src/autoadapt/template/rag/main.py](src/autoadapt/template/rag/main.py)
- [src/autoadapt/template/rag/utils.py](src/autoadapt/template/rag/utils.py)
- [src/autoadapt/template/sft/main.py](src/autoadapt/template/sft/main.py)
- [src/autoadapt/utils/misc.py](src/autoadapt/utils/misc.py)
- [src/deepcore/methods/gradmatch.py](src/deepcore/methods/gradmatch.py)
- [src/deepcore/methods/kcentergreedy.py](src/deepcore/methods/kcentergreedy.py)

</details>



This page provides definitions and technical implementation details for core concepts, terminology, and architectural components within the AutoAdapt codebase.

## Core Architectural Terms

### Adaptation Configuration Graph (ACG)
The **ACG** is a hierarchical JSON structure that defines the search space for all possible adaptation strategies. It consists of nodes that represent choices (e.g., SFT vs. RAG) or specific hyperparameters.
*   **Implementation**: Defined in `src/autoadapt/config/ACG.json` [src/autoadapt/config/ACG.json:1-191]().
*   **Node Types**:
    *   `select:1` or `select:any`: Represents a decision point where agents must choose one or multiple children [src/autoadapt/config/ACG.json:6-8]().
    *   `parameter`: Defines specific hyperparameters (e.g., `learning_rate`, `lora_r`) with default values and types [src/autoadapt/config/ACG.json:56-109]().
    *   `direct_parameter`: Similar to parameter nodes but typically for top-level configuration like RAG settings [src/autoadapt/config/ACG.json:24-42]().
*   **Data Flow**: The `MultiAgentDebatePlanner` traverses this graph to resolve choices and assemble a concrete `Pipeline` object [src/autoadapt/adapt/autoadapt_executor.py:47-52]().

### AutoRefine (LLM-Based HPO)
**AutoRefine** is the system's approach to Hyperparameter Optimization (HPO) that uses Large Language Models (LLMs) to navigate the search space instead of traditional random or grid search.
*   **Executor**: `HpoExecutor` manages the lifecycle of Optuna studies [src/autoadapt/hpo/hpo_executor.py]().
*   **Samplers**:
    *   `LLMSampler`: Directly prompts the LLM for values based on trial history [src/autoadapt/hpo/llm_sampler.py:75-175]().
    *   `LLMGPSampler`: A hybrid approach that uses LLMs to bootstrap a Gaussian Process (GP) model, which then suggests the next best trial [src/autoadapt/hpo/llm_gp_sampler.py:55-107]().

### Coreset Selection
A technique used during the HPO phase to reduce the training dataset to a representative subset, significantly accelerating the evaluation of different hyperparameter configurations.
*   **Implementation**: `CoresetSelector` in `src/autoadapt/hpo/coreset_selection.py` [src/autoadapt/hpo/coreset_selection.py:17-41]().
*   **Methods**:
    *   `RandomCoresetSelector`: Simple random sampling [src/autoadapt/hpo/coreset_selection.py:110-158]().
    *   `EmbeddingCoresetSelector`: Uses `SubmodularEmb` to select samples based on their vector representations (e.g., using `e5-large-v2`) [src/autoadapt/hpo/coreset_selection.py:43-107]().

**Sources**: [src/autoadapt/config/ACG.json:1-191](), [src/autoadapt/hpo/coreset_selection.py:17-158](), [src/autoadapt/hpo/llm_gp_sampler.py:55-107]().

---

## Multi-Agent System Terminology

AutoAdapt uses a specialized agentic workflow to plan adaptation strategies.

| Agent Class | Role | Code Pointer |
| :--- | :--- | :--- |
| `ResearchAgent` | Reasons using domain knowledge from `knowledge.md`. | [src/autoadapt/agents/research_agent.py:60-140]() |
| `AggregatorAgent` | Synthesizes proposals from solvers and critiques into a final recommendation. | [src/autoadapt/agents/aggregator_agent.py:53-169]() |
| `BestPracticeAgent` | Retrieves empirical model cards and historical performance data. | [src/autoadapt/agents/best_practice_agent.py]() |
| `DataAgent` | Analyzes dataset statistics (tokens, duplicates) to inform planning. | [src/autoadapt/agents/extract_dataset_stats.py]() |

### Multi-Agent Planning Flow
The following diagram bridges the Natural Language planning concepts to the specific Code Entities that execute them.

**Planning Phase: NL Space to Code Space**
```mermaid
graph TD
    subgraph "Natural Language Space (User Intent)"
        "UserTask"["'Fine-tune Llama-3 for Medical QA'"]
        "Preference"["'Prioritize accuracy over speed'"]
    end

    subgraph "Code Entity Space (System Logic)"
        "Executor"["AutoAdaptExecutor.plan()"]
        "Planner"["MultiAgentDebatePlanner"]
        "ACG"["ACG.json (Search Space)"]
        "AgentDebate"["Planner.round_debate()"]
        "SharedMem"["SharedMemory (Context)"]
    end

    "UserTask" --> "Executor"
    "Preference" --> "Executor"
    "Executor" --> "Planner"
    "Planner" -- "Traverses" --> "ACG"
    "Planner" -- "Orchestrates" --> "AgentDebate"
    "AgentDebate" -- "Reads/Writes" --> "SharedMem"
    "AgentDebate" -- "Returns" --> "PipelineObj[pipeline.pkl]"
```
**Sources**: [src/autoadapt/adapt/autoadapt_executor.py:32-65](), [src/autoadapt/plan/multiagent_debate_planner.py](), [src/autoadapt/agents/aggregator_agent.py:31-50]().

---

## Adaptation Templates

AutoAdapt supports three primary adaptation strategies, each defined by a "template" containing training and evaluation logic.

### SFT (Supervised Fine-Tuning)
Standard instruction tuning. Supports LoRA and Prefix Tuning via PEFT.
*   **Entrypoint**: `src/autoadapt/template/sft/main.py`.
*   **Key Logic**: Uses `SFTTrainer` and handles model quantization (int4/int8) [src/autoadapt/template/sft/main.py]().

### DPO (Direct Preference Optimization)
Aligns models using preference pairs (chosen vs. rejected).
*   **Entrypoint**: `src/autoadapt/template/dpo/main.py`.
*   **Key Logic**: Configures `DPOTrainer` with a `beta` parameter to control deviation from the reference model [src/autoadapt/config/ACG.json:104-108]().

### RAG (Retrieval-Augmented Generation)
Enhances generation by retrieving context from external documents.
*   **Entrypoint**: `src/autoadapt/template/rag/main.py`.
*   **Key Components**: ChromaDB for indexing and `retriever_top_k` for search depth [src/autoadapt/config/ACG.json:27-31]().

**Template Execution Data Flow**
```mermaid
graph LR
    subgraph "Configuration"
        "YAML"["config.yaml"]
        "BestConfig"["best_config.yaml (from HPO)"]
    end

    subgraph "Template Logic (Code Entities)"
        "SFT_Main"["sft/main.py:run()"]
        "DPO_Main"["dpo/main.py:run()"]
        "RAG_Main"["rag/main.py:run()"]
        "Eval"["Evaluator.evaluate_with_llm()"]
    end

    "YAML" --> "SFT_Main"
    "BestConfig" --> "SFT_Main"
    "SFT_Main" --> "Eval"
    "DPO_Main" --> "Eval"
    "RAG_Main" --> "Eval"
```
**Sources**: [src/autoadapt/template/sft/main.py](), [src/autoadapt/template/dpo/main.py](), [src/autoadapt/template/rag/main.py](), [src/autoadapt/config/ACG.json:13-126]().

---

## DeepCore Terms (Coreset Subsystem)

AutoAdapt integrates the `deepcore` library for advanced data selection.

*   **EarlyTrain**: The base class for methods that require a proxy model to be trained briefly to estimate sample importance [src/deepcore/methods/earlytrain.py]().
*   **kCenterGreedy**: A geometric selection method that picks points to cover the embedding space efficiently [src/deepcore/methods/kcentergreedy.py:8-65]().
*   **GradMatch**: A gradient-based method that selects a subset whose gradient sum matches the full dataset gradient [src/deepcore/methods/gradmatch.py:11-75]().
*   **SubmodularEmb**: A method that treats coreset selection as a submodular function maximization problem over embeddings [src/autoadapt/hpo/coreset_selection.py:74]().

**Sources**: [src/deepcore/methods/kcentergreedy.py:68-156](), [src/deepcore/methods/gradmatch.py:11-156](), [src/autoadapt/hpo/coreset_selection.py:71-77]().

---

## Configuration & Utility Terms

### ACG.json vs. config.yaml
*   **ACG.json**: Defines the **possibility space** (what *can* be configured) [src/autoadapt/config/ACG.json:1-10]().
*   **config.yaml**: Defines the **instance settings** (e.g., project paths, API keys, dataset locations) [app/react/backend/conf/config_default.yaml:15-103]().

### TokenUsageCallback
A utility to track LLM API costs across planning and HPO phases.
*   **Implementation**: `TokenUsageCallback` in `src/autoadapt/utils/token_usage.py`.
*   **Usage**: Initialized in `AutoAdaptExecutor` and passed to the `ChatCompletionModel` [src/autoadapt/adapt/autoadapt_executor.py:40-45]().

### model_client (ChatCompletionModel)
A unified abstraction layer for calling Azure OpenAI or OpenAI models.
*   **Implementation**: `ChatCompletionModel` in `src/autoadapt/utils/llm.py` [src/autoadapt/adapt/autoadapt_executor.py:43-45]().
*   **Role**: Handles retries, logging, and structured output parsing using Pydantic [src/autoadapt/agents/aggregator_agent.py:111]().

**Sources**: [app/react/backend/conf/config_default.yaml:105-128](), [src/autoadapt/adapt/autoadapt_executor.py:32-65](), [src/autoadapt/agents/aggregator_agent.py:73-111]().