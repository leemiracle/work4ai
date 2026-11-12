<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/distrax · page 6 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [distrax/_src/distributions/categorical.py](distrax/_src/distributions/categorical.py)
- [distrax/_src/distributions/categorical_test.py](distrax/_src/distributions/categorical_test.py)
- [distrax/_src/distributions/distribution_from_tfp_test.py](distrax/_src/distributions/distribution_from_tfp_test.py)
- [setup.py](setup.py)
- [test.sh](test.sh)

</details>



This document covers the development workflow, testing framework, and quality assurance practices for Distrax. It provides guidance for contributors on testing methodologies, CI/CD pipeline, and development best practices.

For information about the core distribution and bijector APIs, see [Core Concepts](#2). For specific testing of distributions, see [Distributions](#3).

## Overview

Distrax employs a comprehensive testing strategy that ensures mathematical correctness, JAX compatibility, and seamless integration with TensorFlow Probability. The testing framework is built around equivalence testing, which validates that Distrax implementations produce identical results to their TFP counterparts while maintaining JAX-native performance benefits.

```mermaid
graph TB
    subgraph "Development Workflow"
        DEV["Developer Changes"]
        LOCAL["Local Testing<br/>test.sh"]
        PR["Pull Request"]
        CI["GitHub Actions CI"]
    end
    
    subgraph "Testing Framework"
        EQUIV["EquivalenceTest<br/>Base Class"]
        UNIT["Unit Tests"]
        INTEGRATION["Integration Tests"] 
        COMPAT["TFP Compatibility Tests"]
    end
    
    subgraph "Quality Gates"
        LINT["Code Linting<br/>flake8, pylint"]
        TYPE["Type Checking<br/>pytype"]
        TEST["Test Execution<br/>pytest"]
        BUILD["Package Build<br/>setup.py"]
    end
    
    DEV --> LOCAL
    LOCAL --> PR
    PR --> CI
    
    LOCAL --> EQUIV
    CI --> EQUIV
    
    EQUIV --> UNIT
    EQUIV --> INTEGRATION
    EQUIV --> COMPAT
    
    CI --> LINT
    CI --> TYPE
    CI --> TEST
    CI --> BUILD
    
    style DEV fill:#f9f9f9
    style EQUIV fill:#e1f5fe
    style CI fill:#e8f5e8
```

**Testing Framework Architecture**

Sources: [.github/workflows/tests.yml:1-29](), [test.sh:1-87](), [distrax/_src/distributions/categorical_test.py:29-34]()

## Continuous Integration Pipeline

The CI/CD pipeline runs on GitHub Actions and executes a comprehensive test suite across multiple Python versions and environments.

### Pipeline Configuration

The CI pipeline is configured to run on:
- **Triggers**: Push to master, pull requests, and nightly scheduled runs
- **Python Versions**: 3.9, 3.10, 3.11
- **Operating System**: Ubuntu Latest
- **Test Script**: `test.sh`

```mermaid
graph LR
    subgraph "Trigger Events"
        PUSH["Push to Master"]
        PR["Pull Request"]
        SCHEDULE["Nightly Schedule<br/>3:30 AM UTC"]
    end
    
    subgraph "Matrix Strategy"
        PY39["Python 3.9"]
        PY310["Python 3.10"] 
        PY311["Python 3.11"]
        UBUNTU["ubuntu-latest"]
    end
    
    subgraph "Test Execution"
        CHECKOUT["actions/checkout@v2"]
        SETUP["actions/setup-python@v1"]
        TEST["bash test.sh"]
    end
    
    PUSH --> CHECKOUT
    PR --> CHECKOUT
    SCHEDULE --> CHECKOUT
    
    CHECKOUT --> SETUP
    SETUP --> TEST
    
    PY39 --> TEST
    PY310 --> TEST
    PY311 --> TEST
    UBUNTU --> TEST
    
    style TEST fill:#e8f5e8
    style SCHEDULE fill:#fff3e0
```

**CI/CD Pipeline Flow**

Sources: [.github/workflows/tests.yml:1-29]()

### Test Script Workflow

The main test script [`test.sh`] implements a multi-stage testing process:

| Stage | Tools | Purpose |
|-------|-------|---------|
| Environment Setup | `python3 -m venv`, `pip` | Isolated dependency management |
| Code Linting | `flake8`, `pylint` | Code style and quality enforcement |
| Package Building | `setup.py`, `pip wheel` | Installation verification |
| Type Checking | `pytype` | Static type analysis |
| Test Execution | `pytest` | Comprehensive test suite |

```mermaid
graph TB
    subgraph "Environment Preparation"
        VENV["Virtual Environment<br/>/tmp/distrax-env"]
        DEPS["Dependency Installation<br/>requirements.txt"]
        TFP["TFP Nightly<br/>tfp-nightly"]
    end
    
    subgraph "Quality Checks"
        FLAKE8["flake8<br/>E9,F63,F7,F82,E225,E251"]
        PYLINT["pylint<br/>Google OSS Config"]
        PYTYPE["pytype<br/>Static Type Check"]
    end
    
    subgraph "Package Verification"
        SDIST["setup.py sdist"]
        WHEEL["pip wheel"]
        INSTALL["pip install"]
    end
    
    subgraph "Test Execution"
        MAIN["Main Tests<br/>JAX_DISABLE_MOST_OPTIMIZATIONS"]
        FLOAT64["Float64 Tests<br/>Isolated Execution"]
        PARALLEL["Parallel Execution<br/>pytest -n"]
    end
    
    VENV --> DEPS
    DEPS --> TFP
    TFP --> FLAKE8
    FLAKE8 --> PYLINT
    PYLINT --> PYTYPE
    PYTYPE --> SDIST
    SDIST --> WHEEL
    WHEEL --> INSTALL
    INSTALL --> MAIN
    MAIN --> FLOAT64
    
    style VENV fill:#f9f9f9
    style MAIN fill:#e8f5e8
    style PYTYPE fill:#e1f5fe
```

**Test Script Execution Flow**

Sources: [test.sh:19-86]()

## Testing Framework

### EquivalenceTest Base Class

The core of Distrax's testing strategy is the `EquivalenceTest` framework, which ensures mathematical equivalence between Distrax and TensorFlow Probability implementations.

#### Test Structure Pattern

All distribution and bijector tests follow a consistent pattern:

```python
class ExampleTest(equivalence.EquivalenceTest):
    def setUp(self):
        super().setUp()
        self._init_distr_cls(example.Example)
```

Key testing methods provided by `EquivalenceTest`:
- `_test_sample_shape()` - Validates sample shape consistency
- `_test_sample_and_log_prob()` - Cross-validates sampling and probability computation
- `_test_attribute()` - Tests distribution properties and methods
- `_test_with_two_distributions()` - Tests KL divergence and cross-entropy

Sources: [distrax/_src/distributions/categorical_test.py:29-34]()

### JAX Transformation Testing

Distrax extensively tests compatibility with JAX transformations using the `@chex.all_variants` decorator:

| Transformation | Test Coverage |
|----------------|---------------|
| `jit` | JIT compilation compatibility |
| `vmap` | Vectorization across batch dimensions |
| `pmap` | Parallel mapping (where applicable) |
| `grad` | Gradient computation verification |

Example test pattern:
```python
@chex.all_variants
@parameterized.named_parameters(...)
def test_sample_and_log_prob(self, distr_params, sample_shape):
    super()._test_sample_and_log_prob(...)
```

Sources: [distrax/_src/distributions/categorical_test.py:64-132]()

### TensorFlow Probability Compatibility

#### Cross-Framework Validation

```mermaid
graph TB
    subgraph "Distrax Implementation"
        DISTRAX_DIST["Distrax Distribution"]
        DISTRAX_METHOD["dist.method()"]
        DISTRAX_RESULT["Distrax Result"]
    end
    
    subgraph "TFP Reference"
        TFP_DIST["TFP Distribution<br/>equiv_tfp_cls"]
        TFP_METHOD["tfp_dist.method()"]
        TFP_RESULT["TFP Result"]
    end
    
    subgraph "Validation"
        COMPARE["assertion_fn<br/>rtol/atol comparison"]
        PASS["Test Pass/Fail"]
    end
    
    DISTRAX_DIST --> DISTRAX_METHOD
    DISTRAX_METHOD --> DISTRAX_RESULT
    
    TFP_DIST --> TFP_METHOD
    TFP_METHOD --> TFP_RESULT
    
    DISTRAX_RESULT --> COMPARE
    TFP_RESULT --> COMPARE
    COMPARE --> PASS
    
    style COMPARE fill:#e1f5fe
    style PASS fill:#e8f5e8
```

**Cross-Framework Validation Process**

#### KL Divergence Registration Testing

Distrax tests bidirectional KL divergence compatibility:

```python
# Test patterns for KL divergence
('kl distrax_to_distrax', 'kl_divergence', 'distrax_to_distrax'),
('kl distrax_to_tfp', 'kl_divergence', 'distrax_to_tfp'),
('kl tfp_to_distrax', 'kl_divergence', 'tfp_to_distrax'),
```

Sources: [distrax/_src/distributions/categorical_test.py:307-324](), [distrax/_src/distributions/categorical.py:203-216]()

### Parameterized Testing

Distrax uses extensive parameterized testing to cover edge cases and different configurations:

#### Test Parameter Categories

| Category | Examples | Purpose |
|----------|----------|---------|
| Input Types | `logits` vs `probs` | Parameter flexibility |
| Data Types | `int16`, `int32`, `float32`, `float64` | Type safety |
| Shapes | `1d`, `2d`, batch dimensions | Broadcasting compatibility |
| Edge Cases | `inf`, `-inf`, `0.0` values | Numerical stability |

Example parameterized test:
```python
@parameterized.named_parameters(
    ('1d logits', (4,), False),
    ('2d probs', (3, 4), True),
)
def test_properties(self, shape, from_probs):
```

Sources: [distrax/_src/distributions/categorical_test.py:35-52]()

## Development Best Practices

### Code Quality Standards

#### Linting Configuration

The project uses a multi-layered linting approach:

1. **flake8**: Basic syntax and style checking
   - Selected error codes: `E9`, `F63`, `F7`, `F82`, `E225`, `E251`
   
2. **pylint**: Advanced code quality analysis
   - Based on Google's Open Source Style Guide
   - Custom disabled warnings for test files

#### Type Checking

- **Tool**: `pytype` (Python < 3.11)
- **Scope**: All source files in `distrax/_src/`
- **Configuration**: Jittable type safety verification

Sources: [test.sh:32-66]()

### Testing Guidelines

#### Test Organization

```mermaid
graph TB
    subgraph "Source Structure"
        SRC["distrax/_src/"]
        DIST["distributions/"]
        BIJ["bijectors/"]
        UTIL["utils/"]
    end
    
    subgraph "Test Structure" 
        DIST_TEST["*_test.py<br/>Distribution Tests"]
        BIJ_TEST["*_test.py<br/>Bijector Tests"] 
        UTIL_TEST["*_test.py<br/>Utility Tests"]
    end
    
    subgraph "Test Categories"
        UNIT_TEST["Unit Tests<br/>Individual Methods"]
        INTEGRATION_TEST["Integration Tests<br/>Cross-Component"]
        COMPAT_TEST["Compatibility Tests<br/>TFP Equivalence"]
    end
    
    SRC --> DIST
    SRC --> BIJ  
    SRC --> UTIL
    
    DIST --> DIST_TEST
    BIJ --> BIJ_TEST
    UTIL --> UTIL_TEST
    
    DIST_TEST --> UNIT_TEST
    DIST_TEST --> INTEGRATION_TEST
    DIST_TEST --> COMPAT_TEST
    
    style DIST_TEST fill:#e1f5fe
    style COMPAT_TEST fill:#fff3e0
```

**Test Organization Structure**

#### Required Test Coverage

For new distributions or bijectors, tests must cover:

1. **Core Functionality**
   - `sample()`, `log_prob()`, `prob()`
   - `entropy()`, `mode()`, statistical properties
   
2. **JAX Compatibility**  
   - JIT compilation with `@chex.all_variants`
   - Vectorization with `vmap`
   - Gradient computation
   
3. **TFP Equivalence**
   - Cross-validation against `equiv_tfp_cls`
   - KL divergence registration
   
4. **Edge Cases**
   - Invalid inputs, boundary conditions
   - Numerical stability with extreme values

Sources: [distrax/_src/distributions/categorical_test.py:377-454]()

### Contribution Workflow

#### Pull Request Requirements

1. **Local Testing**: Run `bash test.sh` successfully
2. **Code Review**: All submissions require review
3. **CLA**: Contributor License Agreement required
4. **Style Compliance**: Pass all linting checks

#### Package Building

The setup process validates package integrity:

```python
# Package configuration
install_requires=_parse_requirements('requirements/requirements.txt')
tests_require=_parse_requirements('requirements/requirements-tests.txt')
python_requires='>=3.9'
```

Sources: [setup.py:44-77](), [CONTRIBUTING.md:1-35]()

---

