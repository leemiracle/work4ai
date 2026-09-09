> 来源: [https://deepwiki.com/mlc-ai/xgrammar/1-overview](https://deepwiki.com/mlc-ai/xgrammar/1-overview)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Overview

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
 
  XGrammar is a library for efficient, flexible, and portable **grammar-guided generation** for Large Language Models (LLMs). It constrains LLM outputs to follow specific grammars, schemas, or patterns by generating token-level bitmasks during inference. The library supports multiple input formats (EBNF, JSON Schema, regular expressions, structural tags) and provides high-performance runtime matching using Earley parsing with optimized finite state machines (FSMs).

 For specific topics:

 
 - Installation and basic usage: see [Installation and Setup](https://deepwiki.com/mlc-ai/xgrammar/1.1-installation-and-setup) and [Quick Start Guide](https://deepwiki.com/mlc-ai/xgrammar/1.2-quick-start-guide)
 - Core implementation details: see [Core Concepts](https://deepwiki.com/mlc-ai/xgrammar/2-core-concepts)
 - API reference: see [Python API Reference](https://deepwiki.com/mlc-ai/xgrammar/3-python-api-reference)
 - C++ implementation: see [C++ Implementation Details](https://deepwiki.com/mlc-ai/xgrammar/11-c++-implementation-details)
 
 **Sources:** [pyproject.toml1-161](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L1-L161) [include/xgrammar/xgrammar.h1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L1-L18) [README.md](https://github.com/mlc-ai/xgrammar/blob/c30554f7/README.md?plain=1)

 
---

 
## Library Purpose and Scope

 XGrammar enables **constrained generation** where LLM token sampling is restricted to valid continuations according to user-defined grammars. The library:

 
 - **Accepts multiple input formats** and converts them to a unified internal representation
 - **Compiles grammars** into optimized data structures with per-rule FSMs and adaptive token masks
 - **Validates token sequences** at runtime using an Earley parser
 - **Generates token bitmasks** that mark valid/invalid tokens for LLM samplers
 - **Integrates with LLM inference engines** via Python/C++ APIs with hardware-accelerated kernels
 
 The library is designed for production use with:

 
 - **Performance**: Multi-level caching, parallel compilation, optimized FSMs, hardware-specific kernels
 - **Flexibility**: Support for context-free grammars, JSON schemas, regex, mixed structured/unstructured generation
 - **Portability**: Cross-platform support (Linux, macOS, Windows) with CPU/CUDA/Triton backends
 
 **Sources:** [pyproject.toml1-24](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L1-L24) [include/xgrammar/xgrammar.h1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/xgrammar.h#L1-L18) [CMakeLists.txt1-145](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L1-L145)

 
---

 
## High-Level Architecture

 
### Component Layering

 
```

```

 XGrammar is organized into four primary layers:

 
 - **Input Layer**: Multiple format parsers and converters normalize inputs to EBNF
 - **Grammar Definition Layer**: EBNF is parsed into `Grammar::Impl` with CSR-based storage
 - **Compilation & Optimization Layer**: Grammars undergo optimization passes and FSM construction
 - **Runtime Matching Layer**: Earley parser validates sequences and generates token bitmasks
 
 **Sources:** [cpp/grammar.cc1-185](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L1-L185) [include/xgrammar/grammar.h1-189](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L1-L189) [include/xgrammar/compiler.h1-116](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h#L1-L116) [include/xgrammar/matcher.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/matcher.h)

 
---

 
### Data Flow: Schema to LLM Token Masking

 
```

```

 This diagram shows the complete transformation from user-provided schemas to runtime token masking. Key optimizations include:

 
 - **Compilation caching** to avoid redundant work across sessions
 - **Two-tier token mask caching** (grammar-level and rule-level)
 - **Adaptive mask storage** with three modes based on acceptance patterns
 - **Hardware-specific kernel dispatch** for efficient bitmask application
 
 **Sources:** [cpp/grammar.cc37-73](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L37-L73) [cpp/grammar_compiler.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc) [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc) [cpp/adaptive_token_mask.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/adaptive_token_mask.cc)

 
---

 
## Core Components

 
### Grammar Representation (`Grammar` and `Grammar::Impl`)

 The `Grammar` class represents context-free grammars internally using a **Compressed Sparse Row (CSR)** format for efficient storage and traversal.

 
| Component | Type | Description |
|---|---|---|
| rules_ | std::vector<std::string> | Rule names indexed by rule_id |
| grammar_expr_data_ | std::vector<int32_t> | Flattened GrammarExpr data in CSR format |
| grammar_expr_indptr_ | std::vector<int32_t> | Index pointers into expr_data (CSR indptr) |
| complete_fsm | CompactFSM | FSM for the entire grammar |
| per_rule_fsms | std::vector<CompactFSM> | Per-rule FSMs for each rule |

 **GrammarExpr Types** (stored in CSR format):

 
 - `ByteString`: UTF-8 byte sequences
 - `CharClass`: Unicode character ranges (e.g., `[a-z]`, `[^0-9]`)
 - `CharClassStar`: Kleene star over character class (e.g., `[a-z]*`)
 - `Sequence`: Concatenation of expressions
 - `Choices`: Alternatives (disjunction)
 - `RuleRef`: Reference to another rule by rule_id
 - `TagDispatch`: Special dispatch for structural tags
 - `EmptyStr`: Empty string (ε)
 
 **Sources:** [include/xgrammar/grammar.h32-78](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L32-L78) [cpp/grammar_data_structure.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_data_structure.h)

 
---

 
### Compilation Pipeline (`GrammarCompiler`)

 
```

```

 The `GrammarCompiler` orchestrates the compilation process:

 
 - **Normalization**: Convert grammar to standard form (choices of sequences)
 - **Inlining**: Substitute small rule definitions to reduce indirection
 - **Byte Fusion**: Merge consecutive byte strings for efficiency
 - **Dead Code Elimination**: Remove unreachable rules
 - **Lookahead Analysis**: Add assertions to guide parsing
 - **FSM Construction**: Build NFAs, convert to DFAs, minimize
 - **Token Mask Precomputation**: Generate adaptive masks with caching
 
 **Caching Strategy**:

 
 - **Grammar-level cache**: LRU cache storing entire `CompiledGrammar` objects (keyed by grammar hash + tokenizer metadata)
 - **Rule-level cache**: FSM hash-based cache for individual rule masks (shared across grammars)
 
 **Sources:** [cpp/grammar_compiler.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc) [cpp/grammar_functor.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc) [include/xgrammar/compiler.h50-111](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h#L50-L111)

 
---

 
### Runtime Matching (`GrammarMatcher` and Earley Parser)

 
```

```

 The `GrammarMatcher` uses an **Earley parser** for runtime validation:

 **Core Operations**:

 
 - `accept_token(token_id)`: Advance parser state by consuming a token via scan operation
 - `accept_string(input_str)`: Accept multiple bytes/tokens at once
 - `fill_next_token_bitmask(bitmask)`: Query adaptive masks to mark valid tokens
 - `rollback(num_tokens)`: Revert parser state for speculative decoding
 - `is_terminated()`: Check if grammar accepts current position
 
 **Key Optimizations**:

 
 - **First character filtering**: Precompute valid first bytes to reduce token candidates
 - **Longest Common Prefix (LCP)**: Share parsing work for tokens with common prefixes
 - **Speculative calculation**: Handle self-recursive patterns without full expansion
 - **Scanable state history**: `Compact2DArray` for efficient state storage
 
 **Sources:** [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc) [cpp/earley_parser.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc) [include/xgrammar/matcher.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/matcher.h)

 
---

 
## Python-C++ Integration

 
```

```

 **Architecture**:

 
 - **Python API**: High-level interface exposing `Grammar`, `GrammarCompiler`, `CompiledGrammar`, `GrammarMatcher`, `TokenizerInfo`
 - **nanobind layer**: Type-safe C++/Python bridge with automatic type conversions
 - **DLTensor protocol**: Zero-copy tensor sharing between Python (torch/numpy) and C++
 - **C++ static library**: Performance-critical algorithms compiled as `libxgrammar.a`
 
 **Build Process**:

 
 - `scikit-build-core` orchestrates CMake from `pyproject.toml`
 - CMake compiles C++ sources into static library
 - nanobind builds Python extension module linking against static library
 - `cibuildwheel` produces platform-specific wheels (manylinux, macOS, Windows)
 
 **Sources:** [pyproject.toml43-161](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L43-L161) [CMakeLists.txt1-145](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L1-L145) [cpp/nanobind/nanobind.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/nanobind/nanobind.cc) [python/xgrammar/base.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/base.py)

 
---

 
## Key Capabilities

 
### Multi-Format Input Support

 
| Format | Entry Point | Converter | Use Case |
|---|---|---|---|
| EBNF | Grammar.from_ebnf() | Direct parsing | General context-free grammars |
| JSON Schema | Grammar.from_json_schema() | JSONSchemaToEBNF() | Structured data generation |
| Regular Expression | Grammar.from_regex() | RegexToEBNF() | Pattern matching |
| Structural Tags | Grammar.from_structural_tag() | StructuralTagToGrammar() | Mixed structured/unstructured, tool calling |

 All formats are normalized to EBNF internally, then compiled through the same optimization pipeline.

 **Sources:** [python/xgrammar/grammar.py155-350](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L155-L350) [cpp/grammar.cc37-73](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L37-L73)

 
---

 
### Performance Optimizations

 XGrammar employs multiple optimization strategies:

 **Compilation-time**:

 
 - Grammar simplification (normalization, inlining, fusion)
 - FSM minimization using Hopcroft's algorithm
 - Dead code elimination
 - Multi-threaded compilation with configurable thread pool
 
 **Runtime**:

 
 - Two-tier caching (grammar-level LRU + rule-level FSM hash)
 - Adaptive token mask storage (accepted/rejected/bitset modes)
 - First character filtering to reduce token candidates
 - Longest Common Prefix (LCP) optimization
 - Speculative calculation for self-recursive patterns
 
 **Hardware acceleration**:

 
 - CPU backend: Vectorized operations
 - CUDA backend: GPU kernel for bitmask application
 - Triton backend: JIT-compiled kernels
 - Automatic backend selection based on tensor device
 
 **Sources:** [cpp/grammar_compiler.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc) [cpp/adaptive_token_mask.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/adaptive_token_mask.cc) [python/xgrammar/kernels/](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/)

 
---

 
### Structural Tags for Dynamic Format Switching

 Structural tags enable **mixed structured/unstructured generation** where the grammar switches between free-form text and constrained formats:

 
```

```

 **Use Cases**:

 
 - LLM tool calling (e.g., `<function=calculator>{"expr": "2+2"}</function>`)
 - Mixed format output (text with embedded JSON/XML)
 - Format variants (QwenXML, MiniMaxXML, DeepSeekXML)
 
 **Implementation**: `TagDispatch` grammar expression with trigger detection automaton

 **Sources:** [cpp/structural_tag/](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag/) [python/xgrammar/structural_tag.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/structural_tag.py) For detailed information see [Structural Tags Deep Dive](https://deepwiki.com/mlc-ai/xgrammar/6-structural-tags-deep-dive)

 
---

 
## Library Dependencies

 **Python Dependencies** (from `pyproject.toml`):

 
 - `pydantic`: Schema definition and validation
 - `torch>=1.10.0`: Tensor operations and DLTensor protocol
 - `transformers>=4.38.0`: HuggingFace tokenizer integration
 - `triton`: JIT-compiled GPU kernels (Linux x86_64 only)
 - `numpy`: Numerical operations
 
 **C++ Dependencies** (vendored in `3rdparty/`):

 
 - `picojson`: JSON parsing/serialization
 - `dlpack`: Tensor interchange format
 - `nanobind`: Python-C++ bindings
 - `cpptrace` (optional): Stack trace support for debugging
 - `googletest` (optional): C++ unit testing
 
 **Build Tools**:

 
 - CMake >=3.18
 - C++17 compiler (GCC, Clang, MSVC)
 - `scikit-build-core>=0.10.0`: Python package builder
 - `cibuildwheel`: Multi-platform wheel builder
 
 **Sources:** [pyproject.toml16-45](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L16-L45) [CMakeLists.txt1-145](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L1-L145) [3rdparty/](https://github.com/mlc-ai/xgrammar/blob/c30554f7/3rdparty/)

 
---

 
## Memory Management

 XGrammar uses **PImpl pattern** for major classes (`Grammar`, `CompiledGrammar`, `GrammarMatcher`, `GrammarCompiler`) with reference-counted shared pointers:

 
```

```

 **Benefits**:

 
 - Efficient object copying and passing (copies shared_ptr, not data)
 - Automatic memory management
 - Python-C++ object sharing without copies
 - Safe concurrent access to immutable compiled grammars
 
 **Memory-Efficient Data Structures**:

 
 - **CSR format**: Grammar expressions stored compactly
 - `CompactFSM`: Minimized FSM representation
 - `Compact2DArray`: Efficient 2D array for parser states
 - `DynamicBitset`: Packed bit arrays for token masks
 
 **Sources:** [include/xgrammar/object.h1-52](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/object.h#L1-L52) [cpp/grammar_data_structure.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_data_structure.h) [cpp/support/dynamic_bitset.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/support/dynamic_bitset.h)

 
---

 
## Platform Support

 **Supported Platforms**:

 
 - **Linux**: x86_64, aarch64 (manylinux wheels)
 - **macOS**: x86_64, arm64 (macOS 10.14+)
 - **Windows**: AMD64
 
 **Python Versions**: 3.9, 3.10, 3.11, 3.12, 3.13 (limited platform support)

 **Hardware Backends**:

 
 - CPU: All platforms
 - CUDA: Linux/Windows with NVIDIA GPUs
 - Triton: Linux x86_64 only
 - Metal (experimental): macOS arm64 via `mlx-lm`
 
 **Build Configuration** (from `CMakeLists.txt`):

 
 - `XGRAMMAR_BUILD_PYTHON_BINDINGS`: Enable Python bindings (default: ON)
 - `XGRAMMAR_BUILD_CXX_TESTS`: Enable C++ tests (default: OFF)
 - `XGRAMMAR_ENABLE_CPPTRACE`: Enable stack traces (Linux only, default: OFF)
 - `XGRAMMAR_CUDA_ARCHITECTURES`: Target CUDA architectures (default: native)
 
 **Sources:** [pyproject.toml136-161](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L136-L161) [CMakeLists.txt17-46](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L17-L46) [.github/workflows/](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.github/workflows/)
