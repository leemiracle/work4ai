<!-- source: DeepWiki mcp.deepwiki.com · repo aannoo/hcom · page 8 Multi-Agent Communication · fetched 2026-10-26 -->

# Multi-Agent Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/bootstrap.rs](src/bootstrap.rs)
- [src/commands/send.rs](src/commands/send.rs)

</details>



This page provides a high-level overview of the multi-agent communication system in `hcom`, covering message routing, event subscriptions, context sharing via bundles, and instance forking. For detailed technical mechanics, implementation details, and edge cases, refer to the respective child pages.

## Message Flow Architecture

Messages flow through the SQLite `events` table, which serves as the central append-only log coordinating all agent communication [src/db.rs:5-11](). The `hcom send` command, managed via `SendArgs` [src/commands/send.rs:54-60](), facilitates this by logging a message event that is subsequently picked up by delivery threads.

For details on broadcast vs mentions scope, `@instance` addressing, cross-device routing, and `delivered_to` tracking, see [Message Scopes and Delivery Logic](#8.1).

Title: "Message Flow Pipeline: Natural Language to Code Entity Space"
```mermaid
graph TB
    Sender["Agent A<br/>(hcom send)"]
    SendCmd["SendArgs struct<br/>src/commands/send.rs:54-60"]
    LogEvent["HcomDb::log_event()<br/>src/db.rs"]
    EventsTable[("events table<br/>type='message'")]
    CheckSubs["check_event_subscriptions()<br/>src/db.rs"]
    SubsTable[("kv table<br/>key='events_sub:*'")]
    SendNotif["send_sub_notification()<br/>src/db.rs"]
    NotifyTable[("notify_endpoints<br/>TCP ports")]
    DeliveryThread["run_delivery_loop()<br/>src/delivery.rs"]
    GetUnread["get_unread_messages()<br/>src/db.rs"]
    ShouldDeliver["should_deliver_message()<br/>src/messages.rs"]
    Receiver["Agent B<br/>(PTY Injection)"]
    
    Sender --> SendCmd
    SendCmd --> LogEvent
    LogEvent --> EventsTable
    LogEvent --> CheckSubs
    CheckSubs --> SubsTable
    CheckSubs --> SendNotif
    SendNotif --> EventsTable
    NotifyTable --> DeliveryThread
    DeliveryThread --> GetUnread
    GetUnread --> EventsTable
    GetUnread --> ShouldDeliver
    ShouldDeliver --> Receiver
```
Sources: [src/db.rs:5-11](), [src/commands/send.rs:54-60](), [src/messages.rs:9-12](), [src/delivery.rs:1-12]()

## Event Subscriptions

Event subscriptions enable reactive patterns where agents automatically receive notifications when specific events occur. Subscriptions are stored in the `kv` table with keys prefixed `events_sub:` [src/db/subscriptions.rs:3-6]().

For details on subscription SQL filters, `--once` vs persistent subscriptions, request-watch policy, cancellation, and collision detection, see [Event Subscriptions](#8.2).

Title: "Subscription Lifecycle: Event State to Code Entities"
```mermaid
stateDiagram-v2
    [*] --> Created: "create_filter_subscription()"
    Created --> Active: "Stored in kv table"
    Active --> Matching: "New event logged"
    Matching --> Notification: "SQL filter matches"
    Notification --> Active: "Persistent subscription"
    Notification --> Removed: "once=true flag"
    Active --> Removed: "kv_set(key, None)"
    Removed --> [*]
```
Sources: [src/db/subscriptions.rs:1-23](), [src/db.rs:1855-1900]()

## Context Transfer via Bundles

Bundles are structured context packages for inter-agent handoffs. They aggregate files, transcript ranges, and event references into a single JSON object attached to messages [src/db.rs:70]().

For details on bundle structure (`title`, `description`, `refs`), bundle prepare workflow, inline vs explicit bundles, and detail levels, see [Bundles and Context Sharing](#8.3).

Title: "Bundle Structure: CLI Flags to JSON Code Entities"
```mermaid
graph LR
    Bundle["SendArgs::build_bundle_data()<br/>src/commands/send.rs:161-213"]
    Metadata["Metadata<br/>title, description, extends"]
    Refs["refs object"]
    Events["events[]<br/>Event ID ranges"]
    Files["files[]<br/>File paths"]
    Transcript["transcript[]<br/>Range:detail pairs"]
    
    Bundle --> Metadata
    Bundle --> Refs
    Refs --> Events
    Refs --> Files
    Refs --> Transcript
```
Sources: [src/commands/send.rs:161-213](), [src/db.rs:70]()

## Instance Forking and Subagents

Forking creates derivative instances that inherit session state from a parent. Subagents are task executors spawned by tools (e.g., Claude Code's Task tool).

For details on the `fork` command, subagent detection and registration, `parent_type_N` naming, and `running_tasks` tracking, see [Instance Forking and Subagents](#8.4).

Title: "Instance Hierarchy and Subagent Tracking"
```mermaid
graph TB
    Parent["luna<br/>session_id=sess-1"]
    Fork["luna_fork_1<br/>parent_session_id=sess-1"]
    Subagent1["luna_Task_1<br/>parent_name=luna"]
    Subagent2["luna_Task_2<br/>parent_name=luna"]
    
    Parent --> Fork
    Parent --> Subagent1
    Parent --> Subagent2
```
Sources: [src/db.rs:94-126](), [src/db.rs:1576-1595](), [src/instances.rs:22-44]()

---

