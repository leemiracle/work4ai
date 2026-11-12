# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE/pull_request_template.md](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)
- [README.md](README.md)
- [docs/README.hu-Cs4K1Sr4C.md](docs/README.hu-Cs4K1Sr4C.md)
- [docs/README.zh-HANS.md](docs/README.zh-HANS.md)
- [next/src/components/console/ChatMessage.tsx](next/src/components/console/ChatMessage.tsx)
- [next/src/components/console/ChatWindow.tsx](next/src/components/console/ChatWindow.tsx)
- [next/src/components/console/MacWindowHeader.tsx](next/src/components/console/MacWindowHeader.tsx)
- [next/src/components/console/SummarizeButton.tsx](next/src/components/console/SummarizeButton.tsx)
- [next/src/pages/agent/index.tsx](next/src/pages/agent/index.tsx)
- [next/src/pages/index.tsx](next/src/pages/index.tsx)
- [next/src/services/agent/agent-run-model.tsx](next/src/services/agent/agent-run-model.tsx)
- [next/src/services/agent/autonomous-agent.ts](next/src/services/agent/autonomous-agent.ts)
- [next/src/services/agent/message-service.ts](next/src/services/agent/message-service.ts)
- [next/src/stores/agentStore.ts](next/src/stores/agentStore.ts)

</details>



This document provides a comprehensive overview of the AgentGPT system, covering its architecture, core components, and execution flow. AgentGPT is an autonomous AI agent platform that allows users to configure and deploy AI agents capable of pursuing complex goals through iterative task execution and learning.

The system consists of a Next.js frontend application, a FastAPI backend platform, and various supporting services. Users can define goals for AI agents, which then autonomously break down these goals into tasks, execute them using various tools, and learn from the results to achieve their objectives.

For detailed information about specific subsystems, see [Frontend](#2) for the user interface components, [Backend](#3) for the Python services, and [Agent System](#4) for the autonomous agent execution logic.

## System Purpose

AgentGPT enables users to create and deploy autonomous AI agents through a web browser interface. The platform handles the complete lifecycle of agent execution, from goal definition to task completion, while providing real-time feedback and interaction capabilities.

**Sources:** [README.md:24-26](), [next/src/pages/index.tsx:31-180]()

## High-Level Architecture

The system follows a modern full-stack architecture with clear separation between frontend presentation, backend services, and external integrations.

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        HomePage["pages/index.tsx"]
        ChatInterface["components/console/ChatWindow.tsx"]
        AgentControls["components/index/landing.tsx"]
        StateManagement["stores/agentStore.ts"]
    end
    
    subgraph "Service Layer"  
        AutonomousAgent["services/agent/autonomous-agent.ts"]
        AgentAPI["services/agent/agent-api.ts"]
        MessageService["services/agent/message-service.ts"]
        AgentRunModel["services/agent/agent-run-model.tsx"]
    end
    
    subgraph "Backend Platform"
        FastAPI["platform/ (FastAPI)"]
        AgentService["Agent Service Endpoints"]
        ToolSystem["Tool System"]
        PromptTemplates["Prompt Templates"]
    end
    
    subgraph "External Services"
        OpenAI["OpenAI API"]
        SearchAPIs["Search APIs (Serper)"]
        ImageGen["Image Generation (Replicate)"]
    end
    
    subgraph "Data Layer"
        MySQL["MySQL Database"]
        Prisma["Prisma ORM"]
    end
    
    HomePage --> ChatInterface
    ChatInterface --> StateManagement
    StateManagement --> AutonomousAgent
    AutonomousAgent --> AgentAPI
    AutonomousAgent --> MessageService
    AutonomousAgent --> AgentRunModel
    
    AgentAPI --> FastAPI
    FastAPI --> AgentService
    AgentService --> ToolSystem
    ToolSystem --> OpenAI
    ToolSystem --> SearchAPIs
    ToolSystem --> ImageGen
    
    AgentAPI --> Prisma
    Prisma --> MySQL
```

**Sources:** [next/src/pages/index.tsx:1-194](), [next/src/services/agent/autonomous-agent.ts:1-172](), [README.md:82-92]()

## Core Components

### Frontend Application

The frontend is built with Next.js 13 and TypeScript, providing a responsive web interface for agent interaction. The main entry point is the `index.tsx` page which conditionally renders either a landing interface or chat interface based on agent state.

Key frontend components include:
- `Landing` component for initial goal input and agent configuration
- `Chat` component for ongoing agent interaction and message display  
- `ChatWindow` and `ChatMessage` components for message presentation
- Zustand stores for state management (`agentStore`, `messageStore`, `taskStore`)

### Backend Services

The backend consists of Python services built with FastAPI, handling agent execution, tool integration, and data persistence. The system uses a service-oriented architecture with clear separation of concerns.

### Agent Execution Engine

The core agent execution is handled by the `AutonomousAgent` class, which manages the complete lifecycle of autonomous task execution. This includes work scheduling, error handling, and state management through various lifecycle phases.

**Sources:** [next/src/pages/index.tsx:31-194](), [next/src/components/console/ChatWindow.tsx:29-114](), [next/src/services/agent/autonomous-agent.ts:17-172]()

## Agent Execution Flow

The following diagram illustrates how an agent processes goals and executes tasks:

### Agent Lifecycle Diagram

```mermaid
sequenceDiagram
    participant User
    participant HomePage as "pages/index.tsx"
    participant AgentStore as "stores/agentStore.ts"
    participant AutonomousAgent as "AutonomousAgent"
    participant MessageService as "MessageService"
    participant AgentAPI as "AgentApi"
    participant FastAPI as "Backend Platform"
    
    User->>HomePage: "Define goal and start agent"
    HomePage->>AgentStore: "setAgent(newAgent)"
    HomePage->>AutonomousAgent: "new AutonomousAgent()"
    AutonomousAgent->>MessageService: "sendGoalMessage()"
    AutonomousAgent->>AgentStore: "setLifecycle('running')"
    
    loop "Agent Execution Loop"
        AutonomousAgent->>AgentAPI: "Execute work item"
        AgentAPI->>FastAPI: "API calls to tools"
        FastAPI-->>AgentAPI: "Tool results"
        AgentAPI-->>AutonomousAgent: "Work completion"
        AutonomousAgent->>MessageService: "Update progress"
        MessageService->>HomePage: "Render messages"
    end
    
    AutonomousAgent->>AgentStore: "setLifecycle('stopped')"
```

The agent execution follows this pattern:
1. User defines a goal through the web interface
2. A new `AutonomousAgent` instance is created with the goal
3. The agent enters a work execution loop, processing tasks sequentially
4. Each work item involves API calls to backend tools and services
5. Progress updates are streamed to the user interface in real-time
6. The agent continues until all tasks are completed or stopped by the user

**Sources:** [next/src/pages/index.tsx:72-101](), [next/src/services/agent/autonomous-agent.ts:42-82](), [next/src/services/agent/message-service.ts:19-106]()

## Technology Stack

The system leverages a modern technology stack optimized for AI application development:

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend Framework | Next.js 13 + TypeScript | React-based web application with server-side rendering |
| State Management | Zustand | Lightweight state management for React components |
| Styling | TailwindCSS + HeadlessUI | Utility-first CSS framework with accessible components |
| Backend API | FastAPI | High-performance Python web framework for APIs |
| Database | MySQL + Prisma | Relational database with type-safe ORM |
| Authentication | Next-Auth.js | Authentication and session management |
| Schema Validation | Zod + Pydantic | Runtime type validation for frontend and backend |
| AI Integration | OpenAI API | Large language model integration |
| Containerization | Docker | Application containerization and deployment |

### Component Integration Diagram

```mermaid
graph TD
    subgraph "State Management Layer"
        useAgentStore["useAgentStore"]
        useMessageStore["useMessageStore"] 
        useTaskStore["useTaskStore"]
        useAgentInputStore["useAgentInputStore"]
    end
    
    subgraph "Service Classes"
        DefaultAgentRunModel["DefaultAgentRunModel"]
        MessageService["MessageService"]
        AgentApi["AgentApi"]
    end
    
    subgraph "React Components"
        Home["Home (index.tsx)"]
        Landing["Landing"]
        Chat["Chat"]
        ChatWindow["ChatWindow"]
        ChatMessage["ChatMessage"]
    end
    
    Home --> useAgentStore
    Home --> useMessageStore
    Home --> useAgentInputStore
    Home --> DefaultAgentRunModel
    Home --> MessageService
    Home --> AgentApi
    
    Landing --> useAgentInputStore
    Chat --> useMessageStore
    ChatWindow --> useAgentStore
    ChatMessage --> useMessageStore
    
    DefaultAgentRunModel --> useAgentStore
    DefaultAgentRunModel --> useTaskStore
    MessageService --> useMessageStore
```

The architecture emphasizes separation of concerns with dedicated layers for state management, business logic, and presentation. The Zustand stores provide centralized state management, while service classes handle business logic and external API interactions.

**Sources:** [README.md:82-92](), [next/src/stores/agentStore.ts:1-97](), [next/src/services/agent/agent-run-model.tsx:34-80](), [next/src/components/console/ChatWindow.tsx:29-114]()

## Deployment Architecture

AgentGPT supports multiple deployment configurations through Docker containerization and automated setup scripts. The system can be deployed locally for development or in production environments.

The deployment includes:
- Automated environment setup via CLI tools (`setup.sh`, `setup.bat`)
- Docker Compose orchestration for multi-service deployment
- Environment variable configuration for API keys and database connections
- Database migration and initialization scripts

**Sources:** [README.md:36-78](), [README.md:45-56]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE/pull_request_template.md](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)
- [README.md](README.md)
- [docs/README.hu-Cs4K1Sr4C.md](docs/README.hu-Cs4K1Sr4C.md)
- [docs/README.zh-HANS.md](docs/README.zh-HANS.md)
- [next/package-lock.json](next/package-lock.json)
- [next/package.json](next/package.json)
- [next/public/locales/en/indexPage.json](next/public/locales/en/indexPage.json)
- [next/src/components/Button.tsx](next/src/components/Button.tsx)
- [next/src/components/Input.tsx](next/src/components/Input.tsx)
- [next/src/components/Label.tsx](next/src/components/Label.tsx)
- [next/src/components/Switch.tsx](next/src/components/Switch.tsx)
- [next/src/components/console/ChatMessage.tsx](next/src/components/console/ChatMessage.tsx)
- [next/src/components/drawer/DrawerItemButton.tsx](next/src/components/drawer/DrawerItemButton.tsx)
- [next/src/server/api/routers/agentRouter.ts](next/src/server/api/routers/agentRouter.ts)
- [platform/poetry.lock](platform/poetry.lock)
- [platform/pyproject.toml](platform/pyproject.toml)
- [platform/reworkd_platform/settings.py](platform/reworkd_platform/settings.py)
- [platform/reworkd_platform/web/api/agent/dependancies.py](platform/reworkd_platform/web/api/agent/dependancies.py)

</details>



## Purpose and Scope

This document describes the overall system architecture of AgentGPT, an autonomous AI agent platform that allows users to configure and deploy AI agents in their browser. It covers the high-level technical architecture, key components, data flow, and integration points between the Next.js frontend, FastAPI backend, and external services.

For information about specific agent execution flows and algorithms, see [Agent System](#4). For deployment and configuration details, see [Setup and Deployment](#5).

## High-Level Architecture Overview

AgentGPT follows a modern full-stack architecture with clear separation between frontend and backend services:

```mermaid
graph TB
    subgraph "Frontend Layer"
        NEXTJS["next (Next.js 13 + TypeScript)"]
        TRPC["@trpc/client"]
        PRISMA["@prisma/client"]
        ZUSTAND["zustand (State Management)"]
    end
    
    subgraph "Backend Layer"
        FASTAPI["reworkd_platform (FastAPI)"]
        AGENT_SERVICE["OpenAIAgentService"]
        TOOLS["Tool System"]
        SQLALCHEMY["SQLAlchemy ORM"]
    end
    
    subgraph "Database Layer"
        MYSQL["MySQL Database"]
    end
    
    subgraph "External Services"
        OPENAI["OpenAI API"]
        SERP["SERP API (Search)"]
        REPLICATE["Replicate API (Images)"]
    end
    
    NEXTJS --> TRPC
    NEXTJS --> PRISMA
    NEXTJS --> ZUSTAND
    TRPC --> FASTAPI
    PRISMA --> MYSQL
    FASTAPI --> AGENT_SERVICE
    FASTAPI --> SQLALCHEMY
    AGENT_SERVICE --> TOOLS
    SQLALCHEMY --> MYSQL
    TOOLS --> OPENAI
    TOOLS --> SERP
    TOOLS --> REPLICATE
```

The system uses a microservices-inspired approach where the frontend handles user interactions and state management, while the backend focuses on AI agent orchestration and external service integration.

**Sources:** [README.md:82-92](), [next/package.json:17-64](), [platform/pyproject.toml:16-44]()

## Frontend Architecture

The frontend is built with Next.js 13 and TypeScript, providing a modern React-based user interface:

```mermaid
graph TD
    subgraph "Pages & Routing"
        HOME["/ (Home Page)"]
        AGENT_PAGE["/agent/[id] (Agent View)"]
    end
    
    subgraph "Core Components"
        CHATMESSAGE["ChatMessage"]
        INPUT["Input"]
        BUTTON["Button"]
        SWITCH["Switch"]
    end
    
    subgraph "API Layer"
        AGENT_ROUTER["agentRouter (tRPC)"]
        AGENT_API["next/src/server/api/routers/agentRouter.ts"]
    end
    
    subgraph "State Management"
        AGENT_STORE["Agent Store (Zustand)"]
        MESSAGE_STORE["Message Store (Zustand)"]
    end
    
    subgraph "Database Integration"
        PRISMA_CLIENT["@prisma/client"]
        PRISMA_SCHEMA["prisma/schema.prisma"]
    end
    
    HOME --> CHATMESSAGE
    HOME --> INPUT
    HOME --> BUTTON
    CHATMESSAGE --> MESSAGE_STORE
    INPUT --> AGENT_STORE
    AGENT_ROUTER --> PRISMA_CLIENT
    AGENT_API --> PRISMA_SCHEMA
    AGENT_STORE --> AGENT_ROUTER
```

### Key Frontend Components

| Component | Purpose | File Path |
|-----------|---------|-----------|
| `ChatMessage` | Renders agent messages and task status | [next/src/components/console/ChatMessage.tsx]() |
| `Input` | Reusable form input component | [next/src/components/Input.tsx]() |
| `Button` | Interactive button with loading states | [next/src/components/Button.tsx]() |
| `agentRouter` | tRPC router for agent operations | [next/src/server/api/routers/agentRouter.ts]() |

The frontend uses tRPC for type-safe API communication, ensuring compile-time validation of API contracts between frontend and backend.

**Sources:** [next/src/components/console/ChatMessage.tsx:1-109](), [next/src/components/Input.tsx:1-73](), [next/src/components/Button.tsx:1-63](), [next/src/server/api/routers/agentRouter.ts:1-125]()

## Backend Architecture

The backend is implemented with FastAPI and follows a layered architecture pattern:

```mermaid
graph TB
    subgraph "API Layer"
        FASTAPI_APP["FastAPI Application"]
        AGENT_ROUTER_BE["AgentRouter (Backend)"]
        DEPENDENCIES["dependancies.py"]
    end
    
    subgraph "Service Layer"
        AGENT_CRUD["AgentCRUD"]
        OPENAI_SERVICE["OpenAIAgentService"]
        MOCK_SERVICE["MockAgentService"]
    end
    
    subgraph "Tool System"
        SEARCH_TOOL["SearchTool"]
        CODE_TOOL["CodeTool"]
        IMAGE_TOOL["ImageTool"]
        REASON_TOOL["ReasonTool"]
        CONCLUDE_TOOL["ConcludeTool"]
    end
    
    subgraph "Configuration"
        SETTINGS["Settings (settings.py)"]
        ENV_CONFIG[".env Configuration"]
    end
    
    subgraph "External APIs"
        OPENAI_API["OpenAI API"]
        SERP_API["SERP API"]
        REPLICATE_API["Replicate API"]
    end
    
    FASTAPI_APP --> AGENT_ROUTER_BE
    AGENT_ROUTER_BE --> DEPENDENCIES
    DEPENDENCIES --> AGENT_CRUD
    AGENT_CRUD --> OPENAI_SERVICE
    OPENAI_SERVICE --> SEARCH_TOOL
    OPENAI_SERVICE --> CODE_TOOL
    OPENAI_SERVICE --> IMAGE_TOOL
    SEARCH_TOOL --> SERP_API
    CODE_TOOL --> OPENAI_API
    IMAGE_TOOL --> REPLICATE_API
    SETTINGS --> ENV_CONFIG
    OPENAI_SERVICE --> SETTINGS
```

### Core Backend Services

The backend uses dependency injection through FastAPI's dependency system. The `AgentCRUD` class manages database operations, while service classes handle AI agent logic:

```python
# Example of dependency injection pattern
def agent_crud(
    user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AgentCRUD:
    return AgentCRUD(session, user)
```

### Configuration Management

The `Settings` class centralizes all configuration using Pydantic's `BaseSettings`:

| Setting Category | Key Properties | Purpose |
|------------------|----------------|---------|
| OpenAI | `openai_api_key`, `openai_api_base` | API access configuration |
| Database | `db_host`, `db_port`, `db_user`, `db_pass` | MySQL connection settings |
| External APIs | `serp_api_key`, `replicate_api_key` | Third-party service integration |

**Sources:** [platform/reworkd_platform/web/api/agent/dependancies.py:1-96](), [platform/reworkd_platform/settings.py:34-179]()

## Database Architecture and Data Flow

The system uses MySQL as the primary database with dual ORM access patterns:

```mermaid
graph LR
    subgraph "Frontend Database Access"
        PRISMA_CLIENT["@prisma/client"]
        PRISMA_SCHEMA["prisma/schema.prisma"]
    end
    
    subgraph "Backend Database Access"
        SQLALCHEMY["SQLAlchemy"]
        ASYNC_SESSION["AsyncSession"]
    end
    
    subgraph "Database"
        MYSQL_DB["MySQL Database"]
        AGENT_TABLE["Agent Table"]
        TASK_TABLE["AgentTask Table"]
        USER_TABLE["User Table"]
    end
    
    PRISMA_CLIENT --> PRISMA_SCHEMA
    PRISMA_SCHEMA --> MYSQL_DB
    SQLALCHEMY --> ASYNC_SESSION
    ASYNC_SESSION --> MYSQL_DB
    MYSQL_DB --> AGENT_TABLE
    MYSQL_DB --> TASK_TABLE
    MYSQL_DB --> USER_TABLE
```

### Data Flow Patterns

1. **Agent Creation**: Frontend creates agents via tRPC → `agentRouter.create` → Prisma → MySQL
2. **Task Execution**: Backend services use SQLAlchemy for transactional operations
3. **Real-time Updates**: WebSocket connections for streaming agent progress

The dual ORM approach allows the frontend to use Prisma's type-safe client while the backend leverages SQLAlchemy's advanced async capabilities for complex operations.

**Sources:** [next/src/server/api/routers/agentRouter.ts:56-67](), [platform/reworkd_platform/settings.py:122-130]()

## External Service Integration

AgentGPT integrates with multiple external APIs to provide comprehensive AI agent capabilities:

### API Integration Architecture

```mermaid
graph TB
    subgraph "Agent Tools"
        SEARCH["SearchTool"]
        CODE["CodeTool"]
        IMAGE["ImageTool"]
        REASON["ReasonTool"]
    end
    
    subgraph "External APIs"
        OPENAI["OpenAI API<br/>gpt-3.5-turbo, gpt-4"]
        SERP["SERP API<br/>Web Search"]
        REPLICATE["Replicate API<br/>Image Generation"]
    end
    
    subgraph "Configuration"
        SETTINGS_CLASS["Settings Class"]
        API_KEYS["API Keys"]
    end
    
    SEARCH --> SERP
    CODE --> OPENAI
    IMAGE --> REPLICATE
    REASON --> OPENAI
    SETTINGS_CLASS --> API_KEYS
    API_KEYS --> OPENAI
    API_KEYS --> SERP
    API_KEYS --> REPLICATE
```

### Service Configuration

The system supports multiple deployment modes through environment configuration:

| Service | Configuration Keys | Purpose |
|---------|-------------------|---------|
| OpenAI | `OPENAI_API_KEY`, `OPENAI_API_BASE` | LLM operations and reasoning |
| SERP | `SERP_API_KEY` | Web search capabilities |
| Replicate | `REPLICATE_API_KEY` | AI image generation |
| Helicone | `HELICONE_API_KEY` | OpenAI proxy and monitoring |

**Sources:** [platform/reworkd_platform/settings.py:54-65](), [README.md:53-55]()

## Development and Deployment Infrastructure

The system supports multiple deployment modes with Docker-based containerization:

### Deployment Architecture

```mermaid
graph TB
    subgraph "Development Setup"
        SETUP_SH["setup.sh"]
        SETUP_BAT["setup.bat"]
        CLI_TOOL["CLI Configuration Tool"]
    end
    
    subgraph "Docker Containers"
        FRONTEND_CONTAINER["Frontend Container<br/>(Next.js)"]
        BACKEND_CONTAINER["Backend Container<br/>(FastAPI)"]
        DB_CONTAINER["MySQL Container"]
    end
    
    subgraph "Configuration"
        ENV_EXAMPLE[".env.example"]
        DOCKER_COMPOSE["docker-compose.yml"]
    end
    
    SETUP_SH --> CLI_TOOL
    CLI_TOOL --> ENV_EXAMPLE
    CLI_TOOL --> DOCKER_COMPOSE
    DOCKER_COMPOSE --> FRONTEND_CONTAINER
    DOCKER_COMPOSE --> BACKEND_CONTAINER
    DOCKER_COMPOSE --> DB_CONTAINER
```

The setup scripts automate environment configuration, Docker container orchestration, and API key management, providing a streamlined developer experience.

**Sources:** [README.md:36-79](), [platform/reworkd_platform/settings.py:172-176]()

---

# Page: Frontend

# Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/public/favicon.svg](next/public/favicon.svg)
- [next/public/locales/en/drawer.json](next/public/locales/en/drawer.json)
- [next/public/prod_square.png](next/public/prod_square.png)
- [next/src/components/AppHead.tsx](next/src/components/AppHead.tsx)
- [next/src/components/BannerBadge.tsx](next/src/components/BannerBadge.tsx)
- [next/src/components/GlowWrapper.tsx](next/src/components/GlowWrapper.tsx)
- [next/src/components/HeroCard.tsx](next/src/components/HeroCard.tsx)
- [next/src/components/NavBar.tsx](next/src/components/NavBar.tsx)
- [next/src/components/console/ChatWindow.tsx](next/src/components/console/ChatWindow.tsx)
- [next/src/components/console/MacWindowHeader.tsx](next/src/components/console/MacWindowHeader.tsx)
- [next/src/components/console/SummarizeButton.tsx](next/src/components/console/SummarizeButton.tsx)
- [next/src/components/landing/Hero.tsx](next/src/components/landing/Hero.tsx)
- [next/src/components/motions/CycleIcons.tsx](next/src/components/motions/CycleIcons.tsx)
- [next/src/pages/agent/index.tsx](next/src/pages/agent/index.tsx)
- [next/src/pages/index.tsx](next/src/pages/index.tsx)
- [next/src/services/agent/agent-run-model.tsx](next/src/services/agent/agent-run-model.tsx)
- [next/src/services/agent/autonomous-agent.ts](next/src/services/agent/autonomous-agent.ts)
- [next/src/services/agent/message-service.ts](next/src/services/agent/message-service.ts)
- [next/src/stores/agentStore.ts](next/src/stores/agentStore.ts)
- [next/src/styles/globals.css](next/src/styles/globals.css)
- [next/tailwind.config.cjs](next/tailwind.config.cjs)

</details>



The frontend is a Next.js application that provides the user interface for interacting with autonomous AI agents. It handles user authentication, agent configuration, real-time chat interfaces, and visual workflow management. This document covers the client-side architecture, components, state management, and integration patterns.

For information about the backend API services, see [Backend](#3). For details on the agent execution system, see [Agent System](#4).

## Architecture Overview

The frontend follows a modern React architecture with Next.js as the framework, TypeScript for type safety, and Zustand for state management.

### Frontend Technology Stack

```mermaid
graph TB
    subgraph "Frontend Framework"
        NextJS["Next.js 13+"]
        React["React 18"]
        TypeScript["TypeScript"]
    end
    
    subgraph "State Management"
        Zustand["Zustand stores"]
        AgentStore["useAgentStore"]
        MessageStore["useMessageStore"] 
        TaskStore["useTaskStore"]
        AgentInputStore["useAgentInputStore"]
    end
    
    subgraph "UI Layer"
        TailwindCSS["Tailwind CSS"]
        HeadlessUI["Headless UI"]
        FramerMotion["Framer Motion"]
        Spline["Spline 3D"]
    end
    
    subgraph "Data Layer"
        AgentAPI["AgentApi"]
        MessageService["MessageService"]
        AutonomousAgent["AutonomousAgent"]
    end
    
    NextJS --> React
    React --> Zustand
    Zustand --> AgentStore
    Zustand --> MessageStore
    Zustand --> TaskStore
    Zustand --> AgentInputStore
    
    React --> TailwindCSS
    React --> HeadlessUI
    React --> FramerMotion
    React --> Spline
    
    React --> AgentAPI
    React --> MessageService
    React --> AutonomousAgent
```

Sources: [next/src/pages/index.tsx:1-194](), [next/src/stores/agentStore.ts:1-97](), [next/src/services/agent/autonomous-agent.ts:1-172](), [next/tailwind.config.cjs:1-278]()

## Page Structure and Routing

The application uses Next.js file-based routing with several key pages and layouts.

### Main Page Components

```mermaid
graph TD
    subgraph "Page Routes"
        IndexPage["pages/index.tsx<br/>Home"]
        AgentPage["pages/agent/index.tsx<br/>AgentPage"]
    end
    
    subgraph "Layout Components"
        DashboardLayout["layout/dashboard<br/>DashboardLayout"]
        AppHead["components/AppHead.tsx<br/>AppHead"]
    end
    
    subgraph "Main UI Components"
        Landing["components/index/landing<br/>Landing"]
        Chat["components/index/chat<br/>Chat"]
        Hero["components/landing/Hero.tsx<br/>Hero"]
        NavBar["components/NavBar.tsx<br/>NavBar"]
    end
    
    subgraph "State Conditional Rendering"
        AgentNull["agent === null"]
        AgentActive["agent !== null"]
    end
    
    IndexPage --> DashboardLayout
    IndexPage --> AgentNull
    IndexPage --> AgentActive
    AgentNull --> Landing
    AgentActive --> Chat
    
    AgentPage --> DashboardLayout
    DashboardLayout --> AppHead
    DashboardLayout --> NavBar
    
    Landing --> Hero
```

Sources: [next/src/pages/index.tsx:138-179](), [next/src/pages/agent/index.tsx:44-95](), [next/src/components/AppHead.tsx:1-33]()

### Page State Logic

The main page (`pages/index.tsx`) conditionally renders either the landing experience or the active agent chat interface based on agent state:

| Condition | Component Rendered | Purpose |
|-----------|-------------------|---------|
| `agent === null` | `Landing` | Initial onboarding and agent creation |
| `agent !== null` | `Chat` | Active agent interaction interface |

Sources: [next/src/pages/index.tsx:153-175]()

## Key UI Components

### Hero Component

The `Hero` component provides the main landing page experience with 3D graphics and interactive elements.

```mermaid
graph LR
    subgraph "Hero.tsx Component Structure"
        Hero["Hero"]
        SplineGraphics["Spline 3D Graphics"]
        HeroCards["HeroCard Slider"]
        BannerBadge["BannerBadge"]
        PrimaryButton["PrimaryButton"]
    end
    
    subgraph "Interactive Elements"
        SliderControls["Slider Navigation"]
        WindowResize["Window Resize Handler"]
        VideoFallback["Mobile Video Fallback"]
    end
    
    subgraph "Animation System"
        FramerMotion["Framer Motion"]
        FadeIn["FadeIn"]
        MotionDiv["motion.div"]
    end
    
    Hero --> SplineGraphics
    Hero --> HeroCards
    Hero --> BannerBadge
    Hero --> PrimaryButton
    
    Hero --> SliderControls
    Hero --> WindowResize
    Hero --> VideoFallback
    
    Hero --> FramerMotion
    FramerMotion --> FadeIn
    FramerMotion --> MotionDiv
```

The Hero component includes:
- **Spline 3D Integration**: Interactive 3D graphics for desktop users ([next/src/components/landing/Hero.tsx:69-75]())
- **Responsive Design**: Falls back to static image on mobile ([next/src/components/landing/Hero.tsx:60-68]())
- **Slider Interface**: Showcases different use cases with animated transitions ([next/src/components/landing/Hero.tsx:115-128]())

Sources: [next/src/components/landing/Hero.tsx:20-200]()

### Navigation System

```mermaid
graph TB
    subgraph "NavBar.tsx Component"
        NavBar["NavBar"]
        DisclosureMenu["Headless UI Disclosure"]
        NavigationItems["navigation array"]
        CycleIcons["CycleIcons"]
    end
    
    subgraph "Navigation Items"
        Home["Home: /home"]
        Blog["Blog: /blog"] 
        Pricing["Pricing: external"]
        Github["Github: external"]
        Docs["Docs: external"]
    end
    
    subgraph "Mobile Menu"
        HamburgerMenu["Mobile Menu Button"]
        DisclosurePanel["Disclosure.Panel"]
    end
    
    NavBar --> DisclosureMenu
    NavBar --> NavigationItems
    NavBar --> CycleIcons
    
    NavigationItems --> Home
    NavigationItems --> Blog
    NavigationItems --> Pricing
    NavigationItems --> Github
    NavigationItems --> Docs
    
    DisclosureMenu --> HamburgerMenu
    DisclosureMenu --> DisclosurePanel
```

Sources: [next/src/components/NavBar.tsx:18-125]()

### Chat Interface

The chat interface handles real-time agent communication and displays conversation history.

```mermaid
graph TD
    subgraph "ChatWindow.tsx Component"
        ChatWindow["ChatWindow"]
        MacWindowHeader["MacWindowHeader"]
        MessageList["Message List Container"]
        ChatControls["Chat Controls"]
    end
    
    subgraph "Message Display"
        ScrollContainer["Scroll Container"]
        AutoScroll["Auto-scroll Logic"]
        ThinkingIndicator["Thinking Indicator"]
    end
    
    subgraph "Export Features"
        ExportMenu["Export Menu"]
        ImageExport["saveElementAsImage"]
        TextCopy["copyElementText"]
        PDFButton["PDFButton"]
    end
    
    ChatWindow --> MacWindowHeader
    ChatWindow --> MessageList
    ChatWindow --> ChatControls
    
    MessageList --> ScrollContainer
    ScrollContainer --> AutoScroll
    ScrollContainer --> ThinkingIndicator
    
    MacWindowHeader --> ExportMenu
    ExportMenu --> ImageExport
    ExportMenu --> TextCopy
    ExportMenu --> PDFButton
```

Sources: [next/src/components/console/ChatWindow.tsx:29-114](), [next/src/components/console/MacWindowHeader.tsx:24-150]()

## State Management System

The frontend uses Zustand for state management with multiple specialized stores.

### Store Architecture

```mermaid
graph TB
    subgraph "Zustand Store System"
        useAgentStore["useAgentStore"]
        useMessageStore["useMessageStore"]
        useTaskStore["useTaskStore"]
        useAgentInputStore["useAgentInputStore"]
    end
    
    subgraph "Agent Store State"
        agent["agent: AutonomousAgent | null"]
        lifecycle["lifecycle: AgentLifecycle"]
        isThinking["isAgentThinking: boolean"]
        summarized["summarized: boolean"]
        tools["tools: ActiveTool[]"]
    end
    
    subgraph "Message Store State" 
        messages["messages: Message[]"]
        addMessage["addMessage()"]
        updateMessage["updateMessage()"]
    end
    
    subgraph "Task Store State"
        tasks["tasks: Task[]"]
        addTask["addTask()"]
        updateTask["updateTask()"]
    end
    
    subgraph "Input Store State"
        nameInput["nameInput: string"]
        goalInput["goalInput: string"]
        setNameInput["setNameInput()"]
        setGoalInput["setGoalInput()"]
    end
    
    useAgentStore --> agent
    useAgentStore --> lifecycle
    useAgentStore --> isThinking
    useAgentStore --> summarized
    useAgentStore --> tools
    
    useMessageStore --> messages
    useMessageStore --> addMessage
    useMessageStore --> updateMessage
    
    useTaskStore --> tasks
    useTaskStore --> addTask
    useTaskStore --> updateTask
    
    useAgentInputStore --> nameInput
    useAgentInputStore --> goalInput
    useAgentInputStore --> setNameInput
    useAgentInputStore --> setGoalInput
```

Sources: [next/src/stores/agentStore.ts:10-97](), [next/src/pages/index.tsx:33-46]()

### Agent Lifecycle Management

The `AgentLifecycle` type defines the possible states:

| State | Description | UI Behavior |
|-------|-------------|-------------|
| `"offline"` | No agent instance | Shows landing page |
| `"running"` | Agent actively executing | Shows thinking indicator |
| `"pausing"` | Agent transitioning to pause | Maintains current UI |
| `"paused"` | Agent execution suspended | Shows resume option |
| `"stopped"` | Agent execution completed | Shows summarize option |

Sources: [next/src/services/agent/agent-run-model.tsx:32](), [next/src/components/console/ChatWindow.tsx:32-33]()

## Agent Integration Layer

The frontend integrates with the agent system through service classes that manage agent lifecycle and communication.

### Service Layer Architecture

```mermaid
graph TB
    subgraph "Frontend Agent Services"
        AutonomousAgent["AutonomousAgent"]
        MessageService["MessageService"]
        AgentApi["AgentApi"]
        DefaultAgentRunModel["DefaultAgentRunModel"]
    end
    
    subgraph "Agent Initialization Flow"
        handleNewAgent["handleNewAgent()"]
        createAgentApi["new AgentApi()"]
        createMessageService["new MessageService()"]
        createAgent["new AutonomousAgent()"]
        setAgent["setAgent()"]
        runAgent["agent.run()"]
    end
    
    subgraph "Message Flow"
        addMessage["addMessage callback"]
        renderMessage["renderMessage()"]
        updateMessage["updateMessage()"]
        sendMessage["sendMessage()"]
    end
    
    handleNewAgent --> createAgentApi
    createAgentApi --> createMessageService
    createMessageService --> createAgent
    createAgent --> setAgent
    setAgent --> runAgent
    
    MessageService --> addMessage
    addMessage --> renderMessage
    renderMessage --> updateMessage
    updateMessage --> sendMessage
```

Sources: [next/src/pages/index.tsx:72-101](), [next/src/services/agent/autonomous-agent.ts:27-40](), [next/src/services/agent/message-service.ts:12-27]()

### Agent State Synchronization

The frontend maintains synchronization between the agent service and UI state through reactive patterns:

```mermaid
sequenceDiagram
    participant UI as "UI Components"
    participant Store as "Zustand Store"
    participant Agent as "AutonomousAgent"
    participant Message as "MessageService"
    
    UI->>Store: setAgent(newAgent)
    Store->>Agent: agent.run()
    Agent->>Message: sendMessage()
    Message->>Store: addMessage()
    Store->>UI: re-render with new message
    Agent->>Store: setLifecycle("running")
    Store->>UI: update thinking indicator
```

Sources: [next/src/pages/index.tsx:84-100](), [next/src/services/agent/message-service.ts:19-22]()

## Styling and Theme System

The application uses Tailwind CSS with extensive customization for design consistency.

### Custom Design System

The theme system includes custom colors, animations, and utility classes defined in `tailwind.config.cjs`:

| Category | Examples | Purpose |
|----------|----------|---------|
| Custom Colors | `slate.1` through `slate.12` | Consistent grayscale palette |
| Box Shadows | `depth-1`, `depth-2`, `depth-3` | Layered depth system |
| Animations | `animate-border-pulse`, `moveBackground` | Interactive feedback |
| Custom Screens | `sm-h`, `md-h`, `lg-h` | Height-based breakpoints |

Sources: [next/tailwind.config.cjs:75-241](), [next/src/styles/globals.css:162-198]()

### CSS Custom Classes

Key utility classes defined in `globals.css`:

- **`.border-gradient`**: Gradient border effects for UI elements ([next/src/styles/globals.css:15-20]())
- **`.resend-font-effect-hero`**: Text shadow effects for hero text ([next/src/styles/globals.css:9-13]())
- **`.window-heights`**: Responsive height utilities ([next/src/styles/globals.css:76-78]())

Sources: [next/src/styles/globals.css:1-198]()

---

# Page: Landing Page UI

# Landing Page UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/public/favicon.svg](next/public/favicon.svg)
- [next/public/hero-background.png](next/public/hero-background.png)
- [next/public/locales/en/drawer.json](next/public/locales/en/drawer.json)
- [next/public/prod_square.png](next/public/prod_square.png)
- [next/src/components/AppHead.tsx](next/src/components/AppHead.tsx)
- [next/src/components/BannerBadge.tsx](next/src/components/BannerBadge.tsx)
- [next/src/components/GlowWrapper.tsx](next/src/components/GlowWrapper.tsx)
- [next/src/components/HeroCard.tsx](next/src/components/HeroCard.tsx)
- [next/src/components/Menu.tsx](next/src/components/Menu.tsx)
- [next/src/components/NavBar.tsx](next/src/components/NavBar.tsx)
- [next/src/components/WindowButton.tsx](next/src/components/WindowButton.tsx)
- [next/src/components/landing/Backing.tsx](next/src/components/landing/Backing.tsx)
- [next/src/components/landing/ConnectorSection.tsx](next/src/components/landing/ConnectorSection.tsx)
- [next/src/components/landing/FooterLinks.tsx](next/src/components/landing/FooterLinks.tsx)
- [next/src/components/landing/Hero.tsx](next/src/components/landing/Hero.tsx)
- [next/src/components/motions/CycleIcons.tsx](next/src/components/motions/CycleIcons.tsx)
- [next/src/pages/_app.tsx](next/src/pages/_app.tsx)
- [next/src/pages/home.tsx](next/src/pages/home.tsx)
- [next/src/styles/globals.css](next/src/styles/globals.css)
- [next/tailwind.config.cjs](next/tailwind.config.cjs)

</details>



This document describes the landing page user interface components, structure, and styling used in the AgentGPT application. The landing page serves as the primary entry point for users visiting the application, providing an introduction to the platform's capabilities and encouraging user engagement. For information about the main Agent Interface where users actually interact with AI agents, see [Agent Interface](#2.2).

## Overview

The landing page consists of several key components:
- A navigation bar (NavBar)
- A hero section with animated elements
- Interactive cards showcasing use cases
- A 3D animation element
- Call-to-action buttons
- Footer with additional information

The entire UI is built using React components with Next.js, styled with Tailwind CSS, and includes animations with Framer Motion.

Sources: [next/src/pages/home.tsx:1-40]()

## Component Structure

The landing page is organized as a hierarchy of React components:

```mermaid
graph TD
    HomePage["HomePage (home.tsx)"]
    NavBar["NavBar (NavBar.tsx)"]
    Hero["Hero (landing/Hero.tsx)"]
    FooterSection["Footer Section"]
    
    HomePage --> NavBar
    HomePage --> Hero
    HomePage --> FooterSection
    
    NavBar --> NavLogo["Logo (Dark-default-solid.svg)"]
    NavBar --> NavLinks["Navigation Links"]
    NavBar --> NavPrimaryButton["PrimaryButton"]
    NavBar --> DisclosurePanel["Mobile Menu"]
    
    Hero --> FadeIn["FadeIn Animation"]
    FadeIn --> HeroContent["Hero Content"]
    
    HeroContent --> SplineAnim["3D Spline Animation"]
    HeroContent --> HeroBanner["BannerBadge"]
    HeroContent --> Headline["Headline (Gradient Text)"]
    HeroContent --> Description["Description"]
    HeroContent --> CardSlider["Hero Cards Slider"]
    HeroContent --> HeroCTA["CTA Button"]
    
    CardSlider --> HeroCards["Multiple HeroCards"]
    
    FooterSection --> Backing["Backing Component"]
    FooterSection --> FooterLinks["Footer Links"]
    FooterSection --> Copyright["Copyright Text"]
```

Sources: 
- [next/src/pages/home.tsx:11-37]()
- [next/src/components/landing/Hero.tsx:20-164]()
- [next/src/components/NavBar.tsx:30-124]()

## Navigation Bar (NavBar)

The NavBar component provides navigation to different parts of the application and external resources:

### Structure and Features
- Logo and branding
- Navigation links (Home, Blog, Pricing, Github, Docs)
- Call-to-action button "Join the Waitlist"
- Mobile-responsive design with collapsible menu
- Icon cycling animation on hover

### Implementation Details
- Navigation links are defined in a static array
- Uses Headless UI's Disclosure component for the mobile menu
- Implements CycleIcons animation to highlight current/hovered navigation item
- Border gradient effect for the navigation container

Sources:
- [next/src/components/NavBar.tsx:18-27]() (Navigation links)
- [next/src/components/NavBar.tsx:53-74]() (Desktop navigation)
- [next/src/components/NavBar.tsx:76-91]() (CTA button)
- [next/src/components/NavBar.tsx:93-119]() (Mobile menu)

## Hero Section

The Hero section is the main visual element of the landing page, designed to capture attention and communicate the application's purpose:

### Key Components
1. **Title and Description**: Gradient text with engaging copy about web extraction capabilities
2. **3D Animation**: Interactive Spline animation that renders on desktop, with a static image fallback on mobile
3. **Banner Badge**: Highlighting recent funding announcement with animated hover effect
4. **Hero Cards Carousel**: Showcasing different use cases with horizontally scrollable cards
5. **Call-to-action Button**: "Join the Waitlist" with glow effect

### User Interaction Flow
The Hero section enables several user interactions:

```mermaid
sequenceDiagram
    participant User
    participant Hero as "Hero.tsx"
    participant Cards as "HeroCards"
    participant CTA as "Call-to-action"
    participant Spline as "3D Animation"
    
    User->>Hero: View landing page
    Note over Hero: FadeIn animation plays (delay: 0.75s)
    User->>Spline: Interact with 3D animation
    User->>Cards: View use case cards
    User->>Hero: Click navigation arrows
    Hero->>Cards: Slide cards using motion.div
    User->>CTA: Click "Join the Waitlist"
    CTA->>User: Open typeform in new tab
    User->>Cards: Click card sparkle icon
    Cards->>User: Open typeform in new tab
```

Sources:
- [next/src/components/landing/Hero.tsx:52-163]()
- [next/src/components/landing/Hero.tsx:69-74]() (3D animation)
- [next/src/components/landing/Hero.tsx:86-101]() (Title and description)
- [next/src/components/landing/Hero.tsx:114-141]() (Hero cards carousel)
- [next/src/components/landing/Hero.tsx:143-159]() (CTA button)

## HeroCard Component

Each HeroCard represents a specific use case for the platform, organized as part of the carousel in the Hero section:

### Structure and Properties
- Industry title (e.g., "Manufacturing", "E-commerce")
- Use case subtitle (e.g., "Collect product data", "Get competitor prices")
- Left icon (different for each industry)
- Clickable sparkle icon that opens the waitlist form

### Visual Styling
- Border gradient effect
- Text gradients for title and subtitle
- Glow effect on the sparkle icon

Sources:
- [next/src/components/HeroCard.tsx:7-41]()
- [next/src/components/landing/Hero.tsx:167-198]() (roles array defining cards)

## Visual Styling and Animations

The landing page uses several custom styling techniques and animations:

### CSS Classes and Effects
1. **Gradient Text**: Using the `bg-gradient-to-r` and `bg-clip-text` utilities
2. **Border Gradients**: Custom CSS class `border-gradient` for container borders
3. **Glow Effects**: Using the `GlowWrapper` component for buttons and interactive elements
4. **Animation Components**:
   - `FadeIn`: For fade-in entrance animations
   - `CycleIcons`: For cycling through icons in the navbar
   - Framer Motion `motion.div`: For smooth card carousel animations

### Responsive Design
The layout adapts to different screen sizes:
- Mobile: Simplified layout with image instead of 3D animation
- Tablet: Adjusted spacing and layout
- Desktop: Full layout with all features

### CSS Implementation
The styling is implemented through:
- Tailwind CSS utilities
- Custom CSS classes in globals.css
- Component-specific styling

```mermaid
graph TD
    StyleSystem["Landing Page Styling System"]
    
    StyleSystem --> GlobalCSS["globals.css"]
    StyleSystem --> TailwindUtil["Tailwind Utilities"]
    StyleSystem --> ComponentStyles["Component-specific Styles"]
    
    GlobalCSS --> FontEffects["resend-font-effect-hero"]
    GlobalCSS --> BorderGradient["border-gradient"]
    GlobalCSS --> RadialBG["radial-background-1"]
    GlobalCSS --> AfterGradient["after-gradient"]
    
    TailwindUtil --> FlexLayout["Flexbox Utilities"]
    TailwindUtil --> GridLayout["Grid Utilities"] 
    TailwindUtil --> TextGradients["Text Gradient Utilities"]
    TailwindUtil --> ResponsiveClasses["Responsive Breakpoints"]
    
    ComponentStyles --> GlowWrapperStyle["GlowWrapper.tsx Styles"]
    ComponentStyles --> HeroCardStyle["HeroCard.tsx Styles"]
    ComponentStyles --> NavBarStyle["NavBar.tsx Styles"]
```

Sources:
- [next/src/styles/globals.css:9-13]() (resend-font-effect-hero)
- [next/src/styles/globals.css:15-20]() (border-gradient)
- [next/src/components/GlowWrapper.tsx:9-23]() (Glow effect)
- [next/tailwind.config.cjs:13-19]() (Responsive breakpoints)

## User Interaction Flows

The landing page enables several key user interactions:

### Navigation
- Clicking navigation links in the navbar redirects to different sections of the application
- Mobile menu toggle for smaller screens

### Call-to-Action
- "Join the Waitlist" button in the navbar and hero section
- Clicking HeroCard sparkle icons

### Hero Cards Carousel
- Left/right arrows for manual navigation
- Animation when changing cards

### Screen Size Adaptation
- Dynamic content loading based on screen size (3D animation vs. static image)
- Responsive layout adjustments

Sources:
- [next/src/components/landing/Hero.tsx:30-42]() (Slider navigation)
- [next/src/components/landing/Hero.tsx:143-159]() (CTA button)
- [next/src/components/landing/Hero.tsx:25-49]() (Screen size detection)
- [next/src/components/HeroCard.tsx:28-36]() (HeroCard interaction)

## Integration with Page Structure

The landing page components are integrated into the overall application structure:

```mermaid
graph TD
    AppHead["AppHead (meta tags)"]
    HomePage["HomePage (home.tsx)"]
    NextApp["Next.js App (_app.tsx)"]
    
    NextApp --> HomePage
    HomePage --> AppHead
    HomePage --> BackgroundElements["Background Elements"]
    HomePage --> MainContent["Main Content"]
    HomePage --> FooterSection["Footer Section"]
    
    BackgroundElements --> Stars["Stars Background"]
    BackgroundElements --> GradientOverlay["Gradient Overlay"]
    
    MainContent --> NavBar["NavBar.tsx"]
    MainContent --> Hero["Hero.tsx"]
    
    FooterSection --> Backing["Backing Component"]
    FooterSection --> FooterLinks["Footer Links"]
    FooterSection --> Copyright["Copyright"]
```

Sources:
- [next/src/pages/home.tsx:11-37]()
- [next/src/pages/_app.tsx:17-41]()
- [next/src/components/AppHead.tsx:3-32]()

## Technical Implementation Details

### Key Technologies
- **React & Next.js**: For component-based UI
- **Tailwind CSS**: For styling
- **Framer Motion**: For animations
- **Headless UI**: For accessible UI components like Disclosure
- **Spline**: For 3D animation

### State Management
The Hero component maintains several state variables:
- `sliderIndex`: For tracking the current position in the HeroCard carousel
- `showVideo`: Boolean state for determining whether to show 3D animation or static image

### Event Handlers
- Window resize handler to switch between 3D animation and static image
- Slider button handlers for navigating the HeroCard carousel

Sources:
- [next/src/components/landing/Hero.tsx:22-24]() (State variables)
- [next/src/components/landing/Hero.tsx:26-49]() (Event handlers)
- [next/src/components/landing/Hero.tsx:115-140]() (Carousel implementation)

## Summary

The Landing Page UI serves as an engaging entry point to the AgentGPT application, utilizing modern web technologies to create a visually appealing and interactive experience. Its component-based architecture allows for easy maintenance and extension, while responsive design ensures usability across different devices.

The page effectively communicates the application's value proposition through its hero section, use case cards, and clear call-to-action elements, driving user engagement and conversion.

---

# Page: Agent Interface

# Agent Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/src/components/console/ChatWindow.tsx](next/src/components/console/ChatWindow.tsx)
- [next/src/components/console/MacWindowHeader.tsx](next/src/components/console/MacWindowHeader.tsx)
- [next/src/components/console/SummarizeButton.tsx](next/src/components/console/SummarizeButton.tsx)
- [next/src/pages/agent/index.tsx](next/src/pages/agent/index.tsx)
- [next/src/pages/index.tsx](next/src/pages/index.tsx)
- [next/src/pages/settings.tsx](next/src/pages/settings.tsx)
- [next/src/services/agent/agent-run-model.tsx](next/src/services/agent/agent-run-model.tsx)
- [next/src/services/agent/autonomous-agent.ts](next/src/services/agent/autonomous-agent.ts)
- [next/src/services/agent/message-service.ts](next/src/services/agent/message-service.ts)
- [next/src/stores/agentStore.ts](next/src/stores/agentStore.ts)
- [next/src/stores/modelSettingsStore.ts](next/src/stores/modelSettingsStore.ts)
- [next/src/types/modelSettings.ts](next/src/types/modelSettings.ts)
- [next/src/ui/combox.tsx](next/src/ui/combox.tsx)
- [next/src/ui/input.tsx](next/src/ui/input.tsx)
- [next/src/utils/constants.ts](next/src/utils/constants.ts)

</details>



This document covers the main user interface for interacting with autonomous agents in AgentGPT. It includes the home page layout, chat interface components, state management, and the integration between frontend UI components and backend agent services.

For information about the underlying agent execution logic, see [Agent Service](#3.2). For details about the workflow builder interface, see [Workflow System](#2.5).

## Main Interface Components

The agent interface is primarily implemented in the home page at [next/src/pages/index.tsx](), which conditionally renders different UI states based on the agent's lifecycle. The interface switches between two main modes:

| Component | Purpose | Condition |
|-----------|---------|-----------|
| `Landing` | Initial goal input interface | `agent === null` |
| `Chat` | Active agent interaction interface | `agent !== null` |

The main interface uses the `DashboardLayout` wrapper and manages agent creation through several key services:

```mermaid
graph TD
    HomePage["Home (/index.tsx)"] --> DashboardLayout["DashboardLayout"]
    HomePage --> AgentCondition{"agent !== null?"}
    
    AgentCondition -->|false| Landing["Landing Component"]
    AgentCondition -->|true| Chat["Chat Component"]
    
    Landing --> GoalInput["Goal Input Form"]
    Landing --> HandlePlay["handlePlay()"]
    
    Chat --> ChatWindow["ChatWindow"]
    Chat --> MessageDisplay["Message Display"]
    Chat --> ChatControls["Chat Controls"]
    
    HandlePlay --> NewAgent["handleNewAgent()"]
    NewAgent --> AgentServices["Agent Services"]
    
    AgentServices --> DefaultAgentRunModel["DefaultAgentRunModel"]
    AgentServices --> MessageService["MessageService"]
    AgentServices --> AgentApi["AgentApi"]
    AgentServices --> AutonomousAgent["AutonomousAgent"]
```

**Sources:** [next/src/pages/index.tsx:138-179](), [next/src/layout/dashboard.tsx]()

## Agent State Management

The interface uses Zustand stores to manage agent state, with the primary state flow controlled through the `useAgentStore` and related stores:

```mermaid
graph LR
    UI["User Interface"] --> AgentInputStore["useAgentInputStore"]
    UI --> AgentStore["useAgentStore"]
    UI --> MessageStore["useMessageStore"]
    UI --> TaskStore["useTaskStore"]
    
    AgentInputStore --> nameInput["nameInput"]
    AgentInputStore --> goalInput["goalInput"]
    
    AgentStore --> agent["agent: AutonomousAgent"]
    AgentStore --> lifecycle["lifecycle: AgentLifecycle"]
    AgentStore --> isAgentThinking["isAgentThinking"]
    
    MessageStore --> messages["messages: Message[]"]
    TaskStore --> tasks["tasks: Task[]"]
    
    agent --> AgentLifecycles["'offline' | 'running' | 'pausing' | 'paused' | 'stopped'"]
```

The agent lifecycle transitions are managed through the interface:

| Lifecycle State | UI Behavior | Actions Available |
|-----------------|-------------|-------------------|
| `offline` | Shows Landing component | Start new agent |
| `running` | Shows Chat with thinking indicator | Pause agent, chat |
| `pausing` | Transitioning to paused | None |
| `paused` | Shows Chat with resume option | Resume, stop |
| `stopped` | Shows Chat with restart option | Restart, summarize |

**Sources:** [next/src/stores/agentStore.ts:10-19](), [next/src/services/agent/agent-run-model.tsx:32](), [next/src/pages/index.tsx:37-41]()

## Chat Interface Components

The chat interface is built around the `ChatWindow` component which provides a macOS-style terminal interface:

```mermaid
graph TD
    ChatWindow["ChatWindow"] --> MacWindowHeader["MacWindowHeader"]
    ChatWindow --> MessageList["Message List Container"]
    ChatWindow --> ChatControls["Chat Controls (Optional)"]
    
    MacWindowHeader --> ExportOptions["Export Options"]
    MacWindowHeader --> WindowButtons["Mac Window Buttons"]
    
    ExportOptions --> ImageExport["Image Export"]
    ExportOptions --> CopyToClipboard["Copy to Clipboard"]
    ExportOptions --> PDFExport["PDF Export"]
    
    MessageList --> ScrollContainer["Scroll Container (#messageListId)"]
    MessageList --> ThinkingIndicator["Thinking Indicator"]
    MessageList --> ScrollToBottom["Scroll to Bottom Button"]
    
    ChatControls --> ChatInput["Chat Input Field"]
    ChatControls --> SendButton["Send Chat Button"]
    
    ScrollContainer --> MessageComponents["Individual Message Components"]
```

The chat interface includes several interactive features:

- **Auto-scroll Management**: Tracks user scrolling behavior and conditionally auto-scrolls to new messages
- **Export Functionality**: Allows exporting conversation as image, text, or PDF
- **Real-time Chat**: Supports chatting with running agents through `chatControls` prop
- **Thinking Indicator**: Shows when agent is processing with spinner animation

**Sources:** [next/src/components/console/ChatWindow.tsx:29-114](), [next/src/components/console/MacWindowHeader.tsx:24-118]()

## Agent Creation and Lifecycle

The interface manages agent creation through a structured flow that integrates authentication, model settings, and backend services:

```mermaid
sequenceDiagram
    participant User
    participant HomePage as "Home Page"
    participant Auth as "Authentication"
    participant Stores as "Zustand Stores"
    participant AgentApi as "AgentApi"
    participant AutonomousAgent as "AutonomousAgent"
    
    User->>HomePage: Enter goal and click play
    HomePage->>HomePage: handlePlay(goal)
    
    alt Agent is stopped
        HomePage->>HomePage: handleRestart()
        HomePage->>Stores: resetAllSlices()
    else Agent is new/paused
        HomePage->>HomePage: handleNewAgent(goal)
    end
    
    HomePage->>Auth: Check session
    
    alt No session
        HomePage->>localStorage: Store agent data
        HomePage->>User: Show SignInDialog
    else Has session
        HomePage->>HomePage: Create agent services
        HomePage->>AgentApi: new AgentApi(config)
        HomePage->>AutonomousAgent: new AutonomousAgent(model, messageService, settings, api)
        AutonomousAgent->>AutonomousAgent: run()
        HomePage->>Stores: setAgent(newAgent)
    end
```

The agent creation process involves several key services:

- **`DefaultAgentRunModel`**: Manages task queue and agent run state
- **`MessageService`**: Handles message rendering and updates
- **`AgentApi`**: Interfaces with backend API using model settings and session
- **`AutonomousAgent`**: Main agent orchestrator that runs the execution loop

**Sources:** [next/src/pages/index.tsx:67-101](), [next/src/services/agent/autonomous-agent.ts:27-40](), [next/src/services/agent/message-service.ts:12-17]()

## Settings Integration

The agent interface integrates with the settings system through the `useSettings` hook and model configuration:

```mermaid
graph LR
    SettingsPage["/settings"] --> ModelSettingsStore["useModelSettingsStore"]
    
    ModelSettingsStore --> ModelConfig["Model Configuration"]
    ModelConfig --> customApiKey["customApiKey"]
    ModelConfig --> customModelName["customModelName"]
    ModelConfig --> customTemperature["customTemperature"]
    ModelConfig --> customMaxLoops["customMaxLoops"]
    ModelConfig --> maxTokens["maxTokens"]
    
    HomePage["/index"] --> useSettings["useSettings()"]
    useSettings --> ModelSettingsStore
    
    HomePage --> toApiModelSettings["toApiModelSettings()"]
    toApiModelSettings --> AgentApi["AgentApi configuration"]
    
    AgentApi --> BackendAPI["Backend API calls"]
```

The settings are applied when creating new agents through the `toApiModelSettings` utility function, which converts frontend model settings into the format expected by the backend API.

**Sources:** [next/src/pages/index.tsx:47](), [next/src/pages/settings.tsx:34-67](), [next/src/utils/interfaces.ts](), [next/src/stores/modelSettingsStore.ts:11-31]()

## Message and Task Display

The interface renders different types of messages and tasks through a structured message system:

| Message Type | Display | Purpose |
|--------------|---------|---------|
| `goal` | Goal announcement | Shows initial agent goal |
| `task` | Task with status | Shows queued/running tasks |
| `system` | System message | Shows agent actions/thinking |
| `error` | Error message | Shows error states |

The task management integrates with the `useTaskStore` to track task lifecycle:

- **Task Creation**: New tasks are added through `MessageService.startTask()`
- **Task Updates**: Task status and results are updated through `AgentRunModel`
- **Task Display**: Tasks are rendered with status indicators (started, completed)

**Sources:** [next/src/services/agent/message-service.ts:29-64](), [next/src/stores/taskStore.ts](), [next/src/types/message.ts](), [next/src/types/task.ts]()

---

# Page: UI Components

# UI Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/package-lock.json](next/package-lock.json)
- [next/package.json](next/package.json)
- [next/public/errorFavicon.ico](next/public/errorFavicon.ico)
- [next/public/locales/en/indexPage.json](next/public/locales/en/indexPage.json)
- [next/src/components/Button.tsx](next/src/components/Button.tsx)
- [next/src/components/Input.tsx](next/src/components/Input.tsx)
- [next/src/components/Label.tsx](next/src/components/Label.tsx)
- [next/src/components/PrimaryButton.tsx](next/src/components/PrimaryButton.tsx)
- [next/src/components/Switch.tsx](next/src/components/Switch.tsx)
- [next/src/components/TextButton.tsx](next/src/components/TextButton.tsx)
- [next/src/components/console/MarkdownRenderer.tsx](next/src/components/console/MarkdownRenderer.tsx)
- [next/src/components/console/SourceCard.tsx](next/src/components/console/SourceCard.tsx)
- [next/src/components/console/SourceLink.tsx](next/src/components/console/SourceLink.tsx)
- [next/src/components/drawer/DrawerItemButton.tsx](next/src/components/drawer/DrawerItemButton.tsx)
- [next/src/components/landing/OpenSource.tsx](next/src/components/landing/OpenSource.tsx)
- [next/src/components/sidebar/AuthItem.tsx](next/src/components/sidebar/AuthItem.tsx)
- [next/src/components/sidebar/LinkIconItem.tsx](next/src/components/sidebar/LinkIconItem.tsx)
- [next/src/server/api/root.ts](next/src/server/api/root.ts)
- [next/src/server/api/routers/agentRouter.ts](next/src/server/api/routers/agentRouter.ts)
- [next/src/stores/configStore.ts](next/src/stores/configStore.ts)
- [next/src/ui/button.tsx](next/src/ui/button.tsx)
- [next/src/ui/dialog.tsx](next/src/ui/dialog.tsx)
- [platform/reworkd_platform/db/utils.py](platform/reworkd_platform/db/utils.py)
- [platform/reworkd_platform/services/ssl.py](platform/reworkd_platform/services/ssl.py)

</details>



This document covers the reusable UI component system used throughout the AgentGPT frontend application. These components provide the foundational building blocks for user interfaces including buttons, inputs, dialogs, and specialized content rendering components.

For information about the specific agent interface components and chat UI, see [Agent Interface](#2.2). For details about the workflow-specific UI components, see [Workflow System](#2.5).

## Component Architecture Overview

The UI component system follows a hierarchical structure with base components in the `ui/` directory and specialized components in the `components/` directory. Components are built using TypeScript, Tailwind CSS for styling, and various UI libraries for accessibility and functionality.

```mermaid
graph TD
    subgraph "Base UI Components"
        BaseButton["button.tsx"]
        BaseDialog["dialog.tsx"]
    end
    
    subgraph "Composed Components"
        PrimaryButton["PrimaryButton.tsx"]
        TextButton["TextButton.tsx"]
        Input["Input.tsx"]
        Switch["Switch.tsx"]
    end
    
    subgraph "Specialized Components"
        MarkdownRenderer["MarkdownRenderer.tsx"]
        SourceLink["SourceLink.tsx"]
        AuthItem["AuthItem.tsx"]
        DrawerItemButton["DrawerItemButton.tsx"]
    end
    
    subgraph "External Libraries"
        HeadlessUI["@headlessui/react"]
        RadixUI["@radix-ui/react-*"]
        TailwindCSS["tailwindcss"]
        FramerMotion["framer-motion"]
    end
    
    BaseButton --> PrimaryButton
    BaseButton --> TextButton
    BaseDialog --> AuthItem
    
    PrimaryButton --> SpecializedComponents["Landing Page, Agent Interface"]
    Input --> SpecializedComponents
    MarkdownRenderer --> SpecializedComponents
    
    HeadlessUI --> BaseDialog
    RadixUI --> Switch
    TailwindCSS --> AllComponents["All Components"]
    FramerMotion --> SpecializedComponents
```

Sources: [next/src/ui/button.tsx:1-41](), [next/src/ui/dialog.tsx:1-94](), [next/src/components/PrimaryButton.tsx:1-28](), [next/package.json:17-65]()

## Core Button Components

The button system uses a base `Button` component that provides loading states, accessibility features, and consistent styling, with specialized variants for different use cases.

```mermaid
graph LR
    subgraph "Button Component Hierarchy"
        BaseButtonComponent["`**Button**
        (ui/button.tsx)
        - Loading states
        - Click handlers
        - Accessibility`"]
        
        PrimaryButtonComponent["`**PrimaryButton**
        (PrimaryButton.tsx)
        - White background
        - Black border
        - Hover effects`"]
        
        TextButtonComponent["`**TextButton**
        (TextButton.tsx)
        - Transparent background
        - Neutral colors
        - Hover transitions`"]
        
        LegacyButtonComponent["`**Button (Legacy)**
        (Button.tsx)
        - Blue background
        - Custom loader
        - Deprecated`"]
    end
    
    BaseButtonComponent --> PrimaryButtonComponent
    BaseButtonComponent --> TextButtonComponent
    
    PrimaryButtonComponent --> LandingPage["Landing Page CTAs"]
    TextButtonComponent --> Navigation["Navigation Items"]
    LegacyButtonComponent --> OlderComponents["Older Components"]
```

### Base Button Component

The foundational `Button` component provides core functionality:

| Feature | Implementation | File Reference |
|---------|---------------|----------------|
| Loading States | `loader` prop with `Loader` component | [next/src/ui/button.tsx:31]() |
| Click Handling | Async-aware onClick handler | [next/src/ui/button.tsx:18-21]() |
| Accessibility | Forward ref and proper button attributes | [next/src/ui/button.tsx:17]() |
| Visual Indicators | `Ping` component for notifications | [next/src/ui/button.tsx:31]() |

### Button Variants

**PrimaryButton**: Used for primary actions with white background and black border styling.
- Props: `className`, `children`, `icon`, `onClick`
- Styling: Rounded, hover effects, focus states
- Usage: Main CTAs, deploy buttons

**TextButton**: Used for secondary actions with transparent background.
- Props: `children`, `icon`, `onClick`, `className`
- Styling: Neutral colors, subtle hover effects
- Usage: Navigation, secondary actions

Sources: [next/src/ui/button.tsx:1-41](), [next/src/components/PrimaryButton.tsx:1-28](), [next/src/components/TextButton.tsx:1-27]()

## Input Components

The input system provides flexible form controls with consistent styling and label integration.

```mermaid
graph TD
    InputComponent["`**Input Component**
    (Input.tsx)
    - Text and textarea support
    - Integrated labels
    - Validation states`"]
    
    LabelComponent["`**Label Component**
    (Label.tsx)
    - Tooltip integration
    - Responsive design
    - Type-aware styling`"]
    
    SwitchComponent["`**Switch Component**
    (Switch.tsx)
    - Radix UI primitive
    - SSR-safe state
    - Accessibility`"]
    
    TooltipComponent["`**Tooltip**
    (Referenced)
    - Context help
    - Positioning`"]
    
    InputComponent --> LabelComponent
    LabelComponent --> TooltipComponent
    
    InputComponent --> AgentGoalInput["Agent Goal Input"]
    SwitchComponent --> SettingsToggles["Settings Toggles"]
```

### Input Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Type Support | Text input and textarea modes | [next/src/components/Input.tsx:25-27]() |
| Label Integration | Optional left-side labels with tooltips | [next/src/components/Input.tsx:31-33]() |
| Styling Variants | Small size option, disabled states | [next/src/components/Input.tsx:10]() |
| Keyboard Events | onKeyDown support for shortcuts | [next/src/components/Input.tsx:21]() |

### Switch Component

The `Switch` component uses Radix UI primitives for accessibility:
- SSR-safe state management with `useEffect`
- Proper focus and keyboard navigation
- Visual state indicators with CSS transitions

Sources: [next/src/components/Input.tsx:1-73](), [next/src/components/Label.tsx:1-39](), [next/src/components/Switch.tsx:1-48]()

## Dialog System

The dialog system provides modal interactions using Headless UI for accessibility.

```mermaid
graph LR
    subgraph "Dialog Architecture"
        DialogComponent["`**Dialog**
        (ui/dialog.tsx)
        - Headless UI integration
        - Transition animations
        - Focus management`"]
        
        DialogFeatures["`**Features**
        - Modal overlay
        - Icon support
        - Action buttons
        - Inline variant`"]
        
        AuthItemUsage["`**AuthItem Usage**
        (AuthItem.tsx)
        - User profile dialog
        - Sign out actions
        - Account info`"]
    end
    
    DialogComponent --> DialogFeatures
    DialogComponent --> AuthItemUsage
    
    HeadlessUILib["@headlessui/react"] --> DialogComponent
    TransitionLib["Transition animations"] --> DialogComponent
```

### Dialog Features

| Feature | Purpose | Implementation |
|---------|---------|----------------|
| Overlay | Modal background with opacity transition | [next/src/ui/dialog.tsx:35]() |
| Focus Management | Initial focus and keyboard navigation | [next/src/ui/dialog.tsx:23]() |
| Action Buttons | Customizable footer actions | [next/src/ui/dialog.tsx:81-83]() |
| Responsive Design | Mobile and desktop layouts | [next/src/ui/dialog.tsx:40-44]() |

Sources: [next/src/ui/dialog.tsx:1-94](), [next/src/components/sidebar/AuthItem.tsx:62-96]()

## Specialized Content Components

Several components handle specific content rendering and interaction patterns.

### MarkdownRenderer

Renders markdown content with syntax highlighting and interactive features:

```mermaid
graph TD
    MarkdownRenderer["`**MarkdownRenderer**
    - ReactMarkdown integration
    - Syntax highlighting
    - Custom components`"]
    
    CustomPre["`**CustomPre**
    - Code block header
    - Copy functionality
    - Language detection`"]
    
    CustomCodeBlock["`**CustomCodeBlock**
    - Inline and block code
    - Syntax highlighting
    - Language classes`"]
    
    CustomLink["`**CustomLink**
    - External link styling
    - Security attributes
    - Hover effects`"]
    
    MarkdownRenderer --> CustomPre
    MarkdownRenderer --> CustomCodeBlock
    MarkdownRenderer --> CustomLink
    
    ReactMarkdownLib["react-markdown"] --> MarkdownRenderer
    HighlightLib["rehype-highlight"] --> CustomCodeBlock
```

**Key Features:**
- GitHub Flavored Markdown support via `remark-gfm`
- Syntax highlighting with `rehype-highlight`
- Copy-to-clipboard functionality for code blocks
- Custom styling for headers, lists, and links

### SourceLink Component

Displays clickable source links with metadata:
- Fetches link metadata (title, favicon, hostname)
- Loading states with skeleton animation
- Error handling with fallback display
- Numbered indicators for source ordering

Sources: [next/src/components/console/MarkdownRenderer.tsx:1-146](), [next/src/components/console/SourceLink.tsx:1-79](), [next/src/components/console/SourceCard.tsx:1-24]()

## Drawer and Navigation Components

Components for sidebar and navigation interfaces.

```mermaid
graph LR
    subgraph "Navigation Components"
        DrawerItemButton["`**DrawerItemButton**
        (DrawerItemButton.tsx)
        - Text display
        - Click handling
        - Loading states`"]
        
        LinkIconItem["`**LinkIconItem**
        (LinkIconItem.tsx)
        - Icon containers
        - Hover effects
        - Click prevention`"]
        
        AuthItem["`**AuthItem**
        (AuthItem.tsx)
        - User avatar
        - Sign in/out
        - Account dialog`"]
    end
    
    DrawerItemButton --> SidebarContent["Sidebar Content"]
    LinkIconItem --> IconNavigation["Icon Navigation"]
    AuthItem --> UserManagement["User Management"]
```

### Component Responsibilities

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `DrawerItemButton` | Sidebar navigation items | Text truncation, loading states |
| `LinkIconItem` | Icon-based navigation | Hover animations, click handling |
| `AuthItem` | User authentication UI | Avatar display, dialog integration |

Sources: [next/src/components/drawer/DrawerItemButton.tsx:1-30](), [next/src/components/sidebar/LinkIconItem.tsx:1-17](), [next/src/components/sidebar/AuthItem.tsx:1-103]()

## Styling and Theming System

The component system uses a consistent approach to styling and theming.

### Technology Stack

| Technology | Purpose | Usage Pattern |
|------------|---------|---------------|
| Tailwind CSS | Utility-first styling | Class-based styling throughout |
| clsx | Conditional classes | Dynamic styling based on props/state |
| CSS Variables | Color tokens | Slate color palette (slate-1 to slate-12) |
| Framer Motion | Animations | Transitions and interactive animations |

### Styling Patterns

**Conditional Styling**: Components use `clsx` to apply styles based on props:
```typescript
className={clsx(
  "base-classes",
  props.disabled && "disabled-classes",
  props.variant === "primary" && "primary-classes"
)}
```

**Responsive Design**: Components use Tailwind's responsive prefixes:
- `sm:` for small screens and up
- `md:` for medium screens and up
- Mobile-first approach with progressive enhancement

**Color System**: Consistent use of slate color palette:
- `slate-1` to `slate-3`: Background colors
- `slate-6` to `slate-8`: Border colors  
- `slate-10` to `slate-12`: Text colors
- `sky-*`: Accent colors for interactive elements

Sources: [next/src/components/Input.tsx:36-57](), [next/src/ui/dialog.tsx:25-58](), [next/src/components/PrimaryButton.tsx:18-21]()

---

# Page: State Management

# State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/src/components/console/MarkdownRenderer.tsx](next/src/components/console/MarkdownRenderer.tsx)
- [next/src/pages/settings.tsx](next/src/pages/settings.tsx)
- [next/src/stores/configStore.ts](next/src/stores/configStore.ts)
- [next/src/stores/modelSettingsStore.ts](next/src/stores/modelSettingsStore.ts)
- [next/src/types/modelSettings.ts](next/src/types/modelSettings.ts)
- [next/src/ui/combox.tsx](next/src/ui/combox.tsx)
- [next/src/ui/input.tsx](next/src/ui/input.tsx)
- [next/src/utils/constants.ts](next/src/utils/constants.ts)
- [platform/reworkd_platform/db/utils.py](platform/reworkd_platform/db/utils.py)
- [platform/reworkd_platform/services/ssl.py](platform/reworkd_platform/services/ssl.py)

</details>



## Purpose and Scope

This document covers the client-side state management system in the AgentGPT frontend application. The system uses Zustand for reactive state management, handling application configuration, model settings, layout preferences, and user interface state. For backend data persistence and database schemas, see [Storage and Database](#3.4). For API integration patterns, see [Agent API](#3.1).

## Architecture Overview

The AgentGPT frontend implements a distributed state management architecture using Zustand stores. Each store manages a specific domain of application state with built-in persistence and type safety.

### Store Architecture

```mermaid
graph TB
    subgraph "Component Layer"
        SettingsPage["SettingsPage"]
        DashboardLayout["DashboardLayout"]
        AgentInterface["Agent Interface Components"]
    end
    
    subgraph "Hook Layer"
        useSettings["useSettings()"]
        useAuth["useAuth()"]
        useModels["useModels()"]
    end
    
    subgraph "State Stores"
        configStore["useConfigStore"]
        modelSettingsStore["useModelSettingsStore"]
        AgentStore["Agent Store"]
        MessageStore["Message Store"]
        TaskStore["Task Store"]
    end
    
    subgraph "Persistence Layer"
        localStorage["localStorage"]
        createJSONStorage["createJSONStorage()"]
        persistMiddleware["persist middleware"]
    end
    
    subgraph "State Structure"
        LayoutSlice["LayoutSlice"]
        AuthSlice["AuthSlice"]
        ModelSettingsSlice["ModelSettingsSlice"]
    end
    
    SettingsPage --> useSettings
    SettingsPage --> useAuth
    DashboardLayout --> configStore
    AgentInterface --> AgentStore
    
    useSettings --> modelSettingsStore
    useAuth --> configStore
    
    configStore --> LayoutSlice
    configStore --> AuthSlice
    modelSettingsStore --> ModelSettingsSlice
    
    configStore --> persistMiddleware
    modelSettingsStore --> persistMiddleware
    persistMiddleware --> createJSONStorage
    createJSONStorage --> localStorage
```

Sources: [next/src/stores/configStore.ts:1-76](), [next/src/stores/modelSettingsStore.ts:1-55](), [next/src/pages/settings.tsx:32-68]()

## Store Implementations

### Configuration Store

The `useConfigStore` manages application layout and organization state through two primary slices: `LayoutSlice` and `AuthSlice`.

#### Layout Management

```mermaid
graph LR
    subgraph "Layout State"
        showRightSidebar["showRightSidebar: boolean"]
        showLogSidebar["showLogSidebar: boolean"]
    end
    
    subgraph "Layout Actions"
        setLayout["setLayout(layout: Partial<Layout>)"]
    end
    
    subgraph "Business Logic"
        MutualExclusion["Sidebar Mutual Exclusion Logic"]
    end
    
    setLayout --> MutualExclusion
    MutualExclusion --> showRightSidebar
    MutualExclusion --> showLogSidebar
```

The layout slice implements mutual exclusion logic for sidebar visibility:

| Property | Type | Purpose |
|----------|------|---------|
| `showRightSidebar` | `boolean` | Controls right sidebar visibility |
| `showLogSidebar` | `boolean` | Controls log sidebar visibility |

The `setLayout` function enforces that only one sidebar can be visible at a time through conditional logic at [next/src/stores/configStore.ts:37-38]().

#### Organization Management

```mermaid
graph TB
    subgraph "Organization State"
        orgId["id: string"]
        orgName["name: string"] 
        orgRole["role: string"]
    end
    
    subgraph "Organization Actions"
        setOrganization["setOrganization(orgRole: OrganizationRole | undefined)"]
    end
    
    setOrganization --> orgId
    setOrganization --> orgName
    setOrganization --> orgRole
```

The `AuthSlice` manages user organization context through the `OrganizationRole` interface defined at [next/src/stores/configStore.ts:17-21]().

Sources: [next/src/stores/configStore.ts:7-48](), [next/src/stores/configStore.ts:50-59]()

### Model Settings Store

The `useModelSettingsStore` handles AI model configuration and user preferences with comprehensive persistence.

#### Settings State Structure

```mermaid
graph TB
    subgraph "ModelSettings Interface"
        language["language: Language"]
        customApiKey["customApiKey: string"]
        customModelName["customModelName: GPTModelNames"]
        customTemperature["customTemperature: number"]
        customMaxLoops["customMaxLoops: number"]
        maxTokens["maxTokens: number"]
    end
    
    subgraph "Default Values"
        defaultLanguage["ENGLISH"]
        defaultModel["GPT_35_TURBO"]
        defaultTemp["0.8"]
        defaultLoops["DEFAULT_MAX_LOOPS_FREE"]
        defaultTokens["1250"]
    end
    
    subgraph "Store Actions"
        updateSettings["updateSettings<Key>(key: Key, value: ModelSettings[Key])"]
        resetSettings["resetSettings()"]
    end
    
    defaultLanguage --> language
    defaultModel --> customModelName
    defaultTemp --> customTemperature
    defaultLoops --> customMaxLoops
    defaultTokens --> maxTokens
    
    updateSettings --> language
    updateSettings --> customApiKey
    updateSettings --> customModelName
    resetSettings --> defaultLanguage
```

The store implements type-safe updates through generic constraints at [next/src/stores/modelSettingsStore.ts:25-29]().

#### Persistence Configuration

The store uses selective persistence with data transformation:

| Persistence Feature | Implementation | Purpose |
|---------------------|----------------|---------|
| Storage Key | `"agentgpt-settings-storage-v2"` | Versioned localStorage key |
| Partialize Function | Custom transformer | Ensures model compatibility |
| Token Clamping | `Math.min(maxTokens, 4000)` | Prevents invalid token counts |

Sources: [next/src/stores/modelSettingsStore.ts:11-31](), [next/src/stores/modelSettingsStore.ts:33-52](), [next/src/utils/constants.ts:11-20]()

## State Persistence System

### Zustand Middleware Integration

```mermaid
graph LR
    subgraph "Store Creation"
        create["create<T>()"]
        persist["persist()"]
        createJSONStorage["createJSONStorage()"]
    end
    
    subgraph "Storage Backend"
        localStorage["localStorage"]
        storageKey["Storage Key"]
        version["Version Control"]
    end
    
    subgraph "Data Transformation"
        partialize["partialize()"]
        serialize["JSON.stringify()"]
        deserialize["JSON.parse()"]
    end
    
    create --> persist
    persist --> createJSONStorage
    createJSONStorage --> localStorage
    
    persist --> partialize
    partialize --> serialize
    serialize --> storageKey
    storageKey --> version
    
    localStorage --> deserialize
    deserialize --> create
```

Both stores implement persistence through Zustand's `persist` middleware with `createJSONStorage(() => localStorage)` at [next/src/stores/configStore.ts:71]() and [next/src/stores/modelSettingsStore.ts:41]().

### Storage Keys and Versioning

| Store | Storage Key | Version Strategy |
|-------|-------------|------------------|
| Config Store | `"reworkd-config-2"` | Explicit version field |
| Model Settings Store | `"agentgpt-settings-storage-v2"` | Version in key name |

Sources: [next/src/stores/configStore.ts:69-72](), [next/src/stores/modelSettingsStore.ts:40-49]()

## Component Integration Patterns

### Settings Page Integration

The settings page demonstrates comprehensive state integration across multiple stores and external APIs:

```mermaid
graph TB
    subgraph "SettingsPage Component"
        useSettings["useSettings()"]
        useAuth["useAuth()"]
        useModels["useModels()"]
        useState["useState<boolean | undefined>()"]
    end
    
    subgraph "State Operations"
        updateSettings["updateSettings()"]
        updateLanguage["updateLanguage()"]
        validateApiKey["validateApiKey()"]
    end
    
    subgraph "External APIs"
        openaiApi["OpenAI API"]
        i18next["i18next"]
    end
    
    subgraph "UI Components"
        Input["Input"]
        Combo["Combo<T>"]
        Button["Button"]
    end
    
    useSettings --> updateSettings
    useSettings --> updateLanguage
    useState --> validateApiKey
    
    validateApiKey --> openaiApi
    updateLanguage --> i18next
    
    updateSettings --> Input
    updateLanguage --> Combo
    validateApiKey --> Button
```

The component implements real-time API key validation through axios requests to `https://api.openai.com/v1/engines` at [next/src/pages/settings.tsx:40-52]().

### State-UI Synchronization

The settings page demonstrates bidirectional data binding patterns:

| UI Component | State Binding | Update Pattern |
|--------------|---------------|----------------|
| Language Selector | `settings.language` | `updateLanguage(e)` |
| API Key Input | `settings.customApiKey` | `updateSettings("customApiKey", value)` |
| Model Selector | `getModel(settings.customModelName)` | `updateModel(model)` |
| Temperature Slider | `settings.customTemperature` | `updateSettings("customTemperature", value)` |

Sources: [next/src/pages/settings.tsx:91-100](), [next/src/pages/settings.tsx:151-167](), [next/src/pages/settings.tsx:168-182]()

## State Management Patterns

### Type Safety and Generics

The stores implement comprehensive type safety through TypeScript generics and interfaces:

```mermaid
graph TB
    subgraph "Type System"
        StateCreator["StateCreator<T>"]
        ModelSettings["ModelSettings interface"]
        GPTModelNames["GPTModelNames union type"]
        Language["Language interface"]
    end
    
    subgraph "Generic Functions"
        updateSettings["updateSettings<Key extends keyof ModelSettings>()"]
        createSelectors["createSelectors<T>()"]
    end
    
    subgraph "Type Constraints"
        keyofConstraint["Key extends keyof ModelSettings"]
        valueConstraint["value: ModelSettings[Key]"]
    end
    
    StateCreator --> updateSettings
    ModelSettings --> keyofConstraint
    keyofConstraint --> valueConstraint
    updateSettings --> createSelectors
```

The `updateSettings` function uses mapped types for compile-time safety at [next/src/stores/modelSettingsStore.ts:25]().

### Selector Pattern Implementation

Both stores use the `createSelectors` helper to generate automatic selectors:

```typescript
// Enables both object and function access patterns
const store = useConfigStore() // Full state object
const layout = useConfigStore.layout() // Individual selector
```

This pattern is implemented through the helper at [next/src/stores/configStore.ts:5]() and applied at [next/src/stores/configStore.ts:61-75]().

Sources: [next/src/stores/helpers.ts](), [next/src/types/modelSettings.ts:17-24](), [next/src/stores/modelSettingsStore.ts:12-14]()

---

# Page: Workflow System

# Workflow System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/src/services/fetch-utils.ts](next/src/services/fetch-utils.ts)
- [next/src/ui/select.tsx](next/src/ui/select.tsx)

</details>



## Purpose and Scope

The Workflow System provides a visual workflow builder interface that allows users to create and execute AI agent workflows through a flowchart-based interface. This system serves as an alternative to the traditional chat-based agent interface, enabling users to design complex multi-step processes using visual nodes and connections.

This document covers the frontend workflow builder components, visual interface elements, and integration with the backend workflow execution system. For information about the underlying agent execution and task processing, see [Agent System](#4). For details about the API layer that powers workflow execution, see [Agent API](#3.1).

## System Architecture

The Workflow System is implemented as part of the Next.js frontend and consists of several key architectural components that work together to provide visual workflow creation and execution capabilities.

### High-Level Architecture

```mermaid
graph TD
    subgraph "Frontend Workflow System"
        WorkflowPages["WorkflowPages"]
        WorkflowBuilder["WorkflowBuilder"] 
        FlowchartInterface["FlowchartInterface"]
        WorkflowNodes["WorkflowNodes"]
    end
    
    subgraph "Shared UI Components"
        Select["Select"]
        UIComponents["UIComponents"]
    end
    
    subgraph "API Communication"
        FetchUtils["FetchUtils"]
        WorkflowAPI["WorkflowAPI"]
    end
    
    subgraph "Backend Integration"
        AgentService["AgentService"]
        WorkflowExecution["WorkflowExecution"]
    end
    
    WorkflowPages --> WorkflowBuilder
    WorkflowBuilder --> FlowchartInterface
    FlowchartInterface --> WorkflowNodes
    
    WorkflowBuilder --> Select
    WorkflowBuilder --> UIComponents
    
    WorkflowAPI --> FetchUtils
    WorkflowBuilder --> WorkflowAPI
    WorkflowAPI --> AgentService
    AgentService --> WorkflowExecution
```

Sources: Overall system architecture diagram, Component hierarchy diagram

### Component Structure

The workflow system follows a hierarchical component structure where workflow pages contain the builder interface, which in turn manages individual workflow nodes and their connections.

| Component Level | Purpose | Key Responsibilities |
|-----------------|---------|---------------------|
| **Workflow Pages** | Page-level routing and layout | Handle workflow creation, editing, and execution views |
| **Workflow Builder** | Main interface component | Manage workflow state, node creation, and connections |
| **Flowchart Interface** | Visual editor | Render nodes, handle drag-and-drop, manage canvas |
| **Workflow Nodes** | Individual workflow elements | Represent specific actions, conditions, or agent tasks |

Sources: Component hierarchy diagram

## Visual Interface Components

The workflow system leverages shared UI components from the broader AgentGPT frontend to maintain consistency and reusability across the application.

### Select Component Integration

The workflow builder utilizes the generic `Select` component for various configuration options within workflow nodes:

```mermaid
graph LR
    WorkflowNode["WorkflowNode"] --> NodeConfig["NodeConfig"]
    NodeConfig --> Select["Select<T>"]
    Select --> ListboxButton["Listbox.Button"]
    Select --> ListboxOptions["Listbox.Options"]
    
    subgraph "Select Props"
        Value["value: T"]
        OnChange["onChange: (T) => void"]
        Items["items: T[]"]
        ValueMapper["valueMapper: (T) => string"]
        Icon["icon: IconType"]
    end
    
    Select --> Value
    Select --> OnChange  
    Select --> Items
    Select --> ValueMapper
    Select --> Icon
```

Sources: [next/src/ui/select.tsx:8-16]()

The `Select` component provides a flexible dropdown interface that workflow nodes can use for:
- Agent model selection
- Tool selection for specific workflow steps
- Conditional logic options
- Output format configurations

Key features of the select component include:
- Generic type support for any data type
- Custom value mapping for display
- Icon integration for visual identification
- Disabled state support
- Keyboard navigation and accessibility

Sources: [next/src/ui/select.tsx:18-99]()

## API Communication Layer

The workflow system communicates with the backend through a structured API layer that handles workflow creation, execution, and monitoring.

### Fetch Utilities Integration

The workflow API service builds upon the core fetch utilities to maintain consistent error handling and authentication across all backend communications:

```mermaid
graph TD
    subgraph "Workflow API Operations"
        CreateWorkflow["createWorkflow()"]
        ExecuteWorkflow["executeWorkflow()"]
        GetWorkflowStatus["getWorkflowStatus()"]
        UpdateWorkflow["updateWorkflow()"]
        DeleteWorkflow["deleteWorkflow()"]
    end
    
    subgraph "HTTP Methods"
        POST["post()"]
        GET["get()"]
        PUT["put()"]
        DELETE["delete_()"]
    end
    
    subgraph "Request Handling"
        Headers["getHeaders()"]
        Auth["Authorization"]
        OrgId["X-Organization-Id"]
        ContentType["Content-Type"]
    end
    
    CreateWorkflow --> POST
    ExecuteWorkflow --> POST
    GetWorkflowStatus --> GET
    UpdateWorkflow --> PUT
    DeleteWorkflow --> DELETE
    
    POST --> Headers
    GET --> Headers
    PUT --> Headers
    DELETE --> Headers
    
    Headers --> Auth
    Headers --> OrgId
    Headers --> ContentType
```

Sources: [next/src/services/fetch-utils.ts:5-11](), [next/src/services/fetch-utils.ts:13-93]()

### Request Flow

The workflow system follows a consistent pattern for all API communications:

1. **Authentication**: Each request includes bearer token authentication and optional organization ID headers
2. **Schema Validation**: All responses are validated using Zod schemas to ensure type safety
3. **Error Handling**: Failed requests throw standardized errors that the UI can handle consistently
4. **Type Safety**: Generic type parameters ensure compile-time type checking for all API responses

| HTTP Method | Usage in Workflow System | Schema Validation |
|-------------|-------------------------|-------------------|
| `GET` | Retrieve workflow definitions and execution status | Response parsed with Zod schema |
| `POST` | Create new workflows and trigger execution | Request body serialized, response validated |
| `PUT` | Update existing workflow configurations | Full workflow state updates |
| `DELETE` | Remove workflows and cancel executions | Confirmation response validation |

Sources: [next/src/services/fetch-utils.ts:13-30](), [next/src/services/fetch-utils.ts:32-51](), [next/src/services/fetch-utils.ts:53-72](), [next/src/services/fetch-utils.ts:74-93]()

## Integration with Agent System

The workflow system serves as a visual interface layer that ultimately drives the same underlying agent execution engine used by the traditional chat interface.

### Workflow to Agent Translation

```mermaid
sequenceDiagram
    participant User
    participant WorkflowBuilder as "WorkflowBuilder"
    participant WorkflowAPI as "WorkflowAPI" 
    participant FetchUtils as "FetchUtils"
    participant Backend as "Backend"
    participant AgentService as "AgentService"
    
    User->>WorkflowBuilder: "Create Visual Workflow"
    WorkflowBuilder->>WorkflowBuilder: "Build Node Graph"
    User->>WorkflowBuilder: "Execute Workflow"
    WorkflowBuilder->>WorkflowAPI: "translateToAgentTasks()"
    WorkflowAPI->>FetchUtils: "post('/workflows/execute')"
    FetchUtils->>Backend: "HTTP POST with auth headers"
    Backend->>AgentService: "Create Agent with workflow tasks"
    AgentService-->>Backend: "Task execution results"
    Backend-->>FetchUtils: "JSON response"
    FetchUtils-->>WorkflowAPI: "Parsed response"
    WorkflowAPI-->>WorkflowBuilder: "Execution status"
    WorkflowBuilder-->>User: "Visual progress updates"
```

Sources: Agent execution flow diagram, [next/src/services/fetch-utils.ts:32-51]()

### State Management Integration

The workflow system integrates with the existing Zustand-based state management system to maintain consistency with the rest of the application. Workflow state is managed separately but follows the same patterns as agent and message stores.

The workflow system represents a sophisticated visual interface that translates user-created flowcharts into executable agent tasks, leveraging the same robust backend infrastructure that powers the traditional agent interface while providing an intuitive drag-and-drop workflow creation experience.

Sources: Component hierarchy diagram, Backend tool & service architecture diagram

---

# Page: Backend

# Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/src/utils/interfaces.ts](next/src/utils/interfaces.ts)
- [platform/poetry.lock](platform/poetry.lock)
- [platform/pyproject.toml](platform/pyproject.toml)
- [platform/reworkd_platform/settings.py](platform/reworkd_platform/settings.py)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py)
- [platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py)
- [platform/reworkd_platform/web/api/agent/dependancies.py](platform/reworkd_platform/web/api/agent/dependancies.py)
- [platform/reworkd_platform/web/api/agent/views.py](platform/reworkd_platform/web/api/agent/views.py)

</details>



This document provides an overview of the Python/FastAPI backend platform that powers AgentGPT's autonomous agent execution system. The backend handles agent lifecycle management, task processing, tool integration, and external service communication.

For information about the frontend Next.js application, see [Frontend](#2). For details about the agent execution algorithms and lifecycle, see [Agent System](#4).

## Architecture Overview

The AgentGPT backend is built using FastAPI and follows a service-oriented architecture with clear separation between API routing, business logic, and external integrations. The system is designed to handle autonomous agent execution through a series of coordinated services.

```mermaid
graph TB
    subgraph "FastAPI Application"
        ROUTER["/api/agent router<br/>views.py"]
        DEPS["Dependencies<br/>dependancies.py"]
        VALIDATOR["Request Validators"]
    end
    
    subgraph "Agent Service Layer"
        PROVIDER["AgentServiceProvider<br/>agent_service_provider.py"]
        OPENAI_SVC["OpenAIAgentService<br/>open_ai_agent_service.py"]
        MOCK_SVC["MockAgentService<br/>mock_agent_service.py"]
        INTERFACE["AgentService Protocol<br/>agent_service.py"]
    end
    
    subgraph "Core Services"
        TOKEN_SVC["TokenService"]
        MODEL_FACTORY["WrappedChatOpenAI<br/>model_factory.py"]
        SETTINGS["Settings<br/>settings.py"]
    end
    
    subgraph "External APIs"
        OPENAI_API["OpenAI API"]
        TOOLS_API["Tool APIs<br/>(SERP, Replicate, etc.)"]
    end
    
    subgraph "Database"
        MYSQL_DB["MySQL Database<br/>SQLAlchemy + aiomysql"]
    end
    
    ROUTER --> DEPS
    DEPS --> VALIDATOR
    VALIDATOR --> PROVIDER
    PROVIDER --> OPENAI_SVC
    PROVIDER --> MOCK_SVC
    OPENAI_SVC --> INTERFACE
    MOCK_SVC --> INTERFACE
    
    OPENAI_SVC --> TOKEN_SVC
    OPENAI_SVC --> MODEL_FACTORY
    PROVIDER --> SETTINGS
    
    MODEL_FACTORY --> OPENAI_API
    OPENAI_SVC --> TOOLS_API
    
    DEPS --> MYSQL_DB
```

**Backend System Architecture**

Sources: [platform/reworkd_platform/web/api/agent/views.py:1-146](), [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py:1-54](), [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:1-228](), [platform/reworkd_platform/settings.py:1-179]()

## Technology Stack

The backend leverages a modern Python stack optimized for asynchronous processing and AI workloads:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI | High-performance async API server |
| **Database ORM** | SQLAlchemy 2.0 | Async database operations |
| **Database Driver** | aiomysql | Async MySQL connectivity |
| **AI/LLM** | LangChain + OpenAI | Language model orchestration |
| **HTTP Client** | httpx | Async HTTP requests |
| **Streaming** | Lanarky | FastAPI streaming response utilities |
| **Configuration** | Pydantic BaseSettings | Environment-based configuration |
| **Logging** | Loguru | Structured logging |
| **Message Queue** | aiokafka (optional) | Event streaming |

Sources: [platform/pyproject.toml:16-44]()

## Core Agent Service Architecture

The agent service layer implements the core business logic for autonomous agent execution through a clean protocol-based design:

```mermaid
graph TD
    subgraph "Service Protocol Layer"
        PROTOCOL["AgentService Protocol"]
        METHODS["• start_goal_agent()<br/>• analyze_task_agent()<br/>• execute_task_agent()<br/>• create_tasks_agent()<br/>• summarize_task_agent()<br/>• chat()"]
    end
    
    subgraph "Implementation Layer"
        OPENAI_IMPL["OpenAIAgentService"]
        MOCK_IMPL["MockAgentService"]
    end
    
    subgraph "Factory Layer"
        PROVIDER_FUNC["get_agent_service()"]
        FEATURE_FLAG["ff_mock_mode_enabled"]
    end
    
    subgraph "Core Dependencies"
        MODEL["WrappedChatOpenAI"]
        TOKEN_SERVICE["TokenService"]
        SETTINGS_OBJ["ModelSettings"]
        USER["UserBase"]
        OAUTH["OAuthCrud"]
    end
    
    PROTOCOL --> METHODS
    PROTOCOL <|-- OPENAI_IMPL
    PROTOCOL <|-- MOCK_IMPL
    
    PROVIDER_FUNC --> FEATURE_FLAG
    FEATURE_FLAG -->|"enabled"| MOCK_IMPL
    FEATURE_FLAG -->|"disabled"| OPENAI_IMPL
    
    OPENAI_IMPL --> MODEL
    OPENAI_IMPL --> TOKEN_SERVICE
    OPENAI_IMPL --> SETTINGS_OBJ
    OPENAI_IMPL --> USER
    OPENAI_IMPL --> OAUTH
```

**Agent Service Class Hierarchy**

Sources: [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py:1-52](), [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:43-58](), [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py:22-54]()

## FastAPI Router and Endpoints

The API layer exposes agent functionality through RESTful endpoints that handle the complete agent execution workflow:

```mermaid
graph LR
    subgraph "API Endpoints"
        START["/start<br/>POST"]
        ANALYZE["/analyze<br/>POST"] 
        EXECUTE["/execute<br/>POST"]
        CREATE["/create<br/>POST"]
        SUMMARIZE["/summarize<br/>POST"]
        CHAT["/chat<br/>POST"]
        TOOLS["/tools<br/>GET"]
    end
    
    subgraph "Request Bodies"
        AGENT_RUN["AgentRun"]
        TASK_ANALYZE["AgentTaskAnalyze"]
        TASK_EXECUTE["AgentTaskExecute"]
        TASK_CREATE["AgentTaskCreate"]
        AGENT_SUMMARIZE["AgentSummarize"]
        AGENT_CHAT["AgentChat"]
    end
    
    subgraph "Response Types"
        NEW_TASKS["NewTasksResponse"]
        ANALYSIS_RESP["Analysis"]
        STREAMING["StreamingResponse"]
        TOOLS_RESP["ToolsResponse"]
    end
    
    START --> AGENT_RUN
    ANALYZE --> TASK_ANALYZE
    EXECUTE --> TASK_EXECUTE
    CREATE --> TASK_CREATE
    SUMMARIZE --> AGENT_SUMMARIZE
    CHAT --> AGENT_CHAT
    
    START --> NEW_TASKS
    ANALYZE --> ANALYSIS_RESP
    EXECUTE --> STREAMING
    CREATE --> NEW_TASKS
    SUMMARIZE --> STREAMING
    CHAT --> STREAMING
    TOOLS --> TOOLS_RESP
```

**API Endpoint Structure**

The core agent workflow endpoints are:

- **`/agent/start`** - Initializes agent with goal and returns initial task list
- **`/agent/analyze`** - Analyzes a task to determine appropriate tool and arguments  
- **`/agent/execute`** - Executes a task using the selected tool (streaming response)
- **`/agent/create`** - Generates new tasks based on execution results
- **`/agent/summarize`** - Creates summary of agent run results (streaming response)
- **`/agent/chat`** - Enables chat interaction with agent results (streaming response)
- **`/agent/tools`** - Returns available tools and their metadata

Sources: [platform/reworkd_platform/web/api/agent/views.py:34-146](), [next/src/utils/interfaces.ts:25-38]()

## Dependency Injection and Validation

The backend uses FastAPI's dependency injection system to handle request validation, database sessions, and service instantiation:

```mermaid
graph TB
    subgraph "Validation Pipeline"
        REQUEST["HTTP Request"]
        VALIDATOR["Request Validator Functions"]
        AGENT_CRUD["AgentCRUD"]
        DB_SESSION["AsyncSession"]
        USER_AUTH["UserBase"]
    end
    
    subgraph "Service Resolution"
        SERVICE_PROVIDER["get_agent_service()"]
        AGENT_SERVICE["AgentService"]
        TOKEN_SERVICE["TokenService"]
        OAUTH_CRUD["OAuthCrud"]
    end
    
    subgraph "Validator Functions"
        START_VALIDATOR["agent_start_validator"]
        ANALYZE_VALIDATOR["agent_analyze_validator"] 
        EXECUTE_VALIDATOR["agent_execute_validator"]
        CREATE_VALIDATOR["agent_create_validator"]
        SUMMARIZE_VALIDATOR["agent_summarize_validator"]
        CHAT_VALIDATOR["agent_chat_validator"]
    end
    
    REQUEST --> VALIDATOR
    VALIDATOR --> AGENT_CRUD
    AGENT_CRUD --> DB_SESSION
    VALIDATOR --> USER_AUTH
    
    VALIDATOR --> START_VALIDATOR
    VALIDATOR --> ANALYZE_VALIDATOR
    VALIDATOR --> EXECUTE_VALIDATOR
    VALIDATOR --> CREATE_VALIDATOR
    VALIDATOR --> SUMMARIZE_VALIDATOR
    VALIDATOR --> CHAT_VALIDATOR
    
    SERVICE_PROVIDER --> AGENT_SERVICE
    SERVICE_PROVIDER --> TOKEN_SERVICE
    SERVICE_PROVIDER --> OAUTH_CRUD
```

**Dependency Injection Flow**

Each endpoint validator creates database records to track agent runs and tasks, ensuring proper audit trails and state management throughout the agent execution process.

Sources: [platform/reworkd_platform/web/api/agent/dependancies.py:26-96]()

## Configuration System

The backend uses Pydantic `BaseSettings` for environment-based configuration management with comprehensive service integrations:

| Configuration Category | Key Settings | Purpose |
|------------------------|--------------|---------|
| **Application** | `host`, `port`, `environment`, `log_level` | Basic server configuration |
| **OpenAI Integration** | `openai_api_key`, `openai_api_base`, `azure_openai_deployment_name` | LLM service configuration |  
| **Database** | `db_host`, `db_port`, `db_user`, `db_pass`, `db_base` | MySQL connection settings |
| **External APIs** | `replicate_api_key`, `serp_api_key`, `helicone_api_key` | Tool service API keys |
| **Feature Flags** | `ff_mock_mode_enabled`, `max_loops` | Development and safety controls |
| **Security** | `secret_signing_key`, `frontend_url` | Authentication and CORS |

The `Settings` class includes computed properties like `db_url`, `pusher_enabled`, `kafka_enabled` that derive connection URLs and feature availability from the base configuration.

Sources: [platform/reworkd_platform/settings.py:34-179]()

## Database Integration

The backend uses SQLAlchemy 2.0 with async support for database operations, connecting to MySQL via the `aiomysql` driver. The database URL is constructed as `mysql+aiomysql://user:pass@host:port/database`.

Key database integration components:
- **`AgentCRUD`** - Handles agent run and task persistence  
- **`OAuthCrud`** - Manages user authentication tokens
- **`AsyncSession`** - Provides async database session management

Sources: [platform/reworkd_platform/settings.py:122-131](), [platform/pyproject.toml:23-25]()

## External Service Integration

The backend integrates with multiple external services through dedicated API clients and abstractions:

- **OpenAI/Azure OpenAI** - Primary LLM provider via LangChain integration
- **Helicone** - Optional LLM observability and caching layer  
- **Replicate** - Image generation capabilities
- **SERP API** - Web search functionality
- **Pinecone** - Vector database for semantic search (optional)
- **AWS Services** - S3 storage and Secrets Manager via boto3
- **Kafka** - Event streaming for distributed processing (optional)

The service availability is controlled through feature flags and API key presence checks in the settings configuration.

Sources: [platform/reworkd_platform/settings.py:54-171](), [platform/pyproject.toml:19-44]()

---

# Page: Agent API

# Agent API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/package-lock.json](next/package-lock.json)
- [next/package.json](next/package.json)
- [next/public/locales/en/indexPage.json](next/public/locales/en/indexPage.json)
- [next/src/components/Button.tsx](next/src/components/Button.tsx)
- [next/src/components/Input.tsx](next/src/components/Input.tsx)
- [next/src/components/Label.tsx](next/src/components/Label.tsx)
- [next/src/components/Switch.tsx](next/src/components/Switch.tsx)
- [next/src/components/drawer/DrawerItemButton.tsx](next/src/components/drawer/DrawerItemButton.tsx)
- [next/src/server/api/routers/agentRouter.ts](next/src/server/api/routers/agentRouter.ts)
- [next/src/utils/interfaces.ts](next/src/utils/interfaces.ts)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py)
- [platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py)
- [platform/reworkd_platform/web/api/agent/views.py](platform/reworkd_platform/web/api/agent/views.py)

</details>



## Purpose and Scope

The Agent API provides REST endpoints for managing and executing autonomous AI agents. This document covers the Python/FastAPI backend API endpoints, the agent service layer, and the tRPC integration that connects the Next.js frontend to the backend services. 

For information about the agent execution logic and lifecycle, see [Agent Lifecycle](#4.1). For details about the frontend interface components, see [Agent Interface](#2.2).

## API Architecture Overview

The Agent API is built using a layered architecture with FastAPI handling HTTP requests, a service layer abstracting the agent implementation, and dependency injection for service selection.

```mermaid
graph TB
    subgraph "Frontend Layer"
        TRPC_CLIENT["@trpc/client"]
        AGENT_ROUTER["agentRouter.ts"]
    end
    
    subgraph "Backend API Layer"
        API_VIEWS["views.py"]
        VALIDATORS["dependancies.py"]
    end
    
    subgraph "Service Layer"
        AGENT_SERVICE_PROVIDER["agent_service_provider.py"]
        OPENAI_SERVICE["OpenAIAgentService"]
        MOCK_SERVICE["MockAgentService"]
    end
    
    subgraph "External Services"
        OPENAI_API["OpenAI API"]
        DATABASE["MySQL Database"]
    end
    
    TRPC_CLIENT --> AGENT_ROUTER
    AGENT_ROUTER --> API_VIEWS
    API_VIEWS --> VALIDATORS
    VALIDATORS --> AGENT_SERVICE_PROVIDER
    AGENT_SERVICE_PROVIDER --> OPENAI_SERVICE
    AGENT_SERVICE_PROVIDER --> MOCK_SERVICE
    OPENAI_SERVICE --> OPENAI_API
    AGENT_ROUTER --> DATABASE
    
    style API_VIEWS fill:#f9f9f9
    style AGENT_SERVICE_PROVIDER fill:#f9f9f9
    style OPENAI_SERVICE fill:#f9f9f9
```

**Sources:** [platform/reworkd_platform/web/api/agent/views.py:1-146](), [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py:1-54](), [next/src/server/api/routers/agentRouter.ts:1-124]()

## REST API Endpoints

The Agent API exposes six main endpoints through the `/agent` router, each handling different phases of agent execution:

| Endpoint | HTTP Method | Purpose | Response Type |
|----------|-------------|---------|---------------|
| `/start` | POST | Initialize agent with a goal and generate initial tasks | JSON |
| `/analyze` | POST | Analyze a task and determine appropriate tool | JSON |
| `/execute` | POST | Execute a task using the selected tool | Streaming |
| `/create` | POST | Generate new tasks based on execution results | JSON |
| `/summarize` | POST | Summarize completed tasks and results | Streaming |
| `/chat` | POST | Interactive chat with agent context | Streaming |
| `/tools` | GET | Retrieve available tools for the agent | JSON |

### Agent Execution Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant "views.py" as API
    participant "AgentService" as Service
    participant "OpenAI" as LLM
    
    Frontend->>API: "POST /agent/start"
    API->>Service: "start_goal_agent(goal)"
    Service->>LLM: "Generate initial tasks"
    LLM-->>Service: "Task list"
    Service-->>API: "NewTasksResponse"
    API-->>Frontend: "JSON response"
    
    loop "For each task"
        Frontend->>API: "POST /agent/analyze"
        API->>Service: "analyze_task_agent()"
        Service->>LLM: "Analyze task, select tool"
        LLM-->>Service: "Analysis result"
        Service-->>API: "Analysis object"
        API-->>Frontend: "JSON response"
        
        Frontend->>API: "POST /agent/execute"
        API->>Service: "execute_task_agent()"
        Service->>LLM: "Execute using tool"
        LLM-->>Service: "Streaming results"
        Service-->>API: "StreamingResponse"
        API-->>Frontend: "Server-sent events"
        
        Frontend->>API: "POST /agent/create"
        API->>Service: "create_tasks_agent()"
        Service->>LLM: "Generate next tasks"
        LLM-->>Service: "New task list"
        Service-->>API: "NewTasksResponse"
        API-->>Frontend: "JSON response"
    end
```

**Sources:** [platform/reworkd_platform/web/api/agent/views.py:34-84](), [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:60-176]()

## Agent Service Architecture

The service layer uses dependency injection and the strategy pattern to provide different agent implementations based on configuration:

```mermaid
classDiagram
    class AgentService {
        <<Protocol>>
        +start_goal_agent(goal: str) List[str]
        +analyze_task_agent(goal: str, task: str, tool_names: List[str]) Analysis
        +execute_task_agent(goal: str, task: str, analysis: Analysis) StreamingResponse
        +create_tasks_agent(...) List[str]
        +summarize_task_agent(goal: str, results: List[str]) StreamingResponse
        +chat(message: str, results: List[str]) StreamingResponse
    }
    
    class OpenAIAgentService {
        -model: WrappedChatOpenAI
        -settings: ModelSettings
        -token_service: TokenService
        -callbacks: List[AsyncCallbackHandler]
        -user: UserBase
        -oauth_crud: OAuthCrud
        +start_goal_agent(goal: str) List[str]
        +analyze_task_agent(...) Analysis
        +execute_task_agent(...) StreamingResponse
        +create_tasks_agent(...) List[str]
        +summarize_task_agent(...) StreamingResponse
        +chat(...) StreamingResponse
    }
    
    class MockAgentService {
        +start_goal_agent(...) List[str]
        +analyze_task_agent(...) Analysis
        +execute_task_agent(...) StreamingResponse
        +create_tasks_agent(...) List[str]
        +summarize_task_agent(...) StreamingResponse
        +chat(...) StreamingResponse
    }
    
    class get_agent_service {
        +__call__(validator, streaming, llm_model) AgentService
    }
    
    AgentService <|.. OpenAIAgentService
    AgentService <|.. MockAgentService
    get_agent_service --> AgentService : "creates"
```

The service provider function `get_agent_service` determines which implementation to use based on the `settings.ff_mock_mode_enabled` flag and creates the appropriate service with its dependencies.

**Sources:** [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py:1-52](), [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:43-59](), [platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py:13-75](), [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py:22-53]()

## tRPC Integration

The frontend uses tRPC for type-safe API communication, with a separate router handling database operations and the main agent operations delegated to the Python backend:

```mermaid
graph LR
    subgraph "Frontend tRPC Client"
        TRPC_HOOKS["useTRPC hooks"]
        REACT_QUERY["@tanstack/react-query"]
    end
    
    subgraph "Next.js API Routes"
        AGENT_ROUTER["agentRouter.ts"]
        TRPC_SERVER["@trpc/server"]
    end
    
    subgraph "Database Operations"
        PRISMA["Prisma ORM"]
        MYSQL_DB["MySQL Database"]
    end
    
    subgraph "Python Backend"
        FASTAPI_ENDPOINTS["FastAPI /agent/* endpoints"]
        AGENT_SERVICES["Agent Services"]
    end
    
    TRPC_HOOKS --> REACT_QUERY
    REACT_QUERY --> TRPC_SERVER
    TRPC_SERVER --> AGENT_ROUTER
    AGENT_ROUTER --> PRISMA
    AGENT_ROUTER --> FASTAPI_ENDPOINTS
    PRISMA --> MYSQL_DB
    FASTAPI_ENDPOINTS --> AGENT_SERVICES
```

The `agentRouter` handles:
- `create`: Creates new agent records in the database using `generateAgentName()`
- `save`: Persists agent tasks to the database via `AgentTask` entities
- `getAll`: Retrieves user's agent history
- `findById`: Fetches specific agent with tasks
- `deleteById`: Soft-deletes agents

**Sources:** [next/src/server/api/routers/agentRouter.ts:56-124](), [next/package.json:23-26]()

## Request/Response Schemas

The API uses Pydantic models for request validation and response serialization. Key schema interfaces include:

### Core Request Types

```typescript
interface RequestBody {
  run_id?: string;
  model_settings: ApiModelSettings;
  goal: string;
  task?: string;
  tasks?: string[];
  last_task?: string;
  result?: string;
  results?: string[];
  completed_tasks?: string[];
  analysis?: Analysis;
  tool_names?: string[];
  message?: string;
}

interface ApiModelSettings {
  language: string;
  model: GPTModelNames;
  temperature: number;
  max_tokens: number;
}
```

### Response Types

The API returns two main response patterns:
- **Synchronous responses**: JSON objects like `NewTasksResponse` and `Analysis`
- **Streaming responses**: Server-sent events using `FastAPIStreamingResponse` for long-running operations

**Sources:** [next/src/utils/interfaces.ts:25-38](), [next/src/utils/interfaces.ts:6-23](), [platform/reworkd_platform/web/api/agent/views.py:120-128]()

## Authentication and Dependencies

The Agent API integrates with the application's authentication system through dependency injection:

### Dependency Chain

```mermaid
graph TD
    REQUEST["HTTP Request"] --> VALIDATOR["agent_*_validator"]
    VALIDATOR --> AGENT_SERVICE_PROVIDER["get_agent_service()"]
    AGENT_SERVICE_PROVIDER --> GET_CURRENT_USER["get_current_user()"]
    AGENT_SERVICE_PROVIDER --> GET_TOKEN_SERVICE["get_token_service()"]
    AGENT_SERVICE_PROVIDER --> OAUTH_CRUD["OAuthCrud.inject()"]
    
    GET_CURRENT_USER --> USER_BASE["UserBase"]
    GET_TOKEN_SERVICE --> TOKEN_SERVICE["TokenService"]
    OAUTH_CRUD --> OAUTH_CRUD_INSTANCE["OAuthCrud"]
    
    USER_BASE --> OPENAI_AGENT_SERVICE["OpenAIAgentService"]
    TOKEN_SERVICE --> OPENAI_AGENT_SERVICE
    OAUTH_CRUD_INSTANCE --> OPENAI_AGENT_SERVICE
```

Each endpoint uses FastAPI's dependency injection to validate requests, authenticate users, and provide the appropriate agent service implementation. The validation functions (`agent_start_validator`, `agent_analyze_validator`, etc.) ensure request schemas are correct before processing.

**Sources:** [platform/reworkd_platform/web/api/agent/views.py:37-39](), [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py:27-32](), [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:44-58]()

---

# Page: Agent Service

# Agent Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/src/utils/interfaces.ts](next/src/utils/interfaces.ts)
- [platform/reworkd_platform/services/tokenizer/token_service.py](platform/reworkd_platform/services/tokenizer/token_service.py)
- [platform/reworkd_platform/tests/agent/test_analysis.py](platform/reworkd_platform/tests/agent/test_analysis.py)
- [platform/reworkd_platform/tests/agent/test_crud.py](platform/reworkd_platform/tests/agent/test_crud.py)
- [platform/reworkd_platform/tests/agent/test_task_output_parser.py](platform/reworkd_platform/tests/agent/test_task_output_parser.py)
- [platform/reworkd_platform/tests/agent/test_tools.py](platform/reworkd_platform/tests/agent/test_tools.py)
- [platform/reworkd_platform/tests/test_settings.py](platform/reworkd_platform/tests/test_settings.py)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py)
- [platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py)
- [platform/reworkd_platform/web/api/agent/model_factory.py](platform/reworkd_platform/web/api/agent/model_factory.py)
- [platform/reworkd_platform/web/api/agent/views.py](platform/reworkd_platform/web/api/agent/views.py)

</details>



The Agent Service is a core component of the AgentGPT backend that orchestrates interactions between API endpoints and language models (LLMs) to enable autonomous agent operation. It provides the implementation for task generation, analysis, execution, and conversation capabilities that power the autonomous agent functionality.

For information about the API endpoints that call this service, see [Agent API](#3.1). For details about the tools that agents can use, see [Agent Tools](#3.3).

## Agent Service Interface

The Agent Service defines a protocol that all implementations must follow, providing a consistent interface for agent operations.

```mermaid
classDiagram
    class AgentService {
        <<Protocol>>
        +start_goal_agent(goal: str) -> List[str]
        +analyze_task_agent(goal: str, task: str, tool_names: List[str]) -> Analysis
        +execute_task_agent(goal: str, task: str, analysis: Analysis) -> FastAPIStreamingResponse
        +create_tasks_agent(goal: str, tasks: List[str], last_task: str, result: str, completed_tasks: List[str]) -> List[str]
        +summarize_task_agent(goal: str, results: List[str]) -> FastAPIStreamingResponse
        +chat(message: str, results: List[str]) -> FastAPIStreamingResponse
    }
```

Sources: [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py]()

## Service Implementations

The system provides two implementations of the Agent Service interface:

1. **OpenAIAgentService**: Primary implementation that uses OpenAI's language models
2. **MockAgentService**: Test implementation that returns mock responses for development/testing

### OpenAI Agent Service

The `OpenAIAgentService` class implements the core agent functionality using OpenAI's language models. It manages token usage, handles prompt construction, and coordinates with various agent tools.

```mermaid
classDiagram
    class OpenAIAgentService {
        -model: WrappedChatOpenAI
        -settings: ModelSettings
        -token_service: TokenService
        -callbacks: Optional[List[AsyncCallbackHandler]]
        -user: UserBase
        -oauth_crud: OAuthCrud
        +start_goal_agent(goal: str) -> List[str]
        +analyze_task_agent(goal: str, task: str, tool_names: List[str]) -> Analysis
        +execute_task_agent(goal: str, task: str, analysis: Analysis) -> StreamingResponse
        +create_tasks_agent(goal: str, tasks: List[str], last_task: str, result: str, completed_tasks: Optional[List[str]]) -> List[str]
        +summarize_task_agent(goal: str, results: List[str]) -> FastAPIStreamingResponse
        +chat(message: str, results: List[str]) -> FastAPIStreamingResponse
    }
```

Key dependencies:
- `model`: A `WrappedChatOpenAI` instance created by the model factory
- `settings`: `ModelSettings` containing language, temperature, and token limits
- `token_service`: `TokenService` for calculating and managing token usage
- `callbacks`: Optional list of `AsyncCallbackHandler` for model interactions
- `user`: `UserBase` containing current user information
- `oauth_crud`: `OAuthCrud` service for OAuth operations with external tools

Sources: [platform/reworkd_platform/web/api/agent/agent_service/open_i_agent_service.py:43-58]()

### Mock Agent Service

The `MockAgentService` provides a testing implementation that returns predefined responses without calling external APIs.

Sources: [platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py]()

## Agent Service Provider

The Agent Service Provider is a factory function that determines which Agent Service implementation to create based on configuration and dependencies.

```mermaid
graph TD
    views["views.py API Endpoints"] --> get_agent_service["get_agent_service() Factory"]
    get_agent_service --> |"If settings.ff_mock_mode_enabled"| MockAgentService["MockAgentService"]
    get_agent_service --> |"Otherwise"| OpenAIAgentService["OpenAIAgentService"]
    
    get_agent_service --> AgentRun["AgentRun (from validator)"]
    get_agent_service --> UserBase["UserBase (from get_current_user)"]
    get_agent_service --> TokenService["TokenService (from get_token_service)"]
    get_agent_service --> OAuthCrud["OAuthCrud (from OAuthCrud.inject)"]
    
    OpenAIAgentService --> create_model["create_model() Factory"]
    create_model --> |"Azure configuration"| WrappedAzureChatOpenAI["WrappedAzureChatOpenAI"]
    create_model --> |"Standard configuration"| WrappedChatOpenAI["WrappedChatOpenAI"]
    
    OpenAIAgentService --> get_tool_from_name["get_tool_from_name() Tool Selector"]
```

The `get_agent_service` function creates an Agent Service instance with the appropriate dependencies:
- Language model (created by the Model Factory)
- Token service for managing token usage
- User information and OAuth credentials

Sources: [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py]()

## API Integration and Method Mapping

The Agent Service methods are mapped to API endpoints in the views module:

```mermaid
graph TD
    start_tasks["POST /agent/start"] --> start_goal_agent["start_goal_agent()"]
    analyze_tasks["POST /agent/analyze"] --> analyze_task_agent["analyze_task_agent()"]
    execute_tasks["POST /agent/execute"] --> execute_task_agent["execute_task_agent()"]
    create_tasks["POST /agent/create"] --> create_tasks_agent["create_tasks_agent()"]
    summarize["POST /agent/summarize"] --> summarize_task_agent["summarize_task_agent()"]
    chat["POST /agent/chat"] --> chat_method["chat()"]
    
    subgraph "API Endpoints (views.py)"
        start_tasks
        analyze_tasks
        execute_tasks
        create_tasks
        summarize
        chat
    end
    
    subgraph "Agent Service Methods"
        start_goal_agent
        analyze_task_agent
        execute_task_agent
        create_tasks_agent
        summarize_task_agent
        chat_method
    end
```

Sources: [platform/reworkd_platform/web/api/agent/views.py]()

## Model Factory

The Agent Service relies on the Model Factory to create language model instances:

```mermaid
graph TD
    create_model["create_model()"] --> model_type["Determine Model Type"]
    model_type --> |"Azure OpenAI"| WrappedAzureChatOpenAI["WrappedAzureChatOpenAI"]
    model_type --> |"Standard OpenAI"| WrappedChatOpenAI["WrappedChatOpenAI"]
    
    create_model --> base_and_headers["get_base_and_headers()"]
    base_and_headers --> |"Helicone enabled"| helicone_config["Configure Helicone Headers"]
    base_and_headers --> |"Custom API key"| custom_api["Use custom API base"]
    base_and_headers --> |"Default"| default_api["Use settings.openai_api_base"]
    
    create_model --> configs["Apply Configurations"]
    configs --> model_name["model: LLM_Model"]
    configs --> temperature["temperature: float"]
    configs --> max_tokens["max_tokens: int"]
    configs --> streaming["streaming: bool"]
```

The Model Factory:
- Creates wrapped instances of ChatOpenAI or AzureChatOpenAI
- Configures API endpoints and authentication
- Sets model parameters based on user settings
- Handles Helicone integration for API monitoring

Sources: [platform/reworkd_platform/web/api/agent/model_factory.py]()

## Agent Service Operations

### Agent Lifecycle Workflow

The following sequence diagram shows how the Agent Service manages the agent lifecycle:

```mermaid
sequenceDiagram
    participant Client
    participant ApiEndpoints as "API Endpoints (views.py)"
    participant AgentService as "OpenAIAgentService"
    participant LLM as "Language Model"
    participant Tools as "Agent Tools"
    
    Client->>ApiEndpoints: POST /agent/start (goal)
    ApiEndpoints->>AgentService: start_goal_agent(goal)
    AgentService->>LLM: Prompt with start_goal_prompt
    Note over AgentService,LLM: Token calculation occurs here
    LLM-->>AgentService: Completion with task list
    AgentService->>AgentService: Parse with TaskOutputParser
    AgentService-->>ApiEndpoints: Return task list
    ApiEndpoints-->>Client: NewTasksResponse
    
    Client->>ApiEndpoints: POST /agent/analyze (goal, task, tool_names)
    ApiEndpoints->>AgentService: analyze_task_agent(goal, task, tool_names)
    AgentService->>AgentService: get_user_tools()
    AgentService->>LLM: Prompt with analyze_task_prompt + functions
    LLM-->>AgentService: Function call with arguments
    AgentService->>AgentService: Parse into Analysis object
    AgentService-->>ApiEndpoints: Return Analysis
    ApiEndpoints-->>Client: Analysis response
    
    Client->>ApiEndpoints: POST /agent/execute (goal, task, analysis)
    ApiEndpoints->>AgentService: execute_task_agent(goal, task, analysis)
    AgentService->>AgentService: get_tool_from_name(analysis.action)
    AgentService->>Tools: tool.call(goal, task, analysis.arg, user, oauth_crud)
    Tools-->>AgentService: StreamingResponse
    AgentService-->>ApiEndpoints: StreamingResponse
    ApiEndpoints-->>Client: Stream execution results
    
    Client->>ApiEndpoints: POST /agent/create (goal, tasks, last_task, result)
    ApiEndpoints->>AgentService: create_tasks_agent(goal, tasks, last_task, result)
    AgentService->>LLM: Prompt with create_tasks_prompt
    LLM-->>AgentService: Completion with new task
    AgentService->>AgentService: Filter out existing tasks
    AgentService-->>ApiEndpoints: Return new tasks
    ApiEndpoints-->>Client: NewTasksResponse
```

Sources:
- [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py]()
- [platform/reworkd_platform/web/api/agent/views.py]()

### Method Details

#### 1. Start Goal Agent

The `start_goal_agent` method generates initial tasks based on a user's goal:

```python
async def start_goal_agent(self, *, goal: str) -> List[str]:
    # Create prompt from goal and language
    # Calculate max tokens for response
    # Call model with the prompt
    # Parse output into a list of tasks
```

Key implementation details:
- Creates `ChatPromptTemplate` from `SystemMessagePromptTemplate` with `start_goal_prompt`
- Formats prompt with goal and `self.settings.language`
- Calculates token limits via `self.token_service.calculate_max_tokens`
- Calls model with error handling via `call_model_with_handling`
- Parses response using `TaskOutputParser` with empty `completed_tasks` list

Sources: [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:60-86]()

#### 2. Analyze Task Agent

The `analyze_task_agent` method determines which tool to use for a given task:

```python
async def analyze_task_agent(self, *, goal: str, task: str, tool_names: List[str]) -> Analysis:
    # Get available tools based on tool_names
    # Create functions for each tool
    # Prompt the model with goal, task, and functions
    # Parse the function call and arguments into an Analysis object
```

Key implementation details:
- Retrieves user-accessible tools via `get_user_tools(tool_names, self.user, self.oauth_crud)`
- Maps tools to OpenAI function definitions with `get_tool_function`
- Formats `analyze_task_prompt` with goal, task, and `self.settings.language`
- Calculates tokens including function definitions in `str(functions)`
- Handles OpenAI errors via `openai_error_handler` with functions parameter
- Extracts function call from `message.additional_kwargs.get("function_call", {})`
- Parses arguments using `PydanticOutputParser(pydantic_object=AnalysisArguments)`
- Falls back to `Analysis.get_default_analysis(task)` on validation errors

Sources: [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:88-124]()

#### 3. Execute Task Agent

The `execute_task_agent` method executes a task using the selected tool:

```python
async def execute_task_agent(self, *, goal: str, task: str, analysis: Analysis) -> StreamingResponse:
    # Adjust token limit for the response
    # Get tool class based on analysis.action
    # Call the tool with goal, task, and analysis.arg
    # Return streaming response
```

Key implementation details:
- Reduces `self.model.max_tokens` by 1000 if > 3000 (minimum 3000) to leave completion room
- Gets tool class via `get_tool_from_name(analysis.action)`
- Instantiates tool with `tool_class(self.model, self.settings.language)`
- Calls tool's `call` method with `(goal, task, analysis.arg, self.user, self.oauth_crud)`
- Returns `StreamingResponse` directly from tool execution

Sources: [platform/reworkd_platform/web/api/agent/agent_service/open_i_agent_service.py:126-144]()

#### 4. Create Tasks Agent

The `create_tasks_agent` method generates new tasks based on previous task results:

```python
async def create_tasks_agent(self, *, goal: str, tasks: List[str], 
                             last_task: str, result: str, 
                             completed_tasks: Optional[List[str]] = None) -> List[str]:
    # Create prompt with goal, tasks, last_task, result
    # Calculate max tokens for response
    # Call model with prompt
    # Filter out duplicate tasks
    # Return list of new tasks
```

Key implementation details:
- Creates `ChatPromptTemplate` from `SystemMessagePromptTemplate` with `create_tasks_prompt`
- Formats prompt with goal, language, tasks (joined with `\n`), last_task, and result
- Calculates token limits via `self.token_service.calculate_max_tokens`
- Calls model with error handling via `call_model_with_handling`
- Combines `completed_tasks` and current `tasks` into `previous_tasks`
- Returns `[completion]` if completion not in `previous_tasks`, else empty list

Sources: [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:146-176]()

#### 5. Summarize Task Agent

The `summarize_task_agent` method generates a summary of all task results:

```python
async def summarize_task_agent(self, *, goal: str, results: List[str]) -> FastAPIStreamingResponse:
    # Use a high-capacity model
    # Limit tokens for summary
    # Tokenize and truncate results if necessary
    # Use summarize utility to generate summary
```

Key implementation details:
- Overrides `self.model.model_name = "gpt-3.5-turbo-16k"`
- Sets `self.model.max_tokens = 8000` for total tokens (prompt + completion)
- Limits input to `snippet_max_tokens = 7000` tokens to leave room for prompt overhead
- Tokenizes results with `self.token_service.tokenize("".join(results))`
- Truncates tokens with `text_tokens[0:snippet_max_tokens]` and detokenizes
- Calls `summarize(model=self.model, language=self.settings.language, goal=goal, text=text)`

Sources: [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:178-197]()

#### 6. Chat

The `chat` method enables conversational interaction with the agent:

```python
async def chat(self, *, message: str, results: List[str]) -> FastAPIStreamingResponse:
    # Use a high-capacity model
    # Create prompt with system message, previous results, and user message
    # Calculate max tokens for response
    # Create LLMChain for the conversation
    # Return streaming response
```

Key implementation details:
- Overrides `self.model.model_name = "gpt-3.5-turbo-16k"`
- Creates `ChatPromptTemplate` with `SystemMessagePromptTemplate(prompt=chat_prompt)`
- Adds each result as `HumanMessage(content=result)` to message list
- Appends user message as final `HumanMessage(content=message)`
- Calculates token limits via `self.token_service.calculate_max_tokens`
- Creates `LLMChain(llm=self.model, prompt=prompt)`
- Returns `StreamingResponse.from_chain` with `{"language": self.settings.language}`

Sources: [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:199-227]()

## Error Handling

The Agent Service uses utility functions to handle errors during model interactions:

```mermaid
graph TD
    call_model_with_handling["call_model_with_handling()"] --> openai_error_handler["openai_error_handler()"]
    openai_error_handler --> |"ServiceUnavailableError"| service_error["Return OpenAI service status message"]
    openai_error_handler --> |"InvalidRequestError"| request_error["Return model access or format error"]
    openai_error_handler --> |"AuthenticationError"| auth_error["Return API key error"]
    openai_error_handler --> |"RateLimitError"| rate_limit["Return quota information"]
    
    parse_with_handling["parse_with_handling()"] --> |"OutputParserException"| parser_error["Return parsing error message"]
```

These utility functions:
- `call_model_with_handling`: Wraps model calls with `openai_error_handler`
- `openai_error_handler`: Catches specific OpenAI exceptions and converts to `OpenAIError`
- `parse_with_handling`: Handles `OutputParserException` during response parsing
- Control logging based on whether `model_settings.custom_api_key` is used

Sources: [platform/reworkd_platform/web/api/agent/helpers.py]()

## Integration with Tools

The Agent Service interacts with various tools to execute tasks:

```mermaid
graph TD
    OpenAIAgentService["OpenAIAgentService"] --> |"analyze_task_agent()"| Analysis["Analysis Object"]
    Analysis --> |"action field"| ToolName["Tool Name (e.g., search, reason, image)"]
    
    OpenAIAgentService --> |"execute_task_agent()"| get_tool_from_name["get_tool_from_name(analysis.action)"]
    get_tool_from_name --> Tool["Tool Instance (e.g., Search, Reason, Image)"]
    Tool --> |"call(goal, task, arg, user, oauth_crud)"| StreamingResponse["StreamingResponse"]
    
    OpenAIAgentService --> |"get_user_tools()"| AvailableTools["User-accessible Tools"]
    AvailableTools --> |"get_tool_function()"| FunctionDefinitions["OpenAI Function Definitions"]
```

The `analyze_task_agent` method determines which tool to use, and the `execute_task_agent` method instantiates and calls the selected tool with the appropriate arguments.

Sources:
- [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py]()
- [platform/reworkd_platform/web/api/agent/tools/tools.py]()

## Token Management

The Agent Service uses the `TokenService` to manage token usage:

```python
# Calculate maximum tokens for a response
self.token_service.calculate_max_tokens(
    self.model,
    prompt.format_prompt(**args).to_string()
)
```

The Token Service:
- Counts tokens in prompt text
- Calculates available completion tokens based on model limits
- Adjusts the model's `max_tokens` parameter to stay within limits
- Handles token truncation when necessary

Sources: [platform/reworkd_platform/services/tokenizer/token_service.py]()

## Summary

The Agent Service is a critical component of the AgentGPT architecture that:

1. Defines a consistent interface for agent operations
2. Provides implementations using OpenAI models
3. Manages the entire agent lifecycle from goal setting to task execution
4. Handles error scenarios and token limitations
5. Integrates with various tools for task execution
6. Enables streaming responses for real-time feedback

Understanding this component is essential for extending the agent's capabilities or modifying its behavior within the system.

---

# Page: Agent Tools

# Agent Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [platform/reworkd_platform/web/api/agent/prompts.py](platform/reworkd_platform/web/api/agent/prompts.py)
- [platform/reworkd_platform/web/api/agent/tools/code.py](platform/reworkd_platform/web/api/agent/tools/code.py)
- [platform/reworkd_platform/web/api/agent/tools/conclude.py](platform/reworkd_platform/web/api/agent/tools/conclude.py)
- [platform/reworkd_platform/web/api/agent/tools/image.py](platform/reworkd_platform/web/api/agent/tools/image.py)
- [platform/reworkd_platform/web/api/agent/tools/reason.py](platform/reworkd_platform/web/api/agent/tools/reason.py)
- [platform/reworkd_platform/web/api/agent/tools/search.py](platform/reworkd_platform/web/api/agent/tools/search.py)
- [platform/reworkd_platform/web/api/agent/tools/tool.py](platform/reworkd_platform/web/api/agent/tools/tool.py)
- [platform/reworkd_platform/web/api/agent/tools/tools.py](platform/reworkd_platform/web/api/agent/tools/tools.py)
- [platform/reworkd_platform/web/api/agent/tools/utils.py](platform/reworkd_platform/web/api/agent/tools/utils.py)
- [platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py](platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py)

</details>



This document covers the modular tool system that enables AgentGPT agents to perform various tasks including web search, code generation, image creation, and reasoning. The tool system provides a pluggable architecture where agents can dynamically select and execute appropriate tools based on their current objectives.

For information about how agents orchestrate tool usage during task execution, see [Task Execution](#4.2). For details about the prompt templates that guide tool selection, see [Prompts and Output Parsing](#4.3).

## Tool Architecture Overview

The agent tool system is built around an abstract `Tool` base class that defines a common interface for all agent capabilities. Each tool is responsible for a specific type of task and can integrate with external APIs or perform local computations.

### Tool Class Hierarchy

```mermaid
classDiagram
    class Tool {
        <<abstract>>
        +description: str
        +public_description: str
        +arg_description: str
        +image_url: str
        +model: BaseChatModel
        +language: str
        +__init__(model, language)
        +available()$ bool
        +dynamic_available(user, oauth_crud)$ bool
        +call(goal, task, input_str, user, oauth_crud)* StreamingResponse
    }
    
    class Search {
        +description: str
        +call() StreamingResponse
        -_google_serper_search_results()
        -_call()
    }
    
    class Code {
        +description: str
        +call() StreamingResponse
    }
    
    class Image {
        +description: str
        +call() StreamingResponse
        +get_replicate_image()
        +get_open_ai_image()
    }
    
    class Reason {
        +description: str
        +call() StreamingResponse
    }
    
    class Conclude {
        +description: str
        +call() StreamingResponse
    }
    
    class Wikipedia {
        +description: str
        +call() StreamingResponse
    }
    
    Tool <|-- Search
    Tool <|-- Code
    Tool <|-- Image
    Tool <|-- Reason
    Tool <|-- Conclude
    Tool <|-- Wikipedia
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tool.py:11-42](), [platform/reworkd_platform/web/api/agent/tools/search.py:42-110](), [platform/reworkd_platform/web/api/agent/tools/code.py:10-26](), [platform/reworkd_platform/web/api/agent/tools/image.py:47-67](), [platform/reworkd_platform/web/api/agent/tools/reason.py:10-28](), [platform/reworkd_platform/web/api/agent/tools/conclude.py:9-16](), [platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py:10-31]()

## Available Tool Types

The system provides several specialized tools, categorized as default tools (always available) and external tools (conditionally available based on API keys and user permissions).

| Tool Class | Type | Description | External API | Availability Method |
|------------|------|-------------|--------------|-------------------|
| `Search` | Default | Search Google for current information and facts | Serper API | `settings.serp_api_key` |
| `Code` | External | Write, refactor, and explain code | OpenAI API | Always available |
| `Image` | External | Generate AI images from text prompts | Replicate API + OpenAI DALL-E | API key dependent |
| `Reason` | Internal | Perform reasoning tasks using LLM | OpenAI API | Always available |
| `Conclude` | Internal | Mark task completion | None | Always available |
| `Wikipedia` | External | Search Wikipedia for historical information | Wikipedia API | Currently disabled |

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tools.py:27-39](), [platform/reworkd_platform/web/api/agent/tools/search.py:42-54](), [platform/reworkd_platform/web/api/agent/tools/image.py:47-49](), [platform/reworkd_platform/web/api/agent/tools/code.py:10-12]()

## Tool Execution Flow

The following diagram shows how agents select and execute tools during task processing:

```mermaid
sequenceDiagram
    participant Agent as "OpenAIAgentService"
    participant ToolMgr as "get_user_tools()"
    participant AnalyzePrompt as "analyze_task_prompt"
    participant LLM as "BaseChatModel"
    participant ToolImpl as "Tool Implementation"
    participant ExtAPI as "External API"
    
    Agent->>ToolMgr: "get_user_tools(tool_names, user, crud)"
    ToolMgr->>ToolMgr: "Filter available tools"
    ToolMgr-->>Agent: "List[Type[Tool]]"
    
    Agent->>AnalyzePrompt: "Format with goal, task, language"
    AnalyzePrompt-->>Agent: "Formatted prompt"
    
    Agent->>LLM: "Send prompt with tool options"
    LLM-->>Agent: "Selected tool + arguments"
    
    Agent->>ToolImpl: "call(goal, task, input_str, user, crud)"
    
    alt "Tool uses external API"
        ToolImpl->>ExtAPI: "API request"
        ExtAPI-->>ToolImpl: "API response"
    else "Tool uses LLM directly"
        ToolImpl->>LLM: "Tool-specific prompt"
        LLM-->>ToolImpl: "Generated content"
    end
    
    ToolImpl-->>Agent: "StreamingResponse"
    Agent->>Agent: "Process tool output"
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tools.py:12-16](), [platform/reworkd_platform/web/api/agent/prompts.py:24-36](), [platform/reworkd_platform/web/api/agent/tools/tool.py:32-41]()

## Tool Management System

The tool management system handles tool discovery, availability checking, and instantiation. Key functions in the `tools.py` module orchestrate tool operations:

### Tool Discovery Functions

```mermaid
flowchart TD
    GetUserTools["get_user_tools(tool_names, user, crud)"] --> MapTools["map(get_tool_from_name, tool_names)"]
    MapTools --> GetDefault["get_default_tools()"]
    GetDefault --> FilterAvailable["filter by dynamic_available()"]
    FilterAvailable --> UserToolList["List[Type[Tool]]"]
    
    GetAvailable["get_available_tools()"] --> GetExternal["get_external_tools()"]
    GetExternal --> DefaultTools["get_default_tools()"]
    DefaultTools --> AllToolsList["List[Type[Tool]]"]
    
    GetExternal --> ExternalList["[Image, Code, SID]"]
    DefaultTools --> DefaultList["[Search]"]
    
    GetToolFromName["get_tool_from_name(tool_name)"] --> FormatName["format_tool_name()"]
    FormatName --> FindMatch["Find matching tool"]
    FindMatch --> ReturnTool["Return tool class"]
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tools.py:12-79]()

### Tool Availability Checking

Tools implement two availability mechanisms:

1. **Static Availability** (`available()` method): Checks if required API keys and configuration are present
2. **Dynamic Availability** (`dynamic_available()` method): Performs user-specific and runtime checks

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tool.py:24-30](), [platform/reworkd_platform/web/api/agent/tools/search.py:51-53]()

## Integration with Language Models and Prompts

Tools integrate closely with the prompt system and language models to generate contextual responses:

### Tool-Specific Prompt Usage

```mermaid
flowchart LR
    subgraph "Prompt Templates"
        AnalyzeTask["analyze_task_prompt"]
        CodePrompt["code_prompt"]
        ExecuteTask["execute_task_prompt"]
        SummarizeWithSources["summarize_with_sources_prompt"]
        SummarizeSid["summarize_sid_prompt"]
    end
    
    subgraph "Tool Implementations"
        SearchTool["Search.call()"]
        CodeTool["Code.call()"]
        ReasonTool["Reason.call()"]
        ImageTool["Image.call()"]
    end
    
    subgraph "Utility Functions"
        SummarizeUtil["summarize_with_sources()"]
        SummarizeSidUtil["summarize_sid()"]
    end
    
    AnalyzeTask --> SearchTool
    CodePrompt --> CodeTool
    ExecuteTask --> ReasonTool
    
    SearchTool --> SummarizeUtil
    SummarizeUtil --> SummarizeWithSources
    
    SummarizeSidUtil --> SummarizeSid
```

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:24-36](), [platform/reworkd_platform/web/api/agent/prompts.py:38-56](), [platform/reworkd_platform/web/api/agent/prompts.py:58-67](), [platform/reworkd_platform/web/api/agent/tools/utils.py:55-76](), [platform/reworkd_platform/web/api/agent/tools/utils.py:78-98]()

### LLMChain Integration

Most tools utilize `LLMChain` from LangChain to process prompts and stream responses:

```python
# Common pattern in tool implementations
chain = LLMChain(llm=self.model, prompt=specific_prompt)
return StreamingResponse.from_chain(
    chain,
    {"goal": goal, "language": self.language, "task": task},
    media_type="text/event-stream",
)
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/code.py:19-25](), [platform/reworkd_platform/web/api/agent/tools/reason.py:21-27]()

## External Service Integration

The tool system integrates with multiple external APIs to extend agent capabilities:

### API Integration Architecture

```mermaid
flowchart TD
    subgraph "Tool Layer"
        SearchTool["Search Tool"]
        ImageTool["Image Tool"]
        CodeTool["Code Tool"]
    end
    
    subgraph "External APIs"
        SerperAPI["google.serper.dev"]
        ReplicateAPI["replicate.com"]
        OpenAIAPI["api.openai.com"]
        WikiAPI["Wikipedia API"]
    end
    
    subgraph "API Functions"
        GoogleSearch["_google_serper_search_results()"]
        ReplicateImg["get_replicate_image()"]
        OpenAIImg["get_open_ai_image()"]
    end
    
    subgraph "Settings & Auth"
        Settings["settings.serp_api_key"]
        ReplicateKey["settings.replicate_api_key"]
        OpenAIKey["settings.openai_api_key"]
    end
    
    SearchTool --> GoogleSearch
    GoogleSearch --> SerperAPI
    Settings --> GoogleSearch
    
    ImageTool --> ReplicateImg
    ImageTool --> OpenAIImg
    ReplicateImg --> ReplicateAPI
    OpenAIImg --> OpenAIAPI
    ReplicateKey --> ReplicateImg
    OpenAIKey --> OpenAIImg
    
    CodeTool --> OpenAIAPI
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/search.py:22-39](), [platform/reworkd_platform/web/api/agent/tools/image.py:15-44](), [platform/reworkd_platform/settings.py]()

### Error Handling and Fallbacks

Tools implement robust error handling with fallback mechanisms. For example, the `Search` tool falls back to `Reason` tool when the Serper API fails:

```python
async def call(self, goal: str, task: str, input_str: str, *args, **kwargs):
    try:
        return await self._call(goal, task, input_str, *args, **kwargs)
    except ClientResponseError:
        logger.exception("Error calling Serper API, falling back to reasoning")
        return await Reason(self.model, self.language).call(
            goal, task, input_str, *args, **kwargs
        )
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/search.py:55-64]()

---

# Page: Storage and Database

# Storage and Database

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/prisma/schema.prisma](next/prisma/schema.prisma)
- [platform/poetry.lock](platform/poetry.lock)
- [platform/pyproject.toml](platform/pyproject.toml)
- [platform/reworkd_platform/settings.py](platform/reworkd_platform/settings.py)
- [platform/reworkd_platform/web/api/agent/dependancies.py](platform/reworkd_platform/web/api/agent/dependancies.py)

</details>



This page documents the database schemas, Prisma ORM integration, and data persistence layers used throughout the AgentGPT system. The system employs a dual-ORM architecture with Prisma for the Next.js frontend and SQLAlchemy for the FastAPI backend, both connecting to a shared MySQL database.

For information about Agent API and service implementation, see [Agent API](3.1) and [Agent Service](3.2).

## Database Architecture Overview

AgentGPT uses a dual-ORM approach to handle database operations across the full-stack application:

1. **Frontend (Next.js)**: Uses Prisma Client for database operations and schema management
2. **Backend (FastAPI)**: Uses SQLAlchemy with async MySQL driver for database operations  
3. **Shared Database**: MySQL database with consistent schema across both access layers

### Dual-ORM Architecture Diagram

```mermaid
flowchart TB
    subgraph "Frontend Layer"
        NextJS["Next.js Application"]
        PrismaClient["Prisma Client"]
        PrismaSchema["schema.prisma"]
    end
    
    subgraph "Backend Layer"  
        FastAPI["FastAPI Application"]
        SQLAlchemy["SQLAlchemy ORM"]
        AgentCRUD["AgentCRUD"]
        AsyncSession["AsyncSession"]
    end
    
    subgraph "Database Layer"
        MySQL[("MySQL Database")]
    end
    
    NextJS --> PrismaClient
    PrismaClient --> PrismaSchema
    PrismaClient -->|"Database connection"| MySQL
    
    FastAPI --> SQLAlchemy  
    SQLAlchemy --> AgentCRUD
    AgentCRUD --> AsyncSession
    SQLAlchemy -->|"aiomysql driver"| MySQL
    
    PrismaSchema -.->|"Schema definition"| MySQL
```

Sources: [next/prisma/schema.prisma](), [platform/reworkd_platform/settings.py:71-79](), [platform/reworkd_platform/web/api/agent/dependancies.py:26-30]()

## Database Schema

The database schema is defined in `schema.prisma` and encompasses several key domains for the agent platform:

1. **Authentication System**: NextAuth.js models for user authentication and sessions
2. **Agent Execution System**: Models for agent definitions, tasks, and execution runs
3. **Organization Management**: Multi-tenant organization and user role models
4. **OAuth Integration**: Secure storage for OAuth provider credentials

### Core Entity Relationships

```mermaid
erDiagram
    User ||--o{ Account : "has"
    User ||--o{ Session : "has"  
    User ||--o{ Agent : "creates"
    User ||--o{ Run : "executes"
    User ||--o{ NewRun : "executes"
    User ||--o{ OrganizationUser : "belongs_to"
    
    Agent ||--o{ AgentTask : "contains"
    NewRun ||--o{ Task : "contains"
    
    Organization ||--o{ OrganizationUser : "has_members"
    
    User {
        string id PK
        string name
        string email UK
        datetime emailVerified
        string image
        boolean superAdmin
        datetime createDate
    }
    
    Agent {
        string id PK
        string userId FK
        string name
        string goal
        datetime createDate
        datetime deleteDate
    }
    
    AgentTask {
        string id PK
        string agentId FK
        string type
        string status
        string value
        string info
        int sort
        datetime createDate
        datetime deleteDate
    }
    
    NewRun {
        string id PK
        string user_id FK
        datetime create_date
        string goal
    }
    
    Task {
        string id PK
        string run_id FK
        string type
        datetime create_date
    }
```

Sources: [next/prisma/schema.prisma:41-191]()

## Database Models

## Database Models

### Authentication Models (NextAuth.js Integration)

The system integrates with NextAuth.js using standard authentication models:

| Model | Purpose | Key Fields | Indices |
|-------|---------|------------|---------|
| `User` | Core user entity | `id`, `email`, `name`, `superAdmin`, `createDate` | `email`, `createDate` |
| `Account` | OAuth provider accounts | `provider`, `providerAccountId`, `userId` | `userId` |
| `Session` | Active user sessions | `sessionToken`, `userId`, `expires` | `userId` |
| `VerificationToken` | Email verification tokens | `identifier`, `token`, `expires` | `identifier + token` |

Sources: [next/prisma/schema.prisma:12-100]()

### Agent Execution Models

The core agent system uses both legacy and new implementations for tracking agent runs:

#### Legacy Agent Models
| Model | Purpose | Key Fields | Indices |
|-------|---------|------------|---------|
| `Agent` | Agent definition | `userId`, `name`, `goal`, `createDate`, `deleteDate` | `createDate`, `userId + deleteDate + createDate` |
| `AgentTask` | Agent task execution | `agentId`, `type`, `status`, `value`, `info`, `sort` | `agentId`, `type`, `createDate` |
| `Run` | Basic run tracking | `userId`, `createDate` | `userId + createDate`, `userId` |

#### New Agent Models  
| Model | Purpose | Key Fields | Indices |
|-------|---------|------------|---------|
| `NewRun` (mapped to `agent_run`) | Enhanced run tracking | `user_id`, `goal`, `create_date` | `user_id + create_date`, `user_id` |
| `Task` (mapped to `agent_task`) | Enhanced task tracking | `run_id`, `type`, `create_date` | `run_id` |

Sources: [next/prisma/schema.prisma:126-191]()

### Organization Management Models

Multi-tenant organization support with role-based access:

| Model | Purpose | Key Fields | Indices |
|-------|---------|------------|---------|
| `Organization` | Organization entity | `name`, `created_by`, `create_date` | `name` |
| `OrganizationUser` | User-organization relationships | `user_id`, `organization_id`, `role` | `user_id`, `organization_id`, `user_id + organization_id` |

Sources: [next/prisma/schema.prisma:61-92]()

### OAuth Integration Model

Secure storage for OAuth provider credentials with encryption:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | String | Primary key |
| `user_id` | String | Associated user |
| `organization_id` | String? | Optional organization scope |
| `provider` | String | OAuth provider name |
| `state` | String | OAuth state parameter |
| `redirect_uri` | String | OAuth callback URI |
| `access_token_enc` | String? | Encrypted access token |
| `refresh_token_enc` | String? | Encrypted refresh token |
| `scope` | String? | OAuth scope permissions |

Sources: [next/prisma/schema.prisma:102-124]()

## Database Connectivity

The system uses different connection strategies for frontend and backend database access, both connecting to the same MySQL database.

### Database Connection Architecture

```mermaid
flowchart TB
    subgraph "Connection Configuration"
        Settings["Settings class"]
        ENV_VARS["Environment Variables"]
        DATABASE_URL["DATABASE_URL"]
    end
    
    subgraph "Frontend Connections"
        PrismaClient["Prisma Client"]
        PrismaEngine["Prisma Query Engine"]
    end
    
    subgraph "Backend Connections"
        SQLAlchemyEngine["SQLAlchemy Engine"]
        AIOMySQL["aiomysql driver"]
        AsyncSession["AsyncSession"]
        AgentCRUD["AgentCRUD"]
    end
    
    subgraph "Database"
        MySQL[("MySQL Database")]
    end
    
    ENV_VARS --> Settings
    ENV_VARS --> DATABASE_URL
    
    Settings -->|"db_url property"| SQLAlchemyEngine
    DATABASE_URL --> PrismaEngine
    
    PrismaClient --> PrismaEngine
    PrismaEngine -->|"mysql://"| MySQL
    
    SQLAlchemyEngine --> AIOMySQL
    AIOMySQL -->|"mysql+aiomysql://"| MySQL
    
    AsyncSession --> SQLAlchemyEngine
    AgentCRUD --> AsyncSession
```

### Backend Database Configuration

The FastAPI backend uses SQLAlchemy with async MySQL support through the `Settings` class:

```python
# Database connection URL construction
@property
def db_url(self) -> URL:
    return URL.build(
        scheme="mysql+aiomysql",
        host=self.db_host,
        port=self.db_port,
        user=self.db_user,
        password=self.db_pass,
        path=f"/{self.db_base}",
    )
```

**Key Configuration Fields:**
- `db_host`: Database host (default: "localhost")
- `db_port`: Database port (default: 3308)
- `db_user`: Database username (default: "reworkd_platform")
- `db_pass`: Database password (default: "reworkd_platform")
- `db_base`: Database name (default: "reworkd_platform")
- `db_echo`: SQLAlchemy logging (default: False)

### Frontend Database Configuration

The Next.js frontend uses Prisma with the `DATABASE_URL` environment variable for connection management. The Prisma configuration includes:

- **Provider**: `mysql`
- **Relation Mode**: `prisma` (for compatibility with serverless databases like PlanetScale)
- **Client Generation**: Automatic Prisma Client generation

### Database Session Management

Backend database sessions are managed through dependency injection:

```python
def agent_crud(
    user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AgentCRUD:
    return AgentCRUD(session, user)
```

The `AgentCRUD` class provides database operations with user context and async session management.

Sources: [platform/reworkd_platform/settings.py:121-130](), [next/prisma/schema.prisma:5-9](), [platform/reworkd_platform/web/api/agent/dependancies.py:26-30](), [platform/reworkd_platform/settings.py:71-78]()

## Data Persistence Patterns

The system implements several data persistence patterns to support agent execution and user management.

### Agent Execution Data Flow

The agent execution system uses a dual-model approach for tracking runs and tasks:

```mermaid
sequenceDiagram
    participant Frontend as "Next.js Frontend"
    participant Backend as "FastAPI Backend" 
    participant AgentCRUD as "AgentCRUD"
    participant Database as "MySQL Database"
    
    Frontend->>Backend: "Create Agent Run"
    Backend->>AgentCRUD: "create_run(goal)"
    AgentCRUD->>Database: "INSERT INTO agent_run"
    Database-->>AgentCRUD: "run_id"
    AgentCRUD-->>Backend: "NewRun object"
    Backend-->>Frontend: "AgentRun with run_id"
    
    loop Task Execution
        Frontend->>Backend: "Execute Task"
        Backend->>AgentCRUD: "create_task(run_id, type)"
        AgentCRUD->>Database: "INSERT INTO agent_task"
        Database-->>AgentCRUD: "task_id"
        AgentCRUD-->>Backend: "Task object"
        Backend-->>Frontend: "Task results"
    end
```

### CRUD Operations Architecture

The backend implements CRUD operations through the `AgentCRUD` class, which provides user-scoped database operations:

```mermaid
classDiagram
    class AgentCRUD {
        -session: AsyncSession
        -user: UserBase
        +create_run(goal: str) NewRun
        +create_task(run_id: str, type: Loop_Step) Task
        +get_user_runs() List[NewRun]
        +get_run_tasks(run_id: str) List[Task]
    }
    
    class AsyncSession {
        +add(instance: object) None
        +commit() None
        +refresh(instance: object) None
        +execute(statement: SQL) Result
    }
    
    class UserBase {
        +id: str
        +email: str
        +name: str
    }
    
    AgentCRUD --> AsyncSession: uses
    AgentCRUD --> UserBase: scoped_to
```

### Database Transaction Patterns

Database operations follow consistent transaction patterns with user context:

1. **Run Creation**: Creates new agent execution with user association and goal
2. **Task Creation**: Creates individual tasks linked to runs with execution type
3. **User Scoping**: All operations are scoped to authenticated user context
4. **Async Sessions**: All database operations use async/await patterns for scalability

Sources: [platform/reworkd_platform/web/api/agent/dependancies.py:42-50](), [platform/reworkd_platform/web/api/agent/dependancies.py:26-30]()

## Database Dependencies and Patterns

The system uses FastAPI dependency injection for database session management and user context:

### Dependency Injection Pattern

```mermaid
flowchart TD
    Request["HTTP Request"]
    GetCurrentUser["get_current_user()"]
    GetDBSession["get_db_session()"]
    AgentCRUD["AgentCRUD(session, user)"]
    BusinessLogic["Agent API Logic"]
    
    Request --> GetCurrentUser
    Request --> GetDBSession
    GetCurrentUser --> AgentCRUD
    GetDBSession --> AgentCRUD
    AgentCRUD --> BusinessLogic
```

**Key Dependency Functions:**
- `get_current_user()`: Extracts authenticated user from request
- `get_db_session()`: Provides async database session
- `agent_crud()`: Combines user and session into CRUD operations

### Validation and Data Flow

The system implements validation decorators for agent operations:

- `agent_start_validator`: Validates agent run creation
- `agent_analyze_validator`: Validates task analysis requests  
- `agent_execute_validator`: Validates task execution requests
- `agent_create_validator`: Validates task creation requests
- `agent_summarize_validator`: Validates summarization requests

Each validator creates database records and returns typed objects for downstream processing.

Sources: [platform/reworkd_platform/web/api/agent/dependancies.py:33-96]()

## Security Considerations

The system implements several security measures for data storage:

1. **Database Security**:
   - SSL connections in production environments
   - Encrypted OAuth tokens (indicated by `_enc` suffix in field names)

2. **S3 Security**:
   - Presigned URLs with limited validity for secure file access
   - Region-specific configuration (US East 1)

3. **Client Storage**:
   - Versioned localStorage keys to handle schema migrations

Sources: [platform/reworkd_platform/services/aws/s3.py:29-44](), [next/prisma/schema.prisma:112-114]()

---

# Page: Agent System

# Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE/pull_request_template.md](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)
- [README.md](README.md)
- [docs/README.hu-Cs4K1Sr4C.md](docs/README.hu-Cs4K1Sr4C.md)
- [docs/README.zh-HANS.md](docs/README.zh-HANS.md)
- [next/src/components/console/ChatMessage.tsx](next/src/components/console/ChatMessage.tsx)
- [platform/reworkd_platform/web/api/agent/prompts.py](platform/reworkd_platform/web/api/agent/prompts.py)
- [platform/reworkd_platform/web/api/agent/tools/code.py](platform/reworkd_platform/web/api/agent/tools/code.py)
- [platform/reworkd_platform/web/api/agent/tools/conclude.py](platform/reworkd_platform/web/api/agent/tools/conclude.py)
- [platform/reworkd_platform/web/api/agent/tools/image.py](platform/reworkd_platform/web/api/agent/tools/image.py)
- [platform/reworkd_platform/web/api/agent/tools/reason.py](platform/reworkd_platform/web/api/agent/tools/reason.py)
- [platform/reworkd_platform/web/api/agent/tools/search.py](platform/reworkd_platform/web/api/agent/tools/search.py)
- [platform/reworkd_platform/web/api/agent/tools/tool.py](platform/reworkd_platform/web/api/agent/tools/tool.py)
- [platform/reworkd_platform/web/api/agent/tools/tools.py](platform/reworkd_platform/web/api/agent/tools/tools.py)
- [platform/reworkd_platform/web/api/agent/tools/utils.py](platform/reworkd_platform/web/api/agent/tools/utils.py)
- [platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py](platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py)

</details>



This document covers the autonomous agent execution system that forms the core of AgentGPT. The agent system handles goal decomposition, task execution, and tool coordination to enable autonomous AI agents to work toward user-defined objectives.

For information about the web API endpoints that expose agent functionality, see [Agent API](#3.1). For details about individual tools that agents use, see [Agent Tools](#3.3). For prompt template management, see [Prompts and Output Parsing](#4.3).

## System Purpose

The Agent System implements an autonomous execution loop where agents:
1. Accept high-level goals from users
2. Break down goals into executable tasks  
3. Select and execute appropriate tools for each task
4. Learn from results and generate new tasks
5. Continue until the goal is achieved or terminated

## Agent Architecture Overview

The agent system follows a modular architecture with clear separation between prompt management, tool execution, and service coordination.

```mermaid
graph TD
    User["User Goal Input"] --> AgentService["OpenAIAgentService"]
    AgentService --> PromptSystem["Prompt Template System"]
    AgentService --> ToolSystem["Tool Execution System"]
    AgentService --> ModelFactory["ModelFactory"]
    
    PromptSystem --> StartGoal["start_goal_prompt"]
    PromptSystem --> AnalyzeTask["analyze_task_prompt"] 
    PromptSystem --> CreateTasks["create_tasks_prompt"]
    PromptSystem --> ExecuteTask["execute_task_prompt"]
    PromptSystem --> Summarize["summarize_prompt"]
    
    ToolSystem --> Search["Search Tool"]
    ToolSystem --> Code["Code Tool"]
    ToolSystem --> Image["Image Tool"]
    ToolSystem --> Reason["Reason Tool"]
    ToolSystem --> Conclude["Conclude Tool"]
    
    ModelFactory --> OpenAI["OpenAI Chat Models"]
    ModelFactory --> TokenService["Token Management"]
    
    AgentService --> TaskQueue["Task Execution Queue"]
    TaskQueue --> Results["Streamed Results"]
```

Sources: [platform/reworkd_platform/web/api/agent/prompts.py:1-186](), [platform/reworkd_platform/web/api/agent/tools/tools.py:1-79]()

## Core Execution Loop

The agent execution follows a structured loop that combines prompt-driven task generation with tool-based execution.

### Agent Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant AgentService as "OpenAIAgentService"
    participant PromptSystem as "Prompt Templates"
    participant ToolSelector as "Tool Selection"
    participant ToolExecution as "Tool Execution"
    participant LLM as "OpenAI Models"
    
    User->>AgentService: "Goal Definition"
    AgentService->>PromptSystem: "start_goal_prompt"
    PromptSystem->>LLM: "Generate Initial Tasks"
    LLM-->>AgentService: "Task List"
    
    loop "Task Execution Loop"
        AgentService->>PromptSystem: "analyze_task_prompt"
        PromptSystem->>LLM: "Analyze Current Task"
        LLM-->>ToolSelector: "Tool Selection"
        ToolSelector->>ToolExecution: "Execute Selected Tool"
        ToolExecution->>LLM: "Tool-specific Processing"
        LLM-->>AgentService: "Task Results"
        AgentService->>PromptSystem: "create_tasks_prompt"
        PromptSystem->>LLM: "Generate Next Tasks"
        LLM-->>AgentService: "New Tasks"
    end
    
    AgentService->>PromptSystem: "summarize_prompt"
    PromptSystem->>LLM: "Final Summary"
    LLM-->>User: "Completed Results"
```

Sources: [platform/reworkd_platform/web/api/agent/prompts.py:5-22](), [platform/reworkd_platform/web/api/agent/prompts.py:24-36](), [platform/reworkd_platform/web/api/agent/prompts.py:69-92]()

### Task Generation and Analysis

The system uses structured prompts to break down goals and analyze tasks:

| Prompt Template | Purpose | Key Variables |
|-----------------|---------|---------------|
| `start_goal_prompt` | Convert user goal into initial search queries | `goal`, `language` |
| `analyze_task_prompt` | Determine appropriate tool for current task | `goal`, `task`, `language` |
| `create_tasks_prompt` | Generate next task based on previous results | `goal`, `tasks`, `lastTask`, `result`, `language` |
| `execute_task_prompt` | Execute reasoning-based tasks | `goal`, `task`, `language` |
| `summarize_prompt` | Combine results into cohesive output | `goal`, `text`, `language` |

Sources: [platform/reworkd_platform/web/api/agent/prompts.py:5-22](), [platform/reworkd_platform/web/api/agent/prompts.py:24-36](), [platform/reworkd_platform/web/api/agent/prompts.py:69-92](), [platform/reworkd_platform/web/api/agent/prompts.py:58-67](), [platform/reworkd_platform/web/api/agent/prompts.py:94-109]()

## Tool Selection and Execution

The agent system integrates multiple specialized tools that can be dynamically selected based on task requirements.

### Available Tool Types

```mermaid
graph TD
    ToolSystem["Tool Selection System"] --> DefaultTools["Default Tools"]
    ToolSystem --> ExternalTools["External Tools"]
    
    DefaultTools --> Search["Search Tool"]
    
    ExternalTools --> Image["Image Tool"]
    ExternalTools --> Code["Code Tool"] 
    ExternalTools --> SID["SID Search Tool"]
    
    Search --> SerperAPI["Google Serper API"]
    Image --> OpenAIImage["OpenAI DALL-E"]
    Image --> ReplicateAPI["Replicate Stable Diffusion"]
    Code --> CodeGeneration["LLM Code Generation"]
    SID --> CustomSearch["Custom Search Implementation"]
    
    Search --> SearchResults["CitedSnippet Results"]
    Image --> ImageURL["Generated Image URLs"]
    Code --> CodeBlocks["Formatted Code Output"]
    SID --> SnippetResults["Text Snippets"]
```

Sources: [platform/reworkd_platform/web/api/agent/tools/tools.py:27-39](), [platform/reworkd_platform/web/api/agent/tools/search.py:42-110](), [platform/reworkd_platform/web/api/agent/tools/image.py:47-67](), [platform/reworkd_platform/web/api/agent/tools/code.py:10-26]()

### Tool Availability and Selection

The system dynamically determines tool availability based on API key configuration and user permissions:

```python
# Tool availability checking
def get_available_tools() -> List[Type[Tool]]:
    return get_external_tools() + get_default_tools()

async def get_user_tools(
    tool_names: List[str], user: UserBase, crud: OAuthCrud
) -> List[Type[Tool]]:
    tools = list(map(get_tool_from_name, tool_names)) + get_default_tools()
    return [tool for tool in tools if await tool.dynamic_available(user, crud)]
```

Sources: [platform/reworkd_platform/web/api/agent/tools/tools.py:19-21](), [platform/reworkd_platform/web/api/agent/tools/tools.py:12-16]()

## Agent Service Implementation

The core agent service coordinates between prompts, tools, and language models to execute the autonomous behavior.

### Service Architecture

```mermaid
graph TD
    AgentService["OpenAIAgentService"] --> ServiceProvider["Agent Service Provider"]
    AgentService --> ModelFactory["Model Factory"]
    AgentService --> ToolManager["Tool Management"]
    
    ServiceProvider --> OpenAIService["OpenAI Agent Service"]
    ServiceProvider --> MockService["Mock Agent Service"]
    
    ModelFactory --> ChatModels["BaseChatModel Instances"]
    ModelFactory --> TokenService["Token Usage Tracking"]
    ModelFactory --> Settings["Configuration Settings"]
    
    ToolManager --> ToolFactory["Tool Instantiation"]
    ToolManager --> ToolSelection["Dynamic Tool Selection"]
    ToolManager --> ToolExecution["Streaming Tool Execution"]
    
    ToolExecution --> SearchTool["Search.call()"]
    ToolExecution --> CodeTool["Code.call()"]
    ToolExecution --> ImageTool["Image.call()"]
    ToolExecution --> ReasonTool["Reason.call()"]
```

Sources: [platform/reworkd_platform/web/api/agent/tools/tool.py:11-42](), [platform/reworkd_platform/web/api/agent/tools/search.py:55-110](), [platform/reworkd_platform/web/api/agent/tools/reason.py:10-28]()

### Tool Base Class Interface

All tools implement a common interface for consistent integration:

```python
class Tool(ABC):
    description: str = ""
    public_description: str = ""
    arg_description: str = "The argument to the function."
    image_url: str = "/tools/openai-white.png"
    
    model: BaseChatModel
    language: str
    
    @abstractmethod
    async def call(
        self,
        goal: str,
        task: str,
        input_str: str,
        user: UserBase,
        oauth_crud: OAuthCrud,
    ) -> StreamingResponse:
        pass
```

Sources: [platform/reworkd_platform/web/api/agent/tools/tool.py:11-42]()

## Streaming Response System

The agent system uses streaming responses to provide real-time feedback during task execution, allowing users to see progress as tasks are being processed.

### Response Flow

All tool executions return `FastAPIStreamingResponse` objects that stream results back to the frontend as they are generated. This enables:

- Real-time task progress visibility
- Immediate feedback on tool execution
- Graceful handling of long-running operations
- User engagement throughout the agent execution process

Sources: [platform/reworkd_platform/web/api/agent/tools/search.py:55-64](), [platform/reworkd_platform/web/api/agent/tools/utils.py:34-53](), [platform/reworkd_platform/web/api/agent/stream_mock.py]()

## Error Handling and Fallbacks

The system implements robust error handling with automatic fallbacks to ensure agent execution continues even when specific tools fail:

```python
async def call(
    self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any
) -> FastAPIStreamingResponse:
    try:
        return await self._call(goal, task, input_str, *args, **kwargs)
    except ClientResponseError:
        logger.exception("Error calling Serper API, falling back to reasoning")
        return await Reason(self.model, self.language).call(
            goal, task, input_str, *args, **kwargs
        )
```

When external APIs fail (like search services), the system automatically falls back to reasoning-based task execution using the language model directly.

Sources: [platform/reworkd_platform/web/api/agent/tools/search.py:55-64](), [platform/reworkd_platform/web/api/agent/tools/reason.py:16-28]()

---

# Page: Agent Lifecycle

# Agent Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE/pull_request_template.md](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)
- [README.md](README.md)
- [docs/README.hu-Cs4K1Sr4C.md](docs/README.hu-Cs4K1Sr4C.md)
- [docs/README.zh-HANS.md](docs/README.zh-HANS.md)
- [next/src/components/console/ChatMessage.tsx](next/src/components/console/ChatMessage.tsx)
- [next/src/components/console/ChatWindow.tsx](next/src/components/console/ChatWindow.tsx)
- [next/src/components/console/MacWindowHeader.tsx](next/src/components/console/MacWindowHeader.tsx)
- [next/src/components/console/SummarizeButton.tsx](next/src/components/console/SummarizeButton.tsx)
- [next/src/pages/agent/index.tsx](next/src/pages/agent/index.tsx)
- [next/src/pages/index.tsx](next/src/pages/index.tsx)
- [next/src/services/agent/agent-run-model.tsx](next/src/services/agent/agent-run-model.tsx)
- [next/src/services/agent/autonomous-agent.ts](next/src/services/agent/autonomous-agent.ts)
- [next/src/services/agent/message-service.ts](next/src/services/agent/message-service.ts)
- [next/src/stores/agentStore.ts](next/src/stores/agentStore.ts)

</details>



This document details the complete lifecycle of an agent in the AgentGPT system, from creation to completion. It covers the agent states, initialization, execution flow, and how the agent processes tasks. For specific details about task execution and analysis, see [Task Execution](#4.2). For information about prompt templates used in agent operations, see [Prompts and Output Parsing](#4.3).

## Agent Lifecycle Overview

The AgentGPT system implements an autonomous agent that can execute a sequence of tasks to achieve a user-defined goal. The agent lifecycle encompasses the entire process from when a user initializes an agent with a goal to when the agent completes its execution.

```mermaid
stateDiagram-v2
    [*] --> "offline" : Initialize
    "offline" --> "running" : Start with goal
    "running" --> "pausing" : Pause request
    "pausing" --> "paused" : Pause complete
    "paused" --> "running" : Resume
    "running" --> "stopped" : Complete all tasks/Error/Manual stop
    "paused" --> "stopped" : Manual stop
    "stopped" --> [*]

    note right of "offline"
      Initial state before agent starts
    end note
    note right of "running"
      Agent actively processing tasks
    end note
    note right of "paused"
      Execution temporarily halted
    end note
    note right of "stopped"
      Agent execution completed
    end note
```

Sources: [next/src/services/agent/agent-run-model.tsx:32](). [next/src/services/agent/autonomous-agent.ts:42-81]().

## Agent Components and Architecture

The agent system consists of frontend components that coordinate to manage the agent's lifecycle and execution.

```mermaid
graph TD
    subgraph "Frontend Components"
        IndexPage["pages/index.tsx"] -->|handleNewAgent| AutonomousAgent["AutonomousAgent"]
        AutonomousAgent -->|constructor| DefaultAgentRunModel["DefaultAgentRunModel"]
        AutonomousAgent -->|constructor| MessageService["MessageService"]
        AutonomousAgent -->|constructor| AgentApi["AgentApi"]
        AutonomousAgent -->|maintains| workLog["workLog: AgentWork[]"]
        
        subgraph "State Management"
            useAgentStore["useAgentStore"] -->|lifecycle| AgentSlice["AgentSlice"]
            useTaskStore["useTaskStore"] -->|tasks| TaskSlice["tasks"]
            useMessageStore["useMessageStore"] -->|messages| MessageSlice["messages"]
        end
        
        subgraph "Work Types"
            workLog -->|contains| StartGoalWork["StartGoalWork"]
            workLog -->|contains| AnalyzeTaskWork["AnalyzeTaskWork"] 
            workLog -->|contains| SummarizeWork["SummarizeWork"]
            workLog -->|contains| ChatWork["ChatWork"]
        end
    end

    User -->|sets goalInput| IndexPage
    AutonomousAgent -->|setAgent| useAgentStore
    MessageService -->|addMessage| useMessageStore
```

Sources: [next/src/pages/index.tsx:72-100](). [next/src/services/agent/autonomous-agent.ts:17-39](). [next/src/stores/agentStore.ts:10-26](). [next/src/stores/taskStore.ts:1-50](). [next/src/stores/messageStore.ts:1-30]().

### Core Components

| Component | File Location | Description |
|-----------|---------------|-------------|
| `AutonomousAgent` | [next/src/services/agent/autonomous-agent.ts:17]() | Main class managing agent lifecycle with `run()`, `pauseAgent()`, `stopAgent()` methods |
| `DefaultAgentRunModel` | [next/src/services/agent/agent-run-model.tsx:34]() | Implements `AgentRunModel` interface, manages goal, tasks, and lifecycle state |
| `MessageService` | [next/src/services/agent/message-service.ts:12]() | Handles `sendMessage()`, `sendErrorMessage()`, `startTask()` for UI updates |
| `AgentApi` | [next/src/services/agent/agent-api.ts:1]() | Frontend service for backend API communication |
| `useAgentStore` | [next/src/stores/agentStore.ts:78]() | Zustand store managing `agent`, `lifecycle`, `isAgentThinking` state |

Sources: [next/src/services/agent/autonomous-agent.ts:17-40](). [next/src/services/agent/agent-run-model.tsx:34-79](). [next/src/services/agent/message-service.ts:12-17](). [next/src/stores/agentStore.ts:10-26]().

## Agent Initialization

The agent initialization process starts when a user defines a goal in the `goalInput` field and triggers `handleNewAgent()`.

```mermaid
sequenceDiagram
    participant User
    participant IndexPage as "pages/index.tsx"
    participant Agent as "AutonomousAgent"
    participant Model as "DefaultAgentRunModel"
    participant MessageService as "MessageService"
    participant AgentAPI as "AgentApi"
    participant AgentStore as "useAgentStore"

    User->>IndexPage: Enter goalInput, trigger handlePlay()
    IndexPage->>IndexPage: handleNewAgent(goal.trim())
    IndexPage->>Model: new DefaultAgentRunModel(goal.trim())
    Model->>Model: this.id = v4().toString()
    IndexPage->>MessageService: new MessageService(addMessage)
    IndexPage->>AgentAPI: new AgentApi({model_settings, goal, session, agentUtils})
    IndexPage->>Agent: new AutonomousAgent(model, messageService, settings, agentApi, session)
    Agent->>Agent: this.workLog = [new StartGoalWork(this)]
    IndexPage->>AgentStore: setAgent(newAgent)
    IndexPage->>Agent: newAgent?.run()
    Agent->>Model: model.setLifecycle("running")
    Agent->>Agent: addTasksIfWorklogEmpty()
    Note over Agent: Starts with StartGoalWork in workLog
```

Sources: [next/src/pages/index.tsx:72-100](). [next/src/services/agent/autonomous-agent.ts:27-39](). [next/src/services/agent/agent-run-model.tsx:34-41](). [next/src/services/agent/message-service.ts:12-16]().

The initialization process involves:

1. User enters goal in `goalInput` and calls `handlePlay(goalInput)` [next/src/pages/index.tsx:67-70]()
2. `handleNewAgent()` creates a new `DefaultAgentRunModel(goal.trim())` with unique ID via `v4()` [next/src/services/agent/agent-run-model.tsx:38-41]()
3. `MessageService` is created with `addMessage` callback from `useMessageStore` [next/src/pages/index.tsx:85]()
4. `AgentApi` is created with `toApiModelSettings()` configuration [next/src/pages/index.tsx:86-91]()
5. `AutonomousAgent` constructor initializes `workLog` with `StartGoalWork` [next/src/services/agent/autonomous-agent.ts:39]()
6. `setAgent(newAgent)` updates `useAgentStore` state [next/src/pages/index.tsx:99]()
7. `newAgent?.run()` starts the execution loop [next/src/pages/index.tsx:100]()

Sources: [next/src/pages/index.tsx:72-100](). [next/src/services/agent/autonomous-agent.ts:27-39](). [next/src/services/agent/agent-run-model.tsx:34-47]().

The initialization process involves:

1. User sets a goal in the frontend
2. The frontend creates a new `DefaultAgentRunModel` with the goal
3. The frontend creates a `MessageService` for handling UI messages
4. The frontend creates an `AgentApi` for communicating with the backend
5. The frontend creates an `AutonomousAgent` with these components
6. The `AutonomousAgent.run()` method is called to start execution
7. The agent sends a request to the backend to generate initial tasks
8. The backend uses LLM prompting to generate tasks based on the goal
9. The tasks are returned to the frontend and displayed to the user

Sources: [next/src/pages/index.tsx:72-100](). [next/src/services/agent/autonomous-agent.ts:42-46]().

## Agent Execution Process

After initialization, the agent enters its main execution loop, processing tasks until completion.

### Agent Execution Loop

The `AutonomousAgent.run()` method implements the main execution loop using a `workLog` array of `AgentWork` items.

```mermaid
flowchart TD
    Start([run]) --> SetRunning["model.setLifecycle('running')"]
    SetRunning --> CheckConclusion{"lastConclusion exists?"}
    CheckConclusion -->|Yes| RunConclusion["await this.lastConclusion()"]
    CheckConclusion -->|No| AddTasks["addTasksIfWorklogEmpty()"]
    RunConclusion --> AddTasks
    AddTasks --> CheckWorkLog{"this.workLog[0] exists?"}
    CheckWorkLog -->|No| CheckLifecycle1{"lifecycle === 'pausing'?"}
    CheckLifecycle1 -->|Yes| SetPaused["model.setLifecycle('paused')"]
    CheckLifecycle1 -->|No| StopAgent["stopAgent()"]
    CheckWorkLog -->|Yes| CheckPausing{"lifecycle === 'pausing'?"}
    CheckPausing -->|Yes| SetPaused
    CheckPausing -->|No| CheckRunning{"lifecycle !== 'running'?"}
    CheckRunning -->|Yes| Return["return"]
    CheckRunning -->|No| GetWork["work = this.workLog[0]"]
    GetWork --> RunWork["await this.runWork(work)"]
    RunWork --> ShiftWork["this.workLog.shift()"]
    ShiftWork --> CheckLifecycle2{"lifecycle !== 'running'?"}
    CheckLifecycle2 -->|Yes| SaveConclusion["this.lastConclusion = () => work.conclude()"]
    CheckLifecycle2 -->|No| ConcludeWork["await work.conclude()"]
    SaveConclusion --> GetNext["next = work.next()"]
    ConcludeWork --> GetNext
    GetNext --> CheckNext{"next exists?"}
    CheckNext -->|Yes| PushNext["this.workLog.push(next)"]
    CheckNext -->|No| AddTasks
    PushNext --> AddTasks
    SetPaused --> Return
    StopAgent --> Return
    Return --> End([End])
```

Sources: [next/src/services/agent/autonomous-agent.ts:42-81]().

The execution process follows these steps:

1. `model.setLifecycle("running")` sets the agent state [next/src/services/agent/autonomous-agent.ts:43]()
2. Resumes any pending `lastConclusion` from paused state [next/src/services/agent/autonomous-agent.ts:46-49]()
3. `addTasksIfWorklogEmpty()` adds `AnalyzeTaskWork` if tasks exist [next/src/services/agent/autonomous-agent.ts:115-123]()
4. Main loop processes `this.workLog[0]` until empty [next/src/services/agent/autonomous-agent.ts:52-75]()
5. `runWork(work)` executes the work item with retry logic [next/src/services/agent/autonomous-agent.ts:87-112]()
6. `this.workLog.shift()` removes completed work [next/src/services/agent/autonomous-agent.ts:61]()
7. `work.conclude()` finalizes the work and `work.next()` provides follow-up work [next/src/services/agent/autonomous-agent.ts:65-72]()
8. Process repeats until `workLog` is empty and no tasks remain

Sources: [next/src/services/agent/autonomous-agent.ts:42-81]().

The execution process follows these steps:

1. The agent sets its lifecycle to "running"
2. It checks if the work log is empty
   - If empty, it adds tasks if any are available, otherwise stops
3. It runs the next work item in the work log
4. It removes the completed work from the work log
5. It concludes the work and adds any follow-up work
6. It repeats the process until all tasks are complete
7. When done, it sets the lifecycle to "stopped"

Sources: [next/src/services/agent/autonomous-agent.ts:42-81]().

### AgentWork Types

The agent uses different `AgentWork` subclasses in its `workLog` to handle execution stages:

| Work Type | File Location | Description |
|-----------|---------------|-------------|
| `StartGoalWork` | [next/src/services/agent/agent-work/start-task-work.ts]() | Initial work added to `workLog` in constructor, gets initial tasks from goal |
| `AnalyzeTaskWork` | [next/src/services/agent/agent-work/analyze-task-work.ts]() | Added by `addTasksIfWorklogEmpty()` when `getCurrentTask()` exists |
| `SummarizeWork` | [next/src/services/agent/agent-work/summarize-work.ts]() | Created by `summarize()` method for final summary generation |
| `ChatWork` | [next/src/services/agent/agent-work/chat-work.ts]() | Created by `chat(message)` method for user interactions |

Each `AgentWork` implements:
- `run()`: Main execution logic
- `conclude()`: Finalization after execution  
- `next()`: Returns follow-up work or undefined
- `onError?()`: Optional error handling

Sources: [next/src/services/agent/autonomous-agent.ts:5-9](). [next/src/services/agent/autonomous-agent.ts:39](). [next/src/services/agent/autonomous-agent.ts:121](). [next/src/services/agent/autonomous-agent.ts:134-140](). [next/src/services/agent/autonomous-agent.ts:142-155]().

## Agent-Backend Interaction

The agent communicates with the backend through several API endpoints to perform its functions:

```mermaid
sequenceDiagram
    participant Agent as "AutonomousAgent"
    participant API as "AgentApi"
    participant Backend as "Backend Endpoints"
    participant Service as "OpenAIAgentService"
    participant LLM as "Language Model"
    participant Tools as "Agent Tools"

    Agent->>API: Start agent with goal
    API->>Backend: POST /start
    Backend->>Service: start_goal_agent(goal)
    Service->>LLM: Generate tasks with prompt
    LLM-->>Service: Return tasks
    Service-->>Backend: Return tasks
    Backend-->>API: Return tasks
    API-->>Agent: Return tasks

    loop For each task
        Agent->>API: Analyze task
        API->>Backend: POST /analyze
        Backend->>Service: analyze_task_agent(goal, task, tool_names)
        Service->>LLM: Analyze task with prompt
        LLM-->>Service: Return tool selection
        Service-->>Backend: Return analysis
        Backend-->>API: Return analysis
        API-->>Agent: Return analysis

        Agent->>API: Execute task
        API->>Backend: POST /execute
        Backend->>Service: execute_task_agent(goal, task, analysis)
        Service->>Tools: Call appropriate tool
        Tools-->>Service: Return tool result
        Service-->>Backend: Stream response
        Backend-->>API: Stream response
        API-->>Agent: Stream response

        Agent->>API: Create new tasks
        API->>Backend: POST /create
        Backend->>Service: create_tasks_agent(goal, tasks, last_task, result)
        Service->>LLM: Generate new tasks
        LLM-->>Service: Return new tasks
        Service-->>Backend: Return new tasks
        Backend-->>API: Return new tasks
        API-->>Agent: Return new tasks
    end

    Agent->>API: Summarize results
    API->>Backend: POST /summarize
    Backend->>Service: summarize_task_agent(goal, results)
    Service->>LLM: Generate summary
    LLM-->>Service: Return summary
    Service-->>Backend: Stream summary
    Backend-->>API: Stream summary
    API-->>Agent: Stream summary
```

Sources: [platform/reworkd_platform/web/api/agent/views.py:34-117](). [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:60-227](). [next/src/services/agent/autonomous-agent.ts:42-168]().

The agent interacts with the backend through these key endpoints:

1. **Start** (`/start`): Initializes the agent with a goal and generates initial tasks
2. **Analyze** (`/analyze`): Analyzes a task to determine the appropriate tool
3. **Execute** (`/execute`): Executes a task using the selected tool
4. **Create** (`/create`): Creates new tasks based on results
5. **Summarize** (`/summarize`): Generates a summary of results
6. **Chat** (`/chat`): Handles user interactions during execution

Each endpoint corresponds to a stage in the agent lifecycle and is handled by corresponding methods in the `OpenAIAgentService`.

Sources: [platform/reworkd_platform/web/api/agent/views.py:34-117](). [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:60-227]().

## Agent Tools

The agent uses various tools to accomplish tasks. These tools are selected during the task analysis phase:

| Tool | Description | Use Case |
|------|-------------|----------|
| `Search` | Searches Google for information | Finding current information and answering questions |
| `Image` | Generates images based on prompts | Creating visual content |
| `Code` | Writes and reviews code | Programming tasks and code explanation |
| `Reason` | Uses logical reasoning | Making decisions and analyzing information |
| `Wikipedia` | Searches Wikipedia | Finding historical and factual information |
| `Conclude` | Concludes task execution | Ending a task when complete |

The tool selection process:
1. The agent analyzes the task using the `analyze_task_agent` method
2. The LLM determines the most appropriate tool for the task
3. The selected tool is called with the task information
4. The tool's result is returned to the agent

Sources: [platform/reworkd_platform/web/api/agent/tools/tools.py:12-78](). [platform/reworkd_platform/web/api/agent/tools/search.py:42-109](). [platform/reworkd_platform/web/api/agent/tools/image.py:47-66](). [platform/reworkd_platform/web/api/agent/tools/code.py:10-25](). [platform/reworkd_platform/web/api/agent/tools/reason.py:10-27](). [platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py:10-30](). [platform/reworkd_platform/web/api/agent/tools/conclude.py:9-15]().

## Agent State Management

The agent state is managed through Zustand stores and the `DefaultAgentRunModel`:

### Zustand Stores

| Store | File Location | State Management |
|-------|---------------|------------------|
| `useAgentStore` | [next/src/stores/agentStore.ts:78]() | `agent: AutonomousAgent`, `lifecycle: AgentLifecycle`, `isAgentThinking: boolean` |
| `useTaskStore` | [next/src/stores/taskStore.ts]() | `tasks: Task[]`, `addTask()`, `updateTask()` methods |
| `useMessageStore` | [next/src/stores/messageStore.ts]() | `messages: Message[]`, `addMessage()`, `updateMessage()` methods |

### AgentLifecycle States

The `AgentLifecycle` type defines agent execution states:

```mermaid
stateDiagram-v2
    [*] --> offline : "initialAgentState"
    offline --> running : "model.setLifecycle('running')"
    running --> pausing : "pauseAgent()"
    pausing --> paused : "lifecycle check in run()"
    paused --> running : "run() resume"
    running --> stopped : "stopAgent() or completion"
    paused --> stopped : "stopAgent()"
    stopped --> [*] : "agent cleanup"

    note right of offline
      Initial state in agentStore
    end note
    note right of running
      Main execution loop active
    end note
    note right of pausing
      Transitional state
    end note
    note right of stopped
      Final state
    end note
```

Sources: [next/src/services/agent/agent-run-model.tsx:32](). [next/src/stores/agentStore.ts:21-26]().

### State Transitions

| Transition | Trigger | Implementation |
|------------|---------|----------------|
| `offline` → `running` | `handleNewAgent()` calls `newAgent?.run()` | [next/src/pages/index.tsx:100]() |
| `running` → `pausing` | User clicks pause, calls `pauseAgent()` | [next/src/services/agent/autonomous-agent.ts:125-127]() |
| `pausing` → `paused` | `run()` loop checks `getLifecycle() === "pausing"` | [next/src/services/agent/autonomous-agent.ts:54]() |
| `paused` → `running` | User resumes, calls `run()` again | [next/src/services/agent/autonomous-agent.ts:42]() |
| Any → `stopped` | `stopAgent()` or completion | [next/src/services/agent/autonomous-agent.ts:129-132]() |

The `DefaultAgentRunModel` proxies lifecycle state to `useAgentStore`:
- `getLifecycle()` calls `useAgentStore.getState().lifecycle` [next/src/services/agent/agent-run-model.tsx:46]()
- `setLifecycle()` calls `useAgentStore.getState().setLifecycle()` [next/src/services/agent/agent-run-model.tsx:47]()

Sources: [next/src/services/agent/agent-run-model.tsx:46-47](). [next/src/services/agent/autonomous-agent.ts:125-132](). [next/src/stores/agentStore.ts:40-44]().

## Special Operations

### Agent Summarization

The `SummarizeButton` component triggers agent summarization when conditions are met:

```mermaid
sequenceDiagram
    participant SummarizeButton as "SummarizeButton"
    participant Agent as "AutonomousAgent"
    participant SummarizeWork as "SummarizeWork"
    participant AgentStore as "useAgentStore"

    SummarizeButton->>SummarizeButton: Check conditions
    Note over SummarizeButton: agent && lifecycle === "stopped"<br/>tasksWithResults.length >= 1<br/>!summarized
    SummarizeButton->>AgentStore: setSummarized(true)
    SummarizeButton->>Agent: agent?.summarize()
    Agent->>Agent: model.setLifecycle("running")
    Agent->>SummarizeWork: new SummarizeWork(this)
    Agent->>Agent: await this.runWork(summarizeWork)
    Agent->>SummarizeWork: await summarizeWork.conclude()
    Agent->>Agent: model.setLifecycle("stopped")
```

Sources: [next/src/components/console/SummarizeButton.tsx:8-39](). [next/src/services/agent/autonomous-agent.ts:134-140]().

Conditions for summarization:
- `agent !== null` and `lifecycle === "stopped"` [next/src/components/console/SummarizeButton.tsx:17]()
- `tasksWithResults.length >= 1` where tasks have `status === "completed"` [next/src/components/console/SummarizeButton.tsx:11-13]()
- `!summarized` to prevent duplicate summaries [next/src/components/console/SummarizeButton.tsx:17]()

### Agent Chat Interaction

The `ChatWindow` component enables user chat with agents through `chatControls`:

```mermaid
sequenceDiagram
    participant ChatWindow as "ChatWindow"
    participant Agent as "AutonomousAgent"
    participant ChatWork as "ChatWork"

    ChatWindow->>ChatWindow: User enters message, clicks chat button
    ChatWindow->>Agent: agent.chat(message)
    Agent->>Agent: Check if running, call pauseAgent()
    Agent->>Agent: Set paused = true if stopped
    Agent->>ChatWork: new ChatWork(this, message)
    Agent->>Agent: await this.runWork(chatWork)
    Agent->>ChatWork: await chatWork.conclude()
    Agent->>Agent: Reset lifecycle if was paused
```

Sources: [next/src/components/console/ChatWindow.tsx:93-109](). [next/src/services/agent/autonomous-agent.ts:142-155]().

The `chat()` method handles different lifecycle states:
- If `lifecycle === "running"`, calls `pauseAgent()` first [next/src/services/agent/autonomous-agent.ts:143]()
- If `lifecycle === "stopped"`, temporarily sets to `"pausing"` for execution [next/src/services/agent/autonomous-agent.ts:145-148]()
- Creates and executes `ChatWork` with user message [next/src/services/agent/autonomous-agent.ts:149-151]()

Sources: [next/src/services/agent/autonomous-agent.ts:142-155](). [next/src/components/console/ChatWindow.tsx:93-109]().

## Agent Error Handling

The agent implements error handling to handle various failure scenarios:

1. **Network errors**: Retry the operation with exponential backoff
2. **API errors**: Display appropriate error messages
3. **LLM errors**: Fallback to default responses
4. **Tool errors**: Fall back to reasoning tool

The `runWork` method in `AutonomousAgent` uses the `withRetries` function to retry operations that fail due to retryable errors.

Sources: [next/src/services/agent/autonomous-agent.ts:87-112](). [next/src/services/agent/message-service.ts:66-106]().

## Conclusion

The Agent Lifecycle in AgentGPT encompasses the entire process of agent creation, initialization, task execution, and completion. The system uses a combination of frontend components for user interaction and state management, and backend services for LLM-based task processing and tool execution. The agent transitions through various lifecycle states as it processes tasks and responds to user actions, providing a flexible and powerful autonomous agent capability.

---

# Page: Task Execution

# Task Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE/pull_request_template.md](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)
- [README.md](README.md)
- [docs/README.hu-Cs4K1Sr4C.md](docs/README.hu-Cs4K1Sr4C.md)
- [docs/README.zh-HANS.md](docs/README.zh-HANS.md)
- [next/src/components/console/ChatMessage.tsx](next/src/components/console/ChatMessage.tsx)
- [platform/reworkd_platform/web/api/agent/prompts.py](platform/reworkd_platform/web/api/agent/prompts.py)
- [platform/reworkd_platform/web/api/agent/tools/code.py](platform/reworkd_platform/web/api/agent/tools/code.py)
- [platform/reworkd_platform/web/api/agent/tools/conclude.py](platform/reworkd_platform/web/api/agent/tools/conclude.py)
- [platform/reworkd_platform/web/api/agent/tools/image.py](platform/reworkd_platform/web/api/agent/tools/image.py)
- [platform/reworkd_platform/web/api/agent/tools/reason.py](platform/reworkd_platform/web/api/agent/tools/reason.py)
- [platform/reworkd_platform/web/api/agent/tools/search.py](platform/reworkd_platform/web/api/agent/tools/search.py)
- [platform/reworkd_platform/web/api/agent/tools/tool.py](platform/reworkd_platform/web/api/agent/tools/tool.py)
- [platform/reworkd_platform/web/api/agent/tools/tools.py](platform/reworkd_platform/web/api/agent/tools/tools.py)
- [platform/reworkd_platform/web/api/agent/tools/utils.py](platform/reworkd_platform/web/api/agent/tools/utils.py)
- [platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py](platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py)

</details>



This document covers how AgentGPT agents break down high-level goals into executable tasks and execute them using various tools and LLM interactions. The task execution system is the core engine that drives autonomous agent behavior through iterative planning, tool selection, and result processing.

For information about the overall agent lifecycle and management, see [Agent Lifecycle](#4.1). For details about prompt templates and output parsing, see [Prompts and Output Parsing](#4.3).

## Overview

The task execution system operates through a continuous loop where agents:
1. Break down goals into specific, actionable tasks
2. Analyze each task to select appropriate tools
3. Execute tools with LLM-generated inputs
4. Process results to determine next actions
5. Create new tasks or conclude when goals are met

This process is managed by the agent service layer and coordinated through a series of specialized prompt templates and tool implementations.

## Task Creation and Goal Decomposition

### Initial Task Generation

When an agent receives a high-level goal, the system uses the `start_goal_prompt` to decompose it into specific search queries or actionable tasks.

```mermaid
graph TD
    UserGoal["User Goal Input"] --> start_goal_prompt["start_goal_prompt"]
    start_goal_prompt --> LLM["Language Model"]
    LLM --> SearchQueries["JSON Array of Search Queries"]
    SearchQueries --> TaskQueue["Initial Task Queue"]
    
    start_goal_prompt -.-> PromptTemplate["PromptTemplate with goal, language variables"]
```

**Task Creation Process Flow**

```mermaid
sequenceDiagram
    participant Agent as "Agent Service"
    participant Prompt as "start_goal_prompt"
    participant LLM as "Language Model"
    participant TaskQueue as "Task Queue"
    
    Agent->>Prompt: format(goal, language)
    Prompt->>LLM: Generated prompt text
    LLM->>Agent: JSON array of search queries
    Agent->>TaskQueue: Add initial tasks
```

The `start_goal_prompt` implements plan-and-solve prompting methodology, limiting initial tasks to a maximum of 5 queries and ensuring they are succinct and actionable.

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:5-22]()

### Dynamic Task Creation

As agents execute tasks and receive results, they generate new tasks using the `create_tasks_prompt` to continue progress toward the goal.

```mermaid
graph LR
    CompletedTask["Completed Task"] --> create_tasks_prompt["create_tasks_prompt"]
    TaskResult["Task Result"] --> create_tasks_prompt
    IncompleTasks["Incomplete Tasks"] --> create_tasks_prompt
    Goal["Overall Goal"] --> create_tasks_prompt
    
    create_tasks_prompt --> LLM["Language Model"]
    LLM --> NewTask["Single New Task or Empty"]
    NewTask --> TaskQueue["Task Queue"]
```

The system creates only one new task at a time to maintain focused execution and prevent task explosion.

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:69-92]()

## Task Analysis and Tool Selection

### Task Analysis Process

Before executing each task, the agent analyzes it using the `analyze_task_prompt` to determine the most appropriate tool for execution.

```mermaid
graph TD
    CurrentTask["Current Task"] --> analyze_task_prompt["analyze_task_prompt"]
    HighLevelGoal["High Level Goal"] --> analyze_task_prompt
    analyze_task_prompt --> LLM["Language Model"]
    LLM --> FunctionSelection["Selected Function/Tool"]
    
    FunctionSelection --> get_tool_from_name["get_tool_from_name()"]
    get_tool_from_name --> ToolClass["Tool Class Instance"]
```

The analysis prompt ensures the agent selects the most efficient tool and includes reasoning in the specified language.

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:24-36](), [platform/reworkd_platform/web/api/agent/tools/tools.py:65-70]()

### Available Tools Mapping

The system maintains a registry of available tools through the tools module:

| Tool Class | Tool Name | Description | Primary Use Case |
|------------|-----------|-------------|------------------|
| `Search` | `search` | Google search via Serper API | Current events, factual information |
| `Code` | `code` | Code generation and review | Programming tasks, debugging |
| `Image` | `image` | AI image generation | Visual content creation |
| `Reason` | `reason` | Logical reasoning and analysis | Decision making, problem solving |
| `Conclude` | `conclude` | Task conclusion | Ending task execution |

**Tool Selection Architecture**

```mermaid
graph TD
    get_user_tools["get_user_tools(tool_names, user, crud)"] --> get_tool_from_name["get_tool_from_name()"]
    get_tool_from_name --> ToolRegistry["Tool Registry"]
    
    ToolRegistry --> Search["Search"]
    ToolRegistry --> Code["Code"] 
    ToolRegistry --> Image["Image"]
    ToolRegistry --> Reason["Reason"]
    ToolRegistry --> Conclude["Conclude"]
    
    get_default_tools["get_default_tools()"] --> Search
    get_external_tools["get_external_tools()"] --> Code
    get_external_tools --> Image
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tools.py:12-16](), [platform/reworkd_platform/web/api/agent/tools/tools.py:27-39]()

## Tool Execution

### Tool Interface

All tools implement the abstract `Tool` class with a standardized `call()` method signature:

```mermaid
classDiagram
    class Tool {
        <<abstract>>
        +description: str
        +public_description: str
        +arg_description: str
        +image_url: str
        +model: BaseChatModel
        +language: str
        +call(goal, task, input_str, user, oauth_crud) StreamingResponse*
        +available() bool
        +dynamic_available(user, oauth_crud) bool
    }
    
    Tool <|-- Search
    Tool <|-- Code
    Tool <|-- Image
    Tool <|-- Reason
    Tool <|-- Conclude
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tool.py:11-41]()

### Search Tool Execution

The `Search` tool performs web searches and processes results with source citations:

```mermaid
graph TD
    SearchCall["Search.call()"] --> _google_serper_search_results["_google_serper_search_results()"]
    _google_serper_search_results --> SerperAPI["Serper.dev API"]
    SerperAPI --> RawResults["Raw Search Results"]
    
    RawResults --> ProcessResults["Process Results"]
    ProcessResults --> CitedSnippet["CitedSnippet Objects"]
    CitedSnippet --> summarize_with_sources["summarize_with_sources()"]
    summarize_with_sources --> StreamingResponse["StreamingResponse"]
    
    SearchCall -.-> FallbackReason["Fallback to Reason tool on error"]
```

The search tool extracts answer boxes, organic results, and structured data, creating `CitedSnippet` objects with source URLs for proper attribution.

**Sources:** [platform/reworkd_platform/web/api/agent/tools/search.py:42-109](), [platform/reworkd_platform/web/api/agent/tools/utils.py:10-21]()

### Code Tool Execution

The `Code` tool generates programming solutions using specialized prompts:

```mermaid
graph TD
    CodeCall["Code.call()"] --> code_prompt["code_prompt"]
    code_prompt --> LLMChain["LLMChain"]
    LLMChain --> CodeGeneration["Generated Code with Comments"]
    CodeGeneration --> StreamingResponse["StreamingResponse"]
    
    code_prompt -.-> PromptVars["goal, language, task variables"]
```

The code prompt instructs the model to act as a world-class software engineer, providing bug-free code with explanations in the specified language.

**Sources:** [platform/reworkd_platform/web/api/agent/tools/code.py:10-25](), [platform/reworkd_platform/web/api/agent/prompts.py:38-56]()

### Image Tool Execution

The `Image` tool supports dual image generation backends with fallback logic:

```mermaid
graph TD
    ImageCall["Image.call()"] --> TryReplicate["Try get_replicate_image()"]
    TryReplicate --> ReplicateSuccess["Replicate Image URL"]
    TryReplicate --> ReplicateFail["RuntimeError"]
    
    ReplicateFail --> get_open_ai_image["get_open_ai_image()"]
    get_open_ai_image --> OpenAISuccess["OpenAI Image URL"]
    
    ReplicateSuccess --> FormatResponse["Format Markdown Image"]
    OpenAISuccess --> FormatResponse
    FormatResponse --> StreamingResponse["StreamingResponse"]
```

The tool prioritizes Replicate's Stable Diffusion model but falls back to OpenAI's DALL-E when Replicate is unavailable.

**Sources:** [platform/reworkd_platform/web/api/agent/tools/image.py:47-66](), [platform/reworkd_platform/web/api/agent/tools/image.py:15-32](), [platform/reworkd_platform/web/api/agent/tools/image.py:36-44]()

## Task Flow Control

### Execution Loop

The agent execution follows a controlled loop pattern with decision points for task continuation:

```mermaid
stateDiagram-v2
    [*] --> AnalyzeTask: New Task
    AnalyzeTask --> SelectTool: analyze_task_prompt
    SelectTool --> ExecuteTool: Tool Selection
    ExecuteTool --> ProcessResult: Tool Execution
    ProcessResult --> CreateNewTask: create_tasks_prompt
    ProcessResult --> ConcludeTask: No more tasks
    CreateNewTask --> AnalyzeTask: New Task Generated
    ConcludeTask --> [*]: Task Complete
    
    ExecuteTool --> HandleError: Tool Error
    HandleError --> FallbackReason: Use Reason tool
    FallbackReason --> ProcessResult
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/search.py:58-64]()

### Task Conclusion

Tasks conclude when the `Conclude` tool is selected or when the `create_tasks_prompt` returns no new tasks:

```mermaid
graph LR
    TaskComplete["Task Completed"] --> EvaluateProgress["Evaluate Progress"]
    EvaluateProgress --> NoMoreTasks["create_tasks_prompt returns empty"]
    EvaluateProgress --> SelectConclude["Select Conclude tool"]
    
    NoMoreTasks --> TaskConclusion["Task Execution Concluded"]
    SelectConclude --> ConcludeCall["Conclude.call()"]
    ConcludeCall --> TaskConclusion
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/conclude.py:9-15]()

## Results Processing and Summarization

### Result Summarization

The system processes task results through various summarization functions depending on the data type and source:

```mermaid
graph TD
    TaskResults["Task Results"] --> ResultType["Determine Result Type"]
    
    ResultType --> summarize["summarize()"]
    ResultType --> summarize_with_sources["summarize_with_sources()"]
    ResultType --> summarize_sid["summarize_sid()"]
    
    summarize --> summarize_prompt["summarize_prompt"]
    summarize_with_sources --> summarize_with_sources_prompt["summarize_with_sources_prompt"]
    summarize_sid --> summarize_sid_prompt["summarize_sid_prompt"]
    
    summarize_prompt --> LLMChain1["LLMChain"]
    summarize_with_sources_prompt --> LLMChain2["LLMChain"]
    summarize_sid_prompt --> LLMChain3["LLMChain"]
    
    LLMChain1 --> FormattedSummary["Formatted Summary"]
    LLMChain2 --> CitedSummary["Summary with Citations"]
    LLMChain3 --> FilteredSummary["Filtered Summary"]
```

The summarization system ensures results are formatted appropriately for the goal context and include proper source attribution when applicable.

**Sources:** [platform/reworkd_platform/web/api/agent/tools/utils.py:34-98](), [platform/reworkd_platform/web/api/agent/prompts.py:94-109](), [platform/reworkd_platform/web/api/agent/prompts.py:138-156](), [platform/reworkd_platform/web/api/agent/prompts.py:158-172]()

### Streaming Response Handling

All tool executions return `StreamingResponse` objects to provide real-time feedback to users through the frontend interface. This enables live updates as agents process tasks and generate results.

**Sources:** [platform/reworkd_platform/web/api/agent/tools/tool.py:33-41](), [platform/reworkd_platform/web/api/agent/tools/utils.py:44-52]()

---

# Page: Prompts and Output Parsing

# Prompts and Output Parsing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [platform/reworkd_platform/web/api/agent/helpers.py](platform/reworkd_platform/web/api/agent/helpers.py)
- [platform/reworkd_platform/web/api/agent/prompts.py](platform/reworkd_platform/web/api/agent/prompts.py)
- [platform/reworkd_platform/web/api/agent/task_output_parser.py](platform/reworkd_platform/web/api/agent/task_output_parser.py)
- [platform/reworkd_platform/web/api/agent/tools/code.py](platform/reworkd_platform/web/api/agent/tools/code.py)
- [platform/reworkd_platform/web/api/agent/tools/conclude.py](platform/reworkd_platform/web/api/agent/tools/conclude.py)
- [platform/reworkd_platform/web/api/agent/tools/image.py](platform/reworkd_platform/web/api/agent/tools/image.py)
- [platform/reworkd_platform/web/api/agent/tools/reason.py](platform/reworkd_platform/web/api/agent/tools/reason.py)
- [platform/reworkd_platform/web/api/agent/tools/search.py](platform/reworkd_platform/web/api/agent/tools/search.py)
- [platform/reworkd_platform/web/api/agent/tools/tool.py](platform/reworkd_platform/web/api/agent/tools/tool.py)
- [platform/reworkd_platform/web/api/agent/tools/tools.py](platform/reworkd_platform/web/api/agent/tools/tools.py)
- [platform/reworkd_platform/web/api/agent/tools/utils.py](platform/reworkd_platform/web/api/agent/tools/utils.py)
- [platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py](platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py)

</details>



This document covers the prompt template system and output parsing mechanisms used throughout the AgentGPT platform. It explains how natural language prompts are constructed, sent to language models, and how the responses are parsed and validated.

For information about how agents execute tasks using these prompts, see [Task Execution](#4.2). For details about the agent lifecycle that orchestrates prompt usage, see [Agent Lifecycle](#4.1).

## Prompt Template System

AgentGPT uses LangChain's `PromptTemplate` class to manage structured prompts with variable substitution. All prompt templates are centralized in the prompts module and support multilingual operation through language-specific formatting.

```mermaid
graph TD
    PromptTemplate["PromptTemplate"] --> StartGoal["start_goal_prompt"]
    PromptTemplate --> AnalyzeTask["analyze_task_prompt"] 
    PromptTemplate --> CodeGeneration["code_prompt"]
    PromptTemplate --> ExecuteTask["execute_task_prompt"]
    PromptTemplate --> CreateTasks["create_tasks_prompt"]
    PromptTemplate --> Summarize["summarize_prompt"]
    
    StartGoal --> TaskCreation["Task Creation"]
    AnalyzeTask --> ToolSelection["Tool Selection"]
    CodeGeneration --> CodeTool["Code Tool"]
    ExecuteTask --> ReasonTool["Reason Tool"]
    CreateTasks --> TaskGeneration["Task Generation"]
    Summarize --> ResultSummary["Result Summary"]
```

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:1-186]()

## Core Prompt Categories

### Goal Initialization Prompts

The `start_goal_prompt` transforms high-level objectives into actionable search queries using Plan-and-Solve prompting methodology:

| Variable | Purpose | Example |
|----------|---------|---------|
| `goal` | User's objective | "Analyze market trends for electric vehicles" |
| `language` | Response language | "English", "Spanish", etc. |

The prompt constrains output to JSON arrays with a maximum of 5 queries, ensuring structured responses that can be reliably parsed.

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:5-22]()

### Task Analysis and Tool Selection

The `analyze_task_prompt` enables agents to select appropriate tools for task execution:

```mermaid
graph LR
    TaskInput["Current Task"] --> AnalyzePrompt["analyze_task_prompt"]
    GoalContext["High Level Goal"] --> AnalyzePrompt
    AnalyzePrompt --> ToolSelection["Tool Selection Decision"]
    ToolSelection --> ToolExecution["Tool Execution"]
```

This prompt enforces mandatory tool selection and includes multilingual reasoning requirements.

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:24-36]()

### Specialized Tool Prompts

#### Code Generation
The `code_prompt` provides context-aware code generation with specific formatting requirements:
- Enforces markdown formatting with code blocks
- Requires step-by-step file-by-file approach
- Includes goal context for relevant code generation

#### Task Execution
The `execute_task_prompt` handles general reasoning and decision-making tasks when specialized tools aren't required.

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:38-67]()

### Task Management Prompts

#### Task Creation
The `create_tasks_prompt` generates new tasks based on completed work and remaining objectives:

```mermaid
graph TD
    CompletedTask["Last Completed Task"] --> CreatePrompt["create_tasks_prompt"]
    TaskResult["Task Result"] --> CreatePrompt
    IncompleteTasks["Incomplete Tasks"] --> CreatePrompt
    Goal["Overall Goal"] --> CreatePrompt
    CreatePrompt --> NewTask["Single New Task"]
    CreatePrompt --> NoTask["No Task (if complete)"]
```

#### Summarization
Multiple summarization prompts handle different content types:
- `summarize_prompt`: General text consolidation
- `summarize_with_sources_prompt`: Citation-aware summarization
- `summarize_sid_prompt`: Query-specific snippet processing

**Sources:** [platform/reworkd_platform/web/api/agent/prompts.py:69-172]()

## Output Parsing Architecture

### Task Output Parser

The `TaskOutputParser` extends LangChain's `BaseOutputParser` to handle task list extraction from LLM responses:

```mermaid
graph TD
    LLMResponse["LLM Response Text"] --> ExtractArray["extract_array()"]
    ExtractArray --> JSONArray["JSON Array"]
    ExtractArray --> MultilineString["Multiline String"]
    
    JSONArray --> FilterTasks["real_tasks_filter()"]
    MultilineString --> HandleMultiline["handle_multiline_string()"]
    HandleMultiline --> FilterTasks
    
    FilterTasks --> RemovePrefix["remove_prefix()"]
    RemovePrefix --> DeduplicateCompleted["Remove Completed Tasks"]
    DeduplicateCompleted --> FinalTasks["Final Task List"]
```

The parser handles multiple input formats:
- JSON arrays: `["task1", "task2"]`
- Numbered lists: `1. First task\n2. Second task`
- Mixed formats with prefixes and noise

**Sources:** [platform/reworkd_platform/web/api/agent/task_output_parser.py:8-89]()

### Parsing Helper Functions

#### Array Extraction
The `extract_array` function uses regex patterns to identify and extract array-like structures:

```python
regex = (
    r"\[\s*\]|"  # Empty array check
    r"(\[(?:\s*(?:\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\')\s*,?)*\s*\])"
)
```

#### Task Filtering
The `real_tasks_filter` function removes non-actionable responses using pattern matching:
- "No tasks required" patterns
- "Task complete" patterns  
- Empty or "do nothing" responses

**Sources:** [platform/reworkd_platform/web/api/agent/task_output_parser.py:41-88]()

## Error Handling and Validation

### Parse Exception Management

The `parse_with_handling` function wraps parser operations with consistent error handling:

```mermaid
graph TD
    Parser["BaseOutputParser.parse()"] --> Success["Parsed Result"]
    Parser --> OutputParserException["OutputParserException"]
    OutputParserException --> OpenAIError["OpenAIError with user message"]
    OpenAIError --> UserFeedback["User-friendly error message"]
```

### Model Interaction Error Handling

The `openai_error_handler` function provides comprehensive error management for LLM interactions:

| Error Type | Handling Strategy |
|------------|------------------|
| `ServiceUnavailableError` | Direct user to OpenAI status page |
| `InvalidRequestError` | Check model access and API key validity |
| `AuthenticationError` | Validate API key configuration |
| `RateLimitError` | Inform about quota limits and billing |

**Sources:** [platform/reworkd_platform/web/api/agent/helpers.py:19-77]()

## Integration with Agent Tools

### Tool-Specific Prompt Usage

Each tool integrates prompts differently based on its functionality:

```mermaid
graph TD
    SearchTool["Search Tool"] --> SummarizeWithSources["summarize_with_sources_prompt"]
    CodeTool["Code Tool"] --> CodePrompt["code_prompt"]
    ReasonTool["Reason Tool"] --> ExecutePrompt["execute_task_prompt"]
    ImageTool["Image Tool"] --> DirectExecution["Direct API Call"]
```

### Streaming Response Integration

Tools use `LLMChain` with prompts to generate streaming responses:

```python
chain = LLMChain(llm=self.model, prompt=execute_task_prompt)
return StreamingResponse.from_chain(
    chain,
    {"goal": goal, "language": self.language, "task": task},
    media_type="text/event-stream",
)
```

**Sources:** [platform/reworkd_platform/web/api/agent/tools/reason.py:16-27](), [platform/reworkd_platform/web/api/agent/tools/code.py:14-25]()

### Model Chain Execution

The `call_model_with_handling` function standardizes prompt execution across the system:

```mermaid
graph LR
    ModelChain["LLMChain Creation"] --> ErrorWrapper["openai_error_handler"]
    ErrorWrapper --> ChainExecution["chain.arun()"]
    ChainExecution --> Result["String Result"]
    ChainExecution --> Exception["Handled Exception"]
```

This ensures consistent error handling and logging across all prompt-based operations.

**Sources:** [platform/reworkd_platform/web/api/agent/helpers.py:68-77](), [platform/reworkd_platform/web/api/agent/tools/utils.py:34-99]()

---

# Page: Setup and Deployment

# Setup and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [cli/package-lock.json](cli/package-lock.json)
- [cli/package.json](cli/package.json)
- [cli/src/envGenerator.js](cli/src/envGenerator.js)
- [cli/src/helpers.js](cli/src/helpers.js)
- [cli/src/index.js](cli/src/index.js)
- [cli/src/questions/existingEnvQuestions.js](cli/src/questions/existingEnvQuestions.js)
- [cli/src/questions/newEnvQuestions.js](cli/src/questions/newEnvQuestions.js)
- [cli/src/questions/sharedQuestions.js](cli/src/questions/sharedQuestions.js)
- [docker-compose.yml](docker-compose.yml)
- [next/.husky/pre-commit](next/.husky/pre-commit)
- [next/entrypoint.sh](next/entrypoint.sh)
- [next/next.config.mjs](next/next.config.mjs)
- [next/public/locales/en/chat.missing.json](next/public/locales/en/chat.missing.json)
- [next/public/logos/panache-default-solid.svg](next/public/logos/panache-default-solid.svg)
- [next/public/logos/yc-default-solid.svg](next/public/logos/yc-default-solid.svg)
- [next/src/components/console/ExampleAgents.tsx](next/src/components/console/ExampleAgents.tsx)
- [next/src/env/schema.mjs](next/src/env/schema.mjs)
- [next/wait-for-db.sh](next/wait-for-db.sh)
- [platform/Dockerfile](platform/Dockerfile)
- [platform/entrypoint.sh](platform/entrypoint.sh)
- [setup.sh](setup.sh)

</details>



This document covers the setup, configuration, and deployment processes for the AgentGPT system. It includes automated CLI-based setup, Docker containerization, environment configuration, and database initialization procedures.

For information about the overall system architecture, see [System Architecture](#1.1). For details about environment-specific configuration variables, see [Environment Configuration](#5.1). For CLI tool usage, see [CLI Configuration](#5.3). For Docker-based deployment, see [Docker Deployment](#5.2).

## Deployment Architecture Overview

The AgentGPT system supports two primary deployment methods: automated Docker Compose deployment and manual setup. The deployment involves three main services: the Next.js frontend, Python FastAPI backend platform, and MySQL database.

**Deployment Architecture**

```mermaid
graph TB
    subgraph "Setup Process"
        SETUP_SH["setup.sh"]
        CLI_TOOL["CLI Tool"]
        ENV_GEN["envGenerator.js"]
    end
    
    subgraph "Docker Services"
        FRONTEND_SVC["frontend service"]
        PLATFORM_SVC["platform service"] 
        DB_SVC["agentgpt_db service"]
    end
    
    subgraph "Configuration Files"
        ENV_FILE[".env files"]
        DOCKER_COMPOSE["docker-compose.yml"]
        ENV_SCHEMA["schema.mjs"]
    end
    
    subgraph "Entry Points"
        FRONTEND_ENTRY["next/entrypoint.sh"]
        PLATFORM_ENTRY["platform/entrypoint.sh"]
        DB_WAIT["wait-for-db.sh"]
    end
    
    SETUP_SH --> CLI_TOOL
    CLI_TOOL --> ENV_GEN
    ENV_GEN --> ENV_FILE
    ENV_FILE --> DOCKER_COMPOSE
    
    DOCKER_COMPOSE --> FRONTEND_SVC
    DOCKER_COMPOSE --> PLATFORM_SVC
    DOCKER_COMPOSE --> DB_SVC
    
    FRONTEND_SVC --> FRONTEND_ENTRY
    PLATFORM_SVC --> PLATFORM_ENTRY
    FRONTEND_ENTRY --> DB_WAIT
    
    ENV_SCHEMA -.-> ENV_FILE
```

Sources: [setup.sh:1-9](), [cli/src/index.js:1-61](), [docker-compose.yml:1-59](), [next/entrypoint.sh:1-29](), [platform/entrypoint.sh:1-15]()

## Environment Configuration Process

The system uses a comprehensive environment configuration process managed by the CLI tool. The configuration includes API keys, database connections, authentication providers, and deployment-specific settings.

**Environment Configuration Flow**

```mermaid
flowchart TD
    START["Deployment Start"]
    CHECK_ENV{"doesEnvFileExist()"}
    NEW_ENV["handleNewEnv()"]
    EXISTING_ENV["handleExistingEnv()"]
    TEST_ENV["testEnvFile()"]
    PROMPT_NEW["newEnvQuestions"]
    PROMPT_EXISTING["existingEnvQuestions"]
    GENERATE["generateEnv()"]
    SAVE_ENV["saveEnvFile()"]
    RUN_OPTION["handleRunOption()"]
    
    START --> CHECK_ENV
    CHECK_ENV -->|false| NEW_ENV
    CHECK_ENV -->|true| EXISTING_ENV
    
    NEW_ENV --> PROMPT_NEW
    EXISTING_ENV --> TEST_ENV
    TEST_ENV --> PROMPT_EXISTING
    
    PROMPT_NEW --> GENERATE
    GENERATE --> SAVE_ENV
    SAVE_ENV --> RUN_OPTION
    PROMPT_EXISTING --> RUN_OPTION
    
    RUN_OPTION -->|"docker-compose"| DOCKER["Docker Compose Up"]
    RUN_OPTION -->|"manual"| MANUAL["Manual Instructions"]
```

Sources: [cli/src/index.js:54-61](), [cli/src/envGenerator.js:101-103](), [cli/src/envGenerator.js:5-21](), [cli/src/envGenerator.js:139-142]()

### Environment Variable Categories

The system organizes environment variables into logical categories defined in `getEnvDefinition()`:

| Category | Purpose | Key Variables |
|----------|---------|---------------|
| Deployment Environment | Runtime environment settings | `NODE_ENV`, `NEXT_PUBLIC_VERCEL_ENV` |
| NextJS | Frontend configuration | `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_MAX_LOOPS` |
| Next Auth config | Authentication setup | `NEXTAUTH_SECRET`, `NEXTAUTH_URL` |
| Auth providers | OAuth integration | `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, `DISCORD_CLIENT_ID` |
| Backend | Platform API configuration | `REWORKD_PLATFORM_OPENAI_API_KEY`, `REWORKD_PLATFORM_SERP_API_KEY` |
| Database (Backend) | Backend database connection | `REWORKD_PLATFORM_DATABASE_URL` |
| Database (Frontend) | Frontend database connection | `DATABASE_URL` |

Sources: [cli/src/envGenerator.js:23-76](), [.env.example:1-52]()

### Environment Validation

The CLI performs comprehensive validation for API keys including format checking and live API validation:

- **OpenAI API Key**: Validates format `/^sk-[a-zA-Z0-9]{48}$/` and tests against `https://api.openai.com/v1/models`
- **SERP API Key**: Validates format `/^[a-zA-Z0-9]{40}$/` and tests against `https://google.serper.dev/search`
- **Replicate API Key**: Validates format `/^r8_[a-zA-Z0-9]{37}$/` and tests against `https://api.replicate.com/v1/models`

Sources: [cli/src/questions/newEnvQuestions.js:12-30](), [cli/src/questions/newEnvQuestions.js:37-60](), [cli/src/questions/newEnvQuestions.js:67-85]()

## Docker Service Configuration

The Docker Compose configuration defines three interconnected services with specific dependencies and networking requirements.

**Docker Service Dependencies**

```mermaid
graph LR
    subgraph "Container Network"
        FRONTEND_CONTAINER["frontend:3000"]
        PLATFORM_CONTAINER["platform:8000"] 
        DB_CONTAINER["agentgpt_db:3307"]
    end
    
    subgraph "Volume Mounts"
        NEXT_VOL["./next/:/next/"]
        PLATFORM_VOL["./platform:/app/src/"]
        DB_VOL["agentgpt_db:/var/lib/mysql"]
    end
    
    subgraph "Environment Sources"
        ENV_FILE_MOUNT["./next/.env"]
        DB_ENV["MySQL Environment"]
    end
    
    PLATFORM_CONTAINER --> DB_CONTAINER
    FRONTEND_CONTAINER -.-> PLATFORM_CONTAINER
    
    FRONTEND_CONTAINER --> NEXT_VOL
    PLATFORM_CONTAINER --> PLATFORM_VOL
    DB_CONTAINER --> DB_VOL
    
    FRONTEND_CONTAINER --> ENV_FILE_MOUNT
    PLATFORM_CONTAINER --> ENV_FILE_MOUNT
    DB_CONTAINER --> DB_ENV
```

Sources: [docker-compose.yml:4-16](), [docker-compose.yml:17-37](), [docker-compose.yml:39-55]()

### Service Configurations

**Frontend Service** (`frontend`):
- Built from `./next/Dockerfile`
- Exposes port `3000:3000`
- Mounts environment file at `/next/.env`
- Excludes `node_modules` and `.next` from volume mounts

**Platform Service** (`platform`):
- Built from `./platform/Dockerfile` with `prod` target
- Exposes port `8000:8000`
- Depends on `agentgpt_db` service
- Uses environment file from `next/.env`
- Configures database connection via environment variables

**Database Service** (`agentgpt_db`):
- Uses `mysql:8.0` image
- Exposes port `3308:3307` (non-standard MySQL port)
- Configures UTF8MB4 character set
- Persistent volume storage

Sources: [docker-compose.yml:4-16](), [docker-compose.yml:17-37](), [docker-compose.yml:39-55]()

## Database Initialization Process

The system implements a multi-stage database initialization process with dependency checking and schema migration.

**Database Initialization Sequence**

```mermaid
sequenceDiagram
    participant Frontend as "Frontend Container"
    participant Platform as "Platform Container" 
    participant Database as "agentgpt_db"
    participant WaitScript as "wait-for-db.sh"
    participant Prisma as "Prisma CLI"
    
    Platform->>Database: Check connection (nc agentgpt_db 3306)
    Database-->>Platform: Connection available
    
    Frontend->>WaitScript: Execute wait-for-db.sh agentgpt_db 3307
    WaitScript->>Database: SELECT 1 query
    Database-->>WaitScript: Response received
    WaitScript-->>Frontend: Database ready
    
    Frontend->>Prisma: npx prisma migrate deploy
    Prisma->>Database: Apply migrations
    Database-->>Prisma: Migration complete
    
    Frontend->>Prisma: npx prisma db push
    Prisma->>Database: Push schema changes
    Database-->>Prisma: Schema updated
    
    Frontend->>Prisma: npx prisma generate
    Prisma-->>Frontend: Client generated
```

Sources: [next/entrypoint.sh:15-26](), [next/wait-for-db.sh:1-12](), [platform/entrypoint.sh:3-14]()

### Database Connection Configuration

The database connection uses different ports for internal Docker networking versus external access:

- **Internal Docker Network**: Port `3307` (configured in `MYSQL_TCP_PORT`)
- **External Host Access**: Port `3308` (mapped from container port `3307`)
- **Database Name**: `reworkd_platform`
- **Credentials**: `reworkd_platform:reworkd_platform`

Sources: [docker-compose.yml:46-52](), [.env.example:37-43]()

## Manual Deployment Process

For manual deployment, the system provides instructions for running services independently outside of Docker containers.

### Manual Setup Requirements

1. **Frontend Setup**:
   ```bash
   cd ./next
   npm install && npm run dev
   ```

2. **Backend Setup**:
   ```bash
   cd ./platform
   poetry install && poetry run python -m reworkd_platform
   ```

3. **Database Setup**: Configure MySQL instance with credentials from environment file

Sources: [cli/src/index.js:41-51]()

### Environment Schema Validation

The Next.js application validates environment variables using Zod schemas defined in `schema.mjs`:

**Server Schema** includes:
- `DATABASE_URL`: Database connection string
- `NEXTAUTH_SECRET`: Authentication secret (required in production)
- OAuth provider credentials (`GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, etc.)

**Client Schema** includes:
- `NEXT_PUBLIC_BACKEND_URL`: Backend API endpoint
- `NEXT_PUBLIC_MAX_LOOPS`: Agent execution limit
- `NEXT_PUBLIC_FF_MOCK_MODE_ENABLED`: Mock mode feature flag

Sources: [next/src/env/schema.mjs:17-36](), [next/src/env/schema.mjs:63-73]()

## Post-Deployment Verification

After successful deployment, the system provides these endpoints for verification:

- **Frontend**: `http://localhost:3000` (Next.js application)
- **Backend API**: `http://localhost:8000` (FastAPI platform)
- **Database**: `localhost:3308` (MySQL external access)

The CLI tool automatically validates API key connectivity during setup, ensuring external service integration is functional before deployment completion.

Sources: [cli/src/questions/newEnvQuestions.js:19-28](), [docker-compose.yml:9-10](), [docker-compose.yml:22-23](), [docker-compose.yml:45-46]()

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [cli/package-lock.json](cli/package-lock.json)
- [cli/package.json](cli/package.json)
- [cli/src/envGenerator.js](cli/src/envGenerator.js)
- [cli/src/helpers.js](cli/src/helpers.js)
- [cli/src/index.js](cli/src/index.js)
- [cli/src/questions/existingEnvQuestions.js](cli/src/questions/existingEnvQuestions.js)
- [cli/src/questions/newEnvQuestions.js](cli/src/questions/newEnvQuestions.js)
- [cli/src/questions/sharedQuestions.js](cli/src/questions/sharedQuestions.js)
- [docker-compose.yml](docker-compose.yml)
- [next/next.config.mjs](next/next.config.mjs)
- [next/public/logos/panache-default-solid.svg](next/public/logos/panache-default-solid.svg)
- [next/public/logos/yc-default-solid.svg](next/public/logos/yc-default-solid.svg)
- [next/src/components/console/ExampleAgents.tsx](next/src/components/console/ExampleAgents.tsx)
- [next/src/env/schema.mjs](next/src/env/schema.mjs)

</details>



This document covers the environment configuration system for AgentGPT, including the automated CLI setup tool, manual configuration options, and environment variable validation. The system requires configuration of API keys, database connections, authentication providers, and deployment settings.

For information about Docker deployment specifically, see [Docker Deployment](#5.2). For CLI tool usage beyond environment setup, see [CLI Configuration](#5.3).

## Environment Variable Categories

AgentGPT requires configuration across multiple service layers, each with distinct environment variable requirements:

### Platform Configuration
- **Maximum Loops**: Controls agent execution limits (`NEXT_PUBLIC_MAX_LOOPS`, `REWORKD_PLATFORM_MAX_LOOPS`)
- **Environment Mode**: Development, test, or production (`NODE_ENV`, `NEXT_PUBLIC_VERCEL_ENV`)

### API Service Keys
- **OpenAI API**: Required for core agent functionality (`REWORKD_PLATFORM_OPENAI_API_KEY`)
- **Search Services**: SERP API for web search capabilities (`REWORKD_PLATFORM_SERP_API_KEY`)
- **Image Generation**: Replicate API for image creation (`REWORKD_PLATFORM_REPLICATE_API_KEY`)

### Database Configuration
Separate database configurations for frontend and backend services with identical connection parameters but different variable prefixes.

### Authentication Services
- **NextAuth**: Session management (`NEXTAUTH_SECRET`, `NEXTAUTH_URL`)
- **OAuth Providers**: Google, GitHub, Discord client credentials

**Sources**: [.env.example:1-52](), [cli/src/envGenerator.js:23-76]()

## CLI-Based Environment Generation

The AgentGPT CLI provides an interactive setup process that automatically generates properly configured environment files:

```mermaid
graph TD
    CLI_START["`CLI Startup
    cli/src/index.js`"] --> ENV_CHECK{"`Environment File
    Exists?`"}
    
    ENV_CHECK -->|Yes| VALIDATE["`Validate Existing
    testEnvFile()`"]
    ENV_CHECK -->|No| NEW_ENV["`Interactive Setup
    newEnvQuestions`"]
    
    VALIDATE --> VALID{Valid?}
    VALID -->|Yes| RUN_OPTS["`Choose Run Option
    existingEnvQuestions`"]
    VALID -->|No| ERROR_MSG["`Display Missing Keys
    Error Message`"]
    
    NEW_ENV --> API_VALIDATION["`API Key Validation
    OpenAI, SERP, Replicate`"]
    API_VALIDATION --> ENV_GEN["`Generate Config
    generateEnv()`"]
    
    ENV_GEN --> WRITE_FILES["`Write Files
    ./next/.env
    ./platform/.env`"]
    
    RUN_OPTS --> DOCKER_OPTION{"`Docker Compose
    Selected?`"}
    WRITE_FILES --> DOCKER_OPTION
    
    DOCKER_OPTION -->|Yes| DOCKER_UP["`docker-compose up
    --build`"]
    DOCKER_OPTION -->|No| MANUAL_SETUP["`Manual Setup
    Instructions`"]
```

The CLI performs real-time API key validation by making test requests to verify credentials before generating the environment files.

**Sources**: [cli/src/index.js:1-61](), [cli/src/envGenerator.js:5-21](), [cli/src/questions/newEnvQuestions.js:1-87]()

## Environment File Structure

The CLI generates environment files following a structured format with categorized sections:

| Section | Variables | Purpose |
|---------|-----------|---------|
| Deployment Environment | `NODE_ENV`, `NEXT_PUBLIC_VERCEL_ENV` | Runtime environment detection |
| NextJS | `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_MAX_LOOPS` | Frontend configuration |
| Next Auth | `NEXTAUTH_SECRET`, `NEXTAUTH_URL` | Authentication configuration |
| Auth Providers | Google, GitHub, Discord credentials | OAuth integration |
| Backend | Platform service configuration | Python FastAPI backend |
| Database (Backend) | `REWORKD_PLATFORM_DATABASE_*` | Backend database connection |
| Database (Frontend) | `DATABASE_*` | Frontend database connection |

The `generateEnvFileContent` function creates the final configuration by iterating through the structured definition and formatting key-value pairs with section comments.

**Sources**: [cli/src/envGenerator.js:78-90](), [cli/src/envGenerator.js:23-76]()

## Environment Validation

### Frontend Schema Validation

The Next.js frontend uses Zod schemas for environment variable validation:

```mermaid
graph LR
    SERVER_SCHEMA["`serverSchema
    next/src/env/schema.mjs`"] --> SERVER_VARS["`Server Variables
    DATABASE_URL
    NEXTAUTH_SECRET
    OAuth Credentials`"]
    
    CLIENT_SCHEMA["`clientSchema
    next/src/env/schema.mjs`"] --> CLIENT_VARS["`Client Variables
    NEXT_PUBLIC_*
    Feature Flags`"]
    
    SERVER_VARS --> VALIDATION["`Runtime Validation
    serverEnv object`"]
    CLIENT_VARS --> VALIDATION
    
    VALIDATION --> BUILD_CHECK["`Build-time Check
    next.config.mjs`"]
```

The validation system distinguishes between server-side and client-side environment variables, with client variables requiring the `NEXT_PUBLIC_` prefix for browser exposure.

**Sources**: [next/src/env/schema.mjs:17-36](), [next/src/env/schema.mjs:63-73](), [next/next.config.mjs:8]()

### CLI Validation Process

The CLI includes comprehensive validation for existing environment files:

```mermaid
graph TD
    EXISTING_ENV["`Existing .env File
    doesEnvFileExist()`"] --> READ_FILE["`Read File Content
    testEnvFile()`"]
    
    READ_FILE --> PARSE_LINES["`Parse Non-comment Lines
    Split by '='`"]
    PARSE_LINES --> EXTRACT_KEYS["`Extract Environment Keys
    From File`"]
    
    FAKE_DEF["`Generate Reference Definition
    getEnvDefinition()`"] --> REF_KEYS["`Extract Reference Keys
    From Definition`"]
    
    EXTRACT_KEYS --> COMPARE["`Compare Key Sets
    Find Missing Keys`"]
    REF_KEYS --> COMPARE
    
    COMPARE --> MISSING{"`Missing Keys
    Found?`"}
    MISSING -->|Yes| ERROR["`Display Error Message
    Recommend File Deletion`"]
    MISSING -->|No| PROCEED["`Proceed with Existing Config`"]
```

**Sources**: [cli/src/envGenerator.js:106-137](), [cli/src/envGenerator.js:101-103]()

## Docker Environment Integration

Docker Compose orchestrates environment configuration across multiple services:

```mermaid
graph TB
    ENV_FILE["`Environment File
    next/.env`"] --> FRONTEND_SVC["`Frontend Service
    frontend container`"]
    ENV_FILE --> PLATFORM_SVC["`Platform Service
    platform container`"]
    
    PLATFORM_SVC --> DB_OVERRIDE["`Database Override
    REWORKD_PLATFORM_DB_*`"]
    DB_OVERRIDE --> MYSQL_SVC["`MySQL Service
    agentgpt_db container`"]
    
    FRONTEND_SVC --> PORT_3000["`Port 3000
    Next.js Application`"]
    PLATFORM_SVC --> PORT_8000["`Port 8000
    FastAPI Backend`"]
    MYSQL_SVC --> PORT_3308["`Port 3308
    External MySQL Access`"]
    
    subgraph "Container Network"
        FRONTEND_SVC
        PLATFORM_SVC
        MYSQL_SVC
    end
```

The Docker configuration overrides specific database connection parameters to use container networking while maintaining the base environment file structure.

**Sources**: [docker-compose.yml:27-35](), [docker-compose.yml:47-52]()

## Configuration Files and Paths

The system maintains multiple configuration files across different service layers:

| File Path | Purpose | Generated By |
|-----------|---------|--------------|
| `next/.env` | Frontend environment variables | CLI or manual |
| `platform/.env` | Backend environment variables | CLI (copy of frontend) |
| `next/src/env/schema.mjs` | Environment validation schema | Manual |
| `.env.example` | Template and documentation | Manual |

Both `next/.env` and `platform/.env` contain identical content, as the CLI writes the same configuration to both locations using `saveEnvFile`.

**Sources**: [cli/src/envGenerator.js:98-99](), [cli/src/envGenerator.js:139-142]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [cli/src/envGenerator.js](cli/src/envGenerator.js)
- [docker-compose.yml](docker-compose.yml)
- [next/.husky/pre-commit](next/.husky/pre-commit)
- [next/entrypoint.sh](next/entrypoint.sh)
- [next/next.config.mjs](next/next.config.mjs)
- [next/public/locales/en/chat.missing.json](next/public/locales/en/chat.missing.json)
- [next/public/logos/panache-default-solid.svg](next/public/logos/panache-default-solid.svg)
- [next/public/logos/yc-default-solid.svg](next/public/logos/yc-default-solid.svg)
- [next/src/components/console/ExampleAgents.tsx](next/src/components/console/ExampleAgents.tsx)
- [next/src/env/schema.mjs](next/src/env/schema.mjs)
- [next/wait-for-db.sh](next/wait-for-db.sh)
- [platform/Dockerfile](platform/Dockerfile)
- [platform/entrypoint.sh](platform/entrypoint.sh)
- [setup.sh](setup.sh)

</details>



This document provides detailed instructions for deploying the AgentGPT system using Docker and Docker Compose. Docker allows for consistent deployment across different environments by containerizing the application components. This guide covers both automated setup using the provided CLI tool and manual Docker deployment configurations.

For environment configuration details not specific to Docker, see [Environment Configuration](#5.1).

## Prerequisites

Before deploying AgentGPT with Docker, ensure you have the following installed:

- [Docker](https://www.docker.com/products/docker-desktop) (latest version)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)
- [Git](https://git-scm.com/downloads) for cloning the repository
- API keys:
  - An [OpenAI API key](https://platform.openai.com/signup) (required)
  - A [Serper API Key](https://serper.dev/signup) (optional)
  - A [Replicate API Token](https://replicate.com/signin) (optional)

Sources: [README.md:46-56](). [.env.example:27-32]()

## Docker Architecture

The AgentGPT system is containerized using Docker Compose with three main services:

```mermaid
flowchart TD
    subgraph "AgentGPT Docker Architecture"
        User[/"User Browser"/] <--> |"Port 3000"| Frontend["frontend container\n(Next.js)"]
        Frontend <--> |"Port 8000"| Platform["platform container\n(FastAPI)"]
        Platform <--> |"Port 3307"| DB[("agentgpt_db\n(MySQL 8.0)")]
        
        subgraph "Volumes"
            ENV[".env file"] --> Frontend
            ENV --> Platform
            DBVol["agentgpt_db volume"] --> DB
            SourceCode["Source code mounts"] --> Frontend
            SourceCode --> Platform
        end
    end
```

### Docker Compose Services

The [docker-compose.yml:1-59]() file defines three interconnected services:

| Service | Container Name | Base Image | Port Mapping | Key Environment Variables |
|---------|----------------|------------|--------------|--------------------------|
| frontend | frontend | Custom Next.js build | 3000:3000 | NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 |
| platform | platform | python:3.11-slim-buster | 8000:8000 | REWORKD_PLATFORM_HOST=0.0.0.0<br>REWORKD_PLATFORM_DB_HOST=agentgpt_db |
| agentgpt_db | agentgpt_db | mysql:8.0 | 3308:3307 | MYSQL_DATABASE=reworkd_platform<br>MYSQL_TCP_PORT=3307 |

#### Volume Mounts and Dependencies

```mermaid
graph TD
    subgraph "Docker Compose Configuration"
        frontend["frontend container"] --> env_file["./next/.env"]
        frontend --> next_src["./next/ source mount"]
        frontend --> node_modules["/next/node_modules (excluded)"]
        
        platform["platform container"] --> platform_src["./platform:/app/src/"]
        platform --> platform_env["env_file: next/.env"]
        
        agentgpt_db["agentgpt_db container"] --> db_volume["agentgpt_db:/var/lib/mysql"]
        
        platform -.->|"depends_on"| agentgpt_db
    end
```

Sources: [docker-compose.yml:4-58]()

## Container Initialization Flow

```mermaid
sequenceDiagram
    participant User
    participant setup_sh as "setup.sh"
    participant envGenerator as "cli/envGenerator.js"
    participant docker_compose as "docker-compose"
    participant agentgpt_db as "agentgpt_db container"
    participant platform as "platform container"
    participant frontend as "frontend container"

    User->>setup_sh: Execute ./setup.sh
    setup_sh->>envGenerator: npm run start
    envGenerator->>envGenerator: generateEnv() with docker-compose config
    envGenerator->>envGenerator: Set DATABASE_HOST=agentgpt_db, PORT=3307
    
    User->>docker_compose: docker-compose up -d
    docker_compose->>agentgpt_db: Start MySQL with MYSQL_TCP_PORT=3307
    docker_compose->>platform: Start with entrypoint.sh
    platform->>platform: Wait for agentgpt_db:3306 connection
    docker_compose->>frontend: Start with entrypoint.sh
    
    frontend->>frontend: ./wait-for-db.sh agentgpt_db 3307
    frontend->>frontend: npx prisma migrate deploy
    frontend->>frontend: npx prisma db push
    frontend->>frontend: npx prisma generate
    frontend-->>User: Next.js serves on port 3000
    platform-->>User: FastAPI serves on port 8000
```

Sources: [setup.sh:6-8](), [cli/src/envGenerator.js:6-20](), [next/entrypoint.sh:16-25](), [platform/entrypoint.sh:3-14]()

## Automated Setup with CLI

The easiest way to deploy AgentGPT with Docker is using the provided setup script:

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/reworkd/AgentGPT.git
cd AgentGPT
```

2. Run the setup script:

```bash
# For Mac/Linux
./setup.sh

# For Windows
./setup.bat
```

3. Follow the CLI prompts to configure your environment:
   - When asked about the run option, select "docker-compose"
   - Enter your API keys as prompted
   - The CLI will generate the necessary `.env` file and start the Docker containers

Sources: [README.md:57-77](). [cli/src/envGenerator.js:5-142]()

## Manual Docker Deployment

If you prefer to set up manually or need more control over the deployment:

1. Clone the repository:

```bash
git clone https://github.com/reworkd/AgentGPT.git
cd AgentGPT
```

2. Create a `.env` file in the `next` directory based on the `.env.example` file.

3. Make sure the Docker-specific environment variables are properly configured:

```
# Database (Backend):
REWORKD_PLATFORM_DATABASE_USER="reworkd_platform"
REWORKD_PLATFORM_DATABASE_PASSWORD="reworkd_platform"
REWORKD_PLATFORM_DATABASE_HOST="agentgpt_db"
REWORKD_PLATFORM_DATABASE_PORT="3307"
REWORKD_PLATFORM_DATABASE_NAME="reworkd_platform"

# Database (Frontend):
DATABASE_USER="reworkd_platform"
DATABASE_PASSWORD="reworkd_platform"
DATABASE_HOST="agentgpt_db"
DATABASE_PORT="3307"
DATABASE_NAME="reworkd_platform"
```

4. Start the Docker containers:

```bash
docker-compose up -d
```

5. Access the application at http://localhost:3000

Sources: [.env.example:37-51](). [docker-compose.yml:1-59]()

## Environment Configuration for Docker

## Docker-Specific Environment Configuration

The [cli/src/envGenerator.js:23-76]() `getEnvDefinition()` function generates Docker-specific environment variables when `envValues.runOption === "docker-compose"`:

### Key Docker Environment Variables

| Variable | Docker Value | Local Value | Code Reference |
|----------|--------------|-------------|----------------|
| REWORKD_PLATFORM_DATABASE_HOST | agentgpt_db | localhost | [cli/src/envGenerator.js:60]() |
| REWORKD_PLATFORM_DATABASE_PORT | 3307 | 3306 | [cli/src/envGenerator.js:7,61]() |
| DATABASE_HOST | agentgpt_db | localhost | [cli/src/envGenerator.js:69]() |
| DATABASE_PORT | 3307 | 3306 | [cli/src/envGenerator.js:7,70]() |
| NEXT_PUBLIC_BACKEND_URL | http://localhost:8000 | http://localhost:8000 | [cli/src/envGenerator.js:30]() |

### Environment Variable Generation Logic

```mermaid
flowchart TD
    subgraph "cli/src/envGenerator.js Environment Logic"
        generateEnv["generateEnv(envValues)"] --> check_docker{"envValues.runOption === 'docker-compose'"}
        check_docker -->|"true"| docker_config["isDockerCompose = true<br>dbPort = 3307<br>platformUrl = http://host.docker.internal:8000"]
        check_docker -->|"false"| local_config["isDockerCompose = false<br>dbPort = 3306<br>platformUrl = http://localhost:8000"]
        
        docker_config --> get_env_def["getEnvDefinition()"]
        local_config --> get_env_def
        get_env_def --> backend_db_config["REWORKD_PLATFORM_DATABASE_HOST: 'agentgpt_db'"]
        get_env_def --> frontend_db_config["DATABASE_HOST: 'agentgpt_db'"]
        get_env_def --> generate_content["generateEnvFileContent()"]
        generate_content --> save_files["saveEnvFile() -> next/.env & platform/.env"]
    end
```

The `agentgpt_db` hostname resolves to the MySQL container through Docker's internal networking, while port 3307 is used internally within the Docker network.

Sources: [cli/src/envGenerator.js:6-20](), [cli/src/envGenerator.js:57-74](), [docker-compose.yml:40-52]()

## Docker Container Details

### Frontend Container Initialization

The frontend container executes [next/entrypoint.sh:1-29]() which orchestrates database connectivity and Prisma setup:

#### Frontend Container Startup Process

```mermaid
flowchart TD
    subgraph "Frontend Container (next/entrypoint.sh)"
        entrypoint_start["#!/usr/bin/env sh"] --> dos2unix_wait["dos2unix wait-for-db.sh"]
        dos2unix_wait --> copy_env["Copy .env.example if .env missing"]
        copy_env --> source_env["source .env"]
        source_env --> wait_for_db["./wait-for-db.sh agentgpt_db 3307"]
        wait_for_db --> prisma_check{"Check if DATABASE_URL exists"}
        prisma_check -->|"Not exists"| prisma_migrate["npx prisma migrate deploy --name init"]
        prisma_migrate --> prisma_push["npx prisma db push"]
        prisma_push --> prisma_generate["npx prisma generate"]
        prisma_check -->|"Exists"| prisma_generate
        prisma_generate --> exec_cmd["exec \"$@\""]
    end
    
    subgraph "wait-for-db.sh Script"
        wait_loop["nc $host $port"] --> wait_sleep["sleep 2"]
        wait_sleep --> wait_loop
        wait_loop -->|"Connection successful"| db_ready["Database available"]
    end
```

The [next/wait-for-db.sh:6-9]() script uses `nc` (netcat) to test database connectivity before proceeding with Prisma operations.

Sources: [next/entrypoint.sh:4-28](), [next/wait-for-db.sh:6-11]()

### Platform Container Build and Runtime

The platform container is built using [platform/Dockerfile:1-38]() with a multi-stage approach and executes the FastAPI backend service.

#### Multi-Stage Dockerfile Build Process

```mermaid
flowchart TD
    subgraph "platform/Dockerfile Multi-Stage Build"
        base["FROM python:3.11-slim-buster as prod"] --> apt_install["apt-get install mysql, gcc, openjdk-11-jdk"]
        apt_install --> poetry_install["pip install poetry==1.4.2"]
        poetry_install --> poetry_config["poetry config virtualenvs.create false"]
        poetry_config --> copy_pyproject["COPY pyproject.toml /app/src/"]
        copy_pyproject --> poetry_main["poetry install --only main"]
        poetry_main --> apt_purge["apt-get purge gcc, g++"]
        apt_purge --> copy_app["COPY . /app/src/"]
        copy_app --> cmd_python["CMD python -m reworkd_platform"]
        
        cmd_python --> dev_stage["FROM prod as dev"]
        dev_stage --> poetry_dev["poetry install (all dependencies)"]
    end
```

#### Platform Container Runtime

The platform container uses [platform/entrypoint.sh:3-14]() to ensure database connectivity:

```mermaid
flowchart TD
    subgraph "Platform Container Runtime"
        entrypoint_start["#!/usr/bin/env sh"] --> set_vars["host=agentgpt_db, port=3306"]
        set_vars --> nc_loop["nc $host $port connection test"]
        nc_loop -->|"Failed"| sleep_2["sleep 2"]
        sleep_2 --> nc_loop
        nc_loop -->|"Success"| db_available["Database available"]
        db_available --> exec_cmd["exec \"$@\""]
        exec_cmd --> python_main["python -m reworkd_platform"]
    end
```

Note: The platform entrypoint tests port 3306 while the actual MySQL container runs on port 3307 internally. This is handled by Docker networking.

Sources: [platform/Dockerfile:1-33](), [platform/entrypoint.sh:3-14](), [docker-compose.yml:30-35]()

### Database Container

The database container runs MySQL 8.0 and:
- Stores data in a persistent volume
- Uses port 3307 inside Docker and maps to 3308 on the host
- Initializes with the reworkd_platform database and user

## Troubleshooting Docker Deployment

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Cannot connect to database | Database container not started | Ensure `docker-compose ps` shows the database container running |
| | Wrong database connection parameters | Check DATABASE_HOST and REWORKD_PLATFORM_DATABASE_HOST are set to "agentgpt_db" |
| Frontend can't connect to backend | Backend container not running | Check if platform container is running with `docker-compose ps` |
| | Incorrect NEXT_PUBLIC_BACKEND_URL | Ensure it's set to "http://localhost:8000" |
| Container exits immediately | Missing environment variables | Verify .env file exists and is properly formatted |
| | Permission issues with mounted volumes | Check file permissions on mounted directories |

### Viewing Container Logs

To view logs for troubleshooting:

```bash
# View logs for all containers
docker-compose logs

# View logs for a specific container
docker-compose logs frontend
docker-compose logs platform
docker-compose logs agentgpt_db
```

### Rebuilding Containers

If you make changes to the codebase or configuration:

```bash
# Rebuild and restart containers
docker-compose up -d --build

# Restart a specific container
docker-compose restart frontend
```

Sources: [README.md:36-49](). [docker-compose.yml:1-59]()

## Summary

Docker deployment provides a consistent and isolated environment for running AgentGPT. The system consists of three main containers (frontend, backend, and database) orchestrated by Docker Compose. Using the provided setup script automates much of the configuration process, including environment variable setup and container initialization.

For more details on CLI configuration options, refer to [CLI Configuration](#5.3).

---

# Page: CLI Configuration

# CLI Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/package-lock.json](cli/package-lock.json)
- [cli/package.json](cli/package.json)
- [cli/src/helpers.js](cli/src/helpers.js)
- [cli/src/index.js](cli/src/index.js)
- [cli/src/questions/existingEnvQuestions.js](cli/src/questions/existingEnvQuestions.js)
- [cli/src/questions/newEnvQuestions.js](cli/src/questions/newEnvQuestions.js)
- [cli/src/questions/sharedQuestions.js](cli/src/questions/sharedQuestions.js)

</details>



This document covers the AgentGPT command-line interface (CLI) tool, which provides automated setup and configuration for the development environment. The CLI handles environment file generation, API key validation, and deployment option selection. For information about environment variables and configuration files, see [Environment Configuration](#5.1). For Docker deployment details, see [Docker Deployment](#5.2).

## Overview

The AgentGPT CLI is a Node.js-based command-line tool that streamlines the initial setup process by generating required environment files and configuring the system for deployment. It provides an interactive experience for collecting API keys, validating credentials, and choosing deployment methods.

**CLI Execution Flow**

```mermaid
flowchart TD
    START["CLI Start"] --> PRINT_TITLE["printTitle()"]
    PRINT_TITLE --> CHECK_ENV["doesEnvFileExist()"]
    CHECK_ENV -->|true| HANDLE_EXISTING["handleExistingEnv()"]
    CHECK_ENV -->|false| HANDLE_NEW["handleNewEnv()"]
    
    HANDLE_EXISTING --> VALIDATE["testEnvFile()"]
    VALIDATE --> EXISTING_PROMPT["inquirer.prompt(existingEnvQuestions)"]
    EXISTING_PROMPT --> RUN_OPTION["handleRunOption()"]
    
    HANDLE_NEW --> NEW_PROMPT["inquirer.prompt(newEnvQuestions)"]
    NEW_PROMPT --> GENERATE_ENV["generateEnv(answers)"]
    GENERATE_ENV --> RUN_OPTION
    
    RUN_OPTION -->|docker-compose| DOCKER_SPAWN["spawn('docker-compose', ['up', '--build'])"]
    RUN_OPTION -->|manual| MANUAL_INSTRUCTIONS["Console output with manual setup steps"]
    
    DOCKER_SPAWN --> END["Process Complete"]
    MANUAL_INSTRUCTIONS --> END
```

Sources: [cli/src/index.js:1-61]()

## CLI Architecture and Components

The CLI is structured as a modular Node.js application with clear separation of concerns between user interaction, validation, and system integration.

**CLI Component Structure**

```mermaid
graph TD
    subgraph "Entry Point"
        INDEX["index.js"]
    end
    
    subgraph "User Interface"
        HELPERS["helpers.js"]
        PRINT_TITLE["printTitle()"]
        VALID_KEY["isValidKey()"]
    end
    
    subgraph "Question Modules"
        NEW_ENV_Q["newEnvQuestions.js"]
        EXISTING_ENV_Q["existingEnvQuestions.js"]
        SHARED_Q["sharedQuestions.js"]
        RUN_OPTION_Q["RUN_OPTION_QUESTION"]
    end
    
    subgraph "Environment Management"
        ENV_GEN["envGenerator.js"]
        DOES_EXIST["doesEnvFileExist()"]
        GENERATE_ENV["generateEnv()"]
        TEST_ENV["testEnvFile()"]
    end
    
    subgraph "External Dependencies"
        INQUIRER["inquirer"]
        FIGLET["figlet"]
        CHALK["chalk"]
        DOTENV["dotenv"]
        SPAWN["child_process.spawn"]
    end
    
    INDEX --> PRINT_TITLE
    INDEX --> DOES_EXIST
    INDEX --> GENERATE_ENV
    INDEX --> TEST_ENV
    
    PRINT_TITLE --> FIGLET
    PRINT_TITLE --> CHALK
    
    NEW_ENV_Q --> VALID_KEY
    NEW_ENV_Q --> RUN_OPTION_Q
    EXISTING_ENV_Q --> RUN_OPTION_Q
    
    INDEX --> INQUIRER
    INDEX --> SPAWN
    INDEX --> DOTENV
```

Sources: [cli/src/index.js:1-8](), [cli/src/helpers.js:1-27](), [cli/package.json:16-31]()

## Interactive Setup Process

The CLI provides two distinct paths based on whether environment files already exist, with comprehensive validation for API keys and deployment options.

### New Environment Setup

For fresh installations, the CLI collects and validates API credentials for external services:

| Service | Key Pattern | Validation Method |
|---------|-------------|-------------------|
| OpenAI | `sk-[a-zA-Z0-9]{48}` | GET request to `/v1/models` endpoint |
| SERP API | `[a-zA-Z0-9]{40}` | POST request to `/search` endpoint |
| Replicate | `r8_[a-zA-Z0-9]{37}` | GET request to `/v1/models/replicate/hello-world` |

The validation process includes actual API calls to verify key authenticity:

```javascript
// OpenAI validation example from newEnvQuestions
const endpoint = "https://api.openai.com/v1/models"
const response = await fetch(endpoint, {
    headers: {
        "Authorization": `Bearer ${apikey}`,
    },
});
```

Sources: [cli/src/questions/newEnvQuestions.js:12-30](), [cli/src/questions/newEnvQuestions.js:37-60](), [cli/src/questions/newEnvQuestions.js:67-85]()

### Existing Environment Handling

When environment files are detected, the CLI validates the existing configuration using the `testEnvFile()` function and presents deployment options without requiring credential re-entry.

**Environment Detection and Validation Flow**

```mermaid
sequenceDiagram
    participant CLI as "CLI Process" 
    participant ENV_CHECK as "doesEnvFileExist()"
    participant VALIDATOR as "testEnvFile()"
    participant INQUIRER as "inquirer.prompt()"
    participant HANDLER as "handleRunOption()"
    
    CLI->>ENV_CHECK: "Check for ./next/env"
    ENV_CHECK-->>CLI: "File exists: true"
    CLI->>VALIDATOR: "Validate existing env"
    
    alt Validation Success
        VALIDATOR-->>CLI: "Validation passed"
        CLI->>INQUIRER: "existingEnvQuestions"
        INQUIRER-->>CLI: "User answers"
        CLI->>HANDLER: "Process deployment choice"
    else Validation Failed
        VALIDATOR-->>CLI: "Error message"
        CLI->>CLI: "Exit process"
    end
```

Sources: [cli/src/index.js:10-23](), [cli/src/questions/existingEnvQuestions.js:1-6]()

## Deployment Integration

The CLI provides two deployment pathways with different levels of automation and complexity.

### Docker Compose Integration

The recommended deployment method uses `child_process.spawn()` to execute Docker Compose with build flags:

```javascript
const dockerComposeUp = spawn("docker-compose", ["up", "--build"], {
  stdio: "inherit",
});
```

This approach:
- Inherits stdio for real-time output
- Builds containers before starting services
- Provides automated orchestration of all system components

### Manual Deployment Instructions

For advanced users or development scenarios, the CLI provides detailed manual setup instructions covering:
- Frontend setup: `npm install && npm run dev` in `./next` directory
- Backend setup: `poetry install && poetry run python -m reworkd_platform` in `./platform` directory
- Database configuration requirements

Sources: [cli/src/index.js:34-52]()

## Question System Architecture

The CLI uses a modular question system built on the `inquirer` library, with shared components and validation logic.

**Question Module Dependencies**

```mermaid
graph TD
    subgraph "Question Definitions"
        NEW_ENV["newEnvQuestions"]
        EXISTING_ENV["existingEnvQuestions"] 
        SHARED["sharedQuestions"]
    end
    
    subgraph "Shared Components"
        RUN_OPTION["RUN_OPTION_QUESTION"]
        CHOICES["Docker/Manual choices"]
    end
    
    subgraph "Validation"
        IS_VALID_KEY["isValidKey(apikey, pattern)"]
        FETCH_VALIDATION["API endpoint validation"]
        ERROR_MSG["validKeyErrorMessage"]
    end
    
    subgraph "Input Types"
        LIST_TYPE["type: 'list'"]
        INPUT_TYPE["type: 'input'"]
        ASYNC_VALIDATE["validate: async(apikey)"]
    end
    
    NEW_ENV --> RUN_OPTION
    NEW_ENV --> IS_VALID_KEY
    NEW_ENV --> FETCH_VALIDATION
    NEW_ENV --> INPUT_TYPE
    NEW_ENV --> ASYNC_VALIDATE
    
    EXISTING_ENV --> RUN_OPTION
    EXISTING_ENV --> LIST_TYPE
    
    SHARED --> RUN_OPTION
    SHARED --> CHOICES
    
    IS_VALID_KEY --> ERROR_MSG
```

Sources: [cli/src/questions/sharedQuestions.js:1-11](), [cli/src/questions/newEnvQuestions.js:1-87](), [cli/src/helpers.js:21-26]()

## CLI Dependencies and Runtime

The CLI requires Node.js version `>=18.0.0 <19.0.0` and utilizes several key dependencies for functionality:

| Dependency | Purpose | Usage |
|------------|---------|--------|
| `inquirer` | Interactive prompts | User input collection and validation |
| `chalk` | Terminal styling | Colored output and formatting |
| `figlet` | ASCII art | Application title display |
| `dotenv` | Environment loading | Configuration file parsing |
| `node-fetch` | HTTP requests | API key validation |
| `configstore` | Configuration persistence | CLI settings storage |

The CLI integrates with the broader AgentGPT ecosystem by generating configuration files that are consumed by both the Next.js frontend and Python backend services.

Sources: [cli/package.json:6-8](), [cli/package.json:16-31]()