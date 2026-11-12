<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Agents · page 4 Deployment and Hosting · fetched 2026-10-26 -->

# Deployment and Hosting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MCSandAgentsEcosystemLinks.md](MCSandAgentsEcosystemLinks.md)
- [README.md](README.md)
- [samples/nodejs/quickstart/README.md](samples/nodejs/quickstart/README.md)
- [samples/nodejs/quickstart/env.TEMPLATE](samples/nodejs/quickstart/env.TEMPLATE)
- [samples/nodejs/quickstart/package.json](samples/nodejs/quickstart/package.json)
- [samples/nodejs/quickstart/src/index.ts](samples/nodejs/quickstart/src/index.ts)
- [samples/nodejs/quickstart/tsconfig.json](samples/nodejs/quickstart/tsconfig.json)

</details>



This document covers the deployment and hosting architecture for Microsoft 365 Agents SDK applications. It explains runtime environments, local development setup, Azure Bot Service integration, cloud deployment options, and storage configuration.

For information about the underlying Activity Protocol and Channel APIs that agents communicate through, see [Activity Protocol Specification](#8.2). For CI/CD pipeline details and automated build processes, see [CI/CD and Build Pipeline](#4.3). For local development workflows using the Agents Playground, see [Local Development](#4.2).

## Deployment Architecture Overview

Agents built with the Microsoft 365 Agents SDK follow a flexible deployment model that supports both local development and production hosting across multiple environments. All implementations share a common architecture regardless of language or hosting platform.

```mermaid
graph TB
    subgraph "Development"
        DEV_CODE["Agent Code<br/>.NET / Node.js / Python"]
        VSCODE["VS Code IDE"]
        DEVTUNNEL["dev tunnel<br/>Local Endpoint Exposure"]
        
        VSCODE --> DEV_CODE
        DEV_CODE --> DEVTUNNEL
    end
    
    subgraph "Azure Bot Service"
        BOT_REG["Bot Registration<br/>App ID + Secret"]
        OAUTH["OAuth Connections"]
        CHANNELS["Channel Configuration"]
        MSG_ENDPOINT["Messaging Endpoint"]
        
        BOT_REG --> OAUTH
        BOT_REG --> CHANNELS
        BOT_REG --> MSG_ENDPOINT
    end
    
    subgraph "Hosting Environments"
        ANON["Anonymous Mode<br/>localhost:3978"]
        AZURE["Azure App Service<br/>Cloud Hosting"]
        CONTAINER["Container Hosting<br/>Docker / Kubernetes"]
        ONPREM["On-Premises<br/>Self-Hosted"]
        
        ANON -.dev only.-> PLAYGROUND["Agents Playground"]
    end
    
    subgraph "State Storage"
        MEM["MemoryStorage<br/>Development"]
        COSMOS["CosmosDB<br/>Production State"]
        BLOB["Blob Storage<br/>Attachments"]
    end
    
    subgraph "Client Channels"
        TEAMS["Microsoft Teams"]
        M365["M365 Copilot"]
        WEBCHAT["WebChat Control"]
        CUSTOM["Custom Channels"]
    end
    
    DEVTUNNEL --> MSG_ENDPOINT
    MSG_ENDPOINT --> ANON
    MSG_ENDPOINT --> AZURE
    MSG_ENDPOINT --> CONTAINER
    MSG_ENDPOINT --> ONPREM
    
    ANON --> MEM
    AZURE --> COSMOS
    AZURE --> BLOB
    CONTAINER --> COSMOS
    CONTAINER --> BLOB
    ONPREM --> COSMOS
    
    BOT_REG --> TEAMS
    BOT_REG --> M365
    BOT_REG --> WEBCHAT
    BOT_REG --> CUSTOM
    
    TEAMS -.activities.-> MSG_ENDPOINT
    M365 -.activities.-> MSG_ENDPOINT
    WEBCHAT -.activities.-> MSG_ENDPOINT
    CUSTOM -.activities.-> MSG_ENDPOINT
```

**Sources**: [README.md:1-106](), [samples/nodejs/quickstart/README.md:1-104]()

## Runtime Environments

The Microsoft 365 Agents SDK supports three language runtimes, each with specific version requirements and hosting integrations.

### Runtime Requirements

| Language | Minimum Version | Hosting Framework | Package Manager |
|----------|----------------|-------------------|-----------------|
| .NET | 8.0 | ASP.NET Core | NuGet |
| Node.js | 20+ (22 recommended) | Express.js v5 | npm |
| Python | 3.8+ | aiohttp | pip |

### Node.js Runtime Configuration

Node.js agents use the Express.js framework for HTTP hosting. The `@microsoft/agents-hosting-express` package provides the integration layer.

```mermaid
graph LR
    INDEX["index.ts<br/>Agent Entry Point"]
    APP["AgentApplication<br/>Core Agent Logic"]
    STORAGE["MemoryStorage<br/>IStorage implementation"]
    DOWNLOADER["AttachmentDownloader<br/>File handling"]
    SERVER["startServer<br/>Express Integration"]
    EXPRESS["Express.js v5<br/>HTTP Server"]
    
    INDEX --> APP
    INDEX --> STORAGE
    INDEX --> DOWNLOADER
    INDEX --> SERVER
    APP --> STORAGE
    APP --> DOWNLOADER
    SERVER --> APP
    SERVER --> EXPRESS
    EXPRESS --> PORT["Port 3978<br/>HTTP Endpoint"]
```

The basic agent initialization pattern is shown in [samples/nodejs/quickstart/src/index.ts:1-44]():

- Line 19: `MemoryStorage` is instantiated for development
- Line 21: `AttachmentDownloader` handles file downloads
- Lines 23-26: `AgentApplication` is created with storage and downloader configuration
- Line 43: `startServer` from `@microsoft/agents-hosting-express` starts the HTTP server

**Sources**: [samples/nodejs/quickstart/src/index.ts:1-44](), [samples/nodejs/quickstart/package.json:1-30]()

## Local Development Setup

Local development requires configuring the agent to run on `localhost` and exposing it for testing with client applications.

### Anonymous Mode Operation

Anonymous mode allows agents to run without Azure Bot Service authentication, suitable for initial development and testing with the Agents Playground.

```mermaid
graph TB
    START["npm run start:anon"]
    BUILD["npm run build<br/>TypeScript compilation"]
    NODE["node ./dist/index.js<br/>Start agent"]
    LISTEN["localhost:3978<br/>Listening for activities"]
    
    PLAYGROUND["agentsplayground<br/>npm run test-tool"]
    BROWSER["Web Browser<br/>Test Interface"]
    
    START --> BUILD
    BUILD --> NODE
    NODE --> LISTEN
    
    PLAYGROUND --> BROWSER
    BROWSER -.HTTP POST.-> LISTEN
    LISTEN -.Activity Response.-> BROWSER
```

The anonymous mode is configured via npm scripts in [samples/nodejs/quickstart/package.json:1-30]():

- Line 14: `start:anon` runs the agent without environment variables
- Line 15: `start` uses `--env-file .env` for authenticated mode
- Line 16: `test-tool` launches the Agents Playground
- Line 17: `test` runs both agent and test tool in parallel

**Sources**: [samples/nodejs/quickstart/package.json:1-30](), [samples/nodejs/quickstart/README.md:26-66]()

### Dev Tunnel for External Access

Dev tunnel exposes the local agent endpoint to external services like Azure Bot Service for testing with real channels.

```mermaid
graph LR
    AGENT["Agent Process<br/>localhost:3978"]
    DEVTUNNEL["dev tunnel<br/>devtunnel host"]
    PUBLIC["Public URL<br/>https://*.devtunnels.ms"]
    ABS["Azure Bot Service<br/>Messaging Endpoint"]
    TEAMS["Teams Client"]
    
    AGENT --> DEVTUNNEL
    DEVTUNNEL --> PUBLIC
    ABS --> PUBLIC
    TEAMS --> ABS
    PUBLIC -.forwards.-> AGENT
```

Dev tunnel setup as described in [samples/nodejs/quickstart/README.md:80-88]():

1. Install dev tunnel: `https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started`
2. Run: `devtunnel host -p 3978 --allow-anonymous`
3. Note the URL shown after "Connect via browser:"
4. Configure Azure Bot Service messaging endpoint to `{tunnel-url}/api/messages`

**Sources**: [samples/nodejs/quickstart/README.md:70-95]()

## Azure Bot Service Configuration

Azure Bot Service provides bot registration, channel management, and OAuth connection configuration. All production agents require an Azure Bot Service registration.

### Bot Registration Components

```mermaid
graph TB
    subgraph "Azure Active Directory"
        APPREG["App Registration<br/>Application ID"]
        SECRET["Client Secret<br/>Secret Value"]
        TENANT["Tenant ID"]
    end
    
    subgraph "Azure Bot Service"
        BOTREG["Bot Resource<br/>Bot Handle"]
        SETTINGS["Bot Settings<br/>Configuration"]
        MSGENDPOINT["Messaging Endpoint<br/>/api/messages"]
        OAUTHCONN["OAuth Connections<br/>User Auth"]
        CHANNELS["Channels<br/>Teams, WebChat, etc"]
    end
    
    subgraph "Agent Configuration"
        ENVFILE[".env File"]
        CLIENTID["clientId"]
        CLIENTSECRET["clientSecret"]
        TENANTID["tenantId"]
    end
    
    APPREG --> BOTREG
    APPREG --> CLIENTID
    SECRET --> CLIENTSECRET
    TENANT --> TENANTID
    
    BOTREG --> SETTINGS
    SETTINGS --> MSGENDPOINT
    SETTINGS --> OAUTHCONN
    SETTINGS --> CHANNELS
    
    CLIENTID --> ENVFILE
    CLIENTSECRET --> ENVFILE
    TENANTID --> ENVFILE
    
    ENVFILE -.configures.-> AGENT["AgentApplication<br/>Runtime"]
    MSGENDPOINT -.routes to.-> AGENT
```

Configuration template is provided in [samples/nodejs/quickstart/env.TEMPLATE:1-10]():

- Line 2: `connections__serviceConnection__settings__clientId` - Application ID from App Registration
- Line 3: `connections__serviceConnection__settings__clientSecret` - Secret value from App Registration
- Line 4: `connections__serviceConnection__settings__tenantId` - Tenant ID where app is registered
- Lines 6-7: Connection mapping for service URLs
- Line 9: Debug logging configuration

**Sources**: [samples/nodejs/quickstart/env.TEMPLATE:1-10](), [samples/nodejs/quickstart/README.md:70-95]()

### Service Connection Configuration Pattern

The hierarchical configuration structure uses double underscores (`__`) to denote nested configuration objects:

```
connections__serviceConnection__settings__clientId
└─┬─────┘ └────────┬──────────┘ └───┬────┘ └───┬───┘
  │               │                  │          │
  Root         Connection       Settings    Property
               Name              Group        Name
```

The `connectionsMap` array maps connection names to service URLs:
- `connectionsMap__0__connection=serviceConnection` - Connection name
- `connectionsMap__0__serviceUrl=*` - Wildcard matches all service URLs

**Sources**: [samples/nodejs/quickstart/env.TEMPLATE:1-10]()

## Cloud Deployment Options

Production agents deploy to Azure App Services, container platforms, or on-premises infrastructure with production-grade storage backends.

### Azure App Service Deployment

```mermaid
graph TB
    subgraph "Source Control"
        REPO["Git Repository<br/>Agent Code"]
    end
    
    subgraph "Build Pipeline"
        CICD["CI/CD Pipeline<br/>GitHub Actions / Azure DevOps"]
        BUILD["Build Step<br/>npm ci / dotnet build"]
        TEST["Test Step<br/>Unit Tests"]
    end
    
    subgraph "Azure Resources"
        APPSERVICE["App Service<br/>Linux / Windows"]
        APPSETTINGS["Application Settings<br/>Environment Variables"]
        SLOTS["Deployment Slots<br/>Staging / Production"]
    end
    
    subgraph "Dependencies"
        COSMOS["CosmosDB<br/>Conversation State"]
        BLOB["Blob Storage<br/>Attachments"]
        KEYVAULT["Key Vault<br/>Secrets"]
    end
    
    subgraph "Bot Service"
        BOTCONFIG["Bot Registration<br/>Messaging Endpoint"]
    end
    
    REPO --> CICD
    CICD --> BUILD
    BUILD --> TEST
    TEST --> APPSERVICE
    
    KEYVAULT --> APPSETTINGS
    APPSETTINGS --> APPSERVICE
    
    APPSERVICE --> COSMOS
    APPSERVICE --> BLOB
    
    BOTCONFIG -.points to.-> APPSERVICE
```

Deployment configuration requirements:

1. **Runtime Configuration**: Node.js 20+, .NET 8.0, or Python 3.8+ runtime
2. **Application Settings**: Environment variables from `.env` template
3. **Messaging Endpoint**: `https://{app-service-name}.azurewebsites.net/api/messages`
4. **Storage Connection Strings**: CosmosDB and Blob Storage connection strings
5. **Authentication Secrets**: Client ID, Client Secret, Tenant ID from Key Vault

**Sources**: [README.md:1-106](), [samples/nodejs/quickstart/README.md:96-98]()

### Container Deployment

Agents can be containerized using Docker and deployed to Kubernetes or Azure Container Instances:

```mermaid
graph LR
    DOCKERFILE["Dockerfile<br/>Multi-stage build"]
    IMAGE["Container Image<br/>Registry"]
    
    subgraph "Orchestration"
        K8S["Kubernetes<br/>Pods + Services"]
        ACI["Azure Container<br/>Instances"]
    end
    
    CONFIG["ConfigMaps<br/>Secrets"]
    STORAGE["Storage<br/>CosmosDB / Blob"]
    
    DOCKERFILE --> IMAGE
    IMAGE --> K8S
    IMAGE --> ACI
    
    CONFIG --> K8S
    CONFIG --> ACI
    
    K8S --> STORAGE
    ACI --> STORAGE
```

Container deployment considerations:
- Base image should include Node.js 20+, .NET 8.0, or Python 3.8+
- Multi-stage builds reduce final image size
- Environment variables injected via Kubernetes ConfigMaps or Secrets
- Health check endpoints for container orchestration
- Horizontal scaling requires stateless design with external storage

**Sources**: [README.md:1-106]()

## State and Storage Configuration

Agents require state storage for maintaining conversation context and blob storage for attachment handling.

### Storage Architecture

```mermaid
graph TB
    subgraph "Agent Runtime"
        APP["AgentApplication"]
        TURNSTATE["TurnState<br/>Conversation State"]
        STORAGE_INT["IStorage Interface"]
    end
    
    subgraph "Development Storage"
        MEMORY["MemoryStorage<br/>In-memory only"]
    end
    
    subgraph "Production Storage"
        COSMOS["CosmosDbPartitionedStorage<br/>Persistent State"]
        COSDB[("CosmosDB<br/>Document Database")]
        
        BLOB["BlobsStorage<br/>Attachment Storage"]
        BLOBSTORE[("Azure Blob Storage<br/>Object Store")]
    end
    
    APP --> TURNSTATE
    TURNSTATE --> STORAGE_INT
    
    STORAGE_INT -.dev mode.-> MEMORY
    STORAGE_INT -.production.-> COSMOS
    STORAGE_INT -.attachments.-> BLOB
    
    COSMOS --> COSDB
    BLOB --> BLOBSTORE
```

The `MemoryStorage` implementation shown in [samples/nodejs/quickstart/src/index.ts:15-19]():

```typescript
// Line 19: MemoryStorage instantiation for development
const storage = new MemoryStorage()
```

For production deployments:
- Replace `MemoryStorage` with `CosmosDbPartitionedStorage` for state persistence
- Configure `BlobsStorage` for attachment handling
- State survives agent restarts and supports clustered deployments
- CosmosDB provides partition key strategies for scaling

**Sources**: [samples/nodejs/quickstart/src/index.ts:15-19](), [samples/nodejs/quickstart/README.md:1-104]()

### MemoryStorage vs Production Storage

| Feature | MemoryStorage | CosmosDB + Blob |
|---------|---------------|-----------------|
| **Persistence** | None (lost on restart) | Persistent across restarts |
| **Scalability** | Single instance only | Horizontal scaling support |
| **Use Case** | Development and testing | Production deployments |
| **Configuration** | No configuration needed | Connection strings required |
| **Cost** | Free | Pay per usage |
| **Attachments** | In-memory | Blob Storage |

**Sources**: [samples/nodejs/quickstart/src/index.ts:15-26]()

## Environment Configuration Management

Configuration for deployed agents follows a hierarchical structure supporting both development and production scenarios.

### Configuration Hierarchy

```mermaid
graph TB
    subgraph "Configuration Sources"
        ENVFILE[".env File<br/>Local Development"]
        APPSETTINGS["App Settings<br/>Azure App Service"]
        KEYVAULT["Key Vault<br/>Secrets"]
        CONFIGMAP["ConfigMap<br/>Kubernetes"]
    end
    
    subgraph "Configuration Categories"
        BOTAUTH["Bot Authentication<br/>clientId, clientSecret, tenantId"]
        CONNMAP["Connection Mappings<br/>serviceUrl patterns"]
        STORAGE["Storage Config<br/>CosmosDB, Blob"]
        DEBUG["Debug Settings<br/>Log levels"]
    end
    
    subgraph "Runtime"
        PROCESS["process.env<br/>Node.js"]
        CONFIG["Configuration<br/>Object"]
        AGENT["AgentApplication<br/>Initialization"]
    end
    
    ENVFILE --> PROCESS
    APPSETTINGS --> PROCESS
    KEYVAULT --> APPSETTINGS
    CONFIGMAP --> PROCESS
    
    PROCESS --> CONFIG
    CONFIG --> BOTAUTH
    CONFIG --> CONNMAP
    CONFIG --> STORAGE
    CONFIG --> DEBUG
    
    BOTAUTH --> AGENT
    CONNMAP --> AGENT
    STORAGE --> AGENT
```

Configuration loading in Node.js uses the `--env-file` flag as shown in [samples/nodejs/quickstart/package.json:15]():

```json
"start": "node --env-file .env ./dist/index.js"
```

This loads environment variables from `.env` file before starting the agent process.

**Sources**: [samples/nodejs/quickstart/package.json:1-30](), [samples/nodejs/quickstart/env.TEMPLATE:1-10]()

### Secret Management Best Practices

1. **Never commit secrets to source control**: Use `.env` for local development, add to `.gitignore`
2. **Azure Key Vault for production**: Store `clientSecret` and connection strings in Key Vault
3. **App Service Configuration**: Reference Key Vault secrets in App Settings: `@Microsoft.KeyVault(SecretUri=...)`
4. **Managed Identity**: Use system-assigned or user-assigned managed identities to access Key Vault
5. **Least privilege**: Grant only necessary permissions to service principals

**Sources**: [samples/nodejs/quickstart/env.TEMPLATE:1-10](), [README.md:1-106]()

## Port and Endpoint Configuration

Agents expose HTTP endpoints for receiving activities from Azure Bot Service and other channels.

### Standard Endpoint Configuration

```mermaid
graph LR
    subgraph "HTTP Server"
        PORT["Port 3978<br/>Default Listening Port"]
        ROUTE["/api/messages<br/>Activity Endpoint"]
    end
    
    subgraph "Express.js Routes"
        EXPRESS["Express Router"]
        MIDDLEWARE["Middleware Pipeline"]
        HANDLER["Activity Handler"]
    end
    
    subgraph "Agent Processing"
        APP["AgentApplication"]
        CONTEXT["TurnContext"]
        HANDLERS["Event Handlers"]
    end
    
    PORT --> ROUTE
    ROUTE --> EXPRESS
    EXPRESS --> MIDDLEWARE
    MIDDLEWARE --> HANDLER
    HANDLER --> APP
    APP --> CONTEXT
    CONTEXT --> HANDLERS
```

The `startServer` function from `@microsoft/agents-hosting-express` automatically:
- Starts Express.js server on port 3978
- Configures `/api/messages` route
- Sets up activity handling middleware
- Initializes JWT validation for bot authentication

Standard messaging endpoint format:
- **Local**: `http://localhost:3978/api/messages`
- **Dev Tunnel**: `https://{tunnel-id}.devtunnels.ms/api/messages`
- **Azure App Service**: `https://{app-name}.azurewebsites.net/api/messages`
- **Custom Domain**: `https://{custom-domain}/api/messages`

**Sources**: [samples/nodejs/quickstart/src/index.ts:43](), [samples/nodejs/quickstart/README.md:38-94]()

## Deployment Checklist

Before deploying an agent to production, verify the following:

### Pre-Deployment Requirements

| Category | Requirement | Verification |
|----------|-------------|--------------|
| **Bot Registration** | Azure Bot Service created | Azure Portal |
| **App Registration** | App ID and Secret generated | Azure AD |
| **Storage** | CosmosDB provisioned | Connection string tested |
| **Blob Storage** | Storage account created | Container exists |
| **Secrets** | Key Vault configured | Managed Identity assigned |
| **Endpoint** | Messaging endpoint configured | Bot Service settings |
| **Channels** | Required channels enabled | Teams, WebChat, etc. |

### Post-Deployment Validation

1. **Health Check**: Verify agent responds to health endpoint
2. **WebChat Test**: Test via Bot Service WebChat
3. **Teams Test**: Send message in Teams if enabled
4. **Authentication**: Verify OAuth flow completes
5. **State Persistence**: Confirm conversation state saves between messages
6. **Logging**: Check Application Insights for telemetry
7. **Error Handling**: Test error scenarios and verify graceful failure

**Sources**: [samples/nodejs/quickstart/README.md:70-104](), [README.md:1-106]()

## Multi-Environment Deployment Strategy

Production agent deployments typically follow a multi-environment strategy for safe releases.

```mermaid
graph LR
    DEV["Development<br/>localhost + dev tunnel"]
    TEST["Test Environment<br/>Azure App Service"]
    STAGE["Staging<br/>Deployment Slot"]
    PROD["Production<br/>Main Slot"]
    
    DEV -->|"Manual Deploy"| TEST
    TEST -->|"CI/CD Pipeline"| STAGE
    STAGE -->|"Slot Swap"| PROD
    
    STAGE -.shares.-> RESOURCES["Shared Resources<br/>CosmosDB, Blob"]
    PROD -.shares.-> RESOURCES
```

Environment-specific considerations:
- **Development**: Anonymous mode, MemoryStorage, dev tunnel
- **Test**: Azure Bot Service, test App ID, MemoryStorage or CosmosDB
- **Staging**: Production Bot Service, staging slot, production storage
- **Production**: Production slot, production secrets, monitoring enabled

Deployment slots enable:
- Zero-downtime deployments via slot swapping
- A/B testing with traffic splitting
- Quick rollback to previous version
- Independent configuration per slot

**Sources**: [README.md:1-106](), [samples/nodejs/quickstart/README.md:1-104]()

---

