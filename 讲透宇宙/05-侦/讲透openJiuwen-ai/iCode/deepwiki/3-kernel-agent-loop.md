<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/iCode · page 3 Kernel: Agent Loop · fetched 2026-11-02 -->

# Kernel: Agent Loop

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/chrys/foundation/io/result_content.py](src/chrys/foundation/io/result_content.py)
- [src/chrys/foundation/text/model_json.py](src/chrys/foundation/text/model_json.py)
- [src/chrys/kernel/_content.py](src/chrys/kernel/_content.py)
- [src/chrys/kernel/_loop_recorder.py](src/chrys/kernel/_loop_recorder.py)
- [src/chrys/kernel/_result_ceiling.py](src/chrys/kernel/_result_ceiling.py)
- [src/chrys/kernel/_tool_execution.py](src/chrys/kernel/_tool_execution.py)
- [src/chrys/kernel/agent.py](src/chrys/kernel/agent.py)
- [src/chrys/kernel/loop.py](src/chrys/kernel/loop.py)
- [src/chrys/kernel/tools.py](src/chrys/kernel/tools.py)
- [src/chrys/service/approval/judge.py](src/chrys/service/approval/judge.py)
- [src/chrys/service/llm/openai_responses/history.py](src/chrys/service/llm/openai_responses/history.py)
- [tests/architecture/test_copy_freshness.py](tests/architecture/test_copy_freshness.py)
- [tests/foundation/text/test_model_json.py](tests/foundation/text/test_model_json.py)
- [tests/kernel/test_agent.py](tests/kernel/test_agent.py)
- [tests/kernel/test_agent_service_handles.py](tests/kernel/test_agent_service_handles.py)
- [tests/kernel/test_loop.py](tests/kernel/test_loop.py)
- [tests/kernel/test_loop_exhaustion_tail.py](tests/kernel/test_loop_exhaustion_tail.py)
- [tests/kernel/test_result_ceiling.py](tests/kernel/test_result_ceiling.py)
- [tests/kernel/test_tools.py](tests/kernel/test_tools.py)

</details>



## Purpose and Scope

The agent kernel orchestrates the multi-turn interaction cycle between chat middleware, model wire clients, and local function tools. It provides the core blocking and streaming execution drivers that drive agentic loops, manage tool dispatches, handle interruption recovery, shape outputs, and collect telemetry. 

As a middle layer in the architecture, the kernel sits between lower-level foundation primitives (`chrys.foundation.*`) and upper-level orchestration/application layers (`chrys.agent`, `chrys.service`) [src/chrys/kernel/loop.py:19-21](), [src/chrys/kernel/agent.py:13-27]().

Sources: [src/chrys/kernel/loop.py:5-21](), [src/chrys/kernel/agent.py:5-27]()

---

## 3.1. Loop and Agent Execution

The primary execution loop is owned by `ToolLoopLayer` in `src/chrys/kernel/loop.py` [src/chrys/kernel/loop.py:7-13](). It manages per-run middleware pipelines, model calls via `_WireCaller`, iteration counts bounded by `DEFAULT_MAX_ITERATIONS` [src/chrys/kernel/loop.py:102-103](), consecutive error budgets (`DEFAULT_MAX_CONSECUTIVE_ERRORS`) [src/chrys/kernel/loop.py:103-104](), and exhaustion tails when iteration ceilings are reached [src/chrys/kernel/loop.py:173-182]().

The loop coordinates with `LoopRecorder` to journal message histories and supports interrupt-recovery checkpoints [src/chrys/kernel/loop.py:12-13]().

For details, see [Loop and Agent Execution](#3.1).

```mermaid
graph TD
    sub:Client[""Agent Client""] --> loopLayer[""ToolLoopLayer (src/chrys/kernel/loop.py)""]
    loopLayer --> wireCaller[""_WireCaller (src/chrys/kernel/loop.py)""]
    wireCaller --> chatLayer[""ChatMiddlewareLayer (src/chrys/kernel/middleware.py)""]
    loopLayer --> recorder[""LoopRecorder (src/chrys/kernel/_loop_recorder.py)""]
    loopLayer --> toolExec[""_execute_function_calls (src/chrys/kernel/_tool_execution.py)""]
```
Sources: [src/chrys/kernel/loop.py:5-14](), [src/chrys/kernel/_loop_recorder.py:1-15]()

Sources: [src/chrys/kernel/loop.py:5-21]()

---

## 3.2. Tool Execution and Result Shaping

Tool definitions, parsing, schema generation, and asynchronous execution are managed in `src/chrys/kernel/tools.py` via `FunctionTool` [src/chrys/kernel/tools.py:5-11](). The module handles content normalization, explicit-null overlays (`_null_overlay.py`), and validation against JSON schemas.

Oversized local tool outputs are controlled by the result ceiling mechanism in `src/chrys/kernel/_result_ceiling.py` (`apply_result_ceiling`), ensuring token limits are enforced without truncating error states or critical structured markers [src/chrys/kernel/_result_ceiling.py:177-181]().

For details, see [Tool Execution and Result Shaping](#3.2).

```mermaid
graph TD
    toolCall[""Function Tool Call""] --> fnTool[""FunctionTool.invoke (src/chrys/kernel/tools.py)""]
    fnTool --> nullOverlay[""restore_explicit_nulls (src/chrys/kernel/_null_overlay.py)""]
    fnTool --> ceiling[""apply_result_ceiling (src/chrys/kernel/_result_ceiling.py)""]
    ceiling --> contentModel[""Content (src/chrys/kernel/_content.py)""]
```
Sources: [src/chrys/kernel/tools.py:5-14](), [src/chrys/kernel/_result_ceiling.py:177-181]()

Sources: [src/chrys/kernel/tools.py:5-18]()

---

## 3.3. Context Compaction

When token limits approach capacity or context overflow conditions arise, the kernel employs compaction strategies and overflow sinks (`ContextOverflowSink`) [src/chrys/kernel/loop.py:82]() to prune conversation history while retaining semantic continuity.

Middleware layers interact with token counters and usage metrics to trigger compaction before requests hit the wire clients.

For details, see [Context Compaction](#3.3).

Sources: [src/chrys/kernel/loop.py:82]()

---

## 3.4. Kernel Telemetry and Instrumentation

Observability across the execution loop is managed via OpenTelemetry integration in `src/chrys/kernel/instrumentation.py`. Spans track request/response durations, turn transitions, and tool-invocation timings.

Trajectory timestamps and metadata keys (`OPERATION_ID_KEY`, `ANALYTICS_ITEM_ID_KEY`) link execution telemetry back to agent analytics engines [src/chrys/foundation/trajectory/metadata.py:63-66]().

For details, see [Kernel Telemetry and Instrumentation](#3.4).

Sources: [src/chrys/foundation/trajectory/metadata.py:63-66]()

---

