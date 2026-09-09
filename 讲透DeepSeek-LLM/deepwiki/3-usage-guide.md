> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-LLM/3-usage-guide](https://deepwiki.com/deepseek-ai/DeepSeek-LLM/3-usage-guide)
> DeepWiki deepseek-ai/DeepSeek-LLM

# Usage Guide

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-LLM/blob/6712a86b/README.md?plain=1)
 
  This guide provides comprehensive instructions for utilizing DeepSeek-LLM models in various inference scenarios. It covers model loading, inference methods, hardware requirements, and optimization techniques for both base and chat model variants.

 For information about model architecture and training methodology, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-LLM/2-model-architecture).

 
## Model Selection and Setup

 DeepSeek-LLM comes in various sizes and types, each optimized for different use cases.

 
### Available Model Variants

 
```

```

 Sources: [README.md63-76](https://github.com/deepseek-ai/DeepSeek-LLM/blob/6712a86b/README.md?plain=1#L63-L76)

 
### Installation Requirements

 Before using DeepSeek-LLM, ensure you have Python 3.8 or higher and install the necessary dependencies:

 
```

```

 Sources: [README.md214-218](https://github.com/deepseek-ai/DeepSeek-LLM/blob/6712a86b/README.md?plain=1#L214-L218)

 
## Inference with Transformers Library

 The primary method for utilizing DeepSeek-LLM is through the Hugging Face Transformers library, which provides a standardized interface for model loading and text generation.

 
### Model Loading and Inference Flow

 
```

```

 Sources: [README.md220-242](https://github.com/deepseek-ai/DeepSeek-LLM/blob/6712a86b/README.md?plain=1#L220-L242) [README.md246-265](https://github.com/deepseek-ai/DeepSeek-LLM/blob/6712a86b/README.md?plain=1#L246-L265)

 
### Text Completion with Base Models

 For general text completion tasks, use the base models as follows:

 
```

```

 Sources: [README.md222-242](https://github.com/deepseek-ai/DeepSeek-LLM/blob/6712a86b/README.md?plain=1#L222-L242)

 
### Chat Completion with Chat Models

 For conversational interactions, use the chat models with properly formatted inputs:

 
```

```

 Sources: [README.md246-265](https://github.com/deepseek-ai/DeepSeek-LLM/blob/6712a86b/README.md?plain=1#L246-L265)

 
### Chat Template Structure

 DeepSeek-LLM chat models use a specific format for conversations. While `apply_chat_template()` handles this automatically, understanding the format is useful for troubleshooting or manual formatting:

 
```

```

 If not using `apply_chat_template()`, you can format conversations manually:

 
```
User: {messages[0]['content']}
```
