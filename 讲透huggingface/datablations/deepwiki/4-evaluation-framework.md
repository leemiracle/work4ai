<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/datablations · page 4 Evaluation Framework · fetched 2026-10-26 -->

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [plotstables/training_validation_filter.pdf](plotstables/training_validation_filter.pdf)
- [plotstables/validation_c4py.pdf](plotstables/validation_c4py.pdf)

</details>



The Evaluation Framework in the datablations repository provides structured methods for assessing language model performance on downstream tasks. This framework utilizes the lm-evaluation-harness to evaluate models across three distinct evaluation types: rank-based, generative, and bAbI tasks. This page explains the overall evaluation process, how to execute evaluations, and how results are processed for further analysis.

For information about model training that precedes evaluation, see [Model Training](#3).

## Evaluation Workflow Overview

The evaluation process follows a systematic workflow, transforming trained model checkpoints into a format suitable for evaluation, running the evaluation tasks, and processing the results for analysis.

```mermaid
flowchart TD
    subgraph "Checkpoint Preparation"
        A["Megatron-DeepSpeed Checkpoint"] -->|"deepspeed_to_transformers.py"| B["Transformers Format Checkpoint"]
    end
    
    subgraph "Evaluation Process"
        B --> C["lm-evaluation-harness"]
        C --> D1["Rank Evaluation"]
        C --> D2["Generative Evaluation"]
        C --> D3["bAbI Evaluation"]
    end
    
    subgraph "Results Processing"
        D1 -->|"report-to-csv.py"| E1["Rank Results CSV"]
        D2 -->|"merge_generative.py"| E2["Merged Generation Files"]
        E2 -->|"csv_generative.py"| E3["Generative Results CSV"]
        D3 --> E4["bAbI Results CSV"]
    end
    
    subgraph "Analysis"
        E1 --> F["Performance Analysis"]
        E3 --> F
        E4 --> F
    end
```

Sources: [README.md:379-394]()

## Checkpoint Conversion

Before evaluation can begin, model checkpoints from Megatron-DeepSpeed must be converted to the Hugging Face Transformers format.

```mermaid
flowchart LR
    A["Megatron-DeepSpeed Checkpoint"] -->|"Model Conversion"| B["Transformers Format"]
    
    subgraph "Conversion Process"
        C["deepspeed_to_transformers.py"] -->|"Extracts weights"| D["Model architecture files"]
        C -->|"Generates"| E["Tokenizer configuration"]
        C -->|"Creates"| F["Model configuration"]
    end
    
    A --> C
```

The conversion process uses the `deepspeed_to_transformers.py` script, which transforms the distributed model checkpoint into a format compatible with the Hugging Face Transformers library.

Example conversion command:
```
python Megatron-DeepSpeed/tools/convert_checkpoint/deepspeed_to_transformers.py --input_folder global_step52452 --output_folder transformers --target_tp 1 --target_pp 1
```

Sources: [README.md:286]()

## Evaluation Types

The framework supports three distinct types of evaluation, each targeting different aspects of language model capabilities.

### Rank Evaluation

Rank evaluation assesses the model's ability to predict correct answers by ranking possible answer choices. This is particularly useful for multiple-choice tasks and knowledge-based evaluations.

#### Process

```mermaid
flowchart LR
    A["Transformers Model"] --> B["lm-evaluation-harness"]
    B --> C["Execute Tasks"]
    C --> D["Calculate Probabilities"]
    D --> E["Rank Answer Choices"]
    E --> F["Compute Accuracy"]
    F --> G["Generate JSON Report"]
    G -->|"report-to-csv.py"| H["Convert to CSV"]
```

#### Implementation

To run rank evaluation:
1. Install the evaluation harness: `pip install git+https://github.com/EleutherAI/lm-evaluation-harness.git`
2. Execute the evaluation script: `sbatch utils/eval_rank.sh`
3. Convert results to CSV: `python Megatron-DeepSpeed/tasks/eval_harness/report-to-csv.py outfile.json`

Sources: [README.md:375-380]()

### Generative Evaluation

Generative evaluation measures the model's text generation capabilities using metrics like ROUGE. This approach is suitable for summarization, translation, and open-ended generative tasks.

#### Process

```mermaid
flowchart LR
    A["Transformers Model"] --> B["lm-evaluation-harness (addtasks branch)"]
    B --> C["Generate Text Responses"]
    C --> D["Compute ROUGE Scores"]
    D --> E["Store Results"]
    E -->|"merge_generative.py"| F["Merge Generation Files"]
    F -->|"csv_generative.py"| G["Create CSV Report"]
```

#### Implementation

To run generative evaluation:
1. Clone the specialized branch: `git clone -b addtasks https://github.com/Muennighoff/lm-evaluation-harness.git`
2. Install dependencies: `pip install -e ".[dev]"; pip uninstall -y promptsource; pip install git+https://github.com/Muennighoff/promptsource.git@tr13`
3. Execute the evaluation script: `sbatch utils/eval_generative.sh`
4. Merge and convert results: 
   ```
   python utils/merge_generative.py
   python utils/csv_generative.py merged.json
   ```

Sources: [README.md:382-387]()

### bAbI Evaluation

bAbI evaluation tests a model's reasoning capabilities using the bAbI dataset, measuring exact match accuracy in answering questions that require logical reasoning.

#### Process

```mermaid
flowchart LR
    A["Transformers Model"] --> B["lm-evaluation-harness (babi branch)"]
    B --> C["Process bAbI Tasks"]
    C --> D["Evaluate Reasoning"]
    D --> E["Compute Exact Match"]
    E --> F["Generate Results CSV"]
```

#### Implementation

To run bAbI evaluation:
1. Clone the specialized branch: `git clone -b babi https://github.com/Muennighoff/lm-evaluation-harness.git`
2. Install dependencies: `pip install -e ".[dev]"`
3. Ensure model checkpoint includes tokenizer files
4. Execute the evaluation script: `sbatch utils/eval_babi.sh`

Sources: [README.md:390-394]()

## Evaluation Framework Components

The following diagram illustrates the relationship between the evaluation components and the corresponding code files:

```mermaid
graph TD
    subgraph "Evaluation Framework"
        A["lm-evaluation-harness"] --- B["eval_rank.sh"]
        A --- C["eval_generative.sh"]
        A --- D["eval_babi.sh"]
    end
    
    subgraph "Results Processing"
        E["report-to-csv.py"] --- B
        F["merge_generative.py"] --- C
        G["csv_generative.py"] --- F
    end
    
    subgraph "Model Preparation"
        H["deepspeed_to_transformers.py"] --> A
    end
    
    I["Trained Model Checkpoint"] --> H
    A --> J["Evaluation Results"]
    J --> K["CSV Reports"]
    K --> L["Analysis & Visualization"]
```

Sources: [README.md:375-394]()

## Evaluation Metrics and Tasks

The different evaluation types focus on specific metrics relevant to their task categories:

| Evaluation Type | Primary Metrics | Example Tasks |
|----------------|-----------------|---------------|
| Rank Evaluation | Accuracy, Exact Match | MMLU, HellaSwag, Winogrande |
| Generative Evaluation | ROUGE-1, ROUGE-2, ROUGE-L | CNN/DailyMail, XSum, WebNLG |
| bAbI Evaluation | Exact Match | Logical reasoning, Inference, Deduction |

Sources: [README.md:375-394]()

## Results Processing

After evaluation, the raw results are transformed into standardized CSV formats for further analysis:

```mermaid
flowchart TD
    A["Raw Evaluation Results"] --> B{"Evaluation Type"}
    B -->|"Rank"| C["report-to-csv.py"]
    B -->|"Generative"| D["merge_generative.py"]
    D --> E["csv_generative.py"]
    B -->|"bAbI"| F["Direct CSV Output"]
    
    C --> G["CSV Reports"]
    E --> G
    F --> G
    
    G --> H["Performance Analysis"]
    H --> I["Parametric Fitting"]
    H --> J["Scaling Law Analysis"]
```

The CSV reports enable consistent analysis across different experiment types and allow for visualization of performance patterns across model sizes and training data configurations.

Sources: [README.md:375-394]()

## Integration with the Analysis Pipeline

The evaluation results feed directly into the analysis pipeline, which fits parametric scaling laws and visualizes performance trends:

```mermaid
flowchart LR
    A["Evaluation Results"] --> B["CSV Reports"]
    B --> C["Analysis Scripts"]
    
    subgraph "Analysis Pipeline"
        C --> D["parametric_fit.ipynb"]
        C --> E["Visualization Scripts"]
        D --> F["Scaling Law Parameters"]
        F --> G["Performance Predictions"]
        E --> H["Performance Visualizations"]
    end
```

For more information on the analysis of evaluation results, see [Scaling Laws and Analysis](#5).

Sources: [README.md:396-439]()

---

