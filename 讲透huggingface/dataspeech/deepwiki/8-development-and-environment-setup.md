<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataspeech · page 8 Development and Environment Setup · fetched 2026-10-26 -->

# Development and Environment Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

This page covers the technical setup required for developing and contributing to the dataspeech codebase. It includes dependency management, environment configuration, project structure understanding, and development workflows. For information about running the processing pipeline, see [Core Processing Pipeline](#2). For configuration of specific processing modules, see [Configuration and Data Management](#5).

## Prerequisites and System Requirements

The dataspeech repository requires specific system capabilities depending on the intended usage:

### Hardware Requirements

| Component | Minimum | Recommended | Purpose |
|-----------|---------|-------------|---------|
| RAM | 8GB | 16GB+ | Dataset loading and processing |
| GPU Memory | N/A (CPU only) | 8GB+ VRAM | GPU-accelerated enrichments |
| Storage | 50GB | 200GB+ | Dataset caching and artifacts |
| CPU | 4 cores | 8+ cores | Parallel processing |

### Software Prerequisites

- Python 3.8+
- CUDA 11.8+ (for GPU acceleration)
- Git (for repository management)
- Optional: Docker (for containerized development)

## Installation and Dependencies

### Core Dependencies Structure

```mermaid
graph TB
    subgraph "Audio Processing Dependencies"
        DATASETS["datasets[audio]"] --> AUDIO_IO["Audio I/O & Format Support"]
        BROUHAHA["brouhaha-vad<br/>(GitHub: marianne-m/brouhaha-vad)"] --> VAD["Voice Activity Detection"]
        DEMUCS["demucs"] --> SEPARATION["Audio Source Separation"]
    end
    
    subgraph "Speech Analysis Dependencies"
        PENN["penn"] --> PITCH["Pitch Analysis"]
        G2P["g2p"] --> PHONEMES["Phoneme Conversion"]
    end
    
    subgraph "Machine Learning Dependencies"
        TRANSFORMERS["transformers"] --> LLM["Language Model Support"]
        ACCELERATE["accelerate"] --> DISTRIBUTED["Multi-GPU Distribution"]
        BITSANDBYTES["bitsandbytes"] --> QUANTIZATION["Model Quantization"]
    end
    
    subgraph "Core Framework"
        PYTORCH["torch (implied)"] --> GPU_COMPUTE["GPU Computation"]
        TORCHAUDIO["torchaudio (implied)"] --> AUDIO_PROC["Audio Processing"]
    end
```

Sources: [requirements.txt:1-8]()

### Installation Process

1. **Environment Creation**
```bash
python -m venv env_dataspeech
source env_dataspeech/bin/activate  # Linux/Mac
# env_dataspeech\Scripts\activate  # Windows
```

2. **Dependency Installation**
```bash
pip install -r requirements.txt
```

3. **GPU Setup Verification**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
```

## Project Structure and Code Organization

### Development File Structure

```mermaid
graph TB
    subgraph "Root Directory Structure"
        ROOT["/"] --> MAIN_PY["main.py<br/>Pipeline Orchestrator"]
        ROOT --> REQUIREMENTS["requirements.txt<br/>Dependencies"]
        ROOT --> GITIGNORE[".gitignore<br/>Version Control Rules"]
        
        ROOT --> SCRIPTS_DIR["scripts/<br/>Processing Scripts"]
        ROOT --> DATASPEECH_DIR["dataspeech/<br/>Core Modules"]
        ROOT --> CONFIG_DIR["*_bin_edges.json<br/>*_text_bins.json<br/>Configuration Files"]
    end
    
    subgraph "Generated/Ignored Directories"
        ROOT --> ARTIFACTS["artefacts/<br/>(ignored)"]
        ROOT --> ENV["env_dataspeech/<br/>(ignored)"]
        ROOT --> CACHE["__pycache__/<br/>(ignored)"]
        ROOT --> WIP["wip_scripts/<br/>(ignored)"]
        ROOT --> PLOTS["plots/<br/>(ignored)"]
        ROOT --> VSCODE[".vscode/<br/>(ignored)"]
    end
    
    subgraph "Core Module Structure"
        DATASPEECH_DIR --> GPU_MODULES["GPU Enrichments<br/>pitch_apply, snr_apply, squim_apply"]
        DATASPEECH_DIR --> CPU_MODULES["CPU Enrichments<br/>rate_apply"]
        DATASPEECH_DIR --> UTILS["Utility Modules<br/>Filtering, Processing"]
    end
```

Sources: [.gitignore:1-6]()

### Code Entity Mapping

The development environment interacts with these key code entities:

| Directory/File | Primary Classes/Functions | Development Purpose |
|----------------|---------------------------|-------------------|
| `main.py` | Pipeline orchestration functions | Entry point debugging |
| `dataspeech/` | `*_apply` functions | Module development |
| `scripts/` | Processing scripts | Workflow automation |
| `*.json` | Configuration dictionaries | Parameter tuning |

## Development Environment Configuration

### Environment Variables and Paths

```mermaid
graph LR
    subgraph "Development Configuration"
        ENV_VAR["Environment Variables"] --> CACHE_DIR["HF_DATASETS_CACHE<br/>Dataset Caching"]
        ENV_VAR --> GPU_CONFIG["CUDA_VISIBLE_DEVICES<br/>GPU Selection"]
        ENV_VAR --> TRANSFORMERS_CACHE["TRANSFORMERS_CACHE<br/>Model Caching"]
    end
    
    subgraph "Development Paths"
        WORK_DIR["Working Directory"] --> DATA_PATH["./data/<br/>Local Datasets"]
        WORK_DIR --> OUTPUT_PATH["./output/<br/>Processing Results"]
        WORK_DIR --> ARTIFACTS_PATH["./artefacts/<br/>Build Artifacts"]
    end
    
    subgraph "Ignored Development Files"
        DEV_FILES["Development Files"] --> PYCACHE["__pycache__/"]
        DEV_FILES --> VSCODE_CONFIG[".vscode/"]
        DEV_FILES --> WIP_SCRIPTS["wip_scripts/"]
        DEV_FILES --> PLOT_OUTPUT["plots/"]
    end
```

Sources: [.gitignore:1-6]()

### GPU vs CPU Development Setup

The development environment must accommodate both GPU and CPU execution modes:

```mermaid
flowchart TD
    subgraph "Development Mode Detection"
        START["Development Environment Start"] --> GPU_CHECK{{"torch.cuda.is_available()"}}
        
        GPU_CHECK -->|True| GPU_DEV["GPU Development Mode"]
        GPU_CHECK -->|False| CPU_DEV["CPU Development Mode"]
    end
    
    subgraph "GPU Development Setup"
        GPU_DEV --> GPU_DEPS["GPU Dependencies<br/>• CUDA Toolkit<br/>• cuDNN<br/>• TensorRT (optional)"]
        GPU_DEV --> GPU_MODULES["GPU Module Development<br/>• pitch_apply<br/>• snr_apply<br/>• squim_apply"]
    end
    
    subgraph "CPU Development Setup"
        CPU_DEV --> CPU_DEPS["CPU Dependencies<br/>• OpenMP<br/>• BLAS Libraries"]
        CPU_DEV --> CPU_MODULES["CPU Module Development<br/>• rate_apply<br/>• Fallback implementations"]
    end
    
    subgraph "Shared Development Tools"
        SHARED["Shared Development Environment"] --> DEBUGGING["Debugging Tools<br/>• pdb, ipdb<br/>• VSCode debugger"]
        SHARED --> PROFILING["Profiling Tools<br/>• cProfile<br/>• py-spy"]
        SHARED --> TESTING["Testing Framework<br/>• pytest<br/>• unittest"]
    end
    
    GPU_MODULES --> SHARED
    CPU_MODULES --> SHARED
```

## Development Workflow

### Common Development Tasks

1. **Module Development**
   - Implement new enrichment functions in `dataspeech/`
   - Follow the `*_apply` naming convention
   - Ensure GPU/CPU compatibility

2. **Script Development**
   - Create processing scripts in `scripts/`
   - Use existing scripts as templates
   - Handle configuration management

3. **Configuration Updates**
   - Modify bin edge definitions
   - Update text classification mappings
   - Validate configuration consistency

### Development Testing Pattern

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant ENV as "Development Environment"
    participant GPU as "GPU/CPU Resources"
    participant DATA as "Test Dataset"
    
    DEV->>ENV: "Activate virtual environment"
    ENV->>GPU: "Check resource availability"
    GPU-->>ENV: "Return capability status"
    
    DEV->>ENV: "Load test configuration"
    ENV->>DATA: "Load minimal test dataset"
    DATA-->>ENV: "Return sample data"
    
    DEV->>ENV: "Run enrichment function"
    ENV->>GPU: "Execute processing"
    GPU-->>ENV: "Return results"
    
    ENV-->>DEV: "Display metrics and validation"
    
    Note over DEV,DATA: "Iterative development cycle"
```

### Debugging and Development Utilities

The development environment provides several debugging capabilities:

| Tool | Purpose | Usage Context |
|------|---------|---------------|
| `pdb.set_trace()` | Interactive debugging | Function-level debugging |
| VSCode debugger | Visual debugging | IDE-integrated development |
| `torch.profiler` | GPU performance profiling | Optimization work |
| Dataset sampling | Quick testing | Module validation |

Sources: [requirements.txt:1-8](), [.gitignore:1-6]()

## Development Best Practices

### Code Organization
- Follow the modular enrichment pattern
- Implement both GPU and CPU code paths
- Use configuration files for parameters
- Handle resource constraints gracefully

### Environment Management
- Use virtual environments consistently
- Pin dependency versions for reproducibility
- Test across GPU and CPU configurations
- Monitor resource usage during development

### Version Control
- Respect `.gitignore` patterns for development artifacts
- Keep work-in-progress scripts in `wip_scripts/`
- Commit configuration changes separately from code changes

This development setup supports the full dataspeech processing pipeline while providing the flexibility needed for research and development work.