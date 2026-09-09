> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/5-getting-started](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/5-getting-started)
> DeepWiki deepseek-ai/DeepSeek-Math-V2

# Getting Started

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1)
 
  This page provides a practical guide for accessing and using DeepSeekMath-V2. It covers model download from Hugging Face, local inference setup using the DeepSeek-V3.2-Exp repository, and basic usage patterns for mathematical problem-solving. For technical details about the model architecture, see [Model Architecture Details](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/6.2-model-architecture-details). For information about output formats and result interpretation, see [Data Formats & Outputs](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/4-data-formats-and-outputs).

 **Scope**: This guide assumes basic familiarity with Python, PyTorch, and command-line tools. It focuses on getting the model running for inference, not training or fine-tuning.

 
---

 
## Access Methods Overview

 DeepSeekMath-V2 can be accessed through three primary methods, each suited to different use cases.

 
```

```

 **Access Methods Comparison**

 
| Method | Use Case | Requirements | Latency | Customization |
|---|---|---|---|---|
| Online Chat (chat.deepseek.com) | Quick testing, demos | Browser only | Low | None |
| Direct Download (deepseek-ai/DeepSeek-Math-V2) | Research, archival | ~100GB storage | N/A | Full |
| Local Inference (DeepSeek-V3.2-Exp) | Production, batch processing | GPU, Python 3.8+ | Medium | Full |

 **Sources**: [README.md69-70](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L69-L70) [README.md10-22](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L10-L22)

 
---

 
## Prerequisites

 Before setting up local inference, ensure your system meets these requirements:

 **Hardware Requirements**

 
 - **GPU Memory**: Minimum 80GB VRAM (single A100/H100) or distributed setup
 - **System RAM**: 128GB+ recommended
 - **Storage**: 150GB+ free space for model weights and dependencies
 
 **Software Requirements**

 
 - Python 3.8 or higher
 - PyTorch 2.0+ with CUDA support
 - Git and Git LFS for repository cloning
 
 **Python Dependencies** (installed via `DeepSeek-V3.2-Exp` repository)

 
 - `transformers` (Hugging Face)
 - `torch` (PyTorch)
 - `accelerate` (for multi-GPU inference)
 - Additional dependencies specified in the inference repository
 
 **Sources**: [README.md69-70](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L69-L70)

 
---

 
## Model Download from Hugging Face

 The DeepSeekMath-V2 model weights are hosted on Hugging Face and must be downloaded before local inference.

 
### Hugging Face Model Repository

 The model is located at: `https://huggingface.co/deepseek-ai/DeepSeek-Math-V2`

 
### Download Methods

 **Method 1: Using Hugging Face CLI** (Recommended)

 
```

```

 **Method 2: Using Git LFS**

 
```

```

 **Method 3: Programmatic Download**

 
```

```

 
### Model Files Structure

 After download, the model directory contains:

 
```
DeepSeek-Math-V2/
├── config.json              # Model configuration
├── model-*.safetensors      # Model weight shards
├── tokenizer_config.json    # Tokenizer configuration
├── tokenizer.json           # Tokenizer vocabulary
├── special_tokens_map.json  # Special token mappings
└── README.md                # Model card documentation
```

 **Sources**: [README.md69](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L69-L69)

 
---

 
## Inference Setup

 Local inference requires the `DeepSeek-V3.2-Exp` repository, which provides inference scripts optimized for the model architecture.

 
```

```

 
### Step 1: Clone Inference Repository

 
```

```

 
### Step 2: Install Dependencies

 
```

```

 
### Step 3: Configure Model Path

 Update the inference script to point to your downloaded model:

 
```

```

 
### Step 4: Initialize Model

 Basic inference initialization pattern:

 
```

```

 
### Single-GPU vs Multi-GPU Setup

 **Single GPU (80GB+ VRAM)**

 
```

```

 **Multi-GPU (Distributed)**

 
```

```

 **Sources**: [README.md70](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L70-L70)

 
---

 
## Basic Usage Patterns

 This section demonstrates typical usage patterns for mathematical problem-solving with DeepSeekMath-V2.

 
### Input Format

 Mathematical problems should be provided as plain text strings. The model accepts natural language problem descriptions:

 
```

```

 
### Generation Parameters

 Recommended parameters for mathematical reasoning:

 
| Parameter | Value | Purpose |
|---|---|---|
| max_new_tokens | 4096-8192 | Accommodate detailed proofs |
| temperature | 0.7-1.0 | Balance creativity and rigor |
| top_p | 0.95 | Nucleus sampling for quality |
| do_sample | True | Enable sampling for diverse solutions |
| num_return_sequences | 1-8 | Generate multiple solution attempts |

 
### Basic Inference Example

 
```

```

 
### Expected Output Structure

 The model generates structured proofs with:

 
 - **Problem Restatement**: Clarifies the question
 - **Notation**: Defines variables and symbols
 - **Solution Strategy**: Outlines the approach
 - **Step-by-Step Derivation**: Detailed logical progression
 - **Verification**: Self-checks key steps
 - **Final Answer**: Explicit conclusion
 
 Example output structure:

 
```
**Problem**: Find all positive integers n such that 2^n + 1 is divisible by 3.

**Solution**:

Let's analyze when 2^n + 1 ≡ 0 (mod 3).

Note that 2 ≡ -1 (mod 3), so:
2^n ≡ (-1)^n (mod 3)

Therefore:
2^n + 1 ≡ (-1)^n + 1 (mod 3)

Case 1: n is even
Then (-1)^n = 1, so 2^n + 1 ≡ 1 + 1 = 2 (mod 3) ≠ 0

Case 2: n is odd
Then (-1)^n = -1, so 2^n + 1 ≡ -1 + 1 = 0 (mod 3)

**Conclusion**: All odd positive integers n satisfy the condition.
```

 **Sources**: [README.md50](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L50-L50)

 
---

 
## Batch Processing

 For processing multiple problems (e.g., from benchmark datasets):

 
```

```

 This pattern matches the output format used in `outputs/` directory for benchmark results. For details on the JSONL schema and rating systems, see [JSONL Schema](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/4.1-jsonl-schema) and [Evaluation Metrics](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/4.3-evaluation-metrics).

 **Sources**: [README.md50](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L50-L50)

 
---

 
## Integration Flow

 
```

```

 **Sources**: [README.md69-70](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L69-L70)

 
---

 
## Memory Optimization

 For systems with limited GPU memory, use these strategies:

 
### Quantization

 
```

```

 
### Gradient Checkpointing

 
```

```

 
### Batch Size Adjustment

 
```

```

 **Sources**: [README.md69-70](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L69-L70)

 
---

 
## Verification and Quality Checks

 After generation, verify output quality:

 
### Automatic Checks

 
```

```

 
### Manual Verification Criteria

 For human evaluation (see [Evaluation Metrics](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/4.3-evaluation-metrics)):

 
 - **Correctness**: Each step follows logically
 - **Completeness**: All cases covered
 - **Rigor**: No unjustified leaps
 - **Clarity**: Easy to follow reasoning
 
 **Sources**: [README.md50](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L50-L50)

 
---

 
## Troubleshooting

 
### Common Issues and Solutions

 
| Issue | Possible Cause | Solution |
|---|---|---|
| Out of memory (OOM) | Model too large for GPU | Use quantization or multi-GPU setup |
| Generation hangs | Infinite loop in generation | Set max_new_tokens explicitly |
| Poor quality output | Temperature too high/low | Adjust to 0.7-1.0 range |
| Tokenization error | Wrong tokenizer version | Use tokenizer from same repo as model |
| Model not found | Incorrect path | Verify path to DeepSeek-Math-V2/ |

 
### Debugging Tips

 
```

```

 **Sources**: [README.md70](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L70-L70)

 
---

 
## Next Steps

 After successfully setting up inference:

 
 - **Explore Examples**: See [Example Usage](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/5.3-example-usage) for detailed problem-solving patterns
 - **Understand Output Format**: Review [Data Formats & Outputs](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/4-data-formats-and-outputs) to interpret results
 - **Evaluate Performance**: Learn about benchmarks in [Evaluation & Results](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/3-evaluation-and-results)
 - **Deep Dive**: For architectural details, see [Technical Deep Dive](https://deepwiki.com/deepseek-ai/DeepSeek-Math-V2/6-technical-deep-dive)
 
 For community support and discussions:

 
 - **Discord**: Join at `https://discord.gg/Tc7c45Zzu5`
 - **WeChat**: Scan QR code in [README.md19](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L19-L19)
 - **Email**: Contact `service@deepseek.com` for technical issues
 
 **Sources**: [README.md10-28](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L10-L28) [README.md85-87](https://github.com/deepseek-ai/DeepSeek-Math-V2/blob/6147f908/README.md?plain=1#L85-L87)
