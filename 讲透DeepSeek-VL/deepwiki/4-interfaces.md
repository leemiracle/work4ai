> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-VL/4-interfaces](https://deepwiki.com/deepseek-ai/DeepSeek-VL/4-interfaces)
> DeepWiki deepseek-ai/DeepSeek-VL

# Interfaces

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1)
 - [cli_chat.py](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/cli_chat.py)
 - [deepseek_vl/serve/app_deepseek.py](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/serve/app_deepseek.py)
 
  This page documents the available interfaces for interacting with the DeepSeek-VL model. It covers how users can access and utilize the model's capabilities through different interaction methods. For information about the model's architecture and capabilities, see [Overview](https://deepwiki.com/deepseek-ai/DeepSeek-VL/1-overview) and [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-VL/1.1-model-architecture).

 
## 1. Interface Overview

 DeepSeek-VL provides three primary interfaces for users to interact with the model:

 
 - **Command Line Interface (CLI)** - For terminal-based interactions
 - **Web Interface (Gradio)** - For browser-based interactions with a graphical user interface
 - **Python API** - For programmatic interactions within Python applications
 
 These interfaces allow users to send text and image inputs to the model and receive generated responses based on the multimodal understanding of DeepSeek-VL.

 
```

```

 Sources: [README.md60-62](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L60-L62) [README.md106-116](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L106-L116)

 
## 2. Command Line Interface (CLI)

 The Command Line Interface provides a terminal-based way to interact with DeepSeek-VL through a chat-like experience.

 
### 2.1 CLI Features

 
 - Interactive chat with the model
 - Support for image input through file paths
 - Multiple image handling in a single conversation
 - Conversation management (new conversations, help, exit)
 - Configurable generation parameters
 
 
### 2.2 CLI Usage

 
```
python cli_chat.py --model_path "deepseek-ai/deepseek-vl-7b-chat"
```

 Parameters:

 
 - `--model_path`: Model identifier or local path (default: "deepseek-ai/deepseek-vl-7b-chat")
 - `--temperature`: Controls randomness in generation (default: 0.2)
 - `--top_p`: Controls diversity via nucleus sampling (default: 0.95)
 - `--repetition_penalty`: Penalizes repetition (default: 1.1)
 - `--max_gen_len`: Maximum tokens to generate (default: 512)
 
 
### 2.3 CLI Interaction Flow

 
```

```

 Sources: [cli_chat.py94-184](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/cli_chat.py#L94-L184) [cli_chat.py210-224](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/cli_chat.py#L210-L224)

 
### 2.4 CLI Commands

 Within the CLI interface, users can use these special commands:

 
 - `exit`: Quit the chat program
 - `help`: Display help message
 - `new`: Start a new conversation (clears history)
 - `<image_placeholder>`: Indicates an image insertion point in the text
 
 Sources: [cli_chat.py33-54](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/cli_chat.py#L33-L54) [cli_chat.py94-133](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/cli_chat.py#L94-L133)

 
## 3. Gradio Web Interface

 The Gradio-based web interface provides a graphical user interface for interacting with DeepSeek-VL through a web browser.

 
### 3.1 Web Interface Features

 
 - Chat-like conversation interface
 - Image upload capability
 - Model parameter adjustment panel
 - Example showcases
 - Conversation controls (regenerate, new conversation, remove last turn)
 - Response streaming for real-time feedback
 
 
### 3.2 Web Interface Setup

 To start the Gradio web interface:

 
```

```

 The server will start on `http://0.0.0.0:8122` by default.

 
### 3.3 Web Interface Components

 
```

```

 Sources: [deepseek_vl/serve/app_deepseek.py318-500](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/serve/app_deepseek.py#L318-L500)

 
### 3.4 Web Interface Interaction Flow

 The web interface follows this interaction pattern:

 
 - User enters text and/or uploads an image
 - User clicks "Send" or presses Enter
 - Interface prepares the input (combining text and image)
 - Model processes the input and generates a response
 - Response is streamed back to the interface in real-time
 - User can continue the conversation or start a new one
 
 Sources: [deepseek_vl/serve/app_deepseek.py196-279](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/serve/app_deepseek.py#L196-L279) [deepseek_vl/serve/app_deepseek.py482-498](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/serve/app_deepseek.py#L482-L498)

 
## 4. Python API

 The Python API allows developers to integrate DeepSeek-VL directly into their Python applications.

 
### 4.1 API Overview

 The Python API provides programmatic access to:

 
 - Load and initialize the model
 - Process text and image inputs
 - Generate responses
 - Configure generation parameters
 
 
### 4.2 API Usage Example

 
```

```

 Sources: [README.md117-187](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L117-L187)

 
### 4.3 API Core Components

 The main components used in the Python API are:

 
| Component | Description | Purpose |
|---|---|---|
| VLChatProcessor | Processes conversations and images | Prepares inputs for the model |
| MultiModalityCausalLM | Core model class | Handles vision-language processing |
| prepare_inputs_embeds() | Method of MultiModalityCausalLM | Creates input embeddings |
| generate() | Method of language model | Generates text responses |
| load_pil_images() | Utility function | Loads and prepares images |

 Sources: [README.md120-123](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L120-L123) [README.md127-133](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L127-L133) [README.md165-172](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L165-L172) [README.md175-186](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L175-L186)

 
## 5. Interaction Flow Between Components

 The following diagram illustrates how user inputs flow through the DeepSeek-VL system, regardless of which interface is used:

 
```

```

 Sources: [README.md165-187](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L165-L187) [cli_chat.py55-77](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/cli_chat.py#L55-L77) [deepseek_vl/serve/app_deepseek.py250-268](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/serve/app_deepseek.py#L250-L268)

 
## 6. Example Images

 DeepSeek-VL includes several example images that showcase the model's capabilities across different types of visual content:

 
| Example Image | Description | Path |
|---|---|---|
| Training Pipeline | Diagram of training process | ./images/training_pipelines.jpg |
| App Screenshot | UI screenshot | deepseek_vl/serve/examples/app.png |
| Rap Image | Image for rap generation | deepseek_vl/serve/examples/rap.jpeg |
| Pipeline Diagram | Technical pipeline | deepseek_vl/serve/examples/pipeline.png |
| Chart | Data visualization | deepseek_vl/serve/examples/chart.png |
| Mirror Image | Optical illusion | deepseek_vl/serve/examples/mirror.png |
| Puzzle Image | Puzzle pieces | deepseek_vl/serve/examples/puzzle.png |

 These examples can be used with any of the interfaces to test the model's multimodal understanding.

 Sources: [deepseek_vl/serve/app_deepseek.py414-439](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/deepseek_vl/serve/app_deepseek.py#L414-L439) [README.md135-142](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L135-L142)

 
## 7. Interface Selection Guide

 
| Interface | Best For | Technical Requirements | Startup Time |
|---|---|---|---|
| CLI | Terminal users, batch processing, scripting | Python environment | Fast |
| Web UI | Visual interaction, parameter tuning, demonstrations | Python + browser | Medium |
| Python API | Integration into applications, custom workflows | Python development skills | N/A (embedded) |

 Choose the interface that best fits your use case and technical environment.

 Sources: [README.md106-116](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L106-L116) [README.md118-187](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L118-L187) [README.md189-196](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L189-L196) [README.md198-204](https://github.com/deepseek-ai/DeepSeek-VL/blob/681bffb4/README.md?plain=1#L198-L204)
