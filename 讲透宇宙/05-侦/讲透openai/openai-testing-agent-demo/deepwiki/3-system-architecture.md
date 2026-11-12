<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-testing-agent-demo · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cua-server/README.md](cua-server/README.md)
- [frontend/README.md](frontend/README.md)

</details>



## Purpose and Scope

This document provides a high-level overview of the Testing Agent Demo's system architecture, focusing on how the three main applications work together to enable AI-driven web testing. It covers the overall system design, communication patterns, and execution flow between components.

For detailed implementation of individual components, see [CUA Server](#4) for the core backend service, [Frontend Application](#5) for the web interface, and [Development Guide](#6) for the sample test application structure.

## System Overview

The Testing Agent Demo is architected as a monorepo containing three distinct applications that work together to provide AI-powered web testing capabilities.

### Application Architecture

```mermaid
graph TB
    subgraph MonorepoRoot["Testing Agent Demo Monorepo"]
        FrontendApp[Frontend<br/>"Next.js Application"<br/>":3000"]
        CuaServerApp[CuaServer<br/>"Node.js Service"<br/>":8080"]
        SampleApp[SampleTestApp<br/>"Demo E-commerce Site"<br/>":3005"]
    end
    
    subgraph ExternalServices["External Dependencies"]
        OpenAIAPI["OpenAI CUA Model<br/>"gpt-4o-cua""]
        PlaywrightEngine["Playwright Browser<br/>"Chromium/Firefox/Safari""]
    end
    
    User --> FrontendApp
    FrontendApp <-->|"Socket.IO WebSocket"| CuaServerApp
    CuaServerApp --> OpenAIAPI
    CuaServerApp --> PlaywrightEngine
    PlaywrightEngine --> SampleApp
    PlaywrightEngine -.->|"Can target any web app"| ExternalWebApps["External Web Applications"]
```

**Sources:** [README.md:7-11](), [frontend/README.md:5-6](), [cua-server/README.md:5]()

### Component Responsibilities

| Component | Primary Responsibility | Technology | Default Port |
|-----------|----------------------|------------|--------------|
| `frontend` | User interface for test configuration and monitoring | Next.js | 3000 |
| `cua-server` | AI orchestration and browser automation | Node.js + Socket.IO | 8080 |
| `sample-test-app` | Demo target application for testing | Next.js | 3005 |

**Sources:** [README.md:9-11](), [README.md:59-63]()

## Application Communication Architecture

The system uses WebSocket-based real-time communication between the frontend and CUA server, with the CUA server orchestrating external API calls and browser automation.

### Communication Flow Architecture

```mermaid
graph LR
    subgraph FrontendLayer["Frontend Layer"]
        ReactUI["React Components"]
        SocketIOClient["Socket.IO Client"]
    end
    
    subgraph NetworkLayer["Network Communication"]
        WebSocketConnection["WebSocket Connection<br/>localhost:8080"]
    end
    
    subgraph CuaServerLayer["CUA Server Layer"]
        SocketIOServer["Socket.IO Server"]
        EventHandlers["Event Handlers<br/>testCaseInitiated<br/>testCaseUpdate<br/>message"]
        OpenAIClient["OpenAI Client"]
        PlaywrightController["Playwright Controller"]
    end
    
    subgraph ExternalLayer["External Integrations"]
        OpenAIService["OpenAI API<br/>chat/completions"]
        BrowserInstance["Browser Instance<br/>screenshot()<br/>click()<br/>type()"]
        TargetApplication["Target Web Application"]
    end
    
    ReactUI --> SocketIOClient
    SocketIOClient <--> WebSocketConnection
    WebSocketConnection <--> SocketIOServer
    SocketIOServer --> EventHandlers
    EventHandlers --> OpenAIClient
    EventHandlers --> PlaywrightController
    OpenAIClient <--> OpenAIService
    PlaywrightController <--> BrowserInstance
    BrowserInstance <--> TargetApplication
```

**Sources:** [cua-server/README.md:5](), [frontend/README.md:5]()

## Test Execution Flow Architecture

The system follows a structured flow from user input through AI processing to browser automation and result reporting.

### Execution Pipeline Architecture

```mermaid
sequenceDiagram
    participant User
    participant ReactUI as "React UI"
    participant SocketClient as "Socket.IO Client"
    participant SocketServer as "Socket.IO Server"
    participant TestCaseAgent as "TestCaseAgent"
    participant CuaLoop as "Computer Use Loop"
    participant OpenAI as "OpenAI CUA Model"
    participant Playwright as "Playwright Browser"
    participant TargetApp as "Target Application"
    
    User->>ReactUI: "Configure test case and URL"
    ReactUI->>SocketClient: "testCaseInitiated event"
    SocketClient->>SocketServer: "WebSocket message"
    SocketServer->>TestCaseAgent: "generateTestCase()"
    TestCaseAgent->>OpenAI: "Create structured test steps"
    OpenAI-->>TestCaseAgent: "JSON test case structure"
    
    SocketServer->>Playwright: "Launch browser and navigate"
    Playwright->>TargetApp: "Navigate to target URL"
    
    loop "Computer Use Loop"
        SocketServer->>CuaLoop: "Execute next step"
        CuaLoop->>Playwright: "Take screenshot"
        CuaLoop->>OpenAI: "Send screenshot + instructions"
        OpenAI-->>CuaLoop: "Browser action commands"
        CuaLoop->>Playwright: "Execute actions"
        Playwright->>TargetApp: "Perform interactions"
        CuaLoop-->>SocketServer: "Status update"
        SocketServer-->>SocketClient: "Real-time progress"
        SocketClient-->>ReactUI: "Update UI"
    end
    
    SocketServer-->>SocketClient: "Test completion results"
    SocketClient-->>ReactUI: "Display final results"
    ReactUI-->>User: "Show test results and screenshots"
```

**Sources:** [README.md:5](), [cua-server/README.md:5]()

## Deployment Architecture

The system is designed to run locally with specific port assignments and environment configurations.

### Service Deployment Architecture

```mermaid
graph TB
    subgraph LocalDevelopment["Local Development Environment"]
        subgraph Port3000["localhost:3000"]
            NextJSFrontend["Next.js Frontend<br/>npm run dev"]
        end
        
        subgraph Port8080["localhost:8080"]
            NodeCuaServer["Node.js CUA Server<br/>Socket.IO WebSocket<br/>npm run dev"]
        end
        
        subgraph Port3005["localhost:3005"]
            SampleTestApp["Sample Test App<br/>Next.js E-commerce<br/>npm run dev"]
        end
        
        subgraph ProcessLevel["Process Management"]
            ConcurrentlyRunner["npm run dev<br/>concurrently script<br/>starts all services"]
        end
    end
    
    subgraph EnvironmentConfig["Environment Configuration"]
        OpenAIKey["OPENAI_API_KEY<br/>Required for all components"]
        SocketPort["SOCKET_PORT<br/>Default: 8080"]
        CorsOrigin["CORS_ORIGIN<br/>Cross-origin settings"]
        AdminCreds["ADMIN_USERNAME<br/>ADMIN_PASSWORD<br/>Sample app login"]
    end
    
    subgraph Dependencies["Runtime Dependencies"]
        NodeModules["node_modules<br/>Shared workspace dependencies"]
        PlaywrightBrowsers["Playwright Browsers<br/>npx playwright install"]
    end
    
    ConcurrentlyRunner --> NextJSFrontend
    ConcurrentlyRunner --> NodeCuaServer
    ConcurrentlyRunner --> SampleTestApp
    
    OpenAIKey --> NextJSFrontend
    OpenAIKey --> NodeCuaServer
    SocketPort --> NodeCuaServer
    CorsOrigin --> NodeCuaServer
    AdminCreds --> SampleTestApp
    
    NodeModules --> NextJSFrontend
    NodeModules --> NodeCuaServer  
    NodeModules --> SampleTestApp
    PlaywrightBrowsers --> NodeCuaServer
```

**Sources:** [README.md:53-63](), [README.md:27-44](), [cua-server/README.md:20-26]()

## Technology Stack and Dependencies

The system integrates multiple technologies to provide AI-driven browser automation capabilities.

### Technology Integration Architecture

```mermaid
graph TB
    subgraph FrontendStack["Frontend Technology Stack"]
        NextJS["Next.js<br/>React Framework"]
        SocketIOClientLib["socket.io-client<br/>WebSocket communication"]
        TailwindCSS["Tailwind CSS<br/>Styling framework"]
    end
    
    subgraph BackendStack["Backend Technology Stack"]
        NodeJS["Node.js<br/>JavaScript runtime"]
        SocketIOServer["socket.io<br/>WebSocket server"]
        PlaywrightLib["@playwright/test<br/>Browser automation"]
        OpenAISDK["openai<br/>AI model integration"]
    end
    
    subgraph AIStack["AI and Automation Stack"]
        CUAModel["gpt-4o-cua<br/>Computer Use Agent model"]
        ChromiumBrowser["Chromium Browser<br/>Playwright automation target"]
        ScreenshotAPI["Screenshot API<br/>Visual context for AI"]
    end
    
    subgraph ConfigStack["Configuration and Build"]
        TypeScript["TypeScript<br/>Type safety"]
        ESLint["ESLint<br/>Code linting"]
        TailwindConfig["tailwind.config.js<br/>Style configuration"]
        PlaywrightConfig["playwright.config.ts<br/>Browser configuration"]
    end
    
    NextJS --> SocketIOClientLib
    NodeJS --> SocketIOServer
    NodeJS --> PlaywrightLib
    NodeJS --> OpenAISDK
    OpenAISDK --> CUAModel
    PlaywrightLib --> ChromiumBrowser
    PlaywrightLib --> ScreenshotAPI
    
    TypeScript --> NextJS
    TypeScript --> NodeJS
    ESLint --> NextJS
    ESLint --> NodeJS
```

**Sources:** [README.md:5](), [README.md:48-50](), [cua-server/README.md:14-18](), [frontend/README.md:14-17]()

---

