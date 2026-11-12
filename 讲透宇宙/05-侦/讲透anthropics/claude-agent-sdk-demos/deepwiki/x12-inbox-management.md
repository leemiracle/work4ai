<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-agent-sdk-demos · extra page Inbox Management · fetched 2026-10-26 -->

# Inbox Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [email-agent/client/App.tsx](email-agent/client/App.tsx)
- [email-agent/client/components/InboxView.tsx](email-agent/client/components/InboxView.tsx)

</details>



## Purpose and Scope

This page documents the `InboxView` component, which provides the email list interface for the Email Agent demo. The component handles email list rendering, selection state management, screenshot mode for privacy, and visual indicators for email metadata. For full email content display, see [Email Viewing Components](#4.4.2). For application-level state management and tab navigation, see [Application Structure](#4.4.1).

**Sources:** [email-agent/client/components/InboxView.tsx:1-180](), [email-agent/client/App.tsx:1-162]()

---

## Component Architecture

The `InboxView` component is a self-contained sidebar panel (400px wide) that displays the email list with integrated listeners panel and screenshot mode controls.

### InboxView Component Structure

```mermaid
graph TB
    InboxView["InboxView Component"]
    
    subgraph "Props Interface"
        Props["InboxViewProps"]
        EmailsProp["emails: Email[]"]
        OnSelectProp["onEmailSelect: (email) => void"]
        SelectedIdProp["selectedEmailId?: number"]
    end
    
    subgraph "Internal State"
        ScreenshotContext["useScreenshotMode()"]
        IsScreenshotMode["isScreenshotMode: boolean"]
        ToggleFunction["toggleScreenshotMode()"]
    end
    
    subgraph "Utility Functions"
        FormatTime["formatRelativeTime(dateString)"]
        TruncateText["truncate(text, maxLength)"]
    end
    
    subgraph "Child Components"
        ActivePanel["ActiveListenersPanel"]
    end
    
    subgraph "Placeholder System"
        PlaceholderUtils["utils/placeholders"]
        GetName["getPlaceholderName(index)"]
        GetEmail["getPlaceholderEmail(index)"]
        GetSubject["getPlaceholderSubject(index)"]
        GetSnippet["getPlaceholderSnippet(index)"]
        GetDate["getPlaceholderDate(index)"]
    end
    
    Props --> EmailsProp
    Props --> OnSelectProp
    Props --> SelectedIdProp
    
    InboxView --> Props
    InboxView --> ScreenshotContext
    InboxView --> FormatTime
    InboxView --> TruncateText
    InboxView --> ActivePanel
    
    ScreenshotContext --> IsScreenshotMode
    ScreenshotContext --> ToggleFunction
    
    IsScreenshotMode --> PlaceholderUtils
    PlaceholderUtils --> GetName
    PlaceholderUtils --> GetEmail
    PlaceholderUtils --> GetSubject
    PlaceholderUtils --> GetSnippet
    PlaceholderUtils --> GetDate
```

**Sources:** [email-agent/client/components/InboxView.tsx:29-37](), [email-agent/client/components/InboxView.tsx:5-11]()

---

## Email Interface Definition

The `InboxView` component operates on an `Email` interface that defines the structure of email data received from the server.

### Email Type Definition

| Property | Type | Description |
|----------|------|-------------|
| `id` | `number` | Database primary key |
| `message_id` | `string` | IMAP message ID |
| `subject` | `string` | Email subject line |
| `from_address` | `string` | Sender email address |
| `from_name` | `string?` | Optional sender display name |
| `date_sent` | `string` | ISO timestamp of send date |
| `body_text` | `string?` | Plain text body |
| `body_html` | `string?` | HTML body |
| `snippet` | `string?` | Preview text (first ~150 chars) |
| `is_read` | `boolean` | Read/unread status |
| `is_starred` | `boolean` | Starred/flagged status |
| `has_attachments` | `boolean` | Attachment indicator |
| `folder` | `string?` | IMAP folder name |

**Sources:** [email-agent/client/components/InboxView.tsx:13-27]()

---

## Layout Structure

The `InboxView` component follows a three-section vertical layout: header, content area, and footer.

### Component Layout Diagram

```mermaid
graph TB
    Container["div.w-400px.h-full.bg-white"]
    
    subgraph "Header Section"
        HeaderDiv["div.px-4.py-3.border-b"]
        InboxIcon["Inbox Icon"]
        InboxLabel["INBOX Label"]
        EmailCount["Badge: email count"]
    end
    
    subgraph "Active Listeners"
        ListenersPanel["ActiveListenersPanel Component"]
    end
    
    subgraph "Content Section"
        ContentDiv["div.flex-1.overflow-y-auto"]
        EmptyState["Empty State (No emails)"]
        EmailList["div.divide-y"]
        EmailItem1["Email Item 1"]
        EmailItem2["Email Item 2"]
        EmailItemN["Email Item N"]
    end
    
    subgraph "Footer Section"
        FooterDiv["div.px-4.py-2.border-t.bg-gray-50"]
        EmailCountText["Count Text"]
        ScreenshotButton["Screenshot Mode Toggle"]
    end
    
    Container --> HeaderDiv
    Container --> ListenersPanel
    Container --> ContentDiv
    Container --> FooterDiv
    
    HeaderDiv --> InboxIcon
    HeaderDiv --> InboxLabel
    HeaderDiv --> EmailCount
    
    ContentDiv --> EmptyState
    ContentDiv --> EmailList
    
    EmailList --> EmailItem1
    EmailList --> EmailItem2
    EmailList --> EmailItemN
    
    FooterDiv --> EmailCountText
    FooterDiv --> ScreenshotButton
```

**Sources:** [email-agent/client/components/InboxView.tsx:62-178]()

---

## Email List Rendering

### Empty State

When no emails are present, the component displays a centered empty state with an icon and explanatory text.

```mermaid
graph LR
    EmailsCheck{"emails.length === 0"}
    EmptyState["Empty State Display"]
    MailIcon["Mail Icon (w-12 h-12)"]
    NoEmailsText["'No emails in inbox'"]
    SyncText["'Emails will appear here once synced'"]
    
    EmailsCheck -->|true| EmptyState
    EmptyState --> MailIcon
    EmptyState --> NoEmailsText
    EmptyState --> SyncText
```

**Sources:** [email-agent/client/components/InboxView.tsx:83-88]()

### Email Item Structure

Each email item is rendered with a hierarchical layout displaying sender, subject, snippet, and metadata indicators.

```mermaid
graph TB
    EmailItem["Email Item div"]
    
    subgraph "Row 1: Sender and Date"
        SenderBlock["Sender Block"]
        FromName["from_name or from_address"]
        UnreadDot["Unread Dot (blue-500)"]
        FromEmail["from_address (text-xs)"]
        DateTime["Relative Time"]
    end
    
    subgraph "Row 2: Subject"
        SubjectText["subject (truncated to 50)"]
    end
    
    subgraph "Row 3: Snippet"
        SnippetText["snippet (line-clamp-2)"]
    end
    
    subgraph "Row 4: Metadata Icons"
        MetadataRow["Metadata Row"]
        StarIcon["Star Icon (if starred)"]
        AttachIcon["Attachment Icon (if has_attachments)"]
        FolderBadge["Folder Badge (if not INBOX)"]
    end
    
    EmailItem --> SenderBlock
    EmailItem --> SubjectText
    EmailItem --> SnippetText
    EmailItem --> MetadataRow
    
    SenderBlock --> FromName
    SenderBlock --> UnreadDot
    SenderBlock --> FromEmail
    SenderBlock --> DateTime
    
    MetadataRow --> StarIcon
    MetadataRow --> AttachIcon
    MetadataRow --> FolderBadge
```

**Sources:** [email-agent/client/components/InboxView.tsx:90-152]()

---

## Selection Handling

Email selection is managed through click handlers and visual feedback based on the `selectedEmailId` prop.

### Selection State Flow

```mermaid
graph LR
    UserClick["User Clicks Email Item"]
    OnClick["onClick Handler"]
    OnEmailSelect["onEmailSelect(email)"]
    ParentState["Parent Component State"]
    PropUpdate["selectedEmailId Prop Update"]
    VisualFeedback["Visual Feedback Applied"]
    
    UserClick --> OnClick
    OnClick --> OnEmailSelect
    OnEmailSelect --> ParentState
    ParentState --> PropUpdate
    PropUpdate --> VisualFeedback
```

### Visual Feedback Classes

| State | CSS Classes | Description |
|-------|-------------|-------------|
| Unselected, Read | `hover:bg-gray-50` | Light hover effect |
| Unselected, Unread | `bg-blue-50/30 hover:bg-gray-50` | Blue tint background |
| Selected | `bg-gray-100 border-l-2 border-gray-900` | Gray background with left border |
| Unread Text | `font-semibold` (subject) | Bold text for unread |

**Sources:** [email-agent/client/components/InboxView.tsx:91-98]()

### Integration with App Component

```mermaid
graph TB
    AppComponent["App.tsx Component"]
    SelectedState["selectedEmail State"]
    InboxViewComp["InboxView Component"]
    EmailViewerComp["EmailViewer Component"]
    
    subgraph "Props Passed to InboxView"
        EmailsProp["emails={emails}"]
        OnSelectProp["onEmailSelect={setSelectedEmail}"]
        SelectedIdProp["selectedEmailId={selectedEmail?.id}"]
    end
    
    subgraph "Conditional Rendering"
        EmailViewerRender["selectedEmail && <EmailViewer />"]
    end
    
    AppComponent --> SelectedState
    AppComponent --> InboxViewComp
    AppComponent --> EmailViewerComp
    
    InboxViewComp --> EmailsProp
    InboxViewComp --> OnSelectProp
    InboxViewComp --> SelectedIdProp
    
    SelectedState --> EmailViewerRender
```

**Sources:** [email-agent/client/App.tsx:17](), [email-agent/client/App.tsx:98-102](), [email-agent/client/App.tsx:136-141]()

---

## Screenshot Mode

Screenshot mode replaces sensitive email data with placeholder values to enable safe screenshots and documentation.

### Screenshot Mode Architecture

```mermaid
graph TB
    ScreenshotContext["ScreenshotModeContext"]
    UseHook["useScreenshotMode()"]
    IsEnabled["isScreenshotMode: boolean"]
    ToggleFunc["toggleScreenshotMode()"]
    
    subgraph "Conditional Rendering Logic"
        CheckMode{"isScreenshotMode?"}
        RealData["Real Email Data"]
        PlaceholderData["Placeholder Data"]
    end
    
    subgraph "Placeholder Functions"
        GetPlaceholderName["getPlaceholderName(index)"]
        GetPlaceholderEmail["getPlaceholderEmail(index)"]
        GetPlaceholderSubject["getPlaceholderSubject(index)"]
        GetPlaceholderSnippet["getPlaceholderSnippet(index)"]
        GetPlaceholderDate["getPlaceholderDate(index)"]
    end
    
    subgraph "UI Controls"
        FooterButton["Footer Toggle Button"]
        CameraIcon["Camera Icon (enabled)"]
        CameraOffIcon["CameraOff Icon (disabled)"]
    end
    
    ScreenshotContext --> UseHook
    UseHook --> IsEnabled
    UseHook --> ToggleFunc
    
    IsEnabled --> CheckMode
    CheckMode -->|true| PlaceholderData
    CheckMode -->|false| RealData
    
    PlaceholderData --> GetPlaceholderName
    PlaceholderData --> GetPlaceholderEmail
    PlaceholderData --> GetPlaceholderSubject
    PlaceholderData --> GetPlaceholderSnippet
    PlaceholderData --> GetPlaceholderDate
    
    ToggleFunc --> FooterButton
    FooterButton --> CameraIcon
    FooterButton --> CameraOffIcon
```

### Screenshot Mode Data Replacement

| Email Field | Real Data | Placeholder Function | Index Parameter |
|-------------|-----------|---------------------|-----------------|
| Sender Name | `email.from_name \|\| email.from_address.split('@')[0]` | `getPlaceholderName(index)` | Email array index |
| Sender Email | `email.from_address` | `getPlaceholderEmail(index)` | Email array index |
| Subject | `email.subject` | `getPlaceholderSubject(index)` | Email array index |
| Snippet | `email.snippet` | `getPlaceholderSnippet(index)` | Email array index |
| Date | `formatRelativeTime(email.date_sent)` | `getPlaceholderDate(index * 3)` | `index * 3` for variety |

**Sources:** [email-agent/client/components/InboxView.tsx:36](), [email-agent/client/components/InboxView.tsx:104-122](), [email-agent/client/components/InboxView.tsx:164-176]()

---

## Utility Functions

### formatRelativeTime

Converts ISO date strings to human-readable relative time strings.

**Function Logic:**

```mermaid
graph TB
    Input["dateString: string"]
    ParseDate["new Date(dateString)"]
    CalcDiff["Calculate time difference"]
    
    subgraph "Time Range Checks"
        LessThan1Min{"< 1 minute?"}
        LessThan60Min{"< 60 minutes?"}
        LessThan24Hr{"< 24 hours?"}
        LessThan7Days{"< 7 days?"}
    end
    
    JustNow["Return 'just now'"]
    Minutes["Return '{diffMins}m ago'"]
    Hours["Return '{diffHours}h ago'"]
    Days["Return '{diffDays}d ago'"]
    FullDate["Return 'Mon DD' format"]
    
    Input --> ParseDate
    ParseDate --> CalcDiff
    CalcDiff --> LessThan1Min
    
    LessThan1Min -->|true| JustNow
    LessThan1Min -->|false| LessThan60Min
    LessThan60Min -->|true| Minutes
    LessThan60Min -->|false| LessThan24Hr
    LessThan24Hr -->|true| Hours
    LessThan24Hr -->|false| LessThan7Days
    LessThan7Days -->|true| Days
    LessThan7Days -->|false| FullDate
```

**Sources:** [email-agent/client/components/InboxView.tsx:39-53]()

### truncate

Truncates text to a maximum length with ellipsis.

**Parameters:**
- `text: string | undefined` - Text to truncate
- `maxLength: number` - Maximum character length

**Returns:** Truncated string with `...` appended if length exceeded, empty string if text is undefined

**Sources:** [email-agent/client/components/InboxView.tsx:56-60]()

---

## Visual Indicators

The component uses various visual indicators to convey email status and metadata.

### Status Indicators

| Indicator | Condition | Visual Representation | Location |
|-----------|-----------|----------------------|----------|
| Unread Dot | `!email.is_read` | Blue circle (`w-2 h-2 bg-blue-500 rounded-full`) | Next to sender name |
| Unread Background | `!email.is_read` | Light blue tint (`bg-blue-50/30`) | Entire email item |
| Unread Text | `!email.is_read` | Bold font (`font-semibold` or `font-medium`) | Sender name and subject |
| Star Icon | `email.is_starred` | Yellow star (`★` with `text-yellow-500`) | Metadata row |
| Attachment Icon | `email.has_attachments` | Paperclip emoji (`📎`) | Metadata row |
| Folder Badge | `email.folder && email.folder !== 'INBOX'` | Gray badge with folder name | Metadata row |
| Selection Border | `selectedEmailId === email.id` | Left border (`border-l-2 border-gray-900`) | Entire email item |

**Sources:** [email-agent/client/components/InboxView.tsx:94-98](), [email-agent/client/components/InboxView.tsx:108-110](), [email-agent/client/components/InboxView.tsx:139-151]()

---

## Active Listeners Panel Integration

The `InboxView` component includes the `ActiveListenersPanel` component directly below the header, providing visibility into automated email monitoring rules.

```mermaid
graph TB
    InboxView["InboxView Container"]
    Header["Header Section"]
    ListenersPanel["<ActiveListenersPanel />"]
    Content["Email List Content"]
    Footer["Footer Section"]
    
    InboxView --> Header
    InboxView --> ListenersPanel
    InboxView --> Content
    InboxView --> Footer
    
    ListenersPanel -.->|"See Listeners System"| ListenersDocs["Documentation: 4.6"]
```

The panel is positioned between the header and email list, allowing users to see active automated rules while browsing their inbox. For detailed information on how listeners work and how to create them, see [Listeners System](#4.6).

**Sources:** [email-agent/client/components/InboxView.tsx:77-78]()

---

## Footer Controls

The footer section displays email count statistics and screenshot mode toggle controls.

### Footer Layout

```mermaid
graph LR
    Footer["Footer div.px-4.py-2"]
    FlexContainer["flex.items-center.justify-between"]
    LeftSide["Email Count Text"]
    RightSide["Screenshot Mode Button"]
    
    CountText["'{emails.length} recent emails'"]
    Button["button.flex.items-center"]
    Icon["Camera / CameraOff Icon"]
    Label["'Screenshot mode'"]
    
    Footer --> FlexContainer
    FlexContainer --> LeftSide
    FlexContainer --> RightSide
    
    LeftSide --> CountText
    RightSide --> Button
    
    Button --> Icon
    Button --> Label
```

**Sources:** [email-agent/client/components/InboxView.tsx:158-177]()

---

