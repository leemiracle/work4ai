<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphageometry · page 5 Language Model Component · fetched 2026-10-26 -->

# Language Model Component

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [beam_search.py](beam_search.py)
- [decoder_stack.py](decoder_stack.py)

</details>



## Purpose and Scope

The Language Model Component provides neural augmentation capabilities for AlphaGeometry mode. When the symbolic DD+AR solver reaches saturation without proving the goal, this component proposes auxiliary geometric constructions that can unlock new reasoning paths. This page describes the high-level architecture, configuration system, and integration points between the neural model and symbolic solver.

For details on the transformer architecture itself, see [Model Architecture](#5.1). For beam search decoding algorithms, see [Beam Search Decoding](#5.2). For how auxiliary constructions are generated and validated, see [Auxiliary Construction Generation](#5.3).

Sources: [README.md:1-441](), [beam_search.py:1-464](), [decoder_stack.py:1-56]()

## Role in AlphaGeometry System

The Language Model Component serves as a learned construction oracle. It has been trained on millions of synthetic geometry problems and their solutions, learning patterns about which auxiliary constructions are useful in different geometric contexts. During proof search, when DDAR fails to solve a problem, the LM analyzes the current problem state and proposes candidate auxiliary points with associated geometric constraints.

The LM operates in an alternating loop with DDAR:
1. DDAR attempts symbolic proof search
2. If unsuccessful, LM proposes auxiliary constructions
3. Best-scoring constructions are added to the problem
4. DDAR retries with expanded problem
5. Repeat until solved or maximum depth reached

This hybrid approach combines the precision of symbolic reasoning with the intuition-like pattern recognition of neural networks.

Sources: [README.md:199-302]()

## Core Components and Code Entities

```mermaid
graph TD
    subgraph "Entry Point"
        LM_INF["lm_inference.py<br/>LanguageModelInference class"]
    end
    
    subgraph "Configuration Layer"
        GIN_PARSER["parse_gin_configuration()<br/>in lm_inference.py"]
        GIN_FILES["Gin configuration files:<br/>base_htrans.gin<br/>size/medium_150M.gin<br/>options/positions_t5.gin<br/>geometry_150M_generate.gin"]
    end
    
    subgraph "Model Architecture"
        MODELS["models.py<br/>DecoderOnlyLanguageModel<br/>DecoderOnlyLanguageModelGenerate"]
        DEC_STACK["decoder_stack.py<br/>DecoderStackGenerate"]
        TRANS_LAYER["transformer_layer.py<br/>TransformerLayerGenerate"]
    end
    
    subgraph "Inference Engine"
        BEAM["beam_search.py<br/>beam_search_flat()"]
        BEAM_STATE["BeamState dataclass"]
        TOKENS_TO_LOGITS["tokens_to_logits()<br/>forward pass function"]
    end
    
    subgraph "External Dependencies"
        MELIAD["meliad library<br/>transformer framework"]
        CKPT["ag_ckpt_vocab/<br/>model checkpoint<br/>vocabulary file"]
    end
    
    LM_INF --> GIN_PARSER
    GIN_PARSER --> GIN_FILES
    GIN_PARSER --> MODELS
    
    LM_INF --> MODELS
    MODELS --> DEC_STACK
    DEC_STACK --> TRANS_LAYER
    
    LM_INF --> BEAM
    BEAM --> BEAM_STATE
    BEAM --> TOKENS_TO_LOGITS
    TOKENS_TO_LOGITS --> MODELS
    
    MELIAD --> MODELS
    MELIAD --> GIN_FILES
    CKPT --> LM_INF
```

**Key Code Entities:**

| Entity | File | Description |
|--------|------|-------------|
| `LanguageModelInference` | lm_inference.py | Main interface class for model inference |
| `parse_gin_configuration()` | lm_inference.py | Loads and merges gin config files |
| `DecoderOnlyLanguageModel` | models.py | Transformer model implementation |
| `DecoderStackGenerate` | decoder_stack.py | Stack of decoder layers for generation |
| `TransformerLayerGenerate` | transformer_layer.py | Individual transformer layer with attention |
| `beam_search_flat()` | beam_search.py | Beam search decoding algorithm |
| `BeamState` | beam_search.py | Data structure holding beam search state |

Sources: [README.md:115-132](), [decoder_stack.py:40-56](), [beam_search.py:175-222]()

## Integration with Symbolic Solver

```mermaid
graph LR
    subgraph "Symbolic Layer"
        DDAR["ddar.py<br/>run_ddar()"]
        GRAPH["graph.py<br/>Graph object<br/>proof state"]
    end
    
    subgraph "Orchestration"
        AG["alphageometry.py<br/>beam_search_alphageometry()"]
    end
    
    subgraph "LM Component"
        ENCODE["Encode problem state<br/>to text sequence"]
        LM_INF["lm_inference.py<br/>LanguageModelInference"]
        DECODE["Decode LM output<br/>to construction predicates"]
        VALIDATE["try_translate_constrained_to_construct()"]
    end
    
    DDAR -->|"Goal not proven"| AG
    AG --> GRAPH
    GRAPH -->|"Extract state"| ENCODE
    ENCODE -->|"'a b c : T a b c d 00 ? ...'| LM_INF
    LM_INF -->|"'d = on_line d a b ; '| DECODE
    DECODE --> VALIDATE
    VALIDATE -->|"Valid construction"| GRAPH
    GRAPH -->|"Updated graph"| DDAR
```

**Integration Flow:**

1. **State Extraction**: The current proof graph is serialized into a text sequence representing known points, their relationships, and the goal
2. **Encoding**: Problem state is tokenized using SentencePiece vocabulary [README.md:120]()
3. **Generation**: Beam search generates multiple candidate construction sequences in parallel
4. **Decoding**: Raw token sequences are parsed into formal geometric predicates
5. **Validation**: Each construction is validated for geometric soundness and added to the graph if valid
6. **Retry**: DDAR attempts proof search with the augmented problem

Sources: [README.md:199-302]()

## Configuration System

The Language Model Component uses the Gin configuration library to manage model hyperparameters. Configuration is hierarchical, allowing modular specification of different aspects:

```mermaid
graph TD
    subgraph "Gin Configuration Hierarchy"
        BASE["base_htrans.gin<br/>Base transformer settings:<br/>- Activation functions<br/>- Normalization strategy<br/>- Dropout rates"]
        SIZE["size/medium_150M.gin<br/>Model size:<br/>- 152M parameters<br/>- Hidden dimension<br/>- Number of layers<br/>- Attention heads"]
        POS["options/positions_t5.gin<br/>Position encoding:<br/>- T5-style relative positions"]
        LR["options/lr_cosine_decay.gin<br/>Learning rate schedule:<br/>- Cosine decay<br/>- Warmup steps"]
        SEQ["options/seq_1024_nocache.gin<br/>Sequence settings:<br/>- Max length 1024<br/>- Cache disabled"]
        TASK["geometry_150M_generate.gin<br/>Task-specific config:<br/>- Generation mode<br/>- Output token losses<br/>- Batch size<br/>- Sequence length"]
    end
    
    BASE --> TASK
    SIZE --> TASK
    POS --> TASK
    LR --> TASK
    SEQ --> TASK
    
    TASK --> RUNTIME["Runtime Parameters<br/>via --gin_param flags"]
```

**Key Configuration Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Model size | 150M parameters | Total trainable parameters [README.md:104]() |
| Batch size | 2 (example) / 32 (paper) | Number of parallel constructions [README.md:93-94]() |
| Beam size | 2 (example) / 512 (paper) | Number of beams in beam search [README.md:94]() |
| Sequence length | 128 | Max tokens in input/output [README.md:130]() |
| Max decode length | 32 | Max tokens to generate [beam_search.py:40]() |

**Configuration Flags in Command Line:**

```
LM_ARGS=(
  --ckpt_path=$DATA \
  --vocab_path=$DATA/geometry.757.model
  --gin_search_paths=$MELIAD_PATH/transformer/configs,$(pwd) \
  --gin_file=base_htrans.gin \
  --gin_file=size/medium_150M.gin \
  --gin_file=options/positions_t5.gin \
  --gin_file=options/lr_cosine_decay.gin \
  --gin_file=options/seq_1024_nocache.gin \
  --gin_file=geometry_150M_generate.gin \
  --gin_param=DecoderOnlyLanguageModelGenerate.output_token_losses=True \
  --gin_param=TransformerTaskConfig.batch_size=$BATCH_SIZE \
  --gin_param=TransformerTaskConfig.sequence_length=128 \
  --gin_param=Trainer.restore_state_variables=False
);
```

Sources: [README.md:115-132](), [beam_search.py:35-44]()

## Input Format: Problem State Encoding

The LM receives the current proof state as a text sequence with specific syntax:

**Format Structure:**
```
{S} <points> : <predicates> ? <goal> {F1} x00
```

**Components:**
- `{S}`: Start-of-sequence token
- Points: Space-separated point names (e.g., `a b c d`)
- Predicates: Numbered geometric relationships (e.g., `T a b c d 00` for perpendicularity)
- `?`: Separator before goal
- Goal: Target predicate to prove
- `{F1}`: Marker indicating auxiliary construction needed
- `x00`: Depth marker

**Example from README:**
```
{S} a : ; b : ; c : ; d : T a b c d 00 T a c b d 01 ? T a d b c {F1} x00
```

This encodes:
- Points: a, b, c, d
- Known facts: `T a b c d 00` (perpendicularity), `T a c b d 01`
- Goal: `T a d b c` (perpendicularity to prove)
- Request: Auxiliary construction needed (depth 0)

Sources: [README.md:233-234]()

## Output Format: Construction Proposals

The LM outputs auxiliary construction specifications in a structured format:

**Format Structure:**
```
<point> : <predicate1> <predicate2> ... ;
```

**Examples from README:**

1. **Intersection of line and circle:**
   ```
   e : C a c e 02 C b d e 03 ;
   ```
   Translation: `e = on_line e a c, on_line e b d`
   
2. **Equidistance construction:**
   ```
   e = eqdistance e c a b, eqdistance e b a c
   ```
   Translation: construct E as intersection of circle(center=C, radius=AB) and circle(center=B, radius=AC)

**Scoring:**
Each construction receives a score from beam search (log probability divided by brevity penalty). Higher scores indicate more likely constructions. The beam search generates multiple candidates ranked by score:
- First candidate: score = -1.186
- Second candidate: score = -1.102 (better, tried first)

Sources: [README.md:238-240](), [README.md:290-300](), [beam_search.py:47-60]()

## Model Initialization

The Language Model Component is initialized during the AlphaGeometry startup phase:

```mermaid
sequenceDiagram
    participant Main as alphageometry.py
    participant Parser as parse_gin_configuration
    participant LM as LanguageModelInference
    participant Model as DecoderOnlyLanguageModel
    participant Ckpt as Checkpoint Files
    
    Main->>Parser: Load gin configurations
    Parser->>Parser: Merge base_htrans.gin
    Parser->>Parser: Merge size/medium_150M.gin
    Parser->>Parser: Merge options/*.gin
    Parser->>Parser: Apply --gin_param overrides
    Parser-->>Main: Configuration object
    
    Main->>LM: Initialize(config, vocab_path, ckpt_path)
    LM->>Ckpt: Load vocabulary (geometry.757.model)
    LM->>Model: Create model from config
    Model->>Model: Initialize 152M parameters
    LM->>Ckpt: Load checkpoint weights
    LM-->>Main: Ready for inference
    
    Note over Main,LM: Model loaded in memory<br/>Ready for beam search
```

**Initialization Steps:**

1. **Parse Configuration** [README.md:117-127](): Load and merge gin files
2. **Load Vocabulary**: Read SentencePiece model [README.md:120]()
3. **Create Model**: Instantiate transformer with 152M parameters [README.md:224]()
4. **Load Checkpoint**: Restore trained weights from `ag_ckpt_vocab/` [README.md:119]()
5. **Prepare for Generation**: Set up beam search parameters [README.md:129]()

Sources: [README.md:115-132](), [README.md:223-225]()

## Inference Process

During proof search, the LM performs inference through beam search:

```mermaid
graph TD
    START["Input: Encoded problem state"]
    
    INIT["Initialize BeamState<br/>beam_init()"]
    SEED["Seed token: start of sequence"]
    CACHE["Initialize transformer cache"]
    
    LOOP_START["Beam search loop iteration"]
    SLICE["Extract current position tokens<br/>lax.dynamic_slice()"]
    FLATTEN["Flatten beam dimension<br/>flatten_beam_dim()"]
    
    FORWARD["Forward pass<br/>tokens_to_logits()"]
    LOGITS["Get next-token logits"]
    
    UNFLATTEN["Unflatten beam dimension<br/>unflatten_beam_dim()"]
    LOGPROBS["Compute log probabilities<br/>jax.nn.log_softmax()"]
    MASK["Apply vocabulary mask"]
    
    TOPK["Select top-2k candidates<br/>lax.top_k()"]
    UPDATE["Update sequences with new tokens"]
    
    CHECK_EOS{"Reached<br/>end-of-sequence?"}
    FINISHED["Move to finished beams"]
    LIVE["Keep in live beams"]
    
    BREVITY["Apply brevity penalty<br/>brevity_penalty()"]
    BEST["Select top-k by score"]
    
    LOOP_COND{"Continue?<br/>not at max_len<br/>and search active"}
    
    OUTPUT["Output: Top beam sequences<br/>and scores"]
    
    START --> INIT
    INIT --> SEED
    INIT --> CACHE
    
    SEED --> LOOP_START
    CACHE --> LOOP_START
    
    LOOP_START --> SLICE
    SLICE --> FLATTEN
    FLATTEN --> FORWARD
    FORWARD --> LOGITS
    LOGITS --> UNFLATTEN
    UNFLATTEN --> LOGPROBS
    LOGPROBS --> MASK
    MASK --> TOPK
    TOPK --> UPDATE
    
    UPDATE --> CHECK_EOS
    CHECK_EOS -->|Yes| FINISHED
    CHECK_EOS -->|No| LIVE
    
    FINISHED --> BREVITY
    LIVE --> BREVITY
    BREVITY --> BEST
    
    BEST --> LOOP_COND
    LOOP_COND -->|Yes| LOOP_START
    LOOP_COND -->|No| OUTPUT
```

**Key Functions:**

| Function | File | Purpose |
|----------|------|---------|
| `beam_init()` | beam_search.py:194-221 | Initialize beam search state with seed token |
| `flatten_beam_dim()` | beam_search.py:93-97 | Flatten batch and beam dimensions for model |
| `tokens_to_logits()` | beam_search.py:243 | Forward pass through transformer |
| `unflatten_beam_dim()` | beam_search.py:100-105 | Restore beam dimension after forward pass |
| `brevity_penalty()` | beam_search.py:47-60 | Score adjustment favoring longer sequences |
| `gather_topk_beams()` | beam_search.py:140-156 | Select best-scoring beams |

Sources: [beam_search.py:1-464](), [README.md:227-301]()

## Beam State Management

The `BeamState` dataclass tracks all information needed during beam search:

```python
@flax.struct.dataclass
class BeamState:
  cur_index: jax.Array          # Current decode position
  live_logprobs: jax.Array      # [batch_size, beam_size] log probs
  finished_scores: jax.Array    # [batch_size, beam_size] final scores
  live_seqs: jax.Array          # [batch_size, beam_size, max_len] active
  finished_seqs: jax.Array      # [batch_size, beam_size, max_len] complete
  finished_flags: jax.Array     # [batch_size, beam_size] completion flags
  cache: Any                    # Transformer attention cache
```

**State Evolution:**

1. **Initialization** [beam_search.py:194-221](): Start with single active beam per batch
2. **Expansion**: Expand to `beam_size` beams (e.g., 512) [README.md:94]()
3. **Iteration**: Each step generates `beam_size * vocab_size` candidates
4. **Selection**: Keep top `beam_size` active and top `beam_size` finished
5. **Termination**: Stop when all beams finish or max length reached

Sources: [beam_search.py:175-192]()

## Dependencies and External Libraries

The Language Model Component relies on several external libraries:

```mermaid
graph TD
    subgraph "Core Dependencies"
        JAX["JAX<br/>Numerical computation<br/>JIT compilation"]
        FLAX["Flax<br/>Neural network framework<br/>struct.dataclass"]
        NUMPY["NumPy/JNP<br/>Array operations"]
    end
    
    subgraph "Transformer Framework"
        MELIAD["Meliad<br/>Google Research library<br/>transformer configs"]
        GIN["Gin<br/>Configuration management<br/>@gin.configurable"]
    end
    
    subgraph "Text Processing"
        SENTENCEPIECE["SentencePiece<br/>Tokenization<br/>vocabulary model"]
    end
    
    subgraph "LM Component"
        LM_INF["lm_inference.py"]
        MODELS["models.py"]
        BEAM["beam_search.py"]
        DEC_STACK["decoder_stack.py"]
    end
    
    JAX --> BEAM
    JAX --> MODELS
    FLAX --> BEAM
    NUMPY --> BEAM
    
    MELIAD --> MODELS
    MELIAD --> DEC_STACK
    GIN --> MODELS
    GIN --> DEC_STACK
    
    SENTENCEPIECE --> LM_INF
    
    MELIAD --> LM_INF
    JAX --> LM_INF
```

**Installation Requirements:**

The Meliad library is not registered with pip and must be manually installed:

```bash
MELIAD_PATH=meliad_lib/meliad
mkdir -p $MELIAD_PATH
git clone https://github.com/google-research/meliad $MELIAD_PATH
export PYTHONPATH=$PYTHONPATH:$MELIAD_PATH
```

**Note:** The DDAR solver can run without these dependencies by disabling the LM inference import in alphageometry.py [README.md:137-138]()

Sources: [README.md:23-34](), [README.md:63-71](), [README.md:399-413]()

## Performance Characteristics

The Language Model Component has significant computational requirements:

**Model Size:**
- Parameters: 152,072,288 (152M) [README.md:223]()
- Architecture: Decoder-only transformer

**Hardware Requirements (Paper Settings):**
- GPUs: 4 V100 GPUs for model inference [README.md:106]()
- CPUs: 250 CPU workers for DDAR [README.md:106-107]()
- Purpose: Stay under IMO time limits [README.md:106]()

**Inference Parameters:**
- Batch size: 32 (generates 32 constructions in parallel) [README.md:104]()
- Beam size: 512 (maintains 512 hypotheses) [README.md:104]()
- Search depth: 16 (maximum auxiliary construction iterations) [README.md:105]()

**Simplified Settings:**
The repository examples use lightweight values for demonstration:
- Batch size: 2
- Beam size: 2  
- Depth: 2

Sources: [README.md:93-109](), [README.md:223-225]()

## Limitations and Optimizations

**Current Implementation:**

The released implementation removes several optimizations present in the research system:

1. **Parallelization Removed** [README.md:279-287]():
   - No multi-GPU model inference
   - No multi-CPU DDAR parallelization
   - No parallel execution of LM and DDAR
   - No shared CPU worker pool across problems

2. **Simplifications for Clarity** [README.md:286-287]():
   - Memory optimizations removed
   - Speed optimizations stripped
   - Code abstractions reduced

**Reproducibility Note:**

There is a known issue where different users may observe different LM scores for the same inputs, though the top beam decodes remain consistent [README.md:312]()

Sources: [README.md:279-312]()

---

