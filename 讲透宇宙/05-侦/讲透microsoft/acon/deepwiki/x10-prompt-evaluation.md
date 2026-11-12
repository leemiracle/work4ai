<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/acon · extra page Prompt Evaluation · fetched 2026-10-26 -->

# Prompt Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experiments/appworld/run_ctxopt_pipeline.py](experiments/appworld/run_ctxopt_pipeline.py)

</details>



This page describes how the ACON framework evaluates optimized prompts to determine which performs best for context optimization tasks. The evaluation system runs experiments with multiple prompt variants, collects performance metrics, and automatically selects the optimal prompt configuration.

For information about configuring the optimization pipeline itself, see [Pipeline Configuration](#7.2.1). For details on the underlying token analysis system, see [analyze_experiment_tokens_v2](#7.1.1).

## Overview

The prompt evaluation system in `run_ctxopt_pipeline.py` implements an automated comparative evaluation workflow. After prompts have been optimized (typically by external optimization tools), this pipeline:

1. Generates context optimization configuration files for each prompt variant
2. Executes experiments using each configuration on a designated dataset split
3. Collects performance metrics including token usage and task success rates
4. Ranks prompts by specified criteria
5. Automatically selects and saves the best-performing configuration

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:1-17]()

## Evaluation Workflow

```mermaid
graph TB
    subgraph "Input Stage"
        PROMPTS_DIR["Prompts Directory<br/>optimized_prompts/"]
        JINJA_FILES["Jinja Templates<br/>improved_*_prompt_*.jinja"]
        PROMPTS_DIR --> JINJA_FILES
    end
    
    subgraph "Config Generation Stage"
        DETECT["Detect Prompt Type<br/>history vs. obs"]
        GEN_YAML["generate_yaml_config_*<br/>Create YAML configs"]
        CONFIG_DIR["Config Output Directory<br/>context_opt/<derived>/"]
        
        JINJA_FILES --> DETECT
        DETECT --> GEN_YAML
        GEN_YAML --> CONFIG_DIR
    end
    
    subgraph "Execution Stage"
        LOOP["Sequential Execution Loop"]
        RUN_ALL["subprocess.run<br/>run_all.py --co_config_path"]
        EVAL_CMD["appworld evaluate<br/>{run_id} {split}"]
        
        CONFIG_DIR --> LOOP
        LOOP --> RUN_ALL
        RUN_ALL --> EVAL_CMD
    end
    
    subgraph "Collection Stage"
        SUMMARY_JSON["experiment_summary.json<br/>success_rate, total_tasks"]
        EVAL_JSON["evaluations/{split}.json<br/>task_goal_completion"]
        RUN_SUMMARIES["run_summaries list<br/>Per-config metadata"]
        
        EVAL_CMD --> SUMMARY_JSON
        EVAL_CMD --> EVAL_JSON
        SUMMARY_JSON --> RUN_SUMMARIES
        EVAL_JSON --> RUN_SUMMARIES
    end
    
    subgraph "Analysis Stage"
        TOKEN_ANALYSIS["analyze_experiment_tokens_v2<br/>Token usage calculation"]
        COMP_ROWS["comp_rows list<br/>Complete metrics per config"]
        
        RUN_SUMMARIES --> TOKEN_ANALYSIS
        TOKEN_ANALYSIS --> COMP_ROWS
    end
    
    subgraph "Output Stage"
        RANKING["Sort by total_in ascending"]
        RICH_TABLE["Rich Console Table<br/>Visual comparison"]
        MD_TABLE["ctxopt_comparison_*.md<br/>Markdown report"]
        BEST_CONFIG["best_improved_*_prompt_samples.yaml<br/>Selected winner"]
        
        COMP_ROWS --> RANKING
        RANKING --> RICH_TABLE
        RANKING --> MD_TABLE
        RANKING --> BEST_CONFIG
    end
```

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:87-448]()

## Prompt Discovery and Configuration Generation

The pipeline begins by scanning the specified prompts directory for Jinja template files. It preferentially selects templates with specific naming patterns based on the context optimization type.

### Template Discovery Logic

For history optimization, the system searches for files matching `improved_history_prompt_*.jinja`. For observation optimization, it searches for `improved_observation_prompt_*.jinja`. If no preferred templates are found, the system falls back to all `.jinja` files excluding system prompts.

```mermaid
graph LR
    subgraph "Template Filtering"
        ALL_JINJA["All *.jinja files"]
        EXCLUDE["Exclude:<br/>system_prompt.jinja<br/>system_success_workflow.jinja<br/>manifest.json"]
        FILTERED["Filtered templates"]
        
        ALL_JINJA --> EXCLUDE
        EXCLUDE --> FILTERED
    end
    
    subgraph "Preference Selection"
        CTXOPT_TYPE["args.ctxopt_type"]
        HIST_PATTERN["startswith<br/>improved_history_prompt_"]
        OBS_PATTERN["startswith<br/>improved_observation_prompt_"]
        PREFERRED["Preferred templates"]
        
        FILTERED --> CTXOPT_TYPE
        CTXOPT_TYPE -->|history| HIST_PATTERN
        CTXOPT_TYPE -->|obs| OBS_PATTERN
        HIST_PATTERN --> PREFERRED
        OBS_PATTERN --> PREFERRED
    end
    
    subgraph "Config Generation"
        LOOP_TEMPLATES["For each template"]
        GENERATE["generate_yaml_config_*<br/>Build YAML dict"]
        WRITE_FILE["Write to config_out_dir/<br/>{yaml_stem}.yaml"]
        
        PREFERRED --> LOOP_TEMPLATES
        LOOP_TEMPLATES --> GENERATE
        GENERATE --> WRITE_FILE
    end
```

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:107-116](), [experiments/appworld/run_ctxopt_pipeline.py:144-195]()

### Configuration Parameters

For history optimization, the generated YAML configuration includes:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `type` | "history" | Identifies optimizer type |
| `model` | From `--model-name` arg | Model for compression |
| `compressor_type` | "full" | Full compression mode |
| `history_summarization_threshold` | 4096 | Token threshold for summarization |
| `preserve_last_k_turns` | 1 | Recent turns to preserve |
| `history_summary_rule` | "reset" | Summary accumulation strategy |
| `history_prompt_dir` | Path to prompts directory | Template location |
| `history_version` | From `--opt-version` arg | Version identifier |

For observation optimization, the configuration includes:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `type` | "obs" | Identifies optimizer type |
| `model` | From `--model-name` arg | Model for compression |
| `compressor_type` | "full" | Full compression mode |
| `obs_summarization_threshold` | 1024 | Token threshold for summarization |
| `obs_prompt_dir` | Path to prompts directory | Template location |
| `obs_version` | From `--opt-version` arg | Version identifier |

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:51-84]()

## Experiment Execution

Once configurations are generated, the pipeline sequentially executes experiments for each prompt variant. Each execution follows a three-step process:

```mermaid
graph TB
    subgraph "Per-Config Execution Loop"
        CONFIG["Config YAML<br/>improved_*_prompt_N.yaml"]
        TAG_SUFFIX["Extract suffix N<br/>from filename"]
        PER_RUN_TAG["Compose tag:<br/>{base_tag}_{suffix}"]
        
        CONFIG --> TAG_SUFFIX
        TAG_SUFFIX --> PER_RUN_TAG
    end
    
    subgraph "Step 1: Run Experiment"
        CMD_BUILD["Build command:<br/>run_all.py --split --tag<br/>--model_name --co_config_path"]
        SUBPROCESS["subprocess.run<br/>Execute in script_dir"]
        CHECK_RC["Check returncode"]
        
        PER_RUN_TAG --> CMD_BUILD
        CMD_BUILD --> SUBPROCESS
        SUBPROCESS --> CHECK_RC
    end
    
    subgraph "Step 2: Evaluate Results"
        RUN_ID["Compute run_id:<br/>{model}_{tag}"]
        EVAL_CMD["appworld evaluate<br/>{run_id} {split}"]
        EVAL_SUBPROCESS["subprocess.run<br/>External CLI"]
        
        CHECK_RC -->|success| RUN_ID
        RUN_ID --> EVAL_CMD
        EVAL_CMD --> EVAL_SUBPROCESS
    end
    
    subgraph "Step 3: Collect Metrics"
        SUMMARY_PATH["outputs/{run_id}/{split}/<br/>experiment_summary.json"]
        EVAL_PATH["experiments/outputs/{run_id}/<br/>evaluations/{split}.json"]
        EXTRACT["Extract:<br/>success_rate<br/>total_tasks<br/>task_goal_completion"]
        APPEND["Append to<br/>run_summaries list"]
        
        EVAL_SUBPROCESS --> SUMMARY_PATH
        EVAL_SUBPROCESS --> EVAL_PATH
        SUMMARY_PATH --> EXTRACT
        EVAL_PATH --> EXTRACT
        EXTRACT --> APPEND
    end
```

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:232-299]()

### Command Construction

The command for each experiment run includes:

- **`--split`**: Dataset split to evaluate (e.g., `train_history_tiny`)
- **`--tag`**: Unique tag composed from base tag and config suffix
- **`--model_name`**: Agent model name (from `--main-model-name`)
- **`--co_config_path`**: Path to the generated YAML configuration
- **`--debug`**: Optional flag to reduce workload (if provided)
- **`--task_ids`**: Optional list of specific task IDs to run

The execution environment ensures the `PYTHONPATH` includes `src/` for local imports.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:246-264](), [experiments/appworld/run_ctxopt_pipeline.py:216-221]()

## Metrics Collection

After each experiment completes, the pipeline collects metrics from two sources:

### Experiment Summary Metrics

The `experiment_summary.json` file provides basic execution statistics:

- **`success_rate`**: Percentage of successful task completions
- **`total_tasks`**: Number of tasks executed

### Evaluation Metrics

The evaluation output at `evaluations/{split}.json` provides the official AppWorld metric:

- **`aggregate.task_goal_completion`**: Official task completion score

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:276-298]()

## Token Analysis and Comparison

After all configurations have been executed, the pipeline performs comprehensive token analysis using the `analyze_experiment_tokens_v2` function from the analysis tools.

```mermaid
graph TB
    subgraph "Token Analysis Per Config"
        RUN_SUMMARY["run_summaries entry<br/>{run_id, cfg, tag, ...}"]
        ANALYZE_CALL["analyze_experiment_tokens_v2<br/>agent_model, optimizer_model"]
        RESULTS["Results dict:<br/>tasks → per-task metrics"]
        
        RUN_SUMMARY --> ANALYZE_CALL
        ANALYZE_CALL --> RESULTS
    end
    
    subgraph "Aggregation"
        LOOP_TASKS["For each task in results"]
        AGENT_TOKENS["agent.total_input_tokens"]
        OPT_TOKENS["optimizer.total_input_tokens"]
        NUM_STEPS["agent.num_steps"]
        SUM["Accumulate across tasks"]
        
        RESULTS --> LOOP_TASKS
        LOOP_TASKS --> AGENT_TOKENS
        LOOP_TASKS --> OPT_TOKENS
        LOOP_TASKS --> NUM_STEPS
        AGENT_TOKENS --> SUM
        OPT_TOKENS --> SUM
        NUM_STEPS --> SUM
    end
    
    subgraph "Computed Metrics"
        TOTAL_IN["total_in =<br/>agent_in + opt_in"]
        AVG_STEPS["avg_steps =<br/>total_steps / step_tasks"]
        COMP_ROW["comp_rows entry:<br/>Complete metrics per config"]
        
        SUM --> TOTAL_IN
        SUM --> AVG_STEPS
        TOTAL_IN --> COMP_ROW
        AVG_STEPS --> COMP_ROW
    end
```

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:303-338]()

### Collected Metrics

For each configuration, the comparison row contains:

| Field | Source | Description |
|-------|--------|-------------|
| `cfg` | Config filename | YAML configuration name |
| `tag` | Experiment tag | Unique identifier for this run |
| `run_id` | Computed | `{model}_{tag}` format |
| `tasks` | `experiment_summary.json` | Total tasks executed |
| `success_rate` | `experiment_summary.json` | Basic success percentage |
| `task_goal_completion` | `evaluations/{split}.json` | Official AppWorld metric |
| `agent_in` | Token analysis | Total agent input tokens |
| `opt_in` | Token analysis | Total optimizer input tokens |
| `total_in` | Computed | Sum of agent and optimizer tokens |
| `avg_steps` | Token analysis | Average steps per task |

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:327-338]()

## Ranking and Selection

The pipeline ranks configurations using a two-stage process:

### Initial Ranking by Token Usage

First, all configurations are sorted by `total_in` (total input tokens) in ascending order. This provides a baseline ranking focused on efficiency.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:340-341]()

### Best Prompt Selection

The final "best" configuration is selected using a more sophisticated strategy:

```mermaid
graph TB
    subgraph "Selection Strategy"
        COMP_ROWS["comp_rows<br/>All evaluated configs"]
        PRIMARY["Primary Key:<br/>task_goal_completion<br/>maximize"]
        TIE_BREAKER["Tie-breaker:<br/>total_in<br/>minimize"]
        MAX_FUNC["max() with composite key"]
        
        COMP_ROWS --> MAX_FUNC
        PRIMARY --> MAX_FUNC
        TIE_BREAKER --> MAX_FUNC
    end
    
    subgraph "Winner Selection"
        BEST_ROW["best_row with highest score"]
        BEST_CFG_NAME["best_cfg_name<br/>Config filename"]
        LOCATE["Find config in generated list"]
        
        MAX_FUNC --> BEST_ROW
        BEST_ROW --> BEST_CFG_NAME
        BEST_CFG_NAME --> LOCATE
    end
    
    subgraph "Output"
        COPY_CONTENT["Read config content"]
        DEST_NAME["Destination:<br/>best_improved_history_prompt_samples.yaml<br/>or best_improved_observation_prompt_samples.yaml"]
        WRITE["Write to config_out_dir/"]
        
        LOCATE --> COPY_CONTENT
        COPY_CONTENT --> DEST_NAME
        DEST_NAME --> WRITE
    end
```

The selection uses this composite key:

1. **Primary criterion**: Maximize `task_goal_completion` (AppWorld's official metric)
2. **Tie-breaker**: Minimize `total_in` (total input tokens) for efficiency

This ensures the best prompt achieves the highest task completion while preferring more efficient prompts when multiple configurations perform equally well.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:399-444]()

## Output Artifacts

The evaluation process generates several output files for analysis and record-keeping:

### Rich Console Table

If the `rich` library is available, the pipeline displays a formatted comparison table in the console with columns:

- Rank (by total input tokens)
- Config filename
- Experiment tag
- Tasks executed
- Average steps
- Task goal completion percentage
- Agent input tokens
- Optimizer input tokens
- Total input tokens

The table is sorted by ascending `total_in`, with the lowest-token configuration listed first.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:343-364]()

### Markdown Comparison Table

A markdown file named `ctxopt_comparison_{timestamp}.md` is saved to the prompts directory containing:

- Experiment metadata (model, split)
- Full comparison table with all metrics
- Identification of the best configuration by total input tokens
- Timestamp for reference

This file provides a permanent record of the evaluation results.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:376-395]()

### Best Configuration File

The winning configuration is copied to a standardized filename in the `config_out_dir`:

- **For history optimization**: `best_improved_history_prompt_samples.yaml`
- **For observation optimization**: `best_improved_observation_prompt_samples.yaml`

This allows downstream processes to easily reference the optimal configuration without needing to parse comparison results.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:429-444]()

## Fallback Mechanisms

The pipeline includes several fallback mechanisms to ensure robustness:

### YAML Library Fallback

If the `yaml` library is not available, the pipeline implements a minimal YAML writer specifically for the configuration schema. This writer manually constructs YAML-formatted text for the required fields.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:28-33](), [experiments/appworld/run_ctxopt_pipeline.py:175-194]()

### Rich Library Fallback

If the `rich` library is not available, the pipeline outputs a plain-text comparison table with the same information in a simpler format.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:36-42](), [experiments/appworld/run_ctxopt_pipeline.py:365-373]()

### Evaluation Failure Handling

If the external `appworld evaluate` command fails, the pipeline logs a warning but continues processing other configurations. Similarly, if token analysis fails for a specific configuration, the pipeline continues with available data.

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:267-273](), [experiments/appworld/run_ctxopt_pipeline.py:396-397]()

## Example Usage

To run prompt evaluation for history optimization:

```bash
python experiments/appworld/run_ctxopt_pipeline.py \
  --ctxopt-type history \
  --prompts-dir /path/to/optimized_prompts \
  --model-name gpt-4.1-mini \
  --main-model-name gpt-4.1-mini \
  --tag my_optimization_run \
  --split train_history_tiny
```

This command will:

1. Scan `/path/to/optimized_prompts` for history prompt templates
2. Generate YAML configs for each template
3. Run experiments using `gpt-4.1-mini` on the `train_history_tiny` split
4. Evaluate results using AppWorld's evaluator
5. Analyze token usage across all configurations
6. Display comparison table and save markdown report
7. Save the best configuration as `best_improved_history_prompt_samples.yaml`

For a dry run (config generation only, no execution):

```bash
python experiments/appworld/run_ctxopt_pipeline.py \
  --ctxopt-type history \
  --prompts-dir /path/to/optimized_prompts \
  --model-name gpt-4.1-mini \
  --dry-run
```

**Sources:** [experiments/appworld/run_ctxopt_pipeline.py:8-16](), [experiments/appworld/run_ctxopt_pipeline.py:87-101](), [experiments/appworld/run_ctxopt_pipeline.py:201-203]()

---

