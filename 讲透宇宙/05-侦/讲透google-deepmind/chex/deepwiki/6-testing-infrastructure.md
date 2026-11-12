<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/chex · page 6 Testing Infrastructure · fetched 2026-10-26 -->

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chex/__init__.py](chex/__init__.py)
- [chex/_src/fake.py](chex/_src/fake.py)
- [chex/_src/fake_test.py](chex/_src/fake_test.py)
- [chex/_src/variants_test.py](chex/_src/variants_test.py)

</details>



## Purpose and Scope

This page provides an overview of Chex's testing infrastructure, which consists of two complementary systems for testing and debugging JAX code:

1. **Fake Transformations** - Replace JAX transformations (`jax.jit`, `jax.pmap`) with simpler equivalents for debugging
2. **Test Variants** - Automatically run tests across different JAX execution contexts (with/without JIT, with/without device placement, with pmap)

For detailed information about fake transformations, see [Fake Transformations](#6.1). For the test variants framework, see [Test Variants Framework](#6.2). For assertion utilities used in testing, see [Assertion System](#3).

**Sources:** [chex/__init__.py:77-101](), [chex/_src/fake.py:1-424]()

---

## Overview

Testing JAX code presents unique challenges because code behavior can differ significantly depending on execution context:

- **JIT compilation** changes how Python side effects execute
- **Device placement** affects array types and computation locations  
- **Parallel execution** (`pmap`) requires multiple devices and introduces collective operations

Chex's testing infrastructure addresses these challenges through two mechanisms:

| System | Purpose | Key Exports |
|--------|---------|-------------|
| Fake Transformations | Replace expensive JAX transforms for debugging | `fake_jit()`, `fake_pmap()`, `fake_pmap_and_jit()`, `set_n_cpu_devices()` |
| Test Variants | Run tests across execution contexts | `@variants`, `TestCase`, `params_product()`, `all_variants` |

**Sources:** [chex/__init__.py:77-102](), [chex/_src/fake.py:15-21]()

---

## Testing Infrastructure Architecture

```mermaid
graph TB
    subgraph "User Code"
        TEST["Test Suite<br/>(unittest.TestCase)"]
    end
    
    subgraph "Chex Testing Infrastructure"
        direction TB
        
        subgraph "Test Variants System"
            TESTCASE["variants.TestCase"]
            VARIANTS["@variants decorator"]
            ALL_VAR["@all_variants decorator"]
            PARAMS["params_product()"]
            
            VARIANTS --> TESTCASE
            ALL_VAR --> TESTCASE
            PARAMS --> VARIANTS
        end
        
        subgraph "Fake Transformations System"
            FAKE_JIT["fake_jit()<br/>Context Manager"]
            FAKE_PMAP["fake_pmap()<br/>Context Manager"]
            FAKE_BOTH["fake_pmap_and_jit()<br/>Context Manager"]
            SET_CPU["set_n_cpu_devices(n)"]
            
            FAKE_BOTH --> FAKE_JIT
            FAKE_BOTH --> FAKE_PMAP
            SET_CPU -.->|"enables"| FAKE_PMAP
        end
        
        subgraph "JAX Transform Interception"
            MOCK_JIT["mock.patch('jax.jit')"]
            MOCK_PMAP["mock.patch('jax.pmap')"]
            DISABLE["jax.disable_jit()"]
            
            FAKE_JIT --> DISABLE
            FAKE_PMAP --> MOCK_PMAP
        end
    end
    
    subgraph "JAX Runtime"
        JAX_JIT["jax.jit"]
        JAX_PMAP["jax.pmap"]
        JAX_VMAP["jax.vmap"]
        XLA_FLAGS["XLA_FLAGS env var"]
    end
    
    TEST -->|"inherits from"| TESTCASE
    TEST -->|"uses"| FAKE_JIT
    TEST -->|"uses"| FAKE_PMAP
    TEST -->|"configures"| SET_CPU
    
    MOCK_JIT -.->|"intercepts"| JAX_JIT
    MOCK_PMAP -.->|"intercepts"| JAX_PMAP
    MOCK_PMAP -.->|"replaces with"| JAX_VMAP
    SET_CPU -.->|"modifies"| XLA_FLAGS
    
    VARIANTS -.->|"runs test with"| FAKE_JIT
    VARIANTS -.->|"runs test with"| FAKE_PMAP
```

**Diagram: Testing Infrastructure Components and Dependencies**

This architecture shows how the two testing systems integrate with JAX. The Fake Transformations system uses `unittest.mock.patch` to intercept JAX functions, while the Test Variants system generates multiple test executions across different configurations. Both systems can be used independently or together.

**Sources:** [chex/_src/fake.py:219-258](), [chex/_src/fake.py:260-328](), [chex/_src/variants.py]() (referenced), [chex/_src/fake_test.py:52-199]()

---

## Fake Transformations System

The fake transformations system provides context managers that replace JAX's compilation and parallelization primitives with simpler alternatives. This enables:

- **Interactive debugging** - Remove JIT compilation to enable print statements and debuggers
- **Faster iteration** - Skip expensive compilation during development
- **Single-device testing** - Test `pmap` code without multiple physical devices

### Core Functions

```mermaid
graph LR
    subgraph "Fake Transform Context Managers"
        FAKE_JIT["fake_jit(enable_patching)"]
        FAKE_PMAP["fake_pmap(enable_patching,<br/>jit_result, ignore_axis_index_groups,<br/>fake_parallel_axis)"]
        FAKE_BOTH["fake_pmap_and_jit(enable_pmap_patching,<br/>enable_jit_patching)"]
    end
    
    subgraph "Implementation Details"
        IDENTITY["jax.disable_jit()"]
        VMAP["_fake_pmap()<br/>uses jax.vmap"]
        CONVERT["convert_to_varargs()"]
        IGNORE["_ignore_axis_index_groups()"]
    end
    
    subgraph "Device Setup"
        SET_N["set_n_cpu_devices(n)"]
        GET_N["get_n_cpu_devices_from_xla_flags()"]
        FLAGS_ENV["XLA_FLAGS environment variable"]
    end
    
    FAKE_JIT --> IDENTITY
    FAKE_PMAP --> VMAP
    FAKE_PMAP --> IGNORE
    FAKE_BOTH --> FAKE_JIT
    FAKE_BOTH --> FAKE_PMAP
    
    VMAP --> CONVERT
    
    SET_N --> FLAGS_ENV
    GET_N --> FLAGS_ENV
```

**Diagram: Fake Transformation Functions and Implementation**

**Sources:** [chex/_src/fake.py:219-258](), [chex/_src/fake.py:260-328](), [chex/_src/fake.py:330-353](), [chex/_src/fake.py:54-83]()

### Usage Patterns

| Pattern | Code | When to Use |
|---------|------|-------------|
| Context Manager | `with fake_jit():`<br/>`  @jax.jit`<br/>`  def f(x): ...` | Temporarily disable JIT for a code block |
| Start/Stop | `ctx = fake_jit()`<br/>`ctx.start()`<br/>`...`<br/>`ctx.stop()` | Manual control over fake scope |
| Test Setup | `def setUpModule():`<br/>`  fake.set_n_cpu_devices()` | Configure multi-device simulation for entire test module |
| Combined | `with fake_pmap_and_jit():`<br/>`  test_code()` | Disable both JIT and pmap |

**Sources:** [chex/_src/fake.py:219-258](), [chex/_src/fake_test.py:101-128](), [chex/_src/fake_test.py:33-34]()

### Key Implementation Details

The fake transformations work by intercepting JAX functions at runtime:

- **`fake_jit()`** - Calls `jax.disable_jit()` which makes JIT functions behave like identity functions [chex/_src/fake.py:255-257]()
- **`fake_pmap()`** - Uses `unittest.mock.patch` to replace `jax.pmap` with `_fake_pmap()`, which internally uses `jax.vmap` [chex/_src/fake.py:313]()
- **`_fake_pmap()`** - Converts pmap arguments to vmap-compatible form, handling `static_broadcasted_argnums` and `axis_name` [chex/_src/fake.py:124-203]()
- **`set_n_cpu_devices()`** - Modifies the `XLA_FLAGS` environment variable before XLA initialization to create virtual CPU devices [chex/_src/fake.py:54-83]()

**Sources:** [chex/_src/fake.py:219-258](), [chex/_src/fake.py:260-328](), [chex/_src/fake.py:124-203](), [chex/_src/fake.py:54-83]()

For detailed documentation of fake transformations, see [Fake Transformations](#6.1).

---

## Test Variants System

The test variants system automatically generates multiple test executions across different JAX execution contexts. Instead of writing separate tests for each configuration, you write one test and decorate it with `@variants`.

### Variant Types

```mermaid
graph TB
    subgraph "ChexVariantType Enum"
        WITHOUT_JIT["WITHOUT_JIT<br/>No transformations"]
        WITH_JIT["WITH_JIT<br/>jax.jit applied"]
        WITHOUT_DEVICE["WITHOUT_DEVICE<br/>Python scalars/arrays"]
        WITH_DEVICE["WITH_DEVICE<br/>jax.Array on device"]
        WITH_PMAP["WITH_PMAP<br/>jax.pmap applied"]
    end
    
    subgraph "Decorator Selection"
        VARIANTS["@variants(with_jit=True,<br/>without_jit=True, ...)"]
        ALL_VARIANTS["@all_variants"]
        
        ALL_VARIANTS -.->|"selects all"| WITHOUT_JIT
        ALL_VARIANTS -.->|"selects all"| WITH_JIT
        ALL_VARIANTS -.->|"selects all"| WITHOUT_DEVICE
        ALL_VARIANTS -.->|"selects all"| WITH_DEVICE
        ALL_VARIANTS -.->|"selects all"| WITH_PMAP
        
        VARIANTS -.->|"selects subset"| WITHOUT_JIT
        VARIANTS -.->|"selects subset"| WITH_JIT
    end
    
    subgraph "Test Generation"
        TEST_METHOD["test_foo()"]
        GEN["VariantsTestCaseGenerator"]
        TEST_1["test_foo_without_jit()"]
        TEST_2["test_foo_with_jit()"]
        TEST_3["test_foo_with_device()"]
        
        VARIANTS --> TEST_METHOD
        TEST_METHOD --> GEN
        GEN --> TEST_1
        GEN --> TEST_2
        GEN --> TEST_3
    end
```

**Diagram: Variant Types and Test Generation**

**Sources:** [chex/_src/variants.py]() (referenced from [chex/__init__.py:98-101]()), [chex/_src/variants_test.py:470-496]()

### Core Components

| Component | Type | Purpose |
|-----------|------|---------|
| `variants.TestCase` | Base Class | Extends `unittest.TestCase` with `self.variant` method |
| `@variants` | Decorator | Decorates test methods, specifies which variants to run |
| `@all_variants` | Decorator | Shorthand for all variant types |
| `self.variant` | Method | Wraps test functions with appropriate transformations |
| `params_product()` | Function | Generates parameter combinations for parameterized tests |

**Sources:** [chex/__init__.py:97-101](), [chex/_src/variants_test.py:62-200]()

### Usage Example

```mermaid
graph LR
    subgraph "Test Definition"
        TEST_CLASS["class MyTest(variants.TestCase)"]
        TEST_METHOD["@variants(with_jit=True,<br/>without_jit=True)<br/>def test_function(self)"]
        VARIANT_CALL["fn = self.variant(my_fn)<br/>result = fn(x)"]
        
        TEST_CLASS --> TEST_METHOD
        TEST_METHOD --> VARIANT_CALL
    end
    
    subgraph "Test Execution"
        RUN_1["test_function_without_jit()<br/>my_fn executed directly"]
        RUN_2["test_function_with_jit()<br/>jax.jit(my_fn) executed"]
        
        VARIANT_CALL -.->|"generates"| RUN_1
        VARIANT_CALL -.->|"generates"| RUN_2
    end
    
    subgraph "Transform Application"
        IDENTITY["identity function"]
        JIT["jax.jit()"]
        
        RUN_1 --> IDENTITY
        RUN_2 --> JIT
    end
```

**Diagram: Test Variants Execution Flow**

**Sources:** [chex/_src/variants_test.py:587-599](), [chex/_src/variants_test.py:111-117]()

### Integration with absltest and parameterized

The variants system integrates with `absltest.TestCase` and `parameterized.TestCase`:

```mermaid
graph TB
    BASE_1["unittest.TestCase"]
    BASE_2["absltest.TestCase"]
    BASE_3["parameterized.TestCase"]
    CHEX["variants.TestCase"]
    USER["MyTestClass"]
    
    BASE_1 --> BASE_2
    BASE_2 --> BASE_3
    BASE_3 --> CHEX
    CHEX --> USER
    
    DECORATOR_1["@variants decorator"]
    DECORATOR_2["@parameterized.parameters decorator"]
    
    DECORATOR_2 --> DECORATOR_1
    DECORATOR_1 --> USER
```

**Diagram: Test Class Inheritance and Decorator Order**

**Important:** The `@variants` decorator must be applied **before** `@parameterized.parameters` or `@parameterized.named_parameters`. The correct order is:
```python
@variants(...)
@parameterized.parameters(...)
def test_method(self, param):
    ...
```

**Sources:** [chex/_src/variants_test.py:327-358](), [chex/_src/variants_test.py:379-416](), [chex/_src/variants_test.py:360-377]()

For detailed documentation of the variants framework, see [Test Variants Framework](#6.2).

---

## Integration Patterns

The fake transformations and variants systems can be used together or independently:

### Pattern 1: Variants with Fake Transformations in Tests

```mermaid
graph TB
    TEST["Test Class inherits variants.TestCase"]
    SETUP["setUpModule() calls set_n_cpu_devices()"]
    METHOD["@all_variants test method"]
    VARIANT["self.variant() wraps function"]
    FAKE["with fake_pmap(): context (optional)"]
    
    TEST --> SETUP
    TEST --> METHOD
    METHOD --> VARIANT
    VARIANT --> FAKE
    
    SETUP -.->|"enables"| PMAP_VARIANT["WITH_PMAP variant"]
    METHOD -.->|"generates"| PMAP_VARIANT
    FAKE -.->|"used in"| PMAP_VARIANT
```

**Diagram: Combined Usage Pattern**

This pattern is common when you want comprehensive testing:
1. Use `set_n_cpu_devices()` in module setup to enable multi-device simulation
2. Use `@all_variants` to test all execution modes
3. Optionally use `fake_pmap()` within specific tests for additional debugging

**Sources:** [chex/_src/fake_test.py:33-35](), [chex/_src/variants_test.py:52-56](), [chex/_src/fake_test.py:184-199]()

### Pattern 2: Fake Transformations for Interactive Development

```mermaid
graph LR
    DEVELOP["Development Code<br/>(not in test)"]
    FAKE_CTX["with fake_pmap_and_jit():<br/>  run_model()"]
    DEBUG["Interactive Debugging<br/>Print statements work<br/>No compilation overhead"]
    
    DEVELOP --> FAKE_CTX
    FAKE_CTX --> DEBUG
```

Use fake transformations directly in scripts or notebooks to debug JAX code without writing formal tests.

**Sources:** [chex/_src/fake.py:222-253](), [chex/_src/fake.py:266-304]()

### Pattern 3: Conditional Faking

Both systems support conditional enabling:

```python
# Fake transformations
enable_fake = FLAGS.debug_mode
with fake_jit(enable_patching=enable_fake):
    ...

# Variants can be combined
@variants(with_jit=True)
@variants(without_jit=use_python_mode)
def test_method(self):
    ...
```

**Sources:** [chex/_src/fake.py:248-249](), [chex/_src/variants_test.py:519-524]()

---

## Multi-Device Testing Setup

Testing parallel JAX code (`jax.pmap`) typically requires multiple physical devices (GPUs/TPUs). Chex provides `set_n_cpu_devices()` to simulate multiple devices using CPU threads:

```mermaid
graph TB
    subgraph "Before set_n_cpu_devices()"
        SINGLE["Single CPU device<br/>jax.devices() → [CpuDevice(0)]"]
    end
    
    subgraph "After set_n_cpu_devices(n=4)"
        MULTI["Multiple CPU devices<br/>jax.devices() → [CpuDevice(0), CpuDevice(1),<br/>CpuDevice(2), CpuDevice(3)]"]
    end
    
    subgraph "Implementation"
        ENV["XLA_FLAGS=<br/>'--xla_force_host_platform_device_count=4'"]
        XLA_INIT["XLA Backend Initialization"]
        JAX_DEV["jax.devices()"]
    end
    
    SINGLE -.->|"set_n_cpu_devices(4)"| ENV
    ENV --> XLA_INIT
    XLA_INIT --> JAX_DEV
    JAX_DEV --> MULTI
    
    WARNING["⚠ Must be called BEFORE<br/>any JAX operation"]
    ENV -.-> WARNING
```

**Diagram: Multi-Device Setup Process**

### Critical Timing Constraint

`set_n_cpu_devices()` **must** be called before any JAX operation, including:
- `jax.devices()`
- Any JAX computation
- Importing modules that use JAX

The function modifies the `XLA_FLAGS` environment variable, which is only read during XLA backend initialization. After initialization, the function will raise a `RuntimeError`.

**Sources:** [chex/_src/fake.py:54-83](), [chex/_src/fake.py:72-77]()

### Common Setup Pattern

```python
# At module level in test file
from chex._src import fake

def setUpModule():
    """Called once before any tests in this module."""
    fake.set_n_cpu_devices()  # Uses FLAGS.chex_n_cpu_devices (default: 1)
```

This pattern ensures multi-device simulation is configured before test execution begins.

**Sources:** [chex/_src/fake_test.py:33-35](), [chex/_src/variants_test.py:52-56]()

### Flags for Device Configuration

```python
# Command-line flags
--chex_n_cpu_devices=4  # Number of CPU devices to create
--chex_assert_multiple_cpu_devices  # Fail if < 2 devices available
```

**Sources:** [chex/_src/fake.py:36-39]()

---

## Parallel Operations Compatibility

When using `fake_pmap()`, parallel operations behave differently than under true `pmap`:

```mermaid
graph TB
    subgraph "Real jax.pmap"
        PMAP_REAL["jax.pmap(fn, axis_name='i')"]
        PARALLEL_REAL["Parallel Operations<br/>jax.lax.psum(x, 'i')<br/>jax.lax.all_gather(x, 'i', axis_index_groups=[...])"]
        DEVICES_REAL["Executes on multiple<br/>physical devices"]
        
        PMAP_REAL --> PARALLEL_REAL
        PARALLEL_REAL --> DEVICES_REAL
    end
    
    subgraph "fake_pmap()"
        PMAP_FAKE["fake_pmap() → jax.vmap"]
        PARALLEL_FAKE["Parallel Operations<br/>jax.lax.psum(x, 'i') ✓<br/>jax.lax.all_gather(x, 'i', axis_index_groups=None) ✓"]
        DEVICES_FAKE["Executes on single device<br/>with vmap"]
        
        PMAP_FAKE --> PARALLEL_FAKE
        PARALLEL_FAKE --> DEVICES_FAKE
    end
    
    subgraph "Compatibility Option"
        IGNORE["fake_pmap(<br/>ignore_axis_index_groups=True)"]
        FORCED["axis_index_groups forced to None"]
        WARNING["⚠ Different results than pmap"]
        
        IGNORE --> FORCED
        FORCED --> WARNING
    end
```

**Diagram: Parallel Operations Under fake_pmap**

The `axis_index_groups` parameter is not supported in `vmap`. If your code uses this parameter, you must pass `ignore_axis_index_groups=True` to `fake_pmap()`, which patches parallel operations to ignore this parameter. **Note:** This produces different results than real `pmap`.

**Sources:** [chex/_src/fake.py:91-120](), [chex/_src/fake.py:295-299](), [chex/_src/fake.py:315-323]()

---

## Summary

Chex's testing infrastructure provides two complementary tools:

| System | Primary Use Case | Key Benefits |
|--------|------------------|--------------|
| **Fake Transformations** | Debugging and development | Remove compilation overhead, enable print debugging, test pmap on single device |
| **Test Variants** | Comprehensive test coverage | Automatically test code across execution modes, catch mode-specific bugs |

Both systems integrate seamlessly with standard Python testing frameworks (`unittest`, `absltest`, `parameterized`) and can be used independently or together depending on testing needs.

**Sources:** [chex/_src/fake.py:1-424](), [chex/__init__.py:77-101]()

---

