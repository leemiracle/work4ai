<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Math-Verify · page 3 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/math_verify/__init__.py](src/math_verify/__init__.py)
- [tests/test_string_extraction.py](tests/test_string_extraction.py)

</details>



This page provides an overview of the main functional components that comprise the Math-Verify system. It covers the core modules responsible for mathematical expression parsing, verification, and evaluation, along with their configuration systems and utilities.

For detailed implementation specifics of individual components, see the Parser Module ([3.1](#3.1)), Grader Module ([3.2](#3.2)), and Metrics and Evaluation ([3.3](#3.3)). For usage examples and configuration options, see the Usage Guide ([4](#4)).

## Component Architecture Overview

The Math-Verify system is built around four primary components that work together to extract, parse, and verify mathematical expressions:

```mermaid
graph TB
    subgraph "Core API Layer"
        ParseAPI["parse()"]
        VerifyAPI["verify()"]
        MetricAPI["math_metric()"]
    end
    
    subgraph "Parser Module"
        ExtractionConfigs["ExtractionConfig Classes"]
        RegexEngine["Regex Pattern Engine"]
        TimeoutSystem["Timeout Protection"]
    end
    
    subgraph "Verification Engine"
        Grader["grader.py"]
        Comparators["Expression Comparators"]
        Fallbacks["Fallback Strategies"]
    end
    
    subgraph "Configuration System"
        LatexConfig["LatexExtractionConfig"]
        ExprConfig["ExprExtractionConfig"] 
        StringConfig["StringExtractionConfig"]
        NormConfig["LatexNormalizationConfig"]
    end
    
    subgraph "External Dependencies"
        Latex2Sympy["latex2sympy2_extended"]
        SymPy["SymPy Engine"]
        ANTLR["ANTLR4 Runtime"]
    end
    
    ParseAPI --> ExtractionConfigs
    ParseAPI --> RegexEngine
    ParseAPI --> TimeoutSystem
    
    VerifyAPI --> Grader
    VerifyAPI --> Comparators
    VerifyAPI --> Fallbacks
    
    MetricAPI --> ParseAPI
    MetricAPI --> VerifyAPI
    
    ExtractionConfigs --> LatexConfig
    ExtractionConfigs --> ExprConfig
    ExtractionConfigs --> StringConfig
    
    RegexEngine --> Latex2Sympy
    Grader --> SymPy
    Latex2Sympy --> ANTLR
    NormConfig --> Latex2Sympy
```

Sources: [src/math_verify/__init__.py:1-23](), [README.md:115-175]()

## Main API Components

The system exposes four primary functions through its public API, each serving a distinct role in the mathematical verification pipeline:

| Function | Purpose | Primary Use Case |
|----------|---------|------------------|
| `parse()` | Extract mathematical expressions from text | Convert model outputs to structured format |
| `verify()` | Compare two parsed expressions for equivalence | Validate model answers against gold standards |
| `math_metric()` | Calculate evaluation metrics over datasets | Batch evaluation and scoring |
| Configuration Classes | Control extraction and normalization behavior | Customize parsing for specific formats |

### Core Function Signatures

The main API functions operate with the following key interfaces:

```mermaid
graph LR
    Input["Raw Text Input"]
    Configs["Extraction Configs"]
    ParseResult["Parsed Expression List"]
    Gold["Gold Standard"]
    Answer["Model Answer"] 
    VerifyResult["Boolean Result"]
    
    Input --> ParseFunc["parse(text, extraction_config)"]
    Configs --> ParseFunc
    ParseFunc --> ParseResult
    
    Gold --> VerifyFunc["verify(gold, answer, **kwargs)"]
    Answer --> VerifyFunc
    VerifyFunc --> VerifyResult
    
    ParseResult --> Gold
    ParseResult --> Answer
```

Sources: [src/math_verify/__init__.py:5-12](), [README.md:24-36]()

## Parser Module Components

The parser module implements a multi-strategy extraction system with configurable extraction targets:

```mermaid
graph TD
    subgraph "Extraction Strategies"
        LatexStrategy["LatexExtractionConfig"]
        ExprStrategy["ExprExtractionConfig"]
        StringStrategy["StringExtractionConfig"]
    end
    
    subgraph "Pattern Matching Engine"
        PrioritySystem["Priority-based Regex"]
        RegexPatterns["Compiled Patterns"]
        MatchProcessor["Match Processing"]
    end
    
    subgraph "Normalization Pipeline"
        BasicLatex["Basic LaTeX Commands"]
        UnitHandling["Unit Removal"]
        OperatorFixes["Malformed Operator Fixes"]
        BoxedHandling["\\boxed{} Processing"]
    end
    
    LatexStrategy --> PrioritySystem
    ExprStrategy --> PrioritySystem  
    StringStrategy --> PrioritySystem
    
    PrioritySystem --> RegexPatterns
    RegexPatterns --> MatchProcessor
    MatchProcessor --> BasicLatex
    BasicLatex --> UnitHandling
    UnitHandling --> OperatorFixes
    OperatorFixes --> BoxedHandling
```

### Extraction Configuration Classes

Each extraction strategy is implemented as a configuration class that defines pattern matching behavior:

| Configuration Class | Target Format | Example Input | Use Case |
|-------------------|---------------|---------------|----------|
| `LatexExtractionConfig` | LaTeX expressions in environments | `$\sqrt{2}$`, `\[\frac{1}{2}\]` | Mathematical notation parsing |
| `ExprExtractionConfig` | Plain numerical expressions | `1/2`, `3.14159` | Simple arithmetic extraction |
| `StringExtractionConfig` | Literal string matching | `A`, `B`, `C`, `D` | Multiple choice answers |

Sources: [src/math_verify/__init__.py:8-11](), [README.md:38-45](), [tests/test_string_extraction.py:1-28]()

## Verification Engine Components

The verification engine implements multiple comparison strategies with fallback mechanisms:

```mermaid
graph TD
    subgraph "Primary Comparison Methods"
        StringComp["String Comparison"]
        NumericComp["Numeric Comparison"]  
        SymbolicComp["Symbolic Comparison"]
    end
    
    subgraph "Specialized Comparators"
        SetComp["Set Comparator"]
        RelationComp["Relation Comparator"]
        MatrixComp["Matrix Comparator"]
        ComplexComp["Complex Number Comparator"]
    end
    
    subgraph "Comparison Pipeline"
        InitialCheck["Basic Equality Check"]
        TypeDetection["Expression Type Detection"]
        SpecializedVerify["Specialized Verification"]
        FallbackLogic["Fallback Strategies"]
    end
    
    InitialCheck --> StringComp
    InitialCheck --> NumericComp
    
    TypeDetection --> SetComp
    TypeDetection --> RelationComp
    TypeDetection --> MatrixComp
    TypeDetection --> ComplexComp
    
    StringComp --> SpecializedVerify
    NumericComp --> SymbolicComp
    SymbolicComp --> SpecializedVerify
    SpecializedVerify --> FallbackLogic
```

### Verification Strategies

The `verify()` function employs multiple comparison approaches based on expression types:

| Strategy | Expression Types | Comparison Method | Example |
|----------|-----------------|-------------------|---------|
| String Comparison | All types | Direct string matching after normalization | `"1/2" == "0.5"` |
| Numeric Comparison | Numbers, fractions | Floating point with configurable precision | `0.333... ≈ 1/3` |
| Symbolic Comparison | Algebraic expressions | SymPy symbolic equality | `x + 1 == 1 + x` |
| Set Comparison | Sets, intervals | Element-wise and structural comparison | `{1,2,3} == {3,2,1}` |
| Relation Comparison | Equations, inequalities | Normalized form comparison with flipping | `a < b == b > a` |

Sources: [README.md:139-175](), [src/math_verify/__init__.py:5]()

## Configuration System Architecture

The configuration system provides fine-grained control over extraction and normalization behavior:

```mermaid
graph TB
    subgraph "Extraction Configuration Hierarchy"
        BaseConfig["Base Extraction Config"]
        LatexConfig["LatexExtractionConfig"]
        ExprConfig["ExprExtractionConfig"]
        StringConfig["StringExtractionConfig"]
    end
    
    subgraph "Normalization Configuration"
        NormConfig["LatexNormalizationConfig"]
        BasicLatexOpt["basic_latex"]
        UnitsOpt["units"]
        MalformedOpt["malformed_operators"]
        BoxedOpt["boxed"]
        EquationsOpt["equations"]
    end
    
    subgraph "Runtime Parameters"
        TimeoutConfig["timeout"]
        PrecisionConfig["rounding"]
        StrictConfig["strict_mode"]
        FallbackConfig["no_fallback"]
    end
    
    BaseConfig --> LatexConfig
    BaseConfig --> ExprConfig
    BaseConfig --> StringConfig
    
    LatexConfig --> NormConfig
    NormConfig --> BasicLatexOpt
    NormConfig --> UnitsOpt
    NormConfig --> MalformedOpt
    NormConfig --> BoxedOpt
    NormConfig --> EquationsOpt
    
    LatexConfig --> TimeoutConfig
    LatexConfig --> PrecisionConfig
    ExprConfig --> StrictConfig
    StringConfig --> FallbackConfig
```

### Configuration Parameters

Key configuration options that control system behavior:

| Parameter Category | Options | Purpose |
|-------------------|---------|---------|
| Extraction Target | `latex`, `expr`, `string` | Defines what patterns to extract |
| Normalization | `basic_latex`, `units`, `malformed_operators` | Controls LaTeX preprocessing |
| Matching Strategy | `boxed_match_priority`, `first_match` | Prioritizes extraction patterns |
| Comparison | `rounding`, `strict_mode`, `allow_set_relation_comp` | Controls verification behavior |
| Error Handling | `timeout`, `raise_on_error`, `no_fallback` | Manages failure modes |

Sources: [src/math_verify/__init__.py:1-3](), [README.md:195-210]()

## Data Flow and Integration

The complete data flow through the Math-Verify system follows this processing pipeline:

```mermaid
flowchart TD
    RawInput["Raw Text Input"]
    
    subgraph "Parsing Phase"
        ConfigSelection["Configuration Selection"]
        PatternMatching["Pattern Matching"]
        Extraction["Expression Extraction"]
        TimeoutGuard["Timeout Protection"]
    end
    
    subgraph "Normalization Phase"
        LaTeXNorm["LaTeX Normalization"]
        UnitHandling["Unit Processing"]
        OperatorFix["Operator Correction"]
    end
    
    subgraph "Conversion Phase"
        ANTLR4Parse["ANTLR4 Parsing"]
        SymPyConvert["SymPy Conversion"] 
        ErrorHandling["Error Recovery"]
    end
    
    subgraph "Verification Phase"
        TypeDetect["Type Detection"]
        ComparisonStrategy["Strategy Selection"]
        Verification["Expression Comparison"]
        ResultReturn["Result Generation"]
    end
    
    RawInput --> ConfigSelection
    ConfigSelection --> PatternMatching
    PatternMatching --> Extraction
    Extraction --> TimeoutGuard
    
    TimeoutGuard --> LaTeXNorm
    LaTeXNorm --> UnitHandling
    UnitHandling --> OperatorFix
    
    OperatorFix --> ANTLR4Parse
    ANTLR4Parse --> SymPyConvert
    SymPyConvert --> ErrorHandling
    
    ErrorHandling --> TypeDetect
    TypeDetect --> ComparisonStrategy
    ComparisonStrategy --> Verification
    Verification --> ResultReturn
```

### Integration with External Dependencies

The system integrates with several external libraries:

| Dependency | Integration Point | Purpose |
|------------|------------------|---------|
| `latex2sympy2_extended` | Normalization and parsing | LaTeX to SymPy conversion |
| `sympy` | Verification engine | Symbolic mathematics operations |
| `antlr4-python3-runtime` | Parser generation | Grammar-based expression parsing |
| `lighteval` | Evaluation framework | Model evaluation pipeline |

Sources: [README.md:115-138](), [README.md:10-21]()

---

