# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [README.md](README.md)
- [package.json](package.json)

</details>



## Purpose and Scope

This document provides a high-level introduction to Mongoku, explaining its purpose as a web-based MongoDB client, core features, and architectural foundations. It serves as an entry point for understanding the system before diving into specific implementation details.

For detailed installation and setup instructions, see [Getting Started](#2). For in-depth architectural documentation, see [Core Architecture](#3). For deployment-specific information, see [Deployment and Configuration](#6).

## What is Mongoku

Mongoku is a web-based MongoDB client application that enables users to query, explore, and manage MongoDB databases through a browser interface. Built as a full-stack TypeScript application, it provides a scalable solution for MongoDB administration that can handle large datasets efficiently.

The application consists of an Angular single-page application (SPA) frontend served by an Express.js backend, with specialized components for MongoDB connection management and data operations. It can be deployed locally, in containers, or as a hosted service for team collaboration.

Sources: [README.md:1-7](), [package.json:2-15]()

## Key Features and Capabilities

| Feature Category | Capabilities |
|-----------------|-------------|
| **Data Exploration** | Real-time querying, filtering, sorting, and document viewing |
| **Scalability** | Optimized for large datasets (1TB+ clusters) with fast sort/skip/limit operations |
| **Deployment Flexibility** | NPM package, Docker container, manual build, process manager support |
| **Security** | Read-only mode, AWS credential integration |
| **User Experience** | Interactive JSON viewer, theming support, responsive design |

The system supports multiple MongoDB connection types including local instances, remote servers, and AWS-hosted databases. It provides both direct execution and daemon modes using process managers like `PM2` and `Forever`.

Sources: [README.md:3-7](), [README.md:25-32](), [README.md:95-96]()

## Technology Stack

### Core Dependencies

```mermaid
graph TB
    subgraph "Frontend"
        Angular["Angular SPA<br/>@angular/cli"]
        TypeScript["TypeScript<br/>Language"]
    end
    
    subgraph "Backend"
        Express["Express.js<br/>Web Server"]
        MongoDB["mongodb<br/>Database Driver"]
        NeDB["nedb<br/>Config Storage"]
    end
    
    subgraph "Cloud Integration"
        AWSSDKCreds["@aws-sdk/credential-providers<br/>AWS Authentication"]
        AWS4["aws4<br/>Request Signing"]
    end
    
    subgraph "CLI & Process Management"
        Commander["commander<br/>CLI Interface"]
        Figlet["figlet<br/>ASCII Art"]
        Chalk["chalk<br/>Terminal Colors"]
    end
    
    Angular --> TypeScript
    Express --> MongoDB
    Express --> NeDB
    Express --> AWSSDKCreds
    Express --> AWS4
    Express --> Commander
    Commander --> Figlet
    Commander --> Chalk
```

**Core Technologies:**
- **Frontend**: Angular with TypeScript for the SPA interface
- **Backend**: Express.js server with TypeScript compilation
- **Database**: MongoDB driver v5.9.2 for database operations
- **Configuration**: NeDB for local host configuration storage
- **Cloud**: AWS SDK for credential management and request signing

Sources: [package.json:16-31]()

## High-Level System Architecture

### Application Structure

```mermaid
graph TB
    subgraph "Entry Points"
        CLI["cli.js<br/>Command Line Interface"]
        Server["server.js<br/>Express Application"]
    end
    
    subgraph "Core Backend Services"
        MongoManager["MongoManager<br/>Connection Management"]
        HostsManager["HostsManager<br/>Host Configuration"]
        Factory["Factory Pattern<br/>Dependency Injection"]
    end
    
    subgraph "Data Layer"
        MongoClient["MongoDB Client<br/>Database Driver"]
        NeDBStore["NeDB Store<br/>~/.mongoku.db"]
    end
    
    subgraph "Frontend Application"
        AngularApp["Angular SPA<br/>dist/app"]
        APIEndpoints["REST API<br/>/api/* routes"]
    end
    
    subgraph "External Systems"
        MongoDB[("MongoDB Instances")]
        Browser[("Web Browser")]
    end
    
    CLI --> Server
    Server --> Factory
    Server --> AngularApp
    Server --> APIEndpoints
    
    Factory --> MongoManager
    Factory --> HostsManager
    
    MongoManager --> MongoClient
    HostsManager --> NeDBStore
    
    MongoClient --> MongoDB
    AngularApp --> Browser
    APIEndpoints --> Browser
```

**Architecture Layers:**
- **Entry Layer**: CLI interface and Express server as main entry points
- **Service Layer**: Specialized managers for MongoDB connections and host configuration
- **Data Layer**: MongoDB driver for database operations and NeDB for local configuration
- **Presentation Layer**: Angular SPA for user interface and REST API for data access

Sources: [package.json:33](), [package.json:37-38](), [README.md:76]()

## Core Components Overview

### System Component Mapping

```mermaid
graph LR
    subgraph "Process Management"
        StartCommand["mongoku start"]
        PM2Mode["--pm2 flag"]
        ForeverMode["--forever flag"]
    end
    
    subgraph "Server Runtime"
        ExpressServer["dist/server.js<br/>Express Application"]
        CLIInterface["dist/cli.js<br/>CLI Handler"]
    end
    
    subgraph "Configuration System"
        EnvVars["Environment Variables<br/>MONGOKU_*"]
        DefaultHost["MONGOKU_DEFAULT_HOST"]
        ServerPort["MONGOKU_SERVER_PORT"]
        DatabaseFile["MONGOKU_DATABASE_FILE"]
        ReadOnlyMode["MONGOKU_READ_ONLY_MODE"]
    end
    
    subgraph "Data Operations"
        MongoConnections["MongoDB Connections"]
        ConfigStorage["~/.mongoku.db<br/>Host Storage"]
    end
    
    StartCommand --> CLIInterface
    PM2Mode --> CLIInterface
    ForeverMode --> CLIInterface
    CLIInterface --> ExpressServer
    
    EnvVars --> ExpressServer
    DefaultHost --> MongoConnections
    ServerPort --> ExpressServer
    DatabaseFile --> ConfigStorage
    ReadOnlyMode --> ExpressServer
    
    ExpressServer --> MongoConnections
    ExpressServer --> ConfigStorage
```

**Key Component Responsibilities:**

| Component | File Location | Purpose |
|-----------|---------------|---------|
| CLI Interface | `dist/cli.js` | Command-line entry point and process management |
| Express Server | `dist/server.js` | Web server and API endpoint hosting |
| Angular App | `dist/app/` | Frontend single-page application |
| Configuration | `~/.mongoku.db` | Persistent host configuration storage |

### Environment Configuration

The system supports several environment variables for runtime configuration:

- `MONGOKU_DEFAULT_HOST`: Default MongoDB connection strings
- `MONGOKU_SERVER_PORT`: Web server port (default: 3100)  
- `MONGOKU_DATABASE_FILE`: Host configuration file location
- `MONGOKU_COUNT_TIMEOUT`: Document count timeout in milliseconds
- `MONGOKU_READ_ONLY_MODE`: Security restriction flag

Sources: [README.md:81-97](), [package.json:37-42]()

## Deployment Architecture

Mongoku supports multiple deployment patterns:

1. **NPM Global Installation**: Direct installation via `npm install -g mongoku`
2. **Docker Container**: Pre-built image at `huggingface/mongoku`
3. **Manual Build**: Custom compilation of TypeScript and Angular components
4. **Process Management**: Integration with PM2 and Forever for daemon operation

The application runs on port 3100 by default and can be configured through environment variables for different deployment scenarios.

Sources: [README.md:15-32](), [README.md:34-55](), [README.md:57-77]()

---

# Page: Getting Started

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

# Page: Core Architecture

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This document provides a detailed explanation of Mongoku's internal architecture and how the major systems work together to provide a web-based MongoDB administration interface. It covers the multi-tier system design, component relationships, and data flow patterns that enable users to connect to, explore, and manage MongoDB databases through a browser interface.

For information about installation and deployment methods, see [Deployment and Configuration](#6). For details about the REST API endpoints, see [API Layer](#3.3). For frontend component details, see [Frontend Application](#3.2).

## System Overview

Mongoku implements a classic three-tier web architecture with clear separation between presentation, application logic, and data access layers. The system is built as a Node.js application that serves both a static Angular frontend and dynamic REST API endpoints.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Tier"
        Browser["Web Browser"]
        CLI["CLI Interface<br/>mongoku command"]
    end
    
    subgraph "Application Tier"
        ExpressServer["Express Server<br/>dist/server.js"]
        AngularApp["Angular SPA<br/>Static Assets"]
        APILayer["REST API<br/>/api/* routes"]
    end
    
    subgraph "Business Logic Tier"
        Factory["Factory Pattern<br/>dependency injection"]
        MongoManager["MongoManager<br/>connection orchestration"]
        HostsManager["HostsManager<br/>configuration persistence"]
    end
    
    subgraph "Data Access Tier"
        ServerAbstraction["Server abstraction"]
        DatabaseAbstraction["Database abstraction"]
        CollectionAbstraction["Collection abstraction"]
        JsonEncoder["JsonEncoder<br/>type serialization"]
    end
    
    subgraph "Storage Tier"
        MongoDB[("MongoDB Instances")]
        NeDB[("NeDB Config Store<br/>~/.mongoku.db")]
        AWSMongoDB[("AWS-hosted MongoDB")]
    end
    
    Browser --> ExpressServer
    CLI --> ExpressServer
    ExpressServer --> AngularApp
    ExpressServer --> APILayer
    
    APILayer --> Factory
    Factory --> MongoManager
    Factory --> HostsManager
    
    MongoManager --> ServerAbstraction
    MongoManager --> DatabaseAbstraction
    MongoManager --> CollectionAbstraction
    
    CollectionAbstraction --> JsonEncoder
    JsonEncoder --> MongoDB
    
    HostsManager --> NeDB
    MongoManager --> AWSMongoDB
    MongoManager --> MongoDB
```

Sources: [package.json:33-43](), [package.json:16-26]()

## Backend Architecture

The backend implements a layered architecture using Express.js as the web framework, with specialized managers handling MongoDB connections and host configuration persistence.

### Core Backend Components

```mermaid
graph TB
    subgraph "HTTP Layer"
        server_js["dist/server.js<br/>main entry point"]
        cli_js["dist/cli.js<br/>CLI interface"]
        express_routes["Express routes<br/>/api/* endpoints"]
        static_middleware["Static file middleware<br/>Angular assets"]
    end
    
    subgraph "Application Logic"
        factory_pattern["Factory pattern<br/>dependency injection"]
        mongo_manager["MongoManager<br/>connection management"]
        hosts_manager["HostsManager<br/>host configuration"]
        json_encoder["JsonEncoder<br/>MongoDB type handling"]
    end
    
    subgraph "MongoDB Integration"
        mongodb_driver["mongodb driver v5.9.2<br/>native MongoDB client"]
        connection_pool["Connection pooling<br/>managed by driver"]
        aws_credentials["AWS credential providers<br/>@aws-sdk/credential-providers"]
        aws4_signing["AWS4 request signing<br/>aws4 library"]
    end
    
    subgraph "Configuration Storage"
        nedb_store["NeDB database<br/>~/.mongoku.db"]
        host_configs["Host configuration<br/>connection strings & settings"]
    end
    
    server_js --> express_routes
    cli_js --> server_js
    express_routes --> factory_pattern
    server_js --> static_middleware
    
    factory_pattern --> mongo_manager
    factory_pattern --> hosts_manager
    
    mongo_manager --> mongodb_driver
    mongo_manager --> json_encoder
    mongodb_driver --> connection_pool
    
    mongo_manager --> aws_credentials
    aws_credentials --> aws4_signing
    
    hosts_manager --> nedb_store
    nedb_store --> host_configs
```

Sources: [package.json:38](), [package.json:33](), [package.json:24](), [package.json:25](), [package.json:17-18]()

### MongoDB Connection Management

The system uses a sophisticated connection management strategy that abstracts MongoDB operations through manager classes while supporting various deployment scenarios including AWS-hosted instances.

```mermaid
graph LR
    subgraph "Connection Abstraction"
        MongoManager["MongoManager<br/>central coordinator"]
        ServerClass["Server class<br/>server abstraction"]
        DatabaseClass["Database class<br/>database abstraction"] 
        CollectionClass["Collection class<br/>collection abstraction"]
    end
    
    subgraph "MongoDB Driver Integration"
        MongoClient["MongoClient<br/>mongodb v5.9.2"]
        Db["Db object<br/>database reference"]
        Collection["Collection object<br/>collection reference"]
    end
    
    subgraph "Authentication & AWS"
        CredentialProviders["@aws-sdk/credential-providers<br/>AWS authentication"]
        AWS4["aws4<br/>request signing"]
        ConnectionString["Connection string parsing<br/>mongodb-connection-string-url"]
    end
    
    subgraph "Data Serialization"
        BSON["BSON handling<br/>native MongoDB types"]
        JsonEncoder["JsonEncoder<br/>type conversion"]
        WebSerialization["Web-safe JSON<br/>client consumption"]
    end
    
    MongoManager --> ServerClass
    ServerClass --> DatabaseClass
    DatabaseClass --> CollectionClass
    
    ServerClass --> MongoClient
    DatabaseClass --> Db
    CollectionClass --> Collection
    
    MongoManager --> CredentialProviders
    CredentialProviders --> AWS4
    MongoClient --> ConnectionString
    
    Collection --> BSON
    BSON --> JsonEncoder
    JsonEncoder --> WebSerialization
```

Sources: [package.json:24](), [package.json:17](), [package.json:18]()

## Frontend Architecture

The frontend is implemented as an Angular Single Page Application (SPA) that communicates with the backend through REST API calls. The application provides a hierarchical navigation experience from servers to databases to collections to individual documents.

### Angular Application Structure

```mermaid
graph TB
    subgraph "Angular Application Shell"
        AppComponent["AppComponent<br/>main application shell"]
        AppRouting["App routing<br/>navigation configuration"]
        GlobalStyles["Global styles<br/>theme system"]
    end
    
    subgraph "Feature Components"
        ServersComponent["ServersComponent<br/>server management"]
        DatabasesComponent["DatabasesComponent<br/>database listing"]
        CollectionsComponent["CollectionsComponent<br/>collection browser"]
        ExploreComponent["ExploreComponent<br/>document exploration"]
        DocumentComponent["DocumentComponent<br/>individual document view"]
    end
    
    subgraph "Shared UI Components"
        SearchBoxComponent["SearchBoxComponent<br/>query interface"]
        PrettyJSONComponent["PrettyJSONComponent<br/>JSON visualization"]
        PanelComponent["PanelComponent<br/>container component"]
        NotificationsComponent["NotificationsComponent<br/>user feedback"]
    end
    
    subgraph "Services & Data"
        MongoDBService["MongoDBService<br/>API communication"]
        JsonParserService["JsonParserService<br/>data parsing"]
        NotificationService["NotificationService<br/>error handling"]
        HttpClient["HttpClient<br/>Angular HTTP client"]
    end
    
    AppComponent --> ServersComponent  
    AppComponent --> DatabasesComponent
    AppComponent --> CollectionsComponent
    AppComponent --> ExploreComponent
    AppComponent --> DocumentComponent
    
    ExploreComponent --> SearchBoxComponent
    ExploreComponent --> PrettyJSONComponent
    DocumentComponent --> PrettyJSONComponent
    
    ServersComponent --> PanelComponent
    DatabasesComponent --> PanelComponent
    CollectionsComponent --> PanelComponent
    
    ServersComponent --> MongoDBService
    DatabasesComponent --> MongoDBService
    CollectionsComponent --> MongoDBService
    ExploreComponent --> MongoDBService
    
    SearchBoxComponent --> JsonParserService
    PrettyJSONComponent --> JsonParserService
    
    MongoDBService --> HttpClient
    MongoDBService --> NotificationService
    
    AppComponent --> GlobalStyles
    AppComponent --> NotificationsComponent
```

Sources: Based on Angular SPA architecture patterns described in system diagrams

## Data Flow Architecture

The system implements a request-response pattern where frontend components make HTTP requests to Express API endpoints, which coordinate with MongoDB through the manager layer and return processed results.

### Query Processing Pipeline

```mermaid
sequenceDiagram
    participant Browser
    participant AngularSPA as "Angular SPA<br/>ExploreComponent"
    participant ExpressAPI as "Express Server<br/>/api routes"
    participant Factory as "Factory<br/>dependency injection"
    participant MongoMgr as "MongoManager<br/>connection coordinator"
    participant JsonEnc as "JsonEncoder<br/>type serialization"
    participant MongoDB as "MongoDB Instance"
    
    Browser->>AngularSPA: "User query input"
    AngularSPA->>AngularSPA: "Parse query parameters<br/>SearchBoxComponent"
    AngularSPA->>ExpressAPI: "HTTP GET /api/servers/.../query<br/>MongoDBService"
    ExpressAPI->>Factory: "Route handler invocation"
    Factory->>MongoMgr: "getCollection(server, db, collection)"
    MongoMgr->>MongoDB: "MongoClient.connect()<br/>get collection reference"
    MongoDB-->>MongoMgr: "Collection object"
    MongoMgr-->>Factory: "Collection abstraction wrapper"
    Factory->>MongoMgr: "collection.find(query, projection, sort, limit, skip)"
    MongoMgr->>MongoDB: "collection.find() execution<br/>mongodb driver"
    MongoDB-->>MongoMgr: "Raw BSON results"
    MongoMgr->>JsonEnc: "JsonEncoder.encode(results)<br/>type conversion"
    JsonEnc-->>MongoMgr: "Web-safe JSON"
    MongoMgr-->>Factory: "Serialized results"
    Factory-->>ExpressAPI: "JSON response object"
    ExpressAPI-->>AngularSPA: "HTTP 200 + JSON payload"
    AngularSPA->>AngularSPA: "PrettyJSONComponent<br/>result visualization"
    AngularSPA-->>Browser: "Updated DOM rendering"
```

Sources: Based on Express routing patterns and MongoDB integration described in system architecture

### Configuration Management Flow

```mermaid
graph LR
    subgraph "Host Configuration Persistence"
        UserInput["User adds MongoDB host<br/>ServersComponent"]
        HostsManager["HostsManager<br/>configuration management"]
        NeDBStore["NeDB storage<br/>~/.mongoku.db"]
        ConfigRetrieval["Configuration retrieval<br/>application startup"]
    end
    
    subgraph "Runtime Connection Management"
        ConnectionRequest["Connection request<br/>user navigation"]
        MongoManager["MongoManager<br/>connection coordination"]
        ConnectionPool["MongoDB connection pool<br/>driver managed"]
        ActiveConnections["Active MongoDB connections"]
    end
    
    UserInput --> HostsManager
    HostsManager --> NeDBStore
    NeDBStore --> ConfigRetrieval
    ConfigRetrieval --> HostsManager
    
    ConnectionRequest --> MongoManager
    MongoManager --> ConnectionPool
    ConnectionPool --> ActiveConnections
    HostsManager -.-> MongoManager
```

Sources: [package.json:25]() (NeDB dependency)

## Key Abstractions

The architecture relies on several key abstractions that provide clean separation of concerns and enable the system to handle various MongoDB deployment scenarios.

### Abstraction Layer Design

| Abstraction | Purpose | Key Responsibilities |
|-------------|---------|---------------------|
| `MongoManager` | Connection orchestration | MongoDB client lifecycle, connection pooling, credential management |
| `HostsManager` | Configuration persistence | Host connection strings, user preferences, NeDB operations |
| `Server` | MongoDB server representation | Server-level operations, database enumeration |
| `Database` | Database abstraction | Collection listing, database statistics |
| `Collection` | Collection operations | CRUD operations, query execution, index management |
| `JsonEncoder` | Type serialization | BSON to JSON conversion, web-safe serialization |

### Express.js Integration Pattern

```mermaid
graph TB
    subgraph "Express Application"
        app_js["Express app initialization<br/>dist/server.js"]
        middleware["Middleware stack<br/>body-parser, static files"]
        api_routes["/api/* routes<br/>REST endpoint handlers"]
        error_handler["Error handling middleware<br/>centralized error processing"]
    end
    
    subgraph "Request Processing"
        route_handler["Route handler function<br/>async/await pattern"]
        factory_injection["Factory dependency injection<br/>manager access"]
        business_logic["Business logic execution<br/>MongoDB operations"]
        response_formatting["Response formatting<br/>JSON serialization"]
    end
    
    subgraph "Static Asset Serving"
        angular_assets["Angular production build<br/>static file serving"]
        spa_routing["SPA routing fallback<br/>index.html serving"]
    end
    
    app_js --> middleware
    middleware --> api_routes
    middleware --> angular_assets
    api_routes --> route_handler
    route_handler --> factory_injection
    factory_injection --> business_logic
    business_logic --> response_formatting
    response_formatting --> error_handler
    angular_assets --> spa_routing
```

Sources: [package.json:22]() (Express dependency), [package.json:19]() (body-parser dependency)

The architecture demonstrates a well-structured separation of concerns with clear boundaries between the web layer, business logic, and data access components. The use of factory patterns for dependency injection and abstraction layers for MongoDB operations provides flexibility for different deployment scenarios while maintaining clean, testable code organization.

---

# Page: Backend Systems

# Backend Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [lib/Collection.ts](lib/Collection.ts)
- [lib/HostsManager.ts](lib/HostsManager.ts)
- [lib/JsonEncoder.ts](lib/JsonEncoder.ts)
- [lib/MongoManager.ts](lib/MongoManager.ts)

</details>



This document covers the core backend components that manage MongoDB connections, host configuration, and data operations within Mongoku. These systems form the foundation that enables the web application to interact with MongoDB instances.

For information about the HTTP API endpoints that expose these systems to the frontend, see [API Layer](#3.3). For details about the Angular frontend that consumes these backend services, see [Frontend Application](#3.2).

## Core Backend Architecture

The backend systems are organized into four primary components that work together to provide MongoDB management capabilities:

```mermaid
graph TB
    subgraph "Backend Systems"
        MongoManager["MongoManager<br/>Connection Orchestration"]
        HostsManager["HostsManager<br/>Host Configuration"]
        Collection["Collection<br/>Data Operations"]
        JsonEncoder["JsonEncoder<br/>Type Serialization"]
    end
    
    subgraph "External Storage"
        MongoDB[("MongoDB<br/>Target Databases")]
        NeDB[("NeDB<br/>~/.mongoku.db")]
    end
    
    subgraph "Configuration"
        EnvVars["Environment Variables<br/>MONGOKU_*"]
        Factory["Factory<br/>Dependency Injection"]
    end
    
    Factory --> MongoManager
    Factory --> HostsManager
    
    MongoManager --> Collection
    MongoManager --> HostsManager
    
    Collection --> JsonEncoder
    Collection --> MongoDB
    
    HostsManager --> NeDB
    MongoManager --> MongoDB
    
    EnvVars --> HostsManager
    EnvVars --> Collection
```

Sources: [lib/MongoManager.ts:1-133](), [lib/HostsManager.ts:1-92](), [lib/Collection.ts:1-108](), [lib/JsonEncoder.ts:1-61]()

## Connection Management System

The `MongoManager` class serves as the central orchestrator for all MongoDB connections within Mongoku. It maintains a registry of server connections and handles connection lifecycle, authentication, and error states.

### Core Responsibilities

| Function | Method | Description |
|----------|--------|-------------|
| Connection Management | `connect()` | Establishes MongoDB client connections |
| Authentication | `checkAuth()` | Validates credentials and permissions |
| Server Registry | `getServer()` | Retrieves server instances by hostname |
| Data Access | `getCollection()` | Provides collection access through abstraction layers |

### Connection Flow

```mermaid
sequenceDiagram
    participant Factory
    participant MongoManager
    participant HostsManager
    participant MongoClient
    participant Server
    
    Factory->>MongoManager: "load()"
    MongoManager->>HostsManager: "getHosts()"
    HostsManager-->>MongoManager: "Host[]"
    
    loop for each host
        MongoManager->>MongoManager: "connect(host)"
        MongoManager->>MongoClient: "new MongoClient(urlStr)"
        MongoClient->>MongoClient: "connect()"
        MongoClient-->>MongoManager: "connected client"
        MongoManager->>Server: "new Server(hostname, client)"
        MongoManager->>MongoManager: "checkAuth(hostname)"
        MongoManager->>Server: "toJson()"
        Server-->>MongoManager: "server metadata"
    end
```

The `MongoManager` handles both successful connections and error states, storing `MongoError` instances alongside `Server` instances in its `_servers` registry [lib/MongoManager.ts:15-17]().

Sources: [lib/MongoManager.ts:14-133]()

## Host Configuration System

The `HostsManager` class manages the persistent storage of MongoDB host configurations using NeDB as a local database. It provides the configuration foundation that `MongoManager` uses to establish connections.

### Configuration Storage

The system uses several environment variables and default behaviors:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGOKU_DEFAULT_HOST` | `localhost:27017` | Initial host configuration |
| `MONGOKU_DATABASE_FILE` | `~/.mongoku.db` | NeDB storage location |

### Host Management Operations

```mermaid
graph LR
    subgraph "HostsManager Operations"
        Load["load()<br/>Initialize NeDB"]
        GetHosts["getHosts()<br/>Retrieve all hosts"]
        Add["add(path)<br/>Upsert host entry"]
        Remove["remove(path)<br/>Delete host entry"]
    end
    
    subgraph "Storage Layer"
        NeDB[("NeDB Database<br/>~/.mongoku.db")]
        DefaultHosts["DEFAULT_HOSTS<br/>Environment Variable"]
    end
    
    Load --> NeDB
    Load --> DefaultHosts
    GetHosts --> NeDB
    Add --> NeDB
    Remove --> NeDB
```

The initialization process [lib/HostsManager.ts:22-45]() checks for an existing database file and populates default hosts on first run using the `DEFAULT_HOSTS` array derived from `MONGOKU_DEFAULT_HOST`.

Sources: [lib/HostsManager.ts:1-92]()

## Data Operations Layer

The `Collection` class provides a high-level abstraction over MongoDB collection operations, handling query execution, document manipulation, and metadata retrieval.

### CRUD Operations

| Method | Parameters | Function |
|--------|------------|----------|
| `findOne()` | `document: string` | Retrieve single document by ObjectId |
| `find()` | `query, project, sort, limit, skip` | Execute queries with pagination |
| `updateOne()` | `document, newObj, partial` | Update or replace documents |
| `removeOne()` | `document: string` | Delete single document |
| `count()` | `query` | Count documents with timeout handling |

### Query Processing Architecture

```mermaid
graph TB
    subgraph "Collection Class Methods"
        FindMethod["find(query, project, sort, limit, skip)"]
        FindOneMethod["findOne(document)"]
        UpdateMethod["updateOne(document, newObj, partial)"]
        CountMethod["count(query)"]
    end
    
    subgraph "Data Processing"
        JsonDecoder["JsonEncoder.decode()<br/>Query Parameters"]
        MongoQuery["MongoDB Collection<br/>Native Operations"]
        JsonEncoder["JsonEncoder.encode()<br/>Result Serialization"]
    end
    
    subgraph "MongoDB Driver"
        MongoCollection["MongoDb.Collection<br/>_collection"]
        ObjectId["MongoDb.ObjectId<br/>Document IDs"]
    end
    
    FindMethod --> JsonDecoder
    FindOneMethod --> ObjectId
    UpdateMethod --> JsonDecoder
    CountMethod --> JsonDecoder
    
    JsonDecoder --> MongoQuery
    ObjectId --> MongoQuery
    MongoQuery --> MongoCollection
    MongoCollection --> JsonEncoder
    JsonEncoder --> FindMethod
```

The `count()` method implements intelligent timeout handling [lib/Collection.ts:68-76](), using `estimatedDocumentCount()` as a fallback when `countDocuments()` exceeds the timeout threshold defined by `MONGOKU_COUNT_TIMEOUT`.

Sources: [lib/Collection.ts:1-108]()

## Data Serialization System

The `JsonEncoder` class handles bidirectional conversion between MongoDB-specific data types and JSON-serializable formats for API communication.

### Type Mapping

| MongoDB Type | JSON Representation | Decode Method |
|--------------|-------------------|---------------|
| `ObjectId` | `{$type: 'ObjectId', $value: string, $date: number}` | `new ObjectId()` |
| `Date` | `{$type: 'Date', $value: string}` | `new Date()` |
| `RegExp` | `{$type: 'RegExp', $value: {$pattern, $flags}}` | `new RegExp()` |

### Encoding Process

```mermaid
graph LR
    subgraph "JsonEncoder.encode()"
        Input["MongoDB Document"]
        TypeCheck["Type Detection"]
        ObjectIdCase["ObjectId → JSON"]
        DateCase["Date → JSON"]
        RegExpCase["RegExp → JSON"]
        ArrayCase["Array → Recursive"]
        ObjectCase["Object → Recursive"]
        Output["JSON Document"]
    end
    
    Input --> TypeCheck
    TypeCheck --> ObjectIdCase
    TypeCheck --> DateCase
    TypeCheck --> RegExpCase
    TypeCheck --> ArrayCase
    TypeCheck --> ObjectCase
    
    ObjectIdCase --> Output
    DateCase --> Output
    RegExpCase --> Output
    ArrayCase --> Output
    ObjectCase --> Output
```

The encoding process [lib/JsonEncoder.ts:4-37]() recursively traverses object structures, converting MongoDB types to a structured JSON format that preserves type information for accurate round-trip serialization.

Sources: [lib/JsonEncoder.ts:1-61]()

## System Integration Flow

The backend systems integrate through a coordinated data flow that spans from host configuration to query execution:

```mermaid
sequenceDiagram
    participant API as "API Layer"
    participant MM as "MongoManager"
    participant HM as "HostsManager"
    participant Server as "Server"
    participant Collection as "Collection"
    participant JE as "JsonEncoder"
    participant MongoDB as "MongoDB"
    
    Note over API,MongoDB: System Initialization
    MM->>HM: "getHosts()"
    HM-->>MM: "Host[]"
    MM->>MongoDB: "MongoClient.connect()"
    MongoDB-->>MM: "connected clients"
    
    Note over API,MongoDB: Query Execution
    API->>MM: "getCollection(server, db, collection)"
    MM->>Server: "database(databaseName)"
    Server-->>MM: "Database instance"
    MM->>Server: "collection(collectionName)"
    Server-->>MM: "Collection instance"
    MM-->>API: "Collection"
    
    API->>Collection: "find(query, project, sort, limit, skip)"
    Collection->>JE: "decode(query)"
    JE-->>Collection: "MongoDB query object"
    Collection->>MongoDB: "collection.find().toArray()"
    MongoDB-->>Collection: "raw results"
    Collection->>JE: "encode(results)"
    JE-->>Collection: "JSON results"
    Collection-->>API: "encoded documents"
```

This integration ensures that MongoDB-specific types are properly handled throughout the request lifecycle while maintaining clean separation between connection management, data operations, and serialization concerns.

Sources: [lib/MongoManager.ts:122-131](), [lib/Collection.ts:38-48](), [lib/JsonEncoder.ts:4-37]()

---

# Page: Frontend Application

# Frontend Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/package-lock.json](app/package-lock.json)
- [app/package.json](app/package.json)
- [app/src/app/app.component.html](app/src/app/app.component.html)
- [app/src/app/app.component.ts](app/src/app/app.component.ts)
- [app/src/app/filters/bytes.pipe.ts](app/src/app/filters/bytes.pipe.ts)
- [app/src/app/services/mongo-db.service.ts](app/src/app/services/mongo-db.service.ts)

</details>



## Purpose and Scope

This document covers the Angular frontend application that provides the user interface for Mongoku's web-based MongoDB client. The frontend is a Single Page Application (SPA) that communicates with the backend via REST APIs to enable users to browse databases, explore collections, and view/edit MongoDB documents through an intuitive web interface.

For information about the backend systems that serve the frontend, see [Backend Systems](#3.1). For details about the specific API endpoints used by the frontend, see [API Layer](#3.3). For user-facing features and workflows, see [User Features](#4).

## Architecture Overview

The frontend application is built as an Angular 13 SPA that follows a modular component-based architecture. The application provides a responsive interface for MongoDB database management with real-time navigation, theming support, and comprehensive error handling.

```mermaid
graph TB
    subgraph "Angular Frontend Application"
        AppComponent["App Component<br/>(app.component.ts)"]
        
        subgraph "Core Services"
            MongoDbService["MongoDbService<br/>(mongo-db.service.ts)"]
            NotificationsService["NotificationsService<br/>(notifications.service)"]
        end
        
        subgraph "UI Components"
            ServersComponent["Servers Component"]
            DatabasesComponent["Databases Component"] 
            CollectionsComponent["Collections Component"]
            ExploreComponent["Explore Component"]
            DocumentComponent["Document Component"]
        end
        
        subgraph "Shared Components"
            SearchBox["Search Box Component"]
            PrettyJSON["Pretty JSON Component"]
            Panel["Panel Component"]
            Notifications["Notifications Component"]
        end
        
        subgraph "Utilities"
            BytesPipe["BytesPipe<br/>(bytes.pipe.ts)"]
            JsonParser["JSON Parser Service"]
        end
        
        subgraph "External Dependencies"
            Angular["Angular 13.x Framework"]
            Bootstrap["Bootstrap 4.1.3"]
            CodeMirror["CodeMirror 5.x"]
            NgBootstrap["ng-bootstrap"]
        end
    end
    
    subgraph "Backend API"
        ExpressAPI["Express REST API<br/>(/api/* endpoints)"]
    end
    
    AppComponent --> ServersComponent
    AppComponent --> DatabasesComponent
    AppComponent --> CollectionsComponent
    AppComponent --> ExploreComponent
    AppComponent --> DocumentComponent
    
    ServersComponent --> MongoDbService
    DatabasesComponent --> MongoDbService
    CollectionsComponent --> MongoDbService
    ExploreComponent --> MongoDbService
    DocumentComponent --> MongoDbService
    
    MongoDbService --> NotificationsService
    MongoDbService --> ExpressAPI
    
    ExploreComponent --> SearchBox
    ExploreComponent --> PrettyJSON
    DocumentComponent --> PrettyJSON
    
    BytesPipe --> ServersComponent
    BytesPipe --> DatabasesComponent
    BytesPipe --> CollectionsComponent
    
    AppComponent --> Notifications
    
    Angular --> AppComponent
    Bootstrap --> AppComponent
    CodeMirror --> PrettyJSON
    NgBootstrap --> Panel
```

**Sources:** [app/src/app/services/mongo-db.service.ts:1-129](), [app/src/app/app.component.ts:1-94](), [app/package.json:1-56]()

## Core Services

### MongoDbService

The `MongoDbService` is the primary service responsible for all communication between the frontend and backend API. It provides a typed interface for MongoDB operations and handles error management through integration with the notifications system.

```mermaid
graph LR
    subgraph "MongoDbService Methods"
        isReadOnly["isReadOnly()"]
        getServers["getServers()"]
        addServer["addServer(url)"]
        removeServer["removeServer(server)"]
        getDatabases["getDatabases(server)"]
        getCollections["getCollections(server, database)"]
        getDocument["getDocument(server, database, collection, document)"]
        query["query(server, database, collection, query, project, sort, skip, limit)"]
        update["update(server, database, collection, document, update, partial)"]
        remove["remove(server, database, collection, document)"]
        count["count(server, database, collection, query)"]
    end
    
    subgraph "HTTP Methods"
        get["get<T>(path, options)"]
        post["post<T>(path, body, options)"]
        put["put<T>(path, body, options)"]
        delete["delete<T>(path, options)"]
    end
    
    subgraph "Error Handling"
        handleError["handleError(HttpErrorResponse)"]
        NotificationsService["NotificationsService.notifyError()"]
    end
    
    subgraph "Backend API Endpoints"
        apiServers["/api/servers"]
        apiDatabases["/api/servers/{server}/databases"]
        apiCollections["/api/servers/{server}/databases/{database}/collections"]
        apiQuery["/api/servers/{server}/databases/{database}/collections/{collection}/query"]
        apiDocuments["/api/servers/{server}/databases/{database}/collections/{collection}/documents"]
    end
    
    getServers --> get
    addServer --> put
    removeServer --> delete
    getDatabases --> get
    getCollections --> get
    getDocument --> get
    query --> get
    update --> post
    remove --> delete
    count --> get
    
    get --> handleError
    post --> handleError
    put --> handleError
    delete --> handleError
    
    handleError --> NotificationsService
    
    getServers --> apiServers
    getDatabases --> apiDatabases
    getCollections --> apiCollections
    query --> apiQuery
    getDocument --> apiDocuments
```

The service implements a consistent error handling pattern where all HTTP operations are wrapped with RxJS `catchError` operators that route errors through the `handleError` method, which then displays user-friendly error messages via the `NotificationsService`.

**Sources:** [app/src/app/services/mongo-db.service.ts:14-128]()

### Type Definitions

The service imports and re-exports key type definitions from the backend:

- `ServerJSON`: Represents MongoDB server connection information
- `DatabaseJSON`: Contains database metadata and statistics  
- `CollectionJSON`: Holds collection metadata and document counts

**Sources:** [app/src/app/services/mongo-db.service.ts:6-12]()

## Main Application Shell

### AppComponent Structure

The `AppComponent` serves as the main application shell, providing navigation, breadcrumbs, theming, and layout structure for the entire application.

```mermaid
graph TB
    subgraph "AppComponent Template Structure"
        NavBar["Navbar<br/>(navbar-dark bg-dark)"]
        Breadcrumbs["Breadcrumb Navigation<br/>(breadcrumb bg-dark)"]
        ThemeSwitch["Theme Switch Button<br/>(btn-default btn-sm)"]
        Notifications["Notifications Component<br/>(<notifications>)"]
        RouterOutlet["Router Outlet<br/>(<router-outlet>)"]
    end
    
    subgraph "AppComponent Class Features"
        BreadcrumbsArray["breadcrumbs: Breadcrumb[]"]
        RouteSubscription["Router.events.subscribe()"]
        ThemeManagement["switchTheme(theme: string)"]
        LocalStorage["localStorage theme persistence"]
    end
    
    subgraph "Breadcrumb Interface"
        BreadcrumbHref["href?: string"]
        BreadcrumbActive["active: boolean"] 
        BreadcrumbName["name: string"]
    end
    
    NavBar --> Breadcrumbs
    NavBar --> ThemeSwitch
    
    BreadcrumbsArray --> Breadcrumbs
    RouteSubscription --> BreadcrumbsArray
    ThemeManagement --> LocalStorage
    ThemeSwitch --> ThemeManagement
    
    BreadcrumbHref --> BreadcrumbInterface
    BreadcrumbActive --> BreadcrumbInterface
    BreadcrumbName --> BreadcrumbInterface
    BreadcrumbsArray --> BreadcrumbInterface
```

**Sources:** [app/src/app/app.component.html:1-25](), [app/src/app/app.component.ts:1-94]()

### Dynamic Breadcrumb Generation

The application implements intelligent breadcrumb navigation that automatically updates based on the current route. The breadcrumb system extracts parameters from the router state to build hierarchical navigation links:

| Route Level | Parameter | Breadcrumb Link |
|-------------|-----------|-----------------|
| Server | `params.server` | `/servers/{server}/databases` |
| Database | `params.database` | `/servers/{server}/databases/{database}/collections` |
| Collection | `params.collection` | `/servers/{server}/databases/{database}/collections/{collection}` |
| Document | `params.document` | Non-clickable final breadcrumb |

**Sources:** [app/src/app/app.component.ts:28-76]()

### Theme Management

The application supports light and dark themes with persistent user preference storage:

- Theme state stored in `localStorage` with key `"theme"`
- Theme classes applied to `document.body`: `"theme-light"` for light mode
- Default theme is dark (no additional class applied)
- Theme toggle button dynamically shows opposite theme name

**Sources:** [app/src/app/app.component.ts:20-25](), [app/src/app/app.component.ts:78-92]()

## Component Architecture Pattern

### Angular Framework Integration

The frontend leverages Angular 13's component-based architecture with the following key patterns:

```mermaid
graph TD
    subgraph "Angular Core Dependencies"
        AngularCore["@angular/core"]
        AngularCommon["@angular/common"] 
        AngularRouter["@angular/router"]
        AngularForms["@angular/forms"]
        AngularHttp["@angular/common/http"]
    end
    
    subgraph "Third-Party UI Components"
        NgBootstrap["@ng-bootstrap/ng-bootstrap"]
        CodemirrorWrapper["@ctrl/ngx-codemirror"]
        Bootstrap["bootstrap 4.1.3"]
    end
    
    subgraph "Code Enhancement Libraries"
        CodeMirror["codemirror ^5.65.0"]
        Esprima["esprima ^4.0.1"]
        RxJS["rxjs ^7.5.1"]
    end
    
    subgraph "Core Application Services"
        MongoDbService --> AngularHttp
        NotificationsService --> AngularCore
        JsonParserService --> Esprima
    end
    
    subgraph "UI Components"
        PrettyJSONComponent --> CodeMirror
        PrettyJSONComponent --> CodemirrorWrapper
        SearchComponent --> AngularForms
        PanelComponents --> NgBootstrap
    end
    
    AngularCore --> MongoDbService
    AngularRouter --> AppComponent
    Bootstrap --> NgBootstrap
```

**Sources:** [app/package.json:14-34]()

### Utility Components

#### BytesPipe

The `BytesPipe` provides user-friendly formatting of byte values into appropriate units (B, KB, MB, GB, TB, PB). It uses a simple algorithm that divides by 1024 until the value is less than 1024, then formats to 2 decimal places.

**Sources:** [app/src/app/filters/bytes.pipe.ts:1-26]()

## Technology Stack

### Core Framework Dependencies

| Category | Package | Version | Purpose |
|----------|---------|---------|---------|
| Framework | `@angular/core` | ^13.1.1 | Core Angular framework |
| HTTP Client | `@angular/common` | ^13.1.1 | HTTP client and common utilities |
| Routing | `@angular/router` | ^13.1.1 | Client-side routing |
| Forms | `@angular/forms` | ^13.1.1 | Reactive and template forms |
| Reactive Programming | `rxjs` | ^7.5.1 | Observables and reactive operators |

### UI and Styling Dependencies  

| Category | Package | Version | Purpose |
|----------|---------|---------|---------|
| CSS Framework | `bootstrap` | 4.1.3 | Responsive grid and components |
| Angular Bootstrap | `@ng-bootstrap/ng-bootstrap` | ^11.0.0 | Angular Bootstrap components |
| Code Editor | `codemirror` | ^5.65.0 | Code syntax highlighting |
| CodeMirror Angular | `@ctrl/ngx-codemirror` | ^5.1.1 | Angular CodeMirror wrapper |
| Sass Processing | `node-sass` | ^7.0.1 | Sass to CSS compilation |

### Development and Build Dependencies

| Category | Package | Version | Purpose |
|----------|---------|---------|---------|
| Build Tools | `@angular/cli` | ^13.1.2 | Angular CLI build system |
| Build Angular | `@angular-devkit/build-angular` | ^13.1.2 | Angular build optimizations |
| TypeScript | `typescript` | ^4.5.4 | TypeScript compiler |
| Testing | `jasmine-core` | ^4.0.0 | Unit testing framework |
| Testing | `karma` | ^6.3.10 | Test runner |

**Sources:** [app/package.json:14-54]()

### Build and Development Scripts

The application defines standard Angular CLI commands for development workflow:

- `ng serve`: Development server with hot reload
- `ng build --configuration production`: Production build with optimizations
- `ng test`: Unit test execution
- `ng lint`: Code quality linting
- `ng e2e`: End-to-end testing

**Sources:** [app/package.json:5-12]()

---

# Page: API Layer

# API Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [lib/JsonEncoder.ts](lib/JsonEncoder.ts)
- [routes/api.ts](routes/api.ts)

</details>



## Purpose and Scope

The API Layer serves as the bridge between Mongoku's Angular frontend and the backend MongoDB management systems. It provides a RESTful HTTP interface that exposes MongoDB operations through standardized endpoints, handling request parsing, response formatting, and error management. This layer is implemented as an Express.js router that coordinates with the backend systems to perform database operations.

For information about the backend systems that the API Layer interacts with, see [Backend Systems](#3.1). For details about how the frontend consumes these APIs, see [Frontend Application](#3.2).

## API Architecture Overview

The API Layer is structured as a single Express router that handles all API endpoints under the `/api` path prefix. It integrates with the backend through a factory pattern and provides consistent JSON responses across all operations.

```mermaid
graph TB
    Frontend["Angular Frontend"]
    
    subgraph "API Layer"
        APIRouter["api: express.Router()"]
        BodyParser["bodyParser.json()"]
        WriteEnabled["writeEnabled middleware"]
        ErrorHandler["Error Handling"]
    end
    
    subgraph "Backend Integration"
        Factory["factory: Factory"]
        MongoManager["factory.mongoManager"]
        HostsManager["factory.hostsManager"]
    end
    
    subgraph "Data Transformation"
        JsonEncoder["JsonEncoder.encode()"]
        QueryParser["JSON.parse()"]
    end
    
    Frontend --> APIRouter
    APIRouter --> BodyParser
    APIRouter --> WriteEnabled
    APIRouter --> Factory
    
    Factory --> MongoManager
    Factory --> HostsManager
    
    MongoManager --> JsonEncoder
    APIRouter --> QueryParser
    APIRouter --> ErrorHandler
```

Sources: [routes/api.ts:1-8](), [routes/api.ts:4-5]()

## Endpoint Structure

The API follows a hierarchical REST structure that mirrors MongoDB's organizational hierarchy: servers → databases → collections → documents.

```mermaid
graph TD
    API["/api"]
    
    ReadOnly["/readonly"]
    Servers["/servers"]
    ServerParam["/servers/:server"]
    
    Databases["/servers/:server/databases"]
    Collections["/servers/:server/databases/:database/collections"]
    Documents["/servers/:server/databases/:database/collections/:collection/documents/:document"]
    Query["/servers/:server/databases/:database/collections/:collection/query"]
    Count["/servers/:server/databases/:database/collections/:collection/count"]
    
    API --> ReadOnly
    API --> Servers
    API --> ServerParam
    API --> Databases
    API --> Collections
    API --> Documents
    API --> Query
    API --> Count
    
    ReadOnly --> ReadOnlyOp["GET: Check read-only mode"]
    Servers --> ServersGet["GET: List servers"]
    Servers --> ServersPut["PUT: Add server"]
    ServerParam --> ServersDelete["DELETE: Remove server"]
    Databases --> DatabasesGet["GET: List databases"]
    Collections --> CollectionsGet["GET: List collections"]
    Documents --> DocumentsGet["GET: Get document"]
    Documents --> DocumentsPost["POST: Update document"]
    Documents --> DocumentsDelete["DELETE: Remove document"]
    Query --> QueryGet["GET: Query collection"]
    Count --> CountGet["GET: Count documents"]
```

Sources: [routes/api.ts:10-225]()

## Core Endpoint Categories

### System Management Endpoints

| Endpoint | Method | Purpose | Middleware |
|----------|---------|---------|------------|
| `/readonly` | GET | Check if system is in read-only mode | None |
| `/servers` | GET | List all configured MongoDB servers | None |
| `/servers` | PUT | Add a new MongoDB server | `bodyParser.json()` |
| `/servers/:server` | DELETE | Remove a MongoDB server | None |

The system management endpoints handle server configuration and system status. The read-only endpoint specifically checks the `MONGOKU_READ_ONLY_MODE` environment variable.

Sources: [routes/api.ts:10-47]()

### Database Navigation Endpoints

| Endpoint | Method | Purpose |
|----------|---------|---------|
| `/servers/:server/databases` | GET | List databases on a server |
| `/servers/:server/databases/:database/collections` | GET | List collections in a database |

These endpoints provide the hierarchical navigation structure for MongoDB instances, allowing the frontend to build the database tree view.

Sources: [routes/api.ts:49-70]()

### Document Operations Endpoints

The document operations endpoints provide full CRUD functionality for individual MongoDB documents:

```mermaid
graph LR
    DocumentEndpoint["/servers/:server/databases/:database/collections/:collection/documents/:document"]
    
    GetDoc["GET: Retrieve document"]
    PostDoc["POST: Update document"]
    DeleteDoc["DELETE: Remove document"]
    
    DocumentEndpoint --> GetDoc
    DocumentEndpoint --> PostDoc
    DocumentEndpoint --> DeleteDoc
    
    PostDoc --> WriteEnabledCheck["writeEnabled middleware"]
    DeleteDoc --> WriteEnabledCheck
    
    GetDoc --> FindOne["collection.findOne()"]
    PostDoc --> UpdateOne["collection.updateOne()"]
    DeleteDoc --> RemoveOne["collection.removeOne()"]
```

Sources: [routes/api.ts:72-141]()

### Query and Aggregation Endpoints

| Endpoint | Method | Purpose | Query Parameters |
|----------|---------|---------|------------------|
| `/servers/:server/databases/:database/collections/:collection/query` | GET | Query collection with filters | `q`, `sort`, `project`, `limit`, `skip` |
| `/servers/:server/databases/:database/collections/:collection/count` | GET | Count documents matching query | `q` |

The query endpoint supports complex MongoDB query operations with full parameter parsing and validation.

Sources: [routes/api.ts:143-225]()

## Request Processing Pipeline

The API Layer implements a sophisticated request processing pipeline that handles parameter validation, JSON parsing, and MongoDB-specific type conversion:

```mermaid
sequenceDiagram
    participant Client
    participant APIRouter as "API Router"
    participant Middleware as "Middleware Stack"
    participant Backend as "Backend Systems"
    participant MongoDB as "MongoDB"
    
    Client->>APIRouter: "HTTP Request"
    APIRouter->>Middleware: "Apply middleware"
    
    alt Write Operation
        Middleware->>Middleware: "writeEnabled check"
        Middleware->>Middleware: "bodyParser.json()"
    end
    
    APIRouter->>APIRouter: "Parse route parameters"
    APIRouter->>APIRouter: "Parse query parameters"
    APIRouter->>APIRouter: "JSON.parse() for complex params"
    
    APIRouter->>Backend: "Call backend methods"
    Backend->>MongoDB: "Execute MongoDB operations"
    MongoDB-->>Backend: "Raw MongoDB results"
    Backend->>Backend: "JsonEncoder.encode()"
    Backend-->>APIRouter: "Encoded results"
    
    APIRouter-->>Client: "JSON response"
```

Sources: [routes/api.ts:148-194](), [lib/JsonEncoder.ts:4-37]()

## Data Transformation Layer

The API Layer uses the `JsonEncoder` class to handle MongoDB-specific data types that cannot be directly serialized to JSON:

### Supported Type Transformations

| MongoDB Type | JSON Representation | Encoding Logic |
|-------------|---------------------|----------------|
| `ObjectId` | `{$type: 'ObjectId', $value: string, $date: number}` | Converts to hex string with timestamp |
| `Date` | `{$type: 'Date', $value: string}` | Converts to ISO string |
| `RegExp` | `{$type: 'RegExp', $value: {$pattern: string, $flags: string}}` | Preserves pattern and flags |

```mermaid
graph TB
    MongoData["MongoDB Data"]
    
    subgraph "JsonEncoder"
        EncodeMethod["JsonEncoder.encode()"]
        TypeCheck["Type Detection"]
        Transform["Type Transformation"]
    end
    
    JSONResponse["JSON Response"]
    
    MongoData --> EncodeMethod
    EncodeMethod --> TypeCheck
    TypeCheck --> Transform
    Transform --> JSONResponse
    
    TypeCheck --> ObjectIdCheck["ObjectId → {$type, $value, $date}"]
    TypeCheck --> DateCheck["Date → {$type, $value}"]
    TypeCheck --> RegExpCheck["RegExp → {$type, $value}"]
    TypeCheck --> ArrayCheck["Array → recursive encode"]
    TypeCheck --> ObjectCheck["Object → recursive encode"]
```

Sources: [lib/JsonEncoder.ts:4-37]()

## Error Handling and Response Format

The API Layer implements consistent error handling through Express's built-in error handling mechanism. All endpoints follow a standard response format:

### Success Response Format
```json
{
  "ok": true,
  "data": "endpoint-specific data"
}
```

### Error Handling Pattern
All endpoints use a consistent error handling pattern where errors are passed to the Express error handler using `next(err)`. This ensures consistent error formatting across all API endpoints.

Sources: [routes/api.ts:27-29](), [routes/api.ts:55-57](), [routes/api.ts:93-95]()

## Read-Only Mode Support

The API Layer implements read-only mode through the `writeEnabled` middleware, which is applied to all write operations (POST, PUT, DELETE). This middleware checks the `MONGOKU_READ_ONLY_MODE` environment variable to prevent write operations when the system is configured in read-only mode.

### Write-Protected Endpoints
- `POST /servers/:server/databases/:database/collections/:collection/documents/:document`
- `DELETE /servers/:server/databases/:database/collections/:collection/documents/:document`

Sources: [routes/api.ts:5](), [routes/api.ts:98](), [routes/api.ts:121](), [routes/api.ts:10-15]()

## Query Parameter Processing

The API Layer implements sophisticated query parameter processing for the query endpoint, handling JSON parsing and validation for complex MongoDB queries:

| Parameter | Type | Default | Processing |
|-----------|------|---------|------------|
| `q` | JSON string/object | `{}` | Parsed as MongoDB query |
| `sort` | JSON string/object | `{}` | Parsed as MongoDB sort specification |
| `project` | JSON string/object | `""` | Parsed as MongoDB projection |
| `limit` | Number | `20` | Parsed as integer with validation |
| `skip` | Number | `0` | Parsed as integer with validation |

Sources: [routes/api.ts:148-177](), [routes/api.ts:201-208]()

---

# Page: User Features

# User Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/app/pages/explore/explore.component.ts](app/src/app/pages/explore/explore.component.ts)
- [app/src/app/pages/servers/servers.component.ts](app/src/app/pages/servers/servers.component.ts)

</details>



This document provides a comprehensive guide to the main features available to users for interacting with MongoDB data through Mongoku's web interface. It covers the core functionality that end users interact with, including data exploration, server management, and document operations.

For technical details about the underlying systems that power these features, see [Core Architecture](#3). For information about UI components and interface design, see [User Interface](#5).

## Overview

Mongoku provides a rich web-based interface for MongoDB database management and exploration. The main user-facing features are organized around several key workflows:

| Feature Category | Primary Component | Key Capabilities |
|------------------|-------------------|------------------|
| Data Exploration | `ExploreComponent` | Query documents, filter results, pagination |
| Server Management | `ServersComponent` | Add/remove MongoDB connections |
| Document Operations | `ExploreComponent` | View, edit, delete individual documents |
| Database Navigation | Various components | Browse databases and collections |

The application supports both read-only and read-write modes, with the read-only mode controlled by the `readOnly` property throughout the system [app/src/app/pages/explore/explore.component.ts:21]().

## Data Exploration Workflow

The core data exploration feature allows users to query and browse MongoDB collections through a sophisticated interface built around the `ExploreComponent`.

```mermaid
graph TD
    User[User] --> SearchBox["SearchBox Component"]
    SearchBox --> ExploreComponent["ExploreComponent"]
    ExploreComponent --> MongoDbService["MongoDbService"]
    MongoDbService --> APIEndpoint["/api/servers/.../query"]
    
    ExploreComponent --> QueryParams["Query Parameters"]
    QueryParams --> QueryField["query: MongoDB query"]
    QueryParams --> ProjectField["project: Field projection"]
    QueryParams --> SortField["sort: Sort specification"]
    QueryParams --> SkipField["skip: Pagination offset"]
    QueryParams --> LimitField["limit: Result limit"]
    
    ExploreComponent --> Results["Query Results"]
    Results --> PrettyJSON["PrettyJSON Display"]
    Results --> DocumentActions["Document Actions"]
    DocumentActions --> EditDocument["editDocument()"]
    DocumentActions --> RemoveDocument["remove()"]
    
    ExploreComponent --> PaginationControls["Pagination"]
    PaginationControls --> NextPage["next()"]
    PaginationControls --> PreviousPage["previous()"]
```

### Query Processing

The exploration workflow begins when users specify search parameters through the interface. The `ExploreComponent` processes these parameters and constructs MongoDB queries:

- **Query Construction**: The component accepts query parameters from the URL and transforms them into MongoDB queries [app/src/app/pages/explore/explore.component.ts:74-76]()
- **JSON Parsing**: Raw query strings are parsed using `JsonParserService` to ensure valid MongoDB query syntax [app/src/app/pages/explore/explore.component.ts:83-89]()
- **Parameter Validation**: The system validates that required parameters like `query` and `sort` are present before executing [app/src/app/pages/explore/explore.component.ts:90]()

### Query Execution

The query execution process involves multiple API calls to retrieve both data and metadata:

```mermaid
sequenceDiagram
    participant User
    participant ExploreComponent
    participant MongoDbService
    participant API
    participant MongoDB
    
    User->>ExploreComponent: "update()"
    ExploreComponent->>ExploreComponent: "Parse query parameters"
    ExploreComponent->>MongoDbService: "query(server, db, collection, ...)"
    MongoDbService->>API: "GET /api/servers/.../query"
    API->>MongoDB: "db.collection.find()"
    MongoDB-->>API: "Query results"
    API-->>MongoDbService: "JSON response"
    MongoDbService-->>ExploreComponent: "Results array"
    
    ExploreComponent->>MongoDbService: "count(server, db, collection, query)"
    MongoDbService->>API: "GET /api/servers/.../count"
    API->>MongoDB: "db.collection.countDocuments()"
    MongoDB-->>API: "Document count"
    API-->>MongoDbService: "Count response"
    MongoDbService-->>ExploreComponent: "Total count"
    
    ExploreComponent->>User: "Display results with pagination"
```

The component executes two parallel operations:
1. **Data Retrieval**: Fetches the actual documents matching the query [app/src/app/pages/explore/explore.component.ts:108-115]()
2. **Count Retrieval**: Gets the total count of matching documents for pagination [app/src/app/pages/explore/explore.component.ts:118-126]()

### Pagination System

Mongoku implements a comprehensive pagination system that allows users to navigate through large result sets:

- **Navigation Logic**: The `hasNext` and `hasPrevious` computed properties determine pagination button states [app/src/app/pages/explore/explore.component.ts:173-183]()
- **Page Navigation**: The `next()` and `previous()` methods update the `skip` parameter and trigger new queries [app/src/app/pages/explore/explore.component.ts:177-188]()
- **State Management**: The component tracks current position and total count to provide accurate pagination information [app/src/app/pages/explore/explore.component.ts:28-31]()

Sources: [app/src/app/pages/explore/explore.component.ts:1-191]()

## Document Operations

Mongoku provides comprehensive document manipulation capabilities when not in read-only mode. These operations are implemented directly within the `ExploreComponent`.

### Document Editing

The document editing feature allows users to modify documents in-place:

- **Inline Editing**: Documents can be edited directly in the results view through the `editDocument` method [app/src/app/pages/explore/explore.component.ts:138-160]()
- **ObjectId Protection**: The system prevents changes to document `_id` fields to maintain data integrity [app/src/app/pages/explore/explore.component.ts:142-145]()
- **Partial Updates**: The system supports partial updates when projection is used, updating only the visible fields [app/src/app/pages/explore/explore.component.ts:139]()

### Document Deletion

Document removal is handled through the `remove` method:

- **Safe Deletion**: The system extracts the ObjectId value safely before deletion [app/src/app/pages/explore/explore.component.ts:162-164]()
- **UI Updates**: After successful deletion, the document is removed from the local results array [app/src/app/pages/explore/explore.component.ts:168-170]()
- **Error Handling**: Failed operations are handled gracefully without affecting the UI state

### Document Navigation

Users can navigate to detailed document views:

- **Document Routing**: The `go` method navigates to individual document pages using Angular routing [app/src/app/pages/explore/explore.component.ts:129-136]()
- **URL Structure**: Document URLs follow the pattern `/servers/{server}/databases/{database}/collections/{collection}/documents/{documentId}`

Sources: [app/src/app/pages/explore/explore.component.ts:129-171]()

## Server Management

The server management functionality is implemented through the `ServersComponent`, which provides the primary interface for managing MongoDB server connections.

```mermaid
graph TD
    ServersComponent["ServersComponent"] --> ServerList["Server List Display"]
    ServersComponent --> AddServer["Add Server"]
    ServersComponent --> RemoveServer["Remove Server"]
    
    ServerList --> ServerJSON["ServerJSON[]"]
    ServerJSON --> ServerInfo["Server Information"]
    ServerJSON --> DatabaseList["Database Collections"]
    
    AddServer --> NewServerInput["newServer: string"]
    AddServer --> MongoDbService["mongoDb.addServer()"]
    
    RemoveServer --> ModalConfirmation["NgbModal Confirmation"]
    RemoveServer --> MongoDbService2["mongoDb.removeServer()"]
    
    DatabaseList --> PopoverDisplay["NgbPopover Display"]
    PopoverDisplay --> CollectionPreview["Collection Preview (20 max)"]
```

### Server Connection Management

The server management system provides several key capabilities:

- **Server Listing**: The `refresh()` method loads all configured servers from the backend [app/src/app/pages/servers/servers.component.ts:22-31]()
- **Connection Status**: Each server entry includes connection status and database information
- **Real-time Updates**: The interface automatically refreshes after server addition or removal operations

### Adding New Servers

The server addition process is streamlined through a simple interface:

- **Input Validation**: Users enter connection strings through the `newServer` string property [app/src/app/pages/servers/servers.component.ts:14]()
- **API Integration**: The `addServer()` method calls the backend API to establish new connections [app/src/app/pages/servers/servers.component.ts:45-54]()
- **State Management**: Successful additions reset the input form and refresh the server list

### Server Removal

Server removal includes safety mechanisms to prevent accidental deletions:

- **Modal Confirmation**: The `removeServer()` method requires user confirmation through `NgbModal` [app/src/app/pages/servers/servers.component.ts:56-69]()
- **Clean Removal**: Confirmed deletions call the backend API and refresh the interface
- **Error Handling**: Failed removal attempts are handled gracefully without affecting the UI

### Database and Collection Preview

The servers interface provides quick access to database structure information:

- **Collection Popover**: The `toggle()` method displays collection lists in popup windows [app/src/app/pages/servers/servers.component.ts:33-43]()
- **Collection Limiting**: Large collection lists are truncated to 20 items with a count of remaining items [app/src/app/pages/servers/servers.component.ts:37-41]()
- **Interactive Display**: Users can toggle collection visibility without navigating away from the main servers page

Sources: [app/src/app/pages/servers/servers.component.ts:1-70]()

## Read-Only Mode Support

Mongoku includes comprehensive read-only mode support that restricts destructive operations while preserving data exploration capabilities.

### Mode Detection

The read-only mode is detected and enforced at the component level:

- **Service Integration**: Components query the `MongoDbService.isReadOnly()` method to determine current mode [app/src/app/pages/explore/explore.component.ts:43-45]()
- **State Tracking**: The `readOnly` boolean property controls the availability of edit and delete operations [app/src/app/pages/explore/explore.component.ts:21]()
- **Dynamic Updates**: Mode changes are reflected immediately in the user interface

### Feature Restrictions

When read-only mode is active, the following restrictions apply:

| Operation | Read-Only Behavior | Implementation |
|-----------|-------------------|----------------|
| Document Editing | Disabled | `editDocument()` method checks disabled |
| Document Deletion | Disabled | `remove()` method unavailable |
| Server Addition | Disabled | Add server interface hidden |
| Server Removal | Disabled | Remove server options hidden |
| Data Querying | Enabled | Full query capabilities available |
| Data Viewing | Enabled | All display features functional |

### Security Considerations

The read-only mode provides an additional layer of security for production environments:

- **Backend Enforcement**: Read-only restrictions are enforced at both frontend and backend levels
- **User Communication**: The interface clearly indicates when read-only mode is active
- **Graceful Degradation**: All non-destructive features remain fully functional

Sources: [app/src/app/pages/explore/explore.component.ts:21,43-45]()

---

# Page: Data Exploration

# Data Exploration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/app/components/search-box/search-box.component.html](app/src/app/components/search-box/search-box.component.html)
- [app/src/app/components/search-box/search-box.component.ts](app/src/app/components/search-box/search-box.component.ts)
- [app/src/app/pages/explore/explore.component.html](app/src/app/pages/explore/explore.component.html)
- [app/src/app/pages/explore/explore.component.ts](app/src/app/pages/explore/explore.component.ts)

</details>



This document covers Mongoku's data exploration interface, which provides users with comprehensive tools for querying, viewing, and interacting with MongoDB documents. The exploration system combines a flexible query interface with rich document visualization and basic CRUD operations.

For information about server connection management, see [Server Management](#4.2). For details about the visual components and theming, see [Key Components](#5.1).

## Core Architecture

The data exploration system is built around two primary Angular components that work together to provide a seamless document browsing experience.

### Component Structure

```mermaid
graph TD
    ExploreComponent["ExploreComponent<br/>(explore.component.ts)"] 
    SearchBoxComponent["SearchBoxComponent<br/>(search-box.component.ts)"]
    PrettyJsonComponent["PrettyJsonComponent<br/>(pretty-json)"]
    MongoDbService["MongoDbService<br/>(mongo-db.service)"]
    JsonParserService["JsonParserService<br/>(json-parser.service)"]
    NotificationsService["NotificationsService<br/>(notifications.service)"]
    SearchParams["SearchParams<br/>(interface)"]
    
    ExploreComponent --> SearchBoxComponent
    ExploreComponent --> PrettyJsonComponent
    ExploreComponent --> MongoDbService
    ExploreComponent --> JsonParserService
    ExploreComponent --> NotificationsService
    
    SearchBoxComponent --> SearchParams
    SearchBoxComponent -.-> ExploreComponent
    
    PrettyJsonComponent -.-> ExploreComponent
    
    subgraph "Data Layer"
        MongoDbService --> MongoDB[("MongoDB<br/>Collections")]
    end
    
    subgraph "UI Components"
        SearchBoxComponent
        PrettyJsonComponent
    end
    
    subgraph "Core Logic"
        ExploreComponent
    end
```

**Sources:** [app/src/app/pages/explore/explore.component.ts:1-191](), [app/src/app/components/search-box/search-box.component.ts:1-84]()

The `ExploreComponent` serves as the main orchestrator, managing query execution, pagination, and document operations. It coordinates with the `SearchBoxComponent` for query input and `PrettyJsonComponent` for document display.

### Key Properties and State Management

| Property | Type | Purpose |
|----------|------|---------|
| `server`, `database`, `collection` | `string` | Current navigation context |
| `readOnly` | `boolean` | Controls edit/delete capabilities |
| `params` | `Partial<SearchParams>` | Current query parameters |
| `loading` | `{content: boolean, count: boolean}` | Loading states for UI |
| `count` | `{total: number, start: number}` | Pagination metadata |
| `items` | `Array` | Current document results |

**Sources:** [app/src/app/pages/explore/explore.component.ts:17-32]()

## Query Interface

The search interface provides MongoDB-native query capabilities through the `SearchBoxComponent`, supporting all standard MongoDB query operators and options.

### SearchParams Interface

```typescript
interface SearchParams {
  query:   string;    // MongoDB query document
  sort:    string;    // Sort specification
  project: string;    // Field projection
  limit:   number;    // Result limit
  skip:    number;    // Pagination offset
}
```

**Sources:** [app/src/app/components/search-box/search-box.component.ts:3-9]()

### Query Parameter Management

The search box provides a dynamic interface where users can toggle query parameters on and off. Default values are maintained for consistency:

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `query` | `"{}"` | MongoDB find query |
| `project` | `"{}"` | Field projection |
| `limit` | `20` | Documents per page |
| `skip` | `0` | Pagination offset |
| `sort` | `""` | Sort specification |

**Sources:** [app/src/app/components/search-box/search-box.component.ts:21-27]()

The interface allows users to add/remove parameters dynamically through the dropdown menu and close buttons, ensuring a clean UI that only shows relevant fields.

## Document Display and Interaction

### Document Rendering Pipeline

```mermaid
sequenceDiagram
    participant User
    participant SearchBox as "SearchBoxComponent"
    participant Explore as "ExploreComponent"
    participant MongoDB as "MongoDbService"
    participant JsonParser as "JsonParserService"
    participant PrettyJson as "PrettyJsonComponent"
    
    User->>SearchBox: "Enter query parameters"
    SearchBox->>SearchBox: "validate and format params"
    SearchBox->>Explore: "search.emit()"
    Explore->>Explore: "update()"
    Explore->>JsonParser: "parse(query/sort/project)"
    JsonParser-->>Explore: "parsed JSON objects"
    Explore->>MongoDB: "query(server, db, collection, ...)"
    MongoDB-->>Explore: "query results"
    Explore->>MongoDB: "count(server, db, collection, query)"
    MongoDB-->>Explore: "document count"
    Explore->>PrettyJson: "render documents"
    PrettyJson-->>User: "formatted document display"
```

**Sources:** [app/src/app/pages/explore/explore.component.ts:80-127](), [app/src/app/components/search-box/search-box.component.ts:70-76]()

### Document Operations

The exploration interface supports several document operations when not in read-only mode:

#### Document Editing
The `editDocument` method handles in-place document updates with validation for ObjectId changes:

```typescript
editDocument(_id, json) {
  const partial = this.params.project && Object.keys(this.jsonParser.parse(this.params.project)).length > 0;
  const newId = json && json._id && json._id.$value;
  const oldId = _id && _id.$value;
  // ObjectId change validation and update logic
}
```

**Sources:** [app/src/app/pages/explore/explore.component.ts:138-160]()

#### Document Removal
Document deletion is handled through the `remove` method, which removes documents by ObjectId and updates the local items array:

**Sources:** [app/src/app/pages/explore/explore.component.ts:162-171]()

#### Navigation to Document Detail
Users can navigate to detailed document views through the `go` method, which constructs the appropriate route:

**Sources:** [app/src/app/pages/explore/explore.component.ts:129-136]()

## Pagination System

The pagination system provides efficient navigation through large result sets using MongoDB's native `skip` and `limit` operations.

### Pagination Logic

```mermaid
flowchart TD
    Start["Query Execution"] 
    CheckNext{"hasNext()<br/>count.start + items.length < count.total"}
    CheckPrev{"hasPrevious()<br/>count.start > 0"}
    NextAction["next()<br/>params.skip += params.limit<br/>update()"]
    PrevAction["previous()<br/>params.skip = max(0, params.skip - params.limit)<br/>update()"]
    UpdateUI["Update UI with new results"]
    
    Start --> CheckNext
    Start --> CheckPrev
    CheckNext -->|true| NextAction
    CheckPrev -->|true| PrevAction
    NextAction --> UpdateUI
    PrevAction --> UpdateUI
```

**Sources:** [app/src/app/pages/explore/explore.component.ts:173-189]()

The pagination state is displayed in the UI showing current range and total document count:
```html
<span>{{ count.start + 1 | number }} - {{ count.start + items.length | number }} of </span>{{ count.total | number }} Documents
```

**Sources:** [app/src/app/pages/explore/explore.component.html:7]()

## URL State Management

The exploration interface maintains query state in the URL, allowing for bookmarkable queries and browser navigation. The component subscribes to both route parameters and query parameters:

```typescript
combineLatest(
  this.activatedRoute.paramMap,
  this.activatedRoute.queryParamMap
).subscribe(([params, queryParams]) => {
  // Extract server, database, collection from route
  // Extract query parameters from URL
});
```

**Sources:** [app/src/app/pages/explore/explore.component.ts:46-77]()

Query parameters are automatically updated in the URL when the `update` method is called, ensuring the current query state is preserved:

**Sources:** [app/src/app/pages/explore/explore.component.ts:92-97]()

## Error Handling and User Feedback

The exploration system integrates with Mongoku's notification system to provide user feedback for operations:

- **Query Errors**: Invalid JSON in query parameters
- **Update Errors**: ObjectId modification attempts, validation failures
- **Connection Errors**: MongoDB connection issues

**Sources:** [app/src/app/pages/explore/explore.component.ts:143-144](), [app/src/app/pages/explore/explore.component.ts:157]()

The interface also handles loading states to provide visual feedback during query execution, with separate loading indicators for document content and count operations.

**Sources:** [app/src/app/pages/explore/explore.component.ts:23-26](), [app/src/app/pages/explore/explore.component.html:19-23]()

---

# Page: Server Management

# Server Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/app/pages/servers/servers.component.html](app/src/app/pages/servers/servers.component.html)
- [app/src/app/pages/servers/servers.component.ts](app/src/app/pages/servers/servers.component.ts)

</details>



This document covers Mongoku's server management functionality, which allows users to add, view, and remove MongoDB server connections. Server management is the primary entry point for connecting to MongoDB instances and serves as the foundation for accessing databases and collections.

For information about browsing databases and collections within servers, see [Database and Collection Browsing](#4.3). For details about the underlying API endpoints that power server management, see [API Layer](#3.3).

## System Overview

The server management system is implemented as an Angular component that provides a user interface for managing MongoDB server connections. The system maintains a persistent list of server configurations and displays real-time information about each server's status, databases, and storage usage.

The core functionality includes:
- Adding new MongoDB servers using connection strings
- Displaying server status and metadata
- Removing servers from the managed list
- Handling connection errors and displaying appropriate feedback

Sources: [app/src/app/pages/servers/servers.component.ts:1-71]()

## Core Components

### ServersComponent

The `ServersComponent` class serves as the main controller for server management operations. It manages the component state and coordinates interactions between the user interface and the backend services.

| Property | Type | Purpose |
|----------|------|---------|
| `servers` | `ServerJSON[]` | Array of server configurations and metadata |
| `loading` | `boolean` | Loading state indicator |
| `adding` | `boolean` | Flag for add server form visibility |
| `newServer` | `string` | Connection string for new server |

**Server Management Operations**

```mermaid
graph TD
    ServersComponent["ServersComponent"]
    MongoDbService["MongoDbService"]
    NgbModal["NgbModal"]
    
    ServersComponent --> |"getServers()"| MongoDbService
    ServersComponent --> |"addServer(connectionString)"| MongoDbService  
    ServersComponent --> |"removeServer(serverName)"| MongoDbService
    ServersComponent --> |"open(modal)"| NgbModal
    
    MongoDbService --> |"ServerJSON[]"| ServersComponent
    MongoDbService --> |"{ok: boolean}"| ServersComponent
```

Sources: [app/src/app/pages/servers/servers.component.ts:10-16](), [app/src/app/pages/servers/servers.component.ts:45-69]()

### Key Methods

The component implements several core methods for server lifecycle management:

- `refresh()` - Fetches the current list of servers from the backend
- `addServer()` - Adds a new server using the provided connection string
- `removeServer()` - Removes a server after user confirmation
- `toggle()` - Manages popover display for database information

Sources: [app/src/app/pages/servers/servers.component.ts:22-31](), [app/src/app/pages/servers/servers.component.ts:45-69]()

## Server Management Data Flow

### Server Addition Process

```mermaid
sequenceDiagram
    participant User
    participant ServersComponent
    participant MongoDbService
    participant Backend
    participant MongoDB
    
    User->>ServersComponent: "Click Add Server"
    ServersComponent->>ServersComponent: "Set adding = true"
    User->>ServersComponent: "Enter connection string"
    User->>ServersComponent: "Click Add button"
    ServersComponent->>MongoDbService: "addServer(connectionString)"
    MongoDbService->>Backend: "POST /api/servers"
    Backend->>MongoDB: "Test connection"
    MongoDB-->>Backend: "Connection result"
    Backend-->>MongoDbService: "{ok: boolean}"
    MongoDbService-->>ServersComponent: "Response data"
    ServersComponent->>ServersComponent: "refresh() if successful"
    ServersComponent->>User: "Updated server list"
```

Sources: [app/src/app/pages/servers/servers.component.ts:45-54]()

### Server Information Display

The system displays comprehensive server information including connection status, database count, and total storage size. Error states are handled gracefully with badge indicators and tooltips.

```mermaid
graph LR
    ServerJSON["ServerJSON"]
    
    ServerJSON --> name["name: string"]
    ServerJSON --> databases["databases: DatabaseInfo[]"]
    ServerJSON --> size["size: number"]
    ServerJSON --> error["error?: ErrorInfo"]
    
    databases --> database_name["name: string"]
    databases --> collections["collections: CollectionInfo[]"]
    databases --> database_size["size: number"]
    
    error --> error_message["message: string"]
```

Sources: [app/src/app/pages/servers/servers.component.html:29-47]()

## User Interface Components

### Server List Table

The main interface displays servers in a responsive table format with the following columns:

| Column | Content | Interactive Features |
|--------|---------|---------------------|
| Name | Server identifier with connection status | Clickable link to databases (if healthy) |
| Databases | Count with detailed popover | Hover to show database breakdown |
| Size | Total storage across all databases | Formatted using bytes pipe |
| Actions | Remove button | Confirmation modal |

### Add Server Form

The add server interface provides inline form controls:
- Connection string input with placeholder format `user:password@hostname:port`
- Toggle button to show/hide the form
- Validation to prevent empty submissions
- Loading state management during operations

Sources: [app/src/app/pages/servers/servers.component.html:6-18]()

### Error Handling

Connection errors are displayed using Bootstrap badge components with tooltips showing detailed error messages. Failed servers remain in the list but are marked with error indicators and cannot be navigated.

Sources: [app/src/app/pages/servers/servers.component.html:32-35]()

## Modal Interactions

### Confirmation Dialog

Server removal operations require explicit user confirmation through a modal dialog to prevent accidental data loss. The modal implementation uses NgBootstrap components.

```mermaid
graph TD
    RemoveButton["Remove Button Click"]
    NgbModal["NgbModal.open()"]
    ConfirmModal["Confirmation Modal"]
    UserChoice{"User Choice"}
    RemoveAPI["mongoDb.removeServer()"]
    Refresh["refresh()"]
    
    RemoveButton --> NgbModal
    NgbModal --> ConfirmModal
    ConfirmModal --> UserChoice
    UserChoice -->|"Yes"| RemoveAPI
    UserChoice -->|"No/Cancel"| Refresh
    RemoveAPI --> Refresh
```

Sources: [app/src/app/pages/servers/servers.component.ts:56-69](), [app/src/app/pages/servers/servers.component.html:89-100]()

### Database Information Popover

Database details are displayed in interactive popovers triggered by hover events. The popover content includes:
- Database name
- Collection count
- Individual database size
- Clipping indicator for large lists (shows first 20 items)

Sources: [app/src/app/pages/servers/servers.component.ts:33-43](), [app/src/app/pages/servers/servers.component.html:69-87]()

---

# Page: Database and Collection Browsing

# Database and Collection Browsing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/app/pages/collections/collections.component.html](app/src/app/pages/collections/collections.component.html)
- [app/src/app/pages/collections/collections.component.ts](app/src/app/pages/collections/collections.component.ts)
- [app/src/app/pages/databases/databases.component.html](app/src/app/pages/databases/databases.component.html)
- [app/src/app/pages/databases/databases.component.ts](app/src/app/pages/databases/databases.component.ts)

</details>



This document covers Mongoku's database and collection browsing capabilities, which allow users to navigate the hierarchical structure of MongoDB instances and view metadata about databases and collections. This functionality provides the foundation for exploring MongoDB data structures before diving into document-level operations.

For detailed information about exploring and querying documents within collections, see [Data Exploration](#4.1). For managing server connections, see [Server Management](#4.2).

## Navigation Hierarchy

Mongoku implements a three-level hierarchical navigation system for MongoDB data browsing:

```mermaid
graph TD
    Server["Server Connection"] --> Database["Database Level"] 
    Database --> Collection["Collection Level"]
    Collection --> Documents["Document Exploration"]
    
    Server -.-> ServerStats["Server Statistics"]
    Database -.-> DatabaseStats["Database Statistics<br/>Storage & Performance Metrics"]
    Collection -.-> CollectionStats["Collection Statistics<br/>Indexes & Size Information"]
    
    subgraph "UI Components"
        DatabasesComponent["DatabasesComponent<br/>/servers/:server/databases"]
        CollectionsComponent["CollectionsComponent<br/>/servers/:server/databases/:database/collections"]
    end
    
    Database --> DatabasesComponent
    Collection --> CollectionsComponent
```

Each level provides progressively more granular information about the MongoDB data structure, with routing handled through Angular's router system using parameterized URLs.

Sources: [app/src/app/pages/databases/databases.component.html:12](), [app/src/app/pages/collections/collections.component.html:13]()

## Database Browsing Interface

The `DatabasesComponent` presents a tabular view of all databases available on a selected server. The interface displays three primary columns of information for each database:

| Column | Data Source | Description |
|--------|-------------|-------------|
| name | `database.name` | Database identifier with navigation link |
| collections | `database.collections.length` | Count of collections with hover details |
| size | `database.size` | Total database size with detailed statistics |

```mermaid
graph LR
    subgraph "DatabasesComponent Flow"
        RouteParams["ActivatedRoute<br/>paramMap"] --> ServerParam["server parameter"]
        ServerParam --> MongoDbService["MongoDbService<br/>getDatabases()"]
        MongoDbService --> DatabaseJSON["DatabaseJSON[]<br/>Response Data"]
        DatabaseJSON --> TableDisplay["HTML Table Display"]
        
        subgraph "Interactive Features"
            HoverCollection["Collection List Popover<br/>toggleCollection()"]
            HoverStats["Database Stats Popover<br/>toggleStats()"]
        end
        
        TableDisplay --> HoverCollection
        TableDisplay --> HoverStats
    end
```

The component implements hover-activated popovers using Angular Bootstrap's `NgbPopover` directive. When users hover over collection counts, they see a detailed breakdown of individual collections with their respective sizes. Similarly, hovering over the size column reveals comprehensive database statistics including average object size, data size, storage size, and index size.

Sources: [app/src/app/pages/databases/databases.component.ts:23-31](), [app/src/app/pages/databases/databases.component.html:4-45]()

## Collection Browsing Interface

The `CollectionsComponent` provides detailed metadata about collections within a specific database. The interface extends the database browsing pattern with additional collection-specific information:

| Column | Data Source | Description |
|--------|-------------|-------------|
| name | `collection.name` | Collection identifier with navigation link |
| documents | `collection.count` | Document count in collection |
| indexes | `collection.nIndexes` | Number of indexes with detailed breakdown |
| size | `collection.size` | Collection size with performance statistics |

```mermaid
graph TD
    subgraph "CollectionsComponent Architecture"
        RouteParams["ActivatedRoute<br/>server + database params"] --> ServiceCall["MongoDbService<br/>getCollections(server, database)"]
        ServiceCall --> CollectionData["CollectionJSON[]<br/>Response Array"]
        
        subgraph "Data Processing"
            IndexParser["indexName()<br/>Parse Index Names"]
            StatsExtractor["Collection Statistics<br/>Extraction"]
        end
        
        CollectionData --> IndexParser
        CollectionData --> StatsExtractor
        
        subgraph "UI Rendering"
            TableView["HTML Table<br/>collections.component.html"]
            IndexPopover["Index Details Popover<br/>toggleIndexes()"]
            StatsPopover["Stats Details Popover<br/>toggleStats()"]
        end
        
        IndexParser --> IndexPopover
        StatsExtractor --> StatsPopover
        CollectionData --> TableView
    end
```

The collections interface includes sophisticated index name parsing through the `indexName()` method, which converts MongoDB's internal index naming convention into human-readable JSON objects. This method handles special cases like `_id` field transformations and directional indicators.

Sources: [app/src/app/pages/collections/collections.component.ts:35-44](), [app/src/app/pages/collections/collections.component.html:1-90]()

## Statistics and Metadata Display

Both database and collection browsing interfaces implement rich metadata display through popover components. These popovers provide detailed statistics without cluttering the main interface:

### Database Statistics Popover
- Average object size
- Data size
- Storage size  
- Index size

### Collection Statistics Popover
- Average object size
- Data size
- Storage size
- Total index size

### Index Information Popover
- Individual index names (parsed from MongoDB format)
- Index sizes
- Truncation indicator for large index lists (>20 items)

```mermaid
graph LR
    subgraph "Popover Implementation Pattern"
        MouseEnter["mouseenter event"] --> ToggleMethod["toggle*() method"]
        ToggleMethod --> PopoverData["Data Preparation<br/>stats/indexes/collections"]
        PopoverData --> NgbPopover["NgbPopover.open()<br/>with prepared data"]
        
        MouseLeave["mouseleave event"] --> ClosePopover["NgbPopover.close()"]
        
        subgraph "Data Limiting"
            DataFilter["Filter to 20 items<br/>clippedCol/clippedIndexes"]
            ClippedIndicator["'X more items...'<br/>overflow indicator"]
        end
        
        PopoverData --> DataFilter
        DataFilter --> ClippedIndicator
    end
```

The popover system implements data limiting to maintain performance with large datasets. Both collection lists and index lists are truncated to 20 items with overflow indicators showing the count of additional items.

Sources: [app/src/app/pages/databases/databases.component.ts:45-51](), [app/src/app/pages/collections/collections.component.ts:58-70]()

## Data Flow and Service Integration

Database and collection browsing relies on the `MongoDbService` for data retrieval, implementing a consistent pattern across both components:

```mermaid
sequenceDiagram
    participant Route as "Angular Router"
    participant Component as "Database/Collections Component"
    participant Service as "MongoDbService"
    participant API as "Backend API"
    participant MongoDB as "MongoDB Instance"
    
    Route->>Component: "Route parameters (server/database)"
    Component->>Component: "Set loading = true"
    Component->>Service: "getDatabases() or getCollections()"
    Service->>API: "HTTP GET /api/servers/.../databases"
    API->>MongoDB: "MongoDB query"
    MongoDB-->>API: "Raw database/collection data"
    API-->>Service: "JSON response"
    Service-->>Component: "DatabaseJSON[] or CollectionJSON[]"
    Component->>Component: "Set loading = false"
    Component->>Component: "Render data in table"
```

Both components implement identical loading state management and error handling patterns. The loading state is displayed as a centered "Loading..." message while data is being fetched, and empty states show appropriate "No databases..." or "No collections..." messages.

Sources: [app/src/app/pages/databases/databases.component.ts:19-31](), [app/src/app/pages/collections/collections.component.ts:20-33]()

---

# Page: User Interface

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/app/components/pretty-json/pretty-json.component.ts](app/src/app/components/pretty-json/pretty-json.component.ts)
- [app/src/app/services/json-parser.service.ts](app/src/app/services/json-parser.service.ts)
- [app/src/app/services/services.module.ts](app/src/app/services/services.module.ts)
- [app/src/sass/themes/dark-default.scss](app/src/sass/themes/dark-default.scss)
- [app/src/sass/themes/light.scss](app/src/sass/themes/light.scss)

</details>



This document covers Mongoku's user interface architecture, core UI components, and styling system. It provides an overview of how the Angular frontend application presents MongoDB data to users through interactive components and customizable themes.

For detailed information about specific UI components like PrettyJSON and search functionality, see [Key Components](#5.1). For theming and visual customization options, see [Theming and Styling](#5.2).

## UI Architecture Overview

Mongoku's user interface is built as an Angular Single Page Application (SPA) with a component-based architecture. The UI layer handles data visualization, user interactions, and provides a responsive interface for MongoDB operations.

### Frontend Component Structure

```mermaid
graph TB
    AppComponent["AppComponent<br/>Main Application Shell"]
    
    subgraph "Page Components"
        ServersComponent["ServersComponent<br/>Server Management"]
        DatabasesComponent["DatabasesComponent<br/>Database Listing"]
        CollectionsComponent["CollectionsComponent<br/>Collection Browser"]
        ExploreComponent["ExploreComponent<br/>Document Exploration"]
        DocumentComponent["DocumentComponent<br/>Document Viewer"]
    end
    
    subgraph "Shared UI Components"
        PrettyJsonComponent["PrettyJsonComponent<br/>JSON Data Renderer"]
        SearchBoxComponent["SearchBoxComponent<br/>Query Interface"]
        PanelComponent["PanelComponent<br/>Container Wrapper"]
        NotificationsComponent["NotificationsComponent<br/>User Feedback"]
    end
    
    subgraph "UI Services"
        JsonParserService["JsonParserService<br/>Data Parsing Logic"]
        NotificationsService["NotificationsService<br/>Error Handling"]
        MongoDbService["MongoDbService<br/>API Communication"]
    end
    
    AppComponent --> ServersComponent
    AppComponent --> DatabasesComponent
    AppComponent --> CollectionsComponent
    AppComponent --> ExploreComponent
    AppComponent --> DocumentComponent
    
    ExploreComponent --> PrettyJsonComponent
    DocumentComponent --> PrettyJsonComponent
    ExploreComponent --> SearchBoxComponent
    
    PrettyJsonComponent --> JsonParserService
    PrettyJsonComponent --> NotificationsService
    
    ServersComponent --> MongoDbService
    DatabasesComponent --> MongoDbService
    CollectionsComponent --> MongoDbService
    ExploreComponent --> MongoDbService
```

Sources: [app/src/app/components/pretty-json/pretty-json.component.ts:1-383](), [app/src/app/services/json-parser.service.ts:1-141](), [app/src/app/services/services.module.ts:1-18]()

## Core UI Components

### PrettyJsonComponent

The `PrettyJsonComponent` is the primary data visualization component responsible for rendering MongoDB documents in a formatted, interactive JSON view. It provides collapsible tree structures, syntax highlighting, and edit capabilities.

| Property | Type | Description |
|----------|------|-------------|
| `json` | `any` | Input data to be displayed |
| `autoCollapse` | `boolean` | Automatically collapse nested structures |
| `readOnly` | `boolean` | Disable editing functionality |
| `go` | `EventEmitter` | Navigate to referenced documents |
| `edit` | `EventEmitter` | Handle document modifications |
| `remove` | `EventEmitter` | Delete document operations |

The component uses a custom rendering engine that converts JSON objects into DOM elements with appropriate CSS classes for styling and interaction.

### JSON Data Type Handling

```mermaid
graph LR
    JsonInput["JSON Input Data"]
    
    subgraph "Type Processing"
        StringType["String Values<br/>quote() method"]
        NumberType["Number Values<br/>span('value number')"]
        BooleanType["Boolean Values<br/>span('value boolean')"]
        ObjectIdType["ObjectId Type<br/>fnCall('ObjectId')"]
        DateType["Date Type<br/>fnCall('Date')"]
        RegExpType["RegExp Type<br/>span('value regexp')"]
        ArrayType["Array Values<br/>span('value array')"]
        ObjectType["Object Values<br/>span('value object')"]
    end
    
    subgraph "Rendered Output"
        FormattedDOM["Formatted DOM Elements<br/>with CSS Classes"]
        InteractiveElements["Collapsible Structures<br/>Edit Capabilities"]
    end
    
    JsonInput --> StringType
    JsonInput --> NumberType
    JsonInput --> BooleanType
    JsonInput --> ObjectIdType
    JsonInput --> DateType
    JsonInput --> RegExpType
    JsonInput --> ArrayType
    JsonInput --> ObjectType
    
    StringType --> FormattedDOM
    NumberType --> FormattedDOM
    BooleanType --> FormattedDOM
    ObjectIdType --> FormattedDOM
    DateType --> FormattedDOM
    RegExpType --> FormattedDOM
    ArrayType --> InteractiveElements
    ObjectType --> InteractiveElements
    
    FormattedDOM --> InteractiveElements
```

Sources: [app/src/app/components/pretty-json/pretty-json.component.ts:225-352]()

### Interactive Features

The `PrettyJsonComponent` provides several interactive capabilities:

- **Collapsible Views**: Arrays and objects can be collapsed/expanded using the `collapse()` method [app/src/app/components/pretty-json/pretty-json.component.ts:365-381]()
- **In-line Editing**: CodeMirror-based editor with syntax validation [app/src/app/components/pretty-json/pretty-json.component.ts:82-119]()
- **Document Navigation**: Clickable ObjectId references for cross-document navigation [app/src/app/components/pretty-json/pretty-json.component.ts:133-136]()
- **Link Detection**: Automatic URL linking for string values [app/src/app/components/pretty-json/pretty-json.component.ts:184-190]()

Sources: [app/src/app/components/pretty-json/pretty-json.component.ts:50-119]()

## Styling and Theme System

Mongoku implements a CSS custom property-based theming system supporting both light and dark color schemes. The theming system uses CSS variables to enable dynamic theme switching.

### Theme Structure

| Theme Variable | Light Theme Value | Dark Theme Value | Usage |
|----------------|-------------------|------------------|-------|
| `--background-color` | `hsl(228, 26%, 98%)` | `hsl(216, 26%, 15%)` | Main background |
| `--text` | `hsl(0, 0%, 12%)` | `hsl(0, 0%, 88%)` | Primary text |
| `--panel-body` | `hsl(232, 23%, 93%)` | `hsl(220, 23%, 21%)` | Panel backgrounds |
| `--code-string` | `#a31515` | `#ce9178` | JSON string values |
| `--code-numbers` | `#09885a` | `#b5cea8` | Numeric values |
| `--code-boolean` | `#0000ff` | `#569cd6` | Boolean/null values |

Sources: [app/src/sass/themes/light.scss:1-35](), [app/src/sass/themes/dark-default.scss:1-35]()

### JSON Syntax Highlighting

The `PrettyJsonComponent` applies semantic CSS classes for syntax highlighting:

- `.value.string` - String literals
- `.value.number` - Numeric values  
- `.value.boolean` - Boolean values
- `.value.null` - Null values
- `.value.regexp` - Regular expressions
- `.call.function` - MongoDB type constructors (ObjectId, Date)

Sources: [app/src/app/components/pretty-json/pretty-json.component.ts:237-260]()

## Data Flow Architecture

The UI components follow a unidirectional data flow pattern where user interactions trigger events that flow up to parent components and services.

### Component Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant PrettyJsonComponent
    participant JsonParserService
    participant NotificationsService
    participant ParentComponent
    
    User->>PrettyJsonComponent: "Clicks edit button"
    PrettyJsonComponent->>PrettyJsonComponent: "enableEditor()"
    PrettyJsonComponent->>User: "Show CodeMirror editor"
    
    User->>PrettyJsonComponent: "Modifies JSON content"
    User->>PrettyJsonComponent: "Saves changes (Ctrl+Enter)"
    PrettyJsonComponent->>JsonParserService: "parse(editJson)"
    
    alt "Parse Success"
        JsonParserService->>PrettyJsonComponent: "Parsed JSON object"
        PrettyJsonComponent->>ParentComponent: "edit.emit(updatedJson)"
        PrettyJsonComponent->>PrettyJsonComponent: "disableEditor()"
    else "Parse Error"
        JsonParserService->>NotificationsService: "reportError(message)"
        NotificationsService->>User: "Display error notification"
        PrettyJsonComponent->>PrettyJsonComponent: "Highlight error line"
    end
```

Sources: [app/src/app/components/pretty-json/pretty-json.component.ts:99-119](), [app/src/app/services/json-parser.service.ts:105-139]()

## Error Handling and User Feedback

The UI implements comprehensive error handling through the `NotificationsService`, which provides user feedback for various error conditions:

- JSON parsing errors with line-specific highlighting
- MongoDB connection failures
- Invalid query syntax
- Network communication errors

The `PrettyJsonComponent` integrates with this system by highlighting syntax errors directly in the CodeMirror editor and displaying contextual error messages.

Sources: [app/src/app/components/pretty-json/pretty-json.component.ts:110-118](), [app/src/app/services/json-parser.service.ts:16-18](), [app/src/app/services/services.module.ts:15]()

---

# Page: Key Components

# Key Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/app/app.component.scss](app/src/app/app.component.scss)
- [app/src/app/components/panel/panel.component.scss](app/src/app/components/panel/panel.component.scss)
- [app/src/app/components/pretty-json/pretty-json.component.html](app/src/app/components/pretty-json/pretty-json.component.html)
- [app/src/app/components/pretty-json/pretty-json.component.ts](app/src/app/components/pretty-json/pretty-json.component.ts)
- [app/src/app/components/search-box/search-box.component.html](app/src/app/components/search-box/search-box.component.html)
- [app/src/app/components/search-box/search-box.component.ts](app/src/app/components/search-box/search-box.component.ts)
- [app/src/app/pages/document/document.component.html](app/src/app/pages/document/document.component.html)

</details>



This page documents the core user interface components that make up Mongoku's frontend experience. These components handle data visualization, user input, and layout structure within the Angular single-page application.

For information about the overall frontend architecture and routing, see [Frontend Application](#3.2). For details on theming and visual customization, see [Theming and Styling](#5.2).

## Overview

Mongoku's user interface is built around three primary component types that work together to provide a comprehensive MongoDB data exploration experience:

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `SearchBoxComponent` | Query interface for MongoDB operations | Parameter management, dynamic UI, search execution |
| `PrettyJsonComponent` | JSON data visualization and editing | Syntax highlighting, collapsible view, inline editing |
| `PanelComponent` | Layout container for content sections | Consistent styling, title/body structure |

## SearchBoxComponent Architecture

### Component Structure Diagram
```mermaid
graph TB
    SearchBoxComponent["SearchBoxComponent"]
    SearchParams["SearchParams Interface"]
    DropdownMenu["ngbDropdown Menu"]
    ParamsGroup["params-group"]
    
    SearchBoxComponent --> SearchParams
    SearchBoxComponent --> DropdownMenu
    SearchBoxComponent --> ParamsGroup
    
    SearchParams --> query["query: string"]
    SearchParams --> sort["sort: string"] 
    SearchParams --> project["project: string"]
    SearchParams --> limit["limit: number"]
    SearchParams --> skip["skip: number"]
    
    ParamsGroup --> QueryInput["Query Input"]
    ParamsGroup --> SortInput["Sort Input (conditional)"]
    ParamsGroup --> SkipInput["Skip Input (conditional)"]
    ParamsGroup --> LimitInput["Limit Input (conditional)"]
    ParamsGroup --> ProjectInput["Project Input (conditional)"]
    
    DropdownMenu --> AddSort["Add Sort Option"]
    DropdownMenu --> AddSkip["Add Skip Option"] 
    DropdownMenu --> AddLimit["Add Limit Option"]
    DropdownMenu --> AddProject["Add Project Option"]
```

The `SearchBoxComponent` manages MongoDB query parameters through a structured interface. The component implements the `SearchParams` interface which defines five core parameters for database operations.

**Sources:** [app/src/app/components/search-box/search-box.component.ts:1-84](), [app/src/app/components/search-box/search-box.component.html:1-44]()

### Parameter Management System

The component uses a `defaults` object to manage parameter state and a `show` object to control UI visibility:

```typescript
private defaults = {
  query:   "{}",
  project: "{}",
  limit:   20,
  skip:    0,
  sort:    ""
};
```

The `toggle()` method at [app/src/app/components/search-box/search-box.component.ts:58-64]() controls parameter visibility and resets values to defaults when parameters are hidden. The `canAddParams()` method determines when the add parameter button should be displayed.

**Sources:** [app/src/app/components/search-box/search-box.component.ts:21-33](), [app/src/app/components/search-box/search-box.component.ts:58-68]()

## PrettyJsonComponent Architecture

### Component Data Flow Diagram
```mermaid
graph TB
    PrettyJsonComponent["PrettyJsonComponent"]
    JsonParserService["JsonParserService"]
    NotificationsService["NotificationsService"]
    CodeMirror["CodeMirror Editor"]
    
    Input["json: any"]
    AutoCollapse["autoCollapse: boolean"]
    ReadOnly["readOnly: boolean"]
    
    GoEvent["go EventEmitter"]
    EditEvent["edit EventEmitter"] 
    RemoveEvent["remove EventEmitter"]
    
    Input --> PrettyJsonComponent
    AutoCollapse --> PrettyJsonComponent
    ReadOnly --> PrettyJsonComponent
    
    PrettyJsonComponent --> JsonParserService
    PrettyJsonComponent --> NotificationsService
    PrettyJsonComponent --> CodeMirror
    
    PrettyJsonComponent --> GoEvent
    PrettyJsonComponent --> EditEvent
    PrettyJsonComponent --> RemoveEvent
    
    CreateView["createView() method"]
    CollapseLogic["collapse() method"]
    EditorLogic["Editor Management"]
    
    PrettyJsonComponent --> CreateView
    PrettyJsonComponent --> CollapseLogic
    PrettyJsonComponent --> EditorLogic
```

The `PrettyJsonComponent` is the most complex UI component, handling JSON visualization with MongoDB-specific type support. It processes input data through the `createView()` method and provides interactive editing capabilities.

**Sources:** [app/src/app/components/pretty-json/pretty-json.component.ts:1-383](), [app/src/app/components/pretty-json/pretty-json.component.html:1-36]()

### JSON Rendering System

The component implements a sophisticated JSON rendering system that handles MongoDB-specific data types:

| Data Type | Rendering Method | Special Handling |
|-----------|------------------|------------------|
| `ObjectId` | `fnCall()` method | Displays as `ObjectId("value")` |
| `Date` | `fnCall()` method | Displays as `Date("value")` |
| `RegExp` | Inline formatting | Displays as `/pattern/flags` |
| Arrays | Collapsible structure | With `[...]` summary |
| Objects | Collapsible structure | With `{...}` summary |

The type detection logic is implemented in the `createView()` method at [app/src/app/components/pretty-json/pretty-json.component.ts:252-260]().

**Sources:** [app/src/app/components/pretty-json/pretty-json.component.ts:225-352](), [app/src/app/components/pretty-json/pretty-json.component.ts:252-260]()

### Editing and Persistence

The component provides inline editing through CodeMirror integration with the following workflow:

```mermaid
sequenceDiagram
    participant User
    participant PrettyJsonComponent
    participant CodeMirrorEditor
    participant JsonParserService
    participant NotificationsService
    
    User->>PrettyJsonComponent: enableEditor()
    PrettyJsonComponent->>CodeMirrorEditor: Initialize with current JSON
    User->>CodeMirrorEditor: Edit JSON content
    User->>PrettyJsonComponent: save() or Ctrl+Enter
    PrettyJsonComponent->>JsonParserService: parse(editJson)
    alt Valid JSON
        JsonParserService-->>PrettyJsonComponent: Parsed object
        PrettyJsonComponent->>PrettyJsonComponent: emit edit event
    else Invalid JSON
        JsonParserService-->>PrettyJsonComponent: Parse error
        PrettyJsonComponent->>NotificationsService: notifyError()
        PrettyJsonComponent->>CodeMirrorEditor: Highlight error line
    end
```

The editor configuration is defined in `editorOptions` at [app/src/app/components/pretty-json/pretty-json.component.ts:50-59]() and includes keyboard shortcuts for saving.

**Sources:** [app/src/app/components/pretty-json/pretty-json.component.ts:82-131](), [app/src/app/components/pretty-json/pretty-json.component.ts:50-59]()

## PanelComponent Structure

The `PanelComponent` serves as a consistent layout container with styling support for titles and body content. It implements a simple structure with CSS custom properties for theming:

```mermaid
graph TB
    PanelComponent["PanelComponent"]
    PanelTitle["panel-title"]
    PanelBody["panel-body"]
    
    PanelComponent --> PanelTitle
    PanelComponent --> PanelBody
    
    PanelTitle --> TitleText["Title Content"]
    PanelBody --> BodyContent["Body Content"]
    
    CSSVars["CSS Custom Properties"]
    CSSVars --> PanelTitleBG["--panel-title"]
    CSSVars --> PanelBodyBG["--panel-body"] 
    CSSVars --> TextColor["--text"]
    CSSVars --> BorderColor["--color-3"]
```

The panel styling uses CSS custom properties for theme integration and supports optional border removal through the `border=false` attribute.

**Sources:** [app/src/app/components/panel/panel.component.scss:1-37]()

## Component Integration Patterns

### Document Display Integration
The components work together in document display scenarios as shown in the document component template:

```mermaid
graph LR
    DocumentComponent["DocumentComponent"]
    PrettyJsonComponent["PrettyJsonComponent"]
    PanelComponent["PanelComponent"]
    
    DocumentComponent --> PrettyJsonComponent
    PrettyJsonComponent --> PanelComponent
    
    DocumentComponent --> EditHandler["editDocument()"]
    DocumentComponent --> RemoveHandler["remove()"]
    
    PrettyJsonComponent --> EditEvent["edit event"]
    PrettyJsonComponent --> RemoveEvent["remove event"]
    
    EditEvent --> EditHandler
    RemoveEvent --> RemoveHandler
```

The document component at [app/src/app/pages/document/document.component.html:3-9]() demonstrates the integration pattern where `PrettyJsonComponent` is wrapped within the document page logic.

**Sources:** [app/src/app/pages/document/document.component.html:1-12]()

### Explore Page Integration
In the explore interface, `SearchBoxComponent` and `PrettyJsonComponent` work together to provide query and display functionality, with the search component controlling the data that feeds into the JSON display components.

The integration follows a pattern where search parameters from `SearchBoxComponent` are used to fetch data that is then displayed using multiple `PrettyJsonComponent` instances for result sets.

**Sources:** [app/src/app/components/search-box/search-box.component.ts:70-76](), [app/src/app/components/pretty-json/pretty-json.component.ts:36-42]()

---

# Page: Theming and Styling

# Theming and Styling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/app/components/pretty-json/pretty-json.component.scss](app/src/app/components/pretty-json/pretty-json.component.scss)
- [app/src/app/components/search-box/search-box.component.scss](app/src/app/components/search-box/search-box.component.scss)
- [app/src/app/pages/explore/explore.component.scss](app/src/app/pages/explore/explore.component.scss)
- [app/src/app/services/json-parser.service.ts](app/src/app/services/json-parser.service.ts)
- [app/src/app/services/services.module.ts](app/src/app/services/services.module.ts)
- [app/src/sass/themes/dark-default.scss](app/src/sass/themes/dark-default.scss)
- [app/src/sass/themes/light.scss](app/src/sass/themes/light.scss)
- [app/src/styles.scss](app/src/styles.scss)

</details>



This document covers Mongoku's visual theming system and styling architecture. It explains how themes are implemented using CSS custom properties, how the color schemes are organized, and how component-specific styling integrates with the global theme system.

For information about specific UI components and their functionality, see [Key Components](#5.1).

## Theme System Architecture

Mongoku implements a flexible theming system based on CSS custom properties (CSS variables) that allows for easy switching between light and dark themes. The system uses SCSS for preprocessing and Bootstrap as the foundation framework.

### Theme File Structure

```mermaid
graph TD
    StylesRoot["styles.scss<br/>Main entry point"]
    
    subgraph "Theme Files"
        DarkTheme["sass/themes/dark-default.scss<br/>Default dark theme"]
        LightTheme["sass/themes/light.scss<br/>Light theme variant"]
        CodeMirrorTheme["sass/themes/codemirror<br/>Editor theme"]
    end
    
    subgraph "External Dependencies"
        Bootstrap["Bootstrap SCSS<br/>Base framework"]
        GoogleFonts["Google Fonts<br/>Cuprum & Rajdhani"]
        CodeMirrorCSS["CodeMirror CSS<br/>Editor styles"]
    end
    
    subgraph "Component Styles"
        PrettyJSON["pretty-json.component.scss<br/>JSON viewer styling"]
        SearchBox["search-box.component.scss<br/>Search interface styling"]
        Explore["explore.component.scss<br/>Explore page styling"]
    end
    
    StylesRoot --> Bootstrap
    StylesRoot --> DarkTheme
    StylesRoot --> LightTheme
    StylesRoot --> GoogleFonts
    StylesRoot --> CodeMirrorCSS
    StylesRoot --> CodeMirrorTheme
    
    DarkTheme --> PrettyJSON
    DarkTheme --> SearchBox
    DarkTheme --> Explore
    
    LightTheme --> PrettyJSON
    LightTheme --> SearchBox
    LightTheme --> Explore
```

Sources: [app/src/styles.scss:1-15](), [app/src/sass/themes/dark-default.scss:1-34](), [app/src/sass/themes/light.scss:1-34]()

## CSS Custom Properties System

The theming system relies heavily on CSS custom properties to create a consistent color palette and styling approach across all components.

### Color Palette Structure

Both themes define a structured color palette using a four-tier system:

| Variable | Purpose | Dark Theme Value | Light Theme Value |
|----------|---------|------------------|-------------------|
| `--color-1` | Primary background | `hsl(216, 26%, 15%)` | `hsl(228, 26%, 98%)` |
| `--color-2` | Secondary background | `hsl(220, 23%, 21%)` | `hsl(232, 23%, 93%)` |
| `--color-3` | Border/separator color | `hsl(217, 20%, 25%)` | `hsl(229, 20%, 88%)` |
| `--color-4` | Input/control color | `hsl(220, 20%, 30%)` | `hsl(232, 20%, 83%)` |

### Text and UI Variables

```mermaid
graph LR
    subgraph "Text Variables"
        TextPrimary["--text<br/>Primary text color"]
        TextInverse["--text-inverse<br/>Opposite contrast text"]
        TextDarker["--text-darker<br/>Muted text"]
        TextLighter["--text-lighter<br/>Bright white text"]
    end
    
    subgraph "UI Elements"
        BackgroundColor["--background-color<br/>Body background"]
        PanelTitle["--panel-title<br/>Panel header background"]
        PanelBody["--panel-body<br/>Panel content background"]
        ErrorColor["--error<br/>Error message color"]
    end
    
    subgraph "Button Variables"
        ButtonDanger["--button-danger<br/>Danger button color"]
        ButtonSuccess["--button-success<br/>Success button color"]
        ButtonLight["--button-light<br/>Light button color"]
    end
    
    subgraph "Code Syntax"
        CodeNamespace["--code-namespace"]
        CodeBoolean["--code-boolean"]
        CodeNumbers["--code-numbers"]
        CodeString["--code-string"]
        CodeFunction["--code-function"]
    end
```

Sources: [app/src/sass/themes/dark-default.scss:1-34](), [app/src/sass/themes/light.scss:1-34]()

## Theme Implementation

### Dark Theme (Default)

The dark theme is defined in `:root` and serves as the default theme for the application. It uses a blue-tinted dark color scheme with high contrast text.

Key characteristics:
- Base color: `hsl(216, 26%, 15%)` - dark blue-gray
- Text color: `hsl(0, 0%, 88%)` - light gray
- Syntax highlighting optimized for dark backgrounds
- VS Code-inspired color palette for code elements

### Light Theme

The light theme uses the `.theme-light` class selector and provides a clean, bright alternative with inverted colors from the dark theme.

Key characteristics:
- Base color: `hsl(228, 26%, 98%)` - very light blue-gray
- Text color: `hsl(0, 0%, 12%)` - dark gray
- Syntax highlighting optimized for light backgrounds
- Traditional light theme color palette

Sources: [app/src/sass/themes/dark-default.scss:1-34](), [app/src/sass/themes/light.scss:1-34]()

## Component-Specific Styling

### PrettyJSON Component Styling

The `PrettyJSONComponent` includes extensive styling for JSON syntax highlighting and interactive features:

```mermaid
graph TD
    PrettyJSONRoot["pretty-json.component.scss"]
    
    subgraph "Visual Elements"
        ObjectInfo["object-info<br/>Document metadata display"]
        EditorLayer["editor<br/>Inline editing overlay"]
        RemoveLayer["remove-layer<br/>Delete confirmation overlay"]
    end
    
    subgraph "Syntax Highlighting"
        NullStyle[".null<br/>var(--code-null)"]
        BooleanStyle[".boolean<br/>var(--code-boolean)"]
        NumberStyle[".number<br/>var(--code-numbers)"]
        StringStyle[".quoted<br/>var(--code-string)"]
        RegexpStyle[".regexp<br/>var(--code-regexp)"]
        FunctionStyle[".function<br/>var(--code-function)"]
    end
    
    subgraph "Interactive Features"
        Collapser[".collapser<br/>Expand/collapse controls"]
        EditorActions[".editor-actions<br/>Save/cancel buttons"]
        HoverActions[":host:hover .actions<br/>Show on hover"]
    end
    
    PrettyJSONRoot --> ObjectInfo
    PrettyJSONRoot --> EditorLayer
    PrettyJSONRoot --> RemoveLayer
    PrettyJSONRoot --> NullStyle
    PrettyJSONRoot --> BooleanStyle
    PrettyJSONRoot --> NumberStyle
    PrettyJSONRoot --> StringStyle
    PrettyJSONRoot --> RegexpStyle
    PrettyJSONRoot --> FunctionStyle
    PrettyJSONRoot --> Collapser
    PrettyJSONRoot --> EditorActions
    PrettyJSONRoot --> HoverActions
```

Sources: [app/src/app/components/pretty-json/pretty-json.component.scss:1-227]()

### Search Box Styling

The search box component implements a complex flexbox layout with multiple input groups and custom styling:

Key styling features:
- `.search-box` - Main container with flexbox layout
- `.params-group` - Contains multiple parameter input groups
- `.input-group` - Individual query parameter sections
- `.label` - Parameter name displays
- `.add-param` and `.confirm-search` - Action buttons

Sources: [app/src/app/components/search-box/search-box.component.scss:1-106]()

## Global Style Overrides

The main `styles.scss` file contains global overrides for Bootstrap and third-party components:

### Bootstrap Overrides

| Component | Customization | CSS Variables Used |
|-----------|---------------|-------------------|
| `.navbar` | Border color | `var(--color-3)` |
| `.bg-dark` | Background color | `var(--color-2)` |
| `.table` | Border colors | `var(--color-3)` |
| `.btn.btn-default` | Theme-aware buttons | `var(--color-1)`, `var(--text)` |
| `.modal-content` | Modal appearance | `var(--color-2)`, `var(--color-3)` |

### Typography

- Primary font: `'Rajdhani', sans-serif` for UI text
- Code font: `'Source Code Pro', monospace` for code elements
- Imported from Google Fonts: Cuprum and Rajdhani

Sources: [app/src/styles.scss:17-156]()

## Theme Integration Points

### Service Integration

The theming system integrates with Angular services, particularly for error handling and notifications:

```mermaid
graph LR
    subgraph "Angular Services"
        JsonParserService["JsonParserService<br/>Handles JSON parsing"]
        NotificationsService["NotificationsService<br/>User feedback"]
    end
    
    subgraph "Theme Variables"
        ErrorVar["--error<br/>Error message color"]
        TextVar["--text<br/>Primary text color"]
        ButtonVars["--button-danger<br/>--button-success<br/>Button colors"]
    end
    
    subgraph "UI Components"
        PrettyJSON["PrettyJSONComponent<br/>Uses syntax colors"]
        SearchBox["SearchBoxComponent<br/>Uses input styling"]
        Notifications["Notification display<br/>Uses error colors"]
    end
    
    JsonParserService --> PrettyJSON
    NotificationsService --> Notifications
    PrettyJSON --> TextVar
    SearchBox --> ButtonVars
    Notifications --> ErrorVar
```

Sources: [app/src/app/services/json-parser.service.ts:1-141](), [app/src/app/services/services.module.ts:1-18]()

## Customization Guidelines

### Adding New Themes

To add a new theme:

1. Create a new SCSS file in `app/src/sass/themes/`
2. Define all required CSS custom properties
3. Import the theme in `app/src/styles.scss`
4. Use a class-based selector (e.g., `.theme-custom`)

### Extending Component Styles

Component styles should:
- Use CSS custom properties for colors and spacing
- Follow the established naming conventions
- Maintain compatibility with both light and dark themes
- Use the Source Code Pro font for code-related elements

Sources: [app/src/styles.scss:1-156](), [app/src/sass/themes/dark-default.scss:1-34](), [app/src/sass/themes/light.scss:1-34]()

---

# Page: Deployment and Configuration

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

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [lib/JsonEncoder.ts](lib/JsonEncoder.ts)

</details>



This document covers Docker-based deployment of Mongoku, including using pre-built images from Docker Hub and building custom Docker images. It explains the Docker configuration options, environment variables, and container management for production deployment.

For general installation methods including npm and manual builds, see [Getting Started](#2). For detailed environment configuration reference, see [Environment Configuration](#6.2).

## Docker Deployment Options

Mongoku provides two primary Docker deployment approaches: using the official Docker Hub image or building a custom image from source. Both methods provide identical functionality but offer different levels of customization and control.

### Using Docker Hub Image

The simplest deployment method uses the pre-built image `huggingface/mongoku` from Docker Hub:

```bash
docker run -d --name mongoku -p 3100:3100 huggingface/mongoku
```

This image includes the complete Mongoku application with default configuration. The container exposes port 3100 and connects to `mongodb://localhost:27017` by default.

### Custom Image Build

For environments requiring customization or specific build configurations, build a custom image from the repository:

```bash
docker build -t yournamehere/mongoku .
docker run -d --name mongoku -p 3100:3100 yournamehere/mongoku
```

Sources: [README.md:34-55](), [Dockerfile:1-30]()

## Docker Configuration Architecture

```mermaid
graph TB
    subgraph "Docker Container"
        NodeRuntime["Node.js 18 Runtime"]
        MongokuApp["Mongoku Application<br/>dist/server.js"]
        AngularBuild["Angular Production Build<br/>app/dist/"]
        ConfigFile["Configuration Storage<br/>/tmp/mongoku.db"]
    end
    
    subgraph "Environment Variables"
        DefaultHost["MONGOKU_DEFAULT_HOST"]
        ServerPort["MONGOKU_SERVER_PORT"]
        DatabaseFile["MONGOKU_DATABASE_FILE"]
        CountTimeout["MONGOKU_COUNT_TIMEOUT"]
        ReadOnlyMode["MONGOKU_READ_ONLY_MODE"]
    end
    
    subgraph "External Systems"
        HostNetwork["Host Network<br/>Port 3100"]
        MongoDBServers["Target MongoDB<br/>Instances"]
        HostVolumes["Optional Volume Mounts<br/>Persistent Config"]
    end
    
    DefaultHost --> MongokuApp
    ServerPort --> MongokuApp
    DatabaseFile --> ConfigFile
    CountTimeout --> MongokuApp
    ReadOnlyMode --> MongokuApp
    
    MongokuApp --> AngularBuild
    MongokuApp --> MongoDBServers
    ConfigFile --> HostVolumes
    
    NodeRuntime --> MongokuApp
    HostNetwork --> MongokuApp
```

Sources: [Dockerfile:3-11](), [README.md:81-97]()

## Environment Variable Configuration

The Docker container supports configuration through environment variables that control server behavior and MongoDB connections:

| Variable | Default Value | Purpose |
|----------|---------------|---------|
| `MONGOKU_DEFAULT_HOST` | `mongodb://localhost:27017` | MongoDB connection string(s) |
| `MONGOKU_SERVER_PORT` | `3100` | HTTP server port |
| `MONGOKU_DATABASE_FILE` | `/tmp/mongoku.db` | Host configuration storage |
| `MONGOKU_COUNT_TIMEOUT` | `5000` | Document count timeout (ms) |
| `MONGOKU_READ_ONLY_MODE` | `false` | Enable read-only mode |

### Example with Custom Configuration

```bash
docker run -d --name mongoku -p 8080:8080 \
  --env MONGOKU_DEFAULT_HOST="mongodb://user:password@myhost.com:27017" \
  --env MONGOKU_SERVER_PORT=8080 \
  --env MONGOKU_READ_ONLY_MODE=true \
  huggingface/mongoku
```

Sources: [README.md:41-42](), [Dockerfile:5-10]()

## Docker Build Process

```mermaid
graph LR
    subgraph "Build Context"
        SourceCode["Source Files"]
        PackageJSON["package.json"]
        AngularApp["app/ Directory"]
        TypeScriptCode["lib/ Directory"]
        DockerFile["Dockerfile"]
        DockerIgnore[".dockerignore"]
    end
    
    subgraph "Build Steps"
        NodeBase["FROM node:18"]
        InstallTools["npm install -g<br/>typescript @angular/cli"]
        InstallDeps["npm ci"]
        AngularBuild["ng build --configuration production"]
        TypeScriptCompile["tsc"]
    end
    
    subgraph "Runtime Image"
        FinalImage["Built Image"]
        DistServer["dist/server.js"]
        AngularDist["app/dist/"]
        NodeModules["node_modules/"]
    end
    
    SourceCode --> NodeBase
    DockerFile --> NodeBase
    DockerIgnore --> NodeBase
    
    NodeBase --> InstallTools
    InstallTools --> InstallDeps
    PackageJSON --> InstallDeps
    InstallDeps --> AngularBuild
    AngularApp --> AngularBuild
    AngularBuild --> TypeScriptCompile
    TypeScriptCode --> TypeScriptCompile
    
    TypeScriptCompile --> FinalImage
    FinalImage --> DistServer
    FinalImage --> AngularDist
    FinalImage --> NodeModules
```

The Docker build process executes these steps in sequence:

1. **Base Image Setup**: Uses `node:18` as the foundation
2. **Tool Installation**: Installs TypeScript and Angular CLI globally
3. **Dependency Installation**: Runs `npm ci` for reproducible builds
4. **Frontend Build**: Compiles Angular application with production configuration
5. **Backend Compilation**: Compiles TypeScript server code to JavaScript
6. **Runtime Configuration**: Sets up environment and exposes port 3100

Sources: [Dockerfile:17-23](), [.dockerignore:1-4]()

## Container Lifecycle Management

### Starting and Stopping

```bash
# Start container
docker run -d --name mongoku -p 3100:3100 huggingface/mongoku

# Stop container
docker stop mongoku

# Restart container
docker restart mongoku

# View logs
docker logs mongoku
```

### Persistent Configuration

For persistent host configuration across container restarts, mount a volume for the database file:

```bash
docker run -d --name mongoku -p 3100:3100 \
  --env MONGOKU_DATABASE_FILE="/data/mongoku.db" \
  -v /host/path:/data \
  huggingface/mongoku
```

### Health Monitoring

Monitor container health by checking the HTTP endpoint:

```bash
# Check if service is responding
curl http://localhost:3100

# Container process status
docker exec mongoku ps aux
```

Sources: [Dockerfile:25-29](), [README.md:38-55]()

## Production Deployment Considerations

### Resource Requirements

The Docker container typically requires:
- **Memory**: 256MB minimum, 512MB recommended
- **CPU**: 0.5 vCPU minimum for small workloads
- **Storage**: 100MB for application, additional space for configuration

### Security Configuration

Enable read-only mode for production environments where data modification should be restricted:

```bash
docker run -d --name mongoku -p 3100:3100 \
  --env MONGOKU_READ_ONLY_MODE=true \
  huggingface/mongoku
```

### Network Configuration

For production deployments, consider:
- Using reverse proxy (nginx, Apache) for SSL termination
- Restricting container network access to required MongoDB instances
- Implementing container-to-container networking for isolated environments

Sources: [Dockerfile:9-10](), [README.md:95-96]()

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [README.md](README.md)
- [cli.ts](cli.ts)
- [server.ts](server.ts)

</details>



This document provides a comprehensive reference for configuring Mongoku through environment variables and runtime settings. Environment configuration allows operators to customize Mongoku's behavior without modifying source code, making it suitable for various deployment scenarios from local development to production environments.

For deployment-specific configuration including Docker setup, see [Docker Deployment](#6.1). For general deployment approaches, see [Deployment and Configuration](#6).

## Environment Variables Reference

Mongoku supports several environment variables that control its runtime behavior. All environment variables are prefixed with `MONGOKU_` for namespace isolation.

| Variable | Purpose | Default Value | Type | Example |
|----------|---------|---------------|------|---------|
| `MONGOKU_DEFAULT_HOST` | Default MongoDB connection strings | `localhost:27017` | String | `mongodb://user:pass@host:27017` |
| `MONGOKU_SERVER_PORT` | HTTP server port | `3100` | Integer | `8000` |
| `MONGOKU_DATABASE_FILE` | Path to hosts configuration storage | `$HOME/.mongoku.db` | Path | `/tmp/mongoku.db` |
| `MONGOKU_COUNT_TIMEOUT` | Document count timeout in milliseconds | `5000` | Integer | `1000` |
| `MONGOKU_READ_ONLY_MODE` | Enable read-only mode | `false` | Boolean | `true` |

Sources: [README.md:79-97]()

## Configuration Loading Architecture

The following diagram shows how environment variables flow through the Mongoku application during startup and runtime:

```mermaid
graph TD
    subgraph "Environment Sources"
        EnvVars["Environment Variables<br/>MONGOKU_*"]
        ProcessEnv["process.env"]
        DefaultValues["Default Values<br/>Hardcoded Fallbacks"]
    end
    
    subgraph "Application Entry Points"
        CLIStart["cli.ts<br/>Command Line Interface"]
        ServerStart["server.ts<br/>Direct Server Start"]
        DockerEntry["Docker Container<br/>Environment Injection"]
    end
    
    subgraph "Configuration Processing"
        ServerSetup["setupServer()<br/>server.ts:10"]
        FactoryLoad["factory.load()<br/>Dependency Injection"]
        PortBinding["SERVER_PORT<br/>process.env.MONGOKU_SERVER_PORT"]
    end
    
    subgraph "Runtime Application"
        ExpressServer["Express Application<br/>app.listen()"]
        HostsManager["HostsManager<br/>Configuration Persistence"]
        APILayer["API Routes<br/>/api endpoints"]
    end
    
    EnvVars --> ProcessEnv
    ProcessEnv --> CLIStart
    ProcessEnv --> ServerStart
    ProcessEnv --> DockerEntry
    
    CLIStart --> ServerSetup
    ServerStart --> ServerSetup
    DockerEntry --> ServerSetup
    
    ServerSetup --> FactoryLoad
    ServerSetup --> PortBinding
    DefaultValues --> PortBinding
    
    FactoryLoad --> HostsManager
    PortBinding --> ExpressServer
    ServerSetup --> APILayer
```

Sources: [server.ts:10-12](), [cli.ts:21-65](), [README.md:79-97]()

## Configuration Variable Details

### MONGOKU_DEFAULT_HOST

Controls the default MongoDB connection strings available when Mongoku starts. Supports multiple connection strings separated by semicolons.

**Format Options:**
- Simple: `localhost:27017`
- Authenticated: `mongodb://username:password@host:port`
- Multiple hosts: `host1:27017;host2:27017`
- Full URI: `mongodb://user:pass@cluster.mongodb.net/database`

**Usage in Code:**
The default host configuration is processed during application initialization and stored in the hosts configuration system.

```bash
# Single host
MONGOKU_DEFAULT_HOST="localhost:27017"

# Authenticated connection
MONGOKU_DEFAULT_HOST="mongodb://admin:password@production-mongo:27017"

# Multiple hosts
MONGOKU_DEFAULT_HOST="mongodb://user:pass@primary:27017;mongodb://user:pass@secondary:27017"
```

### MONGOKU_SERVER_PORT

Defines the HTTP port where the Express server listens for incoming connections. This affects both the web interface and API endpoints.

**Code Integration:**
The port configuration is read in [server.ts:11]() and used in [server.ts:49]() for the Express server binding.

```bash
# Custom port
MONGOKU_SERVER_PORT=8080

# Standard HTTP port
MONGOKU_SERVER_PORT=80
```

### MONGOKU_DATABASE_FILE

Specifies the file system path where Mongoku stores its internal configuration, including saved MongoDB host connections. Uses NeDB for local storage.

```bash
# Custom location
MONGOKU_DATABASE_FILE="/opt/mongoku/config/hosts.db"

# Temporary storage
MONGOKU_DATABASE_FILE="/tmp/mongoku-config.db"
```

### MONGOKU_COUNT_TIMEOUT

Sets the timeout threshold for MongoDB collection document counting operations. When counting takes longer than this value, Mongoku falls back to estimated counts for better performance.

```bash
# Fast timeout for large collections
MONGOKU_COUNT_TIMEOUT=1000

# Extended timeout for accuracy
MONGOKU_COUNT_TIMEOUT=10000
```

### MONGOKU_READ_ONLY_MODE

Enables read-only mode, preventing any write operations to MongoDB through the Mongoku interface. Critical for production environments where data modification should be restricted.

```bash
# Enable read-only mode
MONGOKU_READ_ONLY_MODE=true

# Disable read-only mode (default)
MONGOKU_READ_ONLY_MODE=false
```

Sources: [README.md:82-96]()

## Configuration Processing Flow

The following diagram illustrates how configuration variables are processed and applied throughout the application lifecycle:

```mermaid
sequenceDiagram
    participant Env as "Environment"
    participant CLI as "cli.ts"
    participant Server as "server.ts"
    participant Factory as "Factory"
    participant Express as "Express App"
    participant Hosts as "HostsManager"
    
    Env->>CLI: "Environment variables available"
    CLI->>Server: "start() function call"
    Server->>Factory: "factory.load()"
    Factory->>Hosts: "Initialize with MONGOKU_DATABASE_FILE"
    Hosts->>Hosts: "Load host configurations"
    Server->>Server: "Read MONGOKU_SERVER_PORT"
    Server->>Express: "app.listen(SERVER_PORT)"
    Express->>Express: "Bind to configured port"
    
    Note over Factory,Hosts: "MONGOKU_DEFAULT_HOST processed"
    Note over Server,Express: "MONGOKU_READ_ONLY_MODE applied"
    Note over Hosts: "MONGOKU_COUNT_TIMEOUT stored"
```

Sources: [server.ts:52-61](), [cli.ts:64]()

## Deployment Integration Examples

### Docker Environment Configuration

When using Docker, environment variables can be passed through multiple mechanisms:

```bash
# Docker run with environment variables
docker run -d \
  --name mongoku \
  -p 3100:3100 \
  --env MONGOKU_DEFAULT_HOST="mongodb://user:password@mongo-cluster:27017" \
  --env MONGOKU_READ_ONLY_MODE=true \
  huggingface/mongoku
```

### Process Manager Configuration

For PM2 and Forever daemon modes, environment variables are inherited from the parent shell:

```bash
# Set environment before starting with PM2
export MONGOKU_SERVER_PORT=8080
mongoku start --pm2

# Set environment before starting with Forever
export MONGOKU_READ_ONLY_MODE=true
mongoku start --forever
```

### Production Configuration Template

A typical production environment configuration:

```bash
# Production MongoDB cluster
MONGOKU_DEFAULT_HOST="mongodb://mongoku-user:secure-password@prod-cluster.company.com:27017/admin"

# Non-standard port for security
MONGOKU_SERVER_PORT=8443

# Persistent configuration storage
MONGOKU_DATABASE_FILE="/opt/mongoku/data/hosts.db"

# Fast timeouts for large collections
MONGOKU_COUNT_TIMEOUT=2000

# Read-only for safety
MONGOKU_READ_ONLY_MODE=true
```

Sources: [README.md:38-43](), [cli.ts:38-48](), [cli.ts:51-60]()

## Configuration Validation and Error Handling

Mongoku implements basic validation for configuration values:

- **Port validation**: Must be a valid integer port number
- **File path validation**: Directory must be writable for `MONGOKU_DATABASE_FILE`
- **Boolean validation**: `MONGOKU_READ_ONLY_MODE` accepts `true`/`false` strings
- **Timeout validation**: `MONGOKU_COUNT_TIMEOUT` must be a positive integer

Invalid configurations will cause application startup failure with error messages logged to the console.

Sources: [server.ts:52-61]()

---

# Page: Development Reference

# Development Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/package-lock.json](app/package-lock.json)
- [app/package.json](app/package.json)
- [package-lock.json](package-lock.json)

</details>



This document provides technical reference material for developers who want to understand, modify, or contribute to Mongoku. It covers the development technology stack, dependency architecture, build systems, and key code entities that comprise the application.

For deployment and configuration information, see [Deployment and Configuration](#6). For user-facing feature documentation, see [User Features](#4).

## Technology Stack Overview

Mongoku is built as a full-stack web application using a modern JavaScript/TypeScript technology stack with clear separation between frontend and backend concerns.

### Core Technologies Architecture

```mermaid
graph TB
    subgraph "Runtime Environment"
        NodeJS["Node.js Runtime"]
        V8["V8 JavaScript Engine"]
    end
    
    subgraph "Backend Stack"
        Express["express@4.17.2<br/>Web Server Framework"]
        MongoDB["mongodb@5.9.2<br/>Database Driver"]
        AWS["@aws-sdk/credential-providers@3.592.0<br/>Cloud Integration"]
        NeDB["nedb@1.8.0<br/>Local Config Storage"]
    end
    
    subgraph "Frontend Stack"
        Angular["@angular/core@13.4.0<br/>SPA Framework"]
        Bootstrap["bootstrap@4.1.3<br/>UI Framework"]
        CodeMirror["codemirror@5.65.0<br/>Code Editor"]
        RxJS["rxjs@7.5.1<br/>Reactive Programming"]
    end
    
    subgraph "Build System"
        AngularCLI["@angular/cli@13.3.11<br/>Frontend Build"]
        TypeScript["typescript@4.5.4<br/>Type System"]
        Webpack["webpack@5.76.1<br/>Module Bundler"]
        Sass["sass@1.49.9<br/>CSS Preprocessor"]
    end
    
    subgraph "Development Tools"
        TSNode["ts-node@10.4.0<br/>TypeScript Execution"]
        Jasmine["jasmine-core@4.0.0<br/>Testing Framework"]
        Karma["karma@6.3.10<br/>Test Runner"]
        TSLint["tslint@6.1.3<br/>Code Linting"]
    end
    
    NodeJS --> Express
    NodeJS --> Angular
    Express --> MongoDB
    Express --> AWS
    Express --> NeDB
    Angular --> Bootstrap
    Angular --> CodeMirror
    Angular --> RxJS
    
    AngularCLI --> Angular
    AngularCLI --> Webpack
    TypeScript --> Angular
    TypeScript --> Express
    Sass --> Bootstrap
    
    TSNode --> TypeScript
    Jasmine --> Karma
    TSLint --> TypeScript
```

Sources: [package.json:11-21](), [app/package.json:14-34](), [app/package.json:35-54]()

## Dependency Architecture

The application dependencies are organized into distinct categories based on their function within the development and runtime environments.

### Runtime Dependencies Structure

```mermaid
graph LR
    subgraph "Core Server Dependencies"
        express["express"]
        bodyparser["body-parser"]
        mongodb["mongodb"]
        nedb["nedb"]
    end
    
    subgraph "AWS Integration"
        awssdk["@aws-sdk/credential-providers"]
        aws4["aws4"]
    end
    
    subgraph "CLI Framework"
        commander["commander"]
        figlet["figlet"]
        chalk["chalk"]
    end
    
    subgraph "Angular Runtime"
        angularcore["@angular/core"]
        angularcommon["@angular/common"]
        angularrouter["@angular/router"]
        angularforms["@angular/forms"]
    end
    
    subgraph "UI Components"
        bootstrap["bootstrap"]
        ngbootstrap["@ng-bootstrap/ng-bootstrap"]
        codemirror["codemirror"]
        ngxcodemirror["@ctrl/ngx-codemirror"]
    end
    
    subgraph "Utility Libraries"
        rxjs["rxjs"]
        corejs["core-js"]
        esprima["esprima"]
        zonejs["zone.js"]
    end
    
    express --> bodyparser
    express --> mongodb
    express --> nedb
    express --> awssdk
    express --> aws4
    express --> commander
    
    angularcore --> angularcommon
    angularcore --> angularrouter
    angularcore --> angularforms
    angularcore --> bootstrap
    angularcore --> rxjs
    
    bootstrap --> ngbootstrap
    codemirror --> ngxcodemirror
    angularcore --> corejs
    angularcore --> zonejs
```

Sources: [package.json:11-21](), [app/package.json:14-34]()

## Build System Architecture

Mongoku uses a dual-build system approach with separate build processes for the backend Node.js application and the frontend Angular application.

### Build Process Flow

| Component | Build Tool | Input | Output | Configuration |
|-----------|------------|--------|--------|---------------|
| **Backend** | `tsc` (TypeScript Compiler) | `src/**/*.ts` | `dist/**/*.js` | `tsconfig.json` |
| **Frontend** | `@angular/cli` | `app/src/**/*.ts` | `app/dist/**/*.js` | `app/angular.json` |
| **Styles** | `sass-loader` | `app/src/**/*.scss` | CSS bundles | Webpack config |
| **Assets** | `copy-webpack-plugin` | Static files | `app/dist/assets/` | Angular build config |

### Development vs Production Builds

The build system supports different optimization levels:

**Development Mode:**
- Source maps enabled for debugging
- Hot module replacement for frontend
- Unminified code for easier debugging
- Development server with live reload

**Production Mode:**
- Code minification via `terser@5.14.2`
- Tree shaking for dead code elimination
- Asset optimization and compression
- Ahead-of-time (AOT) compilation for Angular

Sources: [app/package.json:35-54](), [package.json:25-30]()

## Key Development Dependencies

### Frontend Development Tools

The Angular application uses a comprehensive set of development tools:

```mermaid
graph TD
    subgraph "Angular Toolchain"
        AngularCLI["@angular/cli@13.3.11"]
        AngularDevkit["@angular-devkit/build-angular@13.3.11"]
        AngularCompiler["@angular/compiler-cli@13.4.0"]
    end
    
    subgraph "Testing Infrastructure"
        Jasmine["jasmine-core@4.0.0"]
        Karma["karma@6.3.10"]
        KarmaChrome["karma-chrome-launcher@3.1.0"]
        KarmaJasmine["karma-jasmine@4.0.1"]
        Protractor["protractor@7.0.0"]
    end
    
    subgraph "Code Quality"
        TSLint["tslint@6.1.3"]
        Codelyzer["codelyzer@6.0.2"]
        TypeScript["typescript@4.5.4"]
    end
    
    subgraph "Build Pipeline"
        TSNode["ts-node@10.4.0"]
        Webpack["webpack@5.76.1"]
        SassLoader["sass-loader@12.4.0"]
        CSSLoader["css-loader@6.5.1"]
    end
    
    AngularCLI --> AngularDevkit
    AngularDevkit --> AngularCompiler
    AngularDevkit --> Webpack
    
    Karma --> Jasmine
    Karma --> KarmaChrome
    Karma --> KarmaJasmine
    
    TSLint --> TypeScript
    TSLint --> Codelyzer
    
    Webpack --> SassLoader
    Webpack --> CSSLoader
    TSNode --> TypeScript
```

Sources: [app/package.json:35-54]()

### Backend Development Dependencies

The backend uses TypeScript definitions and development utilities:

- `@types/express@4.17.13`: TypeScript definitions for Express.js
- `@types/figlet@1.5.4`: TypeScript definitions for ASCII art library
- `@types/mongodb@4.0.7`: TypeScript definitions for MongoDB driver  
- `@types/nedb@1.8.12`: TypeScript definitions for NeDB

Sources: [package.json:25-30]()

## Development Workflow

### Local Development Setup

1. **Backend Development**: TypeScript files in `/src` are compiled to `/dist` using the TypeScript compiler
2. **Frontend Development**: Angular application in `/app` uses Angular CLI development server with hot reload
3. **Concurrent Development**: Both backend and frontend can be developed simultaneously using separate terminal sessions

### Testing Strategy

| Test Type | Framework | Location | Purpose |
|-----------|-----------|----------|---------|
| **Unit Tests** | Jasmine + Karma | `app/src/**/*.spec.ts` | Component and service testing |
| **E2E Tests** | Protractor | `app/e2e/` | End-to-end user workflows |
| **Backend Tests** | Custom (if any) | `src/**/*.test.ts` | Server logic testing |

### Code Quality Tools

- **TSLint**: Enforces TypeScript coding standards
- **Codelyzer**: Angular-specific linting rules
- **TypeScript**: Static type checking for both frontend and backend

Sources: [app/package.json:5-12](), [app/package.json:40-53]()

## File Structure and Module Organization

### Backend Module Structure

The backend follows a modular architecture with these key areas:

- **Express Server**: Web server and routing logic
- **MongoDB Manager**: Database connection and operations management
- **Host Manager**: Configuration and connection string management  
- **API Layer**: REST endpoint definitions and request handling
- **CLI Interface**: Command-line interface and process management

### Frontend Module Structure  

The Angular application is organized into feature modules:

- **Core Module**: Shared services and singleton providers
- **Shared Module**: Reusable components and directives
- **Feature Modules**: Page-specific components and logic
- **Routing Module**: Navigation and route configuration

Sources: Based on system architecture diagrams and dependency analysis

This development reference provides the foundation for understanding Mongoku's technical architecture. For specific build instructions and environment setup, see [Build and Development Setup](#7.2). For dependency details and system requirements, see [Dependencies and Requirements](#7.1).

---

# Page: Dependencies and Requirements

# Dependencies and Requirements

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/package-lock.json](app/package-lock.json)
- [app/package.json](app/package.json)
- [package-lock.json](package-lock.json)
- [package.json](package.json)

</details>



This document provides a comprehensive breakdown of all dependencies, system requirements, and development prerequisites for Mongoku. It covers both the backend Node.js/Express server dependencies and the frontend Angular application dependencies, along with their specific purposes and version constraints.

For information about setting up a development environment and build processes, see [Build and Development Setup](#7.2). For deployment-specific configuration requirements, see [Environment Configuration](#6.2).

## System Requirements

Mongoku requires specific versions of Node.js and npm to function properly across both backend and frontend components.

### Runtime Requirements

| Component | Requirement | Source |
|-----------|-------------|---------|
| Node.js | ≥16.0.0 | Backend AWS SDK constraints |
| Node.js | ^12.20.0 \|\| ^14.15.0 \|\| ≥16.10.0 | Angular CLI constraints |
| npm | ^6.11.0 \|\| ^7.5.6 \|\| ≥8.0.0 | Angular tooling |

The most restrictive requirement comes from the AWS SDK dependencies, which require Node.js ≥16.0.0 for the latest security and compatibility features.

**Sources:** [package-lock.json:194-196](), [app/package-lock.json:76-80]()

## Backend Dependencies Architecture

The backend dependencies are organized into several functional categories that support different aspects of the MongoDB client functionality.

```mermaid
graph TD
    subgraph "Core Server Stack"
        express["express@^4.17.2"]
        bodyParser["body-parser@^1.19.1"]
        nedb["nedb@^1.8.0"]
    end
    
    subgraph "MongoDB Integration"
        mongodb["mongodb@^5.9.2"]
        aws4["aws4@^1.13.0"]
        awsCredentials["@aws-sdk/credential-providers@^3.592.0"]
    end
    
    subgraph "CLI Interface"
        commander["commander@^8.3.0"]
        figlet["figlet@^1.5.2"]
        chalk["chalk@^2.4.2"]
    end
    
    subgraph "Development Tools"
        typescript["@types/express@^4.17.13"]
        mongoTypes["@types/mongodb@^4.0.7"]
        nedbTypes["@types/nedb@^1.8.12"]
    end
    
    express --> bodyParser
    mongodb --> awsCredentials
    mongodb --> aws4
    commander --> chalk
    commander --> figlet
```

**Sources:** [package.json:16-26](), [package.json:27-32]()

### Core Backend Dependencies

#### Web Server Framework
- **`express@^4.17.2`** - Primary web application framework providing HTTP server functionality and middleware support for the API layer
- **`body-parser@^1.19.1`** - HTTP request body parsing middleware for handling JSON and form data in API endpoints

#### Database Connectivity
- **`mongodb@^5.9.2`** - Official MongoDB Node.js driver providing connection management and query execution capabilities
- **`nedb@^1.8.0`** - Embedded JavaScript database used for local configuration storage in `~/.mongoku.db`

#### AWS Integration
- **`@aws-sdk/credential-providers@^3.592.0`** - AWS SDK credential provider modules supporting various authentication methods for cloud MongoDB instances
- **`aws4@^1.13.0`** - AWS request signing utility for secure API communication with AWS-hosted MongoDB services

#### Command Line Interface
- **`commander@^8.3.0`** - Command-line interface framework powering the `mongoku` CLI commands
- **`figlet@^1.5.2`** - ASCII art text generator for CLI banner display
- **`chalk@^2.4.2`** - Terminal string styling library for colored CLI output

**Sources:** [package.json:16-26]()

## Frontend Dependencies Architecture

The Angular frontend has a comprehensive set of dependencies supporting modern web application development with rich UI components and development tooling.

```mermaid
graph TD
    subgraph "Angular Framework"
        angularCore["@angular/core@^13.1.1"]
        angularCommon["@angular/common@^13.1.1"]
        angularRouter["@angular/router@^13.1.1"]
        angularForms["@angular/forms@^13.1.1"]
    end
    
    subgraph "UI Components"
        bootstrap["bootstrap@4.1.3"]
        ngBootstrap["@ng-bootstrap/ng-bootstrap@^11.0.0"]
        codemirror["codemirror@^5.65.0"]
        ngxCodemirror["@ctrl/ngx-codemirror@^5.1.1"]
    end
    
    subgraph "JavaScript Parsing"
        esprima["esprima@^4.0.1"]
        esprimaTypes["@types/esprima@^4.0.3"]
    end
    
    subgraph "Runtime Support"
        rxjs["rxjs@^7.5.1"]
        coreJs["core-js@^3.20.2"]
        zoneJs["zone.js@^0.11.4"]
        tslib["tslib@^2.3.1"]
    end
    
    angularCore --> rxjs
    angularCore --> zoneJs
    ngBootstrap --> bootstrap
    ngxCodemirror --> codemirror
    esprima --> esprimaTypes
```

**Sources:** [app/package.json:14-34]()

### Core Frontend Dependencies

#### Angular Framework Stack
- **`@angular/core@^13.1.1`** - Core Angular framework providing dependency injection, change detection, and component lifecycle management
- **`@angular/common@^13.1.1`** - Common Angular directives, pipes, and services used throughout the application
- **`@angular/router@^13.1.1`** - Client-side routing for navigation between database exploration views
- **`@angular/forms@^13.1.1`** - Form handling and validation for search queries and configuration inputs

#### User Interface Components
- **`bootstrap@4.1.3`** - CSS framework providing responsive grid system and base styling for UI components
- **`@ng-bootstrap/ng-bootstrap@^11.0.0`** - Angular-specific Bootstrap components with TypeScript support
- **`codemirror@^5.65.0`** - Code editor library providing syntax highlighting and editing capabilities for JSON documents
- **`@ctrl/ngx-codemirror@^5.1.1`** - Angular wrapper for CodeMirror integration

#### JavaScript Processing
- **`esprima@^4.0.1`** - JavaScript parser for analyzing and validating MongoDB query syntax
- **`@types/esprima@^4.0.3`** - TypeScript type definitions for esprima parser

#### Runtime Support Libraries
- **`rxjs@^7.5.1`** - Reactive programming library for handling asynchronous operations and HTTP requests
- **`core-js@^3.20.2`** - Polyfill library for modern JavaScript features across different browsers
- **`zone.js@^0.11.4`** - Execution context library required by Angular for change detection
- **`tslib@^2.3.1`** - TypeScript runtime helper library

**Sources:** [app/package.json:14-34]()

## Development Dependencies

### Backend Development Tools

```mermaid
graph LR
    subgraph "Type Definitions"
        typesExpress["@types/express@^4.17.13"]
        typesMongodb["@types/mongodb@^4.0.7"]
        typesNedb["@types/nedb@^1.8.12"]
        typesFiglet["@types/figlet@^1.5.4"]
    end
    
    subgraph "Runtime Dependencies"
        express["express"]
        mongodb["mongodb"]
        nedb["nedb"]
        figlet["figlet"]
    end
    
    typesExpress -.-> express
    typesMongodb -.-> mongodb
    typesNedb -.-> nedb
    typesFiglet -.-> figlet
```

The backend development dependencies provide TypeScript type definitions for all major runtime dependencies, enabling type safety and IntelliSense support in development environments.

**Sources:** [package.json:27-32]()

### Frontend Development Tools

The frontend includes an extensive development toolchain supporting Angular development, testing, and building:

| Category | Dependencies | Purpose |
|----------|--------------|---------|
| Angular CLI | `@angular/cli@^13.1.2`, `@angular-devkit/build-angular@^13.1.2` | Build system and development server |
| TypeScript | `typescript@^4.5.4`, `@angular/compiler-cli@^13.1.1` | TypeScript compilation and Angular template processing |
| Testing | `jasmine-core@^4.0.0`, `karma@^6.3.10`, `protractor@^7.0.0` | Unit and end-to-end testing frameworks |
| Code Quality | `tslint@^6.1.3`, `codelyzer@^6.0.2` | Static code analysis and linting |

**Sources:** [app/package.json:35-54]()

## Dependency Version Constraints

### Critical Version Compatibility

Several dependencies have strict version constraints that affect system compatibility:

1. **Node.js ≥16.0.0** - Required by AWS SDK v3 for modern security features and API compatibility
2. **Angular 13.x** - All Angular packages must use compatible versions within the same major release
3. **TypeScript ^4.5.4** - Maximum version 4.7 supported by Angular 13.x toolchain
4. **MongoDB Driver ^5.9.2** - Provides compatibility with MongoDB 4.4+ server versions

### Package Lock Integrity

Both `package-lock.json` and `app/package-lock.json` files use lockfileVersion 3, ensuring reproducible builds across development and deployment environments. The lock files specify exact dependency trees with integrity hashes for security verification.

**Sources:** [package-lock.json:3-4](), [app/package-lock.json:3-4]()

---

# Page: Build and Development Setup

# Build and Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/package-lock.json](app/package-lock.json)
- [app/package.json](app/package.json)
- [cli.ts](cli.ts)
- [package.json](package.json)
- [server.ts](server.ts)

</details>



This document covers the complete build and development setup for Mongoku, including project structure, dependencies, build processes, and development workflows. It provides technical guidance for developers who want to contribute to the project, modify the codebase, or understand the build pipeline.

For information about deploying Mongoku in production environments, see [Docker Deployment](#6.1) and [Environment Configuration](#6.2). For details about the overall system architecture, see [Core Architecture](#3).

## Project Structure Overview

Mongoku is organized as a monorepo with separate frontend and backend build configurations. The project uses TypeScript for both the backend server and build tooling, while the frontend is built with Angular.

```mermaid
graph TD
    subgraph "Root Project"
        RootPkg["package.json<br/>Backend Dependencies"]
        ServerTS["server.ts<br/>Express Server"]
        CliTS["cli.ts<br/>CLI Interface"]
        LibDir["lib/<br/>Backend Logic"]
        RoutesDir["routes/<br/>API Routes"]
    end
    
    subgraph "Angular Application"
        AppPkg["app/package.json<br/>Frontend Dependencies"]
        AppSrc["app/src/<br/>Angular Components"]
        AppDist["app/dist/<br/>Built Frontend"]
    end
    
    subgraph "Build Outputs"
        DistDir["dist/<br/>Compiled Backend"]
        DistServer["dist/server.js<br/>Main Entry Point"]
        DistCli["dist/cli.js<br/>CLI Binary"]
    end
    
    RootPkg --> DistDir
    ServerTS --> DistServer
    CliTS --> DistCli
    AppPkg --> AppDist
    AppSrc --> AppDist
    
    DistServer --> AppDist
```

**Sources:** [package.json:1-44](), [app/package.json:1-56](), [server.ts:1-68](), [cli.ts:1-66]()

## Prerequisites and Requirements

### System Requirements

| Component | Requirement | Purpose |
|-----------|-------------|----------|
| Node.js | ^12.20.0 \|\| ^14.15.0 \|\| >=16.10.0 | Runtime environment |
| TypeScript | >=4.4.3 <4.7 | Backend compilation |
| Angular CLI | ^13.1.2 | Frontend build system |
| npm | ^6.11.0 \|\| ^7.5.6 \|\| >=8.0.0 | Package management |

### Core Dependencies

The project maintains two separate dependency trees:

**Backend Dependencies** ([package.json:16-32]()):
- `express`: Web server framework
- `mongodb`: MongoDB driver
- `commander`: CLI argument parsing
- `nedb`: Local configuration storage
- `aws4`: AWS authentication support

**Frontend Dependencies** ([app/package.json:14-34]()):
- `@angular/core`: Angular framework
- `@ctrl/ngx-codemirror`: Code editor component
- `bootstrap`: UI framework
- `rxjs`: Reactive programming library

**Sources:** [package.json:16-32](), [app/package.json:14-34](), [app/package-lock.json:76-80]()

## Development Environment Setup

### Initial Setup Process

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Root as "Root Project"
    participant App as "Angular App"
    participant Build as "Build System"
    
    Dev->>Root: npm install
    Root->>Root: Install backend dependencies
    Dev->>App: cd app && npm install
    App->>App: Install Angular dependencies
    Dev->>Build: npm run build
    Build->>Root: tsc (compile TypeScript)
    Build->>App: ng build --prod
    App->>Build: Generate dist/app
    Build->>Root: Copy to dist/
```

### Build Configuration

The build system uses two separate package managers and build tools:

**Backend Build** ([package.json:34-36]()):
```json
"scripts": {
  "debug-server": "npx tsc -w & npx nodemon --inspect=9017 ./dist/server.js"
}
```

**Frontend Build** ([app/package.json:5-12]()):
```json
"scripts": {
  "ng": "ng",
  "start": "ng serve",
  "build": "ng build --configuration production",
  "test": "ng test",
  "lint": "ng lint"
}
```

**Sources:** [package.json:34-36](), [app/package.json:5-12]()

## Build Process Architecture

### Compilation Pipeline

```mermaid
graph LR
    subgraph "Source Files"
        ServerTS["server.ts"]
        CliTS["cli.ts"] 
        LibTS["lib/*.ts"]
        RoutesTS["routes/*.ts"]
        AppSrc["app/src/**/*"]
    end
    
    subgraph "Build Tools"
        TSC["TypeScript Compiler"]
        NgBuild["Angular CLI Build"]
        Webpack["Webpack via Angular CLI"]
    end
    
    subgraph "Output Artifacts"
        DistServer["dist/server.js"]
        DistCli["dist/cli.js"]
        DistLib["dist/lib/"]
        AppDist["dist/app/"]
    end
    
    ServerTS --> TSC
    CliTS --> TSC
    LibTS --> TSC
    RoutesTS --> TSC
    
    TSC --> DistServer
    TSC --> DistCli
    TSC --> DistLib
    
    AppSrc --> NgBuild
    NgBuild --> Webpack
    Webpack --> AppDist
```

### Build Entry Points

The build system has clearly defined entry points specified in [package.json:33-42]():

- **Main Entry Point**: `./dist/server.js` - Express server
- **CLI Binary**: `./dist/cli.js` - Command-line interface  
- **Published Files**: Only `/dist` directory is included in npm package

**Sources:** [package.json:33-42](), [server.ts:10-61](), [cli.ts:11-65]()

## Development Workflows

### Backend Development

For backend development, the project provides a debug script that combines TypeScript compilation with live reloading:

```bash
npm run debug-server
```

This command ([package.json:35]()):
1. Runs `tsc -w` (TypeScript compiler in watch mode)
2. Runs `nodemon --inspect=9017 ./dist/server.js` (Node.js with debugging)

### Frontend Development

For frontend development, use the Angular CLI development server:

```bash
cd app
npm start  # Equivalent to ng serve
```

### Development Server Configuration

The development setup uses specific port configurations ([server.ts:11]()): 

```typescript
const SERVER_PORT = process.env.MONGOKU_SERVER_PORT || 3100;
```

**Sources:** [package.json:35](), [server.ts:11](), [app/package.json:7]()

## Testing and Debugging

### Debug Configuration

The project includes debugging support through Node.js inspector protocol. The debug script ([package.json:35]()) starts the server with inspector on port 9017:

```bash
npx nodemon --inspect=9017 ./dist/server.js
```

### Testing Framework

Frontend testing uses the Angular testing ecosystem ([app/package.json:35-54]()):

| Tool | Purpose |
|------|---------|
| `jasmine-core` | Testing framework |
| `karma` | Test runner |
| `protractor` | End-to-end testing |
| `karma-chrome-launcher` | Browser testing |

### Available Test Commands

```bash
cd app
npm test     # Unit tests
npm run e2e  # End-to-end tests  
npm run lint # Code linting
```

**Sources:** [package.json:35](), [app/package.json:35-54]()

## Production Build Process

### Build Optimization

The production build process optimizes both frontend and backend code:

```mermaid
graph TD
    subgraph "Production Build"
        ProdBuild["ng build --configuration production"]
        TSBuild["tsc (TypeScript compilation)"]
        Minify["Angular CLI Minification"]
        TreeShake["Tree Shaking"]
        Bundle["Asset Bundling"]
    end
    
    subgraph "Output Optimizations"
        SmallBundle["Minimized JavaScript"]
        OptCSS["Optimized CSS"]
        StaticAssets["Static Asset Optimization"]
        SourceMaps["Source Maps"]
    end
    
    ProdBuild --> Minify
    ProdBuild --> TreeShake  
    ProdBuild --> Bundle
    
    Minify --> SmallBundle
    TreeShake --> OptCSS
    Bundle --> StaticAssets
    Bundle --> SourceMaps
```

### Deployment Artifacts

After building, the project creates a complete deployment package:

- **Backend**: Compiled JavaScript in `dist/` directory
- **Frontend**: Optimized Angular application in `dist/app/`
- **CLI**: Executable binary at `dist/cli.js`

The server serves the Angular application statically ([server.ts:13-38]()) from the `app/` directory relative to the server location.

**Sources:** [app/package.json:8](), [server.ts:13-38](), [package.json:40-42]()

## Process Management Integration

### CLI Process Management

The CLI ([cli.ts:21-65]()) supports multiple process management options:

```typescript
// PM2 process manager
if (pm2) {
    child_process.exec(`pm2 start --name mongoku ${entryPath}`, ...);
}

// Forever process manager  
if (forever) {
    child_process.exec(`forever --uid mongoku start -a ${entryPath}`, ...);
}
```

### Process Manager Commands

| Command | Purpose | Process Manager |
|---------|---------|-----------------|
| `mongoku start` | Direct execution | None |
| `mongoku start --pm2` | Daemon with PM2 | PM2 |
| `mongoku start --forever` | Daemon with Forever | Forever |

**Sources:** [cli.ts:21-65]()