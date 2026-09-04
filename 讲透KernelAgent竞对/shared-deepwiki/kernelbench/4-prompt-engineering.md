> 来源: https://deepwiki.com/ScalingIntelligence/KernelBench/4-prompt-engineering | 抓取: 2026-09-03 | DeepWiki SSR 快照

# Prompt Engineering

Relevant source files

- scripts/verify_generation.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/verify_generation.py]

- src/kernelbench/prompts/model_ex_add_thunderkittens.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/prompts/model_ex_add_thunderkittens.py]

- src/kernelbench/prompts/model_new_ex_add_thunderkittens.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/prompts/model_new_ex_add_thunderkittens.py]

- src/kernelbench/prompts/prompts.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/kernelbench/prompts/prompts.toml]

This document explains KernelBench's TOML-based prompt construction system. It covers how prompts are assembled from modular templates, the different backend and prompting strategies supported, and how to customize prompts for specific optimization goals. For practical usage of these prompts in kernel generation, see page 3.1.

## Overview

KernelBench uses a declarative TOML configuration system (src/prompts/prompts.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml]) to define prompt templates and assembly rules. The system supports multiple kernel backends (CUDA, Triton, CuTe, TileLang), multiple prompting strategies (zero-shot, one-shot, few-shot), and optional hardware-specific guidance. Prompts are composed from reusable template blocks and filled with context (reference architecture, examples, hardware specs) at generation time.

Core Prompt Construction Pipeline:

```

The main entry points are `get_prompt_for_backend()` and `get_custom_prompt()` in src/prompt_constructor_toml.py330-397 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L330-L397] which internally call `render_prompt_by_option()` to assemble prompts from TOML-defined components.

Sources: src/prompt_constructor_toml.py1-20 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L1-L20] src/prompts/prompts.toml1-214 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L1-L214]

## TOML Configuration Structure

The src/prompts/prompts.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml] file organizes prompt components into several hierarchical sections:

| | Section | Purpose | Example Keys
| `[meta]` | Global defaults | `version`, `default_backend`, `default_precision`
| `[shared]` | Backend-agnostic text | `problem_statement`, `instruction`
| `[backends.<name>]` | Backend-specific config | `backend_display`, `one_shot_new_arch`, `few_shot_examples`
| `[precision.<type>]` | Precision descriptions | `precision_display` for fp32/fp16/bf16
| `[templates.common]` | Reusable template blocks | `arch_block`, `examples_block`, `precision_note`
| `[templates.hardware]` | GPU-specific templates | `hardware_specs`, `hardware_definitions`, `hardware_best_practices`
| `[options.<name>]` | Prompt assembly rules | `components` list, `requires_example` flag
| `[custom_prompts.<name>]` | User-defined compositions | Custom `components` ordering

The configuration uses placeholder syntax (e.g., `{backend_display}`, `{ref_arch_src}`) that is filled at render time.

Sources: src/prompts/prompts.toml1-214 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L1-L214] src/prompt_constructor_toml.py36-65 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L36-L65]

## Prompt Assembly Process

Diagram: Template Composition Flow

```

The `render_prompt_by_option()` function implements this assembly logic:

- Load Configuration: Parse src/prompts/prompts.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml] into a `PromptConfig` instance

- Validate Backend/Option: Check that the specified backend and option exist in configuration

- Build Component List: Retrieve `components` array from `[options.<name>]`, optionally inject hardware blocks

- Prepare Context: Assemble a dictionary with values for all placeholders (`ref_arch_src`, `backend_display`, `precision_display`, `gpu_specs_bullets`, etc.)

- Load Examples: If option requires examples, load example architecture files and format them

- Compose Blocks: For each component name, retrieve the corresponding template string using `compose_blocks()`

- Format and Return: Apply `.format(**context)` to replace all placeholders

Sources: src/prompt_constructor_toml.py135-324 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L135-L324] src/prompt_constructor_toml.py67-97 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L67-L97]

## Backend-Specific Configuration

KernelBench supports four kernel backends, each with its own display name and example files:

Supported Backends:

```

CUDA Backend: Provides the richest set of examples, including few-shot examples for operator fusion and flash attention:

- One-shot: src/prompts/model_new_ex_add.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/model_new_ex_add.py]

- Few-shot: src/prompts/few_shot/model_new_ex_add.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/few_shot/model_new_ex_add.py] src/prompts/few_shot/model_new_ex_fuse_gelu.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/few_shot/model_new_ex_fuse_gelu.py] src/prompts/few_shot/model_new_ex_flash_attn.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/few_shot/model_new_ex_flash_attn.py]

Other Backends: Currently provide one-shot examples only. When few-shot option is selected for these backends, the system automatically falls back to one-shot mode.

Each backend has a `backend_display` string that is substituted into prompt templates (e.g., "CUDA operators", "Triton kernels").

Sources: src/prompts/prompts.toml26-50 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L26-L50] src/prompt_constructor_toml.py249-291 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L249-L291]

## Prompt Template Components

Prompts are assembled from modular template blocks defined in src/prompts/prompts.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml]:

Core Template Blocks:

| | Component Name | Location | Purpose | Required Placeholders
| `problem_statement` | `[shared]` | Describes the kernel optimization task | `{backend_display}`
| `instruction` | `[shared]` | Specifies output format and naming | `{backend_display}`
| `arch_block` | `[templates.common]` | Presents the reference architecture | `{ref_arch_src}`
| `examples_block` | `[templates.common]` | Shows input/output example pairs | `{examples_intro}`, `{examples_entries}`
| `precision_note` | `[templates.common]` | Specifies target precision | `{precision_display}`

Hardware Template Blocks (optional, injected when `include_hardware=True`):

| | Component Name | Purpose | Required Placeholders
| `hardware_header` | Introduces hardware section | None
| `hardware_specs` | Lists GPU specifications | `{gpu_name}`, `{gpu_architecture}`, `{gpu_specs_bullets}`
| `hardware_definitions` | Explains GPU concepts | `{gpu_definitions_bullets}`
| `hardware_best_practices` | Provides optimization tips | `{gpu_best_practices_bullets}`

Example Block Structure:

The `examples_block` template is dynamically formatted based on the number of examples:

```

Each example entry includes the input architecture, optimized output, and labels formatted using `example_entry_template`.

Sources: src/prompts/prompts.toml66-163 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L66-L163] src/prompt_constructor_toml.py227-291 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L227-L291]

## Prompting Options

The `[options.<name>]` sections in src/prompts/prompts.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml] define different prompting strategies by specifying which template components to include and in what order.

### Zero-Shot Prompting

Configuration: `[options.zero_shot]`

Zero-shot prompting provides no examples - the LLM must infer the task entirely from the problem description and instruction.

Component sequence:

- `problem_statement` - Task description

- `arch_block` - Reference architecture to optimize

- `precision_note` - Target precision

- `instruction` - Output format requirements

When to use: Testing LLM's baseline capability without guidance, or when no relevant examples exist.

Sources: src/prompts/prompts.toml168-170 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L168-L170]

### One-Shot Prompting

Configuration: `[options.one_shot]`

One-shot prompting includes a single example demonstrating the optimization task. This is the default strategy used in KernelBench baseline evaluations.

Component sequence:

- `problem_statement`

- `examples_block` - Single input/output example pair

- `arch_block`

- `precision_note`

- `instruction`

Example selection: Uses the `one_shot_new_arch` file specified in the backend configuration (e.g., src/prompts/model_new_ex_add.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/model_new_ex_add.py] for CUDA).

When to use: Standard kernel generation tasks. Provides enough context without overwhelming the LLM with multiple examples.

Sources: src/prompts/prompts.toml172-176 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L172-L176] src/prompt_constructor_toml.py275-285 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L275-L285]

### Few-Shot Prompting

Configuration: `[options.few_shot]`

Few-shot prompting shows multiple examples covering different optimization patterns. For CUDA backend, this includes:

- Element-wise addition (basic parallelization)

- Fused GeLU (operator fusion)

- Flash attention (advanced algorithm)

Component sequence: Same as one-shot, but `examples_block` contains multiple example pairs.

Fallback behavior: If a backend lacks `few_shot_examples` configuration, the system automatically falls back to one-shot mode.

When to use: Complex problems that benefit from seeing multiple optimization approaches, or when evaluating LLM's ability to learn from diverse examples.

Diagram: Few-Shot Example Selection

```

Sources: src/prompts/prompts.toml178-181 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L178-L181] src/prompts/prompts.toml31-35 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L31-L35] src/prompt_constructor_toml.py250-273 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L250-L273]

## Hardware-Aware Prompting

Hardware-aware prompting injects GPU-specific information into prompts to guide optimization for particular architectures.

Activation: Set `include_hardware=True` and provide `gpu_name` when calling `get_prompt_for_backend()` or `render_prompt_by_option()`.

Hardware Information Source: src/prompts/hardware/gpu_specs.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/hardware/gpu_specs.py] defines three data structures:

- `GPU_SPEC_INFO`: Dictionary mapping GPU names to specifications (memory bandwidth, SM count, etc.)

- `GPU_DEFINITIONS`: Glossary of GPU architecture terms (warp, block, shared memory, etc.)

- `GPU_BEST_PRACTICES`: List of optimization guidelines

Injection Location: Hardware blocks are inserted immediately before `arch_block` in the component sequence, or at explicit positions if using custom component ordering.

Diagram: Hardware Context Loading

```

Example usage:

```

Sources: src/prompt_constructor_toml.py99-133 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L99-L133] src/prompt_constructor_toml.py184-194 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L184-L194] src/prompts/prompts.toml141-162 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L141-L162]

## Custom Prompt Definitions

Users can define custom prompt compositions in src/prompts/prompts.toml [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml] under `[custom_prompts.<name>]` sections. This allows arbitrary component ordering and selection.

Example Custom Prompt (`[custom_prompts.custom]`):

```

Usage: Call `get_custom_prompt()` with `custom_key` parameter:

```

Requirements:

- Backend and precision must still be specified (required for evaluation)

- Hardware templates require `include_hardware=True` and `gpu_name`

- Components must reference valid template paths in the TOML file

Custom Template Blocks: Define new templates under `[templates.common]` or elsewhere, then reference them in custom component lists:

```

Sources: src/prompts/prompts.toml189-214 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/prompts.toml#L189-L214] src/prompt_constructor_toml.py361-397 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L361-L397]

## Practical Usage Examples

Script: scripts/verify_generation.py [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/verify_generation.py] demonstrates prompt construction and LLM querying for quick iteration.

Basic Generation:

```

Testing Multiple Prompt Strategies: src/prompt_constructor_toml.py413-478 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L413-L478] contains a `test_prompt()` function that generates and saves prompts for different configurations:

- Baseline (one-shot CUDA)

- Few-shot (multiple CUDA examples)

- DSL (Triton backend)

- Hardware-aware (CuTe with GPU specs)

- Custom (user-defined template)

Output files are saved to `./scratch/` for inspection.

Sources: scripts/verify_generation.py10-88 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/scripts/verify_generation.py#L10-L88] src/prompt_constructor_toml.py413-478 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompt_constructor_toml.py#L413-L478]

## 6. Example Templates

KernelBench includes several example templates that demonstrate different optimization techniques:

| | Example | Description | Location
| ex_add | Pointwise addition | src/prompts/few_shot/model_ex_add.py
| ex_fuse_gelu | Fused GeLU activation | src/prompts/few_shot/model_ex_fuse_gelu.py
| ex_tiled_matmul | Tiled matrix multiplication | src/prompts/few_shot/model_ex_tiled_matmul.py
| ex_flash_attn | Simple flash attention | src/prompts/few_shot/model_ex_flash_attn.py
| ex_mnist2 | Fused convolutions and ReLU | src/prompts/few_shot/model_ex_mnist2.py

These examples serve as templates for few-shot learning and as demonstrations of different optimization techniques.

Sources: src/prompts/README.md1-10 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/README.md?plain=1#L1-L10] src/prompts/few_shot/model_new_ex_mnist2.py1-95 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/few_shot/model_new_ex_mnist2.py#L1-L95] src/prompts/few_shot/model_ex_flash_attn.py1-36 [https://github.com/ScalingIntelligence/KernelBench/blob/2f65279d/src/prompts/few_shot/model_ex_flash_attn.py#L1-L36]

## 7. Conclusion

The prompt engineering system in KernelBench provides a flexible framework for generating optimized CUDA kernels using various LLM prompting strategies. From basic examples to sophisticated hardware-aware chain-of-thought prompting, the system offers multiple approaches to guide LLMs in creating efficient, correct CUDA implementations.

For detailed information about how these prompts are used in kernel generation, see Generating Kernels with LLMs [/ScalingIntelligence/KernelBench/3.1-generating-kernels-with-llms], and for evaluation of the generated kernels, see Evaluating Kernels [/ScalingIntelligence/KernelBench/3.2-batch-evaluation].

DismissRefresh this wiki

