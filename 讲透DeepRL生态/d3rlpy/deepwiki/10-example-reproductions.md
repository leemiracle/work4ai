> 来源: [https://deepwiki.com/takuseno/d3rlpy/10-example-reproductions](https://deepwiki.com/takuseno/d3rlpy/10-example-reproductions)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Example Reproductions

  Relevant source files 
 - [README.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1)
 - [ROADMAP.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/ROADMAP.md?plain=1)
 - [d3rlpy/algos/__init__.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/__init__.py)
 - [docs/references/algos.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst)
 - [docs/requirements.txt](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/requirements.txt)
 - [reproductions/offline/bcq.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bcq.py)
 - [reproductions/offline/bear.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bear.py)
 - [reproductions/offline/cql.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/cql.py)
 - [reproductions/offline/discrete_cql.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/discrete_cql.py)
 - [reproductions/offline/plas.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/plas.py)
 - [reproductions/offline/plas_with_perturbation.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/plas_with_perturbation.py)
 
  This document covers the example reproduction scripts provided with d3rlpy that demonstrate real-world usage patterns for training state-of-the-art offline reinforcement learning algorithms. These scripts serve as both benchmarking tools and practical examples showing proper algorithm configuration, hyperparameter tuning, and evaluation protocols.

 For information about the underlying algorithm implementations, see [Algorithm System](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system). For basic usage tutorials, see [Quick Start Tutorial](https://deepwiki.com/takuseno/d3rlpy/3-quick-start-tutorial). For details about training and evaluation systems, see [Training and Evaluation](https://deepwiki.com/takuseno/d3rlpy/8-training-and-evaluation).

 
## Purpose and Scope

 The reproduction scripts in d3rlpy provide complete, runnable examples that reproduce the results from original research papers. Each script demonstrates:

 
 - Proper algorithm configuration with paper-specific hyperparameters
 - Dataset loading and preprocessing setup
 - Training loop configuration with evaluation protocols
 - Seed management for reproducible results
 - GPU utilization and compilation optimizations
 
 These scripts are located in the [reproductions/](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/) directory and serve as both validation of d3rlpy's implementation quality and practical templates for users implementing their own training pipelines.

 
## Reproduction Script Architecture

 
### Common Structure Pattern

 All reproduction scripts follow a consistent architectural pattern that demonstrates d3rlpy best practices:

 
```

```

 **Script Execution Flow** This diagram shows the standard execution pattern used across all reproduction scripts. Each script processes command-line arguments, loads the appropriate dataset, configures seeds for reproducibility, creates the algorithm with paper-specific settings, and executes training with environment evaluation.

 Sources: [reproductions/offline/bear.py6-57](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bear.py#L6-L57) [reproductions/offline/cql.py6-51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/cql.py#L6-L51) [reproductions/offline/bcq.py6-48](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bcq.py#L6-L48)

 
### Algorithm-Specific Configurations

 Different algorithms require specific configuration patterns that reflect their original paper implementations:

 
```

```

 **Algorithm Configuration Patterns** This diagram illustrates the key configuration patterns for major offline RL algorithms. Each algorithm has specific hyperparameter requirements that reflect the original paper implementations and optimal performance characteristics.

 Sources: [reproductions/offline/cql.py20-38](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/cql.py#L20-L38) [reproductions/offline/bear.py20-44](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bear.py#L20-L44) [reproductions/offline/bcq.py20-35](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bcq.py#L20-L35) [reproductions/offline/plas.py20-37](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/plas.py#L20-L37)

 
## Specific Algorithm Examples

 
### Conservative Q-Learning (CQL)

 The CQL reproduction script demonstrates advanced offline RL configuration with dataset-specific hyperparameter selection:

 
| Configuration Aspect | Implementation | Purpose |
|---|---|---|
| Encoder Architecture | VectorEncoderFactory([256, 256, 256]) | Three-layer fully connected networks |
| Conservative Weight | 10.0 for medium datasets, 5.0 for others | Dataset-specific regularization strength |
| Learning Rates | Actor: 1e-4, Critic: 3e-4, Temperature: 1e-4 | Balanced learning across components |
| Action Sampling | n_action_samples=10 | Conservative Q-function estimation |
| Training Steps | 500000 with 1000 steps per epoch | Extended training for convergence |

 The script implements dataset-specific logic for optimal performance:

 
```

```

 Sources: [reproductions/offline/cql.py22-36](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/cql.py#L22-L36)

 
### Bootstrapping Error Accumulation Reduction (BEAR)

 The BEAR reproduction script showcases MMD-based policy constraint configuration:

 
| Configuration Aspect | Implementation | Purpose |
|---|---|---|
| VAE Encoder | VectorEncoderFactory([750, 750]) | Large capacity for behavior modeling |
| MMD Kernel | gaussian for HalfCheetah, laplacian for others | Environment-specific kernel selection |
| MMD Parameters | sigma=20.0, n_mmd_action_samples=4 | Maximum Mean Discrepancy tuning |
| Support Constraint | alpha_threshold=0.05, n_target_samples=10 | Policy support constraint parameters |
| Warmup Period | warmup_steps=40000 | Behavior cloning initialization |

 The script includes environment-specific MMD kernel selection:

 
```

```

 Sources: [reproductions/offline/bear.py22-44](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bear.py#L22-L44)

 
### Batch Constrained Q-Learning (BCQ)

 The BCQ reproduction script demonstrates VAE-based action constraint methodology:

 
| Configuration Aspect | Implementation | Purpose |
|---|---|---|
| VAE Encoder | VectorEncoderFactory([750, 750]) | Behavior modeling capacity |
| RL Encoders | VectorEncoderFactory([400, 300]) | Actor and critic network sizing |
| Constraint Parameter | lam=0.75 | VAE reconstruction weight |
| Action Flexibility | action_flexibility=0.05 | Perturbation magnitude |
| Action Sampling | n_action_samples=100 | Extensive action sampling |

 Sources: [reproductions/offline/bcq.py20-34](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bcq.py#L20-L34)

 
### Policy in Latent Action Space (PLAS)

 The PLAS reproduction scripts demonstrate sophisticated VAE-based policy learning with dataset-specific action flexibility:

 
| Dataset | Action Flexibility | Rationale |
|---|---|---|
| walker2d-random-v0 | 0.05 | Conservative exploration in random data |
| hopper-random-v0 | 0.5 | Higher flexibility for unstable dynamics |
| halfcheetah-medium-v0 | 0.1 | Balanced constraint for medium quality data |
| hopper-medium-expert-v0 | 0.01 | Minimal deviation from expert behavior |

 The action flexibility mapping demonstrates dataset-aware hyperparameter selection:

 
```

```

 Sources: [reproductions/offline/plas_with_perturbation.py5-18](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/plas_with_perturbation.py#L5-L18) [reproductions/offline/plas.py20-36](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/plas.py#L20-L36)

 
### Discrete CQL for Atari

 The discrete CQL reproduction script demonstrates pixel-based offline RL configuration:

 
| Configuration Aspect | Implementation | Purpose |
|---|---|---|
| Dataset Loading | get_atari_transitions(fraction=0.01) | 1% subset for manageable training |
| Quantile Regression | QRQFunctionFactory(n_quantiles=200) | Distributional Q-function estimation |
| Pixel Scaling | PixelObservationScaler() | Pixel normalization to [0,1] |
| Reward Clipping | ClipRewardScaler(-1.0, 1.0) | Standard Atari reward preprocessing |
| Optimizer Tuning | AdamFactory(eps=1e-2/32) | Epsilon adjustment for stability |

 Sources: [reproductions/offline/discrete_cql.py25-37](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/discrete_cql.py#L25-L37)

 
## Usage and Execution

 
### Command Line Interface

 All reproduction scripts support a consistent command-line interface:

 
```

```

 
### Common Parameters

 
| Parameter | Type | Default | Purpose |
|---|---|---|---|
| --dataset | str | Algorithm-specific | D4RL dataset identifier |
| --seed | int | 1 | Random seed for reproducibility |
| --gpu | int | None | GPU device index (CPU if unspecified) |
| --compile | flag | False | Enable torch.compile optimization |

 Sources: [reproductions/offline/bear.py7-12](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bear.py#L7-L12) [reproductions/offline/cql.py7-12](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/cql.py#L7-L12)

 
### Reproducibility Practices

 The scripts implement comprehensive reproducibility through multi-level seeding:

 
```

```

 **Reproducibility and Experiment Management** This diagram shows the comprehensive approach to ensuring reproducible results through multi-level seeding and systematic experiment naming conventions used across all reproduction scripts.

 Sources: [reproductions/offline/bear.py16-18](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bear.py#L16-L18) [reproductions/offline/cql.py16-18](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/cql.py#L16-L18)

 
### Training Configuration Patterns

 The reproduction scripts demonstrate consistent training configuration:

 
| Setting | Value | Purpose |
|---|---|---|
| Training Steps | 500000 (most) / 1000000 (PLAS) | Sufficient convergence time |
| Steps per Epoch | 1000 | Regular evaluation frequency |
| Save Interval | 10 epochs | Checkpoint preservation |
| Batch Size | Algorithm-specific (32-256) | Memory and stability balance |
| Environment Evaluation | EnvironmentEvaluator(env) | Performance monitoring |

 Sources: [reproductions/offline/cql.py40-47](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/cql.py#L40-L47) [reproductions/offline/bear.py46-53](https://github.com/takuseno/d3rlpy/blob/4f0956ba/reproductions/offline/bear.py#L46-L53)
