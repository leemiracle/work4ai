<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-support-agent-demo · page 4 User Interfaces · fetched 2026-10-26 -->

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document covers all user-facing interfaces in the OpenAI Customer Support Agent Demo system. It describes the five main interface types: customer chat, agent chat, knowledge base browsing, FAQ viewing, and vector store initialization. These interfaces work together to provide a complete human-in-the-loop customer service experience.

For information about the underlying API endpoints that power these interfaces, see [API Reference](#3). For configuration of interface behavior and styling, see [Configuration and Customization](#5).

## Interface Architecture Overview

The system provides five distinct user interfaces, each serving different user roles and workflows:

```mermaid
graph TB
    subgraph "Customer-Facing Interfaces"
        CustomerChat["/"]
        KnowledgeBase["/kb"]  
        FAQ["/faq"]
    end
    
    subgraph "Agent-Facing Interfaces"
        AgentChat["/agent"]
        InitVS["/init_vs"]
    end
    
    subgraph "Core API Layer"
        TurnResponse["/api/turn_response"]
        VectorStores["/api/vector_stores/*"]
        ListFiles["/api/list_files"]
    end
    
    subgraph "UI Components"
        ChatInterface["Chat Interface Component"]
        ListArticles["ListArticles Component"]
        FileUpload["File Upload Component"]
    end
    
    CustomerChat --> ChatInterface
    AgentChat --> ChatInterface
    ChatInterface --> TurnResponse
    
    KnowledgeBase --> ListArticles
    FAQ --> ListArticles
    ListArticles --> ListFiles
    
    InitVS --> FileUpload
    InitVS --> VectorStores
    FileUpload --> VectorStores
    
    TurnResponse --> VectorStores
```

**Interface Types:**

| Interface | Route | Purpose | User Type |
|-----------|-------|---------|-----------|
| Customer Chat | `/` | Main customer service chat | End customers |
| Agent Chat | `/agent` | Human agent oversight interface | Support agents |
| Knowledge Base | `/kb` | Browse support articles | Public/customers |
| FAQ | `/faq` | Browse frequently asked questions | Public/customers |
| Vector Store Init | `/init_vs` | Initialize AI knowledge base | Administrators |

Sources: [README.md:1-129]()

## Customer and Agent Chat Interfaces

The core chat functionality is implemented through two parallel interfaces that share the same underlying chat components but provide different user experiences.

### Chat Interface Architecture

```mermaid
graph TB
    subgraph "Customer Interface ('/')"
        CustomerUI["Customer Chat UI"]
        CustomerInput["Message Input"]
        CustomerHistory["Chat History"]
    end
    
    subgraph "Agent Interface ('/agent')"
        AgentUI["Agent Chat UI"]
        AgentInput["Message Input with Edit"]
        AgentHistory["Chat History"]
        SuggestedResponse["Suggested Response Panel"]
        ActionsPanel["Suggested Actions Panel"]
        ContextPanel["Context & Articles Panel"]
    end
    
    subgraph "Shared Components"
        ChatInterface["Chat Interface Component"]
        MessageRenderer["Message Renderer"]
        StreamingHandler["Streaming Response Handler"]
    end
    
    subgraph "Backend Integration"
        TurnResponseAPI["/api/turn_response"]
        SSEStream["Server-Sent Events"]
        OpenAIAPI["OpenAI Responses API"]
    end
    
    CustomerUI --> ChatInterface
    AgentUI --> ChatInterface
    
    ChatInterface --> MessageRenderer
    ChatInterface --> StreamingHandler
    ChatInterface --> TurnResponseAPI
    
    TurnResponseAPI --> SSEStream
    TurnResponseAPI --> OpenAIAPI
    
    SSEStream --> SuggestedResponse
    SSEStream --> ActionsPanel
    SSEStream --> ContextPanel
    
    CustomerInput --> TurnResponseAPI
    AgentInput --> TurnResponseAPI
```

### Interface Differences

**Customer Interface (`/`):**
- Simple chat interface for end customers
- Direct message sending and receiving
- No editing capabilities for AI responses
- Focused on conversation flow

**Agent Interface (`/agent`):**
- Enhanced interface for human agents
- Streaming suggested responses from AI
- Ability to edit responses before sending
- Action suggestion panel for tool calls
- Context panel showing relevant knowledge base articles
- Human oversight controls for sensitive actions

### Chat Flow Integration

```mermaid
sequenceDiagram
    participant Customer as "Customer ('/')"
    participant Agent as "Agent ('/agent')"
    participant TurnAPI as "/api/turn_response"
    participant OpenAI as "OpenAI API"
    participant Functions as "Tool Functions"
    
    Customer->>TurnAPI: "Send message"
    TurnAPI->>OpenAI: "Stream request with tools"
    
    par "Parallel Processing"
        OpenAI-->>Agent: "Stream suggested response"
        Agent->>Agent: "Review & edit response"
    and
        OpenAI-->>Agent: "Stream suggested actions"
        Agent->>Agent: "Approve/reject actions"
        Agent->>Functions: "Execute approved actions"
    end
    
    Agent->>Customer: "Send final response"
    Customer->>Customer: "Display response"
```

Sources: [README.md:7-11](), [README.md:16-24](), [README.md:81-86]()

## Knowledge Base and FAQ Pages

The system provides public-facing interfaces for browsing the knowledge base content that powers the AI's contextual responses.

### Knowledge Base Interface Structure

```mermaid
graph TB
    subgraph "Public Content Pages"
        KBPage["/kb"]
        FAQPage["/faq"]
    end
    
    subgraph "Content Display Components"
        ListArticles["ListArticles Component"]
        ArticleRenderer["Article Content Renderer"]
        FolderNavigation["Folder Navigation"]
    end
    
    subgraph "File System Integration"
        ListFilesAPI["/api/list_files"]
        PublicKB["/public/knowledge_base/"]
        PublicFAQ["/public/faq/"]
    end
    
    subgraph "Configuration"
        KBFolders["KB_FOLDERS Config"]
        Constants["config/constants.ts"]
    end
    
    KBPage --> ListArticles
    FAQPage --> ListArticles
    
    ListArticles --> ArticleRenderer
    ListArticles --> FolderNavigation
    ListArticles --> ListFilesAPI
    
    ListFilesAPI --> PublicKB
    ListFilesAPI --> PublicFAQ
    
    KBFolders --> ListFilesAPI
    Constants --> ListArticles
```

### Content Organization

**Knowledge Base (`/kb`):**
- Displays structured support articles
- Organized by folders defined in `KB_FOLDERS` configuration
- Direct access to files in `/public/knowledge_base/`
- Used by AI for contextual responses via vector store

**FAQ (`/faq`):**
- Displays frequently asked questions
- Organized by folders defined in `KB_FOLDERS` configuration  
- Direct access to files in `/public/faq/`
- Provides quick answers to common questions

### Article Display Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Folder Navigation | Browse articles by category | `FolderNavigation` component |
| Article Rendering | Display markdown/text content | `ArticleRenderer` component |
| File Listing | Dynamic file discovery | `/api/list_files` endpoint |
| Cross-Reference | Link articles to chat responses | Vector store integration |

Sources: [README.md:18-19](), [README.md:84-85]()

## Vector Store Initialization Interface

The `/init_vs` interface provides administrative functionality for setting up and managing the AI's knowledge base through OpenAI's vector store system.

### Vector Store Management Flow

```mermaid
graph TB
    subgraph "Initialization Interface ('/init_vs')"
        InitPage["Vector Store Init Page"]
        CreateButton["Create Vector Store Button"]
        UploadPanel["File Upload Panel"]
        StatusDisplay["Upload Status Display"]
        StoreIDInput["Vector Store ID Input"]
    end
    
    subgraph "Vector Store API Integration"
        CreateStore["/api/vector_stores/create_store"]
        UploadFile["/api/vector_stores/upload_file"]
        AddFile["/api/vector_stores/add_file"]
        RetrieveStore["/api/vector_stores/retrieve_store"]
        ListStoreFiles["/api/vector_stores/list_files"]
    end
    
    subgraph "File Processing"
        ListFiles["/api/list_files"]
        PublicFiles["/public/ directories"]
        OpenAIVectorStore["OpenAI Vector Store"]
    end
    
    subgraph "Configuration Update"
        ConstantsUpdate["Update config/constants.ts"]
        VectorStoreID["VECTOR_STORE_ID constant"]
    end
    
    InitPage --> CreateButton
    InitPage --> UploadPanel
    InitPage --> StatusDisplay
    
    CreateButton --> CreateStore
    UploadPanel --> UploadFile
    UploadPanel --> AddFile
    
    CreateStore --> OpenAIVectorStore
    UploadFile --> OpenAIVectorStore
    AddFile --> OpenAIVectorStore
    
    ListFiles --> PublicFiles
    UploadPanel --> ListFiles
    
    InitPage --> ConstantsUpdate
    ConstantsUpdate --> VectorStoreID
    
    OpenAIVectorStore --> RetrieveStore
    OpenAIVectorStore --> ListStoreFiles
```

### Initialization Workflow

**Step 1: Vector Store Creation**
- Click "Create Vector Store" to establish new vector store via `/api/vector_stores/create_store`
- Receives vector store ID from OpenAI
- Updates local configuration with new ID

**Step 2: Content Upload**
- Scans `/public/knowledge_base/` and `/public/faq/` directories
- Uploads files through `/api/vector_stores/upload_file`
- Associates files with vector store via `/api/vector_stores/add_file`

**Step 3: Configuration Update**
- Manual update of `config/constants.ts` with new `VECTOR_STORE_ID`
- Enables AI to use uploaded content for contextual responses

### Administrative Features

| Feature | API Endpoint | Purpose |
|---------|-------------|---------|
| Store Creation | `/api/vector_stores/create_store` | Initialize new vector store |
| File Upload | `/api/vector_stores/upload_file` | Upload individual files |
| File Association | `/api/vector_stores/add_file` | Link files to store |
| Store Retrieval | `/api/vector_stores/retrieve_store` | Get store metadata |
| File Listing | `/api/vector_stores/list_files` | View store contents |

Sources: [README.md:67-69](), [README.md:18]()

## Interface Integration and Data Flow

The interfaces work together to provide a complete customer service ecosystem, with data flowing between customer interactions, agent oversight, and knowledge management.

### Cross-Interface Data Flow

```mermaid
graph LR
    subgraph "Customer Journey"
        CustomerQuery["Customer Query (/)"]
        CustomerResponse["Customer Receives Response"]
    end
    
    subgraph "Agent Workflow"  
        AgentReview["Agent Reviews (/agent)"]
        AgentEdit["Agent Edits Response"]
        AgentApprove["Agent Approves Actions"]
    end
    
    subgraph "Knowledge Integration"
        VectorSearch["Vector Store Search"]
        KBArticles["KB Articles (/kb)"]
        FAQContent["FAQ Content (/faq)"]
    end
    
    subgraph "Admin Management"
        VectorInit["Vector Store Init (/init_vs)"]
        ContentUpdate["Content Updates"]
    end
    
    CustomerQuery --> VectorSearch
    VectorSearch --> KBArticles
    VectorSearch --> FAQContent
    VectorSearch --> AgentReview
    
    AgentReview --> AgentEdit
    AgentEdit --> AgentApprove
    AgentApprove --> CustomerResponse
    
    VectorInit --> ContentUpdate
    ContentUpdate --> VectorSearch
    
    AgentReview -.-> KBArticles
    AgentReview -.-> FAQContent
```

### State Management Across Interfaces

**Shared State Elements:**
- Chat conversation history
- Vector store ID and content
- Tool function availability
- Configuration settings from `config/constants.ts`

**Interface-Specific State:**
- Customer interface: Simple message history
- Agent interface: Suggested responses, pending actions, context articles
- Knowledge interfaces: File listings, folder navigation
- Admin interface: Upload progress, store status

Sources: [README.md:96-104](), [README.md:110-118]()

---

