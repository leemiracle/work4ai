<!-- source: DeepWiki mcp.deepwiki.com · repo Significant-Gravitas/AutoGPT · extra page Notification System · fetched 2026-10-26 -->

# Notification System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [autogpt_platform/backend/backend/data/notifications.py](autogpt_platform/backend/backend/data/notifications.py)
- [autogpt_platform/backend/backend/data/user.py](autogpt_platform/backend/backend/data/user.py)
- [autogpt_platform/backend/backend/executor/scheduler.py](autogpt_platform/backend/backend/executor/scheduler.py)
- [autogpt_platform/backend/backend/monitoring/block_error_monitor.py](autogpt_platform/backend/backend/monitoring/block_error_monitor.py)
- [autogpt_platform/backend/backend/monitoring/late_execution_monitor.py](autogpt_platform/backend/backend/monitoring/late_execution_monitor.py)
- [autogpt_platform/backend/backend/monitoring/notification_monitor.py](autogpt_platform/backend/backend/monitoring/notification_monitor.py)
- [autogpt_platform/backend/backend/notifications/email.py](autogpt_platform/backend/backend/notifications/email.py)
- [autogpt_platform/backend/backend/notifications/notifications.py](autogpt_platform/backend/backend/notifications/notifications.py)
- [autogpt_platform/backend/backend/notifications/templates/agent_run.html.jinja2](autogpt_platform/backend/backend/notifications/templates/agent_run.html.jinja2)
- [autogpt_platform/backend/backend/notifications/templates/base.html.jinja2](autogpt_platform/backend/backend/notifications/templates/base.html.jinja2)
- [autogpt_platform/backend/backend/util/service.py](autogpt_platform/backend/backend/util/service.py)
- [autogpt_platform/backend/backend/util/service_test.py](autogpt_platform/backend/backend/util/service_test.py)

</details>



The Notification System manages all user communications within the AutoGPT Platform, handling email delivery, notification batching, user preferences, and scheduled summaries. This system processes various notification types including agent execution results, balance alerts, error notifications, and periodic summaries.

For information about the broader service architecture that the notification system operates within, see [Service Architecture](#3.2.1). For details about API key management and user authentication, see [API Key Management](#3.2.14).

## Architecture Overview

The notification system follows a queue-based architecture using RabbitMQ for message routing and processing different notification strategies:

```mermaid
graph TB
    subgraph "Notification Sources"
        EXEC["ExecutionManager"]
        SCHED["Scheduler"]
        API["API Endpoints"]
        WEBHOOK["Webhook Handlers"]
    end
    
    subgraph "Queue Management"
        QUEUE_FUNC["queue_notification()"]
        ROUTING["get_routing_key()"]
        
        subgraph "RabbitMQ Exchanges"
            NOTIF_EXCHANGE["notifications Exchange"]
            DL_EXCHANGE["dead_letter Exchange"]
        end
        
        subgraph "Processing Queues"
            IMM_QUEUE["immediate_notifications_v2"]
            BATCH_QUEUE["batch_notifications_v2"]
            SUMMARY_QUEUE["summary_notifications_v2"]
            ADMIN_QUEUE["admin_notifications_v2"]
            FAILED_QUEUE["failed_notifications_v2"]
        end
    end
    
    subgraph "NotificationManager Service"
        MANAGER["NotificationManager"]
        PROCESS_IMM["_process_immediate()"]
        PROCESS_BATCH["_process_batch()"]
        PROCESS_SUMMARY["_process_summary()"]
        PROCESS_ADMIN["_process_admin_message()"]
    end
    
    subgraph "Email Delivery"
        EMAIL_SENDER["EmailSender"]
        POSTMARK["Postmark API"]
        TEMPLATES["Jinja2 Templates"]
    end
    
    subgraph "Data Layer"
        USER_PREFS["User Preferences"]
        BATCH_STORAGE["Notification Batches"]
        EMAIL_VERIFICATION["Email Verification"]
    end
    
    %% Flow from sources
    EXEC --> QUEUE_FUNC
    SCHED --> QUEUE_FUNC
    API --> QUEUE_FUNC
    WEBHOOK --> QUEUE_FUNC
    
    %% Queue routing
    QUEUE_FUNC --> ROUTING
    ROUTING --> NOTIF_EXCHANGE
    NOTIF_EXCHANGE --> IMM_QUEUE
    NOTIF_EXCHANGE --> BATCH_QUEUE
    NOTIF_EXCHANGE --> SUMMARY_QUEUE
    NOTIF_EXCHANGE --> ADMIN_QUEUE
    
    %% Processing
    IMM_QUEUE --> PROCESS_IMM
    BATCH_QUEUE --> PROCESS_BATCH
    SUMMARY_QUEUE --> PROCESS_SUMMARY
    ADMIN_QUEUE --> PROCESS_ADMIN
    
    PROCESS_IMM --> EMAIL_SENDER
    PROCESS_BATCH --> EMAIL_SENDER
    PROCESS_SUMMARY --> EMAIL_SENDER
    PROCESS_ADMIN --> EMAIL_SENDER
    
    %% Email delivery
    EMAIL_SENDER --> TEMPLATES
    EMAIL_SENDER --> POSTMARK
    
    %% Data dependencies
    MANAGER --> USER_PREFS
    MANAGER --> BATCH_STORAGE
    MANAGER --> EMAIL_VERIFICATION
    
    %% Failed message handling
    IMM_QUEUE -.-> DL_EXCHANGE
    BATCH_QUEUE -.-> DL_EXCHANGE
    SUMMARY_QUEUE -.-> DL_EXCHANGE
    ADMIN_QUEUE -.-> DL_EXCHANGE
    DL_EXCHANGE --> FAILED_QUEUE
```

Sources: [autogpt_platform/backend/backend/notifications/notifications.py:59-125](), [autogpt_platform/backend/backend/notifications/notifications.py:207-291]()

## Core Components

### NotificationManager Service

The `NotificationManager` class serves as the main orchestrator for notification processing:

```mermaid
graph TB
    subgraph "NotificationManager Class"
        INIT["__init__()"]
        RUN_SERVICE["run_service()"]
        RUN_QUEUE["_run_queue()"]
        
        subgraph "Processing Methods"
            PROCESS_IMM["_process_immediate()"]
            PROCESS_BATCH["_process_batch()"]
            PROCESS_SUMMARY["_process_summary()"]
            PROCESS_ADMIN["_process_admin_message()"]
        end
        
        subgraph "Utility Methods"
            SHOULD_EMAIL["_should_email_user_based_on_preference()"]
            SHOULD_BATCH["_should_batch()"]
            GATHER_SUMMARY["_gather_summary_data()"]
            PARSE_MSG["_parse_message()"]
        end
        
        subgraph "Exposed Methods"
            QUEUE_WEEKLY["queue_weekly_summary()"]
            PROCESS_BATCHES["process_existing_batches()"]
            DISCORD_ALERT["discord_system_alert()"]
        end
    end
    
    subgraph "Dependencies"
        RABBITMQ["AsyncRabbitMQ"]
        EMAIL_SENDER["EmailSender"]
        DB_CLIENT["DatabaseManagerClient"]
    end
    
    INIT --> EMAIL_SENDER
    RUN_SERVICE --> RABBITMQ
    RUN_QUEUE --> PROCESS_IMM
    RUN_QUEUE --> PROCESS_BATCH
    RUN_QUEUE --> PROCESS_SUMMARY
    RUN_QUEUE --> PROCESS_ADMIN
    
    PROCESS_IMM --> SHOULD_EMAIL
    PROCESS_BATCH --> SHOULD_BATCH
    PROCESS_SUMMARY --> GATHER_SUMMARY
    
    QUEUE_WEEKLY --> DB_CLIENT
    PROCESS_BATCHES --> DB_CLIENT
```

Sources: [autogpt_platform/backend/backend/notifications/notifications.py:207-291](), [autogpt_platform/backend/backend/notifications/notifications.py:728-781]()

### Notification Data Models

The system supports multiple notification types with specific data structures:

| Notification Type | Data Model | Queue Strategy | Purpose |
|-------------------|------------|----------------|---------|
| `AGENT_RUN` | `AgentRunData` | BATCH | Agent execution reports |
| `ZERO_BALANCE` | `ZeroBalanceData` | BACKOFF | Credit depletion alerts |
| `LOW_BALANCE` | `LowBalanceData` | IMMEDIATE | Low credit warnings |
| `BLOCK_EXECUTION_FAILED` | `BlockExecutionFailedData` | BACKOFF | Block execution errors |
| `CONTINUOUS_AGENT_ERROR` | `ContinuousAgentErrorData` | BACKOFF | Persistent agent failures |
| `DAILY_SUMMARY` | `DailySummaryData` | SUMMARY | Daily activity reports |
| `WEEKLY_SUMMARY` | `WeeklySummaryData` | SUMMARY | Weekly activity reports |
| `REFUND_REQUEST` | `RefundRequestData` | ADMIN | Payment refund requests |
| `AGENT_APPROVAL` | `AgentApprovalData` | IMMEDIATE | Notification for agent approval |
| `AGENT_REJECTION` | `AgentRejectionData` | IMMEDIATE | Notification for agent rejection |

Sources: [autogpt_platform/backend/backend/data/notifications.py:46-242](), [autogpt_platform/backend/backend/data/notifications.py:266-318]()

## Queue Processing Strategies

The notification system implements four distinct processing strategies:

### Immediate Processing

Messages routed to `immediate_notifications_v2` queue are processed immediately by `_process_immediate()`:

- Validates user email and preferences
- Sends notification directly via `EmailSender`
- Used for critical notifications like low balance warnings
Sources: [autogpt_platform/backend/backend/notifications/notifications.py:555-580]()

### Batch Processing

Messages routed to `batch_notifications_v2` queue are accumulated and processed by `_process_batch()`:

- Notifications are stored in `UserNotificationBatch` records
- Batches are processed when they reach maximum age (defined by `get_batch_delay()`)
- Multiple notifications of the same type are combined into single emails
- Prevents notification spam for high-frequency events
Sources: [autogpt_platform/backend/backend/notifications/notifications.py:582-640]()

### Summary Processing

Messages routed to `summary_notifications_v2` queue trigger summary generation by `_process_summary()`:

- Aggregates data from multiple sources (executions, credits, etc.)
- Generates comprehensive activity reports
- Scheduled via `Scheduler` service for daily/weekly summaries
Sources: [autogpt_platform/backend/backend/notifications/notifications.py:642-695]()

### Admin Processing

Messages routed to `admin_notifications_v2` queue are processed by `_process_admin_message()`:

- Sent directly to admin email addresses
- Used for system-critical notifications requiring immediate attention
- Bypasses user preferences and verification checks
Sources: [autogpt_platform/backend/backend/notifications/notifications.py:697-726]()

## Email Delivery System

### EmailSender Component

The `EmailSender` class handles template processing and email delivery:

```mermaid
graph TB
    subgraph "EmailSender Class"
        INIT["__init__()"]
        SEND_TEMPLATED["send_templated()"]
        GET_TEMPLATE["_get_template()"]
        SEND_EMAIL["_send_email()"]
    end
    
    subgraph "Template System"
        BASE_TEMPLATE["base.html.jinja2"]
        NOTIF_TEMPLATES["Notification Templates"]
        TEXT_FORMATTER["TextFormatter"]
    end
    
    subgraph "External Service"
        POSTMARK_CLIENT["TypedPostmarkClient"]
        POSTMARK_API["Postmark API"]
    end
    
    INIT --> POSTMARK_CLIENT
    INIT --> TEXT_FORMATTER
    
    SEND_TEMPLATED --> GET_TEMPLATE
    GET_TEMPLATE --> BASE_TEMPLATE
    GET_TEMPLATE --> NOTIF_TEMPLATES
    
    SEND_TEMPLATED --> TEXT_FORMATTER
    SEND_TEMPLATED --> SEND_EMAIL
    
    SEND_EMAIL --> POSTMARK_CLIENT
    POSTMARK_CLIENT --> POSTMARK_API
```

Sources: [autogpt_platform/backend/backend/notifications/email.py:34-137]()

### Template System

Email templates are stored as Jinja2 files with specific naming conventions:

- Base template: `templates/base.html.jinja2` [autogpt_platform/backend/backend/notifications/templates/base.html.jinja2:1-174]()
- Notification templates: `templates/{notification_type}.html.jinja2` (e.g., `agent_run.html.jinja2` [autogpt_platform/backend/backend/notifications/templates/agent_run.html.jinja2:1-143]())
- Templates receive notification data and formatting context
- Support for unsubscribe links and branding

Sources: [autogpt_platform/backend/backend/notifications/email.py:92-109](), [autogpt_platform/backend/backend/notifications/templates/agent_run.html.jinja2:1-143]()

## User Preferences and Controls

### Notification Preferences

Users can control notification delivery through preference settings:

```mermaid
graph TB
    subgraph "User Preference System"
        PREFS["NotificationPreference"]
        UPDATE_PREFS["update_user_notification_preference()"]
        GET_PREFS["get_user_notification_preference()"]
        EMAIL_VERIFICATION["get_user_email_verification()"]
    end
    
    subgraph "Preference Controls"
        NOTIF_TYPES["Notification Type Flags"]
        DAILY_LIMIT["maxEmailsPerDay"]
        EMAIL_ADDR["email"]
        EMAIL_VERIFIED["emailVerified"]
    end
    
    subgraph "Unsubscribe System"
        UNSUB_LINK["generate_unsubscribe_link()"]
        UNSUB_TOKEN["unsubscribe_user_by_token()"]
        HMAC_VERIFY["HMAC Signature Verification"]
    end
    
    PREFS --> NOTIF_TYPES
    PREFS --> DAILY_LIMIT
    PREFS --> EMAIL_ADDR
    PREFS --> EMAIL_VERIFIED
    
    UPDATE_PREFS --> PREFS
    GET_PREFS --> PREFS
    
    UNSUB_LINK --> HMAC_VERIFY
    UNSUB_TOKEN --> HMAC_VERIFY
```

Sources: [autogpt_platform/backend/backend/data/user.py:208-319](), [autogpt_platform/backend/backend/data/user.py:348-401]()

## Scheduled Operations

### Scheduler Integration

The `Scheduler` service manages periodic notification operations:

| Operation | Schedule | Function | Purpose |
|-----------|----------|----------|---------|
| Weekly Summary | `0 * * * *` (hourly) | `process_weekly_summary()` | Queue weekly summary notifications |
| Batch Processing | On-demand | `process_existing_batches()` | Process aged notification batches |
| Late Execution Alerts | Configurable interval | `report_late_executions()` | Alert on delayed executions |
| Block Error Rates | Configurable interval | `report_block_error_rates()` | Alert on high block error rates |

Sources: [autogpt_platform/backend/backend/executor/scheduler.py:254-281](), [autogpt_platform/backend/backend/monitoring/notification_monitor.py:18-30](), [autogpt_platform/backend/backend/monitoring/late_execution_monitor.py:109-112](), [autogpt_platform/backend/backend/monitoring/block_error_monitor.py:53-54]()

### Background Processing

Long-running operations use `ProcessPoolExecutor` for background execution:

- Weekly summary generation: `background_executor.submit()`
- Batch processing: `_process_existing_batches()`
- Prevents blocking of main service thread

Sources: [autogpt_platform/backend/backend/notifications/notifications.py:235-266](), [autogpt_platform/backend/backend/util/service.py:60]()

## Service Communication

### Client Interface

Other services interact with the notification system via `NotificationManagerClient`:

```mermaid
graph TB
    subgraph "NotificationManagerClient"
        PROCESS_BATCHES["process_existing_batches"]
        QUEUE_WEEKLY["queue_weekly_summary"]
        DISCORD_ALERT["discord_system_alert"]
        QUEUE_NOTIFICATION["queue_notification"]
        QUEUE_NOTIFICATION_ASYNC["queue_notification_async"]
    end
    
    subgraph "Service Callers"
        SCHEDULER["Scheduler"]
        EXECUTOR["ExecutionManager"]
        API_ENDPOINTS["API Endpoints"]
        MONITORS["Monitoring Services"]
    end
    
    SCHEDULER --> PROCESS_BATCHES
    SCHEDULER --> QUEUE_WEEKLY
    MONITORS --> DISCORD_ALERT
    
    EXECUTOR --> QUEUE_NOTIFICATION
    API_ENDPOINTS --> QUEUE_NOTIFICATION_ASYNC
```

Sources: [autogpt_platform/backend/backend/notifications/notifications.py:783-791](), [autogpt_platform/backend/backend/notifications/notifications.py:157-204]()

## Configuration and Setup

### RabbitMQ Configuration

The notification system requires specific RabbitMQ setup via `create_notification_config()`:

- **Exchanges**: `notifications` (topic), `dead_letter` (topic)
- **Queues**: Each with dead letter routing for failed messages, using `x-queue-type: quorum` for durability.
- **Routing Keys**: Pattern-based routing using notification type and strategy.

Sources: [autogpt_platform/backend/backend/notifications/notifications.py:63-118]()

### Service Dependencies

The `NotificationManager` depends on:

- **RabbitMQ**: Message queuing and routing
- **PostgreSQL**: User data, preferences, and batch storage  
- **Redis**: Caching and event bus (inherited from `AppService`)
- **Postmark**: Email delivery service
- **DatabaseManager**: Data access layer

Sources: [autogpt_platform/backend/backend/notifications/notifications.py:63-118](), [autogpt_platform/backend/backend/util/service.py:114-227]()

---

