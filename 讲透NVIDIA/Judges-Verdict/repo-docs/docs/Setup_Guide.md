# Judge's Verdict Setup Guide

This guide provides detailed instructions for setting up the Judge's Verdict framework.

## Prerequisites

- Python 3.12 or higher
- Poetry (recommended) or pip
- API keys for desired LLM providers

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/NVIDIA/Judges-Verdict.git
cd Judges-Verdict

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/NVIDIA/Judges-Verdict.git
cd Judges-Verdict

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e .
```

## API Key Configuration

### OpenAI Models
For GPT-4, GPT-4o, and other OpenAI models:
```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic Models
For Claude models:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### NVIDIA NIM Models
For NVIDIA-hosted models (Llama, Nemotron, Gemma):
```bash
export NVIDIA_NIM_API_KEY="nvapi-..."
export NVIDIA_NIM_API_BASE="https://integrate.api.nvidia.com/v1"
```

## Data Preparation

### Download and Prepare Dataset

Run the data preparation script to fetch the evaluation dataset:

```bash
python scripts/data_prep.py
```

This will:
1. Download the `nvidia/judges-verdict` dataset from HuggingFace
2. Process train and test splits
3. Join with external datasets (CORAL, DC767)
4. Create `data/evaluation.json` (1,994 total entries)

### Dataset Details
- **Train split**: 200 techqa entries
- **Test split**: 1,794 entries across 6 datasets:
  - coral (318 entries)
  - dc767 (347 entries)
  - enterprise_rag_benchmark (346 entries)
  - hotpotqa (342 entries)
  - squad (346 entries)
  - techqa (95 entries)

## Configuration

### Basic Configuration

The framework uses YAML configuration files. A minimal example:

```yaml
# config/my_judges.yaml
defaults:
  temperature: 0.0
  max_tokens: 8
  num_workers: 16
  timeout: 60

models:
  gpt-4o:
    framework: litellm
    model: openai/gpt-4o
    num_workers: 8
    
  claude-sonnet:
    framework: litellm
    model: anthropic/claude-sonnet-4-20250514
    num_workers: 4
```

### Advanced Configuration

For local models or custom endpoints:

```yaml
models:
  local-llama:
    framework: litellm
    model: hosted_vllm/meta-llama/Llama-3.3-70B-Instruct
    base_url: http://localhost:8000/v1
    api_key: EMPTY
    num_workers: 1
    temperature: 0.0
    max_tokens: 100
```

## Running Evaluations

### Basic Usage

```bash
# Using the default configuration
poetry run llm-judge-score

# Or with custom options
poetry run llm-judge-score \
    --evaluation-file data/evaluation.json \
    --config config/judge_config_litellm.yaml \
    --output-dir results/
```

### Specific Judges Only

```bash
# Run only specific judges
poetry run llm-judge-score --judges gpt-4o claude-sonnet
```

### Custom Configuration File

```bash
# Use a custom configuration
poetry run llm-judge-score --config config/my_custom_judges.yaml
```

### Advanced Options

```bash
poetry run llm-judge-score \
    --evaluation-file data/my_data.json \
    --config config/my_judges.yaml \
    --output-dir my_results/ \
    --judges gpt-4o claude-sonnet llama-70b \
    --max-trials 5 \
    --default-workers 32
```

## Local Model Setup

### Using vLLM

1. Start vLLM server:
```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.3-70B-Instruct \
    --port 8000
```

2. Configure in YAML:
```yaml
models:
  local-llama-70b:
    framework: litellm
    model: hosted_vllm/meta-llama/Llama-3.3-70B-Instruct
    base_url: http://localhost:8000/v1
    api_key: EMPTY
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure package is installed
poetry install
# Or
pip install -e .
```

#### Missing API Keys
Check environment variables:
```bash
env | grep -E "(OPENAI|ANTHROPIC|NVIDIA|ONE_API)_"
```

#### Rate Limits
Reduce worker count in configuration:
```yaml
models:
  my-model:
    num_workers: 2  # Reduce from default
```

#### Memory Issues
For large local models:
```bash
# Set CUDA memory fraction
export CUDA_VISIBLE_DEVICES=0
export VLLM_GPU_MEMORY_UTILIZATION=0.9
```

## Performance Tuning

### Worker Configuration
- **API models**: 8-16 workers typically optimal
- **Local models**: 1-4 workers depending on hardware
- **Rate-limited APIs**: 2-4 workers

### Timeout Settings
Increase for slower models:
```yaml
models:
  large-model:
    timeout: 300  # 5 minutes
```

## Next Steps

1. Review [Architecture Overview](Architecture_Overview.md)
2. Check example configurations in `config/`
3. Run a small test evaluation
4. Scale up to full dataset
5. Analyze results using correlation scripts
