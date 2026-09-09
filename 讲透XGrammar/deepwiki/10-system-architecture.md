> 来源: [https://deepwiki.com/mlc-ai/xgrammar/10-system-architecture](https://deepwiki.com/mlc-ai/xgrammar/10-system-architecture)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# System Architecture

  Relevant source files 
 - [CMakeLists.txt](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt)
 - [cpp/grammar.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc)
 - [include/xgrammar/compiler.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h)
 - [include/xgrammar/grammar.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h)
 - [include/xgrammar/object.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/object.h)
 - [include/xgrammar/xgrammar.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h)
 - [pyproject.toml](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml)
 - [python/xgrammar/compiler.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py)
 - [python/xgrammar/grammar.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py)
 
  This document provides a comprehensive overview of the XGrammar system architecture, covering the major layers, components, data structures, and their interactions. It explains how grammars flow from user input through compilation to runtime token generation.

 For detailed implementation of individual subsystems, see:

 
 - Grammar input format processing: [Grammar Input Formats](https://deepwiki.com/mlc-ai/xgrammar/4-grammar-input-formats)
 - Compilation pipeline internals: [Grammar Processing Pipeline](https://deepwiki.com/mlc-ai/xgrammar/7-grammar-processing-pipeline)
 - Runtime matching mechanics: [Runtime Matching Engine](https://deepwiki.com/mlc-ai/xgrammar/8-runtime-matching-engine)
 - C++ implementation details: [C++ Implementation Details](https://deepwiki.com/mlc-ai/xgrammar/11-c++-implementation-details)
 
 
## Architectural Overview

 XGrammar is structured as a layered system where grammars flow through multiple transformation stages before being used in runtime generation. The architecture separates concerns into distinct layers, each with clear responsibilities.

 
```

```

 **Diagram: High-Level System Architecture**

 The system follows a pipeline architecture where user-provided grammars in various formats are parsed, normalized, optimized, compiled with a tokenizer vocabulary, and then used at runtime by a matcher that generates token bitmasks for constrained LLM generation.

 **Sources:** [cpp/grammar_functor.cc1-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L1-L100) [cpp/grammar_compiler.cc1-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L100) [cpp/grammar_impl.h1-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L1-L100) [python/xgrammar/grammar.py1-50](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L1-L50) [python/xgrammar/compiler.py1-50](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L1-L50)

 
## Core Layers

 
### 1. Grammar Input and Parsing Layer

 This layer handles multiple input formats and converts them into a unified `Grammar::Impl` representation. The main components are:

 
| Component | File | Responsibility |
|---|---|---|
| EBNFLexer / EBNFParser | cpp/grammar_parser.cc | Tokenize and parse EBNF strings into Grammar AST |
| JSONSchemaConverter | cpp/json_schema_converter.cc | Convert JSON schemas to EBNF, then parse to Grammar |
| RegexToEBNF | cpp/regex_converter.h | Convert regex patterns to EBNF format |
| StructuralTagToGrammar | cpp/structural_tag.cc | Parse structural tags with dynamic dispatch |

 All converters produce a `Grammar` object containing a `Grammar::Impl` instance with:

 
 - `rules_`: Vector of `Rule` objects with names and body expressions
 - `grammar_expr_data_`: Flat array storing all grammar expression data
 - `grammar_expr_indptr_`: Indices into `grammar_expr_data_` for each expression
 
 **Sources:** [cpp/grammar.cc37-72](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L37-L72) [cpp/grammar_impl.h70-169](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L70-L169) [python/xgrammar/grammar.py132-434](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L132-L434)

 
### 2. Grammar Transformation Layer

 The transformation layer applies a series of functors to normalize and optimize the grammar before compilation:

 
```

```

 **Diagram: Grammar Transformation Pipeline**

 Each transformation is implemented as a `GrammarFunctor`, `GrammarMutator`, or `GrammarVisitor`:

 
 - **`GrammarNormalizer`**: Orchestrates `SingleElementExprEliminator` and `StructureNormalizer` to ensure consistent AST structure
 - **`GrammarOptimizer`**: Applies multiple optimization passes including inlining, dead code elimination, and lookahead analysis
 - **`GrammarFSMBuilder`**: Constructs finite state machines for each rule, storing them in `Grammar::Impl::per_rule_fsms`
 
 **Sources:** [cpp/grammar_functor.cc174-494](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L174-L494) [cpp/grammar_functor.h23-383](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L23-L383)

 
### 3. Compilation Layer

 The `GrammarCompiler` takes an optimized `Grammar` and a `TokenizerInfo` to produce a `CompiledGrammar`:

 
```

```

 **Diagram: Compilation Process**

 The `GrammarCompiler::Impl` class performs the following:

 
 - **Parallel Compilation**: Uses a thread pool (configurable via `max_threads` parameter) to process multiple FSM states concurrently
 - **Token Mask Generation**: For each FSM state, generates an `AdaptiveTokenMask` indicating which vocabulary tokens are valid
 - **Two-Level Caching**: 
 - **Rule-level cache** (`RuleLevelCache`): Stores masks by FSM hash and state, enabling sharing across grammars
 - **Grammar-level cache** (`ThreadSafeLRUCache`): Stores complete `CompiledGrammar` objects
 
 **Sources:** [cpp/grammar_compiler.cc33-131](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L33-L131) [python/xgrammar/compiler.py100-342](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L100-L342) [include/xgrammar/compiler.h1-116](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h#L1-L116)

 
### 4. Runtime Matching Layer

 The runtime layer uses `GrammarMatcher` to validate tokens and generate bitmasks during LLM generation:

 
```

```

 **Diagram: Runtime Matching Flow**

 Key components:

 
 - **`GrammarMatcher::Impl`**: Maintains parser state and orchestrates matching
 - **`EarleyParser`**: Implements Earley parsing algorithm with Scan, Predict, and Complete operations
 - **`ParserState`**: Represents current position in grammar (rule_id, sequence_id, element_id, sub_element_id)
 - **`Compact2DArray`**: Memory-efficient storage for parser state history
 
 **Sources:** [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc) [cpp/earley_parser.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h)

 
## Key Data Structures

 
### Grammar::Impl

 The central data structure representing a grammar AST:

 
| Field | Type | Purpose |
|---|---|---|
| rules_ | std::vector<Rule> | All grammar rules with names and body expressions |
| grammar_expr_data_ | std::vector<int32_t> | Flat array of all expression data (CSR format) |
| grammar_expr_indptr_ | std::vector<int32_t> | Start indices for each expression in data array |
| root_rule_id_ | int32_t | Index of the root rule |
| complete_fsm | CompactFSM | Optional unified FSM for entire grammar |
| per_rule_fsms | std::vector<std::optional<CompactFSMWithStartEnd>> | FSM for each rule |
| allow_empty_rule_ids | std::vector<int32_t> | Rules that can match empty string |

 **Sources:** [cpp/grammar_impl.h70-297](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L70-L297)

 
### GrammarExpr Types

 Each `GrammarExpr` is stored with a type tag and variable-length data:

 
```

```

 **Diagram: GrammarExpr Type Hierarchy**

 **Sources:** [cpp/grammar_impl.h108-151](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L108-L151)

 
### AdaptiveTokenMask

 Represents valid tokens for a given parser state, with multiple storage strategies:

 
```

```

 The mask automatically selects the most memory-efficient representation based on the number of accepted/rejected tokens (threshold: `USE_BITSET_THRESHOLD`).

 **Sources:** [cpp/compiled_grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/compiled_grammar_impl.h)

 
## Data Flow Through the System

 The following sequence diagram illustrates a complete generation cycle:

 
```

```

 **Diagram: Complete Generation Cycle Data Flow**

 **Sources:** [cpp/grammar_compiler.cc38-131](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L38-L131) [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc)

 
## Python-C++ Interface

 The Python API is exposed through nanobind bindings, with a clean object-oriented interface:

 
```

```

 **Diagram: Python-C++ Architecture**

 All Python classes (`Grammar`, `GrammarCompiler`, `CompiledGrammar`, `GrammarMatcher`) inherit from `XGRObject` which holds a `_handle` attribute pointing to the C++ implementation. The nanobind bindings in [python/xgrammar/nanobind.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/nanobind.cc) expose C++ methods as Python methods.

 **Key Design Patterns:**

 
 - **Handle-based ownership**: Python objects hold handles to C++ implementations, managed by nanobind's reference counting
 - **Zero-copy tensor passing**: Uses DLTensor protocol for efficient GPU memory sharing between PyTorch and C++ kernels
 - **Consistent API**: Python methods directly map to C++ methods with minimal overhead
 
 **Sources:** [python/xgrammar/base.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/base.py) [python/xgrammar/grammar.py132-434](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L132-L434) [python/xgrammar/compiler.py100-342](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L100-L342)

 
## Multi-Level Caching Strategy

 XGrammar implements a sophisticated caching system to maximize reuse:

 
| Cache Level | Scope | Key | Value | Implementation |
|---|---|---|---|---|
| Grammar-level | Across requests | Grammar hash + tokenizer metadata | CompiledGrammar | ThreadSafeLRUCache in GrammarCompiler::Impl |
| Rule-level | Across grammars | FSM hash + state ID | AdaptiveTokenMask | RuleLevelCache |

 The rule-level cache enables sharing between different grammars that have similar structural patterns (e.g., multiple JSON schemas with common field types). The grammar-level cache provides instant retrieval for repeated schemas.

 Both caches support configurable memory limits with LRU eviction:

 
 - Grammar-level: Set via `GrammarCompiler(cache_limit_bytes=...)`
 - Rule-level: Set via `RuleLevelCache(max_cache_memory_size=...)`
 
 **Sources:** [cpp/grammar_functor.h407-441](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L407-L441) [cpp/grammar_compiler.cc35-131](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L35-L131)

 
## Threading and Parallelism

 The system leverages multi-threading in two key areas:

 
 - **Compilation**: `GrammarCompiler` uses a thread pool to parallelize token mask generation across FSM states

 
 - Configured via `max_threads` parameter (default: 8)
 - Implementation: [cpp/support/thread_pool.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/thread_pool.h)
 - **Batch Matching**: `BatchGrammarMatcher` processes multiple matchers concurrently

 
 - Useful for serving multiple requests with different schemas
 - Python API: [python/xgrammar/matcher.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py)
 
 All caches are thread-safe using mutexes to protect concurrent access.

 **Sources:** [cpp/grammar_compiler.cc40-60](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L40-L60) [cpp/support/thread_pool.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/thread_pool.h)

 
## Integration Points

 
### Tokenizer Integration

 The `TokenizerInfo` class provides vocabulary information to the compiler:

 
```

```

 **Diagram: Tokenizer Integration**

 The tokenizer info stores:

 
 - **sorted_decoded_vocab**: Tokens sorted lexicographically for binary search
 - **trie_subtree_nodes**: Prefix tree for efficient common prefix detection
 - **special_token_ids**: Set of special tokens to exclude from masking
 
 **Sources:** [include/xgrammar/tokenizer_info.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/tokenizer_info.h) [python/xgrammar/tokenizer_info.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/tokenizer_info.py)

 
### LLM Framework Integration

 XGrammar integrates with LLM frameworks through the bitmask API:

 
 - **Generate bitmask**: `matcher.fill_next_token_bitmask(bitmask, index)` (CPU)
 - **Apply to logits**: `apply_token_bitmask_inplace(logits, bitmask)` (GPU)
 - **Sample token**: LLM framework samples from masked logits
 - **Update matcher**: `matcher.accept_token(token_id)`
 
 The `apply_token_bitmask_inplace` function has three backend implementations:

 
 - **Triton** (default for Python): [python/xgrammar/kernels/apply_token_bitmask_triton.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_triton.py)
 - **CUDA**: [cpp/kernels/apply_token_bitmask.cu](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/kernels/apply_token_bitmask.cu)
 - **CPU**: [cpp/kernels/apply_token_bitmask_cpu.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/kernels/apply_token_bitmask_cpu.cc)
 
 **Sources:** [python/xgrammar/kernels/](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/) [cpp/kernels/](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/kernels/)
