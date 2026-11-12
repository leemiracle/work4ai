<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/candle · page 4 Quantization System · fetched 2026-10-26 -->

# Quantization System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [candle-core/src/cuda_backend/cudnn.rs](candle-core/src/cuda_backend/cudnn.rs)
- [candle-core/src/cuda_backend/device.rs](candle-core/src/cuda_backend/device.rs)
- [candle-core/src/cuda_backend/mod.rs](candle-core/src/cuda_backend/mod.rs)
- [candle-core/src/quantized/avx.rs](candle-core/src/quantized/avx.rs)
- [candle-core/src/quantized/cuda.rs](candle-core/src/quantized/cuda.rs)
- [candle-core/src/quantized/dummy_cuda.rs](candle-core/src/quantized/dummy_cuda.rs)
- [candle-core/src/quantized/dummy_metal.rs](candle-core/src/quantized/dummy_metal.rs)
- [candle-core/src/quantized/ggml_file.rs](candle-core/src/quantized/ggml_file.rs)
- [candle-core/src/quantized/gguf_file.rs](candle-core/src/quantized/gguf_file.rs)
- [candle-core/src/quantized/k_quants.rs](candle-core/src/quantized/k_quants.rs)
- [candle-core/src/quantized/metal.rs](candle-core/src/quantized/metal.rs)
- [candle-core/src/quantized/mod.rs](candle-core/src/quantized/mod.rs)
- [candle-core/src/quantized/neon.rs](candle-core/src/quantized/neon.rs)
- [candle-core/src/quantized/simd128.rs](candle-core/src/quantized/simd128.rs)
- [candle-core/src/quantized/utils.rs](candle-core/src/quantized/utils.rs)
- [candle-core/src/utils.rs](candle-core/src/utils.rs)
- [candle-core/tests/gguf_tests.rs](candle-core/tests/gguf_tests.rs)
- [candle-core/tests/quantized_tests.rs](candle-core/tests/quantized_tests.rs)
- [candle-kernels/src/quantized.cu](candle-kernels/src/quantized.cu)
- [candle-metal-kernels/src/kernels/mod.rs](candle-metal-kernels/src/kernels/mod.rs)
- [candle-metal-kernels/src/kernels/quantized.rs](candle-metal-kernels/src/kernels/quantized.rs)
- [candle-nn/examples/cpu_benchmarks.rs](candle-nn/examples/cpu_benchmarks.rs)
- [candle-wasm-tests/tests/quantized_tests.rs](candle-wasm-tests/tests/quantized_tests.rs)

</details>



The quantization system in Candle enables memory-efficient model inference by storing weights in reduced-precision formats (2-8 bits per weight) while performing computations in higher precision. This reduces memory usage by 4-16x compared to float32 models with minimal accuracy loss. The system supports loading quantized models from GGUF and GGML file formats and provides device-specific optimizations for CPU (SIMD), CUDA, and Metal backends.

For model implementations using quantization, see [Using Quantized Models](#4.3). For the format specifications and quantization type details, see [Quantization Formats and Types](#4.1). For the optimized operations, see [Quantized Operations](#4.2).

## Architecture Overview

The quantization system consists of four main layers: file format loaders, storage abstraction, quantization types, and device-specific operations.

```mermaid
graph TB
    subgraph "File Format Layer"
        GGUF["gguf_file::Content<br/>Read GGUF files"]
        GGML["ggml_file::Content<br/>Read GGML files"]
        IMatrix["imatrix_file::load_imatrix()<br/>Importance matrix weights"]
    end
    
    subgraph "Tensor Abstraction"
        QTensor["QTensor<br/>storage: QStorage<br/>shape: Shape"]
        QStorage["QStorage enum<br/>Cpu/Cuda/Metal"]
    end
    
    subgraph "Storage Implementations"
        QStorageCpu["QStorage::Cpu<br/>Box&lt;dyn QuantizedType&gt;"]
        QStorageCuda["QStorage::Cuda<br/>QCudaStorage<br/>PaddedCudaSlice"]
        QStorageMetal["QStorage::Metal<br/>QMetalStorage<br/>Arc&lt;Buffer&gt;"]
    end
    
    subgraph "Quantization Types"
        GgmlDType["GgmlDType enum<br/>Q4_0, Q8_0, Q2K-Q8K<br/>F16, F32, BF16"]
        BlockTypes["Block Types<br/>BlockQ4_0, BlockQ8_0<br/>BlockQ2K-BlockQ8K"]
        GgmlType["GgmlType trait<br/>to_float(), from_float()<br/>vec_dot()"]
    end
    
    subgraph "Operations"
        QMatMul["QMatMul<br/>Quantized matrix multiplication"]
        Quantize["quantize()<br/>F32 -> Quantized"]
        Dequantize["dequantize()<br/>Quantized -> F32"]
    end
    
    GGUF --> QTensor
    GGML --> QTensor
    IMatrix -.optional.-> Quantize
    
    QTensor --> QStorage
    QStorage --> QStorageCpu
    QStorage --> QStorageCuda
    QStorage --> QStorageMetal
    
    QStorageCpu --> BlockTypes
    QStorageCuda --> BlockTypes
    QStorageMetal --> BlockTypes
    
    BlockTypes -.implements.-> GgmlType
    GgmlType --> GgmlDType
    
    QTensor --> QMatMul
    QTensor --> Dequantize
    Quantize --> QTensor
```

**Sources:** [candle-core/src/quantized/mod.rs:59-91](), [candle-core/src/quantized/k_quants.rs:22-75](), [candle-core/src/quantized/gguf_file.rs:81-128]()

## QTensor and QStorage System

The `QTensor` type is the primary abstraction for quantized tensors, wrapping a `QStorage` enum that dispatches to device-specific implementations.

### QTensor Structure

```mermaid
graph LR
    subgraph "Public API"
        QTensor["QTensor<br/>storage: QStorage<br/>shape: Shape"]
    end
    
    subgraph "Storage Dispatch"
        QStorage["QStorage enum"]
        QStorage --> Cpu["Cpu(Box&lt;dyn QuantizedType&gt;)"]
        QStorage --> Metal["Metal(QMetalStorage)"]
        QStorage --> Cuda["Cuda(QCudaStorage)"]
    end
    
    subgraph "CPU Storage"
        QuantizedType["QuantizedType trait<br/>matmul_t()<br/>dequantize()<br/>from_float()"]
        VecBlockQ4["Vec&lt;BlockQ4_0&gt;"]
        VecBlockQ8["Vec&lt;BlockQ8_0&gt;"]
        VecBlockQ2K["Vec&lt;BlockQ2K&gt;"]
    end
    
    subgraph "GPU Storage"
        QCudaStorage["QCudaStorage<br/>data: PaddedCudaSlice<br/>dtype: GgmlDType<br/>device: CudaDevice"]
        QMetalStorage["QMetalStorage<br/>buffer: Arc&lt;Buffer&gt;<br/>dtype: GgmlDType<br/>device: MetalDevice"]
    end
    
    QTensor --> QStorage
    Cpu --> QuantizedType
    QuantizedType -.implemented by.-> VecBlockQ4
    QuantizedType -.implemented by.-> VecBlockQ8
    QuantizedType -.implemented by.-> VecBlockQ2K
    
    Metal --> QMetalStorage
    Cuda --> QCudaStorage
```

**Sources:** [candle-core/src/quantized/mod.rs:59-91](), [candle-core/src/quantized/cuda.rs:16-20](), [candle-core/src/quantized/metal.rs:7-11]()

### QStorage Operations

The `QStorage` enum provides the following key operations:

| Operation | Purpose | CPU | CUDA | Metal |
|-----------|---------|-----|------|-------|
| `from_data()` | Load from raw bytes | ✓ | ✓ | ✓ |
| `quantize()` | Convert F32 tensor to quantized | ✓ | ✓ | ✓ |
| `quantize_imatrix()` | Quantize with importance matrix | ✓ | ✓ | ✓ |
| `dequantize()` | Convert quantized to F32 | ✓ | ✓ | ✓ |
| `size_in_bytes()` | Get raw storage size | ✓ | ✓ | ✓ |
| `device()` | Get associated Device | ✓ | ✓ | ✓ |

**Sources:** [candle-core/src/quantized/mod.rs:93-171]()

### Creating QTensor from Files

```mermaid
sequenceDiagram
    participant User
    participant File as GGUF/GGML File
    participant Content as gguf_file::Content
    participant TensorInfo as TensorInfo
    participant QTensor
    participant QStorage
    participant Device
    
    User->>File: open file
    User->>Content: Content::read(&mut file)
    Content-->>User: metadata + tensor_infos
    
    loop For each tensor
        User->>TensorInfo: tensor_info.read(file, offset, device)
        TensorInfo->>File: seek + read raw bytes
        TensorInfo->>QStorage: QStorage::from_data(bytes, device, dtype)
        
        alt CPU
            QStorage->>QStorage: dtype.from_data(bytes)
            QStorage-->>TensorInfo: QStorage::Cpu(Box<dyn QuantizedType>)
        else CUDA
            QStorage->>Device: cuda::load_quantized(bytes)
            QStorage-->>TensorInfo: QStorage::Cuda(QCudaStorage)
        else Metal
            QStorage->>Device: metal::load_quantized(bytes)
            QStorage-->>TensorInfo: QStorage::Metal(QMetalStorage)
        end
        
        TensorInfo->>QTensor: QTensor::new(storage, shape)
        TensorInfo-->>User: QTensor
    end
```

**Sources:** [candle-core/src/quantized/gguf_file.rs:88-128](), [candle-core/src/quantized/mod.rs:94-133]()

## Block Quantization Types

Block-based quantization divides tensors into fixed-size blocks, with each block storing quantized values and a scaling factor. Candle implements various formats including standard `Q4_0`, `Q8_0` and the more complex "K-Quants" (`Q2K` through `Q6K`).

### Block Structure Overview

| Type | Block Size | Components | Size (Bytes) |
|------|------------|------------|--------------|
| `BlockQ4_0` | 32 | `d: f16`, `qs: [u8; 16]` | 18 |
| `BlockQ4_1` | 32 | `d: f16`, `m: f16`, `qs: [u8; 16]` | 20 |
| `BlockQ8_0` | 32 | `d: f16`, `qs: [i8; 32]` | 34 |
| `BlockQ2K` | 256 | `scales: [u8; 16]`, `qs: [u8; 64]`, `d: f16`, `dmin: f16` | 84 |
| `BlockQ6K` | 256 | `ql: [u8; 128]`, `qh: [u8; 64]`, `scales: [i8; 16]`, `d: f16` | 210 |
| `BlockQ8K` | 256 | `d: f32`, `qs: [i8; 256]`, `bsums: [i16; 16]` | 292 |

**Sources:** [candle-core/src/quantized/k_quants.rs:79-190]()

### GgmlType Trait

The `GgmlType` trait defines the interface for all quantization block types:

```mermaid
graph TB
    subgraph "GgmlType Trait"
        Trait["trait GgmlType<br/>DTYPE: GgmlDType<br/>BLCK_SIZE: usize<br/>VecDotType: GgmlType"]
        
        Methods["Methods<br/>to_float(xs, ys)<br/>from_float(xs, ys)<br/>from_float_imatrix(xs, ys, imatrix)<br/>vec_dot(n, xs, ys) -> f32<br/>vec_dot_unopt(n, xs, ys) -> f32"]
    end
    
    subgraph "Implementations"
        Q4_0Impl["impl GgmlType for BlockQ4_0<br/>BLCK_SIZE = 32<br/>VecDotType = BlockQ8_0"]
        Q8_0Impl["impl GgmlType for BlockQ8_0<br/>BLCK_SIZE = 32<br/>VecDotType = BlockQ8_0"]
        Q2KImpl["impl GgmlType for BlockQ2K<br/>BLCK_SIZE = 256<br/>VecDotType = BlockQ8K"]
    end
    
    Trait --> Methods
    Trait -.implemented by.-> Q4_0Impl
    Trait -.implemented by.-> Q8_0Impl
    Trait -.implemented by.-> Q2KImpl
```

**Sources:** [candle-core/src/quantized/k_quants.rs:22-75]()

## Optimized Operations

### CPU (SIMD)
Candle provides handwritten SIMD implementations for major architectures:
- **AVX2**: Optimized `vec_dot` routines for x86_64 using instructions like `_mm256_maddubs_epi16`. [candle-core/src/quantized/avx.rs:50-87]()
- **NEON**: Optimized `vec_dot` routines for ARM Aarch64, utilizing `sdot` instructions where available. [candle-core/src/quantized/neon.rs:125-197]()
- **SIMD128**: Optimized `vec_dot` routines for WebAssembly. [candle-core/src/quantized/mod.rs:37]()

### CUDA Fast Paths
For CUDA, Candle includes high-performance kernels for GGUF tiled matrix multiplication:
- **fast_mmvq**: Optimized for small batch sizes (typically 1-8). [candle-core/src/quantized/mod.rs:28]()
- **fast_mmq**: Optimized for larger batch sizes (> 8). [candle-core/src/quantized/mod.rs:26]()
- **DMMV/MMQ**: Standard GGML-style kernels for various compute capabilities (Pascal, Ampere, etc.). [candle-core/src/quantized/cuda.rs:30-34](), [candle-kernels/src/quantized.cu:97-225]()

### Metal Kernels
The Metal backend supports dequantization and matrix-vector products directly in MSL shaders, with a fallback to CPU dequantization for certain paths. [candle-core/src/quantized/metal.rs:40-132]()

## Using Quantized Models

Quantized models are typically loaded using the `quantized_var_builder` which handles GGUF/GGML file parsing and mapping weights to `QTensor` objects. The `QMatMul` struct provides a high-level `Module` implementation for quantized linear layers.

For details on format specifications, see [Quantization Formats and Types](#4.1).
For operation details, see [Quantized Operations](#4.2).
For loading examples (LLaMA, Mistral, etc.), see [Using Quantized Models](#4.3).

**Sources:** [candle-core/src/quantized/gguf_file.rs:1-128](), [candle-core/src/quantized/mod.rs:11-14](), [candle-core/tests/quantized_tests.rs:19-54]()

---

