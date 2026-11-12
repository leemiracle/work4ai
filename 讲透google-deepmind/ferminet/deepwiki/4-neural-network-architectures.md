<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ferminet · page 4 Neural Network Architectures · fetched 2026-10-26 -->

# Neural Network Architectures

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ferminet/networks.py](ferminet/networks.py)
- [ferminet/psiformer.py](ferminet/psiformer.py)
- [ferminet/tests/train_test.py](ferminet/tests/train_test.py)

</details>



This document covers the neural network architectures implemented in FermiNet, specifically the FermiNet and PsiFormer architectures. These are the core wavefunction ansatzes that learn to approximate quantum many-body wavefunctions through antisymmetric neural networks.

For configuration of these networks, see [Configuration System](#2). For the training pipeline that uses these networks, see [Core Training Pipeline](#3). For the physics implementation details like Hamiltonian evaluation, see [Physics and Mathematics](#5).

## Architecture Overview

FermiNet provides two main neural network architectures for quantum wavefunction approximation:

**FermiNet Architecture Comparison**
```mermaid
graph TD
    subgraph "FermiNet Architecture"
        FN_Input["Input Features<br/>ae, ee, r_ae, r_ee"]
        FN_Layers["Permutation Equivariant Layers<br/>One-electron + Two-electron streams"]
        FN_Orbitals["Orbital Shaping<br/>Linear projection to orbitals"]
        FN_Det["Determinant Evaluation<br/>Antisymmetric combination"]
    end
    
    subgraph "PsiFormer Architecture"
        PF_Input["Input Features<br/>ae features + spin"]
        PF_Attn["Self-Attention Layers<br/>Multi-head attention blocks"]
        PF_Orbitals["Orbital Shaping<br/>Linear projection to orbitals"]
        PF_Det["Determinant Evaluation<br/>Antisymmetric combination"]
    end
    
    subgraph "Common Components"
        Envelope["Envelope Functions<br/>Boundary conditions"]
        Jastrow["Jastrow Factors<br/>Electron cusp conditions"]
        Features["Feature Construction<br/>Distance and vector features"]
    end
    
    FN_Input --> FN_Layers
    FN_Layers --> FN_Orbitals
    FN_Orbitals --> FN_Det
    
    PF_Input --> PF_Attn
    PF_Attn --> PF_Orbitals
    PF_Orbitals --> PF_Det
    
    Features --> FN_Input
    Features --> PF_Input
    Envelope --> FN_Orbitals
    Envelope --> PF_Orbitals
    Jastrow --> FN_Det
    Jastrow --> PF_Det
```

Sources: [ferminet/networks.py:1-1525](), [ferminet/psiformer.py:1-462]()

## Network Interface and Data Flow

Both architectures implement common interfaces and follow the same high-level data flow pattern:

**Network Data Flow**
```mermaid
graph LR
    subgraph "Input Data"
        FermiNetData["FermiNetData<br/>positions, spins, atoms, charges"]
        RawInput["Raw electron positions<br/>Shape: (nelectrons*ndim)"]
    end
    
    subgraph "Feature Construction"
        ConstructFeatures["construct_input_features()<br/>ae, ee, r_ae, r_ee"]
        FeatureLayer["feature_layer.apply()<br/>Processed features"]
    end
    
    subgraph "Network Protocols"
        InitFermiNet["InitFermiNet<br/>Parameter initialization"]
        FermiNetLike["FermiNetLike<br/>Main network evaluation"]
        OrbitalFnLike["OrbitalFnLike<br/>Orbital computation"]
    end
    
    subgraph "Output"
        SignLog["(sign, log_magnitude)<br/>Wavefunction in log space"]
        Orbitals["Orbital matrices<br/>For determinant evaluation"]
    end
    
    RawInput --> ConstructFeatures
    ConstructFeatures --> FeatureLayer
    FermiNetData --> FeatureLayer
    
    InitFermiNet --> FermiNetLike
    FeatureLayer --> FermiNetLike
    FermiNetLike --> SignLog
    
    OrbitalFnLike --> Orbitals
    Orbitals --> SignLog
```

Sources: [ferminet/networks.py:40-70](), [ferminet/networks.py:75-151](), [ferminet/networks.py:449-478]()

## FermiNet Architecture

The FermiNet uses a dual-stream architecture with permutation-equivariant layers to maintain antisymmetry:

**FermiNet Layer Structure**
```mermaid
graph TD
    subgraph "Input Processing"
        AE["Electron-atom features<br/>ae_features: (nelectron, natom*(ndim+1))"]
        EE["Electron-electron features<br/>ee_features: (nelectron, nelectron, ndim+1)"]
    end
    
    subgraph "Layer i (repeated)"
        OneElectron["One-electron stream<br/>h_one: (nelectron, dims_one)"]
        TwoElectron["Two-electron stream<br/>h_two: (nelectron, nelectron, dims_two)"]
        Symmetric["construct_symmetric_features()<br/>Permutation-equivariant combination"]
        Residual["Residual connections<br/>(x + y) / sqrt(2)"]
    end
    
    subgraph "Optional Enhancements"
        SchNetEE["SchNet electron-electron<br/>convolutions"]
        SchNetEN["SchNet electron-nuclear<br/>convolutions"]
        SeparateSpins["Separate spin channels<br/>Parallel/antiparallel pairs"]
    end
    
    subgraph "Final Layers"
        LastLayer["Use last layer<br/>Additional symmetric features"]
        OrbitalShape["Orbital shaping<br/>Linear projection"]
    end
    
    AE --> OneElectron
    EE --> TwoElectron
    OneElectron --> Symmetric
    TwoElectron --> Symmetric
    Symmetric --> OneElectron
    OneElectron --> Residual
    TwoElectron --> Residual
    
    SchNetEE --> TwoElectron
    SchNetEN --> Symmetric
    SeparateSpins --> TwoElectron
    
    Residual --> LastLayer
    LastLayer --> OrbitalShape
```

Sources: [ferminet/networks.py:675-1057](), [ferminet/networks.py:514-553]()

### FermiNet Configuration Options

The `FermiNetOptions` class controls the architecture:

| Option | Type | Description |
|--------|------|-------------|
| `hidden_dims` | `FermiLayers` | Tuple of (one-electron, two-electron) dimensions per layer |
| `separate_spin_channels` | `bool` | Use separate streams for parallel/antiparallel spins |
| `schnet_electron_electron_convolutions` | `Tuple[int, ...]` | SchNet convolution dimensions |
| `use_last_layer` | `bool` | Include final permutation-equivariant layer |
| `nuclear_embedding_dim` | `int` | Nuclear embedding dimension for SchNet |
| `electron_nuclear_aux_dims` | `Tuple[int, ...]` | Auxiliary electron-nuclear stream dimensions |

Sources: [ferminet/networks.py:298-334]()

### Key FermiNet Functions

- `make_fermi_net()`: Main factory function [ferminet/networks.py:1363-1524]()
- `make_fermi_net_layers()`: Creates permutation-equivariant layers [ferminet/networks.py:675-1057]()
- `construct_symmetric_features()`: Combines one- and two-electron features [ferminet/networks.py:514-553]()
- `make_schnet_convolution()`: SchNet-style convolutions [ferminet/networks.py:559-634]()

## PsiFormer Architecture

The PsiFormer uses self-attention mechanisms instead of the dual-stream FermiNet architecture:

**PsiFormer Architecture Flow**
```mermaid
graph TD
    subgraph "Input Processing"
        AEFeatures["Electron-atom features<br/>ae_features + spin"]
        Embed["Linear embedding<br/>To attention dimension"]
    end
    
    subgraph "Self-Attention Block (repeated)"
        MultiHead["Multi-head attention<br/>Q, K, V projections"]
        AttnRes["Residual connection<br/>x + attention_output"]
        LayerNorm1["Optional LayerNorm"]
        MLP["MLP<br/>Feed-forward network"]
        MLPRes["Residual connection<br/>x + mlp_output"]
        LayerNorm2["Optional LayerNorm"]
    end
    
    subgraph "Output Processing"
        FinalFeatures["Final attention features<br/>(nelectron, attn_dim)"]
        OrbitalProj["Orbital projection<br/>Linear layer to orbitals"]
    end
    
    AEFeatures --> Embed
    Embed --> MultiHead
    MultiHead --> AttnRes
    AttnRes --> LayerNorm1
    LayerNorm1 --> MLP
    MLP --> MLPRes
    MLPRes --> LayerNorm2
    LayerNorm2 --> MultiHead
    
    LayerNorm2 --> FinalFeatures
    FinalFeatures --> OrbitalProj
```

Sources: [ferminet/psiformer.py:231-323](), [ferminet/psiformer.py:173-228]()

### PsiFormer Configuration Options

The `PsiformerOptions` class controls the attention-based architecture:

| Option | Type | Description |
|--------|------|-------------|
| `num_layers` | `int` | Number of self-attention layers |
| `num_heads` | `int` | Number of attention heads |
| `heads_dim` | `int` | Embedding dimension per head |
| `mlp_hidden_dims` | `Tuple[int, ...]` | MLP hidden dimensions |
| `use_layer_norm` | `bool` | Apply layer normalization |

Sources: [ferminet/psiformer.py:30-48]()

### Key PsiFormer Functions

- `make_fermi_net()`: PsiFormer factory function [ferminet/psiformer.py:326-461]()
- `make_psiformer_layers()`: Creates attention layers [ferminet/psiformer.py:231-323]()
- `make_self_attention_block()`: Self-attention implementation [ferminet/psiformer.py:173-228]()
- `make_multi_head_attention()`: Multi-head attention [ferminet/psiformer.py:71-142]()

## Shared Network Components

Both architectures share several key components that handle common aspects of wavefunction representation:

**Shared Component Architecture**
```mermaid
graph TD
    subgraph "Feature Construction"
        FeatureInit["FeatureInit<br/>Parameter initialization"]
        FeatureApply["FeatureApply<br/>Feature computation"]
        MakeFerminetFeatures["make_ferminet_features()<br/>Standard distance features"]
    end
    
    subgraph "Orbital Construction"
        MakeOrbitals["make_orbitals()<br/>Factory function"]
        OrbitalInit["Orbital parameter init"]
        OrbitalApply["Orbital evaluation"]
    end
    
    subgraph "Envelope Functions"
        EnvelopeInit["envelope.init()"]
        EnvelopeApply["envelope.apply()"]
        PreOrbital["PRE_ORBITAL<br/>Applied to features"]
        PreDeterminant["PRE_DETERMINANT<br/>Applied to orbitals"]
    end
    
    subgraph "Jastrow Factors"
        JastrowInit["jastrow_init()"]
        JastrowApply["jastrow_apply()"]
        ElectronCusp["Electron cusp<br/>conditions"]
    end
    
    subgraph "Determinant Evaluation"
        LogdetMatmul["logdet_matmul()<br/>Antisymmetric combination"]
        StateMatrix["Excited states<br/>Matrix determinants"]
    end
    
    FeatureInit --> FeatureApply
    MakeFerminetFeatures --> FeatureApply
    
    MakeOrbitals --> OrbitalInit
    MakeOrbitals --> OrbitalApply
    
    EnvelopeInit --> EnvelopeApply
    PreOrbital --> OrbitalApply
    PreDeterminant --> OrbitalApply
    
    JastrowInit --> JastrowApply
    ElectronCusp --> LogdetMatmul
    
    OrbitalApply --> LogdetMatmul
    StateMatrix --> LogdetMatmul
```

Sources: [ferminet/networks.py:1063-1244](), [ferminet/networks.py:196-258](), [ferminet/networks.py:481-508]()

### Feature Layers

Feature construction transforms raw positions into network inputs:

```python
# Standard FermiNet features
def make_ferminet_features(natoms, nspins, ndim=3, rescale_inputs=False)
# Returns: FeatureLayer with init and apply functions
# Output: (ae_features, ee_features) where
#   ae_features: (nelectron, natom*(ndim+1))  
#   ee_features: (nelectron, nelectron, ndim+1)
```

Sources: [ferminet/networks.py:481-508]()

### Envelope Functions

Envelopes ensure orbitals decay properly at infinity and can be applied at different points:

- `EnvelopeType.PRE_ORBITAL`: Applied to final layer features [ferminet/networks.py:1183-1187]()
- `EnvelopeType.PRE_DETERMINANT`: Applied to individual orbitals [ferminet/networks.py:1210-1220]()

### Determinant Construction

Both architectures support multiple determinants and excited states:

```python
# Multiple determinants for ground state
options.determinants = 16

# Multiple excited states  
options.states = 3

# Full determinant vs spin-factored
options.full_det = True  # (ndet, nalpha+nbeta, nalpha+nbeta)
options.full_det = False # Separate (ndet, nalpha, nalpha) and (ndet, nbeta, nbeta)
```

Sources: [ferminet/networks.py:1099-1112](), [ferminet/networks.py:1222-1232]()

## Excited State Support

Both architectures support excited state calculations through specialized wrappers:

**Excited State Functions**
```mermaid
graph LR
    subgraph "State Functions"
        BaseNetwork["Base network<br/>Single state output"]
        StateMatrix["make_state_matrix()<br/>Matrix of states psi_i(x_j)"]
        StateTrace["make_state_trace()<br/>Diagonal trace for MCMC"]
        TotalAnsatz["make_total_ansatz()<br/>Meta-determinant"]
    end
    
    subgraph "Usage"
        MCMC["MCMC sampling<br/>Uses state_trace"]
        Energy["Energy evaluation<br/>Uses total_ansatz"]
        Overlap["Overlap calculations<br/>Uses state_matrix"]
    end
    
    BaseNetwork --> StateMatrix
    StateMatrix --> StateTrace
    StateMatrix --> TotalAnsatz
    
    StateTrace --> MCMC
    TotalAnsatz --> Energy
    StateMatrix --> Overlap
```

Sources: [ferminet/networks.py:1250-1357]()

## Testing and Validation

The architecture implementations are extensively tested across various configurations:

**Test Coverage**
```mermaid
graph TD
    subgraph "Network Tests"
        BasicTests["Basic functionality<br/>train_test.py"]
        SchNetTests["SchNet convolutions<br/>Electron-electron/nuclear"]
        SpinTests["Separate spin channels<br/>Parallel/antiparallel"]
        StateTests["Excited states<br/>Multiple state handling"]
    end
    
    subgraph "Configuration Tests"
        OptimizerTests["Optimizer compatibility<br/>KFAC, Adam, etc."]
        ComplexTests["Complex output<br/>Complex wavefunctions"]
        LaplacianTests["Laplacian methods<br/>Default vs FOLX"]
        PseudoTests["Pseudopotential<br/>Effective core potentials"]
    end
    
    subgraph "System Tests"
        AtomTests["Atomic systems<br/>H, Li, etc."]
        MoleculeTests["Molecular systems<br/>LiH, H2O, etc."]
        PBCTests["Periodic systems<br/>Solid state"]
    end
    
    BasicTests --> OptimizerTests
    SchNetTests --> SpinTests
    StateTests --> ComplexTests
    
    OptimizerTests --> AtomTests
    ComplexTests --> MoleculeTests
    LaplacianTests --> PBCTests
```

Sources: [ferminet/tests/train_test.py:51-310]()

Key test configurations include:
- Hidden dimensions: `((16, 4),) * 2` for testing
- Determinants: 2 for fast testing
- Batch size: 32 for memory efficiency
- Iterations: 3 for quick validation

Sources: [ferminet/tests/train_test.py:107-117](), [ferminet/tests/train_test.py:289-309]()

---

