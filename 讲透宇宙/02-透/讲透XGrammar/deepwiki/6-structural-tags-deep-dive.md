> 来源: [https://deepwiki.com/mlc-ai/xgrammar/6-structural-tags-deep-dive](https://deepwiki.com/mlc-ai/xgrammar/6-structural-tags-deep-dive)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Structural Tags Deep Dive

  Relevant source files 
 - [cpp/structural_tag.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc)
 - [cpp/structural_tag.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.h)
 - [docs/tutorials/structural_tag.md](https://github.com/mlc-ai/xgrammar/blob/c30554f7/docs/tutorials/structural_tag.md?plain=1)
 - [python/xgrammar/structural_tag.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/python/xgrammar/structural_tag.py)
 - [tests/python/test_structural_tag_converter.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py)
 
  
## Purpose and Scope

 This document provides comprehensive technical documentation of the **Structural Tags** system in XGrammar. Structural tags enable dynamic, context-aware grammar specification through JSON-based format definitions that support triggered dispatching, nested structures, and flexible text patterns. This is particularly useful for implementing complex prompt templates, tool calling formats, and multi-modal generation patterns.

 For basic usage examples, see the Quick Start Guide ([#1.2](https://deepwiki.com/mlc-ai/xgrammar/1.2-quick-start-guide)). For detailed JSON Schema integration, see [#5](https://deepwiki.com/mlc-ai/xgrammar/5-json-schema-converter-deep-dive). For grammar compilation and matching runtime behavior, see [#2.2](https://deepwiki.com/mlc-ai/xgrammar/2.2-grammar-compilation) and [#2.3](https://deepwiki.com/mlc-ai/xgrammar/2.3-grammar-matching).

 **Sources:** [tests/python/test_structural_tag_converter.py1-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L1-L100) [cpp/structural_tag.cc1-50](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L1-L50)

 
## System Architecture

 The structural tag system consists of three major components that transform JSON format specifications into executable EBNF grammars:

 
```

```

 **Pipeline Flow:**

 
 - **Parsing:** JSON specification is parsed into typed `Format` variants using `StructuralTagParser`
 - **Analysis:** `StructuralTagAnalyzer` validates structure, detects end strings for unlimited formats, and marks format properties
 - **Conversion:** `StructuralTagGrammarConverter` visits each format recursively and builds corresponding EBNF grammar rules
 - **Normalization:** Resulting grammar is normalized using standard grammar optimization passes
 
 **Sources:** [cpp/structural_tag.cc29-62](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L29-L62) [cpp/structural_tag.cc496-548](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L496-L548) [cpp/structural_tag.cc752-779](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L752-L779)

 
## Format Type Hierarchy

 Structural tags support a rich type system with 11 distinct format types. Each format type is represented as a C++ `std::variant` and parsed from JSON:

 
```

```

 **Sources:** [cpp/structural_tag.cc98-171](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L98-L171) [cpp/structural_tag.cc507-518](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L507-L518)

 
## Format Types Reference

 
| Format Type | JSON Field | Description | Use Case |
|---|---|---|---|
| const_string | value | Fixed literal string | Static markers, delimiters |
| json_schema | json_schema | JSON Schema object | Structured data validation |
| qwen_xml_parameter | xml_schema | Qwen XML tool format | Qwen model tool calling |
| any_text | excludes (optional) | Arbitrary text, optionally excluding patterns | Free-form content regions |
| grammar | grammar | EBNF grammar string | Custom syntax rules |
| regex | pattern | Regular expression | Pattern matching |
| sequence | elements | Ordered list of formats | Multi-part structures |
| or | elements | Choice of formats | Alternatives |
| tag | begin, content, end | Tagged content block | Delimited sections |
| triggered_tags | triggers, tags, at_least_one, stop_after_first, excludes | Dynamic tag dispatch | Tool calling, context switching |
| tags_with_separator | tags, separator, at_least_one, stop_after_first | Separated tag list | Multi-item lists |

 **Sources:** [tests/python/test_structural_tag_converter.py93-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L93-L100) [tests/python/test_structural_tag_converter.py119-149](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L119-L149) [tests/python/test_structural_tag_converter.py299-338](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L299-L338)

 
## JSON Format Specification

 Structural tags are specified as JSON objects with a `type` field identifying the format type. The top-level structural tag object wraps a format:

 
```

```

 
### Example: Constant String

 
```

```

 Converts to EBNF:

 
```
const_string ::= (("Hello!"))
root ::= ((const_string))
```

 **Sources:** [tests/python/test_structural_tag_converter.py93-100](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L93-L100) [cpp/structural_tag.cc173-184](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L173-L184)

 
### Example: JSON Schema

 
```

```

 Converts to a complete JSON grammar with type constraints.

 **Sources:** [tests/python/test_structural_tag_converter.py119-149](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L119-L149) [cpp/structural_tag.cc186-199](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L186-L199)

 
### Example: Tag Format

 
```

```

 Supports multiple end strings for flexibility:

 
```

```

 **Sources:** [tests/python/test_structural_tag_converter.py422-454](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L422-L454) [cpp/structural_tag.cc319-365](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L319-L365)

 
### Example: Sequence Format

 
```

```

 Generates: `sequence ::= (const_string json_number regex_pattern)`

 **Sources:** [tests/python/test_structural_tag_converter.py299-338](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L299-L338) [cpp/structural_tag.cc261-283](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L261-L283)

 
### Example: Or Format

 
```

```

 Generates: `or ::= (const_string_a | const_string_b)`

 **Sources:** [tests/python/test_structural_tag_converter.py366-400](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L366-L400) [cpp/structural_tag.cc285-305](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L285-L305)

 
## Triggered Tags Format

 The `triggered_tags` format is the most powerful dynamic dispatching mechanism. It monitors input for trigger strings and activates corresponding tag formats:

 
```

```

 **Key Parameters:**

 
 - `triggers`: List of strings that activate tag matching. When any trigger is encountered, the system dispatches to matching tags
 - `tags`: List of `TagFormat` objects. Each tag's `begin` must start with one of the triggers
 - `at_least_one`: If `true`, requires at least one tag match before allowing completion
 - `stop_after_first`: If `true`, stops after the first tag match (no looping)
 - `excludes`: Strings that are forbidden in free-form text regions
 
 **Generated Grammar Pattern:**

 For standard case (`at_least_one=false`, `stop_after_first=false`):

 
```
triggered_tags ::= TagDispatch(
  ("<function=", triggered_tags_group),
  stop_eos=true,
  stop_str=(),
  loop_after_dispatch=true,
  excludes=()
)
triggered_tags_group ::= ("add>" schema1 "</function>") | ("multiply>" schema2 "</function>")
```

 The `TagDispatch` construct is a special grammar element that uses Aho-Corasick automaton for efficient trigger detection.

 **Sources:** [tests/python/test_structural_tag_converter.py557-658](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L557-L658) [cpp/structural_tag.cc367-445](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L367-L445) [cpp/structural_tag.cc945-1169](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L945-L1169)

 
## Tags With Separator Format

 The `tags_with_separator` format allows lists of tags with a delimiter:

 
```

```

 **Generated Pattern:**

 
```
tags_with_separator_tags ::= (tag_a | tag_b)
tags_with_separator_sub ::= ("," tags_with_separator_tags tags_with_separator_sub) | ("")
tags_with_separator ::= (tags_with_separator_tags tags_with_separator_sub)
```

 This creates a repeating pattern: `tag (separator tag)*`

 **Sources:** [tests/python/test_structural_tag_converter.py826-914](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L826-L914) [cpp/structural_tag.cc447-494](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L447-L494) [cpp/structural_tag.cc1171-1304](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L1171-L1304)

 
## Analysis Phase Details

 The `StructuralTagAnalyzer` performs critical validation and preprocessing:

 
```

```

 
### End String Detection

 The analyzer walks up the format stack to find enclosing `TagFormat` nodes and extracts their `end` strings. This is crucial for `any_text` and `triggered_tags` formats that need to know when to stop consuming input.

 Example:

 
```

```

 During analysis, when visiting `any_text`, `DetectEndStrings()` finds `"</content>"` and stores it in `detected_end_strs_`. The converter then generates:

 
```
any_text ::= TagDispatch(
  stop_eos=false,
  stop_str=("</content>"),
  loop_after_dispatch=false,
  excludes=()
)
```

 **Sources:** [cpp/structural_tag.cc551-561](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L551-L561) [cpp/structural_tag.cc637-640](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L637-L640) [cpp/structural_tag.cc700-726](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L700-L726)

 
### Unlimited Format Checking

 A format is "unlimited" if it can consume arbitrary input without a fixed bound:

 
 - `AnyTextFormat`: Always unlimited
 - `TriggeredTagsFormat`: Always unlimited (dispatches on triggers)
 - `TagsWithSeparatorFormat`: Always unlimited (repeating pattern)
 - `SequenceFormat`: Unlimited if last element is unlimited and not excluded
 - `OrFormat`: Unlimited if all elements are unlimited
 
 **Validation Rules:**

 
 - In a sequence, only the last element can be unlimited (unless it has excludes)
 - In an or, either all elements must be unlimited or all must be limited (consistent behavior)
 - If tag content is unlimited, at least one end string must be non-empty
 
 **Sources:** [cpp/structural_tag.cc563-601](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L563-L601) [cpp/structural_tag.cc650-698](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L650-L698)

 
## Conversion Phase Details

 The `StructuralTagGrammarConverter` recursively visits each format and builds grammar rules:

 
```

```

 
### TagDispatch Grammar Construct

 `TagDispatch` is a special grammar expression type (not standard EBNF) that enables efficient trigger-based dispatching using Aho-Corasick automaton:

 
```

```

 When the grammar matcher encounters `TagDispatch`:

 
 - Constructs Aho-Corasick automaton from trigger strings
 - Scans input until a trigger is matched
 - Dispatches to the corresponding rule
 - If `loop_after_dispatch=true`, continues scanning for more triggers
 - Stops when `stop_eos=true` and EOS is reached, or when `stop_str` is matched
 
 **Sources:** [cpp/structural_tag.cc856-859](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L856-L859) [cpp/structural_tag.cc1108-1115](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L1108-L1115)

 
## Triggered Tags Conversion Logic

 The conversion of `TriggeredTagsFormat` handles four cases based on flags:

 
| Case | at_least_one | stop_after_first | Generated Pattern |
|---|---|---|---|
| 1 | false | false | TagDispatch(triggers, loop=true) |
| 2 | true | false | first_tag TagDispatch(triggers, loop=true) |
| 3 | false | true | TagDispatch(triggers, loop=false) |
| 4 | true | true | Choice(tag1, tag2, ...) (simple selection) |

 **Case 4 Special Handling:**

 When both flags are true, no trigger dispatching is needed—just pick one tag:

 
```
triggered_tags ::= (tag1_full | tag2_full | tag3_full)
```

 Each tag is fully expanded with `begin`, `content`, and `end`.

 **Case 2 Pattern:**

 With `at_least_one=true`, generate the first tag explicitly:

 
```
triggered_tags_first ::= (tag1_full | tag2_full)
triggered_tags_sub ::= TagDispatch(...)
triggered_tags ::= (triggered_tags_first triggered_tags_sub)
```

 This ensures at least one tag appears before allowing completion.

 **Sources:** [cpp/structural_tag.cc981-1048](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L981-L1048) [cpp/structural_tag.cc1050-1169](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L1050-L1169)

 
## Tags With Separator Conversion Logic

 The `tags_with_separator` conversion also handles multiple cases:

 
### Normal Case (stop_after_first=false)

 Generate a recursive rule with separator:

 
```
tags_with_separator_tags ::= (tag1 | tag2 | ...)
tags_with_separator_sub ::= ("," tags_with_separator_tags tags_with_separator_sub) | end_str
tags_with_separator ::= (tags_with_separator_tags tags_with_separator_sub) [| end_str if !at_least_one]
```

 
### Special Case (stop_after_first=true)

 No recursion needed:

 
```
tags_with_separator ::= (tags_with_separator_tags end_str) [| end_str if !at_least_one]
```

 
### Empty Separator Handling

 When `separator=""`, the conversion still works correctly by omitting the separator in the sequence:

 
```
tags_with_separator_sub ::= (tags_with_separator_tags tags_with_separator_sub) | end_str
```

 **Sources:** [cpp/structural_tag.cc1171-1304](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L1171-L1304) [tests/python/test_structural_tag_converter.py1020-1115](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L1020-L1115)

 
## Python API Integration

 The Python API provides a high-level interface through `StructuralTagItem`:

 
```

```

 The `schema` parameter accepts:

 
 - Pydantic `BaseModel` class (converted to JSON Schema)
 - Python `dict` representing JSON Schema
 - JSON string representing JSON Schema
 
 **Sources:** [tests/python/test_grammar_matcher_structural_tag.py21-39](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_structural_tag.py#L21-L39) [tests/python/test_grammar_matcher_structural_tag.py165-194](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_structural_tag.py#L165-L194)

 
## Real-World Examples

 
### Tool Calling (Llama Style)

 
```

```

 Accepts: `<text>{"name": "func1", "parameters": {"arg": 10}}<text>...`

 **Sources:** [tests/python/test_structural_tag_converter.py1117-1143](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L1117-L1143)

 
### Forced Thinking + Tool Calling

 
```

```

 Forces pattern: `<function=...>...</function>`

 **Sources:** [tests/python/test_structural_tag_converter.py1185-1221](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L1185-L1221)

 
### DeepSeek Tool Calling Format

 Complex nested structure with multiple separators:

 
```

```

 **Sources:** [tests/python/test_structural_tag_converter.py1223-1297](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L1223-L1297)

 
## Performance Considerations

 
### Trigger Matching Efficiency

 The `TagDispatch` mechanism uses Aho-Corasick automaton for O(n) trigger detection where n is input length, regardless of the number of triggers. This is critical for real-time LLM generation.

 
### Grammar Optimization

 After conversion, the resulting grammar undergoes standard optimization passes:

 
 - Structure normalization
 - Byte string fusion
 - Rule inlining
 - Dead code elimination
 
 The optimized grammar is significantly smaller and faster to match.

 Example from tests shows before/after optimization:

 **Before:** 162 lines with duplicated rules for `basic_any`, `basic_string_sub`, etc.

 **After:** 81 lines with shared rules and lookahead annotations (`(=(...))`)

 **Sources:** [tests/python/test_grammar_matcher_structural_tag.py41-81](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_structural_tag.py#L41-L81) [tests/python/test_grammar_matcher_structural_tag.py83-162](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_grammar_matcher_structural_tag.py#L83-L162) [cpp/structural_tag.cc1323](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L1323-L1323)

 
## Error Handling

 The system uses `Result<T, E>` types for error propagation:

 
```

```

 **Common Errors:**

 
| Error Type | Cause | Example |
|---|---|---|
| InvalidJSONError | Malformed JSON | Missing quotes, trailing commas |
| ISTError (parsing) | Missing required fields | const_string without value |
| ISTError (analysis) | Unlimited format in middle of sequence | [any_text, const_string] |
| ISTError (analysis) | Mixed unlimited/limited in or | or([any_text, const_string]) |
| ISTError (conversion) | Tag doesn't match any trigger | Tag begin not a prefix of any trigger |

 **Sources:** [cpp/structural_tag.cc64-73](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L64-L73) [cpp/structural_tag.cc658-663](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L658-L663) [cpp/structural_tag.cc689-694](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/structural_tag.cc#L689-L694)

 
## Testing Strategy

 The test suite covers:

 
 - **Format Parsing:** Each format type with valid/invalid inputs
 - **Grammar Generation:** Expected EBNF output for each format
 - **Instance Acceptance:** Sample strings that should/shouldn't match
 - **Edge Cases:** Empty strings, UTF-8, nested structures, multiple end strings
 - **Performance:** Compilation time, matching time profiling
 
 Test pattern:

 
```

```

 **Sources:** [tests/python/test_structural_tag_converter.py70-91](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L70-L91) [tests/python/test_structural_tag_converter.py110-117](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_structural_tag_converter.py#L110-L117)
