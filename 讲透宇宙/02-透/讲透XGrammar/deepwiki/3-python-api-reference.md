> 来源: [https://deepwiki.com/mlc-ai/xgrammar/3-python-api-reference](https://deepwiki.com/mlc-ai/xgrammar/3-python-api-reference)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Python API Reference

  Relevant source files 
 - [cpp/grammar.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc)
 - [include/xgrammar/compiler.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h)
 - [include/xgrammar/grammar.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h)
 - [include/xgrammar/object.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/object.h)
 - [python/xgrammar/compiler.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py)
 - [python/xgrammar/grammar.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py)
 - [python/xgrammar/kernels/__init__.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/__init__.py)
 - [python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py)
 - [python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py)
 - [python/xgrammar/matcher.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py)
 
  This document provides comprehensive reference documentation for XGrammar's Python API. The API serves as a high-level interface to the underlying C++ engine, providing Pythonic access to efficient grammar-guided text generation capabilities for LLMs.

 
## API Organization

 The XGrammar Python API is organized into the following modules:

 
| Module | Primary Classes | Purpose |
|---|---|---|
| xgrammar.grammar | Grammar | Grammar creation from JSON Schema, EBNF, regex, and structural tags |
| xgrammar.compiler | GrammarCompiler, CompiledGrammar | Grammar compilation with caching and multi-threading |
| xgrammar.matcher | GrammarMatcher, BatchGrammarMatcher | Stateful token matching, batch processing, and bitmask generation |
| xgrammar.tokenizer_info | TokenizerInfo | Tokenizer vocabulary integration |
| xgrammar.structural_tag | StructuralTag | Structural tag format definitions |
| xgrammar.kernels | (functions) | Hardware-optimized bitmask application kernels |
| xgrammar.testing | (utilities) | Testing and debugging utilities |

 Sources: [python/xgrammar/__init__.py1-57](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/__init__.py#L1-L57) [python/xgrammar/grammar.py1-434](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L1-L434) [python/xgrammar/compiler.py1-342](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L1-L342) [python/xgrammar/matcher.py1-503](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L1-L503)

 
## Subsections

 This API reference is organized into the following detailed subsections:

 
 - **2.1 Grammar Creation and Formats** - `Grammar` class and factory methods for creating grammars from various input formats
 - **2.2 Grammar Compilation** - `GrammarCompiler` for efficient compilation with caching and parallelization
 - **2.3 Grammar Matching and Validation** - `GrammarMatcher` for stateful token acceptance and validation
 - **2.4 Batch Processing** - `BatchGrammarMatcher` for parallel processing of multiple matchers with multi-threading support
 - **2.5 Token Bitmask Operations** - Functions for allocating and applying token bitmasks to LLM logits
 - **2.6 Tokenizer Integration** - `TokenizerInfo` class for integrating tokenizer vocabularies
 - **2.7 Testing and Development Utilities** - Helper functions for testing and debugging grammars
 
 
## Python-C++ Binding Architecture

 The Python API wraps high-performance C++ implementations using nanobind. All core classes inherit from `XGRObject`, which manages the C++ object lifecycle through internal `_handle` attributes.

 
### Python-C++ Layer Structure

 **Diagram: Python-C++ API Binding Architecture**

 
```

```

 Sources: [python/xgrammar/base.py1-26](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/base.py#L1-L26) [python/xgrammar/grammar.py9](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L9-L9) [python/xgrammar/compiler.py8](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L8-L8) [python/xgrammar/matcher.py12](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L12-L12) [cpp/nanobind/nanobind.cc140-456](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/nanobind/nanobind.cc#L140-L456) [include/xgrammar/grammar.h79-185](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L79-L185) [include/xgrammar/matcher.h67-205](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/matcher.h#L67-L205)

 
### Typical Usage Workflow

 **Diagram: End-to-End API Workflow**

 
```

```

 Sources: [python/xgrammar/grammar.py154-350](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L154-L350) [python/xgrammar/compiler.py100-325](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L100-L325) [python/xgrammar/matcher.py156-349](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L156-L349) [tests/python/test_grammar_matcher_basic.py99-127](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_basic.py#L99-L127)

 
## Core Classes Overview

 
### Grammar Creation

 The `Grammar` class ([python/xgrammar/grammar.py132-434](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L132-L434)) represents a grammar in EBNF format and provides static factory methods for creating grammars from various sources:

 
| Method | Input Format | Purpose |
|---|---|---|
| Grammar.from_ebnf() | EBNF string | Parse grammar from Extended Backus-Naur Form |
| Grammar.from_json_schema() | JSON Schema / Pydantic model | Convert JSON schema to grammar |
| Grammar.from_regex() | Regex string | Convert regular expression to grammar |
| Grammar.from_structural_tag() | StructuralTag | Create grammar from structural tag definition |
| Grammar.builtin_json_grammar() | Built-in | Get standard JSON grammar |

 Sources: [python/xgrammar/grammar.py132-434](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L132-L434) [include/xgrammar/grammar.h79-185](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L79-L185)

 
### Grammar Compilation

 The `GrammarCompiler` class ([python/xgrammar/compiler.py100-342](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L100-L342)) compiles grammars with a tokenizer vocabulary, enabling efficient token mask generation. It includes:

 
 - Multi-threaded compilation support (configurable via `max_threads`)
 - LRU cache for compiled grammars (configurable via `cache_enabled` and `cache_limit_bytes`)
 - Methods for compiling from various formats: `compile_json_schema()`, `compile_grammar()`, `compile_regex()`, `compile_structural_tag()`
 
 The `CompiledGrammar` class ([python/xgrammar/compiler.py19-98](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L19-L98)) stores the compilation result and can be serialized/deserialized for persistence.

 Sources: [python/xgrammar/compiler.py19-342](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L19-L342) [include/xgrammar/compiler.h24-111](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h#L24-L111)

 
### Token Matching

 The `GrammarMatcher` class ([python/xgrammar/matcher.py156-386](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L156-L386)) maintains stateful parsing and generates token masks:

 
| Method | Purpose |
|---|---|
| accept_token() | Accept a token and advance the parser state |
| accept_string() | Accept a string and advance the parser state |
| fill_next_token_bitmask() | Generate bitmask of valid next tokens |
| find_jump_forward_string() | Find deterministic prefix for jump-forward decoding |
| rollback() | Rollback parser state by N tokens |
| reset() | Reset parser to initial state |
| is_terminated() | Check if parsing is complete |

 The `BatchGrammarMatcher` class ([python/xgrammar/matcher.py388-503](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L388-L503)) provides batched operations for parallel processing of multiple matchers:

 
| Method | Purpose |
|---|---|
| batch_fill_next_token_bitmask() | Generate bitmasks for multiple matchers in parallel |
| batch_accept_token() | Accept tokens for multiple matchers (static method) |
| batch_accept_string() | Accept strings for multiple matchers (static method) |

 Sources: [python/xgrammar/matcher.py156-503](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L156-L503) [include/xgrammar/matcher.h67-205](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/matcher.h#L67-L205)

 
## Data Type Definitions

 The API uses several key data types for token bitmask operations:

 
| Type | Definition | Usage |
|---|---|---|
| bitmask_dtype | torch.int32 | Standard dtype for token bitmasks |
| BatchSize | int | Number of sequences in a batch |
| VocabSize | int | Size of tokenizer vocabulary |
| BitmaskShape | Tuple[int, int] | (batch_size, ceil(vocab_size / 32)) |

 The bitmask represents token validity as compressed bits, where each bit indicates whether a token is allowed (1) or masked (0) for the next generation step.

 Sources: [python/xgrammar/matcher.py15-21](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L15-L21)

 
## Module Function Reference

 
### Core Bitmask Functions

 **`get_bitmask_shape(batch_size: int, vocab_size: int) -> Tuple[int, int]`**

 Returns the required shape for token bitmasks: `(batch_size, ceil(vocab_size / 32))`.

 **`allocate_token_bitmask(batch_size: int, vocab_size: int) -> torch.Tensor`**

 Allocates a CPU tensor for token bitmasks, initialized to all-ones (no masking).

 **`reset_token_bitmask(bitmask: torch.Tensor) -> None`**

 Resets a bitmask tensor to all-ones state.

 **`apply_token_bitmask_inplace(logits: torch.Tensor, bitmask: torch.Tensor, *, vocab_size: Optional[int] = None, indices: Optional[List[int]] = None) -> None`**

 Applies token bitmask to logits in-place, setting masked tokens to `-inf`. Supports batched operations and device-specific kernels for CPU, CUDA, and other hardware.

 Sources: [python/xgrammar/matcher.py19-154](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L19-L154)

 
### Hardware Kernel Dispatch

 The `apply_token_bitmask_inplace` function automatically dispatches to optimized kernels based on tensor device:

 
```

```

 Sources: [python/xgrammar/matcher.py139-153](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L139-L153) [python/xgrammar/kernels/__init__.py1-8](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/__init__.py#L1-L8)
