<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/evaluation-guidebook · page 3 Foundational Knowledge · fetched 2026-10-26 -->

# Foundational Knowledge

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This section provides essential background on LLM mechanics that underpins all evaluation approaches. Understanding how models process text, generate predictions, and produce outputs is critical for designing effective evaluations, interpreting results, and troubleshooting issues.

The foundational concepts covered here apply equally to:
- **Automated Benchmarks** (Section 2.1): Understanding tokenization helps explain why prompts must be carefully designed and why small format changes can affect scores
- **Human Evaluation** (Section 2.2): Knowing how models generate text helps annotators understand what they're evaluating
- **LLM-as-a-Judge** (Section 2.3): Judge LLMs use the same inference mechanisms, which informs prompt design and bias mitigation

This overview introduces the core inference pipeline and evaluation modes. For detailed explanations, see:
- **Section 3.1 (Model Inference and Evaluation)**: Complete coverage of tokenization, prediction, evaluation paradigms, and output constraints
- **Section 3.2 (Tokenization)**: Deep dive into tokenization methods, vocabulary considerations, and multilingual challenges

## The LLM Inference Pipeline

Understanding how LLMs process and generate text is fundamental to evaluation design. The inference pipeline consists of three stages: tokenization, prediction, and decoding.

### Inference Pipeline Overview

```mermaid
flowchart TD
    Input["Input Text<br/>(Prompt)"]
    Tokenizer["Tokenization<br/>Text → Token IDs"]
    Model["LLM Forward Pass<br/>Token IDs → Logits"]
    Decode["Decoding Strategy<br/>Logits → Next Token"]
    Output["Output Token"]
    Complete{Complete?}
    
    Input --> Tokenizer
    Tokenizer --> Model
    Model --> Decode
    Decode --> Output
    Output --> Complete
    Complete -->|No| Tokenizer
    Complete -->|Yes| Final["Final Output<br/>(Detokenized Text)"]
    
    style Tokenizer fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Model fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Decode fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Sources: [contents/general-knowledge/model-inference-and-evaluation.md:1-16]()

### Why This Matters for Evaluation

Each stage of the pipeline introduces considerations for evaluation:

| Pipeline Stage | Evaluation Impact | Common Issues |
|----------------|------------------|---------------|
| **Tokenization** | Prompt format sensitivity, multilingual differences | Inconsistent space handling, numeric representation |
| **Prediction** | Score calibration, probability interpretation | Log-probability instability, length bias |
| **Decoding** | Output variance, reproducibility | Temperature effects, sampling randomness |

Understanding these stages helps explain phenomena like:
- Why adding a space changes model performance (tokenization differences)
- Why models prefer certain answer formats (prediction distribution bias)
- Why scores vary between runs (decoding randomness)

**For detailed coverage**, see Section 3.1 (Model Inference and Evaluation) and Section 3.2 (Tokenization).

Sources: [contents/general-knowledge/model-inference-and-evaluation.md:1-67](), [contents/general-knowledge/tokenization.md]()

## Two Evaluation Modes

Evaluation frameworks operate in two distinct modes, each leveraging different aspects of the inference pipeline.

### Evaluation Mode Comparison

```mermaid
flowchart TD
    Pipeline["LLM Inference Pipeline"]
    
    subgraph LogLik["Log-Likelihood Mode"]
        LL_Input["Prompt + All Choices"]
        LL_Forward["Forward Pass Only<br/>(No Decoding)"]
        LL_Logits["Extract Logits"]
        LL_Prob["Compute Probabilities"]
        LL_Select["Select Highest Probability"]
        
        LL_Input --> LL_Forward
        LL_Forward --> LL_Logits
        LL_Logits --> LL_Prob
        LL_Prob --> LL_Select
    end
    
    subgraph Gen["Generative Mode"]
        G_Input["Prompt Only"]
        G_Forward["Forward Pass"]
        G_Decode["Apply Decoding Strategy"]
        G_Gen["Generate Token"]
        G_Stop{Stop?}
        G_Output["Complete Output"]
        
        G_Input --> G_Forward
        G_Forward --> G_Decode
        G_Decode --> G_Gen
        G_Gen --> G_Stop
        G_Stop -->|No| G_Forward
        G_Stop -->|Yes| G_Output
    end
    
    Pipeline --> LogLik
    Pipeline --> Gen
```

Sources: [contents/general-knowledge/model-inference-and-evaluation.md:16-46]()

### Mode Characteristics

| Characteristic | Log-Likelihood | Generative |
|---------------|----------------|------------|
| **Speed** | Fast (single forward pass per choice) | Slower (multiple passes to generate) |
| **Determinism** | Deterministic | Varies with decoding strategy |
| **Use Cases** | Multiple choice, classification | Open-ended generation, reasoning |
| **Metrics** | Accuracy, perplexity | BLEU, exact match, human/LLM judgment |
| **Variance** | Low | High (especially with sampling) |

**When to use each mode:**
- **Log-likelihood**: Multiple-choice datasets (MMLU, ARC), classification tasks, fast screening
- **Generative**: Math problems (GSM8K), code generation (HumanEval), assistant evaluation (MT-Bench)

**For implementation details**, see Section 3.1 which covers request types, metric selection, and output constraints.

Sources: [contents/general-knowledge/model-inference-and-evaluation.md:16-67]()

## Mapping Concepts to Code

Understanding how foundational concepts map to evaluation framework code helps bridge theory and practice.

### Framework Architecture: lighteval Example

```mermaid
flowchart TD
    subgraph Config["Configuration Layer"]
        ModelCfg["BaseModelConfig<br/>VLLMModelConfig"]
        TaskCfg["LightevalTaskConfig"]
        PipelineCfg["PipelineParameters"]
    end
    
    subgraph Core["Core Pipeline"]
        Pipeline["Pipeline"]
        Tokenizer["Tokenization"]
        Inference["Model Inference"]
        Metrics["Metric Computation"]
    end
    
    subgraph Tasks["Task Definition"]
        PromptFunc["prompt_function()"]
        FewShot["few_shots_split<br/>few_shots_select"]
        RequestType["RequestType<br/>.LOGLIKELIHOOD<br/>.GREEDY_UNTIL"]
    end
    
    subgraph MetricImpl["Metric Implementations"]
        LogLikMetric["loglikelihood_acc_norm"]
        GenMetric["quasi_exact_match"]
        OtherMetrics["bleu<br/>rouge<br/>..."]
    end
    
    ModelCfg --> Pipeline
    TaskCfg --> Pipeline
    PipelineCfg --> Pipeline
    
    Pipeline --> Tokenizer
    Tokenizer --> Inference
    Inference --> Metrics
    
    TaskCfg --> PromptFunc
    TaskCfg --> FewShot
    TaskCfg --> RequestType
    
    RequestType -->|LOGLIKELIHOOD| LogLikMetric
    RequestType -->|GREEDY_UNTIL| GenMetric
    RequestType -->|GREEDY_UNTIL| OtherMetrics
    
    Metrics --> LogLikMetric
    Metrics --> GenMetric
    Metrics --> OtherMetrics
```

Sources: [contents/examples/comparing_task_formulations.ipynb:70-87](), [contents/examples/comparing_task_formulations.ipynb:132-151](), [contents/examples/comparing_task_formulations.ipynb:173-174]()

### Key Code Entities and Their Roles

| Code Entity | Role | Maps To Concept |
|-------------|------|-----------------|
| `BaseModelConfig` / `VLLMModelConfig` | Specifies model and inference parameters | Tokenization + Prediction stages |
| `LightevalTaskConfig` | Defines evaluation task structure | Evaluation mode selection |
| `RequestType.LOGLIKELIHOOD` | Signals log-probability evaluation | Log-likelihood mode |
| `RequestType.GREEDY_UNTIL` | Signals generative evaluation | Generative mode |
| `prompt_function()` | Formats input for model | Output constraint (prompt engineering) |
| `few_shots_split` / `few_shots_select` | Controls example selection | Output constraint (few-shot learning) |
| `loglikelihood_acc_norm` | Computes accuracy from probabilities | Log-likelihood metric |
| `quasi_exact_match` | Compares generated vs reference text | Generative metric |

### Example: Defining a Task

```python
# Maps foundational concepts to code
task_config = LightevalTaskConfig(
    name="my_task",
    prompt_function=my_prompt_fn,        # Output constraint: prompt design
    suite=["custom"],
    hf_repo="my_dataset",
    hf_subset="default",
    evaluation_splits=["test"],
    few_shots_split="train",             # Output constraint: few-shot examples
    few_shots_select="random",           
    metric=[Metrics.loglikelihood_acc_norm],  # Evaluation mode: log-likelihood
)
```

**This configuration connects:**
1. Prompt design (`prompt_function`) to output constraint methods
2. Few-shot learning (`few_shots_split`) to in-context learning
3. Metric selection (`Metrics.loglikelihood_acc_norm`) to evaluation mode (log-likelihood)

Sources: [contents/examples/comparing_task_formulations.ipynb:132-151](), [contents/examples/comparing_task_formulations.ipynb:173-174]()
</thinking>

### Code-Level Workflow

```mermaid
sequenceDiagram
    participant User
    participant Pipeline
    participant ModelConfig as BaseModelConfig
    participant TaskConfig as LightevalTaskConfig
    participant Tokenizer
    participant Model
    participant Metric
    
    User->>Pipeline: Initialize with configs
    User->>Pipeline: run()
    
    Pipeline->>TaskConfig: Get prompt_function()
    TaskConfig-->>Pipeline: Formatted prompt
    
    Pipeline->>ModelConfig: Get tokenizer
    ModelConfig-->>Pipeline: Tokenizer instance
    
    Pipeline->>Tokenizer: tokenize(prompt)
    Tokenizer-->>Pipeline: token_ids
    
    Pipeline->>Model: forward(token_ids)
    Model-->>Pipeline: logits
    
    alt RequestType.LOGLIKELIHOOD
        Pipeline->>Metric: loglikelihood_acc_norm(logits, choices)
        Metric-->>Pipeline: accuracy score
    else RequestType.GREEDY_UNTIL
        Pipeline->>Model: generate(token_ids)
        Model-->>Pipeline: generated_text
        Pipeline->>Metric: quasi_exact_match(generated, reference)
        Metric-->>Pipeline: match score
    end
    
    Pipeline-->>User: Results
```

Sources: [contents/examples/comparing_task_formulations.ipynb:460-477](), [contents/examples/comparing_task_formulations.ipynb:541-583]()

## Practical Implications for Evaluation Design

Foundational knowledge directly informs evaluation design decisions across all methodologies.

### Design Decision Framework

```mermaid
flowchart TD
    Question{Evaluation Design Question}
    
    Question --> Q1{What format should<br/>my prompt use?}
    Question --> Q2{Which evaluation<br/>mode should I use?}
    Question --> Q3{Why are my scores<br/>varying?}
    
    Q1 --> A1["Consider tokenization:<br/>- Space handling<br/>- Special tokens<br/>- Format sensitivity"]
    
    Q2 --> A2["Consider task type:<br/>- Multiple choice → Log-likelihood<br/>- Open generation → Generative<br/>- Speed vs flexibility"]
    
    Q3 --> A3["Consider pipeline stages:<br/>- Tokenization differences<br/>- Decoding randomness<br/>- Temperature settings"]
    
    A1 --> Next["See Section 3.2:<br/>Tokenization Details"]
    A2 --> Next2["See Section 3.1:<br/>Evaluation Modes"]
    A3 --> Next3["See Section 4:<br/>Troubleshooting"]
```

Sources: [contents/general-knowledge/model-inference-and-evaluation.md:1-67](), [contents/troubleshooting/troubleshooting-reproducibility.md]()

### Common Evaluation Scenarios

| Scenario | Relevant Concept | Guideline |
|----------|-----------------|-----------|
| Designing prompts for MMLU | Tokenization sensitivity | Test with/without spaces; check special tokens |
| Comparing models on math tasks | Generative mode + output parsing | Use structured generation or robust parsers |
| Creating a new benchmark | Evaluation mode selection | Log-likelihood for speed; generative for realism |
| Debugging score variance | Decoding strategy | Fix temperature=0 for deterministic results |
| Evaluating multilingual models | Tokenization differences | Check vocabulary coverage per language |
| Building LLM-as-judge | All concepts | Judge uses same inference; understand biases |

**These scenarios are covered in depth in:**
- **Section 2.1 (Automated Benchmarks)**: Prompt design, dataset selection
- **Section 2.3 (LLM-as-a-Judge)**: Judge prompt engineering, bias mitigation
- **Section 4 (Troubleshooting)**: Inference issues, reproducibility problems

Sources: [contents/automated-benchmarks/designing-your-automatic-evaluation.md](), [contents/model-as-a-judge/designing-your-evaluation-prompt.md](), [contents/troubleshooting/troubleshooting-inference.md]()

## Relationship to Main Evaluation Approaches

These general knowledge concepts form the foundation for the three main evaluation approaches covered in this guidebook:

```mermaid
graph TD
    A["General Knowledge"] --> B["Tokenization"]
    A --> C["Prediction Process"]
    A --> D["Evaluation Paradigms"]
    A --> E["Output Constraints"]
    
    B & C & D & E --> F["Automated Benchmarks"]
    B & C & D & E --> G["Human Evaluation"]
    B & C & D & E --> H["LLM-as-a-Judge"]
    
    subgraph "Evaluation Implementation Tools"
        I["lighteval"]
        J["lm_eval Harness"]
        K["Argilla"]
        L["distilabel"]
    end
    
    F -.-> I & J
    G -.-> K
    H -.-> L
```

Sources: README.md:9-11, README.md:17-49

Understanding these core concepts enables more effective implementation of specific evaluation approaches and better interpretation of evaluation results across all methodologies.

---

