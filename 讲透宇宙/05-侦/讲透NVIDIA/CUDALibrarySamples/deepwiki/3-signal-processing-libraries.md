<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/CUDALibrarySamples · page 3 Signal Processing Libraries · fetched 2026-10-26 -->

# Signal Processing Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/README.md](cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/README.md)
- [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu](cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu)
- [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/README.md](cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/README.md)
- [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu](cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu)
- [cuFFTMp/samples/reshape/cufftmp_reshape.cu](cuFFTMp/samples/reshape/cufftmp_reshape.cu)
- [cuSOLVERSp2cuDSS/CMakeLists.txt](cuSOLVERSp2cuDSS/CMakeLists.txt)
- [cuSOLVERSp2cuDSS/README.md](cuSOLVERSp2cuDSS/README.md)
- [cuSOLVERSp2cuDSS/cuSolverRf2cuDSS.hpp](cuSOLVERSp2cuDSS/cuSolverRf2cuDSS.hpp)
- [cuSOLVERSp2cuDSS/cuSolverRf2cuDSS_double.cpp](cuSOLVERSp2cuDSS/cuSolverRf2cuDSS_double.cpp)
- [cuSOLVERSp2cuDSS/cuSolverSp2cuDSS.hpp](cuSOLVERSp2cuDSS/cuSolverSp2cuDSS.hpp)
- [cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_dcomplex.cpp](cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_dcomplex.cpp)
- [cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_double.cpp](cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_double.cpp)
- [cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_float.cpp](cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_float.cpp)
- [cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_scomplex.cpp](cuSOLVERSp2cuDSS/cuSolverSp2cuDSS_scomplex.cpp)
- [cuSOLVERSp2cuDSS/test_complex.mtx](cuSOLVERSp2cuDSS/test_complex.mtx)
- [cuSOLVERSp2cuDSS/test_real.mtx](cuSOLVERSp2cuDSS/test_real.mtx)

</details>



## Purpose and Scope

This document provides a technical overview of the signal processing libraries available in the NVIDIA CUDA Library Samples repository. It focuses primarily on cuFFTMp, NVIDIA's multi-process/multi-GPU Fast Fourier Transform library. This page covers the architecture, data distribution patterns, and usage examples of these libraries. For information about linear algebra libraries, see [Linear Algebra Libraries](#2).

Sources: [README.md:1-52]()

## Overview of Signal Processing Libraries

NVIDIA provides GPU-accelerated signal processing libraries as part of their CUDA ecosystem. These libraries enable efficient computation of signal processing operations across multiple GPUs and nodes.

```mermaid
flowchart TB
    subgraph "Signal Processing Libraries"
        cuFFT["cuFFT\nSingle-GPU FFT"]
        cuFFTMp["cuFFTMp\nMulti-GPU/Multi-Node FFT"]
        cuFFTDx["cuFFTDx\nDevice-side FFT Extensions"]
    end

    subgraph "Communication Libraries"
        MPI["MPI\nMessage Passing Interface"]
        NVSHMEM["NVSHMEM\nNVIDIA Shared Memory"]
        CAL["CAL\nCommunication Abstraction Layer"]
    end

    cuFFTMp --- MPI
    cuFFTMp --- NVSHMEM
    
    subgraph "Applications"
        SignalProc["Signal Processing"]
        ImageProc["Image Processing"]
        ScientificComputing["Scientific Computing"]
    end

    cuFFT --> SignalProc
    cuFFTMp --> SignalProc
    cuFFTMp --> ScientificComputing
    cuFFTDx --> SignalProc
    cuFFTDx --> ImageProc
```

Sources: [README.md:9-14](), [README.md:32-34]()

## cuFFTMp Library

cuFFTMp is NVIDIA's distributed FFT library designed for multi-GPU and multi-node deployments. It extends the functionality of cuFFT to operate across multiple GPUs, enabling processing of larger datasets and providing better performance scaling.

### Key Features

- Multi-GPU and multi-node FFT operations
- Support for various data distribution patterns
- Integration with MPI and NVSHMEM for inter-GPU/node communication
- Data redistribution capabilities
- Support for complex-to-complex (C2C), real-to-complex (R2C), and complex-to-real (C2R) transforms

```mermaid
flowchart LR
    Input["Input Data"] --> Distribution["Data Distribution"]
    Distribution --> Execution["FFT Execution"]
    Execution --> Redistribution["Data Redistribution"]
    Redistribution --> Output["Output Results"]
    
    subgraph "cuFFTMp Workflow"
        Distribution
        Execution
        Redistribution
    end
    
    subgraph "Communication Methods"
        MPI["MPI"]
        NVSHMEM["NVSHMEM"]
    end
    
    Distribution --- MPI & NVSHMEM
    Redistribution --- MPI & NVSHMEM
```

Sources: [README.md:32-34](), [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu:13-43]()

## Data Distribution Patterns

cuFFTMp supports several data distribution patterns, allowing users to choose the most appropriate pattern for their specific workload.

### Built-in Distribution Patterns

- **X-Slabs (CUFFT_XT_FORMAT_INPLACE)**: Data distributed along the X dimension
- **Y-Slabs (CUFFT_XT_FORMAT_INPLACE_SHUFFLED)**: Data distributed along the Y dimension
- **Custom distributions**: User-defined distribution patterns

The following diagram illustrates the data distribution for a 3D FFT:

```mermaid
flowchart TD
    subgraph "X-Slabs Distribution (Input)"
        XSlab1["Rank 0\nX slices: 0 to nx/size-1\nFull Y and Z dimensions"]
        XSlab2["Rank 1\nX slices: nx/size to 2nx/size-1\nFull Y and Z dimensions"]
        XSlab3["...\nAdditional Ranks"]
    end
    
    subgraph "Y-Slabs Distribution (After Transform)"
        YSlab1["Rank 0\nFull X dimension\nY slices: 0 to ny/size-1\nFull Z dimension"]
        YSlab2["Rank 1\nFull X dimension\nY slices: ny/size to 2ny/size-1\nFull Z dimension"]
        YSlab3["...\nAdditional Ranks"]
    end
    
    XSlab1 & XSlab2 & XSlab3 --> Transform["cuFFTMp Transform"]
    Transform --> YSlab1 & YSlab2 & YSlab3
```

Sources: [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu:21-42]()

### Pencil Distribution

For certain applications, a "pencil" distribution is more efficient, where each rank owns a subset of two dimensions:

```mermaid
flowchart TD
    subgraph "Pencil Distribution (Real Space)"
        Pencil1["Rank 0\nX subset, Y subset\nFull Z dimension"]
        Pencil2["Rank 1\nX subset, Y subset\nFull Z dimension"]
        Pencil3["...\nAdditional Ranks"]
    end
    
    subgraph "Pencil Distribution (After R2C Transform)"
        PencilC1["Rank 0\nX subset, Full Y dimension\nZ subset (complex)"]
        PencilC2["Rank 1\nX subset, Full Y dimension\nZ subset (complex)"]
        PencilC3["...\nAdditional Ranks"]
    end
    
    Pencil1 & Pencil2 & Pencil3 --> R2CTransform["R2C Transform"]
    R2CTransform --> PencilC1 & PencilC2 & PencilC3
```

Sources: [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu:133-145]()

## API Overview

cuFFTMp provides several APIs for creating and executing FFT plans on distributed data.

### Key Functions

| Function | Description |
|----------|-------------|
| `cufftMpCreate` | Creates a cuFFTMp plan |
| `cufftMpMakePlan3d` | Creates a 3D plan with built-in data distributions |
| `cufftMpMakePlanDecomposition` | Creates a plan with custom data decomposition |
| `cufftMpExecDescriptor` | Executes a plan using descriptors |
| `cufftMpExecReshapeAsync` | Executes a data redistribution |
| `cufftMpDestroy` | Destroys a cuFFTMp plan |
| `cufftXtMalloc` | Allocates distributed memory |
| `cufftXtFree` | Frees distributed memory |

Sources: [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu:57-64](), [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu:47-50]()

## Execution Workflow

A typical workflow for executing transforms with cuFFTMp involves the following steps:

```mermaid
sequenceDiagram
    participant App as Application
    participant Plan as cuFFTMp Plan
    participant Mem as GPU Memory
    participant Comm as Communication Library
    
    App->>Plan: cufftCreate()
    App->>Plan: cufftMpMakePlan3d() or cufftMpMakePlanDecomposition()
    App->>Mem: cufftXtMalloc()
    App->>Mem: Copy input data to GPU
    App->>Plan: cufftXtExecDescriptor(FORWARD)
    Plan->>Comm: Inter-GPU communication
    Note over Mem: Data is redistributed during transform
    App->>Mem: Perform operations on transformed data
    App->>Plan: cufftXtExecDescriptor(INVERSE)
    Plan->>Comm: Inter-GPU communication
    App->>Mem: Copy results back to host
    App->>Mem: cufftXtFree()
    App->>Plan: cufftDestroy()
```

Sources: [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu:45-91](), [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu:26-82]()

## Data Reshaping

cuFFTMp provides functionality to redistribute data between different decompositions using the `cufftMpCreateReshape` and `cufftMpExecReshapeAsync` functions.

### Data Reshaping Example

The following describes a data reshaping operation where a 2D matrix is redistributed across ranks:

```mermaid
flowchart LR
    subgraph "Initial Distribution"
        ID1["Rank 0\n[0,1,2]\n[5,6,7]\n[10,11,12]\n[15,16,17]"]
        ID2["Rank 1\n[3,4]\n[8,9]\n[13,14]\n[18,19]"]
    end
    
    subgraph "Target Distribution"
        TD1["Rank 0\n[0,1,2,3,4]\n[5,6,7,8,9]"]
        TD2["Rank 1\n[10,11,12,13,14]\n[15,16,17,18,19]"]
    end
    
    ID1 & ID2 --> Reshape["cufftMpExecReshapeAsync()"]
    Reshape --> TD1 & TD2
```

Sources: [cuFFTMp/samples/reshape/cufftmp_reshape.cu:30-53]()

### Box-Based Data Description

cuFFTMp uses "boxes" to describe data distributions, where each box specifies:
- Lower bounds of the data region
- Upper bounds of the data region
- Strides for memory layout

```mermaid
classDiagram
    class Box3D {
        int64 lower[3]
        int64 upper[3]
        int64 strides[3]
    }
    
    class cufftReshapeHandle {
    }
    
    Box3D --> cufftReshapeHandle : Used to configure
```

Sources: [cuFFTMp/samples/reshape/cufftmp_reshape.cu:63-68](), [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu:113-121]()

## Sample Usage

Below is a high-level overview of using cuFFTMp for a C2C (complex-to-complex) transform:

1. Initialize MPI and NVSHMEM for inter-GPU communication
2. Create a cuFFT plan 
3. Configure the plan for distributed execution
4. Allocate distributed memory
5. Execute the forward transform
6. Process the transformed data
7. Execute the inverse transform
8. Retrieve the results

Sources: [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu:93-142]()

### Example: R2C-C2R with Pencil Distribution

This example demonstrates the implementation of a real-to-complex followed by complex-to-real transform using a pencil distribution pattern:

```mermaid
flowchart TB
    Start["Initialize MPI"] --> SetupA["Create FFT Plans\ncuFFTCreate()"]
    SetupA --> SetupB["Configure Distribution\ncufftMpMakePlanDecomposition()"]
    SetupB --> Memory["Allocate Memory\ncufftXtMalloc()"]
    Memory --> Forward["Execute R2C Transform\ncufftXtExecDescriptor(FORWARD)"]
    Forward --> Scale["Scale Data"]
    Scale --> Backward["Execute C2R Transform\ncufftXtExecDescriptor(INVERSE)"]
    Backward --> Result["Copy Results to Host\ncufftXtMemcpy()"]
    Result --> Cleanup["Free Resources\ncufftXtFree()\ncufftDestroy()"]
```

Sources: [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu:26-82]()

## Integration with Communication Libraries

cuFFTMp integrates with MPI and NVSHMEM for inter-GPU and inter-node communication.

### MPI Integration

MPI is used for communication between processes, which can be running on different nodes:

```mermaid
flowchart LR
    subgraph "Node 1"
        GPU1["GPU 0\nRank 0"]
        GPU2["GPU 1\nRank 1"]
    end
    
    subgraph "Node 2"
        GPU3["GPU 0\nRank 2"]
        GPU4["GPU 1\nRank 3"]
    end
    
    GPU1 <--> MPI["MPI Communication"] <--> GPU3
    GPU2 <--> MPI <--> GPU4
```

Sources: [cuFFTMp/samples/c2c_no_descriptors_cufftMpMakePlan/cufftmp_c2c_no_descriptors_cufftMpMakePlan.cu:95-108]()

### NVSHMEM Integration

NVSHMEM provides efficient GPU-to-GPU communication within and across nodes:

```mermaid
flowchart LR
    subgraph "GPU Memory Space"
        GPU1Mem["GPU 0 Memory"]
        GPU2Mem["GPU 1 Memory"]
        GPU3Mem["GPU 2 Memory"]
        GPU4Mem["GPU 3 Memory"]
    end
    
    GPU1Mem <--> NVSHMEM["NVSHMEM\nShared Memory Space"] <--> GPU3Mem
    GPU2Mem <--> NVSHMEM <--> GPU4Mem
```

Sources: [cuFFTMp/samples/reshape/cufftmp_reshape.cu:110-111](), [cuFFTMp/samples/reshape/cufftmp_reshape.cu:122-122]()

## Data Synchronization Considerations

When using cuFFTMp with NVSHMEM, proper synchronization is required to avoid race conditions:

1. Before executing a distributed operation, ensure all buffers are ready on all GPUs
2. Use `nvshmemx_sync_all_on_stream()` to synchronize all processing elements
3. After execution, ensure all operations are complete before accessing memory

This is especially important for operations like `cufftMpExecReshapeAsync` which access memory on remote GPUs.

Sources: [cuFFTMp/samples/reshape/cufftmp_reshape.cu:117-122]()

## Relation to Other NVIDIA Libraries

cuFFTMp is part of NVIDIA's suite of GPU-accelerated libraries:

```mermaid
flowchart TD
    CUDA["CUDA Libraries"]
    
    subgraph "Math Libraries"
        LA["Linear Algebra"]
        FT["Fourier Transforms"]
        RNG["Random Number Generation"]
    end
    
    subgraph "Image Processing"
        JPG["JPEG Processing"]
        TIFF["TIFF Processing"]
    end
    
    CUDA --> FT & LA & RNG & JPG & TIFF
    
    FT --> cuFFT["cuFFT"]
    FT --> cuFFTMp["cuFFTMp"]
    
    LA --> cuBLAS["cuBLAS"]
    LA --> cuBLASMp["cuBLASMp"]
    LA --> cuSOLVER["cuSOLVER"]
    
    JPG --> nvJPEG["nvJPEG"]
    TIFF --> nvTIFF["nvTIFF"]
```

Sources: [README.md:3-15]()

## Performance Considerations

For optimal performance with cuFFTMp:

1. Choose data distributions that minimize communication
2. For best performance with pencil distributions, ensure local dimensions differ between input and output to reduce communication phases
3. Use NVSHMEM for communication when GPUs are within the same node
4. Properly synchronize operations to avoid race conditions

Sources: [cuFFTMp/samples/r2c_c2r_pencils_cufftMpMakePlan/cufftmp_r2c_c2r_pencils_cufftMpMakePlan.cu:142-145]()

## Conclusion

cuFFTMp provides a powerful and flexible framework for distributed FFT operations across multiple GPUs and nodes. Its integration with MPI and NVSHMEM enables efficient communication, while support for various data distribution patterns allows optimization for different workloads. For more information about other NVIDIA libraries, refer to their respective documentation pages.

Sources: [README.md:53-60]()

---

