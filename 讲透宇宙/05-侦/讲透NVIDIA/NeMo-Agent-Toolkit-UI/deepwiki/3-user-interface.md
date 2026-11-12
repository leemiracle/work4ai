<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Agent-Toolkit-UI · page 3 User Interface · fetched 2026-10-26 -->

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [public/screenshots/ui_generate_example.png](public/screenshots/ui_generate_example.png)
- [public/screenshots/ui_home_page.png](public/screenshots/ui_home_page.png)

</details>



This document provides an overview of the user interface architecture and components that make up the AIQ Toolkit-UI frontend application. The UI serves as the primary interaction layer between users and AI agents, providing a chat-based interface for human-in-the-loop workflows and agent communication.

For detailed information about specific chat interface components, see [Chat Interface Components](#3.1). For content rendering mechanisms, see [Content Rendering](#3.2). For human-in-the-loop workflow features, see [Human-in-the-Loop Features](#3.3).

## UI Architecture Overview

The AIQ Toolkit-UI is built as a Next.js React application that provides a modern, responsive web interface for interacting with AI agents and workflows. The architecture follows a component-based design with clear separation between presentation, communication, and data processing layers.

```mermaid
graph TB
    subgraph "Frontend Application Layer"
        App["App Component<br/>Next.js Application Root"]
        Layout["Layout Component<br/>Application Shell"]
        Auth["Authentication UI<br/>Login/Session Management"]
    end
    
    subgraph "Core UI Components"
        Chat["Chat Component<br/>Main Interface"]
        Input["ChatInput Component<br/>Message Input Interface"]
        History["MessageHistory Component<br/>Conversation Display"]
        Settings["SettingsPanel Component<br/>Configuration UI"]
    end
    
    subgraph "Content Display Components"
        Markdown["MarkdownRenderer<br/>Text Content Display"]
        Charts["ChartRenderer<br/>Data Visualization"]
        Code["CodeHighlighter<br/>Syntax Highlighting"]
        Math["MathRenderer<br/>Mathematical Equations"]
    end
    
    subgraph "Utility Components"
        FileUpload["FileUpload<br/>File Processing UI"]
        ImageCompress["ImageCompressor<br/>Image Optimization"]
        Export["ExportUtils<br/>Content Export Features"]
    end
    
    App --> Layout
    Layout --> Auth
    Layout --> Chat
    
    Chat --> Input
    Chat --> History
    Chat --> Settings
    
    History --> Markdown
    History --> Charts
    History --> Code
    History --> Math
    
    Input --> FileUpload
    Input --> ImageCompress
    Chat --> Export
```

Sources: Based on system architecture diagrams and Next.js application patterns

## Component Hierarchy and Responsibilities

The user interface follows a hierarchical component structure designed for modularity and reusability. Each component has specific responsibilities within the overall user experience.

| Component Level | Component Name | Primary Responsibility | Key Features |
|----------------|----------------|----------------------|--------------|
| Application | `App` | Root application container | Next.js routing, global state |
| Layout | `Layout` | Application shell and navigation | Header, sidebar, main content area |
| Authentication | `AuthPage` | User authentication flow | OAuth integration, session management |
| Chat Interface | `Chat` | Main conversation interface | Message display, input handling |
| Input | `ChatInput` | User message input | Text input, file upload, formatting |
| Display | `MessageHistory` | Conversation history | Message rendering, scrolling |
| Settings | `SettingsPanel` | Configuration interface | Communication mode, preferences |

Sources: Inferred from architectural patterns and component responsibilities

## User Experience Flow

The primary user interaction flow follows a structured pattern from authentication through active conversation with AI agents.

```mermaid
sequenceDiagram
    participant User
    participant AuthUI as "Authentication UI"
    participant ChatUI as "Chat Interface"
    participant InputComponent as "Chat Input Component"
    participant MessageDisplay as "Message Display"
    participant Backend as "AIQ Backend"
    
    User->>AuthUI: "Access Application"
    AuthUI->>User: "Display Login Form"
    User->>AuthUI: "Enter Credentials"
    AuthUI->>Backend: "Authenticate User"
    Backend->>AuthUI: "Return Session Token"
    AuthUI->>ChatUI: "Redirect to Chat"
    
    ChatUI->>User: "Display Chat Interface"
    User->>InputComponent: "Type Message"
    User->>InputComponent: "Upload Files (Optional)"
    InputComponent->>Backend: "Send Message + Files"
    Backend->>MessageDisplay: "Stream Response"
    MessageDisplay->>User: "Display AI Response"
    
    loop "Ongoing Conversation"
        User->>InputComponent: "Continue Conversation"
        InputComponent->>Backend: "Send Follow-up"
        Backend->>MessageDisplay: "Stream Response"
        MessageDisplay->>User: "Display Response"
    end
```

Sources: Based on authentication flow and chat system communication patterns

## Communication Integration

The UI seamlessly integrates with backend services through dual communication protocols, allowing users to choose between HTTP and WebSocket modes based on their needs and network conditions.

```mermaid
graph LR
    subgraph "User Interface Layer"
        ChatInterface["Chat Interface Component"]
        ModeSelector["Communication Mode Selector"]
        MessageQueue["Message Queue Manager"]
    end
    
    subgraph "Communication Layer"
        HTTPClient["HTTP Client<br/>chat.ts"]
        WSClient["WebSocket Client<br/>ws-handler.ts"]
        ErrorHandler["Error Handler<br/>Network Recovery"]
    end
    
    subgraph "Backend Integration"
        HTTPEndpoints["HTTP API Endpoints<br/>/generate, /chat, /stream"]
        WSEndpoint["WebSocket Endpoint<br/>/websocket"]
        AIAgents["AI Agent Services"]
    end
    
    ChatInterface --> ModeSelector
    ModeSelector --> HTTPClient
    ModeSelector --> WSClient
    ChatInterface --> MessageQueue
    
    HTTPClient --> HTTPEndpoints
    WSClient --> WSEndpoint
    HTTPClient --> ErrorHandler
    WSClient --> ErrorHandler
    
    HTTPEndpoints --> AIAgents
    WSEndpoint --> AIAgents
```

Sources: Based on communication protocol architecture and backend integration patterns

## Content Processing Pipeline

The UI incorporates sophisticated content processing capabilities to handle various types of user input and AI-generated output, including text, images, mathematical equations, and structured data.

```mermaid
graph TB
    subgraph "Input Processing"
        UserInput["User Input Interface"]
        FileValidator["File Validation<br/>fileValidation.ts"]
        ImageProcessor["Image Compression<br/>imageUtils.ts"]
    end
    
    subgraph "Content Rendering Engine"
        MarkdownEngine["Markdown Processor<br/>ReactMarkdown"]
        MathEngine["Math Renderer<br/>MathJax Integration"]
        CodeEngine["Code Highlighter<br/>SyntaxHighlighter"]
        ChartEngine["Chart Renderer<br/>Chart.js/Recharts"]
    end
    
    subgraph "Output Display"
        MessageContainer["Message Container"]
        ContentRenderer["Content Renderer"]
        ExportFunctions["Export Functions<br/>pptxUtils.ts"]
    end
    
    UserInput --> FileValidator
    UserInput --> ImageProcessor
    
    FileValidator --> MarkdownEngine
    ImageProcessor --> MarkdownEngine
    
    MarkdownEngine --> MathEngine
    MarkdownEngine --> CodeEngine
    MarkdownEngine --> ChartEngine
    
    MathEngine --> MessageContainer
    CodeEngine --> MessageContainer
    ChartEngine --> MessageContainer
    
    MessageContainer --> ContentRenderer
    ContentRenderer --> ExportFunctions
```

Sources: Based on content processing pipeline and rendering capabilities

## State Management and Data Flow

The UI implements a unidirectional data flow pattern with centralized state management for conversation history, user preferences, and application configuration.

| State Category | Management Approach | Key Data | Update Triggers |
|---------------|-------------------|----------|----------------|
| Authentication | NextAuth.js session | User credentials, tokens | Login/logout events |
| Conversation | Component state | Message history, current thread | New messages, user actions |
| UI Preferences | Local storage | Theme, language, settings | User configuration changes |
| Communication | Context providers | Connection status, mode | Network events, user selection |
| File Processing | Temporary state | Upload progress, validation | File operations |

Sources: Based on state management patterns and data flow architecture

The user interface serves as the primary touchpoint for users interacting with the AIQ Toolkit system, providing an intuitive and feature-rich environment for AI-powered conversations and workflows. The modular design ensures maintainability while the dual communication protocols provide flexibility for different use cases and network conditions.

---

