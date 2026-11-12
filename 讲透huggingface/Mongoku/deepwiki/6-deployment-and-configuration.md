<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Mongoku · page 6 Deployment and Configuration · fetched 2026-10-26 -->

# Deployment and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [lib/JsonEncoder.ts](lib/JsonEncoder.ts)

</details>



This document provides a comprehensive guide to deploying Mongoku in various environments and configuring it for specific operational requirements. It covers installation methods, runtime configuration options, process management, and security considerations.

For detailed Docker-specific deployment instructions, see [Docker Deployment](#6.1). For complete environment variable reference, see [Environment Configuration](#6.2).

## Overview

Mongoku supports multiple deployment strategies to accommodate different infrastructure requirements, from local development to production containerized environments. The application can be deployed as a global npm package, Docker container, or built manually from source.

## Deployment Methods

### Installation Options

Mongoku provides four primary deployment approaches, each suited for different use cases:

#### Deployment Method Comparison

| Method | Use Case | Complexity | Customization |
|--------|----------|------------|---------------|
| NPM Global | Development, Quick Setup | Low | Limited |
| Docker Hub | Production, Standard Deployment | Low | Medium |
| Custom Docker | Production, Custom Requirements | Medium | High |
| Manual Build | Development, Custom Modifications | High | Full |

#### Deployment Architecture Flow

```mermaid
graph TD
    subgraph "Installation Methods"
        NPMInstall["`npm install -g mongoku`"]
        DockerPull["`docker pull huggingface/mongoku`"]
        CustomBuild["`docker build -t custom/mongoku .`"]
        ManualBuild["`ng build && tsc`"]
    end
    
    subgraph "Process Management"
        DirectExec["`mongoku start`"]
        PM2Daemon["`mongoku start --pm2`"]
        ForeverDaemon["`mongoku start --forever`"]
        DockerRun["`docker run -d mongoku`"]
    end
    
    subgraph "Runtime Components"
        ExpressServer["`dist/server.js`"]
        AngularApp["`app/dist/*`"]
        CLIInterface["`dist/cli.js`"]
    end
    
    subgraph "Configuration Sources"
        EnvVars["`MONGOKU_*`<br/>Environment Variables"]
        ConfigDB["`~/.mongoku.db`<br/>Host Configuration"]
        DefaultHosts["`MONGOKU_DEFAULT_HOST`"]
    end
    
    NPMInstall --> DirectExec
    NPMInstall --> PM2Daemon
    NPMInstall --> ForeverDaemon
    
    DockerPull --> DockerRun
    CustomBuild --> DockerRun
    ManualBuild --> DirectExec
    
    DirectExec --> ExpressServer
    PM2Daemon --> ExpressServer
    ForeverDaemon --> ExpressServer
    DockerRun --> ExpressServer
    
    ExpressServer --> AngularApp
    CLIInterface --> ExpressServer
    
    EnvVars --> ExpressServer
    ConfigDB --> ExpressServer
    DefaultHosts --> ExpressServer
```

Sources: [README.md:13-77](), [Dockerfile:1-29]()

### NPM Global Installation

The simplest deployment method installs Mongoku globally via npm, providing command-line access to start the application:

```bash
npm install -g mongoku
mongoku start
```

This method creates the `mongoku` CLI command available system-wide, which internally executes the compiled server located at `dist/server.js`.

Sources: [README.md:17-23]()

### Docker Deployment

Docker deployment offers containerized execution with pre-configured environment variables and port mappings. The official image `huggingface/mongoku` provides a ready-to-run container:

```bash
docker run -d --name mongoku -p 3100:3100 huggingface/mongoku
```

The Docker build process compiles both frontend and backend components within the container, as defined in the build stages.

Sources: [README.md:34-55](), [Dockerfile:17-23]()

### Manual Build Process

Manual building provides full control over the compilation process, requiring separate frontend and backend build steps:

```bash
# Frontend compilation
cd app
npm install
ng build

# Backend compilation  
cd ..
tsc

# Execution
node dist/server.js
```

Sources: [README.md:57-77]()

## Configuration System

### Configuration Architecture

```mermaid
graph LR
    subgraph "Configuration Sources"
        EnvVarsMONGOKU_DEFAULT_HOST["`MONGOKU_DEFAULT_HOST`"]
        EnvVarsMONGOKU_SERVER_PORT["`MONGOKU_SERVER_PORT`"]
        EnvVarsMONGOKU_DATABASE_FILE["`MONGOKU_DATABASE_FILE`"]
        EnvVarsMONGOKU_COUNT_TIMEOUT["`MONGOKU_COUNT_TIMEOUT`"]
        EnvVarsMONGOKU_READ_ONLY_MODE["`MONGOKU_READ_ONLY_MODE`"]
    end
    
    subgraph "Application Layer"
        ServerJS["`dist/server.js`"]
        HostsManager["`HostsManager`"]
        MongoManager["`MongoManager`"]
    end
    
    subgraph "Runtime Behavior"
        PortBinding["Port 3100<br/>(configurable)"]
        HostConnections["MongoDB Connections"]
        ConfigPersistence["`~/.mongoku.db`<br/>Host Storage"]
        SecurityMode["Read-Only Mode<br/>(optional)"]
    end
    
    EnvVarsMONGOKU_DEFAULT_HOST --> ServerJS
    EnvVarsMONGOKU_SERVER_PORT --> PortBinding
    EnvVarsMONGOKU_DATABASE_FILE --> ConfigPersistence
    EnvVarsMONGOKU_COUNT_TIMEOUT --> MongoManager
    EnvVarsMONGOKU_READ_ONLY_MODE --> SecurityMode
    
    ServerJS --> HostsManager
    ServerJS --> MongoManager
    HostsManager --> ConfigPersistence
    MongoManager --> HostConnections
    ServerJS --> PortBinding
    ServerJS --> SecurityMode
```

Sources: [README.md:79-97](), [Dockerfile:5-10]()

### Core Configuration Parameters

| Variable | Purpose | Default Value | Example |
|----------|---------|---------------|---------|
| `MONGOKU_DEFAULT_HOST` | Default MongoDB connection strings | `mongodb://localhost:27017` | `mongodb://user:pass@host:27017` |
| `MONGOKU_SERVER_PORT` | HTTP server port | `3100` | `8000` |
| `MONGOKU_DATABASE_FILE` | Host configuration storage location | `$HOME/.mongoku.db` | `/tmp/mongoku.db` |
| `MONGOKU_COUNT_TIMEOUT` | Document count timeout (ms) | `5000` | `1000` |
| `MONGOKU_READ_ONLY_MODE` | Enable read-only operations | `false` | `true` |

Sources: [README.md:82-96]()

## Process Management

### Process Management Options

Mongoku supports multiple process management strategies for production deployment:

#### Direct Execution
```bash
mongoku start
```
Runs the application in the foreground, suitable for development or supervised containers.

#### PM2 Daemon
```bash
mongoku start --pm2
```
Launches Mongoku as a PM2-managed daemon with automatic restart capabilities and process monitoring.

#### Forever Daemon  
```bash
mongoku start --forever
```
Executes Mongoku using Forever process manager for continuous operation and automatic restart on failure.

Sources: [README.md:25-32]()

### Docker Container Management

Docker containers provide isolated execution environments with standardized configuration. The container exposes port 3100 by default and includes all necessary runtime dependencies.

The Dockerfile defines default environment variables that can be overridden at container runtime:

```bash
docker run -d --name mongoku -p 3100:3100 \
  --env MONGOKU_DEFAULT_HOST="mongodb://user:password@myhost.com:8888" \
  huggingface/mongoku
```

Sources: [README.md:38-43](), [Dockerfile:25-29]()

## Security Considerations

### Read-Only Mode

The `MONGOKU_READ_ONLY_MODE` environment variable enables security-restricted operation, preventing data modification operations while preserving query and browse functionality. This mode is particularly useful for production monitoring scenarios where data integrity must be maintained.

### Host Configuration Persistence

MongoDB host configurations are stored in the file specified by `MONGOKU_DATABASE_FILE`. This file contains connection details and should be secured appropriately in production environments. The default location `~/.mongoku.db` provides user-specific configuration storage.

Sources: [README.md:95-96](), [README.md:89-90]()

## System Requirements

### Runtime Dependencies

The application requires Node.js 18+ runtime environment, as specified in the Docker base image. Development builds additionally require TypeScript compiler and Angular CLI for source compilation.

### Build Dependencies

Manual builds require the following global packages:
- `typescript@4.5.4` 
- `@angular/cli`

These dependencies are automatically installed in Docker builds but must be manually installed for local development environments.

Sources: [Dockerfile:1](), [Dockerfile:17](), [README.md:62-63]()

---

