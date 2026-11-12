<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Mongoku · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [cli.ts](cli.ts)
- [lib/JsonEncoder.ts](lib/JsonEncoder.ts)
- [server.ts](server.ts)

</details>



This document provides a comprehensive guide to installing, configuring, and running Mongoku for the first time. It covers all supported deployment methods including NPM installation, Docker deployment, and manual builds, along with essential configuration options and process management.

For detailed information about Mongoku's architecture and internal components, see [Core Architecture](#3). For advanced deployment configurations and environment-specific setups, see [Deployment and Configuration](#6).

## Installation Methods

Mongoku supports multiple installation approaches to accommodate different deployment scenarios and user preferences. Each method provides the same core functionality but offers different advantages for specific use cases.

### NPM Global Installation

The NPM installation is the recommended approach for most users, providing the simplest setup process and automatic dependency management.

```bash
# Install globally
npm install -g mongoku

# Start the server
mongoku start
```

The CLI interface defined in [cli.ts:1-66]() provides a command-line entry point that handles process management and server initialization. The `mongoku start` command loads the factory system and launches the Express server on the default port 3100.

**Sources:** [README.md:15-32](), [cli.ts:1-66]()

### Docker Deployment

Docker provides containerized deployment with consistent environments across different systems. Mongoku offers both pre-built images and custom build options.

#### Using Pre-built Docker Image

```bash
# Basic deployment
docker run -d --name mongoku -p 3100:3100 huggingface/mongoku

# With custom default hosts
docker run -d --name mongoku -p 3100:3100 \
  --env MONGOKU_DEFAULT_HOST="mongodb://user:password@myhost.com:8888" \
  huggingface/mongoku
```

#### Custom Docker Build

```bash
# Clone and build custom image
git clone <repository-url>
cd mongoku
docker build -t yournamehere/mongoku .

# Run custom image
docker run -d --name mongoku -p 3100:3100 yournamehere/mongoku
```

The [Dockerfile:1-30]() configures a Node.js 18 environment with pre-installed Angular CLI and TypeScript, building both frontend and backend components during image creation.

**Sources:** [README.md:34-55](), [Dockerfile:1-30]()

### Manual Build Process

Manual builds provide maximum control over the build process and are useful for development environments or custom deployments.

```bash
# Install build dependencies
npm install -g typescript @angular/cli
npm install

# Build frontend
cd app
npm install
ng build

# Build backend
cd ..
tsc

# Run server directly
node dist/server.js
```

This process separately compiles the Angular frontend application and TypeScript backend, creating production-ready assets in the `dist` directory.

**Sources:** [README.md:57-77]()

## Installation Method Comparison

| Method | Best For | Advantages | Requirements |
|--------|----------|------------|--------------|
| NPM Global | Quick setup, personal use | Simple commands, automatic updates | Node.js, npm |
| Docker Hub | Production deployment | Consistent environment, easy scaling | Docker runtime |
| Custom Docker | Custom configurations | Full control, reproducible builds | Docker, build tools |
| Manual Build | Development, customization | Maximum flexibility, debugging | Node.js, Angular CLI, TypeScript |

## Configuration Options

Mongoku supports extensive configuration through environment variables, allowing customization of server behavior, database connections, and operational parameters.

### Core Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGOKU_DEFAULT_HOST` | `localhost:27017` | Default MongoDB connection string |
| `MONGOKU_SERVER_PORT` | `3100` | HTTP server port |
| `MONGOKU_DATABASE_FILE` | `$HOME/.mongoku.db` | Host configuration storage file |
| `MONGOKU_COUNT_TIMEOUT` | `5000` | Document count timeout (ms) |
| `MONGOKU_READ_ONLY_MODE` | `false` | Enable read-only operations |

### Example Configuration

```bash
# Multi-host setup with authentication
export MONGOKU_DEFAULT_HOST="mongodb://user:password@localhost:27017;localhost:27017"

# Custom port and configuration file
export MONGOKU_SERVER_PORT=8000
export MONGOKU_DATABASE_FILE="/tmp/mongoku.db"

# Performance tuning
export MONGOKU_COUNT_TIMEOUT=1000

# Security mode
export MONGOKU_READ_ONLY_MODE=true
```

The server initialization in [server.ts:10-11]() reads the `MONGOKU_SERVER_PORT` environment variable to configure the Express application's listening port.

**Sources:** [README.md:79-97](), [server.ts:10-11](), [Dockerfile:5-10]()

## Startup Flow and Process Management

### Basic Startup Process

```mermaid
flowchart TD
    CLI["`mongoku start`"] --> ParseArgs["Parse CLI Arguments"]
    ParseArgs --> CheckFlags["Check PM2/Forever Flags"]
    CheckFlags --> DirectStart{"Direct Start?"}
    CheckFlags --> PM2Start{"PM2 Mode?"}
    CheckFlags --> ForeverStart{"Forever Mode?"}
    
    DirectStart -->|Yes| ServerStart["server.start()"]
    PM2Start -->|Yes| PM2Exec["pm2 start --name mongoku dist/server.js"]
    ForeverStart -->|Yes| ForeverExec["forever --uid mongoku start -a dist/server.js"]
    
    ServerStart --> FactoryLoad["factory.load()"]
    FactoryLoad --> SetupServer["setupServer()"]
    SetupServer --> ExpressListen["app.listen(SERVER_PORT)"]
    
    PM2Exec --> PM2Process["PM2 Daemon Process"]
    ForeverExec --> ForeverProcess["Forever Daemon Process"]
    
    PM2Process --> ServerInstance["Server Instance"]
    ForeverProcess --> ServerInstance
    ExpressListen --> ServerInstance
    
    ServerInstance --> Ready["Ready: http://localhost:3100"]
```

**Sources:** [cli.ts:21-65](), [server.ts:52-61]()

### Process Management Options

Mongoku supports three process management approaches:

#### Direct Execution
```bash
mongoku start
```
Runs the server in the current terminal session, suitable for development and testing.

#### PM2 Daemon
```bash
mongoku start --pm2
```
Launches Mongoku as a PM2-managed process with automatic restart capabilities and process monitoring.

#### Forever Daemon
```bash
mongoku start --forever
```
Uses Forever for process management, providing basic daemon functionality and crash recovery.

The CLI implementation in [cli.ts:38-62]() handles process manager integration by executing child processes with appropriate command-line arguments.

**Sources:** [README.md:25-32](), [cli.ts:38-62]()

## Server Architecture and Startup

```mermaid
flowchart TD
    ServerStart["server.start()"] --> FactoryLoad["factory.load()"]
    FactoryLoad --> SetupServer["setupServer()"]
    
    SetupServer --> RouteSetup["Route Configuration"]
    RouteSetup --> StaticRoute["app.get('/', serve index.html)"]
    RouteSetup --> APIRoute["app.use('/api', api)"]
    RouteSetup --> CatchallRoute["app.get('/*', serve Angular assets)"]
    
    SetupServer --> ErrorHandler["Error Handling Middleware"]
    ErrorHandler --> AppListen["app.listen(SERVER_PORT)"]
    
    StaticRoute --> ServeIndex["Serve app/index.html"]
    APIRoute --> APILayer["API Route Handlers"]
    CatchallRoute --> ServeAssets["Serve Angular Static Files"]
    
    AppListen --> ServerReady["Server Ready"]
    ServerReady --> LogOutput["Console: listening on port 3100"]
```

The server setup process in [server.ts:10-50]() configures Express middleware for serving the Angular single-page application and API endpoints, with fallback error handling for production reliability.

**Sources:** [server.ts:10-50]()

## First-Time Setup Verification

After installation and startup, verify your Mongoku deployment by following these steps:

### 1. Server Accessibility
Navigate to `http://localhost:3100` (or your configured port) to access the Mongoku web interface.

### 2. MongoDB Connection
Add your first MongoDB server connection through the Servers interface. The default configuration expects MongoDB at `localhost:27017`.

### 3. Basic Functionality Test
- Browse available databases
- Explore collections
- Execute basic queries to verify connectivity

### Common Port Configurations

| Environment | Typical Port | Configuration |
|-------------|--------------|---------------|
| Development | 3100 | Default setting |
| Production | 80/443 | Reverse proxy setup |
| Docker | 3100 | Container port mapping |
| Custom | User-defined | `MONGOKU_SERVER_PORT` environment variable |

The server listens on the port specified by `MONGOKU_SERVER_PORT` or defaults to 3100, as configured in [server.ts:11]().

**Sources:** [server.ts:11](), [server.ts:49]()

---

