<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/EdgeML · page 6 Development Setup · fetched 2026-10-26 -->

# Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [c_reference/include/quantized_datatypes.h](c_reference/include/quantized_datatypes.h)
- [c_reference/src/Makefile](c_reference/src/Makefile)
- [c_reference/tests/Makefile](c_reference/tests/Makefile)
- [c_reference/tests/fastgrnn/test_quantized_fastgrnn.c](c_reference/tests/fastgrnn/test_quantized_fastgrnn.c)
- [c_reference/tests/mbconv/q_wider_regression_model/mbconv.h](c_reference/tests/mbconv/q_wider_regression_model/mbconv.h)
- [c_reference/tests/mbconv/test_quantized_mbconv.c](c_reference/tests/mbconv/test_quantized_mbconv.c)
- [pytorch/requirements-cpu.txt](pytorch/requirements-cpu.txt)
- [pytorch/requirements-gpu.txt](pytorch/requirements-gpu.txt)
- [tf/requirements-cpu.txt](tf/requirements-cpu.txt)

</details>



This document provides instructions for setting up a development environment for EdgeML, including installing dependencies, building components, and validating installations across all supported frameworks (TensorFlow, PyTorch, and C/C++).

For detailed requirements and installation procedures, see [Requirements and Installation](#6.1). For comprehensive building and testing instructions, see [Building and Testing](#6.2).

## Development Environment Overview

EdgeML supports multiple implementation frameworks, each with specific requirements and build processes. The development setup varies depending on which components you plan to use.

```mermaid
graph TB
    subgraph "EdgeML Development Environment"
        DEV["Developer Machine"]
        
        subgraph "Python Environments"
            TF_ENV["TensorFlow Environment"]
            PT_ENV["PyTorch Environment"]
        end
        
        subgraph "Build Tools"
            GCC["GCC Compiler"]
            MAKE["GNU Make"]
            CUDA["CUDA Toolkit (Optional)"]
        end
        
        subgraph "Framework Requirements"
            TF_REQ["tf/requirements-cpu.txt"]
            PT_CPU["pytorch/requirements-cpu.txt"]
            PT_GPU["pytorch/requirements-gpu.txt"]
        end
        
        subgraph "C Reference Build System"
            CONFIG["c_reference/config.mk"]
            SRC_MAKE["c_reference/src/Makefile"]
            TEST_MAKE["c_reference/tests/Makefile"]
        end
        
        subgraph "Validation Tests"
            TF_TESTS["TensorFlow Training Scripts"]
            PT_TESTS["PyTorch Training Scripts"]
            C_TESTS["C Reference Test Binaries"]
        end
    end
    
    DEV --> TF_ENV
    DEV --> PT_ENV
    DEV --> GCC
    DEV --> MAKE
    
    TF_ENV --> TF_REQ
    PT_ENV --> PT_CPU
    PT_ENV --> PT_GPU
    
    GCC --> CONFIG
    MAKE --> SRC_MAKE
    MAKE --> TEST_MAKE
    
    TF_ENV --> TF_TESTS
    PT_ENV --> PT_TESTS
    CONFIG --> C_TESTS
```

**Sources:** [tf/requirements-cpu.txt:1-12](), [pytorch/requirements-cpu.txt:1-10](), [pytorch/requirements-gpu.txt:1-10](), [c_reference/tests/Makefile:1-48](), [c_reference/src/Makefile:1-42]()

## Framework Requirements Summary

EdgeML supports development across three main frameworks, each with distinct dependency requirements:

| Framework | Python Version | Key Dependencies | GPU Support |
|-----------|----------------|------------------|-------------|
| TensorFlow | Python 3.6+ | `tensorflow==1.15.4`, `numpy==1.16.4` | CPU/GPU |
| PyTorch | Python 3.6+ | `torch==1.4.0`, `torchvision==0.5.0` | CPU/GPU |
| C Reference | N/A | GCC, GNU Make | N/A |

**Common Dependencies:**
- `numpy==1.16.4`
- `scipy==1.3.0`
- `scikit-learn==0.21.2`
- `pandas==0.23.4`
- `jupyter==1.0.0`

**Additional Tools:**
- `antlr4-python3-runtime==4.7` (for SeeDot quantization)
- `onnx==1.8.0` (for model export)
- `bokeh==2.1.1` (for visualization)
- `tqdm==4.56.0` (for progress bars)

**Sources:** [tf/requirements-cpu.txt:1-12](), [pytorch/requirements-cpu.txt:1-10](), [pytorch/requirements-gpu.txt:1-10]()

## C Reference Build System Architecture

The C reference implementation uses a hierarchical Makefile-based build system for compiling quantized inference code and validation tests.

```mermaid
graph TD
    subgraph "C Reference Build System"
        CONFIG["c_reference/config.mk<br/>Build Configuration"]
        
        subgraph "Source Build"
            SRC_MAKE["c_reference/src/Makefile"]
            SRC_TARGETS["Source Targets"]
            
            UTILS_O["utils.o"]
            FASTGRNN_O["fastgrnn.o"]
            CLASSIFIER_O["classifier.o"]
            RNNPOOL_O["rnnpool.o"]
            Q_UTILS_O["quantized_utils.o"]
            Q_FASTGRNN_O["quantized_fastgrnn.o"]
            Q_RNNPOOL_O["quantized_rnnpool.o"]
            Q_MBCONV_O["quantized_mbconv.o"]
        end
        
        subgraph "Test Build"
            TEST_MAKE["c_reference/tests/Makefile"]
            TEST_TARGETS["Test Targets"]
            
            TEST_FASTGRNN["test_fastgrnn_lr"]
            TEST_RNNPOOL["test_rnnpool"]
            TEST_Q_UTILS["test_quantized_utils"]
            TEST_Q_FASTGRNN["test_quantized_fastgrnn"]
            TEST_Q_RNNPOOL["test_quantized_rnnpool"]
            TEST_Q_MBCONV["test_quantized_mbconv"]
            TEST_FACE["test_quantized_face_detection"]
        end
        
        subgraph "Data Types"
            DATATYPES["c_reference/include/quantized_datatypes.h"]
            Q7_T["Q7_T: int8_t"]
            Q15_T["Q15_T: int16_t"]
            SCALE_T["SCALE_T: int32_t"]
            ITER_T["ITER_T: uint32_t"]
        end
    end
    
    CONFIG --> SRC_MAKE
    CONFIG --> TEST_MAKE
    
    SRC_MAKE --> SRC_TARGETS
    SRC_TARGETS --> UTILS_O
    SRC_TARGETS --> FASTGRNN_O
    SRC_TARGETS --> CLASSIFIER_O
    SRC_TARGETS --> RNNPOOL_O
    SRC_TARGETS --> Q_UTILS_O
    SRC_TARGETS --> Q_FASTGRNN_O
    SRC_TARGETS --> Q_RNNPOOL_O
    SRC_TARGETS --> Q_MBCONV_O
    
    TEST_MAKE --> TEST_TARGETS
    TEST_TARGETS --> TEST_FASTGRNN
    TEST_TARGETS --> TEST_RNNPOOL
    TEST_TARGETS --> TEST_Q_UTILS
    TEST_TARGETS --> TEST_Q_FASTGRNN
    TEST_TARGETS --> TEST_Q_RNNPOOL
    TEST_TARGETS --> TEST_Q_MBCONV
    TEST_TARGETS --> TEST_FACE
    
    DATATYPES --> Q7_T
    DATATYPES --> Q15_T
    DATATYPES --> SCALE_T
    DATATYPES --> ITER_T
    
    Q_UTILS_O --> TEST_Q_FASTGRNN
    Q_FASTGRNN_O --> TEST_Q_FASTGRNN
    Q_UTILS_O --> TEST_Q_RNNPOOL
    Q_RNNPOOL_O --> TEST_Q_RNNPOOL
    Q_UTILS_O --> TEST_Q_MBCONV
    Q_MBCONV_O --> TEST_Q_MBCONV
```

**Sources:** [c_reference/tests/Makefile:1-48](), [c_reference/src/Makefile:1-42](), [c_reference/include/quantized_datatypes.h:1-26]()

## Installation and Validation Workflow

The development setup follows a structured workflow from environment preparation through validation testing.

```mermaid
flowchart TD
    START["Development Setup Start"]
    
    subgraph "Environment Setup"
        CHOOSE["Choose Framework(s)"]
        TF_SETUP["Install TensorFlow Environment<br/>pip install -r tf/requirements-cpu.txt"]
        PT_SETUP["Install PyTorch Environment<br/>pip install -r pytorch/requirements-cpu.txt"]
        C_SETUP["Install Build Tools<br/>GCC, GNU Make"]
    end
    
    subgraph "Build Components"
        BUILD_C["Build C Reference<br/>make -C c_reference/src"]
        BUILD_TESTS["Build Test Suite<br/>make -C c_reference/tests"]
    end
    
    subgraph "Validation"
        RUN_TF["Run TensorFlow Examples<br/>tf/examples/"]
        RUN_PT["Run PyTorch Examples<br/>pytorch/examples/"]
        RUN_C_TESTS["Run C Reference Tests<br/>./test_quantized_fastgrnn"]
        VALIDATE["Validation Complete"]
    end
    
    START --> CHOOSE
    CHOOSE --> TF_SETUP
    CHOOSE --> PT_SETUP
    CHOOSE --> C_SETUP
    
    TF_SETUP --> RUN_TF
    PT_SETUP --> RUN_PT
    C_SETUP --> BUILD_C
    
    BUILD_C --> BUILD_TESTS
    BUILD_TESTS --> RUN_C_TESTS
    
    RUN_TF --> VALIDATE
    RUN_PT --> VALIDATE
    RUN_C_TESTS --> VALIDATE
    
    subgraph "Test Examples"
        TF_EXAMPLE["test_quantized_fastgrnn.c<br/>Validates quantized FastGRNN"]
        MBCONV_EXAMPLE["test_quantized_mbconv.c<br/>Validates MBConv operations"]
        FACE_EXAMPLE["Face detection tests<br/>Complete application validation"]
    end
    
    RUN_C_TESTS --> TF_EXAMPLE
    RUN_C_TESTS --> MBCONV_EXAMPLE
    RUN_C_TESTS --> FACE_EXAMPLE
```

**Sources:** [c_reference/tests/fastgrnn/test_quantized_fastgrnn.c:1-39](), [c_reference/tests/mbconv/test_quantized_mbconv.c:1-202]()

## Key Build Targets and Commands

The C reference implementation provides several important build targets for development and testing:

### Source Compilation Targets

```bash
# Build all source objects
make -C c_reference/src all

# Individual targets
make -C c_reference/src utils.o fastgrnn.o classifier.o rnnpool.o
make -C c_reference/src quantized_utils.o quantized_fastgrnn.o quantized_rnnpool.o quantized_mbconv.o
```

### Test Compilation Targets

```bash
# Build all tests
make -C c_reference/tests all

# Specific algorithm tests
make -C c_reference/tests test_fastgrnn_lr test_rnnpool
make -C c_reference/tests test_quantized_fastgrnn test_quantized_rnnpool test_quantized_mbconv

# Application tests
make -C c_reference/tests test_quantized_face_detection
```

### Quantized Data Types

The C reference implementation defines specific data types for quantized operations in [c_reference/include/quantized_datatypes.h:10-24]():

- `Q7_T`: `int8_t` for 8-bit quantized values
- `Q15_T`: `int16_t` for 16-bit quantized values  
- `SCALE_T`: `int32_t` for scaling operations
- `ITER_T`: `uint32_t` for iteration counters

**Sources:** [c_reference/tests/Makefile:11-39](), [c_reference/src/Makefile:9-33](), [c_reference/include/quantized_datatypes.h:10-24]()

## Next Steps

For detailed installation procedures and dependency management, see [Requirements and Installation](#6.1).

For comprehensive build instructions, testing procedures, and troubleshooting, see [Building and Testing](#6.2).

---

