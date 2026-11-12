<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/course · page 3 🤗 Transformers Library Core Components · fetched 2026-10-26 -->

# 🤗 Transformers Library Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chapters/ru/_toctree.yml](chapters/ru/_toctree.yml)
- [chapters/ru/chapter2/1.mdx](chapters/ru/chapter2/1.mdx)
- [chapters/ru/chapter2/2.mdx](chapters/ru/chapter2/2.mdx)
- [chapters/ru/chapter2/3.mdx](chapters/ru/chapter2/3.mdx)
- [chapters/ru/chapter2/4.mdx](chapters/ru/chapter2/4.mdx)
- [chapters/ru/chapter2/5.mdx](chapters/ru/chapter2/5.mdx)
- [chapters/ru/chapter2/6.mdx](chapters/ru/chapter2/6.mdx)
- [chapters/ru/chapter2/7.mdx](chapters/ru/chapter2/7.mdx)
- [chapters/ru/chapter2/8.mdx](chapters/ru/chapter2/8.mdx)

</details>



This document provides an overview of the core components that make up the Hugging Face Transformers library. It explains how these components work together to enable efficient use of pre-trained transformer models for various natural language processing (NLP) tasks. For information about specific model architectures, see the related wiki pages on transformers architectures.

## Overview of Core Components

The 🤗 Transformers library provides a unified interface for working with transformer-based models. At its core, the library consists of several key components that work together in a pipeline:

```mermaid
flowchart TD
    subgraph "Core Components Pipeline"
        "RawText"["Raw Text Input"] --> "Tokenizer"["AutoTokenizer"]
        "Tokenizer" --> "ModelInputs"["Preprocessed Inputs<br>(input_ids, attention_mask)"]
        "ModelInputs" --> "Model"["AutoModel"]
        "Model" --> "HiddenStates"["Hidden States<br>(Batch, Seq, Hidden)"]
        "HiddenStates" --> "ModelHead"["Task-Specific Head"]
        "ModelHead" --> "Outputs"["Task Outputs<br>(logits, etc.)"]
        "Outputs" --> "PostProcess"["Post-processing"]
        "PostProcess" --> "Predictions"["Final Predictions"]
    end
    
    "Pipeline"["pipeline() function"] -.-> "Tokenizer"
    "Pipeline" -.-> "Model"
    "Pipeline" -.-> "PostProcess"
```

Sources: [chapters/ru/chapter2/2.mdx:56-61](). The diagram shows the complete processing pipeline from raw text to predictions.

Let's explore each of these core components in detail.

## AutoClasses: The Entry Point

The `Auto*` classes serve as the primary entry point to the library, automatically loading the appropriate implementation based on the specified pre-trained checkpoint.

```mermaid
flowchart TD
    subgraph "Auto Classes System"
        "Checkpoint"["Checkpoint Name<br>(e.g., 'bert-base-uncased')"] --> "AutoTokenizer"["AutoTokenizer.from_pretrained()"]
        "Checkpoint" --> "AutoModelClasses"["AutoModel*.from_pretrained()"]
        
        "AutoModelClasses" --> "AutoModel"["AutoModel<br>(Base architecture only)"]
        "AutoModelClasses" --> "TaskModels"["Task-Specific Models"]
        
        "TaskModels" --> "AutoSeqClass"["AutoModelForSequenceClassification"]
        "TaskModels" --> "AutoTokenClass"["AutoModelForTokenClassification"]
        "TaskModels" --> "AutoQA"["AutoModelForQuestionAnswering"]
        "TaskModels" --> "AutoCausalLM"["AutoModelForCausalLM"]
        "TaskModels" --> "AutoMaskedLM"["AutoModelForMaskedLM"]
        
        "ConfigFile"["config.json"] --> "AutoModelClasses"
        "WeightsFile"["pytorch_model.bin/tf_model.h5"] --> "AutoModelClasses"
    end
```

Sources: [chapters/ru/chapter2/3.mdx:30-47]()

The `Auto*` classes provide a convenient way to instantiate models and tokenizers without needing to know the specific implementation details. When you call `from_pretrained()` with a checkpoint name, the appropriate class is automatically selected based on the model's architecture.

## Models

Models are the core of the Transformers library, implementing various transformer architectures.

### Base Models vs Models with Heads

The library makes an important distinction between base models and models with task-specific heads:

```mermaid
flowchart TD
    subgraph "Model Architecture Components"
        "InputIds"["input_ids"] --> "Transformer"["Transformer Base Model"]
        "AttentionMask"["attention_mask"] --> "Transformer"
        "Transformer" --> "HiddenStates"["Hidden States<br>(Batch, Seq, Hidden)"]
        "HiddenStates" --> "ModelHead"["Task-Specific Head"]
        "ModelHead" --> "TaskOutput"["Task Outputs (e.g., logits)"]
    end
```

Sources: [chapters/ru/chapter2/2.mdx:174-178](), [chapters/ru/chapter2/2.mdx:214-226]()

Base models (loaded with `AutoModel`) return hidden states which represent contextualized embeddings for each token in the input sequence. These hidden states have a shape of (batch_size, sequence_length, hidden_size).

Models with heads (loaded with classes like `AutoModelForSequenceClassification`) include a task-specific component that transforms these hidden states into outputs appropriate for a specific task, such as classification logits, token predictions, or generated text.

### Model Loading and Saving

Models can be loaded from pre-trained checkpoints:

```python
from transformers import AutoModel, AutoModelForSequenceClassification

# Load base model
base_model = AutoModel.from_pretrained("bert-base-uncased")

# Load model with classification head
classifier = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased-finetuned-sst-2-english")
```

And saved to disk:

```python
model.save_pretrained("directory_on_my_computer")
# Creates config.json and pytorch_model.bin/tf_model.h5
```

Sources: [chapters/ru/chapter2/3.mdx:146-169]()

## Tokenizers

Tokenizers convert raw text into numerical representations that models can process.

### Tokenization Process

```mermaid
flowchart TD
    subgraph "Tokenization Pipeline"
        "Text"["Raw Text"] --> "Tokenize"["tokenizer.tokenize()"]
        "Tokenize" --> "StringTokens"["String Tokens"]
        "StringTokens" --> "ConvertIds"["tokenizer.convert_tokens_to_ids()"]
        "ConvertIds" --> "InputIds"["Input IDs"]
        
        "Text2"["Raw Text"] --> "TokenizerCall"["tokenizer(text, padding=True, truncation=True)"]
        "TokenizerCall" --> "InternalProcess"["Internal Processing"]
        "InternalProcess" --> "ModelInputs"["Complete Model Inputs<br>{input_ids, attention_mask, ...}"]
    end
```

Sources: [chapters/ru/chapter2/4.mdx:92-137](), [chapters/ru/chapter2/4.mdx:168-183]()

The tokenization process involves:

1. **Tokenization**: Breaking text into tokens (words, subwords, or characters)
2. **ID Conversion**: Converting tokens to numeric IDs based on a vocabulary
3. **Additional Processing**: Adding special tokens, padding, and generating attention masks

### Tokenization Strategies

The library supports several tokenization strategies:

- **Word-based**: Split text into words (large vocabulary, many unknown tokens)
- **Character-based**: Split text into characters (small vocabulary, longer sequences)
- **Subword-based**: Balance between word and character (used by most models)
  - Examples: BPE (GPT-2), WordPiece (BERT), SentencePiece (multilingual models)

Sources: [chapters/ru/chapter2/4.mdx:39-119]()

### Handling Multiple Sequences

When processing multiple sequences of different lengths, tokenizers handle padding and attention masking:

```mermaid
flowchart TD
    subgraph "Multiple Sequence Processing"
        "Sequences"["Multiple Text Sequences"] --> "TokenizeEach"["Tokenize Each Sequence"]
        "TokenizeEach" --> "VaryingLengths"["Sequences of Varying Lengths"]
        "VaryingLengths" --> "Padding"["Apply Padding to Match Lengths"]
        "Padding" --> "PaddedIds"["Padded input_ids"]
        "PaddedIds" --> "AttentionMask"["Generate attention_mask"]
        "AttentionMask" --> "MaskValues"["1 for Real Tokens, 0 for Padding"]
        "PaddedIds" --> "BatchedInput"["Batched Model Input"]
        "MaskValues" --> "BatchedInput"
    end
```

Sources: [chapters/ru/chapter2/5.mdx:188-214](), [chapters/ru/chapter2/5.mdx:266-315]()

Attention masks tell the model which tokens to "pay attention to" (1s) and which to ignore (0s). This is crucial for correctly processing batched inputs with padding.

## The Pipeline Function

The `pipeline()` function provides a high-level interface that combines all the components:

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("I've been waiting for a HuggingFace course my whole life.")
# [{'label': 'POSITIVE', 'score': 0.9598047137260437}]
```

This function:
1. Loads the appropriate tokenizer and model
2. Preprocesses the input text
3. Runs the model
4. Post-processes the output

Sources: [chapters/ru/chapter2/2.mdx:34-54]()

## Working with Inputs and Outputs

### Model Inputs

Models expect batched inputs in the form of tensors. The key inputs are:

- **input_ids**: Token IDs from the tokenizer
- **attention_mask**: Binary mask indicating which tokens should be attended to
- **token_type_ids**: (For some models) Indicates which sequence a token belongs to

Example of complete inputs:

```python
inputs = {
    'input_ids': tensor([[101, 1045, ..., 102]]),
    'attention_mask': tensor([[1, 1, ..., 1]])
}
```

Sources: [chapters/ru/chapter2/2.mdx:99-146]()

### Model Outputs

Model outputs are typically objects with attributes for different output components:

```python
outputs = model(**inputs)
# Base models return hidden states
hidden_states = outputs.last_hidden_state  # Shape: (batch_size, seq_length, hidden_size)

# Models with heads return task-specific outputs
logits = outputs.logits  # For classification models
```

For classification tasks, logits are typically converted to probabilities using softmax:

```python
import torch
import tensorflow as tf

# PyTorch
probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

# TensorFlow
probs = tf.math.softmax(outputs.logits, axis=-1)
```

Sources: [chapters/ru/chapter2/2.mdx:279-320]()

## Practical Usage Tips

### Batching and Sequence Length

- Models expect inputs in batches, even for single sequences
- Sequences longer than the model's maximum length need to be truncated
- Sequences in a batch need to be padded to the same length
- Always use attention masks with padded inputs

```python
# Process multiple sequences
sequences = ["Hello world", "This is a longer sequence that needs padding"]
inputs = tokenizer(sequences, padding=True, truncation=True, return_tensors="pt")
```

Sources: [chapters/ru/chapter2/5.mdx:40-189](), [chapters/ru/chapter2/5.mdx:326-338]()

### Matching Tokenizers and Models

Always use tokenizers and models from the same checkpoint to ensure compatibility:

```python
# Correct usage
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Incorrect usage - tokenizer and model from different checkpoints
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("gpt2")  # Will likely produce nonsensical results
```

Sources: [chapters/ru/chapter2/8.mdx:268-274]()

## Summary

The core components of the 🤗 Transformers library work together to provide a powerful yet flexible system for using transformer models:

1. **AutoClasses**: Provide a convenient entry point to load appropriate implementations
2. **Models**: Implement various transformer architectures and task-specific heads
3. **Tokenizers**: Convert text to numerical inputs for models
4. **Pipeline**: Combines all components for easy use

Understanding these core components allows you to use the library effectively, from simple pipelines to custom implementations.

---

