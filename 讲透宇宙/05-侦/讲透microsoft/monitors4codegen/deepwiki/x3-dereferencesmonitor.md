<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/monitors4codegen · extra page DereferencesMonitor · fetched 2026-10-26 -->

# DereferencesMonitor

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py](src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py)
- [tests/monitor_guided_decoding/test_dereferences_monitor_java.py](tests/monitor_guided_decoding/test_dereferences_monitor_java.py)
- [tests/monitor_guided_decoding/test_dereferences_monitor_java_openai.py](tests/monitor_guided_decoding/test_dereferences_monitor_java_openai.py)

</details>



## Purpose and Scope

The `DereferencesMonitor` enforces type-valid identifier dereferencing during code generation, ensuring that when a language model generates code containing member access patterns (e.g., `object.member`), the generated member is semantically valid according to the type system. This monitor is particularly effective for languages with static typing such as Java, Rust, and potentially Python.

For information about other monitor types, see [Monitor Implementations](#3.2). For the broader Monitor-Guided Decoding framework, see [Monitor-Guided Decoding](#3).

---

## Overview

The `DereferencesMonitor` addresses a common problem in neural code generation: language models often generate syntactically plausible but semantically invalid member accesses. For example, given code like `serverNode.`, a model might generate `serverNode.invalidMethod()` when `invalidMethod` is not a member of the `serverNode` type.

The monitor intervenes at generation time by:
1. Detecting when a dot (`.`) character appears in the generated code
2. Querying the Language Server Protocol (LSP) to determine valid completions at that cursor position
3. Constraining the language model to only generate tokens that correspond to valid members

**Key Characteristics:**
- **Language Support**: Primarily Java (tested extensively), with potential for Rust and Python
- **LSP Queries**: Uses `textDocument/completion` requests
- **Constraint Scope**: Applies only after dot operators, minimal overhead otherwise
- **State-Based**: Uses a finite state machine to track when constraints should apply

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:1-245]()

---

## Architecture

### State Machine

The `DereferencesMonitor` operates as a finite state machine with three states defined in the `DecoderStates` enum:

```mermaid
stateDiagram-v2
    [*] --> UnInitialized: Monitor created
    UnInitialized --> S0: initialize() called
    UnInitialized --> Constrained: initialize() + dot detected
    
    S0 --> S0: Generate token (no dot)
    S0 --> Constrained: Dot detected + valid completions found
    S0 --> S0: Dot detected + no completions
    
    Constrained --> Constrained: Generate valid token (no break char)
    Constrained --> S0: Breaking character detected
    
    note right of UnInitialized
        Initial state before
        first maskgen() call
    end note
    
    note right of S0
        Unconstrained generation.
        Monitor waits for dot character.
    end note
    
    note right of Constrained
        Active constraint.
        Only tokens matching
        legal_completions allowed.
    end note
```

**State Descriptions:**

| State | Description | Actions |
|-------|-------------|---------|
| `UnInitialized` | Monitor has been created but not yet invoked | None |
| `S0` | Unconstrained generation, monitoring for dot operators | Returns empty blacklist |
| `Constrained` | Active constraint after detecting a dot | Returns blacklist of invalid tokens |

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:20-28](), [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:77-89]()

### Class Structure

```mermaid
classDiagram
    class Monitor {
        <<abstract>>
        +tokenizer: TokenizerWrapper
        +monitor_file_buffer: MonitorFileBuffer
        +responsible_for_file_buffer_state: bool
        +initialize(input_ids, input_text)*
        +maskgen(input_ids)* List[int]
        +update(generated_token)*
    }
    
    class DereferencesMonitor {
        +decoder_state: DecoderStates
        +all_break_chars: Set[str]
        +prompt_len: int
        +legal_completions: List[str]
        +__init__(tokenizer, monitor_file_buffer, responsible_for_file_buffer_state)
        +initialize(input_ids, input_text)
        +maskgen(input_ids) List[int]
        +pre()
        +a_phi() List[str]
        +update(generated_token)
        +find_all_break_chars(charset, language)$ Set[str]
    }
    
    class DecoderStates {
        <<enumeration>>
        UnInitialized
        S0
        Constrained
    }
    
    class MonitorFileBuffer {
        +lsp: SyncLanguageServer
        +file_path: str
        +current_lc: tuple
        +language: Language
        +gen_text: str
        +append_text(text)
    }
    
    class TokenizerWrapper {
        <<abstract>>
        +vocab_trie: Trie
        +all_token_ids: List[int]
        +tokenizer_char_set: Set[str]
        +decode(token_ids) str
    }
    
    Monitor <|-- DereferencesMonitor
    DereferencesMonitor --> DecoderStates
    DereferencesMonitor --> MonitorFileBuffer
    DereferencesMonitor --> TokenizerWrapper
```

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:30-36](), [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:20-28]()

---

## Implementation Details

### Token Masking Algorithm

The core constraint mechanism is implemented in the `maskgen()` method, which is invoked for every token to be generated. The algorithm flow:

```mermaid
flowchart TD
    A["maskgen(input_ids) called"] --> B{"decoder_state == UnInitialized?"}
    B -->|Yes| C["initialize(input_ids, input_text)"]
    B -->|No| D["Extract new generated text"]
    C --> E["Call pre()"]
    D --> F["update(new_gen_text)"]
    
    F --> G{"decoder_state == S0?"}
    G -->|Yes| E
    G -->|No| H{"decoder_state == Constrained?"}
    
    E --> I{"Last char == '.'?"}
    I -->|No| J["decoder_state = S0"]
    I -->|Yes| K["completions = a_phi()"]
    K --> L{"len(completions) > 0?"}
    L -->|No| J
    L -->|Yes| M["decoder_state = Constrained<br/>legal_completions = completions"]
    
    J --> N["Return empty blacklist"]
    H -->|Yes| O["Compute possible_token_ids<br/>from legal_completions"]
    H -->|No| N
    O --> P["blacklisted_ids = all_tokens - possible_tokens"]
    P --> Q["Return blacklisted_ids"]
    M --> O
```

**Key Steps:**

1. **Initialization (first call only)**: Records prompt length and checks for initial constraint via `pre()`
2. **Update**: Processes newly generated text and updates internal state
3. **Pre-check**: Determines if a dot operator was just generated
4. **Constraint Application**: If in `Constrained` state, computes valid token set

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:91-146]()

### LSP Integration via a_phi()

The `a_phi()` method performs static analysis to determine valid completions:

```mermaid
sequenceDiagram
    participant DM as DereferencesMonitor
    participant LSP as SyncLanguageServer
    participant LS as Language Server<br/>(e.g., Eclipse JDT.LS)
    
    DM->>DM: pre() detects dot character
    DM->>LSP: request_completions(file, line, col)
    LSP->>LS: textDocument/completion
    LS->>LS: Analyze type at cursor position
    LS-->>LSP: CompletionList (valid members)
    LSP-->>DM: legal_completions1
    
    DM->>DM: Check bracket balance
    alt Unbalanced brackets detected
        DM->>LSP: insert_text_at_position(closing_brackets)
        DM->>LSP: request_completions(file, line, col)
        LSP->>LS: textDocument/completion
        LS-->>LSP: CompletionList (with balanced code)
        LSP-->>DM: legal_completions2
        DM->>LSP: delete_text_between_positions()
    end
    
    DM->>DM: Merge completions: legal_completions1 + legal_completions2
    DM->>DM: Filter out keywords
    DM-->>DM: Return List[str] of valid identifiers
```

**Bracket Balancing Logic:**

The monitor implements sophisticated bracket balancing to handle incomplete code contexts. When the cursor position has unbalanced brackets (e.g., more opening than closing), the monitor:

1. Inserts temporary closing brackets
2. Re-queries the LSP for completions in the now-balanced context
3. Deletes the temporary brackets
4. Merges both completion sets

This ensures the LSP can properly analyze types even in syntactically incomplete code.

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:148-221]()

### Breaking Characters

The monitor uses "breaking characters" to determine when a constrained identifier has ended:

```mermaid
graph LR
    subgraph "Tokenizer Vocabulary"
        V1["Token: 'abc'"]
        V2["Token: 'abc,'"]
        V3["Token: 'abc.'"]
        V4["Token: 'abcd'"]
    end
    
    subgraph "Breaking Character Detection"
        T1["Test: 'abc' + char"]
        T2["Tokenize result"]
        T3["If first token == 'abc'<br/>then char is breaking"]
    end
    
    subgraph "Breaking Characters (examples)"
        B1["','"]
        B2["'.'"]
        B3["'('"]
        B4["')'"]
        B5["';'"]
        B6["whitespace"]
    end
    
    V1 --> T1
    T1 --> T2
    T2 --> T3
    T3 --> B1
    T3 --> B2
    T3 --> B3
    T3 --> B4
    T3 --> B5
    T3 --> B6
```

The `find_all_break_chars()` static method identifies characters that, when appended to an identifier, cause it to be tokenized separately. This is language-dependent and tokenizer-dependent.

**Usage in Constraint:**

When in `Constrained` state, the monitor allows tokens that:
1. Are prefixes of valid completions
2. Match a valid completion followed by a breaking character (e.g., `method(` when `method` is valid)

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:44-57](), [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:131-141]()

### Token Matching Strategy

```mermaid
flowchart TD
    A["For each legal_completion in legal_completions"] --> B["Check if vocab_trie has node for legal_completion"]
    B -->|Yes| C["Iterate tokens with legal_completion as prefix"]
    C --> D{"Does token contain<br/>breaking char after completion?"}
    D -->|Yes| E["Add token_id to possible_token_ids"]
    D -->|No| C
    
    B --> F["Iterate prefix tokens of legal_completion"]
    F --> G["Add token_id to possible_token_ids"]
    G --> F
    
    E --> H["Continue with next legal_completion"]
    G --> H
    H --> I["Compute blacklisted_ids = all_tokens - possible_tokens"]
```

The monitor uses a trie data structure (`vocab_trie`) to efficiently:
- Find all tokens that are prefixes of valid completions
- Find tokens that contain a valid completion followed by breaking characters

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:129-142]()

---

## Usage Examples

### HuggingFace Models Integration

Example from test suite demonstrating usage with SantaCoder model:

```mermaid
sequenceDiagram
    participant Test as test_dereferences_monitor_java_huggingface_models
    participant LSP as SyncLanguageServer
    participant FB as MonitorFileBuffer
    participant DM as DereferencesMonitor
    participant Proc as MGDLogitsProcessor
    participant Model as AutoModelForCausalLM
    
    Test->>LSP: create(config, logger, source_directory)
    Test->>LSP: start_server()
    Test->>LSP: open_file(filepath)
    Test->>LSP: delete_text_between_positions()
    
    Test->>FB: MonitorFileBuffer(lsp, filepath, pos, lang)
    Test->>DM: DereferencesMonitor(tokenizer_wrapper, filebuffer)
    Test->>Proc: MGDLogitsProcessor([monitor], event_loop)
    
    Test->>Model: generate(prompt, logits_processor=[mgd_processor])
    
    loop For each token
        Model->>Proc: __call__(input_ids, scores)
        Proc->>DM: maskgen(input_ids)
        DM->>LSP: request_completions() [if dot detected]
        LSP-->>DM: valid completions
        DM-->>Proc: blacklisted_token_ids
        Proc->>Proc: scores[blacklisted_ids] = -inf
        Proc-->>Model: modified_scores
    end
    
    Model-->>Test: generated_code
```

**Code Example:**

The test at [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:25-97]() demonstrates:

```python
# Setup: Create LSP, file buffer, and monitor
filebuffer = MonitorFileBuffer(lsp.language_server, filepath, (74, 17), (74, 17), code_language, "")
monitor = DereferencesMonitor(HFTokenizerWrapper(tokenizer), filebuffer)
mgd_logits_processor = MGDLogitsProcessor([monitor], lsp.language_server.server.loop)

# Generation with constraint
logits_processor = LogitsProcessorList([mgd_logits_processor])
generated_code = model.generate(
    prompt_tokenized,
    do_sample=False,
    max_new_tokens=30,
    logits_processor=logits_processor,
    early_stopping=True,
)
```

**Result Comparison:**

| Generation Mode | Output |
|----------------|---------|
| Without MGD | `builder()\n.hostAddress(arr[0])\n.port(Integer.parseInt(arr[1]))\n.build();` |
| With DereferencesMonitor | `newServerNode()\n.withIp(arr[0])\n.withPort(Integer.parseInt(arr[1]))\n.build();` |

The monitor correctly constrains generation to use the valid `newServerNode()` method instead of the invalid `builder()` method.

Sources: [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:25-97](), [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:74-97]()

### OpenAI Models Integration

Example demonstrating usage with OpenAI's text-davinci-003:

```mermaid
sequenceDiagram
    participant Test as test_dereferences_monitor_java_openai
    participant Client as OpenAI Client
    participant Func as openai_mgd
    participant DM as DereferencesMonitor
    participant LSP as SyncLanguageServer
    
    Test->>Client: OpenAI()
    Test->>LSP: create() and start_server()
    Test->>DM: DereferencesMonitor(TikTokenWrapper, filebuffer)
    
    Test->>Func: openai_mgd(client, model, tokenizer, prompt, monitor)
    
    loop For each token (up to num_new_tokens)
        Func->>DM: maskgen(current_tokens)
        DM->>LSP: request_completions() [if dot detected]
        LSP-->>DM: valid completions
        DM-->>Func: blacklisted_token_ids
        Func->>Func: Construct logit_bias dict (max 300 tokens)
        Func->>Client: completions.create(logit_bias={...})
        Client-->>Func: next_token
        Func->>DM: update(decoded_token)
    end
    
    Func-->>Test: generated_tokens, generated_code
```

**Code Example:**

From [tests/monitor_guided_decoding/test_dereferences_monitor_java_openai.py:23-108]():

```python
# Setup with TikToken tokenizer for OpenAI
encoding = tiktoken.encoding_for_model("text-davinci-003")
tokenizer = TikTokenWrapper(encoding)

filebuffer = MonitorFileBuffer(lsp.language_server, filepath, (74, 17), (74, 17), code_language)
monitor = DereferencesMonitor(tokenizer, filebuffer)

# Generation using openai_mgd function
gen_tokens, generated_code = openai_mgd(
    client=client,
    model=OpenAI_Models.TD3,
    tokenizer=tokenizer,
    prompt_tokenized=prompt_tokenized,
    temp=0,
    top_p=0.95,
    monitor=monitor,
    num_new_tokens=30,
)
```

Sources: [tests/monitor_guided_decoding/test_dereferences_monitor_java_openai.py:23-108]()

---

## Real-World Test Cases

The test suite uses the `clickhouse-highlevel-sinker` repository to demonstrate real-world effectiveness:

### Test Case 1: Builder Pattern Correction

**Context**: `ClickHouseDataSource.java`, line 74, after `serverNodes.add(ClickHouseServerNode.`

| Without Monitor | With Monitor |
|----------------|--------------|
| `builder()` (invalid method) | `newServerNode()` (correct factory method) |

The language server correctly identifies that `ClickHouseServerNode` does not have a `builder()` method but does have a `newServerNode()` factory method.

Sources: [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:25-97]()

### Test Case 2: Method Chaining

**Context**: Modified repository with custom `withIpPort()` method

**Prompt ends with**: `.withIpPort(`

| Without Monitor | With Monitor |
|----------------|--------------|
| `arr[0])` followed by invalid continuation | `arr[0])` followed by valid method chain |

The monitor ensures subsequent method calls in the builder chain are also valid.

Sources: [tests/monitor_guided_decoding/test_dereferences_monitor_java.py:100-240]()

---

## Configuration and Parameters

### Constructor Parameters

The `DereferencesMonitor` constructor accepts:

| Parameter | Type | Description |
|-----------|------|-------------|
| `tokenizer` | `TokenizerWrapper` | Wrapper around HuggingFace or TikToken tokenizer |
| `monitor_file_buffer` | `MonitorFileBuffer` | Manages file state and LSP communication |
| `responsible_for_file_buffer_state` | `bool` | Whether this monitor should update file buffer (default: `True`) |

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:35-36]()

### Internal State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `decoder_state` | `DecoderStates` | Current state machine state |
| `all_break_chars` | `Set[str]` | Characters that terminate identifiers |
| `prompt_len` | `int` | Length of initial prompt in tokens |
| `legal_completions` | `List[str]` | Valid identifiers when in `Constrained` state |

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:37-42]()

---

## Performance Considerations

### When Constraints Apply

The monitor has minimal overhead when:
- No dot operator is present in generated code
- The cursor position is not immediately after a dot

Heavy LSP queries only occur:
- When a dot is detected in `pre()` method
- Once per constraint activation (cached in `legal_completions`)

### LSP Query Optimization

The monitor makes at most 2 LSP completion requests per dot operator:
1. Initial request at cursor position
2. Optional second request with balanced brackets (if needed)

Both requests are asynchronous and do not block unless using `SyncLanguageServer`.

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:148-221]()

---

## Limitations and Edge Cases

### Language-Specific Behavior

1. **Java**: Fully tested and supported
2. **Rust**: Potentially supported but limited testing
3. **Python**: Dynamic typing may reduce effectiveness
4. **C#**: Not explicitly tested in provided codebase

### Known Limitations

1. **Keyword Filtering**: Keywords are filtered out from completions [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:163]() but may sometimes be valid (e.g., `class` as property name in some languages)

2. **Tokenizer Dependence**: Breaking character detection is tokenizer-specific; different tokenizers may produce different results

3. **Incomplete Code**: While bracket balancing helps, extremely malformed code may still produce incomplete LSP results

4. **Chain Length**: No inherent limit on method chain length, but LSP performance may degrade with very complex expressions

Sources: [src/monitors4codegen/monitor_guided_decoding/monitors/dereferences_monitor.py:1-245]()

---

