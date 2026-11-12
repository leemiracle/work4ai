> 来源: [https://deepwiki.com/mlc-ai/xgrammar/8-runtime-matching-engine](https://deepwiki.com/mlc-ai/xgrammar/8-runtime-matching-engine)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Runtime Matching Engine

  Relevant source files 
 - [cpp/earley_parser.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc)
 - [cpp/earley_parser.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h)
 - [cpp/grammar_matcher.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc)
 - [python/xgrammar/kernels/__init__.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/__init__.py)
 - [python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py)
 - [python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py)
 - [python/xgrammar/matcher.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py)
 - [tests/python/test_grammar_matcher_ebnf.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_ebnf.py)
 
  The Runtime Matching Engine encompasses the core components that execute during LLM generation to validate token sequences against compiled grammars and generate token constraints. This layer operates in the inference loop, accepting tokens, maintaining parser state, and producing bitmasks that restrict the LLM's next token selection to grammar-compliant choices.

 For details on how grammars are compiled before runtime, see [Grammar Compilation](https://deepwiki.com/mlc-ai/xgrammar/2.2-grammar-compilation). For integration with LLM inference systems, see [LLM Integration Patterns](https://deepwiki.com/mlc-ai/xgrammar/8.5-llm-integration-patterns).

 
## Architecture Overview

 The Runtime Matching Engine consists of several interconnected components that work together to enforce grammar constraints during token generation:

 
```

```

 **Sources:** [cpp/grammar_matcher.cc1-467](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L1-L467) [python/xgrammar/matcher.py1-538](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L1-L538) [cpp/earley_parser.h1-486](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.h#L1-L486)

 
## Core Runtime Components

 
### GrammarMatcher

 `GrammarMatcher` is the primary stateful object that tracks parsing progress and generates token constraints. Each instance maintains its own Earley parser state and can independently validate token sequences.

 
| Component | File | Purpose |
|---|---|---|
| GrammarMatcher (Python) | python/xgrammar/matcher.py191-421 | Public Python API for token matching |
| GrammarMatcher::Impl (C++) | cpp/grammar_matcher.cc331-420 | Core implementation with Earley parser |
| EarleyParser | cpp/earley_parser.h219-482 | Base class implementing Earley algorithm |
| ParserState | cpp/earley_parser.h41-130 | Represents a position in the parsing process |

 **Constructor Parameters:**

 
```

```

 The matcher is initialized with a `CompiledGrammar` and maintains internal state including:

 
 - Earley parser states (scanable and completable)
 - Token acceptance history for rollback support
 - Stop token configuration
 
 **Sources:** [cpp/grammar_matcher.cc331-365](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L331-L365) [python/xgrammar/matcher.py209-258](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L209-L258)

 
### BatchGrammarMatcher

 `BatchGrammarMatcher` enables parallel processing of multiple matchers, leveraging multi-threading to fill token bitmasks concurrently for batched LLM inference.

 
```

```

 The batch matcher configuration:

 
 - `max_threads`: Number of worker threads (default: `hardware_concurrency / 2`)
 - Thread pool is created on-demand for each batch operation
 - Static methods for batch token acceptance without threading overhead
 
 **Sources:** [cpp/grammar_matcher.cc422-466](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L422-L466) [python/xgrammar/matcher.py423-537](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L423-L537)

 
## Runtime Generation Workflow

 The typical inference loop integrates the Runtime Matching Engine through a sequence of operations:

 
```

```

 **Key Operations:**

 
 - **`fill_next_token_bitmask(bitmask, index)`**: Analyzes current parser state and populates bitmask with acceptable tokens
 - **`apply_token_bitmask_inplace(logits, bitmask)`**: Applies bitmask to logits using hardware-specific kernel
 - **`accept_token(token_id)`**: Advances parser state by validating and accepting a token
 - **`is_terminated()`**: Checks if matching is complete (stop token accepted or grammar matched)
 
 **Sources:** [cpp/grammar_matcher.cc491-592](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L491-L592) [python/xgrammar/matcher.py260-384](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L260-L384)

 
## Token Acceptance and State Management

 Token acceptance is a multi-step process that validates tokens against the current grammar state and updates the Earley parser:

 
```

```

 **State Tracking:**

 The `GrammarMatcher::Impl` maintains several state components:

 
 - `scanable_state_history_`: History of scanable parser states at each input position
 - `rule_id_to_completable_states_`: Maps rule IDs to states that can complete them (for Earley completion)
 - `token_length_history`: Deque tracking the length of each accepted token for rollback
 - `stop_token_is_accepted_`: Flag indicating termination
 
 **Rollback Support:**

 The `rollback(num_tokens)` operation enables speculative decoding by reverting parser state:

 
```

```

 Implementation pops states from history:

 
 - Validates `num_tokens <= len(token_length_history)`
 - For each token, pops `token_length_history.back()` character states
 - Enables unlimited rollback (unlike older versions with `max_rollback_tokens`)
 
 **Sources:** [cpp/grammar_matcher.cc491-592](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L491-L592) [cpp/grammar_matcher.cc838-848](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L838-L848) [python/xgrammar/matcher.py359-368](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L359-L368)

 
## Token Bitmask Generation

 The `fill_next_token_bitmask()` operation is the performance-critical path that determines which tokens are grammar-compliant from the current state:

 
```

```

 **Adaptive Token Mask Cache:**

 The `CompiledGrammar` contains a pre-computed cache (`adaptive_token_mask_cache`) that maps `ParserState` to `AdaptiveTokenMask`. Each mask categorizes tokens:

 
| Store Type | Description | Usage Pattern |
|---|---|---|
| kAcceptedBitset | Bitset of accepted tokens | When accepted tokens < rejected tokens |
| kAccepted | Vector of accepted token indices | For sparse accepted sets |
| kRejected | Vector of rejected token indices | When rejected tokens < accepted tokens |

 **Optimization Techniques:**

 
 - **Longest Common Prefix (LCP)**: Reuses parsing work between similar tokens by tracking matched prefixes [cpp/grammar_matcher.cc714-728](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L714-L728)
 - **First Character Filtering**: Pre-computed masks eliminate tokens with invalid first characters
 - **Subtree Range Pruning**: When a token prefix is rejected, all tokens in its trie subtree are rejected [cpp/grammar_matcher.cc702-708](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L702-L708)
 - **Union/Intersection Logic**:

 
 - Accepted tokens: union across all states
 - Rejected tokens: intersection across all states
 - Final mask: `accepted | (all_tokens - rejected)`
 
 **Sources:** [cpp/grammar_matcher.cc624-777](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L624-L777) [cpp/grammar_matcher.cc850-905](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L850-L905)

 
## Hardware Acceleration for Bitmask Application

 Once the bitmask is generated, it must be applied to the LLM's logits tensor. XGrammar provides multiple backend implementations optimized for different hardware:

 
```

```

 **Backend Selection Logic:**

 
```

```

 **Triton Kernel Implementation:**

 The Triton kernel [python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py12-78](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py#L12-L78) achieves high throughput by:

 
 - Processing vocabulary in blocks of size 4096
 - Distributing work across streaming multiprocessors
 - Unpacking 32-bit integers into individual bits
 - Vectorized masking operations
 
 **CUDA Native Implementation:**

 The CUDA backend [python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py1-120](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py#L1-L120) compiles a custom CUDA kernel at runtime using `torch.utils.cpp_extension.load_inline()`. This is useful for:

 
 - C++-based inference engines that need tight integration
 - Systems requiring maximum control over CUDA execution
 - Environments where Triton is not available
 
 **CPU Implementation:**

 The CPU backend [cpp/grammar_matcher.cc89-231](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L89-L231) uses the C++ `DynamicBitset` class to efficiently process bitmasks:

 
 - Handles both float32 and float16/bfloat16 logits
 - Supports selective application via `indices` parameter
 - Direct memory access with minimal overhead
 
 **Sources:** [python/xgrammar/matcher.py58-189](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L58-L189) [python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py12-127](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py#L12-L127) [python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py1-120](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/kernels/apply_token_bitmask_inplace_cuda.py#L1-L120) [cpp/grammar_matcher.cc89-231](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L89-L231)

 
## Batch Processing

 The `BatchGrammarMatcher` enables efficient parallel processing of multiple matchers, essential for high-throughput inference:

 
```

```

 **Configuration:**

 
```

```

 The implementation:

 
 - Creates a new `ThreadPool` for each batch operation (thread pools cannot be reused)
 - Defaults to `hardware_concurrency / 2` for `"auto"` mode
 - Validates `max_threads >= 1` and caps at `hardware_concurrency`
 - Provides static methods `batch_accept_token()` and `batch_accept_string()` without threading
 
 **Use Cases:**

 
 - Batched LLM serving with per-request grammars
 - Speculative decoding with multiple candidate sequences
 - Multi-turn conversations with different grammar constraints
 
 **Sources:** [cpp/grammar_matcher.cc422-466](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L422-L466) [cpp/grammar_matcher.cc932-975](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L932-L975) [python/xgrammar/matcher.py423-537](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/matcher.py#L423-L537)

 
## Performance Characteristics

 The Runtime Matching Engine is designed for minimal latency overhead in the LLM generation loop:

 
| Operation | Typical Latency | Scaling Factor |
|---|---|---|
| fill_next_token_bitmask() | 10-100 μs | O(vocab_size × num_states) with heavy caching |
| accept_token() | 5-50 μs | O(token_length × num_states) |
| apply_token_bitmask_inplace() (GPU) | 5-20 μs | O(vocab_size / parallelism) |
| rollback() | 1-10 μs | O(num_tokens) |

 **Key Performance Features:**

 
 - **Adaptive Token Mask Caching**: Pre-computed masks for common parser states eliminate redundant token validation [cpp/grammar_matcher.cc634-669](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L634-L669)
 - **Earley Parser Efficiency**: The new Earley-based implementation significantly reduces the number of active states compared to previous stack-based approaches
 - **Longest Common Prefix (LCP) Optimization**: Tokens sharing prefixes reuse parsing work, reducing redundant state exploration
 - **Hardware-Specific Kernels**: Triton and CUDA kernels achieve near-peak memory bandwidth for bitmask application
 - **Bitset Operations**: Using `DynamicBitset` with packed 32-bit integers minimizes memory traffic compared to byte-based masks
 
 **Sources:** [cpp/grammar_matcher.cc624-777](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_matcher.cc#L624-L777) [cpp/earley_parser.cc1-1425](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/earley_parser.cc#L1-L1425)
