<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/tilus · page 3 Core Systems · fetched 2026-10-26 -->

# Core Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [python/tilus/ir/builders/stmt_builder.py](python/tilus/ir/builders/stmt_builder.py)
- [python/tilus/lang/script.py](python/tilus/lang/script.py)

</details>



This page documents the fundamental systems that form the foundation of the Tilus GPU programming framework. These core systems provide the essential infrastructure for defining, compiling, and executing GPU kernels through a high-level Python DSL.

The core systems consist of the Script DSL interface, the statement building infrastructure, the memory and tensor model, and the compilation pipeline. For detailed information about specific aspects, see [Script System](#3.1), [JIT Compilation and Autotuning](#3.2), [Memory Model and Tensor Types](#3.3), and [Target System](#3.4).

## System Architecture Overview

The Tilus core systems form a layered architecture where user-defined scripts are processed through multiple abstraction levels to generate optimized GPU code.

**Core System Architecture**

```mermaid
graph TB
    subgraph "User Interface Layer"
        Script["tilus.Script"]
        Attrs["Attributes"]
        InstGroups["Instruction Groups<br/>(tmem, tma, mbarrier)"]
    end
    
    subgraph "Builder Infrastructure"
        StmtBuilder["StmtBuilder"]
        StmtBuilderCore["StmtBuilderCore"]
        Contexts["Context Classes<br/>(ForContext, IfContext, etc.)"]
    end
    
    subgraph "Tensor System"
        GlobalTensor["GlobalTensor"]
        SharedTensor["SharedTensor"] 
        RegisterTensor["RegisterTensor"]
        TMemoryTensor["TMemoryTensor"]
    end
    
    subgraph "Instruction System"
        Instructions["Instruction Classes"]
        InstStmt["InstStmt"]
        Stmt["Statement IR"]
    end
    
    Script --> StmtBuilder
    InstGroups --> StmtBuilder
    StmtBuilder --> StmtBuilderCore
    StmtBuilder --> Instructions
    StmtBuilderCore --> Contexts
    Contexts --> Stmt
    Instructions --> InstStmt
    InstStmt --> Stmt
    
    GlobalTensor --> Instructions
    SharedTensor --> Instructions
    RegisterTensor --> Instructions
    TMemoryTensor --> Instructions
```

**Sources:** [python/tilus/lang/script.py:599-649](), [python/tilus/ir/builders/stmt_builder.py:279-370]()

## Script DSL System

The `Script` class serves as the primary interface for users to define GPU kernels using a Python-based domain-specific language.

**Script System Components**

```mermaid
graph TB
    subgraph "Script Class Structure"
        ScriptBase["Script.__new__()"]
        ScriptInit["Script.__init__()"]
        Transpiler["_transpiler"]
        Builder["_optional_builder"]
    end
    
    subgraph "Instruction Groups"
        TmemGroup["TmemInstructionGroup"]
        TmaGroup["TmaInstructionGroup"] 
        BarrierGroup["BarrierInstructionGroup"]
    end
    
    subgraph "Core Operations"
        TensorOps["Tensor Operations<br/>(register_tensor, shared_tensor, etc.)"]
        MemOps["Memory Operations<br/>(load_global, store_shared, etc.)"]
        ComputeOps["Compute Operations<br/>(dot, add, transpose, etc.)"]
        ControlOps["Control Operations<br/>(range, thread_group, assume)"]
    end
    
    ScriptBase --> InstantiatedScriptCache
    ScriptInit --> Transpiler
    ScriptInit --> Builder
    ScriptInit --> TmemGroup
    ScriptInit --> TmaGroup
    ScriptInit --> BarrierGroup
    
    Script --> TensorOps
    Script --> MemOps
    Script --> ComputeOps
    Script --> ControlOps
    
    TmemGroup --> Builder
    TmaGroup --> Builder
    BarrierGroup --> Builder
```

The `Script` class provides methods for tensor allocation, memory operations, mathematical computations, and control flow. Key components include:

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| Tensor Allocation | Create tensors in different memory spaces | `register_tensor()`, `shared_tensor()`, `global_tensor()` |
| Memory Operations | Transfer data between memory hierarchies | `load_global()`, `store_shared()`, `copy_async()` |
| Compute Operations | Mathematical operations on tensors | `dot()`, `add()`, `transpose()`, `cast()` |
| Control Flow | Program structure and synchronization | `range()`, `thread_group()`, `assume()` |

**Sources:** [python/tilus/lang/script.py:599-649](), [python/tilus/lang/script.py:903-955](), [python/tilus/lang/script.py:1358-1433]()

## Statement Builder Infrastructure

The `StmtBuilder` system translates high-level DSL calls into intermediate representation statements and instructions.

**Statement Builder Hierarchy**

```mermaid
graph TB
    subgraph "Builder Core"
        StmtBuilderCore["StmtBuilderCore"]
        Stack["_stack: List[List[Stmt]]"]
        Contexts["Context Management"]
    end
    
    subgraph "Context Types"
        ForContext["ForContext"]
        IfContext["IfContext"]
        ThreadGroupContext["ThreadGroupContext"]
        WhileContext["WhileContext"]
    end
    
    subgraph "Statement Builder"
        StmtBuilder["StmtBuilder"]
        RegOps["Register Operations"]
        SharedOps["Shared Operations"]
        GlobalOps["Global Operations"]
        ControlOps["Control Operations"]
    end
    
    subgraph "Instruction Creation"
        Instructions["Instruction Instances"]
        InstStmt["InstStmt"]
        SeqStmt["SeqStmt"]
    end
    
    StmtBuilderCore --> Stack
    StmtBuilderCore --> Contexts
    Contexts --> ForContext
    Contexts --> IfContext
    Contexts --> ThreadGroupContext
    Contexts --> WhileContext
    
    StmtBuilder --> StmtBuilderCore
    StmtBuilder --> RegOps
    StmtBuilder --> SharedOps
    StmtBuilder --> GlobalOps
    StmtBuilder --> ControlOps
    
    StmtBuilder --> Instructions
    Instructions --> InstStmt
    Contexts --> SeqStmt
```

The builder system uses a stack-based approach to manage nested contexts and generates structured IR. Context managers handle control flow constructs like loops and conditionals.

**Sources:** [python/tilus/ir/builders/stmt_builder.py:128-144](), [python/tilus/ir/builders/stmt_builder.py:146-179](), [python/tilus/ir/builders/stmt_builder.py:371-391]()

## Memory Hierarchy and Tensor System

Tilus provides explicit tensor types for each level of the GPU memory hierarchy, enabling fine-grained control over data placement and movement.

**Tensor Type Hierarchy**

```mermaid
graph TB
    subgraph "Memory Hierarchy"
        Global["Global Memory<br/>(DRAM)"]
        Shared["Shared Memory<br/>(On-chip SRAM)"]
        Register["Register Memory<br/>(Register File)"]
        TMemory["Tensor Memory<br/>(SM90+ Hardware)"]
    end
    
    subgraph "Tensor Types"
        GlobalTensor["GlobalTensor"]
        SharedTensor["SharedTensor"]
        RegisterTensor["RegisterTensor"]
        TMemoryTensor["TMemoryTensor"]
    end
    
    subgraph "Operations"
        LoadStore["Load/Store Operations"]
        AsyncCopy["Async Copy Operations"]
        DotProduct["Dot Product (MMA)"]
        Elementwise["Elementwise Operations"]
    end
    
    Global --> GlobalTensor
    Shared --> SharedTensor
    Register --> RegisterTensor
    TMemory --> TMemoryTensor
    
    GlobalTensor --> LoadStore
    SharedTensor --> LoadStore
    RegisterTensor --> Elementwise
    RegisterTensor --> DotProduct
    
    GlobalTensor --> AsyncCopy
    SharedTensor --> AsyncCopy
    TMemoryTensor --> AsyncCopy
```

Each tensor type supports specific operations optimized for its memory location:

| Tensor Type | Memory Space | Key Operations | Performance Characteristics |
|-------------|--------------|----------------|----------------------------|
| `GlobalTensor` | Global DRAM | Load, store, async copy | High capacity, high latency |
| `SharedTensor` | On-chip SRAM | Load, store, async copy | Medium capacity, low latency |
| `RegisterTensor` | Register file | Compute, elementwise ops | Low capacity, no latency |
| `TMemoryTensor` | Tensor cores | MMA operations | Specialized for matrix operations |

**Sources:** [python/tilus/lang/script.py:956-999](), [python/tilus/lang/script.py:1001-1027](), [python/tilus/lang/script.py:903-955]()

## Instruction and Control Flow System

The instruction system provides fine-grained control over GPU execution through specialized instruction groups and control flow constructs.

**Instruction Group Organization**

```mermaid
graph TB
    subgraph "Specialized Instruction Groups"
        TmemInstructions["TmemInstructionGroup<br/>(alloc, load, store, wait)"]
        TmaInstructions["TmaInstructionGroup<br/>(copy_async_tensor_*)"]
        BarrierInstructions["BarrierInstructionGroup<br/>(init, arrive, wait)"]
    end
    
    subgraph "Control Flow Constructs"
        ForRange["for i in self.range()"]
        ThreadGroup["with self.thread_group()"]
        Conditional["with vb.if_then()"]
        WhileLoop["with vb.while_loop()"]
    end
    
    subgraph "Synchronization Primitives"
        Barriers["Memory Barriers"]
        ThreadSync["Thread Synchronization"]
        ClusterSync["Cluster Synchronization"]
        AsyncWait["Async Operation Waits"]
    end
    
    Script --> TmemInstructions
    Script --> TmaInstructions
    Script --> BarrierInstructions
    
    StmtBuilder --> ForRange
    StmtBuilder --> ThreadGroup
    StmtBuilder --> Conditional
    StmtBuilder --> WhileLoop
    
    BarrierInstructions --> Barriers
    TmaInstructions --> AsyncWait
    StmtBuilder --> ThreadSync
    StmtBuilder --> ClusterSync
```

Control flow in Tilus is managed through context managers that generate structured IR. The system supports nested scoping and proper resource management.

**Sources:** [python/tilus/lang/script.py:110-156](), [python/tilus/lang/script.py:158-284](), [python/tilus/lang/script.py:491-597](), [python/tilus/ir/builders/stmt_builder.py:284-313]()

## Compilation Flow Integration

The core systems work together to transform user scripts into executable GPU code through a structured compilation pipeline.

**Core System Interaction Flow**

```mermaid
graph LR
    subgraph "User Script Definition"
        UserCode["class MyKernel(tilus.Script)"]
        CallMethod["def __call__(self, ...)"]
    end
    
    subgraph "DSL Processing"
        ScriptInstance["Script Instance"]
        TranspilerCall["Transpiler Invocation"]
        StmtBuilding["Statement Building"]
    end
    
    subgraph "IR Generation"
        Instructions["Instruction Creation"]
        StmtIR["Statement IR"]
        FunctionIR["Function IR"]
    end
    
    subgraph "Compilation Pipeline"
        Optimization["IR Optimization"]
        CodeGen["Code Generation"]
        GPUExec["GPU Execution"]
    end
    
    UserCode --> ScriptInstance
    CallMethod --> TranspilerCall
    ScriptInstance --> StmtBuilding
    TranspilerCall --> StmtBuilding
    StmtBuilding --> Instructions
    Instructions --> StmtIR
    StmtIR --> FunctionIR
    FunctionIR --> Optimization
    Optimization --> CodeGen
    CodeGen --> GPUExec
```

The core systems provide the foundation for Tilus's ability to express complex GPU computations in a high-level Python interface while maintaining fine-grained control over hardware resources.

**Sources:** [python/tilus/lang/script.py:617-624](), [python/tilus/ir/builders/stmt_builder.py:348-368]()

---

