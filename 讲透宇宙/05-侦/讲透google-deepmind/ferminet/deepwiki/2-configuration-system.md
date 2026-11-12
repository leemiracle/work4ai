<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ferminet · page 2 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ferminet/base_config.py](ferminet/base_config.py)
- [ferminet/configs/atom.py](ferminet/configs/atom.py)

</details>



The Configuration System provides a centralized framework for managing all parameters, hyperparameters, and system definitions required for FermiNet calculations. It uses `ml_collections.ConfigDict` to create hierarchical, type-safe configuration objects that control every aspect of neural network training, physics calculations, and system behavior.

For information about the core training pipeline that consumes these configurations, see [Core Training Pipeline](#3). For details about specific system definitions and molecular setups, see [System Configurations](#2.2).

## Configuration Architecture

The configuration system follows a hierarchical structure where a base configuration provides defaults that can be overridden by system-specific configurations and command-line flags.

```mermaid
graph TD
    BaseConfig["base_config.default()"]
    SystemConfigs["System-Specific Configs<br/>configs/atom.py<br/>configs/heg.py"]
    UserConfig["User Config Files<br/>Custom get_config()"]
    CLIFlags["Command Line Flags<br/>--config.batch_size 256"]
    
    ResolveFunc["base_config.resolve()"]
    FinalConfig["Resolved ConfigDict"]
    
    TrainFunc["train.train()"]
    NetworkFactory["networks.make_fermi_net"]
    LossFactory["loss.make_loss"]
    MCMCFactory["mcmc.make_mcmc_step"]
    
    BaseConfig --> SystemConfigs
    BaseConfig --> UserConfig
    SystemConfigs --> ResolveFunc
    UserConfig --> ResolveFunc
    CLIFlags --> ResolveFunc
    
    ResolveFunc --> FinalConfig
    
    FinalConfig --> TrainFunc
    FinalConfig --> NetworkFactory
    FinalConfig --> LossFactory
    FinalConfig --> MCMCFactory
```

**Sources:** [ferminet/base_config.py:36-325](), [ferminet/configs/atom.py:64-76](), [README.md:49-66]()

## Base Configuration Structure

The base configuration is defined in `base_config.default()` and contains six major sections that control different aspects of the system:

```mermaid
graph TB
    subgraph ConfigDict["ml_collections.ConfigDict"]
        BatchSize["batch_size: 4096"]
        ConfigModule["config_module: __name__"]
        
        subgraph Optim["optim"]
            Objective["objective: 'vmc'"]
            Iterations["iterations: 1000000"]
            Optimizer["optimizer: 'kfac'"]
            LR["lr: {rate, decay, delay}"]
            KFAC["kfac: {damping, cov_ema_decay, ...}"]
        end
        
        subgraph System["system"]
            SystemType["type: MOLECULE.value"]
            Molecule["molecule: placeholder(list)"]
            Electrons["electrons: tuple()"]
            States["states: 0"]
            PP["pp: {type, basis, symbols}"]
        end
        
        subgraph Network["network"]
            NetworkType["network_type: 'ferminet'"]
            FermiNetCfg["ferminet: {hidden_dims, ...}"]
            PsiFormerCfg["psiformer: {num_layers, ...}"]
            Determinants["determinants: 16"]
            Jastrow["jastrow: 'default'"]
        end
        
        subgraph MCMC["mcmc"]
            BurnIn["burn_in: 100"]
            Steps["steps: 10"]
            MoveWidth["move_width: 0.02"]
        end
        
        subgraph Log["log"]
            StatsFreq["stats_frequency: 1"]
            SaveFreq["save_frequency: 10.0"]
            SavePath["save_path: ''"]
        end
        
        subgraph Observables["observables"]
            S2["s2: False"]
            Density["density: False"]
            Dipole["dipole: False"]
        end
    end
```

**Sources:** [ferminet/base_config.py:46-323]()

## Configuration Resolution Process

Configuration resolution transforms user inputs into a complete, validated configuration through the `resolve()` function:

| Phase | Function | Purpose |
|-------|----------|---------|
| 1. Molecule Setup | `cfg.system.set_molecule()` | Execute callable to configure molecular system |
| 2. Reference Resolution | `cfg.copy_and_resolve_references()` | Resolve `ml_collections.FieldReference` values |
| 3. Validation | Implicit type checking | Ensure configuration consistency |

The resolution process handles special cases for nested references in molecular coordinates and system definitions:

```mermaid
graph LR
    UserCfg["User Configuration"]
    SetMol["set_molecule callable"]
    ResolveRefs["copy_and_resolve_references()"]
    FinalCfg["Resolved Configuration"]
    
    UserCfg --> SetMol
    SetMol --> ResolveRefs
    ResolveRefs --> FinalCfg
    
    subgraph Special["Special Handling"]
        MolCoords["Molecule coordinates<br/>FieldReference resolution"]
        FuncName["Function name serialization<br/>for ConfigDict serialization"]
    end
    
    SetMol --> Special
```

**Sources:** [ferminet/base_config.py:328-355]()

## System Type Classification

The configuration system uses the `SystemType` enum to categorize different physical systems:

```python
class SystemType(enum.IntEnum):
  MOLECULE = enum.auto()
```

Currently, only molecular systems are supported, but the enum structure allows for future extensions to other system types like crystalline solids or homogeneous electron gases.

**Sources:** [ferminet/base_config.py:23-34]()

## Configuration Sections Reference

### Optimization Configuration (`cfg.optim`)

Controls training objectives, optimizers, and convergence parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `objective` | `'vmc'` | Loss function type: `'vmc'`, `'wqmc'`, or `'vmc_overlap'` |
| `optimizer` | `'kfac'` | Optimizer: `'adam'`, `'kfac'`, `'lamb'`, or `'none'` |
| `iterations` | `1000000` | Maximum training iterations |
| `lr.rate` | `0.05` | Base learning rate |
| `clip_local_energy` | `5.0` | Energy clipping threshold in standard deviations |

**Sources:** [ferminet/base_config.py:55-123]()

### System Configuration (`cfg.system`)

Defines the physical system being studied:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `molecule` | `placeholder(list)` | List of `system.Atom` objects |
| `electrons` | `tuple()` | `(n_alpha, n_beta)` electron counts |
| `states` | `0` | Number of excited states to compute |
| `use_pp` | `False` | Enable pseudopotentials |

**Sources:** [ferminet/base_config.py:145-194]()

### Network Configuration (`cfg.network`)

Specifies neural network architecture and parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `network_type` | `'ferminet'` | Architecture: `'ferminet'` or `'psiformer'` |
| `determinants` | `16` | Number of Slater determinants |
| `ferminet.hidden_dims` | `((256, 32), ...)` | Layer dimensions for FermiNet |
| `psiformer.num_layers` | `4` | Number of transformer layers |

**Sources:** [ferminet/base_config.py:223-297]()

### MCMC Configuration (`cfg.mcmc`)

Controls Monte Carlo sampling parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `burn_in` | `100` | Burn-in steps after pretraining |
| `steps` | `10` | MCMC steps between network updates |
| `move_width` | `0.02` | Gaussian proposal width |
| `adapt_frequency` | `100` | Steps between move width adaptation |

**Sources:** [ferminet/base_config.py:195-222]()

## Configuration Usage Patterns

The configuration system integrates with the training pipeline through factory functions that consume specific configuration sections:

```mermaid
graph TB
    Config["Resolved ConfigDict"]
    
    subgraph Factories["Factory Functions"]
        NetworkFactory["networks.make_fermi_net<br/>(cfg.network)"]
        LossFactory["loss.make_loss<br/>(cfg.optim.objective)"]
        MCMCFactory["mcmc.make_mcmc_step<br/>(cfg.mcmc)"]
        HamFactory["hamiltonian.local_energy<br/>(cfg.system)"]
    end
    
    subgraph Components["System Components"]
        Network["Neural Network"]
        LossFunc["Loss Function"]
        MCMCStep["MCMC Stepper"]
        Hamiltonian["Hamiltonian"]
    end
    
    Config --> NetworkFactory
    Config --> LossFactory
    Config --> MCMCFactory
    Config --> HamFactory
    
    NetworkFactory --> Network
    LossFactory --> LossFunc
    MCMCFactory --> MCMCStep
    HamFactory --> Hamiltonian
```

**Sources:** [README.md:72-96](), [ferminet/configs/atom.py:64-76]()

---

