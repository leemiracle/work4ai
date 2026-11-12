<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/open-agent-platform · page 3 Agent Management · fetched 2026-10-26 -->

# Agent Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/src/lib/agent-utils.ts](apps/web/src/lib/agent-utils.ts)
- [apps/web/src/providers/Agents.tsx](apps/web/src/providers/Agents.tsx)
- [apps/web/src/types/deployment.ts](apps/web/src/types/deployment.ts)

</details>



This document covers the comprehensive agent lifecycle management system in the Open Agent Platform, including agent discovery, classification, loading, and state management. The system handles multiple agent types across different deployments and provides a unified interface for managing AI agents.

For information about the agent dashboard interface, see [Agent Dashboard](#3.1). For details about agent configuration forms, see [Agent Forms and Dialogs](#3.2). For information about the chat interface with agents, see [Chat Interface](#4).

## Core Architecture

The agent management system consists of several key components that work together to provide agent discovery, classification, and state management across multiple deployments.

```mermaid
graph TD
    subgraph "Agent Management Architecture"
        AgentsProvider["AgentsProvider Context"]
        useAgentsContext["useAgentsContext Hook"]
        getAgents["getAgents Function"]
        getOrCreateDefaultAssistants["getOrCreateDefaultAssistants"]
    end
    
    subgraph "Agent Classification"
        isUserCreatedDefaultAssistant["isUserCreatedDefaultAssistant"]
        isSystemCreatedDefaultAssistant["isSystemCreatedDefaultAssistant"]
        isPrimaryAssistant["isPrimaryAssistant"]
        groupAgentsByGraphs["groupAgentsByGraphs"]
    end
    
    subgraph "External Dependencies"
        LangGraphSDK["LangGraph SDK Client"]
        createClient["createClient"]
        getDeployments["getDeployments"]
        useAuthContext["useAuthContext"]
        extractConfigurationsFromAgent["extractConfigurationsFromAgent"]
    end
    
    subgraph "Data Sources"
        DefaultAssistantsAPI["/langgraph/defaults API"]
        AssistantsSearchAPI["client.assistants.search"]
        ConfigSchemaAPI["getAgentConfigSchema"]
    end
    
    AgentsProvider --> getAgents
    getAgents --> getOrCreateDefaultAssistants
    getAgents --> groupAgentsByGraphs
    getAgents --> extractConfigurationsFromAgent
    
    getAgents --> createClient
    createClient --> LangGraphSDK
    LangGraphSDK --> AssistantsSearchAPI
    
    getOrCreateDefaultAssistants --> DefaultAssistantsAPI
    
    groupAgentsByGraphs --> isUserCreatedDefaultAssistant
    groupAgentsByGraphs --> isSystemCreatedDefaultAssistant
    
    AgentsProvider --> useAuthContext
    AgentsProvider --> getDeployments
    
    useAgentsContext --> AgentsProvider
```

The system provides a React context-based architecture for managing agent state across the application, with automatic loading, classification, and configuration detection.

**Sources:** [apps/web/src/providers/Agents.tsx:1-245](), [apps/web/src/lib/agent-utils.ts:1-172]()

## Agent Types and Classification

The platform distinguishes between several types of agents based on their origin, purpose, and role within the system.

| Agent Type | Identifier Function | Description | Visibility |
|------------|-------------------|-------------|------------|
| User-Created Default | `isUserCreatedDefaultAssistant` | Default agent created by users for a specific graph | Visible to users |
| System-Created Default | `isSystemCreatedDefaultAssistant` | Platform-generated default agents | Hidden from users |
| Primary Assistant | `isPrimaryAssistant` | The main default assistant across all graphs | Special designation |

```mermaid
graph TD
    subgraph "Agent Classification System"
        AgentInput["Agent or Assistant"]
        
        UserDefault["User-Created Default<br/>metadata._x_oap_is_default = true"]
        SystemDefault["System-Created Default<br/>metadata.created_by = 'system'"]
        Primary["Primary Assistant<br/>metadata._x_oap_is_primary = true"]
        Regular["Regular Agent"]
    end
    
    AgentInput --> isUserCreatedDefaultAssistant
    AgentInput --> isSystemCreatedDefaultAssistant  
    AgentInput --> isPrimaryAssistant
    
    isUserCreatedDefaultAssistant -->|true| UserDefault
    isSystemCreatedDefaultAssistant -->|true| SystemDefault
    isPrimaryAssistant -->|true| Primary
    isUserCreatedDefaultAssistant -->|false| Regular
```

The classification system uses metadata fields to determine agent types and controls their visibility and behavior in the user interface.

**Sources:** [apps/web/src/lib/agent-utils.ts:18-55]()

## Agent Discovery and Loading Process

The agent loading process involves fetching agents from multiple deployments, combining different assistant types, and extracting configuration capabilities.

```mermaid
sequenceDiagram
    participant AgentsProvider
    participant getAgents
    participant getOrCreateDefaultAssistants
    participant LangGraphClient
    participant extractConfigurationsFromAgent
    
    AgentsProvider->>getAgents: Load agents for deployments
    
    loop For each deployment
        getAgents->>getOrCreateDefaultAssistants: Fetch default assistants
        getOrCreateDefaultAssistants->>LangGraphClient: GET /langgraph/defaults
        LangGraphClient-->>getOrCreateDefaultAssistants: Default assistants
        
        getAgents->>LangGraphClient: client.assistants.search()
        LangGraphClient-->>getAgents: User assistants
        
        getAgents->>getAgents: Merge assistants in Map
        getAgents->>groupAgentsByGraphs: Group by graph_id
        
        loop For each graph group
            getAgents->>extractConfigurationsFromAgent: Extract config schema
            extractConfigurationsFromAgent-->>getAgents: Supported configs
        end
    end
    
    getAgents-->>AgentsProvider: Combined agents array
```

The loading process handles multiple deployments concurrently and ensures proper merging of default and user-created assistants while avoiding duplicates.

**Sources:** [apps/web/src/providers/Agents.tsx:67-146](), [apps/web/src/providers/Agents.tsx:26-65]()

## Agent State Management

The `AgentsProvider` component manages global agent state using React Context and provides methods for loading and refreshing agent data.

```mermaid
graph LR
    subgraph "AgentsProvider State Management"
        AgentsState["agents: Agent[]"]
        LoadingState["loading: boolean"]
        RefreshLoadingState["refreshAgentsLoading: boolean"]
        RefreshFunction["refreshAgents: () => Promise<void>"]
    end
    
    subgraph "State Updates"
        InitialLoad["Initial Load on Mount"]
        RefreshAction["Manual Refresh Action"]
        AuthChange["Auth Token Change"]
    end
    
    subgraph "Dependencies"
        useAuthContext["useAuthContext"]
        useAgents["useAgents Hook"]
        getDeployments["getDeployments"]
    end
    
    InitialLoad --> AgentsState
    RefreshAction --> RefreshFunction
    RefreshFunction --> AgentsState
    AuthChange --> InitialLoad
    
    AgentsState --> useAuthContext
    AgentsState --> useAgents
    AgentsState --> getDeployments
```

The context provides reactive state management with automatic loading on authentication changes and manual refresh capabilities for real-time updates.

**Sources:** [apps/web/src/providers/Agents.tsx:148-168](), [apps/web/src/providers/Agents.tsx:170-243]()

## Agent Grouping and Organization

Agents are organized by their `graph_id` and sorted within groups to prioritize default agents and recent updates.

```mermaid
graph TD
    subgraph "Agent Organization System"
        AllAgents["All Agents Array"]
        groupAgentsByGraphs["groupAgentsByGraphs"]
        AgentGroups["Agent Groups by graph_id"]
        sortAgentGroup["sortAgentGroup"]
        SortedGroups["Sorted Agent Groups"]
    end
    
    subgraph "Sorting Logic"
        DefaultFirst["Default Agents First"]
        UpdatedAtDesc["Sort by updated_at DESC"]
        ValidateTime["Handle Invalid Dates"]
    end
    
    AllAgents --> groupAgentsByGraphs
    groupAgentsByGraphs --> AgentGroups
    AgentGroups --> sortAgentGroup
    
    sortAgentGroup --> DefaultFirst
    sortAgentGroup --> UpdatedAtDesc
    sortAgentGroup --> ValidateTime
    
    sortAgentGroup --> SortedGroups
```

The grouping system ensures that related agents (same graph) are organized together, with default agents prominently displayed and recent updates prioritized.

**Sources:** [apps/web/src/lib/agent-utils.ts:104-117](), [apps/web/src/lib/agent-utils.ts:76-97]()

## Configuration Schema Integration

The agent management system integrates with the configuration system to determine which features each agent supports based on its schema.

```mermaid
graph LR
    subgraph "Configuration Detection"
        AgentSchema["Agent Config Schema"]
        extractConfigurationsFromAgent["extractConfigurationsFromAgent"]
        ConfigTypes["Configuration Types"]
    end
    
    subgraph "Supported Configurations"
        ToolsConfig["tools"]
        RAGConfig["rag"] 
        SupervisorConfig["supervisor"]
    end
    
    subgraph "Agent Enhancement"
        BaseAgent["Base Agent Data"]
        EnhancedAgent["Agent + supportedConfigs"]
    end
    
    AgentSchema --> extractConfigurationsFromAgent
    extractConfigurationsFromAgent --> ConfigTypes
    
    ConfigTypes --> ToolsConfig
    ConfigTypes --> RAGConfig
    ConfigTypes --> SupervisorConfig
    
    BaseAgent --> EnhancedAgent
    ConfigTypes --> EnhancedAgent
```

Each agent is enhanced with a `supportedConfigs` array that indicates which configuration panels should be available in the user interface.

**Sources:** [apps/web/src/providers/Agents.tsx:114-138]()

## API Key Management Integration

The system includes validation for deployments that require API keys and provides user warnings when keys are missing.

```mermaid
graph TD
    subgraph "API Key Validation System"
        Deployment["Deployment Config"]
        requiresApiKeys["requiresApiKeys: boolean"]
        hasApiKeys["User API Keys Status"]
        requiresApiKeysButNotSet["requiresApiKeysButNotSet"]
    end
    
    subgraph "User Experience"
        checkApiKeysWarning["checkApiKeysWarning"]
        ToastWarning["Toast Warning Message"]
        SettingsLink["Link to Settings Page"]
    end
    
    subgraph "Deployment Configuration"
        requiresApiKeysFlag["requiresApiKeys: boolean"]
        apiKeysRequiredMessage["apiKeysRequiredMessage: string"]
    end
    
    Deployment --> requiresApiKeys
    requiresApiKeys --> requiresApiKeysButNotSet
    hasApiKeys --> requiresApiKeysButNotSet
    
    requiresApiKeysButNotSet --> checkApiKeysWarning
    checkApiKeysWarning --> ToastWarning
    ToastWarning --> SettingsLink
    
    requiresApiKeysFlag --> Deployment
    apiKeysRequiredMessage --> ToastWarning
```

The validation system helps ensure users are properly configured before attempting to use agents that require external API access.

**Sources:** [apps/web/src/lib/agent-utils.ts:125-171](), [apps/web/src/types/deployment.ts:30-37]()

---

