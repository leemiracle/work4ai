> 来源: [https://deepwiki.com/tensorforce/tensorforce/4-neural-network-architecture](https://deepwiki.com/tensorforce/tensorforce/4-neural-network-architecture)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Neural Network Architecture

  Relevant source files 
 - [tensorforce/core/networks/__init__.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/__init__.py)
 - [tensorforce/core/networks/auto.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/auto.py)
 - [tensorforce/core/networks/network.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py)
 
  This page documents the neural network architecture system within Tensorforce. It explains how neural networks are structured, configured, and used to represent policies and value functions in reinforcement learning agents.

 
## Purpose and Role

 Neural networks in Tensorforce serve as function approximators that map states to actions (policy networks) or estimate value functions. They are a key component in the agent architecture, sitting between state inputs and action outputs or value estimations.

 For information about how these networks are used within specific agent implementations, see [Agent Implementations](https://deepwiki.com/tensorforce/tensorforce/3-agent-implementations).

 Sources: [tensorforce/core/networks/network.py28-111](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L28-L111)

 
## Network Class Hierarchy

 Tensorforce implements a flexible neural network architecture system through a hierarchy of classes:

 
```

```

 
### Network Base Class

 The `Network` abstract base class defines the core interface that all networks must implement:

 
 - `output_spec()`: Returns the output tensor specification
 - `internals_spec`: Property that returns specifications for internal states
 - `apply()`: Processes inputs through the network and returns outputs
 
 This base class ensures that all network implementations share a common interface for use by agents.

 Sources: [tensorforce/core/networks/network.py28-111](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L28-L111)

 
### LayerbasedNetwork

 `LayerbasedNetwork` extends the base `Network` class to provide common functionality for networks built from individual layers:

 
 - Manages registered tensors for inter-layer communication
 - Handles layer submodules and their specifications
 - Processes inputs through layers with proper tensor registration
 
 This class serves as a foundation for constructing networks from Tensorforce layers.

 Sources: [tensorforce/core/networks/network.py113-268](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L113-L268)

 
### LayeredNetwork

 `LayeredNetwork` provides a concrete implementation of `LayerbasedNetwork` that allows networks to be specified as a list of layer configurations:

 
 - Parses layer specifications into a structured representation
 - Implements the `apply()` method to process inputs through the layer structure
 - Supports complex architectures with nested layer stacks
 
 This is the default network type in Tensorforce, allowing for flexible network architectures through configuration.

 Sources: [tensorforce/core/networks/network.py271-437](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L271-L437)

 
### AutoNetwork

 `AutoNetwork` extends `LayeredNetwork` to automatically configure network architectures based on input types and shapes:

 
 - Determines appropriate layer types based on input ranks
 - Handles embedding of boolean and integer inputs
 - Automatically configures layer sizes and depths
 - Supports optional RNN layers for sequential data
 
 This network type simplifies configuration by inferring appropriate architectures for given inputs.

 Sources: [tensorforce/core/networks/auto.py22-177](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/auto.py#L22-L177)

 
## Network Configuration

 
### Network Configuration Flow

 The following diagram illustrates how networks are configured and built in Tensorforce:

 
```

```

 Sources: [tensorforce/core/networks/__init__.py24-27](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/__init__.py#L24-L27) [tensorforce/core/networks/network.py296-305](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L296-L305) [tensorforce/core/networks/auto.py49-177](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/auto.py#L49-L177)

 
### LayeredNetwork Configuration

 The `LayeredNetwork` can be configured using a list of layer specifications or a nested list for more complex architectures:

 
```
layers = [
    {"type": "dense", "size": 64},
    {"type": "relu"},
    {"type": "dense", "size": 64},
    {"type": "relu"}
]
```

 Each layer specification is converted into a layer submodule during network initialization.

 Sources: [tensorforce/core/networks/network.py271-352](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L271-L352)

 
### AutoNetwork Configuration

 `AutoNetwork` simplifies configuration by requiring only high-level parameters:

 
 - `size`: The size of layers for processing individual state components
 - `depth`: Number of layers per state component
 - `final_size`: Layer size after concatenation of multiple state components
 - `final_depth`: Number of layers after concatenation
 - `rnn`: Whether to add an LSTM cell as the last layer
 
 
```
network = "auto"  # Use AutoNetwork
network_kwargs = {
    "size": 64,
    "depth": 2,
    "rnn": 10  # LSTM with horizon of 10
}
```

 The network then automatically determines appropriate layer types based on input specifications.

 Sources: [tensorforce/core/networks/auto.py49-177](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/auto.py#L49-L177)

 
## Network Layer Processing

 
### Layer Processing Flow

 This diagram shows how inputs flow through a layered network:

 
```

```

 Sources: [tensorforce/core/networks/network.py354-437](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L354-L437)

 
### Layer Types and Processing

 The network architecture supports various layer types with specialized processing:

 
 - **MultiInputLayer**: Processes tensors from multiple inputs
 - **TemporalLayer**: Processes temporal data with internal state (e.g., RNN, LSTM)
 - **NondeterministicLayer**: Applies processing based on a deterministic flag
 - **Register**: Stores outputs in registered tensors for later use
 - **Standard Layers**: Standard neural network layers like Dense, Conv2D, etc.
 
 The `_recursive_apply` method in `LayeredNetwork` handles the flow of data through these different layer types.

 Sources: [tensorforce/core/networks/network.py374-437](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L374-L437)

 
## AutoNetwork Architecture Construction

 
### AutoNetwork Input Processing

 
```

```

 Sources: [tensorforce/core/networks/auto.py84-173](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/auto.py#L84-L173)

 The `AutoNetwork` constructs its architecture based on input specifications:

 
 - For each input state:

 
 - Retrieves the state tensor
 - Adds embedding layers for boolean and integer inputs
 - Selects appropriate layer types based on input rank: 
 - Rank 0: Flatten followed by Dense
 - Rank 1: Dense layers
 - Rank 2: Conv1D layers
 - Rank 3: Conv2D layers
 - Applies pooling for inputs with rank > 1
 - Registers the state-specific embedding
 - For multiple input states:

 
 - Retrieves and concatenates all state embeddings
 - Applies final dense layers
 - Optionally adds an LSTM layer for temporal processing
 
 This automatic construction simplifies network configuration for complex input spaces.

 Sources: [tensorforce/core/networks/auto.py84-173](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/auto.py#L84-L173)

 
## Integration with Agents

 Neural networks in Tensorforce are used by agents primarily in two contexts:

 
 - **Policy Networks**: Map states to actions or action distributions
 - **Value Networks**: Estimate value functions (state values, action values, etc.)
 
 
```

```

 The neural network architecture serves as a flexible foundation for implementing various reinforcement learning algorithms, allowing agents to adapt their behavior and value estimates through interaction with the environment.

 The integration between networks and other components is handled within the agent's model, which coordinates the flow of information between networks, distributions, optimizers, and memory systems.

 Sources: [tensorforce/core/networks/network.py28-42](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L28-L42)

 
## Custom Networks

 To create custom network architectures, users can:

 
 - Use the `LayeredNetwork` with custom layer configurations
 - Extend the `Network` or `LayerbasedNetwork` classes
 - Implement the required methods: 
 - `output_spec()`
 - `apply()`
 
 Custom networks allow for specialized architectures that may not be easily expressed through the standard configuration options.

 Sources: [tensorforce/core/networks/network.py28-111](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L28-L111) [tensorforce/core/networks/network.py113-268](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/networks/network.py#L113-L268)

 
## Summary

 The neural network architecture system in Tensorforce provides a flexible foundation for implementing various reinforcement learning algorithms:

 
 - The base `Network` class defines a common interface
 - `LayerbasedNetwork` and `LayeredNetwork` provide layered network capabilities
 - `AutoNetwork` automatically configures network architecture based on inputs
 - Multiple layer types support different processing needs
 - Networks integrate with agents to implement policies and value functions
 
 This modular design allows for a wide range of network architectures to be used within reinforcement learning agents, supporting both standard configurations and custom implementations.
