<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuopt · extra page Dual Simplex Algorithm · fetched 2026-10-26 -->

# Dual Simplex Algorithm

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cpp/src/barrier/translate_soc.hpp](cpp/src/barrier/translate_soc.hpp)
- [cpp/src/dual_simplex/basis_solves.cpp](cpp/src/dual_simplex/basis_solves.cpp)
- [cpp/src/dual_simplex/basis_solves.hpp](cpp/src/dual_simplex/basis_solves.hpp)
- [cpp/src/dual_simplex/basis_updates.cpp](cpp/src/dual_simplex/basis_updates.cpp)
- [cpp/src/dual_simplex/basis_updates.hpp](cpp/src/dual_simplex/basis_updates.hpp)
- [cpp/src/dual_simplex/crossover.cpp](cpp/src/dual_simplex/crossover.cpp)
- [cpp/src/dual_simplex/folding.cpp](cpp/src/dual_simplex/folding.cpp)
- [cpp/src/dual_simplex/phase2.cpp](cpp/src/dual_simplex/phase2.cpp)
- [cpp/src/dual_simplex/phase2.hpp](cpp/src/dual_simplex/phase2.hpp)
- [cpp/src/dual_simplex/presolve.cpp](cpp/src/dual_simplex/presolve.cpp)
- [cpp/src/dual_simplex/presolve.hpp](cpp/src/dual_simplex/presolve.hpp)
- [cpp/src/dual_simplex/primal.cpp](cpp/src/dual_simplex/primal.cpp)
- [cpp/src/dual_simplex/right_looking_lu.cpp](cpp/src/dual_simplex/right_looking_lu.cpp)
- [cpp/src/dual_simplex/right_looking_lu.hpp](cpp/src/dual_simplex/right_looking_lu.hpp)
- [cpp/src/dual_simplex/solve.cpp](cpp/src/dual_simplex/solve.cpp)
- [cpp/src/dual_simplex/solve.hpp](cpp/src/dual_simplex/solve.hpp)
- [cpp/src/dual_simplex/user_problem.hpp](cpp/src/dual_simplex/user_problem.hpp)
- [cpp/src/linear_algebra/vector_math.hpp](cpp/src/linear_algebra/vector_math.hpp)
- [cpp/tests/dual_simplex/unit_tests/right_looking_ldlt.cpp](cpp/tests/dual_simplex/unit_tests/right_looking_ldlt.cpp)
- [cpp/tests/linear_programming/pdlp_test.cu](cpp/tests/linear_programming/pdlp_test.cu)
- [cpp/tests/socp/general_quadratic_test.cu](cpp/tests/socp/general_quadratic_test.cu)

</details>



## Purpose and Scope

This document describes the CPU-based **revised dual simplex** LP solver in cuOpt, implemented in the `cpp/src/dual_simplex/` directory. The dual simplex method is one of three LP solving approaches available in cuOpt, alongside PDLP (GPU first-order method, see page 2.1.1) and the Barrier method (GPU interior point, see page 2.1.3).

The term "revised" refers to maintaining an LU factorization of the basis matrix $B$ rather than explicitly storing $B^{-1}$. This representation enables efficient basis updates via rank-one modifications and reduces memory requirements. The `basis_update_mpf_t` class manages the middle product form LU factorization with Forrest-Tomlin updates [cpp/src/dual_simplex/basis_updates.hpp:169-184]().

The core implementation centers on the `dual_phase2()` function which performs the main simplex iteration. This method maintains dual feasibility ($A'y + z = c$ with appropriate signs on $z$) while iteratively driving primal infeasibility to zero, producing exact basic solutions at optimality. These vertex solutions are essential for warm-starting the MIP branch-and-bound solver where small bound changes from branching decisions typically preserve dual feasibility, enabling fast reoptimization at each node [cpp/src/dual_simplex/phase2.cpp:1-50]().

**Key characteristics:**
- CPU-based with OpenMP parallelization for matrix operations [cpp/src/dual_simplex/phase2.cpp:1-50]().
- Exact basic solutions (vertices of feasible region).
- Steepest edge pricing for selecting leaving variables [cpp/src/dual_simplex/phase2.cpp:879-913]().
- Harris ratio test with bound flipping for selecting entering variables [cpp/src/dual_simplex/phase2.cpp:1030-1135]().
- Refactorization every 100 iterations (default) to maintain numerical stability [cpp/src/dual_simplex/solve.cpp:8-43]().

Sources: [cpp/src/dual_simplex/phase2.cpp:1-50](), [cpp/src/dual_simplex/basis_updates.hpp:169-184](), [cpp/src/dual_simplex/solve.cpp:8-43]()

---

## Algorithm Overview

The revised dual simplex method solves linear programs of the form:

```
minimize    c'x
subject to  Ax = b
            l ≤ x ≤ u
```

by maintaining a basis matrix $B = A(:, basic\_list)$ and its LU factorization $P \cdot B = L \cdot U$, where:
- **L** is lower triangular with unit diagonal.
- **U** is upper triangular.
- **P** is a row permutation matrix [cpp/src/dual_simplex/basis_updates.cpp:39-58]().

Variables are partitioned into:
- **Basic variables** ($m$ variables, stored in `basic_list[m]`): Can violate bounds, form basis $B$ [cpp/src/dual_simplex/basis_solves.cpp:33-59]().
- **Nonbasic variables** ($n-m$ variables, stored in `nonbasic_list[n-m]`): Fixed at bounds (lower, upper, or free at 0) [cpp/src/dual_simplex/basis_solves.cpp:46-52]().

The algorithm maintains dual feasibility ($A'y + z = c$, with $z_j \ge 0$ for variables at lower bounds, $z_j \le 0$ for variables at upper bounds, $z_j = 0$ for basic variables) while iteratively reducing primal infeasibility in the basic variables.

**Diagram: Phase 2 Iteration Flow with Code Entities**
```mermaid
graph TB
    subgraph "IterationState"
        State[""vstatus[n]<br/>basic_list[m]<br/>nonbasic_list[n-m]<br/>x[n], y[m], z[n]<br/>dy_steepest_edge[m]""]
    end
    
    subgraph "PricingStage"
        CheckInfeas{"primal_inf_squared > 0?"}
        Pricing[""steepest_edge_pricing_with_infeasibilities()<br/>leaving_index, direction<br/>max (squared_infeas[j] / dy_steepest_edge[j])""]
    end
    
    subgraph "BTRANStage"
        BTRAN[""ft.b_transpose_solve_sparse()<br/>e_leaving → delta_y_sparse<br/>Solves B'·δy = e_leaving""]
    end
    
    subgraph "ReducedCostStage"
        ComputeDZ[""compute_delta_z()<br/>A_transpose, delta_y_sparse<br/>→ delta_z[n-m]<br/>δz[j] = -A(:,j)'·δy""]
    end
    
    subgraph "RatioTestStage"
        FirstStage[""first_stage_harris()<br/>Compute α_max""]
        SecondStage[""second_stage_harris()<br/>Select entering_index<br/>with max |δz[j]|""]
        BoundFlip[""bound_flipping_ratio_test()<br/>Allow nonbasic bound flips""]
    end
    
    subgraph "FTRANStage"
        FTRAN[""ft.b_solve()<br/>a_entering → delta_xB<br/>Solves B·δx = a_entering""]
    end
    
    subgraph "SolutionUpdateStage"
        UpdatePrimal[""x[j] += α·δx[j] for j in basic_list<br/>x[entering] = l or u""]
        UpdateDual[""y[i] += α·δy[i]<br/>z[j] += α·δz[j]""]
    end
    
    subgraph "BasisUpdateStage"
        SwapVars[""vstatus[leaving] = NONBASIC_*<br/>vstatus[entering] = BASIC<br/>basic_list[leaving_pos] = entering""]
        UpdateLU[""ft.update(delta_xB, leaving_pos)<br/>Rank-1 update: S_.col_start[k]++""]
        CheckRefactor{"ft.num_updates_ >= refactor_frequency?"}
        Refactor[""factorize_basis()<br/>Rebuild L0_, U0_<br/>Reset num_updates_ = 0""]
    end
    
    subgraph "EdgeWeightStage"
        UpdateEdge[""update_steepest_edge_weights()<br/>dy_steepest_edge[j] updated<br/>using delta_y pattern""]
    end
    
    State --> CheckInfeas
    CheckInfeas -->|"Yes"| Pricing
    CheckInfeas -->|"No"| Optimal["return OPTIMAL"]
    
    Pricing --> BTRAN
    BTRAN --> ComputeDZ
    ComputeDZ --> FirstStage
    FirstStage --> SecondStage
    SecondStage --> BoundFlip
    
    BoundFlip --> FTRAN
    FTRAN --> UpdatePrimal
    UpdatePrimal --> UpdateDual
    UpdateDual --> SwapVars
    SwapVars --> UpdateLU
    UpdateLU --> CheckRefactor
    CheckRefactor -->|"Yes"| Refactor
    CheckRefactor -->|"No"| UpdateEdge
    Refactor --> UpdateEdge
    UpdateEdge --> State
```
Sources: [cpp/src/dual_simplex/phase2.cpp:879-913](), [cpp/src/dual_simplex/basis_solves.cpp:846-878](), [cpp/src/dual_simplex/phase2.cpp:372-442](), [cpp/src/dual_simplex/phase2.cpp:1030-1135](), [cpp/src/dual_simplex/basis_solves.cpp:803-843](), [cpp/src/dual_simplex/basis_updates.cpp:525-545](), [cpp/src/dual_simplex/basis_solves.cpp:160-193]()

---

## Phase 2: Optimization

Once dual feasibility is established, Phase 2 runs the main dual simplex algorithm via `dual_phase2()` on the original problem. At each iteration:

1. **Pricing**: Call `steepest_edge_pricing()` or `steepest_edge_pricing_with_infeasibilities()` to select a primal-infeasible basic variable (leaving variable) with maximum (infeasibility)²/edge_weight ratio [cpp/src/dual_simplex/phase2.cpp:879-913]().

2. **BTRAN (Backward Transformation)**: Solve $B' \cdot \delta y = e_{leaving}$ using `b_transpose_solve()` or `b_transpose_solve_sparse()` to compute the dual simplex direction [cpp/src/dual_simplex/basis_solves.cpp:846-878]().

3. **Update reduced costs**: Compute $\delta z$ for nonbasic variables via `compute_delta_z()` which uses $A\_transpose$ to compute $\delta z_j = -A(:,j)' \cdot \delta y$ [cpp/src/dual_simplex/phase2.cpp:372-442]().

4. **Ratio test**: Call `phase2_ratio_test()` with Harris two-stage procedure or `bound_flipping_ratio_test()` to determine step length $\alpha$ and entering variable [cpp/src/dual_simplex/phase2.cpp:1030-1135]().

5. **FTRAN (Forward Transformation)**: Solve $B \cdot \delta x = a_{entering}$ using `b_solve()` to compute the primal direction for the entering column [cpp/src/dual_simplex/basis_solves.cpp:803-843]().

6. **Update primal solution**: $x \leftarrow x + \alpha \cdot \delta x$ where $\alpha$ is the step length from ratio test [cpp/src/dual_simplex/phase2.cpp:1-50]().

7. **Update dual solution**: $y \leftarrow y + \alpha \cdot \delta y, z \leftarrow z + \alpha \cdot \delta z$ [cpp/src/dual_simplex/phase2.cpp:1-50]().

8. **Update basis**: Swap entering/leaving variables, update `vstatus` array, call `ft.update()` to perform rank-one update of LU factorization [cpp/src/dual_simplex/basis_updates.hpp:106-109]().

9. **Update steepest edge weights**: Incrementally update edge norms via `update_steepest_edge_weights()` using the sparse pattern from BTRAN/FTRAN [cpp/src/dual_simplex/phase2.cpp:1-50]().

10. **Check refactorization**: If update count exceeds frequency, call `factorize_basis()` to rebuild $L \cdot U = P \cdot B$ [cpp/src/dual_simplex/basis_solves.cpp:160-172]().

Sources: [cpp/src/dual_simplex/phase2.cpp:1-50](), [cpp/src/dual_simplex/basis_updates.hpp:106-109](), [cpp/src/dual_simplex/basis_solves.cpp:160-172]()

---

## Basis Factorization and Updates

The dual simplex method maintains an LU factorization of the basis matrix $B$ with incremental rank-one updates. This is managed by the `basis_update_mpf_t` class (middle product form).

**Key Data Members:**
| Member | Type | Purpose |
|--------|------|---------|
| `L0_` | `csc_matrix_t` | Initial lower triangular factor from LU decomposition, unit diagonal [cpp/src/dual_simplex/basis_updates.hpp:172-172]() |
| `U0_` | `csc_matrix_t` | Initial upper triangular factor (column swaps applied during updates) [cpp/src/dual_simplex/basis_updates.hpp:173-173]() |
| `S_` | `csc_matrix_t` | Stores update vectors $d_i$ as columns: $S_(:, i)$ is the spike for $R_i$ [cpp/src/dual_simplex/basis_updates.hpp:176-176]() |
| `row_permutation_` | `std::vector<i_t>` | Row permutation $P$ from $P \cdot B = L \cdot U$ [cpp/src/dual_simplex/basis_updates.hpp:174-174]() |
| `refactor_frequency_` | `i_t` | Count threshold of rank-one updates before full refactorization [cpp/src/dual_simplex/basis_updates.hpp:181-181]() |

### basis_update_mpf_t Class

The `basis_update_mpf_t` class maintains the middle product form LU factorization:

```
L = L0 · R1^{-1} · R2^{-1} · ... · Rk^{-1}
U = U0 (modified in-place)

where Ri = I + ei·di'  (rank-one elementary matrices)
```

Sources: [cpp/src/dual_simplex/basis_updates.hpp:169-184](), [cpp/src/dual_simplex/basis_solves.cpp:160-193]()

---

## Pricing Strategies

Pricing determines which primal-infeasible basic variable should leave the basis. cuOpt implements **steepest edge pricing**, which selects the variable that gives the largest improvement in dual objective per simplex iteration.

### Steepest Edge Pricing

The steepest edge rule selects the leaving variable $j$ that maximizes:

$$(infeasibility_j)^2 / \|B^{-T} \cdot e_j\|^2$$

where $\|B^{-T} \cdot e_j\|^2$ is the steepest edge weight (stored in `dy_steepest_edge[j]`) [cpp/src/dual_simplex/phase2.cpp:879-913]().

Sources: [cpp/src/dual_simplex/phase2.cpp:879-913]()

---

## Ratio Test

The ratio test determines how far to move in the dual simplex direction before a nonbasic variable reaches its bound, which identifies the entering variable.

### Harris Ratio Test

The Harris ratio test is a numerically stable two-stage procedure implemented in `first_stage_harris()` and `second_stage_harris()` [cpp/src/dual_simplex/phase2.cpp:1030-1135]():

**Stage 1: Determine maximum step length** [cpp/src/dual_simplex/phase2.cpp:1030-1062]()  
Computes $\alpha_{max}$ by scanning nonbasic variables and determining the step length that maintains dual feasibility within `dual_tol`.

**Stage 2: Select entering variable** [cpp/src/dual_simplex/phase2.cpp:1065-1135]()  
Among all nonbasic variables $j$ with ratio $\alpha_j < \alpha_{max}$, selects the one with largest $|\delta z_j|$ to improve numerical stability.

### Bound Flipping Ratio Test

The bound flipping ratio test extends the standard ratio test by allowing bounded variables to flip from one bound to the other without entering the basis, reducing the total number of iterations [cpp/src/dual_simplex/phase2.cpp:1138-1157]().

Sources: [cpp/src/dual_simplex/phase2.cpp:1030-1157]()

---

## Presolve and Scaling

Before the simplex iterations begin, the problem undergoes presolving and scaling to improve numerical stability and reduce problem size via transformation utilities [cpp/src/dual_simplex/presolve.cpp:1-50]().

Sources: [cpp/src/dual_simplex/presolve.cpp:1-50]()

---

## Key Data Structures

### lp_problem_t
Represents the LP problem in standard equality form used internally by the dual simplex algorithm [cpp/src/dual_simplex/presolve.hpp:41-72]().

```cpp
template <typename i_t, typename f_t>
struct lp_problem_t {
  i_t num_rows;
  i_t num_cols;
  std::vector<f_t> objective;
  csc_matrix_t<i_t, f_t> A;
  std::vector<f_t> rhs;
  std::vector<f_t> lower;
  std::vector<f_t> upper;
  f_t obj_constant;
  f_t obj_scale;
};
```

Sources: [cpp/src/dual_simplex/presolve.hpp:41-72]()

---

