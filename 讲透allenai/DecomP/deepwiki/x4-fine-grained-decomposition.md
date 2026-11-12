<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/DecomP · extra page Fine-grained Decomposition · fetched 2026-10-26 -->

# Fine-grained Decomposition

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet](configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet)
- [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt](configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt)

</details>



## Purpose and Scope

This document describes the fine-grained decomposition strategy for CommAQA multi-hop question answering. Fine-grained decomposition breaks complex questions into a sequence of typed sub-questions, each routed to specialized QA models. For the alternative coarse-grained approach, see [Coarse-grained Decomposition](#4.3.2). For general CommAQA background, see [CommAQA Multi-hop Question Answering](#4.3).

## Overview

Fine-grained decomposition decomposes complex multi-hop questions into explicit sub-operations with typed routing. Unlike coarse-grained decomposition which uses general-purpose reasoning, fine-grained decomposition:

1. **Explicitly types each sub-question** (simple fact lookup, position-based query, award-based query)
2. **Routes to specialized models** based on question type
3. **Specifies operations** (select, project_values_flat_unique) for each step
4. **Maintains references** between steps using numbered placeholders (#1, #2, #3)

This approach provides maximum control over the reasoning process by explicitly encoding the query structure and data flow.

## Pipeline Architecture

### System Architecture Diagram

```mermaid
graph TB
    INPUT["Input: Complex Question<br/>(e.g., 'What awards have movies<br/>produced by people born in 1910 won?')"]
    
    GEN["gen Model<br/>Type: llmqadecomp<br/>Prompt: decomp_fine.txt<br/>add_context: false"]
    
    EXECUTE["execute Model<br/>Type: execute_router<br/>Orchestrates sub-model execution"]
    
    SIMP["simp_qa Model<br/>Type: llmqa<br/>Prompt: simp_qa.txt<br/>add_context: true"]
    
    POS["pos_qa Model<br/>Type: llmqa<br/>Prompt: pos_qa.txt<br/>add_context: true"]
    
    AW["aw_qa Model<br/>Type: llmqa<br/>Prompt: aw_qa.txt<br/>add_context: true"]
    
    READER["drop Reader<br/>add_paras: true<br/>Provides knowledge base context"]
    
    OUTPUT["Output: Final Answer<br/>with decomposition trace"]
    
    INPUT --> GEN
    GEN -->|"next_model: execute"| EXECUTE
    
    EXECUTE -->|"Route to [simp_qa]"| SIMP
    EXECUTE -->|"Route to [pos_qa]"| POS
    EXECUTE -->|"Route to [aw_qa]"| AW
    
    SIMP -->|"Result #1"| EXECUTE
    POS -->|"Result #2"| EXECUTE
    AW -->|"Result #3"| EXECUTE
    
    READER -.->|"Knowledge context"| SIMP
    READER -.->|"Knowledge context"| POS
    READER -.->|"Knowledge context"| AW
    
    EXECUTE -->|"[EOQ] reached"| OUTPUT
```

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:1-38]()

### State Transition Flow

```mermaid
stateDiagram-v2
    [*] --> gen: start_state
    
    gen --> execute: next_model
    
    state execute {
        [*] --> ParseQS
        ParseQS --> RouteToModel: Extract [model_name]
        
        RouteToModel --> simp_qa: [simp_qa]
        RouteToModel --> pos_qa: [pos_qa]
        RouteToModel --> aw_qa: [aw_qa]
        
        simp_qa --> StoreResult
        pos_qa --> StoreResult
        aw_qa --> StoreResult
        
        StoreResult --> CheckEOQ
        CheckEOQ --> ParseQS: More QS steps
        CheckEOQ --> [*]: [EOQ] reached
    }
    
    execute --> [EOQ]: end_state
    [EOQ] --> [*]
```

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:5-12]()

## Configuration Structure

The fine-grained decomposition configuration is defined in [commaqae_fine_greedy_search.jsonnet](configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet).

### Model Definitions

| Model Key | Type | Prompt Template | Add Context | Purpose |
|-----------|------|-----------------|-------------|---------|
| `gen` | `llmqadecomp` | `decomp_fine.txt` | `false` | Decomposes complex question into typed sub-questions |
| `execute` | `execute_router` | N/A | N/A | Routes sub-questions to appropriate specialized models |
| `simp_qa` | `llmqa` | `simp_qa.txt` | `true` | Answers simple factual questions (e.g., "Who was born in 1910?") |
| `pos_qa` | `llmqa` | `pos_qa.txt` | `true` | Answers position-based questions (e.g., "Who produced movie X?") |
| `aw_qa` | `llmqa` | `aw_qa.txt` | `true` | Answers award-based questions (e.g., "What awards did X win?") |

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:7-33]()

### Configuration Parameters

```jsonnet
{
  "start_state": "gen",
  "end_state": "[EOQ]",
  "models": {
    "gen": {
      "name": "llmqadecomp",
      "prompt_file": "configs/prompts/commaqa_e/commaqa_e_" + std.extVar("promptid") + "/decomp_fine.txt",
      "next_model": "execute",
      "end_state": "[EOQ]",
      "add_context": false
    },
    "execute": {
      "name": "execute_router"
    }
  },
  "reader": {
    "name": "drop",
    "add_paras": true
  }
}
```

Key configuration aspects:
- **`start_state: "gen"`** - Inference begins at the `gen` model
- **`next_model: "execute"`** - After decomposition, control passes to the router
- **`add_context: false`** for `gen` - Decomposition doesn't need knowledge base
- **`add_context: true`** for QA models - Sub-questions require factual grounding
- **`reader: "drop"`** with `add_paras: true` - Provides paragraph-level context

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:4-37]()

## Prompt Template Format

The decomposition prompt follows a structured few-shot format defined in [decomp_fine.txt](configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt).

### Structure Components

```mermaid
graph TB
    QC["QC: Complex Question<br/>(Query to decompose)"]
    QS1["QS: (operation) [model] sub-question #1<br/>(First decomposition step)"]
    A1["A: ['result1', 'result2']<br/>(Answer to step 1)"]
    QS2["QS: (operation) [model] sub-question #2<br/>(References #1 if needed)"]
    A2["A: ['result3', 'result4']<br/>(Answer to step 2)"]
    QS3["QS: (operation) [model] sub-question #3<br/>(References #2 if needed)"]
    A3["A: ['result5', 'result6']<br/>(Answer to step 3)"]
    EOQ["QS: [EOQ]<br/>(End of query marker)"]
    
    QC --> QS1
    QS1 --> A1
    A1 --> QS2
    QS2 --> A2
    A2 --> QS3
    QS3 --> A3
    A3 --> EOQ
```

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:1-49]()

### Format Syntax

Each decomposition example consists of:

1. **`QC:`** - Original complex question
2. **`QS:`** - Question step with three components:
   - **(operation)** - Data operation type: `select`, `project_values_flat_unique`
   - **[model]** - Target model: `[simp_qa]`, `[pos_qa]`, `[aw_qa]`
   - **sub-question text** - Simplified question, may reference previous results with `#1`, `#2`, etc.
3. **`A:`** - Answer in JSON list format
4. **`QS: [EOQ]`** - End marker

### Example Decomposition

From [decomp_fine.txt:1-8]():

```
QC: What awards have movies produced by people born in 1910 won?
QS: (select) [simp_qa] Who were born in the year 1910?
A: ["Teeplemole", "Muntaril"]
QS: (project_values_flat_unique) [pos_qa] For which movies was #1 the producer?
A: ["Featsaw", "Zalate", "Premercy"]
QS: (project_values_flat_unique) [aw_qa] Which awards were given to #2?
A: ["Zorgion", "Chowwurst", "Hallowcock"]
QS: [EOQ]
```

**Decomposition logic:**
1. **Step 1** - Use `simp_qa` to find people born in 1910 → Result stored as `#1`
2. **Step 2** - Use `pos_qa` to find movies produced by `#1` → Result stored as `#2`
3. **Step 3** - Use `aw_qa` to find awards given to `#2` → Final answer

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:1-8]()

### Operation Types

| Operation | Purpose | Typical Usage |
|-----------|---------|---------------|
| `select` | Initial filtering/selection from knowledge base | First step to identify entities matching criteria |
| `project_values_flat_unique` | Extract and flatten related values | Later steps to traverse relationships and aggregate results |

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:2-48]()

## Specialized Sub-models

The fine-grained strategy employs three specialized QA models, each optimized for different question types.

### Sub-model Comparison

```mermaid
graph LR
    subgraph "Question Type Classification"
        Q["Incoming Sub-question"]
    end
    
    subgraph "simp_qa"
        S1["Simple Factual Queries"]
        S2["Examples:<br/>- Who was born in year X?<br/>- Who is from country Y?"]
    end
    
    subgraph "pos_qa"
        P1["Position/Role Queries"]
        P2["Examples:<br/>- Who produced movie X?<br/>- Who acted in movie Y?<br/>- Who directed movie Z?"]
    end
    
    subgraph "aw_qa"
        A1["Award-related Queries"]
        A2["Examples:<br/>- What awards did X win?<br/>- Which movies won award Y?"]
    end
    
    Q -->|"[simp_qa]"| S1
    Q -->|"[pos_qa]"| P1
    Q -->|"[aw_qa]"| A1
    
    S1 --> S2
    P1 --> P2
    A1 --> A2
```

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:15-29]()

### Model Specifications

#### simp_qa

- **Type:** `llmqa`
- **Prompt:** `simp_qa.txt`
- **Context:** Knowledge base enabled (`add_context: true`)
- **Purpose:** Answers straightforward factual questions requiring simple lookup

**Configuration:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:25-29]()

#### pos_qa

- **Type:** `llmqa`
- **Prompt:** `pos_qa.txt`
- **Context:** Knowledge base enabled (`add_context: true`)
- **Purpose:** Answers questions about roles and positions (producer, actor, director, writer)

**Configuration:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:20-24]()

#### aw_qa

- **Type:** `llmqa`
- **Prompt:** `aw_qa.txt`
- **Context:** Knowledge base enabled (`add_context: true`)
- **Purpose:** Answers questions about awards given to entities

**Configuration:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:15-19]()

## Execution Flow

### Step-by-Step Execution

```mermaid
sequenceDiagram
    participant User
    participant gen as gen (llmqadecomp)
    participant execute as execute (execute_router)
    participant simp as simp_qa (llmqa)
    participant pos as pos_qa (llmqa)
    participant aw as aw_qa (llmqa)
    participant reader as drop Reader
    
    User->>gen: Complex question
    gen->>execute: Decomposed steps (QS sequence)
    
    execute->>execute: Parse QS: (select) [simp_qa]
    execute->>reader: Request context
    reader->>simp: Provide paragraphs
    execute->>simp: "Who were born in 1910?"
    simp->>execute: ["Teeplemole", "Muntaril"]
    execute->>execute: Store as #1
    
    execute->>execute: Parse QS: (project) [pos_qa]
    execute->>execute: Substitute #1 in question
    execute->>reader: Request context
    reader->>pos: Provide paragraphs
    execute->>pos: "For which movies was Teeplemole, Muntaril the producer?"
    pos->>execute: ["Featsaw", "Zalate", "Premercy"]
    execute->>execute: Store as #2
    
    execute->>execute: Parse QS: (project) [aw_qa]
    execute->>execute: Substitute #2 in question
    execute->>reader: Request context
    reader->>aw: Provide paragraphs
    execute->>aw: "Which awards were given to Featsaw, Zalate, Premercy?"
    aw->>execute: ["Zorgion", "Chowwurst", "Hallowcock"]
    
    execute->>execute: Parse QS: [EOQ]
    execute->>User: Final answer with trace
```

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:1-38](), [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:1-8]()

### Reference Resolution

When the `execute_router` encounters references like `#1` or `#2` in sub-questions:

1. **Parse the QS line** to identify the model and question text
2. **Identify reference placeholders** (`#1`, `#2`, etc.)
3. **Substitute references** with actual results from previous steps
4. **Route to specified model** with the resolved question
5. **Store the result** for potential use in subsequent steps

Example transformation:
```
Original QS: "For which movies was #1 the producer?"
After #1 = ["Teeplemole", "Muntaril"]
Resolved:    "For which movies was Teeplemole, Muntaril the producer?"
```

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:1-49]()

## Usage Example

### Running Fine-grained Decomposition

```bash
# Run fine-grained decomposition with prompt ID p1
allennlp predict \
  configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet \
  data/commaqa_e/test.json \
  --output-file predictions/commaqae_fine_p1.json \
  --include-package decomp \
  --predictor configurable_inference \
  --use-dataset-reader \
  --cuda-device 0 \
  --overrides '{"environ": {"promptid": "p1"}}'
```

The `promptid` environment variable controls which prompt variant to use, corresponding to directories under [configs/prompts/commaqa_e/]().

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:10](), [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:17](), [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:22](), [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:27]()

## Complete Example Traces

### Example 1: Multi-hop Award Query

**Input Question:**
```
What awards have movies produced by people born in 1910 won?
```

**Decomposition Trace:**
```
QS: (select) [simp_qa] Who were born in the year 1910?
A: ["Teeplemole", "Muntaril"]

QS: (project_values_flat_unique) [pos_qa] For which movies was #1 the producer?
A: ["Featsaw", "Zalate", "Premercy"]

QS: (project_values_flat_unique) [aw_qa] Which awards were given to #2?
A: ["Zorgion", "Chowwurst", "Hallowcock"]

QS: [EOQ]
```

**Final Answer:** `["Zorgion", "Chowwurst", "Hallowcock"]`

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:1-8]()

### Example 2: Country-based Actor Query

**Input Question:**
```
What movies have people from the country Stridery acted in?
```

**Decomposition Trace:**
```
QS: (select) [simp_qa] Who is from the country Stridery?
A: ["Gastrat"]

QS: (project_values_flat_unique) [pos_qa] Which movies has #1 been an actor in?
A: ["Partnershipmaker", "Nilitude", "Warpstone"]

QS: [EOQ]
```

**Final Answer:** `["Partnershipmaker", "Nilitude", "Warpstone"]`

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:10-15]()

### Example 3: Three-hop Award Chain

**Input Question:**
```
What awards have the actors of the Erowid winning movies received?
```

**Decomposition Trace:**
```
QS: (select) [aw_qa] Which movies were given the Erowid award?
A: ["Dewbar", "Caudacite"]

QS: (project_values_flat_unique) [pos_qa] Who are the actors in the movie #1?
A: ["Wetherality", "Lougerière", "Gigabut"]

QS: (project_values_flat_unique) [aw_qa] Which awards were given to #2?
A: ["Aniconder", "Trifogation"]

QS: [EOQ]
```

**Final Answer:** `["Aniconder", "Trifogation"]`

**Sources:** [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:17-24]()

## Key Design Principles

The fine-grained decomposition strategy embodies several important principles:

1. **Explicit Type Routing** - Each sub-question explicitly declares its target model, providing clear execution paths
2. **Operation Annotations** - Data operations (`select`, `project_values_flat_unique`) make the reasoning structure explicit
3. **Compositional References** - The `#1`, `#2` notation enables information flow between steps
4. **Specialized Knowledge Access** - Only QA models receive knowledge base context, while decomposition remains abstract
5. **Deterministic Execution** - The `execute_router` follows explicit routing instructions without additional LLM calls

These principles enable precise control over the reasoning process while maintaining interpretability of the decomposition steps.

**Sources:** [configs/inference/commaqa_e/commaqae_fine_greedy_search.jsonnet:1-38](), [configs/prompts/commaqa_e/commaqa_e_p1/decomp_fine.txt:1-49]()

---

