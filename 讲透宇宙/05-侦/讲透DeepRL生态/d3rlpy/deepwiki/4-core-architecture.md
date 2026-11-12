> 来源: [https://deepwiki.com/takuseno/d3rlpy/4-core-architecture](https://deepwiki.com/takuseno/d3rlpy/4-core-architecture)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Core Architecture

  Relevant source files 
 - [d3rlpy/base.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py)
 - [docs/references/logging.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/logging.rst)
 - [tests/base_test.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/base_test.py)
 
  This document explains the foundational design patterns and base classes that underpin all d3rlpy algorithms. The core architecture provides a three-layer abstraction that separates configuration, algorithm logic, and PyTorch implementation details.

 For comprehensive coverage of the algorithm framework that builds on these foundations, see [Algorithm System](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system). For details about the neural network components used in implementations, see [Model Components](https://deepwiki.com/takuseno/d3rlpy/7-model-components).

 
## Architectural Overview

 The d3rlpy architecture follows a consistent three-layer pattern that separates concerns between configuration, algorithm lifecycle management, and PyTorch implementation details.

 
### Core Architecture Layers

 
```

```

 **Sources:** [d3rlpy/base.py47-88](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L47-L88) [d3rlpy/base.py207-231](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L207-L231) [d3rlpy/base.py90-117](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L90-L117)

 
## Configuration Layer

 The configuration layer uses dataclasses to define algorithm parameters and provides factory methods for creating algorithm instances.

 
### LearnableConfig Base Class

 The `LearnableConfig` class serves as the base for all algorithm configurations, providing common parameters and the creation interface.

 
| Property | Type | Default | Purpose |
|---|---|---|---|
| batch_size | int | 256 | Training batch size |
| gamma | float | 0.99 | Discount factor |
| observation_scaler | Optional[ObservationScaler] | None | Observation preprocessing |
| action_scaler | Optional[ActionScaler] | None | Action preprocessing |
| reward_scaler | Optional[RewardScaler] | None | Reward preprocessing |
| compile_graph | bool | False | Enable torch.compile optimization |

 The `create()` method serves as the factory interface:

 
```

```

 
### Configuration Registration System

 The architecture includes a dynamic configuration registration system that enables serialization and deserialization:

 
```

```

 **Sources:** [d3rlpy/base.py90-122](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L90-L122) [d3rlpy/base.py120-122](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L120-L122)

 
## Algorithm Base Layer

 The `LearnableBase` class provides the core algorithm interface and lifecycle management. It uses generic typing to maintain type safety across the configuration-algorithm-implementation chain.

 
### Generic Type System

 
```

```

 This design ensures type safety while allowing algorithm-specific implementations to specialize the base types.

 
### Core Algorithm Properties

 The algorithm layer exposes configuration properties and manages the implementation lifecycle:

 
| Property | Source | Purpose |
|---|---|---|
| config | Configuration instance | Access to algorithm parameters |
| impl | Implementation instance | Access to PyTorch components |
| observation_shape | Implementation delegate | Input data shape |
| action_size | Implementation delegate | Output action dimensions |
| grad_step | Internal counter | Training progress tracking |

 
### Implementation Creation Workflow

 
```

```

 **Sources:** [d3rlpy/base.py301-318](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L301-L318) [d3rlpy/base.py320-329](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L320-L329) [d3rlpy/base.py331-342](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L331-L342)

 
## Implementation Layer

 The `ImplBase` class provides the PyTorch-specific implementation interface. All algorithm implementations inherit from this base to ensure consistent neural network management.

 
### Implementation Base Structure

 
```

```

 
### Neural Network Management

 The implementation layer uses the `Modules` container pattern for managing PyTorch components:

 
```

```

 **Sources:** [d3rlpy/base.py47-88](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L47-L88) [d3rlpy/base.py63-64](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L63-L64)

 
## Lifecycle Management

 The architecture provides comprehensive lifecycle management including creation, serialization, and reconstruction of algorithm instances.

 
### Serialization Architecture

 
```

```

 
### Reconstruction Workflow

 The architecture supports multiple reconstruction pathways:

 
| Method | Input | Purpose |
|---|---|---|
| load_learnable() | *.d3 file | Full algorithm reconstruction |
| from_json() | params.json | Configuration-based reconstruction |
| load_model() | *.pt file | Model weights only |

 **Sources:** [d3rlpy/base.py169-204](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L169-L204) [d3rlpy/base.py232-275](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L232-L275) [d3rlpy/base.py276-299](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L276-L299)

 
## Device and Compilation Handling

 The architecture provides unified device management and performance optimization through compilation.

 
### Device Processing

 
```

```

 
### Compilation Support

 The architecture integrates with PyTorch's compilation features:

 
```

```

 This enables CudaGraph optimization and `torch.compile` when running on CUDA devices with the `compile_graph` flag enabled.

 **Sources:** [d3rlpy/base.py151-166](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L151-L166) [d3rlpy/base.py361-371](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/base.py#L361-L371)
