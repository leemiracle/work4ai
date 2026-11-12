<!-- source: DeepWiki mcp.deepwiki.com · repo hypermodeinc/modus · page 6 Configuration · fetched 2026-10-26 -->

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/manifest/dgraph.go](lib/manifest/dgraph.go)
- [lib/manifest/go.sum](lib/manifest/go.sum)
- [lib/manifest/manifest.go](lib/manifest/manifest.go)
- [lib/manifest/modus_schema.json](lib/manifest/modus_schema.json)
- [lib/manifest/test/manifest_test.go](lib/manifest/test/manifest_test.go)
- [lib/manifest/test/valid_modus.json](lib/manifest/test/valid_modus.json)
- [runtime/dgraphclient/dgraph.go](runtime/dgraphclient/dgraph.go)

</details>



This document covers the Modus configuration system, which manages application settings through manifest files and connection definitions. The configuration system handles endpoint definitions, AI model configurations, database connections, and secret management through template variables.

For information about deploying configured applications, see [Deployment and Operations](#8). For details about the manifest file structure validation, see [Application Manifests](#6.1). For connection and secret management specifics, see [Connections and Secrets](#6.2).

## Configuration System Architecture

The Modus configuration system is built around the `modus.json` manifest file, which serves as the central configuration source for applications. The system provides type-safe parsing, JSON schema validation, and template variable resolution for secrets.

**Configuration System Components**

```mermaid
graph TD
    subgraph "Configuration Files"
        ModusJSON["modus.json<br/>Main Manifest"]
        Schema["modus_schema.json<br/>JSON Schema"]
        EnvVars["Environment Variables<br/>Secret Values"]
    end
    
    subgraph "Manifest Library"
        ManifestGo["manifest.go<br/>Manifest struct"]
        Validator["ValidateManifest()<br/>Schema Validation"]
        Parser["ReadManifest()<br/>JSON Parser"]
        Variables["GetVariables()<br/>Variable Extractor"]
    end
    
    subgraph "Connection Types"
        HTTPConn["HTTPConnectionInfo"]
        PostgresConn["PostgresqlConnectionInfo"]
        MySQLConn["MysqlConnectionInfo"]
        DgraphConn["DgraphConnectionInfo"]
        Neo4jConn["Neo4jConnectionInfo"]
    end
    
    subgraph "Runtime Usage"
        GraphQLEngine["GraphQL Engine<br/>Endpoint Config"]
        DatabaseClients["Database Clients<br/>Connection Pool"]
        ModelInvocation["Model Invocation<br/>AI Service Calls"]
    end
    
    ModusJSON --> Validator
    Schema --> Validator
    Validator --> Parser
    Parser --> ManifestGo
    
    ManifestGo --> HTTPConn
    ManifestGo --> PostgresConn
    ManifestGo --> MySQLConn
    ManifestGo --> DgraphConn
    ManifestGo --> Neo4jConn
    
    Variables --> EnvVars
    
    ManifestGo --> GraphQLEngine
    HTTPConn --> ModelInvocation
    PostgresConn --> DatabaseClients
    MySQLConn --> DatabaseClients
    DgraphConn --> DatabaseClients
    Neo4jConn --> DatabaseClients
```

Sources: [lib/manifest/manifest.go:35-40](), [lib/manifest/modus_schema.json:1-318]()

## Manifest File Structure

The `modus.json` file defines three main configuration sections: endpoints, models, and connections. The manifest uses version 3 of the schema and supports JSON with comments (JSONC format).

**Manifest Core Structure**

```mermaid
graph LR
    subgraph "Manifest struct"
        Version["Version int<br/>Schema Version"]
        Endpoints["Endpoints map[string]EndpointInfo"]
        Models["Models map[string]ModelInfo"]
        Connections["Connections map[string]ConnectionInfo"]
    end
    
    subgraph "Endpoint Types"
        GraphQL["GraphqlEndpointInfo<br/>Type: 'graphql'"]
    end
    
    subgraph "Model Configuration"
        SourceModel["SourceModel string<br/>Model Identifier"]
        Provider["Provider string<br/>e.g. 'hugging-face'"]
        Connection["Connection string<br/>Connection Name"]
        Path["Path string<br/>Model Path"]
    end
    
    Endpoints --> GraphQL
    Models --> SourceModel
    Models --> Provider
    Models --> Connection
    Models --> Path
```

Sources: [lib/manifest/manifest.go:35-40](), [lib/manifest/test/valid_modus.json:1-95]()

### Endpoint Configuration

Endpoints define GraphQL API access points with authentication settings. The default endpoint configuration provides a GraphQL interface at `/graphql` with bearer token authentication.

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `type` | string | Endpoint type (currently only "graphql") | - |
| `path` | string | URL path for the endpoint | "/graphql" |
| `auth` | string | Authentication type ("none" or "bearer-token") | "bearer-token" |

Example endpoint configuration:
```json
{
  "endpoints": {
    "default": {
      "type": "graphql",
      "path": "/graphql", 
      "auth": "bearer-token"
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:4-9](), [lib/manifest/modus_schema.json:15-55]()

### Model Configuration

Models define AI model access through either the Hypermode platform or external connections. Models can reference Hugging Face models through the built-in "hypermode" connection or custom HTTP connections.

**Model Configuration Types**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sourceModel` | string | Yes | Model identifier from provider |
| `provider` | string | For hypermode | Provider name (e.g., "hugging-face") |
| `connection` | string | Yes | Connection name ("hypermode" or custom) |
| `path` | string | Optional | Model endpoint path for custom connections |

Example model configurations:
```json
{
  "models": {
    "model-1": {
      "sourceModel": "example/source-model-1",
      "provider": "hugging-face",
      "connection": "hypermode"
    },
    "model-2": {
      "sourceModel": "source-model-2", 
      "connection": "my-model-connection",
      "path": "path/to/model-2"
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:11-25](), [lib/manifest/modus_schema.json:57-121]()

## Connection Types

The configuration system supports multiple connection types for databases and HTTP services. Each connection type has specific fields and validation rules defined in the JSON schema.

**Connection Type Implementation**

```mermaid
graph TD
    subgraph "ConnectionInfo Interface"
        ConnName["ConnectionName() string"]
        ConnType["ConnectionType() ConnectionType"]
        Hash["Hash() string"]
        Variables["Variables() []string"]
    end
    
    subgraph "HTTP Connections"
        HTTPType["Type: 'http'"]
        BaseURL["BaseURL string<br/>Base URL with trailing slash"]
        Endpoint["Endpoint string<br/>Full URL endpoint"]
        Headers["Headers map[string]string"]
        QueryParams["QueryParameters map[string]string"]
    end
    
    subgraph "Database Connections"
        PostgresType["Type: 'postgresql'"]
        MySQLType["Type: 'mysql'"]
        DgraphType["Type: 'dgraph'"]
        Neo4jType["Type: 'neo4j'"]
        ConnStr["ConnStr string<br/>Connection String"]
    end
    
    subgraph "Dgraph Specific"
        GrpcTarget["GrpcTarget string<br/>gRPC Address"]
        Key["Key string<br/>API Key"]
    end
    
    ConnName --> HTTPType
    ConnName --> PostgresType
    HTTPType --> BaseURL
    HTTPType --> Endpoint
    HTTPType --> Headers
    HTTPType --> QueryParams
    
    PostgresType --> ConnStr
    MySQLType --> ConnStr
    DgraphType --> ConnStr
    DgraphType --> GrpcTarget
    DgraphType --> Key
```

Sources: [lib/manifest/manifest.go:153-191](), [lib/manifest/dgraph.go:14-20]()

### HTTP Connections

HTTP connections support both base URL and full endpoint configurations. They can include custom headers and query parameters for authentication and API access.

**HTTP Connection Configuration**

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `type` | string | Must be "http" | Required |
| `baseUrl` | string | Base URL ending with "/" | Use for path-based APIs |
| `endpoint` | string | Complete URL | Use for single endpoint APIs |
| `headers` | object | HTTP headers | Supports template variables |
| `queryParameters` | object | Query parameters | Supports template variables |

Example HTTP connections:
```json
{
  "connections": {
    "my-rest-api": {
      "type": "http",
      "baseUrl": "https://api.example.com/v1/",
      "queryParameters": {
        "api_token": "{{API_TOKEN}}"
      }
    },
    "my-graphql-api": {
      "type": "http", 
      "endpoint": "https://api.example.com/graphql",
      "headers": {
        "Authorization": "Bearer {{AUTH_TOKEN}}"
      }
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:49-62](), [lib/manifest/modus_schema.json:132-202]()

### Database Connections

Database connections use connection strings following standard URI formats. Each database type has specific connection string patterns validated by the JSON schema.

**Database Connection Types**

| Database | Type | Connection String Pattern | Example |
|----------|------|--------------------------|---------|
| PostgreSQL | `postgresql` | `postgresql://user:pass@host:port/db` | `postgresql://{{USER}}:{{PASS}}@localhost:5432/mydb` |
| MySQL | `mysql` | `mysql://user:pass@host:port/db` | `mysql://{{USER}}:{{PASS}}@localhost:3306/mydb` |
| Dgraph | `dgraph` | `dgraph://host:port` or gRPC target | `dgraph://localhost:9080` |
| Neo4j | `neo4j` | `bolt://host:port` or `neo4j://host:port` | `bolt://localhost:7687` |

Example database connections:
```json
{
  "connections": {
    "neon": {
      "type": "postgresql",
      "connString": "postgresql://{{POSTGRESQL_USERNAME}}:{{POSTGRESQL_PASSWORD}}@1.2.3.4:5432/data?sslmode=disable"
    },
    "my-dgraph-cloud": {
      "type": "dgraph", 
      "grpcTarget": "frozen-mango.grpc.eu-central-1.aws.cloud.dgraph.io:443",
      "key": "{{DGRAPH_KEY}}"
    }
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:63-93](), [lib/manifest/modus_schema.json:204-311]()

## Variable Templating

The configuration system supports template variables for secrets and environment-specific values. Variables are enclosed in double braces (`{{VARIABLE_NAME}}`) and resolved at runtime from environment variables.

**Variable Resolution Process**

```mermaid
sequenceDiagram
    participant Config as "Configuration File"
    participant Parser as "parseManifestJson()"
    participant Extractor as "GetVariables()"
    participant Runtime as "Runtime"
    participant Env as "Environment Variables"
    
    Config->>Parser: Load modus.json
    Parser->>Parser: Parse connection configs
    Parser->>Extractor: Extract {{VARIABLES}}
    Extractor->>Extractor: extractVariables() per connection
    Extractor->>Runtime: Return variable map
    Runtime->>Env: Resolve variable values
    Runtime->>Runtime: Substitute values in connections
```

Sources: [lib/manifest/manifest.go:46-57](), [lib/manifest/test/manifest_test.go:262-286]()

### Variable Extraction

The `GetVariables()` method extracts all template variables from connection configurations, returning a map of connection names to their required variables.

Example variable extraction result:
```go
map[string][]string{
    "my-model-connection":      {"API_KEY"},
    "my-graphql-api":           {"AUTH_TOKEN"},
    "neon":                     {"POSTGRESQL_USERNAME", "POSTGRESQL_PASSWORD"},
    "my-dgraph-cloud":          {"DGRAPH_KEY"},
}
```

### Advanced Variable Functions

The system supports function-style variable templating for complex transformations:

| Function | Usage | Description |
|----------|-------|-------------|
| `base64()` | `{{base64(USERNAME:PASSWORD)}}` | Base64 encode credentials |

Example with function:
```json
{
  "headers": {
    "Authorization": "Basic {{base64(USERNAME:PASSWORD)}}"
  }
}
```

Sources: [lib/manifest/test/valid_modus.json:60](), [lib/manifest/test/manifest_test.go:269]()

## Schema Validation

The configuration system includes comprehensive JSON schema validation through the `ValidateManifest()` function. The schema enforces naming conventions, required fields, and format validation for all configuration elements.

**Validation Rules**

| Element | Rule | Pattern |
|---------|------|---------|
| Connection names | Alphanumeric with hyphens | `^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$` |
| Model names | Alphanumeric with hyphens | `^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$` |
| Endpoint paths | Must start with "/" | `^\/\S*$` |
| HTTP URLs | Valid URI format | Standard URI validation |
| Database URIs | Database-specific patterns | Protocol-specific validation |

The validation process uses the `jsonschema` library with a compiled schema loaded at package initialization:

```go
func ValidateManifest(content []byte) error {
    r := bytes.NewReader(jsonc.ToJSON(content))
    doc, err := jsonschema.UnmarshalJSON(r)
    if err != nil {
        return fmt.Errorf("failed to parse manifest: %w", err)
    }
    
    if err := schema.Validate(doc); err != nil {
        return fmt.Errorf("failed to validate manifest: %w", err)
    }
    
    return nil
}
```

Sources: [lib/manifest/manifest.go:81-93](), [lib/manifest/modus_schema.json:17-23]()

---

