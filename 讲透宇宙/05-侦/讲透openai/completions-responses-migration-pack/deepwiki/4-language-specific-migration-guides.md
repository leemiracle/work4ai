<!-- source: DeepWiki mcp.deepwiki.com · repo openai/completions-responses-migration-pack · page 4 Language-Specific Migration Guides · fetched 2026-10-26 -->

# Language-Specific Migration Guides

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/language-recipes/java.md](docs/language-recipes/java.md)
- [docs/language-recipes/node.md](docs/language-recipes/node.md)
- [docs/language-recipes/python.md](docs/language-recipes/python.md)

</details>



This document provides comprehensive migration instructions for transitioning from OpenAI's legacy Completions and Chat APIs to the unified Responses API across multiple programming languages and environments. Each language guide includes practical examples, parameter mappings, and platform-specific implementation details.

For information about the overall migration process and script execution, see [Getting Started](#2). For detailed API reference documentation, see [Responses API Reference](#6).

## Overview of Language Support

The migration toolkit supports transformation of legacy OpenAI API calls across six major programming languages and environments. Each language follows the same core transformation pattern while accommodating language-specific idioms and SDK differences.

### Supported Environments

| Language | Primary Interface | Migration Focus |
|----------|------------------|-----------------|
| Node.js | OpenAI SDK v4+ | Client method transformation |
| Python | OpenAI Python SDK | Library method migration |
| Java | HTTP Client | Direct HTTP API calls |
| Go | HTTP Client | Request/response handling |
| C# | HttpClient | JSON payload construction |
| Ruby | Net::HTTP | HTTP endpoint migration |

**Sources:** [docs/language-recipes/node.md:1-148](), [docs/language-recipes/python.md:1-44](), [docs/language-recipes/java.md:1-31]()

## Migration Transformation Flow

The following diagram illustrates how legacy API calls transform to the unified Responses API across different programming languages:

```mermaid
graph TB
    subgraph "Legacy APIs"
        A1["openai.createCompletion()"]
        A2["openai.Completion.create()"]
        A3["HttpRequest to /v1/completions"]
        A4["HTTP POST /v1/chat/completions"]
    end
    
    subgraph "Common Transformations"
        B1["Parameter Mapping"]
        B2["Endpoint Migration"]
        B3["Response Schema Update"]
        B4["SDK Method Changes"]
    end
    
    subgraph "Unified Responses API"
        C1["client.responses.create()"]
        C2["HTTP POST /v1/responses"]
        C3["Unified Response Schema"]
        C4["Enhanced Features"]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B2
    A4 --> B2
    
    B1 --> B4
    B2 --> B3
    B3 --> C3
    B4 --> C1
    
    C1 --> C2
    C2 --> C3
    C3 --> C4
    
    subgraph "Language Implementations"
        D1["Node.js: import OpenAI"]
        D2["Python: from openai import OpenAI"]
        D3["Java: HttpRequest.newBuilder()"]
        D4["Go: http.NewRequest()"]
        D5["C#: HttpClient"]
        D6["Ruby: Net::HTTP"]
    end
    
    C1 --> D1
    C1 --> D2
    C2 --> D3
    C2 --> D4
    C2 --> D5
    C2 --> D6
```

**Sources:** [docs/language-recipes/node.md:6-21](), [docs/language-recipes/python.md:5-19](), [docs/language-recipes/java.md:3-16]()

## Parameter Mapping Patterns

All languages follow consistent parameter transformations when migrating from legacy APIs to the Responses API:

```mermaid
graph LR
    subgraph "Legacy Parameters"
        L1["prompt"]
        L2["max_tokens"]
        L3["response_format"]
        L4["messages"]
        L5["temperature"]
    end
    
    subgraph "Transformation Rules"
        T1["Direct Mapping"]
        T2["Structure Change"]
        T3["Feature Enhancement"]
        T4["Schema Migration"]
    end
    
    subgraph "Responses Parameters"
        R1["input"]
        R2["max_output_tokens"]
        R3["text.format"]
        R4["input items array"]
        R5["temperature (unchanged)"]
        R6["reasoning.effort"]
        R7["store: false"]
    end
    
    L1 --> T1 --> R1
    L2 --> T1 --> R2
    L3 --> T4 --> R3
    L4 --> T2 --> R4
    L5 --> T1 --> R5
    
    T3 --> R6
    T3 --> R7
```

### Core Parameter Transformations

| Legacy Parameter | Responses Parameter | Notes |
|------------------|-------------------|-------|
| `prompt` | `input` | String or structured input items |
| `max_tokens` | `max_output_tokens` | Same value, different name |
| `temperature` | `temperature` | Unchanged |
| `response_format` | `text.format` | JSON schema structure |
| `messages` | `input` | Array of input items with role/content |

**Sources:** [docs/language-recipes/node.md:69-88](), [docs/language-recipes/python.md:36-40](), [docs/language-recipes/java.md:3-5]()

## Language-Specific Implementation Patterns

### SDK-Based Languages (Node.js, Python)

These languages use the official OpenAI SDK and follow object-oriented patterns:

```mermaid
graph TB
    subgraph "Client Initialization"
        I1["new OpenAI({ apiKey })"]
        I2["OpenAI()"]
    end
    
    subgraph "Method Transformation"
        M1["client.responses.create()"]
        M2["Payload Construction"]
        M3["Response Handling"]
    end
    
    subgraph "Advanced Features"
        F1["Streaming: stream: true"]
        F2["Tools: tools: [{ type }]"]
        F3["Reasoning: reasoning: { effort }"]
        F4["Image Input: input_image"]
    end
    
    I1 --> M1
    I2 --> M1
    M1 --> M2
    M2 --> M3
    
    M1 --> F1
    M1 --> F2
    M1 --> F3
    M1 --> F4
```

**Sources:** [docs/language-recipes/node.md:16-35](), [docs/language-recipes/python.md:14-34]()

### HTTP-Based Languages (Java, Go, C#, Ruby)

These languages work directly with HTTP clients and require manual request construction:

```mermaid
graph TB
    subgraph "HTTP Request Setup"
        H1["HttpRequest.newBuilder()"]
        H2["URI: /v1/responses"]
        H3["Authorization Header"]
        H4["Content-Type: application/json"]
    end
    
    subgraph "Payload Construction"
        P1["JSON String Building"]
        P2["Parameter Mapping"]
        P3["Request Body"]
    end
    
    subgraph "Response Processing"
        R1["HTTP Response"]
        R2["JSON Parsing"]
        R3["output_text Extraction"]
    end
    
    H1 --> H2
    H2 --> H3
    H3 --> H4
    H4 --> P1
    
    P1 --> P2
    P2 --> P3
    P3 --> R1
    
    R1 --> R2
    R2 --> R3
```

**Sources:** [docs/language-recipes/java.md:10-28]()

## Detailed Language Guides

For comprehensive migration instructions specific to each programming language:

- **Node.js Applications**: See [Node.js Migration](#4.1) for SDK client usage, streaming, and TypeScript examples
- **Python Projects**: See [Python Migration](#4.2) for library method transformations and async patterns  
- **Java HTTP Clients**: See [Java Migration](#4.3) for HTTP request construction and response parsing
- **Go Applications**: See [Go Migration](#4.4) for HTTP client implementation and error handling
- **C# Projects**: See [C# Migration](#4.5) for HttpClient usage and JSON serialization
- **Ruby Scripts**: See [Ruby Migration](#4.6) for Net::HTTP implementation and stateless requests

Each guide includes before/after code examples, parameter mapping tables, and language-specific best practices for implementing the Responses API.

**Sources:** [docs/language-recipes/node.md:1-148](), [docs/language-recipes/python.md:1-44](), [docs/language-recipes/java.md:1-31]()

---

