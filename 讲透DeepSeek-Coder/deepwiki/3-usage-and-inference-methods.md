> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Coder/3-usage-and-inference-methods](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/3-usage-and-inference-methods)
> DeepWiki deepseek-ai/DeepSeek-Coder

# Usage and Inference Methods

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1)
 
  This document provides a comprehensive guide to using DeepSeek Coder for inference across different use cases. It covers the various inference methods supported by the models, including code completion, code insertion, chat-based interaction, repository-level completion, and high-throughput inference with vLLM. For information about fine-tuning the models, see [Fine-tuning](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/5-fine-tuning).

 
## Inference Methods Overview

 DeepSeek Coder offers multiple inference methods depending on your use case. Each method is optimized for specific scenarios and leverages different capabilities of the models.

 
```

```

 Sources: [README.md11-27](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L11-L27)

 The table below summarizes each inference method, its appropriate model types, and typical use cases:

 
| Inference Method | Model Type | Use Case | Key Features |
|---|---|---|---|
| Code Completion | Base | Generate code from comments/prompts | Simple, straightforward generation |
| Code Insertion (FIM) | Base | Fill gaps in existing code | Contextual code insertion |
| Chat Model Inference | Instruct | Interactive coding assistance | Dialog-based interaction |
| Repository-Level Completion | Base | Complete code across multiple files | Cross-file understanding |
| vLLM Inference | Both | High-throughput production scenarios | Efficient, parallel processing |

 Sources: [README.md67-269](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L67-L269)

 
## Inference Process Flow

 All inference methods follow a similar process flow, with variations in how inputs are processed and outputs are generated.

 
```

```

 Sources: [README.md76-142](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L76-L142)

 
## Code Completion

 Code completion is the most basic inference method, where the model generates code based on a comment or prompt.

 
### Usage Example

 
```

```

 Sources: [README.md76-85](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L76-L85)

 
### Key Parameters for Generation

 
| Parameter | Description | Example Value |
|---|---|---|
| max_length | Maximum length of generated sequence | 128 |
| max_new_tokens | Maximum number of tokens to generate | 512 |
| do_sample | Whether to use sampling | False (greedy) or True (sampling) |
| temperature | Sampling temperature (higher = more random) | 0.7 |
| top_p | Nucleus sampling probability | 0.95 |
| top_k | Top-k sampling | 50 |

 Sources: [README.md140-141](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L140-L141)

 
## Code Insertion (FIM)

 Code Insertion, also known as Fill-in-the-Middle (FIM), allows the model to fill in gaps in existing code.

 
### FIM Special Tokens

 The FIM task uses special tokens to mark different parts of the input:

 
 - `<｜fim▁begin｜>`: Marks the beginning of the context
 - `<｜fim▁hole｜>`: Marks the gap that needs to be filled
 - `<｜fim▁end｜>`: Marks the end of the context
 
 
### Usage Example

 
```

```

 Sources: [README.md102-122](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L102-L122)

 
## Chat Model Inference

 Chat Model Inference uses the instruction-tuned models for interactive, dialog-based code generation.

 
```

```

 Sources: [README.md129-176](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L129-L176)

 
### Usage Example

 
```

```

 Sources: [README.md129-142](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L129-L142)

 
### Chat Template

 If not using the `apply_chat_template` method, you can manually format the chat input using this template:

 
```
You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
['content']
### Response:
['content']
<|EOT|>
### Instruction:
['content']
### Response:
```

 Sources: [README.md164-176](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L164-L176)

 
## Repository-Level Completion

 Repository-Level Completion allows the model to understand and complete code across multiple files, demonstrating cross-file contextual understanding.

 
### Usage Example

 This example shows how the model can understand code dependencies across utility, model, and main files to complete appropriate implementation:

 
```

```

 Sources: [README.md178-266](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L178-L266)

 
## High-throughput Inference with vLLM

 For production scenarios requiring efficient inference, DeepSeek Coder supports integration with vLLM for high-throughput processing.

 
```

```

 Sources: [README.md333-382](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L333-L382)

 
### Text Completion with vLLM

 
```

```

 Sources: [README.md339-356](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L339-L356)

 
### Chat Completion with vLLM

 
```

```

 Sources: [README.md358-382](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L358-L382)

 
## Special Configurations

 
### Using Instruct Models for Code Completion

 Although the instruction-tuned models are primarily designed for chat interactions, they can be used for code completion by modifying the `eos_token_id` parameter:

 
```

```

 This adjustment enables the instruction-tuned models to perform code completion by changing how they recognize the end of a sequence.

 Sources: [README.md415-418](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L415-L418)

 
## Model Variants and Recommended Inference Methods

 
| Model | Size | Recommended Inference Methods |
|---|---|---|
| deepseek-coder-1b-base | 1B | Code Completion, Code Insertion |
| deepseek-coder-5.7b-base | 5.7B | Code Completion, Code Insertion, Repository-Level |
| deepseek-coder-6.7b-base | 6.7B | Code Completion, Code Insertion, Repository-Level |
| deepseek-coder-33b-base | 33B | Code Completion, Code Insertion, Repository-Level |
| deepseek-coder-6.7b-instruct | 6.7B | Chat Model Inference, Code Completion* |
| deepseek-coder-33b-instruct | 33B | Chat Model Inference, Code Completion* |

 *Requires modified `eos_token_id` as noted above.

 Sources: [README.md19-26](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L19-L26) [README.md415-418](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L415-L418)
