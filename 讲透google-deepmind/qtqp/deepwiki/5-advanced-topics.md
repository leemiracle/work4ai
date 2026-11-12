<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/qtqp · page 5 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/qtqp/__init__.py](src/qtqp/__init__.py)
- [src/qtqp/direct.py](src/qtqp/direct.py)

</details>



This page covers advanced usage patterns, optimization techniques, and solver internals for the QTQP solver. Topics include numerical stability improvements, performance optimization, understanding convergence behavior, and interpreting non-standard termination states.

For basic usage and problem formulation, see [Getting Started](#2). For detailed API reference, see [API Reference](#4). For architecture and algorithm details, see [Architecture](#3).

## Scope and Organization

This page introduces five advanced topics that enable sophisticated usage of the QTQP solver:

| Topic | Purpose | Key Code Entity |
|-------|---------|-----------------|
| **Equilibration** | Improve numerical conditioning via Ruiz scaling | `QTQP._equilibrate()` |
| **Warm Starting** | Accelerate convergence for sequences of related problems | `QTQP.solve(x=..., y=..., s=...)` |
| **Iterative Refinement** | Achieve high accuracy despite ill-conditioned systems | `DirectKktSolver.solve()` |
| **Infeasibility Detection** | Understand how solver certifies infeasible/unbounded problems | `QTQP._check_termination()` |
| **Performance Tuning** | Select optimal solvers and parameters for specific problems | `LinearSolver` enum |

Each subsection (5.1-5.5) provides detailed coverage of one topic.

## Advanced Features Integration

The following diagram shows how advanced features integrate into the main solver workflow:

```mermaid
flowchart TD
    Input["Problem Input<br/>a, b, c, p, z"]
    
    Equil{{"equilibrate=True?"}}
    DoEquil["_equilibrate()<br/>Ruiz scaling<br/>Returns: d, e scale factors"]
    SkipEquil["Use original<br/>a, p, b, c"]
    
    WarmStart{{"x, y, s provided?"}}
    UseWarm["Use provided<br/>initial iterates"]
    ColdStart["Initialize:<br/>x=0, y[z:]=1, s[z:]=1"]
    
    SetupKKT["DirectKktSolver.__init__()<br/>Build KKT scaffold"]
    
    MainLoop["Main Iteration Loop<br/>it in range(max_iter)"]
    
    UpdateKKT["DirectKktSolver.update()<br/>mu, s, y parameters"]
    
    IterRefine["DirectKktSolver.solve()<br/>Iterative refinement<br/>up to max_iterative_refinement_steps"]
    
    CheckTerm["_check_termination()<br/>Check SOLVED, INFEASIBLE,<br/>UNBOUNDED, FAILED"]
    
    Done{{"Converged?"}}
    
    UnEquil["_unequilibrate_iterates()<br/>Scale back x, y, s"]
    
    Return["Return Solution<br/>status, x/tau, y/tau, s/tau"]
    
    Input --> Equil
    Equil -->|Yes| DoEquil
    Equil -->|No| SkipEquil
    DoEquil --> WarmStart
    SkipEquil --> WarmStart
    
    WarmStart -->|Yes| UseWarm
    WarmStart -->|No| ColdStart
    UseWarm --> SetupKKT
    ColdStart --> SetupKKT
    
    SetupKKT --> MainLoop
    MainLoop --> UpdateKKT
    UpdateKKT --> IterRefine
    IterRefine --> CheckTerm
    CheckTerm --> Done
    Done -->|No| MainLoop
    Done -->|Yes| UnEquil
    UnEquil --> Return
```

**Sources:** [src/qtqp/__init__.py:145-373](), [src/qtqp/__init__.py:375-412](), [src/qtqp/__init__.py:414-418](), [src/qtqp/direct.py:204-383]()

## Code Entity Mapping

The following diagram maps advanced feature names to their implementing code entities:

```mermaid
graph TB
    subgraph "User-Facing API"
        SolveMethod["QTQP.solve()"]
        EquilParam["equilibrate: bool"]
        WarmParams["x, y, s: ndarray | None"]
        RefinementParams["max_iterative_refinement_steps: int<br/>linear_solver_atol: float<br/>linear_solver_rtol: float"]
        RegParam["min_static_regularization: float"]
    end
    
    subgraph "Equilibration Implementation"
        EquilMethod["QTQP._equilibrate()"]
        EquilIter["QTQP._equilibrate_iterates()"]
        UnEquilIter["QTQP._unequilibrate_iterates()"]
        ScaleFactors["self.d: ndarray<br/>self.e: ndarray"]
    end
    
    subgraph "Warm Start Implementation"
        InitCheck["Lines 234-238:<br/>Validate y[z:] >= 0<br/>Validate s[z:] >= 0<br/>Validate s[:z] == 0"]
        Normalize["QTQP._normalize()"]
    end
    
    subgraph "Iterative Refinement Implementation"
        KKTSolve["DirectKktSolver.solve()"]
        RefineLoop["Lines 334-366:<br/>while residual_norm > tolerance"]
        CorrectionStep["correction = solver.solve(residual)<br/>new_sol = sol + correction"]
        StallCheck["Lines 354-362:<br/>if new_residual_norm >= residual_norm"]
    end
    
    subgraph "KKT System Regularization"
        KKTUpdate["DirectKktSolver.update()"]
        RegDiags["Lines 280-285:<br/>reg_diags = max(true_diags, min_static_regularization)"]
    end
    
    subgraph "Termination Check"
        CheckTerm["QTQP._check_termination()"]
        SolvedCheck["Lines 579-584:<br/>gap < atol + rtol * costs<br/>pres < atol + rtol * prelrhs<br/>dres < atol + rtol * drelrhs"]
        UnboundedCheck["Lines 585-587:<br/>ctx < -EPS and dinfeas < tol"]
        InfeasCheck["Lines 589-592:<br/>bty < -EPS and pinfeas < tol"]
    end
    
    SolveMethod --> EquilParam
    SolveMethod --> WarmParams
    SolveMethod --> RefinementParams
    SolveMethod --> RegParam
    
    EquilParam --> EquilMethod
    EquilMethod --> ScaleFactors
    ScaleFactors --> EquilIter
    ScaleFactors --> UnEquilIter
    
    WarmParams --> InitCheck
    InitCheck --> Normalize
    
    RefinementParams --> KKTSolve
    KKTSolve --> RefineLoop
    RefineLoop --> CorrectionStep
    CorrectionStep --> StallCheck
    
    RegParam --> KKTUpdate
    KKTUpdate --> RegDiags
    
    SolveMethod --> CheckTerm
    CheckTerm --> SolvedCheck
    CheckTerm --> UnboundedCheck
    CheckTerm --> InfeasCheck
```

**Sources:** [src/qtqp/__init__.py:145-164](), [src/qtqp/__init__.py:375-418](), [src/qtqp/__init__.py:234-238](), [src/qtqp/__init__.py:523-527](), [src/qtqp/direct.py:262-292](), [src/qtqp/direct.py:294-382](), [src/qtqp/__init__.py:535-622]()

## Numerical Stability Architecture

The solver employs a multi-layered approach to numerical stability:

```mermaid
flowchart LR
    subgraph "Layer 1: Preprocessing"
        Equil["Ruiz Equilibration<br/>_equilibrate()"]
    end
    
    subgraph "Layer 2: KKT Regularization"
        StaticReg["Static Regularization<br/>min_static_regularization"]
        DynamicReg["Dynamic Regularization<br/>mu * I on diagonal"]
    end
    
    subgraph "Layer 3: Iterative Refinement"
        TrueDiag["True Diagonals<br/>for residual calculation"]
        RegDiag["Regularized Diagonals<br/>for factorization"]
        RefineLoop["Iterative correction<br/>until converged or stalled"]
    end
    
    subgraph "Layer 4: Interior Point Safeguards"
        StepScale["step_size_scale<br/>keeps iterates interior"]
        MinValues["Lines 342-344:<br/>y[z:] = max(y[z:], 1e-30)<br/>s[z:] = max(s[z:], 1e-30)<br/>tau = max(tau, 1e-30)"]
    end
    
    Equil --> StaticReg
    Equil --> DynamicReg
    StaticReg --> RegDiag
    DynamicReg --> RegDiag
    RegDiag --> TrueDiag
    TrueDiag --> RefineLoop
    RefineLoop --> StepScale
    StepScale --> MinValues
```

**Sources:** [src/qtqp/__init__.py:375-412](), [src/qtqp/direct.py:262-292](), [src/qtqp/direct.py:294-382](), [src/qtqp/__init__.py:332-344]()

## Homogeneous Self-Dual Embedding

The solver uses homogeneous self-dual embedding to detect infeasibility and unboundedness. The embedding introduces a tau variable that allows the algorithm to distinguish between optimal solutions, certificates of infeasibility, and certificates of unboundedness:

```mermaid
graph TB
    subgraph "Homogeneous Variables"
        Tau["tau: homogeneous variable<br/>Initialized to 1.0<br/>Line 232"]
        X["x: primal variables"]
        Y["y: dual variables"]
        S["s: slack variables"]
    end
    
    subgraph "Normalization"
        NormFunc["_normalize(x, y, tau, s)<br/>Lines 523-527"]
        NormScale["scale = sqrt(m - z + 1) / vec_norm<br/>where vec_norm = sqrt(x@x + y@y + tau@tau)"]
    end
    
    subgraph "Complementarity Measure"
        Mu["mu = (y @ s) / max(EPS, x@x + y@y + tau@tau)<br/>Line 272"]
    end
    
    subgraph "Solution Recovery"
        TauCheck{{"tau close to 0?"}}
        OptSol["SOLVED:<br/>return x/tau, y/tau, s/tau<br/>Lines 357-358"]
        PInfeas["INFEASIBLE:<br/>y is certificate, x=NaN, s=NaN<br/>Lines 359-363"]
        DInfeas["UNBOUNDED:<br/>x, s are certificate, y=NaN<br/>Lines 364-368"]
    end
    
    subgraph "Termination Conditions"
        CheckCtx["ctx = c @ x<br/>Line 545"]
        CheckBty["bty = b @ y<br/>Line 546"]
        CtxNeg{{"ctx < -EPS?"}}
        BtyNeg{{"bty < -EPS?"}}
        DInfeasLow{{"dinfeas < tol?"}}
        PInfeasLow{{"pinfeas < tol?"}}
    end
    
    Tau --> NormFunc
    X --> NormFunc
    Y --> NormFunc
    S --> NormFunc
    NormFunc --> NormScale
    
    X --> Mu
    Y --> Mu
    Tau --> Mu
    S --> Mu
    
    Mu --> TauCheck
    TauCheck -->|"tau > threshold"| OptSol
    TauCheck -->|"tau ≈ 0"| CheckCtx
    TauCheck -->|"tau ≈ 0"| CheckBty
    
    CheckCtx --> CtxNeg
    CtxNeg -->|Yes| DInfeasLow
    DInfeasLow -->|Yes| DInfeas
    
    CheckBty --> BtyNeg
    BtyNeg -->|Yes| PInfeasLow
    PInfeasLow -->|Yes| PInfeas
```

**Sources:** [src/qtqp/__init__.py:230-238](), [src/qtqp/__init__.py:269-273](), [src/qtqp/__init__.py:523-527](), [src/qtqp/__init__.py:535-622]()

## Predictor-Corrector Step Computation

The solver implements Mehrotra's predictor-corrector algorithm. Understanding this flow is essential for tuning convergence behavior:

```mermaid
flowchart TD
    subgraph "Per-Iteration Setup"
        UpdateMu["Compute mu = (y @ s) / vec_norm<br/>Line 272"]
        UpdateKKT["DirectKktSolver.update(mu, s, y)<br/>Factorize KKT matrix"]
        SolveQ["Solve KKT @ kkt_inv_q = q<br/>Reused for both steps<br/>Lines 277-279"]
    end
    
    subgraph "Predictor (Affine) Step"
        PredictorCall["_newton_step(mu_target=0.0)<br/>Lines 282-293"]
        PredictorSolve["Solve KKT system<br/>with mu_target=0"]
        ComputeAlphaP["alpha_p = _compute_step_size()<br/>Line 301"]
        ComputeSigma["sigma = _compute_sigma()<br/>Mehrotra heuristic<br/>Lines 302-304"]
    end
    
    subgraph "Corrector Step"
        ConeCor["cone_correction = -d_s_p * d_y_p / y<br/>Mehrotra nonlinearity term<br/>Line 308"]
        CorrectorCall["_newton_step(mu_target=sigma*mu)<br/>Lines 310-319"]
        CorrectorSolve["Solve KKT system<br/>with centering and correction"]
    end
    
    subgraph "Update Iterates"
        ComputeStep["d_x = x_c - x<br/>d_y = y_c - y<br/>d_tau = tau_c - tau<br/>d_s computed from y_c<br/>Lines 323-329"]
        ComputeAlpha["alpha = _compute_step_size(y, s, d_y, d_s)<br/>Line 331"]
        ApplyStep["x += step_size_scale * alpha * d_x<br/>y += step_size_scale * alpha * d_y<br/>tau += step_size_scale * alpha * d_tau<br/>s += step_size_scale * alpha * d_s<br/>Lines 332-338"]
        ClipPos["Clip y[z:], s[z:], tau to >= 1e-30<br/>Lines 342-344"]
    end
    
    UpdateMu --> UpdateKKT
    UpdateKKT --> SolveQ
    SolveQ --> PredictorCall
    PredictorCall --> PredictorSolve
    PredictorSolve --> ComputeAlphaP
    ComputeAlphaP --> ComputeSigma
    ComputeSigma --> ConeCor
    ConeCor --> CorrectorCall
    CorrectorCall --> CorrectorSolve
    CorrectorSolve --> ComputeStep
    ComputeStep --> ComputeAlpha
    ComputeAlpha --> ApplyStep
    ApplyStep --> ClipPos
```

**Sources:** [src/qtqp/__init__.py:269-344]()

## Iterative Refinement Process

The `DirectKktSolver.solve()` method implements iterative refinement to improve solution accuracy:

```mermaid
flowchart TD
    Start["DirectKktSolver.solve(rhs, warm_start)"]
    
    Prep["Prepare:<br/>sol = warm_start.copy()<br/>rhs_norm = ||rhs||_inf<br/>tolerance = atol + rtol * rhs_norm<br/>Lines 321-323"]
    
    InitRes["Initial residual:<br/>residual = rhs - kkt @ sol<br/>residual_norm = ||residual||_inf<br/>Lines 326-327"]
    
    Check{{"residual_norm<br/><= tolerance?"}}
    
    MaxCheck{{"solves ><br/>max_steps?"}}
    
    LinearSolve["correction = solver.solve(residual)<br/>Line 348"]
    
    Update["new_sol = sol + correction<br/>new_residual = rhs - kkt @ new_sol<br/>new_residual_norm = ||new_residual||_inf<br/>Lines 349-351"]
    
    StallCheck{{"new_residual_norm<br/>>= residual_norm?"}}
    
    Accept["sol = new_sol<br/>residual = new_residual<br/>residual_norm = new_residual_norm<br/>solves += 1<br/>Lines 364-366"]
    
    ReturnStalled["status = 'stalled'<br/>return sol, stats<br/>Lines 361-362"]
    
    ReturnNonConv["status = 'non-converged'<br/>return sol, stats<br/>Lines 329, 336-343"]
    
    ReturnConv["status = 'converged'<br/>return sol, stats<br/>Line 369"]
    
    NanCheck{{"any(isnan(sol))?"}}
    
    RaiseError["raise ValueError:<br/>'Linear solver returned NaNs'<br/>Line 372"]
    
    Start --> Prep
    Prep --> InitRes
    InitRes --> Check
    Check -->|Yes| NanCheck
    Check -->|No| MaxCheck
    MaxCheck -->|Yes| ReturnNonConv
    MaxCheck -->|No| LinearSolve
    LinearSolve --> Update
    Update --> StallCheck
    StallCheck -->|Yes, stalled| ReturnStalled
    StallCheck -->|No, improving| Accept
    Accept --> Check
    NanCheck -->|Yes| RaiseError
    NanCheck -->|No| ReturnConv
```

**Sources:** [src/qtqp/direct.py:294-382]()

## KKT Matrix Update Strategy

The `DirectKktSolver.update()` method uses an optimization to avoid copying the full KKT matrix:

```mermaid
sequenceDiagram
    participant Caller as QTQP.solve()
    participant KKT as DirectKktSolver
    participant Solver as LinearSolver
    
    Note over Caller: Per iteration
    Caller->>KKT: update(mu, s, y)
    
    Note over KKT: Compute diagonal blocks
    KKT->>KKT: h = [0, ..., 0, s[z:]/y[z:]]<br/>Line 276
    KKT->>KKT: true_diags = [p_diags, h] + mu<br/>Line 280
    KKT->>KKT: reg_diags = max(true_diags, min_reg)<br/>Line 282
    KKT->>KKT: Flip signs: diags[n:] *= -1<br/>Lines 284-285
    
    Note over KKT: Temporary injection
    KKT->>KKT: kkt.data[kkt_nan_idxs] = reg_diags<br/>Line 288
    KKT->>Solver: solver.update(kkt)
    Note over Solver: Factorize with<br/>regularized diagonals
    
    Note over KKT: Restore for residuals
    KKT->>KKT: kkt.data[kkt_nan_idxs] = true_diags<br/>Line 292
    
    KKT-->>Caller: Ready for solve()
    
    Note over Caller: Later in iteration
    Caller->>KKT: solve(rhs, warm_start)
    Note over KKT: Uses true_diags<br/>for accurate residual<br/>calculation
```

This strategy enables accurate residual computation (using true diagonals) while maintaining numerical stability (factorizing with regularized diagonals).

**Sources:** [src/qtqp/direct.py:262-292]()

## Performance Characteristics by Linear Solver

Different linear solvers have different performance characteristics:

| Solver | Backend | Format | Factorization Type | Best For | Limitations |
|--------|---------|--------|-------------------|----------|-------------|
| `SCIPY` | `scipy.sparse.linalg` | CSC | LU-based | Default, portable | Slower than specialized solvers |
| `PARDISO` | Intel MKL via pydiso | CSR | LDL^T | Intel CPUs, large dense KKT | Ubuntu only, requires Intel CPU |
| `QDLDL` | qdldl library | CSC | LDL^T quasi-definite | Sparse KKT systems | May be slower than CHOLMOD |
| `CHOLMOD` | SuiteSparse via scikit-sparse | CSC | Simplicial LDL^T | Sparse KKT, good sparsity | Requires CHOLMOD installation |
| `EIGEN` | Eigen via eigenpy | CSC | Simplicial LDL^T | C++ integration, moderate size | Requires eigenpy compilation |
| `CUDSS` | NVIDIA cuDSS | CSR | GPU-accelerated | Very large problems, GPU available | Requires NVIDIA GPU, CUDA toolkit |

**Sources:** [src/qtqp/__init__.py:36-44](), [src/qtqp/direct.py:40-202]()

## Solver Selection Code Pattern

```python
# Example: Selecting different linear solvers
from qtqp import QTQP, LinearSolver

# Default (portable but slower)
solver = QTQP(a=a, b=b, c=c, z=z, p=p)
solution = solver.solve(linear_solver=LinearSolver.SCIPY)

# Intel CPU optimization
solution = solver.solve(linear_solver=LinearSolver.PARDISO)

# GPU acceleration (requires NVIDIA GPU)
solution = solver.solve(linear_solver=LinearSolver.CUDSS)

# Sparse system optimization
solution = solver.solve(linear_solver=LinearSolver.CHOLMOD)
```

**Sources:** [src/qtqp/__init__.py:36-44](), [src/qtqp/__init__.py:158-164]()

## Tuning Parameters for Convergence

Key parameters that affect convergence behavior:

| Parameter | Default | Effect | Increase When | Decrease When |
|-----------|---------|--------|---------------|---------------|
| `atol` | 1e-7 | Absolute tolerance for optimality | Want faster (looser) convergence | Need higher precision |
| `rtol` | 1e-8 | Relative tolerance for optimality | Want faster convergence | Need higher precision |
| `max_iter` | 100 | Maximum iterations | Problem doesn't converge | Want early termination |
| `step_size_scale` | 0.99 | Fraction of maximum step taken | Getting stuck at boundary | Taking too cautious steps |
| `min_static_regularization` | 1e-7 | KKT diagonal regularization | Factorization fails | Want exact KKT system |
| `max_iterative_refinement_steps` | 50 | Max refinement iterations per KKT solve | Linear solves aren't accurate | Want faster iterations |
| `linear_solver_atol` | 1e-12 | Absolute tolerance for refinement | Want faster KKT solves | Need exact KKT solves |
| `linear_solver_rtol` | 1e-12 | Relative tolerance for refinement | Want faster KKT solves | Need exact KKT solves |

**Sources:** [src/qtqp/__init__.py:145-164]()

## Equilibration Benefits

Equilibration transforms the problem to have better-conditioned matrices:

```mermaid
flowchart LR
    subgraph "Original Problem"
        OrigA["a: constraint matrix<br/>Potentially ill-conditioned"]
        OrigP["p: cost matrix<br/>Potentially ill-conditioned"]
        OrigBC["b, c: vectors"]
    end
    
    subgraph "Ruiz Equilibration"
        ComputeD["Compute row scaling d[i]<br/>d[i] = 1/sqrt(||a[i,:]||_inf)<br/>Lines 385-387"]
        ComputeE["Compute column scaling e[j]<br/>e[j] = 1/sqrt(max(||a[:,j]||_inf, ||p[:,j]||_inf))<br/>Lines 390-394"]
        ApplyScale["Apply scaling:<br/>a_new = diag(d) @ a @ diag(e)<br/>p_new = diag(e) @ p @ diag(e)<br/>Lines 397-400"]
        Iterate["Iterate 10 times<br/>Line 382"]
    end
    
    subgraph "Equilibrated Problem"
        EqA["a_new: row/column norms ≈ 1"]
        EqP["p_new: column norms ≈ 1"]
        EqBC["b_new = b * d<br/>c_new = c * e<br/>Line 412"]
    end
    
    subgraph "During Solve"
        EqIter["_equilibrate_iterates():<br/>x_eq = x / e<br/>y_eq = y / d<br/>s_eq = s * d<br/>Lines 417-418"]
        UnEqIter["_unequilibrate_iterates():<br/>x = x_eq * e<br/>y = y_eq * d<br/>s = s_eq / d<br/>Lines 414-415"]
    end
    
    OrigA --> ComputeD
    OrigA --> ComputeE
    OrigP --> ComputeE
    ComputeD --> ApplyScale
    ComputeE --> ApplyScale
    ApplyScale --> Iterate
    Iterate --> EqA
    Iterate --> EqP
    OrigBC --> EqBC
    
    EqA --> EqIter
    EqP --> EqIter
    EqBC --> EqIter
    EqIter --> UnEqIter
```

Equilibration typically reduces condition numbers by orders of magnitude, enabling more accurate solutions and faster convergence.

**Sources:** [src/qtqp/__init__.py:375-418]()

## Warm Start Usage Pattern

Warm starting provides initial values for `x`, `y`, `s` to accelerate convergence:

```python
# First solve: cold start
solver = QTQP(a=a, b=b1, c=c, z=z, p=p)
solution1 = solver.solve()

# Subsequent solve with slightly different b
# Use previous solution as warm start
solver2 = QTQP(a=a, b=b2, c=c, z=z, p=p)
solution2 = solver2.solve(
    x=solution1.x,  # Previous primal solution
    y=solution1.y,  # Previous dual solution  
    s=solution1.s   # Previous slack solution
)
```

Requirements for warm start values:
- `y[z:] >= 0` (dual variables for inequality constraints are non-negative)
- `s[z:] >= 0` (slack variables for inequality constraints are non-negative)  
- `s[:z] == 0` (slack variables for equality constraints are zero)

**Sources:** [src/qtqp/__init__.py:161-163](), [src/qtqp/__init__.py:210-238]()

## Infeasibility Certificate Structure

When the solver detects infeasibility or unboundedness, it returns certificates:

```mermaid
graph TB
    subgraph "INFEASIBLE: Primal Infeasible / Dual Unbounded"
        InfeasCond["Condition: bty < -EPS<br/>pinfeas < tolerance<br/>Lines 589-592"]
        InfeasCert["Certificate: y<br/>scaled by 1/abs(b@y)<br/>Line 363"]
        InfeasProps["Properties:<br/>- A^T @ y = 0<br/>- b^T @ y < 0<br/>- y[z:] >= 0"]
        InfeasInterpret["Interpretation:<br/>Direction y proves<br/>dual is unbounded"]
        InfeasReturn["Return:<br/>x = NaN<br/>y = certificate<br/>s = NaN<br/>Lines 361-363"]
    end
    
    subgraph "UNBOUNDED: Dual Infeasible / Primal Unbounded"
        UnboundCond["Condition: ctx < -EPS<br/>dinfeas < tolerance<br/>Lines 585-587"]
        UnboundCert["Certificate: x, s<br/>scaled by 1/abs(c@x)<br/>Lines 367-368"]
        UnboundProps["Properties:<br/>- A @ x + s = 0<br/>- c^T @ x < 0<br/>- P @ x = 0<br/>- s[z:] >= 0"]
        UnboundInterpret["Interpretation:<br/>Direction x, s proves<br/>primal is unbounded"]
        UnboundReturn["Return:<br/>x = certificate<br/>y = NaN<br/>s = certificate<br/>Lines 365-368"]
    end
    
    InfeasCond --> InfeasCert
    InfeasCert --> InfeasProps
    InfeasProps --> InfeasInterpret
    InfeasInterpret --> InfeasReturn
    
    UnboundCond --> UnboundCert
    UnboundCert --> UnboundProps
    UnboundProps --> UnboundInterpret
    UnboundInterpret --> UnboundReturn
```

**Sources:** [src/qtqp/__init__.py:535-622](), [src/qtqp/__init__.py:359-368]()

## Termination Criteria Details

The `_check_termination()` method computes multiple residuals and checks conditions:

| Status | Condition | Residuals Checked |
|--------|-----------|-------------------|
| `SOLVED` | All KKT conditions satisfied within tolerance | `pres`: primal residual<br/>`dres`: dual residual<br/>`gap`: duality gap |
| `INFEASIBLE` | Certificate of primal infeasibility found | `pinfeas`: `‖A^T y‖_∞ / |b^T y|` |
| `UNBOUNDED` | Certificate of dual infeasibility found | `dinfeas_a`: `‖A x + s‖_∞ / |c^T x|`<br/>`dinfeas_p`: `‖P x‖_∞ / |c^T x|` |
| `UNFINISHED` | None of the above | Continue iterating |

Computed values (with equilibration disabled):
- `pcost = (c^T x + 0.5 x^T P x / tau) / tau` (line 549)
- `dcost = (-b^T y - 0.5 x^T P x / tau) / tau` (line 550)
- `pres = ‖(A x + s) / tau - b‖_∞` (line 553)
- `dres = ‖(P x + A^T y) / tau + c‖_∞` (line 554)
- `gap = |(c^T x + b^T y + x^T P x / tau) / tau|` (line 555)

**Sources:** [src/qtqp/__init__.py:535-622]()

## Iteration Statistics

Each iteration produces a statistics dictionary with the following keys:

| Key | Description | Usage |
|-----|-------------|-------|
| `iter` | Iteration number | Track progress |
| `pcost`, `dcost` | Primal and dual objective values | Monitor convergence |
| `pres`, `dres` | Primal and dual residuals | Check feasibility |
| `gap` | Duality gap | Check optimality |
| `complementarity` | `|(y @ s) / tau^2|` | Check complementarity |
| `pinfeas`, `dinfeas` | Infeasibility measures | Detect infeasibility/unboundedness |
| `mu` | Barrier parameter | Track centrality |
| `sigma` | Centering parameter | Monitor predictor-corrector behavior |
| `alpha` | Step size taken | Understand step behavior |
| `tau` | Homogeneous variable | Track embedding behavior |
| `q_lin_sys_stats` | Linear solve stats for q direction | Debug KKT solver |
| `predictor_lin_sys_stats` | Predictor step solve stats | Debug predictor step |
| `corrector_lin_sys_stats` | Corrector step solve stats | Debug corrector step |
| `time` | Elapsed time in seconds | Profile performance |

**Sources:** [src/qtqp/__init__.py:596-621]()

---

