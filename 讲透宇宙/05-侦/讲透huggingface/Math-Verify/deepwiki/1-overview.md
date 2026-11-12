<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/Math-Verify · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



This document provides a comprehensive overview of the Math-Verify system, a robust mathematical expression evaluation library designed for assessing Large Language Model (LLM) outputs in mathematical tasks. Math-Verify addresses critical limitations in existing mathematical evaluators by providing format-agnostic answer extraction, advanced parsing capabilities, and intelligent expression comparison.

For detailed information about specific components, see [Core Components](#3). For practical usage instructions, see [Usage Guide](#4). For model evaluation workflows, see [Evaluation Framework](#5).

## Purpose and Scope

Math-Verify is a HuggingFace library that solves a fundamental problem in LLM evaluation: accurately assessing mathematical answers regardless of their format or representation. The system achieves higher accuracy than existing evaluators on the MATH dataset, with a score of 0.1328 compared to 0.0802 (Harness) and 0.1288 (Qwen).

The library serves three primary use cases:
- **Individual Expression Verification**: Direct comparison of mathematical expressions using `parse()` and `verify()` functions
- **Batch Output Processing**: Evaluation of model outputs stored in CSV format using `evaluate_model_outputs.py`
- **End-to-End Model Evaluation**: Complete evaluation pipeline using `evaluate_model.py` with support for datasets including GSM8K, MATH-Hard, AIME24, and AMC23

**Sources**: [pyproject.toml:1-25](), [README.md:1-8](), [README.md:78-105]()

## System Architecture

Math-Verify follows a layered architecture with clear separation between parsing, verification, and evaluation concerns:

```mermaid
graph TB
    subgraph "Core Math-Verify System"
        direction TB
        parse["math_verify.parse<br/>Expression Extraction & Parsing"]
        verify["math_verify.verify<br/>Mathematical Verification"]
        metric["math_verify.math_metric<br/>Evaluation Metrics"]
    end
    
    subgraph "External Dependencies"
        direction TB
        latex2sympy["latex2sympy2_extended==1.10.2<br/>LaTeX→SymPy Conversion"]
        sympy["SymPy<br/>Symbolic Mathematics Engine"]
        antlr4["ANTLR4 Runtime<br/>Parser Generation"]
    end
    
    subgraph "Evaluation Infrastructure"
        direction TB
        lighteval["lighteval[math]<br/>Model Evaluation Framework"]
        tasks["Mathematical Task Definitions<br/>GSM8K, MATH-Hard, AIME24, AMC23"]
    end
    
    subgraph "Command-Line Applications"
        direction TB
        evaluate_model["evaluate_model.py<br/>End-to-End Model Evaluation"]
        evaluate_outputs["evaluate_model_outputs.py<br/>Batch Output Processing"]
        extract_answers["extract_answers.py<br/>Answer Extraction Tool"]
    end
    
    parse --> latex2sympy
    verify --> parse
    verify --> sympy
    metric --> verify
    
    evaluate_model --> lighteval
    evaluate_model --> tasks
    evaluate_outputs --> parse
    evaluate_outputs --> verify
    extract_answers --> parse
    
    latex2sympy --> antlr4
    latex2sympy --> sympy
    
    lighteval --> metric
```

**Sources**: [pyproject.toml:22-30](), [README.md:85-105]()

## Core Processing Workflow

The mathematical verification process follows a three-step pipeline that transforms raw text input into verified mathematical results:

```mermaid
flowchart TD
    input["Raw Model Output<br/>Mixed text with mathematical content"]
    
    subgraph "Step 1: Answer Extraction"
        direction TB
        configs["ExtractionConfig Classes<br/>LatexExtractionConfig<br/>ExprExtractionConfig<br/>StringExtractionConfig"]
        regex["Priority-Based Regex Matching<br/>Format-agnostic extraction"]
        timeout["Timeout Protection<br/>TimeoutException handling"]
    end
    
    subgraph "Step 2: Expression Parsing"
        direction TB
        normalize["LaTeX Normalization<br/>\\boxed{} processing<br/>Unit removal<br/>Malformed operator fixes"]
        antlr_parse["ANTLR4 Grammar Parsing<br/>latex2sympy2_extended"]
        sympy_convert["SymPy Expression Conversion<br/>Common representation"]
    end
    
    subgraph "Step 3: Mathematical Verification"
        direction TB
        string_comp["String Comparison<br/>Direct normalization match"]
        numeric_comp["Numeric Comparison<br/>Precision-based equality"]
        symbolic_comp["Symbolic Comparison<br/>SymPy expression equality"]
        special_comp["Special Type Handling<br/>Sets, Relations, Matrices"]
    end
    
    result["Boolean Verification Result<br/>+ Optional extracted values"]
    gold["Gold Standard Expression"] 
    
    input --> configs
    configs --> regex
    regex --> timeout
    timeout --> normalize
    normalize --> antlr_parse
    antlr_parse --> sympy_convert
    
    sympy_convert --> string_comp
    string_comp --> numeric_comp
    numeric_comp --> symbolic_comp
    symbolic_comp --> special_comp
    special_comp --> result
    
    gold --> special_comp
```

**Sources**: [README.md:112-175]()

## Key Components and Modules

Math-Verify consists of three primary modules that handle different aspects of mathematical verification:

| Module | Primary Functions | Purpose |
|--------|------------------|---------|
| `math_verify.parse` | `parse()`, extraction configs | Format-agnostic answer extraction from text |
| `math_verify.verify` | `verify()`, comparison strategies | Mathematical expression verification |
| `math_verify.math_metric` | Evaluation metrics | Model performance assessment |

### Core Function Interface

```mermaid
graph LR
    subgraph "Public API Functions"
        direction TB
        parse_func["parse(text, extraction_config=None)<br/>Returns: SymPy expression"]
        verify_func["verify(gold, answer, **kwargs)<br/>Returns: Boolean result"]
    end
    
    subgraph "Configuration Classes"
        direction TB
        latex_config["LatexExtractionConfig<br/>LaTeX environment parsing"]
        expr_config["ExprExtractionConfig<br/>Plain expression parsing"]  
        string_config["StringExtractionConfig<br/>Literal string matching"]
        norm_config["NormalizationConfig<br/>Preprocessing options"]
    end
    
    subgraph "Internal Processing"
        direction TB
        extraction["Answer Extraction Logic"]
        normalization["LaTeX Normalization"]
        comparison["Multi-Strategy Comparison"]
    end
    
    parse_func --> latex_config
    parse_func --> expr_config
    parse_func --> string_config
    parse_func --> extraction
    
    verify_func --> norm_config
    verify_func --> comparison
    
    extraction --> normalization
    normalization --> comparison
```

**Sources**: [README.md:23-36](), [README.md:38-46]()

## Supported Mathematical Types

Math-Verify provides comprehensive support for diverse mathematical expression types commonly found in LLM outputs:

| Type Category | Examples | Verification Strategy |
|---------------|----------|----------------------|
| **Numeric** | `1/3`, `0.333`, `33.33%` | Precision-based comparison |
| **Symbolic** | `x + 2y`, `sin(π/4)` | SymPy symbolic equality |
| **Sets** | `{1,2,3}`, `(1,3) ∪ (2,4)` | Element-wise and operation comparison |
| **Relations** | `x < 2`, `1 ≤ y ≤ 5` | Normalized form and flip support |
| **Matrices** | `[[1,2],[3,4]]` | Element-wise with shape validation |
| **Complex** | `2+3i`, `Re(z)` | Component-wise comparison |

**Sources**: [README.md:55-77](), [README.md:145-175]()

## Integration Points and Dependencies

Math-Verify integrates with the broader Python mathematical and ML ecosystem through well-defined dependency relationships:

```mermaid
graph TB
    subgraph "Math-Verify Core"
        direction TB
        core_lib["src/math_verify/<br/>Core library modules"]
    end
    
    subgraph "Required Dependencies"
        direction TB
        latex2sympy_dep["latex2sympy2_extended==1.10.2<br/>LaTeX parsing and normalization"]
        python_runtime["Python >=3.10<br/>Runtime requirement"]
    end
    
    subgraph "Optional Dependencies"
        direction TB
        lighteval_dep["lighteval[math]<br/>Model evaluation (inference extra)"]
        antlr_variants["ANTLR4 Runtime Variants<br/>4.9.3, 4.11.0, 4.13.2"]
        dev_tools["Development Tools<br/>pytest, ruff (dev/test extras)"]
    end
    
    subgraph "External Integrations"
        direction TB
        hf_ecosystem["HuggingFace Ecosystem<br/>Model hub, datasets"]
        pypi_dist["PyPI Distribution<br/>Package management"]
    end
    
    core_lib --> latex2sympy_dep
    core_lib --> python_runtime
    
    latex2sympy_dep --> antlr_variants
    
    core_lib -.-> lighteval_dep
    core_lib -.-> dev_tools
    
    lighteval_dep --> hf_ecosystem
    core_lib --> pypi_dist
```

**Sources**: [pyproject.toml:22-56](), [README.md:10-21]()

## Version and Compatibility

The current version 0.8.0 introduces enhanced error handling capabilities with the `raise_on_error` parameter and improved `\boxed{}` expression processing. The system maintains compatibility across Python 3.10+ and supports multiple ANTLR4 runtime versions for maximum deployment flexibility.

Key version features include:
- **Flexible ANTLR4 Support**: Compatible with runtimes 4.9.3, 4.11.0, and 4.13.2
- **Error Handling Options**: Configurable exception propagation via `raise_on_error` parameter  
- **Enhanced Logging**: Debug-level error logging with optional verbose modes
- **Boxed Expression Improvements**: Better handling of units, percentages, and multiple boxed values

**Sources**: [pyproject.toml:3](), [pyproject.toml:16-18](), [pyproject.toml:45-55](), [CHANGELOG.md:3-10]()

---

