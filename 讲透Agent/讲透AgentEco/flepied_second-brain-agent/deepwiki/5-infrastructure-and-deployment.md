<!-- source: DeepWiki mcp.deepwiki.com · repo flepied/second-brain-agent · page 5 Infrastructure and Deployment · fetched 2026-10-27 -->

# Infrastructure and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [compose.yaml](compose.yaml)
- [install-systemd-services.sh](install-systemd-services.sh)
- [sba-md-service.sh](sba-md-service.sh)

</details>



This document covers the operational deployment aspects of the Second Brain Agent system, including vector database setup, system service configuration, and environment management. It focuses on the production deployment architecture and automated service management.

For development environment setup and dependencies, see [Development Environment](#6). For details on the data processing pipeline components, see [Data Processing Pipeline](#2).

## Deployment Architecture

The Second Brain Agent system follows a service-oriented deployment model with containerized storage and systemd-managed processing services. The deployment consists of three primary operational layers:

```mermaid
graph TB
    subgraph "Infrastructure Layer"
        ENV[".env Configuration"]
        COMPOSE["compose.yaml<br/>ChromaDB Container"]
        SYSTEMD["systemd User Services"]
    end
    
    subgraph "Processing Services"
        SBA_MD["sba-md.service<br/>Markdown Processing"]
        SBA_TXT["sba-txt.service<br/>Text Vectorization"]
        MD_SCRIPT["sba-md-service.sh"]
        TXT_SCRIPT["sba-txt-service.sh"]
    end
    
    subgraph "Storage Services"
        CHROMADB["chroma-server:8000<br/>Vector Database"]
        FILESYSTEM["DSTDIR File Structure<br/>/Db, /Text, /Chunk, /Orig"]
    end
    
    subgraph "Runtime Dependencies"
        SRCDIR["SRCDIR<br/>Source Documents"]
        DSTDIR["DSTDIR<br/>Processed Data"]
        APIS["External APIs<br/>OpenAI, HuggingFace, AssemblyAI"]
    end
    
    ENV --> SBA_MD
    ENV --> SBA_TXT  
    ENV --> COMPOSE
    
    SYSTEMD --> SBA_MD
    SYSTEMD --> SBA_TXT
    SBA_MD --> MD_SCRIPT
    SBA_TXT --> TXT_SCRIPT
    
    COMPOSE --> CHROMADB
    CHROMADB --> FILESYSTEM
    
    MD_SCRIPT --> SRCDIR
    MD_SCRIPT --> DSTDIR
    TXT_SCRIPT --> DSTDIR
    TXT_SCRIPT --> APIS
```

Sources: [compose.yaml:1-22](), [example.env:1-7](), [install-systemd-services.sh:1-49]()

## Vector Database Setup

The system uses ChromaDB as its vector database, deployed via Docker Compose for isolation and persistence management. The database configuration emphasizes data persistence and development flexibility.

### ChromaDB Container Configuration

```mermaid
graph LR
    subgraph "Host System"
        DSTDIR_DB["$DSTDIR/Db<br/>Host Volume"]
        COMPOSE_FILE["compose.yaml"]
        ENV_FILE[".env"]
    end
    
    subgraph "Docker Container"
        CHROMA_IMAGE["ghcr.io/chroma-core/chroma:1.0.20"]
        CHROMA_DATA["/data<br/>Container Volume"]
        CHROMA_PORT["8000:8000<br/>HTTP API"]
    end
    
    subgraph "Container Environment"
        IS_PERSISTENT["IS_PERSISTENT=TRUE"]
        ALLOW_RESET["ALLOW_RESET=TRUE"]
    end
    
    ENV_FILE --> COMPOSE_FILE
    COMPOSE_FILE --> CHROMA_IMAGE
    DSTDIR_DB --> CHROMA_DATA
    CHROMA_IMAGE --> CHROMA_PORT
    CHROMA_IMAGE --> IS_PERSISTENT
    CHROMA_IMAGE --> ALLOW_RESET
```

The ChromaDB service mounts the `$DSTDIR/Db` directory to `/data` inside the container with SELinux-compatible `z` flag for persistent storage. The service exposes the HTTP API on port 8000 for client connections.

### Database Deployment Commands

| Operation | Command |
|-----------|---------|
| Start ChromaDB | `docker-compose up -d` |
| View logs | `docker-compose logs -f server` |
| Stop database | `docker-compose down` |
| Reset data | `docker-compose down -v` |

Sources: [compose.yaml:8-20]()

## System Services Configuration

The system uses systemd user services to manage the continuous data processing pipeline. Two primary services handle different stages of the document processing workflow.

### Service Architecture

```mermaid
stateDiagram-v2
    [*] --> install_systemd_services.sh
    
    install_systemd_services.sh --> sba_md_service: "Creates & enables"
    install_systemd_services.sh --> sba_txt_service: "Creates & enables"
    
    state sba_md_service {
        [*] --> sba_md_service.sh
        sba_md_service.sh --> monitor_transform_md: "Executes"
        monitor_transform_md --> [*]
    }
    
    state sba_txt_service {
        [*] --> sba_txt_service.sh  
        sba_txt_service.sh --> monitor_transform_txt: "Executes"
        monitor_transform_txt --> [*]
    }
    
    sba_md_service --> SRCDIR: "Monitors"
    sba_txt_service --> DSTDIR: "Processes"
```

### Service Installation Process

The [install-systemd-services.sh:1-49]() script automatically creates and enables both services:

| Service | Purpose | Script |
|---------|---------|--------|
| `sba-md.service` | Transform documents to text | [sba-md-service.sh:1-19]() |
| `sba-txt.service` | Generate vectors and chunks | `sba-txt-service.sh` |

Each service runs as a simple systemd unit with `RemainAfterExit=yes` to maintain continuous monitoring. The services depend on network availability and start after the `network.target`.

### Service Management Commands

| Operation | Command |
|-----------|---------|
| Install services | `./install-systemd-services.sh` |
| Check status | `systemctl --user status sba-md.service` |
| View logs | `journalctl --user -u sba-md.service -f` |
| Restart service | `systemctl --user restart sba-md.service` |
| Stop services | `systemctl --user stop sba-md.service sba-txt.service` |

Sources: [install-systemd-services.sh:7-26](), [install-systemd-services.sh:28-47](), [sba-md-service.sh:1-19]()

## Configuration Management

The system uses environment-based configuration with a centralized `.env` file pattern. All services and components read configuration from environment variables loaded from the `.env` file.

### Environment Variable Architecture

```mermaid
graph TD
    subgraph "Configuration Sources"
        EXAMPLE_ENV["example.env<br/>Template"]
        USER_ENV[".env<br/>User Configuration"]
    end
    
    subgraph "Path Configuration"
        SRCDIR["SRCDIR<br/>Source Documents"]
        DSTDIR["DSTDIR<br/>Processing Output"]
        SBA_ORG_DOC["SBA_ORG_DOC<br/>Organization Document"]
    end
    
    subgraph "API Configuration"
        OPENAI_API_KEY["OPENAI_API_KEY<br/>OpenAI Access"]
        HUGGINGFACEHUB_API_TOKEN["HUGGINGFACEHUB_API_TOKEN<br/>HuggingFace Access"] 
        ASSEMBLYAI_API_KEY["ASSEMBLYAI_API_KEY<br/>Audio Transcription"]
    end
    
    subgraph "Service Consumers"
        SBA_MD_SVC["sba-md-service.sh"]
        SBA_TXT_SVC["sba-txt-service.sh"]
        DOCKER_COMPOSE["compose.yaml"]
        AGENT_SYSTEM["Agent & Web UI"]
    end
    
    EXAMPLE_ENV -.->|"Template"| USER_ENV
    USER_ENV --> SRCDIR
    USER_ENV --> DSTDIR
    USER_ENV --> SBA_ORG_DOC
    USER_ENV --> OPENAI_API_KEY
    USER_ENV --> HUGGINGFACEHUB_API_TOKEN
    USER_ENV --> ASSEMBLYAI_API_KEY
    
    SRCDIR --> SBA_MD_SVC
    DSTDIR --> SBA_MD_SVC
    DSTDIR --> SBA_TXT_SVC
    DSTDIR --> DOCKER_COMPOSE
    
    OPENAI_API_KEY --> AGENT_SYSTEM
    HUGGINGFACEHUB_API_TOKEN --> AGENT_SYSTEM
    ASSEMBLYAI_API_KEY --> AGENT_SYSTEM
    SBA_ORG_DOC --> AGENT_SYSTEM
```

### Required Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SRCDIR` | Source document directory | `/home/user/documents` |
| `DSTDIR` | Processing output directory | `/home/user/second-brain-data` |
| `OPENAI_API_KEY` | OpenAI API access token | `sk-...` |
| `HUGGINGFACEHUB_API_TOKEN` | HuggingFace Hub token | `hf_...` |
| `ASSEMBLYAI_API_KEY` | AssemblyAI transcription token | `...` |
| `SBA_ORG_DOC` | Organization document filename | `SecondBrainOrganization.md` |

### Directory Structure Creation

The [sba-md-service.sh:14-14]() script automatically creates the required directory structure within `$DSTDIR`:

```
$DSTDIR/
├── Orig/          # Original document backups
├── Text/          # Extracted text files  
├── Markdown/      # Processed markdown
├── Chunk/         # Text chunks (created by txt service)
└── Db/            # ChromaDB data (mounted in container)
```

Sources: [example.env:1-7](), [sba-md-service.sh:7-16](), [compose.yaml:12-12]()

## Deployment Verification

The system includes verification mechanisms to ensure proper deployment and service health.

### Service Health Checks

```mermaid
sequenceDiagram
    participant Admin as "Administrator"  
    participant Install as "install-systemd-services.sh"
    participant Systemctl as "systemctl"
    participant Services as "SBA Services"
    
    Admin->>Install: "./install-systemd-services.sh"
    Install->>Systemctl: "systemctl --user status sba-md.service"
    Systemctl-->>Install: "Service status check"
    
    alt Service not exists
        Install->>Install: "Create service file"
        Install->>Systemctl: "systemctl --user enable service"
        Install->>Systemctl: "systemctl --user start service"
        Install->>Systemctl: "systemctl --user status service"
        Systemctl->>Services: "Verify running"
    end
    
    Install->>Admin: "Service installation complete"
```

The installation script performs status checks before creating services, ensuring idempotent deployment. Each service creation includes immediate status verification to confirm successful startup.

Sources: [install-systemd-services.sh:7-7](), [install-systemd-services.sh:23-25](), [install-systemd-services.sh:44-46]()

---

