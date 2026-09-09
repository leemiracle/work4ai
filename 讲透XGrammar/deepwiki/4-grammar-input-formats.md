> 来源: [https://deepwiki.com/mlc-ai/xgrammar/4-grammar-input-formats](https://deepwiki.com/mlc-ai/xgrammar/4-grammar-input-formats)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Grammar Input Formats

  Relevant source files 
 - [cpp/grammar.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc)
 - [cpp/grammar_parser.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc)
 - [include/xgrammar/compiler.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h)
 - [include/xgrammar/grammar.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h)
 - [include/xgrammar/object.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/object.h)
 - [python/xgrammar/compiler.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py)
 - [python/xgrammar/grammar.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py)
 - [tests/python/test_grammar_parser.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py)
 
  XGrammar accepts grammar specifications in four formats: EBNF, JSON Schema, Regular Expressions, and Structural Tags. All formats are converted to a unified `Grammar::Impl` internal representation.

 This page provides an overview of the four input formats, the conversion pipeline, and API reference. For detailed syntax and features of each format:

 
 - [EBNF Grammar Specification](https://deepwiki.com/mlc-ai/xgrammar/4.1-ebnf-grammar-specification) - Native grammar format with full control
 - [JSON Schema Conversion](https://deepwiki.com/mlc-ai/xgrammar/4.2-json-schema-conversion) - Structured JSON output validation
 - [Regular Expression Grammars](https://deepwiki.com/mlc-ai/xgrammar/4.3-regular-expression-grammars) - Pattern-based matching
 - [Structural Tags System](https://deepwiki.com/mlc-ai/xgrammar/4.4-structural-tags-system) - Dynamic grammar dispatching
 
 For the internal representation: [Grammar Representation](https://deepwiki.com/mlc-ai/xgrammar/2.1-grammar-representation)

 
## Conversion Pipeline

 All input formats follow a common conversion pattern:

 
 - **Format-Specific Processing** - Parse or convert to intermediate form
 - **Grammar Construction** - Build `Grammar::Impl` AST using `GrammarBuilder`
 - **Normalization** - Apply optimization passes
 - **Output** - Return normalized `Grammar` object
 
 Sources: [cpp/grammar.cc37-72](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L37-L72) [cpp/grammar_parser.cc427-643](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L427-L643) [cpp/grammar_builder.h24-344](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_builder.h#L24-L344)

 
## Input Formats Overview

 
### EBNF (Extended Backus-Naur Form)

 Native format for XGrammar. Parsed directly using `EBNFLexer` and `EBNFParser` into `Grammar::Impl`.

 
| Feature | Support |
|---|---|
| Quantifiers | *, +, ?, {n}, {n,m}, {n,} |
| Character classes | [a-z], [^0-9] |
| Rule references | Supported with recursion |
| Lookahead assertions | (=expr) |

 
```

```

 See [EBNF Grammar Specification](https://deepwiki.com/mlc-ai/xgrammar/4.1-ebnf-grammar-specification) for complete syntax.

 Sources: [cpp/grammar_parser.cc24-643](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L24-L643) [cpp/grammar_parser.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.h)

 
### JSON Schema

 Converts JSON Schema to EBNF via `JSONSchemaConverter`, then to `Grammar::Impl`. Uses intermediate `SchemaSpec` representation.

 
| Feature | Support |
|---|---|
| Keywords | type, properties, items, enum, anyOf, allOf, $ref, required |
| Whitespace control | Configurable via any_whitespace, indent, separators |
| Strict mode | Prevents additional properties |

 
```

```

 See [JSON Schema Conversion](https://deepwiki.com/mlc-ai/xgrammar/4.2-json-schema-conversion) for supported features.

 Sources: [cpp/json_schema_converter.cc1-1000](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1-L1000) [cpp/json_schema_converter.h26-298](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L26-L298)

 
### Regular Expressions

 Converts regex patterns to EBNF using regex parsing algorithms, then to `Grammar::Impl`.

 
```

```

 See [Regular Expression Grammars](https://deepwiki.com/mlc-ai/xgrammar/4.3-regular-expression-grammars) for supported syntax.

 Sources: [cpp/regex_converter.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/regex_converter.cc) [cpp/regex_converter.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/regex_converter.h)

 
### Structural Tags

 Defines dynamic grammar dispatching based on triggers. Parsed by `StructuralTagParser`, analyzed by `StructuralTagAnalyzer`, converted by `StructuralTagGrammarConverter`.

 
| Feature | Description |
|---|---|
| Format types | ConstStringFormat, JSONSchemaFormat, AnyTextFormat, GrammarFormat, RegexFormat, TagFormat, TriggeredTagsFormat, SequenceFormat, OrFormat |
| Composability | Formats can be nested and combined |
| TagDispatch | Uses kTagDispatch grammar expression type |

 
```

```

 See [Structural Tags System](https://deepwiki.com/mlc-ai/xgrammar/4.4-structural-tags-system) for format specification.

 Sources: [cpp/structural_tag.cc30-520](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L30-L520) [cpp/structural_tag.h1-195](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.h#L1-L195) [python/xgrammar/structural_tag.py1-320](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/structural_tag.py#L1-L320)

 
## Format Conversion Architecture

 **Diagram: Format-to-Grammar Pipeline**

 
```

```

 Sources: [cpp/grammar_parser.cc24-643](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L24-L643) [cpp/json_schema_converter.cc132-1000](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L132-L1000) [cpp/structural_tag.cc30-520](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L30-L520) [cpp/grammar_builder.h24-344](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_builder.h#L24-L344) [cpp/grammar_functor.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_functor.cc)

 **Diagram: GrammarBuilder Construction Methods**

 
```

```

 Sources: [cpp/grammar_builder.h69-220](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_builder.h#L69-L220) [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h)

 
## Python API

 
### Grammar Factory Methods

 Static methods on `xgrammar.Grammar` class:

 
| Method | Parameters | Returns |
|---|---|---|
| from_ebnf() | ebnf_string: strroot_rule_name: str = "root" | Grammar |
| from_json_schema() | schema: Union[str, Type[BaseModel], Dict]any_whitespace: bool = Trueindent: Optional[int] = Noneseparators: Optional[Tuple[str, str]] = Nonestrict_mode: bool = Truemax_whitespace_cnt: Optional[int] = Noneprint_converted_ebnf: bool = False | Grammar |
| from_regex() | regex_string: strprint_converted_ebnf: bool = False | Grammar |
| from_structural_tag() | structural_tag: Union[StructuralTag, str, Dict] | Grammar |
| builtin_json_grammar() | None | Grammar |

 Sources: [python/xgrammar/grammar.py132-284](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L132-L284)

 
### GrammarCompiler Methods

 Combines format conversion with tokenizer-specific compilation:

 
| Method | Returns |
|---|---|
| compile_grammar(ebnf_or_grammar, root_rule_name="root") | CompiledGrammar |
| compile_json_schema(schema, **kwargs) | CompiledGrammar |
| compile_regex(regex_string) | CompiledGrammar |
| compile_structural_tag(structural_tag) | CompiledGrammar |
| compile_builtin_json_grammar() | CompiledGrammar |

 Sources: [python/xgrammar/compiler.py100-249](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/compiler.py#L100-L249)

 
## C++ API

 
### Grammar Static Factory Methods

 Defined in `xgrammar::Grammar`:

 
```

```

 Sources: [include/xgrammar/grammar.h79-135](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L79-L135) [cpp/grammar.cc35-72](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L35-L72)

 
### GrammarCompiler Methods

 Defined in `xgrammar::GrammarCompiler`:

 
```

```

 Sources: [include/xgrammar/compiler.h57-112](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/compiler.h#L57-L112)

 
## Internal Representation

 
### Grammar::Impl Storage Format

 `Grammar::Impl` uses CSR (Compressed Sparse Row) format for compact storage:

 **Diagram: Grammar::Impl Structure**

 
```

```

 
### GrammarExprType Encoding

 
| Type | Data Format |
|---|---|
| kByteString | [type, len, byte₀, byte₁, ..., byteₙ] where bytes ∈ [0, 255] |
| kCharacterClass | [type, len, is_negative, lower₀, upper₀, lower₁, upper₁, ...] |
| kCharacterClassStar | Same as kCharacterClass with star quantifier |
| kEmptyStr | [type, 0] |
| kRuleRef | [type, 1, rule_id] |
| kSequence | [type, n, expr_id₀, expr_id₁, ..., expr_idₙ₋₁] |
| kChoices | [type, n, expr_id₀, expr_id₁, ..., expr_idₙ₋₁] |
| kTagDispatch | [type, len, tag_expr_id₀, rule_id₀, ..., stop_eos, stop_str_choices_id, loop_after_dispatch, exclude_str_choices_id] |

 Sources: [cpp/grammar_impl.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_impl.h) [cpp/grammar_builder.h69-220](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_builder.h#L69-L220)

 
### EBNF Parsing Flow

 **Diagram: EBNFLexer and EBNFParser Pipeline**

 
```

```

 Sources: [cpp/grammar_parser.cc24-643](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L24-L643) [cpp/grammar_builder.h24-344](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_builder.h#L24-L344)

 
## Usage Examples

 
### Python

 
```

```

 Sources: [python/xgrammar/grammar.py155-284](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L155-L284) [tests/python/test_grammar_parser.py10-30](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_parser.py#L10-L30)

 
### C++

 
```

```

 Sources: [include/xgrammar/grammar.h79-135](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L79-L135) [cpp/grammar.cc35-72](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L35-L72)

 
## Key Conversion Functions

 The following functions are the entry points for format conversion:

 
| Function | Location | Purpose |
|---|---|---|
| ParseEBNF() | cpp/grammar_parser.cc | Tokenize and parse EBNF string |
| JSONSchemaToEBNF() | cpp/json_schema_converter.cc | Convert JSON Schema to EBNF |
| RegexToEBNF() | cpp/regex_converter.cc | Convert regex pattern to EBNF |
| StructuralTagToGrammar() | cpp/structural_tag.cc | Analyze and convert structural tag |
| GrammarNormalizer::Apply() | cpp/grammar_functor.cc | Normalize and optimize grammar |

 Sources: [cpp/grammar.cc37-72](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar.cc#L37-L72) [cpp/grammar_parser.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.h) [cpp/json_schema_converter.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h) [cpp/regex_converter.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/regex_converter.h) [cpp/structural_tag.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.h)

 
## Error Handling

 Each input format has specific error handling:

 
 - **EBNF**: Parsing errors report line and column numbers via `XGRAMMAR_LOG(FATAL)`
 - **JSON Schema**: Invalid schema structure raises runtime errors
 - **Regex**: Unsupported regex features raise conversion errors
 - **Structural Tag**: Returns `std::variant<Grammar, StructuralTagError>` in C++, raises exceptions in Python
 
 Error messages include context and location information to help debug grammar specifications.

 Sources: [cpp/grammar_parser.cc99-105](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L99-L105) [cpp/grammar_parser.cc556-563](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/grammar_parser.cc#L556-L563) [python/xgrammar/grammar.py155-284](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/grammar.py#L155-L284) [include/xgrammar/grammar.h135-137](https://github.com/mlc-ai/xgrammar/blob/c30554f7/include/xgrammar/grammar.h#L135-L137)
