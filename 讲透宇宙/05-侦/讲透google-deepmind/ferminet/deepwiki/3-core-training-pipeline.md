<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/ferminet · page 3 Core Training Pipeline · fetched 2026-10-26 -->

# Core Training Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ferminet/psiformer.py](ferminet/psiformer.py)
- [ferminet/tests/train_test.py](ferminet/tests/train_test.py)
- [ferminet/train.py](ferminet/train.py)

</details>



## Purpose and Scope

This document covers the core training pipeline in FermiNet, which orchestrates the main training loop that combines Monte Carlo sampling with neural network optimization for variational quantum Monte Carlo (VMC) calculations. The training pipeline coordinates between MCMC sampling, loss evaluation, and parameter optimization to train neural network wavefunctions.

For details about specific network architectures used in training, see [Neural Network Architectures](#4). For information about the physics calculations performed during training, see [Physics and Mathematics](#5). For configuration options that control the training pipeline, see [Configuration System](#2).

## Training Pipeline Overview

The training pipeline follows a standard pattern: initialize electron configurations, perform MCMC sampling to generate new configurations, evaluate the loss function (typically the local energy), compute gradients, and update network parameters. This process repeats for a specified number of iterations.

```mermaid
graph TD
    subgraph "Initialization Phase"
        Config["cfg: ConfigDict<br/>Configuration"]
        InitElectrons["init_electrons()<br/>Initial walker positions"]
        InitNetwork["network.init()<br/>Network parameters"]
        InitOptimizer["optimizer.init()<br/>Optimizer state"]
    end
    
    subgraph "Main Training Loop"
        MCMCStep["mcmc_step()<br/>Sample new configurations"]
        LossEval["evaluate_loss()<br/>Compute local energy"]
        GradCompute["jax.value_and_grad()<br/>Compute gradients"]
        ParamUpdate["optimizer.update()<br/>Update parameters"]
        ObservableCalc["observable_fns<br/>Calculate observables"]
    end
    
    subgraph "Monitoring & Control"
        Checkpoint["checkpoint.save()<br/>Save model state"]
        Logging["writer.write()<br/>Log training metrics"]
        MCMCAdapt["update_mcmc_width()<br/>Adapt step size"]
    end
    
    Config --> InitElectrons
    Config --> InitNetwork
    Config --> InitOptimizer
    
    InitElectrons --> MCMCStep
    InitNetwork --> MCMCStep
    InitOptimizer --> ParamUpdate
    
    MCMCStep --> LossEval
    LossEval --> GradCompute
    GradCompute --> ParamUpdate
    ParamUpdate --> MCMCStep
    
    LossEval --> ObservableCalc
    ParamUpdate --> Checkpoint
    ObservableCalc --> Logging
    MCMCStep --> MCMCAdapt
```

Sources: [ferminet/train.py:389-1070]()

## Main Training Function Architecture

The `train` function in [ferminet/train.py:389-1070]() serves as the main entry point and orchestrates the entire training pipeline. It handles device setup, configuration processing, network construction, and the main training loop.

### Key Training Components

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| **Main Loop** | `train()` function | Coordinates all training components |
| **Step Function** | `Step` protocol | Defines interface for training steps |
| **Optimizer Update** | `OptUpdate` protocol | Defines optimization interface |
| **MCMC Sampling** | `mcmc_step` callable | Generates new electron configurations |
| **Loss Evaluation** | `evaluate_loss` callable | Computes local energy and gradients |

```mermaid
graph LR
    subgraph "Core Protocols"
        StepProtocol["Step Protocol<br/>__call__(data, params, state, key, mcmc_width)"]
        OptUpdateProtocol["OptUpdate Protocol<br/>__call__(params, data, opt_state, key)"]
    end
    
    subgraph "Concrete Implementations"
        TrainingStep["make_training_step()<br/>Standard optimizers"]
        KFACStep["make_kfac_training_step()<br/>KFAC optimizer"]
        OptStep["make_opt_update_step()<br/>Optax optimizers"]
        LossStep["make_loss_step()<br/>Loss evaluation only"]
    end
    
    subgraph "Return Types"
        StepResults["StepResults<br/>(data, params, state, loss, aux_data, pmove)"]
        OptResults["OptUpdateResults<br/>(params, opt_state, loss, aux_data)"]
    end
    
    StepProtocol --> TrainingStep
    StepProtocol --> KFACStep
    OptUpdateProtocol --> OptStep
    OptUpdateProtocol --> LossStep
    
    TrainingStep --> StepResults
    KFACStep --> StepResults
    OptStep --> OptResults
    LossStep --> OptResults
```

Sources: [ferminet/train.py:181-222](), [ferminet/train.py:157-179](), [ferminet/train.py:274-321](), [ferminet/train.py:323-387]()

## Training Step Implementations

The training pipeline supports different step implementations depending on the optimizer type and use case.

### Standard Training Step

The `make_training_step` function creates the training step for most optimizers (Adam, Lamb):

```mermaid
graph TD
    subgraph "make_training_step"
        MCMCLoop["mcmc_step(params, data, key, mcmc_width)<br/>Monte Carlo sampling"]
        OptUpdate["optimizer_step(params, data, state, key)<br/>Loss + gradient computation"]
        NaNCheck["reset_if_nan check<br/>Optional parameter reset"]
    end
    
    subgraph "Inputs"
        InputData["data: FermiNetData<br/>positions, spins, atoms, charges"]
        InputParams["params: ParamTree<br/>Network parameters"]
        InputState["state: OptState<br/>Optimizer state"]
        InputKey["key: PRNGKey<br/>Random number generator"]
        InputWidth["mcmc_width: ndarray<br/>MCMC step width"]
    end
    
    subgraph "Outputs"
        OutputData["data: FermiNetData<br/>Updated configurations"]
        OutputParams["params: ParamTree<br/>Updated parameters"]
        OutputState["state: OptState<br/>Updated optimizer state"]
        OutputLoss["loss: ndarray<br/>Local energy"]
        OutputAux["aux_data: AuxiliaryLossData<br/>Additional loss data"]
        OutputPmove["pmove: ndarray<br/>Acceptance probability"]
    end
    
    InputData --> MCMCLoop
    InputParams --> MCMCLoop
    InputKey --> MCMCLoop
    InputWidth --> MCMCLoop
    
    MCMCLoop --> OptUpdate
    InputParams --> OptUpdate
    InputState --> OptUpdate
    
    OptUpdate --> NaNCheck
    NaNCheck --> OutputParams
    NaNCheck --> OutputState
    MCMCLoop --> OutputData
    OptUpdate --> OutputLoss
    OptUpdate --> OutputAux
    MCMCLoop --> OutputPmove
```

Sources: [ferminet/train.py:274-321]()

### KFAC Training Step

KFAC (Kronecker-Factored Approximate Curvature) requires special handling due to its more complex optimization procedure:

```mermaid
graph TD
    subgraph "make_kfac_training_step"
        KFACMCMCStep["mcmc_step (pmapped)<br/>MCMC sampling"]
        KFACOptStep["optimizer.step()<br/>KFAC optimization"]
        KFACNaNCheck["reset_if_nan check<br/>Parameter/state reset"]
    end
    
    subgraph "KFAC Specifics"
        SharedMom["shared_mom: replicated<br/>Momentum parameter"]
        SharedDamping["shared_damping: replicated<br/>Damping parameter"]
        CopyTree["copy_tree()<br/>Parameter copying for reset"]
        PmappedOps["Already pmapped operations<br/>Multi-device coordination"]
    end
    
    subgraph "KFAC Integration"
        KFACOptimizer["kfac_jax.Optimizer<br/>KFAC optimizer instance"]
        CurvatureEstimation["Curvature estimation<br/>Fisher information matrix"]
        InversePeriodic["Inverse update<br/>Periodic matrix inversion"]
    end
    
    KFACMCMCStep --> KFACOptStep
    SharedMom --> KFACOptStep
    SharedDamping --> KFACOptStep
    
    KFACOptStep --> KFACNaNCheck
    CopyTree --> KFACNaNCheck
    
    KFACOptimizer --> CurvatureEstimation
    CurvatureEstimation --> InversePeriodic
    InversePeriodic --> KFACOptStep
```

Sources: [ferminet/train.py:323-387]()

## Configuration and Initialization

The training pipeline requires extensive configuration and initialization before the main training loop begins.

### System Configuration Processing

```mermaid
graph TD
    subgraph "Input Processing"
        PySCFMol["cfg.system.pyscf_mol<br/>PySCF molecule object"]
        MoleculeConvert["pyscf_mol_to_internal_representation()<br/>Convert to internal format"]
        AtomArrays["atoms, charges arrays<br/>Atomic positions and charges"]
    end
    
    subgraph "Device Setup"
        DeviceCount["jax.local_device_count()<br/>Available devices"]
        BatchConfig["Batch size configuration<br/>Per-device batch sizing"]
        DataShape["data_shape: (num_devices, device_batch_size)<br/>Data parallelization"]
    end
    
    subgraph "Random State"
        SeedGeneration["Seed generation<br/>Deterministic or random"]
        KeySharding["kfac_jax.utils.make_different_rng_key_on_all_devices()<br/>Per-device PRNG keys"]
        MultiHostSync["multihost_utils.broadcast_one_to_all()<br/>Multi-host synchronization"]
    end
    
    PySCFMol --> MoleculeConvert
    MoleculeConvert --> AtomArrays
    
    DeviceCount --> BatchConfig
    BatchConfig --> DataShape
    
    SeedGeneration --> KeySharding
    KeySharding --> MultiHostSync
```

Sources: [ferminet/train.py:401-437](), [ferminet/train.py:686-687]()

### Network and Optimizer Construction

The training pipeline supports multiple network architectures and optimizers through a factory pattern:

```mermaid
graph TD
    subgraph "Network Construction"
        NetworkType["cfg.network.network_type<br/>'ferminet' or 'psiformer'"]
        FermiNetFactory["networks.make_fermi_net()<br/>FermiNet construction"]
        PsiFormerFactory["psiformer.make_fermi_net()<br/>PsiFormer construction"]
        NetworkInit["network.init(key)<br/>Parameter initialization"]
    end
    
    subgraph "Feature Layers"
        FeatureLayer["make_feature_layer()<br/>Input feature construction"]
        Envelope["envelopes.make_isotropic_envelope()<br/>Boundary conditions"]
        CustomFeatures["cfg.network.make_feature_layer_fn<br/>Custom feature layers"]
    end
    
    subgraph "Loss Function Construction"
        LossType["cfg.optim.objective<br/>'vmc', 'wqmc', 'vmc_overlap'"]
        VMCLoss["qmc_loss_functions.make_loss()<br/>Standard VMC loss"]
        WQMCLoss["qmc_loss_functions.make_wqmc_loss()<br/>Weighted QMC loss"]
        OverlapLoss["qmc_loss_functions.make_energy_overlap_loss()<br/>Overlap penalty loss"]
    end
    
    subgraph "Optimizer Construction"
        OptimizerType["cfg.optim.optimizer<br/>'adam', 'lamb', 'kfac', 'none'"]
        AdamOpt["optax.chain(optax.scale_by_adam(), ...)<br/>Adam optimizer"]
        LambOpt["optax.chain(optax.clip_by_global_norm(), ...)<br/>Lamb optimizer"]
        KFACOpt["kfac_jax.Optimizer()<br/>KFAC optimizer"]
    end
    
    NetworkType --> FermiNetFactory
    NetworkType --> PsiFormerFactory
    FermiNetFactory --> NetworkInit
    PsiFormerFactory --> NetworkInit
    
    FeatureLayer --> FermiNetFactory
    FeatureLayer --> PsiFormerFactory
    Envelope --> FermiNetFactory
    Envelope --> PsiFormerFactory
    CustomFeatures --> FeatureLayer
    
    LossType --> VMCLoss
    LossType --> WQMCLoss
    LossType --> OverlapLoss
    
    OptimizerType --> AdamOpt
    OptimizerType --> LambOpt
    OptimizerType --> KFACOpt
```

Sources: [ferminet/train.py:500-530](), [ferminet/train.py:786-827](), [ferminet/train.py:834-876]()

## Main Training Loop

The core training loop executes for a specified number of iterations, performing MCMC sampling, loss evaluation, parameter updates, and monitoring.

### Training Loop Flow

```mermaid
graph TD
    subgraph "Pre-Training"
        BurnIn["MCMC Burn-in<br/>cfg.mcmc.burn_in steps"]
        InitialEnergy["Initial energy evaluation<br/>evaluate_loss(params, key, data)"]
    end
    
    subgraph "Main Loop: for t in range(t_init, cfg.optim.iterations)"
        StepExecution["step(data, params, opt_state, key, mcmc_width)<br/>Training step execution"]
        LossProcessing["loss[0], weighted statistics<br/>Loss averaging and statistics"]
        ObservableUpdate["Observable calculations<br/>S², dipole, density matrix"]
        MCMCAdaptation["mcmc.update_mcmc_width()<br/>Adaptive step size"]
        NaNChecking["chex.assert_tree_all_finite()<br/>NaN detection"]
    end
    
    subgraph "Monitoring"
        StatsLogging["Logging every cfg.log.stats_frequency<br/>Energy, variance, pmove"]
        MatrixSaving["Matrix saving for excited states<br/>energy_matrix.npy, s2_matrix.npy"]
        Checkpointing["Checkpoint saving<br/>cfg.log.save_frequency minutes"]
    end
    
    BurnIn --> InitialEnergy
    InitialEnergy --> StepExecution
    
    StepExecution --> LossProcessing
    LossProcessing --> ObservableUpdate
    ObservableUpdate --> MCMCAdaptation
    MCMCAdaptation --> NaNChecking
    NaNChecking --> StatsLogging
    StatsLogging --> MatrixSaving
    MatrixSaving --> Checkpointing
    Checkpointing --> StepExecution
```

Sources: [ferminet/train.py:907-926](), [ferminet/train.py:968-1070]()

### Observable and Statistics Management

The training pipeline computes various physical observables and maintains training statistics:

```mermaid
graph TD
    subgraph "Observable Functions"
        S2Observable["observables.make_s2()<br/>Spin-squared operator"]
        DipoleObservable["observables.make_dipole()<br/>Dipole moment"]
        DensityObservable["observables.make_density_matrix()<br/>Density matrix"]
        CustomObservables["observables.make_observable_fns()<br/>Custom observables"]
    end
    
    subgraph "Statistics Tracking"
        WeightedStats["statistics.exponentialy_weighted_stats()<br/>Exponential moving average"]
        MCMCStats["pmove tracking<br/>MCMC acceptance rate"]
        EnergyClipping["cfg.optim.clip_local_energy<br/>Energy outlier handling"]
    end
    
    subgraph "Data Persistence"
        CSVWriter["writers.Writer<br/>Training metrics CSV"]
        NPYFiles["*.npy files<br/>Large matrix data"]
        Checkpoints["checkpoint.save()<br/>Model state persistence"]
    end
    
    S2Observable --> WeightedStats
    DipoleObservable --> WeightedStats
    DensityObservable --> NPYFiles
    
    WeightedStats --> CSVWriter
    MCMCStats --> CSVWriter
    EnergyClipping --> WeightedStats
    
    CSVWriter --> Checkpoints
    NPYFiles --> Checkpoints
```

Sources: [ferminet/train.py:641-684](), [ferminet/train.py:982-984](), [ferminet/train.py:1016-1043](), [ferminet/train.py:1044-1055]()

## Error Handling and Recovery

The training pipeline includes robust error handling and recovery mechanisms:

### NaN Detection and Recovery

```mermaid
graph TD
    subgraph "NaN Detection"
        TreeCheck["chex.assert_tree_all_finite()<br/>Check params, loss, optim state"]
        ConfigFlag["cfg.debug.check_nan<br/>Enable/disable checking"]
        ResetFlag["cfg.optim.reset_if_nan<br/>Enable parameter reset"]
    end
    
    subgraph "Recovery Mechanisms"
        ParamReset["jax.lax.cond(jnp.isnan(loss))<br/>Conditional parameter reset"]
        StateReset["Reset optimizer state<br/>Previous valid state"]
        CounterTracking["num_resets counter<br/>Limit reset attempts"]
    end
    
    subgraph "Failure Handling"
        MaxResets["num_resets > 100<br/>Maximum reset limit"]
        ExceptionRaise["raise AssertionError<br/>Training termination"]
    end
    
    TreeCheck --> ConfigFlag
    ConfigFlag --> ResetFlag
    ResetFlag --> ParamReset
    ParamReset --> StateReset
    StateReset --> CounterTracking
    CounterTracking --> MaxResets
    MaxResets --> ExceptionRaise
```

Sources: [ferminet/train.py:1000-1014](), [ferminet/train.py:311-317]()

The core training pipeline provides a robust and flexible framework for training neural network wavefunctions, supporting multiple architectures, optimizers, and loss functions while maintaining comprehensive monitoring and error recovery capabilities.

---

