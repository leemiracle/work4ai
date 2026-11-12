<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browser-use-node · page 3 Real-time Features · fetched 2026-10-30 -->

# Real-time Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/lib/nextjs/hooks/useBrowserUse.ts](src/lib/nextjs/hooks/useBrowserUse.ts)
- [src/lib/nextjs/server/utils.ts](src/lib/nextjs/server/utils.ts)
- [src/lib/webhooks.ts](src/lib/webhooks.ts)
- [src/resources/tasks.ts](src/resources/tasks.ts)
- [tests/lib/webhooks.test.ts](tests/lib/webhooks.test.ts)
- [yarn.lock](yarn.lock)

</details>



This document covers the real-time capabilities of the browser-use-node SDK, including task streaming, webhook notifications, and framework integrations. These features enable monitoring of browser automation tasks as they execute, receiving immediate notifications of status changes, and integrating real-time updates into web applications.

For detailed API documentation of the Tasks resource, see [API Documentation](#7.1). For webhook configuration and authentication setup, see [Authentication](#5.2).

## Overview

The browser-use-node SDK provides three primary methods for receiving real-time updates about task execution:

| Method | Use Case | Communication Pattern | Latency |
|--------|----------|----------------------|---------|
| **Task Streaming** | Direct task monitoring | Polling with async generators | ~500ms intervals |
| **Webhooks** | Server-to-server notifications | HTTP POST with signature verification | Near real-time |
| **Server-Sent Events** | Web application integration | EventSource streaming | Real-time |

## Real-time Communication Architecture

```mermaid
graph TD
    CloudAPI["Browser Use Cloud API"]
    
    subgraph "SDK Client Layer"
        TasksResource["Tasks Resource<br/>(tasks.ts)"]
        WebhookUtils["Webhook Utilities<br/>(webhooks.ts)"]
        NextJSUtils["Next.js Utils<br/>(nextjs/server/utils.ts)"]
    end
    
    subgraph "Communication Methods"
        Polling["Polling via watch()<br/>tasks.ts:130-164"]
        Streaming["Streaming via stream()<br/>tasks.ts:166-192"]
        WebhookEvents["Webhook Events<br/>webhooks.ts:67-119"]
        SSE["Server-Sent Events<br/>gtos() function"]
    end
    
    subgraph "Client Integration"
        ReactHook["useBrowserUse Hook<br/>useBrowserUse.ts:10-37"]
        CLIListen["CLI listen command"]
        WebApp["Web Applications"]
    end
    
    CloudAPI --> TasksResource
    CloudAPI --> WebhookEvents
    
    TasksResource --> Polling
    TasksResource --> Streaming
    WebhookUtils --> WebhookEvents
    NextJSUtils --> SSE
    
    Polling --> Streaming
    Streaming --> SSE
    SSE --> ReactHook
    WebhookEvents --> CLIListen
    
    ReactHook --> WebApp
    CLIListen --> WebApp
    
    style TasksResource fill:#e8f5e8
    style WebhookEvents fill:#fff3e0
    style SSE fill:#e1f5fe
```

**Real-time Communication Flow**

Sources: [src/resources/tasks.ts:130-192](), [src/lib/webhooks.ts:67-119](), [src/lib/nextjs/server/utils.ts:15-69](), [src/lib/nextjs/hooks/useBrowserUse.ts:10-37]()

## Task Streaming Implementation

The core streaming functionality is built around an async generator pattern that polls the Browser Use Cloud API for task status updates.

```mermaid
graph LR
    subgraph "Tasks Resource Methods"
        watch["watch()<br/>private polling method"]
        stream["stream()<br/>public streaming API"]
        retrieve["retrieve()<br/>task status fetch"]
    end
    
    subgraph "Streaming Flow"
        poll["Poll every 500ms"]
        hash["Hash comparison<br/>getTaskViewHash()"]
        yield["Yield status events"]
        check["Check terminal status"]
    end
    
    stream --> watch
    watch --> retrieve
    watch --> poll
    poll --> hash
    hash --> yield
    yield --> check
    check --> poll
    
    style watch fill:#e8f5e8
    style stream fill:#c8e6c9
```

**Task Streaming Method Chain**

The `stream()` method [src/resources/tasks.ts:174-192]() wraps the private `watch()` method [src/resources/tasks.ts:130-164](), which implements a polling loop that:

1. Calls `retrieve()` to get current task status
2. Compares hash using `getTaskViewHash()` to detect changes
3. Yields events only when status actually changes
4. Terminates when task reaches terminal state (`finished`, `stopped`, `paused`)

Sources: [src/resources/tasks.ts:130-192](), [src/lib/stream.ts:15]()

## Webhook Event System

Webhooks provide server-to-server notifications with cryptographic signature verification for security.

```mermaid
graph TD
    subgraph "Webhook Event Types"
        TestEvent["test<br/>zWebhookTest"]
        TaskStatusEvent["agent.task.status_update<br/>zWebhookAgentTaskStatusUpdate"]
    end
    
    subgraph "Verification Process"
        ParseBody["Parse JSON body"]
        ValidateSchema["Validate against zWebhookSchema"]
        CreateSignature["createWebhookSignature()"]
        CompareSignature["Compare HMAC signatures"]
    end
    
    subgraph "Event Processing"
        verifyWebhookEventSignature["verifyWebhookEventSignature()<br/>webhooks.ts:67-99"]
        EventHandler["Application Event Handler"]
    end
    
    TestEvent --> ValidateSchema
    TaskStatusEvent --> ValidateSchema
    
    ParseBody --> ValidateSchema
    ValidateSchema --> CreateSignature
    CreateSignature --> CompareSignature
    CompareSignature --> verifyWebhookEventSignature
    verifyWebhookEventSignature --> EventHandler
    
    style verifyWebhookEventSignature fill:#fff3e0
    style TaskStatusEvent fill:#e8f5e8
```

**Webhook Event Processing Pipeline**

The webhook system uses Zod schemas [src/lib/webhooks.ts:13-60]() for type-safe event parsing and HMAC-SHA256 signatures [src/lib/webhooks.ts:104-119]() for security verification.

Sources: [src/lib/webhooks.ts:13-119](), [tests/lib/webhooks.test.ts:58-113]()

## Server-Sent Events Integration

For web applications, the SDK provides utilities to convert async generators into Server-Sent Events streams.

```mermaid
sequenceDiagram
    participant Client as "React Component"
    participant Hook as "useBrowserUse Hook"
    participant EventSource as "EventSource API"
    participant Server as "Next.js API Route"
    participant Generator as "tasks.stream()"
    
    Client->>Hook: useBrowserUse(route)
    Hook->>EventSource: new EventSource(route)
    EventSource->>Server: GET /api/stream
    Server->>Generator: tasks.stream(taskId)
    
    loop Real-time Updates
        Generator->>Server: yield { event: 'status', data }
        Server->>EventSource: event: status\ndata: {...}
        EventSource->>Hook: MessageEvent
        Hook->>Client: setStatus(data)
    end
    
    Generator->>Server: task finished
    Server->>EventSource: event: end
    EventSource->>Hook: close connection
```

**Server-Sent Events Flow**

The `gtos()` function [src/lib/nextjs/server/utils.ts:15-69]() converts task streaming generators into properly formatted Server-Sent Events, while the `useBrowserUse` hook [src/lib/nextjs/hooks/useBrowserUse.ts:10-37]() provides React integration with automatic connection management.

Sources: [src/lib/nextjs/server/utils.ts:15-69](), [src/lib/nextjs/hooks/useBrowserUse.ts:10-37]()

## Event Data Structures

All real-time communication uses consistent data structures for task status updates:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Task identifier |
| `status` | `TaskStatus` | Current execution state |
| `sessionId` | `string` | Browser session identifier |
| `steps` | `TaskStepView[]` | Execution steps with screenshots |
| `doneOutput` | `string` | Final task result |
| `metadata` | `Record<string, unknown>` | User-defined metadata |

The `TaskStatus` enum [src/resources/tasks.ts:466]() defines possible states: `started`, `paused`, `finished`, `stopped`.

For webhook events, the payload structure varies by event type but follows the `zWebhookSchema` discriminated union [src/lib/webhooks.ts:54-58]().

Sources: [src/resources/tasks.ts:511-587](), [src/lib/webhooks.ts:54-58]()

## Integration Patterns

The real-time features support multiple integration patterns:

1. **Direct Streaming**: Use `tasks.stream()` for command-line tools and Node.js applications
2. **Webhook Notifications**: Configure HTTP endpoints for server-to-server communication  
3. **React Applications**: Use `useBrowserUse()` hook with Server-Sent Events
4. **CLI Development**: Use `browser-use listen` command for local webhook forwarding

For specific implementation details, see [Task Streaming](#3.1), [Webhook System](#3.2), and [Next.js Integration](#3.3).

Sources: [src/resources/tasks.ts:174-192](), [src/lib/webhooks.ts:67-99](), [src/lib/nextjs/hooks/useBrowserUse.ts:10-37]()

---

