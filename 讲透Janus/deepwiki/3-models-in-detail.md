> 来源: [https://deepwiki.com/deepseek-ai/Janus/3-models-in-detail](https://deepwiki.com/deepseek-ai/Janus/3-models-in-detail)
> DeepWiki deepseek-ai/Janus

# Models in Detail

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1)
 - [images/teaser_janusflow.png](https://github.com/deepseek-ai/Janus/blob/1daa72fa/images/teaser_janusflow.png)
 
  This document provides comprehensive technical information about the architecture, components, and implementation details of each model in the Janus family: Janus, JanusFlow, and Janus-Pro. For installation and usage information, see [Usage Guide](https://deepwiki.com/deepseek-ai/Janus/4-usage-guide).

 
## Model Family Overview

 The Janus model family consists of three main variants, all built on a unified architecture that can handle both multimodal understanding and text-to-image generation:

 
```

```

 Sources: [README.md75-116](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L75-L116)

 
## Shared Architecture Components

 All models in the Janus family share a common foundation built around these core components:

 
```

```

 Sources: [README.md323-371](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L323-L371) [README.md524-571](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L524-L571)

 
### Common Processing Flow

 All Janus models follow the same basic processing flow for multimodal understanding:

 
```

```

 Sources: [README.md338-371](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L338-L371) [README.md539-571](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L539-L571) [README.md152-184](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L152-L184)

 
## Janus Model (1.3B)

 The standard Janus model implements a unified architecture that decouples visual encoding for understanding and generation tasks within a single transformer-based model.

 
### Janus Architecture Components

 
```

```

 Sources: [README.md324-337](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L324-L337) [README.md375-392](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L375-L392)

 
### Janus Text-to-Image Generation Process

 Janus generates images using a token-by-token autoregressive approach:

 
```

```

 Sources: [README.md394-472](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L394-L472)

 
## JanusFlow Model (1.3B)

 JanusFlow introduces a different approach to image generation by integrating autoregressive language models with rectified flow, while maintaining the same multimodal understanding capabilities.

 
### JanusFlow Architecture Components

 
```

```

 Sources: [README.md525-538](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L525-L538) [README.md574-597](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L574-L597)

 
### JanusFlow Text-to-Image Generation Process

 JanusFlow generates images using a rectified flow approach with ODE solving:

 
```

```

 Sources: [README.md599-697](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L599-L697)

 
## Janus-Pro Models (1B and 7B)

 Janus-Pro models are enhanced versions of the original Janus with improved training strategies, expanded training data, and scaling to larger model sizes (available in 1B and 7B parameters).

 
### Janus-Pro Architecture Components

 The architecture is similar to the original Janus but with enhanced components:

 
```

```

 Sources: [README.md137-151](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L137-L151) [README.md188-205](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L188-L205)

 
### Janus-Pro Improvements

 The key enhancements in Janus-Pro include:

 
 - Optimized training strategy
 - Expanded training data
 - Scaling to larger model sizes (1B and 7B)
 - Enhanced stability for text-to-image generation
 - Significantly improved performance on both multimodal understanding and generation tasks
 
 Sources: [README.md75-86](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L75-L86) [README.md124-185](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L124-L185)

 
## Model Comparison

 
### Feature Comparison

 
| Feature | Janus-1.3B | JanusFlow-1.3B | Janus-Pro-1B | Janus-Pro-7B |
|---|---|---|---|---|
| Parameters | 1.3B | 1.3B | 1B | 7B |
| Understanding Encoder | CLIP-based | CLIP-based | Enhanced CLIP-based | Enhanced CLIP-based |
| Generation Method | Token-by-token | Rectified Flow | Token-by-token | Token-by-token |
| Generation Implementation | Autoregressive | ODE Solver | Autoregressive | Autoregressive |
| External Components | None | SDXL VAE | None | None |
| CFG Implementation | Conditional/Unconditional Pairs | Conditional/Unconditional Pairs | Same as Janus | Same as Janus |

 Sources: [README.md103-116](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L103-L116) [README.md394-472](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L394-L472) [README.md599-697](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L599-L697)

 
### Processing Pipeline Comparison

 
```

```

 Sources: [README.md338-371](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L338-L371) [README.md394-472](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L394-L472) [README.md599-697](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L599-L697)

 
## Integration with Demo Applications

 The models are integrated into demo applications through these implementations:

 
```

```

 Sources: [README.md474-503](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L474-L503) [README.md698-710](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L698-L710) [README.md287-302](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L287-L302)

 
## Technical Implementation Details

 
### Classifier-Free Guidance

 All models implement classifier-free guidance for image generation, but with different approaches:

 
 - **Janus/Janus-Pro**: Processes paired conditional/unconditional inputs and combines logits with a weighting factor
 - **JanusFlow**: Applies guidance on the velocity predictions in the rectified flow process
 
 Sources: [README.md425-444](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L425-L444) [README.md627-680](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L627-L680)

 
### Image Token Representation

 
 - **Janus/Janus-Pro**: Uses 576 discrete tokens (24×24 grid) for image representation
 - **JanusFlow**: Uses continuous latent representation with dimensions 4×48×48
 
 Sources: [README.md432](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L432-L432) [README.md636](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L636-L636)

 
### External Dependencies

 
 - **Janus/Janus-Pro**: Self-contained, uses internal components only
 - **JanusFlow**: Requires SDXL VAE for final image decoding
 
 Sources: [README.md394-472](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L394-L472) [README.md594-596](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L594-L596)
