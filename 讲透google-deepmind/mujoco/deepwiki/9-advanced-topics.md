<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mujoco · page 9 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [doc/XMLreference.rst](doc/XMLreference.rst)
- [doc/XMLschema.rst](doc/XMLschema.rst)
- [doc/changelog.rst](doc/changelog.rst)
- [src/user/user_api.cc](src/user/user_api.cc)
- [src/user/user_api.h](src/user/user_api.h)
- [src/user/user_mesh.cc](src/user/user_mesh.cc)
- [src/user/user_model.cc](src/user/user_model.cc)
- [src/user/user_model.h](src/user/user_model.h)
- [src/user/user_objects.cc](src/user/user_objects.cc)
- [src/user/user_objects.h](src/user/user_objects.h)
- [src/xml/xml_native_reader.cc](src/xml/xml_native_reader.cc)
- [src/xml/xml_native_writer.cc](src/xml/xml_native_writer.cc)
- [test/user/user_api_test.cc](test/user/user_api_test.cc)
- [test/user/user_mesh_test.cc](test/user/user_mesh_test.cc)
- [test/user/user_objects_test.cc](test/user/user_objects_test.cc)
- [test/xml/xml_native_reader_test.cc](test/xml/xml_native_reader_test.cc)
- [test/xml/xml_native_writer_test.cc](test/xml/xml_native_writer_test.cc)

</details>



This document covers advanced features and internal implementation details of MuJoCo, including the default system and attribute inheritance, compiler options and processing phases, memory management strategies, the plugin system architecture, analytical derivatives, and documentation/asset workflows. These topics are essential for users who need fine-grained control over model compilation, performance optimization, or extension of MuJoCo's capabilities.

For basic model specification, see [Model Definition Pipeline](#2). For core physics simulation, see [Physics Simulation Pipeline](#4). For language bindings, see [C and Python APIs](#5).

## Default System and Inheritance (#9.1)

The MJCF format employs a hierarchical default system that allows for concise model definitions. Elements can inherit attributes from "default classes" (`mjclass`), reducing redundancy. This system manages attribute inheritance, childclass mechanisms, and class override behaviors during the compilation phase. The runtime system also uses these relationships to determine properties like `body_sameframe` or `geom_sameframe` by comparing child frames to their parent body or inertial frames [src/user/user_model.cc:153-172]().

For details, see [Default System and Inheritance](#9.1).

## Compiler Options and Processing (#9.2)

The MuJoCo compiler processes high-level MJCF or `mjSpec` descriptions into the runtime `mjModel`. This phase handles compiler flags, coordinate frame conversions (e.g., local vs. global), and angle representations. Key processing steps include configuring compiler directives, resolving alternative orientations via `ResolveOrientation` [src/user/user_objects.cc:154-159](), and processing complex assets and hierarchy attributes.

For details, see [Compiler Options and Processing](#9.2).

## Memory Management Strategies (#9.3)

MuJoCo uses a custom memory management architecture designed for high-performance physics. Central to this is the **Arena**, a large pre-allocated buffer in `mjData` used for workspace variables, with size configurable via attributes like `<size memory="..."/>` [test/xml/xml_native_reader_test.cc:168-173](). The engine utilizes stack-based allocation mechanisms to manage temporary memory without the overhead of heap allocation during stepping phases.

### Memory Allocation Architecture

```mermaid
graph TD
    subgraph "mjData_Memory_Layout"
        ["Arena_Buffer<br/>(mjData.arena)"] -- "Configured by" --> ["Size_Element<br/>(model->narena)"]
        ["Temporary_Stack"] -- "Managed by" --> ["mj_markStack/mj_freeStack"]
        ["Workspace_Arrays"] -- "Static Layout" --> ["qpos, qvel, qfrc_bias"]
    end

    subgraph "Allocation_Patterns"
        ["mj_makeData"] -- "Initializes" --> ["Static_Allocation"]
        ["Stack_Operations"] -- "Used in" --> ["Forward_Dynamics_Pipeline"]
    end

    ["Static_Allocation"] --> ["Workspace_Arrays"]
```

**Sources:** [test/xml/xml_native_reader_test.cc:168-173](), [src/user/user_model.cc:150-175]()

For details, see [Memory Management Strategies](#9.3).

## Plugin System (#9.4)

The plugin system allows developers to extend MuJoCo's core capabilities, such as custom actuators, sensors, and passive forces, as well as decoder plugins and elasticity models. Plugin configuration attributes are parsed via `ReadPluginConfigs` [src/xml/xml_native_reader.cc:131-157]() and mapped to specification structures (`mjsPlugin`), allowing modular runtime execution.

### Plugin Pipeline Association

```mermaid
graph LR
    subgraph "Parsing_and_Resolution"
        ["XMLElement<br/>(plugin/config)"] -- "Parsed by" --> ["ReadPluginConfigs"]
        ["ReadPluginConfigs"] -- "Populates" --> ["mjsPlugin"]
    end

    subgraph "Runtime_Execution"
        ["mj_compile"] -- "Resolves" --> ["mjPlugin_Instances"]
        ["Forward_Pipeline"] -- "Invokes" --> ["Plugin_Callbacks"]
    end

    ["mjsPlugin"] -- "Initializes" --> ["mjPlugin_Instances"]
```

**Sources:** [src/xml/xml_native_reader.cc:131-157]()

For details, see [Plugin System](#9.4).

## Analytical Derivatives (#9.5)

MuJoCo provides analytical derivatives for smooth dynamics, which are significantly faster than finite difference methods. These derivatives cover force derivatives with respect to state vectors (positions and velocities) and form the foundation for implicit integration support and state transition matrices.

### Derivative Computation Flow

| Function / Component | Purpose |
| :--- | :--- |
| `mjd_smooth_vel` | Computes analytical derivatives of smooth forces with respect to velocities |
| State Transition Jacobians | Linearization of system dynamics for control and optimization |
| Implicit Integration Support | Leverages analytical Jacobians to solve stiff equations stably |

**Sources:** [src/user/user_model.cc:70-125]()

For details, see [Analytical Derivatives](#9.5).

## Documentation and Model Assets (#9.6)

MuJoCo maintains an extensive documentation suite built via Sphinx (`doc/conf.py`) alongside a rich model/asset library used extensively by tests and examples. The XML schema (`mjcf.xsd`) serves as the single source of truth for schema validation and editor auto-completion [doc/XMLreference.rst:128-146]().

For details, see [Documentation and Model Assets](#9.6).

---

