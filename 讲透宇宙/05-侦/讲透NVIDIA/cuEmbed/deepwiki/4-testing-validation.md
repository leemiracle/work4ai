<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuEmbed · page 4 Testing & Validation · fetched 2026-10-26 -->

# Testing & Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/CMakeLists.txt](tests/CMakeLists.txt)

</details>



This document covers the comprehensive testing and validation strategy for cuEmbed, including correctness validation against CPU reference implementations, component-level unit testing, and performance benchmarking infrastructure. The testing system ensures both functional correctness and performance optimization across different GPU configurations and embedding scenarios.

For information about the core library components being tested, see [Core Library](#2). For PyTorch integration testing, see [PyTorch Integration](#3). For build system configuration, see [Build System](#5).

## Testing Architecture Overview

cuEmbed employs a multi-layered testing strategy that validates both correctness and performance across different dimensions:

### Testing Strategy Diagram

```mermaid
graph TB
    subgraph "Validation_Approach"
        CPU_REF["CPU Reference Implementations"]
        GPU_IMPL["GPU cuEmbed Implementations"] 
        TORCH_ALLCLOSE["torch.allclose Comparison"]
    end
    
    subgraph "Test_Categories"
        CORRECTNESS_TESTS["test_embedding_against_cpu.cu"]
        UNIT_TESTS["Component Unit Tests"]
        INTEGRATION_TESTS["PyTorch Integration Tests"]
        PERFORMANCE_TESTS["manual_benchmark.cu"]
    end
    
    subgraph "Test_Infrastructure"
        GTEST["Google Test Framework"]
        TEST_UTILS["Test Utilities & AllocationOptions"]
        DATA_GEN["PowerLaw Data Generation"]
        CMAKE_TESTS["tests/CMakeLists.txt"]
    end
    
    subgraph "Performance_Analysis"
        PARAM_SWEEP["sweep_parameters.sh"]
        CSV_OUTPUT["CSV Performance Data"]
        BENCHMARK_ANALYSIS["Performance Analysis Tools"]
    end
    
    CPU_REF --> TORCH_ALLCLOSE
    GPU_IMPL --> TORCH_ALLCLOSE
    TORCH_ALLCLOSE --> CORRECTNESS_TESTS
    
    CORRECTNESS_TESTS --> GTEST
    UNIT_TESTS --> GTEST
    INTEGRATION_TESTS --> GTEST
    
    PERFORMANCE_TESTS --> PARAM_SWEEP
    PARAM_SWEEP --> CSV_OUTPUT
    CSV_OUTPUT --> BENCHMARK_ANALYSIS
    
    TEST_UTILS --> CORRECTNESS_TESTS
    TEST_UTILS --> UNIT_TESTS
    DATA_GEN --> CORRECTNESS_TESTS
    CMAKE_TESTS --> GTEST
```

**Sources:** Diagrams from system analysis, [tests/CMakeLists.txt:1-38]()

## Test Categories

The testing framework encompasses several distinct categories, each serving specific validation purposes:

### Correctness Validation

The primary correctness validation compares GPU implementations against CPU reference implementations using `torch.allclose` for numerical precision verification. This ensures that the CUDA-accelerated operations produce mathematically equivalent results to their CPU counterparts.

Key test files:
- `test_embedding_against_cpu.cu` - Main GPU vs CPU validation suite
- Component-specific correctness tests for individual operations

### Unit Testing

Component-level unit tests validate individual classes and operations in isolation:
- `Addresser` class functionality
- `Combiner` operation modes (sum, mean, concat)
- `IndexLoader` data handling
- Forward and backward pass correctness
- Memory allocation and deallocation patterns

### Integration Testing

Integration tests validate the complete pipeline including:
- PyTorch tensor integration
- Autograd compatibility
- Multi-GPU scenarios
- Mixed-precision operations

### Performance Benchmarking

Performance tests measure execution time, memory usage, and throughput across different configurations:
- `manual_benchmark.cu` - Detailed performance measurement
- Parameter sweeping across embedding dimensions, batch sizes, and sparsity patterns
- GPU memory bandwidth utilization analysis

**Sources:** System analysis diagrams, testing strategy documentation

## Test Infrastructure

### Build System Integration

The test build system automatically discovers and compiles all test files:

```mermaid
graph LR
    subgraph "Test_Discovery"
        GLOB_CPP["file(GLOB test_source_files_cpp)"]
        GLOB_CU["file(GLOB test_source_files_cu)"]
        TEST_FILES["Combined test_source_files"]
    end
    
    subgraph "Test_Compilation"
        EXECUTABLE["add_executable(test_name)"]
        INCLUDES["target_include_directories"]
        LIBRARIES["target_link_libraries"]
    end
    
    subgraph "Dependencies"
        GTEST_LIB["gtest & gtest_main"]
        CUEMBED_HDRS["cuembed_hdrs"]
        CUDA_LIB["cuda"]
        UTILS_LIB["utils"]
        ABSEIL["absl::log & absl::check"]
    end
    
    subgraph "Output"
        BIN_DIR["PROJECT_BINARY_DIR/bin/test"]
        TEST_EXECUTABLES["Individual Test Executables"]
    end
    
    GLOB_CPP --> TEST_FILES
    GLOB_CU --> TEST_FILES
    TEST_FILES --> EXECUTABLE
    
    EXECUTABLE --> INCLUDES
    EXECUTABLE --> LIBRARIES
    
    GTEST_LIB --> LIBRARIES
    CUEMBED_HDRS --> LIBRARIES
    CUDA_LIB --> LIBRARIES
    UTILS_LIB --> LIBRARIES
    ABSEIL --> LIBRARIES
    
    LIBRARIES --> BIN_DIR
    BIN_DIR --> TEST_EXECUTABLES
```

**Sources:** [tests/CMakeLists.txt:16-37]()

### Test Framework Components

Each test executable is built with the following components:

| Component | Purpose | Linkage |
|-----------|---------|---------|
| `gtest` | Core testing framework | [tests/CMakeLists.txt:27-28]() |
| `gtest_main` | Test runner main function | [tests/CMakeLists.txt:27-28]() |
| `cuembed_hdrs` | cuEmbed header-only library | [tests/CMakeLists.txt:26]() |
| `cuda` | CUDA runtime libraries | [tests/CMakeLists.txt:29]() |
| `utils` | Test utility functions | [tests/CMakeLists.txt:30]() |
| `absl::log` | Abseil logging framework | [tests/CMakeLists.txt:31]() |
| `absl::check` | Abseil assertion macros | [tests/CMakeLists.txt:32]() |

**Sources:** [tests/CMakeLists.txt:24-32]()

## Validation Strategy

### CPU vs GPU Validation Flow

The core validation strategy compares GPU kernel outputs against CPU reference implementations:

```mermaid
graph TD
    subgraph "Input_Generation"
        EMBEDDING_TABLE["Embedding Table Parameters"]
        INDEX_DATA["Index Data (Fixed/CSR)"]
        WEIGHT_DATA["Optional Weight Data"]
        POWERLAW_GEN["PowerLaw Distribution Generator"]
    end
    
    subgraph "CPU_Reference"
        CPU_FORWARD["CPU EmbeddingForward"]
        CPU_BACKWARD["CPU EmbeddingBackward"] 
        CPU_RESULTS["CPU Reference Results"]
    end
    
    subgraph "GPU_Implementation"
        GPU_FORWARD["cuembed::EmbeddingForward"]
        GPU_BACKWARD["cuembed::EmbeddingBackward"]
        GPU_RESULTS["GPU Kernel Results"]
    end
    
    subgraph "Validation"
        TORCH_COMPARE["torch.allclose Comparison"]
        TOLERANCE_CHECK["Numerical Tolerance Validation"]
        PASS_FAIL["Pass/Fail Result"]
    end
    
    POWERLAW_GEN --> EMBEDDING_TABLE
    POWERLAW_GEN --> INDEX_DATA
    POWERLAW_GEN --> WEIGHT_DATA
    
    EMBEDDING_TABLE --> CPU_FORWARD
    INDEX_DATA --> CPU_FORWARD
    WEIGHT_DATA --> CPU_FORWARD
    CPU_FORWARD --> CPU_BACKWARD
    CPU_BACKWARD --> CPU_RESULTS
    
    EMBEDDING_TABLE --> GPU_FORWARD
    INDEX_DATA --> GPU_FORWARD
    WEIGHT_DATA --> GPU_FORWARD
    GPU_FORWARD --> GPU_BACKWARD
    GPU_BACKWARD --> GPU_RESULTS
    
    CPU_RESULTS --> TORCH_COMPARE
    GPU_RESULTS --> TORCH_COMPARE
    TORCH_COMPARE --> TOLERANCE_CHECK
    TOLERANCE_CHECK --> PASS_FAIL
```

**Sources:** System analysis, correctness testing strategy

### Test Data Generation

Test data generation utilizes realistic distribution patterns:

- **PowerLaw Distribution**: Simulates real-world embedding access patterns with high-frequency and long-tail items
- **Configurable Parameters**: Embedding dimensions, batch sizes, sparsity levels
- **AllocationOptions**: Memory allocation testing across different GPU memory configurations
- **Edge Cases**: Empty batches, maximum dimension sizes, boundary conditions

**Sources:** Data generation utilities from system analysis

## Performance Benchmarking

### Benchmark Execution Pipeline

```mermaid
graph LR
    subgraph "Benchmark_Setup"
        MANUAL_BENCHMARK["manual_benchmark.cu"]
        PARAM_CONFIG["Parameter Configurations"]
        GPU_SETUP["GPU Environment Setup"]
    end
    
    subgraph "Parameter_Sweeping"
        SWEEP_SCRIPT["sweep_parameters.sh"]
        BATCH_SIZES["Batch Size Sweep"]
        EMBED_DIMS["Embedding Dimension Sweep"]
        SPARSITY_LEVELS["Sparsity Level Sweep"]
    end
    
    subgraph "Performance_Metrics"
        EXECUTION_TIME["Kernel Execution Time"]
        MEMORY_BANDWIDTH["Memory Bandwidth Utilization"]
        THROUGHPUT["Operations Per Second"]
    end
    
    subgraph "Output_Analysis"
        CSV_DATA["CSV Performance Data"]
        PERFORMANCE_ANALYSIS["Analysis Tools"]
        OPTIMIZATION_INSIGHTS["Optimization Recommendations"]
    end
    
    MANUAL_BENCHMARK --> PARAM_CONFIG
    PARAM_CONFIG --> GPU_SETUP
    GPU_SETUP --> SWEEP_SCRIPT
    
    SWEEP_SCRIPT --> BATCH_SIZES
    SWEEP_SCRIPT --> EMBED_DIMS  
    SWEEP_SCRIPT --> SPARSITY_LEVELS
    
    BATCH_SIZES --> EXECUTION_TIME
    EMBED_DIMS --> MEMORY_BANDWIDTH
    SPARSITY_LEVELS --> THROUGHPUT
    
    EXECUTION_TIME --> CSV_DATA
    MEMORY_BANDWIDTH --> CSV_DATA
    THROUGHPUT --> CSV_DATA
    CSV_DATA --> PERFORMANCE_ANALYSIS
    PERFORMANCE_ANALYSIS --> OPTIMIZATION_INSIGHTS
```

**Sources:** Performance testing infrastructure from system analysis

The benchmarking system provides comprehensive performance analysis across multiple dimensions, enabling optimization decisions based on quantitative measurements of GPU kernel efficiency and memory utilization patterns.

---

