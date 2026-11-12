<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphatensor_quantum · page 7 Precomputed Data Assets · fetched 2026-10-26 -->

# Precomputed Data Assets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [decompositions/load_decompositions.ipynb](decompositions/load_decompositions.ipynb)
- [decompositions/multiplication_finite_fields_gadgets.npz](decompositions/multiplication_finite_fields_gadgets.npz)
- [decompositions/multiplication_finite_fields_no_gadgets.npz](decompositions/multiplication_finite_fields_no_gadgets.npz)

</details>



This document covers the precomputed tensor decomposition data and benchmarks included with the AlphaTensor-Quantum repository. These assets contain optimized quantum circuit decompositions discovered by the reinforcement learning system, stored in compressed formats for analysis and comparison.

For information about the algorithms that generate these decompositions, see [Core Architecture](#3). For details on synthetic demonstration generation during training, see [Synthetic Demonstrations](#6).

## Data Format and Structure

The precomputed assets are stored as compressed NumPy archives (`.npz` files) containing dictionaries that map target circuit names to decomposition arrays. Each decomposition array has shape `(num_decompositions, num_factors, tensor_size)`, where:

- `num_decompositions`: Number of non-equivalent decompositions (maximum 10)
- `num_factors`: Number of rank-one factors in the decomposition  
- `tensor_size`: Dimensionality of the target tensor

```mermaid
graph TB
    subgraph "NPZ Archive Structure"
        NPZFile["NPZ File<br/>(Compressed Archive)"]
        Dict["Dictionary<br/>str -> ndarray"]
        Arrays["Decomposition Arrays<br/>(num_decomps, num_factors, size)"]
    end
    
    subgraph "Circuit Mappings"
        QFT4["'qft_4'<br/>43 qubits, 53 T-count"]
        Toffoli["'BARENCO_TOFF_3'<br/>Circuit tensors"]
        FiniteField["'gf_2pow10_mult_comp2'<br/>GF multiplication"]
    end
    
    NPZFile --> Dict
    Dict --> Arrays
    Dict --> QFT4
    Dict --> Toffoli  
    Dict --> FiniteField
    
    subgraph "Array Contents"
        Factors["Individual Factors<br/>Binary vectors"]
        Gadgets["Gadget Patterns<br/>Toffoli (7 factors)<br/>CS (3 factors)"]
    end
    
    Arrays --> Factors
    Arrays --> Gadgets
```

Sources: [decompositions/load_decompositions.ipynb:114-125]()

## Asset Categories

### Finite Field Multiplication Components

The repository includes precomputed decompositions for finite field multiplication operations in various Galois fields. These are organized into two main categories:

**With Gadgets** (`multiplication_finite_fields_gadgets.npz`):
- Contains decompositions that leverage Toffoli and CS gadgets
- Reduced effective T-count through gadget optimization
- Components for GF(2^n) where n ranges from 2 to 10

**Without Gadgets** (`multiplication_finite_fields_no_gadgets.npz`):
- Direct factor-to-T-gate correspondence
- No gadget-based optimizations
- Baseline decompositions for comparison

```mermaid
graph LR
    subgraph "Finite Field Assets"
        GadgetFile["multiplication_finite_fields_gadgets.npz"]
        NoGadgetFile["multiplication_finite_fields_no_gadgets.npz"]
    end
    
    subgraph "GF Components"
        GF2["gf_2pow2_mult_comp2<br/>GF(2^2) multiplication"]
        GF3["gf_2pow3_mult_comp2<br/>GF(2^3) multiplication"] 
        GF10["gf_2pow10_mult_comp2<br/>GF(2^10) multiplication"]
    end
    
    GadgetFile --> GF2
    GadgetFile --> GF3
    GadgetFile --> GF10
    
    NoGadgetFile --> GF2
    NoGadgetFile --> GF3
    NoGadgetFile --> GF10
```

Sources: [decompositions/multiplication_finite_fields_gadgets.npz:1-216](), [decompositions/multiplication_finite_fields_no_gadgets.npz:1-80]()

### Benchmark Circuit Collections

Additional benchmark datasets are referenced in the analysis notebook, including:

- `benchmarks_no_gadgets.npz`: Quantum circuit benchmarks without gadget optimizations
- `benchmarks_gadgets.npz`: Quantum circuit benchmarks with gadget-based T-count reduction

These contain decompositions for standard quantum circuits such as quantum Fourier transforms (`qft_4`) and other algorithmic primitives.

Sources: [decompositions/load_decompositions.ipynb:58-59](), [decompositions/load_decompositions.ipynb:138-139]()

## Gadget Detection and Analysis

The precomputed assets support two types of quantum gadgets that provide T-count optimizations:

### Toffoli Gadgets
- Consist of 7 factors with specific linear dependency patterns
- Provide 5-factor T-count reduction (7 factors → 2 effective T-gates)
- Detected using `_check_toffoli_gadget()` function

### CS (Controlled-S) Gadgets  
- Consist of 3 factors with linear dependencies
- Provide 1-factor T-count reduction (3 factors → 2 effective T-gates)
- Detected using `_check_cs_gadget()` function

```mermaid
graph TB
    subgraph "Gadget Analysis Pipeline"
        Factors["Input Factors<br/>shape: (num_factors, size)"]
        DetectToffoli["_check_toffoli_gadget()<br/>7-factor patterns"]
        DetectCS["_check_cs_gadget()<br/>3-factor patterns"]
        FindGadgets["find_gadgets()<br/>Complete analysis"]
    end
    
    subgraph "Output Metrics"
        TCount["Effective T-count"]
        NumToffoli["Number of Toffoli gadgets"]
        NumCS["Number of CS gadgets"]
        FactorMasks["Boolean masks<br/>factors_in_toffoli_gadget<br/>factors_in_cs_gadget"]
    end
    
    Factors --> DetectToffoli
    Factors --> DetectCS
    DetectToffoli --> FindGadgets
    DetectCS --> FindGadgets
    
    FindGadgets --> TCount
    FindGadgets --> NumToffoli
    FindGadgets --> NumCS
    FindGadgets --> FactorMasks
```

Sources: [decompositions/load_decompositions.ipynb:230-306]()

## Loading and Verification

The repository provides a complete analysis framework through the Jupyter notebook interface. The loading process includes automatic verification of decomposition correctness:

```mermaid
graph TD
    subgraph "Loading Process"
        Upload["files.upload()<br/>Interactive file selection"]
        Load["np.load(filename)<br/>Extract dictionary"]
        Copy["np.copy().astype(np.int32)<br/>Deep copy for analysis"]
    end
    
    subgraph "Verification Steps"  
        CheckDims["Verify array dimensions<br/>size, num_factors"]
        CheckTensor["np.einsum('bru,brv,brw->buvw')<br/>Reconstruct target tensor"]
        CheckEquiv["assert_array_equal()<br/>Verify equivalence"]
        CheckGadgets["find_gadgets()<br/>Validate T-count metrics"]
    end
    
    Upload --> Load
    Load --> Copy
    Copy --> CheckDims
    CheckDims --> CheckTensor
    CheckTensor --> CheckEquiv
    CheckEquiv --> CheckGadgets
```

The verification process ensures that:
- All decompositions reconstruct the same target tensor
- Factor counts match expected T-gate requirements
- Gadget patterns are correctly identified and counted

Sources: [decompositions/load_decompositions.ipynb:109-126](), [decompositions/load_decompositions.ipynb:191-207](), [decompositions/load_decompositions.ipynb:317-321]()

## Integration with Training System

These precomputed assets serve multiple roles in the broader AlphaTensor-Quantum system:

- **Benchmarking**: Comparison targets for newly discovered decompositions
- **Initialization**: Starting points for further optimization
- **Validation**: Ground truth for testing decomposition algorithms
- **Research**: Analysis of gadget patterns and optimization strategies

The data format directly matches the tensor operations used in [Tensor Operations](#4.1) and the factor manipulation functions in [Factor Operations](#4.2).

Sources: [decompositions/load_decompositions.ipynb:32-33]()

---

