> 来源: [https://deepwiki.com/mlc-ai/xgrammar/5-json-schema-converter-deep-dive](https://deepwiki.com/mlc-ai/xgrammar/5-json-schema-converter-deep-dive)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# JSON Schema Converter Deep Dive

  Relevant source files 
 - [cpp/json_schema_converter.cc](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc)
 - [cpp/json_schema_converter.h](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h)
 - [tests/python/test_json_schema_converter.py](https://github.com/mlc-ai/xgrammar/blob/c30554f7/tests/python/test_json_schema_converter.py)
 
  This document provides a detailed explanation of the JSON Schema to EBNF conversion system in xgrammar. It covers the architecture, intermediate representations, parsing logic, and grammar generation algorithms that transform JSON Schema specifications into executable EBNF grammars for constrained LLM generation.

 For information about the Python API for JSON schema grammars, see [Grammar Definition and Construction](https://deepwiki.com/mlc-ai/xgrammar/3.1-grammar-definition-and-construction). For details on structural tags which provide an alternative schema system, see [Structural Tags Deep Dive](https://deepwiki.com/mlc-ai/xgrammar/6-structural-tags-deep-dive).

 
## Purpose and Scope

 The JSON Schema Converter system transforms JSON Schema documents (Draft 2020-12 compatible) into EBNF grammar rules that can be compiled and executed by xgrammar's runtime matching engine. This enables grammar-guided generation that enforces complex structural and type constraints defined in JSON Schema.

 The system consists of three main phases:

 
 - **Parsing**: JSON Schema → SchemaSpec Intermediate Representation
 - **Conversion**: SchemaSpec IR → EBNF Grammar Rules
 - **Optimization**: Rule deduplication and caching
 
 This page provides an architectural overview. Detailed subsystems are covered in:

 
 - [Converter Architecture](https://deepwiki.com/mlc-ai/xgrammar/5.1-converter-architecture) - SchemaSpec IR, SchemaParser, JSONSchemaConverter
 - [Supported JSON Schema Features](https://deepwiki.com/mlc-ai/xgrammar/5.2-supported-json-schema-features) - Keywords, types, and validation features
 - [Object and Array Schema Processing](https://deepwiki.com/mlc-ai/xgrammar/5.3-object-and-array-schema-processing) - Property and item handling with constraints
 - [Formatting and Whitespace Control](https://deepwiki.com/mlc-ai/xgrammar/5.4-formatting-and-whitespace-control) - IndentManager and formatting options
 - [String Formats and Numeric Ranges](https://deepwiki.com/mlc-ai/xgrammar/5.5-string-formats-and-numeric-ranges) - Format validation and range regex generation
 
 
## Conversion Pipeline Overview

 The conversion process transforms JSON Schema through multiple stages to produce optimized EBNF grammar:

 
```

```

 **Sources**: [cpp/json_schema_converter.cc134-950](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L134-L950) [cpp/json_schema_converter.h253-429](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L253-L429)

 
## Core Architecture

 
### Main Components

 
```

```

 **Sources**: [cpp/json_schema_converter.h25-213](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L25-L213) [cpp/json_schema_converter.cc134-196](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L134-L196)

 
### Class Responsibilities

 
| Class | Location | Responsibility |
|---|---|---|
| SchemaParser | cpp/json_schema_converter.cc146-196 | Parse JSON Schema (picojson::value) into SchemaSpec IR. Handles all JSON Schema keywords, type inference, and $ref resolution. |
| SchemaSpec | cpp/json_schema_converter.h165-181 | Intermediate representation holding a variant of spec types plus cache key and rule name hint. |
| IntegerSpec, NumberSpec, etc. | cpp/json_schema_converter.h33-163 | Typed specification structs holding constraints for each JSON Schema type. |
| JSONSchemaConverter | cpp/json_schema_converter.h253-429 | Base converter class that generates EBNF from SchemaSpec. Virtual methods allow subclass customization for XML formats. |
| IndentManager | cpp/json_schema_converter.h218-245 | Manages indentation and separator formatting. Tracks nesting level and generates appropriate whitespace patterns. |
| GenerateCacheManager | cpp/json_schema_converter.h195-213 | Caches generated rules by (cache_key, is_inner_layer) to avoid duplicate rule generation. |
| EBNFScriptCreator | cpp/json_schema_converter.h367 | Utility for building EBNF grammar strings with rule allocation and helper methods. |

 **Sources**: [cpp/json_schema_converter.h25-429](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L25-L429)

 
## Parsing: JSON Schema to SchemaSpec IR

 The `SchemaParser` class converts raw JSON Schema into a typed intermediate representation:

 
```

```

 **Sources**: [cpp/json_schema_converter.cc259-948](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L259-L948)

 
### Parse Method Dispatch

 The `SchemaParser::Parse()` method dispatches to specialized parse methods based on schema keywords:

 
| Schema Keyword | Parse Method | Spec Type | Lines |
|---|---|---|---|
| type: "integer" | ParseInteger() | IntegerSpec | cpp/json_schema_converter.cc378-461 |
| type: "number" | ParseNumber() | NumberSpec | cpp/json_schema_converter.cc463-509 |
| type: "string" | ParseString() | StringSpec | cpp/json_schema_converter.cc511-539 |
| type: "boolean" | ParseBoolean() | BooleanSpec | cpp/json_schema_converter.cc541-543 |
| type: "null" | ParseNull() | NullSpec | cpp/json_schema_converter.cc545-547 |
| type: "array" | ParseArray() | ArraySpec | cpp/json_schema_converter.cc549-669 |
| type: "object" | ParseObject() | ObjectSpec | cpp/json_schema_converter.cc671-812 |
| const | ParseConst() | ConstSpec | cpp/json_schema_converter.cc814-818 |
| enum | ParseEnum() | EnumSpec | cpp/json_schema_converter.cc820-829 |
| $ref | ParseRef() / ResolveRef() | RefSpec | cpp/json_schema_converter.cc831-887 |
| anyOf / oneOf | ParseAnyOf() | AnyOfSpec | cpp/json_schema_converter.cc889-905 |
| allOf | ParseAllOf() | AllOfSpec | cpp/json_schema_converter.cc907-920 |

 **Sources**: [cpp/json_schema_converter.cc259-948](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L259-L948)

 
### Cache Key Generation

 Each `SchemaSpec` has a `cache_key` computed by `SchemaParser::ComputeCacheKey()` that deterministically serializes the schema (excluding metadata fields like `title`, `description`). This enables rule deduplication:

 
```

```

 **Sources**: [cpp/json_schema_converter.cc198-244](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L198-L244) [cpp/json_schema_converter.cc264-267](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L264-L267)

 
## Generation: SchemaSpec to EBNF

 The `JSONSchemaConverter` traverses the SchemaSpec IR tree and generates EBNF rules using a visitor pattern:

 
```

```

 **Sources**: [cpp/json_schema_converter.cc1123-1323](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1123-L1323)

 
### Generate Method Details

 Each `Generate*()` method constructs EBNF patterns appropriate for the spec type:

 **Integer Generation** ([cpp/json_schema_converter.cc1327-1349](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1327-L1349)):

 
 - If range constraints exist: generates range regex using `GenerateRangeRegex()`
 - Otherwise: generates pattern `(\"0\" | \"-\"? [1-9] [0-9]*)`
 
 **Array Generation** ([cpp/json_schema_converter.cc1425-1525](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1425-L1525)):

 
 - Handles `prefixItems` (fixed position items)
 - Handles `items` / `unevaluatedItems` (additional items)
 - Applies `minItems` / `maxItems` constraints via repetition operators
 
 **Object Generation** ([cpp/json_schema_converter.cc1527-1765](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1527-L1765)):

 
 - Processes `properties` in order
 - Handles `required` properties (must appear)
 - Handles `additionalProperties` / `unevaluatedProperties`
 - Applies `minProperties` / `maxProperties` constraints
 - Supports `patternProperties` and `propertyNames`
 
 **Sources**: [cpp/json_schema_converter.cc1327-1765](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1327-L1765)

 
## Formatting and Indentation

 The `IndentManager` class controls whitespace generation based on configuration:

 
```

```

 **Sources**: [cpp/json_schema_converter.h218-245](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L218-L245) [cpp/json_schema_converter.cc952-1075](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L952-L1075)

 
### Formatting Modes

 
| Mode | indent | any_whitespace | Output Example |
|---|---|---|---|
| Compact | nullopt | false | {"key": "value"} |
| Compact with spaces | nullopt | false | {"key": "value"} (separators control spacing) |
| Indented | 2 | false | {\n  "key": "value"\n} |
| Any whitespace | N/A | true | {[ \n\t]*"key"[ \n\t]*:[ \n\t]*"value"[ \n\t]*} |

 **Sources**: [cpp/json_schema_converter.cc1091-1121](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1091-L1121)

 
## Caching and Optimization

 
### Two-Level Caching Strategy

 
```

```

 **Parsing Level Cache** (`schema_cache_` in SchemaParser):

 
 - Key: Computed from normalized JSON schema
 - Value: Shared `SchemaSpecPtr`
 - Purpose: Avoid duplicate parsing of identical schemas
 
 **Generation Level Cache** (`rule_cache_manager_` in JSONSchemaConverter):

 
 - Key: `cache_key` from SchemaSpec + `is_inner_layer` flag
 - Value: Generated EBNF rule name
 - Purpose: Reuse generated rules across multiple references
 
 **Sources**: [cpp/json_schema_converter.cc198-244](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L198-L244) [cpp/json_schema_converter.cc264-267](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L264-L267) [cpp/json_schema_converter.h195-213](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L195-L213) [cpp/json_schema_converter.cc1251-1263](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1251-L1263)

 
## Reference Resolution

 The system handles JSON Schema `$ref` keywords with support for circular references:

 
```

```

 **URI Formats Supported**:

 
 - `#` - Root schema reference
 - `#/$defs/schemaName` - Definition reference
 - `#/path/to/nested/schema` - JSON Pointer path
 
 **Circular Reference Handling**:

 
 - When encountering a `$ref`, create a placeholder entry in `ref_cache_`
 - Parse the target schema
 - Update `ref_cache_` with the resolved spec
 - Subsequent references to the same URI return the cached spec
 
 **Sources**: [cpp/json_schema_converter.cc831-887](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L831-L887) [cpp/json_schema_converter.cc194](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L194-L194)

 
## Basic Rule Generation

 The converter creates a set of basic rules that all generated schemas can reference:

 
```

```

 These rules are cached with standardized cache keys (e.g., `{\"type\":\"integer\"}` for `basic_integer`) to enable reuse when user schemas match basic types exactly.

 **Sources**: [cpp/json_schema_converter.cc1148-1221](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1148-L1221) [cpp/json_schema_converter.cc1223-1234](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L1223-L1234)

 
## Extensibility: Virtual Methods

 The `JSONSchemaConverter` class uses virtual methods to support format customization (e.g., for XML-style function calling):

 
```

```

 Subclasses can override:

 
 - `GenerateInteger()`, `GenerateObject()`, etc. - Change type generation
 - `FormatPropertyKey()`, `FormatProperty()` - Customize property formatting (e.g., XML tags instead of JSON keys)
 - `GetKeyPattern()` - Use different key patterns
 - `AddBasicRules()` - Define different basic rule sets
 
 **Sources**: [cpp/json_schema_converter.h275-331](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L275-L331) [cpp/json_schema_converter_ext.cc1-400](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter_ext.cc#L1-L400)

 
## Public API Functions

 
| Function | Location | Purpose |
|---|---|---|
| JSONSchemaToEBNF(string) | cpp/json_schema_converter.cc3528-3570 | Main entry point: parse JSON string and convert to EBNF |
| JSONSchemaToEBNF(picojson::value) | cpp/json_schema_converter.cc3572-3611 | Convert pre-parsed JSON schema object |
| QwenXMLToolCallingToEBNF() | cpp/json_schema_converter_ext.cc | Generate Qwen-style XML function calling grammar |
| MiniMaxXMLToolCallingToEBNF() | cpp/json_schema_converter_ext.cc | Generate MiniMax-style XML function calling grammar |
| DeepSeekXMLToolCallingToEBNF() | cpp/json_schema_converter_ext.cc | Generate DeepSeek-style XML function calling grammar |

 **Sources**: [cpp/json_schema_converter.h431-537](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.h#L431-L537) [cpp/json_schema_converter.cc3528-3690](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L3528-L3690)

 
## Error Handling

 The parser uses a typed error system for schema validation:

 
```

```

 **Error Types**:

 
 - `kInvalidSchema` - Schema is not well-formed (e.g., wrong type for keyword)
 - `kUnsatisfiableSchema` - Schema has contradictory constraints (e.g., `minItems: 5, maxItems: 3`)
 
 **Sources**: [cpp/json_schema_converter.cc136-142](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L136-L142) [cpp/json_schema_converter.cc270-284](https://github.com/mlc-ai/xgrammar/blob/c30554f7/cpp/json_schema_converter.cc#L270-L284)
