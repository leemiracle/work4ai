<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvbandwidth · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [common.h](common.h)
- [nvbandwidth.cpp](nvbandwidth.cpp)

</details>



This document outlines the high-level architecture of nvbandwidth, explaining the major components and their relationships within the system. For specific implementation details about the Memory Copy Framework, see [Memory Copy Framework](#3).

## Overview

nvbandwidth is a CUDA-based tool designed to measure memory bandwidth and latency performance between different components in NVIDIA GPU systems. The architecture follows a modular design that separates test definition, memory operations, and result reporting into distinct subsystems.

```mermaid
graph TD
    CLI["CLI Interface"]
    TestCases["Test Case Framework"]
    MemCopyFW["Memory Copy Framework"]
    CUDAKernels["CUDA Kernels"]
    OutputSystem["Output System"]
    
    CLI --> TestCases
    CLI --> OutputSystem
    TestCases --> MemCopyFW
    MemCopyFW --> CUDAKernels
    OutputSystem --> CLI
```

Sources: [nvbandwidth.cpp:178-325](), [CMakeLists.txt:40-52]()

## Core Components

### CLI Interface

The CLI Interface serves as the entry point for nvbandwidth, handling user inputs and orchestrating test execution. It parses command-line arguments using Boost's program_options library, discovers available tests, and dispatches selected test cases.

Key responsibilities:
- Parsing command-line options
- Test case discovery and filtering
- Test execution orchestration
- Result collection and output formatting

```mermaid
flowchart LR
    A["Program Start"] --> B["Parse Arguments"]
    B --> C{"Help/List\nRequested?"}
    C -->|"Yes"| D["Show Info & Exit"]
    C -->|"No"| E["Initialize CUDA/NVML"]
    E --> F["Load Test Cases"]
    F --> G["Preload Kernels"]
    G --> H["Run Selected Tests"]
    H --> I["Format & Output Results"]
```

Sources: [nvbandwidth.cpp:178-325]()

### Test Case Framework

The Test Case Framework provides a standard interface for defining different bandwidth and latency tests. It uses an inheritance-based design with a base `Testcase` class that defines the common interface and specialized derived classes for specific test scenarios.

```mermaid
classDiagram
    class Testcase {
        <<abstract>>
        +run(size_t, unsigned long long)
        +filter() bool
        +testKey() string
        +testDesc() string
    }
    
    class CETests {
        +HostToDeviceCE
        +DeviceToHostCE
        +DeviceToDeviceCE
        +BidirectionalCE
    }
    
    class SMTests {
        +HostToDeviceSM
        +DeviceToHostSM
        +DeviceToDeviceSM
        +BidirectionalSM
    }
    
    class MultinodeTests {
        +MultinodeDeviceToDeviceCE
        +MultinodeDeviceToDeviceSM
    }
    
    Testcase <|-- CETests
    Testcase <|-- SMTests
    Testcase <|-- MultinodeTests
```

Each test case implements:
- `run()`: Executes the test with specified buffer size and iteration count
- `filter()`: Determines if the test is applicable for the current hardware
- `testKey()`: Returns a unique identifier for the test
- `testDesc()`: Returns a human-readable description

Sources: [nvbandwidth.cpp:64-117]()

### Memory Copy Framework

The Memory Copy Framework is the core engine that performs memory operations. It abstracts the complexities of buffer management and memory transfers across different hardware components.

Key components:
- **MemcpyBuffer**: Abstract base class for different memory buffer types
- **MemcpyInitiator**: Interface for different memory copy strategies
- **MemcpyOperation**: Coordinates memory transfers between buffers

```mermaid
classDiagram
    class MemcpyBuffer {
        <<abstract>>
        +getBuffer() CUdeviceptr
        +getBufferSize() size_t
        +getBufferIdx() int
    }
    
    class HostBuffer {
        +HostBuffer(size_t, int)
    }
    
    class DeviceBuffer {
        +DeviceBuffer(size_t, int)
    }
    
    class MemcpyInitiator {
        <<interface>>
        +memcpyFunc(MemcpyDescriptor&)
        +getAdjustedCopySize(size_t)
    }
    
    class MemcpyOperation {
        +doMemcpy(MemcpyBuffer&, MemcpyBuffer&) double
    }
    
    MemcpyBuffer <|-- HostBuffer
    MemcpyBuffer <|-- DeviceBuffer
    MemcpyOperation --> MemcpyInitiator
    MemcpyOperation --> MemcpyBuffer
```

For more details on the Memory Copy Framework, see [Memory Copy Framework](#3).

Sources: [common.h:240-249]()

### CUDA Kernels

The CUDA Kernels component includes specialized CUDA kernels for performing memory operations using different strategies:

- **CE (Copy Engine)**: Uses CUDA's built-in asynchronous memory copy functions
- **SM (Streaming Multiprocessor)**: Uses custom CUDA kernels to perform copies through the SM

```mermaid
graph TD
    subgraph "CUDA Kernels"
        CopyEngine["CE-based\nCopy Functions"]
        SMKernels["SM-based\nCopy Kernels"]
        LatencyKernels["Latency\nMeasurement Kernels"]
    end
    
    MemCopy["MemcpyInitiator"] --> CopyEngine
    MemCopy --> SMKernels
    MemCopy --> LatencyKernels
```

Sources: [CMakeLists.txt:40-52]()

### Output System

The Output System is responsible for formatting and presenting test results. It supports multiple output formats, including plain text and JSON.

```mermaid
classDiagram
    class Output {
        +addTestcase(id, status)
        +addVersionInfo()
        +recordError(message)
        +print()
    }
    
    class JsonOutput {
        +addTestcase(id, status)
        +print()
    }
    
    Output <|-- JsonOutput
```

Sources: [nvbandwidth.cpp:181-250]()

## Data Flow

The overall data flow within nvbandwidth follows this pattern:

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant TestCase
    participant MemcpyOperation
    participant CUDA
    
    User->>CLI: Run command with options
    CLI->>TestCase: Create and configure tests
    TestCase->>MemcpyOperation: Configure memory buffers
    MemcpyOperation->>CUDA: Allocate memory
    loop For each iteration
        TestCase->>MemcpyOperation: Perform memory copy
        MemcpyOperation->>CUDA: Execute kernel/memory copy
        CUDA-->>MemcpyOperation: Complete operation
        MemcpyOperation-->>TestCase: Return timing results
    end
    TestCase-->>CLI: Report test results
    CLI-->>User: Display formatted output
```

Sources: [nvbandwidth.cpp:149-176]()

## Test Types and Memory Paths

nvbandwidth includes multiple test types to measure bandwidth across different memory paths:

| Test Category | Description | Implementation Methods |
|---------------|-------------|------------------------|
| Host to Device | Measures bandwidth from CPU memory to GPU memory | CE, SM |
| Device to Host | Measures bandwidth from GPU memory to CPU memory | CE, SM |
| Device to Device | Measures bandwidth between memories on same GPU | CE, SM |
| Bidirectional | Measures concurrent copy bandwidth in both directions | CE, SM |
| All to One | Measures bandwidth when all GPUs copy to one GPU | CE, SM |
| One to All | Measures bandwidth when one GPU copies to all GPUs | CE, SM |
| All to Host | Measures bandwidth when all GPUs copy to host | CE, SM |
| Host to All | Measures bandwidth when host copies to all GPUs | CE, SM |
| Latency | Measures memory access latency rather than bandwidth | SM |
| Multinode | Measures bandwidth across node boundaries (when built with MPI) | CE, SM |

Sources: [nvbandwidth.cpp:64-117]()

## Execution Model

nvbandwidth follows a straightforward execution model:

1. **Initialization**: Parse command-line arguments, initialize CUDA, and discover available GPUs
2. **Test Selection**: Select test cases to run based on user input
3. **Kernel Preloading**: Preload CUDA kernels on all devices to avoid synchronization issues
4. **Test Execution**: Run each selected test case
5. **Result Collection**: Gather performance results from all tests
6. **Result Presentation**: Format and display results according to the selected output format

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> SelectTests
    SelectTests --> PreloadKernels
    PreloadKernels --> ExecuteTests
    ExecuteTests --> CollectResults
    CollectResults --> PresentResults
    PresentResults --> [*]
```

Sources: [nvbandwidth.cpp:178-325]()

## Design Patterns

The nvbandwidth architecture implements several design patterns:

1. **Strategy Pattern**: Through the `MemcpyInitiator` interface, which allows different memory copy strategies to be implemented and used interchangeably.

2. **Template Method Pattern**: Through the `Testcase` base class, which defines the structure of a test while allowing derived classes to implement specific behaviors.

3. **Factory Method Pattern**: Through the `createTestcases()` function, which creates and returns a collection of test case objects.

4. **Command Pattern**: Each test case encapsulates a specific bandwidth measurement operation that can be executed on demand.

5. **Adapter Pattern**: The output system adapts internal data structures into different output formats (plain text and JSON).

Sources: [nvbandwidth.cpp:64-117](), [nvbandwidth.cpp:178-325]()

## Multi-node Support

When built with MPI support, nvbandwidth includes additional test cases for measuring bandwidth across node boundaries. This functionality uses MPI for process coordination and adds specialized buffer and test case implementations for multi-node scenarios.

```mermaid
graph TD
    subgraph "Single-Node Components"
        SingleTests["Single-Node Tests"]
        LocalBuffers["Local Memory Buffers"]
    end
    
    subgraph "Multi-Node Components"
        MultiTests["Multi-Node Tests"]
        MultiBuffers["Multi-Node Memory Buffers"]
        MPI["MPI Communication Layer"]
    end
    
    SingleTests --> LocalBuffers
    MultiTests --> MultiBuffers
    MultiTests --> MPI
    MultiBuffers --> MPI
```

Sources: [nvbandwidth.cpp:100-115](), [CMakeLists.txt:72-77]()

## System Integration Points

nvbandwidth integrates with several external systems:

1. **CUDA Driver API**: For low-level GPU control and memory management
2. **CUDA Runtime API**: For higher-level CUDA operations
3. **NVML (NVIDIA Management Library)**: For GPU device information and statistics
4. **Boost Program Options**: For command-line argument parsing
5. **MPI (optional)**: For multi-node support

Sources: [nvbandwidth.cpp:18-32](), [CMakeLists.txt:18-77]()

---

