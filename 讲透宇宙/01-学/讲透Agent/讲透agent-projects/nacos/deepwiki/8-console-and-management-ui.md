<!-- source: DeepWiki mcp.deepwiki.com · repo alibaba/nacos · page 8 Console and Management UI · fetched 2026-10-29 -->

# Console and Management UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [console-ui/package-lock.json](console-ui/package-lock.json)
- [console-ui/package.json](console-ui/package.json)
- [console-ui/src/components/Page/TotalRender.js](console-ui/src/components/Page/TotalRender.js)
- [console-ui/src/locales/en-US.js](console-ui/src/locales/en-US.js)
- [console-ui/src/locales/zh-CN.js](console-ui/src/locales/zh-CN.js)
- [console-ui/src/pages/AI/McpDetail/CreateTools/DeleteTool.js](console-ui/src/pages/AI/McpDetail/CreateTools/DeleteTool.js)
- [console-ui/src/pages/AI/McpDetail/CreateTools/components.js](console-ui/src/pages/AI/McpDetail/CreateTools/components.js)
- [console-ui/src/pages/AI/McpDetail/CreateTools/index.js](console-ui/src/pages/AI/McpDetail/CreateTools/index.js)
- [console-ui/src/pages/AI/McpDetail/McpDetail.js](console-ui/src/pages/AI/McpDetail/McpDetail.js)
- [console-ui/src/pages/AI/McpDetail/ShowTools.js](console-ui/src/pages/AI/McpDetail/ShowTools.js)
- [console-ui/src/pages/AI/McpManagement/McpManagement.js](console-ui/src/pages/AI/McpManagement/McpManagement.js)
- [console-ui/src/pages/AI/NewMcpServer/NewMcpServer.js](console-ui/src/pages/AI/NewMcpServer/NewMcpServer.js)
- [console-ui/src/pages/ClusterManagement/ClusterNodeList/ClusterNodeList.js](console-ui/src/pages/ClusterManagement/ClusterNodeList/ClusterNodeList.js)
- [console-ui/src/pages/ConfigurationManagement/ConfigurationManagement/ConfigurationManagement.js](console-ui/src/pages/ConfigurationManagement/ConfigurationManagement/ConfigurationManagement.js)
- [console-ui/src/pages/ConfigurationManagement/HistoryRollback/HistoryRollback.js](console-ui/src/pages/ConfigurationManagement/HistoryRollback/HistoryRollback.js)
- [console-ui/src/pages/ConfigurationManagement/ListeningToQuery/ListeningToQuery.js](console-ui/src/pages/ConfigurationManagement/ListeningToQuery/ListeningToQuery.js)
- [console-ui/src/pages/NameSpace/NameSpace.js](console-ui/src/pages/NameSpace/NameSpace.js)
- [console-ui/src/pages/ServiceManagement/ServiceList/ServiceList.js](console-ui/src/pages/ServiceManagement/ServiceList/ServiceList.js)
- [console-ui/src/pages/ServiceManagement/SubscriberList/SubscriberList.js](console-ui/src/pages/ServiceManagement/SubscriberList/SubscriberList.js)
- [console/src/main/resources/static/css/main.css](console/src/main/resources/static/css/main.css)
- [console/src/main/resources/static/index.html](console/src/main/resources/static/index.html)
- [console/src/main/resources/static/js/main.js](console/src/main/resources/static/js/main.js)

</details>



## Purpose and Scope

This document describes the Nacos console web interface - a React-based management UI that provides administrators and operators with graphical tools for managing configurations, services, namespaces, clusters, and AI/MCP features. The console communicates with backend REST APIs to perform operations and display system state.

For information about the underlying configuration service implementation, see [Configuration Service](#3). For details on the naming/service discovery backend, see [Naming Service](#4). This page focuses on the web UI layer and its integration with backend APIs.

---

## System Architecture

The console follows a three-tier web application architecture with a React frontend, REST API backend, and persistence layer.

### Overall Console Architecture

```mermaid
graph TB
    subgraph "Browser Environment"
        Browser["Web Browser"]
        ReactApp["React Application<br/>console-ui/src"]
        StateManagement["Redux Store<br/>State Management"]
    end
    
    subgraph "Static Resources"
        IndexHTML["index.html<br/>console/src/main/resources/static"]
        BundleJS["main.js<br/>Webpack Bundle"]
        BundleCSS["main.css<br/>Styles"]
    end
    
    subgraph "Backend REST APIs"
        ConsoleBackend["Console Backend<br/>nacos-console"]
        ConfigAPI["Config APIs<br/>/v3/console/cs/config"]
        NamingAPI["Naming APIs<br/>/v3/console/ns"]
        NamespaceAPI["Namespace APIs<br/>/v3/console/namespace"]
        MCPAPI["MCP APIs<br/>/v3/console/ai/mcp"]
        AuthAPI["Auth APIs<br/>/v3/console/auth"]
    end
    
    subgraph "Backend Services"
        ConfigService["ConfigService"]
        NamingService["NamingService"]
        AuthService["AuthService"]
    end
    
    Browser -->|"HTTP Request"| IndexHTML
    IndexHTML -->|"Loads"| BundleJS
    IndexHTML -->|"Loads"| BundleCSS
    BundleJS -->|"Initializes"| ReactApp
    ReactApp -->|"Uses"| StateManagement
    
    ReactApp -->|"REST Calls"| ConsoleBackend
    ConsoleBackend --> ConfigAPI
    ConsoleBackend --> NamingAPI
    ConsoleBackend --> NamespaceAPI
    ConsoleBackend --> MCPAPI
    ConsoleBackend --> AuthAPI
    
    ConfigAPI --> ConfigService
    NamingAPI --> NamingService
    AuthAPI --> AuthService
```

**Sources:** [console/src/main/resources/static/index.html:17-61](), [console-ui/package.json:1-90]()

---

## Frontend Architecture

The console UI is built with React 16.12.0 and uses the Alibaba Fusion Design component library (`@alifd/next`). The application follows a component-based architecture with route-based code splitting.

### Component Hierarchy and Routing

```mermaid
graph TB
    App["App Component<br/>Root Application"]
    
    subgraph "Main Layout"
        Header["Header Component<br/>Navigation & Auth"]
        MainContent["MainLayout<br/>Content Area"]
        Footer["Footer Component"]
    end
    
    subgraph "Configuration Pages"
        ConfigList["ConfigurationManagement<br/>Configuration List"]
        NewConfig["NewConfig<br/>Create Configuration"]
        ConfigEditor["ConfigEditor<br/>Edit Configuration"]
        ConfigDetail["ConfigDetail<br/>View Configuration"]
        HistoryRollback["HistoryRollback<br/>Version History"]
    end
    
    subgraph "Service Management Pages"
        ServiceList["ServiceList<br/>Service List"]
        ServiceDetail["ServiceDetail<br/>Service Details"]
        SubscriberList["SubscriberList<br/>Subscribers"]
    end
    
    subgraph "AI Management Pages"
        McpManagement["McpManagement<br/>MCP Server List"]
        McpDetail["McpDetail<br/>MCP Server Details"]
        NewMcpServer["NewMcpServer<br/>Create/Edit MCP Server"]
        ShowTools["ShowTools<br/>Tool Configuration"]
    end
    
    subgraph "Authority Pages"
        UserList["UserManagement<br/>User List"]
        RoleList["RolesManagement<br/>Role Management"]
        PermissionList["PermissionsManagement<br/>Permissions"]
    end
    
    subgraph "Cluster Pages"
        ClusterNodes["ClusterNodeList<br/>Node List"]
        NamespaceList["NameSpace<br/>Namespace Management"]
    end
    
    App --> Header
    App --> MainContent
    App --> Footer
    
    MainContent --> ConfigList
    MainContent --> ServiceList
    MainContent --> McpManagement
    MainContent --> UserList
    MainContent --> ClusterNodes
    
    ConfigList -->|"Create"| NewConfig
    ConfigList -->|"Edit"| ConfigEditor
    ConfigList -->|"View"| ConfigDetail
    ConfigList -->|"History"| HistoryRollback
    
    ServiceList -->|"Details"| ServiceDetail
    ServiceList -->|"Subscribers"| SubscriberList
    
    McpManagement -->|"Create/Edit"| NewMcpServer
    McpManagement -->|"Details"| McpDetail
    NewMcpServer --> ShowTools
    McpDetail --> ShowTools
```

**Sources:** [console-ui/src/locales/zh-CN.js:44-81](), [console-ui/src/locales/en-US.js:46-87]()

### State Management Architecture

The application uses Redux for global state management with specific reducers for different domain entities:

```mermaid
graph LR
    subgraph "Redux Store"
        RootReducer["Root Reducer"]
        ConfigReducer["configuration<br/>Reducer"]
        NamespaceReducer["namespace<br/>Reducer"]
        GlobalReducer["global<br/>Reducer"]
    end
    
    subgraph "Action Creators"
        GetConfigs["getConfigs()<br/>Fetch Configurations"]
        GetConfigsV2["getConfigsV2()<br/>Fetch with Filters"]
    end
    
    subgraph "React Components"
        ConnectedComponent["@connect()<br/>Connected Component"]
        ComponentState["Local Component State<br/>Field, Form State"]
    end
    
    RootReducer --> ConfigReducer
    RootReducer --> NamespaceReducer
    RootReducer --> GlobalReducer
    
    GetConfigs --> ConfigReducer
    GetConfigsV2 --> ConfigReducer
    
    ConnectedComponent -->|"mapStateToProps"| ConfigReducer
    ConnectedComponent -->|"mapDispatchToProps"| GetConfigs
    ConnectedComponent -->|"Local State"| ComponentState
```

**Sources:** [console-ui/src/pages/AI/McpManagement/McpManagement.js:56-62](), [console-ui/package.json:67-88]()

---

## Backend API Structure

The console backend exposes REST APIs under the `/v3/console/` prefix. These APIs handle CRUD operations for configurations, services, namespaces, and other entities.

### API Endpoint Categories

```mermaid
graph TB
    subgraph "API Base Path: /v3/console"
        ConfigAPIs["/cs/config<br/>Configuration APIs"]
        NamingAPIs["/ns<br/>Naming/Service APIs"]
        NamespaceAPIs["/namespace<br/>Namespace APIs"]
        AuthAPIs["/auth<br/>Authentication APIs"]
        MCPAPIs["/ai/mcp<br/>MCP Management APIs"]
        PluginAPIs["/plugin<br/>Plugin Management APIs"]
        ClusterAPIs["/cluster<br/>Cluster Node APIs"]
    end
    
    ConfigAPIs -->|"GET"| ConfigList["List Configurations"]
    ConfigAPIs -->|"POST"| ConfigCreate["Create Configuration"]
    ConfigAPIs -->|"PUT"| ConfigUpdate["Update Configuration"]
    ConfigAPIs -->|"DELETE"| ConfigDelete["Delete Configuration"]
    
    NamingAPIs -->|"GET"| ServiceList["List Services"]
    NamingAPIs -->|"POST"| ServiceCreate["Create Service"]
    NamingAPIs -->|"GET /instance/list"| InstanceList["List Instances"]
    
    NamespaceAPIs -->|"GET"| NamespaceList["List Namespaces"]
    NamespaceAPIs -->|"POST"| NamespaceCreate["Create Namespace"]
    NamespaceAPIs -->|"DELETE"| NamespaceDelete["Delete Namespace"]
    
    MCPAPIs -->|"GET /list"| MCPList["List MCP Servers"]
    MCPAPIs -->|"GET"| MCPDetail["MCP Server Details"]
    MCPAPIs -->|"POST"| MCPCreate["Create MCP Server"]
    MCPAPIs -->|"PUT"| MCPUpdate["Update MCP Server"]
    MCPAPIs -->|"DELETE"| MCPDelete["Delete MCP Server"]
    
    AuthAPIs -->|"POST /login"| Login["User Login"]
    AuthAPIs -->|"POST /users"| UserCreate["Create User"]
    AuthAPIs -->|"GET /users"| UserList["List Users"]
```

### Request Flow with Authentication

```mermaid
sequenceDiagram
    participant UI as React Component
    participant Util as request() Utility
    participant Interceptor as Auth Interceptor
    participant API as Backend API
    participant Service as Backend Service
    
    UI->>Util: request({url, method, data})
    Util->>Util: Extract XSRF-TOKEN from cookie
    Util->>Util: Get Authorization token from localStorage
    Util->>Interceptor: Add headers (Authorization, AccessToken)
    Interceptor->>API: HTTP Request with auth headers
    
    alt Authentication Success
        API->>Service: Process request
        Service->>API: Response data
        API->>Interceptor: 200 OK
        Interceptor->>Util: Parse response
        Util->>UI: Return data
    else Authentication Failed
        API->>Interceptor: 401/403 Unauthorized
        Interceptor->>Interceptor: Detect auth error
        Interceptor->>UI: Redirect to login
        UI->>UI: goLogin() - Clear token & redirect
    end
```

**Sources:** [console/src/main/resources/static/js/main.js:1-1](), [console-ui/src/locales/zh-CN.js:1-1000]()

---

## Configuration Management UI

The Configuration Management UI provides comprehensive tools for creating, editing, searching, importing, exporting, and managing configuration items. It is one of the primary functions of the Nacos console.

### Configuration List Page Components

```mermaid
graph TB
    subgraph "ConfigurationManagement Page"
        SearchPanel["Search Panel<br/>Filters and Query"]
        ConfigTable["Configuration Table<br/>Display Results"]
        Pagination["Pagination Component"]
        BatchActions["Batch Actions Bar<br/>Export, Clone, Delete"]
    end
    
    subgraph "Search Filters"
        DataIdFilter["Data ID Input<br/>Fuzzy Search Support"]
        GroupFilter["Group Input<br/>Fuzzy Search Support"]
        NamespaceFilter["Namespace Selector<br/>Current Namespace"]
        AdvancedFilters["Advanced Filters<br/>App, Tags, Type"]
    end
    
    subgraph "Table Operations Per Row"
        DetailsAction["Details Button<br/>View Configuration"]
        EditAction["Edit Button<br/>Modify Configuration"]
        HistoryAction["History Button<br/>Version History"]
        DeleteAction["Delete Button<br/>Remove Configuration"]
        MoreMenu["More Menu<br/>Listen Query, Sample Code"]
    end
    
    subgraph "Batch Operations"
        ExportSelected["Export Selected<br/>Download as ZIP"]
        CloneSelected["Clone Selected<br/>Copy to Namespace"]
        DeleteSelected["Delete Selected<br/>Bulk Delete"]
        ImportConfigs["Import Configurations<br/>Upload ZIP"]
    end
    
    SearchPanel --> DataIdFilter
    SearchPanel --> GroupFilter
    SearchPanel --> NamespaceFilter
    SearchPanel --> AdvancedFilters
    
    ConfigTable --> DetailsAction
    ConfigTable --> EditAction
    ConfigTable --> HistoryAction
    ConfigTable --> DeleteAction
    ConfigTable --> MoreMenu
    
    BatchActions --> ExportSelected
    BatchActions --> CloneSelected
    BatchActions --> DeleteSelected
    BatchActions --> ImportConfigs
    
    Pagination --> ConfigTable
```

### Configuration Editor Flow

```mermaid
sequenceDiagram
    participant User
    participant Editor as ConfigEditor Component
    participant Monaco as MonacoEditor Component
    participant Validator as Validation Logic
    participant API as Config API
    
    User->>Editor: Open configuration
    Editor->>API: GET /v3/console/cs/config
    API-->>Editor: Configuration data
    Editor->>Monaco: Initialize editor with content
    Monaco-->>Editor: Editor ready
    
    User->>Monaco: Edit configuration content
    Monaco->>Monaco: Syntax highlighting
    User->>Editor: Click "Publish"
    
    Editor->>Validator: Validate dataId, group, content
    alt Validation Failed
        Validator-->>User: Show error message
    else Validation Passed
        Editor->>Monaco: Get edited content
        Monaco-->>Editor: Return content
        Editor->>API: PUT /v3/console/cs/config
        API-->>Editor: Success/Failure response
        alt Success
            Editor-->>User: Show success message
            Editor->>Editor: Redirect to config list
        else Failure
            Editor-->>User: Show error message
        end
    end
```

**Sources:** [console-ui/src/locales/zh-CN.js:349-437](), [console-ui/src/locales/en-US.js:349-445]()

---

## Service Management UI

The Service Management UI allows operators to view, create, edit, and monitor services and their instances. It integrates with the Naming Service backend.

### Service List and Instance Management

```mermaid
graph TB
    subgraph "ServiceList Page"
        ServiceSearch["Service Search Panel<br/>Name & Group Filters"]
        ServiceTable["Service Table<br/>Name, Cluster, Instances"]
        ServiceActions["Service Actions<br/>Create, Detail, Delete"]
    end
    
    subgraph "ServiceDetail Page"
        ServiceInfo["Service Information<br/>Name, Group, Metadata"]
        ClusterTabs["Cluster Tabs<br/>One Tab Per Cluster"]
        InstanceTable["Instance Table<br/>IP, Port, Health, Weight"]
        InstanceFilter["Instance Filter<br/>Metadata Filtering"]
        InstanceActions["Instance Actions<br/>Edit, Online, Offline"]
    end
    
    subgraph "EditInstanceDialog"
        InstanceForm["Instance Form<br/>Port, Weight, Metadata"]
        MetadataEditor["Metadata Editor<br/>Key-Value Pairs"]
        OnlineToggle["Online Toggle<br/>Enable/Disable"]
    end
    
    subgraph "SubscriberList Page"
        SubscriberTable["Subscriber Table<br/>Address, Client Version, App"]
        SubscriberSearch["Subscriber Search<br/>Service Name Filter"]
    end
    
    ServiceList --> ServiceSearch
    ServiceList --> ServiceTable
    ServiceTable --> ServiceActions
    
    ServiceActions -->|"Details"| ServiceDetail
    
    ServiceDetail --> ServiceInfo
    ServiceDetail --> ClusterTabs
    ServiceDetail --> InstanceFilter
    ClusterTabs --> InstanceTable
    InstanceTable --> InstanceActions
    
    InstanceActions -->|"Edit"| EditInstanceDialog
    EditInstanceDialog --> InstanceForm
    InstanceForm --> MetadataEditor
    InstanceForm --> OnlineToggle
    
    ServiceList -->|"Subscribers"| SubscriberList
    SubscriberList --> SubscriberTable
    SubscriberList --> SubscriberSearch
```

### Service-to-Backend Integration

```mermaid
graph LR
    subgraph "UI Components"
        ServiceListComp["ServiceList<br/>React Component"]
        ServiceDetailComp["ServiceDetail<br/>React Component"]
    end
    
    subgraph "API Calls"
        GetServiceList["GET /v3/console/ns/service/list"]
        GetServiceDetail["GET /v3/console/ns/service"]
        GetInstanceList["GET /v3/console/ns/instance/list"]
        UpdateInstance["PUT /v3/console/ns/instance"]
        DeleteService["DELETE /v3/console/ns/service"]
    end
    
    subgraph "Backend Services"
        ServiceManagerClass["ServiceManager<br/>Service Registry"]
        InstanceController["InstanceController<br/>Instance CRUD"]
        DistroFilterClass["DistroFilter<br/>Request Distribution"]
    end
    
    ServiceListComp --> GetServiceList
    GetServiceList --> ServiceManagerClass
    
    ServiceDetailComp --> GetServiceDetail
    ServiceDetailComp --> GetInstanceList
    GetServiceDetail --> ServiceManagerClass
    GetInstanceList --> InstanceController
    
    ServiceDetailComp --> UpdateInstance
    ServiceDetailComp --> DeleteService
    UpdateInstance --> InstanceController
    DeleteService --> ServiceManagerClass
    
    InstanceController --> DistroFilterClass
```

**Sources:** [console-ui/src/locales/zh-CN.js:164-201](), [console-ui/src/locales/en-US.js:170-206]()

---

## AI and MCP Management System

The AI and MCP (Model Context Protocol) Management system is a newer feature that allows users to register, configure, and manage MCP servers and AI agents. This subsystem provides a sophisticated UI for defining tools, security schemes, and runtime configurations.

### MCP Server Management Architecture

```mermaid
graph TB
    subgraph "MCP Management UI Pages"
        McpManagement["McpManagement<br/>MCP Server List Page"]
        NewMcpServer["NewMcpServer<br/>Create/Edit MCP Server"]
        McpDetail["McpDetail<br/>View MCP Server Details"]
        ShowTools["ShowTools<br/>Tool Configuration UI"]
        CreateTools["CreateTools<br/>Tool Editor Dialog"]
    end
    
    subgraph "MCP Server Configuration"
        BasicInfo["Basic Information<br/>Name, Version, Protocol"]
        ServerConfig["Server Configuration<br/>Local or Remote"]
        LocalConfig["LocalServerConfig<br/>Command, Args, Env"]
        RemoteConfig["RemoteServerConfig<br/>Service Ref or Endpoint"]
        ToolSpec["Tool Specification<br/>Tools and Metadata"]
        SecuritySchemes["Security Schemes<br/>Authentication Config"]
    end
    
    subgraph "Tool Configuration Components"
        ToolList["Tool List Display"]
        ToolEditor["Tool Editor<br/>Input/Output Schema"]
        InputSchema["InputSchema Component<br/>Parameter Tree Editor"]
        OutputSchema["OutputSchema Component<br/>Return Value Editor"]
        AdvancedConfig["AdvancedConfig<br/>Templates, Security"]
        MetaEditor["MetaEditor<br/>Custom Metadata"]
        AnnotationsEditor["AnnotationsEditor<br/>Tool Hints"]
    end
    
    McpManagement -->|"Create/Edit"| NewMcpServer
    McpManagement -->|"View"| McpDetail
    
    NewMcpServer --> BasicInfo
    NewMcpServer --> ServerConfig
    ServerConfig --> LocalConfig
    ServerConfig --> RemoteConfig
    NewMcpServer --> ShowTools
    
    ShowTools --> ToolList
    ShowTools --> CreateTools
    
    CreateTools --> ToolEditor
    ToolEditor --> InputSchema
    ToolEditor --> OutputSchema
    ToolEditor --> AdvancedConfig
    ToolEditor --> MetaEditor
    ToolEditor --> AnnotationsEditor
    
    NewMcpServer --> ToolSpec
    NewMcpServer --> SecuritySchemes
    
    McpDetail --> ShowTools
```

### MCP Server Data Flow

```mermaid
sequenceDiagram
    participant User
    participant NewMcpServer as NewMcpServer Page
    participant ShowTools as ShowTools Component
    participant CreateTools as CreateTools Dialog
    participant API as MCP API
    participant Backend as MCP Backend Service
    
    User->>NewMcpServer: Create new MCP server
    NewMcpServer->>NewMcpServer: Initialize form fields
    
    User->>NewMcpServer: Configure basic info (name, version)
    User->>NewMcpServer: Select protocol (stdio/http/https)
    
    alt Local Server
        User->>NewMcpServer: Configure local server (command, args, env)
    else Remote Server
        User->>NewMcpServer: Configure remote server (service ref or endpoint)
    end
    
    User->>ShowTools: Add/Edit tools
    ShowTools->>CreateTools: Open tool editor
    User->>CreateTools: Define tool name, description
    User->>CreateTools: Configure input schema (parameters)
    User->>CreateTools: Configure output schema (return values)
    User->>CreateTools: Set security schemes
    CreateTools->>ShowTools: Return tool specification
    ShowTools->>NewMcpServer: Update tool list
    
    User->>NewMcpServer: Click "Create/Update"
    NewMcpServer->>NewMcpServer: Validate all fields
    NewMcpServer->>API: POST/PUT /v3/console/ai/mcp
    API->>Backend: Process MCP server configuration
    Backend->>API: Success response
    API->>NewMcpServer: Return result
    NewMcpServer->>User: Show success message
    NewMcpServer->>NewMcpServer: Redirect to MCP list
```

### Tool Schema Editor Structure

The tool schema editor uses a tree-based structure to represent nested parameters with support for complex types (objects, arrays).

```mermaid
graph TB
    subgraph "InputSchema Component"
        ArgumentsList["Arguments List<br/>Root Node"]
        ParamTree["Parameter Tree<br/>Nested Structure"]
        ParamEditor["Parameter Editor<br/>Name, Type, Description"]
    end
    
    subgraph "Parameter Types"
        StringType["string<br/>Simple String"]
        NumberType["number<br/>Numeric Value"]
        BooleanType["boolean<br/>True/False"]
        ObjectType["object<br/>Nested Properties"]
        ArrayType["array<br/>List of Items"]
    end
    
    subgraph "Parameter Attributes"
        Required["required<br/>Mandatory Parameter"]
        DefaultValue["defaultValue<br/>Default When Omitted"]
        EnumValues["enum<br/>Allowed Values"]
        Format["format<br/>Value Format"]
    end
    
    ArgumentsList --> ParamTree
    ParamTree --> ParamEditor
    
    ParamEditor --> StringType
    ParamEditor --> NumberType
    ParamEditor --> BooleanType
    ParamEditor --> ObjectType
    ParamEditor --> ArrayType
    
    ParamEditor --> Required
    ParamEditor --> DefaultValue
    ParamEditor --> EnumValues
    ParamEditor --> Format
    
    ObjectType -->|"has properties"| ParamTree
    ArrayType -->|"has items"| ParamTree
```

**Sources:** [console-ui/src/pages/AI/NewMcpServer/NewMcpServer.js:1-1000](), [console-ui/src/pages/AI/McpDetail/ShowTools.js:1-600](), [console-ui/src/pages/AI/McpDetail/CreateTools/index.js:1-400](), [console-ui/src/locales/zh-CN.js:885-1200](), [console-ui/src/locales/en-US.js:875-1150]()

---

## Localization System (i18n)

The console supports multiple languages through a comprehensive internationalization system. All user-facing text is externalized into locale files.

### Localization Architecture

```mermaid
graph LR
    subgraph "Locale Files"
        ZhCN["zh-CN.js<br/>Simplified Chinese"]
        EnUS["en-US.js<br/>English"]
    end
    
    subgraph "Configuration"
        LocaleConfig["I18N_CONF Object<br/>Nested Structure"]
        LanguageKey["LANGUAGE_KEY<br/>localStorage Key"]
    end
    
    subgraph "React Components"
        ConfigProvider["@ConfigProvider.config<br/>Decorator"]
        ComponentProps["props.locale<br/>Injected Locale Object"]
        ComponentRender["render()<br/>Uses locale strings"]
    end
    
    subgraph "User Interaction"
        LanguageSwitch["Language Switch Button<br/>Header Component"]
        LocalStorage["localStorage<br/>Persist Selection"]
    end
    
    ZhCN --> LocaleConfig
    EnUS --> LocaleConfig
    LocaleConfig --> LanguageKey
    
    LanguageSwitch -->|"Toggle Language"| LocalStorage
    LocalStorage -->|"Read"| LanguageKey
    LanguageKey -->|"Select Locale"| ConfigProvider
    ConfigProvider -->|"Inject"| ComponentProps
    ComponentProps --> ComponentRender
```

### Locale Object Structure

The locale files organize translations by functional area:

| Locale Key | Purpose | Example Keys |
|------------|---------|--------------|
| `Header` | Navigation and authentication | `home`, `docs`, `logout`, `changePassword` |
| `Login` | Login page | `login`, `pleaseInputUsername`, `submit` |
| `MainLayout` | Main navigation menu | `configurationManagement`, `serviceManagement`, `namespace` |
| `ConfigurationManagement` | Configuration list page | `createConfiguration`, `export`, `import`, `query` |
| `NewConfig` | Configuration editor | `newListingMain`, `publishFailed`, `dataIdIsNotEmpty` |
| `ServiceList` | Service list page | `serviceList`, `serviceName`, `query`, `detail` |
| `McpManagement` | MCP management | `mcpServerManagement`, `createMcpServer`, `importFromRegistry` |
| `PluginManagement` | Plugin management | `pluginManagement`, `enable`, `disable`, `configure` |

### Usage Pattern in Components

```javascript
// Component decorated with @ConfigProvider.config
@ConfigProvider.config
class MyComponent extends React.Component {
  static propTypes = {
    locale: PropTypes.object, // Injected by ConfigProvider
  };
  
  render() {
    const { locale } = this.props;
    return (
      <div>
        <h1>{locale.pageTitle}</h1>
        <Button>{locale.submitButton}</Button>
        <Message>{locale.successMessage}</Message>
      </div>
    );
  }
}
```

**Sources:** [console-ui/src/locales/zh-CN.js:17-1500](), [console-ui/src/locales/en-US.js:17-1500]()

---

## Namespace and Multi-Tenancy UI

Namespaces provide logical isolation for configurations and services. The console provides a namespace selector and management interface.

### Namespace Selection Flow

```mermaid
graph TB
    subgraph "Header Component"
        NamespaceSelector["Namespace Selector<br/>Dropdown or Tab View"]
        CurrentNamespace["Current Namespace Display<br/>Name and ID"]
    end
    
    subgraph "Namespace Management Page"
        NamespaceList["Namespace List<br/>Table View"]
        CreateButton["Create Namespace Button"]
        NamespaceActions["Actions Per Namespace<br/>Edit, Delete, Details"]
    end
    
    subgraph "Create/Edit Dialog"
        NamespaceForm["Namespace Form"]
        NamespaceId["Namespace ID<br/>Auto-generated or Manual"]
        NamespaceName["Namespace Name<br/>Display Name"]
        NamespaceDesc["Description<br/>Optional Text"]
    end
    
    subgraph "State Management"
        GlobalState["window.nownamespace<br/>Global Namespace Context"]
        URLParams["URL Parameters<br/>namespace=xxx"]
        LocalStorage["localStorage<br/>Persist Selection"]
    end
    
    NamespaceSelector -->|"Select"| GlobalState
    GlobalState --> URLParams
    URLParams -->|"Filter Data"| ConfigAPI["Config API Calls"]
    URLParams -->|"Filter Data"| ServiceAPI["Service API Calls"]
    
    NamespaceList --> NamespaceActions
    CreateButton --> NamespaceForm
    NamespaceActions -->|"Edit"| NamespaceForm
    
    NamespaceForm --> NamespaceId
    NamespaceForm --> NamespaceName
    NamespaceForm --> NamespaceDesc
    
    GlobalState --> LocalStorage
```

### Namespace-Aware API Requests

All API requests include the current namespace context:

```mermaid
sequenceDiagram
    participant UI as React Component
    participant Global as Global State (window.nownamespace)
    participant Request as request() Utility
    participant API as Backend API
    
    UI->>Global: Get current namespace ID
    Global-->>UI: namespace ID
    UI->>Request: request({url, data: {namespaceId}})
    Request->>Request: Append namespace to query params
    Request->>API: GET /v3/console/.../list?namespaceId=xxx
    API->>API: Filter by namespace
    API-->>Request: Namespace-filtered results
    Request-->>UI: Display data
```

**Sources:** [console-ui/src/locales/zh-CN.js:138-163](), [console-ui/src/locales/en-US.js:144-169]()

---

## Authentication and Authorization UI

The console implements a complete authentication and authorization system with user management, role-based access control, and permission management.

### Login Flow

```mermaid
sequenceDiagram
    participant User
    participant LoginPage as Login Page
    participant API as Auth API
    participant Backend as Auth Backend
    participant Storage as localStorage
    
    User->>LoginPage: Navigate to /login
    LoginPage->>LoginPage: Display login form
    User->>LoginPage: Enter username & password
    LoginPage->>API: POST /v3/console/auth/login
    API->>Backend: Validate credentials
    
    alt Authentication Success
        Backend-->>API: JWT token + access token
        API-->>LoginPage: {code: 0, data: {token, accessToken}}
        LoginPage->>Storage: Save tokens to localStorage
        LoginPage->>LoginPage: Redirect to main page
    else Authentication Failed
        Backend-->>API: Error response
        API-->>LoginPage: {code: 401, message: "Invalid credentials"}
        LoginPage->>User: Display error message
    end
```

### Authority Management UI Components

```mermaid
graph TB
    subgraph "User Management"
        UserList["UserManagement<br/>User List Page"]
        CreateUser["NewUser Dialog<br/>Create User Form"]
        ResetPassword["PasswordReset Dialog<br/>Reset User Password"]
    end
    
    subgraph "Role Management"
        RoleList["RolesManagement<br/>Role List Page"]
        BindRole["NewRole Dialog<br/>Bind User to Role"]
    end
    
    subgraph "Permission Management"
        PermissionList["PermissionsManagement<br/>Permission List Page"]
        AddPermission["NewPermissions Dialog<br/>Assign Permission to Role"]
    end
    
    subgraph "Permission Model"
        User["User<br/>Username"]
        Role["Role<br/>Role Name"]
        Resource["Resource<br/>Config/Service/Namespace"]
        Action["Action<br/>Read/Write/Delete"]
    end
    
    UserList --> CreateUser
    UserList --> ResetPassword
    
    RoleList --> BindRole
    BindRole -->|"Assigns"| User
    BindRole -->|"To"| Role
    
    PermissionList --> AddPermission
    AddPermission -->|"Grants"| Role
    AddPermission -->|"Access to"| Resource
    AddPermission -->|"With"| Action
```

### Permission Enforcement

```mermaid
graph LR
    subgraph "Frontend"
        Component["React Component<br/>User Action"]
        AuthCheck["Check localStorage token"]
    end
    
    subgraph "Backend"
        AuthFilter["Auth Filter<br/>Validate JWT"]
        PermissionCheck["Permission Check<br/>Verify RBAC"]
        ResourceAccess["Resource Access<br/>Config/Service Operation"]
    end
    
    Component --> AuthCheck
    AuthCheck -->|"Token Present"| AuthFilter
    AuthCheck -->|"No Token"| LoginRedirect["Redirect to Login"]
    
    AuthFilter -->|"Valid Token"| PermissionCheck
    AuthFilter -->|"Invalid/Expired"| LoginRedirect
    
    PermissionCheck -->|"Has Permission"| ResourceAccess
    PermissionCheck -->|"No Permission"| Forbidden["403 Forbidden"]
```

**Sources:** [console-ui/src/locales/zh-CN.js:647-743](), [console-ui/src/locales/en-US.js:648-743]()

---

## Plugin Management UI

The Plugin Management system allows administrators to view, enable, disable, and configure Nacos plugins at runtime.

### Plugin Management Page Structure

```mermaid
graph TB
    subgraph "PluginManagement Page"
        SearchPanel["Search Panel<br/>Name, Type, Status Filters"]
        PluginTable["Plugin Table<br/>Display All Plugins"]
        PluginActions["Actions Per Plugin<br/>Detail, Enable, Disable, Configure"]
    end
    
    subgraph "Plugin Types"
        AuthPlugin["auth<br/>Authentication Plugin"]
        DatasourcePlugin["datasource-dialect<br/>Database Plugin"]
        ConfigChangePlugin["config-change<br/>Config Change Plugin"]
        EncryptionPlugin["encryption<br/>Encryption Plugin"]
        TracePlugin["trace<br/>Trace Plugin"]
        ControlPlugin["control<br/>Control Plugin"]
        EnvironmentPlugin["environment<br/>Environment Plugin"]
    end
    
    subgraph "PluginDetail Dialog"
        BasicInfo["Basic Information<br/>Name, Type, Status"]
        ConfigItems["Configuration Items<br/>Editable Fields"]
        NodeAvailability["Node Availability<br/>Cluster Status"]
        SaveConfig["Save Configuration Button"]
    end
    
    PluginTable --> PluginActions
    PluginActions -->|"Detail"| PluginDetail
    
    PluginDetail --> BasicInfo
    PluginDetail --> ConfigItems
    PluginDetail --> NodeAvailability
    PluginDetail --> SaveConfig
    
    SearchPanel -->|"Filter by Type"| AuthPlugin
    SearchPanel -->|"Filter by Type"| DatasourcePlugin
    SearchPanel -->|"Filter by Type"| ConfigChangePlugin
    SearchPanel -->|"Filter by Type"| EncryptionPlugin
    SearchPanel -->|"Filter by Type"| TracePlugin
    SearchPanel -->|"Filter by Type"| ControlPlugin
    SearchPanel -->|"Filter by Type"| EnvironmentPlugin
```

### Plugin Lifecycle Operations

```mermaid
sequenceDiagram
    participant Admin
    participant PluginUI as PluginManagement UI
    participant PluginAPI as Plugin API
    participant PluginService as Plugin Service
    participant AllNodes as All Cluster Nodes
    
    Admin->>PluginUI: View plugin list
    PluginUI->>PluginAPI: GET /v3/console/plugin/list
    PluginAPI->>PluginService: Query all plugins
    PluginService-->>PluginAPI: Plugin list with status
    PluginAPI-->>PluginUI: Display plugins
    
    Admin->>PluginUI: Click "Enable" on disabled plugin
    PluginUI->>PluginAPI: POST /v3/console/plugin/enable
    PluginAPI->>PluginService: Enable plugin
    PluginService->>AllNodes: Notify all nodes to load plugin
    AllNodes-->>PluginService: Acknowledgment
    PluginService-->>PluginAPI: Success
    PluginAPI-->>PluginUI: Plugin enabled
    
    Admin->>PluginUI: Click "Configure" on plugin
    PluginUI->>PluginAPI: GET /v3/console/plugin/{pluginName}
    PluginAPI-->>PluginUI: Plugin config schema
    PluginUI->>Admin: Display config dialog
    Admin->>PluginUI: Modify config values
    PluginUI->>PluginAPI: PUT /v3/console/plugin/{pluginName}/config
    PluginAPI->>PluginService: Update plugin config
    PluginService->>AllNodes: Distribute new config
    AllNodes-->>PluginService: Config applied
    PluginService-->>PluginAPI: Success
    PluginAPI-->>PluginUI: Config updated
```

**Sources:** [console-ui/src/locales/zh-CN.js:83-128](), [console-ui/src/locales/en-US.js:88-129]()

---

## Build System and Deployment

The console UI is built using Webpack 4 and deployed as static assets served by the Nacos server.

### Build Process Architecture

```mermaid
graph LR
    subgraph "Source Files"
        ReactComponents["React Components<br/>console-ui/src"]
        SCSS["SCSS Styles<br/>*.scss"]
        Assets["Static Assets<br/>Images, Fonts"]
        LocaleFiles["Locale Files<br/>i18n/*.js"]
    end
    
    subgraph "Build Tools"
        Webpack["Webpack 4<br/>webpack.config.js"]
        BabelLoader["babel-loader<br/>JSX → JS"]
        SASSLoader["sass-loader<br/>SCSS → CSS"]
        MiniCSSExtract["mini-css-extract-plugin<br/>Extract CSS"]
        UglifyJS["uglifyjs-webpack-plugin<br/>Minify JS"]
    end
    
    subgraph "Build Output"
        MainJS["main.js<br/>Bundled JavaScript"]
        MainCSS["main.css<br/>Bundled Styles"]
        IndexHTML["index.html<br/>Entry Point"]
        ChunkJS["Chunk JS Files<br/>Code Split Bundles"]
    end
    
    subgraph "Deployment Target"
        ConsoleStatic["console/src/main/resources/static/<br/>Nacos Server Static Dir"]
        JavaServer["Nacos Server<br/>Serves Static Files"]
    end
    
    ReactComponents --> BabelLoader
    SCSS --> SASSLoader
    LocaleFiles --> BabelLoader
    
    BabelLoader --> Webpack
    SASSLoader --> MiniCSSExtract
    MiniCSSExtract --> Webpack
    Assets --> Webpack
    
    Webpack --> MainJS
    Webpack --> MainCSS
    Webpack --> IndexHTML
    Webpack --> ChunkJS
    
    MainJS --> ConsoleStatic
    MainCSS --> ConsoleStatic
    IndexHTML --> ConsoleStatic
    ChunkJS --> ConsoleStatic
    
    ConsoleStatic --> JavaServer
```

### Build Scripts and Configuration

| npm Script | Purpose | Command |
|------------|---------|---------|
| `start` | Development server with hot reload | `cross-env NODE_ENV=development webpack-dev-server` |
| `build` | Production build with optimization | `cross-env NODE_ENV=production webpack` |
| `eslint` | Run linter on source files | `eslint --ext .js src/` |
| `eslint-fix` | Auto-fix linting issues | `eslint --ext .js --fix src/` |

### Webpack Configuration Highlights

Key features of the Webpack configuration:

1. **Code Splitting**: Lazy loading of route components using dynamic imports
2. **CSS Extraction**: Separate CSS files for better caching
3. **Asset Optimization**: Image and font compression
4. **Source Maps**: Generated for development builds
5. **Bundle Analysis**: Optional plugin to analyze bundle size
6. **Theme Support**: Alibaba Fusion Design theme compilation via `@alifd/next-theme-loader`

**Sources:** [console-ui/package.json:6-11](), [console-ui/package.json:28-70]()

---

## Component Library and UI Framework

The console uses Alibaba's Fusion Design component library (`@alifd/next`) for consistent UI components.

### Core UI Components Used

| Component | Usage | Pages |
|-----------|-------|-------|
| `Table` | Data tables with pagination, sorting, selection | Configuration List, Service List, User List, Plugin List |
| `Form` | Input forms with validation | Configuration Editor, User Management, MCP Server Editor |
| `Dialog` | Modal dialogs for confirmations and forms | Delete confirmations, Create/Edit dialogs |
| `Button` | Action buttons with various styles | All pages |
| `Input` | Text input fields with search support | Search panels, form fields |
| `Select` | Dropdown selectors for filters | Namespace selector, type filters |
| `Message` | Toast notifications for success/error | All CRUD operations |
| `Loading` | Loading spinners for async operations | All data fetching scenarios |
| `Tab` | Tab navigation within pages | Service Detail (clusters), MCP Server Editor (tabs) |
| `Tree` | Hierarchical data display | Parameter schema editors |
| `MonacoEditor` | Code editor with syntax highlighting | Configuration content editor |

### Theme Customization

The console uses `@alifd/theme-design-pro` for a professional look:

```javascript
// Theme is applied via next-theme-loader in webpack config
// Customizes colors, spacing, typography for all @alifd/next components
```

**Sources:** [console-ui/package.json:67-88](), [console/src/main/resources/static/index.html:29-37]()

---

## Error Handling and User Feedback

The console implements comprehensive error handling with user-friendly feedback mechanisms.

### Error Handling Flow

```mermaid
graph TB
    subgraph "User Action"
        UserClick["User Clicks Button<br/>e.g., Save Configuration"]
    end
    
    subgraph "Frontend Validation"
        ClientValidation["Client-Side Validation<br/>Field.validate()"]
        ValidationError["Validation Error"]
        ShowFieldError["Display Field Error<br/>Red Border + Message"]
    end
    
    subgraph "API Call"
        RequestUtil["request() Utility"]
        NetworkError["Network Error<br/>Timeout, Connection Failed"]
        ShowNetworkError["Show Network Error Toast"]
    end
    
    subgraph "Backend Response"
        SuccessResponse["Success (code: 0)"]
        ErrorResponse["Error (code: 401, 403, 500, etc.)"]
        ShowSuccessMsg["Show Success Toast<br/>Message.success()"]
        ShowErrorMsg["Show Error Toast<br/>Message.error()"]
    end
    
    subgraph "Special Error Handling"
        AuthError["401/403 Auth Error"]
        RedirectLogin["Clear Token & Redirect to Login<br/>goLogin()"]
    end
    
    UserClick --> ClientValidation
    ClientValidation -->|"Valid"| RequestUtil
    ClientValidation -->|"Invalid"| ValidationError
    ValidationError --> ShowFieldError
    
    RequestUtil -->|"Network Issue"| NetworkError
    NetworkError --> ShowNetworkError
    
    RequestUtil -->|"Response Received"| SuccessResponse
    RequestUtil -->|"Response Received"| ErrorResponse
    
    SuccessResponse --> ShowSuccessMsg
    ErrorResponse --> ShowErrorMsg
    
    ErrorResponse -->|"401/403"| AuthError
    AuthError --> RedirectLogin
```

### Error Message Localization

Error messages are localized and context-specific:

```javascript
// Example from ConfigEditor
if (result.code === 0) {
  Message.success(locale.publishSuccess);
  this.props.history.push('/configurationManagement');
} else if (result.code === 403) {
  Message.error(locale.publishFailed403); // "Publish failed. No permission"
} else {
  Message.error(result.message || locale.publishFailed); // Generic or server message
}
```

**Sources:** [console/src/main/resources/static/js/main.js:1-1]()

---

## Summary

The Nacos Console and Management UI is a comprehensive React-based web application that provides:

1. **Configuration Management**: Full CRUD operations, version history, import/export, and cloning capabilities
2. **Service Management**: Service and instance registration, health monitoring, and subscriber tracking
3. **AI/MCP Integration**: Advanced MCP server configuration with tool schema editors and security management
4. **Namespace Isolation**: Multi-tenancy support with namespace-based data segregation
5. **Access Control**: User, role, and permission management with RBAC enforcement
6. **Plugin Management**: Runtime plugin configuration and lifecycle management
7. **Internationalization**: Full i18n support for Chinese and English
8. **Modern Build System**: Webpack-based build with code splitting and optimization

The UI communicates with backend REST APIs under `/v3/console/` and maintains authentication state using JWT tokens stored in localStorage. The architecture emphasizes component reusability, type safety via PropTypes, and comprehensive error handling with localized user feedback.

---

