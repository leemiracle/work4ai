<!-- source: DeepWiki mcp.deepwiki.com · repo iflytek/astron-agent · page 4 Workflow and Publishing System · fetched 2026-10-26 -->

# Workflow and Publishing System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java](console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/controller/publish/BotPublishController.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/controller/publish/BotPublishController.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/entity/BotConversationStats.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/entity/BotConversationStats.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/listener/WorkflowBotPublishListener.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/listener/WorkflowBotPublishListener.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/mapper/BotConversationStatsMapper.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/mapper/BotConversationStatsMapper.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/BotPublishService.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/BotPublishService.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/McpService.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/McpService.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/impl/BotPublishServiceImpl.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/impl/BotPublishServiceImpl.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/PublishStrategy.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/PublishStrategy.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/PublishStrategyFactory.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/PublishStrategyFactory.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/ApiPublishStrategy.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/ApiPublishStrategy.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/FeishuPublishStrategy.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/FeishuPublishStrategy.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/MarketPublishStrategy.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/MarketPublishStrategy.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/McpPublishStrategy.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/McpPublishStrategy.java)
- [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/WechatPublishStrategy.java](console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/WechatPublishStrategy.java)
- [console/backend/hub/src/main/resources/mapper/BotConversationStatsMapper.xml](console/backend/hub/src/main/resources/mapper/BotConversationStatsMapper.xml)
- [core/workflow/engine/callbacks/callback_handler.py](core/workflow/engine/callbacks/callback_handler.py)
- [core/workflow/engine/dsl_engine.py](core/workflow/engine/dsl_engine.py)
- [core/workflow/engine/entities/chains.py](core/workflow/engine/entities/chains.py)
- [core/workflow/engine/entities/variable_pool.py](core/workflow/engine/entities/variable_pool.py)
- [core/workflow/engine/entities/workflow_dsl.py](core/workflow/engine/entities/workflow_dsl.py)
- [core/workflow/engine/node.py](core/workflow/engine/node.py)
- [core/workflow/engine/nodes/base_node.py](core/workflow/engine/nodes/base_node.py)
- [core/workflow/engine/nodes/code/executor/local/local_executor.py](core/workflow/engine/nodes/code/executor/local/local_executor.py)
- [core/workflow/engine/nodes/if_else/if_else_node.py](core/workflow/engine/nodes/if_else/if_else_node.py)
- [core/workflow/engine/nodes/iteration/iteration_node.py](core/workflow/engine/nodes/iteration/iteration_node.py)
- [core/workflow/engine/nodes/llm/spark_llm_node.py](core/workflow/engine/nodes/llm/spark_llm_node.py)
- [core/workflow/service/chat_service.py](core/workflow/service/chat_service.py)
- [core/workflow/service/flow_service.py](core/workflow/service/flow_service.py)

</details>



The Workflow and Publishing System manages the complete lifecycle of bot publishing across multiple channels (Market, WeChat, MCP, API, Feishu). It coordinates workflow version management, synchronization with the external MaaS platform, multi-channel publishing strategies, and API credential provisioning. The system uses an event-driven architecture with the Strategy pattern to handle channel-specific publishing logic.

For bot creation and configuration prior to publishing, see [Bot Lifecycle Management](#5). For publishing UI components, see [Release Management and Publishing UI](#9.5).

## System Architecture

The publishing system spans multiple services with the console backend (`console-hub`) orchestrating publishing operations and the workflow service (`core-workflow`) managing workflow execution. The system integrates with the external MaaS platform for workflow version management and API publishing.

### Publishing System Components

```mermaid
graph TB
    subgraph "Console Backend (Spring Boot :8080)"
        BotPublishController["BotPublishController<br/>/publish/bots/*"]
        BotPublishServiceImpl["BotPublishServiceImpl<br/>publishing coordination"]
        PublishStrategyFactory["PublishStrategyFactory<br/>strategy selection"]
        WorkflowReleaseServiceImpl["WorkflowReleaseServiceImpl<br/>version creation"]
    end
    
    subgraph "Publishing Strategies"
        MarketPublishStrategy["MarketPublishStrategy<br/>agent hub market"]
        WechatPublishStrategy["WechatPublishStrategy<br/>WeChat OAuth"]
        McpPublishStrategy["McpPublishStrategy<br/>MCP server"]
        ApiPublishStrategy["ApiPublishStrategy<br/>API endpoint"]
        FeishuPublishStrategy["FeishuPublishStrategy<br/>Feishu integration"]
    end
    
    subgraph "External Integration"
        MaasUtil["MaasUtil<br/>workflow sync utility"]
        MaasPlatform["MaaS Platform<br/>workflow management"]
    end
    
    subgraph "Database Entities"
        ChatBotBase["ChatBotBase<br/>bot configuration"]
        ChatBotMarket["ChatBotMarket<br/>market listings"]
        ChatBotApi["ChatBotApi<br/>API credentials"]
        WorkflowVersion["WorkflowVersion<br/>version history"]
        UserLangChainInfo["UserLangChainInfo<br/>workflow mapping"]
    end
    
    subgraph "Event System"
        EventPublisher["ApplicationEventPublisher"]
        BotPublishStatusChangedEvent["BotPublishStatusChangedEvent<br/>workflow bot listener"]
    end
    
    BotPublishController --> BotPublishServiceImpl
    BotPublishServiceImpl --> PublishStrategyFactory
    PublishStrategyFactory --> MarketPublishStrategy
    PublishStrategyFactory --> WechatPublishStrategy
    PublishStrategyFactory --> McpPublishStrategy
    PublishStrategyFactory --> ApiPublishStrategy
    PublishStrategyFactory --> FeishuPublishStrategy
    
    MarketPublishStrategy --> EventPublisher
    EventPublisher --> BotPublishStatusChangedEvent
    BotPublishStatusChangedEvent --> WorkflowReleaseServiceImpl
    
    WorkflowReleaseServiceImpl --> MaasUtil
    MaasUtil --> MaasPlatform
    
    BotPublishServiceImpl --> ChatBotBase
    MarketPublishStrategy --> ChatBotMarket
    WorkflowReleaseServiceImpl --> WorkflowVersion
    WorkflowReleaseServiceImpl --> ChatBotApi
    WorkflowReleaseServiceImpl --> UserLangChainInfo
```

**Sources:** [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/impl/BotPublishServiceImpl.java:68-87](), [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/McpPublishStrategy.java:18-38](), [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java:36-42](), [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/impl/BotPublishServiceImpl.java:70-87]()

## Workflow Architecture and MaaS Integration

The system integrates with an external MaaS (Model-as-a-Service) platform for workflow version management and API publishing. The `MaasUtil` class provides the integration layer, handling HTTP communication with the MaaS platform via `OkHttpClient` [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:44-49]().

### MaaS Synchronization Flow

The `synchronizeWorkFlow()` method performs bidirectional workflow synchronization between the Astron platform and the external MaaS engine.

```mermaid
graph TB
    subgraph "Bot Configuration Space"
        BotCreateForm["BotCreateForm<br/>name, desc, avatar"]
        UserLangChainInfo["UserLangChainInfo<br/>botId, maasId, flowId"]
        TalkAgentConfig["TalkAgentConfigDto<br/>flow configuration"]
    end
    
    subgraph "MaasUtil.java Logic"
        SynchronizeWorkflow["synchronizeWorkFlow()<br/>PUT or POST"]
        DeleteSynchronize["deleteSynchronize()<br/>DELETE"]
        CopyWorkflow["copyWorkFlow()<br/>clone workflow"]
    end
    
    subgraph "MaaS Platform API Space"
        SyncURL["synchronizeUrl<br/>/v1/workflow/sync"]
        CloneURL["cloneWorkFlowUrl<br/>/v1/workflow/clone"]
    end
    
    subgraph "Request Entity Construction"
        JSONParam["JSONObject payload<br/>avatarIcon, description, advancedConfig"]
        HTTPMethod["PUT if maasId exists<br/>POST for new workflow"]
        AuthHeader["Authorization header<br/>from HttpServletRequest"]
    end
    
    subgraph "Persistence and Cache"
        MaasID["Extract maasId<br/>from response.data.id"]
        FlowID["Extract flowId<br/>from response.data.flowId"]
        RedisCache["RedissonClient.getBucket()<br/>PREFIX_MAAS_COPY"]
    end
    
    BotCreateForm --> SynchronizeWorkflow
    UserLangChainInfo --> SynchronizeWorkflow
    TalkAgentConfig --> SynchronizeWorkflow
    
    SynchronizeWorkflow --> JSONParam
    JSONParam --> HTTPMethod
    HTTPMethod --> AuthHeader
    
    AuthHeader --> SyncURL
    SynchronizeWorkflow --> DeleteSynchronize
    DeleteSynchronize --> SyncURL
    
    SynchronizeWorkflow --> CopyWorkflow
    CopyWorkflow --> CloneURL
    
    SyncURL --> MaasID
    SyncURL --> FlowID
    MaasID --> RedisCache
```

**Sources:** [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:108-167](), [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:169-249]()

The `synchronizeWorkFlow()` method at [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:169-249]() performs bidirectional workflow synchronization:

1. **Request Preparation** - Builds `JSONObject` payload with bot metadata including `avatarIcon`, `description`, and `advancedConfig` (prologue, inputExample, text-to-speech settings) [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:170-181]().
2. **HTTP Method Selection** - Uses `PUT` if `UserLangChainInfo.maasId` exists (update), `POST` for new workflows [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:214-221]().
3. **Authorization** - Extracts Authorization header from `HttpServletRequest` via `getAuthorizationHeader()` [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:131]().
4. **Redis Caching** - Stores maasId in Redis with key pattern `maas_copy_{botId}` using `redissonClient` [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:94-96]().

For more details on integration patterns, see [Workflow Architecture and MaaS Integration](#4.1).

## Bot Publishing Lifecycle

The publishing lifecycle uses an event-driven architecture with status transitions managed through the `BotPublishServiceImpl` and channel-specific strategies.

### Publishing Status Flow

```mermaid
graph TB
    subgraph "Status Enumeration (ShelfStatusEnum)"
        OffShelf["OFF_SHELF (0)<br/>Bot is private"]
        OnShelf["ON_SHELF (1)<br/>Bot is public"]
    end
    
    subgraph "Publishing Actions (BotPublishServiceImpl.java)"
        Publish["publish()<br/>Strategy selection"]
        Offline["offline()<br/>Take down bot"]
    end
    
    subgraph "Data Persistence"
        FirstPublish["ChatBotMarketMapper.insert()<br/>Create market record"]
        RepublishSync["ChatBotMarketMapper.updateById()<br/>Full data sync"]
        OfflineUpdate["ChatBotMarketMapper.updateStatus()<br/>Status toggle"]
    end
    
    subgraph "Event System (Spring Event)"
        BotPublishStatusChangedEvent["BotPublishStatusChangedEvent<br/>Type: PUBLISH/OFFLINE"]
    end
    
    OffShelf --> Publish
    Publish --> OnShelf
    OnShelf --> Offline
    Offline --> OffShelf
    
    Publish --> FirstPublish
    OnShelf --> RepublishSync
    Offline --> OfflineUpdate
    
    FirstPublish --> BotPublishStatusChangedEvent
    RepublishSync --> BotPublishStatusChangedEvent
```

**Sources:** [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/impl/BotPublishServiceImpl.java:68-150](), [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/MarketPublishStrategy.java:40-93](), [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/event/BotPublishStatusChangedEvent.java:1-49]()

The `BotPublishServiceImpl` implements the core publishing flow by validating permissions, coordinating with the `PublishStrategyFactory`, and emitting a `BotPublishStatusChangedEvent` [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/publish/impl/BotPublishServiceImpl.java:75](). For a deep dive into status transitions, see [Bot Publishing Lifecycle](#4.2).

## Multi-Channel Publishing Strategy

The system uses the Strategy pattern to handle channel-specific publishing logic. The `PublishStrategyFactory` manages strategy selection based on the `ReleaseTypeEnum`.

### Strategy Pattern Implementation

The `PublishStrategy` interface defines the contract for all publishing channels.

- **Market Strategy**: Handles publishing to the platform's internal agent marketplace via `MarketPublishStrategy` [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/MarketPublishStrategy.java:32]().
- **WeChat Strategy**: Manages bot deployment to WeChat via `WechatPublishStrategy`.
- **MCP Strategy**: Handles bot publishing to Model Context Protocol servers [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/strategy/publish/impl/McpPublishStrategy.java:18-38]().
- **API Strategy**: Provisions dedicated API endpoints and credentials via `ApiPublishStrategy`.

For channel-specific logic, see [Multi-Channel Publishing Strategy](#4.3).

## Workflow Versioning and Release Management

The `WorkflowReleaseServiceImpl` manages workflow version creation and release to the MaaS platform. It ensures that every publication is associated with a specific, immutable version of the workflow DSL.

### Version Creation Flow

```mermaid
graph TB
    subgraph "Release Service (WorkflowReleaseServiceImpl.java)"
        PublishWorkflow["publishWorkflow()<br/>Entry point"]
        GetFlowId["UserLangChainDataService.findFlowIdByBotId()"]
        GetVersionName["getNextVersionName()<br/>POST /get-version-name"]
    end
    
    subgraph "Version Entity (WorkflowVersion.java)"
        BuildRequest["WorkflowReleaseRequestDto<br/>botId, flowId, name"]
        CreateVersion["createWorkflowVersion()<br/>POST maas.workflowVersion"]
    end
    
    subgraph "API Sync System"
        GetAppId["getAppIdByBotId()<br/>ChatBotApiMapper lookup"]
        SyncToApi["syncToApiSystem()<br/>MaaS API synchronization"]
    end
    
    subgraph "Audit Result Tracking"
        UpdateAudit["updateAuditResult()<br/>POST /update-channel-result"]
    end
    
    PublishWorkflow --> GetFlowId
    GetFlowId --> GetVersionName
    GetVersionName --> BuildRequest
    BuildRequest --> CreateVersion
    CreateVersion --> GetAppId
    GetAppId --> SyncToApi
    SyncToApi --> UpdateAudit
```

**Sources:** [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java:76-137](), [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java:143-203]()

The `publishWorkflow()` method orchestrates the release by fetching the `flowId`, generating a version name via MaaS APIs, and creating a record in the `workflow_version` table [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java:103-111](). For more on version management, see [Workflow Versioning and Release Management](#4.4).

## Bot API Publishing Service

The API publishing system provisions tenant applications with credentials and publishes workflow APIs through the MaaS platform. It uses the `ChatBotApi` entity to track application bindings.

### API Publishing Architecture

1. **Persistence**: Stores binding in the `chat_bot_api` table via `ChatBotApiMapper` [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java:40]().
2. **MaaS Registration**: Calls `publishApi` and `authApi` endpoints defined in `MaasUtil` to expose the workflow as a RESTful service [console/backend/commons/src/main/java/com/iflytek/astron/console/commons/util/MaasUtil.java:75-79]().
3. **App ID Resolution**: Resolves the target `appId` for the API based on whether the bot is published to the marketplace (using `maas.appId`) or a custom tenant app [console/backend/hub/src/main/java/com/iflytek/astron/console/hub/service/workflow/impl/WorkflowReleaseServiceImpl.java:117-122]().

For details on credential management and API lifecycles, see [Bot API Publishing Service](#4.5).

---

