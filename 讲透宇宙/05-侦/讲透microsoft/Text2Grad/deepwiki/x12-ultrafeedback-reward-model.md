<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Text2Grad · extra page UltraFeedback Reward Model · fetched 2026-10-26 -->

# UltraFeedback Reward Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nl_reward_model/slf5k/evaluation/3_metrics.py](nl_reward_model/slf5k/evaluation/3_metrics.py)
- [nl_reward_model/ultrafeedback/evaluation/2_infer.py](nl_reward_model/ultrafeedback/evaluation/2_infer.py)
- [nl_reward_model/ultrafeedback/evaluation/3_metrics.py](nl_reward_model/ultrafeedback/evaluation/3_metrics.py)

</details>



This page describes the training and inference pipeline for reward models in the UltraFeedback task domain. The UltraFeedback reward model learns to evaluate question-answering responses by identifying `good_spans` (high-quality phrases) and `poor_spans` (problematic phrases) within generated text.

For information about the UltraFeedback dataset format and preprocessing, see [UltraFeedback Dataset Format](#7.2.1). For using this reward model in policy optimization, see [UltraFeedback Policy Optimization](#7.2.3). For general reward model training concepts, see [Training Reward Models](#5.1).

## Model Architecture and Configuration

The UltraFeedback reward model is built on `Llama-3.1-8B-Instruct` with LoRA (Low-Rank Adaptation) for parameter-efficient fine-tuning. The model learns to generate structured JSON output containing span-level annotations.

### Base Model Specifications

| Component | Configuration |
|-----------|--------------|
| Base Model | `meta-llama/Llama-3.1-8B-Instruct` |
| Fine-tuning Method | LoRA (via PEFT library) |
| LoRA Rank (r) | 16 |
| LoRA Alpha | 32 |
| Target Modules | Query, Key, Value, Output projections |
| Training Framework | DeepSpeed with ZeRO Stage 3 |
| Precision | FP16 (float16) |

The model is trained to take a prompt-response pair and output:
- `good_spans`: List of string phrases that improve response quality
- `poor_spans`: List of string phrases that harm response quality

### Prompt Format

The model uses the Llama 3.1 chat template with a structured system prompt that defines evaluation criteria:

```mermaid
graph TB
    subgraph "Input Structure"
        UP["User Prompt<br/>(Question)"]
        AR["Assistant Response<br/>(Generated Answer)"]
    end
    
    subgraph "format_prompt()"
        TEMPLATE["Llama 3.1 Template:<br/>|begin_of_text|...|end_header_id|"]
        INSTRUCTIONS["Evaluation Instructions:<br/>- Accuracy<br/>- Relevance<br/>- Clarity<br/>- Completeness"]
        DEFINITIONS["Span Definitions:<br/>- good_spans<br/>- poor_spans"]
    end
    
    subgraph "Expected Output"
        JSON["JSON Format:<br/>{<br/>  good_spans: [...],<br/>  poor_spans: [...]<br/>}"]
    end
    
    UP --> TEMPLATE
    AR --> TEMPLATE
    TEMPLATE --> INSTRUCTIONS
    INSTRUCTIONS --> DEFINITIONS
    DEFINITIONS --> JSON
```

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:25-60]()

## Training Process

The training process follows the standard reward model training pipeline with task-specific data formatting. Training is performed using the scripts in `nl_reward_model/ultrafeedback/`.

### Training Configuration

The training typically uses:
- **Optimizer**: AdamW with DeepSpeed ZeRO Stage 3
- **Batch Size**: Configured based on GPU memory (typically 8-32 per GPU)
- **Learning Rate**: ~2e-5 to 5e-5 for LoRA adapters
- **Epochs**: Monitored with validation loss for early stopping
- **Gradient Checkpointing**: Enabled for memory efficiency
- **Mixed Precision**: FP16 training

### Data Format for Training

Training data consists of prompt-response pairs with ground truth annotations. Each training example contains:

```json
{
  "prompt": "user question or instruction",
  "response": "generated assistant response",
  "good_spans": ["phrase1", "phrase2"],
  "poor_spans": ["phrase3", "phrase4"]
}
```

The `QACDataset` class (referenced in the general training pipeline) tokenizes these examples and formats them according to the Llama 3.1 chat template.

### Checkpoint Organization

Training produces LoRA adapter checkpoints with the following structure:

```
nl_reward_model/ultrafeedback/ckpt/
└── {model_name}/
    └── {step}/
        ├── adapter_config.json
        ├── adapter_model.safetensors (or .bin)
        └── training_args.bin
```

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:12-13]() (references checkpoint paths)

## Model Merging and Deployment

Before inference, LoRA adapters must be merged with the base model to create a standalone deployment model. This is performed by `1_merge_lora.py` (typically located in the evaluation directory).

### Merging Process

```mermaid
graph LR
    subgraph "Input Components"
        BASE["Base Model<br/>Llama-3.1-8B-Instruct"]
        ADAPTER["LoRA Adapters<br/>adapter_model.safetensors"]
        CONFIG["Adapter Config<br/>adapter_config.json"]
    end
    
    subgraph "merge_lora.py"
        LOAD["PeftModel.from_pretrained()"]
        MERGE["model.merge_and_unload()"]
        SAVE["save_pretrained()"]
    end
    
    subgraph "Output"
        FULL["Merged Full Model<br/>{step}_merge/"]
    end
    
    BASE --> LOAD
    ADAPTER --> LOAD
    CONFIG --> LOAD
    LOAD --> MERGE
    MERGE --> SAVE
    SAVE --> FULL
```

The merged model contains all weights in a single model file, eliminating the need for PEFT at inference time and enabling compatibility with optimized inference engines like VLLM.

**Sources:** Diagram 3 from high-level architecture

## Inference Pipeline

Inference uses VLLM (vLLM) for high-throughput batch processing. The pipeline is implemented in `2_infer.py`.

### VLLM Configuration

```python
# Key configuration from 2_infer.py
LLM(
    model=model_path,
    tensor_parallel_size=tensor_parallel_size,  # Multi-GPU parallelism
    dtype="float16",
    trust_remote_code=True,
    max_model_len=8192
)

SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=300  # Sufficient for JSON span output
)
```

### Inference Data Flow

```mermaid
graph TB
    subgraph "Input: Test Dataset"
        TEST_JSON["test_annotated_v4_concurrent_2step.json"]
        ITEMS["List of:<br/>{prompt, response, good_spans, poor_spans}"]
    end
    
    subgraph "2_infer.py Main Loop"
        BATCH["Batch Creation<br/>(batch_size=32)"]
        FORMAT["format_prompt()<br/>Add chat template"]
        GENERATE["model.generate()<br/>VLLM batch inference"]
    end
    
    subgraph "Response Processing"
        EXTRACT["Extract generated text<br/>from output.outputs[0].text"]
        PARSE["parse_response()<br/>JSON extraction"]
        FALLBACK["extract_spans_with_regex()<br/>Regex fallback"]
    end
    
    subgraph "Output Storage"
        RESULT["Result JSON:<br/>{prompt, response,<br/>ground_truth, model_output,<br/>raw_model_output}"]
        OUTPUT_FILE["validation_results.json"]
    end
    
    TEST_JSON --> ITEMS
    ITEMS --> BATCH
    BATCH --> FORMAT
    FORMAT --> GENERATE
    GENERATE --> EXTRACT
    EXTRACT --> PARSE
    PARSE -->|Success| RESULT
    PARSE -->|Fail| FALLBACK
    FALLBACK --> RESULT
    RESULT --> OUTPUT_FILE
```

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:103-176]()

### Command-Line Arguments

The inference script accepts the following arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--model_path` | `../ckpt/llama31-8B-span2span-v2-nofeedback/0_10000_merge` | Path to merged model |
| `--valid_dataset_file` | `../data/ultrafeedback/RM/test_annotated_v4_concurrent_2step.json` | Test data path |
| `--output_file` | `validation_results.json` | Output JSON file |
| `--batch_size` | `32` | Batch size for inference |
| `--max_new_tokens` | `300` | Maximum tokens to generate |
| `--num_samples` | `1000` | Number of samples to evaluate (-1 for all) |
| `--tensor_parallel_size` | `1` | Number of GPUs for tensor parallelism |
| `--gpu_ids` | `0,1,2,3,4,5,6,7` | Comma-separated GPU IDs |

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:10-23]()

## Response Parsing Strategies

The inference pipeline implements robust parsing with multiple fallback strategies to handle malformed JSON outputs, which are common with LLM generation.

### Primary JSON Parsing

```mermaid
graph TD
    RAW["Raw Model Output<br/>(assistant_part)"]
    FIND_JSON["Find JSON boundaries<br/>json_start = find('{' )<br/>json_end = rfind('}')"]
    EXTRACT["Extract json_str<br/>[json_start:json_end]"]
    PARSE["json.loads(json_str)"]
    
    SUCCESS{{"Success?"}}
    RETURN_JSON["Return parsed dict"]
    
    RAW --> FIND_JSON
    FIND_JSON --> EXTRACT
    EXTRACT --> PARSE
    PARSE --> SUCCESS
    SUCCESS -->|Yes| RETURN_JSON
    SUCCESS -->|No| REGEX["Fallback:<br/>extract_spans_with_regex()"]
    REGEX --> RETURN_REGEX["Return extracted spans"]
```

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:62-78]()

### Regex Fallback Extraction

When JSON parsing fails, the system uses regex patterns to extract spans:

```python
# Pattern for good_spans
good_spans_pattern = r'"good_spans"\s*:\s*\[(.*?)\]'

# Pattern for poor_spans
poor_spans_pattern = r'"poor_spans"\s*:\s*\[(.*?)\]'

# Extract individual span strings (handles both " and ')
span_pattern = r'(?:"([^"]*?)"|\'([^\']*?)\')'
```

This regex-based extraction handles:
- Malformed JSON with missing brackets or quotes
- Mixed quote styles (single and double quotes)
- Extra whitespace or formatting issues
- Incomplete JSON structures

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:80-101]()

### Error Handling

The parsing pipeline wraps all operations in exception handling:

```mermaid
graph TD
    PARSE_ATTEMPT["Parse attempt"]
    TRY_JSON["Try json.loads()"]
    TRY_REGEX["Try regex extraction"]
    
    CATCH_JSON_ERROR{{"JSONDecodeError?"}}
    CATCH_ANY_ERROR{{"Any Exception?"}}
    
    RETURN_ERROR["Return:<br/>{error: message,<br/>raw_response: text}"]
    RETURN_RESULT["Return extracted spans"]
    
    PARSE_ATTEMPT --> TRY_JSON
    TRY_JSON --> CATCH_JSON_ERROR
    CATCH_JSON_ERROR -->|Yes| TRY_REGEX
    CATCH_JSON_ERROR -->|No| RETURN_RESULT
    TRY_REGEX --> RETURN_RESULT
    PARSE_ATTEMPT --> CATCH_ANY_ERROR
    CATCH_ANY_ERROR -->|Yes| RETURN_ERROR
    CATCH_ANY_ERROR -->|No| RETURN_RESULT
```

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:77-78]()

## Output Format

The inference script produces a JSON file containing detailed results for each test sample.

### Output Structure

```json
[
  {
    "prompt": "Original user question",
    "response": "Generated assistant response",
    "ground_truth": {
      "good_spans": ["ground truth good phrase 1", ...],
      "poor_spans": ["ground truth poor phrase 1", ...]
    },
    "model_output": {
      "good_spans": ["predicted good phrase 1", ...],
      "poor_spans": ["predicted poor phrase 1", ...]
    },
    "raw_model_output": "Raw text generated by model"
  },
  ...
]
```

### Key Fields

| Field | Description |
|-------|-------------|
| `prompt` | Original user input/question from test set |
| `response` | Assistant's generated response being evaluated |
| `ground_truth` | Human-annotated spans from the test dataset |
| `model_output` | Model's predicted spans (parsed from generation) |
| `raw_model_output` | Complete unprocessed model output for debugging |

This output format is consumed by the metrics calculation script (`3_metrics.py`) for evaluation. See [UltraFeedback Evaluation](#7.2.4) for details on metric computation.

**Sources:** [nl_reward_model/ultrafeedback/evaluation/2_infer.py:155-166]()

## Evaluation Metrics

The reward model's predictions are evaluated using multiple metrics at different granularities. The metrics script (`3_metrics.py`) computes:

### Word-Level Metrics

Each word in the response receives a score based on span membership:
- **Score +1**: Words in `good_spans`
- **Score -1**: Words in `poor_spans`
- **Score 0**: Neutral words

Precision, recall, and F1 are calculated separately for each score class.

### Span-Level Metrics

Span overlap metrics measure how well predicted spans match ground truth spans:

```mermaid
graph TB
    subgraph "Span Extraction"
        WORD_SCORES["word_score_list:<br/>[(word1, 1), (word2, 1), (word3, -1), ...]"]
        EXTRACT["extract_spans()<br/>Group contiguous same-score words"]
        GOOD_SPANS["good_spans:<br/>List of [indices]"]
        POOR_SPANS["poor_spans:<br/>List of [indices]"]
    end
    
    subgraph "IoU Calculation"
        GT_SPANS["Ground Truth Spans"]
        PRED_SPANS["Predicted Spans"]
        INTERSECTION["Intersection:<br/>Overlapping word indices"]
        UNION["Union:<br/>All word indices"]
        IOU["IoU = |Intersection| / |Union|"]
    end
    
    subgraph "Match Types"
        EXACT["Exact Match:<br/>IoU = 1.0"]
        PARTIAL["Partial Match:<br/>IoU > 0"]
    end
    
    WORD_SCORES --> EXTRACT
    EXTRACT --> GOOD_SPANS
    EXTRACT --> POOR_SPANS
    
    GT_SPANS --> INTERSECTION
    PRED_SPANS --> INTERSECTION
    GT_SPANS --> UNION
    PRED_SPANS --> UNION
    INTERSECTION --> IOU
    UNION --> IOU
    
    IOU --> EXACT
    IOU --> PARTIAL
```

**Span metrics include:**
- **Exact Match Count**: Spans with IoU = 1.0 (perfect boundary alignment)
- **Partial Match Count**: Spans with IoU > 0 (any overlap)
- **Average IoU**: Mean intersection-over-union across all span pairs
- **Precision/Recall/F1**: Based on partial matches

**Sources:** [nl_reward_model/ultrafeedback/evaluation/3_metrics.py:143-269]()

### Computation Flow

```mermaid
graph TB
    subgraph "Input Files"
        INFER_OUT["validation_results.json<br/>(from 2_infer.py)"]
        TEST_DATA["test_annotated_v4_concurrent_2step.json<br/>(ground truth)"]
    end
    
    subgraph "3_metrics.py Processing"
        LOAD["Load both JSON files"]
        ALIGN["Align predictions<br/>with ground truth"]
        
        CALC_WORD["calculate_metrics()<br/>Word-level P/R/F1"]
        CALC_SPAN["calculate_span_overlap_metrics()<br/>Span IoU and matches"]
        CALC_ROUGE["calculate_rouge_scores()<br/>N-gram similarity"]
    end
    
    subgraph "Output Files"
        SUMMARY["word_metrics_summary.json:<br/>Overall statistics"]
        DATA["word_metrics_summary_data.json:<br/>Per-sample details"]
    end
    
    INFER_OUT --> LOAD
    TEST_DATA --> LOAD
    LOAD --> ALIGN
    ALIGN --> CALC_WORD
    ALIGN --> CALC_SPAN
    ALIGN --> CALC_ROUGE
    
    CALC_WORD --> SUMMARY
    CALC_SPAN --> SUMMARY
    CALC_ROUGE --> SUMMARY
    CALC_WORD --> DATA
    CALC_SPAN --> DATA
    CALC_ROUGE --> DATA
```

**Sources:** [nl_reward_model/ultrafeedback/evaluation/3_metrics.py:271-593]()

### Sample Metrics Output

The metrics summary includes:

```json
{
  "overall_metrics": {
    "positive": {"precision": 0.xx, "recall": 0.xx, "f1": 0.xx},
    "negative": {"precision": 0.xx, "recall": 0.xx, "f1": 0.xx},
    "neutral": {"precision": 0.xx, "recall": 0.xx, "f1": 0.xx},
    "overall": {"precision": 0.xx, "recall": 0.xx, "f1": 0.xx}
  },
  "overall_span_metrics": {
    "good_span": {
      "gt_count": 100,
      "ex_count": 95,
      "exact_match": 60,
      "partial_match": 80,
      "precision": 0.xx,
      "recall": 0.xx,
      "f1": 0.xx
    },
    "poor_span": { /* similar structure */ }
  }
}
```

For complete evaluation methodology and benchmarking, see [UltraFeedback Evaluation](#7.2.4).

**Sources:** [nl_reward_model/ultrafeedback/evaluation/3_metrics.py:375-412]()

---

