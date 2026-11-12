<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/mcp-gateway · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [dotnet/Microsoft.McpGateway.Service/src/McpSubPathAwareAuthenticationHandler.cs](dotnet/Microsoft.McpGateway.Service/src/McpSubPathAwareAuthenticationHandler.cs)
- [dotnet/Microsoft.McpGateway.Service/src/Program.cs](dotnet/Microsoft.McpGateway.Service/src/Program.cs)

</details>



This document describes the overall system architecture of the MCP Gateway, covering its dual-plane design, core components, and infrastructure integration patterns. The architecture follows a clean separation between runtime data processing and administrative control operations.

For detailed information about individual components, see [Core Components](#3). For API specifications and data contracts, see [API Reference](#4).

## Architectural Overview

The MCP Gateway implements a dual-plane architecture that separates concerns between runtime traffic routing (Data Plane) and administrative operations (Control Plane). The system manages two types of MCP resources: **Adapters** (direct MCP servers) and **Tools** (registered MCP tools with definitions that route through a Tool Gateway Router).

### Dual-Plane Architecture with Adapters and Tools

```mermaid
graph TB
    subgraph "External Clients"
        DataClients["MCP Data Clients"]
        MgmtClients["Management Clients<br/>CLI / API Consumers"]
    end
    
    subgraph "MCP Gateway System"
        subgraph "Authentication"
            AuthHandler["McpSubPathAwareAuthenticationHandler<br/>Azure AD OAuth 2.0"]
            PermProvider["IPermissionProvider<br/>RBAC Authorization"]
        end
        
        subgraph "Data Plane"
            AdapterRouter["AdapterSessionRoutingHandler<br/>/adapters/{name}/mcp"]
            ToolRouter["Tool Gateway Router Routing<br/>/mcp"]
            SessionStore["IAdapterSessionStore<br/>DistributedMemorySessionStore"]
        end
        
        subgraph "Control Plane"
            AdapterMgmt["AdapterManagementService<br/>/adapters CRUD"]
            ToolMgmt["ToolManagementService<br/>/tools CRUD"]
            DeployMgr["KubernetesAdapterDeploymentManager<br/>IAdapterDeploymentManager"]
            AdapterStore["IAdapterResourceStore<br/>CosmosAdapterResourceStore"]
            ToolStore["IToolResourceStore<br/>CosmosToolResourceStore"]
        end
    end
    
    subgraph "Kubernetes Workloads"
        AdapterPods["Adapter StatefulSets<br/>mcp-{name}-0, mcp-{name}-1"]
        ToolGWPods["toolgateway StatefulSet<br/>toolgateway-0, toolgateway-1"]
        ToolPods["Tool StatefulSets<br/>tool-{name}-0, tool-{name}-1"]
    end
    
    subgraph "Storage"
        CosmosDB["Cosmos DB<br/>AdapterContainer<br/>ToolContainer<br/>CacheContainer"]
    end
    
    DataClients -->|"Streamable HTTP"| AuthHandler
    MgmtClients -->|"REST API"| AuthHandler
    
    AuthHandler --> PermProvider
    PermProvider --> AdapterRouter
    PermProvider --> ToolRouter
    PermProvider --> AdapterMgmt
    PermProvider --> ToolMgmt
    
    AdapterRouter <--> SessionStore
    ToolRouter <--> SessionStore
    AdapterRouter -->|"Session Affinity"| AdapterPods
    ToolRouter -->|"Session Affinity"| ToolGWPods
    
    ToolGWPods -->|"Dynamic Routing<br/>by Tool Name"| ToolPods
    
    AdapterMgmt --> DeployMgr
    ToolMgmt --> DeployMgr
    AdapterMgmt --> AdapterStore
    ToolMgmt --> ToolStore
    
    DeployMgr -->|"Create/Update/Delete"| AdapterPods
    DeployMgr -->|"Create/Update/Delete"| ToolGWPods
    DeployMgr -->|"Create/Update/Delete"| ToolPods
    
    AdapterStore --> CosmosDB
    ToolStore --> CosmosDB
    SessionStore --> CosmosDB
```

The architecture maintains strict separation between the Data Plane (runtime routing) and Control Plane (lifecycle management), with shared authentication/authorization infrastructure.

**Sources:** [README.md:22-29](), [dotnet/Microsoft.McpGateway.Service/src/Program.cs:21-137]()

## Data Plane Architecture

The Data Plane handles runtime traffic routing with two distinct routing mechanisms: **Direct Adapter Routing** for accessing specific MCP servers, and **Tool Gateway Routing** for dynamic tool execution through the Tool Gateway Router.

### Data Plane Routing Architecture

```mermaid
graph TB
    subgraph "MCP Clients"
        Client["MCP Client<br/>VS Code / Custom"]
    end
    
    subgraph "Gateway Data Plane"
        AuthN["McpSubPathAwareAuthenticationHandler<br/>OAuth 2.0 Bearer Token"]
        AdapterRoute["POST /adapters/{name}/mcp<br/>AdapterSessionRoutingHandler"]
        ToolRoute["POST /mcp<br/>Tool Gateway Routing"]
        SessionMgr["IAdapterSessionStore<br/>Session Affinity Cache"]
        NodeInfo["IServiceNodeInfoProvider<br/>AdapterKubernetesNodeInfoProvider"]
    end
    
    subgraph "Kubernetes Cluster"
        subgraph "Direct Adapter Access"
            AdapterSvc["Headless Service<br/>mcp-{name}-svc<br/>ClusterIP: None"]
            AdapterPod0["mcp-{name}-0<br/>StatefulSet Pod"]
            AdapterPod1["mcp-{name}-1<br/>StatefulSet Pod"]
        end
        
        subgraph "Tool Gateway System"
            ToolGWSvc["Headless Service<br/>toolgateway-svc<br/>ClusterIP: None"]
            ToolGWPod0["toolgateway-0<br/>StatefulSet Pod<br/>Tool Router"]
            ToolGWPod1["toolgateway-1<br/>StatefulSet Pod<br/>Tool Router"]
        end
        
        subgraph "Registered Tools"
            ToolSvc1["ClusterIP Service<br/>tool-weather-svc"]
            ToolSvc2["ClusterIP Service<br/>tool-calendar-svc"]
            ToolPod1["tool-weather-0<br/>StatefulSet Pod"]
            ToolPod2["tool-calendar-0<br/>StatefulSet Pod"]
        end
    end
    
    Client -->|"Request + Bearer Token"| AuthN
    AuthN --> AdapterRoute
    AuthN --> ToolRoute
    
    AdapterRoute --> SessionMgr
    ToolRoute --> SessionMgr
    AdapterRoute --> NodeInfo
    ToolRoute --> NodeInfo
    
    SessionMgr -->|"Session Affinity<br/>Resolve Pod IP"| AdapterSvc
    AdapterSvc --> AdapterPod0
    AdapterSvc --> AdapterPod1
    
    SessionMgr -->|"Session Affinity<br/>Resolve Pod IP"| ToolGWSvc
    ToolGWSvc --> ToolGWPod0
    ToolGWSvc --> ToolGWPod1
    
    ToolGWPod0 -->|"Dynamic Route<br/>by tool.name"| ToolSvc1
    ToolGWPod0 -->|"Dynamic Route<br/>by tool.name"| ToolSvc2
    ToolGWPod1 -->|"Dynamic Route<br/>by tool.name"| ToolSvc1
    ToolGWPod1 -->|"Dynamic Route<br/>by tool.name"| ToolSvc2
    
    ToolSvc1 --> ToolPod1
    ToolSvc2 --> ToolPod2
```

### Session-Aware Routing Mechanism

The Data Plane implements session affinity using a three-layer routing strategy:

| Component | Responsibility | Implementation |
|-----------|---------------|----------------|
| `AdapterSessionRoutingHandler` | Extracts `session_id` from MCP requests | [dotnet/Microsoft.McpGateway.Service/src/Routing/]() |
| `IAdapterSessionStore` | Maps `session_id` to specific pod instances | `DistributedMemorySessionStore` backed by Cosmos or Redis |
| `IServiceNodeInfoProvider` | Resolves Kubernetes pod IPs for routing | `AdapterKubernetesNodeInfoProvider` queries K8s API |

When a client sends a request:
1. The gateway extracts the `session_id` from the MCP protocol request
2. Session store returns the assigned pod instance (or creates new assignment)
3. Node info provider resolves the pod's cluster IP
4. Request is forwarded directly to the specific pod, bypassing load balancing

This ensures stateful MCP conversations are routed to the same backend instance throughout their lifecycle.

**Sources:** [README.md:141-149](), [dotnet/Microsoft.McpGateway.Service/src/Program.cs:28-30]()

## Control Plane Architecture

The Control Plane manages the complete lifecycle of both adapters and tools through RESTful APIs. It orchestrates Kubernetes deployments, persists metadata, and provides status/logging capabilities.

### Control Plane Service Layer

```mermaid
graph TB
    subgraph "REST API Controllers"
        AdaptersAPI["AdaptersController<br/>POST/GET/PUT/DELETE /adapters<br/>GET /adapters/{name}/status<br/>GET /adapters/{name}/logs"]
        ToolsAPI["ToolsController<br/>POST/GET/PUT/DELETE /tools<br/>GET /tools/{name}/status<br/>GET /tools/{name}/logs"]
    end
    
    subgraph "Management Services"
        AdapterMgmtSvc["AdapterManagementService<br/>IAdapterManagementService"]
        ToolMgmtSvc["ToolManagementService<br/>IToolManagementService"]
        RichResultProvider["AdapterRichResultProvider<br/>IAdapterRichResultProvider"]
    end
    
    subgraph "Deployment Layer"
        IDeploymentMgr["IAdapterDeploymentManager"]
        K8sDeploymentMgr["KubernetesAdapterDeploymentManager<br/>StatefulSet & Service Creation"]
    end
    
    subgraph "Storage Layer"
        IAdapterStore["IAdapterResourceStore"]
        IToolStore["IToolResourceStore"]
        CosmosAdapterStore["CosmosAdapterResourceStore<br/>AdapterContainer"]
        CosmosToolStore["CosmosToolResourceStore<br/>ToolContainer"]
        RedisAdapterStore["RedisAdapterResourceStore<br/>Dev Environment"]
        RedisToolStore["RedisToolResourceStore<br/>Dev Environment"]
    end
    
    subgraph "Kubernetes Abstraction"
        IKubeWrapper["IKubeClientWrapper"]
        KubeClient["KubeClient<br/>Namespace: adapter"]
        K8sClientFactory["IKubernetesClientFactory<br/>LocalKubernetesClientFactory"]
    end
    
    subgraph "Authorization"
        PermProvider["IPermissionProvider<br/>SimplePermissionProvider<br/>Resource Creator + RBAC"]
    end
    
    subgraph "External Systems"
        K8sCluster["Kubernetes Cluster<br/>StatefulSets<br/>Headless Services<br/>ClusterIP Services"]
        CosmosDB["Cosmos DB<br/>McpGatewayDb"]
        RedisCache["Redis<br/>Dev Cache"]
    end
    
    AdaptersAPI --> PermProvider
    ToolsAPI --> PermProvider
    
    PermProvider --> AdapterMgmtSvc
    PermProvider --> ToolMgmtSvc
    PermProvider --> RichResultProvider
    
    AdapterMgmtSvc --> IDeploymentMgr
    AdapterMgmtSvc --> IAdapterStore
    ToolMgmtSvc --> IDeploymentMgr
    ToolMgmtSvc --> IToolStore
    RichResultProvider --> IDeploymentMgr
    
    IDeploymentMgr <|.. K8sDeploymentMgr
    IAdapterStore <|.. CosmosAdapterStore
    IAdapterStore <|.. RedisAdapterStore
    IToolStore <|.. CosmosToolStore
    IToolStore <|.. RedisToolStore
    
    K8sDeploymentMgr --> IKubeWrapper
    IKubeWrapper <|.. KubeClient
    KubeClient --> K8sClientFactory
    
    K8sDeploymentMgr --> K8sCluster
    CosmosAdapterStore --> CosmosDB
    CosmosToolStore --> CosmosDB
    RedisAdapterStore --> RedisCache
    RedisToolStore --> RedisCache
```

### Control Plane Operations

The Control Plane exposes two parallel API surfaces for managing adapters and tools:

| API Endpoint | Purpose | Service Implementation |
|--------------|---------|------------------------|
| `POST /adapters` | Create new adapter | `AdapterManagementService.CreateAdapterAsync()` |
| `GET /adapters` | List adapters | `AdapterManagementService.GetAdaptersAsync()` |
| `GET /adapters/{name}` | Get adapter metadata | `AdapterManagementService.GetAdapterAsync()` |
| `PUT /adapters/{name}` | Update adapter | `AdapterManagementService.UpdateAdapterAsync()` |
| `DELETE /adapters/{name}` | Delete adapter | `AdapterManagementService.DeleteAdapterAsync()` |
| `GET /adapters/{name}/status` | Get deployment status | `AdapterRichResultProvider` + `KubernetesAdapterDeploymentManager` |
| `GET /adapters/{name}/logs` | Get pod logs | `AdapterRichResultProvider` + `KubernetesAdapterDeploymentManager` |
| `POST /tools` | Register new tool | `ToolManagementService.CreateToolAsync()` |
| `GET /tools` | List tools | `ToolManagementService.GetToolsAsync()` |
| `GET /tools/{name}` | Get tool definition | `ToolManagementService.GetToolAsync()` |
| `PUT /tools/{name}` | Update tool | `ToolManagementService.UpdateToolAsync()` |
| `DELETE /tools/{name}` | Delete tool | `ToolManagementService.DeleteToolAsync()` |
| `GET /tools/{name}/status` | Get tool deployment status | Similar to adapters |
| `GET /tools/{name}/logs` | Get tool pod logs | Similar to adapters |

**Sources:** [README.md:119-139](), [dotnet/Microsoft.McpGateway.Service/src/Program.cs:112-120]()

## Tool Gateway System

The Tool Gateway System enables dynamic tool registration and execution through a specialized routing layer. Tools are registered with MCP tool definitions, and the Tool Gateway Router acts as an intelligent dispatcher.

### Tool Gateway Router Architecture

```mermaid
graph TB
    subgraph "Tool Registration"
        DevClient["Management Client"]
        ToolAPI["POST /tools<br/>ToolsController"]
        ToolMgmt["ToolManagementService"]
        ToolStore["IToolResourceStore<br/>ToolContainer in Cosmos"]
        DeployMgr["KubernetesAdapterDeploymentManager"]
    end
    
    subgraph "Kubernetes Tool Deployments"
        ToolStatefulSet["Tool StatefulSet<br/>tool-{name}-0, tool-{name}-1"]
        ToolService["ClusterIP Service<br/>tool-{name}-svc"]
    end
    
    subgraph "Tool Gateway Router"
        RouterStatefulSet["toolgateway StatefulSet<br/>toolgateway-0, toolgateway-1"]
        RouterService["Headless Service<br/>toolgateway-svc"]
        ToolDefProvider["StorageToolDefinitionProvider<br/>IToolDefinitionProvider"]
        HttpToolExecutor["HttpToolExecutor<br/>IToolExecutor"]
    end
    
    subgraph "Runtime Tool Execution"
        McpClient["MCP Client"]
        GatewayRouter["POST /mcp<br/>Tool Gateway Routing"]
        SessionStore["IAdapterSessionStore"]
    end
    
    DevClient -->|"Register Tool<br/>+ Tool Definition"| ToolAPI
    ToolAPI --> ToolMgmt
    ToolMgmt --> ToolStore
    ToolMgmt --> DeployMgr
    
    DeployMgr -->|"Create StatefulSet<br/>+ ClusterIP Service"| ToolStatefulSet
    ToolStatefulSet --> ToolService
    
    DeployMgr -->|"Create/Update<br/>Tool Gateway Router"| RouterStatefulSet
    RouterStatefulSet --> RouterService
    
    ToolStore -->|"Query Definitions"| ToolDefProvider
    
    McpClient -->|"tools/call Request"| GatewayRouter
    GatewayRouter --> SessionStore
    SessionStore -->|"Route to Router Pod"| RouterService
    RouterService --> RouterStatefulSet
    
    RouterStatefulSet --> ToolDefProvider
    RouterStatefulSet --> HttpToolExecutor
    HttpToolExecutor -->|"HTTP Request<br/>Based on Definition"| ToolService
```

### Tool Definition Structure

Each registered tool includes metadata that defines its execution characteristics:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Unique tool identifier used in MCP `tools/call` requests |
| `description` | string | Human-readable description of tool capabilities |
| `inputSchema` | JSON Schema | Defines expected input structure for validation |
| `port` | integer | TCP port where tool server listens (default: 8000) |
| `path` | string | HTTP path for tool execution endpoint (optional) |
| `method` | string | HTTP method (GET, POST, etc.) (optional) |

The `StorageToolDefinitionProvider` loads these definitions from `IToolResourceStore` and makes them available to the Tool Gateway Router at runtime.

### Dynamic Routing Process

1. **Client Request**: MCP client sends `tools/call` request to `POST /mcp`
2. **Session Routing**: Gateway routes to a Tool Gateway Router pod using session affinity
3. **Definition Lookup**: Router queries `StorageToolDefinitionProvider` for tool definition by name
4. **Request Construction**: `HttpToolExecutor` constructs HTTP request using:
   - Service name: `http://tool-{name}-svc:{port}{path}`
   - HTTP method from definition
   - Request body from `tools/call` arguments
5. **Execution**: Router forwards request to target tool server
6. **Response**: Tool result returns through router to gateway to client

This architecture decouples tool discovery from tool execution, enabling hot-swapping tools without gateway restarts.

**Sources:** [README.md:165-189](), [README.md:272-340]()

## Infrastructure Integration

The MCP Gateway integrates with Azure and Kubernetes services to provide enterprise capabilities. The architecture supports both development (local Kubernetes + Redis) and production (AKS + Cosmos DB) environments.

### Kubernetes Resource Topology

```mermaid
graph TB
    subgraph "Kubernetes Cluster - Namespace: adapter"
        subgraph "Gateway Layer"
            GWDeployment["mcpgateway Deployment<br/>Replicas: 2+"]
            GWSvc["mcpgateway-service<br/>ClusterIP: 10.0.1.100<br/>Type: LoadBalancer"]
        end
        
        subgraph "Tool Gateway Router Layer"
            TGWStatefulSet["toolgateway StatefulSet<br/>toolgateway-0, toolgateway-1"]
            TGWSvc["toolgateway-svc<br/>Headless Service<br/>ClusterIP: None"]
        end
        
        subgraph "Adapter Workloads"
            AdapterSS1["StatefulSet: mcp-example<br/>mcp-example-0, mcp-example-1"]
            AdapterSvc1["Headless Service<br/>mcp-example-svc<br/>ClusterIP: None"]
        end
        
        subgraph "Tool Workloads"
            ToolSS1["StatefulSet: tool-weather<br/>tool-weather-0"]
            ToolSvc1["ClusterIP Service<br/>tool-weather-svc"]
            ToolSS2["StatefulSet: tool-calendar<br/>tool-calendar-0"]
            ToolSvc2["ClusterIP Service<br/>tool-calendar-svc"]
        end
        
        subgraph "RBAC"
            ServiceAccount["ServiceAccount<br/>mcpgateway-sa"]
            Role["Role: app-manager<br/>StatefulSets/Services CRUD"]
            RoleBinding["RoleBinding<br/>app-manager-binding"]
        end
    end
    
    subgraph "External Access"
        AppGW["Application Gateway<br/>Public IP<br/>TLS Termination"]
        Client["External Clients"]
    end
    
    subgraph "Azure Services"
        CosmosDB["Cosmos DB<br/>McpGatewayDb<br/>- AdapterContainer<br/>- ToolContainer<br/>- CacheContainer"]
        ACR["Azure Container Registry<br/>mgreg{resourceLabel}.azurecr.io"]
        AppInsights["Application Insights<br/>Telemetry"]
        EntraID["Azure AD / Entra ID<br/>OAuth 2.0"]
    end
    
    Client --> AppGW
    AppGW --> GWSvc
    GWSvc --> GWDeployment
    
    GWDeployment -->|"Session Routing"| AdapterSvc1
    GWDeployment -->|"Session Routing"| TGWSvc
    
    AdapterSvc1 --> AdapterSS1
    TGWSvc --> TGWStatefulSet
    
    TGWStatefulSet -->|"Dynamic Routing"| ToolSvc1
    TGWStatefulSet -->|"Dynamic Routing"| ToolSvc2
    
    ToolSvc1 --> ToolSS1
    ToolSvc2 --> ToolSS2
    
    GWDeployment -.->|"Uses"| ServiceAccount
    TGWStatefulSet -.->|"Uses"| ServiceAccount
    ServiceAccount --> RoleBinding
    RoleBinding --> Role
    
    Role -.->|"Manages"| AdapterSS1
    Role -.->|"Manages"| TGWStatefulSet
    Role -.->|"Manages"| ToolSS1
    Role -.->|"Manages"| ToolSS2
    
    GWDeployment --> CosmosDB
    GWDeployment --> AppInsights
    GWDeployment --> EntraID
    
    AdapterSS1 -.->|"Pull Images"| ACR
    TGWStatefulSet -.->|"Pull Images"| ACR
    ToolSS1 -.->|"Pull Images"| ACR
    ToolSS2 -.->|"Pull Images"| ACR
```

### Service Types and Routing Strategy

The system uses different Kubernetes service types to optimize routing patterns:

| Service Type | Use Case | Example | Routing Behavior |
|--------------|----------|---------|------------------|
| **LoadBalancer** | External gateway access | `mcpgateway-service` | Azure App Gateway backend pool |
| **Headless (ClusterIP: None)** | Session-affinity StatefulSets | `mcp-example-svc`, `toolgateway-svc` | Direct pod IP addressing for sticky sessions |
| **ClusterIP** | Stateless load-balanced tools | `tool-weather-svc`, `tool-calendar-svc` | Round-robin load balancing within cluster |

The gateway has RBAC permissions via `ServiceAccount` + `Role` + `RoleBinding` to dynamically create/update/delete StatefulSets and Services in the `adapter` namespace, enabling meta-orchestration capabilities.

**Sources:** [README.md:349-425](), [dotnet/Microsoft.McpGateway.Service/src/Program.cs:73-105]()

## Component Interaction Patterns

The system implements several key architectural patterns that ensure scalability, maintainability, and operational excellence.

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| **Session Affinity** | Distributed routing with session store | Ensures request consistency for stateful MCP conversations |
| **Adapter Pattern** | `IAdapterDeploymentManager`, `IAdapterResourceStore` | Abstracts deployment and storage implementations |
| **Factory Pattern** | `IKubernetesClientFactory` | Manages Kubernetes client lifecycle |
| **Dependency Injection** | Interface-based service registration | Enables testing and configuration flexibility |
| **Stateless Design** | Distributed session store separation | Supports horizontal scaling and fault tolerance |

### Authentication and Authorization Flow

```mermaid
sequenceDiagram
    participant Client as "MCP Client"
    participant AuthLayer as "Authentication Layer"
    participant DataPlane as "Data Plane Router"
    participant ControlPlane as "Control Plane API"
    participant K8s as "Kubernetes Pods"
    
    Note over Client,K8s: Data Plane Authentication Flow
    Client->>AuthLayer: Request with Bearer Token
    AuthLayer->>AuthLayer: Validate Token (RBAC/ACL)
    AuthLayer->>DataPlane: Authorized Request
    DataPlane->>K8s: Route to MCP Server
    K8s-->>DataPlane: Response
    DataPlane-->>Client: Proxied Response
    
    Note over Client,K8s: Control Plane Authentication Flow
    Client->>AuthLayer: Management Request (/adapters)
    AuthLayer->>AuthLayer: Validate Token & Permissions
    AuthLayer->>ControlPlane: Authorized Management Operation
    ControlPlane->>K8s: Deployment Management
    K8s-->>ControlPlane: Operation Result
    ControlPlane-->>Client: Management Response
```

The dual authentication layers enable independent security policies for runtime data access versus administrative operations, supporting different permission models and audit requirements.

**Sources:** [README.md:37-42](), [README.md:79-80]()

---

