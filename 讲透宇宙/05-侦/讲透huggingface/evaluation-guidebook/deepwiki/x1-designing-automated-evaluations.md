<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/evaluation-guidebook · extra page Designing Automated Evaluations · fetched 2026-10-26 -->

# Designing Automated Evaluations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [contents/automated-benchmarks/designing-your-automatic-evaluation.md](contents/automated-benchmarks/designing-your-automatic-evaluation.md)

</details>



## Purpose and Scope

This page provides a systematic guide for designing robust automated evaluations of language models. It covers the four critical decision points in the evaluation design process: dataset selection, inference method, prompt engineering, and metric selection. The page also introduces functional testing as an emerging paradigm for creating contamination-resistant evaluations.

**Related pages:**
- For a catalog of existing evaluation datasets, see [Evaluation Datasets Catalog](#2.1.2)
- For foundational understanding of inference mechanics, see [Model Inference and Evaluation](#3.1)
- For troubleshooting common issues, see [Tips and Tricks](#2.1.3)
- For understanding metric behavior across evaluations, see [Troubleshooting](#4)

---

## The Evaluation Design Process

Automated evaluation design consists of four sequential decisions, each constraining and informing the next. The quality of your evaluation is fundamentally bounded by the quality of your dataset—no sophisticated metric or prompt engineering can compensate for poorly constructed evaluation samples.

```mermaid
graph TD
    START["Start Evaluation Design"] --> DATASET["Decision 1:<br/>Dataset Selection"]
    
    DATASET --> DATASET_EXIST["Use Existing Dataset"]
    DATASET --> DATASET_NEW["Create New Dataset"]
    
    DATASET_EXIST --> INSPECT["Manual Inspection<br/>(50 random samples)"]
    DATASET_NEW --> CREATE_METHOD["Creation Method"]
    
    CREATE_METHOD --> AGG["Aggregate Existing Data"]
    CREATE_METHOD --> HUMAN["Human Annotators"]
    CREATE_METHOD --> SYNTH["Synthetic/Rule-Based"]
    
    INSPECT --> INFERENCE["Decision 2:<br/>Inference Method"]
    AGG --> INFERENCE
    HUMAN --> INFERENCE
    SYNTH --> INFERENCE
    
    INFERENCE --> LOGPROB["Log-Probability<br/>(MCQA)"]
    INFERENCE --> GEN["Generative<br/>(QA)"]
    
    LOGPROB --> PROMPT["Decision 3:<br/>Prompt Design"]
    GEN --> PROMPT
    
    PROMPT --> TASK_PROMPT["Task description"]
    PROMPT --> CONTEXT["Context"]
    PROMPT --> QUESTION["Question"]
    PROMPT --> OPTIONS["Options (MCQA)"]
    PROMPT --> FEWSHOT["Few-shot examples"]
    
    TASK_PROMPT --> METRIC["Decision 4:<br/>Metric Selection"]
    CONTEXT --> METRIC
    QUESTION --> METRIC
    OPTIONS --> METRIC
    FEWSHOT --> METRIC
    
    METRIC --> LOGPROB_METRICS["accuracy, perplexity,<br/>f1 (normalized)"]
    METRIC --> GEN_METRICS["exact_match, prefix_match,<br/>ROUGE, BLEU"]
    METRIC --> FUNC_METRICS["functional_tests<br/>(unit tests, parsers)"]
    
    LOGPROB_METRICS --> END["Run Evaluation"]
    GEN_METRICS --> END
    FUNC_METRICS --> END
```

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:1-118]()

---

## Dataset Selection

The dataset selection process differs significantly depending on whether you use an existing dataset or create a new one. Both approaches require rigorous quality validation.

### Evaluating Existing Datasets

When selecting an existing dataset, evaluate it across three dimensions: creation process, sample quality, and statistical adequacy.

#### Creation Process Assessment

```mermaid
graph TD
    EVAL["Evaluate Dataset"] --> CREATOR["Who created samples?"]
    EVAL --> REVIEW["Quality review process?"]
    EVAL --> GUIDELINES["Creation guidelines?"]
    
    CREATOR --> C1["Expert created<br/>(highest quality)"]
    CREATOR --> C2["Paid annotators<br/>(moderate quality)"]
    CREATOR --> C3["Crowdsourced<br/>(moderate quality)"]
    CREATOR --> C4["MTurked<br/>(variable quality)"]
    
    REVIEW --> R1["Inter-annotator agreement<br/>(annotators agree?)"]
    REVIEW --> R2["Author examination<br/>(full dataset reviewed?)"]
    
    GUIDELINES --> G1["Clear guidelines provided"]
    GUIDELINES --> G2["Inconsistent or missing"]
    
    C1 --> QUALITY["Quality Score"]
    C2 --> QUALITY
    C3 --> QUALITY
    C4 --> QUALITY
    R1 --> QUALITY
    R2 --> QUALITY
    G1 --> QUALITY
    G2 --> QUALITY
    
    QUALITY --> DATACARD["Check data card for<br/>annotator demographics"]
```

The creation process hierarchy matters because it directly impacts dataset consistency and language diversity. Expert-created datasets generally exhibit higher quality than crowdsourced alternatives, particularly for complex reasoning tasks.

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:8-21]()

#### Sample Quality Checklist

Manually inspect 50 random samples against this checklist:

| Quality Dimension | Evaluation Criteria | Example Issues |
|-------------------|---------------------|----------------|
| **Prompt Clarity** | Are prompts unambiguous and well-specified? | Vague questions requiring unstated assumptions |
| **Answer Correctness** | Are provided answers actually correct? | TriviaQA contains conflicting aliases in gold answers |
| **Information Completeness** | Is all necessary information present? | MMLU misses reference schematics in some questions |
| **Task Relevance** | Do questions match your evaluation goals? | Domain mismatch with target use case |
| **Use Case Alignment** | Are examples relevant to your application? | General knowledge when you need domain expertise |

**Minimum sample requirement:** 100 samples for statistically significant results in automatic benchmarks.

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:22-32]()

### Creating New Datasets

Three approaches exist for creating custom evaluation datasets, each with distinct trade-offs:

```mermaid
graph LR
    subgraph "Approach 1: Aggregation"
        A1["Aggregate existing<br/>human eval datasets"] --> A2["Examples: MATH, LSAT"]
        A2 --> A3["Follow existing<br/>dataset criteria"]
    end
    
    subgraph "Approach 2: Human Annotation"
        H1["Design annotation<br/>guidelines"] --> H2["Select annotators"]
        H2 --> H3["Iterative refinement"]
        H3 --> H4["Quality control"]
        H4 --> H5["See page 2.2.1"]
    end
    
    subgraph "Approach 3: Synthetic"
        S1["LLM Generation"] --> S1A["Example: Cosmopedia"]
        S1 --> S1B["Requires manual filtering"]
        
        S2["Rule-Based"] --> S2A["Infinite sample supply"]
        S2 --> S2B["Contamination resistant"]
        S2 --> S2C["Examples: NPHardEval,<br/>DyVal, MuSR, BabiQA"]
    end
```

**Rule-based generation** is particularly valuable for contamination avoidance. By algorithmically generating test cases, you create samples that cannot have appeared in training data. This approach works well for tasks with formal structure (graph algorithms, mathematical problems, logical reasoning).

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:33-46]()

---

## Inference Method Selection

The inference method determines how you extract model predictions and fundamentally shapes which models will perform well on your evaluation.

### Log-Probability (MCQA) vs Generative (QA)

```mermaid
graph TD
    TASK["Evaluation Task"] --> DECIDE{"What are you<br/>testing?"}
    
    DECIDE -->|Knowledge, disambiguation| MCQA["Log-Probability (MCQA)"]
    DECIDE -->|Fluency, reasoning, generation| GEN["Generative (QA)"]
    
    MCQA --> MCQA_PROCESS["Process:<br/>1. Present options A/B/C/D<br/>2. Compute log P(option|prompt)<br/>3. Select highest probability"]
    
    GEN --> GEN_PROCESS["Process:<br/>1. Generate free-form text<br/>2. Extract answer from generation<br/>3. Compare to reference"]
    
    MCQA_PROCESS --> MCQA_PROS["Pros:<br/>- All models see correct answer<br/>- Fast evaluation (1 token)<br/>- Confidence proxy<br/>- Signal on small models"]
    
    MCQA_PROCESS --> MCQA_CONS["Cons:<br/>- Over-scores small models<br/>- Choice order bias<br/>- Not representative of<br/>  actual use"]
    
    GEN_PROCESS --> GEN_PROS["Pros:<br/>- Tests actual generation<br/>- Matches real usage<br/>- Tests fluency/reasoning"]
    
    GEN_PROCESS --> GEN_CONS["Cons:<br/>- Harder to score<br/>- More expensive<br/>- Requires sampling"]
```

### Trade-offs Table

| Aspect | Log-Probability (MCQA) | Generative (QA) |
|--------|------------------------|-----------------|
| **Speed** | Fast (single token prediction) | Slower (full generation) |
| **Model Coverage** | Works well on small models | Requires capable models for generation |
| **Real-world Validity** | Limited (forced choice) | High (actual use case) |
| **Scoring Complexity** | Simple (argmax probability) | Complex (matching, normalization) |
| **Confidence Signal** | Direct (probability values) | Indirect (must be engineered) |
| **Known Biases** | Choice order effects | Verbosity, format sensitivity |

**Critical consideration:** Some models exhibit choice order bias, favoring specific options (e.g., always preferring option A) regardless of content. This is documented in [arXiv:2309.03882]().

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:48-66]()

---

## Prompt Engineering

Prompt design significantly impacts evaluation results. Semantically equivalent prompts can yield substantially different scores, and models increasingly overfit specific prompt formats.

### Prompt Component Architecture

```mermaid
graph TB
    PROMPT["Complete Prompt"] --> COMP1["Task Description<br/>(optional)"]
    PROMPT --> COMP2["Context<br/>(if needed)"]
    PROMPT --> COMP3["Question<br/>(core prompt)"]
    PROMPT --> COMP4["Options<br/>(MCQA only)"]
    PROMPT --> COMP5["Few-shot Examples<br/>(optional)"]
    PROMPT --> COMP6["Connector Words<br/>('Question:', 'Context:', etc)"]
    
    COMP1 --> EX1["'You are evaluating<br/>mathematical reasoning'"]
    COMP2 --> EX2["Summarization: source document<br/>Extraction: content to analyze"]
    COMP3 --> EX3["'What is the result of 2+2?'"]
    COMP4 --> EX4["A) 3<br/>B) 4<br/>C) 5<br/>D) 6"]
    COMP5 --> EX5["Example Q: ...<br/>Example A: ..."]
    COMP6 --> EX6["Structural markers<br/>for clarity"]
```

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:68-79]()

### Prompt Sensitivity Issues

Three critical challenges affect prompt reliability:

| Issue | Description | Mitigation Strategy |
|-------|-------------|---------------------|
| **Semantic Variance** | Small prompt changes cause large score differences | Run evaluation with multiple prompt variations allocated to equivalent difficulty samples |
| **Format Overfitting** | Models overfit test set formats during training | Use format-diverse prompts; newer models (Llama 3.2, Qwen 2.5) ignore few-shot format cues |
| **Model-Specific Advantages** | Prompt format advantages specific models | Document prompt format in evaluation metadata; consider format ablations |

The format overfitting problem is documented in [arXiv:2407.07890](), which demonstrates that some models achieve inflated scores by memorizing evaluation formats rather than learning underlying capabilities. The Open LLM Leaderboard v2 team observed Llama 3.2 and Qwen 2.5 no longer following few-shot format patterns, suggesting format saturation in training data.

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:81-89]()

### Constrained Generation

For metrics requiring specific output formats, constrained generation techniques force models to produce parseable outputs. These techniques are detailed in the [Model Inference and Evaluation](#3.1) page, section "Constraining model outputs".

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:90-91]()

---

## Metric Selection

Metric selection depends entirely on your inference method. The critical principle: **match your metric to what your task actually measures**.

### Log-Probability Metrics

For log-probability evaluations, metrics are straightforward:

```mermaid
graph LR
    LOGPROB["Log-Probability<br/>Evaluation"] --> NORM["Normalize by length"]
    
    NORM --> CHAR["Character<br/>normalization"]
    NORM --> TOKEN["Token<br/>normalization"]
    NORM --> PMI["PMI normalization"]
    
    CHAR --> METRICS["Available Metrics"]
    TOKEN --> METRICS
    PMI --> METRICS
    
    METRICS --> ACC["Accuracy<br/>(most likely = best?)"]
    METRICS --> PERP["Perplexity<br/>(sequence likelihood)"]
    METRICS --> F1["F1 Score<br/>(precision + recall)"]
    METRICS --> REC["Recall"]
```

**Critical requirement:** Length normalization is essential. Without it, shorter completions systematically achieve higher log-probabilities, biasing results.

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:93-94]()

### Generative Metrics Pipeline

Generative evaluation requires a two-stage process: normalization and comparison.

```mermaid
graph TD
    GEN["Generated Output"] --> DECIDE1{"Normalization<br/>needed?"}
    
    DECIDE1 -->|Yes| NORM["Apply Normalization"]
    DECIDE1 -->|No| RAW["Use raw output"]
    
    NORM --> NORM_MATH["Math: Extract numerical result<br/>from formatted output"]
    NORM --> NORM_COT["Chain of Thought: Remove<br/>reasoning trace"]
    NORM --> NORM_FORMAT["Remove formatting artifacts"]
    
    NORM_MATH --> COMPARE["Comparison Method"]
    NORM_COT --> COMPARE
    NORM_FORMAT --> COMPARE
    RAW --> COMPARE
    
    COMPARE --> MATCH["Match-Based<br/>Metrics"]
    COMPARE --> SIM["Similarity<br/>Metrics"]
    
    MATCH --> M1["exact_match"]
    MATCH --> M2["prefix_match"]
    MATCH --> M3["quasi_exact_match"]
    
    SIM --> S1["ROUGE"]
    SIM --> S2["BLEU"]
    SIM --> S3["character n-gram"]
    
    M1 --> REF["Compare to<br/>Reference"]
    M2 --> REF
    M3 --> REF
    S1 --> REF
    S2 --> REF
    S3 --> REF
```

**Normalization considerations:**
- Normalizations can be unfair if poorly designed (see blog: ["Open LLM Leaderboard Drop"](https://huggingface.co/blog/open-llm-leaderboard-drop))
- They provide valuable task-level signal despite individual-sample artifacts
- Essential for math evaluations with formatted outputs
- Required when using Chain of Thought (CoT) to extract final answers from reasoning traces

**Metric catalog reference:** For a comprehensive list of implemented metrics, see the [lighteval Metric List](https://github.com/huggingface/lighteval/wiki/Metric-List).

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:96-103]()

### Task-Specific Metric Selection

The metric must align with what you're actually measuring. For some domains, average performance is insufficient—you must measure **worst-case performance**:

| Domain | What to Measure | Why |
|--------|-----------------|-----|
| **Medical** | Worst-case accuracy | Patient safety requires consistent correctness |
| **Public Chatbots** | Worst-case toxicity | Public exposure to harmful outputs |
| **Code Generation** | Worst-case security | Single vulnerability compromises system |
| **Knowledge QA** | Average accuracy | Aggregate capability matters |

This distinction is explored in depth in Ehud Reiter's blog: ["Challenges in Evaluating LLMs"](https://ehudreiter.com/2024/07/10/challenges-in-evaluating-llms).

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:105-106]()

---

## Functional Testing: The Emerging Paradigm

Functional testing evaluates models on what they **do** rather than what they **say**. Originating in code evaluation, this approach is expanding to structured text tasks.

### Core Concept

```mermaid
graph LR
    subgraph "Traditional Evaluation"
        T1["Model Output"] --> T2["String Comparison"]
        T2 --> T3["Match Score"]
    end
    
    subgraph "Functional Evaluation"
        F1["Model Output"] --> F2["Execute/Parse<br/>Output"]
        F2 --> F3["Test Against<br/>Specification"]
        F3 --> F4["Binary Pass/Fail"]
    end
    
    T3 --> TRAD_ISSUE["Issues:<br/>- Overfitting semantics<br/>- Memorization<br/>- Ambiguous correctness"]
    
    F4 --> FUNC_BENEFIT["Benefits:<br/>- Tests capability<br/>- Contamination resistant<br/>- Clear pass/fail"]
```

### Benefits of Functional Testing

| Benefit | Explanation | Impact |
|---------|-------------|--------|
| **Easier Test Generation** | Many domains allow rule-based test case generation | Reduced annotation cost |
| **Contamination Resistance** | Generated test cases cannot appear in training data | Addresses data leakage |
| **Capability Focus** | Tests specific active capabilities rather than memorization | More meaningful evaluation |
| **Creativity Requirement** | Requires domain expertise to design functional tests | Barrier to adoption |

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:107-117]()

### Functional Testing Examples

#### Code Evaluation: Unit Tests

The canonical functional testing domain. Models generate code to solve a problem, then that code executes against a test suite:

```mermaid
graph LR
    PROBLEM["Problem:<br/>'Write function to<br/>sort array'"] --> MODEL["Model<br/>Generates Code"]
    
    MODEL --> CODE["def sort_array(arr):<br/>  return sorted(arr)"]
    
    CODE --> TEST1["Test 1: [3,1,2] → [1,2,3]"]
    CODE --> TEST2["Test 2: [] → []"]
    CODE --> TEST3["Test 3: [1] → [1]"]
    CODE --> TEST4["Test 4: [5,5,5] → [5,5,5]"]
    
    TEST1 --> PASS1["✓ Pass"]
    TEST2 --> PASS2["✓ Pass"]
    TEST3 --> PASS3["✓ Pass"]
    TEST4 --> PASS4["✓ Pass"]
    
    PASS1 --> SCORE["Score: 4/4 = 100%"]
    PASS2 --> SCORE
    PASS3 --> SCORE
    PASS4 --> SCORE
```

#### IFEval: Instruction Following Evaluation

IFEval extends functional testing to text by creating verifiable formatting instructions:

```mermaid
graph TD
    INSTR["Instruction:<br/>'Write a paragraph with<br/>exactly 5 bullet points.<br/>Capitalize only the first sentence.'"] --> MODEL["Model<br/>Generates Text"]
    
    MODEL --> OUTPUT["Generated Output"]
    
    OUTPUT --> PARSE["Parser Checks"]
    
    PARSE --> CHECK1{"Exactly 5<br/>bullet points?"}
    PARSE --> CHECK2{"Only first sentence<br/>capitalized?"}
    PARSE --> CHECK3{"Valid paragraph<br/>structure?"}
    
    CHECK1 -->|Yes| P1["✓"]
    CHECK1 -->|No| F1["✗"]
    
    CHECK2 -->|Yes| P2["✓"]
    CHECK2 -->|No| F2["✗"]
    
    CHECK3 -->|Yes| P3["✓"]
    CHECK3 -->|No| F3["✗"]
    
    P1 --> FINAL["Final Score:<br/>3/3 checks passed"]
    P2 --> FINAL
    P3 --> FINAL
    F1 --> FINAL
    F2 --> FINAL
    F3 --> FINAL
```

**IFEval instruction types:**
- Bullet point count constraints
- Sentence capitalization patterns
- Word/character count requirements
- Specific keyword inclusion/exclusion
- Structural formatting (headers, lists, etc.)

Each instruction creates a **verifiable constraint** that can be programmatically tested, independent of semantic content quality.

**Challenge:** Extending functional testing to general text requires creativity. Unlike code (which has natural test suites) or instructions (which have explicit constraints), most text evaluation lacks obvious functional specifications.

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:107-117]()

---

## Complete Evaluation Design Workflow

The following diagram synthesizes all four decision points into an integrated workflow, showing dependencies and feedback loops:

```mermaid
graph TB
    START["Evaluation Design"] --> Q1{"Dataset<br/>exists?"}
    
    Q1 -->|Yes| INSPECT["Manual Inspection:<br/>50 samples"]
    Q1 -->|No| CREATE["Dataset Creation"]
    
    INSPECT --> QUALITY{"Quality<br/>adequate?"}
    QUALITY -->|No| CREATE
    QUALITY -->|Yes| INF_SELECT["Select Inference Method"]
    
    CREATE --> AGG["Aggregation"]
    CREATE --> HUM["Human Annotation"]
    CREATE --> SYN["Synthetic/Rule-Based"]
    
    AGG --> INF_SELECT
    HUM --> INF_SELECT
    SYN --> INF_SELECT
    
    INF_SELECT --> MCQA_INF["MCQA:<br/>Log-probability"]
    INF_SELECT --> QA_INF["QA:<br/>Generative"]
    
    MCQA_INF --> PROMPT_MCQA["Design MCQA Prompt:<br/>- Task description<br/>- Question<br/>- Options A/B/C/D<br/>- Few-shot (optional)"]
    
    QA_INF --> PROMPT_QA["Design QA Prompt:<br/>- Task description<br/>- Context (if needed)<br/>- Question<br/>- Few-shot (optional)<br/>- Constraints"]
    
    PROMPT_MCQA --> TEST_PROMPT["Test Prompt Sensitivity:<br/>Multiple variations"]
    PROMPT_QA --> TEST_PROMPT
    
    TEST_PROMPT --> SENSITIVE{"High<br/>variance?"}
    SENSITIVE -->|Yes| PROMPT_MCQA
    SENSITIVE -->|No| METRIC_SELECT["Select Metric"]
    
    METRIC_SELECT --> MCQA_METRIC["MCQA Metrics:<br/>- Accuracy (normalized)<br/>- Perplexity<br/>- F1"]
    
    METRIC_SELECT --> QA_METRIC["QA Metrics:<br/>- exact_match<br/>- prefix_match<br/>- ROUGE/BLEU"]
    
    METRIC_SELECT --> FUNC_METRIC["Functional Metrics:<br/>- Unit tests<br/>- Parser validation<br/>- Format checks"]
    
    MCQA_METRIC --> RUN["Run Evaluation"]
    QA_METRIC --> RUN
    FUNC_METRIC --> RUN
    
    RUN --> VALIDATE{"Results<br/>reasonable?"}
    VALIDATE -->|No| DEBUG["Debug:<br/>- Check normalization<br/>- Inspect failures<br/>- Review prompt"]
    VALIDATE -->|Yes| COMPLETE["Evaluation Complete"]
    
    DEBUG --> PROMPT_MCQA
    DEBUG --> PROMPT_QA
    DEBUG --> METRIC_SELECT
```

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:1-118]()

---

## Key Takeaways

1. **Dataset quality bounds evaluation quality** — No amount of engineering downstream can compensate for poor samples
2. **Manual inspection is non-negotiable** — Always inspect 50 random samples before committing to a dataset
3. **Inference method shapes results** — MCQA over-scores small models; generative matches real usage
4. **Prompts are sensitive** — Semantically equivalent prompts yield different scores; test multiple variations
5. **Match metric to measurement goal** — Average performance vs worst-case performance requires different metrics
6. **Functional testing is the future** — Tests capabilities rather than memorization; naturally contamination-resistant

**Related Resources:**
- Dataset catalog and contamination analysis: [Evaluation Datasets Catalog](#2.1.2)
- Practical troubleshooting: [Tips and Tricks](#2.1.3)
- Human annotation guidelines: [Using Human Annotators](#2.2.1)
- Inference mechanics: [Model Inference and Evaluation](#3.1)

**Sources:** [contents/automated-benchmarks/designing-your-automatic-evaluation.md:1-118]()

---

