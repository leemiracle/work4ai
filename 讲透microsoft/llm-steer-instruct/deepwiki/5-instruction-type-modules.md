<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/llm-steer-instruct · page 5 Instruction Type Modules · fetched 2026-10-26 -->

# Instruction Type Modules

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data/format/all_base_x_all_instructions_filtered.jsonl](data/format/all_base_x_all_instructions_filtered.jsonl)
- [ifeval_scripts/README.md](ifeval_scripts/README.md)

</details>



## Purpose and Scope

This document provides an overview of the three primary instruction-type modules that implement activation steering for different categories of constraints: **format instructions**, **length instructions**, and **keyword instructions**. Each module follows a similar activation steering methodology but with workflows tailored to the specific characteristics of its constraint type. The document also covers the **composition module** that enables multi-instruction steering by combining vectors from multiple modules.

For detailed information about individual modules:
- Format instructions pipeline → see [Format Instructions Module](#5.1)
- Length instructions pipeline → see [Length Instructions Module](#5.2)  
- Keyword instructions pipeline → see [Keyword Instructions Module](#5.3)
- Multi-instruction composition → see [Multi-Instruction Composition](#5.4)

For foundational concepts about activation steering methodology → see [Activation Steering Methodology](#2.1)  
For the underlying constraint taxonomy → see [Instruction Types and Constraint Taxonomy](#2.2)

---

## Module Overview and Architecture

The repository implements three specialized modules organized in separate directories, each handling a distinct category of instruction-following constraints. These modules share common infrastructure (see [Infrastructure and Utilities](#3)) but differ significantly in their pipeline complexity and evaluation strategies.

### Directory Structure and Key Scripts

```mermaid
graph TB
    subgraph format["format/ Directory"]
        f_compute["compute_representations.py"]
        f_layer["find_best_layer.py"]
        f_perp["compute_response_perplexity.py"]
        f_pre["pre_compute_ivs.py"]
        f_eval["evaluate.py"]
        f_load["load_results.py"]
    end
    
    subgraph length["length/ Directory"]
        l_compute["compute_representations.py"]
        l_eval["evaluate.py"]
        l_load["load_results.py"]
    end
    
    subgraph keywords["keywords/ Directory"]
        k_compute["compute_representations.py"]
        k_perp["compute_response_perplexity.py"]
        k_eval["evaluate.py"]
        k_load["load_results.py"]
    end
    
    subgraph composition["composition/ Directory"]
        c_eval["evaluate_format_plus_length.py"]
        c_load["load_results.py"]
    end
    
    subgraph config["config/ Directory"]
        cfg_format["format/*.yaml"]
        cfg_length["length/*.yaml"]
        cfg_keywords["keywords/*.yaml"]
        cfg_comp["composition/*.yaml"]
    end
    
    cfg_format --> f_compute
    cfg_format --> f_layer
    cfg_format --> f_eval
    
    cfg_length --> l_compute
    cfg_length --> l_eval
    
    cfg_keywords --> k_compute
    cfg_keywords --> k_eval
    
    cfg_comp --> c_eval
    
    f_compute --> f_layer
    f_layer --> f_perp
    f_perp --> f_pre
    f_pre --> f_eval
    f_eval --> f_load
    
    l_compute --> l_eval
    l_eval --> l_load
    
    k_compute --> k_perp
    k_perp --> k_eval
    k_eval --> k_load
    
    f_pre -.->|"format vectors"| c_eval
    l_compute -.->|"length representations"| c_eval
    c_eval --> c_load
```

**Sources:** [README.md:22-48]()

---

## Constraint Taxonomy to Module Mapping

The instruction type modules correspond to specific categories within the IFEval constraint taxonomy, with each module specialized for evaluating and steering particular types of instructions.

```mermaid
graph LR
    subgraph Taxonomy["Constraint Taxonomy (from IFEval)"]
        detect_format["detectable_format:<br/>json_format, number_bullet_lists,<br/>multiple_sections, title,<br/>number_highlighted_sections"]
        detect_content["detectable_content:<br/>number_placeholders,<br/>postscript"]
        change_case["change_case:<br/>english_capital,<br/>english_lowercase,<br/>capital_word_frequency"]
        language["language:<br/>response_language"]
        startend["startend:<br/>end_checker, quotation"]
        punctuation["punctuation:<br/>no_comma"]
        
        length_const["length_constraints:<br/>number_sentences,<br/>number_paragraphs,<br/>number_words,<br/>nth_paragraph_first_word"]
        
        keywords_cat["keywords:<br/>forbidden_words,<br/>existence,<br/>frequency,<br/>letter_frequency"]
        
        combination["combination:<br/>repeat_prompt,<br/>two_responses"]
    end
    
    subgraph Modules["Instruction Type Modules"]
        format_mod["Format Module<br/>(format/)"]
        length_mod["Length Module<br/>(length/)"]
        keywords_mod["Keywords Module<br/>(keywords/)"]
        comp_mod["Composition Module<br/>(composition/)"]
    end
    
    detect_format --> format_mod
    detect_content --> format_mod
    change_case --> format_mod
    language --> format_mod
    startend --> format_mod
    punctuation --> format_mod
    combination --> format_mod
    
    length_const --> length_mod
    
    keywords_cat --> keywords_mod
    
    format_mod -.-> comp_mod
    length_mod -.-> comp_mod
```

**Sources:** [data/format/all_base_x_all_instructions_filtered.jsonl:1-20](), [README.md:62-107]()

---

## Pipeline Complexity Comparison

The three modules implement pipelines of varying complexity, reflecting the different challenges in steering each instruction type. The table below summarizes the key differences:

| Module | Stages | Layer Search | Perplexity Analysis | Pre-computation | Key Challenge |
|--------|--------|--------------|---------------------|-----------------|---------------|
| **Format** | 5 | ✓ (validate on subset) | ✓ (quality proxy) | ✓ (store vectors) | Rich taxonomy (28+ subtypes), quality preservation |
| **Length** | 2 | ✗ (direct evaluation) | ✗ | ✗ | High-level semantics, continuous values |
| **Keywords** | 3 | ✗ (direct evaluation) | ✓ (validation quality) | ✗ | Binary constraints, word-level precision |
| **Composition** | 1 | ✗ (reuses components) | ✗ | ✗ (loads from modules) | Multi-constraint coordination |

**Sources:** [README.md:62-115]()

### Format Instructions: Full 5-Stage Pipeline

The format module implements the most comprehensive pipeline due to its broad constraint taxonomy and the need to balance instruction adherence with response quality.

```mermaid
graph LR
    stage1["Stage 1:<br/>compute_representations.py<br/>Extract hidden states"]
    stage2["Stage 2:<br/>find_best_layer.py<br/>Search optimal layer"]
    stage3["Stage 3:<br/>compute_response_perplexity.py<br/>Quality assessment"]
    stage4["Stage 4:<br/>pre_compute_ivs.py<br/>Store steering vectors"]
    stage5["Stage 5:<br/>evaluate.py<br/>Test performance"]
    
    config1["config/format/<br/>compute_representations.yaml"]
    config2["config/format/<br/>find_best_layer.yaml"]
    config3["config/format/<br/>evaluation.yaml"]
    
    repr_out["format/representations/<br/>*.h5"]
    layer_out["format/layer_search_out/<br/>*.jsonl"]
    iv_out["format/pre_computed_ivs/<br/>*.h5"]
    eval_out["format/out/<br/>*.jsonl"]
    
    config1 --> stage1
    stage1 --> repr_out
    repr_out --> stage2
    config2 --> stage2
    stage2 --> layer_out
    layer_out --> stage3
    stage3 --> stage4
    stage4 --> iv_out
    iv_out --> stage5
    config3 --> stage5
    stage5 --> eval_out
```

**Sources:** [README.md:62-82]()

### Length Instructions: Simplified 2-Stage Pipeline

The length module uses a streamlined pipeline that computes representations and directly evaluates without intermediate optimization steps.

```mermaid
graph LR
    stage1["Stage 1:<br/>compute_representations.py<br/>Extract hidden states"]
    stage2["Stage 2:<br/>evaluate.py<br/>Direct evaluation"]
    
    config1["config/length/<br/>compute_representations.yaml"]
    config2["config/length/<br/>evaluation.yaml"]
    
    repr_out["length/representations/<br/>*.h5"]
    eval_out["length/out/<br/>*.jsonl"]
    
    config1 --> stage1
    stage1 --> repr_out
    repr_out --> stage2
    config2 --> stage2
    stage2 --> eval_out
```

**Sources:** [README.md:84-92]()

### Keywords Instructions: Intermediate 3-Stage Pipeline

The keywords module adds perplexity analysis to the basic pipeline for validation quality assessment, but skips layer search and pre-computation.

```mermaid
graph LR
    stage1["Stage 1:<br/>compute_representations.py<br/>Extract hidden states"]
    stage2["Stage 2:<br/>compute_response_perplexity.py<br/>Validation quality"]
    stage3["Stage 3:<br/>evaluate.py<br/>Test performance"]
    
    config1["config/keywords/<br/>compute_representations.yaml"]
    config2["config/keywords/<br/>evaluation.yaml"]
    
    repr_out["keywords/representations/<br/>*.h5"]
    eval_out["keywords/out/<br/>*.jsonl"]
    
    config1 --> stage1
    stage1 --> repr_out
    repr_out --> stage2
    stage2 --> stage3
    config2 --> stage3
    stage3 --> eval_out
```

**Sources:** [README.md:95-107]()

---

## Common Patterns Across Modules

Despite pipeline differences, all modules share fundamental patterns in their implementation and configuration.

### Shared Script Names and Purposes

All modules include these core scripts:

| Script Name | Purpose | Format | Length | Keywords |
|-------------|---------|--------|--------|----------|
| `compute_representations.py` | Extract paired hidden states | ✓ | ✓ | ✓ |
| `evaluate.py` | Generate steered outputs | ✓ | ✓ | ✓ |
| `load_results.py` | Analyze metrics | ✓ | ✓ | ✓ |
| `compute_response_perplexity.py` | Quality proxy via GPT-2 | ✓ | ✗ | ✓ |
| `find_best_layer.py` | Layer optimization | ✓ | ✗ | ✗ |
| `pre_compute_ivs.py` | Vector storage | ✓ | ✗ | ✗ |

**Sources:** [README.md:22-48]()

### Configuration Management Pattern

Each module uses Hydra for declarative configuration management with YAML files structured consistently:

```mermaid
graph TB
    subgraph compute["Representation Computation Configs"]
        fc["config/format/<br/>compute_representations.yaml"]
        lc["config/length/<br/>compute_representations.yaml"]
        kc["config/keywords/<br/>compute_representations.yaml"]
    end
    
    subgraph eval["Evaluation Configs"]
        fe["config/format/<br/>evaluation.yaml"]
        le["config/length/<br/>evaluation.yaml"]
        ke["config/keywords/<br/>evaluation.yaml"]
        ce["config/composition/<br/>evaluation.yaml"]
    end
    
    subgraph params["Common Parameters"]
        model["model_name:<br/>gemma-2-9b-it"]
        data["data_file:<br/>constraint-specific"]
        layer["steering_layer:<br/>layer index"]
        method["steering_method:<br/>activation_addition/<br/>direction_projection"]
    end
    
    fc --> params
    lc --> params
    kc --> params
    fe --> params
    le --> params
    ke --> params
    ce --> params
```

**Sources:** [README.md:18]()

### Data Flow Pattern

All modules process data through a consistent pipeline structure:

1. **Input:** Base queries from `data/ifeval_wo_instructions.jsonl` or constraint-specific files
2. **Paired Prompts:** With and without instructions (generated via prompt transformation)
3. **Representations:** Hidden states stored in `{module}/representations/*.h5`
4. **Outputs:** Generated responses in `{module}/out/*.jsonl`
5. **Evaluation:** IFEval metrics computed via `ifeval_scripts/`

**Sources:** [README.md:62-107]()

---

## Composition Module Architecture

The composition module implements multi-instruction steering by combining steering vectors from multiple modules, demonstrating the linear composability of activation steering.

```mermaid
graph TB
    subgraph inputs["Input Sources"]
        format_ivs["format/pre_computed_ivs/<br/>*.h5<br/>(pre-computed vectors)"]
        length_reps["length/representations/<br/>*.h5<br/>(representations)"]
    end
    
    subgraph composition["composition/ Module"]
        eval_script["evaluate_format_plus_length.py"]
        config["config/composition/<br/>evaluation.yaml"]
    end
    
    subgraph steering["Steering Application"]
        hook1["Format Hook<br/>(layer N)"]
        hook2["Length Hook<br/>(layer M)"]
        model["Model Generation"]
    end
    
    subgraph output["Output"]
        results["composition/out/<br/>*.jsonl<br/>(satisfies both constraints)"]
        load["load_results.py"]
    end
    
    format_ivs --> eval_script
    length_reps --> eval_script
    config --> eval_script
    
    eval_script --> hook1
    eval_script --> hook2
    hook1 --> model
    hook2 --> model
    model --> results
    results --> load
```

The composition module:
- **Reuses artifacts** from format (pre-computed vectors) and length (representations)
- **Applies multiple hooks** at different layers simultaneously
- **Evaluates satisfaction** of both constraints using IFEval framework
- **Does not require** separate representation computation or layer search

**Sources:** [README.md:109-115]()

---

## Module Selection Guidelines

When working with this codebase, select the appropriate module based on the constraint category:

| Constraint Type | Module | Key Considerations |
|----------------|--------|-------------------|
| Response structure (JSON, bullets, sections) | `format/` | Use full pipeline with layer search for optimal quality |
| Response length (sentences, words, paragraphs) | `length/` | Direct evaluation sufficient; no layer optimization needed |
| Word inclusion/exclusion | `keywords/` | Include perplexity step for validation quality assessment |
| Multiple constraints simultaneously | `composition/` | Requires pre-computed artifacts from other modules |
| Case conversion, language, punctuation | `format/` | Treated as format constraints despite different semantics |

**Cross-Module Experiments:** The format module supports cross-model transfer (steering vectors from instruction-tuned models applied to base models) via the `cross_model` flag in evaluation configs. See [Cross-Model Experiments](#7.1) for details.

**Sources:** [README.md:62-115]()

---

## Next Steps

For detailed documentation of each module's implementation:
- **Format Module:** See [Format Instructions Module](#5.1) for the 5-stage pipeline, constraint subtypes, and pre-computation strategy
- **Length Module:** See [Length Instructions Module](#5.2) for high-level constraints and simplified evaluation
- **Keywords Module:** See [Keyword Instructions Module](#5.3) for keyword set management and validation strategies  
- **Composition Module:** See [Multi-Instruction Composition](#5.4) for multi-constraint coordination and hook management

For understanding the underlying activation steering methodology that all modules share, see [Activation Steering Methodology](#2.1).

---

