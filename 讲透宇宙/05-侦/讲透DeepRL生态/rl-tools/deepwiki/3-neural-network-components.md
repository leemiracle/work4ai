> 来源: [https://deepwiki.com/rl-tools/rl-tools/3-neural-network-components](https://deepwiki.com/rl-tools/rl-tools/3-neural-network-components)
> DeepWiki rl-tools/rl-tools | Last indexed: 2 February 2026 (a0aef4

# Neural Network Components

  Relevant source files 
 - [include/rl_tools/containers/tensor/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/containers/tensor/operations_generic.h)
 - [include/rl_tools/containers/tensor/tensor.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/containers/tensor/tensor.h)
 - [include/rl_tools/nn/layers/embedding/layer.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/embedding/layer.h)
 - [include/rl_tools/nn/layers/embedding/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/embedding/operations_generic.h)
 - [include/rl_tools/nn/layers/gru/layer.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/layer.h)
 - [include/rl_tools/nn/layers/gru/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h)
 - [src/rl/environments/pendulum/sac/wasm/full_training.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/sac/wasm/full_training.h)
 - [src/rl/environments/pendulum/td3/arm/training.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/td3/arm/training.h)
 - [tests/src/container/tensor.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/container/tensor.cpp)
 - [tests/src/nn/default_network_mlp.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/default_network_mlp.h)
 - [tests/src/nn/full_training_mlp.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/full_training_mlp.cpp)
 - [tests/src/nn/layers/gru/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/layers/gru/CMakeLists.txt)
 - [tests/src/nn/layers/gru/gru.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/layers/gru/gru.cpp)
 - [tests/src/nn/layers/gru/gru_model.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/layers/gru/gru_model.h)
 - [tests/src/nn/layers/gru/gru_training.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/layers/gru/gru_training.cpp)
 - [tests/src/nn/layers/gru/jax/jax_test.py](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/layers/gru/jax/jax_test.py)
 - [tests/src/nn/test_mlp.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/test_mlp.cpp)
 - [tests/src/rl/algorithms/td3/first_stage_mlp.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/algorithms/td3/first_stage_mlp.cpp)
 - [tests/src/rl/algorithms/td3/full_training_dummy_dep.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/algorithms/td3/full_training_dummy_dep.cpp)
 - [tests/src/rl/algorithms/td3/second_stage_mlp.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/algorithms/td3/second_stage_mlp.cpp)
 - [tests/src/rl/environments/pendulum/pendulum.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/rl/environments/pendulum/pendulum.cpp)
 
  This document provides a comprehensive overview of the neural network components in the RL-tools library. It covers various layer types, operations, tensor handling, and model composition mechanisms that serve as building blocks for constructing neural networks used in reinforcement learning. For information about specific reinforcement learning algorithms that use these components, see [Reinforcement Learning Algorithms](https://deepwiki.com/rl-tools/rl-tools/2-reinforcement-learning-algorithms).

 
## Architecture Overview

 The neural network components in RL-tools follow a consistent architecture pattern designed for performance and flexibility:

 **Neural Network Component Architecture**

 
```

```

 Sources:

 
 - [include/rl_tools/nn/layers/gru/layer.h11-22](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/layer.h#L11-L22)
 - [include/rl_tools/nn/layers/gru/layer.h23-38](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/layer.h#L23-L38)
 - [include/rl_tools/nn/layers/gru/layer.h99-186](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/layer.h#L99-L186)
 - [include/rl_tools/nn_models/sequential/operations_generic.h10-25](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn_models/sequential/operations_generic.h#L10-L25)
 
 This architecture consists of:

 
 - **Configuration**: Defines layer parameters (like dimensions, activation functions)
 - **Specification**: Combines Configuration with Input Shape and Capability
 - **Layer**: The implementation with Forward, Backward, or Gradient capabilities
 - **Module**: Wraps layers for sequential composition
 - **Model**: A complete neural network built from a module chain
 
 
## Tensor System

 Neural network operations rely on an underlying tensor system that provides efficient multidimensional array manipulation:

 **Tensor System Components**

 
```

```

 Sources:

 
 - [include/rl_tools/containers/tensor/tensor.h28-62](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/containers/tensor/tensor.h#L28-L62)
 - [include/rl_tools/containers/tensor/operations_generic.h440-499](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/containers/tensor/operations_generic.h#L440-L499)
 - [include/rl_tools/containers/tensor/operations_generic.h67-126](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/containers/tensor/operations_generic.h#L67-L126)
 - [include/rl_tools/containers/tensor/operations_generic.h292-363](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/containers/tensor/operations_generic.h#L292-L363)
 
 Key features of the tensor system include:

 
| Feature | Description | Key Functions |
|---|---|---|
| Storage | Both static and dynamic tensor storage | TensorStatic, TensorDynamic |
| Basic Operations | Core arithmetic operations | add, subtract, multiply, divide |
| View Operations | Zero-copy access to tensor subsets | view, view_range, permute |
| Element-wise | Function application to each element | sigmoid, tanh, exp, scale |
| Reduction | Operations that reduce tensor dimensions | sum, abs_diff, unary_reduce |
| Memory | Explicit memory management | malloc, free, copy |

 The tensor system serves as the foundation for all neural network operations, optimized for both CPU and GPU execution.

 
## Layer Types

 RL-tools provides several specialized neural network layer types:

 
### GRU (Gated Recurrent Unit)

 GRU is a recurrent layer for processing sequential data, featuring gates that control information flow.

 **GRU Layer Structure**

 
```

```

 Sources:

 
 - [include/rl_tools/nn/layers/gru/layer.h99-186](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/layer.h#L99-L186)
 - [include/rl_tools/nn/layers/gru/operations_generic.h102-114](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L102-L114)
 - [include/rl_tools/nn/layers/gru/operations_generic.h190-301](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L190-L301)
 - [tests/src/nn/layers/gru/gru.cpp74-328](https://github.com/rl-tools/rl-tools/blob/a0aef476/tests/src/nn/layers/gru/gru.cpp#L74-L328)
 
 The GRU implementation includes:

 
 - Reset and update gates controlling information flow
 - Candidate activation proposing new states
 - Sequence handling with configurable memory
 - Fast evaluation options (`FAST_TANH`)
 
 
### Dense (Fully Connected)

 The standard neural network layer connecting all inputs to all outputs through weights and biases.

 
```

```

 Features:

 
 - Configurable input/output dimensions
 - Multiple activation function options (ReLU, Tanh, Identity, etc.)
 - Weight matrices and bias vectors with gradient tracking
 - Kaiming uniform initialization by default
 
 Sources:

 
 - [include/rl_tools/nn/layers/dense/operations_generic.h16-45](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/dense/operations_generic.h#L16-L45)
 - [include/rl_tools/nn/layers/dense/operations_generic.h57-84](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/dense/operations_generic.h#L57-L84)
 
 
### Standardize

 A normalization layer that transforms inputs to have zero mean and unit variance.

 
```

```

 Features:

 
 - Configurable mean and standard deviation parameters
 - Precision-based computation to avoid division during forward pass
 - Zero-mean, unit-variance output transformation
 
 Sources:

 
 - [include/rl_tools/nn/layers/standardize/operations_generic.h49-63](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/standardize/operations_generic.h#L49-L63)
 - [include/rl_tools/nn/layers/standardize/operations_generic.h64-82](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/standardize/operations_generic.h#L64-L82)
 
 
### Sample and Squash

 A specialized layer for reinforcement learning that samples actions from a distribution and constrains them to a bounded range using tanh squashing.

 
```

```

 Features:

 
 - Gaussian sampling with parameterized mean and log standard deviation
 - Tanh squashing to bounded [-1, 1] range
 - Log probability computation for policy gradient methods
 - Support for external noise injection mode
 
 Sources:

 
 - [include/rl_tools/nn/layers/sample_and_squash/operations_generic.h115-161](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/sample_and_squash/operations_generic.h#L115-L161)
 - [include/rl_tools/nn/layers/sample_and_squash/operations_generic.h248-320](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/sample_and_squash/operations_generic.h#L248-L320)
 
 
### Embedding

 A layer that maps discrete tokens to dense vector representations.

 
```

```

 Features:

 
 - Maps discrete class indices to dense embeddings
 - Configurable number of classes and embedding dimensions
 - Standard normal weight initialization
 - Efficient lookup operation
 
 Sources:

 
 - [include/rl_tools/nn/layers/embedding/operations_generic.h70-85](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/embedding/operations_generic.h#L70-L85)
 - [include/rl_tools/nn/layers/embedding/operations_generic.h53-67](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/embedding/operations_generic.h#L53-L67)
 
 
## Layer Capabilities

 Layers in RL-tools implement different capabilities in a hierarchical structure:

 **Layer Capabilities Hierarchy**

 
```

```

 Sources:

 
 - [include/rl_tools/nn/layers/gru/layer.h164-186](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/layer.h#L164-L186)
 - [include/rl_tools/nn/layers/gru/layer.h201-206](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/layer.h#L201-L206)
 - [include/rl_tools/nn/layers/dense/operations_generic.h16-45](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/dense/operations_generic.h#L16-L45)
 
 
| Capability | Description | Class Suffix | Primary Functions |
|---|---|---|---|
| Forward | Basic forward evaluation | LayerForward | evaluate |
| Backward | Adds backward pass | LayerBackward | backward |
| Gradient | Adds gradient computation | LayerGradient | zero_gradient, update |

 This hierarchical design ensures that layers only include the operations they need, optimizing memory usage and performance.

 
## Neural Network Operations

 The neural network components support a common set of operations:

 
### Forward Pass

 The forward pass computes the output of a layer or model given its input:

 
```

```

 
### Backward Pass

 The backward pass computes gradients through the network:

 
```

```

 
### Weight Initialization

 Different initialization strategies are implemented for each layer type:

 
```

```

 
### Parameter Updates

 Updates layer parameters using optimizers like Adam:

 
```

```

 
### Persistence

 Saving and loading of layer and model parameters:

 
```

```

 Sources:

 
 - [include/rl_tools/nn/layers/gru/operations_generic.h302-307](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L302-L307)
 - [include/rl_tools/nn/layers/gru/operations_generic.h379-382](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L379-L382)
 - [include/rl_tools/nn/layers/gru/operations_generic.h558-698](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L558-L698)
 - [include/rl_tools/nn/layers/gru/operations_generic.h102-114](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L102-L114)
 - [include/rl_tools/nn/layers/dense/operations_generic.h57-84](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/dense/operations_generic.h#L57-L84)
 
 
## Model Composition

 RL-tools provides utilities for composing layers into complete neural network models:

 **Sequential Model Composition**

 
```

```

 **MLP Model Architecture**

 
```

```

 Sources:

 
 - [include/rl_tools/nn_models/sequential/operations_generic.h10-25](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn_models/sequential/operations_generic.h#L10-L25)
 - [include/rl_tools/nn_models/mlp/operations_generic.h12-27](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn_models/mlp/operations_generic.h#L12-L27)
 - [include/rl_tools/nn_models/mlp/operations_generic.h75-99](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn_models/mlp/operations_generic.h#L75-L99)
 
 
### Sequential Composition

 Layers are composed sequentially using the `ModuleForward` template with recursive module chains:

 
```

```

 Key operations that work recursively on the module chain:

 
 - `malloc`/`free` for memory management
 - `init_weights` for parameter initialization
 - `evaluate`/`forward` for computation
 - `get_layer<N>` for accessing specific layers
 
 
### Model Types

 Several pre-configured model types are available:

 
| Model Type | Description | Key Classes | Key Features |
|---|---|---|---|
| MLP | Multi-Layer Perceptron | NeuralNetworkForward, NeuralNetworkGradient | Dense layers with tick/tock buffering |
| Sequential | Generic sequential model | ModuleForward, Build | Flexibly combines any layer types |
| GRU-based | Recurrent models | LayerForward, LayerGradient | Sequence processing with hidden state |
| RL Policy | Stochastic policies | Sample-and-squash output layers | Bounded action spaces with log probabilities |

 
## Usage Examples

 
### Constructing a Simple MLP

 
```

```

 
### Using a GRU Layer

 
```

```

 Sources:

 
 - [include/rl_tools/nn_models/sequential/operations_generic.h10-25](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn_models/sequential/operations_generic.h#L10-L25)
 - [include/rl_tools/nn/layers/gru/operations_generic.h12-20](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L12-L20)
 - [include/rl_tools/nn/layers/gru/operations_generic.h102-114](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/gru/operations_generic.h#L102-L114)
 
 
## Performance Considerations

 The neural network components in RL-tools are designed with performance in mind:

 
 - **View Operations**: Zero-copy tensor views minimize memory allocations and data transfers
 - **Fast Math Options**: Optional faster implementations (`FAST_TANH`, `FAST_SIGMOID`) for performance-critical applications
 - **Memory Management**: Explicit `malloc`/`free` operations allow fine-grained control over memory
 - **Backend Flexibility**: Components work with multiple backends (CPU, CUDA) for optimal performance
 
 For embedded applications where performance is crucial, the library provides optimized implementations that balance accuracy and speed.
