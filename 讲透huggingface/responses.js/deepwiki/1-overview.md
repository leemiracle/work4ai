<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/responses.js · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [demo/package.json](demo/package.json)
- [package.json](package.json)

</details>



## Purpose and Scope

The responses.js system is a lightweight Express.js server that implements a translation layer between OpenAI's Responses API and Chat Completion APIs. This documentation covers the core architecture, API endpoints, tool integration capabilities, and deployment options for the responses.js system.

For detailed setup instructions, see [Getting Started](#2). For API specifications, see [API Reference](#4). For tool integration patterns, see [Tool Integration](#5).

**Sources:** [README.md:1-21](), [package.json:1-10]()

## System Architecture

The responses.js system consists of several interconnected components that work together to provide a complete AI response generation service:

```mermaid
graph TB
    subgraph "Core Server Components"
        ExpressApp[Express.Server<br/>src/server.ts]
        ResponsesHandler["ResponsesHandler<br/>src/routes/responses.ts"]
        LandingRoute["LandingPageRoute<br/>src/routes/landingPageHtml.ts"]
        SchemaValidator["SchemaValidator<br/>src/schemas.ts"]
        MCPClient["MCPClient<br/>src/mcp.ts"]
    end
    
    subgraph "External Integrations"
        ChatCompletionAPI["Chat Completion APIs<br/>OpenAI Compatible"]
        MCPToolServers["MCP Tool Servers<br/>External Process"]
        HuggingFaceAPI["Hugging Face API<br/>Model Inference"]
    end
    
    subgraph "Client Interfaces"
        DemoUI["Next.js Demo UI<br/>demo/"]
        ExampleScripts["Example Scripts<br/>examples/"]
        OpenAIClient["OpenAI Node SDK<br/>Client Applications"]
    end
    
    ExpressApp --> ResponsesHandler
    ExpressApp --> LandingRoute
    ResponsesHandler --> SchemaValidator
    ResponsesHandler --> MCPClient
    
    ResponsesHandler --> ChatCompletionAPI
    MCPClient --> MCPToolServers
    ResponsesHandler --> HuggingFaceAPI
    
    DemoUI --> ResponsesHandler
    ExampleScripts --> ResponsesHandler
    OpenAIClient --> ResponsesHandler
```

**Sources:** [README.md:145-160](), [package.json:60-64]()

## Core Capabilities

The responses.js system provides several key capabilities that bridge the gap between different AI API standards:

| Capability | Implementation | Code Location |
|------------|----------------|---------------|
| **Responses API Translation** | Converts Responses API calls to Chat Completion format | `src/routes/responses.ts` |
| **Provider Agnostic** | Works with any OpenAI-compatible Chat Completion API | `src/routes/responses.ts` |
| **Streaming Support** | Real-time Server-Sent Events for response streaming | `src/routes/responses.ts` |
| **Structured Output** | JSON schema validation using Zod schemas | `src/schemas.ts` |
| **Function Calling** | Tool and function execution capabilities | `src/routes/responses.ts` |
| **Multi-modal Input** | Text and image input processing | `src/schemas.ts` |
| **MCP Integration** | Model Context Protocol for external tool execution | `src/mcp.ts` |
| **Demo Interface** | Interactive web UI for testing and demonstration | `demo/` |

**Sources:** [README.md:9-20](), [package.json:60-64]()

## Request Processing Flow

The system processes requests through a coordinated flow between multiple components:

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant ExpressServer as "Express Server<br/>src/server.ts"
    participant ResponsesRoute as "ResponsesRoute<br/>src/routes/responses.ts"
    participant SchemaValidation as "Zod Schemas<br/>src/schemas.ts"
    participant MCPIntegration as "MCP Client<br/>src/mcp.ts"
    participant ChatAPI as "Chat Completion API"
    
    Client->>ExpressServer: "POST /v1/responses"
    ExpressServer->>ResponsesRoute: "Route request"
    ResponsesRoute->>SchemaValidation: "Validate request body"
    SchemaValidation-->>ResponsesRoute: "Validated data"
    
    alt "MCP Tools Required"
        ResponsesRoute->>MCPIntegration: "Initialize MCP connection"
        MCPIntegration-->>ResponsesRoute: "Tool definitions"
    end
    
    ResponsesRoute->>ChatAPI: "Chat completion request"
    
    loop "Streaming Response"
        ChatAPI-->>ResponsesRoute: "Response chunks"
        ResponsesRoute->>Client: "Server-Sent Events"
        
        alt "Tool Execution"
            ResponsesRoute->>MCPIntegration: "Execute tool call"
            MCPIntegration-->>ResponsesRoute: "Tool results"
        end
    end
    
    ResponsesRoute->>Client: "Final response"
```

**Sources:** [README.md:9-20](), [package.json:60-64]()

## Technology Stack

The responses.js system is built on a modern Node.js technology stack:

```mermaid
mindmap
  root(("responses.js<br/>Technology Stack"))
    ("Core Runtime")
      ["Node.js >=18<br/>package.json"]
      ["TypeScript<br/>Type Safety"]
      ["Express.js<br/>Web Framework"]
    
    ("AI Integration")
      ["OpenAI SDK<br/>Chat Completions"]
      ["MCP SDK<br/>Tool Protocol"]
      ["Hugging Face<br/>Model Hosting"]
    
    ("Data Validation")
      ["Zod Schemas<br/>Runtime Validation"]
      ["TypeScript Types<br/>Compile-time Safety"]
    
    ("Development Tools")
      ["pnpm<br/>Package Manager"]
      ["TSX<br/>Development Server"]
      ["ESLint & Prettier<br/>Code Quality"]
      ["Mocha<br/>Testing Framework"]
    
    ("Deployment")
      ["Docker<br/>Containerization"]
      ["Hugging Face Spaces<br/>Hosting Platform"]
```

**Sources:** [package.json:21-80](), [README.md:24-28]()

## Project Structure

The codebase is organized into distinct functional areas:

```mermaid
graph LR
    subgraph "Source Code (src/)"
        IndexTS["index.ts<br/>Entry Point"]
        ServerTS["server.ts<br/>Express App"]
        RoutesDir["routes/<br/>API Endpoints"]
        SchemasTS["schemas.ts<br/>Validation"]
        MCPTS["mcp.ts<br/>Tool Integration"]
    end
    
    subgraph "Client Applications"
        DemoDir["demo/<br/>Next.js UI"]
        ExamplesDir["examples/<br/>Usage Scripts"]
    end
    
    subgraph "Development & Testing"
        TestsDir["tests/<br/>Integration Tests"]
        ScriptsDir["scripts/<br/>Build Utilities"]
    end
    
    subgraph "Configuration"
        PackageJSON["package.json<br/>Dependencies"]
        TSConfigJSON["tsconfig.json<br/>TypeScript Config"]
        DockerFile["Dockerfile<br/>Container Config"]
    end
    
    IndexTS --> ServerTS
    ServerTS --> RoutesDir
    ServerTS --> SchemasTS
    RoutesDir --> MCPTS
```

The core server components are located in the `src/` directory, with the main entry point at [src/index.ts]() and the Express application configuration in [src/server.ts](). The primary API logic resides in [src/routes/responses.ts](), which handles the translation between Responses API and Chat Completion formats.

**Sources:** [README.md:145-160](), [package.json:46-49]()

---

