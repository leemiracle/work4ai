# Page: Platform Overview

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

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/admin.py](api/admin.py)
- [config/settings.py](config/settings.py)
- [util/subscription_helper.py](util/subscription_helper.py)

</details>



This document provides installation, configuration, and initial setup instructions for the gobii-platform. It covers environment preparation, database initialization, and first-run configuration to get a working instance running in both development and production modes.

For detailed configuration options and deployment strategies, see [Configuration & Deployment](#2.1). For user authentication and signup flows, see [User Lifecycle & Authentication](#2.2).

---

## Overview

The gobii-platform is a Django-based multi-agent orchestration system with asynchronous task processing via Celery. A minimal working installation requires:

- **Application server**: Django (WSGI/ASGI)
- **Database**: PostgreSQL
- **Cache/broker**: Redis
- **Background workers**: Celery workers and beat scheduler
- **Frontend**: Vite-built React SPA (bundled during build)

The platform supports two operational modes:
- **Community Edition**: Open-source build with optional unlimited agent/task quotas, minimal external dependencies
- **Proprietary Mode**: Licensed build with Stripe billing, Cloudflare Turnstile, email verification, and analytics integrations

---

## Prerequisites

### Required

| Component | Minimum Version | Purpose |
|-----------|----------------|---------|
| Python | 3.11+ | Application runtime |
| PostgreSQL | 14+ | Primary data store |
| Redis | 6.0+ | Cache, Celery broker, channel layer |
| Node.js | 18+ | Frontend build (development only) |

### Optional

| Component | Use Case |
|-----------|----------|
| Docker & Docker Compose | Simplified local development |
| Stripe account | Subscription billing (Proprietary Mode) |
| LLM provider API keys | OpenAI, Anthropic, Google, GLM |
| Email provider | Mailgun or Postmark (transactional emails) |
| Twilio account | SMS communication channel |

**Sources:** [config/settings.py:1-937]()

---

## Installation Methods

### Docker Compose (Recommended for Development)

The repository includes a Docker Compose configuration for local development:

```bash
# Clone repository
git clone https://github.com/gobii-ai/gobii-platform.git
cd gobii-platform

# Start services (from infra/platform/local/)
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access application
open http://localhost:8000
```

The Compose stack includes:
- `web`: Django application server
- `db`: PostgreSQL database
- `redis`: Redis cache/broker
- `celery`: Background task workers
- `celery-beat`: Scheduled task dispatcher

**Sources:** [config/settings.py:35-54]()

---

### Manual Installation

For production or non-Docker environments:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure environment (see Configuration section below)
cp infra/platform/local/.env.example .env
# Edit .env with your settings

# 3. Initialize database
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Create superuser
python manage.py createsuperuser

# 6. Start services (in separate terminals/processes)
# Application server
python manage.py runserver  # Development
# OR
gunicorn config.wsgi:application  # Production

# Celery worker
celery -A config worker -l info

# Celery beat scheduler
celery -A config beat -l info --scheduler redbeat.RedBeatScheduler
```

**Sources:** [config/settings.py:287-316](), [config/settings.py:561-601]()

---

## Environment Configuration

### Configuration Hierarchy

```mermaid
graph TB
    EnvFile[".env File<br/>(infra/platform/local/.env)"]
    EnvVars["Environment Variables"]
    SettingsPy["config/settings.py"]
    Defaults["Smart Defaults<br/>(local dev mode)"]
    
    EnvFile -->|"environ.Env.read_env()"| EnvVars
    EnvVars -->|"env() lookups"| SettingsPy
    Defaults -->|"os.environ.setdefault()"| EnvVars
    
    SettingsPy --> Django["Django Application"]
    SettingsPy --> Celery["Celery Workers"]
    SettingsPy --> Database["PostgreSQL"]
    SettingsPy --> Redis["Redis"]
    
    Release["GOBII_RELEASE_ENV<br/>(local/staging/prod)"]
    InDocker["IN_DOCKER flag"]
    
    Release --> Defaults
    InDocker --> Defaults
```

**Sources:** [config/settings.py:18-54]()

---

### Core Environment Variables

The platform uses `django-environ` for configuration management. When `GOBII_RELEASE_ENV=local` and not running in Docker, the system applies smart defaults to enable immediate development without manual configuration.

#### Essential Settings

| Variable | Default (Local) | Description |
|----------|----------------|-------------|
| `DEBUG` | `True` | Enable debug mode (disable in production) |
| `DJANGO_SECRET_KEY` | `dev-insecure` | Django cryptographic signing key |
| `GOBII_ENCRYPTION_KEY` | `dev-insecure` | Application-level encryption key |
| `POSTGRES_HOST` | `localhost` | PostgreSQL server hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port |
| `POSTGRES_DB` | `gobii` | Database name |
| `POSTGRES_USER` | `postgres` | Database username |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |

#### Mode Selection

| Variable | Default | Description |
|----------|---------|-------------|
| `GOBII_PROPRIETARY_MODE` | `False` | Enable proprietary features (requires license) |
| `GOBII_ENABLE_COMMUNITY_UNLIMITED` | `True` | Disable agent/task limits in Community Edition |
| `FIRST_RUN_SETUP_ENABLED` | `True` | Enforce first-run setup wizard |
| `LLM_BOOTSTRAP_OPTIONAL` | `False` | Allow skipping LLM configuration on first run |

**Sources:** [config/settings.py:56-73](), [config/settings.py:111-144]()

---

### Community vs Proprietary Mode

The platform's operational mode is controlled by `GOBII_PROPRIETARY_MODE`:

```python
# config/settings.py:56-66
GOBII_PROPRIETARY_MODE = env.bool("GOBII_PROPRIETARY_MODE", default=False)
```

| Feature | Community Edition | Proprietary Mode |
|---------|------------------|------------------|
| Signup Turnstile | Disabled | Enabled (if configured) |
| Email Verification | `none` | `mandatory` (if Mailgun configured) |
| Stripe Billing | Disabled | Enabled (if keys configured) |
| Agent Limits | Unlimited (configurable) | Plan-based |
| Task Limits | Unlimited (configurable) | Plan-based |
| Brand Links | GitHub, Discord, X (OSS) | Proprietary URLs |
| Default Email Backend | Console | Mailgun/Postmark |

**Community defaults** are loaded from `_COMMUNITY_DEFAULTS` dictionary:

```python
# config/settings.py:81-87
_COMMUNITY_DEFAULTS = {
    "brand": {
        "PUBLIC_DISCORD_URL": "https://discord.gg/yyDB8GwxtE",
        "PUBLIC_X_URL": "https://x.com/gobii_ai",
        "PUBLIC_GITHUB_URL": "https://github.com/gobii-ai",
    }
}
```

**Proprietary defaults** are loaded from the `proprietary` package if installed:

```python
# config/settings.py:75-78
try:
    from proprietary import defaults as _proprietary_defaults_module
except ImportError:
    _proprietary_defaults_module = None
```

**Sources:** [config/settings.py:56-109](), [config/settings.py:232-234]()

---

### External Service Configuration

#### Stripe (Billing & Subscriptions)

Required for paid plans in Proprietary Mode:

| Variable | Description |
|----------|-------------|
| `STRIPE_LIVE_SECRET_KEY` | Live mode secret key |
| `STRIPE_TEST_SECRET_KEY` | Test mode secret key |
| `STRIPE_LIVE_MODE` | Use live mode (`True` in production) |
| `STRIPE_WEBHOOK_SECRET` | Webhook endpoint verification secret |

Stripe integration is automatically enabled when `GOBII_PROPRIETARY_MODE=True` and keys are present.

**Sources:** [config/settings.py:725-743]()

---

#### Email Providers

The platform supports multiple email backends:

| Variable | Provider | Use Case |
|----------|----------|----------|
| `MAILGUN_API_KEY` | Mailgun | Transactional emails (signup, verification) |
| `MAILGUN_SENDER_DOMAIN` | Mailgun | Sending domain |
| `POSTMARK_SERVER_TOKEN` | Postmark | Transactional emails (alternative) |

Default behavior:
- **Community**: Console backend (prints to stdout)
- **Proprietary with keys**: Mailgun/Postmark
- **Proprietary without keys**: Console backend (for local development)

**Sources:** [config/settings.py:451-456](), [config/settings.py:680-717]()

---

#### SMS Provider (Twilio)

Optional for SMS communication channel:

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Twilio account identifier |
| `TWILIO_AUTH_TOKEN` | Twilio authentication token |
| `TWILIO_MESSAGING_SERVICE_SID` | Messaging service for outbound SMS |
| `TWILIO_VERIFY_SERVICE_SID` | Verify service for phone validation |

Twilio is enabled when `TWILIO_ENABLED=True` and credentials are present.

**Sources:** [config/settings.py:838-856]()

---

#### Storage Backends

Media files (browser profiles, attachments) support multiple backends:

| Variable | Description |
|----------|-------------|
| `STORAGE_BACKEND_TYPE` | `LOCAL`, `GCS`, or `S3` |
| `GS_BUCKET_NAME` | Google Cloud Storage bucket |
| `AWS_STORAGE_BUCKET_NAME` | S3-compatible bucket name |
| `AWS_S3_ENDPOINT_URL` | S3 endpoint (for MinIO/DigitalOcean) |

Default: Local filesystem storage at `MEDIA_ROOT`.

**Sources:** [config/settings.py:352-428]()

---

## Database Setup

### Initialization

Run migrations to create schema:

```bash
python manage.py migrate
```

This creates tables for:
- Core Django models (auth, sessions, contenttypes)
- djstripe models (Stripe webhooks, subscriptions)
- Application models (agents, tasks, credits, messages)

**Sources:** [config/settings.py:288-316]()

---

### Database Connection Tuning

The platform uses persistent connections with health checks for stability:

```python
# config/settings.py:296-315
"CONN_MAX_AGE": env.int("DJANGO_DB_CONN_MAX_AGE", default=600),
"CONN_HEALTH_CHECKS": True,
"OPTIONS": {
    "keepalives": env.int("PGTCP_KEEPALIVES", default=1),
    "keepalives_idle": env.int("PGTCP_KEEPALIVES_IDLE", default=60),
    "keepalives_interval": env.int("PGTCP_KEEPALIVES_INTERVAL", default=30),
    "keepalives_count": env.int("PGTCP_KEEPALIVES_COUNT", default=5),
}
```

These settings:
- Keep connections alive for 10 minutes to reduce reconnect overhead
- Validate connections on reuse
- Use TCP keepalives to survive NAT/LB timeouts during long Celery tasks

**Sources:** [config/settings.py:296-315]()

---

## First-Run Setup

### Setup Middleware

On initial access, `FirstRunSetupMiddleware` redirects unauthenticated users to a configuration wizard:

```python
# setup/middleware.py (referenced in settings)
# config/settings.py:241
"setup.middleware.FirstRunSetupMiddleware",
```

The middleware checks:
1. `FIRST_RUN_SETUP_ENABLED` setting
2. Existence of `SetupState` singleton
3. User authentication status

Bypass conditions:
- `/setup/` URLs (setup wizard itself)
- Static/media files
- Admin panel
- API endpoints
- Already authenticated users
- `SetupState.setup_completed=True`

**Sources:** [config/settings.py:71](), [config/settings.py:241]()

---

### LLM Bootstrap Requirement

The platform requires at least one configured LLM tier/endpoint for agent operation. The `llm_bootstrap` context processor checks for usable LLM configuration:

```python
# pages/context_processors.py (referenced in settings)
# config/settings.py:269
"pages.context_processors.llm_bootstrap",
```

LLM configuration can be:
- **Bypassed in tests**: `LLM_BOOTSTRAP_OPTIONAL=True`
- **Configured via admin**: Django admin → LLM Tiers/Endpoints
- **Configured in database**: Seed data during migrations

If no LLM configuration exists and bootstrap is enforced, the UI will prompt for configuration before allowing agent creation.

**Sources:** [config/settings.py:73](), [config/settings.py:269]()

---

### Setup Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Middleware as "FirstRunSetupMiddleware"
    participant DB as "Database"
    participant SetupView as "/setup/ View"
    participant Admin as "Django Admin"
    
    User->>Browser: Navigate to /
    Browser->>Middleware: GET /
    Middleware->>DB: Check SetupState
    
    alt Setup not completed
        Middleware->>Browser: Redirect to /setup/
        Browser->>SetupView: GET /setup/
        SetupView->>Browser: Show wizard
        User->>SetupView: Configure LLM endpoints
        SetupView->>DB: Create LLM tiers/endpoints
        User->>SetupView: Create superuser
        SetupView->>DB: Create User
        SetupView->>DB: Mark setup_completed=True
        SetupView->>Browser: Redirect to /
    else Setup completed
        Middleware->>Browser: Allow request
    end
    
    Browser->>User: Show homepage
    User->>Admin: Access /admin/
    Admin->>User: Login prompt
```

**Sources:** [config/settings.py:71](), [config/settings.py:241](), [config/settings.py:269]()

---

## Running the Platform

### Development Mode

Start all services in development:

```bash
# Terminal 1: Django development server
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery beat scheduler
celery -A config beat -l info --scheduler redbeat.RedBeatScheduler

# Terminal 4 (optional): Frontend dev server with hot reload
cd frontend
npm run dev
```

Frontend Vite integration:
- `VITE_USE_DEV_SERVER=True`: Use live dev server (http://127.0.0.1:5173)
- `VITE_USE_DEV_SERVER=False`: Use built assets from `static/frontend/`

**Sources:** [config/settings.py:324-328]()

---

### Component Startup Order

```mermaid
graph TB
    subgraph "Infrastructure"
        PG["PostgreSQL<br/>Port 5432"]
        Redis["Redis<br/>Port 6379"]
    end
    
    subgraph "Application Services"
        Migration["python manage.py migrate"]
        Static["python manage.py collectstatic"]
        Django["Django Server<br/>runserver / gunicorn"]
        Celery["Celery Worker<br/>celery -A config worker"]
        Beat["Celery Beat<br/>celery -A config beat"]
    end
    
    subgraph "Optional Services"
        Vite["Vite Dev Server<br/>npm run dev<br/>(port 5173)"]
    end
    
    PG --> Migration
    Migration --> Static
    Static --> Django
    
    Redis --> Django
    Redis --> Celery
    Redis --> Beat
    
    Django -.->|"VITE_USE_DEV_SERVER=True"| Vite
    
    style Migration fill:#e1f5ff
    style PG fill:#fff4e1
    style Redis fill:#fff4e1
```

**Sources:** [config/settings.py:287-316](), [config/settings.py:551-559](), [config/settings.py:561-601]()

---

### Production Deployment

Key differences from development:

1. **WSGI Server**: Use `gunicorn` or `uwsgi` instead of `runserver`
2. **Static Files**: Serve via WhiteNoise (bundled) or CDN
3. **Environment**: Set `DEBUG=False`, `GOBII_RELEASE_ENV=prod`
4. **Secrets**: Use strong random values for `DJANGO_SECRET_KEY` and `GOBII_ENCRYPTION_KEY`
5. **Database**: Enable SSL with `POSTGRES_SSLMODE=require`
6. **Process Management**: Use systemd, supervisor, or Kubernetes for service orchestration

Example systemd service for Celery worker:

```ini
[Unit]
Description=Gobii Celery Worker
After=network.target redis.service postgresql.service

[Service]
Type=forking
User=gobii
Group=gobii
WorkingDirectory=/opt/gobii-platform
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"
ExecStart=/opt/gobii-platform/venv/bin/celery -A config worker \
    --detach \
    --pidfile=/var/run/celery/worker.pid \
    --logfile=/var/log/celery/worker.log \
    --loglevel=info

[Install]
WantedBy=multi-user.target
```

**Sources:** [config/settings.py:111-144](), [config/settings.py:561-601]()

---

## Verification

### Service Health Checks

After starting services, verify each component:

| Service | Check Command | Expected Output |
|---------|--------------|-----------------|
| PostgreSQL | `psql -U postgres -d gobii -c 'SELECT 1;'` | `1` |
| Redis | `redis-cli ping` | `PONG` |
| Django | `curl http://localhost:8000/` | HTTP 200 or redirect to /setup/ |
| Celery Worker | `celery -A config inspect ping` | `{'celery@hostname': {'ok': 'pong'}}` |
| Celery Beat | Check logs for `Scheduler: Sending due task...` | Scheduled tasks firing |

**Sources:** [config/settings.py:551-601]()

---

### Admin Access

1. Navigate to `http://localhost:8000/admin/`
2. Log in with superuser credentials
3. Verify models are accessible:
   - **Users** (django.contrib.auth)
   - **PersistentAgent** (api)
   - **TaskCredit** (api)
   - **BrowserUseAgent** (api)

**Sources:** [api/admin.py:1-50]()

---

### Create First Agent

1. Navigate to homepage: `http://localhost:8000/`
2. If first run setup is incomplete, complete wizard
3. Click "Create Agent" or use a template
4. Fill charter (purpose/instructions)
5. Configure schedule (optional)
6. Save and observe:
   - Agent appears in dashboard
   - Celery worker logs show `process_agent_events_task` queued
   - Agent executes and creates `PersistentAgentStep` records

**Sources:** [config/settings.py:71](), [config/settings.py:241]()

---

## Common Configuration Patterns

### Local Development (Community Edition)

```bash
# .env
DEBUG=True
GOBII_PROPRIETARY_MODE=False
GOBII_ENABLE_COMMUNITY_UNLIMITED=True
FIRST_RUN_SETUP_ENABLED=True
LLM_BOOTSTRAP_OPTIONAL=False

# Database & Redis use smart defaults
# No external API keys required
```

**Sources:** [config/settings.py:38-54](), [config/settings.py:66-73]()

---

### Staging Environment (Proprietary Mode)

```bash
# .env
DEBUG=False
GOBII_PROPRIETARY_MODE=True
GOBII_RELEASE_ENV=staging

# PostgreSQL (Cloud SQL, RDS, etc.)
POSTGRES_HOST=staging-db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=gobii_staging
POSTGRES_USER=gobii_app
POSTGRES_PASSWORD=<strong-password>
POSTGRES_SSLMODE=require

# Redis (ElastiCache, Cloud Memorystore, etc.)
REDIS_URL=rediss://staging-redis.example.com:6380/0

# Stripe (test mode)
STRIPE_TEST_SECRET_KEY=sk_test_...
STRIPE_LIVE_MODE=False

# Email (Mailgun sandbox)
MAILGUN_API_KEY=key-...
MAILGUN_SENDER_DOMAIN=sandbox.mailgun.org
```

**Sources:** [config/settings.py:111-144](), [config/settings.py:288-316](), [config/settings.py:725-743]()

---

### Production Environment (Proprietary Mode)

```bash
# .env
DEBUG=False
GOBII_PROPRIETARY_MODE=True
GOBII_RELEASE_ENV=prod

# Security
DJANGO_SECRET_KEY=<cryptographically-random-64-chars>
GOBII_ENCRYPTION_KEY=<cryptographically-random-64-chars>

# Database (replicated, high-availability)
POSTGRES_HOST=prod-db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=gobii_prod
POSTGRES_USER=gobii_app
POSTGRES_PASSWORD=<strong-password>
POSTGRES_SSLMODE=verify-full
DJANGO_DB_CONN_MAX_AGE=600

# Redis (clustered)
REDIS_URL=rediss://prod-redis.example.com:6380/0

# Stripe (live mode)
STRIPE_LIVE_SECRET_KEY=sk_live_...
STRIPE_LIVE_MODE=True
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (Mailgun production)
MAILGUN_API_KEY=key-...
MAILGUN_SENDER_DOMAIN=mail.gobii.ai

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com:4317
OTEL_EXPORTER_OTLP_INSECURE=False
```

**Sources:** [config/settings.py:111-144](), [config/settings.py:799-804]()

---

## Next Steps

After completing initial setup:

1. **Configure LLM Providers**: Add API keys for OpenAI, Anthropic, Google, or GLM in Django admin → LLM Endpoints
2. **Set Up Billing** (Proprietary): Configure Stripe webhook endpoint, test subscription flows
3. **Configure Communication Channels**: Add email accounts, SMS numbers, or enable peer messaging
4. **Create Agent Templates**: Define reusable agent configurations for common use cases
5. **Review Security Settings**: Audit `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and SSL configuration

For detailed configuration options, see [Configuration & Deployment](#2.1).

**Sources:** [config/settings.py:1-937](), [util/subscription_helper.py:1-1029]()

---

# Page: Configuration & Deployment

# Configuration & Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/admin.py](api/admin.py)
- [config/settings.py](config/settings.py)
- [util/subscription_helper.py](util/subscription_helper.py)

</details>



This page covers Django settings, environment variable configuration, deployment modes (Community Edition vs Proprietary Mode), and integration with external services including Stripe, email providers, SMS, analytics platforms, and MCP tool servers.

For information about **user authentication flows** and session management, see [User Lifecycle & Authentication](#2.2). For **Stripe subscription management** and webhook handling, see [Subscription Management](#5.2).

---

## Deployment Modes

The platform supports two operational modes controlled by the `GOBII_PROPRIETARY_MODE` environment variable:

| Mode | Description | Default Features |
|------|-------------|------------------|
| **Community Edition** | Open-source deployment with minimal external dependencies | No Turnstile, no email verification, optional unlimited agents/tasks |
| **Proprietary Mode** | Production deployment with full feature set | Turnstile enabled, email verification, real billing integration |

The mode is set via environment variable and defaults to Community Edition:

```python
GOBII_PROPRIETARY_MODE = env.bool("GOBII_PROPRIETARY_MODE", default=False)
```

**Sources:** [config/settings.py:56-66]()

### Community Edition Behavior

When `GOBII_PROPRIETARY_MODE=False`:

1. **Agent/Task Limits Disabled**: If `GOBII_ENABLE_COMMUNITY_UNLIMITED=True` (default), agent quotas and task credit limits are effectively unlimited
2. **No Turnstile**: Cloudflare Turnstile CAPTCHA is not loaded on signup/login forms
3. **No Email Verification**: `ACCOUNT_EMAIL_VERIFICATION` defaults to `"none"`
4. **Console Email Backend**: Email sending falls back to Django's console backend when no Mailgun credentials are provided
5. **Public Links**: Default brand links point to community resources (Discord, GitHub, X)

**Sources:** [config/settings.py:66-109](), [util/subscription_helper.py:937-946]()

### Proprietary Mode Behavior

When `GOBII_PROPRIETARY_MODE=True`:

1. **Turnstile Enabled**: Anti-bot protection on authentication forms (requires `TURNSTILE_SITEKEY` and `TURNSTILE_SECRET`)
2. **Email Verification Mandatory**: New signups must verify their email address before accessing the platform
3. **Stripe Integration**: Billing and metering are enabled when Stripe keys are present
4. **Production Email**: Mailgun or Postmark is used for transactional email delivery
5. **Proprietary Templates**: Template overrides from the `proprietary` app are loaded first

The proprietary mode prepends the `proprietary` app to `INSTALLED_APPS`:

```python
if GOBII_PROPRIETARY_MODE:
    INSTALLED_APPS = ["proprietary", *INSTALLED_APPS]
```

**Sources:** [config/settings.py:232-234](), [config/settings.py:488-496]()

---

## Environment Variables

### Smart Local Defaults

The platform automatically detects the runtime environment and applies sensible defaults for local development:

```mermaid
graph TB
    Start[Platform Startup] --> CheckEnv{Check GOBII_RELEASE_ENV}
    CheckEnv -->|local + not in Docker| LocalDefaults[Apply Local Defaults]
    CheckEnv -->|staging/prod/preview| ExplicitConfig[Use Explicit Env Vars]
    
    LocalDefaults --> SetDebug["DEBUG=1"]
    LocalDefaults --> SetDB["POSTGRES_HOST=localhost<br/>POSTGRES_PORT=5432"]
    LocalDefaults --> SetRedis["REDIS_URL=redis://localhost:6379/0"]
    LocalDefaults --> SetKeys["DJANGO_SECRET_KEY=dev-insecure<br/>GOBII_ENCRYPTION_KEY=dev-insecure"]
    
    SetDebug --> Ready[Platform Ready]
    SetDB --> Ready
    SetRedis --> Ready
    SetKeys --> Ready
    ExplicitConfig --> Ready
```

**Sources:** [config/settings.py:26-54]()

### Core Configuration Variables

| Variable | Purpose | Default (Local) | Required in Prod? |
|----------|---------|-----------------|-------------------|
| `GOBII_RELEASE_ENV` | Environment identifier (`local`, `staging`, `prod`) | `local` | Yes |
| `DEBUG` | Django debug mode | `True` | No (must be `False`) |
| `DJANGO_SECRET_KEY` | Session/CSRF token signing | `dev-insecure` | Yes |
| `GOBII_ENCRYPTION_KEY` | Field-level encryption key | `dev-insecure` | Yes |
| `POSTGRES_HOST` | Database hostname | `localhost` | Yes |
| `POSTGRES_PORT` | Database port | `5432` | Yes |
| `POSTGRES_DB` | Database name | `gobii` | Yes |
| `POSTGRES_USER` | Database username | `postgres` | Yes |
| `POSTGRES_PASSWORD` | Database password | `postgres` | Yes |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | Yes |

The detection logic uses `IN_DOCKER` to avoid overriding values in containerized environments:

```python
IN_DOCKER = os.path.exists("/.dockerenv") or env.bool("IN_DOCKER", default=False)
RELEASE_ENV = os.getenv("GOBII_RELEASE_ENV", "local")

if RELEASE_ENV == "local" and not IN_DOCKER:
    os.environ.setdefault("DEBUG", "1")
    os.environ.setdefault("DJANGO_SECRET_KEY", "dev-insecure")
    # ... additional defaults
```

**Sources:** [config/settings.py:35-54]()

### External Service Configuration

External integrations are conditionally enabled based on credential presence:

```mermaid
graph LR
    subgraph "Stripe Integration"
        StripeKeys["STRIPE_LIVE_SECRET_KEY<br/>STRIPE_TEST_SECRET_KEY"] --> StripeEnabled{Keys Present?}
        StripeEnabled -->|Yes + Proprietary| StripeActive["STRIPE_ENABLED=True"]
        StripeEnabled -->|No| StripeDisabled["STRIPE_ENABLED=False"]
    end
    
    subgraph "Email Integration"
        MailgunKey["MAILGUN_API_KEY"] --> MailgunEnabled{Key Present?}
        MailgunEnabled -->|Yes + Proprietary| MailgunActive["MAILGUN_ENABLED=True<br/>Backend=anymail.backends.mailgun"]
        MailgunEnabled -->|No| ConsoleBackend["Backend=console"]
    end
    
    subgraph "SMS Integration"
        TwilioSID["TWILIO_ACCOUNT_SID<br/>TWILIO_AUTH_TOKEN<br/>TWILIO_MESSAGING_SERVICE_SID"] --> TwilioEnabled{Credentials Present?}
        TwilioEnabled -->|Yes + Proprietary| TwilioActive["TWILIO_ENABLED=True"]
        TwilioEnabled -->|No| TwilioDisabled["TWILIO_ENABLED=False"]
    end
```

**Sources:** [config/settings.py:451-456](), [config/settings.py:680-708](), [config/settings.py:838-855]()

---

## Database Configuration

### PostgreSQL Settings

The platform uses PostgreSQL as the primary data store with connection pooling and health checks:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
        "CONN_MAX_AGE": env.int("DJANGO_DB_CONN_MAX_AGE", default=600),  # 10 minutes
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "sslmode": env("POSTGRES_SSLMODE", default=None),
            "keepalives": env.int("PGTCP_KEEPALIVES", default=1),
            "keepalives_idle": env.int("PGTCP_KEEPALIVES_IDLE", default=60),
            "keepalives_interval": env.int("PGTCP_KEEPALIVES_INTERVAL", default=30),
            "keepalives_count": env.int("PGTCP_KEEPALIVES_COUNT", default=5),
        },
    }
}
```

**Key Features:**
- **Connection Pooling**: `CONN_MAX_AGE=600` keeps connections alive for 10 minutes to reduce overhead in long-running Celery tasks
- **Health Checks**: Django automatically validates recycled connections with `SELECT 1` before reuse
- **TCP Keepalives**: Prevents connection drops through NAT/load balancers during long-running agent event processing tasks
- **SSL Support**: Configurable via `POSTGRES_SSLMODE` (e.g., `require`, `verify-full`)

**Sources:** [config/settings.py:287-316]()

---

## Redis & Celery Configuration

### Redis Usage

Redis serves three purposes in the platform:

1. **Celery Broker**: Task queue for background jobs
2. **Celery Result Backend**: Storage for task return values
3. **Channels Layer**: WebSocket message routing for real-time chat

```python
REDIS_URL = env("REDIS_URL")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}
```

**Sources:** [config/settings.py:551-559](), [config/settings.py:561-563]()

### Celery Beat Scheduler

The platform uses **RedBeat** (Redis-backed scheduler) instead of the default database scheduler to avoid table locks and enable distributed beat instances:

```python
CELERY_BEAT_SCHEDULER = "redbeat.RedBeatScheduler"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
```

**Sources:** [config/settings.py:599-601]()

### Task Time Limits

Agent event processing tasks have generous time limits to accommodate long-running browser automation:

```python
CELERY_TASK_TIME_LIMIT = 14400        # 4 hours hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 12600   # 3.5 hours soft limit
```

**Sources:** [config/settings.py:564-565]()

### Scheduled Tasks

The `CELERY_BEAT_SCHEDULE` dictionary defines recurring tasks:

| Task | Schedule | Purpose |
|------|----------|---------|
| `grant_monthly_free_credits` | Daily at 00:05 UTC | Grant free-tier monthly credits to users |
| `garbage_collect_timed_out_tasks` | Hourly at :30 | Clean up browser tasks exceeding time limits |
| `prune_prompt_archives` | Daily at 02:15 UTC | Delete old `PersistentAgentPromptArchive` records |
| `twilio_sync_numbers` (optional) | Hourly | Sync provisioned SMS numbers from Twilio |
| `pipedream_connect_gc_daily` (optional) | Daily at 04:45 UTC | Garbage collect orphaned Pipedream Connect sessions |

**Conditional Tasks:**

Tasks are added to the schedule only when their integrations are enabled:

```python
if TWILIO_ENABLED:
    CELERY_BEAT_SCHEDULE["twilio-sync-numbers"] = {
        "task": "api.tasks.sms_tasks.sync_twilio_numbers",
        "schedule": crontab(minute="*/60"),
    }

if PIPEDREAM_GC_ENABLED:
    CELERY_BEAT_SCHEDULE["pipedream-connect-gc-daily"] = {
        "task": "api.tasks.pipedream_connect_gc.gc_orphaned_users",
        "schedule": crontab(hour=4, minute=45),
    }
```

**Sources:** [config/settings.py:566-609]()

---

## Storage Backends

The platform supports three storage backends for user-uploaded files (browser profiles, attachments, etc.):

```mermaid
graph TB
    Check["STORAGE_BACKEND_TYPE<br/>environment variable"] --> Type{Backend Type}
    
    Type -->|LOCAL| LocalFS["Django FileSystemStorage<br/>MEDIA_ROOT directory"]
    Type -->|GCS| GCS["Google Cloud Storage<br/>storages.backends.gcloud"]
    Type -->|S3| S3["S3-compatible storage<br/>storages.backends.s3boto3"]
    
    LocalFS --> LocalConfig["MEDIA_ROOT (default: mediafiles/)<br/>MEDIA_URL=/media/"]
    
    GCS --> GCSConfig["GS_BUCKET_NAME (required)<br/>GS_PROJECT_ID<br/>GS_DEFAULT_ACL=projectPrivate"]
    
    S3 --> S3Config["AWS_STORAGE_BUCKET_NAME (required)<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>AWS_S3_ENDPOINT_URL (optional for MinIO)"]
```

### Configuration Examples

**Local Development:**
```bash
STORAGE_BACKEND_TYPE=LOCAL
MEDIA_ROOT=/app/mediafiles
```

**Google Cloud Storage:**
```bash
STORAGE_BACKEND_TYPE=GCS
GS_BUCKET_NAME=gobii-media-prod
GS_PROJECT_ID=gobii-platform
GS_DEFAULT_ACL=projectPrivate
```

**S3 or MinIO:**
```bash
STORAGE_BACKEND_TYPE=S3
AWS_STORAGE_BUCKET_NAME=gobii-media
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_REGION_NAME=us-west-2
AWS_S3_ENDPOINT_URL=https://s3.us-west-2.amazonaws.com
AWS_S3_ADDRESSING_STYLE=auto  # Use "path" for MinIO
```

### Static Files vs Media Files

- **Static Files**: CSS, JavaScript, images bundled with the application. Served by WhiteNoise in production (or S3 if `STORAGE_BACKEND_TYPE=S3`)
- **Media Files**: User-uploaded content (browser profiles, attachments). Always uses the configured storage backend

When `STORAGE_BACKEND_TYPE=S3`, both static and media files are served from S3:

```python
if STORAGE_BACKEND_TYPE == "S3":
    STORAGES["staticfiles"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            # ... S3 config
            "location": "static",
            "default_acl": "public-read",
        },
    }
```

**Sources:** [config/settings.py:318-428]()

---

## External Service Integration

### Stripe (Billing & Metering)

Stripe integration is enabled when credentials are present and `GOBII_PROPRIETARY_MODE=True`:

```python
STRIPE_LIVE_SECRET_KEY = env("STRIPE_LIVE_SECRET_KEY", default="")
STRIPE_TEST_SECRET_KEY = env("STRIPE_TEST_SECRET_KEY", default="")
STRIPE_LIVE_MODE = env.bool("STRIPE_LIVE_MODE", default=False)
STRIPE_KEYS_PRESENT = bool(STRIPE_LIVE_SECRET_KEY or STRIPE_TEST_SECRET_KEY)
STRIPE_ENABLED = env.bool("STRIPE_ENABLED", default=GOBII_PROPRIETARY_MODE and STRIPE_KEYS_PRESENT)
```

**Required Configuration:**

| Variable | Purpose | Example |
|----------|---------|---------|
| `STRIPE_LIVE_SECRET_KEY` | Production API key | `sk_live_...` |
| `STRIPE_TEST_SECRET_KEY` | Test mode API key | `sk_test_...` |
| `STRIPE_LIVE_MODE` | Use live vs test keys | `True` (prod) |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature verification | `whsec_...` |

The `StripeConfig` model stores additional identifiers (product IDs, price IDs, meter IDs) retrieved from the database at runtime:

```python
@admin.register(StripeConfig)
class StripeConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("release_env", "live_mode")}),
        ("Secrets", {"fields": ("webhook_secret", ...)}),
        ("Identifiers", {
            "fields": (
                "startup_price_id",
                "startup_additional_task_price_id",
                "task_meter_id",
                "task_meter_event_name",
                "org_team_price_id",
                # ...
            )
        }),
    )
```

**Sources:** [config/settings.py:724-744](), [api/admin.py:99-148](), [util/subscription_helper.py:42-52]()

### Email Providers

The platform supports **Mailgun** and **Postmark** via Django Anymail:

```mermaid
graph TB
    EmailSend[Agent Sends Email] --> CheckBackend{Email Backend?}
    
    CheckBackend -->|Mailgun Enabled| MailgunSend["anymail.backends.mailgun.EmailBackend<br/>MAILGUN_API_KEY<br/>MAILGUN_SENDER_DOMAIN"]
    CheckBackend -->|Postmark Enabled| PostmarkSend["anymail.backends.postmark.EmailBackend<br/>POSTMARK_SERVER_TOKEN"]
    CheckBackend -->|Neither| ConsoleSend["django.core.mail.backends.console.EmailBackend<br/>(logs to stdout)"]
    
    MailgunSend --> DeliverEmail[Email Delivered]
    PostmarkSend --> DeliverEmail
    ConsoleSend --> LogEmail[Email Logged to Console]
```

**Mailgun Configuration:**
```bash
MAILGUN_ENABLED=True
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_SENDER_DOMAIN=mg.example.com
```

**Postmark Configuration:**
```bash
POSTMARK_ENABLED=True
POSTMARK_SERVER_TOKEN=your-postmark-token
```

**Email Simulation in Development:**

When `SIMULATE_EMAIL_DELIVERY=True` (default in non-prod), the platform logs email sends without actually delivering them:

```python
SIMULATE_EMAIL_DELIVERY = env.bool(
    "SIMULATE_EMAIL_DELIVERY", default=(GOBII_RELEASE_ENV != "prod")
)
```

**Sources:** [config/settings.py:680-722](), [config/settings.py:829-834]()

### SMS (Twilio)

Twilio integration requires:

```bash
TWILIO_ENABLED=True
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_MESSAGING_SERVICE_SID=MGxxxx
TWILIO_VERIFY_SERVICE_SID=VAxxxx  # Optional for phone verification
```

The platform automatically syncs provisioned numbers when enabled:

```python
if TWILIO_ENABLED:
    CELERY_BEAT_SCHEDULE["twilio-sync-numbers"] = {
        "task": "api.tasks.sms_tasks.sync_twilio_numbers",
        "schedule": crontab(minute="*/60"),
    }
```

**Sources:** [config/settings.py:837-863](), [config/settings.py:591-596]()

### Analytics Integrations

The platform supports multiple analytics providers:

| Provider | Variable | Purpose |
|----------|----------|---------|
| Google Analytics | `GA_MEASUREMENT_ID` | Page view tracking |
| Segment | `SEGMENT_WRITE_KEY` | Server-side event tracking |
| Segment (Web) | `SEGMENT_WEB_WRITE_KEY` | Client-side event tracking |
| Reddit Pixel | `REDDIT_PIXEL_ID` | Ad conversion tracking |
| Meta Pixel | `META_PIXEL_ID` | Facebook/Instagram ads |
| LinkedIn Insight | `LINKEDIN_PARTNER_ID` | LinkedIn ad tracking |
| Mixpanel | `MIXPANEL_PROJECT_TOKEN` | Product analytics |

All analytics variables default to empty strings in Community Edition and proprietary defaults in Proprietary Mode via the `_proprietary_default` helper function.

**Sources:** [config/settings.py:14](), [config/settings.py:762-788](), [config/settings.py:857-861]()

### MCP Tools (Pipedream)

Pipedream Connect enables OAuth-based tool integrations (Google Sheets, Greenhouse, Trello, etc.):

```bash
PIPEDREAM_CLIENT_ID=your-client-id
PIPEDREAM_CLIENT_SECRET=your-client-secret
PIPEDREAM_PROJECT_ID=your-project-id
PIPEDREAM_ENVIRONMENT=development  # or "production"
PIPEDREAM_PREFETCH_APPS=google_sheets,greenhouse,trello
```

The environment automatically maps to Pipedream's two-environment model:

```python
def _default_pipedream_environment() -> str:
    rel = os.getenv("GOBII_RELEASE_ENV", "local").lower()
    return "production" if rel in ("prod", "production") else "development"
```

**Garbage Collection:**

Orphaned Pipedream Connect sessions are cleaned up automatically when enabled:

```python
PIPEDREAM_GC_ENABLED = env.bool(
    "PIPEDREAM_GC_ENABLED",
    default=bool(PIPEDREAM_CLIENT_ID and PIPEDREAM_CLIENT_SECRET and PIPEDREAM_PROJECT_ID),
)
PIPEDREAM_GC_DRY_RUN = env.bool("PIPEDREAM_GC_DRY_RUN", default=(PIPEDREAM_ENVIRONMENT != "production"))
PIPEDREAM_GC_EXPIRED_RETENTION_DAYS = env.int("PIPEDREAM_GC_EXPIRED_RETENTION_DAYS", default=30)
```

**Sources:** [config/settings.py:872-909]()

---

## Feature Flags & Limits

### Credit System Configuration

Default credit costs are configurable via environment variables but are typically overridden by database-backed settings:

```python
CREDITS_PER_TASK = Decimal(env("CREDITS_PER_TASK", default="0.4"))
DEFAULT_AGENT_DAILY_CREDIT_LIMIT = env.int("DEFAULT_AGENT_DAILY_CREDIT_LIMIT", default=25)

TOOL_CREDIT_COSTS = {
    "update_charter": Decimal("0.04"),
    "update_schedule": Decimal("0.04"),
    "sqlite_batch": Decimal("0.8"),
}
```

The database models `TaskCreditConfig` and `ToolCreditCost` take precedence over these defaults when present.

**Sources:** [config/settings.py:746-759]()

### Community Unlimited Mode

When running in Community Edition, the `GOBII_ENABLE_COMMUNITY_UNLIMITED` flag bypasses agent and task quotas:

```python
GOBII_ENABLE_COMMUNITY_UNLIMITED = env.bool("GOBII_ENABLE_COMMUNITY_UNLIMITED", default=True)
```

This is checked throughout the codebase:

```python
def is_community_unlimited_mode() -> bool:
    if 'test_settings' in os.environ.get('DJANGO_SETTINGS_MODULE', ''):
        return False
    return (not getattr(settings, "GOBII_PROPRIETARY_MODE", False)) and bool(
        getattr(settings, "GOBII_ENABLE_COMMUNITY_UNLIMITED", False)
    )
```

**Sources:** [config/settings.py:68-69](), [util/subscription_helper.py:937-946]()

### First-Run Setup

The platform can redirect unauthenticated users to a first-run setup wizard:

```python
FIRST_RUN_SETUP_ENABLED = env.bool("FIRST_RUN_SETUP_ENABLED", default=True)
```

Disable this in automated testing or headless deployments.

**Sources:** [config/settings.py:71]()

### Soft Expiration Settings

Agents on the free plan are automatically soft-expired after inactivity:

```python
AGENT_SOFT_EXPIRATION_INACTIVITY_DAYS = env.int("AGENT_SOFT_EXPIRATION_INACTIVITY_DAYS", default=60)
AGENT_SOFT_EXPIRATION_DOWNGRADE_GRACE_HOURS = env.int("AGENT_SOFT_EXPIRATION_DOWNGRADE_GRACE_HOURS", default=48)
```

**Sources:** [config/settings.py:609-613]()

---

## Frontend Configuration (Vite)

The platform uses **Vite** for frontend asset bundling. In development, Vite runs as a separate dev server with hot module replacement (HMR):

```python
VITE_DEV_SERVER_URL = env('VITE_DEV_SERVER_URL', default='http://127.0.0.1:5173')
VITE_USE_DEV_SERVER = env.bool('VITE_USE_DEV_SERVER', default=DEBUG)
VITE_ASSET_ENTRY = env('VITE_ASSET_ENTRY', default='src/main.tsx')
VITE_MANIFEST_PATH = Path(env('VITE_MANIFEST_PATH', default=str(BASE_DIR / 'static' / 'frontend' / 'manifest.json')))
```

**Development Mode:**
- `VITE_USE_DEV_SERVER=True`: Django loads assets from `http://127.0.0.1:5173` with HMR support
- Template tag `{% vite_asset %}` generates `<script type="module" src="http://127.0.0.1:5173/@vite/client"></script>` and entry point tags

**Production Mode:**
- `VITE_USE_DEV_SERVER=False`: Django reads `manifest.json` to find hashed asset filenames
- Template tag generates `<script type="module" src="/static/frontend/assets/main-abc123.js"></script>` with cache-busting hashes

**Sources:** [config/settings.py:324-328]()

---

## Configuration Diagram: Service Integration Flow

```mermaid
graph TB
    subgraph "Environment Detection"
        EnvVars["Environment Variables<br/>(infra/platform/local/.env)"] --> ReleaseEnv{GOBII_RELEASE_ENV}
        ReleaseEnv -->|local + not Docker| LocalDefaults["Smart Local Defaults<br/>DEBUG=1<br/>POSTGRES_HOST=localhost<br/>REDIS_URL=redis://localhost:6379"]
        ReleaseEnv -->|staging/prod| ExplicitVars["Explicit Configuration<br/>(no defaults)"]
    end
    
    subgraph "Core Services"
        LocalDefaults --> Postgres["PostgreSQL Database<br/>CONN_MAX_AGE=600<br/>TCP keepalives enabled"]
        LocalDefaults --> Redis["Redis<br/>Celery broker + results<br/>Channels layer"]
        ExplicitVars --> Postgres
        ExplicitVars --> Redis
    end
    
    subgraph "External Services"
        ProprietaryMode{GOBII_PROPRIETARY_MODE} -->|True| EnableStripe["Stripe Integration<br/>StripeConfig model<br/>Webhook handlers"]
        ProprietaryMode -->|True| EnableMailgun["Email Providers<br/>Mailgun or Postmark<br/>anymail backend"]
        ProprietaryMode -->|True| EnableTwilio["Twilio SMS<br/>Number provisioning<br/>Webhook ingestion"]
        ProprietaryMode -->|False| CommunityMode["Community Mode<br/>Console email backend<br/>No Stripe/Twilio"]
        
        EnableStripe --> StripeKeys{Keys Present?}
        StripeKeys -->|Yes| StripeActive["STRIPE_ENABLED=True<br/>Subscription webhooks<br/>Metering API"]
        StripeKeys -->|No| StripeDisabled["STRIPE_ENABLED=False"]
        
        EnableMailgun --> MailgunKey{MAILGUN_API_KEY?}
        MailgunKey -->|Yes| MailgunActive["MAILGUN_ENABLED=True<br/>SMTP delivery"]
        MailgunKey -->|No| PostmarkFallback{POSTMARK_SERVER_TOKEN?}
        PostmarkFallback -->|Yes| PostmarkActive["POSTMARK_ENABLED=True"]
        PostmarkFallback -->|No| ConsoleEmail["Console email backend"]
    end
    
    subgraph "Storage"
        StorageType{STORAGE_BACKEND_TYPE} -->|LOCAL| LocalStorage["FileSystemStorage<br/>MEDIA_ROOT"]
        StorageType -->|GCS| GCSStorage["GoogleCloudStorage<br/>GS_BUCKET_NAME"]
        StorageType -->|S3| S3Storage["S3Boto3Storage<br/>AWS_STORAGE_BUCKET_NAME"]
    end
    
    subgraph "Frontend"
        ViteMode{VITE_USE_DEV_SERVER} -->|True| ViteDev["Vite Dev Server<br/>http://127.0.0.1:5173<br/>HMR enabled"]
        ViteMode -->|False| ViteProd["Compiled Assets<br/>manifest.json<br/>Hashed filenames"]
    end
```

**Sources:** [config/settings.py:35-54](), [config/settings.py:287-316](), [config/settings.py:551-563](), [config/settings.py:724-744](), [config/settings.py:680-708](), [config/settings.py:352-428](), [config/settings.py:324-328]()

---

## Authentication & Turnstile

The platform uses **django-allauth** for authentication with optional Cloudflare Turnstile CAPTCHA:

```python
TURNSTILE_ENABLED = env.bool("TURNSTILE_ENABLED", default=GOBII_PROPRIETARY_MODE)

if TURNSTILE_ENABLED:
    INSTALLED_APPS.append("turnstile")
    ACCOUNT_FORMS = {
        "signup": "turnstile_signup.SignupFormWithTurnstile",
        "login": "turnstile_signup.LoginFormWithTurnstile",
    }
```

**Turnstile Configuration:**

```bash
TURNSTILE_ENABLED=True
TURNSTILE_SITEKEY=1x00000000000000000000AA  # Test key (default)
TURNSTILE_SECRET=1x0000000000000000000000000000000AA  # Test secret (default)
```

Use Cloudflare's production keys in staging/prod environments. The default test keys allow development without external dependencies.

**Email Verification:**

```python
ACCOUNT_EMAIL_VERIFICATION = env(
    "ACCOUNT_EMAIL_VERIFICATION",
    default="mandatory" if GOBII_PROPRIETARY_MODE and MAILGUN_API_KEY else "none",
)
```

In Proprietary Mode with email configured, users must verify their email before accessing the platform. Community Edition defaults to `"none"`.

**Sources:** [config/settings.py:488-512](), [config/settings.py:459-472]()

---

## Deployment Checklist

### Required Environment Variables (Production)

```bash
# Release Environment
GOBII_RELEASE_ENV=prod
GOBII_PROPRIETARY_MODE=True
DEBUG=False

# Security
DJANGO_SECRET_KEY=<generate-random-50+-char-string>
GOBII_ENCRYPTION_KEY=<generate-random-key>
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database
POSTGRES_HOST=<db-hostname>
POSTGRES_PORT=5432
POSTGRES_DB=gobii_prod
POSTGRES_USER=<db-user>
POSTGRES_PASSWORD=<secure-password>
POSTGRES_SSLMODE=require

# Redis
REDIS_URL=redis://<redis-hostname>:6379/0

# Storage (choose one)
STORAGE_BACKEND_TYPE=S3
AWS_STORAGE_BUCKET_NAME=<your-bucket>
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
AWS_S3_REGION_NAME=us-west-2

# Email
MAILGUN_ENABLED=True
MAILGUN_API_KEY=<mailgun-key>
MAILGUN_SENDER_DOMAIN=mg.yourdomain.com
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Billing (if using Stripe)
STRIPE_ENABLED=True
STRIPE_LIVE_MODE=True
STRIPE_LIVE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Turnstile
TURNSTILE_ENABLED=True
TURNSTILE_SITEKEY=<cloudflare-sitekey>
TURNSTILE_SECRET=<cloudflare-secret>
```

### Optional Services

```bash
# SMS
TWILIO_ENABLED=True
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_MESSAGING_SERVICE_SID=MG...

# Analytics
SEGMENT_WRITE_KEY=...
GA_MEASUREMENT_ID=G-...

# MCP Tools
PIPEDREAM_CLIENT_ID=...
PIPEDREAM_CLIENT_SECRET=...
PIPEDREAM_PROJECT_ID=...
PIPEDREAM_ENVIRONMENT=production
```

**Sources:** [config/settings.py:56-66](), [config/settings.py:111-113](), [config/settings.py:134-139](), [config/settings.py:287-316](), [config/settings.py:551](), [config/settings.py:392-428](), [config/settings.py:680-708](), [config/settings.py:724-744](), [config/settings.py:488-506](), [config/settings.py:838-855](), [config/settings.py:762-788](), [config/settings.py:872-888]()

---

# Page: User Lifecycle & Authentication

# User Lifecycle & Authentication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [console/forms.py](console/forms.py)
- [console/templates/console/organization_detail.html](console/templates/console/organization_detail.html)
- [console/templates/partials/_org_invite_modal.html](console/templates/partials/_org_invite_modal.html)
- [constants/stripe.py](constants/stripe.py)
- [pages/signals.py](pages/signals.py)
- [tests/unit/test_organizations.py](tests/unit/test_organizations.py)
- [tests/unit/test_pages_signals.py](tests/unit/test_pages_signals.py)

</details>



This page documents the user registration, authentication, and session management systems. It covers signup flows, login/logout events, UTM attribution tracking, analytics integration, and organization membership management.

For API key authentication and authorization mechanics, see [Authentication & Authorization](#9.2). For subscription provisioning during signup, see [Subscription Management](#5.2).

---

## User Signup Flow

User registration is handled through **django-allauth**, an integrated authentication framework. The platform tracks signup events for analytics and attribution purposes using Django signals.

### Signup Signal Handler

When a new user completes registration, the `user_signed_up` signal fires, triggering analytics tracking and UTM attribution capture:

```mermaid
graph TD
    Allauth["allauth.account.signals.user_signed_up"] --> Handler["handle_user_signed_up()"]
    Handler --> Session["Set session flag:<br/>show_signup_tracking=True"]
    Handler --> ParseUTM["Parse UTM cookies:<br/>__utm_first + current UTMs"]
    ParseUTM --> FirstTouch["Calculate first-touch attribution"]
    ParseUTM --> LastTouch["Calculate last-touch attribution"]
    
    FirstTouch --> Identify["Analytics.identify()<br/>with user traits"]
    LastTouch --> Identify
    
    Identify --> Track["Analytics.track()<br/>event=SIGNUP"]
    Track --> EventID["Generate event ID:<br/>reg-{uuid4}"]
    EventID --> Context["Include campaign context<br/>for CAPI integration"]
    
    Session --> Complete["Signup complete"]
    Context --> Complete
```

**Sources:** [pages/signals.py:113-195]()

The signup handler performs three key operations:

1. **Session Marking**: Sets `show_signup_tracking=True` in the session to enable downstream tracking
2. **User Identification**: Calls `Analytics.identify()` with user profile data and UTM parameters
3. **Event Tracking**: Fires a `SIGNUP` event with attribution data and a unique event ID for cross-platform tracking

### UTM Attribution System

The platform implements **dual-touch attribution** tracking both first-touch (initial discovery) and last-touch (conversion source) campaign parameters.

#### UTM Cookie Structure

```mermaid
graph LR
    subgraph "Browser Cookies"
        FirstCookie["__utm_first<br/>{<br/>  utm_source: 'google',<br/>  utm_medium: 'cpc',<br/>  utm_campaign: 'launch'<br/>}"]
        
        CurrentSource["utm_source<br/>'facebook'"]
        CurrentMedium["utm_medium<br/>'social'"]
        CurrentCampaign["utm_campaign<br/>'retarget'"]
    end
    
    subgraph "Signal Handler Processing"
        Parse["Parse __utm_first JSON"]
        Merge["Merge with current UTMs"]
        FirstTouch["First-touch:<br/>utm_source_first='google'<br/>utm_medium_first='cpc'"]
        LastTouch["Last-touch:<br/>utm_source_last='facebook'<br/>utm_medium_last='social'"]
    end
    
    FirstCookie --> Parse
    CurrentSource --> Merge
    CurrentMedium --> Merge
    CurrentCampaign --> Merge
    Parse --> Merge
    Merge --> FirstTouch
    Merge --> LastTouch
    
    FirstTouch --> Analytics["Analytics traits<br/>and event properties"]
    LastTouch --> Analytics
```

**Sources:** [pages/signals.py:129-178]()

The UTM mapping system uses a standardized key structure:

| UTM Parameter | Cookie Key | Analytics Key (First) | Analytics Key (Last) |
|---------------|------------|----------------------|---------------------|
| Source | `utm_source` | `utm_source_first` | `utm_source_last` |
| Medium | `utm_medium` | `utm_medium_first` | `utm_medium_last` |
| Campaign | `utm_campaign` | `utm_campaign_first` | `utm_campaign_last` |
| Content | `utm_content` | `utm_content_first` | `utm_content_last` |
| Term | `utm_term` | `utm_term_first` | `utm_term_last` |

**Sources:** [pages/signals.py:42-48]()

#### Attribution Logic

The handler implements a fallback chain for attribution:

1. **First-touch preservation**: Values in `__utm_first` cookie take precedence for first-touch
2. **Current-to-first fallback**: If `__utm_first` is missing a parameter but current request has it, use current
3. **Last-touch capture**: Current UTM cookies become last-touch attribution

This ensures accurate attribution even if users clear cookies between visits or arrive through multiple campaigns.

**Sources:** [pages/signals.py:138-156]()

### Analytics Event Payload

The signup event includes comprehensive tracking data:

```python
# Event properties
{
    'plan': 'free',
    'date_joined': '2025-01-15T08:30:00Z',
    'utm_source_first': 'google',
    'utm_source_last': 'facebook',
    # ... additional UTM fields
}

# Context for CAPI integration
{
    'campaign': {
        'source': 'facebook',
        'medium': 'social',
        'name': 'retarget',
        # ... other last-touch UTMs
    },
    'userAgent': 'Mozilla/5.0 ...'
}
```

The event includes a deterministic `message_id` in format `reg-{uuid}` for deduplication across analytics platforms like Facebook CAPI and Reddit Pixel.

**Sources:** [pages/signals.py:164-190]()

---

## Login & Logout Events

The platform tracks user authentication state changes through django-allauth signals.

### Login Handler

```mermaid
graph LR
    Signal["user_logged_in"] --> Handler["handle_user_logged_in()"]
    Handler --> Identify["Analytics.identify()<br/>refresh user traits"]
    Handler --> Track["Analytics.track_event()<br/>event=LOGGED_IN"]
    Track --> Properties["properties: {}<br/>source: WEB"]
```

**Sources:** [pages/signals.py:196-217]()

The login handler:
1. **Refreshes user identity** with current profile data (name, email, join date)
2. **Tracks login event** with minimal properties (login source is always `WEB` for browser-based sessions)

### Logout Handler

```mermaid
graph LR
    Signal["user_logged_out"] --> Handler["handle_user_logged_out()"]
    Handler --> Track["Analytics.track_event()<br/>event=LOGGED_OUT"]
    Track --> Properties["properties: {}<br/>source: WEB"]
```

**Sources:** [pages/signals.py:218-231]()

The logout handler fires a simple tracking event. Session cleanup is handled by Django's authentication system.

### Error Handling

All analytics operations are wrapped in try-except blocks to prevent tracking failures from disrupting authentication flows. Exceptions are logged but do not propagate to users.

**Sources:** [pages/signals.py:193-216](), [pages/signals.py:229-231]()

---

## Session Management

The platform uses Django's session framework for maintaining user state across requests.

### Session Data Structure

User sessions store:

| Session Key | Type | Purpose |
|-------------|------|---------|
| `show_signup_tracking` | `bool` | Flags newly signed-up users for tracking |
| `context_type` | `str` | Current context: `'user'` or `'organization'` |
| `context_id` | `str` | UUID of active user or organization |
| `context_name` | `str` | Display name for UI context switcher |
| `org_seat_portal_target` | `dict` | Pending seat changes during Stripe checkout |
| `org_overage_detach` | `dict` | Temporary state for overage SKU management |

**Sources:** [tests/unit/test_organizations.py:505-519](), [tests/unit/test_organizations.py:537-552]()

### Context Switching

Users can operate in either **personal** or **organization** context. The active context determines:
- Which API keys are accessible
- Which agents are visible
- Which billing entity is charged for operations

```mermaid
graph TD
    User["Authenticated User"] --> Check{"Has Org<br/>Memberships?"}
    Check -->|No| Personal["Personal Context<br/>context_type='user'<br/>context_id=user.id"]
    Check -->|Yes| OrgList["Show Organization<br/>Switcher"]
    
    OrgList --> Select["User Selects Org"]
    Select --> OrgContext["Organization Context<br/>context_type='organization'<br/>context_id=org.id"]
    
    Personal --> Operations["Operations billed to<br/>UserBilling"]
    OrgContext --> OrgOps["Operations billed to<br/>OrganizationBilling"]
```

**Sources:** [tests/unit/test_organizations.py:505-519]()

Context switching persists across requests until the user explicitly changes it or logs out.

---

## Organization Membership

Organizations enable team collaboration with role-based access control. Users can belong to multiple organizations with different roles.

### Membership Roles

The platform defines three organization roles in `OrganizationMembership.OrgRole`:

| Role | Permissions |
|------|-------------|
| `OWNER` | Full control: manage members, roles, billing, seats, delete org |
| `ADMIN` | Manage members (except owners), invite/remove, change roles (except owner) |
| `MEMBER` | View organization, use organization agents, consume org credits |
| `VIEWER` | Read-only access to organization resources |

**Sources:** [console/templates/console/organization_detail.html:82-112]()

### Invitation Flow

Organization admins and owners can invite new members via email. The invitation system enforces seat limits and prevents duplicate invites.

```mermaid
sequenceDiagram
    participant Admin
    participant View as "organization_detail view"
    participant Form as "OrganizationInviteForm"
    participant DB as Database
    participant Email as Email System
    
    Admin->>View: POST /orgs/{id}/<br/>email, role
    View->>Form: Validate invitation
    
    Form->>DB: Check pending invites<br/>for email
    
    alt Existing Invite
        DB-->>Form: InviteExists
        Form-->>View: ValidationError:<br/>"already has pending invitation"
        View-->>Admin: Error message
    else No Existing Invite
        Form->>DB: Check seats_available
        
        alt No Seats
            DB-->>Form: seats_available=0
            Form-->>View: ValidationError:<br/>"No seats available"
            View-->>Admin: Error + purchase prompt
        else Seats Available
            Form->>DB: Create OrganizationInvite<br/>with unique token
            DB->>Email: Send invitation email<br/>with accept URL
            Email-->>Admin: Confirmation:<br/>"Invitation sent"
        end
    end
```

**Sources:** [tests/unit/test_organizations.py:53-109](), [console/templates/partials/_org_invite_modal.html:53-78]()

### Invite Model Structure

Each `OrganizationInvite` contains:

```python
{
    'org': Organization,           # Target organization
    'email': str,                  # Invitee email (case-insensitive)
    'role': str,                   # Assigned role on acceptance
    'token': UUID,                 # Unique acceptance token
    'invited_by': User,            # Admin who sent invite
    'sent_at': datetime,           # Initial send timestamp
    'expires_at': datetime,        # Expiration (default 7 days)
    'accepted_at': datetime | None,# Acceptance timestamp
    'revoked_at': datetime | None  # Revocation timestamp
}
```

**Sources:** [console/templates/console/organization_detail.html:164-192]()

### Acceptance Flow

Invited users receive an email with a unique acceptance URL: `/invite/{token}/accept/`

```mermaid
graph TD
    Email["Invitation Email"] --> Click["User clicks accept link"]
    Click --> Check{"User has<br/>account?"}
    
    Check -->|No| Signup["Redirect to signup<br/>preserve token"]
    Check -->|Yes| Login["Ensure logged in"]
    
    Signup --> PostSignup["Post-signup redirect<br/>to accept URL"]
    Login --> Accept["Accept invite"]
    PostSignup --> Accept
    
    Accept --> CreateMembership["Create OrganizationMembership<br/>with specified role"]
    CreateMembership --> MarkAccepted["Set invite.accepted_at"]
    MarkAccepted --> Redirect["Redirect to org detail"]
```

**Sources:** [tests/unit/test_organizations.py:83-94]()

Invites can also be **rejected** via `/invite/{token}/reject/`, which sets `revoked_at` without creating membership.

**Sources:** [tests/unit/test_organizations.py:745-763]()

### Seat Reservation Logic

The system reserves seats for pending invites to prevent over-subscription:

```python
seats_reserved = active_memberships_count + pending_invites_count
seats_available = purchased_seats - seats_reserved
```

An invite can only be sent if `seats_available > 0`. This prevents situations where accepted invites exceed purchased capacity.

**Sources:** [tests/unit/test_organizations.py:96-150]()

### Member Management

Owners and admins can:
- **Change roles** via dropdown (admins cannot promote to owner or demote owners)
- **Remove members** (admins cannot remove owners; no self-removal)
- **Leave organization** (any member can leave; owners must transfer ownership first)

**Sources:** [console/templates/console/organization_detail.html:96-131]()

---

## Authentication Mechanisms

The platform supports two authentication methods:

### Web Authentication (django-allauth)

Primary authentication for browser-based access using:
- Email/password credentials
- Session-based authentication
- CSRF protection via Django middleware

Allauth handles:
- User registration
- Email verification (optional)
- Password reset flows
- Account management

**Sources:** [pages/signals.py:10]()

### API Key Authentication

For programmatic access, users and organizations can create API keys. This system is documented in detail in [Authentication & Authorization](#9.2).

API keys are managed through the console interface and scoped to either:
- **Personal API keys**: Owned by a user, operate in user context
- **Organization API keys**: Owned by an organization, operate in org context

**Sources:** [console/forms.py:22-64]()

---

## Related Systems

- **Billing Integration**: When subscriptions are created via Stripe, the `handle_subscription_event` signal updates user/org billing records. See [Subscription Management](#5.2)
- **Credit Provisioning**: Subscription events trigger credit grants. See [TaskCreditService](#5.1)
- **Organization Billing**: Seat purchases and overage handling. See [Organization Billing](#5.3)

**Sources:** [pages/signals.py:233-651]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/migrations/0115_persistentagentstep_credits_fields.py](api/migrations/0115_persistentagentstep_credits_fields.py)
- [api/models.py](api/models.py)
- [console/views.py](console/views.py)
- [tasks/services.py](tasks/services.py)
- [tests/unit/test_persistent_agent_step_credits.py](tests/unit/test_persistent_agent_step_credits.py)
- [tests/unit/test_task_credit_service.py](tests/unit/test_task_credit_service.py)
- [tests/unit/test_tool_costs.py](tests/unit/test_tool_costs.py)
- [util/tool_costs.py](util/tool_costs.py)

</details>



This document introduces the fundamental data models, ownership patterns, and resource control mechanisms in the gobii-platform. It covers the dual ownership model (User vs Organization), core entity types (Agents, Credits, API Keys), and how they interrelate.

For detailed information about specific subsystems, see:
- Agent lifecycle and configuration: [Agents](#3.1)
- Credit consumption and quotas: [Task Credits](#3.2)
- Multi-user organizations: [Organizations](#3.3)
- Agent creation workflows: [Creating Agents](#4.1)
- Billing infrastructure: [Credit & Billing System](#5)

---

## Dual Ownership Model

The platform supports two ownership contexts: **personal (User)** and **organizational (Organization)**. Most entities can be owned by either type, enforced via database constraints.

### Ownership Enforcement Patterns

```mermaid
graph TB
    subgraph "User Ownership"
        U[User]
        U --> PA1["PersistentAgent<br/>(user_id)"]
        U --> TC1["TaskCredit<br/>(user_id)"]
        U --> AK1["ApiKey<br/>(user_id)"]
    end
    
    subgraph "Organization Ownership"
        O[Organization]
        O --> PA2["PersistentAgent<br/>(organization_id)"]
        O --> TC2["TaskCredit<br/>(organization_id)"]
        O --> AK2["ApiKey<br/>(organization_id)"]
        O --> M["OrganizationMembership"]
        M --> U2[User]
    end
    
    subgraph "Constraint: user XOR organization"
        XOR["CheckConstraint:<br/>api_key_exactly_one_owner<br/>taskcredit_owner_xor_user_org"]
    end
    
    PA1 -.->|enforced by| XOR
    PA2 -.->|enforced by| XOR
    TC1 -.->|enforced by| XOR
    TC2 -.->|enforced by| XOR
    AK1 -.->|enforced by| XOR
    AK2 -.->|enforced by| XOR
```

**Sources:** [api/models.py:122-176](), [api/models.py:290-385]()

### Key Ownership Rules

| Entity | User Ownership | Organization Ownership | Enforcement |
|--------|---------------|------------------------|-------------|
| `ApiKey` | `user_id NOT NULL` | `organization_id NOT NULL` | [api/models.py:168-174]() |
| `TaskCredit` | `user_id NOT NULL` | `organization_id NOT NULL` | [api/models.py:375-384]() |
| `PersistentAgent` | `user_id NOT NULL` | `organization_id` (optional) | Agents always have a user, optionally have an org |
| `BrowserUseAgent` | `user_id NOT NULL` | N/A | Always user-owned |

The constraint pattern `(user__isnull=False, organization__isnull=True) | (user__isnull=True, organization__isnull=False)` ensures exactly one owner exists.

**Sources:** [api/models.py:156-175](), [api/models.py:350-385]()

---

## Core Entity Types

### Agent Hierarchy

```mermaid
graph TB
    subgraph "Agent Architecture"
        U[User] -->|creates| BUA[BrowserUseAgent]
        U -->|creates| PA[PersistentAgent]
        O[Organization] -.->|owns| PA
        
        PA -->|links to| BUA
        PA -->|has| Charter["charter: TextField"]
        PA -->|has| Schedule["schedule: CharField<br/>cron expression"]
        PA -->|has| LifeState["life_state: ACTIVE/EXPIRED"]
        
        BUA -->|has| Profile["Browser Profile<br/>(object storage)"]
        BUA -->|has| Proxy["preferred_proxy:<br/>ProxyServer FK"]
        
        PA -->|creates| Step[PersistentAgentStep]
        PA -->|creates| Msg[PersistentAgentMessage]
        PA -->|creates| Tool[PersistentAgentToolCall]
        
        BUA -->|creates| Task[BrowserUseAgentTask]
        Task -->|has| TaskStep[BrowserUseAgentTaskStep]
    end
```

**Sources:** [api/models.py:472-611](), [api/models.py:1131-1376]()

### Agent Relationships

**BrowserUseAgent** (`api.models.BrowserUseAgent`)
- Represents browser automation capability
- One-to-one relationship with `PersistentAgent`
- Manages Chrome profile persistence in object storage
- Auto-assigns `preferred_proxy` on creation via `select_random_proxy()`
- Enforces user agent limits via `AgentService.get_agents_available()`

**PersistentAgent** (`api.models.PersistentAgent`)
- Orchestrates long-running autonomous behavior
- References a `BrowserUseAgent` for web automation tasks
- Contains `charter` (mission/instructions) and `schedule` (cron expression)
- Tracks `life_state` (ACTIVE/EXPIRED) for activation management
- Can be owned by User or Organization (dual ownership)

**Sources:** [api/models.py:472-502](), [api/models.py:1131-1198]()

---

## Task Credit System

Credits are the platform's resource control mechanism. They gate agent execution, tool usage, and API operations.

### Credit Data Model

```mermaid
graph LR
    subgraph "TaskCredit Structure"
        TC[TaskCredit]
        TC -->|has| Credits["credits: Decimal(12,3)"]
        TC -->|has| Used["credits_used: Decimal(12,3)"]
        TC -->|has| Avail["available_credits: GeneratedField<br/>credits - credits_used"]
        TC -->|has| Granted["granted_date: DateTimeField"]
        TC -->|has| Expires["expiration_date: DateTimeField"]
        TC -->|has| Plan["plan: PlanNamesChoices"]
        TC -->|has| AddlTask["additional_task: BooleanField"]
        TC -->|has| GrantType["grant_type: GrantTypeChoices"]
    end
    
    subgraph "Ownership"
        TC -.->|user_id XOR organization_id| Owner[User or Organization]
    end
    
    subgraph "Consumption Links"
        TC <-->|consumed by| Step[PersistentAgentStep]
        TC <-->|consumed by| BUTask[BrowserUseAgentTask]
    end
```

**Sources:** [api/models.py:290-390]()

### Credit Configuration

The credit cost system uses a two-tier configuration:

1. **Default Cost** - Stored in `TaskCreditConfig` singleton ([api/models.py:393-427]())
2. **Per-Tool Overrides** - Stored in `ToolCreditCost` ([api/models.py:429-471]())

```python
# Cache-backed retrieval (5-minute TTL)
default_cost = get_default_task_credit_cost()  # util/tool_costs.py:101
tool_cost = get_tool_credit_cost("send_email")  # util/tool_costs.py:106
```

The `TaskCreditService` handles atomic consumption using `SELECT FOR UPDATE` locking to prevent race conditions.

**Sources:** [util/tool_costs.py:55-88](), [tasks/services.py:418-534]()

### Credit Granting Patterns

| Grant Type | Trigger | Owner | Characteristics |
|------------|---------|-------|-----------------|
| PLAN | Subscription cycle start | User or Org | Monthly recurring, expires at period end |
| ADDITIONAL_TASK | Overage usage | User or Org | Created on-demand, metered to Stripe |
| COMPENSATION | Admin action | User or Org | Manual grants for support/errors |
| PROMO | Marketing campaign | User or Org | Promotional credits |

**Sources:** [constants/grant_types.py](), [tasks/services.py:202-306](), [tasks/services.py:308-416]()

---

## The TASKS_UNLIMITED Constant

A special sentinel value `-1` represents unlimited credits:

```python
# util/constants/task_constants.py
TASKS_UNLIMITED = -1
```

When a user or organization has `TASKS_UNLIMITED` credits:
- Pre-processing credit gates return immediately ([api/agent/core/event_processing.py:836-854]())
- Usage tracking is bypassed
- No credit consumption occurs

This is used for:
- Internal/admin accounts
- Community Edition unlimited mode (`GOBII_ENABLE_COMMUNITY_UNLIMITED=True`)
- Special promotional plans

**Sources:** [util/constants/task_constants.py](), [tasks/services.py:109-125](), [api/agent/core/event_processing.py:836-854]()

---

## Credit Consumption Flow

### Atomic Consumption Pattern

```mermaid
sequenceDiagram
    participant Agent as PersistentAgent
    participant Service as TaskCreditService
    participant DB as Database
    
    Agent->>Service: check_and_consume_credit(owner)
    Service->>DB: SELECT FOR UPDATE<br/>available TaskCredit blocks
    DB-->>Service: Locked credit row(s)
    
    alt Sufficient Credits
        Service->>DB: credits_used = F('credits_used') + amount
        Service->>DB: COMMIT
        DB-->>Service: Updated credit
        Service-->>Agent: {"success": True, "credit": TaskCredit}
    else Insufficient Plan Credits
        alt Extra Tasks Allowed
            Service->>DB: CREATE additional_task TaskCredit
            Service->>Stripe: Report metered usage
            DB-->>Service: New credit
            Service-->>Agent: {"success": True, "credit": TaskCredit}
        else No Extra Tasks
            Service-->>Agent: {"success": False, "error_message": "..."}
        end
    end
```

**Sources:** [tasks/services.py:536-643](), [api/agent/core/event_processing.py:510-710]()

### Pre-Processing Credit Gate

Before agent event processing begins, `process_agent_events` checks credit availability:

```python
# api/agent/core/event_processing.py:836-854
available = TaskCreditService.get_user_task_credits_available(owner_user)

if available is not None and available != TASKS_UNLIMITED:
    most_expensive_cost = get_most_expensive_tool_cost()
    if Decimal(available) < most_expensive_cost:
        # Log system step: credit_insufficient
        # Exit early without processing
```

This prevents wasting compute on LLM calls when the agent cannot execute any tools.

**Sources:** [api/agent/core/event_processing.py:836-854]()

### Mid-Loop Tool Gating

During the agent reasoning loop, each tool invocation is gated:

```python
# api/agent/core/event_processing.py:510-710
def _ensure_credit_for_tool(agent, tool_name, span=None):
    cost = get_tool_credit_cost(tool_name)
    
    # Check daily limit
    daily_state = _get_agent_daily_credit_state(agent)
    if not _has_sufficient_daily_credit(daily_state, cost):
        # Create system step: daily_credit_limit_mid_loop
        return False
    
    # Check owner credits
    consumed = TaskCreditService.check_and_consume_credit(owner_user, amount=cost)
    if not consumed or not consumed.get('success'):
        # Create system step: credit_insufficient_mid_loop
        return False
    
    return cost
```

**Sources:** [api/agent/core/event_processing.py:510-710]()

---

## API Keys & Authentication

API keys provide programmatic access and implement the dual ownership model.

### ApiKey Structure

```mermaid
graph TB
    subgraph "ApiKey Model"
        AK[ApiKey]
        AK --> ID["id: UUIDField"]
        AK --> User["user: FK<br/>(nullable)"]
        AK --> Org["organization: FK<br/>(nullable)"]
        AK --> CreatedBy["created_by: FK<br/>(User)"]
        AK --> Name["name: CharField"]
        AK --> Prefix["prefix: CharField(8)<br/>(first 8 chars)"]
        AK --> Hash["hashed_key: CharField(64)<br/>(SHA256 hash)"]
        AK --> RawKey["raw_key: CharField(128)<br/>(stored once, display only)"]
        AK --> RevokedAt["revoked_at: DateTimeField<br/>(nullable)"]
    end
    
    subgraph "Constraints"
        UniqueUserName["UniqueConstraint:<br/>user + name"]
        UniqueOrgName["UniqueConstraint:<br/>organization + name"]
        ExactlyOne["CheckConstraint:<br/>user XOR organization"]
    end
    
    AK -.-> UniqueUserName
    AK -.-> UniqueOrgName
    AK -.-> ExactlyOne
```

**Sources:** [api/models.py:122-176]()

### Key Generation & Validation

```python
# api/models.py:178-180
@staticmethod
def generate() -> tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    return raw, _hash(raw)  # SHA256 hash

# api/models.py:265-266
def matches(self, raw: str) -> bool:
    return self.hashed_key == _hash(raw) and self.revoked_at is None
```

**Key Limits:**
- User API keys: `MAX_API_KEYS_PER_USER = 50` ([api/models.py:123]())
- Organization API keys: `MAX_API_KEYS_PER_ORG = 50` ([api/models.py:124]())

Enforced via `clean()` validation before creation ([api/models.py:213-257]()).

**Sources:** [api/models.py:177-180](), [api/models.py:213-257](), [api/models.py:265-266]()

### Console Context Resolution

The console interface uses `build_console_context()` to determine active ownership:

```python
# console/views.py:153-175
@cached_property
def api_key_context(self):
    resolved = build_console_context(self.request)
    if resolved.current_context.type == "organization":
        membership = resolved.current_membership
        return {
            "type": "organization",
            "organization": membership.org,
            "membership": membership,
            "can_manage": membership.role in API_KEY_MANAGE_ROLES,
        }
    return {
        "type": "user",
        "user": self.request.user,
        "can_manage": True,
    }
```

**Sources:** [console/views.py:149-181]()

---

## Plans & Subscriptions

Plans define credit entitlements and feature access.

### Plan Types

```mermaid
graph TB
    subgraph "User Plans"
        UFree[FREE<br/>10 credits/month]
        UStarter[STARTER<br/>100 credits/month]
        UPro[PRO<br/>500 credits/month]
        UPlus[PLUS<br/>1000 credits/month]
    end
    
    subgraph "Organization Plans"
        OFree[ORG_FREE<br/>50 credits/seat]
        OTeam[ORG_TEAM<br/>500 credits/seat]
        OBusiness[ORG_BUSINESS<br/>1000 credits/seat]
        OEnterprise[ORG_ENTERPRISE<br/>2500 credits/seat]
    end
    
    subgraph "Subscription Storage"
        UB[UserBilling]
        UB -->|subscription: CharField| UPlan[PlanNamesChoices]
        UB -->|max_extra_tasks: IntegerField| Overage
        
        OB[OrganizationBilling]
        OB -->|subscription: CharField| OPlan[OrganizationPlanNamesChoices]
        OB -->|purchased_seats: IntegerField| Seats
        OB -->|max_extra_tasks: IntegerField| OOverage
    end
```

**Sources:** [constants/plans.py](), [api/models.py:2034-2082](), [api/models.py:2211-2287]()

### Credit Provisioning

When a subscription is created or renewed:

```python
# tasks/services.py:202-306
def grant_subscription_credits(user, plan=None, invoice_id="", ...):
    # For users: grant plan.monthly_task_credits
    # Expiration aligns with subscription.current_period_end
    TaskCredit.objects.create(
        user=user,
        credits=credits_to_grant,
        granted_date=grant_date,
        expiration_date=expiration_date,
        plan=plan["id"],
        grant_type=GrantTypeChoices.PLAN,
        additional_task=False,
    )

# tasks/services.py:308-416
def grant_subscription_credits_for_organization(org, seats, ...):
    # For orgs: grant (plan.credits_per_seat * seats)
    credits_to_grant = Decimal(credits_per_seat) * Decimal(seats)
    TaskCredit.objects.create(
        organization=org,
        credits=credits_to_grant,
        ...
    )
```

**Sources:** [tasks/services.py:202-306](), [tasks/services.py:308-416]()

---

## Communication Channels

Agents can communicate via multiple channels, defined by the `CommsChannel` enum:

```python
# api/models.py:103-110
class CommsChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    SLACK = "slack", "Slack"
    DISCORD = "discord", "Discord"
    WEB = "web", "Web Chat"
    OTHER = "other", "Other"
```

Each channel has an associated tool:
- `EMAIL` → `send_email` tool
- `SMS` → `send_sms` tool
- `WEB` → `send_chat_message` tool

Channel-specific credit costs are retrieved via:

```python
# util/tool_costs.py:141-152
def get_tool_credit_cost_for_channel(channel: str) -> Decimal:
    tool_name = _CHANNEL_TOOL_NAMES.get(normalized_channel)
    return get_tool_credit_cost(tool_name)
```

**Sources:** [api/models.py:103-110](), [util/tool_costs.py:141-152]()

---

## Budget Cycles

Agent execution is tracked within **budget cycles** to prevent runaway resource consumption.

### Budget Context Structure

```python
# api/agent/core/budget.py
@dataclass
class BudgetContext:
    agent_id: str          # UUID of PersistentAgent
    budget_id: str         # Cycle identifier
    branch_id: str         # Execution branch (for follow-ups)
    depth: int             # Recursion depth
    max_steps: int         # Step limit per cycle
    max_depth: int         # Max recursion depth
```

Budget cycles are stored in Redis with TTL:
- `agent:{agent_id}:budget:status` → "active" | "closed"
- `agent:{agent_id}:budget:cycle_id` → current cycle ID
- `agent:{agent_id}:budget:branch:{branch_id}:depth` → outstanding children counter

**Sources:** [api/agent/core/budget.py](), [api/agent/core/event_processing.py:715-801]()

### Cycle Lifecycle

```mermaid
graph LR
    Trigger[Agent Triggered] --> FindOrStart[find_or_start_cycle]
    FindOrStart -->|existing| Reuse[Reuse active cycle]
    FindOrStart -->|none| Create[Create new cycle]
    
    Reuse --> Process[process_agent_events]
    Create --> Process
    
    Process --> ToolExec[Tool Execution]
    ToolExec -->|browser_use| BrowserTask[BrowserUseAgentTask]
    BrowserTask -->|on complete| FollowUp[Schedule follow-up]
    FollowUp -->|same budget_id| Process
    
    Process --> CheckClose{Depth = 0?}
    CheckClose -->|yes| Close[close_cycle]
    CheckClose -->|no| Wait[Wait for children]
```

**Sources:** [api/agent/core/event_processing.py:715-801](), [api/agent/core/budget.py]()

---

## Entity Relationship Overview

```mermaid
erDiagram
    User ||--o{ BrowserUseAgent : creates
    User ||--o{ PersistentAgent : creates
    User ||--o{ ApiKey : owns
    User ||--o{ TaskCredit : owns
    User ||--|| UserBilling : has
    
    Organization ||--o{ PersistentAgent : owns
    Organization ||--o{ ApiKey : owns
    Organization ||--o{ TaskCredit : owns
    Organization ||--|| OrganizationBilling : has
    Organization ||--o{ OrganizationMembership : has
    OrganizationMembership }o--|| User : member
    
    PersistentAgent ||--|| BrowserUseAgent : links_to
    PersistentAgent ||--o{ PersistentAgentStep : creates
    PersistentAgent ||--o{ PersistentAgentMessage : creates
    
    BrowserUseAgent ||--o{ BrowserUseAgentTask : creates
    BrowserUseAgentTask ||--o{ BrowserUseAgentTaskStep : has
    
    TaskCredit ||--o{ PersistentAgentStep : consumed_by
    TaskCredit ||--o{ BrowserUseAgentTask : consumed_by
    
    PersistentAgentStep ||--o| PersistentAgentToolCall : may_have
```

**Sources:** [api/models.py:122-2500]()

---

# Page: Agents

# Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/llm_config.py](api/agent/core/llm_config.py)
- [api/agent/tools/mcp_tools.py](api/agent/tools/mcp_tools.py)
- [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py](api/migrations/0155_persistentagent_daily_credit_limit_and_more.py)
- [api/tasks/browser_agent_tasks.py](api/tasks/browser_agent_tasks.py)
- [console/templates/console/agent_detail.html](console/templates/console/agent_detail.html)
- [console/templates/partials/_agent_list.html](console/templates/partials/_agent_list.html)
- [tests/unit/test_agent_event_processing_credits.py](tests/unit/test_agent_event_processing_credits.py)
- [tests/unit/test_browser_task_follow_up.py](tests/unit/test_browser_task_follow_up.py)
- [tests/unit/test_console.py](tests/unit/test_console.py)
- [tests/unit/test_event_processing_llm_selection.py](tests/unit/test_event_processing_llm_selection.py)
- [tests/unit/test_llm_failover.py](tests/unit/test_llm_failover.py)
- [tests/unit/test_mcp_tools.py](tests/unit/test_mcp_tools.py)
- [tests/utils/llm_seed.py](tests/utils/llm_seed.py)

</details>



## Purpose and Scope

This document describes the core agent models in the gobii-platform: `PersistentAgent` and `BrowserUseAgent`. These models form the foundation of the platform's multi-agent orchestration capabilities. An agent is an autonomous AI entity that can execute tasks, use tools, communicate via multiple channels, and operate on a schedule.

For information about creating agents via the provisioning service, see [Creating Agents](#4.1). For details on agent event processing and execution flow, see [Agent Event Processing](#4.3). For agent communication channels, see [Communication Systems](#7).

---

## Agent Architecture Overview

The platform uses a dual-model architecture where each autonomous agent consists of two linked database records:

```mermaid
graph TB
    subgraph "Agent Models"
        PA[PersistentAgent]
        BUA[BrowserUseAgent]
    end
    
    subgraph "Ownership"
        User[User]
        Org[Organization]
    end
    
    subgraph "Configuration"
        Charter["charter (TextField)"]
        Schedule["schedule (CharField)"]
        Contacts["Communication Endpoints"]
        Secrets["Encrypted Secrets"]
        Tools["Enabled MCP Tools"]
    end
    
    subgraph "Execution State"
        Steps["PersistentAgentStep"]
        Conversations["PersistentAgentConversation"]
        Tasks["BrowserUseAgentTask"]
    end
    
    User --> PA
    Org --> PA
    PA -->|"browser_use_agent (FK)"| BUA
    
    PA --> Charter
    PA --> Schedule
    PA --> Contacts
    PA --> Secrets
    PA --> Tools
    
    PA --> Steps
    PA --> Conversations
    BUA --> Tasks
```

**Sources:** [api/models.py](), [console/templates/console/agent_detail.html:1-550]()

---

## PersistentAgent Model

The `PersistentAgent` model represents the high-level autonomous agent. It handles:

- **Reasoning and decision-making** via LLM interactions
- **Tool orchestration** including MCP tools and browser automation
- **Communication** via email, SMS, web chat, and peer messaging
- **Scheduling** via cron expressions for recurring execution
- **Credit management** including daily limits and consumption tracking

### Key Fields

| Field | Type | Purpose |
|-------|------|---------|
| `user` | ForeignKey | Owner (can be null if org-owned) |
| `organization` | ForeignKey | Organization owner (can be null if user-owned) |
| `browser_use_agent` | OneToOneField | Linked browser automation agent |
| `name` | CharField | Display name |
| `charter` | TextField | Agent's purpose and instructions |
| `schedule` | CharField | Cron expression for scheduled execution |
| `is_active` | BooleanField | Whether agent can execute |
| `daily_credit_limit` | PositiveIntegerField | Max task credits per day (null = unlimited) |
| `life_state` | CharField | ACTIVE or EXPIRED (lifecycle state) |

### Lifecycle States

Agents have both an `is_active` flag (user-controlled pause/resume) and a `life_state` (system-managed expiration):

```mermaid
stateDiagram-v2
    [*] --> ACTIVE: Agent Created
    ACTIVE --> EXPIRED: No interaction for 7+ days
    EXPIRED --> ACTIVE: User messages agent or manually activates
    ACTIVE --> ACTIVE: is_active toggled (pause/resume)
    
    note right of ACTIVE
        is_active=True: Agent executes tasks
        is_active=False: Agent paused by user
    end note
    
    note right of EXPIRED
        Agent suspended due to inactivity
        Can be reactivated by user action
    end note
```

**Sources:** [api/models.py](), [api/agent/core/event_processing.py](), [console/templates/console/agent_detail.html:160-199]()

### Daily Credit Limits

Each agent can have a `daily_credit_limit` that constrains how many task credits it can consume in a 24-hour window:

- **Null value** = unlimited credits (common for Pro plans)
- **Integer value** = maximum credits per day
- **Tracking** = sum of `credits_cost` from `PersistentAgentStep` records for the current day
- **Reset** = daily at midnight in the agent owner's timezone
- **Enforcement** = checked both pre-processing and mid-loop during tool execution

When the limit is reached, event processing exits early with a `daily_credit_limit_exhausted` system step.

**Sources:** [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py:1-51](), [tests/unit/test_agent_event_processing_credits.py:148-182](), [console/templates/console/agent_detail.html:201-253]()

---

## BrowserUseAgent Model

The `BrowserUseAgent` model represents the browser automation component. It handles:

- **Browser profile persistence** via compressed archives in object storage
- **Proxy selection** for routing browser traffic
- **Browser task execution** using the `browser-use` library
- **File uploads and downloads** via the agent filespace

### Key Fields

| Field | Type | Purpose |
|-------|------|---------|
| `user` | ForeignKey | Owner of the browser agent |
| `name` | CharField | Display name |
| `preferred_proxy` | ForeignKey | Preferred proxy server for browser tasks |

### Browser Profile Management

Browser profiles are persisted to enable stateful browsing (cookies, local storage, etc.):

```mermaid
graph LR
    Task["BrowserUseAgentTask Created"] --> CheckProfile["Check for Profile in Storage"]
    CheckProfile -->|Exists| Download["Download & Decompress Profile"]
    CheckProfile -->|"Does Not Exist"| CreateTemp["Create Fresh Profile"]
    Download --> TempDir["Temporary Profile Directory"]
    CreateTemp --> TempDir
    
    TempDir --> Execute["Execute Browser Task"]
    Execute --> Prune["Prune Cache Directories"]
    Prune --> CheckSize{"Size > 500MB?"}
    CheckSize -->|Yes| Reset["Reset Profile"]
    CheckSize -->|No| Compress["Compress Profile"]
    
    Reset --> Upload["Upload to Storage"]
    Compress --> Upload
    Upload --> Cleanup["Delete Temporary Directory"]
```

Profile storage uses a sharded key structure: `browser_profiles/{uuid[:2]}/{uuid[2:4]}/{uuid}.tar.zst` to distribute millions of profiles across object storage prefixes.

**Sources:** [api/tasks/browser_agent_tasks.py:495-538](), [api/tasks/browser_agent_tasks.py:586-680]()

### Proxy Selection

Browser agents can use a `preferred_proxy` or fall back to the proxy selection algorithm. The `select_proxy_for_task()` function in [api/tasks/browser_agent_tasks.py:408-447]() handles:

1. **Override proxy** (if provided explicitly)
2. **Agent preferred proxy** (if configured)
3. **Health-checked proxy** (from the pool)
4. **No proxy** (in debug mode or when pool is exhausted)

**Sources:** [api/tasks/browser_agent_tasks.py:408-447](), [api/proxy_selection.py]()

---

## Agent Relationship and Responsibilities

The two models work together in a coordinated manner:

```mermaid
graph TB
    subgraph "PersistentAgent Responsibilities"
        PA_Plan["Plan Actions via LLM"]
        PA_Tools["Select Tools to Execute"]
        PA_Comms["Handle Communications"]
        PA_State["Maintain Conversation State"]
    end
    
    subgraph "BrowserUseAgent Responsibilities"
        BUA_Browse["Execute Browser Automation"]
        BUA_Profile["Persist Browser State"]
        BUA_Files["Download Files"]
        BUA_Proxy["Route via Proxy"]
    end
    
    subgraph "Execution Flow"
        Event["process_agent_events_task"] --> Loop["_run_agent_loop"]
        Loop --> LLM["LLM Completion"]
        LLM --> ToolCall{"Tool Call?"}
        ToolCall -->|"browse_web"| CreateTask["Create BrowserUseAgentTask"]
        CreateTask --> BrowserWorker["Browser Task Worker"]
        BrowserWorker --> FollowUp["Schedule Follow-up"]
        FollowUp --> Event
        ToolCall -->|"Other Tools"| Execute["Execute in Loop"]
        Execute --> Loop
    end
    
    PA_Plan --> Loop
    PA_Tools --> ToolCall
    PA_Comms --> Execute
    PA_State --> Loop
    
    BUA_Browse --> BrowserWorker
    BUA_Profile --> BrowserWorker
    BUA_Files --> BrowserWorker
    BUA_Proxy --> BrowserWorker
```

**Key Integration Points:**

1. **Task Creation**: `PersistentAgent` creates `BrowserUseAgentTask` records when the LLM calls `browse_web`
2. **Async Processing**: Browser tasks execute in separate Celery workers
3. **Follow-up Scheduling**: After browser tasks complete, `_schedule_agent_follow_up()` triggers the persistent agent to continue its reasoning loop
4. **Budget Cycle Continuity**: The follow-up can preserve the original budget cycle context or start fresh

**Sources:** [api/tasks/browser_agent_tasks.py:72-153](), [api/agent/core/event_processing.py](), [tests/unit/test_browser_task_follow_up.py:1-88]()

---

## Agent Creation and Deletion

### Creation Flow

Agents are created via the `PersistentAgentProvisioningService`:

```mermaid
sequenceDiagram
    participant User
    participant Form["Agent Creation Form"]
    participant Service["PersistentAgentProvisioningService"]
    participant DB["Database"]
    participant Celery["Celery Queue"]
    
    User->>Form: Submit charter & config
    Form->>Service: provision(user, org, charter, ...)
    Service->>DB: Create BrowserUseAgent
    Service->>DB: Create PersistentAgent
    Service->>DB: Apply template (if provided)
    Service->>Service: Configure email/SMS endpoints
    Service-->>Form: ProvisioningResult
    Form->>DB: transaction.on_commit
    DB->>Celery: process_agent_events_task.delay(agent_id)
```

**Sources:** [api/agent/provisioning/service.py](), [console/views.py]()

### Deletion Flow

Deleting a `PersistentAgent` also deletes the linked `BrowserUseAgent`:

```mermaid
graph LR
    Request["DELETE /agents/:id"] --> View["agent_delete view"]
    View --> QueryPA["Get PersistentAgent"]
    QueryPA --> DeletePA["agent.delete()"]
    DeletePA --> CascadeBA["CASCADE deletes BrowserUseAgent"]
    DeletePA --> CascadeTasks["CASCADE deletes BrowserUseAgentTask"]
    DeletePA --> CascadeSteps["CASCADE deletes PersistentAgentStep"]
    CascadeBA --> Response["200 OK"]
```

The deletion is protected by foreign key cascades, and the view handles edge cases where the `BrowserUseAgent` might be missing.

**Sources:** [console/views.py](), [tests/unit/test_console.py:23-148]()

---

## Agent Configuration

### Charter

The `charter` field is a free-form text description of the agent's purpose. It is injected into every LLM prompt as context:

```
You are an AI agent with the following charter:
{agent.charter}

Your task is to...
```

**Sources:** [api/agent/core/event_processing.py](), [console/templates/console/agent_detail.html:256-276]()

### Schedule

Agents can have a `schedule` field containing a cron expression. The Celery Beat scheduler triggers `process_agent_events_task` at the specified intervals.

**Example cron expressions:**
- `0 9 * * *` = daily at 9:00 AM
- `0 */6 * * *` = every 6 hours
- `0 0 * * 1` = weekly on Monday at midnight

**Sources:** [api/agent/core/event_processing.py](), [celery_app/tasks.py]()

### Communication Endpoints

Agents can have multiple communication endpoints:

- **Email**: `AgentEmailAccount` with IMAP/SMTP credentials
- **SMS**: `SmsNumber` provisioned via Twilio
- **Web Chat**: Built-in WebSocket-based chat interface
- **Peer Links**: Direct messaging to other agents

**Sources:** [api/models.py](), [console/templates/console/agent_detail.html:106-158]()

### Secrets

Agents can store encrypted secrets (API keys, passwords, etc.) as `PersistentAgentSecret` records. These are accessible during browser automation via the `sensitive_data` parameter.

**Sources:** [api/models.py](), [api/encryption.py](), [api/tasks/browser_agent_tasks.py:842-856]()

### MCP Tools

Agents can dynamically enable MCP tools via the `search_tools` function. Enabled tools are tracked in `PersistentAgentEnabledTool` with LRU eviction when the limit of 40 is reached.

**Sources:** [api/agent/tools/mcp_manager.py](), [api/agent/tools/mcp_tools.py:1-84](), [tests/unit/test_mcp_tools.py:1-553]()

---

## Agent Execution Context

### LLM Selection

Agents use a tiered LLM failover system with token-based selection. The `get_llm_config_with_failover()` function returns a prioritized list of LLM endpoints based on:

1. **Token count** of the current prompt
2. **Database-configured tiers** (via `PersistentTokenRange` and `PersistentLLMTier`)
3. **Weighted random selection** within each tier
4. **Availability** of API keys (admin-encrypted or environment variable)

**Token ranges:**
- **Small** (0-7,500 tokens): GPT-5/Google primary, Anthropic/GLM-4.5 fallback
- **Medium** (7,500-20,000 tokens): GLM-4.5 primary with mixed fallbacks
- **Large** (20,000+ tokens): GLM-4.5/Google primary, GPT-5/Anthropic fallback

**Sources:** [api/agent/core/llm_config.py:1-478](), [tests/unit/test_llm_failover.py:1-185]()

### Credit Gating

Agent execution is protected by two levels of credit checks:

1. **Pre-processing gate**: Before `_run_agent_loop()` begins, `TaskCreditService.get_user_task_credits_available()` checks for sufficient credits
2. **Mid-loop gate**: Before each tool execution, `_ensure_credit_for_tool()` verifies that the tool's cost can be covered

If either check fails in proprietary mode, a system step is created and execution halts:

- `credit_insufficient` (pre-processing)
- `credit_insufficient_mid_loop` (tool execution)
- `daily_credit_limit_exhausted` (daily limit reached)
- `daily_credit_limit_mid_loop` (daily limit reached during tool)

**Sources:** [api/agent/core/event_processing.py](), [tests/unit/test_agent_event_processing_credits.py:1-346]()

### Vision Support

LLM endpoints can declare `supports_vision` capability. When enabled, the agent can include screenshots in LLM prompts during browser automation. This is controlled at the endpoint level and passed as a hint to the execution layer.

**Sources:** [api/agent/core/llm_config.py:381-382](), [api/tasks/browser_agent_tasks.py:836-838]()

### Parallel Tool Calls

Some LLM endpoints support parallel tool calling (executing multiple tools in one turn). This is tracked via the `use_parallel_tool_calls` hint on endpoint configurations and passed to `litellm.completion()` when supported.

**Sources:** [api/agent/core/llm_config.py:384-387](), [tests/unit/test_event_processing_llm_selection.py:46-84]()

---

## Data Model Relationships

```mermaid
erDiagram
    User ||--o{ PersistentAgent : "owns"
    Organization ||--o{ PersistentAgent : "owns"
    PersistentAgent ||--|| BrowserUseAgent : "has"
    PersistentAgent ||--o{ PersistentAgentStep : "tracks"
    PersistentAgent ||--o{ PersistentAgentConversation : "maintains"
    PersistentAgent ||--o{ PersistentAgentEnabledTool : "enables"
    PersistentAgent ||--o{ PersistentAgentSecret : "stores"
    BrowserUseAgent ||--o{ BrowserUseAgentTask : "executes"
    BrowserUseAgent }o--|| ProxyServer : "prefers"
    
    PersistentAgent {
        uuid id PK
        uuid user_id FK
        uuid organization_id FK
        uuid browser_use_agent_id FK
        string name
        text charter
        string schedule
        boolean is_active
        int daily_credit_limit
        string life_state
    }
    
    BrowserUseAgent {
        uuid id PK
        uuid user_id FK
        string name
        uuid preferred_proxy_id FK
    }
    
    PersistentAgentStep {
        uuid id PK
        uuid agent_id FK
        text description
        decimal credits_cost
        timestamp created_at
    }
    
    BrowserUseAgentTask {
        uuid id PK
        uuid agent_id FK
        uuid user_id FK
        text prompt
        string status
    }
```

**Sources:** [api/models.py](), [api/migrations/]()

---

## Summary

The agent architecture separates concerns between high-level orchestration (`PersistentAgent`) and browser automation (`BrowserUseAgent`). This design enables:

- **Persistent state** across multiple execution cycles
- **Asynchronous browser tasks** that don't block the reasoning loop
- **Flexible ownership** (user or organization)
- **Resource control** via credit limits and daily caps
- **Multi-channel communication** with unified conversation tracking
- **Dynamic tool discovery** with LRU eviction

For implementation details on how agents process events and execute tools, see [Agent Event Processing](#4.3). For provisioning logic, see [Creating Agents](#4.1).

---

# Page: Task Credits

# Task Credits

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/migrations/0115_persistentagentstep_credits_fields.py](api/migrations/0115_persistentagentstep_credits_fields.py)
- [api/models.py](api/models.py)
- [console/views.py](console/views.py)
- [tasks/services.py](tasks/services.py)
- [tests/unit/test_persistent_agent_step_credits.py](tests/unit/test_persistent_agent_step_credits.py)
- [tests/unit/test_task_credit_service.py](tests/unit/test_task_credit_service.py)
- [tests/unit/test_tool_costs.py](tests/unit/test_tool_costs.py)
- [util/tool_costs.py](util/tool_costs.py)

</details>



## Purpose and Scope

This document describes the **task credit system**, which is the platform's primary resource control and monetization mechanism. Task credits gate all agent operations that consume compute resources (LLM calls, browser automation, tool execution, etc.). The system supports fractional credits, dual ownership (users and organizations), expiring credit blocks, and per-tool cost configuration.

For information about billing and subscription integration, see [Subscription Management](#5.2). For organization-specific billing and seat management, see [Organization Billing](#5.3). For usage analytics and reporting, see [Usage Analytics](#5.4).

---

## Credit Data Model

### TaskCredit Model

The `TaskCredit` model represents discrete blocks of credits granted to users or organizations. Each block has a grant date, expiration date, and tracks usage atomically.

```mermaid
erDiagram
    TaskCredit ||--o| User : "owned by (XOR)"
    TaskCredit ||--o| Organization : "owned by (XOR)"
    TaskCredit ||--o{ PersistentAgentStep : "consumed by"
    TaskCredit ||--o{ BrowserUseAgentTask : "consumed by"
    
    TaskCredit {
        UUID id PK
        UUID user_id FK_nullable
        UUID organization_id FK_nullable
        Decimal credits "Total credits in block"
        Decimal credits_used "Atomically updated"
        Decimal available_credits "Generated column"
        DateTime granted_date
        DateTime expiration_date
        String stripe_invoice_id
        String plan "PlanNamesChoices"
        Boolean additional_task "Overage flag"
        String grant_type "GrantTypeChoices"
        Boolean voided "Invalidation flag"
        Date grant_month "Generated from granted_date"
    }
```

**Sources:** [api/models.py:290-391]()

### Dual Ownership: Users vs Organizations

Credits can be owned by **either** a user **or** an organization, enforced by a database constraint. This enables both personal and team-based billing models.

```mermaid
graph TB
    subgraph "User Credits"
        UserCredit["TaskCredit<br/>user_id=123<br/>organization_id=NULL"]
        UserAgent["PersistentAgent<br/>user_id=123<br/>organization_id=NULL"]
        UserAgent -->|"consumes via<br/>PersistentAgentStep"| UserCredit
    end
    
    subgraph "Organization Credits"
        OrgCredit["TaskCredit<br/>user_id=NULL<br/>organization_id=456"]
        OrgAgent["PersistentAgent<br/>user_id=123<br/>organization_id=456"]
        OrgAgent -->|"consumes via<br/>PersistentAgentStep"| OrgCredit
    end
    
    CheckConstraint["DB Constraint:<br/>(user XOR organization)"]
    UserCredit -.->|enforced by| CheckConstraint
    OrgCredit -.->|enforced by| CheckConstraint
```

The ownership model is validated at the database level via `CHECK` constraint and at the application level via `TaskCredit.clean()`.

**Sources:** [api/models.py:375-385](), [tasks/services.py:158-198]()

### Credit Block Lifecycle

Credits are provisioned as blocks that expire on a specific date (typically aligned with subscription billing cycles). Blocks are consumed in **expiration order** (FIFO) to minimize waste.

| Phase | Description | Key Fields |
|-------|-------------|------------|
| **Provisioning** | Created when subscription starts/renews | `granted_date`, `expiration_date`, `stripe_invoice_id` |
| **Active** | Available for consumption | `granted_date <= now < expiration_date`, `voided=False` |
| **Consumption** | Atomically decremented via `SELECT FOR UPDATE` | `credits_used` incremented |
| **Expiration** | No longer consumable | `expiration_date < now` |
| **Voiding** | Administratively invalidated | `voided=True` |

**Sources:** [api/models.py:290-391](), [tasks/services.py:418-534]()

---

## Credit Configuration

### TaskCreditConfig

The `TaskCreditConfig` singleton model stores the **default credit cost** applied when no tool-specific override exists. Updating this record automatically invalidates the cache.

```mermaid
graph LR
    Admin["Admin updates<br/>TaskCreditConfig"] --> Save["save()<br/>triggers cache clear"]
    Save --> Cache["clear_tool_credit_cost_cache()"]
    Cache --> Refresh["Next request<br/>fetches new value"]
```

**Sources:** [api/models.py:393-427](), [util/tool_costs.py:21-23]()

### ToolCreditCost

Per-tool cost overrides are stored in the `ToolCreditCost` model. Tool names are **case-insensitive** and normalized on save.

| Tool Name | Credit Cost | Usage |
|-----------|-------------|-------|
| `send_email` | 0.90 | Outbound email via SMTP |
| `send_sms` | 0.35 | Outbound SMS via Twilio |
| `search_web` | 0.10 | Web search via MCP |
| `browse_web` | 0.50 | Browser automation task |
| *(default)* | 0.40 | All other tools |

**Sources:** [api/models.py:429-471](), [util/tool_costs.py:106-121]()

### TASKS_UNLIMITED Constant

The special value `-1` (defined as `TASKS_UNLIMITED`) indicates unlimited credits. This is used for:
- Community Edition when `GOBII_ENABLE_COMMUNITY_UNLIMITED=True`
- Organizations with `max_extra_tasks=-1`
- Users with unlimited overage plans

```python
# util/constants/task_constants.py
TASKS_UNLIMITED = -1
```

When `calculate_available_tasks()` returns `TASKS_UNLIMITED`, all credit checks pass without consumption.

**Sources:** [tasks/services.py:19](), [tasks/services.py:136-143]()

---

## Credit Provisioning

### Subscription-Based Granting

When a user subscribes (or their subscription renews), credits are granted via `TaskCreditService.grant_subscription_credits()`.

```mermaid
sequenceDiagram
    participant Stripe
    participant Webhook as handle_subscription_event
    participant Service as TaskCreditService
    participant DB as TaskCredit table
    
    Stripe->>Webhook: invoice.payment_succeeded
    Webhook->>Webhook: Extract invoice_id
    Webhook->>Service: grant_subscription_credits(user, invoice_id=...)
    Service->>DB: Check if invoice_id exists
    alt Invoice already processed
        DB-->>Service: Existing record
        Service-->>Webhook: Return 0 (idempotent)
    else New invoice
        Service->>Service: Get plan credits (e.g., 500)
        Service->>Service: Set expiration = current_period_end
        Service->>DB: CREATE TaskCredit
        DB-->>Service: New record
        Service-->>Webhook: Return credits granted
    end
```

**Key Parameters:**
- `credit_override`: Override default plan credits (for manual grants)
- `invoice_id`: Stripe invoice ID for idempotency
- `grant_date`: Defaults to `timezone.now()`
- `expiration_date`: Defaults to subscription `current_period_end`

**Sources:** [tasks/services.py:201-306]()

### Organization Seat-Based Credits

Organizations receive credits based on purchased seats: `credits_per_seat × purchased_seats`.

When seats change mid-cycle, the `replace_current=True` flag **refreshes** the existing credit block instead of creating a duplicate:

```python
# Renewal flow: reset usage on existing block
grant_subscription_credits_for_organization(
    org,
    seats=3,
    invoice_id="inv_renewal",
    replace_current=True,  # Resets credits_used to 0
)
```

**Sources:** [tasks/services.py:308-416]()

### Additional Tasks

When a user/organization exhausts their plan credits but has `allow_extra_tasks=True`, the system creates **additional task credits** on-demand:

```mermaid
graph TB
    ToolExec["Agent tool execution"] --> CheckPlan["Check plan credits"]
    CheckPlan -->|"available >= cost"| ConsumePlan["Consume from plan block"]
    CheckPlan -->|"available < cost"| CheckExtra{"Extra tasks<br/>allowed?"}
    
    CheckExtra -->|Yes| CreateExtra["Create TaskCredit<br/>additional_task=True<br/>credits=cost<br/>credits_used=cost"]
    CreateExtra --> MeterStripe["Report to Stripe<br/>metering API"]
    
    CheckExtra -->|No| DenyExec["Deny execution"]
```

Additional task credits are:
1. Created with `additional_task=True`
2. Immediately consumed (`credits_used = credits`)
3. Reported to Stripe's metering API for overage billing

**Sources:** [tasks/services.py:456-473](), [api/agent/core/event_processing.py:510-711]()

---

## Credit Consumption

### Atomic Consumption with SELECT FOR UPDATE

Credit consumption uses **database-level locking** to prevent race conditions when multiple workers consume credits concurrently.

```python
# tasks/services.py:476-511
with transaction.atomic():
    remaining = Decimal(plan_amount)
    while remaining > 0:
        credit = (
            TaskCredit.objects.select_for_update()
            .filter(
                user_id=user.id,
                expiration_date__gt=now,
                credits_used__lt=F("credits"),
                voided=False,
            )
            .order_by("expiration_date")  # FIFO by expiration
            .first()
        )
        
        if credit is None:
            raise ValidationError({"credits": "Insufficient task credits"})
        
        available_here = credit.credits - credit.credits_used
        consume_now = min(available_here, remaining)
        
        credit.credits_used = F("credits_used") + consume_now
        credit.save(update_fields=["credits_used"])
        credit.refresh_from_db()
        remaining -= consume_now
```

**Sources:** [tasks/services.py:476-511]()

### Fractional Credits

Credits are stored as `DecimalField(max_digits=12, decimal_places=3)`, enabling **fractional consumption** (e.g., 0.100 credits per tool call).

| Tool | Cost | Precision |
|------|------|-----------|
| `send_chat_message` | 0.000 | Free |
| `search_web` | 0.100 | One-tenth |
| `send_email` | 0.900 | Nine-tenths |
| `browse_web` | 0.500 | Half |

This allows fine-grained resource control and reduces waste.

**Sources:** [api/models.py:310-311](), [tests/unit/test_persistent_agent_step_credits.py:58-77]()

### Multi-Block Consumption

When a single operation costs more than the remaining balance in the current block, the system **spans multiple blocks**:

```mermaid
graph LR
    Request["Request 1.5 credits"] --> Block1["Block A<br/>available=1.0"]
    Block1 -->|"consume 1.0"| Block2["Block B<br/>available=2.0"]
    Block2 -->|"consume 0.5"| Complete["1.5 consumed"]
```

**Sources:** [tasks/services.py:476-511]()

### Credit-Step Linking

Each `PersistentAgentStep` and `BrowserUseAgentTask` is linked to the `TaskCredit` block it consumed from, enabling **audit trails** and usage analytics.

```mermaid
erDiagram
    PersistentAgentStep ||--o| TaskCredit : "task_credit_id"
    PersistentAgentStep {
        UUID task_credit_id FK
        Decimal credits_cost "Cost at time of creation"
    }
```

The `credits_cost` field is set at creation time and **never changes**, preserving historical pricing even if tool costs are later updated.

**Sources:** [api/models.py:1831-1845](), [api/migrations/0115_persistentagentstep_credits_fields.py]()

---

## Credit Gating in Agent Execution

Agent event processing has **two credit gates** to prevent runaway costs:

### Pre-Processing Gate

Before starting the agent loop, `process_agent_events()` checks if the owner has sufficient credits for at least one iteration:

```python
# api/agent/core/event_processing.py:891-933
available = TaskCreditService.get_user_task_credits_available(owner_user)
if available is not None and available != TASKS_UNLIMITED and available <= 0:
    step = PersistentAgentStep.objects.create(
        agent=agent,
        description="Processing skipped: insufficient task credits.",
    )
    PersistentAgentSystemStep.objects.create(
        step=step,
        code=PersistentAgentSystemStep.Code.PROCESS_EVENTS,
        notes="credit_insufficient",
    )
    return  # Exit early
```

**Sources:** [api/agent/core/event_processing.py:891-933]()

### Per-Tool Mid-Loop Gate

Before each tool execution, `_ensure_credit_for_tool()` performs a **just-in-time** credit check and consumption:

```mermaid
sequenceDiagram
    participant Loop as Agent Loop
    participant Gate as _ensure_credit_for_tool
    participant Service as TaskCreditService
    participant DB
    
    Loop->>Gate: tool_name="browse_web"
    Gate->>Gate: Get tool cost (0.5)
    Gate->>Gate: Check daily limit
    alt Daily limit exceeded
        Gate->>DB: Create SystemStep (daily_credit_limit_mid_loop)
        Gate-->>Loop: Return False (skip tool)
    else Daily limit OK
        Gate->>Service: check_and_consume_credit(user, amount=0.5)
        Service->>DB: SELECT FOR UPDATE + consume
        alt Consumption successful
            DB-->>Service: Credit consumed
            Service-->>Gate: {success: True, credit: ...}
            Gate-->>Loop: Return 0.5 (proceed)
        else Insufficient credits
            Service-->>Gate: {success: False}
            Gate->>DB: Create SystemStep (credit_insufficient_mid_loop)
            Gate-->>Loop: Return False (skip tool)
        end
    end
```

**Sources:** [api/agent/core/event_processing.py:510-711]()

### Daily Credit Limits

Each `PersistentAgent` can have a `daily_credit_limit`, which restricts how many credits it can consume per calendar day:

```python
# api/agent/core/event_processing.py:451-489
def _get_agent_daily_credit_state(agent: PersistentAgent) -> dict:
    today = dj_timezone.localdate()
    limit = agent.get_daily_credit_limit_value()  # e.g., Decimal("10.0")
    used = agent.get_daily_credit_usage(usage_date=today)
    remaining = limit - used if limit else None
    
    return {
        "limit": limit,
        "used": used,
        "remaining": remaining,
        "next_reset": (today + timedelta(days=1)).replace(hour=0, minute=0),
    }
```

Daily limits **do not consume credits** from the owner's balance; they merely gate execution until the next day.

**Sources:** [api/agent/core/event_processing.py:451-489](), [api/models.py:2089-2143]()

---

## Owner-Aware Operations

The `TaskCreditService` provides **owner-aware methods** that work identically for both `User` and `Organization` owners:

| Method | User Variant | Organization Variant |
|--------|--------------|---------------------|
| `get_owner_task_credits_granted(owner)` | `get_user_task_credits_granted(user)` | Aggregates `TaskCredit.filter(organization=org)` |
| `get_owner_task_credits_used(owner)` | `get_user_task_credits_used(user)` | Aggregates `credits_used` for org |
| `calculate_available_tasks_for_owner(owner)` | `calculate_available_tasks(user)` | `entitled - used` for org |
| `get_tasks_entitled_for_owner(owner)` | `get_tasks_entitled(user)` | `credits_per_seat × seats + extra` |

Internal helper `_is_organization_owner(owner)` determines routing:

```python
# tasks/services.py:588-594
def _is_organization_owner(owner) -> bool:
    return isinstance(owner, get_model("api", "Organization"))
```

**Sources:** [tasks/services.py:158-198](), [tasks/services.py:588-625]()

---

## Usage Tracking and Thresholds

The system monitors credit usage and publishes **threshold events** when users cross 75%, 90%, or 100% usage:

```mermaid
graph TB
    Consume["consume_credit()"] --> Threshold["handle_task_threshold(user)"]
    Threshold --> CalcPct["used_pct = used / entitled × 100"]
    CalcPct --> Check75{"crossed 75%?"}
    Check75 -->|Yes & new| Publish75["Analytics.publish_threshold_event(75)"]
    Check75 -->|No| Check90{"crossed 90%?"}
    Check90 -->|Yes & new| Publish90["Analytics.publish_threshold_event(90)"]
    Check90 -->|No| Check100{"crossed 100%?"}
    Check100 -->|Yes & new| Publish100["Analytics.publish_threshold_event(100)"]
```

Threshold crossings are tracked via `TaskCreditUsageThreshold` model to avoid duplicate notifications within the same billing period.

**Sources:** [tasks/services.py:753-819]()

---

## Tool Cost Configuration

### Default Cost

The default cost is retrieved from `TaskCreditConfig.default_task_cost` and cached for 5 minutes:

```python
# util/tool_costs.py:101-103
def get_default_task_credit_cost() -> Decimal:
    default_cost, _ = _get_tool_cost_config()
    return default_cost
```

**Sources:** [util/tool_costs.py:101-103]()

### Per-Tool Overrides

Tool-specific costs are retrieved via case-insensitive lookup:

```python
# util/tool_costs.py:106-121
def get_tool_credit_cost(tool_name: str | None) -> Decimal:
    default_cost, overrides = _get_tool_cost_config()
    key = _normalize_tool_name(tool_name)  # Strip and lowercase
    
    if key in overrides:
        return overrides[key]
    
    return default_cost
```

**Sources:** [util/tool_costs.py:106-121]()

### Channel-Specific Costs

Communication channels map to specific tools:

```python
# util/tool_costs.py:15-19
_CHANNEL_TOOL_NAMES: Dict[str, str] = {
    "email": "send_email",
    "sms": "send_sms",
    "web": "send_chat_message",
}
```

This enables credit gating on outbound messages via:

```python
cost = get_tool_credit_cost_for_channel(CommsChannel.EMAIL)
```

**Sources:** [util/tool_costs.py:141-152]()

---

## Code Entity Reference

### Key Classes and Functions

| Entity | Location | Purpose |
|--------|----------|---------|
| `TaskCredit` | [api/models.py:290-391]() | Credit block model |
| `TaskCreditConfig` | [api/models.py:393-427]() | Default cost singleton |
| `ToolCreditCost` | [api/models.py:429-471]() | Per-tool cost overrides |
| `TaskCreditService` | [tasks/services.py:107-819]() | Credit management service |
| `grant_subscription_credits()` | [tasks/services.py:201-306]() | User credit provisioning |
| `grant_subscription_credits_for_organization()` | [tasks/services.py:308-416]() | Org credit provisioning |
| `consume_credit()` | [tasks/services.py:418-534]() | Atomic consumption |
| `check_and_consume_credit()` | [tasks/services.py:536-567]() | Check + consume wrapper |
| `_ensure_credit_for_tool()` | [api/agent/core/event_processing.py:510-711]() | Mid-loop credit gate |
| `get_default_task_credit_cost()` | [util/tool_costs.py:101-103]() | Default cost retrieval |
| `get_tool_credit_cost()` | [util/tool_costs.py:106-121]() | Tool-specific cost lookup |
| `TASKS_UNLIMITED` | [util/constants/task_constants.py]() | Unlimited constant (-1) |

**Sources:** All file references above.

---

# Page: Organizations

# Organizations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/models.py](api/models.py)
- [console/forms.py](console/forms.py)
- [console/templates/console/organization_detail.html](console/templates/console/organization_detail.html)
- [console/templates/partials/_org_invite_modal.html](console/templates/partials/_org_invite_modal.html)
- [console/views.py](console/views.py)
- [constants/stripe.py](constants/stripe.py)
- [pages/signals.py](pages/signals.py)
- [tests/unit/test_organizations.py](tests/unit/test_organizations.py)
- [tests/unit/test_pages_signals.py](tests/unit/test_pages_signals.py)

</details>



Organizations provide multi-user workspaces where teams can collaborate on agents, share API keys, and pool task credits under a unified billing account. Organizations operate on a seat-based subscription model where each seat grants access to one team member.

For information about individual user billing, see [Subscription Management](#5.2). For organization-specific billing operations, see [Organization Billing](#5.3).

---

## Purpose and Scope

This document covers:
- Organization creation and lifecycle
- Membership management with role-based permissions
- Invitation and seat reservation system
- Seat-based billing and subscription handling
- Organization-owned resources (agents, API keys, credits)
- Console context switching between personal and organization workspaces

**Key Models**: `Organization`, `OrganizationMembership`, `OrganizationInvite`, `OrganizationBilling`

---

## Data Model Overview

### Core Models and Relationships

```mermaid
erDiagram
    User ||--o{ OrganizationMembership : "has"
    Organization ||--o{ OrganizationMembership : "has"
    Organization ||--|| OrganizationBilling : "has"
    Organization ||--o{ OrganizationInvite : "has"
    Organization ||--o{ PersistentAgent : "owns"
    Organization ||--o{ ApiKey : "owns"
    Organization ||--o{ TaskCredit : "owns"
    OrganizationBilling ||--o| Subscription : "stripe_subscription_id"
    
    Organization {
        uuid id PK
        string name
        string slug UK
        string description
        user created_by FK
        datetime created_at
        datetime updated_at
    }
    
    OrganizationMembership {
        uuid id PK
        org organization FK
        user user FK
        string role
        string status
        datetime joined_at
    }
    
    OrganizationInvite {
        uuid id PK
        org organization FK
        string email
        string role
        string token UK
        datetime expires_at
        datetime accepted_at
        user invited_by FK
    }
    
    OrganizationBilling {
        uuid id PK
        org organization OneToOne
        string stripe_customer_id
        string stripe_subscription_id
        int purchased_seats
        int pending_seat_quantity
        datetime pending_seat_effective_at
        string subscription
        int billing_cycle_anchor
    }
```

**Sources**: [api/models.py:1925-2190]()

---

### Organization Model

The `Organization` model represents a multi-user workspace with shared resources.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | CharField(128) | Display name |
| `slug` | SlugField(128) | URL-safe unique identifier |
| `description` | TextField | Optional description |
| `created_by` | ForeignKey(User) | Founding user |
| `created_at` | DateTimeField | Creation timestamp |
| `updated_at` | DateTimeField | Last modification timestamp |

**Key Properties**:
- `billing`: OneToOne relationship to `OrganizationBilling` (auto-created on save via signal)
- Reverse relations: `memberships`, `invites`, `persistent_agents`, `api_keys`, `task_credits`

**Sources**: [api/models.py:1925-1969]()

---

### OrganizationMembership Model

The `OrganizationMembership` model tracks user participation in organizations with role-based permissions.

#### Role Definitions

```python
class OrgRole(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"
    BILLING = "billing", "Billing"
```

#### Status Definitions

```python
class OrgStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
```

| Field | Type | Description |
|-------|------|-------------|
| `org` | ForeignKey(Organization) | Organization reference |
| `user` | ForeignKey(User) | User reference |
| `role` | CharField | One of: OWNER, ADMIN, MEMBER, BILLING |
| `status` | CharField | ACTIVE or SUSPENDED |
| `joined_at` | DateTimeField | Membership start timestamp |

**Constraints**:
- Unique together: `(org, user)`
- At least one OWNER required per organization (enforced in views)

**Sources**: [api/models.py:1972-2026]()

---

### Role Permission Matrix

The following table shows which actions each role can perform:

| Action | OWNER | ADMIN | BILLING | MEMBER |
|--------|-------|-------|---------|--------|
| View organization details | ✓ | ✓ | ✓ | ✓ |
| Create agents | ✓ | ✓ | - | ✓ |
| Manage own agents | ✓ | ✓ | - | ✓ |
| View all org agents | ✓ | ✓ | - | ✓ |
| Invite members | ✓ | ✓ | - | - |
| Remove members | ✓ | ✓ | - | - |
| Change member roles (except OWNER) | ✓ | ✓ | - | - |
| Promote to OWNER | ✓ | - | - | - |
| Purchase seats | ✓ | ✓ | ✓ | - |
| View billing | ✓ | ✓ | ✓ | - |
| Manage subscription | ✓ | ✓ | ✓ | - |
| View API keys | ✓ | ✓ | ✓ | - |
| Create API keys | ✓ | ✓ | - | - |
| Revoke/delete API keys | ✓ | ✓ | - | - |

**Constants**:
```python
BILLING_MANAGE_ROLES = {OrgRole.OWNER, OrgRole.ADMIN, OrgRole.BILLING}
MEMBER_MANAGE_ROLES = {OrgRole.OWNER, OrgRole.ADMIN}
API_KEY_MANAGE_ROLES = {OrgRole.OWNER, OrgRole.ADMIN}
API_KEY_VIEW_ROLES = {OrgRole.OWNER, OrgRole.ADMIN, OrgRole.BILLING}
```

**Sources**: [console/views.py:128-147]()

---

## Invitation System

### OrganizationInvite Model

The `OrganizationInvite` model manages pending invitations with seat reservation.

| Field | Type | Description |
|-------|------|-------------|
| `org` | ForeignKey(Organization) | Target organization |
| `email` | EmailField(255) | Invitee email (case-insensitive) |
| `role` | CharField | Role to grant upon acceptance |
| `token` | CharField(64) | Unique secure token for acceptance URL |
| `invited_by` | ForeignKey(User) | Inviter reference |
| `created_at` | DateTimeField | Invitation creation timestamp |
| `expires_at` | DateTimeField | Expiration (default: 7 days) |
| `accepted_at` | DateTimeField | Acceptance timestamp (null if pending) |

**Constraints**:
- Unique: `token`
- Unique together: `(org, email)` for non-accepted invites

**Sources**: [api/models.py:2029-2082]()

---

### Invitation Flow Sequence

```mermaid
sequenceDiagram
    participant Admin as "Admin User"
    participant View as "OrganizationDetailView"
    participant Form as "OrganizationInviteForm"
    participant Billing as "OrganizationBilling"
    participant Invite as "OrganizationInvite"
    participant Mail as "Email Service"
    participant Invitee as "Invited User"
    participant Accept as "OrgInviteAcceptView"
    participant Membership as "OrganizationMembership"
    
    Admin->>View: POST organization_detail
    View->>Form: validate(email, role)
    Form->>Billing: check seats_available
    
    alt No seats available
        Billing-->>Form: seats_available = 0
        Form-->>View: ValidationError
        View-->>Admin: Error: No seats available
    else Seats available
        Billing-->>Form: seats_available > 0
        Form->>Invite: create(org, email, role, token)
        Note over Invite: Seat is reserved<br/>expires_at = now + 7 days
        Invite->>Mail: send_invitation_email(token)
        Mail->>Invitee: Email with accept URL
        View-->>Admin: Success: Invitation sent
        
        Invitee->>Accept: GET org_invite_accept/<token>
        Accept->>Invite: get(token, accepted_at__isnull=True)
        
        alt Invite expired or invalid
            Accept-->>Invitee: Error: Invalid or expired
        else Valid invite
            Accept->>Membership: create(org, user, role, status=ACTIVE)
            Accept->>Invite: update(accepted_at=now)
            Accept-->>Invitee: Redirect to organization_detail
        end
    end
```

**Sources**: [console/views.py:1555-1664](), [console/forms.py:443-522](), [tests/unit/test_organizations.py:53-94]()

---

### Seat Reservation Logic

Pending invitations reserve seats from the organization's purchased capacity:

```python
# OrganizationBilling.seats_reserved (generated field)
seats_reserved = (
    active_memberships_count + pending_invites_count
)

# OrganizationBilling.seats_available (generated field)
seats_available = purchased_seats - seats_reserved
```

**Validation**: When creating an invite, `OrganizationInviteForm.clean()` checks:
1. `seats_available > 0`
2. No existing pending invite for the same email
3. User is not already a member

**Sources**: [api/models.py:2162-2190](), [console/forms.py:486-513]()

---

## Seat-Based Billing

### OrganizationBilling Model

Organizations use seat-based subscriptions where each seat grants one user access.

| Field | Type | Description |
|-------|------|-------------|
| `organization` | OneToOneField | Parent organization |
| `stripe_customer_id` | CharField(128) | Stripe Customer ID |
| `stripe_subscription_id` | CharField(128) | Stripe Subscription ID |
| `purchased_seats` | PositiveIntegerField | Number of seats purchased |
| `subscription` | CharField(32) | Plan name (e.g., "org_team") |
| `billing_cycle_anchor` | PositiveIntegerField | Day of month for billing |
| `pending_seat_quantity` | PositiveIntegerField | Scheduled seat change |
| `pending_seat_effective_at` | DateTimeField | When pending change takes effect |

**Generated Fields**:
- `seats_reserved`: Count of active members + pending invites
- `seats_available`: `purchased_seats - seats_reserved`

**Sources**: [api/models.py:2085-2190]()

---

### Seat Purchase Flow

Organizations purchase seats through Stripe Checkout or Billing Portal:

```mermaid
graph TB
    Start["Admin clicks 'Manage Seats'"]
    CheckSub{"Has active<br/>subscription?"}
    
    Start --> CheckSub
    
    CheckSub -->|No| Checkout["Stripe Checkout Session"]
    Checkout --> CheckoutForm["OrganizationSeatPurchaseForm"]
    CheckoutForm --> CreateSession["stripe.checkout.Session.create"]
    CreateSession --> StripeHosted["Stripe-hosted checkout"]
    StripeHosted --> WebhookCreate["Webhook: subscription.created"]
    
    CheckSub -->|Yes| Portal["Stripe Billing Portal"]
    Portal --> RetrieveSub["stripe.Subscription.retrieve"]
    RetrieveSub --> FindLicensed{"Find licensed item<br/>in subscription"}
    
    FindLicensed -->|Not found| Error["Error: No seat item found"]
    FindLicensed -->|Found| CheckOverage{"Has overage SKU?"}
    
    CheckOverage -->|Yes| DetachOverage["Detach overage item<br/>temporarily"]
    CheckOverage -->|No| BuildPortal["Build portal session"]
    DetachOverage --> SetMetadata["Set metadata:<br/>org_overage_sku_state"]
    SetMetadata --> BuildPortal
    
    BuildPortal --> PortalCreate["stripe.billing_portal.Session.create<br/>flow_data: subscription_update_confirm"]
    PortalCreate --> StripePortal["Stripe-hosted portal"]
    StripePortal --> WebhookUpdate["Webhook: subscription.updated"]
    
    WebhookCreate --> UpdateBilling["Update OrganizationBilling<br/>purchased_seats"]
    WebhookUpdate --> UpdateBilling
    UpdateBilling --> GrantCredits["Grant credits for new seats"]
    GrantCredits --> End["Complete"]
    Error --> End
```

**Sources**: [console/views.py:1810-2061](), [pages/signals.py:233-597]()

---

### Overage SKU Management

Organizations using the overage SKU (metered additional tasks) require special handling during seat updates:

**Problem**: Stripe Billing Portal cannot modify subscriptions with multiple line items when using `subscription_update_confirm` flow.

**Solution**: Temporarily detach the overage SKU, allow seat update, then reattach.

#### Detach Flow

```python
# console/views.py:_detach_org_overage_item
def _detach_org_overage_item(subscription, overage_price_id, org_id, request):
    # 1. Find overage item in subscription
    overage_item = find_item_by_price_id(subscription, overage_price_id)
    
    # 2. Delete the subscription item
    stripe.SubscriptionItem.delete(overage_item["id"])
    
    # 3. Mark subscription metadata
    stripe.Subscription.modify(
        subscription["id"],
        metadata={ORG_OVERAGE_STATE_META_KEY: ORG_OVERAGE_STATE_DETACHED_PENDING}
    )
    
    # 4. Store in session for reattachment
    _set_overage_detach_session(request, org_id, subscription["id"], overage_price_id)
```

#### Reattach Flow

When the subscription webhook arrives with updated seats:

```python
# pages/signals.py:handle_subscription_event (org branch)
if has_overage_item == False:
    overage_state = metadata.get(ORG_OVERAGE_STATE_META_KEY)
    seat_delta = new_seats - prev_seats
    
    # Reattach if not in detached_pending state OR seats changed
    if overage_state != DETACHED_PENDING or seat_delta != 0:
        stripe.SubscriptionItem.create(
            subscription=subscription_id,
            price=overage_price_id
        )
        stripe.Subscription.modify(
            subscription_id,
            metadata={ORG_OVERAGE_STATE_META_KEY: ""}
        )
```

**Constants**: [constants/stripe.py:1-5]()

**Sources**: [console/views.py:252-350](), [pages/signals.py:472-549]()

---

## Credit Provisioning for Organizations

Organizations receive credits based on seat count and plan configuration.

### Subscription Webhook Handler

```mermaid
graph TB
    Webhook["Stripe Webhook:<br/>subscription.created/updated"]
    Parse["Parse subscription payload"]
    FindOwner{"Identify owner<br/>via customer"}
    
    Webhook --> Parse
    Parse --> FindOwner
    
    FindOwner -->|No owner| Ignore["Ignore webhook"]
    FindOwner -->|User| UserFlow["User billing flow<br/>(see Subscription Mgmt)"]
    FindOwner -->|Organization| OrgFlow["Organization flow"]
    
    OrgFlow --> ExtractSeats["Extract quantity from<br/>licensed item"]
    ExtractSeats --> CalcDelta["seat_delta =<br/>new_seats - prev_seats"]
    CalcDelta --> CheckDelta{"seat_delta > 0?"}
    
    CheckDelta -->|No| SkipGrant["Skip credit grant"]
    CheckDelta -->|Yes| CheckReason{"billing_reason?"}
    
    CheckReason -->|subscription_cycle| GrantReplace["Grant credits<br/>replace_current=True"]
    CheckReason -->|Other| GrantDelta["Grant credits<br/>seats=seat_delta"]
    
    GrantReplace --> UpdateBilling["Update OrganizationBilling:<br/>purchased_seats<br/>billing_cycle_anchor"]
    GrantDelta --> UpdateBilling
    SkipGrant --> UpdateBilling
    UpdateBilling --> End["Complete"]
    Ignore --> End
```

**Key Logic**:
- `billing_reason == "subscription_cycle"`: Full renewal, replace all credits
- `billing_reason == "subscription_update"` or `"subscription_create"`: Grant credits for seat delta only
- Seat decreases: No credit grant (no clawback)

**Sources**: [pages/signals.py:233-597]()

---

### TaskCreditService for Organizations

```python
# tasks/services.py:TaskCreditService
@classmethod
def grant_subscription_credits_for_organization(
    cls,
    organization: Organization,
    plan: dict,
    seats: int,
    invoice_id: str = "",
    replace_current: bool = False,
    subscription=None,
):
    # Calculate credits: seats * credits_per_seat
    credits_per_seat = plan.get("credits_per_seat", 0)
    total_credits = Decimal(seats) * Decimal(credits_per_seat)
    
    # Determine expiration from subscription
    expiration_date = subscription.current_period_end
    
    if replace_current:
        # Void existing non-additional credits
        TaskCredit.objects.filter(
            organization=organization,
            additional_task=False,
            voided=False,
        ).update(voided=True)
    
    # Create new TaskCredit block
    TaskCredit.objects.create(
        organization=organization,
        credits=total_credits,
        granted_date=timezone.now(),
        expiration_date=expiration_date,
        plan=plan["id"],
        grant_type=GrantTypeChoices.PLAN,
    )
```

**Note**: Organization credits use `organization` FK instead of `user` FK in `TaskCredit` model.

**Sources**: [api/models.py:290-309](), Referenced in webhook handler

---

## Organization-Owned Resources

### Persistent Agents

Agents can be owned by an organization instead of a user:

```python
# api/models.py:PersistentAgent
class PersistentAgent(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    organization = models.ForeignKey(Organization, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(user__isnull=False, organization__isnull=True)
                    | Q(user__isnull=True, organization__isnull=False)
                ),
                name="persistent_agent_owner_xor",
            )
        ]
```

**Ownership Rules**:
- Exactly one of `user` or `organization` must be set (enforced by CHECK constraint)
- Organization-owned agents consume credits from organization's `TaskCredit` pool
- All organization members can view/interact with organization agents

**Sources**: [api/models.py:1156-1262]()

---

### API Keys

API keys can be owned by organizations:

```python
# api/models.py:ApiKey
class ApiKey(models.Model):
    MAX_API_KEYS_PER_ORG = 50
    
    user = models.ForeignKey(User, null=True, blank=True)
    organization = models.ForeignKey(Organization, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name="created_api_keys")
    
    @classmethod
    def create_for_org(cls, organization, *, created_by, name="default"):
        raw, hashed = cls.generate()
        return cls.objects.create(
            organization=organization,
            created_by=created_by,
            name=name,
            prefix=raw[:8],
            hashed_key=hashed,
            raw_key=raw,
        )
```

**Permission Enforcement**:
- API keys inherit organization permissions when authenticating
- Agents created via org API key are automatically org-owned
- API key management requires `API_KEY_MANAGE_ROLES` (OWNER or ADMIN)
- Viewing API keys requires `API_KEY_VIEW_ROLES` (OWNER, ADMIN, or BILLING)

**Sources**: [api/models.py:122-277](), [console/views.py:149-182]()

---

## Console Context Switching

Users can switch between personal workspace and organization workspaces.

### Context Resolution

```python
# console/context_helpers.py:build_console_context
def build_console_context(request):
    # 1. Check for org_id in session
    active_org_id = request.session.get("active_org_id")
    
    if active_org_id:
        # 2. Verify active membership exists
        membership = OrganizationMembership.objects.filter(
            org_id=active_org_id,
            user=request.user,
            status=OrganizationMembership.OrgStatus.ACTIVE,
        ).select_related("org").first()
        
        if membership:
            return ConsoleContext(
                type="organization",
                id=membership.org.id,
                name=membership.org.name,
                membership=membership,
            )
    
    # 3. Fall back to personal context
    return ConsoleContext(
        type="user",
        id=request.user.id,
        email=request.user.email,
    )
```

**Context Storage**: 
- Stored in session: `request.session["active_org_id"]`
- Cleared when user explicitly switches to personal workspace
- Automatically cleared if membership becomes invalid

**Sources**: [console/context_helpers.py:1-89]() (referenced in views)

---

### Context-Aware Views

Views use `ConsoleViewMixin` to inject context into templates:

```python
# console/mixins.py:ConsoleViewMixin
class ConsoleViewMixin(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Build and inject console context
        resolved = build_console_context(self.request)
        context['current_context'] = {
            'type': resolved.type,
            'id': resolved.id,
            'name': resolved.name,
        }
        context['current_membership'] = resolved.membership
        
        # List all user's organizations
        context['organizations'] = Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__status=OrganizationMembership.OrgStatus.ACTIVE,
        ).distinct()
        
        return context
```

**Context-Dependent Behavior**:
- Agent listings filter by `organization_id` when in org context
- Credit availability calculated from org `TaskCredit` records
- Dashboard metrics aggregate org-owned resources
- Billing views show org subscription when in org context

**Sources**: [console/views.py:351-577](), [console/mixins.py:1-85]() (referenced)

---

## Database Schema Summary

### Key Constraints and Indexes

```sql
-- Organization uniqueness
ALTER TABLE api_organization ADD CONSTRAINT unique_slug UNIQUE (slug);

-- Membership uniqueness
ALTER TABLE api_organizationmembership 
    ADD CONSTRAINT unique_org_user UNIQUE (org_id, user_id);

-- Invite uniqueness
ALTER TABLE api_organizationinvite 
    ADD CONSTRAINT unique_pending_invite 
    UNIQUE (org_id, email) 
    WHERE accepted_at IS NULL;

-- Billing one-to-one
ALTER TABLE api_organizationbilling 
    ADD CONSTRAINT unique_organization UNIQUE (organization_id);

-- Owner XOR constraints
ALTER TABLE api_apikey 
    ADD CONSTRAINT api_key_exactly_one_owner 
    CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    );

ALTER TABLE api_persistentagent 
    ADD CONSTRAINT persistent_agent_owner_xor 
    CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    );

ALTER TABLE api_taskcredit 
    ADD CONSTRAINT taskcredit_owner_xor_user_org 
    CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    );
```

**Sources**: [api/models.py:156-175](), [api/models.py:373-385](), [api/models.py:1972-2026]()

---

## Usage Example: Organization Lifecycle

### 1. Create Organization

```python
org = Organization.objects.create(
    name="Acme Corp",
    slug="acme",
    created_by=founder_user,
)
# OrganizationBilling auto-created via post_save signal
```

### 2. Add Founder as Owner

```python
OrganizationMembership.objects.create(
    org=org,
    user=founder_user,
    role=OrganizationMembership.OrgRole.OWNER,
    status=OrganizationMembership.OrgStatus.ACTIVE,
)
```

### 3. Purchase Seats via Stripe

```python
# User completes Stripe Checkout
# Webhook receives subscription.created event
# Signal handler in pages/signals.py:
#   - Updates org.billing.purchased_seats
#   - Grants credits via TaskCreditService
```

### 4. Invite Team Member

```python
invite = OrganizationInvite.objects.create(
    org=org,
    email="engineer@example.com",
    role=OrganizationMembership.OrgRole.MEMBER,
    invited_by=founder_user,
    expires_at=timezone.now() + timedelta(days=7),
)
# Email sent with acceptance link
```

### 5. Accept Invitation

```python
# User clicks link: /orgs/invite/<token>/accept/
# View creates membership:
membership = OrganizationMembership.objects.create(
    org=invite.org,
    user=invitee_user,
    role=invite.role,
    status=OrganizationMembership.OrgStatus.ACTIVE,
)
invite.accepted_at = timezone.now()
invite.save()
```

### 6. Create Organization-Owned Agent

```python
agent = PersistentAgent.objects.create(
    organization=org,
    charter="Monitor social media daily",
)
# Agent consumes credits from org.task_credits
```

**Sources**: [api/models.py:1925-2190](), [console/views.py:1555-1664](), [tests/unit/test_organizations.py:31-151]()

---

# Page: Agent Management

# Agent Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agents/services.py](agents/services.py)
- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/models.py](api/models.py)
- [console/templates/partials/_agent_contact_form.html](console/templates/partials/_agent_contact_form.html)
- [console/views.py](console/views.py)
- [pages/templates/ai_directory/detail.html](pages/templates/ai_directory/detail.html)
- [pages/templates/ai_directory/index.html](pages/templates/ai_directory/index.html)
- [pages/templates/home.html](pages/templates/home.html)
- [pages/views.py](pages/views.py)
- [tests/unit/test_agent_limits.py](tests/unit/test_agent_limits.py)
- [tests/unit/test_ai_employee_directory.py](tests/unit/test_ai_employee_directory.py)
- [tests/unit/test_console_context.py](tests/unit/test_console_context.py)

</details>



## Purpose and Scope

This document covers the creation, configuration, and lifecycle management of persistent agents in the gobii-platform. Agent management encompasses quota enforcement, provisioning workflows, ownership models (personal vs organization), and template-based agent creation.

For details on how agents execute tasks and process events, see [Agent Event Processing](#4.3). For credit consumption and billing integration, see [TaskCreditService](#5.1). For organization-level agent ownership, see [Organizations](#3.3).

---

## Core Data Models

The platform uses a dual-agent architecture where every `PersistentAgent` wraps a `BrowserUseAgent`. This separation allows the persistent agent to manage long-running state, schedules, and communication endpoints, while the browser agent handles task execution and browser profile management.

### Dual-Agent Architecture

```mermaid
graph TB
    subgraph "Agent Models"
        PA[PersistentAgent]
        BA[BrowserUseAgent]
        
        PA -->|browser_use_agent| BA
        PA -->|user| User
        PA -->|organization?| Org
        BA -->|user| User
        BA -->|preferred_proxy?| Proxy
    end
    
    subgraph "Related Models"
        PAMessage[PersistentAgentMessage]
        PAStep[PersistentAgentStep]
        PAEndpoint[PersistentAgentCommsEndpoint]
        BATask[BrowserUseAgentTask]
        
        PA -->|messages| PAMessage
        PA -->|steps| PAStep
        PA -->|endpoints| PAEndpoint
        BA -->|tasks| BATask
    end
    
    subgraph "State Management"
        PA -->|life_state| LifeState["LifeState.ACTIVE<br/>LifeState.EXPIRED"]
        PA -->|is_active| IsActive["Boolean flag"]
    end
```

**Sources:** [api/models.py:1095-1223](), [api/models.py:472-611]()

### PersistentAgent Fields

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Primary key |
| `user` | ForeignKey | Owner (always set) |
| `organization` | ForeignKey | Org ownership (optional) |
| `browser_use_agent` | ForeignKey | Wrapped browser agent |
| `name` | CharField | Display name |
| `charter` | TextField | Agent instructions/mission |
| `schedule` | CharField | Cron expression for execution |
| `life_state` | CharField | ACTIVE or EXPIRED |
| `is_active` | Boolean | Soft deletion flag |
| `last_interaction_at` | DateTimeField | Last activity timestamp |
| `daily_credit_limit` | DecimalField | Per-agent daily cap |

**Sources:** [api/models.py:1095-1223]()

### BrowserUseAgent Fields

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Primary key |
| `user` | ForeignKey | Owner |
| `name` | CharField | Display name |
| `preferred_proxy` | ForeignKey | Proxy server selection |
| `created_at` | DateTimeField | Creation timestamp |

**Sources:** [api/models.py:472-611]()

---

## Agent Provisioning Flow

Agent creation follows a multi-step workflow involving quota validation, dual-model creation, and optional template application. The `PersistentAgentProvisioningService` orchestrates this process.

### Provisioning Sequence

```mermaid
sequenceDiagram
    participant User
    participant HomeView
    participant ContactView
    participant ProvService as PersistentAgentProvisioningService
    participant QuotaCheck as AgentService.get_agents_available
    participant DB
    participant Celery
    
    User->>HomeView: POST charter
    HomeView->>HomeView: Store in session['agent_charter']
    HomeView-->>User: Redirect to contact form
    
    User->>ContactView: Submit contact preferences
    ContactView->>QuotaCheck: Check quota
    QuotaCheck->>DB: Count existing agents
    QuotaCheck-->>ContactView: Available slots
    
    alt Quota exceeded
        ContactView-->>User: Validation error
    else Quota available
        ContactView->>ProvService: provision(user, org, charter, contacts)
        
        ProvService->>DB: Create BrowserUseAgent
        DB-->>ProvService: browser_agent
        
        ProvService->>DB: Create PersistentAgent
        DB-->>ProvService: persistent_agent
        
        alt Template in session
            ProvService->>ProvService: Apply template defaults
            ProvService->>DB: Set schedule, tools, etc
        end
        
        ProvService->>DB: Create endpoints
        ProvService-->>ContactView: ProvisioningResult
        
        ContactView->>DB: transaction.on_commit
        DB->>Celery: process_agent_events_task.delay(agent.id)
        
        ContactView-->>User: Redirect to agent detail
    end
```

**Sources:** [pages/views.py:198-244](), [console/views.py:1490-1691](), [api/services/persistent_agents.py:1-200]()

### Provisioning Service Methods

The `PersistentAgentProvisioningService` exposes a single `provision` method that handles the entire creation process:

```python
# api/services/persistent_agents.py
def provision(
    user: User,
    organization: Organization | None,
    charter: str,
    contacts: dict,
    template_code: str | None = None,
) -> ProvisioningResult
```

**Key responsibilities:**
1. Validate quota availability via `AgentService.get_agents_available`
2. Create `BrowserUseAgent` with random proxy assignment
3. Create `PersistentAgent` linked to browser agent
4. Apply template defaults if `template_code` provided
5. Create communication endpoints based on `contacts` dict
6. Return `ProvisioningResult` with success/error status

**Sources:** [api/services/persistent_agents.py:50-150](), [console/views.py:1490-1691]()

---

## Agent Quota System

The platform enforces multi-level quota constraints to prevent runaway agent creation. The quota system operates at three levels: per-user quotas, plan-based limits, and a global safety cap.

### Quota Enforcement Layers

```mermaid
graph TB
    subgraph "Quota Check Flow"
        AgentCreate[Agent Creation Request]
        AgentCreate --> ServiceCheck[AgentService.get_agents_available]
        
        ServiceCheck --> CommunityCheck{Community<br/>Unlimited<br/>Mode?}
        CommunityCheck -->|Yes| SetMax[user_limit = MAX_AGENT_LIMIT]
        CommunityCheck -->|No| PlanCheck{Has<br/>Unlimited<br/>Plan?}
        
        PlanCheck -->|Yes| SetMax
        PlanCheck -->|No| QuotaLookup[Load UserQuota]
        
        QuotaLookup --> QuotaExists{Quota<br/>Exists?}
        QuotaExists -->|No| Return0[Return 0]
        QuotaExists -->|Yes| CalcLimit["user_limit = min(quota.agent_limit, MAX_AGENT_LIMIT)"]
        
        SetMax --> CalcRemaining
        CalcLimit --> CalcRemaining
        CalcRemaining["remaining = max(user_limit - agents_in_use, 0)"]
        
        CalcRemaining --> FinalCheck{remaining > 0?}
        FinalCheck -->|Yes| AllowCreate[Allow Creation]
        FinalCheck -->|No| BlockCreate[Raise ValidationError]
    end
    
    subgraph "Constants"
        MaxCap["MAX_AGENT_LIMIT = 1000"]
        Unlimited["AGENTS_UNLIMITED = -1"]
    end
```

**Sources:** [agents/services.py:44-97](), [api/models.py:278-288](), [config/plans.py:10-15]()

### UserQuota Model

```python
# api/models.py
class UserQuota(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agent_limit = models.PositiveIntegerField(default=5)
    max_agent_contacts = models.PositiveIntegerField(null=True, blank=True)
```

**Quota sources:**
- **Default plan limits**: Defined in `PLAN_CONFIG` (e.g., Free = 5, Startup = 20)
- **Per-user overrides**: `UserQuota.agent_limit` takes precedence
- **Safety cap**: `MAX_AGENT_LIMIT = 1000` applied to all users
- **Community mode**: `GOBII_ENABLE_COMMUNITY_UNLIMITED=True` bypasses limits

**Sources:** [api/models.py:278-288](), [agents/services.py:44-97](), [tests/unit/test_agent_limits.py:1-284]()

### Validation Hooks

Agent creation enforces quotas via model-level `clean()` validation:

```python
# api/models.py:503-513
def clean(self):
    super().clean()
    if self._state.adding and getattr(self, 'user_id', None):
        agents_available = AgentService.get_agents_available(self.user)
        if agents_available <= 0:
            raise ValidationError("Agent limit reached for this user.")
```

**Sources:** [api/models.py:503-513]()

---

## Ownership Models: Personal vs Organization

Agents can be owned either by individual users (personal) or by organizations (shared). Ownership determines access control, credit consumption, and billing scope.

### Ownership Resolution

```mermaid
graph TB
    subgraph "Agent Ownership Determination"
        Agent[PersistentAgent]
        Agent --> OrgSet{organization_id<br/>not null?}
        
        OrgSet -->|Yes| OrgOwned["Owner: Organization<br/>Credits: org.task_credits<br/>Billing: org.billing"]
        OrgSet -->|No| UserOwned["Owner: User<br/>Credits: user.task_credits<br/>Billing: user.billing"]
    end
    
    subgraph "Console Context"
        Session["request.session"]
        Session --> CtxType{context_type}
        
        CtxType -->|personal| ShowPersonal["Filter: user=request.user<br/>organization__isnull=True"]
        CtxType -->|organization| VerifyMembership{Active<br/>Membership?}
        
        VerifyMembership -->|Yes| ShowOrg["Filter: organization_id=context_id"]
        VerifyMembership -->|No| Forbidden403["HTTP 403"]
    end
    
    subgraph "Creation Permissions"
        CreateAttempt[Create Agent Request]
        CreateAttempt --> CheckContext{Context Type?}
        
        CheckContext -->|personal| AllowPersonal[Create with user=request.user]
        CheckContext -->|organization| CheckRole{Role in<br/>OWNER/ADMIN?}
        
        CheckRole -->|Yes| AllowOrg["Create with organization=org"]
        CheckRole -->|No| BlockOrg["Show permission warning"]
    end
```

**Sources:** [console/context_helpers.py:1-150](), [console/views.py:1490-1691](), [tests/unit/test_console_context.py:1-314]()

### Context Switching

Users with organization memberships can switch their console context to view and manage organization-owned agents:

**Session keys:**
- `context_type`: `"personal"` or `"organization"`
- `context_id`: User ID or Organization UUID
- `context_name`: Display name for UI

**Agent filtering by context:**
- **Personal context**: `PersistentAgent.objects.filter(user=user, organization__isnull=True)`
- **Organization context**: `PersistentAgent.objects.filter(organization_id=org_id)`

**Creation permissions:**
- Personal agents: All authenticated users
- Organization agents: `OWNER` or `ADMIN` roles only

**Sources:** [console/context_helpers.py:50-120](), [console/templates/partials/_agent_contact_form.html:23-48](), [tests/unit/test_console_context.py:215-268]()

---

## AI Employee Templates

The platform provides a curated directory of pre-configured agent templates (AI Employees) that users can hire with one click. Templates define charter, schedule, tools, and communication preferences.

### Template Data Model

```mermaid
graph TB
    subgraph "Template System"
        Template[PersistentAgentTemplate]
        Template --> Fields["code: unique slug<br/>display_name: UI name<br/>charter: instructions<br/>base_schedule: cron<br/>schedule_jitter_minutes: randomization<br/>default_tools: JSON array<br/>recommended_contact_channel: enum<br/>event_triggers: JSON array<br/>is_active: visibility flag<br/>show_on_homepage: featured flag<br/>priority: sort order"]
    end
    
    subgraph "Template Application Flow"
        User[User clicks 'Hire']
        User --> StoreSession["session['agent_charter'] = template.charter<br/>session['ai_employee_template_code'] = code"]
        StoreSession --> ContactForm[Redirect to contact form]
        ContactForm --> Provision[PersistentAgentProvisioningService.provision]
        Provision --> LoadTemplate[AIEmployeeTemplateService.get_template_by_code]
        LoadTemplate --> ApplyDefaults["Set schedule with jitter<br/>Enable default_tools<br/>Set contact preferences"]
    end
    
    subgraph "Template Discovery"
        Directory[AI Employee Directory]
        Directory --> FilterCategory[Filter by category]
        Directory --> Search[Search name/tagline/description]
        Directory --> DisplayCards[Show templates grid]
        DisplayCards --> Detail[Detail page with full charter]
    end
```

**Sources:** [api/models.py:1650-1750](), [agents/services.py:119-265](), [pages/views.py:247-374]()

### AIEmployeeTemplateService

Key utility methods for working with templates:

| Method | Purpose |
|--------|---------|
| `get_active_templates()` | Returns queryset of visible templates |
| `get_template_by_code(code)` | Lookup by unique code slug |
| `compute_schedule_with_jitter(base, jitter_minutes)` | Apply random offset to cron schedule |
| `describe_schedule(cron)` | Human-readable cron description |
| `get_tool_display_map(tool_names)` | Lookup friendly names for tools |
| `describe_contact_channel(channel)` | Human-readable contact method |

**Sources:** [agents/services.py:119-265]()

### Schedule Jitter

Templates support schedule randomization to prevent thundering herd problems when many users hire the same template:

```python
# agents/services.py:149-180
def compute_schedule_with_jitter(base_schedule: str, jitter_minutes: int):
    # Parse "M H * * *" format
    minute_val = int(minute)
    hour_val = int(hour)
    total_minutes = hour_val * 60 + minute_val
    
    # Apply random offset
    offset = random.randint(-jitter_minutes, jitter_minutes)
    total_minutes = (total_minutes + offset) % (24 * 60)
    
    # Return adjusted schedule
    return f"{jittered_minute} {jittered_hour} {day} {month} {dow}"
```

**Example:** Template with `base_schedule="0 9 * * *"` and `schedule_jitter_minutes=30` creates agents that run between 8:30 AM and 9:30 AM.

**Sources:** [agents/services.py:149-180](), [tests/unit/test_ai_employee_directory.py:8-19]()

---

## Agent Creation UI Flow

The user-facing agent creation process spans three views: home charter submission, contact configuration, and provisioning confirmation.

### Creation Workflow

```mermaid
sequenceDiagram
    participant User
    participant HomePage as pages.views.HomePage
    participant SpawnView as pages.views.HomeAgentSpawnView
    participant ContactView as console.views.AgentContactView
    participant ProvService as PersistentAgentProvisioningService
    participant DB
    
    User->>HomePage: GET / or /l/{code}
    HomePage->>HomePage: Load template if ?g= param
    HomePage->>HomePage: Render charter form
    HomePage-->>User: Display form with prefilled charter
    
    User->>SpawnView: POST charter
    SpawnView->>SpawnView: Validate PersistentAgentCharterForm
    SpawnView->>SpawnView: session['agent_charter'] = charter
    
    alt Template selected
        SpawnView->>SpawnView: session['ai_employee_template_code'] = code
    end
    
    alt User authenticated
        SpawnView-->>User: Redirect to /agents/create/contact
    else User not authenticated
        SpawnView-->>User: Redirect to login, then /agents/create/contact
    end
    
    User->>ContactView: GET /agents/create/contact
    ContactView->>ContactView: Load session['agent_charter']
    ContactView->>ContactView: Load template if code in session
    ContactView-->>User: Display contact form with org selector
    
    User->>ContactView: POST contact preferences
    ContactView->>ContactView: Validate PersistentAgentContactForm
    ContactView->>ContactView: Check org permissions if org context
    
    alt Permission denied
        ContactView-->>User: Show permission warning
    else Allowed
        ContactView->>ProvService: provision(user, org, charter, contacts)
        ProvService->>DB: Create BrowserUseAgent + PersistentAgent
        ProvService->>ProvService: Apply template if present
        ProvService-->>ContactView: ProvisioningResult
        
        ContactView->>ContactView: Clear session charter/template
        ContactView->>DB: transaction.on_commit(trigger events task)
        ContactView-->>User: Redirect to agent detail page
    end
```

**Sources:** [pages/views.py:50-244](), [console/views.py:1490-1691](), [pages/templates/home.html:100-160](), [console/templates/partials/_agent_contact_form.html:1-400]()

### Session State Management

The creation flow stores intermediate state in the user session:

| Session Key | Type | Purpose |
|-------------|------|---------|
| `agent_charter` | str | User-entered or template charter |
| `agent_charter_source` | str | `"user"` or `"template"` |
| `ai_employee_template_code` | str | Template code for applying defaults |
| `context_type` | str | `"personal"` or `"organization"` |
| `context_id` | str | User ID or Organization UUID |

**Session cleanup:** All agent creation keys are cleared after successful provisioning to prevent accidental reuse.

**Sources:** [pages/views.py:209-212](), [console/views.py:1580-1591]()

---

## Agent Limit Enforcement

Agent limits are enforced at multiple checkpoints to prevent quota violations while maintaining a good user experience.

### Enforcement Points

```mermaid
graph TB
    subgraph "Pre-Creation Checks"
        UICheck1[Home page banner]
        UICheck1 --> ShowWarning{agents_available == 0?}
        ShowWarning -->|Yes| HideForm["Display 'No agents available' card"]
        ShowWarning -->|No| ShowForm["Display charter form"]
        
        UICheck2[Contact form submission]
        UICheck2 --> QuotaAPI[AgentService.get_agents_available]
        QuotaAPI --> HasSlots{Available > 0?}
        HasSlots -->|No| FormError["Add form.non_field_errors"]
        HasSlots -->|Yes| ProceedToModel
    end
    
    subgraph "Model-Level Validation"
        ProceedToModel[BrowserUseAgent.clean]
        ProceedToModel --> ReCheckQuota[AgentService.get_agents_available]
        ReCheckQuota --> ModelCheck{Available > 0?}
        ModelCheck -->|No| RaiseValidation["raise ValidationError('Agent limit reached')"]
        ModelCheck -->|Yes| AllowSave[Allow save]
    end
    
    subgraph "Race Condition Prevention"
        AllowSave --> TransactionIsolation["DB transaction with default isolation"]
        TransactionIsolation --> Note["Note: No explicit locking<br/>May allow brief over-quota<br/>if concurrent creates"]
    end
```

**Sources:** [agents/services.py:44-97](), [api/models.py:503-513](), [pages/templates/home.html:211-289]()

### Quota Calculation Logic

```python
# agents/services.py:44-97
@staticmethod
def get_agents_available(user) -> int:
    in_use = AgentService.get_agents_in_use(user)
    
    community_unlimited = is_community_unlimited_mode()
    plan_unlimited = has_unlimited_agents(user)
    
    if community_unlimited or plan_unlimited:
        user_limit = MAX_AGENT_LIMIT
    else:
        try:
            user_quota = UserQuota.objects.get(user_id=user.id)
            user_limit = min(user_quota.agent_limit, MAX_AGENT_LIMIT)
        except UserQuota.DoesNotExist:
            return 0  # No quota = no capacity
    
    remaining = max(user_limit - in_use, 0)
    return remaining
```

**Safety guarantees:**
1. Always returns non-negative integers
2. Caps unlimited users at `MAX_AGENT_LIMIT = 1000`
3. Returns 0 if `UserQuota` not found (fail-safe)
4. Uses `max()` to prevent negative results if over-quota

**Sources:** [agents/services.py:44-97](), [tests/unit/test_agent_limits.py:63-155]()

---

## Organization Agent Management

Organization-owned agents differ from personal agents in ownership, credit consumption, and access control. All active organization members can view org agents, but only `OWNER` and `ADMIN` roles can create or modify them.

### Organization Context Flow

```mermaid
graph TB
    subgraph "Context Selection"
        User[User with org membership]
        User --> Dropdown["Agent owner selector<br/>(contact form & console)"]
        Dropdown --> SelectPersonal["Personal - {username}"]
        Dropdown --> SelectOrg["Organization - {org.name}"]
        
        SelectPersonal --> PostSwitch1[POST /switch_context]
        SelectOrg --> PostSwitch2[POST /switch_context]
        
        PostSwitch1 --> SetSession1["session['context_type'] = 'personal'<br/>session['context_id'] = user.id"]
        PostSwitch2 --> SetSession2["session['context_type'] = 'organization'<br/>session['context_id'] = org.id"]
        
        SetSession1 --> Reload[Reload page]
        SetSession2 --> Reload
    end
    
    subgraph "Permission Enforcement"
        CreateAttempt[POST to create agent]
        CreateAttempt --> LoadContext[build_console_context]
        LoadContext --> CheckOrgCtx{context_type ==<br/>'organization'?}
        
        CheckOrgCtx -->|No| AllowPersonalCreate[Create as personal agent]
        CheckOrgCtx -->|Yes| CheckMembership{Active membership<br/>with OWNER/ADMIN?}
        
        CheckMembership -->|No| ShowWarning["show_org_permission_warning = True<br/>Disable submit button"]
        CheckMembership -->|Yes| AllowOrgCreate["Create with organization=org<br/>can_manage_org_agents = True"]
    end
    
    subgraph "Credit Resolution"
        EventProcess[process_agent_events_task]
        EventProcess --> LoadAgent[Load PersistentAgent]
        LoadAgent --> CheckOwner{organization_id<br/>not null?}
        
        CheckOwner -->|Yes| OrgCredits["TaskCreditService.get_org_credits(org)<br/>Consume from organization.task_credits"]
        CheckOwner -->|No| UserCredits["TaskCreditService.get_user_credits(user)<br/>Consume from user.task_credits"]
    end
```

**Sources:** [console/context_helpers.py:1-150](), [console/templates/partials/_agent_contact_form.html:23-48](), [tests/unit/test_console_context.py:215-268]()

### Agent Filtering by Context

Console views filter agents based on the active context to prevent leaking organization data:

```python
# Pseudo-code from console views
resolved = build_console_context(request)

if resolved.current_context.type == 'organization':
    # Verify membership is active
    if not resolved.current_membership:
        raise PermissionDenied()
    
    agents = PersistentAgent.objects.filter(
        organization_id=resolved.current_context.id
    )
else:
    # Personal context: exclude org-owned agents
    agents = PersistentAgent.objects.filter(
        user=request.user,
        organization__isnull=True
    )
```

**Sources:** [console/views.py:1245-1280](), [console/context_helpers.py:80-120]()

### Role-Based Access Control

| Action | MEMBER | ADMIN | OWNER | BILLING |
|--------|--------|-------|-------|---------|
| View org agents | ✓ | ✓ | ✓ | ✓ |
| Create org agents | ✗ | ✓ | ✓ | ✗ |
| Modify org agents | ✗ | ✓ | ✓ | ✗ |
| Delete org agents | ✗ | ✓ | ✓ | ✗ |
| View billing | ✗ | ✓ | ✓ | ✓ |

**Constants:**
- `MEMBER_MANAGE_ROLES = {OWNER, ADMIN}` - Can create/edit agents
- `BILLING_MANAGE_ROLES = {OWNER, ADMIN, BILLING}` - Can view/edit billing

**Sources:** [console/views.py:128-147](), [tests/unit/test_console_context.py:228-268]()

---

## Agent Lifecycle States

Agents transition between `ACTIVE` and `EXPIRED` lifecycle states. The `life_state` field tracks this independently from the `is_active` soft-deletion flag.

### State Definitions

```mermaid
stateDiagram-v2
    [*] --> ACTIVE: Agent created
    
    ACTIVE --> EXPIRED: User deactivates<br/>OR credit exhaustion<br/>OR manual expiration
    
    EXPIRED --> ACTIVE: User reactivates<br/>AND has credits
    
    ACTIVE --> SoftDeleted: User clicks Delete
    EXPIRED --> SoftDeleted: User clicks Delete
    
    SoftDeleted --> [*]: Permanent deletion<br/>(not implemented)
    
    note right of ACTIVE
        life_state = "active"
        is_active = True
        Processes events on schedule
        Responds to messages
    end note
    
    note right of EXPIRED
        life_state = "expired"
        is_active = True or False
        Skips scheduled execution
        May respond to messages if is_active=True
    end note
    
    note right of SoftDeleted
        is_active = False
        Hidden from UI listings
        Database record retained
    end note
```

**Sources:** [api/models.py:1060-1068](), [api/agent/core/event_processing.py:850-920]()

### State Transitions

| Trigger | From State | To State | Code Path |
|---------|-----------|----------|-----------|
| Agent creation | N/A | ACTIVE | `PersistentAgentProvisioningService.provision` |
| User deactivation | ACTIVE | EXPIRED | `AgentDetailView.post` (deactivate action) |
| User reactivation | EXPIRED | ACTIVE | `AgentDetailView.post` (reactivate action) |
| Credit exhaustion | ACTIVE | EXPIRED | `process_agent_events` auto-sleep logic |
| Soft deletion | Any | is_active=False | `AgentDetailView.post` (delete action) |

**Note on auto-sleep:** When an agent exhausts credits and has no pending work, `process_agent_events` may set `life_state=EXPIRED` to prevent further scheduled executions. This behavior is controlled by the `AUTO_SLEEP_FLAG` context variable.

**Sources:** [console/views.py:1745-1850](), [api/agent/core/event_processing.py:178-208]()

### Soft Deletion

Agents use `is_active=False` for soft deletion rather than hard deletes:

```python
# api/models.py:1185-1190
def soft_delete(self):
    self.is_active = False
    self.save(update_fields=['is_active'])
```

**Benefits:**
- Preserves audit trail of agent history
- Retains associated steps, messages, and tasks
- Allows potential future restoration
- Prevents foreign key constraint violations

**UI behavior:** Soft-deleted agents are excluded from console listings via `.filter(is_active=True)`.

**Sources:** [api/models.py:1185-1190](), [console/views.py:1245-1280]()

---

## Agent-to-Agent Communication

Agents can send direct messages to other agents via peer links. This enables multi-agent collaboration with quota enforcement and debouncing.

### Peer Link Architecture

```mermaid
graph TB
    subgraph "Peer Link Setup"
        AgentA[PersistentAgent A]
        AgentB[PersistentAgent B]
        
        AgentA --> Link[AgentPeerLink]
        AgentB --> Link
        
        Link --> State[AgentCommPeerState]
        State --> Fields["messages_per_window: quota<br/>window_hours: reset period<br/>credits_remaining: current quota<br/>window_start: quota window start<br/>last_reset: last quota reset<br/>last_message_at: debounce tracking"]
    end
    
    subgraph "Message Send Flow"
        SendAttempt[Agent calls send_agent_message tool]
        SendAttempt --> LoadLink[Load AgentPeerLink]
        LoadLink --> LinkEnabled{Link enabled?}
        
        LinkEnabled -->|No| Error1[Return error: No link]
        LinkEnabled -->|Yes| LoadState[Get/Create AgentCommPeerState]
        
        LoadState --> DebounceCheck{last_message_at<br/>< 5s ago?}
        DebounceCheck -->|Yes| Error2["Return error: Debounced<br/>Include retry_at timestamp"]
        
        DebounceCheck -->|No| QuotaCheck{credits_remaining<br/>> 0?}
        QuotaCheck -->|No| Error3["Return error: Throttled<br/>Schedule wake at window_reset"]
        
        QuotaCheck -->|Yes| DeductCredit["credits_remaining -= 1<br/>last_message_at = now"]
        DeductCredit --> CreateMsgs[Create 2 PersistentAgentMessage records]
        CreateMsgs --> UpdateReceiver["receiver.last_interaction_at = now"]
        UpdateReceiver --> TriggerEvent[process_agent_events_task.delay(receiver.id)]
    end
```

**Sources:** [api/models.py:1930-2050](), [api/agent/tools/peer_dm.py:1-150](), [api/agent/comms/peer_messaging.py:1-200]()

### Quota Enforcement

Peer messaging implements per-link quotas to prevent spam and runaway message loops:

| Field | Default | Purpose |
|-------|---------|---------|
| `messages_per_window` | 10 | Max messages sender can send per window |
| `window_hours` | 24 | Duration of quota window in hours |
| `credits_remaining` | 10 | Current available quota |
| `window_start` | Now | Start of current quota window |
| `debounce_seconds` | 5 | Minimum time between messages |

**Quota reset logic:**
```python
# api/agent/comms/peer_messaging.py
if now >= state.window_start + timedelta(hours=state.window_hours):
    state.credits_remaining = link.messages_per_window
    state.window_start = now
    state.last_reset = now
```

**Sources:** [api/models.py:1980-2010](), [api/agent/comms/peer_messaging.py:80-120]()

---

## Summary

The Agent Management system provides:

1. **Dual-model architecture**: `PersistentAgent` wraps `BrowserUseAgent` for separation of concerns
2. **Multi-level quotas**: Per-user limits, plan-based caps, and global safety ceiling at 1000 agents
3. **Ownership models**: Personal and organization agents with role-based access control
4. **Template system**: Pre-configured AI Employees with schedule jitter and default tool sets
5. **Lifecycle states**: ACTIVE/EXPIRED states with soft deletion support
6. **Peer communication**: Agent-to-agent messaging with quota enforcement and debouncing

Key code entry points:
- Agent creation: `PersistentAgentProvisioningService.provision` [api/services/persistent_agents.py:50-150]()
- Quota checking: `AgentService.get_agents_available` [agents/services.py:44-97]()
- Template application: `AIEmployeeTemplateService` [agents/services.py:119-265]()
- Ownership resolution: `build_console_context` [console/context_helpers.py:50-120]()

---

# Page: Creating Agents

# Creating Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agents/services.py](agents/services.py)
- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/models.py](api/models.py)
- [console/templates/partials/_agent_contact_form.html](console/templates/partials/_agent_contact_form.html)
- [console/views.py](console/views.py)
- [pages/templates/ai_directory/detail.html](pages/templates/ai_directory/detail.html)
- [pages/templates/ai_directory/index.html](pages/templates/ai_directory/index.html)
- [pages/templates/home.html](pages/templates/home.html)
- [pages/views.py](pages/views.py)
- [tests/unit/test_agent_limits.py](tests/unit/test_agent_limits.py)
- [tests/unit/test_ai_employee_directory.py](tests/unit/test_ai_employee_directory.py)
- [tests/unit/test_console_context.py](tests/unit/test_console_context.py)

</details>



## Purpose and Scope

This page documents the complete agent creation workflow, from initial user interaction through final provisioning and database persistence. It covers:

- Entry points for agent creation (homepage form and AI employee directory)
- The two-step creation flow (charter submission → contact configuration)
- Quota enforcement and agent limit validation
- Organization vs personal ownership mechanics
- The role of `PersistentAgentProvisioningService`

For information about agent lifecycle states and activation/deactivation, see [Agent Lifecycle](#4.4). For post-creation configuration (schedules, secrets, allowlists), see [Configuring Agents](#4.2). For the event processing loop that executes agent tasks, see [Agent Event Processing](#4.3).

---

## Agent Creation Flow Overview

Agent creation follows a two-step flow: charter definition followed by contact configuration. The system supports two entry points that converge on the same provisioning pipeline.

### High-Level Creation Sequence

```mermaid
sequenceDiagram
    participant User
    participant HomePage as "HomePage / AIEmployeeDirectoryView"
    participant Session
    participant ContactView as "AgentContactView"
    participant ProvService as "PersistentAgentProvisioningService"
    participant DB as "Database (PersistentAgent, BrowserUseAgent)"
    participant TaskQueue as "Celery (process_agent_events_task)"

    User->>HomePage: Submit charter form OR hire template
    HomePage->>Session: Store charter/template_code
    HomePage->>User: Redirect to agent_create_contact
    
    User->>ContactView: GET agent_create_contact
    ContactView->>Session: Retrieve charter/template_code
    ContactView->>User: Render contact configuration form
    
    User->>ContactView: POST contact preferences (email/SMS)
    ContactView->>ContactView: Validate quota (AgentService.get_agents_available)
    
    alt Quota exhausted
        ContactView->>User: Error - agent limit reached
    else Quota available
        ContactView->>ProvService: provision(user, org, charter, template_code, contacts)
        ProvService->>DB: Create BrowserUseAgent
        ProvService->>DB: Create PersistentAgent
        ProvService->>DB: Create PersistentAgentCommsEndpoint(s)
        ProvService->>DB: Apply template defaults (schedule, tools)
        ProvService->>TaskQueue: process_agent_events_task.delay(agent_id)
        ProvService-->>ContactView: ProvisioningResult
        ContactView->>User: Redirect to agent detail page
    end
```

**Sources:** [pages/views.py:198-244](), [console/templates/partials/_agent_contact_form.html:6-234](), [agents/services.py:44-97]()

---

## Entry Points

### Homepage Charter Form

The primary entry point is the homepage charter form where users define an agent's purpose in natural language.

**Form Location:** [pages/templates/home.html:107-160]()

**Handler:** `HomeAgentSpawnView.post()` at [pages/views.py:202-238]()

**Flow:**
1. User submits `charter` field via POST to `/spawn/`
2. `PersistentAgentCharterForm` validates charter (non-empty, max length)
3. Charter stored in session: `request.session['agent_charter']`, `request.session['agent_charter_source'] = 'user'`
4. Analytics event tracked: `PERSISTENT_AGENT_CHARTER_SUBMIT` (if authenticated)
5. Redirect to `agent_create_contact` (via login flow if unauthenticated)

**Session Keys:**
- `agent_charter`: The charter text
- `agent_charter_source`: Either `'user'` (custom) or `'template'` (from directory)

**Sources:** [pages/views.py:198-244](), [pages/templates/home.html:107-160]()

---

### AI Employee Directory (Template-Based Creation)

The AI employee directory provides pre-configured agent templates with curated charters, schedules, and tool configurations.

**Directory View:** `AIEmployeeDirectoryView` at [pages/views.py:247-299]()

**Template Detail View:** `AIEmployeeDetailView` at [pages/views.py:302-326]()

**Hire Handler:** `AIEmployeeHireView.post()` at [pages/views.py:329-373]()

**Flow:**
1. User clicks "Hire" button on template card (POST to `/ai-employees/{slug}/hire/`)
2. Template retrieved via `AIEmployeeTemplateService.get_template_by_code(code)` at [agents/services.py:139-146]()
3. Template charter and code stored in session:
   - `request.session['agent_charter'] = template.charter`
   - `request.session[AIEmployeeTemplateService.TEMPLATE_SESSION_KEY] = template.code` (key is `"ai_employee_template_code"`)
   - `request.session['agent_charter_source'] = 'template'`
4. Analytics event tracked: `PERSISTENT_AGENT_CHARTER_SUBMIT` with `template_code` property
5. Redirect to `agent_create_contact` (via login flow if unauthenticated)

**Template Data Model:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | CharField | Unique identifier for template |
| `charter` | TextField | Pre-written agent instructions |
| `base_schedule` | CharField | Cron expression for execution cadence |
| `schedule_jitter_minutes` | IntegerField | Random offset applied to schedule |
| `default_tools` | JSONField | List of tool names to enable |
| `event_triggers` | JSONField | Event-based trigger configurations |
| `recommended_contact_channel` | CharField | Suggested communication method |

**Sources:** [pages/views.py:329-373](), [agents/services.py:119-264](), [pages/templates/ai_directory/index.html:97-103]()

---

## Contact Configuration Step

After charter submission, users configure how the agent will communicate with them. This is the second and final step before provisioning.

**View Handler:** `AgentContactView` (not fully shown in provided files, but referenced in templates and tests)

**Template:** [console/templates/partials/_agent_contact_form.html:1-235]()

### Contact Configuration Form Fields

```mermaid
flowchart TD
    Form["AgentContactView Form"]
    
    EmailToggle["email_enabled (checkbox)"]
    EmailInput["contact_endpoint_email (EmailField)"]
    
    SmsToggle["sms_enabled (checkbox)"]
    SmsInput["Phone number input (UserPhoneNumberForm)"]
    SmsVerify["Verification code"]
    
    Preferred["preferred_contact_method (RadioSelect)"]
    
    OrgSelector["agent-owner-selector (if orgs enabled)"]
    
    Form --> EmailToggle
    Form --> EmailInput
    Form --> SmsToggle
    Form --> SmsInput
    Form --> SmsVerify
    Form --> Preferred
    Form --> OrgSelector
    
    EmailToggle -->|checked| EmailInput
    SmsToggle -->|checked| SmsInput
    SmsInput --> SmsVerify
```

**Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email_enabled` | BooleanField | No | Toggle email communication |
| `contact_endpoint_email` | EmailField | If email enabled | Email address for agent contact |
| `sms_enabled` | BooleanField | No | Toggle SMS communication |
| `phone_number` | CharField | If SMS enabled | Phone number (E.164 format) |
| `verification_code` | CharField | If SMS new | OTP for phone verification |
| `preferred_contact_method` | ChoiceField | Yes | Primary communication channel (email/sms/web) |

**Validation Logic:**
- At least one contact method must be enabled
- If `preferred_contact_method` is `'email'`, email must be enabled
- If `preferred_contact_method` is `'sms'`, SMS must be enabled and phone verified
- Phone numbers must be verified before agent creation (OTP flow)

**Sources:** [console/templates/partials/_agent_contact_form.html:89-210]()

---

### Organization Context and Ownership

Agents can be owned by either a **User** OR an **Organization** (mutually exclusive). The ownership is determined by the console context at creation time.

**Context Selection:** [console/templates/partials/_agent_contact_form.html:23-48]()

**Context Storage:**

Session keys set by `build_console_context()` and context switch endpoint:
- `context_type`: `"personal"` or `"organization"`
- `context_id`: User ID (string) or Organization ID (UUID string)
- `context_name`: User display name or organization name

**Organization Agent Creation Requirements:**

| Role | Can Create Org Agents | Notes |
|------|----------------------|-------|
| OWNER | ✓ | Full permissions |
| ADMIN | ✓ | Full permissions |
| MEMBER | ✗ | Blocked by permission check |
| BILLING | ✗ | Blocked by permission check |

**Permission Enforcement:**

```mermaid
flowchart TD
    SubmitForm["POST to agent_create_contact"]
    CheckContext{"context_type == 'organization'?"}
    CheckMembership["Retrieve OrganizationMembership"]
    CheckRole{"role in (OWNER, ADMIN)?"}
    AllowCreate["Provision org-owned agent"]
    DenyCreate["Render form with error: 'You need to be an organization owner or admin'"]
    PersonalCreate["Provision user-owned agent"]
    
    SubmitForm --> CheckContext
    CheckContext -->|Yes| CheckMembership
    CheckContext -->|No| PersonalCreate
    CheckMembership --> CheckRole
    CheckRole -->|Yes| AllowCreate
    CheckRole -->|No| DenyCreate
```

**Data Model Constraints:**

From [api/models.py:168-175]():
```python
models.CheckConstraint(
    check=(
        (models.Q(user__isnull=False, organization__isnull=True))
        | (models.Q(user__isnull=True, organization__isnull=False))
    ),
    name="api_key_exactly_one_owner",
)
```

This pattern applies to `PersistentAgent`, `BrowserUseAgent`, and `BrowserUseAgentTask` models.

**Sources:** [console/templates/partials/_agent_contact_form.html:23-48](), [tests/unit/test_console_context.py:228-267]()

---

## Quota Enforcement

Agent creation is gated by quota limits to prevent runaway usage. Quotas are enforced at multiple layers.

### Quota Calculation Flow

```mermaid
flowchart TD
    CreateRequest["Agent creation request"]
    
    GetInUse["AgentService.get_agents_in_use(user)"]
    CountAgents["Count BrowserUseAgent records"]
    
    CheckUnlimited{"is_community_unlimited_mode() OR has_unlimited_agents(user)?"}
    
    SetUnlimited["user_limit = MAX_AGENT_LIMIT (1000)"]
    
    GetQuota["UserQuota.objects.get(user=user)"]
    QuotaExists{"Quota exists?"}
    
    SetQuotaLimit["user_limit = min(quota.agent_limit, MAX_AGENT_LIMIT)"]
    SetZero["user_limit = 0 (quota required)"]
    
    CalcRemaining["remaining = max(user_limit - in_use, 0)"]
    
    ReturnAvailable["Return remaining count"]
    
    CreateRequest --> GetInUse
    GetInUse --> CountAgents
    CountAgents --> CheckUnlimited
    
    CheckUnlimited -->|Yes| SetUnlimited
    CheckUnlimited -->|No| GetQuota
    
    GetQuota --> QuotaExists
    QuotaExists -->|Yes| SetQuotaLimit
    QuotaExists -->|No| SetZero
    
    SetUnlimited --> CalcRemaining
    SetQuotaLimit --> CalcRemaining
    SetZero --> CalcRemaining
    
    CalcRemaining --> ReturnAvailable
```

**Key Functions:**

**`AgentService.get_agents_in_use(user)`** at [agents/services.py:26-42]()
- Returns count of `BrowserUseAgent` records for user
- Simple: `BrowserUseAgent.objects.filter(user_id=user.id).count()`

**`AgentService.get_agents_available(user)`** at [agents/services.py:44-97]()
- Calculates remaining agent slots
- Enforces `MAX_AGENT_LIMIT` constant (1000) as absolute ceiling
- Checks `UserQuota.agent_limit` for per-user limits
- Returns 0 if no `UserQuota` record exists
- Never returns negative values

**Constants:**

| Constant | Value | Location | Description |
|----------|-------|----------|-------------|
| `MAX_AGENT_LIMIT` | 1000 | `config/plans.py` | Absolute safety ceiling |
| `AGENTS_UNLIMITED` | -1 | `config/plans.py` | Sentinel for unlimited plans |

**Sources:** [agents/services.py:19-117](), [tests/unit/test_agent_limits.py:1-284]()

---

### Validation in BrowserUseAgent.clean()

Pre-save validation occurs in `BrowserUseAgent.clean()` method at [api/models.py:503-513]():

```python
def clean(self):
    super().clean()
    if self._state.adding and getattr(self, 'user_id', None):
        agents_available = AgentService.get_agents_available(self.user)
        
        if agents_available <= 0:
            raise ValidationError(
                "Agent limit reached for this user."
            )
```

**Validation Flow:**
1. Only validates on creation (`self._state.adding`)
2. Calls `AgentService.get_agents_available()`
3. Raises `ValidationError` if `agents_available <= 0`
4. Validation called automatically by `BrowserUseAgent.save()`

**Sources:** [api/models.py:503-513](), [tests/unit/test_agent_limits.py:169-193]()

---

## Agent Provisioning Service

The `PersistentAgentProvisioningService` is the authoritative component for agent creation. While the full implementation isn't in the provided files, we can infer its interface and responsibilities.

### Provisioning Service Interface

**Import:** [console/views.py:97-100]()
```python
from api.services.persistent_agents import (
    PersistentAgentProvisioningError,
    PersistentAgentProvisioningService,
)
```

**Expected Method Signature:**
```python
def provision(
    user: User,
    organization: Optional[Organization],
    charter: str,
    template_code: Optional[str] = None,
    contacts: Dict[str, Any] = None,
    **kwargs
) -> ProvisioningResult
```

### Provisioning Steps (Inferred)

```mermaid
flowchart TD
    Provision["PersistentAgentProvisioningService.provision()"]
    
    ValidateQuota["Validate AgentService.get_agents_available() > 0"]
    QuotaFail["Raise PersistentAgentProvisioningError"]
    
    CreateBrowser["Create BrowserUseAgent (user=user, name=...)"]
    SelectProxy["BrowserUseAgent.select_random_proxy()"]
    
    CreatePersistent["Create PersistentAgent (user/org, charter, browser_use_agent)"]
    
    LoadTemplate{"template_code provided?"}
    ApplyTemplate["Load PersistentAgentTemplate by code"]
    ApplySchedule["Set agent.schedule = template.base_schedule + jitter"]
    ApplyTools["Enable default_tools via MCPToolManager"]
    
    CreateEndpoints["Create PersistentAgentCommsEndpoint records"]
    CreateEmailEndpoint["For email: PersistentAgentEmailEndpoint"]
    CreateSmsEndpoint["For SMS: PersistentAgentSmsEndpoint"]
    
    QueueEvent["process_agent_events_task.delay(agent_id)"]
    
    Return["Return ProvisioningResult (agent, browser_agent)"]
    
    Provision --> ValidateQuota
    ValidateQuota -->|Available| CreateBrowser
    ValidateQuota -->|Exhausted| QuotaFail
    
    CreateBrowser --> SelectProxy
    SelectProxy --> CreatePersistent
    
    CreatePersistent --> LoadTemplate
    LoadTemplate -->|Yes| ApplyTemplate
    LoadTemplate -->|No| CreateEndpoints
    
    ApplyTemplate --> ApplySchedule
    ApplySchedule --> ApplyTools
    ApplyTools --> CreateEndpoints
    
    CreateEndpoints --> CreateEmailEndpoint
    CreateEndpoints --> CreateSmsEndpoint
    
    CreateEmailEndpoint --> QueueEvent
    CreateSmsEndpoint --> QueueEvent
    
    QueueEvent --> Return
```

### Data Models Created

**BrowserUseAgent** (primary agent record):
- `id`: UUID primary key
- `user`: ForeignKey to User
- `name`: Agent name (defaults to charter prefix or template name)
- `preferred_proxy`: ForeignKey to ProxyServer (auto-assigned via `select_random_proxy()`)

**PersistentAgent** (always-on agent wrapper):
- `id`: UUID primary key
- `user`: ForeignKey to User (nullable)
- `organization`: ForeignKey to Organization (nullable, XOR with user)
- `charter`: TextField (agent instructions)
- `browser_use_agent`: OneToOneField to BrowserUseAgent
- `schedule`: CharField (cron expression, nullable)
- `life_state`: CharField (defaults to ACTIVE)
- `is_active`: BooleanField (defaults to True)

**PersistentAgentCommsEndpoint** (abstract base):
- `agent`: ForeignKey to PersistentAgent
- `channel`: CharField (email/sms/web)
- `is_primary`: BooleanField

**PersistentAgentEmailEndpoint** (concrete):
- Inherits from PersistentAgentCommsEndpoint
- `email_address`: EmailField
- `allow_inbound`: BooleanField
- `allow_outbound`: BooleanField

**PersistentAgentSmsEndpoint** (concrete):
- Inherits from PersistentAgentCommsEndpoint
- `phone_number`: ForeignKey to UserPhoneNumber
- `allow_inbound`: BooleanField
- `allow_outbound`: BooleanField

**Sources:** [console/views.py:97-100](), [api/models.py:472-611]() (BrowserUseAgent), [tests/unit/test_console_context.py:58-74]()

---

## Template Application

When `template_code` is provided (from AI employee directory), the provisioning service applies template defaults.

### Template Default Application

**Schedule with Jitter:**

`AIEmployeeTemplateService.compute_schedule_with_jitter()` at [agents/services.py:149-180]()

```python
jitter = max(int(jitter_minutes or 0), 0)
if jitter == 0:
    return base_schedule

# Parse cron expression: "minute hour day month weekday"
parts = base_schedule.split()
minute_val = int(parts[0])
hour_val = int(parts[1])

total_minutes = hour_val * 60 + minute_val
offset = random.randint(-jitter, jitter)
total_minutes = (total_minutes + offset) % (24 * 60)

jittered_hour, jittered_minute = divmod(total_minutes, 60)
return f"{jittered_minute} {jittered_hour} {day_of_month} {month} {day_of_week}"
```

**Example:**
- Template: `base_schedule = "0 9 * * *"` (9:00 AM daily), `schedule_jitter_minutes = 30`
- Applied: `"17 8 * * *"` (8:17 AM, offset by -43 minutes)

**Tool Enablement:**

Templates specify `default_tools` as a list of tool names. These are enabled via `enable_mcp_tool()` (referenced at [console/views.py:95]()).

**Event Triggers:**

Templates can specify `event_triggers` (JSONField) to configure automatic agent wakeup on specific events (e.g., incoming emails, specific times).

**Sources:** [agents/services.py:149-180](), [pages/views.py:329-373](), [pages/templates/ai_directory/detail.html:42-47]()

---

## Post-Creation Event Queue

Immediately after provisioning, the agent is queued for initial event processing.

**Task Dispatch:**

```python
from api.agent.tasks import process_agent_events_task

transaction.on_commit(lambda: process_agent_events_task.delay(agent.id))
```

**Task Entry Point:** [api/agent/core/event_processing.py:716-862]()

This initial task execution:
1. Establishes budget cycle via `AgentBudgetManager`
2. Acquires Redis distributed lock (`Redlock`)
3. Runs initial agent loop with empty conversation history
4. Processes any initial messages or triggers
5. Sets `last_interaction_at` timestamp

**Sources:** [api/agent/core/event_processing.py:716-862](), [console/views.py:96]()

---

## Summary: Key Code Entities

| Entity | Type | Location | Role |
|--------|------|----------|------|
| `HomeAgentSpawnView` | View | [pages/views.py:198-244]() | Handles charter form submission |
| `AIEmployeeHireView` | View | [pages/views.py:329-373]() | Handles template hire |
| `AgentContactView` | View | (Referenced in templates/tests) | Handles contact configuration |
| `PersistentAgentProvisioningService` | Service | [console/views.py:97-100]() | Orchestrates agent creation |
| `AgentService` | Service | [agents/services.py:19-117]() | Quota calculations and validation |
| `AIEmployeeTemplateService` | Service | [agents/services.py:119-264]() | Template management and application |
| `BrowserUseAgent` | Model | [api/models.py:472-611]() | Core agent record |
| `PersistentAgent` | Model | [api/models.py]() | Always-on agent wrapper |
| `UserQuota` | Model | [api/models.py:278-288]() | Per-user agent limits |
| `process_agent_events_task` | Celery Task | [api/agent/core/event_processing.py:716-862]() | Initial agent execution |
| `build_console_context()` | Helper | (Referenced in views) | Determines user/org ownership context |

**Sources:** All files referenced in this document.

---

# Page: Configuring Agents

# Configuring Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py](api/migrations/0155_persistentagent_daily_credit_limit_and_more.py)
- [console/templates/console/agent_detail.html](console/templates/console/agent_detail.html)
- [console/templates/partials/_agent_list.html](console/templates/partials/_agent_list.html)
- [tests/unit/test_agent_event_processing_credits.py](tests/unit/test_agent_event_processing_credits.py)
- [tests/unit/test_console.py](tests/unit/test_console.py)

</details>



## Purpose and Scope

This page documents the configuration options available for `PersistentAgent` instances after creation. It covers all user-facing settings that control agent behavior, resource limits, communication channels, and inter-agent connections. 

For information about the agent creation process, see [Creating Agents](#4.1). For details about how agents process events and execute tasks, see [Agent Event Processing](#4.3). For agent lifecycle states and activation/deactivation, see [Agent Lifecycle](#4.4).

---

## Configuration Interface Overview

Agent configuration is accessed via the agent detail page at `/console/agent/<id>/`, rendered by the `agent_detail` view. The interface is organized into several configuration sections, each controlling different aspects of agent behavior.

```mermaid
graph TB
    User["User Access"] --> DetailView["agent_detail view<br/>console/views.py"]
    DetailView --> Template["agent_detail.html"]
    
    Template --> BasicConfig["Basic Configuration"]
    Template --> CreditConfig["Credit & Resource Limits"]
    Template --> CommConfig["Communication Settings"]
    Template --> PeerConfig["Peer Links"]
    Template --> DangerZone["Ownership & Deletion"]
    
    BasicConfig --> Name["name: str"]
    BasicConfig --> Charter["charter: text"]
    BasicConfig --> Status["is_active: bool"]
    BasicConfig --> Ownership["organization: FK"]
    
    CreditConfig --> DailyLimit["daily_credit_limit: int"]
    
    CommConfig --> EmailAccount["AgentEmailAccount"]
    CommConfig --> SmsNumber["SmsNumber"]
    CommConfig --> Allowlist["CommsAllowlistEntry"]
    
    PeerConfig --> PeerLinks["AgentPeerLink"]
    
    DangerZone --> Transfer["AgentTransferInvite"]
    DangerZone --> Delete["Soft Delete"]
    
    style BasicConfig fill:#f9f9f9
    style CreditConfig fill:#f9f9f9
    style CommConfig fill:#f9f9f9
    style PeerConfig fill:#f9f9f9
```

**Sources:**
- [console/templates/console/agent_detail.html:1-640]()
- [console/views.py]() (agent_detail view)

---

## Basic Settings

### Agent Name

The `name` field provides a human-readable identifier for the agent. Names must be unique within their ownership scope (per-user for personal agents, per-organization for org-owned agents).

**Validation:**
- Maximum length: 255 characters
- Must be unique within the agent's ownership context
- Updated via POST to `agent_detail` view

```mermaid
graph LR
    Form["Form Input<br/>name field"] --> Validation["Uniqueness Check<br/>Per Owner"]
    Validation -->|Valid| Save["PersistentAgent.save()"]
    Validation -->|Duplicate| Error["ValidationError"]
    
    Save --> Display["Update UI<br/>agent.name"]
```

**Sources:**
- [console/templates/console/agent_detail.html:46-66]()

### Charter (Assignment)

The `charter` field is a text description of the agent's purpose and responsibilities. This field is incorporated into the agent's system prompt during event processing and guides LLM reasoning.

**Key Characteristics:**
- Free-form text field (TextField in Django)
- Directly injected into prompt via `Promptree` template system
- Can be modified at any time without affecting running tasks
- Appears in agent listing views as truncated description

```mermaid
graph TB
    UserInput["Charter Text<br/>textarea"] --> DB["PersistentAgent.charter"]
    DB --> PromptBuilder["Promptree Template<br/>_run_agent_loop"]
    PromptBuilder --> SystemPrompt["LLM System Prompt"]
    
    DB --> ListingView["Agent List View<br/>listing_description"]
```

**Sources:**
- [console/templates/console/agent_detail.html:256-276]()
- [api/agent/core/event_processing.py]() (_run_agent_loop function)

### Active Status

The `is_active` boolean controls whether the agent can process events. Deactivated agents skip all event processing but retain their configuration.

**Toggle Behavior:**
- UI: Toggle switch in status section
- Database: `PersistentAgent.is_active` boolean field
- Effect: Inactive agents bypass event processing in celery tasks

```mermaid
stateDiagram-v2
    [*] --> Inactive: is_active=False
    Inactive --> Active: Toggle ON + Save
    Active --> Inactive: Toggle OFF + Save
    
    Active --> EventProcessing: process_agent_events_task
    Inactive --> SkipProcessing: Task exits early
```

**Sources:**
- [console/templates/console/agent_detail.html:161-199]()
- [api/models.py]() (PersistentAgent.is_active field)

---

## Credit & Resource Limits

### Daily Credit Limit

The `daily_credit_limit` field (added in migration 0155) caps the number of task credits an agent may consume within a 24-hour window. This is an agent-level quota that operates independently of user/organization credit pools.

**Field Specifications:**
- Type: `PositiveIntegerField` (nullable)
- `NULL` value means unlimited
- Defaults to 10 for Free tier agents (set via migration)
- Pro/Enterprise agents default to `NULL` (unlimited)

```mermaid
graph TB
    DailyLimit["daily_credit_limit<br/>PersistentAgent field"] --> CheckLoop["_get_agent_daily_credit_state()"]
    
    CheckLoop --> Query["SUM credits_cost<br/>WHERE created_at >= start_of_day"]
    Query --> State["Daily Credit State Dict"]
    
    State --> Fields["- date<br/>- limit<br/>- used<br/>- remaining<br/>- next_reset"]
    
    State --> PreGate["Pre-processing Gate<br/>_process_agent_events_locked"]
    State --> MidLoopGate["Mid-loop Gate<br/>_ensure_credit_for_tool"]
    
    PreGate -->|remaining = 0| ExitEarly["Create SystemStep<br/>daily_credit_limit_exhausted"]
    MidLoopGate -->|remaining < tool_cost| SkipTool["Create SystemStep<br/>daily_credit_limit_mid_loop"]
```

**Daily Credit State Calculation:**

The system computes daily credit state by:
1. Determining the start of the current day in the agent owner's timezone
2. Summing `credits_cost` from all `PersistentAgentStep` records created today
3. Comparing usage against `daily_credit_limit` (or treating as unlimited if NULL)
4. Calculating the next reset time (start of next day)

**Gating Behavior:**

Daily limits are enforced at two checkpoints:
- **Pre-processing gate**: Before `_run_agent_loop` executes, prevents entire event processing cycle
- **Mid-loop gate**: Before each tool execution in `_ensure_credit_for_tool`, skips individual tools

**Sources:**
- [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py:1-51]()
- [api/agent/core/event_processing.py]() (_get_agent_daily_credit_state function)
- [tests/unit/test_agent_event_processing_credits.py:148-182]() (test_process_agent_events_respects_daily_limit)
- [console/templates/console/agent_detail.html:201-253]()

### Daily Credit UI Components

The agent detail page displays daily credit status with visual indicators:

| Component | Display Condition | Purpose |
|-----------|------------------|---------|
| Usage Progress Bar | `daily_credit_limit` is not NULL | Visual representation of credit consumption |
| Low Credit Warning | `daily_credit_remaining < 1.0` | Alert banner at top of form |
| Remaining Credits | Always (when limit set) | Precise decimal count of credits left |
| Next Reset Time | Always (when limit set) | Timestamp for quota refresh |

**Warning Threshold:**

The UI sets `daily_credit_low = True` when:
- Daily limit is configured (not NULL)
- Remaining credits < 1.0

This triggers amber alert boxes in both the detail view and agent list view.

**Sources:**
- [console/templates/console/agent_detail.html:219-242]()
- [console/templates/partials/_agent_list.html:104-108]()
- [tests/unit/test_console.py:236-291]() (test_agent_detail_updates_daily_credit_limit)

---

## Ownership & Context

### User vs Organization Ownership

Agents can be owned by individual users or by organizations. Ownership determines:
- Credit pool (user credits vs org credits)
- Quota enforcement (user limits vs seat-based limits)
- Access control (who can configure/delete the agent)

```mermaid
graph TB
    Agent["PersistentAgent"] --> OwnerCheck{organization<br/>field}
    
    OwnerCheck -->|NULL| UserOwned["User-Owned Agent"]
    OwnerCheck -->|FK set| OrgOwned["Org-Owned Agent"]
    
    UserOwned --> UserCredits["TaskCredit<br/>WHERE user=agent.user"]
    UserOwned --> UserBilling["UserBilling.subscription"]
    
    OrgOwned --> OrgCredits["TaskCredit<br/>WHERE organization=agent.organization"]
    OrgOwned --> OrgBilling["OrganizationBilling<br/>purchased_seats"]
    
    UserOwned --> UserQuota["max_agents<br/>from PlanSpec"]
    OrgOwned --> SeatQuota["1 agent per seat"]
```

**Organization Assignment:**

When the `organizations` waffle flag is active, the detail page allows reassigning agents between personal and organizational ownership. This requires:
- User must have OWNER or ADMIN role in target organization
- Agent name must be unique within target organization
- Organization must have available seats (for org-assignment)

**Reassignment Flow:**

1. User selects target organization from dropdown
2. Client-side JS POSTs to ownership reassignment endpoint
3. Backend validates role and seat availability
4. Updates `PersistentAgent.organization` and `PersistentAgent.user`
5. Reloads page to reflect new context

**Sources:**
- [console/templates/console/agent_detail.html:68-104]()
- [api/models.py]() (PersistentAgent.organization field)

---

## Communication Settings

### Email Configuration

Each agent can have a dedicated email account for sending and receiving messages. The primary email account is linked via the `AgentEmailAccount` model.

**Email Account Properties:**
- `address`: The email address (e.g., `agent-abc123@agents.gobii.ai`)
- `imap_enabled`: Whether to poll for incoming messages
- `smtp_enabled`: Whether agent can send outbound email
- IMAP/SMTP credentials stored in `email_credentials` JSON field

**Management Flow:**

The detail page links to a separate email settings interface:
```
[Manage Email] button → /console/agent/<id>/email-settings/
```

This dedicated view handles:
- IMAP/SMTP connection testing
- Credential updates
- Inbox polling configuration
- Send/receive toggles

**Sources:**
- [console/templates/console/agent_detail.html:106-142]()
- [api/models.py]() (AgentEmailAccount model)

### SMS Configuration

SMS capabilities are provisioned via `SmsNumber` records. Unlike email (which is created by default), SMS must be explicitly enabled.

**Enablement Process:**
1. User clicks "Enable SMS" link on detail page
2. System provisions a Twilio number
3. Creates `SmsNumber` record with webhook configuration
4. Associates number with agent via `agent` FK

**SMS Number Characteristics:**
- `address`: E.164 formatted phone number
- `is_primary`: Boolean flag (one primary per agent)
- `twilio_sid`: Twilio phone number identifier
- Incoming messages trigger webhook → creates `PersistentAgentMessage` → queues event processing

**Sources:**
- [console/templates/console/agent_detail.html:123-128]()
- [console/templates/console/agent_detail.html:144-158]()
- [api/models.py]() (SmsNumber model)

### Communication Allowlist

The allowlist controls which external contacts can communicate with the agent. As of the current implementation, all agents use **manual allowlist policy** exclusively.

**Allowlist Entry Structure:**

Each `CommsAllowlistEntry` record specifies:
- `channel`: Email or SMS
- `address`: Contact identifier (email or phone)
- `allow_inbound`: Can this contact message the agent?
- `allow_outbound`: Can the agent message this contact?

**Directional Permissions:**

The system supports asymmetric communication:
- Agent can notify user, but user cannot command agent: `allow_inbound=False, allow_outbound=True`
- User can command agent, but agent cannot initiate: `allow_inbound=True, allow_outbound=False`
- Bidirectional: Both flags set to `True`

```mermaid
graph TB
    InboundMsg["Inbound Message<br/>Email/SMS/Chat"] --> AllowlistCheck{"CommsAllowlistEntry<br/>WHERE address=sender"}
    
    AllowlistCheck -->|Not Found| DefaultCheck{"Default Allowlist<br/>Policy"}
    AllowlistCheck -->|Found| InboundFlag{"allow_inbound?"}
    
    DefaultCheck -->|Owner/Org Member| Allow["Create Message<br/>Trigger Agent"]
    DefaultCheck -->|External| Reject["Ignore Message"]
    
    InboundFlag -->|True| Allow
    InboundFlag -->|False| Reject
    
    OutboundMsg["Agent Wants to Send"] --> OutboundCheck{"CommsAllowlistEntry<br/>WHERE address=recipient"}
    OutboundCheck -->|Not Found| DefaultCheck
    OutboundCheck -->|Found| OutboundFlag{"allow_outbound?"}
    
    OutboundFlag -->|True| Send["Send Message"]
    OutboundFlag -->|False| SkipSend["Skip Send"]
```

**Management Interface:**

The detail page includes inline allowlist management (when `show_allowlist` context variable is True):
- Add entry form with channel selection
- Inbound/outbound checkbox toggles
- List of current entries with remove buttons
- Contact count display: `N / MAX contacts`

**Quota Enforcement:**

The system enforces `max_contacts_per_agent` from the account's plan specification. The UI displays this limit and prevents adding entries beyond the quota.

**Sources:**
- [console/templates/console/agent_detail.html:278-384]()
- [api/models.py]() (CommsAllowlistEntry model)
- [api/services/comms_service.py]() (allowlist validation logic)

---

## Secrets Management

Agents can store encrypted secrets (API keys, passwords, etc.) via the `AgentSecret` model. The detail page provides a link to a dedicated secrets management interface.

**Navigation:**
```
[Manage Secrets] button → /console/agent/<id>/secrets/
```

**Secret Storage:**
- Key-value pairs stored per-agent
- Values encrypted at rest
- Available to agent during tool execution via `get_agent_secrets()` helper
- Used for MCP server authentication, third-party API access, etc.

**Sources:**
- [console/templates/console/agent_detail.html:416-422]()
- [api/models.py]() (AgentSecret model)

---

## Peer Links (Agent-to-Agent Communication)

Peer links enable direct messaging between agents owned by the same user. Each link is represented by an `AgentPeerLink` record with quota and debounce controls.

### Link Configuration

| Field | Type | Purpose |
|-------|------|---------|
| `from_agent` | FK | Initiating agent |
| `to_agent` | FK | Receiving agent |
| `messages_per_window` | Int | Quota (e.g., 10 messages) |
| `window_hours` | Int | Time window for quota (e.g., 24 hours) |
| `is_enabled` | Bool | Active/inactive toggle |
| `feature_flag` | Str | Optional flag name for conditional enablement |

### Quota Enforcement

The system tracks quota usage via `AgentCommPeerState` records:
- `credits_remaining`: Messages left in current window
- `window_reset_at`: Timestamp when quota refreshes
- `last_message_at`: Last message sent (for debouncing)

**Debouncing:**
The system enforces a 5-second cooldown between consecutive messages to prevent runaway message loops.

```mermaid
sequenceDiagram
    participant A1 as Agent 1
    participant PMS as PeerMessagingService
    participant State as AgentCommPeerState
    participant A2 as Agent 2
    
    A1->>PMS: send_peer_message(to=A2)
    PMS->>State: Check last_message_at
    
    alt < 5 seconds since last message
        State-->>PMS: Debounced error
        PMS-->>A1: Error: retry_at timestamp
    else >= 5 seconds
        State->>State: Check credits_remaining
        alt credits_remaining = 0
            State-->>PMS: Throttled error
            PMS-->>A1: Error: Schedule wake at window_reset_at
        else credits > 0
            State->>State: credits_remaining -= 1
            State->>State: Update last_message_at
            PMS->>A2: Create inbound PersistentAgentMessage
            PMS->>A2: Trigger process_agent_events_task
            PMS-->>A1: Success
        end
    end
```

### UI Management

The detail page displays all peer links with inline editing:
- Table view showing linked agents, quotas, and remaining credits
- Per-link forms to update `messages_per_window`, `window_hours`, `feature_flag`, and `is_enabled`
- Remove link button (soft delete via `AgentPeerLink.delete()`)

**Sources:**
- [console/templates/console/agent_detail.html:487-597]()
- [api/models.py]() (AgentPeerLink, AgentCommPeerState models)
- [api/services/peer_messaging_service.py]() (quota enforcement logic)

---

## Ownership Transfer

Agents can be transferred to other users via the `AgentTransferInvite` system. This is a two-step process requiring acceptance by the recipient.

### Transfer Flow

```mermaid
stateDiagram-v2
    [*] --> NoTransfer: Agent owned by User A
    NoTransfer --> InviteSent: User A sends invite
    InviteSent --> Accepted: User B accepts
    InviteSent --> Cancelled: User A cancels
    InviteSent --> Declined: User B declines
    InviteSent --> Expired: 7 days pass
    
    Accepted --> [*]: Ownership transferred
    Cancelled --> NoTransfer
    Declined --> NoTransfer
    Expired --> NoTransfer
```

### Invitation Creation

Users initiate transfer via form on detail page:
- Input: Recipient email address
- Optional: Transfer message
- POST to `agent_detail` view with `action=transfer_agent`

**Backend Processing:**
1. Validate no pending invite exists
2. Create `AgentTransferInvite` record with `status=PENDING`
3. Send email notification to recipient
4. Display invite details on detail page

### Pending Transfer State

While an invite is pending:
- Detail page shows amber alert with recipient email and sent timestamp
- Original owner retains full configuration access
- `[Cancel Invitation]` button available
- Recipient sees invite in their dashboard with Accept/Decline buttons

**Sources:**
- [console/templates/console/agent_detail.html:22-35]()
- [console/templates/console/agent_detail.html:444-485]()
- [api/models.py]() (AgentTransferInvite model)

---

## Deletion

Agent deletion is a soft-delete operation that removes the agent from active listings but retains historical data.

### Delete Flow

```mermaid
graph TB
    DeleteBtn["Delete Agent Button<br/>Danger Zone"] --> Confirm["JavaScript Confirmation"]
    Confirm -->|Confirmed| Request["DELETE /console/agent/<id>/"]
    
    Request --> View["agent_delete view"]
    View --> ValidateOwner["Verify User Owns Agent"]
    ValidateOwner --> DeletePA["PersistentAgent.delete()"]
    
    DeletePA --> SignalHandler["pre_delete signal"]
    SignalHandler --> DeleteBA["BrowserUseAgent.delete()"]
    
    DeleteBA --> CascadeTasks["CASCADE DELETE<br/>BrowserUseAgentTask records"]
    DeletePA --> CascadeSteps["CASCADE DELETE<br/>PersistentAgentStep records"]
    
    CascadeSteps --> Response["200 OK JSON response"]
```

**Cascading Deletes:**

When a `PersistentAgent` is deleted:
1. Associated `BrowserUseAgent` is deleted (via signal handler)
2. All `BrowserUseAgentTask` records are cascade-deleted (FK constraint)
3. All `PersistentAgentStep` records are cascade-deleted (FK constraint)
4. All `PersistentAgentMessage` records are cascade-deleted
5. All `AgentSecret` records are cascade-deleted
6. Email accounts and SMS numbers are disassociated (FK set to NULL)

**Error Handling:**

The delete view includes defensive handling for edge cases:
- Missing `BrowserUseAgent` record (catches `DoesNotExist` exception)
- Foreign key constraint violations (attempts manual cleanup)
- Continues with deletion even if browser agent cleanup fails

**Sources:**
- [console/templates/console/agent_detail.html:599-640]()
- [console/views.py]() (agent_delete view)
- [tests/unit/test_console.py:23-174]()

---

## Configuration Persistence

All configuration changes are persisted via standard Django ORM operations:

| Configuration Area | Model | Update Method |
|-------------------|-------|---------------|
| Name, Charter, Status | `PersistentAgent` | Direct field update via form POST |
| Daily Credit Limit | `PersistentAgent` | `daily_credit_limit` field |
| Ownership | `PersistentAgent` | `organization` and `user` FK updates |
| Email Settings | `AgentEmailAccount` | Separate view/form |
| SMS Settings | `SmsNumber` | Separate view/form |
| Allowlist Entries | `CommsAllowlistEntry` | AJAX create/delete |
| Peer Links | `AgentPeerLink` | Inline form updates |
| Secrets | `AgentSecret` | Separate view/form |

**Transaction Safety:**

Configuration updates use database transactions to ensure atomicity. Failed validations roll back changes and display error messages to the user.

**Sources:**
- [console/views.py]() (agent_detail POST handler)
- [api/models.py]() (model definitions)

---

# Page: Agent Event Processing

# Agent Event Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py](api/migrations/0155_persistentagent_daily_credit_limit_and_more.py)
- [api/models.py](api/models.py)
- [console/templates/console/agent_detail.html](console/templates/console/agent_detail.html)
- [console/templates/partials/_agent_list.html](console/templates/partials/_agent_list.html)
- [console/views.py](console/views.py)
- [tests/unit/test_agent_event_processing_credits.py](tests/unit/test_agent_event_processing_credits.py)
- [tests/unit/test_console.py](tests/unit/test_console.py)

</details>



## Purpose and Scope

This page documents the event processing pipeline for persistent agents, covering the core execution flow from event triggers through LLM reasoning to tool execution. This includes credit gating, distributed locking, budget cycle management, and the LLM-tool loop that powers agent behavior.

For agent creation and provisioning, see [Creating Agents](#4.1). For agent lifecycle states and activation/deactivation, see [Agent Lifecycle](#4.4). For credit system architecture, see [TaskCreditService](#5.1).

---

## System Overview

Agent event processing is the central execution engine for `PersistentAgent` instances. When triggered by a cron schedule, incoming message, web chat interaction, or manual invocation, the system:

1. Acquires a distributed lock to prevent concurrent execution
2. Checks user/organization credit balance and daily agent limits
3. Executes an LLM-powered reasoning loop with tool calls
4. Manages budget cycles for follow-up processing after async tasks
5. Records execution steps and system events

```mermaid
graph TB
    Trigger["Trigger Event<br/>(cron/message/chat/manual)"]
    Entry["process_agent_events()"]
    Lock["Acquire Redlock<br/>(Redis-based)"]
    BudgetCtx["Initialize BudgetContext<br/>(agent_id, budget_id, branch_id, depth)"]
    PreCredit{{"Pre-processing<br/>Credit Gate"}}
    DailyLimit{{"Daily Credit<br/>Limit Check"}}
    AgentLoop["_run_agent_loop()"]
    PostProcess["Close Budget Cycle<br/>Update last_interaction_at"]
    
    Trigger --> Entry
    Entry --> Lock
    Lock --> BudgetCtx
    BudgetCtx --> PreCredit
    PreCredit -->|"No Credits"| LogCredit["Create SystemStep:<br/>credit_insufficient"]
    PreCredit -->|"Credits OK"| DailyLimit
    DailyLimit -->|"Limit Exceeded"| LogDaily["Create SystemStep:<br/>daily_credit_limit_exhausted"]
    DailyLimit -->|"Under Limit"| AgentLoop
    AgentLoop --> PostProcess
    LogCredit --> PostProcess
    LogDaily --> PostProcess
    
    style PreCredit fill:#ffe1e1
    style DailyLimit fill:#ffe1e1
```

**Sources:** [api/agent/core/event_processing.py:716-950]()

---

## Entry Point: `process_agent_events()`

The `process_agent_events()` function is the public API for triggering agent execution. It is called by:

- **Celery task** `process_agent_events_task` for async execution
- **Manual triggers** from console views
- **Follow-up scheduling** after browser tasks complete
- **Peer messaging** wake-up calls

### Distributed Locking

The function uses a Redis-based `Redlock` to ensure only one process handles events for a given agent at a time. If the lock cannot be acquired, a pending flag is set in Redis so that exactly one follow-up task runs after the current holder releases the lock.

| Lock Behavior | Action |
|--------------|--------|
| Lock acquired | Proceed with event processing |
| Lock busy | Set pending flag (`agent-event-processing:pending:{agent_id}`) and exit |
| Lock released | If pending flag exists, schedule follow-up task |

**Sources:** [api/agent/core/event_processing.py:804-834]()

### Budget Context Management

Event processing operates within a **budget cycle**, which tracks:

- `budget_id`: Unique identifier for the execution cycle
- `branch_id`: Identifier for this execution branch (for parallel child tasks)
- `depth`: Current recursion depth (0 for top-level)
- `max_steps`: Maximum steps allowed per cycle
- `max_depth`: Maximum recursion depth allowed

If no `budget_id` is provided (top-level trigger), the system calls `AgentBudgetManager.find_or_start_cycle()` to create or reuse an active cycle. If a `budget_id` is provided (follow-up from browser task), it validates the cycle is still active before proceeding.

**Sources:** [api/agent/core/event_processing.py:729-801]()

---

## Credit Gating Architecture

Event processing enforces credit limits at two levels: **pre-processing** (before the agent loop runs) and **per-tool** (during loop execution).

### Pre-Processing Credit Gate

Before entering the agent loop, the system checks:

1. **User/Organization Credit Balance**: Via `TaskCreditService.get_user_task_credits_available()`
2. **Daily Agent Limit**: Via `_get_agent_daily_credit_state()`

If either check fails, processing exits early and creates a `PersistentAgentSystemStep` with the appropriate code:

| Failure Reason | System Step Code | Notes Field |
|----------------|------------------|-------------|
| No user credits available | `PROCESS_EVENTS` | `credit_insufficient` |
| Daily agent limit exhausted | `PROCESS_EVENTS` | `daily_credit_limit_exhausted` |

**Sources:** [api/agent/core/event_processing.py:860-916]()

### Daily Credit Limit Calculation

Each agent can have a `daily_credit_limit` field (integer or null). The system calculates:

```python
daily_state = {
    "date": timezone.localdate(),
    "limit": agent.daily_credit_limit,  # None = unlimited
    "used": sum(step.credits_cost for today),
    "remaining": limit - used,
    "next_reset": midnight_tomorrow
}
```

The limit is checked using `_has_sufficient_daily_credit()`, which returns `False` if `remaining < cost`.

**Sources:** [api/agent/core/event_processing.py:451-508]()

### Per-Tool Credit Gate

During the agent loop, before each tool executes, `_ensure_credit_for_tool()` performs:

1. **Tool cost lookup**: Via `get_tool_credit_cost(tool_name)` (defaults to 1.0)
2. **Daily limit check**: Recomputed to include credits consumed in this loop
3. **Credit consumption**: `TaskCreditService.check_and_consume_credit(owner_user, amount=cost)`

If any check fails, the tool is skipped and a `PersistentAgentStep` is created with description indicating the reason.

```mermaid
graph TB
    ToolCall["LLM Returns Tool Call"]
    CostLookup["get_tool_credit_cost(tool_name)"]
    DailyCheck{{"Daily Limit<br/>Sufficient?"}}
    AvailCheck{{"Credits<br/>Available?"}}
    Consume["TaskCreditService.check_and_consume_credit()"]
    ConsumeOK{{"Consumption<br/>Success?"}}
    Execute["Execute Tool"]
    Skip["Skip Tool + Create Step<br/>(credit_insufficient_mid_loop)"]
    
    ToolCall --> CostLookup
    CostLookup --> DailyCheck
    DailyCheck -->|"No"| Skip1["Skip + Create Step<br/>(daily_credit_limit_mid_loop)"]
    DailyCheck -->|"Yes"| AvailCheck
    AvailCheck -->|"No"| Skip
    AvailCheck -->|"Yes"| Consume
    Consume --> ConsumeOK
    ConsumeOK -->|"No"| Skip2["Skip + Create Step<br/>(credit_consumption_failure)"]
    ConsumeOK -->|"Yes"| Execute
    
    style DailyCheck fill:#ffe1e1
    style AvailCheck fill:#ffe1e1
    style ConsumeOK fill:#ffe1e1
```

**Sources:** [api/agent/core/event_processing.py:510-711]()

---

## The Agent Loop: `_run_agent_loop()`

The core reasoning engine is `_run_agent_loop()`, which implements a ReAct-style (Reasoning + Acting) pattern. The loop alternates between:

1. **LLM reasoning** with context from conversation history, tool results, and system prompts
2. **Tool execution** based on LLM-generated tool calls
3. **Iteration** until completion criteria are met or limits are hit

### Loop Structure

```mermaid
graph TB
    Start["Loop Iteration i"]
    BuildPrompt["Build Prompt via Promptree<br/>(charter, history, tool defs)"]
    EstimateTokens["Estimate Token Count"]
    SelectTier["Select LLM Tier<br/>(based on token budget)"]
    Failover["_completion_with_failover()"]
    ParseResp{{"Response<br/>Has Tool Calls?"}}
    
    Reasoning["Create PersistentAgentStep<br/>(description = reasoning text)"]
    ToolLoop["For Each Tool Call"]
    CreditCheck["_ensure_credit_for_tool()"]
    ToolOK{{"Credit<br/>OK?"}}
    ExecTool["Execute Tool<br/>(browser/MCP/comms)"]
    RecordResult["Create PersistentAgentToolCall<br/>Link to Step"]
    
    CheckLimit{{"i < MAX_ITERATIONS<br/>and not done?"}}
    Complete["Loop Complete"]
    
    Start --> BuildPrompt
    BuildPrompt --> EstimateTokens
    EstimateTokens --> SelectTier
    SelectTier --> Failover
    Failover --> ParseResp
    
    ParseResp -->|"No Tools"| Reasoning
    ParseResp -->|"Has Tools"| ToolLoop
    
    ToolLoop --> CreditCheck
    CreditCheck --> ToolOK
    ToolOK -->|"No"| SkipTool["Skip Tool"]
    ToolOK -->|"Yes"| ExecTool
    ExecTool --> RecordResult
    RecordResult --> NextTool{{"More<br/>Tools?"}}
    SkipTool --> NextTool
    
    NextTool -->|"Yes"| ToolLoop
    NextTool -->|"No"| CheckLimit
    Reasoning --> CheckLimit
    
    CheckLimit -->|"Yes"| Start
    CheckLimit -->|"No"| Complete
    
    style ToolOK fill:#ffe1e1
```

**Sources:** [api/agent/core/event_processing.py:1164-1605]()

### Prompt Building with Promptree

The system uses the `Promptree` library to build prompts within a token budget. Key components:

- **System Prompt**: Includes charter, current date/time, filesystem context (if SQLite DB exists), enabled tool definitions
- **Conversation History**: Recent `PersistentAgentMessage` records (compacted if needed)
- **Tool Execution History**: Recent `PersistentAgentStep` + `PersistentAgentToolCall` records (compacted if needed)
- **Token Budget**: `PROMPT_TOKEN_BUDGET = 120000` tokens

The `Promptree.build()` method estimates token counts and prunes history to fit within the budget, prioritizing recent interactions.

**Sources:** [api/agent/core/event_processing.py:1164-1350]()

### LLM Tier Selection

Before calling the LLM, the system estimates total tokens (prompt + expected completion) and selects a tier using `get_llm_config_with_failover()`. Tiers are defined in `llm_config.py` and typically look like:

| Tier | Token Range | Providers |
|------|-------------|-----------|
| Tier 1 | < 10K tokens | Fast, cheap models (e.g., GPT-4o mini) |
| Tier 2 | 10K-50K tokens | Mid-tier models (e.g., Claude 3.5 Sonnet) |
| Tier 3 | 50K-120K tokens | Large context models (e.g., Claude 3 Opus) |

Each tier has a failover list with weighted endpoint distribution.

**Sources:** [api/agent/core/event_processing.py:1353-1363](), [api/agent/core/llm_config.py:150-280]()

---

## LLM Completion with Failover

The `_completion_with_failover()` function implements tiered failover across multiple LLM providers. It iterates through pre-selected provider configurations and retries with exponential backoff for transient errors.

### Failover Flow

```mermaid
graph TB
    Start["_completion_with_failover()<br/>(messages, tools, failover_configs)"]
    ForEach["For Each (provider, model, params)"]
    TryCall["run_completion()<br/>(LiteLLM wrapper)"]
    Success{{"Success?"}}
    Return["Return Response + Token Usage"]
    NextProvider["Try Next Provider"]
    AllFailed["Raise Last Exception"]
    
    Start --> ForEach
    ForEach --> TryCall
    TryCall --> Success
    Success -->|"Yes"| Return
    Success -->|"No"| Log["Log Exception + Mark Span Failed"]
    Log --> NextProvider
    NextProvider --> MoreProviders{{"More<br/>Providers?"}}
    MoreProviders -->|"Yes"| ForEach
    MoreProviders -->|"No"| AllFailed
    
    style Success fill:#e1f5ff
```

### Token Usage Tracking

On successful completion, the function extracts token usage from `response.model_extra.get("usage")` and builds a dictionary:

```python
token_usage = {
    "prompt_tokens": usage.prompt_tokens,
    "completion_tokens": usage.completion_tokens,
    "total_tokens": usage.total_tokens,
    "model": model,
    "provider": provider,
    "cached_tokens": usage.prompt_tokens_details.cached_tokens  # if available
}
```

This data is recorded in `PersistentAgentStep` for audit purposes.

**Sources:** [api/agent/core/event_processing.py:289-419]()

### Exponential Backoff Wrapper

The `_completion_with_backoff()` function (legacy, now mostly unused) wraps LiteLLM calls with retry logic using the `tenacity` library:

- **Wait strategy**: Exponential backoff (1s to 60s)
- **Stop condition**: 3 attempts max
- **Retry on**: `RateLimitError`, `ServiceUnavailableError`, `APIConnectionError`, `Timeout`

**Sources:** [api/agent/core/event_processing.py:421-445]()

---

## Tool Execution

When the LLM response includes tool calls, each tool is executed sequentially within the loop. Tool execution varies by type:

### Tool Type Dispatch

```mermaid
graph LR
    ToolCall["Tool Call from LLM"]
    Dispatch{{"Tool Type?"}}
    
    Browser["browse_web<br/>execute_spawn_web_task()"]
    MCP["MCP Tool<br/>execute_mcp_tool()"]
    Email["send_email<br/>execute_send_email()"]
    SMS["send_sms<br/>execute_send_sms()"]
    Chat["send_chat_message<br/>execute_send_chat_message()"]
    Peer["send_agent_message<br/>execute_send_agent_message()"]
    SQLite["sqlite_query/sqlite_batch<br/>execute_sqlite_batch()"]
    Schedule["update_schedule<br/>execute_update_schedule()"]
    Charter["update_charter<br/>execute_update_charter()"]
    
    ToolCall --> Dispatch
    Dispatch --> Browser
    Dispatch --> MCP
    Dispatch --> Email
    Dispatch --> SMS
    Dispatch --> Chat
    Dispatch --> Peer
    Dispatch --> SQLite
    Dispatch --> Schedule
    Dispatch --> Charter
```

### Browser Tasks

Browser automation tools (`browse_web`, `spawn_web_task`) create a `BrowserUseAgentTask` record and schedule it for async execution via `process_browser_use_task.delay()`. The browser worker:

1. Sets up Chrome profile and proxy
2. Executes browser automation using the `browser-use` library
3. Saves result and creates `BrowserUseAgentTaskStep` records
4. Calls `_schedule_agent_follow_up()` to continue the agent loop

The follow-up passes the same `budget_id` to continue the budget cycle, allowing the agent to see the browser task result in its next iteration.

**Sources:** [api/agent/core/event_processing.py:1417-1440](), [api/agent/tasks.py:150-500]()

### MCP Tool Execution

MCP (Model Context Protocol) tools are executed via `execute_mcp_tool()`, which:

1. Resolves the server (Bright Data stdio or Pipedream HTTP)
2. Calls `client.call_tool()` with tool name and arguments
3. Handles OAuth Connect Link flows for tools requiring user authorization
4. Returns result or action-required response

If a Connect Link is required, the agent creates a `PipedreamConnectSession`, generates a first-party OAuth URL, and includes it in the tool result. The agent loop pauses until the user authorizes, then resumes via webhook.

**Sources:** [api/agent/tools/mcp_tools.py:200-350]()

### Communication Tools

Communication tools (email, SMS, chat, peer messaging) execute synchronously and return success/failure status:

- `send_email`: Creates `PersistentAgentMessage` with `direction=OUTBOUND`, sends via SMTP
- `send_sms`: Creates message, sends via Twilio
- `send_chat_message`: Broadcasts via WebSocket to web chat clients
- `send_agent_message`: Uses `PeerMessagingService` to send to another agent (with quota/debouncing checks)

All communication tools respect the agent's allowlist configuration.

**Sources:** [api/agent/core/event_processing.py:1441-1520]()

---

## State Management

### Step Recording

Each tool execution creates a `PersistentAgentStep` record with:

- `agent`: Foreign key to `PersistentAgent`
- `description`: Human-readable summary of the action
- `created_at`: Timestamp
- `credits_cost`: Cost consumed for this step (if applicable)

If the tool generated a tool call, a `PersistentAgentToolCall` record is also created:

- `step`: Foreign key to the step
- `name`: Tool function name
- `arguments`: JSON of arguments passed
- `result`: JSON of result returned

**Sources:** [api/agent/core/event_processing.py:1380-1520]()

### System Steps for Errors

When processing encounters errors or skips actions, it creates a `PersistentAgentSystemStep` linked to a step:

| Code | Notes | Meaning |
|------|-------|---------|
| `PROCESS_EVENTS` | `credit_insufficient` | Pre-processing credit gate blocked execution |
| `PROCESS_EVENTS` | `daily_credit_limit_exhausted` | Daily limit reached before loop |
| `PROCESS_EVENTS` | `credit_insufficient_mid_loop` | Tool skipped due to insufficient credits |
| `PROCESS_EVENTS` | `daily_credit_limit_mid_loop` | Tool skipped due to daily limit |
| `PROCESS_EVENTS` | `credit_consumption_failure_mid_loop` | Credit consumption transaction failed |

**Sources:** [api/agent/core/event_processing.py:860-916](), [api/agent/core/event_processing.py:582-688]()

### Budget Cycle Closing

When the agent loop completes (or exits early), the system attempts to close the budget cycle via `AgentBudgetManager.close_cycle()`. This only succeeds if:

- The current branch depth is 0 (no outstanding child tasks)
- The cycle hasn't already been closed

If child tasks are outstanding (e.g., browser tasks still running), the cycle remains active so follow-ups can continue it.

**Sources:** [api/agent/core/event_processing.py:178-208](), [api/agent/core/event_processing.py:1880-1900]()

---

## Code Entity Reference

### Key Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `process_agent_events()` | [api/agent/core/event_processing.py:716-950]() | Entry point for event processing |
| `_process_agent_events_locked()` | [api/agent/core/event_processing.py:952-1162]() | Internal handler after lock acquisition |
| `_run_agent_loop()` | [api/agent/core/event_processing.py:1164-1605]() | Main LLM-tool reasoning loop |
| `_completion_with_failover()` | [api/agent/core/event_processing.py:289-419]() | LLM completion with tiered failover |
| `_ensure_credit_for_tool()` | [api/agent/core/event_processing.py:510-711]() | Per-tool credit gate |
| `_get_agent_daily_credit_state()` | [api/agent/core/event_processing.py:451-489]() | Daily limit calculation |

### Key Models

| Model | Purpose |
|-------|---------|
| `PersistentAgent` | Main agent configuration (charter, schedule, etc.) |
| `PersistentAgentStep` | Individual execution step record |
| `PersistentAgentToolCall` | Tool invocation details |
| `PersistentAgentSystemStep` | Error/event annotations |
| `PersistentAgentMessage` | Communication history |
| `BrowserUseAgentTask` | Browser automation task record |
| `TaskCredit` | Credit allocation and consumption tracking |

### Key Constants

| Constant | Value | Location |
|----------|-------|----------|
| `MAX_AGENT_LOOP_ITERATIONS` | 100 | [api/agent/core/event_processing.py:107]() |
| `PROMPT_TOKEN_BUDGET` | 120000 | [api/agent/core/event_processing.py:211]() |
| `MESSAGE_HISTORY_LIMIT` | 20 | [api/agent/core/event_processing.py:108]() |
| `TOOL_CALL_HISTORY_LIMIT` | 20 | [api/agent/core/event_processing.py:109]() |

**Sources:** [api/agent/core/event_processing.py:1-112](), [api/models.py:1-5000]()

---

## Testing

The event processing system has comprehensive test coverage:

- **Credit gating tests**: [tests/unit/test_agent_event_processing_credits.py]() validates pre-processing gates, daily limits, and per-tool credit checks
- **Console integration tests**: [tests/unit/test_console.py]() verifies daily limit UI and agent updates
- **Agent lifecycle tests**: Validate state transitions and budget cycle management

Tests use mocking extensively to isolate event processing from external dependencies (LLM APIs, browser execution, etc.).

**Sources:** [tests/unit/test_agent_event_processing_credits.py:1-346](), [tests/unit/test_console.py:236-316]()

---

# Page: Agent Lifecycle

# Agent Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [api/exceptions.py](api/exceptions.py)
- [api/migrations/0145_browseruseagenttask_organization_and_more.py](api/migrations/0145_browseruseagenttask_organization_and_more.py)
- [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py](api/migrations/0155_persistentagent_daily_credit_limit_and_more.py)
- [api/serializers.py](api/serializers.py)
- [api/services/persistent_agents.py](api/services/persistent_agents.py)
- [api/urls.py](api/urls.py)
- [api/views.py](api/views.py)
- [console/templates/console/agent_detail.html](console/templates/console/agent_detail.html)
- [console/templates/partials/_agent_list.html](console/templates/partials/_agent_list.html)
- [tests/unit/test_agent_event_processing_credits.py](tests/unit/test_agent_event_processing_credits.py)
- [tests/unit/test_api.py](tests/unit/test_api.py)
- [tests/unit/test_api_persistent_agents.py](tests/unit/test_api_persistent_agents.py)
- [tests/unit/test_console.py](tests/unit/test_console.py)

</details>



This page documents the lifecycle states and transitions of `PersistentAgent` instances, including activation/deactivation, soft deletion, hard deletion, and lifecycle hooks. For information about creating agents, see [Creating Agents](#4.1). For event processing behavior, see [Agent Event Processing](#4.3).

---

## Agent Lifecycle States

Agents exist in one of two **life states** and have an independent **activation flag**. These two dimensions control whether an agent is operational and how it interacts with the platform.

### Life State Enumeration

The `life_state` field on `PersistentAgent` uses the `LifeState` enumeration with two values:

| State | Value | Description |
|-------|-------|-------------|
| `ACTIVE` | `"active"` | Default state. Agent is operational and can be scheduled or triggered. |
| `EXPIRED` | `"expired"` | Terminal state. Agent has been soft-deleted and cannot be reactivated without manual intervention. |

**Sources:** [api/models.py:PersistentAgent.LifeState]()

### Activation Flag

The `is_active` boolean field independently controls whether the agent accepts new work:

- **`is_active=True`**: Agent responds to triggers (schedule, messages, manual events)
- **`is_active=False`**: Agent is paused; triggers are ignored but agent remains in the system

This flag can be toggled by users via the console UI or API without affecting `life_state`.

**Sources:** [console/templates/console/agent_detail.html:160-199](), [api/serializers.py:435-465]()

---

## State Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> ACTIVE_Active: provision()
    
    ACTIVE_Active: life_state=ACTIVE<br/>is_active=True
    ACTIVE_Paused: life_state=ACTIVE<br/>is_active=False
    EXPIRED_Inactive: life_state=EXPIRED<br/>is_active=False
    
    ACTIVE_Active --> ACTIVE_Paused: User toggles is_active=False
    ACTIVE_Paused --> ACTIVE_Active: User toggles is_active=True
    
    ACTIVE_Active --> EXPIRED_Inactive: Soft Delete (API DELETE)
    ACTIVE_Paused --> EXPIRED_Inactive: Soft Delete (API DELETE)
    
    EXPIRED_Inactive --> [*]: Hard Delete (Console UI)
    
    note right of ACTIVE_Active
        Accepts all triggers:
        - Cron schedule
        - Inbound messages
        - Manual events
        - Peer messages
    end note
    
    note right of ACTIVE_Paused
        Ignores triggers.
        Agent exists but dormant.
    end note
    
    note right of EXPIRED_Inactive
        Terminal state.
        schedule set to null.
        Cannot be reactivated via UI/API.
    end note
```

**Sources:** [tests/unit/test_api_persistent_agents.py:376-387](), [api/views.py:596-657]()

---

## Activation and Deactivation

### User-Initiated Activation Toggle

Users can toggle `is_active` via:

1. **Console UI**: Agent detail page toggle switch [console/templates/console/agent_detail.html:192-197]()
2. **REST API**: `PATCH /api/v1/agents/{id}/` with `{"is_active": true/false}`

When toggled, the agent's behavior changes immediately:

- **Activated** (`is_active=True`): The agent begins accepting triggers and will process events on the next scheduled run or incoming message.
- **Deactivated** (`is_active=False`): The agent stops processing new events. Scheduled tasks are not executed, and inbound messages are ignored (though message records may still be created for audit purposes).

**Implementation Detail**: The `is_active` flag is checked at the start of event processing in `process_agent_events_locked`. If `False`, the function exits early without consuming credits or executing the agent loop.

**Sources:** [api/serializers.py:435-465](), [console/templates/console/agent_detail.html:160-199]()

---

## Soft Deletion (API DELETE)

When a user issues a `DELETE` request to the API endpoint for an agent, the system performs a **soft delete** rather than removing the database record.

### Soft Delete Behavior

The `PersistentAgentViewSet.destroy()` method [api/views.py:596-657]() executes the following state transitions:

1. Set `life_state = PersistentAgent.LifeState.EXPIRED`
2. Set `is_active = False`
3. Set `schedule = None` (cancels all scheduled triggers)

```mermaid
graph LR
    A["DELETE /api/v1/agents/{id}/"] --> B["PersistentAgentViewSet.destroy()"]
    B --> C["Set life_state=EXPIRED"]
    C --> D["Set is_active=False"]
    D --> E["Set schedule=None"]
    E --> F["HTTP 204 No Content"]
    
    style A fill:#f9f9f9
    style F fill:#f9f9f9
```

**Sources:** [api/views.py:596-657](), [tests/unit/test_api_persistent_agents.py:376-387]()

### Why Soft Delete?

Soft deletion preserves:
- Historical data (agent steps, messages, tasks)
- Audit trails for billing and usage analytics
- The ability to restore agents manually if needed (though no automated UI flow exists)

The agent becomes invisible in normal UI listings (filtered by `life_state=ACTIVE`) but remains queryable for administrative purposes.

**Sources:** [api/views.py:596-657]()

---

## Hard Deletion (Console UI)

The console provides a **hard delete** operation that fully removes the agent and its associated `BrowserUseAgent` record from the database.

### Hard Delete Flow

```mermaid
sequenceDiagram
    participant User
    participant Console as "Console UI"
    participant View as "agent_delete view"
    participant DB as "Database"
    
    User->>Console: Click "Delete Agent"
    Console->>User: Show confirmation modal
    User->>Console: Confirm deletion
    Console->>View: DELETE /console/agents/{pk}/delete/
    
    View->>DB: Load PersistentAgent
    View->>DB: Load BrowserUseAgent
    
    alt BrowserUseAgent exists
        View->>DB: DELETE BrowserUseAgent
    end
    
    View->>DB: DELETE PersistentAgent
    View->>Console: HTTP 200 OK
    Console->>User: Redirect to agent list
```

**Sources:** [tests/unit/test_console.py:23-84]()

### Deletion Safeguards

The console view handles several edge cases:

1. **Missing BrowserUseAgent**: If the `BrowserUseAgent` record is missing (e.g., manually deleted), deletion proceeds without error [tests/unit/test_console.py:61-83]()
2. **Orphaned Tasks**: Associated `BrowserUseAgentTask` records are cascade-deleted [tests/unit/test_console.py:151-173]()
3. **Exception Handling**: If `PersistentAgent.delete()` raises `BrowserUseAgent.DoesNotExist`, the view catches it and performs manual cleanup [tests/unit/test_console.py:126-148]()

**Sources:** [tests/unit/test_console.py:23-174]()

---

## Lifecycle Hooks and Side Effects

### On Agent Creation

When a `PersistentAgent` is created via the provisioning service:

1. **BrowserUseAgent Creation**: A backing `BrowserUseAgent` is created first [api/services/persistent_agents.py:78-91]()
2. **Template Application**: If `template_code` is provided, charter and schedule are populated from the template [api/services/persistent_agents.py:133-162]()
3. **Daily Credit Limit**: For free-tier users, `daily_credit_limit` is set to the default value [api/services/persistent_agents.py:120-131]()
4. **Event Processing Trigger**: After transaction commit, `process_agent_events_task.delay()` is enqueued [api/serializers.py:428-431]()

**Sources:** [api/services/persistent_agents.py:50-169](), [api/serializers.py:370-433]()

### On Activation

When `is_active` transitions from `False` to `True`:

- **No immediate side effects** beyond the database update
- The agent becomes eligible for processing on the next trigger (schedule, message, etc.)
- If a schedule exists, Celery Beat will begin invoking the agent on the next scheduled interval

**Sources:** [api/serializers.py:435-465]()

### On Deactivation

When `is_active` transitions from `True` to `False`:

- **In-flight tasks continue**: If event processing is already running, it completes
- **Future triggers ignored**: Scheduled tasks are skipped; the Celery Beat task checks `is_active` before enqueueing work
- **Messages still recorded**: Inbound messages may still create `PersistentAgentMessage` records depending on allowlist configuration, but processing is deferred

**Sources:** [console/templates/console/agent_detail.html:160-199]()

### On Soft Deletion

When `life_state` transitions to `EXPIRED`:

1. **Schedule Cleared**: `schedule = None` prevents any future Celery Beat triggers [api/views.py:596-657]()
2. **Deactivation**: `is_active = False` ensures immediate cessation of processing
3. **UI Filtering**: Agent is hidden from console listings (filtered by `life_state=ACTIVE`)
4. **Data Retention**: All related records (steps, messages, tasks) are preserved

**Sources:** [api/views.py:596-657](), [tests/unit/test_api_persistent_agents.py:376-387]()

### On Hard Deletion

When a `PersistentAgent` is hard-deleted:

1. **BrowserUseAgent Deletion**: The backing browser agent is deleted (cascade) [tests/unit/test_console.py:23-58]()
2. **Task Cleanup**: All `BrowserUseAgentTask` records are cascade-deleted [tests/unit/test_console.py:151-173]()
3. **Step Cleanup**: All `PersistentAgentStep` records are cascade-deleted
4. **Message Cleanup**: `PersistentAgentMessage` records may be cascade-deleted depending on foreign key configuration

**Sources:** [tests/unit/test_console.py:23-174]()

---

## Daily Credit Limits and Lifecycle

The `daily_credit_limit` field affects agent lifecycle by imposing a per-day spending cap.

### Daily Limit Lifecycle

```mermaid
graph TD
    A["Agent Activated"] --> B{"daily_credit_limit set?"}
    B -->|No| C["Unlimited credits per day"]
    B -->|Yes| D["Track daily usage"]
    
    D --> E{"Usage >= limit?"}
    E -->|No| F["Process events normally"]
    E -->|Yes| G["Skip event processing"]
    
    G --> H["Create SystemStep: daily_credit_limit_exhausted"]
    H --> I["Wait for daily reset"]
    
    I --> J["Midnight UTC"]
    J --> D
    
    F --> K["Consume credits"]
    K --> D
```

**Sources:** [tests/unit/test_agent_event_processing_credits.py:148-182](), [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py:1-51]()

### Daily Limit Enforcement

Daily limits are enforced at two levels:

1. **Pre-processing gate** [tests/unit/test_agent_event_processing_credits.py:148-182](): Before the agent loop begins, `_process_agent_events_locked` checks if the agent has exceeded its daily limit. If so, it creates a `PersistentAgentSystemStep` with `notes="daily_credit_limit_exhausted"` and exits early.

2. **Mid-loop gate** [tests/unit/test_agent_event_processing_credits.py:316-346](): During tool execution, `_ensure_credit_for_tool` checks daily limits before executing each tool. If the limit is hit mid-loop, the tool is skipped with a system note.

### Daily Limit Configuration

- **Free-tier default**: Set to `DEFAULT_AGENT_DAILY_CREDIT_LIMIT` (typically 10 credits) during provisioning [api/services/persistent_agents.py:120-131]()
- **Pro plans**: Typically `null` (unlimited)
- **User-configurable**: Can be updated via console UI or API [console/templates/console/agent_detail.html:202-253]()

**Sources:** [api/migrations/0155_persistentagent_daily_credit_limit_and_more.py:1-51](), [tests/unit/test_console.py:237-291]()

---

## Agent Ownership Transfer Lifecycle

Agents can be transferred between users via an invitation flow. During the transfer, the agent remains operational but ownership is in a pending state.

### Transfer States

```mermaid
stateDiagram-v2
    [*] --> OwnedByOriginal: Agent exists
    OwnedByOriginal --> TransferPending: Create AgentTransferInvite
    TransferPending --> OwnedByRecipient: Recipient accepts
    TransferPending --> OwnedByOriginal: Sender cancels OR recipient declines
    OwnedByRecipient --> [*]
    
    note right of TransferPending
        Agent remains owned by sender.
        Sender can still edit settings.
        Invitation visible in UI.
    end note
```

**Sources:** [console/templates/console/agent_detail.html:22-35](), [console/templates/console/agent_detail.html:444-485]()

### Transfer Lifecycle Details

1. **Invitation Creation**: Sender enters recipient email and optional message. An `AgentTransferInvite` record is created with `status=PENDING` [console/templates/console/agent_detail.html:466-482]()

2. **Pending State**: 
   - Agent remains fully owned by sender
   - Sender can continue editing configuration
   - Warning banner shows in agent detail view [console/templates/console/agent_detail.html:22-35]()
   - Sender can cancel the invitation at any time [console/templates/console/agent_detail.html:457-463]()

3. **Acceptance**: Recipient logs in, sees invitation in their console, and accepts. Ownership transfers atomically.

4. **Cancellation**: If sender cancels or recipient declines, invitation is deleted and agent remains with sender.

**Sources:** [console/templates/console/agent_detail.html:22-35](), [console/templates/console/agent_detail.html:444-485]()

---

## Lifecycle Code Entities Reference

### Key Models

| Model | Field/Method | Purpose |
|-------|-------------|---------|
| `PersistentAgent` | `life_state` | Tracks ACTIVE/EXPIRED state |
| `PersistentAgent` | `is_active` | Boolean activation flag |
| `PersistentAgent` | `schedule` | Cron expression; cleared on soft delete |
| `PersistentAgent` | `daily_credit_limit` | Per-day spending cap (nullable) |
| `BrowserUseAgent` | (record) | Backing agent for browser automation; deleted on hard delete |

**Sources:** [api/models.py:PersistentAgent]()

### Key Service Methods

| Class | Method | Lifecycle Role |
|-------|--------|----------------|
| `PersistentAgentProvisioningService` | `provision()` | Creates agent with initial ACTIVE state |
| `PersistentAgentViewSet` | `destroy()` | Implements soft delete (sets EXPIRED) |
| Console view | `agent_delete` | Implements hard delete (removes from DB) |

**Sources:** [api/services/persistent_agents.py:50-169](), [api/views.py:596-657]()

### Key Tests

| Test | File | Coverage |
|------|------|----------|
| `test_soft_delete_agent_marks_expired` | test_api_persistent_agents.py:376-387 | Verifies soft delete state transitions |
| `test_delete_persistent_agent_also_deletes_browser_agent` | test_console.py:23-58 | Verifies hard delete cascade behavior |
| `test_process_agent_events_respects_daily_limit` | test_agent_event_processing_credits.py:148-182 | Verifies daily limit enforcement |

**Sources:** [tests/unit/test_api_persistent_agents.py:376-387](), [tests/unit/test_console.py:23-174](), [tests/unit/test_agent_event_processing_credits.py:148-182]()

---

## Summary

The agent lifecycle is managed through two primary state dimensions:

1. **`life_state`**: Binary ACTIVE/EXPIRED distinction, where EXPIRED is a terminal state reached via soft deletion
2. **`is_active`**: User-controllable activation flag that determines whether the agent processes events

Deletion occurs at two levels: **soft delete** (via API, sets EXPIRED) and **hard delete** (via console, removes from database). Daily credit limits add an operational constraint that can pause agents without changing their lifecycle state.

For information on how lifecycle states interact with event processing, see [Agent Event Processing](#4.3). For initial provisioning details, see [Creating Agents](#4.1).

---

# Page: Credit & Billing System

# Credit & Billing System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/migrations/0115_persistentagentstep_credits_fields.py](api/migrations/0115_persistentagentstep_credits_fields.py)
- [console/forms.py](console/forms.py)
- [console/templates/console/organization_detail.html](console/templates/console/organization_detail.html)
- [console/templates/partials/_org_invite_modal.html](console/templates/partials/_org_invite_modal.html)
- [constants/stripe.py](constants/stripe.py)
- [pages/signals.py](pages/signals.py)
- [tasks/services.py](tasks/services.py)
- [tests/unit/test_organizations.py](tests/unit/test_organizations.py)
- [tests/unit/test_pages_signals.py](tests/unit/test_pages_signals.py)
- [tests/unit/test_persistent_agent_step_credits.py](tests/unit/test_persistent_agent_step_credits.py)
- [tests/unit/test_task_credit_service.py](tests/unit/test_task_credit_service.py)
- [tests/unit/test_tool_costs.py](tests/unit/test_tool_costs.py)
- [util/tool_costs.py](util/tool_costs.py)

</details>



## Purpose and Scope

This document describes the platform's financial management infrastructure, covering credit allocation, consumption tracking, subscription management, and usage metering. The credit system controls resource access by gating agent operations based on available task credits, while the billing system manages subscription lifecycle, seat-based organizational billing, and integration with Stripe for payments and metering.

For information about agent execution and event processing (which consumes credits), see [Agent Event Processing](#4.3). For details on specific plan configurations and limits, see [Platform Overview](#1).

---

## Architecture Overview

The billing system operates on a dual-ownership model where both individual users and organizations can own agents and consume credits. Credits are granted based on subscription plans, consumed during agent operations, and metered to Stripe for overage billing.

```mermaid
graph TB
    subgraph "Owner Types"
        User["User<br/>(UserBilling)"]
        Org["Organization<br/>(OrganizationBilling)"]
    end
    
    subgraph "Stripe Integration"
        StripeCustomer["Stripe Customer"]
        StripeSub["Stripe Subscription<br/>- Base Plan SKU<br/>- Overage SKU (optional)"]
        StripeMeter["Stripe Meter Events"]
    end
    
    subgraph "Credit Management"
        TaskCreditService["TaskCreditService"]
        TaskCredit["TaskCredit<br/>- credits<br/>- credits_used<br/>- expiration_date<br/>- additional_task flag"]
        TaskCreditConfig["TaskCreditConfig<br/>(singleton)"]
        ToolCreditCost["ToolCreditCost<br/>(per-tool overrides)"]
    end
    
    subgraph "Consumption Points"
        AgentStep["PersistentAgentStep"]
        BrowserTask["BrowserUseAgentTask"]
        CommMessage["PersistentAgentMessage"]
    end
    
    User --> UserBilling
    Org --> OrganizationBilling
    
    UserBilling --> StripeCustomer
    OrganizationBilling --> StripeCustomer
    StripeCustomer --> StripeSub
    
    StripeSub -->|"webhook events"| TaskCreditService
    
    TaskCreditService -->|"grants"| TaskCredit
    TaskCreditService -->|"consumes"| TaskCredit
    TaskCreditService -->|"reads config"| TaskCreditConfig
    TaskCreditService -->|"reads costs"| ToolCreditCost
    
    AgentStep -->|"consumes on create"| TaskCredit
    BrowserTask -->|"consumes on create"| TaskCredit
    CommMessage -->|"consumes via service"| TaskCredit
    
    TaskCredit -->|"additional_task=true"| StripeMeter
```

**Sources:** [tasks/services.py:1-1433](), [pages/signals.py:233-651](), [util/tool_costs.py:1-153]()

---

## Core Data Models

### TaskCredit

The `TaskCredit` model represents a block of credits granted to a user or organization. Each block has a fixed quantity, tracks usage, and expires at a specific date aligned with the billing cycle.

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | User owner (null for org-owned credits) |
| `organization` | ForeignKey | Organization owner (null for user-owned credits) |
| `credits` | Decimal | Total credits in this block |
| `credits_used` | Decimal | Credits consumed from this block |
| `granted_date` | DateTime | When credits became available |
| `expiration_date` | DateTime | When credits expire (typically subscription period end) |
| `stripe_invoice_id` | String | Associated Stripe invoice for idempotency |
| `plan` | Enum | Plan that granted these credits |
| `grant_type` | Enum | Source of grant (PLAN, MANUAL, etc.) |
| `additional_task` | Boolean | True if overage credit (triggers metering) |
| `voided` | Boolean | Invalidates credit without deletion |

**Sources:** [tasks/services.py:244-306](), [tests/unit/test_task_credit_service.py:290-359]()

### Billing Models

**UserBilling:**
- `subscription`: Current plan name
- `max_extra_tasks`: Overage limit (-1 for unlimited)
- `billing_cycle_anchor`: Day of month for billing (1-28)
- `stripe_customer_id`: Associated Stripe customer

**OrganizationBilling:**
- `subscription`: Current plan name
- `purchased_seats`: Number of paid seats
- `max_extra_tasks`: Overage limit per seat
- `billing_cycle_anchor`: Day of month for billing
- `stripe_subscription_id`: Active subscription ID
- `pending_seat_quantity`: Scheduled seat change (if any)
- `pending_seat_effective_at`: When seat change takes effect
- `pending_seat_schedule_id`: Stripe schedule ID
- `cancel_at`: Scheduled cancellation timestamp
- `cancel_at_period_end`: Whether to cancel at period end

**Sources:** [pages/signals.py:293-356](), [tests/unit/test_organizations.py:569-629]()

---

## TaskCreditService

The `TaskCreditService` ([tasks/services.py:107-1433]()) is the authoritative service for all credit operations. It provides owner-aware methods that handle both user and organization contexts transparently.

### Credit Granting

#### User Subscription Credits

When a user subscribes, credits are granted based on their plan's `monthly_task_credits` value:

```mermaid
sequenceDiagram
    participant Stripe
    participant Webhook as handle_subscription_event
    participant Service as TaskCreditService
    participant DB as TaskCredit

    Stripe->>Webhook: subscription.created/updated
    Webhook->>Webhook: Extract plan and invoice_id
    Webhook->>Service: grant_subscription_credits(user, plan, invoice_id)
    Service->>DB: Check existing invoice_id
    alt Invoice already processed
        Service-->>Webhook: Return 0 (idempotent)
    else New invoice
        Service->>DB: Create TaskCredit<br/>credits=plan.monthly_task_credits<br/>expiration_date=current_period_end
        Service-->>Webhook: Return credits_granted
    end
```

**Key Implementation Details:**
- Idempotency via `stripe_invoice_id` check ([tasks/services.py:247-255]())
- Expiration defaults to subscription `current_period_end` ([tasks/services.py:278-287]())
- Coerces timestamps from Stripe's various formats ([tasks/services.py:81-104]())

**Sources:** [tasks/services.py:201-306](), [pages/signals.py:428-434](), [tests/unit/test_task_credit_service.py:52-89]()

#### Organization Subscription Credits

Organizations receive credits based on `credits_per_seat × purchased_seats`:

```mermaid
sequenceDiagram
    participant Webhook
    participant Service as TaskCreditService
    participant DB as TaskCredit

    Webhook->>Service: grant_subscription_credits_for_organization(org, seats, plan)
    Service->>Service: Calculate credits = plan.credits_per_seat × seats
    
    alt replace_current=True (renewal)
        Service->>DB: Find existing PLAN block
        Service->>DB: UPDATE credits, reset credits_used=0
    else New grant
        Service->>DB: CREATE new TaskCredit
    end
    
    Service-->>Webhook: Return credits_granted
```

The `replace_current` flag ([tasks/services.py:364-402]()) handles monthly renewals by updating the existing credit block instead of stacking duplicates. This ensures organizations don't accumulate multiple overlapping credit blocks during normal billing cycles.

**Sources:** [tasks/services.py:308-416](), [pages/signals.py:643-650](), [tests/unit/test_task_credit_service.py:328-359]()

### Credit Consumption

#### Atomic Consumption with SELECT FOR UPDATE

Credits are consumed atomically using database row-level locking to prevent race conditions:

```python
# Simplified from tasks/services.py:476-510
with transaction.atomic():
    remaining = Decimal(plan_amount)
    while remaining > 0:
        credit = (
            TaskCredit.objects.select_for_update()
            .filter(
                user_id=user.id,
                expiration_date__gt=now,
                credits_used__lt=F("credits"),
                voided=False,
            )
            .order_by("expiration_date")
            .first()
        )
        
        if credit is None:
            raise ValidationError({"credits": "Insufficient task credits"})
        
        available_here = (credit.credits - credit.credits_used)
        consume_now = min(available_here, remaining)
        
        credit.credits_used = F("credits_used") + consume_now
        credit.save(update_fields=["credits_used"])
        credit.refresh_from_db()
        
        remaining -= consume_now
```

This implementation:
1. Locks credit blocks in expiration order (oldest first)
2. Consumes fractional amounts across multiple blocks if needed
3. Uses `F()` expressions for database-level atomic updates
4. Returns the last touched credit block for linking

**Sources:** [tasks/services.py:418-534](), [tests/unit/test_task_credit_service.py:96-117]()

#### Additional Tasks (Overage)

When standard credits are exhausted, the system can create "additional task" credits if the owner's plan allows:

```mermaid
graph LR
    Check["check_and_consume_credit_for_owner(owner)"]
    Try["Try consume_credit_for_owner(owner)"]
    Success["Return success=True"]
    CheckExtra{"allow_extra_tasks?"}
    CreateAdditional["consume_credit_for_owner(owner, additional_task=True)"]
    Fail["Return success=False"]
    
    Check --> Try
    Try -->|"Success"| Success
    Try -->|"ValidationError"| CheckExtra
    CheckExtra -->|"Yes"| CreateAdditional
    CheckExtra -->|"No"| Fail
    CreateAdditional -->|"Success"| Success
    CreateAdditional -->|"ValidationError"| Fail
```

Additional task credits:
- Have `additional_task=True` flag set
- Are immediately consumed (`credits_used = credits`)
- Are reported to Stripe Metering API (handled by periodic rollup task)
- Expire at the end of the current billing period

**Sources:** [tasks/services.py:753-786](), [tests/unit/test_task_credit_service.py:153-173]()

#### Per-Tool Credit Costs

The default credit cost per task is configurable via `TaskCreditConfig.default_task_cost` (singleton). Individual tools can override this via `ToolCreditCost` entries:

```python
# Simplified from util/tool_costs.py:101-121
def get_tool_credit_cost(tool_name: str | None) -> Decimal:
    default_cost, overrides = _get_tool_cost_config()
    
    key = _normalize_tool_name(tool_name)
    if key in overrides:
        return overrides[key]
    
    return default_cost
```

Configuration is cached for 5 minutes ([util/tool_costs.py:13]()). Tools like `send_email`, `send_sms`, and browser automation can have different costs than the default reasoning step.

**Sources:** [util/tool_costs.py:55-153](), [tests/unit/test_tool_costs.py:14-100]()

### Entitlement Calculation

The system distinguishes between:
- **Granted**: Credits explicitly created in `TaskCredit` records
- **Entitled**: Total credits available (granted + allowed overage)
- **Available**: Entitled - used
- **Used**: Sum of `credits_used` across all valid `TaskCredit` blocks

```python
# Simplified from tasks/services.py:537-607
def get_tasks_entitled_for_owner(owner) -> int:
    if is_organization_owner(owner):
        plan = get_organization_plan(owner)
        addl_limit = get_organization_extra_task_limit(owner)
        
        if addl_limit == TASKS_UNLIMITED:
            return TASKS_UNLIMITED
        
        tasks_granted = TaskCredit.objects.filter(
            organization=owner,
            granted_date__lte=now,
            expiration_date__gte=now,
            additional_task=False,
            voided=False,
        ).aggregate(Sum('credits'))['total_granted'] or 0
        
        return tasks_granted + addl_limit
    else:
        # Similar logic for users
        pass
```

**Sources:** [tasks/services.py:537-607](), [tests/unit/test_task_credit_service.py:206-260]()

---

## Subscription Lifecycle Management

### Stripe Webhook Processing

The `handle_subscription_event` signal ([pages/signals.py:233-651]()) processes Stripe webhooks for subscription lifecycle events:

```mermaid
graph TB
    Webhook["djstripe_receiver<br/>subscription.created/updated/deleted"]
    Validate["Validate event<br/>- Check object type<br/>- Verify Stripe enabled<br/>- Get API key"]
    Sync["Subscription.sync_from_stripe_data"]
    Owner{"Identify Owner"}
    
    UserFlow["User Flow"]
    OrgFlow["Organization Flow"]
    
    Deleted{"Event = deleted<br/>OR status = canceled?"}
    Downgrade["downgrade_owner_to_free_plan"]
    
    Active{"Status = active<br/>AND has licensed item?"}
    MarkPlan["mark_owner_billing_with_plan"]
    GrantCredits["TaskCreditService.grant_*_credits"]
    UpdateAnchor["Update billing_cycle_anchor"]
    
    Webhook --> Validate
    Validate --> Sync
    Sync --> Owner
    Owner -->|"customer.subscriber"| UserFlow
    Owner -->|"OrganizationBilling"| OrgFlow
    
    UserFlow --> Deleted
    OrgFlow --> Deleted
    
    Deleted -->|"Yes"| Downgrade
    Deleted -->|"No"| Active
    
    Active -->|"Yes"| MarkPlan
    MarkPlan --> GrantCredits
    GrantCredits --> UpdateAnchor
```

**Key Processing Steps:**

1. **Idempotency**: Invoice ID checked before granting credits ([tasks/services.py:247-255]())
2. **Owner Detection**: Checks `customer.subscriber` (user) vs `OrganizationBilling.stripe_customer_id` (org) ([pages/signals.py:295-311]())
3. **Plan Identification**: Locates licensed subscription item and matches product ID to plan config ([pages/signals.py:402-418]())
4. **Billing Anchor Sync**: Updates `billing_cycle_anchor` from Stripe's `current_period_start.day` ([pages/signals.py:438-446]())

**Sources:** [pages/signals.py:233-651](), [tests/unit/test_pages_signals.py:110-191]()

### Subscription Cancellation

When a subscription is deleted or cancelled:

1. `downgrade_owner_to_free_plan` is called ([pages/signals.py:323-356]())
2. For organizations:
   - `purchased_seats` set to 0
   - `stripe_subscription_id` cleared
   - `cancel_at` and `cancel_at_period_end` cleared
3. Existing `TaskCredit` blocks remain valid until their `expiration_date`
4. Analytics event fired for tracking

**Sources:** [pages/signals.py:316-356](), [util/subscription_helper.py]() (referenced)

---

## Organization Billing

Organizations use a seat-based model where each purchased seat grants a fixed number of credits per billing period.

### Seat Purchase Flow

```mermaid
sequenceDiagram
    participant Admin
    participant View as organization_seat_checkout
    participant Stripe
    participant Webhook
    participant Service as TaskCreditService
    
    Admin->>View: POST with seats count
    View->>View: Check membership permissions
    
    alt No existing subscription
        View->>Stripe: checkout.Session.create<br/>- Base plan price<br/>- Overage price (if configured)
        Stripe-->>View: Checkout URL
        View-->>Admin: Redirect to checkout
    else Has subscription
        View->>Stripe: Subscription.retrieve
        View->>View: Find licensed item<br/>Calculate new quantity
        View->>Stripe: billing_portal.Session.create<br/>- subscription_update_confirm flow
        Stripe-->>View: Portal URL
        View-->>Admin: Redirect to portal
    end
    
    Admin->>Stripe: Complete payment
    Stripe->>Webhook: subscription.created/updated
    Webhook->>Service: grant_subscription_credits_for_organization
```

**Implementation Details:**

The checkout view ([console/views.py](), referenced in tests) handles two scenarios:

1. **New Subscription**: Creates Stripe Checkout session with base plan SKU
2. **Existing Subscription**: Uses Billing Portal with `subscription_update_confirm` flow to add seats ([tests/unit/test_organizations.py:189-240]())

**Sources:** [tests/unit/test_organizations.py:152-240](), [console/templates/console/organization_detail.html:13-18]()

### Seat Reduction and Scheduling

Reducing seats uses Stripe Subscription Schedules to defer the change until the next billing period:

```mermaid
graph TB
    Request["Admin requests seat reduction"]
    Retrieve["Retrieve current subscription"]
    Schedule{"Has existing schedule?"}
    
    Release["SubscriptionSchedule.release"]
    Create["SubscriptionSchedule.create<br/>from_subscription"]
    
    Modify["SubscriptionSchedule.modify<br/>- Phase 0: current period (old quantity)<br/>- Phase 1: next period (new quantity)"]
    
    UpdateBilling["Update OrganizationBilling:<br/>- pending_seat_quantity<br/>- pending_seat_effective_at<br/>- pending_seat_schedule_id"]
    
    Request --> Retrieve
    Retrieve --> Schedule
    Schedule -->|"Yes"| Release
    Schedule -->|"No"| Create
    Release --> Create
    Create --> Modify
    Modify --> UpdateBilling
```

When the billing period ends and Stripe transitions to the new phase:
1. Webhook receives `subscription.updated` event
2. Detects `purchased_seats != prev_seats`
3. Clears pending seat fields ([pages/signals.py:595-606]())
4. No new credits granted (seats decreased, no prorated credit)

**Sources:** [tests/unit/test_organizations.py:569-629](), [console/views.py]() (referenced)

### Overage SKU Management

Organizations can have an optional overage SKU (metered price) for additional tasks. When seats are reduced via the Billing Portal, the platform must temporarily detach the overage SKU to avoid Stripe validation errors (portal doesn't support subscriptions with both licensed and metered items).

```mermaid
sequenceDiagram
    participant View
    participant Stripe
    
    View->>Stripe: Retrieve subscription
    View->>View: Detect overage item present<br/>AND seat reduction requested
    View->>Stripe: SubscriptionItem.delete(overage_item_id)
    View->>Stripe: Subscription.modify<br/>metadata[org_overage_sku_state] = "detached_pending"
    View->>Stripe: billing_portal.Session.create
    
    Note over View,Stripe: Portal flow happens
    
    Stripe->>Webhook: subscription.updated
    Webhook->>Webhook: Detect metadata state = "detached_pending"<br/>AND seats changed
    Webhook->>Stripe: SubscriptionItem.create(overage_price_id)
    Webhook->>Stripe: Subscription.modify<br/>metadata[org_overage_sku_state] = ""
```

This ensures the overage SKU is present during normal operations but temporarily removed for portal-based seat updates.

**Sources:** [tests/unit/test_organizations.py:325-393](), [pages/signals.py:471-575](), [constants/stripe.py:1-5]()

---

## Usage Tracking and Metering

### Credit Consumption Tracking

Every credit-consuming operation links to a `TaskCredit` record:

- `PersistentAgentStep.task_credit` ([api/migrations/0115_persistentagentstep_credits_fields.py:13-21]())
- `BrowserUseAgentTask.task_credit` (similar field)
- `PersistentAgentMessage` (consumes via service, links in step)

This enables:
1. **Usage queries**: Aggregate `credits_used` by period, tool, or agent
2. **Audit trails**: Link every operation back to its credit source
3. **Fractional costs**: Different tools can consume different credit amounts

**Sources:** [tests/unit/test_persistent_agent_step_credits.py:42-89](), [api/migrations/0115_persistentagentstep_credits_fields.py:1-34]()

### Threshold Notifications

The service tracks credit usage percentage and fires analytics events at thresholds (75%, 90%, 100%):

```python
# Simplified from tasks/services.py:1093-1177
def handle_task_threshold(user):
    entitled = get_tasks_entitled(user)
    used = get_user_total_tasks_used(user)
    
    for threshold in THRESHOLDS:  # [75, 90, 100]
        pct = (used / entitled) * 100
        
        if pct >= threshold:
            Usage = apps.get_model("api", "TaskCreditUsage")
            _, created = Usage.objects.get_or_create(
                user=user,
                threshold=threshold,
                billing_cycle_start=get_current_billing_start(user)
            )
            
            if created:
                Analytics.publish_threshold_event(user, threshold, pct, entitled, used)
```

This uses `TaskCreditUsage` as a deduplication mechanism (one notification per threshold per billing period).

**Sources:** [tasks/services.py:1093-1177](), [tests/unit/test_task_credit_service.py:361-407]()

### Stripe Metering (Overage Billing)

Additional task credits (`additional_task=True`) are metered to Stripe for overage billing. A periodic Celery task aggregates these and reports usage:

```mermaid
graph LR
    Step["Agent consumes credit<br/>additional_task=True"]
    Create["TaskCredit.objects.create<br/>additional_task=True"]
    Rollup["Periodic rollup task"]
    Aggregate["Aggregate by:<br/>- Owner<br/>- Billing period<br/>- Price ID"]
    Meter["Stripe.billing.MeterEvent.create"]
    
    Step --> Create
    Create -.->|"Async"| Rollup
    Rollup --> Aggregate
    Aggregate --> Meter
```

The rollup task:
1. Groups additional task credits by owner and billing period
2. Rounds quantities to whole tasks for Stripe metering
3. Reports via Stripe Meter Event API
4. Tracks reported events in `MeteringBatch` for idempotency

**Note**: This replaces the previous per-task metering approach to reduce API calls and improve reliability.

**Sources:** [tasks/services.py:456-473]() (additional task creation), comments indicate rollup task handles metering

---

## Configuration and Customization

### TaskCreditConfig (Singleton)

Global credit configuration is stored in a singleton `TaskCreditConfig` record:

```python
# Database model
class TaskCreditConfig(models.Model):
    singleton_id = models.IntegerField(default=1, unique=True)
    default_task_cost = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.40")
    )
```

This is cached and used as the fallback when no tool-specific cost exists.

**Sources:** [util/tool_costs.py:55-88](), [tests/unit/test_tool_costs.py:39-47]()

### ToolCreditCost (Per-Tool Overrides)

Individual tools can override the default cost:

```python
# Database model
class ToolCreditCost(models.Model):
    tool_name = models.CharField(max_length=128, unique=True)
    credit_cost = models.DecimalField(max_digits=12, decimal_places=3)
```

Tool name matching is case-insensitive. Communication channels (email/sms/web) map to specific tool names:

```python
_CHANNEL_TOOL_NAMES = {
    "email": "send_email",
    "sms": "send_sms",
    "web": "send_chat_message",
}
```

**Sources:** [util/tool_costs.py:12-153](), [tests/unit/test_tool_costs.py:24-79]()

### Community Edition Unlimited Mode

When `GOBII_PROPRIETARY_MODE=False` and `GOBII_ENABLE_COMMUNITY_UNLIMITED=True`, the system bypasses all credit checks and returns `TASKS_UNLIMITED` (-1) for all entitlement calculations:

```python
# From tasks/services.py:109-125
@staticmethod
def _is_community_unlimited() -> bool:
    try:
        if 'test_settings' in os.environ.get('DJANGO_SETTINGS_MODULE', ''):
            return False
        return (not getattr(settings, "GOBII_PROPRIETARY_MODE", False)) and bool(
            getattr(settings, "GOBII_ENABLE_COMMUNITY_UNLIMITED", False)
        )
    except Exception:
        return False
```

This mode:
- Disabled during tests
- Allows unlimited agent operations
- Prevents low-credit warnings

**Sources:** [tasks/services.py:109-155](), [util/constants/task_constants.py]() (referenced for `TASKS_UNLIMITED`)

---

## Error Handling and Edge Cases

### Negative Available Credits

If a user downgrades or their entitlement decreases, `calculate_available_tasks` clamps to zero rather than returning negative values:

```python
available = entitled - used
if available < 0:
    logger.warning(f"User {user.id} has more used ({used}) than entitled ({entitled})")
    available = 0
```

**Sources:** [tasks/services.py:151-153]()

### Concurrent Consumption Race Conditions

The `SELECT FOR UPDATE` pattern prevents double-spending:

```python
with transaction.atomic():
    credit = (
        TaskCredit.objects.select_for_update()
        .filter(...)
        .first()
    )
    # Lock held until transaction commits
```

Tests verify this works correctly under concurrent access scenarios.

**Sources:** [tasks/services.py:476-510]()

### Expired Credits

Credits are filtered by `expiration_date__gte=now` in all queries. Expired credits remain in the database but are excluded from:
- Available credit calculations
- Consumption attempts
- Entitlement totals

**Sources:** [tasks/services.py:640-663]()

### Voided Credits

The `voided` flag soft-deletes credits without removing audit history. Voided credits are excluded via `.filter(voided=False)` in all active queries.

**Sources:** [tasks/services.py:247-255]() (invoice idempotency check includes voided filter)

---

## Key Methods Reference

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `grant_subscription_credits` | user, credit_override, plan, invoice_id, grant_date, expiration_date | int | Grant credits to user based on subscription |
| `grant_subscription_credits_for_organization` | organization, seats, plan, invoice_id, grant_date, expiration_date, subscription, replace_current | int | Grant credits to organization based on seats |
| `consume_credit` | user, additional_task, amount | TaskCredit | Atomically consume credits for user |
| `consume_credit_for_owner` | owner, additional_task, amount | TaskCredit | Consume credits for user or org |
| `check_and_consume_credit_for_owner` | owner, amount | dict | Try consumption with overage fallback |
| `get_tasks_entitled_for_owner` | owner | int | Calculate total entitled credits |
| `calculate_available_tasks_for_owner` | owner, task_credits | Decimal | Calculate remaining credits |
| `get_owner_task_credits_used` | owner, task_credits | Decimal | Sum credits consumed |
| `get_tool_credit_cost` | tool_name | Decimal | Get per-tool credit cost |
| `get_default_task_credit_cost` | - | Decimal | Get default credit cost |

**Sources:** [tasks/services.py:107-1433](), [util/tool_costs.py:101-153]()

---

# Page: TaskCreditService

# TaskCreditService

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/migrations/0115_persistentagentstep_credits_fields.py](api/migrations/0115_persistentagentstep_credits_fields.py)
- [tasks/services.py](tasks/services.py)
- [tests/unit/test_persistent_agent_step_credits.py](tests/unit/test_persistent_agent_step_credits.py)
- [tests/unit/test_task_credit_service.py](tests/unit/test_task_credit_service.py)
- [tests/unit/test_tool_costs.py](tests/unit/test_tool_costs.py)
- [util/tool_costs.py](util/tool_costs.py)

</details>



## Purpose and Scope

The `TaskCreditService` is the authoritative service for all task credit operations in the gobii-platform. It provides a centralized API for granting, consuming, and calculating task credits for both individual users and organizations. This service acts as the primary resource control mechanism, gating agent execution and tool usage based on subscription plans and credit availability.

For subscription lifecycle management and Stripe webhook handling, see [Subscription Management](#5.2). For organization-specific billing operations including seat management, see [Organization Billing](#5.3). For usage analytics and reporting, see [Usage Analytics](#5.4).

**Sources:** [tasks/services.py:107-1430]()

---

## Core Concepts

### TaskCredit Model

The `TaskCredit` model represents a block of credits granted to either a User or Organization. Key attributes:

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Owner if user-owned (mutually exclusive with `organization`) |
| `organization` | ForeignKey | Owner if org-owned (mutually exclusive with `user`) |
| `credits` | Decimal | Total credits in this block |
| `credits_used` | Decimal | Credits consumed from this block |
| `granted_date` | DateTime | When credits became available |
| `expiration_date` | DateTime | When credits expire |
| `additional_task` | Boolean | `True` for overage credits, `False` for plan credits |
| `plan` | Choice | Plan type (FREE, STARTUP, PRO, etc.) |
| `grant_type` | Choice | PLAN, MANUAL, BONUS, etc. |
| `stripe_invoice_id` | String | Associated Stripe invoice for idempotency |
| `voided` | Boolean | Whether this credit block is invalidated |

### Owner Model

The service supports dual ownership through a polymorphic owner pattern:
- **User-owned credits**: Individual user subscriptions with `max_extra_tasks` limit
- **Organization-owned credits**: Multi-seat subscriptions with per-seat credit allocation

The service detects owner type via `_is_organization_owner()` which checks the model's metadata rather than using `isinstance()` to avoid circular imports.

### Credit Types

**Plan Credits**: Regular credits granted as part of subscription provisioning. Created with `additional_task=False` and `grant_type=PLAN`. These credits are the primary entitlement from the user's plan.

**Additional Task Credits**: Overage credits created when plan credits are exhausted but the plan allows extra tasks. Created with `additional_task=True` and immediately consumed (`credits_used == credits`). These are metered to Stripe for billing.

### Fractional Credits

Credits are stored and consumed as `Decimal` values, not integers. This allows tools to have fractional costs (e.g., 0.1 credits for a lightweight API call, 0.8 for browser automation). The default task cost is configurable via `TaskCreditConfig.default_task_cost`.

**Sources:** [tasks/services.py:1-61](), [util/tool_costs.py:1-153]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Entry Points"
        AgentEvent["Agent Event Processing<br/>process_agent_events_task"]
        DirectAPI["Direct API Consumption<br/>PersistentAgentStep.save()"]
    end
    
    subgraph "TaskCreditService"
        CheckConsume["check_and_consume_credit_for_owner()<br/>tasks/services.py:754"]
        ConsumeOwner["consume_credit_for_owner()<br/>tasks/services.py:690"]
        ConsumeUser["consume_credit()<br/>tasks/services.py:419"]
        
        CalcAvail["calculate_available_tasks_for_owner()<br/>tasks/services.py:183"]
        GetEntitled["get_tasks_entitled_for_owner()<br/>tasks/services.py:543"]
        GetUsed["get_owner_task_credits_used()<br/>tasks/services.py:171"]
        
        GrantSub["grant_subscription_credits()<br/>tasks/services.py:201"]
        GrantOrg["grant_subscription_credits_for_organization()<br/>tasks/services.py:309"]
    end
    
    subgraph "Database Layer"
        TaskCreditModel["TaskCredit Model<br/>SELECT FOR UPDATE<br/>Atomic Consumption"]
        TaskCreditConfig["TaskCreditConfig<br/>default_task_cost"]
        ToolCreditCost["ToolCreditCost<br/>per-tool overrides"]
    end
    
    subgraph "External Systems"
        Stripe["Stripe Metering<br/>MeteringBatch"]
        Analytics["Analytics<br/>Threshold Events"]
    end
    
    AgentEvent --> CheckConsume
    DirectAPI --> ConsumeOwner
    
    CheckConsume --> ConsumeOwner
    ConsumeOwner -->|User| ConsumeUser
    ConsumeOwner -->|Org| ConsumeOwner
    
    ConsumeUser --> TaskCreditModel
    ConsumeOwner --> TaskCreditModel
    
    CheckConsume --> CalcAvail
    CalcAvail --> GetEntitled
    CalcAvail --> GetUsed
    
    GetEntitled --> TaskCreditModel
    GetUsed --> TaskCreditModel
    
    GrantSub --> TaskCreditModel
    GrantOrg --> TaskCreditModel
    
    ConsumeUser --> TaskCreditConfig
    ConsumeUser --> ToolCreditCost
    
    ConsumeUser --> Stripe
    ConsumeUser --> Analytics
```

**Sources:** [tasks/services.py:107-1430](), Diagram 3 from high-level architecture

---

## Credit Granting

### Subscription-Based Granting for Users

The `grant_subscription_credits()` method provisions credits when a user subscribes or renews:

```mermaid
sequenceDiagram
    participant Webhook as Stripe Webhook Handler
    participant Service as TaskCreditService
    participant DB as TaskCredit Model
    
    Webhook->>Service: grant_subscription_credits(user, invoice_id)
    Service->>DB: Check if invoice_id exists
    
    alt Invoice already processed
        DB-->>Service: Existing TaskCredit found
        Service-->>Webhook: Return 0 (idempotent)
    else New invoice
        Service->>Service: Get user plan<br/>Calculate credits_to_grant
        Service->>Service: Extract current_period_end<br/>from subscription
        Service->>DB: Create TaskCredit<br/>(credits=plan credits,<br/>expiration=period_end,<br/>additional_task=False)
        DB-->>Service: TaskCredit created
        Service-->>Webhook: Return credits_to_grant
    end
```

**Key Logic:**
- **Idempotency**: Checks for existing `stripe_invoice_id` to prevent duplicate grants ([tasks/services.py:247-255]())
- **Expiration alignment**: Sets `expiration_date` to subscription's `current_period_end` ([tasks/services.py:278-287]())
- **Fallback expiration**: If no subscription, defaults to `grant_date + 30 days`
- **Plan-based allocation**: Uses `plan["monthly_task_credits"]` for credit amount ([tasks/services.py:266]())

**Sources:** [tasks/services.py:201-306](), [tests/unit/test_task_credit_service.py:50-89]()

### Subscription-Based Granting for Organizations

Organizations receive credits based on purchased seats via `grant_subscription_credits_for_organization()`:

**Calculation Formula:**
```
credits_to_grant = plan.credits_per_seat × organization.billing.purchased_seats
```

**Replace Current Cycle Mode:**

When `replace_current=True` (used during billing cycle renewal), the service updates an existing PLAN credit block instead of creating a new one. This prevents double-counting entitlements:

1. Finds the most recent non-voided PLAN credit for the organization
2. Updates its `credits`, `credits_used` (reset to 0), `granted_date`, `expiration_date`, and `stripe_invoice_id`
3. Returns without creating a duplicate block

This ensures organizations have exactly one active PLAN credit block per billing cycle.

**Sources:** [tasks/services.py:309-416](), [tests/unit/test_task_credit_service.py:328-359]()

---

## Credit Consumption

### Atomic Consumption with SELECT FOR UPDATE

Credit consumption uses database-level locking to prevent race conditions when multiple workers attempt to consume credits simultaneously:

```mermaid
sequenceDiagram
    participant Agent as Agent Execution
    participant Service as TaskCreditService
    participant TX as Database Transaction
    participant Credit as TaskCredit Row
    
    Agent->>Service: consume_credit(user, amount=0.4)
    Service->>TX: BEGIN TRANSACTION
    
    loop While remaining > 0
        TX->>Credit: SELECT FOR UPDATE<br/>WHERE user_id=X<br/>AND credits_used < credits<br/>ORDER BY expiration_date
        Credit-->>TX: Locked row
        
        TX->>TX: available = credits - credits_used
        TX->>TX: consume_now = min(available, remaining)
        
        TX->>Credit: UPDATE credits_used<br/>= F('credits_used') + consume_now
        Credit-->>TX: Row updated
        
        TX->>Credit: REFRESH FROM DB
        Credit-->>TX: Refreshed values
        
        TX->>TX: remaining -= consume_now
    end
    
    TX->>TX: COMMIT
    TX-->>Service: Success
    Service-->>Agent: Return TaskCredit
```

**Critical Implementation Details:**

1. **Row-level locking**: `select_for_update()` prevents concurrent consumption of the same credit block ([tasks/services.py:481-491]())

2. **F-expressions**: Uses `F('credits_used')` to ensure the database performs atomic increment, avoiding lost updates ([tasks/services.py:505-507]())

3. **Refresh after save**: Calls `refresh_from_db()` to get the actual updated value after the F-expression update ([tasks/services.py:508]())

4. **Multi-block consumption**: Loops across multiple credit blocks if a single block has insufficient credits ([tasks/services.py:478-510]())

5. **Expiration ordering**: Consumes from blocks closest to expiration first to minimize waste ([tasks/services.py:489]())

**Sources:** [tasks/services.py:419-534](), [tasks/services.py:690-751]()

### Fractional Consumption

The service supports sub-unit credit consumption for cost-effective tool execution:

```python
# Example: Lightweight tool costs 0.1 credits
consume_credit(user, amount=Decimal("0.1"))

# Heavier tool costs 0.8 credits  
consume_credit(user, amount=Decimal("0.8"))
```

Credit blocks can be partially consumed across multiple operations. For instance, a 1.0 credit block can service ten 0.1-credit operations.

**Default Cost Retrieval:**

When `amount` is not specified, the service fetches the default from `get_default_task_credit_cost()` which queries `TaskCreditConfig.default_task_cost` with a 5-minute cache ([util/tool_costs.py:101-103]()).

**Sources:** [tasks/services.py:453](), [util/tool_costs.py:55-103](), [tests/unit/test_persistent_agent_step_credits.py:58-78]()

### Additional Tasks (Overage Credits)

When plan credits are exhausted but the user/organization plan allows additional tasks, the service creates on-demand overage credits:

**User Additional Tasks:**

```mermaid
graph LR
    A["consume_credit(user,<br/>additional_task=True)"] --> B["Get current<br/>billing period"]
    B --> C["Create TaskCredit<br/>credits=amount<br/>credits_used=amount"]
    C --> D["Set expiration<br/>to period end"]
    D --> E["Mark<br/>additional_task=True"]
    E --> F["Return credit"]
```

**Characteristics:**
- Immediately consumed: `credits == credits_used` ([tasks/services.py:466]())
- Expires at billing period end ([tasks/services.py:461-467]())
- Metered to Stripe via periodic rollup task (not per-task reporting as of current implementation)
- Counts against `max_extra_tasks` limit

**Organization Additional Tasks:**

Similar flow but uses `get_current_billing_period_for_owner()` and creates credit with `organization_id` instead of `user_id` ([tasks/services.py:701-714]()).

**Sources:** [tasks/services.py:456-473](), [tasks/services.py:701-714](), [tests/unit/test_task_credit_service.py:119-142]()

### Check-and-Consume Pattern

The `check_and_consume_credit_for_owner()` method implements a two-tier fallback strategy:

1. **Attempt plan credit consumption**: Try to consume from regular credit blocks
2. **If insufficient, try additional task**: If allowed by plan, create an overage credit
3. **Return result dict**: Contains `success`, `credit`, and `error_message`

This pattern is used throughout agent event processing to gracefully handle credit exhaustion without raising exceptions in the main execution path.

**Sources:** [tasks/services.py:754-786](), [tests/unit/test_task_credit_service.py:145-203]()

---

## Owner-Aware Operations

### Dual Ownership Detection

The service uses model metadata inspection to distinguish between User and Organization owners:

```python
@staticmethod
def _is_organization_owner(owner) -> bool:
    meta = getattr(owner, "_meta", None)
    return bool(meta and meta.app_label == "api" and meta.model_name == "organization")
```

This approach avoids circular imports that would occur with `isinstance(owner, Organization)` checks.

**Sources:** [tasks/services.py:666-669]()

### Owner-Polymorphic Methods

The service provides parallel method sets for user-specific and owner-agnostic operations:

| User-Specific Method | Owner-Aware Method | Purpose |
|---------------------|-------------------|---------|
| `calculate_available_tasks()` | `calculate_available_tasks_for_owner()` | Remaining credits |
| `get_user_task_credits_granted()` | `get_owner_task_credits_granted()` | Total granted |
| `get_user_task_credits_used()` | `get_owner_task_credits_used()` | Total consumed |
| `consume_credit()` | `consume_credit_for_owner()` | Consume credits |
| `get_tasks_entitled()` | `get_tasks_entitled_for_owner()` | Calculate entitlement |

**Internal Routing Logic:**

```mermaid
graph TB
    Call["Caller invokes<br/>owner-aware method"] --> Check{"_is_organization_owner()?"}
    Check -->|True| OrgPath["Execute organization<br/>logic variant"]
    Check -->|False| UserPath["Delegate to user-specific<br/>method"]
    
    OrgPath --> OrgDB["Query TaskCredit.objects.filter(<br/>organization=owner)"]
    UserPath --> UserDB["Query TaskCredit.objects.filter(<br/>user=owner)"]
```

**Sources:** [tasks/services.py:157-198](), [tasks/services.py:665-787]()

### Organization-Specific Differences

**Credit Entitlement Calculation:**

Organizations require `purchased_seats > 0` to have any entitlement. The formula is:
```
entitled = (plan.credits_per_seat × purchased_seats) + max_extra_tasks
```

If `purchased_seats == 0`, the organization receives 0 entitlement regardless of plan ([tasks/services.py:580-607]()).

**Additional Task Restrictions:**

Organizations can only create additional task credits if:
1. `allow_organization_extra_tasks(org)` returns `True` (checks subscription status)
2. `allow_and_has_extra_tasks_for_organization(org)` returns `True` (checks quota availability)

**Sources:** [tasks/services.py:580-607](), [tasks/services.py:754-786]()

---

## Credit Calculations

### Available Tasks Calculation

```mermaid
graph LR
    A["calculate_available_tasks_for_owner()"] --> B{"Community<br/>unlimited?"}
    B -->|Yes| C["Return<br/>TASKS_UNLIMITED"]
    B -->|No| D["Get entitled"]
    D --> E{"entitled ==<br/>TASKS_UNLIMITED?"}
    E -->|Yes| C
    E -->|No| F["Get used"]
    F --> G["Return<br/>max(entitled - used, 0)"]
```

**Entitlement Calculation:**

For **users** ([tasks/services.py:554-578]()):
```
tasks_granted = SUM(TaskCredit.credits WHERE user=X AND in_range AND NOT additional_task)
if tasks_granted == 0:
    tasks_granted = plan.monthly_task_credits
extra_tasks = get_user_extra_task_limit(user)
entitled = tasks_granted + extra_tasks
```

For **organizations** ([tasks/services.py:580-607]()):
```
if purchased_seats == 0:
    return 0
tasks_granted = SUM(TaskCredit.credits WHERE organization=X AND in_range AND NOT additional_task)
if tasks_granted == 0:
    tasks_granted = get_organization_task_credit_limit(org)
extra_tasks = get_organization_extra_task_limit(org)
entitled = tasks_granted + extra_tasks
```

**Usage Calculation:**

Sums `credits_used` across all current TaskCredit blocks (both plan and additional task credits):
```sql
SELECT SUM(credits_used) 
FROM task_credit 
WHERE (user_id=X OR organization_id=X)
  AND granted_date <= NOW()
  AND expiration_date >= NOW()
  AND NOT voided
```

**Sources:** [tasks/services.py:128-155](), [tasks/services.py:183-198](), [tasks/services.py:537-607]()

### Percentage Used Calculation

The `calculate_used_pct()` method calculates usage as a percentage with special handling:

```python
def calculate_used_pct(user: User):
    total_credits = get_tasks_entitled(user)
    if total_credits == 0:
        return 0.0
    used_credits = get_user_total_tasks_used(user)
    pct = (used_credits / total_credits) * 100
    if pct > 100:
        pct = 100.0
    return pct
```

This is used by the threshold notification system to determine when to alert users.

**Sources:** [tasks/services.py:611-636]()

---

## Tool Credit Costs

### Configurable Cost System

The platform supports per-tool credit cost overrides via the `ToolCreditCost` model:

```mermaid
graph TB
    Request["get_tool_credit_cost('search_web')"] --> Cache{"Cache hit?"}
    Cache -->|Yes| Return["Return cached value"]
    Cache -->|No| Fetch["_fetch_tool_cost_configuration()"]
    
    Fetch --> DB1["Query TaskCreditConfig<br/>for default_task_cost"]
    Fetch --> DB2["Query ToolCreditCost.objects.all()<br/>for per-tool overrides"]
    
    DB1 --> Build["Build cost map:<br/>default + overrides dict"]
    DB2 --> Build
    
    Build --> CacheStore["cache.set(data, ttl=300)"]
    CacheStore --> Lookup["Lookup tool in overrides"]
    
    Lookup -->|Found| Return
    Lookup -->|Not found| Default["Return default_task_cost"]
    Default --> Return
```

**Default Cost Configuration:**

Stored in `TaskCreditConfig.default_task_cost` (singleton row with `singleton_id=1`). Falls back to `settings.CREDITS_PER_TASK` if the table doesn't exist (during migrations).

**Per-Tool Overrides:**

Stored in `ToolCreditCost` table with columns:
- `tool_name` (String): Case-insensitive tool identifier
- `credit_cost` (Decimal): Override cost for this tool

**Lookup Logic:**

1. Normalize tool name to lowercase with `.strip().lower()`
2. Check overrides dictionary
3. If found, return override cost
4. Otherwise, return default cost

**Sources:** [util/tool_costs.py:55-122](), [tests/unit/test_tool_costs.py:14-79]()

### Channel-Based Cost Lookup

Communication channels have implicit tool name mappings:

| Channel | Tool Name |
|---------|-----------|
| `email` | `send_email` |
| `sms` | `send_sms` |
| `web` | `send_chat_message` |

The `get_tool_credit_cost_for_channel()` function maps channel enums to tool names and performs the cost lookup:

```python
_CHANNEL_TOOL_NAMES = {
    "email": "send_email",
    "sms": "send_sms", 
    "web": "send_chat_message",
}

def get_tool_credit_cost_for_channel(channel: str) -> Decimal:
    normalized = channel.strip().lower()
    tool_name = _CHANNEL_TOOL_NAMES.get(normalized)
    return get_tool_credit_cost(tool_name)
```

This is used when agents send messages to consume credits based on the communication medium.

**Sources:** [util/tool_costs.py:141-153](), [tests/unit/test_tool_costs.py:58-78]()

### Most Expensive Tool Cost

The `get_most_expensive_tool_cost()` function returns the maximum configured cost across all tools (including the default). This is used for pre-flight credit checks when the exact tool is unknown:

```python
max_cost = default_cost
for value in overrides.values():
    if value > max_cost:
        max_cost = value
return max_cost
```

This ensures that credit gate checks are conservative and don't falsely allow execution when only an expensive tool would be used.

**Sources:** [util/tool_costs.py:124-138](), [tests/unit/test_tool_costs.py:80-99]()

---

## Threshold Notifications

The `handle_task_threshold()` method monitors credit usage and publishes analytics events when users cross 75%, 90%, or 100% usage thresholds:

```mermaid
graph TB
    Entry["handle_task_threshold(user)"] --> CalcPct["Calculate usage %"]
    CalcPct --> GetPeriod["Get current billing period"]
    GetPeriod --> LoopStart["For threshold in [75, 90, 100]"]
    
    LoopStart --> Check{"usage >= threshold?"}
    Check -->|No| Next["Continue to next threshold"]
    Check -->|Yes| CheckUsage["ThresholdUsage.objects<br/>.get_or_create(user, month, threshold)"]
    
    CheckUsage --> AlreadySent{"created == False?"}
    AlreadySent -->|Yes| Next
    AlreadySent -->|No| Publish["Analytics.publish_threshold_event(<br/>user, threshold, pct, month)"]
    
    Publish --> Next
    Next --> LoopStart
```

**Threshold Logic:**

1. Calculates percentage used via `calculate_used_pct(user)`
2. Treats usage within 0.05 credits of entitled as 100% to handle floating-point imprecision
3. For each threshold (75, 90, 100), checks if usage >= threshold
4. Uses `get_or_create()` to ensure notification is sent only once per month per threshold
5. Publishes event to Analytics if this is the first time crossing this threshold

**De-duplication:**

The `ThresholdUsage` model has a unique constraint on `(user, month, threshold)`, preventing duplicate notifications. The `month` is derived from the billing cycle anchor, not the calendar month.

**Sources:** [tasks/services.py:1237-1318](), [tests/unit/test_task_credit_service.py:361-408]()

---

## Community Edition Mode

### Unlimited Credits Flag

When running in Community Edition mode with unlimited credits enabled, all credit checks return `TASKS_UNLIMITED`:

```python
@staticmethod
def _is_community_unlimited() -> bool:
    """Return True when running Community Edition with unlimited credits enabled."""
    try:
        # Never enable unlimited mode during test runs
        if 'test_settings' in os.environ.get('DJANGO_SETTINGS_MODULE', ''):
            return False
        return (not getattr(settings, "GOBII_PROPRIETARY_MODE", False)) and bool(
            getattr(settings, "GOBII_ENABLE_COMMUNITY_UNLIMITED", False)
        )
    except Exception:
        return False
```

**Settings Required:**
- `GOBII_PROPRIETARY_MODE = False` (default)
- `GOBII_ENABLE_COMMUNITY_UNLIMITED = True` (default in `config/settings.py`)

**Impact:**

When this mode is active:
- `calculate_available_tasks()` returns `TASKS_UNLIMITED` immediately ([tasks/services.py:136-137]())
- `calculate_available_tasks_for_owner()` returns `TASKS_UNLIMITED` immediately ([tasks/services.py:186-187]())
- `get_user_task_credits_available()` returns `TASKS_UNLIMITED` immediately ([tasks/services.py:807-808]())

This allows self-hosted deployments to run without credit restrictions while maintaining the credit infrastructure for proprietary cloud deployments.

**Test Exclusion:**

The function explicitly checks for test settings modules and returns `False` to ensure tests run with realistic credit limits and don't inadvertently pass due to unlimited mode.

**Sources:** [tasks/services.py:109-125](), [tasks/services.py:136-137](), [tasks/services.py:186-187]()

---

## Integration Points

### Agent Event Processing

The agent event processing pipeline calls `check_and_consume_credit_for_owner()` before starting the LLM reasoning loop:

```mermaid
graph LR
    A["process_agent_events_task"] --> B["Acquire Redlock"]
    B --> C["check_and_consume_credit_for_owner(owner)"]
    C --> D{"success?"}
    D -->|False| E["Create SystemStep:<br/>credit_insufficient"]
    D -->|True| F["Proceed to<br/>_run_agent_loop"]
```

This prevents agent execution when credits are exhausted, creating a system step with type `credit_insufficient` for observability.

**Sources:** High-level Diagram 2 (Agent Lifecycle), [tasks/services.py:754-786]()

### PersistentAgentStep Credit Linking

When a `PersistentAgentStep` is created, its `save()` method automatically consumes credits and links to the consumed `TaskCredit` block:

```python
# In PersistentAgentStep.save()
if not self.pk:  # New step
    owner = self.agent.organization or self.agent.user
    cost = self.credits_cost or get_default_task_credit_cost()
    credit = TaskCreditService.consume_credit_for_owner(owner, amount=cost)
    self.task_credit = credit
    self.credits_cost = cost
```

This creates an audit trail linking each agent step to its consumed credit, enabling detailed usage analysis.

**Sources:** [tests/unit/test_persistent_agent_step_credits.py:42-89](), [api/migrations/0115_persistentagentstep_credits_fields.py:1-34]()

### Stripe Metering Integration

While the service creates `MeteringBatch` records when additional task credits are consumed, the actual reporting to Stripe is handled by a periodic rollup task (not per-task immediate reporting). This batching approach reduces API calls and costs.

The metering logic uses the billing cycle anchor to aggregate usage into monthly buckets for accurate overage billing.

**Sources:** [tasks/services.py:456-473](), Diagram 3 from high-level architecture

---

## Database Schema Relationships

```mermaid
erDiagram
    User ||--o{ TaskCredit : "owns"
    Organization ||--o{ TaskCredit : "owns"
    TaskCredit ||--o{ PersistentAgentStep : "consumed_by"
    TaskCredit ||--o{ BrowserUseAgentTask : "consumed_by"
    
    TaskCreditConfig ||--|| Singleton : "is"
    ToolCreditCost }o--|| TaskCreditConfig : "references"
    
    TaskCredit {
        int id PK
        int user_id FK
        int organization_id FK
        decimal credits
        decimal credits_used
        datetime granted_date
        datetime expiration_date
        boolean additional_task
        string plan
        string grant_type
        string stripe_invoice_id
        boolean voided
    }
    
    TaskCreditConfig {
        int singleton_id PK
        decimal default_task_cost
    }
    
    ToolCreditCost {
        int id PK
        string tool_name
        decimal credit_cost
    }
    
    PersistentAgentStep {
        int id PK
        int task_credit_id FK
        decimal credits_cost
    }
```

**Sources:** [tasks/services.py:1-1430](), [util/tool_costs.py:1-153](), [api/migrations/0115_persistentagentstep_credits_fields.py:1-34]()

---

# Page: Subscription Management

# Subscription Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [console/forms.py](console/forms.py)
- [console/templates/console/organization_detail.html](console/templates/console/organization_detail.html)
- [console/templates/partials/_org_invite_modal.html](console/templates/partials/_org_invite_modal.html)
- [constants/stripe.py](constants/stripe.py)
- [pages/signals.py](pages/signals.py)
- [tests/unit/test_organizations.py](tests/unit/test_organizations.py)
- [tests/unit/test_pages_signals.py](tests/unit/test_pages_signals.py)

</details>



## Purpose and Scope

This page documents the subscription lifecycle management system that processes Stripe webhook events to provision credits, manage billing cycles, and handle seat-based organization subscriptions. The system bridges Stripe's subscription state with the platform's credit allocation and billing models.

For credit consumption mechanics, see [TaskCreditService](#5.1). For organization-specific seat purchasing and reduction flows, see [Organization Billing](#5.3). For usage tracking and reporting, see [Usage Analytics](#5.4).

**Sources:** [pages/signals.py:1-651]()

---

## System Overview

The subscription management system is webhook-driven, responding to Stripe events (`customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`) to synchronize subscription state and provision credits. It handles both individual user subscriptions and organization seat-based subscriptions with different provisioning logic.

### High-Level Flow

```mermaid
graph TB
    Stripe["Stripe<br/>(Subscription Events)"]
    Webhook["@djstripe_receiver<br/>handle_subscription_event"]
    Sync["Subscription.sync_from_stripe_data"]
    OwnerResolution["Owner Resolution"]
    UserPath["User Subscription Path"]
    OrgPath["Organization Subscription Path"]
    CreditGrant["Credit Provisioning"]
    BillingUpdate["Billing Record Update"]
    
    Stripe -->|"customer.subscription.*"| Webhook
    Webhook --> Sync
    Sync --> OwnerResolution
    OwnerResolution -->|"customer.subscriber exists"| UserPath
    OwnerResolution -->|"OrganizationBilling.stripe_customer_id"| OrgPath
    
    UserPath --> CreditGrant
    OrgPath --> CreditGrant
    CreditGrant --> BillingUpdate
    
    BillingUpdate -->|"User"| UserBilling["UserBilling<br/>- subscription<br/>- billing_cycle_anchor"]
    BillingUpdate -->|"Organization"| OrgBilling["OrganizationBilling<br/>- purchased_seats<br/>- billing_cycle_anchor<br/>- stripe_subscription_id"]
```

**Sources:** [pages/signals.py:233-651]()

---

## Webhook Event Handler

The `handle_subscription_event` function is the central webhook handler decorated with `@djstripe_receiver` for subscription events. It performs defensive validation, owner resolution, and delegates to appropriate processing paths.

### Event Processing Pipeline

```mermaid
graph TD
    Start["Webhook Received"]
    ValidateObject{"object == 'subscription'?"}
    CheckStripe{"Stripe Enabled?"}
    SyncSub["Subscription.sync_from_stripe_data"]
    SyncFallback["Retry with expand=['items']"]
    GetCustomer["Get Customer from Subscription"]
    ResolveOwner["Resolve Owner:<br/>User or Organization"]
    
    Start --> ValidateObject
    ValidateObject -->|No| IgnoreNonSub["Log & Return"]
    ValidateObject -->|Yes| CheckStripe
    CheckStripe -->|No| IgnoreDisabled["Log & Return"]
    CheckStripe -->|Yes| SyncSub
    
    SyncSub -->|Success| GetCustomer
    SyncSub -->|"auto_paging_iter error"| SyncFallback
    SyncFallback --> GetCustomer
    
    GetCustomer -->|"customer exists"| ResolveOwner
    GetCustomer -->|"customer is None"| IgnoreNoCustomer["Log & Return"]
    
    ResolveOwner -->|"customer.subscriber"| UserOwner["owner_type = 'user'"]
    ResolveOwner -->|"OrganizationBilling match"| OrgOwner["owner_type = 'organization'"]
    ResolveOwner -->|"No match"| IgnoreNoOwner["Log & Return"]
    
    UserOwner --> HandleEvent["Handle Event Type"]
    OrgOwner --> HandleEvent
```

**Sources:** [pages/signals.py:233-311]()

### Subscription Sync with Fallback

The handler attempts to sync subscription data using `Subscription.sync_from_stripe_data()`. If an `auto_paging_iter` error occurs (common with certain Stripe SDK versions), it falls back to retrieving the subscription with expanded items:

```python
try:
    sub = Subscription.sync_from_stripe_data(payload)
except Exception as exc:
    if "auto_paging_iter" in str(exc):
        stripe_sub = stripe.Subscription.retrieve(
            payload["id"],
            expand=["items"],
        )
        sub = Subscription.sync_from_stripe_data(stripe_sub)
    else:
        raise
```

**Sources:** [pages/signals.py:264-280]()

---

## Owner Resolution

Subscriptions can be owned by either individual users or organizations. The system determines ownership through two mechanisms:

| Owner Type | Resolution Method | Identifier Field |
|------------|-------------------|------------------|
| **User** | `customer.subscriber` (dj-stripe model) | Direct foreign key |
| **Organization** | `OrganizationBilling.stripe_customer_id` | Stripe customer ID match |

```mermaid
graph LR
    Customer["Stripe Customer"]
    CheckSubscriber{"customer.subscriber<br/>exists?"}
    UserPath["User Owner"]
    QueryOrgBilling["OrganizationBilling.objects<br/>.filter(stripe_customer_id)"]
    OrgPath["Organization Owner"]
    NoOwner["No Owner - Return"]
    
    Customer --> CheckSubscriber
    CheckSubscriber -->|Yes| UserPath
    CheckSubscriber -->|No| QueryOrgBilling
    QueryOrgBilling -->|Found| OrgPath
    QueryOrgBilling -->|Not Found| NoOwner
```

**Sources:** [pages/signals.py:291-311]()

---

## Subscription Lifecycle Events

The handler processes three event types with different behaviors:

### Deletion Events (`customer.subscription.deleted`)

When a subscription is deleted or canceled, the owner is immediately downgraded to the free plan:

```mermaid
graph TD
    DeleteEvent["Event Type:<br/>customer.subscription.deleted"]
    CheckCanceled{"sub.status == 'canceled'?"}
    Downgrade["downgrade_owner_to_free_plan(owner)"]
    UserCleanup["For Users:<br/>Analytics.track_event<br/>(SUBSCRIPTION_CANCELLED)"]
    OrgCleanup["For Orgs:<br/>- purchased_seats = 0<br/>- stripe_subscription_id = None<br/>- cancel_at = None<br/>- cancel_at_period_end = False"]
    
    DeleteEvent --> CheckCanceled
    CheckCanceled -->|Yes| Downgrade
    Downgrade -->|"owner_type == 'user'"| UserCleanup
    Downgrade -->|"owner_type == 'organization'"| OrgCleanup
```

**Sources:** [pages/signals.py:316-356]()

### Active Subscriptions (`status == 'active'`)

For active subscriptions, the handler extracts the licensed subscription item, retrieves the plan configuration, and provisions credits:

```mermaid
graph TD
    ActiveSub["Active Subscription"]
    FindLicensed["Find Licensed Item:<br/>usage_type == 'licensed'"]
    GetPlan["get_plan_by_product_id(product)"]
    CheckOwner{"Owner Type?"}
    UserGrant["mark_user_billing_with_plan<br/>TaskCreditService.grant_subscription_credits"]
    OrgGrant["mark_owner_billing_with_plan<br/>TaskCreditService.grant_subscription_credits_for_organization"]
    UpdateAnchor["Update billing_cycle_anchor<br/>from current_period_start.day"]
    
    ActiveSub --> FindLicensed
    FindLicensed -->|"Found"| GetPlan
    FindLicensed -->|"Not Found"| WarnReturn["Log Warning & Return"]
    GetPlan --> CheckOwner
    CheckOwner -->|User| UserGrant
    CheckOwner -->|Organization| OrgGrant
    UserGrant --> UpdateAnchor
    OrgGrant --> UpdateAnchor
```

**Sources:** [pages/signals.py:410-446](), [pages/signals.py:577-650]()

---

## User Subscription Handling

For individual users, subscription processing is straightforward:

1. **Plan Assignment**: `mark_user_billing_with_plan(owner, plan_value, update_anchor=False)`
2. **Credit Grant**: `TaskCreditService.grant_subscription_credits(owner, plan, invoice_id)`
3. **Anchor Alignment**: Extract `current_period_start.day` and update `UserBilling.billing_cycle_anchor`
4. **Analytics**: `Analytics.identify()` with plan, `Analytics.track_event()` with subscription created event

### Billing Cycle Anchor Alignment

The billing cycle anchor is extracted from Stripe's `current_period_start` and stored as the day of month:

```python
current_period_start_dt = _coerce_datetime(_get_stripe_data_value(source_data, "current_period_start"))
if current_period_start_dt:
    new_day = current_period_start_dt.day
    if ub.billing_cycle_anchor != new_day:
        ub.billing_cycle_anchor = new_day
        ub.save(update_fields=["billing_cycle_anchor"])
```

This ensures credit grants align with Stripe's billing periods.

**Sources:** [pages/signals.py:428-446]()

---

## Organization Subscription Handling

Organization subscriptions are more complex due to seat-based billing and overage SKU management. The handler processes seat quantity changes and provisions credits proportionally.

### Seat Quantity Extraction

The licensed item's `quantity` field represents purchased seats:

```python
seats = 0
try:
    seats = int(licensed_item.get("quantity") or 0)
except (TypeError, ValueError):
    seats = 0

prev_seats = getattr(organization_billing, "purchased_seats", 0)
```

**Sources:** [pages/signals.py:462-470]()

### Credit Granting Logic by Billing Reason

The system uses `billing_reason` to determine whether and how many credits to grant:

| Billing Reason | Condition | Seats to Grant | Invoice ID | Replace Current |
|----------------|-----------|----------------|------------|-----------------|
| `subscription_create` | `prev_seats == 0` | `seats` (full) | `invoice_id` | `True` |
| `subscription_create` | `prev_seats > 0` | `max(seats - prev_seats, 0)` | Empty | `False` |
| `subscription_cycle` | Always | `seats` (full) | `invoice_id` | `True` |
| `subscription_update` | `seats > prev_seats` | `seats - prev_seats` | Empty | `False` |
| `subscription_update` | `seats <= prev_seats` | 0 (no grant) | Empty | `False` |

The `replace_current` flag indicates whether to reset the current credit block (for cycle renewals) or add incremental credits (for mid-cycle upgrades).

**Sources:** [pages/signals.py:621-650](), [tests/unit/test_pages_signals.py:236-403]()

### Billing Record Updates

The handler updates multiple fields on `OrganizationBilling`:

```mermaid
graph TD
    UpdateSeats["purchased_seats = seats"]
    UpdateAnchor["billing_cycle_anchor = current_period_start.day"]
    UpdateSubId["stripe_subscription_id = sub.id"]
    ClearPending["Clear pending_seat_* fields<br/>if seats changed"]
    UpdateCancel["cancel_at = cancel_at_dt<br/>cancel_at_period_end = flag"]
    
    UpdateSeats --> UpdateAnchor
    UpdateAnchor --> UpdateSubId
    UpdateSubId --> ClearPending
    ClearPending --> UpdateCancel
```

Pending seat changes (from Subscription Schedules) are cleared when the seat quantity changes, as the schedule has been applied or replaced.

**Sources:** [pages/signals.py:577-619]()

---

## Overage SKU Management

Organizations use a metered overage SKU (`org_team_additional_task_price_id`) for additional task charges beyond seat-based credits. The webhook handler ensures this item is attached to subscriptions and manages its lifecycle during seat changes.

### Overage Item Attachment

When processing an active subscription without the overage item, the handler attaches it:

```mermaid
graph TD
    CheckOverage{"Overage Price ID<br/>Configured?"}
    CheckPresent{"Overage Item<br/>Present?"}
    CheckMetadata{"Metadata:<br/>org_overage_sku_state == 'detached_pending'?"}
    CheckSeatDelta{"seat_delta == 0?"}
    ReattachItem["stripe.SubscriptionItem.create<br/>(price=overage_price_id)"]
    ClearFlag["stripe.Subscription.modify<br/>(metadata={'org_overage_sku_state': ''})"]
    SkipReattach["Skip Reattachment"]
    
    CheckOverage -->|Yes| CheckPresent
    CheckOverage -->|No| SkipReattach
    CheckPresent -->|No| CheckMetadata
    CheckPresent -->|Yes| AlreadyPresent["Already Present"]
    CheckMetadata -->|Yes| CheckSeatDelta
    CheckMetadata -->|No| ReattachItem
    CheckSeatDelta -->|Yes| SkipReattach
    CheckSeatDelta -->|No| ReattachItem
    ReattachItem --> ClearFlag
    AlreadyPresent --> ClearFlag
```

The `org_overage_sku_state: detached_pending` metadata flag is set during seat reduction flows (via Billing Portal) to temporarily suppress overage item reattachment until the user confirms the change.

**Sources:** [pages/signals.py:472-575]()

### Detached Pending State

The `ORG_OVERAGE_STATE_DETACHED_PENDING` constant marks subscriptions where the overage item has been temporarily removed during a seat update via Stripe Billing Portal:

```python
overage_state = metadata.get(ORG_OVERAGE_STATE_META_KEY, "")
seat_delta = seats - prev_seats

should_reattach = not has_overage_item and (
    overage_state != ORG_OVERAGE_STATE_DETACHED_PENDING or seat_delta != 0
)
```

If the subscription has this flag AND the seat count hasn't changed (delta == 0), reattachment is skipped. Otherwise, the item is reattached and the flag cleared.

**Sources:** [pages/signals.py:488-563](), [constants/stripe.py:1-5]()

---

## Billing Reason Extraction

The `billing_reason` field is critical for determining credit grant logic but isn't always present in the subscription payload. The handler uses a multi-level extraction strategy:

```mermaid
graph TD
    CheckPayload{"billing_reason in<br/>subscription payload?"}
    CheckInvoice{"latest_invoice<br/>present?"}
    RetrieveInvoice["stripe.Invoice.retrieve(invoice_id)"]
    ExtractReason["billing_reason from Invoice"]
    UseFallback["Use subscription.billing_reason<br/>or None"]
    
    CheckPayload -->|Yes| UsePayload["Use Payload Value"]
    CheckPayload -->|No| CheckInvoice
    CheckInvoice -->|Yes| RetrieveInvoice
    CheckInvoice -->|No| UseFallback
    RetrieveInvoice --> ExtractReason
```

The handler retrieves the invoice to extract `billing_reason` when it's missing from the subscription object:

```python
invoice_id = _get_stripe_data_value(source_data, "latest_invoice")
if invoice_id and not billing_reason:
    try:
        invoice_data = stripe.Invoice.retrieve(invoice_id)
        invoice = Invoice.sync_from_stripe_data(invoice_data)
        billing_reason = getattr(invoice, "billing_reason", None)
    except Exception as exc:
        logger.warning("Failed to fetch invoice %s: %s", invoice_id, exc)
```

**Sources:** [pages/signals.py:377-398]()

---

## Helper Functions for Data Extraction

The webhook handler uses helper functions to safely extract and coerce data from Stripe payloads:

### `_get_stripe_data_value(container, key)`

Fetches a key from either dict-like or object-like containers:

```python
if isinstance(container, Mapping):
    return container.get(key)
try:
    return getattr(container, key)
except AttributeError:
    return None
```

**Sources:** [pages/signals.py:51-60]()

### `_coerce_datetime(value)`

Normalizes timestamps (integers, strings, or datetime objects) to timezone-aware datetime objects:

```python
if isinstance(value, Number):
    candidate = datetime.fromtimestamp(float(value), tz=dt_timezone.utc)
elif isinstance(value, str):
    parsed = parse_datetime(value.strip())
    # ... fallback to timestamp parsing
```

Ensures all datetimes are timezone-aware using Django's timezone utilities.

**Sources:** [pages/signals.py:63-93]()

### `_coerce_bool(value)`

Converts Stripe boolean-ish values (strings, numbers) to strict booleans:

```python
if isinstance(value, str):
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
```

**Sources:** [pages/signals.py:96-111]()

---

## Integration with Credit System

The subscription handler delegates credit provisioning to `TaskCreditService`:

### User Credit Grant

```python
TaskCreditService.grant_subscription_credits(
    owner,
    plan=plan,
    invoice_id=invoice_id or ""
)
```

Creates a `TaskCredit` record with:
- `credits` = `plan["monthly_task_credits"]`
- `expiration_date` = subscription current period end
- `invoice_id` for Stripe reconciliation

**Sources:** [pages/signals.py:430-434]()

### Organization Credit Grant

```python
TaskCreditService.grant_subscription_credits_for_organization(
    owner,
    seats=seats_to_grant,
    plan=plan,
    invoice_id=grant_invoice_id,
    subscription=sub,
    replace_current=replace_current,
)
```

Creates credits based on `seats × plan["credits_per_seat"]`. The `replace_current` flag controls whether to reset the active credit block (for cycle renewals) or add incremental credits.

**Sources:** [pages/signals.py:643-650]()

---

## Observability and Tracing

The handler is instrumented with OpenTelemetry spans for monitoring:

```python
with tracer.start_as_current_span("handle_subscription_event") as span:
    span.set_attribute('subscription.customer.id', customer.id)
    span.set_attribute('subscription.owner.type', owner_type)
    span.set_attribute('subscription.event_type', event_type)
    span.add_event('org_subscription_overage_item_added', {...})
```

Key events logged:
- `Ignoring non-subscription event`
- `Stripe disabled; ignoring webhook`
- `Ignoring subscription with no customer`
- `org_subscription_overage_item_added`
- `org_subscription_overage_item_exists`

**Sources:** [pages/signals.py:236-575]()

---

## Error Handling

The system employs defensive error handling at multiple levels:

| Failure Scenario | Handling Strategy |
|------------------|-------------------|
| Non-subscription object | Log warning, return early |
| Stripe disabled | Log info, return early |
| Missing customer | Log info, return early |
| No billing owner | Log info, return early |
| Invoice retrieval failure | Log warning, continue with fallback billing_reason |
| SubscriptionItem.create failure | Log exception, attempt continues |
| UserBilling.DoesNotExist | Log exception, anchor update skipped |

**Sources:** [pages/signals.py:240-446](), [pages/signals.py:508-563]()

---

## Test Coverage

The subscription webhook handler has comprehensive test coverage:

### User Subscription Tests

- **Anchor updates from Stripe**: Verifies `billing_cycle_anchor` syncs with `current_period_start.day`
- **Missing UserBilling handling**: Logs exception when billing record doesn't exist
- **Analytics tracking**: Confirms identify/track events fire with correct properties

**Sources:** [tests/unit/test_pages_signals.py:111-191]()

### Organization Subscription Tests

- **Subscription create with seats**: Grants full seat credits with invoice ID
- **Subscription create with existing seats**: Grants only delta (new - previous)
- **Subscription update increase**: Grants incremental credits without invoice
- **Subscription update decrease**: No credits granted
- **Subscription cycle renewal**: Grants full credits with `replace_current=True`
- **Overage item missing**: Attaches overage SKU
- **Overage item present**: Skips attachment
- **Detached pending state**: Skips overage attachment when flag set and seats unchanged
- **Detached pending clear**: Clears flag when overage item exists

**Sources:** [tests/unit/test_pages_signals.py:193-519]()

---

## Configuration Dependencies

The subscription handler relies on several configuration sources:

### Stripe Settings

Retrieved via `get_stripe_settings()`:

```python
stripe_settings = get_stripe_settings()
overage_price_id = stripe_settings.org_team_additional_task_price_id
```

Configuration includes:
- `org_team_price_id` - Base seat price
- `org_team_additional_task_price_id` - Overage/metered price

**Sources:** [pages/signals.py:472-474]()

### Plan Configuration

Retrieved via `get_plan_by_product_id(product_id)`:

```python
plan = get_plan_by_product_id(plan_id)
plan_choice = PlanNamesChoices(plan["id"])
```

Plan dictionaries contain:
- `id` - Plan identifier (matches `PlanNamesChoices`)
- `monthly_task_credits` - Credits for user plans
- `credits_per_seat` - Credits per seat for organization plans

**Sources:** [pages/signals.py:17-18](), [pages/signals.py:418-426]()

---

## Analytics Integration

User subscription events trigger analytics tracking:

```python
Analytics.identify(owner.id, {
    'plan': plan_value,
})

Analytics.track_event(
    user_id=owner.id,
    event=AnalyticsEvent.SUBSCRIPTION_CREATED,
    source=AnalyticsSource.WEB,
    properties={
        'plan': plan_value,
        'stripe.invoice_id': invoice_id,
    }
)
```

Cancellations also trigger `SUBSCRIPTION_CANCELLED` events.

**Sources:** [pages/signals.py:448-460](), [pages/signals.py:327-337]()

---

## Summary

The subscription management system serves as the authoritative sync point between Stripe's subscription state and the platform's credit/billing models. Key design principles:

1. **Webhook-Driven**: All state changes originate from Stripe webhooks
2. **Dual Ownership**: Handles both user and organization subscriptions with different provisioning logic
3. **Defensive Validation**: Multiple early-return paths for invalid/incomplete data
4. **Atomic Updates**: Database fields updated together with selective `update_fields`
5. **Credit Integration**: Delegates to `TaskCreditService` with context-aware parameters
6. **Observability**: Comprehensive logging and tracing for debugging

The system's robustness comes from its careful handling of Stripe's evolving data structures, fallback mechanisms for missing data, and clear separation between user and organization billing flows.

**Sources:** [pages/signals.py:233-651]()

---

# Page: Organization Billing

# Organization Billing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [console/forms.py](console/forms.py)
- [console/templates/console/organization_detail.html](console/templates/console/organization_detail.html)
- [console/templates/partials/_org_invite_modal.html](console/templates/partials/_org_invite_modal.html)
- [constants/stripe.py](constants/stripe.py)
- [pages/signals.py](pages/signals.py)
- [tests/unit/test_organizations.py](tests/unit/test_organizations.py)
- [tests/unit/test_pages_signals.py](tests/unit/test_pages_signals.py)

</details>



## Purpose and Scope

This document covers the seat-based billing system for multi-user organizations, including seat purchase flows, seat modifications (increases and reductions), overage SKU management, and Stripe integration patterns specific to organizations.

For individual user billing and subscription management, see [Subscription Management](#5.2). For how purchased seats translate into task credits, see [TaskCreditService](#5.1). For general organization concepts and membership management, see [Organizations](#3.3).

**Sources:** [console/templates/console/organization_detail.html:1-203](), [tests/unit/test_organizations.py:1-30]()

---

## Seat-Based Billing Model

Organizations use a **seat-based billing model** where each purchased seat grants a monthly allocation of task credits. The organization owner or admins purchase seats via Stripe, and each active or pending member consumes one seat.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Purchased Seats** | Total number of seats currently paid for on the Stripe subscription |
| **Seats Reserved** | Seats consumed by active members + pending invitations |
| **Seats Available** | `purchased_seats - seats_reserved` - can invite new members if > 0 |
| **Credits per Seat** | Defined in plan configuration (e.g., 500 credits/seat/month for Team plan) |

Organizations cannot invite new members when `seats_available <= 0`, enforced at the form validation level.

**Sources:** [console/templates/console/organization_detail.html:22-39](), [console/forms.py:96-109]()

---

## OrganizationBilling Model

The `OrganizationBilling` model tracks all billing state for an organization:

### Core Fields

```python
# From api/models.py (OrganizationBilling)
purchased_seats: int              # Current seat count on Stripe subscription
stripe_customer_id: str           # Stripe Customer ID
stripe_subscription_id: str       # Stripe Subscription ID
billing_cycle_anchor: int         # Day of month (1-31) when billing renews
subscription: str                 # Plan name (e.g., "org_team")
cancel_at: datetime               # Scheduled cancellation timestamp
cancel_at_period_end: bool        # Whether subscription cancels at period end
```

### Pending Seat Changes

For seat reductions (which use Stripe Subscription Schedules to apply changes at the next billing cycle):

```python
pending_seat_quantity: int        # Future seat count (after schedule takes effect)
pending_seat_effective_at: datetime  # When the change will apply
pending_seat_schedule_id: str     # Stripe Schedule ID for cancellation
```

These fields allow the UI to display upcoming changes before they take effect.

**Sources:** [pages/signals.py:595-619](), [tests/unit/test_organizations.py:625-629]()

---

## Seat Purchase Flows

### Diagram: Seat Checkout Decision Tree

```mermaid
graph TD
    Start["User clicks 'Add Seats'"]
    Start --> CheckSub{"Has existing<br/>subscription?"}
    
    CheckSub -->|No| Checkout["Stripe Checkout<br/>organization_seat_checkout"]
    CheckSub -->|Yes| Portal["Billing Portal<br/>subscription_update_confirm"]
    
    Checkout --> CreateSub["Create new subscription<br/>with licensed item"]
    CreateSub --> Webhook["Webhook: subscription.created"]
    
    Portal --> DetachCheck{"Overage SKU<br/>present?"}
    DetachCheck -->|Yes| Detach["Detach overage item<br/>set metadata flag"]
    DetachCheck -->|No| PortalURL["Generate portal URL"]
    
    Detach --> PortalURL
    PortalURL --> UserUpdate["User updates quantity<br/>in Stripe portal"]
    UserUpdate --> ReturnSuccess["Return with ?seats_success=1"]
    
    ReturnSuccess --> Reattach["_reattach_overage_from_session"]
    Reattach --> Complete["Subscription updated"]
    
    Webhook --> GrantSeats["Update purchased_seats<br/>Grant credits"]
    GrantSeats --> Complete
```

**Sources:** [tests/unit/test_organizations.py:152-177](), [tests/unit/test_organizations.py:189-240]()

### Initial Purchase (No Existing Subscription)

When an organization has no active subscription, adding seats triggers a **Stripe Checkout** flow:

1. View: `organization_seat_checkout` creates a Checkout Session with the org team price ID
2. Line items include the licensed seat price (e.g., `org_team_price_id`) with requested quantity
3. Upon completion, Stripe creates a subscription and sends a webhook
4. Webhook handler updates `purchased_seats` and grants credits

**Sources:** [tests/unit/test_organizations.py:152-178]()

### Adding Seats to Existing Subscription

When an organization already has a subscription, the flow uses **Stripe Billing Portal** with `subscription_update_confirm`:

```mermaid
sequenceDiagram
    participant User
    participant View as organization_seat_checkout
    participant Stripe
    participant Portal as Billing Portal
    participant Webhook
    participant DB
    
    User->>View: POST seats=5
    View->>Stripe: Retrieve subscription
    Stripe-->>View: items with licensed item
    
    View->>View: Check for overage SKU
    alt Overage SKU present
        View->>Stripe: SubscriptionItem.delete(overage_item)
        View->>Stripe: Subscription.modify(metadata)
        Note over View,Stripe: Set org_overage_sku_state=detached_pending
    end
    
    View->>Stripe: billing_portal.Session.create
    Note over View,Stripe: flow_data: subscription_update_confirm
    Stripe-->>View: portal_url
    View->>User: Redirect to portal_url
    
    User->>Portal: Update quantity to 5
    Portal->>Stripe: Update subscription
    Stripe->>Webhook: customer.subscription.updated
    Webhook->>DB: Update purchased_seats=5
    
    Portal-->>User: Redirect to return_url?seats_success=1
    User->>View: billing view
    View->>View: _reattach_overage_from_session
    View->>Stripe: SubscriptionItem.create(overage)
    View->>Stripe: Subscription.modify(metadata="")
```

**Sources:** [tests/unit/test_organizations.py:325-393](), [tests/unit/test_organizations.py:404-497]()

### Overage SKU Detachment During Portal Updates

**Problem:** Stripe Billing Portal does not support subscriptions with multiple items when using `subscription_update_confirm` flow.

**Solution:** Temporarily detach the overage SKU before opening the portal, then reattach it upon return.

The detachment process:
1. View calls `stripe.SubscriptionItem.delete(overage_item_id)`
2. View sets `metadata[org_overage_sku_state] = "detached_pending"` on subscription
3. Store detachment info in Django session: `org_overage_detach[org_id]`
4. When user returns from portal, `_reattach_overage_from_session` restores the SKU

**Sources:** [tests/unit/test_organizations.py:325-393](), [constants/stripe.py:1-5]()

---

## Seat Reduction with Subscription Schedules

Organizations cannot immediately reduce seats (to prevent disruption mid-cycle). Instead, seat reductions use **Stripe Subscription Schedules** to apply changes at the next billing period.

### Diagram: Seat Reduction Flow

```mermaid
graph TB
    Start["Admin requests reduction<br/>organization_seat_schedule"]
    Start --> CheckSchedule{"Existing schedule?"}
    
    CheckSchedule -->|Yes| ReleaseOld["SubscriptionSchedule.release(old_id)"]
    CheckSchedule -->|No| CreateNew["SubscriptionSchedule.create"]
    
    ReleaseOld --> CreateNew
    CreateNew --> ModifySchedule["SubscriptionSchedule.modify"]
    
    ModifySchedule --> DefinePhases["Define 2 phases:<br/>1. Current period (current qty)<br/>2. Next period (new qty)"]
    
    DefinePhases --> UpdateDB["Update OrganizationBilling:<br/>pending_seat_quantity<br/>pending_seat_effective_at<br/>pending_seat_schedule_id"]
    
    UpdateDB --> Display["Show pending change in UI"]
    
    BillingCycle["Next billing cycle starts"] --> ScheduleApplies["Schedule phase 2 activates"]
    ScheduleApplies --> WebhookUpdate["Webhook updates purchased_seats"]
    WebhookUpdate --> ClearPending["Clear pending_seat_* fields"]
```

**Sources:** [tests/unit/test_organizations.py:569-629](), [tests/unit/test_organizations.py:636-689]()

### Schedule Creation Process

The view `organization_seat_schedule` creates a two-phase schedule:

**Phase 1 (Current Period):**
- `start_date`: Current `current_period_start` timestamp
- `end_date`: Current `current_period_end` timestamp  
- `items[0].quantity`: Current seat count (unchanged)

**Phase 2 (Next Period):**
- `start_date`: Current `current_period_end` timestamp (when phase 1 ends)
- `items[0].quantity`: New reduced seat count

The schedule is set to `end_behavior="release"`, meaning it releases control back to the subscription after applying the change.

**Sources:** [tests/unit/test_organizations.py:612-623]()

### Replacing Existing Schedules

If a pending reduction already exists, the flow:
1. Calls `SubscriptionSchedule.release(existing_schedule_id)` to cancel the old schedule
2. Creates a new schedule with updated quantities
3. Updates the local `pending_seat_schedule_id` reference

This allows admins to change their mind about the future seat count before it takes effect.

**Sources:** [tests/unit/test_organizations.py:636-689]()

### Canceling Pending Reductions

The view `organization_seat_schedule_cancel`:
1. Calls `SubscriptionSchedule.release(schedule_id)`
2. Clears `pending_seat_quantity`, `pending_seat_effective_at`, and `pending_seat_schedule_id`

**Sources:** [tests/unit/test_organizations.py:694-718]()

---

## Overage SKU Management

The **overage SKU** is a metered Stripe Price that bills for additional tasks consumed beyond the base credits included with purchased seats.

### Configuration

The overage price ID is configured in Stripe settings:
- `org_team_additional_task_price_id` - Metered price for overage tasks

### Automatic Attachment on Subscription Creation/Update

The webhook handler `handle_subscription_event` ensures the overage SKU is attached to all active organization subscriptions:

```mermaid
graph TD
    WebhookReceived["Webhook: subscription.created<br/>or subscription.updated"]
    WebhookReceived --> CheckStatus{"status == active?"}
    
    CheckStatus -->|No| Exit["Exit"]
    CheckStatus -->|Yes| CheckOverageConfig{"overage_price_id<br/>configured?"}
    
    CheckOverageConfig -->|No| SkipOverage["Skip overage logic"]
    CheckOverageConfig -->|Yes| ParseItems["Parse subscription items"]
    
    ParseItems --> CheckPresent{"Overage item<br/>present?"}
    CheckPresent -->|Yes| CheckMetadata{"Metadata flag<br/>detached_pending?"}
    CheckPresent -->|No| CheckShouldAttach{"Should attach?"}
    
    CheckMetadata -->|Yes| ClearFlag["Subscription.modify<br/>clear metadata flag"]
    CheckMetadata -->|No| Done["Done"]
    
    CheckShouldAttach --> CheckFlag{"Metadata flag<br/>detached_pending?"}
    CheckFlag -->|Yes| NoAttach["Skip attachment"]
    CheckFlag -->|No| CheckDelta{"Seat quantity<br/>changed?"}
    
    CheckDelta -->|Yes| Attach["SubscriptionItem.create"]
    CheckDelta -->|No| VerifyPresent{"Re-fetch and verify"}
    
    VerifyPresent -->|Not present| Attach
    VerifyPresent -->|Present| Done
    
    Attach --> Done
    NoAttach --> Done
    ClearFlag --> Done
    SkipOverage --> Done
```

**Sources:** [pages/signals.py:472-575](), [tests/unit/test_pages_signals.py:407-426]()

### Attachment Logic

The webhook attaches the overage SKU when:
1. The subscription is `active`
2. Overage price ID is configured
3. Overage item is not already present
4. Metadata does **not** have `org_overage_sku_state = "detached_pending"`
5. Either:
   - Seat quantity changed (delta != 0), OR
   - Metadata previously had `detached_pending` flag set

This logic prevents duplicate attachment while ensuring the SKU is restored after portal flows.

**Sources:** [pages/signals.py:488-550]()

### Detached Pending State

The metadata key `org_overage_sku_state` with value `detached_pending` signals:
- The overage SKU was deliberately detached for a portal update
- Do **not** automatically reattach it during webhook processing
- The reattachment will happen via `_reattach_overage_from_session` when user returns

When the webhook sees this flag and the overage item is **present**, it clears the flag.

**Sources:** [pages/signals.py:552-575](), [constants/stripe.py:1-5]()

---

## Webhook Processing for Organizations

The `handle_subscription_event` function in `pages/signals.py` processes organization subscriptions differently from user subscriptions.

### Diagram: Webhook Flow for Organizations

```mermaid
graph TB
    Webhook["customer.subscription.*<br/>webhook event"]
    Webhook --> SyncSub["Subscription.sync_from_stripe_data"]
    
    SyncSub --> GetCustomer["Get Customer from subscription"]
    GetCustomer --> CheckSubscriber{"customer.subscriber<br/>exists?"}
    
    CheckSubscriber -->|Yes| UserFlow["User billing flow"]
    CheckSubscriber -->|No| LookupOrg["OrganizationBilling.objects.filter<br/>stripe_customer_id=customer.id"]
    
    LookupOrg --> OrgFound{"Organization found?"}
    OrgFound -->|No| Exit["Exit - no owner"]
    OrgFound -->|Yes| SetOwner["owner = organization<br/>owner_type = 'organization'"]
    
    SetOwner --> CheckDeleted{"Event type<br/>subscription.deleted?"}
    CheckDeleted -->|Yes| Downgrade["downgrade_owner_to_free_plan<br/>purchased_seats = 0"]
    CheckDeleted -->|No| ProcessActive["Process active subscription"]
    
    ProcessActive --> ExtractSeats["Extract quantity from<br/>licensed item"]
    ExtractSeats --> DetermineGrant["Determine seats_to_grant<br/>based on billing_reason"]
    
    DetermineGrant --> GrantCredits["TaskCreditService.<br/>grant_subscription_credits_for_organization"]
    
    GrantCredits --> UpdateBilling["Update OrganizationBilling:<br/>- purchased_seats<br/>- stripe_subscription_id<br/>- billing_cycle_anchor<br/>- cancel_at / cancel_at_period_end"]
    
    UpdateBilling --> ManageOverage["Manage overage SKU<br/>attachment/detachment"]
```

**Sources:** [pages/signals.py:234-651]()

### Organization Identification

Organizations are identified when:
1. `customer.subscriber` is `None` (no linked User)
2. `OrganizationBilling.stripe_customer_id` matches the customer ID

**Sources:** [pages/signals.py:299-311]()

### Billing Reason and Credit Granting

The webhook uses `billing_reason` to determine how many seats to grant credits for:

| Billing Reason | Seats to Grant | Invoice ID Passed | Replace Current |
|----------------|----------------|-------------------|-----------------|
| `subscription_create` | All seats (or delta if prev_seats > 0) | Yes (if prev_seats == 0) | Yes |
| `subscription_cycle` | All seats | Yes | Yes |
| `subscription_update` | Delta (if seats increased) | No | No |
| Other/None | 0 (no grant) | No | No |

The `replace_current` flag tells `TaskCreditService` whether to reset the active monthly credit block or add a new one.

**Sources:** [pages/signals.py:621-650](), [tests/unit/test_pages_signals.py:371-402]()

### Billing Reason Resolution

The webhook tries to find `billing_reason` in this order:
1. `source_data.billing_reason` (from subscription payload)
2. `subscription.billing_reason` attribute
3. Fetch latest invoice and check `invoice.billing_reason`

This fallback ensures the correct grant logic even when the subscription object doesn't include the reason.

**Sources:** [pages/signals.py:380-399]()

### Subscription Field Updates

The webhook updates `OrganizationBilling` fields atomically:

```python
# From pages/signals.py:577-619
updates = []
if current_period_start_dt:
    new_day = current_period_start_dt.day
    if billing.billing_cycle_anchor != new_day:
        billing.billing_cycle_anchor = new_day
        updates.append("billing_cycle_anchor")

if seats and billing.purchased_seats != seats:
    billing.purchased_seats = seats
    updates.append("purchased_seats")

# Clear pending seat changes if quantity changed
if pending_schedule_id and seats != prev_seats:
    billing.pending_seat_quantity = None
    billing.pending_seat_effective_at = None
    billing.pending_seat_schedule_id = ""
    updates.extend([...])

if billing.cancel_at != cancel_at_dt:
    billing.cancel_at = cancel_at_dt
    updates.append("cancel_at")

if updates:
    billing.save(update_fields=updates)
```

This ensures only changed fields are saved, minimizing database writes.

**Sources:** [pages/signals.py:577-619]()

### Pending Seat Change Clearance

When a webhook updates `purchased_seats` and the new quantity differs from the old quantity, any pending seat schedule is assumed to have taken effect. The webhook clears:
- `pending_seat_quantity`
- `pending_seat_effective_at`
- `pending_seat_schedule_id`

This prevents stale pending change info from displaying in the UI after the schedule applies.

**Sources:** [pages/signals.py:595-607]()

---

## UI Integration

### Organization Detail Page

The organization detail template displays billing information:

```django
<!-- From console/templates/console/organization_detail.html:22-39 -->
<dl class="grid gap-4 sm:grid-cols-3">
  <div>
    <dt>Seats Purchased</dt>
    <dd>{{ org_billing.purchased_seats }}</dd>
  </div>
  <div>
    <dt>In Use</dt>
    <dd>{{ org_billing.seats_reserved }}</dd>
  </div>
  <div>
    <dt>Available</dt>
    <dd>{{ org_billing.seats_available }}</dd>
  </div>
</dl>
```

**Computed Properties:**
- `seats_reserved`: Active members + pending invitations
- `seats_available`: `purchased_seats - seats_reserved`

**Sources:** [console/templates/console/organization_detail.html:22-39]()

### Seat Availability Checks

Invite forms check seat availability and disable invitations when none remain:

```django
<!-- From console/templates/console/organization_detail.html:51-58 -->
{% if org_billing and org_billing.seats_available <= 0 %}
  <span class="warning-badge">No seats available</span>
{% endif %}
```

Form validation also enforces this:

**Sources:** [console/forms.py:96-109](), [console/templates/partials/_org_invite_modal.html:39-51]()

---

## Integration with TaskCreditService

Seat purchases flow to credit grants via `TaskCreditService.grant_subscription_credits_for_organization`:

```python
# Simplified from pages/signals.py:643-650
TaskCreditService.grant_subscription_credits_for_organization(
    owner=organization,
    seats=seats_to_grant,
    plan=plan,
    invoice_id=grant_invoice_id,
    subscription=sub,
    replace_current=True,  # For cycle/create events
)
```

For details on how this service creates `TaskCredit` records with seat-based quantities, see [TaskCreditService](#5.1).

**Sources:** [pages/signals.py:643-650]()

---

## Error Handling and Edge Cases

### Missing Billing Record

If webhook processing cannot find either a user or organization owner, it logs and exits without error:

```python
# From pages/signals.py:308-311
if not owner:
    logger.info("Subscription %s has no linked billing owner; nothing to do.", sub.id)
    return
```

**Sources:** [pages/signals.py:308-311]()

### Portal Failure Fallback

When the Billing Portal fails with `InvalidRequestError` (often due to multiple items), the view falls back to **direct subscription modification**:

1. View catches `stripe.error.InvalidRequestError`
2. Retrieves subscription again
3. Modifies subscription item quantity directly via `stripe.SubscriptionItem.modify`
4. Reattaches overage SKU immediately
5. Displays success message: "Stripe portal seat updates are disabled, so we applied the seat change immediately."

This ensures seat changes complete even when the portal flow is unavailable.

**Sources:** [tests/unit/test_organizations.py:404-497]()

### Auto-Paging Iterator Errors

Stripe's Python SDK sometimes returns iterators in `subscription.items` instead of lists. The webhook handles this:

```python
# From pages/signals.py:264-280
try:
    sub = Subscription.sync_from_stripe_data(payload)
except Exception as exc:
    if "auto_paging_iter" in str(exc):
        stripe_sub = stripe.Subscription.retrieve(
            payload["id"],
            expand=["items"],
        )
        sub = Subscription.sync_from_stripe_data(stripe_sub)
    else:
        raise
```

**Sources:** [pages/signals.py:264-280]()

---

## Summary

Organization billing uses a seat-based model where:
- Organizations purchase seats via Stripe (Checkout for new, Billing Portal for existing)
- Each seat grants monthly credits (`plan.credits_per_seat × purchased_seats`)
- Seat increases take effect immediately via webhook
- Seat reductions use Subscription Schedules to apply at next billing period
- An overage SKU (metered price) tracks additional task consumption
- Overage SKU is temporarily detached for portal flows, then reattached
- All state synchronization happens via Stripe webhooks

**Sources:** [pages/signals.py:234-651](), [tests/unit/test_organizations.py:1-800](), [console/templates/console/organization_detail.html:1-203]()

---

# Page: Usage Analytics

# Usage Analytics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [config/urls.py](config/urls.py)
- [console/usage_views.py](console/usage_views.py)
- [frontend/src/components/usage/types.ts](frontend/src/components/usage/types.ts)
- [frontend/src/screens/UsageScreen.tsx](frontend/src/screens/UsageScreen.tsx)
- [tests/unit/test_usage_trends_api.py](tests/unit/test_usage_trends_api.py)

</details>



The Usage Analytics system provides real-time visibility into agent and API activity, credit consumption, and resource utilization. It aggregates data from both agent-driven tasks and direct API calls to generate comprehensive usage reports, trend analysis, and performance metrics.

For information about credit provisioning and consumption mechanics, see [TaskCreditService](#5.1). For subscription billing and metering, see [Subscription Management](#5.2).

---

## Purpose and Scope

This system exposes a suite of JSON API endpoints that power the usage dashboard in the Console interface. It enables users and organizations to:

- Monitor credit consumption across billing periods
- Track agent performance and activity levels
- Identify which tools consume the most resources
- Analyze usage trends over time (hourly, daily, monthly)
- Filter metrics by specific agents or date ranges

The system is context-aware, automatically scoping queries to personal or organization resources based on the authenticated user's active context.

**Sources**: [console/usage_views.py:1-943](), [frontend/src/screens/UsageScreen.tsx:1-338]()

---

## Core Concepts

### API Agent

The system introduces a special pseudo-agent identifier `API_AGENT_ID = "api"` to represent tasks created directly via the REST API without an associated `PersistentAgent`. This allows direct API usage to appear alongside agent-driven activity in all analytics views.

API tasks are identified by `agent_id__isnull=True` in the `BrowserUseAgentTask` model. They are assigned a default credit cost of `1.0` if no explicit `credits_cost` is provided.

**Sources**: [console/usage_views.py:27-29](), [console/usage_views.py:116-123]()

### Data Sources

Usage metrics are aggregated from two primary models:

| Model | Purpose | Credit Field |
|-------|---------|--------------|
| `BrowserUseAgentTask` | Browser automation tasks (agent-driven or API-initiated) | `credits_cost` |
| `PersistentAgentStep` | Agent reasoning steps, tool calls, and runtime overhead | `credits_cost` |

Both data sources are queried in parallel and their credits are summed to produce total consumption figures.

**Sources**: [console/usage_views.py:226-263](), [console/usage_views.py:454-486]()

### Context Awareness

All endpoints respect the user's active context (personal or organization). The context is determined via `build_console_context(request)`, which reads session state set by the context switcher.

- **Personal context**: Filters by `user=request.user` and `organization__isnull=True`
- **Organization context**: Filters by `organization=<org>` where the user is a member

This ensures users only see data they are authorized to access.

**Sources**: [console/usage_views.py:180-189](), [console/usage_views.py:410-421]()

---

## API Endpoints

### Endpoint Overview

```mermaid
graph TB
    Client["Frontend Client"]
    
    Summary["UsageSummaryAPIView<br/>/console/api/usage/summary/"]
    Trends["UsageTrendAPIView<br/>/console/api/usage/trends/"]
    Tools["UsageToolBreakdownAPIView<br/>/console/api/usage/tools/"]
    Leaderboard["UsageAgentLeaderboardAPIView<br/>/console/api/usage/agents/leaderboard/"]
    Agents["UsageAgentsAPIView<br/>/console/api/usage/agents/"]
    
    Client --> Summary
    Client --> Trends
    Client --> Tools
    Client --> Leaderboard
    Client --> Agents
    
    Summary --> DB["Database<br/>BrowserUseAgentTask<br/>PersistentAgentStep<br/>TaskCredit"]
    Trends --> DB
    Tools --> DB
    Leaderboard --> DB
    Agents --> DB
    
    style Summary fill:#e1f5ff
    style Trends fill:#fff4e1
    style Tools fill:#ffe1e1
    style Leaderboard fill:#e8f5e9
    style Agents fill:#f3e5f5
```

**Sources**: [config/urls.py:122-126](), [console/usage_views.py:176-943]()

---

### Summary Endpoint

**Route**: `GET /console/api/usage/summary/`

**View**: `UsageSummaryAPIView`

Returns high-level metrics for a billing period, including task counts by status, total credit consumption, and quota information.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | ISO date | Start date (defaults to billing period start) |
| `to` | ISO date | End date (defaults to billing period end) |
| `agent` | string[] | Filter by agent IDs (supports "api" for API tasks) |

#### Response Structure

```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31",
    "label": "Jan 1 – Jan 31, 2024",
    "timezone": "America/New_York"
  },
  "context": {
    "type": "personal",
    "id": "...",
    "name": "user@example.com"
  },
  "metrics": {
    "tasks": {
      "count": 150.0,
      "completed": 140.0,
      "in_progress": 5.0,
      "pending": 3.0,
      "failed": 2.0,
      "cancelled": 0.0
    },
    "credits": {
      "total": 150.0,
      "unit": "credits"
    },
    "quota": {
      "available": 850.0,
      "total": 1000.0,
      "used": 150.0,
      "used_pct": 15.0
    }
  }
}
```

#### Implementation Details

The view performs three major aggregations:

1. **Task status breakdown**: Groups `BrowserUseAgentTask` by `status` and sums credits using `_per_task_credit_expression()`. This expression handles the API agent special case by defaulting to `1.0` credit when `agent_id` is null.

2. **Persistent step credits**: Sums `PersistentAgentStep.credits_cost` for all steps in the period. These are counted as "completed" since steps represent finished work.

3. **Current quota**: Queries `TaskCredit` for non-voided credits where `granted_date <= now` and `expiration_date >= now`, computing available, total, and used amounts.

**Sources**: [console/usage_views.py:176-334](), [console/usage_views.py:143-152]()

---

### Trend Endpoint

**Route**: `GET /console/api/usage/trends/`

**View**: `UsageTrendAPIView`

Returns time-bucketed usage data for visualizing trends. Supports three modes with automatic lookback periods.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `mode` | string | Required: `day`, `week`, or `month` |
| `from` | ISO date | Custom range start (optional) |
| `to` | ISO date | Custom range end (optional) |
| `agent` | string[] | Filter by agent IDs |

#### Mode Behavior

| Mode | Resolution | Default Range | Comparison Period |
|------|-----------|---------------|-------------------|
| `day` | Hourly | Today | Previous 24 hours |
| `week` | Daily | Last 7 days | Prior 7 days |
| `month` | Daily | Last 30 days | Prior 30 days |

#### Response Structure

```json
{
  "mode": "week",
  "resolution": "day",
  "timezone": "America/New_York",
  "current_period": {
    "start": "2024-01-08T00:00:00-05:00",
    "end": "2024-01-15T00:00:00-05:00"
  },
  "previous_period": {
    "start": "2024-01-01T00:00:00-05:00",
    "end": "2024-01-08T00:00:00-05:00"
  },
  "agents": [
    {"id": "...", "name": "Agent Alpha"},
    {"id": "api", "name": "API"}
  ],
  "buckets": [
    {
      "timestamp": "2024-01-08T00:00:00-05:00",
      "current": 15.0,
      "previous": 12.0,
      "agents": {
        "...": 10.0,
        "api": 5.0
      }
    }
  ]
}
```

#### Implementation Details

The view uses `TruncHour` or `TruncDay` from Django ORM to bucket timestamps. It executes two separate queries for current and previous periods, then aligns buckets using `timedelta` arithmetic.

The `agents` field in each bucket breaks down credits by agent ID, enabling stacked area charts or multi-series line graphs.

**Sources**: [console/usage_views.py:337-590](), [console/usage_views.py:433-567]()

---

### Tool Breakdown Endpoint

**Route**: `GET /console/api/usage/tools/`

**View**: `UsageToolBreakdownAPIView`

Aggregates credit consumption by tool name, showing which integrations (MCP tools, browser automation, etc.) consume the most resources.

#### Query Parameters

Same as summary endpoint: `from`, `to`, `agent`

#### Response Structure

```json
{
  "range": {
    "start": "2024-01-01T00:00:00-05:00",
    "end": "2024-01-31T23:59:59-05:00"
  },
  "timezone": "America/New_York",
  "total_count": 145.5,
  "total_credits": 145.5,
  "total_invocations": 127,
  "tools": [
    {
      "name": "search_tools",
      "invocations": 45,
      "credits": 52.5
    },
    {
      "name": "send_email",
      "invocations": 30,
      "credits": 30.0
    },
    {
      "name": "api_task",
      "invocations": 12,
      "credits": 15.0
    },
    {
      "name": "agent_runtime",
      "invocations": 0,
      "credits": 48.0
    }
  ]
}
```

#### Special Tool Categories

- **Named tools**: Populated from `PersistentAgentToolCall.tool_name`, representing explicit MCP or built-in tool invocations
- **`api_task`**: Browser tasks created via API without a PersistentAgent (`agent_id__isnull=True`)
- **`agent_runtime`**: Residual credits from `PersistentAgentStep` that are not attributed to specific tool calls (LLM reasoning overhead, system messages, etc.)

The residual calculation ensures all consumed credits are accounted for:

```python
residual_credits = persistent_step_credits - total_tool_credits
```

**Sources**: [console/usage_views.py:593-758](), [console/usage_views.py:728-737]()

---

### Leaderboard Endpoint

**Route**: `GET /console/api/usage/agents/leaderboard/`

**View**: `UsageAgentLeaderboardAPIView`

Ranks agents by total credit consumption, computing average credits per day and success/error breakdowns.

#### Response Structure

```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31",
    "label": "Jan 1 – Jan 31, 2024",
    "timezone": "America/New_York"
  },
  "agents": [
    {
      "id": "...",
      "name": "Agent Alpha",
      "tasks_total": 125.5,
      "tasks_per_day": 4.05,
      "success_count": 120.0,
      "error_count": 5.5,
      "persistent_id": "..."
    },
    {
      "id": "api",
      "name": "API",
      "tasks_total": 45.0,
      "tasks_per_day": 1.45,
      "success_count": 45.0,
      "error_count": 0.0,
      "persistent_id": null
    }
  ]
}
```

#### Calculation Logic

- **tasks_total**: Sum of all credits (browser tasks + persistent steps)
- **success_count**: Credits from `COMPLETED` browser tasks + all persistent steps (steps are assumed successful)
- **error_count**: Credits from `FAILED` browser tasks
- **tasks_per_day**: `tasks_total / period_length_days`

The leaderboard is sorted descending by `tasks_total`.

**Sources**: [console/usage_views.py:761-918](), [console/usage_views.py:884-906]()

---

### Agents List Endpoint

**Route**: `GET /console/api/usage/agents/`

**View**: `UsageAgentsAPIView`

Returns all agents accessible in the current context, used to populate filter dropdowns.

#### Response Structure

```json
{
  "agents": [
    {"id": "api", "name": "API"},
    {"id": "...", "name": "Agent Alpha"},
    {"id": "...", "name": "Agent Beta"}
  ]
}
```

The list always includes the special `API_AGENT_ID` entry and is sorted alphabetically by name.

**Sources**: [console/usage_views.py:921-943](), [console/usage_views.py:67-101]()

---

## Data Flow Architecture

```mermaid
graph TB
    Request["HTTP Request<br/>GET /console/api/usage/summary/"]
    
    View["UsageSummaryAPIView.get()"]
    Context["build_console_context(request)"]
    
    ParseDates["_parse_query_date()<br/>Parse from/to params"]
    GetAgents["_get_accessible_agents()<br/>Filter by context"]
    AgentFilter["_resolve_agent_selection()<br/>Parse agent filter"]
    
    BillingPeriod["BillingService.get_current_billing_period_for_owner()"]
    
    TaskQuery["BrowserUseAgentTask.objects.filter()"]
    TaskAnnotate["annotate(total=Sum(_per_task_credit_expression()))"]
    TaskGroup["values('status')"]
    
    StepQuery["PersistentAgentStep.objects.filter()"]
    StepSum["aggregate(total=Sum('credits_cost'))"]
    
    CreditQuery["TaskCredit.objects.filter()"]
    CreditAgg["aggregate(available, total, used)"]
    
    Response["JsonResponse(payload)"]
    
    Request --> View
    View --> Context
    View --> ParseDates
    View --> GetAgents
    View --> AgentFilter
    View --> BillingPeriod
    
    View --> TaskQuery
    TaskQuery --> TaskAnnotate
    TaskAnnotate --> TaskGroup
    
    View --> StepQuery
    StepQuery --> StepSum
    
    View --> CreditQuery
    CreditQuery --> CreditAgg
    
    TaskGroup --> Response
    StepSum --> Response
    CreditAgg --> Response
    
    style View fill:#e1f5ff
    style TaskQuery fill:#fff4e1
    style StepQuery fill:#ffe1e1
    style CreditQuery fill:#e8f5e9
```

**Sources**: [console/usage_views.py:176-334](), [console/usage_views.py:42-173]()

---

## Query Construction Patterns

### Agent Filtering

All views use a common helper chain to resolve agent filters:

```mermaid
graph LR
    Raw["Raw agent IDs<br/>from query params"]
    GetAccessible["_get_accessible_agents()<br/>context-scoped list"]
    
    Filter["_filter_agent_ids()<br/>validate against accessible"]
    Split["_split_agent_filter_values()<br/>separate 'api' from UUIDs"]
    Build["_build_agent_filter()<br/>construct Q object"]
    
    Apply["Apply to queryset.filter()"]
    
    Raw --> GetAccessible
    GetAccessible --> Filter
    Filter --> Split
    Split --> Build
    Build --> Apply
    
    style GetAccessible fill:#e1f5ff
    style Split fill:#fff4e1
    style Build fill:#ffe1e1
```

The `_build_agent_filter()` function returns a Django `Q` object combining:
- `Q(agent_id__in=actual_agent_ids)` for concrete agents
- `Q(agent_id__isnull=True)` if the "api" pseudo-agent is selected

**Sources**: [console/usage_views.py:104-141](), [console/usage_views.py:155-173]()

### Credit Expression

The `_per_task_credit_expression()` function is a Django `Case/When` construct that normalizes credit costs across API and agent-driven tasks:

```python
Case(
    When(agent_id__isnull=True, then=Coalesce(F("credits_cost"), Value(Decimal("1")))),
    default=Coalesce(F("credits_cost"), Value(Decimal("0"))),
    output_field=DecimalField(max_digits=20, decimal_places=6)
)
```

This ensures:
- API tasks without explicit `credits_cost` default to `1.0`
- Agent tasks without explicit cost default to `0.0` (should not happen in practice but prevents null issues)

**Sources**: [console/usage_views.py:143-152]()

---

## Frontend Integration

### UsageScreen Component

The main dashboard component manages state for:
- Date range selection (billing period vs custom range)
- Agent filtering
- Tab navigation across metrics, trends, tools, and leaderboard

```mermaid
graph TB
    Screen["UsageScreen"]
    
    Store["useUsageStore<br/>Zustand global state"]
    Query["useQuery<br/>React Query"]
    
    Header["UsagePeriodHeader<br/>Date picker + agent filter"]
    Metrics["UsageMetricsGrid<br/>Summary cards"]
    Trends["UsageTrendSection<br/>Time series chart"]
    Tools["UsageToolChart<br/>Pie chart"]
    Leaderboard["UsageAgentLeaderboard<br/>Table"]
    
    Screen --> Store
    Screen --> Query
    Screen --> Header
    Screen --> Metrics
    Screen --> Trends
    Screen --> Tools
    Screen --> Leaderboard
    
    Header -.->|"User actions"| Screen
    Metrics --> Query
    Trends --> Query
    Tools --> Query
    Leaderboard --> Query
    
    style Screen fill:#e1f5ff
    style Store fill:#fff4e1
    style Query fill:#ffe1e1
```

**Sources**: [frontend/src/screens/UsageScreen.tsx:1-338]()

### Date Range Handling

The component supports two selection modes:

- **Billing mode**: Navigates forward/backward by full billing cycles using `shiftBillingRange()`. Automatically aligns to the billing cycle anchor day.
- **Custom mode**: Navigates by the length of the user-selected range using `shiftCustomRangeByDays()`.

The effective range is tracked in three state variables:
- `appliedRange`: Currently active filter
- `calendarRange`: Temporary selection while picker is open
- `summaryRange`: Server's billing period (fallback)

**Sources**: [frontend/src/screens/UsageScreen.tsx:38-216]()

### State Synchronization

React Query handles API fetching, while Zustand (`useUsageStore`) provides synchronous access to the latest data for immediate UI updates. This prevents loading flashes when switching tabs or agents.

**Sources**: [frontend/src/screens/UsageScreen.tsx:47-100]()

---

## Testing Strategy

The test suite validates all endpoints under both personal and organization contexts, agent filtering, and edge cases.

### Key Test Cases

| Test Class | Coverage |
|------------|----------|
| `UsageTrendAPITests` | Week/day/month modes, previous period calculation, persistent steps, API agent |
| `UsageAgentLeaderboardAPITests` | Zero-state, totals, per-day averages, persistent step inclusion, API tasks |
| `UsageToolBreakdownAPITests` | Tool aggregation, agent filtering, org context, API task surfacing, residual calculation |
| `UsageAgentsAPITests` | Personal vs org context, agent list sorting |
| `UsageSummaryAPITests` | Agent filtering, context isolation, persistent steps, API tasks |

All tests use `@tag("batch_usage_api")` for targeted test execution and `@override_settings(FIRST_RUN_SETUP_ENABLED=False, LLM_BOOTSTRAP_OPTIONAL=True)` to bypass setup requirements.

**Sources**: [tests/unit/test_usage_trends_api.py:1-821]()

---

## Common Query Patterns

### Filtering by Agent

```
GET /console/api/usage/summary/?agent=<agent_id>&agent=api
```

Multiple `agent` parameters are OR'd together. The special `api` value includes agentless browser tasks.

### Custom Date Range

```
GET /console/api/usage/trends/?mode=week&from=2024-01-01&to=2024-01-07
```

Dates must be ISO 8601 format (`YYYY-MM-DD`). If omitted, defaults to the current billing period.

### Organization Context

The backend automatically scopes queries based on the user's active session context. No query parameter is needed—context is read from `request.session`.

**Sources**: [console/usage_views.py:191-200](), [console/usage_views.py:348-364]()

---

## Performance Considerations

- All aggregations use database-level `Sum()` and `Count()` to minimize data transfer
- `select_related("persistent_agent")` is used when loading agents to avoid N+1 queries
- Date range filters use indexed `created_at` fields
- Decimal arithmetic is performed in Python after aggregation to maintain precision

The trend endpoint can be expensive for hourly resolution over long periods. The default 7-day and 30-day lookbacks are chosen to balance granularity with query cost.

**Sources**: [console/usage_views.py:87](), [console/usage_views.py:235-241]()

---

# Page: Tool Integration

# Tool Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/llm_config.py](api/agent/core/llm_config.py)
- [api/agent/tools/mcp_manager.py](api/agent/tools/mcp_manager.py)
- [api/agent/tools/mcp_tools.py](api/agent/tools/mcp_tools.py)
- [api/integrations/pipedream_connect.py](api/integrations/pipedream_connect.py)
- [api/migrations/0127_pipedream_connect_session.py](api/migrations/0127_pipedream_connect_session.py)
- [api/migrations/0137_add_trello_tool_friendly_names.py](api/migrations/0137_add_trello_tool_friendly_names.py)
- [api/tasks/browser_agent_tasks.py](api/tasks/browser_agent_tasks.py)
- [tests/unit/test_browser_task_follow_up.py](tests/unit/test_browser_task_follow_up.py)
- [tests/unit/test_event_processing_llm_selection.py](tests/unit/test_event_processing_llm_selection.py)
- [tests/unit/test_llm_failover.py](tests/unit/test_llm_failover.py)
- [tests/unit/test_mcp_tools.py](tests/unit/test_mcp_tools.py)
- [tests/unit/test_pipedream_connect.py](tests/unit/test_pipedream_connect.py)
- [tests/unit/test_pipedream_greenhouse.py](tests/unit/test_pipedream_greenhouse.py)
- [tests/unit/test_pipedream_trello.py](tests/unit/test_pipedream_trello.py)
- [tests/utils/llm_seed.py](tests/utils/llm_seed.py)

</details>



The gobii platform provides three primary integration systems that enable agents to interact with external services, automate browser tasks, and leverage multiple LLM providers. This document provides an architectural overview of these integration layers. For detailed implementation specifics, see:
- [MCP Tools](#6.1) - Model Context Protocol tool discovery and execution
- [Browser Automation](#6.2) - Web automation via browser-use library  
- [LLM Integration](#6.3) - Multi-provider LLM configuration and failover

---

## Overview

The platform's tool integration architecture consists of three independent but complementary systems:

| System | Purpose | Primary Code Entity |
|--------|---------|-------------------|
| **MCP Tools** | Dynamic discovery and execution of 2,800+ external API integrations via Model Context Protocol | `MCPToolManager` |
| **Browser Automation** | Headless Chrome automation for web scraping and interaction | `process_browser_use_task` |
| **LLM Integration** | Multi-provider LLM configuration with token-based tier selection and automatic failover | `get_llm_config_with_failover()` |

These systems operate independently—agents can use MCP tools without browser automation, or browser tasks without MCP tools—but are often composed together during agent event processing.

**Sources:** [api/agent/tools/mcp_manager.py:1-735](), [api/tasks/browser_agent_tasks.py:1-1130](), [api/agent/core/llm_config.py:1-478]()

---

## System Architecture

### High-Level Component Interaction

```mermaid
graph TB
    subgraph "Agent Event Loop"
        EventProcessor["process_agent_events_task<br/>(Celery)"]
        LLMCall["_completion_with_failover()"]
        ToolDispatch["Tool Execution Dispatcher"]
    end
    
    subgraph "LLM Integration"
        LLMConfig["get_llm_config_with_failover()"]
        TokenRange["PersistentTokenRange<br/>(DB)"]
        LLMTier["PersistentLLMTier<br/>(DB)"]
        TierEndpoint["PersistentTierEndpoint<br/>(DB)"]
        Providers["LLM Providers:<br/>Anthropic, Google,<br/>OpenAI, OpenRouter"]
    end
    
    subgraph "MCP Tool System"
        MCPManager["MCPToolManager<br/>(_mcp_manager)"]
        SearchTools["search_tools()"]
        EnableTool["enable_mcp_tool()"]
        ExecuteTool["execute_mcp_tool()"]
        ToolCache["_tools_cache<br/>(in-memory)"]
        EnabledTools["PersistentAgentEnabledTool<br/>(DB)"]
        MCPServers["MCP Servers:<br/>Bright Data (stdio),<br/>Pipedream (HTTP/SSE)"]
    end
    
    subgraph "Browser Automation"
        BrowserTask["process_browser_use_task<br/>(Celery)"]
        BrowserSession["BrowserSession<br/>(browser-use)"]
        ProfileMgr["Profile Persistence<br/>(S3/Local Storage)"]
        ProxySelect["select_proxy_for_task()"]
        TaskModel["BrowserUseAgentTask<br/>(DB)"]
    end
    
    subgraph "Pipedream OAuth"
        ConnectSession["create_connect_session()"]
        PDSession["PipedreamConnectSession<br/>(DB)"]
        Webhook["pipedream_connect_webhook"]
    end
    
    EventProcessor --> LLMCall
    LLMCall --> LLMConfig
    LLMConfig --> TokenRange
    TokenRange --> LLMTier
    LLMTier --> TierEndpoint
    TierEndpoint --> Providers
    
    EventProcessor --> ToolDispatch
    ToolDispatch --> SearchTools
    ToolDispatch --> ExecuteTool
    ToolDispatch --> BrowserTask
    
    SearchTools --> MCPManager
    ExecuteTool --> MCPManager
    MCPManager --> ToolCache
    MCPManager --> EnabledTools
    MCPManager --> MCPServers
    MCPManager --> ConnectSession
    
    ExecuteTool --> PDSession
    ConnectSession --> PDSession
    PDSession --> Webhook
    Webhook --> EventProcessor
    
    BrowserTask --> BrowserSession
    BrowserTask --> ProfileMgr
    BrowserTask --> ProxySelect
    BrowserTask --> TaskModel
    BrowserTask -.schedule follow-up.-> EventProcessor
    
    EnableTool --> EnabledTools
    EnableTool --> MCPManager
```

**Sources:** [api/agent/tools/mcp_manager.py:78-735](), [api/tasks/browser_agent_tasks.py:542-1130](), [api/agent/core/llm_config.py:235-401]()

---

## MCP Tool Integration

The MCP (Model Context Protocol) system enables agents to discover and execute tools from multiple servers without hardcoded integrations. The platform supports both **stdio-based** servers (like Bright Data) and **HTTP/SSE** servers (like Pipedream).

### Tool Discovery and Enablement Flow

```mermaid
sequenceDiagram
    participant Agent
    participant search_tools
    participant MCPManager as "MCPToolManager<br/>(_mcp_manager)"
    participant LLM as "LLM (via litellm)"
    participant enable_tools
    participant DB as "PersistentAgentEnabledTool"
    
    Agent->>search_tools: query="send email via Gmail"
    search_tools->>MCPManager: get_all_available_tools()
    MCPManager-->>search_tools: List[MCPToolInfo]
    
    search_tools->>search_tools: Build compact catalog<br/>_strip_desc(), _summarize_params()
    search_tools->>LLM: completion(tools=[enable_tools])
    LLM-->>search_tools: tool_call: enable_tools(["gmail-send-email"])
    
    search_tools->>enable_tools: tool_names=["gmail-send-email"]
    enable_tools->>DB: Check enabled count
    
    alt Count < 40
        enable_tools->>DB: Create PersistentAgentEnabledTool
    else Count >= 40
        enable_tools->>DB: Evict oldest by last_used_at
        enable_tools->>DB: Create new record
    end
    
    DB-->>enable_tools: Enabled
    enable_tools-->>search_tools: {"status": "success", "enabled": [...]}
    search_tools-->>Agent: Tools enabled and ready
```

**Key Components:**

| Entity | Purpose | Location |
|--------|---------|----------|
| `MCPToolManager` | Singleton managing MCP server connections and tool catalog | [api/agent/tools/mcp_manager.py:78-735]() |
| `_mcp_manager` | Global instance of MCPToolManager | [api/agent/tools/mcp_manager.py:735]() |
| `search_tools()` | LLM-driven tool discovery that auto-enables relevant tools | [api/agent/tools/mcp_manager.py:738-901]() |
| `enable_mcp_tool()` | Enable a single tool with LRU eviction (40-tool limit) | [api/agent/tools/mcp_manager.py:904-985]() |
| `MCPToolInfo` | Dataclass representing discovered tool metadata | [api/agent/tools/mcp_manager.py:58-75]() |
| `PersistentAgentEnabledTool` | DB model tracking enabled tools per agent | [api/models.py]() |

**Tool Discovery Process:**

1. **Initialization:** `MCPToolManager.initialize()` connects to configured servers and caches tools in `_tools_cache`
2. **Server Registration:** `_register_server()` creates stdio or HTTP transport and fetches available tools
3. **Tool Filtering:** `_is_tool_blacklisted()` applies glob patterns from `TOOL_BLACKLIST` 
4. **LLM Analysis:** `search_tools()` builds a compact catalog and lets an LLM select relevant tools
5. **Auto-Enable:** Selected tools are enabled via internal `enable_tools()` function call

**Sources:** [api/agent/tools/mcp_manager.py:158-343](), [api/agent/tools/mcp_manager.py:738-901]()

### Tool Execution

When an agent needs to execute an enabled MCP tool:

```mermaid
graph LR
    A["execute_mcp_tool()<br/>(agent, tool_name, params)"]
    B["Check<br/>PersistentAgentEnabledTool"]
    C["_resolve_tool()<br/>(server_name, tool_name)"]
    D{Server Type?}
    E["stdio client<br/>(Bright Data)"]
    F["_get_pipedream_agent_client()<br/>(per-agent, per-app)"]
    G["_execute_async()<br/>client.call_tool()"]
    H{Result contains<br/>Connect Link?}
    I["create_connect_session()"]
    J["Return action_required<br/>with connect_url"]
    K["Return success/error"]
    
    A --> B
    B -->|Not enabled| K
    B -->|Enabled| C
    C --> D
    D -->|stdio| E
    D -->|Pipedream| F
    E --> G
    F --> G
    G --> H
    H -->|Yes| I
    I --> J
    H -->|No| K
```

**Key Functions:**

| Function | Purpose | File Location |
|----------|---------|--------------|
| `execute_mcp_tool()` | Main execution entry point with blacklist/permission checks | [api/agent/tools/mcp_manager.py:397-608]() |
| `_resolve_tool()` | Map full_name to (server_name, actual_tool_name) | [api/agent/tools/mcp_manager.py:630-647]() |
| `_execute_async()` | Async wrapper for client.call_tool() | [api/agent/tools/mcp_manager.py:610-613]() |
| `_get_pipedream_agent_client()` | Get or create per-agent, per-app Pipedream client | [api/agent/tools/mcp_manager.py:706-729]() |

**Execution Flow:**

1. Check if tool is blacklisted via `_is_tool_blacklisted()` 
2. Verify tool is enabled in `PersistentAgentEnabledTool`
3. Update `last_used_at` and `usage_count` for LRU tracking
4. Resolve server and actual tool name
5. For Pipedream: create per-agent client with OAuth headers
6. Execute via async `client.call_tool()`
7. If result contains Pipedream Connect Link, trigger OAuth flow

**Sources:** [api/agent/tools/mcp_manager.py:397-608](), [api/agent/tools/mcp_manager.py:706-729]()

---

## Pipedream OAuth Integration

Pipedream tools requiring user credentials pause agent execution and generate a Connect Link for user authorization.

### Connect Link Flow

```mermaid
sequenceDiagram
    participant Agent
    participant execute_mcp_tool
    participant MCPClient as "Pipedream MCP Client"
    participant create_connect_session
    participant PDSession as "PipedreamConnectSession<br/>(DB)"
    participant PDAPI as "Pipedream API"
    participant User
    participant Webhook as "pipedream_connect_webhook"
    
    Agent->>execute_mcp_tool: "google_sheets-add-row"
    execute_mcp_tool->>MCPClient: call_tool(params)
    MCPClient-->>execute_mcp_tool: "Connect: https://pipedream.com/..."
    
    execute_mcp_tool->>execute_mcp_tool: Detect Connect Link pattern
    execute_mcp_tool->>PDSession: Check for PENDING session<br/>(agent, app_slug)
    
    alt Existing valid session
        PDSession-->>execute_mcp_tool: Reuse connect_link_url
    else No valid session
        execute_mcp_tool->>create_connect_session: (agent, "google_sheets")
        create_connect_session->>PDSession: Create PENDING session<br/>with webhook_secret
        create_connect_session->>PDAPI: POST /v1/connect/{project}/tokens
        PDAPI-->>create_connect_session: {token, connect_link_url, expires_at}
        create_connect_session->>PDSession: Save connect_token, link, expiry
        PDSession-->>execute_mcp_tool: connect_link_url
    end
    
    execute_mcp_tool-->>Agent: {"status": "action_required",<br/>"connect_url": "..."}
    Agent->>User: Send connect_url via email/chat
    User->>User: Click link, authorize app
    User->>PDAPI: OAuth authorization
    PDAPI->>Webhook: POST /api/v1/webhooks/pipedream/connect/{session_id}/<br/>?t={webhook_secret}
    Webhook->>PDSession: Update status=SUCCESS,<br/>account_id
    Webhook->>Webhook: process_agent_events_task.delay(agent_id)
    Webhook-->>PDAPI: 200 OK
```

**Key Components:**

| Entity | Purpose | Location |
|--------|---------|----------|
| `create_connect_session()` | Generate Pipedream Connect token and session | [api/integrations/pipedream_connect.py:29-140]() |
| `PipedreamConnectSession` | DB model tracking OAuth sessions | [api/models.py]() |
| `pipedream_connect_webhook` | Webhook handler for authorization callbacks | [api/webhooks.py]() |
| `_pd_build_headers()` | Build per-agent, per-app Pipedream headers | [api/agent/tools/mcp_manager.py:683-696]() |

**Session Lifecycle:**

1. **Detection:** `execute_mcp_tool()` detects Pipedream connect link in tool result [api/agent/tools/mcp_manager.py:468-599]()
2. **Reuse Check:** Query for existing `PENDING` session with `expires_at` > now + 30s buffer
3. **Token Creation:** If no valid session, call `create_connect_session()` which posts to Pipedream API
4. **Session Persistence:** Store `connect_token`, `connect_link_url`, `webhook_secret`, and `expires_at`
5. **User Authorization:** Agent sends link to user via email/chat/web
6. **Webhook Callback:** Pipedream POSTs to `/api/v1/webhooks/pipedream/connect/{session_id}/?t={secret}`
7. **Agent Wake:** Webhook handler triggers `process_agent_events_task.delay()` to resume agent

**Session Statuses:**

| Status | Meaning |
|--------|---------|
| `PENDING` | Session created, awaiting user authorization |
| `SUCCESS` | User authorized, credentials available |
| `ERROR` | Link expired before delivery or authorization failed |

**Sources:** [api/integrations/pipedream_connect.py:29-140](), [api/agent/tools/mcp_manager.py:468-599](), [tests/unit/test_pipedream_connect.py:22-141]()

---

## Browser Automation

Browser automation tasks execute in separate Celery workers with persistent Chrome profiles and proxy support.

### Browser Task Execution Architecture

```mermaid
graph TB
    subgraph "Event Processing"
        EventLoop["_run_agent_loop()"]
        ToolCall["LLM returns<br/>browse_web tool call"]
        CreateTask["Create BrowserUseAgentTask<br/>(DB)"]
    end
    
    subgraph "Celery Worker"
        BrowserTask["process_browser_use_task"]
        ProfileRestore["Profile Restore from S3<br/>_profile_storage_key()"]
        ProxySelect["select_proxy_for_task()"]
        SessionInit["BrowserSession.start()"]
        AgentRun["BUAgent.run()"]
        ProfileSave["Profile Prune & Save<br/>_prune_chrome_profile()"]
        FollowUp["_schedule_agent_follow_up()"]
    end
    
    subgraph "Storage"
        S3["S3 / Local Storage<br/>browser_profiles/{uuid}.tar.zst"]
        DB["BrowserUseAgentTask<br/>BrowserUseAgentTaskStep"]
    end
    
    subgraph "Network"
        Proxy["ProxyServer<br/>(DB)"]
        Web["Target Website"]
    end
    
    EventLoop --> ToolCall
    ToolCall --> CreateTask
    CreateTask --> DB
    CreateTask -.delay.-> BrowserTask
    
    BrowserTask --> ProfileRestore
    ProfileRestore --> S3
    BrowserTask --> ProxySelect
    ProxySelect --> Proxy
    BrowserTask --> SessionInit
    SessionInit --> Web
    SessionInit --> AgentRun
    AgentRun --> DB
    AgentRun --> ProfileSave
    ProfileSave --> S3
    AgentRun --> FollowUp
    FollowUp -.delay.-> EventLoop
```

**Key Functions:**

| Function | Purpose | Location |
|----------|---------|----------|
| `process_browser_use_task` | Main Celery task executing browser automation | [api/tasks/browser_agent_tasks.py:972-1130]() |
| `_run_agent()` | Async wrapper setting up browser session and executing BUAgent | [api/tasks/browser_agent_tasks.py:542-965]() |
| `select_proxy_for_task()` | Select proxy based on agent preferences and health checks | [api/tasks/browser_agent_tasks.py:408-447]() |
| `_profile_storage_key()` | Generate sharded S3 key for browser profile | [api/tasks/browser_agent_tasks.py:502-512]() |
| `_prune_chrome_profile()` | Remove cache/temp files from profile before persistence | [api/tasks/browser_agent_tasks.py:199-273]() |
| `_schedule_agent_follow_up()` | Trigger agent event processing after task completion | [api/tasks/browser_agent_tasks.py:72-153]() |

**Profile Persistence Flow:**

1. **Restore:** On task start, check if `browser_profiles/{shard1}/{shard2}/{uuid}.tar.zst` exists in storage
2. **Extract:** If found, decompress with zstandard and extract tar to temp directory
3. **Execute:** Run browser automation with profile directory
4. **Prune:** Remove cache directories and temp files to reduce size [api/tasks/browser_agent_tasks.py:199-273]()
5. **Compress:** Create tar.zst archive with compression level 3
6. **Upload:** Save to storage with hierarchical key sharding

**Profile Sharding:** Uses first 4 hex chars of UUID for two-level directory sharding to avoid millions of objects in a single prefix. Example: `123e4567-e89b-12d3-...` → `browser_profiles/12/3e/123e4567-e89b-12d3-....tar.zst`

**Sources:** [api/tasks/browser_agent_tasks.py:542-965](), [api/tasks/browser_agent_tasks.py:199-273](), [api/tasks/browser_agent_tasks.py:502-512]()

### Browser Task Follow-Up

After browser task completion, agents can either continue the same budget cycle or start fresh:

```mermaid
graph TD
    A["BrowserUseAgentTask completes"]
    B["_schedule_agent_follow_up()"]
    C["AgentBudgetManager.get_cycle_status()"]
    D{Status == 'active' AND<br/>active_id == budget_id?}
    E["process_agent_events_task.delay()<br/>(with budget_id, branch_id, depth)"]
    F["process_agent_events_task.delay()<br/>(no budget context)"]
    
    A --> B
    B --> C
    C --> D
    D -->|Yes| E
    D -->|No| F
    
    E -->|"Continue same<br/>budget cycle"| G["Agent resumes with<br/>existing context"]
    F -->|"Start fresh<br/>budget cycle"| H["Agent starts new<br/>event processing"]
```

**Budget Cycle Logic:**

- If the original budget cycle is still `active` and matches the task's `budget_id`, the follow-up continues the same cycle
- Otherwise, a fresh event processing is triggered without budget context
- This prevents agents from resuming expired or closed budget cycles

**Sources:** [api/tasks/browser_agent_tasks.py:72-153](), [tests/unit/test_browser_task_follow_up.py:1-89]()

---

## LLM Provider Integration

The platform uses a database-backed multi-tier failover system for LLM provider selection based on token count.

### Token-Based Tier Selection

```mermaid
graph TD
    A["get_llm_config_with_failover()<br/>(token_count)"]
    B["Query PersistentTokenRange<br/>WHERE min_tokens <= count<br/>AND max_tokens > count"]
    C{Token Range<br/>Found?}
    D["Query PersistentLLMTier<br/>ORDER BY order"]
    E["For each tier, query<br/>PersistentTierEndpoint"]
    F{Endpoint enabled<br/>& has API key?}
    G["Build failover_configs<br/>List[(endpoint_key, model, params)]"]
    H["Weighted random selection<br/>within tier"]
    I["Raise LLMNotConfiguredError"]
    
    A --> B
    B --> C
    C -->|Yes| D
    C -->|No| I
    D --> E
    E --> F
    F -->|Yes| G
    F -->|No| E
    G --> H
    H -->|Return| J["Return ordered list of<br/>(endpoint, model, params)"]
```

**Database Schema:**

| Model | Purpose | Key Fields |
|-------|---------|-----------|
| `PersistentTokenRange` | Define token ranges (e.g., 0-7500, 7500-20000) | `min_tokens`, `max_tokens` |
| `PersistentLLMTier` | Define failover tiers within a token range | `token_range`, `order` |
| `PersistentTierEndpoint` | Link endpoints to tiers with weights | `tier`, `endpoint`, `weight` |
| `PersistentModelEndpoint` | Specific model configurations | `provider`, `litellm_model`, `api_base`, `supports_vision` |
| `LLMProvider` | Provider credentials and settings | `key`, `api_key_encrypted`, `env_var_name`, `browser_backend` |

**Configuration Flow:**

1. **Token Estimation:** Before LLM call, estimate tokens via `_estimate_agent_context_tokens()` 
2. **Range Selection:** Query `PersistentTokenRange` to find matching range
3. **Tier Iteration:** Load tiers for range ordered by `order` field
4. **Endpoint Filtering:** For each tier, load enabled endpoints with valid API keys
5. **Weighted Selection:** Use `random.choices()` with endpoint weights for load balancing
6. **Failover List:** Return all usable endpoints across tiers in priority order

**API Key Resolution:** Endpoints prefer encrypted admin keys from `LLMProvider.api_key_encrypted`, falling back to environment variables specified in `env_var_name`.

**Sources:** [api/agent/core/llm_config.py:235-401](), [tests/utils/llm_seed.py:18-87]()

### LLM Failover Execution

```mermaid
sequenceDiagram
    participant Agent
    participant completion as "_completion_with_failover()"
    participant litellm as "litellm.completion()"
    participant Tier1 as "Tier 1 Endpoint"
    participant Tier2 as "Tier 2 Endpoint"
    
    Agent->>completion: (messages, tools, failover_configs)
    completion->>completion: Extract first config from list
    completion->>litellm: (model, messages, tools, **params)
    litellm->>Tier1: API request
    
    alt Success
        Tier1-->>litellm: Response
        litellm-->>completion: Response
        completion-->>Agent: Success
    else Failure
        Tier1-->>litellm: Error
        litellm-->>completion: Exception
        completion->>completion: Pop failed config, try next
        completion->>litellm: (next_model, messages, tools, **next_params)
        litellm->>Tier2: API request
        Tier2-->>litellm: Response
        litellm-->>completion: Response
        completion-->>Agent: Success (after failover)
    end
```

**Failover Logic:**

- `_completion_with_failover()` receives pre-computed `failover_configs` list
- Tries each config in order until success or exhaustion
- Removes internal hints (`supports_tool_choice`, `use_parallel_tool_calls`, `supports_vision`) before passing to litellm
- Logs failures and advances to next tier
- For providers like OpenAI, adds `parallel_tool_calls` and `drop_params` flags

**Sources:** [api/agent/core/event_processing.py](), [tests/unit/test_event_processing_llm_selection.py:22-84]()

---

## Configuration

### MCP Server Configuration

MCP servers are configured in `MCPToolManager.AVAILABLE_SERVERS`:

```python
AVAILABLE_SERVERS = [
    MCPServer(
        name="brightdata",
        display_name="Bright Data",
        command="npx",
        args=["-y", "@brightdata/mcp@2.5.0"],
        env={"API_TOKEN": os.getenv("BRIGHT_DATA_TOKEN", "")},
        enabled=True
    ),
    MCPServer(
        name="pipedream",
        display_name="Pipedream",
        url="https://remote.mcp.pipedream.net",
        env={},
        headers={},
        enabled=True
    ),
]
```

**Environment Variables:**

| Variable | Purpose | Used By |
|----------|---------|---------|
| `BRIGHT_DATA_TOKEN` | API token for Bright Data MCP server | stdio transport |
| `BRIGHT_DATA_WEB_UNLOCKER_ZONE` | Optional zone configuration for web unlocker | Bright Data server |
| `PIPEDREAM_CLIENT_ID` | OAuth client ID | Pipedream authentication |
| `PIPEDREAM_CLIENT_SECRET` | OAuth client secret | Pipedream authentication |
| `PIPEDREAM_PROJECT_ID` | Pipedream project identifier | Connect API calls |
| `PIPEDREAM_ENVIRONMENT` | Environment (development/production) | Connect headers |
| `PIPEDREAM_PREFETCH_APPS` | Comma-separated app slugs to prefetch | Tool discovery |

**Sources:** [api/agent/tools/mcp_manager.py:82-113]()

### Tool Blacklist

Tools matching glob patterns in `TOOL_BLACKLIST` are excluded from discovery:

```python
TOOL_BLACKLIST = [
    "mcp_brightdata_scraping_browser_*",  # Blacklist all scraping browser tools
    "select_apps"
]
```

**Sources:** [api/agent/tools/mcp_manager.py:121-127]()

### Browser Configuration

Browser automation settings:

| Setting | Default | Purpose |
|---------|---------|---------|
| `BROWSER_HEADLESS` | `True` | Run Chrome in headless mode |
| `ALLOW_FILE_UPLOAD` | `False` | Enable file uploads from agent filespace |
| `ALLOW_FILE_DOWNLOAD` | `False` | Enable file downloads to agent filespace |
| `CHROME_PROFILE_MAX_SIZE_BYTES` | 500 MB | Reset profile if exceeds after pruning |

**Sources:** [api/tasks/browser_agent_tasks.py:196-273](), [api/tasks/browser_agent_tasks.py:704-723]()

---

## Integration Patterns

### Tool Discovery Pattern

Agents discover tools via natural language queries:

```python
# Agent calls search_tools via LLM tool call
result = search_tools(agent, "send emails via Gmail")

# Returns:
{
    "status": "success",
    "message": "Enabled: gmail-send-email, gmail-get-thread",
    "enabled_tools": ["gmail-send-email", "gmail-get-thread"],
    "already_enabled": [],
    "evicted": [],
    "invalid": []
}
```

The LLM analyzes a compact catalog and calls the internal `enable_tools()` function to enable all relevant tools in one step, avoiding multiple round-trips.

**Sources:** [api/agent/tools/mcp_manager.py:738-901]()

### Tool Execution Pattern

After enablement, tools are executed directly:

```python
result = _mcp_manager.execute_mcp_tool(
    agent=agent,
    tool_name="gmail-send-email",
    params={"to": "user@example.com", "subject": "Hello", "body": "..."}
)

# Returns:
{
    "status": "success",
    "result": "Email sent successfully with ID: <msg_id>"
}

# Or if OAuth required:
{
    "status": "action_required",
    "result": "Authorization required. Please connect your account via: https://...",
    "connect_url": "https://example.com/connect?token=..."
}
```

**Sources:** [api/agent/tools/mcp_manager.py:397-608]()

### Browser Automation Pattern

Browser tasks are created and execute asynchronously:

```python
# In event processing loop
task = BrowserUseAgentTask.objects.create(
    agent=browser_use_agent,
    user=user,
    prompt="Navigate to example.com and extract the title",
    budget_id=budget_id,
    branch_id=branch_id,
    depth=depth
)

# Trigger async execution
process_browser_use_task.delay(str(task.id))

# Worker executes, then triggers follow-up
_schedule_agent_follow_up(task, budget_id=budget_id, branch_id=branch_id, depth=depth)
```

**Sources:** [api/tasks/browser_agent_tasks.py:972-1130](), [api/tasks/browser_agent_tasks.py:72-153]()

---

## Limitations and Constraints

### MCP Tool Limits

- **40-Tool Cap:** Each agent can enable maximum 40 MCP tools (enforced via LRU eviction)
- **No Nested Clients:** Pipedream clients are cached per (agent_id, app_slug, mode) to avoid connection leaks
- **Blacklist Enforcement:** Blacklisted tools cannot be enabled or executed

**Sources:** [api/agent/tools/mcp_manager.py:40](), [api/agent/tools/mcp_manager.py:904-985]()

### Browser Automation Limits

- **Profile Size:** Chrome profiles exceeding 500 MB after pruning are reset to avoid storage bloat
- **Single Session:** Only one browser session per task (no parallel sessions)
- **Proxy Dependency:** Tasks may fail if no healthy proxy available and debug mode disabled

**Sources:** [api/tasks/browser_agent_tasks.py:196-273](), [api/tasks/browser_agent_tasks.py:408-447]()

### LLM Integration Limits

- **Bootstrap Required:** Platform requires at least one configured endpoint before agents can run
- **No Dynamic Key Rotation:** API keys are loaded at config time, not per-request
- **Tier Exhaustion:** If all endpoints in all tiers fail, the completion fails (no infinite retry)

**Sources:** [api/agent/core/llm_config.py:394-401](), [api/agent/core/llm_config.py:450-466]()

---

## Testing

The codebase includes comprehensive tests for each integration system:

| Test Suite | Coverage | File |
|------------|----------|------|
| MCP Tool Management | Discovery, enablement, LRU eviction, blacklist | [tests/unit/test_mcp_tools.py]() |
| Pipedream Connect | OAuth flow, session reuse, webhook callbacks | [tests/unit/test_pipedream_connect.py]() |
| Pipedream Greenhouse | App-specific OAuth, discovery headers | [tests/unit/test_pipedream_greenhouse.py]() |
| Pipedream Trello | Trello-specific OAuth and tool discovery | [tests/unit/test_pipedream_trello.py]() |
| LLM Failover | Token-based selection, weighted distribution | [tests/unit/test_llm_failover.py]() |
| Browser Task Follow-Up | Budget cycle continuation logic | [tests/unit/test_browser_task_follow_up.py]() |

**Test Utilities:**

- `seed_persistent_basic()` - Seeds minimal LLM configuration for DB-only tests
- `clear_llm_db()` - Cleans up LLM configuration tables

**Sources:** [tests/unit/test_mcp_tools.py:1-711](), [tests/utils/llm_seed.py:4-87](), [tests/unit/test_browser_task_follow_up.py:1-89]()

---

# Page: MCP Tools

# MCP Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/tools/mcp_manager.py](api/agent/tools/mcp_manager.py)
- [api/integrations/pipedream_connect.py](api/integrations/pipedream_connect.py)
- [api/migrations/0127_pipedream_connect_session.py](api/migrations/0127_pipedream_connect_session.py)
- [api/migrations/0137_add_trello_tool_friendly_names.py](api/migrations/0137_add_trello_tool_friendly_names.py)
- [tests/unit/test_pipedream_connect.py](tests/unit/test_pipedream_connect.py)
- [tests/unit/test_pipedream_greenhouse.py](tests/unit/test_pipedream_greenhouse.py)
- [tests/unit/test_pipedream_trello.py](tests/unit/test_pipedream_trello.py)

</details>



## Purpose and Scope

This document describes the **Model Context Protocol (MCP) tool integration system**, which enables persistent agents to dynamically discover, enable, and execute external tools from multiple MCP servers. The system provides access to web scraping (Bright Data) and 2,800+ API integrations (Pipedream Connect) through a unified interface.

For information about browser automation tasks, see [Browser Automation](#6.2). For LLM provider configuration, see [LLM Integration](#6.3).

---

## Overview

The MCP tool system allows agents to:

1. **Discover tools dynamically** via natural language queries analyzed by an LLM
2. **Enable/disable tools** with automatic LRU eviction when the 40-tool per-agent limit is reached
3. **Execute tools** with automatic credential management for OAuth-enabled Pipedream apps
4. **Manage multiple server types**: stdio-based (Bright Data) and HTTP/SSE-based (Pipedream)

The core implementation is in `MCPToolManager`, which maintains client connections, caches discovered tools, and routes execution requests to the appropriate server.

**Sources:** [api/agent/tools/mcp_manager.py:1-40]()

---

## System Architecture

### Core Components

```mermaid
graph TB
    subgraph "Agent Layer"
        Agent["PersistentAgent"]
        EnabledTools["PersistentAgentEnabledTool<br/>(max 40 per agent)"]
    end
    
    subgraph "MCP Manager"
        Manager["MCPToolManager<br/>_mcp_manager (singleton)"]
        ToolsCache["_tools_cache<br/>Dict[server_name, List[MCPToolInfo]]"]
        Clients["_clients<br/>Dict[server_name, Client]"]
        PDClients["_pd_agent_clients<br/>Dict[agent_key, Client]"]
    end
    
    subgraph "MCP Servers"
        BrightData["Bright Data<br/>stdio: npx @brightdata/mcp"]
        Pipedream["Pipedream<br/>HTTP/SSE: remote.mcp.pipedream.net"]
    end
    
    subgraph "Pipedream Connect"
        PDSession["PipedreamConnectSession<br/>- connect_token<br/>- webhook_secret<br/>- account_id"]
        PDAuth["OAuth Flow<br/>create_connect_session()"]
    end
    
    subgraph "Discovery & Enablement"
        SearchTool["search_tools()<br/>LLM-driven discovery"]
        EnableTool["enable_mcp_tool()<br/>LRU eviction if needed"]
        DisableTool["disable_mcp_tool()"]
    end
    
    Agent --> EnabledTools
    Agent --> SearchTool
    SearchTool --> Manager
    EnableTool --> Manager
    EnableTool --> EnabledTools
    
    Manager --> ToolsCache
    Manager --> Clients
    Manager --> PDClients
    
    Clients --> BrightData
    Clients --> Pipedream
    PDClients --> Pipedream
    
    Pipedream -.->|requires auth| PDAuth
    PDAuth --> PDSession
    PDSession -.->|wake agent| Agent
```

**Sources:** [api/agent/tools/mcp_manager.py:78-735](), [api/integrations/pipedream_connect.py:1-141](), [api/models.py]()

---

## MCP Server Configuration

### Available Servers

The platform supports two types of MCP servers:

| Server Name | Type | Transport | URL/Command | Description |
|-------------|------|-----------|-------------|-------------|
| `brightdata` | stdio | StdioTransport | `npx -y @brightdata/mcp@2.5.0` | Web scraping with CAPTCHA bypass, search engine |
| `pipedream` | HTTP/SSE | StreamableHttpTransport | `https://remote.mcp.pipedream.net` | 2,800+ API integrations (Google Sheets, Greenhouse, Trello, etc.) |

**Sources:** [api/agent/tools/mcp_manager.py:82-113]()

### Server Dataclass Structure

```python
@dataclass
class MCPServer:
    name: str
    display_name: str
    description: str
    command: Optional[str] = None      # For stdio servers
    args: Optional[List[str]] = None
    url: Optional[str] = None          # For HTTP/SSE servers
    env: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    prefetch_apps: Optional[List[str]] = None  # Pipedream only
    enabled: bool = True
```

**Sources:** [api/agent/tools/mcp_manager.py:43-56]()

### Bright Data Configuration

Bright Data is configured as a stdio server with environment variables:

- `API_TOKEN`: Required authentication token from `BRIGHT_DATA_TOKEN` setting
- `NPM_CONFIG_CACHE`: Cache directory (default: `/tmp/.npm`)
- `PRO_MODE`: Set to `"true"` to enable full tool catalog
- `WEB_UNLOCKER_ZONE`: Optional zone configuration from `BRIGHT_DATA_WEB_UNLOCKER_ZONE`

**Sources:** [api/agent/tools/mcp_manager.py:83-101]()

### Pipedream Configuration

Pipedream is configured as an HTTP/SSE server requiring:

- `PIPEDREAM_CLIENT_ID`: OAuth client ID
- `PIPEDREAM_CLIENT_SECRET`: OAuth client secret
- `PIPEDREAM_PROJECT_ID`: Project identifier
- `PIPEDREAM_ENVIRONMENT`: Deployment environment (e.g., `"development"`)
- `PIPEDREAM_PREFETCH_APPS`: Comma-separated app slugs to discover at initialization (default: `"google_sheets,greenhouse"`)

**Sources:** [api/agent/tools/mcp_manager.py:102-112](), [api/agent/tools/mcp_manager.py:176-188]()

---

## Tool Discovery and Enablement

### Discovery Flow

```mermaid
sequenceDiagram
    participant Agent as "PersistentAgent"
    participant SearchFn as "search_tools()"
    participant Manager as "MCPToolManager"
    participant LLM as "LLM Provider"
    participant DB as "Database"
    
    Agent->>SearchFn: Natural language query<br/>"find tools to create spreadsheets"
    SearchFn->>Manager: get_all_available_tools()
    Manager-->>SearchFn: List[MCPToolInfo]
    
    SearchFn->>SearchFn: Build compact catalog<br/>- Strip markdown links<br/>- Summarize params<br/>- Truncate descriptions
    
    SearchFn->>LLM: System: "You are a tool discovery assistant"<br/>User: Query + Tool catalog<br/>Functions: [enable_tools]
    
    LLM-->>SearchFn: Tool call: enable_tools(<br/>["google_sheets-add-single-row",<br/> "google_sheets-create-spreadsheet"])
    
    SearchFn->>Manager: For each selected tool
    Manager->>DB: Check enabled count
    
    alt Count >= 40
        Manager->>DB: Evict oldest by last_used_at
    end
    
    Manager->>DB: Create PersistentAgentEnabledTool
    Manager->>DB: Update last_used_at = now
    
    SearchFn-->>Agent: Success with tool list
```

**Sources:** [api/agent/tools/mcp_manager.py:738-897]()

### Tool Catalog Format

The discovery system prepares a compact, plain-text catalog to minimize LLM token usage:

```
- google_sheets-add-single-row: Add a row to a Google Sheet | params: spreadsheetId*:string, sheetName:string, values*:array +2 more
- greenhouse-create-candidate: Create a new candidate in Greenhouse | params: first_name*:string, last_name*:string, email:string
- trello-create-card: Create a card on a Trello board | params: name*:string, idList*:string, desc:string
```

**Implementation details:**
- Markdown links `[text](url)` are stripped: [api/agent/tools/mcp_manager.py:773-774]()
- URLs are removed: [api/agent/tools/mcp_manager.py:775-776]()
- Descriptions truncated to 180 chars: [api/agent/tools/mcp_manager.py:770-778]()
- Parameters summarized to first 6, with required params marked with `*`: [api/agent/tools/mcp_manager.py:780-799]()

**Sources:** [api/agent/tools/mcp_manager.py:769-821]()

### LRU Eviction Policy

When an agent reaches the 40-tool limit (`MAX_MCP_TOOLS`), the system evicts the **least recently used** tool:

```python
MAX_MCP_TOOLS = 40
```

**Eviction logic:**
1. Query current enabled tool count for agent
2. If count >= 40, find tool with oldest `last_used_at` timestamp
3. Delete that `PersistentAgentEnabledTool` record
4. Proceed with new tool enablement

**Sources:** [api/agent/tools/mcp_manager.py:40](), [api/agent/tools/mcp_manager.py:925-940]()

---

## Tool Blacklisting

The system maintains a blacklist of tool patterns that should not be discovered or executed:

```python
TOOL_BLACKLIST = [
    "mcp_brightdata_scraping_browser_*",  # Glob pattern
    "select_apps"
]
```

Blacklist matching uses `fnmatch` glob-style patterns. Tools matching any pattern are:
- Excluded during server tool discovery: [api/agent/tools/mcp_manager.py:328-330]()
- Rejected during execution with error response: [api/agent/tools/mcp_manager.py:401-406]()

**Sources:** [api/agent/tools/mcp_manager.py:121-127](), [api/agent/tools/mcp_manager.py:150-156]()

---

## Tool Naming Conventions

### Prefixed vs Unprefixed

| Server Type | Naming Convention | Example |
|-------------|-------------------|---------|
| Bright Data | `mcp_{server}_{tool}` | `mcp_brightdata_scrape_as_markdown` |
| Pipedream | Unprefixed | `google_sheets-add-single-row` |

**Rationale:** Pipedream tools are not prefixed to avoid excessively long names like `mcp_pipedream_google_sheets-add-single-row`.

**Sources:** [api/agent/tools/mcp_manager.py:315-342]()

---

## Tool Execution

### Execution Flow

```mermaid
sequenceDiagram
    participant Agent as "Agent Loop"
    participant Manager as "MCPToolManager"
    participant DB as "Database"
    participant Client as "MCP Client"
    participant PDConnect as "Pipedream Connect"
    
    Agent->>Manager: execute_mcp_tool(agent, tool_name, params)
    
    Manager->>Manager: Check blacklist
    alt Blacklisted
        Manager-->>Agent: Error: Tool blacklisted
    end
    
    Manager->>DB: Check PersistentAgentEnabledTool exists
    alt Not enabled
        Manager-->>Agent: Error: Tool not enabled
    end
    
    Manager->>DB: Update last_used_at, usage_count
    
    Manager->>Manager: _resolve_tool(tool_name)<br/>→ (server_name, actual_tool_name)
    
    alt server_name == "pipedream"
        Manager->>Manager: _pd_parse_tool(tool_name)<br/>→ (app_slug, mode)
        Manager->>Manager: _get_pipedream_agent_client(agent, app_slug, mode)
    else Other servers
        Manager->>Manager: Use cached _clients[server_name]
    end
    
    Manager->>Client: call_tool(actual_tool_name, params)
    
    alt Result contains Connect Link
        Manager->>PDConnect: Detect "pipedream.com/_static/connect.html"
        Manager->>PDConnect: create_connect_session(agent, app_slug)
        PDConnect-->>Manager: (session, first_party_url)
        Manager-->>Agent: action_required<br/>+ connect_url
    else Normal result
        Manager-->>Agent: success + result content
    end
```

**Sources:** [api/agent/tools/mcp_manager.py:397-608]()

### Usage Tracking

On each tool execution, the system updates:

```python
row.last_used_at = datetime.now(UTC)
row.usage_count = (row.usage_count or 0) + 1
row.save(update_fields=["last_used_at", "usage_count"])
```

This enables LRU eviction and usage analytics.

**Sources:** [api/agent/tools/mcp_manager.py:416-424]()

---

## Pipedream Connect OAuth Flow

### Architecture

Pipedream tools requiring user-specific credentials (e.g., Google Sheets, Greenhouse, Trello) use **Pipedream Connect**, which implements a delegated OAuth flow.

```mermaid
graph TB
    subgraph "Initial Tool Call"
        ToolCall["Agent calls<br/>google_sheets-add-single-row"]
        MCPServer["Pipedream MCP Server"]
        PassThruLink["Response contains<br/>pipedream.com/_static/connect.html?token=xyz"]
    end
    
    subgraph "First-Party Connect Session"
        DetectLink["MCPToolManager detects<br/>Connect Link pattern"]
        CheckExisting["Query PipedreamConnectSession<br/>status=PENDING, app_slug=google_sheets"]
        
        CreateSession["create_connect_session(agent, app_slug)"]
        PDAPI["POST /v1/connect/{project}/tokens<br/>- external_user_id=agent.id<br/>- webhook_uri=https://domain/api/v1/webhooks/pipedream/connect/{session.id}/?t={secret}"]
        
        StoreSession["PipedreamConnectSession<br/>- connect_token<br/>- connect_link_url<br/>- webhook_secret<br/>- expires_at"]
        
        AppendApp["Append &app=google_sheets<br/>to final URL"]
        ReturnAction["Return action_required<br/>+ connect_url"]
    end
    
    subgraph "User Authorization"
        UserClick["User clicks connect_url<br/>in chat/email"]
        PipedreamOAuth["Pipedream OAuth flow<br/>User grants permissions"]
        Webhook["Webhook: CONNECTION_SUCCESS<br/>POST /api/v1/webhooks/pipedream/connect/{session.id}/?t={secret}"]
        UpdateStatus["Update session.status=SUCCESS<br/>session.account_id=apn_xxx"]
        WakeAgent["process_agent_events_task.delay(agent.id)"]
    end
    
    subgraph "Retry with Credentials"
        AgentResume["Agent resumes execution"]
        PDClient["Per-agent Pipedream client<br/>x-pd-external-user-id=agent.id<br/>x-pd-account-id available"]
        ToolSuccess["Tool executes with<br/>user's Google account"]
    end
    
    ToolCall --> MCPServer
    MCPServer --> PassThruLink
    PassThruLink --> DetectLink
    DetectLink --> CheckExisting
    
    CheckExisting -->|No valid session| CreateSession
    CheckExisting -->|Valid session exists| AppendApp
    
    CreateSession --> PDAPI
    PDAPI --> StoreSession
    StoreSession --> AppendApp
    AppendApp --> ReturnAction
    
    ReturnAction --> UserClick
    UserClick --> PipedreamOAuth
    PipedreamOAuth --> Webhook
    Webhook --> UpdateStatus
    UpdateStatus --> WakeAgent
    
    WakeAgent --> AgentResume
    AgentResume --> PDClient
    PDClient --> ToolSuccess
```

**Sources:** [api/agent/tools/mcp_manager.py:468-599](), [api/integrations/pipedream_connect.py:29-141]()

### Connect Link Detection

The system detects Pipedream Connect Links using pattern matching:

```python
if isinstance(content, dict):
    for v in content.values():
        if isinstance(v, str) and "pipedream.com/_static/connect.html" in v:
            connect_url = v
            break
elif isinstance(content, str) and "pipedream.com/_static/connect.html" in content:
    connect_url = content
```

**Sources:** [api/agent/tools/mcp_manager.py:470-477]()

### Session Reuse Logic

To avoid creating redundant Connect Links:

1. Query for existing `PipedreamConnectSession` with:
   - Same `agent`
   - Same `app_slug`
   - `status=PENDING`
   - Non-empty `connect_link_url`
2. Check if `expires_at > now + EFFECTIVE_EXPIRATION_BUFFER_SECONDS` (30 seconds)
3. If valid, reuse the existing `connect_link_url`
4. Otherwise, mark session as `ERROR` and create a new one

**Sources:** [api/agent/tools/mcp_manager.py:511-551](), [api/integrations/pipedream_connect.py:20-21]()

### Expired Link Handling

If a Connect Link has expired before it can be delivered to the user:

```python
if expires_at and expires_at <= now + timedelta(seconds=EFFECTIVE_EXPIRATION_BUFFER_SECONDS):
    logger.warning("PD Connect: token expired before delivery")
    session.status = PipedreamConnectSession.Status.ERROR
    session.save(update_fields=["status", "updated_at"])
    return session, None
```

The system returns `action_required` with a message explaining the link expired, prompting the agent to request a new one.

**Sources:** [api/integrations/pipedream_connect.py:119-128](), [api/agent/tools/mcp_manager.py:569-580]()

---

## Per-Agent Pipedream Clients

Pipedream maintains separate client connections **per agent per app slug** to ensure credential isolation:

### Client Cache Key

```python
cache_key = f"{agent.id}:{app_slug or ''}:{mode}"
```

**Example:** Agent `123` accessing Google Sheets in sub-agent mode has cache key `"123:google_sheets:sub-agent"`

**Sources:** [api/agent/tools/mcp_manager.py:706-729]()

### Headers for Per-Agent Clients

```python
headers = {
    "Authorization": f"Bearer {token}",
    "x-pd-project-id": PIPEDREAM_PROJECT_ID,
    "x-pd-environment": PIPEDREAM_ENVIRONMENT,
    "x-pd-external-user-id": str(agent.id),
    "x-pd-conversation-id": str(agent.id),
    "x-pd-app-discovery": "true",
    "x-pd-tool-mode": "sub-agent",
    "x-pd-app-slug": app_slug,
}
```

This allows Pipedream to route tool executions to the correct user account after OAuth completion.

**Sources:** [api/agent/tools/mcp_manager.py:683-696]()

---

## Tool Information Dataclass

```python
@dataclass 
class MCPToolInfo:
    full_name: str       # e.g., "google_sheets-add-single-row"
    server_name: str     # e.g., "pipedream"
    tool_name: str       # e.g., "google_sheets-add-single-row"
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    
    def to_search_dict(self) -> Dict[str, str]:
        """Convert to dictionary for LLM search context."""
        return {
            "name": self.full_name,
            "server": self.server_name,
            "tool": self.tool_name,
            "description": self.description,
            "parameters": json.dumps(self.parameters) if self.parameters else "{}",
        }
```

**Sources:** [api/agent/tools/mcp_manager.py:58-75]()

---

## Default Enabled Tools

Certain tools are automatically enabled for all new agents:

```python
DEFAULT_ENABLED_TOOLS = [
    "mcp_brightdata_scrape_as_markdown",
]
```

This provides immediate web scraping capabilities without requiring explicit enablement.

**Sources:** [api/agent/tools/mcp_manager.py:115-119]()

---

## Token Management for Pipedream

### OAuth Client Credentials Flow

The system caches Pipedream access tokens with automatic refresh:

```python
def _get_pipedream_access_token(self) -> Optional[str]:
    # Reuse cached token if valid for at least 2 minutes
    if self._pd_access_token and self._pd_token_expiry and datetime.now(UTC) < (self._pd_token_expiry - timedelta(minutes=2)):
        return self._pd_access_token
    
    resp = requests.post(
        "https://api.pipedream.com/v1/oauth/token",
        json={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=15,
    )
    data = resp.json()
    self._pd_access_token = data.get("access_token")
    self._pd_token_expiry = datetime.now(UTC) + timedelta(seconds=expires_in)
```

**Sources:** [api/agent/tools/mcp_manager.py:649-681]()

---

## Initialization and Cleanup

### Initialization

```python
def initialize(self) -> bool:
    """Initialize all configured MCP servers and cache their tools."""
    if self._initialized:
        return True
    
    success_count = 0
    for server in self.AVAILABLE_SERVERS:
        if not server.enabled:
            continue
        
        # Validate required environment variables
        # ...
        
        try:
            self._register_server(server)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to register MCP server '{server.name}': {e}")
    
    self._initialized = success_count > 0
    return self._initialized
```

**Sources:** [api/agent/tools/mcp_manager.py:158-197]()

### Cleanup

```python
def cleanup(self):
    """Clean up resources."""
    for c in self._pd_agent_clients.values():
        try:
            c.close()
        except Exception:
            pass
    self._pd_agent_clients.clear()
    self._clients.clear()
    self._tools_cache.clear()
    if self._loop and not self._loop.is_closed():
        self._loop.close()
    self._initialized = False
```

**Sources:** [api/agent/tools/mcp_manager.py:615-628]()

---

## Database Models

### PersistentAgentEnabledTool

Tracks which tools are enabled for each agent:

| Field | Type | Description |
|-------|------|-------------|
| `agent` | ForeignKey | Reference to `PersistentAgent` |
| `tool_full_name` | CharField | Full tool name (e.g., `"google_sheets-add-single-row"`) |
| `last_used_at` | DateTimeField | Timestamp of most recent execution |
| `usage_count` | IntegerField | Total number of executions |
| `created_at` | DateTimeField | When tool was enabled |

**Unique constraint:** `(agent, tool_full_name)`

**Sources:** [api/models.py]()

### PipedreamConnectSession

Manages Pipedream Connect OAuth sessions:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUIDField | Primary key |
| `agent` | ForeignKey | Reference to `PersistentAgent` |
| `app_slug` | CharField | App identifier (e.g., `"google_sheets"`) |
| `external_user_id` | CharField | Agent ID for Pipedream |
| `conversation_id` | CharField | Agent ID for Pipedream |
| `connect_token` | CharField | Pipedream Connect token |
| `connect_link_url` | TextField | OAuth authorization URL |
| `webhook_secret` | CharField | Secret for webhook validation |
| `expires_at` | DateTimeField | Token expiration |
| `status` | CharField | `PENDING` / `SUCCESS` / `ERROR` |
| `account_id` | CharField | Pipedream account ID after auth |

**Sources:** [api/migrations/0127_pipedream_connect_session.py:1-52]()

---

## API Functions

### Core Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `search_tools()` | `agent: PersistentAgent`<br/>`query: str` | `Dict[str, Any]` | LLM-driven tool discovery |
| `enable_mcp_tool()` | `agent: PersistentAgent`<br/>`tool_name: str` | `Dict[str, Any]` | Enable tool with LRU eviction |
| `disable_mcp_tool()` | `agent: PersistentAgent`<br/>`tool_name: str` | `Dict[str, Any]` | Disable tool |
| `get_mcp_manager()` | None | `MCPToolManager` | Get singleton instance |

**Sources:** [api/agent/tools/mcp_manager.py:738-1001]()

### Manager Methods

| Method | Purpose |
|--------|---------|
| `initialize()` | Register all enabled MCP servers |
| `get_all_available_tools()` | Return all discovered tools across servers |
| `find_tool_by_name()` | Lookup tool by exact full name |
| `has_tool()` | Check if tool exists in catalog |
| `get_enabled_tools_definitions()` | Get OpenAI-format tool definitions for agent |
| `execute_mcp_tool()` | Execute enabled tool with params |
| `cleanup()` | Close connections and clear caches |

**Sources:** [api/agent/tools/mcp_manager.py:158-628]()

---

## Example: Tool Discovery and Execution

### Step 1: Agent Searches for Tools

Agent wants to create spreadsheets:

```
Agent calls: search_tools(agent, "find tools to create and update Google Sheets")
```

**LLM receives:**
```
Query: find tools to create and update Google Sheets

Available tools:
- google_sheets-add-single-row: Add a row to a Google Sheet | params: spreadsheetId*:string, sheetName:string, values*:array
- google_sheets-create-spreadsheet: Create a new Google Sheet | params: title*:string, sheetNames:array
- google_sheets-update-cell: Update a cell in Google Sheet | params: spreadsheetId*:string, range*:string, value*:string
...

Select the relevant tools and call enable_tools once with their exact full names.
```

**LLM response:**
```
Tool call: enable_tools(
  tool_names=[
    "google_sheets-add-single-row",
    "google_sheets-create-spreadsheet",
    "google_sheets-update-cell"
  ]
)
```

**Sources:** [api/agent/tools/mcp_manager.py:823-836]()

### Step 2: Tools Are Enabled

System creates `PersistentAgentEnabledTool` records:
- If agent has 38 enabled tools → all 3 new tools enabled
- If agent has 40 enabled tools → 3 oldest tools evicted, 3 new tools enabled

**Sources:** [api/agent/tools/mcp_manager.py:925-940]()

### Step 3: Agent Executes Tool

Agent attempts to create a spreadsheet:

```python
result = execute_mcp_tool(
    agent,
    "google_sheets-create-spreadsheet",
    {"title": "Q1 Revenue Report", "sheetNames": ["January", "February", "March"]}
)
```

**First execution (no OAuth):**
```json
{
  "status": "action_required",
  "result": "Authorization required. Please connect your account via: https://gobii.ai/connect?token=abc&app=google_sheets",
  "connect_url": "https://gobii.ai/connect?token=abc&app=google_sheets"
}
```

**After user authorizes, second execution:**
```json
{
  "status": "success",
  "result": {
    "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
  }
}
```

**Sources:** [api/agent/tools/mcp_manager.py:397-608]()

---

## Testing

### Test Coverage

The system includes comprehensive tests for:

1. **Basic discovery and enablement**: [tests/unit/test_mcp_manager.py]()
2. **Pipedream Connect session creation**: [tests/unit/test_pipedream_connect.py:22-92]()
3. **Webhook handling for OAuth completion**: [tests/unit/test_pipedream_connect.py:94-139]()
4. **Connect link rewriting**: [tests/unit/test_pipedream_connect.py:142-241]()
5. **Session reuse logic**: [tests/unit/test_pipedream_connect.py:243-296]()
6. **App-specific flows (Google Sheets, Greenhouse, Trello)**: [tests/unit/test_pipedream_greenhouse.py](), [tests/unit/test_pipedream_trello.py]()

**Sources:** [tests/unit/test_pipedream_connect.py:1-296](), [tests/unit/test_pipedream_greenhouse.py:1-163](), [tests/unit/test_pipedream_trello.py:1-152]()

---

## Configuration Reference

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `BRIGHT_DATA_TOKEN` | Yes (for Bright Data) | API authentication token |
| `BRIGHT_DATA_WEB_UNLOCKER_ZONE` | No | Optional zone override |
| `PIPEDREAM_CLIENT_ID` | Yes (for Pipedream) | OAuth client ID |
| `PIPEDREAM_CLIENT_SECRET` | Yes (for Pipedream) | OAuth client secret |
| `PIPEDREAM_PROJECT_ID` | Yes (for Pipedream) | Project identifier |
| `PIPEDREAM_ENVIRONMENT` | Yes (for Pipedream) | Environment name |
| `PIPEDREAM_PREFETCH_APPS` | No | Comma-separated app slugs (default: `"google_sheets,greenhouse"`) |

**Sources:** [api/agent/tools/mcp_manager.py:91-98](), [api/agent/tools/mcp_manager.py:176-188]()

---

## Logging and Observability

The system uses OpenTelemetry tracing for key operations:

```python
@tracer.start_as_current_span("AGENT TOOL Search Tools")
def search_tools(agent: PersistentAgent, query: str) -> Dict[str, Any]:
    span = trace.get_current_span()
    span.set_attribute("persistent_agent.id", str(agent.id))
    span.set_attribute("search.query", query)
```

**Key log points:**
- Server registration: [api/agent/tools/mcp_manager.py:241]()
- Tool catalog details: [api/agent/tools/mcp_manager.py:243-255]()
- Discovery query and results: [api/agent/tools/mcp_manager.py:754-820]()
- Connect Link detection: [api/agent/tools/mcp_manager.py:482-504]()
- Session creation: [api/integrations/pipedream_connect.py:46-136]()

**Sources:** [api/agent/tools/mcp_manager.py:29-37](), [api/agent/tools/mcp_manager.py:738-746]()

---

# Page: Browser Automation

# Browser Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/llm_config.py](api/agent/core/llm_config.py)
- [api/agent/tools/mcp_tools.py](api/agent/tools/mcp_tools.py)
- [api/tasks/browser_agent_tasks.py](api/tasks/browser_agent_tasks.py)
- [tests/unit/test_browser_task_follow_up.py](tests/unit/test_browser_task_follow_up.py)
- [tests/unit/test_event_processing_llm_selection.py](tests/unit/test_event_processing_llm_selection.py)
- [tests/unit/test_llm_failover.py](tests/unit/test_llm_failover.py)
- [tests/unit/test_mcp_tools.py](tests/unit/test_mcp_tools.py)
- [tests/utils/llm_seed.py](tests/utils/llm_seed.py)

</details>



## Purpose and Scope

This document describes the browser automation system that executes web-based tasks for agents using the browser-use library. It covers task execution, Chrome profile persistence, LLM provider configuration, proxy selection, and follow-up scheduling. For information about agent event processing that triggers these tasks, see [Agent Event Processing](#4.3). For MCP tool integration that provides additional capabilities, see [MCP Tools](#6.1).

---

## Architecture Overview

The browser automation system executes `BrowserUseAgentTask` instances in isolated Celery workers with persistent Chrome profiles, configurable proxies, and multi-tier LLM failover.

**Diagram: Browser Automation Architecture**

```mermaid
graph TB
    subgraph "Task Creation"
        EventLoop["Agent Event Loop<br/>_run_agent_loop"]
        ToolCall["LLM Tool Call:<br/>browse_web"]
        CreateTask["Create BrowserUseAgentTask"]
    end
    
    subgraph "Celery Worker"
        TaskQueue["process_browser_use_task"]
        RestoreProfile["Profile Restore<br/>from S3/Storage"]
        SelectProxy["select_proxy_for_task"]
        RunAgent["_run_agent<br/>async execution"]
        SaveProfile["Profile Save<br/>prune + compress"]
    end
    
    subgraph "Browser Session"
        BrowserProfile["BrowserProfile<br/>stealth=True<br/>user_data_dir"]
        BrowserSession["BrowserSession<br/>playwright context"]
        BUAgent["browser_use.Agent<br/>LLM + Controller"]
    end
    
    subgraph "LLM Selection"
        ResolveDB["_resolve_browser_provider<br/>_priority_from_db"]
        FallbackTiers["DEFAULT_PROVIDER_TIERS<br/>4-tier failover"]
        ProviderBackend["Backend:<br/>OPENAI/ANTHROPIC<br/>GOOGLE/OPENAI_COMPAT"]
    end
    
    subgraph "Result Processing"
        SaveSteps["Save BrowserUseAgent<br/>TaskStep records"]
        ScheduleFollowUp["_schedule_agent<br/>_follow_up"]
        ContinueCycle["Continue Budget Cycle<br/>or Fresh Trigger"]
    end
    
    EventLoop --> ToolCall
    ToolCall --> CreateTask
    CreateTask --> TaskQueue
    
    TaskQueue --> RestoreProfile
    TaskQueue --> SelectProxy
    RestoreProfile --> RunAgent
    SelectProxy --> RunAgent
    
    RunAgent --> BrowserProfile
    BrowserProfile --> BrowserSession
    BrowserSession --> BUAgent
    
    RunAgent --> ResolveDB
    ResolveDB --> FallbackTiers
    FallbackTiers --> ProviderBackend
    ProviderBackend --> BUAgent
    
    BUAgent --> SaveSteps
    SaveSteps --> SaveProfile
    SaveProfile --> ScheduleFollowUp
    ScheduleFollowUp --> ContinueCycle
    
    style RunAgent fill:#e1f5ff
    style BrowserProfile fill:#fff4e1
    style ResolveDB fill:#ffe1e1
```

**Sources:** [api/tasks/browser_agent_tasks.py:72-154](), [api/tasks/browser_agent_tasks.py:542-894]()

---

## Task Execution Pipeline

### Task Creation and Queuing

Browser tasks are created by the agent event loop when the LLM calls the `browse_web` tool. The task is persisted as a `BrowserUseAgentTask` record and queued to Celery.

```mermaid
sequenceDiagram
    participant EventLoop as _run_agent_loop
    participant DB as Database
    participant Celery as Celery Queue
    participant Worker as process_browser_use_task
    participant RunAgent as _run_agent
    
    EventLoop->>DB: Create BrowserUseAgentTask
    EventLoop->>Celery: process_browser_use_task.delay(task_id)
    
    Celery->>Worker: Execute task
    Worker->>DB: Load task, agent, user
    Worker->>Worker: Restore Chrome profile
    Worker->>Worker: Select proxy
    Worker->>RunAgent: Execute browser automation
    
    RunAgent->>RunAgent: Setup browser session
    RunAgent->>RunAgent: Configure LLM provider
    RunAgent->>RunAgent: Run browser-use Agent
    RunAgent-->>Worker: Return result
    
    Worker->>DB: Save task steps
    Worker->>Worker: Prune and save profile
    Worker->>Celery: Schedule follow-up
```

**Sources:** [api/tasks/browser_agent_tasks.py:542-558]()

### Execution Context

The `_run_agent()` function establishes the execution context with several key components:

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| **Xvfb Manager** | Virtual display for headless environments | Enabled when `should_use_ephemeral_xvfb()` returns True |
| **Browser Profile** | Persistent Chrome user data directory | Restored from storage, pruned after use |
| **Proxy Settings** | Network routing via proxy servers | Selected from ProxyServer pool |
| **LLM Client** | Language model for agent decisions | Multi-tier failover configuration |
| **File Paths** | Available files for upload | Loaded from agent's default filespace |
| **Download Listener** | Handle file downloads | Registered if `ALLOW_FILE_DOWNLOAD=True` |

**Sources:** [api/tasks/browser_agent_tasks.py:575-738]()

---

## Chrome Profile Management

### Profile Storage Architecture

Chrome profiles are persisted to object storage (S3 or local) using a sharded directory structure to avoid overwhelming single directories with millions of files.

**Diagram: Profile Storage Sharding**

```mermaid
graph LR
    UUID["agent_uuid:<br/>123e4567-e89b-12d3-<br/>a456-426614174000"]
    Strip["Strip hyphens:<br/>123e4567e89b12d3a456426614174000"]
    Shard1["First 2 chars:<br/>12"]
    Shard2["Next 2 chars:<br/>3e"]
    Key["Storage Key:<br/>browser_profiles/12/3e/<br/>123e4567-e89b-12d3-a456-426614174000.tar.zst"]
    
    UUID --> Strip
    Strip --> Shard1
    Strip --> Shard2
    Shard1 --> Key
    Shard2 --> Key
```

**Sources:** [api/tasks/browser_agent_tasks.py:495-512]()

### Profile Restore Process

When a task begins, the worker attempts to restore the agent's Chrome profile from storage:

1. **Storage Key Calculation**: Compute sharded key via `_profile_storage_key(agent_uuid)`
2. **Existence Check**: Test if `default_storage.exists(storage_key)`
3. **Download and Decompress**: Stream from storage through zstandard decompressor
4. **Tar Extraction**: Extract each member safely using `_safe_extract_tar_member()` to prevent path traversal attacks
5. **Size Logging**: Track compressed size, extraction time, and extracted file count

**Sources:** [api/tasks/browser_agent_tasks.py:586-678]()

### Profile Pruning and Persistence

After task completion, profiles are pruned to remove temporary data before compression:

**Pruned Directories:**
- `Cache`, `Code Cache`, `ShaderCache`, `GPUCache`
- `Service Worker/CacheStorage`
- `Crashpad/completed`, `Crashpad/pending`
- `Safe Browsing`

**Pruned Files:**
- `BrowserMetrics-spare.pma`, `SingletonCookie`, `SingletonLock`, `SingletonSocket`
- Any file ending with `.tmp` or `.old`

**Size Enforcement:**
- Maximum post-prune size: 500 MB (`CHROME_PROFILE_MAX_SIZE_BYTES`)
- If exceeded: Profile directory is deleted and recreated empty
- Purpose: Prevent unbounded growth from cache accumulation

**Sources:** [api/tasks/browser_agent_tasks.py:199-274]()

### Secure Tar Extraction

The `_safe_extract_tar_member()` function prevents path traversal attacks by validating each tar member before extraction:

```python
# Validates that extracted path stays within dest_dir
abs_target = os.path.realpath(target_path)
abs_dest = os.path.realpath(dest_dir)

if not (abs_target == abs_dest or abs_target.startswith(abs_dest + os.sep)):
    raise Exception(f"Unsafe path detected: {member.name}")
```

**Sources:** [api/tasks/browser_agent_tasks.py:518-537]()

---

## LLM Provider Selection

### Multi-Tier Failover Architecture

Browser automation uses a sophisticated LLM selection system with two configuration sources:

1. **Database-Backed Configuration** (Primary): `_resolve_browser_provider_priority_from_db()` reads from `BrowserLLMPolicy`, `BrowserLLMTier`, and `BrowserTierEndpoint` tables
2. **Default Tier Configuration** (Fallback): `DEFAULT_PROVIDER_TIERS` provides hardcoded 4-tier failover

**Diagram: LLM Provider Selection Flow**

```mermaid
graph TB
    Start["_run_agent called"]
    DBResolve["_resolve_browser_provider<br/>_priority_from_db"]
    DBCheck{DB Config<br/>Available?}
    DBTiers["Use DB Tiers<br/>BrowserLLMPolicy<br/>BrowserLLMTier"]
    DefaultTiers["Use DEFAULT_PROVIDER_TIERS<br/>4-tier hardcoded"]
    
    WeightedSelect["Weighted Random Selection<br/>within Tier"]
    CheckKey{API Key<br/>Available?}
    NextInTier["Try Next Endpoint<br/>in Same Tier"]
    NextTier["Advance to<br/>Next Tier"]
    CreateLLM["Create LLM Client<br/>ChatOpenAI/ChatAnthropic<br/>ChatGoogle"]
    
    Start --> DBResolve
    DBResolve --> DBCheck
    DBCheck -->|Yes| DBTiers
    DBCheck -->|No| DefaultTiers
    
    DBTiers --> WeightedSelect
    DefaultTiers --> WeightedSelect
    
    WeightedSelect --> CheckKey
    CheckKey -->|Yes| CreateLLM
    CheckKey -->|No, More in Tier| NextInTier
    CheckKey -->|No, Tier Exhausted| NextTier
    
    NextInTier --> WeightedSelect
    NextTier --> WeightedSelect
    
    style DBResolve fill:#e1f5ff
    style DefaultTiers fill:#fff4e1
    style CreateLLM fill:#ffe1e1
```

**Sources:** [api/tasks/browser_agent_tasks.py:303-365]()

### Default Provider Tiers

When DB configuration is unavailable, the system uses these hardcoded tiers:

| Tier | Providers | Weights | Purpose |
|------|-----------|---------|---------|
| **Tier 1** | OpenAI GPT-4.1 (80%)<br/>Anthropic Sonnet 4 (20%) | Load-balanced primary | High-quality, low-latency responses |
| **Tier 2** | Google Gemini 2.5 Pro (100%) | Secondary fallback | Vision support, long context |
| **Tier 3** | Fireworks Qwen3-235B (50%)<br/>OpenRouter GLM-4.5 (50%) | Cost-effective tier | Open-source alternatives |
| **Tier 4** | Anthropic Sonnet 4 (100%) | Last resort | Guaranteed completion |

**Sources:** [api/tasks/browser_agent_tasks.py:286-293]()

### Backend Configuration

Each provider uses a specific backend implementation:

**Provider Backends:**

```mermaid
graph LR
    subgraph "OPENAI Backend"
        OpenAI["openai provider"]
        GPT4["model: gpt-5-mini"]
        OpenAIClient["ChatOpenAI client"]
    end
    
    subgraph "ANTHROPIC Backend"
        Anthropic["anthropic provider"]
        Sonnet["model: claude-sonnet-4-20250514"]
        AnthropicClient["ChatAnthropic client"]
    end
    
    subgraph "GOOGLE Backend"
        Google["google provider"]
        Gemini["model: gemini-2.5-pro"]
        GoogleClient["ChatGoogle client"]
    end
    
    subgraph "OPENAI_COMPAT Backend"
        OpenRouter["openrouter/fireworks"]
        CustomModel["custom model name"]
        BaseURL["base_url override"]
        OpenAICompatClient["ChatOpenAI client<br/>with base_url"]
    end
    
    OpenAI --> GPT4 --> OpenAIClient
    Anthropic --> Sonnet --> AnthropicClient
    Google --> Gemini --> GoogleClient
    OpenRouter --> CustomModel --> BaseURL --> OpenAICompatClient
```

**Sources:** [api/tasks/browser_agent_tasks.py:742-781]()

### Vision Support

Vision support (screenshot analysis) is determined by:

1. **Database Metadata**: `endpoint.supports_vision` field if DB config is used
2. **Default Mapping**: `DEFAULT_PROVIDER_VISION_SUPPORT` dictionary for fallback

```python
DEFAULT_PROVIDER_VISION_SUPPORT = {
    "openai": True,
    "anthropic": True,
    "google": True,
    "openrouter": False,
    "fireworks": False,
}
```

The `use_vision` flag is passed to `browser_use.Agent` constructor to enable/disable screenshot capabilities.

**Sources:** [api/tasks/browser_agent_tasks.py:40-46](), [api/tasks/browser_agent_tasks.py:837]()

---

## Proxy Configuration

### Proxy Selection Logic

The `select_proxy_for_task()` function delegates to `select_proxy_for_browser_task()` from the proxy_selection module with the following priority:

1. **Override Proxy**: If provided explicitly, use it
2. **Agent Preferred Proxy**: If `task.agent.preferred_proxy` is set, use it
3. **Random Healthy Proxy**: Select from pool of healthy proxies
4. **Debug Mode Fallback**: Allow no proxy if `allow_no_proxy_in_debug=True`

**Diagram: Proxy Selection Flow**

```mermaid
graph TD
    Start["select_proxy_for_task"]
    OverrideCheck{override_proxy<br/>provided?}
    UseOverride["Use Override Proxy"]
    PreferredCheck{agent.preferred_proxy<br/>set?}
    UsePreferred["Use Preferred Proxy"]
    HealthCheck["Query ProxyServer<br/>is_healthy=True"]
    RandomSelect["Random Selection<br/>from Healthy Pool"]
    DebugCheck{Debug Mode<br/>Enabled?}
    AllowNone["Return None<br/>no proxy"]
    Error["Error: No Proxy<br/>Available"]
    
    Start --> OverrideCheck
    OverrideCheck -->|Yes| UseOverride
    OverrideCheck -->|No| PreferredCheck
    PreferredCheck -->|Yes| UsePreferred
    PreferredCheck -->|No| HealthCheck
    HealthCheck --> RandomSelect
    RandomSelect -->|Success| Return["Return ProxyServer"]
    RandomSelect -->|Failed| DebugCheck
    DebugCheck -->|Yes| AllowNone
    DebugCheck -->|No| Error
    
    UseOverride --> Return
    UsePreferred --> Return
    AllowNone --> Return
    
    style RandomSelect fill:#e1f5ff
    style HealthCheck fill:#fff4e1
```

**Sources:** [api/tasks/browser_agent_tasks.py:409-447]()

### Proxy Settings Configuration

When a proxy is selected, it's configured as a `ProxySettings` object for browser-use:

```python
proxy_settings = ProxySettings(
    server=f"{proxy_server.proxy_type.lower()}://{proxy_server.host}:{proxy_server.port}"
)
if proxy_server.username:
    proxy_settings.username = proxy_server.username
if proxy_server.password:
    proxy_settings.password = proxy_server.password
```

**Sources:** [api/tasks/browser_agent_tasks.py:688-695]()

### Observability

Proxy selection is instrumented with OpenTelemetry tracing:

```python
@tracer.start_as_current_span("SELECT Proxy")
def select_proxy_for_task(task_obj, override_proxy=None):
    # Sets attributes:
    # - proxy.id, proxy.host, proxy.port
    # - proxy.proxy_type, proxy.name
    # - agent.has_preferred_proxy
    # - no_proxy_available (if none selected)
```

**Sources:** [api/tasks/browser_agent_tasks.py:408-446]()

---

## File Upload and Download

### File Upload Configuration

Agents can upload files from their filespace to web forms when `settings.ALLOW_FILE_UPLOAD=True`:

**File Path Discovery:**

```mermaid
graph LR
    Agent["PersistentAgent"]
    GetFilespace["get_or_create_default_filespace"]
    QueryNodes["Query AgentFsNode<br/>node_type=FILE<br/>is_deleted=False"]
    BuildPaths["build_available_file_paths"]
    ProfileContext["BrowserProfile<br/>custom_context<br/>available_file_paths"]
    
    Agent --> GetFilespace
    GetFilespace --> QueryNodes
    QueryNodes --> BuildPaths
    BuildPaths --> ProfileContext
```

The `available_file_paths` list is passed to browser-use via `BrowserProfile.custom_context` to enable file selection in forms.

**Sources:** [api/tasks/browser_agent_tasks.py:370-403](), [api/tasks/browser_agent_tasks.py:704-723]()

### File Download Handling

When `settings.ALLOW_FILE_DOWNLOAD=True`, downloads are captured and persisted to the agent's filespace:

1. **Listener Registration**: `register_download_listener(browser_session, persistent_agent_id)` attaches a handler to the browser session
2. **Download Events**: Browser-use emits `FileDownloadedEvent` when files are saved
3. **Persistence**: Downloaded files are moved to the agent's filespace and tracked in `AgentFsNode`

**Sources:** [api/tasks/browser_agent_tasks.py:730-736]()

---

## Follow-up Scheduling

### Budget Cycle Continuity

After a browser task completes, `_schedule_agent_follow_up()` determines whether to continue the current budget cycle or start fresh:

**Diagram: Follow-up Decision Logic**

```mermaid
graph TD
    TaskComplete["Browser Task Complete"]
    CheckBudget{budget_id<br/>provided?}
    NoBudget["Schedule Fresh<br/>process_agent_events_task"]
    
    GetStatus["AgentBudgetManager<br/>.get_cycle_status"]
    GetActiveID["AgentBudgetManager<br/>.get_active_budget_id"]
    
    CheckActive{status == 'active'<br/>AND<br/>active_id == budget_id?}
    
    ContinueCycle["Schedule with Context<br/>budget_id, branch_id<br/>depth-1"]
    StartFresh["Schedule Fresh<br/>no context"]
    
    TaskComplete --> CheckBudget
    CheckBudget -->|No| NoBudget
    CheckBudget -->|Yes| GetStatus
    GetStatus --> GetActiveID
    GetActiveID --> CheckActive
    
    CheckActive -->|Yes| ContinueCycle
    CheckActive -->|No| StartFresh
    
    style ContinueCycle fill:#e1f5ff
    style StartFresh fill:#fff4e1
```

**Sources:** [api/tasks/browser_agent_tasks.py:72-154]()

### Follow-up Parameters

When continuing a budget cycle, the following parameters are preserved:

| Parameter | Purpose | Transformation |
|-----------|---------|----------------|
| `budget_id` | Maintains credit cycle context | Passed through unchanged |
| `branch_id` | Tracks execution branch | Passed through unchanged |
| `depth` | Prevents infinite recursion | Decremented: `max((depth or 1) - 1, 0)` |

When starting fresh, only the `agent_id` is passed, creating a new budget cycle.

**Sources:** [api/tasks/browser_agent_tasks.py:120-147]()

---

## Configuration Reference

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `BROWSER_HEADLESS` | Run Chrome in headless mode | `True` |
| `ALLOW_FILE_UPLOAD` | Enable file uploads from filespace | `False` |
| `ALLOW_FILE_DOWNLOAD` | Enable file downloads to filespace | `False` |
| `ANONYMIZED_TELEMETRY` | Disable browser-use telemetry | `false` |
| `STORAGE_BACKEND_TYPE` | Profile storage backend (LOCAL/S3/GCS) | `LOCAL` |

**Sources:** [api/tasks/browser_agent_tasks.py:54](), [api/tasks/browser_agent_tasks.py:704](), [api/tasks/browser_agent_tasks.py:712]()

### LLM Provider Environment Variables

| Provider | Environment Variable | Model |
|----------|---------------------|-------|
| OpenAI | `OPENAI_API_KEY` | `gpt-5-mini` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google | `GOOGLE_API_KEY` | `gemini-2.5-pro` |
| OpenRouter | `OPENROUTER_API_KEY` | `z-ai/glm-4.5` |
| Fireworks | `FIREWORKS_AI_API_KEY` | `qwen3-235b-a22b-instruct-2507` |

**Sources:** [api/tasks/browser_agent_tasks.py:278-284]()

### Google Vertex AI Configuration

For Google provider, additional environment variables configure Vertex AI:

```python
params.update({
    "vertex_project": os.getenv("GOOGLE_CLOUD_PROJECT", "browser-use-458714"),
    "vertex_location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4"),
})
```

**Sources:** [api/tasks/browser_agent_tasks.py:199-201]() in api/agent/core/llm_config.py

### Profile Pruning Constants

```python
CHROME_PROFILE_MAX_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

CHROME_PROFILE_PRUNE_DIRS = [
    "Cache", "Code Cache", "ShaderCache", "GPUCache",
    "Service Worker/CacheStorage",
    "Crashpad/completed", "Crashpad/pending",
    "Safe Browsing"
]

CHROME_PROFILE_PRUNE_FILES = [
    "BrowserMetrics-spare.pma", 
    "SingletonCookie", 
    "SingletonLock", 
    "SingletonSocket"
]
```

**Sources:** [api/tasks/browser_agent_tasks.py:182-193]()

---

# Page: LLM Integration

# LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/llm_config.py](api/agent/core/llm_config.py)
- [api/agent/tools/mcp_tools.py](api/agent/tools/mcp_tools.py)
- [api/tasks/browser_agent_tasks.py](api/tasks/browser_agent_tasks.py)
- [tests/unit/test_browser_task_follow_up.py](tests/unit/test_browser_task_follow_up.py)
- [tests/unit/test_event_processing_llm_selection.py](tests/unit/test_event_processing_llm_selection.py)
- [tests/unit/test_llm_failover.py](tests/unit/test_llm_failover.py)
- [tests/unit/test_mcp_tools.py](tests/unit/test_mcp_tools.py)
- [tests/utils/llm_seed.py](tests/utils/llm_seed.py)

</details>



## Purpose and Scope

This document describes the platform's LLM (Large Language Model) provider integration system, which enables both persistent agents and browser automation tasks to interact with multiple LLM providers through a unified, fault-tolerant architecture. The system supports tiered failover with weighted distribution, token-based tier selection, and dynamic database-backed configuration.

For information about how agents use LLM reasoning during task execution, see [Agent Event Processing](#4.3). For browser automation configuration specifically, see [Browser Automation](#6.2). For MCP tool integration that uses LLMs for tool discovery, see [MCP Tools](#6.1).

---

## Architecture Overview

The platform integrates LLMs through two distinct execution paths with unified failover logic:

```mermaid
graph TB
    subgraph "Execution Paths"
        PersistentAgents["PersistentAgent<br/>Event Processing"]
        BrowserTasks["BrowserUseAgentTask<br/>Execution"]
    end
    
    subgraph "LLM Clients"
        LiteLLM["LiteLLM<br/>(Persistent Agents)"]
        NativeClients["Native Clients<br/>(Browser Automation)"]
        
        ChatOpenAI["ChatOpenAI"]
        ChatAnthropic["ChatAnthropic"]
        ChatGoogle["ChatGoogle"]
    end
    
    subgraph "Configuration Layer"
        DBConfig["DB-Backed Configuration<br/>LLMProvider<br/>PersistentModelEndpoint<br/>PersistentTokenRange<br/>PersistentLLMTier"]
        
        EnvVars["Environment Variables<br/>ANTHROPIC_API_KEY<br/>OPENAI_API_KEY<br/>GOOGLE_API_KEY<br/>OPENROUTER_API_KEY"]
        
        FailoverLogic["Tiered Failover Logic<br/>get_llm_config_with_failover()<br/>_resolve_browser_provider_priority_from_db()"]
    end
    
    subgraph "LLM Providers"
        Anthropic["Anthropic<br/>Claude Sonnet 4"]
        OpenAI["OpenAI<br/>GPT-4.1 / GPT-5"]
        Google["Google Vertex AI<br/>Gemini 2.5 Pro"]
        OpenRouter["OpenRouter<br/>GLM-4.5"]
        Fireworks["Fireworks AI<br/>Qwen3-235B<br/>GPT-OSS-120B"]
    end
    
    PersistentAgents --> LiteLLM
    BrowserTasks --> NativeClients
    
    NativeClients --> ChatOpenAI
    NativeClients --> ChatAnthropic
    NativeClients --> ChatGoogle
    
    LiteLLM --> FailoverLogic
    NativeClients --> FailoverLogic
    
    FailoverLogic --> DBConfig
    FailoverLogic --> EnvVars
    
    DBConfig --> Anthropic
    DBConfig --> OpenAI
    DBConfig --> Google
    DBConfig --> OpenRouter
    DBConfig --> Fireworks
    
    EnvVars --> Anthropic
    EnvVars --> OpenAI
    EnvVars --> Google
    EnvVars --> OpenRouter
    EnvVars --> Fireworks
```

**Sources:** [api/agent/core/llm_config.py:1-477](), [api/tasks/browser_agent_tasks.py:278-365]()

---

## Provider Configuration

### PROVIDER_CONFIG Structure

The platform maintains a centralized provider configuration mapping that defines supported LLM providers, their authentication requirements, and model identifiers:

| Provider Key | Environment Variable | Model Path | Use Case |
|-------------|---------------------|------------|----------|
| `anthropic` | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4-20250514` | High-quality reasoning, vision support |
| `google` | `GOOGLE_API_KEY` | `vertex_ai/gemini-2.5-pro` | Large context, vision support |
| `openai` | `OPENAI_API_KEY` | `openai/gpt-4.1` | General purpose |
| `openai_gpt5` | `OPENAI_API_KEY` | `openai/gpt-5` | Latest frontier model |
| `openrouter_glm` | `OPENROUTER_API_KEY` | `openrouter/z-ai/glm-4.5` | Long context, cost-effective |
| `fireworks_qwen3_235b_a22b` | `FIREWORKS_AI_API_KEY` | `fireworks_ai/accounts/fireworks/models/qwen3-235b-a22b-instruct-2507` | Large parameter model |
| `fireworks_gpt_oss_120b` | `FIREWORKS_AI_API_KEY` | `fireworks_ai/accounts/fireworks/models/gpt-oss-120b` | Tested for persistent agents |

**Sources:** [api/agent/core/llm_config.py:40-77](), [api/tasks/browser_agent_tasks.py:278-284]()

### Vision Support Metadata

The system tracks which providers support vision capabilities (image understanding) for browser automation tasks. This metadata is stored both in code defaults and in the database `PersistentModelEndpoint.supports_vision` field:

```python
DEFAULT_PROVIDER_VISION_SUPPORT = {
    "openai": True,
    "anthropic": True,
    "google": True,
    "openrouter": False,
    "fireworks": False,
}
```

**Sources:** [api/tasks/browser_agent_tasks.py:40-46](), [api/agent/core/llm_config.py:381-382]()

---

## Tiered Failover System

### Token-Based Tier Selection

The system automatically selects different provider configurations based on the estimated token count of the request. This optimizes for both cost and performance across different context sizes:

```mermaid
graph LR
    TokenCount["Estimated<br/>Token Count"]
    
    Small["Small Tier<br/>0-7,500 tokens"]
    Medium["Medium Tier<br/>7,500-20,000 tokens"]
    Large["Large Tier<br/>20,000+ tokens"]
    
    SmallTier1["Tier 1:<br/>90% GPT-5<br/>10% Google"]
    SmallTier2["Tier 2:<br/>100% Google"]
    SmallTier3["Tier 3:<br/>50% Anthropic<br/>50% GLM-4.5"]
    
    MediumTier1["Tier 1:<br/>70% GLM-4.5<br/>10% Google<br/>10% GPT-5<br/>10% GPT-OSS-120B"]
    MediumTier2["Tier 2:<br/>33% GLM-4.5<br/>33% GPT-5<br/>34% Anthropic"]
    MediumTier3["Tier 3:<br/>100% GPT-5"]
    
    LargeTier1["Tier 1:<br/>70% GLM-4.5<br/>10% Google<br/>10% GPT-5<br/>10% GPT-OSS-120B"]
    LargeTier2["Tier 2:<br/>100% GPT-5"]
    LargeTier3["Tier 3:<br/>100% Anthropic"]
    LargeTier4["Tier 4:<br/>100% Qwen3-235B"]
    
    TokenCount --> Small
    TokenCount --> Medium
    TokenCount --> Large
    
    Small --> SmallTier1
    SmallTier1 -.fails.-> SmallTier2
    SmallTier2 -.fails.-> SmallTier3
    
    Medium --> MediumTier1
    MediumTier1 -.fails.-> MediumTier2
    MediumTier2 -.fails.-> MediumTier3
    
    Large --> LargeTier1
    LargeTier1 -.fails.-> LargeTier2
    LargeTier2 -.fails.-> LargeTier3
    LargeTier3 -.fails.-> LargeTier4
```

The function `get_tier_config_for_tokens()` maps token counts to tier configurations:

**Sources:** [api/agent/core/llm_config.py:84-140]()

### Weighted Provider Distribution

Within each tier, providers are selected using weighted random distribution. The `get_llm_config_with_failover()` function implements this by:

1. Selecting a tier based on token count (or custom override)
2. Within the tier, randomly selecting an endpoint based on weight
3. Removing the selected endpoint from the pool
4. Repeating until all endpoints are ordered for failover

This ensures load distribution while maintaining failover priority.

**Sources:** [api/agent/core/llm_config.py:235-401](), [api/tasks/browser_agent_tasks.py:303-365]()

---

## Database-Backed Configuration

### Schema Overview

The platform supports dynamic LLM configuration through the following database models:

```mermaid
erDiagram
    LLMProvider ||--o{ PersistentModelEndpoint : "has"
    PersistentTokenRange ||--o{ PersistentLLMTier : "contains"
    PersistentLLMTier ||--o{ PersistentTierEndpoint : "includes"
    PersistentTierEndpoint }o--|| PersistentModelEndpoint : "references"
    
    LLMProvider {
        string key "e.g. 'anthropic'"
        string display_name
        boolean enabled
        string env_var_name "e.g. 'ANTHROPIC_API_KEY'"
        text api_key_encrypted "Admin-provided key"
        string browser_backend "OPENAI|ANTHROPIC|GOOGLE|OPENAI_COMPAT"
        string vertex_project "For Google only"
        string vertex_location "For Google only"
    }
    
    PersistentModelEndpoint {
        string key "e.g. 'anthropic_sonnet4'"
        string litellm_model "e.g. 'anthropic/claude-sonnet-4-20250514'"
        boolean enabled
        boolean supports_tool_choice
        boolean supports_vision
        boolean use_parallel_tool_calls
        string api_base "For OpenAI-compatible proxies"
        decimal temperature_override "Optional"
    }
    
    PersistentTokenRange {
        string name "e.g. 'small'"
        int min_tokens
        int max_tokens "nullable for unbounded"
    }
    
    PersistentLLMTier {
        int order "1, 2, 3..."
    }
    
    PersistentTierEndpoint {
        decimal weight "0.0-1.0"
    }
```

**Sources:** [api/agent/core/llm_config.py:259-392](), [tests/utils/llm_seed.py:18-86]()

### OpenAI-Compatible Endpoint Support

The system supports custom OpenAI-compatible endpoints (e.g., vLLM, Ollama) through the `api_base` field. When an endpoint has:
- `litellm_model` starting with `openai/`
- `api_base` configured

The system automatically routes requests to the custom base URL, enabling deployment of local or private models.

**Sources:** [api/agent/core/llm_config.py:290-310](), [api/agent/core/llm_config.py:365-377]()

### API Key Resolution

The system resolves API keys in the following priority order:

1. **Admin-provided encrypted key** (`LLMProvider.api_key_encrypted`) - Decrypted using `SecretsEncryption`
2. **Environment variable** (`LLMProvider.env_var_name`) - Fallback if admin key not present
3. **Dummy key for proxies** - For OpenAI-compatible endpoints with `api_base`, uses `"sk-noauth"` if no key available

**Sources:** [api/agent/core/llm_config.py:336-353]()

---

## Browser Automation LLM Integration

### Native Client Instantiation

Browser automation tasks use native LLM clients from the `browser_use` library rather than LiteLLM. The `_run_agent()` function instantiates clients based on the `provider_backend_override` parameter:

| Backend | Client Class | Default Model |
|---------|--------------|---------------|
| `OPENAI` | `ChatOpenAI` | `gpt-5-mini` |
| `ANTHROPIC` | `ChatAnthropic` | `claude-sonnet-4-20250514` |
| `GOOGLE` | `ChatGoogle` | `gemini-2.5-pro` (configurable) |
| `OPENAI_COMPAT` | `ChatOpenAI` with `base_url` | Provider-specific |

**Sources:** [api/tasks/browser_agent_tasks.py:740-781]()

### Browser LLM Policy

Browser tasks use a separate configuration system via `BrowserLLMPolicy`, `BrowserLLMTier`, and `BrowserTierEndpoint` models. The function `_resolve_browser_provider_priority_from_db()` builds tiered configurations specifically for browser automation:

```python
# Example resolved structure:
[
    [  # Tier 1
        {
            'provider_key': 'openai',
            'endpoint_key': 'openai_gpt41',
            'weight': 0.8,
            'browser_model': 'gpt-4.1',
            'base_url': '',
            'backend': 'OPENAI',
            'supports_vision': True,
            'api_key': '...',
            'has_key': True,
        },
        # ... more tier 1 endpoints
    ],
    # ... more tiers
]
```

**Sources:** [api/tasks/browser_agent_tasks.py:303-365]()

---

## Persistent Agent LLM Integration

### LiteLLM Wrapper

Persistent agents use LiteLLM for unified provider access. The function `get_llm_config_with_failover()` returns configurations in LiteLLM format:

```python
# Returns: List[Tuple[endpoint_key, model, params]]
# Example:
[
    ("anthropic_sonnet4", "anthropic/claude-sonnet-4-20250514", {
        "temperature": 0.1,
        "api_key": "...",
        "supports_tool_choice": True,
        "use_parallel_tool_calls": True,
        "supports_vision": True,
    }),
    # ... failover configurations
]
```

The calling code passes these to `litellm.completion()` with failover handling.

**Sources:** [api/agent/core/llm_config.py:143-167](), [api/agent/core/llm_config.py:235-401]()

### Tool Choice and Parallel Calls

The system tracks two important capabilities per endpoint:

- **`supports_tool_choice`**: Whether the model supports the `tool_choice` parameter to force specific tool usage
- **`use_parallel_tool_calls`**: Whether to enable parallel tool calling (some models perform better with sequential calls)

These are passed as hints in the parameter dict but filtered before sending to LiteLLM to avoid provider rejections.

**Sources:** [api/agent/core/llm_config.py:380-387](), [tests/unit/test_mcp_tools.py:403-440]()

### Reference Tokenizer

Token counting uses a consistent reference model before provider selection:

```python
REFERENCE_TOKENIZER_MODEL = "openai/gpt-4o"
```

This ensures consistent tier selection regardless of which provider is ultimately chosen.

**Sources:** [api/agent/core/llm_config.py:80]()

---

## Failover Execution Flow

The following sequence shows how a persistent agent request flows through the failover system:

```mermaid
sequenceDiagram
    participant Agent as PersistentAgent
    participant EventProc as _run_agent_loop
    participant Tokenizer as tiktoken
    participant Failover as get_llm_config_with_failover
    participant DB as Database
    participant Redis as Redis Cache
    participant LiteLLM as litellm.completion
    participant Provider1 as Provider Tier 1
    participant Provider2 as Provider Tier 2
    
    Agent->>EventProc: Process event
    EventProc->>Tokenizer: Estimate tokens<br/>for messages + tools
    Tokenizer-->>EventProc: token_count = 8500
    
    EventProc->>Failover: get_llm_config_with_failover(token_count=8500)
    
    Failover->>DB: Query PersistentTokenRange<br/>WHERE min_tokens <= 8500<br/>AND (max_tokens > 8500 OR NULL)
    DB-->>Failover: "medium" range (7500-20000)
    
    Failover->>DB: Query PersistentLLMTier<br/>WHERE token_range="medium"<br/>ORDER BY order
    DB-->>Failover: Tier 1, Tier 2, Tier 3
    
    Failover->>DB: Query PersistentTierEndpoint<br/>JOIN PersistentModelEndpoint<br/>WHERE tier=Tier1 AND enabled=True
    DB-->>Failover: [GLM-4.5 (0.7), Google (0.1), GPT-5 (0.1), GPT-OSS (0.1)]
    
    Failover->>Failover: Weighted random selection
    Note over Failover: Selected: GLM-4.5 (70% chance)
    
    Failover->>Failover: Build remaining tier order
    Failover-->>EventProc: [(glm_endpoint, "openrouter/z-ai/glm-4.5", params),<br/>(google_endpoint, "vertex_ai/gemini-2.5-pro", params),<br/>...]
    
    EventProc->>LiteLLM: completion(<br/>model="openrouter/z-ai/glm-4.5",<br/>messages=..., tools=...,<br/>**params)
    
    LiteLLM->>Provider1: OpenRouter API call
    Provider1-->>LiteLLM: Error 500
    
    LiteLLM->>Provider2: Google Vertex API call
    Provider2-->>LiteLLM: Success response
    
    LiteLLM-->>EventProc: Completion result
    EventProc-->>Agent: Process tool calls
```

**Sources:** [api/agent/core/llm_config.py:235-401](), [api/agent/core/event_processing.py:1-1000]() (inferred from test references)

---

## Configuration Management

### Bootstrap Flow

When no LLM configuration exists, the platform enters bootstrap mode. The function `is_llm_bootstrap_required()` checks whether any usable configuration is available:

```python
def is_llm_bootstrap_required(*, force_refresh: bool = False) -> bool:
    """Return True when the platform lacks any usable LLM configuration."""
    if getattr(settings, "LLM_BOOTSTRAP_OPTIONAL", False):
        return False
    if not force_refresh:
        cached = cache.get(_LLM_BOOTSTRAP_CACHE_KEY)
        if cached is not None:
            return bool(cached)
    
    try:
        configs = get_llm_config_with_failover(token_count=0, allow_unconfigured=True)
        required = not bool(configs)
    except Exception:
        required = True
    
    _cache_bootstrap_status(required)
    return required
```

The bootstrap status is cached in Redis for 30 seconds to avoid repeated database queries during UI checks.

**Sources:** [api/agent/core/llm_config.py:450-466](), [api/agent/core/llm_config.py:28-30]()

### LLMNotConfiguredError

When configuration is required but unavailable, the system raises `LLMNotConfiguredError` to trigger the setup wizard rather than crashing:

```python
class LLMNotConfiguredError(RuntimeError):
    """Raised when no LLM providers/endpoints are available for use."""
```

This allows the platform to gracefully handle first-run scenarios.

**Sources:** [api/agent/core/llm_config.py:24-25]()

### Cache Invalidation

Configuration changes must invalidate the bootstrap cache to ensure UI reflects current state:

```python
def invalidate_llm_bootstrap_cache() -> None:
    """Invalidate cached bootstrap status after config changes."""
    try:
        cache.delete(_LLM_BOOTSTRAP_CACHE_KEY)
    except Exception:
        logger.debug("Unable to invalidate LLM bootstrap cache", exc_info=True)
```

This function should be called after:
- Creating/updating `LLMProvider` records
- Enabling/disabling endpoints
- Adding API keys

**Sources:** [api/agent/core/llm_config.py:442-447]()

---

## Integration Points Summary

The LLM integration system serves as the foundation for multiple platform capabilities:

| Component | Integration Path | Key Function |
|-----------|-----------------|--------------|
| Persistent Agent Reasoning | `_run_agent_loop` → `_completion_with_failover` | `get_llm_config_with_failover()` |
| Browser Automation | `_run_agent()` in Celery worker | `_resolve_browser_provider_priority_from_db()` |
| MCP Tool Discovery | `search_tools()` → `litellm.completion()` | `get_llm_config_with_failover()` |
| Message Summarization | `_get_conversation_summary()` | `get_summarization_llm_config()` |

The unified failover architecture ensures consistent behavior across all agent operations while allowing specialization for browser automation's unique requirements (native clients, vision support, proxy endpoints).

**Sources:** [api/agent/core/llm_config.py:1-477](), [api/tasks/browser_agent_tasks.py:1-1895](), [api/agent/tools/mcp_manager.py:1-800]() (inferred from test references)

---

# Page: Communication Systems

# Communication Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [api/agent/peer_comm.py](api/agent/peer_comm.py)
- [api/agent/peer_link_signals.py](api/agent/peer_link_signals.py)
- [api/agent/tools/peer_dm.py](api/agent/tools/peer_dm.py)
- [api/apps.py](api/apps.py)
- [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py](api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py)
- [frontend/src/components/agentChat/AgentChatLayout.tsx](frontend/src/components/agentChat/AgentChatLayout.tsx)
- [frontend/src/screens/AgentChatPage.tsx](frontend/src/screens/AgentChatPage.tsx)
- [frontend/src/stores/agentChatStore.ts](frontend/src/stores/agentChatStore.ts)
- [frontend/src/styles/agentChatLegacy.css](frontend/src/styles/agentChatLegacy.css)
- [tests/unit/test_agent_short_description.py](tests/unit/test_agent_short_description.py)
- [tests/unit/test_peer_agent_messaging.py](tests/unit/test_peer_agent_messaging.py)

</details>



This document describes the communication infrastructure that enables agents to interact with users and other agents. The gobii-platform supports four primary communication channels: **Web Chat** (real-time browser-based messaging), **Email** (via IMAP/SMTP), **SMS** (via Twilio), and **Peer Messaging** (direct agent-to-agent communication). Each channel implements allowlist-based access control, message threading, and lifecycle integration with agent processing.

For information about agent event processing triggered by messages, see [Agent Event Processing](#4.3). For API endpoints that expose message data, see [REST API](#9.1).

---

## Communication Architecture Overview

The communication system serves three primary functions:

1. **Inbound Message Processing**: Messages from external sources (email, SMS, web) trigger agent event processing via `process_agent_events_task`
2. **Outbound Message Delivery**: Agents send messages through tools during their execution loops
3. **Agent Coordination**: Peer messaging enables multi-agent workflows with rate limiting and lifecycle awareness

All messages are stored in the `PersistentAgentMessage` model and linked to `PersistentAgentConversation` objects for threading.

### Channel Overview

| Channel | Direction | Triggering | Allowlist Support | Primary Use Case |
|---------|-----------|------------|-------------------|------------------|
| Web Chat | Bidirectional | User-initiated | Implicit (session-based) | Real-time user interaction |
| Email | Bidirectional | IMAP polling/IDLE | Yes (directional) | Asynchronous communication |
| SMS | Bidirectional | Twilio webhook | Yes (directional) | Mobile notifications |
| Peer DM | Bidirectional | Tool invocation | Yes (via `AgentPeerLink`) | Agent collaboration |

**Sources:**
- [Diagram 5 from system architecture]()
- [api/models.py]()

---

## Communication Flow Diagram

```mermaid
graph TB
    subgraph "Inbound Channels"
        WebMsg["Web Chat<br/>POST /messages/"]
        EmailPoll["Email<br/>IMAP Polling"]
        SMSWebhook["SMS<br/>Twilio Webhook"]
        PeerDM["Peer DM<br/>send_agent_message tool"]
    end
    
    subgraph "Message Processing"
        WebMsg --> AllowlistCheck{Allowlist<br/>Check}
        EmailPoll --> AllowlistCheck
        SMSWebhook --> AllowlistCheck
        PeerDM --> PeerLinkCheck{AgentPeerLink<br/>Exists?}
        
        AllowlistCheck -->|Allow| CreateMsg["Create<br/>PersistentAgentMessage"]
        PeerLinkCheck -->|Yes| QuotaCheck{Quota<br/>Check}
        
        CreateMsg --> LinkConv["Link to<br/>PersistentAgentConversation"]
        QuotaCheck -->|Credits Available| CreatePeerMsg["Create 2x<br/>PersistentAgentMessage"]
        
        LinkConv --> TriggerAgent["Trigger<br/>process_agent_events_task"]
        CreatePeerMsg --> TouchAgent["Touch receiver<br/>last_interaction_at"]
        TouchAgent --> TriggerAgent
    end
    
    subgraph "Outbound Channels"
        TriggerAgent --> AgentLoop["Agent Loop<br/>_run_agent_loop"]
        AgentLoop --> ToolCall{Tool Type}
        
        ToolCall -->|send_email| EmailSend["Send via<br/>AgentEmailAccount<br/>SMTP"]
        ToolCall -->|send_sms| SMSSend["Send via<br/>SmsNumber<br/>Twilio API"]
        ToolCall -->|send_chat| WebSend["WebSocket<br/>Broadcast"]
        ToolCall -->|send_agent_message| PeerSend["PeerMessagingService<br/>.send_message"]
        
        EmailSend --> RecordOutbound["Record Outbound<br/>PersistentAgentMessage"]
        SMSSend --> RecordOutbound
        WebSend --> RecordOutbound
        PeerSend --> RecordOutbound
    end
    
    subgraph "State Management"
        RecordOutbound --> UpdateConv["Update<br/>PersistentAgentConversation"]
        UpdateConv --> WS["WebSocket Notification<br/>to UI"]
    end
```

**Sources:**
- [Diagram 5 from system architecture]()
- [api/agent/tasks.py]()
- [api/agent/peer_comm.py:103-213]()

---

## Web Chat System

The web chat interface provides real-time messaging between users and agents through a React-based UI with WebSocket updates. The system implements bidirectional scrolling, auto-scroll pinning, and processing indicators.

### Frontend Architecture

The chat UI consists of three primary components:

1. **`AgentChatLayout`** [frontend/src/components/agentChat/AgentChatLayout.tsx:27-147](): Layout component that renders timeline events, composer, and controls
2. **`AgentChatPage`** [frontend/src/screens/AgentChatPage.tsx:19-203](): Page controller managing state, scroll behavior, and WebSocket integration
3. **`useAgentChatStore`** [frontend/src/stores/agentChatStore.ts:199-472](): Zustand store managing timeline state, pagination, and processing updates

### Timeline Event Structure

```mermaid
graph LR
    Store["useAgentChatStore"] --> Events["events: TimelineEvent[]"]
    Events --> MessageEvent["kind: 'message'"]
    Events --> StepsEvent["kind: 'steps'<br/>(Tool Cluster)"]
    
    MessageEvent --> MsgData["AgentMessage<br/>bodyText<br/>bodyHtml<br/>is_outbound"]
    StepsEvent --> Entries["entries: ToolCallEntry[]<br/>collapsible<br/>collapseThreshold"]
    
    Store --> Cursors["oldestCursor<br/>newestCursor"]
    Store --> Pagination["hasMoreOlder<br/>hasMoreNewer"]
    Store --> Processing["processingActive<br/>processingWebTasks"]
```

**Sources:**
- [frontend/src/stores/agentChatStore.ts:170-197]()
- [frontend/src/types/agentChat.ts]()

### Auto-Scroll System

The auto-scroll system maintains user position in the timeline while dynamically loading new events:

1. **Bottom Sentinel Observer** [frontend/src/screens/AgentChatPage.tsx:133-154](): `IntersectionObserver` detects when user is near bottom
2. **Scroll Pin State** [frontend/src/stores/agentChatStore.ts:438-461](): Tracks whether auto-scroll is active
3. **Suppression Mechanism** [frontend/src/stores/agentChatStore.ts:462-471](): Temporarily disables auto-scroll after user interactions

When unpinned, new events accumulate in `pendingEvents` array and a "Jump to Latest" button appears.

### Message Send Flow

```mermaid
sequenceDiagram
    participant User
    participant Composer as AgentComposer
    participant Store as useAgentChatStore
    participant API as POST /messages/
    participant Backend as Django View
    participant Celery as process_agent_events_task
    
    User->>Composer: Type message & submit
    Composer->>Store: sendMessage(body)
    Store->>API: POST /agents/{id}/messages/
    API->>Backend: Create PersistentAgentMessage
    Backend->>Celery: Trigger agent processing
    Backend-->>API: Return TimelineEvent
    API-->>Store: Event with cursor
    Store->>Store: receiveRealtimeEvent()
    Store->>Store: Merge into events array
```

**Sources:**
- [frontend/src/stores/agentChatStore.ts:376-394]()
- [frontend/src/components/agentChat/AgentComposer.tsx]()
- [api/views/agent_chat.py]()

### Processing Indicator

The `ProcessingIndicator` component [frontend/src/components/agentChat/ProcessingIndicator.tsx]() displays when agents are actively processing:

- **Active State**: Shown when `processingActive=true` and `hasMoreNewer=false`
- **Browser Tasks**: Displays `processingWebTasks` array with status, prompt preview, and elapsed time
- **Expandable View**: Tasks can be expanded to show full prompt and task ID

Styling is handled by [frontend/src/styles/agentChatLegacy.css:37-307]().

**Sources:**
- [frontend/src/components/agentChat/AgentChatLayout.tsx:93-99]()
- [frontend/src/styles/agentChatLegacy.css:51-89]()

---

## Email & SMS Communication

Email and SMS channels enable agents to communicate asynchronously through external services. Each agent can have dedicated email accounts and SMS numbers for isolated communication.

### Email Infrastructure

Email communication uses agent-specific `AgentEmailAccount` objects with IMAP (inbound) and SMTP (outbound) configuration:

- **Inbound**: IMAP polling or IDLE monitoring detects new messages
- **Outbound**: SMTP sends messages through configured mail servers
- **Allowlists**: `CommsAllowlistEntry` controls which addresses can message the agent

### SMS Infrastructure

SMS communication uses `SmsNumber` objects provisioned through Twilio:

- **Inbound**: Twilio webhooks POST to `/sms/webhook/` endpoint
- **Outbound**: Twilio REST API sends messages
- **Allowlists**: Phone number validation against `CommsAllowlistEntry` records

### Allowlist System

```mermaid
graph TB
    InboundMsg["Inbound Message"] --> Policy{Allowlist<br/>Policy}
    
    Policy -->|MANUAL| CheckEntry["Check<br/>CommsAllowlistEntry"]
    Policy -->|DEFAULT| ImplicitCheck["Check Implicit<br/>Permissions"]
    
    CheckEntry --> EntryExists{Entry<br/>Exists?}
    EntryExists -->|Yes| Directional{allow_inbound<br/>=true?}
    EntryExists -->|No| Reject["Reject Message"]
    
    Directional -->|Yes| Accept["Accept Message"]
    Directional -->|No| Reject
    
    ImplicitCheck --> IsOwner{Sender is<br/>Owner/Org Member?}
    IsOwner -->|Yes| Accept
    IsOwner -->|No| Reject
    
    Accept --> CreateMsg["Create<br/>PersistentAgentMessage"]
    Reject --> Log["Log Rejection"]
```

**Allowlist Fields:**
- `address`: Email address or phone number
- `allow_inbound`: Whether sender can message agent
- `allow_outbound`: Whether agent can message this address
- `policy`: `MANUAL` (explicit entries) or `DEFAULT` (implicit permissions)

Directional allowlists enable asymmetric communication (e.g., agent can notify user but user cannot command agent).

**Sources:**
- [api/models.py:AgentEmailAccount]()
- [api/models.py:SmsNumber]()
- [api/models.py:CommsAllowlistEntry]()
- [Diagram 5 from system architecture]()

---

## Peer Messaging System

Peer messaging enables direct agent-to-agent communication with quota enforcement, debouncing, and lifecycle integration. This system supports multi-agent workflows where agents coordinate tasks.

### Peer Link Model

The `AgentPeerLink` model [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py:34-85]() establishes bidirectional communication permissions between two agents:

```python
# Key Fields
pair_key: str              # Deterministic key from sorted agent IDs
agent_a: PersistentAgent   # First agent in sorted order
agent_b: PersistentAgent   # Second agent in sorted order
messages_per_window: int   # Quota (default: 30)
window_hours: int          # Rolling window duration (default: 6)
is_enabled: bool           # Feature toggle
feature_flag: str          # Optional rollout flag
conversation: PersistentAgentConversation  # Shared conversation thread
```

The `pair_key` ensures uniqueness: [api/models.py]()

```python
@staticmethod
def build_pair_key(agent_a_id: UUID, agent_b_id: UUID) -> str:
    """Generate deterministic pair key from sorted UUIDs."""
    ids = sorted([str(agent_a_id), str(agent_b_id)])
    return f"{ids[0]}:{ids[1]}"
```

### Peer Messaging Flow

```mermaid
sequenceDiagram
    participant AgentA as Agent A<br/>Sender
    participant Tool as send_agent_message tool
    participant Service as PeerMessagingService
    participant State as AgentCommPeerState
    participant DB as Database
    participant AgentB as Agent B<br/>Receiver
    participant Celery as process_agent_events_task
    
    AgentA->>Tool: send_agent_message(peer_agent_id, message)
    Tool->>Service: PeerMessagingService(agent_a, agent_b)
    Service->>Service: _load_link() - Get AgentPeerLink
    
    Service->>DB: BEGIN TRANSACTION
    Service->>State: SELECT FOR UPDATE AgentCommPeerState
    
    State->>State: Check debounce (5s)
    State->>State: Check credits_remaining
    
    alt Credits Available
        State->>State: credits_remaining -= 1
        State->>State: last_message_at = now
        State->>DB: Save state
        
        Service->>DB: Create outbound PersistentAgentMessage<br/>(owner_agent=A)
        Service->>DB: Create inbound PersistentAgentMessage<br/>(owner_agent=B)
        
        Service->>AgentB: Touch last_interaction_at
        Service->>AgentB: Wake if EXPIRED + is_active
        
        DB->>DB: COMMIT
        Service->>Celery: process_agent_events_task.delay(agent_b_id)
        Service-->>Tool: PeerSendResult(status='ok')
    else Debounced
        Service-->>Tool: PeerMessagingError(status='debounced', retry_at)
    else Quota Exhausted
        Service->>Celery: Schedule follow-up at window_reset_at
        Service-->>Tool: PeerMessagingError(status='throttled', retry_at)
    end
```

**Sources:**
- [api/agent/peer_comm.py:50-329]()
- [tests/unit/test_peer_agent_messaging.py:67-93]()

### Rate Limiting & Quota Management

The `AgentCommPeerState` model [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py:19-31]() tracks quota consumption per peer link:

```python
# Key Fields
link: AgentPeerLink
channel: CommsChannel          # Always CommsChannel.OTHER for peer DM
messages_per_window: int       # Inherited from link
window_hours: int              # Inherited from link
credits_remaining: int         # Current available credits
window_reset_at: datetime      # When quota resets
last_message_at: datetime      # Last send timestamp
debounce_seconds: int          # Anti-loop protection (default: 5)
```

**Quota Logic** [api/agent/peer_comm.py:214-251]():

1. Lock state with `SELECT FOR UPDATE`
2. If `window_reset_at <= now`, reset `credits_remaining` and advance window
3. Check debounce: reject if `(now - last_message_at) < debounce_seconds`
4. Check quota: reject if `credits_remaining <= 0`
5. Deduct credit and update `last_message_at`
6. If credits hit zero, schedule follow-up at `window_reset_at`

### Debouncing & Anti-Loop Protection

To prevent rapid message loops between agents, the system enforces a 5-second debounce:

```python
# api/agent/peer_comm.py:116-129
if state.last_message_at is not None:
    elapsed = (now - state.last_message_at).total_seconds()
    if elapsed < state.debounce_seconds:
        retry_at = state.last_message_at + timedelta(seconds=state.debounce_seconds)
        raise PeerMessagingError(
            "Peer messaging suppressed to avoid a rapid loop.",
            status="debounced",
            retry_at=retry_at,
        )
```

**Sources:**
- [api/agent/peer_comm.py:116-129]()
- [tests/unit/test_peer_agent_messaging.py:95-114]()

### Lifecycle Integration

Peer messages can wake expired agents [api/agent/peer_comm.py:285-306]():

```python
def _touch_peer_agent(self, now) -> None:
    """Update receiver agent's last_interaction_at and restore schedule if expired."""
    locked = PersistentAgent.objects.select_for_update().get(id=self.peer_agent.id)
    
    updates = ["last_interaction_at"]
    locked.last_interaction_at = now
    
    if locked.life_state == PersistentAgent.LifeState.EXPIRED and locked.is_active:
        if locked.schedule_snapshot:
            locked.schedule = locked.schedule_snapshot
            updates.append("schedule")
        locked.life_state = PersistentAgent.LifeState.ACTIVE
        updates.append("life_state")
    
    locked.save(update_fields=updates)
```

This allows agents to "summon" expired peers back to active state when collaboration is needed.

**Sources:**
- [api/agent/peer_comm.py:285-306]()
- [api/models.py:PersistentAgent.LifeState]()

### Tool Interface

The `send_agent_message` tool [api/agent/tools/peer_dm.py:14-39]() exposes peer messaging to agents:

**Tool Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "send_agent_message",
    "description": "Send a concise direct message to another agent that shares a peer link with you.",
    "parameters": {
      "type": "object",
      "properties": {
        "peer_agent_id": {
          "type": "string",
          "description": "UUID of the linked agent you want to contact."
        },
        "message": {
          "type": "string",
          "description": "The body of the message to send. Keep it brief and actionable."
        }
      },
      "required": ["peer_agent_id", "message"]
    }
  }
}
```

**Execution** [api/agent/tools/peer_dm.py:42-110]():

1. Validate `peer_agent_id` is a valid UUID
2. Prevent self-messaging
3. Verify target agent exists
4. Call `PeerMessagingService.send_message()`
5. Return result with status, remaining credits, and optional retry timestamp
6. If successful (`status="ok"`), set `auto_sleep_ok=True` to signal agent can sleep after handoff

**Sources:**
- [api/agent/tools/peer_dm.py:14-110]()
- [tests/unit/test_peer_agent_messaging.py:159-177]()

### Peer Link Creation Signal

The `handle_peer_link_created` signal [api/agent/peer_link_signals.py:14-34]() is registered but intentionally disabled for automation:

```python
@receiver(post_save, sender=AgentPeerLink)
def handle_peer_link_created(sender, instance: AgentPeerLink, created: bool, raw: bool, **kwargs):
    """Signal handler for new peer links (intro automation disabled)."""
    if raw or not created:
        return
    
    logger.info(
        "Peer link %s connects agent %s with agent %s; intro automation disabled.",
        instance.id,
        agent_a.id,
        agent_b.id,
    )
```

The signal exists for future extensibility (e.g., sending automated introduction messages) but currently takes no action.

**Sources:**
- [api/agent/peer_link_signals.py:14-34]()
- [api/apps.py:25-30]()
- [tests/unit/test_peer_agent_messaging.py:212-234]()

---

## Message Storage Schema

All communication channels store messages in a unified schema:

```mermaid
erDiagram
    PersistentAgentMessage {
        uuid id
        uuid owner_agent_id
        uuid conversation_id
        uuid from_endpoint_id
        uuid peer_agent_id
        bool is_outbound
        text body
        text body_html
        jsonb raw_payload
        datetime timestamp
    }
    
    PersistentAgentConversation {
        uuid id
        string channel
        string address
        string display_name
        bool is_peer_dm
        uuid peer_link_id
    }
    
    PersistentAgentCommsEndpoint {
        uuid id
        uuid owner_agent_id
        string channel
        string address
        bool is_primary
    }
    
    AgentPeerLink {
        uuid id
        uuid agent_a_id
        uuid agent_b_id
        string pair_key
        int messages_per_window
        int window_hours
        bool is_enabled
    }
    
    AgentCommPeerState {
        uuid id
        uuid link_id
        string channel
        int credits_remaining
        datetime window_reset_at
        datetime last_message_at
    }
    
    PersistentAgentMessage }o--|| PersistentAgentConversation : "conversation"
    PersistentAgentMessage }o--|| PersistentAgentCommsEndpoint : "from_endpoint"
    PersistentAgentMessage }o--|| PersistentAgent : "owner_agent"
    PersistentAgentMessage }o--|| PersistentAgent : "peer_agent (optional)"
    
    PersistentAgentConversation ||--|| AgentPeerLink : "peer_link (if is_peer_dm)"
    
    AgentPeerLink ||--|| PersistentAgent : "agent_a"
    AgentPeerLink ||--|| PersistentAgent : "agent_b"
    
    AgentCommPeerState }o--|| AgentPeerLink : "link"
```

**Key Relationships:**
- `PersistentAgentMessage.owner_agent`: The agent whose timeline owns this message
- `PersistentAgentMessage.peer_agent`: For peer DMs, the other participating agent
- `PersistentAgentMessage.conversation`: Groups messages into threads
- `PersistentAgentConversation.peer_link`: Links conversation to `AgentPeerLink` for peer DMs
- `AgentCommPeerState.link`: Tracks quota state per peer link

**Sources:**
- [api/models.py:PersistentAgentMessage]()
- [api/models.py:PersistentAgentConversation]()
- [api/models.py:AgentPeerLink]()
- [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py]()

---

## Testing Strategy

Communication systems are tested in dedicated batches:

| Test Batch | Tag | Focus |
|------------|-----|-------|
| `batch_agent_chat` | `batch_agent_chat` | Web chat API endpoints, WebSocket events |
| `batch_peer_dm` | `batch_peer_dm` | Peer messaging service, quota enforcement, debouncing |
| `batch_peer_intro` | `batch_peer_intro` | Peer link creation signals (currently no-op) |
| `batch_email` | `batch_email` | Email inbound/outbound processing |
| `batch_sms` | `batch_sms` | SMS webhook processing |
| `batch_allowlist_direction` | `batch_allowlist_direction` | Directional allowlist permissions |

**Key Test Files:**
- [tests/unit/test_peer_agent_messaging.py](): Comprehensive peer messaging tests
- [tests/unit/test_agent_short_description.py](): Includes peer link signal tests

**Sources:**
- [.github/workflows/ci.yml:145-152]()
- [tests/unit/test_peer_agent_messaging.py:20-234]()

---

# Page: Agent Web Chat

# Agent Web Chat

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/components/agentChat/AgentChatLayout.tsx](frontend/src/components/agentChat/AgentChatLayout.tsx)
- [frontend/src/screens/AgentChatPage.tsx](frontend/src/screens/AgentChatPage.tsx)
- [frontend/src/stores/agentChatStore.ts](frontend/src/stores/agentChatStore.ts)
- [frontend/src/styles/agentChatLegacy.css](frontend/src/styles/agentChatLegacy.css)

</details>



## Purpose and Scope

Agent Web Chat provides a real-time, browser-based communication interface between users and their persistent agents. This page covers the chat timeline architecture, WebSocket-based event delivery, message structure, and the state management systems that enable interactive conversations.

For information about the React UI components and visual styling, see [Agent Chat Interface](#8.3). For agent-to-agent communication, see [Peer Messaging](#7.3). For email and SMS communication channels, see [Email & SMS](#7.2).

---

## Architecture Overview

The web chat system operates as a real-time communication channel built on three core layers: a timeline event model that structures conversation history, a WebSocket connection for live updates, and a React-based state management system that synchronizes UI state with backend events.

```mermaid
graph TB
    User[User Browser]
    AgentChatPage["AgentChatPage Component"]
    Store["useAgentChatStore<br/>(Zustand)"]
    Socket["useAgentChatSocket Hook"]
    API["REST API<br/>/agents/{id}/timeline/<br/>/agents/{id}/messages/"]
    WS["WebSocket<br/>/ws/agents/{id}/"]
    Django["Django Backend"]
    
    User --> AgentChatPage
    AgentChatPage --> Store
    AgentChatPage --> Socket
    Store --> API
    Socket --> WS
    API --> Django
    WS --> Django
    
    Store -->|"Timeline events"| AgentChatPage
    Socket -->|"Real-time events"| Store
    
    subgraph "State Flow"
        Store
        Socket
    end
    
    subgraph "Backend"
        API
        WS
        Django
    end
```

**Sources:** [frontend/src/screens/AgentChatPage.tsx:1-204](), [frontend/src/stores/agentChatStore.ts:1-473]()

---

## Timeline Event Model

The chat timeline consists of heterogeneous event types serialized as `TimelineEvent` objects. Each event has a `cursor` field (format: `{timestamp}:{discriminator}`) used for pagination and ordering.

### Event Types

| Event Kind | Description | Key Fields |
|------------|-------------|------------|
| `message` | User or agent message | `message.bodyText`, `message.bodyHtml`, `message.direction` |
| `steps` | Tool call cluster | `entries[]`, `collapsible`, `collapseThreshold` |
| `schedule` | Schedule display | `schedule.cronExpression`, `schedule.humanReadable` |

**Message Events**

Message events represent text communication in either direction (`INBOUND` from user, `OUTBOUND` from agent). The frontend normalizes HTML content via `sanitizeHtml()` before rendering.

[frontend/src/stores/agentChatStore.ts:34-69]()

**Tool Cluster Events**

Tool execution (e.g., `browse_web`, `send_email`, MCP tool calls) appears as a `steps` event containing multiple `ToolCallEntry` objects. Clusters with ≥ `collapseThreshold` entries become collapsible UI elements.

[frontend/src/stores/agentChatStore.ts:81-111]()

### Event Normalization and Merging

The store implements merge logic to handle:
1. **HTML sanitization**: Raw text that looks like HTML is sanitized and stored in `bodyHtml`
2. **Cluster merging**: Incoming `steps` events merge with existing ones at the same cursor
3. **Deduplication**: Events with identical cursors replace previous versions

[frontend/src/stores/agentChatStore.ts:113-129]()

**Sources:** [frontend/src/stores/agentChatStore.ts:1-473](), [frontend/src/types/agentChat.ts]()

---

## Real-time Communication

### WebSocket Connection

The `useAgentChatSocket` hook establishes a WebSocket connection to `/ws/agents/{agentId}/` and routes incoming messages to the store.

```mermaid
sequenceDiagram
    participant Browser
    participant Socket as useAgentChatSocket
    participant Store as useAgentChatStore
    participant WS as WebSocket Server
    participant Agent as Agent Event Processor
    
    Browser->>Socket: Mount component
    Socket->>WS: Connect /ws/agents/{id}/
    WS-->>Socket: Connection established
    
    Agent->>WS: process_agent_events completes
    WS->>Socket: {type: 'timeline_event', event: {...}}
    Socket->>Store: receiveRealtimeEvent(event)
    Store->>Store: Merge event into timeline
    Store-->>Browser: UI re-renders
    
    Agent->>WS: Tool execution starts
    WS->>Socket: {type: 'processing', active: true}
    Socket->>Store: updateProcessing({active: true})
    Store-->>Browser: Show processing indicator
```

**Sources:** [frontend/src/hooks/useAgentChatSocket.ts]()

### Processing Status Updates

WebSocket messages with `type: 'processing'` or `type: 'processing_snapshot'` control the visibility of the processing indicator. The `ProcessingSnapshot` object includes:
- `active`: Boolean indicating if agent is processing
- `webTasks`: Array of `ProcessingWebTask` objects for browser automation tasks

[frontend/src/stores/agentChatStore.ts:133-168]()

**Sources:** [frontend/src/stores/agentChatStore.ts:133-168](), [frontend/src/types/agentChat.ts]()

---

## Message Flow: User to Agent

When a user sends a message through the chat interface, the following sequence occurs:

```mermaid
sequenceDiagram
    participant User
    participant Composer as AgentComposer
    participant Store as useAgentChatStore
    participant API as POST /agents/{id}/messages/
    participant WS as WebSocket
    participant Django
    participant Celery as process_agent_events_task
    
    User->>Composer: Type message, click Send
    Composer->>Store: sendMessage(body)
    Store->>API: {body_text: "..."}
    API->>Django: Create PersistentAgentMessage
    Django->>Celery: Trigger agent processing
    Django-->>API: TimelineEvent (user message)
    API-->>Store: Return event
    Store->>Store: receiveRealtimeEvent()
    Store-->>User: Optimistic UI update
    
    Celery->>Celery: _run_agent_loop
    Celery->>WS: {type: 'processing', active: true}
    WS->>Store: updateProcessing()
    
    Celery->>Celery: LLM generates response
    Celery->>Django: Save agent reply message
    Django->>WS: {type: 'timeline_event', event: {...}}
    WS->>Store: receiveRealtimeEvent()
    Store-->>User: Display agent reply
    
    Celery->>WS: {type: 'processing', active: false}
    WS->>Store: updateProcessing({active: false})
```

**Key Implementation Details:**

1. **Optimistic Updates**: `sendMessage()` immediately adds the user's message to the timeline via `receiveRealtimeEvent()`, avoiding perceived latency [frontend/src/stores/agentChatStore.ts:376-394]()

2. **Credit Gating**: The backend may reject message processing if credits are exhausted (see [TaskCreditService](#5.1))

3. **Conversation Threading**: Messages link to a `PersistentAgentConversation` record for context preservation

**Sources:** [frontend/src/stores/agentChatStore.ts:376-394](), [frontend/src/api/agentChat.ts]()

---

## State Management Architecture

### useAgentChatStore

The Zustand-based store manages all chat state, including timeline events, pagination cursors, loading states, and auto-scroll behavior.

**Core State Fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `agentId` | `string \| null` | Current agent identifier |
| `events` | `TimelineEvent[]` | Visible timeline window (max 100 events) |
| `oldestCursor` / `newestCursor` | `string \| null` | Pagination boundaries |
| `hasMoreOlder` / `hasMoreNewer` | `boolean` | Infinite scroll flags |
| `processingActive` | `boolean` | Agent processing indicator |
| `processingWebTasks` | `ProcessingWebTask[]` | Active browser automation tasks |
| `autoScrollPinned` | `boolean` | Whether to auto-scroll to bottom |
| `pendingEvents` | `TimelineEvent[]` | Events received while scrolled up |

[frontend/src/stores/agentChatStore.ts:170-197]()

### Pagination System

The store maintains a sliding window of up to 100 events (`TIMELINE_WINDOW_SIZE`). When loading older or newer events, the window shifts and excess events are trimmed.

**Load Older Flow:**

```mermaid
graph LR
    A["User clicks<br/>'Load older'"] --> B["loadOlder()"]
    B --> C["fetchAgentTimeline()<br/>direction='older'"]
    C --> D["Merge with existing events"]
    D --> E["Trim to 100 events<br/>(keep oldest)"]
    E --> F["Update cursors<br/>Set hasMoreNewer=true<br/>if trimmed"]
```

[frontend/src/stores/agentChatStore.ts:265-299]()

**Load Newer Flow:**

When loading newer events, the window shifts forward, trimming older events if necessary. If the newest events are loaded, `hasMoreNewer` becomes `false` and the processing indicator becomes visible.

[frontend/src/stores/agentChatStore.ts:301-340]()

**Sources:** [frontend/src/stores/agentChatStore.ts:131-340]()

---

## Auto-scroll System

The auto-scroll system ensures new messages appear automatically while allowing users to browse history without disruption.

### Scroll Pinning Mechanism

A scroll is "pinned" when the user is viewing the bottom of the timeline. The system tracks this via two mechanisms:

1. **IntersectionObserver**: Watches a sentinel element at timeline bottom [frontend/src/screens/AgentChatPage.tsx:133-154]()
2. **Scroll Event Listener**: Detects manual scrolling and unpins if distance > 160px from bottom [frontend/src/screens/AgentChatPage.tsx:69-117]()

```mermaid
stateDiagram-v2
    [*] --> Pinned: Initial load
    Pinned --> Unpinned: User scrolls up > 160px
    Unpinned --> Pinned: User scrolls to within 12px of bottom
    
    Pinned --> Pinned: New event arrives → auto-scroll
    Unpinned --> Unpinned: New event arrives → add to pendingEvents
    
    note right of Unpinned
        hasUnseenActivity = true
        Show "Jump to latest" button
    end note
```

### Pending Events Queue

When unpinned, incoming real-time events accumulate in `pendingEvents[]` rather than appearing immediately. This prevents the timeline from shifting unexpectedly while the user reads old messages.

[frontend/src/stores/agentChatStore.ts:396-427]()

When the user re-pins (scrolls to bottom or clicks "Jump to latest"), pending events merge into the main timeline.

[frontend/src/stores/agentChatStore.ts:438-461]()

### Auto-scroll Suppression

The `suppressAutoScrollPin()` method temporarily prevents auto-scroll re-activation for a duration (default 1000ms). This is used when programmatic scrolling occurs to avoid race conditions.

[frontend/src/stores/agentChatStore.ts:462-471]()

**Sources:** [frontend/src/screens/AgentChatPage.tsx:69-172](), [frontend/src/stores/agentChatStore.ts:396-471]()

---

## Processing Indicators

### Active Processing State

The `ProcessingIndicator` component renders when `processingActive` is true and no newer events exist to load. It displays the agent's first name with a pulsing visual indicator.

[frontend/src/components/agentChat/ProcessingIndicator.tsx](), [frontend/src/styles/agentChatLegacy.css:37-110]()

### Browser Task Cards

When browser automation tasks (`BrowserUseAgentTask`) are running, the processing indicator expands to show individual task cards with:
- **Status badge**: Color-coded status (pending, running, succeeded, failed)
- **Elapsed time**: Duration since task start
- **Prompt preview**: Truncated task prompt
- **Expandable details**: Full prompt in Markdown format

```mermaid
graph TB
    subgraph "ProcessingIndicator States"
        Simple["Simple Mode<br/>(no web tasks)<br/>Agent is thinking..."]
        Expanded["Expanded Mode<br/>(webTasks.length > 0)<br/>Show task cards"]
    end
    
    Simple -->|"webTasks received"| Expanded
    Expanded -->|"webTasks cleared"| Simple
    
    Expanded --> Card1["Task Card 1<br/>Status: RUNNING<br/>15s elapsed"]
    Expanded --> Card2["Task Card 2<br/>Status: PENDING<br/>-"]
```

The frontend polls `/agents/{id}/processing-status/` to refresh task details if they become stale.

[frontend/src/stores/agentChatStore.ts:251-263]()

**Sources:** [frontend/src/components/agentChat/ProcessingIndicator.tsx](), [frontend/src/stores/agentChatStore.ts:251-263](), [frontend/src/styles/agentChatLegacy.css:37-293]()

---

## Timeline Rendering

### AgentChatLayout Component

The `AgentChatLayout` component is the primary layout shell that composes:
- **Timeline event list**: Scrollable history with load controls
- **Processing indicator**: Agent activity status
- **Composer**: Message input field
- **Jump button**: Floating action button to return to latest

[frontend/src/components/agentChat/AgentChatLayout.tsx:27-147]()

**Layout Structure:**

```mermaid
graph TB
    Root["#agent-workspace-root<br/>(flex container)"]
    Shell["#timeline-shell<br/>(scrollable area)"]
    Events["#timeline-events<br/>(event list container)"]
    
    LoadOlder["Load older button"]
    EventList["TimelineEventList"]
    Processing["ProcessingIndicator"]
    Sentinel["Bottom sentinel<br/>(IntersectionObserver target)"]
    LoadNewer["Load newer button"]
    Composer["AgentComposer<br/>(fixed at bottom)"]
    JumpBtn["Jump to latest<br/>(floating button)"]
    
    Root --> Shell
    Shell --> Events
    Events --> LoadOlder
    Events --> EventList
    Events --> Processing
    Events --> Sentinel
    Events --> LoadNewer
    Root --> Composer
    Root --> JumpBtn
```

### Conditional Rendering Logic

| Element | Visible When |
|---------|-------------|
| Load Older Button | `hasMoreOlder || loadingOlder` |
| Load Newer Button | `hasMoreNewer || loadingNewer` |
| Processing Indicator | `processingActive && !hasMoreNewer` |
| Bottom Sentinel | `!initialLoading && !hasMoreNewer` |
| Jump to Latest Button | `hasMoreNewer \|\| hasUnseenActivity \|\| !autoScrollPinned` |

[frontend/src/components/agentChat/AgentChatLayout.tsx:47-52]()

**Sources:** [frontend/src/components/agentChat/AgentChatLayout.tsx:1-148](), [frontend/src/styles/agentChatLegacy.css:1-1317]()

---

## Event Styling and Animation

### Message Bubbles

Chat bubbles use distinct styling based on direction and type:

| Class | Applied To | Styling |
|-------|-----------|---------|
| `.chat-bubble--user` | User messages | Gradient purple background, white text |
| `.chat-bubble--agent` | Agent messages | Light background, dark text, subtle border |
| `.chat-bubble--peer-out` | Outbound peer messages | Light purple gradient, border |
| `.chat-bubble--peer-in` | Inbound peer messages | Light background, dashed border |

[frontend/src/styles/agentChatLegacy.css:1180-1203]()

### Incoming Animation

New events that arrive via WebSocket receive the `.timeline-event--incoming` class, triggering a slide-up animation with highlight effect:

[frontend/src/styles/agentChatLegacy.css:539-579]()

```css
@keyframes timelineEventIncoming {
  0% { opacity: 0; transform: translateY(12px); }
  100% { opacity: 1; transform: translateY(0); }
}
```

**Sources:** [frontend/src/styles/agentChatLegacy.css:528-579](), [frontend/src/components/agentChat/TimelineEventList.tsx]()

---

## Web Session Management

The `useAgentWebSession` hook initializes a session via `POST /agents/{id}/web-session/` to track user presence for analytics. This is separate from WebSocket connectivity and does not affect chat functionality.

[frontend/src/hooks/useAgentWebSession.ts](), [frontend/src/screens/AgentChatPage.tsx:49]()

**Sources:** [frontend/src/hooks/useAgentWebSession.ts](), [frontend/src/screens/AgentChatPage.tsx:1-204]()

---

# Page: Email & SMS

# Email & SMS

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



This document describes the email and SMS communication systems that enable persistent agents to interact with external contacts via traditional messaging channels. These systems handle provisioning communication endpoints, processing inbound messages, sending outbound messages, and enforcing allowlist-based permissions.

For real-time web-based chat, see [Agent Web Chat](#7.1). For agent-to-agent direct messaging, see [Peer Messaging](#7.3).

---

## Overview

The platform supports two traditional communication channels for agents:

- **Email**: Agents can send and receive emails via dedicated email accounts (IMAP/SMTP) or transactional email providers (Mailgun, Postmark)
- **SMS**: Agents can send and receive SMS messages via provisioned phone numbers through Twilio

Both systems follow a similar architecture:
1. **Endpoint Provisioning**: Agents are assigned dedicated email addresses or phone numbers
2. **Inbound Processing**: External messages arrive via webhooks or polling and trigger agent event processing
3. **Outbound Sending**: Agents use LLM-powered tools to compose and send messages
4. **Allowlist Enforcement**: Directional permissions control who can contact agents and whom agents can contact

---

## Email System Architecture

### Email Account Model

The `AgentEmailAccount` model represents a dedicated email account for agent communication. Each account stores IMAP/SMTP credentials and provider configuration.

**Core Data Model**

```mermaid
classDiagram
    class AgentEmailAccount {
        +UUID id
        +PersistentAgent agent
        +str email_address
        +str display_name
        +str imap_server
        +int imap_port
        +bool imap_use_ssl
        +str smtp_server
        +int smtp_port
        +str smtp_encryption
        +BinaryField encrypted_password
        +str provider
        +JSONField provider_config
        +datetime last_check_at
        +bool is_active
        +get_imap_password()
        +set_imap_password()
        +get_smtp_password()
        +set_smtp_password()
    }
    
    class PersistentAgent {
        +UUID id
        +str name
        +User user
        +Organization organization
    }
    
    class PersistentAgentEmailEndpoint {
        +UUID id
        +PersistentAgent agent
        +AgentEmailAccount email_account
        +datetime created_at
    }
    
    AgentEmailAccount --> PersistentAgent : agent
    PersistentAgentEmailEndpoint --> PersistentAgent : agent
    PersistentAgentEmailEndpoint --> AgentEmailAccount : email_account
```

Sources: [api/models.py:2400-2600]()

**Key Fields:**
- **IMAP Configuration**: Server, port, SSL settings for receiving mail
- **SMTP Configuration**: Server, port, encryption (STARTTLS/SSL) for sending mail  
- **Encrypted Credentials**: Password stored using `GOBII_ENCRYPTION_KEY` via `encrypt_value()`/`decrypt_value()`
- **Provider**: `"smtp"` for custom IMAP/SMTP or `"postmark"` for transactional email
- **Provider Config**: JSON field for provider-specific settings (e.g., Postmark server token)

### Email Delivery Modes

The platform supports three email delivery modes, selected per account:

| Mode | Configuration | Use Case |
|------|--------------|----------|
| **IMAP/SMTP** | Custom mail server credentials | Self-hosted or ISP email accounts |
| **Postmark** | Postmark server token + inbound hash | Transactional email with tracking |
| **Simulated** | `SIMULATE_EMAIL_DELIVERY=True` | Local development without external providers |

Sources: [config/settings.py:829-834]()

**Simulated Delivery**

When `SIMULATE_EMAIL_DELIVERY=True` (default in non-production environments), outbound emails are logged but not actually sent. This allows agent testing without configuring real email providers.

Sources: [config/settings.py:832-834]()

### Inbound Email Processing

Inbound emails are processed through two mechanisms:

#### 1. IMAP IDLE Watcher (Optional)

When `IMAP_IDLE_ENABLED=True`, a management command runs dedicated IMAP IDLE watchers for agent email accounts:

```mermaid
sequenceDiagram
    participant Runner as IMAP IDLE Runner
    participant Redis
    participant IMAP as IMAP Server
    participant Celery
    participant Agent as process_agent_events_task
    
    Runner->>Redis: Scan for active AgentEmailAccount
    Runner->>Redis: Acquire lease (60s TTL)
    Runner->>IMAP: Connect & IDLE
    IMAP-->>Runner: New message notification
    Runner->>Redis: Set debounce flag (10s)
    Runner->>Celery: Queue poll_agent_email task
    Celery->>IMAP: FETCH new messages
    Celery->>Celery: Parse email body/headers
    Celery->>Celery: Create PersistentAgentMessage
    Celery->>Agent: process_agent_events_task.delay()
```

Sources: [config/settings.py:808-820]()

**Configuration Variables:**
- `IMAP_IDLE_ENABLED`: Enable/disable IDLE watcher (default: `False`)
- `IMAP_IDLE_MAX_CONNECTIONS`: Max watchers per runner process (default: 200)
- `IMAP_IDLE_SCAN_INTERVAL_SEC`: Account rescan interval (default: 30s)
- `IMAP_IDLE_REISSUE_SEC`: Re-issue IDLE command interval (default: 1500s)
- `IMAP_IDLE_DEBOUNCE_SEC`: Debounce window for duplicate polls (default: 10s)
- `IMAP_IDLE_LEASE_TTL_SEC`: Cross-runner lease TTL (default: 60s)

#### 2. Webhook Delivery (Postmark/Mailgun)

For provider-based accounts, inbound emails arrive via HTTP webhooks:

```mermaid
graph TB
    Email[External Email] --> Provider[Email Provider<br/>Postmark/Mailgun]
    Provider --> Webhook[POST /webhooks/email/inbound/]
    Webhook --> Verify{Verify Token}
    Verify -->|Invalid| Reject[401 Unauthorized]
    Verify -->|Valid| Parse[Parse Email]
    Parse --> Match{Match Email<br/>Account?}
    Match -->|No| Ignore[Ignore]
    Match -->|Yes| CheckAllow{Check<br/>Allowlist}
    CheckAllow -->|Blocked| Drop[Drop Message]
    CheckAllow -->|Allowed| CreateMsg[Create<br/>PersistentAgentMessage]
    CreateMsg --> Queue[process_agent_events_task]
```

Sources: [config/settings.py:822-823]()

**Webhook Tokens:**
- `POSTMARK_INCOMING_WEBHOOK_TOKEN`: Token for Postmark inbound webhook auth
- `MAILGUN_INCOMING_WEBHOOK_TOKEN`: Token for Mailgun inbound webhook auth

### Outbound Email Sending

Agents send emails using the `send_email` tool exposed during agent event processing.

**Tool Execution Flow**

```mermaid
sequenceDiagram
    participant Loop as _run_agent_loop
    participant LLM
    participant Tool as execute_send_email
    participant Check as Allowlist Check
    participant Send as Email Sender
    participant DB
    
    Loop->>LLM: Completion with send_email tool
    LLM-->>Loop: Tool call: send_email(to, subject, body)
    Loop->>Tool: Execute tool
    Tool->>Check: Verify recipient in allowlist
    Check-->>Tool: Allowed
    Tool->>DB: Create PersistentAgentMessage (outbound)
    Tool->>Send: Send via SMTP/Provider
    Send-->>Tool: Delivery status
    Tool->>DB: Update message status
    Tool-->>Loop: Result: message_id
```

Sources: [api/agent/core/event_processing.py:63]()

**Tool Schema** (send_email):
- `to`: Email address (string, required)
- `subject`: Subject line (string, required)
- `body`: Message body (string, required)
- `cc`: CC recipients (array of strings, optional)
- `bcc`: BCC recipients (array of strings, optional)

**Delivery Status Tracking**

Messages track delivery through the `DeliveryStatus` enum:

| Status | Meaning |
|--------|---------|
| `QUEUED` | Created but not yet sent |
| `SENDING` | Transmission in progress |
| `SENT` | Successfully delivered to provider |
| `DELIVERED` | Provider confirmed delivery (webhooks) |
| `FAILED` | Delivery failed |

Sources: [api/models.py:112-117]()

---

## SMS System Architecture

### SMS Number Provisioning

The `SmsNumber` model represents a Twilio phone number provisioned for agent communication.

```mermaid
classDiagram
    class SmsNumber {
        +BigAutoField id
        +str phone_number (E.164)
        +str friendly_name
        +SmsProvider provider
        +str provider_number_sid
        +JSONField capabilities
        +bool is_active
        +datetime created_at
        +datetime updated_at
    }
    
    class PersistentAgentSmsEndpoint {
        +UUID id
        +PersistentAgent agent
        +SmsNumber sms_number
        +datetime created_at
    }
    
    class SmsProvider {
        <<enumeration>>
        TWILIO
    }
    
    SmsNumber --> SmsProvider : provider
    PersistentAgentSmsEndpoint --> SmsNumber : sms_number
    PersistentAgentSmsEndpoint --> PersistentAgent : agent
```

Sources: [api/models.py:2100-2200]()

**Key Fields:**
- **phone_number**: E.164 format (e.g., `+12025551234`)
- **provider_number_sid**: Twilio SID for the number
- **capabilities**: JSON field storing SMS/MMS/Voice flags
- **is_active**: Whether the number is currently available for use

**Number Sync Task**

The `sync_twilio_numbers` Celery Beat task periodically synchronizes available numbers from Twilio:

```mermaid
graph LR
    Beat[Celery Beat<br/>Hourly] --> Task[sync_twilio_numbers]
    Task --> Twilio[Twilio API<br/>List Numbers]
    Twilio --> Update[Update/Create<br/>SmsNumber Records]
    Update --> DB[(Database)]
```

Sources: [config/settings.py:591-596](), [api/tasks/sms_tasks.py]()

**Configuration:**
- `TWILIO_ENABLED`: Feature flag (default: `False` in community mode)
- `TWILIO_ACCOUNT_SID`: Twilio account identifier
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_MESSAGING_SERVICE_SID`: Messaging service for outbound SMS

Sources: [config/settings.py:837-849]()

### Inbound SMS Processing

Inbound SMS messages arrive via Twilio webhooks:

```mermaid
sequenceDiagram
    participant Phone as External Phone
    participant Twilio
    participant Webhook as POST /webhooks/sms/inbound/
    participant Verify as Token Verification
    participant Parse as Message Parser
    participant Allow as Allowlist Check
    participant DB
    participant Agent as process_agent_events_task
    
    Phone->>Twilio: Send SMS
    Twilio->>Webhook: POST with message data
    Webhook->>Verify: Check TWILIO_INCOMING_WEBHOOK_TOKEN
    Verify-->>Webhook: Valid
    Webhook->>Parse: Extract From/To/Body
    Parse->>Allow: Check sender allowlist
    Allow-->>Parse: Allowed
    Parse->>DB: Create PersistentAgentMessage
    DB->>Agent: Queue agent processing
```

Sources: [config/settings.py:863]()

**Webhook Security:**
- `TWILIO_INCOMING_WEBHOOK_TOKEN`: Token appended to webhook URL for verification
- Webhook URL format: `/webhooks/sms/inbound/?token={TWILIO_INCOMING_WEBHOOK_TOKEN}`

**Message Parsing:**
- Body length limit: `SMS_MAX_BODY_LENGTH` (default: 1450 characters)
- Reply stripping: `EMAIL_STRIP_REPLIES` controls whether to strip quoted replies (default: `False`)

Sources: [config/settings.py:866-870]()

### Outbound SMS Sending

Agents send SMS messages using the `send_sms` tool.

**Tool Execution Flow**

```mermaid
sequenceDiagram
    participant Loop as _run_agent_loop
    participant LLM
    participant Tool as execute_send_sms
    participant Allow as Allowlist Check
    participant Twilio
    participant DB
    
    Loop->>LLM: Completion with send_sms tool
    LLM-->>Loop: Tool call: send_sms(to, body)
    Loop->>Tool: Execute tool
    Tool->>Allow: Verify recipient in allowlist
    Allow-->>Tool: Allowed
    Tool->>DB: Create PersistentAgentMessage
    Tool->>Twilio: Send via Messaging Service
    Twilio-->>Tool: Message SID
    Tool->>DB: Update with provider message ID
    Tool-->>Loop: Result: message_id
```

Sources: [api/agent/core/event_processing.py:64]()

**Tool Schema** (send_sms):
- `to`: Phone number in E.164 format (string, required)
- `body`: Message text (string, required, max length from config)

**Twilio Messaging Service**

Outbound SMS uses Twilio's Messaging Service for:
- Automatic number selection from available pool
- Delivery optimization and fallback
- Compliance with carrier regulations

Configuration: `TWILIO_MESSAGING_SERVICE_SID`

Sources: [config/settings.py:841]()

---

## Communication Endpoints

### Endpoint Hierarchy

Communication endpoints link agents to their email accounts or phone numbers:

```mermaid
classDiagram
    class PersistentAgentCommsEndpoint {
        <<abstract>>
        +UUID id
        +PersistentAgent agent
        +CommsChannel channel
        +bool is_active
        +datetime created_at
    }
    
    class PersistentAgentEmailEndpoint {
        +AgentEmailAccount email_account
    }
    
    class PersistentAgentSmsEndpoint {
        +SmsNumber sms_number
    }
    
    PersistentAgentCommsEndpoint <|-- PersistentAgentEmailEndpoint
    PersistentAgentCommsEndpoint <|-- PersistentAgentSmsEndpoint
```

Sources: [api/models.py:2650-2750]()

**Channel Types** (CommsChannel enum):
- `EMAIL`: Email communication
- `SMS`: SMS messaging
- `WEB`: Web chat (see [Agent Web Chat](#7.1))
- `SLACK`: Slack integration (future)
- `DISCORD`: Discord integration (future)
- `OTHER`: Custom/unknown channels

Sources: [api/models.py:103-109]()

### Endpoint Lifecycle

**Creation:**
1. Agent provisioned with contact preferences
2. Email account or SMS number assigned
3. Endpoint record created linking agent to communication method
4. Allowlist entries populated with initial contacts

**Activation/Deactivation:**
- Endpoints have `is_active` flag controlling whether they process messages
- Deactivated endpoints ignore inbound messages and prevent outbound sends
- Useful for temporarily disabling communication without deletion

**Deletion:**
- Soft delete: Set `is_active=False`
- Hard delete: Remove endpoint record (orphans messages, not recommended)

Sources: [api/models.py:2650-2850]()

---

## Allowlist System

The allowlist controls which external contacts can send messages to agents and which contacts agents can message.

### CommsAllowlistEntry Model

```mermaid
classDiagram
    class CommsAllowlistEntry {
        +UUID id
        +PersistentAgent agent
        +str address
        +CommsChannel channel
        +bool allow_inbound
        +bool allow_outbound
        +str notes
        +datetime created_at
        +datetime updated_at
    }
    
    class CommsChannel {
        <<enumeration>>
        EMAIL
        SMS
        WEB
        SLACK
        DISCORD
        OTHER
    }
    
    CommsAllowlistEntry --> CommsChannel : channel
```

Sources: [api/models.py:3200-3300]()

**Key Fields:**
- **address**: Email address or phone number (E.164)
- **channel**: Communication channel type
- **allow_inbound**: Whether this contact can send messages to the agent
- **allow_outbound**: Whether the agent can send messages to this contact
- **notes**: Optional description of why contact is allowed

### Directional Permissions

Allowlist entries support **asymmetric permissions**, enabling fine-grained control:

| Configuration | Use Case |
|--------------|----------|
| `allow_inbound=True`<br/>`allow_outbound=True` | Full bidirectional communication |
| `allow_inbound=True`<br/>`allow_outbound=False` | Agent can receive but not initiate |
| `allow_inbound=False`<br/>`allow_outbound=True` | Agent can notify but user can't reply |
| `allow_inbound=False`<br/>`allow_outbound=False` | Blocked (entry can be kept for audit) |

**Example:** An agent monitoring customer support might have:
- Customers: `allow_inbound=True, allow_outbound=True` (bidirectional)
- Admin dashboard: `allow_inbound=False, allow_outbound=True` (notifications only)

### Allowlist Policies

Agents can operate under two allowlist policies:

**1. Default Policy** (implicit allow):
- Owner email/phone automatically allowed
- Organization member contacts automatically allowed
- No explicit `CommsAllowlistEntry` required

**2. Manual Policy** (explicit allow):
- Only addresses in `CommsAllowlistEntry` permitted
- Stricter security for sensitive use cases
- Must explicitly add each contact

Policy selection is configured per-agent during provisioning.

Sources: From high-level architecture diagrams in prompt

### Allowlist Enforcement

**Inbound Message Processing:**

```mermaid
graph TB
    Msg[Inbound Message] --> Parse[Parse Sender]
    Parse --> GetPolicy{Agent<br/>Allowlist<br/>Policy?}
    GetPolicy -->|Default| CheckDefault{Sender is<br/>Owner/Org<br/>Member?}
    GetPolicy -->|Manual| CheckEntry{Entry<br/>Exists?}
    CheckDefault -->|Yes| AllowIn[Allow]
    CheckDefault -->|No| RejectIn[Reject]
    CheckEntry -->|Yes| CheckInbound{allow_inbound<br/>= True?}
    CheckEntry -->|No| RejectIn
    CheckInbound -->|Yes| AllowIn
    CheckInbound -->|No| RejectIn
    AllowIn --> Process[Create Message<br/>& Process]
    RejectIn --> Log[Log Rejection]
```

**Outbound Message Sending:**

```mermaid
graph TB
    Send[send_email/send_sms] --> GetRecip[Get Recipient]
    GetRecip --> GetPolicy{Agent<br/>Allowlist<br/>Policy?}
    GetPolicy -->|Default| AllowOut[Allow]
    GetPolicy -->|Manual| CheckEntry{Entry<br/>Exists?}
    CheckEntry -->|Yes| CheckOutbound{allow_outbound<br/>= True?}
    CheckEntry -->|No| RejectOut[Reject Tool Call]
    CheckOutbound -->|Yes| AllowOut
    CheckOutbound -->|No| RejectOut
    AllowOut --> Deliver[Send Message]
    RejectOut --> ReturnErr[Return Error to LLM]
```

Sources: Inferred from allowlist system description in high-level diagrams

---

## Message Processing

### PersistentAgentMessage Model

All inbound and outbound messages are stored in `PersistentAgentMessage`:

```mermaid
classDiagram
    class PersistentAgentMessage {
        +UUID id
        +PersistentAgent owner_agent
        +PersistentAgentConversation conversation
        +CommsChannel channel
        +str direction (inbound/outbound)
        +str sender_address
        +str recipient_address
        +str subject
        +str body
        +JSONField metadata
        +DeliveryStatus status
        +str provider_message_id
        +datetime timestamp
        +datetime delivered_at
    }
    
    class PersistentAgentConversation {
        +UUID id
        +PersistentAgent agent
        +str subject
        +datetime created_at
        +datetime updated_at
    }
    
    class PersistentAgentMessageAttachment {
        +UUID id
        +PersistentAgentMessage message
        +str filename
        +str content_type
        +int size_bytes
        +FileField file
    }
    
    PersistentAgentMessage --> PersistentAgentConversation : conversation
    PersistentAgentMessageAttachment --> PersistentAgentMessage : message
```

Sources: [api/models.py:2900-3100]()

**Key Fields:**
- **direction**: `"inbound"` or `"outbound"`
- **channel**: CommsChannel enum (EMAIL, SMS, etc.)
- **sender_address/recipient_address**: Email or phone in canonical format
- **subject**: Email subject (null for SMS)
- **body**: Message content
- **metadata**: Provider-specific data (headers, timestamps, etc.)
- **status**: DeliveryStatus tracking
- **provider_message_id**: Twilio SID or email message ID for tracking

### Conversation Threading

Messages are grouped into `PersistentAgentConversation` threads for context:

**Email Threading:**
- Messages with same subject (normalized) linked to conversation
- References/In-Reply-To headers used when available
- Fallback: sender address + time proximity

**SMS Threading:**
- Messages with same sender grouped into conversation
- Each phone number creates separate conversation thread

Sources: [api/agent/comms/message_service.py]() referenced in [console/views.py:103]()

### Message Compaction

To manage prompt token limits, message history is compacted:

1. **Recent Messages**: Last N messages kept verbatim
2. **Older Messages**: Summarized via `llm_summarise_comms()`
3. **Snapshots**: Compressed summaries stored in `PersistentAgentCommsSnapshot`

Configuration in event processing:
- `MESSAGE_HISTORY_LIMIT = 20`: Recent messages to keep

Sources: [api/agent/core/event_processing.py:48,108]()

---

## Agent Communication Tools

### send_email Tool

**Function:** `execute_send_email()` in [api/agent/tools/email_sender.py]()

**LLM Schema:**
```json
{
  "name": "send_email",
  "description": "Send an email message to a contact",
  "parameters": {
    "to": {"type": "string", "description": "Recipient email address"},
    "subject": {"type": "string", "description": "Email subject line"},
    "body": {"type": "string", "description": "Email body content"},
    "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients (optional)"},
    "bcc": {"type": "array", "items": {"type": "string"}, "description": "BCC recipients (optional)"}
  }
}
```

**Tool Registration:**
- Registered in `get_send_email_tool()` 
- Exposed to LLM during `_run_agent_loop()`
- Credit cost: Configurable per-tool override or default task cost

**Execution Steps:**
1. Validate recipient against allowlist
2. Create outbound `PersistentAgentMessage`
3. Select email account (agent's `AgentEmailAccount`)
4. Send via SMTP or provider API
5. Update message delivery status
6. Return message ID to LLM

Sources: [api/agent/core/event_processing.py:63]()

### send_sms Tool

**Function:** `execute_send_sms()` in [api/agent/tools/sms_sender.py]()

**LLM Schema:**
```json
{
  "name": "send_sms",
  "description": "Send an SMS text message to a phone number",
  "parameters": {
    "to": {"type": "string", "description": "Recipient phone number (E.164 format)"},
    "body": {"type": "string", "description": "Message text (max length configured)"}
  }
}
```

**Tool Registration:**
- Registered in `get_send_sms_tool()`
- Exposed to LLM during `_run_agent_loop()`
- Credit cost: Configurable per-tool override or default task cost

**Execution Steps:**
1. Validate phone number format (E.164)
2. Check recipient against allowlist
3. Create outbound `PersistentAgentMessage`
4. Select SMS number (agent's `SmsNumber`)
5. Send via Twilio Messaging Service
6. Update message with Twilio SID
7. Return message ID to LLM

Sources: [api/agent/core/event_processing.py:64]()

---

## Configuration Reference

### Email Provider Settings

| Variable | Purpose | Default |
|----------|---------|---------|
| `MAILGUN_ENABLED` | Enable Mailgun provider | `False` (community), depends on API key (proprietary) |
| `MAILGUN_API_KEY` | Mailgun API key | `""` |
| `MAILGUN_SENDER_DOMAIN` | Mailgun verified domain | From proprietary defaults |
| `MAILGUN_INCOMING_WEBHOOK_TOKEN` | Inbound webhook auth token | `"dummy-mailgun-incoming-token"` |
| `POSTMARK_ENABLED` | Enable Postmark provider | `False` (community), depends on token (proprietary) |
| `POSTMARK_SERVER_TOKEN` | Postmark server token | `""` |
| `POSTMARK_INCOMING_WEBHOOK_TOKEN` | Inbound webhook auth token | `"dummy-postmark-incoming-token"` |
| `SIMULATE_EMAIL_DELIVERY` | Skip actual email sending (dev) | `True` (non-prod), `False` (prod) |

Sources: [config/settings.py:451-456,691-708,822-823,829-834]()

### IMAP/SMTP Settings

Configured per `AgentEmailAccount`, not global environment variables:
- **IMAP Server/Port/SSL**: Agent-specific connection details
- **SMTP Server/Port/Encryption**: Agent-specific sending configuration
- **Password**: Encrypted with `GOBII_ENCRYPTION_KEY`

### IMAP IDLE Watcher Settings

| Variable | Purpose | Default |
|----------|---------|---------|
| `IMAP_IDLE_ENABLED` | Enable IDLE watcher | `False` |
| `IMAP_IDLE_MAX_CONNECTIONS` | Max watchers per runner | 200 |
| `IMAP_IDLE_SCAN_INTERVAL_SEC` | Account rescan interval | 30 |
| `IMAP_IDLE_REISSUE_SEC` | Re-issue IDLE interval | 1500 |
| `IMAP_IDLE_DEBOUNCE_SEC` | Debounce duplicate polls | 10 |
| `IMAP_IDLE_LEASE_TTL_SEC` | Cross-runner lease TTL | 60 |

Sources: [config/settings.py:808-820]()

### SMS/Twilio Settings

| Variable | Purpose | Default |
|----------|---------|---------|
| `TWILIO_ENABLED` | Enable Twilio SMS | `False` |
| `TWILIO_ACCOUNT_SID` | Twilio account ID | `""` |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | `""` |
| `TWILIO_MESSAGING_SERVICE_SID` | Messaging service for sends | `""` |
| `TWILIO_VERIFY_SERVICE_SID` | Verify service for phone verification | `""` |
| `TWILIO_INCOMING_WEBHOOK_TOKEN` | Inbound webhook auth token | `"dummy-twilio-incoming-webhook-token"` |
| `SMS_MAX_BODY_LENGTH` | Max SMS body length | 1450 |

Sources: [config/settings.py:837-866]()

### Email Parsing Settings

| Variable | Purpose | Default |
|----------|---------|---------|
| `EMAIL_STRIP_REPLIES` | Strip quoted replies from email body | `False` |

Sources: [config/settings.py:870]()

---

## Admin Interface

### AgentEmailAccount Admin

**Location:** Django admin at `/admin/api/agentemailaccount/`

**Features:**
- Create/edit email accounts with IMAP/SMTP settings
- Test email sending via admin action
- View last check timestamp for IMAP polling
- Activate/deactivate accounts
- Password fields use custom widget for encryption

**Form:** `AgentEmailAccountForm` in [api/admin.py:13]()

Sources: [api/admin.py:1950-2050]()

### SMS Number Admin

**Location:** Django admin at `/admin/api/smsnumber/`

**Features:**
- View provisioned Twilio numbers
- Sync numbers from Twilio (admin action)
- Test SMS sending (admin action via `send_test_sms`)
- View number capabilities (SMS/MMS/Voice)
- Activate/deactivate numbers

**Test SMS Form:** `TestSmsForm` in [api/admin.py:13]()

Sources: [api/admin.py:1850-1950]()

### CommsAllowlistEntry Admin

**Location:** Django admin at `/admin/api/commsallowlistentry/`

**Features:**
- Add/edit allowlist entries
- Filter by agent, channel, inbound/outbound permissions
- Search by address
- Bulk enable/disable entries
- Notes field for documentation

Sources: [api/admin.py:3100-3200]()

---

## Integration Examples

### Email Account Setup Flow

```mermaid
sequenceDiagram
    participant Admin as Platform Admin
    participant UI as Console UI
    participant Form as AgentEmailAccountForm
    participant Model as AgentEmailAccount
    participant Crypto as Encryption
    participant DB
    
    Admin->>UI: Navigate to agent settings
    UI->>Form: Display email account form
    Admin->>Form: Enter IMAP/SMTP credentials
    Form->>Crypto: encrypt_value(password)
    Crypto-->>Form: Encrypted bytes
    Form->>Model: Create AgentEmailAccount
    Model->>DB: Save with encrypted_password
    DB-->>Model: Record created
    Model->>Model: Create PersistentAgentEmailEndpoint
    Model-->>UI: Account ready
```

**Console View:** Agent email configuration at `/console/agents/{id}/contacts/`

Sources: [console/views.py:106](), [api/models.py:2400-2600]()

### SMS Number Provisioning Flow

```mermaid
sequenceDiagram
    participant Admin as Platform Admin
    participant Beat as Celery Beat
    participant Task as sync_twilio_numbers
    participant Twilio
    participant DB
    participant UI as Console UI
    
    Beat->>Task: Hourly trigger
    Task->>Twilio: GET /IncomingPhoneNumbers
    Twilio-->>Task: Number list with SIDs
    Task->>DB: Update/Create SmsNumber records
    DB-->>Task: Synced
    
    Admin->>UI: Assign SMS to agent
    UI->>DB: Create PersistentAgentSmsEndpoint
    DB-->>UI: Endpoint ready
```

Sources: [config/settings.py:591-596](), [api/models.py:2100-2300]()

### Message Webhook Processing Flow

```mermaid
sequenceDiagram
    participant Ext as External Sender
    participant Provider as Email/SMS Provider
    participant Hook as Webhook View
    participant Auth as Token Verification
    participant Allow as Allowlist Check
    participant DB
    participant Queue as Celery
    participant Agent as process_agent_events_task
    
    Ext->>Provider: Send message
    Provider->>Hook: POST webhook
    Hook->>Auth: Verify token
    Auth-->>Hook: Valid
    Hook->>DB: Find agent by address
    DB-->>Hook: PersistentAgent + Endpoint
    Hook->>Allow: Check allowlist
    Allow-->>Hook: Allowed
    Hook->>DB: Create PersistentAgentMessage
    Hook->>Queue: process_agent_events_task.delay()
    Queue->>Agent: Execute agent loop
    Agent->>Agent: Process message in context
```

Sources: High-level architecture diagram and inferred webhook flow

---

## Security Considerations

### Credential Storage

- **Email Passwords**: Encrypted with `GOBII_ENCRYPTION_KEY` using `encrypt_value()`/`decrypt_value()` from `util.encryption`
- **Provider Tokens**: Stored in `provider_config` JSON field, also encrypted
- **Webhook Tokens**: Environment variables, not stored in database

**Key Rotation:** Changing `GOBII_ENCRYPTION_KEY` requires re-encrypting all stored credentials.

Sources: [api/models.py:2400-2600]()

### Webhook Authentication

All inbound webhooks require token verification:
- Email: `POSTMARK_INCOMING_WEBHOOK_TOKEN` or `MAILGUN_INCOMING_WEBHOOK_TOKEN`
- SMS: `TWILIO_INCOMING_WEBHOOK_TOKEN`

Tokens appended as query parameters or headers depending on provider.

Sources: [config/settings.py:822-823,863]()

### Allowlist Enforcement

- **Default Policy:** Implicit allow for owner/org members (configurable)
- **Manual Policy:** Explicit allow required (stricter)
- **Directional Permissions:** Separate inbound/outbound controls
- **Rejection Logging:** Blocked messages logged but not processed

Sources: Inferred from allowlist system architecture

### Rate Limiting

Currently not enforced at the email/SMS layer. Plan-level rate limits apply to overall agent task execution but not per-channel message sending.

**Future Consideration:** Per-channel rate limits to prevent abuse.

---

## Troubleshooting

### Email Not Sending

**Symptoms:** Outbound emails created but status stuck in `QUEUED` or `SENDING`

**Checks:**
1. Verify `SIMULATE_EMAIL_DELIVERY=False` in production
2. Check SMTP credentials in `AgentEmailAccount`
3. Review SMTP server logs for connection errors
4. Confirm recipient in allowlist (`allow_outbound=True`)
5. Check `AgentEmailAccount.is_active=True`

### Email Not Received

**Symptoms:** External emails sent but agent not processing

**Checks:**
1. Verify IMAP credentials if using IDLE watcher
2. Check `IMAP_IDLE_ENABLED=True` if relying on IDLE
3. Confirm webhook URL configured in provider (Postmark/Mailgun)
4. Verify webhook token matches environment variable
5. Check sender in allowlist (`allow_inbound=True`)
6. Review `AgentEmailAccount.last_check_at` timestamp

### SMS Not Sending

**Symptoms:** Outbound SMS created but not delivered

**Checks:**
1. Verify `TWILIO_ENABLED=True`
2. Confirm `TWILIO_MESSAGING_SERVICE_SID` configured
3. Check recipient phone in E.164 format
4. Verify recipient in allowlist (`allow_outbound=True`)
5. Review Twilio console for delivery failures
6. Confirm `SmsNumber.is_active=True`

### SMS Not Received

**Symptoms:** External SMS sent but agent not processing

**Checks:**
1. Verify webhook URL configured in Twilio console
2. Check `TWILIO_INCOMING_WEBHOOK_TOKEN` matches webhook URL
3. Confirm sender in allowlist (`allow_inbound=True`)
4. Review Twilio webhook logs for errors
5. Check `PersistentAgentSmsEndpoint` exists and is active

Sources: General troubleshooting patterns inferred from architecture

---

## Related Systems

- **Agent Web Chat** ([#7.1](#7.1)): Real-time browser-based messaging
- **Peer Messaging** ([#7.3](#7.3)): Agent-to-agent direct communication
- **Agent Event Processing** ([#4.3](#4.3)): Core loop that processes inbound messages
- **Communication Systems** ([#7](#7)): Parent section covering all communication channels

---

# Page: Peer Messaging

# Peer Messaging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [api/agent/peer_comm.py](api/agent/peer_comm.py)
- [api/agent/peer_link_signals.py](api/agent/peer_link_signals.py)
- [api/agent/tools/peer_dm.py](api/agent/tools/peer_dm.py)
- [api/apps.py](api/apps.py)
- [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py](api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py)
- [tests/unit/test_agent_short_description.py](tests/unit/test_agent_short_description.py)
- [tests/unit/test_peer_agent_messaging.py](tests/unit/test_peer_agent_messaging.py)

</details>



## Purpose and Scope

This document describes the **Peer Messaging** subsystem, which enables direct agent-to-agent communication within the gobii-platform. This system allows `PersistentAgent` instances to send messages to each other through a quota-enforced, debounced messaging channel.

For web-based user-to-agent chat, see [Agent Web Chat](#7.1). For external communication via email and SMS, see [Email & SMS](#7.2).

**Sources:** [api/agent/peer_comm.py:1-329]()

---

## Overview

The Peer Messaging system provides a structured communication channel for agents to coordinate tasks without external communication overhead. Unlike email or SMS channels, peer messaging operates entirely within the platform's internal data model and enforces strict quotas to prevent message loops and runaway costs.

Key characteristics:
- **Bidirectional Links**: Two agents are connected via an `AgentPeerLink` with symmetric quota policies
- **Quota Enforcement**: Rate limiting via rolling windows (e.g., 30 messages per 6 hours)
- **Debouncing**: 5-second minimum interval between messages to prevent rapid loops
- **Automatic Wake-up**: Receiving agents are automatically triggered for event processing
- **Lifecycle Integration**: Messages can wake `EXPIRED` agents if they remain active

**Sources:** [api/agent/peer_comm.py:50-102](), [tests/unit/test_peer_agent_messaging.py:1-235]()

---

## Core Data Models

The peer messaging system uses three primary models to manage links, state, and message records.

### Model Relationship Diagram

```mermaid
erDiagram
    AgentPeerLink ||--o{ AgentCommPeerState : "tracks quota for"
    AgentPeerLink ||--o| PersistentAgentConversation : "owns conversation"
    PersistentAgent ||--o{ AgentPeerLink : "agent_a"
    PersistentAgent ||--o{ AgentPeerLink : "agent_b"
    PersistentAgentConversation ||--o{ PersistentAgentMessage : "contains"
    PersistentAgent ||--o{ PersistentAgentMessage : "owner_agent"
    PersistentAgent ||--o{ PersistentAgentMessage : "peer_agent"
    
    AgentPeerLink {
        uuid id
        string pair_key
        int messages_per_window
        int window_hours
        bool is_enabled
        string feature_flag
    }
    
    AgentCommPeerState {
        uuid id
        string channel
        int messages_per_window
        int window_hours
        int credits_remaining
        datetime window_reset_at
        datetime last_message_at
        int debounce_seconds
    }
    
    PersistentAgentConversation {
        uuid id
        bool is_peer_dm
        string address
    }
    
    PersistentAgentMessage {
        uuid id
        bool is_outbound
        string body
        datetime timestamp
    }
```

**Sources:** [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py:1-120]()

### AgentPeerLink

The `AgentPeerLink` model establishes a bidirectional relationship between two agents. It uses a deterministic `pair_key` constructed from sorted agent IDs to ensure uniqueness regardless of creation order.

| Field | Type | Description |
|-------|------|-------------|
| `agent_a` | ForeignKey | First agent in the sorted pair |
| `agent_b` | ForeignKey | Second agent in the sorted pair |
| `pair_key` | CharField(96) | Unique key: `{sorted_ids[0]},{sorted_ids[1]}` |
| `messages_per_window` | PositiveInteger | Quota limit (1-500, default 30) |
| `window_hours` | PositiveInteger | Rolling window duration (1-168, default 6) |
| `is_enabled` | Boolean | Global enable/disable toggle |
| `feature_flag` | CharField(64) | Optional Waffle flag name |
| `conversation` | OneToOne | Associated `PersistentAgentConversation` |

**Sources:** [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py:34-45](), [api/agent/peer_comm.py:60-102]()

### AgentCommPeerState

Tracks quota consumption and enforces rate limits for a specific `AgentPeerLink`. One state record exists per link per channel (peer messaging uses `CommsChannel.OTHER`).

| Field | Type | Description |
|-------|------|-------------|
| `link` | ForeignKey | Associated `AgentPeerLink` |
| `channel` | CharField | Channel type (always `OTHER` for peer DMs) |
| `credits_remaining` | PositiveInteger | Messages left in current window |
| `window_reset_at` | DateTimeField | When quota resets |
| `last_message_at` | DateTimeField | Timestamp of last send (for debouncing) |
| `debounce_seconds` | PositiveInteger | Minimum interval between sends (default 5) |

The state is locked via `select_for_update()` during message sends to prevent race conditions.

**Sources:** [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py:18-32](), [api/agent/peer_comm.py:214-251]()

### PersistentAgentMessage Extensions

Peer messages extend the existing `PersistentAgentMessage` model with two fields:

- `peer_agent`: ForeignKey to the other agent in the conversation
- New index: `pa_msg_peer_agent_idx` on `(peer_agent, -timestamp)`

Each peer DM creates **two** message records:
1. **Outbound** record owned by the sending agent (with `is_outbound=True`)
2. **Inbound** record owned by the receiving agent (with `is_outbound=False`)

Both messages link to the same `PersistentAgentConversation` (where `is_peer_dm=True`).

**Sources:** [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py:52-59](), [api/agent/peer_comm.py:169-189]()

---

## Message Flow

### Sequence Diagram: Sending a Peer Message

```mermaid
sequenceDiagram
    participant AgentA as "Agent A<br/>(sender)"
    participant Tool as "send_agent_message tool"
    participant Service as "PeerMessagingService"
    participant State as "AgentCommPeerState"
    participant DB as "Database<br/>(PostgreSQL)"
    participant Celery as "Celery Queue"
    participant AgentB as "Agent B<br/>(receiver)"
    
    AgentA->>Tool: execute_send_agent_message()
    Tool->>Service: __init__(agent_a, agent_b)
    Service->>DB: Load AgentPeerLink
    DB-->>Service: link with pair_key
    
    Service->>Service: Check is_enabled & feature_flag
    
    AgentA->>Service: send_message("handoff")
    
    Service->>DB: SELECT FOR UPDATE AgentCommPeerState
    DB-->>Service: locked state
    
    Service->>Service: Check debounce<br/>(elapsed >= 5s?)
    
    alt Debounced
        Service-->>AgentA: PeerMessagingError<br/>status=debounced
    end
    
    Service->>Service: Check credits_remaining > 0
    
    alt Quota Exhausted
        Service->>Celery: schedule follow-up at window_reset_at
        Service-->>AgentA: PeerMessagingError<br/>status=throttled
    end
    
    Service->>State: credits_remaining -= 1
    Service->>State: last_message_at = now()
    State->>DB: UPDATE state
    
    Service->>DB: Ensure PersistentAgentConversation
    Service->>DB: Ensure PersistentAgentCommsEndpoint
    
    Service->>DB: Create outbound message<br/>(owner=agent_a)
    Service->>DB: Create inbound message<br/>(owner=agent_b)
    
    Service->>DB: UPDATE agent_b.last_interaction_at
    Service->>DB: Check agent_b.life_state
    
    alt Agent B is EXPIRED and active
        Service->>DB: UPDATE life_state=ACTIVE
    end
    
    Service->>DB: COMMIT transaction
    
    DB->>Celery: on_commit() hook
    Celery->>AgentB: process_agent_events_task.delay(agent_b.id)
    
    Service-->>AgentA: PeerSendResult<br/>status=ok<br/>remaining_credits<br/>window_reset_at
```

**Sources:** [api/agent/peer_comm.py:103-213](), [api/agent/tools/peer_dm.py:42-110]()

### PeerMessagingService._lock_state() Logic

The `_lock_state()` method acquires an exclusive lock on the `AgentCommPeerState` record and performs several normalization steps:

1. **Get or Create**: Acquires state with `select_for_update().get_or_create()`
2. **Sync Quota Config**: Copies `messages_per_window` and `window_hours` from the link if changed
3. **Reset Window**: If `window_reset_at <= now`, resets `credits_remaining` and advances `window_reset_at`
4. **Cap Credits**: If `credits_remaining > messages_per_window`, clamps to the max
5. **Debounce Default**: Ensures `debounce_seconds >= 5`

This ensures quota configuration changes on the link are reflected in the state before consumption.

**Sources:** [api/agent/peer_comm.py:214-251]()

---

## Quota and Rate Limiting

### Rolling Window Quota

The quota system uses a **rolling window** approach:
- Each link defines `messages_per_window` (e.g., 30) and `window_hours` (e.g., 6)
- When the window expires (`window_reset_at <= now`), credits fully replenish
- Credits decrement with each send; sends fail when `credits_remaining == 0`

### Debouncing

To prevent rapid message loops, the system enforces a **minimum 5-second interval** between consecutive sends:

```python
if state.last_message_at is not None:
    elapsed = (now - state.last_message_at).total_seconds()
    if elapsed < state.debounce_seconds:
        retry_at = state.last_message_at + timedelta(seconds=state.debounce_seconds)
        raise PeerMessagingError(
            "Peer messaging suppressed to avoid a rapid loop.",
            status="debounced",
            retry_at=retry_at,
        )
```

This prevents agents from immediately replying to each other in tight loops.

**Sources:** [api/agent/peer_comm.py:115-129]()

### Quota Exhaustion Handling

When quota is exhausted (`credits_remaining <= 0`), the service:
1. Raises `PeerMessagingError` with `status="throttled"`
2. Schedules a follow-up task at `window_reset_at` via `apply_async(eta=...)`
3. Returns `retry_at` in the exception so the tool can inform the LLM

The scheduled follow-up ensures the sending agent resumes processing when quota replenishes.

**Sources:** [api/agent/peer_comm.py:131-143](), [api/agent/peer_comm.py:314-328]()

### Quota Configuration Table

| Parameter | Min | Max | Default | Purpose |
|-----------|-----|-----|---------|---------|
| `messages_per_window` | 1 | 500 | 30 | Maximum messages per window |
| `window_hours` | 1 | 168 | 6 | Window duration (168h = 1 week) |
| `debounce_seconds` | 5 | N/A | 5 | Minimum send interval |

**Sources:** [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py:23-24]()

---

## Tool Integration

### send_agent_message Tool Schema

Agents discover peer messaging via the `send_agent_message` tool, which is exposed to the LLM with this schema:

```json
{
  "type": "function",
  "function": {
    "name": "send_agent_message",
    "description": "Send a concise direct message to another agent that shares a peer link with you. Use this to coordinate tasks with partner agents. Keep messages focused and avoid loops.",
    "parameters": {
      "type": "object",
      "properties": {
        "peer_agent_id": {
          "type": "string",
          "description": "UUID of the linked agent you want to contact."
        },
        "message": {
          "type": "string",
          "description": "The body of the message to send. Keep it brief and actionable."
        }
      },
      "required": ["peer_agent_id", "message"]
    }
  }
}
```

**Sources:** [api/agent/tools/peer_dm.py:14-39]()

### execute_send_agent_message() Function

The tool executor validates parameters, constructs a `PeerMessagingService`, and calls `send_message()`:

**Input Validation:**
- Ensures `peer_agent_id` and `message` are provided
- Parses `peer_agent_id` as UUID (raises error if invalid)
- Prevents self-messaging (`peer_agent_uuid == agent.id`)
- Verifies target agent exists in database

**Success Response:**
```python
{
    "status": "ok",
    "message": "Peer message delivered.",
    "remaining_credits": 29,
    "window_reset_at_iso": "2025-01-15T12:00:00Z",
    "auto_sleep_ok": True
}
```

The `auto_sleep_ok` flag signals the event processor that the agent can safely sleep after sending a handoff message.

**Error Responses:**
- `status="error"`: Invalid parameters, missing link, or unexpected failure
- `status="debounced"`: Message sent too soon (includes `retry_at_iso`)
- `status="throttled"`: Quota exhausted (includes `retry_at_iso`)
- `status="disabled"`: Link disabled or feature flag inactive

**Sources:** [api/agent/tools/peer_dm.py:42-110]()

---

## Lifecycle Integration

### Waking Expired Agents

When a peer message arrives, the `PeerMessagingService._touch_peer_agent()` method performs lifecycle checks on the receiving agent:

```python
def _touch_peer_agent(self, now) -> None:
    locked = PersistentAgent.objects.select_for_update().get(id=self.peer_agent.id)
    
    updates = ["last_interaction_at"]
    locked.last_interaction_at = now
    
    if (locked.life_state == PersistentAgent.LifeState.EXPIRED
        and locked.is_active):
        if locked.schedule_snapshot:
            locked.schedule = locked.schedule_snapshot
            updates.append("schedule")
        locked.life_state = PersistentAgent.LifeState.ACTIVE
        updates.append("life_state")
    
    locked.save(update_fields=updates)
```

This means **peer messages can revive expired agents** if they remain active, restoring their schedule and transitioning them back to `ACTIVE` state.

**Sources:** [api/agent/peer_comm.py:285-306]()

### Automatic Event Processing

After creating the inbound message, the service triggers processing on the receiver:

```python
transaction.on_commit(
    lambda: self._enqueue_processing(self.peer_agent.id)
)
```

This queues `process_agent_events_task.delay(agent_b.id)`, ensuring the receiving agent processes the new message immediately after transaction commit.

**Sources:** [api/agent/peer_comm.py:195-197](), [api/agent/peer_comm.py:308-312]()

---

## Conversation Threading

### PersistentAgentConversation for Peer DMs

Each `AgentPeerLink` has an associated `PersistentAgentConversation` with these properties:
- `is_peer_dm=True` to distinguish from external channels
- `peer_link` references back to the `AgentPeerLink`
- `channel=CommsChannel.OTHER`
- `address` format: `peer://{pair_key}`
- `display_name` format: `"{agent_a.name} <-> {agent_b.name}"`

The conversation is lazily created on first message send via `_ensure_conversation()`.

**Sources:** [api/agent/peer_comm.py:253-270]()

### PersistentAgentCommsEndpoint

Each agent in a peer link gets a synthetic endpoint with:
- `channel=CommsChannel.OTHER`
- `address=f"peer://agent/{agent.id}"`
- `is_primary=False`

This endpoint is used as the `from_endpoint` on both outbound and inbound message records.

**Sources:** [api/agent/peer_comm.py:272-283]()

---

## Error Handling

### PeerMessagingError Exception

Custom exception class with three attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | str | Human-readable error description |
| `status` | str | Machine-readable status code |
| `retry_at` | datetime | Optional timestamp when retry is allowed |

**Sources:** [api/agent/peer_comm.py:30-36]()

### Status Codes

| Status | Trigger Condition | Retry Behavior |
|--------|------------------|----------------|
| `ok` | Message sent successfully | N/A |
| `error` | Validation failure, missing link, self-send | Manual correction needed |
| `disabled` | `is_enabled=False` or feature flag inactive | Admin must enable link |
| `debounced` | Message sent within `debounce_seconds` | Automatic retry after `retry_at` |
| `throttled` | `credits_remaining == 0` | Automatic retry at `window_reset_at` |

**Sources:** [api/agent/tools/peer_dm.py:84-91](), [api/agent/peer_comm.py:71-99]()

---

## Signal Handlers

### AgentPeerLink Post-Save Signal

The `handle_peer_link_created` signal receiver was originally designed to send introduction messages when links were created but is currently disabled:

```python
@receiver(post_save, sender=AgentPeerLink)
def handle_peer_link_created(sender, instance, created, raw, **kwargs):
    if raw or not created:
        return
    
    # Intro automation disabled
    logger.info(
        "Peer link %s connects agent %s with agent %s; intro automation disabled.",
        instance.id,
        agent_a.id,
        agent_b.id,
    )
```

The signal is registered in `api/apps.py:ready()` but performs no actions, allowing future extension for automated introductions.

**Sources:** [api/agent/peer_link_signals.py:1-35](), [api/apps.py:25-30]()

---

## Testing Strategy

### Test Batches

Peer messaging tests are split across two CI batches:

| Batch | Tag | Tests |
|-------|-----|-------|
| `peer_dm` | `batch_peer_dm` | Core `PeerMessagingService` functionality |
| `peer_intro` | `batch_peer_intro` | Signal handler behavior (intro automation) |

**Sources:** [.github/workflows/ci.yml:147-150]()

### Key Test Cases

**PeerMessagingServiceTests** (`batch_peer_dm`):
- `test_send_message_creates_records_and_triggers_processing`: Verifies dual message creation and Celery task triggering
- `test_debounce_prevents_rapid_repeat`: Confirms 5-second debounce enforcement
- `test_throttle_when_quota_exhausted`: Tests quota exhaustion and follow-up scheduling
- `test_execute_tool_handles_errors`: Validates error responses for invalid inputs
- `test_execute_tool_success_sets_auto_sleep_flag`: Checks `auto_sleep_ok` flag behavior

**AgentPeerLinkSignalTests** (`batch_peer_intro`):
- `test_peer_link_creation_skips_intro_steps_and_processing`: Confirms signal fires but doesn't create steps

**Sources:** [tests/unit/test_peer_agent_messaging.py:20-235]()

---

## Configuration and Setup

### Creating a Peer Link

Peer links are created via Django ORM:

```python
link = AgentPeerLink.objects.create(
    agent_a=agent_alpha,
    agent_b=agent_beta,
    messages_per_window=30,
    window_hours=6,
    created_by=user,
    is_enabled=True,
)
```

The `pair_key` is automatically generated using `AgentPeerLink.build_pair_key(agent_a.id, agent_b.id)`.

**Sources:** [tests/unit/test_peer_agent_messaging.py:58-64]()

### Feature Flags

Optional rollout control via Waffle:

```python
link = AgentPeerLink.objects.create(
    agent_a=agent_alpha,
    agent_b=agent_beta,
    feature_flag="peer_messaging_v2",
    ...
)
```

The service checks `flag_is_active(None, link.feature_flag)` before allowing sends.

**Sources:** [api/agent/peer_comm.py:82-99]()

### Disabling a Link

Set `is_enabled=False` to prevent all peer messaging on a link:

```python
link.is_enabled = False
link.save()
```

Attempts to send will raise `PeerMessagingError` with `status="disabled"`.

**Sources:** [api/agent/peer_comm.py:76-80]()

---

## Architecture Summary Diagram

```mermaid
graph TB
    subgraph "Agent Event Processing"
        AgentLoop["_run_agent_loop"]
        ToolDispatch["Tool Call Dispatcher"]
    end
    
    subgraph "Peer Messaging Tool"
        ToolSchema["send_agent_message<br/>tool schema"]
        ToolExecutor["execute_send_agent_message()"]
    end
    
    subgraph "Core Service"
        PeerService["PeerMessagingService"]
        SendMessage["send_message()"]
        LockState["_lock_state()"]
        TouchPeer["_touch_peer_agent()"]
    end
    
    subgraph "Data Models"
        PeerLink["AgentPeerLink<br/>pair_key, quotas"]
        PeerState["AgentCommPeerState<br/>credits, debounce"]
        Conversation["PersistentAgentConversation<br/>is_peer_dm=True"]
        Messages["PersistentAgentMessage<br/>dual records"]
    end
    
    subgraph "Processing Queue"
        CeleryQueue["process_agent_events_task"]
        FollowUp["apply_async(eta=...)"]
    end
    
    AgentLoop --> ToolDispatch
    ToolDispatch --> ToolSchema
    ToolSchema --> ToolExecutor
    
    ToolExecutor --> PeerService
    PeerService --> SendMessage
    SendMessage --> LockState
    LockState --> PeerState
    
    SendMessage --> PeerLink
    SendMessage --> Conversation
    SendMessage --> Messages
    SendMessage --> TouchPeer
    
    SendMessage -.->|on_commit| CeleryQueue
    SendMessage -.->|quota exhausted| FollowUp
    
    CeleryQueue -.->|wakes receiver| AgentLoop
    
    PeerLink --> PeerState
    PeerLink --> Conversation
```

**Sources:** [api/agent/peer_comm.py:1-329](), [api/agent/tools/peer_dm.py:1-111](), [api/models.py (implied)]()

---

# Page: User Interfaces

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agents/services.py](agents/services.py)
- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/models.py](api/models.py)
- [console/templates/partials/_agent_contact_form.html](console/templates/partials/_agent_contact_form.html)
- [console/views.py](console/views.py)
- [pages/templates/ai_directory/detail.html](pages/templates/ai_directory/detail.html)
- [pages/templates/ai_directory/index.html](pages/templates/ai_directory/index.html)
- [pages/templates/home.html](pages/templates/home.html)
- [pages/views.py](pages/views.py)
- [tests/unit/test_agent_limits.py](tests/unit/test_agent_limits.py)
- [tests/unit/test_ai_employee_directory.py](tests/unit/test_ai_employee_directory.py)
- [tests/unit/test_console_context.py](tests/unit/test_console_context.py)

</details>



**Purpose**: This document covers the web-based user interfaces in the gobii-platform, including the console dashboard, homepage with agent spawning, and the AI employee directory. These interfaces provide the primary user experience for creating and managing persistent agents, viewing usage metrics, and configuring billing.

**Scope**: This page focuses on the view layer, templates, and UI interaction patterns. For backend API endpoints, see [REST API](#9.1). For agent creation logic, see [Creating Agents](#4.1). For billing system internals, see [Credit & Billing System](#5).

---

## UI Layer Architecture

The platform uses a traditional Django view/template architecture with progressive enhancement via HTMX for dynamic interactions. The UI layer is organized into three main areas:

1. **Console** (`/console/*`) - Authenticated management dashboard
2. **Homepage** (`/`) - Public landing page with agent spawn form
3. **AI Employee Directory** (`/ai-employees/*`) - Curated template gallery

All views inherit from mixins that provide common context data including authentication state, current console context (personal vs organization), and usage metrics.

**Sources**: [console/views.py:1-2570](), [pages/views.py:1-477]()

---

## Console Interface

### ConsoleHome Dashboard

The `ConsoleHome` view ([console/views.py:351-577]()) serves as the primary management interface. It displays:

- Agent count and task statistics
- Credit balance and usage percentage  
- API key management shortcuts
- Task status breakdown (completed, in progress, failed, cancelled)
- Pending agent transfer invitations

The dashboard context varies based on whether the user is in **personal** or **organization** mode:

```mermaid
graph TB
    Request[HTTP Request] --> ConsoleHome["ConsoleHome.get_context_data()"]
    ConsoleHome --> BuildContext["build_console_context(request)"]
    
    BuildContext --> ContextType{Context Type?}
    
    ContextType -->|Personal| PersonalMetrics["Load Personal Metrics"]
    ContextType -->|Organization| OrgMetrics["Load Organization Metrics"]
    
    PersonalMetrics --> PersonalAgents["PersistentAgent.objects.filter(user=user)"]
    PersonalMetrics --> PersonalTasks["BrowserUseAgentTask.objects.filter(user=user)"]
    PersonalMetrics --> UserCredits["TaskCreditService.calculate_available_tasks(user)"]
    
    OrgMetrics --> OrgAgents["PersistentAgent.objects.filter(organization=org)"]
    OrgMetrics --> OrgTasks["Filter tasks by org-owned agents"]
    OrgMetrics --> OrgCredits["TaskCredit.objects.filter(organization=org)"]
    
    PersonalAgents --> RenderTemplate[Render index.html]
    PersonalTasks --> RenderTemplate
    UserCredits --> RenderTemplate
    OrgAgents --> RenderTemplate
    OrgTasks --> RenderTemplate
    OrgCredits --> RenderTemplate
```

**Key Code Symbols**:
- `ConsoleViewMixin` - Base mixin providing console context to all views
- `build_console_context(request)` - Resolves current context from session
- `current_context` dict with keys: `type`, `id`, `name`

**Sources**: [console/views.py:351-577](), [console/context_helpers.py]() (referenced)

---

### Context Switching System

Users can switch between **personal** and **organization** contexts via a session-based system. The active context determines which agents, tasks, and billing information are displayed.

```mermaid
graph LR
    UserAction[User selects context] --> SwitchEndpoint["/console/switch-context/"]
    SwitchEndpoint --> ValidateMembership{Has Active<br/>Membership?}
    
    ValidateMembership -->|Yes| UpdateSession["session['context_type'] = 'organization'<br/>session['context_id'] = org.id<br/>session['context_name'] = org.name"]
    ValidateMembership -->|No| DenySwitch[403 Forbidden]
    
    UpdateSession --> NextView["Redirect to requested view"]
    NextView --> ConsoleViewMixin["ConsoleViewMixin.get_context_data()"]
    ConsoleViewMixin --> ScopedQuery["Filter queries by context"]
```

Context is stored in three session keys:
- `context_type` - Either `"personal"` or `"organization"`
- `context_id` - User ID or Organization UUID
- `context_name` - Display name for UI

**Sources**: [console/views.py:184-195](), [tests/unit/test_console_context.py:93-106]()

---

### API Key Management

The API key management interface demonstrates the HTMX-driven interaction pattern used throughout the console. The `ApiKeyListView` ([console/views.py:583-745]()) handles both listing and creation.

**Request Flow**:

1. **GET** `/console/api-keys/` - Renders full page with table
2. **POST** `/console/api-keys/` (HTMX) - Creates key, returns partial
3. **PATCH** `/console/api-keys/<id>/` (HTMX) - Revokes key
4. **DELETE** `/console/api-keys/<id>/` (HTMX) - Deletes key

The view uses `ApiKeyOwnerMixin` ([console/views.py:149-181]()) to resolve whether keys belong to the current user or the active organization context. This mixin provides:

- `api_key_context` - Dict with `type`, `organization`/`user`, `can_manage`
- `_ensure_can_manage_api_keys()` - Permission guard

**HTMX Response Pattern**:
```python
if request.htmx:
    response = render(request, "partials/_api_key_created.html", {
        "raw_key": raw_key,
        "key_id": api_key.id
    })
    response["HX-Trigger"] = json.dumps({
        "refreshApiKeysTable": None,
        "close-modal": {"id": "create-api-key-modal"},
    })
    return response
```

**Sources**: [console/views.py:583-917](), [console/views.py:149-181]()

---

### Billing Views

The `BillingView` ([console/views.py:918-1125]()) adapts its display based on context:

**Personal Context**:
- User's active subscription (from djstripe)
- Task credit balance via `TaskCreditService.calculate_available_tasks()`
- Additional tasks usage (overage tracking)
- Stripe checkout links for plan upgrades

**Organization Context**:
- Organization billing details (`OrganizationBilling` model)
- Seat management (purchased seats, pending changes)
- Organization-level credit pool
- Stripe billing portal links

The view enforces role-based access via `BILLING_MANAGE_ROLES` ([console/views.py:128-132]()):
```python
BILLING_MANAGE_ROLES = {
    OrganizationMembership.OrgRole.OWNER,
    OrganizationMembership.OrgRole.ADMIN,
    OrganizationMembership.OrgRole.BILLING,
}
```

**Sources**: [console/views.py:918-1125](), [console/org_billing_helpers.py]() (referenced)

---

## Homepage & AI Employee Directory

### Homepage Agent Spawn

The `HomePage` view ([pages/views.py:50-195]()) serves dual purposes:
1. Public landing page for unauthenticated users
2. Agent creation entry point for authenticated users

**Charter Input Flow**:

```mermaid
sequenceDiagram
    participant User
    participant HomePage as HomePage.get()
    participant Session
    participant Form as PersistentAgentCharterForm
    
    User->>HomePage: GET /?dc=<charter> OR ?g=<landing_code>
    
    alt Landing page code present
        HomePage->>LandingPage: LandingPage.objects.get(code=g)
        LandingPage-->>HomePage: charter, hero_text, image_url
        HomePage->>Form: Initialize with landing.charter
    else Default charter present
        HomePage->>Form: Initialize with dc parameter
    else Session has saved charter
        HomePage->>Session: Get agent_charter
        Session-->>HomePage: Saved charter text
        HomePage->>Form: Initialize with session charter
    end
    
    HomePage-->>User: Render home.html with form
    
    User->>HomeAgentSpawnView: POST /spawn-agent/ (form submit)
    HomeAgentSpawnView->>Session: Save charter, source='user'
    HomeAgentSpawnView->>Analytics: Track PERSISTENT_AGENT_CHARTER_SUBMIT
    
    alt User authenticated
        HomeAgentSpawnView-->>User: Redirect to /agents/create/contact/
    else Not authenticated
        HomeAgentSpawnView-->>User: Redirect to login, next=/agents/create/contact/
    end
```

**Key Template Features** ([pages/templates/home.html:1-615]()):
- Game-of-life animated background (canvas-based)
- Charter textarea with inline submit button
- Featured AI employee cards (3 shown, see below)
- Recent agents widget for authenticated users

**Sources**: [pages/views.py:50-245](), [pages/templates/home.html:100-161]()

---

### AI Employee Directory

The `AIEmployeeTemplateService` ([agents/services.py:119-265]()) provides utilities for working with curated agent templates stored in the `PersistentAgentTemplate` model.

**Directory Views**:

| View | Route | Purpose |
|------|-------|---------|
| `AIEmployeeDirectoryView` | `/ai-employees/` | Grid of all active templates with category filter |
| `AIEmployeeDetailView` | `/ai-employees/<slug>/` | Full template details, charter preview |
| `AIEmployeeHireView` | `/ai-employees/<slug>/hire/` | POST handler to initiate creation |

**Template Selection Flow**:

```mermaid
graph TB
    Browse[User browses directory] --> Filter{Filter or Search?}
    Filter -->|Category| CategoryFilter["templates.filter(category=selected)"]
    Filter -->|Search| SearchFilter["templates.filter(Q(display_name__icontains) | Q(tagline__icontains))"]
    Filter -->|None| AllTemplates["AIEmployeeTemplateService.get_active_templates()"]
    
    CategoryFilter --> EnrichTemplates[Enrich Templates]
    SearchFilter --> EnrichTemplates
    AllTemplates --> EnrichTemplates
    
    EnrichTemplates --> DescribeSchedule["template.schedule_description = AIEmployeeTemplateService.describe_schedule()"]
    DescribeSchedule --> MapTools["AIEmployeeTemplateService.get_tool_display_map()"]
    MapTools --> RenderGrid[Render template grid]
    
    RenderGrid --> UserClicksHire[User clicks 'Hire']
    UserClicksHire --> SaveToSession["session['agent_charter'] = template.charter<br/>session['ai_employee_template_code'] = template.code<br/>session['agent_charter_source'] = 'template'"]
    SaveToSession --> RedirectToContact["Redirect to /agents/create/contact/"]
```

**Schedule Description** ([agents/services.py:183-202]()):
The service converts cron expressions to human-readable text using `cron-descriptor`:
- `"0 9 * * MON-FRI"` → `"At 09:00 AM, Monday through Friday"`
- `"@daily"` → Expanded via `_CRON_MACRO_MAP` → `"At 12:00 AM"`

**Jitter Computation** ([agents/services.py:149-180]()):
Templates include `schedule_jitter_minutes` to randomize execution times:
```python
# If base_schedule = "0 10 * * *" and jitter = 15
# Random offset between -15 and +15 minutes
# Result could be "7 10 * * *" (10:07 AM)
```

**Sources**: [pages/views.py:247-374](), [agents/services.py:119-265](), [pages/templates/ai_directory/index.html:1-120]()

---

## Agent Creation Flow

The agent creation process spans multiple views and uses session state to preserve user input across steps.

### Multi-Step Process

```mermaid
stateDiagram-v2
    [*] --> HomePage: User enters charter
    HomePage --> Session1: Save charter to session
    
    Session1 --> CheckAuth: Submit form
    CheckAuth --> Login: Not authenticated
    CheckAuth --> ContactForm: Authenticated
    
    Login --> ContactForm: After login
    
    ContactForm --> ValidateContext: User submits contact info
    ValidateContext --> DenyMember: Org context + MEMBER role
    ValidateContext --> ProvisionAgent: Valid context
    
    DenyMember --> ContactForm: Show error
    
    ProvisionAgent --> CreateBrowserAgent: PersistentAgentProvisioningService.provision()
    CreateBrowserAgent --> CreatePersistentAgent
    CreatePersistentAgent --> ApplyTemplate: Template code in session?
    
    ApplyTemplate --> EnableTools: Apply template.default_tools
    ApplyTemplate --> SetSchedule: Apply template.base_schedule with jitter
    ApplyTemplate --> SetEndpoint: Apply template.recommended_contact_channel
    
    EnableTools --> ClearSession
    SetSchedule --> ClearSession
    SetEndpoint --> ClearSession
    
    ClearSession --> TriggerProcessing: transaction.on_commit()
    TriggerProcessing --> [*]: Redirect to agent detail
```

**Sources**: [pages/views.py:198-244](), [console/views.py:2064-2570]()

---

### Contact Form View

The `AgentContactFormView` ([console/views.py:2064-2570]() approximately) handles the second step of agent creation. This view demonstrates several important patterns:

**Organization Context Handling** ([console/templates/partials/_agent_contact_form.html:23-48]()):
- Dropdown to select personal vs organization ownership
- Permission check: Only `OWNER`/`ADMIN` roles can create org agents
- If current user is `MEMBER`, submit button is disabled with `aria-disabled="true"`

**Contact Method Configuration**:
The form collects:
- Email endpoint with toggle
- SMS endpoint with phone verification (inline form)
- Preferred contact method (radio buttons)

**Template Integration**:
If `session['ai_employee_template_code']` exists:
```python
template = AIEmployeeTemplateService.get_template_by_code(code)
# Pre-fill charter, schedule, tools
# Display template info card in UI
```

**Sources**: [console/templates/partials/_agent_contact_form.html:1-336](), [tests/unit/test_console_context.py:215-268]()

---

### Organization Permission Enforcement

When creating agents in organization context, the view enforces role-based permissions:

```mermaid
graph TD
    FormSubmit[User submits contact form] --> GetContext["build_console_context(request)"]
    GetContext --> CheckType{Context Type?}
    
    CheckType -->|Personal| AllowCreate[Allow creation]
    CheckType -->|Organization| CheckMembership{Membership exists?}
    
    CheckMembership -->|No| Deny403[403 Forbidden]
    CheckMembership -->|Yes| CheckRole{Role in<br/>OWNER/ADMIN?}
    
    CheckRole -->|No| ShowWarning["Render form with:<br/>show_org_permission_warning=True<br/>Button disabled"]
    CheckRole -->|Yes| AllowCreate
    
    AllowCreate --> Provision["PersistentAgentProvisioningService.provision(<br/>  user=user,<br/>  org=org if org_context else None,<br/>  charter=session['agent_charter']<br/>)"]
    
    Provision --> CreateAgents["Create BrowserUseAgent + PersistentAgent"]
    CreateAgents --> ApplyTemplate{Template in session?}
    
    ApplyTemplate -->|Yes| EnableTools["Enable template.default_tools via enable_mcp_tool()"]
    ApplyTemplate -->|No| SaveEndpoints[Save contact endpoints]
    
    EnableTools --> SaveEndpoints
    SaveEndpoints --> TriggerTask["on_commit: process_agent_events_task.delay()"]
```

**Role Constants** ([console/views.py:128-146]()):
```python
BILLING_MANAGE_ROLES = {OWNER, ADMIN, BILLING}
MEMBER_MANAGE_ROLES = {OWNER, ADMIN}
API_KEY_MANAGE_ROLES = {OWNER, ADMIN}
API_KEY_VIEW_ROLES = {OWNER, ADMIN, BILLING}
```

**Sources**: [console/views.py:2064-2570](), [tests/unit/test_console_context.py:228-268]()

---

## UI-Backend Integration Patterns

### Session Management

The platform uses Django sessions extensively for multi-step flows:

**Agent Creation Session Keys**:
- `agent_charter` - User's charter text
- `agent_charter_source` - Either `"user"` or `"template"`
- `ai_employee_template_code` - Template code if using a template
- `org_seat_portal_target` - Stripe portal redirect info (billing)
- `org_overage_detach` - Temporary overage SKU state (org billing)

**Console Context Session Keys**:
- `context_type` - `"personal"` or `"organization"`
- `context_id` - UUID string of user/org
- `context_name` - Display name

**Sources**: [pages/views.py:62-109](), [console/views.py:223-250]()

---

### Analytics Tracking

All major user actions trigger analytics events via the `Analytics` utility:

```python
# Example from homepage agent spawn
Analytics.track_event(
    user_id=request.user.id,
    event=AnalyticsEvent.PERSISTENT_AGENT_CHARTER_SUBMIT,
    source=AnalyticsSource.WEB,
    properties={
        'charter': form.cleaned_data['charter'],
        'source_page': 'home',
    }
)
```

**Organization Events** use a helper to attach org metadata ([console/views.py:197-220]()):
```python
props = _org_event_properties(request, {
    'key_id': str(api_key.id),
    'key_name': name,
})
# props now includes: organization_id, organization_name, organization_plan
```

Events are tracked via `transaction.on_commit()` to ensure the event fires only after successful DB commits.

**Sources**: [pages/views.py:213-224](), [console/views.py:197-220](), [console/views.py:707-724]()

---

### HTMX Interaction Pattern

HTMX enables partial page updates without full reloads. The pattern used throughout:

1. **Initial GET**: Render full page with `<div hx-get="...">` or `<form hx-post="...">`
2. **HTMX Request**: Detected via `request.htmx` property
3. **Partial Response**: Return only the updated fragment
4. **Client Events**: Trigger additional updates via `HX-Trigger` header

**Example**: API Key Revocation ([console/views.py:792-822]()):
```python
def patch(self, request, *args, **kwargs):
    api_key = self.get_object()
    api_key.revoke()
    
    if request.htmx:
        response = render(request, "partials/_api_key_success.html", {
            "message": f"API key '{api_key.name}' has been revoked.",
            "id": api_key.id
        })
        # Trigger client-side refresh of the specific table row
        response["HX-Trigger"] = f"refresh-row-{api_key.id}"
        return response
    else:
        # Traditional full-page redirect
        messages.success(request, f"API key '{api_key.name}' has been revoked.")
        return redirect(reverse('api_keys'))
```

**Sources**: [console/views.py:726-862]()

---

## Template Organization

The UI templates follow a consistent structure:

**Base Templates**:
- `base.html` - Global layout with nav, includes `_console_context_switch.html`
- `console_base.html` - Console-specific layout with sidebar

**Page Templates**:
- `index.html` - Console home dashboard
- `home.html` - Public homepage
- `billing.html` - Billing management
- `api_keys.html` - API key management
- `ai_directory/index.html` - Template directory
- `ai_directory/detail.html` - Template detail

**Partials** (under `partials/` or `console/templates/partials/`):
- `_agent_contact_form.html` - Agent creation step 2
- `_api_key_form.html` - API key creation form
- `_api_key_row.html` - Single API key table row
- `_api_key_created.html` - Success message with new key
- `_task_usage.html` - Credit usage widget
- `_sms_form.html` - Phone verification inline form

**Sources**: [console/templates/](), [pages/templates/]()

---

## Key UI Components

### Agent Listings

Agent lists appear on both the console home and the dedicated agents page. Each agent card displays:

- Agent name and status badge (Active/Expired)
- Schedule description (via `AIEmployeeTemplateService.describe_schedule()`)
- Listing description (generated or placeholder)
- Last interaction timestamp

**Listing Description** ([api/agent/short_description.py]() referenced):
- Initially shows placeholder text while description generates
- Async background task creates summary from charter
- Stored in `PersistentAgent.listing_description`

**Sources**: [pages/views.py:160-193](), [pages/templates/home.html:162-210]()

---

### Credit Usage Widget

The `_task_usage.html` partial ([referenced]) displays current credit balance with visual indicators:

**Personal Context**:
- `available_tasks` from `TaskCreditService.calculate_available_tasks()`
- Additional tasks enabled/used/remaining
- Percentage bar for additional tasks quota

**Organization Context**:
- `org_tasks_available` from org-owned `TaskCredit` aggregation
- `org_tasks_used_pct` percentage of org credit pool consumed

**Sources**: [console/views.py:356-509](), [pages/templates/home.html:94-98]()

---

## Summary

The UI layer provides three primary interfaces:

1. **Console**: Role-aware management dashboard with context switching between personal and organization modes
2. **Homepage**: Public landing with agent spawn form and featured templates  
3. **AI Employee Directory**: Curated template gallery with hire flow

All views use consistent patterns:
- Session-based state for multi-step flows
- `ConsoleViewMixin` for authentication and context
- HTMX for progressive enhancement
- Analytics tracking on `transaction.on_commit()`
- Role-based permission enforcement for organization features

The agent creation flow demonstrates the integration of these patterns: charter input → authentication → contact configuration → provisioning → template application → async event processing.

**Sources**: [console/views.py:1-2570](), [pages/views.py:1-477](), [agents/services.py:1-265](), [console/templates/](), [pages/templates/]()

---

# Page: Console Interface

# Console Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/models.py](api/models.py)
- [console/views.py](console/views.py)

</details>



The Console Interface provides the primary web-based management dashboard for users and organizations to manage agents, API keys, billing, and tasks. It implements Django class-based views that render server-side templates, supplemented by HTMX for interactive components and WebSocket connections for real-time updates.

For REST API endpoints and programmatic access, see [REST API](#9.1). For the agent chat user interface, see [Agent Chat Interface](#8.3). For the public-facing homepage and template directory, see [Homepage & AI Employee Directory](#8.2).

---

## Architecture Overview

The console is implemented as a collection of Django views in [console/views.py](). These views handle authentication, context resolution (personal vs organization), credit enforcement, and integration with Stripe for billing operations. The views leverage mixins for common behaviors:

- **ConsoleViewMixin**: Provides context resolution and organization switching
- **StripeFeatureRequiredMixin**: Guards billing features behind Stripe availability
- **ApiKeyOwnerMixin**: Resolves API key ownership (user vs organization)
- **PhoneNumberMixin**: Handles phone verification workflows

```mermaid
graph TB
    Browser["Web Browser"]
    
    subgraph "Console Views Layer"
        ConsoleHome["ConsoleHome<br/>(TemplateView)"]
        ApiKeyList["ApiKeyListView<br/>(ListView, FormMixin)"]
        BillingView["BillingView<br/>(TemplateView)"]
        TasksView["tasks_view<br/>(function view)"]
        AgentsView["PersistentAgentsView<br/>(TemplateView)"]
        ProfileView["ProfileView<br/>(TemplateView)"]
    end
    
    subgraph "Console Mixins"
        ConsoleViewMixin["ConsoleViewMixin"]
        StripeFeatureMixin["StripeFeatureRequiredMixin"]
        ApiKeyOwnerMixin["ApiKeyOwnerMixin"]
    end
    
    subgraph "Helper Modules"
        ContextHelpers["build_console_context<br/>(context_helpers.py)"]
        OrgBillingHelpers["build_org_billing_overview<br/>(org_billing_helpers.py)"]
    end
    
    subgraph "Backend Services"
        TaskCreditService["TaskCreditService"]
        AgentService["AgentService"]
        StripeAPI["Stripe API"]
    end
    
    subgraph "Data Models"
        PersistentAgent["PersistentAgent"]
        ApiKey["ApiKey"]
        BrowserUseAgentTask["BrowserUseAgentTask"]
        Organization["Organization"]
        OrganizationMembership["OrganizationMembership"]
    end
    
    Browser --> ConsoleHome
    Browser --> ApiKeyList
    Browser --> BillingView
    Browser --> TasksView
    Browser --> AgentsView
    
    ConsoleHome --> ConsoleViewMixin
    BillingView --> ConsoleViewMixin
    BillingView --> StripeFeatureMixin
    AgentsView --> ConsoleViewMixin
    
    ApiKeyList --> ApiKeyOwnerMixin
    ApiKeyOwnerMixin --> ContextHelpers
    
    ConsoleHome --> ContextHelpers
    ConsoleHome --> TaskCreditService
    
    BillingView --> OrgBillingHelpers
    BillingView --> StripeAPI
    
    TasksView --> BrowserUseAgentTask
    AgentsView --> PersistentAgent
    
    ContextHelpers --> Organization
    ContextHelpers --> OrganizationMembership
```

**Sources:** [console/views.py:1-2800](), [console/mixins.py](), [console/context_helpers.py](), [console/org_billing_helpers.py]()

---

## Console Context Resolution

The console operates in two modes: **personal context** (user-owned resources) or **organization context** (organization-owned resources). The `build_console_context()` function resolves the active context from session data and enforces membership permissions.

```mermaid
graph LR
    Request["HTTP Request<br/>+ Session Data"]
    
    BuildContext["build_console_context()"]
    
    SessionCtx["Session Keys:<br/>context_type<br/>context_id<br/>context_name"]
    
    ResolvedCtx["ResolvedContext:<br/>- current_context<br/>- current_membership<br/>- can_manage_org_agents"]
    
    PersonalCtx["Personal Context<br/>type: personal<br/>id: user.id"]
    
    OrgCtx["Organization Context<br/>type: organization<br/>id: org.id<br/>+ OrganizationMembership"]
    
    Request --> BuildContext
    BuildContext --> SessionCtx
    SessionCtx --> ResolvedCtx
    
    ResolvedCtx --> PersonalCtx
    ResolvedCtx --> OrgCtx
```

The resolved context determines:
- Which agents/tasks are visible
- Which API keys are accessible
- Billing information displayed
- Permission levels for administrative actions

**Sources:** [console/context_helpers.py](), [console/views.py:154-195]()

---

## ConsoleHome Dashboard

The `ConsoleHome` view ([console/views.py:351-577]()) provides the main landing page after login. It aggregates:

| Metric | Personal Context | Organization Context |
|--------|------------------|----------------------|
| **Agent Count** | `BrowserUseAgent.objects.filter(user=user)` | `PersistentAgent.objects.filter(organization_id=org_id)` |
| **Task Stats** | User's `BrowserUseAgentTask` by status | Org's tasks via `organization_id` or agent ownership |
| **Credits Available** | `TaskCreditService.calculate_available_tasks(user)` | Org credits via `TaskCredit.objects.filter(organization=org)` |
| **Subscription** | User's `UserBilling` record | Org's `OrganizationBilling` record |
| **API Keys** | Oldest non-revoked personal key | Hidden (org keys managed separately) |

### Dashboard Metrics Query

```mermaid
graph TB
    ConsoleHomeGet["ConsoleHome.get_context_data()"]
    
    subgraph "Personal Context Queries"
        AgentCount["BrowserUseAgent.objects<br/>.filter(user=request.user)<br/>.count()"]
        TaskStats["BrowserUseAgentTask.objects<br/>.filter(user=request.user)<br/>.values('status')<br/>.annotate(count=Count('status'))"]
        UserCredits["TaskCreditService<br/>.calculate_available_tasks(user)"]
        UserSub["get_active_subscription(user)"]
    end
    
    subgraph "Organization Context Queries"
        OrgAgents["PersistentAgent.objects<br/>.filter(organization_id=org_id)<br/>.count()"]
        OrgTasks["BrowserUseAgentTask.objects<br/>.filter(organization_id=org_id)<br/>.values('status')<br/>.annotate(count=Count('status'))"]
        OrgCredits["TaskCredit.objects<br/>.filter(organization=org)<br/>.aggregate(avail=Sum('available_credits'))"]
    end
    
    ConsoleHomeGet --> AgentCount
    ConsoleHomeGet --> TaskStats
    ConsoleHomeGet --> UserCredits
    ConsoleHomeGet --> UserSub
    
    ConsoleHomeGet --> OrgAgents
    ConsoleHomeGet --> OrgTasks
    ConsoleHomeGet --> OrgCredits
```

**Task Status Breakdown:** The dashboard displays task counts grouped by status:
- `completed`: Successfully finished tasks
- `in_progress`: Currently executing
- `pending`: Queued for execution
- `failed`: Encountered errors
- `cancelled`: User-cancelled tasks

**Sources:** [console/views.py:351-577](), [tasks/services.py:TaskCreditService.calculate_available_tasks]()

---

## API Key Management

API keys are managed through a set of views that support both personal and organization-owned keys. The `ApiKeyOwnerMixin` ([console/views.py:149-182]()) resolves ownership context and enforces role-based permissions.

### API Key Views

| View Class | HTTP Methods | Purpose |
|------------|--------------|---------|
| `ApiKeyListView` | GET, POST | List all keys + create new keys |
| `ApiKeyDetailView` | GET, PATCH, DELETE | Refresh row, revoke key, delete key |
| `ApiKeyTableView` | GET | HTMX partial for table body refresh |
| `ApiKeyBlankFormView` | GET | HTMX partial for blank form |
| `ApiKeyCreateModalView` | GET | HTMX partial for modal dialog |

### Role-Based Permissions

For **organization-owned API keys**, permissions are role-scoped:

```python
API_KEY_MANAGE_ROLES = {
    OrganizationMembership.OrgRole.OWNER,
    OrganizationMembership.OrgRole.ADMIN,
}

API_KEY_VIEW_ROLES = API_KEY_MANAGE_ROLES | {
    OrganizationMembership.OrgRole.BILLING,
}
```

Members with BILLING role can view keys but cannot create/revoke/delete.

### API Key Creation Flow

```mermaid
sequenceDiagram
    participant User
    participant ApiKeyListView
    participant ApiKeyOwnerMixin
    participant ApiKey_Model as ApiKey Model
    participant Analytics
    
    User->>ApiKeyListView: POST /api-keys/ (name="production")
    ApiKeyListView->>ApiKeyOwnerMixin: _ensure_can_manage_api_keys()
    ApiKeyOwnerMixin-->>ApiKeyListView: Permission granted
    
    ApiKeyListView->>ApiKeyListView: form.is_valid()
    
    alt Organization Context
        ApiKeyListView->>ApiKey_Model: ApiKey.create_for_org(org, created_by=user, name)
    else Personal Context
        ApiKeyListView->>ApiKey_Model: ApiKey.create_for_user(user, name, created_by=user)
    end
    
    ApiKey_Model-->>ApiKeyListView: (raw_key, api_key_instance)
    
    ApiKeyListView->>Analytics: track_event(API_KEY_CREATED)
    
    alt HTMX Request
        ApiKeyListView-->>User: Render partials/_api_key_created.html<br/>HX-Trigger: refreshApiKeysTable
    else Traditional Request
        ApiKeyListView-->>User: Redirect to /api-keys/ with success message
    end
```

**Key Validation:** The `ApiKey.clean()` method ([api/models.py:213-257]()) enforces:
- Maximum 50 keys per user
- Maximum 50 keys per organization
- Unique name per owner
- Exactly one owner (user XOR organization)

**Sources:** [console/views.py:583-906](), [api/models.py:122-276]()

---

## Billing & Subscription Management

The `BillingView` ([console/views.py:918-1089]()) provides a unified interface for personal and organization billing, with context-specific rendering.

### Personal Billing

For personal context, displays:
- Subscription plan (Free, Startup, etc.)
- Current billing period (start/end dates)
- Cancellation status (`cancel_at`, `cancel_at_period_end`)
- Extra task limits and usage
- Stripe portal redirect for plan changes

### Organization Billing

For organization context, displays:
- Purchased seats and seat utilization
- Per-seat credit allocation
- Extra task auto-purchase settings
- Pending seat changes (scheduled via Stripe Subscription Schedules)
- Overage SKU management

```mermaid
graph TB
    BillingViewGet["BillingView.get()"]
    
    CheckContext{Context Type?}
    
    PersonalBilling["Personal Billing:<br/>- get_user_plan(user)<br/>- get_active_subscription(user)<br/>- UserBilling.max_extra_tasks"]
    
    OrgBilling["Organization Billing:<br/>- build_org_billing_overview(org)<br/>- OrganizationBilling.purchased_seats<br/>- OrganizationBilling.max_extra_tasks<br/>- Pending seat changes"]
    
    RenderTemplate["Render billing.html"]
    
    BillingViewGet --> CheckContext
    CheckContext -->|type=personal| PersonalBilling
    CheckContext -->|type=organization| OrgBilling
    
    PersonalBilling --> RenderTemplate
    OrgBilling --> RenderTemplate
```

### Organization Seat Management

Organizations must purchase seats to accommodate members beyond the founder. The system enforces:

**Seat Requirement Calculation:**
```python
founder_allowance = 1
active_members = OrganizationMembership.objects.filter(
    org_id=org_id, 
    status=ACTIVE
).count()
pending_invites = OrganizationInvite.objects.filter(
    org_id=org_id,
    accepted_at__isnull=True,
    revoked_at__isnull=True,
    expires_at__gte=now
).count()

seats_required = max(active_members - founder_allowance, 0) + pending_invites
```

**Seat Purchase Flow:**
1. Admin initiates seat purchase via `OrganizationSeatPurchaseForm`
2. If overage SKU exists, it's temporarily detached and stored in session
3. Stripe checkout session created for seat subscription
4. On success redirect, overage SKU is reattached
5. Credits provisioned based on `purchased_seats * credits_per_seat`

**Seat Reduction Flow:**
1. Admin initiates reduction via `OrganizationSeatReductionForm`
2. System validates `new_quantity >= seats_reserved`
3. Stripe Subscription Schedule created for end-of-period reduction
4. `pending_seat_quantity` and `pending_seat_effective_at` recorded
5. Schedule applied automatically at period end

**Sources:** [console/views.py:918-1089](), [console/org_billing_helpers.py](), [api/models.py:1398-1545]()

---

## Task Management Views

The console provides views for browsing and managing browser automation tasks.

### tasks_view

Function-based view ([console/views.py:1297-1371]()) that lists tasks with:
- Context-aware filtering (personal vs organization)
- Status filtering via `?status=pending`
- Text search via `?search=keyword`
- Pagination (10 tasks per page)

**Query Construction:**

```python
# Organization context
tasks_queryset = BrowserUseAgentTask.objects.filter(
    models.Q(organization_id=context_id) |
    models.Q(agent__persistent_agent__organization_id=context_id),
    is_deleted=False,
).distinct().order_by('-created_at')

# Personal context
tasks_queryset = BrowserUseAgentTask.objects.filter(
    user=request.user,
    is_deleted=False,
    organization__isnull=True,
).exclude(
    agent__persistent_agent__organization__isnull=False
).order_by('-created_at')
```

### task_detail_view

Displays a single task ([console/views.py:1374-1386]()) with related steps via `prefetch_related('steps')`.

### task_result_view

Handles result viewing and downloading ([console/views.py:1427-1493]()):
- HTML rendering of task results
- JSON download via `?format=json`
- Analytics tracking for downloads

**Sources:** [console/views.py:1297-1493]()

---

## Agent Management Views

### PersistentAgentsView

The `PersistentAgentsView` ([console/views.py:1496-1620]()) lists all persistent agents for the current context with optimizations:

**Prefetch Optimization:**
```python
primary_email_prefetch = models.Prefetch(
    'comms_endpoints',
    queryset=PersistentAgentCommsEndpoint.objects.filter(
        channel=CommsChannel.EMAIL, 
        is_primary=True
    ),
    to_attr='primary_email_endpoints'
)

persistent_agents = PersistentAgent.objects.filter(
    organization_id=current_context.get('id')
).select_related('browser_use_agent').prefetch_related(
    primary_email_prefetch
).order_by('-created_at')
```

This prevents N+1 queries when displaying agent contact information.

### Agent Lifecycle Actions

The console provides HTMX-powered actions for agent management:

| View Function | Action | HTTP Method |
|---------------|--------|-------------|
| `agent_toggle_active` | Pause/resume agent | PATCH |
| `agent_delete` | Soft-delete agent | DELETE |
| `agent_restore` | Restore deleted agent | POST |
| `agent_expire` | Mark agent as expired | POST |
| `agent_wake` | Wake expired agent | POST |

**Agent Expiration:** The platform implements soft-expiration ([console/views.py:1775-1866]()):
- Agents inactive >30 days transition to `life_state=EXPIRED`
- Schedule is cleared; `is_active` remains True
- User receives email notification
- Waking restores previous schedule from `schedule_snapshot`

**Sources:** [console/views.py:1496-1866](), [api/models.py:2067-2261]()

---

## HTMX Integration

Many console views support HTMX for interactive updates without full page refreshes. HTMX requests are detected via `request.htmx`.

### HTMX Response Patterns

**Pattern 1: Partial Swap**
```python
if request.htmx:
    response = render(request, "partials/_api_key_row.html", context)
    response["HX-Retarget"] = "#api-key-row-123"
    response["HX-Reswap"] = "outerHTML"
    return response
```

**Pattern 2: Trigger Events**
```python
response = render(request, "partials/_api_key_created.html", context)
response["HX-Trigger"] = json.dumps({
    "refreshApiKeysTable": None,
    "close-modal": {"id": "create-api-key-modal"},
})
return response
```

**Pattern 3: Form Validation**
```python
if form.is_valid():
    # Process form
    return redirect(success_url)
else:
    if request.htmx:
        response = render(request, "partials/_form.html", {"form": form})
        response["HX-Retarget"] = "#form-container"
        return response
```

**Sources:** [console/views.py:626-745]() (API key creation), [console/views.py:810-822]() (API key revocation)

---

## Analytics Integration

The console tracks user actions via the `Analytics` service. Events are tracked using `transaction.on_commit()` to ensure they fire only after successful database writes.

### Organization Event Tracking

Helper functions wrap organization context into analytics properties:

```python
def _org_event_properties(request, properties: dict | None = None, *, organization=None) -> dict:
    """Attach organization metadata to analytics properties."""
    org = organization or _resolve_org_from_request(request)
    return Analytics.with_org_properties(properties, organization=org)

def _track_org_event_for_console(request, event: AnalyticsEvent, extra_props: dict | None = None, *, organization=None) -> dict:
    """Track event with organization context."""
    props = _org_event_properties(request, extra_props or {}, organization=organization)
    transaction.on_commit(lambda: Analytics.track_event(
        user_id=request.user.id,
        event=event,
        source=AnalyticsSource.WEB,
        properties=props.copy(),
    ))
    return props
```

### Tracked Events

| Event | Triggered By | Properties |
|-------|--------------|------------|
| `API_KEY_CREATED` | API key creation | `key_id`, `key_name`, `organization_id` |
| `API_KEY_REVOKED` | API key revocation | `key_id`, `key_name` |
| `API_KEY_DELETED` | API key deletion | `key_id`, `key_name` |
| `BILLING_UPDATED` | Extra task settings change | `max_extra_tasks`, `auto_purchase`, `infinite` |
| `BILLING_CANCELLATION` | Subscription cancellation | None |
| `WEB_TASK_CANCELLED` | Task cancellation | `task_id`, `task_status` |
| `WEB_TASK_RESULT_DOWNLOADED` | Result download | `task_id`, `result_step_id` |
| `ORGANIZATION_BILLING_VIEWED` | Org billing page view | `has_stripe_subscription`, `organization_id` |

**Sources:** [console/views.py:197-221]() (helper functions), [console/views.py:712-724]() (API key events), [console/views.py:1475-1480]() (result download)

---

## Billing Update Endpoints

### update_billing_settings

JSON endpoint ([console/views.py:1132-1215]()) for toggling extra task auto-purchase:

**Request Body:**
```json
{
  "enabled": true,
  "infinite": false,
  "maxTasks": 100
}
```

**Behavior:**
- `enabled=false`: Sets `max_extra_tasks=0`
- `enabled=true, infinite=true`: Sets `max_extra_tasks=-1`
- `enabled=true, infinite=false`: Sets `max_extra_tasks=maxTasks`

**Persistence:**
- Personal: `UserBilling.max_extra_tasks`
- Organization: `OrganizationBilling.max_extra_tasks`

### get_billing_settings

JSON endpoint ([console/views.py:1218-1257]()) returns current settings:

```json
{
  "max_extra_tasks": 100,
  "owner_type": "organization",
  "can_modify": true
}
```

**Sources:** [console/views.py:1132-1257]()

---

## Profile Management

The `ProfileView` ([console/views.py:1092-1127]()) allows users to update basic profile information and manage phone numbers. It delegates phone number operations to `PhoneNumberMixin`:

```mermaid
graph LR
    ProfileView_POST["ProfileView.post()"]
    
    PhoneMixin["PhoneNumberMixin<br/>._handle_phone_post()"]
    
    PhoneActions["Phone Actions:<br/>- add_phone<br/>- verify_phone<br/>- delete_phone"]
    
    ProfileForm["UserProfileForm"]
    
    ProfileView_POST --> PhoneMixin
    PhoneMixin --> PhoneActions
    
    PhoneMixin -->|No phone action| ProfileView_POST
    ProfileView_POST --> ProfileForm
```

**Phone Verification Flow:**
1. User submits `PhoneAddForm` with E.164 phone number
2. Twilio verification request sent
3. User receives SMS with code
4. User submits `PhoneVerifyForm` with code
5. On success, `UserPhoneNumber.is_verified=True`

**Sources:** [console/views.py:1092-1127](), [pages/mixins.py:PhoneNumberMixin]()

---

## Context Switching Flow

Users can switch between personal and organization contexts via session updates:

```mermaid
sequenceDiagram
    participant User
    participant BillingView
    participant Session
    participant Database
    
    User->>BillingView: GET /billing/?org_id=<uuid>
    BillingView->>Database: OrganizationMembership.objects.get(<br/>user=user, org_id=org_id, status=ACTIVE)
    
    alt Membership exists
        Database-->>BillingView: membership
        BillingView->>Session: session['context_type'] = 'organization'
        BillingView->>Session: session['context_id'] = str(org.id)
        BillingView->>Session: session['context_name'] = org.name
        BillingView->>Session: session.modified = True
        BillingView-->>User: Render organization billing
    else No membership
        Database-->>BillingView: DoesNotExist
        BillingView-->>User: Error: "You don't have access to that organization."
    end
```

**Session Keys:**
- `context_type`: "personal" or "organization"
- `context_id`: User ID or Organization UUID (as string)
- `context_name`: Display name for UI breadcrumbs

**Sources:** [console/views.py:982-1006]()

---

## Security & Permission Enforcement

### Organization Role Hierarchy

Different features require different role levels:

```python
BILLING_MANAGE_ROLES = {
    OrganizationMembership.OrgRole.OWNER,
    OrganizationMembership.OrgRole.ADMIN,
    OrganizationMembership.OrgRole.BILLING,
}

MEMBER_MANAGE_ROLES = {
    OrganizationMembership.OrgRole.OWNER,
    OrganizationMembership.OrgRole.ADMIN,
}

API_KEY_MANAGE_ROLES = {
    OrganizationMembership.OrgRole.OWNER,
    OrganizationMembership.OrgRole.ADMIN,
}
```

### Permission Denial Patterns

Views raise `PermissionDenied` when authorization fails:

```python
def _ensure_can_manage_api_keys(self):
    ctx = self.api_key_context
    if not ctx.get("can_manage"):
        raise PermissionDenied(
            "You do not have permission to manage API keys for this organization."
        )
    return ctx
```

**Sources:** [console/views.py:128-147]() (role definitions), [console/views.py:177-181]() (permission enforcement)

---

## Stripe Integration Points

The console integrates directly with Stripe for seat management and overage SKU handling:

### Overage SKU Detachment

When purchasing additional seats, the overage SKU must be temporarily removed to avoid subscription item conflicts:

```python
def _detach_org_overage_item(subscription: dict, overage_price_id: str | None, org_id: str, request) -> bool:
    """Remove overage SKU from subscription and store detach state in session."""
    # Find overage item
    items = subscription.get("items", {}).get("data", [])
    overage_item = next((i for i in items if i.get("price", {}).get("id") == overage_price_id), None)
    
    if overage_item:
        stripe.SubscriptionItem.delete(overage_item.get("id"))
        # Mark detach state in subscription metadata
        stripe.Subscription.modify(subscription.get("id"), metadata={
            ORG_OVERAGE_STATE_META_KEY: ORG_OVERAGE_STATE_DETACHED_PENDING
        })
        # Store for reattachment
        _set_overage_detach_session(request, org_id, subscription.get("id"), overage_price_id)
        return True
```

### Overage SKU Reattachment

After seat purchase completes, the overage SKU is restored:

```python
def _reattach_org_overage_subscription(subscription_id: str | None, price_id: str | None) -> bool:
    """Reattach overage SKU if missing and clear detach flag."""
    subscription = stripe.Subscription.retrieve(subscription_id, expand=["items.data.price"])
    items = subscription.get("items", {}).get("data", [])
    has_overage = any(item.get("price", {}).get("id") == price_id for item in items)
    
    if not has_overage:
        stripe.SubscriptionItem.create(subscription=subscription_id, price=price_id)
    
    stripe.Subscription.modify(subscription_id, metadata={ORG_OVERAGE_STATE_META_KEY: ""})
```

**Sources:** [console/views.py:252-350]()

---

# Page: Homepage & AI Employee Directory

# Homepage & AI Employee Directory

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agents/services.py](agents/services.py)
- [console/templates/partials/_agent_contact_form.html](console/templates/partials/_agent_contact_form.html)
- [pages/templates/ai_directory/detail.html](pages/templates/ai_directory/detail.html)
- [pages/templates/ai_directory/index.html](pages/templates/ai_directory/index.html)
- [pages/templates/home.html](pages/templates/home.html)
- [pages/views.py](pages/views.py)
- [tests/unit/test_agent_limits.py](tests/unit/test_agent_limits.py)
- [tests/unit/test_ai_employee_directory.py](tests/unit/test_ai_employee_directory.py)
- [tests/unit/test_console_context.py](tests/unit/test_console_context.py)

</details>



This document describes the homepage interface and AI employee directory system that serve as the primary onboarding entry points for agent creation. For information about the actual agent provisioning logic after charter submission, see [Creating Agents](#4.1). For the contact form that follows charter selection, see the agent creation flow in the console UI.

## Purpose and Scope

The homepage and AI employee directory provide two distinct paths for users to create persistent agents:

1. **Custom Charter Path**: Users write a freeform charter describing their agent's mission
2. **Template Path**: Users select from curated "AI employee" templates with pre-configured charters, schedules, and tools

Both paths store the selected charter in the session and redirect to the contact form ([console/templates/partials/_agent_contact_form.html:1-500]()), where users configure communication endpoints before the agent is provisioned via `PersistentAgentProvisioningService`.

---

## Homepage Structure

### Main Components

The homepage ([pages/templates/home.html:1-656]()) consists of four primary sections:

| Section | Purpose | Visibility |
|---------|---------|------------|
| Hero & Charter Input | Freeform agent charter submission with "Spawn" button | Always visible |
| Task Usage Warning | Displays credit consumption and warnings | Authenticated users only |
| Recent Agents | Shows up to 3 recently updated agents with quick access links | Authenticated users with agents |
| Featured Templates | Displays up to 3 `show_on_homepage=True` templates | Always visible |

**Homepage View Flow**

```mermaid
graph TB
    Request["HTTP GET /"]
    HomePage["HomePage.get_context_data()"]
    
    CheckAuth{"user.is_authenticated?"}
    
    LoadForm["Load PersistentAgentCharterForm"]
    CheckSession{"Session has<br/>agent_charter?"}
    CheckLanding{"URL param 'g'<br/>(landing code)?"}
    CheckDC{"URL param 'dc'<br/>(default charter)?"}
    
    LoadLanding["LandingPage.objects.get(code=...)"]
    PreFillCharter["Pre-fill charter<br/>from session/landing/dc"]
    
    BuildConsoleCtx["build_console_context(request)"]
    LoadOrgs["OrganizationMembership.objects.filter(user=...)"]
    
    LoadTemplates["AIEmployeeTemplateService<br/>.get_active_templates()<br/>.filter(show_on_homepage=True)"]
    AddScheduleDesc["For each template:<br/>describe_schedule(base_schedule)"]
    AddToolDisplay["get_tool_display_map(default_tools)"]
    
    LoadRecentAgents["PersistentAgent.objects<br/>.filter(user_id=...)<br/>.order_by('-updated_at')[:3]"]
    BuildAgentCards["For each agent:<br/>- display_schedule<br/>- listing_description<br/>- status_label/class"]
    
    RenderTemplate["Render home.html<br/>with context"]
    
    Request --> HomePage
    HomePage --> CheckAuth
    
    CheckAuth -->|No| LoadForm
    CheckAuth -->|Yes| BuildConsoleCtx
    
    BuildConsoleCtx --> LoadOrgs
    LoadOrgs --> LoadForm
    
    LoadForm --> CheckSession
    CheckSession -->|Yes| PreFillCharter
    CheckSession -->|No| CheckLanding
    CheckLanding -->|Yes| LoadLanding
    CheckLanding -->|No| CheckDC
    CheckDC -->|Yes| PreFillCharter
    CheckDC -->|No| PreFillCharter
    LoadLanding --> PreFillCharter
    
    PreFillCharter --> LoadTemplates
    LoadTemplates --> AddScheduleDesc
    AddScheduleDesc --> AddToolDisplay
    
    AddToolDisplay --> CheckAuth
    CheckAuth -->|Yes| LoadRecentAgents
    CheckAuth -->|No| RenderTemplate
    
    LoadRecentAgents --> BuildAgentCards
    BuildAgentCards --> RenderTemplate
```

**Sources:** [pages/views.py:50-196](), [pages/templates/home.html:76-290]()

### Charter Input Form

The charter input is a textarea with auto-resize functionality and a gradient "Spawn" button. The form supports pre-filling from multiple sources:

1. **Session Storage**: `request.session['agent_charter']` from previous submission ([pages/views.py:101-105]())
2. **Landing Pages**: URL parameter `g={code}` loads charter from `LandingPage` model ([pages/views.py:72-95]())
3. **Direct Charter**: URL parameter `dc={text}` directly sets charter ([pages/views.py:69-71]())
4. **Template Selection**: Set when user "hires" a template (covered below)

The form submission is handled by `HomeAgentSpawnView`:

```mermaid
graph TB
    Submit["POST /agents/spawn/"]
    ValidateForm["PersistentAgentCharterForm.is_valid()"]
    
    StoreSession["session['agent_charter'] = charter<br/>session['agent_charter_source'] = 'user'"]
    
    CheckAuth{"user.is_authenticated?"}
    
    TrackAnalytics["Analytics.track_event()<br/>PERSISTENT_AGENT_CHARTER_SUBMIT"]
    
    RedirectContact["redirect('agent_create_contact')"]
    RedirectLogin["redirect_to_login()<br/>next=agent_create_contact"]
    
    Submit --> ValidateForm
    ValidateForm -->|Valid| StoreSession
    ValidateForm -->|Invalid| ReRender["Re-render home.html<br/>with form errors"]
    
    StoreSession --> CheckAuth
    CheckAuth -->|Yes| TrackAnalytics
    CheckAuth -->|No| RedirectLogin
    TrackAnalytics --> RedirectContact
```

**Sources:** [pages/views.py:198-244](), [pages/templates/home.html:107-159]()

### Recent Agents Section

For authenticated users with existing agents, the homepage displays up to 3 recent agents ([pages/views.py:159-193]()):

```python
recent_agents_qs = PersistentAgent.objects.filter(user_id=self.request.user.id)
total_agents = recent_agents_qs.count()
recent_agents = list(recent_agents_qs.order_by('-updated_at')[:3])
```

Each agent card includes:
- Agent name
- Status badge (Active/Expired) derived from `life_state` field
- Display schedule via `AIEmployeeTemplateService.describe_schedule()`
- Listing description via `build_listing_description()` (max 140 chars)
- Link to agent detail page

**Sources:** [pages/views.py:159-193](), [pages/templates/home.html:162-210]()

### Game of Life Animation

The charter input card features a Conway's Game of Life animation rendered on a `<canvas>` element ([pages/templates/home.html:349-588]()). The implementation:

- Uses `ResizeObserver` to adapt grid size to container
- Pauses animation when not visible via `IntersectionObserver`
- Applies radial gradient masking for visual effect
- Sprinkles new cells on low population or every 200 ticks
- Supports pointer interaction to seed new cells

**Sources:** [pages/templates/home.html:7-74](), [pages/templates/home.html:349-588]()

---

## AI Employee Directory

The AI employee directory provides a browsable catalog of curated agent templates stored in the `PersistentAgentTemplate` model.

### Directory Index

**Template Listing View**

```mermaid
graph TB
    Request["GET /ai-employees/"]
    
    DirectoryView["AIEmployeeDirectoryView<br/>.get_context_data()"]
    
    GetTemplates["AIEmployeeTemplateService<br/>.get_active_templates()"]
    
    ApplyCategory{"URL param<br/>'category'?"}
    ApplySearch{"URL param<br/>'q'?"}
    
    FilterCategory["templates_queryset<br/>.filter(category__iexact=...)"]
    FilterSearch["templates_queryset<br/>.filter(<br/>Q(display_name__icontains=...)<br/>| Q(tagline__icontains=...)<br/>| Q(description__icontains=...))"]
    
    CollectTools["Collect all template.default_tools<br/>into tool_names set"]
    
    GetToolMap["AIEmployeeTemplateService<br/>.get_tool_display_map(tool_names)"]
    
    EnrichTemplates["For each template:<br/>- describe_schedule(base_schedule)<br/>- get_tool_display_list(default_tools)"]
    
    LoadCategories["Get distinct categories<br/>from active templates"]
    
    RenderIndex["Render ai_directory/index.html"]
    
    Request --> DirectoryView
    DirectoryView --> GetTemplates
    
    GetTemplates --> ApplyCategory
    ApplyCategory -->|Yes| FilterCategory
    ApplyCategory -->|No| ApplySearch
    FilterCategory --> ApplySearch
    
    ApplySearch -->|Yes| FilterSearch
    ApplySearch -->|No| CollectTools
    FilterSearch --> CollectTools
    
    CollectTools --> GetToolMap
    GetToolMap --> EnrichTemplates
    EnrichTemplates --> LoadCategories
    LoadCategories --> RenderIndex
```

**Sources:** [pages/views.py:247-299](), [pages/templates/ai_directory/index.html:1-120]()

### Template Cards

Each template card displays ([pages/templates/ai_directory/index.html:42-109]()):

| Field | Source | Example |
|-------|--------|---------|
| Category badge | `template.category` | "Sales", "HR", "Finance" |
| Display name | `template.display_name` | "Daily Sales Intelligence Agent" |
| Tagline | `template.tagline` | "Monitors pipeline, sends daily summaries" |
| Schedule | `describe_schedule(base_schedule)` | "Every day at 9:00 AM" |
| Event triggers | `template.event_triggers` (JSON array) | "New lead", "Deal closed" |
| Tools | First 3 from `display_default_tools` | "Google Sheets", "Slack", "+2 more" |

### Template Detail Page

The detail view ([pages/views.py:302-327]()) provides full template information:

```mermaid
graph TB
    Request["GET /ai-employees/{slug}/"]
    
    Dispatch["AIEmployeeDetailView.dispatch()"]
    GetTemplate["AIEmployeeTemplateService<br/>.get_template_by_code(slug)"]
    
    Check404{"Template<br/>found?"}
    
    BuildContext["get_context_data():"]
    DescribeSchedule["describe_schedule(base_schedule)"]
    GetToolMap["get_tool_display_map(default_tools)"]
    GetToolList["get_tool_display_list(default_tools)"]
    DescribeContact["describe_contact_channel(<br/>recommended_contact_channel)"]
    
    RenderDetail["Render ai_directory/detail.html<br/>- Full charter text<br/>- Event triggers list<br/>- Built-in integrations<br/>- 'Hire now' button"]
    
    Request --> Dispatch
    Dispatch --> GetTemplate
    GetTemplate --> Check404
    
    Check404 -->|No| Raise404["raise Http404"]
    Check404 -->|Yes| BuildContext
    
    BuildContext --> DescribeSchedule
    DescribeSchedule --> GetToolMap
    GetToolMap --> GetToolList
    GetToolList --> DescribeContact
    DescribeContact --> RenderDetail
```

**Sources:** [pages/views.py:302-327](), [pages/templates/ai_directory/detail.html:1-97]()

---

## Template System Architecture

### AIEmployeeTemplateService

The `AIEmployeeTemplateService` ([agents/services.py:119-265]()) provides utilities for working with `PersistentAgentTemplate` records:

**Core Methods**

```mermaid
graph TB
    subgraph "Template Discovery"
        GetActive["get_active_templates()"]
        GetByCode["get_template_by_code(code)"]
        
        GetActive --> QueryActive["Template.objects<br/>.filter(is_active=True)<br/>.order_by('priority', 'display_name')"]
        GetByCode --> QueryCode["Template.objects<br/>.get(code=code, is_active=True)"]
    end
    
    subgraph "Schedule Processing"
        ComputeJitter["compute_schedule_with_jitter(<br/>base_schedule, jitter_minutes)"]
        DescribeSchedule["describe_schedule(base_schedule)"]
        
        ComputeJitter --> ParseCron["Parse cron expression<br/>Apply random offset ±jitter"]
        DescribeSchedule --> NormalizeCron["_normalize_cron_expression()"]
        NormalizeCron --> CronDescriptor["cron_descriptor<br/>.get_description()"]
    end
    
    subgraph "Tool Display"
        GetToolMap["get_tool_display_map(tool_names)"]
        GetToolList["get_tool_display_list(<br/>tool_names, display_map)"]
        
        GetToolMap --> QueryToolNames["ToolFriendlyName.objects<br/>.filter(tool_name__in=...)"]
        GetToolList --> MapNames["Map each tool_name<br/>to display_name<br/>or _fallback_tool_display()"]
    end
    
    subgraph "Contact Channel"
        DescribeChannel["describe_contact_channel(channel)"]
        DescribeChannel --> Mapping["Map 'email' → 'Email updates'<br/>'sms' → 'Text message (SMS)'<br/>'slack' → 'Slack message'"]
    end
```

**Sources:** [agents/services.py:119-265]()

### Schedule Jitter

Templates support schedule jitter to distribute execution times ([agents/services.py:149-180]()):

```python
def compute_schedule_with_jitter(base_schedule: str | None, jitter_minutes: int | None) -> str | None:
    # Parse "30 9 * * *" (9:30 AM daily)
    # Apply jitter: random offset ±jitter_minutes
    # Return "37 9 * * *" (9:37 AM daily)
    
    total_minutes = hour_val * 60 + minute_val
    offset = random.randint(-jitter, jitter)
    total_minutes = (total_minutes + offset) % (24 * 60)
```

This prevents thundering herd when many templates use the same base schedule.

**Sources:** [agents/services.py:149-180](), [tests/unit/test_ai_employee_directory.py:8-19]()

### Cron Description

The service converts cron expressions to human-readable text using the `cron_descriptor` library:

| Input | Output |
|-------|--------|
| `"0 9 * * *"` | "Every day at 9:00 AM" |
| `"0 9 * * MON-FRI"` | "At 9:00 AM, Monday through Friday" |
| `"@daily"` | "Every day at 12:00 AM" |
| `"@hourly"` | "Every hour" |

Macros like `@daily` are normalized using `_CRON_MACRO_MAP` ([agents/services.py:123-131]()) before being passed to `cron_descriptor`.

**Sources:** [agents/services.py:182-214]()

---

## Agent Creation Flow

### Template Hire Flow

When a user clicks "Hire" on a template, the following sequence occurs:

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AIEmployeeHireView
    participant Session
    participant Analytics
    participant LoginView
    participant ContactForm
    
    User->>Browser: Click "Hire" button
    Browser->>AIEmployeeHireView: POST /ai-employees/{slug}/hire/
    
    AIEmployeeHireView->>AIEmployeeHireView: get_template_by_code(slug)
    
    alt Template not found
        AIEmployeeHireView-->>Browser: HTTP 404
    end
    
    AIEmployeeHireView->>Session: session['agent_charter'] = template.charter
    AIEmployeeHireView->>Session: session['ai_employee_template_code'] = template.code
    AIEmployeeHireView->>Session: session['agent_charter_source'] = 'template'
    
    alt User authenticated
        AIEmployeeHireView->>Analytics: track_event(PERSISTENT_AGENT_CHARTER_SUBMIT)
        AIEmployeeHireView-->>Browser: redirect('agent_create_contact')
        Browser->>ContactForm: GET /agents/create/contact/
    else User anonymous
        AIEmployeeHireView->>Analytics: track_event_anonymous()
        AIEmployeeHireView-->>Browser: redirect_to_login(next='agent_create_contact')
        Browser->>LoginView: GET /login/?next=/agents/create/contact/
    end
```

**Sources:** [pages/views.py:329-373]()

### Session State Management

Both homepage spawn and template hire flows use session storage to preserve state:

| Session Key | Set By | Used By | Purpose |
|-------------|--------|---------|---------|
| `agent_charter` | `HomeAgentSpawnView`, `AIEmployeeHireView` | `AgentCreateContactView` | Stores the agent's charter text |
| `agent_charter_source` | `HomeAgentSpawnView` (`'user'`), `AIEmployeeHireView` (`'template'`) | Homepage (display logic) | Distinguishes user-written vs template charters |
| `ai_employee_template_code` | `AIEmployeeHireView` | `PersistentAgentProvisioningService` | Template code for applying defaults (schedule, tools, etc.) |

The contact form ([console/templates/partials/_agent_contact_form.html:1-500]()) retrieves these values and displays template information if `ai_employee_template_code` is present:

```mermaid
graph TB
    LoadContact["AgentCreateContactView.get()"]
    
    CheckCharter{"session has<br/>'agent_charter'?"}
    
    CheckTemplate{"session has<br/>'ai_employee_template_code'?"}
    
    LoadTemplate["AIEmployeeTemplateService<br/>.get_template_by_code()"]
    
    EnrichTemplate["- describe_schedule(base_schedule)<br/>- get_tool_display_list(default_tools)<br/>- describe_contact_channel()"]
    
    BuildForm["Build AgentContactForm<br/>with toggle switches for<br/>email/sms"]
    
    RenderForm["Render _agent_contact_form.html<br/>with template info card"]
    
    LoadContact --> CheckCharter
    CheckCharter -->|No| Redirect404["Redirect to homepage<br/>(no charter to create from)"]
    CheckCharter -->|Yes| CheckTemplate
    
    CheckTemplate -->|Yes| LoadTemplate
    CheckTemplate -->|No| BuildForm
    
    LoadTemplate --> EnrichTemplate
    EnrichTemplate --> BuildForm
    BuildForm --> RenderForm
```

**Sources:** [console/templates/partials/_agent_contact_form.html:50-85](), [pages/views.py:336-339]()

### Context Switching

The contact form supports organization context switching ([console/templates/partials/_agent_contact_form.html:23-47]()):

```html
<select id="agent-owner-selector-contact">
  <option value='{"type": "personal", "id": "...", "name": "..."}'>
    Personal – {{ request.user.get_full_name }}
  </option>
  {% for membership in user_organizations %}
    <option value='{"type": "organization", "id": "...", "name": "..."}'>
      Organization – {{ membership.org.name }}
    </option>
  {% endfor %}
</select>
```

On change, JavaScript calls `POST /console/switch-context/` to update session context ([console/templates/partials/_agent_contact_form.html:240-280]()). The provisioning service then creates the agent under the selected owner (user or organization).

**Sources:** [console/templates/partials/_agent_contact_form.html:23-47](), [console/templates/partials/_agent_contact_form.html:240-280](), [tests/unit/test_console_context.py:215-244]()

---

## Search and Filtering

### Directory Filters

The directory supports two filter mechanisms ([pages/views.py:254-265]()):

**Category Filter**
```python
category = self.request.GET.get('category', '').strip()
if category:
    templates_queryset = templates_queryset.filter(category__iexact=category)
```

**Text Search**
```python
search = self.request.GET.get('q', '').strip()
if search:
    templates_queryset = templates_queryset.filter(
        Q(display_name__icontains=search)
        | Q(tagline__icontains=search)
        | Q(description__icontains=search)
    )
```

Categories are dynamically loaded from existing templates ([pages/views.py:282-289]()):

```python
all_categories = (
    AIEmployeeTemplateService.get_active_templates()
    .exclude(category__isnull=True)
    .exclude(category__exact="")
    .values_list('category', flat=True)
    .distinct()
    .order_by('category')
)
```

**Sources:** [pages/views.py:247-299](), [pages/templates/ai_directory/index.html:13-38]()

---

## Analytics Integration

Both flows track analytics events via the `Analytics` service:

**Homepage Spawn**
```python
Analytics.track_event(
    user_id=request.user.id,
    event=AnalyticsEvent.PERSISTENT_AGENT_CHARTER_SUBMIT,
    source=AnalyticsSource.WEB,
    properties={
        'charter': form.cleaned_data['charter'],
        'source_page': 'home',
    }
)
```

**Template Hire (Authenticated)**
```python
Analytics.track_event(
    user_id=request.user.id,
    event=AnalyticsEvent.PERSISTENT_AGENT_CHARTER_SUBMIT,
    source=AnalyticsSource.WEB,
    properties={
        "source_page": "ai_employee_directory",
        "template_code": template.code,
    },
)
```

**Template Hire (Anonymous)**
```python
Analytics.track_event_anonymous(
    anonymous_id=str(session_key),
    event=AnalyticsEvent.PERSISTENT_AGENT_CHARTER_SUBMIT,
    source=AnalyticsSource.WEB,
    properties={
        "source_page": "ai_employee_directory",
        "template_code": template.code,
    },
)
```

**Sources:** [pages/views.py:214-223](), [pages/views.py:342-366]()

---

## Template Model Structure

The `PersistentAgentTemplate` model (referenced but not shown in files) includes:

| Field | Type | Purpose |
|-------|------|---------|
| `code` | String (unique) | URL-safe identifier (e.g., "sales-intelligence") |
| `display_name` | String | Human-readable name |
| `tagline` | String | Short description |
| `description` | Text | Full description of what the template does |
| `charter` | Text | Agent charter/instructions |
| `category` | String | Category for filtering (e.g., "Sales", "HR") |
| `base_schedule` | String | Cron expression for scheduling |
| `schedule_jitter_minutes` | Integer | Randomization range for schedule |
| `default_tools` | JSON Array | List of tool names to enable by default |
| `event_triggers` | JSON Array | List of event trigger configurations |
| `recommended_contact_channel` | String | Suggested communication method |
| `is_active` | Boolean | Whether template appears in directory |
| `show_on_homepage` | Boolean | Whether to feature on homepage |
| `priority` | Integer | Sort order (lower = higher priority) |

**Sources:** [pages/views.py:138-156](), [pages/templates/ai_directory/detail.html:1-97]()

---

## Landing Page Integration

The homepage supports landing pages via the `LandingPage` model ([pages/views.py:72-95]()):

**URL Pattern**: `/?g={landing_code}`

**Loading Logic**:
```python
landing = LandingPage.objects.get(code=self.request.GET['g'], disabled=False)
initial['charter'] = landing.charter.strip()
context['landing_hero_text'] = landing.hero_text  # With {blue} tag support
context['landing_preview_image'] = landing.image_url
```

Landing pages can customize:
- Hero text with gradient highlighting via `{blue}...{/blue}` tags
- Pre-filled charter
- Preview image
- UTM parameters for tracking

The `LandingRedirectView` ([pages/views.py:393-442]()) handles short URLs like `/g/{code}/` and redirects to `/?g={code}` with UTM preservation.

**Sources:** [pages/views.py:72-95](), [pages/views.py:393-442]()

---

## Agent Quota Display

For authenticated users, the homepage shows agent availability ([pages/templates/home.html:211-289]()):

**When No Agents Available**:
```html
<div class="bg-gradient-to-br from-blue-50 to-indigo-50">
  <h3>No Agents Available</h3>
  <p>You've reached your agent limit (0/{{ account.usage.agent_limit }})</p>
  <a href="{% url 'proprietary:startup_checkout' %}">Upgrade Your Plan</a>
</div>
```

This display uses the `account.usage.agents_available` property calculated by `AgentService.get_agents_available()` ([agents/services.py:45-97]()).

**Sources:** [pages/templates/home.html:211-289](), [agents/services.py:45-97](), [tests/unit/test_agent_limits.py:1-284]()

---

# Page: Agent Chat Interface

# Agent Chat Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/components/agentChat/AgentChatLayout.tsx](frontend/src/components/agentChat/AgentChatLayout.tsx)
- [frontend/src/screens/AgentChatPage.tsx](frontend/src/screens/AgentChatPage.tsx)
- [frontend/src/stores/agentChatStore.ts](frontend/src/stores/agentChatStore.ts)
- [frontend/src/styles/agentChatLegacy.css](frontend/src/styles/agentChatLegacy.css)

</details>



## Purpose and Scope

The Agent Chat Interface provides a real-time, interactive web chat experience for communicating with persistent agents. This interface enables users to send messages to agents, view agent responses and tool executions in a timeline format, and monitor ongoing processing activities. For information about agent event processing and tool execution, see [Agent Event Processing](#4.3). For details about the underlying chat communication system, see [Agent Web Chat](#7.1).

**Sources:**
- [frontend/src/screens/AgentChatPage.tsx:1-204]()
- [frontend/src/components/agentChat/AgentChatLayout.tsx:1-148]()

---

## Architecture Overview

The chat interface follows a layered architecture with clear separation between presentation, state management, and data synchronization:

```mermaid
graph TB
    subgraph "Page Layer"
        AgentChatPage["AgentChatPage"]
    end
    
    subgraph "State Management"
        agentChatStore["agentChatStore<br/>(Zustand)"]
        autoScrollState["Auto-scroll State"]
        timelineWindow["Timeline Window<br/>(100 events max)"]
    end
    
    subgraph "Layout Layer"
        AgentChatLayout["AgentChatLayout"]
        TimelineEventList["TimelineEventList"]
        AgentComposer["AgentComposer"]
        ProcessingIndicator["ProcessingIndicator"]
        JumpButton["Jump to Latest Button"]
    end
    
    subgraph "Integration Hooks"
        useAgentChatSocket["useAgentChatSocket"]
        useAgentWebSession["useAgentWebSession"]
    end
    
    subgraph "API Layer"
        fetchAgentTimeline["fetchAgentTimeline"]
        sendAgentMessage["sendAgentMessage"]
        fetchProcessingStatus["fetchProcessingStatus"]
    end
    
    subgraph "Real-time"
        WebSocket["WebSocket Connection"]
    end
    
    AgentChatPage --> agentChatStore
    AgentChatPage --> useAgentChatSocket
    AgentChatPage --> useAgentWebSession
    AgentChatPage --> AgentChatLayout
    
    AgentChatLayout --> TimelineEventList
    AgentChatLayout --> AgentComposer
    AgentChatLayout --> ProcessingIndicator
    AgentChatLayout --> JumpButton
    
    agentChatStore --> fetchAgentTimeline
    agentChatStore --> sendAgentMessage
    agentChatStore --> fetchProcessingStatus
    
    useAgentChatSocket --> WebSocket
    WebSocket --> agentChatStore
    
    agentChatStore --> autoScrollState
    agentChatStore --> timelineWindow
```

**Sources:**
- [frontend/src/screens/AgentChatPage.tsx:1-204]()
- [frontend/src/stores/agentChatStore.ts:1-473]()

---

## State Management with agentChatStore

The chat interface uses a Zustand store (`agentChatStore`) to manage all state, including timeline events, pagination, processing status, and auto-scroll behavior.

### Store Structure

| State Property | Type | Purpose |
|----------------|------|---------|
| `agentId` | `string \| null` | Currently active agent identifier |
| `events` | `TimelineEvent[]` | Current timeline window (sorted by cursor) |
| `oldestCursor` | `string \| null` | Cursor of oldest event in window |
| `newestCursor` | `string \| null` | Cursor of newest event in window |
| `hasMoreOlder` | `boolean` | Whether more older events exist |
| `hasMoreNewer` | `boolean` | Whether more newer events exist |
| `hasUnseenActivity` | `boolean` | Whether new events arrived while unpinned |
| `processingActive` | `boolean` | Whether agent is currently processing |
| `processingWebTasks` | `ProcessingWebTask[]` | Active browser automation tasks |
| `autoScrollPinned` | `boolean` | Whether auto-scroll is enabled |
| `autoScrollPinSuppressedUntil` | `number \| null` | Timestamp until which re-pinning is suppressed |
| `pendingEvents` | `TimelineEvent[]` | Events queued while auto-scroll is off |

### Timeline Window Management

The store maintains a sliding window of **100 events** maximum (`TIMELINE_WINDOW_SIZE`). When loading older or newer events, the window automatically trims from the opposite end:

```mermaid
sequenceDiagram
    participant User
    participant Store as agentChatStore
    participant API as fetchAgentTimeline
    
    User->>Store: loadOlder()
    Store->>Store: Check hasMoreOlder & !loadingOlder
    Store->>API: fetch(direction='older', cursor=oldestCursor)
    API-->>Store: { events: [...], has_more_older }
    Store->>Store: mergeEvents(existing, incoming)
    Store->>Store: events.slice(0, 100)
    Store->>Store: Update oldestCursor, hasMoreOlder
    Note over Store: Trim from newer end if > 100
    Store->>Store: Set hasMoreNewer = true (if trimmed)
    
    User->>Store: loadNewer()
    Store->>Store: Check hasMoreNewer & !loadingNewer
    Store->>API: fetch(direction='newer', cursor=newestCursor)
    API-->>Store: { events: [...], has_more_newer }
    Store->>Store: mergeEvents(existing, incoming)
    Store->>Store: events.slice(-100)
    Store->>Store: Update newestCursor, hasMoreNewer
    Note over Store: Trim from older end if > 100
    Store->>Store: Set hasMoreOlder = true (if trimmed)
```

**Sources:**
- [frontend/src/stores/agentChatStore.ts:131-131]()
- [frontend/src/stores/agentChatStore.ts:265-299]()
- [frontend/src/stores/agentChatStore.ts:301-340]()

### Event Normalization and Merging

Events are normalized before insertion to ensure consistent HTML rendering and to handle tool cluster aggregation:

**Event Normalization Flow:**
1. **HTML Sanitization**: `normalizeEvent()` detects HTML content in message bodies and sanitizes it via `sanitizeHtml()` [frontend/src/stores/agentChatStore.ts:34-65]()
2. **Cursor-based Deduplication**: Events are stored in a `Map<cursor, event>` to prevent duplicates [frontend/src/stores/agentChatStore.ts:113-129]()
3. **Tool Cluster Merging**: When a `ToolClusterEvent` arrives with the same cursor as an existing cluster, their entries are merged and re-sorted [frontend/src/stores/agentChatStore.ts:81-111]()

**Tool Cluster Merging Logic:**

```mermaid
graph LR
    A["Existing Cluster<br/>cursor: '123:steps'<br/>entries: [A, B]"] --> M["mergeClusters()"]
    B["Incoming Cluster<br/>cursor: '123:steps'<br/>entries: [B, C]"] --> M
    M --> C["Merged Cluster<br/>cursor: '123:steps'<br/>entries: [A, B, C]<br/>sorted by entry cursor"]
```

This ensures that tool execution steps appearing incrementally via WebSocket are aggregated into a single collapsible cluster rather than fragmented across multiple timeline entries.

**Sources:**
- [frontend/src/stores/agentChatStore.ts:14-69]()
- [frontend/src/stores/agentChatStore.ts:71-79]()
- [frontend/src/stores/agentChatStore.ts:81-111]()
- [frontend/src/stores/agentChatStore.ts:113-129]()

### Cursor Format and Sorting

Timeline events use cursors in the format `{timestamp}:{type}` (e.g., `"1640000000000:message"`). The `parseCursorValue()` function extracts the numeric timestamp prefix for sorting [frontend/src/stores/agentChatStore.ts:71-75]().

**Sources:**
- [frontend/src/stores/agentChatStore.ts:71-79]()

---

## Layout Components

### AgentChatLayout

The `AgentChatLayout` component is the main presentational shell that orchestrates the visual structure of the chat interface.

**Component Props:**

| Prop | Type | Purpose |
|------|------|---------|
| `agentName` | `string` | Full agent name for display |
| `agentFirstName` | `string` | Agent first name (derived from full name) |
| `events` | `TimelineEvent[]` | Events to render in timeline |
| `hasMoreOlder` | `boolean` | Controls "Load older" button visibility |
| `hasMoreNewer` | `boolean` | Controls "Load newer" button visibility |
| `processingActive` | `boolean` | Controls processing indicator visibility |
| `processingWebTasks` | `ProcessingWebTask[]` | Active browser tasks to display |
| `onLoadOlder` | `() => void` | Callback for loading older events |
| `onLoadNewer` | `() => void` | Callback for loading newer events |
| `onJumpToLatest` | `() => void` | Callback for jump-to-latest button |
| `onSendMessage` | `(body: string) => Promise<void>` | Callback for sending messages |
| `autoScrollPinned` | `boolean` | Whether auto-scroll is active |
| `hasUnseenActivity` | `boolean` | Whether to show activity indicator on jump button |

**Layout Structure:**

```mermaid
graph TB
    Main["main.min-h-screen"]
    Workspace["#agent-workspace-root<br/>.relative.flex.flex-1"]
    TimelineShell["#timeline-shell<br/>.relative.flex-1"]
    TimelineEvents["#timeline-events<br/>.flex.flex-col.gap-3"]
    
    LoadOlder["#timeline-load-older<br/>Load Older Button"]
    EventList["#timeline-event-list<br/>TimelineEventList"]
    ProcessingSlot["#processing-indicator-slot<br/>ProcessingIndicator"]
    BottomSentinel["#timeline-bottom-sentinel<br/>Intersection Observer Target"]
    LoadNewer["#timeline-load-newer<br/>Load Newer Button"]
    
    Composer["AgentComposer<br/>.composer-shell (fixed)"]
    JumpButton["#jump-to-latest<br/>.jump-to-latest (fixed)"]
    
    Main --> Workspace
    Workspace --> TimelineShell
    Workspace --> Composer
    Main --> JumpButton
    
    TimelineShell --> TimelineEvents
    TimelineEvents --> LoadOlder
    TimelineEvents --> EventList
    TimelineEvents --> ProcessingSlot
    TimelineEvents --> BottomSentinel
    TimelineEvents --> LoadNewer
```

**Key Element IDs:**
- `#timeline-events`: Main scrollable timeline container with dynamic padding based on `data-has-jump-button` attribute [frontend/src/styles/agentChatLegacy.css:15-22]()
- `#timeline-bottom-sentinel`: 1px-height element used by IntersectionObserver to detect scroll position [frontend/src/components/agentChat/AgentChatLayout.tsx:101-103]()
- `#jump-to-latest`: Fixed-position button that appears when `hasMoreNewer || hasUnseenActivity || !autoScrollPinned` [frontend/src/components/agentChat/AgentChatLayout.tsx:52-143]()

**Sources:**
- [frontend/src/components/agentChat/AgentChatLayout.tsx:27-147]()
- [frontend/src/styles/agentChatLegacy.css:1-26]()
- [frontend/src/styles/agentChatLegacy.css:373-424]()

### AgentComposer

The message input component, rendered in a fixed position at the bottom of the viewport with `.composer-shell` styling [frontend/src/styles/agentChatLegacy.css:309-328](). The composer:
- Floats above the timeline via `z-index: 40`
- Has a CSS custom property `--composer-height: 6.5rem` used for timeline padding calculations
- Triggers `onSubmit` callback with trimmed message text

**Sources:**
- [frontend/src/components/agentChat/AgentChatLayout.tsx:126-126]()
- [frontend/src/styles/agentChatLegacy.css:11-13]()
- [frontend/src/styles/agentChatLegacy.css:309-363]()

### ProcessingIndicator

Displays when `processingActive` is true and there are no newer events to load. The indicator:
- Shows a pulsing pip with the agent's first name
- Expands to show individual browser tasks when multiple tasks are active
- Each task card shows status, duration, and prompt preview
- Supports click-to-expand for viewing full task details

The indicator is wrapped in `#processing-indicator-slot` with `data-visible` attribute controlling display via CSS [frontend/src/styles/agentChatLegacy.css:37-49]().

**Processing Web Tasks Display:**

```mermaid
graph TB
    Indicator["#agent-processing-indicator"]
    Label["processing-label (clickable)"]
    Content["processing-content"]
    TaskList["processing-task-list"]
    
    Task1["Task Card 1<br/>status badge + duration<br/>prompt preview<br/>task ID"]
    Task2["Task Card 2<br/>..."]
    
    Indicator --> Label
    Indicator --> Content
    Content --> TaskList
    TaskList --> Task1
    TaskList --> Task2
    
    style Task1 text-align:left
    style Task2 text-align:left
```

**Sources:**
- [frontend/src/components/agentChat/AgentChatLayout.tsx:93-99]()
- [frontend/src/styles/agentChatLegacy.css:37-307]()

---

## Auto-Scroll System

The auto-scroll system manages whether the timeline automatically scrolls to show new events or allows the user to browse history without interruption.

### Pinned vs Unpinned States

| State | Behavior |
|-------|----------|
| **Pinned** | New events immediately appear; timeline scrolls to bottom; jump button hidden |
| **Unpinned** | New events go to `pendingEvents` queue; jump button shows with activity indicator; user controls scroll position |

### IntersectionObserver Integration

The `AgentChatPage` uses an IntersectionObserver to detect when the bottom sentinel element becomes visible:

```mermaid
sequenceDiagram
    participant User
    participant Sentinel as bottomSentinelRef
    participant Observer as IntersectionObserver
    participant Store as agentChatStore
    
    Note over Sentinel: Element at bottom of timeline
    
    Observer->>Sentinel: observe(sentinel)
    
    User->>User: Scrolls near bottom
    Sentinel->>Observer: isIntersecting = true
    Observer->>Store: setAutoScrollPinned(true)
    
    User->>User: Scrolls up
    Sentinel->>Observer: isIntersecting = false
    Observer->>Store: setAutoScrollPinned(false)
```

The observer is configured with `threshold: 0.75`, meaning the sentinel must be 75% visible before triggering [frontend/src/screens/AgentChatPage.tsx:134-154]().

**Sources:**
- [frontend/src/screens/AgentChatPage.tsx:133-154]()

### Scroll Position Tracking

In addition to IntersectionObserver, the page also monitors scroll distance from bottom:

**Scroll Event Handler Logic:**
1. Calculate `distanceToBottom = scrollHeight - clientHeight - scrollTop`
2. If `distanceToBottom <= 12px` and currently unpinned and no suppression active → pin
3. If `distanceToBottom > 160px` and currently pinned → unpin

The dual system (IntersectionObserver + scroll distance) ensures reliable auto-scroll toggling across different viewport sizes and scrolling behaviors [frontend/src/screens/AgentChatPage.tsx:69-117]().

**Sources:**
- [frontend/src/screens/AgentChatPage.tsx:69-117]()

### Auto-Scroll Suppression

The store provides `suppressAutoScrollPin(durationMs)` to prevent immediate re-pinning after certain actions. This is used to avoid jarring behavior when the user intentionally scrolls or when layout shifts occur [frontend/src/stores/agentChatStore.ts:462-471]().

When `autoScrollPinSuppressedUntil` is set to a future timestamp, the scroll handler skips re-pinning even if scroll position meets the criteria [frontend/src/screens/AgentChatPage.tsx:89-96]().

**Sources:**
- [frontend/src/stores/agentChatStore.ts:462-471]()
- [frontend/src/screens/AgentChatPage.tsx:89-96]()

### Pending Events Queue

When unpinned, incoming real-time events are added to `pendingEvents` rather than the main `events` array:

```mermaid
graph TB
    WS["WebSocket receives event"]
    Check{autoScrollPinned?}
    Merge1["mergeEvents(events, [event])<br/>Update events immediately"]
    Merge2["mergeEvents(pendingEvents, [event])<br/>Update pendingEvents only"]
    Activity["Set hasUnseenActivity = true"]
    
    WS --> Check
    Check -->|true| Merge1
    Check -->|false| Merge2
    Merge2 --> Activity
    
    style Activity fill:#fff4e1
```

When the user re-pins (via jump button or scrolling to bottom), pending events are merged into the main timeline [frontend/src/stores/agentChatStore.ts:438-461]().

**Sources:**
- [frontend/src/stores/agentChatStore.ts:396-427]()
- [frontend/src/stores/agentChatStore.ts:438-461]()

---

## Timeline Event Processing

### Event Types

The chat interface handles multiple event kinds defined in the `TimelineEvent` union type:

| Event Kind | Description | Rendering |
|------------|-------------|-----------|
| `message` | User or agent text messages | Chat bubble with author label |
| `steps` | Tool execution cluster | Collapsible tool chips |
| `schedule` | Schedule configuration event | Schedule card with cron details |

### Real-Time Event Reception

The `receiveRealtimeEvent(event)` method handles incoming WebSocket events with special logic for tool clusters:

```mermaid
graph TB
    Receive["receiveRealtimeEvent(event)"]
    Normalize["normalizeEvent(event)"]
    CheckPin{autoScrollPinned?}
    
    CheckKind{event.kind === 'steps'<br/>AND<br/>last event is 'steps'?}
    
    MergeCluster["mergeClusters(lastEvent, event)<br/>Replace last event"]
    RegularMerge["mergeEvents([event])<br/>Append event"]
    
    AddPending["Add to pendingEvents<br/>Set hasUnseenActivity"]
    UpdateTimeline["Update events array<br/>Update cursors"]
    
    Receive --> Normalize
    Normalize --> CheckPin
    
    CheckPin -->|false| AddPending
    CheckPin -->|true| CheckKind
    
    CheckKind -->|true| MergeCluster
    CheckKind -->|false| RegularMerge
    
    MergeCluster --> UpdateTimeline
    RegularMerge --> UpdateTimeline
```

The special handling for consecutive tool clusters prevents timeline fragmentation when an agent executes multiple tools in succession [frontend/src/stores/agentChatStore.ts:396-427]().

**Sources:**
- [frontend/src/stores/agentChatStore.ts:396-427]()

### Message Sending Flow

```mermaid
sequenceDiagram
    participant User
    participant Composer as AgentComposer
    participant Page as AgentChatPage
    participant Store as agentChatStore
    participant API as sendAgentMessage
    
    User->>Composer: Type message & submit
    Composer->>Page: onSendMessage(body)
    Page->>Store: sendMessage(body)
    Store->>Store: Validate & trim
    Store->>API: POST /messages/
    API-->>Store: TimelineEvent (optimistic)
    Store->>Store: receiveRealtimeEvent(event)
    Store->>Store: Merge into events
    Page->>Page: scrollToBottom() if pinned
```

After sending, if auto-scroll is pinned, the page explicitly scrolls to bottom to ensure the user's message is visible [frontend/src/screens/AgentChatPage.tsx:165-172]().

**Sources:**
- [frontend/src/stores/agentChatStore.ts:376-394]()
- [frontend/src/screens/AgentChatPage.tsx:165-172]()

---

## Real-Time Integration

### WebSocket Connection

The `useAgentChatSocket` hook (referenced but not provided in files) establishes a WebSocket connection for the agent. Based on the store integration, it must call:
- `receiveRealtimeEvent(event)` when timeline events arrive
- `updateProcessing(snapshot)` when processing status changes

### Processing Status Polling

The store provides `refreshProcessing()` to manually fetch current processing status via `fetchProcessingStatus()` API [frontend/src/stores/agentChatStore.ts:251-263]().

Processing snapshots include:
- `active`: Boolean indicating if any processing is occurring
- `webTasks`: Array of `ProcessingWebTask` objects with status, prompt, timestamps

**Processing Snapshot Normalization:**

The `normalizeProcessingUpdate()` function coerces various input formats (boolean, partial snapshot, null) into a consistent `ProcessingSnapshot` structure [frontend/src/stores/agentChatStore.ts:135-168]().

**Sources:**
- [frontend/src/stores/agentChatStore.ts:251-263]()
- [frontend/src/stores/agentChatStore.ts:135-168]()
- [frontend/src/stores/agentChatStore.ts:429-436]()

---

## Processing Indicator Display

### Task Card Structure

Each processing web task is rendered as a card showing:

| Field | Display |
|-------|---------|
| `status` | Badge with color-coded status (pending/completed/failed) |
| `elapsedSeconds` | Duration in human-readable format |
| `promptPreview` | Truncated task prompt |
| `prompt` | Full prompt (when expanded) |
| `id` | Task UUID in monospace font |

**Task Status Color Mapping:**

```css
.processing-task-status[data-status='pending'] { color: #6366f1; }
.processing-task-status[data-status='completed'] { color: #0f766e; }
.processing-task-status[data-status='failed'] { color: #dc2626; }
```

**Sources:**
- [frontend/src/styles/agentChatLegacy.css:163-292]()

### Expandable Behavior

The processing indicator supports two states:
1. **Collapsed**: Shows count badge (e.g., "2 tasks") with pulsing pip
2. **Expanded** (via `data-expanded='true'`): Shows full task list with individual cards

When expanded, the pulsing pip is hidden via `.processing-pip { display: none; }` [frontend/src/styles/agentChatLegacy.css:75-77]().

**Sources:**
- [frontend/src/styles/agentChatLegacy.css:67-77]()
- [frontend/src/styles/agentChatLegacy.css:144-156]()

---

## CSS Architecture

### ID-Based Styling

The chat interface relies heavily on ID-based selectors for predictable styling of singleton elements:

| Element ID | Purpose |
|------------|---------|
| `#agent-workspace-root` | Main container with min-height |
| `#timeline-shell` | Centered, max-width container |
| `#timeline-events` | Scrollable timeline with dynamic padding |
| `#processing-indicator-slot` | Conditional processing indicator wrapper |
| `#timeline-bottom-sentinel` | IntersectionObserver target |
| `#jump-to-latest` | Fixed-position navigation button |

**Sources:**
- [frontend/src/styles/agentChatLegacy.css:1-26]()

### Data Attributes for State

The layout uses data attributes to control visibility and styling without JavaScript DOM manipulation:

```css
#timeline-events[data-has-jump-button="true"] {
  padding-bottom: calc(var(--composer-height, 6.5rem) + 2rem);
}

#processing-indicator-slot[data-visible="true"] {
  display: flex;
}

.jump-to-latest[data-visible='false'] {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}
```

**Sources:**
- [frontend/src/styles/agentChatLegacy.css:20-22]()
- [frontend/src/styles/agentChatLegacy.css:45-49]()
- [frontend/src/styles/agentChatLegacy.css:392-397]()

### Animation System

The interface includes several CSS animations:

| Animation | Applied To | Effect |
|-----------|-----------|--------|
| `processingPulse` | `.processing-pip`, `.loading-pip` | Pulsing scale + shadow effect |
| `timelineLoadPulse` | `.timeline-load-indicator[data-loading='true']` | Pulsing opacity during loading |
| `timelineEventIncoming` | `.timeline-event--incoming` | Slide-up fade-in for new events |
| `timelineEventBubbleHighlight` | `.timeline-event--incoming .chat-bubble` | Shadow emphasis on new messages |

All animations respect `prefers-reduced-motion` media query [frontend/src/styles/agentChatLegacy.css:567-579]().

**Sources:**
- [frontend/src/styles/agentChatLegacy.css:294-307]()
- [frontend/src/styles/agentChatLegacy.css:490-503]()
- [frontend/src/styles/agentChatLegacy.css:547-579]()

---

## Responsive Behavior

The chat interface adapts to mobile viewports with specific breakpoint adjustments:

**Mobile Optimizations (`@media (max-width: 768px)`):**

| Element | Desktop | Mobile |
|---------|---------|--------|
| Composer bottom margin | `1.25rem` | `1rem` |
| Timeline padding-bottom | `calc(var(--composer-height) - 0.5rem)` | `calc(var(--composer-height) - 0.75rem)` |
| Jump button size | `3.25rem × 3.25rem` | `2.85rem × 2.85rem` |
| Chat bubble max-width | `min(60rem, 100%)` | `95%` |
| Chat bubble font-size | `0.9375rem` | `0.9rem` |

**Sources:**
- [frontend/src/styles/agentChatLegacy.css:1290-1316]()

---

## Initialization and Lifecycle

### Page Initialization Flow

```mermaid
sequenceDiagram
    participant Mount
    participant Page as AgentChatPage
    participant Store as agentChatStore
    participant Socket as useAgentChatSocket
    participant Session as useAgentWebSession
    participant API
    
    Mount->>Page: useEffect (agentId changed)
    Page->>Store: initialize(agentId)
    Store->>Store: Reset state, set loading=true
    Store->>API: fetchAgentTimeline(initial, limit=100)
    API-->>Store: { events, has_more_*, processing_* }
    Store->>Store: Normalize & sort events
    Store->>Store: Set cursors, processing state
    Store->>Store: Set loading=false, autoScrollPinned=true
    
    Page->>Socket: useAgentChatSocket(agentId)
    Socket->>Socket: Establish WebSocket connection
    
    Page->>Session: useAgentWebSession(agentId)
    Session->>Session: Maintain session heartbeat
    
    Page->>Page: Setup IntersectionObserver
    Page->>Page: Setup scroll listeners
    Page->>Page: useLayoutEffect → scrollToBottom()
```

The initialization sequence ensures:
1. State is reset before fetching to prevent stale data
2. Auto-scroll starts pinned to show latest events
3. Real-time connection establishes after initial load
4. Scroll observers activate to track user navigation

**Sources:**
- [frontend/src/screens/AgentChatPage.tsx:29-65]()
- [frontend/src/stores/agentChatStore.ts:217-249]()

### Cleanup and Unmount

The page registers cleanup functions for:
- Scroll event listeners (window, document, scrollingElement) [frontend/src/screens/AgentChatPage.tsx:112-116]()
- IntersectionObserver disconnection [frontend/src/screens/AgentChatPage.tsx:151-153]()

**Sources:**
- [frontend/src/screens/AgentChatPage.tsx:69-117]()
- [frontend/src/screens/AgentChatPage.tsx:133-154]()

---

## Jump to Latest Functionality

The jump-to-latest button provides a mechanism to quickly return to the most recent events:

```mermaid
graph TB
    Button["#jump-to-latest button"]
    Visible{Should show?}
    Handler["handleJumpToLatest()"]
    Store["jumpToLatest()"]
    API["fetchAgentTimeline(initial)"]
    Scroll["scrollTo(scrollHeight)"]
    Pin["setAutoScrollPinned(true)"]
    
    Button --> Visible
    Visible -->|hasMoreNewer OR<br/>hasUnseenActivity OR<br/>!autoScrollPinned| Button
    
    Button --> Handler
    Handler --> Store
    Store --> API
    API --> Store
    Store --> Handler
    Handler --> Scroll
    Handler --> Pin
    
    style Visible fill:#fff4e1
```

The button visibility logic [frontend/src/components/agentChat/AgentChatLayout.tsx:52-52]():
- `hasMoreNewer`: User scrolled into history
- `hasUnseenActivity`: New events arrived while unpinned
- `!autoScrollPinned`: User manually disabled auto-scroll

When clicked, the button:
1. Calls `store.jumpToLatest()` which re-fetches initial timeline window
2. Clears `pendingEvents` and `hasUnseenActivity`
3. Scrolls viewport to bottom
4. Forcibly re-enables auto-scroll pinning

**Sources:**
- [frontend/src/components/agentChat/AgentChatLayout.tsx:52-143]()
- [frontend/src/screens/AgentChatPage.tsx:156-163]()
- [frontend/src/stores/agentChatStore.ts:342-374]()

---

## Timeline Navigation Controls

### Load Older Button

Appears at the top of the timeline when `hasMoreOlder === true`. The button:
- Shows loading state via `data-loading` attribute
- Disabled while `loadingOlder === true`
- Triggers `onLoadOlder` callback which invokes `store.loadOlder()`

When exhausted (`!hasMoreOlder && !initialLoading`), displays "Beginning of history" label instead [frontend/src/components/agentChat/AgentChatLayout.tsx:80-82]().

**Sources:**
- [frontend/src/components/agentChat/AgentChatLayout.tsx:64-83]()

### Load Newer Button

Appears at the bottom of the timeline (above the bottom sentinel) when `hasMoreNewer === true`. Mirrors the "Load older" behavior but fetches in the opposite direction [frontend/src/components/agentChat/AgentChatLayout.tsx:105-122]().

**Sources:**
- [frontend/src/components/agentChat/AgentChatLayout.tsx:105-122]()

### Loading States

Both buttons use a shared `.timeline-load-button` class with pulsing indicator:

```css
.timeline-load-indicator[data-loading='true'] {
  animation: timelineLoadPulse 0.9s linear infinite;
}
```

The indicator pulses between 30% and 90% opacity with scale transforms [frontend/src/styles/agentChatLegacy.css:486-503]().

**Sources:**
- [frontend/src/styles/agentChatLegacy.css:443-503]()

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [api/exceptions.py](api/exceptions.py)
- [api/migrations/0145_browseruseagenttask_organization_and_more.py](api/migrations/0145_browseruseagenttask_organization_and_more.py)
- [api/serializers.py](api/serializers.py)
- [api/services/persistent_agents.py](api/services/persistent_agents.py)
- [api/urls.py](api/urls.py)
- [api/views.py](api/views.py)
- [tests/unit/test_api.py](tests/unit/test_api.py)
- [tests/unit/test_api_persistent_agents.py](tests/unit/test_api_persistent_agents.py)

</details>



## Purpose and Scope

This page provides a technical overview of the gobii-platform REST API, including endpoint structure, request/response patterns, and authentication mechanisms. For detailed endpoint specifications and request/response formats, see [REST API](#9.1). For authentication and authorization implementation details, see [Authentication & Authorization](#9.2).

The API exposes programmatic access to agent creation, task management, timeline events, and communication endpoints. All API interactions require authentication via API keys and follow standard REST conventions with JSON payloads.

---

## API Overview

### Base Configuration

The API is exposed under the `/api/v1/` prefix and is implemented using Django REST Framework. All endpoints return JSON responses and accept JSON request bodies.

**Key Characteristics:**
- **Content Type:** `application/json`
- **Authentication:** API Key via `X-API-KEY` header
- **Pagination:** Page-based with configurable page size (default 10, max 100)
- **Error Format:** JSON with `detail` field and HTTP status codes
- **Timestamp Format:** ISO 8601 with UTC timezone

**Sources:** [api/urls.py:1-87](), [api/views.py:64-68]()

### Error Handling

The platform uses a custom exception handler that ensures all API errors return JSON, even for unexpected exceptions. Each unhandled error receives a unique `error_id` for tracking.

```python
# Example error response
{
  "detail": "Internal server error.",
  "error_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Sources:** [api/exceptions.py:12-42]()

---

## Authentication Model

The platform supports two types of API keys:

| Type | Owner | Scope | Agent Access |
|------|-------|-------|-------------|
| **Personal** | User | User's resources only | User's agents and tasks |
| **Organization** | Organization | Organization resources only | Organization agents and tasks |

Organization API keys have additional restrictions:
- Cannot create `BrowserUseAgent` instances directly (must use `PersistentAgent`)
- Automatically set `organization` field on created resources
- Cannot access personal resources of organization members

For implementation details, see [Authentication & Authorization](#9.2).

**Sources:** [api/views.py:100-104](), [api/views.py:198-202](), [tests/unit/test_api.py:262-381]()

---

## API Request Flow

The following diagram illustrates how API requests flow through the platform components:

**Diagram: API Request Processing Pipeline**

```mermaid
graph TB
    Client[API Client]
    AuthMW[Authentication Middleware]
    ViewSet[ViewSet<br/>e.g. PersistentAgentViewSet]
    Serializer[Serializer<br/>e.g. PersistentAgentSerializer]
    Service[Business Logic<br/>e.g. PersistentAgentProvisioningService]
    DB[(PostgreSQL)]
    Celery[Celery Task Queue]
    ExceptionHandler[json_exception_handler]
    
    Client -->|"POST /api/v1/agents/"| AuthMW
    AuthMW -->|Validate X-API-KEY| ViewSet
    ViewSet -->|get_serializer| Serializer
    Serializer -->|validate data| Serializer
    ViewSet -->|perform_create| Service
    Service -->|provision agent| DB
    Service -->|on_commit| Celery
    DB -->|agent created| Service
    Service -->|return ProvisioningResult| ViewSet
    ViewSet -->|serialize response| Serializer
    Serializer -->|JSON response| Client
    
    ViewSet -.->|exception| ExceptionHandler
    Serializer -.->|ValidationError| ExceptionHandler
    Service -.->|PersistentAgentProvisioningError| ExceptionHandler
    ExceptionHandler -->|JSON error| Client
    
    style Service fill:#e1f5ff
    style Celery fill:#fff4e1
```

**Sources:** [api/views.py:664-702](), [api/serializers.py:370-433](), [api/services/persistent_agents.py:51-169](), [api/exceptions.py:12-42]()

---

## Endpoint Architecture

The API organizes endpoints into three primary categories: agent management, task operations, and agent communication/monitoring.

**Diagram: Endpoint Category Map**

```mermaid
graph LR
    subgraph "Agent Management"
        AgentsList["GET /api/v1/agents/<br/>List PersistentAgents"]
        AgentsCreate["POST /api/v1/agents/<br/>Create PersistentAgent"]
        AgentsGet["GET /api/v1/agents/{id}/<br/>Get PersistentAgent"]
        AgentsUpdate["PATCH /api/v1/agents/{id}/<br/>Update PersistentAgent"]
        AgentsDelete["DELETE /api/v1/agents/{id}/<br/>Soft-delete PersistentAgent"]
        
        BrowserList["GET /api/v1/agents/browser-use/<br/>List BrowserUseAgents"]
        BrowserGet["GET /api/v1/agents/browser-use/{id}/<br/>Get BrowserUseAgent"]
    end
    
    subgraph "Task Operations"
        TasksAgentList["GET /agents/browser-use/{agentId}/tasks/<br/>List agent tasks"]
        TasksAgentCreate["POST /agents/browser-use/{agentId}/tasks/<br/>Create agent task"]
        TasksUserList["GET /tasks/browser-use/<br/>List all user tasks"]
        TasksUserCreate["POST /tasks/browser-use/<br/>Create agentless task"]
        TaskGet["GET /tasks/browser-use/{id}/<br/>Get task details"]
        TaskUpdate["PATCH /tasks/browser-use/{id}/<br/>Update task prompt"]
        TaskCancel["POST /tasks/browser-use/{id}/cancel/<br/>Cancel task"]
        TaskResult["GET /tasks/browser-use/{id}/result/<br/>Get task result"]
    end
    
    subgraph "Communication & Monitoring"
        Timeline["GET /agents/{id}/timeline/<br/>Get timeline events"]
        ProcessingStatus["GET /agents/{id}/processing-status/<br/>Check processing state"]
        WebTasks["GET /agents/{id}/web-tasks/<br/>List browser tasks"]
        Messages["POST /agents/{id}/messages/<br/>Send message to agent"]
        SchedulePreview["POST /agents/{id}/schedule-preview/<br/>Preview schedule"]
    end
    
    subgraph "Utility"
        Ping["GET /api/v1/ping/<br/>Test connectivity"]
    end
```

**Sources:** [api/urls.py:23-86](), [api/views.py:149-156]()

### Dual-Scoped Task Endpoints

The platform provides both **agent-scoped** and **user-scoped** task endpoints to support different workflows:

```
# Agent-scoped: tasks must belong to specified agent
POST /api/v1/agents/browser-use/{agentId}/tasks/

# User-scoped: tasks can be agentless or specify agent in payload
POST /api/v1/tasks/browser-use/
```

When creating tasks through the user-scoped endpoint, the `agent` field is optional in the request body. Organization API keys automatically set the `organization` field on created tasks.

**Sources:** [api/views.py:301-343](), [api/views.py:354-367](), [api/urls.py:38-74]()

---

## Resource Ownership and Filtering

All API endpoints enforce ownership-based filtering to ensure users only access their own resources or resources within their organization.

**Diagram: Ownership Resolution Flow**

```mermaid
graph TB
    Request[Incoming Request]
    CheckAuth{Check request.auth}
    
    CheckAuth -->|"isinstance(auth, ApiKey)"| CheckOrg{auth.organization_id?}
    CheckAuth -->|"User session"| UserQuery["Filter: user=request.user"]
    
    CheckOrg -->|"Yes"| OrgQuery["Filter: organization=auth.organization"]
    CheckOrg -->|"No"| UserQuery
    
    OrgQuery --> OrgSet[Organization Resource Set]
    UserQuery --> UserSet[User Resource Set]
    
    OrgSet --> Response[Paginated Response]
    UserSet --> Response
    
    style CheckOrg fill:#e1f5ff
    style OrgQuery fill:#fff4e1
```

**Key Implementation Points:**

| ViewSet | Filter Logic | Code Reference |
|---------|-------------|----------------|
| `PersistentAgentViewSet` | `organization=org` or `user=user, organization__isnull=True` | [api/views.py:703-714]() |
| `BrowserUseAgentViewSet` | `persistent_agent__organization=org` or `user=user` | [api/views.py:106-129]() |
| `BrowserUseAgentTaskViewSet` | `organization=org` or `agent__persistent_agent__organization=org` or `user=user, organization__isnull=True` | [api/views.py:221-268]() |

**Sources:** [api/views.py:100-105](), [api/views.py:671-676]()

---

## Request Validation and Serialization

The platform uses Django REST Framework serializers for all request validation and response serialization. Each resource type has both detail and list serializers.

### Serializer Pairs

| Resource | List Serializer | Detail Serializer | Purpose |
|----------|----------------|-------------------|---------|
| `PersistentAgent` | `PersistentAgentListSerializer` | `PersistentAgentSerializer` | Agent CRUD with template support |
| `BrowserUseAgent` | `BrowserUseAgentListSerializer` | `BrowserUseAgentSerializer` | Browser agent metadata |
| `BrowserUseAgentTask` | `BrowserUseAgentTaskListSerializer` | `BrowserUseAgentTaskSerializer` | Task lifecycle management |

List serializers provide read-only fields for efficient listing, while detail serializers support write operations with full validation.

**Sources:** [api/serializers.py:198-230](), [api/serializers.py:259-310](), [api/views.py:131-135]()

### Field Validation Examples

**Schedule Validation:**
The `PersistentAgent` model validates schedule strings using `ScheduleParser` which supports cron expressions, `@daily`, and `@every` syntax:

```python
# Valid schedules
"@daily"
"0 0 * * *"
"@every 30m"
"@every 1h 30m"

# Invalid schedules
"@reboot"  # Not supported
"@every 5x"  # Invalid format
```

**Sources:** [api/serializers.py:276-298](), [tests/unit/test_api_persistent_agents.py:67-111]()

**Secrets Validation:**
Task secrets must follow domain-specific format and are encrypted before storage:

```json
{
  "https://example.com": {
    "x_api_key": "value",
    "x_username": "user"
  }
}
```

**Sources:** [api/serializers.py:122-145](), [api/views.py:340-362]()

---

## Wait Parameter and Synchronous Results

The task creation endpoint supports an optional `wait` parameter (0-1350 seconds) that allows clients to synchronously wait for task completion:

```json
POST /api/v1/agents/browser-use/{agentId}/tasks/
{
  "prompt": "Navigate to example.com",
  "wait": 600
}

Response (if completed):
{
  "id": "...",
  "status": "completed",
  "result": { /* task result data */ }
}

Response (if still running):
{
  "id": "...",
  "status": "in_progress"
}
```

The implementation uses Celery's `wait()` method on the AsyncResult object to block until completion or timeout.

**Sources:** [api/serializers.py:81-87](), [api/views.py:372-436](), [api/views.py:502-532]()

---

## Credit Gating

All task creation endpoints check credit availability before accepting requests. If the user has insufficient credits, the API returns HTTP 402 (Payment Required):

```json
{
  "message": "User does not have enough task credits to create a new task. Please upgrade your plan or enable extra task purchases."
}
```

Credit checks happen in the `create()` method before serializer validation to fail fast.

**Sources:** [api/views.py:505-512](), [util/constants/task_constants.py]()

---

## Pagination

All list endpoints use `StandardResultsSetPagination` with the following configuration:

| Parameter | Default | Maximum | Query Param |
|-----------|---------|---------|-------------|
| Page Size | 10 | 100 | `page_size` |
| Page Number | 1 | N/A | `page` |

Example paginated response:

```json
{
  "count": 42,
  "next": "http://api.example.com/api/v1/agents/?page=2",
  "previous": null,
  "results": [ /* array of resources */ ]
}
```

**Sources:** [api/views.py:65-68](), [api/views.py:98]()

---

## Soft Deletion

The `BrowserUseAgentTask` model implements soft deletion. When a task is deleted via the API, it is marked as deleted but retained in the database:

```python
# DELETE /api/v1/tasks/browser-use/{id}/
# Sets: is_deleted=True, deleted_at=<timestamp>
```

Soft-deleted tasks are filtered from all list queries using the `alive()` queryset manager.

**Sources:** [api/views.py:534-560](), [tests/unit/test_api.py:837-865]()

---

## OpenAPI Schema Generation

The API uses `drf-spectacular` for automatic OpenAPI schema generation. All ViewSets and actions are decorated with `@extend_schema` to provide operation IDs and tags:

```python
@extend_schema_view(
    list=extend_schema(operation_id='listPersistentAgents', tags=['persistent-agents']),
    create=extend_schema(operation_id='createPersistentAgent', tags=['persistent-agents']),
    # ...
)
class PersistentAgentViewSet(viewsets.ModelViewSet):
    # ...
```

This enables automatic generation of client libraries and interactive API documentation.

**Sources:** [api/views.py:83-90](), [api/views.py:158-181](), [api/views.py:656-663]()

---

## Webhook Endpoints

The platform exposes several webhook endpoints for external integrations:

| Endpoint | Purpose | Authentication |
|----------|---------|----------------|
| `/api/v1/webhooks/inbound/sms/` | Twilio SMS delivery | Twilio signature validation |
| `/api/v1/webhooks/status/sms/` | Twilio delivery status | Twilio signature validation |
| `/api/v1/webhooks/inbound/email/` | Postmark email delivery | Postmark token validation |
| `/api/v1/webhooks/inbound/email/mg/` | Mailgun email delivery | Mailgun signature validation |
| `/api/v1/webhooks/pipedream/connect/{session_id}/` | Pipedream OAuth completion | Session ID validation |
| `/api/v1/webhooks/bi/email/` | Email open/click tracking | Open tracking pixel |

These endpoints do not require API key authentication but use provider-specific validation mechanisms.

**Sources:** [api/urls.py:76-86](), [api/webhooks.py]()

---

## Common Response Patterns

### Success Responses

| Status | Meaning | Example Operations |
|--------|---------|-------------------|
| 200 OK | Resource retrieved/updated | GET, PATCH |
| 201 Created | Resource created | POST (create agent, task) |
| 204 No Content | Resource deleted | DELETE |

### Error Responses

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| 400 Bad Request | Validation error | Invalid schedule, missing required fields |
| 401 Unauthorized | Missing API key | No `X-API-KEY` header |
| 402 Payment Required | Insufficient credits | Credit quota exhausted |
| 403 Forbidden | Invalid API key | Malformed or expired key |
| 404 Not Found | Resource not found or access denied | Agent doesn't exist or belongs to another user |
| 409 Conflict | Resource state conflict | Cancelling a completed task |
| 500 Internal Server Error | Unexpected error | Includes `error_id` for tracking |

**Sources:** [api/views.py:505-512](), [api/views.py:647-653](), [api/exceptions.py:35-39]()

---

## Analytics Tracking

All API operations emit analytics events for monitoring and billing purposes. The `Analytics` service tracks:

- `AGENTS_LISTED`, `AGENT_CREATED`
- `TASKS_LISTED`, `TASK_CREATED`, `TASK_DELETED`, `TASK_CANCELLED`, `TASK_RESULT_VIEWED`
- Organization-specific variants (e.g., `ORGANIZATION_TASK_CREATED`)

Events include properties like `agent_id`, `task_id`, `organization_id`, and operation metadata.

**Sources:** [api/views.py:115-128](), [api/views.py:144](), [api/views.py:476-492]()

---

For detailed endpoint specifications, request/response schemas, and example payloads, see [REST API](#9.1). For API key creation, permissions, and the dual-ownership model, see [Authentication & Authorization](#9.2).

---

# Page: REST API

# REST API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [api/exceptions.py](api/exceptions.py)
- [api/migrations/0145_browseruseagenttask_organization_and_more.py](api/migrations/0145_browseruseagenttask_organization_and_more.py)
- [api/serializers.py](api/serializers.py)
- [api/services/persistent_agents.py](api/services/persistent_agents.py)
- [api/urls.py](api/urls.py)
- [api/views.py](api/views.py)
- [tests/unit/test_api.py](tests/unit/test_api.py)
- [tests/unit/test_api_persistent_agents.py](tests/unit/test_api_persistent_agents.py)

</details>



This document describes the HTTP REST API endpoints for managing agents, tasks, timelines, and messages. The API follows RESTful conventions and returns JSON responses. For authentication mechanisms including API keys, see [Authentication & Authorization](#9.2). For WebSocket-based real-time communication, that is covered separately.

---

## Purpose and Scope

The REST API provides programmatic access to the gobii-platform's core functionality:
- Creating and managing agents (both `BrowserUseAgent` and `PersistentAgent`)
- Submitting and monitoring browser automation tasks
- Sending messages to agents
- Retrieving execution timelines and processing status
- Managing agent configurations (schedules, contacts, secrets)

The API supports both user-owned and organization-owned resources via a dual-ownership authentication model detailed in [Authentication & Authorization](#9.2).

---

## Base URL and Versioning

All API endpoints are prefixed with `/api/v1/`. The current implementation does not use explicit versioning beyond this prefix.

**Example Base URL:**
```
https://app.gobii.ai/api/v1/
```

Sources: [api/urls.py:1-86]()

---

## Authentication

The API uses custom API key authentication via the `X-Api-Key` HTTP header. All endpoints require authentication except for webhooks.

**Request Header:**
```
X-Api-Key: <your-api-key>
```

API keys can be scoped to either:
- **Personal Keys**: Access user-owned resources
- **Organization Keys**: Access organization-owned resources

The authentication layer automatically determines ownership context and filters querysets accordingly. See [Authentication & Authorization](#9.2) for detailed implementation.

Sources: [api/views.py:100-104](), [api/views.py:198-202](), [api/views.py:671-675]()

---

## URL Routing Architecture

The following diagram shows the complete URL structure and how routes map to ViewSets:

```mermaid
graph TD
    subgraph "Utility Endpoints"
        ping["/ping/"]
    end
    
    subgraph "Agent Resources"
        agents["/agents/"]
        browserAgents["/agents/browser-use/"]
        
        agents --> agentDetail["/agents/{id}/"]
        browserAgents --> browserDetail["/agents/browser-use/{id}/"]
        
        agentDetail --> timeline["/agents/{id}/timeline/"]
        agentDetail --> messages["/agents/{id}/messages/"]
        agentDetail --> status["/agents/{id}/processing-status/"]
        agentDetail --> webTasks["/agents/{id}/web-tasks/"]
        agentDetail --> schedulePreview["/agents/{id}/preview-schedule/"]
    end
    
    subgraph "Task Resources - Agent Scoped"
        browserAgentTasks["/agents/browser-use/{agentId}/tasks/"]
        browserAgentTasks --> agentTaskDetail["/agents/browser-use/{agentId}/tasks/{id}/"]
        agentTaskDetail --> agentTaskResult["/agents/browser-use/{agentId}/tasks/{id}/result/"]
        agentTaskDetail --> agentTaskCancel["/agents/browser-use/{agentId}/tasks/{id}/cancel/"]
    end
    
    subgraph "Task Resources - User Scoped"
        userTasks["/tasks/browser-use/"]
        userTasks --> userTaskDetail["/tasks/browser-use/{id}/"]
        userTaskDetail --> userTaskResult["/tasks/browser-use/{id}/result/"]
        userTaskDetail --> userTaskCancel["/tasks/browser-use/{id}/cancel/"]
    end
    
    subgraph "Webhook Endpoints"
        webhooks["/webhooks/..."]
        webhooks --> smsWebhook["/webhooks/inbound/sms/"]
        webhooks --> emailWebhook["/webhooks/inbound/email/"]
        webhooks --> pipedreamWebhook["/webhooks/pipedream/connect/{session_id}/"]
    end
    
    ping -.-> PingView["ping()"]
    agents -.-> PersistentAgentViewSet
    browserAgents -.-> BrowserUseAgentViewSet
    browserAgentTasks -.-> BrowserUseAgentTaskViewSet
    userTasks -.-> BrowserUseAgentTaskViewSet
```

**URL Pattern Summary:**

| Pattern | ViewSet | Purpose |
|---------|---------|---------|
| `/agents/` | `PersistentAgentViewSet` | CRUD for persistent agents |
| `/agents/browser-use/` | `BrowserUseAgentViewSet` | CRUD for browser-use agents |
| `/agents/browser-use/{agentId}/tasks/` | `BrowserUseAgentTaskViewSet` | Agent-specific tasks |
| `/tasks/browser-use/` | `BrowserUseAgentTaskViewSet` | User-level tasks (optional agent) |
| `/webhooks/...` | Various webhook handlers | Inbound message ingestion |

Sources: [api/urls.py:29-86]()

---

## Core ViewSets and Serializers

The API uses Django REST Framework's ViewSet pattern. Each ViewSet handles CRUD operations and custom actions for a specific resource.

```mermaid
graph LR
    subgraph "ViewSets"
        BrowserUseAgentViewSet["BrowserUseAgentViewSet<br/>(browser-use agents)"]
        PersistentAgentViewSet["PersistentAgentViewSet<br/>(persistent agents)"]
        BrowserUseAgentTaskViewSet["BrowserUseAgentTaskViewSet<br/>(tasks)"]
    end
    
    subgraph "Serializers - List"
        BrowserUseAgentListSerializer
        PersistentAgentListSerializer
        BrowserUseAgentTaskListSerializer
    end
    
    subgraph "Serializers - Detail"
        BrowserUseAgentSerializer
        PersistentAgentSerializer
        BrowserUseAgentTaskSerializer
    end
    
    BrowserUseAgentViewSet --> BrowserUseAgentListSerializer
    BrowserUseAgentViewSet --> BrowserUseAgentSerializer
    
    PersistentAgentViewSet --> PersistentAgentListSerializer
    PersistentAgentViewSet --> PersistentAgentSerializer
    
    BrowserUseAgentTaskViewSet --> BrowserUseAgentTaskListSerializer
    BrowserUseAgentTaskViewSet --> BrowserUseAgentTaskSerializer
```

**ViewSet-Serializer Mapping:**

The API uses different serializers for list vs. detail operations to optimize payload size:

- **List operations** return minimal fields (id, name, timestamps)
- **Detail operations** return full resource representations

Sources: [api/views.py:91-147](), [api/views.py:183-561](), [api/views.py:664-1062](), [api/serializers.py:19-466]()

---

## Resource: Browser-Use Agents

Browser-use agents represent the underlying browser automation engine. Most users interact with persistent agents instead, but this resource is exposed for direct task submission.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/agents/browser-use/` | List all browser agents |
| POST | `/agents/browser-use/` | Create a new browser agent |
| GET | `/agents/browser-use/{id}/` | Get agent details |
| PATCH | `/agents/browser-use/{id}/` | Update agent |
| DELETE | `/agents/browser-use/{id}/` | Delete agent |

### List Browser Agents

**Request:**
```http
GET /api/v1/agents/browser-use/
X-Api-Key: <key>
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Agent 1",
      "created_at": "2024-01-15T10:30:00Z",
      "listing_description": "Automates product updates",
      "listing_description_source": "charter"
    }
  ]
}
```

### Create Browser Agent

**Request:**
```http
POST /api/v1/agents/browser-use/
X-Api-Key: <key>
Content-Type: application/json

{
  "name": "My Agent"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_email": "user@example.com",
  "name": "My Agent",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "listing_description": "Agent is initializing…",
  "listing_description_source": "placeholder"
}
```

**Important:** Organization API keys cannot create browser agents directly (returns 400). Organizations must create persistent agents instead, which automatically provision a browser agent.

Sources: [api/views.py:91-147](), [api/serializers.py:19-67](), [tests/unit/test_api.py:64-231]()

---

## Resource: Persistent Agents

Persistent agents are the primary interface for scheduled, stateful automation. They wrap a browser-use agent and add scheduling, communication channels, and lifecycle management.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/agents/` | List all persistent agents |
| POST | `/agents/` | Create a new persistent agent |
| GET | `/agents/{id}/` | Get agent details |
| PATCH | `/agents/{id}/` | Update agent configuration |
| DELETE | `/agents/{id}/` | Soft-delete agent (sets expired) |
| GET | `/agents/{id}/timeline/` | Get event timeline |
| POST | `/agents/{id}/messages/` | Send message to agent |
| GET | `/agents/{id}/processing-status/` | Check if agent is processing |
| GET | `/agents/{id}/web-tasks/` | List browser tasks for agent |
| POST | `/agents/{id}/preview-schedule/` | Preview schedule execution times |

### Create Persistent Agent

The provisioning process creates both a `PersistentAgent` and underlying `BrowserUseAgent` atomically.

**Request:**
```http
POST /api/v1/agents/
X-Api-Key: <key>
Content-Type: application/json

{
  "name": "Sales Assistant",
  "charter": "Monitor CRM for new leads and send welcome emails",
  "schedule": "0 9 * * 1-5",
  "is_active": true,
  "preferred_contact_endpoint": "email"
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Sales Assistant",
  "charter": "Monitor CRM for new leads and send welcome emails",
  "short_description": "Monitor CRM for new leads and send welcome emails",
  "schedule": "0 9 * * 1-5",
  "schedule_snapshot": null,
  "is_active": true,
  "life_state": "active",
  "whitelist_policy": "default",
  "last_interaction_at": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_id": "770e8400-e29b-41d4-a716-446655440002",
  "organization_id": null,
  "browser_use_agent_id": "880e8400-e29b-41d4-a716-446655440003",
  "preferred_contact_endpoint_id": "990e8400-e29b-41d4-a716-446655440004"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique agent name for owner |
| `charter` | string | No | Agent's purpose and instructions |
| `schedule` | string | No | Cron expression or `@every` syntax |
| `is_active` | boolean | No | Whether agent can execute (default: true) |
| `preferred_contact_endpoint` | string/uuid | No | `"email"`, `"sms"`, or endpoint ID |
| `template_code` | string | No | AI employee template to apply |

**Provisioning Behavior:**

1. Validates agent quota via `AgentService.has_agents_available()`
2. Creates `BrowserUseAgent` with unique name
3. Creates `PersistentAgent` linked to browser agent
4. Applies template if `template_code` provided (overwrites charter/schedule)
5. Sets default `daily_credit_limit` for free plans
6. Enqueues `process_agent_events_task` on transaction commit

Sources: [api/views.py:664-754](), [api/serializers.py:259-466](), [api/services/persistent_agents.py:27-180](), [tests/unit/test_api_persistent_agents.py:262-339]()

---

### Update Persistent Agent

**Request:**
```http
PATCH /api/v1/agents/{id}/
X-Api-Key: <key>
Content-Type: application/json

{
  "charter": "Updated instructions",
  "is_active": false
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Sales Assistant",
  "charter": "Updated instructions",
  "is_active": false,
  ...
}
```

**Updatable Fields:**
- `name`, `charter`, `short_description`, `schedule`
- `is_active`, `life_state`, `whitelist_policy`
- `preferred_contact_endpoint`

All other fields are read-only.

Sources: [api/serializers.py:435-465](), [tests/unit/test_api_persistent_agents.py:340-374]()

---

### Soft Delete Agent

Deleting an agent sets `life_state=EXPIRED`, `is_active=False`, and clears `schedule`.

**Request:**
```http
DELETE /api/v1/agents/{id}/
X-Api-Key: <key>
```

**Response:**
```
204 No Content
```

The agent record remains in the database but will not execute.

Sources: [api/views.py:755-779](), [tests/unit/test_api_persistent_agents.py:376-387]()

---

### Timeline Endpoint

The timeline provides a chronological view of agent activity including messages, steps, and reasoning.

**Request:**
```http
GET /api/v1/agents/{id}/timeline/?cursor=<cursor>&limit=50
X-Api-Key: <key>
```

**Response:**
```json
{
  "events": [
    {
      "kind": "message",
      "id": "msg-123",
      "timestamp": "2024-01-15T10:30:00Z",
      "conversation_id": "conv-456",
      "direction": "inbound",
      "channel": "email",
      "sender": "user@example.com",
      "subject": "Question about reports",
      "body": "Can you send me the latest report?",
      "metadata": {}
    },
    {
      "kind": "step",
      "id": "step-789",
      "timestamp": "2024-01-15T10:31:00Z",
      "step_number": 1,
      "model_output": "I'll retrieve the latest report.",
      "tool_calls": [],
      "is_result": false,
      "hidden": false
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjUwfQ==",
  "has_more": true
}
```

**Query Parameters:**
- `cursor`: Pagination cursor (opaque string)
- `limit`: Events per page (default: 25, max: 100)

Sources: [api/views.py:815-866](), [console/agent_chat/timeline.py:1-305]()

---

### Messages Endpoint

Submit messages to trigger agent processing. The agent will receive the message and respond based on its charter.

**Request:**
```http
POST /api/v1/agents/{id}/messages/
X-Api-Key: <key>
Content-Type: application/json

{
  "channel": "email",
  "sender": "user@example.com",
  "recipient": "agent@example.com",
  "subject": "Status update",
  "body": "Please provide the daily summary"
}
```

**Response:**
```json
{
  "message": {
    "id": "msg-123",
    "conversation_id": "conv-456",
    "direction": "inbound",
    "channel": "email",
    "sender": "user@example.com",
    "recipient": "agent@example.com",
    "subject": "Status update",
    "body": "Please provide the daily summary",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "event": {
    "kind": "message",
    "id": "msg-123",
    "timestamp": "2024-01-15T10:30:00Z",
    ...
  }
}
```

**Behavior:**
1. Validates sender against agent's allowlist
2. Creates `PersistentAgentMessage` linked to conversation
3. Enqueues `process_agent_events_task`
4. Returns message and timeline event representation

Sources: [api/views.py:868-941](), [tests/unit/test_api_persistent_agents.py:388-418]()

---

### Processing Status Endpoint

Check whether the agent is currently executing and view the active processing snapshot.

**Request:**
```http
GET /api/v1/agents/{id}/processing-status/
X-Api-Key: <key>
```

**Response:**
```json
{
  "processing_active": true,
  "processing_snapshot": {
    "agent_id": "660e8400-e29b-41d4-a716-446655440001",
    "agent_name": "Sales Assistant",
    "current_cycle_id": "cycle-123",
    "started_at": "2024-01-15T10:30:00Z",
    "last_step_at": "2024-01-15T10:31:45Z",
    "iteration_count": 3,
    "pending_tasks": 1,
    "recent_steps": [
      {
        "step_number": 3,
        "timestamp": "2024-01-15T10:31:45Z",
        "model_output": "Sending welcome email...",
        "tool_calls": ["send_email"]
      }
    ]
  }
}
```

Returns `processing_active: false` with `processing_snapshot: null` if agent is idle.

Sources: [api/views.py:943-984](), [console/agent_chat/timeline.py:175-238]()

---

## Resource: Browser-Use Tasks

Tasks represent discrete browser automation jobs. They can be agent-scoped (submitted to a specific agent) or agentless (submitted directly by a user).

### Endpoints

**Agent-Scoped:**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/agents/browser-use/{agentId}/tasks/` | List agent's tasks |
| POST | `/agents/browser-use/{agentId}/tasks/` | Create task for agent |
| GET | `/agents/browser-use/{agentId}/tasks/{id}/` | Get task details |
| PATCH | `/agents/browser-use/{agentId}/tasks/{id}/` | Update pending task |
| DELETE | `/agents/browser-use/{agentId}/tasks/{id}/` | Soft-delete task |
| GET | `/agents/browser-use/{agentId}/tasks/{id}/result/` | Get task result |
| POST | `/agents/browser-use/{agentId}/tasks/{id}/cancel/` | Cancel running task |

**User-Scoped (Agentless):**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks/browser-use/` | List user's tasks |
| POST | `/tasks/browser-use/` | Create agentless task |
| GET | `/tasks/browser-use/{id}/` | Get task details |
| ... | ... | (same detail operations) |

---

### Create Task Flow

The following diagram shows the complete task creation and execution pipeline:

```mermaid
sequenceDiagram
    participant Client
    participant ViewSet as BrowserUseAgentTaskViewSet
    participant CreditService as TaskCreditService
    participant Serializer as BrowserUseAgentTaskSerializer
    participant DB as Database
    participant Celery as Celery Queue
    participant Worker as Browser Worker
    
    Client->>ViewSet: POST /tasks/browser-use/
    ViewSet->>CreditService: calculate_available_tasks(user)
    
    alt No Credits Available
        CreditService-->>ViewSet: 0
        ViewSet-->>Client: 402 Payment Required
    end
    
    CreditService-->>ViewSet: credits available
    ViewSet->>Serializer: validate(data)
    Serializer-->>ViewSet: validated_data
    
    ViewSet->>DB: Create BrowserUseAgentTask
    DB-->>ViewSet: task instance
    
    alt Secrets Provided
        ViewSet->>ViewSet: encrypt_secrets()
        ViewSet->>DB: Save encrypted_secrets
    end
    
    alt wait parameter provided
        ViewSet->>Celery: apply_async(task_id)
        ViewSet->>ViewSet: async_result.wait(timeout=wait)
        
        Worker->>Worker: Execute browser automation
        Worker->>DB: Save result
        
        ViewSet->>DB: Refresh task
        ViewSet-->>Client: 201 with result
    else No wait parameter
        ViewSet->>Celery: delay(task_id)
        ViewSet-->>Client: 201 without result
    end
```

Sources: [api/views.py:301-532]()

---

### Create Task (Synchronous)

Submit a task and wait for its completion.

**Request:**
```http
POST /api/v1/agents/browser-use/{agentId}/tasks/
X-Api-Key: <key>
Content-Type: application/json

{
  "prompt": "Navigate to example.com and extract the page title",
  "output_schema": {
    "type": "object",
    "properties": {
      "title": {"type": "string"}
    },
    "required": ["title"]
  },
  "wait": 120,
  "secrets": {
    "https://example.com": {
      "api_key": "secret-value"
    }
  }
}
```

**Response (if completed within wait time):**
```json
{
  "id": "task-123",
  "agent_id": "agent-456",
  "status": "completed",
  "result": {
    "title": "Example Domain"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:15Z"
}
```

**Response (if still running after wait time):**
```json
{
  "id": "task-123",
  "agent_id": "agent-456",
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string/object | Yes | Task instructions or structured input |
| `output_schema` | object | No | JSON Schema for structured output |
| `wait` | integer | No | Seconds to wait (0-1350) |
| `secrets` | object | No | Domain-specific secrets for task |
| `credits_cost` | decimal | No | Custom credit cost override |

**Credit Gating:**

Before task creation, the system checks available credits:
- If `available <= 0` and not `TASKS_UNLIMITED`, returns `402 Payment Required`
- Credits are deducted during task execution by `TaskCreditService`

Sources: [api/views.py:301-532](), [api/serializers.py:69-161](), [tests/unit/test_api.py:383-529]()

---

### Secrets Encryption

The `secrets` field allows domain-specific authentication. Secrets are encrypted at rest using `SecretsEncryption`.

**Format:**
```json
{
  "secrets": {
    "https://example.com": {
      "x_api_key": "secret-value",
      "x_username": "user"
    },
    "https://another.com": {
      "authorization": "Bearer token"
    }
  }
}
```

**Validation:**
- Each key must be a valid domain pattern
- Secret values must be strings
- Total serialized size cannot exceed `MAX_TOTAL_SECRETS_SIZE_BYTES`
- Keys are logged for audit, values are never logged

Secrets are decrypted during task execution and injected as placeholders in the browser automation prompt.

Sources: [api/serializers.py:122-145](), [api/views.py:325-362]()

---

### Get Task Result

Retrieve the final output of a completed task.

**Request:**
```http
GET /api/v1/tasks/browser-use/{id}/result/
X-Api-Key: <key>
```

**Response (Completed):**
```json
{
  "id": "task-123",
  "agent_id": "agent-456",
  "status": "completed",
  "result": {
    "title": "Example Domain",
    "description": "This domain is for use in examples"
  }
}
```

**Response (Failed):**
```json
{
  "id": "task-123",
  "agent_id": "agent-456",
  "status": "failed",
  "result": null,
  "error_message": "Navigation timeout after 30 seconds"
}
```

**Response (Pending/Running):**
```json
{
  "id": "task-123",
  "agent_id": "agent-456",
  "status": "in_progress",
  "message": "Task is not yet completed."
}
```

Sources: [api/views.py:562-601](), [tests/unit/test_api.py:531-555]()

---

### Cancel Task

Cancel a pending or running task.

**Request:**
```http
POST /api/v1/tasks/browser-use/{id}/cancel/
X-Api-Key: <key>
```

**Response (Success):**
```json
{
  "status": "cancelled",
  "message": "Task has been cancelled."
}
```

**Response (Already Completed):**
```json
{
  "detail": "Task is already completed and cannot be cancelled."
}
```

Only tasks with status `PENDING` or `IN_PROGRESS` can be cancelled. Returns `409 Conflict` for other statuses.

Sources: [api/views.py:603-653](), [tests/unit/test_api.py:596-689]()

---

### Update Task (Pending Only)

Modify the prompt or output schema of a pending task.

**Request:**
```http
PATCH /api/v1/tasks/browser-use/{id}/
X-Api-Key: <key>
Content-Type: application/json

{
  "prompt": "Updated task instructions"
}
```

**Response:**
```json
{
  "id": "task-123",
  "agent_id": "agent-456",
  "prompt": "Updated task instructions",
  "status": "pending",
  ...
}
```

**Validation:**
- Task must have `status=PENDING`
- Returns `400 Bad Request` if task is `IN_PROGRESS`, `COMPLETED`, `FAILED`, or `CANCELLED`

Sources: [api/serializers.py:162-185](), [tests/unit/test_api.py:690-836]()

---

## Pagination

All list endpoints support cursor-based pagination via query parameters.

**Standard Pagination (Tasks/Agents):**
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 10, max: 100)

**Response Format:**
```json
{
  "count": 42,
  "next": "https://app.gobii.ai/api/v1/agents/?page=2",
  "previous": null,
  "results": [...]
}
```

**Timeline Pagination (Cursor-Based):**
- `cursor`: Opaque pagination token
- `limit`: Events per page (default: 25, max: 100)

**Response Format:**
```json
{
  "events": [...],
  "next_cursor": "eyJvZmZzZXQiOjI1fQ==",
  "has_more": true
}
```

Sources: [api/views.py:65-68](), [console/agent_chat/timeline.py:45-62]()

---

## Error Handling

The API returns structured error responses with consistent formatting.

### Error Response Format

```json
{
  "detail": "Error message",
  "field_name": ["Field-specific error"],
  "non_field_errors": ["General validation error"]
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Missing/invalid API key |
| 402 | Payment Required | Insufficient credits |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource doesn't exist or not owned |
| 409 | Conflict | State conflict (e.g., cancel completed task) |
| 500 | Internal Server Error | Unhandled exception |

### Validation Error Example

**Request:**
```http
POST /api/v1/agents/
X-Api-Key: <key>
Content-Type: application/json

{
  "name": "",
  "schedule": "invalid-cron"
}
```

**Response:**
```json
{
  "name": ["This field may not be blank."],
  "schedule": ["Invalid schedule format: 'invalid-cron' is not a valid cron expression or @every syntax."]
}
```

### Unhandled Exception Format

For unexpected errors, the system returns:

```json
{
  "detail": "Internal server error.",
  "error_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The `error_id` can be used to locate the exception in server logs.

Sources: [api/exceptions.py:12-42](), [api/serializers.py:422-426](), [api/serializers.py:458-461]()

---

## Ownership Filtering

The API automatically filters resources based on authentication context:

```mermaid
graph TD
    Request["HTTP Request<br/>X-Api-Key: key"] --> AuthMiddleware["ApiKeyAuthentication"]
    
    AuthMiddleware --> DetectKeyType{Key Type?}
    
    DetectKeyType -->|Personal| SetUserContext["request.auth = ApiKey<br/>org_id = None"]
    DetectKeyType -->|Organization| SetOrgContext["request.auth = ApiKey<br/>org_id = <uuid>"]
    
    SetUserContext --> ViewSet["ViewSet.get_queryset()"]
    SetOrgContext --> ViewSet
    
    ViewSet --> CheckOwnership{Owner Type?}
    
    CheckOwnership -->|User| FilterUser["qs.filter(user=request.user,<br/>organization__isnull=True)"]
    CheckOwnership -->|Organization| FilterOrg["qs.filter(organization=org)"]
    
    FilterUser --> Results["Filtered Queryset"]
    FilterOrg --> Results
```

**Implementation:**

Each ViewSet implements `_request_organization()` to detect the ownership context:

```python
def _request_organization(self):
    auth = getattr(self.request, 'auth', None)
    if isinstance(auth, ApiKey) and getattr(auth, 'organization_id', None):
        return auth.organization
    return None
```

When organization is detected:
- Agents: `qs.filter(organization=org)`
- Tasks: `qs.filter(Q(organization=org) | Q(agent__persistent_agent__organization=org))`

When organization is None (personal key):
- Agents: `qs.filter(user=request.user)`
- Tasks: `qs.filter(user=request.user, organization__isnull=True)`

Sources: [api/views.py:100-129](), [api/views.py:198-270](), [api/views.py:671-702](), [tests/unit/test_api.py:262-381]()

---

## Special Endpoints

### Ping

Simple connectivity test.

**Request:**
```http
GET /api/v1/ping/
X-Api-Key: <key>
```

**Response:**
```json
{
  "pong": true,
  "user": "user@example.com"
}
```

Sources: [api/views.py:149-155]()

---

### Schedule Preview

Preview when an agent's schedule will execute.

**Request:**
```http
POST /api/v1/agents/{id}/preview-schedule/
X-Api-Key: <key>
Content-Type: application/json

{
  "schedule": "0 9 * * 1-5"
}
```

**Response:**
```json
{
  "next_runs": [
    "2024-01-15T09:00:00Z",
    "2024-01-16T09:00:00Z",
    "2024-01-17T09:00:00Z"
  ],
  "description": "Every weekday at 9:00 AM"
}
```

Uses `ScheduleParser.parse()` to validate and compute execution times.

Sources: [api/views.py:1023-1062]()

---

## Rate Limiting and Quotas

### Credit Gating

All task creation is gated by credit availability:

1. **Pre-Creation Check**: `TaskCreditService.calculate_available_tasks(user)` in [api/views.py:506-512]()
2. Returns `402 Payment Required` if credits exhausted
3. **Runtime Consumption**: Credits deducted during task execution by [api/agent/core/event_processing.py]()

### Agent Quotas

Agent creation enforces `UserQuota.agent_limit`:

1. `AgentService.has_agents_available(user)` called during provisioning
2. Returns `PersistentAgentProvisioningError` if limit reached
3. Default limits defined in `constants/plans.py`

No explicit rate limiting exists beyond credit/quota enforcement.

Sources: [api/views.py:506-512](), [api/services/persistent_agents.py:71-72]()

---

## Common Request Patterns

### Create Agent + Submit Task

```python
import requests

headers = {"X-Api-Key": "your-key"}
base = "https://app.gobii.ai/api/v1"

# Create agent
agent_resp = requests.post(
    f"{base}/agents/",
    json={
        "name": "Data Extractor",
        "charter": "Extract product data from e-commerce sites",
        "schedule": "@daily"
    },
    headers=headers
)
agent_id = agent_resp.json()["browser_use_agent_id"]

# Submit task
task_resp = requests.post(
    f"{base}/agents/browser-use/{agent_id}/tasks/",
    json={
        "prompt": "Navigate to example.com and extract all product names",
        "wait": 120
    },
    headers=headers
)
print(task_resp.json())
```

### Poll Task Status

```python
task_id = "task-123"
agent_id = "agent-456"

while True:
    resp = requests.get(
        f"{base}/agents/browser-use/{agent_id}/tasks/{task_id}/result/",
        headers=headers
    )
    data = resp.json()
    
    if data["status"] == "completed":
        print(data["result"])
        break
    elif data["status"] == "failed":
        print(data["error_message"])
        break
    
    time.sleep(5)
```

### Send Message to Agent

```python
agent_id = "agent-789"

resp = requests.post(
    f"{base}/agents/{agent_id}/messages/",
    json={
        "channel": "email",
        "sender": "user@example.com",
        "recipient": "agent@example.com",
        "body": "Please provide the weekly report"
    },
    headers=headers
)
print(resp.json())
```

---

## Testing

The API includes comprehensive test coverage demonstrating usage patterns:

| Test File | Coverage Area |
|-----------|---------------|
| `tests/unit/test_api.py` | Browser agents, tasks, pagination, org keys |
| `tests/unit/test_api_persistent_agents.py` | Persistent agents, messages, timeline |

**Key Test Scenarios:**
- Agent CRUD with ownership validation [tests/unit/test_api.py:64-231]()
- Task creation with wait parameter [tests/unit/test_api.py:511-529]()
- Organization API key scoping [tests/unit/test_api.py:262-381]()
- Soft deletion [tests/unit/test_api.py:837-879]()
- Timeline pagination [tests/unit/test_api_persistent_agents.py:388-418]()

Run tests:
```bash
uv run python manage.py test tests.unit.test_api tests.unit.test_api_persistent_agents --settings=config.test_settings
```

Sources: [tests/unit/test_api.py:1-1053](), [tests/unit/test_api_persistent_agents.py:1-440]()

---

## Related Documentation

- [Authentication & Authorization](#9.2) - API key management and permission model
- [Agent Management](#4) - Agent lifecycle and configuration
- [Credit & Billing System](#5) - Credit consumption and quotas
- [Task Credits](#3.2) - How the credit system works

---

# Page: Authentication & Authorization

# Authentication & Authorization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [api/agent/core/event_processing.py](api/agent/core/event_processing.py)
- [api/exceptions.py](api/exceptions.py)
- [api/migrations/0145_browseruseagenttask_organization_and_more.py](api/migrations/0145_browseruseagenttask_organization_and_more.py)
- [api/models.py](api/models.py)
- [api/serializers.py](api/serializers.py)
- [api/services/persistent_agents.py](api/services/persistent_agents.py)
- [api/urls.py](api/urls.py)
- [api/views.py](api/views.py)
- [console/views.py](console/views.py)
- [tests/unit/test_api.py](tests/unit/test_api.py)
- [tests/unit/test_api_persistent_agents.py](tests/unit/test_api_persistent_agents.py)

</details>



This page documents the API authentication mechanism and authorization model for the gobii-platform. It covers API key-based authentication, the dual-ownership model (user vs organization), permission enforcement, and how these systems integrate with resource access control.

For information about user session management and web-based authentication, see [User Lifecycle & Authentication](#2.2). For credit-based resource gating, see [TaskCreditService](#5.1).

---

## Overview

The platform uses **API key authentication** for programmatic access to the REST API. API keys can be owned by individual users (personal keys) or by organizations (organization keys). Each resource in the system (agents, tasks, credits) is owned by either a user or an organization, enforced via database constraints. Authorization checks ensure that API keys can only access resources belonging to their owner.

---

## API Key Model

### Dual-Ownership Structure

API keys implement an **XOR ownership constraint**: each key belongs to exactly one owner—either a `user` or an `organization`, never both.

```mermaid
graph TB
    ApiKey["ApiKey Model"]
    User["User<br/>(settings.AUTH_USER_MODEL)"]
    Org["Organization"]
    
    ApiKey -->|"user_id<br/>(nullable)"| User
    ApiKey -->|"organization_id<br/>(nullable)"| Org
    
    Constraint["CheckConstraint:<br/>user XOR organization"]
    ApiKey -.->|"enforces"| Constraint
    
    ApiKey --> Fields["Fields:<br/>- id (UUID)<br/>- name (CharField)<br/>- prefix (8 chars)<br/>- hashed_key (SHA256)<br/>- raw_key (stored once)<br/>- created_at<br/>- revoked_at<br/>- created_by (FK User)"]
```

**Sources:** [api/models.py:122-276]()

### Key Limits

- **Personal Keys**: Maximum 50 per user (`MAX_API_KEYS_PER_USER`)
- **Organization Keys**: Maximum 50 per organization (`MAX_API_KEYS_PER_ORG`)

Limits are enforced in `ApiKey.clean()` validation method during creation.

**Sources:** [api/models.py:213-237]()

---

## Authentication Flow

### Request Authentication

Authentication occurs via the `X-API-KEY` HTTP header. The platform uses a custom authentication class that extracts the key, hashes it, and validates it against stored records.

```mermaid
sequenceDiagram
    participant Client
    participant DRF as "DRF Middleware"
    participant Auth as "ApiKeyAuthentication"
    participant DB as "Database"
    participant View as "ViewSet"
    
    Client->>DRF: "GET /api/v1/agents/<br/>X-API-KEY: {raw_key}"
    DRF->>Auth: authenticate(request)
    Auth->>Auth: "Extract X-API-KEY header"
    Auth->>Auth: "hash(raw_key) → hashed"
    Auth->>DB: "ApiKey.objects.filter(<br/>prefix=raw_key[:8],<br/>hashed_key=hashed,<br/>revoked_at=None)"
    
    alt Key Found & Valid
        DB-->>Auth: ApiKey instance
        Auth->>Auth: "api_key.last_used_at = now()"
        Auth->>DB: "api_key.save()"
        Auth-->>DRF: "(user, api_key)"
        DRF->>View: "request.user = user<br/>request.auth = api_key"
        View->>View: "Check permissions"
        View-->>Client: "200 OK + data"
    else Key Invalid/Revoked
        DB-->>Auth: "None"
        Auth-->>DRF: "None"
        DRF-->>Client: "401 Unauthorized"
    end
```

**Sources:** The authentication logic is implemented in a custom authentication class (not shown in provided files, but referenced in settings). The `ApiKey.matches()` method validates keys at [api/models.py:265-266]().

---

## Dual-Ownership Model

### Resource Ownership Architecture

All major resources implement dual ownership through nullable foreign keys with XOR constraints:

```mermaid
graph TB
    subgraph "Ownership Model"
        User["User"]
        Org["Organization"]
    end
    
    subgraph "API Keys"
        ApiKey["ApiKey<br/>(user XOR organization)"]
    end
    
    subgraph "Agent Resources"
        PA["PersistentAgent<br/>(user XOR organization)"]
        BUA["BrowserUseAgent<br/>(always user-owned)"]
    end
    
    subgraph "Execution Resources"
        Task["BrowserUseAgentTask<br/>(user XOR organization)"]
    end
    
    subgraph "Credits"
        TC["TaskCredit<br/>(user XOR organization)"]
    end
    
    User -->|"personal key"| ApiKey
    Org -->|"org key"| ApiKey
    
    User -->|"personal agent"| PA
    Org -->|"org agent"| PA
    
    User --> BUA
    PA -.->|"references"| BUA
    
    User --> Task
    Org --> Task
    
    User --> TC
    Org --> TC
```

**Sources:** [api/models.py:122-175]() (ApiKey), [api/models.py:290-387]() (TaskCredit), [api/models.py:618-636]() (BrowserUseAgentTask)

### Ownership Resolution Pattern

Views resolve ownership from the authenticated API key:

| Key Type | Ownership Source | Access Scope |
|----------|------------------|--------------|
| Personal (`user_id` set) | `request.user` | User-owned resources only |
| Organization (`organization_id` set) | `request.auth.organization` | Organization-owned resources only |

**Sources:** [api/views.py:100-104](), [api/views.py:198-202]()

---

## Permission Enforcement

### Organization Roles

Organization members have role-based permissions for managing organization resources:

| Role | API Key View | API Key Manage | Billing Access | Member Management |
|------|--------------|----------------|----------------|-------------------|
| `OWNER` | ✓ | ✓ | ✓ | ✓ |
| `ADMIN` | ✓ | ✓ | ✓ | ✓ |
| `BILLING` | ✓ | ✗ | ✓ | ✗ |
| `MEMBER` | ✗ | ✗ | ✗ | ✗ |

**Sources:** [console/views.py:128-146]()

### Resource Access Control

```mermaid
sequenceDiagram
    participant Client
    participant View as "BrowserUseAgentViewSet"
    participant Auth as "request.auth"
    participant DB as "Database"
    
    Client->>View: "GET /api/v1/agents/"
    View->>Auth: "_request_organization()"
    
    alt Organization Key
        Auth-->>View: "Organization instance"
        View->>DB: "BrowserUseAgent.objects.filter(<br/>persistent_agent__organization=org)"
        DB-->>View: "Org-owned agents"
    else Personal Key
        Auth-->>View: "None"
        View->>DB: "BrowserUseAgent.objects.filter(<br/>user=request.user)"
        DB-->>View: "User-owned agents"
    end
    
    View-->>Client: "Filtered results"
```

**Sources:** [api/views.py:106-129]()

### Validation in Serializers

Serializers enforce ownership during creation and updates:

```mermaid
graph TB
    Request["POST /api/v1/agents/<br/>{agent: agent_id}"]
    Serializer["BrowserUseAgentTaskSerializer"]
    Validate["validate(attrs)"]
    
    Request --> Serializer
    Serializer --> Validate
    
    Validate --> CheckKey{"request.auth<br/>type?"}
    
    CheckKey -->|"Organization Key"| OrgCheck{"agent.persistent_agent<br/>.organization_id<br/>== auth.organization_id?"}
    CheckKey -->|"Personal Key"| UserCheck{"agent.user<br/>== request.user?"}
    
    OrgCheck -->|"No"| Error["ValidationError:<br/>'agent does not belong<br/>to organization'"]
    UserCheck -->|"No"| Error
    
    OrgCheck -->|"Yes"| Success["Allow"]
    UserCheck -->|"Yes"| Success
```

**Sources:** [api/serializers.py:162-185]()

---

## API Key Management

### Console-Based Management

The console provides views for creating, listing, revoking, and deleting API keys. The `ApiKeyOwnerMixin` resolves context and enforces role-based permissions:

```mermaid
graph TB
    subgraph "Context Resolution"
        Request["HTTP Request"]
        Mixin["ApiKeyOwnerMixin"]
        Context["build_console_context()"]
        
        Request --> Mixin
        Mixin --> Context
    end
    
    Context --> Check{"current_context<br/>.type?"}
    
    Check -->|"organization"| OrgContext["Organization Context:<br/>- organization<br/>- membership<br/>- can_manage (role-based)"]
    Check -->|"personal"| UserContext["User Context:<br/>- user<br/>- can_manage (always true)"]
    
    OrgContext --> RoleCheck{"membership.role<br/>in API_KEY_MANAGE_ROLES?"}
    RoleCheck -->|"No"| Forbidden["PermissionDenied"]
    RoleCheck -->|"Yes"| Allowed["Allow"]
    
    UserContext --> Allowed
```

**Sources:** [console/views.py:149-181]()

### Key Generation

API keys use secure random generation:

1. **Raw Key**: 32-byte URL-safe token via `secrets.token_urlsafe(32)`
2. **Prefix**: First 8 characters (for quick lookup)
3. **Hashed Key**: SHA256 hash of raw key (stored for validation)
4. **Raw Key Storage**: Stored once on creation, then cleared or shown only once to user

**Sources:** [api/models.py:177-180](), [api/models.py:183-211]()

---

## API Restrictions by Key Type

### Organization Key Restrictions

Organization API keys have specific limitations to maintain separation between personal and organizational resources:

| Operation | Personal Key | Organization Key |
|-----------|--------------|------------------|
| Create `BrowserUseAgent` | ✓ | ✗ (raises `ValidationError`) |
| Create `PersistentAgent` | ✓ | ✓ |
| Create agentless `BrowserUseAgentTask` | ✓ (user-owned) | ✓ (org-owned) |
| List agents | User-owned only | Org-owned only |
| List tasks | User-owned only | Org-owned only |
| Access organization billing | If member | If OWNER/ADMIN/BILLING |

**Rationale**: `BrowserUseAgent` is always user-owned (legacy model), while `PersistentAgent` supports dual ownership. Organization keys cannot create browser agents directly but can create persistent agents, which provision browser agents internally.

**Sources:** [api/views.py:137-146](), [api/serializers.py:370-433]()

---

## Credit System Integration

### Owner-Aware Credit Operations

The `TaskCreditService` determines ownership from the agent's user or organization, then consumes credits from the appropriate owner:

```mermaid
graph TB
    AgentAction["Agent Executes Tool"]
    Determine["Determine Owner"]
    
    AgentAction --> Determine
    
    Determine --> Check{"agent.organization_id?"}
    
    Check -->|"Yes"| OrgCredits["TaskCreditService.check_and_consume_credit(<br/>organization=agent.organization,<br/>amount=cost)"]
    Check -->|"No"| UserCredits["TaskCreditService.check_and_consume_credit(<br/>user=agent.user,<br/>amount=cost)"]
    
    OrgCredits --> Query1["SELECT TaskCredit<br/>WHERE organization_id = ?<br/>AND available_credits >= cost<br/>FOR UPDATE"]
    
    UserCredits --> Query2["SELECT TaskCredit<br/>WHERE user_id = ?<br/>AND available_credits >= cost<br/>FOR UPDATE"]
    
    Query1 --> Consume["Atomic credit consumption"]
    Query2 --> Consume
    
    Consume --> LinkStep["Link to PersistentAgentStep"]
```

The service uses `SELECT FOR UPDATE` to ensure atomic credit consumption and prevent race conditions.

**Sources:** [tasks/services.py]() (service implementation, not directly shown but referenced), [api/agent/core/event_processing.py:510-711]() (credit gating in agent loop)

---

## Implementation Examples

### Console API Key Creation

When creating an API key from the console, the view resolves ownership from the active console context:

```python
# From ApiKeyListView.post()
ctx = self.api_key_context  # Resolved by ApiKeyOwnerMixin

if ctx["type"] == "organization":
    raw_key, api_key = ApiKey.create_for_org(
        ctx["organization"],
        created_by=self.request.user,
        name=name,
    )
else:
    raw_key, api_key = ApiKey.create_for_user(
        self.request.user,
        name=name,
        created_by=self.request.user,
    )
```

**Sources:** [console/views.py:685-705]()

### Task Creation with Organization Key

When creating a task via an organization API key, the task automatically inherits organization ownership:

```python
# From BrowserUseAgentTaskViewSet.perform_create()
org = self._request_organization()  # Returns org if auth is ApiKey with org

save_kwargs = {'agent': agent, 'user': self.request.user}
if org is not None:
    save_kwargs['organization'] = org
elif agent and hasattr(agent, 'persistent_agent') and agent.persistent_agent.organization:
    save_kwargs['organization'] = agent.persistent_agent.organization

task = serializer.save(**save_kwargs)
```

**Sources:** [api/views.py:328-334]()

### Queryset Filtering by Ownership

Views filter querysets based on the authenticated key's ownership:

```python
# From BrowserUseAgentTaskViewSet.get_queryset()
org = self._request_organization()
if org is not None:
    qs = qs.filter(
        models.Q(organization=org) |
        models.Q(agent__persistent_agent__organization=org)
    ).distinct()
else:
    qs = qs.filter(user=self.request.user, organization__isnull=True)
```

**Sources:** [api/views.py:241-250]()

---

## Database Constraints

### XOR Ownership Enforcement

All dual-ownership models enforce exactly-one-owner constraints at the database level:

```sql
-- ApiKey constraint
ALTER TABLE api_apikey
ADD CONSTRAINT api_key_exactly_one_owner
CHECK (
    (user_id IS NOT NULL AND organization_id IS NULL) OR
    (user_id IS NULL AND organization_id IS NOT NULL)
);

-- TaskCredit constraint  
ALTER TABLE api_taskcredit
ADD CONSTRAINT taskcredit_owner_xor_user_org
CHECK (
    (user_id IS NOT NULL AND organization_id IS NULL) OR
    (user_id IS NULL AND organization_id IS NOT NULL)
);
```

These constraints prevent orphaned resources and ambiguous ownership.

**Sources:** [api/models.py:168-175](), [api/models.py:375-385]()

---

## Testing

### Organization API Key Tests

The test suite includes comprehensive tests for organization key behavior:

```python
# Test: org key lists only org-owned agents
def test_org_key_lists_only_org_agents(self):
    self.client.credentials(HTTP_X_API_KEY=self.raw_org_key)
    response = self.client.get('/api/v1/agents/')
    
    names = {agent['name'] for agent in response.data['results']}
    self.assertIn(self.org_browser.name, names)
    self.assertNotIn(self.personal_browser.name, names)
```

**Sources:** [tests/unit/test_api.py:261-381]() (OrganizationApiKeyTests class)

---

## Summary

The authentication and authorization system implements:

1. **API Key Authentication**: SHA256-hashed keys with prefix-based lookup and last-used tracking
2. **Dual Ownership**: XOR constraints ensure resources belong to exactly one owner (user or organization)
3. **Role-Based Access**: Organization members have differentiated permissions based on role
4. **Queryset Filtering**: Views automatically scope queries to the authenticated key's owner
5. **Serializer Validation**: Ownership checks prevent cross-owner access during creation and updates
6. **Database Integrity**: Constraints enforce ownership rules at the data layer

This architecture enables the platform to serve both individual users and multi-member organizations while maintaining strict access control and resource isolation.

---

# Page: Development & Administration

# Development & Administration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [api/admin.py](api/admin.py)
- [api/agent/peer_comm.py](api/agent/peer_comm.py)
- [api/agent/peer_link_signals.py](api/agent/peer_link_signals.py)
- [api/agent/tools/peer_dm.py](api/agent/tools/peer_dm.py)
- [api/apps.py](api/apps.py)
- [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py](api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py)
- [config/settings.py](config/settings.py)
- [tests/unit/test_agent_short_description.py](tests/unit/test_agent_short_description.py)
- [tests/unit/test_peer_agent_messaging.py](tests/unit/test_peer_agent_messaging.py)
- [util/subscription_helper.py](util/subscription_helper.py)

</details>



This document covers development tools, administrative interfaces, and operational infrastructure for the gobii-platform. It includes Django admin customizations, testing methodology, CI/CD pipelines, and configuration management for both community and proprietary deployment modes.

For platform architecture and core concepts, see [Platform Overview](#1). For deployment configuration details, see [Configuration & Deployment](#2.1).

---

## Configuration Management

### Settings Architecture

The platform uses a layered configuration system centered on [config/settings.py:1-937](), with a distinction between **Community Edition** (open-source, minimal dependencies) and **Proprietary Mode** (licensed deployment with full external integrations).

**Key Configuration Constructs:**

| Setting | Purpose | Default (Community) | Default (Proprietary) |
|---------|---------|---------------------|----------------------|
| `GOBII_PROPRIETARY_MODE` | Enables proprietary features | `False` | `True` |
| `GOBII_ENABLE_COMMUNITY_UNLIMITED` | Removes agent/task limits | `True` | `False` |
| `TURNSTILE_ENABLED` | Cloudflare bot protection | `False` | `True` |
| `ACCOUNT_EMAIL_VERIFICATION` | Email verification requirement | `"none"` | `"mandatory"` |
| `STRIPE_ENABLED` | Billing integration | `False` | `True` (if keys present) |

The configuration system uses `django-environ` to parse `.env` files and applies smart defaults for local development [config/settings.py:36-54]():

```python
if RELEASE_ENV == "local" and not IN_DOCKER:
    os.environ.setdefault("DEBUG", "1")
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
```

### Proprietary Defaults System

Proprietary-specific defaults are loaded from a separate `proprietary` package [config/settings.py:75-98](). This allows clean separation of licensed configuration while maintaining a functional community build:

```mermaid
graph LR
    Settings["config/settings.py"] --> CheckMode{"GOBII_PROPRIETARY_MODE?"}
    CheckMode -->|True| LoadProp["proprietary.defaults"]
    CheckMode -->|False| Community["_COMMUNITY_DEFAULTS"]
    
    LoadProp --> Getter["_proprietary_default()"]
    Community --> CommunityGetter["_community_default()"]
    
    Getter --> Branding["Brand URLs<br/>Support Emails"]
    Getter --> Analytics["Segment Keys<br/>Pixel IDs"]
    Getter --> Stripe["Stripe Product IDs"]
    
    CommunityGetter --> OSS["Public Discord<br/>GitHub URLs"]
```

**Sources:** [config/settings.py:75-108]()

### Environment Variable Categories

The platform organizes environment variables into functional groups:

1. **Core Django Settings** [config/settings.py:111-186]()
   - `DJANGO_SECRET_KEY`: Session encryption
   - `DEBUG`: Development mode toggle
   - `CSRF_TRUSTED_ORIGINS`: Security whitelist
   - `PUBLIC_BRAND_NAME`: Deployment branding

2. **Database & Cache** [config/settings.py:288-316]()
   - `POSTGRES_*`: Database connection parameters
   - `REDIS_URL`: Cache and message broker
   - `CONN_MAX_AGE`: Connection pooling (default: 600s)

3. **Celery Task Queue** [config/settings.py:561-601]()
   - `CELERY_BROKER_URL`: Task broker
   - `CELERY_TASK_TIME_LIMIT`: Hard timeout (14400s/4 hours)
   - `CELERY_BEAT_SCHEDULER`: RedBeat for distributed scheduling

4. **External Integrations** [config/settings.py:686-927]()
   - `MAILGUN_API_KEY`, `POSTMARK_SERVER_TOKEN`: Email delivery
   - `TWILIO_*`: SMS provisioning
   - `PIPEDREAM_*`: MCP remote tool servers
   - `STRIPE_*`: Billing and subscriptions

**Sources:** [config/settings.py:1-937]()

---

## Django Admin Interface

### Custom Admin Architecture

The platform extensively customizes Django's admin interface to provide operational tools beyond standard CRUD. The admin system is organized into domain-specific admin classes with specialized actions and views.

```mermaid
graph TB
    BaseAdmin["django.contrib.admin.ModelAdmin"] --> Custom["Custom Admin Classes"]
    
    Custom --> Credits["TaskCreditAdmin"]
    Custom --> Agents["BrowserUseAgentAdmin<br/>PersistentAgentAdmin"]
    Custom --> Billing["UserBilling/OrgBillingAdmin"]
    Custom --> Infra["ProxyServerAdmin<br/>DecodoIPAdmin"]
    
    Credits --> Actions1["Bulk Actions"]
    Credits --> CustomViews["Custom Views"]
    
    Actions1 --> GrantPlan["grant_by_plan_view<br/>CSV export"]
    Actions1 --> GrantIDs["grant_by_user_ids_view<br/>Dry-run mode"]
    
    CustomViews --> HealthCheck["Proxy Health Checks"]
    CustomViews --> Simulation["Agent Simulation"]
    
    Agents --> InlineAdmin["Inline Admins"]
    InlineAdmin --> TaskInline["BrowserUseAgentTaskInline<br/>MAX_DISPLAY=50"]
    InlineAdmin --> StepInline["BrowserUseAgentTaskStepInline<br/>MAX_DISPLAY=50"]
```

**Sources:** [api/admin.py:1-2687]()

### Bulk Credit Granting

The `TaskCreditAdmin` provides two custom views for bulk credit operations:

#### Grant by Plan

Located at `/admin/api/taskcredit/grant-by-plan/`, this view grants credits to all users on a specific subscription plan [api/admin.py:263-389]():

**Form Parameters:**
- `plan`: Target plan (Free, Startup, Team, etc.)
- `credits`: Amount to grant
- `grant_type`: Classification (PLAN, PROMOTIONAL, etc.)
- `expiration_date`: When credits expire
- `only_if_out_of_credits`: Filter to users with zero available credits
- `dry_run`: Preview mode without database changes
- `export_csv`: Download affected user list

**Implementation Detail:** The system iterates active users, calls `get_user_plan()` for each, and matches against the target plan [api/admin.py:299-309](). When `only_if_out_of_credits=True`, a subquery aggregates available credits and filters to users with `SUM(available_credits) <= 0` [api/admin.py:311-337]().

#### Grant by User IDs

Located at `/admin/api/taskcredit/grant-by-user-ids/`, accepts comma or newline-separated user IDs [api/admin.py:391-512]():

```python
# Parse input: "123,456\n789" -> [123, 456, 789]
ids = [s for s in re.split(r"[\s,]+", raw.strip()) if s]
users = list(User.objects.filter(id__in=ids, is_active=True))
```

Both views support dry-run CSV export for audit trails before executing bulk operations.

**Sources:** [api/admin.py:245-512]()

### Proxy Management Actions

The `ProxyServerAdmin` and `DecodoIPAdmin` classes expose operational actions for proxy infrastructure:

```mermaid
graph LR
    ProxyAdmin["ProxyServerAdmin"] --> Action1["health_check_single"]
    ProxyAdmin --> Action2["bulk_health_check"]
    
    DecodoAdmin["DecodoIPAdmin"] --> Action3["sync_ip_block"]
    DecodoAdmin --> Action4["backfill_proxies"]
    
    Action1 --> Task1["proxy_health_check_single.delay"]
    Action2 --> Task2["Enqueue per-proxy tasks"]
    Action3 --> Task3["sync_ip_block.delay"]
    Action4 --> Task4["backfill_missing_proxy_records.delay"]
    
    Task1 --> Result["Health check results<br/>stored in ProxyHealthCheckResult"]
    Task3 --> IPList["Fetches IP list from Decodo API<br/>creates DecodoIP records"]
```

These actions trigger Celery tasks and provide admin feedback via Django messages [api/admin.py:1583-1648]().

**Sources:** [api/admin.py:1465-1648](), [api/tasks.py:various]()

### Inline Admin Optimizations

To avoid performance issues when displaying related objects, the platform limits inline admins with custom `get_queryset()` methods:

**BrowserUseAgentTaskInline** [api/admin.py:599-656]():
- Displays the 50 most recent tasks per agent
- Extracts `object_id` from URL to filter tasks
- Returns unsliced queryset filtered by PK list (Django admin requirement)

```python
def get_queryset(self, request):
    qs = super().get_queryset(request)
    object_id = request.resolver_match.kwargs.get("object_id")
    if not object_id:
        return qs.none()
    qs = qs.filter(agent__pk=object_id).order_by('-created_at')
    recent_pks = list(qs.values_list('pk', flat=True)[:self.MAX_DISPLAY])
    return self.model.objects.filter(pk__in=recent_pks).order_by('-created_at')
```

This pattern prevents Django from attempting to render thousands of inline rows, which can cause browser crashes.

**Sources:** [api/admin.py:599-774]()

### Custom Admin Forms

**StripeConfigAdmin** [api/admin.py:99-148]() uses a custom form to handle encrypted secrets:

- `webhook_secret`: Write-only field with encryption via `set_value()`
- `clear_webhook_secret`: Checkbox to delete stored secret
- `webhook_secret_status`: Read-only display of encryption status

**AgentEmailAccountForm** [api/admin_forms.py:various]() provides OAuth flow initiation for agent email configuration.

**Sources:** [api/admin.py:99-148](), [api/admin_forms.py:1-198]()

---

## Testing Infrastructure

### Tag-Based Test Organization

The platform uses Django's test tagging system to organize tests into parallelizable batches. Each test class/method is decorated with a `@tag()` marker:

```python
@tag("batch_peer_dm")
class PeerMessagingServiceTests(TestCase):
    # Tests for peer messaging
```

All tests **must** be tagged, enforced by a pre-test guard script [.github/workflows/ci.yml:20-34]():

```yaml
- name: Verify all tests are tagged and tags are in CI
  run: python3 scripts/check_test_tags.py
```

This script parses all test files, extracts tags, and ensures:
1. Every test has at least one tag
2. Every tag referenced in tests appears in the CI workflow matrix

**Benefits:**
- **Parallelization:** Each batch runs in a separate CI job
- **Isolation:** Batch failures don't block unrelated tests
- **Debuggability:** Failed tests can be re-run by tag locally
- **Consistency:** Tag guard prevents untagged/orphaned tests

**Sources:** [.github/workflows/ci.yml:20-34](), test files with `@tag()` decorators

### Test Batching Strategy

The CI workflow defines 66+ test batches in a matrix [.github/workflows/ci.yml:44-194]():

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - batch: email
        tag: batch_email
      - batch: peer_dm
        tag: batch_peer_dm
      - batch: agent_lifecycle
        tag: batch_agent_lifecycle
      # ... 60+ more batches
```

**Batch Design Principles:**
1. **Functional isolation:** Each batch covers a cohesive feature area
2. **Runtime balance:** Batches target ~2-5 minute execution time
3. **Dependency grouping:** Related tests run together (e.g., all email tests)
4. **Smoke test separation:** Core path tests in dedicated batches

### Test Settings

Tests use a separate settings module [.github/workflows/ci.yml:197]():

```yaml
env:
  DJANGO_SETTINGS_MODULE: config.test_settings
```

**Key Test Overrides:**
- Database: SQLite in-memory for speed
- Redis: Fakeredis for zero infrastructure
- Celery: `CELERY_TASK_ALWAYS_EAGER=True` for synchronous execution
- LLM: Mock providers to avoid external API calls
- Email: Console backend for no-op delivery

**Satisfying Settings Import:** Because `manage.py` imports `config.settings` before Django loads test settings, CI must provide all required environment variables [.github/workflows/ci.yml:202-214]():

```yaml
DJANGO_SECRET_KEY: test-secret
POSTGRES_DB: test  # Not used, but settings.py requires it
REDIS_URL: redis://localhost:6379/0
OPENAI_API_KEY: dummy  # Satisfies LLM fail-fast check
```

**Sources:** [.github/workflows/ci.yml:195-216]()

### Running Tests Locally

**Run a specific batch:**
```bash
python manage.py test --tag batch_peer_dm --settings=config.test_settings
```

**Run with XML output for debugging:**
```bash
python manage.py test --tag batch_email \
  --settings=config.test_settings \
  --testrunner=xmlrunner.extra.djangotestrunner.XMLTestRunner
```

**Run all untagged tests (finds missing tags):**
```bash
python manage.py test --exclude-tag batch_* --settings=config.test_settings
```

**Sources:** [.github/workflows/ci.yml:264-276]()

---

## CI/CD Pipeline

### GitHub Actions Workflow

The platform uses a single workflow file [.github/workflows/ci.yml:1-308]() with multiple jobs:

```mermaid
graph TB
    Trigger["Push/PR Event"] --> TagGuard["Job: tag-guard<br/>check_test_tags.py"]
    
    TagGuard -->|Pass| TestMatrix["Job: tests<br/>Matrix: 66 batches"]
    TagGuard -->|Fail| Block["Block PR"]
    
    TestMatrix --> Batch1["Batch: email<br/>tag: batch_email"]
    TestMatrix --> Batch2["Batch: peer_dm<br/>tag: batch_peer_dm"]
    TestMatrix --> BatchN["Batch: ...<br/>66 total batches"]
    
    Batch1 --> Artifacts1["Upload test-results-email"]
    Batch2 --> Artifacts2["Upload test-results-peer_dm"]
    BatchN --> ArtifactsN["Upload test-results-*"]
    
    Artifacts1 --> Report["Job: report<br/>Merge all artifacts"]
    Artifacts2 --> Report
    ArtifactsN --> Report
    
    Report --> Publish["Publish Combined<br/>Test Results<br/>EnricoMi/publish-unit-test-result-action"]
```

**Sources:** [.github/workflows/ci.yml:1-308]()

### Dependency Caching

The workflow uses multiple cache layers to optimize build time:

#### UV Cache

The `setup-uv` action provides automatic caching for the UV package manager [.github/workflows/ci.yml:226-230]():

```yaml
- name: Set up uv (with cache)
  uses: astral-sh/setup-uv@v6
  with:
    enable-cache: true
    ignore-nothing-to-cache: true
```

#### Venv Cache

A separate cache stores the Python virtual environment [.github/workflows/ci.yml:232-262]():

```yaml
- name: Restore venv cache
  id: restore-venv
  uses: actions/cache/restore@v4
  with:
    path: .venv
    key: venv-${{ runner.os }}-py3.12-${{ hashFiles('uv.lock') }}
    restore-keys: |
      venv-${{ runner.os }}-py3.12-
```

**Cache Strategy:**
1. Restore cached venv if `uv.lock` matches
2. Run `uv sync --frozen` to install dependencies
3. Save updated venv for future runs (if cache miss)

This reduces dependency installation from ~2 minutes to ~10 seconds on cache hits.

**Sources:** [.github/workflows/ci.yml:226-262]()

### Test Execution

Each batch job runs tests with specific tags [.github/workflows/ci.yml:264-276]():

```bash
uv run python manage.py test --tag "$TAG" \
  --settings=config.test_settings \
  --parallel 1 \
  --testrunner=xmlrunner.extra.djangotestrunner.XMLTestRunner
```

**Parallelization:** `--parallel 1` disables Django's built-in parallelization because parallelism occurs at the batch level (66 concurrent CI jobs).

**XML Output:** The `xmlrunner` generates JUnit XML files for each batch, uploaded as artifacts [.github/workflows/ci.yml:278-286]():

```yaml
- name: Upload test results artifact
  if: always()  # Upload even if tests fail
  uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ matrix.batch }}
    path: test-results/**
    retention-days: 7
```

**Sources:** [.github/workflows/ci.yml:264-286]()

### Combined Test Reporting

The `report` job runs after all batches complete (`needs: [tests]`) and aggregates results [.github/workflows/ci.yml:289-307]():

```yaml
- name: Download all test result artifacts
  uses: actions/download-artifact@v4
  with:
    pattern: test-results-*
    merge-multiple: true
    path: all-results

- name: Publish combined test results
  uses: EnricoMi/publish-unit-test-result-action@v2
  with:
    files: all-results/**/*.xml
    check_name: "Combined Test Results"
    comment_mode: off  # Reduce PR noise
```

This creates a single "Combined Test Results" check on PRs showing overall pass/fail status and detailed failure reports.

**Sources:** [.github/workflows/ci.yml:289-307]()

### Concurrency Control

The workflow includes auto-cancellation of outdated runs [.github/workflows/ci.yml:9-11]():

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

This ensures that pushing a new commit to a PR immediately cancels the previous CI run, saving compute resources and reducing feedback latency.

**Sources:** [.github/workflows/ci.yml:8-11]()

---

## Development Workflows

### Local Development Setup

**Prerequisites:**
1. Python 3.12+
2. PostgreSQL (or use Docker Compose)
3. Redis (or use Docker Compose)
4. UV package manager (`pip install uv`)

**Bootstrap Steps:**

```bash
# Clone repository
git clone https://github.com/gobii-ai/gobii-platform.git
cd gobii-platform

# Install dependencies
uv sync --all-extras --dev

# Create local environment file
cp infra/platform/local/.env.example infra/platform/local/.env
# Edit .env to add API keys (OPENAI_API_KEY, etc.)

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Start services
uv run python manage.py runserver  # Django
uv run celery -A config worker -l info  # Celery worker
uv run celery -A config beat -l info  # Celery beat
```

**LLM Bootstrap Requirement:** The platform enforces at least one LLM provider key on startup [config/settings.py:73](). Set `LLM_BOOTSTRAP_OPTIONAL=1` to bypass in non-interactive environments.

**Sources:** [config/settings.py:36-73]()

### Admin Access Patterns

Common admin workflows:

**Grant credits to specific users:**
1. Navigate to `/admin/api/taskcredit/grant-by-user-ids/`
2. Paste user IDs (comma or newline separated)
3. Set credit amount and expiration
4. Enable "Dry run" + "Export CSV" to preview
5. Submit to execute

**Check proxy health:**
1. Navigate to `/admin/api/proxyserver/`
2. Select proxies
3. Choose "Run health check on selected proxies"
4. View results in `/admin/api/proxyhealthcheckresult/`

**Simulate agent execution:**
1. Navigate to agent detail page in admin
2. Click "Simulate Agent" custom action
3. Review generated steps in test mode

**Sources:** [api/admin.py:various]()

### Test Development Guidelines

**When adding new tests:**

1. **Tag immediately:** Add `@tag("batch_<feature>")` decorator
2. **Choose/create batch:** Group related tests under same tag
3. **Update CI matrix:** Add batch to [.github/workflows/ci.yml:44-194]() if new
4. **Run tag guard:** `python3 scripts/check_test_tags.py` before committing

**Example:**

```python
from django.test import TestCase, tag

@tag("batch_new_feature")
class NewFeatureTests(TestCase):
    def test_something(self):
        # Test implementation
```

**Then update CI:**
```yaml
- batch: new_feature
  tag: batch_new_feature
```

**Sources:** [.github/workflows/ci.yml:20-34](), test files

---

## Configuration Reference

### Critical Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DJANGO_SECRET_KEY` | Yes | `"dev-insecure"` (local) | Session encryption |
| `GOBII_ENCRYPTION_KEY` | Yes | `"dev-insecure"` (local) | Field-level encryption |
| `POSTGRES_*` | Yes | `localhost:5432/gobii` | Database connection |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Cache and broker |
| `OPENAI_API_KEY` | Yes* | None | LLM provider (*or other LLM key) |
| `GOBII_PROPRIETARY_MODE` | No | `False` | Feature mode toggle |
| `STRIPE_LIVE_SECRET_KEY` | No* | None | Billing (*if STRIPE_ENABLED) |
| `MAILGUN_API_KEY` | No* | None | Email delivery (*if proprietary) |

### Feature Flags

The platform uses Waffle for runtime feature flags managed via admin:

- **Storage:** Database-backed (`waffle_flag` table)
- **Default behavior:** `WAFFLE_FLAG_DEFAULT=False` (explicit management required)
- **Admin URL:** `/admin/waffle/flag/`

**Usage in code:**
```python
from waffle import flag_is_active

if flag_is_active(request, 'new_feature'):
    # Feature-gated logic
```

**Sources:** [config/settings.py:617-620]()

### Deployment Modes

The `GOBII_RELEASE_ENV` variable controls environment-specific behavior:

- `"local"`: Development mode, smart defaults, debug enabled
- `"preview"`: Staging environment with production-like config
- `"prod"`: Production mode, strict security, external services required

**Sources:** [config/settings.py:29-36]()

---

## Troubleshooting

### Common Development Issues

**Issue: "LLM bootstrap check failed"**
- **Cause:** No LLM API keys configured
- **Fix:** Set at least one of `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GLM_API_KEY` in `.env`
- **Bypass:** Set `LLM_BOOTSTRAP_OPTIONAL=1` for tests

**Issue: "Database connection refused"**
- **Cause:** PostgreSQL not running or wrong host
- **Fix:** Start PostgreSQL locally or adjust `POSTGRES_HOST` in `.env`
- **Alternative:** Use Docker Compose: `docker-compose up -d db redis`

**Issue: "Celery worker not processing tasks"**
- **Cause:** Redis connection failure or worker not started
- **Fix:** Verify `REDIS_URL` and run `celery -A config worker`

**Issue: "Tests fail with 'Tag not in CI matrix'"**
- **Cause:** Tag guard detected missing batch
- **Fix:** Add batch to [.github/workflows/ci.yml:44-194]() matrix

**Sources:** Various configuration and troubleshooting patterns

### Admin Performance Issues

**Symptom:** Admin page times out loading agent with many tasks

**Cause:** Inline admin rendering too many related objects

**Fix:** The platform limits inlines to 50 records [api/admin.py:607](). If still slow, the query optimization may need adjustment. Check `list_select_related` and `get_queryset()` overrides.

**Symptom:** Bulk credit grant hangs

**Cause:** Iterating too many users without batch processing

**Fix:** Use "Dry run" mode with CSV export to identify scale, then batch manually or increase timeout.

**Sources:** [api/admin.py:599-774]()

---

# Page: Django Admin Interface

# Django Admin Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [api/admin.py](api/admin.py)
- [config/settings.py](config/settings.py)
- [util/subscription_helper.py](util/subscription_helper.py)

</details>



## Purpose and Scope

This page documents the custom Django admin interface implementation in gobii-platform. The admin interface provides operational tools for managing agents, credits, billing, proxies, and user data. For information about REST API endpoints, see [9.1](#9.1). For automated testing of admin functionality, see [10.2](#10.2).

The admin interface extends Django's default admin with:
- **Bulk credit granting** workflows for subscription provisioning
- **Agent simulation tools** for testing email and SMS integrations
- **Proxy health monitoring** and synchronization controls
- **Custom performance optimizations** to handle large datasets efficiently

---

## Admin Architecture Overview

The admin interface is registered in Django's standard admin site and consists of custom `ModelAdmin` subclasses that provide enhanced functionality beyond basic CRUD operations.

```mermaid
graph TB
    AdminSite["django.contrib.admin.site"]
    
    subgraph "Credit & Billing Admins"
        TaskCreditAdmin["TaskCreditAdmin"]
        TaskCreditConfigAdmin["TaskCreditConfigAdmin"]
        ToolCreditCostAdmin["ToolCreditCostAdmin"]
        MeteringBatchAdmin["MeteringBatchAdmin"]
        StripeConfigAdmin["StripeConfigAdmin"]
    end
    
    subgraph "Agent Admins"
        BrowserUseAgentAdmin["BrowserUseAgentAdmin"]
        BrowserUseAgentTaskAdmin["BrowserUseAgentTaskAdmin"]
        PersistentAgentAdmin["PersistentAgentAdmin"]
    end
    
    subgraph "Communication Admins"
        PersistentAgentCommsEndpointAdmin["PersistentAgentCommsEndpointAdmin"]
        AgentEmailAccountAdmin["AgentEmailAccountAdmin"]
        SmsNumberAdmin["SmsNumberAdmin"]
    end
    
    subgraph "Proxy Admins"
        DecodoCredentialAdmin["DecodoCredentialAdmin"]
        DecodoIPBlockAdmin["DecodoIPBlockAdmin"]
        ProxyServerAdmin["ProxyServerAdmin"]
        ProxyHealthCheckResultAdmin["ProxyHealthCheckResultAdmin"]
    end
    
    subgraph "User Admins"
        CustomUserAdmin["CustomUserAdmin"]
        OrganizationAdmin["OrganizationAdmin"]
        UserBillingAdmin["UserBillingAdmin"]
    end
    
    AdminSite --> TaskCreditAdmin
    AdminSite --> BrowserUseAgentAdmin
    AdminSite --> PersistentAgentAdmin
    AdminSite --> DecodoIPBlockAdmin
    AdminSite --> ProxyServerAdmin
    AdminSite --> CustomUserAdmin
```

**Sources:** [api/admin.py:1-2456]()

---

## Credit and Billing Admins

### TaskCreditAdmin

`TaskCreditAdmin` manages `TaskCredit` records and provides bulk credit granting workflows. This is one of the most heavily customized admins in the platform.

**Key Features:**
- **Custom list filters:** `OwnershipTypeFilter` (user vs org), plan type, expiration date
- **Performance optimization:** Uses `list_select_related` to prefetch `user` and `organization` in a single query
- **Annotated search:** Supports searching by numeric user IDs via custom `get_search_results()`
- **Custom change list template:** `admin/taskcredit_change_list.html` adds navigation buttons

**Custom URLs and Views:**

| URL Pattern | View Method | Purpose |
|------------|-------------|---------|
| `grant-by-plan/` | `grant_by_plan_view()` | Grant credits to all users on a specific plan |
| `grant-by-user-ids/` | `grant_by_user_ids_view()` | Grant credits to a comma/newline-separated list of user IDs |

```mermaid
flowchart TD
    Start["Admin clicks 'Grant by Plan' button"]
    Form["Render GrantPlanCreditsForm"]
    
    Start --> Form
    Form --> Submit{Form Valid?}
    
    Submit -->|No| Form
    Submit -->|Yes| FilterUsers["Filter User.objects.filter(is_active=True)"]
    
    FilterUsers --> MatchPlan["For each user: get_user_plan(user)"]
    MatchPlan --> PlanMatch{Plan matches?}
    
    PlanMatch -->|No| Skip["Skip user"]
    PlanMatch -->|Yes| CheckZero{only_if_out_of_credits?}
    
    CheckZero -->|Yes| QueryCredits["Check available credits"]
    CheckZero -->|No| Include["Include user"]
    
    QueryCredits --> HasCredits{Has credits > 0?}
    HasCredits -->|Yes| Skip
    HasCredits -->|No| Include
    
    Include --> DryRun{dry_run?}
    DryRun -->|Yes & export_csv| ExportCSV["Generate CSV with user IDs, emails, plan, credits"]
    DryRun -->|Yes & no CSV| ShowMessage["Display 'would grant to N users'"]
    DryRun -->|No| CreateRecords["TaskCredit.objects.create() for each user"]
    
    CreateRecords --> Success["Redirect to changelist with success message"]
    ExportCSV --> Download["HTTP response with CSV file"]
    ShowMessage --> Form
```

The grant-by-plan workflow iterates over active users and calls `get_user_plan()` from `util.subscription_helper` to match the target plan. When `only_if_out_of_credits` is enabled, it annotates users with `available_credits_sum` via a database aggregation to filter out users who still have unused credits.

**Sources:** [api/admin.py:188-513](), [api/admin_forms.py:1-100](), [util/subscription_helper.py:196-198]()

---

### TaskCreditConfigAdmin and ToolCreditCostAdmin

These admins manage the database-backed credit configuration introduced to replace hardcoded constants.

**TaskCreditConfigAdmin:**
- Enforces singleton pattern (only one config record allowed)
- Manages `default_task_cost` (the baseline credit cost per task)
- Prevents deletion via `has_delete_permission() -> False`

**ToolCreditCostAdmin:**
- Manages per-tool credit overrides (e.g., `sqlite_batch` costs 0.8 credits)
- Searchable by tool name
- Lists credit cost and last update timestamp

```mermaid
erDiagram
    TaskCreditConfig {
        int singleton_id PK
        decimal default_task_cost
        datetime created_at
        datetime updated_at
    }
    
    ToolCreditCost {
        uuid id PK
        string tool_name
        decimal credit_cost
        datetime created_at
        datetime updated_at
    }
    
    PersistentAgentStep {
        uuid id PK
        string tool_name
        decimal credits_cost
    }
    
    ToolCreditCost ||--o{ PersistentAgentStep : "overrides cost for"
```

When an agent executes a tool, the system queries `ToolCreditCost` by tool name (case-insensitive) and falls back to `TaskCreditConfig.default_task_cost` if no override exists.

**Sources:** [api/admin.py:515-543](), [api/models.py:1-50]()

---

### MeteringBatchAdmin

`MeteringBatchAdmin` provides read-only inspection of Stripe metering batches, which aggregate additional-task credits reported to Stripe for billing.

**Key Display Fields:**
- `batch_key`: Unique identifier (user/org ID + period start/end)
- `rounded_quantity`: Number of overage tasks reported
- `total_credits`: Sum of credits consumed in the batch
- `stripe_event_id`: Stripe meter event ID for tracking

**Custom Links:**
The `usage_links()` display method generates clickable links to related `BrowserUseAgentTask` and `PersistentAgentStep` records filtered by `meter_batch_key`, allowing operators to drill down into which tasks contributed to a metering event.

**Sources:** [api/admin.py:545-589]()

---

## Agent Management Admins

### BrowserUseAgentAdmin

`BrowserUseAgentAdmin` manages `BrowserUseAgent` records, which represent the browser automation layer backing persistent agents.

**Performance Optimization:**
- Uses `get_queryset()` with `.select_related('user')` and `.annotate(num_tasks=Count('tasks'))` to avoid N+1 queries when displaying the agent list
- The annotated `num_tasks` is accessed via `getattr(obj, 'num_tasks', None)` in display methods

**Inline Display:**
The `BrowserUseAgentTaskInline` inline limits displayed tasks to the 50 most recent to prevent browser lockups when agents have thousands of tasks. This is implemented via a custom `get_queryset()` that extracts `object_id` from the URL resolver and filters/slices the queryset.

```mermaid
sequenceDiagram
    participant Admin as Admin User
    participant View as BrowserUseAgentAdmin Change View
    participant Inline as BrowserUseAgentTaskInline
    participant DB as Database
    
    Admin->>View: GET /admin/api/browseruseagent/{id}/change/
    View->>DB: SELECT * FROM browser_use_agent WHERE id = {id}
    View->>Inline: get_queryset(request)
    Inline->>Inline: Extract object_id from request.resolver_match.kwargs
    Inline->>DB: SELECT pk FROM tasks WHERE agent_id = {object_id} ORDER BY created_at DESC LIMIT 50
    Inline->>DB: SELECT * FROM tasks WHERE pk IN (...)
    Inline-->>View: Return limited queryset
    View-->>Admin: Render change form with 50 most recent tasks
```

**Sources:** [api/admin.py:672-737](), [api/admin.py:599-657]()

---

### BrowserUseAgentTaskAdmin

`BrowserUseAgentTaskAdmin` manages `BrowserUseAgentTask` records with custom garbage collection and step inspection.

**Custom Action: Run Garbage Collection**

The admin changelist template includes a button that queues the `garbage_collect_timed_out_tasks` Celery task. This task identifies tasks stuck in `PROCESSING` status for more than the configured timeout and transitions them to `TIMEOUT` status.

| Component | Implementation |
|-----------|---------------|
| Template | `admin/browseruseagenttask_change_list.html` |
| URL | `run-gc/` → `run_gc_view()` |
| Task | `garbage_collect_timed_out_tasks.delay()` |
| Logic | Defined in `api/tasks.py` |

**Inline Steps:**
`BrowserUseAgentTaskStepInline` displays up to 50 most recent steps per task, using the same limiting pattern as the agent-task inline.

**Sources:** [api/admin.py:803-887](), [api/admin.py:738-802](), [api/tasks.py:1-100]()

---

### PersistentAgentAdmin

`PersistentAgentAdmin` is the most feature-rich admin, providing agent simulation, message inspection, and event processing triggers.

**Custom Inlines:**

| Inline Class | Model | Purpose |
|-------------|-------|---------|
| `PersistentAgentCommsEndpointInline` | `PersistentAgentCommsEndpoint` | Email/SMS addresses |
| `CommsAllowlistEntryInline` | `CommsAllowlistEntry` | Manual allowlist entries |
| `AgentMessageInline` | `PersistentAgentMessage` | Conversation history (50 most recent) |

**Agent Simulation Tools:**

```mermaid
graph LR
    Admin["Admin User"]
    AgentDetail["Agent Change Form"]
    SimEmail["simulate_email_view()"]
    SimSMS["simulate_sms_view()"]
    
    Admin --> AgentDetail
    AgentDetail -->|"Click 'Simulate Email'"| SimEmail
    AgentDetail -->|"Click 'Simulate SMS'"| SimSMS
    
    SimEmail --> ParsedMessage["Create ParsedMessage object"]
    SimSMS --> ParsedMessage
    
    ParsedMessage --> Ingest["ingest_inbound_message()"]
    Ingest --> DB["Save PersistentAgentMessage"]
    DB --> Queue["process_agent_events_task.delay()"]
```

The simulation views create `ParsedMessage` objects and pass them through the same `ingest_inbound_message()` pipeline used by webhooks, ensuring agents react identically to simulated and real messages. This allows testing email/SMS flows without external dependencies.

**Event Processing Trigger:**

The changelist includes a "Trigger Event Processing" button that renders a form accepting newline-separated agent UUIDs. When submitted, it validates each ID and queues `process_agent_events_task.delay(agent_id)` for existing agents.

**Sources:** [api/admin.py:1545-1935](), [api/agent/comms/message_service.py:1-200](), [api/agent/tasks.py:1-100]()

---

## Proxy and Infrastructure Admins

### DecodoIPBlockAdmin

`DecodoIPBlockAdmin` manages `DecodoIPBlock` records, which represent blocks of residential proxy IPs from Decodo.

**Custom Action: Sync IP Block**

Each IP block has a "Sync Now" button that queues the `sync_ip_block.delay(block_id)` Celery task. This task:
1. Calls the Decodo API to fetch updated IP metadata
2. Creates or updates `DecodoIP` records
3. Populates geolocation and ISP information

```mermaid
flowchart TD
    AdminClick["Admin clicks 'Sync Now' button"]
    View["sync_view(request, object_id)"]
    Verify["Verify DecodoIPBlock.objects.get(pk=object_id)"]
    Queue["sync_ip_block.delay(str(ip_block.id))"]
    
    AdminClick --> View
    View --> Verify
    Verify -->|Exists| Queue
    Verify -->|DoesNotExist| Error["Show error message"]
    
    Queue --> Task["Celery Worker: sync_ip_block"]
    Task --> API["Call Decodo API"]
    API --> Parse["Parse IP list"]
    Parse --> Upsert["Update or create DecodoIP records"]
    Upsert --> Complete["Task complete"]
    
    Queue --> Redirect["Redirect to change form"]
    Complete -.->|Background| Done["IP block synchronized"]
```

**Sources:** [api/admin.py:1086-1155](), [api/tasks.py:1-200]()

---

### ProxyServerAdmin

`ProxyServerAdmin` manages `ProxyServer` records and includes health check functionality.

**Health Check Workflow:**

| Component | Implementation |
|-----------|---------------|
| Button | `test_now()` display method |
| URL | `<object_id>/health-check/` |
| View | `health_check_view()` |
| Task | `proxy_health_check_single.delay(proxy_id)` |

The health check task:
1. Loads a `ProxyHealthCheckSpec` (which contains a test prompt)
2. Creates a temporary `BrowserUseAgentTask` using the proxy
3. Records the result in `ProxyHealthCheckResult`

**Bulk Actions:**

- **Backfill Missing Proxies:** Queues `backfill_missing_proxy_records.delay()` to auto-create `ProxyServer` records for all `DecodoIP` entries
- **Test Selected Proxies:** Queues health checks for all selected active proxies

**Sources:** [api/admin.py:1183-1347](), [api/tasks.py:200-400]()

---

## User and Organization Admins

### CustomUserAdmin

`CustomUserAdmin` extends Django's default `UserAdmin` with credit summary and metering rollup actions.

**Performance Optimization:**

The `get_queryset()` method annotates each user with:
```python
.annotate(
    total_credits=Sum("task_credits__credits"),
    used_credits=Sum("task_credits__credits_used"),
)
```

This allows the `taskcredit_summary_link()` display method to compute remaining credits without additional queries:
```python
remaining = total - used
```

**Rollup Action:**

The `queue_rollup_for_selected_users` action queues `rollup_usage_for_user.delay(user_id)` for each selected user. This task aggregates raw usage into metering batches for Stripe reporting.

**Sources:** [api/admin.py:973-1042](), [api/tasks/billing_rollup.py:1-200]()

---

## Admin Forms

Custom forms provide validation and UI enhancements for admin workflows.

### GrantPlanCreditsForm

```mermaid
classDiagram
    class GrantPlanCreditsForm {
        +ChoiceField plan
        +DecimalField credits
        +ChoiceField grant_type
        +DateField grant_date
        +DateField expiration_date
        +BooleanField dry_run
        +BooleanField only_if_out_of_credits
        +BooleanField export_csv
        +clean()
    }
    
    class GrantCreditsByUserIdsForm {
        +CharField user_ids
        +ChoiceField plan
        +DecimalField credits
        +ChoiceField grant_type
        +DateField grant_date
        +DateField expiration_date
        +BooleanField dry_run
        +BooleanField only_if_out_of_credits
        +BooleanField export_csv
        +clean()
    }
```

Both forms validate:
- `expiration_date` must be after `grant_date`
- `credits` must be positive
- `plan` must be a valid `PlanNamesChoices` enum value

**Sources:** [api/admin_forms.py:1-150]()

---

## Performance Patterns

### Query Optimization Techniques

**1. select_related() for Foreign Keys**

```python
# api/admin.py:814-817
def get_queryset(self, request):
    qs = super().get_queryset(request)
    return qs.select_related("agent", "user")
```

This reduces the task changelist from O(n) queries to O(1) by performing a JOIN instead of per-row lookups.

**2. Annotated Counts**

```python
# api/admin.py:684-686
def get_queryset(self, request):
    qs = super().get_queryset(request)
    return qs.select_related('user').annotate(num_tasks=Count('tasks'))
```

The annotated `num_tasks` is then accessed without additional queries:
```python
count = getattr(obj, 'num_tasks', None)
if count is None:
    count = obj.tasks.count()  # Fallback for detail view
```

**3. Limited Inline Queries**

Inlines use a two-query approach to limit results:
1. Get PKs of the most recent N records
2. Fetch full records filtered by those PKs

```python
# api/admin.py:628-635
recent_pks = list(qs.values_list('pk', flat=True)[:self.MAX_DISPLAY])
return self.model.objects.filter(pk__in=recent_pks).order_by('-created_at')
```

This prevents Django from raising `SuspiciousOperation` errors when slicing querysets in inlines.

**4. Raw ID Fields**

```python
# api/admin.py:678
raw_id_fields = ('user',)
```

For models with millions of users, raw ID fields replace dropdown selects with autocomplete inputs, avoiding expensive full-table scans.

**Sources:** [api/admin.py:609-636](), [api/admin.py:814-817](), [api/admin.py:684-686]()

---

## Template Customizations

### Custom Change List Templates

Several admins override `change_list_template` to add custom buttons:

| Admin | Template | Added Buttons |
|-------|----------|---------------|
| `TaskCreditAdmin` | `admin/taskcredit_change_list.html` | "Grant by Plan", "Grant by User IDs" |
| `BrowserUseAgentTaskAdmin` | `admin/browseruseagenttask_change_list.html` | "Run Garbage Collection" |
| `PersistentAgentAdmin` | `admin/persistentagent_change_list.html` | "Trigger Event Processing" |

These templates extend Django's default `admin/change_list.html` and inject buttons into the object tools section:

```django
{% block object-tools-items %}
  {{ block.super }}
  <li>
    <a href="{% url 'admin:api_taskcredit_grant_by_plan' %}" class="button">
      Grant by Plan
    </a>
  </li>
{% endblock %}
```

**Sources:** [api/admin.py:222](), [api/admin.py:805](), [api/admin.py:1547]()

---

## Custom URL Patterns

Admins extend the default URL configuration via `get_urls()`:

```mermaid
graph TD
    DefaultURLs["super().get_urls()"]
    CustomURLs["Custom URL patterns"]
    
    subgraph "TaskCreditAdmin URLs"
        GrantPlan["'grant-by-plan/' → grant_by_plan_view"]
        GrantIDs["'grant-by-user-ids/' → grant_by_user_ids_view"]
    end
    
    subgraph "DecodoIPBlockAdmin URLs"
        Sync["'<object_id>/sync/' → sync_view"]
    end
    
    subgraph "ProxyServerAdmin URLs"
        HealthCheck["'<object_id>/health-check/' → health_check_view"]
    end
    
    subgraph "PersistentAgentAdmin URLs"
        SimEmail["'<object_id>/simulate-email/' → simulate_email_view"]
        SimSMS["'<object_id>/simulate-sms/' → simulate_sms_view"]
        Trigger["'trigger-processing/' → trigger_processing_view"]
    end
    
    DefaultURLs --> Concat["custom_urls + urls"]
    GrantPlan --> CustomURLs
    GrantIDs --> CustomURLs
    Sync --> CustomURLs
    HealthCheck --> CustomURLs
    SimEmail --> CustomURLs
    SimSMS --> CustomURLs
    Trigger --> CustomURLs
    CustomURLs --> Concat
```

**Pattern:**
```python
def get_urls(self):
    urls = super().get_urls()
    custom_urls = [
        path('custom-action/', self.admin_site.admin_view(self.custom_view), name='...'),
    ]
    return custom_urls + urls
```

The `admin_site.admin_view()` wrapper ensures custom views enforce authentication and permissions.

**Sources:** [api/admin.py:246-261](), [api/admin.py:1095-1105](), [api/admin.py:1594-1614]()

---

## Stripe Integration Patching

The platform patches dj-stripe's default admin classes to fix compatibility issues with version 2.10.1:

```mermaid
graph LR
    DjStripe["dj-stripe 2.10.1 defaults"]
    Unregister["admin.site.unregister()"]
    Patched["Custom admin classes"]
    
    DjStripe --> Unregister
    Unregister --> Customer["PatchedCustomerAdmin"]
    Unregister --> BankAccount["PatchedBankAccountAdmin"]
    Unregister --> Card["PatchedCardAdmin"]
    
    Customer --> Patched
    BankAccount --> Patched
    Card --> Patched
```

The patches remove references to `customer__default_source`, which was removed in dj-stripe 2.10 but still referenced in the library's admin classes:

```python
# api/admin.py:50-69
admin.site.unregister(Customer)

@admin.register(Customer)
class PatchedCustomerAdmin(StripeModelAdmin):
    list_select_related = ("subscriber", "djstripe_owner_account", "default_payment_method")
```

**Sources:** [api/admin.py:45-70]()

---

## Summary

The Django admin interface in gobii-platform serves as the operational control plane, providing:

1. **Bulk Operations:** Credit granting by plan or user ID with dry-run and CSV export
2. **Agent Testing:** Email/SMS simulation tools that use production ingestion pipelines
3. **Infrastructure Monitoring:** Proxy health checks and IP synchronization
4. **Performance Optimization:** Annotated queries, select_related, and limited inlines to handle large datasets
5. **Custom Workflows:** Event processing triggers, garbage collection, and metering rollup actions

All admin classes follow Django's standard patterns while extending them with custom URLs, actions, and display methods. The interface is optimized for admin users managing thousands of agents, millions of tasks, and complex billing scenarios.

**Sources:** [api/admin.py:1-2456](), [config/settings.py:187-229]()

---

# Page: Testing & CI/CD

# Testing & CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [api/agent/peer_comm.py](api/agent/peer_comm.py)
- [api/agent/peer_link_signals.py](api/agent/peer_link_signals.py)
- [api/agent/tools/peer_dm.py](api/agent/tools/peer_dm.py)
- [api/apps.py](api/apps.py)
- [api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py](api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py)
- [tests/unit/test_agent_short_description.py](tests/unit/test_agent_short_description.py)
- [tests/unit/test_peer_agent_messaging.py](tests/unit/test_peer_agent_messaging.py)

</details>



This document describes the testing infrastructure and continuous integration/continuous deployment (CI/CD) pipeline for the gobii-platform. It covers the tag-based test batching system, GitHub Actions workflow configuration, test execution, and reporting mechanisms.

For information about the Django admin interface and simulation tools, see [Django Admin Interface](#10.1).

---

## Purpose and Scope

The gobii-platform uses a **tag-based test batching system** to enable parallel test execution in CI. All tests must be tagged with a batch identifier, and the CI pipeline enforces this requirement through an automated guard job. The system supports over 60 parallel test batches, significantly reducing total CI runtime compared to sequential execution.

Key aspects covered:
- Test tagging requirements and conventions
- GitHub Actions CI workflow structure
- Test parallelization strategy
- Environment configuration for tests
- Test result aggregation and reporting

---

## Test Structure and Tagging

### Tag-Based Batching

Every test in the codebase **must** be tagged with a batch identifier using Django's `@tag()` decorator. This is enforced by the `tag-guard` job in CI, which runs `scripts/check_test_tags.py` to verify compliance.

```python
@tag("batch_peer_dm")
class PeerMessagingServiceTests(TestCase):
    # Test implementation
```

[tests/unit/test_peer_agent_messaging.py:20-21]()

The tagging system serves two purposes:
1. **Parallel Execution**: Tests are grouped into batches that can run simultaneously in separate CI jobs
2. **Organizational Clarity**: Related tests are grouped together (e.g., all email tests, all agent lifecycle tests)

### Tag Naming Conventions

Tags follow the pattern `batch_<feature_area>` or `<specific_feature>` for specialized tests:

| Tag Pattern | Example | Purpose |
|-------------|---------|---------|
| `batch_<feature>` | `batch_peer_dm` | Feature-specific test batches |
| `batch_<area>_<detail>` | `batch_email_allowlist` | Subdivided feature areas |
| `<special>` | `smtp`, `xvfb` | Environment-specific or infrastructure tests |
| `<area>_batch` | `oss_readiness_batch` | Special validation suites |

**Sources:** [.github/workflows/ci.yml:44-194](), [tests/unit/test_peer_agent_messaging.py:20](), [tests/unit/test_agent_short_description.py:15]()

---

## Test Batch Categories

The platform organizes tests into the following major categories:

### Communication and Messaging
- `batch_email`, `batch_smtp`, `batch_sms`
- `batch_email_body`, `batch_email_allowlist`, `batch_outbound_email`
- `batch_agent_chat`, `batch_peer_dm`, `batch_peer_intro`
- `batch_allowlist_direction`, `batch_allowlist_rules`

### Agent Lifecycle and Processing
- `batch_agent_lifecycle`, `batch_agent_limits`, `batch_soft_expiration`
- `batch_event_processing`, `batch_event_llm`, `batch_event_parallel`
- `batch_spawn_depth`, `batch_pa_shutdown_triggers`

### API and Serialization
- `batch_api_agents`, `batch_api_tasks`, `batch_api_persistent_agents`
- `batch_api_serializer`, `batch_api_decodo`, `batch_api_org_keys`

### Billing and Credits
- `batch_billing`, `batch_subscription`, `batch_task_credits`
- `batch_org_billing`, `batch_owner_billing`, `batch_billing_rollup`
- `batch_pa_step_credits`, `batch_tool_costs`

### Browser Automation
- `batch_browser_profile`, `batch_browser_task_db`, `batch_browser_task_followup`
- `batch_proxy_selection`, `xvfb`

### Tool Integration
- `batch_mcp_tools`, `pipedream_connect`, `batch_charter_tools`

### Infrastructure and Utilities
- `batch_periodic`, `batch_celery_redbeat`, `batch_redis_leaks`, `batch_redis_budget_cleanup`
- `batch_websocket`, `batch_sqlite`, `batch_compaction`, `batch_step_compaction`

### Console and UI
- `batch_console_agents`, `batch_console_allowlist`, `batch_console_api_keys`, `batch_console_context`
- `batch_pages`, `batch_contact_requests`

### Other Features
- `batch_secrets`, `batch_agent_secrets_ctx`, `batch_agent_invite`
- `batch_organizations`, `batch_agent_transfer`, `batch_usage_api`
- `batch_forward_detection`, `batch_link_shortener`, `batch_output_schema`
- `batch_promptree`, `batch_token_usage`, `batch_text_sanitization`
- `batch_agent_short_description`, `batch_schedule`, `batch_stripe_config`
- `batch_email_blocklist`, `batch_email_sender_db`, `batch_outbound_delivery`
- `batch_agent_filesystem`, `oss_readiness_batch`

**Sources:** [.github/workflows/ci.yml:44-194]()

---

## CI/CD Pipeline Architecture

### Workflow Overview

The CI pipeline is defined in `.github/workflows/ci.yml` and consists of three main jobs:

```mermaid
graph TB
    PR["Pull Request or Push to main"]
    
    PR --> TagGuard["tag-guard Job<br/>Verify All Tests Tagged"]
    
    TagGuard -->|"Pass"| TestMatrix["tests Job Matrix<br/>60+ Parallel Batches"]
    TagGuard -->|"Fail"| BlockPR["Block PR<br/>Tests Missing Tags"]
    
    TestMatrix --> Batch1["Batch: email"]
    TestMatrix --> Batch2["Batch: sms"]
    TestMatrix --> Batch3["Batch: peer_dm"]
    TestMatrix --> BatchN["Batch: ... (60+ total)"]
    
    Batch1 --> Upload1["Upload Artifact<br/>test-results-email"]
    Batch2 --> Upload2["Upload Artifact<br/>test-results-sms"]
    Batch3 --> Upload3["Upload Artifact<br/>test-results-peer_dm"]
    BatchN --> UploadN["Upload Artifact<br/>test-results-..."]
    
    Upload1 --> Report["report Job<br/>Combined Test Results"]
    Upload2 --> Report
    Upload3 --> Report
    UploadN --> Report
    
    Report --> Publish["Publish Unit Test Results<br/>EnricoMi/publish-unit-test-result-action"]
    Publish --> PRCheck["PR Check: Combined Test Results"]
```

**Sources:** [.github/workflows/ci.yml:1-307]()

### Job Definitions

#### 1. Tag Guard Job

The `tag-guard` job ensures all tests are properly tagged before any test execution begins:

[.github/workflows/ci.yml:20-34]()

This job runs `scripts/check_test_tags.py`, which verifies:
- Every test class has at least one `@tag()` decorator
- All tags used in tests are defined in the CI matrix
- No orphaned or undefined tags exist

#### 2. Test Matrix Job

The `tests` job runs in parallel with a matrix strategy, executing one batch per job:

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - batch: email
        tag: batch_email
      - batch: smtp
        tag: smtp
      # ... 60+ more batches
```

[.github/workflows/ci.yml:36-194]()

Each batch job executes:
1. **Checkout code**
2. **Set up Python 3.12**
3. **Install dependencies** using `uv` with venv caching
4. **Run tagged tests** using Django's test runner with XML output
5. **Upload test results** as artifacts

#### 3. Combined Report Job

The `report` job aggregates all test results and publishes a single PR check:

[.github/workflows/ci.yml:289-307]()

This job:
- Downloads all test result artifacts
- Merges XML files
- Uses `EnricoMi/publish-unit-test-result-action` to create a combined check
- Does not post individual PR comments (to reduce noise)

**Sources:** [.github/workflows/ci.yml:1-307]()

---

## Environment Configuration

### Test Settings Override

Tests use a dedicated settings module that overrides production configuration:

```
DJANGO_SETTINGS_MODULE: config.test_settings
```

[.github/workflows/ci.yml:197]()

The test settings module (`config/test_settings.py`) typically:
- Uses **SQLite** instead of PostgreSQL for faster test execution
- Disables external service integrations
- Uses in-memory storage where possible
- Configures faster password hashing

### Environment Variables

The CI workflow sets minimal environment variables to satisfy Django's settings import:

```yaml
env:
  DJANGO_SECRET_KEY: test-secret
  GOBII_ENCRYPTION_KEY: dummy-encryption-key-for-testing
  POSTGRES_DB: test
  POSTGRES_USER: test
  POSTGRES_PASSWORD: test
  POSTGRES_HOST: localhost
  POSTGRES_PORT: "5432"
  REDIS_URL: redis://localhost:6379/0
  OPENAI_API_KEY: dummy
  BROWSER_USE_TASK_MAX_COUNT: "0"
```

[.github/workflows/ci.yml:202-215]()

Key configuration notes:
- **OPENAI_API_KEY** is set to a dummy value to pass LLM provider validation (the actual value is unused in tests)
- **BROWSER_USE_TASK_MAX_COUNT** is set to `0` to disable Celery worker self-shutdown logic
- PostgreSQL credentials are provided but typically unused (SQLite is preferred in tests)

**Sources:** [.github/workflows/ci.yml:195-215]()

---

## Dependency Management with uv

The pipeline uses **uv** (Astral's Python package installer) for fast, reliable dependency installation:

```mermaid
graph LR
    subgraph "Dependency Installation Flow"
        SetupUV["setup-uv@v6<br/>with cache enabled"]
        
        RestoreVenv["Restore venv cache<br/>Key: venv-{os}-py3.12-{uv.lock hash}"]
        
        CheckLock{"uv.lock<br/>exists?"}
        
        SyncLocked["uv sync --frozen<br/>--all-extras --dev"]
        SyncUnlocked["uv sync<br/>--all-extras --dev"]
        
        AddXML["uv pip install<br/>unittest-xml-reporting"]
        
        SaveVenv["Save venv cache<br/>(if cache miss)"]
        
        SetupUV --> RestoreVenv
        RestoreVenv --> CheckLock
        CheckLock -->|Yes| SyncLocked
        CheckLock -->|No| SyncUnlocked
        SyncLocked --> AddXML
        SyncUnlocked --> AddXML
        AddXML --> SaveVenv
    end
```

**Cache Strategy:**
- Cache key includes OS, Python version, and `uv.lock` hash
- Cached `.venv` directories are restored to skip dependency resolution
- `--frozen` flag ensures reproducible builds when lockfile exists
- `unittest-xml-reporting` is added separately for JUnit XML output

**Sources:** [.github/workflows/ci.yml:226-262]()

---

## Test Execution

### Running Tests in CI

Each batch runs with the following command:

```bash
uv run python manage.py test --tag "$TAG" \
  --settings=config.test_settings \
  --parallel 1 \
  --testrunner=xmlrunner.extra.djangotestrunner.XMLTestRunner
```

[.github/workflows/ci.yml:270-273]()

**Command Options:**
- `--tag "$TAG"`: Filters tests to only those with the specified tag
- `--settings=config.test_settings`: Uses test-specific settings
- `--parallel 1`: Runs tests serially within each batch (parallelism is at the job level, not within batches)
- `--testrunner=...XMLTestRunner`: Generates JUnit XML output for reporting

### XML Output Collection

After test execution, any stray XML files are collected:

```bash
for f in TEST-*.xml; do mv "$f" "$TEST_OUTPUT_DIR/"; done || true
```

[.github/workflows/ci.yml:275-276]()

The XML files are then uploaded as artifacts with a batch-specific name:

```yaml
name: test-results-${{ matrix.batch }}
path: test-results/**
```

[.github/workflows/ci.yml:282-283]()

**Sources:** [.github/workflows/ci.yml:264-286]()

---

## Test Examples and Patterns

### Example: Peer Messaging Tests

The `batch_peer_dm` tests demonstrate common patterns:

```python
@tag("batch_peer_dm")
class PeerMessagingServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create shared test data
        User = get_user_model()
        cls.user = User.objects.create_user(...)
        cls.agent_a = PersistentAgent.objects.create(...)
        cls.agent_b = PersistentAgent.objects.create(...)
    
    def setUp(self):
        # Clear per-test data
        AgentPeerLink.objects.all().delete()
        # Create fresh link for each test
        self.link = AgentPeerLink.objects.create(...)
        self.service = PeerMessagingService(self.agent_a, self.agent_b)
```

[tests/unit/test_peer_agent_messaging.py:20-65]()

**Common Patterns:**
- Use `setUpTestData()` for immutable fixtures (runs once per test class)
- Use `setUp()` for per-test state reset
- Mock external dependencies with `unittest.mock.patch`
- Use `transaction.on_commit` patches when testing async task queueing

### Mocking Celery Tasks

When testing code that enqueues Celery tasks:

```python
def test_send_message_creates_records_and_triggers_processing(self):
    with patch('api.agent.tasks.process_agent_events_task') as task_mock, patch(
        'api.agent.peer_comm.transaction.on_commit', lambda cb: cb()
    ):
        task_mock.delay = MagicMock()
        result = self.service.send_message("Hello Beta")
    
    task_mock.delay.assert_called_once_with(str(self.agent_b.id))
```

[tests/unit/test_peer_agent_messaging.py:67-93]()

This pattern:
1. Patches the task to prevent actual Celery execution
2. Patches `transaction.on_commit` to execute callbacks immediately
3. Asserts the task was called with expected arguments

### Testing Error Conditions

Tests verify error handling and edge cases:

```python
def test_throttle_when_quota_exhausted(self):
    # Exhaust quota
    self.service.send_message("First")
    
    state = AgentCommPeerState.objects.get(...)
    self.assertEqual(state.credits_remaining, 0)
    
    # Verify throttling
    with self.assertRaises(PeerMessagingError) as err_ctx:
        self.service.send_message("Second")
    
    self.assertEqual(err_ctx.exception.status, "throttled")
```

[tests/unit/test_peer_agent_messaging.py:115-150]()

**Sources:** [tests/unit/test_peer_agent_messaging.py:1-235](), [tests/unit/test_agent_short_description.py:1-84]()

---

## CI Workflow Execution Diagram

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant GH as "GitHub"
    participant TagGuard as "tag-guard Job"
    participant Matrix as "tests Matrix Job"
    participant Batch as "Individual Batch Runner"
    participant Artifacts as "GitHub Artifacts"
    participant Report as "report Job"
    participant PR as "PR Check"
    
    Dev->>GH: Push to PR or main
    GH->>TagGuard: Trigger tag-guard
    TagGuard->>TagGuard: Run check_test_tags.py
    
    alt All tests tagged
        TagGuard-->>GH: ✓ Pass
        GH->>Matrix: Start 60+ parallel jobs
        
        par Parallel Execution
            Matrix->>Batch: email batch
            Matrix->>Batch: sms batch
            Matrix->>Batch: peer_dm batch
            Matrix->>Batch: ... (57+ more)
        end
        
        Batch->>Batch: Setup Python 3.12
        Batch->>Batch: Restore/Install deps with uv
        Batch->>Batch: Run Django tests for tag
        Batch->>Batch: Collect TEST-*.xml
        Batch->>Artifacts: Upload test-results-{batch}
        
        Batch-->>Matrix: Complete
        
        Matrix-->>Report: All batches finished
        Report->>Artifacts: Download all test-results-*
        Report->>Report: Merge XML files
        Report->>PR: Publish combined results
        PR-->>Dev: Show test status
    else Missing tags
        TagGuard-->>GH: ✗ Fail
        GH->>PR: Block PR
        PR-->>Dev: Fix tagging required
    end
```

**Sources:** [.github/workflows/ci.yml:1-307]()

---

## Concurrency Control

The workflow uses concurrency groups to auto-cancel previous runs when new commits are pushed:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

[.github/workflows/ci.yml:9-11]()

This prevents resource waste from running outdated test suites when developers push rapid iterations.

**Sources:** [.github/workflows/ci.yml:9-11]()

---

## Permissions

The workflow requires specific permissions to post test results:

```yaml
permissions:
  contents: read
  checks: write
  pull-requests: write
```

[.github/workflows/ci.yml:14-17]()

- **contents: read** - Access repository code
- **checks: write** - Create check runs for test results
- **pull-requests: write** - Post comments on PRs (though currently disabled via `comment_mode: off`)

**Sources:** [.github/workflows/ci.yml:14-17]()

---

## Test Result Reporting

### Artifact Storage

Test results are stored as artifacts with a 7-day retention:

```yaml
- name: Upload test results artifact
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ matrix.batch }}
    path: test-results/**
    if-no-files-found: warn
    retention-days: 7
```

[.github/workflows/ci.yml:278-285]()

The `if: always()` condition ensures artifacts are uploaded even if tests fail.

### Combined Reporting

The `report` job uses `EnricoMi/publish-unit-test-result-action@v2` to aggregate results:

```yaml
- name: Publish combined test results
  uses: EnricoMi/publish-unit-test-result-action@v2
  with:
    files: all-results/**/*.xml
    check_name: "Combined Test Results"
    comment_mode: off
```

[.github/workflows/ci.yml:302-307]()

**Configuration:**
- `files`: Pattern matching all downloaded XML files
- `check_name`: Name displayed in PR checks
- `comment_mode: off`: Disables individual PR comments (reduces noise)

**Sources:** [.github/workflows/ci.yml:289-307]()

---

## Running Tests Locally

### Running All Tests

To run all tests locally (not recommended due to time):

```bash
python manage.py test --settings=config.test_settings
```

### Running a Specific Batch

To run a single batch locally:

```bash
python manage.py test --tag batch_peer_dm --settings=config.test_settings
```

### Running a Specific Test

To run an individual test class or method:

```bash
python manage.py test tests.unit.test_peer_agent_messaging.PeerMessagingServiceTests \
  --settings=config.test_settings
```

Or a specific method:

```bash
python manage.py test tests.unit.test_peer_agent_messaging.PeerMessagingServiceTests.test_send_message_creates_records_and_triggers_processing \
  --settings=config.test_settings
```

### Running with Coverage

To generate coverage reports:

```bash
coverage run --source='.' manage.py test --settings=config.test_settings
coverage report
coverage html  # Generate HTML report
```

---

## Test Infrastructure Components

### Key Testing Files and Modules

| Component | Purpose |
|-----------|---------|
| `config/test_settings.py` | Test-specific Django settings (SQLite, mocked services) |
| `scripts/check_test_tags.py` | Tag validation script run by CI |
| `.github/workflows/ci.yml` | CI pipeline definition |
| `tests/unit/` | Unit test directory |
| `tests/integration/` | Integration test directory (if exists) |

### Test Runner Configuration

The platform uses `xmlrunner.extra.djangotestrunner.XMLTestRunner` for JUnit XML output:

[.github/workflows/ci.yml:273]()

This test runner:
- Extends Django's default test runner
- Generates XML files compatible with CI reporting tools
- Outputs to `TEST-*.xml` files in the test output directory

**Sources:** [.github/workflows/ci.yml:1-307](), [tests/unit/test_peer_agent_messaging.py:1-235]()

---

## Summary

The gobii-platform's testing and CI/CD infrastructure achieves:

1. **Fast Feedback**: 60+ parallel test batches reduce CI time from hours to minutes
2. **Enforced Quality**: Tag guard prevents untagged tests from entering the codebase
3. **Reproducibility**: Locked dependencies (`uv.lock`) and caching ensure consistent test environments
4. **Comprehensive Reporting**: Combined test results provide a single source of truth for PR health
5. **Developer Efficiency**: Auto-cancellation prevents wasted resources on stale commits

The tag-based batching system is central to the platform's testing strategy, enabling both organizational clarity and CI parallelism.