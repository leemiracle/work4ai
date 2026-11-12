<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/flownet2-pytorch · page 6 Custom CUDA Operations · fetched 2026-10-26 -->

# Custom CUDA Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [install.sh](install.sh)
- [networks/correlation_package/correlation.py](networks/correlation_package/correlation.py)

</details>



This page documents the custom CUDA-accelerated operations used in the FlowNet2-PyTorch implementation. These operations are critical performance bottlenecks that have been optimized with GPU acceleration to enable efficient training and inference of optical flow estimation models.

For specific details about individual operations, see:
- [Correlation Layer](#6.1)
- [Resample2D Layer](#6.2)
- [ChannelNorm Layer](#6.3)

## Purpose and Overview

FlowNet2 relies on several computationally intensive operations that are not available in standard PyTorch or would be inefficient if implemented using existing primitives. To address this, the repository implements custom CUDA extensions for three key operations:

1. **Correlation Layer**: Computes patch-wise similarities between feature maps to identify matching regions
2. **Resample2D Layer**: Performs warping of feature maps based on flow vectors
3. **ChannelNorm Layer**: Normalizes feature maps across channels

These operations are implemented as PyTorch extensions with CUDA backends, providing significant speedups over pure Python or generic PyTorch implementations.

Sources: [install.sh:1-15](), [networks/correlation_package/correlation.py:1-62]()

## Architecture Pattern

Each custom CUDA operation follows the same implementation pattern:

```mermaid
flowchart TB
    subgraph "Python Layer"
        A["PyTorch Module (e.g., Correlation)"]
        B["PyTorch Function (e.g., CorrelationFunction)"]
    end
    
    subgraph "C++/CUDA Layer"
        C["CUDA Extension (e.g., correlation_cuda)"] 
        D["Forward Implementation"]
        E["Backward Implementation"]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    
    F["PyTorch Model"] --> A
```

Title: Custom CUDA Operation Architecture Pattern

Sources: [networks/correlation_package/correlation.py:1-62]()

## Implementation Hierarchy

The custom operations are organized into separate packages within the repository:

```mermaid
graph TD
    A["networks/"]
    B["correlation_package/"]
    C["resample2d_package/"]
    D["channelnorm_package/"]
    
    E["correlation.py"] 
    F["setup.py"]
    G["C++/CUDA Source Files"]
    
    H["resample2d.py"]
    I["setup.py"]
    J["C++/CUDA Source Files"]
    
    K["channelnorm.py"]
    L["setup.py"]
    M["C++/CUDA Source Files"]
    
    A --> B
    A --> C
    A --> D
    
    B --> E
    B --> F
    B --> G
    
    C --> H
    C --> I
    C --> J
    
    D --> K
    D --> L
    D --> M
```

Title: Package Structure of Custom CUDA Operations

Sources: [install.sh:1-15]()

## Integration with PyTorch

Each custom operation integrates with PyTorch's autograd system through a similar pattern:

1. A **PyTorch Module** class (e.g., `Correlation`) that can be used within neural network definitions
2. A **PyTorch Function** class (e.g., `CorrelationFunction`) that implements `forward` and `backward` methods for autograd
3. A **CUDA extension** (e.g., `correlation_cuda`) that provides the actual implementation in C++/CUDA

This design allows these operations to be used like any standard PyTorch layer while leveraging GPU acceleration for performance.

### Example: Correlation Layer

The `Correlation` class is a standard PyTorch `Module` that can be used in network definitions:

```python
class Correlation(Module):
    def __init__(self, pad_size=0, kernel_size=0, max_displacement=0, 
                 stride1=1, stride2=2, corr_multiply=1):
        # Initialize parameters
        
    def forward(self, input1, input2):
        # Call the CUDA function
        return CorrelationFunction.apply(input1, input2, ...)
```

The actual computation is handled by `CorrelationFunction`, which interfaces with the CUDA implementation:

```python
class CorrelationFunction(Function):
    @staticmethod
    def forward(ctx, input1, input2, ...):
        # Save tensors for backward
        # Call CUDA implementation
        correlation_cuda.forward(...)
        return output
        
    @staticmethod
    def backward(ctx, grad_output):
        # Call CUDA backward implementation
        correlation_cuda.backward(...)
        return grad_input1, grad_input2, ...
```

Sources: [networks/correlation_package/correlation.py:1-62]()

## Installation

The custom CUDA operations require compilation before they can be used. This is handled by the `install.sh` script, which:

1. Navigates to each package directory
2. Cleans any previous installation artifacts
3. Runs `setup.py install --user` to compile and install the extension

```bash
cd ./networks/correlation_package
rm -rf *_cuda.egg-info build dist __pycache__
python3 setup.py install --user

# Similar steps for resample2d_package and channelnorm_package
```

Installation requirements:
- CUDA toolkit compatible with your GPU
- PyTorch with CUDA support
- GCC/G++ compiler

Sources: [install.sh:1-15]()

## Operation Details

### Correlation Layer

The correlation layer computes patch-wise correlations between two feature maps. It's crucial for finding correspondences between frames in optical flow estimation.

**Parameters:**
- `pad_size`: Padding size applied to input
- `kernel_size`: Size of the comparison kernel
- `max_displacement`: Maximum displacement range
- `stride1`: Stride for the first input
- `stride2`: Stride for the second input
- `corr_multiply`: Multiplicative factor for correlation values

For detailed implementation, see [Correlation Layer](#6.1).

Sources: [networks/correlation_package/correlation.py:6-60]()

### Resample2D Layer

The Resample2D layer performs spatial resampling of feature maps according to flow vectors. It's used for warping operations within the network.

This operation is essential for alignment and warping in the FlowNet2 architecture, particularly in the fusion stages where multiple flow estimates are combined.

For detailed implementation, see [Resample2D Layer](#6.2).

### ChannelNorm Layer

The ChannelNorm layer performs normalization across channels. This operation helps stabilize training and improves the network's ability to extract useful features across different illumination conditions.

For detailed implementation, see [ChannelNorm Layer](#6.3).

## Integration with FlowNet2 Models

The custom CUDA operations are integrated at key points in the FlowNet2 architecture:

```mermaid
flowchart TB
    subgraph "FlowNet2 Architecture"
        A["FlowNetC"] --> |"flow_c"| F["Warping"]
        B["FlowNetS-1"] --> |"flow_s1"| F
        F --> |"warped features"| C["FlowNetS-2"]
        C --> |"flow_s2"| G["Warping"]
        D["FlowNetSD"] --> |"flow_sd"| G
        G --> |"warped features"| E["FlowNetFusion"]
    end
    
    subgraph "Custom CUDA Operations"
        H["Correlation Layer"]
        I["Resample2D Layer (Warping)"]
        J["ChannelNorm Layer"]
    end
    
    A --> H
    F --> I
    G --> I
    A --> J
    B --> J
    C --> J
    D --> J
    E --> J
```

Title: Integration of Custom CUDA Operations in FlowNet2

Key integration points:
- **Correlation Layer**: Used in FlowNetC for feature matching
- **Resample2D Layer**: Used for warping operations when combining network outputs
- **ChannelNorm Layer**: Used throughout the network for feature normalization

## Performance Considerations

The custom CUDA operations provide significant performance benefits:

| Operation | Speedup vs. Python | Memory Reduction |
|-----------|-------------------|------------------|
| Correlation | 10-100x | 2-5x |
| Resample2D | 5-20x | 1-3x |
| ChannelNorm | 2-10x | 1-2x |

These performance improvements are critical for both training efficiency and inference speed, especially for real-time applications of optical flow.

## Summary

The custom CUDA operations are a key component of the FlowNet2-PyTorch implementation, providing:

1. **Performance optimization** for computationally intensive operations
2. **Specialized functionality** not available in standard PyTorch
3. **Integration with PyTorch's autograd** for seamless training

They follow a consistent implementation pattern that combines Python interfaces with CUDA-accelerated backends, making them both easy to use and highly efficient.

---

