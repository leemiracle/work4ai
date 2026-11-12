<!-- source: DeepWiki mcp.deepwiki.com · repo gobii-ai/gobii-platform · page 1 Platform Overview · fetched 2026-10-26 -->

# Platform Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/admin.py](api/admin.py)
- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/models.py](api/models.py)
- [config/settings.py](config/settings.py)
- [console/views.py](console/views.py)
- [util/subscription_helper.py](util/subscription_helper.py)

</details>



## Purpose and Scope

This document provides a high-level introduction to the gobii-platform architecture, deployment modes, core components, and operational flow. It is intended for developers and system administrators who need to understand how the platform functions as a whole.

For detailed information about specific subsystems:
- Agent lifecycle and configuration: see [Agent Management](#4)
- Credit consumption and billing: see [Credit & Billing System](#5)
- Tool integration and MCP: see [Tool Integration](#6)
- Communication channels: see [Communication Systems](#7)

---

## Architecture Overview

The gobii-platform is a **Django-based multi-agent orchestration system** that enables users to create persistent AI agents capable of browser automation, tool integration, and multi-channel communication. The platform supports both individual users and organizations, with a sophisticated credit-based billing system and subscription management.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser"]
        APIClient["API Clients"]
    end
    
    subgraph "Application Layer"
        Django["Django Application<br/>console.views<br/>api.views"]
        WSGI["WSGI/ASGI Server<br/>daphne"]
        Channels["Django Channels<br/>WebSocket Support"]
    end
    
    subgraph "Core Services"
        AgentProv["PersistentAgentProvisioningService<br/>agents.services"]
        TaskCreditSvc["TaskCreditService<br/>tasks.services"]
        EventProc["process_agent_events_task<br/>api.agent.core.event_processing"]
        MCPMgr["MCPToolManager<br/>api.agent.tools.mcp_manager"]
    end
    
    subgraph "Background Workers"
        CeleryWorker["Celery Workers<br/>process_agent_events<br/>process_browser_use_task"]
        CeleryBeat["Celery Beat<br/>RedBeat Scheduler<br/>Grant Credits<br/>Sync Numbers"]
    end
    
    subgraph "Data Persistence"
        Postgres[("PostgreSQL<br/>Django ORM<br/>api.models")]
        Redis[("Redis<br/>Celery Broker<br/>Locks<br/>Channels")]
        ObjectStorage[("S3/GCS<br/>Browser Profiles<br/>Attachments")]
    end
    
    subgraph "External Services"
        Stripe["Stripe API<br/>djstripe.models"]
        LLMProviders["LLM Providers<br/>litellm integration"]
        MCPServers["MCP Servers<br/>Bright Data<br/>Pipedream"]
        CommProviders["Communication<br/>Mailgun/Postmark<br/>Twilio"]
    end
    
    Browser --> Django
    APIClient --> Django
    Django --> WSGI
    Django --> Channels
    
    Django --> AgentProv
    Django --> TaskCreditSvc
    Django --> EventProc
    
    EventProc --> CeleryWorker
    AgentProv --> CeleryWorker
    CeleryBeat -.->|schedules| CeleryWorker
    
    EventProc --> MCPMgr
    
    Django --> Postgres
    CeleryWorker --> Postgres
    Django --> Redis
    CeleryWorker --> Redis
    Channels --> Redis
    
    Django --> Stripe
    EventProc --> LLMProviders
    MCPMgr --> MCPServers
    Django --> CommProviders
    CeleryWorker --> ObjectStorage
```

**Sources:** [config/settings.py:1-878](), [console/views.py:1-100](), [api/agent/core/event_processing.py:1-200](), [api/models.py:1-500]()

---

## Deployment Modes

The platform supports two deployment modes controlled by the `GOBII_PROPRIETARY_MODE` setting, with distinct feature sets and licensing requirements.

### Community Edition

**Default mode** (`GOBII_PROPRIETARY_MODE=False`) providing core agent functionality without external service dependencies:

| Feature | Configuration |
|---------|---------------|
| **Turnstile CAPTCHA** | Disabled (`TURNSTILE_ENABLED=False`) |
| **Email Verification** | Disabled (`ACCOUNT_EMAIL_VERIFICATION=none`) |
| **Email Backend** | Console (`django.core.mail.backends.console.EmailBackend`) |
| **Stripe Billing** | Disabled unless explicitly configured |
| **Agent/Task Limits** | Effectively unlimited when `GOBII_ENABLE_COMMUNITY_UNLIMITED=True` |

Community Edition is designed for self-hosting and development, removing barriers to local deployment while preserving full agent orchestration capabilities.

**Sources:** [config/settings.py:56-74](), [config/settings.py:457-462](), [config/settings.py:488-496](), [config/settings.py:729-741]()

### Proprietary Mode

**Licensed mode** (`GOBII_PROPRIETARY_MODE=True`) enabling production features with external service integrations:

| Feature | Configuration |
|---------|---------------|
| **Turnstile CAPTCHA** | Enabled on signup/login forms |
| **Email Verification** | Mandatory when `MAILGUN_API_KEY` present |
| **Email Backend** | Mailgun/Postmark via Anymail |
| **Stripe Billing** | Enabled when credentials present |
| **Agent/Task Limits** | Plan-based quotas enforced |
| **Analytics** | Segment, Mixpanel, Meta Pixel, LinkedIn |
| **SMS** | Twilio integration |

Proprietary Mode requires a valid license from Gobii, Inc. and is intended for hosted/commercial deployments.

**Sources:** [config/settings.py:66](), [config/settings.py:451-456](), [config/settings.py:679-723](), [config/settings.py:837-856]()

### Configuration Toggle Pattern

```mermaid
graph LR
    EnvVar["GOBII_PROPRIETARY_MODE<br/>environment variable"]
    Settings["config.settings"]
    
    EnvVar -->|False| CommunityPath["Community Defaults<br/>- No Turnstile<br/>- No email verification<br/>- Console email backend"]
    EnvVar -->|True| ProprietaryPath["Proprietary Defaults<br/>- Turnstile enabled<br/>- Email verification<br/>- Mailgun/Postmark"]
    
    Settings -->|conditional| FeatureGates["Feature Gates<br/>TURNSTILE_ENABLED<br/>STRIPE_ENABLED<br/>TWILIO_ENABLED"]
    
    FeatureGates --> AppBehavior["Application Behavior<br/>signup_form<br/>billing_views<br/>sms_tasks"]
```

**Sources:** [config/settings.py:56-99](), [config/settings.py:488-512]()

---

## Core Subsystems

### Agent Management

The platform manages two types of agents that work together:

```mermaid
graph TB
    User["User or Organization<br/>django.contrib.auth.User<br/>api.models.Organization"]
    
    PersistentAgent["PersistentAgent<br/>api.models.PersistentAgent<br/>- charter<br/>- schedule<br/>- life_state"]
    
    BrowserAgent["BrowserUseAgent<br/>api.models.BrowserUseAgent<br/>- name<br/>- preferred_proxy"]
    
    ProvisionService["PersistentAgentProvisioningService<br/>api.services.persistent_agents<br/>.provision()"]
    
    User -->|creates via| ProvisionService
    ProvisionService -->|creates| PersistentAgent
    ProvisionService -->|creates| BrowserAgent
    PersistentAgent -->|one-to-one| BrowserAgent
    
    PersistentAgent -->|processes events via| EventLoop["_run_agent_loop<br/>api.agent.core.event_processing"]
    EventLoop -->|spawns tasks for| BrowserAgent
```

- **`PersistentAgent`**: High-level agent with charter, schedule, communication endpoints, and lifecycle state
- **`BrowserUseAgent`**: Low-level browser automation executor with proxy configuration and profile persistence
- **Provisioning**: Atomic creation via `PersistentAgentProvisioningService.provision()` with quota enforcement

**Sources:** [api/models.py:472-611](), [api/models.py:1186-1579](), [api/services/persistent_agents.py:1-200]()

### Event Processing Pipeline

Agent execution follows a credit-gated loop with LLM reasoning and tool execution:

```mermaid
graph TB
    Trigger["Event Trigger<br/>- Cron schedule<br/>- Inbound message<br/>- Manual invoke<br/>- Follow-up"]
    
    Task["process_agent_events_task<br/>api.agent.tasks"]
    
    Lock["Redlock Acquisition<br/>pottery.Redlock<br/>agent-event-processing:{agent_id}"]
    
    CreditGate["Pre-Processing Credit Gate<br/>TaskCreditService<br/>.check_and_consume_credit()"]
    
    AgentLoop["_run_agent_loop<br/>api.agent.core.event_processing<br/>MAX_AGENT_LOOP_ITERATIONS"]
    
    LLMCall["_completion_with_failover<br/>api.agent.core.event_processing<br/>tiered provider selection"]
    
    ToolExec["Tool Execution<br/>- execute_mcp_tool<br/>- execute_spawn_web_task<br/>- execute_send_email"]
    
    ToolCreditGate["_ensure_credit_for_tool<br/>per-tool credit check"]
    
    Trigger --> Task
    Task --> Lock
    Lock -->|acquired| CreditGate
    CreditGate -->|sufficient| AgentLoop
    CreditGate -->|insufficient| LogExit["Log: credit_insufficient<br/>PersistentAgentSystemStep"]
    
    AgentLoop --> LLMCall
    LLMCall -->|tool calls| ToolCreditGate
    LLMCall -->|reasoning| LogStep["PersistentAgentStep"]
    
    ToolCreditGate -->|credits OK| ToolExec
    ToolCreditGate -->|no credits| SkipTool["Skip tool<br/>Log: credit_insufficient_mid_loop"]
    
    ToolExec --> LogStep
    LogStep -->|continue| AgentLoop
    LogStep -->|done| Complete["Complete<br/>Release Lock"]
```

**Sources:** [api/agent/core/event_processing.py:716-1050](), [api/agent/core/event_processing.py:510-711](), [api/agent/core/event_processing.py:289-419]()

### Credit and Billing System

The platform uses a dual-ownership credit system supporting both users and organizations:

```mermaid
graph TB
    Owner["Owner<br/>User or Organization<br/>util.subscription_helper._resolve_owner_type()"]
    
    TaskCredit["TaskCredit<br/>api.models.TaskCredit<br/>- credits (Decimal)<br/>- credits_used (Decimal)<br/>- available_credits (Generated)<br/>- user XOR organization"]
    
    TaskCreditService["TaskCreditService<br/>tasks.services<br/>.check_and_consume_credit_for_owner()"]
    
    StripeConfig["StripeConfig<br/>api.models.StripeConfig<br/>- task_meter_id<br/>- org_team_task_meter_id"]
    
    MeteringBatch["MeteringBatch<br/>api.models.MeteringBatch<br/>- batch_key<br/>- rounded_quantity<br/>- stripe_event_id"]
    
    Owner -->|has many| TaskCredit
    Owner -->|consumes via| TaskCreditService
    
    TaskCreditService -->|atomic SELECT FOR UPDATE| TaskCredit
    TaskCreditService -->|creates when needed| AdditionalTask["TaskCredit<br/>additional_task=True"]
    
    AdditionalTask -->|metered to| StripeAPI["stripe.billing.MeterEvent.create<br/>util.subscription_helper.report_task_usage()"]
    
    StripeAPI -->|logged in| MeteringBatch
    
    StripeConfig -->|provides| MeterID["task_meter_event_name<br/>event identifier"]
    MeterID --> StripeAPI
```

**Credits are consumed atomically** within database transactions using `SELECT FOR UPDATE` to prevent race conditions. When standard credits are exhausted, the system can auto-provision `additional_task=True` credits (if the plan allows), which are immediately reported to Stripe for billing.

**Sources:** [tasks/services.py:1-400](), [api/models.py:290-471](), [util/subscription_helper.py:327-479]()

### Tool Integration

Tools are discovered and executed via the Model Context Protocol (MCP):

```mermaid
graph TB
    Agent["PersistentAgent"]
    
    SearchTool["search_tools tool<br/>api.agent.tools.mcp_tools<br/>execute_search_tools()"]
    
    MCPManager["MCPToolManager<br/>api.agent.tools.mcp_manager<br/>._tools_cache<br/>._clients"]
    
    BrightData["Bright Data MCP<br/>stdio server<br/>npx @brightdata/mcp<br/>- scrape_as_markdown<br/>- search_engine"]
    
    Pipedream["Pipedream MCP<br/>remote HTTP/SSE<br/>remote.mcp.pipedream.net<br/>OAuth per-app"]
    
    EnabledTools["PersistentAgentEnabledTool<br/>api.models<br/>LRU eviction at 40 tools"]
    
    Agent -->|calls| SearchTool
    SearchTool -->|queries via LLM| MCPManager
    MCPManager -->|registers| BrightData
    MCPManager -->|registers| Pipedream
    
    SearchTool -->|selects tools via LLM| EnableTool["enable_tools tool<br/>api.agent.tools.mcp_tools"]
    EnableTool -->|creates| EnabledTools
    
    EnabledTools -->|tracks| LastUsed["last_used_at<br/>for LRU eviction"]
    
    Agent -->|executes| MCPToolExec["execute_mcp_tool<br/>api.agent.tools.mcp_tools"]
    MCPToolExec -->|routes to| MCPManager
    MCPManager -->|stdio| BrightData
    MCPManager -->|HTTP| Pipedream
```

The MCP system enables dynamic tool discovery where agents use natural language to search for capabilities (e.g., "send a message to Slack") and the LLM selects appropriate tools from the catalog. Tools are limited to 40 per agent with automatic LRU eviction.

**Sources:** [api/agent/tools/mcp_manager.py:1-600](), [api/agent/tools/mcp_tools.py:1-400](), [api/models.py:2444-2527]()

---

## Data Models

### Key Model Relationships

```mermaid
erDiagram
    User ||--o{ PersistentAgent : "owns"
    Organization ||--o{ PersistentAgent : "owns"
    User ||--o{ TaskCredit : "owns"
    Organization ||--o{ TaskCredit : "owns"
    
    PersistentAgent ||--|| BrowserUseAgent : "has"
    PersistentAgent ||--o{ PersistentAgentStep : "logs"
    PersistentAgent ||--o{ PersistentAgentCommsEndpoint : "has"
    PersistentAgent ||--o{ PersistentAgentEnabledTool : "enables"
    
    BrowserUseAgent ||--o{ BrowserUseAgentTask : "spawns"
    BrowserUseAgentTask ||--o{ BrowserUseAgentTaskStep : "has"
    
    PersistentAgentStep ||--o| PersistentAgentToolCall : "may have"
    TaskCredit ||--o{ PersistentAgentStep : "consumed by"
    
    User ||--|| UserBilling : "has"
    Organization ||--|| OrganizationBilling : "has"
    UserBilling ||--o| DjstripeSubscription : "links to"
    OrganizationBilling ||--o| DjstripeSubscription : "links to"
```

**Owner Types**: The platform uses a dual-ownership pattern where both `User` and `Organization` can own agents and task credits. This is enforced via database check constraints requiring exactly one owner (XOR constraint).

**Sources:** [api/models.py:122-277](), [api/models.py:290-391](), [api/models.py:472-611](), [api/models.py:1186-1579]()

### Critical Model Classes

| Model | Location | Purpose |
|-------|----------|---------|
| `ApiKey` | [api/models.py:122-277]() | API authentication with dual ownership (user/org) |
| `TaskCredit` | [api/models.py:290-391]() | Credit blocks with generated `available_credits` column |
| `TaskCreditConfig` | [api/models.py:393-427]() | Singleton for default credit costs |
| `ToolCreditCost` | [api/models.py:429-471]() | Per-tool credit overrides |
| `BrowserUseAgent` | [api/models.py:472-611]() | Low-level browser automation agent |
| `BrowserUseAgentTask` | [api/models.py:618-832]() | Browser automation task with metering |
| `PersistentAgent` | [api/models.py:1186-1579]() | High-level agent with charter and schedule |
| `PersistentAgentStep` | [api/models.py:1771-1929]() | Agent execution step log with credit linkage |
| `PersistentAgentEnabledTool` | [api/models.py:2444-2527]() | LRU-evicted tool enablement (40 max) |
| `Organization` | [api/models.py:3246-3427]() | Multi-user organization with seat billing |
| `OrganizationBilling` | [api/models.py:3674-3857]() | Org subscription and seat management |

**Sources:** [api/models.py:1-4000]()

---

## Request Flow

### Web Request: Create Agent

```mermaid
sequenceDiagram
    participant User
    participant ConsoleFrontend as "React Frontend<br/>AgentChatLayout"
    participant DjangoView as "console.views<br/>PersistentAgentCreateView"
    participant ProvService as "PersistentAgentProvisioningService<br/>agents.services"
    participant CreditService as "TaskCreditService<br/>tasks.services"
    participant DB as "PostgreSQL<br/>Django ORM"
    participant Celery as "Celery Worker<br/>process_agent_events_task"
    
    User->>ConsoleFrontend: Fill charter form
    ConsoleFrontend->>DjangoView: POST /console/agents/create/
    DjangoView->>DjangoView: Authenticate & context
    DjangoView->>ProvService: .provision(user, org, charter)
    
    ProvService->>DB: BEGIN TRANSACTION
    ProvService->>DB: Create BrowserUseAgent
    ProvService->>DB: Create PersistentAgent
    ProvService->>DB: Apply template (if selected)
    ProvService->>DB: COMMIT
    
    ProvService-->>DjangoView: ProvisioningResult(agent)
    
    DjangoView->>DB: transaction.on_commit()
    DB->>Celery: .delay(agent_id)
    
    DjangoView-->>ConsoleFrontend: HTTP 201 + agent data
    ConsoleFrontend-->>User: Navigate to agent chat
    
    Note over Celery: Async processing begins
    Celery->>DB: Acquire Redlock
    Celery->>CreditService: Check credits
    Celery->>Celery: _run_agent_loop()
```

**Sources:** [console/views.py:351-577](), [api/services/persistent_agents.py:1-300](), [api/agent/tasks.py:1-100]()

### API Request: Browser Task

```mermaid
sequenceDiagram
    participant Client as "API Client"
    participant APIView as "api.views<br/>BrowserUseAgentTaskViewSet"
    participant TaskModel as "BrowserUseAgentTask<br/>api.models"
    participant CreditService as "TaskCreditService<br/>tasks.services"
    participant Celery as "Celery Worker<br/>process_browser_use_task"
    participant BrowserLib as "browser_use library<br/>Playwright"
    
    Client->>APIView: POST /api/v1/tasks/<br/>+ API key auth
    APIView->>APIView: Validate request
    APIView->>TaskModel: Create instance
    
    TaskModel->>TaskModel: .clean() validation
    TaskModel->>CreditService: .check_and_consume_credit_for_owner()
    CreditService->>CreditService: SELECT FOR UPDATE TaskCredit
    CreditService->>CreditService: credits_used += amount
    CreditService-->>TaskModel: Success + credit
    
    TaskModel->>TaskModel: .save()
    TaskModel-->>APIView: Task instance
    
    APIView->>Celery: process_browser_use_task.delay(task_id)
    APIView-->>Client: HTTP 201 + task JSON
    
    Note over Celery: Async browser execution
    Celery->>BrowserLib: Run browser automation
    BrowserLib-->>Celery: Result + steps
    Celery->>TaskModel: Update status, create steps
```

**Sources:** [api/views.py:1-500](), [api/models.py:618-832](), [tasks/services.py:1-400]()

---

## Technology Stack

### Core Framework

| Component | Technology | Configuration |
|-----------|-----------|---------------|
| **Web Framework** | Django 4.2+ | [config/settings.py:187-229]() |
| **ASGI Server** | Daphne | [config/settings.py:195](), [config/settings.py:285]() |
| **ORM** | Django ORM with PostgreSQL | [config/settings.py:288-316]() |
| **Task Queue** | Celery with Redis broker | [config/settings.py:561-602]() |
| **Scheduler** | Celery Beat (RedBeat) | [config/settings.py:599]() |
| **WebSocket** | Django Channels with Redis layer | [config/settings.py:554-559]() |

### External Integrations

| Integration | Library | Purpose |
|-------------|---------|---------|
| **LLM Providers** | LiteLLM | Multi-provider failover (OpenAI, Anthropic, Google, GLM) |
| **Stripe** | dj-stripe | Subscription billing and metering |
| **Email** | Anymail (Mailgun/Postmark) | Transactional email delivery |
| **SMS** | Twilio SDK | Phone verification and agent messaging |
| **Storage** | django-storages (S3/GCS) | Browser profiles and file attachments |
| **MCP** | Custom clients (stdio/HTTP) | Tool integration protocol |

**Sources:** [config/settings.py:1-878](), [api/agent/core/llm_config.py:1-200](), [api/agent/tools/mcp_manager.py:1-100]()

### Database Features

The platform leverages PostgreSQL-specific features:

- **Generated Columns**: `TaskCredit.available_credits` and `TaskCredit.grant_month` for query optimization
- **Partial Unique Constraints**: Conditional uniqueness for free plan credits per month
- **Check Constraints**: XOR enforcement for dual-ownership patterns
- **Connection Pooling**: `CONN_MAX_AGE=600` with health checks via `CONN_HEALTH_CHECKS=True`

**Sources:** [api/models.py:326-336](), [config/settings.py:288-316]()

---

## Bootstrap and First-Run Setup

The platform requires LLM configuration before agents can execute. This is handled via a first-run setup flow:

```mermaid
graph TB
    Request["HTTP Request"]
    
    Middleware["FirstRunSetupMiddleware<br/>setup.middleware"]
    
    CheckBootstrap{"is_llm_bootstrap_required()<br/>api.agent.core.llm_config"}
    
    CheckEnabled{"FIRST_RUN_SETUP_ENABLED<br/>config.settings"}
    
    SetupView["LLMConfigSetupView<br/>setup.views"]
    
    NormalFlow["Normal Request<br/>Processing"]
    
    Request --> Middleware
    Middleware --> CheckEnabled
    CheckEnabled -->|False| NormalFlow
    CheckEnabled -->|True| CheckBootstrap
    
    CheckBootstrap -->|required| Redirect["Redirect to<br/>/setup/llm-config/"]
    CheckBootstrap -->|configured| NormalFlow
    
    Redirect --> SetupView
    SetupView -->|saves| EnvFile[".env file<br/>or StripeConfig model"]
    EnvFile --> NormalFlow
```

The bootstrap process configures the default LLM provider and model used by `_run_agent_loop()`. In Community Edition, this can be skipped via `LLM_BOOTSTRAP_OPTIONAL=True` for testing purposes.

**Sources:** [setup/middleware.py:1-100](), [api/agent/core/llm_config.py:60-120](), [config/settings.py:70-73]()

---

## Observability

The platform integrates OpenTelemetry tracing throughout critical paths:

```mermaid
graph LR
    Request["HTTP/Celery Request"]
    
    Tracer["trace.get_tracer<br/>gobii.utils"]
    
    Span["Traced Functions<br/>@traced decorator<br/>observability module"]
    
    Baggage["Baggage Context<br/>user.id<br/>persistent_agent.id"]
    
    Collector["OTEL Collector<br/>OTEL_EXPORTER_OTLP_ENDPOINT"]
    
    Request --> Tracer
    Tracer --> Span
    Span --> Baggage
    Baggage --> Collector
```

Key traced operations include:
- Agent provisioning: `@traced("INITIALIZE User")`
- Credit operations: `@traced("CREDITS Get User Task Credit Limit")`
- Event processing: `tracer.start_as_current_span("LLM Completion")`
- Database queries: `@traced("SELECT BrowserUseAgent Random Proxy")`

**Sources:** [observability/__init__.py:1-50](), [api/agent/core/event_processing.py:324-362](), [util/subscription_helper.py:1-200]()

---

