<!-- source: DeepWiki mcp.deepwiki.com · repo plandex-ai/plandex · page 7 Development and Deployment · fetched 2026-10-27 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/go.mod](app/cli/go.mod)
- [app/cli/go.sum](app/cli/go.sum)
- [app/server/go.mod](app/server/go.mod)
- [app/server/go.sum](app/server/go.sum)
- [app/shared/go.mod](app/shared/go.mod)
- [app/shared/go.sum](app/shared/go.sum)
- [releases/cli/versions/2.0.8.md](releases/cli/versions/2.0.8.md)

</details>



This page covers setting up Plandex for development and deploying it in various environments. It includes the module architecture, local development setup, and deployment options for self-hosting.

For production hosting with Plandex Cloud, see the hosting documentation.

## Overview

Plandex uses a client-server architecture with three main Go modules: CLI, server, and shared components. The system supports both cloud-hosted and self-hosted deployments, with the ability to run locally for development or deploy to production environments.

### Development and Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DevCLI["plandex-cli module"]
        DevServer["plandex-server module"]  
        DevShared["plandex-shared module"]
        DevDocker["Docker Compose\n(start_local.sh)"]
    end
    
    subgraph "Build System"
        CLIBuild["CLI Binary\n(go build)"]
        ServerBuild["Server Binary\n(go run main.go)"]
        DockerBuild["Docker Image\n(Dockerfile.server)"]
    end
    
    subgraph "Deployment Targets"
        LocalDev["Local Development\n(localhost:8099)"]
        SelfHosted["Self-Hosted Production\n(Custom Host)"]
        CloudHosted["Plandex Cloud\n(api.plandex.ai)"]
    end
    
    DevCLI --> CLIBuild
    DevServer --> ServerBuild
    DevServer --> DockerBuild
    DevDocker --> LocalDev
    
    CLIBuild --> LocalDev
    CLIBuild --> SelfHosted
    CLIBuild --> CloudHosted
    
    ServerBuild --> LocalDev
    ServerBuild --> SelfHosted
    DockerBuild --> SelfHosted
```

Sources: [app/cli/go.mod:1-89](), [app/server/go.mod:1-51](), [app/shared/go.mod:1-23](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:14-19]()

### Module Dependencies Comparison

| Module | Purpose | Key Dependencies | Build Output |
|--------|---------|------------------|--------------|
| `plandex-cli` | Command-line interface | `cobra`, `bubbletea`, `chromedp`, `go-prompt` | Binary executable |
| `plandex-server` | HTTP API server | `gorilla/mux`, `lib/pq`, `golang-migrate`, `go-tree-sitter` | Server binary or Docker image |
| `plandex-shared` | Common types and utilities | `go-openai`, `tiktoken-go`, `tablewriter` | Shared library |

Sources: [app/cli/go.mod:5-85](), [app/server/go.mod:5-48](), [app/shared/go.mod:5-22]()

## Module Dependencies and Architecture

The Plandex codebase consists of three Go modules that work together to provide the complete system functionality.

### Go Module Structure

```mermaid
graph TB
    subgraph "app/cli (plandex-cli)"
        CLI_Main["main.go"]
        CLI_Cobra["cobra commands"]
        CLI_REPL["bubbletea REPL"]
        CLI_TUI["Terminal UI"]
        CLI_HTTP["HTTP client"]
    end
    
    subgraph "app/server (plandex-server)" 
        Server_Main["main.go"]
        Server_Mux["gorilla/mux router"]
        Server_DB["lib/pq PostgreSQL"]
        Server_TreeSitter["go-tree-sitter parser"]
        Server_Migrate["golang-migrate/v4"]
    end
    
    subgraph "app/shared (plandex-shared)"
        Shared_Types["Common types"]
        Shared_OpenAI["go-openai client"]
        Shared_Tiktoken["tiktoken-go tokenizer"]
        Shared_Utils["Utility functions"]
    end
    
    CLI_Main --> Shared_Types
    CLI_HTTP --> Shared_OpenAI
    CLI_REPL --> Shared_Utils
    
    Server_Main --> Shared_Types  
    Server_Mux --> Shared_OpenAI
    Server_DB --> Shared_Utils
```

Sources: [app/cli/go.mod:1-89](), [app/server/go.mod:1-51](), [app/shared/go.mod:1-23]()

### CLI Module Dependencies

The CLI module (`plandex-cli`) provides the command-line interface and includes:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `github.com/spf13/cobra` | Command-line interface framework | v1.8.0 |
| `github.com/charmbracelet/bubbletea` | Terminal UI framework for REPL | v1.3.0 |
| `github.com/charmbracelet/lipgloss` | Terminal styling | v1.0.0 |
| `github.com/chromedp/chromedp` | Browser automation for diff UI | v0.13.3 |
| `github.com/plandex-ai/go-prompt` | Interactive prompt library | Custom fork |
| `github.com/sashabaranov/go-openai` | OpenAI API client | v1.38.1 |

The CLI replaces the shared module dependency with:
```go
replace plandex-shared => ../shared
```

Sources: [app/cli/go.mod:5-25](), [app/cli/go.mod:88]()

### Server Module Dependencies

The server module (`plandex-server`) provides the HTTP API and includes:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `github.com/gorilla/mux` | HTTP router | v1.8.1 |
| `github.com/lib/pq` | PostgreSQL driver | v1.10.9 |
| `github.com/jmoiron/sqlx` | SQL extensions | v1.4.0 |
| `github.com/golang-migrate/migrate/v4` | Database migrations | v4.18.2 |
| `github.com/smacker/go-tree-sitter` | Code parsing | v0.0.0-20240827094217 |
| `github.com/sashabaranov/go-openai` | OpenAI API client | v1.38.1 |

Sources: [app/server/go.mod:5-48]()

### Shared Module Dependencies

The shared module (`plandex-shared`) contains common types and utilities:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `github.com/sashabaranov/go-openai` | OpenAI API client types | v1.38.1 |
| `github.com/pkoukk/tiktoken-go` | Token counting | v0.1.7 |
| `github.com/olekukonko/tablewriter` | Table formatting | v0.0.5 |
| `github.com/shopspring/decimal` | Decimal number handling | v1.4.0 |

Sources: [app/shared/go.mod:5-22]()

## Local Development Environment

Setting up Plandex for local development involves running the server locally and connecting the CLI to it. This is ideal for contributing to Plandex or customizing it for your needs.

### Local Development Architecture

```mermaid
graph TB
    subgraph "Local Development Setup"
        DevCLI["plandex CLI\n(go build)"]
        StartScript["start_local.sh"]
        DockerCompose["docker-compose.yml"]
    end
    
    subgraph "Development Server Stack"
        LocalServer["plandex-server:8099\n(Docker container)"]
        PostgresDB["postgres:15\n(Docker container)"]
        FileSystem["~/plandex-server\n(Volume mount)"]
    end
    
    subgraph "External Services"
        OpenRouter["openrouter.ai\n(OPENROUTER_API_KEY)"]
        OpenAI["platform.openai.com\n(OPENAI_API_KEY)"]
    end
    
    StartScript --> DockerCompose
    DockerCompose --> LocalServer
    DockerCompose --> PostgresDB
    LocalServer --> FileSystem
    
    DevCLI --> LocalServer
    LocalServer --> OpenRouter
    LocalServer --> OpenAI
```

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:14-19](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:56-64]()

### Quick Development Setup

The quickest way to set up a local development environment:

1. **Clone the repository and start the server:**
   ```bash
   git clone https://github.com/plandex-ai/plandex.git
   cd plandex/app
   ./start_local.sh
   ```

   The `start_local.sh` script will:
   - Pull the latest Docker images
   - Start PostgreSQL and Plandex server containers
   - Set up the development environment on `http://localhost:8099`

2. **Install the CLI (if not already installed):**
   ```bash
   curl -sL https://plandex.ai/install.sh | bash
   ```

3. **Configure the CLI for local development:**
   ```bash
   plandex sign-in
   ```
   Select 'Local mode host' and confirm the default host `http://localhost:8099`.

4. **Set required API keys:**
   ```bash
   export OPENROUTER_API_KEY=<your-openrouter-api-key>
   export OPENAI_API_KEY=<your-openai-api-key>  # optional
   ```

5. **Start developing:**
   ```bash
   cd your-project-directory
   plandex
   ```

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:14-53]()

### Building from Source

For development, you can build and run the components from source:

#### CLI Development Build

```bash
cd plandex/app/cli
go build -ldflags "-X plandex/version.Version=$(cat version.txt)"
./plandex --help
```

#### Server Development Build

```bash
cd plandex/app/server
export GOENV=development
export DATABASE_URL=postgres://user:password@localhost:5432/plandex
export PLANDEX_BASE_DIR=~/plandex-server
go run main.go
```

Sources: [docs/docs/install.md:20-25](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:119-129]()

### Development Environment Variables

For local development, set these environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `GOENV` | Server mode (development/production) | `development` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@localhost:5432/plandex` |
| `PLANDEX_BASE_DIR` | Base directory for file storage | `~/plandex-server` |
| `OPENROUTER_API_KEY` | OpenRouter API access | Your API key |
| `OPENAI_API_KEY` | OpenAI API access (optional) | Your API key |
| `PLANDEX_ENV` | CLI environment mode | `development` |

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:41-72]()

### Upgrading the Development Environment

To upgrade after a new release:

```bash
cd plandex/app
# Stop the current server
ctrl-c
# Restart with latest images
./start_local.sh
```

The script automatically pulls the latest Docker images before starting.

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:56-64]()

## Self-Hosting Plandex

Self-hosting Plandex provides full control over your infrastructure and data. You can deploy it for production use with multiple users or organizations.

### Self-Hosted Production Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        CLIUsers["Multiple CLI Clients"]
        WebAPI["HTTP API Clients"]
    end
    
    subgraph "Application Layer"
        LoadBalancer["Load Balancer\n(Optional)"]
        PlandexServer["plandex-server\n(gorilla/mux)"]
        HealthCheck["Health Check\n(/health endpoint)"]
    end
    
    subgraph "Data Layer"
        PostgresDB["PostgreSQL v14+\n(lib/pq driver)"]
        FileSystem["File Storage\n(/plandex-server)"]
        GitRepos["Git Repositories\n(per-plan storage)"]
    end
    
    subgraph "External Services"
        SMTP["SMTP Server\n(Production mode)"]
        ModelAPIs["AI Model APIs\n(OpenRouter/OpenAI)"]
    end
    
    CLIUsers --> LoadBalancer
    WebAPI --> LoadBalancer
    LoadBalancer --> PlandexServer
    PlandexServer --> HealthCheck
    PlandexServer --> PostgresDB
    PlandexServer --> FileSystem
    PlandexServer --> GitRepos
    PlandexServer --> SMTP
    PlandexServer --> ModelAPIs
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:10-26](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:131-133]()

### System Requirements

For self-hosting Plandex, you need:

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| **PostgreSQL** | v14+ recommended | Plan and conversation storage |
| **File System** | Persistent storage | Git repositories and file context |
| **Git** | Latest version | Version control for plans |
| **Build Tools** | gcc, g++, make | Required for `go-tree-sitter` dependency |
| **Go Runtime** | v1.23.3+ | Server execution |
| **Docker** (Optional) | Latest version | Containerized deployment |

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:10-15](), [app/server/go.mod:3]()

### Environment Configuration

#### Development vs. Production Mode

Set the deployment mode with the `GOENV` environment variable:

| Mode | Use Case | Email | Auth Pins | Base Directory |
|------|----------|-------|-----------|----------------|
| `development` | Single user, local testing | Disabled | Skipped | `$HOME/plandex-server` |
| `production` | Multi-user, production | Required (SMTP) | Email-based | `/plandex-server` |

```bash
export GOENV=production  # or development
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:16-26]()

#### Database Setup

Create a PostgreSQL database for Plandex:

```sql
CREATE USER 'plandex_user' WITH PASSWORD 'secure_password';
CREATE DATABASE 'plandex' OWNER 'plandex_user';
GRANT ALL PRIVILEGES ON DATABASE 'plandex' TO 'plandex_user';
```

Set the database connection:
```bash
export DATABASE_URL=postgres://plandex_user:secure_password@localhost:5432/plandex
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:30-36](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:52-56]()

#### Production Environment Variables

For production deployment, configure these environment variables:

```bash
# Core Configuration
export GOENV=production
export DATABASE_URL=postgres://user:password@host:5432/plandex
export PLANDEX_BASE_DIR=/plandex-server
export PORT=8099
export API_HOST=api.your-domain.com

# SMTP Configuration (Required for production)
export SMTP_HOST=smtp.your-domain.com
export SMTP_PORT=587
export SMTP_USER=noreply@your-domain.com
export SMTP_PASSWORD=smtp_password
export SMTP_FROM=noreply@your-domain.com
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:58-78]()

### Deployment Methods

#### Docker Deployment

**Using pre-built images from DockerHub:**

```bash
docker pull plandexai/plandex-server:latest
docker run -p 8099:8099 \
  -v /plandex-server:/plandex-server \
  -e DATABASE_URL=postgres://user:password@host:5432/plandex \
  -e GOENV=production \
  -e API_HOST=api.your-domain.com \
  -e SMTP_HOST=smtp.your-domain.com \
  -e SMTP_PORT=587 \
  -e SMTP_USER=noreply@your-domain.com \
  -e SMTP_PASSWORD=smtp_password \
  plandexai/plandex-server:latest
```

**Building from source:**

```bash
git clone https://github.com/plandex-ai/plandex.git
VERSION=$(cat app/server/version.txt)
git checkout server/v$VERSION
cd plandex/app
docker build -t plandex-server -f Dockerfile.server .
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:106-113](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:84-101]()

#### Source Deployment

Run the server directly from Go source:

```bash
git clone https://github.com/plandex-ai/plandex.git
cd plandex/
VERSION=$(cat app/server/version.txt)
git checkout server/v$VERSION
cd app/server

# Set environment variables
export GOENV=production
export DATABASE_URL=postgres://user:password@host:5432/plandex
export PLANDEX_BASE_DIR=/plandex-server

# Run server
go run main.go
```

The server will start on port 8099 by default (configurable with `PORT` environment variable).

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:119-129]()

### Health Monitoring

The server provides a health check endpoint for monitoring:

```bash
curl http://your-server:8099/health
```

A successful response returns HTTP 200, indicating the server is running properly.

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:131-133]()

### Client Configuration

Configure the Plandex CLI to connect to your self-hosted server:

```bash
# Set API host for production server
export API_HOST=api.your-domain.com

# Sign in to your server
plandex sign-in
```

When prompted, select "Another host" and enter your server URL.

For development servers, you can use:
```bash
export PLANDEX_ENV=development
plandex sign-in
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:74-78](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:137-141]()

## Security Considerations

### API Key Security

- When self-hosting or using BYO API Key Mode, API keys are stored only in memory during active use
- Keys are never written to disk, logged, or stored in a database
- When a plan stream ends, API keys are removed from memory

Best practices:
- Avoid storing API keys in multiple places
- Don't expose keys to third-party services
- Don't send keys in plain text

Sources: [docs/docs/security.md:12-17]()

### File Security

Plandex respects `.gitignore` and won't load ignored files unless explicitly forced:

- Use `.gitignore` to exclude sensitive files
- Create a `.plandexignore` file with additional ignore patterns
- Use the `--force/-f` flag with `plandex load` to override ignores when needed

Sources: [docs/docs/security.md:8-9]()

## Switching Between Deployment Options

You can switch between deployment options by signing in with the desired host:

1. To switch to Plandex Cloud:
   ```bash
   plandex sign-in
   ```
   When prompted, select 'Plandex Cloud'.

2. To switch to a self-hosted server:
   ```bash
   plandex sign-in
   ```
   When prompted, select 'Local mode host' or 'Another host', then enter the appropriate host URL.

3. For development environments:
   ```bash
   export PLANDEX_ENV=development
   plandex sign-in
   ```
   This defaults to using the local development server.

Sources: [docs/docs/environment-variables.md:15-16](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:33-34]()

## Setup Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant CLI as Plandex CLI
    participant Server as Plandex Server
    participant DB as PostgreSQL
    participant AI as AI Provider APIs
    
    User->>CLI: Install CLI (curl -sL https://plandex.ai/install.sh | bash)
    User->>CLI: plandex sign-in
    
    alt Plandex Cloud
        CLI->>Server: Connect to Plandex Cloud
        User->>CLI: Select hosting mode (Integrated/BYO)
        
        alt Integrated Models
            User->>CLI: Start trial or enter payment info
        else BYO API Key
            User->>CLI: Export OPENROUTER_API_KEY & OPENAI_API_KEY
        end
    else Self-Hosted
        User->>Server: Deploy server (Docker or custom)
        Server->>DB: Initialize database
        User->>CLI: Select "Local mode host" or "Another host"
        User->>CLI: Export OPENROUTER_API_KEY & OPENAI_API_KEY
    end
    
    User->>CLI: cd project-directory
    User->>CLI: plandex
    CLI->>Server: Create new plan
    Server->>DB: Store plan
    User->>CLI: Enter prompt
    CLI->>Server: Send prompt
    Server->>AI: Query AI models
    AI->>Server: Return response
    Server->>CLI: Stream response
    CLI->>User: Display results
```

Sources: [docs/docs/cli-reference.md:800-811](), [docs/docs/quick-start.md:33-56](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:10-53]()

---

