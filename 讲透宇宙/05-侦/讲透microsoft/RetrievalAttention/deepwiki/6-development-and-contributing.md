<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RetrievalAttention · page 6 Development and Contributing · fetched 2026-10-26 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SUPPORT.md](SUPPORT.md)

</details>



This document provides guidance for developers who want to contribute to the RetroInfer project. It covers the development workflow, project structure, testing procedures, and contribution guidelines. 

For information about getting help and reporting issues, see [Getting Support](#6.1). For security-related concerns, see [Security](#6.2). For community guidelines and behavioral expectations, see [Code of Conduct](#6.3).

## Development Workflow

The RetroInfer project follows a structured development workflow that integrates testing, benchmarking, and deployment considerations. The development process centers around the core attention mechanisms and their integration with various model architectures.

### Development Environment Pipeline

```mermaid
graph TD
    DEV_ENV["Development Environment Setup"]
    DOCKER_BUILD["Docker Container Build"]
    CONDA_SETUP["Conda Environment Creation"]
    DEPS_INSTALL["Dependencies Installation"]
    KERNEL_BUILD["RetroInfer Kernel Compilation"]
    
    DEV_ENV --> DOCKER_BUILD
    DOCKER_BUILD --> CONDA_SETUP
    CONDA_SETUP --> DEPS_INSTALL
    DEPS_INSTALL --> KERNEL_BUILD
    
    subgraph "Testing Pipeline"
        SIMPLE_TEST["Simple Test Execution"]
        RULER_TEST["RULER Benchmark"]
        LONGBENCH_TEST["LongBench Evaluation"]
        THROUGHPUT_TEST["Throughput Testing"]
    end
    
    KERNEL_BUILD --> SIMPLE_TEST
    SIMPLE_TEST --> RULER_TEST
    SIMPLE_TEST --> LONGBENCH_TEST
    SIMPLE_TEST --> THROUGHPUT_TEST
    
    subgraph "Validation Gates"
        ACCURACY_CHECK["Accuracy Validation"]
        PERFORMANCE_CHECK["Performance Validation"]
        MEMORY_CHECK["Memory Usage Validation"]
    end
    
    RULER_TEST --> ACCURACY_CHECK
    LONGBENCH_TEST --> ACCURACY_CHECK
    THROUGHPUT_TEST --> PERFORMANCE_CHECK
    THROUGHPUT_TEST --> MEMORY_CHECK
```

**Sources:** README.md, development environment setup procedures

### Key Development Components

The development workflow involves several critical components that contributors should understand:

| Component | Location | Purpose |
|-----------|----------|---------|
| Attention Hub | `attention_hub/` | Core attention mechanism implementations |
| Wave Index | RetroInfer kernels | Attention-aware vector indexing |
| Wave Buffer | RetroInfer kernels | GPU-CPU coordination and overlap |
| Benchmarking | `benchmark/` | Performance evaluation and validation |
| Configuration | `benchmark/config.py` | System configuration management |

## Project Structure for Contributors

Understanding the codebase structure is essential for effective contribution. The project is organized around core attention mechanisms, benchmarking systems, and configuration management.

### Core Code Entity Architecture

```mermaid
graph TB
    subgraph "Attention Implementation Layer"
        ATTN_HUB["attention_hub/__init__.py"]
        FLASH_ATTN["flash_attn_with_kvcache()"]
        RETRO_ATTN["retroinfer_cache()"]
        PREFILL_DECODE["prefill/decode functions"]
    end
    
    subgraph "Model Integration Layer"
        LLAMA_MODEL["LlamaModel integration"]
        QWEN_MODEL["QwenModel integration"]
        MODEL_DISPATCH["model dispatch logic"]
    end
    
    subgraph "Benchmark System Layer"
        RULER_EVAL["benchmark/ruler/eval.py"]
        LONGBENCH_PRED["benchmark/longbench/pred.py"]
        THROUGHPUT_EVAL["benchmark/throughput/"]
        CONFIG_GEN["benchmark/config.py::generate_config()"]
    end
    
    subgraph "Configuration Management Layer"
        MODEL2PATH["model2path.json"]
        MODEL2MAXLEN["model2maxlen.json"]
        DATASET2PROMPT["dataset2prompt.json"]
        DATASET2MAXLEN["dataset2maxlen.json"]
    end
    
    ATTN_HUB --> FLASH_ATTN
    ATTN_HUB --> RETRO_ATTN
    FLASH_ATTN --> PREFILL_DECODE
    RETRO_ATTN --> PREFILL_DECODE
    
    PREFILL_DECODE --> LLAMA_MODEL
    PREFILL_DECODE --> QWEN_MODEL
    MODEL_DISPATCH --> LLAMA_MODEL
    MODEL_DISPATCH --> QWEN_MODEL
    
    CONFIG_GEN --> MODEL2PATH
    CONFIG_GEN --> MODEL2MAXLEN
    CONFIG_GEN --> DATASET2PROMPT
    CONFIG_GEN --> DATASET2MAXLEN
    
    RULER_EVAL --> CONFIG_GEN
    LONGBENCH_PRED --> CONFIG_GEN
    THROUGHPUT_EVAL --> CONFIG_GEN
```

**Sources:** attention_hub structure, benchmark/config.py, benchmark/ruler/eval.py, benchmark/longbench/pred.py

### Critical Code Paths for Contributors

Contributors should focus on these key areas when making modifications:

1. **Attention Mechanisms**: The `attention_hub/` directory contains the core attention implementations that interface with `flash_attn_with_kvcache()` and `retroinfer_cache()` functions.

2. **Benchmarking Scripts**: The `benchmark/` directory structure includes evaluation scripts that call specific functions like `generate_config()` in [benchmark/config.py]().

3. **Model Configuration**: JSON configuration files managed through [benchmark/config.py]() that define model paths, maximum lengths, and dataset prompts.

4. **Evaluation Pipelines**: Scripts in [benchmark/ruler/eval.py]() and [benchmark/longbench/pred.py]() that orchestrate the testing process.

## Testing and Validation Process

The RetroInfer project employs a comprehensive testing strategy that validates both correctness and performance across multiple dimensions.

### Testing Pipeline Architecture

```mermaid
graph LR
    subgraph "Unit Testing Layer"
        SIMPLE_TEST["Simple Test Scripts"]
        ATTENTION_TEST["Attention Mechanism Tests"]
        CACHE_TEST["KV Cache Validation"]
    end
    
    subgraph "Integration Testing Layer"
        RULER_TASKS["RULER Task Execution"]
        LONGBENCH_TASKS["LongBench Task Execution"]
        MODEL_INTEGRATION["Model Integration Tests"]
    end
    
    subgraph "Performance Testing Layer"
        THROUGHPUT_BENCH["Throughput Benchmarks"]
        MEMORY_PROFILE["Memory Usage Profiling"]
        ACCURACY_VALIDATION["Accuracy Validation"]
    end
    
    subgraph "Validation Metrics"
        ACCURACY_SCORE["Accuracy Score Generation"]
        SPEED_METRICS["Speed Improvement Metrics"]
        MEMORY_METRICS["Memory Usage Metrics"]
    end
    
    SIMPLE_TEST --> RULER_TASKS
    ATTENTION_TEST --> RULER_TASKS
    CACHE_TEST --> RULER_TASKS
    
    RULER_TASKS --> THROUGHPUT_BENCH
    LONGBENCH_TASKS --> THROUGHPUT_BENCH
    MODEL_INTEGRATION --> THROUGHPUT_BENCH
    
    THROUGHPUT_BENCH --> ACCURACY_SCORE
    MEMORY_PROFILE --> MEMORY_METRICS
    ACCURACY_VALIDATION --> ACCURACY_SCORE
    
    ACCURACY_SCORE --> SPEED_METRICS
    SPEED_METRICS --> MEMORY_METRICS
```

**Sources:** README.md testing procedures, benchmark/ruler/eval.py, benchmark/longbench/pred.py

### Test Execution Framework

The testing process follows a structured approach:

1. **Simple Testing**: Execute basic functionality tests with 4 batch size and 120K tokens to verify core operations.

2. **RULER Benchmark**: Run synthetic task evaluation using [benchmark/ruler/eval.py]() with tasks defined in `constants.py`.

3. **LongBench Evaluation**: Execute real-world task evaluation through [benchmark/longbench/pred.py]() and [benchmark/longbench/eval.py]().

4. **Throughput Testing**: Measure performance improvements using multi-GPU configurations and NUMA-aware settings.

### Validation Criteria

Contributors should ensure their changes meet these validation criteria:

| Metric | Baseline | Target | Test Command |
|--------|----------|---------|-------------|
| Accuracy | Flash Attention baseline | ≥99% of baseline | RULER + LongBench evaluation |
| Throughput | Flash Attention baseline | 4.5x-10.5x improvement | Throughput benchmarks |
| Memory Usage | Variable by model | GPU ~25GB, CPU ~67GB | Memory profiling |

## Contributing Guidelines

### Code Contribution Process

1. **Fork and Branch**: Create a feature branch from the main repository
2. **Development**: Implement changes following the existing code patterns
3. **Testing**: Run the full test suite including RULER and LongBench evaluations
4. **Documentation**: Update relevant documentation and code comments
5. **Pull Request**: Submit PR with detailed description of changes

### Code Quality Standards

- Follow existing code organization patterns in `attention_hub/` and `benchmark/`
- Maintain compatibility with existing configuration files in [benchmark/config.py]()
- Ensure all attention mechanism changes preserve the interface contracts
- Include appropriate error handling and logging

### Documentation Requirements

- Update README.md for significant feature additions
- Maintain inline code documentation for complex attention mechanisms
- Update configuration documentation for new model or dataset support
- Provide examples for new benchmarking capabilities

**Sources:** [SUPPORT.md:1-14](), [CODE_OF_CONDUCT.md:1-10]()

## Support and Community

The RetroInfer project provides multiple channels for developer support and community engagement.

### Issue Tracking and Support

The project uses GitHub Issues for bug tracking and feature requests. Before filing new issues, contributors should search existing issues to avoid duplicates as outlined in [SUPPORT.md:5-7](). For help with using the project, refer to the main documentation in README.md.

### Community Guidelines

This project follows the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct) as specified in [CODE_OF_CONDUCT.md:3](). Contributors should familiarize themselves with these guidelines and direct questions to [opencode@microsoft.com](mailto:opencode@microsoft.com) as needed.

### Development Support Resources

- **Documentation**: Primary reference in README.md for setup and usage
- **Issue Tracking**: GitHub Issues for bugs and feature requests  
- **Code of Conduct**: Microsoft Open Source Code of Conduct for community guidelines
- **Security**: Dedicated security policy for vulnerability reporting

**Sources:** [SUPPORT.md:1-14](), [CODE_OF_CONDUCT.md:1-10]()

---

