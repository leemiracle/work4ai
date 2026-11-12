<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Text2Grad · extra page KodCode Policy Optimization · fetched 2026-10-26 -->

# KodCode Policy Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py](nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py)
- [nl_gradiant_policy_optimization/kodcode/train_kodcode.py](nl_gradiant_policy_optimization/kodcode/train_kodcode.py)

</details>



This document describes the policy optimization process for code generation models using the Text2Grad framework with the KodCode dataset. It covers the complete workflow from loading trained reward models to running PPO training with natural language gradients on code-specific feedback.

For information about the KodCode dataset structure, see [7.1.1](#7.1.1). For details on training the reward model that powers this optimization, see [7.1.2](#7.1.2). For evaluation of the optimized model, see [7.1.4](#7.1.4).

## Overview

KodCode policy optimization trains a code generation model to improve based on fine-grained feedback about code correctness, efficiency, and quality. Unlike traditional RLHF which uses scalar rewards, this approach:

1. Generates code solutions from the policy model
2. Sends code to a trained reward model for analysis
3. Receives structured feedback identifying wrong code snippets and improvable code snippets
4. Maps these spans back to token-level rewards using fuzzy matching
5. Updates the policy using PPO with token-level gradients

The key innovation is that the reward model provides explanations (`code_feedback`) along with specific code spans (`wrong_code`, `improvement_code`), enabling the policy to learn which specific parts of generated code are problematic.

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:1-160](), [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:106-137]()

## System Components

### Component Architecture

```mermaid
graph TB
    subgraph "Training Script: train_kodcode.py"
        SA[ScriptArguments] --> PPO_CFG[PPOConfig]
        QAC[QACDataset] --> COLLATOR[collator function]
        COLLATOR --> TRAINER
    end
    
    subgraph "Policy Model"
        BASE[AutoModelForCausalLMWithValueHead] --> LORA[LoraConfig<br/>r=16, alpha=32]
        LORA --> ADAPTER[Adapter Weights]
        ADAPTER --> VHEAD[Value Head]
    end
    
    subgraph "Reward Model Pipeline"
        RM[AutoModelForCausalLM<br/>reward_model_name] --> PIPE[pipeline<br/>text-generation]
        RT[reward_tokenizer] --> PIPE
    end
    
    subgraph "Text2GradTrainer"
        TRAINER[Text2GradTrainer] --> GEN[generate method]
        TRAINER --> STEP[step method]
        TRAINER --> BFP[batched_forward_pass]
        TRAINER --> TMB[train_minibatch]
    end
    
    subgraph "Span Processing"
        PREP[prepare_input_data] --> INFER[inference_reward]
        INFER --> EXTRACT[extract_spans_from_reward_model_output]
        EXTRACT --> PROC[process_response_with_spans]
        PROC --> FUZZY[fuzzy_find]
    end
    
    PPO_CFG --> TRAINER
    BASE --> TRAINER
    COLLATOR --> TRAINER
    PIPE --> INFER
    
    GEN --> PREP
    PROC --> STEP
    
    style TRAINER fill:#e8f5e9
    style PIPE fill:#fff4e1
    style FUZZY fill:#ffe1e1
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:78-323](), [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:140-323]()

### Key Classes and Functions

| Component | File Location | Purpose |
|-----------|--------------|---------|
| `Text2GradTrainer` | [text2grad_trainer.py:106-1832]() | Core PPO trainer with NL-gradient support |
| `ScriptArguments` | [train_kodcode.py:78-123]() | Hyperparameters for KodCode training |
| `QACDataset` | [train_kodcode.py:33-76]() | Dataset loader for question-answer-code format |
| `prepare_input_data` | [train_kodcode.py:378-433]() | Formats prompts for reward model |
| `fuzzy_find` | [train_kodcode.py:444-512]() | Locates code spans using fuzzy matching |
| `process_response_with_spans` | [train_kodcode.py:515-631]() | Converts spans to word-level scores |
| `extract_spans_from_reward_model_output` | [train_kodcode.py:633-682]() | Parses JSON feedback from reward model |
| `inference_reward` | [train_kodcode.py:684-718]() | Batch inference on reward model |

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:1-802](), [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:1-1832]()

## Configuration and Setup

### Script Arguments

The `ScriptArguments` dataclass defines all training hyperparameters:

```python
@dataclass
class ScriptArguments:
    base_model_name: str              # Base LLM (e.g., "meta-llama/Llama-3.1-8B-Instruct")
    base_model_adapter_model: str     # Path to existing adapter (for resumption)
    reward_model_name: str            # Trained reward model path
    learning_rate: float = 1e-5       # PPO learning rate
    batch_size: int = 32              # Training batch size
    mini_batch_size: int = 1          # PPO mini-batch size
    ppo_epochs: int = 4               # PPO update epochs per batch
    gradient_accumulation_steps: int = 1
    init_kl_coef: float = 0.2         # Initial KL penalty coefficient
    adap_kl_ctrl: bool = True         # Adaptive KL control
    kl_penalty: str = "full"          # KL divergence calculation method
    prompt_max_length: int = 1000     # Max tokens for prompt
    answer_max_length: int = 500      # Max tokens for generated code
    save_freq: int = 5                # Steps between checkpoints
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:78-123]()

### PPO Configuration

The `PPOConfig` object configures the PPO algorithm:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `vf_coef` | 0.1 | Value function loss coefficient |
| `learning_rate` | 1e-5 | Policy learning rate |
| `batch_size` | 32 | Training batch size |
| `mini_batch_size` | 1 | PPO mini-batch size |
| `ppo_epochs` | 4 | Optimization epochs per batch |
| `init_kl_coef` | 0.2 | Initial KL penalty coefficient |
| `target_kl` | 0.1 | Target KL divergence for early stopping |
| `kl_penalty` | "full" | Full KL divergence computation |

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:137-156]()

### Model Initialization

```mermaid
graph LR
    subgraph "Policy Model Setup"
        BM["base_model_name"] --> AMLM["AutoModelForCausalLMWithValueHead<br/>.from_pretrained"]
        LC["LoraConfig<br/>r=16, alpha=32<br/>dropout=0.05"] --> AMLM
        AMLM --> MODEL["model<br/>(with value head)"]
    end
    
    subgraph "Optional: Resume from Checkpoint"
        ADAPTER["base_model_adapter_model<br/>adapter_model.safetensors"] --> LOAD["Load adapter state"]
        VHEAD_FILE["pytorch_model.bin"] --> LOAD
        OPT_FILE["optimizer.pt"] --> LOAD_OPT["Load optimizer state"]
        LOAD --> MODEL
        LOAD_OPT --> OPTIMIZER
    end
    
    subgraph "Reward Model Setup"
        RM_NAME["reward_model_name"] --> RM_MODEL["AutoModelForCausalLM<br/>.from_pretrained"]
        RM_MODEL --> PIPELINE["pipeline<br/>text-generation"]
        RT["reward_tokenizer"] --> PIPELINE
    end
    
    MODEL --> TRAINER["Text2GradTrainer"]
    OPTIMIZER --> TRAINER
    PIPELINE --> INFERENCE["inference_reward<br/>function"]
```

The policy model uses LoRA adapters for parameter-efficient training. When resuming from a checkpoint, the system loads:
- Adapter weights from `adapter_model.safetensors`
- Value head weights from `pytorch_model.bin`
- Optimizer state from `optimizer.pt` (optional)

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:194-277](), [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:331-343]()

## Training Workflow

### Main Training Loop

```mermaid
graph TB
    START["Start Epoch"] --> LOAD_BATCH["Load batch from<br/>QACDataset"]
    LOAD_BATCH --> GEN["ppo_trainer.generate<br/>Generate code responses"]
    
    GEN --> PREP["prepare_input_data<br/>Format prompts for RM"]
    PREP --> RM["inference_reward<br/>Get feedback from RM"]
    
    RM --> PARSE["extract_spans_from_reward_model_output<br/>Parse JSON response"]
    PARSE --> SPANS["process_response_with_spans<br/>Map spans to word scores"]
    
    SPANS --> VALID{"Min 8 valid<br/>samples?"}
    VALID -->|No| SKIP["Skip step"]
    VALID -->|Yes| STEP["ppo_trainer.step<br/>PPO update"]
    
    STEP --> LOG["Log metrics to WandB"]
    LOG --> SAVE{"step % save_freq<br/>== 0?"}
    
    SAVE -->|Yes| CKPT["Save checkpoint:<br/>adapter + value head<br/>+ optimizer"]
    SAVE -->|No| NEXT
    CKPT --> NEXT["Next step"]
    SKIP --> NEXT
    
    NEXT --> CHECK{"More steps<br/>in epoch?"}
    CHECK -->|Yes| LOAD_BATCH
    CHECK -->|No| END["End Epoch"]
    
    style RM fill:#fff4e1
    style STEP fill:#e8f5e9
    style SPANS fill:#ffe1e1
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:803-1055]()

### Generation Configuration

Two separate generation configurations are used:

**Policy Model Generation** (`generation_kwargs`):
```python
{
    "temperature": 0.6,
    "do_sample": True,
    "top_p": 1,
    "top_k": 0,
    "max_new_tokens": 256,
    "pad_token_id": tokenizer.pad_token_id,
    "eos_token_id": tokenizer.eos_token_id,
}
```

**Reward Model Inference** (`sent_kwargs`):
```python
{
    "batch_size": 32,
    "max_new_tokens": 768,
    "pad_token_id": reward_tokenizer.eos_token_id,
    "eos_token_id": reward_tokenizer.eos_token_id,
}
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:346-362]()

## Reward Model Integration

### Prompt Formatting for Reward Model

The `prepare_input_data` function extracts code from model responses and creates structured prompts:

```mermaid
graph TB
    RESP["Generated Response"] --> EXTRACT["Extract code blocks<br/>using regex:<br/>```python...```"]
    EXTRACT --> CLEAN["Clean code:<br/>replace \\n with newline"]
    
    CLEAN --> FORMAT["Format prompt:<br/>Problem + Solution + Instructions"]
    
    FORMAT --> STRUCT["Structured Prompt:<br/>1. Correctness<br/>2. Efficiency<br/>3. Readability<br/>4. Completeness"]
    
    STRUCT --> JSON["Expected JSON Output:<br/>code_feedback<br/>wrong_code[]<br/>improvement_code[]"]
    
    JSON --> FINAL["<|begin_of_text|><|start_header_id|>user<|end_header_id|>...<br/><|eot_id|><|start_header_id|>assistant<|end_header_id|>"]
```

The prompt asks the reward model to:
1. Evaluate code quality across 4 dimensions
2. Identify specific code snippets with errors (`wrong_code`)
3. Identify code snippets that work but could be improved (`improvement_code`)
4. Provide overall feedback (`code_feedback`)

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:378-433]()

### Reward Model Inference

The `inference_reward` function performs batch inference on the reward model:

```python
def inference_reward(reward_model, input_datas):
    reward_model.model.eval()
    with torch.no_grad():
        results = reward_model(input_datas, **sent_kwargs)
        
        processed_results = []
        for result in results:
            if isinstance(result, (list, tuple)) and len(result) > 0:
                if isinstance(result[0], dict) and 'generated_text' in result[0]:
                    processed_results.append(result)
                else:
                    # Fallback for invalid format
                    processed_results.append([{'generated_text': ''}])
        
        return processed_results
```

Error handling ensures that even if the reward model fails, training continues with empty feedback.

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:684-718]()

## Span-to-Token Mapping

### Fuzzy Matching Algorithm

The core challenge is matching code spans (strings) from the reward model to token positions in the generated response. The `fuzzy_find` function handles this:

```mermaid
graph TB
    START["fuzzy_find<br/>text, pattern, threshold=0.8"] --> NORM["Normalize whitespace:<br/>re.sub(r'\\s+', ' ')"]
    
    NORM --> EXACT{"Exact match<br/>using find()?"}
    EXACT -->|Yes| RETURN1["Return start, end"]
    
    EXACT -->|No| SHORT{"Pattern < 20 chars?"}
    SHORT -->|Yes| ANCHOR["Try anchor matching:<br/>first 3 words"]
    SHORT -->|No| FUZZY
    
    ANCHOR --> APPROX{"Found anchor?"}
    APPROX -->|Yes| RETURN2["Return approximate<br/>start, end"]
    APPROX -->|No| FUZZY
    
    FUZZY["Fuzzy matching loop:<br/>SequenceMatcher"] --> SLIDING["Slide window across text<br/>step_size = pattern_len // 8"]
    
    SLIDING --> RATIO["Calculate similarity ratio<br/>for each window"]
    RATIO --> BEST{"ratio >= threshold?"}
    
    BEST -->|Yes| RETURN3["Return best match<br/>start, end"]
    BEST -->|No| LOWER{"ratio >= threshold * 0.8?"}
    
    LOWER -->|Yes| RETURN4["Return with warning"]
    LOWER -->|No| FAIL["Return -1, -1"]
```

The algorithm tries multiple strategies:
1. **Exact match**: Direct string search
2. **Anchor matching**: For short patterns, find first few words
3. **Fuzzy matching**: Use `difflib.SequenceMatcher` with sliding window
4. **Lower threshold**: Accept matches above 64% similarity with warning

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:444-512]()

### Span Processing Pipeline

The `process_response_with_spans` function converts reward model output to word-level scores:

```mermaid
graph TB
    START["process_response_with_spans<br/>response, wrong_code, improvement_code"] --> CLEAN["Filter empty/invalid spans"]
    
    CLEAN --> WRONG_LOOP["For each span in wrong_code"]
    WRONG_LOOP --> FUZZY_W["fuzzy_find<br/>threshold=0.75"]
    FUZZY_W --> MATCH_W{"Match found?"}
    MATCH_W -->|Yes| ADD_W["Add span<br/>start, end, score=-1"]
    MATCH_W -->|No| PARTIAL_W["Try partial match<br/>first 10 words, threshold=0.7"]
    PARTIAL_W --> ADD_W
    
    START --> IMPROVE_LOOP["For each span in improvement_code"]
    IMPROVE_LOOP --> FUZZY_I["fuzzy_find<br/>threshold=0.75"]
    FUZZY_I --> MATCH_I{"Match found?"}
    MATCH_I -->|Yes| ADD_I["Add span<br/>start, end, score=0"]
    MATCH_I -->|No| PARTIAL_I["Try partial match"]
    PARTIAL_I --> ADD_I
    
    ADD_W --> MERGE["Merge overlapping spans:<br/>keep minimum score"]
    ADD_I --> MERGE
    
    MERGE --> BLOCKS["Create blocks:<br/>scored spans + default score=1"]
    BLOCKS --> WORD_MAP["Map blocks to word positions"]
    WORD_MAP --> SCORES["word_scores list"]
```

The function assigns scores:
- **-1**: Words in `wrong_code` spans (errors)
- **0**: Words in `improvement_code` spans (suboptimal)
- **1**: All other words (good)

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:515-631]()

### Example: Span Matching

Consider a generated response:
```python
def add(a, b):
    return a + b + 1  # Wrong: should not add 1
```

Reward model returns:
```json
{
    "wrong_code": ["return a + b + 1"],
    "improvement_code": []
}
```

Processing:
1. `fuzzy_find` locates "return a + b + 1" at character positions 20-37
2. Response is split into words: ["def", "add(a,", "b):", "return", "a", "+", "b", "+", "1"]
3. Word positions are calculated
4. Words within the span receive score -1
5. Final scores: [1.0, 1.0, 1.0, -1, -1, -1, -1, -1, -1]

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:515-631]()

## Token-Level Reward Assignment

### Word-to-Token Alignment

The `Text2GradTrainer.rematch_scores` method aligns word-level scores to token-level rewards:

```mermaid
graph TB
    START["rematch_scores<br/>scores, words, all_tokens"] --> LOWER["Convert to lowercase:<br/>words and tokens"]
    
    LOWER --> FIND_ASSIST["Find assistant response start:<br/>locate '<|start_header_id|>assistant<|end_header_id|>'"]
    FIND_ASSIST --> EXTRACT["Extract answer tokens<br/>after assistant header"]
    
    EXTRACT --> LOOP["For each sample in batch"]
    LOOP --> CHECK{"Has valid<br/>score_list?"}
    
    CHECK -->|No| ZEROS["Fill with zeros"]
    CHECK -->|Yes| ASSIGN["assign_token_rewards<br/>token_list, word_list, score_list"]
    
    ASSIGN --> MATCH_LOOP["For each word in word_list"]
    MATCH_LOOP --> CONCAT["Concatenate tokens<br/>try 1 to 10 tokens"]
    
    CONCAT --> COMPARE{"Concatenated == word<br/>case-insensitive?"}
    COMPARE -->|Yes| SCORE["Assign score to tokens"]
    COMPARE -->|No| RETRY["Try next token position<br/>max 6 attempts"]
    
    SCORE --> SPECIAL{"Is special<br/>character?"}
    SPECIAL -->|Yes| ZERO["Score = 0"]
    SPECIAL -->|No| USE["Score = word_score"]
    
    RETRY --> MATCH_LOOP
    ZERO --> MATCH_LOOP
    USE --> MATCH_LOOP
    
    ZEROS --> COMBINE
    SCORE --> COMBINE["Combine with non-answer tokens"]
    COMBINE --> RETURN["Return token_scores"]
```

The algorithm:
1. Locates the assistant response start in the full token sequence
2. Extracts only the generated answer tokens
3. For each word, attempts to match it with 1-10 consecutive tokens
4. Assigns the word's score to all matched tokens
5. Handles special characters by assigning score 0
6. Fills unmatched tokens with score 0

**Sources:** [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:1398-1454]()

### Token Reward Integration

```mermaid
graph LR
    subgraph "Word-Level"
        WL["Word List<br/>['return', 'a', '+', 'b']"] --> WS["Word Scores<br/>[-1, -1, -1, -1]"]
    end
    
    subgraph "Token-Level"
        TL["Token List<br/>['return', 'Ġa', 'Ġ+', 'Ġb']"] --> TS["Token Scores<br/>[-1, -1, -1, -1]"]
    end
    
    WS --> MAP["assign_token_rewards<br/>Fuzzy matching"]
    TL --> MAP
    MAP --> TS
    
    TS --> COMPUTE["compute_rewards<br/>Add KL penalty"]
    COMPUTE --> FINAL["Final Rewards<br/>score - kl_penalty"]
```

The final token-level rewards combine:
- **Span-based score**: -1 (error), 0 (improvement), or 1 (good)
- **KL penalty**: `-kl_coef * (logprob - ref_logprob)`

Result: `reward[i] = score[i] - kl_coef * kl[i]`

**Sources:** [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:1456-1499]()

## PPO Update Step

### The `step` Method

The `Text2GradTrainer.step` method performs one PPO update:

```mermaid
graph TB
    START["step<br/>queries, responses, scores, words"] --> SAFETY["_step_safety_checker<br/>Validate inputs"]
    
    SAFETY --> FORWARD1["batched_forward_pass<br/>Get logprobs, values, masks"]
    FORWARD1 --> REF["batched_forward_pass<br/>on ref_model (PEFT disabled)<br/>Get ref_logprobs"]
    
    REF --> REMATCH["rematch_scores<br/>Align word scores to tokens"]
    REMATCH --> REWARDS["compute_rewards<br/>rewards = scores - kl_penalty"]
    
    REWARDS --> ADV["compute_advantages<br/>GAE algorithm"]
    ADV --> BATCH["Prepare batch_dict:<br/>logprobs, values, masks,<br/>advantages, returns"]
    
    BATCH --> PPO_LOOP["For ppo_epochs iterations"]
    PPO_LOOP --> SHUFFLE["Shuffle batch indices"]
    SHUFFLE --> BACKWARD_BATCH["For each backward_batch"]
    
    BACKWARD_BATCH --> MINI_BATCH["For each mini_batch"]
    MINI_BATCH --> FORWARD2["batched_forward_pass<br/>Get current logprobs, logits, vpreds"]
    
    FORWARD2 --> LOSS["train_minibatch<br/>Compute PPO loss"]
    LOSS --> UPDATE["accelerator.backward<br/>Gradient update"]
    
    UPDATE --> CLIP["Gradient clipping<br/>max_grad_norm"]
    CLIP --> OPT["optimizer.step<br/>optimizer.zero_grad"]
    
    OPT --> MINI_BATCH
    MINI_BATCH --> BACKWARD_BATCH
    BACKWARD_BATCH --> PPO_LOOP
    
    PPO_LOOP --> STATS["record_step_stats<br/>Collect metrics"]
    STATS --> GATHER{"Distributed?"}
    GATHER -->|Yes| SYNC["gather_stats<br/>All-reduce across GPUs"]
    GATHER -->|No| RETURN
    SYNC --> RETURN["Return stats, losses, advantages"]
    
    style FORWARD1 fill:#e1f5ff
    style LOSS fill:#e8f5e9
    style REMATCH fill:#ffe1e1
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:668-1023]()

### Loss Computation

The `train_minibatch` method computes PPO losses:

**Policy Loss** (clipped objective):
```python
ratio = torch.exp(logprobs - old_logprobs)
pg_losses = -advantages * ratio
pg_losses2 = -advantages * torch.clamp(ratio, 1 - cliprange, 1 + cliprange)
pg_loss = masked_mean(torch.max(pg_losses, pg_losses2), mask)
```

**Value Loss** (clipped):
```python
vpredclipped = clip_by_value(vpreds, values - cliprange_value, values + cliprange_value)
vf_losses1 = (vpreds - returns) ** 2
vf_losses2 = (vpredclipped - returns) ** 2
vf_loss = 0.5 * masked_mean(torch.max(vf_losses1, vf_losses2), mask)
```

**Total Loss**:
```python
loss = pg_loss + vf_coef * vf_loss
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:1233-1274](), [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:1559-1642]()

## Checkpointing and Resumption

### Checkpoint Saving

When `step % save_freq == 0`, the system saves:

1. **Adapter Model**: `adapter_model.safetensors` (LoRA weights)
2. **Value Head**: `pytorch_model.bin` (value function head)
3. **Optimizer State**: `optimizer.pt` (optimizer + lr_scheduler)

```python
save_path = os.path.join(output_dir, f"epoch_{epoch}_step_{step}")
ppo_trainer.save_pretrained(save_path)

# Save optimizer separately
optimizer_path = os.path.join(save_path, "optimizer.pt")
torch.save({
    'optimizer': optimizer.state_dict(),
    'lr_scheduler': lr_scheduler.state_dict() if lr_scheduler else None,
}, optimizer_path)
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:997-1030]()

### Checkpoint Loading

The system can resume from a checkpoint:

```mermaid
graph TB
    START["Load Checkpoint"] --> ADAPTER["Load adapter_model.safetensors"]
    ADAPTER --> VHEAD["Load pytorch_model.bin<br/>value head weights"]
    
    VHEAD --> RENAME["Rename keys:<br/>k -> 'pretrained_model.' + k + '.default'"]
    RENAME --> MERGE["Merge into model state_dict"]
    
    MERGE --> OPT_CHECK{"optimizer.pt<br/>exists?"}
    OPT_CHECK -->|Yes| LOAD_OPT["Load optimizer state"]
    OPT_CHECK -->|No| FRESH["Use fresh optimizer"]
    
    LOAD_OPT --> PARSE["Parse checkpoint path:<br/>Extract epoch and step"]
    FRESH --> PARSE
    
    PARSE --> CALC["Calculate wandb_step:<br/>epoch * steps_per_epoch + step"]
    CALC --> RESUME["Resume training"]
```

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:208-277]()

## Monitoring and Logging

### WandB Integration

The system logs comprehensive metrics to Weights & Biases:

| Metric Category | Metrics | Source |
|----------------|---------|--------|
| **Loss** | `train/loss_advantage`, `train/loss_value_kl` | PPO losses |
| **Rewards** | `rewards/mean`, `rewards/max`, `rewards/min` | Token rewards |
| **Reward Distribution** | `rewards/positive_ratio`, `rewards/negative_ratio`, `rewards/zero_ratio` | Score statistics |
| **PPO** | `ppo/mean_scores`, `ppo/std_scores`, `ppo/mean_non_score_reward` | PPO metrics |
| **KL** | `objective/kl`, `objective/kl_dist` | KL divergence |
| **Policy** | `policy/entropy`, `policy/approxkl`, `policy/clipfrac` | Policy statistics |
| **Value** | `val/vpred`, `val/error` | Value function |

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:974-995](), [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:1644-1697]()

### Sample Logging

Each batch logs sample information:

```python
batch_log = {
    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "epoch": epoch,
    "step": step,
    "batch_size": len(batch["question"]),
    "successful_samples": 0,
    "failed_samples": 0,
    "sample_logs": []  # Individual sample details
}
```

For each sample:
- Question (first 100 chars)
- Response (first 100 chars)
- Status (success/failed/error)
- Error message (if applicable)
- Reward counts

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:844-947]()

## Error Handling

### Multi-Level Error Recovery

```mermaid
graph TB
    START["Process Sample"] --> VALIDATE{"Valid llm_output<br/>format?"}
    VALIDATE -->|No| LOG1["Log: Invalid format<br/>Continue to next sample"]
    
    VALIDATE -->|Yes| CHECK_TEXT{"generated_text<br/>not empty?"}
    CHECK_TEXT -->|No| LOG2["Log: Empty text<br/>Continue to next sample"]
    
    CHECK_TEXT -->|Yes| LENGTH{"Text length<br/>>= 20 chars?"}
    LENGTH -->|No| LOG3["Log: Text too short<br/>Continue to next sample"]
    
    LENGTH -->|Yes| PARSE["extract_spans_from_reward_model_output"]
    PARSE --> PARSED{"Parsed<br/>successfully?"}
    PARSED -->|No| LOG4["Log: Parse failed<br/>Continue to next sample"]
    
    PARSED -->|Yes| PROCESS["process_response_with_spans"]
    PROCESS --> SCORES{"Valid scores<br/>generated?"}
    SCORES -->|No| LOG5["Log: No valid scores<br/>Continue to next sample"]
    
    SCORES -->|Yes| SUCCESS["Add to training batch"]
    
    LOG1 --> CONTINUE["fail += 1"]
    LOG2 --> CONTINUE
    LOG3 --> CONTINUE
    LOG4 --> CONTINUE
    LOG5 --> CONTINUE
    CONTINUE --> NEXT["Next sample"]
    
    SUCCESS --> NEXT
```

The system tolerates individual sample failures and continues training as long as at least 8 valid samples remain in the batch.

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:854-948]()

### Distributed Training Coordination

When using multiple GPUs, the system ensures all processes have sufficient samples:

```python
if ppo_trainer.accelerator.num_processes > 1:
    valid_samples_tensor = torch.tensor(valid_samples, device=device)
    
    # Gather counts from all processes
    all_valid_samples = [torch.zeros_like(valid_samples_tensor) 
                         for _ in range(num_processes)]
    torch.distributed.all_gather(all_valid_samples, valid_samples_tensor)
    
    min_valid_samples = min([count.item() for count in all_valid_samples])
    
    if min_valid_samples < 8:
        print(f"Warning: Some processes have fewer than 8 valid samples, skipping step")
        continue
```

This prevents deadlocks when different processes have different numbers of valid samples.

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:951-967]()

## Usage Example

### Basic Training Command

```bash
python nl_gradiant_policy_optimization/kodcode/train_kodcode.py \
    --base_model_name meta-llama/Llama-3.1-8B-Instruct \
    --reward_model_name path/to/trained/reward/model \
    --data_file_path path/to/kodcode/train.json \
    --output_dir ckpt/kodcode_ppo \
    --learning_rate 1e-5 \
    --batch_size 32 \
    --mini_batch_size 1 \
    --ppo_epochs 4 \
    --train_epochs 2 \
    --save_freq 5 \
    --kl_penalty full \
    --init_kl_coef 0.2
```

### Resuming from Checkpoint

```bash
python nl_gradiant_policy_optimization/kodcode/train_kodcode.py \
    --base_model_name meta-llama/Llama-3.1-8B-Instruct \
    --base_model_adapter_model ckpt/kodcode_ppo/epoch_0_step_10 \
    --reward_model_name path/to/trained/reward/model \
    --data_file_path path/to/kodcode/train.json \
    --output_dir ckpt/kodcode_ppo
```

The system automatically:
- Loads adapter and value head weights
- Restores optimizer state
- Calculates the correct epoch and step
- Resumes training from that point

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:1-160]()

## Key Differences from Generic PPO

### Code-Specific Adaptations

1. **Fuzzy Matching**: Required because code spans may have different whitespace than tokens
2. **Partial Matching**: For long code blocks, matches first N words to locate approximate position
3. **Special Character Handling**: Tokens like `<|eot_id|>` receive score 0
4. **Code Block Extraction**: Uses regex to extract code from markdown formatting
5. **Structured Feedback**: JSON format with separate arrays for wrong and improvable code

### Comparison with UltraFeedback/SLF5K

| Aspect | KodCode | UltraFeedback | SLF5K |
|--------|---------|---------------|-------|
| **Reward Format** | `wrong_code`, `improvement_code` | `good_spans`, `poor_spans` | Word-level scores |
| **Matching Strategy** | Fuzzy (code whitespace) | Direct (text) | Direct (text) |
| **Score Values** | -1, 0, 1 | -1, 0, 1 | -1, 0, 1 |
| **Prompt Format** | Code analysis | QA evaluation | Summary quality |
| **Max Tokens** | 256 (code) | 512 (answers) | 256 (summaries) |

**Sources:** [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:378-631]()

---

**Complete Sources:**
- [nl_gradiant_policy_optimization/kodcode/text2grad_trainer.py:1-1832]()
- [nl_gradiant_policy_optimization/kodcode/train_kodcode.py:1-1055]()

---

