# Agent APIs Deep Dive

The [API Overview](api-overview.md) covers the basic Agent flow (`ace_agentAddUserInput`, `ace_agentAddToolResult`, `ace_agentRun`). This page covers the rest of the Agent APIs: changing instructions at runtime, direct message manipulation, transient and redacted message flags, the preamble, conversation introspection, serialization, cancellation, and skipping inference.

## Runtime instruction changes

System instructions are normally set at agent creation via `ACEAgentParam_Instructions` on the `ACEAgentParams` passed to `ace_agentCreate`. To change them while the agent is running, call `ace_agentSetInstructions` with the new text (or `NULL` to clear). The change takes effect on the next `ace_agentRun` and applies to all subsequent inferences. Use it for scenarios where the agent's behavior needs to shift during a session, such as switching from advisor mode to narrator mode, or installing a different system prompt mid-game.

## Direct message manipulation

When the role-specific helpers do not fit (for example, when injecting a system message mid-conversation), `ace_agentAddChatMessage` appends an empty `ACEChatMessage` to the conversation and returns it. The caller fills in fields like role, content, and tool calls via the `ace_chatMessage*` setters. See {cpp:type}`ACEChatMessage` in the API reference for the full set of fields.

## Transient messages

A transient message is included in the next prompt the agent prepares for inference, then dropped from subsequent prompts once an assistant message follows it in the conversation. Use it for one-shot steering ("respond in two sentences", "format as JSON") that should influence the next inference but not pollute persistent history. Set the flag via `ace_chatMessageSetTransient` after creating the message with `ace_agentAddChatMessage`. The original content remains in the conversation list (and in serialized snapshots); only the rendering in subsequent prompts changes.

## Redacted messages

A redacted message keeps its original content but renders as `[REDACTED]` in subsequent prompts once the autonomous tool-call chain that produced it has ended. Unlike transient, redaction does not trigger as soon as an assistant message follows: within a single chain the model often combines information across multiple intermediate assistant messages and tool results before producing a final response, so an earlier assistant reply does not mean earlier tool outputs are done being useful.

The chain ends on the same boundary that resets the `MaxSteps` counter: tool result delivery does not end the chain, but any other non-transient client input (a new user message, or a non-transient, non-Tool client-added message) does. Transient messages are excluded from this boundary because they are one-shot nudges consumed on the next inference, not new steering that begins a fresh chain. At that point, every message from the previous chain becomes eligible for redaction in the next prompt the agent prepares.

Use redaction for large tool results that the model needs to process once but should not consume context budget on future inferences. Set the flag via `ace_chatMessageSetRedacted`, or pass `redacted=1` to `ace_agentAddToolResult` for the common tool-result case. As with transient, the original is preserved in the conversation list.

If both flags are set on the same message, transient takes precedence: the message is skipped entirely as soon as an assistant message follows, before the redacted consumption rule would apply.

Both flags are interpreted by `ACEAgent` during prompt preparation. Setting them on messages owned by an `ACEChat` (which the Chat APIs send to the model as-is) has no effect.

## Preamble

The preamble is a persistent prefix between the system instructions and the windowed conversation. Messages added via `ace_agentAddPreambleMessage` survive `HistoryWindow` aging and are emitted on every inference until cleared with `ace_agentClearPreamble`. Use it for context-bridging content that needs to outlive the rolling window: a pending-operations summary that updates as long-running tools complete, or a client-driven summary of conversation history that has aged out (see [Conversation introspection](#conversation-introspection) below).

Transient and redacted flags on preamble messages are ignored: those flags are conversation-message lifecycle concerns, not preamble concerns.

## Conversation introspection

The agent normally hides the message list, but three accessors let the application read it:

* `ace_agentGetConversationCount` returns the total message count.
* `ace_agentGetConversation` returns a read-only pointer to the message at a given index. The pointer is invalidated by the next agent mutation (`ace_agentAddUserInput`, `ace_agentAddChatMessage`, `ace_agentAddToolResult`, `ace_agentRun`, `ace_agentClearConversation`, `ace_agentLoadConversation`).
* `ace_agentGetWindowStart` returns the index of the first message that would be included in the next inference's prompt under the current `HistoryWindow`. Messages at indices `[0, windowStart)` are about to be excluded.

A good use case for these accessors is client-driven summarization: the application monitors `ace_agentGetWindowStart` as the conversation grows, detects when content is about to age out, summarizes the about-to-drop messages (using a separate call to the Chat APIs, a smaller summarization model, or a heuristic), and stores the summary in the preamble. The agent itself does not auto-summarize.

## Serialization

`ace_agentSerializeConversation` returns an opaque byte buffer representing the agent's current conversation. `ace_agentLoadConversation` restores from such a buffer; it is only valid when the agent is in `ACEAgentStatus_Idle`.

Use it to persist the agent's conversation across game sessions. The buffer format is opaque and version-tagged; the load call returns `ACEResultUnsupportedVersion` if the buffer was produced by an incompatible SDK version. A trailing assistant message with unanswered tool calls is stripped on load to avoid feeding an orphaned tool call into the next inference.

The buffer returned from `ace_agentSerializeConversation` is owned by the agent and valid only until the next agent call, so copy it before continuing if the application needs to keep it around.

## Cancellation

`ace_agentCancel` interrupts the agent's current operation. It is thread-safe and designed to be called from another thread while another thread is blocked in `ace_agentRun`. The next `ace_agentRun` returns `ACEAgentStatus_Cancelled`. Good use cases include reacting to a game event that needs the agent's attention immediately (e.g., "monster spotted 2 miles away"), or letting a player redirect mid-response (e.g., typing a new question while the previous one is still streaming).

The `rollback` flag controls what happens to the conversation:

* With `rollback` zero (the default), the conversation is preserved as-is. The partial assistant output of the cancelled inference, if any, is dropped before it would have been appended.
* With `rollback` non-zero, everything after the most recent user message is erased before `Cancelled` is returned. This rebuilds the conversation to the moment just before the agent started reasoning, with the originating user message preserved as an anchor.

`ace_agentClearCancel` clears a pending cancel request without producing a `Cancelled` status. It exists for the race where `ace_agentCancel` is called from another thread but the agent had already completed and returned `Idle` on its own; without `ClearCancel`, the next `ace_agentRun` would consume the stale request. Typical usage: after calling `Cancel`, if the in-flight `Run` returned `Idle` rather than `Cancelled`, call `ClearCancel` before continuing.

## Skip inference

`ace_agentSkipInference` registers a one-shot request that causes the next `ace_agentRun` (when it would otherwise trigger inference) to return `ACEAgentStatus_Idle` instead. The request is cleared once consumed; calling `ace_agentCancel` or `ace_agentClearConversation` also clears it.

Good use cases include fire-and-forget tool calls where the application does not need the model to react to the tool's result. After appending the result via `ace_agentAddToolResult`, call `ace_agentSkipInference` to release the run loop without triggering another inference. Long-running tools (NPC navigation, background processing) can also use this pattern to let the run loop go idle while the tool completes, then deliver the result later via `ace_agentAddToolResult` and let the next normal `ace_agentRun` pick it up.

Some models get confused if they see tool calls in conversation history with no corresponding results. If this happens, add a minimal placeholder result via `ace_agentAddToolResult` (e.g., `"in-progress"`) before calling `ace_agentSkipInference` so the next prompt has a complete tool-call / result pair.
