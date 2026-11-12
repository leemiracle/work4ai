<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuopt · extra page Feasibility Jump Implementation · fetched 2026-10-26 -->

# Feasibility Jump Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cpp/src/mip_heuristics/CMakeLists.txt](cpp/src/mip_heuristics/CMakeLists.txt)
- [cpp/src/mip_heuristics/feasibility_jump/cpu/portfolio.cpp](cpp/src/mip_heuristics/feasibility_jump/cpu/portfolio.cpp)
- [cpp/src/mip_heuristics/feasibility_jump/cpu/state.hpp](cpp/src/mip_heuristics/feasibility_jump/cpu/state.hpp)
- [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cu](cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cu)
- [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cuh](cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cuh)
- [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump_kernels.cu](cpp/src/mip_heuristics/feasibility_jump/feasibility_jump_kernels.cu)
- [cpp/src/mip_heuristics/feasibility_jump/fj_cpu.cuh](cpp/src/mip_heuristics/feasibility_jump/fj_cpu.cuh)
- [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cu](cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cu)
- [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cuh](cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cuh)
- [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary_kernels.cpp](cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary_kernels.cpp)
- [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary_preprocess.cu](cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary_preprocess.cu)
- [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary_utils.hpp](cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary_utils.hpp)
- [cpp/src/mip_heuristics/feasibility_jump/sat/cdcl_sat.cpp](cpp/src/mip_heuristics/feasibility_jump/sat/cdcl_sat.cpp)
- [cpp/src/mip_heuristics/feasibility_jump/sat/cdcl_sat_utils.hpp](cpp/src/mip_heuristics/feasibility_jump/sat/cdcl_sat_utils.hpp)
- [cpp/src/mip_heuristics/local_search/local_search.cu](cpp/src/mip_heuristics/local_search/local_search.cu)
- [cpp/src/mip_heuristics/presolve/probing_cache.cu](cpp/src/mip_heuristics/presolve/probing_cache.cu)
- [cpp/src/mip_heuristics/utils.cuh](cpp/src/mip_heuristics/utils.cuh)
- [cpp/src/routing/util_kernels/runtime_checks.cu](cpp/src/routing/util_kernels/runtime_checks.cu)
- [cpp/src/utilities/macros.cuh](cpp/src/utilities/macros.cuh)
- [cpp/tests/distance_engine/CMakeLists.txt](cpp/tests/distance_engine/CMakeLists.txt)
- [cpp/tests/mip/doc_example_test.cu](cpp/tests/mip/doc_example_test.cu)
- [cpp/tests/mip/feasibility_jump_tests.cu](cpp/tests/mip/feasibility_jump_tests.cu)
- [cpp/tests/mip/semi_continuous_test.cu](cpp/tests/mip/semi_continuous_test.cu)
- [cpp/tests/mip/server_test.cu](cpp/tests/mip/server_test.cu)
- [cpp/tests/mip/unit_test.cu](cpp/tests/mip/unit_test.cu)
- [cpp/tests/qp/CMakeLists.txt](cpp/tests/qp/CMakeLists.txt)
- [cpp/tests/qp/unit_tests/no_constraints.cu](cpp/tests/qp/unit_tests/no_constraints.cu)
- [cpp/tests/qp/unit_tests/two_variable_test.cu](cpp/tests/qp/unit_tests/two_variable_test.cu)
- [cpp/tests/utilities/inline_lp_test_utils.hpp](cpp/tests/utilities/inline_lp_test_utils.hpp)

</details>



## Purpose and Scope

This document provides a deep technical dive into the Feasibility Jump (FJ) algorithm implementation within NVIDIA cuOpt. Feasibility Jump is a core metaheuristic employed within the hybrid GPU/CPU Mixed Integer Programming (MIP) solver for repairing infeasibilities and discovering high-quality primal solutions. 

The implementation spans high-performance GPU kernels for massively parallel move evaluation and load balancing, as well as an advanced CPU portfolio engine featuring specialized binary engines, SAT/CDCL utilities, climber diversification, auditing, and acceptance criteria.

Sources: [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cuh:14-15](), [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cuh:16-20]()

---

## Algorithm Overview and Execution Modes

Feasibility Jump is a local search metaheuristic that explores the solution space by changing variable assignments (jumps) to minimize constraint violations and optimize the objective function. The algorithm operates under several distinct modes (`fj_mode_t`), supporting pure feasibility finding, greedy descents, exit criteria based on local minimum counts, and rounding repair phases.

```mermaid
graph TB
    subgraph "Execution Modes Space"
        Start["fj_t::solve()"] --> ModeCheck{"fj_mode_t"}
        ModeCheck -->|"FIRST_FEASIBLE"| FF["Find First Feasible"]
        ModeCheck -->|"GREEDY_DESCENT"| GD["Single Descent to Local Min"]
        ModeCheck -->|"EXIT_NON_IMPROVING"| EN["Run until n_of_minimums_for_exit"]
        ModeCheck -->|"ROUNDING"| RND["Eliminate Fractional Variables"]
    end
    
    subgraph "Code Entity Space"
        FF --> C_Solve["fj_t::solve(solution_t& solution)"]
        GD --> C_Loop["fj_t::host_loop()"]
        EN --> C_Graph["fj_t::run_step_device()"]
        RND --> C_Round["fj_t::round_remaining_fractionals()"]
    end

    Sources: [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cuh:109-138](), [cpp/tests/mip/feasibility_jump_tests.cu:121-126]()
```

Sources: [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cuh:100-139](), [cpp/tests/mip/feasibility_jump_tests.cu:119-126]()

---

## GPU Architecture and Load Balancing Kernels

The GPU implementation (`fj_t`) manages device-side states using `climber_data_t` structures, leveraging custom kernel launches for score updates, move generation, and load balancing across irregular constraint matrices.

```mermaid
graph TB
    subgraph "GPU System Architecture"
        FJ["cuopt::mathematical_optimization::mip::fj_t"] --> CD["climber_data_t::view_t"]
        CD --> Assign["incumbent_assignment"]
        CD --> LHS["incumbent_lhs"]
        CD --> Weights["cstr_weights"]
        CD --> Scores["jump_move_scores"]
    end

    subgraph "Kernel Execution Space"
        FJ -->|"launch"| LBMap["load_balancing_compute_workid_mappings"]
        FJ -->|"launch"| LBScores["load_balancing_compute_scores_binary"]
        FJ -->|"launch"| MTM["compute_mtm_moves_kernel"]
        FJ -->|"launch"| WeightKernel["handle_local_minimum_kernel"]
    end

    Sources: [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cuh:98-183](), [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cu:76-105]()
```

### Load Balancing and Move Generation
Irregular sparse matrix structures are handled via work-ID mappings (`fj_load_balancing_workid_mapping_t`), prefix sums (`row_size_bin_prefix_sum`, `row_size_nonbin_prefix_sum`), and distributed parallel reduction kernels (`cub::BlockReduce`). Heavy variables and constraints are partitioned across warps to minimize tail latency during move scoring.

Sources: [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cuh:77-83](), [cpp/src/mip_heuristics/feasibility_jump/feasibility_jump.cu:70-104]()

---

## CPU Portfolio, Search, and Audit

The CPU-side feasibility jump architecture (`fj_cpu_worker_t`, `fj_cpu_climber_t`) supports asynchronous multi-threaded execution pools managed via OpenMP tasks. Lane diversification applies distinct personas (e.g., LP starts, network starts, structural completion, weight donation) across parallel workers.

```mermaid
graph LR
    subgraph "CPU Portfolio Orchestration"
        Worker["fj_cpu_worker_t::create_worker()"] --> Climber["fj_cpu_climber_t"]
        Climber --> Lane["apply_lane_diversification()"]
        Lane --> RunAsync["fj_cpu_worker_t::run_async()"]
    end
    
    subgraph "Audit and Verification"
        Climber --> Audit["audit_binary_incumbent()"]
        Audit --> Bounds["check_variable_within_bounds()"]
        Audit --> RowAct["compensated_dot2_csr()"]
    end

    Sources: [cpp/src/mip_heuristics/feasibility_jump/cpu/portfolio.cpp:30-50](), [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cu:47-87]()
```

### Audit Subsystem
To prevent numerical drift or illegal assignments, the CPU engine runs strict verification routines like `audit_binary_incumbent`. These functions assert that assignments satisfy bounds, integrality constraints, row activity tolerances via compensated summation (`compensated_dot2_csr`), and objective alignment.

Sources: [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cu:47-87]()

---

## SAT/CDCL Utilities and Binary Engine

For instances containing exclusively binary variables with integer coefficients within `int8` or `int16` ranges, cuOpt invokes a high-speed SIMD-capable integer binary engine (`fj_bin_engine_t`) and Conflict-Driven Clause Learning (CDCL) SAT utilities (`cdcl_sat.cpp`).

```mermaid
graph TB
    subgraph "Binary Engine Pipeline"
        Scan["fj_bin_scan()"] --> Narrow["fj_bin_narrow()"]
        Narrow --> Encode["fj_bin_encode()"]
        Encode --> Engine["fj_bin_engine_t"]
        Engine --> Sat["fj_bin_sat_search()"]
    end

    subgraph "Code Entity Space"
        Scan --> F1["fj_bin_scan_t"]
        Narrow --> F2["try_cpufj_binary_solve()"]
        Sat --> F3["sat_result_t"]
    end

    Sources: [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cuh:123-161](), [cpp/src/mip_heuristics/feasibility_jump/sat/cdcl_sat.cpp:1-25]()
```

The binary solver pipeline scans coefficients (`fj_bin_scan`), narrows problem bounds, encodes general integers into bit representations (`fj_bin_encode`), and executes specialized local search combined with `fj_bin_sat_search`.

Sources: [cpp/src/mip_heuristics/feasibility_jump/fj_cpu_binary.cuh:123-161](), [cpp/src/mip_heuristics/feasibility_jump/sat/cdcl_sat.cpp:1-50]()

---

## Acceptance Criteria and Quality Assurance

Feasibility Jump solutions undergo rigorous validation against objective targets and feasibility constraints during unit and regression testing (`feasibility_jump_tests.cu`).

| Test Helper / Criterion | Function Signature / Check | Validation Goal |
|-------------------------|----------------------------|-----------------|
| Feasibility Verification | `solution.get_feasible()` | Ensure instance is certified feasible |
| Objective Bound Check | `solution.get_user_objective() <= obj_target` | Verify solution cost does not exceed target threshold |
| Runoff Prevention | `state.incumbent_violation <= 1e60` | Guard against numerical explosion and objective runoff |
| Minimum Tracking | `climber.local_minimums_reached` | Track local search plateau escapes and DDFW weight scaling |

Sources: [cpp/tests/mip/feasibility_jump_tests.cu:117-164]()

---

