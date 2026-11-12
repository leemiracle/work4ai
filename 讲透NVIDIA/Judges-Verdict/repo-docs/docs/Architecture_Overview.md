# Judge's Verdict Architecture Overview

This document provides an overview of the Judge's Verdict framework architecture.

## System Components

### Core Package Structure

```
llm_judge_benchmark/
├── scoring/                 # Judge scoring implementation
│   └── llm_judge_scoring.py # Main evaluation script
├── utils/                   # Utility functions
│   └── litellm_ragas_wrapper.py # RAGAS integration
├── judge_config.py          # Judge configuration classes
└── judge_config_manager.py  # YAML config management
```

### Key Components

#### 1. Judge Configuration Manager
- **Purpose**: Manages judge model configurations from YAML files
- **Location**: `llm_judge_benchmark/judge_config_manager.py`
- **Features**:
  - Loads judge configurations from YAML
  - Supports multiple serving frameworks (LiteLLM, NVDEV, OneAPI)
  - Manages API keys and endpoints
  - Provides model creation interfaces

#### 2. Scoring Engine
- **Purpose**: Evaluates LLM responses using judge models
- **Location**: `llm_judge_benchmark/scoring/llm_judge_scoring.py`
- **Features**:
  - Parallel processing with configurable workers
  - Multiple trial support
  - Progress tracking and checkpointing
  - Integration with RAGAS metrics

#### 3. LiteLLM Integration
- **Purpose**: Provides unified interface for multiple LLM providers
- **Location**: `llm_judge_benchmark/utils/litellm_ragas_wrapper.py`
- **Supported Providers**:
  - OpenAI (GPT-4, GPT-4o, etc.)
  - Anthropic (Claude models)
  - NVIDIA NIM (Llama, Nemotron, Gemma)
  - Local models via vLLM

## Data Flow

### 1. Data Preparation
```
HuggingFace Dataset → data_prep.py → evaluation.json
```

The `scripts/data_prep.py` script:
- Downloads the `nvidia/judges-verdict` dataset
- Processes train and test splits
- Joins with external datasets (CORAL, DC767)
- Creates unified evaluation format

### 2. Judge Evaluation
```
evaluation.json → Scoring Engine → Judge Models → Results
```

The evaluation process:
1. Load evaluation data
2. Create RAGAS dataset
3. For each judge model:
   - Run multiple trials
   - Save results to JSON
   - Track progress

### 3. Results Structure
```
results/
├── judge-model-1/
│   ├── trial1.json
│   ├── trial2.json
│   └── trial3.json
└── judge-model-2/
    ├── trial1.json
    ├── trial2.json
    └── trial3.json
```

## Configuration System

### YAML Configuration Format
```yaml
defaults:
  temperature: 0.0
  max_tokens: 8
  num_workers: 16
  timeout: 60

models:
  model-identifier:
    framework: litellm
    model: provider/model-name
    temperature: 0.0
    max_tokens: 8
    num_workers: 16
```

### Model Identifier Rules
- Model identifiers in YAML become folder names in results/
- Use filesystem-safe names (no special characters)
- Should be descriptive and unique

## Extensibility

### Adding New Judge Models
1. Add configuration to YAML file
2. Ensure API keys are set
3. Run evaluation script

### Adding New Metrics
1. Implement RAGAS-compatible metric
2. Update scoring script to use new metric
3. Modify result processing as needed

### Adding New Frameworks
1. Add new `ServingFramework` enum value
2. Implement framework-specific model creation
3. Update configuration parsing

## Performance Considerations

### Parallelization
- Worker count configurable per judge
- Concurrent processing for efficiency
- Async support where available

### Resource Management
- Timeout configuration
- Retry logic for failed requests

## Error Handling

### Common Issues
1. **Missing API Keys**: Check environment variables
2. **Rate Limits**: Adjust worker count
3. **Timeouts**: Increase timeout value
4. **Model Errors**: Check model availability

### Debugging
- Progress bars show current state
- Checkpoint files for recovery
