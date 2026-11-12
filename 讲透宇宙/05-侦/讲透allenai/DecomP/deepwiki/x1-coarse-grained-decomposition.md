<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/DecomP · extra page Coarse-grained Decomposition · fetched 2026-10-26 -->

# Coarse-grained Decomposition

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet](configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet)
- [configs/prompts/commaqa_e/commaqa_e_p1/decomp_coarse.txt](configs/prompts/commaqa_e/commaqa_e_p1/decomp_coarse.txt)

</details>



## Purpose and Scope

This page documents the coarse-grained decomposition strategy for the CommAQA multi-hop question answering experiment. This strategy breaks complex compositional questions into a sequence of high-level sub-queries that are all answered by a single general-purpose QA model.

For information about the alternative fine-grained decomposition approach that uses specialized QA models for different question types, see [Fine-grained Decomposition](#4.3.1). For general information about the CommAQA experiment, see [CommAQA Multi-hop Question Answering](#4.3).

## Overview

The coarse-grained decomposition strategy simplifies the multi-hop reasoning pipeline by using a uniform QA model to answer all sub-questions, regardless of their semantic type. This approach trades specialization for simplicity, making it easier to apply to diverse question types without requiring separate model configurations for each question category.

**Sources:** [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet:1-28]()

## Configuration Structure

The coarse-grained configuration is defined in `commaqae_coarse_greedy_search.jsonnet` and consists of three primary model components:

| Model Key | Model Type | Purpose | Context Access |
|-----------|------------|---------|----------------|
| `gen` | `llmqadecomp` | Decomposes complex questions into sub-questions | No (`add_context: false`) |
| `qa` | `llmqa` | Answers individual sub-questions | Yes (`add_context: true`) |
| `execute` | `execute_router` | Orchestrates execution of decomposed steps | N/A |

The configuration uses a state machine with `start_state: "gen"` and `end_state: "[EOQ]"`, following the standard DecomP inference pipeline pattern described in [Inference Pipeline](#5.1).

### Configuration Code Structure

```mermaid
graph TB
    CONFIG["commaqae_coarse_greedy_search.jsonnet"]
    
    subgraph "Model Definitions"
        GEN["gen: llmqadecomp<br/>prompt: decomp_coarse.txt<br/>add_context: false<br/>next_model: execute"]
        QA["qa: llmqa<br/>prompt: qa.txt<br/>add_context: true"]
        EXEC["execute: execute_router"]
    end
    
    subgraph "Supporting Components"
        READER["reader: drop<br/>add_paras: true"]
        PRIMS["primitives: base models<br/>+ gen_params"]
    end
    
    CONFIG --> GEN
    CONFIG --> QA
    CONFIG --> EXEC
    CONFIG --> READER
    CONFIG --> PRIMS
    
    GEN --> EXEC
    EXEC --> QA
```

**Diagram:** Configuration structure showing model relationships and data flow

**Sources:** [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet:1-28]()

## Decomposition Pipeline

The coarse-grained pipeline follows a two-stage execution pattern:

### Execution Flow

```mermaid
stateDiagram-v2
    [*] --> gen
    
    state gen {
        [*] --> LoadCoarsePrompt: decomp_coarse.txt
        LoadCoarsePrompt --> Decompose: Generate sub-questions
        Decompose --> OutputSequence: QS list with [qa] routes
    }
    
    gen --> execute: next_model
    
    state execute {
        [*] --> ParseSteps
        ParseSteps --> RouteQA: Route to [qa] model
        
        state RouteQA {
            [*] --> QAModel: Single generic model
            QAModel --> ReturnAnswer: Use context
        }
        
        RouteQA --> NextStep: Continue if more QS
        NextStep --> RouteQA: Loop
        NextStep --> Complete: If QS: [EOQ]
    }
    
    execute --> [EOQ]: All steps complete
    [EOQ] --> [*]
```

**Diagram:** State machine showing the coarse-grained decomposition execution flow

The key difference from fine-grained decomposition is that all sub-questions route to the same `qa` model, which is configured with `add_context: true` to access the knowledge base through the `drop` reader.

**Sources:** [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet:5-22]()

## Prompt Template Format

The coarse-grained prompt template (`decomp_coarse.txt`) demonstrates the decomposition pattern through few-shot examples. Each example follows a consistent structure:

### Template Structure Components

| Component | Syntax | Purpose |
|-----------|--------|---------|
| Complex Query | `QC: <question>` | The original multi-hop question |
| Sub-question | `QS: (<operation>) [qa] <question>` | Individual decomposed step |
| Answer | `A: [<list of values>]` | Answer to the sub-question |
| Reference | `#1`, `#2`, etc. | Reference to previous answer |
| Terminator | `QS: [EOQ]` | End of question sequence |

### Example Decomposition Pattern

```mermaid
graph TD
    QC["QC: What awards have movies produced by<br/>people born in 1910 won?"]
    
    QS1["QS: (select) [qa]<br/>Who were born in the year 1910?"]
    A1["A: ['Teeplemole', 'Muntaril']"]
    
    QS2["QS: (project_values_flat_unique) [qa]<br/>For which movies was #1 the producer?"]
    A2["A: ['Featsaw', 'Zalate', 'Premercy']"]
    
    QS3["QS: (project_values_flat_unique) [qa]<br/>Which awards were given to #2?"]
    A3["A: ['Zorgion', 'Chowwurst', 'Hallowcock']"]
    
    EOQ["QS: [EOQ]"]
    
    QC --> QS1
    QS1 --> A1
    A1 --> QS2
    QS2 --> A2
    A2 --> QS3
    QS3 --> A3
    A3 --> EOQ
```

**Diagram:** Example decomposition showing sequential sub-question answering with intermediate results

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_coarse.txt:1-8]()

## Query Types and Operations

The coarse-grained decomposition uses operation annotations to indicate the semantic type of each sub-question. These operations guide the reasoning process but all questions are still routed to the same `qa` model.

### Supported Operations

| Operation | Description | Example Usage |
|-----------|-------------|---------------|
| `(select)` | Filter entities based on criteria | "Who were born in the year 1910?" |
| `(project_values_flat_unique)` | Extract attribute values and flatten | "For which movies was #1 the producer?" |

### Multi-hop Reasoning Pattern

The prompt template includes six complete examples covering common multi-hop patterns:

```mermaid
graph LR
    subgraph "Example 1: Birth Year → Production → Awards"
        E1_1["(select)<br/>People born in 1910"]
        E1_2["(project)<br/>Movies produced"]
        E1_3["(project)<br/>Awards won"]
        E1_1 --> E1_2 --> E1_3
    end
    
    subgraph "Example 2: Country → Acting → Movies"
        E2_1["(select)<br/>People from Stridery"]
        E2_2["(project)<br/>Movies acted in"]
        E2_1 --> E2_2
    end
    
    subgraph "Example 3: Award → Actors → Awards"
        E3_1["(select)<br/>Erowid winning movies"]
        E3_2["(project)<br/>Actors in movie"]
        E3_3["(project)<br/>Awards to actors"]
        E3_1 --> E3_2 --> E3_3
    end
```

**Diagram:** Multi-hop reasoning patterns demonstrated in the prompt template

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_coarse.txt:1-49]()

## Answer Reference Mechanism

The coarse-grained strategy uses numerical references (`#1`, `#2`, etc.) to chain sub-questions together. These references allow later questions to depend on earlier answers without repeating the actual values.

### Reference Flow Example

```mermaid
sequenceDiagram
    participant Gen as gen model
    participant Exec as execute_router
    participant QA as qa model
    participant KB as Knowledge Base (drop reader)
    
    Gen->>Exec: QS: (select) [qa] Who were born in 1910?
    Exec->>QA: Route to qa model
    QA->>KB: Query with context
    KB-->>QA: Context paragraphs
    QA-->>Exec: A: ["Teeplemole", "Muntaril"]
    
    Gen->>Exec: QS: (project) [qa] For which movies was #1 the producer?
    Note over Exec: Replace #1 with ["Teeplemole", "Muntaril"]
    Exec->>QA: Route to qa model
    QA->>KB: Query with context + previous answer
    KB-->>QA: Context paragraphs
    QA-->>Exec: A: ["Featsaw", "Zalate", "Premercy"]
    
    Gen->>Exec: QS: (project) [qa] Which awards were given to #2?
    Note over Exec: Replace #2 with ["Featsaw", "Zalate", "Premercy"]
    Exec->>QA: Route to qa model
    QA->>KB: Query with context + previous answer
    KB-->>QA: Context paragraphs
    QA-->>Exec: A: ["Zorgion", "Chowwurst", "Hallowcock"]
    
    Gen->>Exec: QS: [EOQ]
    Exec-->>Gen: Final answer: ["Zorgion", "Chowwurst", "Hallowcock"]
```

**Diagram:** Sequence diagram showing answer reference resolution during execution

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_coarse.txt:1-8]()

## Code Entity Mapping

The following table maps natural language concepts to specific code entities in the DecomP codebase:

| Natural Language | Code Entity | Location |
|------------------|-------------|----------|
| Coarse-grained config | `commaqae_coarse_greedy_search.jsonnet` | [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet]() |
| Decomposition prompt | `decomp_coarse.txt` | Loaded by `gen` model's `prompt_file` parameter |
| Generic QA prompt | `qa.txt` | Loaded by `qa` model's `prompt_file` parameter |
| Decomposition model | `llmqadecomp` | `gen` model's `name` parameter |
| QA model | `llmqa` | `qa` model's `name` parameter |
| Execution orchestrator | `execute_router` | `execute` model's `name` parameter |
| Knowledge base reader | `drop` | `reader.name` parameter |
| Context access | `add_context: true` | Enables knowledge base access for `qa` model |
| Prompt variable | `std.extVar("promptid")` | Allows switching between prompt versions (e.g., p1) |

**Sources:** [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet:1-28](), [configs/prompts/commaqa_e/commaqa_e_p1/decomp_coarse.txt:1-49]()

## Comparison with Fine-grained Decomposition

The following table summarizes key differences between coarse-grained and fine-grained decomposition strategies:

| Aspect | Coarse-grained | Fine-grained |
|--------|----------------|--------------|
| **QA Models** | Single `qa` model for all sub-questions | Specialized models: `simp_qa`, `pos_qa`, `aw_qa` |
| **Prompt Files** | `decomp_coarse.txt`, `qa.txt` | `decomp_fine.txt`, `aw_qa.txt`, `pos_qa.txt`, `simp_qa.txt` |
| **Specialization** | Generic approach for all question types | Type-specific models for different semantic categories |
| **Configuration Complexity** | Simpler (2 main models) | More complex (4+ models) |
| **Model Routing** | All routes to `[qa]` | Routes to `[simp_qa]`, `[pos_qa]`, `[aw_qa]` based on question type |
| **Context Access** | `qa` model has `add_context: true` | All specialized models have `add_context: true` |

### Architectural Comparison

```mermaid
graph TB
    subgraph "Coarse-grained Architecture"
        CG_INPUT["Complex Question"]
        CG_GEN["gen: llmqadecomp<br/>decomp_coarse.txt"]
        CG_EXEC["execute: execute_router"]
        CG_QA["qa: llmqa<br/>qa.txt<br/>(handles all types)"]
        
        CG_INPUT --> CG_GEN
        CG_GEN --> CG_EXEC
        CG_EXEC --> CG_QA
        CG_QA --> CG_EXEC
    end
    
    subgraph "Fine-grained Architecture"
        FG_INPUT["Complex Question"]
        FG_GEN["gen: llmqadecomp<br/>decomp_fine.txt"]
        FG_EXEC["execute: execute_router"]
        FG_SIMP["simp_qa: llmqa<br/>simp_qa.txt"]
        FG_POS["pos_qa: llmqa<br/>pos_qa.txt"]
        FG_AW["aw_qa: llmqa<br/>aw_qa.txt"]
        
        FG_INPUT --> FG_GEN
        FG_GEN --> FG_EXEC
        FG_EXEC --> FG_SIMP
        FG_EXEC --> FG_POS
        FG_EXEC --> FG_AW
        FG_SIMP --> FG_EXEC
        FG_POS --> FG_EXEC
        FG_AW --> FG_EXEC
    end
```

**Diagram:** Architectural comparison showing model structure differences

For detailed information about fine-grained decomposition, see [Fine-grained Decomposition](#4.3.1).

**Sources:** [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet:1-28]()

## Usage

To run inference with the coarse-grained decomposition strategy:

```bash
python decomp/inference/configurable_inference.py \
  --input_path datasets/commaqa_e/dev_iid.json \
  --config_path configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet \
  --promptid p1 \
  --output_path output/commaqae_coarse_predictions.json
```

The `promptid` variable selects the prompt directory (e.g., `commaqa_e_p1`) that contains both `decomp_coarse.txt` and `qa.txt` files.

**Sources:** [configs/inference/commaqa_e/commaqae_coarse_greedy_search.jsonnet:10,17]()

---

