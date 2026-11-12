<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NVTX · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [c/include/nvtx3/nvToolsExt.h](c/include/nvtx3/nvToolsExt.h)
- [c/include/nvtx3/nvToolsExtCuda.h](c/include/nvtx3/nvToolsExtCuda.h)
- [c/include/nvtx3/nvToolsExtCudaRt.h](c/include/nvtx3/nvToolsExtCudaRt.h)
- [c/include/nvtx3/nvToolsExtOpenCL.h](c/include/nvtx3/nvToolsExtOpenCL.h)
- [c/include/nvtx3/nvtxDetail/nvtxInit.h](c/include/nvtx3/nvtxDetail/nvtxInit.h)
- [c/include/nvtx3/nvtxDetail/nvtxLinkOnce.h](c/include/nvtx3/nvtxDetail/nvtxLinkOnce.h)
- [docs/index.html](docs/index.html)
- [python/.flake8.cython](python/.flake8.cython)
- [tools/docs/generate-readme.py](tools/docs/generate-readme.py)
- [tools/docs/github-markdown-css/github-markdown.css](tools/docs/github-markdown-css/github-markdown.css)
- [tools/docs/github-markdown-css/license](tools/docs/github-markdown-css/license)

</details>



NVTX (NVIDIA Tools Extension Library) is a cross-platform API for annotating source code with contextual information for developer tools. It allows developers to mark specific points or ranges in their code, name resources, and organize annotations, which are then visualized and analyzed by NVIDIA profiling tools. By default, NVTX adds minimal overhead when no tool is attached, making it suitable for use in production code.

## Architecture

NVTX follows a layered architecture with the C API forming the foundation, while C++ and Python wrappers provide more idiomatic interfaces for those languages.

```mermaid
graph TB
    subgraph "Application Code"
        AppC["C Application"]
        AppCPP["C++ Application"]
        AppPython["Python Application"]
    end
    
    subgraph "NVTX API Layer"
        CAPI["C API<br>nvToolsExt.h"]
        CPPAPI["C++ API Wrappers<br>nvtx3.hpp"]
        PythonAPI["Python API<br>nvtx.py"]
    end
    
    subgraph "Implementation Layer"
        CoreImpl["Core Implementation<br>nvtxImpl.h"]
        CUDAImpl["CUDA Extensions<br>nvtxImplCuda"]
        SyncImpl["Synchronization<br>nvtxImplSync"]
        OpenCLImpl["OpenCL Extensions<br>nvtxImplOpenCL"]
    end
    
    subgraph "Profiling Tools"
        NsightSys["Nsight Systems"]
        NsightComp["Nsight Compute"]
        NsightGfx["Nsight Graphics"]
        CUPTI["CUPTI"]
    end
    
    AppC -->|"Uses"| CAPI
    AppCPP -->|"Uses"| CPPAPI
    AppPython -->|"Uses"| PythonAPI
    
    CPPAPI -->|"Wraps"| CAPI
    PythonAPI -->|"Binds to"| CAPI
    
    CAPI --> CoreImpl
    CAPI --> CUDAImpl
    CAPI --> SyncImpl
    CAPI --> OpenCLImpl
    
    CoreImpl -->|"Annotations"| NsightSys
    CoreImpl -->|"Annotations"| NsightComp
    CoreImpl -->|"Annotations"| NsightGfx
    CoreImpl -->|"Annotations"| CUPTI
```

Sources: [c/include/nvtx3/nvToolsExt.h:21-162](), [c/include/nvtx3/nvtxDetail/nvtxInit.h:415-454](), [README.md:1-24]()

## Key Concepts

NVTX provides several key mechanisms for annotating code:

### Markers and Ranges

NVTX supports two primary annotation types:

- **Markers**: Instantaneous events at specific points in execution
- **Ranges**: Time spans between two points in execution

```mermaid
graph LR
    subgraph "Core Functionality"
        Markers["Markers<br>Instantaneous Events"]
        Ranges["Ranges<br>Time Spans"]
        RNames["Resource Naming"]
        RTrack["Resource Tracking"]
        Domains["Domains<br>Event Grouping"]
    end
    
    subgraph "C API" 
        CMarker["nvtxMarkEx"]
        CRangePush["nvtxRangePushEx"]
        CRangePop["nvtxRangePop"]
        CRangeStart["nvtxRangeStartEx"]
        CRangeEnd["nvtxRangeEnd"]
        CName["nvtxName* Functions"]
        CDomain["nvtxDomain* Functions"]
        CResource["nvtxResource* Functions"]
    end
    
    subgraph "C++ API"
        CPPMark["nvtx3::mark"]
        CPPScopedRange["nvtx3::scoped_range"]
        CPPUniqueRange["nvtx3::unique_range"]
        CPPAttribs["nvtx3::event_attributes"]
        CPPDomain["nvtx3::domain"]
    end
    
    Markers --> CMarker
    Markers --> CPPMark
    
    Ranges --> CRangePush
    Ranges --> CRangePop
    Ranges --> CRangeStart
    Ranges --> CRangeEnd
    Ranges --> CPPScopedRange
    Ranges --> CPPUniqueRange
    
    Domains --> CDomain
    Domains --> CPPDomain
    
    RNames --> CName
    RTrack --> CResource
```

Sources: [c/include/nvtx3/nvToolsExt.h:672-897](), [README.md:51-62]()

| Annotation Type | Description | C API | C++ API |
|-----------------|-------------|-------|---------|
| Markers | Instantaneous events | `nvtxMarkA/W()`, `nvtxMarkEx()` | `nvtx3::mark()` |
| Thread Ranges | Stack-based nested ranges | `nvtxRangePushA/W()`, `nvtxRangePop()` | `nvtx3::scoped_range` |
| Process Ranges | Independent ranges | `nvtxRangeStartA/W()`, `nvtxRangeEnd()` | `nvtx3::unique_range` |

### Resource Naming and Tracking

NVTX allows associating user-provided names with resources like threads, CUDA streams, and OpenCL objects:

```mermaid
graph TD
    subgraph "Resource Types"
        Thread["OS Thread<br>nvtxNameOsThread()"]
        CUDADev["CUDA Device<br>nvtxNameCudaDevice()"]
        CUDAStream["CUDA Stream<br>nvtxNameCudaStream()"]
        CUDAEvent["CUDA Event<br>nvtxNameCudaEvent()"]
        OpenCLQueue["OpenCL Queue<br>nvtxNameClCommandQueue()"]
    end
    
    subgraph "Resource Objects API"
        ResObj["Resource Objects<br>Generic Resource"]
        ResDomain["Domain Resource Objects<br>Domain-Scoped Resource"]
    end
    
    ResObj --> Thread
    ResObj --> CUDADev
    ResObj --> CUDAStream
    ResObj --> CUDAEvent
    ResObj --> OpenCLQueue
    
    ResDomain --> ResObj
```

Sources: [c/include/nvtx3/nvToolsExtCuda.h:64-126](), [c/include/nvtx3/nvToolsExtCudaRt.h:64-104](), [c/include/nvtx3/nvToolsExtOpenCL.h:64-170](), [README.md:64-67]()

### Domains and Categories

Domains provide namespacing for annotations to prevent conflicts between libraries, while categories allow logical grouping:

```mermaid
graph TD
    subgraph "Domain Management"
        DomainCreate["nvtxDomainCreateA/W<br>Create Named Domain"]
        DomainDestroy["nvtxDomainDestroy<br>Cleanup Domain"]
        DomainHandle["nvtxDomainHandle_t<br>Domain Reference"]
    end
    
    subgraph "Domain-Scoped Operations"
        DomainMark["nvtxDomainMarkEx<br>Scoped Marker"]
        DomainRange["nvtxDomainRangePushEx<br>Scoped Range"]
        DomainString["nvtxDomainRegisterString<br>Scoped String"]
    end
    
    subgraph "Categories"
        CategoryName["nvtxNameCategoryA/W<br>Name Category ID"]
        EventAttrib["nvtxEventAttributes_t<br>Includes category field"]
    end
    
    DomainCreate --> DomainHandle
    DomainHandle --> DomainMark
    DomainHandle --> DomainRange
    DomainHandle --> DomainString
    DomainHandle --> DomainDestroy
    
    EventAttrib --> CategoryName
    EventAttrib --> DomainMark
    EventAttrib --> DomainRange
```

Sources: [c/include/nvtx3/nvToolsExt.h:94-120](), [README.md:427-434]()

## API Layers

### C API

The core C API is defined in `nvToolsExt.h` and provides the foundation for all NVTX functionality:

```mermaid
graph TB
    subgraph "Core API (nvToolsExt.h)"
        Markers["Markers<br>nvtxMarkA/W, nvtxMarkEx"]
        ThreadRanges["Thread Ranges<br>nvtxRangePushA/W, nvtxRangePop"]
        ProcessRanges["Process Ranges<br>nvtxRangeStartA/W, nvtxRangeEnd"]
        ResourceNaming["Resource Naming<br>nvtxNameOsThread, etc."]
        Domains["Domains<br>nvtxDomainCreate, etc."]
        Categories["Categories<br>nvtxNameCategory"]
    end
    
    subgraph "Extension Headers"
        CUDAExt["CUDA Extensions<br>nvToolsExtCuda.h"]
        CUDARTExt["CUDA Runtime Extensions<br>nvToolsExtCudaRt.h"]
        OpenCLExt["OpenCL Extensions<br>nvToolsExtOpenCL.h"]
    end
    
    CUDAExt --> ResourceNaming
    CUDARTExt --> ResourceNaming
    OpenCLExt --> ResourceNaming
```

Sources: [c/include/nvtx3/nvToolsExt.h:672-897](), [c/include/nvtx3/nvToolsExtCuda.h:64-126](), [c/include/nvtx3/nvToolsExtCudaRt.h:64-104](), [c/include/nvtx3/nvToolsExtOpenCL.h:64-170]()

### C++ API

The C++ API provides idiomatic C++ wrappers around the C API with RAII-based classes:

```mermaid
graph TB
    subgraph "C++ API (nvtx3.hpp)"
        Mark["nvtx3::mark<br>Create marker"]
        ScopedRange["nvtx3::scoped_range<br>RAII-based range"]
        UniqueRange["nvtx3::unique_range<br>Movable range"]
        Domain["nvtx3::domain<br>Domain wrapper"]
        EventAttribs["nvtx3::event_attributes<br>Marker/Range attributes"]
        Macros["Convenience Macros<br>NVTX3_FUNC_RANGE, etc."]
    end
    
    subgraph "C API (nvToolsExt.h)"
        CMarker["nvtxMarkEx"]
        CRangePush["nvtxRangePushEx"]
        CRangePop["nvtxRangePop"]
        CRangeStart["nvtxRangeStartEx"]
        CRangeEnd["nvtxRangeEnd"]
        CDomain["nvtxDomainCreate, etc."]
        CAttribs["nvtxEventAttributes_t"]
    end
    
    Mark --> CMarker
    ScopedRange --> CRangePush
    ScopedRange --> CRangePop
    UniqueRange --> CRangeStart
    UniqueRange --> CRangeEnd
    Domain --> CDomain
    EventAttribs --> CAttribs
    Macros --> ScopedRange
```

Sources: [README.md:88-96]()

### Python API

The Python API provides Pythonic interfaces with decorators and context managers:

```mermaid
graph TB
    subgraph "Python Package Structure"
        PyPackage["nvtx Python Package"]
        
        subgraph "Public API"
            nvtx_py["nvtx.py<br>Main Interface"]
            colors_py["colors.py<br>Color Utilities"]
            annotate["annotate<br>Decorator/Context Manager"]
            Profile["Profile<br>Automatic Function Annotation"]
        end
        
        subgraph "Internal Implementation"
            lib_pyx["_lib/lib.pyx<br>Cython Extension"]
            lib_pxd["_lib/lib.pxd<br>Cython Declarations"]
            utils["utils<br>Utility Modules"]
        end
    end
    
    nvtx_py --> lib_pyx
    nvtx_py --> colors_py
    nvtx_py --> annotate
    nvtx_py --> Profile
    
    lib_pyx --> lib_pxd
    lib_pxd --> nvtx_py
```

Sources: [README.md:258-262]()

## Initialization and Tool Integration

NVTX uses a lazy initialization model that looks for profiling tools only on first use:

```mermaid
sequenceDiagram
    participant App as Application
    participant NVTX as NVTX Library
    participant Init as nvtxInitOnce
    participant Tool as Profiling Tool
    
    App->>NVTX: First call to any NVTX function
    NVTX->>Init: Check if initialized
    
    Note over Init: Initialization process
    Init->>Init: Look for profiling tool
    
    alt Tool found
        Init->>Tool: Connect to tool
        Tool-->>Init: Set up function hooks
        Init->>NVTX: Configure with tool's implementation
    else No tool found
        Init->>NVTX: Configure with no-op implementations
    end
    
    NVTX->>App: Return from function call
    
    Note over App,NVTX: Subsequent calls
    App->>NVTX: Later NVTX function call
    
    alt Tool connected
        NVTX->>Tool: Forward call to tool
        Tool-->>NVTX: Process annotation
    else No tool
        NVTX->>NVTX: Execute no-op (minimal overhead)
    end
    
    NVTX->>App: Return from function call
```

The initialization process:
1. First NVTX call triggers `nvtxInitOnce()`
2. `nvtxInitializeInjectionLibrary()` searches for a profiling tool
   - Checks environment variables (NVTX_INJECTION64_PATH/NVTX_INJECTION32_PATH)
   - Looks for platform-specific injection methods
3. If a tool is found, NVTX configures function pointers to call into the tool
4. If no tool is found, NVTX sets all functions to no-ops

Sources: [c/include/nvtx3/nvtxDetail/nvtxInit.h:215-454](), [README.md:393-401]()

## Integration Options

### C/C++ Integration

NVTX for C/C++ is a header-only library with no dependencies except for `-ldl` on POSIX platforms:

```cpp
// C API
#include <nvtx3/nvToolsExt.h>

void example() {
    nvtxMarkA("Hello world!");
}

// C++ API
#include <nvtx3/nvtx3.hpp>

void example() {
    nvtx3::mark("Hello world!");
}
```

CMake targets are provided for easy integration:

```cmake
# C program
add_executable(my_c_program main.c)
target_link_libraries(my_c_program PRIVATE nvtx3-c)

# C++ program
add_executable(my_cpp_program main.cpp)
target_link_libraries(my_cpp_program PRIVATE nvtx3-cpp)
```

Sources: [README.md:72-101](), [README.md:106-120]()

### Python Integration

Install NVTX for Python using pip or conda:

```python
import nvtx

# Create a marker
nvtx.mark(message="Hello world!")

# Annotate a function
@nvtx.annotate("Function Range")
def my_function():
    # Function body
    pass

# Annotate a code block
with nvtx.annotate("Block Range"):
    # Code block
    pass
```

Installation methods:
- `pip install nvtx`
- `conda install -c conda-forge nvtx`

Sources: [README.md:258-262](), [README.md:312-315]()

## Supported Tools

NVTX annotations are recognized by several NVIDIA developer tools:

| Tool | NVTX Usage |
|------|------------|
| Nsight Systems | Shows NVTX markers and ranges on timeline |
| Nsight Compute | Uses NVTX ranges to focus kernel analysis |
| Nsight Graphics | Uses NVTX ranges to set bounds for profiling |
| CUPTI | Records NVTX calls in profiling API |

Sources: [README.md:323-331]()

## Platform Support

NVTX works on:
- Windows
- Linux and other POSIX-like platforms (including Cygwin)
- Android

Both 64-bit and 32-bit processes are supported without CPU architecture restrictions.

Sources: [README.md:334-341]()

---

