<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mathematics_dataset · page 4 Mathematical Domain Modules · fetched 2026-10-26 -->

# Mathematical Domain Modules

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mathematics_dataset/modules/modules.py](mathematics_dataset/modules/modules.py)

</details>



## Purpose and Scope

This document covers the mathematical domain modules that form the core of the problem generation system. These modules implement domain-specific logic for generating questions across eight mathematical subject areas: algebra, arithmetic, calculus, comparison, measurement, numbers, polynomials, and probability. Each module provides structured problem generators that can be configured for different difficulty levels and training/testing regimes.

For detailed documentation of individual modules, see [Algebra Module](#4.1), [Arithmetic Module](#4.2), [Calculus Module](#4.3), and [Other Mathematical Modules](#4.4). For information about the underlying mathematical infrastructure used by these modules, see [Mathematical Infrastructure](#3.2).

## Module Organization and Registry

The mathematical domain modules are organized through a centralized registry system implemented in [mathematics_dataset/modules/modules.py](). This registry provides a unified interface for accessing and initializing all mathematical domains.

### Module Registry Structure

```mermaid
graph TB
    subgraph "modules.py Registry"
        ALL_DICT["all_ = {...}"]
        TRAIN_FN["train(entropy_fn)"]
        TEST_FN["test()"]
        TEST_EXTRA_FN["test_extra()"]
    end
    
    subgraph "Domain Module Imports"
        ALG_IMP["algebra"]
        ARITH_IMP["arithmetic"]
        CALC_IMP["calculus"]
        COMP_IMP["comparison"]
        MEAS_IMP["measurement"]
        NUM_IMP["numbers"]
        POLY_IMP["polynomials"]
        PROB_IMP["probability"]
    end
    
    subgraph "Module Instances"
        ALG_MOD["algebra.train()"]
        ARITH_MOD["arithmetic.train()"]
        CALC_MOD["calculus.train()"]
        COMP_MOD["comparison.train()"]
        MEAS_MOD["measurement.train()"]
        NUM_MOD["numbers.train()"]
        POLY_MOD["polynomials.train()"]
        PROB_MOD["probability.train()"]
    end
    
    ALG_IMP --> ALL_DICT
    ARITH_IMP --> ALL_DICT
    CALC_IMP --> ALL_DICT
    COMP_IMP --> ALL_DICT
    MEAS_IMP --> ALL_DICT
    NUM_IMP --> ALL_DICT
    POLY_IMP --> ALL_DICT
    PROB_IMP --> ALL_DICT
    
    ALL_DICT --> TRAIN_FN
    ALL_DICT --> TEST_FN
    ALL_DICT --> TEST_EXTRA_FN
    
    TRAIN_FN --> ALG_MOD
    TRAIN_FN --> ARITH_MOD
    TRAIN_FN --> CALC_MOD
    TRAIN_FN --> COMP_MOD
    TRAIN_FN --> MEAS_MOD
    TRAIN_FN --> NUM_MOD
    TRAIN_FN --> POLY_MOD
    TRAIN_FN --> PROB_MOD
```

The `all_` dictionary [mathematics_dataset/modules/modules.py:32-41]() serves as the master registry, mapping module names to their corresponding module objects. This centralized approach ensures consistent access patterns across the system.

**Sources:** [mathematics_dataset/modules/modules.py:21-41]()

### Module Interface Functions

The registry provides three key functions that return dictionaries of configured modules:

| Function | Purpose | Configuration |
|----------|---------|---------------|
| `train(entropy_fn)` | Training modules | Configured with entropy function for difficulty control |
| `test()` | Standard testing modules | Default testing configuration |
| `test_extra()` | Extrapolation testing modules | Extended difficulty range for testing |

Each function iterates through the `all_` dictionary and calls the corresponding method on each domain module [mathematics_dataset/modules/modules.py:44-58]().

**Sources:** [mathematics_dataset/modules/modules.py:44-58]()

## Training and Testing Regimes

Mathematical domain modules support different operational regimes that control problem difficulty and sampling behavior. The regime system enables curriculum learning by providing graduated difficulty levels.

### Regime Configuration Flow

```mermaid
flowchart TD
    ENTROPY_FN["entropy_fn"]
    TRAIN_CALL["modules.train(entropy_fn)"]
    TEST_CALL["modules.test()"]
    TEST_EXTRA_CALL["modules.test_extra()"]
    
    subgraph "Module Initialization"
        MOD_TRAIN["module.train(entropy_fn)"]
        MOD_TEST["module.test()"]
        MOD_TEST_EXTRA["module.test_extra()"]
    end
    
    subgraph "Configured Module Sets"
        TRAIN_DICT["{'algebra': algebra_train, 'arithmetic': arithmetic_train, ...}"]
        TEST_DICT["{'algebra': algebra_test, 'arithmetic': arithmetic_test, ...}"]
        TEST_EXTRA_DICT["{'algebra': algebra_extra, 'arithmetic': arithmetic_extra, ...}"]
    end
    
    ENTROPY_FN --> TRAIN_CALL
    TRAIN_CALL --> MOD_TRAIN
    TEST_CALL --> MOD_TEST
    TEST_EXTRA_CALL --> MOD_TEST_EXTRA
    
    MOD_TRAIN --> TRAIN_DICT
    MOD_TEST --> TEST_DICT
    MOD_TEST_EXTRA --> TEST_EXTRA_DICT
```

### Regime Types

**Training Regime (`train`)**
- Accepts an `entropy_fn` parameter for difficulty control
- Enables curriculum learning through entropy-based problem selection
- Used for generating training datasets with controlled difficulty progression

**Testing Regime (`test`)**
- Uses default difficulty settings appropriate for evaluation
- Provides consistent baseline for model assessment
- No entropy function parameterization

**Extrapolation Testing Regime (`test_extra`)**
- Generates problems beyond the typical training difficulty range
- Tests model generalization to unseen problem complexities
- Used for measuring extrapolation capabilities

**Sources:** [mathematics_dataset/modules/modules.py:44-58]()

## Domain Overview

The system includes eight mathematical domains, each implementing specialized problem generation logic for their respective subject areas. Each domain module follows a consistent interface pattern, providing `train()`, `test()`, and `test_extra()` methods.

### Domain Module Mapping

| Domain | Module Name | Primary Focus Areas |
|--------|-------------|-------------------|
| `algebra` | Linear equations, polynomial roots, sequences |
| `arithmetic` | Basic operations, mixed expressions, surds |
| `calculus` | Differentiation problems |
| `comparison` | Sorting and ordering operations |
| `measurement` | Unit conversions, time calculations |
| `numbers` | Number theory (GCD, LCM, primality, bases) |
| `polynomials` | Polynomial manipulation and evaluation |
| `probability` | Sampling without replacement |

### Module Dependencies

```mermaid
graph TB
    subgraph "Domain Modules"
        ALG["algebra"]
        ARITH["arithmetic"]
        CALC["calculus"]
        COMP["comparison"]
        MEAS["measurement"]
        NUM["numbers"]
        POLY["polynomials"]
        PROB["probability"]
    end
    
    subgraph "Shared Infrastructure"
        NUMBER["number.py"]
        OPS["ops.py"]
        DISPLAY["display/"]
        COMPOSITION["composition/"]
    end
    
    ALG --> NUMBER
    ALG --> OPS
    ALG --> COMPOSITION
    
    ARITH --> NUMBER
    ARITH --> OPS
    ARITH --> DISPLAY
    
    CALC --> NUMBER
    CALC --> OPS
    
    POLY --> NUMBER
    POLY --> OPS
    
    NUM --> NUMBER
    NUM --> DISPLAY
    
    MEAS --> NUMBER
    MEAS --> DISPLAY
    
    COMP --> NUMBER
    COMP --> DISPLAY
    
    PROB --> NUMBER
    PROB --> COMPOSITION
```

Each domain module leverages the shared mathematical infrastructure while implementing domain-specific problem generation logic. The modules are designed to be self-contained, allowing for independent development and testing of individual mathematical areas.

**Sources:** [mathematics_dataset/modules/modules.py:21-28](), [mathematics_dataset/modules/modules.py:32-41]()

---

