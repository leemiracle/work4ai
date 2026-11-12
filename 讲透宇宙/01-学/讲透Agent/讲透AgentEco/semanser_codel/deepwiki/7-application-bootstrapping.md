<!-- source: DeepWiki mcp.deepwiki.com · repo semanser/codel · page 7 Application Bootstrapping · fetched 2026-10-27 -->

# Application Bootstrapping

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/go.mod](backend/go.mod)
- [backend/go.sum](backend/go.sum)
- [backend/main.go](backend/main.go)
- [backend/models/models.go](backend/models/models.go)
- [frontend/index.html](frontend/index.html)
- [frontend/public/android-chrome-192x192.png](frontend/public/android-chrome-192x192.png)
- [frontend/src/App.tsx](frontend/src/App.tsx)
- [frontend/src/vite-env.d.ts](frontend/src/vite-env.d.ts)
- [frontend/tsconfig.json](frontend/tsconfig.json)
- [frontend/vite.config.ts](frontend/vite.config.ts)

</details>



This page documents how the Codel application initializes and bootstraps both its backend (Go server) and frontend (React application) components. It covers the startup process, dependency initialization, and the sequence of operations that occur when the application launches.

## Overview

Codel's bootstrapping process consists of two main parts:
1. **Backend Bootstrapping**: Go server initialization, database setup, and service preparation
2. **Frontend Bootstrapping**: React application initialization, routing setup, and GraphQL client configuration

The following sections detail each part of the bootstrapping process and how they connect.

## Backend Bootstrapping

The backend bootstrapping process is responsible for initializing the Go server, configuring dependencies, establishing database connections, and preparing Docker containers.

### Backend Bootstrapping Sequence

```mermaid
sequenceDiagram
    participant "main.go" as Main
    participant "config" as Config
    participant "database" as DB
    participant "router" as Router
    participant "assets" as Assets
    participant "executor" as Executor
    participant "http" as HTTP
    
    Main->>Config: "Init()"
    Note right of Config: "Load environment variables"
    
    Main->>DB: "sql.Open(sqlite3)"
    Note right of DB: "Open database connection"
    
    Main->>DB: "goose.Up() migrations"
    Note right of DB: "Run database migrations"
    
    Main->>Router: "New(queries)"
    Note right of Router: "Set up GraphQL router"
    
    Main->>Assets: "Init(templates)"
    Note right of Assets: "Initialize prompt templates"
    
    Main->>Executor: "InitClient()"
    Note right of Executor: "Initialize Docker client"
    
    Main->>Executor: "InitBrowser(queries)"
    Note right of Executor: "Initialize browser container"
    
    Main->>HTTP: "ListenAndServe()"
    Note right of HTTP: "Start HTTP server"
    
    Main-->>Main: "Wait for termination signal"
    Main->>Executor: "Cleanup(queries)"
    Note right of Executor: "Clean up containers on shutdown"
```

Sources: [backend/main.go:31-86]()

### Backend Embedded Resources

The backend embeds several key resources during initialization:

```mermaid
graph TD
    subgraph "Embedded Resources"
        A["promptTemplates"] --> |"Embedded at compile time"| D["main.go"]
        B["scriptTemplates"] --> |"Embedded at compile time"| D
        C["embedMigrations"] --> |"Embedded at compile time"| D
    end
    
    D --> E["assets.Init()"]
    C --> F["goose.Up()"]
    
    E --> G["Prompt and script templates available for use"]
    F --> H["Database schema migration executed"]
```

Sources: [backend/main.go:22-29](), [backend/main.go:56-60]()

### Database Initialization

The database initialization process involves:

1. Opening a connection to the SQLite database
2. Creating a query interface 
3. Running migrations from embedded SQL files

```mermaid
graph TD
    A["main.go"] --> B["sql.Open(sqlite3)"]
    B --> C["database.New(db)"]
    B --> D["goose.SetDialect(sqlite3)"]
    D --> E["goose.Up(db, migrations)"]
    E --> F["Database ready"]
```

Sources: [backend/main.go:36-50]()

### Docker and Browser Initialization

Codel relies on Docker containers for task execution. The bootstrapping process initializes the Docker client and prepares a browser container:

```mermaid
graph TD
    A["main.go"] --> B["executor.InitClient()"]
    A --> C["executor.InitBrowser(queries)"]
    
    B --> D["Docker client initialized"]
    C --> E["Browser container prepared"]
    
    A -->|"On shutdown"| F["executor.Cleanup(queries)"]
    F --> G["Containers cleaned up"]
```

Sources: [backend/main.go:58-66](), [backend/main.go:80-83]()

## Frontend Bootstrapping

The frontend bootstrapping process initializes the React application, sets up routing, and configures the GraphQL client for API communication.

### Frontend Initialization Sequence

```mermaid
graph TD
    A["index.html"] -->|"Load script"| B["main.tsx"]
    B -->|"Render to DOM"| C["App.tsx"]
    
    C --> D["GraphqlProvider"]
    C --> E["RouterProvider"]
    
    D -->|"Initialize"| F["graphqlClient"]
    E -->|"Configure"| G["router"]
    
    G --> H["AppLayout"]
    H --> I["Sidebar + ChatPage"]
```

Sources: [frontend/index.html:14-17](), [frontend/src/App.tsx:17-34]()

### React Application Structure

The React application bootstraps with the following component hierarchy:

```mermaid
graph TD
    A["App"] --> B["GraphqlProvider"]
    B --> C["RouterProvider"]
    C --> D["AppLayout"]
    D --> E["Route: /chat/:id?"]
    E --> F["ChatPage"]
    
    F --> G["Messages Component"]
    F --> H["Panel Component"]
    H --> I["Terminal Component"]
    H --> J["Browser Component"]
```

Sources: [frontend/src/App.tsx:16-34]()

## Environment Configuration

The application relies on environment variables for configuration, which are loaded during the bootstrapping process.

### Backend Configuration

The backend reads environment variables through the `config.Init()` call, which initializes application settings:

```mermaid
graph TD
    A["main.go"] --> B["config.Init()"]
    B --> C["Load .env file"]
    B --> D["Parse environment variables"]
    D --> E["Set config.Config values"]
    E --> F["Configuration available throughout application"]
```

Sources: [backend/main.go:32](), [backend/go.mod:17]()

### Frontend Environment Variables

The frontend uses Vite's environment variables, defined in the `vite-env.d.ts` file:

```mermaid
graph TD
    A["vite.config.ts"] --> B["Development proxy settings"]
    C["vite-env.d.ts"] --> D["Environment type definitions"]
    D --> E["API URL and other settings"]
```

Sources: [frontend/vite.config.ts:8-13](), [frontend/src/vite-env.d.ts:3-9]()

## GraphQL API Initialization

The GraphQL API is a central part of Codel's architecture and is set up during both backend and frontend bootstrapping:

```mermaid
graph TD
    subgraph "Backend"
        A["main.go"] --> B["router.New(queries)"]
        B --> C["GraphQL resolvers"]
    end
    
    subgraph "Frontend"
        D["App.tsx"] --> E["GraphqlProvider"]
        E --> F["graphqlClient"]
    end
    
    C --- |"HTTP/WebSocket"| F
```

Sources: [backend/main.go:54](), [frontend/src/App.tsx:30]()

## Initialization Lifecycle

The overall bootstrapping lifecycle combines both backend and frontend initialization processes:

```mermaid
graph TD
    subgraph "System Startup"
        A["Start Codel application"]
    end
    
    subgraph "Backend Initialization"
        B["Load configuration"]
        C["Initialize database"]
        D["Run migrations"]
        E["Set up GraphQL API"]
        F["Initialize Docker client"]
        G["Prepare browser container"]
        H["Start HTTP server"]
    end
    
    subgraph "Frontend Initialization"
        I["Load React application"]
        J["Set up GraphQL client"]
        K["Configure router"]
        L["Render UI components"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    
    A --> I
    I --> J
    J --> K
    K --> L
    
    H --- J
```

Sources: [backend/main.go:31-86](), [frontend/src/App.tsx:28-34](), [frontend/index.html:14-17]()

## Shutdown Process

The backend also includes a graceful shutdown process that's triggered by system signals:

```mermaid
sequenceDiagram
    participant System as "Operating System"
    participant Main as "main.go"
    participant Executor as "executor"
    
    System->>Main: "SIGTERM/SIGINT"
    Note right of Main: "OS interrupt received"
    Main->>Executor: "Cleanup(queries)"
    Note right of Executor: "Clean up containers"
    Executor-->>Main: "Cleanup complete"
    Main-->>System: "Exit process"
```

Sources: [backend/main.go:33-34](), [backend/main.go:76-85]()

## Data Models Used During Bootstrapping

The bootstrapping process initializes various data models defined in the application:

| Model | Description | Used By |
|-------|-------------|---------|
| Flow | Represents a user session with tasks | Database, GraphQL API |
| Task | Individual operation to be executed | Task processor, Queue |
| Container | Docker container information | Executor, Docker client |
| Provider | Language model interface | Next task determination |

Sources: [backend/models/models.go:10-64]()

## Conclusion

The bootstrapping process in Codel follows a well-defined sequence to initialize all required components. The backend prepares the database, initializes Docker services, and starts the HTTP server with GraphQL API. The frontend initializes the React application with routing and GraphQL client setup. This coordinated bootstrapping ensures all components are properly initialized before the application becomes available to users.

When the application receives a termination signal, it performs a graceful shutdown by cleaning up containers and closing connections before exiting.