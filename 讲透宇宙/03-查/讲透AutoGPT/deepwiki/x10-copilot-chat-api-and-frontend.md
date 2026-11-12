<!-- source: DeepWiki mcp.deepwiki.com · repo Significant-Gravitas/AutoGPT · extra page Copilot Chat API and Frontend · fetched 2026-10-26 -->

# Copilot Chat API and Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [autogpt_platform/backend/backend/api/features/chat/routes.py](autogpt_platform/backend/backend/api/features/chat/routes.py)
- [autogpt_platform/backend/backend/api/features/chat/routes_test.py](autogpt_platform/backend/backend/api/features/chat/routes_test.py)
- [autogpt_platform/backend/backend/copilot/db.py](autogpt_platform/backend/backend/copilot/db.py)
- [autogpt_platform/backend/backend/copilot/db_test.py](autogpt_platform/backend/backend/copilot/db_test.py)
- [autogpt_platform/backend/backend/copilot/model.py](autogpt_platform/backend/backend/copilot/model.py)
- [autogpt_platform/backend/backend/copilot/model_test.py](autogpt_platform/backend/backend/copilot/model_test.py)
- [autogpt_platform/backend/backend/data/db_manager.py](autogpt_platform/backend/backend/data/db_manager.py)
- [autogpt_platform/backend/backend/platform_linking/chat.py](autogpt_platform/backend/backend/platform_linking/chat.py)
- [autogpt_platform/backend/backend/platform_linking/chat_test.py](autogpt_platform/backend/backend/platform_linking/chat_test.py)
- [autogpt_platform/frontend/public/integrations/teams.png](autogpt_platform/frontend/public/integrations/teams.png)
- [autogpt_platform/frontend/public/integrations/whatsapp.png](autogpt_platform/frontend/public/integrations/whatsapp.png)
- [autogpt_platform/frontend/src/app/(platform)/copilot/CopilotPage.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/CopilotPage.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/__tests__/store.test.ts](autogpt_platform/frontend/src/app/(platform)/copilot/__tests__/store.test.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactCard/ArtifactCard.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactCard/ArtifactCard.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/ArtifactContent.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/ArtifactContent.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/ArtifactDragHandle.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/ArtifactDragHandle.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/ArtifactErrorBoundary.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/ArtifactErrorBoundary.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/__tests__/ArtifactContent.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/__tests__/ArtifactContent.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/__tests__/ArtifactDragHandle.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/__tests__/ArtifactDragHandle.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/__tests__/reactArtifactPreview.test.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/__tests__/reactArtifactPreview.test.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/reactArtifactPreview.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/reactArtifactPreview.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/useArtifactContent.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/components/useArtifactContent.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/helpers.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ArtifactPanel/helpers.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatContainer/ChatContainer.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatContainer/ChatContainer.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatContainer/useAutoOpenArtifacts.test.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatContainer/useAutoOpenArtifacts.test.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatContainer/useAutoOpenArtifacts.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatContainer/useAutoOpenArtifacts.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/ChatInput.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/ChatInput.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/__tests__/ChatInput.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/__tests__/ChatInput.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/DryRunToggleButton.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/DryRunToggleButton.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/FileChips.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/FileChips.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/ModeToggleButton.stories.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/ModeToggleButton.stories.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/ModeToggleButton.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/ModeToggleButton.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/ModelToggleButton.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/ModelToggleButton.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/RecordingButton.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/RecordingButton.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/__tests__/DryRunToggleButton.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/__tests__/DryRunToggleButton.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/__tests__/ModelToggleButton.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatInput/components/__tests__/ModelToggleButton.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/ChatMessagesContainer.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/ChatMessagesContainer.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/__tests__/ChatMessagesContainer.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/__tests__/ChatMessagesContainer.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/__tests__/LoadMoreSentinel.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/__tests__/LoadMoreSentinel.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/components/CopyButton.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/components/CopyButton.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/components/TTSButton.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/components/TTSButton.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/helpers.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/helpers.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatOriginIcon/ChatOriginIcon.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatOriginIcon/ChatOriginIcon.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/ChatSearchModal.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/ChatSearchModal.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/ChatSearchResults.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/ChatSearchResults.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/__tests__/ChatSearchModal.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/__tests__/ChatSearchModal.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/__tests__/helpers.test.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/__tests__/helpers.test.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/helpers.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/helpers.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/useChatSearch.ts](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSearchModal/useChatSearch.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSessionBlock/ChatSessionBlock.stories.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSessionBlock/ChatSessionBlock.stories.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSidebar/ChatSidebar.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSidebar/ChatSidebar.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSidebar/__tests__/ChatSidebar.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatSidebar/__tests__/ChatSidebar.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/MobileDrawer/MobileDrawer.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/MobileDrawer/MobileDrawer.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/MobileDrawer/__tests__/MobileDrawer.test.tsx](autogpt_platform/frontend/src/app/(platform)/copilot/components/MobileDrawer/__tests__/MobileDrawer.test.tsx)
- [autogpt_platform/frontend/src/app/(platform)/copilot/helpers/__tests__/convertChatSessionToUiMessages.test.ts](autogpt_platform/frontend/src/app/(platform)/copilot/helpers/__tests__/convertChatSessionToUiMessages.test.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/helpers/convertChatSessionToUiMessages.ts](autogpt_platform/frontend/src/app/(platform)/copilot/helpers/convertChatSessionToUiMessages.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/store.ts](autogpt_platform/frontend/src/app/(platform)/copilot/store.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/useChatSession.ts](autogpt_platform/frontend/src/app/(platform)/copilot/useChatSession.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotPage.ts](autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotPage.ts)
- [autogpt_platform/frontend/src/app/(platform)/copilot/useLoadMoreMessages.ts](autogpt_platform/frontend/src/app/(platform)/copilot/useLoadMoreMessages.ts)
- [autogpt_platform/frontend/src/app/api/openapi.json](autogpt_platform/frontend/src/app/api/openapi.json)
- [autogpt_platform/frontend/src/components/contextual/Chat/components/ChatMessage/useTextToSpeech.ts](autogpt_platform/frontend/src/components/contextual/Chat/components/ChatMessage/useTextToSpeech.ts)
- [autogpt_platform/frontend/src/components/contextual/OutputRenderers/renderers/HTMLRenderer.tsx](autogpt_platform/frontend/src/components/contextual/OutputRenderers/renderers/HTMLRenderer.tsx)
- [autogpt_platform/frontend/src/lib/__tests__/iframe-sandbox-csp.test.ts](autogpt_platform/frontend/src/lib/__tests__/iframe-sandbox-csp.test.ts)
- [autogpt_platform/frontend/src/lib/iframe-sandbox-csp.ts](autogpt_platform/frontend/src/lib/iframe-sandbox-csp.ts)
- [autogpt_platform/frontend/src/services/feature-flags/use-get-flag.ts](autogpt_platform/frontend/src/services/feature-flags/use-get-flag.ts)

</details>



This page documents the backend API routes and frontend components that power the Copilot chat interface. It covers session management (CRUD), Server-Sent Events (SSE) for real-time updates, message hydration and pagination, rate limiting, and the key React components (`CopilotPage`, `useCopilotPage`, `ChatMessagesContainer`).

## Backend Chat API (FastAPI)

The Copilot chat functionality is exposed via a set of FastAPI routes defined in `backend/api/features/chat/routes.py`(). These routes handle the lifecycle of chat sessions, message streaming, and interaction with the Copilot's underlying execution engine.

### Session Management

Chat sessions are managed through standard CRUD operations. A `ChatSession` represents a conversation with the Copilot, storing metadata and linking to `ChatMessage` records.

#### Create Session

A new chat session can be initiated via a POST request. The session can optionally be created in a `dry_run` mode, which affects how the Copilot executes tasks.
- **Endpoint**: `POST /sessions`
- **Request Body**: `CreateSessionRequest` [autogpt_platform/backend/backend/api/features/chat/routes.py:209-213]()
- **Response**: `CreateSessionResponse` [autogpt_platform/backend/backend/api/features/chat/routes.py:215-219]() containing the `session_id`.
- **Implementation**: The `create_session` function [autogpt_platform/backend/backend/api/features/chat/routes.py:221-240]() handles this, calling `backend.copilot.model.create_chat_session` [autogpt_platform/backend/backend/copilot/model.py:309-329]() to persist the session in the database.

#### Get Session

Retrieving a session fetches its metadata and a paginated list of messages.
- **Endpoint**: `GET /sessions/{session_id}`
- **Response**: `GetSessionResponse` [autogpt_platform/backend/backend/api/features/chat/routes.py:242-250]() which includes `ChatSessionInfo` [autogpt_platform/backend/backend/copilot/model.py:177-190]() and `PaginatedMessages` [autogpt_platform/backend/backend/copilot/db.py:32-36]().
- **Implementation**: The `get_session` function [autogpt_platform/backend/backend/api/features/chat/routes.py:252-308]() uses `backend.copilot.db.get_chat_messages_paginated` [autogpt_platform/backend/backend/copilot/db.py:70-149]() to retrieve messages. It also includes logic to handle orphaned running sessions by calling `_try_release_orphan_running` [autogpt_platform/backend/backend/api/features/chat/routes.py:142-162]().

#### Update Session Title

The title of a chat session can be updated.
- **Endpoint**: `PATCH /sessions/{session_id}/title`
- **Request Body**: `UpdateSessionTitleRequest` [autogpt_platform/backend/backend/api/features/chat/routes.py:310-313]()
- **Response**: `UpdateSessionTitleResponse` [autogpt_platform/backend/backend/api/features/chat/routes.py:315-318]()
- **Implementation**: `update_session_title_route` [autogpt_platform/backend/backend/api/features/chat/routes.py:320-337]() calls `backend.copilot.model.update_session_title` [autogpt_platform/backend/backend/copilot/model.py:331-344]().

#### Delete Session

A chat session can be deleted.
- **Endpoint**: `DELETE /sessions/{session_id}`
- **Response**: `DeleteSessionResponse` [autogpt_platform/backend/backend/api/features/chat/routes.py:339-342]()
- **Implementation**: `delete_session_route` [autogpt_platform/backend/backend/api/features/chat/routes.py:344-357]() calls `backend.copilot.model.delete_chat_session` [autogpt_platform/backend/backend/copilot/model.py:346-357]().

#### List Sessions

Users can retrieve a paginated list of their chat sessions.
- **Endpoint**: `GET /sessions`
- **Response**: `ListSessionsResponse` [autogpt_platform/backend/backend/api/features/chat/routes.py:359-364]()
- **Implementation**: `list_sessions` [autogpt_platform/backend/backend/api/features/chat/routes.py:366-386]() uses `backend.copilot.model.get_user_sessions` [autogpt_platform/backend/backend/copilot/model.py:359-379]() to fetch sessions.

#### Builder Session

A special endpoint exists for builder-related sessions, allowing retrieval or creation of a session tied to a specific agent graph.
- **Endpoint**: `GET /sessions/builder/{agent_id}`
- **Response**: `GetSessionResponse` [autogpt_platform/backend/backend/api/features/chat/routes.py:242-250]()
- **Implementation**: `get_builder_session` [autogpt_platform/backend/backend/api/features/chat/routes.py:388-410]() uses `backend.copilot.model.get_or_create_builder_session` [autogpt_platform/backend/backend/copilot/model.py:381-409]().

Sources:
- [autogpt_platform/backend/backend/api/features/chat/routes.py:209-410]()
- [autogpt_platform/backend/backend/copilot/model.py:177-190]()
- [autogpt_platform/backend/backend/copilot/model.py:309-409]()
- [autogpt_platform/backend/backend/copilot/db.py:32-36]()
- [autogpt_platform/backend/backend/copilot/db.py:70-149]()

### Message Streaming (SSE)

The core of the Copilot chat is real-time message streaming using Server-Sent Events (SSE). This allows the frontend to receive updates as the Copilot processes requests and generates responses.

- **Endpoint**: `POST /sessions/{session_id}/stream`
- **Request Body**: `StreamChatRequest` [autogpt_platform/backend/backend/api/features/chat/routes.py:193-200]()
- **Response**: `StreamingResponse` [autogpt_platform/backend/backend/api/features/chat/routes.py:412-500]() with `text/event-stream` content type.
- **Implementation**:
    - The `stream_chat_post` function [autogpt_platform/backend/backend/api/features/chat/routes.py:412-500]() is the entry point.
    - It first validates the session and checks for rate limits and concurrent turn limits.
    - It then calls `backend.copilot.executor.utils.schedule_chat_turn` [autogpt_platform/backend/backend/copilot/executor/utils.py]() to enqueue the user's message for processing.
    - If a turn is successfully scheduled, it enters an `async for` loop over `backend.copilot.stream_registry.stream_events` [autogpt_platform/backend/backend/copilot/stream_registry.py]() to yield events as they arrive.
    - Events are serialized to JSON and formatted as SSE messages.
    - The `_strip_injected_context` helper [autogpt_platform/backend/backend/api/features/chat/routes.py:170-188]() removes internal context blocks from messages before sending them to the frontend.

#### Event Types

The SSE stream can emit various event types, including:
- `StreamStart` [autogpt_platform/backend/backend/copilot/response_model.py:10-13]()
- `StreamStartStep` [autogpt_platform/backend/backend/copilot/response_model.py:15-18]()
- `StreamHeartbeat` [autogpt_platform/backend/backend/copilot/response_model.py:20-23]()
- `StreamFinishStep` [autogpt_platform/backend/backend/copilot/response_model.py:25-28]()
- `StreamFinish` [autogpt_platform/backend/backend/copilot/response_model.py:30-33]()
- `StreamError` [autogpt_platform/backend/backend/copilot/response_model.py:35-38]()
- Various tool-specific response models like `AgentOutputResponse`, `BlockOutputResponse`, `ClarificationNeededResponse`, etc. [autogpt_platform/backend/backend/api/features/chat/routes.py:74-101]()

#### Pending Messages

If a user sends a message while another turn is in progress, the message is queued.
- **Endpoint**: `POST /sessions/{session_id}/pending`
- **Request Body**: `QueuePendingMessageRequest` [autogpt_platform/backend/backend/api/features/chat/routes.py:502-505]()
- **Response**: `QueuePendingMessageResponse` [autogpt_platform/backend/backend/copilot/pending_message_helpers.py:16-19]()
- **Implementation**: `queue_pending_message` [autogpt_platform/backend/backend/api/features/chat/routes.py:507-526]() uses `backend.copilot.pending_message_helpers.queue_pending_for_http` [autogpt_platform/backend/backend/copilot/pending_message_helpers.py:30-46]() to store the message in Redis.

Sources:
- [autogpt_platform/backend/backend/api/features/chat/routes.py:170-188]()
- [autogpt_platform/backend/backend/api/features/chat/routes.py:193-200]()
- [autogpt_platform/backend/backend/api/features/chat/routes.py:412-500]()
- [autogpt_platform/backend/backend/api/features/chat/routes.py:502-505]()
- [autogpt_platform/backend/backend/api/features/chat/routes.py:507-526]()
- [autogpt_platform/backend/backend/copilot/executor/utils.py]()
- [autogpt_platform/backend/backend/copilot/pending_message_helpers.py:16-19]()
- [autogpt_platform/backend/backend/copilot/pending_message_helpers.py:30-46]()
- [autogpt_platform/backend/backend/copilot/response_model.py:10-38]()
- [autogpt_platform/backend/backend/copilot/stream_registry.py]()

### Message Hydration and Pagination

Messages are stored in the database and retrieved in a paginated manner to optimize performance and reduce initial load times.

- **`backend.copilot.db.get_chat_messages_paginated`** [autogpt_platform/backend/backend/copilot/db.py:70-149](): This function is central to message retrieval.
    - It fetches a window of messages for a given `session_id`.
    - Supports cursor-based pagination using `before_sequence` for UI scroll-back.
    - Can fetch the most recent messages (tail load) or a specific range.
    - Includes logic to `_expand_tool_boundary` [autogpt_platform/backend/backend/copilot/db.py:151-190]() and `_expand_for_visibility` [autogpt_platform/backend/backend/copilot/db.py:192-231]() to ensure that tool calls and their responses are always displayed together, even if they span pagination boundaries. This prevents malformed chat displays.
    - Returns `PaginatedMessages` [autogpt_platform/backend/backend/copilot/db.py:32-36]() which includes the messages, a `has_more` flag, the `oldest_sequence` number, and `ChatSessionInfo`.
- **`ChatMessage.from_db`** [autogpt_platform/backend/backend/copilot/model.py:105-122](): Converts Prisma ORM `ChatMessage` objects into Pydantic `ChatMessage` models for API responses.

Sources:
- [autogpt_platform/backend/backend/copilot/db.py:32-36]()
- [autogpt_platform/backend/backend/copilot/db.py:70-149]()
- [autogpt_platform/backend/backend/copilot/db.py:151-190]()
- [autogpt_platform/backend/backend/copilot/db.py:192-231]()
- [autogpt_platform/backend/backend/copilot/model.py:105-122]()

### Rate Limiting

The Copilot API implements rate limiting to manage resource usage and prevent abuse.

- **Implementation**: The `stream_chat_post` route [autogpt_platform/backend/backend/api/features/chat/routes.py:412-500]() calls `backend.copilot.rate_limit.check_rate_limit` [autogpt_platform/backend/backend/copilot/rate_limit.py]() and `backend.copilot.rate_limit.enforce_payment_paywall` [autogpt_platform/backend/backend/copilot/rate_limit.py]() before processing a new message.
- **Endpoints**:
    - `GET /usage` [autogpt_platform/backend/backend/api/features/chat/routes.py:528-544](): Retrieves the user's current Copilot usage status.
    - `POST /usage/reset` [autogpt_platform/backend/backend/api/features/chat/routes.py:546-570](): Allows resetting daily usage (if applicable).
- **Error Handling**: If rate limits are exceeded, a `RateLimitExceeded` exception is raised, resulting in a 429 HTTP status code.

Sources:
- [autogpt_platform/backend/backend/api/features/chat/routes.py:412-500]()
- [autogpt_platform/backend/backend/api/features/chat/routes.py:528-544]()
- [autogpt_platform/backend/backend/api/features/chat/routes.py:546-570]()
- [autogpt_platform/backend/backend/copilot/rate_limit.py]()

### Backend Data Flow for Chat

The following diagram illustrates the backend data flow for Copilot chat interactions.

```mermaid
graph TD
    subgraph "Frontend"
        FE[User Input] -->|POST /sessions/{session_id}/stream| API_STREAM
        FE_PENDING[User Input (while streaming)] -->|POST /sessions/{session_id}/pending| API_PENDING
        FE_GET_SESSION[Load Chat History] -->|GET /sessions/{session_id}| API_GET_SESSION
        FE_LIST_SESSIONS[List Chats] -->|GET /sessions| API_LIST_SESSIONS
        FE_UPDATE_TITLE[Rename Chat] -->|PATCH /sessions/{session_id}/title| API_UPDATE_TITLE
        FE_DELETE_SESSION[Delete Chat] -->|DELETE /sessions/{session_id}| API_DELETE_SESSION
        FE_GET_USAGE[Check Usage] -->|GET /usage| API_GET_USAGE
    end

    subgraph "Backend (FastAPI)"
        API_STREAM(stream_chat_post)
        API_PENDING(queue_pending_message)
        API_GET_SESSION(get_session)
        API_LIST_SESSIONS(list_sessions)
        API_UPDATE_TITLE(update_session_title_route)
        API_DELETE_SESSION(delete_session_route)
        API_GET_USAGE(get_usage_status_route)
    end

    subgraph "Copilot Core"
        CR_VALIDATE[Validate Session & Permissions]
        CR_RATE_LIMIT[Check Rate Limits]
        CR_CONCURRENT_LIMIT[Check Concurrent Turn Limit]
        CR_SCHEDULE[schedule_chat_turn]
        CR_STREAM_REGISTRY[stream_registry.stream_events]
        CR_PENDING_QUEUE[pending_message_helpers.queue_pending_for_http]
        CR_DB_GET_PAGINATED[db.get_chat_messages_paginated]
        CR_DB_GET_METADATA[db.get_chat_session_metadata]
        CR_DB_CREATE_SESSION[model.create_chat_session]
        CR_DB_UPDATE_TITLE[model.update_session_title]
        CR_DB_DELETE_SESSION[model.delete_chat_session]
        CR_DB_GET_USER_SESSIONS[model.get_user_sessions]
        CR_DB_GET_USAGE[rate_limit.get_usage_status]
    end

    subgraph "Database (Prisma)"
        DB_CHAT_SESSION[ChatSession]
        DB_CHAT_MESSAGE[ChatMessage]
        DB_REDIS[Redis (for pending messages, streams, locks)]
    end

    API_STREAM --> CR_VALIDATE
    CR_VALIDATE --> CR_RATE_LIMIT
    CR_RATE_LIMIT --> CR_CONCURRENT_LIMIT
    CR_CONCURRENT_LIMIT --> CR_SCHEDULE
    CR_SCHEDULE --> DB_CHAT_MESSAGE
    CR_SCHEDULE --> DB_REDIS
    CR_SCHEDULE --> CopilotProcessor[CopilotProcessor (execution)]

    API_STREAM --> CR_STREAM_REGISTRY
    CR_STREAM_REGISTRY -->|SSE Events| FE

    API_PENDING --> CR_PENDING_QUEUE
    CR_PENDING_QUEUE --> DB_REDIS

    API_GET_SESSION --> CR_DB_GET_PAGINATED
    CR_DB_GET_PAGINATED --> DB_CHAT_SESSION
    CR_DB_GET_PAGINATED --> DB_CHAT_MESSAGE
    CR_DB_GET_PAGINATED -->|Hydrated Messages| FE_GET_SESSION

    API_LIST_SESSIONS --> CR_DB_GET_USER_SESSIONS
    CR_DB_GET_USER_SESSIONS --> DB_CHAT_SESSION
    CR_DB_GET_USER_SESSIONS -->|Session List| FE_LIST_SESSIONS

    API_UPDATE_TITLE --> CR_DB_UPDATE_TITLE
    CR_DB_UPDATE_TITLE --> DB_CHAT_SESSION

    API_DELETE_SESSION --> CR_DB_DELETE_SESSION
    CR_DB_DELETE_SESSION --> DB_CHAT_SESSION
    CR_DB_DELETE_SESSION --> DB_CHAT_MESSAGE

    API_GET_USAGE --> CR_DB_GET_USAGE
    CR_DB_GET_USAGE --> DB_REDIS
    CR_DB_GET_USAGE -->|Usage Status| FE_GET_USAGE

    CR_DB_CREATE_SESSION --> DB_CHAT_SESSION
    CR_DB_CREATE_SESSION -->|New Session ID| API_STREAM
```

Sources:
- [autogpt_platform/backend/backend/api/features/chat/routes.py]()
- [autogpt_platform/backend/backend/copilot/db.py]()
- [autogpt_platform/backend/backend/copilot/model.py]()
- [autogpt_platform/backend/backend/copilot/rate_limit.py]()
- [autogpt_platform/backend/backend/copilot/pending_message_helpers.py]()
- [autogpt_platform/backend/backend/copilot/stream_registry.py]()
- [autogpt_platform/backend/backend/copilot/executor/utils.py]()

## Frontend Components

The Copilot chat interface is built using React and leverages several key components and hooks to manage state, display messages, and interact with the backend API.

### `CopilotPage`

This is the main entry point for the Copilot chat interface. It orchestrates the various sub-components and hooks to provide a complete chat experience.

- **Location**: `autogpt_platform/frontend/src/app/(platform)/copilot/CopilotPage.tsx`
- **Purpose**: Renders the overall layout, including the chat container, sidebar, and handles global state management for the Copilot.
- **Key Responsibilities**:
    - Integrates `ChatContainer` for message display and input.
    - Manages the visibility of the `ChatSidebar` and `ArtifactPanel`.
    - Provides context for various Copilot-related actions and state.
    - Uses `useCopilotPage` hook to access chat session logic.

Sources:
- [autogpt_platform/frontend/src/app/(platform)/copilot/CopilotPage.tsx]()

### `useCopilotPage` Hook

This custom React hook encapsulates the core logic for managing a Copilot chat session on the frontend. It ties together API interactions, state management, and message processing.

- **Location**: `autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotPage.ts`
- **Purpose**: Provides a centralized interface for Copilot chat functionality to `CopilotPage` and other related components.
- **Key Responsibilities**:
    - **Session Management**:
        - Uses `useChatSession` [autogpt_platform/frontend/src/app/(platform)/copilot/useChatSession.ts]() to manage the current `sessionId`, fetch session data, and handle session creation (`createSession`).
        - Handles `dryRun` mode toggling by creating new sessions when the mode changes.
    - **Message Streaming**:
        - Integrates `useCopilotStream` [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotStream.ts]() to establish and manage the SSE connection for real-time message updates.
        - Provides `messages`, `status`, `error`, `isReconnecting`, `isRestoringActiveSession` from the stream.
        - Exposes `sendMessage` and `stop` functions for interacting with the stream.
    - **Message Hydration and Pagination**:
        - Uses `useLoadMoreMessages` [autogpt_platform/frontend/src/app/(platform)/copilot/useLoadMoreMessages.ts]() to handle fetching older messages when the user scrolls up.
        - Combines paginated messages with current stream messages using `concatWithAssistantMerge` [autogpt_platform/frontend/src/app/(platform)/copilot/helpers/convertChatSessionToUiMessages.ts]() to ensure correct display across page boundaries.
        - Applies `stripReplayPrefix` [autogpt_platform/frontend/src/app/(platform)/copilot/helpers/stripReplayPrefix.ts]() to clean up messages from Claude Agent SDK's `--resume` behavior.
    - **Pending Messages**:
        - Uses `useCopilotPendingChips` [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotPendingChips.ts]() to manage and display messages queued while a turn is in progress.
        - `onSend` function handles routing messages to either the main stream endpoint or the pending queue based on `isInflightRef.current`.
    - **Rate Limiting**:
        - Provides `rateLimitMessage` and `dismissRateLimit` for displaying and managing rate limit notifications.
    - **Notifications**:
        - Integrates `useCopilotNotifications` [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotNotifications.ts]() for handling browser notifications.
    - **UI State**:
        - Manages `isUserStopping` state to provide immediate UI feedback when the user clicks "Stop".
        - Provides `turnStats` for displaying elapsed time and other metrics.

Sources:
- [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotPage.ts:38-176]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useChatSession.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotStream.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useLoadMoreMessages.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/helpers/convertChatSessionToUiMessages.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/helpers/stripReplayPrefix.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotPendingChips.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotNotifications.ts]()

### `ChatMessagesContainer`

This component is responsible for rendering the list of chat messages, handling scroll behavior, and integrating pagination.

- **Location**: `autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/ChatMessagesContainer.tsx`
- **Purpose**: Displays individual chat messages, handles loading of older messages, and provides UI elements like "thinking" indicators and scroll-to-bottom functionality.
- **Key Responsibilities**:
    - **Message Rendering**: Iterates through the `messages` prop and renders each `UIMessage`.
    - **Pagination**:
        - Uses `LoadMoreSentinel` [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/ChatMessagesContainer.tsx:154-180]() to detect when the user scrolls near the top and triggers `onLoadMore`.
        - Preserves scroll position when new older messages are loaded.
        - Provides a manual "Load older messages" button as a fallback.
    - **Real-time Indicators**: Displays `ThinkingIndicator` [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/components/ThinkingIndicator.tsx]() when the Copilot is processing.
    - **Turn Statistics**: Integrates `TurnStatsBar` [autogpt_platform/frontend/src/app/(platform)/copilot/components/JobStatsBar/TurnStatsBar.tsx]() to show elapsed time for active turns.
    - **Message Structure**: Uses `buildRenderSegments` [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/helpers.ts]() to break down complex messages (e.g., those with tool outputs) into renderable segments.
    - **Review Prompts**: Displays `CopilotPendingReviews` [autogpt_platform/frontend/src/app/(platform)/copilot/components/CopilotPendingReviews/CopilotPendingReviews.tsx]() if there are pending human reviews.
    - **Scroll Management**: Leverages `useStickToBottomContext` for scroll-to-bottom behavior.

Sources:
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/ChatMessagesContainer.tsx:41-68]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/ChatMessagesContainer.tsx:154-180]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/helpers.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/CopilotPendingReviews/CopilotPendingReviews.tsx]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/JobStatsBar/TurnStatsBar.tsx]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/components/ThinkingIndicator.tsx]()

### Frontend Data Flow for Chat

The following diagram illustrates the frontend data flow for Copilot chat interactions.

```mermaid
graph TD
    subgraph "User Interface"
        UI_INPUT[Chat Input] -->|User Message| USE_COPILOT_PAGE
        UI_SCROLL[Scroll to Top] -->|Request Older Messages| USE_COPILOT_PAGE
        UI_STOP[Stop Button] -->|Stop Stream| USE_COPILOT_PAGE
        UI_SESSION_LIST[Chat Sidebar] -->|Select Session / New Chat| USE_COPILOT_PAGE
    end

    subgraph "React Hooks & Components"
        COPILOT_PAGE[CopilotPage]
        USE_COPILOT_PAGE(useCopilotPage)
        USE_CHAT_SESSION(useChatSession)
        USE_COPILOT_STREAM(useCopilotStream)
        USE_LOAD_MORE_MESSAGES(useLoadMoreMessages)
        CHAT_MESSAGES_CONTAINER[ChatMessagesContainer]
        LOAD_MORE_SENTINEL[LoadMoreSentinel]
    end

    subgraph "API Client"
        API_CLIENT[BackendAPI Client]
    end

    subgraph "Backend (FastAPI)"
        BE_STREAM[POST /sessions/{session_id}/stream]
        BE_PENDING[POST /sessions/{session_id}/pending]
        BE_GET_SESSION[GET /sessions/{session_id}]
        BE_LIST_SESSIONS[GET /sessions]
    end

    UI_INPUT --> USE_COPILOT_PAGE
    USE_COPILOT_PAGE -->|sendMessage(message, files)| USE_COPILOT_STREAM
    USE_COPILOT_PAGE -->|queueFollowUpMessage(message)| API_CLIENT
    API_CLIENT --> BE_PENDING

    USE_COPILOT_STREAM -->|SSE Connection| BE_STREAM
    BE_STREAM -->|Stream Events (UIMessage, Status)| USE_COPILOT_STREAM
    USE_COPILOT_STREAM -->|messages, status, error| USE_COPILOT_PAGE

    USE_COPILOT_PAGE -->|messages, status, error, etc.| COPILOT_PAGE
    COPILOT_PAGE --> CHAT_MESSAGES_CONTAINER

    USE_COPILOT_PAGE -->|sessionId, dryRun| USE_CHAT_SESSION
    USE_CHAT_SESSION -->|sessionId, initial messages| API_CLIENT
    API_CLIENT --> BE_GET_SESSION
    BE_GET_SESSION -->|Session Data (messages, has_more)| USE_CHAT_SESSION
    USE_CHAT_SESSION -->|hydratedMessages, hasMoreMessages, oldestSequence| USE_COPILOT_PAGE

    UI_SCROLL --> LOAD_MORE_SENTINEL
    LOAD_MORE_SENTINEL -->|onLoadMore| USE_COPILOT_PAGE
    USE_COPILOT_PAGE -->|sessionId, oldestSequence| USE_LOAD_MORE_MESSAGES
    USE_LOAD_MORE_MESSAGES -->|fetch older messages| API_CLIENT
    API_CLIENT --> BE_GET_SESSION
    BE_GET_SESSION -->|Older Messages| USE_LOAD_MORE_MESSAGES
    USE_LOAD_MORE_MESSAGES -->|pagedMessages| USE_COPILOT_PAGE

    USE_COPILOT_PAGE -->|combined messages| CHAT_MESSAGES_CONTAINER
    CHAT_MESSAGES_CONTAINER -->|Render UIMessages| UI_DISPLAY[Displayed Chat Messages]

    UI_STOP --> USE_COPILOT_PAGE
    USE_COPILOT_PAGE -->|stop()| USE_COPILOT_STREAM
    USE_COPILOT_STREAM -->|Close SSE| BE_STREAM

    UI_SESSION_LIST --> USE_COPILOT_PAGE
    USE_COPILOT_PAGE -->|createSession()| USE_CHAT_SESSION
    USE_CHAT_SESSION -->|POST /sessions| API_CLIENT
    API_CLIENT --> BE_GET_SESSION
    BE_GET_SESSION -->|New Session ID| USE_CHAT_SESSION
```

Sources:
- [autogpt_platform/frontend/src/app/(platform)/copilot/CopilotPage.tsx]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotPage.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useChatSession.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useCopilotStream.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/useLoadMoreMessages.ts]()
- [autogpt_platform/frontend/src/app/(platform)/copilot/components/ChatMessagesContainer/ChatMessagesContainer.tsx]()

---

