> 来源: [https://deepwiki.com/mozilla-ai/llamafile/6-multimodal-support-(llava)](https://deepwiki.com/mozilla-ai/llamafile/6-multimodal-support-(llava))
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Multimodal Support (LLaVA)

  Relevant source files 
 - [llama.cpp.patches/llamafile-files/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/llamafile-files/BUILD.mk)
 - [llamafile/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk)
 - [tests/integration/tests/test_multimodal.py](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/integration/tests/test_multimodal.py)
 
  
## Purpose and Scope

 This document describes the multimodal vision-language capabilities in llamafile, implemented through the LLaVA (Large Language and Vision Assistant) architecture. This support enables language models to process and understand images by integrating a CLIP vision encoder with the LLaMA text model. The system processes images into embeddings that are combined with text tokens, allowing the model to answer questions about visual content.

 In addition to the core inference engine, llamafile provides a rich interactive chatbot interface with multimodal support, including image uploading and data URI extraction. Integration tests verify these capabilities across CLI, TUI, and Server modes [tests/integration/tests/test_multimodal.py1-173](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/integration/tests/test_multimodal.py#L1-L173)

 For deep technical details on the image processing pipeline, see [Image Processing Pipeline](https://deepwiki.com/mozilla-ai/llamafile/6.1-image-processing-pipeline).

 
---

 
## Architecture Overview

 The multimodal system consists of three main components: the CLIP vision encoder, a multimodal projector, and the LLaMA language model. Images are processed independently through CLIP to generate embeddings, which are then projected into LLaMA's embedding space and interleaved with text tokens for unified processing. The build system includes `clip.cpp` and specific multimodal tools to support these operations [llama.cpp.patches/llamafile-files/BUILD.mk68](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/llamafile-files/BUILD.mk#L68-L68) [llamafile/BUILD.mk48](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk#L48-L48)

 
### High-Level Component Diagram

 
```

```

 **Sources:** [llamafile/chatbot_main.cpp52-60](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L52-L60) [llamafile/chatbot_file.cpp39-96](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_file.cpp#L39-L96) [llamafile/chatbot_repl.cpp154-210](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_repl.cpp#L154-L210) [llamafile/chatbot_api.cpp58-102](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L58-L102) [llama.cpp.patches/llamafile-files/BUILD.mk68](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/llamafile-files/BUILD.mk#L68-L68)

 
---

 
## Chatbot Multimodal Integration

 The llamafile chatbot provides a user-friendly way to interact with multimodal models through both a Command Line Interface (CLI) and a REPL.

 
### Image Uploading and Handling

 Users can provide images to the model using the `/upload` command in the REPL or by embedding data URIs in their text input.

 
| Feature | Implementation | Description |
|---|---|---|
| /upload Command | llamafile/chatbot_file.cpp39-96 | Loads a local image file, displays it in the terminal, and queues it for the next prompt. |
| Data URI Handling | llamafile/chatbot_api.cpp58-102 | ApiBackend::build_content parses input text for data:image/ URIs and converts them to JSON image_url parts. |
| Pending Content | llamafile/chatbot_main.cpp60 | Stores uploaded file content in g_pending_file_content until the user sends a message. |
| Image Placeholder | llamafile/chatbot_main.cpp84-87 | Uses IMAGE_PLACEHOLDER_TOKEN (-31337) to mark image positions in the sequence. |

 
### Multimodal Context

 The chatbot maintains a global multimodal context `g_mtmd` initialized during startup if the `--mmproj` flag is provided. This context is used by the `DirectBackend` to process images locally.

 
```

```

 **Sources:** [llamafile/chatbot_main.cpp52-60](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L52-L60) [llamafile/chatbot_file.cpp67-96](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_file.cpp#L67-L96) [llamafile/chatbot_api.cpp58-64](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L58-L64)

 
---

 
## Image Processing Pipeline (Summary)

 The pipeline converts raw image bytes into high-dimensional vectors that the language model can understand. For a detailed breakdown of this process, see [Image Processing Pipeline](https://deepwiki.com/mozilla-ai/llamafile/6.1-image-processing-pipeline).

 
 - **Loading**: Images are read from disk via `/upload` [llamafile/chatbot_file.cpp56-60](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_file.cpp#L56-L60) or extracted from data URIs [llamafile/chatbot_api.cpp58-102](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_api.cpp#L58-L102)
 - **Preprocessing**: Images are resized and normalized using CLIP-specific parameters.
 - **Encoding**: The CLIP Vision Transformer processes image patches through self-attention layers.
 - **Projection**: A projector maps CLIP outputs to the LLaMA embedding dimension.
 - **Interleaving**: Resulting image embeddings are inserted at the position of the image placeholder token [llamafile/chatbot_main.cpp84-87](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L84-L87)
 
 
---

 
## Interactive Commands

 The chatbot REPL includes specific commands to manage multimodal interactions and the conversation state.

 
| Command | Function | File Reference |
|---|---|---|
| /upload FILE | Shares a local image or text file with the assistant. | llamafile/chatbot_file.cpp39-96 |
| /clear | Restarts the conversation, clearing the context window. | llamafile/chatbot_comm.cpp63-64 |
| /undo | Erases the last exchange, restoring the conversation to the previous state. | llamafile/chatbot_hist.cpp181-194 |
| /forget | Erases the oldest chat message to free up context space. | llamafile/chatbot_hist.cpp195-215 |

 **Sources:** [llamafile/chatbot_comm.cpp33-87](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_comm.cpp#L33-L87) [llamafile/chatbot_hist.cpp181-215](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_hist.cpp#L181-L215) [llamafile/chatbot_file.cpp39-96](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_file.cpp#L39-L96)

 
---

 
## Model Loading and Initialization

 When running in multimodal mode, llamafile initializes both the LLM and the vision encoder.

 
 - **GPU Initialization**: GPU support is initialized before loading models to ensure backends like Metal or CUDA are ready [llamafile/chatbot_main.cpp125-138](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L125-L138)
 - **Model Loading**: The main model is loaded via `llama_model_load_from_file` [llamafile/chatbot_main.cpp189](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L189-L189)
 - **Multimodal Context**: If a projector is provided via `--mmproj`, the `mtmd_context` is created to handle vision tasks [llamafile/chatbot_main.cpp55](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L55-L55)
 - **Compute Description**: The system identifies the active compute backend (e.g., "Apple Metal GPU") for logging [llamafile/chatbot_main.cpp68-81](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L68-L81)
 
 **Sources:** [llamafile/chatbot_main.cpp55](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L55-L55) [llamafile/chatbot_main.cpp68-81](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L68-L81) [llamafile/chatbot_main.cpp125-189](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/chatbot_main.cpp#L125-L189)

 
---

 
## Child Pages

 
 - [Image Processing Pipeline](https://deepwiki.com/mozilla-ai/llamafile/6.1-image-processing-pipeline) — Detailed documentation of image upload, base64 encoding, compression, CLIP vision encoder integration, and embedding generation.
