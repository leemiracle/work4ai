<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ferminet · page 5 Physics and Mathematics · fetched 2026-10-26 -->

# Physics and Mathematics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ferminet/hamiltonian.py](ferminet/hamiltonian.py)
- [ferminet/mcmc.py](ferminet/mcmc.py)

</details>



## Purpose and Scope

This document covers the quantum mechanical foundations and mathematical methods underlying FermiNet's variational Monte Carlo approach. It focuses on Hamiltonian evaluation, Monte Carlo sampling algorithms, and the mathematical infrastructure for energy calculations. For network architecture details, see [Neural Network Architectures](#4). For observable calculations beyond energy, see [Observables and Density Matrix](#5.3).

## Quantum Mechanical Foundations

FermiNet solves the time-independent Schrödinger equation using variational Monte Carlo (VMC). The core challenge is evaluating the local energy:

```
E_L(R) = (Ĥψ(R)) / ψ(R)
```

where `Ĥ` is the Hamiltonian operator, `ψ(R)` is the neural network wavefunction, and `R` represents electron coordinates.

### Energy Calculation Architecture

```mermaid
graph TD
    WaveFunction["ψ(R)"] --> LocalEnergy["E_L = Ĥψ/ψ"]
    LocalEnergy --> KineticEnergy["T = -½∇²ψ/ψ"]
    LocalEnergy --> PotentialEnergy["V = V_ee + V_en + V_nn"]
    
    KineticEnergy --> LaplacianCalc["local_kinetic_energy()"]
    LaplacianCalc --> DefaultMethod["'default': jvp(grad)"]
    LaplacianCalc --> FolxMethod["'folx': forward_laplacian"]
    
    PotentialEnergy --> ElectronElectron["potential_electron_electron()"]
    PotentialEnergy --> ElectronNuclear["potential_electron_nuclear()"]
    PotentialEnergy --> NuclearNuclear["potential_nuclear_nuclear()"]
    PotentialEnergy --> Pseudopotentials["pp_local + pp_nonlocal"]
    
    LocalEnergy --> TotalEnergy["local_energy()"]
    TotalEnergy --> ExcitedStates["excited_kinetic_energy_matrix()"]
```

Sources: [ferminet/hamiltonian.py:75-158](), [ferminet/hamiltonian.py:319-456]()

The `LocalEnergy` protocol defines the interface for energy evaluation functions, taking network parameters, random key, and MCMC data as inputs. The main implementation is created by the `local_energy` factory function.

### Kinetic Energy Calculation

The kinetic energy operator requires computing the Laplacian of the wavefunction. FermiNet implements two methods:

| Method | Description | Implementation |
|--------|-------------|----------------|
| `'default'` | Uses `jax.grad` and `jax.linearize` for Hessian diagonal | [ferminet/hamiltonian.py:105-140]() |
| `'folx'` | Microsoft's forward-mode automatic differentiation | [ferminet/hamiltonian.py:141-153]() |

The kinetic energy function handles both real and complex wavefunctions, with special handling for phase gradients in the complex case.

### Potential Energy Components

```mermaid
graph LR
    PotentialEnergy["V_total"] --> VEE["V_ee: electron-electron"]
    PotentialEnergy --> VEN["V_en: electron-nuclear"] 
    PotentialEnergy --> VNN["V_nn: nuclear-nuclear"]
    PotentialEnergy --> VPP["V_pp: pseudopotential"]
    
    VEE --> CoulombEE["1/|r_i - r_j|"]
    VEN --> CoulombEN["-Z_A/|r_i - R_A|"]
    VNN --> CoulombNN["Z_A Z_B/|R_A - R_B|"]
    VPP --> PPLocal["pp_local(r_ae)"]
    VPP --> PPNonlocal["pp_nonlocal(...)"]
```

Sources: [ferminet/hamiltonian.py:266-317]()

Each potential component is implemented as a separate function, allowing modular composition. The pseudopotential terms are optional and activated when `pp_symbols` is provided to `local_energy`.

## Monte Carlo Sampling

FermiNet uses Metropolis-Hastings Monte Carlo to sample electron configurations according to the probability distribution `|ψ(R)|²`.

### MCMC Implementation Architecture

```mermaid
graph TD
    MCMCStep["make_mcmc_step()"] --> ChooseUpdate["blocks > 1?"]
    ChooseUpdate -->|Yes| BlockUpdate["mh_block_update()"]
    ChooseUpdate -->|No| AllElectron["mh_update()"]
    
    AllElectron --> ProposalType["atoms provided?"]
    ProposalType -->|No| SymmetricMove["N(0, σ²)"]
    ProposalType -->|Yes| AsymmetricMove["N(0, (h_i σ)²)"]
    
    AsymmetricMove --> HarmonicMean["_harmonic_mean()"]
    HarmonicMean --> ForwardProb["_log_prob_gaussian()"]
    
    BlockUpdate --> BlockProposal["Move electron block i"]
    SymmetricMove --> MHAccept["mh_accept()"]
    ForwardProb --> MHAccept
    BlockProposal --> MHAccept
    
    MHAccept --> AcceptReject["exp(log_ratio) > rand?"]
    AcceptReject --> UpdateConfig["Update positions"]
    AcceptReject --> UpdateAccepts["Update num_accepts"]
```

Sources: [ferminet/mcmc.py:220-284](), [ferminet/mcmc.py:78-148](), [ferminet/mcmc.py:150-218]()

### Move Proposal Strategies

The MCMC implementation supports two move proposal strategies:

1. **Symmetric moves**: Standard Gaussian proposals `N(0, σ²)` when `atoms=None`
2. **Asymmetric moves**: Proposals scaled by harmonic mean of electron-nucleus distances when `atoms` is provided

The asymmetric moves use the harmonic mean function `_harmonic_mean` to calculate distance-dependent step sizes, improving acceptance rates near nuclei.

### Adaptive Step Size Control

```mermaid
graph LR
    PMoveCalc["Calculate pmove"] --> CheckFreq["t % adapt_frequency == 0?"]
    CheckFreq -->|Yes| CheckRange["pmove in [pmove_min, pmove_max]?"]
    CheckRange -->|pmove > 0.55| IncreaseWidth["width *= 1.1"]
    CheckRange -->|pmove < 0.5| DecreaseWidth["width /= 1.1"]
    CheckRange -->|In range| NoChange["width unchanged"]
    CheckFreq -->|No| StoreMove["pmoves[t % freq] = pmove"]
```

Sources: [ferminet/mcmc.py:287-322]()

The `update_mcmc_width` function automatically adjusts the step size to maintain acceptance rates between 50-55%, ensuring efficient sampling.

## Mathematical Methods

### Excited State Calculations

For excited states (`states > 0`), FermiNet computes energy matrices rather than scalar energies:

```mermaid
graph TD
    ExcitedStates["states > 0"] --> StateSpecific["state_specific?"]
    StateSpecific -->|True| DiagonalOnly["Diagonal energies only"]
    StateSpecific -->|False| FullMatrix["Full energy matrix"]
    
    FullMatrix --> PsiMatrix["psi_mat[i,j] = ψ_i(R_j)"]
    FullMatrix --> KineticMatrix["kin_mat[i,j] = (Ĥψ_i)(R_j)"]
    PsiMatrix --> SolveMatrix["solve(psi_mat, hpsi_mat)"]
    KineticMatrix --> SolveMatrix
    SolveMatrix --> TraceEnergy["trace(energy_mat)"]
    
    DiagonalOnly --> FolxOnly["Only folx method supported"]
    FolxOnly --> DiagonalKinetic["diag(kinetic_energy)"]
```

Sources: [ferminet/hamiltonian.py:161-263](), [ferminet/hamiltonian.py:387-438]()

The `excited_kinetic_energy_matrix` function vectorizes the kinetic energy calculation across multiple states, computing the matrix elements needed for the generalized eigenvalue problem.

### Pseudopotential Integration

When pseudopotentials are used (`pp_symbols` provided), the local energy calculation incorporates effective core potentials:

```mermaid
graph LR
    PPCheck["pp_symbols provided?"] -->|Yes| MakePP["make_pp_potential()"]
    PPCheck -->|No| SkipPP["use_pp = False"]
    
    MakePP --> EffectiveCharges["effective_charges"]
    MakePP --> LocalPP["pp_local()"]
    MakePP --> NonlocalPP["pp_nonlocal()"]
    
    EffectiveCharges --> ModifiedCoulomb["Modified V_en"]
    LocalPP --> AdditionalLocal["+ pp_local(r_ae)"]
    NonlocalPP --> NonlocalTerm["+ pp_nonlocal(...)"]
```

Sources: [ferminet/hamiltonian.py:360-376](), [ferminet/hamiltonian.py:447-449]()

The pseudopotential implementation modifies both the nuclear charges and adds local/nonlocal correction terms, enabling accurate treatment of heavy atoms without explicit core electrons.

---

