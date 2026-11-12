<!-- source: DeepWiki mcp.deepwiki.com · repo joinly-ai/joinly · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [joinly/services/tts/resemble.py](joinly/services/tts/resemble.py)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This page provides an overview of how to get started with joinly, covering system setup, basic usage patterns, and the initial workflow for running your first meeting agent. The guide assumes you want to quickly deploy a meeting agent that can join video calls and interact using AI.

For detailed installation instructions, see [Installation and Dependencies](#2.1). For a step-by-step walkthrough with example commands, see [Quick Start Guide](#2.2). For comprehensive configuration options, see [Configuration and Settings](#2.3).

## System Overview

Joinly consists of two main components that work together to enable AI agents in meetings:

1. **Joinly Server** - A Docker container that manages meeting connections, handles audio processing (speech-to-text and text-to-speech), and exposes an MCP (Model Context Protocol) server interface
2. **Joinly Client** - A Python package that connects to the MCP server, manages LLM interactions, and orchestrates agent behavior

### Component Architecture

The following diagram shows the core components and how they map to code entities:

```mermaid
graph TB
    subgraph "User Entry Points"
        DockerCLI["docker run<br/>ghcr.io/joinly-ai/joinly"]
        UVX["uvx joinly-client"]
        PythonCode["Python: JoinlyClient()"]
    end
    
    subgraph "Joinly Server Container"
        MainCLI["joinly.main:cli<br/>(Click CLI)"]
        SessionContainer["SessionContainer<br/>joinly/session/session_container.py"]
        MeetingSession["MeetingSession<br/>joinly/session/meeting_session.py"]
        
        subgraph "MCP Interface"
            FastMCPServer["FastMCP Server<br/>joinly/mcp/server.py<br/>:8000/mcp/"]
            MCPTools["MCP Tools:<br/>join_meeting<br/>speak_text<br/>get_transcript"]
            MCPResources["MCP Resources:<br/>transcript://live"]
        end
        
        subgraph "Speech Pipeline"
            VADService["VAD Service<br/>joinly/services/vad/"]
            STTService["STT Service<br/>joinly/services/stt/<br/>(whisper, deepgram)"]
            TTSService["TTS Service<br/>joinly/services/tts/<br/>(kokoro, elevenlabs)"]
        end
        
        BrowserProvider["BrowserMeetingProvider<br/>joinly/providers/browser/"]
    end
    
    subgraph "Joinly Client Package"
        JoinlyClient["JoinlyClient<br/>joinly_client/client.py"]
        ConvAgent["ConversationalToolAgent<br/>joinly_client/agent.py"]
        MCPClientSession["FastMCP Client<br/>HTTP/SSE Connection"]
    end
    
    subgraph "External Services"
        MeetingPlatform["Google Meet<br/>Zoom<br/>Teams"]
        LLMProvider["LLM Provider<br/>OpenAI/Anthropic/Google"]
    end
    
    DockerCLI --> MainCLI
    MainCLI --> SessionContainer
    SessionContainer -->|"resolves dependencies"| MeetingSession
    SessionContainer -->|"initializes"| FastMCPServer
    
    MeetingSession --> BrowserProvider
    MeetingSession --> VADService
    MeetingSession --> STTService
    MeetingSession --> TTSService
    
    FastMCPServer --> MCPTools
    FastMCPServer --> MCPResources
    
    BrowserProvider <-->|"playwright automation"| MeetingPlatform
    
    UVX --> JoinlyClient
    PythonCode --> JoinlyClient
    JoinlyClient --> MCPClientSession
    JoinlyClient --> ConvAgent
    
    MCPClientSession <-->|"HTTP :8000"| FastMCPServer
    ConvAgent <--> LLMProvider
    
    STTService -->|"transcripts"| MCPResources
    MCPTools -->|"invoke"| TTSService
```

**Sources:** [joinly/main.py](), [joinly/session/session_container.py](), [joinly/session/meeting_session.py](), [joinly/mcp/server.py](), [joinly_client/client.py](), [joinly_client/agent.py](), [joinly/providers/browser/browser_meeting_provider.py](), [README.md:1-290]()

## Deployment Modes

Joinly supports three primary deployment patterns, each suited for different use cases:

```mermaid
graph LR
    subgraph "Mode 1: All-in-One (--client flag)"
        Docker1["Docker Container"]
        Agent1["Built-in Agent"]
        Session1["MeetingSession"]
        
        Docker1 -->|"--client <URL>"| Agent1
        Agent1 -->|"direct access"| Session1
    end
    
    subgraph "Mode 2: Server + External Client"
        Docker2["Docker Container<br/>-p 8000:8000"]
        MCPServer["FastMCP Server<br/>:8000/mcp/"]
        ExtClient["uvx joinly-client<br/>or custom client"]
        
        Docker2 --> MCPServer
        ExtClient <-->|"HTTP/SSE"| MCPServer
    end
    
    subgraph "Mode 3: Custom Client"
        CustomCode["from joinly_client<br/>import JoinlyClient"]
        CustomAgent["Custom Agent<br/>Implementation"]
        
        CustomCode --> CustomAgent
        CustomAgent <-->|"HTTP/SSE"| MCPServer
    end
    
    style Docker1 fill:#f9f9f9
    style Docker2 fill:#f9f9f9
    style MCPServer fill:#f9f9f9
    style ExtClient fill:#f9f9f9
```

**Sources:** [README.md:53-126](), [joinly/main.py:32-58]()

### Mode Comparison

| Mode | Use Case | Command Pattern | Advantages |
|------|----------|----------------|------------|
| **All-in-One** | Quick testing, simple deployments | `docker run --client <URL>` | Simplest setup, no external dependencies |
| **Server + External Client** | Production use, multi-client scenarios | Server: `docker run -p 8000:8000`<br/>Client: `uvx joinly-client <URL>` | Separation of concerns, supports external MCP servers |
| **Custom Client** | Custom agent logic, specialized workflows | `from joinly_client import JoinlyClient` | Full control over agent behavior |

**Sources:** [README.md:87-138]()

## Basic Getting Started Workflow

The typical workflow for getting started with joinly follows these steps:

```mermaid
sequenceDiagram
    participant User
    participant Docker as "Docker<br/>(joinly image)"
    participant EnvFile as ".env file"
    participant Server as "Joinly Server"
    participant Client as "joinly-client"
    participant Meeting as "Meeting Platform"
    participant LLM as "LLM Provider"
    
    User->>EnvFile: Create .env with API keys
    Note over EnvFile: JOINLY_LLM_PROVIDER=openai<br/>OPENAI_API_KEY=xxx
    
    User->>Docker: docker pull ghcr.io/joinly-ai/joinly:latest
    Docker-->>User: Image ready (~2.3GB)
    
    alt Mode 1: All-in-One
        User->>Docker: docker run --env-file .env<br/>--client <MeetingURL>
        Docker->>Server: Start server components
        Docker->>Client: Start built-in agent
        Client->>Server: Connect locally
    else Mode 2: Server + External Client
        User->>Docker: docker run --env-file .env<br/>-p 8000:8000
        Docker->>Server: Start server, expose :8000
        User->>Client: uvx joinly-client --env-file .env<br/><MeetingURL>
        Client->>Server: Connect via HTTP :8000
    end
    
    Client->>Server: Call join_meeting tool
    Server->>Meeting: Join via browser automation
    Meeting-->>Server: Audio stream
    Server->>Client: transcript://live updates
    Client->>LLM: Process with context
    LLM-->>Client: Response with tool calls
    Client->>Server: Call speak_text tool
    Server->>Meeting: Synthesize & play audio
```

**Sources:** [README.md:52-101](), [joinly/main.py](), [joinly_client/__main__.py]()

## Prerequisites

Before starting, ensure you have:

1. **Docker** - For running the joinly server container
2. **API Keys** - At minimum, an API key for an LLM provider (OpenAI, Anthropic, Google, or Azure)
3. **Optional: uv** - For running external clients (Mode 2 or 3)
4. **Meeting Link** - A valid Google Meet, Zoom, or Microsoft Teams meeting URL

For detailed installation instructions, see [Installation and Dependencies](#2.1).

**Sources:** [README.md:56-57](), [.env.example:1-48]()

## Configuration Overview

Joinly is configured through a combination of:

1. **Environment Variables** - Stored in a `.env` file for API keys and provider settings
2. **Command-Line Arguments** - For runtime options like `--tts`, `--stt`, `--lang`, `--name`
3. **HTTP Headers** - For session-specific settings when using external clients (via `joinly-settings` header)

### Essential Environment Variables

The minimum required configuration is an LLM provider setup. Example for OpenAI:

```env
JOINLY_LLM_PROVIDER=openai
JOINLY_LLM_MODEL=gpt-4o
OPENAI_API_KEY=your-api-key-here
```

**Sources:** [.env.example:1-10](), [README.md:58-73]()

### Speech Service Configuration

By default, joinly uses local models (Whisper for STT, Kokoro for TTS), but supports cloud alternatives:

| Service | Provider Options | Configuration |
|---------|-----------------|---------------|
| **Text-to-Speech (TTS)** | `kokoro` (default), `elevenlabs`, `deepgram`, `resemble` | `--tts <provider>` |
| **Speech-to-Text (STT)** | `whisper` (default), `deepgram` | `--stt <provider>` |
| **Voice Activity Detection (VAD)** | `hybrid` (default), `webrtc`, `silero` | `--vad <provider>` |

Cloud providers require API keys in the `.env` file:

```env
DEEPGRAM_API_KEY=your-key
ELEVENLABS_API_KEY=your-key
RESEMBLE_API_KEY=your-key
```

**Sources:** [README.md:160-184](), [.env.example:37-44](), [joinly/services/tts/](), [joinly/services/stt/]()

For comprehensive configuration details, see [Configuration and Settings](#2.3).

## Docker Image Variants

Joinly provides three Docker image variants optimized for different scenarios:

```mermaid
graph TB
    subgraph "Image Variants"
        Base["Base Image<br/>:latest<br/>~2.3GB"]
        CUDA["CUDA Image<br/>:latest-cuda<br/>~5GB"]
        Lite["Lite Image<br/>:latest-lite<br/>~1.5GB"]
    end
    
    subgraph "Base Contents"
        BaseModels["Whisper: base.en<br/>Kokoro: v0.4.9<br/>Chromium browser"]
        BaseDeps["CPU optimized<br/>onnxruntime"]
    end
    
    subgraph "CUDA Contents"
        CUDAModels["Whisper: distil-large-v3<br/>Kokoro: v0.4.9<br/>Chromium browser"]
        CUDADeps["GPU optimized<br/>onnxruntime-gpu<br/>CUDA 12.6+"]
    end
    
    subgraph "Lite Contents"
        LiteModels["No model weights<br/>Chromium browser"]
        LiteDeps["Cloud services only<br/>minimal dependencies"]
    end
    
    Base --> BaseModels
    Base --> BaseDeps
    CUDA --> CUDAModels
    CUDA --> CUDADeps
    Lite --> LiteModels
    Lite --> LiteDeps
    
    Base -.default.-> Use1["Good balance<br/>CPU inference"]
    CUDA -.requires GPU.-> Use2["Best quality<br/>faster inference"]
    Lite -.smallest.-> Use3["Cloud STT/TTS<br/>minimal size"]
```

**Sources:** [README.md:76-214](), [Dockerfile](), [pyproject.toml:32-35]()

### Choosing an Image

- **Base (`:latest`)** - Default choice for most users. Includes `base.en` Whisper model for reasonable quality on CPU.
- **CUDA (`:latest-cuda`)** - For GPU-accelerated inference. Automatically uses `distil-large-v3` Whisper model for better quality. Requires NVIDIA Container Toolkit and CUDA 12.6+.
- **Lite (`:latest-lite`)** - Minimal image without local model weights. Requires cloud STT/TTS services (Deepgram, ElevenLabs, etc.).

**Sources:** [README.md:200-214](), [CHANGELOG.md:133-134]()

## First Steps After Installation

Once you have Docker and your `.env` file ready:

1. **Pull the image:**
   ```bash
   docker pull ghcr.io/joinly-ai/joinly:latest
   ```

2. **Start a meeting and get the URL** from Google Meet, Zoom, or Teams

3. **Run joinly** using one of the deployment modes:
   - All-in-one: `docker run --env-file .env ghcr.io/joinly-ai/joinly:latest --client <MeetingURL>`
   - Server mode: `docker run --env-file .env -p 8000:8000 ghcr.io/joinly-ai/joinly:latest`

4. **Monitor the logs** for connection status and agent activity

For detailed step-by-step instructions with troubleshooting, see [Quick Start Guide](#2.2).

**Sources:** [README.md:76-85]()

## MCP Server Interface

When running in server mode, joinly exposes a FastMCP server on port 8000 that provides standardized tools and resources for meeting interaction:

### Available Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `join_meeting` | Join a video call | `url`, `participant_name`, `passcode?` |
| `leave_meeting` | Leave the current meeting | None |
| `speak_text` | Speak using TTS | `text` |
| `send_chat_message` | Send a chat message | `message` |
| `mute_yourself` / `unmute_yourself` | Control microphone | None |
| `get_transcript` | Retrieve transcript with filters | `minutes?` |
| `get_chat_history` | Get meeting chat | None |
| `get_participants` | List current participants | None |
| `get_video_snapshot` | Capture screen/video frame | None |

### Available Resources

| Resource URI | Description | Subscribable |
|--------------|-------------|--------------|
| `transcript://live` | Real-time meeting transcript with speaker attribution and timestamps | Yes |
| `usage://current` | Current session usage metrics (LLM tokens, STT/TTS minutes) | No |

**Sources:** [README.md:220-238](), [joinly/mcp/server.py]()

## Next Steps

After completing initial setup:

- **For installation details:** See [Installation and Dependencies](#2.1)
- **For a guided walkthrough:** See [Quick Start Guide](#2.2)
- **For configuration reference:** See [Configuration and Settings](#2.3)
- **For architecture details:** See [Architecture](#3)
- **For building custom agents:** See [Client SDK](#6)
- **For adding external MCP servers:** See [LLM and External Service Integration](#7)

**Sources:** [README.md:1-290]()

---

