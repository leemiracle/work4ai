<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-security-bots · page 6 Triage Slackbot · fetched 2026-10-26 -->

# Triage Slackbot

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bots/triage-slackbot/README.md](bots/triage-slackbot/README.md)
- [bots/triage-slackbot/triage_slackbot/bot.py](bots/triage-slackbot/triage_slackbot/bot.py)

</details>



## Purpose and Scope

The Triage Slackbot provides automated categorization and routing of inbound security requests within Slack channels. It leverages OpenAI's function calling API to analyze incoming messages and direct them to appropriate sub-teams or provide automatic responses based on configurable categories and routing rules.

This document covers the triage bot's architecture, AI-powered categorization system, configuration options, and operational workflows. For information about the shared infrastructure used across all security bots, see [Shared Components](#3). For details about other security bots in the system, see [SDLC Slackbot](#4) and [Incident Response Slackbot](#5).

## System Architecture

The Triage Slackbot operates as part of the broader openai-security-bots ecosystem, sharing common infrastructure while providing specialized request routing functionality. The bot is initialized using the shared `start_bot` entrypoint [bots/triage-slackbot/triage_slackbot/bot.py:4-4](), which configures the Slack handlers and Jinja2 templates.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Triage Bot Components [bots/triage-slackbot/triage_slackbot/]"
        TriageBot["bot.py"]
        ConfigLoader["config.py"]
        Handlers["handlers.py"]
    end
    
    subgraph "Shared Infrastructure [shared/openai-slackbot/]"
        SharedBot["openai_slackbot.bot"]
    end
    
    subgraph "External Services"
        SlackAPI["Slack API"]
        OpenAIAPI["OpenAI API<br/>Function Calling"]
    end
    
    subgraph "Slack Channels"
        InboundChannel["inbound_request_channel_id"]
        FeedChannel["feed_channel_id"] 
        CategoryChannels["Category-specific channels"]
        DirectMessages["Direct messages to oncall users"]
    end
    
    TriageBot --> SharedBot
    TriageBot --> ConfigLoader
    TriageBot --> Handlers
    
    SharedBot --> SlackAPI
    SharedBot --> OpenAIAPI
    
    SlackAPI --> InboundChannel
    SlackAPI --> FeedChannel
    SlackAPI --> CategoryChannels
    SlackAPI --> DirectMessages
    
    InboundChannel --> TriageBot
    TriageBot --> FeedChannel
    TriageBot --> CategoryChannels
    TriageBot --> DirectMessages
```

**Sources:** [bots/triage-slackbot/README.md:1-99](), [bots/triage-slackbot/triage_slackbot/bot.py:1-37]()

### Core Workflow Process

The bot utilizes a single message handler, `InboundRequestHandler`, to process new posts and several action handlers to manage user interactions in the feed [bots/triage-slackbot/triage_slackbot/bot.py:18-24]().

```mermaid
sequenceDiagram
    participant User
    participant InboundChannel as "Inbound Channel"
    participant TriageBot as "InboundRequestHandler"
    participant OpenAI as "OpenAI Function Calling"
    participant FeedChannel as "Feed Channel"
    participant OnCall as "OnCall Team/User"
    
    User->>InboundChannel: "Posts security request"
    InboundChannel->>TriageBot: "Message event"
    TriageBot->>OpenAI: "Categorize request with function calling"
    OpenAI->>TriageBot: "Returns category prediction"
    TriageBot->>FeedChannel: "Posts categorization with action buttons"
    
    alt Auto-response category
        TriageBot->>InboundChannel: "Posts automatic response"
        TriageBot->>User: "Marks as handled"
    else Manual routing required
        OnCall->>FeedChannel: "Acknowledges or re-routes"
        TriageBot->>OnCall: "Routes to appropriate channel/DM"
        TriageBot->>InboundChannel: "Confirms routing action"
    end
```

**Sources:** [bots/triage-slackbot/README.md:79-98](), [bots/triage-slackbot/triage_slackbot/bot.py:18-24]()

## Request Categorization System

The triage bot uses OpenAI's function calling API to provide deterministic categorization of inbound requests, enabling consistent routing decisions. For deep technical details on the categorization logic and fallback mechanisms, see [AI-Powered Request Categorization](#6.1).

### Category Configuration Structure

| Configuration Element | Purpose | Example Values |
|----------------------|---------|----------------|
| `key` | Category identifier | `"appsec"`, `"privacy"` |
| `oncall_slack_id` | Routing destination | Channel ID or user ID |
| `auto_respond` | Enable automatic responses | `true`/`false` |
| `other_category_enabled` | Allow manual re-routing | `true`/`false` |

### Category Definition Example

```mermaid
graph LR
    subgraph "Category: appsec"
        AppSecKey["key = 'appsec'"]
        AppSecChannel["oncall_slack_id = '#appsec-requests'"]
        AppSecAuto["auto_respond = false"]
    end
    
    subgraph "Category: privacy"
        PrivacyKey["key = 'privacy'"]
        PrivacyUser["oncall_slack_id = '@tiffany'"]
        PrivacyAuto["auto_respond = false"]
    end
    
    subgraph "Category: physical-security"
        PhysicalKey["key = 'physical-security'"]
        PhysicalChannel["oncall_slack_id = '#facilities'"]
        PhysicalAuto["auto_respond = true"]
    end
    
    AppSecKey --> AppSecChannel
    AppSecChannel --> AppSecAuto
    
    PrivacyKey --> PrivacyUser
    PrivacyUser --> PrivacyAuto
    
    PhysicalKey --> PhysicalChannel  
    PhysicalChannel --> PhysicalAuto
```

**Sources:** [bots/triage-slackbot/README.md:68-77]()

## Channel and Routing Configuration

The triage bot operates across multiple Slack channels with distinct roles in the categorization workflow. Detailed routing rules and template structures are covered in [Setup and Configuration](#6.2).

### Channel Mapping

```mermaid
graph TB
    subgraph "Channel Configuration"
        InboundConfig["inbound_request_channel_id<br/>Where users post requests"]
        FeedConfig["feed_channel_id<br/>Where categorizations appear"]
    end
    
    subgraph "Request Flow"
        UserRequest["User posts in inbound channel"]
        BotProcessing["Bot processes with OpenAI"]
        FeedPosting["Bot posts to feed channel with buttons"]
        OnCallAction["OnCall team takes action"]
    end
    
    subgraph "Routing Destinations"
        CategoryChannel["Category-specific channels"]
        DirectMessage["Direct messages to users"]
        AutoResponse["Automatic thread responses"]
    end
    
    InboundConfig --> UserRequest
    UserRequest --> BotProcessing
    BotProcessing --> FeedPosting
    FeedConfig --> FeedPosting
    FeedPosting --> OnCallAction
    
    OnCallAction --> CategoryChannel
    OnCallAction --> DirectMessage
    OnCallAction --> AutoResponse
```

**Sources:** [bots/triage-slackbot/README.md:64-67]()

## Operational Workflows

The triage bot supports three primary operational scenarios based on the categorization confidence and category configuration.

### Workflow Decision Tree

The interaction logic is distributed across specific action handlers: `InboundRequestAcknowledgeHandler`, `InboundRequestRecategorizeHandler`, `InboundRequestRecategorizeSelectHandler`, and `InboundRequestRecategorizeSelectConversationHandler` [bots/triage-slackbot/triage_slackbot/bot.py:19-24]().

```mermaid
graph TD
    InboundMessage["Inbound Request Message"]
    
    InboundMessage --> OpenAIAnalysis["OpenAI Function Calling Analysis"]
    OpenAIAnalysis --> CategoryPrediction["Category Prediction Generated"]
    
    CategoryPrediction --> AutoResponseCheck{"Category has<br/>auto_respond = true?"}
    
    AutoResponseCheck -->|Yes| AutoResponse["Post automatic response<br/>Mark as handled"]
    AutoResponseCheck -->|No| ManualTriage["Post to feed channel<br/>with action buttons"]
    
    ManualTriage --> OnCallDecision{"OnCall Action"}
    
    OnCallDecision --> Acknowledge["Acknowledge prediction<br/>Route to category destination"]
    OnCallDecision --> Reroute["Re-route to different category"]
    OnCallDecision --> OtherCategory["Select custom destination<br/>(if other_category_enabled)"]
    
    Acknowledge --> RouteMessage["Send message to<br/>category channel/user"]
    Reroute --> RouteMessage
    OtherCategory --> RouteMessage
    
    RouteMessage --> ThreadConfirmation["Post confirmation<br/>in original thread"]
    AutoResponse --> ThreadConfirmation
```

**Sources:** [bots/triage-slackbot/README.md:79-98](), [bots/triage-slackbot/triage_slackbot/bot.py:19-24]()

## Setup and Configuration

### Prerequisites and Environment Setup

The triage bot requires specific Slack application permissions and environment configuration. For a complete guide on variables and routing rules, see [Setup and Configuration](#6.2).

| Requirement | Description |
|-------------|-------------|
| Slack App with Socket Mode | Enables real-time message processing |
| `SOCKET_APP_TOKEN` | App-level token with `connections:write` scope |
| OpenAI API Key | For AI-powered categorization |

### Required Slack Scopes

```mermaid
graph LR
    subgraph "Bot Permissions"
        ChannelsHistory["channels:history<br/>Read channel messages"]
        ChatWrite["chat:write<br/>Post messages and responses"]
        GroupsHistory["groups:history<br/>Read private channel messages"]
        ReactionsRead["reactions:read<br/>Monitor reaction events"]
        ReactionsWrite["reactions:write<br/>Add reaction confirmations"]
    end
    
    subgraph "Functionality Enabled"
        MessageProcessing["Process inbound requests"]
        ResponsePosting["Post categorizations and responses"]
        InteractiveButtons["Handle action button interactions"]
        StatusTracking["Track request handling status"]
    end
    
    ChannelsHistory --> MessageProcessing
    ChatWrite --> ResponsePosting
    GroupsHistory --> MessageProcessing
    ReactionsRead --> StatusTracking
    ReactionsWrite --> StatusTracking
    
    MessageProcessing --> InteractiveButtons
    ResponsePosting --> InteractiveButtons
```

**Sources:** [bots/triage-slackbot/README.md:26-33]()

### Build and Deployment Commands

The triage bot follows the standard build system used across all security bots:

| Command | Purpose |
|---------|---------|
| `make init-env-file` | Initialize environment configuration |
| `make init-pyproject` | Set up Python project dependencies |
| `make clean-venv` | Clean virtual environment |
| `make build-bot BOT=triage-slackbot` | Build bot with dependencies |
| `make run-bot BOT=triage-slackbot` | Run bot with configuration |

**Sources:** [bots/triage-slackbot/README.md:20-58]()

---

