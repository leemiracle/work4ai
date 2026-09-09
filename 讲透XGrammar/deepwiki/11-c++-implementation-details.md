> 来源: [https://deepwiki.com/mlc-ai/xgrammar/11-c++-implementation-details](https://deepwiki.com/mlc-ai/xgrammar/11-c++-implementation-details)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# C++ Implementation Details

  Relevant source files 
 - [cpp/earley_parser.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc)
 - [cpp/earley_parser.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h)
 - [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc)
 - [include/xgrammar/xgrammar.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h)
 - [tests/python/test_grammar_matcher_ebnf.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_ebnf.py)
 
  
## Purpose and Scope

 This section provides technical documentation for developers working on the C++ core of XGrammar. It covers the internal implementation architecture, key data structures, memory management patterns, and integration points between components.

 For high-level system architecture and data flow, see [System Architecture](https://deepwiki.com/mlc-ai/xgrammar/10-system-architecture). For Python API details, see [Python API Reference](https://deepwiki.com/mlc-ai/xgrammar/3-python-api-reference). For specific implementation topics, see the child pages:

 
 - [Grammar Internal Representation](https://deepwiki.com/mlc-ai/xgrammar/11.1-grammar-internal-representation) - CSR format, GrammarBuilder
 - [FSM Implementation](https://deepwiki.com/mlc-ai/xgrammar/11.2-fsm-implementation) - FSM operations and transformations
 - [GrammarMatcher Internal Architecture](https://deepwiki.com/mlc-ai/xgrammar/11.3-grammarmatcher-internal-architecture) - Earley parser internals
 - [Python Bindings with nanobind](https://deepwiki.com/mlc-ai/xgrammar/11.4-python-bindings-with-nanobind) - Binding layer details
 - [Serialization and Persistence](https://deepwiki.com/mlc-ai/xgrammar/11.5-serialization-and-persistence) - JSON serialization
 - [Memory Management and Safety](https://deepwiki.com/mlc-ai/xgrammar/11.6-error-handling-and-result-types) - PIMPL pattern, shared_ptr usage
 
 **Sources:** [include/xgrammar/xgrammar.h1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L1-L18)

 
---

 
## Core Header Organization

 The C++ implementation is organized into a modular header structure under `include/xgrammar/`. The main entry point [xgrammar.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/xgrammar.h) aggregates all public APIs:

 
| Header File | Primary Classes/APIs | Purpose |
|---|---|---|
| grammar.h | Grammar, GrammarBuilder | Grammar representation and construction |
| compiler.h | GrammarCompiler, CompiledGrammar | Grammar optimization and compilation |
| matcher.h | GrammarMatcher | Runtime token matching and validation |
| tokenizer_info.h | TokenizerInfo | Tokenizer vocabulary and metadata |
| config.h | Configuration constants | Build-time configuration |
| exception.h | XGrammarError | Exception types |

 The implementation files reside in `cpp/` with corresponding `.cc` files for each header, plus internal utilities in subdirectories.

 **Diagram 1: Header Dependency Graph**

 
```

```

 **Sources:** [include/xgrammar/xgrammar.h10-15](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L10-L15)

 
---

 
## Component Implementation Architecture

 The C++ implementation follows a PIMPL (Pointer to Implementation) pattern for all major classes, providing ABI stability and encapsulation. Each public class has a nested `Impl` class that holds the actual implementation.

 **Diagram 2: Core Component Class Structure**

 
```

```

 **Key Implementation Patterns:**

 
 - **PIMPL Pattern**: All public classes hold a `std::shared_ptr<Impl>` member, enabling safe copying and reference counting
 - **Inheritance**: `GrammarMatcher::Impl` inherits from `EarleyParser` to implement the core parsing algorithm
 - **Immutability**: Compiled structures (Grammar, CompiledGrammar) are immutable after construction
 - **State Management**: `ParserState` structs track parsing position with fields: `rule_id`, `sequence_id`, `element_id`, `rule_start_pos`, `sub_element_id`, `repeat_count`
 - **Cycle Detection**: `RepeatDetector` prevents infinite loops during prediction with adaptive vector/set storage
 
 **Sources:** [cpp/grammar_matcher.cc332-420](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L332-L420) [cpp/earley_parser.h23-130](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L23-L130) [cpp/earley_parser.cc219-238](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L219-L238)

 
---

 
## Component Interaction Flow

 The following diagram shows how the major C++ components interact during typical usage:

 **Diagram 3: Runtime Token Acceptance Flow**

 
```

```

 **Key Method Responsibilities:**

 
| Method | Responsibility | Returns |
|---|---|---|
| GrammarMatcher::Impl::AcceptToken() | Validates token against grammar, advances parser state | bool (accepted/rejected) |
| EarleyParser::Advance() | Processes single byte, performs Scan → Predict → Complete cycle | bool (accepted/rejected) |
| EarleyParser::Scan() | Matches byte against current parser states, generates new states | void (updates queue) |
| EarleyParser::Predict() | Expands rule references, handles epsilon transitions | pair<bool, bool> (scanable, completable) |
| EarleyParser::Complete() | Handles rule completion, advances parent states | void (enqueues parent states) |
| RepeatDetector::IsVisited() | Prevents infinite loops during prediction | bool (visited/not visited) |

 **Sources:** [cpp/grammar_matcher.cc491-555](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L491-L555) [cpp/earley_parser.cc251-287](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L251-L287) [cpp/earley_parser.cc210-238](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L210-L238) [cpp/earley_parser.h385-401](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L385-L401)

 
---

 
## Key Data Structures Overview

 The following table summarizes the core data structures used throughout the C++ implementation:

 
| Data Structure | Location | Purpose | Key Fields/Methods |
|---|---|---|---|
| ParserState | cpp/earley_parser.h41-130 | Earley parser state | rule_id, sequence_id, element_id, rule_start_pos, sub_element_id, repeat_count, partial_codepoint |
| RepeatDetector | cpp/earley_parser.h187-217 | Cycle detection during prediction | visited_vector_, visited_set_, IsVisited(), Insert(), Clear() |
| EarleyParser | cpp/earley_parser.h219-482 | Core parsing algorithm | scanable_state_history_, rule_id_to_completable_states_, Advance(), Predict(), Scan(), Complete() |
| GrammarMatcher::Impl | cpp/grammar_matcher.cc332-420 | Token matching engine | compiled_grammar_, tokenizer_info_, token_length_history, AcceptToken(), FillNextTokenBitmask() |
| Grammar::Impl CSR | cpp/grammar_impl.h | Compact rule storage | rules_, expr_data_ (CSR format) |
| AdaptiveTokenMask | cpp/compiled_grammar_impl.h | Precomputed token masks | accepted_bitset, rejected_indices, uncertain_indices, StoreType enum |
| Compact2DArray<T> | cpp/earley_parser.h248-254 | 2D array with history | PushBack(), PopBack(), operator[] for row access |
| DynamicBitset | cpp/grammar_matcher.cc35-36 | Token bitmask operations | GetBufferSize(), FindFirstZero(), FindNextZero(), Set(), Count() |

 Detailed documentation for each structure is provided in the respective child pages.

 **Sources:** [cpp/earley_parser.h1-486](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L1-L486) [cpp/grammar_matcher.cc1-467](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L1-L467)

 
---

 
## Memory Management Model

 XGrammar uses a consistent memory management approach across all components:

 **Diagram 4: Memory Ownership Model**

 
```

```

 **Key Points:**

 
 - All public objects are **copyable and cheap** (copying a `shared_ptr` is O(1))
 - **Immutable structures** (Grammar, CompiledGrammar) can be safely shared across threads
 - **Mutable structures** (GrammarMatcher) provide per-instance state isolation
 - **Cache management** handles memory pressure automatically via LRU eviction
 
 For detailed memory safety guarantees, see [Memory Management and Safety](https://deepwiki.com/mlc-ai/xgrammar/11.6-error-handling-and-result-types).

 **Sources:** [include/xgrammar/xgrammar.h1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L1-L18)

 
---

 
## Thread Safety Guarantees

 
| Component | Thread Safety | Mutable State |
|---|---|---|
| Grammar | Thread-safe (immutable) | None after construction |
| CompiledGrammar | Thread-safe (immutable) | None after construction |
| GrammarCompiler | Thread-safe | ThreadSafeLRUCache with mutex protection |
| GrammarMatcher | Not thread-safe | scanable_state_history_, token_length_history, stop_token_is_accepted_ |
| EarleyParser | Not thread-safe | scanable_state_history_, rule_id_to_completable_states_, is_completed_ |
| RepeatDetector | Not thread-safe | visited_vector_, visited_set_, size_ |
| TokenizerInfo | Thread-safe (immutable) | None after construction |
| BatchGrammarMatcher | Thread-safe | Uses ThreadPool for parallel processing of independent matchers |

 **Parallel Usage Pattern:**

 
```

```

 **Mutable State in GrammarMatcher:**

 
 - `scanable_state_history_` ([cpp/earley_parser.h254](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L254-L254)) - grows with each `Advance()` call
 - `rule_id_to_completable_states_` ([cpp/earley_parser.h248](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L248-L248)) - tracks parent states for completion
 - `token_length_history` ([cpp/grammar_matcher.cc414](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L414-L414)) - enables rollback
 - `stop_token_is_accepted_` ([cpp/earley_parser.h269](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L269-L269)) - terminal state flag
 
 **Sources:** [cpp/earley_parser.h219-270](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L219-L270) [cpp/grammar_matcher.cc332-420](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L332-L420) [cpp/grammar_matcher.cc422-466](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L422-L466)

 
---

 
## Build Configuration and Compilation

 The C++ implementation is configured through CMake with optional features:

 
| CMake Option | Default | Effect |
|---|---|---|
| XGRAMMAR_ENABLE_TORCH | OFF | Enable PyTorch kernel support |
| XGRAMMAR_BUILD_PYTHON | ON | Build Python bindings via nanobind |
| XGRAMMAR_BUILD_TESTS | ON | Build C++ test suite |
| CMAKE_BUILD_TYPE | Release | Controls optimization level |

 **Compiler Requirements:**

 
 - C++17 standard required
 - GCC ≥ 7.5, Clang ≥ 7.0, MSVC ≥ 2019
 - OpenMP support (optional, for parallel compilation)
 
 For detailed build instructions, see [Build System Configuration](https://deepwiki.com/mlc-ai/xgrammar/12.1-build-system-and-configuration).

 **Sources:** [include/xgrammar/xgrammar.h1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L1-L18)

 
---

 
## Implementation File Organization

 The C++ implementation files are organized in the `cpp/` directory:

 
```
cpp/
├── grammar_matcher.cc      # GrammarMatcher::Impl, token acceptance
├── earley_parser.cc        # EarleyParser algorithm implementation
├── earley_parser.h         # ParserState, RepeatDetector, EarleyParser
├── compiled_grammar_impl.h # CompiledGrammar::Impl, AdaptiveTokenMask
├── grammar_impl.h          # Grammar::Impl CSR storage
├── grammar.cc              # Grammar class and builder
├── grammar_builder.cc      # GrammarBuilder implementation
├── grammar_functor.cc      # Transformation functors
├── compiler.cc             # GrammarCompiler and caching
├── tokenizer_info.cc       # TokenizerInfo implementation
├── json_schema_converter.cc # JSON Schema → EBNF
├── regex_converter.cc      # Regex → EBNF
├── structural_tag_converter.cc # Structural tags
├── ebnf_parser.cc          # EBNF parsing
├── support/                # Utility implementations
│   ├── fsm.h               # FSM, CompactFSM, FSMWithStartEnd
│   ├── compact_2d_array.h  # Compact2DArray template
│   ├── dynamic_bitset.h    # DynamicBitset operations
│   ├── thread_pool.h       # ThreadPool for parallel compilation
│   ├── logging.h           # XGRAMMAR_LOG, XGRAMMAR_CHECK
│   └── utils.h             # HashCombine, XGRAMMAR_MEMBER_ARRAY
└── pybind/
    └── nanobind.cc         # Python bindings
```

 **Diagram 5: Core Implementation File Dependencies**

 
```

```

 **Key File Responsibilities:**

 
| File | Primary Classes | Key Functionality |
|---|---|---|
| cpp/grammar_matcher.cc1-1465 | GrammarMatcher::Impl, BatchGrammarMatcher::Impl | Token acceptance, bitmask generation, batch processing |
| cpp/earley_parser.cc1-928 | EarleyParser, RepeatDetector | Core Earley parsing algorithm, state transitions |
| cpp/earley_parser.h1-486 | ParserState, EarleyParser, RepeatDetector | Parser state definitions, algorithm interface |
| cpp/compiled_grammar_impl.h | CompiledGrammar::Impl, AdaptiveTokenMask | Compiled artifacts, precomputed token masks |
| cpp/support/compact_2d_array.h | Compact2DArray<T> | History-based 2D array with efficient push/pop |
| cpp/support/dynamic_bitset.h | DynamicBitset | Token bitmask operations, efficient bit manipulation |

 **Sources:** [cpp/grammar_matcher.cc1-29](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L1-L29) [cpp/earley_parser.cc1-22](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L1-L22) [cpp/earley_parser.h1-8](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L1-L8)

 
---

 
## Integration Points with Python

 The C++ implementation exposes APIs to Python through nanobind. Key integration points:

 
| C++ Class | Python Class | Binding Location |
|---|---|---|
| Grammar | xgrammar.Grammar | pybind/nanobind.cc |
| GrammarCompiler | xgrammar.GrammarCompiler | pybind/nanobind.cc |
| CompiledGrammar | xgrammar.CompiledGrammar | pybind/nanobind.cc |
| GrammarMatcher | xgrammar.GrammarMatcher | pybind/nanobind.cc |
| TokenizerInfo | xgrammar.TokenizerInfo | pybind/nanobind.cc |

 **Zero-Copy Integration:**

 
 - DLTensor protocol for token bitmasks (no copy between Python and C++)
 - `std::vector` to NumPy array conversion
 - Efficient string handling via `std::string_view`
 
 For detailed binding implementation, see [Python Bindings with nanobind](https://deepwiki.com/mlc-ai/xgrammar/11.4-python-bindings-with-nanobind).

 **Sources:** [include/xgrammar/xgrammar.h1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L1-L18)

 
---

 
## Error Handling and Assertions

 The C++ implementation uses macros for error checking and logging:

 **Assertion Macros:**

 
| Macro | Purpose | Example Usage |
|---|---|---|
| XGRAMMAR_CHECK(cond) | Runtime assertion with message | XGRAMMAR_CHECK(!IsStopTokenAccepted()) << "Matcher terminated" |
| XGRAMMAR_DCHECK(cond) | Debug-only assertion | XGRAMMAR_DCHECK(state.rule_id != -1) |
| XGRAMMAR_LOG(level) | Logging with severity | XGRAMMAR_LOG(WARNING) << "Invalid token id" |
| XGRAMMAR_UNREACHABLE() | Mark unreachable code | Used in exhaustive switch statements |

 **Error Checking Examples:**

 
```

```

 **Logging Levels:**

 
 - `INFO` - Informational messages (e.g., accepted tokens when `debug_print=true`)
 - `WARNING` - Non-fatal issues (e.g., special token rejection)
 - `FATAL` - Unrecoverable errors (terminates program)
 
 All exceptions are logged and propagate to the Python boundary where they're converted to Python exceptions.

 **Sources:** [cpp/grammar_matcher.cc40-66](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L40-L66) [cpp/grammar_matcher.cc491-554](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L491-L554) [cpp/earley_parser.cc34-40](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L34-L40) [include/xgrammar/xgrammar.h13](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L13-L13)

 
---

 
## Performance Considerations

 The C++ implementation is optimized for:

 
 - **Cycle Detection Optimization**: `RepeatDetector` uses adaptive storage - vector for small sets (≤50 states), unordered_set for larger sets
 - **Memory Efficiency**: 
 - CSR format for grammar storage
 - `Compact2DArray` for parser state history with efficient push/pop
 - `DynamicBitset` for token bitmasks (32-bit blocks)
 - **Cache Locality**: `Compact2DArray` stores states contiguously for sequential access
 - **Minimal Allocations**: 
 - State reuse via `tmp_process_state_queue_` and `tmp_states_to_be_added_`
 - `RepeatDetector` pre-allocates vector of size 50
 - **Zero-Copy**: DLTensor protocol for bitmasks, no Python↔C++ copying
 
 **Key Hot Paths:**

 
| Function | Complexity | Optimization Strategy |
|---|---|---|
| GrammarMatcher::AcceptToken() | O(T×S) where T=token length, S=states | Uses AdaptiveTokenMask for fast rejection, LCP optimization for similar tokens |
| GrammarMatcher::FillNextTokenBitmask() | O(V×S) where V=vocab size | Speculative calculation, first-character filtering, rule-level caching |
| EarleyParser::Advance() | O(S×E) where E=edges per state | RepeatDetector prevents duplicate state processing |
| RepeatDetector::IsVisited() | O(1) amortized | Vector for small sets (O(N) scan), hash set for large (O(1) lookup) |
| Compact2DArray::PushBack() | O(1) amortized | Vector reallocation with exponential growth |

 **Transition Threshold:** The `RepeatDetector` uses `transition_threshold_ = 50` as the cutover point between vector and set storage, tuned empirically for typical grammar sizes.

 For detailed performance analysis, see [Performance and Optimization](https://deepwiki.com/mlc-ai/xgrammar/9-performance-and-optimization).

 **Sources:** [cpp/earley_parser.h187-217](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L187-L217) [cpp/earley_parser.cc894-927](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L894-L927) [cpp/grammar_matcher.cc624-777](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L624-L777)

 
---

 
## Next Steps

 For deeper technical details on specific components:

 
 - **[Grammar Internal Representation](https://deepwiki.com/mlc-ai/xgrammar/11.1-grammar-internal-representation)** - CSR format, rule encoding, GrammarBuilder
 - **[FSM Implementation](https://deepwiki.com/mlc-ai/xgrammar/11.2-fsm-implementation)** - FSM operations, NFA→DFA conversion, minimization
 - **[GrammarMatcher Internal Architecture](https://deepwiki.com/mlc-ai/xgrammar/11.3-grammarmatcher-internal-architecture)** - Earley algorithm, state management
 - **[Python Bindings with nanobind](https://deepwiki.com/mlc-ai/xgrammar/11.4-python-bindings-with-nanobind)** - Binding patterns, type converters, DLTensor
 - **[Serialization and Persistence](https://deepwiki.com/mlc-ai/xgrammar/11.5-serialization-and-persistence)** - JSON format, versioning
 - **[Memory Management and Safety](https://deepwiki.com/mlc-ai/xgrammar/11.6-error-handling-and-result-types)** - PIMPL, shared_ptr, thread safety proofs
 
 For build and development workflows, see [Developer Guide](https://deepwiki.com/mlc-ai/xgrammar/12-developer-guide).

 **Sources:** [include/xgrammar/xgrammar.h1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L1-L18)
