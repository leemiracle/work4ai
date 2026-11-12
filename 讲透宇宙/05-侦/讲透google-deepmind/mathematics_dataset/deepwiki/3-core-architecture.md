<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mathematics_dataset · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mathematics_dataset/generate.py](mathematics_dataset/generate.py)

</details>



This document explains the fundamental systems that power the mathematical problem generation in the mathematics dataset. It covers the high-level architecture, the orchestration mechanisms, and how the various components interact to generate mathematical question-answer pairs.

For detailed information about specific aspects: the generation pipeline flow is covered in [Question Generation Pipeline](#3.1), mathematical building blocks in [Mathematical Infrastructure](#3.2), problem assembly in [Composition and Display System](#3.3), and individual problem structure in [Problem Structure and Templates](#3.4).

## System Overview

The mathematics dataset generation system is built around a modular architecture that separates concerns between problem orchestration, mathematical domain logic, and infrastructure utilities. The system generates problems across multiple difficulty levels and mathematical domains through a pipeline that can be configured for different training and testing regimes.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Generation Orchestration"
        generate["generate.py"]
        init_modules["init_modules()"]
        sample_from_module["sample_from_module()"]
        filter_and_flatten["_filter_and_flatten()"]
    end
    
    subgraph "Module System"
        modules_train["modules.train()"]
        modules_test["modules.test()"]
        modules_test_extra["modules.test_extra()"]
        entropy_fn["_make_entropy_fn()"]
    end
    
    subgraph "Domain Modules"
        algebra["algebra"]
        arithmetic["arithmetic"]
        calculus["calculus"]
        comparison["comparison"]
        measurement["measurement"]
        numbers["numbers"]
        polynomials["polynomials"]
        probability["probability"]
    end
    
    subgraph "Infrastructure"
        generate_settings["generate_settings"]
        composition["composition"]
        number_py["number.py"]
        ops_py["ops.py"]
        display["display"]
    end
    
    generate --> init_modules
    generate --> sample_from_module
    generate --> filter_and_flatten
    
    init_modules --> modules_train
    init_modules --> modules_test
    init_modules --> modules_test_extra
    init_modules --> entropy_fn
    
    modules_train --> algebra
    modules_train --> arithmetic
    modules_train --> calculus
    modules_train --> comparison
    modules_train --> measurement
    modules_train --> numbers
    modules_train --> polynomials
    modules_train --> probability
    
    algebra --> composition
    arithmetic --> number_py
    calculus --> ops_py
    composition --> display
    
    sample_from_module --> generate_settings
```

Sources: [mathematics_dataset/generate.py:1-173]()

## Generation Orchestration

The primary orchestration layer is implemented in `generate.py`, which manages the entire question generation process through several key functions:

### Module Initialization

The `init_modules()` function sets up the problem generation modules for different training regimes:

| Regime | Description | Entropy Function |
|--------|-------------|------------------|
| `train-easy` | Lower 1/3 difficulty range | `_make_entropy_fn(0, 3)` |
| `train-medium` | Middle 1/3 difficulty range | `_make_entropy_fn(1, 3)` |
| `train-hard` | Upper 1/3 difficulty range | `_make_entropy_fn(2, 3)` |
| `interpolate` | Test within training range | `modules.test()` |
| `extrapolate` | Test beyond training range | `modules.test_extra()` |

The system maintains global state in `filtered_modules` and `counts` dictionaries to track available modules and generation quotas.

Sources: [mathematics_dataset/generate.py:92-117]()

### Entropy-Based Difficulty Control

```mermaid
graph LR
    subgraph "Difficulty Levels"
        level0["Level 0 (Easy)"]
        level1["Level 1 (Medium)"]  
        level2["Level 2 (Hard)"]
    end
    
    subgraph "Entropy Mapping"
        make_entropy_fn["_make_entropy_fn(level, num_levels)"]
        modify_entropy["modify_entropy(range_)"]
    end
    
    subgraph "Range Calculation"
        lower["lower = level / num_levels"]
        upper["upper = (level + 1) / num_levels"]
        new_range["range_[0] + lower * length, range_[0] + upper * length"]
    end
    
    level0 --> make_entropy_fn
    level1 --> make_entropy_fn
    level2 --> make_entropy_fn
    
    make_entropy_fn --> modify_entropy
    modify_entropy --> lower
    modify_entropy --> upper
    lower --> new_range
    upper --> new_range
```

The `_make_entropy_fn()` creates difficulty control functions that map entropy ranges to specific difficulty levels. Each level gets an equal subdivision of the total entropy range.

Sources: [mathematics_dataset/generate.py:46-65]()

## Module System Architecture

The module system provides a hierarchical structure for organizing mathematical domains and problem types. The system uses a nested dictionary structure that gets flattened and filtered during initialization.

### Module Filtering and Organization

The `_filter_and_flatten()` function processes the hierarchical module structure:

```mermaid
graph TD
    subgraph "Input Structure"
        nested_modules["Nested Module Dict"]
        algebra_sub["algebra__linear_1d"]
        arithmetic_sub["arithmetic__add_or_sub"]
    end
    
    subgraph "Processing"
        filter_and_flatten["_filter_and_flatten()"]
        add_recursive["add() recursive function"]
        flags_filter["FLAGS.filter matching"]
    end
    
    subgraph "Output Structure"
        flat_dict["Flattened OrderedDict"]
        deterministic_order["Sorted by key names"]
        filtered_results["Filtered by FLAGS.filter"]
    end
    
    nested_modules --> filter_and_flatten
    algebra_sub --> add_recursive
    arithmetic_sub --> add_recursive
    
    filter_and_flatten --> add_recursive
    add_recursive --> flags_filter
    flags_filter --> flat_dict
    flat_dict --> deterministic_order
    deterministic_order --> filtered_results
```

This flattening process creates fully qualified module names using double underscores as separators (e.g., `algebra__linear_1d__solve`), enabling precise filtering and deterministic ordering across multiple machines.

Sources: [mathematics_dataset/generate.py:68-89]()

## Problem Sampling and Validation

The `sample_from_module()` function implements the core sampling logic with built-in validation:

```mermaid
graph TD
    subgraph "Sampling Loop"
        call_module["module()"]
        get_problem["Get Problem instance"]
        extract_question["str(problem.question)"]
        extract_answer["str(problem.answer)"]
    end
    
    subgraph "Validation Checks"
        check_question_length["len(question) > MAX_QUESTION_LENGTH"]
        check_answer_length["len(answer) > MAX_ANSWER_LENGTH"]
        show_dropped["FLAGS.show_dropped logging"]
    end
    
    subgraph "Results"
        return_problem["Return (problem, num_dropped)"]
        increment_dropped["num_dropped += 1"]
        retry["Continue loop"]
    end
    
    call_module --> get_problem
    get_problem --> extract_question
    get_problem --> extract_answer
    
    extract_question --> check_question_length
    extract_answer --> check_answer_length
    
    check_question_length -->|"Too long"| increment_dropped
    check_answer_length -->|"Too long"| increment_dropped
    increment_dropped --> show_dropped
    show_dropped --> retry
    retry --> call_module
    
    check_question_length -->|"Valid"| return_problem
    check_answer_length -->|"Valid"| return_problem
```

The sampling process continues until a valid problem is generated, tracking dropped samples for monitoring purposes. Length constraints are defined in `generate_settings.MAX_QUESTION_LENGTH` and `generate_settings.MAX_ANSWER_LENGTH`.

Sources: [mathematics_dataset/generate.py:119-145]()

## Configuration and Control Flow

The system accepts several command-line flags that control generation behavior:

| Flag | Purpose | Default |
|------|---------|---------|
| `--filter` | Restrict to matching module names | `''` (empty) |
| `--per_train_module` | Examples per training module | `10` |
| `--per_test_module` | Examples per testing module | `10` |
| `--show_dropped` | Print dropped questions for debugging | `False` |

The main execution flow processes all filtered modules across all regimes, generating the specified number of problems per module while tracking and reporting dropped samples.

Sources: [mathematics_dataset/generate.py:34-39](), [mathematics_dataset/generate.py:148-172]()

---

