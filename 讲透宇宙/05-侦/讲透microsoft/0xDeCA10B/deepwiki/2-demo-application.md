<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/0xDeCA10B · page 2 Demo Application · fetched 2026-10-26 -->

# Demo Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [demo/README.md](demo/README.md)
- [demo/client/src/float-utils.js](demo/client/src/float-utils.js)
- [demo/package.json](demo/package.json)
- [demo/yarn.lock](demo/yarn.lock)

</details>



## Purpose and Scope

The Demo Application is a full-stack web application that showcases the Sharing Updatable Models (SUM) framework through an interactive dashboard. It provides a complete example implementation of blockchain-based collaborative machine learning, allowing users to deploy, train, and interact with AI models on a local Ethereum blockchain.

This document covers the technical architecture, components, and implementation details of the demo application. For information about the core SUM framework contracts and smart contract architecture, see [Smart Contracts](#3). For details about the Python-based simulation environment, see [Simulation System](#4).

## System Architecture Overview

The demo application follows a three-tier architecture with a React frontend, Express.js backend, and Ganache blockchain layer. The system demonstrates end-to-end functionality including model deployment, collaborative training, prediction services, and incentive mechanisms.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        ReactApp["React Application"]
        MetaMask["MetaMask Extension"]
        IndexedDB["IndexedDB Storage"]
    end
    
    subgraph "Server Layer"
        ExpressAPI["Express.js Server"]
        SQLiteDB["SQLite Database"]
        LocalStorage["Local File Storage"]
    end
    
    subgraph "Blockchain Layer"
        GanacheCLI["Ganache CLI"]
        CollaborativeTrainer["CollaborativeTrainer64"]
        DataHandler["DataHandler64"]
        Classifiers["ML Classifiers"]
    end
    
    ReactApp --> MetaMask
    ReactApp --> IndexedDB
    ReactApp --> ExpressAPI
    ReactApp --> GanacheCLI
    
    ExpressAPI --> SQLiteDB
    ExpressAPI --> LocalStorage
    
    MetaMask --> GanacheCLI
    GanacheCLI --> CollaborativeTrainer
    GanacheCLI --> DataHandler
    GanacheCLI --> Classifiers
    
    style ReactApp fill:#f9f9f9
    style ExpressAPI fill:#f9f9f9
    style GanacheCLI fill:#f9f9f9
```

Sources: [demo/README.md:1-30](), [demo/package.json:1-35]()

### Data Flow and Interaction Patterns

```mermaid
sequenceDiagram
    participant User
    participant ReactClient as "React Client"
    participant Express as "Express API"
    participant Ganache as "Ganache Blockchain"
    participant MetaMask
    
    Note over User,MetaMask: Model Interaction Flow
    
    User->>ReactClient: "Upload training data"
    ReactClient->>MetaMask: "Request transaction approval"
    MetaMask->>User: "Confirm transaction"
    MetaMask->>Ganache: "Submit addData() transaction"
    ReactClient->>Express: "Store original data"
    Express->>SQLiteDB: "Persist to db.sqlite"
    
    User->>ReactClient: "Request prediction"
    ReactClient->>Ganache: "Call predict() function"
    Ganache-->>ReactClient: "Return prediction result"
    
    User->>ReactClient: "Deploy new model"
    ReactClient->>Express: "POST /api/models"
    Express->>SQLiteDB: "Store model metadata"
    ReactClient->>Ganache: "Deploy smart contracts"
    Ganache-->>ReactClient: "Return contract addresses"
```

Sources: [demo/README.md:100-142](), [demo/package.json:6-15]()

## Frontend Implementation

The React frontend serves as the primary user interface for interacting with blockchain-based machine learning models. It handles Web3 integration, smart contract interactions, and provides components for model management and data visualization.

### Core React Application Structure

```mermaid
graph TB
    subgraph "React Application Structure"
        App["App.js"]
        ModelList["ModelList Component"]
        ModelInteraction["ModelInteraction Component"]
        AddModel["AddModel Component"]
        About["About Component"]
    end
    
    subgraph "Web3 Integration"
        Web3Provider["Web3 Provider"]
        ContractLoader["Contract Loader"]
        MetaMaskInt["MetaMask Integration"]
    end
    
    subgraph "Data Management"
        LocalStore["Local Storage Manager"]
        ServiceStore["Service Data Store"]
        IndexedDBStore["IndexedDB Storage"]
    end
    
    App --> ModelList
    App --> ModelInteraction
    App --> AddModel
    App --> About
    
    ModelList --> Web3Provider
    ModelInteraction --> Web3Provider
    AddModel --> Web3Provider
    
    Web3Provider --> ContractLoader
    Web3Provider --> MetaMaskInt
    
    ModelList --> LocalStore
    ModelList --> ServiceStore
    ModelInteraction --> IndexedDBStore
    
    style App fill:#f9f9f9
    style Web3Provider fill:#f9f9f9
    style LocalStore fill:#f9f9f9
```

Sources: [demo/client/src/float-utils.js:1-20]()

### Development and Build Pipeline

The frontend uses Create React App with additional TypeScript and ESLint configuration for development workflows.

| Component | Technology | Purpose |
|-----------|------------|---------|
| Build System | Create React App | Development and production builds |
| Language | JavaScript/TypeScript | Type-safe frontend development |
| Linting | ESLint + TypeScript ESLint | Code quality enforcement |
| Package Manager | Yarn | Dependency management |
| Testing | Jest | Unit and integration testing |

Sources: [demo/package.json:24-34](), [demo/yarn.lock:90-157]()

## Backend Services

The Express.js backend provides API endpoints for model metadata management, data storage, and serves as an optional persistence layer for the demo application.

### API Server Architecture

```mermaid
graph LR
    subgraph "Express.js Server"
        ExpressApp["express app"]
        BodyParser["body-parser middleware"]
        CORS["CORS middleware"]
    end
    
    subgraph "API Endpoints"
        ModelsAPI["POST /api/models"]
        GetModels["GET /api/models"]
        DataAPI["POST /api/data"]
    end
    
    subgraph "Data Persistence"
        SQLjsDB["sql.js Database"]
        FileSystem["Local File Storage"]
        DBSqlite["db.sqlite file"]
    end
    
    ExpressApp --> BodyParser
    ExpressApp --> CORS
    ExpressApp --> ModelsAPI
    ExpressApp --> GetModels
    ExpressApp --> DataAPI
    
    ModelsAPI --> SQLjsDB
    GetModels --> SQLjsDB
    DataAPI --> FileSystem
    
    SQLjsDB --> DBSqlite
    
    style ExpressApp fill:#f9f9f9
    style SQLjsDB fill:#f9f9f9
```

Sources: [demo/package.json:17-22]()

### Database Schema and Storage

The backend uses SQLite via `sql.js` for lightweight data persistence, storing model metadata and training data references.

```mermaid
erDiagram
    Models {
        string id PK
        string name
        string description
        string contractAddress
        string deployerAddress
        timestamp createdAt
    }
    
    TrainingData {
        string id PK
        string modelId FK
        string userAddress
        blob data
        string classification
        timestamp submittedAt
    }
    
    Models ||--o{ TrainingData : contains
```

Sources: [demo/package.json:21]()

## Blockchain Integration

The demo application integrates with a local Ganache blockchain to demonstrate smart contract interactions for collaborative machine learning.

### Ganache Configuration and Network Setup

The blockchain component uses Ganache CLI with specific configuration for deterministic testing and development:

```mermaid
graph TB
    subgraph "Ganache Configuration"
        GanacheCLI["ganache-cli process"]
        NetworkID["networkId: 5782"]
        ChainID["chainId: 0xDeCA10B"]
        GasLimit["gasLimit: 9000000"]
        Host["host: 0.0.0.0"]
        Port["port: 7545"]
        Mnemonic["Fixed mnemonic seed"]
        Database["blockchain_db directory"]
    end
    
    subgraph "Web3 Connection"
        MetaMaskProvider["MetaMask Provider"]
        RPCEndpoint["http://localhost:7545"]
        PrivateKeys["Deterministic accounts"]
    end
    
    GanacheCLI --> NetworkID
    GanacheCLI --> ChainID
    GanacheCLI --> GasLimit
    GanacheCLI --> Host
    GanacheCLI --> Port
    GanacheCLI --> Mnemonic
    GanacheCLI --> Database
    
    MetaMaskProvider --> RPCEndpoint
    RPCEndpoint --> GanacheCLI
    PrivateKeys --> Mnemonic
    
    style GanacheCLI fill:#f9f9f9
    style MetaMaskProvider fill:#f9f9f9
```

Sources: [demo/package.json:7]()

### Smart Contract Deployment Workflow

```mermaid
graph LR
    subgraph "Contract Deployment"
        TruffleMigration["Truffle Migrations"]
        ContractCompilation["Solidity Compilation"]
        ArtifactGeneration["Contract Artifacts"]
    end
    
    subgraph "Runtime Integration"
        Web3JS["Web3.js Integration"]
        ContractInstances["Contract Instances"]
        TransactionHandling["Transaction Management"]
    end
    
    subgraph "Contract Files"
        CollaborativeTrainer["CollaborativeTrainer64.sol"]
        DataHandler["DataHandler64.sol"]
        Classifiers["Classifier contracts"]
    end
    
    ContractCompilation --> TruffleMigration
    TruffleMigration --> ArtifactGeneration
    ArtifactGeneration --> Web3JS
    Web3JS --> ContractInstances
    ContractInstances --> TransactionHandling
    
    CollaborativeTrainer --> ContractCompilation
    DataHandler --> ContractCompilation
    Classifiers --> ContractCompilation
    
    style TruffleMigration fill:#f9f9f9
    style Web3JS fill:#f9f9f9
```

Sources: [demo/README.md:103-118]()

## Development Workflow

The demo application provides a comprehensive development environment with automated testing, linting, and deployment scripts.

### Build and Development Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `blockchain` | `yarn blockchain` | Start local Ganache blockchain |
| `server` | `yarn server` | Start Express.js API server |
| `client` | `yarn client` | Start React development server |
| `test` | `yarn test` | Run automated test suite |
| `lint` | `yarn lint` | Run code quality checks |
| `clean` | `yarn clean` | Clean blockchain and cache files |

Sources: [demo/package.json:6-15]()

### Testing Infrastructure

```mermaid
graph TB
    subgraph "Test Categories"
        SmartContractTests["Smart Contract Tests"]
        ReactComponentTests["React Component Tests"]
        IntegrationTests["Integration Tests"]
        ManualTests["Manual UI Tests"]
    end
    
    subgraph "Test Tools"
        TruffleTest["Truffle Test Framework"]
        JestTest["Jest Testing Framework"]
        GanacheTest["Test Blockchain Instance"]
    end
    
    subgraph "Test Execution"
        AutomatedPipeline["Automated CI Pipeline"]
        LocalTesting["Local Development Testing"]
        SpecificTests["Targeted Test Execution"]
    end
    
    SmartContractTests --> TruffleTest
    ReactComponentTests --> JestTest
    IntegrationTests --> GanacheTest
    
    TruffleTest --> AutomatedPipeline
    JestTest --> AutomatedPipeline
    
    TruffleTest --> LocalTesting
    JestTest --> LocalTesting
    GanacheTest --> SpecificTests
    
    style TruffleTest fill:#f9f9f9
    style AutomatedPipeline fill:#f9f9f9
```

Sources: [demo/README.md:184-213]()

## Deployment and Production Configuration

The demo application supports both development and production deployment modes with Docker containerization and environment-specific configurations.

### Docker Deployment Strategy

```mermaid
graph TB
    subgraph "Docker Configuration"
        Dockerfile["Dockerfile"]
        ServiceDockerfile["service.Dockerfile"]
        DockerCompose["docker-compose setup"]
    end
    
    subgraph "Container Services"
        DemoContainer["decai-demo container"]
        ClientContainer["React client service"]
        ServerContainer["Express server service"]
        BlockchainContainer["Ganache blockchain"]
    end
    
    subgraph "Volume Mounts"
        SourceVolume["Source code volume"]
        NodeModules["node_modules volumes"]
        BlockchainDB["blockchain_db volume"]
    end
    
    Dockerfile --> DemoContainer
    ServiceDockerfile --> ServerContainer
    
    DemoContainer --> ClientContainer
    DemoContainer --> ServerContainer
    DemoContainer --> BlockchainContainer
    
    SourceVolume --> DemoContainer
    NodeModules --> DemoContainer
    BlockchainDB --> BlockchainContainer
    
    style Dockerfile fill:#f9f9f9
    style DemoContainer fill:#f9f9f9
```

Sources: [demo/README.md:40-73]()

### Environment Configuration

The application uses environment-specific settings for development and production deployments:

| Environment Variable | Purpose | Default |
|---------------------|---------|---------|
| `PORT` | Blockchain port | 7545 |
| `REACT_APP_ENABLE_SERVICE_DATA_STORE` | Enable backend storage | true (dev) |
| `NODE_ENV` | Environment mode | development |

Sources: [demo/README.md:120-128]()

---

