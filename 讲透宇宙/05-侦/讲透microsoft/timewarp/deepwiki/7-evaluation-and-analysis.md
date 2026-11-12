<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/timewarp · page 7 Evaluation and Analysis · fetched 2026-10-26 -->

# Evaluation and Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [evaluate.py](evaluate.py)
- [evaluate_o2.py](evaluate_o2.py)

</details>



This page provides a comprehensive guide to evaluating trained Timewarp models. It covers the evaluation scripts, metrics, visualizations, and sampling strategies available for assessing model quality and physical accuracy.

For information about training models, see [Training](#5). For details on specific evaluation scripts, see [Sampling Script](#7.1), [Peptide Evaluation](#7.2), [O2 Molecule Evaluation](#7.3), and [Trajectory Exploration](#7.4).

## Overview of the Evaluation System

The Timewarp evaluation system consists of multiple specialized scripts that assess different aspects of model performance. Each script is designed for specific molecular systems and evaluation objectives:

| Script | Primary Purpose | Target Systems | Key Features |
|--------|----------------|----------------|--------------|
| `sample.py` | General visualization and sampling | All systems | Trajectory visualization, energy plots, basic sampling |
| `evaluate.py` | Comprehensive peptide evaluation | Di-peptides, Tetra-peptides | Ramachandran plots, internal coordinates, Metropolis-Hastings sampling |
| `evaluate_o2.py` | O2 molecule evaluation | O2, O2-CoM datasets | Bond length distributions, KS tests, harmonic oscillator comparison |
| `exploration.py` | Long trajectory generation | All systems | Extended sampling with energy-based acceptance |

All evaluation scripts share common functionality: they load trained models, sample from the learned conditional distribution `p(y|x)`, compare predictions against OpenMM ground truth simulations, and generate visualizations to assess physical accuracy.

Sources: [README.md:29-74](), [evaluate.py:1-47](), [evaluate_o2.py:1-28]()

## Evaluation Workflow

The following diagram illustrates the standard evaluation workflow used across all evaluation scripts:

```mermaid
graph TB
    subgraph Input["Input Phase"]
        ModelPath["Model Path<br/>best_model.pt"]
        DataDir["Data Directory<br/>PDB + NPZ files"]
        Args["Command Arguments<br/>--num_samples<br/>--protein<br/>--output_dir"]
    end
    
    subgraph Loading["Loading Phase"]
        LoadModel["load_model()<br/>or load_model_and_config()"]
        LoadConfig["TrainingConfig<br/>from checkpoint"]
        LoadDataset["RawMolDynDataset<br/>make_iterator()"]
        CreateBatches["moldyn_dense_collate_fn<br/>SparseMolDynBatch or<br/>DenseMolDynBatch"]
    end
    
    subgraph OpenMMSetup["OpenMM Setup"]
        SimEnv["get_simulation_environment()<br/>or create_o2_system()"]
        PotEnergy["OpenmmPotentialEnergyTorch<br/>Energy evaluator"]
        Masses["Extract particle masses<br/>system.getParticleMass()"]
    end
    
    subgraph Sampling["Sampling Phase"]
        SampleBatches["sample_on_batches()<br/>Conditional on dataset"]
        SampleSingle["sample_on_single_conditional()<br/>Fixed conditioning state"]
        SampleModel["sample_with_model()<br/>MCMC with MH acceptance"]
    end
    
    subgraph Analysis["Analysis Phase"]
        Internal["compute_internal_coordinates()<br/>Bonds, angles, torsions"]
        Energy["Compute energies<br/>Potential + Kinetic"]
        KSTest["Statistical tests<br/>ks_2samp(), ks_1samp()"]
    end
    
    subgraph Visualization["Visualization Phase"]
        Rama["plot_ramachandran()<br/>Dihedral angle plots"]
        Bonds["plot_bonds()<br/>Bond length distributions"]
        EnergyPlots["plot_energy()<br/>Energy distributions"]
        Marginal["plot_marginal_distribution()<br/>Position/velocity distributions"]
        ChainStats["visualize(chain_stats)<br/>MCMC diagnostics"]
    end
    
    subgraph Output["Output Phase"]
        Figures["PNG figures<br/>Plots and histograms"]
        Stats["Pickle files<br/>chain_stats.pkl"]
        Metrics["Console output<br/>Acceptance rates<br/>KS statistics"]
    end
    
    ModelPath --> LoadModel
    DataDir --> LoadDataset
    Args --> LoadModel
    Args --> LoadDataset
    
    LoadModel --> LoadConfig
    LoadConfig --> SimEnv
    LoadDataset --> CreateBatches
    
    SimEnv --> PotEnergy
    SimEnv --> Masses
    
    CreateBatches --> SampleBatches
    CreateBatches --> SampleSingle
    CreateBatches --> SampleModel
    
    LoadModel --> SampleBatches
    LoadModel --> SampleSingle
    LoadModel --> SampleModel
    
    PotEnergy --> SampleModel
    Masses --> SampleModel
    
    SampleBatches --> Internal
    SampleSingle --> Internal
    SampleModel --> Internal
    
    SampleBatches --> Energy
    SampleSingle --> Energy
    SampleModel --> Energy
    
    Energy --> KSTest
    
    Internal --> Rama
    Internal --> Bonds
    Energy --> EnergyPlots
    SampleBatches --> Marginal
    SampleModel --> ChainStats
    
    Rama --> Figures
    Bonds --> Figures
    EnergyPlots --> Figures
    Marginal --> Figures
    ChainStats --> Figures
    
    SampleModel --> Stats
    KSTest --> Metrics
    SampleModel --> Metrics
```

**Evaluation Workflow Phases**

The evaluation process follows five distinct phases:

1. **Loading Phase**: Model checkpoints and datasets are loaded. The `load_model_and_config()` function [evaluate.py:49-91]() retrieves both the model state and its configuration. Datasets are created using `RawMolDynDataset` and collated into batches.

2. **OpenMM Setup**: A simulation environment is configured to provide ground truth physics. For peptides, `get_simulation_environment()` [evaluate.py:292]() creates the OpenMM system. For O2 molecules, `create_o2_system()` [evaluate_o2.py:98]() is used. The `OpenmmPotentialEnergyTorch` wrapper [evaluate.py:296-301]() enables efficient energy evaluation on GPU.

3. **Sampling Phase**: Three sampling modes are available:
   - `sample_on_batches()` [evaluate.py:367-375](): Samples from `p(y|x)` for each conditioning state in the dataset
   - `sample_on_single_conditional()` [evaluate.py:576-584](): Samples multiple times from a fixed conditioning state
   - `sample_with_model()` [evaluate.py:680-697](): Generates long trajectories using MCMC with optional Metropolis-Hastings correction

4. **Analysis Phase**: Predictions are analyzed using:
   - Internal coordinates (bonds, angles, torsions) via `compute_internal_coordinates()` [evaluate.py:334-336]()
   - Energy calculations for potential and kinetic energy [evaluate.py:347-349]()
   - Statistical tests like Kolmogorov-Smirnov to compare distributions [evaluate_o2.py:152]()

5. **Visualization Phase**: Results are visualized through multiple plot types:
   - Ramachandran plots for dihedral angles [evaluate.py:333-344]()
   - Bond length distributions [evaluate.py:495-506]()
   - Energy distributions [evaluate.py:542-559]()
   - Marginal position/velocity distributions [evaluate.py:382-394]()
   - MCMC chain statistics [evaluate.py:759-773]()

Sources: [evaluate.py:49-91](), [evaluate.py:292-301](), [evaluate.py:367-375](), [evaluate.py:680-697]()

## Model and Configuration Loading

The evaluation scripts use a consistent approach to load trained models and their configurations:

```mermaid
graph LR
    subgraph Input
        ModelPath["Model Path<br/>Directory or .pt file"]
        ConfigPath["Optional Config Path<br/>Override checkpoint config"]
    end
    
    subgraph Loading["load_model_and_config()"]
        CheckType["Check if directory<br/>or file"]
        GlobPt["glob_only()<br/>Find *.pt in descendants"]
        LoadCheckpoint["torch.load()<br/>Load checkpoint"]
        ExtractConfig["Extract TrainingConfig<br/>from checkpoint"]
        LoadStateDict["load_model_state_dict()<br/>Load weights"]
    end
    
    subgraph ModelConstruction
        Constructor["model_constructor()<br/>Build model from config"]
        LossWrapper["LossWrapper<br/>Wrap with loss"]
        ToDevice["model.to(device)<br/>Move to GPU/CPU"]
    end
    
    subgraph Output
        Model["Loaded Model<br/>Ready for evaluation"]
        Config["TrainingConfig<br/>step_width, dataset, etc."]
    end
    
    ModelPath --> CheckType
    ConfigPath --> CheckType
    
    CheckType --> GlobPt
    GlobPt --> LoadCheckpoint
    LoadCheckpoint --> ExtractConfig
    
    ExtractConfig --> Constructor
    Constructor --> LossWrapper
    LossWrapper --> LoadStateDict
    LoadStateDict --> ToDevice
    
    ToDevice --> Model
    ExtractConfig --> Config
```

**Key Loading Functions**

The `load_model_and_config()` function [evaluate.py:49-91]() handles two loading scenarios:

1. **Standard Loading** (no `config_path` specified): Loads the complete checkpoint including both model state and configuration [evaluate.py:82-89](). This is the typical case.

2. **Config Override** (with `config_path`): Loads configuration from a separate file while using weights from the checkpoint [evaluate.py:72-78](). This is useful if the checkpoint's config is corrupted or needs modification.

The function automatically detects whether `model_path` is a file or directory. When given a directory, it uses `glob_only()` [evaluate.py:85]() to search for checkpoint files in descendant directories, supporting both standard and DeepSpeed training runs.

Sources: [evaluate.py:49-91](), [evaluate.py:82-89]()

## Evaluation Modes and Sampling Strategies

The evaluation system supports three primary sampling modes, each serving different evaluation purposes:

### Sampling Mode Comparison

| Mode | Function | Purpose | Key Parameters | Output |
|------|----------|---------|----------------|--------|
| **Conditional on Dataset** | `sample_on_batches()` | Evaluate conditional distribution accuracy | `batches`, `model`, `device` | Predictions for each data point |
| **Fixed Conditioning** | `sample_on_single_conditional()` | Analyze single conditional distribution | `batch`, `num_samples`, `simulation` | Multiple samples from p(y\|x₀) |
| **MCMC Sampling** | `sample_with_model()` | Generate long trajectories | `mh`, `num_proposal_steps`, `openmm_on_*` | Markov chain samples |

### Conditional Sampling on Dataset

This mode evaluates how well the model captures the conditional distribution by sampling from `p(y|x)` for each conditioning state in the dataset:

```mermaid
graph TB
    subgraph Inputs
        Batches["List of batches<br/>from dataset"]
        Model["Trained model<br/>p(y|x)"]
        PotEnergy["OpenmmPotentialEnergyTorch"]
    end
    
    subgraph Processing["sample_on_batches()"]
        Iterate["For each batch"]
        Sample["model.sample()<br/>Generate y ~ p(y|x)"]
        ComputeLL["model.log_prob()<br/>Forward/reverse likelihood"]
        ComputeAccept["Metropolis-Hastings<br/>acceptance probability"]
        Transform["Apply data augmentation<br/>if configured"]
    end
    
    subgraph Outputs
        Coords["y_coords_model<br/>Predicted positions"]
        Velocs["y_velocs_model<br/>Predicted velocities"]
        LLForward["ll_forward<br/>Log p(y|x)"]
        LLReverse["ll_reverse<br/>Log p(x|y)"]
        Acceptance["acceptance<br/>MH probability"]
    end
    
    Batches --> Iterate
    Model --> Sample
    Iterate --> Sample
    
    Sample --> ComputeLL
    Sample --> ComputeAccept
    PotEnergy --> ComputeAccept
    
    ComputeLL --> Transform
    ComputeAccept --> Transform
    
    Transform --> Coords
    Transform --> Velocs
    Transform --> LLForward
    Transform --> LLReverse
    Transform --> Acceptance
```

The `sample_on_batches()` function [evaluate.py:367-375]() processes each batch independently and computes:
- Forward log-likelihood `log p(y|x)` [evaluate.py:363]()
- Reverse log-likelihood `log p(x|y)` [evaluate.py:364]()
- Metropolis-Hastings acceptance probability [evaluate.py:366]()

This mode is enabled by default in `evaluate.py` and can be disabled with `--not-on-data` [evaluate.py:145-147]().

### Fixed Conditioning Sampling

This mode samples multiple times from the same conditioning state to visualize the full conditional distribution:

```mermaid
graph TB
    subgraph Inputs
        SingleBatch["Single batch<br/>Initial state x₀"]
        NumSamples["num_samples<br/>Number of samples to draw"]
        Simulation["OpenMM simulation"]
    end
    
    subgraph ModelSampling["Model Sampling"]
        Repeat["Repeat num_samples times"]
        SampleModel["model.sample(batch)<br/>y ~ p(y|x₀)"]
        Collect["Collect all samples"]
    end
    
    subgraph OpenMMSampling["OpenMM Ground Truth"]
        SimRepeat["Repeat num_samples times"]
        ResetState["Set positions/velocities<br/>to x₀"]
        SimStep["simulation.step(step_width)<br/>Integrate forward"]
        GetState["getState()<br/>Extract y coordinates"]
        SimCollect["Collect all samples"]
    end
    
    subgraph Outputs
        ModelSamples["y_coords_model<br/>y_velocs_model<br/>[num_samples, atoms, 3]"]
        OpenMMSamples["traj_coords<br/>traj_velocs<br/>[num_samples, atoms, 3]"]
        Conditioning["traj_coords_conditioning<br/>Repeated x₀"]
    end
    
    SingleBatch --> Repeat
    NumSamples --> Repeat
    Repeat --> SampleModel
    SampleModel --> Collect
    Collect --> ModelSamples
    
    SingleBatch --> SimRepeat
    Simulation --> ResetState
    SimRepeat --> ResetState
    ResetState --> SimStep
    SimStep --> GetState
    GetState --> SimCollect
    SimCollect --> OpenMMSamples
    
    SingleBatch --> Conditioning
```

The `sample_on_single_conditional()` function [evaluate.py:576-584]() is useful for:
- Visualizing the spread of the conditional distribution [evaluate.py:591-606]()
- Comparing model variance to OpenMM variance
- Creating detailed plots centered on a single initial state

This mode is enabled by default unless `--no-conditional` is specified [evaluate.py:140-143]().

### MCMC Sampling with Metropolis-Hastings

This mode generates long trajectories by iteratively sampling from the model and optionally applying Metropolis-Hastings acceptance:

```mermaid
graph TB
    subgraph Initialization
        InitBatch["Initial batch<br/>or random state"]
        InitCoords["current_coords<br/>current_velocs"]
    end
    
    subgraph MCMCLoop["MCMC Iteration Loop"]
        ProposeStep["Propose step:<br/>model.sample(current_state)<br/>→ proposed_state"]
        
        ComputeEnergies["Compute energies:<br/>E(current), E(proposed)"]
        
        ComputeProbs["Compute probabilities:<br/>log p(proposed|current)<br/>log p(current|proposed)"]
        
        MHRatio["Metropolis-Hastings ratio:<br/>α = min(1, exp(ΔLL - ΔE))"]
        
        AcceptReject["Accept with prob α:<br/>if accept: current ← proposed<br/>else: keep current"]
        
        OptionalOpenMM["Optional OpenMM steps:<br/>--sample--openmm-on-current<br/>--sample--openmm-on-proposal"]
        
        RecordStats["Record to chain_stats:<br/>acceptance, energies,<br/>transition_probs"]
    end
    
    subgraph ParallelProposals["Parallel Proposal Mode"]
        NumSteps["--sample--num-proposal-steps<br/>Generate N proposals in parallel"]
        FindFirst["Find first accepted proposal"]
        AddAll["Add all states until acceptance<br/>to Markov chain"]
    end
    
    subgraph Outputs
        FinalCoords["sampled_coords<br/>[num_samples, atoms, 3]"]
        ChainStats["chain_stats<br/>acceptance, energies_pot,<br/>energies_kin, transition_probs"]
    end
    
    InitBatch --> InitCoords
    InitCoords --> ProposeStep
    
    ProposeStep --> ComputeEnergies
    ProposeStep --> ComputeProbs
    
    ComputeEnergies --> MHRatio
    ComputeProbs --> MHRatio
    
    MHRatio --> AcceptReject
    AcceptReject --> OptionalOpenMM
    OptionalOpenMM --> RecordStats
    
    NumSteps --> ProposeStep
    FindFirst --> AcceptReject
    AddAll --> RecordStats
    
    RecordStats --> ProposeStep
    RecordStats --> FinalCoords
    RecordStats --> ChainStats
```

The `sample_with_model()` function [evaluate.py:680-697]() provides several MCMC options:

**Metropolis-Hastings Correction** (`--mh` flag [evaluate.py:130-133]()):
- Computes acceptance probability based on energy changes and likelihood ratios
- Ensures detailed balance and produces physically valid samples
- Essential for accurate equilibrium sampling

**Parallel Proposals** (`--sample--num-proposal-steps` [evaluate.py:210-214]()):
- Generates multiple proposals per iteration in parallel [evaluate.py:695]()
- All states until the first accepted one are added to the chain
- Significantly speeds up sampling when acceptance rates are low

**Adaptive Parallelism** (`--sample--adaptive-parallelism` [evaluate.py:215-219]()):
- Dynamically adjusts number of parallel proposals [evaluate.py:696]()
- Based on smoothed average of recent acceptance rates
- Balances computational cost with sampling efficiency

**OpenMM Integration** (`--sample--openmm-on-current` or `--sample--openmm-on-proposal` [evaluate.py:194-208]()):
- Performs OpenMM simulation steps on current or proposed states [evaluate.py:692-694]()
- Useful for hybrid sampling strategies
- Number of steps controlled by `--sample--num-openmm-steps` [evaluate.py:204-208]()

Sources: [evaluate.py:367-375](), [evaluate.py:576-584](), [evaluate.py:680-697]()

## Key Metrics and Statistical Tests

The evaluation system computes various metrics to quantify model performance and physical accuracy:

### Energy Metrics

| Metric | Computation | Physical Interpretation |
|--------|-------------|------------------------|
| **Potential Energy** | `OpenmmPotentialEnergyTorch(coords)` | Force field energy (kJ/mol) |
| **Kinetic Energy** | `compute_kinetic_energy(velocs, masses)` | 0.5 * m * v² summed over atoms |
| **Total Energy** | Potential + Kinetic | Conserved in NVE ensemble |
| **ΔE (Energy Change)** | E(proposed) - E(current) | Used in MH acceptance |

**Energy Distribution Comparison**: The `plot_energy()` function [evaluate.py:542-559]() creates histograms comparing model-generated energies against OpenMM ground truth. For physically accurate models, these distributions should closely overlap.

### Internal Coordinate Metrics

Internal coordinates provide geometry-based validation:

```mermaid
graph LR
    subgraph Coordinates["Cartesian Coordinates"]
        ModelCoords["y_coords_model<br/>[samples, atoms, 3]"]
        OpenMMCoords["traj_coords<br/>[samples, atoms, 3]"]
    end
    
    subgraph Computation["compute_internal_coordinates()"]
        LoadPDB["Load PDB topology"]
        ExtractBonds["Extract bonds from<br/>adjacency list"]
        ComputeDistances["Compute bond lengths:<br/>||atom_i - atom_j||"]
        ComputeDihedrals["Compute dihedral angles:<br/>φ, ψ torsions"]
    end
    
    subgraph InternalCoords["Internal Coordinates"]
        Bonds["bonds<br/>[samples, num_bonds]"]
        Torsions["torsions<br/>[samples, num_torsions]"]
    end
    
    subgraph Visualization
        BondPlots["plot_bonds()<br/>Bond length distributions"]
        RamaPlots["plot_ramachandran()<br/>Dihedral angle heatmaps"]
    end
    
    ModelCoords --> LoadPDB
    OpenMMCoords --> LoadPDB
    LoadPDB --> ExtractBonds
    ExtractBonds --> ComputeDistances
    ExtractBonds --> ComputeDihedrals
    
    ComputeDistances --> Bonds
    ComputeDihedrals --> Torsions
    
    Bonds --> BondPlots
    Torsions --> RamaPlots
```

The `compute_internal_coordinates()` function [evaluate.py:488-494]() extracts:
- **Bond lengths**: Distances between bonded atoms, should match equilibrium values
- **Dihedral angles**: Backbone φ and ψ angles for peptides, visualized in Ramachandran plots

### Statistical Tests

**Kolmogorov-Smirnov (KS) Test**: Quantifies the difference between two probability distributions:

For O2 molecules [evaluate_o2.py:152]():
```python
ks_result, p_value = ks_2samp(bond_length, bond_length_openmm)
```
- Tests whether model and OpenMM bond length distributions are statistically similar
- Low p-values indicate significant distribution differences
- KS statistic measures maximum distance between cumulative distributions

For velocity distributions [evaluate.py:722-725]():
```python
ks = scipy_stats.ks_1samp(
    2 * chain_stats.energies_kin, 
    scipy_stats.chi2(df=num_atoms * 3).cdf
)
```
- Tests if velocity norms follow the expected χ² distribution
- Validates Maxwell-Boltzmann velocity distribution
- Kinetic energies should follow χ²(3N) distribution at equilibrium

### MCMC Diagnostics

The `ChainStats` object [evaluate.py:748-750]() tracks sampling quality:

| Diagnostic | Interpretation | Visualization |
|------------|----------------|---------------|
| **Acceptance Rate** | Fraction of proposals accepted | Should be 20-50% for efficient sampling |
| **Energy Trajectories** | E_pot and E_kin over time | Should fluctuate around equilibrium values |
| **Transition Probabilities** | Forward and reverse log-likelihoods | Indicates model reversibility quality |
| **Energy Deltas** | ΔE_pot and ΔE_kin | Shows energy barriers encountered |

The `visualize()` function [evaluate.py:759-773]() generates diagnostic plots showing these metrics over the MCMC trajectory.

Sources: [evaluate.py:347-349](), [evaluate.py:488-494](), [evaluate.py:542-559](), [evaluate_o2.py:152](), [evaluate.py:722-725](), [evaluate.py:748-773]()

## Visualization Outputs

The evaluation system generates comprehensive visualizations across multiple plot types:

### Ramachandran Plots

Ramachandran plots visualize the distribution of backbone dihedral angles (φ, ψ) in peptides:

```mermaid
graph LR
    subgraph Input
        Torsions["torsions<br/>[samples, num_torsions]<br/>φ and ψ angles"]
    end
    
    subgraph Processing["plot_ramachandran()"]
        Extract["Extract φ (phi)<br/>and ψ (psi) pairs"]
        Create2DHist["Create 2D histogram<br/>bins × bins grid"]
        Normalize["Normalize to<br/>probability density"]
    end
    
    subgraph Output
        HeatmapPlot["Heatmap visualization<br/>φ on x-axis<br/>ψ on y-axis<br/>Color = probability"]
        SaveFig["Save as PNG<br/>protein_name_title_<br/>ramachandran_step_width.png"]
    end
    
    Torsions --> Extract
    Extract --> Create2DHist
    Create2DHist --> Normalize
    Normalize --> HeatmapPlot
    HeatmapPlot --> SaveFig
```

The `plot_ramachandran()` function [evaluate.py:333-344]() creates heatmaps showing:
- Favored regions of conformational space (α-helix, β-sheet)
- Agreement between model and OpenMM distributions
- Proper sampling of rare conformations

Ramachandran plots are generated for three scenarios [evaluate.py:509-525]():
1. **Model samples**: Conditioned on dataset states
2. **OpenMM samples**: Ground truth from simulation
3. **Model MCMC samples**: Long trajectory sampling [evaluate.py:838-846]()

### Bond Length Distributions

Bond length plots compare geometric accuracy between model and OpenMM:

The `plot_bonds()` function [evaluate.py:495-506]() creates histograms for each bond type showing:
- Distribution overlap between model and OpenMM [evaluate.py:620-633]()
- Deviation from equilibrium bond lengths
- Bond-specific errors

For O2 molecules, bond lengths are compared against the theoretical harmonic oscillator distribution [evaluate_o2.py:129-148]().

### Energy Distributions

Energy plots validate thermodynamic properties:

The `plot_energy()` function [evaluate.py:542-559]() generates:
- **Potential energy histograms**: Should match Boltzmann distribution shape [evaluate.py:777-814]()
- **Kinetic energy histograms**: Should follow Maxwell-Boltzmann distribution [evaluate.py:551-559]()
- Overlay of model and OpenMM distributions for direct comparison

### Marginal Position and Velocity Distributions

The `plot_marginal_distribution()` function [evaluate.py:382-394]() creates:
- Per-atom position change distributions (Δx = y - x)
- Per-atom velocity distributions
- Comparison between model, OpenMM, and optionally dataset background distributions [evaluate.py:604]()

### MCMC Chain Diagnostics

For MCMC sampling, the `visualize()` function [evaluate.py:759-773]() produces time-series plots:

| Plot Type | Content | Purpose |
|-----------|---------|---------|
| **Acceptance Trace** | Acceptance rate over iterations | Check for consistent sampling |
| **Energy Traces** | E_pot and E_kin over time | Verify equilibration |
| **Transition Probabilities** | log p(y\|x) and log p(x\|y) | Assess model reversibility |
| **Energy Deltas** | ΔE_pot and ΔE_kin distributions | Identify energy barriers |

The `visualize()` function can display either absolute values or deltas (changes from previous state) using the `delta=True` parameter [evaluate.py:764-773]().

### Output Organization

All visualizations are saved to the output directory with systematic naming:

```
output_dir/
  ├── {protein}_sample_on_data_marginal_distribution_{step_width}.png
  ├── {protein}_sample_on_data_correlation_openmm_{step_width}.png
  ├── {protein}_sample_on_data_ramachandran_{step_width}.png
  ├── {protein}_sample_on_data_bonds_{step_width}.png
  ├── {protein}_sample_on_samples_potential_energy_distribution_step_width_{step_width}.png
  ├── {protein}_chain_stats.pkl  # Serialized ChainStats object
  ├── {protein}_chain_stats.png  # MCMC diagnostics
  └── ...
```

The naming convention includes:
- Protein/molecule identifier
- Evaluation mode (`sample_on_data`, `sample_on_conditioning`, `sample_on_samples`)
- Plot type (`ramachandran`, `bonds`, `energy`, etc.)
- Step width parameter

Sources: [evaluate.py:333-344](), [evaluate.py:495-506](), [evaluate.py:542-559](), [evaluate.py:382-394](), [evaluate.py:759-773]()

## Command-Line Interface

The evaluation scripts provide extensive command-line options for customization:

### Common Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--savefile` | str | Required | Path to trained model checkpoint (best_model.pt) |
| `--data_dir` | str | Required | Path to directory containing PDB and NPZ files |
| `--protein` | str | All proteins | Specific protein(s) to evaluate (space-separated list) |
| `--num_samples` | int | 1000 | Number of samples to generate |
| `--output_dir` | str | Auto-generated | Directory to save output figures and statistics |
| `--device` | str | Auto (CUDA/CPU) | Device to use for evaluation |
| `--seed` | int | 42 | Random seed for reproducibility |

### Peptide Evaluation Arguments (`evaluate.py`)

**Sampling Control**:
- `--mh`: Enable Metropolis-Hastings correction [evaluate.py:130-133]()
- `--no-sample`: Skip MCMC sampling phase [evaluate.py:135-138]()
- `--no-conditional`: Skip fixed conditioning evaluation [evaluate.py:140-143]()
- `--not-on-data`: Skip conditional sampling on dataset [evaluate.py:145-147]()

**Velocity Options**:
- `--random-velocities`: Treat velocities as isotropic Gaussians [evaluate.py:161-164]()
- `--resample-velocities`: Resample velocities at each MCMC iteration [evaluate.py:166-169]()

**MCMC Advanced Options**:
- `--sample--num-proposal-steps`: Number of parallel proposals per iteration [evaluate.py:210-214]()
- `--sample--adaptive-parallelism`: Adaptively adjust proposal count [evaluate.py:215-219]()
- `--sample--openmm-on-current`: Run OpenMM on current state [evaluate.py:194-197]()
- `--sample--openmm-on-proposal`: Run OpenMM on proposed state [evaluate.py:198-202]()
- `--sample--num-openmm-steps`: OpenMM steps per iteration [evaluate.py:204-208]()
- `--sample--initialize-randomly`: Random initialization instead of data [evaluate.py:188-192]()

### O2 Evaluation Arguments (`evaluate_o2.py`)

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--sample` | bool | False | Whether to perform MCMC sampling with model |

### Example Commands

**Basic peptide evaluation** [README.md:53-60]():
```bash
python evaluate.py \
    path-to-model-output-directory/best_model.pt \
    --data_dir path-to-directory-containing-protein-data/ \
    --num_samples 1000 \
    --output_dir path-to-directory-to-save-figures/
```

**MCMC sampling with Metropolis-Hastings** [README.md:64-72]():
```bash
python evaluate.py \
    path-to-model-output-directory/best_model.pt \
    --data_dir path-to-directory-containing-protein-data/ \
    --num_samples 1000 \
    --output_dir path-to-directory-to-save-figures/ \
    --mh \
    --sample--num-proposal-steps 1000
```

**O2 molecule evaluation** [README.md:43-50]():
```bash
python evaluate_o2.py \
    --savefile path-to-model-output-directory/best_model.pt \
    --data_dir path-to-directory-containing-protein-data/ \
    --num_samples 20 \
    --output_dir path-to-directory-to-save-figures/ \
    --sample True
```

Sources: [README.md:53-72](), [evaluate.py:103-227](), [evaluate_o2.py:31-52]()

## Integration with OpenMM

All evaluation scripts integrate with OpenMM to provide ground truth physics-based comparisons:

```mermaid
graph TB
    subgraph OpenMMSetup["OpenMM Simulation Setup"]
        PDBFile["PDB file<br/>state0pdbpath"]
        Parameters["Force field parameters<br/>alanine-dipeptide"]
        
        CreateSystem["get_simulation_environment()<br/>or create_o2_system()"]
        
        System["OpenMM System<br/>Forces, masses, constraints"]
        Integrator["Integrator<br/>LangevinIntegrator"]
        Platform["Platform selection<br/>CUDA, CPU, Reference"]
    end
    
    subgraph TorchBridge["PyTorch Integration"]
        SystemCopy["system copy"]
        IntegratorCopy["integrator copy"]
        
        Bridge["OpenmmPotentialEnergyTorch<br/>Wrapper class"]
        
        ContextManager["OpenMM Context<br/>on specified platform"]
    end
    
    subgraph EnergyEval["Energy Evaluation"]
        TorchCoords["Coordinates tensor<br/>[batch, atoms, 3]"]
        
        SetPositions["context.setPositions()<br/>Update OpenMM state"]
        GetState["context.getState(getEnergy=True)<br/>Compute potential energy"]
        
        TorchEnergy["Energy tensor<br/>[batch] in kJ/mol"]
    end
    
    subgraph Simulation["Ground Truth Simulation"]
        InitialState["Initial positions/velocities<br/>from batch"]
        
        SetState["context.setPositions()<br/>context.setVelocities()"]
        SimStep["simulation.step(step_width)<br/>Integrate forward"]
        ExtractState["getState(getPositions=True,<br/>getVelocities=True)"]
        
        FinalState["Final state<br/>Ground truth y"]
    end
    
    PDBFile --> CreateSystem
    Parameters --> CreateSystem
    CreateSystem --> System
    CreateSystem --> Integrator
    CreateSystem --> Platform
    
    System --> SystemCopy
    Integrator --> IntegratorCopy
    Platform --> Bridge
    
    SystemCopy --> Bridge
    IntegratorCopy --> Bridge
    Bridge --> ContextManager
    
    TorchCoords --> SetPositions
    ContextManager --> SetPositions
    SetPositions --> GetState
    GetState --> TorchEnergy
    
    InitialState --> SetState
    ContextManager --> SetState
    SetState --> SimStep
    SimStep --> ExtractState
    ExtractState --> FinalState
```

### OpenMM System Creation

For peptides [evaluate.py:290-292]():
```python
simulation = get_simulation_environment(state0pdbpath, parameters)
integrator = get_simulation_environment_integrator(parameters)
system = simulation.system
```

For O2 molecules [evaluate_o2.py:98-101]():
```python
system, topology = create_o2_system()
integrator = mm.LangevinIntegrator(310 * u.kelvin, 1 / u.picosecond, 1 * u.femtosecond)
simulation = mm.app.Simulation(topology, system, integrator)
```

### Energy Computation Bridge

The `OpenmmPotentialEnergyTorch` wrapper [evaluate.py:296-301]() enables efficient GPU-based energy evaluation:

```python
platform, platform_properties = device_to_platform_and_properties(device, num_threads=1)
openmm_potential_energy_torch = OpenmmPotentialEnergyTorch(
    system,
    integrator,
    platform_name=platform,
    platform_properties=platform_properties,
)
```

This wrapper:
- Accepts PyTorch tensors as input
- Returns PyTorch tensors as output
- Maintains gradients if needed
- Runs on the specified platform (CUDA, CPU, etc.)

### Ground Truth Trajectory Generation

For single conditional evaluation [evaluate_o2.py:105-111]():
```python
for _ in range(args.num_samples):
    simulation.context.setPositions(batch.atom_coords.squeeze(0).cpu().numpy())
    simulation.context.setVelocities(batch.atom_velocs.squeeze(0).cpu().numpy())
    simulation.step(step_width)
    state = simulation.context.getState(getPositions=True, getVelocities=True)
    openMM_samples.append(state.getPositions(asNumpy=True)._value)
```

This process:
1. Resets the simulation to the initial state
2. Integrates forward by `step_width` timesteps
3. Extracts the final positions and velocities
4. Repeats to generate multiple independent trajectories from the same starting point

### Mass Extraction

Particle masses are extracted for kinetic energy calculations [evaluate.py:303-305]():
```python
num_atoms = system.getNumParticles()
masses = [system.getParticleMass(i).value_in_unit(u.dalton) for i in range(num_atoms)]
masses = torch.tensor(masses).to(device)
```

These masses are used in:
- `compute_kinetic_energy()` function [evaluate.py:536-539]()
- Metropolis-Hastings acceptance calculations
- Velocity distribution validation

Sources: [evaluate.py:290-305](), [evaluate_o2.py:98-111]()

## Protein Selection and Iteration

The evaluation scripts support flexible protein selection for batch evaluation:

```mermaid
graph TB
    subgraph Input
        ArgProtein["--protein argument<br/>List of protein names<br/>or None"]
        DataDir["--data_dir<br/>Directory with PDB files"]
    end
    
    subgraph Selection["Protein Selection Logic"]
        CheckArg{"args.protein<br/>provided?"}
        UseProvided["Use provided list"]
        ScanDir["list_available_proteins()<br/>Scan data_dir"]
        
        GlobPDB["glob.glob()<br/>**/*-traj-state0.pdb"]
        ExtractNames["Extract protein names<br/>Remove suffix"]
        Sort["Sort alphabetically"]
    end
    
    subgraph Processing
        ShuffleCond{"--shuffle-proteins<br/>flag set?"}
        Shuffle["random.shuffle()<br/>Randomize order"]
        
        Iterate["For each protein<br/>in list"]
    end
    
    subgraph PerProtein["Per-Protein Evaluation"]
        LoadData["Load protein-specific<br/>dataset"]
        CreateSim["Create OpenMM<br/>simulation"]
        RunEval["Run evaluation modes"]
        SaveResults["Save results to<br/>output_dir/protein_*"]
        
        AcceptanceTrack["Track acceptance rate<br/>for final summary"]
    end
    
    ArgProtein --> CheckArg
    DataDir --> CheckArg
    
    CheckArg -->|Yes| UseProvided
    CheckArg -->|No| ScanDir
    
    ScanDir --> GlobPDB
    GlobPDB --> ExtractNames
    ExtractNames --> Sort
    
    UseProvided --> ShuffleCond
    Sort --> ShuffleCond
    
    ShuffleCond -->|Yes| Shuffle
    ShuffleCond -->|No| Iterate
    Shuffle --> Iterate
    
    Iterate --> LoadData
    LoadData --> CreateSim
    CreateSim --> RunEval
    RunEval --> SaveResults
    SaveResults --> AcceptanceTrack
    
    AcceptanceTrack --> Iterate
```

### Protein Discovery

The `list_available_proteins()` function [evaluate.py:94-99]() automatically discovers available proteins:

```python
protein_filenames = glob.glob(
    os.path.join(str(pdb_dir), "**/*-traj-state0.pdb"), recursive=True
)
num_chars_to_drop = len("-traj-state0.pdb")
return sorted([os.path.split(f)[-1][:-num_chars_to_drop] for f in protein_filenames])
```

This searches recursively for all PDB files matching the pattern `*-traj-state0.pdb` and extracts the protein identifiers.

### Protein Loop

The main evaluation loop [evaluate.py:282-288]():

```python
proteins = args.protein if args.protein is not None else list_available_proteins(args.data_dir)
if args.shuffle_proteins:
    random.shuffle(proteins)

average_acceptance_rate_all_proteins = []
for protein in proteins:
    print(f"Running evaluation for {protein}...")
    # ... per-protein evaluation ...
```

**Per-protein execution**:
1. Load protein-specific PDB file [evaluate.py:290]()
2. Create OpenMM simulation environment [evaluate.py:292]()
3. Load trajectory dataset for this protein [evaluate.py:308-312]()
4. Run all enabled evaluation modes
5. Save results with protein name in filename
6. Track acceptance rate for summary statistics [evaluate.py:701]()

### Final Summary

After evaluating all proteins, a summary is generated [evaluate.py:857-864]():

```python
if len(average_acceptance_rate_all_proteins) > 0:
    print(
        f"Average acceptance rate over all: {np.array(average_acceptance_rate_all_proteins).mean()}"
    )
    plt.figure(figsize=(16, 9))
    plt.hist(average_acceptance_rate_all_proteins)
    plt.savefig(os.path.join(output_dir, "acceptance_rate.png"))
```

This provides:
- Mean acceptance rate across all proteins
- Histogram of per-protein acceptance rates
- Saved to `acceptance_rate.png` in output directory

Sources: [evaluate.py:94-99](), [evaluate.py:282-288](), [evaluate.py:857-864]()

## Error Handling and Warnings

The evaluation scripts include several validation checks and warnings:

### Data Availability Warning

If the requested number of samples exceeds available data [evaluate.py:315-321]():

```python
if args.num_samples > len(batches):
    warnings.warn(
        (
            f"The data set consists of only {len(batches)} datapoints."
            f"Hence, some evaluation functions will only use {len(batches)}."
        )
    )
```

This prevents errors when datasets have limited trajectory data.

### Sample Count Recommendation

For O2 evaluation [evaluate_o2.py:83-84]():
```python
if args.num_samples < 10000:
    warnings.warn("It is recommended to use 10000 samples.")
```

Statistical tests require sufficient samples for reliable results.

### Unsupported Dataset Detection

For O2 evaluation script [evaluate_o2.py:66-74]():
```python
if data_set == "O2" or data_set == "O2-CoM":
    protein = "o2"
elif data_set == "AD-1":
    raise ValueError(
        f"So far the evaluation is not implemented for the {data_set} dataset. It is only available for the O2 dataset."
    )
else:
    raise ValueError(...)
```

This ensures the correct evaluation script is used for each dataset type.

### Device Selection

Device selection with fallback [evaluate.py:268-273]():
```python
device = (
    torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if args.device is None
    else torch.device(args.device)
)
print(f"Using device: {device}")
```

Automatically selects CUDA if available, with manual override option.

Sources: [evaluate.py:315-321](), [evaluate_o2.py:83-84](), [evaluate_o2.py:66-74](), [evaluate.py:268-273]()

---

