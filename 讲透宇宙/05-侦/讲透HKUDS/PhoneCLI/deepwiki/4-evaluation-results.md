<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/PhoneCLI · page 4 Evaluation & Results · fetched 2026-11-09 -->

# Evaluation & Results

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [evaluation/definition.py](evaluation/definition.py)
- [generate_result.py](generate_result.py)
- [phonecli_android/generate_result.py](phonecli_android/generate_result.py)

</details>



This section provides a high-level overview of the evaluation framework used to benchmark the PhoneCLI agent. It covers how tasks are defined, the mechanisms for judging agent performance, and the pipeline for aggregating and reporting results. The goal is to provide a clear understanding of how the agent's effectiveness is measured and analyzed.

## Task Definitions and Per-App Checkers
The evaluation process begins with clearly defined tasks for various applications. These tasks are specified in YAML configuration files and are accompanied by programmatic checkers that determine the success or failure of an agent's attempt. These checkers often involve verifying specific states or data within the application after the agent has completed its actions.

For details, see [Task Definitions and Per-App Checkers](#4.1).

Sources:
- [phonecli_android/generate_result.py:15-17]()

## LLM Judging and Result Aggregation
After an agent attempts a task, its performance is judged. This judging can involve both programmatic checkers and, for more complex or subjective tasks, an LLM-based evaluator. The results from individual task runs, including detailed traces, are then aggregated into comprehensive reports. This aggregation process calculates various metrics, such as success rates and resource usage, and can generate human-readable reports, including Excel files.

For details, see [LLM Judging and Result Aggregation](#4.2).

### Evaluation Pipeline
The following diagram illustrates the high-level flow of the evaluation pipeline, from task execution to result generation.

```mermaid
graph TD
    A[Task Execution] --> B{Trace Generation};
    B --> C[trace.jsonl];
    C --> D[Evaluation_Task.evaluate()];
    D --> E[AppConfig.metrics];
    D --> F[LLM Judging];
    F --> G[results.jsonl];
    G --> H[generate_result.py];
    H --> I[total.jsonl];
    I --> J[Excel Report];

    subgraph "Evaluation Components"
        D
        E
        F
    end

    subgraph "Output Files"
        C
        G
        I
        J
    end
```
Sources:
- [phonecli_android/generate_result.py:78-84]()
- [phonecli_android/generate_result.py:93-105]()
- [phonecli_android/generate_result.py:161-188]()
- [evaluation/definition.py:93-106]()

### LLM Judging Process
The `detect_answer` function in `evaluation/definition.py` is central to LLM-based judging. It takes a question, the model's answer, and a standard answer, then uses a judge model (e.g., `glm4` or `gpt`) to determine if the model's answer is "True" or "False" based on the standard.

```mermaid
graph TD
    A[Question] --> B[detect_answer(question, model_answer, standard_answer, args)];
    C[Model Answer] --> B;
    D[Standard Answer] --> B;
    E[args.judge_model] --> B;
    B --> F{Call Judge Model};
    F -- "glm4" --> G[get_completion_glm(prompt, glm4_key)];
    F -- "gpt" --> H[get_completion_gpt(prompt, model_name)];
    G --> I{Return Message};
    H --> I;
    I -- "Contains 'True'" --> J[True];
    I -- "Contains 'False'" --> K[False];
```
Sources:
- [evaluation/definition.py:93-106]()
- [evaluation/definition.py:137-145]()
- [evaluation/definition.py:152-164]()

## Benchmark Results and Ablations
This section will present the quantitative results of the agent's performance on the AndroidLab benchmark. It will include success rates, analysis of step and token reductions achieved through the use of app maps, and a comparison of device-side versus cloud-side processing ratios. Additionally, specific case studies will be highlighted to illustrate key findings and agent behaviors.

For details, see [Benchmark Results and Ablations](#4.3).

Sources:
- [phonecli_android/generate_result.py:87-158]()

---

