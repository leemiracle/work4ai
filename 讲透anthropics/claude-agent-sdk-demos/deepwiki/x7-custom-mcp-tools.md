<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-demos · extra page Custom MCP Tools · fetched 2026-10-26 -->

# Custom MCP Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [email-agent/README.md](email-agent/README.md)
- [email-agent/ccsdk/custom-tools.ts](email-agent/ccsdk/custom-tools.ts)
- [email-agent/ccsdk/email-agent-prompt.ts](email-agent/ccsdk/email-agent-prompt.ts)
- [email-agent/ccsdk/types.ts](email-agent/ccsdk/types.ts)
- [email-agent/client/components/message/AssistantMessage.tsx](email-agent/client/components/message/AssistantMessage.tsx)

</details>



## Purpose and Scope

This document covers the two custom MCP (Model Context Protocol) tools provided to the email agent for email operations: `search_inbox` and `read_emails`. These tools extend the Claude Agent SDK's built-in capabilities to enable domain-specific email querying and retrieval from the SQLite database via the IMAP integration layer.

For the agent's behavioral configuration and how these tools are described to the agent, see [Email Agent Prompt and Capabilities](#4.5.2). For the database and IMAP integration that these tools access, see [IMAP Integration and Email Sync](#4.3.2).

## Custom MCP Server Architecture

The email agent implements a custom MCP server using the SDK's `createSdkMcpServer` function to expose two domain-specific tools. The server is initialized at startup and provides tools that bridge the agent's natural language understanding with the underlying email database operations.

```mermaid
graph TB
    subgraph "Custom MCP Server Definition"
        Server["customServer<br/>(createSdkMcpServer)"]
        Config["Server Config<br/>name: 'email'<br/>version: '1.0.0'"]
        ToolsArray["tools: [...]"]
    end
    
    subgraph "Tool Definitions"
        SearchTool["search_inbox tool<br/>Gmail query syntax"]
        ReadTool["read_emails tool<br/>Fetch by IDs"]
    end
    
    subgraph "Tool Schemas"
        SearchSchema["Schema:<br/>gmailQuery: string"]
        ReadSchema["Schema:<br/>ids: string[]"]
    end
    
    subgraph "Tool Handlers"
        SearchHandler["async handler<br/>EmailAPI.searchEmails()"]
        ReadHandler["async handler<br/>EmailAPI.getEmailsByIds()"]
    end
    
    subgraph "Backend Integration"
        EmailAPI["EmailAPI class<br/>agent/email-api.ts"]
        DBManager["DatabaseManager<br/>SQLite queries"]
        ImapManager["ImapManager<br/>IMAP connection"]
    end
    
    subgraph "Output Artifacts"
        LogFile["logs/email-search-*.json<br/>Timestamped search logs"]
        JSONResponse["JSON response<br/>Formatted email data"]
    end
    
    Server --> Config
    Server --> ToolsArray
    ToolsArray --> SearchTool
    ToolsArray --> ReadTool
    
    SearchTool --> SearchSchema
    SearchTool --> SearchHandler
    ReadTool --> ReadSchema
    ReadTool --> ReadHandler
    
    SearchHandler --> EmailAPI
    ReadHandler --> EmailAPI
    EmailAPI --> DBManager
    EmailAPI --> ImapManager
    
    SearchHandler --> LogFile
    SearchHandler --> JSONResponse
    ReadHandler --> JSONResponse
```

**Sources:** [email-agent/ccsdk/custom-tools.ts:1-170]()

## Tool Definition: search_inbox

The `search_inbox` tool enables the agent to search emails using Gmail query syntax. It accepts a `gmailQuery` string parameter and returns matching emails up to a limit of 30 results.

### Schema Definition

```mermaid
graph LR
    Tool["tool()<br/>function call"]
    Name["name: 'search_inbox'"]
    Desc["description:<br/>'Search emails in the inbox<br/>using Gmail query syntax'"]
    Schema["input schema"]
    Param["gmailQuery: string<br/>Examples:<br/>- from:example@gmail.com<br/>- subject:invoice<br/>- newer_than:1y"]
    Handler["async handler function"]
    
    Tool --> Name
    Tool --> Desc
    Tool --> Schema
    Tool --> Handler
    Schema --> Param
```

The tool schema is defined using Zod validation at [email-agent/ccsdk/custom-tools.ts:28-36]():

- **Tool name:** `search_inbox`
- **Description:** Informs the agent this tool searches emails using Gmail query syntax
- **Input parameter:** `gmailQuery` (string) with examples showing the query format
- **Output:** JSON structure with `totalResults`, `logFilePath`, and a message

**Sources:** [email-agent/ccsdk/custom-tools.ts:28-36]()

### Handler Implementation

The handler executes a multi-step process:

```mermaid
graph TB
    Start["Handler invoked<br/>args.gmailQuery"]
    GetAPI["await getEmailAPI()<br/>Lazy load EmailAPI class"]
    CreateAPI["new EmailAPIClass()"]
    LogCall["console.log query<br/>for debugging"]
    
    Search["api.searchEmails()<br/>gmailQuery, limit: 30"]
    Format["Format results<br/>map to standardized structure"]
    ExtractIDs["Extract messageIds<br/>for reference"]
    
    CreateDir["Create logs/ directory<br/>if not exists"]
    GenFile["Generate filename<br/>email-search-{timestamp}.json"]
    WriteLog["fs.writeFileSync()<br/>Full email data + metadata"]
    
    ReturnJSON["Return JSON response<br/>totalResults, logFilePath"]
    ErrorHandler["Catch block<br/>Return error message"]
    
    Start --> GetAPI
    GetAPI --> CreateAPI
    CreateAPI --> LogCall
    LogCall --> Search
    Search --> Format
    Format --> ExtractIDs
    ExtractIDs --> CreateDir
    CreateDir --> GenFile
    GenFile --> WriteLog
    WriteLog --> ReturnJSON
    
    Search -.->|error| ErrorHandler
```

Key implementation details at [email-agent/ccsdk/custom-tools.ts:37-112]():

1. **Lazy API loading:** Uses `getEmailAPI()` to load the EmailAPI class only when needed, ensuring environment variables are loaded first [email-agent/ccsdk/custom-tools.ts:16-22]()

2. **Search execution:** Calls `api.searchEmails()` with the query and a hard-coded limit of 30 results [email-agent/ccsdk/custom-tools.ts:45-48]()

3. **Result formatting:** Maps raw email objects to a standardized structure including:
   - `index`, `id`, `messageId`
   - `date`, `from`, `to`, `subject`
   - `body` (full email content)
   - `hasAttachments`, `isRead`, `folder`, `labels`

4. **Log file generation:** Creates timestamped JSON files in `logs/` directory with full search results and metadata [email-agent/ccsdk/custom-tools.ts:69-89]()

5. **Response structure:** Returns only the log file path and count, not the full email data, keeping the tool response concise

**Sources:** [email-agent/ccsdk/custom-tools.ts:37-112]()

### Search Result Logging

Each search generates a timestamped log file with this structure:

| Field | Description |
|-------|-------------|
| `query` | Original Gmail query string |
| `timestamp` | ISO 8601 timestamp of search |
| `totalResults` | Number of emails found |
| `ids` | Array of messageId strings |
| `emails` | Full array of formatted email objects |

The log file naming convention is `email-search-{ISO-timestamp}.json` where colons and periods in the timestamp are replaced with hyphens [email-agent/ccsdk/custom-tools.ts:76-78]().

**Sources:** [email-agent/ccsdk/custom-tools.ts:81-89]()

## Tool Definition: read_emails

The `read_emails` tool retrieves full email details for specific message IDs. This is typically used after `search_inbox` to fetch complete content for selected emails.

### Schema Definition

```mermaid
graph LR
    Tool["tool()<br/>function call"]
    Name["name: 'read_emails'"]
    Desc["description:<br/>'Read multiple emails<br/>by their IDs'"]
    Schema["input schema"]
    Param["ids: string[]<br/>Array of messageIds<br/>e.g., ['&lt;abc123@example.com&gt;']"]
    Handler["async handler function"]
    
    Tool --> Name
    Tool --> Desc
    Tool --> Schema
    Tool --> Handler
    Schema --> Param
```

The tool schema at [email-agent/ccsdk/custom-tools.ts:115-120]():

- **Tool name:** `read_emails`
- **Description:** Explains this tool reads multiple emails by their IDs for full content
- **Input parameter:** `ids` (array of strings) - email message IDs in angle bracket format
- **Output:** JSON with `totalFetched` count and array of email objects

**Sources:** [email-agent/ccsdk/custom-tools.ts:115-120]()

### Handler Implementation

The read_emails handler follows a simpler pattern than search_inbox:

```mermaid
graph TB
    Start["Handler invoked<br/>args.ids"]
    GetAPI["await getEmailAPI()<br/>Lazy load"]
    CreateAPI["new EmailAPIClass()"]
    LogIDs["console.log IDs<br/>for debugging"]
    
    Fetch["api.getEmailsByIds(ids)<br/>Batch fetch from database"]
    Format["Format results<br/>Same structure as search_inbox"]
    
    ReturnJSON["Return JSON response<br/>totalFetched, emails array"]
    ErrorHandler["Catch block<br/>Return error message"]
    
    Start --> GetAPI
    GetAPI --> CreateAPI
    CreateAPI --> LogIDs
    LogIDs --> Fetch
    Fetch --> Format
    Format --> ReturnJSON
    
    Fetch -.->|error| ErrorHandler
```

Implementation details at [email-agent/ccsdk/custom-tools.ts:121-168]():

1. **API initialization:** Same lazy loading pattern as search_inbox

2. **Batch fetch:** Calls `api.getEmailsByIds()` with the array of IDs [email-agent/ccsdk/custom-tools.ts:129]()

3. **Result formatting:** Uses identical formatting structure as search_inbox for consistency [email-agent/ccsdk/custom-tools.ts:132-145]()

4. **Direct response:** Unlike search_inbox, returns email data directly in the tool response rather than via a log file

5. **No logging:** Does not create timestamped log files since the operation is deterministic

**Sources:** [email-agent/ccsdk/custom-tools.ts:121-168]()

## Tool Integration with EmailAPI

Both tools delegate to the `EmailAPI` class which provides an abstraction over the database layer:

```mermaid
graph TB
    subgraph "Custom Tools Layer"
        SearchTool["search_inbox tool"]
        ReadTool["read_emails tool"]
    end
    
    subgraph "API Abstraction"
        EmailAPI["EmailAPI class<br/>agent/email-api.ts"]
        SearchMethod["searchEmails()<br/>method"]
        GetMethod["getEmailsByIds()<br/>method"]
    end
    
    subgraph "Data Layer"
        DBManager["DatabaseManager<br/>SQLite operations"]
        ImapMgr["ImapManager<br/>IMAP connection"]
    end
    
    subgraph "Database Tables"
        EmailsTable["emails table<br/>FTS5 search support"]
        AttachmentsTable["attachments table"]
    end
    
    SearchTool --> EmailAPI
    ReadTool --> EmailAPI
    EmailAPI --> SearchMethod
    EmailAPI --> GetMethod
    
    SearchMethod --> DBManager
    GetMethod --> DBManager
    
    DBManager --> EmailsTable
    DBManager --> AttachmentsTable
    
    EmailAPI -.->|sync if needed| ImapMgr
```

The EmailAPI class is lazy-loaded through the `getEmailAPI()` helper function to ensure environment variables are properly loaded before instantiation [email-agent/ccsdk/custom-tools.ts:16-22](). This pattern prevents initialization errors when the custom-tools module is imported.

**Sources:** [email-agent/ccsdk/custom-tools.ts:14-22](), [email-agent/ccsdk/custom-tools.ts:39-41](), [email-agent/ccsdk/custom-tools.ts:123-125]()

## Tool Usage in Agent Workflow

The agent prompt explicitly instructs the AI on when and how to use these tools:

```mermaid
graph TB
    UserQuery["User query received"]
    
    Decision{"Query type?"}
    
    Search["Use search_inbox<br/>with Gmail query syntax"]
    ParseLog["Read log file<br/>from search results"]
    IdentifyIDs["Identify relevant<br/>email IDs"]
    
    Read["Use read_emails<br/>with selected IDs"]
    
    Format["Format response<br/>with [email:ID] references"]
    Display["Present to user"]
    
    UserQuery --> Decision
    Decision -->|"Search/filter"| Search
    Decision -->|"Read specific"| Read
    
    Search --> ParseLog
    ParseLog --> IdentifyIDs
    IdentifyIDs -->|"Need full content"| Read
    
    Read --> Format
    IdentifyIDs -->|"Summary sufficient"| Format
    Format --> Display
```

The agent prompt at [email-agent/ccsdk/email-agent-prompt.ts:1-36]() describes capabilities like:
- Searching by sender, subject, date, or content
- Finding emails with attachments
- Filtering by read/unread status
- Searching for specific email types (invoices, receipts, etc.)

When presenting results, the agent uses the `[email:MESSAGE_ID]` format which the client renders as clickable components [email-agent/ccsdk/email-agent-prompt.ts:31-33]().

**Sources:** [email-agent/ccsdk/email-agent-prompt.ts:1-36](), [email-agent/client/components/message/AssistantMessage.tsx:336-343]()

## Environment Configuration

The custom tools module loads environment variables explicitly to ensure database credentials are available:

| Configuration | Purpose |
|---------------|---------|
| `ANTHROPIC_API_KEY` | Required for Claude API access |
| `EMAIL_USER` | IMAP username |
| `EMAIL_PASSWORD` | IMAP password or app password |
| `IMAP_HOST` | IMAP server hostname |
| `IMAP_PORT` | IMAP server port |

The environment loading occurs at [email-agent/ccsdk/custom-tools.ts:7-9](), locating the `.env` file in the parent directory of the ccsdk module.

**Sources:** [email-agent/ccsdk/custom-tools.ts:7-9]()

## Tool Call Logging and Debugging

Both tools implement comprehensive console logging for debugging:

### search_inbox Logging

```
=== SEARCH INBOX TOOL CALLED ===
Query: from:boss@company.com newer_than:1d
================================
Wrote 5 emails to logs/email-search-2024-01-15T10-30-00-000Z.json
```

The logging pattern at [email-agent/ccsdk/custom-tools.ts:41-43]() and [email-agent/ccsdk/custom-tools.ts:91]() provides visibility into:
- Exact query string received
- Number of results found
- Output file path

### read_emails Logging

```
=== READ EMAILS TOOL CALLED ===
IDs: ['<abc123@example.com>', '<def456@example.com>']
================================
Fetched 2 emails
```

The logging at [email-agent/ccsdk/custom-tools.ts:125-127]() and [email-agent/ccsdk/custom-tools.ts:147]() tracks:
- List of IDs being fetched
- Count of successfully retrieved emails

These logs appear in the server console where the Bun runtime is executing and are essential for debugging agent tool usage patterns.

**Sources:** [email-agent/ccsdk/custom-tools.ts:41-43](), [email-agent/ccsdk/custom-tools.ts:91](), [email-agent/ccsdk/custom-tools.ts:125-127](), [email-agent/ccsdk/custom-tools.ts:147]()

## Error Handling

Both tools implement try-catch blocks that return formatted error responses to the agent:

```mermaid
graph TB
    ToolCall["Tool invoked"]
    TryBlock["try block<br/>Main handler logic"]
    
    Success["Return success response<br/>JSON with results"]
    
    CatchBlock["catch error"]
    LogError["console.error()<br/>Full error details"]
    ReturnError["Return error response<br/>text: 'Error: {message}'"]
    
    ToolCall --> TryBlock
    TryBlock -->|success| Success
    TryBlock -->|exception| CatchBlock
    CatchBlock --> LogError
    LogError --> ReturnError
```

Error responses follow the MCP protocol structure with a `content` array containing a text block with the error message [email-agent/ccsdk/custom-tools.ts:103-111](), [email-agent/ccsdk/custom-tools.ts:159-167](). This allows the agent to understand when operations fail and potentially retry or inform the user.

**Sources:** [email-agent/ccsdk/custom-tools.ts:103-111](), [email-agent/ccsdk/custom-tools.ts:159-167]()

---

