> 来源: [https://deepwiki.com/mlc-ai/xgrammar/2-core-concepts](https://deepwiki.com/mlc-ai/xgrammar/2-core-concepts)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Core Concepts

  Relevant source files 
 - [cpp/earley_parser.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc)
 - [cpp/earley_parser.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h)
 - [cpp/grammar.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc)
 - [cpp/grammar_compiler.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc)
 - [cpp/grammar_functor.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc)
 - [cpp/grammar_functor.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h)
 - [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h)
 - [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc)
 - [include/xgrammar/compiler.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h)
 - [include/xgrammar/grammar.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h)
 - [include/xgrammar/object.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/object.h)
 - [python/xgrammar/compiler.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py)
 - [python/xgrammar/grammar.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py)
 - [tests/python/test_grammar_matcher_ebnf.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_ebnf.py)
 
  This page explains the three fundamental pillars of XGrammar: **Grammar Representation**, **Grammar Compilation**, and **Runtime Matching**. These concepts form the backbone of grammar-guided LLM generation, transforming user-defined grammars into efficient token masks that constrain LLM output.

 For detailed information about specific input formats (EBNF, JSON Schema, regex, structural tags), see [Grammar Input Formats](https://deepwiki.com/mlc-ai/xgrammar/4-grammar-input-formats). For implementation details of the Python API, see [Python API Reference](https://deepwiki.com/mlc-ai/xgrammar/3-python-api-reference). For C++ implementation internals, see [C++ Implementation Details](https://deepwiki.com/mlc-ai/xgrammar/11-c++-implementation-details).

 
## Overview of the Three Pillars

 XGrammar processes grammars through three sequential stages, each with distinct responsibilities:

 
| Stage | Purpose | Key Components | Output |
|---|---|---|---|
| Grammar Representation | Store and manipulate grammar rules in a normalized format | Grammar::Impl, GrammarExpr, CSR storage | In-memory grammar AST |
| Grammar Compilation | Optimize grammar and precompute token acceptance information | GrammarCompiler, optimization functors, FSMBuilder | CompiledGrammar with FSMs and token masks |
| Runtime Matching | Validate token sequences and generate token masks for LLM sampling | GrammarMatcher, EarleyParser, adaptive token masks | Token bitmasks for next-token filtering |

 Sources: [cpp/grammar_impl.h23-279](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L23-L279) [cpp/grammar_compiler.cc1-1285](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L1285) [cpp/grammar_matcher.cc1-883](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L1-L883)

 
### System Data Flow

 
```

```

 **Figure 1: End-to-End Data Flow Through XGrammar**

 Sources: [cpp/grammar_parser.h1-167](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.h#L1-L167) [cpp/grammar_functor.h1-444](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L1-L444) [cpp/grammar_compiler.cc36-131](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L36-L131) [cpp/grammar_matcher.cc332-420](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L332-L420) [cpp/earley_parser.h1-547](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L1-L547)

 
## Grammar Representation: The Internal Format

 
### Core Data Structures

 The `Grammar` class uses a Pimpl pattern with `Grammar::Impl` as the implementation. The grammar is stored as a collection of **rules** and **grammar expressions** in a Compressed Sparse Row (CSR) format.

 
```

```

 **Figure 2: Grammar Class Hierarchy and Core Components**

 Sources: [cpp/grammar_impl.h70-279](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L70-L279) [include/xgrammar/grammar.h79-184](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L79-L184) [include/xgrammar/object.h28-47](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/object.h#L28-L47)

 
### Grammar Expression Types

 Each `GrammarExpr` represents a component of a rule's definition. The type determines how the data array is interpreted:

 
| Type | Data Format | Example |
|---|---|---|
| kByteString | [byte0, byte1, ...] | String literal "abc" |
| kCharacterClass | [is_negative, lower0, upper0, lower1, upper1, ...] | Character class [a-z] |
| kCharacterClassStar | Same as kCharacterClass | Star quantifier [a-z]* |
| kEmptyStr | [] | Empty string "" |
| kRuleRef | [rule_id] | Reference to another rule |
| kSequence | [expr_id0, expr_id1, ...] | Concatenation of expressions |
| kChoices | [expr_id0, expr_id1, ...] | Alternation (A \| B \| C) |
| kTagDispatch | [tag_expr0, rule_id0, ..., loop_flag, excluded_str_id] | Structural tag dispatching |
| kRepeat | [rule_id, min_count, max_count] | Repetition {m,n} |

 Sources: [cpp/grammar_impl.h107-129](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L107-L129) [cpp/grammar_impl.h131-150](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L131-L150)

 
### CSR Storage Format

 Grammar expressions are stored in a flat array (`grammar_expr_data_`) with an index pointer array (`grammar_expr_indptr_`). Each expression starts with `[type, data_len, ...data...]`:

 
```
grammar_expr_data_:    [type0, len0, data0..., type1, len1, data1..., ...]
                        ^                       ^
grammar_expr_indptr_:  [0,                      idx1, ...]
```

 This format enables efficient memory usage and fast sequential access during compilation and matching.

 Sources: [cpp/grammar_impl.h234-241](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L234-L241) [cpp/grammar_impl.h155-167](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L155-L167)

 
## Grammar Compilation: Optimization and Preparation

 The `GrammarCompiler` transforms a normalized `Grammar` into a `CompiledGrammar`, which contains precomputed information for efficient token matching. This process involves multiple optimization passes and FSM construction.

 
### Compilation Pipeline

 
```

```

 **Figure 3: Grammar Compilation Pipeline**

 Sources: [cpp/grammar_functor.cc484-492](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L484-L492) [cpp/grammar_functor.cc1548-1598](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L1548-L1598) [cpp/grammar_compiler.cc1102-1285](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1102-L1285)

 
### Key Compilation Components

 
| Component | Purpose | Implementation |
|---|---|---|
| GrammarNormalizer | Ensures rules follow a normalized structure (choices of sequences) | cpp/grammar_functor.cc244-264 |
| RuleInliner | Eliminates simple rule references by inlining their definitions | cpp/grammar_functor.cc503-584 |
| DeadCodeEliminator | Removes unreferenced rules from the grammar | cpp/grammar_functor.cc635-684 |
| LookaheadAssertionAnalyzer | Detects and adds lookahead assertions to rules | cpp/grammar_functor.cc686-808 |
| GrammarFSMBuilder | Converts grammar expressions to finite state machines | cpp/grammar_functor.cc994-1545 |
| GrammarMatcherForTokenMaskCache | Precomputes which tokens can be accepted at each parser state | cpp/grammar_compiler.cc38-351 |

 Sources: [cpp/grammar_functor.h279-383](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L279-L383) [cpp/grammar_compiler.cc36-131](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L36-L131)

 
### Finite State Machine Generation

 Each rule's body is converted into a `CompactFSM` (Finite State Machine) stored in `Grammar::Impl::per_rule_fsms`. These FSMs enable efficient character-by-character matching during runtime without recursive rule expansion.

 The FSM construction uses Thompson's construction for NFAs, subset construction for NFA-to-DFA conversion, and Hopcroft's algorithm for DFA minimization.

 Sources: [cpp/grammar_functor.cc994-1545](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L994-L1545) [cpp/fsm.h1-800](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/fsm.h#L1-L800)

 
### CompiledGrammar Structure

 
```

```

 **Figure 4: CompiledGrammar Structure and Token Mask Cache**

 Sources: [cpp/compiled_grammar_impl.h1-159](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/compiled_grammar_impl.h#L1-L159) [cpp/adaptive_token_mask.h1-150](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/adaptive_token_mask.h#L1-L150)

 
### Adaptive Token Mask Strategy

 The `AdaptiveTokenMask` for each parser state categorizes tokens into three groups:

 
 - **Accepted indices**: Tokens definitely accepted by this rule
 - **Rejected indices**: Tokens definitely rejected by this rule
 - **Uncertain indices**: Tokens requiring parent context to determine acceptance
 
 This tri-partition optimization significantly reduces runtime token checking overhead.

 Sources: [cpp/adaptive_token_mask.h32-116](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/adaptive_token_mask.h#L32-L116) [cpp/grammar_compiler.cc133-295](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L133-L295)

 
## Runtime Matching: Token Validation and Mask Generation

 The `GrammarMatcher` uses an Earley parser to validate token sequences and generate token bitmasks for the next token in LLM generation.

 
### GrammarMatcher Architecture

 
```

```

 **Figure 5: GrammarMatcher Implementation Hierarchy**

 Sources: [cpp/grammar_matcher.cc332-420](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L332-L420) [cpp/earley_parser.h219-547](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L219-L547) [cpp/earley_parser.h41-130](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L41-L130)

 
### Earley Parsing Algorithm

 The `EarleyParser` implements a modified Earley parsing algorithm with three fundamental operations:

 
 - **Predict**: Expand rule references to add new parser states
 - **Scan**: Advance parser states by consuming a character
 - **Complete**: Handle completion of a rule and advance parent states
 
 The parser maintains a history of scanable states (`scanable_state_history_`) and completable states (`rule_id_to_completable_states_`) for efficient rollback and state management.

 Sources: [cpp/earley_parser.cc150-208](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L150-L208) [cpp/earley_parser.cc210-238](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L210-L238) [cpp/earley_parser.cc42-148](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L42-L148)

 
### Token Bitmask Generation Process

 When `FillNextTokenBitmask()` is called, the matcher:

 
 - Retrieves the latest parser states from `EarleyParser`
 - For each state, looks up its `AdaptiveTokenMask` in the compiled grammar cache
 - For uncertain tokens, performs actual token string matching using the Earley parser
 - Combines results from all states: union of accepted tokens, intersection of rejected tokens
 - Writes the final token set as a packed int32 bitmask in a `DLTensor`
 
 
```

```

 **Figure 6: Token Bitmask Generation Algorithm**

 Sources: [cpp/grammar_matcher.cc624-783](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L624-L783) [cpp/grammar_matcher.cc68-87](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L68-L87)

 
### Integration with LLM Sampling

 The generated bitmask is applied to LLM logits before sampling:

 
```

```

 **Figure 7: Integration with LLM Token Sampling**

 Sources: [cpp/grammar_matcher.cc89-231](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L89-L231) [cpp/grammar_matcher.cc491-555](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L491-L555)

 
## Key Performance Optimizations

 XGrammar employs several strategies to achieve high performance:

 
 - **Two-tier Caching**: Grammar-level cache (LRU) and rule-level FSM hash cache to avoid redundant compilation
 - **Longest Common Prefix (LCP) Optimization**: When checking token sequences, reuse parsing work from common prefixes
 - **First Character Filtering**: Quickly reject tokens based on their first character
 - **Speculative Calculation**: For self-recursive patterns, directly accept tokens matching the pattern without full parsing
 - **CSR Storage**: Compact memory representation for grammar expressions and FSM edges
 - **Parallel Compilation**: Multi-threaded grammar compilation using thread pools
 
 Sources: [cpp/grammar_compiler.cc416-474](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L416-L474) [cpp/grammar_compiler.cc476-627](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L476-L627) [cpp/grammar_matcher.cc714-755](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L714-L755) [cpp/support/thread_pool.h1-120](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/thread_pool.h#L1-L120)

 
## Summary

 The three core concepts work together to enable efficient grammar-guided generation:

 
 - **Grammar Representation** provides a flexible, compact internal format (CSR-based AST)
 - **Grammar Compilation** transforms and optimizes the grammar, building FSMs and precomputing token masks
 - **Runtime Matching** uses Earley parsing with the precomputed masks to efficiently generate token bitmasks
 
 This architecture balances compile-time preprocessing with runtime efficiency, enabling xgrammar to constrain LLM generation with minimal overhead.

 For details on the internal implementation of each component, see:

 
 - [Grammar Representation](https://deepwiki.com/mlc-ai/xgrammar/2.1-grammar-representation) for CSR format and expression types
 - [Grammar Compilation](https://deepwiki.com/mlc-ai/xgrammar/2.2-grammar-compilation) for optimization passes and FSM construction
 - [Grammar Matching](https://deepwiki.com/mlc-ai/xgrammar/2.3-grammar-matching) for Earley parser and bitmask generation algorithms
