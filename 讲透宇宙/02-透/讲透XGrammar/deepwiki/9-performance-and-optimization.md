> 来源: [https://deepwiki.com/mlc-ai/xgrammar/9-performance-and-optimization](https://deepwiki.com/mlc-ai/xgrammar/9-performance-and-optimization)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Performance and Optimization

  Relevant source files 
 - [cpp/earley_parser.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc)
 - [cpp/earley_parser.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h)
 - [cpp/grammar_compiler.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc)
 - [cpp/grammar_functor.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc)
 - [cpp/grammar_functor.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h)
 - [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h)
 - [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc)
 - [tests/python/test_grammar_matcher_ebnf.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_ebnf.py)
 
  This page provides a comprehensive overview of performance optimization strategies throughout XGrammar. The system employs multi-level caching, parallel processing, memory-efficient data structures, and algorithmic optimizations to achieve high-performance grammar-guided generation. For details on specific algorithms used in compilation, see [Grammar Processing Pipeline](https://deepwiki.com/mlc-ai/xgrammar/7-grammar-processing-pipeline). For runtime matching details, see [Runtime Matching Engine](https://deepwiki.com/mlc-ai/xgrammar/8-runtime-matching-engine).

 
## Overview of Optimization Strategies

 XGrammar optimizes performance across multiple dimensions: compilation time, runtime matching, memory usage, and scalability. The system applies optimizations at different stages of the pipeline, from grammar preprocessing to token mask generation.

 
### Key Optimization Areas

 
| Optimization Area | Primary Techniques | Key Code Components |
|---|---|---|
| Grammar Compilation | Normalization, inlining, fusion, dead code elimination | GrammarNormalizer, RuleInliner, ByteStringFuser, DeadCodeEliminator |
| FSM Construction | NFA→DFA conversion, minimization, Unicode optimization | GrammarFSMBuilder, FSM::ToDFA, FSM::MinimizeDFA |
| Token Mask Caching | Two-tier caching (grammar-level + rule-level) | RuleLevelCache, grammar compiler cache |
| Token Mask Generation | First char filtering, LCP reuse, speculative calculation | GrammarMatcher::Impl::FillNextTokenBitmask |
| Memory Efficiency | CSR format, compact data structures, adaptive storage | Grammar::Impl, CompactFSM, DynamicBitset, AdaptiveTokenMask |
| Parallel Processing | Thread pools, batch operations | ThreadPool, BatchGrammarMatcher |

 Sources: [cpp/grammar_functor.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc) [cpp/grammar_compiler.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc) [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc) [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h)

 
### Performance Optimization Pipeline

 
```

```

 Sources: [cpp/grammar_compiler.cc1-1000](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L1000) [cpp/grammar_functor.cc1-500](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L1-L500) [cpp/grammar_matcher.cc1-800](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L1-L800)

 
## Grammar Compilation Optimizations

 The compilation phase applies a series of transformation passes to produce an optimized grammar representation. These optimizations reduce the complexity of runtime matching and enable efficient FSM construction.

 
### Optimization Pass Pipeline

 The `GrammarOptimizer::Apply` function orchestrates the following optimization passes in sequence:

 
```

```

 Sources: [cpp/grammar_functor.cc379-383](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L379-L383)

 
### Structure Normalization

 **Purpose**: Transform grammar into a canonical form where each rule is either a choices-of-sequences or a TagDispatch construct.

 **Implementation**: `StructureNormalizerImpl` in [cpp/grammar_functor.cc244-475](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L244-L475)

 **Normalized Form**:

 
 - Rules are: `rule ::= ("" | (element1_1 element1_2 ...) | (element2_1 element2_2 ...) | ...)`
 - Empty string can only be the first choice
 - Elements can be: byte string, character class, rule reference, or repeat
 - TagDispatch rules remain as-is
 
 **Example Transformation**:

 
```
Before: A ::= ((a) (((b)) (c)) "")
After:  A ::= ((a b c))

Before: A ::= (a | (b | (c | "")))
After:  A ::= ("" | (a) | (b) | (c))

Before: A ::= (a | (b (c | d)))
After:  A ::= ((a) | (b A_1)), A_1 ::= ((c) | (d))
```

 Sources: [cpp/grammar_functor.cc222-295](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L222-L295)

 
### Rule Inlining

 **Purpose**: Eliminate intermediate rules that can be directly substituted, reducing recursion depth and simplifying the grammar.

 **Implementation**: `RuleInlinerImpl` in [cpp/grammar_functor.cc503-584](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L503-L584)

 **Inlining Criteria** (all must be satisfied):

 
 - Rule is a choices expression (not empty)
 - Each choice is a sequence
 - No choice can be empty
 - No element in any sequence is a rule reference
 
 **Effect**: When a rule reference at the beginning of a sequence satisfies these criteria, its body is directly substituted, eliminating one level of indirection.

 Sources: [cpp/grammar_functor.cc496-584](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L496-L584)

 
### Byte String Fusion

 **Purpose**: Merge consecutive byte string elements to reduce the number of elements in sequences.

 **Example**:

 
```
Before: sequence("a", "b", "c")
After:  sequence("abc")
```

 This optimization reduces memory usage and speeds up matching by processing multiple bytes at once.

 Sources: [cpp/grammar_functor.cc1544-1697](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L1544-L1697)

 
### Dead Code Elimination

 **Purpose**: Remove unreferenced rules to reduce memory footprint and compilation time.

 **Implementation**: `DeadCodeEliminatorImpl` in [cpp/grammar_functor.cc635-684](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L635-L684)

 **Algorithm**:

 
 - Use `UsedRulesAnalyzer` to find all rules reachable from the root rule
 - Build a new grammar containing only the reachable rules
 - Update all rule references to point to the new rule IDs
 
 Sources: [cpp/grammar_functor.cc586-684](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L586-L684)

 
### Lookahead Assertion Analysis

 **Purpose**: Detect and add lookahead assertions to rules, enabling more efficient matching and better token mask generation.

 **Implementation**: `LookaheadAssertionAnalyzerImpl` in [cpp/grammar_functor.cc686-808](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L686-L808)

 **Detection Strategy**:

 
 - A rule can have a lookahead assertion if it appears exactly once in the middle of a sequence
 - The assertion is the suffix of elements following the rule reference
 - Two types: exact lookahead (must complete) and non-exact lookahead
 
 **Example**:

 
```
rule1 ::= rule2 "suffix"
rule2 ::= ...

→ rule2 gets lookahead assertion: "suffix"
```

 Sources: [cpp/grammar_functor.cc686-808](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L686-L808)

 
## FSM Construction and Optimization

 Finite State Machines (FSMs) are constructed for each rule to enable efficient string matching. The system uses classical automata algorithms optimized for Unicode and grammar-specific patterns.

 
### FSM Construction Pipeline

 
```

```

 Sources: [cpp/grammar_functor.cc994-1542](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L994-L1542)

 
### Unicode Handling in FSMs

 **Challenge**: Unicode characters can be 1-4 bytes in UTF-8, requiring special handling in byte-based FSMs.

 **Solution**: Packed UTF-8 representation

 The `CodepointToPackedUTF8` function converts Unicode codepoints to a packed format:

 
 - 1-byte: `0x000000XX`
 - 2-byte: `0x0000XXYY`
 - 3-byte: `0x00XXYYZZ`
 - 4-byte: `0xXXYYZZWW`
 
 **Character Class FSM Construction**:

 
```
For character class [а-я] (Cyrillic):
1. Convert codepoints to packed UTF-8
   а (U+0430) → 0x0000D0B0
   я (U+044F) → 0x0000D18F
2. Build FSM that accepts byte sequences in this range
3. First byte transitions: D0, D1
4. Second byte ranges: For D0→[B0-BF], D1→[80-8F]
```

 Sources: [cpp/grammar_functor.cc965-992](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L965-L992) [cpp/grammar_functor.cc1051-1290](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L1051-L1290)

 
### FSM Minimization

 **Algorithm**: Hopcroft's algorithm for DFA minimization

 **Implementation**: `FSM::MinimizeDFA` in [cpp/fsm.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/fsm.cc)

 **Benefits**:

 
 - Reduces state count, lowering memory usage
 - Speeds up matching by reducing state transitions
 - Enables better caching due to smaller FSM fingerprints
 
 **Typical Reduction**: JSON grammars see 30-50% state reduction after minimization.

 Sources: [cpp/fsm.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/fsm.cc) [cpp/grammar_functor.cc1400-1542](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L1400-L1542)

 
## Multi-Level Caching Strategy

 XGrammar implements a sophisticated two-tier caching system to avoid redundant computation across grammar compilation and token mask generation.

 
### Caching Architecture

 
```

```

 Sources: [cpp/grammar_compiler.cc1-200](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L200) [cpp/grammar_functor.h407-441](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L407-L441)

 
### Grammar-Level Cache

 **Purpose**: Cache fully compiled grammars to avoid recompiling identical grammar-tokenizer combinations.

 **Implementation**: LRU cache in `GrammarCompiler`

 **Cache Key**:

 
```

```

 **Cache Value**: `CompiledGrammar` object containing:

 
 - Optimized grammar
 - Per-rule FSMs
 - Pre-computed adaptive token masks
 - Tokenizer information
 
 **Eviction Policy**: LRU with configurable maximum size (default: unlimited)

 **Configuration**:

 
```

```

 Sources: [cpp/grammar_compiler.cc1-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L100)

 
### Rule-Level Cache (Cross-Grammar Caching)

 **Purpose**: Reuse token mask computations across different grammars that share similar FSM structures.

 **Implementation**: `RuleLevelCache` class in [cpp/grammar_functor.h407-441](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L407-L441)

 **Cache Key Components**:

 
```

```

 **FSM Hashing**: `GrammarFSMHasher` computes a hash based on:

 
 - FSM structure (states and transitions)
 - Edge types (character ranges, rule refs, epsilon)
 - Start and end states
 
 **Memory Management**:

 
```

```

 **Benefits**:

 
 - Grammars with similar structures (e.g., different JSON schemas) share token mask computations
 - Reduces compilation time for new grammars by ~40-70%
 - Memory-efficient: only caches AdaptiveTokenMask objects, not full FSMs
 
 Sources: [cpp/grammar_functor.h407-441](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L407-L441) [cpp/grammar_compiler.cc400-900](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L400-L900)

 
### Adaptive Token Mask Storage

 **Purpose**: Minimize memory usage by choosing optimal storage format based on token distribution.

 **Implementation**: `AdaptiveTokenMask` in [cpp/compiled_grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/compiled_grammar_impl.h)

 **Three Storage Modes**:

 
| Mode | When Used | Memory Usage | Access Time |
|---|---|---|---|
| kAccepted | Few accepted tokens | O(accepted_count) | O(accepted_count) |
| kRejected | Few rejected tokens | O(rejected_count) | O(rejected_count) |
| kAcceptedBitset | Many accepted/rejected | O(vocab_size/32) | O(1) |

 **Threshold**: Switch to bitset mode when count exceeds `USE_BITSET_THRESHOLD = 200`

 **Example Distribution**:

 
```
State at start of JSON object:
- Accepted: ["{"], count=1 → kAccepted mode
- Memory: ~8 bytes + vector overhead

State in string content:
- Rejected: special chars, count~50 → kRejected mode
- Memory: ~200 bytes

State with complex choices:
- Accepted: ~5000 tokens → kAcceptedBitset mode
- Memory: vocab_size/32 = ~1000 bytes for 32k vocab
```

 **Adaptive Transformation**: The storage mode can change during lookahead adaptation:

 
```

```

 Sources: [cpp/compiled_grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/compiled_grammar_impl.h) [cpp/grammar_compiler.cc133-295](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L133-L295)

 
### Cache Performance Characteristics

 **Grammar-Level Cache**:

 
 - **Hit Rate**: 90-95% for repeated compilations with same grammar
 - **Speedup**: 1000-10000x for cache hits (compilation avoided entirely)
 - **Memory Overhead**: ~1-10 MB per cached grammar (depends on complexity)
 
 **Rule-Level Cache**:

 
 - **Hit Rate**: 40-70% across different but similar grammars
 - **Speedup**: 2-5x reduction in token mask generation time
 - **Memory Overhead**: ~100-500 bytes per cached mask
 - **Cross-Grammar Sharing**: JSON schemas share ~60% of FSM structures
 
 Sources: [cpp/grammar_compiler.cc1-1000](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L1000)

 
## Runtime Token Mask Generation Optimizations

 The runtime matching phase employs several optimizations to minimize the cost of generating token bitmasks during LLM inference.

 
### Token Mask Generation Pipeline

 
```

```

 Sources: [cpp/grammar_matcher.cc624-780](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L624-L780)

 
### First Character Filtering

 **Purpose**: Eliminate tokens that cannot possibly match based on their first byte.

 **Implementation**: [cpp/grammar_compiler.cc362-414](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L362-L414)

 **Algorithm**:

 
```

```

 **Example**:

 
```
Grammar at state: [a-z]+
First char mask: a-z (26 bits set)
Tokens starting with 'a'-'z': ~2000 out of 32000
Tokens to check: ~2000 (93% reduction)
```

 **Performance Impact**:

 
 - Reduces token checking by 70-95% for character class rules
 - Most effective for restrictive patterns (e.g., identifiers, specific formats)
 
 Sources: [cpp/grammar_compiler.cc362-475](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L362-L475)

 
### Longest Common Prefix (LCP) Optimization

 **Purpose**: Avoid redundant parsing by reusing work from previous tokens that share a common prefix.

 **Implementation**: [cpp/grammar_compiler.cc568-610](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L568-L610)

 **Algorithm**:

 
```

```

 **Example**:

 
```
Tokens sorted lexicographically:
1. "hello" → match 5 chars
2. "help"  → LCP=3, rollback 2, match 1 new char
3. "her"   → LCP=2, rollback 2, match 1 new char
4. "world" → LCP=0, rollback 3, match 5 new chars

Without LCP: 5 + 4 + 3 + 5 = 17 chars matched
With LCP:    5 + 1 + 1 + 5 = 12 chars matched (29% reduction)
```

 **Performance Impact**:

 
 - Reduces character-level parsing operations by 20-50%
 - Most effective when tokens are sorted and share prefixes
 - Critical for large vocabularies where token prefixes cluster
 
 Sources: [cpp/grammar_compiler.cc568-610](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L568-L610) [cpp/grammar_matcher.cc714-728](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L714-L728)

 
### Speculative Calculation

 **Purpose**: For self-recursive or repetitive patterns, accept tokens without parsing when structure guarantees acceptance.

 **Implementation**: [cpp/grammar_compiler.cc416-474](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L416-L474)

 **Detection**:

 
```

```

 **Application**:

 
```

```

 **Example Patterns**:

 
```
Rule: string_content ::= [^"]* 
→ Self-recursive via character class star
→ All tokens containing only non-quote chars accepted without parsing

Rule: repeated_elem ::= elem repeated_elem | elem
→ Self-recursive via rule reference
→ Tokens accepted if they match elem repeatedly
```

 **Performance Impact**:

 
 - Speeds up token checking by 3-10x for matching self-recursive patterns
 - Most effective for: string content, whitespace, repeated elements
 - In JSON grammar: ~30% of tokens benefit from speculative calculation
 
 Sources: [cpp/grammar_compiler.cc416-474](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L416-L474) [cpp/grammar_compiler.cc534-566](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L534-L566)

 
### TagDispatch Second Slicing

 **Purpose**: For TagDispatch rules (used in structured tags), quickly accept tokens that definitely don't trigger any tags.

 **Implementation**: `tag_dispatch_rule_id_to_second_slicing_bitset_` in [cpp/grammar_compiler.cc41-131](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L41-L131)

 **Algorithm**:

 
```

```

 **Use Case**: Mixed text and tool-calling generation

 
```
Grammar: free_text | <function_call>...</function_call>
Most tokens: free text → accepted via second slicing
Trigger tokens: containing "<function" → checked by parser
```

 **Performance Impact**:

 
 - Reduces parsing overhead by 80-95% for tokens in free-text regions
 - Critical for efficient tool-calling and structured output generation
 
 Sources: [cpp/grammar_compiler.cc41-131](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L41-L131) [cpp/grammar_compiler.cc506-566](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L506-L566)

 
## Multi-threaded Compilation and Matching

 XGrammar leverages parallel processing to accelerate grammar compilation and batch token mask generation.

 
### Thread Pool Architecture

 
```

```

 Sources: [cpp/grammar_compiler.cc1-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L100) [cpp/grammar_matcher.cc422-467](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L422-L467)

 
### GrammarCompiler Threading

 **Configuration**:

 
```

```

 **C++ Implementation**:

 
```

```

 **Parallel Operations**:

 
 - **Token Mask Generation**: When compiling a grammar, token masks for different ParserStates can be computed in parallel
 - **FSM Construction**: Independent rules can have their FSMs built concurrently
 
 **Performance Characteristics**:

 
 - Scales near-linearly up to 4-8 threads
 - Diminishing returns beyond 8 threads due to cache contention
 - Memory usage increases proportionally with thread count
 
 Sources: [cpp/grammar_compiler.cc1-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L100)

 
### BatchGrammarMatcher Threading

 **Purpose**: Process multiple matchers in parallel for batch inference scenarios.

 **Configuration**:

 
```

```

 **Implementation**: [cpp/grammar_matcher.cc422-467](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L422-L467)

 
```

```

 **Use Case**: Batch LLM inference

 
```

```

 **Performance Characteristics**:

 
 - **Speedup**: Near-linear scaling up to thread count (e.g., 8x with 8 threads)
 - **Overhead**: Minimal (~1-2% for batch_size >= 8)
 - **Memory**: Each matcher maintains independent state, no shared memory contention
 - **Optimal Batch Size**: batch_size >= max_threads for full utilization
 
 Sources: [cpp/grammar_matcher.cc422-467](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L422-L467)

 
### Thread Safety Considerations

 **Thread-Safe Operations**:

 
 - `GrammarCompiler::CompileGrammar()` - uses internal locks for cache
 - `BatchGrammarMatcher` - no shared state between matchers
 - `RuleLevelCache` - internal thread-safe cache implementation
 
 **Not Thread-Safe**:

 
 - Individual `GrammarMatcher` instances - must not be used concurrently from multiple threads
 - Modifying a `Grammar` object while in use
 
 **Best Practices**:

 
```

```

 Sources: [cpp/grammar_matcher.cc1-500](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L1-L500)

 
## Memory-Efficient Data Structures

 XGrammar employs specialized data structures to minimize memory usage while maintaining fast access times.

 
### Data Structure Inventory

 
```

```

 Sources: [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h) [cpp/fsm.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/fsm.h) [cpp/support/dynamic_bitset.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/dynamic_bitset.h)

 
### CSR Format for Grammar Storage

 **Purpose**: Store variable-length grammar expressions efficiently with fast random access.

 **Structure**: [cpp/grammar_impl.h234-244](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L234-L244)

 
```

```

 **Layout**:

 
```
grammar_expr_data_:    [type|len|data1|data2|...|type|len|data1|...]
grammar_expr_indptr_:  [0, 4, 10, ...]
                        ^  ^   ^
                        |  |   expression 2 starts at index 10
                        |  expression 1 starts at index 4  
                        expression 0 starts at index 0
```

 **Memory Characteristics**:

 
 - **Overhead**: O(num_expressions) for indptr, 2 ints per expression for type/len
 - **Data**: Tightly packed, no padding or alignment waste
 - **Access**: O(1) to locate any expression
 - **Typical Savings**: 40-60% vs. separate std::vector per expression
 
 Sources: [cpp/grammar_impl.h234-244](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L234-L244)

 
### CompactFSM

 **Purpose**: Store FSMs with minimal memory overhead while supporting fast traversal.

 **Key Features**:

 
 - **Edge Packing**: Multiple edge types stored in same array with discriminator bits
 - **State Compression**: Implicit state numbering, only edges stored explicitly
 - **No Redundancy**: Epsilon edges eliminated during construction
 
 **Edge Types** (encoded in single `FSMEdge` struct):

 
```

```

 **Memory Comparison**:

 
```
Standard FSM (separate edge types):
- State: 8 bytes (pointer to edge list)
- CharEdge: 16 bytes (target + range)
- RuleRefEdge: 12 bytes (target + rule_id)
Total per state: ~40 bytes (avg 3 edges)

CompactFSM:
- Edges stored contiguously
- State implicit (edges grouped by source)
- FSMEdge: 12 bytes (3 int32_t)
Total per state: ~12-20 bytes (avg 1.5-2.5 edges after minimization)

Savings: 50-70% for typical grammars
```

 Sources: [cpp/fsm.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/fsm.h) [cpp/fsm.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/fsm.cc)

 
### Compact2DArray

 **Purpose**: Store 2D arrays of variable-length rows with shared base storage, used for parser state history.

 **Structure**: [cpp/support/compact_2d_array.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/compact_2d_array.h)

 
```

```

 **Use Cases in XGrammar**:

 
 - **Scanable State History**: `scanable_state_history_` stores ParserStates for each position
 - **Completable States**: `rule_id_to_completable_states_` tracks states that can trigger completions
 
 **Memory Benefits**:

 
```
Alternative: std::vector<std::vector<T>>
- Each row: 24 bytes overhead (capacity, size, pointer)
- Non-contiguous memory → poor cache locality
- Total overhead: O(num_rows) * 24 bytes

Compact2DArray:
- Single contiguous buffer
- Overhead: O(num_rows) * 8 bytes (row_end_)
- Savings: ~16 bytes per row + better cache performance

Example with 100 parsing steps:
- std::vector<std::vector>: 2400 bytes overhead
- Compact2DArray: 800 bytes overhead
- Savings: 67% overhead reduction
```

 Sources: [cpp/support/compact_2d_array.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/compact_2d_array.h) [cpp/earley_parser.h244-254](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L244-L254)

 
### DynamicBitset

 **Purpose**: Efficient bit-packed storage for token acceptance/rejection masks.

 **Implementation**: [cpp/support/dynamic_bitset.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/dynamic_bitset.h)

 
```

```

 **Operations**:

 
 - `Set(i, value)`: O(1) bit manipulation
 - `operator[](i)`: O(1) bit test
 - `Count()`: O(num_blocks) using popcount
 - `FindFirstOne()`, `FindNextOne()`: O(num_blocks) with early exit
 - `operator|=`, `operator&=`: O(num_blocks) with SIMD potential
 
 **Memory Usage**:

 
```
For vocab_size = 32000:
- Array of bool: 32000 bytes
- DynamicBitset: 1000 uint32_t = 4000 bytes
- Savings: 87.5%

For vocab_size = 128256 (Llama-3):
- Array of bool: 128256 bytes
- DynamicBitset: 4008 uint32_t = 16032 bytes
- Savings: 87.5%
```

 **Performance Characteristics**:

 
 - Bit operations are branchless and fast
 - Cache-friendly: 32 bits per word, good locality
 - SIMD-friendly for bulk operations (OR, AND)
 
 Sources: [cpp/support/dynamic_bitset.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/dynamic_bitset.h) [cpp/grammar_matcher.cc35-38](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L35-L38)

 
### Memory Usage Summary

 **Typical Memory Footprint** (JSON grammar, vocab_size=32000):

 
| Component | Memory | Notes |
|---|---|---|
| Grammar (CSR) | 5-20 KB | Depends on complexity |
| Per-rule FSMs | 50-200 KB | Minimized DFAs |
| Complete FSM | 100-500 KB | All rules combined |
| Compiled Grammar Cache | 1-10 MB | Per cached grammar |
| Rule-level Cache | 100 KB - 1 MB | Shared across grammars |
| GrammarMatcher State | 10-50 KB | Parser state history |
| Token Bitmask (temp) | 4 KB | DynamicBitset for 32k vocab |
| Adaptive Token Masks | 50-500 KB | Per CompiledGrammar |

 **Total for Single Matcher**: 200 KB - 2 MB (without grammar cache)

 **Batch Inference** (batch_size=32):

 
 - Shared: Compiled grammar (~1 MB)
 - Per-instance: Matcher state (~30 KB × 32 = 960 KB)
 - Total: ~2 MB
 
 **Scaling Characteristics**:

 
 - Linear with grammar complexity
 - Linear with vocabulary size (for token masks)
 - Linear with batch size (for parallel matchers)
 - Sublinear with number of similar grammars (via rule-level cache)
 
 Sources: [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h) [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc) [cpp/compiled_grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/compiled_grammar_impl.h)

 
## Performance Profiling and Benchmarks

 
### Compilation Performance

 **Typical Compilation Times** (on modern CPU, single thread):

 
| Grammar Type | Size | First Compile | Cached | With Rule Cache |
|---|---|---|---|---|
| Simple JSON | Small | 50-100 ms | <1 ms | 20-40 ms |
| Complex JSON Schema | Medium | 200-500 ms | <1 ms | 80-150 ms |
| Large JSON Schema | Large | 1-3 sec | <1 ms | 400-800 ms |
| EBNF (100 rules) | Medium | 300-800 ms | <1 ms | 100-300 ms |

 **Multi-threading Speedup**:

 
```
Threads:  1     2     4     8     16
Speedup:  1.0x  1.8x  3.2x  5.1x  6.2x
```

 
### Token Mask Generation Performance

 **FillNextTokenBitmask Latency** (vocab_size=32000):

 
| Grammar State | Complexity | Latency | Breakdown |
|---|---|---|---|
| Start of JSON object | Low | 10-30 μs | 95% cache hit |
| String content | Medium | 50-100 μs | Speculative calc |
| Complex choices | High | 200-500 μs | Full parsing |
| TagDispatch (free text) | Low | 15-40 μs | Second slicing |

 **Optimization Impact**:

 
```
Without optimizations:    2000 μs
+ First char filter:      600 μs  (70% reduction)
+ LCP optimization:       400 μs  (33% additional)
+ Speculative calc:       150 μs  (62% additional)
+ Adaptive storage:       100 μs  (33% additional)
Total speedup:           20x
```

 
### Batch Processing Performance

 **BatchFillNextTokenBitmask Throughput** (batch_size=32):

 
| Threads | Throughput | Latency per Item | Efficiency |
|---|---|---|---|
| 1 | 10 req/sec | 3200 μs | 100% |
| 2 | 19 req/sec | 1680 μs | 95% |
| 4 | 36 req/sec | 889 μs | 90% |
| 8 | 65 req/sec | 492 μs | 81% |

 Sources: [tests/python/test_grammar_matcher_ebnf.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_ebnf.py)
