> 来源: [https://deepwiki.com/Tencent/WeKnora/5-chat-and-query-system](https://deepwiki.com/Tencent/WeKnora/5-chat-and-query-system)
> DeepWiki Tencent/WeKnora

# Chat and Query System

  Relevant source files 
 - [frontend/src/api/chat/streame.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/chat/streame.ts)
 - [frontend/src/components/sessionGrouping.test.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/sessionGrouping.test.ts)
 - [frontend/src/components/sessionGrouping.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/sessionGrouping.ts)
 - [frontend/src/utils/authRefresh.test.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/utils/authRefresh.test.ts)
 - [frontend/src/utils/authRefresh.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/utils/authRefresh.ts)
 - [frontend/src/utils/request.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/utils/request.ts)
 - [internal/application/repository/session.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/session.go)
 - [internal/application/repository/session_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/session_test.go)
 - [internal/application/service/session.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go)
 - [internal/application/service/session_user_scope_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session_user_scope_test.go)
 - [internal/handler/message_suggestion.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/message_suggestion.go)
 - [internal/handler/message_suggestion_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/message_suggestion_test.go)
 - [internal/handler/session/agent_stream_handler.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/agent_stream_handler.go)
 - [internal/handler/session/handler.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/handler.go)
 - [internal/handler/session/helpers.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/helpers.go)
 - [internal/handler/session/helpers_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/helpers_test.go)
 - [internal/handler/session/qa.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go)
 - [internal/handler/session/types.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/types.go)
 - [internal/types/chat_manage.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/chat_manage.go)
 - [internal/types/interfaces/session.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/interfaces/session.go)
 - [internal/types/message.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/message.go)
 - [internal/types/principal.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/principal.go)
 - [internal/types/session.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/session.go)
 - [internal/types/session_access_test.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/session_access_test.go)
 
  
## Purpose and Scope

 The Chat and Query System is WeKnora's conversational AI engine that coordinates natural language interaction, knowledge retrieval, autonomous agent execution, and real-time streaming over Server-Sent Events (SSE). It bridges client interfaces with backend retrieval pipelines, tool registries, and long-term memory systems.

 This page provides a high-level architectural overview of the chat and query subsystems. For detailed technical specifications, implementation details, and configuration, refer to the following child pages:

 
 - [Chat Interface and User Experience](https://deepwiki.com/Tencent/WeKnora/5.1-chat-interface-and-user-experience) — UI components, input features, streaming responses, and agent visualization.
 - [Knowledge QA Mode](https://deepwiki.com/Tencent/WeKnora/5.2-knowledge-qa-mode) — Normal RAG QA mode, query rewriting, retrieval strategies, and context formatting.
 - [Agent Mode and Tool Integration](https://deepwiki.com/Tencent/WeKnora/5.3-agent-mode-and-tool-integration) — ReAct loop execution, tool registration, invocation, and skill sandboxes.
 - [Session Management and Context](https://deepwiki.com/Tencent/WeKnora/5.4-session-management-and-context) — Session lifecycles, Redis context storage, history management, and auto-title generation.
 - [MCP Tool Integration](https://deepwiki.com/Tencent/WeKnora/5.5-mcp-tool-integration) — Model Context Protocol tool registration, proxying, and agent usage.
 - [Web Search Integration](https://deepwiki.com/Tencent/WeKnora/5.6-web-search-integration) — Web search providers, web fetching, and tool workflow integration.
 - [Embedded Chat Channels](https://deepwiki.com/Tencent/WeKnora/5.7-embedded-chat-channels) — Embeddable chat widgets, public session security, and external site embedding.
 
 
---

 
## Architecture Overview

 Conversational flows are initiated via REST endpoints in `internal/handler/session/qa.go`, processed through `qaRequestContext`, and handed off to `SessionService` implementations in `internal/application/service/session.go` [internal/handler/session/qa.go34-97](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L34-L97) [internal/application/service/session.go108-137](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L108-L137)

 
### Architecture Flow Diagram

 
```

```

 **Sources:**

 
 - [internal/handler/session/qa.go34-97](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L34-L97)
 - [internal/handler/session/qa.go99-162](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L99-L162)
 - [internal/application/service/session.go108-137](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L108-L137)
 - [frontend/src/api/chat/streame.ts43-155](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/chat/streame.ts#L43-L155)
 
 
---

 
## Core Sub-Topics

 
### 5.1 Chat Interface and User Experience

 The chat interface manages rich user interactions including Markdown rendering, multimodal image uploads, `@mention` tracking, and real-time streaming indicators. Client requests are dispatched using `useStream` in `frontend/src/api/chat/streame.ts`, which establishes an SSE connection and handles incremental payloads [frontend/src/api/chat/streame.ts28-156](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/chat/streame.ts#L28-L156)

 
```

```

 For detailed component breakdown, UI state handling, and rendering rules, see [Chat Interface and User Experience](https://deepwiki.com/Tencent/WeKnora/5.1-chat-interface-and-user-experience).

 **Sources:**

 
 - [frontend/src/api/chat/streame.ts28-156](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/chat/streame.ts#L28-L156)
 - [internal/handler/session/qa.go99-163](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L99-L163)
 - [internal/handler/session/agent_stream_handler.go83-108](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/agent_stream_handler.go#L83-L108)
 
 
### 5.2 Knowledge QA Mode

 Knowledge QA mode executes standard Retrieval-Augmented Generation (RAG). Queries are analyzed, optionally rewritten using query understanding models, matched against vector and keyword indexes, reranked, and injected into the LLM context.

 The underlying pipeline is defined by `ChatManage` and `PipelineRequest` structures in `internal/types/chat_manage.go`, which coordinate search targets, embedding thresholds, and rerank parameters [internal/types/chat_manage.go5-76](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/chat_manage.go#L5-L76) [internal/types/chat_manage.go146-164](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/chat_manage.go#L146-L164)

 For query rewriting, retrieval strategies, and prompt formatting, see [Knowledge QA Mode](https://deepwiki.com/Tencent/WeKnora/5.2-knowledge-qa-mode).

 **Sources:**

 
 - [internal/types/chat_manage.go5-76](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/chat_manage.go#L5-L76)
 - [internal/types/chat_manage.go146-164](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/chat_manage.go#L146-L164)
 - [internal/types/interfaces/session.go60-69](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/interfaces/session.go#L60-L69)
 
 
### 5.3 Agent Mode and Tool Integration

 When agent mode is enabled, execution transitions from static RAG to the ReAct (Reasoning and Acting) framework. The agent evaluates goals iteratively, invokes tools via `AgentStreamHandler`, and manages intermediate thoughts, tool calls, and final answers [internal/application/service/session.go67-69](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L67-L69) [internal/handler/session/agent_stream_handler.go110-130](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/agent_stream_handler.go#L110-L130)

 
### Agent Execution Diagram

 
```

```

 For details on the ReAct loop, tool registration, and skill execution, see [Agent Mode and Tool Integration](https://deepwiki.com/Tencent/WeKnora/5.3-agent-mode-and-tool-integration).

 **Sources:**

 
 - [internal/application/service/session.go67-69](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L67-L69)
 - [internal/handler/session/agent_stream_handler.go110-130](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/agent_stream_handler.go#L110-L130)
 - [internal/handler/session/agent_stream_handler.go132-177](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/agent_stream_handler.go#L132-L177)
 
 
### 5.4 Session Management and Context

 Conversation sessions provide the container for message histories, metadata, and user scopes. Sessions are managed by `sessionService` and persisted via `SessionRepository`. Conversation history is dynamically rebuilt from the `messages` table on demand rather than relying on cross-turn caches [internal/application/service/session.go108-138](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L108-L138)

 Key repository queries enforce strict tenant and user scopes:

 
 - `GetOwnedSession` [internal/types/interfaces/session.go21](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/interfaces/session.go#L21-L21)
 - `loadSessionForRead` [internal/application/service/session.go62-101](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L62-L101)
 - `QueryPaged` [internal/application/repository/session.go142-190](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/session.go#L142-L190)
 
 For session lifecycles, history loading, and Redis context storage, see [Session Management and Context](https://deepwiki.com/Tencent/WeKnora/5.4-session-management-and-context).

 **Sources:**

 
 - [internal/application/service/session.go108-138](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L108-L138)
 - [internal/types/interfaces/session.go10-40](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/interfaces/session.go#L10-L40)
 - [internal/application/repository/session.go44-93](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/session.go#L44-L93)
 
 
### 5.5 MCP Tool Integration

 WeKnora supports the Model Context Protocol (MCP), enabling external tool services to be discovered, registered, and invoked dynamically during agent execution. MCP services can be selected per-request via `@mentions` or bound at the agent configuration level [internal/handler/session/qa.go49](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L49-L49) [internal/handler/session/types.go53](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/types.go#L53-L53)

 For MCP server registration, configuration, and agent invocation protocols, see [MCP Tool Integration](https://deepwiki.com/Tencent/WeKnora/5.5-mcp-tool-integration).

 **Sources:**

 
 - [internal/handler/session/qa.go49](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L49-L49)
 - [internal/handler/session/types.go53](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/types.go#L53-L53)
 
 
### 5.6 Web Search Integration

 Web search capabilities allow agents and RAG queries to augment local knowledge bases with live internet results. When `WebSearchEnabled` is set on the request or agent configuration, queries route through configured search providers, optionally triggering automated full-page web fetches for reranking [internal/handler/session/qa.go52](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L52-L52) [internal/types/chat_manage.go70-74](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/chat_manage.go#L70-L74)

 For web search provider setup, tool configurations, and agent workflow integration, see [Web Search Integration](https://deepwiki.com/Tencent/WeKnora/5.6-web-search-integration).

 **Sources:**

 
 - [internal/handler/session/qa.go52](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/session/qa.go#L52-L52)
 - [internal/types/chat_manage.go70-74](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/chat_manage.go#L70-L74)
 
 
### 5.7 Embedded Chat Channels

 Embedded chat channels allow WeKnora chat interfaces to be deployed as embeddable widgets on external websites. This subsystem manages channel configurations, the `EmbedChatCore` UI, secure public session flows, and script injection [frontend/src/api/chat/streame.ts55-61](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/chat/streame.ts#L55-L61) [internal/application/service/session.go45-51](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L45-L51)

 For embed configuration, widget UI structures, and authentication protocols, see [Embedded Chat Channels](https://deepwiki.com/Tencent/WeKnora/5.7-embedded-chat-channels).

 **Sources:**

 
 - [frontend/src/api/chat/streame.ts55-61](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/chat/streame.ts#L55-L61)
 - [internal/application/service/session.go45-51](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/session.go#L45-L51)
