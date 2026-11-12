<!-- source: DeepWiki mcp.deepwiki.com · repo Rootly-AI-Labs/Rootly-MCP-server · page 7 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/rootly_mcp_server/__main__.py](src/rootly_mcp_server/__main__.py)
- [src/rootly_mcp_server/client.py](src/rootly_mcp_server/client.py)
- [src/rootly_mcp_server/server.py](src/rootly_mcp_server/server.py)
- [src/rootly_mcp_server/utils.py](src/rootly_mcp_server/utils.py)

</details>



This page documents the complete public API surface of the Rootly MCP Server. It covers all functions, classes, and methods that developers use to create, configure, and interact with the server. For information about internal implementation details and custom tool development, see [Custom Tool Development](#4.5). For information about testing utilities and fixtures, see [Test Fixtures & Utilities](#5.5).

## Overview

The Rootly MCP Server exposes three primary API layers:

1. **Server Creation API** - Functions for initializing and configuring the MCP server
2. **HTTP Client API** - Classes for authenticated communication with the Rootly API
3. **Utility API** - Helper functions for parameter sanitization and error handling

```mermaid
graph TB
    subgraph "Entry Points"
        Main["__main__.main()"]
        GetServer["__main__.get_server()"]
        MCPInstance["__main__.mcp (module-level)"]
    end
    
    subgraph "Server Creation API"
        CreateServer["server.create_rootly_mcp_server()"]
        LoadSwagger["server._load_swagger_spec()"]
        FilterSpec["server._filter_openapi_spec()"]
    end
    
    subgraph "Client API"
        AuthClient["server.AuthenticatedHTTPXClient"]
        RootlyClient["client.RootlyClient"]
    end
    
    subgraph "Utility API"
        SanitizeParam["utils.sanitize_parameter_name()"]
        SanitizeSpec["utils.sanitize_parameters_in_spec()"]
        MCPError["server.MCPError"]
    end
    
    subgraph "FastMCP Integration"
        FastMCP["FastMCP instance"]
        Tools["MCP Tools"]
        Resources["MCP Resources"]
    end
    
    Main --> GetServer
    GetServer --> CreateServer
    MCPInstance --> CreateServer
    
    CreateServer --> LoadSwagger
    CreateServer --> FilterSpec
    CreateServer --> SanitizeSpec
    CreateServer --> AuthClient
    CreateServer --> FastMCP
    
    FastMCP --> Tools
    FastMCP --> Resources
    
    AuthClient --> RootlyClient
    
    SanitizeSpec --> SanitizeParam
    Tools --> MCPError
    
    style CreateServer fill:#f9f9f9,stroke:#333,stroke-width:2px
    style AuthClient fill:#f9f9f9,stroke:#333,stroke-width:2px
    style SanitizeSpec fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [src/rootly_mcp_server/server.py:278-344](), [src/rootly_mcp_server/__main__.py:120-145](), [src/rootly_mcp_server/client.py:15-28](), [src/rootly_mcp_server/utils.py:45-105]()

---

## Server Creation API

### create_rootly_mcp_server()

The primary function for creating a configured Rootly MCP Server instance.

**Function Signature:**

```python
def create_rootly_mcp_server(
    swagger_path: Optional[str] = None,
    name: str = "Rootly",
    allowed_paths: Optional[List[str]] = None,
    hosted: bool = False,
    base_url: Optional[str] = None,
) -> FastMCP
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `swagger_path` | `Optional[str]` | `None` | Path to local Swagger JSON file. If `None`, fetches from `SWAGGER_URL` |
| `name` | `str` | `"Rootly"` | Name of the MCP server instance |
| `allowed_paths` | `Optional[List[str]]` | `None` | API paths to expose as tools. If `None`, uses `DEFAULT_ALLOWED_PATHS` |
| `hosted` | `bool` | `False` | Enable hosted mode (authentication from MCP headers instead of env) |
| `base_url` | `Optional[str]` | `None` | Rootly API base URL. If `None`, uses `ROOTLY_BASE_URL` env var or default |

**Returns:** `FastMCP` - Configured FastMCP server instance with generated tools

**Implementation Details:**

The function performs the following initialization sequence:

```mermaid
sequenceDiagram
    participant Caller
    participant CreateServer["create_rootly_mcp_server()"]
    participant LoadSpec["_load_swagger_spec()"]
    participant FilterSpec["_filter_openapi_spec()"]
    participant SanitizeSpec["sanitize_parameters_in_spec()"]
    participant AuthClient["AuthenticatedHTTPXClient"]
    participant FastMCP
    
    Caller->>CreateServer: Call with config
    CreateServer->>CreateServer: Set default allowed_paths
    CreateServer->>CreateServer: Add /v1 prefix to paths
    CreateServer->>LoadSpec: Load OpenAPI spec
    LoadSpec-->>CreateServer: Raw spec dict
    CreateServer->>FilterSpec: Filter to allowed paths
    FilterSpec-->>CreateServer: Filtered spec
    CreateServer->>SanitizeSpec: Sanitize parameter names
    SanitizeSpec-->>CreateServer: Sanitized spec + mapping
    CreateServer->>AuthClient: Create with parameter_mapping
    AuthClient-->>CreateServer: Client instance
    CreateServer->>FastMCP: from_openapi(spec, client)
    FastMCP-->>CreateServer: MCP instance
    CreateServer->>CreateServer: Register custom tools
    CreateServer-->>Caller: Configured server
```

**Sources:** [src/rootly_mcp_server/server.py:278-344]()

### DEFAULT_ALLOWED_PATHS

Pre-configured list of Rootly API paths that are exposed as MCP tools by default.

**Type:** `List[str]`

**Contents:** 40+ API endpoints including:
- Incident operations: `/incidents/{incident_id}/alerts`, `/alerts`, `/alerts/{alert_id}`
- Team management: `/teams`, `/teams/{team_id}`
- Service catalog: `/services`, `/services/{service_id}`, `/environments`
- On-call schedules: `/schedules`, `/schedules/{schedule_id}/shifts`, `/shifts`
- Workflow management: `/workflows`, `/workflow_runs`
- Status pages: `/status_pages`, `/status_pages/{status_page_id}`

**Sources:** [src/rootly_mcp_server/server.py:121-172]()

### Entry Point Functions

#### get_server()

Factory function for creating server instances from environment variables. Used by FastMCP CLI.

**Function Signature:**

```python
def get_server() -> FastMCP
```

**Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `ROOTLY_SWAGGER_PATH` | Path to local Swagger file | `None` (fetch remote) |
| `ROOTLY_SERVER_NAME` | Server instance name | `"Rootly"` |
| `ROOTLY_HOSTED` | Enable hosted mode | `"false"` |
| `ROOTLY_BASE_URL` | API base URL | `None` (use default) |
| `ROOTLY_ALLOWED_PATHS` | Comma-separated path list | `None` (use defaults) |

**Returns:** Configured `FastMCP` instance

**Sources:** [src/rootly_mcp_server/__main__.py:120-141]()

#### main()

Command-line entry point with argument parsing and logging configuration.

**Function Signature:**

```python
def main() -> None
```

**Command-Line Arguments:**

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--swagger-path` | `str` | Auto-discover | Path to Swagger JSON file |
| `--log-level` | `str` | `"INFO"` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--name` | `str` | `"Rootly"` | Server name |
| `--transport` | `str` | `"stdio"` | Transport protocol (stdio, sse) |
| `--debug` | flag | `False` | Enable debug mode |
| `--base-url` | `str` | `None` | Rootly API base URL |
| `--allowed-paths` | `str` | `None` | Comma-separated path list |
| `--hosted` | flag | `False` | Enable hosted mode |

**Behavior:**
- Validates `ROOTLY_API_TOKEN` environment variable (unless `--hosted`)
- Configures logging to stderr
- Creates and runs server with specified transport

**Sources:** [src/rootly_mcp_server/__main__.py:148-192]()

---

## HTTP Client API

### AuthenticatedHTTPXClient

HTTPX-based client wrapper that handles Rootly API authentication and bidirectional parameter transformation.

**Class Definition:**

```python
class AuthenticatedHTTPXClient:
    def __init__(
        self,
        base_url: str = "https://api.rootly.com",
        hosted: bool = False,
        parameter_mapping: Optional[Dict[str, str]] = None
    )
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `_base_url` | `str` | Rootly API base URL |
| `hosted` | `bool` | Whether running in hosted mode |
| `_api_token` | `Optional[str]` | API token (local mode only) |
| `parameter_mapping` | `Dict[str, str]` | Map of sanitized → original parameter names |
| `client` | `httpx.AsyncClient` | Underlying async HTTP client |

**Methods:**

#### \_\_init\_\_()

Initializes the client with authentication and parameter transformation capabilities.

```mermaid
graph LR
    Init["__init__()"]
    GetToken["_get_api_token()"]
    CreateClient["Create httpx.AsyncClient"]
    
    Init --> GetToken
    Init --> CreateClient
    
    GetToken --> |"hosted=False"| ReadEnv["Read ROOTLY_API_TOKEN"]
    GetToken --> |"hosted=True"| Skip["Skip token retrieval"]
    
    CreateClient --> SetHeaders["Set JSON:API headers"]
    SetHeaders --> AddAuth["Add Authorization header"]
    AddAuth --> ConfigClient["Configure timeouts & limits"]
```

**Sources:** [src/rootly_mcp_server/server.py:178-203]()

#### _get_api_token()

Retrieves API token from environment variables.

**Returns:** `Optional[str]` - API token or `None` if not found

**Logs Warning:** If `ROOTLY_API_TOKEN` not set

**Sources:** [src/rootly_mcp_server/server.py:205-211]()

#### _transform_params()

Transforms sanitized parameter names back to original Rootly API format.

**Function Signature:**

```python
def _transform_params(self, params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]
```

**Parameter Transformation Flow:**

```mermaid
graph TB
    Input["Input params<br/>{filter_status: 'resolved'}"]
    
    CheckMapping{"parameter_mapping<br/>exists?"}
    
    Transform["Transform each key:<br/>sanitized → original"]
    
    Lookup["Lookup in mapping:<br/>filter_status → filter[status]"]
    
    Output["Output params<br/>{filter[status]: 'resolved'}"]
    
    NoOp["Return unchanged"]
    
    Input --> CheckMapping
    CheckMapping -->|Yes| Transform
    CheckMapping -->|No| NoOp
    
    Transform --> Lookup
    Lookup --> Output
```

**Example:**

```python
# Mapping: {"filter_status": "filter[status]", "page_size": "page[size]"}
params = {"filter_status": "resolved", "page_size": 10}
transformed = client._transform_params(params)
# Result: {"filter[status]": "resolved", "page[size]": 10}
```

**Sources:** [src/rootly_mcp_server/server.py:213-225]()

#### request() / get() / post() / put() / patch() / delete()

HTTP method wrappers that apply parameter transformation before forwarding to underlying client.

**Function Signatures:**

```python
async def request(self, method: str, url: str, **kwargs)
async def get(self, url: str, **kwargs)
async def post(self, url: str, **kwargs)
async def put(self, url: str, **kwargs)
async def patch(self, url: str, **kwargs)
async def delete(self, url: str, **kwargs)
```

**Behavior:**
1. Transforms `params` kwarg using `_transform_params()`
2. Delegates to `httpx.AsyncClient.request()`
3. Returns `httpx.Response`

**Sources:** [src/rootly_mcp_server/server.py:227-254]()

#### Properties

**base_url**

**Type:** `str`

**Returns:** The configured base URL for API requests

**Sources:** [src/rootly_mcp_server/server.py:269-271]()

**headers**

**Type:** `httpx.Headers`

**Returns:** Current HTTP headers from underlying client

**Sources:** [src/rootly_mcp_server/server.py:273-275]()

---

### RootlyClient

Legacy synchronous HTTP client for Rootly API. Used in legacy code paths.

**Class Definition:**

```python
class RootlyClient:
    def __init__(self, base_url: Optional[str] = None, hosted: bool = False)
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `base_url` | `str` | Rootly API base URL |
| `hosted` | `bool` | Whether running in hosted mode |
| `_api_token` | `str` | API token (local mode only) |

**Methods:**

#### make_request()

Synchronous HTTP request method with JSON:API support.

**Function Signature:**

```python
def make_request(
    self,
    method: str,
    path: str,
    query_params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    json_api_type: Optional[str] = None,
    api_token: Optional[str] = None,
) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `method` | `str` | HTTP method (GET, POST, PUT, PATCH, DELETE) |
| `path` | `str` | API path (auto-prefixed with `/v1` if missing) |
| `query_params` | `Optional[Dict]` | URL query parameters |
| `json_data` | `Optional[Dict]` | Request body data |
| `json_api_type` | `Optional[str]` | JSON:API type for wrapping payload |
| `api_token` | `Optional[str]` | Override token (hosted mode) |

**Returns:** `str` - JSON-formatted response or error

**JSON:API Format:**

When `json_api_type` is provided, the client automatically:
1. Sets `Content-Type: application/vnd.api+json` header
2. Wraps `json_data` in JSON:API envelope:

```json
{
  "data": {
    "type": "incidents",
    "attributes": { ...json_data... }
  }
}
```

**Sources:** [src/rootly_mcp_server/client.py:30-132]()

---

## Utility API

### Parameter Sanitization

#### sanitize_parameter_name()

Transforms parameter names to match MCP property key pattern `^[a-zA-Z0-9_.-]{1,64}$`.

**Function Signature:**

```python
def sanitize_parameter_name(name: str) -> str
```

**Transformation Rules:**

```mermaid
graph TB
    Input["Input: filter[status]"]
    
    Rule1["Replace brackets:<br/>filter[status] → filter_status"]
    Rule2["Replace invalid chars:<br/>[^a-zA-Z0-9_.-] → _"]
    Rule3["Remove multiple underscores:<br/>a__b → a_b"]
    Rule4["Strip leading/trailing _"]
    Rule5["Truncate to 64 chars"]
    Rule6["Ensure valid start:<br/>prepend 'param_' if starts with digit"]
    
    Output["Output: filter_status"]
    
    Input --> Rule1
    Rule1 --> Rule2
    Rule2 --> Rule3
    Rule3 --> Rule4
    Rule4 --> Rule5
    Rule5 --> Rule6
    Rule6 --> Output
```

**Examples:**

| Input | Output | Notes |
|-------|--------|-------|
| `filter[status]` | `filter_status` | Brackets replaced |
| `page[size]` | `page_size` | Brackets replaced |
| `fields[incidents]` | `fields_incidents` | Brackets replaced |
| `filter[kind][]` | `filter_kind` | Multiple brackets handled |
| `include` | `include` | Already valid |
| `123invalid` | `param_123invalid` | Prepended with `param_` |

**Sources:** [src/rootly_mcp_server/utils.py:12-42]()

#### sanitize_parameters_in_spec()

Sanitizes all parameter names throughout an OpenAPI specification and builds a reverse mapping.

**Function Signature:**

```python
def sanitize_parameters_in_spec(spec: Dict[str, Any]) -> Dict[str, str]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `spec` | `Dict[str, Any]` | OpenAPI specification (modified in-place) |

**Returns:** `Dict[str, str]` - Mapping of sanitized names → original names

**Processing Locations:**

1. **Path-level parameters** - `spec['paths'][path]['parameters']`
2. **Operation-level parameters** - `spec['paths'][path][method]['parameters']`
3. **Component parameters** - `spec['components']['parameters']` (OpenAPI 3.0)

**Example Mapping:**

```python
{
    "filter_status": "filter[status]",
    "page_size": "page[size]",
    "page_number": "page[number]",
    "fields_incidents": "fields[incidents]"
}
```

**Sources:** [src/rootly_mcp_server/utils.py:45-105]()

---

### Error Handling

#### MCPError

Static error formatting utility for MCP-compliant error responses.

**Class Definition:**

```python
class MCPError:
    @staticmethod
    def protocol_error(code: int, message: str, data: Optional[Dict] = None)
    
    @staticmethod
    def tool_error(error_message: str, error_type: str = "execution_error", details: Optional[Dict] = None)
    
    @staticmethod
    def categorize_error(exception: Exception) -> tuple[str, str]
```

**Methods:**

#### protocol_error()

Creates JSON-RPC protocol-level error response.

**Function Signature:**

```python
@staticmethod
def protocol_error(code: int, message: str, data: Optional[Dict] = None) -> Dict
```

**Returns:**

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Error description",
    "data": { "additional": "context" }
  }
}
```

**Sources:** [src/rootly_mcp_server/server.py:31-43]()

#### tool_error()

Creates tool-level error response (returned as successful tool execution with error flag).

**Function Signature:**

```python
@staticmethod
def tool_error(error_message: str, error_type: str = "execution_error", details: Optional[Dict] = None) -> Dict
```

**Error Types:**
- `authentication_error`
- `network_error`
- `client_error`
- `server_error`
- `validation_error`
- `execution_error`

**Returns:**

```json
{
  "error": true,
  "error_type": "authentication_error",
  "message": "Authentication failed: 401 Unauthorized",
  "details": { "status_code": 401 }
}
```

**Sources:** [src/rootly_mcp_server/server.py:45-55]()

#### categorize_error()

Analyzes an exception and returns appropriate error type and message.

**Function Signature:**

```python
@staticmethod
def categorize_error(exception: Exception) -> tuple[str, str]
```

**Returns:** `(error_type, error_message)` tuple

**Categorization Logic:**

```mermaid
graph TB
    Exception["Exception object"]
    
    CheckAuth{"Contains '401',<br/>'unauthorized',<br/>'token'?"}
    CheckNetwork{"Exception type<br/>contains 'connection',<br/>'timeout'?"}
    Check4xx{"Status code<br/>starts with '4'?"}
    Check5xx{"Status code<br/>starts with '5'?"}
    CheckValidation{"Exception type<br/>contains 'validation',<br/>'pydantic'?"}
    
    AuthError["authentication_error"]
    NetworkError["network_error"]
    ClientError["client_error"]
    ServerError["server_error"]
    ValidationError["validation_error"]
    ExecutionError["execution_error"]
    
    Exception --> CheckAuth
    CheckAuth -->|Yes| AuthError
    CheckAuth -->|No| CheckNetwork
    CheckNetwork -->|Yes| NetworkError
    CheckNetwork -->|No| Check4xx
    Check4xx -->|Yes| ClientError
    Check4xx -->|No| Check5xx
    Check5xx -->|Yes| ServerError
    Check5xx -->|No| CheckValidation
    CheckValidation -->|Yes| ValidationError
    CheckValidation -->|No| ExecutionError
```

**Sources:** [src/rootly_mcp_server/server.py:57-82]()

---

## Configuration Constants

### SWAGGER_URL

Default URL for fetching Rootly's OpenAPI specification.

**Value:** `"https://rootly-heroku.s3.amazonaws.com/swagger/v1/swagger.json"`

**Type:** `str`

**Sources:** [src/rootly_mcp_server/server.py:85]()

---

## API Usage Patterns

### Complete Initialization Flow

```mermaid
sequenceDiagram
    participant User
    participant Main["__main__.py"]
    participant CreateServer["create_rootly_mcp_server()"]
    participant Utils["utils.py"]
    participant AuthClient["AuthenticatedHTTPXClient"]
    participant FastMCP
    
    User->>Main: python -m rootly_mcp_server
    Main->>Main: parse_args()
    Main->>Main: setup_logging()
    Main->>Main: check_api_token()
    
    Main->>CreateServer: Call with config
    
    CreateServer->>CreateServer: Load OpenAPI spec
    CreateServer->>CreateServer: Filter to allowed_paths
    
    CreateServer->>Utils: sanitize_parameters_in_spec(spec)
    Utils-->>CreateServer: parameter_mapping
    
    CreateServer->>AuthClient: new(base_url, hosted, mapping)
    AuthClient->>AuthClient: Read ROOTLY_API_TOKEN
    AuthClient->>AuthClient: Create httpx.AsyncClient
    AuthClient-->>CreateServer: Client instance
    
    CreateServer->>FastMCP: from_openapi(spec, client)
    FastMCP-->>CreateServer: MCP instance
    
    CreateServer->>CreateServer: Register custom @mcp.tool()
    CreateServer-->>Main: Configured server
    
    Main->>Main: server.run(transport="stdio")
```

**Sources:** [src/rootly_mcp_server/__main__.py:148-192](), [src/rootly_mcp_server/server.py:278-344](), [src/rootly_mcp_server/utils.py:45-105](), [src/rootly_mcp_server/server.py:175-203]()

### Parameter Transformation Pipeline

```mermaid
graph LR
    subgraph "OpenAPI Spec"
        Original["Original names:<br/>filter[status]<br/>page[size]"]
    end
    
    subgraph "Sanitization Phase"
        Sanitize["sanitize_parameters_in_spec()"]
        Mapping["Build mapping:<br/>{filter_status: filter[status]}"]
    end
    
    subgraph "Tool Interface"
        MCPTools["MCP Tools with<br/>sanitized names:<br/>filter_status<br/>page_size"]
    end
    
    subgraph "Request Phase"
        Transform["_transform_params()"]
        Reverse["Apply reverse mapping"]
    end
    
    subgraph "API Call"
        HTTPX["httpx.AsyncClient.request()"]
        RootlyAPI["Rootly API with<br/>original names:<br/>filter[status]<br/>page[size]"]
    end
    
    Original --> Sanitize
    Sanitize --> Mapping
    Mapping --> MCPTools
    
    MCPTools --> Transform
    Transform --> Reverse
    Reverse --> HTTPX
    HTTPX --> RootlyAPI
```

**Sources:** [src/rootly_mcp_server/utils.py:45-105](), [src/rootly_mcp_server/server.py:213-234]()

---

## Advanced API Patterns

### Dual Authentication Mode

```mermaid
graph TB
    subgraph "Local Mode"
        LocalInit["hosted=False"]
        ReadEnv["Read ROOTLY_API_TOKEN env"]
        StoreToken["Store in _api_token"]
        AddHeader1["Add to Authorization header"]
    end
    
    subgraph "Hosted Mode"
        HostedInit["hosted=True"]
        SkipToken["Skip token retrieval"]
        ExtractHeader["Extract from MCP request headers"]
        AddHeader2["Add to Authorization header"]
    end
    
    subgraph "Request Execution"
        HTTPRequest["HTTP request to Rootly API"]
    end
    
    LocalInit --> ReadEnv
    ReadEnv --> StoreToken
    StoreToken --> AddHeader1
    AddHeader1 --> HTTPRequest
    
    HostedInit --> SkipToken
    SkipToken --> ExtractHeader
    ExtractHeader --> AddHeader2
    AddHeader2 --> HTTPRequest
```

**Implementation:**

**Local Mode:**
```python
# AuthenticatedHTTPXClient.__init__()
if not self.hosted:
    self._api_token = os.getenv("ROOTLY_API_TOKEN")
    headers["Authorization"] = f"Bearer {self._api_token}"
```

**Hosted Mode:**
```python
# In custom tools (e.g., search_incidents)
if hosted:
    from fastmcp.server.dependencies import get_http_headers
    request_headers = get_http_headers()
    auth_header = request_headers.get("authorization", "")
    if auth_header:
        kwargs["headers"]["Authorization"] = auth_header
```

**Sources:** [src/rootly_mcp_server/server.py:178-211](), [src/rootly_mcp_server/server.py:375-392]()

### Error Handling Pattern

```mermaid
graph TB
    ToolCall["MCP Tool Invocation"]
    
    TryBlock["try:<br/>Execute tool logic"]
    
    Success["Return result dict"]
    
    CatchBlock["except Exception as e"]
    
    Categorize["MCPError.categorize_error(e)"]
    
    ToolError["MCPError.tool_error(message, type)"]
    
    Return["Return error dict<br/>{error: true, ...}"]
    
    ToolCall --> TryBlock
    TryBlock -->|Success| Success
    TryBlock -->|Exception| CatchBlock
    
    CatchBlock --> Categorize
    Categorize --> ToolError
    ToolError --> Return
```

**Example Usage:**

```python
@mcp.tool()
async def search_incidents(...) -> dict:
    try:
        response = await make_authenticated_request("GET", "/v1/incidents", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        error_type, error_message = MCPError.categorize_error(e)
        return MCPError.tool_error(error_message, error_type)
```

**Sources:** [src/rootly_mcp_server/server.py:28-82](), [src/rootly_mcp_server/server.py:394-424]()

---

