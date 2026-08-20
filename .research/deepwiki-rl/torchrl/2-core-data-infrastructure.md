# deepwiki torchrl §2 core-data-infrastructure
> 来源: https://deepwiki.com/pytorch/rl/2-core-data-infrastructure

$/$
$?

/$

DeepWiki

DeepWiki
pytorch/rl

$?

/$

Last indexed:  14 December 2025  (eaaa11)

  - Overview
  - Core Data Infrastructure
  - TensorDict System
  - TensorSpec System
  - Environments
  - EnvBase and Environment Specifications
  - Environment Transforms
  - Backend Integrations
  - Batched and Parallel Environments
  - Data Collection
  - Collector Architecture
  - Distributed Collection Strategies
  - Replay Buffers
  - ReplayBuffer Architecture
  - Advanced Replay Buffer Features
  - Modules and Models
  - TensorDictModule System
  - Actors, Critics, and Value Networks
  - Probability Distributions
  - Neural Network Architectures
  - Exploration Strategies
  - Learning Algorithms
  - Loss Module Architecture
  - On-Policy Algorithms
  - Off-Policy Algorithms
  - Value-Based Algorithms
  - Value Estimators
  - Training Infrastructure
  - Trainer System
  - Helper Utilities
  - LLM Integration
  - LLM Wrapper System
  - LLM Data Structures
  - LLM Training Objectives
  - LLM Environments and Tools
  - Multi-Agent Reinforcement Learning
  - Examples and Tutorials
  - Development and Deployment
  - Build System
  - Documentation System

Menu

## Core Data Infrastructure

Relevant source files

  - test/_utils_internal.py

  - test/test_libs.py

  - test/test_specs.py

  - torchrl/data/tensor_specs.py

  - torchrl/data/utils.py

  - torchrl/envs/gym_like.py

  - torchrl/envs/libs/gym.py

The core data infrastructure in TorchRL consists of two foundational systems that enable type-safe, structured data exchange across all components: the TensorDict container (from the `tensordict` library) and the TensorSpec type system (defined in TorchRL). These systems provide the scaffolding for defining, validating, and manipulating the structured tensor data that flows through environments, collectors, replay buffers, and neural network modules.

Scope: This page documents the TensorSpec type system and its role in the data infrastructure. For information about TensorDict operations and usage patterns, see TensorDict System. For environment-specific spec usage, see EnvBase and Environment Specifications.

### Architecture Overview

The core data infrastructure establishes a contract between all TorchRL components through two complementary abstractions:

```

```

TensorDict as Universal Container: `TensorDict` (from the tensordict library) is a dictionary-like container for tensors that preserves batch dimensions and enables nested access patterns. It serves as the universal data format for observations, actions, rewards, and all other data exchanged between components.

TensorSpec as Type System: `TensorSpec` classes define the properties of tensors (shape, dtype, device, bounds) and provide methods for validation, sampling, and encoding. Every component that produces or consumes TensorDict data declares its expectations via specs.

Sources: Diagram 1 from high-level architecture torchrl/data/tensor_specs.py589-615

### TensorSpec Base Class

The `TensorSpec` abstract base class defines the interface for all spec types. Located at torchrl/data/tensor_specs.py589 it provides:

| Property/Method | Purpose |
| shape: torch.Size | Tensor shape including batch dimensions |
| space: Box | Value domain (e.g., ContinuousBox , CategoricalBox ) |
| device: torch.device | Target device for tensors |
| dtype: torch.dtype | Data type |
| rand() | Generate random samples within spec bounds |
| zero() | Generate zero-initialized tensor |
| encode() | Convert raw values to spec-compliant tensors |
| is_in() | Check if value satisfies spec constraints |
| project() | Map out-of-bounds values back to valid domain |
| expand() , reshape() , squeeze() , unsqueeze() | Shape manipulation |
| to() | Device/dtype casting |

#### Core Validation Flow

```

```

The `encode()` method transforms raw data from environments (numpy arrays, lists, dictionaries) into torch tensors with the correct shape, dtype, and device. The `is_in()` method validates that tensor values satisfy spec constraints (bounds, shape, dtype). The `project()` method clamps out-of-bounds values back to the valid domain.

Sources: torchrl/data/tensor_specs.py589-890 torchrl/data/tensor_specs.py699-766 torchrl/data/tensor_specs.py1031-1045

### Concrete Spec Types

#### Bounded and Unbounded Specs

`Bounded` specs represent continuous values with minimum and maximum bounds:

```

```

Example usage from test/test_specs.py142-176:

  - Actions in continuous control (e.g., joint torques)

  - Image pixel values scaled to [0, 1]

  - Normalized observations with known ranges

`Unbounded` specs represent continuous values without constraints:

  - States in unbounded domains

  - Latent representations

  - Value function outputs

Both classes are defined at torchrl/data/tensor_specs.py1149-1409 (Bounded) and torchrl/data/tensor_specs.py1411-1505 (Unbounded).

Sources: torchrl/data/tensor_specs.py1149-1505 test/test_specs.py64-187

#### Discrete Action Specs

TorchRL supports two encodings for discrete actions: categorical (integer indices) and one-hot (binary vectors).

```

```

Key classes:

  - Categorical(n) : Integer values in range [0, n-1], defined at torchrl/data/tensor_specs.py 2168-2344

  - OneHot(n) : Binary vectors with exactly one 1, defined at torchrl/data/tensor_specs.py 1862-2043

  - MultiCategorical(nvec) : Multiple independent discrete variables, defined at torchrl/data/tensor_specs.py 2346-2580

  - MultiOneHot(nvec) : Multiple one-hot vectors concatenated, defined at torchrl/data/tensor_specs.py 2045-2166

Conversion methods (from test/test_specs.py326-356):

  - spec.to_one_hot_spec() / spec.to_categorical_spec() : Convert between spec types

  - spec.to_one_hot(tensor) / spec.to_categorical(tensor) : Convert between value encodings

Sources: torchrl/data/tensor_specs.py1862-2580 test/test_specs.py92-356

#### Binary Spec

`Binary(n)` represents binary vectors of length `n` (each element is 0 or 1), typically used for multi-binary action spaces:

```

```

Defined at torchrl/data/tensor_specs.py2582-2630

Sources: torchrl/data/tensor_specs.py2582-2630 test/test_specs.py223-240

#### NonTensor Spec

`NonTensor` handles non-tensor data that cannot be represented as torch tensors (strings, objects, etc.):

```

```

Used for:

  - Text observations (prompts, responses) in LLM environments

  - Complex structured data from info dicts

  - Arbitrary Python objects that need to flow through TorchRL pipelines

Defined at torchrl/data/tensor_specs.py2632-2747

Sources: torchrl/data/tensor_specs.py2632-2747

### Composite Specs

`Composite` specs define nested, dictionary-like structures matching TensorDict's hierarchical organization:

```

```

#### Key Features

From torchrl/data/tensor_specs.py2749-3771:

| Operation | Description |
| spec["key"] | Get/set nested specs using dictionary syntax |
| spec["nested", "key"] | Access deeply nested specs with tuple keys |
| spec.keys(include_nested=True) | Iterate over all keys, including nested |
| spec.update(other_spec) | Merge another Composite spec |
| spec.rand() | Generate nested TensorDict with random values |
| spec.zero() | Generate nested TensorDict with zeros |
| spec.encode(dict) | Recursively encode nested dictionaries |
| spec.is_in(tensordict) | Validate all nested values |

#### Device and Shape Propagation

When setting a spec in a Composite:

  - If the spec's device doesn't match the Composite's device, it is automatically cast

  - If the spec's shape is empty, it inherits the Composite's batch shape

  - Nested Composites maintain their own shapes and devices

Example from test/test_specs.py399-434:

```

```

Sources: torchrl/data/tensor_specs.py2749-3771 test/test_specs.py358-697

### Box System (Internal Representation)

The `Box` classes are internal data structures that represent the value domains of specs. Located at torchrl/data/tensor_specs.py361-586:

```

```

Box Role: Each TensorSpec has a `.space` attribute pointing to a Box instance that encapsulates the value domain. The Box provides:

  - Storage for bounds (low/high) or cardinality (n)

  - Device management for bound tensors

  - Iteration protocol for unpacking bounds

  - Equality checking for spec comparison

ContinuousBox Batch Size Optimization: From torchrl/data/tensor_specs.py377-421 ContinuousBox can collapse batch dimensions if all bounds are identical across the batch, reducing memory footprint.

Sources: torchrl/data/tensor_specs.py361-586

### Spec Operations and Indexing

TensorSpecs support tensor-like operations for composability:

#### Shape Operations

```

```

From torchrl/data/tensor_specs.py931-1023:

  - spec.expand(*shape) : Broadcast spec to new batch dimensions

  - spec.reshape(*shape) : Reshape like torch.reshape

  - spec.flatten(start_dim, end_dim) : Flatten dimensions

  - spec.unflatten(dim, sizes) : Unflatten a dimension

  - spec.squeeze(dim) , spec.unsqueeze(dim) : Add/remove singleton dimensions

#### Indexing

TensorSpecs support advanced indexing to extract sub-specs:

```

```

Indexing logic at torchrl/data/tensor_specs.py199-325 handles:

  - Integer indices (reduce dimension)

  - Slices (preserve dimension with new size)

  - Ellipsis ( ... ) for wildcard dimensions

  - Lists and tensors for advanced indexing

  - Tuple indexing for multiple dimensions

  - None for adding singleton dimensions

Sources: torchrl/data/tensor_specs.py931-1023 torchrl/data/tensor_specs.py199-325

### Spec Transformations and Conversions

#### Gym/Gymnasium Interoperability

TorchRL provides bidirectional transformations between Gym spaces and TensorSpecs:

```

```

Conversion Functions (from torchrl/envs/libs/gym.py309-710):

  - _gym_to_torchrl_spec_transform(spec, dtype, device, categorical_action_encoding, batch_size) Entry point at torchrl/envs/libs/gym.py 309-353 Uses registry pattern to dispatch to type-specific converters Key parameter: categorical_action_encoding (bool) determines OneHot vs Categorical for discrete spaces

  - _torchrl_to_gym_spec_transform(spec, categorical_action_encoding) Entry point at torchrl/envs/libs/gym.py 640-710 Reverses the transformation for environments that need Gym spaces

#### Converter Registry

The conversion system uses a registry pattern (torchrl/envs/libs/gym.py236-307):

```

```

Built-in converters handle:

  - Box → Bounded/Unbounded (based on bounds)

  - Discrete → Categorical/OneHot

  - MultiDiscrete → MultiCategorical/MultiOneHot

  - MultiBinary → Binary

  - Dict → Composite (with key remapping)

  - Tuple → Stacked specs

  - Sequence → Specs with -1 dimension (variable length)

  - Text → NonTensor

Sources: torchrl/envs/libs/gym.py309-710 test/test_libs.py369-498

### Integration with Environments

Environments use specs to declare their input/output contracts:

```

```

#### Spec Construction in Environments

From torchrl/envs/gym_like.py349-388 environments build specs during initialization:

  - Parse environment's native spec format (e.g., Gym spaces)

  - Transform to TorchRL specs using _gym_to_torchrl_spec_transform

  - Set device and batch_size to match environment configuration

  - Register info_dict keys for auxiliary outputs

Example flow from torchrl/envs/libs/gym.py822-900:

```

```

#### Spec Usage in Step/Reset

From torchrl/envs/gym_like.py441-550:

Step cycle:

  - Extract action from input TensorDict using action_spec.to_numpy()

  - Call environment's native step function

  - Read observation using observation_spec.encode()

  - Read reward using reward_spec.encode()

  - Validate done states against done_spec

  - Return validated TensorDict

Reset cycle:

  - Call environment's native reset function

  - Read observation using observation_spec.encode()

  - Zero-initialize reward, done from specs

  - Return validated TensorDict

Fast Encoding: The `fast_encoding()` method (torchrl/envs/gym_like.py182-225) memoizes the encoding pipeline to skip repeated validation checks, improving performance by ~5-10%.

Sources: torchrl/envs/gym_like.py153-656 torchrl/envs/libs/gym.py795-1050

### Common Patterns and Usage

#### Pattern 1: Building Specs from Scratch

```

```

#### Pattern 2: Inferring Specs from Data

From torchrl/data/tensor_specs.py3773-3881:

```

```

#### Pattern 3: Spec Validation in Custom Components

```

```

#### Pattern 4: Device Management

```

```

#### Pattern 5: Heterogeneous Dimensions

Variable-length sequences use `-1` in shape:

```

```

Sources: torchrl/data/tensor_specs.py2749-3881 test/test_specs.py358-1500

### Summary Table: Spec Types

| Spec Class | Use Case | Value Domain | Shape |
| Bounded | Continuous actions/observations with bounds | [low, high] | Any |
| Unbounded | Continuous values without constraints | (-∞, +∞) | Any |
| Categorical | Discrete actions (integer index) | {0, 1, ..., n-1} | (*) or (*,1) |
| OneHot | Discrete actions (one-hot vector) | {0, 1}^n with sum=1 | (*,n) |
| MultiCategorical | Multiple discrete variables (integer) | Product of categoricals | (*,k) |
| MultiOneHot | Multiple discrete variables (one-hot) | Concatenated one-hots | (*,Σn_i) |
| Binary | Multi-binary actions | {0, 1}^n | (*,n) |
| NonTensor | Non-tensor data (strings, objects) | Any Python object | Any |
| Composite | Nested/dictionary structures | Nested specs | Any |
| StackedComposite | Stacked/batched composite specs | Stacked specs | Adds batch dim |

Sources: torchrl/data/tensor_specs.py1149-3771



#### On this page

  - Core Data Infrastructure
  - Architecture Overview
  - TensorSpec Base Class
  - Core Validation Flow
  - Concrete Spec Types
  - Bounded and Unbounded Specs
  - Discrete Action Specs
  - Binary Spec
  - NonTensor Spec
  - Composite Specs
  - Key Features
  - Device and Shape Propagation
  - Box System (Internal Representation)
  - Spec Operations and Indexing
  - Shape Operations
  - Indexing
  - Spec Transformations and Conversions
  - Gym/Gymnasium Interoperability
  - Converter Registry
  - Integration with Environments
  - Spec Construction in Environments
  - Spec Usage in Step/Reset
  - Common Patterns and Usage
  - Pattern 1: Building Specs from Scratch
  - Pattern 2: Inferring Specs from Data
  - Pattern 3: Spec Validation in Custom Components
  - Pattern 4: Device Management
  - Pattern 5: Heterogeneous Dimensions
  - Summary Table: Spec Types

$!/$$/$
