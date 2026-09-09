> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-MoE/3-model-usage](https://deepwiki.com/deepseek-ai/DeepSeek-MoE/3-model-usage)
> DeepWiki deepseek-ai/DeepSeek-MoE

# Model Usage

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1)
 
  This document provides detailed guidance on how to use the DeepSeekMoE 16B models for inference tasks. It covers basic usage patterns for both the base and chat models, focusing on text completion and chat interactions. For information about fine-tuning these models, please refer to the [Fine-tuning](https://deepwiki.com/deepseek-ai/DeepSeek-MoE/4-fine-tuning) page.

 
## Setup and Installation

 Before using the DeepSeekMoE models, you need to install the necessary dependencies in a Python environment (version 3.8 or higher).

 
```

```

 The models can be loaded using Hugging Face's Transformers library. Both models are available for direct use from the Hugging Face Hub.

 Sources: [README.md114-120](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L114-L120)

 
## DeepSeekMoE Models Overview

 The DeepSeekMoE repository provides two main model variants:

 
 - **DeepSeekMoE 16B Base**: Optimized for general text completion tasks
 - **DeepSeekMoE 16B Chat**: Fine-tuned specifically for conversational interactions
 
 Both models feature a Mixture-of-Experts (MoE) architecture with 16.4B total parameters, though only about 40% of these parameters are activated during inference. This design allows the models to run on a single GPU with 40GB memory without quantization.

 
```

```

 Sources: [README.md61-67](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L61-L67) [README.md108-111](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L108-L111)

 
## Text Completion with Base Model

 The DeepSeekMoE 16B Base model is designed for general text completion tasks. Here's the typical workflow for using this model:

 
```

```

 
### Example Usage

 The following code demonstrates how to use the DeepSeekMoE 16B Base model for text completion:

 
```

```

 Sources: [README.md126-144](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L126-L144)

 
## Chat Completion with Chat Model

 The DeepSeekMoE 16B Chat model is specifically fine-tuned for conversational interactions. The usage flow is similar to the base model but includes formatting messages using a chat template.

 
```

```

 
### Example Usage

 The following code demonstrates how to use the DeepSeekMoE 16B Chat model for conversations:

 
```

```

 Sources: [README.md148-166](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L148-L166)

 
### Chat Template Format

 If you prefer to manually format your chat messages instead of using `apply_chat_template()`, you can follow this template:

 
```
User: {messages[0]['content']}
```
