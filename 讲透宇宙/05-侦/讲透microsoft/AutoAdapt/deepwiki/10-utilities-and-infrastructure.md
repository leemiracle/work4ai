<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/AutoAdapt · page 10 Utilities and Infrastructure · fetched 2026-10-26 -->

# Utilities and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/autoadapt/utils/llm.py](src/autoadapt/utils/llm.py)
- [src/autoadapt/utils/log.py](src/autoadapt/utils/log.py)
- [src/autoadapt/utils/token_usage.py](src/autoadapt/utils/token_usage.py)

</details>



The **Utilities and Infrastructure** module provides the foundational shared services required for the AutoAdapt pipeline. This includes standardized LLM client abstractions, unified logging, token usage tracking, and a comprehensive suite of model training and evaluation utilities. These modules ensure consistency across the planning, HPO, and execution phases.

### Infrastructure Overview

The infrastructure layer bridges high-level agent logic with low-level execution requirements like GPU memory management and API communication.

#### Utility Component Interaction
The following diagram illustrates how utility classes interact with the core execution flow.

```mermaid
graph TD
    subgraph "Natural Language Space"
        [UserPrompt] --> [LLM_Client]
        [AgentDebate] --> [LogHandler]
    end

    subgraph "Code Entity Space"
        [LLM_Client] --> |"create()"| ChatCompletionModel["ChatCompletionModel (llm.py)"]
        [LogHandler] --> |"emit()"| LogHandlerClass["LogHandler (log.py)"]
        [TokenTracker] --> |"update()"| TokenUsageCallback["TokenUsageCallback (token_usage.py)"]
        [Execution] --> |"load_model()"| TemplateUtils["template.py Utilities"]
    end

    ChatCompletionModel -.-> |"tracks"| TokenUsageCallback
    LogHandlerClass -.-> |"persists"| log_jsonl["log.jsonl"]
```
**Sources:** [src/autoadapt/utils/llm.py:8-22](), [src/autoadapt/utils/log.py:21-26](), [src/autoadapt/utils/token_usage.py:5-14]()

---

### LLM Client and Async Utilities
AutoAdapt abstracts LLM interactions through a unified client interface that supports both Azure OpenAI and standard OpenAI backends. This infrastructure handles:
*   **Authentication:** Integration with `DefaultAzureCredential` for managed identity support [src/autoadapt/utils/llm.py:21-22]().
*   **Structured Responses:** Pydantic models (e.g., `PARAMS_PROMPT_ResponseClass`) ensure that LLM outputs are validated before being consumed by the orchestrator [src/autoadapt/utils/llm.py:38-43]().
*   **Process Management:** Utilities in `misc.py` for handling subprocess lifecycles and terminal output redirection via `tee_output`.

For details, see [LLM Client and Async Utilities](#10.1).

**Sources:** [src/autoadapt/utils/llm.py:24-74](), [src/autoadapt/utils/misc.py:1-50]()

---

### Logging and Token Tracking
System-wide observability is provided through specialized logging and cost-tracking modules.
*   **LogHandler:** A custom `logging.FileHandler` that intercepts `OrchestrationEvent`, `AgentEvent`, and `LLMCallEvent` to generate a `log.jsonl` file suitable for the React UI [src/autoadapt/utils/log.py:21-101]().
*   **TokenUsageCallback:** Tracks prompt and completion tokens across different models (e.g., `gpt-4o`, `o1-mini`) and calculates estimated costs based on predefined pricing tiers [src/autoadapt/utils/token_usage.py:5-25]().

#### Token Tracking Logic
| Class | Function | Responsibility |
| :--- | :--- | :--- |
| `LogHandler` | `emit()` | Formats events into JSON for the frontend [src/autoadapt/utils/log.py:26-35](). |
| `TokenUsageCallback` | `update()` | Aggregates token counts by source and model [src/autoadapt/utils/token_usage.py:27-49](). |
| `TokenUsageCallback` | `token_usage_report()` | Generates a human-readable cost breakdown [src/autoadapt/utils/token_usage.py:50-115](). |

**Sources:** [src/autoadapt/utils/log.py:1-102](), [src/autoadapt/utils/token_usage.py:1-118]()

---

### Model Training and Evaluation Utilities
The system provides a robust set of utilities for managing the lifecycle of Large Language Models during adaptation.
*   **Model Loading:** The `load_model` and `get_model` functions handle engine selection between HuggingFace `transformers` and `vLLM` for optimized inference [src/autoadapt/utils/template.py:100-150]().
*   **GPU Management:** Integration with `NVML` to monitor and clear GPU memory between HPO trials.
*   **Evaluation:** The `Evaluator` class and `evaluate_with_llm` function implement the "LLM-as-a-judge" pattern, using structured prompts to determine correctness against ground truth [src/autoadapt/utils/llm.py:68-74]().

For details, see [Model Training and Evaluation Utilities](#10.2).

#### Infrastructure Mapping: Code to Resources
```mermaid
graph LR
    subgraph "Infrastructure Layer"
        [TemplateUtils] --> |"manages"| GPU["NVML GPU Memory"]
        [TemplateUtils] --> |"loads"| Data["load_user_data()"]
        [LLMUtils] --> |"validates"| Schema["Pydantic ResponseClasses"]
    end

    subgraph "System Resources"
        GPU --- [NVIDIA_SMI]
        Data --- [JSONL/Parquet/CSV]
        Schema --- [LLM_Output]
    end
```
**Sources:** [src/autoadapt/utils/template.py:10-200](), [src/autoadapt/utils/llm.py:24-74]()

---

### Insights Generation
Post-execution, the system uses the `INSIGHTS_PROMPT_TEMPLATE` to synthesize the results of multi-agent debates and HPO trials into a markdown report for the user [src/autoadapt/utils/llm.py:75-99](). This bridges the gap between raw parameter optimization and human-understandable reasoning.

**Sources:** [src/autoadapt/utils/llm.py:75-99]()

---

