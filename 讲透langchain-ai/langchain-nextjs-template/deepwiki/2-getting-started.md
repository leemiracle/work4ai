<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchain-nextjs-template · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [package.json](package.json)
- [yarn.lock](yarn.lock)

</details>



This document provides instructions on how to set up, configure, and run the LangChain NextJS Template. For information about system architecture, see [System Architecture](#3), and for details on specific features, see the [Features](#4) section.

## Prerequisites

Before beginning, ensure you have:

```mermaid
flowchart LR
    A["Prerequisites"] --> B["Node.js ≥ 18"]
    A --> C["Package Manager (yarn or npm)"]
    A --> D["API Keys"]
    D --> D1["OPENAI_API_KEY (required)"]
    D --> D2["SERPAPI_API_KEY (for agents)"]
    D --> D3["SUPABASE_URL and SUPABASE_PRIVATE_KEY (for retrieval)"]
```

Sources: [package.json:13-16](), [README.md:29-32]()

## Installation

### Clone the Repository

```bash
git clone https://github.com/langchain-ai/langchain-nextjs-template.git
cd langchain-nextjs-template
```

### Set Up Environment Variables

Create a `.env.local` file in the root directory:

```bash
cp .env.example .env.local
```

At minimum, add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
LANGCHAIN_CALLBACKS_BACKGROUND=false  # For tracing to complete in serverless edge functions
```

### Install Dependencies

```bash
# Using yarn
yarn

# Using npm
npm install
```

Sources: [package.json:5-11](), [README.md:25-34]()

## Running the Application

### Development Server

```bash
# Using yarn
yarn dev

# Using npm
npm run dev
```

Access the application at [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
# Using yarn
yarn build
yarn start

# Using npm
npm run build
npm start
```

Sources: [package.json:6-10]()

## Project Structure Overview

The template is organized according to the Next.js App Router pattern:

```mermaid
flowchart TD
    Root["Project Root"] --> AppDir["app/"]
    Root --> ComponentsDir["components/"]
    Root --> PublicDir["public/"]
    
    AppDir --> APIDir["api/ (Backend Routes)"]
    AppDir --> Pages["*/page.tsx (Frontend Pages)"]
    AppDir --> LayoutFile["layout.tsx (Root Layout)"]
    
    APIDir --> ChatAPIDir["chat/ (LLM Interactions)"]
    APIDir --> RetrievalAPIDir["retrieval/ (Vector Storage)"]
    
    ChatAPIDir --> SimpleChatRoute["route.ts (Basic Chat Chain)"]
    ChatAPIDir --> StructuredOutputRoute["structured_output/route.ts (Function Calling)"]
    ChatAPIDir --> AgentsRoute["agents/route.ts (ReActAgent)"]
    ChatAPIDir --> RetrievalRoute["retrieval/route.ts (RAG Chain)"]
    ChatAPIDir --> RetrievalAgentsRoute["retrieval_agents/route.ts (RAG Agent)"]
    
    RetrievalAPIDir --> IngestRoute["ingest/route.ts (Document Loader)"]
    
    ComponentsDir --> ChatWindowComponent["ChatWindow.tsx (Chat UI)"]
    ComponentsDir --> GuideInfoBox["GuideInfoBox.tsx (Documentation UI)"]
    ComponentsDir --> MessageBubble["ChatMessageBubble.tsx (Message Display)"]
```

Sources: [app/layout.tsx:33-112](), [README.md:8-14]()

## Data Flow and Components

This diagram shows how user requests flow through the system:

```mermaid
sequenceDiagram
    participant User
    participant NextUI as "Next.js Frontend (ChatWindow)"
    participant APIRoutes as "API Routes"
    participant LangChain as "LangChain.js Components"
    participant ExternalAPI as "External Services (OpenAI, Supabase, SERPAPI)"
    
    User->>NextUI: Enter query
    NextUI->>APIRoutes: POST /api/chat/{endpoint}
    
    alt Basic Chat
        APIRoutes->>LangChain: createChatChain()
        LangChain->>ExternalAPI: Call OpenAI
        ExternalAPI-->>LangChain: Return response
    else Structured Output
        APIRoutes->>LangChain: createStructuredOutputChain()
        LangChain->>ExternalAPI: OpenAI function call
        ExternalAPI-->>LangChain: Return structured JSON
    else Agents
        APIRoutes->>LangChain: createReactAgent()
        LangChain->>ExternalAPI: Generate reasoning steps
        ExternalAPI-->>LangChain: Return reasoning
        LangChain->>ExternalAPI: Use tools (SERPAPI, etc.)
        ExternalAPI-->>LangChain: Tool responses
        LangChain->>ExternalAPI: Generate final answer
        ExternalAPI-->>LangChain: Final response
    else Retrieval
        APIRoutes->>LangChain: createRetrievalChain()
        LangChain->>ExternalAPI: Query Supabase vector store
        ExternalAPI-->>LangChain: Return relevant documents
        LangChain->>ExternalAPI: Generate response with context
        ExternalAPI-->>LangChain: Return response with sources
    end
    
    LangChain-->>APIRoutes: Stream response tokens
    APIRoutes-->>NextUI: Stream tokens to UI
    NextUI-->>User: Display streaming response
```

Sources: [README.md:9-14]()

## Core Dependencies

The template relies on several key packages:

| Dependency | Version | Purpose |
|------------|---------|---------|
| @langchain/community | ^0.3.37 | Community-contributed LangChain components |
| @langchain/core | ^0.3.43 | Core LangChain functionality |
| @langchain/langgraph | ^0.2.57 | Framework for building agentic workflows |
| @langchain/openai | ^0.4.9 | OpenAI integration for LangChain |
| @supabase/supabase-js | ^2.32.0 | Vector storage for retrieval examples |
| langchain | ^0.3.19 | Main LangChain library |
| next | ^15.2.4 | Next.js framework |
| ai | ^3.1.12 | Vercel AI SDK for streaming responses |
| react | ^18.3.1 | React framework |
| zod | ^3.23.8 | Schema validation and type generation |

Sources: [package.json:16-47]()

## Feature Examples

The template includes multiple examples demonstrating LangChain capabilities:

| Feature | URL Path | API Route | Description |
|---------|----------|-----------|-------------|
| Basic Chat | / | /api/chat/route.ts | Simple conversation with streaming |
| Structured Output | /structured_output | /api/chat/structured_output/route.ts | Generates structured data using function calling |
| Agents | /agents | /api/chat/agents/route.ts | ReAct agents with web search and calculator tools |
| Retrieval | /retrieval | /api/chat/retrieval/route.ts | RAG with Supabase vector store |
| Retrieval Agents | /retrieval_agents | /api/chat/retrieval_agents/route.ts | Combines agents with document retrieval |
| React Server Components | /ai_sdk | Direct server component integration | Server-side streaming without API routes |
| LangGraph | /langgraph | Custom LangGraph implementation | Complex multi-step agent workflows |

Sources: [app/layout.tsx:74-87](), [README.md:9-17]()

## Environment Configuration

Required environment variables for various features:

```bash
# Required for all examples
OPENAI_API_KEY=sk-...

# For tracing in serverless environments
LANGCHAIN_CALLBACKS_BACKGROUND=false

# For agent examples
SERPAPI_API_KEY=serpapi_...

# For retrieval examples
SUPABASE_URL=https://...
SUPABASE_PRIVATE_KEY=eyJ...

# Optional for tracing and debugging
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
```

Sources: [README.md:29-32](), [README.md:64-86]()

## Next Steps

Once the application is running, you can:

1. Explore the different examples through the navigation bar
2. Examine the code in each API route to understand implementation details
3. Modify the chains, agents, or retrievers to suit your specific use case
4. Deploy to Vercel or another platform that supports Next.js

For deployment instructions, see [README.md:120-124]().

For more detailed information on specific features, refer to the [Features Overview](#4) section.

---

