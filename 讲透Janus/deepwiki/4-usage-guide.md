> 来源: [https://deepwiki.com/deepseek-ai/Janus/4-usage-guide](https://deepwiki.com/deepseek-ai/Janus/4-usage-guide)
> DeepWiki deepseek-ai/Janus

# Usage Guide

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1)
 - [images/teaser_janusflow.png](https://github.com/deepseek-ai/Janus/blob/1daa72fa/images/teaser_janusflow.png)
 
  This guide provides comprehensive instructions for using the Janus model family for multimodal understanding and text-to-image generation tasks. It covers installation, basic usage patterns, and how to run interactive demos. For detailed information about the model architecture, refer to [Architecture](https://deepwiki.com/deepseek-ai/Janus/2-architecture).

 
## Table of Contents

 
## 1. Installation and Setup

 To use Janus models, you'll need Python 3.8 or higher. Follow these steps to set up your environment:

 
### Basic Installation

 
```

```

 
### Additional Requirements for Specific Models

 For JanusFlow, you'll need to install additional dependencies:

 
```

```

 For running the demo applications, install the gradio dependencies:

 
```

```

 Sources: [README.md126-130](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L126-L130) [README.md512-515](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L512-L515) [README.md296](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L296-L296) [README.md482](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L482-L482)

 
## 2. Model Usage Workflow

 The diagram below illustrates the common workflow for using any Janus model:

 
```

```

 Sources: [README.md324-371](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L324-L371) [README.md523-570](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L523-L570)

 
## 3. Multimodal Understanding

 Multimodal understanding involves processing an image along with a text query to generate a relevant response.

 
### Usage Pattern

 The following diagram shows the multimodal understanding workflow:

 
```

```

 
### Code Example

 Here's how to use a Janus model for multimodal understanding:

 
```

```

 Sources: [README.md324-371](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L324-L371) [README.md523-570](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L523-L570)

 
### Model-Specific Adjustments

 Different models in the Janus family require slight adjustments to the import statements:

 
| Model | Import Adjustments |
|---|---|
| Janus/Janus-Pro | from janus.models import MultiModalityCausalLM, VLChatProcessor |
| JanusFlow | from janus.janusflow.models import MultiModalityCausalLM, VLChatProcessor |

 Sources: [README.md324-371](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L324-L371) [README.md523-570](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L523-L570)

 
## 4. Text-to-Image Generation

 The Janus family supports generating images from text prompts, with different underlying mechanisms depending on the model variant.

 
### Generation Workflows

 The generation process differs between standard Janus/Janus-Pro models and JanusFlow:

 
```

```

 Sources: [README.md374-472](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L374-L472) [README.md574-697](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L574-L697)

 
### Janus/Janus-Pro Text-to-Image Example

 
```

```

 Sources: [README.md374-472](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L374-L472)

 
### JanusFlow Text-to-Image Example

 
```

```

 Sources: [README.md574-697](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L574-L697)

 
## 5. Key Parameters for Generation

 The following table summarizes important parameters for text-to-image generation:

 
| Parameter | Description | Janus/Janus-Pro | JanusFlow |
|---|---|---|---|
| temperature | Controls randomness of generation (higher = more random) | ✓ | - |
| parallel_size | Number of images to generate in parallel | ✓ | - |
| cfg_weight | Classifier-free guidance weight (higher = more adherent to prompt) | ✓ | ✓ |
| num_inference_steps | Number of steps in the generation process | - | ✓ |
| batchsize | Number of images to generate in parallel | - | ✓ |
| image_token_num_per_image | Number of tokens per image | ✓ | - |
| img_size | Size of the generated image | ✓ | Controlled by VAE |
| patch_size | Size of image patches used in the model | ✓ | - |

 Sources: [README.md411-421](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L411-L421) [README.md620-622](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L620-L622)

 
## 6. Interactive Demos

 Janus provides several interactive demo applications that allow you to experiment with the models through a user interface.

 
### Demo Applications Structure

 
```

```

 Sources: [README.md474-496](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L474-L496) [README.md698-707](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L698-L707)

 
### Running Gradio Demos

 There are specific demo scripts for each model variant:

 
```

```

 The Gradio interface provides tabs for both multimodal understanding and text-to-image generation.

 Sources: [README.md484-485](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L484-L485) [README.md704-705](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L704-L705) [README.md298-299](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L298-L299)

 
### Running FastAPI Demo (Janus only)

 
```

```

 Sources: [README.md494-502](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L494-L502)

 
## 7. Common Usage Patterns

 
### Working with the VLChatProcessor

 The `VLChatProcessor` is a critical component for preparing inputs for the model. Here's how it's used in both tasks:

 
```

```

 Sources: [README.md350-352](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L350-L352) [README.md402-407](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L402-L407)

 
### Conversation Format

 The conversation format is consistent across all Janus models:

 
```

```

 Sources: [README.md339-346](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L339-L346) [README.md153-160](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L153-L160)

 
## 8. Online Resources

 All Janus models are available on Hugging Face, with online demos for testing:

 
| Model | Hugging Face | Online Demo |
|---|---|---|
| Janus-1.3B | deepseek-ai/Janus-1.3B | Demo |
| JanusFlow-1.3B | deepseek-ai/JanusFlow-1.3B | Demo |
| Janus-Pro-1B | deepseek-ai/Janus-Pro-1B | - |
| Janus-Pro-7B | deepseek-ai/Janus-Pro-7B | Demo |

 Sources: [README.md110-116](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L110-L116) [README.md59](https://github.com/deepseek-ai/Janus/blob/1daa72fa/README.md?plain=1#L59-L59)
