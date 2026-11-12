> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/4-usage-and-inference](https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/4-usage-and-inference)
> DeepWiki deepseek-ai/DeepSeek-Coder-V2

# Usage & Inference

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1)
 
  This document provides a comprehensive guide to using DeepSeek-Coder-V2 models for inference across various platforms and methods. It covers different integration options, usage patterns, and optimization techniques to help users effectively utilize these models for code-related tasks.

 For information about the model architecture itself, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/2-model-architecture). For details on supported programming languages, refer to [Supported Programming Languages](https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/3-supported-programming-languages).

 
## Model Variants Overview

 Before exploring usage methods, it's important to understand the available model variants:

 
| Model | Total Parameters | Active Parameters | Context Length | Purpose |
|---|---|---|---|---|
| DeepSeek-Coder-V2-Lite-Base | 16B | 2.4B | 128K | Code completion and generation (base model) |
| DeepSeek-Coder-V2-Lite-Instruct | 16B | 2.4B | 128K | Chat and instruction following |
| DeepSeek-Coder-V2-Base | 236B | 21B | 128K | Code completion and generation (base model) |
| DeepSeek-Coder-V2-Instruct | 236B | 21B | 128K | Chat and instruction following |

 The Lite variants require fewer computational resources while maintaining good performance. The full models (236B parameters) require 8 GPUs with 80GB memory each for BF16 inference.

 Sources: [README.md68-80](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L68-L80)

 
## Inference Pipeline

 The following diagram shows the general inference flow from user input to model response:

 
```

```

 Sources: [README.md189-205](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L189-L205)

 
## Inference Methods

 DeepSeek-Coder-V2 supports multiple inference methods, each with its own advantages. The following diagram illustrates these methods and their key components:

 
```

```

 Sources: [README.md188-338](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L188-L338)

 
### 1. Hugging Face Transformers

 The most straightforward way to use DeepSeek-Coder-V2 is through Hugging Face's Transformers library. This method supports several use cases:

 
#### Code Completion

 Code completion is when you provide a partial code snippet and the model completes it:

 
```

```

 Sources: [README.md194-204](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L194-L204)

 
#### Code Insertion (FIM)

 The Fill-in-the-Middle (FIM) feature allows you to have the model fill in a gap in the middle of a code snippet:

 
```

```

 The FIM format uses special tokens to indicate the beginning of the code (`<｜fim▁begin｜>`), the hole to be filled (`<｜fim▁hole｜>`), and the end of the code (`<｜fim▁end｜>`).

 Sources: [README.md207-227](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L207-L227)

 
#### Chat Completion

 For instruction-tuned models, you can use the chat completion functionality:

 
```

```

 Sources: [README.md232-243](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L232-L243)

 
#### Chat Template Format

 The chat template follows a specific structure:

 
```
<｜begin▁of▁sentence｜>User: {user_message_1}
```
