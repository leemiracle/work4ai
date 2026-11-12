<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/LMOps · extra page Statistical Analysis and Reporting · fetched 2026-10-26 -->

# Statistical Analysis and Reporting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [RRM-evaluation/analysis/get_benchmark_results.py](RRM-evaluation/analysis/get_benchmark_results.py)
- [RRM-evaluation/analysis/get_per_token_reward.py](RRM-evaluation/analysis/get_per_token_reward.py)
- [RRM-evaluation/analysis/get_subtoken_statistics.py](RRM-evaluation/analysis/get_subtoken_statistics.py)

</details>



This document covers the statistical analysis and reporting components of the RRM-evaluation system that generate human-readable reports from evaluation results. These tools transform raw evaluation data into formatted benchmark tables, comparative analyses, and statistical summaries suitable for research publication and performance assessment.

For information about data processing and format conversion, see [Data Processing and Conversion](#3.2.1). For visualization and plotting capabilities, see [Visualization and Plotting](#3.2.2).

## Overview

The statistical analysis and reporting system consists of three main components that process evaluation results and generate formatted reports:

```mermaid
graph TD
    subgraph "Input Sources"
        HF_Repo["allenai/reward-bench-results<br/>HuggingFace Repository"]
        Local_Results["Local Evaluation Results"]
        Dataset["allenai/reward-bench<br/>Dataset"]
    end
    
    subgraph "Analysis Scripts"
        Benchmark[get_benchmark_results.py]
        DPO[get_dpo_ref_free_results.py] 
        Subtoken[get_subtoken_statistics.py]
    end
    
    subgraph "Output Formats"
        Markdown["Markdown Tables"]
        LaTeX["LaTeX Tables"]
        CSV["CSV Files"]
    end
    
    HF_Repo --> Benchmark
    HF_Repo --> DPO
    Dataset --> Subtoken
    
    Benchmark --> Markdown
    Benchmark --> LaTeX
    Benchmark --> CSV
    
    DPO --> Markdown
    DPO --> LaTeX
    DPO --> CSV
    
    Subtoken --> Markdown
    Subtoken --> LaTeX
    Subtoken --> CSV
```

Sources: [RRM-evaluation/analysis/get_benchmark_results.py:1-270](), [RRM-evaluation/analysis/get_dpo_ref_free_results.py:1-244](), [RRM-evaluation/analysis/get_subtoken_statistics.py:1-164]()

## Benchmark Results Generation

The `get_benchmark_results.py` script serves as the primary tool for generating comprehensive benchmark reports from evaluation results stored in HuggingFace repositories.

### Core Functionality

```mermaid
graph TD
    subgraph "get_benchmark_results.py"
        Main[main]
        GetArgs[get_args]
        GetAverage[get_average_over_rewardbench]
        MultiplyByCols[_multiply_numbered_cols_by]
        PrettifyName[_prettify_model_name]
    end
    
    subgraph "External Dependencies"
        SnapshotDownload[snapshot_download]
        LoadResults[load_results]
        SubsetMapping[SUBSET_MAPPING]
        ExampleCounts[EXAMPLE_COUNTS]
    end
    
    subgraph "Output Processing"
        ToLatex[to_latex]
        ToMarkdown[to_markdown]
        ToCsv[to_csv]
    end
    
    Main --> GetArgs
    Main --> SnapshotDownload
    Main --> LoadResults
    Main --> GetAverage
    
    GetAverage --> SubsetMapping
    GetAverage --> ExampleCounts
    GetAverage --> MultiplyByCols
    
    Main --> PrettifyName
    Main --> ToLatex
    Main --> ToMarkdown
    Main --> ToCsv
```

Sources: [RRM-evaluation/analysis/get_benchmark_results.py:145-270](), [RRM-evaluation/analysis/get_benchmark_results.py:90-142](), [RRM-evaluation/analysis/get_benchmark_results.py:36-81]()

### Key Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--hf_evals_repo` | `allenai/reward-bench-results` | HuggingFace repository containing evaluation results |
| `--output_dir` | None | Directory to save generated reports |
| `--render_latex` | False | Generate LaTeX tables instead of Markdown |
| `--ignore_columns` | None | Comma-separated column names to exclude |
| `--model_type` | None | Filter results by specific model type |
| `--print_all_results` | False | Include detailed results for all categories |
| `--ignore_closed_models` | False | Exclude closed-source models from results |

Sources: [RRM-evaluation/analysis/get_benchmark_results.py:36-81]()

### Weighted Average Computation

The system computes weighted averages across different evaluation subsets using the `get_average_over_rewardbench` function:

```mermaid
graph LR
    subgraph "Subset Processing"
        SubsetCols["subset_cols = [col for col in columns if col in sub_subsets]"]
        SubData["sub_data = new_df[subset_cols].values"]
        SubCounts["sub_counts = [EXAMPLE_COUNTS[s] for s in subset_cols]"]
        WeightedAvg["np.average(sub_data, axis=1, weights=sub_counts)"]
    end
    
    SubsetCols --> SubData
    SubData --> WeightedAvg
    SubCounts --> WeightedAvg
    
    subgraph "Final Average"
        PrefSets["Prior Sets (0.5 weight)"]
        FinalWeights["weights = [2, 2, 2, 2, 1]"]
        TotalAvg["np.ma.average(masked_data, axis=1, weights=weights)"]
    end
    
    WeightedAvg --> PrefSets
    PrefSets --> TotalAvg
    FinalWeights --> TotalAvg
```

Sources: [RRM-evaluation/analysis/get_benchmark_results.py:90-142]()

## DPO Reference-Free Analysis

The `get_dpo_ref_free_results.py` script provides specialized analysis for Direct Preference Optimization (DPO) models, comparing reference-free methods against standard DPO approaches.

### Analysis Pipeline

```mermaid
graph TD
    subgraph "Data Filtering"
        LoadData[load_results]
        FilterDPO["df_dpo = hf_evals_df[model_type == 'DPO']"]
        FilterRefFree["df_dpo_ref_free = hf_evals_df[model_type == 'DPO Ref. Free']"]
        DeduplicateRefFree[drop_duplicates]
        AlignModels["df_dpo = df_dpo[df_dpo['model'].isin(df_dpo_ref_free['model'])]"]
    end
    
    subgraph "Delta Computation"
        ScaleDPO["dpo_scaled = _multiply_numbered_cols_by(100, get_average_over_rewardbench(df_dpo))"]
        ScaleRefFree["ref_free_scaled = _multiply_numbered_cols_by(100, get_average_over_rewardbench(df_dpo_ref_free))"]
        ComputeDelta["ref_free_scaled[col] = ref_free_scaled[col] - dpo_scaled[col]"]
    end
    
    subgraph "Report Generation"
        RenameColumns["rename average to Delta"]
        AddScores["add Orig. Score and New Score columns"]
        FormatLatex["apply color formatting for LaTeX"]
    end
    
    LoadData --> FilterDPO
    LoadData --> FilterRefFree
    FilterRefFree --> DeduplicateRefFree
    FilterDPO --> AlignModels
    DeduplicateRefFree --> AlignModels
    
    AlignModels --> ScaleDPO
    AlignModels --> ScaleRefFree
    ScaleDPO --> ComputeDelta
    ScaleRefFree --> ComputeDelta
    
    ComputeDelta --> RenameColumns
    RenameColumns --> AddScores
    AddScores --> FormatLatex
```

Sources: [RRM-evaluation/analysis/get_dpo_ref_free_results.py:90-244](), [RRM-evaluation/analysis/get_dpo_ref_free_results.py:115-175]()

### LaTeX Color Formatting

The DPO analysis includes sophisticated LaTeX formatting with color-coded cells based on performance deltas:

| Value Range | Color Scheme | Purpose |
|-------------|--------------|---------|
| Positive values | `\cellcolor{blue!{intensity}}` | Performance improvements |
| Negative values | `\cellcolor{red!{intensity}}` | Performance degradations |
| NaN values | `\cellcolor{gray!20}` | Missing data |

Sources: [RRM-evaluation/analysis/get_dpo_ref_free_results.py:181-208]()

## Subtoken Statistics Generation

The `get_subtoken_statistics.py` script analyzes token-level characteristics of benchmark datasets using configurable tokenizers.

### Token Analysis Pipeline

```mermaid
graph TD
    subgraph "Dataset Processing"
        LoadDataset["load_dataset(dataset_name, split=split)"]
        FilterSubsets["subsets = {s: dataset.filter(lambda x: x['subset'] == s) for s in subset_names}"]
        TokenizeExample["_tokenize: convert_tokens_to_ids(tokenizer.tokenize(text))"]
    end
    
    subgraph "Statistics Computation"
        ComputeLens["chosen_lens = len(prompt_tokens) + len(chosen_tokens)"]
        ComputeUnique["chosen_unique_lens = len(set(prompt_tokens + chosen_tokens))"]
        ComputeStats["np.mean, np.max, np.min for all metrics"]
    end
    
    subgraph "Output Generation"
        CreateDataFrame["pd.DataFrame with all statistics"]
        RenderTable["to_latex or to_markdown"]
        SaveCSV["to_csv if output_dir specified"]
    end
    
    LoadDataset --> FilterSubsets
    FilterSubsets --> TokenizeExample
    TokenizeExample --> ComputeLens
    TokenizeExample --> ComputeUnique
    ComputeLens --> ComputeStats
    ComputeUnique --> ComputeStats
    ComputeStats --> CreateDataFrame
    CreateDataFrame --> RenderTable
    CreateDataFrame --> SaveCSV
```

Sources: [RRM-evaluation/analysis/get_subtoken_statistics.py:61-92](), [RRM-evaluation/analysis/get_subtoken_statistics.py:105-120](), [RRM-evaluation/analysis/get_subtoken_statistics.py:124-161]()

### Statistical Metrics

The subtoken analysis computes comprehensive statistics for both chosen and rejected responses:

| Metric Category | Computed Statistics |
|-----------------|-------------------|
| Token Lengths | Mean, Max, Min for chosen and rejected responses |
| Unique Tokens | Mean, Max, Min unique token counts |
| Combined Analysis | Prompt + response token statistics |

Sources: [RRM-evaluation/analysis/get_subtoken_statistics.py:106-142]()

## Output Format Management

All three analysis scripts support multiple output formats with consistent formatting conventions:

```mermaid
graph LR
    subgraph "Format Selection"
        LatexFlag["--render_latex flag"]
        MarkdownDefault["Default Markdown output"]
    end
    
    subgraph "LaTeX Processing"
        LatexTable["df.to_latex(index=False, float_format='%.1f')"]
        ColorFormatting["color_for_value function"]
        PrettifyNames["_prettify_model_name function"]
    end
    
    subgraph "Markdown Processing"
        MarkdownTable["df.to_markdown(index=False, tablefmt='github')"]
        CleanNaN["replace('NaN', '').replace('nan', '')"]
    end
    
    subgraph "CSV Export"
        CSVSave["df.to_csv(output_dir / filename, index=False)"]
    end
    
    LatexFlag --> LatexTable
    LatexTable --> ColorFormatting
    ColorFormatting --> PrettifyNames
    
    MarkdownDefault --> MarkdownTable
    MarkdownTable --> CleanNaN
    
    LatexTable --> CSVSave
    MarkdownTable --> CSVSave
```

Sources: [RRM-evaluation/analysis/get_benchmark_results.py:211-266](), [RRM-evaluation/analysis/get_dpo_ref_free_results.py:181-240](), [RRM-evaluation/analysis/get_subtoken_statistics.py:148-160]()

### Standard Data Cleaning

All scripts implement consistent data cleaning procedures:

- NaN value replacement with empty strings or dashes
- Numeric precision formatting (typically 1 decimal place)
- Column renaming using `SUBSET_NAME_TO_PAPER_READY` mappings
- Model name prettification for publication-ready output

Sources: [RRM-evaluation/analysis/get_benchmark_results.py:258-259](), [RRM-evaluation/analysis/get_dpo_ref_free_results.py:232-233](), [RRM-evaluation/analysis/get_subtoken_statistics.py:153-154]()

---

