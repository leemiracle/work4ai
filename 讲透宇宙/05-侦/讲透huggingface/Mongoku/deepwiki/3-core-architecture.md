<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Mongoku · page 3 Core Architecture · fetched 2026-10-26 -->

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

