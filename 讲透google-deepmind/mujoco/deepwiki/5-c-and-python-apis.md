<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mujoco · page 5 C and Python APIs · fetched 2026-10-26 -->

# C and Python APIs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [doc/APIreference/APIfunctions.rst](doc/APIreference/APIfunctions.rst)
- [doc/APIreference/APItypes.rst](doc/APIreference/APItypes.rst)
- [doc/js/linenumbers.js](doc/js/linenumbers.js)
- [doc/programming/index.rst](doc/programming/index.rst)
- [doc/programming/modeledit.rst](doc/programming/modeledit.rst)
- [doc/programming/visualization.rst](doc/programming/visualization.rst)
- [doc/python.rst](doc/python.rst)
- [python/mujoco/rollout.cc](python/mujoco/rollout.cc)
- [python/mujoco/rollout.py](python/mujoco/rollout.py)
- [python/mujoco/rollout_test.py](python/mujoco/rollout_test.py)

</details>



This page describes MuJoCo's core C API and Python bindings architecture. The C API provides low-level access to the simulation engine, while the Python bindings offer a Pythonic interface built on top of it. For information about the model editing API (mjSpec), see [mjSpec C++ API](#2.2). For details about MJX (JAX-accelerated physics), see [MJX: JAX-Accelerated Physics](#6).

## Purpose and Scope

MuJoCo exposes two primary programming interfaces:

1.  **C API**: The native interface defined in `mujoco.h`, providing direct access to the simulation engine through a collection of functions prefixed with `mj_`, `mju_`, `mjv_`, `mjr_`, and `mjui_`. [include/mujoco/mujoco.h:18-37]()
2.  **Python Bindings**: A pybind11-based wrapper that exposes the C API to Python, adding Pythonic conveniences like NumPy integration, named indexing, and exception-based error handling. [python/mujoco/functions.cc:38-53]()

Both interfaces operate on the same core data structures (`mjModel` and `mjData`) but differ in how they handle memory management, error reporting, and data access patterns.

---

## C API Structure

The C API is defined in a collection of header files, with `mujoco.h` serving as the main entry point. The API is organized into functional groups, each with a distinct naming prefix.

### Header Organization

```mermaid
graph TB
    subgraph "C Header Hierarchy"
    ["include/mujoco/mujoco.h"] -- includes --> ["include/mujoco/mjdata.h"]
    ["include/mujoco/mujoco.h"] -- includes --> ["include/mujoco/mjmodel.h"]
    ["include/mujoco/mujoco.h"] -- includes --> ["include/mujoco/mjspec.h"]
    ["include/mujoco/mujoco.h"] -- includes --> ["include/mujoco/mjrender.h"]
    ["include/mujoco/mujoco.h"] -- includes --> ["include/mujoco/mjvisualize.h"]
    ["include/mujoco/mujoco.h"] -- includes --> ["include/mujoco/mjui.h"]
    
    ["include/mujoco/mjdata.h"] --> ["mjData struct"]
    ["include/mujoco/mjmodel.h"] --> ["mjModel struct"]
    ["include/mujoco/mjspec.h"] --> ["mjSpec struct"]
    ["include/mujoco/mjrender.h"] --> ["mjrContext struct"]
    ["include/mujoco/mjvisualize.h"] --> ["mjvScene struct"]
    ["include/mujoco/mjui.h"] --> ["mjUI struct"]
    end
```

**Sources:** [include/mujoco/mujoco.h:25-37]()

### Function Categories

The C API functions are organized by prefix, indicating their purpose:

| Prefix | Purpose | Example Functions |
| :--- | :--- | :--- |
| `mj_` | Core simulation and model management | `mj_step`, `mj_forward`, `mj_loadXML`, `mj_compile` |
| `mju_` | Utility functions (math, memory, etc.) | `mju_error`, `mju_warning`, `mju_malloc`, `mju_zero` |
| `mjv_` | Visualization scene management | `mjv_updateScene`, `mjv_defaultCamera`, `mjv_addGeoms` |
| `mjr_` | OpenGL rendering | `mjr_render`, `mjr_readPixels`, `mjr_makeContext` |
| `mjui_` | UI framework | `mjui_add`, `mjui_update`, `mjui_event` |

**Sources:** [include/mujoco/mujoco.h:79-185](), [doc/APIreference/functions.rst:5-196]()

### Core Simulation Functions

The main entry points for the simulator are `mj_step`, `mj_forward`, and `mj_inverse`. `mj_step` advances the simulation by one time step, while `mj_forward` performs computations (kinematics, forces, accelerations) without integration. `mj_inverse` maps acceleration to force. [doc/APIreference/functions.rst:179-196]()

### Error Handling and Callbacks

The C API uses global function pointers for error handling and computation pipeline extension. Users can install custom handlers for errors (`mju_user_error`) or warnings (`mju_user_warning`). It also provides hooks for passive forces (`mjcb_passive`), control logic (`mjcb_control`), and sensors (`mjcb_sensor`). [include/mujoco/mujoco.h:45-62]()

---

## Python Bindings Architecture

The Python bindings are implemented using `pybind11`, providing automatic conversion between C types and Python types while maintaining performance through direct memory access.

### Implementation Overview

The bindings are split into several sub-modules that are aggregated in the main `mujoco` package:
*   `_structs`: Bindings for MuJoCo structures like `MjModel` and `MjData`. [python/mujoco/structs.cc:104-104]()
*   `_functions`: Bindings for C API functions. [python/mujoco/functions.cc:40-40]()
*   `_specs`: Bindings for the `mjSpec` editing API. [python/mujoco/specs.cc:1-45]()

### Wrapper Classes and Memory Management

Python bindings use wrapper classes (e.g., `MjModelWrapper`, `MjDataWrapper`) to manage the lifetime of MuJoCo structures. These wrappers ensure that memory is correctly allocated and deallocated, often using custom memory handlers like `mju_malloc` and `mju_free`. [python/mujoco/structs.cc:78-79](), [python/mujoco/functions.cc:159-172]()

### GIL Management

Expensive C functions like `mj_step` and `mj_recompile` are wrapped with `py::gil_scoped_release` to release the Global Interpreter Lock, allowing other Python threads to run during simulation or compilation. [python/mujoco/functions.cc:126-126](), [python/mujoco/structs.cc:85-90]()

---

## Key API Function Categories

### Model Loading and Compilation

**C API:**
`mj_loadXML` parses an XML file and returns a compiled `mjModel`. [include/mujoco/mujoco.h:132-132]() Alternatively, `mj_parseXML` returns an `mjSpec` which can then be compiled via `mj_compile`. [include/mujoco/mujoco.h:136-156]()

**Python API:**
The Python `MjModel` class provides factory methods like `from_xml_string` and `from_xml_path`. The `MjSpec` class also provides a `compile()` method. [python/mujoco/specs_test.py:63-64](), [python/mujoco/bindings_test.py:125-125]()

### Simulation Stepping

| Function | Purpose |
| :--- | :--- |
| `mj_step` | Complete simulation step (Forward dynamics + Integration) |
| `mj_forward` | Forward dynamics only (kinematics, forces, accelerations) |
| `mj_inverse` | Inverse dynamics (acceleration to force mapping) |

**Sources:** [doc/APIreference/functions.rst:179-196](), [python/mujoco/functions.cc:113-132]()

---

## Python-Specific Features

### Named Indexing

Python bindings provide a high-level "named indexing" interface. Instead of manually looking up IDs using `mj_name2id`, users can access elements by name directly on the model or data objects using the `.bind()` method or specialized accessors like `data.actuator('name')`. [python/mujoco/bindings_test.py:209-220](), [python/mujoco/specs_test.py:140-142]()

### NumPy Integration

MuJoCo's numeric arrays (e.g., `qpos`, `qvel`, `ctrl`) are exposed as NumPy arrays via `pybind11::eigen` and custom array wrappers. These arrays are views into the underlying C memory, meaning modifications to the NumPy array directly affect the simulation state. [python/mujoco/structs.cc:58-74](), [python/mujoco/bindings_test.py:166-175]()

### Asset Management and VFS

The Python API supports passing an `assets` dictionary (mapping filenames to bytes) when loading models. This uses MuJoCo's Virtual File System (VFS) internally to provide assets to the compiler without writing them to disk. [python/mujoco/specs.cc:84-113](), [python/mujoco/bindings_test.py:139-141]()

### Exception-Based Error Handling

C-level errors are intercepted using `InterceptMjErrors` and raised as Python exceptions (e.g., `ValueError` or `FatalError`). [python/mujoco/functions.cc:84-88](), [python/mujoco/structs.cc:92-94]()

### System-Level Mapping

```mermaid
graph LR
    subgraph "Natural Language Space"
    ["Simulation Step"]
    ["Model View"]
    ["Data View"]
    end

    subgraph "Code Entity Space"
    ["Simulation Step"] --> ["mj_step()"]
    ["Model View"] --> ["MjModel class"]
    ["Data View"] --> ["MjData class"]
    ["mj_step()"] --> ["python/mujoco/functions.cc"]
    ["MjModel class"] --> ["python/mujoco/structs.cc"]
    ["Data View"] --> ["python/mujoco/structs.cc"]
    end
```

**Sources:** [python/mujoco/functions.cc:113-114](), [python/mujoco/structs.cc:104-108]()

---

## System Identification (sysid)

The `mujoco.sysid` package provides tools for fitting physics parameters to measured data. It includes `ParameterDict` for managing optimization targets and `ModelSequences` for handling multi-step data.

For details, see [System Identification Toolbox](#5.5).

---

## Child Pages

*   [C API Reference](#5.1) — Detailed documentation of core C functions: model loading, simulation stepping, and state management.
*   [Python Bindings Architecture](#5.2) — Deep dive into pybind11 implementation, wrapper classes, and GIL management.
*   [Python API Usage](#5.3) — Practical guide for using the `mujoco` Python package, including loading models and accessing data.
*   [Python Rollout and Optimization](#5.4) — High-performance batched simulation via the `rollout` module and least-squares optimization.
*   [System Identification Toolbox](#5.5) — Tools for physics parameter estimation and model fitting using the `mujoco.sysid` package.

---

