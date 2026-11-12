> 来源: [https://deepwiki.com/Tencent/WeKnora/14-data-sources-and-connectors](https://deepwiki.com/Tencent/WeKnora/14-data-sources-and-connectors)
> DeepWiki Tencent/WeKnora

# Data Sources and Connectors

  Relevant source files 
 - [frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue)
 - [internal/application/service/datasource_service.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go)
 - [internal/application/service/datasource_service_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service_test.go)
 - [internal/datasource/connector.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go)
 - [internal/datasource/connector/feishu/core/shared.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/core/shared.go)
 - [internal/datasource/connector/feishu/drive/connector.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/drive/connector.go)
 - [internal/datasource/connector/feishu/wiki/connector.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/wiki/connector.go)
 - [internal/datasource/connector/feishu/wiki/connector_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/wiki/connector_test.go)
 - [internal/datasource/connector/gitlab/connector.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/gitlab/connector.go)
 - [internal/datasource/scheduler_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/scheduler_test.go)
 - [internal/models/provider/aliyun.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/models/provider/aliyun.go)
 - [internal/types/datasource.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/datasource.go)
 
  WeKnora provides a robust framework for automatic knowledge ingestion from external platforms. By configuring **Data Sources**, users can synchronize documents, wikis, and structured content directly into a Knowledge Base. This process is handled by specialized **Connectors** that abstract the complexities of external APIs and authentication.

 
### Overview of Ingestion Flow

 The system uses a provider-agnostic interface to manage external data. A `DataSource` entity represents a specific configuration—such as a particular Feishu Wiki space or a Notion database—linked to a `KnowledgeBase` [internal/application/service/datasource_service.go68-79](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go#L68-L79) The ingestion logic is orchestrated by the `DataSourceService` which interacts with a `ConnectorRegistry` to invoke the appropriate platform connector [internal/application/service/datasource_service.go26-38](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go#L26-L38) [internal/datasource/connector.go97-127](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go#L97-L127)

 
#### Natural Language to Code Entity Mapping: Ingestion Pipeline

 The following table and diagram illustrate how user-facing actions in the "Natural Language Space" correspond to backend code entities that implement the ingestion and sync framework:

 
| User Action | Code Entity / Service | Purpose |
|---|---|---|
| "Add Feishu Wiki" | CreateDataSource | Validates and persists data source configurations. |
|  |  | internal/application/service/datasource_service.go67-116 |
| "Select Folders" | ListResources (Connector API) | Fetches available external resources (folders, wiki spaces) for user selection. |
|  |  | internal/datasource/connector.go19-28 |
| "Sync Now" | ProcessSync (async task) | Enqueues a background sync task to fetch and ingest documents. |
|  |  | internal/application/service/datasource_service.go50-206 |
| "Schedule Sync" | Scheduler | Registers periodic jobs based on cron expressions to trigger auto-syncs. |
|  |  | internal/application/service/datasource_service.go105-110 |

 **Data Source Lifecycle Diagram**

 
```

```

 Sources: [frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue6-18](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue#L6-L18) [internal/application/service/datasource_service.go26-117](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go#L26-L117) [internal/datasource/connector.go9-127](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go#L9-L127) [internal/types/datasource.go64-129](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/datasource.go#L64-L129)

 
---

 
### Core Components

 
#### 1. Connectors and Streaming

 A **Connector** implements the `Connector` interface defining methods for resource listing, validation, and fetching data:

 
 - `Validate(ctx, config) error`: Checks connectivity and credentials with the external system.
 - `ListResources(ctx, config, parentID)`: Returns configurable external content structures (docs, spaces, folders).
 - `FetchAll(ctx, config, resourceIDs)`: Retrieves all documents from specified sources.
 - `FetchIncremental(ctx, config, cursor)`: Retrieves only updates since last sync.
 
 For large sources like Feishu, streaming connectors implement `StreamingConnector`, allowing item-by-item fetching with incremental cursor checkpointing for fault tolerance and memory efficiency [internal/datasource/connector.go11-94](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go#L11-L94)

 Example: The Feishu Wiki connector implements streaming syncing, fetching only changed wiki nodes since the last recorded sync cursor [internal/datasource/connector/feishu/wiki/connector.go20-160](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/wiki/connector.go#L20-L160)

 
#### 2. Synchronization Engine

 The `DataSourceService` drives syncs by coordinating connector calls and persisting sync state:

 
 - Supports both **Incremental** syncs (efficiently pulling only changes) and **Full** syncs (reimport all data).
 - Manages sync scheduling with cron expressions stored per data source.
 - Supports conflict strategies during ingestion: `overwrite` or `skip` [frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue180-181](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue#L180-L181)
 
 Syncs are recorded in `SyncLog` entities tracking execution status and per-item results (created, updated, deleted, failed) with detailed error metadata for diagnosis [internal/types/datasource.go144-193](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/datasource.go#L144-L193) [frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue6-171](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue#L6-L171)

 
#### 3. Monitoring and Logs

 The frontend periodically polls the backend for sync logs and status updates, showing success/failure metrics, error details, and recent sync timestamps. This improves user visibility into ingestion health and troubleshooting [frontend/src/views/knowledge/settings/DataSourceSettings.vue45-50](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceSettings.vue#L45-L50) [frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue59-156](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue#L59-L156)

 **Sync Execution Flow**

 
```

```

 Sources: [internal/application/service/datasource_service.go26-206](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go#L26-L206) [internal/datasource/connector.go60-75](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go#L60-L75) [frontend/src/views/knowledge/settings/DataSourceSettings.vue45-50](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceSettings.vue#L45-L50) [frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue59-156](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue#L59-L156)

 
---

 
### Supported Connectors

 WeKnora ships with a comprehensive set of connectors for common enterprise platforms. The `ConnectorMetadataRegistry` holds metadata used by the frontend to display connector options [internal/datasource/connector.go151-178](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go#L151-L178)

 
| Connector | Auth Type | Capabilities | Implementation Reference |
|---|---|---|---|
| Feishu / Lark | OAuth2 | Incremental, Streaming, Deletion Sync | internal/datasource/connector/feishu/wiki/connector.go20-160 internal/datasource/connector/feishu/drive/connector.go20-126 |
| Notion | API Key | Incremental | internal/datasource/connector/notion/connector.go (not shown here) |
| Yuque | API Key | Incremental | internal/datasource/connector/yuque/connector.go (not shown here) |
| GitLab | Personal Token | Incremental, Streaming | internal/datasource/connector/gitlab/connector.go1-225 |
| RSS Feed | Custom Headers | Periodic Polling | frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue111-133 |
| Web Crawler | Sitemap, Web | Sitemap-based Crawling | internal/datasource/connector.go182-187 |

 Each connector is designed to handle authentication, resource enumeration, incremental sync, and failure handling specific to its source system.

 Sources: [internal/datasource/connector.go151-178](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go#L151-L178)

 
---

 
### Child Pages

 This page provides a high-level architecture and overview for data sources and connectors. More detailed documentation is available in the following child pages:

 
 - **[Data Source Configuration](https://deepwiki.com/Tencent/WeKnora/14.1-data-source-configuration)**
 Guide to configuring connectors, setting sync schedules and conflict strategies, managing credentials securely, and viewing sync logs. Covers the data source editor dialog and backend API details.
 [internal/application/service/datasource_service.go172-176](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go#L172-L176) [frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue20-110](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue#L20-L110)
 - **[Connector Reference](https://deepwiki.com/Tencent/WeKnora/14.2-connector-reference)**
 Reference documentation for each supported connector including Feishu Docs/Wiki, GitLab, Notion, Yuque, RSS feeds, and web crawlers. Details about authentication, supported sync modes, resource hierarchy, and configuration options.
 [internal/datasource/connector/feishu/wiki/connector.go15-160](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/wiki/connector.go#L15-L160) [internal/datasource/connector/gitlab/connector.go1-225](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/gitlab/connector.go#L1-L225)
 
 Sources: [internal/application/service/datasource_service.go172-176](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go#L172-L176) [frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue20-110](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue#L20-L110) [internal/datasource/connector/feishu/wiki/connector.go15-160](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/wiki/connector.go#L15-L160) [internal/datasource/connector/gitlab/connector.go1-225](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/gitlab/connector.go#L1-L225)

 
---

 
# Summary

 WeKnora’s data ingestion subsystem abstractly manages knowledge ingestion from diverse external sources with a unified `DataSource` configuration and backend connector implementations. The architecture balances robustness (resumable streaming sync), extensibility (pluggable connectors), and usability (incremental sync scheduling and progress monitoring), enabling automated knowledge base updates from popular enterprise content platforms.

 Sources:

 
 - [internal/application/service/datasource_service.go26-176](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/datasource_service.go#L26-L176)
 - [internal/datasource/connector.go9-178](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector.go#L9-L178)
 - [internal/datasource/connector/feishu/wiki/connector.go11-163](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/wiki/connector.go#L11-L163)
 - [internal/datasource/connector/feishu/drive/connector.go20-126](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/feishu/drive/connector.go#L20-L126)
 - [internal/datasource/connector/gitlab/connector.go1-225](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/datasource/connector/gitlab/connector.go#L1-L225)
 - [internal/types/datasource.go64-193](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/datasource.go#L64-L193)
 - [frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue6-110](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue#L6-L110)
 - [frontend/src/views/knowledge/settings/DataSourceSettings.vue45-50](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceSettings.vue#L45-L50)
 - [frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue59-156](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/settings/DataSourceSyncLogs.vue#L59-L156)
