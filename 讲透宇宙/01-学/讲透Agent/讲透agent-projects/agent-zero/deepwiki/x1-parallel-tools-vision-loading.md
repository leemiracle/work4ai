<!-- source: DeepWiki mcp.deepwiki.com · repo agent0ai/agent-zero · extra page Parallel Tools & Vision Loading · fetched 2026-10-29 -->

# Parallel Tools & Vision Loading

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [extensions/python/tool_execute_before/_10_unmask_secrets.py](extensions/python/tool_execute_before/_10_unmask_secrets.py)
- [helpers/parallel_tools.py](helpers/parallel_tools.py)
- [helpers/parallel_tools.py.dox.md](helpers/parallel_tools.py.dox.md)
- [prompts/agent.system.tool.parallel.md](prompts/agent.system.tool.parallel.md)
- [prompts/agent.system.tools_vision.md](prompts/agent.system.tools_vision.md)
- [prompts/fw.vision_load.md](prompts/fw.vision_load.md)
- [tests/test_parallel_code_lifetime.py](tests/test_parallel_code_lifetime.py)
- [tests/test_parallel_tool.py](tests/test_parallel_tool.py)
- [tests/test_parallel_tool_args.py](tests/test_parallel_tool_args.py)
- [tests/test_tool_request_normalization.py](tests/test_tool_request_normalization.py)
- [tests/test_vision_load_image_refs.py](tests/test_vision_load_image_refs.py)
- [tools/parallel.py](tools/parallel.py)
- [tools/parallel.py.dox.md](tools/parallel.py.dox.md)
- [tools/vision_load.py](tools/vision_load.py)
- [tools/vision_load.py.dox.md](tools/vision_load.py.dox.md)

</details>



This page covers the core implementation of asynchronous concurrent tool execution (`helpers/parallel_tools.py` and `tools/parallel.py`) and multimodal vision ingestion (`tools/vision_load.py`). It details job state lifecycles, worker isolation models, tool validation rules, and vision model routing.

Sources: [helpers/parallel_tools.py:1-40](), [tools/vision_load.py:1-35]()

---

## 1. Normalization & Safety Guardrails

The parallel tool subsystem accepts batch requests from the agent, normalizing various payload shapes into canonical structures and enforcing recursion guards and tool restrictions.

Normalization begins when `parallel_tools.normalize_parallel_tool_calls()` parses raw input dictionaries, JSON strings, or full agent-reply envelopes [helpers/parallel_tools.py:83-114](). Each wrapped call is validated against `_ensure_parallel_tool_allowed()` [helpers/parallel_tools.py:117-132](), which rejects nested `parallel` calls, state-mutating session terminal commands (`code_execution_tool` with `output` or `reset`), and heavy/parent-bound tools such as `document_query`, `response`, `goal`, `input`, and `input_remote` [helpers/parallel_tools.py:35]().

```mermaid
flowchart TD
    NL[""Natural Language / Model JSON Payload""] -->|extract_tool_calls| Raw[""Raw Call Array / JSON String""]
    Raw -->|normalize_parallel_tool_calls| Norm[""helpers/parallel_tools.py:83""]
    Norm -->|normalize_tool_request| Ext[""helpers/extract_tools.py""]
    Ext -->|check rules| Guard[""helpers/parallel_tools.py:_ensure_parallel_tool_allowed""]
    Guard -->|Valid| Out[""list[NormalizedToolCall]""]
    Guard -->|Disallowed Tool| Err[""ValueError Exception""]
```
Sources: [helpers/parallel_tools.py:32-132](), [helpers/extract_tools.py:12-17](), [prompts/agent.system.tool.parallel.md:1-21]()

### Key Normalization Symbols
- `NormalizedToolCall`: Dataclass holding `index`, `tool_name`, and `tool_args` [helpers/parallel_tools.py:43-46]().
- `extract_tool_calls()`: Locates wrapped items across `tool_calls`, `calls`, or `items` keys [helpers/parallel_tools.py:76-80]().
- `DEFAULT_MAX_CALLS`: Limits a single parallel batch to at most `8` calls [helpers/parallel_tools.py:32]().
- `DISALLOWED_PARALLEL_TOOLS`: Set containing `document_query`, `response`, `goal`, `input`, and `input_remote` [helpers/parallel_tools.py:35]().

Sources: [helpers/parallel_tools.py:32-80](), [helpers/parallel_tools.py:43-46]()

---

## 2. ParallelJob Lifecycle & Worker Subsystems

Active parallel work is managed via `ParallelJob` instances tracked within the agent context. Jobs operate under two distinct execution topologies: **direct tool workers** and **subordinate agent workers**.

```mermaid
flowchart TD
    Start[""start_parallel_jobs()""] --> Pending[""JobState: pending""]
    Pending --> Running[""JobState: running (DeferredTask)""]
    Running --> Success[""JobState: success""]
    Running --> Error[""JobState: error""]
    Running --> Cancelled[""JobState: cancelled""]
    Running --> Timeout[""JobState: timeout""]
    
    Sub[""JobKind: subordinate""] -.->|Delegation| SubAgent[""Child Agent Context""]
    Tool[""JobKind: tool""] -.->|Background Task| DirectWorker[""Isolated Background Context""]
```
Sources: [helpers/parallel_tools.py:37-69](), [helpers/parallel_tools.py.dox.md:29-34]()

### Job States & Worker Kinds
- `JobState`: Literal type restricted to `"pending"`, `"running"`, `"success"`, `"error"`, `"cancelled"`, or `"timeout"` [helpers/parallel_tools.py:38]().
- `JobKind`: Distinguishes between `"tool"` (direct tool execution) and `"subordinate"` (`call_subordinate` agent delegation) [helpers/parallel_tools.py:39]().
- `ParallelJob`: Dataclass recording execution metadata, timings, parent contexts, and underlying `DeferredTask` handles [helpers/parallel_tools.py:50-69]().
- Worker detection helpers (`is_parallel_worker()`, `get_parallel_worker_job()`) identify whether an executing tool resides inside a background parallel context [helpers/parallel_tools.py:182-194]().

Sources: [helpers/parallel_tools.py:37-69](), [helpers/parallel_tools.py:182-194]()

---

## 3. ParallelTool Actions (`start`, `await`, `collect`, `cancel`) & Execution Flow

The `ParallelTool` class located in `tools/parallel.py` exposes the user-facing interface for controlling asynchronous jobs [tools/parallel.py.dox.md:5-18](). It accepts an `action` argument (`start`, `await`, `collect`, or `cancel`) alongside `tool_calls`, `job_ids`, `wait`, and `timeout`.

```mermaid
flowchart TD
    NLAction[""Agent Prompt: parallel action=start|await|collect|cancel""] --> ToolExec[""tools/parallel.py:ParallelTool.execute()""]
    ToolExec --> Coerce[""Coerce timeout & job_ids""]
    Coerce --> ActCheck{Action Type?}
    
    ActCheck -->|cancel| Cancel[""helpers/parallel_tools.py:cancel_parallel_jobs()""]
    ActCheck -->|start / default| Start[""helpers/parallel_tools.py:start_parallel_jobs()""]
    Start --> AwaitCheck{Wait Flag?}
    AwaitCheck -->|True| Await[""helpers/parallel_tools.py:await_parallel_jobs()""]
    AwaitCheck -->|False| ReturnJobIDs[""Return started job handles""]
    
    ActCheck -->|await / collect| AwaitColl[""helpers/parallel_tools.py:await_parallel_jobs()""]
    AwaitColl --> Collect[""ParallelTool.after_execution: collect_parallel_jobs()""]
```
Sources: [tools/parallel.py.dox.md:13-35](), [helpers/parallel_tools.py.dox.md:50-54]()

### Execution Flow & History Promotion
- `before_execution()`: Prepares runtime state prior to action handling [tools/parallel.py.dox.md:16]().
- `after_execution()`: Sanitizes response messages, records tool results in agent history, and invokes `collect_parallel_jobs()` with `promote_parent_history=True` to flush queued worker history in proper order [tools/parallel.py.dox.md:17](), [helpers/parallel_tools.py.dox.md:53]().
- Timeout handling: `coerce_timeout()` validates integer second durations, defaulting to `300` seconds (`DEFAULT_TIMEOUT_SECONDS`) [helpers/parallel_tools.py:33](), [helpers/parallel_tools.py:158-168]().

Sources: [tools/parallel.py.dox.md:13-18](), [helpers/parallel_tools.py:33](), [helpers/parallel_tools.py:158-168]()

---

## 4. Vision Loading & Multimodal Ingestion (`vision_load`)

The `VisionLoad` tool (`tools/vision_load.py`) processes images for visual reasoning, supporting ephemeral image references, base64 data URLs, and local file paths [tools/vision_load.py:25-105]().

### Image Resolution & Routing Logic
1. **Path Normalization & Limits**: Resolves input paths into a limited set based on `max_embeds` configuration (defaulting to `10`) [tools/vision_load.py:45-55](), [tools/vision_load.py:107-109]().
2. **Ephemerals & Data URLs**: Consumes ephemeral image references (`ephemeral_images.consume_image`) and parses data URLs (`_store_data_url`) [tools/vision_load.py:60-78]().
3. **Local Files**: Validates file existence via `runtime.call_development_function()` and maps mime types via `mimetypes.guess_type()` [tools/vision_load.py:1](), [tools/vision_load.py:79-90]().
4. **Vision Model Call**: If a vision model configuration is active (`get_vision_model_config`), all loaded image paths are batched into a single unified call via `build_vision_model()` using the prompt template `fw.vision_load.md` [tools/vision_load.py:93-102](), [tools/vision_load.py:121-144](). Otherwise, images are attached directly to native model-visible history blocks.

Sources: [tools/vision_load.py:1-144](), [tools/vision_load.py.dox.md:13-38]()

---

