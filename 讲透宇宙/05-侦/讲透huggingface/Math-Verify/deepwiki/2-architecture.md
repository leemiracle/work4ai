<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Math-Verify · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/flow.svg](assets/flow.svg)
- [src/math_verify/errors.py](src/math_verify/errors.py)

</details>



This document describes the detailed system architecture of Math-Verify, including data flow patterns, component relationships, and the core processing pipeline. It covers how mathematical expressions are extracted, normalized, converted, and compared across different representation formats.

For practical usage instructions, see [Usage Guide](#4). For specific component implementations, see [Core Components](#3).

## System Overview

Math-Verify implements a three-stage pipeline architecture designed for robust mathematical expression evaluation:

```mermaid
graph TB
    subgraph "Input Processing"
        input["Raw Model Output"]
        config["ExtractionConfig<br/>LatexExtractionConfig<br/>ExprExtractionConfig<br/>StringExtractionConfig"]
    end
    
    subgraph "Stage 1: Extraction"
        parser["parse()"]
        regex["Regex Pattern Matching"]
        extract["Expression Extraction"]
    end
    
    subgraph "Stage 2: Normalization & Conversion" 
        norm["LaTeX Normalization"]
        convert["latex2sympy2_extended"]
        sympy["SymPy Expression"]
    end
    
    subgraph "Stage 3: Verification"
        grader["verify()"]
        compare["Multi-Strategy Comparison"]
        result["Boolean Result"]
    end
    
    input --> config
    config --> parser
    parser --> regex
    regex --> extract
    extract --> norm
    norm --> convert  
    convert --> sympy
    sympy --> grader
    grader --> compare
    compare --> result
```

**Sources:** [README.md:107-175](), [src/math_verify/parser.py](), [src/math_verify/grader.py]()

## Core Processing Pipeline

The architecture follows a strict sequential processing model where each stage handles specific aspects of mathematical expression processing:

### Stage 1: Expression Extraction

```mermaid
graph TD
    subgraph "ExtractionConfig System"
        LatexConfig["LatexExtractionConfig"]
        ExprConfig["ExprExtractionConfig"] 
        StringConfig["StringExtractionConfig"]
    end
    
    subgraph "Priority-Based Extraction"
        patterns["Regex Pattern Generation"]
        priority["Priority Assignment"]
        matching["Pattern Matching Engine"]
        selection["Last-Match-First Selection"]
    end
    
    subgraph "Timeout Protection"
        timeout["TimeoutException"]
        wrapper["Timeout Wrapper"]
    end
    
    LatexConfig --> patterns
    ExprConfig --> patterns
    StringConfig --> patterns
    patterns --> priority
    priority --> matching
    matching --> selection
    wrapper --> timeout
    matching --> wrapper
```

**Sources:** [src/math_verify/parser.py](), [src/math_verify/errors.py:1-3](), [README.md:115-121]()

### Stage 2: Normalization and Conversion

The normalization pipeline handles LaTeX preprocessing before SymPy conversion:

```mermaid
graph TD
    subgraph "LaTeX Normalization Pipeline"
        input["Raw LaTeX Expression"]
        basic["Basic Command Removal<br/>\\mathrm, \\displaystyle"]
        units["Unit Removal"]
        malformed["Malformed Operator Fixes<br/>\\sqrt(2) → \\sqrt{2}<br/>\\frac13 → \\frac{1}{3}"]
        boxed["Boxed Environment Extraction"]
        equations["Multi-step Equation Shortening<br/>a+b=b+a=1 → b+a=1"]
    end
    
    subgraph "SymPy Conversion"
        antlr["ANTLR4 Parser"]
        sympy_expr["SymPy Expression Object"]
        special["Special Case Handling<br/>Percentages, Matrices<br/>Complex Numbers, Sets"]
    end
    
    input --> basic
    basic --> units
    units --> malformed
    malformed --> boxed
    boxed --> equations
    equations --> antlr
    antlr --> sympy_expr
    sympy_expr --> special
```

**Sources:** [README.md:122-138](), [latex2sympy2_extended/latex2sympy2.py]()

### Stage 3: Verification Engine

```mermaid
graph TD
    subgraph "Comparison Strategies"
        string_comp["String Comparison<br/>strip() normalization"]
        structural["Structural SymPy Equality"]
        numeric["Numeric Comparison<br/>precision-aware"]
        symbolic["Symbolic Comparison<br/>(a-b).simplify() == 0"]
    end
    
    subgraph "Type-Specific Handlers"
        relational["Relational Expressions<br/>Equation/Inequality handling<br/>Flip support (a<b == b>a)"]
        sets["Set and Interval Comparison<br/>Symmetric difference<br/>Element-wise validation"]
        matrices["Matrix Comparison<br/>Element-wise equality<br/>Shape validation"]
        complex_nums["Complex Number Support<br/>Re, Im, arg functions"]
    end
    
    subgraph "Result Processing"
        timeout_check["Timeout Protection"]
        fallback["Graceful Fallback"]
        final_result["Boolean Result"]
    end
    
    string_comp --> relational
    structural --> relational
    numeric --> sets
    symbolic --> matrices
    relational --> timeout_check
    sets --> timeout_check
    matrices --> timeout_check
    complex_nums --> timeout_check
    timeout_check --> fallback
    fallback --> final_result
```

**Sources:** [src/math_verify/grader.py](), [README.md:139-175]()

## Component Interaction Model

The system uses a modular architecture where components interact through well-defined interfaces:

```mermaid
graph TB
    subgraph "Core API Layer"
        parse_func["parse(text, extraction_config)"]
        verify_func["verify(gold, prediction)"]
        math_metric["math_metric(gold_list, pred_list)"]
    end
    
    subgraph "Configuration Layer"
        latex_config["LatexExtractionConfig<br/>- boxed: str<br/>- units: bool<br/>- malformed_operators: bool"]
        expr_config["ExprExtractionConfig<br/>- percentage: bool<br/>- simple_number: bool"]
        string_config["StringExtractionConfig<br/>- strict_match: bool"]
    end
    
    subgraph "Processing Engines"
        extraction_engine["ExtractionEngine"]
        normalization_engine["NormalizationEngine"] 
        comparison_engine["ComparisonEngine"]
    end
    
    subgraph "External Dependencies"
        latex2sympy["latex2sympy2_extended"]
        sympy_lib["SymPy"]
        antlr["ANTLR4 Runtime"]
    end
    
    parse_func --> latex_config
    parse_func --> expr_config
    parse_func --> string_config
    
    latex_config --> extraction_engine
    expr_config --> extraction_engine
    string_config --> extraction_engine
    
    extraction_engine --> normalization_engine
    normalization_engine --> latex2sympy
    latex2sympy --> antlr
    latex2sympy --> sympy_lib
    
    verify_func --> comparison_engine
    comparison_engine --> sympy_lib
    
    math_metric --> parse_func
    math_metric --> verify_func
```

**Sources:** [src/math_verify/__init__.py](), [src/math_verify/math_metric.py](), [pyproject.toml]()

## Configuration Architecture

The system uses a flexible configuration architecture that allows fine-grained control over extraction and comparison behavior:

| Configuration Class | Purpose | Key Parameters |
|---------------------|---------|----------------|
| `LatexExtractionConfig` | LaTeX expression extraction | `boxed`, `units`, `malformed_operators`, `basic_latex` |
| `ExprExtractionConfig` | Plain expression extraction | `percentage`, `simple_number`, `timeout` |
| `StringExtractionConfig` | String literal extraction | `strict_match`, `case_sensitive` |
| `NormalizationConfig` | LaTeX preprocessing | `operator_fixes`, `unit_removal`, `equation_splitting` |

```mermaid
graph TD
    subgraph "Configuration Hierarchy"
        base_config["BaseExtractionConfig"]
        latex_specific["LatexExtractionConfig"]
        expr_specific["ExprExtractionConfig"]
        string_specific["StringExtractionConfig"]
    end
    
    subgraph "Runtime Configuration"
        priority_assignment["Priority Assignment<br/>0 = highest priority"]
        regex_generation["Regex Pattern Generation"]
        timeout_settings["Timeout Configuration<br/>Per-operation timeouts"]
    end
    
    subgraph "Behavioral Modifiers"
        strict_mode["Strict Mode<br/>Variable matching enforcement"]
        fallback_mode["Fallback Strategies<br/>no_fallback, first_match"]
        precision_control["Numeric Precision<br/>Configurable rounding"]
    end
    
    base_config --> latex_specific
    base_config --> expr_specific
    base_config --> string_specific
    
    latex_specific --> priority_assignment
    expr_specific --> priority_assignment
    string_specific --> priority_assignment
    
    priority_assignment --> regex_generation
    regex_generation --> timeout_settings
    
    timeout_settings --> strict_mode
    strict_mode --> fallback_mode
    fallback_mode --> precision_control
```

**Sources:** [README.md:195-210](), [src/math_verify/parser.py](), [tests/test_configs.py]()

## Error Handling and Robustness

Math-Verify implements comprehensive error handling to ensure reliable operation across different platforms and input conditions:

```mermaid
graph TD
    subgraph "Timeout System"
        posix_signals["POSIX Signal Handler<br/>Unix/Linux/MacOS"]
        windows_mp["Windows Multiprocessing<br/>Process termination"]
        timeout_exception["TimeoutException"]
    end
    
    subgraph "Graceful Degradation"
        parsing_fallback["Parsing Fallback<br/>String comparison on SymPy failure"]
        comparison_fallback["Comparison Fallback<br/>Multiple strategy attempts"]
        logging_system["Logging System<br/>Debug/Error levels"]
    end
    
    subgraph "Input Validation"
        malformed_latex["Malformed LaTeX Handling"]
        unicode_support["Unicode Symbol Substitution<br/>β → beta"]
        encoding_safety["Encoding Safety Checks"]
    end
    
    posix_signals --> timeout_exception
    windows_mp --> timeout_exception
    timeout_exception --> parsing_fallback
    
    parsing_fallback --> comparison_fallback
    comparison_fallback --> logging_system
    
    malformed_latex --> unicode_support
    unicode_support --> encoding_safety
    encoding_safety --> parsing_fallback
```

**Sources:** [src/math_verify/errors.py](), [src/math_verify/timeout.py](), [README.md:171-175]()

## External Dependency Integration

The system integrates with several external libraries through well-defined interfaces:

```mermaid
graph TB
    subgraph "Math-Verify Core"
        core_api["Core API Functions"]
        internal_logic["Internal Processing Logic"]
    end
    
    subgraph "LaTeX Processing Stack"
        latex2sympy_ext["latex2sympy2_extended==1.10.2<br/>Primary LaTeX parser"]
        antlr_runtime["ANTLR4 Runtime<br/>Versions: 4.9.3, 4.11.0, 4.13.2"]
        grammar_files["ANTLR Grammar Files<br/>LaTeX parsing rules"]
    end
    
    subgraph "Symbolic Mathematics"
        sympy_core["SymPy Core<br/>Expression manipulation"]
        sympy_solvers["SymPy Solvers<br/>Equation solving"]
        sympy_sets["SymPy Sets<br/>Set operations"]
    end
    
    subgraph "Evaluation Framework"
        lighteval["lighteval[math]<br/>Model evaluation pipeline"]
        huggingface["HuggingFace Integration<br/>Model loading and inference"]
    end
    
    core_api --> latex2sympy_ext
    latex2sympy_ext --> antlr_runtime
    antlr_runtime --> grammar_files
    
    core_api --> sympy_core
    sympy_core --> sympy_solvers
    sympy_core --> sympy_sets
    
    internal_logic --> lighteval
    lighteval --> huggingface
```

**Sources:** [pyproject.toml](), [README.md:10-21](), [requirements.txt]()

---

