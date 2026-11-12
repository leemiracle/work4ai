<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/latent-multi-hop-reasoning · page 4 Utility Modules · fetched 2026-10-26 -->

# Utility Modules

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



The utility modules in the `src/` directory provide shared functionality that supports all experimental approaches in the latent multi-hop reasoning codebase. These modules handle common operations such as data processing, model interactions, tokenization, and specialized evaluation logic, allowing the main entry points to focus on their specific experimental objectives.

For detailed documentation of individual utility modules, see sections [4.1](#4.1) through [4.6](#4.6). For information about the main entry points that use these utilities, see [Main Entry Points](#3).

## Architecture Overview

The utility modules form a layered architecture where core utilities provide fundamental operations, while experiment-specific utilities implement specialized analysis functions:

```mermaid
graph TB
    subgraph "Core Utilities"
        data_utils["data_utils.py<br/>• read_dataframe<br/>• efficient_batchify<br/>• batchify"]
        model_utils["model_utils.py<br/>• get_unembedding_matrix<br/>• get_layers<br/>• is_instruction_tuned"]
        tokenization_utils["tokenization_utils.py<br/>• to_tokens<br/>• find_substrings<br/>• get_completion"]
    end
    
    subgraph "Experiment-Specific Utilities"
        inspection_utils["inspection_utils.py<br/>• run_rq1<br/>• run_rq2<br/>• activation_patching"]
        evaluation_utils["evaluation_utils.py<br/>• run_completion<br/>• shortcut_free_evaluation<br/>• patchscopes_evaluation"]
        patchscopes_utils["patchscopes_utils.py<br/>• get_hidden_states<br/>• generate_with_patching<br/>• layer_intervention"]
    end
    
    data_utils --> inspection_utils
    data_utils --> evaluation_utils
    data_utils --> patchscopes_utils
    
    model_utils --> inspection_utils
    model_utils --> evaluation_utils
    model_utils --> patchscopes_utils
    
    tokenization_utils --> inspection_utils
    tokenization_utils --> evaluation_utils
    tokenization_utils --> patchscopes_utils
```

*Sources: [README.md:88-92]()*

## Utility Module Usage by Main Entry Points

Each main entry point utilizes different combinations of utility modules based on its experimental requirements:

```mermaid
graph LR
    subgraph "Main Entry Points"
        inspect_latent_reasoning["inspect_latent_reasoning.py<br/>Paper 1 Experiments"]
        evaluate_latent_reasoning["evaluate_latent_reasoning.py<br/>Paper 2 Shortcut-Free"]
        run_patchscopes["run_patchscopes.py<br/>Paper 2 Patchscopes"]
    end
    
    subgraph "Utility Modules"
        data_utils["data_utils.py"]
        model_utils["model_utils.py"]
        tokenization_utils["tokenization_utils.py"]
        inspection_utils["inspection_utils.py"]
        evaluation_utils["evaluation_utils.py"] 
        patchscopes_utils["patchscopes_utils.py"]
    end
    
    inspect_latent_reasoning --> data_utils
    inspect_latent_reasoning --> model_utils
    inspect_latent_reasoning --> tokenization_utils
    inspect_latent_reasoning --> inspection_utils
    
    evaluate_latent_reasoning --> data_utils
    evaluate_latent_reasoning --> model_utils
    evaluate_latent_reasoning --> evaluation_utils
    
    run_patchscopes --> data_utils
    run_patchscopes --> model_utils
    run_patchscopes --> evaluation_utils
    run_patchscopes --> patchscopes_utils
```

*Sources: [README.md:88-92]()*

## Module Classification and Dependencies

The utility modules can be categorized by their scope and dependencies:

| Module | Category | Purpose | Used By |
|--------|----------|---------|---------|
| `data_utils.py` | Core | DataFrame operations, batch processing | All entry points |
| `model_utils.py` | Core | Model loading, layer access, random seed control | All entry points |
| `tokenization_utils.py` | Core | Text-to-token conversion, substring finding | All entry points |
| `inspection_utils.py` | Paper 1 Specific | RQ1/RQ2 experiments, activation patching | `inspect_latent_reasoning.py` |
| `evaluation_utils.py` | Paper 2 Specific | Completion generation, shortcut-free evaluation | `evaluate_latent_reasoning.py`, `run_patchscopes.py` |
| `patchscopes_utils.py` | Paper 2 Specific | Hidden state extraction, layer interventions | `run_patchscopes.py` |

*Sources: [README.md:88-92]()*

## Functional Flow Between Utilities

The utilities work together in a typical experimental pipeline following this data flow:

```mermaid
flowchart TD
    read_dataframe["data_utils.read_dataframe<br/>Load CSV datasets"]
    to_tokens["tokenization_utils.to_tokens<br/>Convert text to tokens"]
    efficient_batchify["data_utils.efficient_batchify<br/>Create memory-efficient batches"]
    get_layers["model_utils.get_layers<br/>Access transformer layers"]
    
    subgraph "Experiment-Specific Processing"
        run_rq1["inspection_utils.run_rq1<br/>First-hop analysis"]
        run_rq2["inspection_utils.run_rq2<br/>Second-hop analysis"] 
        run_completion["evaluation_utils.run_completion<br/>Generate completions"]
        get_hidden_states["patchscopes_utils.get_hidden_states<br/>Extract layer representations"]
    end
    
    find_substrings["tokenization_utils.find_substrings<br/>Locate entities in text"]
    get_completion["tokenization_utils.get_completion<br/>Extract generated text"]
    
    read_dataframe --> to_tokens
    to_tokens --> efficient_batchify
    efficient_batchify --> get_layers
    
    get_layers --> run_rq1
    get_layers --> run_rq2
    get_layers --> run_completion
    get_layers --> get_hidden_states
    
    run_rq1 --> find_substrings
    run_rq2 --> find_substrings
    run_completion --> get_completion
    get_hidden_states --> find_substrings
```

*Sources: [README.md:88-92]()*

## Cross-Module Integration Patterns

The utility modules implement several integration patterns that enable seamless collaboration:

### Shared Configuration Pattern
Core utilities like `model_utils.set_random_seed()` and `model_utils.is_instruction_tuned()` provide configuration services used by all experiment-specific modules.

### Data Pipeline Pattern  
`data_utils` functions create standardized data structures that flow through `tokenization_utils` processing and into experiment-specific utilities.

### Model Abstraction Pattern
`model_utils.get_unembedding_matrix()` and `model_utils.get_layers()` provide consistent interfaces to transformer internals, enabling experiment utilities to work across different model architectures.

### Batch Processing Pattern
`data_utils.efficient_batchify()` creates memory-optimized batches that all experiment utilities can process uniformly, regardless of their specific analysis requirements.

*Sources: [README.md:88-92]()*

---

