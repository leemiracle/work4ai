# speculators

> 来源: https://deepwiki.com/vllm-project/speculators 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [README.md](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1)
  * [docs/index.md](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1)
  * [pyproject.toml](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml)

## Purpose and Scope

This document provides a high-level introduction to the Speculators library, explaining its purpose, core components, and main workflows. Speculators is a unified framework for building, training, and deploying speculative decoding models for large language model (LLM) inference acceleration, specifically optimized for frameworks like vLLM.

For installation instructions, see [Installation and Setup](/vllm-project/speculators/1.3-installation-and-setup). For hands-on tutorials, see [Quick Start](/vllm-project/speculators/1.1-quick-start). For detailed system architecture, see [System Architecture](/vllm-project/speculators/1.2-system-architecture).

**Sources:** [README.md13-26](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L13-L26) [docs/index.md11-18](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1#L11-L18)

## What is Speculative Decoding?

Speculative decoding is a lossless inference optimization technique that reduces LLM latency without compromising output quality. The process works as follows:

  1. A smaller, faster **draft model** (the speculator) proposes multiple tokens ahead of time.
  2. The larger **base model** (the verifier) validates these proposed tokens in a single forward pass.
  3. Accepted tokens are guaranteed to match what the base model would have generated independently.
  4. The process repeats until the sequence completes.

This approach achieves speedups by amortizing the cost of the base model's forward pass across multiple token predictions. Since verification is lossless, the output distribution remains identical to standard autoregressive decoding.

**Sources:** [README.md15-16](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L15-L16) [docs/index.md13-15](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1#L13-L15)

## Library Architecture

Speculators provides a complete end-to-end pipeline for speculative decoding, from data generation through deployment. It supports both offline data generation (saving hidden states to disk) and online generation (streaming hidden states directly to the trainer).

Title: Speculators Pipeline Flow

**Key Components:**

Component| Code Entity| Purpose  
---|---|---  
Hidden States Generator| `VllmHiddenStatesGenerator`| Extracts intermediate representations from target model using vLLM  
Draft Model (Training)| `Eagle3DraftModel`| Training-time model with Target-Token-Training (TTT) steps  
Parallel Draft Model| `PEagleDraftModel`| Parallel multi-token prediction using COD sampling  
Draft Model (Deployment)| `EagleSpeculator`| Production model for inference in vLLM  
Training Controller| `Trainer`| FSDP-enabled distributed training loop  
State Management| `Checkpointer`| Handles checkpoint saving/loading for single-GPU and distributed scenarios  
Configuration| `SpeculatorModelConfig`| HuggingFace-compatible model configuration with embedded `speculator_config`  
  
**Sources:** [README.md38-48](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L38-L48) [pyproject.toml13-55](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L13-L55)

## Core Model Framework

The library implements a registry-based framework for defining speculator models with automatic type resolution:

Title: Speculator Model Class Hierarchy

**Architecture Details:**

  * **`SpeculatorModel`** : Abstract base class defining the interface for all speculator implementations. Inherits from `PreTrainedModel` and `GenerationMixin` for full HuggingFace compatibility.
  * **`Eagle3DraftModel`** : Training-time model with TTT (Target-Token-Training) forward pass logic. Uses hidden states from verifier to predict next tokens.
  * **`PEagleDraftModel`** : Extends Eagle3 with parallel group prediction using Conditional-On-Distribution (COD) sampling.
  * **`EagleSpeculator`** : Deployment-optimized variant loaded by vLLM. Contains single decoder layer plus fusion mechanism.
  * **`DFlashDraftModel`** : Implementation of anchor-based block prediction mechanisms using auxiliary hidden states from multiple verifier layers.
  * **`SpeculatorModelConfig`** : Configuration class using Pydantic for validation. Contains nested `speculator_config` with verifier reference and proposal methods.

**Sources:** [README.md42-48](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L42-L48) [pyproject.toml38-56](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L38-L56)

## Supported Models and Deployment

The library has been validated with several major verifier architectures, including Llama, Qwen, and Gemma.

Verifier Architecture| Size| Status| HuggingFace Model  
---|---|---|---  
Llama 3.1| 8B-Instruct| ✅| `RedHatAI/Llama-3.1-8B-Instruct-speculator.eagle3`  
Llama 3.3| 70B-Instruct| ✅| `RedHatAI/Llama-3.3-70B-Instruct-speculator.eagle3`  
Qwen3| 8B| ✅| `RedHatAI/Qwen3-8B-speculator.dflash`  
Qwen3| 14B| ✅| `RedHatAI/Qwen3-14B-speculator.eagle3`  
Qwen3| 32B| ✅| `RedHatAI/Qwen3-32B-speculator.eagle3`  
Qwen3 MoE| 30B-Instruct| ✅| `RedHatAI/Qwen3-30B-A3B-Instruct-2507-speculator.eagle3`  
Gemma 4| 31B-it| ✅| `RedHatAI/gemma-4-31B-it-speculator.dflash`  
gpt-oss| 20B| ✅| `RedHatAI/gpt-oss-20b-speculator.eagle3`  
Mistral 3 Large| 675B-Instruct| ⏳| In progress  
  
**Sources:** [README.md63-162](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L63-L162) [docs/index.md54-162](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1#L54-L162)

## Workflow Patterns

### End-to-End Training Workflow

For training a new speculator from scratch:

  1. **Data Generation** : Use `VllmHiddenStatesGenerator` (offline) or the `vllm_client` (online) to extract hidden states.
  2. **Vocabulary Mapping** : Run vocabulary mapping scripts to create draft-target mappings.
  3. **Training** : Execute training with `Eagle3DraftModel`, `PEagleDraftModel`, or `DFlashDraftModel` for FSDP-enabled distributed training.
  4. **Publishing** : Push trained checkpoint to HuggingFace Hub with `SpeculatorModelConfig`.

The `gen_and_train.py` script automates all stages with isolated environments.

**Sources:** [README.md47-53](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L47-L53) [docs/index.md29-32](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1#L29-L32)

### Model Conversion Workflow

For converting existing Eagle/Eagle3 models to Speculators format:

  1. **Detection** : Automatically detect model variant (Eagle v1/v2/HASS or Eagle-3).
  2. **State Dict Mapping** : Convert legacy checkpoint keys to Speculators format.
  3. **Config Building** : Generate `SpeculatorModelConfig` with embedded `speculator_config`.
  4. **Publishing** : Save in HuggingFace-compatible format.

**Sources:** [README.md55](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L55-L55) [docs/index.md31-32](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1#L31-L32)

## vLLM Integration

Models trained with Speculators deploy seamlessly to vLLM:

This single command:

  1. Loads the model from HuggingFace Hub.
  2. Parses the embedded `speculator_config` from `config.json`.
  3. Initializes both draft and verifier models.
  4. Orchestrates the draft-verify speculative decoding loop.

**Sources:** [README.md17-18](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L17-L18) [docs/index.md39-48](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1#L39-L48)

## Component Locations

Key implementation files:

Component| File Path  
---|---  
Base Model Classes| [src/speculators/models/speculator_model.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/models/speculator_model.py)  
Eagle Implementation| [src/speculators/models/eagle.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/models/eagle.py)  
Eagle3 Implementation| [src/speculators/models/eagle3/core.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/models/eagle3/core.py)  
PEagle Implementation| [src/speculators/models/peagle.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/models/peagle.py)  
DFlash Implementation| [src/speculators/models/dflash.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/models/dflash.py)  
Configuration System| [src/speculators/config.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/config.py)  
Hidden States Generator| [src/speculators/data_generation/vllm_hidden_states_generator.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/data_generation/vllm_hidden_states_generator.py)  
Trainer| [src/speculators/training/trainer.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/training/trainer.py)  
CLI Entrypoint| [src/speculators/__main__.py](https://github.com/vllm-project/speculators/blob/4f80f5dc/src/speculators/__main__.py)  
  
**Sources:** [pyproject.toml5-7](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L5-L7) [pyproject.toml115-116](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L115-L116)

## Development and Testing

The library uses a comprehensive testing framework with specialized GPU runners:

Title: Quality Assurance Pipeline

**Sources:** [pyproject.toml126-210](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L126-L210) [pyproject.toml59-112](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L59-L112)

## Installation Options

Install from PyPI (recommended):

For development installation:

**Sources:** [pyproject.toml13-56](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L13-L56) [docs/index.md174-182](https://github.com/vllm-project/speculators/blob/4f80f5dc/docs/index.md?plain=1#L174-L182)

## Project Links

  * **Repository** : <https://github.com/vllm-project/speculators>
  * **Documentation** : <https://docs.vllm.ai/projects/speculators/en/latest/>
  * **PyPI Package** : <https://pypi.org/project/speculators/>
  * **Model Collection** : <https://huggingface.co/collections/RedHatAI/speculator-models>
  * **vLLM Community Slack** : `#speculators` and `#feat-spec-decode` channels

**Sources:** [README.md29-36](https://github.com/vllm-project/speculators/blob/4f80f5dc/README.md?plain=1#L29-L36) [pyproject.toml118-121](https://github.com/vllm-project/speculators/blob/4f80f5dc/pyproject.toml#L118-L121)
