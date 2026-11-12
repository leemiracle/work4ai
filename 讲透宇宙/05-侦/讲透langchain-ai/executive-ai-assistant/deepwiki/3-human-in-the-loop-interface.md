<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/executive-ai-assistant · page 3 Human-in-the-Loop Interface · fetched 2026-10-26 -->

# Human-in-the-Loop Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [eaia/main/human_inbox.py](eaia/main/human_inbox.py)

</details>



## Purpose and Scope

This document describes the Human-in-the-Loop Interface system in the Executive AI Assistant (EAIA). This system enables human oversight of AI-generated content by allowing users to review, edit, approve or reject actions before they're executed. This document focuses specifically on the interrupt mechanisms, decision flows, and Agent Inbox integration. For information about how this system integrates with email processing, see [Email Processing System](#2), and for Agent Inbox specific details, see [Agent Inbox Integration](#3.1).

## Architecture Overview

The Human-in-the-Loop Interface serves as the critical bridge between automated AI processing and human decision-making in the EAIA system.

### System Components

```mermaid
graph TD
    subgraph "AI Processing"
        Triage["Email Triage"]
        Draft["Email Drafting"]
        Calendar["Calendar Processing"]
    end

    subgraph "Human Interface Layer"
        HumanInbox["human_inbox.py Functions"]
        Interrupt["interrupt() Mechanism"]
        AgentInboxUI["Agent Inbox UI"]
    end

    subgraph "Human Actions"
        Accept["Accept"]
        Edit["Edit"]
        Ignore["Ignore"]
        Respond["Respond with Instructions"]
    end

    subgraph "Reflection System"
        Memory["LangSmith Store"]
        Reflection["Reflection Graphs"]
    end

    Triage -->|"notify()"| HumanInbox
    Draft -->|"send_email_draft()"| HumanInbox
    Calendar -->|"send_cal_invite()"| HumanInbox
    
    HumanInbox -->|"Creates"| Interrupt
    Interrupt -->|"Displayed in"| AgentInboxUI
    
    AgentInboxUI -->|"User selects"| Accept
    AgentInboxUI -->|"User selects"| Edit
    AgentInboxUI -->|"User selects"| Ignore
    AgentInboxUI -->|"User selects"| Respond
    
    Accept & Edit & Ignore & Respond --> HumanInbox
    HumanInbox -->|"Creates feedback"| Memory
    Memory --> Reflection
    Reflection -->|"Improves"| Draft
```

Sources: [eaia/main/human_inbox.py:1-396]()

### Core Components

The Human-in-the-Loop system consists of these key elements:

1. **Interrupt Mechanism**: Pauses AI execution to request human input
2. **Human Interface Layer**: Functions that format AI outputs for human review
3. **Agent Inbox UI**: Where humans review and interact with AI-generated content
4. **Human Action Handlers**: Code to process different types of human responses
5. **Reflection System**: Stores and learns from human feedback

## Interrupt Mechanism

The system uses LangGraph's interrupt mechanism to pause execution and wait for human input. The core structures that enable this are:

```mermaid
classDiagram
    class HumanInterruptConfig {
        +allow_ignore: bool
        +allow_respond: bool
        +allow_edit: bool
        +allow_accept: bool
    }
    
    class ActionRequest {
        +action: str
        +args: dict
    }
    
    class HumanInterrupt {
        +action_request: ActionRequest
        +config: HumanInterruptConfig
        +description: Optional[str]
    }
    
    class HumanResponse {
        +type: "accept"|"ignore"|"response"|"edit"
        +args: Union[None, str, ActionRequest]
    }
    
    HumanInterrupt --> HumanInterruptConfig
    HumanInterrupt --> ActionRequest
```

Sources: [eaia/main/human_inbox.py:16-37]()

## Human Decision Flows

The interface supports four main types of human intervention points, each with different available actions.

### Notification Flow

```mermaid
sequenceDiagram
    participant AI as AI System
    participant Human as Human User
    participant Memory as Memory System
    
    AI->>AI: Triage email as "notify"
    AI->>Human: Show email with notify() interrupt
    
    alt Human responds with instructions
        Human->>AI: Provide instructions
        AI->>Memory: Save email and instructions
        AI->>Memory: Trigger reflection for learning
    else Human ignores
        Human->>AI: Choose "ignore"
        AI->>Memory: Save as "no" (ignored)
    end
```

Sources: [eaia/main/human_inbox.py:240-297]()

### Email Draft Review Flow

```mermaid
sequenceDiagram
    participant AI as AI System
    participant Human as Human User
    participant Memory as Memory System
    
    AI->>AI: Generate email draft
    AI->>Human: Present draft with send_email_draft() interrupt
    
    alt Human accepts
        Human->>AI: Choose "accept"
        AI->>Memory: Save as successful email
        AI->>AI: Continue to send email
    else Human edits
        Human->>AI: Edit content
        AI->>Memory: Save original and edited versions
        AI->>Memory: Trigger reflection with corrections
        AI->>AI: Continue with edited content
    else Human responds with feedback
        Human->>AI: Provide feedback
        AI->>Memory: Save feedback
        AI->>Memory: Trigger reflection with feedback
        AI->>AI: Handle based on feedback
    else Human ignores
        Human->>AI: Choose "ignore"
        AI->>Memory: Save as "no" (ignored)
        AI->>AI: Abort email sending
    end
```

Sources: [eaia/main/human_inbox.py:139-237]()

### Calendar Invite Review Flow

```mermaid
sequenceDiagram
    participant AI as AI System
    participant Human as Human User
    participant Memory as Memory System
    
    AI->>AI: Generate calendar invite
    AI->>Human: Present invite with send_cal_invite() interrupt
    
    alt Human accepts
        Human->>AI: Choose "accept"
        AI->>Memory: Save as successful calendar event
        AI->>AI: Send calendar invite
    else Human edits
        Human->>AI: Edit invite details
        AI->>Memory: Save feedback
        AI->>Memory: Trigger reflection
        AI->>AI: Continue with edited invite
    else Human responds with feedback
        Human->>AI: Provide feedback
        AI->>Memory: Save feedback
        AI->>Memory: Trigger reflection
        AI->>AI: Handle based on feedback
    else Human ignores
        Human->>AI: Choose "ignore"
        AI->>Memory: Save as "no" (ignored)
        AI->>AI: Abort invite sending
    end
```

Sources: [eaia/main/human_inbox.py:300-395]()

## Human Response Types

The system supports four types of human responses, each with different implications for workflow:

| Response Type | Description | Available In | Effect on Workflow |
|---------------|-------------|--------------|-------------------|
| `accept` | Accept content as-is | Email drafts, Calendar invites | Proceeds with sending/scheduling |
| `edit` | Modify the content | Email drafts, Calendar invites | Proceeds with modified content |
| `ignore` | Reject the content | All interrupts | Aborts the action, marks as ignored |
| `response` | Provide textual feedback | All interrupts | Varies by context; may restart flow |

Sources: [eaia/main/human_inbox.py:34-37](), [eaia/main/human_inbox.py:146-152](), [eaia/main/human_inbox.py:308-314]()

## Email Visualization

When presenting emails to humans, the system formats them using a consistent Markdown template that includes:

- Email subject as heading
- Link to view the original email in Gmail
- Sender and recipient information
- Email content

The template is rendered using the `_generate_email_markdown` function which creates a standardized view for all email-related interrupts.

Sources: [eaia/main/human_inbox.py:39-58]()

## Feedback and Learning System

The human-in-the-loop system includes a feedback mechanism that enables the AI to learn from human interactions:

```mermaid
graph TD
    subgraph "Human Actions"
        Edit["Human Edits Content"]
        Accept["Human Accepts Content"]
        Feedback["Human Provides Feedback"]
        Ignore["Human Ignores Content"]
    end
    
    subgraph "Memory System"
        Save["save_email() Function"]
        Store["LangSmith Store"]
    end
    
    subgraph "Learning System"
        Reflection["multi_reflection_graph"]
    end
    
    Edit -->|"Creates learning opportunity"| Save
    Feedback -->|"Creates learning opportunity"| Save
    Accept -->|"Saves successful example"| Save
    Ignore -->|"Saves negative example"| Save
    
    Save -->|"Stores examples"| Store
    Edit -->|"Triggers reflection"| Reflection
    Feedback -->|"Triggers reflection"| Reflection
    
    Reflection -->|"Improves future responses"| AI["AI System"]
```

When the human edits content or provides feedback, the system:

1. Saves the original content, the human's feedback/edits, and email metadata
2. Triggers a reflection process via `multi_reflection_graph`
3. Associates feedback with specific prompt types to focus learning
4. Uses these examples to improve future responses

Sources: [eaia/main/human_inbox.py:61-71](), [eaia/main/human_inbox.py:213-230]()

## Agent Inbox Integration

The system integrates with the Agent Inbox UI, which provides the visual interface for human review.

### Local Setup

```mermaid
graph TD
    LocalDev["langgraph dev"]
    LocalRunIngest["run_ingest.py"]
    AgentInboxLocal["Agent Inbox http://127.0.0.1:2024"]
    HumanUser["Human User"]
    
    LocalDev -->|"Runs EAIA system"| HumanInterrupt["Human Interrupt Functions"]
    LocalRunIngest -->|"Triggers"| LocalDev
    HumanInterrupt -->|"Creates interrupts in"| AgentInboxLocal
    AgentInboxLocal -->|"Displays to"| HumanUser
    HumanUser -->|"Interacts with"| AgentInboxLocal
    AgentInboxLocal -->|"Returns response to"| HumanInterrupt
```

### Cloud Setup

```mermaid
graph TD
    CloudDeploy["LangGraph Cloud Deployment"]
    CloudRunIngest["run_ingest.py with --url"]
    AgentInboxCloud["Agent Inbox with Cloud URL"]
    HumanUser["Human User"]
    CronJob["Cron Job (setup_cron.py)"]
    
    CloudDeploy -->|"Runs EAIA system"| HumanInterrupt["Human Interrupt Functions"]
    CloudRunIngest -->|"Triggers"| CloudDeploy
    CronJob -->|"Schedules"| CloudRunIngest
    HumanInterrupt -->|"Creates interrupts in"| AgentInboxCloud
    AgentInboxCloud -->|"Displays to"| HumanUser
    HumanUser -->|"Interacts with"| AgentInboxCloud
    AgentInboxCloud -->|"Returns response to"| HumanInterrupt
```

Sources: [README.md:92-103](), [README.md:145-152]()

## Implementation Details

The human-in-the-loop interface uses several key technical components:

1. **LangGraph's interrupt mechanism**: Used to pause execution and wait for human input
2. **TypedDict classes**: Define the structure of interrupts and responses
3. **Markdown formatting**: For displaying email content
4. **LangSmith integration**: For storing examples and tracking feedback
5. **LangGraph Client**: For triggering reflection runs

The system is designed to work both locally during development and in the cloud for production use.

Sources: [eaia/main/human_inbox.py:4-10](), [eaia/main/human_inbox.py:13]()

---

