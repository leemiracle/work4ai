<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-chatkit-starter-app · page 4 Managed ChatKit (managed-chatkit) · fetched 2026-10-26 -->

# Managed ChatKit (managed-chatkit)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document describes the **Managed ChatKit** starter application, which demonstrates integration with ChatKit using hosted workflows. This is one of two reference implementations in the repository, offering an alternative to the self-hosted approach.

For detailed information about the self-hosted ChatKit implementation, see [Self-Hosted ChatKit](#3). For general repository structure and setup instructions, see [Overview](#1) and [Getting Started](#2).

**Sources:** [README.md:1-9]()

---

## 4.1 Overview & Hosted Workflows

### What is Managed ChatKit?

The `managed-chatkit/` directory contains a starter application that integrates with ChatKit using **hosted workflows**. Unlike the self-hosted variant, this approach offloads workflow execution and management to hosted infrastructure, reducing operational complexity for developers.

```mermaid
graph TB
    subgraph "Repository Structure"
        REPO["openai-chatkit-starter-app"]
        
        subgraph SelfHosted["chatkit/ - Self-Hosted"]
            SH_BE["Backend: Full Control<br/>Manages All Logic"]
            SH_FE["Frontend: React UI"]
        end
        
        subgraph Managed["managed-chatkit/ - Managed"]
            M_BE["Backend: Delegates to<br/>Hosted Workflows"]
            M_FE["Frontend: React UI"]
        end
    end
    
    subgraph External["External Services"]
        OPENAI["OpenAI API"]
        HOSTED["Hosted Workflow<br/>Infrastructure"]
    end
    
    REPO --> SelfHosted
    REPO --> Managed
    
    SH_BE -->|"Direct API Calls"| OPENAI
    M_BE -->|"Delegates Execution"| HOSTED
    HOSTED -->|"Manages Lifecycle"| OPENAI
    
    style SelfHosted fill:#e8f5e8
    style Managed fill:#f5e8f5
    style External fill:#e1f5ff
```

**Diagram: Integration Pattern Comparison**

**Sources:** [README.md:7-8]()

### Hosted Workflows Explained

Hosted workflows refer to a deployment model where ChatKit conversation management, state handling, and AI orchestration are handled by managed infrastructure rather than developer-maintained servers. This architectural pattern provides:

| Aspect | Self-Hosted (chatkit) | Managed (managed-chatkit) |
|--------|------------------------|---------------------------|
| **Infrastructure Management** | Developer responsibility | Handled by platform |
| **Conversation State** | Custom implementation (e.g., MemoryStore) | Managed persistence |
| **Workflow Execution** | Local agent orchestration | Remote hosted execution |
| **Operational Complexity** | Full control, full responsibility | Reduced operational burden |
| **Customization Flexibility** | Complete code-level control | Configuration-based customization |

**Sources:** [README.md:8]()

### Technology Stack Similarity

Despite architectural differences in workflow execution, the `managed-chatkit/` example maintains the same technology foundation as the self-hosted variant:

```mermaid
graph LR
    subgraph Backend["Backend Layer"]
        PYTHON["Python 3.11+"]
        FASTAPI["FastAPI Framework"]
        SDK["openai-chatkit SDK"]
    end
    
    subgraph Frontend["Frontend Layer"]
        NODE["Node.js 22"]
        VITE["Vite Build Tool"]
        REACT["React Framework"]
        TS["TypeScript"]
    end
    
    subgraph Integration["Integration Model"]
        HOSTED["Hosted Workflows"]
    end
    
    Backend --> Integration
    Frontend -->|"HTTP/WebSocket"| Backend
    Integration -->|"Managed Execution"| OpenAI["OpenAI API"]
```

**Diagram: Managed ChatKit Technology Stack**

**Sources:** [README.md:7-8]()

### When to Choose Managed ChatKit

The managed integration pattern is appropriate when:

- **Reduced Operations**: Team prefers to minimize infrastructure management overhead
- **Rapid Prototyping**: Quick deployment without server maintenance concerns
- **Scalability**: Automatic scaling handled by hosted infrastructure
- **Standard Workflows**: Application requirements align with platform-provided workflow patterns

Conversely, choose self-hosted ChatKit (see [Self-Hosted ChatKit](#3)) when requiring:
- Complete control over conversation logic and state management
- Custom storage backends (databases, caching layers)
- Integration with existing infrastructure
- Specific security or compliance requirements

**Sources:** [README.md:7-8]()

---

## 4.2 Architecture Differences

### Structural Organization

The `managed-chatkit/` directory follows the same structural pattern as `chatkit/`, maintaining consistency across examples:

```
managed-chatkit/
├── backend/          # FastAPI application
│   ├── app/
│   ├── pyproject.toml
│   └── requirements.txt
└── frontend/         # Vite + React UI
    ├── src/
    ├── package.json
    └── vite.config.ts
```

This parallel structure allows developers to compare implementations directly and understand the specific modifications required for hosted workflow integration.

**Sources:** [README.md:8]()

### Request Flow Comparison

The fundamental difference between self-hosted and managed approaches lies in **where workflow execution occurs**:

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "React Frontend"
    participant Backend as "FastAPI Backend"
    participant Workflow as "Workflow Execution"
    participant OpenAI as "OpenAI API"
    
    Note over User,OpenAI: Self-Hosted Flow (chatkit)
    User->>Frontend: Send message
    Frontend->>Backend: POST /chatkit
    Backend->>Backend: Local StarterChatServer
    Backend->>Backend: MemoryStore
    Backend->>Backend: Local agent execution
    Backend->>OpenAI: Direct API call
    OpenAI-->>Backend: Streaming response
    Backend-->>Frontend: Stream events
    Frontend-->>User: Display response
    
    Note over User,OpenAI: Managed Flow (managed-chatkit)
    User->>Frontend: Send message
    Frontend->>Backend: POST /chatkit
    Backend->>Workflow: Delegate to hosted workflow
    Workflow->>Workflow: Managed state & orchestration
    Workflow->>OpenAI: Platform-managed API call
    OpenAI-->>Workflow: Streaming response
    Workflow-->>Backend: Stream events
    Backend-->>Frontend: Stream events
    Frontend-->>User: Display response
```

**Diagram: Request Flow Comparison Between Integration Patterns**

**Sources:** [README.md:7-8]()

### Component Responsibilities

The managed approach shifts several responsibilities from application code to platform infrastructure:

| Component | Self-Hosted Implementation | Managed Implementation |
|-----------|---------------------------|------------------------|
| **Conversation State** | `MemoryStore` class in [chatkit/backend/app/server.py]() | Hosted platform persistence |
| **Agent Orchestration** | `StarterChatServer.respond()` method | Hosted workflow engine |
| **API Key Management** | Application environment variables | Platform credential management |
| **Streaming Logic** | `run_streamed()` in application code | Platform streaming infrastructure |
| **Error Handling** | Custom retry/fallback logic | Platform-managed resilience |

**Sources:** [README.md:7-8]()

### Configuration Differences

While both implementations require similar environment variables for frontend configuration (see [Environment Configuration](#2.2)), the backend configuration differs:

**Common Frontend Variables:**
```
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_*
```

**Backend Configuration Differences:**

| Variable | Self-Hosted | Managed |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Required for direct API access | May be platform-managed |
| Workflow Identifiers | N/A | Required to specify hosted workflow |
| Platform Credentials | N/A | Required for platform authentication |

**Sources:** [README.md:7-8]()

### Development and Deployment

Both implementations share the same development workflow (see [Local Development Setup](#7.1)):

```bash
npm run dev  # Starts both backend and frontend
```

However, deployment considerations differ:

```mermaid
graph TB
    subgraph Development["Development (Both Patterns)"]
        LOCAL["npm run dev<br/>Local backend + frontend"]
    end
    
    subgraph SelfHostedDeploy["Self-Hosted Deployment"]
        SH_INFRA["Provision infrastructure<br/>Database, servers, monitoring"]
        SH_DB["Migrate from MemoryStore<br/>to persistent storage"]
        SH_SCALE["Configure scaling,<br/>load balancing"]
    end
    
    subgraph ManagedDeploy["Managed Deployment"]
        M_CONFIG["Configure workflow<br/>references"]
        M_PLATFORM["Deploy to platform<br/>infrastructure"]
        M_AUTO["Automatic scaling<br/>and management"]
    end
    
    Development --> SelfHostedDeploy
    Development --> ManagedDeploy
    
    SH_INFRA --> SH_DB --> SH_SCALE
    M_CONFIG --> M_PLATFORM --> M_AUTO
```

**Diagram: Deployment Path Comparison**

**Sources:** [README.md:7-8]()

### Code Reuse and Portability

The parallel structure between `chatkit/` and `managed-chatkit/` facilitates:

1. **Pattern Migration**: Developers can start with managed workflows and migrate to self-hosted as requirements evolve
2. **Frontend Compatibility**: UI components remain largely identical, requiring only configuration changes
3. **Learning Path**: Understanding one implementation provides foundation for the other

**Sources:** [README.md:1-9]()

---

## Integration with CI/CD

Both starter applications are validated through the same CI/CD pipeline (see [CI/CD Pipeline](#6)), ensuring code quality consistency:

- Python backend validation: syntax, linting (ruff), formatting, type checking (mypy)
- Frontend validation: dependency installation, ESLint, build verification

This unified quality assurance approach ensures both examples maintain equivalent code standards regardless of their deployment model.

**Sources:** [README.md:1-9]()

---

## Next Steps

To get started with Managed ChatKit:

1. Review [Installation & Prerequisites](#2.1) for required software versions
2. Configure environment variables as described in [Environment Configuration](#2.2)
3. Follow [Running the Application](#2.3) to start the development servers
4. For production deployment considerations, see [Deployment Considerations](#8)

To compare with the self-hosted approach in detail, see [Self-Hosted ChatKit](#3) for complete implementation documentation including `StarterChatServer`, `MemoryStore`, and agent configuration.

**Sources:** [README.md:1-9]()

---

