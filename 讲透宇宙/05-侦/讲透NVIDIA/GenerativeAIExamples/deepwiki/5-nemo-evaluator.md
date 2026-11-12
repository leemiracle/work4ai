<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/GenerativeAIExamples · page 5 NeMo Evaluator · fetched 2026-10-26 -->

# NeMo Evaluator

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nemo/Evaluator/README.md](nemo/Evaluator/README.md)

</details>



## Purpose and Scope

NeMo Evaluator is a microservice within the NeMo Microservices Platform that provides comprehensive model assessment capabilities. This document covers the architecture, evaluation types, integration patterns, and usage workflows for NeMo Evaluator.

NeMo Evaluator supports three primary evaluation categories:
- **LLM-as-a-Judge evaluation**: Using language models to assess the quality of generated outputs
- **Retrieval evaluation**: Measuring the performance of embedding models and retriever systems
- **RAG evaluation**: End-to-end assessment of Retrieval-Augmented Generation pipelines

For information about fine-tuning models that are subsequently evaluated, see [Tool Calling Workflow](#4.1) and [Embedding Fine-tuning Workflow](#4.2). For information about the continuous improvement cycle that uses evaluator results, see [NeMo Data Flywheel](#4).

Sources: [nemo/Evaluator/README.md:1-30]()

---

## Architecture Overview

NeMo Evaluator operates as a standalone microservice that queries deployed models through NVIDIA NIM endpoints and computes quality metrics. It integrates with the Data Flywheel to provide feedback for iterative model improvement.

### Position in NeMo Microservices Ecosystem

```mermaid
graph TB
    subgraph "Data Pipeline"
        DataDesigner["NeMo Data Designer<br/>Synthetic Data Generation"]
        DataStore["NeMo Data Store<br/>Dataset Repository"]
    end
    
    subgraph "Training Pipeline"
        Customizer["NeMo Customizer<br/>Model Fine-tuning"]
        EntityStore["Entity Store<br/>Model Registry"]
    end
    
    subgraph "Inference Layer"
        NIM["NVIDIA NIM<br/>Model Serving"]
    end
    
    subgraph "Quality Assurance"
        Evaluator["NeMo Evaluator<br/>Model Assessment"]
        Guardrails["NeMo Guardrails<br/>Safety Checks"]
    end
    
    DataDesigner -->|"Generates Datasets"| DataStore
    DataStore -->|"Training Data"| Customizer
    Customizer -->|"Fine-tuned Models"| EntityStore
    EntityStore -->|"Deploys Models"| NIM
    
    NIM -->|"Query for Assessment"| Evaluator
    NIM -->|"Safety Validation"| Guardrails
    DataStore -->|"Evaluation Datasets"| Evaluator
    
    Evaluator -.->|"Feedback Metrics"| Customizer
    Evaluator -.->|"Quality Reports"| DataDesigner
    
    style Evaluator fill:#fff4e1,stroke:#333,stroke-width:3px
    style NIM fill:#76b900,stroke:#333,stroke-width:2px
```

**Diagram: NeMo Evaluator in the Microservices Ecosystem** - Shows how Evaluator receives evaluation datasets from Data Store, queries models through NIM, and provides feedback to Customizer and Data Designer for continuous improvement.

Sources: High-level architecture diagrams (Diagram 2, Diagram 3)

---

## Evaluation Workflow

The standard evaluation workflow involves creating an evaluation target (the model to assess), defining an evaluation configuration (metrics and datasets), and executing evaluation jobs.

```mermaid
graph LR
    subgraph "Setup Phase"
        Target["Create Evaluation Target<br/>- Model endpoint URL<br/>- Model type<br/>- Authentication"]
        Config["Create Evaluation Config<br/>- Benchmark/Dataset<br/>- Metrics selection<br/>- Judge model (if applicable)"]
    end
    
    subgraph "Execution Phase"
        Job["Start Evaluation Job<br/>- Target + Config<br/>- Job ID returned"]
        Monitor["Monitor Job Status<br/>- Polling/Callbacks<br/>- Progress tracking"]
    end
    
    subgraph "Results Phase"
        Results["Retrieve Results<br/>- Metric scores<br/>- Per-sample outputs<br/>- Aggregate statistics"]
        Analysis["Analysis<br/>- Compare models<br/>- Identify weaknesses<br/>- Inform next iteration"]
    end
    
    Target --> Config
    Config --> Job
    Job --> Monitor
    Monitor --> Results
    Results --> Analysis
    
    Analysis -.->|"Improve Training"| Target
```

**Diagram: Standard Evaluation Workflow** - The evaluation process from target creation through result analysis, with a feedback loop for model improvement.

Sources: [nemo/Evaluator/README.md:6-10]()

---

## Evaluation Capabilities

### LLM-as-a-Judge Evaluation

LLM-as-a-Judge uses a language model to assess the quality of outputs from another model. This approach enables subjective quality assessment that traditional metrics cannot capture.

**Key Concepts:**
- **Judge Model**: A capable LLM (e.g., GPT-4, Llama 3.1 70B) that evaluates outputs
- **Judge Prompt**: A prompt template instructing the judge on evaluation criteria
- **Evaluation Target**: The model being assessed
- **Reference Dataset**: Input prompts with optional reference outputs

**Code Entity Mapping:**

```mermaid
graph TB
    subgraph "Evaluation Configuration"
        JudgeConfig["Judge Configuration<br/>- judge_model: str<br/>- judge_prompt_template: str<br/>- evaluation_criteria: list"]
        TargetConfig["Target Configuration<br/>- model_endpoint: str<br/>- model_name: str<br/>- task_type: str"]
    end
    
    subgraph "Evaluation Execution"
        EvalJob["Evaluation Job<br/>- job_id: str<br/>- status: str<br/>- progress: float"]
        QueryInterface["Query Interface<br/>- send_prompt()<br/>- get_response()<br/>- batch_inference()"]
    end
    
    subgraph "Result Processing"
        ScoreParser["Score Parser<br/>- parse_judge_output()<br/>- extract_scores()<br/>- validate_format()"]
        ResultStore["Result Store<br/>- per_sample_scores: list<br/>- aggregate_metrics: dict<br/>- raw_outputs: list"]
    end
    
    JudgeConfig --> EvalJob
    TargetConfig --> EvalJob
    EvalJob --> QueryInterface
    QueryInterface --> ScoreParser
    ScoreParser --> ResultStore
```

**Diagram: LLM-as-a-Judge Code Components** - Maps evaluation concepts to code entities involved in judge-based evaluation.

**Use Cases:**
- Summarization quality assessment
- Creative content evaluation
- Instruction following accuracy
- Style and tone adherence

Sources: [nemo/Evaluator/README.md:12-17]()

### Retrieval Evaluation

Retrieval evaluation measures how effectively an embedding model or retriever system finds relevant documents for a given query.

**Standard Retrieval Metrics:**

| Metric | Description | Use Case |
|--------|-------------|----------|
| **NDCG@k** | Normalized Discounted Cumulative Gain at k | Ranking quality with graded relevance |
| **MRR** | Mean Reciprocal Rank | Position of first relevant result |
| **Recall@k** | Fraction of relevant docs in top-k | Coverage assessment |
| **Precision@k** | Fraction of top-k that are relevant | Accuracy assessment |
| **MAP** | Mean Average Precision | Overall retrieval performance |

**Evaluation Process:**

```mermaid
graph TB
    subgraph "Input Data"
        Queries["Query Dataset<br/>- query_text: str<br/>- query_id: str"]
        Corpus["Document Corpus<br/>- doc_id: str<br/>- doc_text: str"]
        QRels["Relevance Judgments<br/>- query_id: str<br/>- doc_id: str<br/>- relevance_score: int"]
    end
    
    subgraph "Embedding & Retrieval"
        EmbedModel["Embedding Model<br/>(via NIM endpoint)<br/>- encode_queries()<br/>- encode_documents()"]
        Retriever["Retriever<br/>- vector_search()<br/>- top_k_retrieval()<br/>- compute_similarity()"]
    end
    
    subgraph "Metric Calculation"
        MetricEngine["Metric Engine<br/>- calculate_ndcg()<br/>- calculate_mrr()<br/>- calculate_recall()<br/>- calculate_precision()"]
        Results["Evaluation Results<br/>- per_query_metrics: dict<br/>- aggregate_scores: dict"]
    end
    
    Queries --> EmbedModel
    Corpus --> EmbedModel
    EmbedModel --> Retriever
    Retriever --> MetricEngine
    QRels --> MetricEngine
    MetricEngine --> Results
```

**Diagram: Retrieval Evaluation Pipeline** - Shows the flow from query/corpus data through embedding and retrieval to metric computation.

**Supported Datasets:**
- FiQA (Financial Question Answering)
- MS MARCO (Microsoft MAchine Reading COmprehension)
- Custom datasets with query-document pairs

Sources: [nemo/Evaluator/README.md:19-28]()

### Retriever + Reranking Evaluation

Reranking evaluation assesses two-stage retrieval systems where an initial retriever produces candidates and a reranker model refines the ranking.

```mermaid
graph LR
    Query["Query"] --> FirstStage["First-Stage Retrieval<br/>(Embedding Model)<br/>Returns top-N candidates"]
    FirstStage --> Reranker["Reranking Model<br/>(Cross-encoder)<br/>Scores N candidates"]
    Reranker --> FinalRanking["Final Ranking<br/>Returns top-k"]
    FinalRanking --> Metrics["Compute Metrics<br/>NDCG@k, MRR, etc."]
    
    GroundTruth["Ground Truth<br/>Relevance Labels"] --> Metrics
```

**Diagram: Two-Stage Retrieval Evaluation** - The reranking evaluation pipeline with first-stage retrieval and cross-encoder reranking.

**Key Differences from Single-Stage:**
- Evaluates combined retrieval + reranking performance
- Measures improvement from reranking stage
- Requires reranker model endpoint in addition to embedding endpoint

Sources: [nemo/Evaluator/README.md:24]()

### RAG Evaluation

RAG evaluation assesses end-to-end Retrieval-Augmented Generation systems, measuring both retrieval quality and generation quality.

**RAG Evaluation Components:**

```mermaid
graph TB
    subgraph "RAG System Under Test"
        Query["User Query"]
        Retriever["Retriever<br/>Vector Search"]
        Context["Retrieved Context<br/>Top-k documents"]
        Generator["Generator LLM<br/>Answer Generation"]
        Answer["Generated Answer"]
    end
    
    subgraph "Evaluation Metrics"
        RetrievalMetrics["Retrieval Metrics<br/>- Context Precision<br/>- Context Recall<br/>- Context Relevance"]
        GenerationMetrics["Generation Metrics<br/>- Answer Relevance<br/>- Faithfulness<br/>- Answer Correctness"]
        EndToEndMetrics["End-to-End Metrics<br/>- Answer Semantic Similarity<br/>- Answer F1"]
    end
    
    Query --> Retriever
    Retriever --> Context
    Context --> Generator
    Generator --> Answer
    
    Context --> RetrievalMetrics
    Answer --> GenerationMetrics
    Query --> GenerationMetrics
    Answer --> EndToEndMetrics
    
    GroundTruth["Ground Truth<br/>- Expected answer<br/>- Relevant docs"] --> RetrievalMetrics
    GroundTruth --> GenerationMetrics
    GroundTruth --> EndToEndMetrics
```

**Diagram: RAG Evaluation Metrics** - Shows the three categories of RAG metrics: retrieval quality, generation quality, and end-to-end performance.

**Ragas Framework Integration:**

NeMo Evaluator integrates with Ragas (RAG Assessment) metrics for comprehensive RAG evaluation:

| Metric | Category | Description |
|--------|----------|-------------|
| **Context Precision** | Retrieval | Measures if retrieved contexts are relevant to the query |
| **Context Recall** | Retrieval | Measures if all necessary information is retrieved |
| **Faithfulness** | Generation | Measures if the answer is grounded in retrieved context |
| **Answer Relevance** | Generation | Measures if the answer addresses the query |
| **Answer Correctness** | End-to-End | Compares answer to ground truth (factual + semantic) |
| **Answer Semantic Similarity** | End-to-End | Cosine similarity with ground truth answer |

**Evaluation Datasets:**
- FiQA with RAG setup
- Synthetic datasets generated by Data Designer
- Custom domain-specific datasets

Sources: [nemo/Evaluator/README.md:20-27]()

---

## Benchmark Evaluation

NeMo Evaluator supports standard benchmarks for comparing models against established baselines.

**Supported Benchmarks:**

| Benchmark | Task Type | Metrics | Use Case |
|-----------|-----------|---------|----------|
| **BigBench** | Diverse Tasks | Accuracy, F1 | General capability assessment |
| **MMLU** | Multi-task Language Understanding | Accuracy | Knowledge and reasoning |
| **GSM8K** | Math Word Problems | Exact Match | Mathematical reasoning |
| **HumanEval** | Code Generation | Pass@k | Programming capability |
| **TruthfulQA** | Truthfulness | MC1, MC2 | Factual accuracy |

**Benchmark Evaluation Flow:**

```mermaid
graph TB
    SelectBenchmark["Select Benchmark<br/>- BigBench<br/>- MMLU<br/>- Custom"] --> ConfigureTarget["Configure Target Model<br/>- model_endpoint<br/>- model_params"]
    
    ConfigureTarget --> RunEval["Run Evaluation Job<br/>- Process test set<br/>- Collect predictions"]
    
    RunEval --> ComputeMetrics["Compute Benchmark Metrics<br/>- Task-specific scoring<br/>- Aggregate results"]
    
    ComputeMetrics --> CompareBaseline["Compare to Baseline<br/>- Published scores<br/>- Previous versions"]
    
    CompareBaseline --> Report["Generate Report<br/>- Per-task breakdown<br/>- Overall score"]
```

**Diagram: Benchmark Evaluation Workflow** - Standard flow for evaluating models on established benchmarks.

Sources: [nemo/Evaluator/README.md:8]()

---

## Integration Patterns

### Integration with NeMo Customizer

NeMo Evaluator provides feedback to the fine-tuning process by evaluating customized models:

```mermaid
graph LR
    subgraph "Customizer"
        Training["Fine-tuning Job<br/>LoRA Training"]
        Checkpoint["Model Checkpoint<br/>Saved Adapter"]
    end
    
    subgraph "Deployment"
        NIM["NIM Deployment<br/>Base + LoRA"]
    end
    
    subgraph "Evaluator"
        EvalJob["Evaluation Job<br/>Test Set Assessment"]
        Metrics["Quality Metrics<br/>Accuracy, F1, etc."]
    end
    
    subgraph "Decision Logic"
        Compare["Compare Metrics<br/>vs. Baseline"]
        Decision{"Meets<br/>Threshold?"}
    end
    
    Training --> Checkpoint
    Checkpoint --> NIM
    NIM --> EvalJob
    EvalJob --> Metrics
    Metrics --> Compare
    Compare --> Decision
    
    Decision -->|"Yes"| Promote["Promote to Production"]
    Decision -->|"No"| Iterate["Iterate Fine-tuning<br/>- Adjust hyperparameters<br/>- Generate more data"]
    
    Iterate -.-> Training
```

**Diagram: Evaluator-Customizer Integration** - Shows how evaluation results inform the fine-tuning iteration loop.

Sources: High-level architecture diagrams (Diagram 3)

### Integration with Data Designer

Evaluation results guide synthetic data generation priorities:

```mermaid
graph TB
    Evaluator["NeMo Evaluator<br/>Model Assessment"] --> Analysis["Error Analysis<br/>- Identify weak areas<br/>- Categorize failures"]
    
    Analysis --> Insights["Data Insights<br/>- Missing scenarios<br/>- Underrepresented categories"]
    
    Insights --> DataDesigner["NeMo Data Designer<br/>Targeted Synthesis"]
    
    DataDesigner --> NewData["Augmented Dataset<br/>- More diverse examples<br/>- Edge cases covered"]
    
    NewData --> Retraining["Re-train Model<br/>with Enhanced Data"]
    
    Retraining --> Evaluator
```

**Diagram: Evaluator-Data Designer Feedback Loop** - Evaluation insights drive targeted synthetic data generation.

Sources: High-level architecture diagrams (Diagram 2, Diagram 3)

---

## API and Client Usage

### NeMo Microservices SDK Integration

NeMo Evaluator is accessed through the `nemo_microservices` Python SDK:

**Key SDK Components:**

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `EvaluatorClient` | Main client interface | `create_target()`, `create_config()`, `start_job()` |
| `EvaluationTarget` | Model endpoint configuration | `from_nim_endpoint()`, `set_auth()` |
| `EvaluationConfig` | Evaluation parameters | `add_benchmark()`, `add_metric()`, `set_dataset()` |
| `EvaluationJob` | Job management | `wait_for_completion()`, `get_results()`, `cancel()` |
| `ResultsProcessor` | Result analysis | `get_aggregate_metrics()`, `get_per_sample()` |

**Typical Usage Pattern:**

```mermaid
sequenceDiagram
    participant Client as Python Client
    participant SDK as nemo_microservices SDK
    participant Evaluator as Evaluator Service
    participant NIM as NIM Endpoint
    
    Client->>SDK: create_target(nim_endpoint)
    SDK->>Evaluator: POST /targets
    Evaluator-->>SDK: target_id
    
    Client->>SDK: create_config(benchmark, metrics)
    SDK->>Evaluator: POST /configs
    Evaluator-->>SDK: config_id
    
    Client->>SDK: start_job(target_id, config_id)
    SDK->>Evaluator: POST /jobs
    Evaluator-->>SDK: job_id
    
    loop Evaluation Process
        Evaluator->>NIM: Query with test samples
        NIM-->>Evaluator: Model predictions
        Evaluator->>Evaluator: Compute metrics
    end
    
    Client->>SDK: get_results(job_id)
    SDK->>Evaluator: GET /jobs/{job_id}/results
    Evaluator-->>SDK: evaluation_results
    SDK-->>Client: processed_metrics
```

**Diagram: SDK-Evaluator Interaction Sequence** - Shows the API call sequence for running an evaluation job through the SDK.

Sources: [nemo/Evaluator/README.md:6-27]()

---

## Example Notebooks

The NeMo Evaluator includes three example notebooks demonstrating different evaluation scenarios:

### Getting Started Notebook

**Location:** [nemo/Evaluator/GettingStarted/Getting Started with NeMo Evaluator.ipynb]()

**Covers:**
- Basic NeMo Evaluator usage patterns
- Evaluating Llama 3.1 8B Instruct on BigBench
- Evaluating customized models on title-generation tasks
- ROUGE metric computation
- Creating evaluation targets and configurations

**Key Concepts Demonstrated:**
- Baseline model evaluation
- Custom task evaluation
- Standard metric usage

Sources: [nemo/Evaluator/README.md:5-10]()

### LLM-as-a-Judge Notebook

**Location:** [nemo/Evaluator/LLMAsAJudge/LLM As a Judge.ipynb]()

**Covers:**
- Setting up judge-based evaluation for summarization
- Creating custom judge prompts
- Configuring judge models
- Analyzing subjective quality metrics
- Result interpretation

**Key Concepts Demonstrated:**
- Judge model selection
- Prompt engineering for judges
- Subjective quality assessment

Sources: [nemo/Evaluator/README.md:12-17]()

### Retriever and RAG Evaluation Notebook

**Location:** [nemo/Evaluator/EmbeddingAndRAG/NeMo_Evaluator_Retriever_and_RAG_Evaluation.ipynb]()

**Covers:**
- Retriever model evaluation on FiQA dataset
- Two-stage retrieval with reranking on FiQA
- RAG system evaluation with Ragas metrics
- Synthetic dataset evaluation for RAG
- Custom dataset integration

**Key Concepts Demonstrated:**
- Retrieval metric computation
- Reranking evaluation
- End-to-end RAG assessment
- Synthetic vs. real data comparison

Sources: [nemo/Evaluator/README.md:19-28]()

---

## File Structure

```
nemo/Evaluator/
├── README.md                                    # Overview and navigation
├── GettingStarted/
│   └── Getting Started with NeMo Evaluator.ipynb   # Basic usage tutorial
├── LLMAsAJudge/
│   └── LLM As a Judge.ipynb                    # Judge-based evaluation
└── EmbeddingAndRAG/
    └── NeMo_Evaluator_Retriever_and_RAG_Evaluation.ipynb  # Retrieval & RAG
```

Sources: [nemo/Evaluator/README.md:1-30]()

---

## Summary

NeMo Evaluator provides comprehensive model assessment capabilities across three primary domains:

1. **LLM Evaluation**: Benchmark testing, judge-based assessment, and task-specific metrics
2. **Retrieval Evaluation**: Embedding model assessment, reranking evaluation, and standard IR metrics
3. **RAG Evaluation**: End-to-end pipeline assessment with retrieval and generation metrics

The service integrates with other NeMo Microservices to enable the Data Flywheel's continuous improvement cycle, providing feedback to both the Customizer (for fine-tuning iterations) and Data Designer (for targeted data generation). Access is provided through the `nemo_microservices` SDK with a consistent API for creating targets, configurations, and evaluation jobs.

Sources: [nemo/Evaluator/README.md:1-30](), High-level architecture diagrams

---

