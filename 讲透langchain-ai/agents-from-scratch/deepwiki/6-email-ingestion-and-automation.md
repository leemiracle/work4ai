<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agents-from-scratch · page 6 Email Ingestion and Automation · fetched 2026-10-26 -->

# Email Ingestion and Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/email_assistant/tools/gmail/README.md](src/email_assistant/tools/gmail/README.md)
- [src/email_assistant/tools/gmail/run_ingest.py](src/email_assistant/tools/gmail/run_ingest.py)
- [src/email_assistant/tools/gmail/setup_gmail.py](src/email_assistant/tools/gmail/setup_gmail.py)

</details>



## Purpose and Scope

This page documents the automated email ingestion system that fetches emails from Gmail and routes them to the LangGraph email assistant for processing. The ingestion system handles Gmail API integration, email filtering, thread management, and optional cron-based automation.

For information about the Gmail API tools used by the assistant itself (send email, schedule meeting, etc.), see [Gmail Integration](#3.4). This page focuses specifically on the **ingestion** side: how emails are discovered, filtered, and fed into the system for processing.

## System Overview

The email ingestion system consists of three main components:

1. **`run_ingest.py`** - Command-line script for fetching and processing emails
2. **Gmail API Integration** - OAuth-authenticated access to Gmail search and retrieval
3. **LangGraph SDK Integration** - Creates threads and runs for each email

```mermaid
flowchart TB
    User["User invokes<br/>run_ingest.py"]
    CLI["CLI Arguments<br/>--email<br/>--minutes-since<br/>--include-read"]
    
    User --> CLI
    CLI --> SearchQuery["Gmail Search Query<br/>to:EMAIL OR from:EMAIL<br/>after:TIMESTAMP<br/>is:unread"]
    
    SearchQuery --> GmailAPI["Gmail API<br/>messages.list()"]
    
    GmailAPI --> Messages["Message IDs<br/>[msg1, msg2, ...]"]
    
    Messages --> Loop["For each message"]
    
    Loop --> FetchThread["Fetch Thread<br/>messages.get()"]
    FetchThread --> Extract["extract_email_data()<br/>headers, content"]
    
    Extract --> Filter{"Apply Filters<br/>unread?<br/>sender?<br/>latest?"}
    
    Filter -->|skip| Next["Next Message"]
    Filter -->|process| ThreadID["Generate thread_id<br/>MD5 hash of Gmail thread ID"]
    
    ThreadID --> LGClient["LangGraph SDK<br/>get_client()"]
    
    LGClient --> CreateThread["threads.create()<br/>or threads.get()"]
    CreateThread --> CleanupRuns["Delete previous runs<br/>runs.delete()"]
    CleanupRuns --> CreateRun["runs.create()<br/>with email_input"]
    
    CreateRun --> Next
    Next --> Loop
    
    CreateRun --> HITL["Agent processes email<br/>with HITL + Memory"]
```

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:1-341](), [src/email_assistant/tools/gmail/README.md:184-280]()

## The run_ingest.py Script

### Core Functionality

The `run_ingest.py` script serves as the primary entry point for email ingestion. It authenticates with Gmail, searches for relevant emails, applies filtering rules, and submits each email to the LangGraph server.

**Key Functions:**

| Function | Purpose | Lines |
|----------|---------|-------|
| `load_gmail_credentials()` | Loads OAuth credentials from `token.json` or `GMAIL_TOKEN` env var | [61-113]() |
| `extract_message_part()` | Recursively extracts email content from MIME parts, preferring text/plain | [30-59]() |
| `extract_email_data()` | Parses message headers and body into structured format | [115-139]() |
| `ingest_email_to_langgraph()` | Creates LangGraph thread and run for an email | [141-202]() |
| `fetch_and_process_emails()` | Main orchestration function | [204-284]() |

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:1-341]()

### Command-Line Parameters

The script accepts several parameters that control email fetching and filtering behavior:

```bash
python src/email_assistant/tools/gmail/run_ingest.py \
  --email user@example.com \
  --minutes-since 120 \
  --graph-name email_assistant_hitl_memory_gmail \
  --url http://127.0.0.1:2024 \
  --include-read \
  --early
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--email` | string | **required** | Email address to fetch messages for |
| `--minutes-since` | int | 120 | Only retrieve emails newer than N minutes |
| `--graph-name` | string | `email_assistant_hitl_memory_gmail` | LangGraph graph to invoke |
| `--url` | string | `http://127.0.0.1:2024` | LangGraph deployment URL |
| `--include-read` | flag | false | Process read emails (default: unread only) |
| `--early` | flag | false | Stop after processing first email |
| `--rerun` | flag | false | Reprocess previously processed emails |
| `--skip-filters` | flag | false | Bypass sender and thread-position filters |

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:286-334](), [src/email_assistant/tools/gmail/README.md:78-96]()

## Gmail Search Query Construction

The script constructs Gmail API search queries dynamically based on CLI parameters:

```mermaid
flowchart LR
    Email["--email<br/>user@example.com"] --> Base["to:user@example.com<br/>OR from:user@example.com"]
    
    Minutes["--minutes-since 120"] --> After["after:UNIX_TIMESTAMP"]
    
    IncludeRead["--include-read<br/>(flag absent)"] --> Unread["is:unread"]
    
    Base --> Query["Final Query"]
    After --> Query
    Unread --> Query
    
    Query --> Example["Example:<br/>'to:user@example.com OR from:user@example.com<br/>after:1745432245 is:unread'"]
```

The query assembly happens in `fetch_and_process_emails()`:

```python
# Construct Gmail search query
query = f"to:{email_address} OR from:{email_address}"

# Add time constraint if specified
if args.minutes_since > 0:
    from datetime import timedelta
    after = int((datetime.now() - timedelta(minutes=args.minutes_since)).timestamp())
    query += f" after:{after}"
    
# Only include unread emails unless include_read is True
if not args.include_read:
    query += " is:unread"
```

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:222-234](), [src/email_assistant/tools/gmail/README.md:189-205]()

## Email Filtering Logic

The ingestion system applies multiple layers of filtering to determine which emails should be processed:

### Three-Stage Filter Pipeline

```mermaid
flowchart TD
    Start["Email found<br/>in search results"]
    
    Start --> Unread{"Stage 1:<br/>Unread Filter"}
    Unread -->|"is:unread in query<br/>(unless --include-read)"| Stage2["Stage 2:<br/>Sender Filter"]
    Unread -->|excluded by search| Skip1["Skip"]
    
    Stage2 --> SenderCheck{"Email from<br/>your address?"}
    SenderCheck -->|yes| Skip2["Skip<br/>(unless --skip-filters)"]
    SenderCheck -->|no| Stage3["Stage 3:<br/>Thread Position Filter"]
    
    Stage3 --> PositionCheck{"Is latest message<br/>in thread?"}
    PositionCheck -->|no| Skip3["Skip<br/>(unless --skip-filters)"]
    PositionCheck -->|yes| Process["Process Email"]
    
    SkipFilters["--skip-filters flag"] -.->|bypasses| SenderCheck
    SkipFilters -.->|bypasses| PositionCheck
```

**Filter Details:**

| Filter | Default Behavior | Override | Implementation |
|--------|-----------------|----------|----------------|
| **Unread** | Only unread emails | `--include-read` | Gmail search query: `is:unread` |
| **Sender** | Skip emails from your address | `--skip-filters` | Check if email address in From header |
| **Thread Position** | Only latest message in thread | `--skip-filters` | Compare message ID with thread's last message |

**Important:** The `--skip-filters` flag does NOT bypass the unread filter. To process read messages, you must use `--include-read`.

**Sources:** [src/email_assistant/tools/gmail/README.md:219-267]()

## Thread Management and Deduplication

### Thread ID Mapping

The system maps Gmail thread IDs to deterministic UUIDs for use as LangGraph thread identifiers:

```mermaid
flowchart LR
    Gmail["Gmail Thread ID<br/>String: '18f3e2a1b2c3d4e5'"]
    
    Gmail --> Hash["MD5 Hash<br/>hashlib.md5"]
    Hash --> Hex["32-character hex<br/>'a1b2c3d4e5...'"]
    Hex --> UUID["UUID<br/>uuid.UUID(hex=...)"]
    
    UUID --> LG["LangGraph thread_id<br/>'a1b2c3d4-e5f6-...'"]
```

**Implementation:**

```python
def ingest_email_to_langgraph(email_data, graph_name, url="http://127.0.0.1:2024"):
    # Create a consistent UUID for the thread
    raw_thread_id = email_data["thread_id"]
    thread_id = str(
        uuid.UUID(hex=hashlib.md5(raw_thread_id.encode("UTF-8")).hexdigest())
    )
    print(f"Gmail thread ID: {raw_thread_id} → LangGraph thread ID: {thread_id}")
```

This ensures that:
- Multiple emails in the same Gmail thread map to the same LangGraph thread
- The mapping is deterministic (same input → same output)
- Thread IDs are valid UUIDs

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:146-150]()

### Run Cleanup and State Management

When processing an email for an existing thread, the script cleans up previous runs to avoid state accumulation:

```mermaid
flowchart TD
    CheckThread["Check if thread exists<br/>client.threads.get()"]
    
    CheckThread -->|exists| ListRuns["List all runs<br/>client.runs.list()"]
    CheckThread -->|new| CreateThread["Create thread<br/>client.threads.create()"]
    
    ListRuns --> DeleteLoop["For each run"]
    DeleteLoop --> DeleteRun["Delete run<br/>client.runs.delete()"]
    
    DeleteRun --> UpdateMeta["Update metadata<br/>threads.update()"]
    CreateThread --> UpdateMeta
    
    UpdateMeta --> CreateRun["Create new run<br/>runs.create()"]
    CreateRun --> Input["Input: email_input dict<br/>from, to, subject, body"]
```

**Key Operations:**

1. **Check Thread Existence** - [src/email_assistant/tools/gmail/run_ingest.py:154-162]()
2. **Cleanup Previous Runs** - [src/email_assistant/tools/gmail/run_ingest.py:165-179]()
3. **Update Metadata** - [src/email_assistant/tools/gmail/run_ingest.py:182]()
4. **Create Fresh Run** - [src/email_assistant/tools/gmail/run_ingest.py:187-198]()

The `multitask_strategy="rollback"` parameter ensures that if a new email arrives while the agent is processing a previous one, the new run rolls back the old one rather than running concurrently.

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:141-202]()

## Email Data Extraction

The script extracts structured email data from Gmail's API response:

```mermaid
flowchart TD
    Message["Gmail Message Object<br/>messages.get() response"]
    
    Message --> Headers["Parse Headers<br/>payload.headers"]
    Message --> Body["Extract Body<br/>extract_message_part()"]
    
    Headers --> Subject["Subject"]
    Headers --> From["From"]
    Headers --> To["To"]
    Headers --> Date["Date"]
    
    Body --> Content["page_content"]
    
    Subject --> EmailData["email_data dict"]
    From --> EmailData
    To --> EmailData
    Date --> EmailData
    Content --> EmailData
    
    Message --> IDs["Message/Thread IDs"]
    IDs --> EmailData
    
    EmailData --> Format["{<br/>'from_email': ...,<br/>'to_email': ...,<br/>'subject': ...,<br/>'page_content': ...,<br/>'id': ...,<br/>'thread_id': ...,<br/>'send_time': ...<br/>}"]
```

### MIME Part Extraction

The `extract_message_part()` function handles complex multipart MIME structures with a priority system:

1. **Prefer text/plain** - Most readable format
2. **Fallback to text/html** - If no plain text available
3. **Recursive search** - Navigate nested multipart structures

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:30-59](), [src/email_assistant/tools/gmail/run_ingest.py:115-139]()

## Cron Job Automation

For production deployments, the system supports scheduled ingestion via cron jobs.

### Cron Architecture

```mermaid
flowchart TD
    Setup["setup_cron.py<br/>One-time setup script"]
    
    Setup --> SDK["LangGraph SDK<br/>client.crons.create()"]
    
    SDK --> CronJob["Cron Job<br/>Scheduled in LangGraph Platform"]
    
    CronJob -->|"triggers every N minutes"| CronGraph["cron.py graph<br/>Simple wrapper graph"]
    
    CronGraph --> Invoke["Invokes fetch_and_process_emails()"]
    
    Invoke --> RunIngest["Same logic as run_ingest.py"]
    
    RunIngest --> Emails["Fetches and processes emails"]
```

**Sources:** [src/email_assistant/tools/gmail/README.md:136-182]()

### Setting Up a Cron Job

```bash
python src/email_assistant/tools/gmail/setup_cron.py \
  --email user@example.com \
  --url https://your-deployment.us.langgraph.app \
  --schedule "*/10 * * * *" \
  --minutes-since 60
```

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--email` | **required** | Email address to monitor |
| `--url` | **required** | LangGraph deployment URL |
| `--schedule` | `"*/10 * * * *"` | Cron expression (every 10 minutes) |
| `--minutes-since` | 60 | Time window for email fetching |
| `--graph-name` | `email_assistant_hitl_memory_gmail` | Graph to use |
| `--include-read` | false | Include read emails |

### Cron Implementation Components

The cron system consists of two files:

1. **`src/email_assistant/cron.py`** - Defines a LangGraph graph that wraps the ingestion logic
2. **`src/email_assistant/tools/gmail/setup_cron.py`** - Creates the scheduled job via SDK

**Managing Cron Jobs:**

```python
from langgraph_sdk import get_client

client = get_client(url="https://your-deployment.us.langgraph.app")

# List all cron jobs
cron_jobs = await client.crons.list()

# Delete a cron job
await client.crons.delete(cron_job_id)
```

**Sources:** [src/email_assistant/tools/gmail/README.md:156-182]()

## Deployment Modes

The ingestion system supports two deployment modes with different setup requirements:

### Local Development

For local development with `langgraph dev`:

```bash
# Terminal 1: Start LangGraph server
langgraph dev

# Terminal 2: Run ingestion
python src/email_assistant/tools/gmail/run_ingest.py \
  --email user@example.com \
  --minutes-since 1000 \
  --url http://127.0.0.1:2024
```

**Requirements:**
- Local `token.json` file in `.secrets/` directory
- LangGraph server running on port 2024
- Can process emails interactively

**Sources:** [src/email_assistant/tools/gmail/README.md:58-97]()

### Hosted Deployment

For production deployments on LangGraph Platform:

```bash
# One-time setup: Deploy graph to platform (via LangSmith UI)
# Set environment variables:
#   GMAIL_TOKEN - Full contents of token.json
#   GMAIL_SECRET - Full contents of secrets.json
#   OPENAI_API_KEY

# Run ingestion against hosted deployment
python src/email_assistant/tools/gmail/run_ingest.py \
  --email user@example.com \
  --minutes-since 120 \
  --url https://your-deployment.us.langgraph.app

# Or set up automated cron job
python src/email_assistant/tools/gmail/setup_cron.py \
  --email user@example.com \
  --url https://your-deployment.us.langgraph.app
```

**Requirements:**
- Deployed graph on LangGraph Platform
- Environment variables set in deployment config
- Optional: Cron job for continuous monitoring

**Sources:** [src/email_assistant/tools/gmail/README.md:105-154]()

## Authentication Setup

Before running ingestion, OAuth credentials must be configured:

### Initial Setup Process

```mermaid
flowchart TD
    Console["Google Cloud Console"]
    
    Console --> EnableAPIs["Enable APIs:<br/>Gmail API<br/>Calendar API"]
    EnableAPIs --> CreateOAuth["Create OAuth Client ID<br/>Application Type: Desktop"]
    CreateOAuth --> Download["Download secrets.json"]
    
    Download --> Place["Place in .secrets/secrets.json"]
    
    Place --> RunSetup["python setup_gmail.py"]
    
    RunSetup --> Browser["Browser window opens<br/>for authorization"]
    Browser --> Grant["User grants permissions"]
    Grant --> TokenSaved["token.json saved<br/>in .secrets/"]
    
    TokenSaved --> UseLocal["Use locally<br/>with run_ingest.py"]
    TokenSaved --> EnvVar["Or set GMAIL_TOKEN<br/>for hosted deployment"]
```

The `setup_gmail.py` script handles the OAuth flow:

1. Reads client configuration from `.secrets/secrets.json`
2. Initiates OAuth flow with required scopes (Gmail + Calendar)
3. Opens browser for user authorization
4. Saves access/refresh tokens to `.secrets/token.json`

**Required Scopes:**
- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/calendar`

**Sources:** [src/email_assistant/tools/gmail/setup_gmail.py:1-87](), [src/email_assistant/tools/gmail/README.md:11-56]()

## Credential Loading

The `load_gmail_credentials()` function supports multiple credential sources:

```mermaid
flowchart TD
    Load["load_gmail_credentials()"]
    
    Load --> TryEnv["Try GMAIL_TOKEN<br/>environment variable"]
    
    TryEnv -->|found| ParseEnv["json.loads(env_var)"]
    TryEnv -->|not found| TryFile["Try .secrets/token.json<br/>local file"]
    
    TryFile -->|found| LoadFile["json.load(file)"]
    TryFile -->|not found| Failed["Return None"]
    
    ParseEnv --> CreateCreds["Create Credentials object"]
    LoadFile --> CreateCreds
    
    CreateCreds --> Return["Return credentials"]
```

This dual-source approach enables:
- **Local development**: Use `token.json` file
- **Hosted deployment**: Use `GMAIL_TOKEN` environment variable

**Sources:** [src/email_assistant/tools/gmail/run_ingest.py:61-113]()

## Gmail API Limitations

The ingestion system must work within Gmail API constraints:

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Search-based retrieval** | No direct "get all emails" endpoint | Use comprehensive search queries |
| **Indexing lag** | Very recent emails may not appear in search | Use `--minutes-since` with buffer time |
| **Two-stage process** | Search returns IDs, then fetch full messages | Script handles both stages automatically |
| **Thread complexity** | Must fetch entire thread to get context | Script fetches full thread for each message |
| **Search result incompleteness** | Search may not return all matching emails | Use broader time windows when troubleshooting |

**Troubleshooting Missing Emails:**

```bash
# Most comprehensive search - processes everything
python run_ingest.py \
  --email user@example.com \
  --minutes-since 10000 \
  --include-read \
  --skip-filters
```

**Sources:** [src/email_assistant/tools/gmail/README.md:268-280](), [src/email_assistant/tools/gmail/README.md:89-96]()

---

