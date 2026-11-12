<!-- source: DeepWiki mcp.deepwiki.com · repo libingzheren/Jev-Mem · page 5 Benchmarks and Evaluation · fetched 2026-10-13 -->

# Benchmarks and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/evaluation.md](docs/evaluation.md)
- [docs/releasing.md](docs/releasing.md)
- [jev_mem/benchmarks/__init__.py](jev_mem/benchmarks/__init__.py)

</details>



This page provides a high-level overview of the evaluation infrastructure and datasets used to benchmark the Jev-Mem system. It introduces the primary benchmarks, scoring mechanisms, and data conventions, with links to child pages for detailed technical information. Understanding these components is crucial for reproducing results, conducting new experiments, and evaluating system performance.

The Jev-Mem system's performance is primarily assessed using two benchmarks: LoCoMo and LongMemEval. Evaluation involves a sophisticated scoring system that can leverage LLM judges and various metrics. All benchmark data adheres to specific conventions for loading and usage.

## LoCoMo Benchmark
The LoCoMo (Long-Context Memory) benchmark is a key tool for evaluating Jev-Mem's ability to handle long conversational contexts and complex memory interactions. It involves running the system against predefined datasets with various categories of questions. The benchmark runner allows for configuration of dataset paths, question limits, Jev-Mem configuration, and the LLM model used for answering [docs/evaluation.md:7-10]().

For details on running the LoCoMo benchmark, its dataset structure, caching mechanisms, question categories, and specific flags, see [LoCoMo Benchmark](#5.1).

Sources:
* [docs/evaluation.md:7-10]()

## LongMemEval Benchmark
The LongMemEval benchmark focuses on evaluating the system's performance in scenarios requiring long-term memory and retrieval across extended interactions. Similar to LoCoMo, it uses specific datasets and allows for configuration of the Jev-Mem system and the LLM model [docs/evaluation.md:12-14](). A key characteristic of LongMemEval is that it constructs memory separately for each question's history [docs/evaluation.md:34-34]().

For a deeper dive into the LongMemEval runner, its dataset loader, the `longmemeval_jev.py` script, and its evaluator, see [LongMemEval Benchmark](#5.2).

Sources:
* [docs/evaluation.md:12-14]()
* [docs/evaluation.md:34-34]()

## Scoring, Judges and Metrics
Evaluating Jev-Mem's performance involves a comprehensive scoring system. This system utilizes various components, including an `evaluator.py` for overall assessment, `llm_judge.py` for leveraging large language models as judges, and `test_harness.py` for orchestrating evaluation runs. Additionally, an anchor recall script is used for specific metric calculations. Optional NLTK and sentence-transformer scoring resources can be initialized on demand for specific metrics [docs/evaluation.md:22-24]().

For detailed information on the `evaluator.py`, `llm_judge.py`, `test_harness.py`, the anchor recall script, and other metric resources, see [Scoring, Judges and Metrics](#5.3).

Sources:
* [docs/evaluation.md:22-24]()

## Datasets and Examples
The integrity and reproducibility of benchmarks rely heavily on well-defined datasets and examples. The `data/` directory follows specific conventions for organizing benchmark data. The `load_dataset.py` utility is responsible for loading these datasets. The `examples/` directory contains observations and synthetic samples that can be used for testing and understanding system behavior.

For a comprehensive understanding of the `data/` conventions, the `load_dataset.py` script, and the observations and synthetic samples found in `examples/`, see [Datasets and Examples](#5.4).

### Evaluation Workflow
```mermaid
graph TD
    A[Start Evaluation] --> B{Select Benchmark};
    B -- "LoCoMo" --> C[jev_mem.benchmarks.locomo];
    B -- "LongMemEval" --> D[jev_mem.benchmarks.longmemeval];

    C -- "--dataset data/locomo10.json" --> E[Load Dataset];
    D -- "--dataset data/longmemeval_s_cleaned.json" --> E;

    E --> F[JevMemSystem Orchestrator];
    F -- "Query" --> G[LLM Provider];
    G -- "Answer" --> H[Scoring and Metrics];

    H -- "Evaluator" --> I[Results];
    I --> J[Analysis];

    subgraph Configuration
        K[jev_mem.json] --> F;
        L[Model Selection] --> G;
    end

    subgraph Ablations
        M[--no-jev-write] --> F;
        N[--no-jev-read] --> F;
        O[--jev-mock] --> F;
    end

    subgraph Caching
        P[--reuse-memory PATH] --> F;
        Q[--rebuild] --> F;
    end

    style C fill:#ace,stroke:#333,stroke-width:2px
    style D fill:#ace,stroke:#333,stroke-width:2px
    style E fill:#ace,stroke:#333,stroke-width:2px
    style F fill:#ace,stroke:#333,stroke-width:2px
    style G fill:#ace,stroke:#333,stroke-width:2px
    style H fill:#ace,stroke:#333,stroke-width:2px
    style I fill:#ace,stroke:#333,stroke-width:2px
    style J fill:#ace,stroke:#333,stroke-width:2px
    style K fill:#ace,stroke:#333,stroke-width:2px
    style L fill:#ace,stroke:#333,stroke-width:2px
    style M fill:#ace,stroke:#333,stroke-width:2px
    style N fill:#ace,stroke:#333,stroke-width:2px
    style O fill:#ace,stroke:#333,stroke-width:2px
    style P fill:#ace,stroke:#333,stroke-width:2px
    style Q fill:#ace,stroke:#333,stroke-width:2px
```
**Diagram 1: High-Level Evaluation Workflow**

This diagram illustrates the general flow of an evaluation run, from selecting a benchmark to analyzing results. It highlights the interaction between the benchmark runners, the Jev-Mem system, LLM providers, and the scoring components. Configuration options and ablation flags are also shown as inputs influencing the system's behavior during evaluation.

Sources:
* [docs/evaluation.md:7-14]()
* [docs/evaluation.md:40-41]()
* [docs/evaluation.md:50-54]()

### Evaluation Components and Code Entities
```mermaid
graph TD
    subgraph "Benchmark Runners"
        BM_LOCOMO["jev_mem.benchmarks.locomo"]
        BM_LONGMEMEVAL["jev_mem.benchmarks.longmemeval"]
    end

    subgraph "Data Handling"
        DATA_DIR["data/"]
        LOAD_DATASET["load_dataset.py"]
        EXAMPLES_DIR["examples/"]
    end

    subgraph "Jev-Mem System"
        JEV_MEM_SYSTEM["JevMemSystem Orchestrator"]
        JEV_CONFIG["config/jev_mem.json"]
        JEV_MOCK["--jev-mock"]
        NO_JEV_WRITE["--no-jev-write"]
        NO_JEV_READ["--no-jev-read"]
    end

    subgraph "Scoring and Metrics"
        EVALUATOR["evaluator.py"]
        LLM_JUDGE["llm_judge.py"]
        TEST_HARNESS["test_harness.py"]
        ANCHOR_RECALL_SCRIPT["Anchor Recall Script"]
        NLTK_RESOURCES["NLTK Resources"]
        SENTENCE_TRANSFORMER_RESOURCES["Sentence-Transformer Resources"]
    end

    BM_LOCOMO --> DATA_DIR;
    BM_LONGMEMEVAL --> DATA_DIR;
    LOAD_DATASET --> DATA_DIR;
    BM_LOCOMO --> JEV_MEM_SYSTEM;
    BM_LONGMEMEVAL --> JEV_MEM_SYSTEM;
    JEV_MEM_SYSTEM --> JEV_CONFIG;
    JEV_MEM_SYSTEM --> JEV_MOCK;
    JEV_MEM_SYSTEM --> NO_JEV_WRITE;
    JEV_MEM_SYSTEM --> NO_JEV_READ;
    JEV_MEM_SYSTEM --> EVALUATOR;
    EVALUATOR --> LLM_JUDGE;
    EVALUATOR --> TEST_HARNESS;
    EVALUATOR --> ANCHOR_RECALL_SCRIPT;
    EVALUATOR --> NLTK_RESOURCES;
    EVALUATOR --> SENTENCE_TRANSFORMER_RESOURCES;
```
**Diagram 2: Evaluation Code Entity Map**

This diagram maps the conceptual components of the evaluation framework to their corresponding code entities and files within the Jev-Mem codebase. It shows how benchmark runners interact with data, the core Jev-Mem system, and the various scoring and metric components.

Sources:
* [jev_mem/benchmarks/__init__.py:1]()
* [docs/evaluation.md:7-14]()
* [docs/evaluation.md:22-24]()
* [docs/evaluation.md:40-41]()
* [docs/evaluation.md:50-54]()

---

