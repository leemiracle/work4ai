<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/open-agent-platform · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.yarnrc.yml](.yarnrc.yml)
- [README.md](README.md)
- [apps/web/scripts/update-agents-mcp-url.ts](apps/web/scripts/update-agents-mcp-url.ts)
- [package.json](package.json)

</details>



This document provides a comprehensive overview of the Open Agent Platform repository, its architecture, core systems, and how they integrate to provide a web-based platform for building and managing AI agents. The platform serves as a frontend orchestrator for multiple backend services, enabling users to create, configure, and interact with LangGraph agents through an intuitive interface.

For specific implementation details about individual subsystems, see [Core Platform Architecture](#2), [Agent Management](#3), [Chat Interface](#4), [RAG](#5), [Tools System](#6), and [UI Components](#8).

## Platform Purpose and Architecture

The Open Agent Platform is a no-code agent building platform that provides a modern, web-based interface for creating, managing, and interacting with LangGraph agents. The system is designed as a Next.js monorepo that orchestrates multiple external services rather than functioning as a standalone backend server.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "NextJS_Web_App" ["Next.js Web Application (apps/web)"]
        ChatInterface["ChatInterface Component"]
        AgentDashboard["Agent Dashboard"]
        ConfigSidebar["ConfigurationSidebar"]
        RAGInterface["RAG Collections Interface"]
        ToolsPlayground["Tools Playground"]
        AuthProvider["AuthProvider Context"]
    end
    
    subgraph "External_Services" ["External Service Integrations"]
        LangGraphPlatform["LangGraph Platform<br/>client.assistants API"]
        SupabaseAuth["Supabase Authentication<br/>JWT Tokens"]
        LangConnectRAG["LangConnect RAG Server<br/>Document Management"]
        MCPServer["MCP Server<br/>External Tools"]
        LangSmithAPI["LangSmith API<br/>Optional Monitoring"]
    end
    
    subgraph "State_Management" ["State Management Layer"]
        StreamProvider["StreamProvider Context<br/>Real-time Messages"]
        AgentsProvider["AgentsProvider Context<br/>Agent Discovery"]
        useConfigStore["useConfigStore<br/>Zustand Configuration"]
        nuqsURLState["nuqs URL State<br/>Navigation Parameters"]
    end
    
    ChatInterface --> StreamProvider
    AgentDashboard --> AgentsProvider
    ConfigSidebar --> useConfigStore
    AuthProvider --> SupabaseAuth
    
    StreamProvider -.->|"useStream Hook"| LangGraphPlatform
    AgentsProvider -.->|"getDeployments"| LangGraphPlatform
    RAGInterface -.->|"HTTP Requests"| LangConnectRAG
    ToolsPlayground -.->|"API Proxy /api/oap_mcp"| MCPServer
    
    useConfigStore --> nuqsURLState
    LangGraphPlatform -.->|"Optional Auth"| LangSmithAPI
```

Sources: [README.md:1-68](), [package.json:1-24]()

## Core System Components

The platform consists of several interconnected systems that work together to provide a comprehensive agent management experience:

### Agent Management System

The agent management system handles the complete lifecycle of LangGraph agents, from discovery to configuration and deployment. The system uses the `getDeployments` function to discover available agents from LangGraph Platform deployments and presents them through the `AgentsProvider` context.

```mermaid
graph LR
    getDeployments["getDeployments()<br/>lib/environment/deployments"]
    AgentsProvider["AgentsProvider<br/>Context Provider"]
    extractConfigurationsFromAgent["extractConfigurationsFromAgent()<br/>lib/ui-config"]
    
    subgraph "Agent_Schema_Processing" ["Agent Schema Processing"]
        Assistant["Assistant API<br/>client.assistants"]
        ConfigSchema["config_schema<br/>JSON Schema"]
        UIConfig["x_oap_ui_config<br/>Metadata"]
    end
    
    subgraph "Configuration_Management" ["Configuration Management"]
        ConfigurableDefaults["getConfigurableDefaults()"]
        useConfigStore["useConfigStore<br/>Zustand State"]
        ConfigurationSidebar["ConfigurationSidebar<br/>Dynamic UI"]
    end
    
    getDeployments --> AgentsProvider
    AgentsProvider --> Assistant
    Assistant --> ConfigSchema
    ConfigSchema --> extractConfigurationsFromAgent
    UIConfig --> extractConfigurationsFromAgent
    
    extractConfigurationsFromAgent --> ConfigurableDefaults
    ConfigurableDefaults --> useConfigStore
    useConfigStore --> ConfigurationSidebar
```

Sources: [apps/web/scripts/update-agents-mcp-url.ts:1-96]()

### Chat and Streaming System

The chat system provides real-time interaction with agents through WebSocket streaming. The `StreamProvider` context manages message flow and agent communication using the LangGraph SDK's `useStream` hook.

```mermaid
graph TB
    subgraph "Chat_UI_Layer" ["Chat UI Components"]
        ChatInterface["ChatInterface<br/>Main Chat Component"]
        ThreadComponent["Thread Component<br/>Message Display"]
        MessageInput["Message Input<br/>User Interaction"]
    end
    
    subgraph "Stream_Management" ["Stream Management"]
        StreamProvider["StreamProvider<br/>Context Provider"]
        useStream["useStream Hook<br/>LangGraph SDK"]
        StreamingMessages["Real-time Message Flow"]
    end
    
    subgraph "Backend_Integration" ["Backend Integration"]
        LangGraphClient["LangGraph Client<br/>WebSocket/HTTP"]
        ThreadAPI["Thread API<br/>Conversation Management"]
        AgentExecution["Agent Execution<br/>LangGraph Platform"]
    end
    
    ChatInterface --> ThreadComponent
    ThreadComponent --> MessageInput
    MessageInput --> StreamProvider
    
    StreamProvider --> useStream
    useStream --> StreamingMessages
    StreamingMessages --> LangGraphClient
    
    LangGraphClient --> ThreadAPI
    ThreadAPI --> AgentExecution
```

Sources: [README.md:13-18]()

## External Service Integration Architecture

The platform integrates with multiple external services to provide comprehensive agent capabilities:

### Service Integration Pattern

```mermaid
graph LR
    subgraph "Web_App_Core" ["Web Application Core"]
        NextJSApp["Next.js Application<br/>apps/web"]
        APIRoutes["API Routes<br/>/api/oap_mcp"]
        EnvironmentConfig["Environment Variables<br/>NEXT_PUBLIC_*"]
    end
    
    subgraph "Authentication_Layer" ["Authentication Layer"]
        SupabaseClient["Supabase Client<br/>JWT Authentication"]
        AuthContext["AuthContext<br/>Session Management"]
        LocalStorage["Local Storage<br/>API Key Storage"]
    end
    
    subgraph "Agent_Services" ["Agent Runtime Services"]
        LangGraphDeployments["LangGraph Platform<br/>Agent Deployments"]
        LangConnectServer["LangConnect Server<br/>RAG Document Management"]
        MCPServerInstance["MCP Server<br/>External Tool Execution"]
    end
    
    NextJSApp --> APIRoutes
    NextJSApp --> AuthContext
    NextJSApp --> EnvironmentConfig
    
    AuthContext --> SupabaseClient
    AuthContext --> LocalStorage
    
    APIRoutes -.->|"Proxy Requests"| MCPServerInstance
    NextJSApp -.->|"Direct REST"| LangGraphDeployments
    NextJSApp -.->|"Direct REST"| LangConnectServer
    
    SupabaseClient -.->|"OAuth Token Exchange"| MCPServerInstance
```

Sources: [README.md:46-50](), [apps/web/scripts/update-agents-mcp-url.ts:12-18]()

## Configuration and Schema System

The platform uses a sophisticated schema-driven configuration system that dynamically generates UI components based on agent metadata. This system processes LangGraph agent schemas and renders appropriate form controls.

### Schema Processing Pipeline

```mermaid
graph TD
    subgraph "Schema_Sources" ["Schema Sources"]
        LangGraphSchema["LangGraph config_schema<br/>JSON Schema"]
        MCPMetadata["MCP Tool Metadata<br/>x_oap_ui_config"]
        RAGMetadata["RAG Configuration<br/>LangConnect Schema"]
        AgentMetadata["Agent Supervision<br/>Metadata"]
    end
    
    subgraph "Processing_Functions" ["Processing Functions"]
        extractConfigurationsFromAgent["extractConfigurationsFromAgent()<br/>lib/ui-config"]
        getConfigurableDefaults["getConfigurableDefaults()<br/>Configuration Defaults"]
        SchemaProcessor["Schema Processing<br/>Dynamic UI Generation"]
    end
    
    subgraph "UI_Generation" ["UI Generation"]
        ConfigurationSidebar["ConfigurationSidebar<br/>Dynamic Form Controls"]
        AgentFormDialogs["Agent Form Dialogs<br/>Create/Edit Forms"]
        ToolsConfiguration["Tools Configuration<br/>Parameter Input"]
    end
    
    LangGraphSchema --> extractConfigurationsFromAgent
    MCPMetadata --> extractConfigurationsFromAgent
    RAGMetadata --> extractConfigurationsFromAgent
    AgentMetadata --> extractConfigurationsFromAgent
    
    extractConfigurationsFromAgent --> getConfigurableDefaults
    getConfigurableDefaults --> SchemaProcessor
    SchemaProcessor --> ConfigurationSidebar
    SchemaProcessor --> AgentFormDialogs
    SchemaProcessor --> ToolsConfiguration
```

Sources: [apps/web/scripts/update-agents-mcp-url.ts:54-89](), [README.md:63-67]()

## Development Architecture

The codebase is structured as a Turbo monorepo with TypeScript support and modern development tooling. The build system uses Yarn 3 with workspaces for managing dependencies across multiple applications.

### Repository Structure

| Component | Location | Purpose |
|-----------|----------|---------|
| Web Application | `apps/web` | Main Next.js application |
| Package Management | `package.json` | Turbo monorepo configuration |
| Development Scripts | `apps/web/scripts/` | Utility scripts for agent management |
| Configuration | `.yarnrc.yml` | Yarn workspace configuration |

The platform is designed to be deployment-flexible, working without a standalone backend server as long as LangGraph Platform deployments are configured. Optional services like RAG (LangConnect) and MCP servers can be added as needed.

Sources: [package.json:1-24](), [.yarnrc.yml:1-3](), [README.md:45-48]()

---

