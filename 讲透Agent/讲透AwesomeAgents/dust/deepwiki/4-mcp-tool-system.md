<!-- source: DeepWiki mcp.deepwiki.com · repo dust-tt/dust · page 4 MCP Tool System · fetched 2026-10-26 -->

# MCP Tool System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [front-api/routes/w/[wId]/assistant/skills/[sId]/suggestions.test.ts](front-api/routes/w/[wId]/assistant/skills/[sId]/suggestions.test.ts)
- [front-api/routes/w/[wId]/mcp/[serverId]/index.test.ts](front-api/routes/w/[wId]/mcp/[serverId]/index.test.ts)
- [front-api/routes/w/[wId]/mcp/[serverId]/index.ts](front-api/routes/w/[wId]/mcp/[serverId]/index.ts)
- [front-api/routes/w/[wId]/mcp/[serverId]/sync.test.ts](front-api/routes/w/[wId]/mcp/[serverId]/sync.test.ts)
- [front-api/routes/w/[wId]/mcp/connections/[connectionType]/[cId]/index.test.ts](front-api/routes/w/[wId]/mcp/connections/[connectionType]/[cId]/index.test.ts)
- [front-api/routes/w/[wId]/mcp/connections/[connectionType]/[cId]/index.ts](front-api/routes/w/[wId]/mcp/connections/[connectionType]/[cId]/index.ts)
- [front-api/routes/w/[wId]/mcp/views/[viewId]/index.test.ts](front-api/routes/w/[wId]/mcp/views/[viewId]/index.test.ts)
- [front-api/routes/w/[wId]/mcp/views/[viewId]/index.ts](front-api/routes/w/[wId]/mcp/views/[viewId]/index.ts)
- [front-api/routes/w/[wId]/me/approvals.ts](front-api/routes/w/[wId]/me/approvals.ts)
- [front-api/routes/w/[wId]/members/index.test.ts](front-api/routes/w/[wId]/members/index.test.ts)
- [front-api/routes/w/[wId]/skills/[sId]/history/index.test.ts](front-api/routes/w/[wId]/skills/[sId]/history/index.test.ts)
- [front-api/routes/w/[wId]/skills/[sId]/restore.test.ts](front-api/routes/w/[wId]/skills/[sId]/restore.test.ts)
- [front-api/routes/w/[wId]/skills/reinforcement_daily_spend.test.ts](front-api/routes/w/[wId]/skills/reinforcement_daily_spend.test.ts)
- [front-api/routes/w/[wId]/skills/reinforcement_spend.test.ts](front-api/routes/w/[wId]/skills/reinforcement_spend.test.ts)
- [front-api/routes/w/[wId]/spaces/[spaceId]/mcp/available.test.ts](front-api/routes/w/[wId]/spaces/[spaceId]/mcp/available.test.ts)
- [front-api/routes/w/[wId]/spaces/[spaceId]/mcp_views/index.test.ts](front-api/routes/w/[wId]/spaces/[spaceId]/mcp_views/index.test.ts)
- [front-api/routes/w/[wId]/spaces/[spaceId]/webhook_source_views/index.test.ts](front-api/routes/w/[wId]/spaces/[spaceId]/webhook_source_views/index.test.ts)
- [front/lib/actions/action_output_limits.ts](front/lib/actions/action_output_limits.ts)
- [front/lib/actions/mcp.ts](front/lib/actions/mcp.ts)
- [front/lib/actions/mcp_actions.test.ts](front/lib/actions/mcp_actions.test.ts)
- [front/lib/actions/mcp_actions.ts](front/lib/actions/mcp_actions.ts)
- [front/lib/actions/mcp_authentication.test.ts](front/lib/actions/mcp_authentication.test.ts)
- [front/lib/actions/mcp_authentication.ts](front/lib/actions/mcp_authentication.ts)
- [front/lib/actions/mcp_execution.test.ts](front/lib/actions/mcp_execution.test.ts)
- [front/lib/actions/mcp_execution.ts](front/lib/actions/mcp_execution.ts)
- [front/lib/actions/mcp_internal_actions/exit_events.test.ts](front/lib/actions/mcp_internal_actions/exit_events.test.ts)
- [front/lib/actions/mcp_internal_actions/exit_events.ts](front/lib/actions/mcp_internal_actions/exit_events.ts)
- [front/lib/actions/mcp_internal_actions/output_schemas.ts](front/lib/actions/mcp_internal_actions/output_schemas.ts)
- [front/lib/actions/mcp_metadata.ts](front/lib/actions/mcp_metadata.ts)
- [front/lib/actions/mcp_metadata_extraction.ts](front/lib/actions/mcp_metadata_extraction.ts)
- [front/lib/actions/mcp_oauth_provider.ts](front/lib/actions/mcp_oauth_provider.ts)
- [front/lib/actions/mcp_utils.ts](front/lib/actions/mcp_utils.ts)
- [front/lib/actions/types/index.ts](front/lib/actions/types/index.ts)
- [front/lib/api/files/action_output_fs/index.ts](front/lib/api/files/action_output_fs/index.ts)
- [front/lib/api/files/action_output_fs/naming.ts](front/lib/api/files/action_output_fs/naming.ts)
- [front/lib/api/files/action_output_fs/registry.ts](front/lib/api/files/action_output_fs/registry.ts)
- [front/lib/api/mcp/error.ts](front/lib/api/mcp/error.ts)
- [front/lib/api/mcp/run_tool.ts](front/lib/api/mcp/run_tool.ts)
- [front/lib/api/mcp/views.ts](front/lib/api/mcp/views.ts)
- [front/lib/api/mcp_oauth_prerequisites.ts](front/lib/api/mcp_oauth_prerequisites.ts)
- [front/lib/api/poke/plugins/mcp_server_views/update-mcp-url.ts](front/lib/api/poke/plugins/mcp_server_views/update-mcp-url.ts)
- [front/lib/resources/internal_mcp_server_in_memory_resource.ts](front/lib/resources/internal_mcp_server_in_memory_resource.ts)
- [front/lib/resources/mcp_server_connection_resource.test.ts](front/lib/resources/mcp_server_connection_resource.test.ts)
- [front/lib/resources/mcp_server_connection_resource.ts](front/lib/resources/mcp_server_connection_resource.ts)
- [front/lib/resources/mcp_server_view_resource.test.ts](front/lib/resources/mcp_server_view_resource.test.ts)
- [front/lib/resources/mcp_server_view_resource.ts](front/lib/resources/mcp_server_view_resource.ts)
- [front/lib/resources/remote_mcp_servers_resource.test.ts](front/lib/resources/remote_mcp_servers_resource.test.ts)
- [front/lib/resources/remote_mcp_servers_resource.ts](front/lib/resources/remote_mcp_servers_resource.ts)
- [front/temporal/agent_loop/activities/run_tool.ts](front/temporal/agent_loop/activities/run_tool.ts)
- [front/types/assistant/agent.ts](front/types/assistant/agent.ts)
- [front/types/assistant/agent_run.ts](front/types/assistant/agent_run.ts)

</details>



The MCP (Model Context Protocol) Tool System enables agents to execute external tools and integrations through a standardized protocol. This system manages tool discovery, configuration, approval workflows, and execution across three distinct server types: internal servers with 40+ built-in tools, client-side servers for desktop integration, and remote servers for workspace-configured external services.

For information about the agent execution loop that orchestrates tool calls, see [Agent Execution and Temporal Workflows](#3.3). For LLM integration details, see [Prompt Construction and LLM Integration](#3.4).

## Architecture Overview

The MCP Tool System consists of multiple layers: server registration and configuration, tool discovery and metadata extraction, approval and validation workflows, and execution with progress streaming.

```mermaid
graph TB
    subgraph "Server Types"
        InternalServers["Internal MCP Servers<br/>INTERNAL_MCP_SERVERS<br/>40+ built-in tools"]
        ClientServers["Client-Side MCP Servers<br/>Desktop integration<br/>via WebSocket"]
        RemoteServers["Remote MCP Servers<br/>Workspace-configured<br/>external services"]
    end
    
    subgraph "Configuration Layer"
        ServerConfig["MCPServerViewResource<br/>mcpServerViewId"]
        ToolConfig["MCPToolConfigurationType<br/>inputSchema, permission"]
        InternalDef["INTERNAL_MCP_SERVERS<br/>front/lib/actions/mcp_internal_actions/constants.ts"]
    end
    
    subgraph "Tool Discovery"
        ListTools["getAvailableMCPTools<br/>front/lib/actions/mcp_actions.ts"]
        MetadataExtract["extractMetadataFromTools<br/>front/lib/actions/mcp_metadata.ts"]
        ToolSpecs["buildToolSpecification<br/>front/lib/actions/mcp_metadata_extraction.ts"]
    end
    
    subgraph "Execution Pipeline"
        StatusCheck["getExecutionStatusFromConfig<br/>front/lib/actions/tool_status.ts"]
        CreateAction["createMCPAction<br/>front/lib/api/mcp/create_mcp.ts"]
        CallTool["tryCallMCPTool<br/>front/lib/api/mcp/run_tool.ts"]
        StreamProgress["ToolNotificationEvent<br/>Progress streaming"]
    end
    
    InternalServers --> InternalDef
    ClientServers --> ServerConfig
    RemoteServers --> ServerConfig
    
    InternalDef --> ListTools
    ServerConfig --> ListTools
    ListTools --> MetadataExtract
    MetadataExtract --> ToolConfig
    ToolConfig --> ToolSpecs
    
    ToolSpecs --> StatusCheck
    StatusCheck --> CreateAction
    CreateAction --> CallTool
    CallTool --> StreamProgress
```

**Sources:** [front/lib/actions/mcp_internal_actions/constants.ts:215-1006](), [front/lib/actions/mcp.ts:1-323](), [front/lib/actions/mcp_actions.ts:1-900](), [front/lib/actions/mcp_metadata.ts:56-61](), [front/lib/actions/mcp_metadata_extraction.ts:1-33](), [front/lib/actions/tool_status.ts:1-228](), [front/lib/api/mcp/create_mcp.ts:1-58](), [front/lib/api/mcp/run_tool.ts:1-170]()

## Server Types and Registration

The system supports three distinct server types, each with its own registration and connection mechanism. For detailed information on each server type, see [MCP Server Architecture](#4.1).

### Internal MCP Servers

Internal servers are defined in `INTERNAL_MCP_SERVERS` with stable IDs, availability settings, and tool configurations. Each server has metadata including `tools_stakes`, `tools_retry_policies`, and `tools_arguments_requiring_approval`.

```mermaid
graph LR
    subgraph "Internal Server Definition"
        ServerEntry["INTERNAL_MCP_SERVERS<br/>front/lib/actions/mcp_internal_actions/constants.ts"]
        Availability["MCPServerAvailability<br/>auto/manual/auto_hidden_builder"]
        ToolStakes["tools_stakes<br/>Record<toolName, MCPToolStakeLevelType>"]
        RetryPolicy["tools_retry_policies<br/>default: retry_on_interrupt"]
    end
    
    subgraph "Registration"
        GetServer["getInternalMCPServer<br/>front/lib/actions/mcp_internal_actions/constants.ts"]
        ServerImpl["Server implementation<br/>githubServer, searchServer, etc."]
    end
    
    subgraph "Examples"
        Search["search (id: 1006)<br/>availability: auto<br/>retry_on_interrupt"]
        GitHub["github (id: 1)<br/>availability: manual<br/>OAuth required"]
        WebBrowse["web_search_&_browse (id: 5)<br/>availability: auto<br/>retry_on_interrupt"]
    end
    
    ServerEntry --> Availability
    ServerEntry --> ToolStakes
    ServerEntry --> RetryPolicy
    ServerEntry --> GetServer
    GetServer --> ServerImpl
    
    ServerEntry --> Search
    ServerEntry --> GitHub
    ServerEntry --> WebBrowse
```

**Sources:** [front/lib/actions/mcp_internal_actions/constants.ts:215-1006](), [front/lib/actions/mcp_internal_actions/servers/index.ts:100-249]()

### Client-Side MCP Servers

Client-side servers enable desktop integration through a registration and heartbeat protocol. For details, see [MCP Server Architecture](#4.1).

```mermaid
sequenceDiagram
    participant Desktop as Desktop Client
    participant API as POST /register-mcp<br/>front/pages/api/v1/w/[wId]/assistant/mcp/register.ts
    participant Registry as ClientSideMCPServerRegistry
    participant Store as Redis Store<br/>TTL: 20 minutes
    
    Desktop->>API: PublicRegisterMCPRequestBody<br/>{serverId, serverInfo, tools}
    API->>Registry: register(serverId, metadata)
    Registry->>Store: Set with TTL
    API-->>Desktop: RegisterMCPResponseType<br/>{success}
    
    loop Every 15 minutes
        Desktop->>API: POST /heartbeat-mcp<br/>{serverId}
        API->>Registry: updateHeartbeat(serverId)
        Registry->>Store: Refresh TTL
        API-->>Desktop: {success}
    end
    
    Note over Desktop,Store: If no heartbeat for 20min,<br/>server expires
```

**Sources:** [front/pages/api/v1/w/[wId]/assistant/mcp/register.ts:1-100](), [front/lib/api/actions/mcp/client_side_registry.ts:1-200](), [sdks/js/src/index.ts:800-850]()

### Remote MCP Servers

Remote servers are configured at the workspace level with connection parameters stored in `MCPServerViewResource`. For details, see [MCP Server Architecture](#4.1).

```mermaid
graph TB
    subgraph "Configuration"
        MCPView["MCPServerViewResource<br/>mcpServerViewId, spaceId"]
        OAuth["OAuthConnectionResource<br/>provider, credentials"]
        RemoteMetadata["RemoteMCPServerToolMetadataResource<br/>Per-tool settings"]
    end
    
    subgraph "Connection"
        ConnectParams["ServerSideMCPConnectionParams<br/>{params, agentLoopContext}"]
        ConnectFn["connectToMCPServer<br/>front/lib/actions/mcp_metadata.ts"]
        MCPClient["Client instance<br/>callTool, listTools"]
    end
    
    subgraph "Tool Execution"
        RunTool["tryCallMCPTool<br/>front/lib/api/mcp/run_tool.ts"]
        AuthCheck["MCPServerPersonalAuthenticationRequiredError<br/>If auth missing"]
    end
    
    MCPView --> OAuth
    MCPView --> RemoteMetadata
    MCPView --> ConnectParams
    ConnectParams --> ConnectFn
    ConnectFn --> MCPClient
    ConnectFn --> AuthCheck
    MCPClient --> RunTool
```

**Sources:** [front/lib/resources/mcp_server_view_resource.ts:1-400](), [front/lib/actions/mcp_metadata.ts:1-500](), [front/lib/actions/mcp_authentication.ts:1-179](), [front/lib/api/mcp/run_tool.ts:1-170]()

## Tool Discovery and Configuration

Tool discovery aggregates tools from all available servers and enriches them with metadata about permissions, retry policies, and approval requirements. For detailed information, see [Tool Discovery Pipeline](#4.2).

```mermaid
graph TB
    subgraph "Discovery Process"
        GetAvailable["getAvailableMCPTools<br/>front/lib/actions/mcp_actions.ts"]
        FilterServers["Filter by space access<br/>& feature flags"]
        ConnectServers["Connect to each server<br/>listTools()"]
    end
    
    subgraph "Tool Processing"
        ExtractMeta["extractMetadataFromTools<br/>front/lib/actions/mcp_metadata.ts"]
        DedupeTools["Deduplicate tools<br/>by toolServerId + originalName"]
        DisambiguateNames["Disambiguate conflicts<br/>Append server name"]
    end
    
    subgraph "Tool Configuration Types"
        ServerSide["ServerSideMCPToolConfigurationType<br/>{mcpServerViewId, dataSources,<br/>childAgentId, timeFrame}"]
        ClientSide["ClientSideMCPToolConfigurationType<br/>{clientSideMcpServerId}"]
        Common["Common fields<br/>{name, inputSchema, permission,<br/>originalName, mcpServerName}"]
    end
    
    subgraph "Output"
        ToolConfigs["MCPToolConfigurationType[]<br/>Enriched with metadata"]
        BuildSpecs["buildToolSpecification<br/>front/lib/actions/mcp_metadata_extraction.ts"]
        LLMSchema["Function schemas for LLM<br/>hideInternalConfiguration"]
    end
    
    GetAvailable --> FilterServers
    FilterServers --> ConnectServers
    ConnectServers --> ExtractMeta
    ExtractMeta --> DedupeTools
    DedupeTools --> DisambiguateNames
    
    DisambiguateNames --> ServerSide
    DisambiguateNames --> ClientSide
    ServerSide --> Common
    ClientSide --> Common
    
    Common --> ToolConfigs
    ToolConfigs --> BuildSpecs
    BuildSpecs --> LLMSchema
```

**Sources:** [front/lib/actions/mcp_actions.ts:600-900](), [front/lib/actions/mcp_metadata_extraction.ts:1-33](), [front/lib/actions/mcp.ts:240-257](), [front/lib/actions/mcp_metadata.ts:56-61]()

### Tool Naming and Disambiguation

Tools are prefixed with their server name and disambiguated when conflicts occur.

```mermaid
graph LR
    subgraph "Tool Naming"
        OriginalName["Original tool name<br/>e.g., 'search'"]
        Prefix["Add server prefix<br/>TOOL_NAME_SEPARATOR '__'"]
        FullName["Full name<br/>'search__semantic_search'"]
    end
    
    subgraph "Disambiguation"
        CheckConflict["Check for name conflicts<br/>in tool list"]
        AppendServer["Append server name<br/>if conflict exists"]
        FinalName["Final tool name<br/>'search__semantic_search__server1'"]
    end
    
    subgraph "Storage"
        ToolConfig["MCPToolConfigurationType<br/>{name, originalName, mcpServerName}"]
        FunctionCall["Agent function call<br/>Uses full prefixed name"]
    end
    
    OriginalName --> Prefix
    Prefix --> FullName
    FullName --> CheckConflict
    CheckConflict --> AppendServer
    AppendServer --> FinalName
    FinalName --> ToolConfig
    ToolConfig --> FunctionCall
```

**Sources:** [front/lib/actions/constants.ts:16-18](), [front/lib/actions/mcp_actions.ts:700-800]()

## Tool Execution Pipeline

Tool execution follows a multi-stage pipeline with status determination, action creation, and execution with progress streaming. For detailed information, see [Tool Execution and Authentication](#4.3).

```mermaid
graph TB
    subgraph "Status Determination"
        InputContext["ToolInputContext<br/>{inputs, agentConfig, user}"]
        GetStatus["getExecutionStatusFromConfig<br/>front/lib/actions/tool_status.ts"]
        CheckStake["Check stake level<br/>never_ask/low/medium/high"]
        CheckApproval["Check if args require approval<br/>argumentsRequiringApproval"]
    end
    
    subgraph "Status Types"
        Ready["ready_allowed_implicitly<br/>Execute immediately"]
        BlockedVal["blocked_validation_required<br/>Needs user approval"]
        BlockedAuth["blocked_authentication_required<br/>OAuth connection needed"]
        BlockedFile["blocked_file_authorization_required<br/>File access needed"]
        Restricted["agent_restricted_by_space_usage<br/>Agent uses restricted spaces"]
    end
    
    subgraph "Action Creation"
        CreateMCP["createMCPAction<br/>front/lib/api/mcp/create_mcp.ts"]
        StepContent["AgentStepContentResource<br/>type: function_call"]
        ActionResource["AgentMCPActionResource<br/>status, params, stepContentId"]
    end
    
    subgraph "Execution"
        TryCall["tryCallMCPTool<br/>front/lib/api/mcp/run_tool.ts"]
        Connect["connectToMCPServer<br/>front/lib/actions/mcp_metadata.ts"]
        CallTool["mcpClient.callTool<br/>{name, arguments}"]
        StreamEvents["Yield ToolNotificationEvent<br/>Progress updates"]
        Result["CallToolResult<br/>content, isError"]
    end
    
    InputContext --> GetStatus
    GetStatus --> CheckStake
    CheckStake --> CheckApproval
    CheckApproval --> Ready
    CheckApproval --> BlockedVal
    CheckApproval --> BlockedAuth
    CheckApproval --> BlockedFile
    CheckApproval --> Restricted
    
    Ready --> CreateMCP
    CreateMCP --> StepContent
    CreateMCP --> ActionResource
    ActionResource --> TryCall
    TryCall --> Connect
    Connect --> CallTool
    CallTool --> StreamEvents
    CallTool --> Result
```

**Sources:** [front/lib/actions/tool_status.ts:100-228](), [front/lib/api/mcp/create_mcp.ts:1-58](), [front/lib/api/mcp/run_tool.ts:1-170](), [front/lib/actions/mcp_metadata.ts:56-61]()

### Action Status Lifecycle

Action statuses transition through various states during execution.

```mermaid
stateDiagram-v2
    [*] --> ready_allowed_implicitly: Stake: never_ask/low
    [*] --> blocked_validation_required: Stake: medium/high<br/>or args require approval
    [*] --> blocked_authentication_required: OAuth connection missing
    [*] --> blocked_file_authorization_required: File access needed
    [*] --> agent_restricted_by_space_usage: Agent uses restricted spaces
    
    ready_allowed_implicitly --> running: Execute immediately
    
    blocked_validation_required --> ready_allowed_explicitly: User approves
    blocked_validation_required --> denied: User rejects
    
    blocked_authentication_required --> ready_allowed_explicitly: User connects OAuth
    blocked_file_authorization_required --> ready_allowed_explicitly: User grants file access
    
    ready_allowed_explicitly --> running: Execute after approval
    
    running --> succeeded: Tool returns success
    running --> errored: Tool returns error
    running --> cancelled: User/system cancels
    
    succeeded --> [*]
    errored --> [*]
    denied --> [*]
    cancelled --> [*]
```

**Sources:** [front/lib/actions/statuses.ts:1-83](), [front/lib/actions/tool_status.ts:1-228](), [front/lib/resources/agent_mcp_action_resource.ts:1-700]()

## Approval and Validation System

The approval system enables user control over tool execution through a validation workflow. For detailed information, see [Tool Execution and Authentication](#4.3).

```mermaid
sequenceDiagram
    participant Agent as Agent Loop
    participant CreateAction as createToolActionsActivity
    participant Status as getExecutionStatusFromConfig
    participant Publish as publishConversationRelatedEvent
    participant User as User Approval UI
    participant Validate as validateAction API
    participant Resume as Agent Loop Resume
    
    Agent->>CreateAction: Create tool actions
    CreateAction->>Status: Determine status
    Status-->>CreateAction: blocked_validation_required
    CreateAction->>Publish: MCPApproveExecutionEvent<br/>{actionId, inputs, stake, metadata}
    Publish-->>User: Display approval request
    
    User->>Validate: POST validate-action<br/>{actionId, approvalState}
    Validate->>AgentMCPActionResource: Update status<br/>ready_allowed_explicitly/denied
    
    alt Approved
        Validate->>Resume: Resume workflow<br/>continueAsNew if needed
        Resume->>Agent: Re-execute step
    else Rejected
        Validate-->>User: Action denied
    end
    
    alt Always Approve
        User->>Validate: approvalState: always_approved
        Validate->>UserToolApproval: Store approval<br/>{userId, agentConfigId, toolServerId, args}
        Note over Validate: Future calls auto-approved<br/>for this arg combination
    end
```

**Sources:** [front/lib/api/assistant/conversation/validate_actions.ts:1-300](), [front/temporal/agent_loop/lib/create_tool_actions.ts:1-200](), [front/pages/api/v1/w/[wId]/assistant/conversations/[cId]/messages/[mId]/validate-action.ts:1-150]()

### Argument-Level Approval

For medium-stake tools, specific arguments can require approval (e.g., email recipients).

```mermaid
graph TB
    subgraph "Tool Configuration"
        ArgsConfig["tools_arguments_requiring_approval<br/>Record<toolName, argNames[]>"]
        Example["gmail.send_mail<br/>requires approval for: ['to']"]
    end
    
    subgraph "Status Check"
        ExtractArgs["extractArgRequiringApprovalValues<br/>front/lib/actions/tool_status.ts"]
        CheckStored["Check UserToolApproval table<br/>Has user approved these args?"]
        Decision{Previously<br/>approved?}
    end
    
    subgraph "Outcomes"
        AutoApprove["ready_allowed_implicitly<br/>Use stored approval"]
        RequireApproval["blocked_validation_required<br/>Show approval UI"]
    end
    
    ArgsConfig --> ExtractArgs
    Example --> ExtractArgs
    ExtractArgs --> CheckStored
    CheckStored --> Decision
    Decision -->|Yes| AutoApprove
    Decision -->|No| RequireApproval
```

**Sources:** [front/lib/actions/tool_status.ts:228](), [front/lib/actions/mcp_internal_actions/constants.ts:350-400](), [front/lib/models/agent/actions/user_tool_approval.ts:1-100]()

## Integration with Agent Loop

The MCP Tool System integrates tightly with the agent loop workflow orchestrated by Temporal.

```mermaid
graph TB
    subgraph "Agent Loop Workflow"
        RunModel["runModelAndCreateActionsActivity<br/>Generate function calls"]
        ParseOutput["Parse LLM output<br/>Extract tool calls"]
        CreateActions["createToolActionsActivity<br/>Create MCP actions"]
    end
    
    subgraph "Status Branching"
        CheckApproval{Any action needs<br/>approval?}
        BlockedActions["Store blocked actions<br/>Exit workflow"]
        ReadyActions["All actions ready<br/>Continue execution"]
    end
    
    subgraph "Tool Execution"
        RunToolsParallel["Promise.all<br/>Execute tools in parallel"]
        RunToolActivity["runToolActivity<br/>front/temporal/agent_loop/activities/run_tool.ts"]
        TryCallMCP["tryCallMCPTool<br/>front/lib/api/mcp/run_tool.ts"]
        StoreResults["Store action outputs<br/>AgentMCPActionOutputItemModel"]
    end
    
    subgraph "Continuation"
        DeferredEvents["Collect deferred events"]
        PublishEvents["publishDeferredEventsActivity<br/>After all tools complete"]
        NextStep["Continue to next step<br/>or complete"]
    end
    
    RunModel --> ParseOutput
    ParseOutput --> CreateActions
    CreateActions --> CheckApproval
    CheckApproval -->|Yes| BlockedActions
    CheckApproval -->|No| ReadyActions
    ReadyActions --> RunToolsParallel
    RunToolsParallel --> RunToolActivity
    RunToolActivity --> TryCallMCP
    TryCallMCP --> StoreResults
    StoreResults --> DeferredEvents
    DeferredEvents --> PublishEvents
    PublishEvents --> NextStep
```

**Sources:** [front/temporal/agent_loop/workflows.ts:1-350](), [front/temporal/agent_loop/activities/run_tool.ts:1-250](), [front/temporal/agent_loop/lib/create_tool_actions.ts:1-200](), [front/lib/api/mcp/run_tool.ts:1-170]()

### Retry Policies

Tools can have different retry policies for handling interruptions.

```mermaid
graph LR
    subgraph "Retry Policy Types"
        NoRetry["no_retry<br/>Fail immediately<br/>maximumAttempts: 1"]
        RetryInterrupt["retry_on_interrupt<br/>Retry on worker restart<br/>maximumAttempts: 3"]
        DefaultPolicy["DEFAULT_MCP_TOOL_RETRY_POLICY<br/>= no_retry"]
    end
    
    subgraph "Configuration"
        ServerLevel["Server-level default<br/>INTERNAL_MCP_SERVERS[name].tools_retry_policies"]
        ToolLevel["Tool-level override<br/>getRetryPolicyFromToolConfiguration"]
    end
    
    subgraph "Temporal Activity"
        ProxyRetry["runRetryableToolActivity<br/>retry_on_interrupt tools"]
        ProxyNoRetry["runToolActivity<br/>no_retry tools"]
    end
    
    ServerLevel --> ToolLevel
    ToolLevel --> NoRetry
    ToolLevel --> RetryInterrupt
    NoRetry --> ProxyNoRetry
    RetryInterrupt --> ProxyRetry
```

**Sources:** [front/lib/api/mcp.ts:1-100](), [front/temporal/agent_loop/workflows.ts:70-88](), [front/lib/actions/constants.ts:1-50]()

## Tool Output and Progress Streaming

Tool execution streams progress notifications and final results back to the client.

```mermaid
sequenceDiagram
    participant Tool as Tool Execution
    participant Progress as Progress Notifications
    participant EventEmitter as EventEmitter
    participant Stream as notificationStream<br/>AsyncGenerator
    participant Publish as publishConversationRelatedEvent
    participant Client as SSE Client
    
    Tool->>Progress: onprogress callback<br/>ProgressNotificationSchema
    Progress->>EventEmitter: emit MCP_NOTIFICATION_EVENT
    EventEmitter->>Stream: yield MCPProgressNotificationType
    
    loop For each notification
        Stream->>Publish: ToolNotificationEvent<br/>{progress, total, data}
        Publish->>Client: SSE stream
    end
    
    Tool->>Tool: Complete execution
    Tool-->>Stream: Return CallToolResult<br/>{content, isError}
    
    alt Success
        Stream->>Publish: tool_success event
    else Error
        Stream->>Publish: tool_error event
    end
```

**Sources:** [front/lib/actions/mcp_actions.ts:375-500](), [front/lib/api/mcp/run_tool.ts:1-170](), [front/lib/actions/mcp_internal_actions/output_schemas.ts:1-200]()

### Output Item Storage

Tool results are stored as structured output items with content size validation. This includes handling file offloading for large outputs.

```mermaid
graph TB
    subgraph "Output Processing"
        CallResult["CallToolResult<br/>{content: ContentItem[], isError}"]
        ValidateSize["isWithinRemoteContentLimit<br/>front/lib/actions/action_output_limits.ts"]
        ProcessItems["processToolResults<br/>front/lib/actions/mcp_execution.ts"]
    end
    
    subgraph "Content Types"
        TextContent["TextContent<br/>type: text, text: string"]
        ImageContent["ImageContent<br/>type: image, data: base64<br/>mimeType: image/*"]
        ResourceContent["ResourceContent<br/>type: resource, resource: {...}<br/>blob, text, mimeType"]
        AudioContent["AudioContent<br/>type: audio, data: base64"]
        FileOffload["makeOffloadedSnippet<br/>makeOffloadMeta<br/>front/lib/actions/mcp_execution.ts"]
    end
    
    subgraph "Storage"
        OutputItem["AgentMCPActionOutputItemModel<br/>{actionId, index, type, value}"]
        FileResource["FileResource<br/>For image/audio content"]
        PersistOutput["persistToolOutput<br/>front/lib/api/files/action_output_fs/index.ts"]
        BatchInsert["Batch insert<br/>OUTPUT_ITEMS_BATCH_SIZE: 32"]
    end
    
    CallResult --> ValidateSize
    ValidateSize --> ProcessItems
    ProcessItems --> TextContent
    ProcessItems --> ImageContent
    ProcessItems --> ResourceContent
    ProcessItems --> AudioContent
    
    TextContent --> OutputItem
    ImageContent --> FileResource
    ResourceContent --> OutputItem
    AudioContent --> FileResource
    
    ProcessItems --> FileOffload
    FileOffload --> PersistOutput
    PersistOutput --> OutputItem
    
    FileResource --> OutputItem
    OutputItem --> BatchInsert
```

**Sources:** [front/lib/resources/agent_mcp_action_resource.ts:500-700](), [front/lib/actions/action_output_limits.ts:1-100](), [front/lib/models/agent/actions/mcp.ts:1-200](), [front/lib/actions/mcp_execution.ts:1-75](), [front/lib/api/files/action_output_fs/index.ts:1-100]()

## Key Classes and Resources

### `AgentMCPActionResource`

Primary resource for managing MCP action execution.

```typescript
// front/lib/resources/agent_mcp_action_resource.ts
class AgentMCPActionResource {
  // Core fields
  id: ModelId;
  workspaceId: string;
  toolConfiguration: LightMCPToolConfigurationType;
  functionCallName: string;
  status: ToolExecutionStatus;
  params: Record<string, unknown>;
  
  // Related resources
  stepContent: AgentStepContentResource;
  metadata: {
    internalMCPServerName: InternalMCPServerNameType | null;
    mcpServerId: string;
  };
  
  // Methods
  static makeNew(auth, blob, transaction): Promise<AgentMCPActionResource>
  static fetchByModelIdWithAuth(auth, actionId): Promise<AgentMCPActionResource>
  fetchOutputItems(): Promise<AgentMCPActionOutputItemModel[]>
  toPublicType(): AgentMCPActionWithOutputType
}
```

**Sources:** [front/lib/resources/agent_mcp_action_resource.ts:70-700]()

### `MCPServerViewResource`

Manages server configuration and access control.

```typescript
// front/lib/resources/mcp_server_view_resource.ts
class MCPServerViewResource {
  id: ModelId;
  mcpServerId: string;
  spaceId: string;
  
  static fetchByIds(auth, mcpServerViewIds): Promise<MCPServerViewResource[]>
  static listForSpace(auth, spaceId): Promise<MCPServerViewResource[]>
  isMCPServerAccessibleByUser(auth): Promise<boolean>
}
```

**Sources:** [front/lib/resources/mcp_server_view_resource.ts:1-400]()

### Tool Configuration Types

```typescript
// front/lib/actions/mcp.ts

type ServerSideMCPToolConfigurationType = {
  type: "mcp_configuration";
  name: string;
  originalName: string;
  mcpServerName: string;
  inputSchema: JSONSchema;
  permission: MCPToolStakeLevelType; // "never_ask" | "low" | "medium" | "high"
  toolServerId: string;
  retryPolicy: MCPToolRetryPolicyType; // "no_retry" | "retry_on_interrupt"
  mcpServerViewId: string;
  argumentsRequiringApproval?: string[];
  // Data source/table/agent configuration
  dataSources: DataSourceConfiguration[];
  tables: TableDataSourceConfiguration[];
  childAgentId: string | null;
};

type ClientSideMCPToolConfigurationType = {
  type: "mcp_configuration";
  name: string;
  originalName: string;
  mcpServerName: string;
  inputSchema: JSONSchema;
  permission: MCPToolStakeLevelType;
  toolServerId: string;
  clientSideMcpServerId: string;
};
```

**Sources:** [front/lib/actions/mcp.ts:59-144]()

## Error Handling and Authentication

The system handles various error conditions including authentication failures and authorization requirements. For detailed information, see [Tool Execution and Authentication](#4.3).

```mermaid
graph TB
    subgraph "Error Types"
        AuthRequired["MCPServerPersonalAuthenticationRequiredError<br/>OAuth connection missing"]
        FileAuthRequired["FileAuthorizationInfo<br/>Google Drive file access"]
        NetworkError["Connection errors<br/>Remote server unavailable"]
        ExecutionError["Tool execution errors<br/>Invalid inputs, timeouts"]
    end
    
    subgraph "Error Response"
        CheckError{Error type?}
        AuthEvent["tool_personal_auth_required event<br/>Provider, scope info"]
        FileEvent["tool_file_auth_required event<br/>FileId, connectionId"]
        ErrorEvent["tool_error event<br/>code, message, metadata"]
    end
    
    subgraph "Client Handling"
        BlockedQueue["Add to blocked actions queue<br/>BlockedActionsProvider"]
        DisplayUI["Show auth/approval UI<br/>MCPServerAuthRequired component"]
        UserAction["User connects OAuth<br/>or grants file access"]
        Retry["Retry action execution"]
    end
    
    AuthRequired --> CheckError
    FileAuthRequired --> CheckError
    NetworkError --> CheckError
    ExecutionError --> CheckError
    
    CheckError -->|Auth| AuthEvent
    CheckError -->|File| FileEvent
    CheckError -->|Other| ErrorEvent
    
    AuthEvent --> BlockedQueue
    FileEvent --> BlockedQueue
    BlockedQueue --> DisplayUI
    DisplayUI --> UserAction
    UserAction --> Retry
```

**Sources:** [front/lib/actions/mcp_authentication.ts:1-179](), [front/lib/actions/types.ts:300-400](), [front/components/assistant/conversation/MCPServerPersonalAuthenticationRequired.tsx:1-68]()

## Constants and Configuration

Key constants that control MCP behavior:

| Constant | Value | Location | Purpose |
|----------|-------|----------|---------|
| `DEFAULT_MCP_REQUEST_TIMEOUT_MS` | 180,000 (3 min) | [front/lib/actions/constants.ts:12]() | Default tool execution timeout |
| `RUN_AGENT_CALL_TOOL_TIMEOUT_MS` | 300,000 (5 min) | [front/lib/actions/constants.ts:11]() | `run_agent` tool timeout |
| `RETRY_ON_INTERRUPT_MAX_ATTEMPTS` | 3 | [front/lib/actions/constants.ts:13]() | Max retries for interrupted tools |
| `TOOL_NAME_SEPARATOR` | `"__"` | [front/lib/actions/constants.ts:16]() | Tool name prefix separator |
| `OUTPUT_ITEMS_BATCH_SIZE` | 32 | [front/lib/resources/agent_mcp_action_resource.ts:63]() | Batch size for output fetching |
| `MAX_OUTPUT_ITEMS` | 128 | [front/lib/actions/mcp_actions.ts:100]() | Maximum output items per action |
| `CLIENT_SIDE_MCP_SERVER_TTL_MS` | 1,200,000 (20 min) | [front/lib/api/actions/mcp/client_side_registry.ts:15]() | Client server registration TTL |

**Sources:** [front/lib/actions/constants.ts:1-50](), [front/lib/resources/agent_mcp_action_resource.ts:63](), [front/lib/actions/mcp_actions.ts:100](), [front/lib/api/actions/mcp/client_side_registry.ts:15]()

---

