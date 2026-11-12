<!-- source: DeepWiki mcp.deepwiki.com · repo openai/harmony · page 3 Demo Application · fetched 2026-10-26 -->

# Demo Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [demo/harmony-demo/README.md](demo/harmony-demo/README.md)
- [demo/harmony-demo/components.json](demo/harmony-demo/components.json)
- [demo/harmony-demo/package-lock.json](demo/harmony-demo/package-lock.json)
- [demo/harmony-demo/package.json](demo/harmony-demo/package.json)

</details>



This document provides an overview of the Next.js demo application that showcases the functionality of the `openai-harmony` library. The demo serves as an interactive example of how to integrate and use the harmony response format in web applications.

For detailed technical breakdown of the core demo component, see [Demo Core Component](#3.1). For comprehensive architecture details including WebAssembly integration, see [Demo Application Architecture](#3.2). For information about the harmony response format itself, see [Harmony Response Format](#2).

## Purpose and Scope

The `harmony-demo` application is a Next.js web application located in `demo/harmony-demo/` that demonstrates real-world usage of the `openai-harmony` library. It provides an interactive interface for users to experiment with harmony format parsing, rendering, and message handling capabilities.

The demo application serves multiple purposes:
- Interactive showcase of harmony format capabilities
- Reference implementation for web developers
- Testing environment for WebAssembly bindings
- Documentation of integration patterns

## Application Overview

### Demo Application Structure

```mermaid
graph TB
    subgraph "Next.js Application"
        APP["`app/page.tsx`<br/>Main Application Entry"]
        QUERY["`QueryClientProvider`<br/>React Query Wrapper"]
        DEMO["`HarmonyDemo`<br/>Core Demo Component"]
    end
    
    subgraph "Dependencies"
        HARMONY["`@openai/harmony`<br/>Local Package Dependency"]
        RADIX["`@radix-ui/*`<br/>UI Component Library"]
        TANSTACK["`@tanstack/react-query`<br/>Data Fetching"]
        TAILWIND["`tailwindcss`<br/>Styling Framework"]
    end
    
    subgraph "Build Assets"
        WASM["`*.wasm`<br/>WebAssembly Files"]
        TIKTOKEN["`o200k_base.tiktoken`<br/>Tokenizer Data"]
        PUBLIC["`public/`<br/>Static Assets"]
    end
    
    APP --> QUERY
    QUERY --> DEMO
    
    DEMO --> HARMONY
    DEMO --> RADIX
    QUERY --> TANSTACK
    DEMO --> TAILWIND
    
    HARMONY --> WASM
    HARMONY --> TIKTOKEN
    WASM --> PUBLIC
    TIKTOKEN --> PUBLIC
```

Sources: [demo/harmony-demo/package.json:1-37](), [demo/harmony-demo/package-lock.json:1-40]()

### Package Configuration

The demo application is configured as a standard Next.js project with specific integration requirements for the harmony library:

| Component | Version | Purpose |
|-----------|---------|---------|
| `next` | 15.4.10 | Web application framework [demo/harmony-demo/package.json:23-23]() |
| `react` | 19.1.0 | UI library [demo/harmony-demo/package.json:24-24]() |
| `@openai/harmony` | file:../../javascript | Local harmony library package [demo/harmony-demo/package.json:13-13]() |
| `@radix-ui/*` | ^1.1.11+ | Accessible UI components [demo/harmony-demo/package.json:14-18]() |
| `@tanstack/react-query` | ^5.83.0 | Data fetching and state management [demo/harmony-demo/package.json:19-19]() |

The package includes a critical `postinstall` script that handles WebAssembly file deployment and tokenizer acquisition:

```bash
cp ./node_modules/@openai/harmony/dist/web/*.wasm ./public/ && 
curl -L https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken -o ./public/o200k_base.tiktoken
```

Sources: [demo/harmony-demo/package.json:6-6](), [demo/harmony-demo/package.json:12-26]()

## Integration Architecture

### Library Integration Pattern

```mermaid
graph LR
    subgraph "Harmony Library"
        RUST_CORE["`openai-harmony`<br/>Rust Core"]
        WASM_BINDING["`wasm-bindgen`<br/>WebAssembly Interface"]
        JS_PACKAGE["`@openai/harmony`<br/>JavaScript Package"]
    end
    
    subgraph "Demo Application"
        NEXTJS["`Next.js App`<br/>Client-side Framework"]
        DEMO_COMPONENT["`HarmonyDemo`<br/>Main Demo Component"]
        UI_COMPONENTS["`Radix UI`<br/>Component Library"]
    end
    
    subgraph "Runtime Assets"
        WASM_FILES["`*.wasm`<br/>Compiled WebAssembly"]
        TIKTOKEN_DATA["`o200k_base.tiktoken`<br/>Tokenizer Database"]
    end
    
    RUST_CORE --> WASM_BINDING
    WASM_BINDING --> JS_PACKAGE
    JS_PACKAGE --> NEXTJS
    NEXTJS --> DEMO_COMPONENT
    DEMO_COMPONENT --> UI_COMPONENTS
    
    JS_PACKAGE -.-> WASM_FILES
    JS_PACKAGE -.-> TIKTOKEN_DATA
```

Sources: [demo/harmony-demo/package.json:6-6](), [demo/harmony-demo/package.json:13-13]()

## Application Entry Point

The main application entry point is implemented as a client-side React component that establishes the foundational application structure.

### Main Application Component

The demo uses a standard React Query pattern where a `QueryClientProvider` wraps the core logic. This ensures that the WebAssembly-backed harmony library can be initialized and managed effectively within the React lifecycle.

Key architectural decisions:
- **Client-side rendering**: Uses interactive functionality for real-time parsing.
- **State management**: Implements React Query (via `@tanstack/react-query`) for managing the library's asynchronous state [demo/harmony-demo/package.json:19-19]().
- **Component isolation**: Delegates core functionality to the `HarmonyDemo` component.

### Component Hierarchy

```mermaid
graph TD
    HOME["`Home`<br/>App Entry Point"]
    PROVIDER["`QueryClientProvider`<br/>React Query Context"]
    HARMONY_DEMO["`HarmonyDemo`<br/>Core Demo Logic"]
    
    QUERY_CLIENT["`queryClient`<br/>Query Client Instance"]
    
    HOME --> PROVIDER
    PROVIDER --> HARMONY_DEMO
    QUERY_CLIENT -.-> PROVIDER
    
    subgraph "External Dependencies"
        TANSTACK["`@tanstack/react-query`"]
        RADIX["`@radix-ui/react-*`"]
    end
    
    PROVIDER --> TANSTACK
    HARMONY_DEMO --> RADIX
```

Sources: [demo/harmony-demo/package.json:14-19](), [demo/harmony-demo/components.json:13-19]()

## Build Process and Asset Management

The demo application requires specific build-time configuration to properly integrate WebAssembly assets and tokenizer data. The `postinstall` script in [demo/harmony-demo/package.json:6-6]() ensures that essential runtime files are available in the `public/` directory:

1. **WebAssembly files**: Copied from the `@openai/harmony` package distribution (`dist/web/*.wasm`).
2. **Tokenizer data**: Downloaded from OpenAI's public blob storage (`o200k_base.tiktoken`).
3. **Static serving**: Assets are made available through Next.js static file serving so the WASM module can fetch them at runtime.

This build process enables the demo to function with the harmony library's WebAssembly bindings while maintaining Next.js deployment compatibility.

Sources: [demo/harmony-demo/package.json:6-6](), [demo/harmony-demo/package.json:13-13]()

---

