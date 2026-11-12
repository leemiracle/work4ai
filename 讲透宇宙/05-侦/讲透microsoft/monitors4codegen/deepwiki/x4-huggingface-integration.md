<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/monitors4codegen · extra page HuggingFace Integration · fetched 2026-10-26 -->

# HuggingFace Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/monitors4codegen/monitor_guided_decoding/hf_gen.py](src/monitors4codegen/monitor_guided_decoding/hf_gen.py)
- [tests/monitor_guided_decoding/test_dereferences_monitor_java.py](tests/monitor_guided_decoding/test_dereferences_monitor_java.py)

</details>



## Purpose and Scope

This page explains how Monitor-Guided Decoding integrates with HuggingFace transformers models through the `MGDLogitsProcessor` class. It covers the architecture, token masking mechanism, and usage patterns for applying monitors to HuggingFace language models during code generation.

For integration with OpenAI models, see [OpenAI Integration](#3.3.2). For general monitor concepts, see [Core Concepts](#3.1).

---

## Architecture Overview

The HuggingFace integration is implemented through `MGDLogitsProcessor`, which extends the `LogitsProcessor` interface from the `transformers` library. This design allows monitors to seamlessly integrate with HuggingFace's standard generation pipeline by modifying token logits before sampling.

```mermaid
graph TB
    subgraph "HuggingFace Model Pipeline"
        Model["AutoModelForCausalLM"]
        Generate["model.generate()"]
        Tokenizer["AutoTokenizer"]
    end
    
    subgraph "MGD Integration Layer"
        MGDProc["MGDLogitsProcessor<br/>(LogitsProcessor)"]
        Wrapper["HFTokenizerWrapper"]
        EventLoop["asyncio.AbstractEventLoop"]
    end
    
    subgraph "Monitor Layer"
        Monitors["List[Monitor]"]
        MonitorInterface["Monitor.maskgen()"]
    end
    
    subgraph "LSP Layer"
        FileBuffer["MonitorFileBuffer"]
        LSP["SyncLanguageServer"]
    end
    
    Tokenizer --> Wrapper
    Model --> Generate
    Generate -->|"logits_processor parameter"| MGDProc
    Wrapper --> MGDProc
    EventLoop --> MGDProc
    
    MGDProc -->|"queries each"| Monitors
    Monitors -->|"calls"| MonitorInterface
    MonitorInterface -->|"uses"| FileBuffer
    FileBuffer -->|"queries"| LSP
    
    MGDProc -->|"returns modified logits"| Generate
```

**Sources:** [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:1-66](), [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:1-241]()

---

## MGDLogitsProcessor Class

The `MGDLogitsProcessor` class is the core component that bridges HuggingFace models with the monitoring framework.

### Class Structure

| Component | Type | Purpose |
|-----------|------|---------|
| `monitors` | `List[Monitor]` | List of monitor instances to apply during generation |
| `loop` | `AbstractEventLoop` | Event loop for asynchronous monitor queries |

**Key Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `monitors: List[Monitor]`<br/>`loop: Union[None, AbstractEventLoop]` | `None` | Initializes processor with monitors and event loop |
| `__call__` | `input_ids: torch.LongTensor`<br/>`scores: torch.FloatTensor` | `torch.FloatTensor` | Called by HuggingFace during generation; modifies logits |
| `process_scores_for_single_input_id` | `segment_idx: int`<br/>`input_ids: torch.LongTensor`<br/>`scores: torch.FloatTensor` | `torch.FloatTensor` | Processes logits for a single sequence |

**Sources:** [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:13-66]()

---

## Token Masking Mechanism

The logits processor implements token masking by setting the scores of blacklisted tokens to negative infinity, effectively preventing their selection during sampling.

```mermaid
sequenceDiagram
    participant Generate as "model.generate()"
    participant MGDProc as "MGDLogitsProcessor"
    participant Monitor as "Monitor.maskgen()"
    participant LSP as "Language Server"
    
    Note over Generate: For each token position
    Generate->>MGDProc: __call__(input_ids, scores)
    Note over MGDProc: input_ids shape: (batch_size, seq_len)<br/>scores shape: (batch_size, vocab_size)
    
    loop For each sequence in batch
        MGDProc->>MGDProc: process_scores_for_single_input_id()
        MGDProc->>Monitor: maskgen(input_ids.tolist())
        Monitor->>LSP: Query valid completions
        LSP-->>Monitor: Valid tokens
        Monitor-->>MGDProc: blacklisted_ids: List[int]
        MGDProc->>MGDProc: Set scores[blacklisted_ids] = -inf
    end
    
    MGDProc-->>Generate: modified_scores
    Generate->>Generate: Sample next token
```

The masking logic is implemented at [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:36-42]():

```python
blacklisted_ids: List[int] = await self.monitors[segment_idx].maskgen(input_ids.tolist())
output_scores: torch.FloatTensor = torch.where(
    torch.tensor([True if i in blacklisted_ids else False for i in range(scores.shape[0])]).to(scores.device),
    float("-inf") * torch.ones(scores.shape[0]).to(scores.device),
    scores,
).to(scores)
```

**Sources:** [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:30-42]()

---

## Event Loop Handling

Since monitors perform asynchronous LSP queries, `MGDLogitsProcessor` manages an event loop to handle concurrent monitor operations.

### Synchronization Strategy

The processor uses `asyncio.run_coroutine_threadsafe()` to execute asynchronous monitor queries from the synchronous HuggingFace generation context:

```mermaid
graph LR
    HFThread["HuggingFace Generation<br/>(Main Thread)"]
    MGDCall["MGDLogitsProcessor.__call__()<br/>(Synchronous)"]
    AsyncFunc["async def f()<br/>(Coroutine)"]
    EventLoop["asyncio.AbstractEventLoop<br/>(Background Thread)"]
    MonitorQueries["Monitor.maskgen() queries<br/>(Async I/O)"]
    
    HFThread --> MGDCall
    MGDCall -->|"asyncio.run_coroutine_threadsafe()"| AsyncFunc
    AsyncFunc -->|"submits to"| EventLoop
    EventLoop -->|"executes"| MonitorQueries
    MonitorQueries -->|"returns"| EventLoop
    EventLoop -->|"future.result()"| MGDCall
    MGDCall --> HFThread
```

Implementation at [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:54-65]():

| Step | Code Component | Purpose |
|------|---------------|---------|
| 1 | `async def f()` | Creates coroutine that gathers monitor results |
| 2 | `asyncio.gather(*new_score_coroutines)` | Executes all monitor queries concurrently |
| 3 | `asyncio.run_coroutine_threadsafe()` | Submits coroutine to event loop |
| 4 | `future.result()` | Blocks until all monitors complete |
| 5 | `torch.stack(results)` | Combines modified scores into tensor |

**Sources:** [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:44-65]()

---

## Usage Example

### Basic Setup

The following example demonstrates setting up MGD with HuggingFace models for Java code generation with the `DereferencesMonitor`:

```python
# Model and tokenizer initialization
model = AutoModelForCausalLM.from_pretrained("bigcode/santacoder", trust_remote_code=True).to(device)
tokenizer = AutoTokenizer.from_pretrained("bigcode/santacoder")

# Language server and file buffer setup
lsp = SyncLanguageServer.create(config, logger, source_directory)
with lsp.start_server():
    with lsp.open_file(filepath):
        filebuffer = MonitorFileBuffer(lsp.language_server, filepath, cursor_pos, cursor_pos, Language.JAVA, "")
        
        # Monitor and processor initialization
        monitor = DereferencesMonitor(HFTokenizerWrapper(tokenizer), filebuffer)
        mgd_logits_processor = MGDLogitsProcessor([monitor], lsp.language_server.server.loop)
        
        # Generation with MGD
        logits_processor = LogitsProcessorList([mgd_logits_processor])
        generated_code = model.generate(
            prompt_tokenized,
            do_sample=False,
            max_new_tokens=30,
            logits_processor=logits_processor,
            early_stopping=True
        )
```

**Sources:** [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:38-97]()

---

## Integration with HuggingFace generate()

### LogitsProcessorList Configuration

`MGDLogitsProcessor` is passed to `model.generate()` via the `logits_processor` parameter, which accepts a `LogitsProcessorList`:

```mermaid
graph TB
    User["User Code"]
    LPL["LogitsProcessorList"]
    MGDProc["MGDLogitsProcessor"]
    Generate["model.generate()"]
    GenLoop["Generation Loop"]
    
    User -->|"creates"| MGDProc
    MGDProc -->|"wrapped in"| LPL
    LPL -->|"logits_processor parameter"| Generate
    
    subgraph "Inside model.generate()"
        Generate --> GenLoop
        GenLoop -->|"for each token"| CallProc["Call each processor"]
        CallProc -->|"invokes"| MGDProc
        MGDProc -->|"returns modified logits"| CallProc
        CallProc --> Sample["Sample from distribution"]
        Sample --> GenLoop
    end
```

### Generation Parameters

| Parameter | Recommended Value | Purpose |
|-----------|------------------|---------|
| `logits_processor` | `LogitsProcessorList([mgd_logits_processor])` | Applies monitor constraints |
| `do_sample` | `False` or `True` | Greedy decoding recommended for determinism |
| `max_new_tokens` | Task-dependent | Controls generation length |
| `early_stopping` | `True` | Stops at natural completion points |

**Sources:** [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:84-91]()

---

## Multi-Monitor Support

`MGDLogitsProcessor` supports multiple monitors operating simultaneously. Each monitor in the list corresponds to a sequence in the batch:

### Batch Processing

```mermaid
graph TB
    InputIDs["input_ids<br/>shape: (batch_size, seq_len)"]
    Scores["scores<br/>shape: (batch_size, vocab_size)"]
    
    subgraph "Parallel Processing"
        Mon0["monitors[0].maskgen()<br/>(sequence 0)"]
        Mon1["monitors[1].maskgen()<br/>(sequence 1)"]
        MonN["monitors[n].maskgen()<br/>(sequence n)"]
        
        Score0["scores[0] modified"]
        Score1["scores[1] modified"]
        ScoreN["scores[n] modified"]
    end
    
    OutputScores["output_scores<br/>shape: (batch_size, vocab_size)"]
    
    InputIDs --> Mon0
    InputIDs --> Mon1
    InputIDs --> MonN
    
    Scores --> Score0
    Scores --> Score1
    Scores --> ScoreN
    
    Mon0 -->|"blacklist"| Score0
    Mon1 -->|"blacklist"| Score1
    MonN -->|"blacklist"| ScoreN
    
    Score0 --> OutputScores
    Score1 --> OutputScores
    ScoreN --> OutputScores
```

**Assertion Requirements:**

- `input_ids.shape[0]` must equal `len(self.monitors)`
- Each monitor processes one sequence independently

**Sources:** [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:50-60]()

---

## Comparison: With vs Without MGD

The test suite demonstrates the effectiveness of MGD by comparing generation with and without the logits processor:

### Example from Test Suite

| Configuration | Generated Code | Correctness |
|--------------|----------------|-------------|
| **Without MGD** | `.builder()`<br/>`.hostAddress(arr[0])` | ❌ Invalid method names |
| **With MGD** | `.newServerNode()`<br/>`.withIp(arr[0])` | ✅ Valid LSP-verified methods |

The test at [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:74-97]() shows:

1. **Baseline generation** (lines 74-81): Produces syntactically plausible but semantically invalid method calls
2. **MGD generation** (lines 84-97): Produces only methods that exist according to the language server

**Sources:** [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:25-97]()

---

## Component Dependencies

The HuggingFace integration requires several components to work together:

```mermaid
graph TB
    MGDProc["MGDLogitsProcessor"]
    
    subgraph "Required Dependencies"
        Monitors["Monitor instances<br/>(DereferencesMonitor, etc.)"]
        TokenWrapper["HFTokenizerWrapper"]
        HFTokenizer["AutoTokenizer"]
        EventLoop["asyncio.AbstractEventLoop"]
        FileBuffer["MonitorFileBuffer"]
        LSP["SyncLanguageServer"]
    end
    
    subgraph "HuggingFace Components"
        Model["AutoModelForCausalLM"]
        TransTokenizer["transformers.AutoTokenizer"]
        GenerateAPI["model.generate()"]
    end
    
    MGDProc -->|"requires"| Monitors
    MGDProc -->|"requires"| EventLoop
    
    Monitors -->|"requires"| TokenWrapper
    Monitors -->|"requires"| FileBuffer
    
    TokenWrapper -->|"wraps"| HFTokenizer
    HFTokenizer -.is instance of.-> TransTokenizer
    
    FileBuffer -->|"requires"| LSP
    
    MGDProc -->|"plugs into"| GenerateAPI
    Model -->|"provides"| GenerateAPI
```

**Initialization Order:**

1. Initialize `AutoModelForCausalLM` and `AutoTokenizer`
2. Create `SyncLanguageServer` and open files
3. Create `MonitorFileBuffer` with file context
4. Wrap tokenizer in `HFTokenizerWrapper`
5. Initialize monitor instances with wrapper and file buffer
6. Create `MGDLogitsProcessor` with monitors and event loop
7. Pass processor to `model.generate()`

**Sources:** [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:38-97](), [src/monitors4codegen/monitor_guided_decoding/hf_gen.py:20-26]()

---

