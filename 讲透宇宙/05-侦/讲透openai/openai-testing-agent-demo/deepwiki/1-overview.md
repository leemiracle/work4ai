<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-testing-agent-demo · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the Testing Agent Demo repository, a monorepo that demonstrates automated web testing using OpenAI's Computer Use Agent (CUA) model. The system showcases how AI-driven browser automation can be used to execute test cases on web applications through natural language instructions and visual feedback.

The Testing Agent Demo consists of three interconnected applications that work together to provide end-to-end automated testing capabilities. For detailed information about individual components, see [CUA Server](#4), [Frontend Application](#5), and [Getting Started](#2) for setup instructions.

Sources: [README.md:1-91]()

## System Composition

The Testing Agent Demo is structured as a monorepo containing three distinct applications:

| Application | Technology | Port | Purpose |
|-------------|------------|------|---------|
| `frontend` | Next.js | 3000 | Web interface for configuring tests and monitoring execution |
| `cua-server` | Node.js | 8080 | Core service that orchestrates AI-driven browser automation |
| `sample-test-app` | Node.js | 3005 | Example e-commerce application used as a testing target |

The system leverages OpenAI's CUA model with computer use capabilities to interpret test instructions and execute browser actions through Playwright automation.

Sources: [README.md:7-11]()

## High-Level Architecture

The following diagram illustrates how the three applications interact within the broader system:

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Testing Agent Demo Monorepo"
        Frontend["frontend<br/>Next.js Application<br/>:3000"]
        CuaServer["cua-server<br/>Node.js Service<br/>:8080"]
        SampleApp["sample-test-app<br/>E-commerce Target<br/>:3005"]
    end
    
    subgraph "External Services"
        OpenAI["OpenAI CUA Model<br/>Computer Use Agent"]
        PlaywrightBrowsers["Playwright Browsers<br/>Browser Automation"]
    end
    
    subgraph "Environment Configuration"
        EnvVars["OPENAI_API_KEY<br/>ADMIN_USERNAME<br/>ADMIN_PASSWORD"]
    end
    
    User --> Frontend
    Frontend <-->|"Socket.IO WebSocket"| CuaServer
    CuaServer --> OpenAI
    CuaServer --> PlaywrightBrowsers
    PlaywrightBrowsers --> SampleApp
    PlaywrightBrowsers -.->|"Can target"| ExternalWebApps["External Web Applications"]
    
    EnvVars --> Frontend
    EnvVars --> CuaServer
    EnvVars --> SampleApp
```

Sources: [README.md:5-11](), [README.md:59-64]()

## Core Testing Workflow

The system follows a structured workflow that combines AI decision-making with browser automation:

### Testing Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant frontend as "frontend<br/>(Next.js UI)"
    participant cuaserver as "cua-server<br/>(Node.js Service)"
    participant OpenAI as "OpenAI CUA Model"
    participant Playwright
    participant target as "Target Web App<br/>(sample-test-app)"
    
    User->>frontend: "Configure test case and target URL"
    frontend->>cuaserver: "testCaseInitiated event via Socket.IO"
    cuaserver->>OpenAI: "Generate structured test steps"
    OpenAI-->>cuaserver: "Test case JSON response"
    
    cuaserver->>Playwright: "Launch browser and navigate"
    Playwright->>target: "Navigate to target URL"
    
    loop "Computer Use Loop"
        cuaserver->>Playwright: "Take screenshot"
        cuaserver->>OpenAI: "Send screenshot + test instructions"
        OpenAI-->>cuaserver: "Browser action commands"
        cuaserver->>Playwright: "Execute actions (click, type, etc.)"
        Playwright->>target: "Perform UI interactions"
        cuaserver->>frontend: "Status updates via Socket.IO"
    end
    
    cuaserver-->>frontend: "Test completion results"
    frontend-->>User: "Display results and screenshots"
```

Sources: [README.md:5-6]()

## Key Technologies and Integrations

The system integrates several key technologies to enable AI-driven testing:

### Core Dependencies

- **OpenAI CUA Model**: Provides computer use capabilities for interpreting screenshots and generating browser actions
- **Playwright**: Handles browser automation, screenshot capture, and UI element interactions
- **Socket.IO**: Enables real-time communication between `frontend` and `cua-server`
- **Next.js**: Powers the web interface for test configuration and monitoring

### Environment Requirements

The system requires several environment variables to function properly:

| Variable | Purpose | Required By |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Authentication for OpenAI CUA model | `frontend`, `cua-server` |
| `ADMIN_USERNAME` | Demo login credentials for sample app | `sample-test-app` |
| `ADMIN_PASSWORD` | Demo login credentials for sample app | `sample-test-app` |

Sources: [README.md:29-44](), [README.md:49-50]()

## Use Cases and Applications

The Testing Agent Demo serves multiple purposes:

### Primary Use Cases

1. **Demonstration Platform**: Shows how AI can automate web testing through natural language instructions
2. **Development Framework**: Provides a foundation for building custom AI-driven testing solutions
3. **Integration Example**: Illustrates how to combine OpenAI's computer use capabilities with browser automation

### Customization Capabilities

The system is designed to be adaptable for different testing scenarios. Users can:

- Test any web application by updating the target URL in `frontend/lib/constants.ts`
- Modify test cases through the configuration UI
- Extend the `cua-server` logic for custom testing workflows

The `sample-test-app` serves purely as an example target, while the core testing logic resides in the `cua-server` component.

Sources: [README.md:73-77]()

---

