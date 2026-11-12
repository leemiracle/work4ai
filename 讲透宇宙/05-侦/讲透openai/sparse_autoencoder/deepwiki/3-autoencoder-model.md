<!-- source: DeepWiki mcp.deepwiki.com · repo openai/sparse_autoencoder · page 3 Autoencoder Model · fetched 2026-10-26 -->

# Autoencoder Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sparse_autoencoder/__init__.py](sparse_autoencoder/__init__.py)
- [sparse_autoencoder/model.py](sparse_autoencoder/model.py)

</details>



This document details the core Autoencoder model used in the sparse_autoencoder repository. It focuses on the implementation, architecture, and key features of the model. For specific information about encoder and decoder components, see [Encoder and Decoder](#3.1); for activation functions, see [Activation Functions](#3.2); for loss functions, see [Loss Functions](#3.3); and for normalization techniques, see [Normalization](#3.4).

## Overview

The Autoencoder model is the central component of the sparse autoencoder system, designed to learn sparse representations of neural network activations. It implements a standard autoencoder architecture with specific adaptations for sparsity, including support for different activation functions and weight tying options.

```mermaid
graph TD
    subgraph "Autoencoder Model Architecture"
        I["Input Data"] --> P["Preprocessing"]
        P --> B["Bias Subtraction (pre_bias)"]
        B --> E["Encoder Linear Layer"]
        E --> A["Latent Bias + Activation"]
        A --> D["Decoder Linear Layer"]
        D --> PB["Pre-bias Addition"]
        PB --> PP["Post-processing"]
        PP --> O["Output (Reconstruction)"]
    end

    subgraph "Options"
        N["Normalization"]
        T["Weight Tying"]
        S["Activation (e.g., ReLU, TopK)"]
    end

    N -.-> P
    N -.-> PP
    T -.-> D
    S -.-> A
```

Sources: [sparse_autoencoder/model.py:16-141]()

## Core Components

The Autoencoder class is implemented as a PyTorch module with the following core components:

| Component | Type | Description |
|-----------|------|-------------|
| `pre_bias` | Parameter | Bias subtracted from input and added to output |
| `encoder` | Linear Layer | Transforms input data to latent space |
| `latent_bias` | Parameter | Bias added to encoder output before activation |
| `activation` | Callable | Activation function (e.g., ReLU, TopK) |
| `decoder` | Linear Layer or TiedTranspose | Transforms latent representation back to input space |

The model implements the following transformation:
```
latents = activation(encoder(x - pre_bias) + latent_bias)
recons = decoder(latents) + pre_bias
```

Sources: [sparse_autoencoder/model.py:16-54]()

## Implementation Details

### Initialization

The Autoencoder's constructor initializes the model components and sets up tracking buffers for monitoring the activity of latent neurons.

```mermaid
classDiagram
    class Autoencoder {
        +pre_bias: Parameter
        +encoder: Linear
        +latent_bias: Parameter
        +activation: Callable
        +decoder: Linear|TiedTranspose
        +normalize: bool
        +stats_last_nonzero: Tensor
        +latents_activation_frequency: Tensor
        +latents_mean_square: Tensor
        +__init__(n_latents, n_inputs, activation, tied, normalize)
    }
```

Key initialization parameters:
- `n_latents`: Dimension of the latent space
- `n_inputs`: Dimension of the input data
- `activation`: Activation function (default: ReLU)
- `tied`: Whether to tie encoder and decoder weights
- `normalize`: Whether to apply normalization

Sources: [sparse_autoencoder/model.py:24-53]()

### Encoding Process

The encoding process consists of two main steps:
1. Optional normalization of input data
2. Linear transformation followed by bias addition and activation

```mermaid
flowchart LR
    X["Input x"] --> |"Optional"| N["Normalization\nLN(x)"]
    N --> S["Subtract pre_bias\nx - pre_bias"]
    S --> L["Linear transform\nencoder(x)"]
    L --> B["Add latent_bias"]
    B --> A["Apply activation\nfunction"]
    A --> O["Latent representation"]
```

The encoding is implemented through two methods:
- `encode_pre_act`: Computes pre-activation latents
- `encode`: Applies activation to produce final latents

Sources: [sparse_autoencoder/model.py:55-80]()

### Decoding Process

The decoder transforms the latent representation back to the original input space:

```mermaid
flowchart LR
    L["Latent representation"] --> D["Decoder transformation\ndecoder(latents)"]
    D --> A["Add pre_bias"]
    A --> |"Optional"| P["Post-processing\n(denormalization)"]
    P --> O["Reconstructed output"]
```

If normalization was applied during encoding, the corresponding denormalization is applied during decoding.

Sources: [sparse_autoencoder/model.py:82-91]()

### Forward Pass

The forward pass ties together the encoding and decoding steps, and also updates tracking statistics:

```mermaid
flowchart TD
    X["Input x"] --> P["Preprocess\n(normalize if enabled)"]
    P --> E["Encode pre-activation\nlatents_pre_act"]
    E --> A["Apply activation\nlatents"]
    A --> D["Decode\nreconstructions"]
    A --> |"Update"| S["Statistics tracking\n(nonzero latents)"]
    D --> R["Return latents_pre_act,\nlatents, reconstructions"]
```

The method tracks which latent neurons are active by updating the `stats_last_nonzero` buffer, which counts how many batches have passed since each neuron was last active.

Sources: [sparse_autoencoder/model.py:93-109]()

## Supporting Components

### TiedTranspose

The `TiedTranspose` class enables weight tying between encoder and decoder, which reduces the number of parameters and enforces a specific form of regularization:

```mermaid
classDiagram
    class TiedTranspose {
        +linear: Linear
        +forward(x)
        +weight: Tensor
        +bias: Tensor
    }
```

When weight tying is enabled, the decoder's weight matrix is the transpose of the encoder's weight matrix.

Sources: [sparse_autoencoder/model.py:144-159]()

### TopK Activation

The `TopK` activation function is a specialized activation that enforces sparsity by only allowing the K largest values to pass through:

```mermaid
classDiagram
    class TopK {
        +k: int
        +postact_fn: Callable
        +forward(x)
        +state_dict()
        +from_state_dict(state_dict, strict)
    }
```

The function:
1. Identifies the K largest values in each input vector
2. Applies a post-activation function (typically ReLU) to these values
3. Sets all other values to zero

This ensures that only a small subset of latent neurons are active for any given input, promoting sparse representations.

Sources: [sparse_autoencoder/model.py:162-185]()

### Layer Normalization

The `LN` function implements layer normalization, which standardizes input data by centering and scaling it:

```mermaid
flowchart LR
    X["Input x"] --> M["Compute mean\nmu"]
    M --> S1["Subtract mean\nx - mu"]
    S1 --> SD["Compute standard\ndeviation std"]
    SD --> S2["Divide by std\nx / (std + eps)"]
    S2 --> O["Normalized output\n+ mu, std for denormalization"]
```

Layer normalization helps stabilize training by reducing internal covariate shift.

Sources: [sparse_autoencoder/model.py:8-13]()

## State Management

The Autoencoder implements custom state dictionary methods to handle saving and loading, including support for the activation function's state:

```mermaid
flowchart TD
    S["state_dict()"] --> B["Base state dict\n(from PyTorch)"]
    B --> A["Add activation\nclass name"]
    A --> AS["Add activation\nstate dict if available"]
    AS --> R["Return complete\nstate dict"]

    L["from_state_dict()"] --> E["Extract n_latents\nand d_model"]
    E --> EA["Create activation\ninstance"]
    EA --> C["Create autoencoder\ninstance"]
    C --> LS["Load state dict\ninto autoencoder"]
    LS --> RA["Return initialized\nautoencoder"]
```

This implementation ensures that all model components, including the activation function, are properly saved and restored.

Sources: [sparse_autoencoder/model.py:111-141]()

## Available Activation Functions

The model supports several activation functions through the `ACTIVATIONS_CLASSES` dictionary:

| Activation Name | Class | Purpose |
|-----------------|-------|---------|
| ReLU | nn.ReLU | Standard non-linear activation |
| Identity | nn.Identity | Linear activation (no non-linearity) |
| TopK | TopK | Sparse activation (keeps only k largest values) |

Sources: [sparse_autoencoder/model.py:188-192]()

## Integration with System Architecture

The Autoencoder model is exported as the primary interface of the sparse_autoencoder package:

```mermaid
graph TD
    M["sparse_autoencoder/model.py"] --> |"exports"| A["Autoencoder class"]
    I["sparse_autoencoder/__init__.py"] --> |"imports and re-exports"| A
    P["Other modules"] --> |"use"| A
```

This makes the Autoencoder class easily accessible to users of the package without requiring them to import from specific submodules.

Sources: [sparse_autoencoder/__init__.py:1-4]()

---

