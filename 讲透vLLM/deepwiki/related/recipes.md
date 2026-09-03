# recipes

> 来源: https://deepwiki.com/vllm-project/recipes 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [.claude/skills/add-recipe/SKILL.md](https://github.com/vllm-project/recipes/blob/7b274be8/.claude/skills/add-recipe/SKILL.md?plain=1)
  * [ArceeAI/Trinity-Large-Thinking.md](https://github.com/vllm-project/recipes/blob/7b274be8/ArceeAI/Trinity-Large-Thinking.md?plain=1)
  * [CLAUDE.md](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1)
  * [DeepSeek/DeepSeek-V3_2.md](https://github.com/vllm-project/recipes/blob/7b274be8/DeepSeek/DeepSeek-V3_2.md?plain=1)
  * [GLM/GLM5.md](https://github.com/vllm-project/recipes/blob/7b274be8/GLM/GLM5.md?plain=1)
  * [MiniMax/MiniMax-M2.md](https://github.com/vllm-project/recipes/blob/7b274be8/MiniMax/MiniMax-M2.md?plain=1)
  * [README.md](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1)
  * [models/PaddlePaddle/PaddleOCR-VL-1.5.yaml](https://github.com/vllm-project/recipes/blob/7b274be8/models/PaddlePaddle/PaddleOCR-VL-1.5.yaml)
  * [scripts/build-recipes-api.mjs](https://github.com/vllm-project/recipes/blob/7b274be8/scripts/build-recipes-api.mjs)
  * [taxonomy.yaml](https://github.com/vllm-project/recipes/blob/7b274be8/taxonomy.yaml)

## Purpose and Scope

The vllm-project/recipes repository is a community-maintained collection of deployment guides and an interactive web application designed to answer the practical question: **"How do I run model X on hardware Y for task Z?"**

The repository serves a dual nature:

  1. **A Content Repository** : A structured collection of YAML definitions and legacy Markdown guides covering dozens of model families (DeepSeek, Qwen, Llama, etc.) and hardware platforms (NVIDIA Hopper/Blackwell, AMD Instinct, Google TPU). [README.md1-5](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1#L1-L5) [CLAUDE.md7-10](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L7-L10)
  2. **An Interactive Web Application** : A Next.js 15 application that renders these recipes as a dynamic command builder, allowing users to toggle features like speculative decoding or tool calling and generate precise `vllm serve` commands. [CLAUDE.md10-13](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L10-L13) [README.md125-133](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1#L125-L133)

For detailed coverage of specific model families, see the [Model Coverage](/vllm-project/recipes/1.2-model-coverage) child page. For details on how the codebase is organized, see [Repository Structure](/vllm-project/recipes/1.1-repository-structure).

Sources: [README.md1-5](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1#L1-L5) [CLAUDE.md7-13](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L7-L13)

## Repository Structure and Organization

The repository has transitioned from a purely Markdown-based collection to a data-driven architecture. While legacy Markdown guides are maintained in the root (e.g., `DeepSeek/`, `Qwen/`), new recipes are authored as structured YAML files in the `models/` directory. [README.md125-138](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1#L125-L138) [CLAUDE.md9-12](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L9-L12)

### System Architecture: From YAML to Interactive UI

**Figure 1: Bridge between Natural Language definitions and Code Entities**

The repository utilizes a build pipeline `scripts/build-recipes-api.mjs` that validates YAML files against a controlled vocabulary in `taxonomy.yaml` and parallelization patterns in `strategies/`. [scripts/build-recipes-api.mjs1-15](https://github.com/vllm-project/recipes/blob/7b274be8/scripts/build-recipes-api.mjs#L1-L15) [taxonomy.yaml1-3](https://github.com/vllm-project/recipes/blob/7b274be8/taxonomy.yaml#L1-L3) [CLAUDE.md42-46](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L42-L46)

For details on the directory layout and the build pipeline, see [Repository Structure](/vllm-project/recipes/1.1-repository-structure).

Sources: [CLAUDE.md34-46](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L34-L46) [README.md125-144](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1#L125-L144) [scripts/build-recipes-api.mjs1-34](https://github.com/vllm-project/recipes/blob/7b274be8/scripts/build-recipes-api.mjs#L1-L34)

## Model and Hardware Coverage

vLLM Recipes provides comprehensive coverage for modern LLM architectures. The repository tracks the latest hardware optimizations, such as FP8 and NVFP4 quantization for NVIDIA Blackwell and Hopper GPUs, as well as AITER acceleration for AMD ROCm. [taxonomy.yaml5-121](https://github.com/vllm-project/recipes/blob/7b274be8/taxonomy.yaml#L5-L121) [MiniMax/MiniMax-M2.md174-188](https://github.com/vllm-project/recipes/blob/7b274be8/MiniMax/MiniMax-M2.md?plain=1#L174-L188)

### Key Coverage Areas

  * **Model Families** : DeepSeek (V3, R1, V4), Qwen (3, 2.5-VL), Llama (3.3, 4-Scout), GLM (5.1), MiniMax (M2), and more. [README.md8-122](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1#L8-L122)
  * **Hardware Profiles** : NVIDIA H100/H200, B200, GB200; AMD MI300X/MI325X; Google TPU Trillium/Ironwood; Intel Xeon 6. [taxonomy.yaml4-166](https://github.com/vllm-project/recipes/blob/7b274be8/taxonomy.yaml#L4-L166)
  * **Tasks** : Text, Multimodal (Vision/Audio), Omni (Any-to-any), and Embedding/Reranking. [taxonomy.yaml167-180](https://github.com/vllm-project/recipes/blob/7b274be8/taxonomy.yaml#L167-L180)

For a complete list of models and their specific deployment nuances, see [Model Coverage](/vllm-project/recipes/1.2-model-coverage).

Sources: [README.md8-122](https://github.com/vllm-project/recipes/blob/7b274be8/README.md?plain=1#L8-L122) [taxonomy.yaml4-180](https://github.com/vllm-project/recipes/blob/7b274be8/taxonomy.yaml#L4-L180) [MiniMax/MiniMax-M2.md174-188](https://github.com/vllm-project/recipes/blob/7b274be8/MiniMax/MiniMax-M2.md?plain=1#L174-L188)

## The vLLM Command Synthesis

The core logic of the repository resides in `src/lib/command-synthesis.js`. This module contains the `resolveCommand` function, which synthesizes the final `vllm serve` command by merging base arguments, hardware-specific overrides, and parallelization strategy requirements. [CLAUDE.md45-46](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L45-L46) [scripts/build-recipes-api.mjs22-34](https://github.com/vllm-project/recipes/blob/7b274be8/scripts/build-recipes-api.mjs#L22-L34)

### Command Generation Workflow

**Figure 2: Command Synthesis Flow**

The system handles complex deployment patterns, including multi-node setups and Prefill/Decode (PD) disaggregation, by generating specialized environment variables and argument flags (e.g., `--tensor-parallel-size`, `--kv-cache-dtype`). [scripts/build-recipes-api.mjs140-162](https://github.com/vllm-project/recipes/blob/7b274be8/scripts/build-recipes-api.mjs#L140-L162) [CLAUDE.md45-46](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L45-L46)

For more information on deployment patterns and parallelization, see [Common Deployment Patterns](/vllm-project/recipes/2.2-common-deployment-patterns) and [Parallelization Strategies Overview](/vllm-project/recipes/2.4-parallelization-strategies-overview).

Sources: [CLAUDE.md45-46](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L45-L46) [scripts/build-recipes-api.mjs22-34](https://github.com/vllm-project/recipes/blob/7b274be8/scripts/build-recipes-api.mjs#L22-L34) [scripts/build-recipes-api.mjs140-162](https://github.com/vllm-project/recipes/blob/7b274be8/scripts/build-recipes-api.mjs#L140-L162)

## Contributing to the Ecosystem

Contributors add new recipes by creating YAML files in `models/<hf_org>/<hf_repo>.yaml`. The repository includes a Claude "skill" and helper scripts like `scripts/hf-info.sh` to automate the extraction of model metadata from HuggingFace. [CLAUDE.md56-61](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L56-L61) [.claude/skills/add-recipe/SKILL.md1-24](https://github.com/vllm-project/recipes/blob/7b274be8/.claude/skills/add-recipe/SKILL.md?plain=1#L1-L24)

For the full contribution workflow and YAML schema details, see [Contributing to vLLM Recipes](/vllm-project/recipes/13-contributing-to-vllm-recipes).

Sources: [.claude/skills/add-recipe/SKILL.md1-24](https://github.com/vllm-project/recipes/blob/7b274be8/.claude/skills/add-recipe/SKILL.md?plain=1#L1-L24) [CLAUDE.md56-61](https://github.com/vllm-project/recipes/blob/7b274be8/CLAUDE.md?plain=1#L56-L61)
