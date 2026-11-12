# Judge's Verdict

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Dataset](https://img.shields.io/badge/dataset-HuggingFace-yellow.svg)](https://huggingface.co/datasets/nvidia/judges-verdict)

A comprehensive framework for evaluating Large Language Models (LLMs) as judges for assessing the quality of AI-generated responses.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Command Line Options](#command-line-options)
- [Troubleshooting](#troubleshooting)
- [Extending the Framework](#extending-the-framework)
- [Development](#development)
- [Contributing](#contributing)

## Overview

This repository contains the evaluation pipeline for running Judge's Verdict on the `nvidia/judges-verdict` HuggingFace dataset. The framework uses LiteLLM as the officially supported approach for interfacing with various LLM providers through a unified API.

**Supported Providers via LiteLLM:**
- OpenAI (GPT-4, GPT-4o, etc.)
- Anthropic (Claude models)
- NVIDIA NIM (Llama, Nemotron, Gemma, etc.)
- Local models (via vLLM or other compatible servers)
- Many other providers (see [LiteLLM docs](https://docs.litellm.ai/docs/providers))


## Features

- **Flexible Judge Configuration**: YAML-based configuration system for managing multiple judge models
- **Multiple Serving Frameworks**: Support for various LLM serving backends
- **Annotation Preparation**: Scripts for preparing and merging human annotations
- **Parallel Processing**: Efficient evaluation with configurable workers
- **Extensible Architecture**: Easy to add new judge models and metrics

## Installation

```bash
# Clone the repository
git clone https://github.com/NVIDIA/Judges-Verdict.git
cd Judges-Verdict

# Install using Poetry (recommended)
poetry install

# Or install with pip
pip install -e .
```

## Project Structure

```
Judges-Verdict/
├── llm_judge_benchmark/         # Core package
│   ├── scoring/                 # Judge scoring implementation
│   ├── utils/                   # Utility functions
│   ├── judge_config.py          # Judge configuration classes
│   └── judge_config_manager.py  # YAML config management
├── scripts/                     # Standalone scripts
│   └── data_prep.py            # Data preparation script (fetches from HuggingFace)
├── config/                      # Configuration files
│   ├── judge_config_litellm.yaml
│   └── judge_config_litellm_example.yaml
├── data/                        # Data directory
│   ├── annotations_sample.json # Sample annotations
│   └── evaluation.json         # Merged evaluation dataset (created by data_prep.py)
├── results/                     # Evaluation results
└── docs/                        # Documentation
```

## Quick Start

### 1. Install dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -e .
```

### 2. Set up API keys

The project uses the LiteLLM framework as the officially supported approach for judge scoring, which provides a unified interface for multiple LLM providers.

```bash
# For OpenAI models (gpt-4o, gpt-4, etc.)
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic models (claude-sonnet-4, etc.)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For NVIDIA NIM models (llama, nemotron, gemma, etc.)
export NVIDIA_NIM_API_KEY="your-nvidia-nim-api-key"
export NVIDIA_NIM_API_BASE="https://integrate.api.nvidia.com/v1"  # or your custom endpoint

# For other providers supported by LiteLLM, see: https://docs.litellm.ai/docs/providers
```

Note: The LiteLLM framework automatically handles provider-specific authentication and API formatting.

### 3. Prepare the data

```bash
# Run the data preparation script
python scripts/data_prep.py
```

This will:
- Download the `nvidia/judges-verdict` dataset from HuggingFace
- Process the train split (200 techqa entries, annotations removed)
- Process the test split (1,794 entries across 6 datasets):
  - **coral** (318 entries): Joins with CORAL dataset from HuggingFace
  - **dc767** (347 entries): Joins with DC767 CSV from GitHub
  - **enterprise_rag_benchmark** (346 entries): Used as-is
  - **hotpotqa** (342 entries): Used as-is
  - **squad** (346 entries): Used as-is
  - **techqa** (95 entries): Used as-is
- Merge all datasets into `data/evaluation.json` (1,994 total entries)

### 4. Run Judge Scoring

```bash
# Using the installed script
poetry run llm-judge-score \
    --evaluation-file data/evaluation.json \
    --output-dir results/

# Or run directly
python -m llm_judge_benchmark.scoring.llm_judge_scoring \
    --evaluation-file data/evaluation.json \
    --config config/judge_config_litellm.yaml \
    --output-dir results/
```


## Configuration

### Judge Configuration

Judges are configured using YAML files with LiteLLM as the primary framework. Each judge requires:

- `identifier`: Unique identifier for the judge (it's also used as the folder name for judge evaluation results)
- `framework`: Always use `litellm` for the officially supported approach
- `model`: Model name in LiteLLM format (e.g., `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514`, `nvidia_nim/meta/llama-3.1-70b-instruct`)
- `temperature`: Temperature setting (usually 0.0 for consistency)
- `max_tokens`: Maximum tokens for response
- `num_workers`: Number of parallel workers
- `timeout`: Request timeout in seconds

The model identifiers in the configuration YAML will be the folder names where results will be stored. For example:

```yaml
models:
  gpt-4o:  # This creates results in results/gpt-4o/
    framework: litellm
    model: openai/gpt-4o
    
  meta_llama-3.1-70b-instruct:  # This creates results in results/meta_llama-3.1-70b-instruct/
    framework: litellm
    model: nvidia_nim/meta/llama-3.1-70b-instruct
```

### Local Model Configuration

Local models are also supported by the `litellm` framework. When configuring a local model, you need to specify:
- `framework: litellm`
- `model`: The model name in litellm format (e.g., `hosted_vllm/...`)
- `base_url`: The URL of your local model server
- `api_key`: Usually set to "EMPTY" for local models

Example configuration for a local Qwen model:

```yaml
local/qwen-0.5b:
  framework: litellm
  model: hosted_vllm/Qwen/Qwen2-0.5B-Instruct
  base_url: http://localhost:8000/v1
  api_key: EMPTY
  num_workers: 1
```

This assumes you have a VLLM server running locally on port 8000 serving the Qwen2-0.5B-Instruct model.

The repository includes configuration files for the LiteLLM framework:
- `config/judge_config_litellm.yaml`: Main configuration file with all supported judge models using LiteLLM
- `config/judge_config_litellm_example.yaml`: Minimal example configuration with verified working models

### Environment Variables

The framework requires API keys to be set as environment variables. See the Quick Start section above for details on setting up API keys for different providers.

### LiteLLM Model Name Format

When configuring models in the YAML files, use the following format for model names:

- **OpenAI**: `openai/model-name` (e.g., `openai/gpt-4o`, `openai/gpt-4`)
- **Anthropic**: `anthropic/model-name` (e.g., `anthropic/claude-sonnet-4-20250514`)
- **NVIDIA NIM**: `nvidia_nim/provider/model-name` (e.g., `nvidia_nim/meta/llama-3.1-70b-instruct`)
- **Local Models**: `hosted_vllm/model-path` (e.g., `hosted_vllm/Qwen/Qwen2-0.5B-Instruct`)

For a complete list of supported providers and their formats, see the [LiteLLM Provider Documentation](https://docs.litellm.ai/docs/providers).

## Evaluation Data Format

The framework uses evaluation data from the HuggingFace dataset `nvidia/judges-verdict`. After processing by `data_prep.py`, the data is in the following format:

```json
[
  {
    "item_name": "unique_identifier",
    "dataset_name": "dataset_source",
    "question": "The question text",
    "gt_answer": "The ground truth/reference answer",
    "gen_answer": "The generated answer"
  }
]
```

The `data_prep.py` script:
- Downloads the `nvidia/judges-verdict` dataset from HuggingFace
- Processes train split data (removes annotations field)
- Processes test split data from 6 different datasets
- For coral and dc767 datasets, joins with external data sources to get complete question/answer pairs
- Merges all data into a single `data/evaluation.json` file

## Command Line Options

The main scoring script supports the following options:

```bash
llm-judge-score \
    --evaluation-file PATH      # Path to evaluation JSON file (default: ./data/evaluation.json)
    --output-dir PATH          # Output directory for results (default: ./results/)
    --judges NAME [NAME ...]   # Specific judges to run (space-separated list, optional)
    --max-trials N             # Maximum trials per judge (default: 3)
    --default-workers N        # Default workers for judges not in config (default: 16)
    --config-file PATH         # Path to judge config YAML file (optional)
```

## Troubleshooting

- **Import errors**: Make sure to install the package with `poetry install` or `pip install -e .`
- **Missing API keys**: Set the appropriate environment variables for your judge models
- **Missing data files**: Run `python scripts/data_prep.py` to download and prepare the evaluation data
- **File not found errors**: Ensure the data preparation script has been run to create `evaluation.json`
- **HuggingFace dataset errors**: Make sure you have the `datasets` library installed (automatically installed with Poetry)

## Extending the Framework

### Adding a New Judge Model

1. Add the model configuration to your YAML config file using the LiteLLM framework
2. Ensure you use the correct LiteLLM model name format (e.g., `provider/model-name`)
3. Set up the required API keys for your model provider

### Adding New Metrics

1. Create a new metric class following the RAGAS metric interface
2. Update the scoring script to use the new metric
3. Add configuration options as needed

## Development

### Code Style and Formatting

This project uses several tools to maintain consistent code quality:

- **Black**: Code formatter with 120-character line limit
- **isort**: Import statement organizer
- **flake8**: Style guide enforcement

#### Running Code Formatters

```bash
# Format all Python files with black
poetry run black llm_judge_benchmark/ scripts/

# Sort imports with isort
poetry run isort llm_judge_benchmark/ scripts/

# Or run both together
poetry run black llm_judge_benchmark/ scripts/ && poetry run isort llm_judge_benchmark/ scripts/
```

#### Running Linter Checks

```bash
# Check code style with flake8
poetry run flake8 llm_judge_benchmark/ scripts/

# Show statistics
poetry run flake8 llm_judge_benchmark/ scripts/ --count --statistics
```

#### Pre-commit Checks (Recommended)

Before committing code, run all formatters and linters:

```bash
# Format code
poetry run black llm_judge_benchmark/ scripts/
poetry run isort llm_judge_benchmark/ scripts/

# Check for any remaining issues
poetry run flake8 llm_judge_benchmark/ scripts/
```

#### Configuration

The project's formatting tools are configured as follows:

- **Black** (`pyproject.toml`):
  - Line length: 120 characters
  - Target Python version: 3.12

- **isort** (`pyproject.toml`):
  - Line length: 120 characters
  - Multi-line output style: 3 (vertical hanging indent)
  - Trailing commas in multi-line imports

- **flake8** (`.flake8`):
  - Line length: 120 characters
  - Ignored rules: W503, E203 (conflicts with black)
  - Complexity threshold: 10

## Contributing

Contributions are welcome! Please ensure your code follows the project's style guidelines by running the formatters and linters before submitting a Pull Request.

