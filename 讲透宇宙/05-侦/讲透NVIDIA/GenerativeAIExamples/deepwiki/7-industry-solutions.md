<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/GenerativeAIExamples · page 7 Industry Solutions · fetched 2026-10-26 -->

# Industry Solutions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [community/SQLServer_AI_with_NVIDIA_NIM/README.md](community/SQLServer_AI_with_NVIDIA_NIM/README.md)
- [community/SQLServer_AI_with_NVIDIA_NIM/local.md](community/SQLServer_AI_with_NVIDIA_NIM/local.md)
- [community/SQLServer_AI_with_NVIDIA_NIM/remote.md](community/SQLServer_AI_with_NVIDIA_NIM/remote.md)
- [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql](community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql)
- [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_create_external_model.sql](community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_create_external_model.sql)
- [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_embedding.sql](community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_embedding.sql)
- [community/SQLServer_AI_with_NVIDIA_NIM/scripts/3_ChangeExternalModel.sql](community/SQLServer_AI_with_NVIDIA_NIM/scripts/3_ChangeExternalModel.sql)
- [community/SQLServer_AI_with_NVIDIA_NIM/scripts/4_Execute_ai_embedding.sql](community/SQLServer_AI_with_NVIDIA_NIM/scripts/4_Execute_ai_embedding.sql)
- [industries/asset_lifecycle_management_agent/.cursor.rules.md](industries/asset_lifecycle_management_agent/.cursor.rules.md)
- [industries/asset_lifecycle_management_agent/.gitignore](industries/asset_lifecycle_management_agent/.gitignore)
- [industries/asset_lifecycle_management_agent/README.md](industries/asset_lifecycle_management_agent/README.md)
- [industries/asset_lifecycle_management_agent/env_template.txt](industries/asset_lifecycle_management_agent/env_template.txt)
- [industries/asset_lifecycle_management_agent/pyproject.toml](industries/asset_lifecycle_management_agent/pyproject.toml)
- [industries/asset_lifecycle_management_agent/setup_database.py](industries/asset_lifecycle_management_agent/setup_database.py)
- [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/__init__.py](industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/__init__.py)
- [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/plotting/code_generation_assistant.py](industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/plotting/code_generation_assistant.py)
- [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/generate_sql_query_and_retrieve_tool.py](industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/generate_sql_query_and_retrieve_tool.py)
- [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_manager.py](industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_manager.py)
- [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_util.py](industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_util.py)

</details>



This document describes production-ready AI solutions for specific industry use cases and enterprise integrations built on NVIDIA's AI infrastructure. These examples demonstrate how to deploy NVIDIA NIMs and related services in real-world enterprise scenarios with production-grade architectures.

The repository includes two major industry solutions:
- **Asset Lifecycle Management Agent**: Multi-agent system for industrial asset management and predictive maintenance (see [7.1](#7.1))
- **SQL Server AI Integration**: Enterprise database integration with AI capabilities (see [7.2](#7.2))

For general RAG implementations and framework examples, see [RAG Implementations](#6). For quick-start examples without GPU requirements, see [Quick Start RAG Examples](#6.1).

---

## Overview

Industry solutions in this repository address specific vertical use cases with complete, deployable architectures. Unlike the general-purpose examples in other sections, these solutions include:

- **Production Architecture**: Multi-tier designs with separation of concerns
- **Enterprise Integration**: Direct integration with enterprise systems (SQL Server, industrial databases)
- **Domain-Specific Logic**: Pre-built models and workflows for specific industries
- **Deployment Options**: Both cloud-hosted (Azure Container Apps) and on-premises (self-hosted NIMs)
- **Security**: TLS/SSL configuration, authentication, and data protection

Both solutions leverage NVIDIA NIM microservices as their inference layer, with the flexibility to use either cloud-hosted NIMs via `build.nvidia.com` or self-hosted Docker containers.

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/README.md:1-155](), [industries/asset_lifecycle_management_agent/README.md:1-100]()

---

## Architecture Comparison

The two industry solutions follow different architectural patterns based on their use cases:

```mermaid
graph TB
    subgraph "Asset Lifecycle Management Agent"
        ALM_User["User Query"]
        ALM_Reasoning["Reasoning Agent<br/>nvidia/llama-3.3-nemotron-super-49b-v1"]
        ALM_ReAct["ReAct Agent<br/>data_analysis_assistant"]
        ALM_Tools["Tools Layer"]
        ALM_SQL["sql_retriever<br/>Vanna + ChromaDB"]
        ALM_RUL["predict_rul<br/>XGBoost + MOMENT"]
        ALM_Anomaly["anomaly_detection<br/>MOMENT-1"]
        ALM_Code["code_generation_assistant<br/>qwen/qwen2.5-coder-32b-instruct"]
        ALM_Sandbox["Docker Sandbox<br/>Code Execution"]
        ALM_DB["nasa_turbo.db<br/>SQLite"]
        
        ALM_User --> ALM_Reasoning
        ALM_Reasoning --> ALM_ReAct
        ALM_ReAct --> ALM_Tools
        ALM_Tools --> ALM_SQL
        ALM_Tools --> ALM_RUL
        ALM_Tools --> ALM_Anomaly
        ALM_Tools --> ALM_Code
        ALM_Code --> ALM_Sandbox
        ALM_SQL --> ALM_DB
    end
    
    subgraph "SQL Server AI Integration"
        SQL_User["T-SQL Query<br/>AI_GENERATE_EMBEDDINGS"]
        SQL_Server["SQL Server 2025<br/>EXTERNAL MODEL"]
        SQL_Endpoint["REST Endpoint<br/>sp_invoke_external_rest_endpoint"]
        SQL_NIM["NVIDIA NIM<br/>llama-nemotron-embed-1b-v2"]
        SQL_Cloud["Azure Container Apps<br/>Cloud Deployment"]
        SQL_Local["Docker Container<br/>Local Deployment"]
        SQL_DB["AdventureWorks DB<br/>ProductDescriptionEmbeddings"]
        
        SQL_User --> SQL_Server
        SQL_Server --> SQL_Endpoint
        SQL_Endpoint --> SQL_NIM
        SQL_NIM -.->|Option 1| SQL_Cloud
        SQL_NIM -.->|Option 2| SQL_Local
        SQL_Server --> SQL_DB
    end
    
    style ALM_Reasoning fill:#e1f5ff
    style ALM_ReAct fill:#ffe1e1
    style SQL_Server fill:#e1f5ff
    style SQL_NIM fill:#76b900
```

**Key Differences**:

| Aspect | Asset Lifecycle Management | SQL Server Integration |
|--------|---------------------------|------------------------|
| **Architecture** | Multi-agent agentic workflow | Direct API integration |
| **Orchestration** | NeMo Agent Toolkit ReAct pattern | T-SQL stored procedures |
| **Primary Use Case** | Complex analysis, predictions, visualization | Embedding generation, semantic search |
| **User Interface** | Natural language chat | SQL queries (T-SQL) |
| **Deployment** | Python application + Docker sandbox | SQL Server + NIM containers |
| **Models Used** | LLM, embeddings, XGBoost, MOMENT | Embedding model only |

Sources: [industries/asset_lifecycle_management_agent/README.md:19-29](), [community/SQLServer_AI_with_NVIDIA_NIM/README.md:32-65]()

---

## Common Infrastructure

Both industry solutions rely on NVIDIA NIM for model serving, but leverage different deployment patterns:

### NVIDIA NIM Deployment Options

```mermaid
graph LR
    subgraph "Cloud Deployment"
        API["build.nvidia.com<br/>API Catalog"]
        Azure["Azure Container Apps<br/>Managed NIM"]
    end
    
    subgraph "Self-Hosted Deployment"
        Docker["Docker Containers<br/>nvcr.io/nim/..."]
        Local["Local GPU Server"]
        OnPrem["Azure Local"]
    end
    
    subgraph "Applications"
        ALM["Asset Lifecycle<br/>Management Agent"]
        SQL["SQL Server 2025<br/>AI Integration"]
    end
    
    API --> ALM
    API --> SQL
    Azure --> SQL
    Docker --> ALM
    Docker --> SQL
    Local --> Docker
    OnPrem --> Docker
```

**API Key Configuration**:
- Both solutions use `NVIDIA_API_KEY` environment variable for authentication
- Cloud deployments use API keys for `build.nvidia.com` or Azure Container Apps
- Self-hosted deployments use NGC API keys for pulling NIM containers from `nvcr.io`

**Model Registry**:
- Asset Lifecycle: Multiple models (LLM for reasoning, embeddings for Vanna, code generation)
- SQL Server: Single embedding model (`llama-nemotron-embed-1b-v2`)

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/README.md:46-64](), [industries/asset_lifecycle_management_agent/env_template.txt:1-17]()

---

## Integration Patterns

### Database Integration Architecture

Both solutions integrate with SQL databases but use different patterns:

```mermaid
graph TB
    subgraph "Asset Lifecycle Management"
        ALM_NL["Natural Language Query"]
        ALM_Vanna["VannaManager<br/>vanna_manager.py"]
        ALM_Vector["ChromaDB / Elasticsearch<br/>Training Data"]
        ALM_LLM["NIM LLM<br/>SQL Generation"]
        ALM_SQL["Generated SQL"]
        ALM_SQLite["nasa_turbo.db<br/>FD001_train, FD001_test, etc."]
        ALM_DF["pandas DataFrame<br/>Query Results"]
        
        ALM_NL --> ALM_Vanna
        ALM_Vanna --> ALM_Vector
        ALM_Vanna --> ALM_LLM
        ALM_LLM --> ALM_SQL
        ALM_SQL --> ALM_SQLite
        ALM_SQLite --> ALM_DF
    end
    
    subgraph "SQL Server Integration"
        SQL_TSQL["T-SQL Command<br/>AI_GENERATE_EMBEDDINGS"]
        SQL_Model["EXTERNAL MODEL<br/>CREATE EXTERNAL MODEL"]
        SQL_Proc["sp_invoke_external_rest_endpoint<br/>POST Request"]
        SQL_NIM["NIM Endpoint<br/>/v1/embeddings"]
        SQL_Response["JSON Response<br/>Embedding Vector"]
        SQL_Table["ProductDescriptionEmbeddings<br/>VECTOR(1024) Column"]
        
        SQL_TSQL --> SQL_Model
        SQL_Model --> SQL_Proc
        SQL_Proc --> SQL_NIM
        SQL_NIM --> SQL_Response
        SQL_Response --> SQL_Table
    end
```

**Asset Lifecycle Management Pattern**:
- Natural language → SQL via Vanna AI
- Vector store (ChromaDB/Elasticsearch) contains training examples
- LLM generates SQL based on database schema and examples
- Direct SQLite connection via `sqlite3` or SQLAlchemy

**SQL Server Integration Pattern**:
- T-SQL native AI functions (`AI_GENERATE_EMBEDDINGS`)
- External model definition with REST endpoint
- Stored procedures manage batch processing
- Direct integration with SQL Server's vector data type

Sources: [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_manager.py:28-300](), [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql:1-177]()

---

## Data Flow Patterns

### Asset Lifecycle Management Data Flow

```mermaid
sequenceDiagram
    participant User
    participant ReasoningAgent as "Reasoning Agent<br/>reasoning_agent"
    participant ReActAgent as "ReAct Agent<br/>data_analysis_assistant"
    participant SQLRetriever as "sql_retriever<br/>generate_sql_query_and_retrieve_tool"
    participant VannaManager as "VannaManager<br/>vanna_manager.py"
    participant DB as "nasa_turbo.db"
    participant CodeGen as "code_generation_assistant"
    participant Sandbox as "Docker Sandbox<br/>localhost:6000"
    
    User->>ReasoningAgent: "Predict RUL for engine 24"
    ReasoningAgent->>ReActAgent: Step-by-step plan
    ReActAgent->>SQLRetriever: Retrieve sensor data for unit 24
    SQLRetriever->>VannaManager: Generate SQL
    VannaManager->>DB: Execute SQL query
    DB-->>VannaManager: Query results
    VannaManager-->>SQLRetriever: pandas DataFrame
    SQLRetriever-->>ReActAgent: JSON file path
    ReActAgent->>CodeGen: Load data and predict RUL
    CodeGen->>Sandbox: Execute Python code
    Sandbox-->>CodeGen: Prediction results
    CodeGen-->>ReActAgent: Output file path
    ReActAgent-->>ReasoningAgent: Task completed
    ReasoningAgent-->>User: Final results with visualizations
```

**Key Components**:
- `reasoning_agent`: High-level orchestration using `nvidia/llama-3.3-nemotron-super-49b-v1`
- `data_analysis_assistant`: Tool-calling agent with access to 7+ specialized tools
- `sql_retriever`: Natural language to SQL using Vanna AI framework
- `code_generation_assistant`: Dynamic Python code generation using `qwen/qwen2.5-coder-32b-instruct`
- Docker sandbox: Isolated execution environment at `localhost:6000`

Sources: [industries/asset_lifecycle_management_agent/README.md:19-32](), [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/plotting/code_generation_assistant.py:42-125]()

### SQL Server Integration Data Flow

```mermaid
sequenceDiagram
    participant App as "Application<br/>SQL Query"
    participant SQLServer as "SQL Server 2025"
    participant StoredProc as "nvidia_run_ai_embedding<br/>Stored Procedure"
    participant ExtModel as "EXTERNAL MODEL<br/>Embed_OpenAI"
    participant REST as "sp_invoke_external_rest_endpoint"
    participant NIM as "NVIDIA NIM<br/>https://.../v1/embeddings"
    participant DB as "ProductDescriptionEmbeddings<br/>Table"
    
    App->>SQLServer: EXEC nvidia_run_ai_embedding
    SQLServer->>StoredProc: Execute procedure
    StoredProc->>DB: SELECT NULL embeddings
    DB-->>StoredProc: Descriptions to embed
    loop For each description
        StoredProc->>ExtModel: AI_GENERATE_EMBEDDINGS(text)
        ExtModel->>REST: POST request
        REST->>NIM: JSON payload
        NIM-->>REST: Embedding vector
        REST-->>ExtModel: Parse response
        ExtModel-->>StoredProc: VECTOR(1024)
        StoredProc->>DB: UPDATE embedding column
    end
    StoredProc-->>SQLServer: Batch complete
    SQLServer-->>App: Success message
```

**Key Components**:
- `nvidia_run_ai_embedding`: Main stored procedure for batch embedding generation [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql:22-174]()
- `CREATE EXTERNAL MODEL`: T-SQL command to define NIM endpoint [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_create_external_model.sql:22-64]()
- `sp_invoke_external_rest_endpoint`: Built-in SQL Server 2025 system procedure
- TLS certificates: Required for secure local deployment [community/SQLServer_AI_with_NVIDIA_NIM/local.md:1-69]()

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql:1-177](), [community/SQLServer_AI_with_NVIDIA_NIM/README.md:82-93]()

---

## Deployment Architectures

### Asset Lifecycle Management Deployment

The Asset Lifecycle Management Agent requires multiple components running in coordination:

**Component Deployment Map**:

| Component | Location | Port | Purpose |
|-----------|----------|------|---------|
| FastAPI Server | `nat serve` | 8000 | Main workflow orchestration |
| Web UI | `frontend/` | 3000 | User interface (React) |
| Docker Sandbox | NeMo-Agent-Toolkit | 6000 | Code execution isolation |
| SQLite Database | `database/nasa_turbo.db` | N/A | NASA turbofan dataset |
| ChromaDB | `vanna_vector_store/` | N/A | SQL training data |
| Output Files | `output_data/` | N/A | Generated results |

**Startup Sequence**:

```mermaid
graph TD
    A["1. Create Conda Environment<br/>conda create -n alm python=3.11"]
    B["2. Install NAT<br/>uv sync --all-groups --all-extras"]
    C["3. Install ALM Agent<br/>uv pip install -e ."]
    D["4. Setup Database<br/>python setup_database.py"]
    E["5. Configure Paths<br/>configs/config-reasoning.yml"]
    F["6. Set Environment<br/>export NVIDIA_API_KEY"]
    G["7. Start Sandbox<br/>start_local_sandbox.sh"]
    H["8. Start Server<br/>nat serve --config_file"]
    I["9. Start UI<br/>npm start"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    H --> I
```

**Configuration Files**:
- `configs/config-reasoning.yml`: Main configuration with LLM, function, and workflow definitions
- `vanna_training_data.yaml`: SQL training examples for Vanna
- `pyproject.toml`: Python dependencies and package metadata
- `.env`: Environment variables (API keys)

Sources: [industries/asset_lifecycle_management_agent/README.md:81-433](), [industries/asset_lifecycle_management_agent/pyproject.toml:1-80]()

### SQL Server Integration Deployment

The SQL Server integration supports two deployment models:

#### Cloud Deployment (Azure Container Apps)

```mermaid
graph TB
    subgraph "Azure Cloud"
        ACA["Azure Container App<br/>ngc-test.ashysmoke-ef652ce7.westus.azurecontainerapps.io"]
        Registry["nvcr.io Registry<br/>NIM Container Pull"]
        GPU["Consumption-GPU-NC24-A100<br/>On-Demand GPU"]
        
        Registry --> ACA
        GPU --> ACA
    end
    
    subgraph "SQL Server"
        SQLServer["SQL Server 2025<br/>Local or Cloud"]
        ExtModel["EXTERNAL MODEL<br/>LOCATION='https://ngc-test...v1/embeddings'"]
        
        SQLServer --> ExtModel
    end
    
    ExtModel -->|HTTPS| ACA
```

**Cloud Configuration** [community/SQLServer_AI_with_NVIDIA_NIM/remote.md:1-30]():
1. Create Azure Container App with ingress on port 8000
2. Configure GPU profile: `Consumption-GPU-NC24-A100`
3. Set environment variables: `NGC_API_KEY`, `OPENSSL_FORCE_FIPS_MODE=0`
4. Pull NIM image: `nim/nvidia/llama-3.2-nv-embedqa-1b-v2:latest`
5. Create `EXTERNAL MODEL` in SQL Server pointing to HTTPS endpoint

#### Local Deployment (Azure Local / On-Premises)

```mermaid
graph TB
    subgraph "Windows VM"
        SQLServer["SQL Server 2025<br/>192.168.10.x"]
        CA["Trusted Root CA<br/>ca_cert.pem"]
    end
    
    subgraph "Ubuntu VM / WSL2"
        Docker["Docker Container<br/>NIM with TLS"]
        Certs["TLS Certificates<br/>ssl_cert.pem, ssl_key.pem"]
        GPU["NVIDIA L4 GPU<br/>Driver 580.82.07"]
        
        Certs --> Docker
        GPU --> Docker
    end
    
    SQLServer -.->|Import CA| CA
    SQLServer -->|HTTPS<br/>192.168.10.218:8000| Docker
```

**Local Configuration** [community/SQLServer_AI_with_NVIDIA_NIM/local.md:1-69]():
1. Generate TLS certificates with proper SAN (Subject Alternative Name)
2. Import CA certificate to Windows Trusted Root store
3. Restart SQL Server to recognize new CA
4. Start NIM container with TLS enabled:
   ```bash
   docker run -e NIM_SSL_MODE="tls" \
     -e NIM_SSL_KEY_PATH="/certs/ssl_key.pem" \
     -e NIM_SSL_CERT_PATH="/certs/ssl_cert.pem" \
     -p 0.0.0.0:8000:8000 \
     nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2:latest
   ```
5. Create `EXTERNAL MODEL` with local IP address

**Key Differences**:

| Aspect | Cloud (ACA) | Local (Azure Local/WSL2) |
|--------|-------------|--------------------------|
| **TLS Setup** | Managed by Azure | Manual certificate generation |
| **Network** | HTTPS public endpoint | Local network with firewall rules |
| **GPU** | On-demand, pay-per-use | Dedicated GPU hardware required |
| **Scaling** | Automatic | Manual container management |
| **Cost** | Compute time only | Infrastructure + power |

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/local.md:1-69](), [community/SQLServer_AI_with_NVIDIA_NIM/remote.md:1-30]()

---

## Tool Implementation Details

### Asset Lifecycle Management Tools

The agent uses 7+ specialized tools registered through NeMo Agent Toolkit:

**Tool Registry and Function Signatures**:

```mermaid
graph TB
    subgraph "Tool Registration"
        Register["@register_function<br/>decorator"]
        Config["FunctionBaseConfig<br/>Pydantic model"]
        Builder["Builder<br/>Dependency injection"]
        FuncInfo["FunctionInfo.from_fn<br/>Tool metadata"]
    end
    
    subgraph "SQL Retriever"
        SQLConfig["GenerateSqlQueryAndRetrieveToolConfig"]
        SQLFunc["generate_sql_query_and_retrieve_tool"]
        SQLVanna["VannaManager<br/>Singleton pattern"]
        SQLChroma["ChromaDB<br/>vanna_vector_store/"]
        
        SQLConfig --> SQLFunc
        SQLFunc --> SQLVanna
        SQLVanna --> SQLChroma
    end
    
    subgraph "Prediction Tools"
        RULConfig["PredictRULToolConfig"]
        RULFunc["predict_rul_tool"]
        XGBoost["XGBoost Model<br/>models/xgb_rul_predictor.pkl"]
        
        RULConfig --> RULFunc
        RULFunc --> XGBoost
    end
    
    subgraph "Anomaly Detection"
        AnomalyConfig["AnomalyDetectionToolConfig"]
        AnomalyFunc["anomaly_detection_tool"]
        MOMENT["MOMENT-1 Model<br/>momentfm library"]
        
        AnomalyConfig --> AnomalyFunc
        AnomalyFunc --> MOMENT
    end
    
    subgraph "Code Generation"
        CodeConfig["CodeGenerationAssistantConfig"]
        CodeFunc["code_generation_assistant"]
        CodeLLM["qwen/qwen2.5-coder-32b-instruct"]
        Sandbox["Docker Sandbox<br/>localhost:6000/execute"]
        
        CodeConfig --> CodeFunc
        CodeFunc --> CodeLLM
        CodeFunc --> Sandbox
    end
    
    Register --> SQLConfig
    Register --> RULConfig
    Register --> AnomalyConfig
    Register --> CodeConfig
    Builder --> SQLFunc
    Builder --> RULFunc
    Builder --> AnomalyFunc
    Builder --> CodeFunc
```

**Tool Configuration Pattern**:

Each tool follows the same registration pattern [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/generate_sql_query_and_retrieve_tool.py:31-88]():

1. Define `FunctionBaseConfig` subclass with parameters
2. Use `@register_function` decorator with config type
3. Implement async function accepting `config` and `builder`
4. Return `FunctionInfo` with input schema and description
5. Builder automatically injects LLM and other dependencies

**Example: SQL Retriever Configuration**:

```python
class GenerateSqlQueryAndRetrieveToolConfig(FunctionBaseConfig, name="generate_sql_query_and_retrieve_tool"):
    llm_name: str = Field(description="The name of the LLM to use")
    embedding_name: str = Field(description="The name of the embedding to use")
    vector_store_type: str = Field(default="chromadb")
    db_connection_string_or_path: str = Field(description="Database connection")
    db_type: str = Field(default="sqlite")
    output_folder: str = Field(description="Output folder path")
    vanna_training_data_path: str = Field(description="Vanna training data")
```

Sources: [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/generate_sql_query_and_retrieve_tool.py:31-88](), [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/plotting/code_generation_assistant.py:30-40]()

### Vanna SQL Generation Implementation

The SQL retriever uses Vanna AI with a custom NVIDIA NIM integration:

**Vanna Architecture**:

```mermaid
graph TB
    subgraph "VannaManager Singleton"
        Manager["VannaManager<br/>_instances: Dict"]
        ConfigKey["create_config_key()<br/>MD5 hash of config"]
        Lock["threading.Lock<br/>Thread-safe creation"]
    end
    
    subgraph "Vanna Instance"
        NIMVanna["NIMVanna<br/>ChromaDB + NIM LLM"]
        ElasticVanna["ElasticNIMVanna<br/>Elasticsearch + NIM LLM"]
        NIMCustomLLM["NIMCustomLLM<br/>ChatNVIDIA wrapper"]
        ChromaDB["ChromaDB_VectorStore<br/>DDL, docs, examples"]
        ElasticVectorStore["ElasticVectorStore<br/>kNN search"]
    end
    
    subgraph "Training Data"
        YAML["vanna_training_data.yaml"]
        DDL["DDL Statements<br/>Table schemas"]
        Docs["Documentation<br/>Domain knowledge"]
        Examples["Question-SQL Pairs<br/>Training examples"]
    end
    
    Manager --> ConfigKey
    Manager --> Lock
    Manager -.->|Creates| NIMVanna
    Manager -.->|Creates| ElasticVanna
    NIMVanna --> NIMCustomLLM
    NIMVanna --> ChromaDB
    ElasticVanna --> NIMCustomLLM
    ElasticVanna --> ElasticVectorStore
    YAML --> DDL
    YAML --> Docs
    YAML --> Examples
    DDL --> ChromaDB
    Docs --> ChromaDB
    Examples --> ChromaDB
```

**Key Implementation Details**:

1. **Singleton Pattern** [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_manager.py:38-51]():
   - One `VannaManager` instance per unique configuration
   - Configuration hashed to create unique key
   - Thread-safe with `threading.Lock`

2. **Vector Store Support** [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_util.py:112-552]():
   - `NIMVanna`: ChromaDB for local vector storage
   - `ElasticNIMVanna`: Elasticsearch for distributed vector storage
   - Both use `NVIDIAEmbeddingFunction` with `llama-3.2-nv-embedqa-1b-v2`

3. **Database Connections** [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_manager.py:236-280]():
   - SQLite: Direct `sqlite3` connection with custom `run_sql` function
   - PostgreSQL: `connect_to_postgres()` with psycopg2
   - Generic SQL: `connect_to_sqlalchemy()` for MySQL, SQL Server, Oracle

4. **Training Data Initialization** [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_manager.py:286-298]():
   - Checks if vector store is empty
   - Automatically loads training data from YAML file
   - Chunks long documentation to avoid token limits

Sources: [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_manager.py:28-553](), [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/retrievers/vanna_util.py:112-708]()

### Code Generation Assistant

The code generation assistant dynamically creates and executes Python code:

**Code Generation Workflow**:

```mermaid
sequenceDiagram
    participant Agent as "ReAct Agent"
    participant CodeGen as "code_generation_assistant"
    participant LLM as "qwen/qwen2.5-coder-32b-instruct"
    participant Sandbox as "Docker Sandbox<br/>localhost:6000"
    participant Utils as "Workspace Utils<br/>/workspace/utils/"
    participant Output as "Output Files<br/>/workspace/*.json"
    
    Agent->>CodeGen: Generate code for instructions
    CodeGen->>LLM: System prompt + user instructions
    Note over LLM: Generate minimal Python code<br/>Check for utils if needed
    LLM-->>CodeGen: Raw Python code
    CodeGen->>CodeGen: _clean_generated_code()
    Note over CodeGen: Remove markdown, comments
    CodeGen->>Sandbox: POST /execute with code
    Sandbox->>Sandbox: Execute in isolated Python
    alt Utils Needed
        Sandbox->>Utils: Import utils.rul_utils
        Utils-->>Sandbox: Utility functions
    end
    Sandbox->>Output: Save results to file
    Sandbox-->>CodeGen: Execution result (stdout/stderr)
    alt Success
        CodeGen->>CodeGen: Extract file paths
        CodeGen-->>Agent: Success + file list
    else Error and retries available
        CodeGen->>LLM: Fix prompt with error details
        LLM-->>CodeGen: Corrected code
        Note over CodeGen: Retry execution
    end
```

**System Prompt Design** [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/plotting/code_generation_assistant.py:67-104]():

Key directives in the system prompt:
- "OUTPUT ONLY THE CODE. NO COMMENTS. NO DOCSTRINGS."
- Database path: `/workspace/database/nasa_turbo.db`
- Utils import pattern: `sys.path.append("/workspace"); import utils`
- File paths: Use only filename, not full paths
- Workspace utilities available for RUL transformations

**Retry Logic** [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/plotting/code_generation_assistant.py:133-244]():

1. Execute generated code in sandbox
2. If execution fails and retries available:
   - Send error details back to LLM
   - Request corrected code
   - Re-execute with new code
3. Maximum retries configurable via `max_retries` parameter

**Workspace Utilities System**:

Provides pre-built, reliable functions to avoid context loss in multi-agent chains:

```python
# Traditional approach (unreliable):
# Reasoning Agent → Complex Algorithm → ReAct Agent → Degraded Instructions → Code Gen → Error-Prone Code

# Utilities approach (robust):
# Reasoning Agent → "Use utility X" → ReAct Agent → Code Gen → Pre-built Utility → Reliable Result
```

Available utilities [industries/asset_lifecycle_management_agent/README.md:436-517]():
- `apply_piecewise_rul_transformation(df, maxlife=100)`: RUL transformation with knee pattern
- Future utilities can be added to `/workspace/utils/` directory

Sources: [industries/asset_lifecycle_management_agent/src/asset_lifecycle_management_agent/plotting/code_generation_assistant.py:42-272](), [industries/asset_lifecycle_management_agent/README.md:436-517]()

---

## SQL Server Integration Implementation

### T-SQL Procedures and Functions

The SQL Server integration uses stored procedures for batch processing:

**Stored Procedure Hierarchy**:

```mermaid
graph TB
    subgraph "Procedure Structure"
        Main["nvidia_run_ai_embedding<br/>Main orchestration"]
        Create["CreateExternalModel<br/>Model registration"]
        Embed["nvidia_run_proc_embedding<br/>Legacy batch processor"]
    end
    
    subgraph "T-SQL Functions"
        AIGen["AI_GENERATE_EMBEDDINGS()<br/>Built-in function"]
        ExtModel["EXTERNAL MODEL<br/>Configuration"]
        REST["sp_invoke_external_rest_endpoint<br/>System procedure"]
    end
    
    subgraph "Processing Modes"
        Query["Query Mode<br/>Single embedding"]
        Batch["Batch Mode<br/>TOP @TopN rows"]
        Sweep["Sweep Mode<br/>Process all NULL"]
    end
    
    Main --> AIGen
    AIGen --> ExtModel
    ExtModel --> REST
    REST -->|POST| NIM["NVIDIA NIM<br/>/v1/embeddings"]
    
    Main -.->|Mode 1| Query
    Main -.->|Mode 2| Batch
    Main -.->|Mode 3| Sweep
```

**Main Procedure: `nvidia_run_ai_embedding`** [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql:22-174]():

Three operational modes:

1. **Query Mode** (lines 42-60): Generate single embedding for a prompt
   ```sql
   @Prompt NVARCHAR(MAX)  -- Input text
   @OutVector VECTOR(1024) OUTPUT  -- Returns embedding
   ```

2. **Batch Mode** (lines 127-172): Process top N records with NULL embeddings
   ```sql
   @TopN INT = 10  -- Batch size
   ```

3. **Sweep Mode** (lines 65-122): Process entire table in batches
   ```sql
   @ProcessAll BIT = 1  -- Enable sweep
   @BatchSize INT = 1000  -- Chunk size
   ```

**Model Creation Helper** [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_create_external_model.sql:22-64]():

Dynamically creates or updates `EXTERNAL MODEL` definitions:

```sql
CREATE EXTERNAL MODEL [Embed_OpenAI]
WITH (
    LOCATION = N'https://192.168.10.218:8000/v1/embeddings',
    API_FORMAT = 'OpenAI',
    MODEL_TYPE = EMBEDDINGS,
    MODEL = N'nvidia/llama-3.2-nv-embedqa-1b-v2',
    PARAMETERS = N'{"input_type":"query","dimensions":1024}'
);
```

**Key Configuration Points** [community/SQLServer_AI_with_NVIDIA_NIM/scripts/3_ChangeExternalModel.sql:17-25]():
- `LOCATION`: NIM endpoint URL (cloud or local)
- `MODEL`: Model identifier matching NIM container
- `PARAMETERS`: Additional POST payload fields (input_type, dimensions)
- `API_FORMAT`: Must be 'OpenAI' for compatibility

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql:1-177](), [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_create_external_model.sql:1-64]()

### TLS Certificate Management

For local deployments, TLS certificates enable secure HTTPS communication:

**Certificate Generation and Trust Chain**:

```mermaid
graph TB
    subgraph "Certificate Authority"
        CAKey["ca_key.pem<br/>Root CA Private Key"]
        CACert["ca_cert.pem<br/>Root CA Certificate"]
    end
    
    subgraph "Server Certificates"
        ServerKey["ssl_key.pem<br/>Server Private Key"]
        ServerCSR["server.csr<br/>Certificate Signing Request"]
        ServerCert["ssl_cert.pem<br/>Server Certificate"]
        SAN["Subject Alternative Name<br/>IP:192.168.10.218 or DNS:localhost"]
    end
    
    subgraph "Windows Trust Store"
        Import["certutil -addstore Root"]
        TrustStore["Trusted Root Certification Authorities"]
        SQLRestart["SQL Server Restart<br/>Recognize new CA"]
    end
    
    subgraph "Docker Container"
        Mount["Volume Mount<br/>-v $HOST_CERT_DIR:$NIM_CERT_DIR"]
        NIMEnv["Environment Variables<br/>NIM_SSL_MODE=tls"]
        NIMCert["NIM Uses Certificates<br/>HTTPS on port 8000"]
    end
    
    CAKey --> CACert
    ServerKey --> ServerCSR
    ServerCSR --> SAN
    SAN --> ServerCert
    CACert -.->|Signs| ServerCert
    
    CACert --> Import
    Import --> TrustStore
    TrustStore --> SQLRestart
    
    ServerKey --> Mount
    ServerCert --> Mount
    Mount --> NIMEnv
    NIMEnv --> NIMCert
```

**Certificate Setup Steps** [community/SQLServer_AI_with_NVIDIA_NIM/local.md:1-41]():

1. **Generate Root CA**:
   ```bash
   openssl genrsa -out ca_key.pem 4096
   openssl req -new -x509 -key ca_key.pem -out ca_cert.pem -days 365
   ```

2. **Generate Server Certificate with SAN**:
   ```bash
   # For Ubuntu VM: IP:192.168.10.218
   # For WSL2: DNS:localhost, IP:127.0.0.1
   openssl req -new -key ssl_key.pem -out server.csr -config san.conf
   openssl x509 -req -in server.csr -CA ca_cert.pem -CAkey ca_key.pem \
     -out ssl_cert.pem -days 365 -extfile san.conf -extensions v3_req
   ```

3. **Import to Windows**:
   ```powershell
   certutil -f -addstore Root "C:\SQL2025\nim-ca.cer"
   Get-Service SQL | ? {$_.Status -eq 'Running'} | Restart-Service
   ```

4. **Start NIM with TLS**:
   ```bash
   docker run -e NIM_SSL_MODE="tls" \
     -e NIM_SSL_KEY_PATH="$NIM_CERT_DIR/ssl_key.pem" \
     -e NIM_SSL_CERT_PATH="$NIM_CERT_DIR/ssl_cert.pem" \
     -v $HOST_CERT_DIR:$NIM_CERT_DIR \
     -p 0.0.0.0:8000:8000 \
     nvcr.io/nim/nvidia/llama-3.2-nv-embedqa-1b-v2:latest
   ```

**Verification**:
```bash
curl --ssl-no-revoke --cacert C:\SQL2025\nim-ca.cer \
  https://192.168.10.218:8000/v1/models
```

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/local.md:1-69]()

---

## Production Considerations

### Asset Lifecycle Management Production Checklist

**Scalability Factors**:

| Component | Scaling Approach | Configuration |
|-----------|------------------|---------------|
| FastAPI Server | Horizontal (Kubernetes) | Multiple pods behind load balancer |
| Docker Sandbox | Pool of containers | Multiple sandbox instances |
| ChromaDB | Migrate to Elasticsearch | Distributed vector search |
| SQLite | Migrate to PostgreSQL/MySQL | Connection pooling, read replicas |
| LLM Inference | Self-hosted NIM cluster | Multiple GPU nodes |

**Configuration for Production** [industries/asset_lifecycle_management_agent/.cursor.rules.md:296-343]():

```yaml
# Production config overrides
general:
  logging:
    level: INFO  # Reduce verbosity

llms:
  reasoning_llm:
    base_url: "https://your-nim-cluster/v1"  # Self-hosted
    
functions:
  sql_retriever:
    vector_store_type: "elasticsearch"  # Distributed
    elasticsearch_url: "https://es-cluster:9200"
    
  code_generation_assistant:
    max_retries: 2  # Limit retries for faster failure
```

**Database Migration** [industries/asset_lifecycle_management_agent/README.md:181-194]():
- PostgreSQL support: `uv pip install -e ".[postgres]"`
- MySQL support: `uv pip install -e ".[mysql]"`
- Connection string format: `postgresql://user:pass@host:port/db`

Sources: [industries/asset_lifecycle_management_agent/.cursor.rules.md:296-343](), [industries/asset_lifecycle_management_agent/pyproject.toml:26-54]()

### SQL Server Integration Production Checklist

**Security Hardening**:

```mermaid
graph TB
    subgraph "Security Layers"
        TLS["TLS 1.2/1.3<br/>Certificate validation"]
        Auth["Authentication<br/>SQL login permissions"]
        Network["Network Security<br/>Firewall rules"]
        Audit["Auditing<br/>Query logging"]
    end
    
    subgraph "SQL Server"
        Endpoint["External Endpoint<br/>Enabled"]
        Login["User Login<br/>GRANT EXECUTE ANY EXTERNAL ENDPOINT"]
        Proc["Stored Procedures<br/>WITH EXECUTE AS OWNER"]
    end
    
    subgraph "NIM Security"
        NGC["NGC API Key<br/>Container pull"]
        Runtime["Runtime API Key<br/>Inference requests"]
        Azure["Azure RBAC<br/>Container Apps"]
    end
    
    TLS --> Endpoint
    Auth --> Login
    Network --> Endpoint
    Login --> Proc
    NGC --> Runtime
    Runtime --> Azure
```

**Permission Configuration** [community/SQLServer_AI_with_NVIDIA_NIM/local.md:43-47]():

```sql
-- Enable REST endpoint feature
EXEC sp_configure 'external rest endpoint enabled', 1;
RECONFIGURE WITH OVERRIDE;

-- Grant permissions (if not sysadmin)
GRANT EXECUTE ANY EXTERNAL ENDPOINT TO [YourLogin];
```

**Network Configuration**:

| Deployment | Port | Protocol | Firewall |
|------------|------|----------|----------|
| Cloud (ACA) | 443 | HTTPS | Azure NSG |
| Local (VM) | 8000 | HTTPS | Host firewall |
| WSL2 | 8000 | HTTPS | Not required |

**Performance Tuning**:
- Batch size: 1000 rows per batch (configurable in stored procedure)
- Parallel processing: `MAXDOP 1` to prevent race conditions
- Index strategy: Indexes on `unit_number` and `embedding IS NULL` columns

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/local.md:43-58](), [community/SQLServer_AI_with_NVIDIA_NIM/scripts/2_proc_ai_embedding.sql:103-114]()

---

## Use Case Examples

### Asset Lifecycle Management Example Workflows

**Predictive Maintenance Workflow**:

```mermaid
graph TD
    A["User Query<br/>'Predict RUL for engine 24'"]
    B["Reasoning Agent<br/>Generate plan"]
    C["Step 1: Retrieve Data<br/>sql_retriever"]
    D["Step 2: Predict RUL<br/>predict_rul"]
    E["Step 3: Visualize<br/>code_generation_assistant"]
    F["Output Files<br/>prediction.json, plot.html"]
    
    A --> B
    B --> C
    C -->|engine_24_data.json| D
    D -->|rul_predictions.json| E
    E --> F
    
    style A fill:#e1f5ff
    style F fill:#e1ffe1
```

**Example Prompts** [industries/asset_lifecycle_management_agent/README.md:540-583]():

1. **Data Retrieval**:
   ```
   Retrieve time in cycles and operational setting 1 from FD001 test table 
   for unit number 1 and plot its value vs time.
   ```

2. **Anomaly Detection**:
   ```
   Retrieve and detect anomalies in sensor 4 measurements for engine number 78 
   in train FD001 dataset.
   ```

3. **RUL Prediction with Utilities**:
   ```
   Perform the following steps:
   1. Retrieve time in cycles, all sensor measurements, and ground truth RUL values 
      for engine unit 24 from FD001 train dataset.
   2. Use the retrieved data to predict the Remaining Useful Life (RUL).
   3. Use the piece wise RUL transformation code utility to apply piecewise RUL 
      transformation only to the observed RUL column with MAXLIFE of 100.
   4. Generate a plot that compares the transformed RUL values and predicted RUL 
      values across time.
   ```

**Output Files Generated**:
- JSON data files: `engine_24_data.json`, `rul_predictions.json`
- Visualizations: `comparison_plot.html`, `sensor_trends.html`
- Logs: Detailed execution traces in FastAPI logs

Sources: [industries/asset_lifecycle_management_agent/README.md:540-583]()

### SQL Server Semantic Search Example

**Workflow: Multi-Language Product Search**:

```mermaid
sequenceDiagram
    participant App as "Application"
    participant SQL as "SQL Server"
    participant Table as "ProductDescriptionEmbeddings"
    participant NIM as "NVIDIA NIM"
    
    Note over SQL,Table: Step 1: Generate embeddings
    App->>SQL: EXEC nvidia_run_ai_embedding @TopN=100
    loop For each product description
        SQL->>NIM: Embed product description
        NIM-->>SQL: VECTOR(1024)
        SQL->>Table: UPDATE Embedding column
    end
    SQL-->>App: 100 products embedded
    
    Note over App,Table: Step 2: Search in different language
    App->>SQL: SELECT @QueryEmbedding = AI_GENERATE_EMBEDDINGS('自行车')
    SQL->>NIM: Embed Chinese query
    NIM-->>SQL: Query vector
    App->>SQL: SELECT TOP 5 * FROM Table<br/>ORDER BY VECTOR_DISTANCE(Embedding, @QueryEmbedding)
    SQL-->>App: Top 5 matching products (bicycles)
```

**SQL Example** [community/SQLServer_AI_with_NVIDIA_NIM/README.md:82-93]():

```sql
-- Generate embeddings for all products
EXEC dbo.nvidia_run_ai_embedding
    @ModelName = 'Embed_OpenAI',
    @TopN = 100;

-- Search using natural language in any language
DECLARE @QueryVector VECTOR(1024);
SELECT @QueryVector = AI_GENERATE_EMBEDDINGS(N'自行车' USE MODEL Embed_OpenAI);

-- Find similar products using cosine distance
SELECT TOP 5 
    ProductDescriptionID,
    Description,
    VECTOR_DISTANCE('cosine', Embedding, @QueryVector) AS Distance
FROM Production.ProductDescriptionEmbeddings
WHERE Embedding IS NOT NULL
ORDER BY Distance ASC;
```

**Cross-Language Capabilities**:
- Query in Chinese (自行车) finds bicycles
- Query in German (Fahrrad) finds bicycles  
- Query in English (bicycle) finds bicycles
- All use same embedding space for semantic matching

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/README.md:82-93]()

---

## Monitoring and Observability

### Asset Lifecycle Management Telemetry

**Phoenix Tracing Integration** [industries/asset_lifecycle_management_agent/README.md:584-622]():

```yaml
# config-reasoning.yml
general:
  telemetry:
    _type: phoenix
    endpoint: http://127.0.0.1:6006
    project_name: asset_lifecycle_agent
```

**Start Phoenix Server**:
```bash
python -m phoenix.server.main serve
# Access UI at http://127.0.0.1:6006
```

**Trace Capture**:
- LLM calls with prompts and completions
- Tool invocations with inputs and outputs
- Agent reasoning steps and decisions
- Execution times for each component
- Error traces with stack traces

**Key Metrics Tracked**:

| Metric | Purpose | Location |
|--------|---------|----------|
| LLM Latency | Token generation time | Phoenix traces |
| Tool Execution Time | SQL, prediction, plotting | Agent logs |
| Code Generation Success Rate | Sandbox execution | CodeGen logs |
| SQL Query Performance | Vanna generation time | SQL retriever logs |
| End-to-End Latency | User query to response | Workflow traces |

Sources: [industries/asset_lifecycle_management_agent/README.md:584-622]()

### SQL Server Monitoring

**Built-in SQL Server Monitoring**:

```sql
-- Monitor external endpoint usage
SELECT 
    execution_id,
    start_time,
    end_time,
    status,
    endpoint_url,
    http_status_code
FROM sys.dm_exec_external_rest_requests
ORDER BY start_time DESC;

-- Monitor AI function usage
SELECT 
    database_name,
    model_name,
    execution_count,
    total_duration_ms,
    avg_duration_ms
FROM sys.dm_exec_model_stats
WHERE model_type = 'EMBEDDINGS';
```

**Azure Container Apps Monitoring**:
- Container logs: Azure Portal → Container Apps → Log stream
- Metrics: CPU usage, memory, request count, latency
- Auto-scaling events: Scale-out/scale-in triggers
- Cost tracking: GPU compute time billing

**Performance Baselines**:

| Operation | Local (L4 GPU) | Cloud (A100 GPU) |
|-----------|----------------|------------------|
| Single embedding | ~50ms | ~30ms |
| Batch 100 embeddings | ~5s | ~3s |
| Semantic search (1000 vectors) | ~10ms | ~10ms |

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/README.md:82-93]()

---

## Summary

The industry solutions demonstrate two complementary approaches to integrating NVIDIA AI into production systems:

**Asset Lifecycle Management Agent**:
- Multi-agent agentic workflow using NeMo Agent Toolkit
- Natural language interface with tool-calling LLM
- Comprehensive predictive maintenance capabilities
- Extensible to full asset lifecycle management

**SQL Server AI Integration**:
- Native T-SQL integration with AI functions
- Direct database embedding generation
- Enterprise-grade security and performance
- Multi-language semantic search capabilities

Both solutions share common infrastructure (NVIDIA NIM, ChromaDB/Elasticsearch, Docker) but target different use cases and integration patterns. The modular design allows organizations to choose the approach that best fits their existing systems and workflows.

For detailed implementation guides, see:
- Asset Lifecycle Management: [7.1](#7.1)
- SQL Server AI Integration: [7.2](#7.2)

Sources: [community/SQLServer_AI_with_NVIDIA_NIM/README.md:1-155](), [industries/asset_lifecycle_management_agent/README.md:1-100]()

---

