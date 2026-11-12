<!-- source: DeepWiki mcp.deepwiki.com · repo joinly-ai/joinly · page 4 Core Server (joinly) · fetched 2026-10-27 -->

# joinly (Core Application)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [common/joinly_common/types.py](common/joinly_common/types.py)
- [joinly/main.py](joinly/main.py)
- [joinly/server.py](joinly/server.py)
- [joinly/utils/usage.py](joinly/utils/usage.py)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



The joinly core application is the main server component that provides MCP (Model Context Protocol) services for AI agents to join and interact with video meetings. This application can operate in two modes: as a standalone MCP server exposing meeting tools and resources, or as a client that directly joins meetings using integrated AI capabilities.

For information about the client SDK for building AI agents, see [joinly-client (Python SDK)](#4.2). For shared utilities and data structures, see [joinly-common (Shared Library)](#4.3).

## Application Architecture

The core application is built around a FastMCP server that provides tools and resources for meeting interaction, with a CLI interface that supports both server and client operational modes.

```mermaid
graph TB
    subgraph "CLI Layer"
        cli["cli() function<br/>main.py"]
        click_options["Click Options<br/>--server/--client, --name, etc."]
    end
    
    subgraph "Core Server"
        mcp_server["mcp: FastMCP<br/>server.py:122"]
        session_lifespan["session_lifespan()<br/>server.py:72"]
        session_context["SessionContext<br/>server.py:33"]
    end
    
    subgraph "MCP Resources"
        transcript_resource["get_transcript()<br/>transcript://live"]
        segments_resource["get_transcript_segments()<br/>transcript://live/segments"]
        usage_resource["get_usage_report()<br/>usage://current"]
    end
    
    subgraph "MCP Tools"
        join_tool["join_meeting()<br/>server.py:161"]
        speak_tool["speak_text()<br/>server.py:197"]
        chat_tool["send_chat_message()<br/>server.py:218"]
        participants_tool["get_participants()<br/>server.py:280"]
    end
    
    subgraph "Context Management"
        settings_ctx["Settings ContextVar<br/>settings.py:48"]
        usage_ctx["Usage ContextVar<br/>utils/usage.py:9"]
        settings_extractor["_extract_settings()<br/>server.py:39"]
    end
    
    cli --> mcp_server
    click_options --> cli
    
    mcp_server --> session_lifespan
    session_lifespan --> session_context
    session_lifespan --> settings_ctx
    session_lifespan --> usage_ctx
    
    session_context --> transcript_resource
    session_context --> segments_resource
    session_context --> usage_resource
    
    session_context --> join_tool
    session_context --> speak_tool
    session_context --> chat_tool
    session_context --> participants_tool
    
    settings_extractor --> settings_ctx
```

Sources: [joinly/main.py:257-311](), [joinly/server.py:122](), [joinly/server.py:32-37](), [joinly/server.py:71-120]()

## CLI Interface and Application Modes

The application supports two primary operational modes controlled by the CLI interface in `main.py`.

```mermaid
graph LR
    subgraph "CLI Entry Point"
        main_cli["cli() function<br/>main.py:257"]
        click_decorator["@click.command()<br/>main.py:35"]
    end
    
    subgraph "Mode Selection Logic"
        mode_logic["Mode Logic<br/>main.py:290"]
        server_check["server is True OR<br/>(server is None AND meeting_url is None)"]
        client_check["else (client mode)"]
    end
    
    subgraph "Server Mode"
        mcp_run["mcp.run()<br/>main.py:291"]
        transport["transport='streamable-http'"]
        host_port["host, port"]
    end
    
    subgraph "Client Mode"
        joinly_client_import["import joinly_client<br/>main.py:293"]
        client_run["joinly_client.run()<br/>main.py:302"]
        meeting_url_required["meeting_url required<br/>main.py:295-300"]
    end
    
    main_cli --> mode_logic
    click_decorator --> main_cli
    
    mode_logic --> server_check
    mode_logic --> client_check
    
    server_check --> mcp_run
    mcp_run --> transport
    mcp_run --> host_port
    
    client_check --> joinly_client_import
    client_check --> client_run
    client_check --> meeting_url_required
```

Sources: [joinly/main.py:257-311](), [joinly/main.py:290-310]()

### Server Mode

When running in server mode, the application starts a FastMCP server that exposes meeting control tools and resources over HTTP. This mode is activated when:
- `--server` flag is explicitly set, or  
- No meeting URL is provided (default behavior)

The server binds to the specified host and port (defaults: `127.0.0.1:8000`) and provides MCP endpoints for client connections.

### Client Mode  

In client mode, the application directly joins a meeting using the integrated `joinly_client` package. This mode requires:
- A meeting URL as a command line argument
- LLM provider and model configuration
- Optional name trigger functionality

## MCP Server Implementation

The FastMCP server provides a comprehensive set of tools and resources for meeting interaction, implemented in [joinly/server.py]().

### Core Tools

| Tool | Function | Description |
|------|----------|-------------|
| `join_meeting` | [server.py:161-181]() | Join a meeting with URL, name, and optional passcode |
| `leave_meeting` | [server.py:188-194]() | Leave the current meeting |
| `speak_text` | [server.py:197-212]() | Speak text using TTS in the meeting |
| `send_chat_message` | [server.py:218-225]() | Send chat messages to meeting participants |
| `get_chat_history` | [server.py:228-237]() | Retrieve meeting chat history |
| `get_transcript` | [server.py:241-273]() | Get transcript with filtering options |
| `get_participants` | [server.py:277-285]() | List current meeting participants |
| `mute_yourself` | [server.py:289-298]() | Mute microphone |
| `unmute_yourself` | [server.py:301-311]() | Unmute microphone |

### MCP Resources

| Resource | URL | Function | Description |
|----------|-----|----------|-------------|
| Live Transcript | `transcript://live` | [server.py:130-133]() | Participant utterances only |
| Transcript Segments | `transcript://live/segments` | [server.py:141-144]() | All transcript segments |
| Usage Statistics | `usage://current` | [server.py:152-154]() | Service usage metrics |

Sources: [joinly/server.py:125-155](), [joinly/server.py:157-311]()

## Session Management

The application implements sophisticated session management using FastMCP's lifespan context system to ensure proper resource allocation and cleanup.

```mermaid
graph TB
    subgraph "Session Lifecycle"
        lifespan_start["session_lifespan() entry<br/>server.py:72"]
        settings_setup["Settings extraction & setup<br/>server.py:75-76"]
        usage_setup["Usage tracking setup<br/>server.py:77-78"]
        container_create["SessionContainer creation<br/>server.py:79-80"]
    end
    
    subgraph "Resource Subscriptions"
        subscribe_handler["_handle_subscribe_resource<br/>server.py:84-97"]
        unsubscribe_handler["_handle_unsubscribe_resource<br/>server.py:99-104"]
        event_remover["_remover dict<br/>server.py:82"]
    end
    
    subgraph "Cleanup Process"
        lifespan_finally["finally block<br/>server.py:108"]
        remover_cleanup["Remove event handlers<br/>server.py:109-110"]
        container_exit["session_container.__aexit__<br/>server.py:116"]
        context_reset["reset_settings & reset_usage<br/>server.py:118-119"]
    end
    
    lifespan_start --> settings_setup
    settings_setup --> usage_setup
    usage_setup --> container_create
    
    container_create --> subscribe_handler
    subscribe_handler --> event_remover
    event_remover --> unsubscribe_handler
    
    lifespan_finally --> remover_cleanup
    remover_cleanup --> container_exit
    container_exit --> context_reset
```

Sources: [joinly/server.py:71-120](), [joinly/server.py:84-104](), [joinly/server.py:108-119]()

## Settings Management

The application uses a context-based settings system that supports dynamic configuration through HTTP headers and environment variables.

```mermaid
graph LR
    subgraph "Settings Context"
        settings_class["Settings class<br/>settings.py:17"]
        context_var["_current_settings<br/>ContextVar<br/>settings.py:48"]
        get_settings["get_settings()<br/>settings.py:51"]
        set_settings["set_settings()<br/>settings.py:60"]
    end
    
    subgraph "Dynamic Settings"
        extract_func["_extract_settings()<br/>server.py:39"]
        http_header["joinly-settings header<br/>server.py:46"]
        json_parsing["JSON validation<br/>server.py:54-67"]
        model_merge["Settings merging<br/>server.py:55-61"]
    end
    
    subgraph "Configuration Sources"
        env_vars["Environment Variables<br/>JOINLY_* prefix"]
        cli_args["CLI Arguments<br/>main.py options"]
        http_override["HTTP Header Override<br/>per-request"]
    end
    
    settings_class --> context_var
    context_var --> get_settings
    context_var --> set_settings
    
    extract_func --> http_header
    http_header --> json_parsing
    json_parsing --> model_merge
    
    env_vars --> settings_class
    cli_args --> settings_class
    http_override --> extract_func
```

The `Settings` class in [joinly/settings.py:17-46]() defines configuration for:
- Meeting provider and AI service selections (`meeting_provider`, `vad`, `stt`, `tts`)
- Service-specific arguments (`meeting_provider_args`, `vad_args`, etc.)
- Basic parameters (`name`, `language`, `device`)

Sources: [joinly/settings.py:17-78](), [joinly/server.py:39-68]()

## Usage Tracking System

The application implements comprehensive usage tracking for AI services and meeting operations using a context-based system.

```mermaid
graph TB
    subgraph "Usage Context"
        usage_contextvar["_current_usage<br/>ContextVar<Usage><br/>utils/usage.py:9"]
        get_usage_func["get_usage()<br/>utils/usage.py:12"]
        set_usage_func["set_usage()<br/>utils/usage.py:21"]
        add_usage_func["add_usage()<br/>utils/usage.py:42"]
    end
    
    subgraph "Usage Data Types"
        usage_class["Usage class<br/>common/types.py:189"]
        service_usage["ServiceUsage class<br/>common/types.py:162"]
        usage_dict["usage: dict[str, int|float]<br/>common/types.py:165"]
        meta_dict["meta: dict[str, str|int|float]<br/>common/types.py:166"]
    end
    
    subgraph "MCP Integration"
        usage_resource["usage://current resource<br/>server.py:147"]
        usage_endpoint["get_usage_report()<br/>server.py:152"]
        session_usage["Session-scoped usage<br/>server.py:77-78"]
    end
    
    usage_contextvar --> get_usage_func
    usage_contextvar --> set_usage_func
    get_usage_func --> add_usage_func
    
    usage_class --> service_usage
    service_usage --> usage_dict
    service_usage --> meta_dict
    
    session_usage --> usage_resource
    usage_resource --> usage_endpoint
    usage_endpoint --> get_usage_func
```

Sources: [joinly/utils/usage.py:1-56](), [common/joinly_common/types.py:162-236](), [joinly/server.py:147-154]()

## Health Check and HTTP Endpoints

The application provides additional HTTP endpoints beyond the MCP protocol:

- **Health Check**: `GET /health` [server.py:314-317]() returns JSON status
- **MCP Endpoints**: Automatically provided by FastMCP at `/mcp/` paths

The server uses "streamable-http" transport, enabling both standard HTTP requests and WebSocket connections for MCP communication.

Sources: [joinly/server.py:314-321](), [joinly/main.py:291]()

---

