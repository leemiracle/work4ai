<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mishax · page 5 Mechanistic Interpretability Guide · fetched 2026-10-26 -->

# Mechanistic Interpretability Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [mishax/ast_patcher.py](mishax/ast_patcher.py)
- [mishax/examples/gemma.py](mishax/examples/gemma.py)
- [mishax/safe_greenlet.py](mishax/safe_greenlet.py)

</details>



## Purpose and Scope

This guide provides a comprehensive overview of using Mishax for mechanistic interpretability research on neural networks, particularly language models. Mechanistic interpretability aims to understand how models work internally by examining their activations and manipulating internal states during forward passes. This document covers the process of instrumenting models, capturing internal activations, and performing targeted interventions to test causal hypotheses about model behavior.

For information about the core utilities that power these capabilities, see [AST Patcher](#2) and [Safe Greenlet](#3). For a concrete implementation example, see [Gemma Instrumentation Example](#4).

Sources: [README.md:5-11]()

## Mechanistic Interpretability Overview

Mechanistic interpretability focuses on understanding neural networks by directly examining their internal mechanisms rather than treating them as black boxes. With Mishax, this involves:

1. **Instrumentation**: Inserting probe points at key locations in model code
2. **Activation capture**: Examining internal representations during execution
3. **Targeted intervention**: Modifying intermediate values to test hypotheses
4. **Causal analysis**: Analyzing how modifications affect model outputs

Mishax combines two powerful capabilities to enable this research:
- Runtime code modification via AST patching
- Structured concurrency via safe greenlets

This allows researchers to observe and modify values at any point in a model's forward pass without needing to fork and modify the original model codebase.

```mermaid
flowchart TD
    subgraph "Mechanistic Interpretability Flow"
        Input["Input"] --> Model["Neural Network"]
        Model --> Output["Output"]
        
        Instrumentation["Instrumentation Code"] -->|"Insert into"| Model
        Model -->|"Expose activations"| Observer["Observer/Researcher"]
        Observer -->|"Modify activations"| Model
    end
```

Sources: [README.md:5-9](), [mishax/examples/gemma.py:16-20]()

## Instrumentation Architecture

The Mishax instrumentation architecture consists of several key components working together:

```mermaid
flowchart TD
    subgraph "Mishax Instrumentation Architecture"
        AST["AST Patcher"] -->|"1. Modifies code at runtime"| Model["Target Model"]
        Sites["Instrumentation Sites"] -->|"2. Define observation points"| Patches["Patch Definitions"]
        Patches -->|"3. Specify code modifications"| AST
        
        Model -->|"4. Yields values at sites"| SG["Safe Greenlet"]
        SG -->|"5. Exposes values to"| Callbacks["Callbacks"]
        Callbacks -->|"6. Process/modify values"| SG
        SG -->|"7. Returns modified values"| Model
    end
```

Sources: [mishax/ast_patcher.py:64-105](), [mishax/safe_greenlet.py:16-23](), [mishax/examples/gemma.py:37-78]()

### Instrumentation Sites

Instrumentation sites define specific points in the model's computation graph where you want to observe or modify values. In the Gemma example, these are implemented as an enum:

```mermaid
classDiagram
    class Site {
        <<enum>>
        INPUTS
        ATTN_INPUT_PRE_LAYERNORM
        PRE_ATTN_LAYERNORM
        KEYS
        VALUES
        QUERIES
        ATTN_LOGITS
        ATTNS
        ATTN_OUTPUT_PRE_LINEAR
        ATTN_OUTPUT
        POST_ATTN_RESIDUAL
        PRE_MLP_LAYERNORM
        MLP_HIDDEN
        MLP_HIDDEN_PRE_GATE
        MLP_POST_ACTIVATION
        MLP_OUTPUT
        FINAL_RESIDUAL
        FINAL_RESIDUAL_POST_LAYERNORM
        
        is_layer_site() bool
        path_from_block
    }
```

Each site represents a specific tensor in the model's computation. Some sites are associated with specific layers (like attention heads or MLP blocks), while others are global (like model inputs or final outputs).

Sources: [mishax/examples/gemma.py:42-78]()

### Mapping Sites to Neural Network Architecture

The following diagram maps instrumentation sites to the standard transformer architecture:

```mermaid
flowchart TD
    Input["Input Tokens"] --> Embedding["Embedding Layer"]
    Embedding --> S1["Site: INPUTS"]
    
    subgraph "Transformer Block"
        S1 --> |"Input"| LN1["LayerNorm"]
        LN1 --> S2["Site: PRE_ATTN_LAYERNORM"]
        
        S2 --> Attn["Self-Attention"]
        Attn --> |"Keys"| S3["Site: KEYS"]
        Attn --> |"Values"| S4["Site: VALUES"]
        Attn --> |"Queries"| S5["Site: QUERIES"]
        
        S3 --> AttnCalc["Attention Calculation"]
        S4 --> AttnCalc
        S5 --> AttnCalc
        
        AttnCalc --> S6["Site: ATTN_LOGITS"]
        S6 --> AttnSoftmax["Softmax"]
        AttnSoftmax --> S7["Site: ATTNS"]
        
        S7 --> AttnOut["Attention Output"]
        AttnOut --> S8["Site: ATTN_OUTPUT"]
        
        S8 --> Add1["Add & Norm"]
        Add1 --> S9["Site: POST_ATTN_RESIDUAL"]
        
        S9 --> LN2["LayerNorm"]
        LN2 --> S10["Site: PRE_MLP_LAYERNORM"]
        
        S10 --> MLP["MLP"]
        MLP --> S11["Site: MLP_HIDDEN"]
        S11 --> Gate["Gating Function"]
        Gate --> S12["Site: MLP_HIDDEN_PRE_GATE"]
        S12 --> Act["Activation Function"]
        Act --> S13["Site: MLP_POST_ACTIVATION"]
        S13 --> MLPOut["MLP Output"]
        MLPOut --> S14["Site: MLP_OUTPUT"]
        
        S14 --> Add2["Add & Norm"]
        Add2 --> S15["Site: FINAL_RESIDUAL"]
    end
    
    S15 --> NextBlock["Next Block or Final LayerNorm"]
    NextBlock --> S16["Site: FINAL_RESIDUAL_POST_LAYERNORM"]
```

Sources: [mishax/examples/gemma.py:42-78](), [mishax/examples/gemma.py:96-182]()

## Setting Up Instrumentation

### Creating AST Patches

AST patches define how to modify the original model code to insert instrumentation. Each patch specifies:
1. Original code to match
2. Modified code with instrumentation

The Gemma example defines patches for:
- Attention module
- FeedForward module
- Block module
- Transformer module

For example, to instrument attention logits, this patch is used:

```
# Original code
'logits = jnp.einsum("BTNH,BSNH->BTNS", query_scaled, key_proj)'

# Modified code with instrumentation
'''
query_scaled = tag(self, Site.QUERIES, query_scaled)
logits = jnp.einsum("BTNH,BSNH->BTNS", query_scaled, key_proj)
logits = tag(self, Site.ATTN_LOGITS, logits)
'''
```

These patches are organized into `ModuleASTPatcher` objects that target specific modules.

Sources: [mishax/examples/gemma.py:96-194](), [mishax/ast_patcher.py:64-105]()

### Installing Patches

Patches must be installed before the target modules are imported:

```mermaid
sequenceDiagram
    participant User
    participant Patcher as "ModuleASTPatcher"
    participant Model as "Model Code"
    
    User->>Patcher: Define patches
    User->>Patcher: Call install() or install_clean()
    Patcher->>Model: Modify code at module level
    User->>User: Import model modules (if using install_clean)
    User->>User: Create model
```

The Gemma example provides two installation methods:
- `install()`: Use when modules are already imported
- `install_clean()`: Use before importing modules (preferred for cleaner patching)

Sources: [mishax/examples/gemma.py:196-206](), [mishax/ast_patcher.py:125-166]()

## Working with Callbacks

Callbacks are functions that receive values from instrumentation sites and can optionally modify them.

### Callback Types

Mishax supports different callback patterns:

```mermaid
classDiagram
    class Callback {
        <<Type Alias>>
        int|None layer
        Site site
        jax.Array value
        returns jax.Array|None
    }
    
    class _SelectedCallback {
        callback: Callback
        layer: int|None
        site: Site
        __call__(value)
    }
    
    class GreenletYield {
        __call__(layer, site, value)
        tree_flatten_with_keys()
        tree_unflatten()
    }
    
    Callback <|-- _SelectedCallback
    Callback <|-- GreenletYield
```

A callback should:
- Accept parameters for layer, site, and the JAX array value
- Return either a modified value (to replace the original) or None (to keep the original)

Sources: [mishax/examples/gemma.py:209-244]()

### Using GreenletYield for Interactive Exploration

The `GreenletYield` callback is particularly useful as it yields control back to the calling code, allowing for interactive exploration and modification:

```mermaid
sequenceDiagram
    participant Model as "Instrumented Model"
    participant GY as "GreenletYield"
    participant SG as "SafeGreenlet"
    participant User as "User Code"
    
    User->>User: Create GreenletYield callback
    User->>Model: Run with callback
    
    loop For each instrumentation site
        Model->>GY: Reach instrumentation site
        GY->>SG: yield_(layer, site, value)
        SG->>User: Yield control with (layer, site, value)
        User->>User: Analyze value
        User->>User: Optionally modify value
        User->>SG: Send back original or modified value
        SG->>GY: Return value
        GY->>Model: Continue execution with value
    end
```

Sources: [mishax/examples/gemma.py:262-293](), [mishax/safe_greenlet.py:182-193]()

## Common Workflows

### Activation Capture

```mermaid
flowchart TD
    Start["Start"] --> Setup["Set up instrumentation"]
    Setup --> Callback["Create logging callback"]
    Callback --> RunModel["Run model with callback"]
    RunModel --> StoreActivations["Store activations by layer and site"]
    StoreActivations --> Analyze["Analyze activations"]
```

### Targeted Intervention

```mermaid
flowchart TD
    Start["Start"] --> Setup["Set up instrumentation"]
    Setup --> Callback["Create intervention callback"]
    Callback --> RunModel["Run model with callback"]
    RunModel --> Intervene["Modify values at specific sites"]
    Intervene --> Compare["Compare to baseline output"]
    Compare --> Analyze["Analyze impact of intervention"]
```

### Causal Tracing

```mermaid
flowchart TD
    Start["Start"] --> BaseRun["Baseline model run"]
    BaseRun --> StoreBase["Store baseline activations"]
    StoreBase --> RunPatched["Run with patched activations"]
    RunPatched --> CompareOutputs["Compare outputs"]
    CompareOutputs --> Analyze["Identify causal paths"]
```

Sources: [mishax/examples/gemma.py:209-293]()

## Implementation Example

The following diagram shows how to implement a basic activation capture workflow using Mishax:

```mermaid
flowchart TD
    subgraph "Setup Phase"
        S1["1. Define Site enum"]
        S2["2. Create AST patches with tag() calls"]
        S3["3. Create ModuleASTPatcher objects"]
        S4["4. Install patches"]
    end
    
    subgraph "Callback Phase"
        C1["1. Define GreenletYield callback"]
        C2["2. Create vars_from_callback"]
        C3["3. Set up safe_greenlet context"]
    end
    
    subgraph "Execution Phase"
        E1["1. Create model input"]
        E2["2. Run model with callback vars"]
        E3["3. Process yielded activations"]
        E4["4. Optionally modify values"]
    end
    
    S1 --> S2 --> S3 --> S4
    S4 --> C1 --> C2 --> C3
    C3 --> E1 --> E2 --> E3 --> E4
```

Sources: [mishax/examples/gemma.py:16-293]()

## Best Practices

When using Mishax for mechanistic interpretability:

1. **Performance considerations**:
   - Cache activations when possible rather than recomputing
   - Be aware that intercepting every site can slow down execution

2. **JAX compatibility**:
   - Ensure callbacks are JAX-compatible (use JAX operations)
   - Be careful with tracer leaks when working with JAX values

3. **Patching safety**:
   - Test patches thoroughly as model code changes can break them
   - Use minimal patches focused on specific components of interest

4. **Memory management**:
   - Be mindful of memory usage when storing large activations
   - Consider using streaming approaches for large models

Sources: [mishax/examples/gemma.py:264-277](), [mishax/ast_patcher.py:90-105](), [README.md:13-15]()

## Conclusion

Mishax provides a powerful framework for mechanistic interpretability research, enabling deep inspection and modification of neural network internals without invasive code changes. By combining AST patching and structured concurrency, it allows researchers to test hypotheses about how models process information and make decisions.

For practical examples, see the [Gemma Instrumentation Example](#4), which demonstrates these techniques on a production-grade language model.

Sources: [README.md:5-11](), [mishax/examples/gemma.py:16-20]()

---

