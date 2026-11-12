<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/Paper2Slides · extra page Message and History Components · fetched 2026-11-09 -->

# Message and History Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/components/ConversationList.jsx](frontend/src/components/ConversationList.jsx)
- [frontend/src/components/HistoryPanel.jsx](frontend/src/components/HistoryPanel.jsx)
- [frontend/src/components/MessageList.jsx](frontend/src/components/MessageList.jsx)

</details>



This page documents the frontend components responsible for displaying conversation messages, file previews, generation progress, conversation history, and document management. These components form the core user interface for viewing results and navigating past generations.

For information about the main chat interface container, see [ChatWindow Component](#4.2.1). For configuration UI components, see [Configuration Components](#4.2.2).

---

## Overview

The message and history system consists of three primary components:

- **MessageList**: Displays messages within the active conversation, including uploaded files, generation progress, and results
- **ConversationList**: Manages the sidebar list of all conversations with metadata and navigation
- **HistoryPanel**: Provides access to previously generated files and uploaded documents for reuse

These components are presentational, receiving state via props from the parent `ChatWindow` component and communicating user actions through callbacks.

**Sources:** [frontend/src/components/MessageList.jsx:1-589](), [frontend/src/components/ConversationList.jsx:1-298](), [frontend/src/components/HistoryPanel.jsx:1-242]()

---

## Component Architecture

### Component Hierarchy

```mermaid
graph TB
    ChatWindow["ChatWindow<br/>(State Manager)"]
    
    subgraph "Conversation Navigation"
        ConvList["ConversationList<br/>frontend/src/components/ConversationList.jsx"]
    end
    
    subgraph "Main Display Area"
        MsgList["MessageList<br/>frontend/src/components/MessageList.jsx"]
    end
    
    subgraph "History & Documents"
        HistPanel["HistoryPanel<br/>frontend/src/components/HistoryPanel.jsx"]
    end
    
    subgraph "Shared State"
        ConvState["conversations[]<br/>currentConversationId<br/>messages[]<br/>history[]"]
    end
    
    ChatWindow --> ConvList
    ChatWindow --> MsgList
    ChatWindow --> HistPanel
    ChatWindow --> ConvState
    
    ConvState -.props.-> ConvList
    ConvState -.props.-> MsgList
    ConvState -.props.-> HistPanel
    
    ConvList -.callbacks.-> ChatWindow
    MsgList -.callbacks.-> ChatWindow
    HistPanel -.callbacks.-> ChatWindow
```

**Sources:** [frontend/src/components/ConversationList.jsx:4-11](), [frontend/src/components/MessageList.jsx:5-5](), [frontend/src/components/HistoryPanel.jsx:4-4]()

---

## MessageList Component

The `MessageList` component is responsible for rendering the conversation thread, showing both user inputs and system responses with rich media support.

### Props Interface

| Prop | Type | Purpose |
|------|------|---------|
| `messages` | Array | Array of message objects with `role`, `content`, `files`, etc. |
| `uploadedFiles` | Array | Files uploaded in current session for URL resolution |
| `currentWorkflow` | Object | Active generation workflow with stages and progress |
| `isLoading` | Boolean | Whether generation is in progress |
| `onCancelGeneration` | Function | Callback to cancel active generation |
| `conversationId` | String | ID of current conversation for workflow matching |

**Sources:** [frontend/src/components/MessageList.jsx:5-5]()

### Message Grouping Logic

Messages are grouped into "conversation rounds" pairing user messages with assistant responses:

```mermaid
graph LR
    Raw["Raw Message Array<br/>[user, assistant, user, assistant]"]
    Group["groupMessagesIntoRounds()"]
    Rounds["Conversation Rounds<br/>[{user, assistant, config}]"]
    
    Raw --> Group
    Group --> Rounds
    
    subgraph "Round Structure"
        Round["Round Object"]
        UserMsg["userMessage<br/>(files, content)"]
        AssistMsg["assistantMessage<br/>(pptUrl, posterUrl)"]
        Config["config<br/>(output, style, length)"]
        
        Round --> UserMsg
        Round --> AssistMsg
        Round --> Config
    end
```

The grouping algorithm [frontend/src/components/MessageList.jsx:65-103]() processes messages sequentially:
1. User message starts a new round
2. Assistant message completes the round
3. Orphan assistant messages (errors/cancels) form standalone rounds
4. Configuration metadata is attached to each round

**Sources:** [frontend/src/components/MessageList.jsx:64-103]()

### UI Structure

```mermaid
graph TB
    MsgList["MessageList Container"]
    
    subgraph "Conversation Rounds"
        Round["Round Card<br/>(white bg, rounded, shadow)"]
        ConfigHeader["Configuration Header<br/>(output, style, content badges)"]
        UserSection["User Message Section"]
        AssistSection["Assistant Message Section"]
    end
    
    subgraph "User Content"
        UserAvatar["User Avatar<br/>(sky blue gradient)"]
        UserText["Message Content"]
        UserFiles["File Chips<br/>(with preview button)"]
    end
    
    subgraph "Assistant Content"
        AssistAvatar["P2S Avatar<br/>(purple-pink gradient)"]
        AssistText["Response Content"]
        PDFViewer["PDF Iframe<br/>(80vh height)"]
        PosterImg["Poster Image"]
        DownloadBtn["Download Buttons"]
    end
    
    subgraph "Workflow Status"
        WorkflowCard["Workflow Status Card<br/>(gradient bg, loading state)"]
        StageList["Stage Progress List"]
        CancelBtn["Stop Button"]
    end
    
    MsgList --> Round
    Round --> ConfigHeader
    Round --> UserSection
    Round --> AssistSection
    
    UserSection --> UserAvatar
    UserSection --> UserText
    UserSection --> UserFiles
    
    AssistSection --> AssistAvatar
    AssistSection --> AssistText
    AssistSection --> PDFViewer
    AssistSection --> PosterImg
    AssistSection --> DownloadBtn
    
    MsgList --> WorkflowCard
    WorkflowCard --> StageList
    WorkflowCard --> CancelBtn
```

**Sources:** [frontend/src/components/MessageList.jsx:108-435]()

### File Preview System

The component implements a modal file preview system:

```mermaid
sequenceDiagram
    participant User
    participant FileChip as "File Chip Component"
    participant Preview as "Preview Modal"
    participant URL as "URL Resolution"
    
    User->>FileChip: Hover over file
    FileChip->>FileChip: Show Eye icon
    User->>FileChip: Click Eye icon
    FileChip->>URL: Resolve file.url or file.blobUrl
    URL->>URL: Search uploadedFiles array
    URL->>URL: Handle relative URLs (/uploads/...)
    URL-->>Preview: Open modal with resolved URL
    Preview->>User: Display PDF iframe or file info
    User->>Preview: Click Close
    Preview-->>FileChip: Close modal
```

File URL resolution logic [frontend/src/components/MessageList.jsx:170-191]() handles multiple sources:
- Direct `file.url` or `file.blobUrl` properties
- Fallback search in `uploadedFiles` array by name matching
- Relative backend URLs (e.g., `/uploads/...`) handled by Vite proxy

**Sources:** [frontend/src/components/MessageList.jsx:9-15](), [frontend/src/components/MessageList.jsx:170-234](), [frontend/src/components/MessageList.jsx:438-531]()

### Workflow Status Display

During active generation, a workflow status card displays stage progress:

| Stage Property | Visual Representation |
|----------------|----------------------|
| `status: 'completed'` | Green checkmark icon, green border |
| `status: 'active'` | Spinning loader, purple border, animated dots |
| `status: 'pending'` | Gray circle, muted colors |

The `getStageStatus()` function [frontend/src/components/MessageList.jsx:53-62]() determines stage status based on position in the stages array and current active stage index.

**Sources:** [frontend/src/components/MessageList.jsx:42-62](), [frontend/src/components/MessageList.jsx:338-435]()

### Result Display

Generated outputs are displayed inline with the assistant message:

- **Slides (PPT)**: PDF embedded in iframe at 80vh height [frontend/src/components/MessageList.jsx:277-288]()
- **Poster**: Image displayed with `contain` object-fit, max 80vh [frontend/src/components/MessageList.jsx:291-302]()
- **Downloads**: Gradient buttons for PDF/poster download [frontend/src/components/MessageList.jsx:305-326]()

**Sources:** [frontend/src/components/MessageList.jsx:274-328]()

---

## ConversationList Component

The `ConversationList` component manages the sidebar showing all conversations with chronological grouping and deletion support.

### Props Interface

| Prop | Type | Purpose |
|------|------|---------|
| `conversations` | Array | All conversation objects |
| `currentConversationId` | String | Active conversation ID for highlighting |
| `onSelectConversation` | Function | Callback when conversation is clicked |
| `onNewConversation` | Function | Callback to create new conversation |
| `onDeleteConversation` | Function | Callback to delete conversation |
| `onCollapse` | Function | Callback to collapse sidebar |

**Sources:** [frontend/src/components/ConversationList.jsx:4-11]()

### Date Grouping Algorithm

Conversations are grouped into four temporal categories:

```mermaid
graph TB
    Convs["conversations[]"]
    Group["groupByDate()"]
    
    subgraph "Grouping Logic"
        Check1{{"updatedAt == today?"}}
        Check2{{"updatedAt == yesterday?"}}
        Check3{{"updatedAt > weekAgo?"}}
    end
    
    Today["Today Group"]
    Yesterday["Yesterday Group"]
    ThisWeek["This Week Group"]
    Older["Older Group"]
    
    Convs --> Group
    Group --> Check1
    Check1 -->|Yes| Today
    Check1 -->|No| Check2
    Check2 -->|Yes| Yesterday
    Check2 -->|No| Check3
    Check3 -->|Yes| ThisWeek
    Check3 -->|No| Older
```

The `groupByDate()` function [frontend/src/components/ConversationList.jsx:80-111]() normalizes dates to midnight and compares timestamps to determine group membership.

**Sources:** [frontend/src/components/ConversationList.jsx:79-111]()

### Conversation Metadata Display

Each conversation item displays computed metadata:

```mermaid
graph LR
    Conv["Conversation Object"]
    
    subgraph "Display Functions"
        Title["getConversationTitle()"]
        Subtitle["getConversationSubtitle()"]
        Date["formatDate()"]
    end
    
    subgraph "UI Elements"
        TitleText["File-based Title<br/>(truncated to 30 chars)"]
        SubtitleText["'N files • M messages'"]
        DateText["'Just now' / '5m ago' / 'Jan 15'"]
    end
    
    Conv --> Title
    Conv --> Subtitle
    Conv --> Date
    
    Title --> TitleText
    Subtitle --> SubtitleText
    Date --> DateText
```

Title derivation [frontend/src/components/ConversationList.jsx:29-38]():
- Uses first file name without extension
- Truncates to 30 characters with ellipsis
- Falls back to `conv.title` or "New Chat"

**Sources:** [frontend/src/components/ConversationList.jsx:15-53]()

### Deletion Workflow

Conversation deletion uses a two-step confirmation pattern:

```mermaid
sequenceDiagram
    participant User
    participant Item as "Conversation Item"
    participant Menu as "Dropdown Menu"
    participant Modal as "Confirmation Modal"
    participant Parent as "ChatWindow"
    
    User->>Item: Hover conversation
    Item->>Item: Show MoreHorizontal icon
    User->>Item: Click menu icon
    Item->>Menu: Show dropdown
    User->>Menu: Click Delete
    Menu->>Modal: Show confirmation dialog
    Modal->>User: "Delete Conversation?"
    User->>Modal: Click "Delete" button
    Modal->>Parent: onDeleteConversation(convId)
    Parent->>Parent: Remove from conversations[]
    Parent->>Parent: Update localStorage
```

The deletion state is managed through `deleteConfirmId` [frontend/src/components/ConversationList.jsx:13-13](), which triggers the modal render when set.

**Sources:** [frontend/src/components/ConversationList.jsx:55-72](), [frontend/src/components/ConversationList.jsx:247-292]()

### Visual States

Conversation items have distinct visual states:

| State | CSS Classes | Visual Effect |
|-------|-------------|---------------|
| Active | `from-purple-100 to-pink-100`, `border-purple-300` | Gradient background, purple border |
| Inactive | `hover:bg-gray-100`, `border-transparent` | Subtle hover effect |
| Hover Actions | `opacity-0 group-hover:opacity-100` | Show menu button on hover |

**Sources:** [frontend/src/components/ConversationList.jsx:124-189]()

---

## HistoryPanel Component

The `HistoryPanel` component provides a tabbed interface for accessing generated files and uploaded documents.

### Props Interface

| Prop | Type | Purpose |
|------|------|---------|
| `history` | Array | Array of generation result objects |
| `uploadedDocuments` | Array | Array of uploaded document objects |
| `onSelectFile` | Function | Callback when document is clicked for reuse |
| `onSelectHistoryItem` | Function | Callback when history item is clicked |

**Sources:** [frontend/src/components/HistoryPanel.jsx:4-4]()

### Tab Structure

```mermaid
graph TB
    Panel["HistoryPanel Container"]
    
    subgraph "Tab System"
        TabBar["Tab Bar<br/>(activeTab state)"]
        GenTab["Generated Files Tab"]
        DocsTab["Documents Tab"]
    end
    
    subgraph "Generated Files View"
        HistList["History Item List"]
        HistItem["History Item Card"]
        SourceFiles["Expandable Source Files"]
        Download["Download Button"]
    end
    
    subgraph "Documents View"
        DocList["Document List"]
        DocItem["Document Card<br/>(clickable for reuse)"]
    end
    
    Panel --> TabBar
    TabBar --> GenTab
    TabBar --> DocsTab
    
    GenTab --> HistList
    HistList --> HistItem
    HistItem --> SourceFiles
    HistItem --> Download
    
    DocsTab --> DocList
    DocList --> DocItem
```

The `activeTab` state [frontend/src/components/HistoryPanel.jsx:6-6]() toggles between `'history'` and `'documents'` views.

**Sources:** [frontend/src/components/HistoryPanel.jsx:78-235]()

### History Item Display Name

History items are displayed with a computed name combining multiple configuration parameters:

```mermaid
graph LR
    Item["History Item Object"]
    
    subgraph "Name Components"
        Output["outputType<br/>'slides' or 'poster'"]
        File["sourceFiles[0].name<br/>(without extension)"]
        Style["style"]
        Content["content"]
        Size["length or density"]
    end
    
    Name["Display Name<br/>'Slides - paper_title - academic - paper - long'"]
    
    Item --> Output
    Item --> File
    Item --> Style
    Item --> Content
    Item --> Size
    
    Output --> Name
    File --> Name
    Style --> Name
    Content --> Name
    Size --> Name
```

The `getHistoryItemDisplayName()` function [frontend/src/components/HistoryPanel.jsx:30-62]() constructs names by joining configuration parameters with " - " separators.

**Sources:** [frontend/src/components/HistoryPanel.jsx:29-62]()

### Source File Expansion

History items include expandable source file lists:

```mermaid
stateDiagram-v2
    [*] --> Collapsed
    Collapsed --> Expanded: Click chevron
    Expanded --> Collapsed: Click chevron
    
    Collapsed: ChevronRight icon
    Collapsed: "Source Files (N)" text
    
    Expanded: ChevronDown icon
    Expanded: List of clickable files
    Expanded: File names with sizes
```

The `expandedItems` state object [frontend/src/components/HistoryPanel.jsx:5-5]() tracks which history items are expanded using item IDs as keys.

**Sources:** [frontend/src/components/HistoryPanel.jsx:8-13](), [frontend/src/components/HistoryPanel.jsx:159-198]()

### File Reuse Pattern

Both tabs support file reuse through click handlers:

```mermaid
sequenceDiagram
    participant User
    participant HistPanel as "HistoryPanel"
    participant ChatWindow as "ChatWindow"
    participant MsgInput as "MessageInput"
    
    User->>HistPanel: Click document in Documents tab
    HistPanel->>ChatWindow: onSelectFile(file)
    ChatWindow->>ChatWindow: Add to selectedFiles[]
    ChatWindow->>MsgInput: Update props
    MsgInput->>User: Show file in upload list
    
    Note over User,MsgInput: OR
    
    User->>HistPanel: Click source file in Generated Files
    HistPanel->>ChatWindow: onSelectFile(file)
    ChatWindow->>ChatWindow: Add to selectedFiles[]
    ChatWindow->>MsgInput: Update props
    MsgInput->>User: Show file in upload list
```

**Sources:** [frontend/src/components/HistoryPanel.jsx:64-75](), [frontend/src/components/HistoryPanel.jsx:177-194](), [frontend/src/components/HistoryPanel.jsx:213-230]()

---

## Data Flow Summary

### State Down, Callbacks Up

```mermaid
graph TB
    ChatWindow["ChatWindow<br/>(State Container)"]
    
    subgraph "Props (Data Down)"
        ConvData["conversations[]<br/>currentConversationId"]
        MsgData["messages[]<br/>uploadedFiles[]<br/>currentWorkflow"]
        HistData["history[]<br/>uploadedDocuments[]"]
    end
    
    subgraph "Callbacks (Actions Up)"
        ConvActions["onSelectConversation()<br/>onNewConversation()<br/>onDeleteConversation()"]
        MsgActions["onCancelGeneration()"]
        HistActions["onSelectFile()<br/>onSelectHistoryItem()"]
    end
    
    ChatWindow --> ConvData
    ChatWindow --> MsgData
    ChatWindow --> HistData
    
    ConvData --> ConversationList
    MsgData --> MessageList
    HistData --> HistoryPanel
    
    ConversationList --> ConvActions
    MessageList --> MsgActions
    HistoryPanel --> HistActions
    
    ConvActions --> ChatWindow
    MsgActions --> ChatWindow
    HistActions --> ChatWindow
```

**Sources:** [frontend/src/components/ConversationList.jsx:4-11](), [frontend/src/components/MessageList.jsx:5-5](), [frontend/src/components/HistoryPanel.jsx:4-4]()

---

## Key Features Summary

| Component | Primary Responsibilities | Key Functions |
|-----------|-------------------------|---------------|
| **MessageList** | Display conversation thread, show generation progress, preview files and results | `groupMessagesIntoRounds()` [frontend/src/components/MessageList.jsx:65-103](), `getStageStatus()` [frontend/src/components/MessageList.jsx:53-62]() |
| **ConversationList** | List conversations with date grouping, handle selection and deletion | `groupByDate()` [frontend/src/components/ConversationList.jsx:80-111](), `getConversationTitle()` [frontend/src/components/ConversationList.jsx:29-38]() |
| **HistoryPanel** | Provide access to generated files and documents for reuse | `getHistoryItemDisplayName()` [frontend/src/components/HistoryPanel.jsx:30-62]() |

All three components follow React best practices with unidirectional data flow and separation of presentation from state management.

**Sources:** [frontend/src/components/MessageList.jsx:1-589](), [frontend/src/components/ConversationList.jsx:1-298](), [frontend/src/components/HistoryPanel.jsx:1-242]()

---

