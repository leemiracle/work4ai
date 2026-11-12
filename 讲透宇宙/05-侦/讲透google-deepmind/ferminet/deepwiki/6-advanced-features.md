<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ferminet · page 6 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ferminet/configs/li_excited.py](ferminet/configs/li_excited.py)
- [ferminet/notebooks/excited_states_analysis.ipynb](ferminet/notebooks/excited_states_analysis.ipynb)
- [ferminet/pbc/envelopes.py](ferminet/pbc/envelopes.py)
- [ferminet/pbc/feature_layer.py](ferminet/pbc/feature_layer.py)
- [ferminet/utils/gto.py](ferminet/utils/gto.py)
- [ferminet/utils/scf.py](ferminet/utils/scf.py)
- [ferminet/utils/tests/gto_test.py](ferminet/utils/tests/gto_test.py)

</details>



This document covers specialized capabilities and extensions to the core FermiNet functionality, including periodic boundary conditions for solid-state systems, excited states calculations, SCF pretraining integration, and Gaussian-type orbital evaluation. For information about the core neural network architectures, see [Neural Network Architectures](#4). For basic configuration and training, see [Configuration System](#2) and [Core Training Pipeline](#3).

## Periodic Boundary Conditions

FermiNet supports periodic boundary conditions (PBC) for modeling solid-state systems, quantum phase transitions, and extended materials. The PBC implementation includes specialized feature layers, envelope functions, and k-point sampling to handle the unique requirements of periodic systems.

### PBC Feature Layer Architecture

```mermaid
graph TD
    Coords["coords: Electron Positions<br/>[batch, nelec, 3]"]
    Lattice["lattice: Lattice Vectors<br/>[3, 3] matrix"]
    
    subgraph "Coordinate Transformation"
        FractCoords["scaled_r: Fractional Coordinates<br/>reciprocal_vecs @ coords"]
        PhaseCoords["s_ae, s_ee: Phase Coordinates<br/>k_i · ae, k_i · ee"]
    end
    
    subgraph "Feature Generation"
        PeriodicFeats["Periodic Features<br/>sin(2π s), cos(2π s)"]
        DistFeats["Distance Features<br/>periodic_norm(metric, s)"]
    end
    
    subgraph "Output Features"
        AEFeats["ae_features: Atom-Electron<br/>[natoms*(2*ndim+1)]"]
        EEFeats["ee_features: Electron-Electron<br/>[2*ndim+1]"]
    end
    
    Coords --> FractCoords
    Lattice --> FractCoords
    FractCoords --> PhaseCoords
    PhaseCoords --> PeriodicFeats
    PhaseCoords --> DistFeats
    PeriodicFeats --> AEFeats
    PeriodicFeats --> EEFeats
    DistFeats --> AEFeats
    DistFeats --> EEFeats
```

The PBC feature layer transforms standard Cartesian coordinates into periodic-aware features using the `make_pbc_feature_layer` function, which handles lattice vector transformations and periodic distance calculations.

**Sources**: [ferminet/pbc/feature_layer.py:46-110]()

### Envelope Functions and K-Point Sampling

```mermaid
graph LR
    subgraph "K-Point Generation"
        LatticeVecs["Lattice Vectors<br/>lattice: [3,3]"]
        RecLattice["Reciprocal Lattice<br/>2π * inv(lattice)"]
        KPoints["K-Points Array<br/>make_kpoints()"]
    end
    
    subgraph "Multiwave Envelope"
        KPoints --> Phases["Phase Coordinates<br/>ae @ kpoints.T"]
        Phases --> Waves["Oscillatory Terms<br/>cos(phase), sin(phase)"]
        Waves --> Envelope["Envelope Function<br/>Σ σ²·waves"]
    end
    
    subgraph "Network Integration"
        Envelope --> PreDet["Pre-Determinant<br/>Multiplication"]
        PreDet --> WaveFunction["Final Wavefunction"]
    end
    
    LatticeVecs --> RecLattice
    RecLattice --> KPoints
```

The envelope system uses `make_multiwave_envelope` to create oscillatory envelope functions based on k-point sampling. The `make_kpoints` function generates reciprocal lattice vectors sorted by magnitude to ensure proper shell filling.

**Sources**: [ferminet/pbc/envelopes.py:31-76](), [ferminet/pbc/envelopes.py:79-122]()

## Excited States and SCF Integration

FermiNet supports calculation of excited electronic states through overlap penalty methods and integration with Hartree-Fock pretraining via PySCF. This enables access to multiple electronic states and improved initialization.

### SCF Integration Architecture

```mermaid
graph TD
    subgraph "PySCF Integration"
        Molecule["system.Atom List<br/>Nuclear coordinates"]
        PySCFMol["pyscf.gto.Mole<br/>Quantum chemistry molecule"]
        SCFCalc["SCF Calculation<br/>RHF/UHF solver"]
    end
    
    subgraph "Orbital Processing"
        MOCoeffs["mo_coeff: MO Coefficients<br/>Basis → orbital transform"]
        ExciteGen["Excitation Generation<br/>get_ordered_excitations()"]
        OrbitalEval["eval_orbitals()<br/>MO evaluation at positions"]
    end
    
    subgraph "FermiNet Integration"
        SlaterDet["eval_slater()<br/>Slater determinant"]
        Pretraining["Pretraining Phase<br/>Network initialization"]
        Training["Main Training<br/>VMC optimization"]
    end
    
    Molecule --> PySCFMol
    PySCFMol --> SCFCalc
    SCFCalc --> MOCoeffs
    MOCoeffs --> ExciteGen
    MOCoeffs --> OrbitalEval
    OrbitalEval --> SlaterDet
    SlaterDet --> Pretraining
    Pretraining --> Training
```

The `Scf` class provides a bridge between FermiNet and quantum chemistry methods, handling molecular orbital evaluation and excited state generation.

**Sources**: [ferminet/utils/scf.py:54-127](), [ferminet/utils/scf.py:362-433]()

### Excited States Configuration

| Configuration Parameter | Purpose | Example Value |
|-------------------------|---------|---------------|
| `cfg.system.states` | Number of states to calculate | `3` |
| `cfg.pretrain.iterations` | SCF pretraining iterations | `1000` |
| `cfg.observables.s2` | Calculate spin magnitude | `True` |
| `cfg.observables.dipole` | Calculate dipole moment | `True` |
| `cfg.observables.density` | Calculate density matrix | `True` |

The excited states system supports both ordered and random excitation generation through the `excitation_type` parameter in the `run` method.

**Sources**: [ferminet/configs/li_excited.py:64-81]()

### Excited States Analysis Workflow

```mermaid
graph LR
    subgraph "Data Collection"
        Training["Training Loop"]
        EnergyMat["energy_matrix.npy<br/>State energy matrices"]
        S2Mat["s2_matrix.npy<br/>Spin observables"]
        DipoleMat["dipole_matrix.npy<br/>Dipole moments"]
        DensityMat["density_matrix.npy<br/>Density matrices"]
    end
    
    subgraph "State Demixing"
        LoadData["load_data()<br/>Average matrices"]
        Eigsolve["Eigenvalue Solve<br/>Extract states"]
        Demix["get_results()<br/>Demixed observables"]
    end
    
    subgraph "Analysis"
        Energies["State Energies"]
        Transitions["Transition Properties"]
        OscStrength["Oscillator Strengths"]
    end
    
    Training --> EnergyMat
    Training --> S2Mat
    Training --> DipoleMat
    Training --> DensityMat
    
    EnergyMat --> LoadData
    S2Mat --> LoadData
    DipoleMat --> LoadData
    DensityMat --> LoadData
    
    LoadData --> Eigsolve
    Eigsolve --> Demix
    Demix --> Energies
    Demix --> Transitions
    Demix --> OscStrength
```

The analysis workflow processes mixed state data from training to extract individual excited state properties through eigenvalue decomposition and statistical analysis.

**Sources**: [ferminet/notebooks/excited_states_analysis.ipynb:148-197]()

## Gaussian-Type Orbital Integration

FermiNet includes a pure JAX implementation for evaluating Gaussian-type orbitals (GTOs), enabling direct integration with quantum chemistry basis sets and molecular orbital calculations.

### GTO Evaluation System

```mermaid
graph TD
    subgraph "Basis Set Processing"
        PySCFMol["pyscf.gto.Mole<br/>Quantum chemistry molecule"]
        BasisDict["basis_dict<br/>cGTO specifications"]
        NormWeights["normalize_primitive_weights<br/>Correct normalization"]
    end
    
    subgraph "Orbital Construction"
        ConstructSpec["_get_orbital_construction_dict<br/>Unravel basis specification"]
        Alpha["alpha: Gaussian exponents"]
        Weights["primitive_weights: Coefficients"]
        Shells["cshell_id: Shell assignments"]
    end
    
    subgraph "Evaluation Engine"
        Coords["coords: Grid points [G, 3]"]
        SolidHarm["solid_harmonic_from_cart<br/>Angular components"]
        RadialPart["Radial gaussian evaluation"]
        Contract["segment_sum contraction"]
        GTOValues["GTO values [G, CGTO]"]
    end
    
    PySCFMol --> BasisDict
    BasisDict --> NormWeights
    NormWeights --> ConstructSpec
    ConstructSpec --> Alpha
    ConstructSpec --> Weights
    ConstructSpec --> Shells
    
    Coords --> SolidHarm
    Alpha --> RadialPart
    Weights --> RadialPart
    SolidHarm --> GTOValues
    RadialPart --> Contract
    Contract --> GTOValues
```

The `Mol` class provides a JAX-native implementation of GTO evaluation that maintains compatibility with PySCF while enabling GPU acceleration and automatic differentiation.

**Sources**: [ferminet/utils/gto.py:219-263](), [ferminet/utils/gto.py:338-389]()

### Spherical Harmonics Implementation

The GTO system includes optimized spherical harmonic evaluation using cartesian-to-spherical transformations:

| Function | Purpose | Key Features |
|----------|---------|--------------|
| `solid_harmonic_from_cart` | Cartesian → spherical conversion | Numerically stable, vectorized |
| `cartesian_product` | Cartesian polynomial products | Efficient mesh generation |
| `full_cart2sph` | Complete transformation matrix | Handles symmetry averaging |
| `grad_solid_harmonic` | Gradient evaluation | Analytical derivatives |

**Sources**: [ferminet/utils/gto.py:137-162](), [ferminet/utils/gto.py:165-201]()

## System Integration

### Advanced Features in Training Pipeline

```mermaid
graph TD
    subgraph "Configuration Layer"
        BaseConfig["base_config.default"]
        PBCConfig["PBC configuration<br/>lattice, kpoints"]
        ExcitedConfig["Excited states config<br/>states, observables"]
        SCFConfig["SCF configuration<br/>basis, pretraining"]
    end
    
    subgraph "Feature Processing"
        StandardFeats["Standard Features<br/>networks.make_fermi_net"]
        PBCFeats["PBC Features<br/>make_pbc_feature_layer"]
        PBCEnvelope["PBC Envelope<br/>make_multiwave_envelope"]
    end
    
    subgraph "Training Integration"
        Pretraining["SCF Pretraining<br/>scf.eval_orbitals"]
        VMCLoss["VMC Loss Function<br/>Multiple states"]
        Observables["Observable Calculation<br/>S², dipole, density"]
    end
    
    subgraph "Specialized Outputs"
        GroundState["Ground State Energy"]
        ExcitedStates["Excited State Energies"]
        TransitionProps["Transition Properties"]
        PeriodicProps["Periodic System Properties"]
    end
    
    BaseConfig --> StandardFeats
    PBCConfig --> PBCFeats
    PBCConfig --> PBCEnvelope
    ExcitedConfig --> VMCLoss
    SCFConfig --> Pretraining
    
    StandardFeats --> VMCLoss
    PBCFeats --> VMCLoss
    PBCEnvelope --> VMCLoss
    Pretraining --> VMCLoss
    
    VMCLoss --> GroundState
    VMCLoss --> ExcitedStates
    Observables --> TransitionProps
    PBCFeats --> PeriodicProps
```

The advanced features integrate seamlessly with the core training pipeline through modular component design, allowing combinations like PBC excited states calculations or SCF-pretrained periodic systems.

**Sources**: [ferminet/pbc/feature_layer.py:46-110](), [ferminet/utils/scf.py:128-183](), [ferminet/configs/li_excited.py:64-81]()

### Testing and Validation

The advanced features include comprehensive testing frameworks to ensure correctness:

- **GTO Tests**: Comparison with PySCF reference implementations for orbital evaluation accuracy
- **PBC Tests**: Validation of periodic distance calculations and lattice transformations  
- **Excited States Tests**: Verification of state orthogonality and observable calculations
- **SCF Integration Tests**: Consistency checks between PySCF and JAX implementations

**Sources**: [ferminet/utils/tests/gto_test.py:36-50]()

---

