<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-demos · extra page IMAP Integration and Email Sync · fetched 2026-10-26 -->

# IMAP Integration and Email Sync

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [email-agent/bun.lock](email-agent/bun.lock)
- [email-agent/client/globals.css](email-agent/client/globals.css)
- [email-agent/database/database-manager.ts](email-agent/database/database-manager.ts)
- [email-agent/package.json](email-agent/package.json)
- [email-agent/server/endpoints/emails.ts](email-agent/server/endpoints/emails.ts)
- [email-agent/server/server.ts](email-agent/server/server.ts)
- [email-agent/tailwind.config.js](email-agent/tailwind.config.js)

</details>



## Purpose and Scope

This document details the IMAP integration layer and email synchronization mechanisms in the Email Agent demo. It covers the `ImapManager` singleton for IMAP server communication, the `EmailSyncService` for orchestrating synchronization between IMAP and SQLite, and the real-time IDLE monitoring system for new email notifications.

For information about the SQLite database schema and search operations, see [Schema and Models](#3.3.1). For details on how custom MCP tools use this layer to serve AI queries, see [Custom MCP Tools](#3.5.1).

---

## Architecture Overview

The IMAP integration implements a dual-source data strategy combining live IMAP access with local SQLite caching. The `ImapManager` handles direct IMAP server operations, while the `EmailSyncService` orchestrates data flow between IMAP and the database.

```mermaid
graph TB
    subgraph "IMAP Layer"
        ImapMgr["ImapManager<br/>(Singleton)"]
        NodeImap["node-imap<br/>Library"]
        MailParser["mailparser<br/>Library"]
    end
    
    subgraph "Sync Layer"
        SyncSvc["EmailSyncService"]
        EmailSearcher["EmailSearcher"]
    end
    
    subgraph "Data Layer"
        EmailDB["EmailDatabase"]
        SQLite[("emails.db<br/>SQLite")]
    end
    
    subgraph "External"
        IMAP["IMAP Server<br/>(Gmail)"]
        ListenersMgr["ListenersManager"]
    end
    
    ImapMgr -->|"connect()<br/>searchEmails()<br/>fetchEmail()"| NodeImap
    NodeImap <-->|"IMAP Protocol"| IMAP
    NodeImap -->|"raw email"| MailParser
    MailParser -->|"parsed email"| ImapMgr
    
    SyncSvc -->|"uses"| EmailSearcher
    EmailSearcher -->|"delegates"| ImapMgr
    SyncSvc -->|"insertEmail()"| EmailDB
    EmailDB -->|"SQL"| SQLite
    
    SyncSvc -->|"checkEvent()<br/>email_received"| ListenersMgr
    
    ImapMgr -.->|"IDLE events<br/>mail/update"| SyncSvc
    
    IMAP -.->|"IDLE push"| NodeImap
```

**Sources:** [email-agent/database/imap-manager.ts:1-61](), [email-agent/database/email-sync.ts:1-35]()

---

## ImapManager Class

### Singleton Pattern and Configuration

The `ImapManager` implements the singleton pattern to ensure a single IMAP connection per application instance. Configuration is sourced from environment variables or explicit constructor parameters.

```mermaid
graph LR
    Env["Environment Variables<br/>EMAIL_ADDRESS<br/>EMAIL_APP_PASSWORD<br/>IMAP_HOST<br/>IMAP_PORT"]
    Constructor["ImapManager.constructor()"]
    Config["ImapConfig<br/>user<br/>password<br/>host<br/>port<br/>tls<br/>keepalive"]
    Instance["ImapManager<br/>instance"]
    NodeImapClient["node-imap client"]
    
    Env -->|"process.env"| Constructor
    Constructor -->|"builds"| Config
    Constructor -->|"creates"| NodeImapClient
    Constructor -->|"stores"| Instance
    
    GetInstance["ImapManager.getInstance()"] -->|"returns"| Instance
```

The configuration includes keepalive settings for maintaining long-lived connections:

| Parameter | Default Value | Purpose |
|-----------|--------------|---------|
| `connTimeout` | 30000ms | Maximum connection establishment time |
| `authTimeout` | 30000ms | Maximum authentication time |
| `keepalive.interval` | 10000ms | Frequency of keepalive NOOPs |
| `keepalive.idleInterval` | 300000ms | Duration to maintain IDLE state |
| `keepalive.forceNoop` | true | Force NOOP even when IDLE available |

**Sources:** [email-agent/database/imap-manager.ts:17-68]()

---

### Connection Management

The `ImapManager` implements connection pooling with promise-based concurrency control to prevent multiple simultaneous connection attempts.

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: connect()
    Connecting --> Connected: ready event
    Connecting --> Disconnected: error event
    Connected --> Disconnected: end event
    Connected --> Disconnected: disconnect()
    Disconnected --> Connecting: reconnect()
    
    Connected --> OpeningMailbox: openMailbox(folder)
    OpeningMailbox --> MailboxOpen: success
    MailboxOpen --> Connected: operation complete
```

Connection lifecycle is managed through state tracking:

- `isConnected`: Boolean flag tracking connection state
- `connectionPromise`: Promise for deduplicating concurrent connection attempts
- `currentFolder`: Tracks currently opened mailbox for IDLE operations

**Sources:** [email-agent/database/imap-manager.ts:70-143]()

---

### Search Criteria and Gmail X-GM-RAW

The `buildImapSearchCriteria()` method converts `SearchCriteria` objects into IMAP search arrays. It prioritizes Gmail's native search syntax (`X-GM-RAW`) when available, enabling complex queries like `OR`, `has:attachment`, and date ranges.

```mermaid
graph TD
    SearchCriteria["SearchCriteria"]
    BuildMethod["buildImapSearchCriteria()"]
    GmailQuery{"gmailQuery<br/>present?"}
    XGM["['X-GM-RAW', query]"]
    Standard["Standard IMAP<br/>criteria array"]
    ImapSearch["IMAP search command"]
    
    SearchCriteria --> BuildMethod
    BuildMethod --> GmailQuery
    GmailQuery -->|"YES"| XGM
    GmailQuery -->|"NO"| Standard
    
    Standard -->|"from"| FromCriteria["['FROM', address]"]
    Standard -->|"to"| ToCriteria["['TO', address]"]
    Standard -->|"subject"| SubjectCriteria["['SUBJECT', text]"]
    Standard -->|"dateRange"| DateCriteria["['SINCE', date]<br/>['BEFORE', date]"]
    Standard -->|"isUnread"| UnseenCriteria["'UNSEEN'"]
    
    XGM --> ImapSearch
    FromCriteria --> ImapSearch
    ToCriteria --> ImapSearch
    SubjectCriteria --> ImapSearch
    DateCriteria --> ImapSearch
    UnseenCriteria --> ImapSearch
```

**Gmail X-GM-RAW Priority Example:**

When `criteria.gmailQuery` is provided, the method returns immediately with Gmail's native search syntax, bypassing standard IMAP criteria:

```
gmailQuery: "from:john@example.com OR from:jane@example.com has:attachment"
→ [['X-GM-RAW', 'from:john@example.com OR from:jane@example.com has:attachment']]
```

**Sources:** [email-agent/database/imap-manager.ts:145-221]()

---

### Parallel Email Fetching

The `fetchEmailsBatch()` method implements parallel fetching with configurable batch sizes to optimize throughput while managing memory constraints.

| Parameter | Default | Headers-Only Default | Purpose |
|-----------|---------|---------------------|---------|
| `batchSize` | 20 | 30 | Emails fetched per batch |
| Memory limit | 50MB | 50MB | Per-email size constraint |

```mermaid
sequenceDiagram
    participant Caller
    participant FetchBatch as "fetchEmailsBatch()"
    participant FetchEmail as "fetchEmail(uid)"
    participant IMAP as "IMAP Server"
    participant Parser as "mailparser"
    
    Caller->>FetchBatch: uids=[1,2,...,50], batchSize=20
    
    loop For each batch
        FetchBatch->>FetchBatch: slice(i, i+20)
        
        par Parallel fetch within batch
            FetchBatch->>FetchEmail: uid=1
            FetchEmail->>IMAP: fetch(1)
            IMAP-->>FetchEmail: raw email data
            FetchEmail->>Parser: simpleParser()
            Parser-->>FetchEmail: parsed email
            FetchEmail-->>FetchBatch: {uid:1, parsed}
        and
            FetchBatch->>FetchEmail: uid=2
            FetchEmail->>IMAP: fetch(2)
            IMAP-->>FetchEmail: raw email data
            FetchEmail->>Parser: simpleParser()
            Parser-->>FetchEmail: parsed email
            FetchEmail-->>FetchBatch: {uid:2, parsed}
        and
            Note over FetchBatch: ... up to 20 parallel
        end
        
        FetchBatch->>FetchBatch: Promise.all(batch)
    end
    
    FetchBatch-->>Caller: Map<uid, parsed>
```

**Sources:** [email-agent/database/imap-manager.ts:232-332](), [email-agent/database/imap-manager.ts:387-460]()

---

### IMAP IDLE Monitoring

The `startIdleMonitoring()` method enables push-based notifications for new emails using the IMAP IDLE extension. The system automatically handles connection errors and reconnection.

```mermaid
graph TB
    Start["startIdleMonitoring(folder, callback)"]
    EnsureConn["ensureConnection()"]
    OpenBox["openMailbox(folder, readOnly=true)"]
    SetFlag["isIdling = true"]
    
    subgraph "Event Listeners"
        MailEvent["imap.on('mail', count)"]
        UpdateEvent["imap.on('update', seqno)"]
        ErrorEvent["imap.on('error', err)"]
        CloseEvent["imap.on('close')"]
    end
    
    Callback["onNewEmailCallback(count)"]
    Reconnect["reconnect()"]
    Restart["startIdleMonitoring()"]
    
    Start --> EnsureConn
    EnsureConn --> OpenBox
    OpenBox --> SetFlag
    SetFlag --> MailEvent
    SetFlag --> UpdateEvent
    SetFlag --> ErrorEvent
    SetFlag --> CloseEvent
    
    MailEvent -->|"New email detected"| Callback
    ErrorEvent -->|"After 5s delay"| Reconnect
    Reconnect --> Restart
    CloseEvent -->|"isConnected = false"| Start
```

**IDLE Event Types:**

| Event | Trigger | Handler Action |
|-------|---------|----------------|
| `mail` | New message arrival | Invokes `onNewEmailCallback(count)` |
| `update` | Message flag change | Logs update with seqno |
| `error` | Connection/IDLE failure | Attempts reconnection after 5s |
| `close` | Connection closed | Resets connection state |

**Sources:** [email-agent/database/imap-manager.ts:504-577]()

---

### Email Actions

The `ImapManager` provides methods for email management operations that modify IMAP flags and mailbox locations:

```mermaid
graph LR
    subgraph "Flag Operations"
        MarkRead["markAsRead(uid)"]
        MarkUnread["markAsUnread(uid)"]
        Star["starEmail(uid)"]
        Unstar["unstarEmail(uid)"]
    end
    
    subgraph "Mailbox Operations"
        Archive["archiveEmail(uid)"]
        AddLabel["addLabel(uid, label)"]
        RemoveLabel["removeLabel(uid, label)"]
    end
    
    subgraph "IMAP Commands"
        AddFlags["imap.addFlags()"]
        DelFlags["imap.delFlags()"]
        Move["imap.move()"]
    end
    
    MarkRead -->|"['\\Seen']"| AddFlags
    MarkUnread -->|"['\\Seen']"| DelFlags
    Star -->|"['\\Flagged']"| AddFlags
    Unstar -->|"['\\Flagged']"| DelFlags
    
    Archive --> Move
    Move -->|"'[Gmail]/All Mail'"| IMAP["IMAP Server"]
    
    AddLabel -->|"['X-GM-LABELS', label]"| AddFlags
    RemoveLabel -->|"['X-GM-LABELS', label]"| DelFlags
    
    AddFlags --> IMAP
    DelFlags --> IMAP
```

All operations require opening the mailbox in read-write mode (`readOnly=false`). The methods are async and return promises that resolve when the IMAP server confirms the operation.

**Sources:** [email-agent/database/imap-manager.ts:579-723]()

---

## EmailSyncService Class

### Synchronization Workflow

The `EmailSyncService` orchestrates data flow from IMAP to SQLite, handling email parsing, recipient extraction, attachment metadata, and listener notifications.

```mermaid
sequenceDiagram
    participant Caller
    participant SyncSvc as "EmailSyncService"
    participant Searcher as "EmailSearcher"
    participant ImapMgr as "ImapManager"
    participant Parser as "Email Parser"
    participant DB as "EmailDatabase"
    participant Listeners as "ListenersManager"
    
    Caller->>SyncSvc: syncEmails(options)
    SyncSvc->>Searcher: connect()
    Searcher->>ImapMgr: connect()
    
    SyncSvc->>Searcher: openFolder(folder)
    SyncSvc->>Searcher: searchEmails(criteria)
    Searcher->>ImapMgr: searchMailbox()
    ImapMgr-->>Searcher: uids[]
    Searcher-->>SyncSvc: uids[]
    
    loop For each UID
        SyncSvc->>Searcher: fetchEmail(uid)
        Searcher->>ImapMgr: fetchEmail(uid)
        ImapMgr-->>Searcher: rawEmail
        Searcher-->>SyncSvc: rawEmail
        
        SyncSvc->>DB: SELECT by message_id
        alt Email exists
            DB-->>SyncSvc: existing record
            Note over SyncSvc: stats.skipped++
        else Email new
            SyncSvc->>Parser: parseEmailAddress()
            Parser-->>SyncSvc: addresses
            SyncSvc->>Parser: extractRecipients()
            Parser-->>SyncSvc: recipients[]
            SyncSvc->>Parser: extractAttachments()
            Parser-->>SyncSvc: attachments[]
            
            SyncSvc->>DB: insertEmail(record, recipients, attachments)
            DB-->>SyncSvc: emailId
            
            SyncSvc->>Listeners: checkEvent('email_received', email)
            Note over SyncSvc: stats.synced++
        end
    end
    
    SyncSvc->>Searcher: disconnect()
    SyncSvc-->>Caller: {synced, skipped, errors}
```

**Sources:** [email-agent/database/email-sync.ts:171-354]()

---

### Email Parsing and Extraction

The `EmailSyncService` implements three extraction methods that transform parsed email objects into normalized database records:

#### parseEmailAddress()

Parses RFC-compliant email address strings including display names:

```
Input: "John Doe <john@example.com>, jane@example.com"
Output: [
  {address: "john@example.com", name: "John Doe"},
  {address: "jane@example.com"}
]
```

#### extractRecipients()

Processes `to`, `cc`, and `bcc` fields from parsed emails, handling both structured (`value` arrays) and string formats:

```mermaid
graph TD
    Parsed["parsed email"]
    ExtractRecip["extractRecipients(parsed, emailId)"]
    
    ToField["parsed.to"]
    CcField["parsed.cc"]
    BccField["parsed.bcc"]
    
    CheckType{"Array or<br/>string?"}
    ValueArray["to.value[]"]
    StringParse["parseEmailAddress()"]
    
    Recipients["recipients[]<br/>{email_id, type, address, name}"]
    
    Parsed --> ExtractRecip
    ExtractRecip --> ToField
    ExtractRecip --> CcField
    ExtractRecip --> BccField
    
    ToField --> CheckType
    CheckType -->|"has .value"| ValueArray
    CheckType -->|"string"| StringParse
    
    ValueArray --> Recipients
    StringParse --> Recipients
```

#### extractAttachments()

Extracts attachment metadata from `parsed.attachments`:

```typescript
{
  email_id: number,
  filename: string,
  content_type: string,
  size_bytes: number,
  content_id?: string,      // For inline images
  is_inline: boolean        // contentDisposition === "inline"
}
```

**Sources:** [email-agent/database/email-sync.ts:37-168]()

---

### IDLE Integration and Event Handling

The `handleIdleNewEmails()` method processes new email notifications from IMAP IDLE:

```mermaid
graph TD
    IdleEvent["IMAP IDLE 'mail' event<br/>count=N"]
    Handler["handleIdleNewEmails(count, folder)"]
    SyncCall["syncEmails(options)"]
    
    Options["SyncOptions:<br/>folder=INBOX<br/>limit=count+5<br/>since=now-60s"]
    
    Result["Sync result:<br/>{synced, skipped, errors}"]
    Listeners["ListenersManager<br/>email_received events"]
    
    IdleEvent -->|"onNewEmailCallback()"| Handler
    Handler --> SyncCall
    SyncCall --> Options
    Options -->|"Buffer for race conditions"| SyncCall
    SyncCall -->|"Per-email"| Listeners
    SyncCall --> Result
```

**Buffer Strategy:**

- `limit = count + 5`: Accounts for potential race conditions
- `since = now - 60s`: 1-minute lookback window to catch timing issues

The method is called by the `ImapManager`'s `onNewEmailCallback` during IDLE monitoring. Each synced email triggers a `checkEvent('email_received', email)` call to the `ListenersManager`.

**Sources:** [email-agent/database/email-sync.ts:368-384](), [email-agent/database/imap-manager.ts:519-524]()

---

## Data Flow: Complete Sync Cycle

The following diagram shows the complete data flow from IMAP server to SQLite database with all transformation steps:

```mermaid
graph TB
    IMAP["IMAP Server<br/>(Gmail)"]
    
    subgraph "IMAP Layer"
        Search["ImapManager.searchEmails()<br/>→ UIDs"]
        Fetch["ImapManager.fetchEmailsBatch()<br/>→ Raw email data"]
        Parse["mailparser.simpleParser()<br/>→ Parsed email object"]
    end
    
    subgraph "Sync Layer"
        Transform["EmailSyncService"]
        ParseAddr["parseEmailAddress()"]
        ExtractRecip["extractRecipients()"]
        ExtractAttach["extractAttachments()"]
    end
    
    subgraph "Database Layer"
        Insert["EmailDatabase.insertEmail()"]
        EmailTable[("emails table")]
        RecipTable[("recipients table")]
        AttachTable[("attachments table")]
        FTS[("emails_fts table")]
    end
    
    subgraph "Event Layer"
        ListenerCheck["ListenersManager.checkEvent()<br/>'email_received'"]
        Listeners["Active listeners"]
    end
    
    IMAP -->|"IMAP protocol"| Search
    Search -->|"UIDs"| Fetch
    Fetch -->|"Raw bytes"| Parse
    
    Parse -->|"Parsed email"| Transform
    Transform --> ParseAddr
    Transform --> ExtractRecip
    Transform --> ExtractAttach
    
    ParseAddr --> Insert
    ExtractRecip --> Insert
    ExtractAttach --> Insert
    
    Insert -->|"EmailRecord"| EmailTable
    Insert -->|"Recipient[]"| RecipTable
    Insert -->|"Attachment[]"| AttachTable
    Insert -.->|"Trigger"| FTS
    
    Insert -->|"Email object"| ListenerCheck
    ListenerCheck --> Listeners
```

**Sources:** [email-agent/database/imap-manager.ts:387-460](), [email-agent/database/email-sync.ts:252-333](), [email-agent/database/email-db.ts:216-329]()

---

## Configuration and Environment Variables

The IMAP integration requires the following environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_ADDRESS` or `EMAIL_USER` | Yes | - | IMAP account username |
| `EMAIL_APP_PASSWORD` or `EMAIL_PASS` | Yes | - | IMAP account password (app-specific for Gmail) |
| `IMAP_HOST` | No | `imap.gmail.com` | IMAP server hostname |
| `IMAP_PORT` | No | `993` | IMAP server port |

**Gmail App Password Setup:**

For Gmail accounts with 2FA enabled, generate an app-specific password at https://myaccount.google.com/apppasswords. The standard account password will not work with IMAP.

**Sources:** [email-agent/database/imap-manager.ts:28-58]()

---

