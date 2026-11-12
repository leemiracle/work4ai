<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/PhoneCLI · page 3 Android Harness & AndroidLab Benchmark · fetched 2026-11-09 -->

# Android Harness & AndroidLab Benchmark

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eval.py](eval.py)
- [phonecli_android/README.md](phonecli_android/README.md)
- [phonecli_android/README_CN.md](phonecli_android/README_CN.md)

</details>



This page provides a high-level overview of the Android agent harness, which is central to the AndroidLab benchmark. It covers the core components involved in running tasks on Android devices, including the evaluation framework, agent implementations, and the process of building app maps. The AndroidLab benchmark evaluates two types of agents: PhoneCLI, which leverages pre-built app maps for efficient macro replay with VLM fallback, and a Baseline agent that relies solely on a VLM loop [phonecli_android/README.md:7-12]().

The `phonecli_android/` directory contains the Android-specific implementation of the PhoneCLI agent and the AndroidLab benchmark. All commands related to this harness should be run from within the `phonecli_android/` directory to ensure correct module imports and relative path resolution [phonecli_android/README.md:39-47]().

## Task Runner and Parallel Execution

The `eval.py` script serves as the primary entry point for running tasks within the Android harness [eval.py:110](). It orchestrates the execution of tasks, either serially or in parallel, against Android emulators (AVDs). The script parses command-line arguments to determine which tasks to run, which configuration to use, and whether to run in debug or parallel mode [eval.py:29-37]().

The `eval.py` script loads configuration from YAML files, expanding environment variables using `config_env.load_config()` [eval.py:41-42](). It then identifies the appropriate `AutoTest` class (e.g., `MacroAgentTask_AutoTest` for PhoneCLI or `ScreenshotCloudTask_AutoTest` for the baseline) based on the loaded configuration [eval.py:47-48]().

For parallel execution, `eval.py` utilizes `evaluation/parallel.py` to distribute tasks across multiple worker processes [eval.py:113](). Each worker manages its own AVD lifecycle, including cloning, booting, and restoring snapshots, ensuring a clean environment for each task.

For details, see [Task Runner and Parallel Execution](#3.1).

### Evaluation Workflow

The following diagram illustrates the high-level workflow of the AndroidLab benchmark, showing how `eval.py` interacts with `auto_test.py` and the different agent types.

```mermaid
graph TD
    A[eval.py: Task Runner] --> B{Load Configs};
    B --> C[agent_config];
    B --> D[task_config];
    B --> E[eval_config];
    C --> F{get_agent(agent_config)};
    D --> G{Resolve Task List};
    E --> H[single_config];
    G --> I[all_task_start_info];
    F --> J[Agent Instance];
    I --> K{Determine AutoTest Class};
    K -- "MacroAgentTask_AutoTest (PhoneCLI)" --> L[MacroAgentTask_AutoTest];
    K -- "ScreenshotCloudTask_AutoTest (Baseline)" --> M[ScreenshotCloudTask_AutoTest];
    J --> L;
    J --> M;
    L --> N{Run Tasks (Serial/Parallel)};
    M --> N;
    N --> O[Logs & Traces];

    subgraph phonecli_android/
        A; B; C; D; E; F; G; H; I; J; K; L; M; N; O;
    end
```
Sources:
- [eval.py:1-114]()
- [phonecli_android/README.md:18-36]()

## MacroAgent: Routing, Replay and Fallback

The `MacroAgentTask_AutoTest` (PhoneCLI) agent, defined in `evaluation/macro_agent.py`, implements a two-phase execution strategy. Initially, it attempts to route tasks to pre-recorded ADB macro replays, which are fast and cost-effective [phonecli_android/README.md:8-10](). These macros are defined within the app maps.

If a task cannot be fully completed by macro replay, or if the agent encounters an unexpected state (e.g., landing verification fails), it falls back to a VLM (Vision-Language Model) loop [phonecli_android/README.md:10](). This VLM loop allows the agent to dynamically interact with the UI based on visual observations and LLM reasoning. The `evaluation/app_map.py` module is crucial for runtime queries against the loaded app map, enabling the agent to understand screen states and available actions.

For details, see [MacroAgent: Routing, Replay and Fallback](#3.2).

## Device Control and Page Executors

Device control for the Android harness is primarily handled via ADB (Android Debug Bridge) commands. The `adb_client.py` module provides the interface for interacting with Android devices. Higher-level control and UI interaction are managed by `utils_mobile/and_controller.py` and `xml_tool.py`, which parse UI hierarchies and execute actions.

The `page_executor/` directory contains various executors that define action primitives. For instance, `text_executor.py` handles text input, while `simple_vision_executor.py` might handle tap or swipe actions based on visual cues. These executors translate agent decisions into concrete device interactions. The `recorder/json_recorder.py` module is responsible for logging all actions and observations, generating detailed traces of each task execution.

For details, see [Device Control and Page Executors](#3.3).

## Model Backends (agent/)

The `agent/model.py` module provides an abstraction layer for integrating various LLM (Large Language Model) and MLLM (Multimodal Large Language Model) backends. This abstraction allows the Android harness to switch between different models without significant code changes.

The `agent/` directory contains implementations for various LLM backends, such as `glm4` and `qwen_llm_model`, and MLLM backends like `claude_model` and `qwen_model`. These models are used for tasks requiring natural language understanding, reasoning, and visual perception, especially during the VLM fallback phase. The `prompt/response` utilities within this module assist in formatting prompts and parsing model outputs.

For details, see [Model Backends (agent/)](#3.4).

## Android App Map Building

App maps are YAML navigation graphs that encode the structure and navigation paths of an Android application [phonecli_android/README.md:15](). These maps are central to the PhoneCLI agent's efficiency. The `build_android_map.py` script is responsible for automatically generating these app maps.

The map building process involves:
1.  **AVD Cloning and Headless Boot**: A clean AVD snapshot is cloned and booted in headless mode to ensure a consistent environment [phonecli_android/README.md:110-111]().
2.  **BFS Crawler**: A Breadth-First Search (BFS) algorithm crawls the target application via ADB, exploring different screens and identifying UI elements [phonecli_android/README.md:110-111]().
3.  **LLM Element Classification and Enrichment**: An LLM is used to classify UI elements as stable or dynamic, and to enrich them with aliases, semantic types, and descriptions [phonecli_android/README.md:111]().

The generated app maps are stored in `app_maps/<app>_android.yaml` and follow a specific YAML schema, detailing screens, elements, and `screen_macros` (pre-recorded action sequences) [phonecli_android/README.md:155-168](). The repository includes pre-built maps for 9 benchmark applications [phonecli_android/README_CN.md:180-194]().

For details, see [Android App Map Building](#3.5).

### App Map Building Workflow

```mermaid
graph TD
    A[build_android_map.py: App Map Builder] --> B{AVD Lifecycle Management};
    B -- "Clone AVD" --> C[AVD Instance];
    C -- "Headless Boot" --> D[Running Emulator];
    D --> E[BFS Crawler (ADB)];
    E -- "Explore App UI" --> F[Discovered Screens & Elements];
    F --> G{LLM Classification & Enrichment};
    G -- "Classify Elements (stable/dynamic)" --> H[Enriched Elements];
    G -- "Add Aliases, Semantic Types, Descriptions" --> H;
    H --> I[Generate app_maps/<app>_android.yaml];
    I --> J[PhoneCLI Agent (Runtime)];

    subgraph phonecli_android/
        A; B; C; D; E; F; G; H; I; J;
    end
```
Sources:
- [phonecli_android/README.md:110-111]()
- [phonecli_android/README.md:155-168]()
- [phonecli_android/README_CN.md:180-194]()

---

