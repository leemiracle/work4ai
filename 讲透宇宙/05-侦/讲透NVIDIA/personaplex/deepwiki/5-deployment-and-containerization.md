<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/personaplex · page 5 Deployment and Containerization · fetched 2026-10-26 -->

# Deployment and Containerization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [client/Dockerfile](client/Dockerfile)

</details>



## Purpose and Scope

PersonaPlex uses a Docker-based deployment architecture with separate containers for the server (`moshi.server` Python module) and client (React/Vite application). This separation enables independent scaling, isolated runtime environments, and distinct resource allocation for model inference versus UI delivery.

### Container Overview

| Container | Base Image | Primary Executable | Exposed Port | Purpose |
|-----------|-----------|-------------------|--------------|---------|
| Server | `nvcr.io/nvidia/cuda:12.4.1-runtime-ubuntu22.04` | `/app/moshi/.venv/bin/python -m moshi.server` | 8998 | GPU-accelerated model inference |
| Client | `node:20` | `npm run dev` (Vite dev server) | 5173 | Web UI serving and build system |

For detailed implementation:
- Server container CUDA configuration, build process, and package management: [Server Container](#5.1)
- Client container build pipeline, SSL generation, and Node.js environment: [Client Container](#5.2)
- Production considerations, security hardening, and scaling: [Production Deployment](#5.3)

For non-containerized deployment options, see [Server Deployment](#3.1) and [Client Setup and Configuration](#4.1).

**Sources:** [Dockerfile:1-26](), [client/Dockerfile:1-22]()

---

## Container Architecture

PersonaPlex employs a two-container architecture that separates concerns between model inference and user interface delivery. This design allows independent scaling, updates, and resource allocation for each component.

### Container Comparison

| Aspect | Server Container | Client Container |
|--------|------------------|------------------|
| **Base Image** | `nvcr.io/nvidia/cuda:12.4.1-runtime-ubuntu22.04` | `node:20` |
| **Language Runtime** | Python 3.12 | Node.js 20 |
| **Package Manager** | UV (astral-sh/uv) | npm |
| **Exposed Port** | 8998 | 5173 |
| **SSL Generation** | External (mounted volume) | Internal (OpenSSL self-signed) |
| **GPU Support** | Yes (CUDA 12.4.1) | No |
| **Primary Purpose** | Model inference, audio streaming | UI serving, build system |

**Sources:** Dockerfile, client/Dockerfile

## Container Build and Runtime Architecture

### Build Dependency Flow

```mermaid
graph TB
    subgraph ExtRes["External Resources"]
        CUDARegistry["nvcr.io/nvidia/cuda:12.4.1-runtime-ubuntu22.04"]
        UVRegistry["ghcr.io/astral-sh/uv:latest"]
        NodeRegistry["node:20"]
        HuggingFace["HuggingFace Model Hub<br/>nvidia/personaplex-7b-v1"]
    end
    
    subgraph ServerBuild["Server Container Build (Dockerfile)"]
        S1["FROM ${BASE_IMAGE}:${BASE_IMAGE_TAG}"]
        S2["COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/"]
        S3["apt-get install libopus-dev"]
        S4["COPY moshi/ /app/moshi/"]
        S5["uv venv /app/moshi/.venv --python 3.12"]
        S6["uv sync"]
        S7["mkdir -p /app/ssl"]
        
        CUDARegistry --> S1
        UVRegistry --> S2
        S1 --> S2
        S2 --> S3
        S3 --> S4
        S4 --> S5
        S5 --> S6
        S6 --> S7
    end
    
    subgraph ClientBuild["Client Container Build (client/Dockerfile)"]
        C1["FROM node:20"]
        C2["COPY . /app"]
        C3["npm install"]
        C4["npm run build"]
        C5["apt-get install openssl"]
        C6["openssl req -x509 -keyout /app/key.pem -out /app/cert.pem"]
        
        NodeRegistry --> C1
        C1 --> C2
        C2 --> C3
        C3 --> C4
        C4 --> C5
        C5 --> C6
    end
    
    subgraph Runtime["Runtime Execution"]
        ServerCmd["/app/moshi/.venv/bin/python -m moshi.server --ssl /app/ssl<br/>Port: 8998"]
        ClientCmd["npm run dev<br/>Port: 5173"]
        SSLVolume["/app/ssl<br/>volume mount"]
        
        S7 --> ServerCmd
        C6 --> ClientCmd
        SSLVolume -.->|"optional"| ServerCmd
        HuggingFace -.->|"model download"| ServerCmd
    end
    
    ClientCmd -->|"HTTPS"| Browser["User Browser"]
    Browser -->|"WSS/HTTPS"| ServerCmd
```

**Sources:** [Dockerfile:1-26](), [client/Dockerfile:1-22]()

### File Structure Mapping

```mermaid
graph LR
    subgraph HostFS["Host Filesystem"]
        RootDir["/"]
        MoshiDir["moshi/"]
        ClientDir["client/"]
        DockerfileServer["Dockerfile"]
        DockerfileClient["client/Dockerfile"]
    end
    
    subgraph ServerContainer["Server Container: /app/"]
        ServerMoshi["/app/moshi/"]
        ServerVenv["/app/moshi/.venv/"]
        ServerSSL["/app/ssl/"]
        ServerPython["/app/moshi/.venv/bin/python"]
    end
    
    subgraph ClientContainer["Client Container: /app/"]
        ClientApp["/app/"]
        ClientCert["/app/cert.pem"]
        ClientKey["/app/key.pem"]
        ClientDist["/app/dist/"]
        ClientNodeModules["/app/node_modules/"]
    end
    
    MoshiDir -->|"COPY moshi/ (Dockerfile:16)"| ServerMoshi
    ServerMoshi -->|"uv venv (Dockerfile:17)"| ServerVenv
    ServerVenv -->|"uv sync (Dockerfile:18)"| ServerPython
    
    ClientDir -->|"COPY . (client/Dockerfile:5)"| ClientApp
    ClientApp -->|"npm install (client/Dockerfile:7)"| ClientNodeModules
    ClientApp -->|"npm run build (client/Dockerfile:9)"| ClientDist
    ClientApp -->|"openssl req (client/Dockerfile:15-17)"| ClientCert
    ClientApp -->|"openssl req (client/Dockerfile:15-17)"| ClientKey
```

**Sources:** [Dockerfile:14-18](), [client/Dockerfile:4-17]()

---

## Build Context and Ignored Files

Build context exclusions reduce image size and build time by preventing unnecessary files from being copied into containers.

### Server Build Context

The `.dockerignore` file specifies:
```
.cache
```

This excludes Python cache directories. The server Dockerfile copies only `moshi/` [Dockerfile:16](), containing the `moshi.server` module and its dependencies defined in `pyproject.toml`.

### Client Build Context

No dedicated `.dockerignore` exists for the client. The `COPY . /app` directive [client/Dockerfile:5]() includes all files from the `client/` directory. The Vite build process [client/Dockerfile:9]() transpiles TypeScript and bundles assets into `dist/`, excluding source files and development dependencies from the runtime bundle.

**Sources:** [Dockerfile:16](), [client/Dockerfile:5-9]()

---

## Build and Execution Flow

### Server Container Execution Sequence

```mermaid
sequenceDiagram
    participant Host as "Host Docker"
    participant Registry as "Container Registries"
    participant Build as "Build Context"
    participant UV as "UV Package Manager"
    participant Runtime as "Container Runtime"
    
    Note over Host,Runtime: Build Phase
    Host->>Registry: "Pull nvcr.io/nvidia/cuda:12.4.1-runtime-ubuntu22.04"
    Registry-->>Host: "CUDA base image"
    Host->>Registry: "Pull ghcr.io/astral-sh/uv:latest"
    Registry-->>Host: "UV binary"
    Host->>Build: "COPY --from=ghcr.io/astral-sh/uv /uv /uvx /bin/"
    Host->>Build: "apt-get install libopus-dev (Dockerfile:8-12)"
    Host->>Build: "COPY moshi/ /app/moshi/ (Dockerfile:16)"
    Build->>UV: "uv venv /app/moshi/.venv --python 3.12 (Dockerfile:17)"
    UV-->>Build: "Virtual environment created"
    Build->>UV: "uv sync (Dockerfile:18)"
    Note over UV: "Installs from pyproject.toml"
    UV-->>Build: "Dependencies installed"
    Build->>Build: "mkdir -p /app/ssl (Dockerfile:20)"
    
    Note over Host,Runtime: Runtime Phase
    Host->>Runtime: "docker run --gpus all -v ssl:/app/ssl"
    Runtime->>Runtime: "CMD /app/moshi/.venv/bin/python -m moshi.server --ssl /app/ssl"
    Note over Runtime: "EXPOSE 8998 (Dockerfile:22)"
```

**Sources:** [Dockerfile:1-26]()

### Client Container Execution Sequence

```mermaid
sequenceDiagram
    participant Host as "Host Docker"
    participant Registry as "node:20 Registry"
    participant NPM as "npm"
    participant Vite as "Vite Build"
    participant OpenSSL as "openssl"
    participant Runtime as "Container Runtime"
    
    Note over Host,Runtime: Build Phase
    Host->>Registry: "Pull node:20 (client/Dockerfile:1)"
    Registry-->>Host: "Node.js image"
    Host->>NPM: "WORKDIR /app (client/Dockerfile:3)"
    Host->>NPM: "COPY . /app (client/Dockerfile:5)"
    NPM->>NPM: "npm install (client/Dockerfile:7)"
    Note over NPM: "Installs from package.json"
    NPM-->>Host: "node_modules/ created"
    Host->>Vite: "npm run build (client/Dockerfile:9)"
    Vite-->>Host: "dist/ bundle created"
    Host->>OpenSSL: "apt-get install openssl (client/Dockerfile:12)"
    Host->>OpenSSL: "openssl req -x509 -keyout /app/key.pem -out /app/cert.pem"
    OpenSSL-->>Host: "Self-signed certificates"
    
    Note over Host,Runtime: Runtime Phase
    Host->>Runtime: "docker run -p 5173:5173"
    Runtime->>Runtime: "CMD npm run dev (client/Dockerfile:21)"
    Note over Runtime: "Vite dev server with HTTPS, EXPOSE 5173 (client/Dockerfile:19)"
```

**Sources:** [client/Dockerfile:1-22]()

---

## Runtime Configuration

### Command Specifications

| Container | Entry Point | Command | Port | Key Arguments |
|-----------|-------------|---------|------|---------------|
| Server | `ENTRYPOINT []` [Dockerfile:24]() | `/app/moshi/.venv/bin/python -m moshi.server --ssl /app/ssl` [Dockerfile:25]() | 8998 [Dockerfile:22]() | `--ssl` specifies SSL certificate directory |
| Client | Default (from `node:20`) | `npm run dev` [client/Dockerfile:21]() | 5173 [client/Dockerfile:19]() | Vite dev server with HMR |

### Server Runtime Behavior

The `ENTRYPOINT []` [Dockerfile:24]() clears the default entry point, allowing the `CMD` to execute directly. The command invokes `moshi.server` module with `--ssl /app/ssl`, expecting mounted certificates (`cert.pem`, `key.pem`). Without these certificates, the server will fail to start.

### Client Runtime Behavior

The `npm run dev` command [client/Dockerfile:21]() executes the Vite development server defined in `package.json`. This serves the React application with hot module replacement, using the self-signed certificates generated during build [client/Dockerfile:15-17]().

**Sources:** [Dockerfile:22-25](), [client/Dockerfile:19-21]()

---

## Network and SSL Configuration

### Port Mapping

| Container | Internal Port | Protocol | Service | SSL Source |
|-----------|--------------|----------|---------|------------|
| Server | 8998 [Dockerfile:22]() | HTTPS/WSS | `moshi.server` inference and streaming | External mount to `/app/ssl/` [Dockerfile:25]() |
| Client | 5173 [client/Dockerfile:19]() | HTTPS | Vite dev server | Build-time generated `/app/cert.pem`, `/app/key.pem` [client/Dockerfile:15-17]() |

### SSL Certificate Requirements

**Server Container:**
- **Directory:** `/app/ssl/` [Dockerfile:20]()
- **Required files:** `cert.pem`, `key.pem`
- **Mount strategy:** Volume mount at runtime
- **Command reference:** `--ssl /app/ssl` [Dockerfile:25]()

**Client Container:**
- **Generated files:** `/app/key.pem`, `/app/cert.pem` [client/Dockerfile:16-17]()
- **Certificate type:** Self-signed X.509, RSA 2048-bit
- **Validity:** 365 days
- **Subject:** `CN=localhost`

### Client-Server Connection

The client connects to the server using environment variables:
- `VITE_QUEUE_API_URL` - Server base URL
- `VITE_QUEUE_API_PATH` - API endpoint path

See [Environment Variables](#7.1) for configuration details.

**Sources:** [Dockerfile:20-25](), [client/Dockerfile:15-19]()

---

## Package Management

### UV Package Manager (Server)

The server uses UV, a Rust-based Python package manager with faster dependency resolution than pip.

**Binary acquisition:** Multi-stage copy from official image [Dockerfile:6]()
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

**Build commands:**
- `uv venv /app/moshi/.venv --python 3.12` [Dockerfile:17]() - Creates Python 3.12 virtual environment
- `uv sync` [Dockerfile:18]() - Installs dependencies from lock file

The `uv sync` command reads `pyproject.toml` in the `moshi/` directory and installs exact versions from the lock file, ensuring reproducible builds.

### npm (Client)

The client uses npm for JavaScript package management [client/Dockerfile:7-9]():

```dockerfile
RUN npm install
RUN npm run build
```

**Process:**
1. `npm install` reads `package.json` and installs dependencies to `node_modules/`
2. `npm run build` invokes Vite, which transpiles TypeScript, bundles React components, and processes Tailwind CSS into `dist/`

**Sources:** [Dockerfile:6-18](), [client/Dockerfile:7-9]()

---

## SSL Certificate Strategies

### Server: External Mount Pattern

The server expects certificates to be provided at runtime [Dockerfile:20-25]():

```dockerfile
RUN mkdir -p /app/ssl
...
CMD ["/app/moshi/.venv/bin/python", "-m", "moshi.server", "--ssl", "/app/ssl"]
```

**Deployment pattern:**
```bash
docker run -v /path/to/certs:/app/ssl ...
```

**Benefits:**
- Supports production certificates from certificate authorities
- Enables certificate rotation without container rebuild
- Compatible with Kubernetes secrets and Docker volumes

**Required files in mount:**
- `cert.pem` - TLS certificate
- `key.pem` - Private key

### Client: Build-Time Generation

The client generates self-signed certificates during image build [client/Dockerfile:15-17]():

```dockerfile
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /app/key.pem -out /app/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

**Output:**
- `/app/key.pem` - RSA 2048-bit private key
- `/app/cert.pem` - X.509 certificate, 365-day validity, `CN=localhost`

**Production note:** Replace with trusted certificates for production use. See [Production Deployment](#5.3) for certificate management strategies.

**Sources:** [Dockerfile:20-25](), [client/Dockerfile:15-17]()

---

## Image Layer Analysis

### Server Layer Caching Strategy

```mermaid
graph TB
    L1["FROM nvcr.io/nvidia/cuda:12.4.1-runtime-ubuntu22.04<br/>Dockerfile:4<br/>Size: ~2-3 GB<br/>Cache: Stable"]
    L2["COPY --from=ghcr.io/astral-sh/uv /uv /uvx /bin/<br/>Dockerfile:6<br/>Size: ~10-20 MB<br/>Cache: Occasional UV updates"]
    L3["apt-get install libopus-dev<br/>Dockerfile:8-12<br/>Size: ~50 MB<br/>Cache: Stable"]
    L4["COPY moshi/ /app/moshi/<br/>Dockerfile:16<br/>Size: Variable<br/>Cache: Code changes"]
    L5["uv venv /app/moshi/.venv --python 3.12<br/>Dockerfile:17<br/>Size: ~50-100 MB<br/>Cache: Python version constant"]
    L6["uv sync<br/>Dockerfile:18<br/>Size: ~500 MB - 2 GB<br/>Cache: pyproject.toml changes"]
    L7["mkdir -p /app/ssl<br/>Dockerfile:20<br/>Size: Negligible<br/>Cache: Stable"]
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    L5 --> L6
    L6 --> L7
```

**Optimization notes:**
- CUDA base [Dockerfile:4]() is large but rarely changes
- UV binary copy [Dockerfile:6]() uses multi-stage `--from` to extract only binary
- Code copy [Dockerfile:16]() is separate from dependencies [Dockerfile:18](), allowing cache reuse when only code changes

### Client Layer Caching Strategy

```mermaid
graph TB
    L1["FROM node:20<br/>client/Dockerfile:1<br/>Size: ~1 GB<br/>Cache: Stable"]
    L2["WORKDIR /app<br/>client/Dockerfile:3<br/>Size: Negligible<br/>Cache: Stable"]
    L3["COPY . /app<br/>client/Dockerfile:5<br/>Size: Variable<br/>Cache: Any file change invalidates"]
    L4["npm install<br/>client/Dockerfile:7<br/>Size: ~200-500 MB<br/>Cache: Invalidated by L3 changes"]
    L5["npm run build<br/>client/Dockerfile:9<br/>Size: Variable<br/>Cache: Source code changes"]
    L6["apt-get install openssl<br/>client/Dockerfile:12<br/>Size: ~10-20 MB<br/>Cache: Stable"]
    L7["openssl req -x509<br/>client/Dockerfile:15-17<br/>Size: ~1 KB<br/>Cache: Unique each build"]
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    L5 --> L6
    L6 --> L7
```

**Optimization concern:** The `COPY . /app` [client/Dockerfile:5]() includes all files before `npm install` [client/Dockerfile:7](), invalidating dependency cache on any file change. Optimal pattern would copy `package.json` first, run `npm install`, then copy source files.

**Sources:** [Dockerfile:4-20](), [client/Dockerfile:1-17]()

---

## GPU Support and CUDA Integration

The server container explicitly includes CUDA support through its base image selection:

```dockerfile
ARG BASE_IMAGE="nvcr.io/nvidia/cuda"
ARG BASE_IMAGE_TAG="12.4.1-runtime-ubuntu22.04"
```

**Key aspects:**
- **Runtime vs. Devel:** Uses `runtime` variant [Dockerfile:2](), which includes CUDA libraries for running GPU code but not compilation tools, reducing image size
- **CUDA Version:** 12.4.1 provides compatibility with modern PyTorch distributions
- **Ubuntu Base:** 22.04 LTS ensures long-term support and stability

To utilize GPU acceleration at runtime, the container must be launched with NVIDIA Container Toolkit support (`--gpus all` flag or equivalent orchestration configuration). See [Production Deployment](#5.3) for GPU runtime requirements.

**Sources:** Dockerfile:1-4

---

