<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ai-foundations · page 2 Core Library Reference · fetched 2026-10-26 -->

# Core Library Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ai_foundations/feedback/course_1/slm/__init__.py](ai_foundations/feedback/course_1/slm/__init__.py)
- [ai_foundations/feedback/utils.py](ai_foundations/feedback/utils.py)
- [ai_foundations/generation/loaders.py](ai_foundations/generation/loaders.py)
- [ai_foundations/ngram/model.py](ai_foundations/ngram/model.py)
- [ai_foundations/visualizations/__init__.py](ai_foundations/visualizations/__init__.py)
- [ai_foundations/visualizations/plots.py](ai_foundations/visualizations/plots.py)

</details>



## Purpose and Scope

This document provides a reference overview of the `ai_foundations` Python package, which serves as the core library supporting the educational labs in this repository. The package contains reusable utilities for language modeling, visualization, training, embeddings, and automated feedback testing.

This page serves as a navigation hub for the core library's major components. For detailed information about specific modules and their APIs, see the following subsections:

- For language model utilities, see [Language Models](#2.1)
- For plotting and visualization functions, see [Visualization System](#2.2)
- For model training utilities, see [Training Utilities](#2.3)
- For embedding operations, see [Embeddings Module](#2.4)
- For testing and feedback mechanisms, see [Feedback and Testing System](#2.5)

For information about how these components are used in educational contexts, see [Course 1: Language Model Foundations](#3), [Course 2: Advanced Tokenization and Embeddings](#4), and [Course 3: Neural Network Training Fundamentals](#5).

**Sources:** [ai_foundations/visualizations/__init__.py:1-28](), [ai_foundations/generation/loaders.py:1-71](), [ai_foundations/ngram/model.py:1-193]()

## Package Structure

The `ai_foundations` package is organized into the following top-level modules:

| Module | Purpose | Key Components |
|--------|---------|----------------|
| `ngram` | Statistical language modeling | `NGramModel` class |
| `generation` | Pre-trained model loading and text generation | `load_gemma()`, prompt utilities |
| `visualizations` | Plotting and visualization utilities | `plot_next_token()`, `plot_loss_curve()`, `plot_data_and_mlp()` |
| `training` | Model training loops and callbacks | `create_model()`, `train_mlp()`, custom callbacks |
| `embeddings` | Token embedding operations | `load_gemma_embeddings()`, `plot_embeddings_tsne()` |
| `feedback` | Automated testing and hints | `test_*` functions, `render_feedback()` |
| `machine_learning` | Neural network utilities | Dataset preparation, evaluation metrics |

**Sources:** [ai_foundations/visualizations/__init__.py:1-28](), [ai_foundations/feedback/course_1/slm/__init__.py:1-23]()

## Module Overview

### ngram Module

The `ngram` module provides statistical language modeling capabilities through the `NGramModel` class. This class estimates conditional probabilities from token sequences and generates text using learned n-gram statistics.

**Key Class:** `NGramModel` ([ai_foundations/ngram/model.py:30-193]())

**Primary Methods:**
- `estimate_probabilities()` - Builds probability distributions from training data
- `generate()` - Generates text using random or greedy sampling

For detailed documentation, see [Language Models](#2.1).

**Sources:** [ai_foundations/ngram/model.py:1-193]()

### generation Module

The `generation` module provides utilities for loading pre-trained Gemma transformer models and generating text with them.

**Key Function:** `load_gemma()` ([ai_foundations/generation/loaders.py:28-71]())

Returns a tuple of `(tokenizer, model, params)` for Gemma-1B or Gemma-4B models. Supports standard models and attention-weight variants.

For detailed documentation, see [Language Models](#2.1).

**Sources:** [ai_foundations/generation/loaders.py:1-71]()

### visualizations Module

The `visualizations` module contains comprehensive plotting functions for analyzing models, data, and training progress.

**Exported Functions** ([ai_foundations/visualizations/__init__.py:18-28]()):
- `plot_next_token()` - Visualizes probability distributions over next tokens
- `plot_word_frequencies()` - Creates log-log plots demonstrating Zipf's law
- `plot_loss_curve()` - Plots training and validation loss over epochs
- `plot_accuracy_curve()` - Plots accuracy metrics over epochs
- `plot_data_and_decision_boundary()` - Visualizes 2D classification boundaries
- `plot_data_and_mlp()` - Shows MLP decision boundaries with train/test data
- `visualize_mlp_architecture()` - Renders neural network layer diagrams
- `visualize_hyperparameter_loss()` - Compares hyperparameter impact on loss
- `visualize_attention()` - Shows attention weight heatmaps

For detailed documentation, see [Visualization System](#2.2).

**Sources:** [ai_foundations/visualizations/__init__.py:1-28](), [ai_foundations/visualizations/plots.py:1-695]()

### training Module

The `training` module provides utilities for building and training neural network models, including custom callbacks for monitoring training progress.

**Key Components:**
- Model creation functions for transformer-based language models
- Training loop implementations with JAX/Keras
- Custom callbacks: `TextGenerator`, `CustomAccuracyPrinter`

For detailed documentation, see [Training Utilities](#2.3).

### embeddings Module

The `embeddings` module provides functions for loading, manipulating, and visualizing token embeddings from pre-trained models.

**Key Functions:**
- `load_gemma_embeddings()` - Extracts embedding matrices from Gemma models
- `plot_embeddings_tsne()` - Projects embeddings to 2D using t-SNE
- `plot_embeddings_dimensions()` - Visualizes raw embedding dimensions

For detailed documentation, see [Embeddings Module](#2.4).

### feedback Module

The `feedback` module provides automated testing infrastructure and interactive hint rendering for educational labs.

**Key Components:**
- `render_feedback()` function ([ai_foundations/feedback/utils.py:32-59]())
- Course-specific test functions organized by lab topic
- Example tests from Course 1: `test_build_vocabulary()`, `test_simple_word_tokenizer()` ([ai_foundations/feedback/course_1/slm/__init__.py:18-22]())

For detailed documentation, see [Feedback and Testing System](#2.5).

**Sources:** [ai_foundations/feedback/utils.py:1-59](), [ai_foundations/feedback/course_1/slm/__init__.py:1-23]()

## Core Architecture

### Module Interaction Diagram

```mermaid
graph TB
    subgraph ngram["ngram Module"]
        NGramModel["NGramModel class"]
        estimate_probabilities["estimate_probabilities()"]
        generate_ngram["generate()"]
    end
    
    subgraph generation["generation Module"]
        load_gemma["load_gemma()"]
        Gemma3Tokenizer["gm.text.Gemma3Tokenizer"]
        Gemma3_1B["gm.nn.Gemma3_1B"]
        Gemma3_4B["gm.nn.Gemma3_4B"]
    end
    
    subgraph visualizations["visualizations Module"]
        plot_next_token["plot_next_token()"]
        plot_word_frequencies["plot_word_frequencies()"]
        plot_loss_curve["plot_loss_curve()"]
        plot_data_and_mlp["plot_data_and_mlp()"]
        plot_data_and_decision_boundary["plot_data_and_decision_boundary()"]
        visualize_mlp_architecture["visualize_mlp_architecture()"]
    end
    
    subgraph training["training Module"]
        create_model["create_model()"]
        train_mlp["train_mlp()"]
        TextGenerator["TextGenerator callback"]
        CustomAccuracyPrinter["CustomAccuracyPrinter callback"]
    end
    
    subgraph embeddings["embeddings Module"]
        load_gemma_embeddings["load_gemma_embeddings()"]
        plot_embeddings_tsne["plot_embeddings_tsne()"]
        plot_embeddings_dimensions["plot_embeddings_dimensions()"]
    end
    
    subgraph feedback["feedback Module"]
        render_feedback["render_feedback()"]
        test_build_vocabulary["test_build_vocabulary()"]
        test_simple_word_tokenizer["test_simple_word_tokenizer()"]
        test_build_tokens_list["test_build_tokens_list()"]
    end
    
    NGramModel --> plot_next_token
    generate_ngram --> plot_word_frequencies
    
    load_gemma --> Gemma3Tokenizer
    load_gemma --> Gemma3_1B
    load_gemma --> Gemma3_4B
    Gemma3_1B --> plot_next_token
    Gemma3_4B --> plot_next_token
    
    create_model --> train_mlp
    train_mlp --> TextGenerator
    train_mlp --> CustomAccuracyPrinter
    train_mlp --> plot_loss_curve
    
    train_mlp --> plot_data_and_mlp
    visualize_mlp_architecture -.documents.- train_mlp
    
    load_gemma_embeddings --> plot_embeddings_tsne
    load_gemma_embeddings --> plot_embeddings_dimensions
    
    test_build_vocabulary --> render_feedback
    test_simple_word_tokenizer --> render_feedback
    test_build_tokens_list --> render_feedback
```

**Sources:** [ai_foundations/visualizations/__init__.py:1-28](), [ai_foundations/ngram/model.py:1-193](), [ai_foundations/generation/loaders.py:1-71](), [ai_foundations/feedback/utils.py:1-59](), [ai_foundations/feedback/course_1/slm/__init__.py:1-23]()

### Data Flow Through Core Systems

```mermaid
graph LR
    subgraph Input["Input Data"]
        RawText["Raw text strings"]
        Tokens["Token sequences"]
        TokenIDs["Token ID arrays"]
    end
    
    subgraph Models["Model Components"]
        NGramModel_flow["NGramModel"]
        GemmaModel["Gemma3_1B/4B"]
        CustomMLP["Custom MLP/SLM"]
    end
    
    subgraph Processing["Processing Functions"]
        tokenize_function["tokenize_function()"]
        Gemma3Tokenizer_flow["Gemma3Tokenizer.encode()"]
        estimate_prob["estimate_probabilities()"]
    end
    
    subgraph Outputs["Output Visualizations"]
        plot_next_token_flow["plot_next_token()"]
        plot_word_freq["plot_word_frequencies()"]
        plot_loss["plot_loss_curve()"]
        plot_mlp["plot_data_and_mlp()"]
    end
    
    subgraph Training["Training Loop"]
        train_mlp_flow["train_mlp()"]
        keras_fit["keras.Model.fit()"]
        history["history dict"]
    end
    
    RawText --> tokenize_function
    tokenize_function --> Tokens
    RawText --> Gemma3Tokenizer_flow
    Gemma3Tokenizer_flow --> TokenIDs
    
    Tokens --> estimate_prob
    estimate_prob --> NGramModel_flow
    TokenIDs --> GemmaModel
    TokenIDs --> CustomMLP
    
    NGramModel_flow --> plot_next_token_flow
    NGramModel_flow --> plot_word_freq
    GemmaModel --> plot_next_token_flow
    
    CustomMLP --> train_mlp_flow
    train_mlp_flow --> keras_fit
    keras_fit --> history
    history --> plot_loss
    
    CustomMLP --> plot_mlp
```

**Sources:** [ai_foundations/ngram/model.py:30-193](), [ai_foundations/generation/loaders.py:28-71](), [ai_foundations/visualizations/plots.py:48-335]()

## Key Classes and Functions Reference

### NGramModel Class

The `NGramModel` class provides statistical language modeling using n-gram probabilities.

| Attribute/Method | Type | Description |
|-----------------|------|-------------|
| `n` | `int` | Order of the n-gram model (e.g., 2 for bigram, 3 for trigram) |
| `probabilities` | `dict[tuple, dict[str, float]]` | Nested dictionary mapping context to next-token distributions |
| `tokenize_function` | `Callable` | Function to tokenize input strings into token lists |
| `estimate_probabilities()` | method | Estimates conditional probabilities from dataset |
| `generate()` | method | Generates text using random or greedy sampling |

**Implementation:** [ai_foundations/ngram/model.py:30-193]()

**Sources:** [ai_foundations/ngram/model.py:30-193]()

### Visualization Functions

The following table summarizes the primary visualization functions and their purposes:

| Function | Primary Use | Input Types | Output |
|----------|-------------|-------------|--------|
| `plot_next_token()` | Token probability distributions | `np.ndarray` or `dict[str, float]` | Interactive Plotly bar chart |
| `plot_word_frequencies()` | Zipf's law visualization | `collections.Counter` | Log-log matplotlib plot |
| `plot_loss_curve()` | Training progress monitoring | `dict` (Keras history) | Matplotlib line plot |
| `plot_accuracy_curve()` | Accuracy over epochs | `dict` (Keras history) | Matplotlib line plot |
| `plot_data_and_decision_boundary()` | Binary classification visualization | `jax.Array`, weight vector, bias | Matplotlib scatter + boundary |
| `plot_data_and_mlp()` | MLP decision boundaries | `jax.Array`, `keras.Model` | Matplotlib contour plot |
| `visualize_mlp_architecture()` | Neural network structure | `list[int]`, `int` | Matplotlib network diagram |
| `visualize_hyperparameter_loss()` | Hyperparameter tuning results | `dict[HyperParameterConfig, float]` | Matplotlib bar/line plots |

**Implementation:** [ai_foundations/visualizations/plots.py:1-695]()

**Sources:** [ai_foundations/visualizations/plots.py:48-695](), [ai_foundations/visualizations/__init__.py:18-28]()

### Model Loading and Generation

```mermaid
graph TD
    load_gemma_call["load_gemma(model_name)"]
    
    subgraph gemma_module["gemma library (gm)"]
        Gemma3Tokenizer_cls["gm.text.Gemma3Tokenizer"]
        Gemma3_1B_cls["gm.nn.Gemma3_1B"]
        Gemma3_4B_cls["gm.nn.Gemma3_4B"]
        load_params["gm.ckpts.load_params()"]
        CheckpointPath["gm.ckpts.CheckpointPath"]
    end
    
    load_gemma_call -->|"model_name='Gemma-1B'"| Gemma3Tokenizer_cls
    load_gemma_call -->|"model_name='Gemma-1B'"| Gemma3_1B_cls
    load_gemma_call -->|"model_name='Gemma-4B'"| Gemma3_4B_cls
    
    CheckpointPath -->|GEMMA3_1B_PT| load_params
    CheckpointPath -->|GEMMA3_4B_PT| load_params
    
    load_params --> params_output["params (model weights)"]
    Gemma3Tokenizer_cls --> tokenizer_output["tokenizer"]
    Gemma3_1B_cls --> model_output["model"]
    Gemma3_4B_cls --> model_output
    
    load_gemma_call --> return_tuple["return (tokenizer, model, params)"]
    tokenizer_output --> return_tuple
    model_output --> return_tuple
    params_output --> return_tuple
```

**Sources:** [ai_foundations/generation/loaders.py:28-71]()

### Feedback System Structure

The feedback system provides automated testing and interactive hints through a two-layer architecture:

1. **Core Utility Layer:** `render_feedback()` function ([ai_foundations/feedback/utils.py:32-59]())
2. **Course-Specific Test Layer:** Individual `test_*` functions organized by course and lab

**Example Feedback Flow:**

```mermaid
graph LR
    UserCode["User's implementation"]
    test_function["test_simple_word_tokenizer()"]
    validation["Validation logic"]
    error_detection["Error detection"]
    render_feedback_call["render_feedback(error, hint)"]
    
    UserCode --> test_function
    test_function --> validation
    validation -->|"checks fail"| error_detection
    error_detection --> render_feedback_call
    render_feedback_call --> display_html["Display HTML feedback"]
    render_feedback_call --> prompt_hint["Prompt for hint"]
    
    validation -->|"checks pass"| success_message["Display success message"]
```

**Common Test Functions (Course 1):**
- `test_build_vocabulary()` - Validates vocabulary construction
- `test_simple_word_tokenizer()` - Validates tokenizer implementation
- `test_build_tokens_list()` - Validates token list generation
- `test_index_to_token()` - Validates index-to-token mapping
- `test_max_min_seqlen()` - Validates sequence length calculations

**Sources:** [ai_foundations/feedback/utils.py:1-59](), [ai_foundations/feedback/course_1/slm/__init__.py:1-23]()

## Integration Patterns

The core library modules work together to support common workflows in the educational labs:

### Pattern 1: Model Comparison Workflow

Used in Lab 1.3 to compare n-gram and transformer models:

```mermaid
graph TD
    dataset["Africa Galore dataset"]
    
    subgraph ngram_path["N-gram Model Path"]
        tokenize_ngram["tokenize_function()"]
        NGramModel_init["NGramModel(dataset, n=3)"]
        generate_ngram_text["ngram_model.generate()"]
    end
    
    subgraph transformer_path["Transformer Model Path"]
        load_gemma_tf["load_gemma('Gemma-1B')"]
        tokenizer_encode["tokenizer.encode()"]
        model_forward["model(token_ids, params)"]
    end
    
    dataset --> tokenize_ngram
    dataset --> load_gemma_tf
    
    tokenize_ngram --> NGramModel_init
    NGramModel_init --> generate_ngram_text
    
    load_gemma_tf --> tokenizer_encode
    tokenizer_encode --> model_forward
    
    generate_ngram_text --> plot_next_token_comp["plot_next_token()"]
    model_forward --> plot_next_token_comp
```

**Sources:** [ai_foundations/ngram/model.py:1-193](), [ai_foundations/generation/loaders.py:28-71](), [ai_foundations/visualizations/plots.py:48-113]()

### Pattern 2: Training and Visualization Workflow

Used in Labs 1.5, 2.6, and throughout Course 3:

```mermaid
graph TD
    train_data["Training data (token IDs)"]
    test_data["Test data (token IDs)"]
    
    create_model_call["create_model()"]
    model_instance["keras.Model instance"]
    
    train_mlp_call["train_mlp(model, train_data, test_data)"]
    callbacks["Callbacks: TextGenerator, CustomAccuracyPrinter"]
    keras_training["keras.Model.fit()"]
    history_dict["history dict with 'loss', 'val_loss'"]
    
    train_data --> create_model_call
    create_model_call --> model_instance
    
    model_instance --> train_mlp_call
    test_data --> train_mlp_call
    
    train_mlp_call --> callbacks
    train_mlp_call --> keras_training
    keras_training --> history_dict
    
    history_dict --> plot_loss_curve_call["plot_loss_curve(history)"]
    model_instance --> plot_data_and_mlp_call["plot_data_and_mlp(features, labels, model)"]
```

**Sources:** [ai_foundations/visualizations/plots.py:304-461]()

### Pattern 3: Embedding Analysis Workflow

Used in Labs 2.5 and 2.6 for embedding exploration:

```mermaid
graph TD
    load_gemma_emb["load_gemma('Gemma-1B')"]
    extract_embeddings["load_gemma_embeddings(model, params)"]
    embedding_matrix["embedding_matrix: np.ndarray"]
    
    subgraph analysis["Embedding Analysis"]
        cosine_similarity["Compute cosine similarity"]
        nearest_neighbors["Find nearest neighbors"]
    end
    
    subgraph visualization["Embedding Visualization"]
        plot_tsne["plot_embeddings_tsne()"]
        plot_dims["plot_embeddings_dimensions()"]
    end
    
    load_gemma_emb --> extract_embeddings
    extract_embeddings --> embedding_matrix
    
    embedding_matrix --> cosine_similarity
    embedding_matrix --> nearest_neighbors
    embedding_matrix --> plot_tsne
    embedding_matrix --> plot_dims
```

**Sources:** [ai_foundations/generation/loaders.py:28-71]()

## Usage Notes

### Color Palette

All visualization functions use a consistent color palette defined in [ai_foundations/visualizations/plots.py:35]():

```python
COLOR_PALETTE = ["#FFC20A", "#0C7BDC", "#71A816"]
```

This ensures visual consistency across all plots in the educational materials.

### JAX and NumPy Compatibility

Most functions accept both JAX arrays and NumPy arrays interchangeably. The library uses `jax.numpy` for computations but converts to standard NumPy for matplotlib visualizations where necessary.

### Error Handling in Feedback System

The `render_feedback()` function handles multiple error formats:
- Two-argument errors: `ValueError(title, detail)`
- Tuple-packed errors: `ValueError((title, detail))`
- Single-argument errors: Falls back to generic title with error string as detail

Implementation: [ai_foundations/feedback/utils.py:32-59]()

**Sources:** [ai_foundations/visualizations/plots.py:35](), [ai_foundations/feedback/utils.py:32-59]()

## Related Documentation

For detailed API documentation of individual modules:
- [Language Models](#2.1) - Full API reference for `NGramModel` and `load_gemma()`
- [Visualization System](#2.2) - Complete documentation of all plotting functions
- [Training Utilities](#2.3) - Training loop implementations and callbacks
- [Embeddings Module](#2.4) - Embedding loading and visualization
- [Feedback and Testing System](#2.5) - Automated testing infrastructure

For practical usage examples in educational contexts:
- [Course 1: Language Model Foundations](#3)
- [Course 2: Advanced Tokenization and Embeddings](#4)
- [Course 3: Neural Network Training Fundamentals](#5)

---

