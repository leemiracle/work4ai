<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/llm-steer-instruct · page 2 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data/format/all_base_x_all_instructions_filtered.jsonl](data/format/all_base_x_all_instructions_filtered.jsonl)
- [ifeval_scripts/README.md](ifeval_scripts/README.md)

</details>



This document introduces the fundamental concepts underlying the activation steering approach used in this repository and the taxonomy of instructions that the system can handle. It provides conceptual background for understanding how the system improves instruction-following behavior in language models.

For detailed implementation of activation steering, see [Activation Steering Methodology](#2.1). For comprehensive documentation of constraint types, see [Instruction Types and Constraint Taxonomy](#2.2). For details on how prompts are engineered, see [Prompt Transformation System](#2.3).

---

## Overview

The llm-steer-instruct system applies **activation steering** to improve language models' ability to follow specific instructions. The approach is based on two core ideas:

1. **Steering vectors represent instruction-following behavior**: The difference in a model's internal activations when processing a prompt with versus without an instruction captures the neural pattern associated with that instruction.

2. **Instructions are categorized by constraint type**: The system handles a taxonomy of instruction types (format, length, keywords, etc.) that are evaluated using the IFEval framework.

The relationship between these concepts is illustrated below:

```mermaid
graph TB
    subgraph "Conceptual Layer"
        Instruction["Instruction Concept<br/>(e.g., 'respond in JSON')"]
        Steering["Steering Vector<br/>(neural representation)"]
        Application["Steered Generation<br/>(instruction adherence)"]
    end
    
    subgraph "Implementation Layer"
        Prompt["prompt_without_instruction<br/>+ single_instruction_id"]
        Repr["representations/<br/>HDF5 files"]
        Hook["activation_addition_hook<br/>direction_projection_hook"]
    end
    
    subgraph "Evaluation Layer"
        IFEval["instruction_id_list<br/>kwargs"]
        Metrics["follow_all_instructions<br/>accuracy"]
    end
    
    Instruction --> Prompt
    Prompt --> Repr
    Repr --> Steering
    Steering --> Hook
    Hook --> Application
    
    Instruction --> IFEval
    Application --> Metrics
    
    style Repr fill:#f9f9f9
    style Hook fill:#f9f9f9
```

**Sources:** [README.md:9-12](), [data/format/all_base_x_all_instructions_filtered.jsonl:1-45]()

---

## Activation Steering Fundamentals

### Paired Input Methodology

Activation steering operates on the principle that the difference between a model's internal states on related inputs reveals the neural pattern associated with a specific behavior. The system computes steering vectors from **paired inputs**:

| Input Type | Description | Field in Data |
|------------|-------------|---------------|
| **Base prompt** | Query without instruction | `prompt_without_instruction` |
| **Constrained prompt** | Query with instruction applied | `model_output` |
| **Steering vector** | Difference in activations | Computed from HDF5 representations |

The pairing structure appears in the data format:

```mermaid
graph LR
    subgraph "Data Record Structure"
        Base["prompt_without_instruction<br/>'Write a summary of...'"]
        Constrained["model_output<br/>'Write a summary...in JSON format'"]
        InstID["single_instruction_id<br/>'detectable_format:json_format'"]
        Kwargs["single_instruction_kwargs<br/>{}"]
    end
    
    Base --> Compute["compute_representations.py"]
    Constrained --> Compute
    InstID --> Compute
    Kwargs --> InstID
    
    Compute --> Diff["Δ = repr_with - repr_without"]
    Diff --> HDF5["representations/*.h5<br/>per-layer activations"]
```

**Sources:** [data/format/all_base_x_all_instructions_filtered.jsonl:1](), [README.md:11-12]()

### Steering Vector Properties

Steering vectors have three key properties exploited by the system:

1. **Layer-specific**: Each steering vector is computed for specific transformer layers, requiring layer search to identify optimal steering locations
2. **Linearly composable**: Multiple steering vectors can be applied simultaneously for multi-instruction scenarios (see [Multi-Instruction Composition](#5.4))
3. **Transferable**: Steering vectors from instruction-tuned models can improve base models (see [Cross-Model Experiments](#7.1))

---

## Instruction Constraint Taxonomy

### Primary Constraint Categories

The system handles instructions organized into a hierarchical taxonomy. The top-level categories are:

```mermaid
graph TB
    Root["Instruction Constraints"]
    
    Root --> Keywords["keywords:<br/>forbidden_words<br/>frequency<br/>existence<br/>letter_frequency"]
    Root --> Length["length_constraints:<br/>number_sentences<br/>number_words<br/>number_paragraphs<br/>nth_paragraph_first_word"]
    Root --> Format["detectable_format:<br/>json_format<br/>title<br/>number_bullet_lists<br/>multiple_sections<br/>number_highlighted_sections<br/>constrained_response"]
    Root --> Content["detectable_content:<br/>number_placeholders<br/>postscript"]
    Root --> Case["change_case:<br/>english_lowercase<br/>english_capital<br/>capital_word_frequency"]
    Root --> Lang["language:<br/>response_language"]
    Root --> StartEnd["startend:<br/>end_checker<br/>quotation"]
    Root --> Combo["combination:<br/>repeat_prompt<br/>two_responses"]
    Root --> Punct["punctuation:<br/>no_comma"]
    
    style Keywords fill:#fff4e1
    style Length fill:#ffe1e1
    style Format fill:#e1f5ff
```

**Sources:** [data/format/all_base_x_all_instructions_filtered.jsonl:1-50]()

### Instruction ID Structure

Each instruction is identified by a composite key: `{category}:{subtype}_{modifier}`. Examples from the data:

| Full Instruction ID | Category | Subtype | Modifier | Example Kwargs |
|---------------------|----------|---------|----------|----------------|
| `keywords:forbidden_words` | keywords | forbidden_words | - | `{'forbidden_words': ['moser', 'glassworks']}` |
| `length_constraints:number_sentences_at least` | length_constraints | number_sentences | at least | `{'relation': 'at least', 'num_sentences': 60}` |
| `detectable_format:json_format` | detectable_format | json_format | - | `{}` |
| `keywords:frequency_less than` | keywords | frequency | less than | `{'relation': 'less than', 'keyword': 'right', 'frequency': 2}` |

The `instruction_id_list` field contains all instructions applied to a prompt, while `single_instruction_id` identifies individual constraints for steering vector computation.

**Sources:** [data/format/all_base_x_all_instructions_filtered.jsonl:1-10]()

### Module-to-Constraint Mapping

Different modules handle different constraint categories:

```mermaid
graph TB
    subgraph "format/ Module"
        FModule["format/compute_representations.py<br/>format/evaluate.py"]
        FConst["detectable_format:*<br/>change_case:*<br/>language:*<br/>startend:*<br/>combination:*<br/>punctuation:*<br/>detectable_content:*"]
    end
    
    subgraph "length/ Module"
        LModule["length/compute_representations.py<br/>length/evaluate.py"]
        LConst["length_constraints:*"]
    end
    
    subgraph "keywords/ Module"
        KModule["keywords/compute_representations.py<br/>keywords/evaluate.py"]
        KConst["keywords:forbidden_words<br/>keywords:existence<br/>keywords:frequency<br/>keywords:letter_frequency"]
    end
    
    subgraph "composition/ Module"
        CModule["composition/evaluate_format_plus_length.py"]
        CConst["Multiple constraints<br/>simultaneously"]
    end
    
    FConst --> FModule
    LConst --> LModule
    KConst --> KModule
    CConst --> CModule
    
    FModule -.->|"pre_computed_ivs/"| CModule
    LModule -.->|"representations/"| CModule
```

**Sources:** [README.md:22-47]()

---

## Data Flow and Representation Pipeline

### From Natural Language to Steering Vectors

The system transforms natural language instructions into steering vectors through a structured pipeline:

```mermaid
graph TD
    subgraph "Input Data"
        BaseQuery["prompt_without_instruction"]
        Constraint["single_instruction_id<br/>single_instruction_kwargs"]
    end
    
    subgraph "Prompt Engineering"
        ICL["icl_prompt_with_single_instruction<br/>(in-context learning example)"]
        Final["model_output<br/>(constrained prompt)"]
    end
    
    subgraph "Representation Extraction"
        CompReps["compute_representations.py"]
        HDF5Store["representations/<br/>{model}_{constraint}.h5<br/>shape: [N, num_layers, hidden_dim]"]
    end
    
    subgraph "Steering Vector Computation"
        Diff["Δ = repr_with - repr_without"]
        Layer["find_best_layer.py<br/>layer_search_out/"]
        PreComp["pre_compute_ivs.py<br/>pre_computed_ivs/*.h5"]
    end
    
    BaseQuery --> ICL
    Constraint --> ICL
    ICL --> Final
    
    BaseQuery --> CompReps
    Final --> CompReps
    CompReps --> HDF5Store
    
    HDF5Store --> Diff
    Diff --> Layer
    Layer --> PreComp
    
    style HDF5Store fill:#f9f9f9
    style PreComp fill:#f9f9f9
```

**Sources:** [README.md:64-77](), [data/format/all_base_x_all_instructions_filtered.jsonl:1]()

### Key Data Structures

The system uses specific JSON structures throughout the pipeline:

**Input Record** (`all_base_x_all_instructions_filtered.jsonl`):
```json
{
  "single_instruction_id": "detectable_format:json_format",
  "single_instruction_kwargs": {},
  "prompt_without_instruction": "Write a summary of...",
  "model_output": "Write a summary... in JSON format.",
  "instruction_id_list": ["detectable_format:json_format"],
  "instruction_id_list_for_eval": ["detectable_format:json_format"],
  "kwargs": [{}]
}
```

**HDF5 Representation Structure**:
- Dataset keys: `{prompt_hash}_{instruction_id}`
- Shape: `[num_layers, hidden_dimension]`
- Stores last token activations per layer

**Sources:** [data/format/all_base_x_all_instructions_filtered.jsonl:19-20]()

---

## Validation and Constraint Filtering

### The `is_valid` Field

Data records include an `is_valid` field indicating whether the constraint was successfully applied during prompt engineering. This filters prompts where constraint integration was problematic:

```mermaid
graph LR
    Original["Original IFEval Prompt"]
    PromptEng["Prompt Transformation<br/>(constraint integration)"]
    Valid{"is_valid == true"}
    
    Original --> PromptEng
    PromptEng --> Valid
    Valid -->|Yes| Include["Include in<br/>all_base_x_all_instructions_filtered.jsonl"]
    Valid -->|No| Exclude["Exclude from dataset"]
    
    Include --> CompReps["compute_representations.py"]
```

All records in `all_base_x_all_instructions_filtered.jsonl` have `"is_valid": true`, meaning only successfully transformed prompts are used for steering vector computation.

**Sources:** [data/format/all_base_x_all_instructions_filtered.jsonl:1-50]()

---

## Relationship to Evaluation

### IFEval Integration

The constraint taxonomy directly aligns with the IFEval evaluation framework. Each `instruction_id_list_for_eval` corresponds to specific IFEval checkers:

| Instruction Family | IFEval Checker | Verification Method |
|-------------------|----------------|---------------------|
| `detectable_format:json_format` | `is_json_format` | Parse response as JSON |
| `length_constraints:number_sentences` | `check_number_sentences` | Count sentences using NLTK |
| `keywords:forbidden_words` | `check_forbidden_words` | String matching (case-insensitive) |
| `startend:end_checker` | `check_ending` | Suffix matching |
| `detectable_format:number_bullet_lists` | `check_bullet_list` | Count markdown bullets |

The system evaluates steering effectiveness using the `follow_all_instructions` metric, which requires all constraints in `instruction_id_list_for_eval` to be satisfied.

**Sources:** [ifeval_scripts/README.md:1-44](), [data/format/all_base_x_all_instructions_filtered.jsonl:1]()

---

## Summary

The core concepts underlying this system are:

1. **Activation steering** computes instruction-specific neural patterns from paired inputs (with/without instruction)
2. **Constraint taxonomy** organizes instructions into 9 major categories with specific subtypes and parameters
3. **Modular implementation** maps constraint families to specialized modules (`format/`, `length/`, `keywords/`, `composition/`)
4. **Evaluation alignment** ensures steering targets match IFEval's standardized instruction-following metrics

These concepts enable the system to systematically improve instruction adherence across diverse constraint types by manipulating model activations during inference.

**Sources:** [README.md:1-165](), [data/format/all_base_x_all_instructions_filtered.jsonl:1-50](), [ifeval_scripts/README.md:1-44]()

---

