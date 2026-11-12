<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuopt-examples · page 10 Benchmarking and Performance · fetched 2026-10-26 -->

# Benchmarking and Performance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmark_apis/README.md](benchmark_apis/README.md)
- [benchmark_apis/analyze_benchmark_results.py](benchmark_apis/analyze_benchmark_results.py)
- [benchmark_apis/benchmark_cuopt.py](benchmark_apis/benchmark_cuopt.py)
- [benchmark_apis/c_api_driver/BUILD_GUIDE.md](benchmark_apis/c_api_driver/BUILD_GUIDE.md)
- [benchmark_apis/c_api_driver/Makefile](benchmark_apis/c_api_driver/Makefile)
- [benchmark_apis/c_api_driver/README.md](benchmark_apis/c_api_driver/README.md)
- [benchmark_apis/c_api_driver/cuopt_json_to_c_api.c](benchmark_apis/c_api_driver/cuopt_json_to_c_api.c)
- [benchmark_apis/c_api_driver/test_problem.json](benchmark_apis/c_api_driver/test_problem.json)
- [benchmark_apis/cuopt_json_to_ampl.py](benchmark_apis/cuopt_json_to_ampl.py)
- [benchmark_apis/cuopt_json_to_cvxpy.py](benchmark_apis/cuopt_json_to_cvxpy.py)
- [benchmark_apis/cuopt_json_to_gams.py](benchmark_apis/cuopt_json_to_gams.py)
- [benchmark_apis/cuopt_json_to_julia.jl](benchmark_apis/cuopt_json_to_julia.jl)
- [benchmark_apis/cuopt_json_to_pulp.py](benchmark_apis/cuopt_json_to_pulp.py)
- [benchmark_apis/cuopt_json_to_python_api.py](benchmark_apis/cuopt_json_to_python_api.py)
- [benchmark_apis/transform.py](benchmark_apis/transform.py)

</details>



This page documents the benchmarking infrastructure for comparing cuOpt performance across different modeling frameworks and APIs. The system measures interface overhead, cuOpt solver time, and end-to-end performance for the same problems solved through different access patterns.

For general cuOpt API usage, see the Python API documentation at [#3.1](). For specific integration examples with modeling languages, see [#8](). For VRP-specific performance considerations, see [#4]().

---

## Purpose and Architecture

The benchmarking system provides standardized performance measurement across seven cuOpt interfaces: C API, Python Problem API, CVXPY, PuLP, AMPL, Julia/JuMP, and GAMS. The architecture uses a common JSON problem format, standardized timing markers, and automated result analysis to enable apples-to-apples performance comparisons.

**Benchmarking System Components**

```mermaid
graph TB
    subgraph "Input"
        MPS["MPS Files<br/>Industry Standard"]
        JSON["cuOpt JSON Format<br/>Standardized Problem Representation"]
    end
    
    subgraph "Conversion"
        TRANSFORM["transform.py<br/>MPS → JSON Converter"]
    end
    
    subgraph "Benchmark Orchestration"
        BENCH["benchmark_cuopt.py<br/>Main Orchestrator"]
        PARSERS["Output Parsers<br/>parse_*_output functions"]
    end
    
    subgraph "API Drivers"
        C_DRIVER["cuopt_json_to_c_api<br/>C executable"]
        PY_DRIVER["cuopt_json_to_python_api.py"]
        CVXPY_DRIVER["cuopt_json_to_cvxpy.py"]
        PULP_DRIVER["cuopt_json_to_pulp.py"]
        AMPL_DRIVER["cuopt_json_to_ampl.py"]
        JULIA_DRIVER["cuopt_json_to_julia.jl"]
        GAMS_DRIVER["cuopt_json_to_gams.py"]
    end
    
    subgraph "Timing Infrastructure"
        MARKERS["Timing Markers<br/>PROBLEM_START<br/>CUOPT_SOLVE_START<br/>CUOPT_SOLVE_RETURN<br/>SOLVE_END_TIME"]
        METRICS["Metrics Calculation<br/>interface_overhead<br/>cuopt_solver_time<br/>process_total_time"]
    end
    
    subgraph "Output"
        CSV["cuopt_benchmark_results.csv<br/>Raw Timing Data"]
        ANALYSIS["analyze_benchmark_results.py<br/>Comparative Analysis"]
        REPORTS["Performance Reports<br/>Fastest Solver<br/>Objective Consistency<br/>Overhead Analysis"]
    end
    
    MPS --> TRANSFORM
    TRANSFORM --> JSON
    JSON --> BENCH
    
    BENCH --> C_DRIVER
    BENCH --> PY_DRIVER
    BENCH --> CVXPY_DRIVER
    BENCH --> PULP_DRIVER
    BENCH --> AMPL_DRIVER
    BENCH --> JULIA_DRIVER
    BENCH --> GAMS_DRIVER
    
    C_DRIVER --> MARKERS
    PY_DRIVER --> MARKERS
    CVXPY_DRIVER --> MARKERS
    PULP_DRIVER --> MARKERS
    AMPL_DRIVER --> MARKERS
    JULIA_DRIVER --> MARKERS
    GAMS_DRIVER --> MARKERS
    
    MARKERS --> PARSERS
    PARSERS --> METRICS
    METRICS --> CSV
    CSV --> ANALYSIS
    ANALYSIS --> REPORTS
    
    BENCH -.incremental updates.-> CSV
```

Sources: [benchmark_apis/benchmark_cuopt.py:18-45](), [benchmark_apis/analyze_benchmark_results.py:18-35](), [benchmark_apis/transform.py:18-42]()

---

## cuOpt JSON Format

The benchmarking system uses a standardized JSON format to represent LP and MILP problems. This format eliminates modeling language differences and enables direct comparison of solver performance. For detailed technical specifications, see [cuOpt JSON Format](#10.1).

### Schema Structure

```mermaid
graph LR
    subgraph "cuOpt JSON Problem"
        CSR["csr_constraint_matrix<br/>offsets: int[]<br/>indices: int[]<br/>values: float[]"]
        OBJ["objective_data<br/>coefficients: float[]<br/>offset: float<br/>scalability_factor: float"]
        CBOUNDS["constraint_bounds<br/>lower_bounds: float[]<br/>upper_bounds: float[]"]
        VBOUNDS["variable_bounds<br/>lower_bounds: float[]<br/>upper_bounds: float[]"]
        VTYPES["variable_types<br/>['C'|'I'][]"]
        VNAMES["variable_names<br/>string[]"]
        MAX["maximize<br/>boolean"]
    end
    
    CSR --> PROBLEM["Problem Instance"]
    OBJ --> PROBLEM
    CBOUNDS --> PROBLEM
    VBOUNDS --> PROBLEM
    VTYPES --> PROBLEM
    VNAMES --> PROBLEM
    MAX --> PROBLEM
```

Sources: [benchmark_apis/c_api_driver/test_problem.json:1-24](), [benchmark_apis/cuopt_json_to_python_api.py:31-45]()

### Infinity Handling

All API drivers must handle string representations of infinity. The `handle_infinity_values` function converts strings like `"inf"` or `"ninf"` back to their float equivalents.

Sources: [benchmark_apis/cuopt_json_to_python_api.py:60-82](), [benchmark_apis/cuopt_json_to_pulp.py:48-77](), [benchmark_apis/cuopt_json_to_julia.jl:38-70]()

### MPS to JSON Conversion

The `transform.py` utility converts industry-standard MPS files to cuOpt JSON format using the `cuopt_mps_parser`.

Sources: [benchmark_apis/transform.py:23-41](), [benchmark_apis/transform.py:45-91]()

---

## Timing Infrastructure

The benchmarking system uses standardized timing markers embedded in API driver output to decompose end-to-end execution time into measurable components.

### Timing Markers

**Timing Marker Flow**

```mermaid
sequenceDiagram
    participant API as "API Driver"
    participant cuOpt as "cuOpt Solver"
    participant Output as "stdout"
    
    API->>Output: PROBLEM_START: timestamp
    Note over API: Parse JSON<br/>Build problem structure<br/>Setup interface objects
    API->>cuOpt: Create Problem
    API->>Output: CUOPT_CREATE_PROBLEM: timestamp
    API->>cuOpt: Solve
    API->>Output: CUOPT_SOLVE_START: timestamp
    Note over cuOpt: GPU-accelerated solving
    cuOpt-->>API: Solution
    API->>Output: CUOPT_SOLVE_RETURN: timestamp
    Note over API: Extract results<br/>Format output
    API->>Output: SOLVE_END_TIME: timestamp
```

Sources: [benchmark_apis/benchmark_cuopt.py:57-91]()

### Computed Metrics

The `calculate_timing_metrics` function computes three key performance indicators: `interface_overhead`, `cuopt_solver_time`, and `total_time`.

Sources: [benchmark_apis/benchmark_cuopt.py:93-121]()

---

## Running Benchmarks

The `benchmark_cuopt.py` script orchestrates benchmark execution across multiple APIs and problem instances. For detailed instructions on running these benchmarks, see [Running Benchmarks](#10.2).

### Solver Configuration

**Solver Mapping Table**

```mermaid
graph TB
    subgraph "Solver Identifiers"
        C["C<br/>C API"]
        PYTHON["python<br/>Python Problem API"]
        CVXPY["cvxpy<br/>CVXPY Integration"]
        PULP["pulp<br/>PuLP Integration"]
        AMPL["ampl<br/>AMPL Integration"]
        JULIA["julia<br/>Julia/JuMP Integration"]
        GAMS["gams<br/>GAMS Integration"]
    end
    
    subgraph "Executables"
        C_EXE["./cuopt_json_to_c_api"]
        PY_EXE["python cuopt_json_to_python_api.py"]
        CVXPY_EXE["python cuopt_json_to_cvxpy.py --solver_verbose"]
        PULP_EXE["python cuopt_json_to_pulp.py --quiet"]
        AMPL_EXE["python cuopt_json_to_ampl.py --quiet"]
        JULIA_EXE["julia cuopt_json_to_julia.jl --quiet"]
        GAMS_EXE["python cuopt_json_to_gams.py"]
    end
    
    subgraph "Parsers"
        C_PARSER["parse_cuopt_json_solver_output"]
        PY_PARSER["parse_cuopt_api2_output"]
        CVXPY_PARSER["parse_cuopt_json_to_cvxpy_output"]
        PULP_PARSER["parse_cuopt_pulp_output"]
        AMPL_PARSER["parse_cuopt_ampl_output"]
        JULIA_PARSER["parse_cuopt_julia_output"]
        GAMS_PARSER["parse_cuopt_gams_output"]
    end
    
    C --> C_EXE --> C_PARSER
    PYTHON --> PY_EXE --> PY_PARSER
    CVXPY --> CVXPY_EXE --> CVXPY_PARSER
    PULP --> PULP_EXE --> PULP_PARSER
    AMPL --> AMPL_EXE --> AMPL_PARSER
    JULIA --> JULIA_EXE --> JULIA_PARSER
    GAMS --> GAMS_EXE --> GAMS_PARSER
```

Sources: [benchmark_apis/benchmark_cuopt.py:20-28](), [benchmark_apis/benchmark_cuopt.py:141-180]()

---

## Results Analysis

The `analyze_benchmark_results.py` script processes benchmark CSV output to generate comparative performance reports, identifying the fastest solver for each problem and checking for objective value consistency.

**Analysis Workflow**

```mermaid
graph TB
    CSV["cuopt_benchmark_results.csv"]
    DISCOVER["discover_solvers<br/>Extract solver names from headers"]
    ANALYZE_ROW["analyze_row<br/>Per-problem analysis"]
    
    subgraph "Per-Problem Analysis"
        EXTRACT["Extract timing data<br/>Convert strings to floats"]
        IDENTIFY["Identify successful solvers<br/>objective != None<br/>total_time != None"]
        CHECK_OBJ["Check objective consistency<br/>is_close with 1e-6 tolerance"]
        FASTEST_TOTAL["Find fastest by total time"]
        FASTEST_CUOPT["Find fastest by cuOpt solver time"]
        FASTEST_INTERFACE["Find fastest by interface overhead"]
        CALC_DIFF["Calculate percentage differences"]
    end
    
    AGGREGATE["Aggregate statistics<br/>Mean, median, std dev"]
    REPORT["Generate formatted report"]
    
    CSV --> DISCOVER
    DISCOVER --> ANALYZE_ROW
    ANALYZE_ROW --> EXTRACT
    EXTRACT --> IDENTIFY
    IDENTIFY --> CHECK_OBJ
    CHECK_OBJ --> FASTEST_TOTAL
    FASTEST_TOTAL --> FASTEST_CUOPT
    FASTEST_CUOPT --> FASTEST_INTERFACE
    FASTEST_INTERFACE --> CALC_DIFF
    CALC_DIFF --> AGGREGATE
    AGGREGATE --> REPORT
```

Sources: [benchmark_apis/analyze_benchmark_results.py:53-72](), [benchmark_apis/analyze_benchmark_results.py:74-143]()

---

## C API Driver

The C API driver provides the lowest-level access to cuOpt with minimal overhead. It requires careful handling of memory management and library linking. For more details, see [C API Driver](#10.3).

**Build System Overview**

```mermaid
graph TB
    subgraph "Build Dependencies"
        CJSON["libcjson-dev<br/>JSON parsing library"]
        CUOPT_H["cuopt_c.h<br/>cuOpt header files"]
        LIBCUOPT["libcuopt.so<br/>cuOpt shared library"]
    end
    
    subgraph "Makefile"
        DETECT["Path Auto-detection<br/>Search conda envs<br/>Search system paths"]
        COMPILE["Compilation<br/>gcc -c cuopt_json_to_c_api.c"]
        LINK["Linking<br/>gcc -o cuopt_json_to_c_api<br/>-lcuopt -lcjson"]
    end
    
    subgraph "Build Modes"
        SYSTEM["System Build<br/>conda deactivate<br/>Use system libraries"]
        CONDA["Conda Build<br/>Set CONDA_ENV=cuopt_dev"]
    end
    
    CJSON --> DETECT
    CUOPT_H --> DETECT
    LIBCUOPT --> DETECT
    DETECT --> COMPILE
    COMPILE --> LINK
    
    SYSTEM --> COMPILE
    CONDA --> COMPILE
```

Sources: [benchmark_apis/c_api_driver/Makefile:19-47](), [benchmark_apis/c_api_driver/Makefile:112-145]()

---

