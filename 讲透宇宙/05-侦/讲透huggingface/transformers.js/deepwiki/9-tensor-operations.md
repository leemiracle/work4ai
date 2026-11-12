<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/transformers.js · page 9 Tensor Operations · fetched 2026-10-26 -->

# Tensor Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/transformers/src/models/chatterbox/modeling_chatterbox.js](packages/transformers/src/models/chatterbox/modeling_chatterbox.js)
- [packages/transformers/src/models/florence2/modeling_florence2.js](packages/transformers/src/models/florence2/modeling_florence2.js)
- [packages/transformers/src/models/multi_modality/modeling_multi_modality.js](packages/transformers/src/models/multi_modality/modeling_multi_modality.js)
- [packages/transformers/src/models/phi3_v/modeling_phi3_v.js](packages/transformers/src/models/phi3_v/modeling_phi3_v.js)
- [packages/transformers/src/utils/tensor.js](packages/transformers/src/utils/tensor.js)
- [packages/transformers/tests/utils/tensor.test.js](packages/transformers/tests/utils/tensor.test.js)

</details>



## Purpose and Scope

This document covers the `Tensor` class and tensor manipulation utilities used internally throughout transformers.js. The `Tensor` class wraps ONNX Runtime tensors with a JavaScript-friendly API for numerical computations, shape manipulation, and mathematical operations. All model inputs and outputs flow through this tensor abstraction, which provides both Python-like convenience methods and hardware-accelerated operations via ONNX Runtime.

**Related Documentation**:
- For detailed tensor method signatures and usage, see [Tensor Methods](#9.1)
- For the ONNX Runtime execution backend, see [ONNX Runtime Backend](#8)
- For tensor usage in model pipelines, see [Pipeline API](#2)

---

## Tensor Class Architecture

The `Tensor` class wraps ONNX Runtime's native tensor implementation, providing a Python-like API for JavaScript environments. It serves as the primary data structure for all numerical computations in the library.

**Tensor Class Architecture Diagram**

```mermaid
graph TB
    subgraph TensorHierarchy["Tensor Class Hierarchy"]
        Tensor["Tensor<br/>(packages/transformers/src/utils/tensor.js)"]
        ONNXTensor["ONNXTensor<br/>(packages/transformers/src/backends/onnx.js)"]
        Tensor -->|"wraps"| ONNXTensor
    end
    
    subgraph DataAccess["Data Access Interface"]
        Props["Properties<br/>dims, type, data, size, location"]
        Methods["Methods<br/>item(), tolist(), indexOf()"]
        Iteration["Iteration<br/>Symbol.iterator"]
        Indexing["Indexing<br/>_getitem(), slice()"]
    end
    
    subgraph Operations["Core Operations"]
        Arithmetic["Arithmetic<br/>add, sub, mul, div"]
        Shape["Shape Manipulation<br/>transpose, permute, squeeze"]
        Stats["Statistical<br/>mean, std_mean"]
        Creation["Creation Functions<br/>zeros, ones, full, cat, stack"]
        Activations["Activations<br/>sigmoid"]
    end
    
    subgraph ONNXBacked["ONNX-Backed Operations"]
        Registry["TensorOpRegistry<br/>(packages/transformers/src/ops/registry.js)"]
        ONNXOps["matmul, interpolate_4d<br/>rfft, stft, top_k, slice"]
    end
    
    Tensor --> Props
    Tensor --> Methods
    Tensor --> Iteration
    Tensor --> Indexing
    
    Tensor --> Arithmetic
    Tensor --> Shape
    Tensor --> Stats
    Tensor --> Creation
    Tensor --> Activations
    
    Tensor -.->|"uses"| Registry
    Registry --> ONNXOps
    ONNXOps -.->|"hardware acceleration"| ONNXTensor
    
    User["Internal Model Code"] --> Tensor
```

**Sources**: [packages/transformers/src/utils/tensor.js:25-72](), [packages/transformers/src/ops/registry.js:33-88]()

---

## Construction and Properties

### Tensor Constructor

The `Tensor` class can be constructed in two ways: by wrapping an existing ONNX tensor or by creating a new tensor from data.

**Tensor Construction Paths**

```mermaid
graph LR
    subgraph ConstructionPaths["Construction Paths"]
        Path1["From ONNX Tensor<br/>new Tensor(ort_tensor)"]
        Path2["From Data<br/>new Tensor(type, data, dims)"]
    end
    
    subgraph InternalRep["Internal Representation"]
        OrtTensor["ort_tensor<br/>(ONNXTensor)"]
    end
    
    subgraph ProxyInterface["Proxy Interface"]
        NumericIndex["Numeric Index<br/>tensor[0], tensor[1]"]
        Properties["Property Access<br/>tensor.dims, tensor.data"]
    end
    
    Path1 --> OrtTensor
    Path2 --> OrtTensor
    
    OrtTensor --> NumericIndex
    OrtTensor --> Properties
    
    NumericIndex -.->|"calls"| Getitem["_getitem()"]
```

The constructor uses a JavaScript Proxy to enable array-like indexing: accessing `tensor[0]` internally calls `tensor._getitem(0)`, returning a view or subarray of the tensor data [packages/transformers/src/utils/tensor.js:91-109]().

**Sources**: [packages/transformers/src/utils/tensor.js:78-110]()

### Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `dims` | `number[]` | Shape of the tensor (e.g., `[2, 3, 4]` for 2×3×4 tensor) |
| `type` | `DataType` | Data type string (e.g., `'float32'`, `'int64'`) |
| `data` | `DataArray` | Underlying typed array containing tensor values |
| `size` | `number` | Total number of elements in the tensor |
| `location` | `string` | Memory location (`'cpu'` or `'gpu-buffer'`) |

**Sources**: [packages/transformers/src/utils/tensor.js:30-70]()

---

## Data Type System

The library supports a comprehensive set of data types through the `DataTypeMap`, which maps type strings to JavaScript typed array constructors.

**Data Type Mapping**

```mermaid
graph TB
    subgraph DataTypeMap["DataTypeMap"]
        Float["Floating Point<br/>float32: Float32Array<br/>float16: Float16Array/Uint16Array<br/>float64: Float64Array"]
        Integer["Integer<br/>int8: Int8Array<br/>uint8: Uint8Array<br/>int16: Int16Array<br/>uint16: Uint16Array<br/>int32: Int32Array<br/>uint32: Uint32Array"]
        BigInt["BigInt<br/>int64: BigInt64Array<br/>uint64: BigUint64Array"]
        Other["Other<br/>bool: Uint8Array<br/>string: Array<br/>uint4: Uint8Array<br/>int4: Int8Array"]
    end
    
    TensorType["Tensor.type"] --> Float
    TensorType --> Integer
    TensorType --> BigInt
    TensorType --> Other
    
    Float -.->|"determines"| Storage["Data Storage<br/>Tensor.data"]
    Integer -.->|"determines"| Storage
    BigInt -.->|"determines"| Storage
    Other -.->|"determines"| Storage
```

**Note**: `float16` uses native `Float16Array` where available (limited browser support), falling back to `Uint16Array` for compatibility [packages/transformers/src/utils/dtypes.js:13-17]().

**Sources**: [packages/transformers/src/utils/tensor.js:21-23](), [packages/transformers/src/utils/dtypes.js:1-35]()

---

## Tensor Creation Functions

These factory functions create new tensors with specific initialization patterns.

### Basic Creation

**Tensor Creation Functions**

```mermaid
graph LR
    subgraph CreationFuncs["Creation Functions"]
        zeros["zeros(dims)<br/>All zeros"]
        ones["ones(dims)<br/>All ones"]
        full["full(dims, value)<br/>Constant value"]
        rand["rand(...dims)<br/>Random [0,1)"]
        randn["randn(...dims)<br/>Normal distribution"]
    end
    
    subgraph TemplateBased["Template-Based"]
        zeros_like["zeros_like(tensor)<br/>Zeros with same shape"]
        ones_like["ones_like(tensor)<br/>Ones with same shape"]
        full_like["full_like(tensor, value)<br/>Constant with same shape"]
    end
    
    Template["Reference Tensor"] --> zeros_like
    Template --> ones_like
    Template --> full_like
    
    zeros --> Output["New Tensor"]
    ones --> Output
    full --> Output
    rand --> Output
    randn --> Output
    zeros_like --> Output
    ones_like --> Output
    full_like --> Output
```

**Sources**: [packages/transformers/src/utils/tensor.js:986-1088]()

### Concatenation and Stacking

| Function | Description | Example |
|----------|-------------|---------|
| `cat(tensors, dim)` | Concatenate tensors along dimension | `cat([t1, t2], 0)` joins along first dimension |
| `stack(tensors, dim)` | Stack tensors to create new dimension | `stack([t1, t2], 0)` creates batch dimension |

**Sources**: [packages/transformers/src/utils/tensor.js:1090-1227]()

---

## Shape Manipulation Operations

### Slicing

The `slice()` method extracts subarrays from tensors using Python-like indexing syntax.

**Tensor Slicing Operations**

```mermaid
graph TB
    Input["Input Tensor<br/>dims: [4, 7]"]
    
    subgraph SliceSpecs["Slice Specifications"]
        Single["Single Index<br/>slice(1) → row 1"]
        Range["Range<br/>slice([1, 3]) → rows 1-2"]
        MultiDim["Multi-dimensional<br/>slice([1, -1], [1, -1])"]
        Null["Full Dimension<br/>slice(null) → all"]
    end
    
    Input --> Single
    Input --> Range
    Input --> MultiDim
    Input --> Null
    
    Single --> Output1["Tensor<br/>dims: [7]"]
    Range --> Output2["Tensor<br/>dims: [2, 7]"]
    MultiDim --> Output3["Tensor<br/>dims: [2, 5]"]
    Null --> Output4["Tensor<br/>dims: [4, 7]"]
```

**Slice Index Types**:
- **Number**: Select single element (e.g., `1` for second row)
- **Array `[start, end]`**: Select range `[start, end)` (end exclusive)
- **`null`**: Select entire dimension
- **Negative indices**: Count from end (e.g., `-1` is last element)

**Sources**: [packages/transformers/src/utils/tensor.js:387-610]()

### Dimension Manipulation

| Method | Description | Example |
|--------|-------------|---------|
| `unsqueeze(dim)` | Add dimension of size 1 | `[3, 4]` → `[1, 3, 4]` with `dim=0` |
| `squeeze(dim)` | Remove dimensions of size 1 | `[1, 3, 1, 4]` → `[3, 4]` |
| `transpose(...axes)` | Swap two dimensions | `[2, 3, 4]` → `[2, 4, 3]` with `transpose(-1, -2)` |
| `permute(...axes)` | Reorder all dimensions | `[2, 3, 4]` → `[4, 2, 3]` with `permute(2, 0, 1)` |
| `view(...dims)` | Reshape without copying data | `[6]` → `[2, 3]` |

**Sources**: [packages/transformers/src/utils/tensor.js:612-750]()

---

## Arithmetic Operations

All arithmetic operations come in two variants:
- **Immutable** (`add`, `mul`, etc.): Create new tensor with result
- **In-place** (`add_`, `mul_`, etc.): Modify tensor in place, return `this`

**Arithmetic Operation Variants**

```mermaid
graph TB
    subgraph ImmutableOps["Immutable Operations"]
        add["add(val)"]
        sub["sub(val)"]
        mul["mul(val)"]
        div["div(val)"]
    end
    
    subgraph InPlaceOps["In-Place Operations"]
        add_["add_(val)"]
        sub_["sub_(val)"]
        mul_["mul_(val)"]
        div_["div_(val)"]
    end
    
    InputTensor["Input Tensor"] --> add
    InputTensor --> sub
    InputTensor --> mul
    InputTensor --> div
    
    InputTensor --> add_
    InputTensor --> sub_
    InputTensor --> mul_
    InputTensor --> div_
    
    add --> Clone["tensor.clone()"] --> InPlace["In-place operation"] --> NewTensor["New Tensor"]
    sub --> Clone
    mul --> Clone
    div --> Clone
    
    add_ --> Modify["Modify tensor.data"] --> Same["Return this"]
    sub_ --> Modify
    mul_ --> Modify
    div_ --> Modify
```

**Implementation Pattern**:
```javascript
// Immutable version creates new tensor
mul(val) {
    return this.clone().mul_(val);
}

// In-place version modifies data directly
mul_(val) {
    const this_data = this.data;
    for (let i = 0; i < this_data.length; ++i) {
        this_data[i] *= val;
    }
    return this;
}
```

**Sources**: [packages/transformers/src/utils/tensor.js:267-348]()

---

## Statistical Operations

### Core Statistical Functions

**Statistical Functions Overview**

```mermaid
graph TB
    Input["Input Tensor"]
    
    subgraph StatFunctions["Statistical Functions"]
        mean["mean(tensor, dim, keepdim)"]
        std_mean["std_mean(tensor, dim, correction, keepdim)"]
        mean_pooling["mean_pooling(tensor, attention_mask)"]
    end
    
    subgraph ReturnValues["Return Values"]
        MeanOut["Mean Tensor"]
        StdMeanOut["[std_tensor, mean_tensor]"]
        PoolOut["Pooled Tensor"]
    end
    
    Input --> mean
    Input --> std_mean
    Input --> mean_pooling
    
    mean --> MeanOut
    std_mean --> StdMeanOut
    mean_pooling --> PoolOut
```

**Function Signatures**:
- `mean(tensor, dim=-1, keepdim=false)`: Compute mean along dimension [packages/transformers/src/utils/tensor.js:764-793]()
- `std_mean(tensor, dim=-1, correction=1, keepdim=false)`: Compute standard deviation and mean [packages/transformers/src/utils/tensor.js:795-837]()
- `mean_pooling(tensor, attention_mask)`: Apply attention-masked pooling for embeddings [packages/transformers/src/utils/tensor.js:839-871]()

**Sources**: [packages/transformers/src/utils/tensor.js:764-871]()

---

## Matrix Operations

Matrix operations are hardware-accelerated through ONNX Runtime via the `TensorOpRegistry`.

**Matrix Operation Execution Flow**

```mermaid
sequenceDiagram
    participant UserCode as "Model Code"
    participant matmul as "matmul()"
    participant Registry as "TensorOpRegistry"
    participant ONNX as "ONNX Session"
    participant Backend as "Execution Provider"
    
    UserCode->>matmul: "matmul(a, b)"
    matmul->>Registry: "await TensorOpRegistry.matmul"
    
    alt "First Call (Lazy Load)"
        Registry->>Registry: "Initialize ONNX session<br/>from serialized bytes"
        Registry->>ONNX: "createInferenceSession()"
    end
    
    Registry->>ONNX: "Run inference<br/>{a, b} → {c}"
    ONNX->>Backend: "Execute on WebGPU/WASM/CPU"
    Backend-->>ONNX: "Result tensor"
    ONNX-->>Registry: "ONNXTensor"
    Registry->>Registry: "Wrap as Tensor"
    Registry-->>matmul: "Result Tensor"
    matmul-->>UserCode: "Matrix product"
```

**Key Matrix Operations**:
- `matmul(a, b)`: Matrix multiplication with broadcasting [packages/transformers/src/utils/tensor.js:752-762]()
- `transpose(tensor, axes)`: Transpose dimensions [packages/transformers/src/utils/tensor.js:633-653]()
- `permute_data(array, dims, axes)`: Low-level permutation for typed arrays [packages/transformers/src/utils/maths.js:332-386]()

**Sources**: [packages/transformers/src/utils/tensor.js:752-762](), [packages/transformers/src/ops/registry.js:71-80]()

---

## Activation Functions

### Sigmoid Activation

The sigmoid function `σ(x) = 1 / (1 + e^(-x))` is commonly used in model inference.

**Sigmoid Function Variants**

```mermaid
graph LR
    Input["Input Tensor<br/>x"]
    
    subgraph SigmoidVariants["Sigmoid Variants"]
        sigmoid["sigmoid()<br/>Creates new tensor"]
        sigmoid_["sigmoid_()<br/>In-place modification"]
    end
    
    Formula["σ(x) = 1 / (1 + e^(-x))"]
    
    Input --> sigmoid
    Input --> sigmoid_
    
    sigmoid --> Formula --> NewTensor["New Tensor<br/>with sigmoid applied"]
    sigmoid_ --> Formula --> SameTensor["Modified Input Tensor<br/>(returns this)"]
```

**Sources**: [packages/transformers/src/utils/tensor.js:209-223]()

---

## ONNX-Backed Operations

The `TensorOpRegistry` provides hardware-accelerated operations through pre-compiled ONNX models. These operations are lazily initialized on first use.

### Registry Architecture

**TensorOpRegistry Lazy Initialization**

```mermaid
graph TB
    subgraph TensorOpRegistry["TensorOpRegistry Static Class"]
        Props["Static Properties<br/>session_options"]
        
        subgraph LazyLoaded["Lazy-Loaded Operations"]
            nearest["nearest_interpolate_4d"]
            bilinear["bilinear_interpolate_4d"]
            bicubic["bicubic_interpolate_4d"]
            matmul_op["matmul"]
            stft_op["stft"]
            rfft_op["rfft"]
            slice_op["slice"]
            topk_op["top_k"]
        end
    end
    
    subgraph InitFlow["Initialization Flow"]
        FirstCall["First Access"] --> wrap["wrap(bytes, opts, names)"]
        wrap --> CreateSession["createInferenceSession()"]
        CreateSession --> Wrapper["Async Function<br/>inputs → outputs"]
    end
    
    subgraph ONNXModelBytes["ONNX Model Bytes"]
        SerializedModels["Inline Uint8Array<br/>Pre-compiled ONNX models"]
    end
    
    nearest -.->|"lazy init"| FirstCall
    bilinear -.->|"lazy init"| FirstCall
    bicubic -.->|"lazy init"| FirstCall
    matmul_op -.->|"lazy init"| FirstCall
    
    SerializedModels --> wrap
    
    Wrapper -.->|"cached"| nearest
    Wrapper -.->|"cached"| bilinear
    Wrapper -.->|"cached"| bicubic
    Wrapper -.->|"cached"| matmul_op
```

**Sources**: [packages/transformers/src/ops/registry.js:14-88]()

### Available Operations

| Operation | Purpose | Input/Output |
|-----------|---------|--------------|
| `nearest_interpolate_4d` | Nearest-neighbor interpolation for 4D tensors | `{x, s}` → `{y}` |
| `bilinear_interpolate_4d` | Bilinear interpolation for images | `{x, s}` → `{y}` |
| `bicubic_interpolate_4d` | Bicubic interpolation for high-quality resize | `{x, s}` → `{y}` |
| `matmul` | Matrix multiplication | `{a, b}` → `{c}` |
| `stft` | Short-Time Fourier Transform | `{s, j, w, l}` → `{o}` |
| `rfft` | Real FFT (1D) | `{input}` → `{output}` |
| `slice` | Generic tensor slicing | `{data, starts, ends, axes, steps}` → `{output}` |
| `top_k` | Top K elements with indices | `{x, k}` → `{values, indices}` |

**Sources**: [packages/transformers/src/ops/registry.js:39-88]()

### Interpolation Operations

The interpolation functions resize 4D tensors (batch, channel, height, width) using different algorithms:

**Interpolation Modes**

```mermaid
graph TB
    Input["Input Tensor<br/>shape: [b, c, h_in, w_in]"]
    Scale["Scale Tensor<br/>shape: [4]<br/>[1, 1, h_out, w_out]"]
    
    subgraph InterpolationModes["Interpolation Modes"]
        Nearest["nearest_interpolate_4d<br/>Fast, blocky"]
        Bilinear["bilinear_interpolate_4d<br/>Smooth, common"]
        Bicubic["bicubic_interpolate_4d<br/>Highest quality"]
    end
    
    Input --> Nearest
    Scale --> Nearest
    Input --> Bilinear
    Scale --> Bilinear
    Input --> Bicubic
    Scale --> Bicubic
    
    Nearest --> Output["Output Tensor<br/>shape: [b, c, h_out, w_out]"]
    Bilinear --> Output
    Bicubic --> Output
```

The high-level `interpolate_4d()` function selects the appropriate ONNX operation based on the mode parameter [packages/transformers/src/utils/tensor.js:1229-1277]().

**Sources**: [packages/transformers/src/ops/registry.js:39-69](), [packages/transformers/src/utils/tensor.js:1229-1277]()

---

## Advanced Operations

### Quantization

The library provides quantization functions for embedding compression:

**Quantization Process**

```mermaid
graph LR
    Input["Float32 Embeddings<br/>Tensor"]
    
    subgraph Quantization["Quantization"]
        quantize["quantize_embeddings(tensor, type)"]
        
        Types["Quantization Types:<br/>ubinary: 1 bit<br/>binary: ±1<br/>int8: 8-bit<br/>uint8: 8-bit unsigned"]
    end
    
    subgraph OutputData["Output"]
        Quantized["Quantized Tensor<br/>Reduced precision"]
        Metadata["ranges: [min, max]<br/>per embedding"]
    end
    
    Input --> quantize
    Types --> quantize
    quantize --> Quantized
    quantize --> Metadata
```

**Supported Types**:
- `'ubinary'`: Ultra-compact binary (1 bit per value)
- `'binary'`: Signed binary (-1 or +1)
- `'int8'`: 8-bit signed integers
- `'uint8'`: 8-bit unsigned integers

**Sources**: [packages/transformers/src/utils/tensor.js:873-984]()

### Top-K Selection

The `topk()` function finds the K largest elements and their indices [packages/transformers/src/utils/tensor.js:1303-1318]():

```javascript
const tensor = new Tensor('float32', [3.0, 1.0, 4.0, 1.0, 5.0], [5]);
const [values, indices] = await topk(tensor, 3);
// values: Tensor([5.0, 4.0, 3.0], [3])
// indices: Tensor([4, 2, 0], [3])
```

This operation uses the ONNX-backed `TensorOpRegistry.top_k` for hardware acceleration.

**Sources**: [packages/transformers/src/utils/tensor.js:1303-1318]()

### Layer Normalization

Layer normalization stabilizes training and inference by normalizing activations [packages/transformers/src/utils/tensor.js:1320-1384]:

**Layer Normalization Process**

```mermaid
graph TB
    Input["Input Tensor<br/>x"]
    Weight["Weight Tensor<br/>γ (gamma)"]
    Bias["Bias Tensor<br/>β (beta)"]
    
    subgraph NormProcess["Normalization Process"]
        Mean["Compute Mean<br/>μ = mean(x)"]
        Variance["Compute Variance<br/>σ² = var(x)"]
        Normalize["Normalize<br/>(x - μ) / √(σ² + ε)"]
        Scale["Scale and Shift<br/>γ × normalized + β"]
    end
    
    Input --> Mean
    Input --> Variance
    Mean --> Normalize
    Variance --> Normalize
    Normalize --> Scale
    Weight --> Scale
    Bias --> Scale
    
    Scale --> Output["Normalized Tensor"]
```

**Function Signature**: `layer_norm(x, normalized_shape, {weight, bias, eps=1e-5})`

**Sources**: [packages/transformers/src/utils/tensor.js:1320-1384]()

---

## Memory Management

### Tensor Disposal

Tensors backed by GPU memory should be explicitly disposed to prevent memory leaks [packages/transformers/src/utils/tensor.js:112-115]():

```javascript
const tensor = new Tensor('float32', data, dims);
// ... use tensor ...
tensor.dispose(); // Frees ONNX tensor resources
```

The `dispose()` method releases the underlying ONNX tensor. For CPU tensors, JavaScript garbage collection handles cleanup automatically.

**Sources**: [packages/transformers/src/utils/tensor.js:112-115]()

### Location Awareness

The `location` property indicates where tensor data resides:
- `'cpu'`: Data in system memory (accessible via `.data`)
- `'gpu-buffer'`: Data in GPU memory (`.data` unavailable)

When tensors are on GPU, operations like `tolist()` and direct data access may trigger expensive device-to-host transfers.

**Sources**: [packages/transformers/src/utils/tensor.js:68-70]()

---

## Integration with Model Inference

Tensors serve as the primary data structure throughout the model inference pipeline. All inputs and outputs are represented as named Tensor dictionaries.

**Tensor Flow Through Inference Pipeline**

```mermaid
graph LR
    subgraph InputProcessing["Input Processing"]
        Raw["Raw Input<br/>text/image/audio"]
        Processor["Processor/Tokenizer"]
        InputTensor["Input Tensors<br/>input_ids, pixel_values"]
    end
    
    subgraph ModelExecution["Model Execution"]
        Validate["validateInputs()<br/>(src/models.js)"]
        ToONNX["Convert to<br/>ort_tensor"]
        RunModel["ONNX Session<br/>runInferenceSession()"]
        FromONNX["Wrap as Tensor<br/>replaceTensors()"]
    end
    
    subgraph OutputProcessing["Output Processing"]
        OutputTensor["Output Tensors<br/>logits, embeddings"]
        PostProcess["Post-processing"]
        Result["Final Result"]
    end
    
    Raw --> Processor
    Processor --> InputTensor
    InputTensor --> Validate
    Validate --> ToONNX
    ToONNX --> RunModel
    RunModel --> FromONNX
    FromONNX --> OutputTensor
    OutputTensor --> PostProcess
    PostProcess --> Result
```

**Key Integration Points**:
- Models receive and return dictionaries of named Tensors.
- Architectural classes like `ChatterboxModel` use `cat`, `ones`, and `full` for input preparation [packages/transformers/src/models/chatterbox/modeling_chatterbox.js:73-111]().
- Multi-modal models like `MultiModalityCausalLM` utilize `Tensor` slicing and `cat` for guided generation and image token handling [packages/transformers/src/models/multi_modality/modeling_multi_modality.js:78-115]().

**Sources**: [packages/transformers/src/models/chatterbox/modeling_chatterbox.js:3-111](), [packages/transformers/src/models/multi_modality/modeling_multi_modality.js:5-156]()

---

## Usage Examples

### Creating and Manipulating Tensors

```javascript
// Create from data
const t1 = new Tensor('float32', [1, 2, 3, 4], [2, 2]);

// Create with factory functions
const zeros_tensor = zeros([3, 4]);
const ones_tensor = ones_like(t1);

// Arithmetic operations
const t2 = t1.mul(2).add(1);  // (t1 * 2) + 1

// Shape manipulation
const reshaped = t1.view(1, 4);  // [2, 2] → [1, 4]
const sliced = t1.slice([0, 1], null);  // First row

// Concatenation
const combined = cat([t1, t2], 0);  // Stack vertically
```

### Matrix Operations

```javascript
const a = new Tensor('float32', [1, 2, 3, 4], [2, 2]);
const b = new Tensor('float32', [5, 6, 7, 8], [2, 2]);

// Matrix multiplication (hardware-accelerated)
const c = await matmul(a, b);

// Transpose
const transposed = a.transpose(-1, -2);
```

### Image Interpolation

```javascript
const image = new Tensor('float32', pixels, [1, 3, 224, 224]);
const size = [1, 3, 384, 384];

// Bilinear interpolation for resizing
const resized = await interpolate_4d(image, {
    mode: 'bilinear',
    size: size,
});
```

**Sources**: [packages/transformers/tests/utils/tensor.test.js:8-141](), [packages/transformers/src/utils/tensor.js:1229-1277]()

---

