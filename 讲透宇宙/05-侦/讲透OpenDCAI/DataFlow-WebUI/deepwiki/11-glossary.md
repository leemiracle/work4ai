<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/DataFlow-WebUI · page 11 Glossary · fetched 2026-11-02 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_zh.md](README_zh.md)
- [backend/app/api/v1/endpoints/pipelines.py](backend/app/api/v1/endpoints/pipelines.py)
- [backend/app/core/config.py](backend/app/core/config.py)
- [backend/app/schemas/pipelines.py](backend/app/schemas/pipelines.py)
- [backend/app/services/dataflow_engine.py](backend/app/services/dataflow_engine.py)
- [backend/app/services/param_coercion.py](backend/app/services/param_coercion.py)
- [backend/app/services/pipeline_registry.py](backend/app/services/pipeline_registry.py)
- [backend/app/services/ray_pipeline_executor.py](backend/app/services/ray_pipeline_executor.py)
- [docs/architecture/adr-001-source-of-truth.md](docs/architecture/adr-001-source-of-truth.md)
- [docs/migration/from-dataflow-skills.md](docs/migration/from-dataflow-skills.md)
- [docs/profiles/skills.md](docs/profiles/skills.md)
- [installers/checks/check_skills.py](installers/checks/check_skills.py)
- [installers/generate_agent_assets.py](installers/generate_agent_assets.py)
- [skills/canonical/dataflow-dev/SKILL.md](skills/canonical/dataflow-dev/SKILL.md)
- [skills/canonical/generating-dataflow-pipeline/SKILL.md](skills/canonical/generating-dataflow-pipeline/SKILL.md)

</details>



## Purpose and Scope

This page defines the core architectural, runtime, and agentic terminology used across the DataFlow-WebUI and DataFlow-Harness codebase. Each entry details the concept's role, implementation context, and direct code pointers to facilitate navigation for developers and AI coding agents.

Sources: `[README.md:1-18]()`, `[README_zh.md:1-15]()`

---

## 1. Core Execution and Runtime Concepts

### Pipeline & `api_pipelines`
A declarative data processing workflow consisting of an input dataset and a sequential or directed acyclic graph (DAG) of operators. In code, pipelines are defined via Pydantic schemas and persisted or parsed from templates in `api_pipelines`.
* **Code Pointers:** `[backend/app/schemas/pipelines.py:55-61]()`, `[backend/app/services/pipeline_registry.py:19-47]()`

### Operator & `operators_detail`
An atomic processing step within a pipeline (e.g., text cleaning, LLM generation, embedding extraction). Operators encapsulate initialization parameters (`init_params`) and runtime arguments (`run_params`). During execution, `operators_detail` tracks live progress, state, and metrics per operator.
* **Code Pointers:** `[backend/app/schemas/pipelines.py:37-41]()`, `[backend/app/services/ray_pipeline_executor.py:162-184]()`

### Level_1 / Level_2 Taxonomy
Classification hierarchy for operators. **Level 1** operators are standard data transformation/filtering utilities operating directly on fields, while **Level 2** operators typically incorporate advanced AI reasoning, multi-turn LLM agent execution, or complex external tool integration.
* **Code Pointers:** `[backend/app/services/pipeline_registry.py:19-91]()`

### Task ID (`task_id`)
A unique string identifier assigned to every asynchronous or synchronous pipeline execution session, used to track execution state, collect logs, and persist results.
* **Code Pointers:** `[backend/app/schemas/pipelines.py:110-111]()`, `[backend/app/core/config.py:22]()`

### Executor Type & Ray Execution
The runtime mechanism used to execute dataflow pipelines. While synchronous execution runs locally, `RayPipelineExecutor` leverages Apache Ray for distributed remote task submission, concurrency control, and worker environment management.
* **Code Pointers:** `[backend/app/services/ray_pipeline_executor.py:1-25]()`, `[backend/app/services/dataflow_engine.py:16-17]()`

```mermaid
graph TD
    sub-natural-language ["Natural Language Pipeline Request"]
    sub-code-space ["Code Entity Execution Space"]

    sub-natural-language -->|Trigger Execution| API["/api/v1/execute"]
    API -->|Submit Task| Engine["DataFlowEngine"]
    Engine -->|Dispatch Remote| RayExec["RayPipelineExecutor"]
    RayExec -->|Capture Stdout| LogStream["LogStream"]
    RayExec -->|Persist Steps| Storage["FileStorage"]

    style sub-natural-language fill:none,stroke:none
    style sub-code-space fill:none,stroke:none
```
*Sources: `[backend/app/services/dataflow_engine.py:1-25]()`, `[backend/app/services/ray_pipeline_executor.py:1-48]()`*

---

## 2. Storage, Registries, and Caching

### Registry Files (`registry files`)
YAML and JSON files stored in the data directory that maintain state for pipelines, tasks, datasets, servings, text2sql databases, and operator caches.
* **Code Pointers:** `[backend/app/core/config.py:21-31]()`

### Cache Local (`cache_local`)
The local file system directory where intermediate pipeline execution steps (`dataflow_cache_step_*.jsonl`) are persisted between operators for state caching, debugging, and resumable execution.
* **Code Pointers:** `[backend/app/core/config.py:31]()`, `[backend/app/services/ray_pipeline_executor.py:4()`]

### Serving Instance
A configured LLM or embedding provider endpoint wrapper (such as `APILLMServing_request`) managed by `ServingRegistry`. It handles API keys, base URLs, model selection, and parameter introspection.
* **Code Pointers:** `[backend/app/services/dataflow_engine.py:1-2]()`, `[backend/app/services/dataflow_engine.py:181-194]()`, `[backend/app/core/config.py:24()`]

### Prompt Template
Reusable prompt structures registered in `PROMPT_REGISTRY` that operators reference during LLM generation and text synthesis tasks.
* **Code Pointers:** `[backend/app/core/config.py:5]()`, `[backend/app/services/dataflow_engine.py:5()`]

### Schema Reference (`schema_ref`)
A string prefix convention (`schema_ref:<schema_id>`) used in operator parameter configurations to reference saved JSON schemas managed by `json_schema_manager`. These references are dereferenced prior to type coercion.
* **Code Pointers:** `[backend/app/services/param_coercion.py:13-48]()`

### FileStorage
The upstream core abstraction (`FileStorage`) responsible for reading, writing, and stepping data payloads between pipeline operators.
* **Code Pointers:** `[backend/app/services/dataflow_engine.py:3()`]

### LogStream
A custom `io.StringIO` subclass that intercepts standard output and error streams in real-time during operator execution. It parses progress bars (such as `tqdm` metrics) and updates execution status.
* **Code Pointers:** `[backend/app/services/ray_pipeline_executor.py:45-98()`]

---

## 3. Agentic Layer, Skills, and MCP

### MCP (Model Context Protocol)
The server implementation mounted on FastAPI that exposes system tools—such as the operator catalog, pipeline validation, and pipeline commit tools—to AI coding agents.
* **Code Pointers:** `[README.md:8-16]()`, `[README_zh.md:5-12]()`

### Profiles (`webui`, `harness`, `skills`)
Deployment configurations defined in `install.sh` that determine whether the system provisions the visual Vue.js canvas (`webui`), the backend and MCP server without a browser (`harness`), or pure static agent instructions (`skills`).
* **Code Pointers:** `[README.md:26-36]()`, `[README_zh.md:20-32]()`, `[docs/profiles/skills.md:1-10()`]

### Canonical Skills (`skills/canonical`) & Skill Layers
The single hand-edited source of truth for all agent instructions and skills. Asset generation scripts compile canonical Markdown files into agent-specific formats (`.claude/skills/`, `.cursor/skills/`, `AGENTS.md`) to prevent documentation drift.
* **Code Pointers:** `[docs/architecture/adr-001-source-of-truth.md:50-64]()`, `[docs/profiles/skills.md:38-60()`]

### Agent Adapters
Backend adapter modules (supporting Claude, Codex, Cursor) that abstract agent communication, context injection, and configuration file generation (`.mcp.json`, `config.toml`, `.cursor/mcp.json`).
* **Code Pointers:** `[README.md:120-136]()`, `[README_zh.md:120-135()`]

```mermaid
graph TD
    sub-natural-language ["Natural Language Agent Session"]
    sub-code-space ["Code Entity Agent & Skill Space"]

    sub-natural-language -->|Invoke Skill| Canonical["skills/canonical/"]
    Canonical -->|Compile Asset| GenScript["installers/generate_agent_assets.py"]
    GenScript -->|Write Config| MCPJson[".mcp.json"]
    MCPJson -->|Expose Tools| MCPServer["FastAPI MCP Server"]
    MCPServer -->|Validate Config| PipelineReg["PipelineRegistry"]

    style sub-natural-language fill:none,stroke:none
    style sub-code-space fill:none,stroke:none
```
*Sources: `[docs/architecture/adr-001-source-of-truth.md:50-85]()`, `[installers/generate_agent_assets.py:1-50()`]*

---

## 4. Errors and Diagnostics

### DataFlowEngineError
The primary custom exception class raised by the execution engine and Ray workers. It captures diagnostic context, original errors, and formatted tracebacks for serialization in API responses.
* **Code Pointers:** `[backend/app/services/dataflow_engine.py:28-44()`]

### ValidationBizError
A business-level validation exception raised when static pipeline checks or configuration payload validations fail. It maps schema violations to structured diagnostic issues with repair hints.
* **Code Pointers:** `[backend/app/schemas/pipelines.py:121-142]()`, `[backend/app/api/v1/endpoints/pipelines.py:70-80()`]

Sources: `[backend/app/services/dataflow_engine.py:28-44](), [backend/app/schemas/pipelines.py:121-142]()`