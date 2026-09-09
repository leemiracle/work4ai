> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL2/4-inference-guide](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/4-inference-guide)
> DeepWiki deepseek-ai/DeepSeek-VL2

# Inference Guide

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1)
 - [inference.py](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py)
 
  This guide provides detailed instructions for running inference with DeepSeek-VL2, a multimodal model that combines vision and language capabilities through a Mixture-of-Experts (MoE) architecture. You'll learn how to set up the model, process inputs, and generate responses for various use cases including single and multiple image scenarios.

 For information about the model architecture, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/2-model-architecture). For advanced memory optimization techniques, see [Memory Optimization Techniques](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/4.1-memory-optimization-techniques). For details on different model variants, see [Model Variants and Requirements](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/4.2-model-variants-and-requirements).

 
## Model Variants and Requirements

 DeepSeek-VL2 is available in three variants, each with different parameter counts and hardware requirements:

 
| Model Variant | Total Parameters | Activated Parameters | Minimum GPU Memory | Hugging Face ID |
|---|---|---|---|---|
| DeepSeek-VL2-tiny | 3.37B | 1.0B | < 40GB | deepseek-ai/deepseek-vl2-tiny |
| DeepSeek-VL2-small | 16.1B | 2.8B | 40GB* | deepseek-ai/deepseek-vl2-small |
| DeepSeek-VL2 | 7.5B | 4.5B | 80GB+ | deepseek-ai/deepseek-vl2 |

 *Requires incremental prefilling technique for 40GB GPUs

 The MoE architecture allows these models to have a large number of total parameters while only activating a subset during inference, reducing computational requirements.

 Sources: [README.md80-90](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L80-L90) [inference.py65-77](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L65-L77)

 
## Inference Components and Workflow

 
### Core Components

 
```

```

 DeepSeek-VL2 uses two main components for inference:

 
 - **DeepseekVLV2Processor**: Handles preprocessing of inputs (images and text)
 - **DeepseekVLV2ForCausalLM**: Performs the actual inference and generates responses
 
 Sources: [inference.py68-77](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L68-L77)

 
### Inference Workflow

 
```

```

 The inference workflow follows these steps:

 
 - Load the model and processor from Hugging Face or a local path
 - Prepare input images and text in a conversation format
 - Process inputs with DeepseekVLV2Processor
 - Generate embeddings with prepare_inputs_embeds
 - Run the language model to generate a response
 
 Sources: [inference.py95-149](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L95-L149)

 
## Conversation Format

 DeepSeek-VL2 expects inputs in a specific conversation format:

 
```

```

 The conversation is a list of messages, where each message is a dictionary with:

 
 - `role`: Either `<|User|>` or `<|Assistant|>`
 - `content`: The text content of the message, with `<image>` placeholders
 - `images`: A list of image paths corresponding to the `<image>` placeholders
 
 The last message should be an empty assistant message where the model will generate the response.

 Sources: [inference.py80-91](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L80-L91) [README.md123-133](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L123-L133)

 
## Basic Inference Examples

 
### Single Image Inference

 Here's a basic example of inference with a single image:

 
```

```

 Sources: [README.md107-160](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L107-L160)

 
### Multiple Image Inference

 You can include multiple images in a single prompt:

 
```

```

 In this example, multiple images are included in the conversation structure and processed together. The `<image>` placeholder in the content string marks where each image appears in the context.

 Sources: [README.md192-232](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L192-L232)

 
## Memory-Optimized Inference with Incremental Prefilling

 For larger models like DeepSeek-VL2-small running on 40GB GPUs, incremental prefilling reduces memory requirements by processing the input in chunks:

 
```

```

 Example code using incremental prefilling:

 
```

```

 Sources: [README.md249-325](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L249-L325) [inference.py107-151](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L107-L151)

 
## Generation Parameters

 When calling the `generate` method, you can customize various parameters:

 
| Parameter | Description | Effect |
|---|---|---|
| max_new_tokens | Maximum number of tokens to generate | Limits response length |
| do_sample | Whether to use sampling | If True, enables non-deterministic outputs |
| temperature | Controls randomness in sampling | Lower = more deterministic, higher = more random |
| top_p | Controls diversity via nucleus sampling | Lower = more focused on likely tokens |
| repetition_penalty | Penalizes repetition | Higher = less repetition |
| use_cache | Whether to use the KV cache | Improves performance |

 Example with generation parameters:

 
```

```

 Sources: [inference.py133-146](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L133-L146)

 
## Special Tokens and Advanced Features

 DeepSeek-VL2 supports several special tokens for advanced features:

 
### Visual Grounding

 Use `<|ref|>` and `<|/ref|>` tokens to refer to specific objects in images:

 
```
<|User|>: <image>
<|ref|>The giraffe at the back.<|/ref|>.

<|Assistant|>: <|ref|>The giraffe at the back.<|/ref|><|det|>[[580, 270, 999, 900]]<|/det|>
```

 The model responds with bounding box coordinates for the referenced object in the format `<|det|>[[x1, y1, x2, y2]]<|/det|>`, where:

 
 - `x1, y1`: Top-left corner coordinates
 - `x2, y2`: Bottom-right corner coordinates
 
 
### Grounded Captioning

 Use the `<|grounding|>` token at the beginning of the prompt to enable grounded captioning:

 
```
<|User|>: <image>
<|grounding|>What animals do you see in this image?

<|Assistant|>: I can see two animals in this image:
1. <|ref|>A giraffe<|/ref|><|det|>[[580, 270, 999, 900]]<|/det|>
2. <|ref|>A zebra<|/ref|><|det|>[[100, 400, 300, 600]]<|/det|>
```

 You can parse these bounding box coordinates using the `parse_ref_bbox` function:

 
```

```

 Sources: [README.md124-126](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L124-L126) [inference.py152-154](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L152-L154)

 
## Command-Line Inference

 You can run inference using the command-line script:

 
```

```

 The script accepts the following arguments:

 
 - `--model_path`: Path to the model (Hugging Face ID or local path)
 - `--chunk_size`: Chunk size for incremental prefilling (-1 to disable)
 
 Sources: [inference.py157-167](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/inference.py#L157-L167) [README.md342-349](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L342-L349)

 
## Web Demo

 For a graphical user interface, you can run the provided Gradio web demo:

 
```

```

 For more details on the web demo, see [Web Demo](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/5-web-demo).

 Sources: [README.md354-380](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L354-L380)
