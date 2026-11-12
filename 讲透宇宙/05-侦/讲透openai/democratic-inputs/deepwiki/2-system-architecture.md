<!-- source: DeepWiki mcp.deepwiki.com · repo openai/democratic-inputs · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [projects/deliberation_at_scale/package-lock.json](projects/deliberation_at_scale/package-lock.json)
- [projects/deliberation_at_scale/package.json](projects/deliberation_at_scale/package.json)
- [projects/deliberation_at_scale/packages/data-core/package.json](projects/deliberation_at_scale/packages/data-core/package.json)
- [projects/deliberation_at_scale/packages/frontend/package.json](projects/deliberation_at_scale/packages/frontend/package.json)
- [projects/deliberation_at_scale/packages/orchestrator/.env.example](projects/deliberation_at_scale/packages/orchestrator/.env.example)
- [projects/deliberation_at_scale/packages/orchestrator/.eslintrc.js](projects/deliberation_at_scale/packages/orchestrator/.eslintrc.js)
- [projects/deliberation_at_scale/packages/orchestrator/package-lock.json](projects/deliberation_at_scale/packages/orchestrator/package-lock.json)
- [projects/deliberation_at_scale/packages/orchestrator/package.json](projects/deliberation_at_scale/packages/orchestrator/package.json)
- [projects/deliberation_at_scale/packages/orchestrator/src/index.ts](projects/deliberation_at_scale/packages/orchestrator/src/index.ts)
- [projects/deliberation_at_scale/packages/orchestrator/src/listener.ts](projects/deliberation_at_scale/packages/orchestrator/src/listener.ts)
- [projects/deliberation_at_scale/packages/orchestrator/src/runner.ts](projects/deliberation_at_scale/packages/orchestrator/src/runner.ts)
- [projects/deliberation_at_scale/packages/orchestrator/src/scheduler.ts](projects/deliberation_at_scale/packages/orchestrator/src/scheduler.ts)

</details>



This document provides a comprehensive overview of the Deliberation at Scale platform architecture, covering the monorepo structure, core packages, and system integrations. It focuses on the technical implementation details and code organization that powers the democratic input platform.

For information about specific AI conversation management, see [AI Orchestration System](#5). For details about the database schema and data relationships, see [Database Schema & Data Layer](#3). For frontend-specific architecture, see [Frontend Systems](#4).

## Overview

The Deliberation at Scale platform is implemented as a Node.js monorepo containing three primary packages that work together to facilitate AI-moderated group deliberations. The system combines real-time web technologies, AI processing pipelines, and structured conversation management to enable scalable democratic input processes.

```mermaid
graph TB
    subgraph "Monorepo Structure"
        ROOT["@deliberation-at-scale/mono-repo"]
        
        subgraph "Core Packages"
            FRONTEND["@deliberation-at-scale/frontend<br/>Next.js Application<br/>Port 3200"]
            ORCHESTRATOR["@deliberation-at-scale/orchestrator<br/>Background Processing<br/>Task Queue System"]
            DATACORE["@deliberation-at-scale/data-core<br/>Database Schema<br/>Migration System"]
        end
        
        subgraph "Workspace Management"
            NX["Nx Build System<br/>Task Coordination"]
            WORKSPACES["NPM Workspaces<br/>Package Linking"]
        end
    end
    
    ROOT --> FRONTEND
    ROOT --> ORCHESTRATOR  
    ROOT --> DATACORE
    ROOT --> NX
    ROOT --> WORKSPACES
```

**Sources:** [projects/deliberation_at_scale/package.json:1-31](), [projects/deliberation_at_scale/package-lock.json:1-24]()

## Package Architecture

### Frontend Package

The frontend package implements a Next.js application serving as the user interface for deliberation sessions. It handles user registration, real-time chat, video integration, and voting interfaces.

```mermaid
graph LR
    subgraph "Frontend Package Structure"
        NEXTAPP["Next.js App<br/>Port 3200"]
        
        subgraph "Key Dependencies"
            APOLLO["@apollo/client<br/>GraphQL Client"]
            SUPABASE_AUTH["@supabase/auth-helpers-nextjs<br/>Authentication"]
            WHEREBY["@whereby.com/browser-sdk<br/>Video Integration"]
            REDUX["@reduxjs/toolkit<br/>State Management"]
            LINGUI["@lingui/react<br/>Internationalization"]
        end
        
        subgraph "Build Tools"
            TYPESCRIPT["TypeScript"]
            TAILWIND["TailwindCSS"]
            CODEGEN["@graphql-codegen/cli<br/>Type Generation"]
        end
    end
    
    NEXTAPP --> APOLLO
    NEXTAPP --> SUPABASE_AUTH
    NEXTAPP --> WHEREBY
    NEXTAPP --> REDUX
    NEXTAPP --> LINGUI
```

**Sources:** [projects/deliberation_at_scale/packages/frontend/package.json:1-98]()

### Orchestrator Package

The orchestrator package manages background task processing, AI integration, and conversation flow control through a sophisticated worker system built on Graphile Worker.

```mermaid
graph TB
    subgraph "Orchestrator Roles"
        ALL["ORCHESTRATOR_ROLE=all<br/>Development Mode"]
        RUNNER["ORCHESTRATOR_ROLE=runner<br/>Task Processing"]
        SCHEDULER["ORCHESTRATOR_ROLE=scheduler<br/>Job Scheduling"]
        LISTENER["ORCHESTRATOR_ROLE=listener<br/>Database Events"]
    end
    
    subgraph "Core Systems"
        TASKS["Task Directory<br/>./src/tasks/"]
        WORKER["Graphile Worker<br/>Queue Management"]
        OPENAI_INT["OpenAI Integration<br/>AI Processing"]
        SUPABASE_RT["Supabase Realtime<br/>Event Listening"]
    end
    
    ALL --> RUNNER
    ALL --> SCHEDULER
    ALL --> LISTENER
    
    RUNNER --> TASKS
    RUNNER --> WORKER
    TASKS --> OPENAI_INT
    
    SCHEDULER --> WORKER
    LISTENER --> SUPABASE_RT
```

**Sources:** [projects/deliberation_at_scale/packages/orchestrator/package.json:1-50](), [projects/deliberation_at_scale/packages/orchestrator/src/index.ts:16-41]()

### Data Core Package

The data core package provides database schema management, migrations, and type generation for the entire platform using Drizzle ORM and Supabase.

```mermaid
graph LR
    subgraph "Data Core Components"
        SCHEMA["Database Schema<br/>Drizzle ORM"]
        MIGRATIONS["Migration System<br/>drizzle-kit"]
        TYPES["Type Generation<br/>Supabase CLI"]
        
        subgraph "Commands"
            MIGRATE["npm run db:migrate"]
            GENERATE["npm run db:generate-types"]
            MAGIC["npm run generate-magic-link"]
        end
    end
    
    SCHEMA --> MIGRATIONS
    MIGRATIONS --> TYPES
    MIGRATE --> SCHEMA
    GENERATE --> TYPES
```

**Sources:** [projects/deliberation_at_scale/packages/data-core/package.json:1-48]()

## External Service Integration

The platform integrates with several external services to provide comprehensive functionality:

```mermaid
graph TB
    subgraph "Platform Core"
        FRONTEND_SVC["Frontend Application"]
        ORCHESTRATOR_SVC["Orchestrator Services"]
    end
    
    subgraph "External Services"
        SUPABASE_SVC["Supabase<br/>Database + Auth + Realtime"]
        OPENAI_SVC["OpenAI API<br/>GPT Models for AI Moderation"]
        WHEREBY_SVC["Whereby API<br/>Video Conferencing Rooms"]
        SENTRY_SVC["Sentry<br/>Error Tracking + Performance"]
    end
    
    FRONTEND_SVC --> SUPABASE_SVC
    FRONTEND_SVC --> WHEREBY_SVC
    FRONTEND_SVC --> SENTRY_SVC
    
    ORCHESTRATOR_SVC --> SUPABASE_SVC
    ORCHESTRATOR_SVC --> OPENAI_SVC
    ORCHESTRATOR_SVC --> WHEREBY_SVC
    ORCHESTRATOR_SVC --> SENTRY_SVC
```

**Sources:** [projects/deliberation_at_scale/packages/orchestrator/.env.example:1-10](), [projects/deliberation_at_scale/packages/frontend/package.json:26-63]()

## Task Processing System

The orchestrator implements a sophisticated task processing system that manages the AI-powered conversation flow:

```mermaid
graph TD
    subgraph "Task Execution Flow"
        SCHEDULER_START["startScheduler()<br/>Job Initialization"]
        RUNNER_START["startRunner()<br/>Worker Process"]
        LISTENER_START["startListener()<br/>Database Events"]
        
        subgraph "Task Types"
            QUEUED["handleQueuedParticipants<br/>Room Assignment"]
            PROGRESSION["triggerRoomProgressionUpdates<br/>Phase Management"]
            VERIFICATION["Message Verification Tasks<br/>verifySafeMessage, verifyEasyMessage"]
        end
        
        subgraph "Worker Infrastructure"
            GRAPHILE["Graphile Worker<br/>Task Queue"]
            CRONTAB["Cron Jobs<br/>Scheduled Tasks"]
            RESCHEDULE["reschedule()<br/>Task Rescheduling"]
        end
    end
    
    SCHEDULER_START --> QUEUED
    SCHEDULER_START --> PROGRESSION
    
    RUNNER_START --> GRAPHILE
    RUNNER_START --> CRONTAB
    
    LISTENER_START --> VERIFICATION
    
    GRAPHILE --> RESCHEDULE
```

**Sources:** [projects/deliberation_at_scale/packages/orchestrator/src/scheduler.ts:6-16](), [projects/deliberation_at_scale/packages/orchestrator/src/runner.ts:9-37](), [projects/deliberation_at_scale/packages/orchestrator/src/listener.ts:10-57]()

## Real-time Data Flow

The platform implements a comprehensive real-time data synchronization system:

```mermaid
graph LR
    subgraph "Frontend State"
        APOLLO_CACHE["Apollo Client Cache<br/>GraphQL State"]
        REDUX_STORE["Redux Store<br/>Application State"]
    end
    
    subgraph "Real-time Layer"
        SUPABASE_RT["Supabase Realtime<br/>postgres_changes Events"]
        GRAPHQL_API["GraphQL API<br/>Queries + Mutations"]
    end
    
    subgraph "Background Processing"
        MESSAGE_LISTENER["Message INSERT Listener<br/>startMessageListener()"]
        TASK_QUEUE["Graphile Worker Queue<br/>quickAddJob()"]
        AI_TASKS["AI Processing Tasks<br/>verifySafeMessage, etc."]
    end
    
    APOLLO_CACHE --> GRAPHQL_API
    REDUX_STORE --> APOLLO_CACHE
    
    GRAPHQL_API --> SUPABASE_RT
    SUPABASE_RT --> MESSAGE_LISTENER
    MESSAGE_LISTENER --> TASK_QUEUE
    TASK_QUEUE --> AI_TASKS
```

**Sources:** [projects/deliberation_at_scale/packages/orchestrator/src/listener.ts:20-56](), [projects/deliberation_at_scale/packages/frontend/package.json:27-28]()

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend Framework** | Next.js 13.5.9 | React-based web application |
| **State Management** | Redux Toolkit + Apollo Client | Client-side state and GraphQL caching |
| **Backend Processing** | Node.js + Graphile Worker | Background task processing |
| **Database** | PostgreSQL via Supabase | Primary data storage |
| **Real-time** | Supabase Realtime | Live data synchronization |
| **AI Integration** | OpenAI API (GPT models) | Conversation moderation and guidance |
| **Video** | Whereby Browser SDK | Video conferencing |
| **Build System** | Nx + TypeScript | Monorepo management |
| **Internationalization** | Lingui | Multi-language support |
| **Error Tracking** | Sentry | Production monitoring |

## Development and Deployment

The system supports multiple deployment configurations through environment-based role assignment:

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_ALL["ORCHESTRATOR_ROLE=all<br/>Single Process Mode"]
        DEV_FRONTEND["Frontend Dev Server<br/>Port 3200"]
    end
    
    subgraph "Production Environment"
        PROD_RUNNER["ORCHESTRATOR_ROLE=runner<br/>Task Processing Nodes"]
        PROD_SCHEDULER["ORCHESTRATOR_ROLE=scheduler<br/>Job Scheduling Node"]
        PROD_LISTENER["ORCHESTRATOR_ROLE=listener<br/>Event Processing Node"]
        PROD_FRONTEND["Production Frontend<br/>Port 3300"]
    end
    
    subgraph "Process Management"
        PM2["PM2 Process Manager<br/>ecosystem.config.js"]
        NX_TASKS["Nx Task Runner<br/>Parallel Execution"]
    end
    
    PM2 --> PROD_RUNNER
    PM2 --> PROD_SCHEDULER
    PM2 --> PROD_LISTENER
    
    NX_TASKS --> DEV_ALL
    NX_TASKS --> DEV_FRONTEND
```

**Sources:** [projects/deliberation_at_scale/packages/orchestrator/src/index.ts:43-64](), [projects/deliberation_at_scale/packages/orchestrator/package.json:13-18](), [projects/deliberation_at_scale/package.json:6-13]()

---

