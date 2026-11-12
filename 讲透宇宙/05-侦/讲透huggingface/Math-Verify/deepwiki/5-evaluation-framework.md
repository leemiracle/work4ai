<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Math-Verify · page 5 Evaluation Framework · fetched 2026-10-26 -->

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [evaluate_model.py](evaluate_model.py)
- [src/math_verify/few_shots.py](src/math_verify/few_shots.py)
- [src/math_verify/tasks.py](src/math_verify/tasks.py)

</details>



This section documents the evaluation framework provided by Math-Verify for assessing mathematical model outputs. The framework integrates with the LightEval evaluation system to provide standardized benchmarking across multiple mathematical datasets including GSM8K, MATH, AIME, and AMC competitions. For core mathematical verification functionality, see [Core Components](#3). For specific metrics and scoring mechanisms, see [Metrics and Evaluation](#3.3).

## System Architecture

The evaluation framework operates as a high-level orchestration layer that coordinates mathematical task execution, few-shot prompting, and result verification through the core Math-Verify components.

### Overall Evaluation System

```mermaid
graph TB
    subgraph "Evaluation Entry Points"
        CLI["evaluate_model.py<br/>Command-line interface"]
        Args["argparse.Namespace<br/>--task, --model, --use_chat_template"]
    end
    
    subgraph "LightEval Integration"
        Pipeline["lighteval.Pipeline<br/>Main evaluation orchestrator"]
        Tracker["EvaluationTracker<br/>Results management"]
        Config["TransformersModelConfig<br/>Model configuration"]
        Params["PipelineParameters<br/>Batch size, parallelism"]
    end
    
    subgraph "Task System"
        TaskTable["TASKS_TABLE<br/>Task registry"]
        TaskConfigs["LightevalTaskConfig<br/>Individual task settings"]
        Prompts["Prompt Functions<br/>Dataset-specific formatting"]
    end
    
    subgraph "Math-Verify Core"
        Metrics["math_metric<br/>Verification logic"]
        Extraction["ExtractionConfigs<br/>LaTeX, Expression parsing"]
        FewShots["Few-shot examples<br/>GSM8K_FEW_SHOTS, MATH_HARD_FEW_SHOTS"]
    end
    
    CLI --> Args
    Args --> Pipeline
    Pipeline --> Tracker
    Pipeline --> Config
    Pipeline --> Params
    Pipeline --> TaskTable
    
    TaskTable --> TaskConfigs
    TaskConfigs --> Prompts
    TaskConfigs --> Metrics
    TaskConfigs --> FewShots
    
    Metrics --> Extraction
```

Sources: [evaluate_model.py:1-71](), [src/math_verify/tasks.py:318-324]()

### Task Configuration System

The framework defines mathematical evaluation tasks through `LightevalTaskConfig` objects that specify dataset sources, prompt formatting, and verification metrics.

```mermaid
graph TB
    subgraph "Task Definitions"
        GSM8K["gsm8k_lighteval<br/>Grade school math"]
        MATH_HARD["math_hard_lighteval<br/>Competition problems"]
        MATH_500["math_500_lighteval<br/>Curated subset"]
        AIME24["aime24_lighteval<br/>2024 AIME problems"]
        AMC23["amc23_lighteval<br/>2023 AMC problems"]
    end
    
    subgraph "Configuration Components"
        HFRepo["hf_repo<br/>Dataset source"]
        PromptFunc["prompt_function<br/>Question formatting"]
        MetricFunc["metric<br/>Answer verification"]
        StopSeq["stop_sequence<br/>Generation boundaries"]
        ExtractConfig["extraction_target<br/>Parser configurations"]
    end
    
    subgraph "Extraction Strategies"
        LatexConfig["LatexExtractionConfig<br/>\\boxed{} patterns"]
        ExprConfig["ExprExtractionConfig<br/>Numeric expressions"]
        PriorityOrder["boxed_match_priority<br/>Pattern precedence"]
    end
    
    GSM8K --> HFRepo
    GSM8K --> PromptFunc
    GSM8K --> MetricFunc
    
    MATH_HARD --> HFRepo
    MATH_HARD --> PromptFunc
    MATH_HARD --> MetricFunc
    
    PromptFunc --> StopSeq
    MetricFunc --> ExtractConfig
    ExtractConfig --> LatexConfig
    ExtractConfig --> ExprConfig
    ExtractConfig --> PriorityOrder
```

Sources: [src/math_verify/tasks.py:167-324]()

## Task Configurations

The framework supports multiple mathematical benchmarks with task-specific configurations for dataset access, prompt formatting, and answer extraction.

### Supported Mathematical Tasks

| Task | Dataset Source | Subsets | Gold Extraction | Prediction Extraction |
|------|----------------|---------|-----------------|----------------------|
| `gsm8k` | `openai/gsm8k` | main | `ExprExtractionConfig` | `LatexExtractionConfig`, `ExprExtractionConfig` |
| `math_hard` | `lighteval/MATH-Hard` | algebra, geometry, etc. | `LatexExtractionConfig` | `LatexExtractionConfig`, `ExprExtractionConfig` |
| `math_500` | `HuggingFaceH4/MATH-500` | default | `LatexExtractionConfig` | `LatexExtractionConfig`, `ExprExtractionConfig` |
| `aime24` | `zwhe99/aime24` | default | `LatexExtractionConfig` | `LatexExtractionConfig`, `ExprExtractionConfig` |
| `amc23` | `zwhe99/amc23` | default | `ExprExtractionConfig` | `LatexExtractionConfig`, `ExprExtractionConfig` |

Sources: [src/math_verify/tasks.py:167-324]()

### Prompt Function Architecture

Each task implements a specialized prompt function that formats questions and handles few-shot examples consistently.

```mermaid
graph LR
    subgraph "Prompt Function Flow"
        Input["Dataset sample<br/>{question, answer, ...}"]
        FewShotCheck["__few_shots check<br/>Training vs evaluation"]
        Format["Query formatting<br/>Question: X Step-by-Step Answer:"]
        DocCreation["Doc object<br/>query, choices, gold_index"]
    end
    
    subgraph "Task-Specific Functions"
        GSM8KPrompt["gsm8k_prompt_function<br/>Handles #### separator"]
        MathPrompt["math_prompt_function<br/>Direct problem/answer"]
        MathHardPrompt["math_hard_prompt_function<br/>problem/solution mapping"]
        AIMEPrompt["math_aime24_prompt_function<br/>reference_solution field"]
        AMCPrompt["math_amc23_prompt_function<br/>question/answer pairs"]
    end
    
    Input --> FewShotCheck
    FewShotCheck --> Format
    Format --> DocCreation
    
    GSM8KPrompt --> Format
    MathPrompt --> Format
    MathHardPrompt --> Format
```

Sources: [src/math_verify/tasks.py:43-164]()

## Few-Shot Prompting System

The framework provides curated few-shot examples to improve model performance through in-context learning.

### Few-Shot Example Structure

The system maintains separate few-shot collections for different mathematical domains:

- **GSM8K_FEW_SHOTS**: Grade school word problems with step-by-step arithmetic solutions
- **MATH_HARD_FEW_SHOTS**: Competition-level problems requiring advanced mathematical reasoning

```mermaid
graph TB
    subgraph "GSM8K Examples"
        GSM8K1["Janet's ducks<br/>Basic arithmetic"]
        GSM8K2["Contractor profit<br/>Multi-step calculation"]
        GSM8K3["Marble counting<br/>Proportional reasoning"]
        GSM8K4["Cookie baking<br/>Unit conversion"]
    end
    
    subgraph "MATH_HARD Examples"
        MATH1["Domain finding<br/>sqrt(x-2)/sqrt(5-x)"]
        MATH2["Matrix determinants<br/>det(AB) = det(A)det(B)"]
        MATH3["Weight lifting<br/>Algebraic equation"]
        MATH4["System of equations<br/>Linear algebra"]
    end
    
    subgraph "Example Structure"
        Question["question field<br/>Problem statement"]
        Answer["answer field<br/>Complete solution with reasoning"]
        Format["Consistent format<br/>'The final answer is X. I hope it is correct.'"]
    end
    
    GSM8K1 --> Question
    MATH1 --> Question
    Question --> Answer
    Answer --> Format
```

Sources: [src/math_verify/few_shots.py:1-69]()

### Few-Shot Selection Logic

The framework implements dynamic few-shot selection based on sample indices during evaluation.

```python
# Example from math_hard_prompt_function
if x.get("__few_shots"):
    index = x["__index"]
    few_shot_doc = (
        MATH_HARD_FEW_SHOTS[index]
        if index < len(MATH_HARD_FEW_SHOTS)
        else MATH_HARD_FEW_SHOTS[-1]
    )
```

Sources: [src/math_verify/tasks.py:44-50]()

## Metric Integration

The evaluation framework bridges LightEval's metric system with Math-Verify's mathematical verification capabilities through the `as_lighteval_metric` adapter function.

### Metric Adapter Architecture

```mermaid
graph TB
    subgraph "LightEval Interface"
        SampleMetric["SampleLevelMetric<br/>LightEval metric type"]
        MetricCategory["MetricCategory.GENERATIVE<br/>Classification"]
        MetricUseCase["MetricUseCase.ACCURACY<br/>Purpose"]
        CorpusLevel["np.mean<br/>Aggregation function"]
    end
    
    subgraph "Math-Verify Bridge"
        Adapter["as_lighteval_metric<br/>Function wrapper"]
        SampleFn["sample_level_fn<br/>Per-sample evaluation"]
        ExtractionStore["formatted_doc.specific<br/>Extracted predictions storage"]
    end
    
    subgraph "Core Verification"
        MathMetric["math_metric<br/>Mathematical comparison"]
        GoldExtraction["gold_extraction_target<br/>Ground truth parsing"]
        PredExtraction["pred_extraction_target<br/>Model output parsing"]
        Result["Float accuracy + extractions<br/>Return tuple"]
    end
    
    Adapter --> SampleMetric
    SampleMetric --> MetricCategory
    SampleMetric --> MetricUseCase
    SampleMetric --> CorpusLevel
    
    SampleFn --> MathMetric
    MathMetric --> GoldExtraction
    MathMetric --> PredExtraction
    MathMetric --> Result
    Result --> ExtractionStore
```

Sources: [src/math_verify/tasks.py:18-40]()

## Evaluation Pipeline Execution

The main evaluation script coordinates the entire evaluation process through LightEval's pipeline system.

### Command-Line Interface

The `evaluate_model.py` script provides a streamlined interface for model evaluation:

```bash
python evaluate_model.py --task gsm8k --model microsoft/Phi-3-mini-4k-instruct --use_chat_template
```

### Pipeline Configuration

The evaluation pipeline configures multiple components for robust execution:

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| `EvaluationTracker` | `output_dir="./results"`, `save_details=True` | Results storage and management |
| `PipelineParameters` | `launcher_type=ACCELERATE`, `max_samples=1000` | Parallelism and sampling control |
| `TransformersModelConfig` | `dtype="bfloat16"`, `use_chat_template` | Model loading configuration |
| `Pipeline` | `tasks="lighteval\|task\|4\|1"` | Task specification and few-shot count |

Sources: [evaluate_model.py:35-68]()

### Execution Flow

```mermaid
graph TD
    subgraph "Initialization"
        Args["parse_args()<br/>Command-line parsing"]
        Tracker["EvaluationTracker<br/>./results output"]
        PipeParams["PipelineParameters<br/>ACCELERATE launcher"]
        ModelConfig["TransformersModelConfig<br/>Model setup"]
    end
    
    subgraph "Pipeline Execution"
        Pipeline["Pipeline object<br/>Task + Config + Tracker"]
        Evaluate["pipeline.evaluate()<br/>Run evaluation"]
        Results["pipeline.show_results()<br/>Display metrics"]
        Save["pipeline.save_and_push_results()<br/>Persist outputs"]
    end
    
    subgraph "Task Resolution"
        TaskString["f'lighteval|{args.task}|4|1'<br/>Format specification"]
        TaskLookup["custom_tasks_directory<br/>'math_verify.tasks'"]
        TaskExecution["Selected LightevalTaskConfig<br/>From TASKS_TABLE"]
    end
    
    Args --> Tracker
    Args --> PipeParams
    Args --> ModelConfig
    
    Tracker --> Pipeline
    PipeParams --> Pipeline
    ModelConfig --> Pipeline
    
    Pipeline --> TaskString
    TaskString --> TaskLookup
    TaskLookup --> TaskExecution
    TaskExecution --> Evaluate
    
    Evaluate --> Results
    Results --> Save
```

Sources: [evaluate_model.py:16-71]()

## Integration Points

The evaluation framework integrates with several external systems and internal components to provide comprehensive mathematical model assessment.

### External Dependencies

- **LightEval Framework**: Provides the core evaluation infrastructure, parallelism management, and result tracking
- **HuggingFace Datasets**: Sources mathematical benchmarks through standardized dataset interfaces
- **Accelerate**: Enables distributed evaluation across multiple GPUs when available

### Internal Component Integration

- **Math-Verify Parser**: Extracts mathematical expressions from model outputs using configurable strategies
- **Math-Verify Grader**: Performs mathematical equivalence checking between predictions and ground truth
- **Timeout System**: Protects against infinite loops during complex mathematical parsing operations

Sources: [evaluate_model.py:1-14](), [src/math_verify/tasks.py:1-13]()

---

