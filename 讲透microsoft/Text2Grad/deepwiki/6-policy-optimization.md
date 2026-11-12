<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Text2Grad · page 6 Policy Optimization · fetched 2026-10-26 -->

# Policy Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py](nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py)

</details>



This page provides an overview of the Natural Language Gradient Policy Optimization component, which uses the `TEXT2GRADTrainer` class to train language models with fine-grained, token-level feedback derived from natural language critiques. This is the third component in the Text2Grad pipeline, following data annotation (see [Data Annotation Pipeline](#4)) and reward model training (see [Reward Models](#5)).

For detailed implementation of specific aspects, see:
- [TEXT2GRADTrainer Architecture](#6.1) - Class structure and initialization
- [PPO Training Loop](#6.2) - Complete training step implementation
- [Token-Reward Alignment](#6.4) - Fuzzy matching algorithm

## Purpose and Scope

Policy optimization in Text2Grad converts natural language feedback from a trained reward model into token-level gradient signals for Proximal Policy Optimization (PPO). Unlike traditional RLHF which uses scalar rewards for entire sequences, this system assigns individual rewards to each token based on whether it appears in "good spans" or "poor spans" identified by the reward model. The `TEXT2GRADTrainer` class orchestrates this process across multiple PPO epochs, handling reward computation, advantage estimation, and policy updates.

This document covers the high-level architecture, training workflow, and key concepts. Implementation details for specific algorithms are documented in child pages.

## System Architecture

### Component Integration

```mermaid
graph TB
    subgraph "Inputs"
        RM["Trained Reward Model<br/>(frozen checkpoint)"]
        BASE["Base Policy Model<br/>(Llama-3.1-8B-Instruct)"]
        DATA["Training Dataset<br/>(prompts)"]
        CONFIG["PPOConfig<br/>(hyperparameters)"]
    end
    
    subgraph "TEXT2GRADTrainer Initialization"
        INIT["TEXT2GRADTrainer.__init__()<br/>line 138-388"]
        
        LORA["LoRA Adapter<br/>(rank 16, alpha 32)"]
        VHEAD["Value Head<br/>(scalar output)"]
        BASE --> LORA
        LORA --> VHEAD
        VHEAD --> POLICY["Policy Model<br/>(PreTrainedModelWrapper)"]
        
        CONFIG --> INIT
        POLICY --> INIT
        RM --> RM_PIPE["Reward Model Pipeline<br/>(text generation)"]
        RM_PIPE --> INIT
        
        INIT --> OPTIMIZER["DummyOptim<br/>(for DeepSpeed)"]
        INIT --> SCHEDULER["DummyScheduler"]
        INIT --> ACCEL["Accelerator<br/>(distributed training)"]
    end
    
    subgraph "Training Loop"
        STEP["step() method<br/>line 663-1018"]
        DATA --> STEP
        INIT --> STEP
        
        STEP --> GEN["generate()<br/>line 452-530"]
        GEN --> RM_PIPE
        RM_PIPE --> FEEDBACK["Structured Feedback<br/>(good_spans, poor_spans)"]
        FEEDBACK --> REMATCH["rematch_scores()<br/>line 1389-1445"]
        REMATCH --> TOKEN_SCORES["Token-Level Scores<br/>+1, -1, or 0"]
        TOKEN_SCORES --> COMPUTE["compute_rewards()<br/>line 1447-1490"]
        COMPUTE --> ADV["compute_advantages()<br/>line 1507-1551"]
        ADV --> LOSS["loss()<br/>line 1553-1643"]
        LOSS --> UPDATE["PPO Update<br/>train_minibatch()"]
    end
    
    subgraph "Outputs"
        UPDATE --> CKPT["Model Checkpoints<br/>(adapter + value head)"]
        STEP --> METRICS["Training Metrics<br/>(WandB logs)"]
        UPDATE --> OPT_POLICY["Optimized Policy"]
    end
```

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:104-388](), [README.md:277-294]()

### TEXT2GRADTrainer Class Structure

The `TEXT2GRADTrainer` class extends TRL's `BaseTrainer` and implements the core PPO algorithm with natural language gradients:

```mermaid
classDiagram
    class BaseTrainer {
        <<TRL Framework>>
    }
    
    class TEXT2GRADTrainer {
        +config: PPOConfig
        +model: PreTrainedModelWrapper
        +ref_model: PreTrainedModelWrapper
        +tokenizer: PreTrainedTokenizerBase
        +optimizer: DummyOptim
        +accelerator: Accelerator
        +kl_ctl: KLController
        
        +__init__(config, model, ref_model, tokenizer, ...)
        +generate(query_tensor, ...) List~Tensor~
        +step(queries, responses, scores, words) dict
        +batched_forward_pass(model, queries, responses, ...) Tuple
        +train_minibatch(old_logprobs, values, ...) dict
        +rematch_scores(scores, words, all_tokens) List~Tensor~
        +compute_rewards(scores, logprobs, ref_logprobs, ...) Tuple
        +compute_advantages(values, rewards, mask) Tuple
        +loss(old_logprobs, values, logits, ...) Tuple
    }
    
    class PPOConfig {
        +batch_size: int
        +mini_batch_size: int
        +learning_rate: float
        +ppo_epochs: int
        +init_kl_coef: float
        +gamma: float
        +lam: float
        +cliprange: float
        +cliprange_value: float
    }
    
    class PreTrainedModelWrapper {
        +pretrained_model: LlamaForCausalLM
        +v_head: ValueHead
        +forward(input_ids, ...) Tuple
        +generate(input_ids, ...) Tensor
    }
    
    class KLController {
        +value: float
        +update(kl, batch_size)
    }
    
    BaseTrainer <|-- TEXT2GRADTrainer
    TEXT2GRADTrainer --> PPOConfig
    TEXT2GRADTrainer --> PreTrainedModelWrapper
    TEXT2GRADTrainer --> KLController
```

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:104-135](), [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:138-388]()

## Training Workflow

### High-Level Training Loop

The training process follows a standard reinforcement learning loop with a critical modification: rewards are computed at the token level rather than as scalar values for entire sequences.

```mermaid
graph TB
    START["Start Training Epoch"]
    
    START --> LOAD["Load Batch from Dataset<br/>(queries: prompts)"]
    
    LOAD --> GENERATE["ppo_trainer.generate()<br/>Generate responses from policy"]
    
    GENERATE --> FORMAT["Format for Reward Model<br/>(question + answer pairs)"]
    
    FORMAT --> RM_INFER["Reward Model Inference<br/>(returns JSON feedback)"]
    
    RM_INFER --> PARSE["Parse Feedback<br/>(extract good_spans, poor_spans)"]
    
    PARSE --> FUZZY["Fuzzy String Matching<br/>(locate spans in response)"]
    
    FUZZY --> WORD_SCORES["Assign Word Scores<br/>(+1: good, -1: poor, 0: neutral)"]
    
    WORD_SCORES --> ALIGN["rematch_scores()<br/>(align words to tokens)"]
    
    ALIGN --> TOKEN_REWARDS["Token-Level Rewards<br/>(one score per token)"]
    
    TOKEN_REWARDS --> FORWARD["batched_forward_pass()<br/>(compute logprobs, values)"]
    
    FORWARD --> KL["Add KL Penalty<br/>(divergence from ref_model)"]
    
    KL --> REWARDS["Final Rewards<br/>(token_score - kl_penalty)"]
    
    REWARDS --> GAE["compute_advantages()<br/>(Generalized Advantage Estimation)"]
    
    GAE --> PPO_EPOCHS{"PPO Epochs<br/>(default: 4)"}
    
    PPO_EPOCHS --> MINI_BATCH["Sample Mini-Batch<br/>(shuffle batch indices)"]
    
    MINI_BATCH --> FORWARD2["Forward Pass<br/>(new logprobs, values)"]
    
    FORWARD2 --> LOSS["loss()<br/>(policy + value loss)"]
    
    LOSS --> BACKWARD["Backward Pass<br/>(compute gradients)"]
    
    BACKWARD --> OPTIMIZER["optimizer.step()<br/>(update parameters)"]
    
    OPTIMIZER --> PPO_CHECK{More<br/>Mini-Batches?}
    
    PPO_CHECK -->|Yes| MINI_BATCH
    PPO_CHECK -->|No| EPOCH_CHECK{More<br/>PPO Epochs?}
    
    EPOCH_CHECK -->|Yes| PPO_EPOCHS
    EPOCH_CHECK -->|No| LOG["Log Metrics<br/>(WandB)"]
    
    LOG --> SAVE{Save<br/>Checkpoint?}
    
    SAVE -->|Yes| CHECKPOINT["Save Adapter + Value Head<br/>+ Optimizer State"]
    SAVE -->|No| NEXT_BATCH{More<br/>Batches?}
    
    CHECKPOINT --> NEXT_BATCH
    NEXT_BATCH -->|Yes| LOAD
    NEXT_BATCH -->|No| END["Training Complete"]
```

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:663-1018]()

### Key Innovation: Token-Level Rewards

Traditional RLHF assigns a single scalar reward to an entire generated sequence. Text2Grad's key innovation is computing rewards at the token level:

| Traditional RLHF | Text2Grad NL-Gradients |
|------------------|------------------------|
| `reward = scalar` (e.g., 0.85) | `rewards = [+1, +1, 0, -1, 0, +1, ...]` |
| Applied uniformly to all tokens | Each token gets individual reward |
| No localization of errors | Pinpoints exact problematic tokens |
| Opaque feedback | Interpretable via natural language |

The process for computing token-level rewards:

1. **Reward Model Output**: JSON with `good_spans` and `poor_spans` lists
   ```json
   {
     "good_spans": ["correctly handles edge case", "efficient algorithm"],
     "poor_spans": ["incorrect variable name", "missing error check"]
   }
   ```

2. **Fuzzy Matching**: Locate these spans in the generated response using string similarity

3. **Word-Level Scoring**: Assign scores to each word
   - Words in `good_spans`: **+1**
   - Words in `poor_spans`: **-1**
   - Other words: **0**

4. **Token Alignment**: Map word scores to tokens via `rematch_scores()` (see [Token-Reward Alignment](#6.4))

5. **KL Penalty**: Subtract KL divergence from reference model to prevent drift

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:780-810](), [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:1447-1490]()

## Core Methods

### Initialization

The `__init__` method (lines 138-388) sets up all components needed for training:

| Component | Configuration | Purpose |
|-----------|--------------|---------|
| **Policy Model** | Base LLM + LoRA (r=16) + Value Head | Model being optimized |
| **Reference Model** | Frozen copy or PEFT base | KL penalty computation |
| **Optimizer** | `DummyOptim` wrapper | DeepSpeed compatibility |
| **Accelerator** | Multi-GPU coordination | Distributed training |
| **KL Controller** | Adaptive or Fixed | Controls KL penalty strength |
| **Data Collator** | `DataCollatorForLanguageModeling` | Batch preparation |

**Critical Detail**: When using PEFT/LoRA, `self.ref_model` is set to `None` and the reference logprobs are computed by temporarily disabling the adapter via `self.optional_peft_ctx()`.

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:138-388]()

### Generation

The `generate()` method (lines 452-530) produces responses from the policy model:

```mermaid
graph LR
    QUERY["Query Tensors<br/>(input_ids)"] --> BATCH["Batch Queries<br/>(padding + masking)"]
    BATCH --> MODEL["model.generate()<br/>(unwrapped for generation)"]
    MODEL --> RAW["Raw Generations<br/>(with special tokens)"]
    RAW --> CLEAN["clean_special_tokens()<br/>(remove headers, EOT)"]
    CLEAN --> TRUNCATE["Truncate at EOS<br/>(first eos_token_id)"]
    TRUNCATE --> RESPONSE["Response Tensors<br/>(clean output)"]
```

The cleaning process is critical for subsequent fuzzy matching:
- Removes Llama-3 special tokens: `<|start_header_id|>`, `<|end_header_id|>`, `<|eot_id|>`
- Strips role markers: `assistant`, `human`
- Normalizes whitespace

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:452-612]()

### PPO Step

The `step()` method (lines 663-1018) implements one complete PPO optimization step:

```mermaid
sequenceDiagram
    participant Caller
    participant step
    participant batched_forward_pass
    participant rematch_scores
    participant compute_rewards
    participant compute_advantages
    participant train_minibatch
    
    Caller->>step: queries, responses, scores, words
    
    step->>step: Safety checks
    step->>step: Optional score scaling/clipping
    
    step->>batched_forward_pass: model, queries, responses
    batched_forward_pass-->>step: logprobs, values, masks, tokens
    
    step->>batched_forward_pass: ref_model, queries, responses
    batched_forward_pass-->>step: ref_logprobs
    
    step->>rematch_scores: scores, words, tokens
    rematch_scores-->>step: token_scores (aligned)
    
    step->>compute_rewards: token_scores, logprobs, ref_logprobs
    compute_rewards-->>step: rewards, non_score_reward, kls
    
    step->>compute_advantages: values, rewards, masks
    compute_advantages-->>step: values, advantages, returns
    
    loop PPO Epochs (default: 4)
        loop Mini-Batches
            step->>train_minibatch: old_logprobs, values, advantages, returns
            train_minibatch->>train_minibatch: Forward pass
            train_minibatch->>train_minibatch: Compute loss
            train_minibatch->>train_minibatch: Backward + optimizer step
            train_minibatch-->>step: train_stats
        end
    end
    
    step->>step: Aggregate statistics
    step-->>Caller: stats, loss_p, loss_v, avg_advantages
```

**Key Steps**:
1. **Safety Checking**: Validate batch dimensions and tensor devices
2. **Forward Passes**: Compute logprobs for policy and reference model
3. **Reward Alignment**: Convert word-level scores to token-level rewards
4. **Reward Computation**: Add token scores and KL penalty
5. **Advantage Estimation**: Compute advantages using GAE (γ=0.99, λ=0.95)
6. **Mini-Batch Training**: Multiple PPO epochs over shuffled mini-batches
7. **Statistics**: Aggregate and log training metrics

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:663-1018]()

## Reward Processing Pipeline

The transformation from natural language feedback to token-level rewards is the distinguishing feature of Text2Grad:

```mermaid
graph TB
    subgraph "Reward Model Output"
        RM_JSON["JSON Response<br/>{good_spans: [...], poor_spans: [...]}"]
    end
    
    subgraph "Word-Level Processing"
        RM_JSON --> EXTRACT["Extract Spans<br/>(list of strings)"]
        EXTRACT --> GOOD["Good Spans<br/>['efficient solution', 'clear logic']"]
        EXTRACT --> POOR["Poor Spans<br/>['syntax error', 'wrong variable']"]
    end
    
    subgraph "Fuzzy Matching (assign_token_rewards)"
        GOOD --> FUZZY["Fuzzy String Matching<br/>(locate in response text)"]
        POOR --> FUZZY
        RESPONSE["Generated Response<br/>(word list)"] --> FUZZY
        
        FUZZY --> WORD_SCORES["Word Scores<br/>word_list: [w1, w2, w3, ...]<br/>score_list: [+1, 0, -1, ...]"]
    end
    
    subgraph "Token Alignment (rematch_scores)"
        WORD_SCORES --> TOKENIZE["Tokenize Response<br/>(tokenizer.encode)"]
        TOKENIZE --> TOKEN_LIST["Token List<br/>[t1, t2, t3, ...]"]
        
        TOKEN_LIST --> ALIGN["Align Words to Tokens<br/>(handle multi-token words)"]
        WORD_SCORES --> ALIGN
        
        ALIGN --> TOKEN_SCORES["Token Scores<br/>[+1, +1, 0, -1, 0, ...]"]
    end
    
    subgraph "Reward Computation"
        TOKEN_SCORES --> KL_PEN["Add KL Penalty<br/>reward = score - β * KL"]
        REF_LOGPROBS["Reference Model<br/>Logprobs"] --> KL_PEN
        LOGPROBS["Policy Model<br/>Logprobs"] --> KL_PEN
        
        KL_PEN --> FINAL_REWARDS["Final Token Rewards<br/>(used for PPO update)"]
    end
```

**Key Functions**:
- `rematch_scores()`: Main coordinator (line 1389-1445)
- `assign_token_rewards()`: Fuzzy matching logic (line 1299-1387)
- `compute_rewards()`: Add KL penalty (line 1447-1490)

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:1299-1490]()

## Loss Computation

The `loss()` method (lines 1553-1643) implements the PPO clipped objective:

```mermaid
graph TB
    subgraph "Inputs"
        OLD_LP["old_logprobs<br/>(from initial forward pass)"]
        NEW_LP["logprobs<br/>(from current mini-batch)"]
        ADV["advantages<br/>(from GAE)"]
        RETURNS["returns<br/>(advantages + values)"]
        VALUES["values<br/>(from value head)"]
        VPREDS["vpreds<br/>(current value predictions)"]
    end
    
    subgraph "Policy Loss"
        OLD_LP --> RATIO["ratio = exp(logprobs - old_logprobs)"]
        NEW_LP --> RATIO
        
        RATIO --> CLIP["clipped_ratio = clip(ratio, 1-ε, 1+ε)<br/>(ε = cliprange = 0.2)"]
        
        ADV --> PG1["pg_loss1 = -advantages * ratio"]
        RATIO --> PG1
        
        ADV --> PG2["pg_loss2 = -advantages * clipped_ratio"]
        CLIP --> PG2
        
        PG1 --> PG_LOSS["pg_loss = max(pg_loss1, pg_loss2)<br/>(masked mean)"]
        PG2 --> PG_LOSS
    end
    
    subgraph "Value Loss"
        VPREDS --> VCLIP["vpred_clipped = clip(vpreds, values-δ, values+δ)<br/>(δ = cliprange_value = 0.2)"]
        VALUES --> VCLIP
        
        VPREDS --> VF1["vf_loss1 = (vpreds - returns)²"]
        RETURNS --> VF1
        
        VCLIP --> VF2["vf_loss2 = (vpred_clipped - returns)²"]
        RETURNS --> VF2
        
        VF1 --> VF_LOSS["vf_loss = 0.5 * max(vf_loss1, vf_loss2)<br/>(masked mean)"]
        VF2 --> VF_LOSS
    end
    
    subgraph "Combined Loss"
        PG_LOSS --> TOTAL["total_loss = pg_loss + vf_coef * vf_loss<br/>(vf_coef = 1.0)"]
        VF_LOSS --> TOTAL
    end
```

**PPO Clipping**: The clipping prevents excessively large policy updates by limiting the ratio of new to old probabilities:
- `ratio ∈ [0.8, 1.2]` (with `cliprange=0.2`)
- If advantage is positive (good action), limit how much we can increase probability
- If advantage is negative (bad action), limit how much we can decrease probability

**Value Clipping**: Similarly prevents large value function updates, improving stability.

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:1553-1643]()

## Distributed Training

The `TEXT2GRADTrainer` uses Hugging Face Accelerate for distributed training:

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| **Accelerator** | `accelerate.Accelerator` | Coordinates multi-GPU training |
| **DummyOptim** | Wraps real optimizer | DeepSpeed compatibility |
| **Padding** | `pad_across_processes()` | Ensures consistent tensor shapes |
| **Gathering** | `gather_object()`, `all_reduce()` | Collects statistics from all GPUs |
| **Barriers** | `dist.barrier()` | Synchronizes processes |

**Key Method**: `gather_stats()` (lines 1053-1067) aggregates metrics across GPUs:
```python
for k, v in stats.items():
    if isinstance(v, torch.Tensor):
        dist.all_reduce(v.to(self.accelerator.device), dist.ReduceOp.SUM)
        v /= self.accelerator.num_processes
```

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:187-192](), [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:721-748](), [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:1053-1067]()

## Task-Specific Training

The `TEXT2GRADTrainer` class is reused across all three tasks with task-specific training scripts:

| Task | Training Script | Dataset | Reward Model |
|------|----------------|---------|--------------|
| **Code Generation** | `nl_gradient_policy_optimization/kodcode/train_kodcode.py` | KodCode-Light-RL-10K | Identifies code errors and correct patterns |
| **Question Answering** | `nl_gradient_policy_optimization/ultrafeedback/train_ultrafeedback.py` | UltraFeedback-Binarized | Evaluates answer quality and relevance |
| **Summarization** | `nl_gradient_policy_optimization/slf5k/train.py` | SLF5K | Assesses summary accuracy and conciseness |

Each training script:
1. Loads task-specific configuration (`ScriptArguments`)
2. Initializes the reward model pipeline
3. Creates dataset with appropriate formatting
4. Instantiates `TEXT2GRADTrainer`
5. Runs training loop with evaluation

**Sources:** [README.md:277-294]()

## Memory Management

The trainer includes extensive memory optimization to handle large models:

```python
# Explicit cache clearing after each operation
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Delete intermediate tensors
del logprobs, logits, vpreds, model_inputs

# Clear cache periodically during batching
if torch.cuda.is_available() and i % 2 == 1:
    torch.cuda.empty_cache()
```

This is critical because:
- Token-level rewards create large tensors
- Multiple forward passes per step (policy + reference)
- Multiple PPO epochs over same data
- Gradient accumulation for large batches

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:676-677](), [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:1104](), [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:1209-1210]()

## Configuration

Key `PPOConfig` parameters for policy optimization:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `learning_rate` | 1e-5 | Optimizer learning rate |
| `batch_size` | 4-8 | Number of samples per batch |
| `mini_batch_size` | 1-2 | Mini-batch size for gradient accumulation |
| `ppo_epochs` | 4 | Number of PPO optimization epochs |
| `init_kl_coef` | 0.05-0.2 | Initial KL penalty coefficient |
| `gamma` | 0.99 | Discount factor for rewards |
| `lam` | 0.95 | GAE lambda parameter |
| `cliprange` | 0.2 | PPO clipping parameter |
| `cliprange_value` | 0.2 | Value function clipping parameter |
| `vf_coef` | 1.0 | Value loss coefficient |

**Sources:** [nl_gradiant_policy_optimization/ultrafeedback/text2grad_trainer.py:138-388]()

## Next Steps

For detailed implementation of specific components:
- [TEXT2GRADTrainer Architecture](#6.1) - Detailed class structure and initialization
- [PPO Training Loop](#6.2) - Step-by-step breakdown of training iterations
- [Reward Processing Pipeline](#6.3) - Natural language to reward conversion
- [Token-Reward Alignment](#6.4) - Fuzzy matching algorithm details
- [Forward Pass and Masking](#6.5) - Batched computation and attention masking
- [Loss Calculation and Updates](#6.6) - PPO objective and optimization
- [Checkpoint Management](#6.7) - Saving and loading trained models
- [Distributed Training](#6.8) - Multi-GPU training strategies

For task-specific guides:
- [Code Generation (KodCode)](#7.1.3) - Code generation policy optimization
- [Question Answering (UltraFeedback)](#7.2.3) - QA policy optimization
- [Summarization (SLF5K)](#7.3.3) - Summarization policy optimization

---

