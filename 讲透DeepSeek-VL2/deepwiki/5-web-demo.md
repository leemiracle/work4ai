> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL2/5-web-demo](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/5-web-demo)
> DeepWiki deepseek-ai/DeepSeek-VL2

# Web Demo

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1)
 - [deepseek_vl2/serve/app_modules/presets.py](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/presets.py)
 - [deepseek_vl2/serve/app_modules/utils.py](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/utils.py)
 
  This page provides a comprehensive guide on setting up and using the Gradio web interface for DeepSeek-VL2. The web demo offers a user-friendly graphical interface to interact with the model's multimodal capabilities without writing code. For information about running inference programmatically, see [Inference Guide](https://deepwiki.com/deepseek-ai/DeepSeek-VL2/4-inference-guide).

 
## Installation and Setup

 
### Requirements

 To run the web demo, you need to install the additional Gradio dependencies:

 
```

```

 This command installs both the core DeepSeek-VL2 package and the Gradio web interface dependencies.

 Sources: [README.md355-357](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L355-L357)

 
### Hardware Requirements

 The hardware requirements depend on the model variant you choose to run:

 
| Model Variant | Total Parameters | Activated Parameters | Minimum GPU Memory |
|---|---|---|---|
| DeepSeek-VL2-tiny | 3.37B | 1.0B | < 40GB |
| DeepSeek-VL2-small | 16.1B | 2.8B | 40GB (with chunking) |
| DeepSeek-VL2 | 7.5B | 4.5B | 80GB+ |

 For the smaller models like DeepSeek-VL2-tiny, you can run the web demo on consumer GPUs with less than 40GB memory. For larger models like DeepSeek-VL2-small, you'll need memory optimization techniques (incremental prefilling) when running on limited hardware.

 Sources: [README.md363-380](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L363-L380)

 
## Running the Web Demo

 
### Basic Command

 To start the web demo with the tiny model variant:

 
```

```

 This command launches a Gradio web interface on port 37914 using the DeepSeek-VL2-tiny model.

 Sources: [README.md363-366](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L363-L366)

 
### Memory Optimization

 For larger models running on limited hardware, enable incremental prefilling with the `--chunk_size` parameter:

 
```

```

 This processes the input in chunks to reduce memory requirements, though it may result in slower response times.

 Sources: [README.md370-374](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L370-L374)

 
### Command Line Options

 The `web_demo.py` script accepts the following key parameters:

 
 - `--model_name`: Hugging Face model identifier (e.g., "deepseek-ai/deepseek-vl2-tiny")
 - `--port`: Port number for the web server (default: 7860)
 - `--chunk_size`: Size of chunks for incremental prefilling (optional, for memory optimization)
 
 
## Web Demo Architecture

 The web demo integrates the DeepSeek-VL2 model with a Gradio interface for user interaction:

 
```

```

 Sources: [README.md352-383](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L352-L383)

 
## Interface Features

 
### Main Components

 The web demo interface includes:

 
 - **Conversation History**: Displays the ongoing chat between the user and the model
 - **Input Area**: Text input for user prompts
 - **Image Upload**: Functionality to upload and include images in the conversation
 - **Special Token Support**: Support for visual grounding tokens
 
 
### Special Tokens and Features

 The web demo supports several special tokens for advanced interactions:

 
 - `<image>`: Marks where an image should be inserted in the text
 - `<|ref|>{query}<|/ref|>`: Used for visual grounding, where `{query}` is the text describing what to locate in the image
 - `<|grounding|>{question}`: Initiates a grounding conversation where the model will provide both textual responses and visual localization
 
 Sources: [deepseek_vl2/serve/app_modules/presets.py24-25](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/presets.py#L24-L25)

 
## Visual Grounding Features

 One of the key features of the web demo is visual grounding, which allows the model to identify and highlight specific objects or regions in an image based on textual descriptions.

 
```

```

 When a response contains visual grounding information, the `parse_ref_bbox` function processes the response text to extract bounding box coordinates and renders them on the image with appropriate labels.

 Sources: [deepseek_vl2/serve/app_modules/utils.py270-313](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/utils.py#L270-L313)

 
### Bounding Box Processing

 The model outputs bounding box coordinates in a normalized format (0-999 range). The web demo processes these coordinates and renders them on the image:

 
```

```

 The bounding box processing flow:

 
 - Extract references and detection tags from the response
 - Parse the coordinates from the `<|det|>` tags
 - Match coordinates with their corresponding labels from `<|ref|>` tags
 - Scale the coordinates from the normalized space (0-999) to actual image dimensions
 - Draw colored rectangles and labels on the image
 
 Sources: [deepseek_vl2/serve/app_modules/utils.py270-313](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/utils.py#L270-L313) [deepseek_vl2/serve/app_modules/presets.py31-45](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/presets.py#L31-L45)

 
## Image Processing

 The web demo includes functionality to process and optimize images for the model:

 
 - **Resizing**: Images are resized to maintain a balance between quality and performance
 - **Format Conversion**: Images are converted to appropriate formats for the model
 - **Base64 Encoding**: Images are encoded for embedding in the web interface
 
 The constants `MAX_IMAGE_SIZE` (800) and `MIN_IMAGE_SIZE` (400) control the resizing behavior to keep images within appropriate dimensions.

 Sources: [deepseek_vl2/serve/app_modules/utils.py240-267](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/utils.py#L240-L267) [deepseek_vl2/serve/app_modules/presets.py28-29](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/presets.py#L28-L29)

 
## Response Formatting

 Responses from the model are processed to create a readable and visually appealing display in the web interface:

 
 - Markdown conversion for proper formatting
 - Code block syntax highlighting
 - Special token handling and removal
 - Visual grounding tag processing and rendering
 
 The demo includes a comprehensive set of utilities to handle various formatting needs, ensuring that code blocks, lists, tables, and other structured content are displayed correctly.

 Sources: [deepseek_vl2/serve/app_modules/utils.py87-209](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/utils.py#L87-L209)

 
## Performance Considerations

 The web demo is a basic implementation without deployment optimizations:

 
 - For production environments, consider using optimized deployment solutions like vllm, sglang, or lmdeploy
 - Incremental prefilling is a memory optimization technique that processes the input in chunks but may result in slower responses
 - Larger models require more GPU memory and computing resources
 
 The README explicitly states that this is a "naive implementation" intended for demonstration purposes rather than production deployment.

 Sources: [README.md382-383](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/README.md?plain=1#L382-L383)

 
## Logging and Debugging

 The web demo includes a logging system that captures events and errors:

 
 - Logs are stored in `deepseek_vl2/serve/logs/{timestamp}_gradio_log.log`
 - Console logging is set to INFO level
 - File logging captures more detailed information
 
 This logging helps diagnose issues when running the web demo and can be useful for troubleshooting performance or functionality problems.

 Sources: [deepseek_vl2/serve/app_modules/utils.py48-71](https://github.com/deepseek-ai/DeepSeek-VL2/blob/ef9f91e2/deepseek_vl2/serve/app_modules/utils.py#L48-L71)
