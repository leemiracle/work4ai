# deepwiki torchrl §9 llm-integration
> 来源: https://deepwiki.com/pytorch/rl/9-llm-integration

$/$
$?

/$

DeepWiki

DeepWiki
pytorch/rl

$?

/$

Last indexed:  14 December 2025  (eaaa11)

  - Overview
  - Core Data Infrastructure
  - TensorDict System
  - TensorSpec System
  - Environments
  - EnvBase and Environment Specifications
  - Environment Transforms
  - Backend Integrations
  - Batched and Parallel Environments
  - Data Collection
  - Collector Architecture
  - Distributed Collection Strategies
  - Replay Buffers
  - ReplayBuffer Architecture
  - Advanced Replay Buffer Features
  - Modules and Models
  - TensorDictModule System
  - Actors, Critics, and Value Networks
  - Probability Distributions
  - Neural Network Architectures
  - Exploration Strategies
  - Learning Algorithms
  - Loss Module Architecture
  - On-Policy Algorithms
  - Off-Policy Algorithms
  - Value-Based Algorithms
  - Value Estimators
  - Training Infrastructure
  - Trainer System
  - Helper Utilities
  - LLM Integration
  - LLM Wrapper System
  - LLM Data Structures
  - LLM Training Objectives
  - LLM Environments and Tools
  - Multi-Agent Reinforcement Learning
  - Examples and Tutorials
  - Development and Deployment
  - Build System
  - Documentation System

Menu

## LLM Integration

Relevant source files

  - docs/source/reference/llms.rst

  - test/llm/test_objectives.py

  - test/llm/test_wrapper.py

  - torchrl/data/llm/history.py

  - torchrl/envs/llm/transforms/kl.py

  - torchrl/modules/llm/policies/__init__.py

  - torchrl/modules/llm/policies/common.py

  - torchrl/modules/llm/policies/transformers_wrapper.py

  - torchrl/modules/llm/policies/vllm_wrapper.py

  - torchrl/objectives/llm/__init__.py

  - torchrl/objectives/llm/grpo.py

  - torchrl/objectives/llm/sft.py

### Purpose and Scope

This document provides a comprehensive overview of TorchRL's Large Language Model (LLM) integration system. TorchRL offers a complete framework for LLM reinforcement learning post-training, including fine-tuning with algorithms like GRPO (Group Relative Policy Optimization), SFT (Supervised Fine-Tuning), and CISPO (Conservative Iterative Sequential Policy Optimization).

The LLM integration system consists of four main subsystems:

  - LLM Wrappers ( 9.1 ): Unified interfaces for Hugging Face Transformers and vLLM backends

  - Data Structures ( 9.2 ): TensorClass objects for managing conversational data ( History , ChatHistory , Text , Tokens , Masks , LogProbs )

  - Training Objectives ( 9.3 ): Loss modules for LLM fine-tuning ( GRPOLoss , SFTLoss , CISPOLoss )

  - Environments and Tools ( 9.4 ): ChatEnv and transforms for RL-based LLM training

For information about distributed data collection, see Data Collection. For information about replay buffers, see Replay Buffers. For general environment concepts, see Environments.

Sources: docs/source/reference/llms.rst1-470 torchrl/modules/llm/policies/__init__.py1-24 torchrl/objectives/llm/__init__.py1-31

### System Architecture

The LLM integration system follows a modular, composable design where data flows through wrappers, environments, collectors, and loss modules. All components communicate using `TensorDict` as the universal data container and specialized `TensorClass` objects for structured LLM data.

#### High-Level Component Diagram

```

```

Sources: torchrl/modules/llm/policies/common.py1-800 torchrl/modules/llm/policies/transformers_wrapper.py1-300 torchrl/modules/llm/policies/vllm_wrapper.py1-300 docs/source/reference/llms.rst1-470

### Core Component Overview

#### LLM Wrappers

The wrapper system provides a unified interface for LLM inference across different backends. The base class `LLMWrapperBase` defines the common API, while backend-specific implementations (`TransformersWrapper`, `vLLMWrapper`) handle model-specific details.

Key Classes:

  - LLMWrapperBase : Abstract base class defining the wrapper interface

  - TransformersWrapper : Wrapper for Hugging Face Transformers models

  - vLLMWrapper : Wrapper for vLLM models (sync and async)

  - RemoteTransformersWrapper : Distributed wrapper using Ray

Input Modes: All wrappers support three input modes:

  - "history" : Uses History / ChatHistory objects for multi-turn conversations

  - "text" : Uses raw text strings

  - "tokens" : Uses pre-tokenized token IDs

Generation Modes:

  - generate=True : Generate new text (returns response )

  - generate=False : Compute log-probabilities only (returns full )

For detailed information, see LLM Wrapper System.

Sources: torchrl/modules/llm/policies/common.py800-1000 torchrl/modules/llm/policies/transformers_wrapper.py40-243 torchrl/modules/llm/policies/vllm_wrapper.py56-264

#### Data Structures

TorchRL provides specialized `TensorClass` objects for managing LLM data. These structures maintain consistency across the pipeline and support both padded and unpadded (nested tensor) representations.

| Class | Purpose | Key Fields |
| History | Raw conversation data | role , content , complete |
| ChatHistory | Structured conversation container | prompt , response , full |
| Text | Text representation | prompt , response , full |
| Tokens | Tokenized representation | prompt , response , full , padded |
| Masks | Attention and assistant masks | all_attention_mask , all_assistant_mask , padded |
| LogProbs | Log-probability values | prompt , response , full , padded |

All data structures follow a consistent pattern with `prompt`, `response`, and `full` fields, where `full = prompt + response`. They also support conversion methods like `to_tokens()`, `to_text()`, and `to_history()`.

For detailed information, see LLM Data Structures.

Sources: torchrl/modules/llm/policies/common.py39-682 torchrl/data/llm/history.py1-300

#### Training Objectives

TorchRL provides LLM-specific loss modules that implement state-of-the-art fine-tuning algorithms. These losses integrate with the wrapper system to compute gradients for policy optimization.

Available Losses:

  - GRPOLoss : Group Relative Policy Optimization with clipped importance sampling

  - SFTLoss : Supervised Fine-Tuning loss with optional KL regularization

  - CISPOLoss : Conservative Iterative Sequential Policy Optimization

  - DAPOLoss : Direct Alignment from Preferences Optimization

Advantage Estimation:

  - MCAdvantage : Monte Carlo advantage estimation for LLM trajectories

Key Features:

  - Token-level masking strategies ( "sft" , "rlhf" , "generic" )

  - KL divergence regularization to reference models

  - Asymmetric clipping thresholds (DAPO-style)

  - Token-wise trust region filtering (KL-Mask)

For detailed information, see LLM Training Objectives.

Sources: torchrl/objectives/llm/grpo.py1-400 torchrl/objectives/llm/sft.py1-234 docs/source/reference/llms.rst429-461

#### Environments and Tools

The environment layer orchestrates data loading, tool execution, and reward computation. `ChatEnv` serves as the base environment, extended by transforms for specific functionality.

Core Environment:

  - ChatEnv : Base conversational environment supporting history/text/token modes

Key Transforms:

  - RetrieveLogProb : Retrieve reference model log-probabilities

  - KLComputation : Compute KL divergence rewards

  - PythonInterpreter : Execute Python code in conversations

  - MCPToolTransform : General tool calling support

  - DataLoadingPrimer : Load prompts from datasets

  - AddThinkingPrompt : Add chain-of-thought reasoning prompts

For detailed information, see LLM Environments and Tools.

Sources: docs/source/reference/llms.rst112-427 torchrl/envs/llm/transforms/kl.py1-300

### Data Flow Pipeline

The following diagram illustrates how data flows through the LLM training pipeline, from raw conversation data through wrappers, environments, collectors, and finally to loss computation.

#### End-to-End Training Pipeline

```

```

Sources: docs/source/reference/llms.rst1-100 torchrl/modules/llm/policies/transformers_wrapper.py638-750 torchrl/objectives/llm/grpo.py320-400

### Input and Output Modes

The wrapper system supports three input modes that determine how data is structured throughout the pipeline. The mode is set during wrapper initialization and affects both input and output keys.

#### Input Mode Configuration

```

```

#### Mode Comparison Table

| Input Mode | Input Type | Generated Output | Use Case |
| "history" | History or ChatHistory | history , text , tokens , masks , log_probs | Multi-turn conversations, RL environments |
| "text" | str or Text | text , tokens , masks , log_probs | Simple text generation, SFT |
| "tokens" | torch.Tensor or Tokens | tokens , masks , log_probs | Pre-tokenized data, custom preprocessing |

Key Differences:

  - History mode preserves conversation structure and supports multi-turn interactions

  - Text mode is simpler but loses conversation structure

  - Tokens mode provides maximum control but requires manual tokenization

Sources: torchrl/modules/llm/policies/transformers_wrapper.py173-200 torchrl/modules/llm/policies/vllm_wrapper.py195-223 torchrl/modules/llm/policies/common.py220-284

### Getting Started Example

The following example demonstrates a complete LLM fine-tuning workflow using GRPO with the recommended components.

#### Basic GRPO Training Setup

```

```

Key Components Explained:

  - AsyncVLLM engines : Use AsyncVLLM for better GPU utilization and throughput

  - Input mode : "history" mode preserves conversation structure for multi-turn

  - Generate modes : Training policy generates text ( generate=True ), reference computes log-probs only ( generate=False )

  - Transforms : RetrieveLogProb gets reference log-probs, KLComputation adds KL rewards

  - MCAdvantage : Computes advantages from rewards using Monte Carlo estimation

  - Masking strategy : "rlhf" masks assistant tokens only for multi-turn conversations

Sources: docs/source/reference/llms.rst20-38 test/llm/test_objectives.py96-180 torchrl/objectives/llm/grpo.py70-150

### Advanced Features

#### Batching for Multi-Threaded Environments

Both `TransformersWrapper` and `vLLMWrapper` support automatic batching for multi-threaded data collection, which improves throughput when using parallel environments.

Configuration:

```

```

Behavior:

  - Threads add requests to a queue

  - When queue reaches min_batch_size , batch is processed

  - Maximum batch size is capped at max_batch_size

  - If timeout expires, partial batch is processed

Sources: torchrl/modules/llm/policies/transformers_wrapper.py152-172 torchrl/modules/llm/policies/vllm_wrapper.py174-194

#### Parameter Standardization

Wrappers accept both backend-specific and standardized parameter names for generation configuration, providing cross-backend compatibility.

Standardized Parameters:

| Standard Name | Transformers | vLLM | Description |
| max_new_tokens | max_new_tokens | max_tokens | Maximum tokens to generate |
| num_return_sequences | num_return_sequences | n | Number of sequences |
| temperature | temperature | temperature | Sampling temperature |
| top_p | top_p | top_p | Nucleus sampling |
| top_k | top_k | top_k | Top-k sampling |
| repetition_penalty | repetition_penalty | repetition_penalty | Repetition penalty |
| do_sample | do_sample | N/A | Enable sampling |

Legacy Support:

  - vLLM: max_tokens and n are automatically converted

  - Transformers: max_tokens is converted to max_new_tokens

Sources: torchrl/modules/llm/policies/transformers_wrapper.py80-126 torchrl/modules/llm/policies/vllm_wrapper.py107-154

#### Distributed Inference with Ray

`RemoteTransformersWrapper` enables distributed LLM inference using Ray, useful for large models that don't fit on a single GPU.

```

```

Sources: torchrl/modules/llm/policies/transformers_wrapper.py1-50

#### Asymmetric Clipping (DAPO)

`GRPOLoss` supports asymmetric clipping thresholds for more stable training, as proposed in the DAPO paper.

```

```

This allows the policy to increase probability more than decrease it, which can improve training stability.

Sources: torchrl/objectives/llm/grpo.py195-253 docs/source/reference/llms.rst148-149

#### Token-Wise Trust Region (KL-Mask)

Enable per-token KL divergence filtering to stabilize training by masking tokens that drift too far from the reference model.

```

```

Tokens where `0.5 * (log(pi_theta/pi_ref))^2 > kl_mask_threshold` are excluded from loss computation.

Sources: torchrl/objectives/llm/grpo.py99-107 test/llm/test_objectives.py249-316

#### MinorSFT Loss

`SFTLoss` supports the MinorSFT variant, which provides implicit KL regularization without requiring explicit reference log-probabilities.

```

```

MinorSFT computes `-log_sigmoid(beta * (log_probs - ref_log_probs))`, making fine-tuning less aggressive than standard SFT.

Sources: torchrl/objectives/llm/sft.py38-74 torchrl/objectives/llm/sft.py104-233

### File Reference Index

#### Core Wrapper Files

  - torchrl/modules/llm/policies/common.py 1-800 - Base classes and data structures

  - torchrl/modules/llm/policies/transformers_wrapper.py 1-2000 - Hugging Face wrapper

  - torchrl/modules/llm/policies/vllm_wrapper.py 1-2000 - vLLM wrapper

#### Loss Module Files

  - torchrl/objectives/llm/grpo.py 1-700 - GRPO, CISPO, DAPO losses

  - torchrl/objectives/llm/sft.py 1-500 - SFT loss

#### Environment Files

  - torchrl/envs/llm/transforms/kl.py 1-600 - KL transforms

#### Test Files

  - test/llm/test_wrapper.py 1-2000 - Wrapper tests

  - test/llm/test_objectives.py 1-500 - Loss module tests

#### Documentation Files

  - docs/source/reference/llms.rst 1-470 - API reference documentation



#### On this page

  - LLM Integration
  - Purpose and Scope
  - System Architecture
  - High-Level Component Diagram
  - Core Component Overview
  - LLM Wrappers
  - Data Structures
  - Training Objectives
  - Environments and Tools
  - Data Flow Pipeline
  - End-to-End Training Pipeline
  - Input and Output Modes
  - Input Mode Configuration
  - Mode Comparison Table
  - Getting Started Example
  - Basic GRPO Training Setup
  - Advanced Features
  - Batching for Multi-Threaded Environments
  - Parameter Standardization
  - Distributed Inference with Ray
  - Asymmetric Clipping (DAPO)
  - Token-Wise Trust Region (KL-Mask)
  - MinorSFT Loss
  - File Reference Index
  - Core Wrapper Files
  - Loss Module Files
  - Environment Files
  - Test Files
  - Documentation Files

$!/$$/$
