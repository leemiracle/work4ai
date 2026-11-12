<!-- source: DeepWiki mcp.deepwiki.com · repo nousresearch/hermes-agent · page 9 Batch Processing and Evaluation · fetched 2026-10-27 -->

# Batch Processing and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gateway/browser_control_artifacts.py](gateway/browser_control_artifacts.py)
- [gateway/browser_control_broker.py](gateway/browser_control_broker.py)
- [hermes_cli/subcommands/_shared.py](hermes_cli/subcommands/_shared.py)
- [hermes_cli/subcommands/peer.py](hermes_cli/subcommands/peer.py)
- [scripts/run_tests.sh](scripts/run_tests.sh)
- [scripts/run_tests_parallel.py](scripts/run_tests_parallel.py)
- [tests/agent/test_phantom_tool_references.py](tests/agent/test_phantom_tool_references.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/gateway/test_browser_control_api.py](tests/gateway/test_browser_control_api.py)
- [tests/gateway/test_browser_control_artifacts.py](tests/gateway/test_browser_control_artifacts.py)
- [tests/gateway/test_browser_control_broker.py](tests/gateway/test_browser_control_broker.py)
- [tests/gateway/test_browser_control_broker_hardening.py](tests/gateway/test_browser_control_broker_hardening.py)
- [tests/gateway/test_browser_control_cloud.py](tests/gateway/test_browser_control_cloud.py)
- [tests/gateway/test_peer_dm_bot_chat_authority.py](tests/gateway/test_peer_dm_bot_chat_authority.py)
- [tests/gateway/test_peer_dm_hidden_e2e.py](tests/gateway/test_peer_dm_hidden_e2e.py)
- [tests/gateway/test_peer_dm_into_open_bot_chat.py](tests/gateway/test_peer_dm_into_open_bot_chat.py)
- [tests/hermes_cli/test_peer_cmd.py](tests/hermes_cli/test_peer_cmd.py)
- [tests/hermes_cli/test_peer_dm_reporting.py](tests/hermes_cli/test_peer_dm_reporting.py)
- [tests/hermes_cli/test_reasoning_effort_menu.py](tests/hermes_cli/test_reasoning_effort_menu.py)
- [tests/scripts/install/test_install_ps1_native_calls.py](tests/scripts/install/test_install_ps1_native_calls.py)
- [tests/scripts/test_run_tests_parallel.py](tests/scripts/test_run_tests_parallel.py)
- [tests/test_basetemp_isolation.py](tests/test_basetemp_isolation.py)
- [tests/tools/test_browser_cdp_tool.py](tests/tools/test_browser_cdp_tool.py)
- [tests/tools/test_browser_extension_router.py](tests/tools/test_browser_extension_router.py)
- [tests/tools/test_browser_extension_router_wiring.py](tests/tools/test_browser_extension_router_wiring.py)
- [tests/tools/test_browser_hardening.py](tests/tools/test_browser_hardening.py)
- [tests/tools/test_browser_headed_mode.py](tests/tools/test_browser_headed_mode.py)
- [tests/tools/test_browser_hybrid_routing.py](tests/tools/test_browser_hybrid_routing.py)
- [tests/tools/test_browser_open_timeout.py](tests/tools/test_browser_open_timeout.py)
- [tests/tools/test_browser_supervisor.py](tests/tools/test_browser_supervisor.py)
- [tests/tools/test_browser_supervisor_capture.py](tests/tools/test_browser_supervisor_capture.py)
- [tests/tools/test_browser_supervisor_capture_dispatch.py](tests/tools/test_browser_supervisor_capture_dispatch.py)
- [tests/tools/test_browser_supervisor_reconnect.py](tests/tools/test_browser_supervisor_reconnect.py)
- [tests/tools/test_model_tools.py](tests/tools/test_model_tools.py)
- [tools/browser_cdp_tool.py](tools/browser_cdp_tool.py)
- [tools/browser_dialog_tool.py](tools/browser_dialog_tool.py)
- [tools/browser_extension_router.py](tools/browser_extension_router.py)
- [tools/browser_supervisor.py](tools/browser_supervisor.py)
- [tools/browser_supervisor_capture.py](tools/browser_supervisor_capture.py)
- [tools/browser_supervisor_dialogs.py](tools/browser_supervisor_dialogs.py)
- [tools/browser_supervisor_frames.py](tools/browser_supervisor_frames.py)
- [tui_gateway/methods_browser_control.py](tui_gateway/methods_browser_control.py)
- [website/docs/developer-guide/browser-supervisor.md](website/docs/developer-guide/browser-supervisor.md)

</details>





## Purpose and Scope

This page provides a high-level overview of the batch processing system and evaluation harnesses within Hermes Agent. The batch system orchestrates running the agent over many prompt inputs in parallel, sampling tool configurations, managing checkpoints, trajectory compression, data collection, and producing structured output data suitable for training and analysis. In addition, evaluation harnesses under `evals/` validate agent capabilities such as compaction recall, browser automation, codebase navigation, core tool deferral, and resource benchmarking.

As a parent page, this document outlines the high-level architecture. For detailed implementations, consult the child pages:

- [Batch Runner](#9.1) — Document BatchRunner architecture (`batch_runner.py`), parallelization, checkpointing, durability, and fault tolerance
- [Toolset Distributions](#9.2) — Explain toolset distribution sampling, probability-based selection, and tool configuration for batch runs
- [Data Generation and Trajectories](#9.3) — Cover trajectory format, tool statistics extraction, reasoning metrics, data normalization, datagen config examples, trajectory compression, and `mini_swe_runner`
- [Evaluation Harnesses](#9.4) — Document the `evals/` directory harnesses: compaction recall, browser-use, codebase navigability, core tool deferral, readtool, session search schema, and fanout resource benchmark

---

## Overview

The batch processing system enables large-scale generation of conversation trajectories by running the `AIAgent` over numerous prompt inputs in parallel worker pools. It samples toolset configurations according to defined probabilistic distributions, runs agent conversations that log tool call activities and reasoning progress, aggregates usage statistics, and outputs structured datasets for evaluation or training.

Key points include:

- The core batch processing is driven by `batch_runner.py`, which handles dataset reading, batch splitting, multiprocessing, checkpointing, and output file management [agent/batch_runner.py:3-65]().
- Toolsets are sampled per prompt based on configured distributions found in `toolset_distributions.py` to diversify tool availability and usage patterns [agent/batch_runner.py:50-54]().
- The mapping of specific tools to high-level toolsets is specified in `model_tools.py` via `TOOL_TO_TOOLSET_MAP`, aligning tool call metadata to statistics extraction [agent/batch_runner.py:61-65](), [agent/model_tools.py:12-21]().
- Core toolsets themselves are defined in `toolsets.py`, with validation and resolution of tool names integrated into the batch pipeline [website/docs/reference/toolsets-reference.md:30-92]().
- The orchestration uses the `AIAgent` class from `run_agent.py` to perform inference loops, conversation steps, and trajectory conversion [agent/batch_runner.py:49]().
- Specialized runners like `mini_swe_runner` gather targeted benchmark data with sandboxed backend execution support.

---

## Batch Runner Architecture

### Pipeline and Parallelization

The batch runner operates by reading prompt data from a JSONL dataset, splitting it into batches of prompt indices paired with corresponding prompt details. A Python `multiprocessing.Pool` distributes these batches among worker processes to achieve concurrent execution and increased throughput [agent/batch_runner.py:41-49]().

Within each worker process:

- An isolated `AIAgent` instance is created configured to omit memory/session storage, local file context, and prompt caching, ensuring that runs are stateless and isolated.
- For each prompt, the toolsets are randomly sampled using `toolset_distributions.sample_toolsets_from_distribution` according to configured probabilities [agent/batch_runner.py:50-54]().
- The agent is run on the prompt, returning a stream of messages enriched with metadata about tool calls and assistant internal scratchpads.
- Tool call statistics including counts, successes, failures, and timing are extracted from both assistant and tool messages using `_extract_tool_stats()` [agent/batch_runner.py:290-309]().
- Reasoning statistics are derived by detecting trace markers and "scratchpad" tokens from the assistant’s content with `_extract_reasoning_stats()` [agent/batch_runner.py:311-329]().
- The full conversation data is converted into a trajectory format suitable for supervised fine-tuning with annotations [agent/batch_runner.py:331-336]().
- Samples lacking reasoning traces can be filtered out to maintain dataset quality by removing unsupported runs [agent/batch_runner.py:338-340]().
- Batch results are checkpointed after processing to support resumability and fault tolerance [agent/batch_runner.py:125-228]().

After batch processing completes, batch output files are combined into consolidated trajectory and statistics files with normalized statistics, facilitating downstream training or evaluation use [agent/batch_runner.py:8-12, 71-98]().

### BatchRunner Execution Flow Diagram

```mermaid
flowchart TD
    DatasetJSONL["dataset.jsonl"] --> LoadDataset["batch_runner.py::_load_dataset()"]
    LoadDataset --> CreateBatches["batch_runner.py::_create_batches()"]
    CreateBatches --> MultiprocessingPool["multiprocessing.Pool"]
    MultiprocessingPool --> ProcessWorker["batch_runner.py::_process_batch_worker()"]
    ProcessWorker --> ProcessPrompt["batch_runner.py::_process_single_prompt()"]
    ProcessPrompt --> SampleDist["toolset_distributions.py::sample_toolsets_from_distribution()"]
    SampleDist --> AIAgentInst["run_agent.py::AIAgent"]
    AIAgentInst --> RunConv["AIAgent.run_conversation()"]
    RunConv --> ExtTool["batch_runner.py::_extract_tool_stats()"]
    RunConv --> ExtReason["batch_runner.py::_extract_reasoning_stats()"]
    RunConv --> ConvTrav["AIAgent._convert_to_trajectory_format()"]
    ConvTrav --> FilterCheck{"Has Reasoning?"}
    FilterCheck -->|"no"| DiscardSample["Discard Sample"]
    FilterCheck -->|"yes"| NormTool["batch_runner.py::_normalize_tool_stats()"]
    NormTool --> BatchFile["batch_N.jsonl"]
    ProcessWorker --> SaveCheck["batch_runner.py::_save_checkpoint()"]
    BatchFile --> CombineFiles["batch_runner.py::combine_batch_files()"]
    CombineFiles --> TrajectoriesOut["trajectories.jsonl"]
    CombineFiles --> StatsOut["statistics.json"]
```

For details, see [Batch Runner](#9.1).

Sources: [agent/batch_runner.py:3-65](), [agent/batch_runner.py:41-49](), [agent/batch_runner.py:125-228](), [agent/batch_runner.py:71-98](), [agent/batch_runner.py:290-309](), [agent/batch_runner.py:311-329](), [agent/batch_runner.py:331-336](), [agent/batch_runner.py:338-340]()

---

## Toolset Distributions

To diversify agent behavior and tool usage patterns across batch runs, `toolset_distributions.py` implements a probabilistic sampling mechanism for toolsets to enable on a per-prompt basis.

### Sampling Process

- The entrypoint, `sample_toolsets_from_distribution(name: str)`, queries a configured distribution dictionary.
- Each toolset in the distribution has an associated probability; the function iterates over them and includes each toolset if a uniform random roll is below the probability [agent/batch_runner.py:50-54]().
- If no toolsets get selected by sampling, a fallback ensures that the most probable toolset is nevertheless included, preventing empty toolset runs.
- The resulting sampled toolsets are used to assemble the effective tool configuration injected into `AIAgent` on that sample.

### Toolset Sampling Logic Diagram

```mermaid
flowchart LR
    DistName["Distribution Name"] --> GetDist["toolset_distributions.py::get_distribution()"]
    GetDist --> LoopTools["Iterate Toolsets in Distribution"]
    LoopTools --> RollProb["random.random() < Probability?"]
    RollProb -->|"yes"| IncToolset["Include Toolset"]
    RollProb -->|"no"| SkipToolset["Skip Toolset"]
    IncToolset --> ResList["selected_toolsets: List[str]"]
    SkipToolset --> ResList
    ResList --> GuardEmpty{"Empty List?"}
    GuardEmpty -->|"yes"| FallbackAdd["Add Highest Prob Toolset"]
    GuardEmpty -->|"no"| OutResult["Return Selected Toolsets"]
    FallbackAdd --> OutResult
```

For details, see [Toolset Distributions](#9.2).

Sources: [agent/batch_runner.py:50-54](), [hermes_cli/tools_config.py:96-123](), [website/docs/reference/toolsets-reference.md:101-171]()

---

## Data Generation, Trajectories, and Statistics

The conversation trajectories generated during batch runs record structured information regarding each prompt interaction, including:

- The agent's messages, tool call invocations, and their results.
- Tool usage statistics such as the number of calls, successes, failures, and related counts grouped by toolset and individual tool keys.
- Reasoning metrics extracted by detecting trace markers and "scratchpad" tokens from the assistant latent scratchpad.

The batch runner normalizes the tool statistics schema according to the union of all known tools and toolsets, ensuring consistency across samples [agent/batch_runner.py:84-98](). The trajectories can be further compressed or transformed as needed.

For configurations and examples involving the trajectory format, tool statistics, reasoning metrics extraction, data normalization, as well as the specialized `mini_swe_runner` used for software engineering benchmark data, see [Data Generation and Trajectories](#9.3).

Sources: [agent/batch_runner.py:84-98]()

---

## Evaluation Harnesses

The evaluation system under the `evals/` directory comprises several specialized harnesses that test and benchmark agent performance in practical and technical domains:

- **Compaction Recall:** Assesses the agent’s ability to recall persistent information after context compression events, linking to context compression systems [website/docs/developer-guide/context-compression-and-caching.md:67-100]().
- **Browser-Use:** Tests automated web navigation and interaction tools (via Playwright/CDP), including `browser_navigate`, `browser_click`, and `browser_snapshot` [website/docs/reference/tools-reference.md:17-30](). The `browser_cdp` tool provides a raw Chrome DevTools Protocol (CDP) passthrough for advanced operations [tools/browser_cdp_tool.py:1-8](). The `CDPSupervisor` manages persistent CDP connections for browser dialog and frame detection [tools/browser_supervisor.py:1-9](). The `BrowserControlBroker` handles transport-neutral browser control, binding controllers to callers across different transports [gateway/browser_control_broker.py:1-7](). Artifacts related to browser control are managed by `ArtifactStore` for secure, temporary storage [gateway/browser_control_artifacts.py:1-6]().
- **Codebase Navigability:** Measures the agent’s capacity to find code symbols, traverse file system paths, and work with LSP semantic diagnostics.
- **Core Tool Deferral:** Evaluates whether the agent properly defers non-core knowledge tasks to external tools.
- **Readtool & Session Search:** Benchmarks file reading operation speeds and effectiveness of session search powered by SQLite FTS5.
- **Fanout Resource Benchmark:** Evaluates the resource consumption of parallel task execution in the agent environment.

Each harness records results, logs, and benchmarking metrics that can be aggregated and compared across versions to detect regressions or verify improvements.

For implementation details and usage patterns, see [Evaluation Harnesses](#9.4).

Sources: [evals/](), [website/docs/developer-guide/context-compression-and-caching.md:67-100](), [website/docs/reference/tools-reference.md:17-30](), [tools/browser_cdp_tool.py:1-8](), [tools/browser_supervisor.py:1-9](), [gateway/browser_control_broker.py:1-7](), [gateway/browser_control_artifacts.py:1-6]()

---

## Architecture Bridging Natural Language Concepts to Code Entities

### Batch Processing Component Relationships Diagram

```mermaid
classDiagram
    class BatchRunner {
        "agent/batch_runner.py"
        ALL_POSSIBLE_TOOLS
        _extract_tool_stats()
        _process_single_prompt()
        combine_batch_files()
    }
    class ToolsetDistributions {
        "agent/toolset_distributions.py"
        sample_toolsets_from_distribution()
        get_distribution()
    }
    class ModelTools {
        "agent/model_tools.py"
        TOOL_TO_TOOLSET_MAP
        get_tool_definitions()
    }
    class ToolsetsRegistry {
        "agent/toolsets.py"
        _HERMES_CORE_TOOLS
        TOOLSETS
    }
    class ToolsConfig {
        "hermes_cli/tools_config.py"
        CONFIGURABLE_TOOLSETS
    }
    class AIAgent {
        "run_agent.py"
        run_conversation()
        _convert_to_trajectory_format()
    }
    class CDPSupervisor {
        "tools/browser_supervisor.py"
        start()
        stop()
        snapshot()
    }
    class BrowserControlBroker {
        "gateway/browser_control_broker.py"
        register_controller()
        dispatch_command()
        complete_command()
    }
    class ArtifactStore {
        "gateway/browser_control_artifacts.py"
        store()
        load()
    }

    BatchRunner ..> ToolsetDistributions : samples toolsets for run
    BatchRunner ..> AIAgent : uses for conversation execution
    BatchRunner ..> ModelTools : uses TOOL_TO_TOOLSET_MAP for tool stats
    ModelTools ..> ToolsetsRegistry : defines toolsets
    ToolsConfig ..> ToolsetsRegistry : maps UI labels to toolsets
    ToolsetDistributions ..> ToolsetsRegistry : references toolset keys for sampling
    AIAgent ..> CDPSupervisor : interacts with browser state
    AIAgent ..> BrowserControlBroker : dispatches browser commands
    AIAgent ..> ArtifactStore : manages browser artifacts
```

### Domain Terminology to Core Code Mapping

```mermaid
flowchart LR
    "Batch Processing System" -->|"Implements"| BatchRunner[agent/batch_runner.py]
    "Toolset Distribution Logic" -->|"Implements"| ToolsetDistributions[agent/toolset_distributions.py]
    "Tool-to-Toolset Mapping" -->|"Defined In"| ModelTools[agent/model_tools.py::TOOL_TO_TOOLSET_MAP]
    "Core Toolsets" -->|"Declared In"| ToolsetsRegistry[agent/toolsets.py]
    "Agent Conversation Execution" -->|"Via"| AIAgent[run_agent.py::AIAgent]
    "Evaluation Harnesses" -->|"Located In"| EvalsDir[evals/ directory]
    "Browser CDP Control" -->|"Managed By"| CDPSupervisor[tools/browser_supervisor.py]
    "Browser Command Broker" -->|"Handled By"| BrowserControlBroker[gateway/browser_control_broker.py]
    "Browser Artifact Storage" -->|"Managed By"| ArtifactStore[gateway/browser_control_artifacts.py]
```

Sources: [agent/batch_runner.py:3-65](), [agent/batch_runner.py:41-49](), [agent/batch_runner.py:50-54](), [agent/batch_runner.py:61-65](), [agent/model_tools.py:12-21](), [website/docs/reference/toolsets-reference.md:30-92](), [hermes_cli/tools_config.py:96-123](), [run_agent.py:15-85](), [evals/](), [tools/browser_supervisor.py:1-9](), [gateway/browser_control_broker.py:1-7](), [gateway/browser_control_artifacts.py:1-6]()

---

## Usage Examples

### Running a batch with specified options

```bash
python batch_runner.py \
  --dataset_file=data/prompts.jsonl \
  --batch_size=10 \
  --run_name=science_run \
  --distribution=image_gen \
  --num_workers=4
```

This command runs batch inference on prompts from `data/prompts.jsonl` in batches of 10, selecting toolsets based on the `image_gen` distribution, using 4 parallel worker processes. Results are checkpointed and saved under a run name `science_run`.

### Resuming a batch run safely after interruption

```bash
python batch_runner.py \
  --dataset_file=data/prompts.jsonl \
  --batch_size=10 \
  --run_name=science_run \
  --resume
```

Using the `--resume` flag, the batch runner picks up from the last saved checkpoint, saving prior work and avoiding redundant computation.

Sources: [agent/batch_runner.py:14-21]()

---

# Child Pages

- [Batch Runner](#9.1)
- [Toolset Distributions](#9.2)
- [Data Generation and Trajectories](#9.3)
- [Evaluation Harnesses](#9.4)

---

