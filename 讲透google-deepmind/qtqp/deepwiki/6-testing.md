<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/qtqp · page 6 Testing · fetched 2026-10-26 -->

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/test_qtqp.py](tests/test_qtqp.py)

</details>



This document describes the test suite for the QTQP solver, explaining how tests validate correctness, the parameterization strategy, and KKT condition checking. The test suite ensures that the solver correctly handles feasible, infeasible, and unbounded quadratic programs across all linear solver backends.

For information about running tests locally and interpreting test output, see [Running Tests](#6.2). For details about the CI/CD testing pipeline, see [CI/CD Pipeline](#7.2).

## Test Suite Overview

The QTQP test suite is located in [tests/test_qtqp.py]() and consists of 266 lines of comprehensive validation code. The tests verify solver correctness by generating synthetic quadratic programs with known properties (feasible, infeasible, unbounded) and validating that solutions satisfy the Karush-Kuhn-Tucker (KKT) optimality conditions.

**Sources:** [tests/test_qtqp.py:1-266]()

## Test Data Generation

The test suite uses three generator functions to create synthetic quadratic programs with specific mathematical properties. Each generator constructs matrices and vectors that guarantee a particular outcome when solved.

### Generator Functions

```mermaid
graph LR
    subgraph "Test Data Generators"
        GenFeasible["_gen_feasible(m, n, z)<br/>[lines 38-51]"]
        GenInfeasible["_gen_infeasible(m, n, z)<br/>[lines 54-67]"]
        GenUnbounded["_gen_unbounded(m, n, z)<br/>[lines 70-87]"]
    end
    
    subgraph "Outputs"
        MatrixA["Matrix a: m×n<br/>sparse CSC"]
        VectorB["Vector b: m"]
        VectorC["Vector c: n"]
        MatrixP["Matrix p: n×n<br/>sparse CSC<br/>PSD"]
    end
    
    subgraph "Input Parameters"
        ParamM["m: constraints"]
        ParamN["n: variables"]
        ParamZ["z: equality count"]
        Seed["random_state: seed"]
    end
    
    ParamM --> GenFeasible
    ParamN --> GenFeasible
    ParamZ --> GenFeasible
    Seed --> GenFeasible
    
    ParamM --> GenInfeasible
    ParamN --> GenInfeasible
    ParamZ --> GenInfeasible
    Seed --> GenInfeasible
    
    ParamM --> GenUnbounded
    ParamN --> GenUnbounded
    ParamZ --> GenUnbounded
    Seed --> GenUnbounded
    
    GenFeasible --> MatrixA
    GenFeasible --> VectorB
    GenFeasible --> VectorC
    GenFeasible --> MatrixP
    
    GenInfeasible --> MatrixA
    GenInfeasible --> VectorB
    GenInfeasible --> VectorC
    GenInfeasible --> MatrixP
    
    GenUnbounded --> MatrixA
    GenUnbounded --> VectorB
    GenUnbounded --> VectorC
    GenUnbounded --> MatrixP
```

### Generator Implementations

| Generator | Purpose | Key Construction Steps | Output Guarantee |
|-----------|---------|------------------------|------------------|
| `_gen_feasible` | Create solvable QP | Generate random x, y, s; construct P as PSD; compute c = -A^T y; compute b = Ax + s | Solution exists with optimal x, y, s |
| `_gen_infeasible` | Create infeasible QP | Generate y; project A to satisfy A^T y = 0; set b = -b / (b^T y) | No feasible solution; certificate y with b^T y = -1 |
| `_gen_unbounded` | Create unbounded QP | Set smallest eigenvalue of P to 0; align A and c with null space | Objective unbounded below; certificate x with c^T x = -1 |

**Sources:** [tests/test_qtqp.py:38-87]()

## KKT Condition Validation

The test suite validates solver correctness by checking that solutions satisfy the Karush-Kuhn-Tucker optimality conditions. Three validation functions correspond to the three problem types.

### KKT Validation Functions

```mermaid
graph TB
    subgraph "Solution Object"
        SolX["solution.x: primal"]
        SolY["solution.y: dual"]
        SolS["solution.s: slack"]
        Status["solution.status"]
    end
    
    subgraph "Validation Functions"
        AssertSol["_assert_solution()<br/>[lines 90-117]<br/>SOLVED status"]
        AssertInf["_assert_infeasible()<br/>[lines 119-133]<br/>INFEASIBLE status"]
        AssertUnb["_assert_unbounded()<br/>[lines 135-154]<br/>UNBOUNDED status"]
    end
    
    subgraph "KKT Checks for SOLVED"
        PrimalRes["Primal residual:<br/>||Ax + s - b||_inf"]
        DualRes["Dual residual:<br/>||Px + A^T y + c||_inf"]
        DualGap["Duality gap:<br/>|c^T x + b^T y + x^T P x|"]
        NonNeg["Non-negativity:<br/>y[z:] >= 0<br/>s[z:] >= 0"]
    end
    
    subgraph "KKT Checks for INFEASIBLE"
        InfCert1["Certificate:<br/>b^T y = -1"]
        InfCert2["Projection:<br/>||A^T y||_inf ~ 0"]
        InfCert3["Non-negativity:<br/>y[z:] >= 0"]
    end
    
    subgraph "KKT Checks for UNBOUNDED"
        UnbCert1["Certificate:<br/>c^T x = -1"]
        UnbCert2["Null space:<br/>||Ax + s||_inf ~ 0"]
        UnbCert3["Null space:<br/>||Px||_inf ~ 0"]
        UnbCert4["Non-negativity:<br/>s[z:] >= 0"]
    end
    
    SolX --> AssertSol
    SolY --> AssertSol
    SolS --> AssertSol
    Status --> AssertSol
    
    SolX --> AssertInf
    SolY --> AssertInf
    SolS --> AssertInf
    Status --> AssertInf
    
    SolX --> AssertUnb
    SolY --> AssertUnb
    SolS --> AssertUnb
    Status --> AssertUnb
    
    AssertSol --> PrimalRes
    AssertSol --> DualRes
    AssertSol --> DualGap
    AssertSol --> NonNeg
    
    AssertInf --> InfCert1
    AssertInf --> InfCert2
    AssertInf --> InfCert3
    
    AssertUnb --> UnbCert1
    AssertUnb --> UnbCert2
    AssertUnb --> UnbCert3
    AssertUnb --> UnbCert4
```

### Validation Tolerances

Each validation function uses tolerance parameters to account for numerical precision:

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `atol` | 1e-7 (solved), 1e-8 (infeasible/unbounded) | Absolute tolerance for residuals |
| `rtol` | 1e-8 (solved), 1e-9 (infeasible/unbounded) | Relative tolerance scaled by problem norm |

The validation functions compute relative tolerance thresholds based on problem data norms to ensure scale-independent validation:

- **Primal relative RHS:** `max(||Ax||_inf, ||s||_inf, ||b||_inf)`
- **Dual relative RHS:** `max(||Px||_inf, ||A^T y||_inf, ||c||_inf)`

**Sources:** [tests/test_qtqp.py:90-154]()

## Parameterized Testing Strategy

The test suite uses pytest parameterization to create a comprehensive test matrix across multiple dimensions: equilibration settings, random seeds, and linear solver backends.

### Test Parameterization Matrix

```mermaid
graph TB
    subgraph "Pytest Decorators"
        DecEquil["@pytest.mark.parametrize<br/>'equilibrate'<br/>[True, False]"]
        DecSeed["@pytest.mark.parametrize<br/>'seed'<br/>np.arange(10)"]
        DecSolver["@pytest.mark.parametrize<br/>'linear_solver'<br/>_SOLVERS"]
    end
    
    subgraph "Test Functions"
        TestSolve["test_solve()<br/>[lines 156-168]"]
        TestUnbound["test_unbounded()<br/>[lines 170-182]"]
        TestInfeas["test_infeasible()<br/>[lines 184-196]"]
        TestWarm["test_solve_warm_start()<br/>[lines 198-218]"]
    end
    
    subgraph "Linear Solver Backends"
        SCIPY["LinearSolver.SCIPY<br/>Always available"]
        QDLDL["LinearSolver.QDLDL<br/>Always available"]
        CHOLMOD["LinearSolver.CHOLMOD<br/>Always available"]
        EIGEN["LinearSolver.EIGEN<br/>Always available"]
        PARDISO["LinearSolver.PARDISO<br/>Linux only"]
    end
    
    subgraph "Test Matrix Calculation"
        Calc["2 equilibrate settings<br/>× 10 seeds<br/>× 5-6 solvers<br/>= 100-120 tests<br/>per function"]
    end
    
    DecEquil --> TestSolve
    DecSeed --> TestSolve
    DecSolver --> TestSolve
    
    DecEquil --> TestUnbound
    DecSeed --> TestUnbound
    DecSolver --> TestUnbound
    
    DecEquil --> TestInfeas
    DecSeed --> TestInfeas
    DecSolver --> TestInfeas
    
    DecEquil --> TestWarm
    DecSeed --> TestWarm
    DecSolver --> TestWarm
    
    DecSolver --> SCIPY
    DecSolver --> QDLDL
    DecSolver --> CHOLMOD
    DecSolver --> EIGEN
    DecSolver --> PARDISO
    
    SCIPY --> Calc
    QDLDL --> Calc
    CHOLMOD --> Calc
    EIGEN --> Calc
    PARDISO --> Calc
```

### Solver Backend Selection

The `_SOLVERS` list is constructed at module import time with platform-specific logic:

```python
_SOLVERS = [
    qtqp.LinearSolver.SCIPY,
    qtqp.LinearSolver.QDLDL,
    qtqp.LinearSolver.CHOLMOD,
    qtqp.LinearSolver.EIGEN,
]

# Only run PARDISO on linux
if sys.platform.startswith("linux"):
    _SOLVERS.append(qtqp.LinearSolver.PARDISO)
```

The PARDISO backend is only included on Linux platforms because it requires Intel MKL, which has platform-specific requirements. The CUDSS GPU backend is excluded from the standard test suite (commented out) as it requires NVIDIA GPU hardware.

**Sources:** [tests/test_qtqp.py:24-36](), [tests/test_qtqp.py:156-218]()

## Core Test Functions

The test suite contains four primary test functions that validate different aspects of solver behavior.

### Test Function Overview

| Test Function | Lines | Purpose | Validations |
|---------------|-------|---------|-------------|
| `test_solve` | 159-168 | Verify correct solution of feasible QPs | Status SOLVED, KKT conditions satisfied |
| `test_unbounded` | 173-182 | Verify detection of unbounded QPs | Status UNBOUNDED, certificate valid, NaN dual |
| `test_infeasible` | 187-196 | Verify detection of infeasible QPs | Status INFEASIBLE, certificate valid, NaN primal/slack |
| `test_solve_warm_start` | 201-218 | Verify warm starting functionality | Solution converges in 0 iterations when warm started with optimal point |

### Test Execution Flow

```mermaid
sequenceDiagram
    participant Test as "Test Function"
    participant Gen as "Generator Function"
    participant QTQP as "qtqp.QTQP"
    participant Val as "Validation Function"
    
    Test->>Gen: Call _gen_*() with m=100, n=100, z=10
    Gen-->>Test: Return a, b, c, p matrices
    Test->>QTQP: QTQP(a, b, c, z, p)
    QTQP-->>Test: Create solver instance
    Test->>QTQP: solve(equilibrate, linear_solver)
    QTQP-->>Test: Return Solution object
    Test->>Val: Call _assert_*() with solution
    Val->>Val: Compute residuals and gaps
    Val->>Val: Check tolerances
    Val->>Val: Assert status matches expected
    Val-->>Test: Validation passes/fails
```

### Warm Start Validation

The `test_solve_warm_start` function has special logic to verify that providing optimal initial values allows the solver to converge immediately:

1. Solve a feasible QP to obtain optimal solution (x*, y*, s*)
2. Create a new QTQP instance with same problem data
3. Solve again with `x=x*`, `y=y*`, `s=s*` as initial values
4. Verify `solution.stats[-1]['iter'] == 0` (zero iterations required)

This validates that the solver correctly recognizes when it starts at an optimal point and terminates immediately.

**Sources:** [tests/test_qtqp.py:159-218]()

## Error Handling Tests

The test suite includes validation tests for error conditions to ensure the solver fails gracefully with appropriate error messages.

### Error Test Cases

```mermaid
graph LR
    subgraph "Error Test Functions"
        TestNoPos["test_raise_error_no_positive_constraints<br/>[lines 220-228]"]
        TestBadY["test_raise_error_invalid_initial_y<br/>[lines 230-239]"]
        TestBadS["test_raise_error_invalid_initial_s<br/>[lines 241-252]"]
        TestShape["test_raise_error_negative_invalid_shapes<br/>[lines 254-266]"]
    end
    
    subgraph "Validated Error Conditions"
        Err1["ValueError: z >= m<br/>No inequality constraints"]
        Err2["ValueError: y[z:] < 0<br/>Negative dual variables"]
        Err3["ValueError: len(y) != m<br/>Shape mismatch"]
        Err4["ValueError: s[z:] < 0<br/>Negative slack variables"]
        Err5["ValueError: s[:z] != 0<br/>Equality slack nonzero"]
        Err6["ValueError: len(s) != m<br/>Shape mismatch"]
        Err7["ValueError: len(b) != m<br/>RHS shape mismatch"]
        Err8["ValueError: len(c) != n<br/>Cost shape mismatch"]
        Err9["ValueError: p.shape != (n,n)<br/>Hessian shape mismatch"]
    end
    
    TestNoPos --> Err1
    TestBadY --> Err2
    TestBadY --> Err3
    TestBadS --> Err4
    TestBadS --> Err5
    TestBadS --> Err6
    TestShape --> Err7
    TestShape --> Err8
    TestShape --> Err9
```

### Error Validation Pattern

All error tests follow the same pattern using pytest's `pytest.raises` context manager:

```python
with pytest.raises(ValueError):
    _ = qtqp.QTQP(a=a, b=b, c=c, z=z, p=p).solve(invalid_parameter)
```

This ensures that:
1. The correct exception type (`ValueError`) is raised
2. The solver does not silently accept invalid inputs
3. Error messages are appropriate for the specific validation failure

**Sources:** [tests/test_qtqp.py:220-266]()

## Test Coverage Summary

The complete test suite provides comprehensive coverage across multiple dimensions:

### Coverage Dimensions

| Dimension | Coverage |
|-----------|----------|
| **Problem Types** | Feasible, infeasible, unbounded |
| **Equilibration** | With and without Ruiz scaling |
| **Random Seeds** | 10 different random problems per test |
| **Linear Solvers** | 5 backends (6 on Linux with PARDISO) |
| **Warm Starting** | Cold start and warm start scenarios |
| **Error Handling** | 9 distinct error conditions |

### Total Test Count

The parameterized tests generate the following test matrix:

- **`test_solve`**: 2 × 10 × 5 = 100 tests (120 on Linux)
- **`test_unbounded`**: 2 × 10 × 5 = 100 tests (120 on Linux)
- **`test_infeasible`**: 2 × 10 × 5 = 100 tests (120 on Linux)
- **`test_solve_warm_start`**: 2 × 10 × 5 = 100 tests (120 on Linux)
- **Error tests**: 4 non-parameterized tests with multiple assertions each

**Total:** ~400 tests on non-Linux platforms, ~480 tests on Linux platforms

### Problem Size Configuration

All parameterized tests use consistent problem dimensions:
- `m = 100` constraints
- `n = 100` variables
- `z = 10` equality constraints (90 inequality constraints)

This size is large enough to expose numerical issues while remaining fast enough for frequent CI execution.

**Sources:** [tests/test_qtqp.py:1-266]()

## Platform-Specific Testing

The test suite adapts to platform capabilities at runtime to ensure consistent behavior across operating systems.

### Platform Detection Logic

```mermaid
graph TD
    Import["Module Import Time"]
    CheckPlatform{"sys.platform<br/>startswith('linux')?"}
    AddPardiso["Append<br/>LinearSolver.PARDISO<br/>to _SOLVERS"]
    SkipPardiso["_SOLVERS has<br/>5 backends"]
    RunTests["Run Parameterized Tests"]
    
    Import --> CheckPlatform
    CheckPlatform -->|Yes| AddPardiso
    CheckPlatform -->|No| SkipPardiso
    AddPardiso --> RunTests
    SkipPardiso --> RunTests
```

### Backend Availability by Platform

| Linear Solver | Linux | macOS | Windows |
|--------------|-------|-------|---------|
| SCIPY | ✓ | ✓ | ✓ |
| QDLDL | ✓ | ✓ | ✓ |
| CHOLMOD | ✓ | ✓ | ✓ |
| EIGEN | ✓ | ✓ | ✓ |
| PARDISO | ✓ | ✗ | ✗ |
| CUDSS | Manual only (requires GPU) | Manual only | Manual only |

The platform-specific logic ensures:
- Tests always pass on all platforms
- Each platform tests all available backends
- PARDISO tests run only where the backend is supported
- No false negatives due to unavailable backends

**Sources:** [tests/test_qtqp.py:33-36]()

---

