> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-MoE/4-fine-tuning](https://deepwiki.com/deepseek-ai/DeepSeek-MoE/4-fine-tuning)
> DeepWiki deepseek-ai/DeepSeek-MoE

# Fine-tuning

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1)
 - [finetune/finetune.py](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py)
 
  This document provides comprehensive guidance on fine-tuning the DeepSeek-MoE 16B model for downstream tasks. It covers the available fine-tuning methods, required configurations, and practical implementation steps. For general information about the model architecture, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-MoE/2-model-architecture).

 
## 1. Fine-tuning Overview

 DeepSeek-MoE supports three main fine-tuning approaches, each with different resource requirements and performance characteristics:

 
 - **Full Fine-tuning**: Updates all model parameters, requiring significant computational resources
 - **LoRA Fine-tuning**: Low-Rank Adaptation that efficiently updates a small subset of parameters
 - **QLoRA Fine-tuning**: Quantized LoRA that further reduces memory requirements through model quantization
 
 
```

```

 Sources: [README.md180-198](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L180-L198) [finetune/finetune.py250-320](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L250-L320)

 
## 2. Prerequisites

 Before beginning the fine-tuning process, ensure you have:

 
 - Installed all required dependencies:

 
```

```
 - Prepared your dataset in the correct format (see Data Preparation section)
 - Sufficient GPU resources based on your chosen fine-tuning method
 - DeepSpeed configured properly
 
 Sources: [README.md186-188](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L186-L188)

 
## 3. Fine-tuning Methods Comparison

 Each fine-tuning method offers different trade-offs between computational requirements and model performance:

 
| Method | Description | Parameters Updated | Memory Requirement | Hardware Recommendation |
|---|---|---|---|---|
| Full Fine-tuning | Updates all model parameters | All 16.4B parameters | Very High | 8× A100 40GB GPUs |
| LoRA | Low-rank adaptations to specific layers | Only LoRA parameters | Medium | Multiple GPUs |
| QLoRA | Quantized LoRA with 4/8-bit precision | Only LoRA parameters | Low | Single A100 80GB GPU |

 Sources: [README.md199-264](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L199-L264) [finetune/finetune.py31-52](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L31-L52)

 
## 4. Data Preparation

 DeepSeek-MoE expects data in a specific format for fine-tuning:

 
### Data Format

 The fine-tuning script expects data in the Parquet format with the following fields:

 
 - `instruction`: The input prompt or instruction
 - `output`: The desired completion or response
 
 
### Example Dataset Item

 
```
{
  "instruction": "Explain the concept of mixture of experts.",
  "output": "Mixture of Experts (MoE) is a neural network architecture..."
}
```

 The script will automatically format this into the appropriate prompting structure:

 
```
You are an AI assistant, developed by DeepSeek Company. For politically sensitive questions, security and privacy issues, you will refuse to answer.
### Instruction:
Explain the concept of mixture of experts.
### Response:
Mixture of Experts (MoE) is a neural network architecture...
```

 Sources: [README.md190-192](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L190-L192) [finetune/finetune.py115-180](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L115-L180) [finetune/finetune.py23-29](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L23-L29)

 
## 5. Fine-tuning System Architecture

 The DeepSeek-MoE fine-tuning system consists of several interconnected components:

 
```

```

 Sources: [finetune/finetune.py250-320](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L250-L320)

 
## 6. Implementation Details

 
### 6.1. Model Initialization

 The model is initialized based on the specified fine-tuning method:

 
```

```

 The function `build_model()` handles loading the pre-trained model and configuring it for fine-tuning based on the specified arguments.

 Sources: [finetune/finetune.py182-248](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L182-L248)

 
### 6.2. Data Processing Pipeline

 
```

```

 The data processing pipeline transforms raw data into tokenized inputs suitable for model training.

 Sources: [finetune/finetune.py115-180](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L115-L180) [finetune/finetune.py280-311](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L280-L311)

 
## 7. Configuration Options

 
### 7.1. Model Arguments

 Key model configuration parameters include:

 
| Parameter | Description | Default |
|---|---|---|
| trainable | Comma-separated list of modules to train | "q_proj,v_proj,k_proj,o_proj,gate_proj,down_proj,up_proj" |
| lora_rank | Rank for LoRA matrices | 8 |
| lora_dropout | Dropout rate for LoRA layers | 0.1 |
| lora_alpha | Scaling factor for LoRA | 32.0 |
| use_lora | Whether to use LoRA | False |
| bits | Quantization bits (4, 8, or 16) | 16 |
| quant_type | Quantization type for QLoRA | "nf4" |

 Sources: [finetune/finetune.py31-52](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L31-L52)

 
### 7.2. Training Arguments

 DeepSeek-MoE uses HuggingFace's `TrainingArguments` with additional parameters:

 
| Parameter | Description |
|---|---|
| model_max_length | Maximum sequence length for training |
| bf16 | Whether to use bfloat16 precision |
| per_device_train_batch_size | Batch size per GPU |
| gradient_accumulation_steps | Steps before parameter update |
| learning_rate | Learning rate for optimization |
| warmup_steps | Steps for learning rate warmup |
| deepspeed | Path to DeepSpeed configuration |

 Sources: [finetune/finetune.py59-67](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L59-L67) [README.md199-264](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L199-L264)

 
## 8. DeepSpeed Integration

 DeepSeek-MoE fine-tuning leverages DeepSpeed to optimize training performance:

 
```

```

 The DeepSpeed configuration varies based on the fine-tuning method:

 
 - Full fine-tuning uses ZeRO-3 for maximum memory efficiency
 - LoRA/QLoRA uses ZeRO-2 which provides a good balance of performance and memory usage
 
 Sources: [README.md199-226](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L199-L226) [README.md229-264](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L229-L264)

 
## 9. Fine-tuning Examples

 
### 9.1. Full Fine-tuning

 For full model fine-tuning, the recommended configuration uses DeepSpeed ZeRO-3 on multiple GPUs:

 
```

```

 This configuration requires 8 A100 40GB GPUs or equivalent hardware.

 Sources: [README.md199-226](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L199-L226)

 
### 9.2. QLoRA Fine-tuning

 For resource-efficient fine-tuning, QLoRA provides a good balance of performance and hardware requirements:

 
```

```

 This configuration can run on a single A100 80GB GPU.

 Sources: [README.md229-264](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L229-L264)

 
## 10. Checkpoint Management

 The fine-tuning system automatically handles checkpoint saving and resuming:

 
```

```

 
 - For LoRA/QLoRA fine-tuning, only the adapter weights are saved
 - For full fine-tuning, the entire model is saved
 - Training automatically resumes from the latest checkpoint if interrupted
 
 Sources: [finetune/finetune.py69-91](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L69-L91) [finetune/finetune.py92-104](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L92-L104)

 
## 11. Best Practices

 For optimal fine-tuning results with DeepSeek-MoE:

 
 - **Method Selection**:

 
 - Use full fine-tuning when maximum performance is required and sufficient hardware is available
 - Use LoRA for efficient fine-tuning with moderate hardware
 - Use QLoRA for resource-constrained scenarios where a single GPU is available
 - **Hyperparameter Recommendations**:

 
 - Learning rate: 1e-5 to 3e-5
 - Batch size: As large as memory allows
 - LoRA rank: 8-64 (higher for more capacity)
 - Gradient accumulation: 4-8 steps for effective larger batch sizes
 - **Data Preparation**:

 
 - Format data with clear instruction/output pairs
 - Include diverse examples for better generalization
 - Balance the dataset to prevent bias
 
 Sources: [README.md199-264](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L199-L264) [finetune/finetune.py250-320](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/finetune/finetune.py#L250-L320)

 
## 12. Conclusion

 The DeepSeek-MoE fine-tuning system offers flexible options for adapting the 16B parameter model to specific tasks. By choosing the appropriate fine-tuning method based on available resources and performance requirements, users can effectively customize the model while maintaining the benefits of its Mixture-of-Experts architecture.

 For advanced model usage after fine-tuning, see [Model Usage](https://deepwiki.com/deepseek-ai/DeepSeek-MoE/3-model-usage).

 Sources: [README.md180-198](https://github.com/deepseek-ai/DeepSeek-MoE/blob/66edeee5/README.md?plain=1#L180-L198)
