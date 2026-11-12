<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nim-anywhere · page 4 User Interfaces · fetched 2026-10-26 -->

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [code/frontend/_static/images/upload-button.png](code/frontend/_static/images/upload-button.png)
- [code/frontend/pages/chat/__init__.py](code/frontend/pages/chat/__init__.py)
- [code/frontend/pages/control/__init__.py](code/frontend/pages/control/__init__.py)
- [code/frontend/pages/control/style.css](code/frontend/pages/control/style.css)
- [requirements.txt](requirements.txt)

</details>



The NVIDIA NIM Anywhere system provides three distinct web-based user interfaces for different aspects of RAG system interaction and management. This page covers the technical implementation and architecture of these frontend applications.

For detailed information about individual interface usage, see [Chat Frontend](#4.1), [Control Panel](#4.2), and [Tutorial Application](#4.3). For backend RAG processing logic, see [RAG Chain Implementation](#3.1).

## Overview

The system implements three Gradio-based web applications that serve different user roles and workflows:

| Interface | Framework | Port | Purpose | Auto-Launch |
|-----------|-----------|------|---------|-------------|
| Chat Frontend | Gradio | 7070 | Primary RAG interaction interface | Yes |
| Control Panel | Gradio | N/A | System configuration and knowledge base management | No |
| Tutorial Application | Streamlit | 8501 | Interactive learning and demonstration | No |

All interfaces run within the NVIDIA AI Workbench container environment and communicate with the chain server backend via HTTP APIs.

## Frontend Architecture

```mermaid
graph TB
    subgraph "Gradio Framework Layer"
        subgraph "ChatApp[code/frontend/pages/chat]"
            ChatPage["page: gr.Blocks"]
            ChatComponents["Chatbot, Textbox, Button"]
            ChatState["session_id: gr.State"]
        end
        
        subgraph "ControlApp[code/frontend/pages/control]"
            ControlPage["page: gr.Blocks"]
            ControlTabs["Control Panel Tab, Knowledge Base Tab"]
            ConfigEditor["editor: gr.Code"]
            FileUpload["upload_btn: gr.UploadButton"]
        end
    end
    
    subgraph "Communication Layer"
        RemoteRunnable["_CHAIN: RemoteRunnable"]
        VectorStore["vector_store: Milvus"]
        EmbeddingModel["embedding_model: NVIDIAEmbeddings"]
    end
    
    subgraph "Backend Services"
        ChainServer["Chain Server<br/>localhost:3030"]
        MilvusDB["Milvus Vector DB"]
        RedisDB["Redis Session Store"]
    end
    
    ChatPage --> RemoteRunnable
    ControlPage --> VectorStore
    ControlPage --> EmbeddingModel
    
    RemoteRunnable --> ChainServer
    VectorStore --> MilvusDB
    EmbeddingModel --> ChainServer
    
    ChainServer --> RedisDB
    ChainServer --> MilvusDB
```

**Sources:** [code/frontend/pages/chat/__init__.py:1-104](), [code/frontend/pages/control/__init__.py:1-342]()

## Component Implementation Structure

```mermaid
graph TB
    subgraph "Frontend Module Structure"
        CommonModule["code/frontend/common.py<br/>THEME, IMG_DIR, initial states"]
        ConfigModule["code/frontend/configuration.py<br/>config object"]
        MermaidModule["code/frontend/mermaid.py<br/>diagram rendering"]
        
        subgraph "Chat Implementation"
            ChatInit["code/frontend/pages/chat/__init__.py"]
            ChatCSS["code/frontend/pages/chat/style.css"]
            ChatJS["code/frontend/pages/chat/scripts.js"]
            UserIcon["code/frontend/_static/images/user_icon.png"]
            BotIcon["code/frontend/_static/images/bot_icon.png"]
        end
        
        subgraph "Control Implementation"
            ControlInit["code/frontend/pages/control/__init__.py"]
            ControlCSS["code/frontend/pages/control/style.css"]
            DiagramTemplate["code/frontend/pages/control/diagram.mmd.j2"]
            UploadIcon["code/frontend/_static/images/upload-button.png"]
            SaveIcon["code/frontend/_static/images/floppy.png"]
            UndoIcon["code/frontend/_static/images/undo.png"]
            HistoryIcon["code/frontend/_static/images/history.png"]
        end
    end
    
    ChatInit --> CommonModule
    ChatInit --> ConfigModule
    ControlInit --> CommonModule
    ControlInit --> ConfigModule
    ControlInit --> MermaidModule
    
    ChatInit --> ChatCSS
    ChatInit --> ChatJS
    ChatInit --> UserIcon
    ChatInit --> BotIcon
    
    ControlInit --> ControlCSS
    ControlInit --> DiagramTemplate
    ControlInit --> UploadIcon
    ControlInit --> SaveIcon
    ControlInit --> UndoIcon
    ControlInit --> HistoryIcon
```

**Sources:** [code/frontend/pages/chat/__init__.py:30-40](), [code/frontend/pages/control/__init__.py:37-82]()

## Communication Patterns

### Chat Frontend Communication Flow

The chat interface implements asynchronous streaming communication with the chain server:

```mermaid
sequenceDiagram
    participant User
    participant "gr.Textbox" as MsgBox
    participant "stream_chain()" as StreamFunc
    participant "_CHAIN: RemoteRunnable" as Chain
    participant "Chain Server" as Server
    participant "gr.Chatbot" as ChatBot
    
    User->>MsgBox: "Enter message"
    MsgBox->>StreamFunc: "msg.submit trigger"
    StreamFunc->>Chain: "chain.astream({question, use_kb, use_reranker})"
    Chain->>Server: "HTTP POST /invoke"
    
    loop "Streaming Response"
        Server-->>Chain: "chunk.content"
        Chain-->>StreamFunc: "yield chunk"
        StreamFunc-->>ChatBot: "update chat[-1][1]"
        ChatBot-->>User: "display partial response"
    end
    
    alt "Connection Error"
        Chain-->>StreamFunc: "ConnectError"
        StreamFunc-->>ChatBot: "❌ Can't reach chain server"
    end
    
    alt "Server Error"
        Chain-->>StreamFunc: "HTTPStatusError"
        StreamFunc-->>ChatBot: "❌ Chain server error"
    end
```

**Sources:** [code/frontend/pages/chat/__init__.py:76-104]()

### Control Panel Data Management

The control panel manages both configuration and knowledge base operations:

```mermaid
graph LR
    subgraph "Configuration Management"
        ConfigEditor["editor: gr.Code"]
        SaveBtn["save_btn: gr.Button"]
        ReadFunc["read_chain_config()"]
        SaveFunc["save_chain_config()"]
        ConfigFile["config.chain_config_file"]
    end
    
    subgraph "Knowledge Base Management"
        UploadBtn["upload_btn: gr.UploadButton"]
        UploadFunc["upload_btn_callback()"]
        PyPDFLoader["PyPDFLoader"]
        VectorStore["vector_store: Milvus"]
        RefreshFunc["refresh_button_callback()"]
        DeleteFunc["confirm_delete_callback()"]
    end
    
    ConfigEditor --> SaveBtn
    SaveBtn --> SaveFunc
    SaveFunc --> ConfigFile
    ReadFunc --> ConfigEditor
    
    UploadBtn --> UploadFunc
    UploadFunc --> PyPDFLoader
    PyPDFLoader --> VectorStore
    VectorStore --> RefreshFunc
    VectorStore --> DeleteFunc
```

**Sources:** [code/frontend/pages/control/__init__.py:179-341]()

## Key Frontend Components

### Gradio Component Definitions

The interfaces utilize specific Gradio components with custom configuration:

| Component | Usage | Key Properties |
|-----------|-------|----------------|
| `gr.Chatbot` | Chat display | `bubble_full_width=False`, `avatar_images=_AVATAR_IMAGES` |
| `gr.Textbox` | Message input | `container=False`, `elem_id="msg"` |
| `gr.Code` | YAML editor | `language="yaml"`, `interactive=True` |
| `gr.UploadButton` | File upload | `file_types=[".pdf"]`, `file_count="multiple"` |
| `gr.Checkbox` | Feature toggles | `USE_KB_INITIAL`, `USE_RERANKER_INITIAL` |

### State Management Implementation

Both interfaces implement state management for different purposes:

**Chat Frontend:**
- `session_id = gr.State("")` - Maintains conversation session identity
- `use_kb = gr.Checkbox(USE_KB_INITIAL, visible=False)` - Hidden knowledge base toggle
- `use_reranker = gr.Checkbox(USE_RERANKER_INITIAL, visible=False)` - Hidden reranker toggle

**Control Panel:**
- Dynamic mermaid diagram updates based on checkbox states
- Configuration file change tracking with visual indicators
- Document list refresh after upload/delete operations

**Sources:** [code/frontend/pages/chat/__init__.py:46-48](), [code/frontend/pages/control/__init__.py:112-113]()

## JavaScript Integration

The frontend implements custom JavaScript for enhanced interactivity:

### Message Passing Between Interfaces

```javascript
// Control panel sends configuration updates to chat frontend
window.top.postMessage({"use_kb": val}, '*');
window.top.postMessage({"use_reranker": val}, '*');
```

### Configuration Editor Visual Feedback

```javascript
// Indicates unsaved changes with orange indicator
title.innerHTML = title.innerHTML.slice(0,-2) + "🟠";
// Indicates saved changes with green indicator  
title.innerHTML = title.innerHTML.slice(0,-2) + "🟢";
```

**Sources:** [code/frontend/pages/control/__init__.py:50-77]()

## Error Handling Patterns

The frontend implements comprehensive error handling for different failure modes:

### Chain Server Communication Errors

The chat interface distinguishes between connection and server errors:

```python
except (HTTPStatusError, ConnectError) as exc:
    if isinstance(exc, ConnectError) or 400 <= exc.response.status_code < 500:
        chat[-1][1] = "❌ **Uh oh...**\nI can't seem to reach to the chain server..."
    else:
        chat[-1][1] = "❌ **Uh oh...**\nThere was an error inside the chain server..."
```

### Configuration Validation

The control panel validates both YAML syntax and configuration schema:

```python
# validate yaml
config_data = yaml.safe_load(config_txt)
# validate configuration  
_ = ChainConfiguration.model_validate(config_data)
```

**Sources:** [code/frontend/pages/chat/__init__.py:87-102](), [code/frontend/pages/control/__init__.py:222-231]()

---

