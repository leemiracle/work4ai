<!-- source: DeepWiki mcp.deepwiki.com · repo stepanogil/autonomous-hr-chatbot · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document describes the high-level architecture of the Autonomous HR Chatbot system, including its major components, their interactions, and deployment options. This architecture enables the HR chatbot to answer employee questions by leveraging language models, specialized tools, and structured data sources.

For implementation details of specific components, see [Frontend Implementation](#2.1), [Backend Implementation](#2.2), and [Agent Tools and Capabilities](#3).

## System Overview

The Autonomous HR Chatbot is built with a modular architecture that separates the user interface from backend processing logic. The system uses LangChain's agent framework to orchestrate language models and specialized tools that access HR policies, employee data, and perform calculations.

```mermaid
graph TD
    User(["User"]) <--> Frontend["Frontend<br/>hr_agent_frontend.py"]
    Frontend <--> Backend["Backend Interface"]
    
    subgraph "Backend Implementations"
        Backend --> LocalBackend["Local Backend<br/>hr_agent_backend_local.py"]
        Backend --> AzureBackend["Azure Backend<br/>hr_agent_backend_azure.py"]
    end
    
    subgraph "LangChain Agent Framework"
        LocalBackend --> LangChainLocal["LangChain Agent<br/>(Local)"]
        AzureBackend --> LangChainAzure["LangChain Agent<br/>(Azure)"]
    end
    
    subgraph "Tools"
        LangChainLocal --> PolicyTool["Timekeeping Policies<br/>RetrievalQA"]
        LangChainLocal --> EmployeeTool["Employee Data<br/>PythonAstREPLTool"]
        LangChainLocal --> CalcTool["Calculator<br/>LLMMathChain"]
        
        LangChainAzure --> PolicyTool
        LangChainAzure --> EmployeeTool
        LangChainAzure --> CalcTool
    end
    
    subgraph "External Services"
        PolicyTool --> Pinecone["Pinecone Vector DB"]
        EmployeeTool --> EmployeeData["Employee Data CSV"]
        
        LocalBackend --> OpenAI["OpenAI API"]
        AzureBackend --> AzureOpenAI["Azure OpenAI Service"]
        AzureBackend --> AzureStorage["Azure Data Lake"]
    end
```

Sources: [README.md:11-18](), [hr_agent_frontend.py](), [hr_agent_backend_local.py](), [hr_agent_backend_azure.py]()

## Core Components

The system consists of the following major components:

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| Frontend | Streamlit-based UI | Provides chat interface for user interaction |
| Backend | Local or Azure implementations | Processes user queries and manages agent interactions |
| Agent Framework | LangChain | Orchestrates tools and language model responses |
| Language Model | OpenAI or Azure OpenAI | Generates responses and reasons about user queries |
| Tools | RetrievalQA, PythonAstREPLTool, LLMMathChain | Provides access to policies, employee data, and calculations |
| Vector Database | Pinecone | Stores and retrieves HR policy embeddings |
| Data Storage | CSV/Azure Data Lake | Stores employee information |

Sources: [README.md:11-18](), [README.md:44-53]()

## Component Interactions

The following diagram illustrates how components interact during a typical user query:

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "hr_agent_frontend.py"
    participant Backend as "hr_agent_backend_(local/azure).py"
    participant Agent as "LangChain Agent"
    participant Tools as "HR Tools"
    
    User->>Frontend: Submit query
    Frontend->>Backend: Forward query
    Backend->>Agent: Initialize agent with tools
    Agent->>Tools: Use relevant tool(s)
    Tools-->>Agent: Return tool results
    Agent-->>Backend: Generate response
    Backend-->>Frontend: Return formatted response
    Frontend-->>User: Display response
```

Sources: [hr_agent_frontend.py](), [hr_agent_backend_local.py](), [hr_agent_backend_azure.py]()

## Backend Implementations

The system supports two backend implementations that share the same interface but differ in their external integrations:

### Local Backend Architecture

```mermaid
graph TD
    Frontend["hr_agent_frontend.py"] --> LocalBackend["hr_agent_backend_local.py"]
    
    subgraph "Local Backend Components"
        LocalBackend --> OpenAILLM["initialize_llm()"]
        LocalBackend --> PineconeInit["initialize_pinecone()"]
        LocalBackend --> AgentCreation["create_hr_agent()"]
        LocalBackend --> ChatProcess["process_chat_history()"]
    end
    
    OpenAILLM --> OpenAIAPI["OpenAI API<br/>gpt-3.5-turbo"]
    PineconeInit --> PineconeDB["Pinecone Vector DB"]
    
    AgentCreation --> PolicyTool["timekeeping_policies_tool"]
    AgentCreation --> EmployeeTool["employee_data_tool"]
    AgentCreation --> CalculatorTool["calculator_tool"]
    
    PolicyTool --> PineconeDB
    EmployeeTool --> EmployeeCSV["employee_data.csv"]
```

Sources: [hr_agent_backend_local.py](), [README.md:34]()

### Azure Backend Architecture

```mermaid
graph TD
    Frontend["hr_agent_frontend.py"] --> AzureBackend["hr_agent_backend_azure.py"]
    
    subgraph "Azure Backend Components"
        AzureBackend --> AzureOpenAILLM["initialize_azure_llm()"]
        AzureBackend --> PineconeInit["initialize_pinecone()"]
        AzureBackend --> AgentCreation["create_hr_agent()"]
        AzureBackend --> ChatProcess["process_chat_history()"]
    end
    
    AzureOpenAILLM --> AzureOpenAI["Azure OpenAI Service"]
    PineconeInit --> PineconeDB["Pinecone Vector DB"]
    
    AgentCreation --> PolicyTool["timekeeping_policies_tool"]
    AgentCreation --> EmployeeTool["employee_data_tool"]
    AgentCreation --> CalculatorTool["calculator_tool"]
    
    PolicyTool --> PineconeDB
    EmployeeTool --> AzureDataLake["Azure Data Lake"]
    
    SAP["SAP HCM"] --> AzureDataFactory["Azure Data Factory"]
    AzureDataFactory --> AzureDataLake
```

Sources: [hr_agent_backend_azure.py](), [README.md:51-53]()

For detailed information about each backend implementation, see [Local Backend](#2.2.1) and [Azure Backend](#2.2.2).

## Tools Architecture

The HR Agent uses three specialized tools integrated through LangChain's agent framework:

```mermaid
graph TD
    Agent["LangChain Agent"] --> ToolSelection["Tool Selection Logic"]
    
    ToolSelection --> PolicyTool["timekeeping_policies_tool<br/>(RetrievalQA)"]
    ToolSelection --> EmployeeTool["employee_data_tool<br/>(PythonAstREPLTool)"]
    ToolSelection --> CalculatorTool["calculator_tool<br/>(LLMMathChain)"]
    
    PolicyTool --> PineconeRetriever["Pinecone Retriever"]
    PineconeRetriever --> OpenAIEmbeddings["text-embedding-ada-002"]
    PineconeRetriever --> PineconeDB["Pinecone Vector DB"]
    
    EmployeeTool --> PythonREPL["Python REPL"]
    PythonREPL --> PandasDF["Pandas DataFrame<br/>employee_data"]
    
    CalculatorTool --> LLMMath["LLM Math Chain"]
    LLMMath --> PythonCalculation["Python Calculation"]
```

Sources: [README.md:14-17](), [hr_agent_backend_local.py]()

For more information on the tools and their capabilities, see [Agent Tools and Capabilities](#3).

## Data Flow Architecture

The following diagram illustrates how data flows through the system during a typical user interaction:

```mermaid
flowchart LR
    User(["User"]) -->|"1. HR query"| Frontend["hr_agent_frontend.py"]
    Frontend -->|"2. Query"| Backend["hr_agent_backend_(local/azure).py"]
    Backend -->|"3. Initialize"| LLM["LLM (OpenAI/Azure)"]
    Backend -->|"4. Create agent"| Agent["HR Agent"]
    
    Agent -->|"5a. Policy question"| PolicyTool["timekeeping_policies_tool"]
    Agent -->|"5b. Employee question"| EmployeeTool["employee_data_tool"]
    Agent -->|"5c. Calculation needed"| CalculatorTool["calculator_tool"]
    
    PolicyTool -->|"6a. Query"| Pinecone["Pinecone Vector DB"]
    EmployeeTool -->|"6b. Query"| EmployeeData["Employee Data"]
    
    Pinecone -->|"7a. Policy chunks"| PolicyTool
    EmployeeData -->|"7b. Employee info"| EmployeeTool
    
    PolicyTool -->|"8a. Tool output"| Agent
    EmployeeTool -->|"8b. Tool output"| Agent
    CalculatorTool -->|"8c. Tool output"| Agent
    
    Agent -->|"9. Response"| LLM
    LLM -->|"10. Final answer"| Backend
    Backend -->|"11. Formatted response"| Frontend
    Frontend -->|"12. Display answer"| User
```

Sources: [hr_agent_frontend.py](), [hr_agent_backend_local.py](), [hr_agent_backend_azure.py]()

## Data Storage Architecture

The system uses different storage solutions for different types of data:

```mermaid
graph TD
    subgraph "HR Policies Storage"
        HRPolicies["HR Policy Documents"] --> TextSplitter["Text Splitter"]
        TextSplitter --> PolicyChunks["Policy Chunks"]
        PolicyChunks --> EmbeddingModel["text-embedding-ada-002"]
        EmbeddingModel --> Embeddings["Vector Embeddings"]
        Embeddings --> PineconeDB["Pinecone Vector DB<br/>namespace=policies"]
    end
    
    subgraph "Employee Data Storage"
        LocalDeploy["Local Deployment"] --> LocalCSV["employee_data.csv"]
        LocalCSV --> PandasDF["Pandas DataFrame"]
        
        AzureDeploy["Azure Deployment"] --> SAP["SAP HCM"]
        SAP --> AzureDataFactory["Azure Data Factory"]
        AzureDataFactory --> AzureDataLake["Azure Data Lake"]
        AzureDataLake --> PandasDF
    end
    
    PineconeDB --> RetrievalQA["RetrievalQA Chain"]
    PandasDF --> PythonREPL["Python REPL Tool"]
    
    RetrievalQA --> Agent["HR Agent"]
    PythonREPL --> Agent
```

Sources: [README.md:14-17](), [README.md:37-41](), [README.md:51-53]()

For detailed information about data processing and storage, see [Data Processing Pipeline](#4).

## Deployment Options

The system supports two primary deployment scenarios:

```mermaid
graph TD
    subgraph "Local Deployment"
        LocalFrontend["hr_agent_frontend.py<br/>(Streamlit)"]
        LocalBackend["hr_agent_backend_local.py"]
        OpenAIAPI["OpenAI API"]
        LocalPinecone["Pinecone Vector DB"]
        LocalCSV["employee_data.csv"]
        
        LocalFrontend <--> LocalBackend
        LocalBackend <--> OpenAIAPI
        LocalBackend <--> LocalPinecone
        LocalBackend <--> LocalCSV
    end
    
    subgraph "Azure Deployment"
        AzureFrontend["hr_agent_frontend.py<br/>(Streamlit)"]
        AzureBackend["hr_agent_backend_azure.py"]
        AzureOpenAI["Azure OpenAI Service"]
        AzurePinecone["Pinecone Vector DB"]
        AzureDataLake["Azure Data Lake"]
        
        AzureFrontend <--> AzureBackend
        AzureBackend <--> AzureOpenAI
        AzureBackend <--> AzurePinecone
        AzureBackend <--> AzureDataLake
    end
```

Sources: [README.md:44-53](), [README.md:29-36]()

For detailed deployment instructions, see [Deployment Guide](#5), including [Local Deployment](#5.1) and [Azure Deployment](#5.2).

## Technical Dependencies

The system relies on the following key technologies:

| Technology | Purpose | Used In |
|------------|---------|---------|
| Streamlit | User interface framework | Frontend |
| streamlit_chat | Chat component | Frontend |
| LangChain | Agent framework | Backend |
| OpenAI/Azure OpenAI | Language model provider | Backend |
| Pinecone | Vector database | Backend/Tools |
| Pandas | Data manipulation | Tools/Employee Data |
| Python 3.10+ | Runtime environment | All components |

Sources: [README.md:44-53]()

## Summary

The Autonomous HR Chatbot architecture is designed with modularity and flexibility in mind, allowing for both local and cloud-based deployment options while maintaining consistent functionality. The system integrates language models with specialized tools to provide contextually relevant responses to HR queries by accessing policies, employee data, and performing calculations as needed.

For implementation details about specific components, please refer to the linked wiki pages for each subsystem.

---

