> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/2-model-architecture](https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/2-model-architecture)
> DeepWiki deepseek-ai/DeepSeek-Coder-V2

# Model Architecture

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1)
 - [paper.pdf](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/paper.pdf)
 
  This document provides a technical overview of the DeepSeek-Coder-V2 model architecture. It covers the Mixture-of-Experts (MoE) design, model variants, and key architectural features that enable the model's performance in code-related tasks.

 For specific information about different model sizes and implementations, see [Model Variants](https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/2.1-model-variants). For details about the extended context window implementation, see [Context Length Capabilities](https://deepwiki.com/deepseek-ai/DeepSeek-Coder-V2/2.2-context-length-capabilities).

 
## Core Architecture

 DeepSeek-Coder-V2 is built on the DeepSeekMoE framework, implementing a sparse Mixture-of-Experts architecture. This design allows the model to maintain a large number of total parameters while only activating a fraction of those parameters during inference.

 
### Mixture-of-Experts Architecture

 
```

```

 In this architecture:

 
 - Input tokens are embedded into continuous vector representations
 - These embeddings pass through multiple transformer layers
 - Within each transformer layer, after self-attention, a router network selectively activates only specific experts in the MoE feed-forward blocks
 - The outputs from activated experts are combined and processed through a language modeling head to produce the final output
 
 Sources: [README.md57-59](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L57-L59) [README.md70](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L70-L70)

 
### Parameter Efficiency

 The key innovation of the MoE architecture is parameter efficiency. For example:

 
 - The 16B parameter model activates only 2.4B parameters for each token
 - The 236B parameter model activates only 21B parameters for each token
 
 This sparse activation pattern enables DeepSeek-Coder-V2 to achieve better computational and memory efficiency than comparable dense models, making it possible to train and deploy larger models effectively.

 
## Model Variants

 DeepSeek-Coder-V2 encompasses four primary model variants:

 
```

```

 
### Model Specifications

 
| Model | Total Parameters | Active Parameters | Context Length | Type |
|---|---|---|---|---|
| DeepSeek-Coder-V2-Lite-Base | 16B | 2.4B | 128K | Base |
| DeepSeek-Coder-V2-Lite-Instruct | 16B | 2.4B | 128K | Instruct |
| DeepSeek-Coder-V2-Base | 236B | 21B | 128K | Base |
| DeepSeek-Coder-V2-Instruct | 236B | 21B | 128K | Instruct |

 Sources: [README.md69-80](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L69-L80)

 
### Base vs. Instruct Models

 The model family includes two types of variants:

 
 - **Base Models**: Foundation models trained primarily for code completion and generation tasks
 - **Instruct Models**: Fine-tuned versions of the base models optimized for following instructions and engaging in dialogue interactions
 
 The Instruct models are better suited for chat-based interactions and following complex instructions, while the Base models may perform better for pure code completion tasks.

 
## Development Process

 DeepSeek-Coder-V2 was developed through a systematic multi-stage process:

 
```

```

 The development process included:

 
 - Starting from an intermediate checkpoint of the DeepSeek-V2 model
 - Additional pre-training with 6 trillion tokens of code-focused data
 - Creating base models optimized for code-related tasks
 - Fine-tuning with instruction data to create the instruct variants
 
 This process enhanced the model's coding and mathematical reasoning capabilities while maintaining its general language understanding.

 Sources: [README.md58-59](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L58-L59)

 
## Technical Implementation

 
### Programming Language Coverage

 The model architecture is designed to support a wide range of programming languages - 338 in total, a significant expansion from the 86 languages supported in previous DeepSeek models. This comprehensive language coverage required architectural considerations to handle the diverse syntax and patterns across different programming languages.

 
### Memory and Computation Design

 The MoE architecture is specifically designed to optimize memory usage and computational efficiency:

 
```

```

 This selective activation approach allows the model to maintain strong performance while reducing the computational requirements for both training and inference.

 
### Inference Optimizations

 The architecture supports several inference optimization techniques:

 
 - **Tensor Parallelism**: Distributing the model across multiple GPUs
 - **FP8 Support**: Reduced precision for more efficient computation
 - **FP8 KV Cache**: Memory-efficient key-value caching
 - **MLA Optimizations**: Multi-layer attention optimizations
 
 Sources: [README.md280-291](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L280-L291)

 
## Hardware Requirements

 The hardware requirements for DeepSeek-Coder-V2 reflect its architecture:

 
 - **DeepSeek-Coder-V2-Lite models**: Can run on consumer hardware with appropriate optimizations
 - **DeepSeek-Coder-V2 (full 236B models)**: Require 80GB*8 GPUs for inference when using BF16 format
 
 These requirements stem directly from the model's architectural design and parameter count.

 Sources: [README.md188-190](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L188-L190)

 
## Model Input and Output Processing

 
```

```

 The model architecture includes specialized tokenization designed to handle code-specific constructs effectively, including:

 
 - Special tokens for code-specific elements
 - Support for FIM (Fill-In-Middle) operations with dedicated tokens (`<｜fim▁begin｜>`, `<｜fim▁hole｜>`, `<｜fim▁end｜>`)
 - Chat template format with role-based tokens for dialogue interactions
 
 Sources: [README.md205-227](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L205-L227) [README.md229-274](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/c59bc464/README.md?plain=1#L229-L274)
