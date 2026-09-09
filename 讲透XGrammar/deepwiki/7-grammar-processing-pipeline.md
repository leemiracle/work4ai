> 来源: [https://deepwiki.com/mlc-ai/xgrammar/7-grammar-processing-pipeline](https://deepwiki.com/mlc-ai/xgrammar/7-grammar-processing-pipeline)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Grammar Processing Pipeline

  Relevant source files 
 - [cpp/grammar_compiler.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc)
 - [cpp/grammar_functor.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc)
 - [cpp/grammar_functor.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h)
 - [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h)
 - [cpp/grammar_parser.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc)
 - [tests/python/test_grammar_parser.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py)
 
  
## Purpose and Scope

 This document provides a comprehensive overview of the grammar processing pipeline in xgrammar, covering the transformation of grammar definitions from various input formats through parsing, optimization, and compilation into efficient runtime representations. The pipeline encompasses all stages from input schema to compiled grammar objects with precomputed token masks.

 For details on specific input format conversions (JSON Schema, Regex, Structural Tags), see [Grammar Input Formats](https://deepwiki.com/mlc-ai/xgrammar/4-grammar-input-formats). For runtime matching using compiled grammars, see [Runtime Matching Engine](https://deepwiki.com/mlc-ai/xgrammar/8-runtime-matching-engine). For the internal representation of grammars, see [Grammar Representation](https://deepwiki.com/mlc-ai/xgrammar/2.1-grammar-representation).

 
## Pipeline Overview

 The grammar processing pipeline consists of six major stages:

 
```

```

 **Title**: Complete Grammar Processing Pipeline

 Sources: [cpp/grammar_parser.cc427-959](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L427-L959) [cpp/grammar_functor.cc1-2544](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L1-L2544) [cpp/grammar_compiler.cc1-1283](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L1283)

 
## Core Data Structures

 The pipeline operates on several key data structures that evolve through each stage:

 
| Structure | Type | Purpose | Location |
|---|---|---|---|
| Grammar::Impl | CSR-based AST | Internal grammar representation with rules and expressions | cpp/grammar_impl.h70-279 |
| GrammarExpr | Tagged union | Individual grammar expressions (sequences, choices, character classes, etc.) | cpp/grammar_impl.h132-150 |
| Rule | Struct | Named grammar rule with body and optional lookahead assertion | cpp/grammar_impl.h73-83 |
| CompactFSM | State machine | Minimized finite state machine for pattern matching | Referenced in cpp/grammar_impl.h249 |
| CompiledGrammar | Container | Final compiled output with FSMs and token masks | Referenced in cpp/grammar_compiler.cc19 |

 Sources: [cpp/grammar_impl.h70-279](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L70-L279)

 
## Stage 1: Format Conversion

 Before parsing, input formats are normalized to EBNF strings:

 
```

```

 **Title**: Input Format Normalization to EBNF

 The conversion process produces EBNF strings that can be uniformly processed by the parser. Each converter translates domain-specific constructs into equivalent EBNF productions.

 Sources: High-level architecture diagrams

 
## Stage 2: EBNF Parsing and Grammar Construction

 The parsing stage transforms EBNF strings into the internal Grammar representation:

 
```

```

 **Title**: EBNF Parsing and Grammar Object Construction

 
### Lexical Analysis

 The `EBNFLexer` performs tokenization with the following token types:

 
 - **Literals**: `StringLiteral`, `IntegerLiteral`, `BooleanLiteral`
 - **Identifiers**: `Identifier`, `RuleName`
 - **Operators**: `Assign` (`::=`), `Pipe` (`|`), `Star` (`*`), `Plus` (`+`), `Question` (`?`)
 - **Delimiters**: `LParen`, `RParen`, `LBracket`, `RBracket`, `LBrace`, `RBrace`
 - **Character Classes**: `CharInCharClass`, `EscapeInCharClass`, `Dash`, `Caret`
 - **Special**: `LookaheadLParen` (`(=`)
 
 Sources: [cpp/grammar_parser.cc24-425](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L24-L425)

 
### Parsing Process

 The `EBNFParser` uses recursive descent parsing with these key methods:

 
| Method | Purpose | Grammar Construct |
|---|---|---|
| ParseRule() | Parse complete rule definition | rule_name ::= body |
| ParseChoices() | Parse alternation | expr1 \| expr2 \| ... |
| ParseSequence() | Parse concatenation | expr1 expr2 ... |
| ParseElementWithQuantifier() | Parse element with optional quantifier | expr*, expr+, expr?, expr{n,m} |
| ParseElement() | Parse atomic element | String, character class, rule reference, grouping |
| ParseCharClass() | Parse character class | [a-z], [^0-9] |
| ParseLookaheadAssertion() | Parse lookahead | (=expr) |

 The parser builds the grammar incrementally using `GrammarBuilder`, which maintains the CSR-format data structures for rules and expressions.

 Sources: [cpp/grammar_parser.cc427-968](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L427-L968)

 
### Quantifier Expansion

 Quantifiers are expanded into equivalent rule references:

 
 - `expr*` → `rule ::= "" | expr rule`
 - `expr+` → `rule ::= expr rule | expr`
 - `expr?` → `rule ::= "" | expr`
 - `expr{n}` → `expr expr ... expr` (n times)
 - `expr{n,m}` → Creates helper rules for bounded repetition
 - `[a-z]*` → Special `kCharacterClassStar` expression type for efficiency
 
 For large repetition ranges (>128), the parser uses a hybrid approach combining explicit unrolling with the `kRepeat` expression type to avoid exponential grammar size growth.

 Sources: [cpp/grammar_parser.cc726-912](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L726-L912)

 
## Stage 3: Grammar Normalization

 Normalization transforms the grammar into a canonical form for efficient processing:

 
```

```

 **Title**: Grammar Normalization Pipeline

 
### Normalization Goals

 The normalized grammar form ensures:

 
 - **Each rule body** is either:

 
 - A `kChoices` expression containing sequences of elements, OR
 - A `kTagDispatch` macro expression
 - **Sequences contain only elements**: `kByteString`, `kCharacterClass`, `kCharacterClassStar`, `kRuleRef`, `kRepeat`
 - **Empty choices first**: If a rule accepts empty string, it appears as the first choice
 - **Lookahead assertions** are sequences of elements
 
 
### Transformation Examples

 
| Before | After | Transformation |
|---|---|---|
| A ::= ("a") | A ::= (("a")) | Single sequence wrapped in choices |
| A ::= (a) (((b)) (c)) | A ::= ((a b c)) | Nested sequences flattened |
| A ::= (a \| (b \| (c \| ""))) | A ::= ("" \| (a) \| (b) \| (c)) | Nested choices flattened, empty moved first |
| A ::= (a \| (b (c \| d))) | A ::= ((a) \| (b A_1))A_1 ::= ((c) \| (d)) | Nested choice extracted to new rule |

 Sources: [cpp/grammar_functor.cc172-492](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L172-L492) [tests/python/test_grammar_parser.py476-495](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py#L476-L495)

 
### Implementation

 The normalization process uses the visitor pattern via `GrammarFunctor` base class:

 
 - `SingleElementExprEliminator` - Removes redundant single-element wrappers
 - `StructureNormalizerImpl` - Enforces canonical structure 
 - `VisitRuleBody()` - Ensures top-level is choices
 - `VisitChoices_()` - Flattens nested choices, moves empty to front
 - `VisitSequence_()` - Flattens nested sequences, extracts nested choices to new rules
 
 Sources: [cpp/grammar_functor.cc172-492](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L172-L492)

 
## Stage 4: Grammar Optimization

 The optimization stage applies multiple transformation passes to improve runtime efficiency:

 
```

```

 **Title**: Grammar Optimization Pass Sequence

 
### Byte String Fusion

 Merges consecutive `kByteString` expressions in sequences to reduce grammar size and improve matching performance. This is implemented as a `GrammarMutator` that traverses sequences and concatenates adjacent byte strings.

 Sources: Referenced in [cpp/grammar_functor.h302-307](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L302-L307)

 
### Rule Inlining

 The `RuleInliner` inlines rules that meet these criteria:

 
 - The rule body is a `kChoices` expression
 - None of the choices are empty strings
 - None of the choices contain `kRuleRef` expressions
 - The rule is referenced only at the beginning of sequences
 
 **Example**:

 
```
root ::= rule1 "a" | rule2 "b"
rule1 ::= "x" | "y"
rule2 ::= "p" | "q"
```

 After inlining:

 
```
root ::= ("x" "a") | ("y" "a") | ("p" "b") | ("q" "b")
```

 The implementation uses `CheckIfRuleCanBeInlined()` to determine eligibility and expands inline during the `VisitChoices()` method.

 Sources: [cpp/grammar_functor.cc503-584](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L503-L584) [tests/python/test_grammar_parser.py497-527](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py#L497-L527)

 
### Dead Code Elimination

 The `DeadCodeEliminator` removes unreachable rules:

 
 - `UsedRulesAnalyzer` performs BFS from root rule to find all reachable rules
 - Creates a new grammar containing only the reachable rules
 - Updates all rule references to use new rule IDs
 
 Sources: [cpp/grammar_functor.cc589-684](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L589-L684) [tests/python/test_grammar_parser.py529-581](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py#L529-L581)

 
### Lookahead Assertion Analysis

 The `LookaheadAssertionAnalyzer` automatically detects and adds lookahead assertions to improve matching efficiency:

 **Detection logic**:

 
 - If a rule `R` appears exactly once in the middle of a sequence (not at the end)
 - And `R` is not referenced in any `kTagDispatch` expression
 - Then the suffix following `R` becomes its lookahead assertion
 
 **Example**:

 
```
root ::= "a" rule1 "b" rule2
rule1 ::= "x"
```

 After analysis:

 
```
rule1 ::= ("x") (=("b" rule2))
```

 The lookahead allows early rejection during token matching when the lookahead cannot be satisfied.

 Sources: [cpp/grammar_functor.cc686-808](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L686-L808) [tests/python/test_grammar_parser.py454-473](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py#L454-L473)

 
### Allow-Empty Rule Analysis

 The `AllowEmptyRuleAnalyzer` identifies all rules that can match empty strings:

 
 - **Direct analysis**: Finds rules with explicit `kEmptyStr` in choices or all-optional sequences
 - **Transitive closure**: Uses Bellman-Ford algorithm on the rule reference graph to find indirect empty rules
 
 This information is stored in `Grammar::Impl::allow_empty_rule_ids` and used during FSM construction and repetition normalization.

 Sources: [cpp/grammar_functor.cc862-963](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L862-L963)

 
### Repetition Normalization

 The `RepetitionNormalizer` optimizes `kRepeat` expressions when the repeated rule can match empty strings:

 
 - If the rule in `{n,m}` is nullable, transforms to `{0,m}` to reduce matching uncertainty
 - This enables more efficient parsing by eliminating redundant checks
 
 Sources: [cpp/grammar_functor.h362-365](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L362-L365) [tests/python/test_grammar_parser.py778-795](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py#L778-L795)

 
## Stage 5: FSM Construction

 The optimized grammar is converted to Finite State Machines for efficient pattern matching:

 
```

```

 **Title**: FSM Construction and Optimization Pipeline

 
### FSM Building Process

 The `GrammarFSMBuilder` constructs FSMs using Thompson's construction:

 
| Expression Type | FSM Construction Method | Output |
|---|---|---|
| kByteString | ByteString() | Sequential states for each byte |
| kCharacterClass | CharacterClass() | Transitions for character ranges with UTF-8 encoding |
| kSequence | Sequence() | Concatenation of component FSMs |
| kChoices | Choices() | Union of component FSMs with epsilon transitions |
| kRuleRef | RuleRef() | Edge to referenced rule's FSM |
| kTagDispatch | TagDispatch() | Aho-Corasick automaton for trigger detection |

 Sources: [cpp/grammar_functor.h342-355](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L342-L355)

 
### Unicode and UTF-8 Handling

 Character classes are converted to UTF-8 byte ranges:

 
```

```

 This ensures proper matching of multi-byte UTF-8 sequences as byte-level transitions in the FSM.

 Sources: [cpp/grammar_functor.cc965-992](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc#L965-L992)

 
### DFA Minimization

 After constructing NFAs, the system applies:

 
 - **Subset Construction**: Converts NFA to DFA by computing epsilon closures and creating states for each reachable set of NFA states
 - **Hopcroft's Algorithm**: Minimizes the DFA by partitioning states into equivalence classes
 - **Compaction**: Stores the minimized FSM in `CompactFSM` format with compressed edge representation
 
 The resulting FSMs are stored in `Grammar::Impl::per_rule_fsms` as `std::optional<CompactFSMWithStartEnd>`, where `std::nullopt` indicates the rule should be matched using Earley parsing instead.

 Sources: High-level architecture, [cpp/grammar_impl.h249-256](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h#L249-L256)

 
## Stage 6: Token Mask Precomputation

 The final compilation stage generates adaptive token masks for efficient LLM token filtering:

 
```

```

 **Title**: Token Mask Generation and Caching

 
### Adaptive Token Mask Structure

 `AdaptiveTokenMask` stores token acceptance information in three possible formats:

 
```

```

 The format is chosen based on which representation is more compact (threshold: 512 tokens). This adaptive representation significantly reduces memory usage.

 Sources: Referenced in [cpp/grammar_compiler.cc35-295](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L35-L295)

 
### First Character Filtering

 The `GetFirstCharacterMask()` method analyzes the FSM edges from the initial state to determine which first characters are possible:

 
```

```

 This allows rejecting entire ranges of tokens based on their first byte, dramatically reducing the number of tokens that need full matching.

 Sources: [cpp/grammar_compiler.cc669-682](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L669-L682)

 
### Speculative Calculation Optimization

 For self-recursive patterns (e.g., `[a-z]*`), the system detects that certain tokens can be definitively accepted without full parsing:

 
 - **Detection**: Check if FSM state has edges to itself or recursive rule references
 - **Application**: If all characters in a token match the recursive pattern, accept immediately
 - **TagDispatch special case**: For structural tags, use precomputed second-slicing bitsets
 
 This optimization is crucial for string content matching where thousands of tokens may be valid continuations.

 Sources: [cpp/grammar_compiler.cc416-474](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L416-L474)

 
### Token Matching with Longest Common Prefix

 To avoid redundant work when processing similar tokens (e.g., "hello" vs "help"):

 
 - **Sort tokens lexicographically** (maintained in `TokenizerInfo::sorted_decoded_vocab`)
 - **Compute LCP** with previous token
 - **Rollback parser state** only for the non-matching suffix
 - **Continue parsing** from the LCP position
 
 This reduces the average parsing work per token significantly.

 Sources: [cpp/grammar_compiler.cc476-667](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L476-L667)

 
### Lookahead Assertion Checking

 For tokens that reach the end of a rule, the `IsTokenPassLookaheadAssertion()` method verifies:

 
 - Push the lookahead assertion onto the parser stack
 - Try to match suffixes of the token against the lookahead
 - Find the longest matching suffix
 - Classify token as: 
 - **Accepted**: Lookahead fully matched
 - **Uncertain**: Lookahead partially matched (needs more context)
 - **Rejected**: Lookahead cannot match
 
 Sources: [cpp/grammar_compiler.cc297-350](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L297-L350)

 
### Rule-Level Caching

 The `RuleLevelCache` enables sharing token masks across different grammar instances:

 **Cache key**: `(fsm_hash, fsm_state_id)`

 
 - `fsm_hash`: Hash of the FSM structure (computed by `GrammarFSMHasher`)
 - `fsm_state_id`: Normalized state ID within the FSM
 
 **Benefits**:

 
 - Masks computed for one grammar can be reused for similar grammars
 - Especially effective for common patterns (JSON, numbers, strings)
 - LRU eviction policy maintains bounded memory usage
 
 Sources: [cpp/grammar_functor.h407-440](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L407-L440) [cpp/grammar_compiler.cc698-738](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L698-L738)

 
## Pipeline Orchestration

 The complete pipeline is orchestrated by `GrammarCompiler`:

 
```

```

 **Title**: GrammarCompiler Orchestration Flow

 
### Compilation Entry Points

 The main compilation API is exposed through `GrammarCompiler::Compile()`:

 
```

```

 This method:

 
 - Checks if the grammar is already optimized (via `grammar->optimized` flag)
 - If not, applies normalization and optimization passes
 - Computes FSM hashes for cache lookup
 - Checks grammar-level cache for previously compiled result
 - If cache miss, generates token masks for all rules and states
 - Stores result in cache and returns `CompiledGrammar`
 
 Sources: Referenced in [cpp/grammar_compiler.cc1-1283](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L1283)

 
### Multi-threading Support

 The compiler supports parallel token mask generation:

 
 - `ThreadPool` configured via `GrammarCompiler::max_threads`
 - Masks for different rules/states can be computed independently
 - Particularly beneficial for large grammars with many rules
 
 Sources: Referenced in [cpp/grammar_compiler.cc1-50](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L50)

 
### Memory Management

 The system employs several strategies to control memory usage:

 
 - **Adaptive storage** in `AdaptiveTokenMask` (indices vs bitset)
 - **LRU cache** in `RuleLevelCache` with configurable size limit
 - **Grammar-level cache** in `GrammarCompiler` (also LRU-based)
 - **Compact FSM representation** minimizing memory footprint
 
 These strategies enable efficient operation even with large vocabularies (32K+ tokens) and complex grammars.

 Sources: [cpp/grammar_compiler.cc1-1283](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_compiler.cc#L1-L1283) [cpp/grammar_functor.h407-440](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.h#L407-L440)
